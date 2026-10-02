#!/usr/bin/env python3
"""
Add course/downloads.js to every course page that carries download links.

The links themselves are untouched. downloads.js intercepts their clicks and
re-issues them as authenticated fetches, which is required now that
/course/downloads/* is a gated function rather than a static path.

It loads after auth.js because it calls CourseAuth.getToken().

Run from the repository root:

    python3 tools/wire_course_downloads.py
"""

import glob
import re

TAG = '<script src="downloads.js"></script>'
AFTER = '<script src="auth.js"></script>'


def main():
    changed = 0
    for path in sorted(glob.glob("course/*.html")):
        with open(path, encoding="utf-8") as fh:
            html = fh.read()

        if 'class="dl-btn"' not in html:
            continue
        if TAG in html:
            continue
        if AFTER not in html:
            print(f"  {path:<34} SKIPPED — no auth.js to anchor to")
            continue

        html = html.replace(AFTER, AFTER + "\n  " + TAG, 1)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(html)
        print(f"  {path:<34} wired")
        changed += 1

    print(f"\n{changed} page(s) updated")


if __name__ == "__main__":
    main()
