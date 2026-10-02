#!/usr/bin/env python3
"""
Extract CSS blocks that are byte-identical across multiple pages into
style.css.

Inline <style> is not cacheable across pages, so a returning visitor
re-downloads the same rules on every page. Roughly 68 KB is duplicated this
way. It is also a maintenance hazard: identical blocks on 11 pages drift
apart the moment anyone edits one.

SAFETY — the two things that could break this:

1. Cascade order. The inline blocks sit AFTER the style.css <link>, so on a
   specificity tie the inline rule wins. Extracted rules are appended to the
   END of style.css, preserving their position relative to the base rules.
   Any page-specific inline block that stays behind still comes after them,
   exactly as before.

2. Pages that do not load style.css. course/*.html carry their own identical
   block but have no <link> to style.css, so extracting theirs would strip
   their styling entirely. Those are excluded by the links_css check.

3. Selector collisions between blocks. This is what makes a wholesale
   extraction unsafe here, and a first attempt at one was reverted because of
   it. Moving a block into style.css gives EVERY page that loads style.css
   those rules — including pages that never had them inline. Where two blocks
   define the same selector differently (.cta-section is styled one way in the
   blog block and another in the service block), the one appended later wins
   everywhere, and pages silently render with another page type's styling.

   So only blocks that share NO selector with any other candidate block are
   extracted. Everything else stays inline, where its scoping is what keeps it
   correct.

Only blocks appearing on 2+ pages, where EVERY carrier links style.css, and
which collide with nothing, are touched. Page-specific CSS is left alone.

Run from the repository root:

    python3 tools/extract_shared_css.py
"""

import glob
import hashlib
import re
import collections

MIN_PAGES = 2
MIN_BYTES = 100

NAMES = {
    "b435f0a189": "Dropdown navigation (was inline on 11 pages)",
    "125b57cb9e": "Blog article layout (was inline on 11 pages)",
    "1a792d5a89": "Service page layout (was inline on 6 pages)",
    "76d398197b": "Auth form layout (was inline on 2 pages)",
    "afa3e07176": "Auth form layout, variant (was inline on 2 pages)",
}


def norm(body):
    return re.sub(r"\s+", " ", body).strip()


def collect():
    blocks = collections.defaultdict(list)
    for path in sorted(glob.glob("**/*.html", recursive=True)):
        if "node_modules" in path:
            continue
        s = open(path, encoding="utf-8", errors="replace").read()
        links_css = bool(re.search(r'href="(\.\./)?style\.css"', s))
        for m in re.finditer(r"<style>(.*?)</style>", s, re.S):
            body = m.group(1)
            if len(norm(body)) < MIN_BYTES:
                continue
            key = hashlib.md5(norm(body).encode()).hexdigest()[:10]
            blocks[key].append((path, body, links_css))
    return blocks


def selectors(css):
    """Rough selector list, for collision reporting only."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    return {
        s.strip()
        for chunk in re.findall(r"([^{}]+)\{", css)
        for s in chunk.split(",")
        if s.strip() and not s.strip().startswith("@")
    }


def main():
    blocks = collect()

    extract = {}
    for key, entries in blocks.items():
        if len(entries) < MIN_PAGES:
            continue
        if not all(c for _, _, c in entries):
            print(f"  SKIP {key}: {len(entries)} pages, but not all link "
                  f"style.css ({entries[0][0]})")
            continue
        extract[key] = entries

    if not extract:
        print("Nothing to extract.")
        return

    # Collision check. A block sharing any selector with another candidate
    # cannot be safely hoisted: in style.css it would apply to every page, and
    # whichever copy lands later would win globally rather than per page type.
    owners = {}
    for key, entries in extract.items():
        for sel in selectors(entries[0][1]):
            owners.setdefault(sel, set()).add(key)

    colliding = {k for sels in owners.values() if len(sels) > 1 for k in sels}
    for key in sorted(colliding):
        shared = sorted(s for s, ks in owners.items() if key in ks and len(ks) > 1)
        print(f"  SKIP {key}: shares {len(shared)} selector(s) with another "
              f"block (e.g. {shared[0]}) — must stay inline to keep its scope")
        del extract[key]

    if not extract:
        print("\nNo collision-free blocks to extract.")
        return

    # Append to style.css, in a stable order.
    additions = ["\n\n/* " + "=" * 74 + "\n   Extracted shared styles\n"
                 "   These were duplicated inline across multiple pages. Kept at the end\n"
                 "   of this file so their position relative to the base rules above is\n"
                 "   unchanged from when they were inline.\n"
                 "   Generated by tools/extract_shared_css.py\n   " + "=" * 74 + " */\n"]

    for key in sorted(extract, key=lambda k: -len(extract[k])):
        entries = extract[key]
        label = NAMES.get(key, f"Shared block {key} ({len(entries)} pages)")
        additions.append(f"\n/* ---- {label} ---- */\n{entries[0][1].strip()}\n")

    css = open("style.css", encoding="utf-8").read()
    if "Extracted shared styles" in css:
        print("style.css already contains extracted block — aborting to avoid "
              "duplicating it.")
        return
    open("style.css", "w", encoding="utf-8").write(css + "".join(additions))

    # Remove the now-redundant inline blocks.
    removed_bytes = 0
    touched = collections.Counter()
    for key, entries in extract.items():
        for path, body, _ in entries:
            s = open(path, encoding="utf-8").read()
            target = f"<style>{body}</style>"
            if target not in s:
                print(f"  WARN exact block not found in {path}; left in place")
                continue
            s = s.replace(target, "", 1)
            open(path, "w", encoding="utf-8").write(s)
            removed_bytes += len(target)
            touched[path] += 1

    print(f"\nExtracted {len(extract)} shared block(s) into style.css")
    print(f"Removed {removed_bytes // 1024} KB of inline CSS from "
          f"{len(touched)} page(s)")


if __name__ == "__main__":
    main()
