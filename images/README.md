# images/

## Art direction

**No stock photography.** The site's visual language is typographic: paper
ground, ink text, hairline rules, and figures set large. Headlines, ledger
rules and numbers carry the page. An earlier version of this file asked for
Unsplash and Pexels searches for "restaurant kitchen" and "business meeting",
which is the opposite of the current direction and produced the generic hero
that was reused on eleven pages before the redesign removed it.

Also avoided, by the same brief: generic illustrations, cartoon graphics,
decorative blobs, gradient backgrounds, glassmorphism, icon libraries, emoji
as iconography, and giant hero graphics that carry no information.

So before adding an image, the question is not "which stock photo" but
"does a picture say something type cannot". Usually it does not. The course
teaser's poster on the homepage is set as HTML text rather than a rendered
slide for exactly this reason: it stays sharp at any density, weighs nothing,
and follows the light and dark themes on its own.

What images are legitimately for here: a real photograph of a real person, a
screenshot of a real artifact, and the social sharing card.

## What is in use

| File | Used by |
|---|---|
| `og-card.jpg` | the `og:image` on every page |
| `advisory-fractional-operations.webp` | `services.html` |
| `ai-integration-restaurants.webp` | `services.html` |
| `local-store-marketing.webp` | `services.html` |
| `menu-engineering-analysis.webp` | `services.html` |
| `restaurant-systems-before-after.webp` | `services.html` |
| `sops-training-systems.webp` | `services.html` |
| `from-the-floor-up-newsletter.webp` | `playbook.html` |
| `tre-coleman-family.webp` | `about.html` |

## What is not in use

Both are still committed; neither is referenced by any page.

- **`hero-restaurant-operations.webp`** — 70.5 KB, 1536×1024. The generic
  restaurant interior that was the hero of eleven pages. The redesign removed
  it everywhere. It is deployed on every build and downloaded by nobody.
- **`tre-headshot.jpg`** — 9.9 KB, 200×200. Never referenced, and too small to
  use at any modern size. A portrait means a new photograph, not an upscale of
  this one. The only real photograph of Tre currently on the site is the family
  shot on `about.html`.

Deleting either is a judgement call for the owner, not for whoever is next in
this directory, which is why they are documented rather than removed.

`tools/check_site.py`'s `unused-img` check only warns above 100 KB, so it says
nothing about either of these. That threshold is deliberate — it exists to
catch weight, not tidiness — but it does mean "no warning" is not the same as
"nothing unused".

## Requirements for anything added here

- `width`, `height` and a descriptive `alt` on every `<img>`, or
  `check_site.py`'s `images` check fails and Lighthouse errors on
  `unsized-images`.
- WebP, unless the format genuinely cannot be (`og-card.jpg` stays JPEG
  because some social scrapers still handle WebP badly).
- Under 400 KB per file, which is where `check_weight` errors.
- Referenced from a page, or it ships to every visitor for nothing.
