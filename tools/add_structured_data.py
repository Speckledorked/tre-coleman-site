#!/usr/bin/env python3
"""
Add the structured data the site was missing, plus the visible content each
schema type must correspond to.

Google requires that structured data describe what a user actually sees on
the page. So this adds visible bylines and dates alongside BlogPosting, not
just the markup.

  * BlogPosting on all 6 article pages, with a visible author byline and
    publication date. Dates come from git history (first commit = published,
    most recent = modified) rather than being invented.
  * BreadcrumbList on article and service pages, with visible breadcrumbs
  * Service on each service page, reusing the same @id already referenced
    from services.html so the entity graph stays consistent
  * WebSite on the homepage (no SearchAction — the site has no search)
  * areaServed expanded from a bare country to the named Virginia markets

Run from the repository root:

    python3 tools/add_structured_data.py
"""

import json
import re
import subprocess

AUTHOR_ID = "https://trecoleman.com/#person"
BUSINESS_ID = "https://trecoleman.com/#business"
SITE = "https://trecoleman.com"
OG_CARD = f"{SITE}/images/og-card.jpg"

ARTICLES = {
    "blog/blog_post_1_profit_leaks_rewritten.html": (
        "Unmasking the Hidden Costs: How to Identify and Plug Profit Leaks in Your Restaurant",
        "Operations",
    ),
    "blog/blog_post_2_systems_growth_rewritten.html": (
        "Beyond the Daily Grind: Implementing Systems for Sustainable Restaurant Growth",
        "Operations",
    ),
    "blog/blog_post_3_menu_engineering_rewritten.html": (
        "Maximizing My Menu's Potential: A Guide to Restaurant Menu Engineering",
        "Operations",
    ),
    "blog/blog_post_4_fractional_coo_rewritten.html": (
        "The Strategic Advantage: How Fractional COO Services Elevate Restaurant Operations",
        "Operations",
    ),
    "blog/blog_post_5_catering_profitability_rewritten.html": (
        "From Food Truck to Empire: Scaling My Catering Business Profitably",
        "Operations",
    ),
    "unreasonably-optimistic.html": (
        "Unreasonably Optimistic",
        "Leadership",
    ),
}

SERVICES = {
    "menu-engineering.html": "Menu Engineering",
    "sops-training.html": "SOPs & Training Systems",
    "lsm.html": "Local Store Marketing",
    "ai-integration.html": "AI Integration",
    "advisory.html": "Advisory & Fractional COO",
    "profit-leak-snapshot.html": "Profit Leak Snapshot",
}

VIRGINIA_MARKETS = [
    "Charlottesville", "Richmond", "Fredericksburg",
    "Harrisonburg", "Louisa",
]


def git_dates(path):
    """(first commit date, most recent commit date) as YYYY-MM-DD."""
    out = subprocess.run(
        ["git", "log", "--format=%cs", "--", path],
        capture_output=True, text=True, check=True,
    ).stdout.split()
    return (out[-1], out[0]) if out else (None, None)


def ld(obj):
    return ('<script type="application/ld+json">\n'
            + json.dumps(obj, indent=2, ensure_ascii=False)
            + "\n</script>\n")


def inject_head(html, block):
    return re.sub(r"</head>", block + "</head>", html, count=1, flags=re.I)


# ---------------------------------------------------------------- articles

def article_schema(path, title, published, modified):
    depth = "blog/" if "/" in path else ""
    url = f"{SITE}/{depth}{path.split('/')[-1]}"
    desc = ""
    return {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": title,
        "url": url,
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "datePublished": published,
        "dateModified": modified,
        "author": {"@id": AUTHOR_ID},
        "publisher": {"@id": BUSINESS_ID},
        "image": OG_CARD,
        "inLanguage": "en-US",
    }


def breadcrumbs(items):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i,
             "name": name, "item": url}
            for i, (name, url) in enumerate(items, 1)
        ],
    }


def visible_crumbs(items, current):
    links = " <span aria-hidden=\"true\">›</span> ".join(
        f'<a href="{href}">{name}</a>' for name, href in items
    )
    return (
        '<nav class="breadcrumbs" aria-label="Breadcrumb">'
        f'{links} <span aria-hidden="true">›</span> '
        f'<span aria-current="page">{current}</span>'
        "</nav>\n"
    )


def do_article(path):
    title, category = ARTICLES[path]
    published, modified = git_dates(path)
    if not published:
        print(f"  SKIP (no git history) {path}")
        return

    with open(path, encoding="utf-8") as fh:
        html = fh.read()
    if "BlogPosting" in html:
        print(f"  skip (already done) {path}")
        return

    slug = path.split("/")[-1]
    up = "../" if "/" in path else ""
    is_blog = "/" in path

    crumb_items = [("Home", f"{up}index.html")]
    if is_blog:
        crumb_items.append(("Blog", f"{up}blog.html"))
    else:
        crumb_items.append(("Blog", "blog.html"))

    schema_items = [("Home", f"{SITE}/")]
    schema_items.append(("Blog", f"{SITE}/blog.html"))
    schema_items.append((title, f"{SITE}/{'blog/' if is_blog else ''}{slug}"))

    html = inject_head(
        html,
        ld(article_schema(path, title, published, modified))
        + ld(breadcrumbs(schema_items)),
    )

    # Visible byline + date, replacing the bare "Category • N min read".
    nice = f"{published}"
    html = re.sub(
        r'<div class="post-meta">([^<]*)</div>',
        lambda m: (
            '<div class="post-meta">'
            f'By <a rel="author" href="{up}about.html">Tre Coleman</a> '
            f'&bull; <time datetime="{published}">{nice}</time> '
            f'&bull; {m.group(1).strip()}'
            "</div>"
        ),
        html,
        count=1,
    )

    # Visible breadcrumbs above the article.
    crumbs = visible_crumbs(crumb_items, title)
    if 'class="breadcrumbs"' not in html:
        html = re.sub(
            r'(<main id="main-content">\s*)',
            lambda m: m.group(1) + crumbs,
            html,
            count=1,
        )

    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"  {path}  published={published} modified={modified}")


# ---------------------------------------------------------------- services

def do_service(path, name):
    with open(path, encoding="utf-8") as fh:
        html = fh.read()
    if "BreadcrumbList" in html:
        print(f"  skip (already done) {path}")
        return

    url = f"{SITE}/{path}"
    crumbs_schema = breadcrumbs([
        ("Home", f"{SITE}/"),
        ("Services", f"{SITE}/services.html"),
        (name, url),
    ])
    html = inject_head(html, ld(crumbs_schema))

    crumbs = visible_crumbs(
        [("Home", "index.html"), ("Services", "services.html")], name
    )
    if 'class="breadcrumbs"' not in html:
        html = re.sub(
            r'(<main id="main-content">\s*)',
            lambda m: m.group(1) + crumbs,
            html,
            count=1,
        )

    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"  {path}")


# ---------------------------------------------------------------- homepage

def do_homepage():
    path = "index.html"
    with open(path, encoding="utf-8") as fh:
        html = fh.read()

    if '"@type": "WebSite"' not in html:
        html = inject_head(html, ld({
            "@context": "https://schema.org",
            "@type": "WebSite",
            "@id": f"{SITE}/#website",
            "url": f"{SITE}/",
            "name": "Tre Coleman Consulting",
            "publisher": {"@id": BUSINESS_ID},
            "inLanguage": "en-US",
        }))

    # Widen areaServed from a bare country to the named Virginia markets.
    old = '''"areaServed": {
            "@type": "Country",
            "name": "United States"
          },'''
    new = '''"areaServed": [
            { "@type": "Country", "name": "United States" },
            { "@type": "State", "name": "Virginia" },
''' + ",\n".join(
        '            { "@type": "City", "name": "%s", '
        '"containedInPlace": { "@type": "State", "name": "Virginia" } }' % m
        for m in VIRGINIA_MARKETS
    ) + '''
          ],'''
    if old in html:
        html = html.replace(old, new, 1)

    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("  index.html  (WebSite + named areaServed)")


def main():
    print("Articles:")
    for path in ARTICLES:
        do_article(path)
    print("\nService pages:")
    for path, name in SERVICES.items():
        do_service(path, name)
    print("\nHomepage:")
    do_homepage()


if __name__ == "__main__":
    main()
