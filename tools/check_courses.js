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
process.env.STRIPE_PRICE_IDS_CATERING_BUNDLE = 'price_bundle';

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

is(c.priceIdsFor('catering-profit').filter((id) => !id.startsWith('price_1UPg')),
  ['price_197', 'price_147'],
  'a trailing comma and stray spaces do not become empty price ids');
const buy = (...ids) => c.purchaseFromLineItems(ids.map((id) => ({ price: { id } })));

is(buy('price_197').slugs, ['catering-profit'],
  'the evergreen price grants the profit course');
is(buy('price_147').slugs, ['catering-profit'],
  'the founding price grants the profit course — the bug this registry exists for');
is(buy('price_people').slugs, ['catering-people'],
  'the people price grants the people course');
is(buy('price_snapshot').slugs, [],
  'the $350 Snapshot grants no course');
is(c.purchaseFromLineItems([]).slugs, [], 'no line items grant no course');
is(c.purchaseFromLineItems(null).slugs, [], 'missing line items grant no course');
is(c.purchaseFromLineItems([{}, { price: null }]).slugs, [],
  'line items without a price grant no course');

/* --- the REAL live price ids -------------------------------------------- */

/* These are the actual prices behind the two payment links on the live site.
   Asserted literally, because the whole point of putting them in the registry
   is that the webhook works without anyone setting an environment variable —
   and because the failure they prevent is silent: a buyer is charged and
   granted nothing, and the first anyone hears of it is an email asking where
   the course went. A typo in one of these ids would reproduce exactly that. */
is(buy('price_1UPgfR3ZIXWMSTgNHf1HlfFv').slugs, ['catering-profit'],
  'the real $197 standard price grants the profit course');
is(buy('price_1UPgeJ3ZIXWMSTgNLDiulogW').slugs, ['catering-profit'],
  'the real $147 founding price grants the profit course');
is(buy('price_1UPgfR3ZIXWMSTgNHf1HlfFv', 'price_1UPgeJ3ZIXWMSTgNLDiulogW').slugs,
  ['catering-profit'],
  'both real prices in one session still grant the course exactly once');

/* The environment variable may only ADD. Dropping a working price by setting
   it would put us straight back in the bug this replaced. */
process.env.STRIPE_PRICE_IDS_CATERING_PROFIT = 'price_added_later';
is(c.priceIdsFor('catering-profit').includes('price_1UPgfR3ZIXWMSTgNHf1HlfFv'), true,
  'setting the variable does not drop the registered $197 price');
is(c.priceIdsFor('catering-profit').includes('price_added_later'), true,
  'and the variable still adds its own');
process.env.STRIPE_PRICE_IDS_CATERING_PROFIT = 'price_197, price_147 ,';

/* --- the bundle, in both shapes Stripe can take ------------------------- */

/* Shape 1: one Price for a single "both courses" product. */
is(buy('price_bundle').slugs, ['catering-profit', 'catering-people'],
  'one bundle price grants both courses');
is(buy('price_bundle').name, 'The Complete Catering System: Profit + People',
  'a bundle is named as the bundle, because that is what the customer chose');
is(buy('price_bundle').bundles, ['catering-complete'], 'the bundle is reported');

/* Shape 2: a payment link holding one line item per course. Granting the
   first and dropping the rest would take the money and deliver half. */
is(buy('price_197', 'price_people').slugs, ['catering-profit', 'catering-people'],
  'two course line items in one session grant both, rather than being refused');
is(buy('price_197', 'price_people').name,
  'The Catering Profit System and The Catering People System',
  'two separately-bought courses are both named, not described as one bundle');

/* Overlap must not double-grant or reorder. */
is(buy('price_bundle', 'price_197').slugs, ['catering-profit', 'catering-people'],
  'a bundle plus one of its own courses grants each course once');
is(buy('price_people', 'price_197').slugs, ['catering-profit', 'catering-people'],
  'grants come back in registry order regardless of line-item order');
is(buy('price_bundle', 'price_snapshot').slugs, ['catering-profit', 'catering-people'],
  'a Snapshot alongside a bundle neither adds nor removes a course');
is(c.allPriceIds().includes('price_bundle'), true,
  'bundle prices are in allPriceIds, or the gate would ignore a bundle purchase entirely');

/* The superseded STRIPE_COURSE_PRICE_ID keeps working for the original
   course. This is what makes the deploy safe in every configuration: without
   it, deploying before the new variables are set would match no price at all,
   and stripe-webhook.js would then fall back to treating every completed
   checkout as a course purchase -- handing the course to $350 Snapshot
   buyers, who that one price id currently excludes correctly. */
process.env.STRIPE_COURSE_PRICE_ID = 'price_legacy';
is(c.priceIdsFor('catering-profit').filter((id) => !id.startsWith('price_1UPg')),
  ['price_197', 'price_147', 'price_legacy'],
  'the superseded variable is added to the profit course, not substituted for it');
is(buy('price_legacy').slugs, ['catering-profit'],
  'a checkout at the superseded price still grants the profit course');
is(c.priceIdsFor('catering-people'), ['price_people'],
  'the superseded variable never grants a later course');

delete process.env.STRIPE_PRICE_IDS_CATERING_PROFIT;
is(c.priceIdsFor('catering-profit').filter((id) => !id.startsWith('price_1UPg')),
  ['price_legacy'],
  'with only the superseded variable set, it still gates the profit course alongside the registered ones');
is(buy('price_snapshot').slugs, [],
  'and the $350 Snapshot is still excluded, which is the regression this guards');
process.env.STRIPE_PRICE_IDS_CATERING_PROFIT = 'price_197, price_147 ,';
delete process.env.STRIPE_COURSE_PRICE_ID;
is(c.priceIdsFor('catering-profit').filter((id) => !id.startsWith('price_1UPg')),
  ['price_197', 'price_147'],
  'and it drops back out once unset');
/* The registered ids are never affected by any of that: they are the floor. */
is(c.priceIdsFor('catering-profit').filter((id) => id.startsWith('price_1UPg')).length, 2,
  'the two registered live prices survive every environment permutation above');

/* --- matching by PRODUCT as well as price -------------------------------- */

/* A line item carries both: the price (one exact amount) and the product it
   belongs to. Matching the product means a registered product grants its
   course however it is priced, so raising a price needs no code change. */
const byProduct = (productId) =>
  c.purchaseFromLineItems([{ price: { id: 'price_irrelevant', product: productId } }]);

is(byProduct('prod_VS4zUUhRNMs2eR').slugs, ['catering-profit', 'catering-people'],
  'the real STANDARD bundle product ($297) grants both courses');
is(byProduct('prod_VS4cctwqCDniwT').slugs, ['catering-profit', 'catering-people'],
  'the real FOUNDERS bundle product ($247) grants both courses');
is(c.bundlesRequiringExisting(byProduct('prod_VS4zUUhRNMs2eR').bundles), [],
  'the standard bundle is bought outright, so it is not gated on owning anything');

/* Every registered Stripe identifier, across every course and bundle, must be
   distinct. The same product under two of them would grant the wrong thing,
   and the symptom is silent: someone is simply let into more than they paid
   for. */
const registered = [
  ...c.SLUGS.flatMap((slug) => [
    ...(c.COURSES[slug].priceIds || []), ...(c.COURSES[slug].productIds || []),
  ]),
  ...c.BUNDLE_SLUGS.flatMap((slug) => [
    ...(c.BUNDLES[slug].priceIds || []), ...(c.BUNDLES[slug].productIds || []),
  ]),
];
is(new Set(registered).size, registered.length,
  'no Stripe price or product id is registered against two different things');
is(registered.every((id) => /^(price|prod)_[A-Za-z0-9]+$/.test(id)), true,
  'every registered id is a price or product id — never a payment link, which would never match');
is(byProduct('prod_VS4cctwqCDniwT').name, 'The Complete Catering System: Profit + People',
  'and is named as the bundle');
is(byProduct('prod_VS4cGwqq2RvVBA').slugs, ['catering-profit', 'catering-people'],
  'the real upgrade product grants both courses');
is(c.bundlesRequiringExisting(byProduct('prod_VS4cGwqq2RvVBA').bundles), ['catering-upgrade'],
  'and the real upgrade product is still gated on already owning a course');
is(byProduct('prod_somethingelse').slugs, [],
  'an unregistered product grants nothing');

/* Stripe sends price.product as an id string, or as the expanded object when
   asked. Reading only one shape would silently stop matching. */
is(c.purchaseFromLineItems([{ price: { id: 'px', product: { id: 'prod_VS4cctwqCDniwT' } } }]).slugs,
  ['catering-profit', 'catering-people'],
  'an EXPANDED product object matches too, not just the id string');
is(c.purchaseFromLineItems([{ price: { id: 'px', product: null } }]).slugs, [],
  'a null product is not a match');

/* Price matching must still work: the two course prices are registered that
   way, and losing it would lock out every buyer at $197 or $147. */
is(buy('price_1UPgfR3ZIXWMSTgNHf1HlfFv').slugs, ['catering-profit'],
  'price matching still works alongside product matching');

/* --- the bundle and the upgrade ---------------------------------------- */

process.env.STRIPE_PRICE_IDS_CATERING_UPGRADE = 'price_upgrade';
is(buy('price_upgrade').slugs, ['catering-profit', 'catering-people'],
  'the upgrade grants BOTH courses, because one price cannot know which one the buyer lacks');
is(buy('price_upgrade').bundles, ['catering-upgrade'], 'the upgrade is reported as its own product');
is(c.bundlesRequiringExisting(buy('price_upgrade').bundles), ['catering-upgrade'],
  'the upgrade is gated on already holding a course — without this it is a $100 link worth $297');
is(c.bundlesRequiringExisting(buy('price_bundle').bundles), [],
  'the full bundle is NOT gated: it is the whole price, bought outright');
is(c.bundlesRequiringExisting([]), [], 'no bundles, nothing gated');
is(c.bundlesRequiringExisting(null), [], 'null is safe');

/* The money has to add up, or the upgrade is either a discount nobody
   intended or a worse deal than buying the second course outright. */
const profit = c.course('catering-profit');
const complete = c.bundle('catering-complete');
const upgrade = c.bundle('catering-upgrade');
is(complete.usd - profit.usd, upgrade.usd,
  'the upgrade is exactly the difference between one standard course and the bundle');
is(complete.foundingUsd - profit.foundingUsd, upgrade.usd,
  'and exactly the difference at the founding prices too, so it is one figure either way');

/* Every bundle price must be gated or not on purpose, never by omission. */
for (const b of c.BUNDLE_SLUGS) {
  is(typeof c.BUNDLES[b].requiresExisting, 'boolean',
    `bundle ${b} states explicitly whether it requires an existing course`);
}
delete process.env.STRIPE_PRICE_IDS_CATERING_UPGRADE;

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

/* Price-id collisions would grant the wrong thing. A bundle price appearing
   under a course as well would be harmless (the union is the same), but the
   same id under two COURSES is a real misconfiguration. */
const all = c.allPriceIds();
is(new Set(all).size, all.length, 'no price id is configured twice');

/* Every course a bundle claims to grant must actually exist, or a buyer is
   given access to something nothing knows how to open. */
for (const b of c.BUNDLE_SLUGS) {
  for (const granted of c.BUNDLES[b].grants) {
    is(Boolean(c.course(granted)), true, `bundle ${b} grants a registered course: ${granted}`);
  }
  is(c.BUNDLES[b].grants.length >= 2, true, `bundle ${b} grants more than one course`);
  is(new Set(c.BUNDLES[b].grants).size, c.BUNDLES[b].grants.length,
    `bundle ${b} does not list a course twice`);
}

/* --- access reads (lib/access.js) --------------------------------------- */

const access = require('../netlify/functions/lib/access.js');

/* Mistaking "the table is not there yet" for a real error 500s every login on
   the site, because tools/sql/course_access.sql is run by hand and nothing
   forces that to happen before a deploy. */
is(access.tableIsMissing({ code: '42P01' }), true,
  'SQLSTATE 42P01 is a missing table');
is(access.tableIsMissing({ code: 'PGRST205' }), true,
  "PGRST205 is a missing table — what the live project actually returns, checked against it");
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
