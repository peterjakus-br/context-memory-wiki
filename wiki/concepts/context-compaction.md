---
title: "Context compaction"
type: concept
created: 2026-10-22
updated: 2026-10-22
tags: [context-management, policy]
sources: [actor-gatherer-framework-blog, actor-gatherer-docs, repo-ucbepic-actor-gatherer]
confidence: medium
---
Context compaction is the default context policy of coding harnesses: append
every action and observation to the context, and when it nears the window
limit, replace older parts with a summary. Memory add-ons can append
retrieved summaries.

## What the sources say
- In typical harnesses (Codex, Claude Code), agents "passively rely on lossy
  summaries of past interactions", while recent detailed trajectories can be
  redundant after a task switch and "incur unnecessary cost". There is no
  lateral information ([[actor-gatherer-framework-blog]]).
- Codex "frequently loses the specification during compaction"; vanilla
  Codex scores 32% average single-agent accuracy on the authors' tasks
  ([[actor-gatherer-framework-blog]]).
- [[actor-gatherer]] turns the harness's own compaction off in Pi and
  OpenCode ([[actor-gatherer-docs]]) and also in Codex ([[repo-ucbepic-actor-gatherer]]). In Claude Code compaction
  stays on and `ag` keeps under its auto-compact limit ([[repo-ucbepic-actor-gatherer]]).

## Related
- [[mem0]] — memory that complements compaction
- [[retrieval-augmented-memory]] — retrieval over raw history as the alternative to lossy summaries
- [[memory-mutation]] — rewriting stored memory, the write-side analogue
- [[segment-based-context-policy]] — the alternative proposed
- [[codex]], [[claude-code]], [[pi-coding-agent]], [[opencode]]
