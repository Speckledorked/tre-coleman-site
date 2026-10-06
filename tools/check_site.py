#!/usr/bin/env python3
"""
Pre-flight checks for the site. Zero dependencies — standard library only.

    python3 tools/check_site.py            # all checks
    python3 tools/check_site.py --quiet    # errors only
    python3 tools/check_site.py --list     # what each check does

Exit code 0 if no errors, 1 if any. Warnings never fail the run.

Every check here corresponds to a real defect this site has actually had:
a secret committed to a public repo, blog posts missing from the sitemap,
an article inheriting another article's schema, a 404 page declaring itself
canonical, images with no dimensions, a stale $750 price in a dead code path.
"""

import argparse
import glob
import json
import os
import re
import sys
import urllib.parse
import xml.dom.minidom

SITE = "https://trecoleman.com"

errors = []
warnings = []


def err(where, msg):
    errors.append((where, msg))


def warn(where, msg):
    warnings.append((where, msg))


def html_files():
    return [p for p in sorted(glob.glob("**/*.html", recursive=True))
            if "node_modules" not in p]


def head_of(s):
    return s.split("</head>")[0] if "</head>" in s else s


def _header_noindex_globs():
    """Paths marked noindex via X-Robots-Tag in netlify.toml."""
    if not os.path.exists("netlify.toml"):
        return []
    toml = open("netlify.toml", encoding="utf-8").read()
    out = []
    for block in re.findall(r"\[\[headers\]\](.*?)(?=\[\[|\Z)", toml, re.S):
        if re.search(r"X-Robots-Tag\s*=\s*\"[^\"]*noindex", block, re.I):
            m = re.search(r'for\s*=\s*"([^"]+)"', block)
            if m:
                out.append(m.group(1).strip("/"))
    return out


_HEADER_NOINDEX = None


def is_noindex(s, path=None):
    if re.search(r'name="robots"[^>]*content="[^"]*noindex', head_of(s), re.I):
        return True
    if path:
        global _HEADER_NOINDEX
        if _HEADER_NOINDEX is None:
            _HEADER_NOINDEX = _header_noindex_globs()
        import fnmatch
        for pat in _HEADER_NOINDEX:
            if fnmatch.fnmatch(path, pat) or fnmatch.fnmatch(path, pat + "/*"):
                return True
    # A file with no <html> element is not a page (e.g. a bare verification
    # token served with a .html extension).
    if "<html" not in s.lower():
        return True
    return False


# --------------------------------------------------------------------------
# 1. Secrets. This is the check that would have caught the Airtable token.
# --------------------------------------------------------------------------

SECRET_PATTERNS = [
    (r"\bsk_live_[A-Za-z0-9]{16,}", "Stripe live secret key"),
    (r"\bsk_test_[A-Za-z0-9]{16,}", "Stripe test secret key"),
    (r"\brk_live_[A-Za-z0-9]{16,}", "Stripe restricted key"),
    (r"\bwhsec_[A-Za-z0-9]{16,}", "Stripe webhook secret"),
    (r"\bre_[A-Za-z0-9]{24,}", "Resend API key"),
    (r"\bpat[A-Za-z0-9]{14}\.[A-Za-z0-9]{40,}", "Airtable personal access token"),
    (r"\bghp_[A-Za-z0-9]{36}", "GitHub personal access token"),
    (r"\bAKIA[0-9A-Z]{16}\b", "AWS access key id"),
    (r'"type"\s*:\s*"service_account"', "Google service account JSON"),
    (r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----", "Private key"),
]

SECRET_SCAN_EXT = {".html", ".js", ".json", ".md", ".txt", ".toml", ".yml",
                   ".yaml", ".py", ".css"}
SECRET_SKIP = {"tools/check_site.py", ".env.example"}


def check_secrets():
    """No live credentials anywhere in the working tree."""
    for path in sorted(glob.glob("**/*", recursive=True)):
        if not os.path.isfile(path):
            continue
        if "node_modules" in path or path.startswith(".git/"):
            continue
        if path in SECRET_SKIP or os.path.splitext(path)[1] not in SECRET_SCAN_EXT:
            continue
        try:
            s = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for pattern, label in SECRET_PATTERNS:
            if re.search(pattern, s):
                err(path, f"possible {label} committed — this repo is public")

    # A service-role JWT is the one Supabase key that must never ship.
    for path in html_files() + sorted(glob.glob("**/*.js", recursive=True)):
        if "node_modules" in path:
            continue
        s = open(path, encoding="utf-8", errors="replace").read()
        for jwt in re.findall(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}", s):
            try:
                import base64
                body = jwt.split(".")[1]
                body += "=" * (-len(body) % 4)
                claims = json.loads(base64.urlsafe_b64decode(body))
                if claims.get("role") == "service_role":
                    err(path, "Supabase SERVICE_ROLE key present — bypasses RLS")
            except Exception:
                pass


def check_gitignore():
    """.env must be ignored, or the next secret lands in history too."""
    if not os.path.exists(".gitignore"):
        err(".gitignore", "missing — nothing stops .env being committed")
        return
    s = open(".gitignore", encoding="utf-8").read()
    if not re.search(r"^\.env\b", s, re.M):
        err(".gitignore", ".env is not ignored")


# --------------------------------------------------------------------------
# 2. Structured data
# --------------------------------------------------------------------------

def check_json_ld():
    """Every JSON-LD block parses, and describes its own page."""
    for path in html_files():
        s = open(path, encoding="utf-8", errors="replace").read()
        for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>',
                              s, re.S):
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError as e:
                err(path, f"invalid JSON-LD: {e}")
                continue
            graph = obj.get("@graph")
            # A @graph with several entities is a hub describing other pages
            # (services.html lists six Service nodes, one per service page).
            # Only a standalone node is expected to describe its own page.
            hub = bool(graph and len(graph) > 1)
            for node in (graph or [obj]):
                t = node.get("@type")
                if not hub and t in ("BlogPosting", "Article", "Service",
                                     "ContactPage", "Course"):
                    url = node.get("url") or node.get("@id") or ""
                    if url and os.path.basename(path) not in url:
                        err(path, f"{t} schema points at {url} — wrong page")
                if t in ("Review", "AggregateRating"):
                    author = (node.get("author") or {})
                    if t == "AggregateRating" or not author.get("name"):
                        err(path, f"{t} without a named author — Google rejects "
                                  "this and self-rating risks a manual action")


# --------------------------------------------------------------------------
# 3. Metadata
# --------------------------------------------------------------------------

def check_metadata():
    for path in html_files():
        s = open(path, encoding="utf-8", errors="replace").read()
        head = head_of(s)
        noindex = is_noindex(s, path)

        for attr, label in (("rel=\"canonical\"", "canonical"),
                            ("name=\"description\"", "description")):
            n = len(re.findall(attr, head))
            if n > 1:
                err(path, f"{n} {label} tags — must be exactly one")

        titles = re.findall(r"<title>(.*?)</title>", head, re.S)
        if len(titles) > 1:
            err(path, f"{len(titles)} <title> tags")
        elif not titles and not noindex:
            err(path, "no <title>")

        if noindex:
            if "rel=\"canonical\"" in head:
                err(path, "noindex page declares a canonical — contradictory")
            continue

        if "rel=\"canonical\"" not in head:
            err(path, "indexable page with no canonical")
        if titles:
            t = re.sub(r"&amp;", "&", titles[0]).strip()
            if len(t) > 62:
                warn(path, f"title {len(t)} chars, will truncate (aim 50-60)")
            elif len(t) < 30:
                warn(path, f"title only {len(t)} chars — wasting the budget")

        m = re.search(r'name="description"[^>]*content="([^"]*)"', head) or \
            re.search(r'content="([^"]*)"[^>]*name="description"', head)
        if not m:
            err(path, "indexable page with no meta description")
        else:
            d = len(re.sub(r"&amp;", "&", m.group(1)))
            if d > 165:
                warn(path, f"description {d} chars, will truncate (aim 140-160)")
            elif d < 90:
                warn(path, f"description only {d} chars")

        if "og:image" in head and "og:image:width" not in head:
            warn(path, "og:image without declared dimensions")

        h1s = re.findall(r"<h1\b", s)
        if len(h1s) > 1:
            err(path, f"{len(h1s)} <h1> elements — must be one")
        elif not h1s:
            warn(path, "no <h1>")


# --------------------------------------------------------------------------
# 4. Structure and links
# --------------------------------------------------------------------------

def check_structure():
    for path in html_files():
        s = open(path, encoding="utf-8", errors="replace").read()
        for tag in ("head", "main", "article", "nav", "footer", "section", "style"):
            opens = len(re.findall(rf"<{tag}\b[^>]*>", s))
            closes = s.count(f"</{tag}>")
            if opens != closes:
                err(path, f"<{tag}> unbalanced: {opens} open, {closes} close")
        if re.search(r"<style[^>]*>\s*</style>", s):
            warn(path, "empty <style> block")
        if "<html" in s.lower() and not re.search(r'<html[^>]*\blang=', s):
            err(path, "<html> has no lang attribute")


def check_links():
    for path in html_files():
        s = open(path, encoding="utf-8", errors="replace").read()
        for href in re.findall(r'href="([^"#][^"]*\.html)"', s):
            if href.startswith(("http://", "https://", "//")):
                continue
            base = "" if href.startswith("/") else os.path.dirname(path)
            target = os.path.normpath(os.path.join(
                base, urllib.parse.unquote(href.lstrip("/"))))
            if not os.path.exists(target):
                err(path, f"broken link: {href}")


def check_images():
    for path in html_files():
        s = open(path, encoding="utf-8", errors="replace").read()
        for tag in re.findall(r"<img\b[^>]*>", s, re.I):
            m = re.search(r'src="([^"]+)"', tag)
            if not m:
                err(path, "<img> with no src")
                continue
            src = m.group(1)
            if src.startswith(("http", "data:")):
                warn(path, f"third-party image: {src[:60]}")
                continue
            target = os.path.normpath(os.path.join(
                os.path.dirname(path), urllib.parse.unquote(src)))
            if not os.path.exists(target):
                err(path, f"missing image: {src}")
            if "width=" not in tag or "height=" not in tag:
                err(path, f"<img> without width/height (causes layout shift): {src}")
            if "loading=" not in tag:
                warn(path, f"<img> without loading attribute: {src}")
            if 'alt="' not in tag:
                err(path, f"<img> without alt: {src}")


# --------------------------------------------------------------------------
# 5. Sitemap and robots
# --------------------------------------------------------------------------

def check_sitemap():
    if not os.path.exists("sitemap.xml"):
        err("sitemap.xml", "missing")
        return
    try:
        xml.dom.minidom.parse("sitemap.xml")
    except Exception as e:
        err("sitemap.xml", f"invalid XML: {e}")
        return

    s = open("sitemap.xml", encoding="utf-8").read()
    listed = set(re.findall(r"<loc>([^<]+)</loc>", s))
    paths = {u.replace(SITE, "").lstrip("/") or "index.html" for u in listed}

    if "<lastmod>" not in s:
        warn("sitemap.xml", "no <lastmod> — the one element Google actually uses")

    for url in listed:
        if not url.startswith(SITE):
            err("sitemap.xml", f"URL on another domain: {url}")

    for path in html_files():
        s2 = open(path, encoding="utf-8", errors="replace").read()
        noindex = is_noindex(s2, path)
        key = "index.html" if path == "index.html" else path
        if noindex and key in paths:
            err("sitemap.xml", f"lists a noindex page: {path}")
        if not noindex and key not in paths and path != "404.html":
            err("sitemap.xml", f"indexable page missing: {path}")


def check_robots():
    if not os.path.exists("robots.txt"):
        err("robots.txt", "missing")
        return
    s = open("robots.txt", encoding="utf-8").read()
    if "Sitemap:" not in s:
        err("robots.txt", "no Sitemap: directive")
    for line in re.findall(r"^Disallow:\s*(\S+)", s, re.M):
        if line == "/":
            err("robots.txt", "Disallow: / blocks the entire site")


# --------------------------------------------------------------------------
# 6. Regressions this site has actually had
# --------------------------------------------------------------------------

# A blanket r"\$750" used to live here. It was removed once a legitimate $750
# appeared: "$500-$750" is the minimum-order range for a staffed buffet, both in
# the course material and in the catering pricing article. check_prices already
# does this properly, matching a figure only when it sits within 40 characters
# of the word "Snapshot", so the blunt rule was the weaker of two checks doing
# the same job.
STALE = [
    (r"images\.unsplash\.com", "hot-linked Unsplash image (unlicensed, slow)"),
    (r"client\.crisp\.chat", "Crisp chat loader (removed; was misconfigured)"),
    (r"blog_post_\d_", "old blog filename — use the slug"),
    (r"familypic\.jpg|hero\.png|calm%20ops|catering%20add", "pre-WebP image path"),
    (r"@import\s+url\(.*fonts\.googleapis", "render-blocking font @import"),
]


def check_stale():
    for path in html_files() + ["style.css", "analytics.js", "exit-intent-popup.js"]:
        if not os.path.exists(path):
            continue
        s = open(path, encoding="utf-8", errors="replace").read()
        for pattern, label in STALE:
            if re.search(pattern, s):
                err(path, f"stale reference: {label}")


def check_js():
    """Catch the duplicate-declaration class of bug that killed the popup."""
    import subprocess
    import shutil
    if not shutil.which("node"):
        warn("js", "node not installed — skipping syntax check")
        return
    for path in sorted(glob.glob("*.js")) + sorted(glob.glob("netlify/functions/*.js")):
        r = subprocess.run(["node", "--check", path],
                           capture_output=True, text=True)
        if r.returncode != 0:
            first = (r.stderr.strip().splitlines() or ["syntax error"])
            err(path, f"JS syntax error: {first[min(2, len(first)-1)].strip()}")



# --------------------------------------------------------------------------
# 7. Link graph — the audit's single biggest finding was four service pages
#    with one inbound link each. Nothing stops that recurring.
# --------------------------------------------------------------------------

def _inbound_counts():
    counts = {p: 0 for p in html_files()}
    for path in html_files():
        s = open(path, encoding="utf-8", errors="replace").read()
        for href in set(re.findall(r'href="([^"#][^"]*\.html)"', s)):
            if href.startswith(("http://", "https://", "//")):
                continue
            base = "" if href.startswith("/") else os.path.dirname(path)
            target = os.path.normpath(os.path.join(
                base, urllib.parse.unquote(href.lstrip("/"))))
            if target in counts and target != path:
                counts[target] += 1
    return counts


def check_orphans():
    """Indexable pages nothing links to, and noindex pages out-linking content."""
    counts = _inbound_counts()

    indexable = []
    for p, c in counts.items():
        body = open(p, encoding="utf-8", errors="replace").read()
        if not is_noindex(body, p):
            indexable.append(c)
    indexable.sort()
    median_indexable = (indexable[len(indexable) // 2] if indexable else 0)
    for path, n in sorted(counts.items()):
        s = open(path, encoding="utf-8", errors="replace").read()
        if is_noindex(s, path):
            # A members-area login link in the footer is normal and harmless;
            # "link equity going nowhere" is not a real mechanism. What IS a
            # real signal is a noindex page out-linking your actual content —
            # which is what this site had when login.html sat at 32 inbound
            # links while each service page had 1. Compare against the median
            # indexable page rather than a fixed number.
            if indexable and n > 1.5 * median_indexable:
                warn(path, f"noindex page has {n} inbound links vs a median of "
                           f"{median_indexable:.0f} for indexable pages — it is "
                           "out-linked against your real content")
            continue
        if n == 0:
            err(path, "orphan: no internal page links to it")
        elif n < 3 and path != "index.html":
            warn(path, f"only {n} inbound internal link(s)")


def check_duplicate_meta():
    """Two pages sharing a title or description compete with each other."""
    titles, descs = {}, {}
    for path in html_files():
        s = open(path, encoding="utf-8", errors="replace").read()
        if is_noindex(s, path):
            continue
        head = head_of(s)
        t = re.search(r"<title>(.*?)</title>", head, re.S)
        if t:
            key = t.group(1).strip()
            if key in titles:
                err(path, f"duplicate <title>, same as {titles[key]}")
            titles[key] = path
        m = re.search(r'name="description"[^>]*content="([^"]*)"', head) or \
            re.search(r'content="([^"]*)"[^>]*name="description"', head)
        if m:
            key = m.group(1).strip()
            if key in descs:
                err(path, f"duplicate meta description, same as {descs[key]}")
            descs[key] = path


def check_canonical_targets():
    """A canonical must point at the page's own URL.

    This is the exact bug a generated article shipped with: it inherited the
    template's canonical and declared itself to be a different article.
    """
    for path in html_files():
        s = open(path, encoding="utf-8", errors="replace").read()
        if is_noindex(s, path):
            continue
        m = re.search(r'rel="canonical"[^>]*href="([^"]+)"', head_of(s)) or \
            re.search(r'href="([^"]+)"[^>]*rel="canonical"', head_of(s))
        if not m:
            continue
        canon = m.group(1)
        expected = SITE + "/" + ("" if path == "index.html" else path)
        if canon.rstrip("/") != expected.rstrip("/"):
            err(path, f"canonical points at {canon}, expected {expected}")

        for prop in ("og:url", "twitter:url"):
            u = re.search(rf'{prop}"[^>]*content="([^"]+)"', head_of(s)) or \
                re.search(rf'content="([^"]+)"[^>]*{prop}"', head_of(s))
            if u and u.group(1).rstrip("/") != canon.rstrip("/"):
                err(path, f"{prop} ({u.group(1)}) disagrees with canonical")


# --------------------------------------------------------------------------
# 8. Weight budgets — services.html once shipped 11 MB of images
# --------------------------------------------------------------------------

MAX_IMAGE_KB = 400
MAX_PAGE_KB = 900


def check_weight():
    for path in html_files():
        s = open(path, encoding="utf-8", errors="replace").read()
        total = len(s.encode())
        refs = set(re.findall(r'src="([^"]+)"', s)) | \
               set(re.findall(r"url\('([^']+)'\)", s))
        for ref in refs:
            if ref.startswith(("http", "data:", "//")):
                continue
            f = os.path.normpath(os.path.join(
                os.path.dirname(path), urllib.parse.unquote(ref)))
            if not os.path.isfile(f):
                continue
            kb = os.path.getsize(f) / 1024
            if kb > MAX_IMAGE_KB and not f.endswith((".js", ".css")):
                err(path, f"{os.path.basename(f)} is {kb:.0f} KB "
                          f"(budget {MAX_IMAGE_KB} KB)")
            total += os.path.getsize(f)
        if total / 1024 > MAX_PAGE_KB:
            warn(path, f"page weight {total/1024:.0f} KB including local assets "
                       f"(budget {MAX_PAGE_KB} KB)")


def check_unused_images():
    referenced = set()
    for path in html_files() + ["style.css"]:
        if not os.path.exists(path):
            continue
        s = open(path, encoding="utf-8", errors="replace").read()
        for ref in re.findall(r'[src=url(]["\']?([^"\')\s]+\.(?:png|jpe?g|webp|svg|gif))',
                              s, re.I):
            referenced.add(os.path.basename(urllib.parse.unquote(ref)))
    for img in glob.glob("*.png") + glob.glob("*.jpg") + glob.glob("images/*"):
        if not os.path.isfile(img):
            continue
        if os.path.basename(img) not in referenced:
            kb = os.path.getsize(img) / 1024
            if kb > 100:
                warn(img, f"unreferenced, {kb:.0f} KB — deployed but unused")


# --------------------------------------------------------------------------
# 9. Config consistency
# --------------------------------------------------------------------------

# Netlify injects these at build and runtime. A function may read one, but it
# must never appear as a settable line in .env.example: writing it by hand in
# the Netlify UI overrides the real value, which is the opposite of the point.
# https://docs.netlify.com/configure-builds/environment-variables/
PLATFORM_ENV = {
    "URL", "DEPLOY_URL", "DEPLOY_PRIME_URL", "CONTEXT", "SITE_NAME", "SITE_ID",
    "COMMIT_REF", "BRANCH", "HEAD", "REPOSITORY_URL", "NETLIFY", "BUILD_ID",
}


def check_env_documented():
    """Every process.env.X used by a function must appear in .env.example.

    COURSE-SYSTEM-SETUP.md documented 6 of 9 variables; the 3 it missed are
    exactly the 3 that were lost when the Netlify project went away.

    A platform variable is exempt from needing a settable line, but not from
    needing an explanation: it still has to be named somewhere in the file, so
    the next person reading it learns the function depends on something they
    will not find in the Netlify UI.
    """
    used = set()
    for f in glob.glob("netlify/functions/*.js"):
        s = open(f, encoding="utf-8", errors="replace").read()
        used |= set(re.findall(r"process\.env\.([A-Z0-9_]+)", s))
    if not used:
        return
    if not os.path.exists(".env.example"):
        err(".env.example", f"missing — {len(used)} env vars are undocumented")
        return
    text = open(".env.example", encoding="utf-8").read()
    documented = set(re.findall(r"^([A-Z0-9_]+)=", text, re.M))

    for v in sorted(used - documented):
        if v in PLATFORM_ENV:
            # Netlify supplies it; it only has to be explained, not set.
            if not re.search(rf"\b{re.escape(v)}\b", text):
                err(".env.example", f"{v} is read by a function and provided by "
                                    f"Netlify, but is not explained anywhere")
            continue
        err(".env.example", f"{v} is used by a function but not documented")

    for v in sorted(documented - used):
        warn(".env.example", f"{v} is documented but no function reads it")

    # A platform variable with a settable line is the failure this guards
    # against: it would be overridden by hand and stop tracking reality.
    for v in sorted(documented & PLATFORM_ENV):
        err(".env.example", f"{v} is set by Netlify — it must not appear as a "
                            f"settable line, or a hand-entered value overrides it")


def check_ga4_ids_agree():
    """The GA4 measurement id is written in two places; they must match.

    analytics.js configures the property for the browser. stripe-webhook.js
    hardcodes the same id to post server-side purchase events to it. Nothing
    at runtime would notice a mismatch: the webhook would keep answering 200
    and keep logging success while posting revenue into a property that does
    not exist, and the only symptom would be a `purchase` conversion stuck at
    zero while Stripe shows sales.
    """
    pairs = [
        ("analytics.js", r"G-[A-Z0-9]+"),
        ("netlify/functions/stripe-webhook.js", r"G-[A-Z0-9]+"),
    ]
    found = {}
    for path, pat in pairs:
        if not os.path.exists(path):
            continue
        ids = set(re.findall(pat, open(path, encoding="utf-8").read()))
        if not ids:
            err(path, "no GA4 measurement id (G-...) found")
            return
        if len(ids) > 1:
            err(path, f"more than one GA4 measurement id: {sorted(ids)}")
            return
        found[path] = ids.pop()

    if len(found) == 2 and len(set(found.values())) != 1:
        err("analytics.js", "GA4 measurement id disagrees with "
                            f"stripe-webhook.js: {found}")


def check_markdown_blocked():
    """Every working .md document must 404, not be served.

    publish = "." serves the whole repository, so a note added at the root is
    a live URL. The rules are per-file because a splat only expands at the END
    of a Netlify path, so "/*.md" matched nothing and silently published
    everything it was written to hide.

    Per-file rules are easy to forget on the next document, which is what this
    check exists to catch: CLAUDE.md was one `git add` away from being served
    when it was written. Files under tools/ and drafts/ are already covered by
    their directory rules, so only the root and images/ are checked here.
    """
    if not os.path.exists("netlify.toml"):
        return
    # tomllib is imported here, not at module scope — check_netlify_toml does
    # the same so the file keeps working on a Python without it. The first
    # version of this function called tomllib.load() as though it were a
    # global and wrapped it in `except Exception: return`, so every run threw
    # NameError, swallowed it, and reported a clean pass over a file it had
    # never opened. Only TOMLDecodeError is caught now, and the import failing
    # is reported rather than hidden.
    try:
        import tomllib
    except ImportError:
        warn("netlify.toml", "tomllib unavailable; .md exposure not checked")
        return
    with open("netlify.toml", "rb") as fh:
        try:
            conf = tomllib.load(fh)
        except tomllib.TOMLDecodeError:
            return          # check_netlify_toml already reported this

    blocked = {
        r.get("from") for r in conf.get("redirects", [])
        if str(r.get("status")) == "404"
    }

    for path in sorted(glob.glob("*.md") + glob.glob("images/*.md")):
        route = "/" + path.replace(os.sep, "/")
        if route not in blocked:
            err(path, f"served publicly — add a 404 redirect for {route} in "
                      f"netlify.toml, or move it under tools/")


MONTHS = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], start=1)}

# A date is only a promise when something nearby says it is one. Without this
# the blog's own post-meta ("August 16, 2026") would trip the check.
PROMISE = r"launch\w*|goes live|going live|coming|release\w*|drops|opens"


def check_launch_dates():
    """A launch date that has already passed must not still be advertised.

    "March 30th, 2026" sat in eleven customer-facing places for six months.
    Every one of them was reachable only AFTER payment — the post-purchase
    page, both confirmation emails, and the logged-in course pages — so the
    public site looked clean while everyone who paid was told the course had
    launched in March. The sales page said only "soon", which is why nobody
    browsing could see the contradiction.

    Only .html and .js are checked, and tools/ and drafts/ are skipped: the
    failure being guarded against is what a customer reads.
    """
    import datetime
    today = datetime.date.today()
    pattern = re.compile(
        rf"(?:{PROMISE})[^<>.]{{0,60}}?"
        rf"({'|'.join(MONTHS)})\s+(\d{{1,2}})(?:st|nd|rd|th)?(?:,?\s+(20\d\d))?",
        re.I)

    files = [f for f in glob.glob("**/*.html", recursive=True)
                     + glob.glob("**/*.js", recursive=True)
             if not f.startswith(("tools/", "drafts/", "node_modules/"))]

    for f in sorted(files):
        text = open(f, encoding="utf-8", errors="replace").read()
        for m in pattern.finditer(text):
            month = MONTHS[m.group(1).capitalize()]
            day = int(m.group(2))
            year = int(m.group(3)) if m.group(3) else today.year
            try:
                when = datetime.date(year, month, day)
            except ValueError:
                continue
            if when < today:
                err(f, f"advertises a launch date that has passed: "
                       f"{m.group(0).strip()!r} ({when.isoformat()})")


def check_redirects():
    """Redirect targets in netlify.toml must exist."""
    if not os.path.exists("netlify.toml"):
        return
    toml = open("netlify.toml", encoding="utf-8").read()
    for block in re.findall(r"\[\[redirects\]\](.*?)(?=\[\[|\Z)", toml, re.S):
        to = re.search(r'to\s*=\s*"([^"]+)"', block)
        frm = re.search(r'from\s*=\s*"([^"]+)"', block)
        if not to:
            continue
        target = to.group(1).split("?")[0].lstrip("/")
        if not target or target.startswith("http"):
            continue

        # A function target is a handler on disk, not a file in the publish
        # directory: /.netlify/functions/foo is netlify/functions/foo.js.
        # Checking it still matters — a redirect naming a function that does
        # not exist is a 404 on a route the site depends on.
        if target.startswith(".netlify/functions/"):
            name = target[len(".netlify/functions/"):]
            if not any(os.path.exists(f"netlify/functions/{name}{ext}")
                       for ext in (".js", ".mjs", ".ts")):
                err("netlify.toml",
                    f"redirect names a function that does not exist: {name}")
            continue

        if not os.path.exists(target):
            err("netlify.toml", f"redirect target does not exist: {to.group(1)}")
        if frm and frm.group(1).lstrip("/") == target:
            err("netlify.toml", f"redirect loop: {frm.group(1)}")


def course_file_text(path):
    """Readable text out of a .xlsx or .docx, for the checks that scan content.

    Both are zip archives of XML, so the text can be pulled without openpyxl,
    which keeps this file dependency-free.

    A spreadsheet stores its strings one of two ways and this repository
    contains both: a shared table in xl/sharedStrings.xml, or inline in the
    worksheet itself. The first version of this read only sharedStrings.xml and
    silently extracted nothing from the files openpyxl had rewritten — it
    reported a clean pass over a spreadsheet it had not read a word of. Read
    the worksheets too, and the shape stops mattering.
    """
    import xml.sax.saxutils
    import zipfile
    ext = os.path.splitext(path)[1].lower()
    if ext not in (".xlsx", ".docx"):
        return ""
    try:
        with zipfile.ZipFile(path) as z:
            if ext == ".docx":
                wanted = [n for n in z.namelist() if n == "word/document.xml"]
            else:
                wanted = [n for n in z.namelist()
                          if n == "xl/sharedStrings.xml"
                          or (n.startswith("xl/worksheets/") and n.endswith(".xml"))]
            if not wanted:
                return ""
            raw = " ".join(z.read(n).decode("utf-8", "replace") for n in wanted)
    except (zipfile.BadZipFile, OSError):
        return ""
    return xml.sax.saxutils.unescape(re.sub(r"<[^>]+>", " ", raw))


def check_prices():
    """The Snapshot price must be $350 wherever it is named.

    A stale "$750 Profit Leak Snapshot" sat in the exit-intent popup for
    months. Only prices stated in the same breath as the Snapshot are checked —
    the site legitimately mentions other figures ($500K revenue bands, a $500
    credit offer, a $500 hypothetical in an article).

    The course downloads are scanned too, and that is not hypothetical: the same
    stale $750 was sitting in two spreadsheets buyers download, quoting a price
    the site has not charged in months. This check only read HTML, which is
    exactly why it survived there. A binary deliverable is still content.
    """
    paths = html_files() + ["exit-intent-popup.js"]
    paths += [p for p in glob.glob("course/downloads/**/*", recursive=True)
              if os.path.isfile(p)]
    for path in paths:
        if not os.path.exists(path):
            continue
        if os.path.splitext(path)[1].lower() in (".xlsx", ".docx"):
            s = course_file_text(path)
        else:
            s = open(path, encoding="utf-8", errors="replace").read()
        for m in re.finditer(r"\$(\d{2,4})[^.\n]{0,40}?(Profit Leak )?Snapshot", s, re.I):
            if m.group(1) != "350":
                err(path, f"Snapshot priced at ${m.group(1)} — it is $350")
        for m in re.finditer(r"Snapshot[^.\n]{0,40}?\$(\d{2,4})", s, re.I):
            if m.group(1) != "350":
                err(path, f"Snapshot priced at ${m.group(1)} — it is $350")


# --------------------------------------------------------------------------
# 10. HTML correctness and accessibility
# --------------------------------------------------------------------------

def check_ids_and_a11y():
    for path in html_files():
        s = open(path, encoding="utf-8", errors="replace").read()

        ids = re.findall(r'\sid="([^"]+)"', s)
        dupes = {i for i in ids if ids.count(i) > 1}
        for d in sorted(dupes):
            err(path, f"duplicate id=\"{d}\" — breaks JS and assistive tech")

        for tag in re.findall(r"<a\b[^>]*target=\"_blank\"[^>]*>", s):
            if "noopener" not in tag:
                err(path, "target=\"_blank\" without rel=\"noopener\"")

        if re.search(r'<(?:script|link|img)[^>]+(?:src|href)="http://', s):
            err(path, "http:// resource on an https site (mixed content)")

        for tag in re.findall(r"<input\b[^>]*>", s):
            t = re.search(r'type="([^"]+)"', tag)
            if t and t.group(1) in ("hidden", "submit", "button"):
                continue
            has_id = re.search(r'\sid="([^"]+)"', tag)
            labelled = ("aria-label" in tag or "placeholder" in tag)
            if has_id and f'for="{has_id.group(1)}"' in s:
                labelled = True
            # <label>Name <input ...></label> — implicit association, valid HTML
            at = s.find(tag)
            if at != -1:
                before = s[max(0, at - 400):at]
                if before.rfind("<label") > before.rfind("</label>"):
                    labelled = True
            if not labelled:
                warn(path, "form input with no label, aria-label or placeholder")

        levels = [int(m) for m in re.findall(r"<h([1-6])\b", s)]
        for a, b in zip(levels, levels[1:]):
            if b - a > 1:
                warn(path, f"heading jumps h{a} to h{b}")
                break


def check_faq_visible():
    """FAQPage markup must correspond to text a user can see."""
    for path in html_files():
        s = open(path, encoding="utf-8", errors="replace").read()
        if "FAQPage" not in s:
            continue
        body = s.split("</head>")[-1]
        visible = re.sub(r"<[^>]+>", " ", body)
        visible = re.sub(r"\s+", " ", visible).lower()
        for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>',
                              s, re.S):
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if obj.get("@type") != "FAQPage":
                continue
            for q in obj.get("mainEntity", []):
                name = re.sub(r"\s+", " ", (q.get("name") or "")).lower()
                probe = name[:40].strip()
                if probe and probe not in visible:
                    err(path, f'FAQPage question not visible on the page: "'
                              f'{q.get("name", "")[:50]}..."')

def check_fragments():
    """Every same-page #fragment must have an element to land on.

    This is the check that was missing when twenty pages shipped a skip link
    pointing at #main-content on pages that had no such id: the first thing a
    keyboard user tabbed to did nothing. lychee found it in CI; it should not
    have needed CI to find it, so it is static now.

    Only same-page fragments are checked. A fragment on a link to another page
    is resolved against that page, and a bare href="#" is a deliberate
    JavaScript hook, not a destination.
    """
    for path in html_files():
        s = open(path, encoding="utf-8", errors="replace").read()
        targets = set(re.findall(r'\sid="([^"]+)"', s))
        targets |= set(re.findall(r'<a\b[^>]*\sname="([^"]+)"', s))
        for frag in sorted(set(re.findall(r'href="#([^"]+)"', s))):
            if frag == "top" or frag in targets:
                continue
            err(path, f'href="#{frag}" but nothing on the page has that id')

        # A skip link is the one fragment that must exist on every page that
        # claims to have one, and must point at the content rather than a modal.
        if "skip-link" in s and 'id="main-content"' not in s:
            err(path, "skip link with no #main-content landmark to skip to")

        # Fragments on links to other pages of this site, which lychee also
        # resolves. Links off the site are left to lychee alone.
        for rel, frag in set(re.findall(r'href="([^":#]+\.html)#([^"]+)"', s)):
            target = os.path.normpath(os.path.join(os.path.dirname(path), rel))
            if not os.path.exists(target):
                continue   # the links check reports the missing file itself
            other = open(target, encoding="utf-8", errors="replace").read()
            if frag not in set(re.findall(r'\sid="([^"]+)"', other)):
                err(path, f'links to {rel}#{frag} but that page has no '
                          f'id="{frag}"')


def check_contrast():
    """No colour pairing that fix_contrast.py would have to repair.

    This delegates to the generator rather than restating its patterns, so the
    two cannot drift. If fix_contrast.py would change a file, the file has a
    pairing measured below WCAG AA and this fails.

    It exists because Lighthouse could not be relied on here. axe cannot
    resolve the backdrop behind an element whose ancestor carries a background
    image, so it reports those descendants as *incomplete* rather than failing,
    and Lighthouse's color-contrast audit counts only failures. advisory.html
    scored accessibility 100 with a white-on-gold button at 2.03:1 sitting
    inside its hero image. axe also never evaluates a :hover state, so a button
    can pass at rest and fail under the pointer. Both gaps are static, so a
    static check closes them.
    """
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    sys.dont_write_bytecode = True   # no __pycache__ beside the tools
    try:
        import fix_contrast
    except ImportError:
        warn("tools/", "fix_contrast.py not importable; contrast unchecked")
        return
    for path in html_files():
        original = open(path, encoding="utf-8", errors="replace").read()
        _, num = fix_contrast.convert(path, original)
        if num:
            err(path, f"{num} colour pairing(s) below WCAG AA — "
                      f"run python3 tools/fix_contrast.py")


def check_course_gate():
    """The paid course files must be behind the function, not served statically.

    publish = "." means every file in the repository is served, so the only
    thing standing between course/downloads/ and the public internet is the
    forced rewrite in netlify.toml. Delete that one block and 26 paid files go
    back to answering 200, silently, with nothing else in the repository
    changing. This asserts the whole chain is present.

    It cannot tell you the gate WORKS — that needs a deployed site. The
    netlify.toml comment carries the one-line curl for that.
    """
    if not os.path.exists("netlify.toml"):
        return
    toml = open("netlify.toml", encoding="utf-8").read()

    gate = None
    for block in re.findall(r"\[\[redirects\]\](.*?)(?=\[\[|\Z)", toml, re.S):
        frm = re.search(r'from\s*=\s*"([^"]+)"', block)
        if frm and frm.group(1) == "/course/downloads/*":
            gate = block
            break

    if gate is None:
        err("netlify.toml", "no rewrite for /course/downloads/* — the paid "
                            "course files are served as public static assets")
        return

    if not re.search(r"force\s*=\s*true", gate):
        err("netlify.toml", "/course/downloads/* rewrite is not force = true, "
                            "so the static files still win and the gate does "
                            "nothing")

    if "course-download" not in gate:
        err("netlify.toml", "/course/downloads/* does not point at the "
                            "course-download function")

    if not os.path.exists("netlify/functions/course-download.js"):
        err("netlify/functions/", "course-download.js is missing")

    # The function reads the files off disk, so they must be in its bundle.
    inc = re.search(r"included_files\s*=\s*\[([^\]]*)\]", toml)
    if not inc or "course/downloads" not in inc.group(1):
        err("netlify.toml", "course/downloads is not in included_files, so the "
                            "function cannot read the files it gates")

    # Every page with download links needs the client that adds the header.
    for path in sorted(glob.glob("course/*.html")):
        page = open(path, encoding="utf-8", errors="replace").read()
        if 'class="dl-btn"' in page and "downloads.js" not in page:
            err(path, "has download links but does not load downloads.js, so "
                      "they will hit the gate without a token")


def check_netlify_toml():
    """netlify.toml must actually parse as TOML.

    Everything else here reads netlify.toml with regular expressions, which
    cannot tell a valid document from a broken one. That gap shipped a
    duplicate `force` key to Netlify: the build failed, every deploy check went
    red, and this checker said PASSED, because a regex looking for
    `force = true` is perfectly happy to find it on the line above a
    contradicting `force = false`.

    tomllib rejects that in one line, so it runs first and the regex checks
    below it are only reached on a document that parses.

    It also catches what the regex checks structurally cannot: a key repeated
    inside one block, a table defined twice, an unterminated string.
    """
    if not os.path.exists("netlify.toml"):
        return
    try:
        import tomllib
    except ImportError:          # Python < 3.11
        warn("netlify.toml", "tomllib unavailable; TOML not validated")
        return
    try:
        with open("netlify.toml", "rb") as fh:
            config = tomllib.load(fh)
    except tomllib.TOMLDecodeError as exc:
        err("netlify.toml", f"does not parse as TOML — Netlify will fail the "
                            f"deploy: {exc}")
        return

    # A redirect needs somewhere to go, and a status Netlify understands.
    for i, rule in enumerate(config.get("redirects", []), start=1):
        if "from" not in rule:
            err("netlify.toml", f"redirect #{i} has no `from`")
        if "to" not in rule:
            err("netlify.toml", f"redirect #{i} ({rule.get('from', '?')}) "
                                f"has no `to`")
        status = rule.get("status", 301)
        if not isinstance(status, int) or not 200 <= status <= 599:
            err("netlify.toml", f"redirect {rule.get('from', '?')} has an "
                                f"invalid status: {status!r}")

        # Netlify expands a splat only at the end of a path. `/*.md` looks like
        # an extension glob and is not one — it matches nothing.
        frm = rule.get("from", "")
        if "*" in frm and not frm.endswith("*"):
            err("netlify.toml", f"`{frm}` has a splat that is not at the end; "
                                f"Netlify will not treat it as a wildcard")


def check_component_css():
    """A component's own CSS must be reachable from every page that uses it.

    Two bugs shipped together and neither was visible to any existing check,
    because every one of them reads a page in isolation and no page was
    malformed. Both were found by a human looking at the live site.

    virginia-neighbors.html carried the full #mainNav but stopped linking
    style.css during the redesign conversion. ledger.css only recolours the
    nav; the layout (flex, list-style, dropdown positioning) is in style.css,
    so the nav rendered as a bulleted list with every dropdown expanded.

    .skip-link's off-screen parking is likewise style.css-only, so the
    thirteen pages that do not link style.css each rendered a permanently
    visible "Skip to content" above the masthead -- including every course
    page and the post-purchase thank-you page.

    So: if a page uses the component, the stylesheet that lays it out has to
    be on that page. ledger.css now carries .skip-link itself, which is why
    that half is satisfied by either sheet.
    """
    for path in html_files():
        s = open(path, encoding="utf-8", errors="replace").read()
        head = head_of(s)
        links_style = re.search(r'<link[^>]+href="[^"]*style\.css"', head)
        links_ledger = re.search(r'<link[^>]+href="[^"]*ledger\.css"', head)

        if 'id="mainNav"' in s and not links_style:
            err(path, 'uses #mainNav but does not link style.css '
                      '(ledger.css only recolours the nav; the layout is in style.css)')

        if "skip-link" in s and not (links_style or links_ledger):
            # A page with no shared stylesheet may park the link inline instead,
            # the way contact.html's honeypot does.
            inline = re.search(r'class="skip-link"[^>]*style="[^"]*position:\s*absolute', s)
            if not inline:
                err(path, 'has a .skip-link but neither links style.css/ledger.css nor '
                          'positions it inline, so it renders as visible text')


CHECKS = [
    ("netlify-toml", check_netlify_toml, "netlify.toml parses and its redirects are sane"),
    ("secrets", check_secrets, "live credentials in tracked files"),
    ("gitignore", check_gitignore, ".env is ignored"),
    ("json-ld", check_json_ld, "schema parses and describes its own page"),
    ("metadata", check_metadata, "title/description/canonical/h1 sanity"),
    ("structure", check_structure, "tag balance and lang attribute"),
    ("component-css", check_component_css, "pages link the stylesheet that lays out the components they use"),
    ("links", check_links, "internal links resolve"),
    ("images", check_images, "images exist and carry width/height/alt"),
    ("sitemap", check_sitemap, "every indexable page listed, no noindex ones"),
    ("robots", check_robots, "robots.txt sane"),
    ("stale", check_stale, "references to removed assets and old prices"),
    ("js", check_js, "JavaScript parses"),
    ("orphans", check_orphans, "every indexable page has inbound links"),
    ("dup-meta", check_duplicate_meta, "no two pages share a title or description"),
    ("canonical", check_canonical_targets, "canonical/og:url point at the page itself"),
    ("weight", check_weight, "image and page weight budgets"),
    ("unused-img", check_unused_images, "images deployed but never referenced"),
    ("env-docs", check_env_documented, "every process.env var is in .env.example"),
    ("ga4-ids", check_ga4_ids_agree, "the GA4 measurement id matches in both files"),
    ("md-private", check_markdown_blocked, "working .md documents are not served"),
    ("launch-date", check_launch_dates, "no advertised launch date has already passed"),
    ("redirects", check_redirects, "netlify.toml redirect targets exist"),
    ("prices", check_prices, "no stale product prices"),
    ("html-a11y", check_ids_and_a11y, "duplicate ids, noopener, mixed content, labels"),
    ("faq-visible", check_faq_visible, "FAQPage markup matches visible text"),
    ("fragments", check_fragments, "every #fragment link has a target"),
    ("contrast", check_contrast, "no colour pairing below WCAG AA"),
    ("course-gate", check_course_gate, "paid course files are behind the function"),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quiet", action="store_true", help="errors only")
    ap.add_argument("--list", action="store_true", help="list checks and exit")
    args = ap.parse_args()

    if args.list:
        for name, _, desc in CHECKS:
            print(f"  {name:<12} {desc}")
        return 0

    for name, fn, _ in CHECKS:
        fn()

    if warnings and not args.quiet:
        print(f"\n{len(warnings)} warning(s):")
        for where, msg in warnings:
            print(f"  {where}: {msg}")

    if errors:
        print(f"\n{len(errors)} error(s):")
        for where, msg in errors:
            print(f"  {where}: {msg}")
        print(f"\nFAILED — {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1

    print(f"\nPASSED — 0 errors, {len(warnings)} warning(s), "
          f"{len(html_files())} pages checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
