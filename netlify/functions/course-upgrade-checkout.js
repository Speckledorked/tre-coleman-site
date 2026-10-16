/**
 * Creates a Stripe Checkout Session for the upgrade, for ONE signed-in student
 * who already owns ONE course.
 *
 * WHY THIS EXISTS RATHER THAN A PAYMENT LINK
 *
 * The upgrade grants both courses, because a single Stripe price cannot know
 * which one the buyer is missing. As a public payment link that makes a $100
 * URL worth $297 to anyone who finds it, and Stripe payment links cannot be
 * gated on a previous purchase — "unlisted" is just a URL nobody has posted
 * yet. One forward in a Facebook group and the bundle is $100 for everybody.
 *
 * So there is no upgrade link. The student presses a button inside the course,
 * this function checks their token and what they actually own, and Stripe
 * returns a session URL good for that one checkout. Nothing to share, because
 * the URL only exists after the check has passed.
 *
 * Defence in depth: stripe-webhook.js STILL verifies on the way back in that
 * the buyer held a course, so a session obtained some other way grants
 * nothing. This function is the gate; that check is the lock.
 */

'use strict';

const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const { createClient } = require('@supabase/supabase-js');
const courses = require('./lib/courses.js');
const { coursesForUser } = require('./lib/access.js');

const UPGRADE = 'catering-upgrade';
const SITE = process.env.URL || 'https://trecoleman.com';

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
};

function json(statusCode, body) {
  return { statusCode, headers: { ...CORS, 'Content-Type': 'application/json' }, body: JSON.stringify(body) };
}

exports.handler = async (event) => {
  if (event.httpMethod === 'OPTIONS') return { statusCode: 200, headers: CORS, body: '' };
  // POST only: this creates something and takes money, so it must not be
  // reachable by a prefetch, a crawler, or a link someone clicks by accident.
  if (event.httpMethod !== 'POST') return json(405, { error: 'Method not allowed' });

  const authHeader = event.headers.authorization || event.headers.Authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return json(401, { error: 'Sign in first' });
  }
  const token = authHeader.slice('Bearer '.length);

  if (!process.env.SUPABASE_URL || !process.env.SUPABASE_ANON_KEY
      || !process.env.SUPABASE_SERVICE_KEY || !process.env.STRIPE_SECRET_KEY) {
    console.error('course-upgrade-checkout: environment variables are missing');
    return json(500, { error: 'Upgrades are unavailable right now' });
  }

  const priceId = courses.bundlePriceIdsFor(UPGRADE)[0];
  if (!priceId) {
    // The product has not been created in Stripe yet. Say so plainly in the
    // log rather than failing in a way that looks like the student's problem.
    console.error('course-upgrade-checkout: no upgrade price is configured. '
      + 'Add it to STRIPE_PRICE_IDS_CATERING_UPGRADE or to lib/courses.js.');
    return json(503, { error: 'The upgrade is not on sale yet' });
  }

  // Identity from the verified token, never from the request body.
  let user;
  try {
    const anon = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_ANON_KEY);
    const { data, error } = await anon.auth.getUser(token);
    if (error || !data || !data.user) {
      return json(401, { error: 'Your session has expired. Please sign in again.' });
    }
    user = data.user;
  } catch (err) {
    console.error('course-upgrade-checkout: token verification failed', err);
    return json(500, { error: 'Upgrades are unavailable right now' });
  }

  const service = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY);

  let held;
  try {
    const { data: profile, error } = await service
      .from('users')
      .select('has_course_access')
      .eq('id', user.id)
      .single();
    // PGRST116 is "no row matched", a legitimate state for an account with no
    // profile row yet.
    if (error && error.code !== 'PGRST116') {
      console.error('course-upgrade-checkout: profile lookup failed', error);
      return json(500, { error: 'Upgrades are unavailable right now' });
    }
    ({ slugs: held } = await coursesForUser(service, user.id, profile && profile.has_course_access));
  } catch (err) {
    // A failed lookup is an error, not a verdict. Answering "you own nothing"
    // here would refuse an upgrade to someone entitled to buy one.
    console.error('course-upgrade-checkout: access lookup threw', err);
    return json(500, { error: 'Upgrades are unavailable right now' });
  }

  const grants = courses.bundle(UPGRADE).grants;
  const owned = grants.filter((slug) => held.includes(slug));
  const missing = grants.filter((slug) => !held.includes(slug));

  if (!owned.length) {
    // Not an error and not a lecture: they simply need to buy a course first,
    // and the sales page is where that happens.
    return json(403, {
      error: 'The upgrade is for students who already own one of the courses.',
      buy: courses.course(grants[0]).salesPage,
    });
  }
  if (!missing.length) {
    return json(409, { error: 'You already have both courses.' });
  }

  try {
    const session = await stripe.checkout.sessions.create({
      mode: 'payment',
      line_items: [{ price: priceId, quantity: 1 }],
      customer_email: user.email,
      // Both carry the account, so the webhook can identify the buyer exactly
      // rather than matching on an email that may differ from the one on their
      // card. client_reference_id survives in the session; metadata is what
      // shows up when reading the payment in the dashboard.
      client_reference_id: user.id,
      metadata: {
        user_id: user.id,
        kind: 'upgrade',
        owned: owned.join(','),
        grants: grants.join(','),
      },
      success_url: `${SITE}/thank-you.html?upgrade=1`,
      cancel_url: `${SITE}/course/dashboard.html`,
    });

    console.log(`Upgrade session ${session.id} created for ${user.id} (owns ${owned.join(',')})`);
    return json(200, { url: session.url, adds: missing });
  } catch (err) {
    console.error('course-upgrade-checkout: could not create session', err);
    return json(500, { error: 'Could not start checkout. Please try again.' });
  }
};
