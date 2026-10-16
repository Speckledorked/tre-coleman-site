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
    /**
     * The live prices, in code.
     *
     * A Stripe PRICE id is an identifier, not a credential — it is what
     * client-side Stripe integrations pass around, and this repository
     * already hardcodes the PAYMENT LINKS these sit behind
     * (index.html:302 and :305), which are strictly more revealing. So
     * there is nothing gained by making the webhook unable to work until
     * someone sets an environment variable, and something real lost: the
     * $147 founding tier shipped on 2026-10-12 against a gate that could
     * name only one price, so whichever price was not named took money
     * and granted nothing.
     *
     * Changing a price is already a code change here, because the payment
     * link in the markup has to change with it. The environment variable
     * still works and is UNIONED with this, so a price can be added
     * without a deploy; it cannot remove one, which is deliberate.
     */
    priceIds: [
      'price_1UPgfR3ZIXWMSTgNHf1HlfFv',   // $197 standard
      'price_1UPgeJ3ZIXWMSTgNLDiulogW',   // $147 founding, first 10 buyers
    ],
    /**
     * What it costs, for the one place that has to agree with the markup.
     *
     * Not read at runtime — the webhook only ever matches price ids, and the
     * amount it charged is Stripe's business. These are here so the arithmetic
     * between the courses, the bundle and the upgrade is checked rather than
     * assumed: tools/check_courses.js asserts the upgrade really is the
     * difference, at both the standard and the founding prices.
     */
    usd: 197,
    foundingUsd: 147,
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
    // Not created yet. Until one exists, no checkout can match this course,
    // which is the correct behaviour: it cannot be bought yet either.
    priceIds: [],
    usd: 197,
    foundingUsd: 147,
    legacyFlag: false,
  },
};

const SLUGS = Object.keys(COURSES);

/**
 * Bundles: things you can BUY that grant more than one course.
 *
 * Kept separate from COURSES because the two are different kinds of thing. A
 * course is something you can open — it has lessons, files, a path. A bundle
 * is only a way to pay for several of them at once, and has none of that.
 * Folding bundles into COURSES would mean every lesson-id and download lookup
 * having to skip entries that can never own a lesson or a file.
 *
 * A bundle works whichever shape it takes in Stripe, because the webhook
 * grants the UNION of everything a session matches:
 *
 *   - one Price for a single "both courses" product -> matches here, grants
 *     both via `grants`
 *   - a payment link holding one line item per course -> matches each course
 *     directly, and the union is the same two courses
 */
const BUNDLES = {
  'catering-complete': {
    slug: 'catering-complete',
    name: 'The Catering Profit + People Bundle',
    grants: ['catering-profit', 'catering-people'],
    priceEnv: 'STRIPE_PRICE_IDS_CATERING_BUNDLE',
    // $297 standard, $247 founding. Price ids go here once the products exist
    // in Stripe; until then no checkout can match, which is correct, because
    // until then it cannot be bought either.
    priceIds: [],
    usd: 297,
    foundingUsd: 247,
    requiresExisting: false,
  },

  /**
   * The upgrade: someone who owns one course paying the difference for the
   * other. $100, which is $297 - $197 and also $247 - $147, so it is the same
   * figure whether they bought at the standard or the founding price.
   *
   * It grants BOTH courses rather than "the other one", because a single
   * Stripe price cannot know which one the buyer is missing. Granting both is
   * correct from either direction: the course_access upsert makes the one they
   * already hold a no-op, so a Profit owner gains People and a People owner
   * gains Profit, from the same price.
   *
   * requiresExisting IS THE POINT. Without it this is a $100 link that hands
   * both courses to anyone who finds it -- a $197 hole, since the bundle is
   * $297. Stripe payment links cannot be gated on a previous purchase, and an
   * unlisted link is still a shareable URL. So the webhook checks that the
   * buyer already holds one of the two and, if they hold neither, grants
   * nothing and asks for a human: that is someone who has underpaid, and
   * whether to refund them or bill the difference is not a decision to make
   * automatically.
   */
  'catering-upgrade': {
    slug: 'catering-upgrade',
    name: 'The Catering Profit + People Bundle (upgrade)',
    grants: ['catering-profit', 'catering-people'],
    priceEnv: 'STRIPE_PRICE_IDS_CATERING_UPGRADE',
    priceIds: [],
    usd: 100,
    requiresExisting: true,
  },
};

const BUNDLE_SLUGS = Object.keys(BUNDLES);

/** The bundle record, or null. */
function bundle(slug) {
  return Object.prototype.hasOwnProperty.call(BUNDLES, slug) ? BUNDLES[slug] : null;
}

/**
 * Bundles matched by these line items that may only be bought by someone who
 * already holds one of the courses they grant. See catering-upgrade.
 */
function bundlesRequiringExisting(bundleSlugs) {
  return (bundleSlugs || []).filter((slug) => {
    const record = bundle(slug);
    return Boolean(record && record.requiresExisting);
  });
}

/** Price ids configured for a bundle. */
function bundlePriceIdsFor(slug) {
  const record = bundle(slug);
  if (!record) return [];
  const ids = [...(record.priceIds || [])];
  for (const id of split(process.env[record.priceEnv])) {
    if (!ids.includes(id)) ids.push(id);
  }
  return ids;
}

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

  // Registry defaults first, then anything the environment adds. Union, so
  // setting the variable can only ever add a price, never silently drop one
  // that is working.
  const ids = [...(record.priceIds || [])];
  for (const id of split(process.env[record.priceEnv])) {
    if (!ids.includes(id)) ids.push(id);
  }

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

/** Every configured price id, across all courses AND bundles. */
function allPriceIds() {
  return [...SLUGS.flatMap(priceIdsFor), ...BUNDLE_SLUGS.flatMap(bundlePriceIdsFor)];
}

/**
 * What a checkout's line items actually bought.
 *
 * Returns every course the session grants, as a union over direct course
 * prices AND any bundle prices, plus a name for the confirmation email.
 *
 * The union is what makes a bundle work in either shape — one bundle Price,
 * or a link holding one line item per course — and it is also why a session
 * matching two courses is no longer refused. Before a bundle existed,
 * granting the first match and dropping the rest would have taken the money
 * and delivered half, so the webhook alerted instead. Now that buying both at
 * once is a real product, granting both is simply the right answer.
 *
 * A payment that is no course at all returns an empty list: the $350 Snapshot
 * finishes on Stripe's own page and must not grant anything.
 *
 * @returns {{slugs: string[], name: string|null, bundles: string[]}}
 */
function purchaseFromLineItems(lineItems) {
  const ids = new Set(
    (lineItems || []).map((item) => item && item.price && item.price.id).filter(Boolean),
  );

  const direct = SLUGS.filter((slug) => priceIdsFor(slug).some((id) => ids.has(id)));
  const bundles = BUNDLE_SLUGS.filter((slug) => bundlePriceIdsFor(slug).some((id) => ids.has(id)));

  const slugs = new Set(direct);
  for (const b of bundles) {
    // Ignore a slug a bundle names that is not a registered course, rather
    // than granting access to something nothing knows how to open.
    for (const slug of BUNDLES[b].grants) if (course(slug)) slugs.add(slug);
  }

  // Keep registry order, so the name and the grants read consistently.
  const ordered = SLUGS.filter((slug) => slugs.has(slug));

  return { slugs: ordered, name: purchaseName(ordered, bundles), bundles };
}

/**
 * What to call this purchase in a confirmation email.
 *
 * A bundle is named as the bundle, because that is what the customer chose. A
 * single course is named as itself. Two courses bought as separate line items
 * with no bundle price are joined, rather than silently described as one.
 */
function purchaseName(slugs, bundles) {
  if (!slugs.length) return null;
  if (bundles.length === 1) return BUNDLES[bundles[0]].name;
  const names = slugs.map((slug) => COURSES[slug].name);
  if (names.length === 1) return names[0];
  return `${names.slice(0, -1).join(', ')} and ${names[names.length - 1]}`;
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
  purchaseFromLineItems,
  purchaseName,
  BUNDLES,
  BUNDLE_SLUGS,
  bundle,
  bundlePriceIdsFor,
  bundlesRequiringExisting,
  lessonIds,
  totalLessons,
  courseForLessonId,
  courseForDownloadPath,
  hasLegacyFlag,
};
