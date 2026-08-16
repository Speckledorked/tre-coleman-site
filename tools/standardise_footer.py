#!/usr/bin/env python3
"""
Add a Services column to the sitewide footer.

The footer appears on all 24 content pages, so a Services column is the
second-biggest lever (after the nav) for getting internal links to the four
service pages that previously had one each.

Course Login moves here from the nav dropdown. It is a noindex auth page
that was collecting 32 internal links — more than any service page — which
told search engines it was among the most important pages on the site.

.footer-grid is `repeat(auto-fit, minmax(250px, 1fr))`, so the extra column
reflows without any CSS change.

Run from the repository root:

    python3 tools/standardise_footer.py
"""

import glob
import re

SERVICES = [
    ("profit-leak-snapshot.html", "Profit Leak Snapshot"),
    ("menu-engineering.html", "Menu Engineering"),
    ("sops-training.html", "SOPs &amp; Training"),
    ("lsm.html", "Local Store Marketing"),
    ("ai-integration.html", "AI Integration"),
    ("advisory.html", "Fractional COO"),
]

QUICK = [
    ("services.html", "All Services"),
    ("about.html", "About"),
    ("blog.html", "Blog"),
    ("catering-profit.html", "Catering Course"),
    ("virginia-neighbors.html", "Virginia Neighbors"),
    ("contact.html", "Contact"),
    ("login.html", "Course Login"),
]

BLOCK = """<div class="footer-section">
            <h4>Services</h4>
            <ul>
{services}
            </ul>
          </div>

          <div class="footer-section">
            <h4>Quick Links</h4>
            <ul>
{quick}
            </ul>
          </div>"""

# The whole <div class="footer-section"> that holds Quick Links.
TARGET = re.compile(
    r'<div class="footer-section">\s*<h4>Quick Links</h4>.*?</ul>\s*</div>',
    re.S | re.I,
)


def items(entries, prefix):
    return "\n".join(
        f'              <li><a href="{prefix}{href}">{label}</a></li>'
        for href, label in entries
    )


def main():
    changed = 0
    for path in sorted(glob.glob("**/*.html", recursive=True)):
        if "node_modules" in path:
            continue
        with open(path, encoding="utf-8") as fh:
            html = fh.read()
        if not TARGET.search(html):
            continue
        if "<h4>Services</h4>" in html:
            continue  # already done

        prefix = "../" if "/" in path else ""
        block = BLOCK.format(
            services=items(SERVICES, prefix),
            quick=items(QUICK, prefix),
        )
        updated = TARGET.sub(lambda _: block, html, count=1)

        if updated != html:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(updated)
            print(f"  {path}")
            changed += 1

    print(f"\n{changed} footer(s) updated.")


if __name__ == "__main__":
    main()
