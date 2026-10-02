#!/usr/bin/env python3
"""
Stop a dropdown tap closing the whole mobile menu.

Twenty-nine pages close the menu when any link inside it is clicked:

    const navLinks = mainNav.querySelectorAll('a');
    navLinks.forEach(link => link.addEventListener('click', closeMenu));

That selector includes the three dropdown parents, which are links but are not
destinations on mobile — they expand a submenu. So tapping "Services" fired
both handlers: the dropdown one opened the submenu, and this one closed the
whole panel over the top of it. The submenu could not be reached at all.

index.html already had the right selector, `nav a:not(.nav-dropdown > a)`, which
is what this applies everywhere.

Worth recording how this was found, because an automated check had already
passed it. The test measured the nav's scrollHeight before and after the tap and
expected it to grow; it does grow, because the submenu really is inserted — and
then the panel hides, which does not change scrollHeight at all. The metric was
measuring the wrong thing. A screenshot of the same page showed an obviously
closed menu. The picture was right and the number was wrong.

Run from the repository root:

    python3 tools/fix_nav_close_selector.py
"""

import glob
import os

OLD = "const navLinks = mainNav.querySelectorAll('a');"
NEW = ("// Dropdown parents are excluded: on mobile they expand a submenu\n"
       "      // rather than navigate, so closing the menu on their click hid\n"
       "      // the submenu they had just opened.\n"
       "      const navLinks = mainNav.querySelectorAll('a:not(.nav-dropdown > a)');")


def main():
    changed = 0
    for path in sorted(glob.glob("*.html") + glob.glob("blog/*.html")
                       + glob.glob("course/*.html")):
        with open(path, encoding="utf-8") as fh:
            page = fh.read()
        if OLD not in page:
            continue
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(page.replace(OLD, NEW))
        print(f"  {os.path.basename(path):<44} close-on-click narrowed")
        changed += 1
    print(f"\n{changed} page(s) updated")


if __name__ == "__main__":
    main()
