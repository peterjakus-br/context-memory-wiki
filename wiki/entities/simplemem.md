---
title: "SimpleMem"
type: entity
created: 2026-10-28
updated: 2026-10-28
tags: [memory-system]
sources: [raw-rag-naive-rag-agentic-memory]
---
SimpleMem converts dialogue windows into compact structured memory entries and combines several retrieval channels. [[raw-rag-naive-rag-agentic-memory]] evaluates it directly only on [[locomo]]; its LongMemEval result is a published score.

## Facts
- **What is stored**: structured memory entries with a factual restatement and timestamp, built per conversation from timestamped windows of 40 messages with a two-message overlap (the final partial window included), in a per-conversation LanceDB store ([[raw-rag-naive-rag-agentic-memory]])
- **How context is selected**: by the system's retrieval, which combines semantic, keyword and structured channels (budgets 25, 5 and 5) with planning and up to two reflection rounds; at most 20 entries, in merged native order, go to the reader. The paper caps its evidence at 100,000 tokens ([[raw-rag-naive-rag-agentic-memory]])
- Scores in the paper: [[locomo]] 78.25 (GPT-4o-mini reader) and 83.87 (GPT-4.1-mini), measured in the paper; [[longmemeval]] 76.87 (GPT-4.1-mini), a published result attributed separately ([[raw-rag-naive-rag-agentic-memory]])

## Related
- [[raw-rag]] — the baseline compared with
- [[evermemos]], [[memos]], [[memu]], [[memmachine]], [[memora]], [[emem]], [[mem0]] — other compared systems
