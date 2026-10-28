---
title: "Mem0"
type: entity
created: 2026-10-22
updated: 2026-10-28
tags: [memory-system]
sources: [actor-gatherer-framework-blog, raw-rag-naive-rag-agentic-memory]
---
Mem0 is a long-term memory layer for agents (Chhikara et al., "Mem0: Building
Production-Ready AI Agents with Scalable Long-Term Memory", arXiv:2504.19413,
2025). It appears in this wiki as the memory baseline in
[[actor-gatherer-framework-blog]] and as an audited and compared system in
[[raw-rag-naive-rag-agentic-memory]].

## Facts
- **What is stored**: summaries of the past ("memories"). **How context is
  selected**: retrieved, e.g. through embedding similarity, based on the user
  task, and appended to the harness context ([[actor-gatherer-framework-blog]]).
- Limitation, per the blog: "Such summaries are still lossy, and
  embedding-based retrieval can be inaccurate". Failures occur "when it either
  does not retrieve the relevant information or the relevant information is
  not included in its memories at all" ([[actor-gatherer-framework-blog]]).
- Mem0-Codex scores 59% average single-agent accuracy, the second best after
  AG-Codex's 91% (agent model gemini-3.1-pro-preview, authors' benchmarks).
  It sometimes recovers the specification that Codex loses in compaction
  ([[actor-gatherer-framework-blog]]).
- **How writes work** (classic Mem0, version 1.0.11 in the paper's audit): it extracts candidate facts, retrieves related existing memories and chooses ADD, UPDATE, DELETE or NONE; the default evaluation setup keeps separate perspectives for two named speakers (retrieval top 20 per identity, then temporal filtering) and uses one context-scoped identity on MemoryAgentBench ([[raw-rag-naive-rag-agentic-memory]])
- Audit: UPDATE plus DELETE were 4.39% of 33,902 write decisions on [[locomo]] and 2.46% of 428,858 on [[longmemeval]]; effective mutations 1.90% and 1.34%. With UPDATE turned into ADD and DELETE into NONE its LoCoMo accuracy rose from 67.36% to 69.42%; see [[memory-mutation]] ([[raw-rag-naive-rag-agentic-memory]])
- Scores in the paper's comparison: LoCoMo 66.88 (GPT-4o-mini reader, published figure retained; the paper notes its published category scores weight to 62.14) and 64.20 (GPT-4.1-mini); LongMemEval 66.40 (GPT-4.1-mini); [[meme-benchmark]] 27.76 (GPT-4o-mini) and 33.16 (DeepSeek-V4-Flash); [[memoryagentbench]] 41.28 and 41.95 on the same readers; PersonaMem-v2 43.85 (GPT-4.1-mini, no persona profile). These are not comparable with the 59% in [[actor-gatherer-framework-blog]], which uses different tasks and an agent model ([[raw-rag-naive-rag-agentic-memory]])
- In the Mem0 paper's own comparison, its RAG baseline (256-token chunks, top 2) scored 60.97 on LoCoMo with GPT-4o-mini; the review in [[raw-rag-naive-rag-agentic-memory]] flags top-k of at most 2 as under-tuned
- With gold-informed access to its complete store on MEME (GPT-4o-mini reader) it improved least of seven systems, from 27.76 to 32.26, leaving it 29.34 points below the raw-evidence control; its coverage was 40.03% on MemoryAgentBench and 63.22% on MEME ([[raw-rag-naive-rag-agentic-memory]])
- The paper's general runs and MEME store use Mem0 2.0.11, a different version from the 1.0.11 audited ([[raw-rag-naive-rag-agentic-memory]])

## Related
- [[context-compaction]] — Mem0 complements a compaction harness
- [[actor-gatherer]] — compared against it
- [[raw-rag]] — raw-history baseline it is compared with
- [[memory-mutation]] — the write-side behaviour audited
- [[retrieval-augmented-memory]] — the approach it belongs to
