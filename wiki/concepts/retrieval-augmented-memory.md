---
title: "Retrieval-augmented memory"
type: concept
created: 2026-10-28
updated: 2026-10-28
tags: [memory, retrieval, context-management]
sources: [raw-rag-naive-rag-agentic-memory, actor-gatherer-framework-blog]
confidence: medium
---
Retrieval-augmented memory keeps an agent's past (conversation turns, actions, observations) in an external store and, at query time, retrieves the pieces judged relevant and appends them to the context. The store can hold raw history or a transformed version of it (extracted facts, summaries, graph nodes, profiles). The sources disagree less on whether to retrieve than on what to store and how much machinery sits between the history and the reader.

## What the sources say
- A naive pipeline over raw history, [[raw-rag]] (256-token windows with overlap, 128 dense candidates, cross-encoder rerank to 15), ranks first among compared memory systems in six of seven benchmark–reader settings on [[locomo]], [[longmemeval]], [[meme-benchmark]] and [[memoryagentbench]] ([[raw-rag-naive-rag-agentic-memory]])
- Variants that replace raw text with extracted content do worse on MemoryAgentBench (GPT-4o-mini reader): atomic facts 28.70 against 48.32, raw summary added to each window 42.51, graph-expanded candidates 42.54 ([[raw-rag-naive-rag-agentic-memory]])
- Even with gold-informed access to every system's complete store on MEME (GPT-4o-mini reader), all seven stores stay 7.58 to 29.38 points below raw evidence once the packing cap is removed; the stores that keep raw conversational content ([[raw-rag]], [[memmachine]]) recover closest. The authors read this as information discarded or distorted at ingestion being hard to recover, while saying that selection, packing and lost-in-the-middle effects also contribute ([[raw-rag-naive-rag-agentic-memory]])
- Systems differ more in how often they surface sufficient evidence than in how well the reader then uses it ([[evidence-coverage-and-utilization]]) ([[raw-rag-naive-rag-agentic-memory]])
- Prior RAG baselines are said to be under-tuned (chunks of 2,048 to 4,096 tokens, top-k of 1 to 5, no reranker among 14 reviewed evaluations), so reported gaps to agentic memory may reflect weak baselines; the authors call this their own assessment and say quantifying it needs controlled reruns ([[raw-rag-naive-rag-agentic-memory]])
- Ingestion cost differs by orders of magnitude: no LLM calls for raw windows, against 0.33 hours for a roughly one-million-token conversation for [[raw-rag]] and 3.25 to 26.95 hours for the other systems that finished ([[raw-rag-naive-rag-agentic-memory]])
- Reader capability matters: on MEME, giving readers the phase-visible raw evidence in order yields 50.50 with GPT-4o-mini and 85.48 with DeepSeek-V4-Flash, and Full-context with DeepSeek-V4-Flash (63.17) beats [[raw-rag]] (43.19), while with GPT-4o-mini Full-context (29.31) trails it (39.30) ([[raw-rag-naive-rag-agentic-memory]])
- In a coding-agent harness, memory that appends retrieved summaries to the context is described as still lossy: "embedding-based retrieval can be inaccurate", and failures occur "when it either does not retrieve the relevant information or the relevant information is not included in its memories at all" ([[actor-gatherer-framework-blog]], about [[mem0]])

## Contradictions
- Whether retrieval is a weak foundation for agent context: [[actor-gatherer-framework-blog]] argues that retrieved, summarised memory is lossy and that agent-driven retrieval misses [[unknown-unknowns]], and reports Mem0-Codex at 59% against 91% for [[actor-gatherer]] on the authors' planted-specification tasks (agent model gemini-3.1-pro-preview). [[raw-rag-naive-rag-agentic-memory]] finds a retrieval-only pipeline over raw history ahead of the extraction-based systems it compares on conversation-memory benchmarks. (inference) The two agree that summaries and extracted memories lose information, and they test different things: planted-specification tasks in coding sessions against question answering over conversation history; the scores are not comparable, and neither source tests the other's setting.

## Related
- [[raw-rag]] — the baseline instance
- [[reranking]] — the second stage that matters most in the ablation
- [[memory-mutation]] — write-side operations that the raw approach skips
- [[context-compaction]] — the lossy-summary default of coding harnesses
- [[proactive-context-management]] — context built by a separate component
- [[mem0]], [[evermemos]], [[memos]], [[memu]], [[memmachine]], [[memora]], [[emem]], [[simplemem]] — systems that transform history
