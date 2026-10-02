#!/usr/bin/env python3
"""
Differentiate the four templated service pages and add FAQPage schema.

menu-engineering, sops-training, lsm and ai-integration all shipped on an
identical H2 skeleton (Problem / Delivers / How / Outcomes / Included / Who /
Ready?) at ~630-730 words each. Structurally near-duplicate pages compete with
each other rather than ranking individually.

Each page gains a "Common Questions" section with questions that only make
sense for that service, plus FAQPage schema backed by that visible content —
Google requires the markup to describe what a user actually sees.

The questions are grounded in what each page already claims and in the
pricing published elsewhere on the site. No invented results or case studies.

Run from the repository root:

    python3 tools/differentiate_service_pages.py
"""

import json
import re

SITE = "https://trecoleman.com"

FAQS = {
    "menu-engineering.html": [
        ("Do I need a POS that exports item-level sales data?",
         "Effectively yes. Menu engineering maps contribution margin against "
         "popularity, and popularity has to come from somewhere. Almost every "
         "modern POS exports an item sales mix report. If yours cannot, we can "
         "work from a manual count over two to three weeks — less precise, but "
         "enough to find the obvious outliers."),
        ("Will this mean raising my prices?",
         "Not across the board. Blanket increases are the blunt version of "
         "this work and they cost you traffic. The usual outcome is a smaller "
         "menu, repositioned items, and selective price moves only where "
         "guests have demonstrated willingness to pay. Several items often "
         "come down."),
        ("What if my menu changes seasonally?",
         "That makes the framework more useful, not less. The point is a "
         "repeatable method you run each time the menu turns over, rather "
         "than a one-off verdict on this season's dishes."),
        ("How is this different from a chef consultant?",
         "A chef consultant works on the food. This works on the economics of "
         "the food — what each item contributes after cost, how the layout "
         "steers ordering, and which dishes are quietly subsidised by the "
         "rest. The recipes stay yours."),
    ],
    "sops-training.html": [
        ("We already have a training manual nobody reads. How is this different?",
         "Most manuals fail because they were written to exist rather than to "
         "be used mid-shift. The work here is checklists and one-page role "
         "scorecards a person can follow on a Friday night, not a binder. If "
         "the frontline will not use it during a rush, it is not finished."),
        ("Who actually writes the documentation?",
         "I do the structure and the first draft, built from observing how "
         "your operation already runs. Your team corrects it — they know the "
         "steps that matter. Documentation written without them describes a "
         "restaurant that does not exist."),
        ("How long before new hires are actually faster to onboard?",
         "The documents exist within weeks; the change in ramp time shows up "
         "over the following hiring cycles, because you only see it as people "
         "come through. The honest answer is that this is a slower-returning "
         "investment than menu or labour work, and it compounds."),
        ("What happens when a process changes?",
         "You update one page, not a binder. Part of the handover is leaving "
         "you with the structure and a cadence for maintaining it, so the "
         "library does not drift out of date six months after I leave."),
    ],
    "lsm.html": [
        ("How is this different from hiring someone to run my social media?",
         "Social media is one channel. Local store marketing is the whole "
         "neighbourhood relationship — nearby employers, schools, other "
         "operators, events, and the offers that bring people back on a "
         "Tuesday. Social posting is a tactic inside it, not the plan."),
        ("Do I need an advertising budget?",
         "No. The calendar is built around activity your team can run — "
         "partnerships, in-store activations, and trackable offers. Paid ads "
         "can sit on top of it, but the point is traffic that does not stop "
         "the day you stop paying for it."),
        ("Who runs the twelve weeks — you or my team?",
         "Your team. A calendar that depends on an outside consultant to "
         "execute stops the moment the engagement ends. The deliverable is "
         "something your managers can run, with the offers and tracking "
         "already defined."),
        ("How do I know whether any of it worked?",
         "Every offer is built to be trackable, which is usually the missing "
         "piece. Most local marketing fails not because the ideas were bad "
         "but because nothing distinguished the promotions that worked from "
         "the ones that did not."),
    ],
    "ai-integration.html": [
        ("Is this going to replace anyone on my team?",
         "No, and that is not what it is for. The target is the administrative "
         "work that pulls managers off the floor — reporting, scheduling "
         "drafts, prep lists, recurring documents. The intent is managers "
         "spending more time running the operation, not fewer managers."),
        ("We are not a tech-forward operation. Is this too early for us?",
         "Usually the opposite. Operations with the least automation have the "
         "most obvious wins, because the manual work is still fully visible. "
         "What matters is whether you have repeatable admin tasks, not "
         "whether your team is technical."),
        ("What tools would we end up paying for?",
         "Whatever you already run is usually the starting point — Google "
         "Workspace, your POS exports, a scheduling tool. Rollout is scoped to "
         "what the operation will actually adopt. Adding five subscriptions "
         "nobody opens is a worse outcome than adding none."),
        ("What stops the AI getting something important wrong?",
         "Human review stays in the loop on anything that touches money, "
         "scheduling or guest communication. These are workflows with "
         "checkpoints, not systems left to run unattended."),
    ],
}


def ld(obj):
    return ('<script type="application/ld+json">\n'
            + json.dumps(obj, indent=2, ensure_ascii=False)
            + "\n</script>\n")


def faq_html(pairs):
    body = "\n".join(
        f'<h3>{q}</h3>\n<p class="mb-2">{a}</p>' for q, a in pairs
    )
    return (
        '<section class="section-bg-cream">\n<div class="container">\n'
        '<h2 class="mb-2">Common Questions</h2>\n'
        f'{body}\n</div>\n</section>\n'
    )


def main():
    for path, pairs in FAQS.items():
        with open(path, encoding="utf-8") as fh:
            html = fh.read()

        if "FAQPage" in html:
            print(f"  skip (already done) {path}")
            continue

        schema = ld({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "@id": f"{SITE}/{path}#faq",
            "mainEntity": [
                {"@type": "Question", "name": q,
                 "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in pairs
            ],
        })
        html = re.sub(r"</head>", schema + "</head>", html, count=1, flags=re.I)

        # Insert the visible FAQ before the closing CTA section, so the page
        # ends on its call to action rather than on questions.
        marker = '<div class="cta-section">'
        idx = html.rfind(marker)
        if idx == -1:
            idx = html.rfind("</main>")
            html = html[:idx] + faq_html(pairs) + html[idx:]
        else:
            # Walk back to the start of the enclosing section if there is one.
            sec = html.rfind("<section", 0, idx)
            at = sec if sec != -1 else idx
            html = html[:at] + faq_html(pairs) + html[at:]

        with open(path, "w", encoding="utf-8") as fh:
            fh.write(html)
        print(f"  {path}  +{len(pairs)} questions, +FAQPage schema")


if __name__ == "__main__":
    main()
