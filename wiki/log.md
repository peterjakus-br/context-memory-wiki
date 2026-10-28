# Log

Append-only. One entry per operation, newest at the bottom.
`grep "^## \[" wiki/log.md | tail -5` shows recent work.

## [2026-10-22] schema | Bootstrap the wiki from evals-bench-wiki
- Forked the structure of peterjakus-br/evals-bench-wiki (itself forked from peterjakus-br/semantic-wiki): CLAUDE.md schema, raw/ and wiki/ layout, scripts (lint, add_source, add_repo, find_papers, fetch_papers), tests, the /ingest, /query, /lint commands and the pdf-to-markdown skill.
- Topic changed to context management and memory for LLMs and agents.
- Schema changes: typing rule rewritten (techniques, policies and phenomena are concepts; frameworks, memory systems, harnesses, models, benchmarks are entities); system entity pages record what is stored, who selects context and when, granularity, scope, integrations and limitations. The evals-specific score rule is kept: every reported number names model, task, setting and source.

## [2026-10-22] ingest | The Actor-Gatherer Framework for AI Agents (blog post)
- Read raw/2026-10-22-actor-gatherer-framework-blog.html (fetched from https://ucbepic.github.io/actor-gatherer/, via the LinkedIn announcement link) through its pandoc companion .md, and its 13 figures, including the 6-step architecture walkthrough SVGs. No separate paper exists; the blog post is the primary write-up.
- Triage: new material (first source on the topic).
- Created [[actor-gatherer-framework-blog]].
- Notable: the TL;DR's "+32%" / "+31%" are percentage points per the figures. Unexplained gap between AG-Codex coding accuracy in the baseline plot (above 80%) and the harness comparison (71%). Recorded under Open questions.

## [2026-10-22] ingest | Actor-Gatherer documentation
- Read raw/2026-10-22-actor-gatherer-docs.html (https://ucbepic.github.io/actor-gatherer/docs.html) through its .md companion. A Haiku reader produced structured notes, spot-checked against the raw file.
- Triage: update to known material (same project; adds CLI, config, integrations, extension APIs).
- Created [[actor-gatherer-docs]].

## [2026-10-22] ingest | ucbepic/actor-gatherer repository
- Snapshotted with add_repo.py (commit 076c26d, MIT, partial snapshot of 177/203 files). A Sonnet reader analysed the code against the blog; key prompts, defaults and quotes were verified by grep.
- Triage: update to known material (implementation detail and code-vs-blog faithfulness).
- Created [[repo-ucbepic-actor-gatherer]] with a Code vs paper table.
- Notable: the evaluation code and baselines are absent. The temporal bias and KV-cache-aware ordering are only partly implemented. The docs table says nothing is turned off for Codex, but the launcher disables Codex auto-compaction.

## [2026-10-22] ingest | Merge: Actor-Gatherer cluster
- Created entities [[actor-gatherer]], [[epic-data-lab]], [[codex]], [[claude-code]], [[pi-coding-agent]], [[opencode]], [[mem0]], [[recursive-language-models]], [[context-language-models]], [[scroll]], [[swe-bench]], [[birdinteract]], [[spider-2]].
- Created concepts [[proactive-context-management]], [[segment-based-context-policy]], [[unknown-unknowns]], [[longitudinal-and-lateral-awareness]], [[context-compaction]], [[tool-based-context-management]], [[kv-cache-aware-context-ordering]], [[environment-change-awareness]], [[multi-agent-context-sharing]].
- Wrote [[overview]] with the three-family framing and a Gaps list. Added a Contradictions section (blog description vs code) to [[segment-based-context-policy]].
- Kept in plain text without pages (passing mentions only): A-MEM, MemGPT, GPT-5.6-Terra, gemini-3.1-pro-preview, the individual authors (single project so far).

## [2026-10-22] ingest | Summary: Actor-Gatherer batch
- 3 raw sources ingested, 25 wiki pages created.
- Needs a human decision: (1) whether to add the baseline papers listed under Gaps in [[overview]]; (2) whether the benchmark entities ([[swe-bench]], [[birdinteract]], [[spider-2]]) should stay or fold into the blog page until a source discusses them directly.

## [2026-10-28] ingest | Is Complex Agentic Memory Always Needed? Naive RAG Is Stronger Than We Thought (arXiv 2610.30755)
- fetched from arxiv.org/pdf/2610.30755 and added with `scripts/add_source.py` (raw/2026-10-28-raw-rag-naive-rag-agentic-memory.pdf); the converted markdown and figures are the `pdf-to-markdown` (Docling 2.144.0) output generated once in a sibling checkout (peterjakus-br/semantic-wiki) and copied here byte for byte next to the identical PDF; read in full apart from the reference list; the main tables were checked against the PDF pages because merged header cells garble some columns; the code repository github.com/Litmeb/RAW-RAG was not ingested
- triage: new material for the memory-systems side of the topic; it also challenges how this wiki's existing claims about memory add-ons ([[mem0]]) and retrieval-based context should be read
- created: [[raw-rag-naive-rag-agentic-memory]]; entities [[raw-rag]], [[locomo]], [[longmemeval]], [[meme-benchmark]], [[memoryagentbench]], [[evermemos]], [[memos]], [[memu]], [[memmachine]], [[memora]], [[emem]], [[simplemem]]; concepts [[retrieval-augmented-memory]], [[evidence-coverage-and-utilization]], [[memory-mutation]], [[reranking]]
- updated: [[mem0]] (write policy, audit, scores), [[proactive-context-management]] (evidence and a contradiction entry), [[unknown-unknowns]], [[context-compaction]], [[actor-gatherer]] (cross-links), [[overview]] (new section 4, evidence, Gaps)
- notable: the paper's retrieval-works result is set against Actor-Gatherer's claim that retrieved summaries are lossy; recorded as an inference-labelled tension, since the tasks, readers and scores differ; the headline "six of seven" omits PersonaMem-v2 (Raw-RAG third of seven, 49.62%, GPT-4.1-mini reader) and Full-context (ahead of Raw-RAG on MEME with DeepSeek-V4-Flash); the comparison was run by the baseline's authors with several baseline scores from other papers; the paper notes Mem0's published LoCoMo overall (66.88) does not match its category scores weighted by question counts (62.14); the same paper is also ingested in peterjakus-br/semantic-wiki with that wiki's schema
- schema note: system entity pages here follow the memory-system rule (what is stored, who selects context, scope, limitations); benchmark entities state "who built it and when" as not stated where the paper gives only a citation
