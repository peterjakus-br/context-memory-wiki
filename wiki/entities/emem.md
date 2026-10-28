---
title: "EMem"
type: entity
created: 2026-10-28
updated: 2026-10-28
tags: [memory-system]
sources: [raw-rag-naive-rag-agentic-memory]
---
EMem is a long-term conversational memory built from extracted elementary discourse units (EDUs); EMem-G is its graph variant (Zhou and Han, "A simple yet strong baseline for long-term conversational memory of LLM agents", arXiv:2511.17208, 2025, as cited in [[raw-rag-naive-rag-agentic-memory]]).

## Facts
- **What is stored**: EDUs extracted by contextual extraction without a further context-generation step, keeping session and turn structure; where question dates define different visible histories it can build separate stores from history prefixes ([[raw-rag-naive-rag-agentic-memory]])
- **How context is selected**: retrieval without personalised PageRank for EMem and with it for EMem-G; the default QA budget is 10 units, overridden to 20 for MEME and MemoryAgentBench; for in-context-learning tasks it also prepends up to five raw demonstration chunks chosen by lexical overlap ([[raw-rag-naive-rag-agentic-memory]])
- Scores in the paper: [[locomo]] 78.00 (GPT-4o-mini reader) and 84.20 (GPT-4.1-mini); [[longmemeval]] 83.00 (GPT-4.1-mini, the 470 non-abstention questions) and 84.90 for EMem-G; [[meme-benchmark]] 33.84 (GPT-4o-mini) and 38.41 (DeepSeek-V4-Flash); [[memoryagentbench]] 38.44 and 39.59 on the same readers ([[raw-rag-naive-rag-agentic-memory]])
- Category wins: it scores above [[raw-rag]] on LongMemEval multi-session questions (82.10) and on MEME aggregation (36.00, GPT-4o-mini), deletion and cascade questions even though Raw-RAG's overall scores are higher ([[raw-rag-naive-rag-agentic-memory]])
- Evidence coverage 34.72% on MemoryAgentBench and 50.08% on MEME; utilization 89.71% and 86.55%, the highest utilization on both ([[raw-rag-naive-rag-agentic-memory]])
- Cost: the fastest of the five systems timed apart from Raw-RAG, 1,561.97 s add-to-ready plus search on 10 MEME episodes and 110 questions ([[raw-rag-naive-rag-agentic-memory]])

## Related
- [[raw-rag]] — the baseline compared with
- [[evidence-coverage-and-utilization]] — its high utilization
- [[evermemos]], [[memos]], [[memu]], [[memmachine]], [[memora]], [[mem0]] — other compared systems
