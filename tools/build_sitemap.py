#!/usr/bin/env python3
"""
Regenerate sitemap.xml with honest <lastmod> values taken from git history.

Run from the repository root:

    python3 tools/build_sitemap.py

<lastmod> is read from each file's most recent commit date, so it stays
truthful automatically. Never hand-edit the dates in sitemap.xml — a stale or
invented <lastmod> is worse than none at all, because Google learns to
distrust the signal sitewide.
"""

import subprocess
import sys

SITE = "https://trecoleman.com"

# (url path, file path, priority, changefreq)
PAGES = [
    ("/",                             "index.html",                 "1.0", "weekly"),
    ("/services.html",                "services.html",              "0.9", "monthly"),
    ("/advisory.html",                "advisory.html",              "0.9", "monthly"),
    ("/profit-leak-snapshot.html",    "profit-leak-snapshot.html",  "0.9", "monthly"),
    ("/food-truck-consulting.html",   "food-truck-consulting.html", "0.8", "monthly"),
    ("/catering-consulting.html",     "catering-consulting.html",   "0.8", "monthly"),
    ("/virginia-restaurant-consulting.html",
     "virginia-restaurant-consulting.html",                         "0.8", "monthly"),
    ("/ai-integration.html",          "ai-integration.html",        "0.8", "monthly"),
    ("/sops-training.html",           "sops-training.html",         "0.8", "monthly"),
    ("/lsm.html",                     "lsm.html",                   "0.8", "monthly"),
    ("/menu-engineering.html",        "menu-engineering.html",      "0.8", "monthly"),
    ("/about.html",                   "about.html",                 "0.8", "monthly"),
    ("/contact.html",                 "contact.html",               "0.8", "monthly"),
    ("/audit.html",                   "audit.html",                 "0.8", "monthly"),
    ("/food-truck-audit.html",        "food-truck-audit.html",      "0.8", "monthly"),
    ("/catering-profit.html",         "catering-profit.html",       "0.7", "monthly"),
    ("/playbook.html",                "playbook.html",              "0.7", "monthly"),
    ("/blog.html",                    "blog.html",                  "0.7", "weekly"),
    ("/blog/blog_post_1_profit_leaks_rewritten.html",
     "blog/blog_post_1_profit_leaks_rewritten.html",                "0.6", "yearly"),
    ("/blog/blog_post_2_systems_growth_rewritten.html",
     "blog/blog_post_2_systems_growth_rewritten.html",              "0.6", "yearly"),
    ("/blog/blog_post_3_menu_engineering_rewritten.html",
     "blog/blog_post_3_menu_engineering_rewritten.html",            "0.6", "yearly"),
    ("/blog/blog_post_4_fractional_coo_rewritten.html",
     "blog/blog_post_4_fractional_coo_rewritten.html",              "0.6", "yearly"),
    ("/blog/blog_post_5_catering_profitability_rewritten.html",
     "blog/blog_post_5_catering_profitability_rewritten.html",      "0.6", "yearly"),
    ("/unreasonably-optimistic.html", "unreasonably-optimistic.html", "0.6", "yearly"),
    ("/virginia-neighbors.html",      "virginia-neighbors.html",    "0.6", "monthly"),
    ("/chat.html",                    "chat.html",                  "0.5", "monthly"),
    ("/privacy.html",                 "privacy.html",               "0.3", "yearly"),
]


def last_modified(path):
    """Most recent commit date for a file, as YYYY-MM-DD."""
    out = subprocess.run(
        ["git", "log", "-1", "--format=%cs", "--", path],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return out or None


def main():
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    unknown = []
    for url, path, priority, changefreq in PAGES:
        date = last_modified(path)
        if date is None:
            unknown.append(path)
            continue
        lines += [
            "  <url>",
            f"    <loc>{SITE}{url}</loc>",
            f"    <lastmod>{date}</lastmod>",
            f"    <changefreq>{changefreq}</changefreq>",
            f"    <priority>{priority}</priority>",
            "  </url>",
        ]
    lines.append("</urlset>")

    with open("sitemap.xml", "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    print(f"Wrote sitemap.xml with {len(PAGES) - len(unknown)} URLs.")
    if unknown:
        print("No git history found (omitted):", ", ".join(unknown), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
