#!/usr/bin/env python3
"""
Replace the render-blocking @import in style.css with per-page <link> tags.

Why: a CSS `@import` cannot start downloading until style.css itself has been
fetched and parsed, which serialises the request chain

    HTML  ->  style.css  ->  fonts.googleapis.com  ->  font files

Moving the font request into the document <head> lets it start in parallel
with style.css, and `preconnect` warms the DNS/TLS handshake ahead of time.

Run from the repository root:

    python3 tools/fix_font_loading.py

Idempotent: pages that already declare a Google Fonts stylesheet are skipped
untouched, so re-running is safe.
"""

import glob
import os
import re

FONT_BLOCK = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800&family=Open+Sans:wght@400;600&display=swap" rel="stylesheet">
"""

STYLE_LINK = re.compile(r'[ \t]*<link[^>]*href="(?:\.\./)?style\.css"[^>]*>\s*\n', re.I)
HEAD_CLOSE = re.compile(r'</head>', re.I)
HAS_FONTS = re.compile(r'fonts\.googleapis\.com/css2', re.I)
USES_FONTS = re.compile(r'Montserrat|Open Sans|style\.css', re.I)


def indent_of(line):
    return line[: len(line) - len(line.lstrip())]


def process(path):
    with open(path, encoding="utf-8") as fh:
        html = fh.read()

    if not USES_FONTS.search(html):
        return "skip (no fonts used)"
    if HAS_FONTS.search(html):
        return "skip (already declared)"
    if not HEAD_CLOSE.search(html):
        return "skip (no <head>)"

    match = STYLE_LINK.search(html)
    if match:
        # Insert immediately before the stylesheet so both start in parallel.
        pad = indent_of(match.group(0))
        block = "".join(pad + line + "\n" for line in FONT_BLOCK.strip().split("\n"))
        html = html[: match.start()] + block + html[match.start():]
    else:
        # No external stylesheet (inline <style> only) — put it before </head>.
        pos = HEAD_CLOSE.search(html).start()
        pad = indent_of(html[: pos].rsplit("\n", 1)[-1]) or "  "
        block = "".join(pad + line + "\n" for line in FONT_BLOCK.strip().split("\n"))
        html = html[:pos] + block + html[pos:]

    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return "updated"


def strip_css_import():
    path = "style.css"
    with open(path, encoding="utf-8") as fh:
        css = fh.read()

    new = re.sub(
        r'[ \t]*/\* Import operator-focused fonts \*/\s*\n'
        r'[ \t]*@import url\([^)]*fonts\.googleapis\.com[^)]*\);[ \t]*\n',
        "/* Fonts are loaded via <link> in each page's <head> — see\n"
        "   tools/fix_font_loading.py. Do not reintroduce an @import here:\n"
        "   it serialises the font request behind this stylesheet. */\n",
        css,
        count=1,
    )
    if new == css:
        return "style.css: no @import found (already clean?)"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(new)
    return "style.css: @import removed"


def main():
    print(strip_css_import())
    counts = {}
    for path in sorted(glob.glob("**/*.html", recursive=True)):
        if "node_modules" in path:
            continue
        result = process(path)
        counts[result] = counts.get(result, 0) + 1
        if result == "updated":
            print(f"  updated  {path}")
    print()
    for key, num in sorted(counts.items()):
        print(f"{num:3d}  {key}")


if __name__ == "__main__":
    main()
