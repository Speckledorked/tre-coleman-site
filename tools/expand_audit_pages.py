#!/usr/bin/env python3
"""
Give the two audit tools real indexable content.

audit.html and food-truck-audit.html look substantial (~3,700 and ~4,200
words) but almost all of it is <option> text — 65 and 108 option tags
respectively. Strip the form and there are a couple of hundred words of
actual prose, which is why two otherwise useful lead magnets rank for
nothing.

Each gains an introduction above the tool explaining what it measures and why
each dimension matters, so the page stands on its own as a resource whether
or not the visitor completes the form.

Benchmarks referenced here are the ones already encoded in each page's own
scoring options (e.g. audit.html already scores food cost under 25% as
"Excellent" and over 35% as "Needs attention"). Nothing new is asserted.

Run from the repository root:

    python3 tools/expand_audit_pages.py
"""

import re

INTROS = {
    "audit.html": """
<section class="audit-intro">
  <h2>What this audit measures</h2>
  <p>
    Most operations that are busy but not profitable are not losing money in one
    dramatic place. They are losing it in five ordinary ones at the same time,
    each small enough to rationalise on its own. This audit walks the five, scores
    where you sit, and tells you which to fix first.
  </p>
  <p>
    It takes about ten minutes and needs no preparation beyond rough familiarity
    with your own numbers. Estimates are fine — the point is to find the gap worth
    investigating, not to produce an accounting record.
  </p>

  <h3>Food cost management</h3>
  <p>
    Food cost is the number most operators can quote and the fewest can act on,
    because the headline percentage hides where it comes from. A kitchen at 32%
    with tight portioning has a different problem from one at 32% with heavy
    waste and loose receiving. The questions separate the two.
  </p>

  <h3>Labour efficiency</h3>
  <p>
    Labour is the fastest-moving line you control week to week, which makes it the
    most expensive one to manage by instinct. One extra overtime hour per shift
    across five days compounds into real money before you have sold a single
    additional plate. This section looks at whether your schedule is built from
    sales patterns or from habit.
  </p>

  <h3>Revenue optimisation</h3>
  <p>
    Revenue problems usually present as traffic problems and turn out to be mix
    problems. If your average check has been flat while costs rose, the issue is
    rarely how many people came in — it is what they ordered once they did, and
    whether anything on the menu or the floor guided that choice.
  </p>

  <h3>Technology and systems</h3>
  <p>
    The question here is not whether you have modern tools. It is whether the
    operation can run a correct shift without you in the building. Systems that
    live only in an owner's head are not systems; they are a constraint on how
    large the business can get and how far away you can be.
  </p>

  <h3>Quality and consistency</h3>
  <p>
    Consistency is what converts a first visit into a habit, and it is the first
    thing to degrade when the other four are under strain. Variability between
    shifts is usually a symptom rather than a cause, which is why it is scored
    last and read alongside everything above it.
  </p>

  <h2>What you get at the end</h2>
  <p>
    A score per dimension and a ranked view of where the weakest link sits. It is
    a self-assessment, not a diagnosis — it tells you which area deserves a proper
    look at your actual numbers. If you would rather skip to that,
    the <a href="profit-leak-snapshot.html">Profit Leak Snapshot</a> reviews four
    weeks of P&amp;Ls, labour reports and item mix directly.
  </p>
</section>
""",
    "food-truck-audit.html": """
<section class="audit-intro">
  <h2>What this audit measures</h2>
  <p>
    A food truck fails differently from a restaurant. There is no second seating to
    recover a bad lunch, no back-of-house to absorb a prep mistake, and the revenue
    ceiling for the day is set before you open by which event you took. Most trucks
    that struggle were not badly run — they were badly scoped before they opened.
  </p>
  <p>
    This audit walks the areas that decide whether a truck is viable, and scores
    how ready yours is. It takes about ten minutes. If you have not launched yet,
    that is the ideal time to run it: almost everything here is cheaper to change
    on paper than after a buildout.
  </p>

  <h3>Menu and production</h3>
  <p>
    The most common pre-launch mistake is a menu designed for a kitchen and
    executed on a line built for four people and a flat-top. Every extra item adds
    prep, holding space and ticket time, and a truck has very little of all three.
    Shorter menus are not a compromise here; they are the format working properly.
  </p>

  <h3>Pricing and margin</h3>
  <p>
    Event pricing is where trucks quietly lose their year. A festival fee, travel,
    prep the day before, staffing, and the day afterwards you cannot book all have
    to be covered by one service. Pricing against the truck parked next to you,
    rather than against your own cost, is how a fully booked season ends flat.
  </p>

  <h3>Operations and logistics</h3>
  <p>
    Commissary access, water and power, generator capacity, storage, and the
    realities of setup and breakdown. These are the constraints that turn a good
    concept into a long day, and they are far easier to plan for than to retrofit.
  </p>

  <h3>Permits and compliance</h3>
  <p>
    Requirements vary by locality and change, so this section flags whether you
    have confirmed them rather than telling you what they are. Verify your
    specific jurisdiction's health department and fire marshal requirements
    directly — a truck that cannot legally trade at an event is the most expensive
    kind of unprepared.
  </p>

  <h3>Marketing and bookings</h3>
  <p>
    A truck's revenue depends on being somewhere people already are, and on those
    people knowing you will be there. The questions cover how you fill a calendar,
    how customers find your location, and whether anything brings them back beyond
    having walked past.
  </p>

  <h2>What you get at the end</h2>
  <p>
    A readiness score and a view of which areas are weakest. It is a
    self-assessment, not a business plan — but it is a reliable way to find the
    gap worth closing before it costs you a season. If you are already trading and
    want the numbers looked at properly, see
    <a href="food-truck-consulting.html">food truck consulting</a>.
  </p>
</section>
""",
}

CSS = """
    .audit-intro {
      max-width: 800px;
      margin: 0 auto;
      padding: 2.5rem 2rem 0.5rem;
    }
    .audit-intro h2 {
      color: var(--primary-navy);
      font-size: 1.6rem;
      margin: 2rem 0 0.75rem;
      line-height: 1.3;
    }
    .audit-intro h2:first-child { margin-top: 0; }
    .audit-intro h3 {
      color: var(--primary-navy);
      font-size: 1.15rem;
      margin: 1.5rem 0 0.5rem;
    }
    .audit-intro p {
      line-height: 1.75;
      margin-bottom: 1rem;
      color: var(--dark-text);
    }
    @media (max-width: 768px) {
      .audit-intro { padding: 2rem 1.25rem 0.5rem; }
      .audit-intro h2 { font-size: 1.35rem; }
    }
"""


def main():
    for path, intro in INTROS.items():
        with open(path, encoding="utf-8") as fh:
            html = fh.read()

        if 'class="audit-intro"' in html:
            print(f"  skip (already done) {path}")
            continue

        # Place the intro after the page's hero header, before the tool itself.
        marker = '<div class="progress-bar">'
        idx = html.find(marker)
        if idx == -1:
            idx = html.find('<div class="content">')
        if idx == -1:
            print(f"  SKIP (no insertion point) {path}")
            continue
        html = html[:idx] + intro.strip() + "\n" + html[idx:]

        # Append styles to the page's last <style> block.
        close = html.rfind("</style>")
        html = html[:close] + CSS + html[close:]

        with open(path, "w", encoding="utf-8") as fh:
            fh.write(html)

        prose = re.sub(r"<[^>]+>", " ", intro).split()
        print(f"  {path}  +{len(prose)} words of prose")


if __name__ == "__main__":
    main()
