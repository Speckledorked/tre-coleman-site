# tools/

Reproducible generators for the site's structural markup. Each script is
idempotent — safe to re-run — and self-documenting; read the docstring at the
top of any of them for what it does and why.

These replace the two GitHub Actions workflows that used to rewrite the nav
with regular expressions (`update-navigation.yml` and its repair companion
`fix-audit-navigation.yml`, which existed only to fix the damage the first one
caused). Editing 40 hand-written HTML files by regex is how the site ended up
with six different nav variants; running one generator that owns the whole
block is how it stays at one.

## When you change the nav or footer

Edit the block at the top of the script, then re-run it:

```bash
python3 tools/standardise_nav.py       # nav on all pages
python3 tools/standardise_footer.py    # footer Services + Quick Links columns
```

## When you add or rename a page

1. Add it to `PAGES` in `tools/build_sitemap.py`
2. Add it to `tools/standardise_nav.py` / `standardise_footer.py` if it should
   be linked sitewide
3. Commit, **then** run `python3 tools/build_sitemap.py`

The sitemap step comes last because `<lastmod>` is read from git history. A
file with no commits yet has no honest date, so the generator omits it and
tells you which ones it skipped rather than inventing one.

## Scripts

| Script | Purpose |
|---|---|
| `build_sitemap.py` | Regenerates `sitemap.xml` with git-derived `<lastmod>` |
| `standardise_nav.py` | Writes one canonical `<nav id="mainNav">` everywhere |
| `standardise_footer.py` | Writes the footer Services and Quick Links columns |
| `fix_font_loading.py` | Keeps Google Fonts on `<link>` rather than a CSS `@import` |
| `optimise_images.py` | Source PNG/JPG → right-sized WebP in `images/` |
| `update_image_refs.py` | Points markup at the WebP files with width/height/loading |
| `build_og_image.py` | Regenerates the 1200×630 social card |
| `fix_og_images.py` | Repoints `og:image` / `twitter:image` at that card |
| `add_structured_data.py` | BlogPosting, BreadcrumbList, WebSite, `areaServed` |
| `rewrite_metadata.py` | Titles and meta descriptions (see `SEO_AUDIT.md` §3) |
| `fix_accessibility.py` | `<main>`, skip links, footer heading levels, nav ARIA |
| `build_new_pages.py` | Generates the service and location pages |
| `migrate_blog_urls.py` | One-shot: renamed blog files to slugs, added 301s |

## Requirements

Python 3 and Pillow (`pip install Pillow`) for the image scripts. Everything
else uses only the standard library.

## Checking the site

```bash
python3 tools/check_site.py           # everything
python3 tools/check_site.py --quiet   # errors only
python3 tools/check_site.py --list    # what each check does
```

Exit code 1 on any error, 0 otherwise. Warnings never fail the run. Zero
dependencies — standard library only.

It also runs in CI on every push and pull request via
`.github/workflows/check-site.yml`, which additionally verifies that
`sitemap.xml` matches what `build_sitemap.py` would generate.

### Run it before every commit

Optional, but this is the check that would have caught the Airtable token
before it reached a public repository:

```bash
cat > .git/hooks/pre-commit <<'HOOK'
#!/bin/sh
python3 tools/check_site.py --quiet || {
  echo "Site checks failed. Fix, or commit with --no-verify to override."
  exit 1
}
HOOK
chmod +x .git/hooks/pre-commit
```

### What it checks, and why each one is there

Every check corresponds to a defect this site has actually had.

| Check | Catches |
|---|---|
| `secrets` | Live Stripe/Resend/Airtable/AWS keys, private keys, and Supabase **service-role** JWTs (it decodes the token to read the role claim) |
| `gitignore` | `.env` not ignored — the absence of a `.gitignore` is how a real Airtable token reached this repo's history |
| `json-ld` | Schema that does not parse, or describes the wrong page. Also blocks `Review`/`AggregateRating` without a named author |
| `metadata` | Missing or duplicated title/description/canonical, multiple `<h1>`, noindex pages that also declare a canonical |
| `structure` | Unbalanced tags, missing `lang` |
| `links` | Internal links to files that do not exist |
| `images` | Missing files, and `<img>` without `width`/`height` (layout shift) or `alt` |
| `sitemap` | Indexable pages missing from it, noindex pages wrongly listed, invalid XML |
| `robots` | Missing `Sitemap:` directive, accidental `Disallow: /` |
| `stale` | Hot-linked Unsplash images, the removed Crisp loader, old blog filenames, the stale `$750` price, pre-WebP image paths, a reintroduced font `@import` |
| `js` | JavaScript that does not parse — the duplicate `const` that left the exit-intent popup dead for months |

### Known limitations

It is a static checker. It cannot see anything that only exists at runtime:
rendered output, actual Core Web Vitals, whether a redirect resolves, whether
Supabase RLS is enabled, or whether an API key is valid. For those, see
`SEO_AUDIT.md` §7 and the external tools listed there.
