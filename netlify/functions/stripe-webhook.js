const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const { createClient } = require('@supabase/supabase-js');
const { Resend } = require('resend');

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
);

const resend = new Resend(process.env.RESEND_API_KEY);

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

    console.log(`Processing purchase for: ${customerEmail}`);

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
                <a href="https://trecoleman.com/login.html" style="background: #F4A460; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">Access Your Course</a>
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
                <a href="https://trecoleman.com/login.html" style="background: #F4A460; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">Log In Now</a>
              </p>

              <p><strong>Course launches March 30th, 2026.</strong> You'll receive another email when the content is live!</p>

              <p style="margin-top: 30px; color: #666;">Let's fix those profit leaks!</p>
              <p style="color: #666;">— Tre Coleman</p>
            </div>
          `
        });

        console.log(`New user created with course access: ${customerEmail}`);
      }

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

function generateTempPassword() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789';
  let password = '';
  for (let i = 0; i < 12; i++) {
    password += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return password;
}
