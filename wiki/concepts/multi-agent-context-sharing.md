---
title: "Multi-agent context sharing"
type: concept
created: 2026-10-22
updated: 2026-10-22
tags: [context-management, multi-agent]
sources: [actor-gatherer-framework-blog, actor-gatherer-docs, repo-ucbepic-actor-gatherer]
confidence: medium
---
Multi-agent context sharing means making information from one agent's
session (the user's requests, decisions, results) available in another
agent's context when it is relevant, including across different harnesses.

## What the sources say
- Existing harnesses provide no information about other agents. In the
  authors' cross-session task, vanilla Codex "is unable to perform any of the
  cross-session tasks correctly" (0%), and Codex+Hint, which is given the path
  to other agents' traces, gets some right at higher cost ([[actor-gatherer-framework-blog]]).
- AG-Codex: 100% average accuracy on cross-session sharing, annotated "+33
  pts" over Codex+Hint, at lower cost per task (gemini-3.1-pro-preview,
  authors' benchmark) ([[actor-gatherer-framework-blog]]).
- Setup: Actors that name the same gatherer (`ag --gatherer NAME …`) share
  it, across harnesses ([[actor-gatherer-docs]]).
- In code: each session is a channel. Other channels' user requests are
  indexed and injected just before the latest user message, and other
  channels' tasks can be ranked in. Their raw agent work is not shown by
  default ([[repo-ucbepic-actor-gatherer]]).

## Related
- [[longitudinal-and-lateral-awareness]]
- [[environment-change-awareness]]
- [[actor-gatherer]]
