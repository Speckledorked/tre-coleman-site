const { createClient } = require('@supabase/supabase-js');
const { coursesForUser } = require('./lib/access.js');

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_ANON_KEY
);

exports.handler = async (event) => {
  // Handle preflight
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

  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: JSON.stringify({ error: 'Method not allowed' }) };
  }

  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
  };

  try {
    const { email, password } = JSON.parse(event.body);

    if (!email || !password) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ error: 'Email and password are required' })
      };
    }

    // Sign in with Supabase Auth
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    });

    if (error) {
      return {
        statusCode: 401,
        headers,
        body: JSON.stringify({ error: 'Invalid email or password' })
      };
    }

    // Get user profile with course access status
    const serviceSupabase = createClient(
      process.env.SUPABASE_URL,
      process.env.SUPABASE_SERVICE_KEY
    );

    const { data: profile, error: profileError } = await serviceSupabase
      .from('users')
      .select('name, has_course_access, stripe_customer_id')
      .eq('id', data.user.id)
      .single();

    // PGRST116 is "no row matched", which is a legitimate state for a user who
    // has signed up but has no profile row yet. Any other error means the
    // lookup itself failed, and the fallbacks below would then quietly report
    // has_course_access: false — telling a paying customer they have not
    // bought the course. Fail loudly instead.
    if (profileError && profileError.code !== 'PGRST116') {
      console.error('Profile lookup failed for', data.user.id, profileError);
      return {
        statusCode: 500,
        headers,
        body: JSON.stringify({ error: 'Login failed. Please try again.' })
      };
    }

    // Which courses this account holds. As with the profile lookup above, a
    // failed read must not become "no access" for someone who paid.
    let courseSlugs;
    try {
      ({ slugs: courseSlugs } = await coursesForUser(
        serviceSupabase, data.user.id, profile?.has_course_access
      ));
    } catch (e) {
      return {
        statusCode: 500,
        headers,
        body: JSON.stringify({ error: 'Login failed' })
      };
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
          name: profile?.name || data.user.user_metadata?.name || 'User',
          // Kept for anything still reading the single-course field. It now
          // means "holds the original course", which is what it always meant.
          has_course_access: courseSlugs.includes('catering-profit'),
          courses: courseSlugs
        }
      })
    };

  } catch (error) {
    console.error('Login error:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: 'Login failed. Please try again.' })
    };
  }
};
