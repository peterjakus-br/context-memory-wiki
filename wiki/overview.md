---
title: Overview
type: overview
created: 2026-10-22
updated: 2026-10-22
tags: [overview]
sources: [actor-gatherer-framework-blog, actor-gatherer-docs, repo-ucbepic-actor-gatherer]
---
# Overview

This wiki compiles sources on context management and memory for LLMs and
agents. It currently holds one project from three angles:
[[actor-gatherer]] (UC Berkeley [[epic-data-lab]], 2026), seen through its
announcement blog post ([[actor-gatherer-framework-blog]]), its
documentation ([[actor-gatherer-docs]]) and its official code
([[repo-ucbepic-actor-gatherer]]).

## 1. Three families of context management

The sources divide current practice into three families:

- [[context-compaction]]: append everything, summarise when full. This is
  the default in [[codex]], [[claude-code]] and [[pi-coding-agent]], and is
  sometimes paired with a memory layer such as [[mem0]]. It is lossy and
  keeps stale detail.
- [[tool-based-context-management]]: context is offloaded to variables or
  files, and the agent queries or edits it itself
  ([[recursive-language-models]], [[context-language-models]], [[scroll]]).
  Its weakness is [[unknown-unknowns]].
- [[proactive-context-management]]: a separate component decides the context
  for the agent. [[actor-gatherer]] is the example here.

## 2. What agents are missing

[[longitudinal-and-lateral-awareness]] separates the agent's own past from
what happens alongside it. Lateral awareness has two halves:
[[multi-agent-context-sharing]] and [[environment-change-awareness]].

## 3. How a proactive policy is built

[[segment-based-context-policy]] keeps the context append-only within a task
and rebuilds it at task boundaries, with LLM segmentation, summaries and
ranking. [[kv-cache-aware-context-ordering]] puts stable material first, so
that rebuilds are rare and cheap.

## 4. Evidence so far

All quantitative evidence comes from the Actor-Gatherer authors, on their
own planted-specification tasks built from [[swe-bench]], [[birdinteract]]
and [[spider-2]]. No independent replication exists, and the released code
contains no evaluation harness. Every concept page is therefore single-source
(one project) at medium confidence or below.

## Gaps

Questions the wiki raises but cannot yet answer, with candidate sources to
add to `raw/`:

- **Baseline primary sources.** The papers for Mem0 (arXiv:2504.19413),
  A-MEM (arXiv:2502.12110), MemGPT (arXiv:2310.08560), Recursive Language
  Models (arXiv:2512.24601), Context Language Models (arXiv:2609.37725) and
  Scroll (arXiv:2608.21690). They would let the entity pages describe each
  system in its own terms, not only as a baseline.
- **Independent evaluation of long-session and multi-agent context.** Are
  there public benchmarks for cross-session or environment-change awareness,
  and does Actor-Gatherer's lead hold on tasks that are not planted
  specifications?
- **Harness documentation.** Primary docs for Codex, Claude Code, Pi and
  OpenCode compaction and memory features, to replace characterisations made
  by a competitor.
- **Cost of the Gatherer.** How many tokens the Gatherer spends (boundary
  checks, segmentation, ranking) relative to the Actor. Neither the blog nor
  the repo reports this.
- **Long-context models vs context management.** Sources on context rot and
  long-context degradation, which would set out why curation beats a bigger
  window.
