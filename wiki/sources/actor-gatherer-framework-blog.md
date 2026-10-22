---
title: "The Actor-Gatherer Framework for AI Agents (blog post)"
type: source
created: 2026-10-22
updated: 2026-10-22
tags: [actor-gatherer, context-management, multi-agent, coding-agents, blog]
source: raw/2026-10-22-actor-gatherer-framework-blog.html
---
Blog post by Sepanta Zeighami, Kerem Akillioglu, Asim Biswal, Alvin Cheung,
Joseph E. Gonzalez and Aditya G. Parameswaran ([[epic-data-lab]], UC
Berkeley), 2026, announcing [[actor-gatherer]]. There is no separate paper; the
post is the primary write-up. It links the code
([[repo-ucbepic-actor-gatherer]]) and a docs page ([[actor-gatherer-docs]]).
Converted text: `raw/2026-10-22-actor-gatherer-framework-blog.md`; figures in
`raw/2026-10-22-actor-gatherer-framework-blog_images/`.

## Summary
The post proposes **Actor-Gatherer**, "a new paradigm in agent design where the
context across agents is managed proactively and externally". An **Actor** agent
(an ordinary coding agent such as [[codex]], [[claude-code]], [[pi-coding-agent]]
or [[opencode]]) performs the task; a **Gatherer** component observes that
Actor, other agents and the environment, stores everything in a shared data
layer and decides, before every LLM call, what the Actor's context should be
— "We separate the 'thinking' from the 'remembering'." The authors argue that
compaction-based harnesses lose information, memory add-ons retrieve lossy
summaries imprecisely, and tool-based approaches (RLM, CLM, Scroll) miss
[[unknown-unknowns]]. In their evaluation, Actor-Gatherer on Codex (AG-Codex)
beats every baseline in single-agent, multi-agent and changing-environment
settings, at lower cost than the second-best approach.

## Key points
- **Problem framing.** Users run interrelated tasks with agents over long
  sessions, often several in parallel. Agents need *longitudinal awareness*
  (history of the current session) and *lateral awareness* (the user's
  simultaneous interactions with other agents and changes in the environment);
  see [[longitudinal-and-lateral-awareness]]. Fig. 3 places compaction
  harnesses (Codex, Claude Code, Pi) at low longitudinal and no lateral
  awareness, memory systems ([[mem0]], A-Mem) and tool-based methods (RLM, CLM,
  Scroll) at medium longitudinal and no lateral awareness, and Actor-Gatherer
  at high/yes.
- **Why existing harnesses fail** (Fig. 4):
  - [[context-compaction]] (Codex, Claude Code): lossy summaries of older
    interactions plus full recent trajectories that may be redundant after a
    task switch; no lateral information, so an agent "may not become aware of
    a file change and incorrectly rely on its old value". Memory add-ons
    ([[mem0]], A-MEM) append retrieved summaries ("memories"), still lossy and
    with inaccurate embedding retrieval.
  - [[tool-based-context-management]] (Recursive Language Models, Context
    Language Models, Scroll, also citing MemGPT): the agent searches or edits
    its own context with tools, which misses [[unknown-unknowns]] — "context
    that an agent needs to perform the task but does not know is needed".
    Example: an earlier instruction to stay compatible with Python 3.8. These
    approaches also keep irrelevant information (recent raw trajectory or its
    metadata) in context.
- **Architecture** (Figs. 4c, 5; walkthrough Figs. 1–6 of the carousel): the
  Gatherer is a server shared by Actors from different harnesses. Actors call
  `insert` to give it information and `get_context` before each LLM call.
  *Pollers* insert information from the environment through pull-based
  streams. A context-management policy inside the Gatherer uses LLMs
  "combined with other temporally-aware rules" to decide what information, at
  what granularity, each Actor gets. This is
  [[proactive-context-management]] and covers
  [[multi-agent-context-sharing]] and [[environment-change-awareness]].
- **Context-management policy** (Fig. 6): a [[segment-based-context-policy]].
  A *segment* is "a contiguous group of user and agent interactions that serve
  a single purpose". Within a segment the context is append-only (new tool
  calls, outputs, plus relevant concurrent events from other agents or the
  environment) to keep cost and latency low. At segment boundaries the
  Gatherer performs a *context switch*: an LLM reasons over the histories and
  trajectories of all agents in the Gatherer database, with "a temporal
  inductive bias that gives more weight to more recent observations", removing
  irrelevant and adding relevant information. Gatherer messages come at
  coarse-to-fine granularity; information expected to stay relevant is placed
  earlier to maximise KV-cache reuse, volatile information later
  ([[kv-cache-aware-context-ordering]]). The post notes that changing context
  can invalidate the KV-cache, so a switch is only worth it when it is
  expected to improve accuracy.
- **Evaluation setup (single agent).** Baselines: vanilla Codex, Mem0-Codex,
  RLM, CLM and Scroll. Agent model gemini-3.1-pro-preview; histories generated
  with GPT-5.6-Terra "to reduce cost". Three tasks:
  - *Coding*: a variation of [[swe-bench]] where part of the task
    specification is removed from the task and planted in a history of other
    related and unrelated tasks.
  - *Data analysis*: same idea with the [[birdinteract]] dataset; the history
    holds planted information about which tables and columns to use.
  - *Session analysis*: questions about the history itself (built from
    [[spider-2]] data-analysis questions), e.g. "which questions discussed
    Africa", scored by F1 of the returned set.
- **Single-agent results** (gemini-3.1-pro-preview agents; figure labels).
  Fig. 1 "Avg. Accuracy": AG-Codex 91%, Codex 32%, Mem0-Codex 59%, Scroll
  41%, RLM 32%, CLM 41%; annotated "+32 pts" over Mem0-Codex. The
  accuracy-vs-cost figure annotates AG-Codex at "+27 pts" over the best
  baseline on coding, "+36 pts" on data analysis and "+0.19 F1" on session
  analysis. Text: RLMs "often do not look for the specification in their
  history"; Scroll does better thanks to a summary of past actions; Codex
  "frequently loses the specification during compaction, which is sometimes
  recovered by Mem0". On data analysis, tool-based baselines do markedly worse
  than on coding because agents often answer without looking at the history.
- **Multi-agent results.** Baselines: Codex and Codex+Hint (told that other
  agents may have relevant information and given the path to their traces).
  Scenarios: *cross-session information sharing* (the specification is in
  another agent's history) and *environment changes* (required files are
  modified mid-task by other agents or the user). Fig. 2 "Avg. Accuracy":
  AG-Codex 100%, Codex+Hint 69%, Codex 0%, annotated "+31 pts". Per-scenario
  figures annotate "+33 pts" (cross-session) and "+25 pts" (environment
  changes) over Codex+Hint. Codex "is unable to perform any of the
  cross-session tasks correctly"; both Codex variants cost more in
  cross-session sharing because they search more.
- **Across harnesses** (coding task): AG-Codex, AG-Pi, AG-OpenCode and
  AG-ClaudeCode all reach 71% average accuracy; average cost per task $1.26,
  $0.87, $1.24, $1.23; average latency 441 s, 206 s, 370 s, 333 s. AG-Pi is
  fastest and cheapest "because it performs less validation after it
  generates a first answer".
- **Headline claims** (TL;DR and conclusion): "+32% higher accuracy over
  state-of-the-art for a long-running single agent, and +31% with parallel
  agents and in a changing environment"; "at least 27% on coding and 36% on
  data analysis tasks" in single-agent settings. The figures label these as
  percentage points.

## Entities and concepts
- [[actor-gatherer]] — the framework introduced
- [[repo-ucbepic-actor-gatherer]] — the official code
- [[actor-gatherer-docs]] — the companion docs page
- [[epic-data-lab]] — the UC Berkeley lab that built it
- [[codex]], [[claude-code]], [[pi-coding-agent]], [[opencode]] — harnesses
  used as Actors; Codex is the main evaluation baseline
- [[mem0]] — memory baseline (Mem0-Codex)
- [[recursive-language-models]], [[context-language-models]], [[scroll]] —
  tool-based baselines
- [[swe-bench]], [[birdinteract]], [[spider-2]] — datasets the tasks are
  built from
- [[proactive-context-management]] — the central idea
- [[segment-based-context-policy]] — the Gatherer's policy
- [[unknown-unknowns]] — the failure mode it targets
- [[longitudinal-and-lateral-awareness]] — the framing of what agents lack
- [[context-compaction]] — the default policy it criticises
- [[tool-based-context-management]] — the alternative it criticises
- [[multi-agent-context-sharing]], [[environment-change-awareness]] — the
  lateral capabilities
- [[kv-cache-aware-context-ordering]] — placement rule in the context

## Open questions
- No paper, no dataset release and no number of task instances are given;
  the benchmarks are the authors' own constructions (planted specifications in
  generated histories), so results may favour a system designed to find
  planted facts. Whether the evaluation harness is public is unclear from the
  post; see [[repo-ucbepic-actor-gatherer]].
- Units: the TL;DR says "+32% higher accuracy", but the figures label the gap
  as "+32 pts" (91% vs 59%). It is an absolute gain in percentage points, not a
  relative one.
- Fig. 1's 91% matches the mean of the coding and data-analysis accuracies
  (inference from the scatter plots; the post does not say how the average is
  formed). The equivalent for Fig. 2 is unclear: the per-scenario gains of +33
  and +25 points do not obviously average to the +31 points shown.
- In the harness comparison, AG-Codex scores 71% on the coding task, while the
  single-agent coding plot shows AG-Codex above the 80% gridline. The post does not
  explain the difference (perhaps another model or a subset).
- Agents run on gemini-3.1-pro-preview, but the histories were generated by a
  different model (GPT-5.6-Terra). Whether the results carry over to
  self-generated histories is not tested.
- The Gatherer's own LLM cost and latency are presumably in the per-task cost
  figures, but the post does not say so explicitly.
- Typos in the conclusion ("It separating", "basedlines") are left as in the
  source.
