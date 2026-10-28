---
title: Overview
type: overview
created: 2026-10-22
updated: 2026-10-28
tags: [overview]
sources: [actor-gatherer-framework-blog, actor-gatherer-docs, repo-ucbepic-actor-gatherer, raw-rag-naive-rag-agentic-memory]
---
# Overview

This wiki compiles sources on context management and memory for LLMs and
agents. It holds one project from three angles:
[[actor-gatherer]] (UC Berkeley [[epic-data-lab]], 2026), seen through its
announcement blog post ([[actor-gatherer-framework-blog]]), its
documentation ([[actor-gatherer-docs]]) and its official code
([[repo-ucbepic-actor-gatherer]]), and one paper on memory systems,
[[raw-rag-naive-rag-agentic-memory]] (2026), which tests whether complex
agentic memory beats retrieval over raw history.

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

## 4. Memory systems and how they are evaluated

[[raw-rag-naive-rag-agentic-memory]] compares [[raw-rag]], a naive dense
retrieval plus [[reranking]] pipeline over raw conversation history, with
twelve or more transformation-based memory systems (those with pages here:
[[mem0]], [[evermemos]],
[[memos]], [[memu]], [[memmachine]], [[memora]], [[emem]], [[simplemem]]) on
[[locomo]], [[longmemeval]], [[meme-benchmark]] and [[memoryagentbench]].
The raw baseline ranks first in six of seven benchmark–reader settings, the
write-side operations that change memory are rarely used ([[memory-mutation]]),
and the differences between systems are mostly about how often sufficient
evidence is surfaced at all ([[evidence-coverage-and-utilization]]). The
overall approach is in [[retrieval-augmented-memory]]. Its scope is offline
conversation question answering: it does not test coding-agent sessions,
parallel agents or environment changes, which is where
[[proactive-context-management]] makes its claims. The two sources' results
are not comparable (different tasks, readers and scores); the tension is
recorded on [[retrieval-augmented-memory]] and [[proactive-context-management]].

## 5. Evidence so far

All quantitative evidence on proactive context comes from the Actor-Gatherer
authors, on their own planted-specification tasks built from [[swe-bench]],
[[birdinteract]] and [[spider-2]]. No independent replication exists, and the
released code contains no evaluation harness. The memory-systems evidence
comes from the authors of the Raw-RAG baseline, who ran the comparison
themselves and took several baseline scores from other papers. Every concept
page is therefore single-source (one project or one paper) at medium
confidence or below.

## Gaps

Questions the wiki raises but cannot yet answer, with candidate sources to
add to `raw/`:

- **Baseline primary sources.** The papers for Mem0 (arXiv:2504.19413),
  A-MEM (arXiv:2502.12110), MemGPT (arXiv:2310.08560), Recursive Language
  Models (arXiv:2512.24601), Context Language Models (arXiv:2609.37725) and
  Scroll (arXiv:2608.21690). They would let the entity pages describe each
  system in its own terms, not only as a baseline.
- **Independent evaluation of long-session and multi-agent context.** Public
  memory benchmarks now have pages ([[locomo]], [[longmemeval]],
  [[meme-benchmark]], [[memoryagentbench]]), but none tests cross-agent or
  environment-change awareness. Does Actor-Gatherer's lead hold on them, and
  does [[raw-rag]] hold up on coding-agent sessions? Neither has been run.
- **Harness documentation.** Primary docs for Codex, Claude Code, Pi and
  OpenCode compaction and memory features, to replace characterisations made
  by a competitor.
- **Cost of the Gatherer.** How many tokens the Gatherer spends (boundary
  checks, segmentation, ranking) relative to the Actor. Neither the blog nor
  the repo reports this.
- **Long-context models vs context management.** Sources on context rot and
  long-context degradation, which would set out why curation beats a bigger
  window. [[raw-rag-naive-rag-agentic-memory]] gives Full-context rows that
  go both ways (ahead of [[raw-rag]] on MEME with DeepSeek-V4-Flash, behind it
  with GPT-4o-mini and on LoCoMo), which shows reader dependence but not a
  mechanism.
- **Raw-RAG code and independent rerun.** The repository
  github.com/Litmeb/RAW-RAG is not in `raw/`. An independent rerun of the
  comparison, ReFind (a concurrent raw-chat-log system the paper cites but
  does not compare), and the primary papers of the compared systems
  ([[evermemos]], [[memos]], [[memu]], [[memmachine]], [[memora]], [[emem]],
  [[simplemem]]) would show how far the result generalises.
- **Governed, multi-user memory.** The paper lists exposing authoritative state
  to tools, erasure and privacy as untested operational needs; a source that
  evaluates them would test where raw retrieval stops being enough.
