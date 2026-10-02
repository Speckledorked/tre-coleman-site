#!/usr/bin/env python3
"""
Generate the remaining framework articles from the content plan in
SEO_AUDIT.md section 4.5.

Covers items #2, #3, #5, #6, #7 and #8. These are the pieces that can be
written from operations fundamentals plus the pricing already published on this
site.

Item #2 is grounded in the owner's own Catering Profit System Module 2
material — the full-cost calculator, the quick-reference card and the service
tier sheet under course/downloads/module-2/. The article teaches the method and
the cost structure; the calculator and the templates stay inside the paid
course. Nothing in it is invented: every range, benchmark and formula is drawn
from those files, which label the per-head figures as industry ranges rather
than measured results, and the article says so too.

Items #9 and #10 are deliberately absent: #9 (ghost kitchens) was declined,
and #10 depends on the owner's own operating history, which cannot be written
by anyone else without inventing it.

Every article:
  * carries BlogPosting + BreadcrumbList schema for its own URL
  * links up to its cluster pillar and across to the matching service page
  * ends on a CTA to the $350 Snapshot
  * contains no invented client results, percentages or case studies.
    Arithmetic shown is worked from figures stated in the text itself.

Run from the repository root:

    python3 tools/build_articles.py
"""

import json
import os
import re

SHELL = "blog/menu-engineering-guide.html"
SITE = "https://trecoleman.com"
OG_CARD = f"{SITE}/images/og-card.jpg"
OG_ALT = ("Tre Coleman — restaurant operations consulting for restaurants, "
          "food trucks, and catering companies")
PUBLISHED = "2026-10-02"
PRETTY_DATE = "October 2, 2026"

ARTICLES = [
    {
        "slug": "blog/how-to-price-catering-jobs.html",
        "title": "How to Price Catering Jobs for Profit | Tre Coleman",
        "h1": "How to Price Catering Jobs So You Actually Make Money",
        "description": "The full cost stack behind a catering quote, the "
                       "break-even formula most operators get backwards, and "
                       "the margin benchmarks that show which events pay.",
        "read": "11 min read",
        "body": """
<p>
  Ask a caterer how they priced a job and you will usually hear some version of the same
  method: work out roughly what the food costs, multiply by three, check it feels about
  right against what the last person charged, send the quote.
</p>
<p>
  That method is not wrong so much as incomplete. Food is the cost that is easiest to see
  and it is rarely the one that decides whether the event made money. The jobs that quietly
  lose money are almost never the ones where the food cost was misjudged. They are the ones
  where four servers stayed two hours longer than planned, the van made a second trip, and
  nobody charged for either.
</p>
<p>
  What follows is the structure for pricing an event against <em>every</em> cost it
  actually incurs, and then the benchmarks for telling whether the number you arrived at
  was any good.
</p>

<h2>The three cost buckets, and the one everyone skips</h2>
<p>
  Every catered event has exactly three categories of direct cost. Quote against all three
  and the arithmetic works. Quote against one and you are guessing.
</p>

<h3>1. Food cost</h3>
<p>
  The obvious one, and the one most operators already track reasonably well. Per person,
  across every component: appetizers, salads, entrees, sides, bread, dessert, non-alcoholic
  beverages, alcohol if you are supplying it, condiments and extras.
</p>
<p>
  Two line items in this bucket are routinely left out. <strong>Disposables and
  servingware</strong> — chafers, sternos, serving utensils, plates, napkins, cutlery —
  are a real per-head cost even when they feel like overhead. And a <strong>waste
  buffer</strong>: you do not cook for exactly one hundred people, you cook for one hundred
  with margin for error, and that margin is a cost. Ten percent on top of raw food cost is
  a reasonable starting assumption until you have tracked your own.
</p>

<h3>2. Labor cost</h3>
<p>
  Priced by role, by hour, for the hours actually worked — not the hours the event runs.
  An event with a 6pm start does not have a 6pm labor clock. Prep begins hours earlier and
  breakdown runs after the last guest leaves.
</p>
<p>
  The roles that belong in the calculation: kitchen lead, line cooks, prep cooks, servers,
  bartender, event captain, dishwasher, and drivers. Drivers in particular get missed,
  because the driving happens outside the event and so feels like it is not part of it.
</p>
<p>
  Count the hours honestly. If your team is on site at 1pm for a 6pm event and clears by
  10:30pm, that is eight and a half hours per person, not four. Pricing against the guest-
  facing window is the single most common way a quote comes in under cost.
</p>

<h3>3. Overhead and other direct costs</h3>
<p>
  This is the bucket that gets skipped, and it is the one that moves a marginal event into
  a loss. Everything an event consumes that is neither food nor payroll:
</p>
<ul>
  <li>Transportation and mileage</li>
  <li>Equipment rental</li>
  <li>Linen and decor rental</li>
  <li>Fuel and propane</li>
  <li>Parking and tolls</li>
  <li>Permits and per-event insurance</li>
  <li>Packaging and to-go containers</li>
  <li>Ice</li>
  <li>A miscellaneous buffer, because something always comes up</li>
</ul>
<p>
  None of these are large on their own. Together they routinely come to several hundred
  dollars on a hundred-guest event — which, on a job quoted at a twenty percent margin, is
  most of the profit.
</p>

<h2>The formula</h2>
<p>
  Once the three buckets are totalled, pricing is arithmetic rather than judgement.
</p>
<p>
  <strong>Break-even price per person</strong> = (food + labor + overhead) &divide; guest
  count. This is the floor. Quoting below it means paying for the privilege of working.
</p>
<p>
  <strong>Target price per person</strong> = break-even &divide; (1 &minus; target margin).
</p>
<p>
  That second formula is where most operators go wrong, because the instinct is to
  <em>add</em> the margin rather than divide by its inverse. If your break-even is $20 per
  head and you want a 25% margin, adding 25% gives you $25 — and $5 of profit on $25 of
  revenue is a 20% margin, not 25%. Dividing gives the right answer: $20 &divide; 0.75 =
  <strong>$26.67</strong>.
</p>
<p>
  The gap looks small per head. On a 150-guest wedding it is $250 of margin you intended to
  earn and did not.
</p>

<h2>Sanity-checking against per-head ranges</h2>
<p>
  A calculated price should land somewhere defensible. These are typical industry ranges
  per person by event type and service level — useful for a quick read on a call, not a
  substitute for costing the actual job. Your market, your menu and your cost base will
  move them.
</p>
<table>
  <thead>
    <tr><th>Event type</th><th>Drop-off</th><th>Buffet</th><th>Full-service</th><th>Plated</th></tr>
  </thead>
  <tbody>
    <tr><td>Corporate lunch</td><td>$12&ndash;$18</td><td>$20&ndash;$30</td><td>$30&ndash;$45</td><td>$40&ndash;$60</td></tr>
    <tr><td>Corporate dinner</td><td>$15&ndash;$22</td><td>$25&ndash;$40</td><td>$40&ndash;$60</td><td>$55&ndash;$85</td></tr>
    <tr><td>Wedding (casual)</td><td>&mdash;</td><td>$25&ndash;$40</td><td>$40&ndash;$65</td><td>$60&ndash;$90</td></tr>
    <tr><td>Wedding (formal)</td><td>&mdash;</td><td>&mdash;</td><td>$55&ndash;$80</td><td>$75&ndash;$125+</td></tr>
    <tr><td>Birthday / anniversary</td><td>$12&ndash;$18</td><td>$20&ndash;$35</td><td>$30&ndash;$50</td><td>$45&ndash;$70</td></tr>
    <tr><td>Holiday party</td><td>$15&ndash;$22</td><td>$25&ndash;$40</td><td>$35&ndash;$55</td><td>$50&ndash;$80</td></tr>
    <tr><td>Nonprofit / fundraiser</td><td>$12&ndash;$18</td><td>$20&ndash;$32</td><td>$30&ndash;$50</td><td>$45&ndash;$65</td></tr>
    <tr><td>Sports / outdoor</td><td>$8&ndash;$14</td><td>$15&ndash;$25</td><td>$25&ndash;$40</td><td>&mdash;</td></tr>
  </tbody>
</table>
<p>
  If your calculated price sits well below the band for that event type, you have probably
  missed a cost. If it sits well above, either your cost base needs attention or you are
  selling something the band does not describe &mdash; which is a positioning question, not
  a pricing one.
</p>

<h2>Minimums are a pricing tool, not a courtesy</h2>
<p>
  Small events are where margin goes to die, because the fixed costs do not shrink with the
  guest count. A twelve-person full-service event needs an event captain the same as a
  sixty-person one.
</p>
<p>
  Reasonable minimum thresholds look roughly like this:
</p>
<table>
  <thead><tr><th>Service type</th><th>Minimum</th><th>Minimum guests</th><th>Why</th></tr></thead>
  <tbody>
    <tr><td>Drop-off delivery</td><td>$150&ndash;$250</td><td>10</td><td>Below this the delivery costs more than the job earns. Offer pickup instead.</td></tr>
    <tr><td>Buffet with staff</td><td>$500&ndash;$750</td><td>25</td><td>You need a minimum staff count to execute at all.</td></tr>
    <tr><td>Full-service</td><td>$1,500&ndash;$2,000</td><td>50</td><td>A captain plus a full team makes small events unprofitable.</td></tr>
    <tr><td>Plated service</td><td>$2,500&ndash;$3,000</td><td>50</td><td>Kitchen complexity requires scale.</td></tr>
    <tr><td>Bar service (add-on)</td><td>$300&ndash;$500</td><td>25</td><td>Bartender plus setup needs volume to justify.</td></tr>
  </tbody>
</table>
<p>
  Publishing minimums also does useful qualifying work before a call. The enquiries that
  fall away were the ones that were going to cost you money.
</p>

<h2>Was it actually a good job? The benchmarks</h2>
<p>
  After the event, the quote only matters relative to what the job consumed. As a
  percentage of revenue:
</p>
<table>
  <thead><tr><th>Cost category</th><th>Target</th><th>Warning zone</th><th>Action needed</th></tr></thead>
  <tbody>
    <tr><td>Food cost</td><td>28&ndash;35%</td><td>35&ndash;40%</td><td>40%+</td></tr>
    <tr><td>Labor cost</td><td>25&ndash;35%</td><td>35&ndash;40%</td><td>40%+</td></tr>
    <tr><td>Overhead / other</td><td>8&ndash;12%</td><td>12&ndash;15%</td><td>15%+</td></tr>
    <tr><td>Total cost</td><td>65&ndash;75%</td><td>75&ndash;85%</td><td>85%+</td></tr>
    <tr><td>Profit margin</td><td>20&ndash;35%</td><td>15&ndash;20%</td><td>Below 15%</td></tr>
  </tbody>
</table>
<p>
  Run this per event rather than per month. A monthly average hides the pattern that
  matters &mdash; which <em>kind</em> of event loses money. Most caterers who track this for
  a quarter discover one event type they have been subsidising, usually the one they take
  on because it feels like it keeps the team busy.
</p>

<h2>Build tiers so the upsell is structural</h2>
<p>
  A single price invites negotiation. Three or four tiers change the question from "can you
  do it cheaper" to "which of these do I want", which is a far better conversation to be
  having.
</p>
<p>
  Tiers work when each one is genuinely different in what it costs you to deliver &mdash;
  drop-off, buffet with staff, full-service with a captain, plated with a tasting. And
  because the higher tiers carry more of the work you are actually good at, they can carry
  a higher target margin: something like 20% at the entry tier rising to 35% at the top is
  a reasonable shape.
</p>
<p>
  The practical effect is that the upsell stops being a sales technique and becomes a
  description of what is included. "We can add an event captain to coordinate everything so
  you do not have to" is not a pitch; it is the difference between two tiers.
</p>

<h2>Premiums you should be charging and probably are not</h2>
<ul>
  <li><strong>Late booking.</strong> Events booked inside seven days disrupt purchasing and
      staffing. A 15&ndash;25% premium is normal and defensible.</li>
  <li><strong>Weekends and holidays.</strong> Peak dates have an opportunity cost, because
      taking one means turning another away. 10&ndash;20%, communicated upfront.</li>
  <li><strong>Deposits.</strong> Not a premium, but a cash-flow tool: 50% to book, balance
      due about a week before. If you are funding food purchases out of your own working
      capital until after the event, that is a problem the deposit structure solves.</li>
</ul>

<h2>The four mistakes that cost the most</h2>
<ol>
  <li><strong>Pricing labor against the event window.</strong> Prep and breakdown are hours
      you pay for. Count them.</li>
  <li><strong>Adding the margin instead of dividing by its inverse.</strong> A quiet
      five-point error on every quote you send.</li>
  <li><strong>Treating overhead as a rounding error.</strong> Mileage, rentals, propane,
      ice and packaging are most of the profit on a thin job.</li>
  <li><strong>Having no minimums.</strong> Small events do not scale down; they just lose
      less revenue against the same fixed cost.</li>
</ol>

<h2>Where to start</h2>
<p>
  Take the last three events you catered &mdash; ideally one that felt good, one that felt
  marginal and one you are not sure about. Rebuild each one against all three cost buckets
  with honest labor hours, and work out the actual margin.
</p>
<p>
  The point is not the three numbers. It is the pattern they reveal: nearly every catering
  operation has one event type, or one service style, or one guest-count band that is
  quietly funded by the others. You cannot fix that until you can see it, and you cannot
  see it from a monthly P&amp;L.
</p>
<p>
  If that sounds like work you would rather do once, properly, with the structure already
  built: <a href="../catering-profit.html">The Catering Profit System</a> includes the
  full-cost calculator this method is built on, the quick-reference card, and the service
  tier template. And if you would rather someone looked at your actual numbers,
  <a href="../catering-consulting.html">catering consulting</a> explains how that works.
</p>
""",
        "cta_h": "Want to know which events are funding the others?",
        "cta_p": "The Profit Leak Snapshot is 90 minutes on your actual numbers "
                 "&mdash; costed by event rather than averaged by month, so the "
                 "job type quietly losing money has somewhere to show up. You "
                 "leave with your top three leaks and the order to fix them in. "
                 "$350, credited toward whatever follows.",
    },
    {
        "slug": "blog/busy-but-not-profitable.html",
        "title": "Why Your Restaurant Is Busy But Not Profitable | Tre Coleman",
        "h1": "Why Your Restaurant Is Busy But Not Profitable",
        "description": "Full dining room, flat bank balance. The four places "
                       "independent restaurants lose margin while volume looks "
                       "healthy, and how to tell which one is yours.",
        "read": "9 min read",
        "body": """
<p>
  There is a specific kind of frustration that comes from a good night. The room was
  full, the tickets kept coming, the team was moving — and at the end of the month the
  number at the bottom of the P&amp;L looks almost exactly like it did when you were
  quieter. Volume went up. Profit did not follow.
</p>
<p>
  This is one of the most common positions an independent operator ends up in, and it is
  almost never caused by one big problem. It is caused by three or four ordinary ones
  compounding, each individually small enough to explain away.
</p>

<h2>Volume amplifies whatever your margins already are</h2>
<p>
  The uncomfortable arithmetic is this: if your contribution margin per cover is thin,
  serving more covers does not fix it. It scales it. More guests means more food cost,
  more labour hours, more wear, more waste — and if the gap between what a cover brings
  in and what it costs to produce is too small, growth just moves more money through the
  business without leaving more behind.
</p>
<p>
  Operators often respond to flat profit by chasing more traffic, which is the one lever
  that reliably makes a margin problem worse. Before you spend on filling more seats, it
  is worth knowing what the seats you already fill actually return.
</p>

<h2>The four places it usually goes</h2>

<h3>1. Item mix, not item price</h3>
<p>
  Most menus contain two or three items that are genuinely unprofitable at current cost,
  and they usually survive because nobody has run the numbers since the last supplier
  increase. They are not obviously bad — they sell. That is what makes them expensive.
</p>
<p>
  The question is not what each item costs as a percentage. It is what each item
  <em>contributes in dollars</em> after food cost, and how often it sells. An item at 55%
  food cost that sells twenty times a week is doing real damage, and it will not show up
  in a headline food-cost percentage that averages it with everything else. This is the
  whole subject of <a href="menu-engineering-guide.html">menu engineering</a>, and it is
  usually the fastest place to find money.
</p>

<h3>2. Labour scheduled by habit</h3>
<p>
  Labour is the fastest-moving cost you control, and the one most often set from memory.
  If your schedule looks roughly the same every week regardless of what sales did, you are
  paying for a pattern rather than for demand.
</p>
<p>
  The tell is overtime that appears consistently rather than occasionally. Consistent
  overtime is not a staffing emergency; it is a scheduling model that does not match the
  business. <a href="restaurant-labor-cost.html">Getting labour under control</a> is
  usually about matching hours to sales patterns before it is about cutting anyone.
</p>

<h3>3. Waste nobody is counting</h3>
<p>
  Prep for a Saturday that did not arrive. Over-portioning that drifted up over months.
  Receiving that nobody checks against the invoice. Each of these is small per occurrence,
  invisible in a monthly total, and continuous.
</p>
<p>
  The reason waste persists is not carelessness — it is that nothing measures it. An
  operation with no waste log does not have less waste; it has unmeasured waste.
</p>

<h3>4. Inconsistency between shifts</h3>
<p>
  If the Tuesday team runs the operation differently from the Friday team, you are running
  two restaurants with one P&amp;L. The difference shows up as variable food cost,
  variable ticket times and variable guest experience, and it averages into numbers that
  look merely mediocre rather than revealing that half your shifts are fine.
</p>
<p>
  This is the problem that <a href="../sops-training.html">written procedures and role
  training</a> solve, and it is the one most likely to be dismissed as a people problem
  when it is a documentation problem.
</p>

<h2>How to find out which one is yours</h2>
<p>
  You do not need a full audit to narrow this down. You need four weeks of three things:
</p>
<ul>
  <li><strong>Your P&amp;L</strong>, at enough granularity that food, labour and
      occupancy are separable</li>
  <li><strong>Labour reports</strong> showing scheduled versus actual hours, and overtime
      by week</li>
  <li><strong>Item-level sales mix</strong> from your POS — what sold, how often</li>
</ul>
<p>
  Lay those three beside each other and the dominant leak usually becomes obvious within
  an hour. If food cost is stable but labour swings week to week, it is scheduling. If
  both are stable but profit is still thin, it is mix or pricing. If everything is
  volatile, it is consistency, and the fix starts with documentation rather than numbers.
</p>

<h2>The cost of waiting</h2>
<p>
  The reason this problem persists for years rather than months is that none of the four
  causes produces a crisis. A leak of $2,000 a month is invisible on any given Tuesday and
  is $24,000 over a year. That is the actual shape of it: not a disaster, just a steady
  subtraction that never announces itself.
</p>
<p>
  Most operators notice in a quiet season, when the volume that was covering the gap stops
  arriving. That is the worst possible time to start looking, because by then cash is
  tight and the obvious fixes — cut labour, cut menu, cut marketing — are the ones most
  likely to make next season worse.
</p>

<h2>Where to start</h2>
<p>
  If you want to work it yourself, pull those three reports and start with item mix; it
  has the shortest path from finding something to fixing it. The
  <a href="../audit.html">free operations audit</a> walks the same five areas in about ten
  minutes and will tell you which to look at first.
</p>
""",
        "cta_h": "Want someone to read the numbers with you?",
        "cta_p": "The Profit Leak Snapshot is a 90-minute session on four weeks "
                 "of your P&amp;Ls, labor reports and item mix. You leave with "
                 "your top three leaks priced in dollars and a prioritised fix "
                 "list. $350, credited toward anything that follows.",
    },
    {
        "slug": "blog/restaurant-labor-cost.html",
        "title": "How to Lower Restaurant Labor Cost | Tre Coleman",
        "h1": "How to Lower Restaurant Labor Cost Without Cutting Service",
        "description": "Labor is the fastest-moving cost you control. How to "
                       "build a schedule from sales patterns instead of habit, "
                       "and why cutting hours is usually the wrong first move.",
        "read": "8 min read",
        "body": """
<p>
  When labour runs high, the instinct is to cut hours. It is the fastest lever and the
  most visible, and it is usually the wrong one to pull first — because high labour cost
  is far more often a <em>distribution</em> problem than a <em>volume</em> problem.
</p>
<p>
  You can have the right number of hours in the week and still be paying too much for
  them, because they are in the wrong places.
</p>

<h2>Start by separating the two questions</h2>
<p>
  There are only two reasons labour cost is too high:
</p>
<ol>
  <li>You are buying more hours than the sales support</li>
  <li>You are buying the right number of hours at the wrong times, or at premium rates</li>
</ol>
<p>
  These need opposite responses. Cutting hours when the real problem is distribution means
  you end up understaffed at peak and still overstaffed at open — worse service and the
  same cost. So establish which one you have before acting.
</p>
<p>
  The quickest diagnostic: pull four weeks of sales by hour alongside labour hours by
  hour. If the two curves have roughly the same shape and labour is simply too tall, it is
  volume. If the shapes do not match — labour flat while sales peak and trough — it is
  distribution, and that is the more common finding.
</p>

<h2>Overtime is a structural signal, not an exception</h2>
<p>
  Occasional overtime is normal; someone is sick, a party books late. Overtime that
  appears every week is not an exception, it is part of your schedule, and it is the most
  expensive hour you buy.
</p>
<p>
  Work the arithmetic on your own numbers. Take one extra overtime hour per shift, five
  shifts a week, at time-and-a-half on your actual wage. Multiply by 52. For most
  independent operations that single line is larger than any menu change you were
  considering, and unlike a menu change it requires no guest to behave differently.
</p>
<p>
  Recurring overtime almost always traces to one of three things: a schedule built before
  you knew your real sales pattern, a role only one person can cover, or a close that
  routinely runs past its planned time. All three are fixable without touching headcount.
</p>

<h2>Build the schedule from sales, not from last week</h2>
<p>
  Most schedules are copied forward. Last week's schedule becomes this week's, adjusted
  for who asked for time off. That means the schedule encodes whatever the business looked
  like whenever someone last built it from scratch — often years ago, at a different
  volume.
</p>
<p>
  The alternative is not complicated:
</p>
<ul>
  <li>Pull sales by day-part for the last 8–12 weeks, so seasonality is visible</li>
  <li>Set a target labour percentage per day-part, not just an overall target — lunch and
      dinner rarely support the same ratio</li>
  <li>Schedule to the pattern, then set a guardrail: who leaves first if sales come in
      under, and who is called if they come in over</li>
  <li>Compare scheduled to actual every week and ask why they differ</li>
</ul>
<p>
  That last step is the one that makes the rest hold. A schedule nobody reviews against
  actuals drifts straight back to habit within a month.
</p>

<h2>Cross-training is a labour strategy</h2>
<p>
  If one person is the only one who can run a station, you are not staffing that station —
  you are staffing that person. It forces overtime when they are needed, idle cost when
  they are not, and it means their holiday is an operational event.
</p>
<p>
  Cross-training reads like a training initiative and functions as a cost control. Two
  people who can each cover two stations give you scheduling flexibility that no amount of
  careful rota-building can replicate. This is one of the practical returns of having
  <a href="../sops-training.html">written procedures and role scorecards</a>: you cannot
  cross-train quickly against knowledge that only exists in someone's head.
</p>

<h2>What not to do</h2>
<p>
  <strong>Do not cut the shift that protects the guest experience.</strong> The hours that
  look most cuttable on a spreadsheet are often the ones absorbing variability — the
  floater, the early prep, the extra closer. Removing them does not remove the work; it
  moves it onto people who are already busy, and it surfaces as slower tickets and
  inconsistency.
</p>
<p>
  <strong>Do not chase a benchmark percentage you did not set.</strong> A target labour
  percentage is only meaningful against your own format, service style and price point. A
  full-service restaurant and a counter-service operation have no business sharing a
  number.
</p>
<p>
  <strong>Do not fix labour in isolation.</strong> Labour, menu mix and prep planning are
  one system. Trimming hours while leaving a menu that requires heavy prep just relocates
  the problem to quality.
</p>

<h2>Where to start this week</h2>
<p>
  Pull four weeks of labour reports and find every overtime hour. Group them by person,
  role and day. Nearly always, a pattern appears — one role, one shift, one recurring
  cause. Fixing that single pattern is usually worth more than a general instruction to
  everyone to watch their hours, and it costs nobody their shift.
</p>
<p>
  If labour is one of several things that feel off at once, the
  <a href="busy-but-not-profitable.html">busy-but-not-profitable problem</a> covers how to
  work out which to address first.
</p>
""",
        "cta_h": "Not sure if it's volume or distribution?",
        "cta_p": "The Profit Leak Snapshot reviews four weeks of labor reports "
                 "against your sales patterns and item mix. You leave knowing "
                 "which of the two you have and what to change first. $350.",
    },
    {
        "slug": "blog/fractional-coo-vs-consultant.html",
        "title": "Fractional COO vs Restaurant Consultant: Which Do You Need? | Tre Coleman",
        "h1": "Fractional COO vs Restaurant Consultant: Which Do You Need?",
        "description": "Project consulting and ongoing fractional leadership "
                       "solve different problems. How to tell which one your "
                       "operation actually needs — including when it's neither.",
        "read": "7 min read",
        "body": """
<p>
  These two get used interchangeably and they are not the same purchase. One buys you an
  answer. The other buys you someone who makes sure the answer gets implemented. Choosing
  the wrong one is the most common way operators waste money on outside help.
</p>

<h2>The actual difference</h2>
<p>
  A <strong>consultant on a project</strong> is scoped to a defined deliverable with an
  end date. You have identified a problem — the menu, the training system, the local
  marketing — and you are buying the expertise and the hours to build the fix. When the
  deliverable is handed over, the engagement is finished.
</p>
<p>
  A <strong>fractional COO</strong> is scoped to an ongoing responsibility. There is no
  single deliverable. You are buying weekly attention on the operation as a whole: KPI
  review, decisions between meetings, and the pressure that keeps change moving when the
  week gets busy.
</p>
<p>
  The distinction that matters: a project ends when the work is <em>built</em>. Fractional
  leadership continues because most operational change fails at <em>adoption</em>, not at
  design.
</p>

<h2>When a project is the right answer</h2>
<p>
  Pick project work when you can finish this sentence specifically: "I need someone to
  build me ___." A menu rebuilt on contribution margin. An SOP library. A twelve-week
  local marketing calendar. An AI workflow for reporting.
</p>
<p>
  Projects suit operations that have a working management layer — someone who will own the
  thing once it exists. The deliverable lands, your team runs it, and you have bought a
  capability rather than a dependency.
</p>
<p>
  Projects are also the right answer when budget is finite and you want a defined cost.
  Scoped work has a number attached to it; ongoing support is a monthly commitment.
</p>

<h2>When fractional leadership is the right answer</h2>
<p>
  Pick ongoing support when the honest problem is not knowing what to do — it is that
  nothing survives contact with a busy week.
</p>
<p>
  That is extremely common and not a character flaw. Operators are pulled into the
  immediate all day; strategic work has no deadline and therefore always loses. A weekly
  cadence with someone outside the business is, more than anything else, a structural
  answer to that.
</p>
<p>
  It also suits operations where the decisions are coming faster than the owner can think
  them through alone — a second location, adding catering, a management transition. In
  those periods the useful thing is not a document, it is judgement available repeatedly.
</p>

<h2>When it is neither</h2>
<p>
  Worth saying plainly: there is a size below which ongoing retainer support does not make
  arithmetic sense. If the monthly fee is a large fraction of your monthly profit, the
  improvement required to justify it is unrealistic.
</p>
<p>
  The usual sequence that does work: a diagnostic first, then one project against whatever
  the diagnostic found, and ongoing support only if implementation turns out to be the
  bottleneck. Buying a retainer before you know the problem is buying attention you cannot
  yet direct.
</p>
<p>
  Equally: if you have a specific, bounded question — a lease, a pricing sanity check, a
  second opinion on a hire — neither model fits. That is an hour of someone's time, not an
  engagement.
</p>

<h2>Questions that resolve it quickly</h2>
<ul>
  <li><strong>Can you name the deliverable?</strong> If yes, it is probably a project. If
      you find yourself describing a situation rather than a thing, it is probably
      ongoing.</li>
  <li><strong>Have you tried to fix this before?</strong> If you have, and it did not
      stick, the gap is implementation — which is what a cadence addresses and a document
      does not.</li>
  <li><strong>Who owns it afterwards?</strong> If nobody on your team can own the result,
      a project will become shelfware. Either build the owner first or buy the ongoing
      support.</li>
  <li><strong>What does doing nothing cost per month?</strong> If you cannot estimate
      that, start with a diagnostic, because you do not yet know what you are buying.</li>
</ul>

<h2>How this works here</h2>
<p>
  For transparency, since most consulting sites hide this: the diagnostic is
  <a href="../profit-leak-snapshot.html">$350</a>, project work is scoped per problem in
  the $2,500–$50,000 range, and <a href="../advisory.html">ongoing advisory</a> is
  $2,000/month aimed at operations above roughly $1M. The $350 credits toward whatever
  follows, specifically so that the diagnosis does not have to be a separate financial
  decision from the fix.
</p>
<p>
  If the pricing question is the one you actually came with,
  <a href="restaurant-consultant-cost.html">what restaurant consultants cost</a> breaks
  down all four common models.
</p>
""",
        "cta_h": "Still not sure which you need?",
        "cta_p": "Start with the diagnostic. 90 minutes on your P&amp;L, labor "
                 "and item mix tells you whether you have a problem to solve or "
                 "an implementation gap to close — and the $350 credits toward "
                 "whichever follows.",
    },
    {
        "slug": "blog/restaurant-profit-and-loss.html",
        "title": "The Restaurant P&L, Line by Line | Tre Coleman",
        "h1": "The Restaurant P&amp;L, Line by Line",
        "description": "A plain-English walk through a restaurant profit and "
                       "loss statement: what each line means, which ones you "
                       "control weekly, and the order to read them in.",
        "read": "10 min read",
        "body": """
<p>
  Most operators can find their P&amp;L and far fewer use it. That is not an intelligence
  problem — it is that the document was designed for accountants, arrives weeks after the
  period it describes, and does not tell you what to do.
</p>
<p>
  It is still the single most useful management document you have, provided you read it in
  the right order and ignore most of it most of the time.
</p>

<h2>Read it in this order</h2>
<p>
  Not top to bottom. Start with the lines you can change this week, then widen out.
</p>
<ol>
  <li>Prime cost (food + labour)</li>
  <li>The components of prime cost separately</li>
  <li>Controllable operating expenses</li>
  <li>Occupancy and fixed costs</li>
  <li>The bottom line</li>
</ol>
<p>
  The bottom line comes last deliberately. It is the output of everything above it, and
  staring at it tells you nothing about which input to touch.
</p>

<h2>Sales</h2>
<p>
  The top line, and the least interesting number on the page. Sales tells you volume; it
  tells you nothing about whether that volume was worth having.
</p>
<p>
  What is worth extracting here is the split — by day-part, by channel, by category. A
  month where sales held steady but the mix moved from entrées to appetisers is a month
  where your margin fell while your top line did not. That movement is invisible on the
  sales line alone.
</p>

<h2>Cost of goods sold</h2>
<p>
  What you spent on the product you sold. Expressed as a percentage of sales, this is your
  food cost — but the percentage is a summary, and summaries hide the thing you need.
</p>
<p>
  A stable food cost percentage can conceal an unprofitable item selling well, offset by a
  profitable one selling badly. The percentage is for spotting <em>movement</em>; item
  mix is for finding <em>cause</em>. If this line moves and you cannot explain it, the
  explanation is in your sales mix report, not here. That is the work covered in
  <a href="menu-engineering-guide.html">menu engineering</a>.
</p>
<p>
  One practical note: this line is only trustworthy if your inventory counts are real. A
  P&amp;L built on estimated inventory produces a food cost that bounces month to month
  for reasons that have nothing to do with the kitchen.
</p>

<h2>Labour</h2>
<p>
  Usually your largest controllable cost and the one that moves fastest. Worth separating
  into at least three parts:
</p>
<ul>
  <li><strong>Hourly</strong> — the part that should flex with sales</li>
  <li><strong>Salaried management</strong> — fixed in the short term</li>
  <li><strong>Taxes and benefits</strong> — often 10–15% on top of wages, and frequently
      forgotten when operators estimate labour cost in their heads</li>
</ul>
<p>
  That third component is why mental arithmetic about labour is usually optimistic. If you
  are reasoning about an extra shift, you are reasoning about more than the hourly rate.
  <a href="restaurant-labor-cost.html">Getting labour under control</a> goes into how to
  schedule against sales rather than habit.
</p>

<h2>Prime cost: the number that matters most</h2>
<p>
  Food plus labour. If you track one figure weekly, track this one.
</p>
<p>
  It matters because the two lines trade against each other. A kitchen can cut food cost
  by prepping everything in-house and spend the saving twice over in labour. Another can
  cut labour by buying prepped product and watch food cost climb. Looking at either in
  isolation lets a real problem hide behind an apparent improvement.
</p>
<p>
  Prime cost is also the number you can act on at a weekly cadence, which the rest of the
  P&amp;L mostly cannot be.
</p>

<h2>Controllable operating expenses</h2>
<p>
  Everything you spend to run the place that is not product or people: supplies, repairs,
  utilities, marketing, credit card fees, delivery commissions.
</p>
<p>
  Individually small, collectively significant, and the category where costs accumulate
  quietly because no single line ever justifies attention. The useful discipline is to
  review this section properly once a quarter rather than skim it monthly. Subscriptions
  that no longer earn their place live here, as do delivery commissions that have grown
  into a major cost since anyone last looked at them.
</p>

<h2>Occupancy and fixed costs</h2>
<p>
  Rent, insurance, licences, loan payments, depreciation. Mostly outside your control
  inside a given year, which is exactly why they deserve a different kind of attention.
</p>
<p>
  Because they are fixed, their <em>percentage</em> moves with sales. Occupancy climbing
  as a percentage while rent has not changed means sales fell. That makes this section a
  useful cross-check on the top line rather than something you act on directly.
</p>

<h2>Net profit</h2>
<p>
  What is left. It is a result, not a lever, and the common mistake is to manage it
  directly — cutting whatever is nearest when it looks thin, which is usually marketing or
  the labour that protects the guest experience, and usually makes next quarter worse.
</p>

<h2>What to actually do with it each month</h2>
<ul>
  <li>Compare against the <strong>same period last year</strong>, not last month. Most
      food-service businesses are seasonal, and month-over-month comparisons mostly
      measure the calendar.</li>
  <li>Look for <strong>movement</strong>, not absolutes. A two-point shift in prime cost
      matters more than whether you hit a benchmark someone else set.</li>
  <li>Pick <strong>one line</strong> to work on until the next statement. P&amp;Ls arrive
      monthly; meaningful operational change takes longer than that.</li>
  <li>Keep a note of <strong>what you changed and when</strong>, so the next statement can
      tell you whether it worked.</li>
</ul>
<p>
  If your P&amp;L does not separate food and labour clearly enough to do this, that is
  worth fixing with your bookkeeper before anything else. A statement you cannot read at
  this granularity is an accounting record rather than a management tool.
</p>
""",
        "cta_h": "Want a second read on yours?",
        "cta_p": "The Profit Leak Snapshot works through four weeks of your "
                 "P&amp;Ls, labor reports and item mix together, which is where "
                 "the causes actually show up. You leave with your top three "
                 "leaks priced in dollars. $350.",
    },
    {
        "slug": "blog/restaurant-sop-templates.html",
        "title": "Restaurant SOPs: What to Document First | Tre Coleman",
        "h1": "Restaurant SOPs: What to Document First",
        "description": "Most restaurant SOP projects fail because they start by "
                       "documenting everything. How to pick the few procedures "
                       "that actually change what happens on a shift.",
        "read": "8 min read",
        "body": """
<p>
  Almost every operator who sets out to document their operation starts in the same place:
  at the beginning, intending to write it all down. Almost all of them stop somewhere
  around the third document, because writing procedures is slow and the shift is now.
</p>
<p>
  The projects that succeed do the opposite. They document very little, pick that little
  carefully, and get it in use before writing anything else.
</p>

<h2>Document where the cost of variation is highest</h2>
<p>
  The criterion is not "what does someone need to know." By that standard everything
  qualifies and you will never finish. The criterion is: <strong>where does it cost you
  money when two people do this differently?</strong>
</p>
<p>
  That narrows a hundred candidate procedures to about eight.
</p>

<h3>Start with these</h3>
<ul>
  <li><strong>Opening and closing checklists</strong> — the highest-frequency, highest-
      consequence procedures in the building. A missed closing step costs you product
      overnight; a missed opening step costs you the first hour of service.</li>
  <li><strong>Portioning and plating for your top ten items</strong> — not every item.
      The ten that drive most of your volume are where portion drift turns into real food
      cost.</li>
  <li><strong>Receiving</strong> — checking deliveries against the invoice. Rarely
      documented, and one of the few procedures that pays for itself the first time it
      catches a short delivery.</li>
  <li><strong>Prep lists and par levels</strong> — the difference between prepping for
      what you expect to sell and prepping for what you prepped last time.</li>
  <li><strong>Cash and close-out</strong> — because the cost of ambiguity here is not
      only financial.</li>
</ul>

<h3>Skip these, at least initially</h3>
<ul>
  <li><strong>Anything performed once a year.</strong> By the time it comes round the
      document is out of date and nobody remembers it exists.</li>
  <li><strong>Anything only one trusted person does, that is not a bottleneck.</strong>
      Document it when you are training a second person, not before.</li>
  <li><strong>Company values and culture statements.</strong> Worth having. Not an SOP,
      and not what fixes a Friday.</li>
  <li><strong>Procedures for equipment you are about to replace.</strong></li>
</ul>

<h2>Format decides whether it gets used</h2>
<p>
  The most common reason documentation fails is not that it is wrong. It is that it is
  unusable at the moment of use.
</p>
<p>
  A procedure gets consulted mid-shift, standing up, with wet hands, under time pressure.
  That rules out most of what people produce:
</p>
<ul>
  <li><strong>One page.</strong> If it does not fit on one page it is two procedures, or
      it contains explanation that belongs in training rather than reference.</li>
  <li><strong>Checkboxes, not paragraphs.</strong> Prose describes; a checklist tracks
      where you are. Those are different jobs.</li>
  <li><strong>Photographs for anything visual.</strong> A plating photo settles a
      disagreement that four sentences will not.</li>
  <li><strong>Located where the work happens.</strong> A binder in the office is a binder
      nobody opens.</li>
</ul>

<h2>Write it with the people who do it</h2>
<p>
  Procedures written by an owner alone describe how the owner believes the work is done.
  Procedures written with the team describe how it is actually done — including the
  workaround somebody invented two years ago that everybody now relies on.
</p>
<p>
  There is also an adoption effect. People follow procedures they helped write at a
  noticeably higher rate than procedures that appear from above, and it costs nothing to
  get that for free.
</p>
<p>
  The practical version: draft from observation rather than from memory, then walk it
  through with whoever runs that station and correct what you got wrong. You will always
  have got something wrong.
</p>

<h2>Role scorecards, not job descriptions</h2>
<p>
  A job description lists duties. A scorecard states what good looks like for that role —
  the handful of things the person is accountable for, expressed so that both of you can
  tell whether they are happening.
</p>
<p>
  This is what makes training repeatable rather than personal. Without it, "is this person
  working out?" is a judgement call that varies by who is asked. With it, it is a
  conversation about four or five specific things.
</p>

<h2>Keeping it from going stale</h2>
<p>
  A library that is not maintained is worse than none, because people stop trusting any of
  it once they find one page that is wrong.
</p>
<p>
  Two habits are enough. Put a review date on every document, and make updating the
  procedure part of changing the process — if a prep method changes on Tuesday, the page
  changes Tuesday, not at some future review. One page, owned by whoever runs that area.
</p>

<h2>What this is actually for</h2>
<p>
  The goal is not a complete manual. It is that the operation runs the same way whether or
  not you are standing in it — which is the thing that makes time off possible, makes a
  second location conceivable, and makes the business worth something to someone else.
</p>
<p>
  Eight well-used pages get you most of that. A hundred unread ones get you none of it.
  If you want this built rather than attempted,
  <a href="../sops-training.html">SOPs and training systems</a> is the engagement for it.
</p>
""",
        "cta_h": "Want this built rather than started?",
        "cta_p": "Most SOP projects stall at document three. A scoped project "
                 "builds the few that matter, written with your team and in use "
                 "before the engagement ends. Start with a $350 Snapshot to "
                 "confirm documentation is actually your bottleneck.",
    },
]


def ld(obj):
    return ('<script type="application/ld+json">\n'
            + json.dumps(obj, indent=2, ensure_ascii=False)
            + "\n</script>\n")


def build(shell, art):
    slug = art["slug"]
    url = f"{SITE}/{slug}"
    bare_h1 = re.sub(r"&amp;", "&", art["h1"])

    schema = ld({
        "@context": "https://schema.org", "@type": "BlogPosting",
        "headline": bare_h1, "url": url,
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "datePublished": PUBLISHED, "dateModified": PUBLISHED,
        "author": {"@id": f"{SITE}/#person"},
        "publisher": {"@id": f"{SITE}/#business"},
        "image": OG_CARD, "inLanguage": "en-US",
        "description": art["description"],
    }) + ld({
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Blog",
             "item": f"{SITE}/blog.html"},
            {"@type": "ListItem", "position": 3, "name": bare_h1, "item": url},
        ],
    })

    head = f"""<title>{art['title']}</title>
<meta content="{art['description']}" name="description"/>
<meta content="article" property="og:type"/>
<meta content="{bare_h1}" property="og:title"/>
<meta content="{url}" property="og:url"/>
<meta content="{art['description']}" property="og:description"/>
<meta content="{OG_CARD}" property="og:image"/>
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:image:alt" content="{OG_ALT}" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{bare_h1}" />
<meta name="twitter:description" content="{art['description']}" />
<meta name="twitter:url" content="{url}" />
<meta name="twitter:image" content="{OG_CARD}" />
<link rel="canonical" href="{url}" />
{schema}"""

    prefix = shell[:shell.index("<title>")]
    middle = shell[shell.index('<link rel="preconnect"'):
                   shell.index('<main id="main-content">')]
    # Strip the shell's own canonical and JSON-LD, or the new article inherits
    # the source article's identity.
    middle = re.sub(r'\s*<link rel="canonical"[^>]*>', "", middle)
    middle = re.sub(r'\s*<script type="application/ld\+json">.*?</script>',
                    "", middle, flags=re.S)
    suffix = shell[shell.index("</article>"):]

    crumbs = (
        '<nav class="breadcrumbs" aria-label="Breadcrumb">'
        '<a href="../index.html">Home</a> <span aria-hidden="true">›</span> '
        '<a href="../blog.html">Blog</a> <span aria-hidden="true">›</span> '
        f'<span aria-current="page">{bare_h1}</span></nav>'
    )

    body = f"""<main id="main-content">
{crumbs}
<article>
<a class="back-link" href="../blog.html">&#8592; Back to all posts</a>
<div class="post-header">
<h1>{art['h1']}</h1>
<div class="post-meta">By <a rel="author" href="../about.html">Tre Coleman</a> &bull; <time datetime="{PUBLISHED}">{PRETTY_DATE}</time> &bull; Operations &bull; {art['read']}</div>
</div>
<div class="post-content">
{art['body'].strip()}
</div>
<div class="cta-section">
<h3>{art['cta_h']}</h3>
<p>{art['cta_p']}</p>
<a class="button" href="../profit-leak-snapshot.html">Book Your Snapshot</a>
</div>
"""
    return prefix + head + middle + body + suffix


def main():
    with open(SHELL, encoding="utf-8") as fh:
        shell = fh.read()

    for art in ARTICLES:
        html = build(shell, art)
        os.makedirs(os.path.dirname(art["slug"]), exist_ok=True)
        with open(art["slug"], "w", encoding="utf-8") as fh:
            fh.write(html)
        words = len(re.sub(r"<[^>]+>", " ", art["body"]).split())
        print(f"  {art['slug']:<45} ~{words} words")


if __name__ == "__main__":
    main()
