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
4. Select events — all three:
   - `checkout.session.completed`
   - `checkout.session.async_payment_succeeded`
   - `checkout.session.async_payment_failed`
5. Save the **Webhook Signing Secret** (starts with `whsec_`)

## Environment Variables

Add these to your Netlify site (Site configuration > Environment variables).
All nine are required. A missing variable does not fail the build — the
affected function fails silently at runtime, so the site looks fine while
signups, logins, purchases or the directory quietly stop working.

See `.env.example` in the repository root for the same list with notes.

| Variable | Description | Format | Recoverable later? |
|---|---|---|---|
| `SUPABASE_URL` | Supabase project URL | `https://xxxxx.supabase.co` | Yes — also in `course/config.js` |
| `SUPABASE_ANON_KEY` | Supabase anon/public key | `eyJhbGciOi...` | Yes — also in `course/config.js` |
| `SUPABASE_SERVICE_KEY` | Service role key (**secret**, bypasses RLS) | `eyJhbGciOi...` | Yes — viewable in dashboard |
| `STRIPE_SECRET_KEY` | Stripe secret key | `sk_live_xxxxx` | Yes — revealable in dashboard |
| `STRIPE_WEBHOOK_SECRET` | Webhook signing secret | `whsec_xxxxx` | **No** — tied to one endpoint URL |
| `STRIPE_COURSE_PRICE_ID` | Price ID of the course (not a payment link) | `price_xxxxx` | Yes — lookup in Products |
| `RESEND_API_KEY` | Resend API key | `re_xxxxx` | **No** — shown once |
| `AIRTABLE_TOKEN` | Airtable personal access token | `patxxxxx...` | **No** — shown once |
| `CHAT_PASSWORD` | Shared password for the premium AI chat | any string | **No** — self-chosen |
| `GA4_API_SECRET` | Measurement Protocol secret for server-side revenue (optional) | opaque string | **No** — shown once |

### The one that is optional

**`GA4_API_SECRET` is the only variable the site runs fine without.** It lets
`stripe-webhook.js` report what each purchase was worth to GA4. Leave it unset
and purchases are simply never reported — the function logs a warning naming
the session it skipped, and the `purchase` conversion in GA4 stays at zero
while Stripe shows sales. Create it in GA4 under Admin -> Data streams -> the
web stream -> Measurement Protocol API secrets.

It is not the measurement ID. That is `G-778929FT8G`, it is public, and it is
hardcoded in both `analytics.js` and `stripe-webhook.js` — `tools/check_site.py`
fails if those two ever disagree.

### Three that are easy to get wrong

**`STRIPE_COURSE_PRICE_ID` must be a price ID, not a payment link.**
`netlify/functions/stripe-webhook.js:45-48` matches it against the checkout
session's line items to decide whether a payment grants course access. If it
is wrong, customers are charged and receive nothing.

**`STRIPE_WEBHOOK_SECRET` cannot be recovered and must be regenerated whenever
the site URL changes.** Create the endpoint at
`<site>/.netlify/functions/stripe-webhook`, subscribe it to
the three `checkout.session.*` events listed above, then copy that endpoint's
signing secret.

**Subscribe to all three, not just `checkout.session.completed`.** A card
payment is already `paid` when the session completes, but an asynchronous
method — a bank debit, Klarna, boleto — completes the session `unpaid` and
settles minutes or days later. The function refuses to grant access on an
unpaid session (it would otherwise hand over the course before any money
moved), and grants it on `async_payment_succeeded` instead. Subscribed only
to `completed`, such a customer is charged and never let in; you would get an
"awaiting payment" alert and then silence. It is verified at `stripe-webhook.js:21-24`.

**`AIRTABLE_TOKEN` needs read AND write scope on base `appk7mBGffiWhowPC`**
(table `Listings`), which is hardcoded at `airtable-proxy.js:3-4`. The base is
not configurable by environment variable.

### Also required, but not environment variables

- **Resend domain verification.** The code sends from
  `noreply@trecoleman.com` (`auth-register.js`, `auth-forgot-password.js`,
  `stripe-webhook.js`). That domain must be verified in Resend with live
  DKIM/SPF records, or registration and password-reset email fails despite a
  valid API key.
- **Supabase row-level security must be ENABLED on every table.** This
  repository is public, so `SUPABASE_ANON_KEY` is public too. That is safe by
  design *only* while RLS is on. See "Verifying row-level security" below.

## Verifying row-level security

This repository is **public**, so `SUPABASE_ANON_KEY` is public. That is safe
by design — but only while row-level security is *enabled* on every table.
Having a policy is not the same as having RLS on: a policy on a table with RLS
disabled does nothing, and the anon key can then read and write the table
freely.

Run this in the Supabase SQL editor. Every row must read `rls_enabled = true`:

```sql
select
  c.relname                as table_name,
  c.relrowsecurity         as rls_enabled,
  c.relforcerowsecurity    as rls_forced,
  count(p.polname)         as policy_count
from pg_class c
join pg_namespace n on n.oid = c.relnamespace
left join pg_policy p on p.polrelid = c.oid
where n.nspname = 'public'
  and c.relkind = 'r'
group by c.relname, c.relrowsecurity, c.relforcerowsecurity
order by c.relrowsecurity, c.relname;
```

Anything with `rls_enabled = false` is readable by anyone who has the anon key,
which is everyone. Enable it:

```sql
alter table public.<table_name> enable row level security;
```

A table showing `rls_enabled = true` but `policy_count = 0` is the opposite
problem: locked to everyone including your own app. Both states are worth
catching.

Re-run the query after any schema change.

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
