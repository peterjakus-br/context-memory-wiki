---
title: "Recursive Language Models (RLM)"
type: entity
created: 2026-10-22
updated: 2026-10-22
tags: [framework, tool-based]
sources: [actor-gatherer-framework-blog]
---
Recursive Language Models (Zhang, Kraska, Khattab, arXiv:2512.24601, 2026):
an approach in which the agent's context is offloaded into variables that the
model accesses programmatically. It is a baseline in
[[actor-gatherer-framework-blog]].

## Facts
- Classed as [[tool-based-context-management]]. RLM "store[s] context in
  variables" ([[actor-gatherer-framework-blog]]).
- On the coding task "RLMs perform poorly, as they often do not look for the
  specification in their history". 32% average single-agent accuracy
  ([[actor-gatherer-framework-blog]]).

## Related
- [[context-language-models]], [[scroll]] — sibling baselines
- [[unknown-unknowns]] — the failure mode attributed to it
