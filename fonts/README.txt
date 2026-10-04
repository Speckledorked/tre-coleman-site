Self-hosted webfonts for ledger.css.

  archivo-var-latin.woff2   Archivo, variable: weight 400-800, width 62-125%
  inter-var-latin.woff2     Inter, variable: weight 400-700

Both are Latin-subset variable fonts retrieved from the Google Fonts CDN, and
both are licensed under the SIL Open Font License 1.1 — full text in
Archivo-OFL.txt and Inter-OFL.txt, which the licence requires be distributed
with the fonts.

  Archivo  Copyright 2020 The Archivo Project Authors
           https://github.com/Omnibus-Type/Archivo
  Inter    Copyright 2020 The Inter Project Authors
           https://github.com/rsms/inter

They are self-hosted rather than linked from fonts.googleapis.com for two
reasons: it removes a third-party origin from the critical path (two
preconnects, a CSS request, then the font fetches), and ledger.css needs the
width axis, which the Google CSS API only serves when explicitly requested.

Archivo's width axis is what produces the condensed display setting — see
font-stretch in ledger.css. Do not replace these with static instances
without checking every font-stretch declaration.
