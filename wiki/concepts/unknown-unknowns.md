---
title: "Unknown unknowns (in agent context)"
type: concept
created: 2026-10-22
updated: 2026-10-22
tags: [failure-mode, context-management]
sources: [actor-gatherer-framework-blog, repo-ucbepic-actor-gatherer]
confidence: medium
---
Unknown unknowns are information an agent needs to do a task correctly but
does not have and does not know it is missing, so it never searches for it.
The term is used in [[actor-gatherer-framework-blog]] as the main argument
against agent-driven retrieval.

## What the sources say
- Tool-based approaches "miss unknown unknowns: context that an agent needs
  to perform the task but does not know is needed, coming from both past and
  parallel user interactions, or from changes in the environment"
  ([[actor-gatherer-framework-blog]]).
- Examples: an earlier instruction to keep the code compatible with Python
  3.8; a file changed by the user or by a parallel agent ([[actor-gatherer-framework-blog]]).
- Evidence offered: on data analysis, "agents often do not know that past
  information is needed … and often answer the question without looking at
  the history at all". Codex+Hint "misses information it doesn't know to
  search for" ([[actor-gatherer-framework-blog]]).
- In code, the counter-measure is a set of per-task retention notes
  (handling, terms, standing instructions), together with a ranking prompt
  that ranks highest a task that carries a standing instruction, "EVEN IF
  ITS OWN SUBJECT LOOKS UNRELATED". Every earlier user request is also kept
  verbatim in an index ([[repo-ucbepic-actor-gatherer]]).

## Related
- [[tool-based-context-management]] — vulnerable to it, per [[actor-gatherer-framework-blog]]
- [[proactive-context-management]] — the proposed remedy
- [[swe-bench]], [[birdinteract]] — planted-specification tasks that probe
  it
