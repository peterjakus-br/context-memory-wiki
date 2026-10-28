---
title: "LongMemEval"
type: entity
created: 2026-10-28
updated: 2026-10-28
tags: [benchmark, memory, conversation]
sources: [raw-rag-naive-rag-agentic-memory]
---
LongMemEval is a long-term chat-memory benchmark in which each example pairs a user–assistant question and question date with its own dated collection of historical sessions, relevant and distractor alike. [[raw-rag-naive-rag-agentic-memory]] uses the standalone LongMemEval-S evaluation (500 examples) and, separately, the LongMemEval source embedded in [[memoryagentbench]].

## Facts
- **Capability measured**: telling user knowledge from assistant knowledge, recovering stated preferences, integrating evidence across sessions, resolving superseded facts and abstaining when the history lacks support. The question date is the reference time for phrases such as "current" or "last month" ([[raw-rag-naive-rag-agentic-memory]])
- **Task format and size**: 500 examples, each with an isolated history. Six question types: single-session-user, single-session-assistant, single-session-preference, multi-session, knowledge-update and temporal-reasoning; abstention items form an extra condition. Some published scores use the 470 answerable (non-abstention) questions ([[raw-rag-naive-rag-agentic-memory]])
- **Scoring**: LLM-judged accuracy, question-weighted; the paper averages three GPT-4o-mini judgments per answer in the settings it matches to other papers ([[raw-rag-naive-rag-agentic-memory]])
- **Who built it and when**: not stated in the paper beyond a citation ([[raw-rag-naive-rag-agentic-memory]])
- **Known problems**: the embedded LongMemEval source in [[memoryagentbench]] uses separate settings and scores from the standalone benchmark; published baselines under different retrievers and judges are not directly comparable, so the paper reports matched-setting tables ([[raw-rag-naive-rag-agentic-memory]])
- Scores in the paper (GPT-4.1-mini reader): [[raw-rag]] 87.53 against Memora's 87.40 (text-embedding-3-small setting, the narrowest lead at 0.13 points); 89.93 against EverMemOS's 83.00 in the Qwen3 setting; Full-context 65.60 ([[raw-rag-naive-rag-agentic-memory]])
- The paper's audit of [[mem0]] over all 500 examples found 428,858 write decisions, 2.46% of them UPDATE or DELETE ([[raw-rag-naive-rag-agentic-memory]])

## Related
- [[locomo]], [[meme-benchmark]], [[memoryagentbench]] — the other benchmarks in the same comparison
- [[raw-rag]] — the baseline evaluated on it
