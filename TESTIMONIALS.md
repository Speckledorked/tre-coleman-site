# Testimonials — collection and markup

**Current state:** the site has exactly one testimonial, on `index.html`, and it
is anonymous:

> "Tre doesn't just talk about restaurant operations; he's lived them. He found
> labor leaks we'd been ignoring for years and helped us build a system to stop
> them for good."
> — Multi-Unit Franchisee, Virginia

That is the entire social proof on a site selling a $2,000/month advisory
retainer. It is the largest conversion gap on the site, and it is the one thing
in the whole audit that cannot be built from the repository — testimonials have
to come from real clients who agree to be named.

---

## Why `Review` schema is deliberately absent

The audit recommends against adding `Review` or `AggregateRating` markup, and
that remains correct while the only testimonial is anonymous:

- Google requires a named `author` on `Review`. "Multi-Unit Franchisee" is not
  a name.
- Self-serving `AggregateRating` on your own site — you rating yourself — is
  against Google's structured data guidelines and carries manual-action risk.
- Invented or incentivised reviews breach FTC endorsement rules.

So the absence is not an oversight to fix with markup. It is a content problem
that markup follows.

---

## What makes a usable testimonial

Ranked by how much weight a prospect actually puts on it:

| Weakest | | Strongest |
|---|---|---|
| "Great to work with" | → | A specific problem, what changed, and a number |
| Anonymous | → | Name, role, business type, market |
| Generic praise | → | Language a peer operator would recognise as real |

A testimonial that says *"our overtime was built into every week and we
couldn't see it — three months later we'd taken a day a week back off the
schedule"* does more than five that say *"highly recommend."*

### Ask for these four things

1. **What was the problem before we started** — in their words, not yours
2. **What specifically changed** — ideally one number they are comfortable sharing
3. **Name, role and business type** — "Owner, 2-unit fast casual, Richmond" is
   enough; the business name is a bonus, not a requirement
4. **Written permission to publish it on the website**

Point 4 matters. Verbal agreement is not a record, and you want this on file
before it appears publicly.

---

## How to ask

Timing: shortly after a visible result, not at the end of an engagement. The
specifics are still fresh and the goodwill is at its peak.

Make it easy to say yes. Rather than "would you write me a testimonial,"
which puts the work on them, offer to draft from something they already said
and let them edit it:

> You mentioned on our last call that the schedule change took a day a week
> back. Would you be comfortable with me using that on the site? Happy to draft
> something from what you said and send it over for you to change or reject —
> and I'd want to credit you as [role, business type, market], or less if you'd
> prefer.

Never offer anything of value in exchange. Incentivised endorsements require
disclosure under FTC rules and devalue the testimonial anyway.

---

## Where they should go

In priority order:

1. **`profit-leak-snapshot.html`** — the page where the $350 decision is made
2. **`advisory.html`** — the highest-value, highest-trust-requirement offer
3. **`index.html`** — replace or supplement the anonymous one
4. **The relevant service page** — a menu engineering testimonial on
   `menu-engineering.html` beats a general one on the homepage

Place them near the decision point, not in a block at the bottom of the page.

---

## Enabling `Review` schema once you have named testimonials

With at least one named, permissioned testimonial, this becomes valid. Add to
the page carrying the testimonial, and make sure the visible text matches
exactly:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Review",
  "itemReviewed": { "@id": "https://trecoleman.com/#business" },
  "author": {
    "@type": "Person",
    "name": "REAL NAME HERE"
  },
  "reviewBody": "The testimonial text, matching the visible page exactly.",
  "datePublished": "YYYY-MM-DD"
}
</script>
```

Notes:

- `reviewRating` is optional and omitted deliberately — you are not running a
  star-rating system, and inventing one would be worse than having none.
- Do **not** add `AggregateRating` to your own site. That is the part Google
  treats as self-serving.
- Google reviews on your Business Profile are a separate and arguably more
  valuable track; those carry weight precisely because you do not control them.

---

## Related

- `CLAIMS.md` — the case studies on `index.html` ("Results from the Field")
  need client permission for anonymised use, which is the same conversation
- `SEO_AUDIT.md` §5.4 — Google Business Profile reviews, the external track
