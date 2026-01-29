# Course Delivery System Setup Guide

This guide walks you through setting up the user authentication and automated course delivery system for The Catering Profit System.

## Overview

The system includes:
- User registration and authentication
- Stripe webhook for automatic course access on purchase
- Protected course dashboard and module pages
- Automated email delivery via Resend
- Supabase for database and auth

## Required Services (All Free Tiers)

### 1. Supabase (Database + Auth)
1. Go to [supabase.com](https://supabase.com) and create a free account
2. Create a new project
3. Save these credentials:
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **Anon/Public Key** (safe for frontend)
   - **Service Role Key** (secret, for backend only)

4. Create the `users` table in Supabase SQL Editor:
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY REFERENCES auth.users(id),
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  has_course_access BOOLEAN DEFAULT FALSE,
  stripe_customer_id TEXT,
  course_purchased_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Policy: Users can read their own data
CREATE POLICY "Users can view own data" ON users
  FOR SELECT USING (auth.uid() = id);

-- Policy: Service role can do everything (for webhooks)
CREATE POLICY "Service role full access" ON users
  FOR ALL USING (auth.role() = 'service_role');
```

### 2. Resend (Email Service)
1. Go to [resend.com](https://resend.com) and create a free account
2. Add and verify your domain (trecoleman.com)
3. Create an API key
4. Save the **API Key**

### 3. Stripe Webhook
1. Go to your [Stripe Dashboard](https://dashboard.stripe.com)
2. Navigate to Developers > Webhooks
3. Add endpoint: `https://trecoleman.com/.netlify/functions/stripe-webhook`
4. Select events: `checkout.session.completed`
5. Save the **Webhook Signing Secret** (starts with `whsec_`)

## Environment Variables

Add these to your Netlify site (Site Settings > Environment Variables):

| Variable | Description | Example |
|----------|-------------|---------|
| `SUPABASE_URL` | Your Supabase project URL | `https://xxxxx.supabase.co` |
| `SUPABASE_ANON_KEY` | Supabase anon/public key | `eyJhbGciOiJIUzI1NiIs...` |
| `SUPABASE_SERVICE_KEY` | Supabase service role key (secret) | `eyJhbGciOiJIUzI1NiIs...` |
| `RESEND_API_KEY` | Resend API key | `re_xxxxx` |
| `STRIPE_SECRET_KEY` | Stripe secret key | `sk_live_xxxxx` |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret | `whsec_xxxxx` |

## File Structure

```
tre-coleman-site/
├── netlify/
│   └── functions/
│       ├── auth-register.js      # User registration
│       ├── auth-login.js         # User login
│       ├── auth-verify.js        # Session verification
│       ├── auth-forgot-password.js # Password reset request
│       └── stripe-webhook.js     # Stripe purchase handler
├── course/
│   ├── auth.js                   # Client-side auth helper
│   ├── dashboard.html            # Course dashboard
│   ├── no-access.html            # No access page
│   ├── module-1.html             # Module 1: Labor Cost Control
│   ├── module-2.html             # Module 2: Pricing
│   ├── module-3.html             # Module 3: Food Cost
│   ├── module-4.html             # Module 4: Logistics
│   ├── module-5.html             # Module 5: Cash Flow
│   └── bonus.html                # Bonus: 90-Day Plan
├── login.html                    # Login page
├── register.html                 # Registration page
├── forgot-password.html          # Forgot password page
├── reset-password.html           # Reset password page
└── package.json                  # Dependencies
```

## How It Works

### User Flow

1. **New Purchase (no account)**:
   - User buys course via Stripe
   - Webhook creates account with temp password
   - User receives email with login credentials
   - User logs in and accesses course

2. **Existing User Purchase**:
   - User buys course via Stripe
   - Webhook grants course access to existing account
   - User receives confirmation email
   - User logs in to access course

3. **Registration (without purchase)**:
   - User creates account
   - User can log in but sees "no access" on dashboard
   - Prompted to purchase course

### Authentication

- Sessions stored in `localStorage`
- Token verified on each protected page load
- Automatic redirect to login if session invalid
- Course access checked separately from login

## Testing Locally

1. Install dependencies:
```bash
npm install
```

2. Install Netlify CLI:
```bash
npm install -g netlify-cli
```

3. Create `.env` file with your environment variables

4. Run locally:
```bash
netlify dev
```

5. Test Stripe webhooks locally with Stripe CLI:
```bash
stripe listen --forward-to localhost:8888/.netlify/functions/stripe-webhook
```

## Deployment

1. Push changes to git
2. Netlify will auto-deploy
3. Verify environment variables are set
4. Test a purchase in Stripe test mode
5. Go live!

## Adding Video Content

When course launches (March 30th), update each module page:

1. Remove the `video-placeholder` div
2. Add YouTube embed:
```html
<div class="video-container">
  <iframe
    src="https://www.youtube.com/embed/YOUR_VIDEO_ID"
    frameborder="0"
    allowfullscreen>
  </iframe>
</div>
```

3. Update lesson links to navigate between videos
4. Add download links for templates

## Troubleshooting

### User not getting course access after purchase
1. Check Stripe webhook logs in dashboard
2. Verify webhook endpoint is correct
3. Check Netlify function logs
4. Manually grant access in Supabase if needed

### Emails not sending
1. Verify Resend API key
2. Check domain verification in Resend
3. Check Netlify function logs for errors

### Login not working
1. Check Supabase auth settings
2. Verify SUPABASE_URL and keys are correct
3. Check browser console for errors

## Support

Questions? Email hello@trecoleman.com
