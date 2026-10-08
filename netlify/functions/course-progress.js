/**
 * Per-student lesson progress for the Catering Profit System.
 *
 * The course pages are static and the site has no server session, but it does
 * already have real accounts: Supabase auth, a `users` row per buyer, and a
 * `has_course_access` flag. So progress does not need a new identity system —
 * it needs one table and this endpoint, reusing the Bearer-token model the
 * rest of the course uses.
 *
 * The identity ALWAYS comes from the verified token, never from the request.
 * A body field naming the user would let any signed-in buyer write to — or
 * read — another buyer's row, which is the obvious way to get this wrong.
 *
 * lesson_id is checked against a fixed allowlist rather than accepted as free
 * text. The table would otherwise accumulate whatever anyone posted, and a
 * completion count computed from `select count(*)` would be inflatable by
 * posting twenty variations of the same lesson.
 *
 * Deliberately NOT done: row-level security as the only gate. RLS is enabled
 * on the table with no policies, so the anon key cannot read it at all and
 * every access goes through the service key here, after this function has
 * checked the token and the access flag. That matches how course-download.js
 * reads `has_course_access` — the answer does not depend on a policy being
 * written correctly.
 *
 * The table this needs (run once, see tools/sql/lesson_progress.sql):
 *
 *   create table public.lesson_progress (
 *     user_id      uuid        not null references auth.users(id) on delete cascade,
 *     lesson_id    text        not null,
 *     completed_at timestamptz not null default now(),
 *     primary key (user_id, lesson_id)
 *   );
 */

const { createClient } = require('@supabase/supabase-js');

/**
 * Five modules of four lessons, plus the bonus roadmap. The ids are opaque on
 * purpose: they are short, stable, and carry no title text, so renaming a
 * lesson never orphans a student's completed row.
 */
const LESSONS = (() => {
  const ids = [];
  for (let m = 1; m <= 5; m += 1) {
    for (let l = 1; l <= 4; l += 1) ids.push(`m${m}l${l}`);
  }
  ids.push('bonus');
  return new Set(ids);
})();

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
};

function json(statusCode, body) {
  return {
    statusCode,
    headers: { ...CORS, 'Content-Type': 'application/json', 'Cache-Control': 'no-store' },
    body: JSON.stringify(body),
  };
}

exports.handler = async (event) => {
  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers: CORS, body: '' };
  }
  if (event.httpMethod !== 'GET' && event.httpMethod !== 'POST') {
    return json(405, { error: 'Method not allowed' });
  }

  const authHeader = event.headers.authorization || event.headers.Authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return json(401, { error: 'Sign in to track your progress' });
  }
  const token = authHeader.slice('Bearer '.length);

  if (!process.env.SUPABASE_URL || !process.env.SUPABASE_ANON_KEY ||
      !process.env.SUPABASE_SERVICE_KEY) {
    console.error('course-progress: Supabase environment variables are missing');
    return json(500, { error: 'Progress tracking is unavailable right now' });
  }

  let user;
  try {
    const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_ANON_KEY);
    const { data, error } = await supabase.auth.getUser(token);
    if (error || !data || !data.user) {
      return json(401, { error: 'Your session has expired. Please sign in again.' });
    }
    user = data.user;
  } catch (err) {
    console.error('course-progress: token verification failed', err);
    return json(500, { error: 'Progress tracking is unavailable right now' });
  }

  const service = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY);

  try {
    const { data: profile, error } = await service
      .from('users')
      .select('has_course_access')
      .eq('id', user.id)
      .single();
    if (error) {
      console.error('course-progress: profile lookup failed', error);
      return json(500, { error: 'Progress tracking is unavailable right now' });
    }
    if (!profile || !profile.has_course_access) {
      return json(403, { error: 'This is part of the Catering Profit System' });
    }
  } catch (err) {
    console.error('course-progress: profile lookup threw', err);
    return json(500, { error: 'Progress tracking is unavailable right now' });
  }

  if (event.httpMethod === 'GET') {
    try {
      const { data, error } = await service
        .from('lesson_progress')
        .select('lesson_id, completed_at')
        .eq('user_id', user.id);
      if (error) {
        console.error('course-progress: read failed', error);
        return json(500, { error: 'Progress tracking is unavailable right now' });
      }
      // Filter on the way out too: a row for a lesson that no longer exists
      // should not count toward the total the page displays.
      const completed = (data || [])
        .filter((r) => LESSONS.has(r.lesson_id))
        .map((r) => r.lesson_id);
      return json(200, { completed, total: LESSONS.size });
    } catch (err) {
      console.error('course-progress: read threw', err);
      return json(500, { error: 'Progress tracking is unavailable right now' });
    }
  }

  let payload;
  try {
    payload = JSON.parse(event.body || '{}');
  } catch (err) {
    return json(400, { error: 'Malformed request' });
  }

  const lessonId = typeof payload.lesson_id === 'string' ? payload.lesson_id : '';
  if (!LESSONS.has(lessonId)) {
    return json(400, { error: 'Unknown lesson' });
  }
  const done = payload.completed !== false;

  try {
    if (done) {
      // The primary key is (user_id, lesson_id), so re-marking a lesson is a
      // no-op rather than a duplicate row.
      const { error } = await service
        .from('lesson_progress')
        .upsert({ user_id: user.id, lesson_id: lessonId }, { onConflict: 'user_id,lesson_id' });
      if (error) {
        console.error('course-progress: upsert failed', error);
        return json(500, { error: 'Could not save that just now' });
      }
    } else {
      const { error } = await service
        .from('lesson_progress')
        .delete()
        .eq('user_id', user.id)
        .eq('lesson_id', lessonId);
      if (error) {
        console.error('course-progress: delete failed', error);
        return json(500, { error: 'Could not save that just now' });
      }
    }
  } catch (err) {
    console.error('course-progress: write threw', err);
    return json(500, { error: 'Could not save that just now' });
  }

  return json(200, { lesson_id: lessonId, completed: done });
};
