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
screenshot of a real artifact, the social sharing card, and the module hero
inside the course.

## Course module heroes

One photograph per module, five per course, supplied by Tre -- not sourced.
The redesigned module page has a slot for it above the lesson index.

    images/course/profit/module-1.webp   ->  course/module-1.html
    images/course/people/module-1.webp   ->  course/people/module-1.html

`tools/wire_course_heroes.py` writes the markup. Drop the file in and run it;
it reads the dimensions from the file itself, so there is no number to keep in
step. It is re-runnable: replacing a file updates the dimensions, and deleting
one removes the figure again.

The page is designed to work with no hero at all -- a module with no file
keeps its typographic hero rather than showing an empty frame -- so the five
can arrive one at a time. `.webp`, `.jpg` and `.png` are all read; `.webp` is
preferred for the reasons below.

`alt` is deliberately empty on these. The hero repeats the module title set
in the `<h1>` beside it, so a screen reader announcing it again is noise.
That is the accessible choice for decoration, not an omission -- an image
that carried information would need real alt text instead.

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

Nothing. Two files were carried unreferenced for a while and have now been
deleted: `hero-restaurant-operations.webp` (70.5 KB, the generic restaurant
interior that was the hero of eleven pages until the redesign removed it) and
`tre-headshot.jpg` (200x200, which ~20 pages had pointed `og:image` at while
declaring 1200x630). Both remain in git history if either is ever wanted back.

`tools/check_site.py`'s `unused-img` check only warns above 100 KB, so it said
nothing about either of them. That threshold is deliberate -- it exists to
catch weight, not tidiness -- but it does mean "no warning" is not the same as
"nothing unused".

## Requirements for anything added here

- `width`, `height` and a descriptive `alt` on every `<img>`, or
  `check_site.py`'s `images` check fails and Lighthouse errors on
  `unsized-images`.
- WebP, unless the format genuinely cannot be (`og-card.jpg` stays JPEG
  because some social scrapers still handle WebP badly).
- Under 400 KB per file, which is where `check_weight` errors.
- Referenced from a page, or it ships to every visitor for nothing.
