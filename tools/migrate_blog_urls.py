#!/usr/bin/env python3
"""
Rename the blog posts from filenames to real URL slugs.

The posts shipped as `/blog/blog_post_3_menu_engineering_rewritten.html`.
"blog_post_3" and "rewritten" are artefacts of how the files were produced,
not anything a reader or a search engine benefits from, and "rewritten" in a
public URL reads as unfinished work.

Doing this now is deliberate: the posts have almost no inbound links yet, so
the cost of changing URLs is close to zero. It only gets more expensive.

Old paths get 301 redirects in netlify.toml, so any existing link or index
entry still resolves.

Run from the repository root:

    python3 tools/migrate_blog_urls.py
"""

import glob
import os
import re
import subprocess

RENAMES = {
    "blog/blog_post_1_profit_leaks_rewritten.html":
        "blog/restaurant-profit-leaks.html",
    "blog/blog_post_2_systems_growth_rewritten.html":
        "blog/restaurant-systems-for-growth.html",
    "blog/blog_post_3_menu_engineering_rewritten.html":
        "blog/menu-engineering-guide.html",
    "blog/blog_post_4_fractional_coo_rewritten.html":
        "blog/fractional-coo-for-restaurants.html",
    "blog/blog_post_5_catering_profitability_rewritten.html":
        "blog/scaling-a-catering-business.html",
}

REDIRECT_BLOCK = """
# ---------------------------------------------------------------------------
# Blog URL migration (see tools/migrate_blog_urls.py)
# The posts originally shipped with generated filenames. These 301s keep any
# existing link, bookmark or index entry resolving to the new slug.
# ---------------------------------------------------------------------------
"""


def main():
    # 1. Rename, preserving git history.
    for old, new in RENAMES.items():
        if os.path.exists(old):
            subprocess.run(["git", "mv", old, new], check=True)
            print(f"  {old}\n    -> {new}")

    # 2. Update every reference across the site, including canonical/og:url.
    changed = 0
    for path in sorted(glob.glob("**/*.html", recursive=True)) + ["sitemap.xml"]:
        if "node_modules" in path or not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        before = text
        for old, new in RENAMES.items():
            text = text.replace(old, new)
            text = text.replace(old.split("/", 1)[1], new.split("/", 1)[1])
        if text != before:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text)
            changed += 1
    print(f"\n{changed} file(s) had references updated.")

    # 3. Add 301s.
    with open("netlify.toml", encoding="utf-8") as fh:
        toml = fh.read()
    if "Blog URL migration" not in toml:
        rules = REDIRECT_BLOCK + "\n".join(
            f'[[redirects]]\n'
            f'  from = "/{old}"\n'
            f'  to = "/{new}"\n'
            f'  status = 301\n'
            f'  force = true\n'
            for old, new in RENAMES.items()
        )
        toml = toml.rstrip() + "\n" + rules
        with open("netlify.toml", "w", encoding="utf-8") as fh:
            fh.write(toml)
        print("Added 301 redirects to netlify.toml.")


if __name__ == "__main__":
    main()
