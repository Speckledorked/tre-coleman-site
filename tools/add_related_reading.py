#!/usr/bin/env python3
"""
Add a "Related reading" block to every article.

The checker flagged all 11 articles with 1-2 inbound internal links. They were
reachable from blog.html and almost nowhere else, which is the same orphaning
problem the audit found on the service pages — just one level down.

Links are chosen by topic cluster (SEO_AUDIT.md section 4.4), not round-robin,
so each one is a link a reader might actually follow:

  profitability   busy-but-not-profitable (pillar), profit-leaks, p-and-l,
                  labor-cost, menu-engineering-guide
  catering        scaling-a-catering-business
  systems         systems-for-growth, sop-templates
  leadership      fractional-coo-for-restaurants, fractional-coo-vs-consultant,
                  consultant-cost

Run from the repository root:

    python3 tools/add_related_reading.py
"""

import os
import re

TITLES = {
    "busy-but-not-profitable.html":
        "Why Your Restaurant Is Busy But Not Profitable",
    "restaurant-profit-leaks.html":
        "How to Find and Fix Restaurant Profit Leaks",
    "restaurant-profit-and-loss.html":
        "The Restaurant P&amp;L, Line by Line",
    "restaurant-labor-cost.html":
        "How to Lower Restaurant Labor Cost",
    "menu-engineering-guide.html":
        "Menu Engineering Guide for Restaurant Owners",
    "restaurant-systems-for-growth.html":
        "Restaurant Systems That Support Real Growth",
    "restaurant-sop-templates.html":
        "Restaurant SOPs: What to Document First",
    "fractional-coo-for-restaurants.html":
        "What a Fractional COO Does for Restaurants",
    "fractional-coo-vs-consultant.html":
        "Fractional COO vs Restaurant Consultant",
    "restaurant-consultant-cost.html":
        "How Much Does a Restaurant Consultant Cost?",
    "scaling-a-catering-business.html":
        "How to Scale a Catering Business Profitably",
}

# Each article -> three siblings a reader of it would plausibly want next.
RELATED = {
    "busy-but-not-profitable.html": [
        "restaurant-profit-and-loss.html",
        "restaurant-labor-cost.html",
        "menu-engineering-guide.html",
    ],
    "restaurant-profit-leaks.html": [
        "busy-but-not-profitable.html",
        "restaurant-profit-and-loss.html",
        "restaurant-labor-cost.html",
    ],
    "restaurant-profit-and-loss.html": [
        "busy-but-not-profitable.html",
        "restaurant-labor-cost.html",
        "menu-engineering-guide.html",
    ],
    "restaurant-labor-cost.html": [
        "busy-but-not-profitable.html",
        "restaurant-sop-templates.html",
        "restaurant-profit-and-loss.html",
    ],
    "menu-engineering-guide.html": [
        "restaurant-profit-leaks.html",
        "restaurant-profit-and-loss.html",
        "busy-but-not-profitable.html",
    ],
    "restaurant-systems-for-growth.html": [
        "restaurant-sop-templates.html",
        "fractional-coo-for-restaurants.html",
        "busy-but-not-profitable.html",
    ],
    "restaurant-sop-templates.html": [
        "restaurant-systems-for-growth.html",
        "restaurant-labor-cost.html",
        "fractional-coo-for-restaurants.html",
    ],
    "fractional-coo-for-restaurants.html": [
        "fractional-coo-vs-consultant.html",
        "restaurant-consultant-cost.html",
        "restaurant-systems-for-growth.html",
    ],
    "fractional-coo-vs-consultant.html": [
        "restaurant-consultant-cost.html",
        "fractional-coo-for-restaurants.html",
        "busy-but-not-profitable.html",
    ],
    "restaurant-consultant-cost.html": [
        "fractional-coo-vs-consultant.html",
        "busy-but-not-profitable.html",
        "restaurant-profit-leaks.html",
    ],
    "scaling-a-catering-business.html": [
        "restaurant-labor-cost.html",
        "menu-engineering-guide.html",
        "restaurant-profit-and-loss.html",
    ],
}

CSS = """
      .related-reading {
        margin-top: 3rem;
        padding-top: 1.75rem;
        border-top: 2px solid var(--bg-cream);
      }
      .related-reading h2 {
        font-size: 1.25rem;
        margin-bottom: 1rem;
        color: var(--primary-navy);
      }
      .related-reading ul {
        list-style: none;
        margin: 0;
        padding: 0;
      }
      .related-reading li {
        margin-bottom: 0.6rem;
        line-height: 1.5;
      }
      .related-reading a {
        color: var(--primary-navy);
        text-decoration: underline;
        text-underline-offset: 2px;
        font-weight: 600;
      }
      .related-reading a:hover { color: var(--accent-gold-text); }
"""


def main():
    changed = 0
    for slug, siblings in RELATED.items():
        path = os.path.join("blog", slug)
        if not os.path.exists(path):
            print(f"  SKIP (missing) {path}")
            continue
        with open(path, encoding="utf-8") as fh:
            html = fh.read()
        if 'class="related-reading"' in html:
            print(f"  skip (already done) {path}")
            continue

        items = "\n".join(
            f'<li><a href="{s}">{TITLES[s]}</a></li>'
            for s in siblings if s != slug and s in TITLES
        )
        block = (
            '<nav class="related-reading" aria-label="Related articles">\n'
            "<h2>Related reading</h2>\n<ul>\n" + items + "\n</ul>\n</nav>\n"
        )

        # Place it after the article body, before the closing CTA.
        marker = '<div class="cta-section">'
        idx = html.rfind(marker)
        if idx == -1:
            print(f"  SKIP (no CTA anchor) {path}")
            continue
        html = html[:idx] + block + html[idx:]

        close = html.rfind("</style>")
        if close != -1 and ".related-reading" not in html[:close]:
            html = html[:close] + CSS + html[close:]

        with open(path, "w", encoding="utf-8") as fh:
            fh.write(html)
        print(f"  {path}  +{len(siblings)} related links")
        changed += 1

    print(f"\n{changed} article(s) updated")


if __name__ == "__main__":
    main()
