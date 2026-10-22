---
title: "BirdInteract"
type: entity
created: 2026-10-22
updated: 2026-10-22
tags: [benchmark, data-analysis, text-to-sql]
sources: [actor-gatherer-framework-blog]
---
BirdInteract, a dataset of interactive data-analysis (database) tasks, used
as the base of the data-analysis task in [[actor-gatherer-framework-blog]].

## Facts
- The history includes "planted information about which tables and columns
  to use, and how to use them" ([[actor-gatherer-framework-blog]]).
- AG-Codex is annotated "+36 pts" over the best baseline (Mem0-Codex) on this
  task. Tool-based baselines do markedly worse than on coding because agents
  answer without consulting history ([[actor-gatherer-framework-blog]]).

## Related
- [[swe-bench]], [[spider-2]]
- [[unknown-unknowns]]
