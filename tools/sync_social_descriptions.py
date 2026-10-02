#!/usr/bin/env python3
"""
Make og:description and twitter:description match the meta description.

The five original posts had their meta descriptions rewritten and their social
ones left behind, so the text Google shows and the text LinkedIn, Facebook and
X show were different — and the social one was still the original marketing
copy: "Discover how to...", "Gain executive-level operational expertise...",
"Your menu is your most powerful profit tool."

Sharing any of those five posted a preview written in a voice the page itself
no longer uses.

It also fixes a truncation. scaling-a-catering-business's twitter:description
ended mid-word:

    content="...leads to losses, not growth. Here"

The source sentence was "Here's how to scale...", and the apostrophe closed the
attribute early. Anyone sharing that post on X got a card that stops in the
middle of a sentence. Rebuilding the value from the meta description removes it,
and the escaping below keeps it from coming back.

Run from the repository root:

    python3 tools/sync_social_descriptions.py
"""

import glob
import html
import os
import re


def meta_value(page, key, attr="name"):
    """The content of a <meta> by name or property, whichever order it uses."""
    tag = re.search(rf'<meta[^>]*{re.escape(attr)}="{re.escape(key)}"[^>]*>', page)
    if not tag:
        return None, None
    value = re.search(r'content="([^"]*)"', tag.group(0))
    return (value.group(1) if value else None), tag.group(0)


def set_content(tag, value):
    """Replace a tag's content, escaping so quotes cannot close it early."""
    safe = html.escape(value, quote=True)
    return re.sub(r'content="[^"]*"', f'content="{safe}"', tag, count=1)


def main():
    changed = 0
    for path in sorted(glob.glob("blog/*.html") + glob.glob("*.html")):
        with open(path, encoding="utf-8") as fh:
            page = fh.read()

        description, _ = meta_value(page, "description")
        if not description:
            continue

        updated = page
        for key, attr in (("og:description", "property"),
                          ("twitter:description", "name")):
            current, tag = meta_value(updated, key, attr)
            if tag is None or current == description:
                continue
            updated = updated.replace(tag, set_content(tag, description), 1)

        if updated != page:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(updated)
            print(f"  {os.path.basename(path):<42} social descriptions synced")
            changed += 1

    print(f"\n{changed} page(s) updated")


if __name__ == "__main__":
    main()
