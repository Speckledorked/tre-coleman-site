/**
 * The contact form, handled on this site instead of by a third party.
 *
 * WHY THIS EXISTS
 *
 * contact.html posted straight to formsubmit.co. That host went down and
 * stayed down for over a week, and because the form was a plain browser POST
 * with nothing catching the failure, every enquiry in that window was lost:
 * the visitor was navigated off the site, waited about twenty seconds, and
 * landed on a Cloudflare 522 error page with no branding and no explanation.
 * Nobody was told, least of all the person whose leads they were.
 *
 * Nothing about that was detectable from here either. The only signal was a
 * link checker noticing the host was unreachable, which reads as a CI
 * nuisance rather than as "the lead form is dead".
 *
 * So the submission now stays on trecoleman.com, where an outage is this
 * site's own problem and shows up as a real error on the page rather than as
 * a silent redirect to someone else's infrastructure.
 *
 * Accepts BOTH shapes:
 *   - application/json, from the fetch in contact.html, answered with JSON so
 *     the page can show success or failure without navigating away
 *   - form-encoded, from a plain submit if JavaScript never runs, answered
 *     with a 303 to /thank-you.html so the form still works without it
 *
 * The reply-to is set to the enquirer, so hitting reply in a mail client
 * answers the person rather than noreply@.
 */

const { Resend } = require('resend');

const resend = new Resend(process.env.RESEND_API_KEY);

// Where the lead goes. Not configurable by the request, obviously.
const TO = 'hello@trecoleman.com';
// The from: address stays on trecoleman.com: that is where Resend's DKIM is.
const FROM = 'Tre Coleman <noreply@trecoleman.com>';

// Mirrors the form in contact.html exactly. An earlier draft of this list
// invented a "timeline" field and omitted budget and start -- both of which
// the form marks required -- so two answers the buyer had given would have
// been dropped from the email without anything failing.
const REQUIRED = ['name', 'email', 'company', 'location', 'interest',
                  'budget', 'start', 'bottleneck'];
const OPTIONAL = ['phone', 'utm_source', 'utm_medium', 'utm_campaign'];

const LABELS = {
  name: 'Name',
  email: 'Email',
  company: 'Company',
  phone: 'Phone',
  location: 'Location',
  interest: 'Interested in',
  budget: 'Budget',
  start: 'Timeline',
  bottleneck: 'Biggest bottleneck',
  utm_source: 'utm_source',
  utm_medium: 'utm_medium',
  utm_campaign: 'utm_campaign',
};

/** Escape before putting anything a stranger typed into an HTML email. */
function esc(value) {
  return String(value == null ? '' : value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/**
 * A header value cannot contain a newline, or it can inject extra headers.
 * reply_to is the only place a submitted value reaches a header.
 */
function safeHeaderValue(value) {
  return String(value || '').replace(/[\r\n]+/g, ' ').trim();
}

function parseBody(event) {
  const type = (event.headers['content-type'] || event.headers['Content-Type'] || '')
    .toLowerCase();
  const raw = event.isBase64Encoded
    ? Buffer.from(event.body || '', 'base64').toString('utf8')
    : (event.body || '');

  if (type.includes('application/json')) {
    return { fields: JSON.parse(raw), wantsJson: true };
  }
  const params = new URLSearchParams(raw);
  const fields = {};
  for (const [k, v] of params) fields[k] = v;
  return { fields, wantsJson: false };
}

// In-memory per-address submission counts, pruned as they age out. This
// only holds within one warm function instance, so it blunts a flood from
// one address rather than stopping a distributed one.
const SUBMISSIONS_BY_IP = new Map();
const RATE_WINDOW_MS = 10 * 60 * 1000;
const RATE_MAX = 5;
function rateLimited(ip) {
  if (!ip) return false;
  const now = Date.now();
  const recent = (SUBMISSIONS_BY_IP.get(ip) || []).filter((t) => now - t < RATE_WINDOW_MS);
  if (recent.length >= RATE_MAX) return true;
  recent.push(now);
  SUBMISSIONS_BY_IP.set(ip, recent);
  if (SUBMISSIONS_BY_IP.size > 5000) SUBMISSIONS_BY_IP.clear();
  return false;
}

exports.handler = async (event) => {
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
      },
      body: '',
    };
  }

  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json',
    'Cache-Control': 'no-store',
  };

  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, headers, body: JSON.stringify({ error: 'Method not allowed' }) };
  }

  let fields;
  let wantsJson = true;
  try {
    ({ fields, wantsJson } = parseBody(event));
  } catch (_) {
    return { statusCode: 400, headers, body: JSON.stringify({ error: 'Malformed submission' }) };
  }

  const done = (statusCode, body) => {
    // Without JavaScript the browser is navigating, so answer with a page to
    // land on rather than a blob of JSON.
    if (!wantsJson) {
      const to = statusCode === 200 ? '/thank-you.html' : '/contact.html?error=1';
      return { statusCode: 303, headers: { Location: to, 'Cache-Control': 'no-store' }, body: '' };
    }
    return { statusCode, headers, body: JSON.stringify(body) };
  };

  // The honeypot, kept from the original markup: a hidden field a person
  // never sees and a bot fills in. Answer as though it worked -- telling a
  // bot it was caught only teaches it to stop filling the field in.
  if (String(fields.website || '').trim() !== '') {
    return done(200, { success: true });
  }

  // Spam defence, part two: the page stamps when it loaded, and the
  // submitter's script sends that stamp with the JSON submission. A real
  // person takes at least a couple of seconds to fill the form in; a bot
  // fires the instant it fetches the page, or replays a stale stamp hours
  // later. Plain form-encoded submits (no JavaScript) carry no stamp and
  // skip this check. A tripped check is answered as though it worked, as
  // with the honeypot -- except a missing stamp, which a stale cached page
  // can cause, and which gets a real error so the person can reload and
  // retry instead of losing the enquiry silently.
  if (wantsJson) {
    const started = Number(fields.started);
    if (!Number.isFinite(started)) {
      return done(400, { error: 'Please reload the page and try again.' });
    }
    const age = Date.now() - started;
    if (age < 2000 || age > 2 * 60 * 60 * 1000 || age < -5 * 60 * 1000) {
      return done(200, { success: true });
    }
  }

  // Spam defence, part three: no more than a handful of submissions from
  // one address in a short window. Over the limit, answer as though the
  // submission worked.
  const forwarded = event.headers['x-forwarded-for'] || event.headers['X-Forwarded-For'] || '';
  const clientIp = (event.headers['x-nf-client-connection-ip']
    || event.headers['X-Nf-Client-Connection-Ip']
    || forwarded.split(',')[0]
    || event.headers['client-ip']
    || event.headers['Client-Ip']
    || '').trim();
  if (rateLimited(clientIp)) {
    return done(200, { success: true });
  }

  const missing = REQUIRED.filter((f) => !String(fields[f] || '').trim());
  if (missing.length) {
    return done(400, { error: `Please fill in: ${missing.join(', ')}` });
  }
  const email = String(fields.email).trim();
  if (!/^[^@\s]+@[^@\s.]+\.[^@\s]+$/.test(email)) {
    return done(400, { error: 'That email address does not look right.' });
  }
  // A bounded guard against someone pasting a novel into the textarea.
  if (String(fields.bottleneck).length > 5000) {
    return done(400, { error: 'That message is too long. Please shorten it.' });
  }

  if (!process.env.RESEND_API_KEY) {
    console.error('contact-form: RESEND_API_KEY is missing');
    return done(500, { error: 'The form is temporarily unavailable. Please email hello@trecoleman.com.' });
  }

  const rows = [...REQUIRED, ...OPTIONAL]
    .filter((f) => String(fields[f] || '').trim())
    .map((f) => `<tr>
        <td style="padding:6px 14px 6px 0;vertical-align:top;color:#55524B;">${esc(LABELS[f] || f)}</td>
        <td style="padding:6px 0;vertical-align:top;"><strong>${esc(fields[f])}</strong></td>
      </tr>`)
    .join('\n');

  try {
    await resend.emails.send({
      from: FROM,
      to: TO,
      // Hitting reply answers the person, not noreply@.
      reply_to: safeHeaderValue(email),
      subject: `New lead: ${safeHeaderValue(fields.name)} — ${safeHeaderValue(fields.interest)}`,
      html: `<div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;max-width:640px;">
        <h1 style="font-size:18px;margin:0 0 16px;">New enquiry from trecoleman.com</h1>
        <table style="border-collapse:collapse;font-size:15px;line-height:1.5;">
${rows}
        </table>
      </div>`,
    });
  } catch (err) {
    // The lead must not vanish the way it did with the old provider: log the
    // whole submission so it can be recovered from the function log.
    console.error('contact-form: notification failed', err, JSON.stringify(fields));
    return done(502, {
      error: 'Could not send that just now. Please email hello@trecoleman.com directly.',
    });
  }

  // The acknowledgement the old provider used to send. Nothing the sender
  // typed is echoed into it, so it cannot be used to deliver a stranger's
  // text to an address they do not control.
  try {
    await resend.emails.send({
      from: FROM,
      to: safeHeaderValue(email),
      reply_to: TO,
      subject: 'Thanks for reaching out — Tre Coleman',
      html: `<div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;max-width:640px;font-size:15px;line-height:1.6;">
        <p>Thanks for reaching out — I'll review what you sent and reply shortly.</p>
        <p>If it's urgent, call or text <a href="tel:540-807-9045">540.807.9045</a>.</p>
        <p style="margin-top:24px;">— Tre Coleman<br>Tre Coleman Consulting LLC</p>
      </div>`,
    });
  } catch (err) {
    // The lead is already delivered; a failed acknowledgement is not the
    // sender's problem and must not be reported to them as a failure.
    console.error('contact-form: autoresponse failed', err);
  }

  return done(200, { success: true });
};
