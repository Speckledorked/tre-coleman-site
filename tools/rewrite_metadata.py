#!/usr/bin/env python3
"""
Apply the title and meta-description rewrites from SEO_AUDIT.md section 3.

Fixes three problems the audit found:

  * Six descriptions ran 165-212 characters and truncated in results
  * Titles were brand-heavy ("Menu Engineering | Tre Coleman" at 30 chars)
    and spent budget on a brand nobody searches for yet, instead of the
    qualifiers buyers actually type
  * Two titles used a smart apostrophe ("Tre' Coleman") inconsistently with
    every other title on the site

Titles target ~50-60 characters, descriptions ~140-160.

Run from the repository root:

    python3 tools/rewrite_metadata.py
"""

import re

# path: (title, description)
REWRITES = {
    "index.html": (
        "Restaurant Operations Consultant in Virginia | Tre Coleman",
        "Independent restaurant, food truck, and catering operators: find and "
        "fix the profit leaks in labor, menu, and systems. Virginia-based, "
        "working nationwide.",
    ),
    "services.html": (
        "Restaurant &amp; Food Service Consulting Services | Tre Coleman",
        "AI workflows, SOPs and training, menu engineering, local marketing, "
        "and fractional ops support for independent restaurant and catering "
        "operators.",
    ),
    "advisory.html": (
        "Fractional COO for Restaurants &amp; Food Trucks | Tre Coleman",
        "Weekly strategy calls, KPI reviews, and on-call operator support for "
        "$1M+ restaurant and catering operations. $2,000/mo, no long-term "
        "contract.",
    ),
    "profit-leak-snapshot.html": (
        "Restaurant Profit Leak Snapshot | 90-Minute Diagnostic",
        "A 90-minute session on your P&amp;L, labor, and item mix. Leave with "
        "your top 3 profit leaks priced in dollars and a prioritized fix "
        "list. $350.",
    ),
    "contact.html": (
        "Contact a Restaurant Operations Consultant | Tre Coleman",
        "Tell me where your operation is bottlenecked and get a practical "
        "first step. Book a $350 Profit Leak Snapshot or send a note about "
        "your operation.",
    ),
    "ai-integration.html": (
        "AI Automation for Restaurant Operations | Tre Coleman",
        "Cut manager admin time with practical AI workflows for scheduling, "
        "prep, reporting, and training. Built by an operator, rolled out "
        "without floor disruption.",
    ),
    "sops-training.html": (
        "Restaurant SOPs &amp; Staff Training Systems | Tre Coleman",
        "Role scorecards, opening and closing checklists, and 30-60-90 "
        "onboarding plans that end tribal knowledge and shorten new-hire ramp "
        "time.",
    ),
    "lsm.html": (
        "Local Store Marketing for Restaurants | Tre Coleman",
        "12-week local marketing calendars, community partnerships, and "
        "trackable offers that fill slow shifts for restaurants and food "
        "trucks.",
    ),
    "menu-engineering.html": (
        "Menu Engineering for Independent Restaurants | Tre Coleman",
        "Contribution margin analysis, menu redesign, and server training "
        "that shift your mix toward high-profit items without "
        "across-the-board price hikes.",
    ),
    "blog.html": (
        "Restaurant Operations Insights &amp; Playbooks | Tre Coleman",
        "Practical operations, profitability, and marketing playbooks for "
        "independent restaurant, food truck, and catering operators. No "
        "theory, just systems.",
    ),
    "about.html": (
        "About Tre Coleman | Restaurant Operations Consultant",
        "10+ years running multi-unit restaurant, catering, and food truck "
        "operations. Operator-first consulting for owners who need systems, "
        "not slide decks.",
    ),
    "audit.html": (
        "Free Restaurant Operations Audit (10-Minute Self-Check)",
        "Score your operation across food cost, labor, systems, training, and "
        "menu. Get benchmarks and a prioritized fix list in about ten "
        "minutes.",
    ),
    "food-truck-audit.html": (
        "Free Food Truck Launch Readiness Audit | Tre Coleman",
        "Score your truck across menu, operations, permits, pricing, and "
        "marketing before you open. Get your readiness score and what to fix "
        "first.",
    ),
    "playbook.html": (
        "Free 90-Day Restaurant Profit Playbook | Tre Coleman",
        "A week-by-week plan for independent operators to find profit leaks "
        "and fix labor, menu pricing, and daily operations. Free, no fluff.",
    ),
    "catering-profit.html": (
        "Catering Profit System: Course for Catering Operators",
        "A self-paced course on catering labor, pricing, food cost, "
        "logistics, and cash flow — the systems that turn catering revenue "
        "into real profit. $67.",
    ),
    "chat.html": (
        "Free AI Restaurant Operations Assistant | Tre Coleman",
        "Ask an AI assistant trained on restaurant operations about labor, "
        "menu engineering, SOPs, and scheduling. Free to try.",
    ),
    "virginia-neighbors.html": (
        "Virginia Local Business Directory | Tre Coleman",
        "Find Virginia restaurants, food trucks, caterers, and local service "
        "businesses — or list your own and connect with neighbors who need "
        "you.",
    ),
    "unreasonably-optimistic.html": (
        "Unreasonably Optimistic: Operating Through Uncertainty",
        "Why the operators who turn things around aren't the most experienced "
        "— they're the ones who keep moving before they feel certain.",
    ),
    "blog/restaurant-profit-leaks.html": (
        "How to Find &amp; Fix Restaurant Profit Leaks | Tre Coleman",
        "Where independent restaurants quietly lose margin — labor, item mix, "
        "waste, and cash flow — and the checks that surface each one.",
    ),
    "blog/restaurant-systems-for-growth.html": (
        "Restaurant Systems That Support Real Growth | Tre Coleman",
        "Move past daily firefighting. The SOPs, scheduling structure, and "
        "financial tracking that let an operation grow without the owner in "
        "the room.",
    ),
    "blog/menu-engineering-guide.html": (
        "Menu Engineering Guide for Restaurant Owners | Tre Coleman",
        "How to map contribution margin against popularity, find the items "
        "quietly costing you money, and redesign your menu around what "
        "actually pays.",
    ),
    "blog/fractional-coo-for-restaurants.html": (
        "What a Fractional COO Does for Restaurants | Tre Coleman",
        "What a fractional COO actually handles week to week, when an "
        "operation is ready for one, and how it compares to a full-time hire "
        "on cost.",
    ),
    "blog/scaling-a-catering-business.html": (
        "How to Scale a Catering Business Profitably | Tre Coleman",
        "More catering volume without pricing, staffing, and logistics "
        "systems means more revenue and less profit. Here's the order to "
        "build them in.",
    ),
}

DESC_ATTR = re.compile(
    r'<meta\s+(?:name="description"\s+content="([^"]*)"'
    r'|content="([^"]*)"\s+name="description")\s*/?>',
    re.I | re.S,
)
DESC_MULTILINE = re.compile(
    r'<meta\s*\n\s*name="description"\s*\n\s*content="[^"]*"\s*/?>',
    re.I,
)


def plain(text):
    return text.replace("&amp;", "&")


def main():
    for path, (title, desc) in REWRITES.items():
        with open(path, encoding="utf-8") as fh:
            html = fh.read()
        before = html

        html = re.sub(
            r"<title>.*?</title>",
            lambda _: f"<title>{title}</title>",
            html, count=1, flags=re.S,
        )

        new_desc = f'<meta name="description" content="{plain(desc)}" />'
        if DESC_MULTILINE.search(html):
            html = DESC_MULTILINE.sub(lambda _: new_desc, html, count=1)
        else:
            html = DESC_ATTR.sub(lambda _: new_desc, html, count=1)

        # Keep the social title in step with the page title.
        for prop in ("og:title", "twitter:title"):
            attr = "property" if prop.startswith("og") else "name"
            html = re.sub(
                rf'<meta\s+{attr}="{prop}"\s+content="[^"]*"\s*/?>',
                lambda _: f'<meta {attr}="{prop}" content="{title}" />',
                html, count=1,
            )
            html = re.sub(
                rf'<meta\s+content="[^"]*"\s+{attr}="{prop}"\s*/?>',
                lambda _: f'<meta {attr}="{prop}" content="{title}" />',
                html, count=1,
            )

        if html != before:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(html)
            print(f"  {len(plain(title)):3d} / {len(plain(desc)):3d}   {path}")


if __name__ == "__main__":
    main()
