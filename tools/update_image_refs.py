#!/usr/bin/env python3
"""
Point every image reference at the optimised WebP files and add the
attributes that keep Core Web Vitals healthy.

For each <img> this sets:
  * src        -> the new images/*.webp path
  * width/height -> the file's real intrinsic size, so the browser can
                    reserve space and Cumulative Layout Shift stays at 0.
                    The existing inline `max-width / height:auto` CSS still
                    governs the rendered size, so nothing looks different.
  * loading    -> "lazy" for below-the-fold images, "eager" for hero images
  * decoding   -> "async"

It also rewrites the CSS background on the homepage hero and adds a
<link rel="preload"> for it, because a CSS background cannot be discovered by
the preload scanner and is the page's LCP element.

Run from the repository root, after tools/optimise_images.py:

    python3 tools/update_image_refs.py
"""

import re
from PIL import Image

# old src (as written in the HTML, including %20 escapes) -> new path
REPLACEMENTS = {
    "fixed%20systems.png": "images/restaurant-systems-before-after.webp",
    "ChatGPT%20Image%20Feb%203,%202026,%2008_52_24%20PM.png": "images/ai-integration-restaurants.webp",
    "Reviewing%20KPIs%20in%20a%20modern%20office.png": "images/sops-training-systems.webp",
    "ChatGPT%20Image%20Feb%203,%202026,%2008_53_59%20PM.png": "images/local-store-marketing.webp",
    "Reviewing%20restaurant%20menus%20and%20notes.png": "images/menu-engineering-analysis.webp",
    "ChatGPT%20Image%20Feb%203,%202026,%2008_55_43%20PM.png": "images/advisory-fractional-operations.webp",
    "familypic.jpg": "images/tre-coleman-family.webp",
    "newsletterlogo.png": "images/from-the-floor-up-newsletter.webp",
    "facebookbackground.png": "images/restaurant-operations-management.webp",
    "calm%20ops.png": "images/calm-operations-are-built.webp",
    "catering%20add.png": "images/adding-catering-to-restaurant.webp",
}

# Images that sit above the fold and must not be lazy-loaded.
EAGER = {"images/tre-coleman-family.webp"}

HERO_OLD = "url('hero.png')"
HERO_NEW = "url('images/hero-restaurant-operations.webp')"
HERO_PRELOAD = (
    '    <link rel="preload" as="image" '
    'href="images/hero-restaurant-operations.webp" fetchpriority="high">\n'
)

PAGES = [
    "index.html", "services.html", "about.html", "advisory.html",
    "catering-profit.html", "playbook.html", "profit-leak-snapshot.html",
]

_sizes = {}


def intrinsic(path):
    if path not in _sizes:
        with Image.open(path) as img:
            _sizes[path] = img.size
    return _sizes[path]


def set_attr(tag, name, value):
    """Set or replace an attribute on a single HTML tag string."""
    pattern = re.compile(rf'\s{name}\s*=\s*"[^"]*"', re.I)
    if pattern.search(tag):
        return pattern.sub(f' {name}="{value}"', tag, count=1)
    # insert just before the tag's closing bracket
    return re.sub(r'\s*/?>$', lambda m: f' {name}="{value}"' + m.group(0), tag, count=1)


def fix_img_tag(tag):
    match = re.search(r'\ssrc\s*=\s*"([^"]+)"', tag, re.I)
    if not match:
        return tag, False
    old = match.group(1)
    if old not in REPLACEMENTS:
        return tag, False

    new = REPLACEMENTS[old]
    width, height = intrinsic(new)

    tag = re.sub(r'(\ssrc\s*=\s*")[^"]+(")', rf'\g<1>{new}\g<2>', tag, count=1)
    tag = set_attr(tag, "width", str(width))
    tag = set_attr(tag, "height", str(height))
    tag = set_attr(tag, "loading", "eager" if new in EAGER else "lazy")
    tag = set_attr(tag, "decoding", "async")
    if new in EAGER:
        tag = set_attr(tag, "fetchpriority", "high")
    return tag, True


def main():
    total = 0
    for page in PAGES:
        with open(page, encoding="utf-8") as fh:
            html = fh.read()
        original = html
        changed = 0

        def repl(match):
            nonlocal changed
            new_tag, did = fix_img_tag(match.group(0))
            if did:
                changed += 1
            return new_tag

        html = re.sub(r'<img\b[^>]*>', repl, html, flags=re.I)

        # Homepage hero: CSS background -> WebP, plus a preload hint.
        if HERO_OLD in html:
            html = html.replace(HERO_OLD, HERO_NEW)
            changed += 1
            if "rel=\"preload\" as=\"image\"" not in html:
                html = html.replace("    <title>", HERO_PRELOAD + "    <title>", 1)

        if html != original:
            with open(page, "w", encoding="utf-8") as fh:
                fh.write(html)
        print(f"{changed:2d} reference(s) updated  {page}")
        total += changed

    print(f"\n{total} image references updated.")


if __name__ == "__main__":
    main()
