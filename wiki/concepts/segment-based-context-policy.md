---
title: "Segment-based context policy"
type: concept
created: 2026-10-22
updated: 2026-10-22
tags: [context-management, policy]
sources: [actor-gatherer-framework-blog, actor-gatherer-docs, repo-ucbepic-actor-gatherer]
confidence: medium
---
A context-management policy that divides an interaction history into
*segments* (tasks): contiguous runs of user and agent turns that serve one
purpose. Context is append-only within a segment and is rebuilt (a "context
switch") only at segment boundaries. Introduced with [[actor-gatherer]] as
the Gatherer's policy.

## What the sources say
- Definition: "a segment is a contiguous group of user and agent interactions
  that serve a single purpose". The policy is append-only within a segment,
  since "the context needed within a segment" is expected to be similar, and
  performs context switches at boundaries that "both remove irrelevant
  information and bring in relevant information" ([[actor-gatherer-framework-blog]]).
- At a switch, an LLM reasons over the histories of all agents in the
  Gatherer database, "augmented by a temporal inductive bias that gives more
  weight to more recent observations". Information is included at varying
  granularity, with long-lived information early for KV-cache reuse
  ([[kv-cache-aware-context-ordering]]; [[actor-gatherer-framework-blog]]).
- The docs never use the word "segment". They describe "grouping events into
  turns and tasks, segmentation, summarization, the new-task check, ranking,
  rendering to a token budget" ([[actor-gatherer-docs]]).
- Implementation (`ProactiveContextManager`): LLM segmentation ("A TASK is a
  run of CONSECUTIVE turns that serve one high level objective"); a cheap
  boundary check biased toward "no new task"; per-task summaries of what the
  user established; LLM ranking of earlier tasks; a coarse-to-fine section
  layout. A build is adopted only at a user message or when over the limit,
  and only if smaller than what it replaces ([[repo-ucbepic-actor-gatherer]]).
- Recency in code is structural (newest-first filling, previous task in
  full) rather than an explicit weight. The LLM ranks task descriptions and
  summaries rather than raw trajectories ([[repo-ucbepic-actor-gatherer]]).

## Contradictions
- [[actor-gatherer-framework-blog]] describes the switch as an LLM reasoning over "the past history and
  trajectories of all the agents" with a temporal inductive bias.
  [[repo-ucbepic-actor-gatherer]] implements a narrower version: ranking over task summaries, other
  agents seen through their user requests and ranked tasks, and recency
  expressed only by layout. This is less a disagreement than a gap between
  the description and the shipped code.

## Related
- [[proactive-context-management]]
- [[context-compaction]] — the append-then-compact policy it replaces
- [[kv-cache-aware-context-ordering]]
