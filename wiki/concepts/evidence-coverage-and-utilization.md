---
title: "Evidence coverage and utilization"
type: concept
created: 2026-10-28
updated: 2026-10-28
tags: [evaluation, memory, retrieval]
sources: [raw-rag-naive-rag-agentic-memory]
confidence: low
---
A two-factor decomposition of memory-augmented question answering. Coverage is the fraction of questions whose retrieved context contains sufficient evidence to derive the answer; utilization is the answer accuracy among those questions. It separates "did the system surface the evidence" from "did the reader use it", which a single accuracy score hides. A third measure, conditional path coverage, asks whether answer values arrive together with the relations needed to use them. One source so far.

## What the sources say
- Definitions: coverage is the mean of per-question sufficiency labels; utilization is the answer score summed over sufficient questions divided by the number of sufficient questions. Correct answers outside the sufficient set can reflect label errors, partial evidence, prior knowledge or guessing ([[raw-rag-naive-rag-agentic-memory]])
- Sufficiency is judged by an LLM (DeepSeek-V4-Flash, temperature zero) on [[memoryagentbench]], using an excerpt of the context built around literal matches of the reference answer values, and by task-specific deterministic checks on [[meme-benchmark]] ([[raw-rag-naive-rag-agentic-memory]])
- Systems differ more in coverage than in utilization: on MemoryAgentBench (GPT-4o-mini reader) coverage runs from 19.07% ([[memu]]) to 45.29% ([[raw-rag]]) while utilization only from 80.00% to 89.71%; on MEME the spreads are 40.66 and 21.04 percentage points ([[raw-rag-naive-rag-agentic-memory]])
- Omnibus tests reject equality in all four cases; after Holm correction 20 of 21 system pairs differ in MemoryAgentBench coverage against 7 of 21 in utilization, and 19 against 17 on MEME ([[raw-rag-naive-rag-agentic-memory]])
- [[raw-rag]] has the highest coverage on both (45.29% and 76.35%) but not the highest utilization (84.43% and 73.76%); higher coverage offsets lower utilization ([[raw-rag-naive-rag-agentic-memory]])
- Conditional path coverage on MEME tracking and cascade after-state questions (GPT-4o-mini): Raw-RAG 62.34%, [[memmachine]] 56.70%, [[evermemos]] 50.00%, [[emem]] 49.50%, [[mem0]] 47.66%, [[memos]] 24.03%, [[memu]] 9.62%. Systems that retrieve answer values can still differ greatly in keeping the supporting relations ([[raw-rag-naive-rag-agentic-memory]])
- The authors caution that system-specific question sets preclude a controlled comparison of readers, and that the labels are conditional on the store builds and the judge ([[raw-rag-naive-rag-agentic-memory]])

## Related
- [[unknown-unknowns]] — a coverage failure the agent cannot notice (inference: coverage misses are the cases where needed information is never surfaced; the paper does not discuss agents that fail to ask)
- [[retrieval-augmented-memory]] — where the decomposition is applied
- [[raw-rag]] — the system whose result it explains
