---
title: "Reranking"
type: concept
created: 2026-10-28
updated: 2026-10-28
tags: [retrieval, memory]
sources: [raw-rag-naive-rag-agentic-memory]
confidence: low
---
Reranking is a second retrieval stage that re-scores a first-stage candidate set (typically from dense or lexical search) with a more expensive model, most often a cross-encoder that reads the question and each candidate passage together, and keeps only the best few for the reader. It trades extra computation per query for precision. One source so far.

## What the sources say
- In [[raw-rag]], dense retrieval takes 128 candidate windows and a cross-encoder keeps 15. Removing the reranker lowers the [[memoryagentbench]] total by 3.92 points (GPT-4o-mini reader; Holm-adjusted p = 0.0012; 95% interval -5.80 to -2.06) ([[raw-rag-naive-rag-agentic-memory]])
- The Qwen3-Reranker-4B variant is prompted with a yes/no relevance instruction ("determine if the passage contains information relevant to answering the question"); the other setting uses Cohere Rerank-v3.5 ([[raw-rag-naive-rag-agentic-memory]])
- Appendix E names absent reranking, alongside too-large chunks and too-low top-k, as a weakness of several prior RAG baselines (for example xMemory's raw baseline), and calls cross-encoder reranking over a broad dense candidate pool the missing control in evaluations that already tune chunk size and top-k ([[raw-rag-naive-rag-agentic-memory]])
- Final k from 5 to 60 stays within 1.3 points of the default 15 on MemoryAgentBench, while k of 1 loses 11.73 points and k of 120 loses 14.57 ([[raw-rag-naive-rag-agentic-memory]])
- Among the compared systems, [[memos]] also reranks (its fine search mode uses reranking and maximal-marginal-relevance deduplication) ([[raw-rag-naive-rag-agentic-memory]])

## Related
- [[retrieval-augmented-memory]] — the pipeline reranking sits in
- [[raw-rag]] — the baseline built around it
