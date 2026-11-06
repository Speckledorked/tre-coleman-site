# Course module hero images — generation prompts

Ten images, one per module, five per course. Drop them in and run
`python3 tools/wire_course_heroes.py`; it reads the dimensions from the file
and writes the markup. Nothing breaks if only some arrive — a module with no
file keeps its typographic hero.

## Specs

| | |
|---|---|
| Aspect | **3:1** — generate at **1800 × 600** |
| Format | WebP, **under 400 KB** (`check_site.py` errors above that) |
| Crop | `object-fit: cover`. On mobile the box is ~2.2:1, so the **sides get cropped** — keep the subject centred with empty space left and right |
| Height on screen | 160px (phone) to 256px (desktop). Detail is lost; favour simple, legible shapes |
| Text | **None.** No signage, no logos, no numbers, no lettering anywhere |

The image sits between a 2px rule above and a hairline below, on a page that
is bone-white in light mode and near-black in dark mode, and the same file is
used in both. So keep it **mid-tone**: no blown-out whites, no crushed blacks,
nothing that only works against one ground.

## Style block — paste this at the start of every prompt

> Documentary photograph, available light only, overcast north-window quality.
> Muted desaturated palette of warm grey, bone, oak, scuffed steel and kraft
> paper. Mid-tone exposure throughout, no blown highlights, no crushed shadows.
> Shot from working height or slightly above, horizontal composition, subject
> centred with generous empty space at left and right. Real used surfaces with
> wear and small imperfections. Calm, plain, unstyled, quiet. Shallow depth of
> field. No people's faces, hands only if a person appears at all.

## Negative prompt

> text, lettering, signage, logos, numbers, watermark, faces, posed models,
> stock-photo styling, food magazine styling, glossy highlights, steam, glow,
> golden hour, neon, teal and orange grade, HDR, oversaturated, gradient
> background, seamless studio backdrop, vignette, bokeh balls, clutter,
> busy composition, tilted horizon, fisheye

---

## The Catering Profit System

**`images/course/profit/module-1.webp` — Labor Cost Control**
> A printed staffing roster and a handwritten timesheet lying on a stainless
> steel prep table, a pencil resting across them, a neat stack of folded dark
> aprons at one edge of the frame. Nothing cooking, nobody present.

**`images/course/profit/module-2.webp` — Pricing That Actually Works**
> A printed catering quote on a worn wooden worktop, a basic desk calculator
> beside it, a pen laid down mid-annotation, a second sheet half-tucked
> underneath. The paperwork of pricing a job, not the job itself.

**`images/course/profit/module-3.webp` — Food Cost & Menu Engineering**
> A flat digital kitchen scale on a steel counter with a plain stainless bowl
> of prepped vegetables resting on it, a handwritten recipe card propped
> against the bowl. The act of weighing and costing, not a finished dish.

**`images/course/profit/module-4.webp` — Delivery & Logistics Systems**
> Stacked insulated catering carriers and an empty sheet-pan rack standing
> ready beside a roller door, a clipboard hanging on a hook. Loaded, labelled,
> waiting to go out. Daylight from the open door, no vehicle visible.

**`images/course/profit/module-5.webp` — Cash Flow Management**
> A small office desk, not a kitchen: a squared stack of printed invoices, a
> bank statement partly visible beneath, a cooling mug of coffee, a pen. The
> back-office side of a catering business, early morning light.

## The Catering People System

**`images/course/people/module-1.webp` — Lead Generation**
> A desk with an open notebook showing a handwritten list of names, a phone
> lying face-up and dark beside it, a small fan of plain business cards. The
> quiet work of finding and contacting buyers.

**`images/course/people/module-2.webp` — Marketing**
> A single printed one-page menu flyer on a plain table, a phone held just
> above it on a tripod arm photographing a simple plated dish from directly
> overhead. Making the marketing material, not the polished result.

**`images/course/people/module-3.webp` — Winning and Keeping Clients**
> Two used coffee cups and an open folder of papers across a café table by a
> window, two empty chairs pushed back. A client meeting that has just ended.
> Soft daylight, nobody in frame.

**`images/course/people/module-4.webp` — Hiring and Staffing**
> A table with a stack of printed applications and a scoring sheet on a
> clipboard, a pen across them, one empty chair pulled up square to the table.
> Plain room, interview about to begin.

**`images/course/people/module-5.webp` — Team and Culture**
> A row of clean pressed aprons hanging on wall hooks beside a blank wall-
> mounted whiteboard, a service station wiped down and set out ready. Before
> service, nobody there yet. Completely blank board — no writing.

---

## After generating

1. Save each at its exact path above.
2. `python3 tools/build_people_course.py` first if the People pages are being
   regenerated, then `python3 tools/wire_course_heroes.py` — that order,
   because the generator rewrites those pages wholesale.
3. `python3 tools/check_site.py` to confirm sizing and weight pass.

Replacing a file and re-running updates the stored dimensions; deleting one
removes the figure again.
