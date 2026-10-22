# Index

Catalog of every page in this wiki. Read this first when answering a query.
Updated on every ingest. See [[overview]] for the big picture.

Pages: 3 sources, 13 entities, 9 concepts, 0 synthesis.

## Sources

| Page | Description |
|---|---|
| [[actor-gatherer-framework-blog]] | 2026 UC Berkeley blog post introducing Actor-Gatherer: a Gatherer sets coding agents' context; +32 pts single-agent, +31 pts multi-agent on the authors' tasks. |
| [[actor-gatherer-docs]] | Actor-Gatherer documentation: `ag` CLI, config, harness integrations (hook vs proxy), Policy/Poller/Adaptor extension APIs. |
| [[repo-ucbepic-actor-gatherer]] | Official Actor-Gatherer code (MIT, 076c26d): SQLite event store, ProactiveContextManager, file poller, 4 harnesses; no eval code. |

## Entities

| Page | Description |
|---|---|
| [[actor-gatherer]] | Bolt-on framework: Actors do tasks, a shared Gatherer decides their context before every model call. |
| [[birdinteract]] | Interactive data-analysis dataset; base of Actor-Gatherer's planted-spec data-analysis task. |
| [[claude-code]] | Anthropic's coding harness; compaction-based; integrated into Actor-Gatherer through a proxy. |
| [[codex]] | OpenAI's coding harness; main baseline and default Actor (AG-Codex) in the Actor-Gatherer evaluation. |
| [[context-language-models]] | CLM: agent edits its own context file; tool-based baseline. |
| [[epic-data-lab]] | UC Berkeley lab (ucbepic) behind Actor-Gatherer. |
| [[mem0]] | Long-term memory layer (retrieved summaries); memory baseline Mem0-Codex. |
| [[opencode]] | Open-source coding harness; integrated into Actor-Gatherer through a plugin. |
| [[pi-coding-agent]] | Pi coding harness; AG-Pi fastest and cheapest in the harness comparison. |
| [[recursive-language-models]] | RLM: context offloaded into variables the model accesses; tool-based baseline. |
| [[scroll]] | Context as an Environment: programmatic context offloading with a summary of past actions; baseline. |
| [[spider-2]] | Text-to-SQL benchmark; source of the session-analysis history. |
| [[swe-bench]] | GitHub-issue benchmark; base of the planted-spec coding task. |

## Concepts

| Page | Description |
|---|---|
| [[context-compaction]] | Default harness policy: append, then summarise when near the limit; lossy. |
| [[environment-change-awareness]] | Telling an agent that files it relies on changed outside its own actions. |
| [[kv-cache-aware-context-ordering]] | Stable context first, volatile last; edit context only when worth the cache miss. |
| [[longitudinal-and-lateral-awareness]] | Own-history vs parallel-agents-and-environment awareness framing. |
| [[multi-agent-context-sharing]] | Making one agent's session information available to another, across harnesses. |
| [[proactive-context-management]] | A component other than the agent chooses its context before each call. |
| [[segment-based-context-policy]] | Append-only within a task segment; LLM-driven context switch at boundaries. |
| [[tool-based-context-management]] | Agent searches/edits offloaded context with tools (RLM, CLM, Scroll). |
| [[unknown-unknowns]] | Needed information the agent does not know it lacks, so never searches for. |

## Synthesis

| Page | Description |
|---|---|

## Unprocessed

