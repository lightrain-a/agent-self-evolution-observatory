# Manuscript-backed experimental reader index

Page: `rsi/experimental-atlas.html`.

The page has five views: dataset-to-paper relations, the 60-entry paper register,
64 measurement families, 18 control patterns, and 38 original resource families.
The six question filters are independent of the task-setting categories.

## Source contract

`rsi/experiment-catalog.json` is a snapshot exported by
`RSI_review2610/scripts/export_experimental_reader.py`. Its `source_commit`
identifies the exact manuscript revision. The manuscript's
`tables/reader-resources.tex` is the canonical dataset-use relation table.
Do not manually infer new relations from the broad resource-family register.
`application`, `introduction`, and `protocol` are different relation types.

To refresh, check out the authorized manuscript at a verified commit and run:

```bash
python3 /path/to/RSI_review2610/scripts/export_experimental_reader.py > rsi/experiment-catalog.json
python3 scripts/build_rsi_research.py
python3 scripts/build_rsi_site.py
python3 scripts/test_experimental_atlas.py
python3 scripts/test_rsi_site.py
```

Update fixed audit counts intentionally when adding/removing indexed relations.
This is an explicit build operation, not a background watcher.

## Navigation and runtime

The page is registered in `build_rsi_research.py` under the Evidence group.
Its page-local script is on the `page-router.js` initialization allowlist.
The DOM is server-rendered; no external API is required for search/filtering.
Search terms, question, category, and view are stored in URL query parameters.
Reverse links move between dataset and paper cards without fetching a new page.
CSS is scoped to this page. Formula source is retained in expandable LaTeX
rather than being silently treated as faithfully rendered mathematics.

## Verification for initial reader release

Manuscript source: `86ef276f167524c3dae39096cf4471da1ef31ccb`.
Website base: `64f87c0f7e18e7b937961ee0cd68a024cf87bf85`.

- 54 resource/family entries; 71 typed source relations, including 59 reported uses.
- All 180 prior register entries retained (60 papers, 38 families, 64 measures, 18 controls).
- Full static build and standalone RSI export passed.
- RSI audit passed: 43 pages; existing local links, anchors, menus and public export checked.
- Source/HTML audit passed: unique IDs, relation types, source commit, card counts and reverse links.
- Browser test passed using installed Chromium: resource and question filters, Chinese keyword aliases,
  empty results, all five views, dataset/paper reverse lookup, soft-navigation and browser back.
- Desktop 1440x1100 and mobile 390x844 tested; no horizontal mobile overflow or uncaught browser exceptions.
- Existing curated-figure and problem-atlas frontend tests passed.

Optional local browser check (requires an installed Chromium and the `ws` Node module):
`node scripts/test_experimental_atlas_browser.js`.
The test binds services only to loopback and terminates its browser/server afterward.
No model experiment or benchmark reproduction is claimed. Deployment is separately
verified on the public URL; passing a local build alone is not a live-release receipt.
