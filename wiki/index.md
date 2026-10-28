# Index

Catalog of every page in this wiki. Read this first when answering a query.
Updated on every ingest. See [[overview]] for the big picture.

Pages: 5 sources, 25 entities, 13 concepts, 0 synthesis.

## Sources

| Page | Description |
|---|---|
| [[actor-gatherer-framework-blog]] | 2026 UC Berkeley blog post introducing Actor-Gatherer: a Gatherer sets coding agents' context; +32 pts single-agent, +31 pts multi-agent on the authors' tasks. |
| [[actor-gatherer-docs]] | Actor-Gatherer documentation: `ag` CLI, config, harness integrations (hook vs proxy), Policy/Poller/Adaptor extension APIs. |
| [[repo-ucbepic-actor-gatherer]] | Official Actor-Gatherer code (MIT, 076c26d): SQLite event store, ProactiveContextManager, file poller, 4 harnesses; no eval code. |
| [[raw-rag-naive-rag-agentic-memory]] | Bao et al. (arXiv 2610.30755, 2026): dense retrieval plus rerank over raw history ranks first among compared memory systems in 6 of 7 settings; coverage and raw preservation explain it. |
| [[repo-litmeb-raw-rag]] | Official Raw-RAG code (MIT, 9563919): one `rag` adapter in an EverCore-based evaluation harness, Mem0 add-only control, ablation adapters, paper profiles; no data or results; manifest-only. |

## Entities

| Page | Description |
|---|---|
| [[actor-gatherer]] | Bolt-on framework: Actors do tasks, a shared Gatherer decides their context before every model call. |
| [[birdinteract]] | Interactive data-analysis dataset; base of Actor-Gatherer's planted-spec data-analysis task. |
| [[claude-code]] | Anthropic's coding harness; compaction-based; integrated into Actor-Gatherer through a proxy. |
| [[codex]] | OpenAI's coding harness; main baseline and default Actor (AG-Codex) in the Actor-Gatherer evaluation. |
| [[context-language-models]] | CLM: agent edits its own context file; tool-based baseline. |
| [[emem]] | Memory system: elementary discourse units (EMem) and graph variant (EMem-G); highest utilization. |
| [[epic-data-lab]] | UC Berkeley lab (ucbepic) behind Actor-Gatherer. |
| [[evermemos]] | Memory system: MemCells, episodes, atomic facts, profile; agentic retrieval; slowest ingestion of the six timed. |
| [[locomo]] | Long-term conversation QA benchmark: 10 conversations, 1,540 non-adversarial questions. |
| [[longmemeval]] | Chat-memory benchmark, a dated history per example; 500 examples, six question types plus abstention. |
| [[mem0]] | Long-term memory layer (retrieved summaries); memory baseline Mem0-Codex; audited for UPDATE/DELETE rates; scores in the Raw-RAG comparison. |
| [[meme-benchmark]] | Dynamic-memory benchmark: 100 episodes, 1,188 questions on recall, aggregation, tracking, deletion, cascade, absence. |
| [[memmachine]] | Memory system: episodic plus semantic memory; closest competitor to Raw-RAG; separate top-20 sections. |
| [[memora]] | Memory system: values plus cue anchors, prompted-policy retriever; strongest compared on LongMemEval and MemoryAgentBench. |
| [[memoryagentbench]] | 2,071 questions from 14 sources: retrieval, test-time learning, long-range understanding, conflict resolution. |
| [[memos]] | Memory system: extracted text and preference memories, fine search with rerank and MMR. |
| [[memu]] | Memory system: profile, event, knowledge and behaviour items; lowest coverage and path coverage in the Raw-RAG comparison. |
| [[opencode]] | Open-source coding harness; integrated into Actor-Gatherer through a plugin. |
| [[pi-coding-agent]] | Pi coding harness; AG-Pi fastest and cheapest in the harness comparison. |
| [[raw-rag]] | Naive baseline: raw 256-token windows, 128 dense candidates, cross-encoder rerank to 15; no LLM at ingestion. |
| [[recursive-language-models]] | RLM: context offloaded into variables the model accesses; tool-based baseline. |
| [[scroll]] | Context as an Environment: programmatic context offloading with a summary of past actions; baseline. |
| [[simplemem]] | Memory system: compact structured entries, three retrieval channels with reflection; evaluated on LoCoMo. |
| [[spider-2]] | Text-to-SQL benchmark; source of the session-analysis history. |
| [[swe-bench]] | GitHub-issue benchmark; base of the planted-spec coding task. |

## Concepts

| Page | Description |
|---|---|
| [[context-compaction]] | Default harness policy: append, then summarise when near the limit; lossy. |
| [[environment-change-awareness]] | Telling an agent that files it relies on changed outside its own actions. |
| [[evidence-coverage-and-utilization]] | Coverage (sufficient evidence surfaced) vs utilization (accuracy given it) vs path coverage. |
| [[kv-cache-aware-context-ordering]] | Stable context first, volatile last; edit context only when worth the cache miss. |
| [[longitudinal-and-lateral-awareness]] | Own-history vs parallel-agents-and-environment awareness framing. |
| [[memory-mutation]] | UPDATE/DELETE vs append-only memory writes; Mem0 audit and ADD/NONE-only result. |
| [[multi-agent-context-sharing]] | Making one agent's session information available to another, across harnesses. |
| [[proactive-context-management]] | A component other than the agent chooses its context before each call. |
| [[reranking]] | Second-stage cross-encoder re-scoring of retrieval candidates; removal costs 3.92 points in the Raw-RAG ablation. |
| [[retrieval-augmented-memory]] | Retrieving stored history (raw or transformed) into context at query time; raw-history retrieval vs extraction. |
| [[segment-based-context-policy]] | Append-only within a task segment; LLM-driven context switch at boundaries. |
| [[tool-based-context-management]] | Agent searches/edits offloaded context with tools (RLM, CLM, Scroll). |
| [[unknown-unknowns]] | Needed information the agent does not know it lacks, so never searches for. |

## Synthesis

| Page | Description |
|---|---|

## Unprocessed

