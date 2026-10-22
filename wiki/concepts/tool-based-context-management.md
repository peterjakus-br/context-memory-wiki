---
title: "Tool-based context management"
type: concept
created: 2026-10-22
updated: 2026-10-22
tags: [context-management, policy, context-offloading]
sources: [actor-gatherer-framework-blog, repo-ucbepic-actor-gatherer]
confidence: medium
---
Tool-based context management offloads the agent's context to external
variables or files and gives the agent tools to search, read or edit that
store, so the agent manages its own context. Examples are
[[recursive-language-models]], [[context-language-models]] and [[scroll]];
MemGPT is cited as an earlier instance.

## What the sources say
- "the agent itself can search the history using tools. However, this
  approach relies on agents knowing what information to search for in the
  first place" ([[actor-gatherer-framework-blog]]).
- Such approaches also often keep irrelevant information in context, because
  "retrieval is often imprecise" and they keep recent raw trajectory or its
  metadata ([[actor-gatherer-framework-blog]]).
- Results on the authors' tasks (gemini-3.1-pro-preview): RLM 32%, Scroll 41%,
  CLM 41% average single-agent accuracy, against AG-Codex's 91% ([[actor-gatherer-framework-blog]]).
- [[actor-gatherer]] keeps only a fallback of this kind: the context tells
  the agent the SQLite path and a sample query for full history ([[repo-ucbepic-actor-gatherer]]).

## Related
- [[unknown-unknowns]] — the weakness attributed to it
- [[proactive-context-management]] — the contrasting approach
