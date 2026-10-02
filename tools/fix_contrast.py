#!/usr/bin/env python3
"""
Raise every colour pairing axe measured below WCAG AA to a passing one.

style.css has carried --accent-gold-text (#A85F28, 4.85:1 on white) since the
first accessibility pass, because the brand gold #F4A460 is 2.03:1 and fails AA
by more than a factor of two in both directions. What that pass did not reach
was colour declared *on the page*: inline styles, page-local <style> blocks, and
a handful of pages that re-declare the whole nav and so shadow the stylesheet
entirely.

Those pages were invisible to CI, because .lighthouserc.json sampled seven
pages and none of them was affected. Expanding the sample to about.html,
catering-profit.html and virginia-neighbors.html is what produced the numbers
below — every one of them is axe's own measurement of the rendered page, not an
estimate:

    catering-profit    #F4A460 h3 on #fff9e6             1.93:1  ->  4.60:1
    catering-profit    #27ae60 h3 on #f8f9fa             2.73:1  ->  5.09:1
    virginia-neighbors white .nav-cta on gold            2.03:1  ->  4.85:1
    virginia-neighbors #e53e3e status text on #fafaf8    3.95:1  ->  5.23:1

Only pairings are rewritten. A gold border, rule, bullet marker or focus
outline carries no text, contrast minimums do not apply to it, and the brand
colour should stay wherever it can.

Run from the repository root:

    python3 tools/fix_contrast.py
"""

import glob
import re

GOLD = r"(?:#F4A460|var\(--accent-gold\))"
GOLD_TEXT = "var(--accent-gold-text)"
WHITE = r"(?:white|#fff(?:fff)?|var\(--white\))"

# The gold gradient and its darkened equivalent. #A85F28 is 4.85:1 against
# white and #94501F is 5.84:1, so white text passes across the whole sweep.
GOLD_GRADIENT = "#F4A460 0%, #e09450 100%"
GOLD_GRADIENT_TEXT = "#A85F28 0%, #94501F 100%"

# Hover shades. These sit in :hover rules that set only the background and
# inherit white text from the base rule, so the pairing regexes cannot see
# them, and axe never tests a hover state at all — a button can pass at rest
# and fail the moment a pointer touches it. After the gradient rewrite above,
# every remaining occurrence of these two values is a hover background under
# white text, so replacing them outright is exact.
HOVER = {
    "#c89456": "#8F4F21",   # white on it: 2.68:1 -> 6.35:1
    "#e09450": "#94501F",   # white on it: 2.46:1 -> 6.13:1
}

# background:<gold> … color:<white>, in either order, inside one declaration
# block or one inline style attribute. The body between the two must not
# contain a brace, so a match cannot straddle two rules.
PAIRED = re.compile(
    r"(background(?:-color)?\s*:\s*)" + GOLD
    # (?![\w-]) rather than \b: \b after var(--white) can never match, because
    # ")" and the space after it are both non-word characters. That cost a round
    # — virginia-neighbors.html's .nav-cta writes `color: var(--white)` and was
    # silently skipped while the same rule written `color: white` was fixed.
    + r"(\s*(?:!important)?\s*;[^{}]*?color\s*:\s*" + WHITE + r"(?![\w-]))",
    re.I,
)
PAIRED_REVERSED = re.compile(
    r"(color\s*:\s*" + WHITE + r"\s*(?:!important)?\s*;[^{}]*?"
    r"background(?:-color)?\s*:\s*)" + GOLD,
    re.I,
)

# Colour used as text only fails on a light background, and whether the
# background is light comes from an ancestor rather than the declaration, so a
# regex cannot decide it. These four were measured by axe and are listed
# individually. Each entry is (path, exact text to replace, replacement).
#
# Deliberately NOT changed, because axe measured them as passing:
#   #mainNav a:hover, .footer-section a:hover   gold on navy
#   .dashboard-footer a                         gold on #2c3e50
#   .module-deliverables li:before              a ">" list marker: glyph text,
#       but it carries nothing a sighted user needs and no screen reader
#       announces it, so it stays gold under the decorative exemption
MEASURED = [
    # "Week 1" labels, informational text on course/bonus.html's #f8f9fa body
    ("course/bonus.html",
     ".timeline .week { font-weight: 700; color: #F4A460;",
     ".timeline .week { font-weight: 700; color: #A85F28;"),
    # BONUS heading, gold on the #fff9e6 callout
    ("catering-profit.html",
     '<h3 style="color: #F4A460;">',
     '<h3 style="color: #A85F28;">'),
    # "Who this fits" heading, green on #f8f9fa. 2.73:1 fails even the 3:1
    # large-text threshold it qualifies for at 21.6px bold.
    ("catering-profit.html",
     '<h3 style="color: #27ae60; margin-bottom: 1rem;">',
     '<h3 style="color: #1B7A43; margin-bottom: 1rem;">'),
    # Directory loading/error status text, red on #fafaf8
    ("virginia-neighbors.html",
     '<p style="color:#e53e3e;">',
     '<p style="color:#c53030;">'),
]


def convert(path, text):
    text, a = PAIRED.subn(r"\1" + GOLD_TEXT + r"\2", text)
    text, b = PAIRED_REVERSED.subn(r"\1" + GOLD_TEXT, text)

    # A gold gradient under white text, for the same reason as a flat fill.
    # On course/dashboard.html the gradient and the white text are in separate
    # rules — .bonus-card .module-header sets only the background and inherits
    # colour from .module-header — so the pairing regexes cannot see it.
    c = text.count(GOLD_GRADIENT)
    if c:
        text = text.replace(GOLD_GRADIENT, GOLD_GRADIENT_TEXT)

    e = 0
    for old, new in HOVER.items():
        if old in text:
            e += text.count(old)
            text = text.replace(old, new)

    d = 0
    for listed_path, old, new in MEASURED:
        if path == listed_path and old in text:
            d += text.count(old)
            text = text.replace(old, new)

    return text, a + b + c + d + e


def main():
    total = 0
    for path in sorted(glob.glob("**/*.html", recursive=True)):
        if "node_modules" in path:
            continue
        with open(path, encoding="utf-8") as fh:
            original = fh.read()
        converted, num = convert(path, original)
        if num:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(converted)
            print(f"  {path:<44} {num}")
            total += num
    print(f"\n{total} failing pairing(s) raised above WCAG AA")


if __name__ == "__main__":
    main()
