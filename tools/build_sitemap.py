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
    ("/blog/busy-but-not-profitable.html",
     "blog/busy-but-not-profitable.html",                           "0.7", "yearly"),
    ("/blog/restaurant-profit-and-loss.html",
     "blog/restaurant-profit-and-loss.html",                        "0.7", "yearly"),
    ("/blog/restaurant-labor-cost.html",
     "blog/restaurant-labor-cost.html",                             "0.7", "yearly"),
    ("/blog/restaurant-sop-templates.html",
     "blog/restaurant-sop-templates.html",                          "0.7", "yearly"),
    ("/blog/fractional-coo-vs-consultant.html",
     "blog/fractional-coo-vs-consultant.html",                      "0.7", "yearly"),
    ("/blog/restaurant-consultant-cost.html",
     "blog/restaurant-consultant-cost.html",                        "0.7", "yearly"),
    ("/blog/restaurant-profit-leaks.html",
     "blog/restaurant-profit-leaks.html",                "0.6", "yearly"),
    ("/blog/restaurant-systems-for-growth.html",
     "blog/restaurant-systems-for-growth.html",              "0.6", "yearly"),
    ("/blog/menu-engineering-guide.html",
     "blog/menu-engineering-guide.html",            "0.6", "yearly"),
    ("/blog/fractional-coo-for-restaurants.html",
     "blog/fractional-coo-for-restaurants.html",              "0.6", "yearly"),
    ("/blog/scaling-a-catering-business.html",
     "blog/scaling-a-catering-business.html",      "0.6", "yearly"),
    ("/blog/how-to-price-catering-jobs.html",
     "blog/how-to-price-catering-jobs.html",       "0.6", "yearly"),
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


def refuse_if_history_is_useless(dates):
    """Refuse when every page resolved to the same commit, in a shallow clone.

    `git log -1 -- <path>` in a depth-1 clone can only return the one commit it
    has, so every page resolves to the same date and the sitemap comes out
    uniformly stamped with whenever the clone happened. Nothing errors; the
    output is simply wrong, which is the worst failure mode a generator has.

    It bit CI rather than a person: the workflow used the default
    fetch-depth: 1 and its sitemap check compared the committed file against
    34 URLs all dated today. That matched by luck whenever regeneration and CI
    fell on the same day, and stopped matching the first time a session crossed
    midnight.

    The test is the symptom, not `--is-shallow-repository`. A truncated clone
    is usually fine: this very checkout reports shallow while holding 189
    commits and resolving per-file dates correctly. What is never fine is a
    shallow clone in which every single page collapsed onto one date, because
    that is the signature of history too short to answer the question.
    """
    if len(dates) < 2 or len(set(dates)) != 1:
        return
    shallow = subprocess.run(
        ["git", "rev-parse", "--is-shallow-repository"],
        capture_output=True, text=True,
    ).stdout.strip()
    if shallow != "true":
        return          # genuinely one commit touched everything; believable
    sys.exit(
        f"refusing to write a sitemap: all {len(dates)} pages resolved to "
        f"{dates[0]} in a shallow clone.\n"
        "<lastmod> comes from per-file git history, and this clone has too "
        "little of it to tell the pages apart.\n"
        "Fix: `git fetch --unshallow`, or set fetch-depth: 0 on "
        "actions/checkout."
    )


def main():
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    unknown = []
    collected = []
    for url, path, priority, changefreq in PAGES:
        date = last_modified(path)
        if date is None:
            unknown.append(path)
            continue
        collected.append(date)
        lines += [
            "  <url>",
            f"    <loc>{SITE}{url}</loc>",
            f"    <lastmod>{date}</lastmod>",
            f"    <changefreq>{changefreq}</changefreq>",
            f"    <priority>{priority}</priority>",
            "  </url>",
        ]
    lines.append("</urlset>")

    # Check before writing: a wrong sitemap on disk is worse than none.
    refuse_if_history_is_useless(collected)

    with open("sitemap.xml", "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    print(f"Wrote sitemap.xml with {len(PAGES) - len(unknown)} URLs.")
    if unknown:
        print("No git history found (omitted):", ", ".join(unknown), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
