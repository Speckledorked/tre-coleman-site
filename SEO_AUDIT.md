# SEO Audit — trecoleman.com

**Audited:** 2026-08-16
**Repository:** `speckledorked/tre-coleman-site` (branch `claude/consulting-site-seo-audit-kekwtz`)
**Scope:** Full repository — 43 HTML files, `style.css`, `analytics.js`, `robots.txt`, `sitemap.xml`, `netlify.toml`, `_headers`, `.github/workflows/`
**Method:** Static code inspection only. No crawl, no rendering, no Search Console, no Analytics, no rank/traffic/backlink data was available to this audit.

> **What this audit cannot tell you.** Everything below is derived from source code. It contains **no** claims about current rankings, traffic, impressions, indexed page counts, backlinks, or Core Web Vitals field data, because none of that is in the repository. Items requiring outside verification are labelled **[VERIFY]** or **[EXTERNAL]**.

---

## 1. Executive summary

### Overall SEO score: **6 / 10**

This is a well-above-average small-business site on *intent* and *metadata discipline*, and well-below-average on *performance* and *link architecture*. Someone has clearly done deliberate SEO work here — canonical tags on every indexable page, Open Graph and Twitter cards sitewide, a genuinely good `@graph` LocalBusiness/Person schema, correct `noindex` on every auth and course page, and GA4 with custom conversion events. That foundation is real and it is worth protecting.

What holds the score down is that the site's **four highest-commercial-intent service pages are almost orphaned**, the **blog is entirely absent from the sitemap**, the **homepage ships a 2 MB LCP image**, and the **social preview image is 200×200 pixels**. These are not subtle problems; they are load-bearing ones, and they are all fixable in days rather than months.

| Dimension | Score | Note |
|---|---|---|
| Indexability & crawl control | 7/10 | Canonicals + noindex discipline good; sitemap incomplete |
| Metadata quality | 7/10 | Present everywhere, but generic titles and 6 over-length descriptions |
| Structured data | 6/10 | Excellent on 2 pages, absent on the other 24 |
| Site architecture / internal linking | 3/10 | Money pages have 1 inbound link each |
| Core Web Vitals readiness | 2/10 | ~9.6 MB of images on one page; render-blocking font `@import` |
| Content depth & topical coverage | 6/10 | Strong service copy; no local, ghost-kitchen, or bottom-funnel content |
| Local SEO readiness | 3/10 | Zero named Virginia markets; NAP inconsistency |
| Conversion / lead capture | 6/10 | Clear offer ladder; one anonymous testimonial, thin contact page |
| Analytics & measurement | 6/10 | GA4 + events present; no GSC verification, no conversion definitions |

### Top 5 issues by expected impact

1. **The four core service pages are structurally orphaned.** `ai-integration.html`, `sops-training.html`, `lsm.html`, and `menu-engineering.html` each receive exactly **one** inbound internal link — from `services.html`. They are not in the site navigation, not in the footer, and not linked from the homepage or from any blog post. These are the pages that carry your `Service` schema and target your highest-value commercial keywords, and the site is telling Google they are its least important pages. *(Evidence: link-count analysis across all HTML; nav blocks in every page contain only Snapshot/Services/Advisory/Insights▾/Resources▾/About/Contact.)*

2. **All five blog posts are missing from `sitemap.xml`.** The sitemap lists 19 URLs and omits `/blog/blog_post_1…` through `…_5…` entirely (`sitemap.xml:1-88`). Combined with two inbound links each and no `Article` schema, your entire content asset is nearly invisible. This is also the content most likely to earn links and rank for informational queries.

3. **Core Web Vitals will fail on mobile.** `index.html:319` loads `hero.png` — **2,004 KB, 1536×1024** — as the LCP element's CSS background. `services.html:262-303` loads six PNGs totalling **~9.6 MB**. No `<img>` on the site has `width`/`height` attributes (guaranteed CLS) or `loading="lazy"`. `style.css:10` uses `@import` for Google Fonts, which chains a third-party request *behind* the stylesheet and blocks render. Seven pages hot-link 1920px hero images from Unsplash's CDN, and a Crisp Chat widget — bundled unannounced inside `exit-intent-popup.js:18-25` and apparently misconfigured — loads on 17 pages.

4. **Social preview images are broken sitewide.** ~20 pages set `og:image` to `https://trecoleman.com/images/tre-headshot.jpg`, which is **200×200 px** — below the minimum for the `summary_large_image` card type those same pages declare, and far below the 1200×630 recommendation. `index.html:18` and `blog.html` use `familypic.jpg` (1440×1541, portrait) instead, which is large enough but the wrong aspect ratio. Every share to LinkedIn, Facebook, or Slack renders degraded. This is not a ranking factor but it directly suppresses the click-through and referral traffic that *do* feed rankings.

5. **Local SEO is asserted but never built.** The site says "Virginia" 40+ times, almost all of it in boilerplate footer text. It names **zero** specific markets — no Richmond, Charlottesville, Norfolk, Hampton Roads, Northern Virginia, Roanoke, or Fredericksburg appears anywhere outside `about.html:322`. The `LocalBusiness` schema declares `addressLocality: "Louisa"` (`index.html:549`) while `about.html:322` says "Home base is Lake Monticello, VA" — an internal NAP conflict that will undermine any Google Business Profile you create. **[VERIFY]**

### Top 5 quickest wins

Each of these is under an hour and carries no design risk.

1. **Add the five blog posts + `unreasonably-optimistic.html` to `sitemap.xml`**, and add `<lastmod>` to every entry. ~15 minutes. Fully automatable.
2. **Replace `@import` in `style.css:10` with a `<link rel="preconnect">` + `<link rel="stylesheet">` pair in each page's `<head>`.** Two pages (`index.html:28-30`, `virginia-neighbors.html:22`) already do this correctly — copy that pattern. Removes a render-blocking request chain on ~40 pages.
3. **Produce one 1200×630 OG image and repoint every `og:image` / `twitter:image` to it.** ~30 minutes including the image. Sitewide fix, zero risk.
4. **Add the four service pages to the main navigation** as a "Services ▾" dropdown (the dropdown pattern already exists — see `services.html` nav, "Insights" and "Resources"). Takes them from 1 inbound link to ~40.
5. **Add `width`, `height`, and `loading="lazy"` to all 11 `<img>` tags.** Dimensions are already known (listed in §2.6). Eliminates CLS on every page with an image.

### Current strengths — protect these

- **Canonical tags on 100% of indexable pages**, all self-referencing and absolute. Genuinely rare at this size.
- **Correct `noindex, nofollow` on every utility page** — all 8 `/course/*` pages, `login`, `register`, `forgot-password`, `reset-password`, `thank-you`, `profit-leak-calculator`, `client-assistant`, `email-signature`. Crawl budget is not being wasted on member content.
- **The `@graph` schema on `index.html:532-631` is strong.** Correct `@id` linking between `LocalBusiness`/`ProfessionalService` and `Person`, a real `hasOfferCatalog` with three priced offers, `knowsAbout`, and `sameAs`. Most consulting sites have nothing.
- **The `FAQPage` schema on `index.html:635-680` mirrors visible on-page FAQ content** — which is exactly the requirement Google enforces. Five substantive, genuinely useful Q&As.
- **`services.html:76-176` carries six `Service` entities** each correctly referencing `{"@id": "…/#business"}` as provider.
- **A clear, well-priced offer ladder** — $350 Snapshot → project work → $2,000/mo advisory — repeated consistently across pages. This is the hardest part of consulting-site conversion and it is already done.
- **GA4 with custom conversion events** (`analytics.js`), including `booking_click` on Stripe links, loaded on 32 pages.
- **Semantic HTML basics are sound**: exactly one `<h1>` per page on all 41 content pages, `lang="en"` everywhere, `<header>`/`<nav>`/`<footer>`/`<section>` used properly, `aria-label` on the mobile menu toggle.
- **Static HTML on a CDN.** No hydration cost, no SSR complexity, no JS framework tax. Once the images are fixed, this site can be genuinely fast.

---

## 2. Technical SEO audit

### Framework & rendering strategy

**Finding (informational):** This is a hand-authored **static HTML site** with no build step (`package.json` `"build": "echo 'No build required'"`). It deploys on **Netlify** (`netlify.toml`, `netlify/functions/` with 8 serverless functions) while also carrying a `CNAME` file containing `trecoleman.com` — a GitHub Pages artifact. Since `/.netlify/functions/*` calls are live in the code (`virginia-neighbors.html:468`, `course/auth.js:37`), Netlify is the real host and `CNAME` is a leftover.

For SEO this is close to the ideal architecture: every page is fully rendered HTML with no client-side hydration. The two exceptions are noted below.

**Severity: Low** — remove `CNAME` if GitHub Pages is retired, to avoid future deploy ambiguity. **[VERIFY]** which host is authoritative before deleting. **Safe to automate: no** (deployment-affecting).

---

### 2.1 Indexability & crawl control

| # | Finding | Severity | File / line |
|---|---|---|---|
| T1 | Blog posts absent from sitemap | **Critical** | `sitemap.xml` |
| T2 | `zohoverify/verifyforzoho.html` is indexable and empty | **High** | `zohoverify/verifyforzoho.html` |
| T3 | `404.html` has canonical + OG tags | **Medium** | `404.html:6-16` |
| T4 | No `<lastmod>` in sitemap | **Medium** | `sitemap.xml` |
| T5 | `robots.txt` has no `Disallow` for gated paths | **Low** | `robots.txt` |
| T6 | Paid course product is publicly downloadable | **High (business)** | repo root |

**T1 — Blog posts missing from sitemap. Critical.**
`sitemap.xml` contains 19 `<url>` entries. Missing: all five `/blog/blog_post_*.html` files and `unreasonably-optimistic.html`. Present but questionable: nothing.
*Why it matters:* These six pages have only 2 inbound internal links each (from `blog.html`) and no `Article` schema. The sitemap is the single strongest discovery signal available to a site with a weak internal link graph, and it is not being used for the exact pages that need it most.
*Fix:* Add all six URLs. Also fix the priority scheme — `blog.html` is currently `0.6` while `chat.html` is `0.5` and `privacy.html` is `0.3`; relative priority should reflect commercial value, so blog posts at `0.6`, service pages at `0.8`.
*Safe to automate:* **Yes.**

**T2 — Orphaned indexable verification file. High.**
`zohoverify/verifyforzoho.html` has **no `<title>`, no meta description, no canonical, no `noindex`, and 0 words of body content**. It is a Zoho Mail domain-verification token file. If crawled, it is a textbook thin/soft-404 page.
*Fix:* Add `<meta name="robots" content="noindex, nofollow">` — do **not** delete the file or Zoho Mail verification breaks. Optionally add `Disallow: /zohoverify/` to `robots.txt` as belt-and-braces.
*Safe to automate:* **Yes** (adding the meta tag only — deleting the file is not).

**T3 — `404.html` declares itself canonical. Medium.**
`404.html:6` sets `<link rel="canonical" href="https://trecoleman.com/404.html">` plus a full OG/Twitter card set (`:7-16`). A 404 page should never invite indexing.
*Why it matters:* Netlify serves `404.html` with an HTTP 404 status, which protects you in practice — but the canonical tag actively contradicts the status code, and any misconfiguration (or a soft-404 path) turns this into an indexable error page.
*Fix:* Remove the canonical and OG/Twitter blocks; add `<meta name="robots" content="noindex">`. Keep the helpful navigation links — a good 404 that recirculates users is worth having.
*Safe to automate:* **Yes.**

**T4 — No `<lastmod>` anywhere in the sitemap. Medium.**
Every entry has `<priority>` and `<changefreq>` — the two elements Google has publicly said it largely ignores — and lacks `<lastmod>`, the one it uses.
*Fix:* Add `<lastmod>` to every URL, ideally generated from git commit dates so it stays honest. A stale or fabricated `<lastmod>` is worse than none.
*Safe to automate:* **Yes**, if generated from `git log -1 --format=%cI -- <file>`.

**T5 — `robots.txt` is a three-line allow-all. Low.**
```
User-agent: *
Allow: /

Sitemap: https://trecoleman.com/sitemap.xml
```
The `Sitemap:` directive is correct. Gated paths (`/course/`, `/client-assistant/`, `/zohoverify/`) rely solely on page-level `noindex`, which is the technically correct mechanism — a `Disallow` would actually *prevent* Google from seeing the `noindex`. So the current setup is defensible.
*Fix (optional):* Add `Disallow: /course/downloads/` — those are binary files that can't carry a `noindex` meta tag and are currently crawlable.
*Safe to automate:* **Yes.**

**T6 — Paid product downloadable without payment. High (business risk, not SEO).**
`Catering Profit Course-20260315T205458Z-3-001.zip` sits in the repository root and, with `publish = "."` in `netlify.toml`, is served at `https://trecoleman.com/Catering%20Profit%20Course-20260315T205458Z-3-001.zip`. It contains **26 files — the complete $67 product** (all five modules' spreadsheets and documents plus the bonus pack). Separately, `/course/downloads/**` is protected only by client-side JS (`course/auth.js` reads `localStorage`), so direct URLs bypass authentication entirely. `lead system.pdf` is likewise public at the root.
*Why it's in an SEO audit:* Google indexes ZIP, PDF, XLSX, and DOCX files. Your paid product can appear in search results.
*Fix:* Remove the ZIP from the repo (it is redundant — the same files are already in `course/downloads/`). Gate `/course/downloads/` behind a Netlify function or signed URLs. At minimum, add `Disallow: /course/downloads/` and remove the root ZIP.
*Safe to automate:* **No** — deleting a product file and changing an auth model needs your sign-off.

---

### 2.2 Internal linking & site architecture — the biggest structural problem

**T7 — Money pages are orphaned. Critical.**

Inbound internal link counts across the whole site:

| Page | Inbound links | Commercial value |
|---|---:|---|
| `profit-leak-snapshot.html` | 78 | High ✅ |
| `blog.html` | 55 | Medium ✅ |
| `advisory.html` | 54 | High ✅ |
| `services.html` | 52 | High ✅ |
| `contact.html` | 51 | High ✅ |
| `virginia-neighbors.html` | 39 | Low ⚠️ over-linked |
| `login.html` | 32 | **None** ⚠️ over-linked |
| **`ai-integration.html`** | **1** | **High** 🔴 |
| **`sops-training.html`** | **1** | **High** 🔴 |
| **`lsm.html`** | **1** | **High** 🔴 |
| **`menu-engineering.html`** | **1** | **High** 🔴 |
| each `/blog/blog_post_*.html` | 2 | Medium 🔴 |

*Why it matters:* Internal links are how you tell a search engine which of your pages matter. Right now `login.html` — a `noindex` auth page — has **32× more internal links than your menu engineering service page**. The four orphaned pages are the ones that target "restaurant menu engineering consultant", "restaurant SOP consultant", "local store marketing agency", and "AI for restaurants" — the searches your buyers actually run.

*Fix (three parts):*
1. Add a **"Services ▾" dropdown** to the main nav containing all five service pages. The dropdown pattern already exists and works (`services.html` nav → "Insights", "Resources"), so this is a copy-paste of an established component.
2. Add a **Services column to the footer**, which appears on all 41 pages. Move `login.html` out of the nav dropdown into the footer only.
3. Add **contextual body links** inside each service page to its two nearest siblings ("Menu engineering pairs well with [SOPs & training]…"). Currently every service page's only body link is to `profit-leak-snapshot.html` — one link each (`ai-integration.html`, `sops-training.html`, `lsm.html`, `menu-engineering.html`).

*Safe to automate:* **Partly.** Nav and footer changes are mechanical and automatable — but note there are already two GitHub Actions (`.github/workflows/update-navigation.yml`, `.github/workflows/fix-audit-navigation.yml`) that do regex surgery on nav blocks, and the second exists specifically to repair damage the first caused ("*the problem: broken HTML structure where Resources tab was inserted incorrectly*"). **Do not add a third regex workflow.** Contextual body links must be written by hand — they need real editorial judgment.

**T8 — The homepage has the *smallest* navigation on the site. High.**
`index.html:702-710` renders 5 nav links. Every other page renders 14 (`services.html`, `about.html`, `advisory.html`, and 30+ others). Your strongest page — the one that accumulates the most external authority — passes the least of it onward.
*Fix:* Standardise `index.html`'s nav to match the rest of the site (plus the new Services dropdown from T7).
*Safe to automate:* **Yes**, carefully — see the warning above about the existing regex workflows.

**T9 — No breadcrumbs anywhere. Medium.**
Blog posts sit at `/blog/…` with no breadcrumb trail, and no `BreadcrumbList` schema exists anywhere in the repo. Blog posts have a single "← Back to all posts" link (`blog/blog_post_1_profit_leaks_rewritten.html:41`), which is a partial substitute but doesn't produce breadcrumb rich results.
*Fix:* Add visible breadcrumbs plus `BreadcrumbList` JSON-LD on blog posts and service pages. Home → Blog → Post; Home → Services → Menu Engineering.
*Safe to automate:* **Yes.**

**T10 — Blog posts don't link to the services they discuss. High (conversion + topical).**
`blog_post_3_menu_engineering_rewritten.html` is a 1,186-word guide to menu engineering that **does not link to `menu-engineering.html`**. Same pattern across all five: `blog_post_4_fractional_coo` doesn't link to `advisory.html`; `blog_post_5_catering_profitability` doesn't link to `catering-profit.html` or `menu-engineering.html`. Every post's only body CTA is `../profit-leak-snapshot.html` (line 92 in post 1).
*Why it matters:* This is the single cheapest topical-authority and conversion fix on the site. The reader has just spent seven minutes reading about menu engineering; the service page is the obvious next step and it isn't offered.
*Fix:* 2–4 contextual in-body links per post to the matching service page, using descriptive anchor text.
*Safe to automate:* **No** — placement and anchor text require reading the surrounding prose.

**T11 — Non-semantic dropdown toggles. Low.**
Nav dropdowns use `<a href="#" onclick="return false;">` (e.g. `services.html` nav). Crawlers see `href="#"`, and keyboard/screen-reader users get a link that isn't a link.
*Fix:* Use `<button aria-expanded="false" aria-haspopup="true">`. Minor SEO impact, real accessibility impact.
*Safe to automate:* **Yes.**

---

### 2.3 Structured data

**T12 — No `Article`/`BlogPosting` schema on any blog post. High.**
Zero of the six article pages carry `Article` or `BlogPosting` markup. They also carry **no visible publish date, no modified date, and no author byline** — verified by inspecting `blog/blog_post_1_profit_leaks_rewritten.html` end to end.
*Why it matters:* For a consultant, author attribution is the E-E-A-T signal. Anonymous, undated articles are exactly what Google's helpful-content systems treat as low-trust.
*Fix:* Add `BlogPosting` with `headline`, `datePublished`, `dateModified`, `author: {"@id": "https://trecoleman.com/#person"}` (the `Person` node already exists at `index.html:632`), `publisher`, `image`, and `mainEntityOfPage`. Add a visible byline and date to match — schema must never assert something the page doesn't show. **[VERIFY]** the real publication dates before adding them; do not back-date.
*Safe to automate:* **Partly** — structure yes, dates no.

**T13 — No `BreadcrumbList` schema anywhere. Medium.** See T9.

**T14 — No `WebSite` schema on the homepage. Low.**
Adding a `WebSite` node with `name`, `url`, and `publisher` to the existing `@graph` (`index.html:532`) is a two-minute addition that helps entity consolidation. Skip `SearchAction` — the site has no search function, and declaring one you don't have is invalid markup.
*Safe to automate:* **Yes.**

**T15 — `Service` schema exists only on `services.html`, not on the service pages themselves. Medium.**
`services.html:76-176` defines six `Service` entities with `@id` values pointing at `ai-integration.html`, `sops-training.html`, `lsm.html`, `menu-engineering.html`, `advisory.html`, and `profit-leak-snapshot.html` — but those six pages carry no schema of their own. The `@id`s are doing the right thing conceptually, but each service page should also self-describe.
*Fix:* Move (or mirror) each `Service` block onto its own page, keeping the same `@id` so the graph stays consistent.
*Safe to automate:* **Yes.**

**T16 — No `Review`/`AggregateRating` schema. Correct as-is — do not "fix" this.**
The only testimonial on the site is anonymous: *"— Multi-Unit Franchisee, Virginia"* (`index.html:825`). Anonymous testimonials **cannot** support valid `Review` schema — Google requires a named `author`, and self-serving `AggregateRating` on your own site is against their guidelines and a manual-action risk. The current absence of review schema is the right call. To gain it legitimately, collect named, attributed testimonials with written permission (see §5). **[VERIFY]**

**T17 — `priceRange: "$350–$50,000"` uses an en-dash. Low.**
`index.html:546`. `priceRange` is a free-text field so this won't invalidate, but the conventional `$$` / `$$$` format or a plain hyphen parses more reliably.
*Safe to automate:* **Yes.**

---

### 2.4 Core Web Vitals

**T18 — LCP: the homepage hero is a 2 MB PNG. Critical.**
`index.html:319`: `background: url('hero.png') center/cover no-repeat;` applied to `.hero` (`index.html:715`). `hero.png` is **2,004 KB at 1536×1024**. As a CSS background it cannot be preloaded, cannot be `fetchpriority="high"`, and cannot use `<picture>` for responsive sources. On a 4G connection this alone is several seconds of LCP.
*Fix:* Convert to WebP/AVIF at ~1600px wide (expect 100–200 KB), serve via `<img>` with `fetchpriority="high"` and `<picture>` sources rather than a CSS background, and add `<link rel="preload" as="image">`.
*Safe to automate:* **Partly** — conversion and compression yes; changing background→`<img>` needs a visual check.

**T19 — `services.html` ships ~9.6 MB of images. Critical.**
Six PNGs at `services.html:262, 271, 279, 287, 295, 303`:

| Line | File | Size | Dimensions | Displayed at |
|---|---|---:|---|---|
| 262 | `fixed systems.png` | 1,668 KB | 1024×1024 | max 700px |
| 271 | `ChatGPT Image Feb 3, 2026, 08_52_24 PM.png` | 1,844 KB | 1024×1536 | max 280px |
| 279 | `Reviewing KPIs in a modern office.png` | 1,930 KB | 1024×1536 | max 280px |
| 287 | `ChatGPT Image Feb 3, 2026, 08_53_59 PM.png` | 1,913 KB | 1024×1536 | max 280px |
| 295 | `Reviewing restaurant menus and notes.png` | 1,920 KB | 1024×1536 | max 280px |
| 303 | `ChatGPT Image Feb 3, 2026, 08_55_43 PM.png` | 2,060 KB | 1024×1536 | max 280px |

Five images displayed at **280 px wide** are being downloaded at **1024 px wide and ~1.9 MB each**. That is roughly 50× more bytes than needed.
*Fix:* Resize to 2× display width (560 px), convert to WebP. Expect ~20 KB each — a **~99% reduction**, from 9.6 MB to under 150 KB.
*Safe to automate:* **Yes** (image processing is deterministic; keep originals).

**T20 — Render-blocking font `@import`. High.**
`style.css:10`: `@import url('https://fonts.googleapis.com/css2?…')`. A CSS `@import` cannot begin until `style.css` itself has downloaded and parsed, creating a serial request chain: HTML → style.css → fonts.googleapis.com → font files. It also has no `preconnect`.
`index.html:28-30` and `virginia-neighbors.html:22` already do this correctly with `<link rel="preconnect">` + `<link rel="stylesheet">` — but the `@import` in `style.css` still fires on those pages too, duplicating the request.
*Fix:* Delete line 10 of `style.css`; add the preconnect+link pair to every page's `<head>`. Confirm `&display=swap` is present (it is) to prevent invisible text.
*Safe to automate:* **Yes.**

**T21 — Zero `width`/`height` attributes on any image → guaranteed CLS. High.**
All 11 `<img>` tags across the site lack intrinsic dimensions; sizing is done via inline `style="max-width:…; height:auto"`. The browser cannot reserve space, so every image causes layout shift as it loads.
*Fix:* Add `width` and `height` matching the intrinsic dimensions (all listed in T19 and below), and keep the CSS `max-width:100%; height:auto` so responsiveness is unaffected. This is the standard modern pattern and it fully eliminates CLS.
*Safe to automate:* **Yes** — dimensions are already measured.

**T22 — No `loading="lazy"` on any image. Medium.**
No image on the site is lazy-loaded. On `services.html` this means all six multi-megabyte PNGs load immediately, including the five below the fold.
*Fix:* `loading="lazy"` on every below-fold image. Do **not** lazy-load the LCP/hero image.
*Safe to automate:* **Yes**, with manual confirmation of which image is above the fold per page.

**T23 — Seven pages hot-link hero backgrounds from Unsplash's CDN. High.**

| File | Line |
|---|---|
| `advisory.html` | 76 |
| `ai-integration.html` | 78 |
| `lsm.html` | 78 |
| `menu-engineering.html` | 78 |
| `sops-training.html` | 78 |
| `audit.html` | 120 |
| `food-truck-audit.html` | 70 |

Each loads a 1920px image from `images.unsplash.com` as a CSS background.
*Why it matters:* Three compounding problems. **(a) Performance** — an uncached third-party DNS + TLS + fetch on the LCP element of seven pages. **(b) Reliability** — if Unsplash changes or removes a photo ID, seven hero sections break silently. **(c) Licensing** — hot-linking is not the same as licensed use, and Unsplash's terms don't guarantee permanent hosting. **[VERIFY]** the license status of each photo before continuing to use them commercially.
*Fix:* Download, optimise, self-host, and confirm licensing. Same treatment as T18/T19.
*Safe to automate:* **No** — licensing verification is a human decision.

**T24 — Inline CSS duplicated across pages. Medium.**
`index.html` carries **500 lines** of inline `<style>`; `advisory.html` 432; `food-truck-audit.html` 328; `audit.html` 322; `menu-engineering.html` 222. Much of this is repeated page to page (the service pages share near-identical styling). Additionally there are 42 inline `style="…"` attributes on `index.html` and 41 on `services.html`.
*Why it matters:* Inline `<style>` isn't cacheable across pages, so a returning visitor re-downloads it every time. It also makes maintenance error-prone — the exact class of problem that produced `fix-audit-navigation.yml`.
*Fix:* Extract shared rules to `style.css`; keep only genuinely page-specific critical CSS inline.
*Safe to automate:* **No** — high regression risk across 40 pages.

**T25 — Three unused multi-megabyte images in the repo. Low.**
`cross train.png` (1,494 KB), `food sells first.png` (1,612 KB), `forgottenarm.png` (1,403 KB) are referenced by no HTML or CSS file — 4.4 MB of dead weight. They aren't served to users, so this is repo hygiene, not a CWV issue.
*Fix:* Remove, or move to an `assets-source/` folder excluded from the publish directory. **[VERIFY]** they aren't used in social posts or email before deleting.
*Safe to automate:* **No.**

**T26 — INP risk is otherwise low.** `analytics.js` uses passive event delegation. `header-scroll.js` attaches a non-passive `scroll` listener that does a single `classList` toggle — negligible, but adding `{passive: true}` is free. Only `profit-leak-calculator.html` loads React + Babel-standalone from CDN (`:17-19`), and that page is `noindex` and orphaned (see T34).

**T41 — An undisclosed third-party chat widget is hidden inside the exit-intent script. High.**
`exit-intent-popup.js:18-25` loads **Crisp Chat** from `https://client.crisp.chat/l.js`. This has nothing to do with exit intent — the file's own header comment describes only a lead-magnet modal, and the Crisp loader was appended above it. It executes on **17 pages**, including `services.html`, `profit-leak-snapshot.html`, `advisory.html`, and all five blog posts.

Three separate problems:

- **Performance.** A live-chat widget is one of the heaviest third-party categories on the web — additional DNS, TLS, script, websocket, and font requests, plus main-thread work that lands squarely in the INP measurement window. It is `defer`red, which helps, but it still runs on your most commercially important pages.
- **The Website ID looks malformed.** `window.CRISP_WEBSITE_ID="be57159b-af24-45a1-8e47-1207df3715lf"` (`:20`). Crisp IDs are UUIDs, which are hexadecimal — and `l` is not a hex character. This is very likely a typo for `1`. If so, the widget is loading Crisp's script on 17 pages and then failing to initialise, meaning you pay the full performance cost and get no chat. **[VERIFY]** in the Crisp dashboard and by opening any of those 17 pages.
- **It is not disclosed in your privacy policy.** `privacy.html` describes a Calendly scheduling widget (`:132`) that **does not exist anywhere in the repository**, and does not mention Crisp, which does load and does set identifiers. The policy documents a tool you don't use and omits one you do.

*Fix:* Decide whether you want live chat. If yes — separate it from `exit-intent-popup.js` into its own file, fix the Website ID, load it lazily on interaction rather than on page load, and add it to the privacy policy. If no — delete lines 18-25. Either way, correct `privacy.html` so it describes the tools actually in use.
*Safe to automate:* **No** — this is a business decision about a customer-facing channel plus a privacy-disclosure correction.

**T42 — Exit-intent lead capture is missing from the two highest-value pages. Medium (conversion).**
`exit-intent-popup.js` runs on 17 pages but **not** on `index.html` or `contact.html` — the homepage and the contact page. It also uses `formsubmit.co` (`:208`), the same third-party form relay as `contact.html:123`.
*Fix:* Add the script to `index.html` (suppressing it on `contact.html` is defensible — a user already on the contact page doesn't need an exit offer). Note that the popup's own A/B logic and FormSubmit captures are not instrumented in GA4 (see A9).
*Safe to automate:* **Yes** for adding the script tag.

---

### 2.5 Metadata & on-page structure

**T27 — `og:image` is 200×200 while pages declare `summary_large_image`. High.**
~20 pages point `og:image` and `twitter:image` at `images/tre-headshot.jpg`, which is **200×200 px, 10 KB**, while declaring `<meta name="twitter:card" content="summary_large_image">`. Twitter/X requires a minimum of 300×157 for that card; Facebook/LinkedIn recommend 1200×630. `index.html:18` and `blog.html` use `familypic.jpg` (1440×1541 — large but portrait, so it'll be centre-cropped badly).
*Fix:* Create one 1200×630 branded OG image (headshot + name + "Restaurant Operations Consultant" + logo). Repoint all `og:image`/`twitter:image` to it. Add `og:image:width`, `og:image:height`, and `og:image:alt`. Per-page images later, as a refinement.
*Safe to automate:* **Yes** (the repointing; the image needs designing).

**T28 — Six meta descriptions exceed ~160 characters and will truncate. Medium.**

| Page | Length | File |
|---|---:|---|
| `services.html` | 212 | `services.html:8-10` |
| `audit.html` | 202 | `audit.html` head |
| `advisory.html` | 201 | `advisory.html` head |
| `index.html` | 188 | `index.html:8-10` |
| `profit-leak-snapshot.html` | 187 | head |
| `blog_post_4_fractional_coo…` | 171 | head |

Rewrites in §3.

**T29 — Titles are brand-heavy and location-free. Medium.**
Almost every title follows `[Topic] | Tre Coleman`. "Tre Coleman" is not yet a search-demand brand, so it consumes 14 characters of a ~60-character budget that should carry qualifiers buyers actually type — *Virginia*, *for restaurants*, *consultant*. Several are also too short to be working: `chat.html` at 21 chars, `contact.html` at 21, `menu-engineering.html` at 30. Full rewrites in §3.

**T30 — Heading hierarchy skips H1 → H4 on four pages. Low.**
`contact.html`, `privacy.html`, `404.html`, and `unreasonably-optimistic.html` have an `<h1>` followed directly by the footer's three `<h4>` elements, with no `<h2>`/`<h3>` between. On `contact.html` this reflects a genuinely thin page (see T33). Accessibility issue more than ranking issue.
*Fix:* Change footer column headings from `<h4>` to `<h2>` (they are section headings), or add real `<h2>` content sections to these pages.
*Safe to automate:* **Yes** for the footer change.

**T31 — Emoji in H1 on two pages. Low.**
`audit.html:393` — `<h1>🍽️ Hospitality Operations Audit</h1>`; `food-truck-audit.html` — `<h1>🚚 Food Truck Launch Readiness Audit</h1>`. Google renders these fine but the emoji occupies characters in a title-adjacent signal and reads inconsistently across platforms.
*Fix:* Move emoji out of the H1 into an adjacent decorative `<span aria-hidden="true">`.
*Safe to automate:* **Yes.**

**T32 — No `<main>` element and no skip-links on any page. Low.**
No page uses `<main>` or `role="main"`; no page has a skip-to-content link. `<article>` appears only on blog posts. This affects screen-reader navigation and Google's main-content extraction.
*Fix:* Wrap primary content in `<main>`; add a skip link as the first focusable element.
*Safe to automate:* **Yes**, with care around existing structure.

---

### 2.6 Thin, duplicate, and orphaned pages

**T33 — `contact.html` is the thinnest important page on the site. High.**
341 words including nav and footer boilerplate — realistically ~60 words of unique content: an H1, one line of copy, one pricing line, and a form (`contact.html:122-123`). It receives 51 internal links, making it one of the most-linked pages on the site, and it has almost nothing to rank with.
*Why it matters:* "restaurant consultant contact" is low-volume, but this page is where high-intent traffic converts. Thin contact pages also underperform on the local pack.
*Fix:* Expand to 400–600 words: what happens after you submit, response time, who this is for and who it isn't, service areas (named Virginia markets — see §5), phone and email in crawlable text (currently only in the footer), and 3–4 FAQs. Add `ContactPage` schema.
*Safe to automate:* **No** — needs real copy and **[VERIFY]** on response-time claims.

**T34 — `profit-leak-calculator.html` is a 3,044-word orphan. Medium.**
`noindex`, **zero inbound links from anywhere**, React + Babel-standalone loaded from CDN (`:17-19`), no meta description. It's a genuinely useful interactive tool that no user or crawler can reach.
*Fix:* Decide deliberately. Either **(a)** make it a lead magnet — remove `noindex`, add a wrapper page with real indexable copy explaining the calculator, link it from the nav Resources dropdown alongside the two audits, gate results behind an email capture; or **(b)** delete it. Option (a) is the better business call: an interactive profit calculator is exactly the kind of asset that earns links from restaurant-industry sites. If you keep it, replace Babel-standalone with a pre-compiled bundle — in-browser JSX compilation is a significant runtime cost.
*Safe to automate:* **No** — strategic decision.

**T35 — The four service pages are near-duplicate templates. Medium.**
All four use an identical H2 skeleton:

> The Problem You're Facing → What [X] Delivers → How We [X] → Real Outcomes You Can Expect → What's Included → Who This Is For → Ready to [X]?

At 790–890 words each, with the same structure and similar surrounding boilerplate, they sit close to the near-duplicate threshold. The *body copy* is genuinely distinct — this is a template-similarity risk, not plagiarism.
*Fix:* Differentiate meaningfully rather than cosmetically: add a short case example, a service-specific FAQ block, and 2–3 unique H2s per page. Vary the section ordering.
*Safe to automate:* **No.**

**T36 — `chat.html` and `virginia-neighbors.html` are client-side rendered. Medium.**
`virginia-neighbors.html` renders "Loading directory…" in static HTML and fetches listings from `/.netlify/functions/airtable-proxy` (`:468, :499`). Google *can* render JS, but does so on a delayed second pass and with no guarantee. The directory content — the page's entire value — is invisible in the initial HTML. `chat.html` is similar at 516 words.
*Why it matters:* `virginia-neighbors.html` has 39 internal links (4th most on the site) but is a `0.6`-priority page whose content Google may never see. That's a lot of internal link equity flowing into a page that can't use it.
*Fix:* Server-render the directory at build time, or at minimum add substantial static above-the-fold copy about Virginia food-service businesses so the page has indexable content regardless of JS execution. Also reconsider whether it deserves 39 internal links versus your service pages' 1.
*Safe to automate:* **No.**

**T37 — `audit.html` and `food-truck-audit.html` are large but content-thin. Low.**
3,722 and 4,263 words respectively — but the overwhelming majority is `<select>`/`<option>` form text ("Under 25% (Excellent)", "25-30% (Good)"). Actual indexable prose is a few hundred words. They rank for nothing in their current state despite `0.8` sitemap priority.
*Fix:* Add 400–600 words of genuine introductory content above the tool — what the audit covers, what the benchmarks mean, why each metric matters. This turns two form pages into two rankable pages targeting "restaurant operations checklist" and "food truck startup checklist".
*Safe to automate:* **No.**

---

### 2.7 Mobile & accessibility

| Finding | Severity | Detail |
|---|---|---|
| Viewport meta present on all pages | ✅ | Correct, no `user-scalable=no` |
| Responsive breakpoints exist | ✅ | `style.css:306, 873, 960, 1005, 1052` |
| Mobile menu with Escape-key close & focus handling | ✅ | Better than most |
| `aria-label` on menu toggle | ✅ | Present |
| No `:focus-visible` styles | Medium | `style.css:763-770` styles `:focus` on form inputs only — links and buttons have no visible focus indicator |
| No `prefers-reduced-motion` support | Low | No occurrences in `style.css` |
| Dropdown toggles are `<a href="#">` | Medium | See T11 |
| No `<main>`, no skip link | Low | See T32 |
| Alt text present on 10 of 11 images | ✅ | Only real gap is quality, not presence |

**T38 — Alt text is generic on decorative/illustrative images. Low.**
`services.html:271` — `alt="AI Integration for restaurants"`; `:295` — `alt="Menu engineering and analysis"`. These are illustrative images beside headings that already say the same thing, so the alt text is redundant rather than descriptive. Two are good: `advisory.html:543` (`alt="Calm operations are built. They are not a personality trait."`) and `catering-profit.html:594` accurately transcribe text-bearing images — that's exactly right.
*Fix:* For images that carry text, transcribe the text. For purely decorative ones, `alt=""` is more correct than a keyword-flavoured phrase.

**T39 — Image filenames are not crawl-friendly. Low.**
`ChatGPT Image Feb 3, 2026, 08_52_24 PM.png` (×3), `Reviewing KPIs in a modern office.png`, `calm ops.png`, `fixed systems.png` — spaces force `%20` encoding in every `src`, and "ChatGPT Image Feb 3" tells Google Images nothing.
*Fix:* Rename to lowercase-hyphenated descriptive slugs — `ai-integration-restaurant-consulting.webp`, `restaurant-kpi-review.webp`. Do this in the same pass as the WebP conversion so `src` attributes are only touched once.
*Safe to automate:* **Yes**, if `src` updates are done in the same commit.

---

## 3. Metadata audit

All 26 indexable pages. Character counts are exact. "Canonical" = self-referencing absolute canonical present. "OG" = ✅ full Open Graph + Twitter card set; ⚠️ = present but broken image (see T27).

### Core commercial pages

| Route | Current title (len) | Current meta description (len) | Canon | OG | Primary keyword / intent | Problems | Recommended title | Recommended description |
|---|---|---|---|---|---|---|---|---|
| `/` | Restaurant Operations Consultant \| Tre Coleman (46) | I help independent restaurants, food trucks, and catering companies find and fix profit leaks… (188) | ✅ | ⚠️ | "restaurant operations consultant" — commercial | Desc 28 over; no location in title; `og:image` portrait crop | Restaurant Operations Consultant in Virginia \| Tre Coleman (58) | Independent restaurant, food truck, and catering operators: find and fix $10K–$50K in annual profit leaks. Virginia-based, working nationwide. (141) |
| `/services.html` | Restaurant Consulting Services \| Tre Coleman (44) | Restaurant consulting services for independent operators: AI integration, SOPs and training… (212) | ✅ | ⚠️ | "restaurant consulting services" — commercial | Desc 52 over — worst on site; title omits food truck/catering | Restaurant & Food Service Consulting Services \| Tre Coleman (58) | AI workflows, SOPs and training, menu engineering, local marketing, and fractional ops support for independent restaurant and catering operators. (144) |
| `/advisory.html` | Fractional COO for Hospitality Operations \| Tre Coleman (55) | Weekly strategy calls. Unlimited support. Real accountability… (201) | ✅ | ⚠️ | "fractional COO restaurant" — high commercial | Desc 41 over; "Unlimited support" is an absolute claim **[VERIFY]** | Fractional COO for Restaurants & Food Trucks \| Tre Coleman (57) | Weekly strategy calls, KPI reviews, and on-call operator support for $1M+ restaurant and catering operations. $2,000/mo, no long-term contract. (142) |
| `/profit-leak-snapshot.html` | Profit Leak Snapshot \| Tre Coleman (34) | Your restaurant, food truck, or catering operation is profitable on paper… (187) | ✅ | ⚠️ | "restaurant profit analysis" — transactional | Desc 27 over; title has no keyword a buyer would type | Restaurant Profit Leak Snapshot \| 90-Minute Diagnostic (53) | A 90-minute session on your P&L, labor, and item mix. Leave with your top 3 profit leaks priced in dollars and a prioritized fix list. $350. (139) |
| `/contact.html` | Contact \| Tre Coleman (21) | Tell me your bottleneck. Get a simple first step today. (55) | ✅ | ⚠️ | "restaurant consultant contact" — navigational | Title & desc both far too short; page is thin (T33) | Contact a Restaurant Operations Consultant \| Tre Coleman (55) | Tell me where your operation is bottlenecked and get a practical first step. Book a $350 Profit Leak Snapshot or send a note about your operation. (146) |

### Service pages (currently orphaned — see T7)

| Route | Current title (len) | Current meta description (len) | Canon | OG | Primary keyword / intent | Problems | Recommended title | Recommended description |
|---|---|---|---|---|---|---|---|---|
| `/ai-integration.html` | AI Integration & Automation \| Tre Coleman (41) | Transform restaurant operations with AI automation. Cut admin time 40-60%… (160) | ✅ | ⚠️ | "AI for restaurant operations" — commercial | Title omits "restaurant" — the qualifier that makes it findable; "40-60%" **[VERIFY]** | AI Automation for Restaurant Operations \| Tre Coleman (52) | Cut manager admin time with practical AI workflows for scheduling, prep, reporting, and training. Built by an operator, rolled out without floor disruption. (154) |
| `/sops-training.html` | SOPs & Training Systems \| Tre Coleman (37) | Build training systems that eliminate tribal knowledge and get new hires productive 50% faster… (164) | ✅ | ⚠️ | "restaurant SOP development" — commercial | Title omits "restaurant"; "50% faster" **[VERIFY]** | Restaurant SOPs & Staff Training Systems \| Tre Coleman (53) | Role scorecards, opening and closing checklists, and 30-60-90 onboarding plans that end tribal knowledge and shorten new-hire ramp time. (135) |
| `/lsm.html` | Local Store Marketing (LSM) \| Tre Coleman (41) | Drive consistent traffic with trackable local marketing. 12-week calendars… (150) | ✅ | ⚠️ | "local store marketing restaurant" — commercial | "(LSM)" is industry jargon consuming title space | Local Store Marketing for Restaurants \| Tre Coleman (50) | 12-week local marketing calendars, community partnerships, and trackable offers that fill slow shifts for restaurants and food trucks. (133) |
| `/menu-engineering.html` | Menu Engineering \| Tre Coleman (30) | Find the hidden profit in your menu. Contribution margin analysis… lift check average 12-18%… (161) | ✅ | ⚠️ | "menu engineering consultant" — high commercial | Title 30 chars — wasting half the budget; "12-18%" **[VERIFY]** | Menu Engineering for Independent Restaurants \| Tre Coleman (57) | Contribution margin analysis, menu redesign, and server training that shift your mix toward high-profit items without across-the-board price hikes. (146) |

### Content & lead-magnet pages

| Route | Current title (len) | Current meta description (len) | Canon | OG | Primary keyword / intent | Problems | Recommended title | Recommended description |
|---|---|---|---|---|---|---|---|---|
| `/blog.html` | Insights & Playbooks \| Tre Coleman (34) | Operator-first insights on AI integration, restaurant operations… (122) | ✅ | ⚠️ | "restaurant operations blog" — informational | Title lacks "restaurant"; `og:image` = portrait `familypic.jpg` | Restaurant Operations Insights & Playbooks \| Tre Coleman (55) | Practical operations, profitability, and marketing playbooks for independent restaurant, food truck, and catering operators. No theory, just systems. (148) |
| `/blog/blog_post_1_profit_leaks_rewritten.html` | Stop Restaurant Profit Leaks: A Practical Guide \| Tre Coleman (61) | Discover how to identify and eliminate hidden profit leaks… (158) | ✅ | ⚠️ | "restaurant profit leaks" — informational | URL slug is a filename, not a slug; no date/author/`Article` schema; not in sitemap | How to Find & Fix Restaurant Profit Leaks \| Tre Coleman (54) | Where independent restaurants quietly lose margin — labor, item mix, waste, and cash flow — and the checks that surface each one. (129) |
| `/blog/blog_post_2_systems_growth_rewritten.html` | Restaurant Systems for Sustainable Growth \| Tre Coleman (55) | Move beyond daily firefighting… (161) | ✅ | ⚠️ | "restaurant operational systems" — informational | Same as above | Restaurant Systems That Support Real Growth \| Tre Coleman (56) | Move past daily firefighting. The SOPs, scheduling structure, and financial tracking that let an operation grow without the owner in the room. (140) |
| `/blog/blog_post_3_menu_engineering_rewritten.html` | Restaurant Menu Engineering: Maximize Your Menu \| Tre Coleman (61) | Your menu is your most powerful profit tool… (154) | ✅ | ⚠️ | "menu engineering guide" — informational | Same; **doesn't link to `/menu-engineering.html`** (T10) | Menu Engineering Guide for Restaurant Owners \| Tre Coleman (57) | How to map contribution margin against popularity, find the items quietly costing you money, and redesign your menu around what actually pays. (140) |
| `/blog/blog_post_4_fractional_coo_rewritten.html` | Fractional COO Services for Restaurant Operators \| Tre Coleman (62) | Gain executive-level operational expertise without the overhead… (171) | ✅ | ⚠️ | "fractional COO restaurant" — commercial-informational | Desc 11 over; doesn't link to `/advisory.html` | What a Fractional COO Does for Restaurants \| Tre Coleman (55) | What a fractional COO actually handles week to week, when an operation is ready for one, and how it compares to a full-time hire on cost. (135) |
| `/blog/blog_post_5_catering_profitability_rewritten.html` | Scaling a Catering Business Profitably \| Tre Coleman (52) | Increasing catering volume without the right systems leads to losses… (156) | ✅ | ⚠️ | "catering business profitability" — informational | Same; doesn't link to `/catering-profit.html` | How to Scale a Catering Business Profitably \| Tre Coleman (56) | More catering volume without pricing, staffing, and logistics systems means more revenue and less profit. Here's the order to build them in. (139) |
| `/unreasonably-optimistic.html` | Unreasonably Optimistic \| Tre Coleman (37) | The difference between restaurant owners who turn things around… (159) | ✅ | ⚠️ | Brand/thought-leadership — informational | No keyword target; not in sitemap | Unreasonably Optimistic: Operating Through Uncertainty (53) | Why the operators who turn things around aren't the most experienced — they're the ones who keep moving before they feel certain. (128) |
| `/playbook.html` | 90-Day Profit Playbook \| Tre Coleman (36) | A step-by-step 90-day playbook for restaurant operators… (125) | ✅ | ⚠️ | "restaurant profit plan" — informational, lead magnet | Title/desc under-length; email gate (`:112`) hides 4,166 words | Free 90-Day Restaurant Profit Playbook \| Tre Coleman (51) | A week-by-week plan for independent operators to find profit leaks and fix labor, menu pricing, and daily operations. Free, no fluff. (131) |
| `/audit.html` | Free Hospitality Operations Audit - Tre' Coleman (48) | Get a free hospitality operations audit… (202) | ✅ | ⚠️ | "restaurant operations audit" — informational, lead magnet | Desc 42 over; smart-apostrophe "Tre'" inconsistent with all other titles; emoji H1 | Free Restaurant Operations Audit (10-Minute Self-Check) (54) | Score your operation across food cost, labor, systems, training, and menu. Get benchmarks and a prioritized fix list in about ten minutes. (136) |
| `/food-truck-audit.html` | Free Food Truck Launch Readiness Audit - Tre' Coleman (53) | Free food truck launch readiness audit… (141) | ✅ | ⚠️ | "food truck launch checklist" — informational, lead magnet | Smart-apostrophe inconsistency; emoji H1 | Free Food Truck Launch Readiness Audit \| Tre Coleman (51) | Score your truck across menu, operations, permits, pricing, and marketing before you open. Get your readiness score and what to fix first. (136) |
| `/catering-profit.html` | The Catering Profit System \| Tre Coleman (40) | Scale your catering business without killing your margins… Pre-order now for $67. (149) | ✅ | ⚠️ | "catering business course" — transactional | "Pre-order" — **[VERIFY]** still accurate; hard-coded price will go stale | Catering Profit System: Course for Catering Operators (52) | A self-paced course on catering labor, pricing, food cost, logistics, and cash flow — the systems that turn catering revenue into real profit. (140) |
| `/chat.html` | AI Chat \| Tre Coleman (21) | Chat with our AI assistant. Get generic answers for free… (115) | ✅ | ⚠️ | Low search intent | Title far too short; "generic answers" is unappealing copy; CSR content (T36) | Free AI Restaurant Operations Assistant \| Tre Coleman (52) | Ask an AI assistant trained on restaurant operations about labor, menu engineering, SOPs, and scheduling. Free to try, no account needed. (135) |
| `/virginia-neighbors.html` | Virginia Neighbors – Local Business Directory \| Tre Coleman (59) | A directory of Virginia restaurant, food truck, and catering businesses… (124) | ✅ | ⚠️ | "virginia local business directory" — informational | Content is client-side rendered (T36); 39 internal links to a low-value page | Virginia Local Business Directory \| Tre Coleman (46) | Find Virginia restaurants, food trucks, caterers, and local service businesses — or list your own and connect with neighbors who need you. (136) |
| `/about.html` | About Tre' Coleman \| Operator-first Strategy (44) | Operator-first strategy and execution… (165) | ✅ | ⚠️ | "restaurant consultant Virginia" — brand/navigational | Smart quotes and non-breaking hyphens in title render unpredictably; desc 5 over; no credentials **[VERIFY]** | About Tre Coleman \| Restaurant Operations Consultant (51) | 10+ years running multi-unit restaurant, catering, and food truck operations. Operator-first consulting for owners who need systems, not slide decks. (148) |
| `/privacy.html` | Privacy Policy \| Tre Coleman (28) | Learn how we collect and use data… (92) | ✅ | ⚠️ | Utility | None material — leave as is | *(no change)* | *(no change)* |

### Pages that should not be indexable

| Route | Status | Problem | Fix |
|---|---|---|---|
| `/404.html` | Indexable | Canonical + full OG set on an error page (T3) | Remove canonical/OG; add `noindex` |
| `/zohoverify/verifyforzoho.html` | Indexable | No title, no description, 0 words (T2) | Add `noindex` — **do not delete** |

**Correctly `noindex`** (no action): all 8 `/course/*`, `login`, `register`, `forgot-password`, `reset-password`, `thank-you`, `profit-leak-calculator`, `client-assistant/index`, `email-signature`. Note that `profit-leak-calculator.html`, `thank-you.html`, `email-signature.html`, and `client-assistant/index.html` also lack meta descriptions — harmless while `noindex`, but worth fixing if any is ever exposed (T34).

---

## 4. Content and keyword strategy

### 4.1 Current topical coverage

**Covered well:**
- Restaurant profit leaks / profitability diagnostics — the strongest cluster (`index.html`, `profit-leak-snapshot.html`, blog post 1, `playbook.html`, `audit.html`)
- Menu engineering — service page + blog post + course module
- SOPs & training systems — service page + blog post 2
- Fractional COO / advisory — service page + blog post 4
- Catering profitability — service page, course, blog post 5, `food-truck-audit.html` adjacency
- AI in restaurant operations — service page + `chat.html`; genuinely differentiated positioning
- Local store marketing — service page

**Covered thinly:**
- Food trucks — one audit tool, no service page. `food-truck-audit.html` (4,263 words) is the only dedicated asset, and it's a form.
- Local store marketing — one page, no supporting content

**Not covered at all:**
- **Ghost kitchens** — mentioned in `advisory.html`'s meta description and `audit.html`'s, and nowhere else on the site. Zero pages, zero content. You are claiming a service you have no page for.
- **Any named Virginia market** — see §5
- **Restaurant labor cost / scheduling** as a standalone topic (referenced constantly, never given its own page)
- **Restaurant P&L literacy** — the single highest-intent operator search cluster
- **Restaurant staffing & retention**
- **Bottom-funnel comparison content** — "how much does a restaurant consultant cost", "restaurant consultant vs fractional COO"

### 4.2 The gap that matters most

Your site is built almost entirely around **your offer names** (Profit Leak Snapshot, Catering Profit System, 90-Day Profit Playbook) rather than **what operators type into Google**. Nobody searches "Profit Leak Snapshot." They search "why is my restaurant not making money", "restaurant food cost too high", "how to lower labor cost restaurant."

The fix isn't to abandon your branded offers — the offer ladder is a genuine asset. It's to build the informational layer that captures those searches and routes into the ladder you already have.

### 4.3 Recommended target keywords

**No search volume or difficulty figures are given below** — the repository contains no keyword data, and inventing numbers would be worse than omitting them. **[EXTERNAL]** Validate every term in Google Keyword Planner, Ahrefs, or Semrush before committing content resources. Difficulty estimates below are qualitative judgments based on commercial intent and typical SERP composition, not measured scores.

#### Core service keywords

| # | Keyword | Intent | Target page | Suggested CTA |
|---|---|---|---|---|
| 1 | restaurant operations consultant | Commercial | `/` (exists) | Book $350 Snapshot |
| 2 | restaurant consultant for independent operators | Commercial | `/services.html` (exists) | Book $350 Snapshot |
| 3 | fractional COO for restaurants | Commercial, high value | `/advisory.html` (exists) | Book advisory call |
| 4 | hospitality operations consultant | Commercial | `/services.html` (exists) | Book $350 Snapshot |
| 5 | restaurant turnaround consultant | Commercial, urgent | **New page** | Book $350 Snapshot |

#### Restaurant operations & profitability keywords

| # | Keyword | Intent | Target page | Suggested CTA |
|---|---|---|---|---|
| 6 | why is my restaurant not making money | Informational, high pain | **New pillar page** | Free ops audit → Snapshot |
| 7 | how to reduce restaurant labor cost | Informational | **New page** | Free ops audit |
| 8 | restaurant profit margin benchmarks | Informational | **New page** | Free ops audit |
| 9 | menu engineering consultant | Commercial | `/menu-engineering.html` (exists) | Book $350 Snapshot |
| 10 | restaurant SOP templates | Informational, tool-seeking | **New page** + gated download | Email capture → nurture |
| 11 | restaurant P&L explained | Informational | **New page** | Free playbook |

#### Food truck consulting keywords

| # | Keyword | Intent | Target page | Suggested CTA |
|---|---|---|---|---|
| 12 | food truck consultant | Commercial | **New service page** 🔴 *missing* | Book $350 Snapshot |
| 13 | how to start a food truck business | Informational | `/food-truck-audit.html` (expand — T37) | Free readiness audit |
| 14 | food truck profit margin | Informational | **New page** | Free readiness audit |
| 15 | food truck event pricing | Informational, high intent | **New page** | Book $350 Snapshot |

#### Catering consulting keywords

| # | Keyword | Intent | Target page | Suggested CTA |
|---|---|---|---|---|
| 16 | catering business consultant | Commercial | **New service page** 🔴 *missing* | Book $350 Snapshot |
| 17 | how to price catering jobs | Informational, very high intent | **New page** | Catering Profit System ($67) |
| 18 | catering profit margin | Informational | **New page** | Catering Profit System |
| 19 | how to scale a catering business | Informational | Blog post 5 (exists — expand) | Catering Profit System |

#### Ghost kitchen consulting keywords

| # | Keyword | Intent | Target page | Suggested CTA |
|---|---|---|---|---|
| 20 | ghost kitchen consultant | Commercial | **New service page** 🔴 *claimed but missing* | Book $350 Snapshot |
| 21 | ghost kitchen profitability | Informational | **New page** | Free ops audit |
| 22 | virtual brand strategy for restaurants | Informational-commercial | **New page** | Book $350 Snapshot |

> ⚠️ **Only build the ghost-kitchen cluster if you have genuine ghost-kitchen operating experience. [VERIFY]** Two meta descriptions currently claim ghost-kitchen service with no supporting page or stated experience anywhere on the site. If the experience isn't there, remove the claim from those meta descriptions rather than building content around it.

#### Local / service-area keywords

| # | Keyword | Intent | Target page | Suggested CTA |
|---|---|---|---|---|
| 23 | restaurant consultant Virginia | Commercial-local | **New page** | Book $350 Snapshot |
| 24 | restaurant consultant Richmond VA | Commercial-local | **New page** (only if genuine presence) | Book $350 Snapshot |
| 25 | restaurant consultant Charlottesville VA | Commercial-local | **New page** (only if genuine presence) | Book $350 Snapshot |

#### Informational topics that generate qualified leads

| # | Topic | Intent | Target page | Suggested CTA |
|---|---|---|---|---|
| 26 | how much does a restaurant consultant cost | Commercial investigation, **very high intent** | **New page** | Book $350 Snapshot |
| 27 | restaurant consultant vs fractional COO | Commercial comparison | **New page** | Book advisory call |
| 28 | restaurant staff training program | Informational | `/sops-training.html` (exists) | Free ops audit |

### 4.4 Topic-cluster structure

Four clusters, each with a pillar page that links down to spokes and up to a service page.

```
CLUSTER 1 — RESTAURANT PROFITABILITY  (pillar: /restaurant-profitability-guide)
  ├── how to reduce restaurant labor cost
  ├── restaurant profit margin benchmarks
  ├── restaurant P&L explained
  ├── menu engineering guide (blog post 3 — exists)
  ├── restaurant profit leaks (blog post 1 — exists)
  └─→ converts to: /profit-leak-snapshot.html, /menu-engineering.html

CLUSTER 2 — FOOD TRUCK OPERATIONS  (pillar: /food-truck-consulting) ← NEW SERVICE PAGE
  ├── how to start a food truck business
  ├── food truck profit margin
  ├── food truck event pricing
  ├── food truck readiness audit (exists — expand)
  └─→ converts to: /profit-leak-snapshot.html

CLUSTER 3 — CATERING OPERATIONS  (pillar: /catering-consulting) ← NEW SERVICE PAGE
  ├── how to price catering jobs
  ├── catering profit margin
  ├── how to scale a catering business (blog post 5 — exists)
  └─→ converts to: /catering-profit.html ($67), /profit-leak-snapshot.html

CLUSTER 4 — SYSTEMS & LEADERSHIP  (pillar: /services.html — exists)
  ├── restaurant SOP templates
  ├── restaurant staff training program (/sops-training.html — exists)
  ├── what a fractional COO does (blog post 4 — exists)
  ├── restaurant consultant vs fractional COO
  ├── how much does a restaurant consultant cost
  └─→ converts to: /advisory.html, /sops-training.html
```

**Internal linking rules to apply:**

1. Every spoke links **up** to its pillar with descriptive anchor text.
2. Every pillar links **down** to all its spokes.
3. Every spoke links **across** to 1–2 sibling spokes in the same cluster.
4. Every content page links to **exactly one** service page, chosen for topical fit — not always the Snapshot (this is the current failure mode, T10).
5. Service pages link to their 2–3 best supporting articles (proves depth, keeps users on-site).
6. Anchor text describes the destination. Not "learn more" — "our [menu engineering service]".
7. Never more than 3 clicks from the homepage to any page.

### 4.5 Ten blog articles to write, in priority order

Prioritised by commercial intent × plausible competitiveness × fit with demonstrated expertise.

| # | Title | Target keyword | Why this one | Word count | CTA |
|---|---|---|---|---|---|
| 1 | How Much Does a Restaurant Consultant Cost? (2026 Pricing Breakdown) | how much does a restaurant consultant cost | Highest commercial intent on the list. Searchers are shopping *right now*. You already publish transparent pricing ($350 / $2,000/mo), which most competitors hide — publishing it wins the click and pre-qualifies the lead. | 1,500 | Book $350 Snapshot |
| 2 | How to Price Catering Jobs So You Actually Make Money | how to price catering jobs | Extremely high intent, directly matches your $67 course, and you have Module 2 material already built (`course/module-2.html`, `Full_Cost_Pricing_Calculator.xlsx`). | 2,000 | Catering Profit System |
| 3 | Why Your Restaurant Is Busy But Not Profitable | why is my restaurant not making money | The pain query. High volume, and it maps perfectly onto the Snapshot offer. Becomes Cluster 1's pillar. | 2,500 | Free ops audit → Snapshot |
| 4 | Food Truck Event Pricing: What to Charge for Festivals, Weddings & Corporate | food truck event pricing | Genuinely underserved query. Your FAQ already states food-truck operators "struggle with event pricing" (`index.html:660`) — write the answer. | 1,800 | Book $350 Snapshot |
| 5 | Restaurant Labor Cost: How to Get It Under 30% Without Cutting Service | how to reduce restaurant labor cost | Your strongest proof area — the homepage case study cites a 22% overtime reduction (`index.html`). Perennial operator pain. | 2,000 | Free ops audit |
| 6 | Fractional COO vs. Restaurant Consultant: Which Do You Actually Need? | restaurant consultant vs fractional COO | Comparison content converts. You sell both, so you can write it honestly — including when the answer is "neither yet." | 1,500 | Book advisory call |
| 7 | The Restaurant P&L, Line by Line (What to Look At First) | restaurant P&L explained | Foundational, links to everything, ages well. Strong internal-hub candidate. | 2,500 | Free playbook |
| 8 | Restaurant SOP Templates: What to Document First (and What to Skip) | restaurant SOP templates | Tool-seeking searchers convert well to email capture. Feeds `/sops-training.html`. | 1,800 | Gated SOP pack |
| 9 | Ghost Kitchen Profitability: The Numbers Nobody Shows You | ghost kitchen profitability | Lower competition, growing category. **Only write this if you have real ghost-kitchen experience [VERIFY]** — otherwise skip and remove the claim from your meta descriptions instead. | 2,000 | Book $350 Snapshot |
| 10 | What I Learned Running Multi-Unit Restaurants in Virginia | restaurant consultant Virginia (secondary) | E-E-A-T + local relevance in one asset. First-person experience is the thing AI-generated competitor content cannot replicate, and it's your genuine differentiator. **[VERIFY]** every specific brand, location, and figure before publishing. | 2,000 | Book $350 Snapshot |

**A note on the existing posts.** All five read as generic industry content — "Every restaurant owner dreams of a thriving business, bustling with happy customers and healthy profits" (`blog/blog_posts_data.json`) is the kind of opening that ranks for nothing in 2026. They are also anonymous and undated. Before writing new posts, consider rewriting these five with first-person operator specifics, real numbers, and a byline. Your competitive advantage is that you've actually done the work; the current posts hide that entirely.

Also: rename the blog URLs. `/blog/blog_post_1_profit_leaks_rewritten.html` is a filename, not a URL — "rewritten" in a public URL looks unfinished. Move to `/blog/restaurant-profit-leaks/` with 301 redirects via `netlify.toml`. Do this **before** the posts accumulate links, not after.

---

## 5. Local SEO strategy

### 5.1 Readiness assessment: not ready

| Signal | Status | Evidence |
|---|---|---|
| `LocalBusiness` schema | ✅ Present | `index.html:534-631` |
| `PostalAddress` in schema | ⚠️ City/region only | `index.html:547-552` — no `streetAddress` |
| `telephone` in schema | ✅ | `index.html:543` — `+15408079045` |
| Phone in crawlable HTML | ✅ Footer only | `540.807.9045` sitewide footer |
| NAP consistency | 🔴 **Conflict** | Schema says Louisa (`index.html:549`); `about.html:322` says Lake Monticello |
| Named service areas | 🔴 **None** | Zero occurrences of Richmond, Charlottesville, Norfolk, Hampton Roads, Northern Virginia, Roanoke, Fredericksburg anywhere in the repo |
| `areaServed` in schema | ⚠️ Country-level only | `index.html:554-557` — `{"@type": "Country", "name": "United States"}` |
| Location landing page | 🔴 None | — |
| Embedded map / directions | 🔴 None | — |
| Local business schema on service pages | 🔴 None | Only `index.html` |
| GBP reviews surfaced on site | 🔴 None | One anonymous testimonial (`index.html:825`) |

**The core problem:** the site says "Virginia" constantly, but it's all footer boilerplate — *"Virginia-based restaurant operations consultant. Serving operators nationwide."* repeated across 41 pages. Repeating the same sentence in a footer 41 times generates zero local relevance. Google needs to see specific markets in body content, headings, and structured data.

**T40 — NAP conflict must be resolved first. High.** **[VERIFY]**
`index.html:549` declares `addressLocality: "Louisa"`. `about.html:322` says *"Home base is Lake Monticello, VA."* These are different places (Lake Monticello is in Fluvanna County; Louisa is in Louisa County, adjacent). Both may be defensible — home base vs. mailing address — but Google resolves local entities by NAP consistency, and an internal contradiction on your own site is the worst possible starting point for a Google Business Profile. **Pick one, use it everywhere, and match it exactly to whatever you register with GBP.** This must be settled before any other local work.

### 5.2 Schema recommendations

**Keep `["LocalBusiness", "ProfessionalService"]`** on `index.html` — the dual type is correct for a consultancy with a physical base.

| Schema | Where | Status | Action |
|---|---|---|---|
| `LocalBusiness` / `ProfessionalService` | `/` | ✅ Exists | Add `areaServed` array of named Virginia localities; add `geo`; add `hasMap` if you have a GBP listing |
| `Person` | `/` | ✅ Exists | Add `alumniOf`, `hasCredential`, `description` — **only if verifiable [VERIFY]** |
| `Service` (×6) | `/services.html` | ✅ Exists | Mirror onto each service page (T15); add `areaServed` |
| `FAQPage` | `/` | ✅ Exists | Add to each service page with page-specific questions |
| `BreadcrumbList` | Everywhere | 🔴 Missing | Add to blog posts + service pages (T13) |
| `BlogPosting` | 6 article pages | 🔴 Missing | Add with real dates and author `@id` (T12) |
| `WebSite` | `/` | 🔴 Missing | Add to `@graph`; **no `SearchAction`** — the site has no search |
| `ContactPage` | `/contact.html` | 🔴 Missing | Add alongside the T33 expansion |
| `Review` / `AggregateRating` | — | ⚪ Correctly absent | **Do not add** until you have named, permissioned testimonials (T16) |
| `Course` | `/catering-profit.html` | 🔴 Missing | Valid and useful — `provider`, `hasCourseInstance`, `offers` at $67 **[VERIFY]** current price/availability |

**Required fields for the `areaServed` upgrade:**
```json
"areaServed": [
  {"@type": "State", "name": "Virginia"},
  {"@type": "City", "name": "Richmond", "containedInPlace": {"@type": "State", "name": "Virginia"}},
  {"@type": "City", "name": "Charlottesville", "containedInPlace": {"@type": "State", "name": "Virginia"}}
]
```
Only list markets you genuinely serve. **[VERIFY]**

### 5.3 Location pages — how to do this without building doorway pages

The temptation is to spin up "Restaurant Consultant in Richmond", "…Charlottesville", "…Norfolk" from one template. **Don't.** Google's doorway-page guidelines target exactly that, and for a solo consultant it's both a penalty risk and a credibility risk — a Richmond operator reads a page that could be about anywhere and bounces.

**Recommended structure — one strong page, then earn the rest:**

1. **Build `/virginia-restaurant-consulting` first.** A single, substantial (1,200+ word) page covering: the Virginia markets you actually serve, real regulatory context (Virginia ABC licensing, VDH food-safety requirements, local health-department differences by county), what in-person vs. remote engagement looks like, and any Virginia work you can describe. **[VERIFY]** every regulatory claim against current Virginia ABC and VDH sources before publishing — regulations change and wrong details destroy credibility with the exact audience you're targeting.

2. **Only add a city page once you have something real to say about that city** — a named client (with permission), a local partnership, a market-specific insight. One page about Richmond written by someone who knows Richmond beats six templated pages.

3. **Add a "Service Areas" section to `contact.html`** during the T33 expansion, listing named markets in body text, with a clear "remote nationwide, in-person across Central Virginia" statement.

4. **Use the Virginia Neighbors directory as genuine local proof** (`virginia-neighbors.html`). You already have a Virginia business directory. Fix its rendering (T36) and it becomes an authentic local-relevance asset — but reconsider whether it deserves 39 internal links while your service pages have 1.

### 5.4 Actions outside this repository **[EXTERNAL]**

None of these can be done in code. All require business accounts and verification.

**Google Business Profile** — the highest-leverage local action available.
- Create/claim the profile. Category: "Business consultant" or "Marketing consultant"; secondary as applicable.
- As a service-area business, **hide the street address** and define a service-area radius. Address must match the NAP you settle in T40.
- Complete every field: services (matching your five service pages), hours, description, booking link (your Stripe booking URL).
- Post weekly. GBP posts are one of the few local signals you control directly.
- **[VERIFY]** eligibility — GBP requires a real business presence and in-person customer contact. A remote-only consultancy may not qualify. Check current guidelines before investing here.

**Citations** — build only after NAP is settled. Inconsistent citations are worse than none.
- Priority: Apple Business Connect, Bing Places, LinkedIn Company Page, Facebook Business Page (the profile already exists — `index.html` `sameAs`).
- Industry-relevant: Virginia Restaurant Lodging & Travel Association, local chambers of commerce, Clutch, UpCity.
- Skip paid bulk-citation services. For a service-area consultancy the ROI is poor and the data quality is unreliable.

**Reviews** — your single biggest credibility gap.
- One anonymous testimonial (`index.html:825`) is all the social proof on the entire site. For a $2,000/mo advisory offer, that is not enough.
- Ask past clients for Google reviews and for permission to use named testimonials on-site. Named + role + business type ("Maria S., Owner, 2-unit fast casual, Richmond") is dramatically stronger than "Multi-Unit Franchisee, Virginia."
- **Never** buy, incentivise, or write reviews. Beyond being against Google's policies, in your industry it's the kind of thing that gets noticed.
- Once you have 3+ named testimonials with written permission, `Review` schema becomes legitimately available (T16).

**Local backlinks & partnerships**
- Virginia Restaurant, Lodging & Travel Association — membership, speaking, contributed articles
- Local chambers (Charlottesville, Richmond, Louisa County) — member directory listings are genuine local citations
- Restaurant supply distributors, POS resellers, food-service accountants, hospitality staffing agencies — natural referral partners who also link
- Community college / SBDC hospitality programs — guest lectures earn `.edu` links
- Virginia food-industry podcasts and local business press
- **[EXTERNAL]** All require outreach. None can be done in this repo.

---

## 6. Traffic growth plan — 90 days

Measurement targets below are **directional planning figures, not forecasts.** No baseline data was available to this audit, so no honest projection is possible. Establish a baseline in weeks 1–2, then set real targets from it.

### Weeks 1–2 — Technical foundation & metadata

| # | Action | Impact | Effort | Dependencies | Success measured by |
|---|---|---|---|---|---|
| 1.1 | Verify domain in Google Search Console; submit sitemap | **Critical** — nothing is measurable without it | 1h | **[EXTERNAL]** GSC account | Property verified, sitemap "Success" |
| 1.2 | Add 6 missing URLs + `<lastmod>` to `sitemap.xml` (T1, T4) | High | 1h | — | All 25 URLs discovered in GSC |
| 1.3 | `noindex` on `zohoverify/` and `404.html`; strip 404 canonical/OG (T2, T3) | Medium | 30m | — | Pages absent from GSC coverage |
| 1.4 | Compress & convert all images to WebP; rename to slugs (T19, T39) | **Critical** | 4h | Image tooling | Total page weight <500 KB on every page |
| 1.5 | Replace `hero.png` with optimised WebP + `<img>` + preload (T18) | **Critical** | 2h | 1.4 | LCP <2.5s mobile (PageSpeed Insights) |
| 1.6 | Remove `@import` from `style.css:10`; add preconnect+link sitewide (T20) | High | 2h | — | No render-blocking font chain in Lighthouse |
| 1.7 | Add `width`/`height`/`loading="lazy"` to all 11 images (T21, T22) | High | 1h | 1.4 | CLS <0.1 |
| 1.8 | Create 1200×630 OG image; repoint all `og:image`/`twitter:image` (T27) | High | 2h | Design | Facebook Sharing Debugger + Twitter Card Validator pass |
| 1.9 | Rewrite 6 over-length descriptions + 12 weak titles per §3 (T28, T29) | High | 3h | — | Zero GSC truncation warnings; CTR baseline set |
| 1.10 | Self-host or license-verify the 7 Unsplash heroes (T23) | High | 3h | **[VERIFY]** licensing | No third-party image requests |
| 1.11 | Remove root course ZIP; gate `/course/downloads/` (T6) | High (business) | 2h | **[VERIFY]** with owner | Direct URL returns 403 |
| 1.12 | Fix or remove the Crisp widget in `exit-intent-popup.js:18-25` (T41) | High | 1h | **[VERIFY]** Website ID | Widget either works or is gone from all 17 pages |
| 1.13 | Correct `privacy.html:132` — remove the Calendly claim, disclose Crisp if kept (T41) | Medium | 30m | 1.12 | Policy matches tools actually in use |

**Week 1–2 checkpoint:** Lighthouse mobile Performance ≥85 on `/`, `/services.html`, `/advisory.html`. GSC reporting. This is the base everything else builds on.

### Weeks 3–6 — Architecture, service pages & conversion

| # | Action | Impact | Effort | Dependencies | Success measured by |
|---|---|---|---|---|---|
| 2.1 | Add Services dropdown to nav + Services footer column (T7) | **Critical** | 4h | — | 4 service pages go from 1 → ~40 inbound links |
| 2.2 | Standardise `index.html` nav to match sitewide (T8) | High | 1h | 2.1 | Consistent nav on all 41 pages |
| 2.3 | Add contextual links from 5 blog posts → matching service pages (T10) | High | 3h | — | +10–15 contextual internal links |
| 2.4 | Add `BlogPosting` schema + visible bylines/dates to 6 articles (T12) | High | 4h | **[VERIFY]** real dates | Rich Results Test passes ×6 |
| 2.5 | Add `BreadcrumbList` + visible breadcrumbs (T9, T13) | Medium | 3h | — | Breadcrumbs in SERP |
| 2.6 | Expand `contact.html` to 400–600 words + `ContactPage` schema (T33) | High | 3h | Copy | Contact page organic sessions ↑ |
| 2.7 | Build `/food-truck-consulting` service page | **High** | 6h | Copy | Page indexed, first impressions |
| 2.8 | Build `/catering-consulting` service page | **High** | 6h | Copy | Page indexed, first impressions |
| 2.9 | Add page-specific `FAQPage` schema to 5 service pages | Medium | 3h | Copy | FAQ rich results |
| 2.10 | Differentiate the 4 templated service pages (T35) | Medium | 6h | Copy | Reduced template similarity |
| 2.11 | Decide `profit-leak-calculator.html`: promote or delete (T34) | Medium | 2–8h | Decision | If promoted: indexed + linked |
| 2.12 | Collect 3–5 named testimonials with written permission | **High** | **[EXTERNAL]** | Client outreach | Testimonials live; `Review` schema becomes valid |
| 2.13 | Migrate blog URLs to clean slugs + 301s in `netlify.toml` | Medium | 3h | Do before links accumulate | 301s verified, no 404s in GSC |

**Week 3–6 checkpoint:** All service pages properly linked and indexed. Two new service pages live. Named testimonials on-site.

### Weeks 7–12 — Content, local authority & distribution

| # | Action | Impact | Effort | Dependencies | Success measured by |
|---|---|---|---|---|---|
| 3.1 | Publish articles 1–5 from §4.5 (one per week) | **High** | 6h each | Copy | Indexed within 7d; impressions by week 12 |
| 3.2 | Build `/virginia-restaurant-consulting` (§5.3) | **High** | 8h | **[VERIFY]** VA regs | Impressions for "restaurant consultant Virginia" |
| 3.3 | Add named `areaServed` to `LocalBusiness` schema | Medium | 1h | 3.2, T40 resolved | Rich Results Test passes |
| 3.4 | Resolve NAP conflict sitewide (T40) | **High** | 2h | **[VERIFY]** with owner | One address everywhere |
| 3.5 | Create & fully populate Google Business Profile | **High** | 3h | **[EXTERNAL]**, 3.4 | Profile verified & live |
| 3.6 | Build citations: Apple, Bing, LinkedIn, chambers | Medium | 4h | **[EXTERNAL]**, 3.4 | 8–10 consistent citations |
| 3.7 | Request Google reviews from past clients | **High** | **[EXTERNAL]** | Client relationships | 5+ genuine reviews |
| 3.8 | Local partnership outreach: VRLTA, chambers, SBDC, suppliers | High | Ongoing | **[EXTERNAL]** | 3–5 referring domains |
| 3.9 | Publish articles 6–8 | High | 6h each | Copy | Growing impressions |
| 3.10 | Repurpose each article to LinkedIn + newsletter | Medium | 1h each | — | Referral traffic; list growth |
| 3.11 | Extract shared inline CSS into `style.css` (T24) | Medium | 8h | Regression testing | Repeat-visit load time ↓ |
| 3.12 | Server-render or statically supplement `virginia-neighbors.html` (T36) | Medium | 6h | Dev | Directory content in initial HTML |

**Day 90 checkpoint:** 8+ new indexed pages, GBP live with reviews, 3–5 new referring domains, named testimonials, all technical items closed. Compare against the week-2 baseline — not against a number invented today.

---

## 7. Analytics and measurement

### 7.1 What exists in the repo

| Item | Status | Evidence |
|---|---|---|
| Google Analytics 4 | ✅ Present | `analytics.js:5,12` — `G-778929FT8G` |
| GA4 loaded sitewide | ✅ 32 pages | All content pages; absent on `/course/*` (intentional) |
| Custom conversion events | ✅ Good | `analytics.js:26` `booking_click`, `:36` `snapshot_cta_click`, `:46` `advisory_cta_click`, `:57` `form_submit` |
| Google Tag Manager | 🔴 Absent | No GTM container anywhere |
| Search Console verification | 🔴 **Absent** | No `google-site-verification` meta or file in repo |
| Bing Webmaster verification | 🔴 Absent | No `msvalidate.01` |
| Meta/Facebook Pixel | 🔴 Absent | No `fbq(` calls |
| LinkedIn Insight Tag | 🔴 Absent | — |
| Crisp Chat | ⚠️ Loads on 17 pages, likely broken | `exit-intent-popup.js:18-25` — see T41 |
| Exit-intent popup | ⚠️ 17 pages, untracked | `exit-intent-popup.js` — absent from `/` and `/contact.html` (T42) |
| Call tracking | 🔴 Absent | `tel:540-807-9045` in footer is untracked |
| Stripe purchase → GA4 revenue | ⚠️ Partial | `booking_click` fires on click; `netlify/functions/stripe-webhook.js` handles completion but sends no GA4 event |
| Zoho verification | ✅ Present | `zohoverify/verifyforzoho.html` (email, not search) |

**The `analytics.js` implementation is better than typical.** Event delegation on `document` catches every CTA across all 41 pages without per-page instrumentation, and it correctly distinguishes booking clicks from softer CTA clicks. Whoever wrote it knew what they were doing.

### 7.2 What's missing

**A1 — No Search Console verification. Critical. [EXTERNAL]**
Without GSC there is no impression data, no click data, no average position, no index-coverage reporting, no way to submit a sitemap, and no way to measure whether any recommendation in this document worked. **This is the single most important item in the entire audit.** Verify via DNS TXT record (survives redeploys) or by adding a `google-site-verification` meta tag to `index.html`.

**A2 — `booking_click` fires on click, not on purchase. High.**
`analytics.js:26` fires when a user clicks a `book.stripe.com` link — that's an *intent* signal, not a conversion. Actual bookings complete on Stripe's domain. `netlify/functions/stripe-webhook.js` already receives completion webhooks; extend it to send a GA4 Measurement Protocol event with real revenue. Until then, treat `booking_click` as top-of-funnel and expect it to overstate conversions.

**A3 — No GA4 Key Events configured. High. [EXTERNAL]**
The events fire but nothing in the repo indicates they've been marked as Key Events (conversions) in the GA4 interface. Without that they don't appear in conversion reports or attribute to channels.

**A4 — `form_submit` doesn't distinguish form types. Medium.**
`analytics.js:57` fires one generic `form_submit` for every form on the site — the contact form (`contact.html:123`), the newsletter signup (`blog.html:286`), the playbook gate (`playbook.html:112`), and all four auth forms. A newsletter signup and a $350 consultation request are not the same event. Split by form ID.

**A5 — No `page_view` on the client-side directory. Medium.**
`virginia-neighbors.html` filters and searches client-side with no interaction events, so all engagement is invisible.

**A6 — Phone calls are untracked. Medium. [EXTERNAL]**
The footer `tel:` link on 41 pages produces zero measurable data. Minimum: add a click event on `tel:` links. Better: a call-tracking number (CallRail or similar) — but a tracked number **must** match your GBP number or you break NAP consistency (§5.1). Use GBP's own call-tracking feature instead, which is designed for this.

**A7 — No Bing Webmaster Tools. Low. [EXTERNAL]**
Bing drives meaningful B2B traffic and increasingly feeds AI search surfaces. Verification takes five minutes and imports directly from GSC.

**A8 — Consider GTM. Low.**
Not urgent for a static site — direct gtag is faster and simpler. Revisit only if you add Meta/LinkedIn pixels.

**A9 — The exit-intent popup is completely untracked. Medium.**
`exit-intent-popup.js` runs on 17 pages, contains built-in A/B logic that randomly emphasises one of two lead magnets, and captures leads via `formsubmit.co` (`:208`) — with **no GA4 events at all**. The generic `form_submit` handler in `analytics.js:57` will fire on submission, but there is no impression event, no dismissal event, and no variant label, so the A/B test cannot be read. You are running an experiment you cannot measure.
*Fix:* Fire `exit_intent_shown` (with the variant as a parameter), `exit_intent_dismissed`, and `exit_intent_submitted`. Without the variant parameter the A/B test is decorative.

### 7.3 Metrics to monitor

**Acquisition (Search Console)**
- Impressions — total and by page; the leading indicator of index growth
- Clicks — total and by page
- CTR by page — the direct measure of whether the §3 metadata rewrites worked
- Average position — by query cluster, not sitewide (sitewide average is noise)
- Indexed pages — Coverage report; watch for the six blog posts appearing after 1.2
- Top queries — is the site attracting *operators*, or students and job-seekers?

**Engagement (GA4)**
- Organic sessions, by landing page
- Engagement rate on service pages (the four orphans are the ones to watch after 2.1)
- Scroll depth on long pages (`playbook.html`, `audit.html`)
- Pages per session — measures whether the internal-linking fixes are working

**Conversion (GA4 + Stripe + inbox)**
- `snapshot_cta_click` → Snapshot page → `booking_click` → completed purchase (full funnel, with drop-off at each step)
- Contact form submissions, segmented from newsletter signups (A4)
- Playbook downloads (email captures)
- Catering course purchases
- Phone clicks (once A6 is done)
- **Organic conversion rate** — organic sessions ÷ qualified leads. The number that actually matters.
- **Cost per qualified lead** vs. paid channels

**Local (Google Business Profile Insights) [EXTERNAL]**
- Profile views, search vs. discovery
- Direction requests, calls, website clicks from GBP
- Review count and average rating

**Quality — the ones that separate qualified from vanity traffic**
- % of leads that are actual food-service operators (manual tagging in your CRM)
- Snapshot bookings per 1,000 organic sessions
- Lead-to-client conversion rate by traffic source

### 7.4 Monthly report structure

One page. If it takes longer than 20 minutes to produce, it won't get produced.

```
TRECOLEMAN.COM — ORGANIC PERFORMANCE — [Month]

1. HEADLINE
   Organic sessions:     ___  (MoM __%)  |  Qualified leads:  ___
   Snapshot bookings:    ___             |  Revenue attributed to organic: $___

2. SEARCH VISIBILITY (Search Console, 28-day)
   Impressions ___ | Clicks ___ | CTR __% | Avg position ___
   Indexed pages: ___ / ___ submitted
   Top 5 gaining queries        Top 5 declining queries

3. PAGE PERFORMANCE
   Top 5 landing pages by organic sessions
   Top 5 by conversion rate  ← the more useful list
   Pages with impressions but CTR <2%  → metadata rewrite candidates
   Pages with 0 impressions            → indexing or relevance problem

4. CONVERSION FUNNEL
   Organic session → service page → snapshot CTA → booking click → purchase
   Drop-off at each step, vs. last month

5. CONTENT SHIPPED
   Published this month: ___
   Performance of last month's posts (impressions, clicks, position)

6. LOCAL [EXTERNAL]
   GBP views ___ | Calls ___ | Website clicks ___ | New reviews ___

7. TECHNICAL HEALTH
   Core Web Vitals: LCP ___ | CLS ___ | INP ___  (mobile, field data)
   GSC errors: ___   Broken links: ___

8. NEXT MONTH — top 3 priorities
```

Review weekly for the first month after the Weeks 1–2 fixes (to catch anything that broke), then settle into monthly.

---

## 8. Implementation backlog

### P0 — Urgent: indexing, measurement, and revenue protection

- [ ] **Verify Search Console and submit the sitemap** — nothing else is measurable without it **[EXTERNAL]**
- [ ] Add the 5 blog posts + `unreasonably-optimistic.html` to `sitemap.xml`; add `<lastmod>` to all entries *(T1, T4)*
- [ ] Add `noindex` to `zohoverify/verifyforzoho.html` — do not delete the file *(T2)*
- [ ] Remove canonical + OG tags from `404.html`; add `noindex` *(T3)*
- [ ] Remove the course ZIP from the repo root; gate `/course/downloads/` *(T6)* **[VERIFY with owner]**
- [ ] Optimise all images to WebP — 9.6 MB → ~150 KB on `services.html` alone *(T19)*
- [ ] Replace `hero.png` (2 MB) with an optimised, preloaded LCP image *(T18)*
- [ ] Remove `@import` from `style.css:10`; use preconnect + link *(T20)*
- [ ] Add `width`/`height`/`loading="lazy"` to all 11 images *(T21, T22)*
- [ ] Create a 1200×630 OG image; repoint every `og:image`/`twitter:image` *(T27)*
- [ ] **Resolve the Louisa vs. Lake Monticello NAP conflict** *(T40)* **[VERIFY]**

### P1 — High-impact: architecture, metadata, and conversion

- [ ] Add a Services dropdown to the nav + a Services footer column — takes 4 pages from 1 to ~40 inbound links *(T7)*
- [ ] Standardise `index.html`'s 5-link nav to match the sitewide 14-link nav *(T8)*
- [ ] Add contextual links from each blog post to its matching service page *(T10)*
- [ ] Rewrite the 6 over-length meta descriptions and 12 weak titles per §3 *(T28, T29)*
- [ ] Add `BlogPosting` schema + visible bylines and dates to all 6 articles *(T12)* **[VERIFY dates]**
- [ ] Add `BreadcrumbList` schema + visible breadcrumbs *(T9, T13)*
- [ ] Mirror `Service` schema onto each service page *(T15)*
- [ ] Expand `contact.html` from ~60 to 400–600 unique words; add `ContactPage` schema *(T33)*
- [ ] Self-host and license-verify the 7 Unsplash hero images *(T23)* **[VERIFY]**
- [ ] Build `/food-truck-consulting` — claimed audience, no page *(§4.3)*
- [ ] Build `/catering-consulting` — claimed audience, no page *(§4.3)*
- [ ] **Either build a ghost-kitchen page or remove the claim from `advisory.html` and `audit.html` meta descriptions** *(§4.1)* **[VERIFY]**
- [ ] Collect 3–5 named testimonials with written permission *(T16)* **[EXTERNAL]**
- [ ] Configure GA4 Key Events; split `form_submit` by form ID *(A3, A4)* **[EXTERNAL]**
- [ ] Send a GA4 event with revenue from `stripe-webhook.js` on completed purchase *(A2)*
- [ ] **Resolve the Crisp Chat widget in `exit-intent-popup.js:18-25`** — fix the malformed Website ID or remove it; it currently loads on 17 pages and likely fails *(T41)* **[VERIFY]**
- [ ] Correct `privacy.html:132` — it documents a Calendly widget that doesn't exist and omits Crisp, which does *(T41)*
- [ ] Audit every quantitative claim on the site *(see verification list below)* **[VERIFY]**

### P2 — Growth and authority

- [ ] Publish articles 1–5 from §4.5, one per week
- [ ] Build `/virginia-restaurant-consulting` *(§5.3)* **[VERIFY Virginia regulatory content]**
- [ ] Add named `areaServed` to `LocalBusiness` schema *(§5.2)*
- [ ] Create and fully populate a Google Business Profile *(§5.4)* **[EXTERNAL]**
- [ ] Build 8–10 consistent citations *(§5.4)* **[EXTERNAL]**
- [ ] Request Google reviews from past clients *(§5.4)* **[EXTERNAL]**
- [ ] Local partnership outreach: VRLTA, chambers, SBDC, suppliers *(§5.4)* **[EXTERNAL]**
- [ ] Migrate blog URLs to clean slugs with 301 redirects *(§4.5)*
- [ ] Add `FAQPage` schema to each service page *(§5.2)*
- [ ] Differentiate the 4 near-duplicate service page templates *(T35)*
- [ ] Decide `profit-leak-calculator.html`: promote as a lead magnet, or delete *(T34)*
- [ ] Expand `audit.html` and `food-truck-audit.html` with 400–600 words of real content *(T37)*
- [ ] Publish articles 6–8; repurpose each to LinkedIn and the newsletter
- [ ] Add exit-intent tracking events with A/B variant labels *(A9)*
- [ ] Add `exit-intent-popup.js` to `index.html` *(T42)*
- [ ] Verify Bing Webmaster Tools *(A7)* **[EXTERNAL]**
- [ ] Add call tracking — via GBP, not a separate number *(A6)* **[EXTERNAL]**

### P3 — Longer-term

- [ ] Extract shared inline CSS into `style.css` *(T24)* — 500 lines on `index.html` alone
- [ ] Server-render or statically supplement `virginia-neighbors.html` *(T36)*
- [ ] Rewrite the 5 existing blog posts with first-person operator specifics *(§4.5)*
- [ ] Replace `<a href="#" onclick="return false">` dropdowns with `<button aria-expanded>` *(T11)*
- [ ] Add `<main>` landmarks and skip-links to all pages *(T32)*
- [ ] Add `:focus-visible` styles and `prefers-reduced-motion` support *(§2.7)*
- [ ] Change footer `<h4>` to `<h2>` to fix hierarchy skips *(T30)*
- [ ] Move emoji out of `<h1>` on `audit.html` and `food-truck-audit.html` *(T31)*
- [ ] Rename image files to descriptive slugs *(T39)*
- [ ] Remove the 3 unused images — 4.4 MB *(T25)* **[VERIFY unused elsewhere]**
- [ ] Add `Course` schema to `catering-profit.html` *(§5.2)* **[VERIFY price/availability]**
- [ ] Remove `CNAME` if GitHub Pages is retired **[VERIFY]**
- [ ] Consider consolidating the two nav-editing GitHub Actions workflows — one exists to repair the other
- [ ] Set `{passive: true}` on the scroll listener in `header-scroll.js`
- [ ] Per-page OG images for top service pages
- [ ] Add `hasCredential` / `alumniOf` to `Person` schema **[VERIFY]**

---

## Claims requiring verification before publishing

Every item below is currently published on the live site. None can be verified from the repository. Under FTC endorsement and advertising-substantiation rules, performance claims need documentation you can produce on request — and in a market where your buyers have been pitched by many consultants, an unsupported number is a credibility liability as much as a legal one.

| Claim | Where | What's needed |
|---|---|---|
| "10+ years managing multi-unit restaurant operations" | `about.html:341`, `index.html`, `blog.html` | Employment history |
| "300+ employees led across multiple locations" | `about.html:341`, `index.html` | Documentation |
| "$300K+ in revenue waste eliminated for clients" | `about.html:341` | Client documentation |
| "National Hospitality Brands" | `index.html` | Which brands? Naming them (with permission) is far stronger than the vague phrase |
| "Cut admin time 40-60%" | `ai-integration.html` meta + body | Measured client results |
| "New hires productive 40% faster with AI" | `ai-integration.html:417` | Measured results |
| "50% faster onboarding — 2-3 weeks instead of 4-6" | `sops-training.html:318,419` | Measured results |
| "12-18% increase in average check size within 90 days" | `menu-engineering.html:420` | Measured results |
| "15-25% increase in traffic during slow periods" | `lsm.html:420` | Measured results |
| "Typical ROI: 8-12x within the first quarter" | `menu-engineering.html:429` | Substantiation — ROI claims attract the most scrutiny |
| "Typical ROI: 4-6x within the first 90 days" | `sops-training.html:428` | Substantiation |
| "Most operators find $5,000–$20,000 in annual leaks in a single session" | `index.html` FAQ + schema | Sample size — this is in your FAQPage schema, so it's eligible for rich results |
| "Losing $10K–$50K a year to profit leaks" | `index.html` hero, `virginia-neighbors.html` | Industry source citation, or reframe as an estimate |
| Three case studies: "Overtime dropped 22% / ~$18,000 annual savings"; "Average event margin up 11 points"; "Onboarding cut from 3 weeks to 8 days" | `index.html` "Results from the Field" | Client permission for anonymised use. These are your strongest assets — worth documenting properly |
| "Unlimited support" | `advisory.html` meta description | An absolute claim on a $2,000/mo service. Define the boundaries or soften the wording |
| "— Multi-Unit Franchisee, Virginia" | `index.html:825` | Permission to attribute by name — anonymous testimonials convert poorly and block valid `Review` schema |
| "Pre-order now for $67" | `catering-profit.html` | Is this still a pre-order? Is $67 current? |
| Address: Louisa, VA vs. Lake Monticello, VA | `index.html:549` vs. `about.html:322` | **Must be resolved before any local SEO work** |
| Phone `540.807.9045` | Footer sitewide, schema `index.html:543` | Confirm this is the number that will go on GBP |
| Unsplash photo licensing (7 hot-linked images) | 7 files, §2.4 T23 | Commercial-use rights |
| Crisp Website ID `…1207df3715lf` | `exit-intent-popup.js:20` | `l` is not a hex character; UUIDs are hex. Confirm in the Crisp dashboard whether the widget actually initialises on the 17 pages that load it |
| "We also embed a scheduling widget from Calendly" | `privacy.html:132` | No Calendly embed exists in the repository. Either the policy is inaccurate, or an integration was removed and the disclosure wasn't |

**A note on tone, not compliance:** these numbers are specific and plausible — they read like real operator results, not marketing invention. That's exactly why they're worth substantiating properly. A consultant who can produce the documentation behind "overtime dropped 22%" is in a completely different credibility bracket from one who can't, and that difference shows up in close rates long before it shows up in rankings.

---

## Appendix — Audit coverage

**Files reviewed:** 43 HTML files (26 indexable, 17 `noindex`/utility), `style.css` (1,050+ lines), `analytics.js`, `header-scroll.js`, `exit-intent-popup.js`, `course/auth.js`, `course/config.js`, `robots.txt`, `sitemap.xml`, `netlify.toml`, `_headers`, `package.json`, `CNAME`, `.gitattributes`, 2 GitHub Actions workflows, 8 Netlify functions, 16 root images (measured for size and dimensions), `blog/blog_posts_data.json`, `images/README.md`, `NAV-FOOTER-STANDARDIZATION-GUIDE.md`, `COURSE-SYSTEM-SETUP.md`.

**Analyses performed:** metadata extraction with exact character counts across all 43 pages; heading-hierarchy census; internal link-graph construction with inbound counts per target; image dimension and byte-size measurement; JSON-LD extraction and validation by inspection; third-party asset inventory; word-count analysis; near-duplicate template comparison; orphan-page detection; nav consistency comparison across all pages.

**Not performed** (requires access outside this repository): live crawl, rendered-DOM inspection, Core Web Vitals field data, Search Console data, Analytics data, keyword volume and difficulty research, backlink analysis, SERP competitor analysis, mobile-device testing, screen-reader testing, HTTP header and status-code verification.

*This audit reports only what is observable in the repository. Where data was unavailable, that is stated rather than estimated.*
