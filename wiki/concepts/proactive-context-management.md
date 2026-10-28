---
title: "Proactive context management"
type: concept
created: 2026-10-22
updated: 2026-10-28
tags: [context-management, architecture]
sources: [actor-gatherer-framework-blog, actor-gatherer-docs, repo-ucbepic-actor-gatherer, raw-rag-naive-rag-agentic-memory]
confidence: medium
---
Proactive context management means that a component other than the acting
agent decides, before each model call, what the agent's context should
contain: based on the task, the agent's actions, other agents and the
environment, without waiting for the agent to ask. It contrasts with passive
[[context-compaction]] and with agent-driven
[[tool-based-context-management]]. The term and the framing come from one
group of authors so far.

## What the sources say
- "Our key insight is that context should be proactively constructed for a
  given task". The Gatherer is "in charge of storing all relevant information
  and providing the context for agents that solve the task" ([[actor-gatherer-framework-blog]]).
- The design decouples "reasoning and acting from context management";
  context can be added or removed "at any point during Actor reasoning"
  ([[actor-gatherer-framework-blog]]).
- Claimed benefits: higher accuracy by allocating limited context with LLM
  reasoning over all lateral and longitudinal information, and lower cost by
  removing redundant information ([[actor-gatherer-framework-blog]]).
- Cost/latency trade-off: changing context can invalidate the KV-cache, and
  spending more time gathering worsens latency, so either is "only worth it if
  it is expected to improve accuracy" ([[actor-gatherer-framework-blog]]).
- In code, the context is built without any agent tool call. Slow LLM work
  runs in background builds, and the per-call `read` stays fast. A
  database-path hint lets the agent query full history as a fallback
  ([[repo-ucbepic-actor-gatherer]]). The docs' policy contract: `read` "runs before every model call"
  ([[actor-gatherer-docs]]).
- A related result on the write side of memory: adding LLM-driven processing between history and reader (atomic-fact extraction, summaries, graph links) lowered accuracy and raised ingestion cost on MemoryAgentBench (GPT-4o-mini reader: -19.62, -5.81 and -5.78 points; 21.6 to 109.3M LLM tokens against none), so extra LLM reasoning is not automatically a gain ([[raw-rag-naive-rag-agentic-memory]])

## Contradictions
- Whether extra LLM reasoning over context pays off: [[actor-gatherer-framework-blog]] claims higher accuracy from LLM reasoning over lateral and longitudinal information (+32 points single-agent on the authors' tasks), while [[raw-rag-naive-rag-agentic-memory]] finds LLM-built memory entries worse than raw retrieval on conversation benchmarks. (inference) They differ in stage (building context for each call against ingestion-time memory construction), task and reader; neither tests the other's setting.

## Related
- [[actor-gatherer]] — the reference implementation
- [[segment-based-context-policy]] — its concrete policy
- [[unknown-unknowns]] — the motivating failure mode
- [[longitudinal-and-lateral-awareness]]
