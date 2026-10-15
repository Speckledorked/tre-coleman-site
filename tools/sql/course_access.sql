-- Per-course access for students, replacing the single users.has_course_access
-- boolean now that there is more than one course.
--
-- Run this once in the Supabase SQL editor (Dashboard -> SQL Editor -> New
-- query -> Run). It is idempotent, so running it twice is harmless.
--
-- SAFE TO RUN BEFORE THE CODE DEPLOYS, AND SAFE TO DEPLOY THE CODE BEFORE
-- RUNNING THIS. The functions read this table and fall back to
-- users.has_course_access for the Catering Profit System, so neither order
-- locks an existing student out. Run it first by preference: then the
-- fallback is never needed.

create table if not exists public.course_access (
  user_id     uuid        not null references auth.users (id) on delete cascade,
  course_slug text        not null,
  granted_at  timestamptz not null default now(),
  -- Which Stripe checkout granted it, for reconciling a refund or a dispute
  -- against the row that let someone in. Null for the backfill below, which
  -- has no session to point at.
  session_id  text,
  primary key (user_id, course_slug)
);

-- The endpoints always filter by user_id, and the primary key's leading column
-- already serves that, so no extra index is needed.

-- RLS on with no policies: the anon key cannot read or write this table at
-- all. That is deliberate, and it matches lesson_progress. Every access goes
-- through a Netlify Function that checks the caller's Bearer token with the
-- service key first, so the gate does not depend on a policy being written
-- correctly. Do not disable RLS to make a client query work -- add a policy.
alter table public.course_access enable row level security;

-- ---------------------------------------------------------------------------
-- Backfill: everyone who already paid keeps what they paid for.
--
-- has_course_access was only ever the Catering Profit System, so that is the
-- only course it can grant. on conflict do nothing makes a re-run a no-op
-- rather than resetting granted_at, which would misreport when someone bought.
-- ---------------------------------------------------------------------------
insert into public.course_access (user_id, course_slug, granted_at)
select u.id,
       'catering-profit',
       coalesce(u.course_purchased_at, u.created_at, now())
from public.users u
where u.has_course_access is true
on conflict (user_id, course_slug) do nothing;

-- ---------------------------------------------------------------------------
-- users.has_course_access IS DELIBERATELY NOT DROPPED.
--
-- stripe-webhook.js keeps writing it alongside the new row for the Catering
-- Profit System, so this change can be rolled back by reverting the code
-- alone, with no second migration under a customer who is mid-purchase. It is
-- the fallback the functions read if this table is somehow empty for a user
-- who has the boolean.
--
-- Drop it only once the table has been authoritative for long enough to trust,
-- and once nothing reads it:
--
--     select count(*) from public.users where has_course_access is true;
--     select count(*) from public.course_access where course_slug = 'catering-profit';
--
-- Those two should agree before anyone considers:
--
--     alter table public.users drop column has_course_access;
--
-- Check the counts first. They disagreeing means a buyer exists in one place
-- and not the other, which is a person who cannot get in.
-- ---------------------------------------------------------------------------

-- A deleted account takes its access with it, via the cascade above.
