---
title: "Environment-change awareness"
type: concept
created: 2026-10-22
updated: 2026-10-22
tags: [context-management, multi-agent]
sources: [actor-gatherer-framework-blog, actor-gatherer-docs, repo-ucbepic-actor-gatherer]
confidence: medium
---
Environment-change awareness means telling an agent when something it relies
on (a file, a table) has changed outside its own actions, whether through the
user or a parallel agent, so that it does not act on stale observations.

## What the sources say
- Without it, "an agent may not become aware of a file change and incorrectly
  rely on its old value" ([[actor-gatherer-framework-blog]]).
- Evaluation: files required by a task are modified mid-task. AG-Codex
  reaches 100% average accuracy in this scenario, annotated "+25 pts" over
  Codex+Hint, while vanilla Codex "handles environment changes incorrectly"
  ([[actor-gatherer-framework-blog]]).
- Mechanism: pollers insert environment events into the Gatherer. The
  shipped `file_changes` poller watches the working directory ([[actor-gatherer-docs]]).
  A notice reaches the agent only if earlier context mentions the file, the
  change is in the same cwd and it was not the agent's own write. Changes are
  picked up at the next model call ([[repo-ucbepic-actor-gatherer]]).

## Related
- [[longitudinal-and-lateral-awareness]]
- [[multi-agent-context-sharing]]
- [[unknown-unknowns]]
