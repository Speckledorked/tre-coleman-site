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
