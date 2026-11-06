#!/usr/bin/env python3
"""Put the module hero photograph on a module page -- when the file exists.

One image per module, five per course. Tre supplies them; until a file lands
the hero stays typographic, which is why presence is checked rather than
assumed. A slot that renders an <img> for a file that is not on disk is a
broken frame on a paid page, and an <img> with no width/height is a
Lighthouse `unsized-images` error outright.

Both courses, one code path. The People pages are generated and the Profit
pages are hand-maintained, so heroes could easily have ended up handled twice
and differently; this owns them for both.

RE-RUNNABLE and self-correcting:
  file added    -> the figure is inserted
  file replaced -> width/height are re-read and updated
  file removed  -> the figure is removed again

Dimensions come from the file header, never from a number typed somewhere: a
wrong width is a layout shift that Lighthouse scores and review does not
catch.

ORDER: run this AFTER tools/build_people_course.py. That generator rewrites
the People pages wholesale and would discard the figures.

    images/course/profit/module-1.webp  ->  course/module-1.html
    images/course/people/module-1.webp  ->  course/people/module-1.html
"""

import glob
import io
import os
import re
import sys

COURSES = [
    # (image dir, page glob, depth of the page below the repo root)
    ("profit", "course/module-{n}.html", ".."),
    ("people", "course/people/module-{n}.html", "../.."),
]
EXTS = ("webp", "jpg", "jpeg", "png")

FIGURE = re.compile(
    r'[ \t]*<figure class="module-hero__figure">\n.*?</figure>\n',
    re.S)
# The figure goes at the top of the main column, above the lesson index.
ANCHOR = re.compile(r'(<main\b[^>]*\bid="main-content"[^>]*>\n)')


def image_size(path):
    """Width and height read from the file's own header.

    WebP, PNG and JPEG. Verified against ImageMagick's `identify` on every
    image in this repository rather than trusted from the specification.
    """
    with open(path, "rb") as fh:
        head = fh.read(32)
        if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
            chunk = head[12:16]
            if chunk == b"VP8X":
                return (int.from_bytes(head[24:27], "little") + 1,
                        int.from_bytes(head[27:30], "little") + 1)
            if chunk == b"VP8 ":
                return (int.from_bytes(head[26:28], "little") & 0x3FFF,
                        int.from_bytes(head[28:30], "little") & 0x3FFF)
            if chunk == b"VP8L":
                bits = int.from_bytes(head[21:25], "little")
                return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
            return None
        if head[:8] == b"\x89PNG\r\n\x1a\n":
            return (int.from_bytes(head[16:20], "big"),
                    int.from_bytes(head[20:24], "big"))
        if head[:2] == b"\xff\xd8":
            fh.seek(2)
            while True:
                marker = fh.read(2)
                if len(marker) < 2 or marker[0] != 0xFF:
                    return None
                if 0xC0 <= marker[1] <= 0xCF and marker[1] not in (0xC4, 0xC8, 0xCC):
                    fh.read(3)                      # segment length + precision
                    h = int.from_bytes(fh.read(2), "big")
                    w = int.from_bytes(fh.read(2), "big")
                    return w, h
                size = int.from_bytes(fh.read(2), "big")
                fh.seek(size - 2, 1)
    return None


def find_image(course, n):
    for ext in EXTS:
        path = f"images/course/{course}/module-{n}.{ext}"
        if os.path.exists(path):
            return path
    return None


def figure_for(path, prefix, title):
    dims = image_size(path)
    if not dims:
        return None
    w, h = dims
    # alt="" on purpose: the hero repeats the module title set in <h1> beside
    # it, so describing it again is noise in a screen reader. It is
    # decoration, and saying so is the accessible choice.
    return (f'        <figure class="module-hero__figure">\n'
            f'          <img src="{prefix}/{path}" width="{w}" height="{h}" '
            f'alt="" loading="lazy" decoding="async">\n'
            f'        </figure>\n')


def wire(page, course, n, prefix):
    if not os.path.exists(page):
        return None, 'page missing'
    s = io.open(page, encoding='utf-8').read()
    before = s
    s = FIGURE.sub('', s)                     # start from no figure, then add

    path = find_image(course, n)
    if path:
        fig = figure_for(path, prefix, f'Module {n}')
        if fig is None:
            return None, f'unreadable image: {path}'
        m = ANCHOR.search(s)
        if not m:
            return None, 'no main-content anchor'
        s = s[:m.end()] + fig + s[m.end():]

    if s == before:
        return False, 'no image' if not path else 'unchanged'
    io.open(page, 'w', encoding='utf-8').write(s)
    return True, f'hero from {path}' if path else 'hero removed'


def main():
    changed = 0
    errors = []
    for course, pattern, prefix in COURSES:
        for n in range(1, 6):
            page = pattern.format(n=n)
            ok, why = wire(page, course, n, prefix)
            if ok is None:
                errors.append(f'{page}: {why}')
            elif ok:
                print(f'  {page}: {why}')
                changed += 1
    print(f'{changed} page(s) updated')
    if errors:
        print('ERRORS:', *errors, sep='\n  ')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
