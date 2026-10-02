# Claims register

Every quantitative or credential claim currently published on trecoleman.com,
with where it appears and what would substantiate it.

**Why this file exists.** Under FTC advertising-substantiation rules, a
performance claim needs evidence you can produce on request. Beyond the legal
point, your buyers have been pitched by other consultants — an unsupported
number is a credibility liability, and a documented one is a genuine
differentiator.

These numbers are specific and plausible. They read like real operator results
rather than marketing invention, which is exactly why they are worth
documenting properly rather than removing.

**How to use this.** Fill in the Evidence column. Where you have documentation,
note where it lives. Where you do not, pick an action: soften the wording to
something you can stand behind, or remove it.

Status key — `documented` · `needs softening` · `remove` · `unreviewed`

---

## Credentials and experience

| # | Claim | Where | Evidence | Status |
|---|---|---|---|---|
| 1 | "10+ years managing multi-unit restaurant operations" | `about.html`, `index.html`, `blog.html` | Resume: summary claims "over a decade"; Potbelly District Manager Oct 2020–Nov 2024 across multiple store locations | documented (2026-10-02, verified from resume screenshots) |
| 2 | "300+ employees led across multiple locations" | `about.html`, `index.html` | No headcount on resume | softened (2026-10-02) — now "District Manager leading multiple store locations" / tile "Multi-Unit District Manager" |
| 3 | "$300K+ in revenue waste eliminated for clients" | `about.html` | Resume: "combined $300k revenue across multiple store locations" (Potbelly DM) | reworded (2026-10-02) — now "$300K+ in revenue across multiple store locations"; the "waste eliminated for clients" framing had no backing |
| 4 | "National Hospitality Brands" | `index.html` | Resume: Potbelly (District Manager); Hooters confirmed by Tre' | softened (2026-10-02) — now "Potbelly · Hooters" |

> On #4 — naming the brands (with permission) is far stronger than the vague
> phrase. Specificity is the whole credibility mechanism here.

## Service outcome claims

| # | Claim | Where | Evidence | Status |
|---|---|---|---|---|
| 5 | "Cut admin time 40-60%" | `ai-integration.html` meta + body | | softened (2026-10-02) |
| 6 | "New hires productive 40% faster with AI" | `ai-integration.html` | | softened (2026-10-02) |
| 7 | "3-5 hours per week saved per manager" | `ai-integration.html` | | softened (2026-10-02) |
| 8 | "50% faster onboarding — 2-3 weeks instead of 4-6" | `sops-training.html` | | softened (2026-10-02) |
| 9 | "12-18% increase in average check size within 90 days" | `menu-engineering.html` | | softened (2026-10-02) |
| 10 | "15-25% increase in traffic during slow periods" | `lsm.html` | | softened (2026-10-02) |

## ROI claims

> ROI claims attract the most scrutiny of anything on this list, because they
> are the easiest to state and the hardest to evidence.

| # | Claim | Where | Evidence | Status |
|---|---|---|---|---|
| 11 | "Typical ROI: 8-12x return within the first quarter" | `menu-engineering.html` | | softened (2026-10-02) |
| 12 | "Typical ROI: 4-6x return within the first 90 days" | `sops-training.html` | | softened (2026-10-02) |

## Diagnostic claims

| # | Claim | Where | Evidence | Status |
|---|---|---|---|---|
| 13 | "Most operators find $5,000–$20,000 in annual leaks in a single session" | `index.html` FAQ **and FAQPage schema** | | softened (2026-10-02) |
| 14 | "Losing $10K–$50K a year to profit leaks" | `index.html` hero, `virginia-neighbors.html` | | softened (2026-10-02) |

> #13 is inside your `FAQPage` structured data, so it is eligible to appear as
> a rich result. A claim Google may surface directly deserves the firmest
> evidence on this page, or the softest wording.
>
> #14 could be reframed as an industry estimate with a cited source rather
> than an implied finding of your own, which would make it defensible without
> losing the hook.

## Case studies

Currently presented on `index.html` under "Results from the Field", labelled
"Real operators, real numbers. Details anonymized."

| # | Claim | Evidence | Status |
|---|---|---|---|
| 15 | Fast-casual: "Overtime dropped 22%. ~$18,000 in annual labor savings" | | unreviewed |
| 16 | Catering: "Average event margin up 11 points" | | unreviewed |
| 17 | Food truck: "Onboarding cut from 3 weeks to 8 days" | | unreviewed |

> These are your strongest assets on the whole site — specific, operational,
> and the kind of thing a prospect recognises as real. Worth documenting
> properly: which client, what the before/after numbers were, and written
> permission for anonymised use.

## Service description claims

| # | Claim | Where | Evidence | Status |
|---|---|---|---|---|
| 18 | "Unlimited support" / "Unlimited Slack/Text Access" | `advisory.html` meta, `blog/fractional-coo-for-restaurants.html` | | softened (2026-10-02) |

> "Unlimited" is an absolute claim on a $2,000/month service. Either define the
> boundaries in the service description or soften to something like "on-call
> between sessions" — which is what it presumably means in practice.

## Pricing and availability

| # | Claim | Where | Evidence | Status |
|---|---|---|---|---|
| 19 | "Pre-order now for $67" | `catering-profit.html` | Is this still a pre-order? Is $67 current? | documented / keep (2026-10-02) |
| 20 | Course launch date "May 31st, 2026" | `catering-profit.html` | Date has passed — needs updating or removing | unreviewed |

---

## When you have worked through this

Three follow-ups:

1. **Update `SEO_AUDIT.md`.** Its verification section lists these same items;
   mark them resolved there so the audit stays accurate.
2. **Re-check the schema.** Claims 13 and 14 appear in structured data as well
   as body copy. If you soften the wording, soften both — markup that no
   longer matches the visible page is a structured-data violation.
3. **Keep this file updated.** Any new performance claim added to the site
   should get a row here at the time it is written, not retroactively.
