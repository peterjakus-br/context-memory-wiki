---
title: "Mem0"
type: entity
created: 2026-10-22
updated: 2026-10-22
tags: [memory-system]
sources: [actor-gatherer-framework-blog]
---
Mem0 is a long-term memory layer for agents (Chhikara et al., "Mem0: Building
Production-Ready AI Agents with Scalable Long-Term Memory", arXiv:2504.19413,
2025). It appears in this wiki as the memory baseline in
[[actor-gatherer-framework-blog]].

## Facts
- **What is stored**: summaries of the past ("memories"). **How context is
  selected**: retrieved, e.g. through embedding similarity, based on the user
  task, and appended to the harness context ([[actor-gatherer-framework-blog]]).
- Limitation, per the blog: "Such summaries are still lossy, and
  embedding-based retrieval can be inaccurate". Failures occur "when it either
  does not retrieve the relevant information or the relevant information is
  not included in its memories at all" ([[actor-gatherer-framework-blog]]).
- Mem0-Codex scores 59% average single-agent accuracy, the second best after
  AG-Codex's 91% (agent model gemini-3.1-pro-preview, authors' benchmarks).
  It sometimes recovers the specification that Codex loses in compaction
  ([[actor-gatherer-framework-blog]]).

## Related
- [[context-compaction]] — Mem0 complements a compaction harness
- [[actor-gatherer]] — compared against it
