---
title: "KV-cache-aware context ordering"
type: concept
created: 2026-10-22
updated: 2026-10-22
tags: [context-management, cost, latency]
sources: [actor-gatherer-framework-blog, repo-ucbepic-actor-gatherer]
confidence: low
---
KV-cache-aware context ordering arranges the context so that the parts least
likely to change come first and volatile parts last. Changes to context then
keep the longest possible reusable prefix in the provider's KV/prompt cache,
which cuts cost and latency. Context edits are made only when they are worth
the cache invalidation.

## What the sources say
- "changing the model context can invalidate the KV-cache, which can increase
  cost and latency, and is thus only worth doing when modifying the context is
  expected to improve accuracy" ([[actor-gatherer-framework-blog]]).
- "Information expected to remain relevant for more tasks is placed earlier in
  the context to maximize KV-cache reuse, while information expected to change
  more frequently is placed towards the end" ([[actor-gatherer-framework-blog]]).
- In code this is only partly realised: sections are reused unchanged between
  context switches, so the prefix is stable within a segment. Claude Code's
  `cache_control` markers are re-placed. There is no volatility-based
  placement logic, and "KV cache" does not occur in the package code
  ([[repo-ucbepic-actor-gatherer]]).

## Related
- [[segment-based-context-policy]] — append-only within segments partly for
  this reason
