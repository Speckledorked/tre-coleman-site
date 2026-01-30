const { createClient } = require('@supabase/supabase-js');
const { Resend } = require('resend');

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
);

const resend = new Resend(process.env.RESEND_API_KEY);

exports.handler = async (event) => {
  // Only allow POST
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: JSON.stringify({ error: 'Method not allowed' }) };
  }

  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
  };

  try {
    const { email, password, name } = JSON.parse(event.body);

    // Validate input
    if (!email || !password || !name) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ error: 'Email, password, and name are required' })
      };
    }

    if (password.length < 8) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ error: 'Password must be at least 8 characters' })
      };
    }

    // Create user in Supabase Auth
    const { data: authData, error: authError } = await supabase.auth.admin.createUser({
      email,
      password,
      email_confirm: true, // Auto-confirm email for simplicity
      user_metadata: { name }
    });

    if (authError) {
      // Check if user already exists
      if (authError.message.includes('already been registered')) {
        return {
          statusCode: 409,
          headers,
          body: JSON.stringify({ error: 'An account with this email already exists' })
        };
      }
      throw authError;
    }

    // Create user profile in our users table
    const { error: profileError } = await supabase
      .from('users')
      .insert({
        id: authData.user.id,
        email: email.toLowerCase(),
        name,
        has_course_access: false,
        created_at: new Date().toISOString()
      });

    if (profileError) {
      console.error('Profile creation error:', profileError);
      // Continue anyway - user can still log in
    }

    // Send welcome email
    try {
      await resend.emails.send({
        from: 'Tre Coleman <noreply@trecoleman.com>',
        to: email,
        subject: 'Welcome to Tre Coleman - Account Created',
        html: `
          <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #1F4788;">Welcome, ${name}!</h1>
            <p>Your account has been created successfully.</p>
            <p>You can now <a href="https://trecoleman.com/login.html" style="color: #F4A460;">log in to your account</a>.</p>
            <p style="margin-top: 30px; color: #666;">— Tre Coleman</p>
          </div>
        `
      });
    } catch (emailError) {
      console.error('Welcome email error:', emailError);
      // Continue anyway - account is created
    }

    return {
      statusCode: 201,
      headers,
      body: JSON.stringify({
        success: true,
        message: 'Account created successfully',
        user: { id: authData.user.id, email, name }
      })
    };

  } catch (error) {
    console.error('Registration error:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: 'Failed to create account. Please try again.' })
    };
  }
};
