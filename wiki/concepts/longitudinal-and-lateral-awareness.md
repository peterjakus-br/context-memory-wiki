---
title: "Longitudinal and lateral awareness"
type: concept
created: 2026-10-22
updated: 2026-10-22
tags: [context-management, framing]
sources: [actor-gatherer-framework-blog, repo-ucbepic-actor-gatherer]
confidence: medium
---
A framing of what an agent needs to know: **longitudinal awareness** is
knowledge of the agent's own past (the history of the current session),
while **lateral awareness** is knowledge of what happens alongside it (the
user's simultaneous work with other agents, and changes in the environment).
Introduced in [[actor-gatherer-framework-blog]].

## What the sources say
- "agents need longitudinal awareness of past user interactions with the
  agent itself … as well as lateral awareness of the user's simultaneous
  interactions with other agents and changes in the environment"
  ([[actor-gatherer-framework-blog]]).
- Placement in the blog's Fig. 3: compaction harnesses (Codex, Claude Code,
  Pi) are low/no; memory systems (Mem0, A-Mem) and tool-based methods (RLM,
  CLM, Scroll) are medium/no; Actor-Gatherer is high/yes ([[actor-gatherer-framework-blog]]).
- In code, longitudinal awareness comes from the channel's own tasks and
  sections, and lateral awareness from other channels' requests and ranked
  tasks plus file-change notices ([[repo-ucbepic-actor-gatherer]]).

## Related
- [[multi-agent-context-sharing]], [[environment-change-awareness]] — the two
  lateral halves
- [[context-compaction]] — limits longitudinal awareness
