---
title: "MemoryAgentBench"
type: entity
created: 2026-10-28
updated: 2026-10-28
tags: [benchmark, memory]
sources: [raw-rag-naive-rag-agentic-memory]
---
MemoryAgentBench presents a long source context as a sequence of memory-ingestion units followed by many questions over the same context ("ingest once, query many"), across heterogeneous tasks. In [[raw-rag-naive-rag-agentic-memory]] it has the widest task spread and carries the retrieval ablations.

## Facts
- **Capability measured**: four capabilities. Accurate Retrieval (AR): LongMemEval chat history, EventQA, two RULER QA sources. Test-Time Learning (TTL): five in-context classification sources plus ReDial recommendation. Long-Range Understanding (LRU): DetectiveQA and InfBench summarisation. Conflict Resolution (CR): single-hop and multi-hop FactConsolidation, where a larger serial number means newer information ([[raw-rag-naive-rag-agentic-memory]])
- **Task format and size**: 2,071 questions from 14 sources; each source context forms one shared memory store. Undated sources get timestamps that encode source order ([[raw-rag-naive-rag-agentic-memory]])
- **Scoring**: each source's native metric (substring match, numerical-label or choice accuracy, recommendation recall, LLM judge, summary score); Overall is the mean of the four capability scores, with TTL averaging the five classification scores and combining them with ReDial. A flat average over questions would weight sources differently ([[raw-rag-naive-rag-agentic-memory]])
- **Who built it and when**: not stated in the paper beyond a citation ([[raw-rag-naive-rag-agentic-memory]])
- **Known problems** (authors' observations): compression that helps one capability can remove what another needs; the embedded LongMemEval source uses settings separate from the standalone [[longmemeval]]; Full-context results are unavailable because of context length ([[raw-rag-naive-rag-agentic-memory]])
- Scores in the paper: [[raw-rag]] 48.32 (GPT-4o-mini reader) and 53.41 (DeepSeek-V4-Flash), 4.48 to 5.53 points above the strongest compared system ([[memora]] in both). Atomic-fact extraction cut Raw-RAG's TTL from 47.68 to 15.37 and raw-summary augmentation cut CR from 46.00 to 27.00 (GPT-4o-mini) ([[raw-rag-naive-rag-agentic-memory]])
- Used for the coverage and utilization analysis, the reranker, top-k and chunk-size ablations and the 5,000-token cross-system budget control; see [[evidence-coverage-and-utilization]] ([[raw-rag-naive-rag-agentic-memory]])

## Related
- [[locomo]], [[longmemeval]], [[meme-benchmark]] — the other benchmarks in the same comparison
- [[raw-rag]] — the baseline evaluated on it
