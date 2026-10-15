/**
 * Tests for the course registry (netlify/functions/lib/courses.js).
 *
 * The registry decides who gets access to what and whose progress is whose,
 * so its edge cases are worth pinning down. Two in particular would fail
 * silently and expensively:
 *
 *   - catering-profit's lesson prefix is the EMPTY STRING, because its rows
 *     predate there being a second course. Any prefix match that does not try
 *     the longest prefix first therefore resolves every `pp-` id to the wrong
 *     course, mixing one student's two courses together. Same for download
 *     paths.
 *   - A course with two live prices needs BOTH honoured. The Catering Profit
 *     System sells at $197 and $147; if only one is configured, the other's
 *     buyers pay and get nothing.
 *
 * No test framework: node tools/check_courses.js, exits non-zero on failure.
 * That keeps package.json at the three runtime dependencies the Netlify
 * Functions need.
 */

'use strict';

process.env.STRIPE_PRICE_IDS_CATERING_PROFIT = 'price_197, price_147 ,';
process.env.STRIPE_PRICE_IDS_CATERING_PEOPLE = 'price_people';

const c = require('../netlify/functions/lib/courses.js');

const failures = [];
let ran = 0;

function is(got, want, label) {
  ran += 1;
  if (JSON.stringify(got) !== JSON.stringify(want)) {
    failures.push(`${label}\n      expected ${JSON.stringify(want)}\n      got      ${JSON.stringify(got)}`);
  }
}

/* --- prices ------------------------------------------------------------- */

is(c.priceIdsFor('catering-profit'), ['price_197', 'price_147'],
  'a trailing comma and stray spaces do not become empty price ids');
is(c.courseForLineItems([{ price: { id: 'price_197' } }]), 'catering-profit',
  'the evergreen price grants the profit course');
is(c.courseForLineItems([{ price: { id: 'price_147' } }]), 'catering-profit',
  'the founding price grants the profit course — the bug this registry exists for');
is(c.courseForLineItems([{ price: { id: 'price_people' } }]), 'catering-people',
  'the people price grants the people course');
is(c.courseForLineItems([{ price: { id: 'price_snapshot' } }]), null,
  'the $350 Snapshot grants no course');
is(c.courseForLineItems([]), null, 'no line items grant no course');
is(c.courseForLineItems(null), null, 'missing line items grant no course');
is(c.courseForLineItems([{}, { price: null }]), null,
  'line items without a price grant no course');
is(c.matchedCourses([{ price: { id: 'price_197' } }, { price: { id: 'price_people' } }]),
  ['catering-profit', 'catering-people'],
  'a session touching both courses reports both, so a caller can refuse to half-grant');

/* The superseded STRIPE_COURSE_PRICE_ID keeps working for the original
   course. This is what makes the deploy safe in every configuration: without
   it, deploying before the new variables are set would match no price at all,
   and stripe-webhook.js would then fall back to treating every completed
   checkout as a course purchase -- handing the course to $350 Snapshot
   buyers, who that one price id currently excludes correctly. */
process.env.STRIPE_COURSE_PRICE_ID = 'price_legacy';
is(c.priceIdsFor('catering-profit'), ['price_197', 'price_147', 'price_legacy'],
  'the superseded variable is added to the profit course, not substituted for it');
is(c.courseForLineItems([{ price: { id: 'price_legacy' } }]), 'catering-profit',
  'a checkout at the superseded price still grants the profit course');
is(c.priceIdsFor('catering-people'), ['price_people'],
  'the superseded variable never grants a later course');

delete process.env.STRIPE_PRICE_IDS_CATERING_PROFIT;
is(c.priceIdsFor('catering-profit'), ['price_legacy'],
  'with only the superseded variable set, it alone gates the profit course — exactly as before this change');
is(c.courseForLineItems([{ price: { id: 'price_snapshot' } }]), null,
  'and the $350 Snapshot is still excluded, which is the regression this guards');
process.env.STRIPE_PRICE_IDS_CATERING_PROFIT = 'price_197, price_147 ,';
delete process.env.STRIPE_COURSE_PRICE_ID;
is(c.priceIdsFor('catering-profit'), ['price_197', 'price_147'],
  'and it drops back out once unset');

/* --- lesson ids --------------------------------------------------------- */

is(c.totalLessons('catering-profit'), 21, 'profit: 5 modules x 4 lessons + bonus');
is(c.totalLessons('catering-people'), 21, 'people: same shape');
is(c.courseForLessonId('m1l1'), 'catering-profit', 'a bare id belongs to the profit course');
is(c.courseForLessonId('m5l4'), 'catering-profit', 'the last bare lesson');
is(c.courseForLessonId('bonus'), 'catering-profit', 'the bare bonus');
is(c.courseForLessonId('pp-m1l1'), 'catering-people',
  'a prefixed id belongs to the people course, NOT to the empty-prefix course');
is(c.courseForLessonId('pp-m5l4'), 'catering-people', 'the last prefixed lesson');
is(c.courseForLessonId('pp-bonus'), 'catering-people', 'the prefixed bonus');
is(c.courseForLessonId('m9l9'), null, 'an out-of-range lesson is rejected');
is(c.courseForLessonId('pp-m9l9'), null, 'an out-of-range prefixed lesson is rejected');
is(c.courseForLessonId('m0l0'), null, 'a zero-indexed lesson is rejected');
is(c.courseForLessonId(''), null, 'an empty lesson id is rejected');
is(c.courseForLessonId(null), null, 'a null lesson id is rejected');
is(c.courseForLessonId("'; drop table lesson_progress--"), null,
  'free text is rejected rather than stored');
is(c.lessonIds('catering-profit').has('pp-m1l1'), false,
  'the profit course does not accept the people course ids');
is(c.lessonIds('catering-people').has('m1l1'), false,
  'the people course does not accept bare ids');
is(c.lessonIds('catering-profit').size, 21, 'profit allowlist size');
is(c.lessonIds('nope').size, 0, 'an unknown slug has no lessons');

/* --- downloads ---------------------------------------------------------- */

is(c.courseForDownloadPath('module-1/Full_Cost_Pricing_Calculator.xlsx'), 'catering-profit',
  'an unprefixed download belongs to the profit course');
is(c.courseForDownloadPath('bonus/roadmap.pdf'), 'catering-profit',
  'the bonus downloads belong to the profit course');
is(c.courseForDownloadPath('people/module-1/rota.xlsx'), 'catering-people',
  'a people/ download belongs to the people course, not to the empty-prefix course');
is(c.courseForDownloadPath('/people/module-1/rota.xlsx'), 'catering-people',
  'a leading slash does not change ownership');

/* --- misc --------------------------------------------------------------- */

is(c.hasLegacyFlag('catering-profit'), true,
  'the profit course still honours users.has_course_access as a fallback');
is(c.hasLegacyFlag('catering-people'), false,
  'the people course never honours the single-course boolean');
is(c.hasLegacyFlag('nope'), false, 'an unknown slug has no legacy flag');
is(c.course('nope'), null, 'an unknown slug has no record');
is(c.priceIdsFor('nope'), [], 'an unknown slug has no prices');
is(c.SLUGS.includes('catering-profit') && c.SLUGS.includes('catering-people'), true,
  'both courses are registered');

/* Every course needs a distinct lesson prefix and download prefix, or two
   courses silently claim each other's rows and files. */
const lessonPrefixes = c.SLUGS.map((s) => c.COURSES[s].lessonPrefix);
is(new Set(lessonPrefixes).size, lessonPrefixes.length, 'lesson prefixes are unique');
const downloadPrefixes = c.SLUGS.map((s) => c.COURSES[s].downloadPrefix);
is(new Set(downloadPrefixes).size, downloadPrefixes.length, 'download prefixes are unique');
is(c.SLUGS.filter((s) => c.COURSES[s].downloadPrefix === '').length, 1,
  'exactly one course may own the unprefixed download namespace');
is(c.SLUGS.filter((s) => c.COURSES[s].legacyFlag).length, 1,
  'exactly one course may honour the single-course boolean');

/* Price-id collisions across courses would grant the wrong course. */
const all = c.allPriceIds();
is(new Set(all).size, all.length, 'no price id is configured for two courses');

/* --- access reads (lib/access.js) --------------------------------------- */

const access = require('../netlify/functions/lib/access.js');

/* Mistaking "the table is not there yet" for a real error 500s every login on
   the site, because tools/sql/course_access.sql is run by hand and nothing
   forces that to happen before a deploy. */
is(access.tableIsMissing({ code: '42P01' }), true,
  'SQLSTATE 42P01 is a missing table');
is(access.tableIsMissing({ message: 'relation "public.course_access" does not exist' }), true,
  'the worded form is a missing table');
is(access.tableIsMissing({ message: "Could not find the table 'public.course_access' in the schema cache" }), true,
  "PostgREST's schema-cache wording is a missing table");
is(access.tableIsMissing({ code: 'PGRST301', message: 'JWT expired' }), false,
  'a real error is NOT a missing table');
is(access.tableIsMissing(null), false, 'no error is not a missing table');

is(access.holds(['catering-profit'], 'catering-profit'), true, 'holds: yes');
is(access.holds(['catering-profit'], 'catering-people'), false, 'holds: no');
is(access.holds(null, 'catering-profit'), false, 'holds: no list');
is(access.holds(undefined, 'catering-profit'), false, 'holds: undefined list');

/* A Supabase client stub: .from().select().eq() resolves to one canned reply. */
const stub = (reply) => ({ from: () => ({ select: () => ({ eq: async () => reply }) }) });

async function accessTests() {
  let r = await access.coursesForUser(stub({ data: [{ course_slug: 'catering-people' }], error: null }), 'u', false);
  is(r.slugs, ['catering-people'], 'the table alone grants the people course');

  r = await access.coursesForUser(stub({ data: [], error: null }), 'u', true);
  is(r.slugs, ['catering-profit'],
    'the legacy boolean alone still grants the profit course, so nobody is locked out before the migration runs');

  r = await access.coursesForUser(stub({ data: [{ course_slug: 'catering-people' }], error: null }), 'u', true);
  is(r.slugs.slice().sort(), ['catering-people', 'catering-profit'], 'both sources union');

  r = await access.coursesForUser(stub({ data: [{ course_slug: 'catering-profit' }], error: null }), 'u', true);
  is(r.slugs, ['catering-profit'], 'no duplicate when both sources agree');

  r = await access.coursesForUser(stub({ data: [{ course_slug: 'ghost-course' }], error: null }), 'u', false);
  is(r.slugs, [], 'a slug not in the registry is ignored');

  r = await access.coursesForUser(stub({ data: null, error: { code: '42P01' } }), 'u', true);
  is([r.slugs, r.legacyOnly], [['catering-profit'], true],
    'a missing table falls back to the boolean instead of throwing');

  let threw = false;
  try {
    await access.coursesForUser(stub({ data: null, error: { code: '08006', message: 'connection failure' } }), 'u', true);
  } catch (e) {
    threw = true;
  }
  is(threw, true,
    'a real query failure throws, so the caller answers 500 rather than telling a buyer they have nothing');
}

/* --- report ------------------------------------------------------------- */

function report() {
  if (failures.length) {
    console.error(`\nFAILED — ${failures.length} of ${ran} course-system assertion(s):\n`);
    failures.forEach((f) => console.error(`  ${f}\n`));
    process.exit(1);
  }
  console.log(`PASSED — ${ran} course-system assertion(s).`);
}

accessTests().then(report).catch((err) => {
  console.error('course-system tests crashed:', err);
  process.exit(1);
});
