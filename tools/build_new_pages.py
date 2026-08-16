#!/usr/bin/env python3
"""
Build the service and location pages the site was missing.

The site markets to food truck and catering operators throughout its copy and
schema, but had no page for either — so those searches had nowhere to land.
It also asserts "Virginia" ~40 times in footer boilerplate without naming a
single market.

Pages are generated from menu-engineering.html's shell so the nav, footer,
CSS and script blocks stay byte-identical to the rest of the site. Only the
<head> metadata and <main> content differ.

Deliberately claim-light: no invented percentages, ROI multiples or case
studies. Every figure that appears ($350, $2,000/mo, $67) is one already
published elsewhere on the site.

Run from the repository root:

    python3 tools/build_new_pages.py
"""

import json
import re

SHELL_SOURCE = "menu-engineering.html"
SITE = "https://trecoleman.com"
BUSINESS_ID = f"{SITE}/#business"
OG_CARD = f"{SITE}/images/og-card.jpg"
OG_ALT = ("Tre Coleman — restaurant operations consulting for restaurants, "
          "food trucks, and catering companies")


def head_block(slug, title, description, og_title, extra_ld):
    url = f"{SITE}/{slug}"
    blocks = "".join(
        '<script type="application/ld+json">\n'
        + json.dumps(obj, indent=2, ensure_ascii=False)
        + "\n</script>\n"
        for obj in extra_ld
    )
    return f"""<title>{title}</title>
<meta content="{description}" name="description"/>
<link rel="canonical" href="{url}" />
<meta property="og:type" content="website" />
<meta property="og:url" content="{url}" />
<meta property="og:title" content="{og_title}" />
<meta property="og:description" content="{description}" />
<meta property="og:image" content="{OG_CARD}" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:image:alt" content="{OG_ALT}" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:url" content="{url}" />
<meta name="twitter:title" content="{og_title}" />
<meta name="twitter:description" content="{description}" />
<meta name="twitter:image" content="{OG_CARD}" />
{blocks}"""


def service_ld(slug, name, description, service_type):
    return {
        "@context": "https://schema.org",
        "@type": "Service",
        "@id": f"{SITE}/{slug}",
        "name": name,
        "description": description,
        "provider": {"@id": BUSINESS_ID},
        "serviceType": service_type,
        "areaServed": [
            {"@type": "Country", "name": "United States"},
            {"@type": "State", "name": "Virginia"},
        ],
        "url": f"{SITE}/{slug}",
    }


def breadcrumb_ld(name, slug, parent=("Services", "services.html")):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home",
             "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": parent[0],
             "item": f"{SITE}/{parent[1]}"},
            {"@type": "ListItem", "position": 3, "name": name,
             "item": f"{SITE}/{slug}"},
        ],
    }


def faq_ld(pairs):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in pairs
        ],
    }


def crumbs(name, parent=("Services", "services.html")):
    return (
        '<nav class="breadcrumbs" aria-label="Breadcrumb">'
        '<a href="index.html">Home</a> <span aria-hidden="true">›</span> '
        f'<a href="{parent[1]}">{parent[0]}</a> '
        f'<span aria-hidden="true">›</span> '
        f'<span aria-current="page">{name}</span></nav>'
    )


def hero(h1, subtitle):
    return f"""<div class="service-hero">
<div class="container text-center">
<h1>{h1}</h1>
<p class="subtitle">{subtitle}</p>
</div>
</div>"""


def section(bg, inner):
    return (f'<section class="section-bg-{bg}">\n<div class="container">\n'
            f'{inner}\n</div>\n</section>')


def cards(items):
    body = "\n".join(
        f'<div class="benefit-card">\n<h3>{t}</h3>\n<p>{d}</p>\n</div>'
        for t, d in items
    )
    return f'<div class="benefits-grid">\n{body}\n</div>'


def steps(items):
    body = "\n".join(
        f'<div class="process-step">\n<h3>{t}</h3>\n<p>{d}</p>\n</div>'
        for t, d in items
    )
    return f'<div class="process-steps">\n{body}\n</div>'


def outcomes(intro, items):
    li = "\n".join(f"<li>{i}</li>" for i in items)
    return (f'<div class="outcomes-list">\n<p>{intro}</p>\n<ul>\n{li}\n</ul>\n'
            "</div>")


def faq_section(pairs):
    body = "\n".join(
        f'<h3>{q}</h3>\n<p class="mb-2">{a}</p>' for q, a in pairs
    )
    return section("cream", f'<h2 class="mb-2">Common Questions</h2>\n{body}')


def cta(heading, text, href="profit-leak-snapshot.html",
        label="Book Your $350 Profit Leak Snapshot"):
    return f"""<div class="cta-section">
<h2>{heading}</h2>
<p>{text}</p>
<a class="button" href="{href}">{label}</a>
</div>"""


# ------------------------------------------------------------------ content

FOOD_TRUCK_FAQ = [
    ("Do you work with trucks that haven't launched yet?",
     "Yes. Pre-launch work looks different — menu scoping, equipment fit, "
     "event selection and a pricing model built before you commit to a "
     "buildout. If you have not opened yet, the free Food Truck Launch "
     "Readiness Audit is the right starting point."),
    ("How is this different from restaurant consulting?",
     "The constraints are different. A truck has a fixed line, a fixed "
     "footprint, and revenue that depends on which events you take. Pricing "
     "an event badly costs you the whole day, and there is no second seating "
     "to make it back. The work concentrates on event pricing, prep planning "
     "and getting the operation to run without the owner on the line."),
    ("Can you help if I run a truck alongside a restaurant?",
     "Yes, and it is common. The usual problem is that the truck is costed "
     "as though its labor and prep are free because they come out of the "
     "restaurant. Separating the two P&Ls is often the first thing we do."),
]

CATERING_FAQ = [
    ("What is the difference between this and the Catering Profit System course?",
     "The course is a self-paced $67 product covering labor, pricing, food "
     "cost, logistics and cash flow — the right choice if you want to work "
     "through it yourself. Consulting applies the same frameworks directly "
     "to your numbers and contracts. Many operators start with the course "
     "and move to consulting when they want it built for them."),
    ("We cater out of an existing restaurant. Does that change anything?",
     "It changes the costing. Restaurant-based catering usually shares labor, "
     "prep space and inventory with the dining room, which makes event "
     "margins look better than they are. Splitting those costs honestly is "
     "normally where the work starts."),
    ("Do you help with pricing existing contracts, or only new ones?",
     "Both. Existing contracts often carry the worst margins because they "
     "were priced before the operation understood its true costs. Reviewing "
     "what you are already committed to usually surfaces the fastest wins."),
]

VIRGINIA_FAQ = [
    ("Do you only work with Virginia operators?",
     "No. The practice is based in Louisa, Virginia and works with operators "
     "across the country. Virginia clients can add in-person time; everyone "
     "else works remotely, which is how the majority of engagements run "
     "regardless of location."),
    ("What does in-person work actually involve?",
     "Usually a service observation — being on site through a real shift or "
     "event rather than a conference-room meeting. It is most useful early "
     "in an engagement, and for problems that are hard to see in the numbers "
     "alone, like flow, handoffs and station layout."),
    ("How far will you travel for on-site work?",
     "Central Virginia is straightforward. Beyond that it depends on the "
     "scope of the project — worth raising on the first call so travel is "
     "priced into the proposal rather than added later."),
]

PAGES = [
    {
        "slug": "food-truck-consulting.html",
        "name": "Food Truck Consulting",
        "title": "Food Truck Consulting & Profitability | Tre Coleman",
        "og_title": "Food Truck Consulting for Owner-Operators | Tre Coleman",
        "description":
            "Event pricing, prep systems, and staffing for food truck "
            "operators who are busy but not profitable. Remote nationwide, "
            "in person across Virginia.",
        "h1": "Food Truck Consulting",
        "subtitle":
            "Event pricing, prep planning, and systems for operators who need "
            "the truck to make money — not just make sales.",
        "service_type": "Food Truck Operations Consulting",
        "problem": [
            "The truck is booked. The events are busy. The line moves. And at "
            "the end of the month the numbers still do not work. Most food "
            "truck operators are not short of demand — they are short of a "
            "pricing model that survives contact with a real event.",
            "<strong>What that usually looks like:</strong> festival and "
            "private-event pricing set by guesswork or by what the last truck "
            "charged. Prep that takes two days for a six-hour service. A menu "
            "built for a kitchen, running on a line built for four. And an "
            "operation where nothing happens unless the owner is standing in "
            "it.",
        ],
        "benefits": [
            ("Event Pricing That Holds",
             "A model that prices festivals, private events, and corporate "
             "bookings against their real cost — travel, prep, staffing, "
             "waste, and the days you cannot book because you are recovering "
             "from the last one."),
            ("Prep That Fits the Service",
             "Par levels and prep plans scaled to what the event will "
             "actually sell, so you stop cooking for a crowd that never "
             "arrives and stop selling out at hour three."),
            ("A Menu Built for the Line",
             "Item-level review against your actual equipment and station "
             "count. Fewer items, faster tickets, and margins you can defend."),
            ("Off the Truck",
             "Written prep lists, open and close procedures, and role "
             "training so the truck can run a service without you on it."),
            ("Event Selection",
             "Not every booking is worth taking. A simple framework for "
             "deciding which events earn their day and which quietly cost "
             "you money."),
            ("Numbers You Can Read",
             "A one-page view of what each event actually returned, so the "
             "next season's calendar is built on evidence."),
        ],
        "steps": [
            ("Review the last season",
             "We go through your event history, pricing, prep time, and "
             "staffing against what each booking actually returned. Most "
             "operators have never seen this laid out event by event."),
            ("Rebuild the pricing model",
             "A full-cost model covering travel, prep, labor, waste, and "
             "recovery time — with floors you can hold when a client pushes "
             "back."),
            ("Fix prep and par levels",
             "Prep planning tied to forecast volume per event type, so prep "
             "time and waste both come down."),
            ("Write it down and train it",
             "Prep lists, station setups, open and close procedures. The "
             "point is a truck that runs the same whether or not you are "
             "there."),
        ],
        "outcomes_intro":
            "What operators typically want out of this work:",
        "outcomes": [
            "Event pricing that covers full cost, including the days you "
            "cannot book",
            "Prep time that matches the service instead of doubling it",
            "A menu the line can actually execute at volume",
            "Written procedures so a trained crew can run a service",
            "A clear read on which events are worth repeating",
        ],
        "audience": [
            "You run one or more trucks and cannot tell which events actually "
            "made money",
            "You are booked but your margins are thin or unpredictable",
            "You are the only person who knows how to run the truck",
            "You are adding catering or a second truck and want the pricing "
            "right before you scale",
        ],
        "faq": FOOD_TRUCK_FAQ,
        "cta": ("Ready to find out what your events are really returning?",
                "Start with a 90-minute Profit Leak Snapshot. We review your "
                "event history, pricing, and prep, and you leave with your "
                "top three leaks and a prioritised fix list."),
        "related": [
            ("food-truck-audit.html",
             "Free Food Truck Launch Readiness Audit",
             "Not open yet? Score your menu, operations, permits, and pricing "
             "before you launch."),
            ("menu-engineering.html", "Menu Engineering",
             "Item-level margin work for operators whose menu is the "
             "bottleneck."),
            ("catering-consulting.html", "Catering Consulting",
             "Adding events and private catering to the truck."),
        ],
    },
    {
        "slug": "catering-consulting.html",
        "name": "Catering Consulting",
        "title": "Catering Business Consulting & Pricing | Tre Coleman",
        "og_title": "Catering Consulting for Owner-Operators | Tre Coleman",
        "description":
            "Full-cost pricing, labor allocation, and contract margin work "
            "for catering operations growing in revenue but not in profit. "
            "Remote nationwide.",
        "h1": "Catering Consulting",
        "subtitle":
            "Full-cost pricing, labor allocation, and contract margins for "
            "caterers whose revenue is growing faster than their profit.",
        "service_type": "Catering Operations Consulting",
        "problem": [
            "Catering is the easiest place in food service to grow revenue "
            "and lose money doing it. Volume goes up, the calendar fills, the "
            "team is stretched — and the margin is thinner than it was at "
            "half the size.",
            "<strong>What that usually looks like:</strong> quotes built off "
            "food cost with labor guessed at the end. Staffing set by feel "
            "rather than by event type. Prep that spills into days nobody "
            "costed. And no way to tell which contracts are carrying the "
            "business and which are quietly draining it.",
        ],
        "benefits": [
            ("Full-Cost Pricing",
             "A quoting model that includes prep labor, service labor, "
             "travel, rentals, breakage, and the overhead most caterers leave "
             "out entirely."),
            ("Margin by Event Type",
             "Contribution margin tracked per event type, so you can see "
             "which work to chase and which to price differently or decline."),
            ("Staffing Models",
             "Staffing built per event type and guest count instead of by "
             "instinct, so labor stops being the line that ruins an "
             "otherwise good job."),
            ("Prep and Production Planning",
             "Production schedules that spread load across the week rather "
             "than compressing it into the two days before a Saturday."),
            ("Payment Terms That Protect You",
             "Deposit structure, payment schedule, and collection policy so "
             "cash arrives before the costs do."),
            ("Contract Review",
             "A read on the agreements you are already committed to, which is "
             "usually where the fastest recoverable margin sits."),
        ],
        "steps": [
            ("Cost the last quarter honestly",
             "We rebuild what a representative set of your recent events "
             "actually cost, including the labor and prep time that never "
             "made it onto the quote."),
            ("Build the pricing model",
             "A full-cost calculator you can quote from, with tier structures "
             "and floors that hold under negotiation."),
            ("Fix staffing and production",
             "Staffing ratios by event type, and a production schedule that "
             "stops compressing everything into the final 48 hours."),
            ("Set the cash terms",
             "Deposits, payment schedule, and a collection policy so growth "
             "does not become a cash-flow problem."),
        ],
        "outcomes_intro":
            "What operators typically want out of this work:",
        "outcomes": [
            "Quotes that include every real cost, not just food",
            "A clear read on which event types actually carry margin",
            "Staffing set by model rather than by instinct",
            "Production load spread across the week",
            "Deposits and terms that keep cash ahead of costs",
        ],
        "audience": [
            "Your catering revenue is growing but profit is flat or falling",
            "You cannot say which contracts or event types are profitable",
            "You are quoting off food cost and adding labor at the end",
            "You cater out of a restaurant and share labor between the two",
        ],
        "faq": CATERING_FAQ,
        "cta": ("Want to know which contracts are actually profitable?",
                "Start with a 90-minute Profit Leak Snapshot. We review your "
                "recent events, quotes, and labor, and you leave with your "
                "top three leaks and a prioritised fix list."),
        "related": [
            ("catering-profit.html", "The Catering Profit System",
             "The self-paced $67 course covering labor, pricing, food cost, "
             "logistics, and cash flow."),
            ("menu-engineering.html", "Menu Engineering",
             "Item-level margin work for catering and restaurant menus."),
            ("sops-training.html", "SOPs & Training Systems",
             "Written procedures so events run the same without you."),
        ],
    },
    {
        "slug": "virginia-restaurant-consulting.html",
        "name": "Virginia",
        "title": "Restaurant Consulting in Virginia | Tre Coleman",
        "og_title": "Restaurant Operations Consulting in Virginia | Tre Coleman",
        "description":
            "Restaurant, food truck, and catering consulting based in Louisa, "
            "Virginia. In-person across Central Virginia, remote nationwide.",
        "h1": "Restaurant Consulting in Virginia",
        "subtitle":
            "Based in Louisa. On-site across Central Virginia, and working "
            "remotely with operators anywhere in the country.",
        "service_type": "Restaurant Operations Consulting",
        "parent": ("Services", "services.html"),
        "problem": [
            "Most restaurant consulting is sold as either a fly-in engagement "
            "or a purely remote one. Neither is quite right. The numbers work "
            "— P&amp;L review, item mix, labor modelling, menu margin — is "
            "genuinely better done remotely, with time to think. But some "
            "problems only show up on the floor during a real service.",
            "This practice is based in <strong>Louisa, Virginia</strong>. "
            "Virginia operators get both: the analysis done remotely, and "
            "on-site time where being in the room is what actually answers "
            "the question.",
        ],
        "benefits": [
            ("Charlottesville",
             "Roughly 30 minutes from home base. Straightforward for service "
             "observations and on-site working sessions."),
            ("Richmond",
             "About an hour out. Regular on-site work is practical, including "
             "multi-day project time."),
            ("Fredericksburg",
             "Around an hour. On-site sessions and service observations are "
             "workable within a normal day."),
            ("Harrisonburg &amp; the Valley",
             "Reachable for scheduled on-site work, usually grouped into "
             "fuller days to make the trip worthwhile."),
            ("Louisa &amp; Lake Anna",
             "Home ground. Short-notice on-site time is genuinely possible "
             "here in a way it is not elsewhere."),
            ("Everywhere else",
             "Remote, which is how most engagements run anyway — Zoom, "
             "shared docs, and recorded walkthroughs of your numbers."),
        ],
        "steps": [
            ("Start with the numbers",
             "Four weeks of P&amp;Ls, labor reports, and item-level sales "
             "data. This part is remote for everyone, Virginia or not, "
             "because it is better done with time than in a room."),
            ("Add a service observation",
             "For Virginia operators, being on site through a real service or "
             "event. Flow, handoffs, station layout, and the gap between how "
             "a shift is supposed to run and how it does."),
            ("Build the fixes",
             "Whatever the diagnosis calls for — labor model, menu work, "
             "written procedures, local marketing calendar. Built remotely, "
             "reviewed together."),
            ("Stay in it",
             "Implementation is where most consulting quietly fails. Ongoing "
             "advisory keeps a weekly cadence on it; on-site check-ins are "
             "available for Virginia clients."),
        ],
        "outcomes_intro":
            "Who this practice works with across Virginia:",
        "outcomes": [
            "Independent restaurants — single location and small multi-unit",
            "Food truck operators working events across the Commonwealth",
            "Catering companies, standalone and restaurant-based",
            "Operators adding a second location, a truck, or a catering arm",
        ],
        "audience": [
            "You are a Virginia operator who wants someone who can actually "
            "come stand in your operation",
            "You want the analysis done properly, not in a two-hour site visit",
            "You are outside Virginia and want the same work done remotely",
            "You want a consultant who has run units, not just advised on them",
        ],
        "faq": VIRGINIA_FAQ,
        "cta": ("Operating in Virginia? Start with a Snapshot.",
                "A 90-minute diagnostic on your P&amp;L, labor, and item mix. "
                "You leave with your top three profit leaks and a prioritised "
                "fix list. In person where it makes sense, remote where it "
                "does not."),
        "related": [
            ("services.html", "All Services",
             "Menu engineering, SOPs and training, local marketing, AI "
             "workflows, and advisory."),
            ("virginia-neighbors.html", "Virginia Neighbors Directory",
             "A directory of Virginia restaurants, food trucks, caterers, and "
             "local businesses."),
            ("lsm.html", "Local Store Marketing",
             "Filling slow shifts through the neighbourhood rather than paid "
             "ads."),
        ],
    },
]


def build_body(page):
    parent = page.get("parent", ("Services", "services.html"))
    out = [crumbs(page["name"], parent), hero(page["h1"], page["subtitle"])]

    problem = "\n".join(f'<p class="mb-2">{p}</p>' for p in page["problem"])
    out.append(section("white", f'<h2 class="mb-2">The Problem You\'re Facing'
                                f'</h2>\n{problem}'))

    out.append(section(
        "cream",
        f'<h2 class="mb-2">What This Covers</h2>\n{cards(page["benefits"])}',
    ))

    out.append(section(
        "white",
        f'<h2 class="mb-2">How It Works</h2>\n{steps(page["steps"])}',
    ))

    out.append(section(
        "cream",
        '<h2 class="mb-2">What You Get</h2>\n'
        + outcomes(page["outcomes_intro"], page["outcomes"]),
    ))

    aud = "\n".join(f"<li>{a}</li>" for a in page["audience"])
    out.append(section(
        "white",
        f'<h2 class="mb-2">Who This Is For</h2>\n'
        f'<ul class="mb-2">\n{aud}\n</ul>',
    ))

    out.append(faq_section(page["faq"]))

    rel = "\n".join(
        f'<div class="benefit-card">\n<h3><a href="{h}">{t}</a></h3>\n'
        f"<p>{d}</p>\n</div>"
        for h, t, d in page["related"]
    )
    out.append(section(
        "white",
        f'<h2 class="mb-2">Related</h2>\n'
        f'<div class="benefits-grid">\n{rel}\n</div>',
    ))

    out.append(section("white", cta(*page["cta"])))
    return "\n".join(out)


def main():
    with open(SHELL_SOURCE, encoding="utf-8") as fh:
        shell = fh.read()

    head_start = shell.index("<title>")
    head_end = shell.index("<link rel=\"preconnect\"")
    prefix = shell[:head_start]
    middle = shell[head_end:shell.index('<main id="main-content">')]
    suffix = shell[shell.index("</main>"):]

    for page in PAGES:
        parent = page.get("parent", ("Services", "services.html"))
        extra = [
            service_ld(page["slug"], page["h1"], page["description"],
                       page["service_type"]),
            breadcrumb_ld(page["name"], page["slug"], parent),
            faq_ld(page["faq"]),
        ]
        html = (
            prefix
            + head_block(page["slug"], page["title"], page["description"],
                         page["og_title"], extra)
            + middle
            + '<main id="main-content">\n'
            + build_body(page)
            + "\n"
            + suffix
        )
        with open(page["slug"], "w", encoding="utf-8") as fh:
            fh.write(html)
        words = len(re.sub(r"<[^>]+>", " ", build_body(page)).split())
        print(f"  {page['slug']:<42} ~{words} words of body copy")


if __name__ == "__main__":
    main()
