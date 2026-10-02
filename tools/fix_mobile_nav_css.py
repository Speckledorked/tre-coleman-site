#!/usr/bin/env python3
"""
Stop page-local CSS breaking the mobile navigation.

style.css makes the dropdown `position: static` below 1024px, so an open
submenu pushes the rest of the menu down and everything stays reachable. Five
pages re-declare the whole nav in a page-local <style> block and only carry the
desktop rule, `position: absolute`. A page-local block loads after the
stylesheet, so it wins, and on those five an open submenu was drawn on top of
the nav items below it: opening Services covered Insights and Resources, which
could not then be tapped.

Measured on about.html at 390x844 before this fix: the nav's scrollHeight
equalled its clientHeight (844) with Services open, meaning the seven submenu
items added no height at all because they were overlaying rather than pushing.
index.html, which uses the shared stylesheet, reported 979 against 844.

The same shadowing broke something worse on playbook.html. style.css shows the
hamburger below 1024px with `display: flex`; that page's own CSS declares
`.mobile-menu-toggle{display:none}` and never overrides it for mobile, so the
button was `display: none` at 390px and **there was no way to open the menu at
all on a phone**. Measured, not inferred: the toggle reported a 0x0 box.

The fix appends a mobile override to each page's own style block rather than
adding !important to style.css, so it wins on source order alone and desktop is
untouched. Affected pages are found by inspection rather than listed, so a
further page growing either problem is covered automatically.

Run from the repository root:

    python3 tools/fix_mobile_dropdowns.py
"""

import glob
import os
import re

MARKER = "/* mobile dropdown override (tools/fix_mobile_dropdowns.py) */"

OVERRIDE = f"""
    {MARKER}
    @media screen and (max-width: 1024px) {{
      .mobile-menu-toggle {{
        display: flex;
        justify-content: center;
        align-items: center;
        min-width: 44px;
        min-height: 44px;
      }}
      /* Off-screen is not hidden: without this the closed panel keeps taking
         keyboard focus, and tabbing walks into links at x=468 in a 390px
         viewport. */
      nav, #mainNav {{
        visibility: hidden;
        transition: right 0.3s ease, visibility 0s linear 0.3s;
      }}
      nav.active, #mainNav.active {{
        visibility: visible;
        transition: right 0.3s ease, visibility 0s;
      }}
      .dropdown-menu {{
        position: static;
        opacity: 1;
        visibility: visible;
        transform: none;
        box-shadow: none;
        display: none;
      }}
      .nav-dropdown.active .dropdown-menu {{
        display: block;
      }}
    }}
"""


def needs_fix(page):
    """Page-local CSS breaks the mobile nav in either of the two known ways."""
    styles = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", page, re.S))
    mobile = re.findall(r"@media[^{]*max-width[^{]*\{(.*)", styles, re.S)

    # 1. Dropdown pinned absolute, so an open submenu overlays the nav below it.
    absolute = re.search(r"\.dropdown-menu\s*\{[^}]*position:\s*absolute", styles)
    if absolute and not any(
        re.search(r"\.dropdown-menu\s*\{[^}]*position:\s*static", m) for m in mobile
    ):
        return True

    # 2. Hamburger hidden, with nothing to bring it back below 1024px.
    hidden = re.search(r"\.mobile-menu-toggle\s*\{[^}]*display:\s*none", styles)
    if hidden and not any(
        re.search(r"\.mobile-menu-toggle\s*\{[^}]*display:\s*(flex|block|inline-flex)", m)
        for m in mobile
    ):
        return True

    # 3. The page redeclares the slide-out panel itself. Whatever else it gets
    #    right, a local `right: -100%` without `visibility: hidden` leaves the
    #    closed panel in the focus order, and a local `.mobile-menu-toggle`
    #    without a minimum size reverts the 44x44 target.
    if re.search(r"(?:nav|#mainNav)[^{}]*\{[^}]*right:\s*-100%", styles):
        return True

    return False


def main():
    changed = 0
    for path in sorted(glob.glob("*.html") + glob.glob("blog/*.html")
                       + glob.glob("course/*.html")):
        with open(path, encoding="utf-8") as fh:
            page = fh.read()

        if "mobileMenuToggle" not in page or MARKER in page:
            continue
        if not needs_fix(page):
            continue

        # Append to the LAST page-local style block, so it beats the rule above.
        last = None
        for m in re.finditer(r"</style>", page):
            last = m
        if last is None:
            print(f"  {path:<44} SKIPPED — no <style> block to extend")
            continue

        page = page[:last.start()] + OVERRIDE + page[last.start():]
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(page)
        print(f"  {os.path.basename(path):<44} mobile nav CSS fixed")
        changed += 1

    print(f"\n{changed} page(s) updated")


if __name__ == "__main__":
    main()
