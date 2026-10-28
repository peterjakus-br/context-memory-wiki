---
title: "EverMemOS"
type: entity
created: 2026-10-28
updated: 2026-10-28
tags: [memory-system]
sources: [raw-rag-naive-rag-agentic-memory]
---
EverMemOS is an agentic memory system that builds organised episodic memories and structured facts from conversation history (Hu et al., cited in [[raw-rag-naive-rag-agentic-memory]] as the source of its published scores and evaluation setting). It is one of the stronger baselines [[raw-rag]] is compared with.

## Facts
- **What is stored**: histories are segmented into coherent units called MemCells, from which episodic representations and atomic facts are extracted; lexical and embedding indices support retrieval; incremental profile extraction was enabled in the paper's runs ([[raw-rag-naive-rag-agentic-memory]])
- **How context is selected**: by the system's own retrieval, which combines lexical and semantic search with query refinement and checks for evidence sufficiency; 10 results by default, presented as subject-episode blocks ([[raw-rag-naive-rag-agentic-memory]])
- **Scope**: one store per conversation; runs locally in the paper's evaluation with extraction concurrency 20 ([[raw-rag-naive-rag-agentic-memory]])
- Scores in the paper: [[locomo]] 86.76 (GPT-4o-mini reader) and 93.05 (GPT-4.1-mini), from its own Qwen3 retrieval setting; [[longmemeval]] 83.00 (GPT-4.1-mini, Qwen3 setting); [[meme-benchmark]] 21.57 (GPT-4o-mini) and 27.24 (DeepSeek-V4-Flash); [[memoryagentbench]] 36.49 and 42.54 on the same two readers; PersonaMem-v2 53.25 (GPT-4.1-mini, profile enabled), the highest of the seven systems compared there ([[raw-rag-naive-rag-agentic-memory]])
- Cost: 8,217.69 s to become ready plus 1,083.79 s of search (9,301.48 s) on 10 MEME episodes and 110 questions with one outer worker, the slowest of the six systems timed; its native evidence on MemoryAgentBench averages 15,394.8 tokens per question, and a 5,000-token cap changes 2,011 of 2,071 questions ([[raw-rag-naive-rag-agentic-memory]])
- Evidence coverage 25.11% and conditional utilization 80.00% on MemoryAgentBench, 47.64% and 76.86% on MEME ([[raw-rag-naive-rag-agentic-memory]])
- **Known limitations** (as measured by the paper): with gold-informed access to its complete store on MEME (GPT-4o-mini reader) it rises from 21.57 to 51.59, still 10.01 points below the raw-evidence control; its exported stores keep no historical versions ([[raw-rag-naive-rag-agentic-memory]])

## Related
- [[raw-rag]] — the baseline compared with
- [[evidence-coverage-and-utilization]] — its coverage and utilization
- [[mem0]], [[memos]], [[memu]], [[memmachine]], [[memora]], [[emem]] — other compared systems
