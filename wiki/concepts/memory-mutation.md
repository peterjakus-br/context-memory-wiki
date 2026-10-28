---
title: "Memory mutation"
type: concept
created: 2026-10-28
updated: 2026-10-28
tags: [memory, write-path]
sources: [raw-rag-naive-rag-agentic-memory]
confidence: low
---
Memory mutation is the write-side practice of changing or removing stored memories when new information arrives, as against only appending. In systems such as [[mem0]] each candidate fact is compared with retrieved neighbours and the system chooses ADD, UPDATE, DELETE or NONE. The question is whether UPDATE and DELETE earn their complexity. One source so far.

## What the sources say
- In an audit of [[mem0]] 1.0.11 over all [[locomo]] conversations and all 500 [[longmemeval]] examples, UPDATE and DELETE were 4.39% of 33,902 write decisions and 2.46% of 428,858. Effective mutations (persisted text-changing updates or deletions) were 1.90% and 1.34%. Many proposed updates were duplicates or malformed ([[raw-rag-naive-rag-agentic-memory]])
- Replacing UPDATE with ADD and DELETE with NONE raised Mem0's LoCoMo accuracy from 67.36% to 69.42% with no category lower (multi-hop +1.42, temporal +3.32, open-domain +6.94, single-hop +1.23), in the paper's configuration ([[raw-rag-naive-rag-agentic-memory]])
- On [[meme-benchmark]], readers given phase-visible raw evidence in chronological order resolved changed state themselves: DeepSeek-V4-Flash 82.32% on cascades and 91.54% on invalidation, though GPT-4o-mini scored 1.83% on cascades, so state reconstruction depends on the reader ([[raw-rag-naive-rag-agentic-memory]])
- The authors list operational needs that answer accuracy does not cover: exposing authoritative state to other tools, triggering actions after updates, and erasing stored information; their raw-history approach does not address them, and they say structured memory might still help weaker readers ([[raw-rag-naive-rag-agentic-memory]])
- The paper's general MEME store uses Mem0 2.0.11, a different version from the 1.0.11 audited, so the audit does not describe the newer version ([[raw-rag-naive-rag-agentic-memory]])

## Related
- [[retrieval-augmented-memory]] — the read side
- [[raw-rag]] — the append-only, no-mutation baseline
- [[context-compaction]] — summarising old context is another lossy rewrite
