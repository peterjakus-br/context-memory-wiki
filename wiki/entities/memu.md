---
title: "MemU"
type: entity
created: 2026-10-28
updated: 2026-10-28
tags: [memory-system]
sources: [raw-rag-naive-rag-agentic-memory]
---
MemU extracts profile, event, knowledge and behaviour items from interaction resources. It is the weakest of the compared systems in most settings of [[raw-rag-naive-rag-agentic-memory]].

## Facts
- **What is stored**: extracted items and summaries; each conversation is treated as one user's history, ingested in order, with items linked to category summaries. The paper's complete-store export contains item summaries and non-empty category summaries but no original resource text ([[raw-rag-naive-rag-agentic-memory]])
- **How context is selected**: by the system's retrieval within one conversation, with intention routing and evidence-sufficiency checks; the final result cap is 20 by default and 10 on MemoryAgentBench (MemU 1.5.1, default configuration) ([[raw-rag-naive-rag-agentic-memory]])
- **Integrations**: PostgreSQL with pgvector; in the paper's runs a GPU item index gives exact cosine similarity ([[raw-rag-naive-rag-agentic-memory]])
- Scores in the paper: [[locomo]] 61.15 (GPT-4o-mini reader) and 66.67 (GPT-4.1-mini); [[longmemeval]] 38.40 (GPT-4.1-mini); [[meme-benchmark]] 19.87 (GPT-4o-mini) and 18.80 (DeepSeek-V4-Flash); [[memoryagentbench]] 26.12 and 28.27 on the same readers; PersonaMem-v2 38.70 (GPT-4.1-mini, profile enabled) ([[raw-rag-naive-rag-agentic-memory]])
- Evidence coverage 19.07% on MemoryAgentBench and 35.69% on MEME; utilization 89.37% and 84.20%, so its weakness is surfacing evidence, not using it ([[raw-rag-naive-rag-agentic-memory]])
- **Known limitations** (as measured by the paper): conditional path coverage on MEME tracking and cascade questions is 9.62%, the lowest of seven systems; with gold-informed access to its complete store it reaches only 31.07 on MEME (GPT-4o-mini), 30.54 points below raw evidence ([[raw-rag-naive-rag-agentic-memory]])

## Related
- [[raw-rag]] — the baseline compared with
- [[evidence-coverage-and-utilization]] — coverage versus utilization
- [[evermemos]], [[memos]], [[memmachine]], [[memora]], [[emem]], [[mem0]] — other compared systems
