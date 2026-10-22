---
title: "Codex (OpenAI coding agent)"
type: entity
created: 2026-10-22
updated: 2026-10-22
tags: [harness, coding-agent]
sources: [actor-gatherer-framework-blog, actor-gatherer-docs, repo-ucbepic-actor-gatherer]
---
OpenAI's Codex coding-agent harness. In [[actor-gatherer-framework-blog]] it is the main baseline and the default Actor (AG-Codex).

## Facts
- Classed by the blog as a compaction harness: "Codex includes a summary of
  the history in context, which is lossy". In the coding task it
  "frequently loses the specification during compaction" ([[actor-gatherer-framework-blog]]).
- Vanilla Codex: 32% average accuracy in the single-agent tasks and 0% in the
  multi-agent tasks; Codex+Hint (told where other agents' traces are): 69%
  (agent model gemini-3.1-pro-preview) ([[actor-gatherer-framework-blog]]).
- AG-Codex on the coding task across harnesses: 71% accuracy, $1.26 per task,
  441 s ([[actor-gatherer-framework-blog]]).
- Integration: a local proxy via a `base_url` override (`-c`). The thread id
  is the channel, and Gatherer messages arrive as developer messages
  ([[actor-gatherer-docs]]). Codex's automatic compaction is switched off for the run, and
  `ag` keeps under 90% of the window ([[repo-ucbepic-actor-gatherer]]).

## Related
- [[actor-gatherer]] — runs as an Actor under it
- [[context-compaction]] — its default context policy
