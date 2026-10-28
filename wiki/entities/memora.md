---
title: "Memora"
type: entity
created: 2026-10-28
updated: 2026-10-28
tags: [memory-system]
sources: [raw-rag-naive-rag-agentic-memory]
---
Memora separates stored memory values from indexed primary abstractions and cue anchors, linking compact retrieval representations to more specific factual and episodic content. In [[raw-rag-naive-rag-agentic-memory]] it is the strongest compared system on [[longmemeval]] and [[memoryagentbench]].

## Facts
- **What is stored**: memory values plus indexed abstractions and cue anchors; messages are grouped by session and segmented (by an LLM) before extraction, with source attribution kept. Each conversation has an isolated Chroma store ([[raw-rag-naive-rag-agentic-memory]])
- **How context is selected**: a prompted-policy retriever that takes at most five steps, with cue indexing, BM25 hybrid search and episodic memory enabled, returning the top 20 before temporal processing. For each factual memory the reader receives its value and history together with linked episodic memories; the answer context has a separate 100,000-token cap ([[raw-rag-naive-rag-agentic-memory]])
- Scores in the paper: [[locomo]] 80.61 (GPT-4o-mini reader) and 86.30 (GPT-4.1-mini); [[longmemeval]] 87.40 (GPT-4.1-mini), 0.13 points below [[raw-rag]]; [[meme-benchmark]] 33.52 (GPT-4o-mini) and 36.36 (DeepSeek-V4-Flash); [[memoryagentbench]] 43.84 and 47.88 on the same readers. The GPT-4.1-mini LoCoMo and LongMemEval entries use Memora's published policy-retriever results, not a rerun ([[raw-rag-naive-rag-agentic-memory]])
- **Cost**: the slowest ingestion on a roughly one-million-token, 1,710-message conversation: 26.95 hours cumulative add time against 0.33 hours for Raw-RAG ([[raw-rag-naive-rag-agentic-memory]])

## Related
- [[raw-rag]] — the baseline compared with
- [[evermemos]], [[memos]], [[memu]], [[memmachine]], [[emem]], [[mem0]] — other compared systems
