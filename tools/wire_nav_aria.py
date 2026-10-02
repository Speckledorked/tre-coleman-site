#!/usr/bin/env python3
"""
Load nav-aria.js on every page that has the mobile navigation.

The script keeps aria-expanded in step with the `active` class. It is wired in
rather than folded into the existing inline handlers because those come in two
shapes across the site, and editing 35 inline blocks by hand is how this
repository got six nav variants in the first place.

Placed immediately before </body> with `defer`, so it never blocks rendering
and runs after the markup it observes exists.

Run from the repository root:

    python3 tools/wire_nav_aria.py
"""

import glob
import os
import re

TAG = '<script src="/nav-aria.js" defer></script>'


def main():
    changed = 0
    for path in sorted(glob.glob("*.html") + glob.glob("blog/*.html")
                       + glob.glob("course/*.html")):
        with open(path, encoding="utf-8") as fh:
            page = fh.read()

        if "mobileMenuToggle" not in page:
            continue          # no mobile nav on this page
        if TAG in page:
            continue          # already wired

        if "</body>" not in page:
            print(f"  {path:<44} SKIPPED — no </body>")
            continue

        page = page.replace("</body>", f"{TAG}\n</body>", 1)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(page)
        print(f"  {os.path.basename(path):<44} wired")
        changed += 1

    print(f"\n{changed} page(s) updated")


if __name__ == "__main__":
    main()
