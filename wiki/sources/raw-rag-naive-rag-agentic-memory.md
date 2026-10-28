---
title: "Is Complex Agentic Memory Always Needed? Naive RAG Is Stronger Than We Thought"
type: source
created: 2026-10-28
updated: 2026-10-28
tags: [agent-memory, rag, reranking, evaluation, benchmark, arxiv-preprint]
source: raw/2026-10-28-raw-rag-naive-rag-agentic-memory.pdf
---

## Summary
Preprint (arXiv 2610.30755v1 [cs.AI], 22 Oct 2026, no venue stated) by Zhengye Bao, Shengtao Zhang, Haokai Zhang, Shiqi Lou, Muning Wen and Minnan Luo (Luo Lab Undergraduate Division at Xi'an Jiaotong University; Shanghai Jiao Tong University; Zhejiang University; The Chinese University of Hong Kong). It asks whether the complexity of agentic memory systems (mutation, structural organisation, learned retrieval) is always necessary for long-term conversation understanding. Its test is [[raw-rag]], a naive RAG baseline: dense retrieval plus cross-encoder reranking over raw conversation history, with no LLM-based extraction, summarisation, graph construction or mutation. Raw-RAG ranks first among the compared memory systems in six of seven benchmark–model settings on [[locomo]], [[longmemeval]], [[meme-benchmark]] and [[memoryagentbench]], and diagnostic experiments point to evidence access and preserved raw information as the reasons. The title page links code at github.com/Litmeb/RAW-RAG; that repository has not been ingested.

## Key points
- Two objections to RAG for long-term memory motivate the study: a conceptual one (RAG suits static corpora, but conversations contain superseded facts, deletions and dependent state changes) and an empirical one (prior evaluations report RAG trailing agentic memory systems).
- Preliminary audit of Mem0 on all LoCoMo conversations and all 500 LongMemEval examples: UPDATE and DELETE are 4.39% of 33,902 write decisions on LoCoMo and 2.46% of 428,858 on LongMemEval; effective mutations (persisted text-changing updates or deletions) are 1.90% and 1.34%. Many proposed updates are duplicates or malformed. Replacing UPDATE with ADD and DELETE with NONE raises Mem0's LoCoMo accuracy from 67.36% to 69.42% with no category reduced (Table 1).
- Source-evidence oracle on MEME: readers given the phase-visible evidence in chronological order score 50.50% (GPT-4o-mini), 85.48% (DeepSeek-V4-Flash) and 70.25% (Qwen3.5-35B-A3B) overall; DeepSeek-V4-Flash reaches 82.32% on cascades and 91.54% on invalidation. The authors conclude that capable readers can often resolve changing state from sufficient raw evidence, while reader quality varies widely (GPT-4o-mini scores 1.83% on cascades).
- Raw-RAG design: each conversation is serialised with timestamps and image captions, split into 256-token windows with 32-token overlap and embedded in a flat index. At query time the question retrieves the 128 nearest windows by cosine similarity, a cross-encoder reranks them, and the top 15 go to the reader, expanded to complete source turns on LoCoMo, LongMemEval and MEME (turn expansion is disabled on MemoryAgentBench). The retrieval query is the original question.
- Main results (excluding Full-context): Raw-RAG leads LoCoMo by 0.65–0.95 points, LongMemEval by 0.13, GPT-4o-mini MEME by 2.24 and MemoryAgentBench by 4.48–5.53 points. Examples: LoCoMo overall 89.07 (GPT-4o-mini) and 93.70 (GPT-4.1-mini) against MemMachine 88.12 and EverMemOS 93.05; LongMemEval 87.53 against Memora 87.40; MemoryAgentBench 48.32 (GPT-4o-mini) and 53.41 (DeepSeek-V4-Flash).
- The one lost setting is DeepSeek-V4-Flash on MEME: MemMachine leads Raw-RAG among memory systems by 1.52 points (44.71 vs 43.19), and Full-context leads Raw-RAG by 19.98 points (63.17). Elsewhere Full-context trails Raw-RAG where it has a score (for example GPT-4o-mini MEME 29.31 against 39.30, and LoCoMo 72.30 against 89.07), and it is unavailable on MemoryAgentBench because of context length.
- Supplementary PersonaMem-v2 (5,000 multiple-choice questions, 32k histories, GPT-4.1-mini): Raw-RAG scores 49.62%, third of seven behind EverMemOS (53.25) and MemOS (50.72), without leading any scenario. Raw-RAG uses no persona profile; EverMemOS, MemOS, MemU and MemoryOS use theirs. The authors state significance is untested. This setting is outside the seven counted in the headline claim.
- RQ1, why this design (MemoryAgentBench, paired bootstrap with Holm correction): removing the reranker costs 3.92 points (p = 0.0012); final k of 1 costs 11.73 points and k of 120 costs 14.57; k of 5, 10, 30 and 60 stay within 1.3 points; chunk sizes 128 to 1,024 tokens make no significant difference.
- RQ2, can memory management help: three variants (atomic-fact extraction, raw summary augmentation, graph-expanded raw windows) reuse the same chunking, embedder and reranker. None beats Raw-RAG's 48.32: atomic facts 28.70 (test-time learning falls from 47.68 to 15.37), raw summary 42.51 (conflict resolution 46.00 to 27.00), graph expansion 42.54. Display-turn deduplication also lowers Total, to 45.93.
- RQ3, cost: the three variants need 21.6–109.3M LLM tokens and 2.9–8.8 hours for Add plus Search on 11 MemoryAgentBench sources, against 12 minutes for Raw-RAG with no LLM calls. On a 10-episode, 110-question MEME slice, Raw-RAG finishes Add-to-ready plus Search in 305.91 s, 5.1× faster than the next system (EMem, 1,561.97 s) and 30.4× faster than EverMemOS (9,301.48 s). Streaming a 1,710-message BEAM conversation of about one million tokens, cumulative Add time ranges from 0.33 hours for Raw-RAG to 26.95 hours for Memora; MemOS, the next-fastest completed run, takes 3.25 hours. Timings come from one local machine with API-based models and exclude answer generation.
- Coverage versus utilization (Finding 1): Raw-RAG supplies sufficient evidence most often (MemoryAgentBench 45.29%, MEME 76.35%) while its conditional accuracy given sufficient evidence is not the highest (84.43% and 73.76%). Across systems coverage spans 19.07–45.29% on MemoryAgentBench but utilization only 80.00–89.71%; on MEME the spreads are 40.66 and 21.04 points. See [[evidence-coverage-and-utilization]].
- Path preservation (Finding 2): on MEME tracking and cascade after-state questions, among questions whose answer values were retrieved, Raw-RAG's retrieved context also holds a complete supporting path 62.34% of the time, against MemMachine 56.70% and MemU 9.62%.
- Complete-store oracle (Finding 3): with gold-informed selection over each system's exported stores and a 5,000-token budget, all seven systems improve over native retrieval, but stay below the raw-evidence control of 61.60%. Raw-RAG reaches 57.54% and MemMachine 57.46% (both keep raw conversational content); EverMemOS 51.59, MemOS 45.12, Mem0 32.26, MemU 31.07. Removing the packing cap leaves all seven stores 7.58–29.38 points below raw evidence. The authors caution that the gap is not a pure measure of ingestion loss (selection, packing and lost-in-the-middle effects also contribute) and that MEME Abs answers can earn credit by saying "uncertain" when evidence is missing.
- Budget controls: under a 5,000-token evidence cap, Raw-RAG stays ahead on MemoryAgentBench (48.32, unchanged, against 44.74 for the strongest capped baseline), and its own capped scores are 89.42 (LoCoMo), 89.20 (LongMemEval) and 38.21 (MEME). Appendix A.4 notes the capped Raw-RAG still trails EMem on LongMemEval multi-session questions and on MEME aggregation, deletion and cascade.
- Review of 14 prior RAG evaluations (Appendix E, Table 34): several baselines use chunks that are too large (Nemori 4,096 tokens; RecMem about 2,048), top-k that is too low (Mem0 k of 1 or 2; Memobase k of 1; Memora k of 3; BEAM k of 5), or no reranker (xMemory). The authors label these as their own assessments, not controlled reruns, and say quantifying their effect needs controlled reruns.
- Limitations stated: offline conversation on public benchmarks only; no claim about interactive, multimodal or operational settings (exposing authoritative state to tools, triggering actions, erasing stored information); raw storage grows with history and raises privacy concerns; state reconstruction depends on reader capability, and weaker readers might benefit from explicit state; atomic-fact and summary losses on test-time learning couple token volume, demonstration format and factual loss.
- Conclusion: "Improved agentic memory systems should demonstrate gains over a well-specified naive RAG baseline and establish what the added complexity contributes."

## Chapter guide
- Sections 1–3 (pp. 1–5): introduction with the Mem0 audit and MEME oracle, related work, the Raw-RAG pipeline.
- Section 4 (pp. 5–8): benchmarks, main results (Tables 3 and 4), ablations (Tables 5 and 6, Figure 4), efficiency.
- Section 5 (pp. 8–9): coverage and utilization, path coverage, complete-store oracle; Findings 1–3.
- Section 6 (p. 10): limitations and conclusion.
- Appendix A (pp. 16–30): matched-setting results on LoCoMo (text-embedding-3-small and Qwen3 settings, short-answer metrics), LongMemEval-S, PersonaMem-v2; retrieval-depth, evidence-length and 5,000-token controls; coverage and complete-store statistics; efficiency.
- Appendix B (pp. 30–32): Raw-RAG indexing, evidence assembly, query construction, context-length policy.
- Appendix C (pp. 32–37): diagnostic procedures and statistical methods.
- Appendix D (pp. 38–46): benchmark descriptions, per-baseline configurations, scoring, latency method, hardware (an i9-13900HX laptop with 16 GiB RAM and an RTX 5070 Ti Laptop GPU).
- Appendix E (pp. 46–48): review of 14 prior RAG evaluations.
- Appendix F (p. 49): extended discussion and limitations.
- Appendix G (pp. 49–62): reranker, memory-variant, reader and judge prompt templates.

## Entities and concepts
- [[raw-rag]] — the proposed baseline
- [[locomo]], [[longmemeval]], [[meme-benchmark]], [[memoryagentbench]] — the four benchmarks
- [[mem0]] — audited for mutation rates and compared as a baseline
- [[evermemos]], [[memos]], [[memu]], [[memmachine]], [[memora]], [[emem]], [[simplemem]] — compared memory systems with configuration detail in Appendix D.3
- [[retrieval-augmented-memory]] — the approach the baseline instantiates
- [[reranking]] — cross-encoder reranking, the component whose removal costs most
- [[memory-mutation]] — UPDATE and DELETE decisions in memory writes
- [[evidence-coverage-and-utilization]] — the diagnostic decomposition

## Open questions
- Code vs paper: the official repository is ingested as [[repo-litmeb-raw-rag]].
- The comparison is run by the authors of Raw-RAG. For LoCoMo and LongMemEval, published baseline scores are retained from other papers and Raw-RAG is measured in this study under settings the authors say are aligned (Appendix A); Table 3 pairs Raw-RAG's text-embedding-3-small run with some baselines taken from Qwen3-setting papers (for example EverMemOS 86.76 equals its Table 11 value). The matched-setting tables A.1–A.2 show the same ordering, but baselines were not rerun by an independent party.
- The paper reports that Mem0's published GPT-4o-mini LoCoMo category scores weight to 62.14 rather than the published overall 66.88 (Appendix A.1.2); the tables keep both. Which is right is not settled.
- LoCoMo's judge is generous by design ("as long as it touches on the same topic as the gold answer, it should be counted as CORRECT") and the historical records cannot separate format failures from WRONG judgments (zero-score counts of 252–505 of 4,620 judgments per condition, Appendix G.3). Absolute LoCoMo numbers are therefore soft; the paper does not test significance for the main tables.
- The headline "six of seven" counts one reader–benchmark setting per cell and leaves out PersonaMem-v2 (third of seven), Full-context (which beats Raw-RAG on MEME with DeepSeek-V4-Flash) and per-category losses (EMem on LongMemEval multi-session and MEME aggregation, deletion, cascade). The abstract's wording ("among the compared memory systems") is accurate; reading it as "RAG beats agentic memory" is not.
- Appendix E's diagnosis of weak baselines is the authors' reading of other papers' configurations, with no controlled reruns.
- Conversation-only evidence. The paper does not test document knowledge bases, multi-user or operational memory, longer histories than BEAM's one-million-token timing run, or weaker readers; whether raw retrieval still wins there is open.
- ReFind, a concurrent system that keeps raw chat logs with an agent doing iterative lexical search, is cited but not compared; the paper isolates a fixed pipeline from query-time search control.
- The paper evaluates memory for offline conversation. Whether the result carries over to the contexts of coding or tool-using agents (the setting of [[actor-gatherer]]), where the history is actions and observations and where facts the agent does not know it lacks matter ([[unknown-unknowns]]), is not tested.
- The converted markdown garbles some multi-line table cells (for example the LongMemEval M-S./KU. columns in Table 3); the values used here were cross-checked against the PDF.
