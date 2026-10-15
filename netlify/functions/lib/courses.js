/**
 * The course registry: one place that knows what courses exist.
 *
 * Everything that used to be implicit in "the course" being singular now reads
 * from here — which Stripe prices grant what, which lesson ids belong to which
 * course, how many lessons each has, and where its files live.
 *
 * WHY THIS EXISTS
 *
 * Before a second course, access was one boolean on the user row and the
 * webhook matched one price id from STRIPE_COURSE_PRICE_ID. Two problems
 * followed from that, and the first is live right now:
 *
 *   1. ONE price id cannot cover a course with two prices. The Catering Profit
 *      System sells at $197 evergreen and $147 to the first ten founding
 *      members, which are separate Stripe payment links and so separate Price
 *      objects. Whichever one STRIPE_COURSE_PRICE_ID does not name is a
 *      customer who pays and is told the payment "is not for the course".
 *      COURSE-SYSTEM-SETUP.md says it plainly: "If it is wrong, customers are
 *      charged and receive nothing."
 *
 *   2. ONE boolean cannot say WHICH course. A second product on the same
 *      webhook would grant the first course to whoever bought the second, and
 *      email them about a course they did not buy.
 *
 * So prices are a LIST per course, and access is per course.
 *
 * It is placed in lib/ rather than beside the functions because Netlify treats
 * every top-level .js in netlify/functions as a function entrypoint. A file in
 * a subdirectory that does not match the directory name is not deployed as a
 * function, but esbuild still inlines it into every function that requires it.
 */

'use strict';

/**
 * Lesson ids are deliberately NOT migrated for the existing course.
 *
 * The Catering Profit System's rows are already in lesson_progress as bare
 * `m1l1`..`m5l4` and `bonus`. Renaming them to a prefixed form would mean an
 * UPDATE across every paying student's progress to gain nothing a prefix on
 * the NEW course does not already give. So catering-profit keeps the bare ids
 * and every later course carries a prefix. Nothing has to be rewritten, and
 * the two courses cannot collide.
 */
const COURSES = {
  'catering-profit': {
    slug: 'catering-profit',
    name: 'The Catering Profit System',
    salesPage: '/catering-profit.html',
    basePath: '/course/',
    // Downloads sit directly under course/downloads/module-N/.
    downloadPrefix: '',
    lessonPrefix: '',
    modules: 5,
    lessonsPerModule: 4,
    hasBonus: true,
    priceEnv: 'STRIPE_PRICE_IDS_CATERING_PROFIT',
    /* The single-course boolean on users. Only this course honours it, and
       only as a fallback, so buyers keep working between this deploying and
       tools/sql/course_access.sql being run. See hasLegacyFlag below. */
    legacyFlag: true,
  },
  'catering-people': {
    slug: 'catering-people',
    name: 'The Catering People Course',
    salesPage: '/catering-people.html',
    basePath: '/course/people/',
    downloadPrefix: 'people/',
    lessonPrefix: 'pp-',
    modules: 5,
    lessonsPerModule: 4,
    hasBonus: true,
    priceEnv: 'STRIPE_PRICE_IDS_CATERING_PEOPLE',
    legacyFlag: false,
  },
};

const SLUGS = Object.keys(COURSES);

/** The course record, or null for an unknown slug. */
function course(slug) {
  return Object.prototype.hasOwnProperty.call(COURSES, slug) ? COURSES[slug] : null;
}

/**
 * The Stripe price ids that grant a course, read at call time rather than at
 * module load so a Netlify environment-variable change takes effect without a
 * redeploy.
 *
 * Comma-separated, because a course can have several prices at once: an
 * evergreen price and a founding price, or an old price still honoured for
 * people who bought at it. Blank entries are dropped so a trailing comma or a
 * stray space cannot silently become an empty price id that matches nothing.
 */
function priceIdsFor(slug) {
  const record = course(slug);
  if (!record) return [];

  const ids = split(process.env[record.priceEnv]);

  /**
   * Honour the superseded STRIPE_COURSE_PRICE_ID for the original course.
   *
   * Without this, deploying before the new variables are set would stop the
   * gate matching anything, and the fallback in stripe-webhook.js would then
   * treat EVERY completed checkout as a course purchase -- including the $350
   * Snapshot, which today is correctly excluded by that one price id. A
   * deploy must not widen who gets a free course because an environment
   * variable has not been renamed yet.
   *
   * It is additive rather than an either/or, so setting the new variable while
   * the old one is still present cannot drop a price that was working.
   */
  if (record.legacyFlag) {
    for (const id of split(process.env.STRIPE_COURSE_PRICE_ID)) {
      if (!ids.includes(id)) ids.push(id);
    }
  }

  return ids;
}

/** Comma-separated env value to a clean list. Blanks dropped, so a trailing
    comma or a stray space never becomes an empty id that matches nothing. */
function split(value) {
  return String(value || '')
    .split(',')
    .map((id) => id.trim())
    .filter(Boolean);
}

/** Every configured price id, across all courses. */
function allPriceIds() {
  return SLUGS.flatMap(priceIdsFor);
}

/**
 * Which course a checkout's line items bought, or null for a payment that is
 * not a course at all — the $350 Snapshot finishes on Stripe's own page and
 * must not grant anything.
 *
 * Returns the FIRST course matched. A session containing prices from two
 * courses would need a bundle, which does not exist yet; matchedCourses below
 * is what a caller uses to notice that case rather than silently half-grant.
 */
function courseForLineItems(lineItems) {
  const matches = matchedCourses(lineItems);
  return matches.length ? matches[0] : null;
}

/** Every course the line items touch, de-duplicated and in registry order. */
function matchedCourses(lineItems) {
  const ids = new Set(
    (lineItems || []).map((item) => item && item.price && item.price.id).filter(Boolean),
  );
  return SLUGS.filter((slug) => priceIdsFor(slug).some((id) => ids.has(id)));
}

/** The lesson ids a course accepts: m1l1..mNlM, plus bonus, with its prefix. */
function lessonIds(slug) {
  const record = course(slug);
  if (!record) return new Set();
  const ids = [];
  for (let m = 1; m <= record.modules; m += 1) {
    for (let l = 1; l <= record.lessonsPerModule; l += 1) {
      ids.push(`${record.lessonPrefix}m${m}l${l}`);
    }
  }
  if (record.hasBonus) ids.push(`${record.lessonPrefix}bonus`);
  return new Set(ids);
}

/** How many lessons a course has in total, bonus included. */
function totalLessons(slug) {
  const record = course(slug);
  if (!record) return 0;
  return record.modules * record.lessonsPerModule + (record.hasBonus ? 1 : 0);
}

/**
 * Which course owns a lesson id.
 *
 * Longest prefix first, so a prefixed id is never mistaken for one belonging
 * to catering-profit, whose prefix is the empty string and therefore matches
 * everything. Without that ordering every `pp-` id would resolve to the wrong
 * course.
 */
function courseForLessonId(lessonId) {
  const id = String(lessonId || '');
  const byPrefixLength = SLUGS.slice().sort(
    (a, b) => COURSES[b].lessonPrefix.length - COURSES[a].lessonPrefix.length,
  );
  for (const slug of byPrefixLength) {
    if (id.startsWith(COURSES[slug].lessonPrefix) && lessonIds(slug).has(id)) return slug;
  }
  return null;
}

/**
 * Which course owns a path under course/downloads/.
 *
 * Same longest-prefix rule and for the same reason: catering-profit's prefix
 * is empty, so it would otherwise claim people/module-1/whatever.xlsx.
 */
function courseForDownloadPath(relativePath) {
  const p = String(relativePath || '').replace(/^\/+/, '');
  const byPrefixLength = SLUGS.slice().sort(
    (a, b) => COURSES[b].downloadPrefix.length - COURSES[a].downloadPrefix.length,
  );
  for (const slug of byPrefixLength) {
    const prefix = COURSES[slug].downloadPrefix;
    if (prefix && p.startsWith(prefix)) return slug;
  }
  // No prefix matched: it belongs to whichever course has the empty prefix.
  const fallback = SLUGS.find((slug) => COURSES[slug].downloadPrefix === '');
  return fallback || null;
}

/** Does this course still honour users.has_course_access as a fallback? */
function hasLegacyFlag(slug) {
  const record = course(slug);
  return Boolean(record && record.legacyFlag);
}

module.exports = {
  COURSES,
  SLUGS,
  course,
  priceIdsFor,
  allPriceIds,
  courseForLineItems,
  matchedCourses,
  lessonIds,
  totalLessons,
  courseForLessonId,
  courseForDownloadPath,
  hasLegacyFlag,
};
