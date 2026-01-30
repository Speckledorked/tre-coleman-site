const { createClient } = require('@supabase/supabase-js');
const { Resend } = require('resend');

const resend = new Resend(process.env.RESEND_API_KEY);

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

  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: JSON.stringify({ error: 'Method not allowed' }) };
  }

  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
  };

  try {
    const { email } = JSON.parse(event.body);

    if (!email) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ error: 'Email is required' })
      };
    }

    const supabase = createClient(
      process.env.SUPABASE_URL,
      process.env.SUPABASE_SERVICE_KEY
    );

    // Check if user exists
    const { data: users } = await supabase
      .from('users')
      .select('id, name')
      .eq('email', email.toLowerCase())
      .limit(1);

    // Always return success to prevent email enumeration
    if (!users || users.length === 0) {
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          success: true,
          message: 'If an account exists with this email, you will receive a password reset link.'
        })
      };
    }

    // Generate password reset link via Supabase
    const { data, error } = await supabase.auth.admin.generateLink({
      type: 'recovery',
      email,
      options: {
        redirectTo: 'https://trecoleman.com/reset-password.html'
      }
    });

    if (error) {
      console.error('Reset link generation error:', error);
      throw error;
    }

    // Extract the token from the link
    const resetUrl = data.properties.action_link;

    // Send password reset email
    await resend.emails.send({
      from: 'Tre Coleman <noreply@trecoleman.com>',
      to: email,
      subject: 'Reset Your Password - Tre Coleman',
      html: `
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
          <h1 style="color: #1F4788;">Password Reset Request</h1>
          <p>Hi ${users[0].name || 'there'},</p>
          <p>We received a request to reset your password. Click the button below to create a new password:</p>
          <p style="margin: 30px 0;">
            <a href="${resetUrl}" style="background: #F4A460; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">Reset Password</a>
          </p>
          <p style="color: #666; font-size: 14px;">This link will expire in 1 hour. If you didn't request this, you can safely ignore this email.</p>
          <p style="margin-top: 30px; color: #666;">— Tre Coleman</p>
        </div>
      `
    });

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        success: true,
        message: 'If an account exists with this email, you will receive a password reset link.'
      })
    };

  } catch (error) {
    console.error('Forgot password error:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: 'Failed to process request. Please try again.' })
    };
  }
};
