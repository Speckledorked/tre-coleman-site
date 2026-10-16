/**
 * Reading which courses a user may open.
 *
 * One implementation, shared by auth-login, auth-verify, course-progress and
 * course-download, because four copies of an access check is four places for
 * them to drift apart — and the way they drift is one of them saying no to
 * someone who paid.
 *
 * TWO FAILURE MODES THIS IS WRITTEN AROUND
 *
 * 1. A FAILED LOOKUP IS NOT "NO ACCESS". auth-verify.js already carried this
 *    rule for the old boolean, and the comment there is worth keeping: every
 *    page in the course calls it on load, so answering "no access" when the
 *    query merely failed locks a paying customer out of what they bought. So
 *    a real query error throws, and the caller returns 500 — an error the
 *    student can retry, not a verdict.
 *
 * 2. THE TABLE MIGHT NOT EXIST YET. tools/sql/course_access.sql has to be run
 *    by hand in the Supabase dashboard, and nothing forces that to happen
 *    before this code deploys. A missing table is therefore an expected state,
 *    not an error: it falls back to users.has_course_access and warns. Without
 *    that, deploying before running the migration would 500 every login on the
 *    site.
 */

'use strict';

const courses = require('./courses.js');

/**
 * Postgres undefined_table, and PostgREST's own code for a table it cannot
 * find in its schema cache.
 *
 * PGRST205 is what the live project actually returns — verified against it
 * with the public anon key, which answers 404 / PGRST205 for a table that does
 * not exist and an empty array for one that exists but is closed by RLS.
 * 42P01 is the SQLSTATE underneath, kept because PostgREST passes it through
 * in other situations.
 */
const MISSING_TABLE_CODES = new Set(['42P01', 'PGRST205']);

function tableIsMissing(error) {
  if (!error) return false;
  if (MISSING_TABLE_CODES.has(error.code)) return true;
  // Belt and braces: PostgREST has worded this differently across versions,
  // and mistaking "table missing" for a real failure 500s every login.
  return /relation .*course_access.* does not exist|could not find the table/i
    .test(String(error.message || ''));
}

/**
 * Every course slug this user may open.
 *
 * @param supabase   a client built with the SERVICE key — this table has RLS
 *                   on with no policies, so the anon key reads nothing
 * @param userId     the id from the VERIFIED token, never from a request body
 * @param legacyFlag users.has_course_access, already fetched by the caller
 * @returns {Promise<{slugs: string[], legacyOnly: boolean}>}
 *          legacyOnly is true when the answer came from the boolean alone,
 *          which means the migration has not been run yet.
 * @throws  on a real query failure, so the caller can answer 500 rather than
 *          telling a buyer they have nothing.
 */
async function coursesForUser(supabase, userId, legacyFlag) {
  const slugs = new Set();

  // The boolean only ever meant the one course, and only that course honours
  // it. Applied first so it still holds if the table read falls over.
  const legacyCourse = courses.SLUGS.find((slug) => courses.hasLegacyFlag(slug));
  if (legacyFlag && legacyCourse) slugs.add(legacyCourse);

  const { data, error } = await supabase
    .from('course_access')
    .select('course_slug')
    .eq('user_id', userId);

  if (error) {
    if (tableIsMissing(error)) {
      console.warn(
        'course_access does not exist yet, so access is falling back to '
        + 'users.has_course_access and only the Catering Profit System can be '
        + 'granted. Run tools/sql/course_access.sql in the Supabase SQL editor.'
      );
      return { slugs: [...slugs], legacyOnly: true };
    }
    // A real failure. Let the caller turn this into a 500.
    console.error('course_access lookup failed for', userId, error.message);
    throw new Error(`course_access lookup failed: ${error.message}`);
  }

  for (const row of data || []) {
    // Ignore a slug no longer in the registry rather than handing back
    // something nothing knows how to open.
    if (row && row.course_slug && courses.course(row.course_slug)) {
      slugs.add(row.course_slug);
    }
  }

  return { slugs: [...slugs], legacyOnly: false };
}

/**
 * Does this user hold this course?
 *
 * Takes the slug list rather than querying again, so a caller that already
 * fetched it does not pay for a second round trip.
 */
function holds(slugs, slug) {
  return Array.isArray(slugs) && slugs.includes(slug);
}

module.exports = { coursesForUser, holds, tableIsMissing };
