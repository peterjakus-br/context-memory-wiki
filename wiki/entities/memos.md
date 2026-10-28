---
title: "MemOS"
type: entity
created: 2026-10-28
updated: 2026-10-28
tags: [memory-system]
sources: [raw-rag-naive-rag-agentic-memory]
---
MemOS manages extracted text memories and preference information within a memory-operating-system abstraction. It is a compared system in [[raw-rag-naive-rag-agentic-memory]].

## Facts
- **What is stored**: memories extracted by MemOS itself (the paper uses its fine-grained extraction setting rather than the default fast mode, to exercise its memory management), including preference, tool and skill memories ([[raw-rag-naive-rag-agentic-memory]])
- **How context is selected**: by the system's retrieval: top 20 text memories and preferences with fine search, reranking and maximal-marginal-relevance deduplication. For two named speakers it writes and searches separate speaker perspectives and gives the reader both; on MemoryAgentBench it uses a context-scoped identity, and for in-context-learning sources the reader also receives up to five original label-mapping chunks chosen by lexical overlap ([[raw-rag-naive-rag-agentic-memory]])
- **Scope and integrations**: locally hosted MemOS 2.0.23 per the paper, on Qdrant 1.15.3 and Neo4j ([[raw-rag-naive-rag-agentic-memory]])
- Scores in the paper: [[locomo]] 75.80 (GPT-4o-mini reader) and 80.76 (GPT-4.1-mini); [[longmemeval]] 77.80 (GPT-4.1-mini); [[meme-benchmark]] 30.24 (GPT-4o-mini) and 31.23 (DeepSeek-V4-Flash); [[memoryagentbench]] 35.72 and 37.47 on the same readers; PersonaMem-v2 50.72 (GPT-4.1-mini, profile enabled) ([[raw-rag-naive-rag-agentic-memory]])
- Cost: 2,769.56 s add-to-ready plus search on 10 MEME episodes and 110 questions, one outer worker ([[raw-rag-naive-rag-agentic-memory]])
- Evidence coverage 34.48% and utilization 85.85% on MemoryAgentBench, 62.12% and 66.67% on MEME ([[raw-rag-naive-rag-agentic-memory]])
- **Known limitations** (as measured by the paper): conditional path coverage on MEME tracking and cascade questions is 24.03%; gold-informed access to its complete store lifts it from 30.24 to 45.12 (GPT-4o-mini), still 16.48 points below raw evidence ([[raw-rag-naive-rag-agentic-memory]])

## Related
- [[raw-rag]] — the baseline compared with
- [[evermemos]], [[memu]], [[memmachine]], [[memora]], [[emem]], [[mem0]] — other compared systems
