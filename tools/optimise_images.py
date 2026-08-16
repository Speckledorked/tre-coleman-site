#!/usr/bin/env python3
"""
Convert the site's oversized PNG/JPG assets to right-sized WebP.

The originals are 1.4-2.3 MB each and several are displayed at 280px while
being downloaded at 1024px wide. Each image is resized to roughly 2x its
largest CSS display width (capped at its intrinsic size, so nothing is
upscaled) and re-encoded as WebP.

Outputs land in images/ under descriptive, lowercase-hyphenated filenames.
The originals are left on disk untouched — once you have eyeballed the new
versions on the site, they can be deleted (git history retains them).

Run from the repository root:

    python3 tools/optimise_images.py
"""

import os
from PIL import Image

QUALITY = 82

# source, destination, target width, note on where it is displayed
IMAGES = [
    ("hero.png",
     "images/hero-restaurant-operations.webp", 1536,
     "index.html hero background (LCP element)"),
    ("fixed systems.png",
     "images/restaurant-systems-before-after.webp", 1024,
     "services.html, displayed at max 700px"),
    ("ChatGPT Image Feb 3, 2026, 08_52_24 PM.png",
     "images/ai-integration-restaurants.webp", 560,
     "services.html service card, displayed at max 280px"),
    ("Reviewing KPIs in a modern office.png",
     "images/sops-training-systems.webp", 560,
     "services.html service card, displayed at max 280px"),
    ("ChatGPT Image Feb 3, 2026, 08_53_59 PM.png",
     "images/local-store-marketing.webp", 560,
     "services.html service card, displayed at max 280px"),
    ("Reviewing restaurant menus and notes.png",
     "images/menu-engineering-analysis.webp", 560,
     "services.html service card, displayed at max 280px"),
    ("ChatGPT Image Feb 3, 2026, 08_55_43 PM.png",
     "images/advisory-fractional-operations.webp", 560,
     "services.html service card, displayed at max 280px"),
    ("familypic.jpg",
     "images/tre-coleman-family.webp", 400,
     "about.html hero, displayed as a 200px circle"),
    ("newsletterlogo.png",
     "images/from-the-floor-up-newsletter.webp", 600,
     "playbook.html footer, displayed at max 300px"),
    ("facebookbackground.png",
     "images/restaurant-operations-management.webp", 1200,
     "profit-leak-snapshot.html, 800px container"),
    ("calm ops.png",
     "images/calm-operations-are-built.webp", 1200,
     "advisory.html, displayed at max 600px"),
    ("catering add.png",
     "images/adding-catering-to-restaurant.webp", 1024,
     "catering-profit.html, 800px container"),
]


def convert(src, dst, target_width):
    img = Image.open(src)
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        # WebP handles alpha, but these are all photographic — flatten onto
        # white so we get the smaller lossy encode rather than lossless.
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
        img = bg
    else:
        img = img.convert("RGB")

    if img.width > target_width:
        height = round(img.height * target_width / img.width)
        img = img.resize((target_width, height), Image.LANCZOS)

    os.makedirs(os.path.dirname(dst), exist_ok=True)
    img.save(dst, "WEBP", quality=QUALITY, method=6)
    return img.size


def main():
    before_total = after_total = 0
    print(f"{'source':<46} {'->':<2} {'result':<46} {'before':>9} {'after':>8}  saving")
    print("-" * 130)
    for src, dst, width, _note in IMAGES:
        if not os.path.exists(src):
            print(f"MISSING  {src}")
            continue
        before = os.path.getsize(src)
        size = convert(src, dst, width)
        after = os.path.getsize(dst)
        before_total += before
        after_total += after
        pct = 100 * (1 - after / before)
        print(f"{src[:45]:<46} -> {os.path.basename(dst)[:45]:<46} "
              f"{before/1024:8.0f}K {after/1024:7.0f}K  -{pct:4.1f}%  ({size[0]}x{size[1]})")

    print("-" * 130)
    pct = 100 * (1 - after_total / before_total)
    print(f"{'TOTAL':<46} {'':<2} {'':<46} {before_total/1024/1024:7.2f}M "
          f"{after_total/1024:7.0f}K  -{pct:.1f}%")


if __name__ == "__main__":
    main()
