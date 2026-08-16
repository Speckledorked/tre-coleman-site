#!/usr/bin/env python3
"""
Generate the sitewide Open Graph / Twitter card image at 1200x630.

The site previously pointed og:image at images/tre-headshot.jpg, which is
200x200 — below the minimum for the `summary_large_image` card the pages
declare, so every share on LinkedIn, Facebook, X and Slack rendered degraded.

Run from the repository root:

    python3 tools/build_og_image.py

Fonts: Outfit (headings) and Work Sans (body), both SIL Open Font License —
chosen because they are the closest available match to the site's Montserrat
and Open Sans.
"""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
NAVY = (31, 71, 136)
NAVY_DARK = (21, 43, 69)
GOLD = (244, 164, 96)
WHITE = (255, 255, 255)

FONT_DIR = "/mnt/skills/examples/canvas-design/canvas-fonts"
HEAD = os.path.join(FONT_DIR, "Outfit-Bold.ttf")
BODY = os.path.join(FONT_DIR, "WorkSans-Regular.ttf")
BODY_BOLD = os.path.join(FONT_DIR, "WorkSans-Bold.ttf")

BACKDROP = "images/hero-restaurant-operations.webp"
HEADSHOT = "images/tre-headshot.jpg"
OUT = "images/og-card.jpg"

KICKER = "RESTAURANTS  ·  FOOD TRUCKS  ·  CATERING"
HEADLINE = ["Restaurant Operations", "Consulting"]
SUBLINE = "Find and fix the profit leaks in labor, menu, and systems."
NAME = "Tre Coleman"
SITE = "trecoleman.com"


def backdrop():
    """Hero photo, cropped to 1200x630 and heavily darkened for text contrast."""
    if not os.path.exists(BACKDROP):
        return Image.new("RGB", (W, H), NAVY)

    img = Image.open(BACKDROP).convert("RGB")
    scale = max(W / img.width, H / img.height)
    img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    left = (img.width - W) // 2
    top = (img.height - H) // 2
    img = img.crop((left, top, left + W, top + H))

    # Navy wash at 86% so white text clears WCAG AA comfortably.
    wash = Image.new("RGB", (W, H), NAVY_DARK)
    return Image.blend(img, wash, 0.86)


def circular(path, size):
    img = Image.open(path).convert("RGB")
    side = min(img.size)
    img = img.crop((
        (img.width - side) // 2, (img.height - side) // 2,
        (img.width - side) // 2 + side, (img.height - side) // 2 + side,
    )).resize((size, size), Image.LANCZOS)

    mask = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size * 4, size * 4), fill=255)
    img.putalpha(mask.resize((size, size), Image.LANCZOS))
    return img


def main():
    card = backdrop()
    draw = ImageDraw.Draw(card)

    f_kicker = ImageFont.truetype(BODY_BOLD, 22)
    f_head = ImageFont.truetype(HEAD, 68)
    f_sub = ImageFont.truetype(BODY, 27)
    f_name = ImageFont.truetype(BODY_BOLD, 26)
    f_site = ImageFont.truetype(BODY, 24)

    x, y = 80, 132

    draw.text((x, y), KICKER, font=f_kicker, fill=GOLD)
    y += 52

    draw.rectangle((x, y, x + 74, y + 5), fill=GOLD)
    y += 38

    for line in HEADLINE:
        draw.text((x, y), line, font=f_head, fill=WHITE)
        y += 80

    y += 14
    draw.text((x, y), SUBLINE, font=f_sub, fill=(226, 232, 240))

    # Byline pinned to the bottom-left.
    by = H - 96
    if os.path.exists(HEADSHOT):
        shot = circular(HEADSHOT, 64)
        ring = Image.new("RGBA", (72, 72), (0, 0, 0, 0))
        ImageDraw.Draw(ring).ellipse((0, 0, 71, 71), fill=GOLD + (255,))
        card.paste(ring, (x - 4, by - 4), ring)
        card.paste(shot, (x, by), shot)

    draw.text((x + 84, by + 8), NAME, font=f_name, fill=WHITE)
    draw.text((x + 84, by + 38), SITE, font=f_site, fill=GOLD)

    card.save(OUT, "JPEG", quality=88, optimize=True, progressive=True)
    print(f"Wrote {OUT}  {card.size[0]}x{card.size[1]}  "
          f"{os.path.getsize(OUT)/1024:.0f} KB")


if __name__ == "__main__":
    main()
