#!/usr/bin/env python3
"""
Replace every page's <nav id="mainNav"> with one canonical block.

Two problems this solves:

1. The four service pages (ai-integration, sops-training, lsm,
   menu-engineering) each had exactly ONE inbound internal link, from
   services.html. They were effectively orphaned despite being the highest
   commercial-intent pages on the site. They now sit in a Services dropdown
   on all 25 navigable pages.

2. index.html shipped a 5-link nav while every other page had 14. The
   homepage — the page that accumulates the most external authority — was
   passing on the least.

login.html is deliberately dropped from the nav: it is a noindex auth page
that was collecting 32 internal links, more than any service page. It moves
to the footer, where course customers can still find it.

Six different nav variants existed before this ran. Run from the repo root:

    python3 tools/standardise_nav.py
"""

import glob
import re

NAV = """<nav id="mainNav">
          <ul>
            <li><a href="{p}profit-leak-snapshot.html" class="nav-cta">Snapshot</a></li>
            <li class="nav-dropdown">
              <a href="{p}services.html">Services</a>
              <div class="dropdown-menu">
                <a href="{p}services.html">All Services</a>
                <a href="{p}menu-engineering.html">Menu Engineering</a>
                <a href="{p}sops-training.html">SOPs &amp; Training Systems</a>
                <a href="{p}lsm.html">Local Store Marketing</a>
                <a href="{p}ai-integration.html">AI Integration</a>
              </div>
            </li>
            <li><a href="{p}advisory.html">Advisory</a></li>
            <li class="nav-dropdown">
              <a href="#" onclick="return false;">Insights</a>
              <div class="dropdown-menu">
                <a href="{p}blog.html">Blog &amp; Playbooks</a>
                <a href="{p}catering-profit.html">Catering Profit System</a>
              </div>
            </li>
            <li class="nav-dropdown">
              <a href="#" onclick="return false;">Resources</a>
              <div class="dropdown-menu">
                <a href="{p}audit.html">Restaurant Ops Audit</a>
                <a href="{p}food-truck-audit.html">Food Truck Launch Audit</a>
                <a href="{p}playbook.html">90-Day Profit Playbook</a>
                <a href="{p}virginia-neighbors.html">Virginia Neighbors Directory</a>
              </div>
            </li>
            <li><a href="{p}about.html">About</a></li>
            <li><a href="{p}contact.html">Contact</a></li>
          </ul>
        </nav>"""

NAV_RE = re.compile(r'<nav id="mainNav">.*?</nav>', re.S | re.I)


def main():
    changed = 0
    for path in sorted(glob.glob("**/*.html", recursive=True)):
        if "node_modules" in path:
            continue
        with open(path, encoding="utf-8") as fh:
            html = fh.read()
        if not NAV_RE.search(html):
            continue

        prefix = "../" if "/" in path else ""
        new = NAV.format(p=prefix)
        updated = NAV_RE.sub(lambda _: new, html, count=1)

        if updated != html:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(updated)
            print(f"  {path}")
            changed += 1

    print(f"\n{changed} nav block(s) standardised.")


if __name__ == "__main__":
    main()
