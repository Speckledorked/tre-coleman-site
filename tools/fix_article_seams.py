#!/usr/bin/env python3
"""
Close the seam in the five original blog posts.

Each of the five had its opening rewritten and the rest left alone, so the
first paragraph reads as one or two sharp, specific sentences followed by the
original draft resuming mid-paragraph in a different voice. REWRITE-NOTES.md
has the full diagnosis; this script fixes only the mechanical half of it, which
needs no new writing:

  * a restatement of what the new opening just said, deleted
  * a contrastive connective ("Yet," "However,") with nothing left to contrast
    against, deleted
  * one stranded clause list, reattached by reordering the sentence

Every edit below is a deletion, a reorder, or a one-word connective swap. No
sentence is invented and no claim is added. The two substantive points the old
drafts made that the new openings do not — menu items kept out of sentimentality,
and the owner drawn into tactical execution — are kept rather than cut along
with the filler around them.

An earlier revision of this script rewrote the menu-engineering connective into
a new clause. That was writing in the owner's voice, which is the half of
REWRITE-NOTES.md deliberately left to the owner, so it was reverted to the
one-word swap.

What this deliberately does NOT do: the second paragraph of all five is an "I
understand this struggle / in this article I'll delve into" preamble that also
carries the unverified "over a decade" and "multi-unit" claims. Cutting or
replacing it is a voice and evidence decision, not a mechanical one, so it
stays in REWRITE-NOTES.md for the owner.

Run from the repository root:

    python3 tools/fix_article_seams.py
"""

import os

# (path, old, new). Matching is exact and asserted, so a silent no-op is
# impossible — if an article is edited by hand later, this fails loudly rather
# than reporting success over a file it did not change.
EDITS = [
    # ------------------------------------------------------------------ 1
    # "You see the sales numbers, but the cash in the bank doesn't quite add
    # up" is the old draft restating the new first two sentences. The target
    # keyword moves into the surviving sentence so it is not lost with it.
    (
        "blog/restaurant-profit-leaks.html",
        "is almost always a set of small, continuous leaks rather than one "
        "dramatic problem. You see the sales numbers, but the cash in the bank "
        "doesn't quite add up. This disconnect often points to "
        "<strong>profit leaks</strong> – insidious drains on your revenue "
        "that can go unnoticed until they've significantly impacted your "
        "bottom line. These aren't always obvious,",
        "is almost always a set of small, continuous <strong>profit "
        "leaks</strong> rather than one dramatic problem. These aren't always "
        "obvious,",
    ),
    # ------------------------------------------------------------------ 2
    # The clause list had lost the subject it described. Reordering reattaches
    # it to "a specific person is standing in it" without adding a word, and
    # restores the antecedent for the "daily grind" that follows.
    (
        "blog/restaurant-systems-for-growth.html",
        "They stall because the operation only works when a specific person is "
        "standing in it, which puts a hard ceiling on how large the business "
        "can get – putting out fires, managing staff, and ensuring "
        "customer satisfaction.",
        "They stall because the operation only works when a specific person is "
        "standing in it — putting out fires, managing staff, ensuring "
        "customer satisfaction — which puts a hard ceiling on how large "
        "the business can get.",
    ),
    # ------------------------------------------------------------------ 3
    # "Yet" contrasted with a sentence that no longer exists. It becomes
    # "also", which costs one word and turns the sentence into what it now
    # actually is — a second cause alongside the new opening's, sentiment
    # rather than arithmetic — instead of a contradiction of nothing.
    (
        "blog/menu-engineering-guide.html",
        "since the last supplier increase. Yet, many restaurant owners "
        "overlook its strategic potential,",
        "since the last supplier increase. Many restaurant owners also "
        "overlook its strategic potential,",
    ),
    # ------------------------------------------------------------------ 4
    # "The demands of daily operations become overwhelming" restates the new
    # opening. The rest of the sentence does not, so only the clause goes.
    (
        "blog/fractional-coo-for-restaurants.html",
        "the number of decisions one person can make well in a week. The "
        "demands of daily operations become overwhelming, strategic planning "
        "takes a backseat,",
        "the number of decisions one person can make well in a week. Strategic "
        "planning takes a backseat,",
    ),
    # ------------------------------------------------------------------ 5
    # "However" contrasted with nothing, and the sentence restated the new
    # opening almost exactly. Deleted outright.
    (
        "blog/scaling-a-catering-business.html",
        "the margin ends up thinner than it was at half the size. However, "
        "many operators find that as their catering volume increases, so do "
        "their headaches – and often, their losses. What seems like",
        "the margin ends up thinner than it was at half the size. What seems "
        "like",
    ),
]


def main():
    done = 0
    for path, old, new in EDITS:
        with open(path, encoding="utf-8") as fh:
            html = fh.read()
        if new in html and old not in html:
            print(f"  {os.path.basename(path):<42} already closed")
            continue
        if old not in html:
            raise SystemExit(
                f"\n{path}: the text to replace is not present.\n"
                f"The article has been edited since this script was written. "
                f"Re-read it and update the EDITS entry rather than loosening "
                f"the match.\n"
            )
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(html.replace(old, new, 1))
        print(f"  {os.path.basename(path):<42} seam closed")
        done += 1
    print(f"\n{done} article(s) changed")


if __name__ == "__main__":
    main()
