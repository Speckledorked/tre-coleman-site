-- Per-student lesson progress for the Catering Profit System.
--
-- Run this once in the Supabase SQL editor (Dashboard -> SQL Editor -> New
-- query -> Run). It is idempotent, so running it twice is harmless.
--
-- netlify/functions/course-progress.js is the only thing that touches this
-- table, and it does so with the service key after verifying the caller's
-- Bearer token and their has_course_access flag.

create table if not exists public.lesson_progress (
  user_id      uuid        not null references auth.users (id) on delete cascade,
  lesson_id    text        not null,
  completed_at timestamptz not null default now(),
  primary key (user_id, lesson_id)
);

-- The endpoint always filters by user_id, and the primary key's leading column
-- already serves that, so no extra index is needed.

-- RLS on with no policies: the anon key cannot read or write this table at
-- all. That is deliberate. Every access goes through course-progress.js, which
-- checks the token and the access flag first, so the gate does not depend on a
-- policy being written correctly. If you later want the client to read its own
-- rows directly, add a policy then -- do not disable RLS to make it work.
alter table public.lesson_progress enable row level security;

-- A deleted account takes its progress with it, via the cascade above. Nothing
-- else references this table, so dropping it loses only completion ticks.
