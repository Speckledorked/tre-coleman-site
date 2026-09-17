#!/usr/bin/env python3
"""
Point every og:image / twitter:image at the 1200x630 card, and declare its
dimensions and alt text.

Previously ~20 pages pointed og:image at a 200x200 headshot while declaring
`twitter:card = summary_large_image`, so shares rendered as a broken or tiny
thumbnail. og:image:width / og:image:height let Facebook and LinkedIn lay the
card out on first scrape instead of waiting to fetch and measure it.

Run from the repository root, after tools/build_og_image.py:

    python3 tools/fix_og_images.py

Idempotent — safe to re-run.
"""

import glob
import re

CARD = "https://trecoleman.com/images/og-card.jpg"
ALT = ("Tre Coleman — restaurant operations consulting for restaurants, "
       "food trucks, and catering companies")

OLD_IMAGES = [
    "https://trecoleman.com/images/tre-headshot.jpg",
    "https://trecoleman.com/familypic.jpg",
]

OG_IMAGE = re.compile(
    r'<meta\s+(?:property="og:image"\s+content="([^"]*)"'
    r'|content="([^"]*)"\s+property="og:image")\s*/?>',
    re.I,
)


def indent_of(text, pos):
    line_start = text.rfind("\n", 0, pos) + 1
    raw = text[line_start:pos]
    return raw if raw.strip() == "" else ""


def process(path):
    with open(path, encoding="utf-8") as fh:
        html = fh.read()
    original = html

    for old in OLD_IMAGES:
        html = html.replace(old, CARD)

    # Add width/height/alt directly after the og:image tag, once.
    if "og:image:width" not in html:
        match = OG_IMAGE.search(html)
        if match:
            pad = indent_of(html, match.start())
            extra = (
                f'\n{pad}<meta property="og:image:width" content="1200" />'
                f'\n{pad}<meta property="og:image:height" content="630" />'
                f'\n{pad}<meta property="og:image:alt" content="{ALT}" />'
            )
            html = html[: match.end()] + extra + html[match.end():]

    if html == original:
        return False
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return True


def main():
    changed = 0
    for path in sorted(glob.glob("**/*.html", recursive=True)):
        if "node_modules" in path:
            continue
        if process(path):
            print(f"  updated  {path}")
            changed += 1
    print(f"\n{changed} page(s) updated.")


if __name__ == "__main__":
    main()
