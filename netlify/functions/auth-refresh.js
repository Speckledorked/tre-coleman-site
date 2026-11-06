/**
 * Exchanges a refresh token for a live session.
 *
 * WHY THIS EXISTS
 *
 * auth-login stored `refresh_token` and `expires_at` in the browser from the
 * day it shipped, and nothing ever read them. A Supabase access token expires
 * (an hour by default), so every signed-in student's token simply died and
 * nothing renewed it. What that looked like from the outside: the course
 * pages kept working from an already-open tab, then a download answered 401,
 * course/downloads.js sent the student to /login.html?redirect=..., and
 * login.html -- which ignored that parameter until this change -- bounced
 * them to the dashboard. "The downloads don't work and it just goes to my
 * dashboard."
 *
 * The refresh token is the one credential that can mint a new session, so it
 * is sent in a POST body rather than a query string: a query string lands in
 * browser history, Netlify's access logs and any onward Referer, which is the
 * same reasoning course-download.js gives for not accepting a token that way.
 *
 * The response shape is auth-login's, exactly, so the browser stores the
 * result the same way it stores a login and nothing downstream can tell the
 * difference. The courses list is re-read here rather than carried over,
 * because a purchase made since the student signed in should take effect on
 * the next refresh rather than waiting for them to sign out.
 */

const { createClient } = require('@supabase/supabase-js');
const { coursesForUser } = require('./lib/access.js');

exports.handler = async (event) => {
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
      },
      body: ''
    };
  }

  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json',
    // A session must never be stored by a shared cache.
    'Cache-Control': 'no-store'
  };

  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, headers, body: JSON.stringify({ error: 'Method not allowed' }) };
  }

  if (!process.env.SUPABASE_URL || !process.env.SUPABASE_ANON_KEY ||
      !process.env.SUPABASE_SERVICE_KEY) {
    console.error('auth-refresh: Supabase environment variables are missing');
    return { statusCode: 500, headers, body: JSON.stringify({ error: 'Could not refresh your session' }) };
  }

  let refreshToken;
  try {
    ({ refresh_token: refreshToken } = JSON.parse(event.body || '{}'));
  } catch (_) {
    return { statusCode: 400, headers, body: JSON.stringify({ error: 'Malformed request' }) };
  }
  if (!refreshToken || typeof refreshToken !== 'string') {
    return { statusCode: 400, headers, body: JSON.stringify({ error: 'No refresh token' }) };
  }

  let data;
  try {
    const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_ANON_KEY);
    const result = await supabase.auth.refreshSession({ refresh_token: refreshToken });
    if (result.error || !result.data || !result.data.session || !result.data.user) {
      // A spent or revoked refresh token is a normal end of session, not a
      // fault: 401 tells the browser to ask the student to sign in again.
      return {
        statusCode: 401,
        headers,
        body: JSON.stringify({ error: 'Your session has expired. Please sign in again.' })
      };
    }
    data = result.data;
  } catch (err) {
    console.error('auth-refresh: refreshSession threw', err);
    return { statusCode: 500, headers, body: JSON.stringify({ error: 'Could not refresh your session' }) };
  }

  const serviceSupabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY);

  const { data: profile, error: profileError } = await serviceSupabase
    .from('users')
    .select('name, has_course_access')
    .eq('id', data.user.id)
    .single();

  // Same rule as auth-login and auth-verify: PGRST116 is "no row matched" and
  // is legitimate; anything else means the lookup failed, and reporting no
  // access on a failed lookup locks a buyer out of what they paid for.
  if (profileError && profileError.code !== 'PGRST116') {
    console.error('auth-refresh: profile lookup failed for', data.user.id, profileError);
    return { statusCode: 500, headers, body: JSON.stringify({ error: 'Could not refresh your session' }) };
  }

  let courseSlugs;
  try {
    ({ slugs: courseSlugs } = await coursesForUser(
      serviceSupabase, data.user.id, profile && profile.has_course_access
    ));
  } catch (e) {
    return { statusCode: 500, headers, body: JSON.stringify({ error: 'Could not refresh your session' }) };
  }

  return {
    statusCode: 200,
    headers,
    body: JSON.stringify({
      success: true,
      session: {
        access_token: data.session.access_token,
        refresh_token: data.session.refresh_token,
        expires_at: data.session.expires_at
      },
      user: {
        id: data.user.id,
        email: data.user.email,
        name: (profile && profile.name) || data.user.user_metadata?.name || 'User',
        has_course_access: courseSlugs.includes('catering-profit'),
        courses: courseSlugs
      }
    })
  };
};
