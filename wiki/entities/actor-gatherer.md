---
title: "Actor-Gatherer"
type: entity
created: 2026-10-22
updated: 2026-10-22
tags: [framework, context-management, multi-agent]
sources: [actor-gatherer-framework-blog, actor-gatherer-docs, repo-ucbepic-actor-gatherer]
---
Actor-Gatherer is an open-source, bolt-on context-management framework for
coding agents from [[epic-data-lab]] (UC Berkeley, 2026). It splits an agent
into an **Actor**, an existing harness that does the task, and a **Gatherer**,
a shared component that stores what all Actors and the environment do and
decides each Actor's context before every model call. It is this wiki's
reference example of [[proactive-context-management]]: context is chosen for
the agent rather than fetched by it, which is aimed at
[[unknown-unknowns]].

## Facts
- Authors: Sepanta Zeighami, Kerem Akillioglu, Asim Biswal, Alvin Cheung,
  Joseph E. Gonzalez, Aditya G. Parameswaran ([[actor-gatherer-framework-blog]]).
- Stated goal: give agents both longitudinal and lateral awareness
  ([[longitudinal-and-lateral-awareness]]): "We separate the 'thinking' from
  the 'remembering'" ([[actor-gatherer-framework-blog]]).
- **What is stored**: every message, tool call, tool output, pinned
  harness context, reasoning blob, file-change event and stream message, as
  typed events in one SQLite database per named gatherer. Rows are never
  deleted, and every context sent is logged ([[actor-gatherer-docs]], [[repo-ucbepic-actor-gatherer]]).
- **Who selects context, and when**: the Gatherer's policy, on every model
  call (`get_context`, `read` in code). Heavy LLM work (segmentation,
  summaries, ranking) runs in background builds, and the context is switched
  only at task (segment) boundaries or when over the limit
  ([[segment-based-context-policy]]; [[actor-gatherer-framework-blog]], [[repo-ucbepic-actor-gatherer]]).
- **Granularity**: coarse to fine sections (index of all user requests,
  messages-only tasks, ranked related tasks with retention notes, previous
  task in full, verbatim running task) ([[repo-ucbepic-actor-gatherer]]). The blog describes
  placing stable information early for KV-cache reuse
  ([[kv-cache-aware-context-ordering]]; [[actor-gatherer-framework-blog]]).
- **Scope**: multi-agent and cross-harness. Actors that name the same
  gatherer share it, and each session is a `channel`
  ([[multi-agent-context-sharing]]; [[actor-gatherer-docs]], [[repo-ucbepic-actor-gatherer]]). The environment is
  observed through pollers; only a file-change poller ships
  ([[environment-change-awareness]]; [[repo-ucbepic-actor-gatherer]]).
- **Integrations**: [[claude-code]] and [[codex]] (local proxy),
  [[pi-coding-agent]] and [[opencode]] (plugins) ([[actor-gatherer-docs]], [[repo-ucbepic-actor-gatherer]]).
- **Results** (authors' benchmarks; agent model gemini-3.1-pro-preview; Actor
  = Codex): 91% average accuracy vs 59% for Mem0-Codex in single-agent
  tasks, and 100% vs 69% for Codex+Hint in multi-agent tasks ([[actor-gatherer-framework-blog]]).
  Across harnesses on the coding task, all four AG variants reach 71%
  ([[actor-gatherer-framework-blog]]).
- **Limitations**: there is no default Gatherer LLM, and every Gatherer call
  costs tokens or subscription quota ([[actor-gatherer-docs]]). Evaluation code and baselines
  are not released ([[repo-ucbepic-actor-gatherer]]). A gatherer's policy cannot be changed once in
  use ([[actor-gatherer-docs]]).

## Related
- [[mem0]], [[recursive-language-models]], [[context-language-models]],
  [[scroll]] — baselines it is compared against
- [[context-compaction]], [[tool-based-context-management]] — the two
  approaches it positions itself against
