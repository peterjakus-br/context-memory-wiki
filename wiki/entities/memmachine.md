---
title: "MemMachine"
type: entity
created: 2026-10-28
updated: 2026-10-28
tags: [memory-system]
sources: [raw-rag-naive-rag-agentic-memory]
---
MemMachine combines source-grounded episodic memory with extracted semantic memory. In [[raw-rag-naive-rag-agentic-memory]] it is the closest competitor to [[raw-rag]], the one system whose store keeps raw conversational content besides Raw-RAG itself.

## Facts
- **What is stored**: episodic memory that keeps source episodes, plus semantic memory (extracted features) and episode summaries; each conversation has an isolated store with both types enabled. Semantic extraction can continue after message ingestion, so "ingestion complete" and "ready for retrieval" are different timing points ([[raw-rag-naive-rag-agentic-memory]])
- **How context is selected**: by the system's retrieval (MemMachine 0.3.4, default configuration): episodes, episode summaries and semantic features appear in separate context sections with independent top-20 budgets. Episodic candidates are date-filtered but undated semantic features bypass the filter, so the date cutoff does not establish temporal validity for semantic evidence ([[raw-rag-naive-rag-agentic-memory]])
- **Integrations**: PostgreSQL 16 with pgvector and Neo4j 5.23 Community; model access through OpenRouter ([[raw-rag-naive-rag-agentic-memory]])
- Scores in the paper: [[locomo]] 88.12 (GPT-4o-mini reader) and 91.69 (GPT-4.1-mini); [[longmemeval]] 74.33 (GPT-4.1-mini); [[meme-benchmark]] 37.06 (GPT-4o-mini) and 44.71 (DeepSeek-V4-Flash), where it beats [[raw-rag]] by 1.52 points; [[memoryagentbench]] 35.53 and 42.05 on the same readers ([[raw-rag-naive-rag-agentic-memory]])
- Evidence coverage 21.54% on MemoryAgentBench and 70.37% on MEME, with utilization 84.30% and 82.66% (the highest MEME utilization of the seven systems); conditional path coverage on MEME 56.70%, second to Raw-RAG ([[raw-rag-naive-rag-agentic-memory]])
- With gold-informed access to its complete store on MEME (GPT-4o-mini reader) it reaches 57.46 against 61.60 for raw evidence ([[raw-rag-naive-rag-agentic-memory]])
- **Cost and evidence length**: 3,515.74 s add-to-ready plus search on 10 MEME episodes and 110 questions with one outer worker; native evidence on MemoryAgentBench averages 26,296.9 tokens per question, so a 5,000-token cap changes 2,030 of 2,071 questions and lowers its score by 3.89 points (GPT-4o-mini) ([[raw-rag-naive-rag-agentic-memory]])

## Related
- [[raw-rag]] — the baseline compared with
- [[evidence-coverage-and-utilization]] — coverage and path coverage
- [[evermemos]], [[memos]], [[memu]], [[memora]], [[emem]], [[mem0]] — other compared systems
