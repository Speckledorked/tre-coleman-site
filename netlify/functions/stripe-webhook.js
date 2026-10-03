const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const { createClient } = require('@supabase/supabase-js');
const { Resend } = require('resend');
const crypto = require('crypto');

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

  // Handle the checkout.session.completed event
  if (stripeEvent.type === 'checkout.session.completed') {
    const session = stripeEvent.data.object;

    // Get customer email from session
    const customerEmail = session.customer_details?.email || session.customer_email;

    if (!customerEmail) {
      console.error('No customer email in session');
      return { statusCode: 400, body: 'No customer email' };
    }

    // If a course price ID is configured, verify this payment is for the course.
    // This prevents ad-hoc service payments from triggering course access.
    const coursePriceId = process.env.STRIPE_COURSE_PRICE_ID;
    // Describes the purchase to GA4 further down. Stays null when no course
    // price is configured, because nothing then needs to read the line items
    // and an extra Stripe call on every payment would buy nothing.
    let lineItems = null;
    if (coursePriceId) {
      const items = await stripe.checkout.sessions.listLineItems(session.id, { limit: 5 });
      lineItems = items.data;
      const isCoursePayment = lineItems.some(item => item.price?.id === coursePriceId);
      if (!isCoursePayment) {
        console.log(`Payment from ${customerEmail} is not for the course (session ${session.id}). Skipping course access.`);
        // Not the course, but still money taken: the $350 Snapshot finishes
        // on Stripe's own page and never touches the site, so this is the
        // only place it can be counted.
        await reportPurchaseToGA4(stripeEvent, lineItems);
        return { statusCode: 200, body: 'Non-course payment acknowledged' };
      }
    }

    console.log(`Processing course purchase for: ${customerEmail}`);

    try {
      // Check if user already exists
      const { data: existingUser } = await supabase
        .from('users')
        .select('id, name')
        .eq('email', customerEmail.toLowerCase())
        .single();

      if (existingUser) {
        // User exists - grant course access
        await supabase
          .from('users')
          .update({
            has_course_access: true,
            stripe_customer_id: session.customer,
            course_purchased_at: new Date().toISOString()
          })
          .eq('id', existingUser.id);

        // Send access granted email
        await resend.emails.send({
          from: 'Tre Coleman <noreply@trecoleman.com>',
          to: customerEmail,
          subject: 'Your Course Access is Ready! - The Catering Profit System',
          html: `
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
              <h1 style="color: #1F4788;">You're In! Course Access Granted</h1>
              <p>Hi ${existingUser.name || 'there'},</p>
              <p>Thank you for purchasing <strong>The Catering Profit System</strong>!</p>
              <p>Your account has been updated with full course access. You can log in now to start learning:</p>
              <p style="margin: 30px 0;">
                <a href="${SITE}/login.html" style="background: #F4A460; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">Access Your Course</a>
              </p>
              <p><strong>Course launches March 30th, 2026.</strong> You'll receive another email when the content is live!</p>
              <p style="margin-top: 30px; color: #666;">Let's fix those profit leaks!</p>
              <p style="color: #666;">— Tre Coleman</p>
            </div>
          `
        });

        console.log(`Course access granted for existing user: ${customerEmail}`);
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
        await supabase
          .from('users')
          .insert({
            id: authData.user.id,
            email: customerEmail.toLowerCase(),
            name: session.customer_details?.name || 'Course Student',
            has_course_access: true,
            stripe_customer_id: session.customer,
            course_purchased_at: new Date().toISOString(),
            created_at: new Date().toISOString()
          });

        // Send welcome + course access email with temp password
        await resend.emails.send({
          from: 'Tre Coleman <noreply@trecoleman.com>',
          to: customerEmail,
          subject: 'Welcome! Your Course Access + Login Details - The Catering Profit System',
          html: `
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
              <h1 style="color: #1F4788;">Welcome to The Catering Profit System!</h1>
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

              <p><strong>Course launches March 30th, 2026.</strong> You'll receive another email when the content is live!</p>

              <p style="margin-top: 30px; color: #666;">Let's fix those profit leaks!</p>
              <p style="color: #666;">— Tre Coleman</p>
            </div>
          `
        });

        console.log(`New user created with course access: ${customerEmail}`);
      }

      // Last, and never in a way that can fail the purchase: access is
      // granted and the email is away by this point.
      await reportPurchaseToGA4(stripeEvent, lineItems);

      return { statusCode: 200, body: 'Success' };

    } catch (error) {
      console.error('Error processing purchase:', error);

      // Send notification to admin about failed processing
      try {
        await resend.emails.send({
          from: 'System <noreply@trecoleman.com>',
          to: 'hello@trecoleman.com',
          subject: 'ALERT: Failed to process course purchase',
          html: `
            <p>Failed to automatically process purchase for: ${customerEmail}</p>
            <p>Stripe Session ID: ${session.id}</p>
            <p>Error: ${error.message}</p>
            <p>Please manually grant course access.</p>
          `
        });
      } catch (e) {
        console.error('Failed to send admin alert:', e);
      }

      return { statusCode: 500, body: 'Processing error' };
    }
  }

  return { statusCode: 200, body: 'Event received' };
};

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
    console.error(`Could not report purchase ${session.id} to GA4:`, err.message);
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
