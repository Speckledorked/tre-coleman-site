#!/usr/bin/env python3
"""
Generate a new blog post from the existing post shell.

Reuses menu-engineering-guide.html's head, nav, styles and footer so a new
article is structurally identical to the existing ones, then swaps in the
metadata, BlogPosting/BreadcrumbList schema, and body copy.

Run from the repository root:

    python3 tools/build_article.py
"""

import json
import re

SHELL = "blog/menu-engineering-guide.html"
SITE = "https://trecoleman.com"
OG_CARD = f"{SITE}/images/og-card.jpg"
OG_ALT = ("Tre Coleman — restaurant operations consulting for restaurants, "
          "food trucks, and catering companies")

SLUG = "blog/restaurant-consultant-cost.html"
TITLE = "How Much Does a Restaurant Consultant Cost? | Tre Coleman"
OG_TITLE = "How Much Does a Restaurant Consultant Cost?"
H1 = "How Much Does a Restaurant Consultant Cost?"
DESCRIPTION = ("What restaurant consultants actually charge, how the common "
               "pricing models differ, and how to tell whether an engagement "
               "will pay for itself.")
PUBLISHED = "2026-08-16"
READ_TIME = "8 min read"
CATEGORY = "Operations"

BODY = """
<h2>The short answer</h2>
<p>
  Most restaurant consulting in the United States falls into four pricing shapes: a paid
  diagnostic in the <strong>$300–$1,500</strong> range, hourly work at roughly
  <strong>$150–$400/hour</strong>, scoped projects from around <strong>$2,500</strong> to
  <strong>$50,000</strong> depending on breadth, and monthly retainers that generally start
  near <strong>$2,000/month</strong> and climb from there with the size of the operation.
</p>
<p>
  Those are wide bands, and the width is the point. "Restaurant consultant" covers people who
  design menus, people who fix labor models, people who run marketing, and people who broker
  equipment. The number only becomes meaningful once you know which problem you are buying a
  solution to.
</p>
<p>
  For transparency, since it is unusual for a consulting site to publish this: the diagnostic
  here is <a href="../profit-leak-snapshot.html">$350</a>, project work runs
  <strong>$2,500–$50,000</strong> scoped to the problem, and
  <a href="../advisory.html">ongoing advisory</a> is <strong>$2,000/month</strong>. Those are
  the same numbers on the services pages, not a range invented for an article.
</p>

<h2>Why so few consultants publish a price</h2>
<p>
  Two honest reasons and one less honest one.
</p>
<p>
  The honest ones: scope genuinely varies, and a rebuild of a labor model for a single
  location is not comparable to a multi-unit SOP rollout. And consultants who work on
  retainer often price against the size of the operation, because a $6M business consumes
  more of a week than an $800K one.
</p>
<p>
  The less honest one: a hidden price means the number can be set after the discovery call,
  once the consultant has a read on what you can afford. If a consultant will not give you a
  band before a sales call, that is worth noticing.
</p>

<h2>The four pricing models, and when each is right</h2>

<h3>1. The paid diagnostic ($300–$1,500)</h3>
<p>
  A fixed-scope session where someone reviews your numbers and tells you what is wrong. Good
  diagnostics require preparation — typically several weeks of P&amp;Ls, labor reports, and
  item-level sales data — because without them the session becomes a conversation about
  symptoms rather than causes.
</p>
<p>
  <strong>Right when:</strong> you know something is wrong but not what. You are profitable on
  paper and not in the bank. You want a second read before committing to a bigger engagement.
</p>
<p>
  <strong>Wrong when:</strong> you already know the diagnosis and need execution. Paying for a
  diagnostic to confirm what you have known for six months is an expensive way to feel
  validated.
</p>

<h3>2. Hourly ($150–$400/hour)</h3>
<p>
  Straightforward, and the most common structure for advisory conversations and one-off
  questions.
</p>
<p>
  <strong>Right when:</strong> you have a specific, bounded question — a lease review, a
  pricing sanity check, a second opinion on a hire.
</p>
<p>
  <strong>Wrong when:</strong> the work is open-ended. Hourly billing puts you and the
  consultant on opposite sides of the clock, which is a bad structure for anything that
  requires digging.
</p>

<h3>3. Project-based ($2,500–$50,000)</h3>
<p>
  A defined deliverable with a defined price: an SOP library, a menu rebuild, a local
  marketing calendar, an AI workflow rollout. The range is wide because the projects are.
</p>
<p>
  <strong>Right when:</strong> you know what needs building. This is where most implementation
  work belongs, and where you should expect a written scope covering what is included, what is
  not, and what "done" means.
</p>
<p>
  <strong>Wrong when:</strong> the diagnosis is still unclear. Scoping a project before you
  know the problem is how operations end up with a beautiful SOP library that does not touch
  the thing actually costing them money.
</p>

<h3>4. Monthly retainer (from ~$2,000/month)</h3>
<p>
  Ongoing access — weekly calls, KPI review, and someone to think with between them. Often
  called fractional COO work when it carries real operational responsibility rather than just
  advice.
</p>
<p>
  <strong>Right when:</strong> implementation is the bottleneck. Most operators do not fail
  because they lack a plan; they fail because nothing enforces the plan once the week gets
  busy. A weekly cadence is what a retainer actually buys.
</p>
<p>
  <strong>Wrong when:</strong> you are below roughly $1M in revenue. Below that, the fee is
  usually a bigger share of profit than the improvement it can realistically produce. A
  diagnostic plus one project is normally the better sequence.
</p>

<h2>How to tell whether it will pay for itself</h2>
<p>
  Run the arithmetic before you sign, not after. It is simple, and most operators never do it.
</p>
<p>
  Take the fee. Work out what change in a single number would cover it. If a project costs
  $8,000 and your annual revenue is $1.2M, you need a <strong>0.67%</strong> improvement in
  net margin to break even. If a retainer costs $2,000/month and your labor line is $30,000/month,
  you need labor to come down by <strong>6.7%</strong> to pay for itself — before counting
  anything else.
</p>
<p>
  Now ask whether the specific work proposed is plausibly capable of that. Not guaranteed —
  plausible. If a consultant cannot explain which line moves and roughly by how much, that is
  the answer.
</p>
<p>
  Then ask the harder question: what happens if nothing changes? A leak of $2,000/month left
  alone for a year is $24,000. Against that, an $8,000 project is not an expense decision, it
  is a timing one. This is the calculation
  <a href="restaurant-profit-leaks.html">most profit leaks</a> hide behind — each one is small
  enough to ignore in isolation.
</p>

<h2>What should be included at any price</h2>
<ul>
  <li><strong>A written scope.</strong> What is being done, what is not, and what "finished"
      means. Verbal scope is how engagements drift.</li>
  <li><strong>Access to the actual consultant.</strong> Confirm who does the work. Being sold
      by a principal and delivered to by a junior is common and rarely disclosed.</li>
  <li><strong>Your data back.</strong> Models, spreadsheets, and templates built during the
      engagement should be yours to keep and run without them.</li>
  <li><strong>An implementation path.</strong> A report is not a result. Ask what happens
      after delivery, and who is responsible for the change actually landing.</li>
  <li><strong>A defined exit.</strong> Especially on retainers. An engagement with no natural
      end is a subscription, not a project.</li>
</ul>

<h2>Questions worth asking on the first call</h2>
<ul>
  <li>Have you operated, or only advised? Both can be useful; they are not the same.</li>
  <li>What kind of operation do you turn down?</li>
  <li>Which line on my P&amp;L do you expect to move, and roughly how far?</li>
  <li>What do you need from me, and how much of my time will this take?</li>
  <li>What does this cost, in a range, before we go further?</li>
</ul>
<p>
  That last one is the test. A consultant who can give you a band on a first call is one who
  knows what their work is worth. One who cannot is deciding based on you.
</p>

<h2>A note on the cheapest option</h2>
<p>
  The cheapest consulting is usually the most expensive. Not because low fees signal low
  quality — plenty of good operators charge modestly — but because cheap engagements are
  almost always scoped too thin to change anything. A $500 "menu review" that produces a
  formatted PDF and no margin analysis has not cost you $500. It has cost you $500 plus
  another quarter of the leak you still have.
</p>
<p>
  Judge on scope and on whether the person can explain which number moves. Not on the fee.
</p>

<h2>Where to start</h2>
<p>
  If you do not yet know what is wrong, start with a diagnostic rather than a project — it is
  the cheapest way to avoid buying the wrong solution. The
  <a href="../profit-leak-snapshot.html">Profit Leak Snapshot</a> is $350 and covers four
  weeks of P&amp;Ls, labor reports, and item mix, and the fee credits toward any engagement
  that follows.
</p>
<p>
  If you would rather score your own operation first, the
  <a href="../audit.html">free operations audit</a> takes about ten minutes and costs nothing.
</p>
"""


def ld(obj):
    return ('<script type="application/ld+json">\n'
            + json.dumps(obj, indent=2, ensure_ascii=False)
            + "\n</script>\n")


def main():
    with open(SHELL, encoding="utf-8") as fh:
        shell = fh.read()

    url = f"{SITE}/{SLUG}"
    schema = ld({
        "@context": "https://schema.org", "@type": "BlogPosting",
        "headline": OG_TITLE, "url": url,
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "datePublished": PUBLISHED, "dateModified": PUBLISHED,
        "author": {"@id": f"{SITE}/#person"},
        "publisher": {"@id": f"{SITE}/#business"},
        "image": OG_CARD, "inLanguage": "en-US",
        "description": DESCRIPTION,
    }) + ld({
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home",
             "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Blog",
             "item": f"{SITE}/blog.html"},
            {"@type": "ListItem", "position": 3, "name": OG_TITLE,
             "item": url},
        ],
    })

    head = f"""<title>{TITLE}</title>
<meta content="{DESCRIPTION}" name="description"/>
<meta content="article" property="og:type"/>
<meta content="{OG_TITLE}" property="og:title"/>
<meta content="{url}" property="og:url"/>
<meta content="{DESCRIPTION}" property="og:description"/>
<meta content="{OG_CARD}" property="og:image"/>
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:image:alt" content="{OG_ALT}" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{OG_TITLE}" />
<meta name="twitter:description" content="{DESCRIPTION}" />
<meta name="twitter:url" content="{url}" />
<meta name="twitter:image" content="{OG_CARD}" />
<link rel="canonical" href="{url}" />
{schema}"""

    prefix = shell[:shell.index("<title>")]
    middle = shell[shell.index('<link rel="preconnect"'):
                   shell.index('<main id="main-content">')]
    # The shell carries its own canonical AND its own BlogPosting /
    # BreadcrumbList blocks. Both must go, or the new article silently
    # declares itself to be the source article.
    middle = re.sub(r'\s*<link rel="canonical"[^>]*>', "", middle)
    middle = re.sub(
        r'\s*<script type="application/ld\+json">.*?</script>',
        "", middle, flags=re.S,
    )
    suffix = shell[shell.index("</article>"):]

    crumbs = (
        '<nav class="breadcrumbs" aria-label="Breadcrumb">'
        '<a href="../index.html">Home</a> <span aria-hidden="true">›</span> '
        '<a href="../blog.html">Blog</a> <span aria-hidden="true">›</span> '
        f'<span aria-current="page">{OG_TITLE}</span></nav>'
    )

    body = f"""<main id="main-content">
{crumbs}
<article>
<a class="back-link" href="../blog.html">&#8592; Back to all posts</a>
<div class="post-header">
<h1>{H1}</h1>
<div class="post-meta">By <a rel="author" href="../about.html">Tre Coleman</a> &bull; <time datetime="{PUBLISHED}">August 16, 2026</time> &bull; {CATEGORY} &bull; {READ_TIME}</div>
</div>
<div class="post-content">
{BODY.strip()}
</div>
<div class="cta-section">
<h3>Not sure which of these you need?</h3>
<p>Start with a $350 Profit Leak Snapshot. Ninety minutes on your P&amp;L, labor, and item mix, and you leave with your top three leaks and a prioritised fix list. The fee credits toward whatever follows.</p>
<a class="button" href="../profit-leak-snapshot.html">Book Your Snapshot</a>
</div>
"""

    html = prefix + head + middle + body + suffix
    with open(SLUG, "w", encoding="utf-8") as fh:
        fh.write(html)

    words = len(re.sub(r"<[^>]+>", " ", BODY).split())
    print(f"Wrote {SLUG}  ~{words} words")


if __name__ == "__main__":
    main()
