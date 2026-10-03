# Working agreement

Conventions for anyone — human or agent — making changes here. The technical
contract for the generators, the checks and the CI gates lives in
`tools/README.md`; this file is only about how work is delivered.

## Batch related work into one pull request

Open one PR per *piece of work*, not per commit or per idea.

The reason is cost, not tidiness. Every PR triggers GitHub's
`Code scanning AI findings` check, which spends one Copilot **premium
request** from the account's monthly allowance (Free 50, Pro 300,
Pro+ 1,500). On 2026-10-03 that allowance ran out mid-session: PRs #89
through #100 produced about twenty scan runs in two days, and every PR
afterwards failed with `402 / errorCode: quota` before the scanner read a
line of the diff. Three of those PRs could have been one.

So: accumulate related changes on the working branch, then open a single PR.
Split only when the changes are genuinely independent, or when one of them
needs to ship on its own.

A corollary — a red `Code scanning AI findings` check whose log shows
`errorCode: 'quota'` is a spent allowance, not a finding about the code. It
reports nothing because it never ran. Do not chase it as a code problem.

## Merge when CI is green

Drive a PR to green and merge it. `check`, `Lighthouse` and `Link check` are
the substantive gates. If one fails, diagnose and push a fix rather than
re-running blindly — and never skip or disable a check to get green.

## Develop on the working branch

Changes go on `claude/consulting-site-seo-audit-kekwtz`, never straight to
`main`.

## Regenerate the sitemap AFTER committing content

`tools/build_sitemap.py` reads each page's `lastmod` from
`git log -1 --format=%cs -- <file>`, so a page's date is only correct once the
change to it is committed. The order is: commit the content, run the
generator, commit the sitemap. Doing it the other way round stamps the page
with its previous date and CI fails on the diff.

## A new root-level `.md` is public unless you say otherwise

`publish = "."` serves the whole repository, so a working document added at
the root is a live URL. Each one needs a 404 rule in `netlify.toml`;
`tools/check_site.py` fails if one is missing. Files under `tools/` and
`drafts/` are already covered by their directory rules.
