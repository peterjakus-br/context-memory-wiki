---
title: "Scroll (Context as an Environment)"
type: entity
created: 2026-10-22
updated: 2026-10-22
tags: [framework, tool-based]
sources: [actor-gatherer-framework-blog]
---
Scroll, from "Context as an Environment: Programmatic Context Management for
Long-Horizon Agents" (Lin et al., arXiv:2608.21690, 2026): programmatic
context offloading into variables, plus a kept summary of past actions. It is
a baseline in [[actor-gatherer-framework-blog]].

## Facts
- Stores context in variables, like RLM but with a different strategy for
  what is kept in context ([[actor-gatherer-framework-blog]]).
- "Scroll performs better than RLM, as it maintains a summary of past
  actions that allows the agent to obtain the past specification". 41%
  average single-agent accuracy ([[actor-gatherer-framework-blog]]).

## Related
- [[tool-based-context-management]]
- [[recursive-language-models]], [[context-language-models]]
