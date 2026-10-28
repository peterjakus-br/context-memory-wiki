---
title: "Raw-RAG"
type: entity
created: 2026-10-28
updated: 2026-10-28
tags: [memory-system, baseline, retrieval]
sources: [raw-rag-naive-rag-agentic-memory, repo-litmeb-raw-rag]
---
Raw-RAG is the naive baseline proposed in [[raw-rag-naive-rag-agentic-memory]] to test whether agentic memory needs its complexity: [[retrieval-augmented-memory|retrieval]] over raw conversation history with only dense retrieval and a cross-encoder [[reranking|reranker]], leaving evidence interpretation and state reconstruction to the reader model. The paper offers it as a diagnostic baseline that memory systems should be compared against, not as a product.

## Facts
- **What is stored**: the raw history itself. Each conversation is serialised with message timestamps and image captions, cut into 256-token windows with 32-token overlap (GPT-4 tokenizer) and embedded in a flat per-conversation index. There is no LLM-based extraction, summarisation, graph construction or mutation ([[raw-rag-naive-rag-agentic-memory]])
- **How context is selected**: a fixed pipeline, not the agent and not a separate LLM component. The original question is the retrieval query; the 128 nearest windows by cosine similarity are scored jointly with the question by a cross-encoder and the top 15 go to the reader. On LoCoMo, LongMemEval and MEME each selected window is expanded to the complete source turns it overlaps; on MemoryAgentBench expansion is disabled ([[raw-rag-naive-rag-agentic-memory]])
- Embedder and reranker pairs, by comparison setting: text-embedding-3-small with Cohere Rerank-v3.5, and Qwen3-Embedding-4B with Qwen3-Reranker-4B ([[raw-rag-naive-rag-agentic-memory]])
- **Granularity and eviction**: fixed-size overlapping windows; nothing is evicted, so storage grows with history length ([[raw-rag-naive-rag-agentic-memory]])
- **Scope**: one local index per conversation (LoCoMo, MEME, PersonaMem-v2 questions on one history share it; LongMemEval has one per example); single-agent, offline conversation benchmarks. Embedding and reranking use API endpoints ([[raw-rag-naive-rag-agentic-memory]])
- Results (the paper's runs; LLM-judged or benchmark-scored as each benchmark prescribes): [[locomo]] 89.07 with a GPT-4o-mini reader and 93.70 with GPT-4.1-mini; [[longmemeval]] 87.53 with GPT-4.1-mini; [[meme-benchmark]] 39.30 with GPT-4o-mini and 43.19 with DeepSeek-V4-Flash; [[memoryagentbench]] 48.32 with GPT-4o-mini and 53.41 with DeepSeek-V4-Flash. First among the compared memory systems (Full-context excluded) in six of these seven benchmark–reader settings; the exception is MEME with DeepSeek-V4-Flash, where [[memmachine]] leads by 1.52 points and Full-context by 19.98 ([[raw-rag-naive-rag-agentic-memory]])
- Third of seven on PersonaMem-v2 (49.62%, GPT-4.1-mini reader, no persona profile), behind [[evermemos]] and [[memos]], which use profiles ([[raw-rag-naive-rag-agentic-memory]])
- Ablations on MemoryAgentBench (GPT-4o-mini): dropping the reranker costs 3.92 points; final k from 5 to 60 and chunk sizes from 128 to 1,024 tokens change little; top-1 and top-120 lose 11.73 and 14.57 points; adding atomic-fact extraction, raw summaries or graph-expanded candidates lowers the total ([[raw-rag-naive-rag-agentic-memory]])
- **Cost**: no LLM calls at ingestion. On 10 MEME episodes and 110 questions (one outer worker, API-served models, no answer generation) Add-to-ready plus search takes 305.91 s against 1,561.97 to 9,301.48 s for the five systems timed; on a roughly one-million-token, 1,710-message conversation cumulative add time is 0.33 hours against 3.25 to 26.95 hours for the systems that finished ([[raw-rag-naive-rag-agentic-memory]])
- Highest evidence coverage of the systems compared (45.29% on MemoryAgentBench, 76.35% on MEME) and highest conditional path coverage on MEME (62.34%); see [[evidence-coverage-and-utilization]] ([[raw-rag-naive-rag-agentic-memory]])
- **Known limitations** (authors): offline conversation benchmarks only; raw storage grows with history and raises privacy concerns; no tested answer to operational needs such as exposing state to tools or erasing stored information ([[raw-rag-naive-rag-agentic-memory]])
- **Code**: official implementation in `Litmeb/RAW-RAG` ([[repo-litmeb-raw-rag]]): the pipeline is one adapter (`system: rag`) in an evaluation harness; the code matches the paper's 256/32 windows, 128 candidates and top 15, reranks all 128 candidates in one call, fails loudly if the reranker response is malformed instead of falling back to dense order, and filters windows by session date before selecting candidates ([[repo-litmeb-raw-rag]])
- The reader sees each window under a header such as `Memory N (chunk=…, similarity=…, rerank=…)`, which exposes the retrieval scores; the paper does not describe this ([[repo-litmeb-raw-rag]])
- An independent reproduction of the LoCoMo result by the GoodMem team is reported in the repository README: 88.68 (GPT-4o-mini reader) and 93.48 (GPT-4.1-mini) against the paper's 89.07 and 93.70; the claim is not verified here ([[repo-litmeb-raw-rag]])

## Related
- [[repo-litmeb-raw-rag]] — its code
- [[retrieval-augmented-memory]] — the approach
- [[memory-mutation]] — what it leaves out on purpose
- [[mem0]], [[evermemos]], [[memos]], [[memu]], [[memmachine]], [[memora]], [[emem]], [[simplemem]] — systems it is compared with
- [[context-compaction]] — the lossy-summary alternative in coding harnesses
