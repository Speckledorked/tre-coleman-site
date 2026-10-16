const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const { createClient } = require('@supabase/supabase-js');
const { Resend } = require('resend');
const crypto = require('crypto');
const courses = require('./lib/courses.js');
const { coursesForUser } = require('./lib/access.js');

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
);

const resend = new Resend(process.env.RESEND_API_KEY);

// Where to point links in outbound email.
//
// Netlify sets URL to the site's primary address: the custom domain once one is
// attached, and the *.netlify.app address until then. Hardcoding
// https://trecoleman.com meant that while the custom domain was not attached,
// every link in every transactional email landed on a host that fails TLS — a
// customer could buy the course and be unable to reach it. The fallback keeps
// behaviour unchanged if URL is ever unset.
//
// The from: addresses stay on trecoleman.com: that is where Resend's DKIM
// record lives, and it is verified independently of where the site is served.
const SITE = process.env.URL || 'https://trecoleman.com';


// GA4 property that analytics.js:5 configures. Hardcoded rather than read
// from the environment because it is public either way — it ships in the page
// — and one fewer required variable is one fewer way for revenue reporting to
// be silently misconfigured. tools/check_site.py asserts the two agree.
const GA4_MEASUREMENT_ID = 'G-778929FT8G';



exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method not allowed' };
  }

  const sig = event.headers['stripe-signature'];
  let stripeEvent;

  try {
    stripeEvent = stripe.webhooks.constructEvent(
      event.body,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET
    );
  } catch (err) {
    console.error('Webhook signature verification failed:', err.message);
    return { statusCode: 400, body: `Webhook Error: ${err.message}` };
  }

  // The customer's asynchronous payment did not clear. Nothing was granted
  // when the session completed — the payment_status guard below refuses an
  // unpaid session — so there is nothing to revoke. The owner should still
  // know a sale fell through rather than watch it quietly disappear.
  if (stripeEvent.type === 'checkout.session.async_payment_failed') {
    const session = stripeEvent.data.object;
    const email = session.customer_details?.email || session.customer_email || 'unknown';
    console.log(`Async payment failed for session ${session.id} (${email}). No access was granted.`);
    await alertAdmin('Course purchase payment failed', `
      <p>An asynchronous payment did not clear, so no course access was granted.</p>
      <p>Customer: ${email}</p>
      <p>Stripe Session ID: ${session.id}</p>
      <p>No action is needed unless you expected this sale to complete.</p>
    `);
    return { statusCode: 200, body: 'Async payment failure acknowledged' };
  }

  // The two events that can grant course access.
  //
  // checkout.session.completed fires when the customer finishes checkout,
  // which is not the same as the money having arrived. With an asynchronous
  // payment method — a bank debit, Klarna, boleto — the session completes
  // with payment_status 'unpaid' and settles minutes or days later, or never.
  // checkout.session.async_payment_succeeded is that settlement.
  //
  // Both run the same path below and the payment_status guard decides which
  // one actually grants, so an async purchase is refused at completion and
  // granted at settlement without a second code path.
  //
  // The endpoint must be subscribed to BOTH in Stripe. Subscribed only to
  // completed, an async buyer would be charged and never let in.
  const GRANTS_ACCESS = [
    'checkout.session.completed',
    'checkout.session.async_payment_succeeded'
  ];

  if (GRANTS_ACCESS.includes(stripeEvent.type)) {
    const session = stripeEvent.data.object;

    // Get customer email from session
    const customerEmail = session.customer_details?.email || session.customer_email;

    if (!customerEmail) {
      console.error('No customer email in session');
      return { statusCode: 400, body: 'No customer email' };
    }

    // Which course did they buy?
    //
    // This used to match ONE price id from STRIPE_COURSE_PRICE_ID, which broke
    // in two ways as soon as there was more than one of anything. A course
    // with two live prices -- the Catering Profit System sells at $197 and at
    // $147 to the first ten founding members, separate payment links and so
    // separate Price objects -- had one of them treated as "not the course",
    // and the buyer was charged and let in nowhere. And one price id cannot
    // say WHICH course, so a second product would have granted the first.
    //
    // netlify/functions/lib/courses.js now holds a LIST of price ids per
    // course. See .env.example for the variables.
    const configuredPriceIds = courses.allPriceIds();

    // Describes the purchase to GA4 further down. Stays null when no course
    // price is configured, because nothing then needs to read the line items
    // and an extra Stripe call on every payment would buy nothing.
    let lineItems = null;
    // Every course this payment grants. A bundle grants more than one, so this
    // is a list rather than a single course all the way through.
    let purchased = { slugs: [], name: null, bundles: [] };

    if (configuredPriceIds.length) {
      const items = await stripe.checkout.sessions.listLineItems(session.id, { limit: 10 });
      lineItems = items.data;

      purchased = courses.purchaseFromLineItems(lineItems);

      if (!purchased.slugs.length) {
        console.log(`Payment from ${customerEmail} is not for a course (session ${session.id}). Skipping course access.`);
        // Not a course, but still money taken: the $350 Snapshot finishes on
        // Stripe's own page and never touches the site, so this is the only
        // place it can be counted.
        await reportPurchaseToGA4(stripeEvent, lineItems);
        return { statusCode: 200, body: 'Non-course payment acknowledged' };
      }

      /**
       * The upgrade price is only for someone who already owns one course.
       *
       * It grants both courses, because one Stripe price cannot know which one
       * the buyer is missing. That makes the $100 link worth $297 to anyone
       * who finds it, and a Stripe payment link cannot be gated on a previous
       * purchase — an unlisted link is still a shareable URL.
       *
       * So: if they hold neither course, grant nothing and ask for a human.
       * They have underpaid, and whether to refund or bill the difference is
       * not a decision to make automatically. Checked BEFORE any access is
       * written, so nothing has to be taken back.
       */
      const gated = courses.bundlesRequiringExisting(purchased.bundles);
      if (gated.length) {
        const existing = await heldCourses(customerEmail);
        const qualifies = existing.some((slug) => purchased.slugs.includes(slug));
        if (!qualifies) {
          console.error(`Upgrade bought by ${customerEmail} who holds no course (session ${session.id})`);
          await alertAdmin('Upgrade price bought by someone with no course', `
            <p>${customerEmail} paid the upgrade price, which is the difference
               between one course and the bundle, but holds neither course.</p>
            <p>Stripe Session ID: ${session.id}</p>
            <p>Amount: $${((session.amount_total || 0) / 100).toFixed(2)}</p>
            <p><strong>No access has been granted.</strong> They have underpaid
               for what that price grants, so this needs a decision: refund
               them, bill the difference, or grant it anyway by inserting rows
               into <code>course_access</code> for
               <code>${purchased.slugs.join('</code> and <code>')}</code>.</p>
            <p>If this keeps happening the upgrade link has got out, and the
               price should be replaced with a fresh one.</p>
          `);
          await reportPurchaseToGA4(stripeEvent, lineItems);
          // 200: a redelivery cannot change who they are, and a 500 makes
          // Stripe retry the same event for days.
          return { statusCode: 200, body: 'Upgrade without a prior course, owner alerted' };
        }
      }
    }

    // With nothing configured the gate is skipped, exactly as before, and the
    // payment is treated as the original course. That keeps a missing variable
    // from locking out buyers, but it also means the Snapshot would grant a
    // course, so say so loudly rather than only in a comment.
    if (!purchased.slugs.length) {
      purchased = {
        slugs: ['catering-profit'],
        name: courses.course('catering-profit').name,
        bundles: [],
      };
      console.warn(
        'No course price ids are configured, so every completed checkout is '
        + 'being treated as a purchase of the Catering Profit System -- the '
        + '$350 Snapshot included. Set STRIPE_PRICE_IDS_CATERING_PROFIT, '
        + 'STRIPE_PRICE_IDS_CATERING_PEOPLE and STRIPE_PRICE_IDS_CATERING_BUNDLE. '
        + 'See .env.example.'
      );
    }

    // What to call it in the email and the logs.
    const purchasedName = purchased.name || 'your course';

    // The money has to have actually arrived.
    //
    // Reaching this point used to be enough to hand over the paid course, a
    // Supabase auth user and working login credentials. For a card payment
    // that is right — payment_status is already 'paid' when the session
    // completes. For an asynchronous method it is not: the session completes
    // 'unpaid' and the charge settles later, so the course went out before
    // any money moved, and stayed out if the payment then failed.
    //
    // Only an explicit 'unpaid' blocks. 'paid' is the normal case, and
    // 'no_payment_required' is a legitimately zero-value session — a 100%
    // discount code, which is the owner's to issue — so both grant. A missing
    // value grants too, which preserves exactly the behaviour this guard
    // replaces: Stripe documents the field as always present on a
    // payment-mode session, and inventing a new way to refuse a real buyer
    // would be a worse bug than the one being closed.
    if (session.payment_status === 'unpaid') {
      console.log(
        `Session ${session.id} from ${customerEmail} completed but is unpaid; ` +
        `not granting access. Waiting for checkout.session.async_payment_succeeded.`
      );
      await alertAdmin('Course purchase is awaiting payment', `
        <p>A course checkout completed but the payment has not cleared, so no
           access has been granted yet.</p>
        <p>Customer: ${customerEmail}</p>
        <p>Stripe Session ID: ${session.id}</p>
        <p>This is normal for an asynchronous payment method such as a bank
           debit or Klarna. Access is granted automatically when Stripe sends
           <code>checkout.session.async_payment_succeeded</code>, and you will
           get a separate email if the payment fails instead.</p>
        <p>If neither email arrives, check that the webhook endpoint is
           subscribed to <code>checkout.session.async_payment_succeeded</code>
           — without it this customer would be charged and never let in.</p>
      `);
      // 200, not 500: a redelivery cannot change payment_status, and a 500
      // makes Stripe retry this same event for days.
      return { statusCode: 200, body: 'Awaiting payment' };
    }

    console.log(`Processing ${purchased.slugs.join('+')} purchase for: ${customerEmail}`);

    try {
      // Check if user already exists
      const { data: existingUser } = await supabase
        .from('users')
        .select('id, name')
        .eq('email', customerEmail.toLowerCase())
        .single();

      if (existingUser) {
        // User exists - grant access to the course they bought
        const update = {
          stripe_customer_id: session.customer,
          // "Most recent purchase". Per-course timing lives on the
          // course_access row's granted_at, so overwriting this loses nothing.
          course_purchased_at: new Date().toISOString()
        };
        // Only the original course still writes the single-course boolean, and
        // only so this change can be rolled back by reverting the code alone.
        // The single-course boolean is still written when the purchase
        // includes the original course, so this stays revertible.
        if (purchased.slugs.some((slug) => courses.hasLegacyFlag(slug))) {
          update.has_course_access = true;
        }

        await supabase
          .from('users')
          .update(update)
          .eq('id', existingUser.id);

        // Every course the purchase covers. A bundle grants two.
        for (const slug of purchased.slugs) {
          await grantCourseAccess(existingUser.id, slug, session.id);
        }

        // Send access granted email
        await resend.emails.send({
          from: 'Tre Coleman <noreply@trecoleman.com>',
          to: customerEmail,
          subject: `Your Course Access is Ready! - ${purchasedName}`,
          html: `
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
              <h1 style="color: #1F4788;">You're In! Course Access Granted</h1>
              <p>Hi ${existingUser.name || 'there'},</p>
              <p>Thank you for purchasing <strong>${purchasedName}</strong>!</p>
              <p>Your account has been updated with full course access. You can log in now to start learning:</p>
              <p style="margin: 30px 0;">
                <a href="${SITE}/login.html" style="background: #F4A460; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">Access Your Course</a>
              </p>
              <p>Your materials are ready now. Remaining lesson videos are being added as they're finished.</p>
              <p style="margin-top: 30px; color: #666;">Let's fix those profit leaks!</p>
              <p style="color: #666;">— Tre Coleman</p>
            </div>
          `
        });

        console.log(`${purchased.slugs.join('+')} access granted for existing user: ${customerEmail}`);
      } else {
        // New user - create account with temporary password
        const tempPassword = generateTempPassword();

        // Create user in Supabase Auth
        const { data: authData, error: authError } = await supabase.auth.admin.createUser({
          email: customerEmail,
          password: tempPassword,
          email_confirm: true,
          user_metadata: { name: session.customer_details?.name || 'Course Student' }
        });

        if (authError) {
          console.error('Error creating user:', authError);
          throw authError;
        }

        // Create user profile with course access
        const profile = {
          id: authData.user.id,
          email: customerEmail.toLowerCase(),
          name: session.customer_details?.name || 'Course Student',
          stripe_customer_id: session.customer,
          course_purchased_at: new Date().toISOString(),
          created_at: new Date().toISOString()
        };
        if (purchased.slugs.some((slug) => courses.hasLegacyFlag(slug))) {
          profile.has_course_access = true;
        }

        await supabase.from('users').insert(profile);

        for (const slug of purchased.slugs) {
          await grantCourseAccess(authData.user.id, slug, session.id);
        }

        // Send welcome + course access email with temp password
        await resend.emails.send({
          from: 'Tre Coleman <noreply@trecoleman.com>',
          to: customerEmail,
          subject: `Welcome! Your Course Access + Login Details - ${purchasedName}`,
          html: `
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
              <h1 style="color: #1F4788;">Welcome to ${purchasedName}!</h1>
              <p>Hi ${session.customer_details?.name || 'there'},</p>
              <p>Thank you for your purchase! Your account has been created and you have full course access.</p>

              <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 25px 0;">
                <h3 style="color: #1F4788; margin-top: 0;">Your Login Details</h3>
                <p><strong>Email:</strong> ${customerEmail}</p>
                <p><strong>Temporary Password:</strong> ${tempPassword}</p>
                <p style="color: #e74c3c; font-size: 14px;">Please change your password after logging in!</p>
              </div>

              <p style="margin: 30px 0;">
                <a href="${SITE}/login.html" style="background: #F4A460; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">Log In Now</a>
              </p>

              <p>Your materials are ready now. Remaining lesson videos are being added as they're finished.</p>

              <p style="margin-top: 30px; color: #666;">Let's fix those profit leaks!</p>
              <p style="color: #666;">— Tre Coleman</p>
            </div>
          `
        });

        console.log(`New user created with ${purchased.slugs.join('+')} access: ${customerEmail}`);
      }

      // Last, and never in a way that can fail the purchase: access is
      // granted and the email is away by this point.
      await reportPurchaseToGA4(stripeEvent, lineItems);

      return { statusCode: 200, body: 'Success' };

    } catch (error) {
      console.error('Error processing purchase:', error);

      await alertAdmin('Failed to process course purchase', `
        <p>Failed to automatically process purchase for: ${customerEmail}</p>
        <p>Stripe Session ID: ${session.id}</p>
        <p>Error: ${error.message}</p>
        <p>Course(s): <strong>${purchased.slugs.join(', ') || 'unknown'}</strong></p>
        <p>Please grant access by hand: insert a row into
           <code>course_access</code> for this customer's user id for EACH
           <code>course_slug</code> listed above.</p>
      `);

      return { statusCode: 500, body: 'Processing error' };
    }
  }

  return { statusCode: 200, body: 'Event received' };
};

/**
 * Which courses the account behind this email already holds.
 *
 * Used only by the upgrade guard, before anything is granted. Returns an
 * EMPTY list for an unknown email, which is the honest answer: no account, no
 * courses, so an upgrade bought with it does not qualify.
 *
 * Never throws. A failure here must not fail the purchase of a bundle that
 * does not need the check, and the caller treats an empty list as "does not
 * qualify", which alerts a human rather than granting or refusing silently.
 */
async function heldCourses(email) {
  try {
    const { data: user } = await supabase
      .from('users')
      .select('id')
      .eq('email', String(email || '').toLowerCase())
      .single();
    if (!user) return [];

    const { data: profile } = await supabase
      .from('users')
      .select('has_course_access')
      .eq('id', user.id)
      .single();

    const { slugs } = await coursesForUser(
      supabase, user.id, profile && profile.has_course_access
    );
    return slugs;
  } catch (e) {
    console.error('Could not read existing courses for', email, e.message);
    return [];
  }
}


/**
 * Record that a user may open a course.
 *
 * THROWS on failure, deliberately. The caller's catch block alerts the owner
 * and returns 500 so Stripe retries, which is what should happen: a customer
 * who paid and has no row is locked out of what they bought, and that is worse
 * than a retried webhook. Swallowing this would make the failure invisible
 * until the customer emailed to ask where their course was.
 *
 * upsert, so a Stripe redelivery of the same event is a no-op rather than a
 * duplicate-key error that would look like a real failure and trigger a
 * pointless alert. ignoreDuplicates keeps the original granted_at and
 * session_id: the first grant is the one that happened.
 */
async function grantCourseAccess(userId, courseSlug, sessionId) {
  const { error } = await supabase
    .from('course_access')
    .upsert(
      {
        user_id: userId,
        course_slug: courseSlug,
        granted_at: new Date().toISOString(),
        session_id: sessionId || null
      },
      { onConflict: 'user_id,course_slug', ignoreDuplicates: true }
    );

  if (error) {
    // Surfaced with the slug and user so the row can be written by hand from
    // the alert alone, without digging through logs for which course it was.
    console.error(`Failed to grant ${courseSlug} to ${userId}:`, error.message);
    throw new Error(`course_access upsert failed for ${courseSlug}: ${error.message}`);
  }
}


// Tell the owner that something needs a human.
//
// Never throws. An alert that cannot be sent must not take down the path that
// was trying to send it — the original problem is already worse than the
// missing email, and in the catch block below this would have replaced a
// recoverable error with an unhandled one.
async function alertAdmin(subject, html) {
  try {
    await resend.emails.send({
      from: 'System <noreply@trecoleman.com>',
      to: 'hello@trecoleman.com',
      subject: `ALERT: ${subject}`,
      html
    });
  } catch (e) {
    console.error(`Failed to send admin alert (${subject}):`, e.message);
  }
}


// ── Reporting revenue to GA4 ───────────────────────────────────────────────
//
// The browser cannot do this job. It never learns the amount, it never sees
// the $350 Snapshot at all (that link finishes on Stripe's own page), and
// both products used to arrive at one thank-you page that could not tell
// them apart. Stripe, here, knows exactly what was bought and for how much.
//
// Sent via the Measurement Protocol, which is the server-side equivalent of
// gtag('event', 'purchase', ...).
// https://developers.google.com/analytics/devguides/collection/protocol/ga4
//
// This function is written so that it can never fail a purchase. Everything
// is inside one try/catch, it is awaited only after course access has been
// granted and the confirmation email sent, and a missing API secret is a
// logged warning rather than an error. Analytics are worth less than a
// customer getting what they paid for.
async function reportPurchaseToGA4(stripeEvent, lineItems) {
  const session = stripeEvent.data.object;
  try {
    const apiSecret = process.env.GA4_API_SECRET;
    if (!apiSecret) {
      console.warn(
        `GA4_API_SECRET is not set — purchase ${session.id} was not reported ` +
        `to GA4 and its revenue will be missing from reporting.`
      );
      return;
    }

    // An unpaid or still-processing session is not revenue yet.
    if (session.payment_status && session.payment_status !== 'paid') {
      console.log(`Session ${session.id} is ${session.payment_status}; not reporting to GA4.`);
      return;
    }

    // What the customer actually paid. No shipping exists on either product
    // and Stripe Tax is not enabled, so gross equals net here; tax and
    // shipping are passed through anyway so the figure stays honest if that
    // ever changes.
    const value = (session.amount_total || 0) / 100;
    const currency = (session.currency || 'usd').toUpperCase();
    const details = session.total_details || {};

    const items = (lineItems || []).map((item, i) => {
      const quantity = item.quantity || 1;
      return {
        item_id: item.price?.id || item.id,
        item_name: item.description || 'Unnamed line item',
        price: Math.round(((item.amount_total || 0) / quantity)) / 100,
        quantity,
        index: i
      };
    });

    // GA4 requires at least one item on a purchase. Line items are only
    // fetched when a course price is configured, so fall back to describing
    // the session as a single line.
    if (!items.length) {
      items.push({
        item_id: 'stripe_checkout',
        item_name: 'Stripe checkout',
        price: value,
        quantity: 1,
        index: 0
      });
    }

    const params = {
      transaction_id: session.id,
      value,
      currency,
      items
    };
    if (details.amount_tax) params.tax = details.amount_tax / 100;
    if (details.amount_shipping) params.shipping = details.amount_shipping / 100;

    const body = {
      client_id: ga4ClientId(session),
      // Stripe retries a failed webhook for days. Stamping the event with
      // when the payment happened rather than when this code ran keeps a
      // retried purchase on the right day. The Measurement Protocol accepts
      // backdated events up to 72 hours.
      timestamp_micros: (stripeEvent.created || Math.floor(Date.now() / 1000)) * 1000000,
      events: [{ name: 'purchase', params }]
    };

    const url = `https://www.google-analytics.com/mp/collect` +
                `?measurement_id=${encodeURIComponent(GA4_MEASUREMENT_ID)}` +
                `&api_secret=${encodeURIComponent(apiSecret)}`;

    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });

    // The Measurement Protocol answers 2xx even for a payload it then
    // discards, so a success here means delivered, not necessarily accepted.
    // Use GA4's DebugView or /debug/mp/collect to validate the shape.
    if (!res.ok) {
      console.error(`GA4 rejected purchase ${session.id}: HTTP ${res.status}`);
      return;
    }
    console.log(`Reported purchase ${session.id} to GA4: ${value} ${currency}`);

  } catch (err) {
    // Never fatal. The customer has already been served.
    //
    // The message is scrubbed of the API secret first. The Measurement
    // Protocol carries that secret in the query string — Google supports no
    // other transport — and a fetch failure is free to quote the URL it was
    // given. Scrubbing makes it impossible for the secret to reach a log
    // regardless of what the error text turns out to contain.
    const secret = process.env.GA4_API_SECRET;
    let message = (err && err.message) || String(err);
    if (secret) message = message.split(secret).join('[redacted]');
    console.error(`Could not report purchase ${session.id} to GA4:`, message);
  }
}


// Which GA4 user to credit the purchase to.
//
// analytics.js stamps the browser's GA4 client id onto every Stripe link as
// client_reference_id, encoded `ga-<digits>-<digits>` because Stripe allows
// no dots. When it survives the round trip, the purchase joins the same user
// and the same session as the click that started it, and the traffic source
// that produced the sale is preserved.
//
// When it does not — a payment link opened straight from an email, a blocked
// analytics script — the id is derived from the Stripe session instead. That
// is deliberately deterministic: a webhook retry must not invent a second
// user, because GA4 only collapses two purchases sharing a transaction id if
// they also share a user. Revenue lands correctly; acquisition reads direct.
function ga4ClientId(session) {
  const forwarded = /^ga-(\d+)-(\d+)$/.exec(session.client_reference_id || '');
  if (forwarded) return `${forwarded[1]}.${forwarded[2]}`;

  const digest = crypto.createHash('sha256').update(session.id).digest();
  return `${digest.readUInt32BE(0)}.${digest.readUInt32BE(4)}`;
}


function generateTempPassword() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789';
  let password = '';
  for (let i = 0; i < 12; i++) {
    password += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return password;
}
