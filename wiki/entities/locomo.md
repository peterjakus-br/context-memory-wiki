---
title: "LoCoMo"
type: entity
created: 2026-10-28
updated: 2026-10-28
tags: [benchmark, memory, conversation]
sources: [raw-rag-naive-rag-agentic-memory]
---
LoCoMo is a long-term conversation benchmark: long, multi-session dialogues between two named speakers, each followed by free-form questions about the history. In this wiki it is one of the four benchmarks on which [[raw-rag-naive-rag-agentic-memory]] compares memory systems, and many baseline scores there are taken from other papers rather than rerun.

## Facts
- **Capability measured**: finding sparse evidence in a long, personally grounded history while keeping speaker attribution, names and time references. Single-hop questions need precise recovery of a fact; multi-hop questions combine facts across turns or sessions; temporal questions anchor relative dates and order events; open-domain questions connect the conversation with broader knowledge ([[raw-rag-naive-rag-agentic-memory]])
- **Task format and size**: the 10-conversation release, 1,540 questions after excluding adversarial category 5: single-hop (category 4, 841 questions), multi-hop (category 1, 282), temporal (category 2, 321), open-domain (category 3, 96). Sessions carry dates; images appear as supplied captions; all questions of a conversation share one memory store ([[raw-rag-naive-rag-agentic-memory]])
- **Scoring**: in the paper, an LLM judge (GPT-4o-mini, temperature zero, three judgments per answer) with a deliberately generous prompt: "as long as it touches on the same topic as the gold answer, it should be counted as CORRECT". Published baselines use different judge and lexical-metric conventions (judge accuracy, token F1, BLEU-1), which the paper keeps separate ([[raw-rag-naive-rag-agentic-memory]])
- **Who built it and when**: not stated in the paper beyond a citation ([[raw-rag-naive-rag-agentic-memory]])
- **Known problems**: the paper's historical judge records contain only binary scores, so a zero cannot be told apart from a format or request failure (252 to 505 zero-scores out of 4,620 judgments per Raw-RAG condition); Mem0's published GPT-4o-mini category scores weight to 62.14 rather than the published overall 66.88; and scores from different papers use different retrievers, readers and judges ([[raw-rag-naive-rag-agentic-memory]])
- Scores in the paper: [[raw-rag]] 89.07 (GPT-4o-mini reader) and 93.70 (GPT-4.1-mini), against [[memmachine]] 88.12 and [[evermemos]] 93.05, whose score comes from its own Qwen3 retrieval setting; Full-context 72.30 and 80.60 ([[raw-rag-naive-rag-agentic-memory]])
- The paper's audit of [[mem0]] over all LoCoMo conversations found 33,902 write decisions, 4.39% of them UPDATE or DELETE; see [[memory-mutation]] ([[raw-rag-naive-rag-agentic-memory]])

## Related
- [[longmemeval]], [[meme-benchmark]], [[memoryagentbench]] — the other benchmarks in the same comparison
- [[raw-rag]] — the baseline evaluated on it
