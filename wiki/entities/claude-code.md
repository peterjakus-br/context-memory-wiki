---
title: "Claude Code"
type: entity
created: 2026-10-22
updated: 2026-10-22
tags: [harness, coding-agent]
sources: [actor-gatherer-framework-blog, actor-gatherer-docs, repo-ucbepic-actor-gatherer]
---
Anthropic's Claude Code coding-agent harness, one of the four harnesses [[actor-gatherer]] can wrap (AG-ClaudeCode).

## Facts
- Placed by the blog among compaction harnesses with low longitudinal and
  no lateral awareness ([[actor-gatherer-framework-blog]]).
- AG-ClaudeCode on the coding task: 71% accuracy, $1.23 per task, 333 s
  ([[actor-gatherer-framework-blog]]).
- Integration: a local proxy, with `ANTHROPIC_BASE_URL` pointing at
  `/h/<gatherer>/`. The session is the channel, and Gatherer messages arrive
  as system messages or user-turn reminders ([[actor-gatherer-docs]]). Claude Code's own
  compaction stays on, and `ag` keeps the context under its auto-compact
  limit. Subagent calls are not managed. `cache_control` markers are
  re-placed ([[repo-ucbepic-actor-gatherer]]).
- It can also serve as the Gatherer's own LLM (`claude-code/sonnet`), on
  the user's subscription ([[actor-gatherer-docs]]).

## Related
- [[actor-gatherer]] — runs as an Actor under it
- [[context-compaction]] — its default context policy
