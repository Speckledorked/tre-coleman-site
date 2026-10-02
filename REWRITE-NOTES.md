# Rewriting the five original posts

A working list, not an essay. Each post has a short section with what to cut,
what to keep, and where your numbers go.

**The audit row said these "read as generic industry content." That is still
true of the bodies, and it is worth being precise about why**, because at a
glance they now look fixed. Each post opens with one or two sharp,
specific sentences. Then the original draft resumes mid-paragraph, in a
different voice, usually restating what the new opening just said.

So the problem is no longer "these are generic." It is that each post is two
documents stitched together, and the seam is visible in the first fifteen
seconds of reading.

> **The seams are now closed** — see `tools/fix_article_seams.py`. That was the
> mechanical half, and it needed no new writing. Everything below about voice,
> filler and missing numbers is still open and still yours, because it cannot
> be done without your material.

---

## The seam, in all five — DONE

In each case the **bold** text is the new opening and what follows is the old
draft picking up where it left off.

| Post | The seam |
|---|---|
| `restaurant-profit-leaks` | **"...almost always a set of small, continuous leaks rather than one dramatic problem."** → "You see the sales numbers, but the cash in the bank doesn't quite add up." |
| `restaurant-systems-for-growth` | **"...which puts a hard ceiling on how large the business can get"** → "– putting out fires, managing staff, and ensuring customer satisfaction." |
| `menu-engineering-guide` | **"...nobody has run the numbers since the last supplier increase."** → "Yet, many restaurants..." |
| `fractional-coo-for-restaurants` | **"...the number of decisions one person can make well in a week."** → "The demands of daily operations become overwhelming..." |
| `scaling-a-catering-business` | **"...the margin ends up thinner than it was at half the size."** → "However, many operators find that as their catering volume increases..." |

All five were confirmed against the raw HTML, not against extracted text. That
distinction mattered: a sixth finding — a stray space before a comma in
`scaling-a-catering-business` — turned out to be an artifact of stripping a
`</strong>` tag during extraction, and is not in the file. It has been removed
from this list.

Three of the five were mechanically broken rather than merely redundant:

- **`restaurant-profit-leaks`** says the same thing twice in two voices. The
  second sentence is a weaker restatement of the first and can simply go.
- **`restaurant-systems-for-growth`** has a stranded dash. The clause it
  attached to was removed, so the sentence now reads "...how large the business
  can get – putting out fires, managing staff..." which does not parse.
- **`menu-engineering-guide`** and **`scaling-a-catering-business`** open their
  second sentence with "Yet," and "However," — contrastive connectives with
  nothing left to contrast against, because the sentence they were arguing
  with was replaced.

---

## Post by post

### 1. `restaurant-profit-leaks` — 1,081 words. Worst of the five.

Twelve generic markers, the most of any post. The ones to cut on sight:

> "insidious drains on your revenue" · "I'll delve into" · "I understand this
> struggle intimately" · "My approach isn't theoretical" · "echoing my
> no-nonsense, results-driven philosophy" · "The Silent Saboteurs"

The second paragraph is the biggest problem. It is 90 words of self-description
that makes a claim and then tells the reader how to feel about it. It should
either become one sentence of evidence or disappear.

**Claim to verify:** *"Having managed multi-unit restaurant operations for over
a decade."* This appears here and in two other posts. It is on the list in
`CLAIMS.md` and needs a specific, checkable form — which groups, which years,
how many units.

**Where your numbers go:** the article names four leak categories and gives a
figure for none of them. One real example per category — "an extra hour of
overtime across six people is $X a year at $Y an hour" — would do more than the
whole second paragraph.

### 2. `scaling-a-catering-business` — 876 words. Second worst.

Nine markers: "delve into", "leverage", "robust", "thriving", "unlock",
"navigate the", "crucial".

This post now overlaps with the new
[catering pricing article](blog/how-to-price-catering-jobs.html), which covers
costing and margin properly. Decide what this one is *for*: the honest answer is
probably logistics, staffing and capacity as volume grows, with pricing handed
off to the newer piece. Otherwise they compete.

### 3. `restaurant-systems-for-growth` — 907 words.

Six markers: "robust", "vital", "crucial", "thriving".

Beyond the stranded dash, this is the most salvageable of the five. The argument
is sound and specific. It needs the adjectives stripped and one worked example
of a system that actually removed a decision from your week.

**No figures at all.** Not one number in 907 words on a topic that is entirely
about measurable capacity.

### 4. `fractional-coo-for-restaurants` — 835 words.

Only two markers ("unlock", "actionable strategies"), so the prose is nearly
there. The weakness is different: it describes the service without ever saying
what a week actually looks like. It also now overlaps
`fractional-coo-vs-consultant.html`. Make this one the "what it is and how it
runs" piece and let the comparison article do the comparing.

**Claim to verify:** *"extensive multi-unit restaurant management experience."*

### 5. `menu-engineering-guide` — 999 words. Best of the five.

Two markers, and it is the only one of the five that already carries real
figures ($19, $20, 55%, 70%). Those make it readable and they are also the
reason it needs checking first: **if those numbers are illustrative rather than
measured, say so in the text.** An unattributed percentage reads as a result.

---

## Suggested order

1. **`restaurant-profit-leaks`** — worst prose, highest-intent topic, and the
   pillar the cluster links into.
2. **`scaling-a-catering-business`** — resolve the overlap with the new pricing
   article before both compete for the same searches.
3. **`restaurant-systems-for-growth`** — mostly a trim.
4. **`fractional-coo-for-restaurants`** — scope it against the comparison piece.
5. **`menu-engineering-guide`** — label the figures, otherwise leave alone.

## What is left

The seams are closed. What remains in every one of the five is the **second
paragraph**: an "I understand this struggle / in this article I'll delve into"
preamble that says nothing, in a voice that is not yours, and which carries the
two claims needing verification — *"over a decade"* and *"multi-unit"*.

That paragraph is the single highest-value remaining edit, and it is the one
that cannot be done for you: replacing it means choosing between cutting it
outright and turning it into one sentence of real evidence. Either is a
judgement about what you are willing to claim.

After that, in order: the generic markers listed per post above, then the
missing numbers — `restaurant-systems-for-growth` still contains not one figure
in 907 words on a subject that is entirely about measurable capacity.
