---
title: "OpenCode"
type: entity
created: 2026-10-22
updated: 2026-10-22
tags: [harness, coding-agent]
sources: [actor-gatherer-framework-blog, actor-gatherer-docs, repo-ucbepic-actor-gatherer]
---
OpenCode, an open-source coding-agent harness, one of the four harnesses [[actor-gatherer]] integrates (AG-OpenCode).

## Facts
- AG-OpenCode on the coding task: 71% accuracy, $1.24 per task, 370 s
  ([[actor-gatherer-framework-blog]]).
- Integration: a hook (plugin added through `OPENCODE_CONFIG_CONTENT`).
  Gatherer messages arrive as a synthetic user message, and auto-compaction
  and tool-output pruning are turned off ([[actor-gatherer-docs]]). The plugin uses
  `experimental.chat.messages.transform` ([[repo-ucbepic-actor-gatherer]]).

## Related
- [[actor-gatherer]] — runs as an Actor under it
- [[context-compaction]] — its default context policy
