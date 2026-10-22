---
title: "Pi (coding agent)"
type: entity
created: 2026-10-22
updated: 2026-10-22
tags: [harness, coding-agent]
sources: [actor-gatherer-framework-blog, actor-gatherer-docs, repo-ucbepic-actor-gatherer]
---
Pi, an open coding-agent harness, one of the four harnesses [[actor-gatherer]] integrates (AG-Pi).

## Facts
- AG-Pi on the coding task: 71% accuracy, $0.87 per task, 206 s. It was
  the fastest and cheapest, "because it performs less validation after it
  generates a first answer" ([[actor-gatherer-framework-blog]]).
- Integration: a hook (extension loaded with `-e`, gatherer passed as
  `--ag-gatherer NAME`). Gatherer messages arrive as a hidden custom message,
  and Pi's compaction is turned off unless `AG_PI_COMPACTION=allow`
  ([[actor-gatherer-docs]]). Implemented on Pi's `context` event in TypeScript ([[repo-ucbepic-actor-gatherer]]).

## Related
- [[actor-gatherer]] — runs as an Actor under it
- [[context-compaction]] — its default context policy
