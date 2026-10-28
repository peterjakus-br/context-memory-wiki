---
title: "MEME benchmark"
type: entity
created: 2026-10-28
updated: 2026-10-28
tags: [benchmark, memory, dynamic-state]
sources: [raw-rag-naive-rag-agentic-memory]
---
MEME is a benchmark of chronological episodes (personal-life and software-project domains) with evidence sessions, distractor sessions, fictitious entity values and explicit dependency rules, and questions asked before and after a designated change. It targets dynamic memory: updates, deletions and dependent state changes. [[raw-rag-naive-rag-agentic-memory]] runs most of its diagnostics on it.

## Facts
- **Capability measured**: six task types. Exact Recall (ER) reproduces a stable value; Aggregation (Agg) collects several entities' values from distributed evidence; Tracking (Tr) reconstructs an entity's value history in order; Deletion (Del) acknowledges a removal without revealing the deleted value; Cascade (Cas) applies a stated conditional rule after an upstream change, over one or two hops; Absence (Abs) recognises that a dependent old value is no longer trustworthy when no replacement is supplied. Fictitious values reduce the use of parametric knowledge ([[raw-rag-naive-rag-agentic-memory]])
- **Task format and size**: the paper uses the condition with 32k tokens of distractors: 100 episodes and 1,188 phase-specific questions (494 before-phase, 694 after-phase) ([[raw-rag-naive-rag-agentic-memory]])
- **Scoring**: task-specific checks on after-phase answers; for Cas, Abs and Del credit also needs the before-phase answer to be right; Overall is the six-task macro-average. Del scoring does not require physical erasure from storage ([[raw-rag-naive-rag-agentic-memory]])
- **Who built it and when**: not stated in the paper beyond a citation ([[raw-rag-naive-rag-agentic-memory]])
- **Known problems**: on Abs, missing evidence can elicit an "uncertain" answer that earns credit, so a correct answer does not prove the dependency was reconstructed; scores depend strongly on the reader (GPT-4o-mini scores 1.83% on cascades when given the evidence directly, DeepSeek-V4-Flash 82.32%) ([[raw-rag-naive-rag-agentic-memory]])
- Scores in the paper: [[raw-rag]] 39.30 (GPT-4o-mini reader) and 43.19 (DeepSeek-V4-Flash); Full-context 29.31 and 63.17; the source-evidence oracle (readers receive the phase-visible evidence in order) scores 50.50 (GPT-4o-mini), 85.48 (DeepSeek-V4-Flash) and 70.25 (Qwen3.5-35B-A3B). Cascades are near zero for GPT-4o-mini readers in every memory system (Raw-RAG 4.27) ([[raw-rag-naive-rag-agentic-memory]])
- Used for the path-coverage diagnostic (62.34% for Raw-RAG, GPT-4o-mini), the complete-store oracle, and a latency comparison on 10 episodes and 110 questions; see [[evidence-coverage-and-utilization]] ([[raw-rag-naive-rag-agentic-memory]])

## Related
- [[locomo]], [[longmemeval]], [[memoryagentbench]] — the other benchmarks in the same comparison
- [[raw-rag]] — the baseline evaluated on it
- [[memory-mutation]] — the update and deletion behaviour MEME probes
