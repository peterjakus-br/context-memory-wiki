---
title: "Litmeb/RAW-RAG (code repository)"
type: source
created: 2026-10-28
updated: 2026-10-28
tags: [repository, memory, retrieval, evaluation, benchmark]
source: raw/repos/2026-10-28-litmeb-raw-rag.md
---
The **official** code for [[raw-rag-naive-rag-agentic-memory]]: the paper's title page links it and its README opens "Implementation and experimental code for" the paper. Snapshotted at commit `95639191e954` (2026-10-25, branch `main`), MIT licence (root `LICENSE`). The tree has 731 files (7.3 MB) and is recorded **manifest-only** (6.2 MB of code would be kept, over the 3 MB cap), so the manifest holds the file tree and README; the code was read in a scratch clone at the same commit. The repository is an evaluation harness plus the baseline's adapter, not a library: benchmark data, results and API keys are not included.

## Summary
The Raw-RAG pipeline is a single adapter (`methods/EverCore/evaluation/src/adapters/rag_adapter.py`, `system: rag`) that builds 256-token windows with 32-token overlap, embeds them, takes the 128 nearest windows, reranks all 128 with an HTTP cross-encoder and keeps 15. Around it sit adapters for the compared systems ([[evermemos]], [[mem0]], [[memmachine]], [[memora]], [[memos]], [[memu]], [[emem]], [[simplemem]], Zep, MemoryOS), a Full-context adapter, the three memory-management ablations, dataset and judge configurations, 54 analysis and oracle scripts for the paper's diagnostics, and 54 test files. A PowerShell runner, `scripts/paper/run_rawrag.ps1`, runs the paper's main and appendix conditions from per-condition profiles. The README reports an independent LoCoMo reproduction by another team.

## Key points
- **Layout.** `methods/EverCore/src` (443 files, about 5 MB) is a vendored copy of the EverCore system source (package `memsys`, Apache-2.0 in its `pyproject.toml`, against the repository's root MIT licence); the RAW-RAG-specific code lives in `methods/EverCore/evaluation` (193 files, 148 Python), `methods/EverCore/tests` (54 files) and `scripts` (25 files). That EverCore is the system behind [[evermemos]] is an inference from the directory name and from `evermemos` adapters sitting beside the `rag` adapter; the README does not say.
- **Pipeline** (`rag_adapter.py`, `config/systems/rag.yaml`): the whole conversation is serialised to one document and cut into token windows of `chunk_size` 256 and `chunk_overlap` 32 with the GPT-4 tokenizer (stride 224). Embeddings are batched in 128s. At search time the question alone is embedded, windows from sessions dated after the question date are dropped first (date-level granularity, a chunk is hidden if any of its turns is later), the top `embedding_top_k` = 128 are reranked as one list (`top_n` = all candidates), and `rerank_top_k` = 15 are kept in rerank order unless a dataset override sorts them chronologically (MEME does).
- **Display.** With `expand_turns_on_display` true (the default; off for MemoryAgentBench) each kept window is shown as the complete turns it overlaps, prefixed with a conversation header on the first chunk. Each block is labelled `Memory N (chunk=…, similarity=…, rerank=…)`, so the reader sees the retrieval and rerank scores; the paper counts "memory headers" in evidence length but does not describe this content.
- **Reranker.** Calls `{base_url}{endpoint}` with `model`, `query`, `documents` and `top_n`, retries up to 3 times, and **raises** if the response is malformed (wrong count, duplicate indices, non-finite scores); there is no silent fallback to dense order, which matches the paper's warning that falling back omits reranking. For models whose name contains `qwen3-reranker` it wraps query and documents in the chat template reproduced in the paper's Appendix G.1.
- **Paper profiles** (`scripts/paper/configs`, `conditions.json`): `textemb3` = text-embedding-3-small plus Cohere `rerank-v3.5` (`/v2/rerank`), `qwen3` = Qwen3-Embedding-4B plus Qwen3-Reranker-4B; readers GPT-4o-mini, GPT-4.1-mini and DeepSeek-V4-Flash; judges GPT-4o-mini-2024-07-18 (three runs) for LoCoMo and LongMemEval and GPT-4o-2024-11-20 for MEME. Each of the 15 conditions (7 main, 8 appendix) records `expected_questions` (1,540, 500, 470, 1,188, 2,071 or 5,000) and the `reported_score` from the paper (for example 89.07, 93.70, 87.53, 39.30, 43.19, 48.32, 53.41 for the main group and 89.13, 94.55, 89.93, 49.62 among the appendix ones), which agree with the paper's tables. The DeepSeek-V4-Flash MEME and MemoryAgentBench conditions reuse the GPT-4o-mini retrieval and rerun only answering and evaluation.
- **Dataset overrides** in `rag.yaml`: MemoryAgentBench turns off turn expansion and keeps the two fact-consolidation sources as one-message-per-chunk (`strategy: turn`, `chunk_size: 1`); MEME sorts selected chunks by time and uses the official MEME answer prompt; PersonaMem-v2 uses a personalization prompt.
- **Mem0 add-only control** (`mem0_adapter.py`, `config/systems/mem0_local_no_update_delete.yaml`): pinned to mem0ai 1.0.11 and enforced in code, not by prompt: the adapter wraps the LLM's response so UPDATE becomes ADD (dropping `id` and `old_memory`) and DELETE becomes NONE, and also removes ids from NONE events so no vector update occurs at all. An add-audit log (`mem0_add_audit.jsonl`) records the decisions. This is the mechanism behind the paper's 67.36 to 69.42 LoCoMo result.
- **Memory-management ablations** (`rag_memory_ablation_adapter.py`, `config/systems/rag_*.yaml`): variants `atomic_facts_only`, `raw_summary`, `graph_only` and `graph_expanded_raw`, all reusing the chunking, embedding and reranking stack. The extraction model defaults to gpt-4o-mini-2024-07-18 at temperature 0 with `fail_on_extraction_error: true`. The graph variant compares each new window with its 10 nearest earlier windows, lets the LLM accept links, and at query time takes 32 embedding seeds, adds every one-hop neighbour (`max_raw_candidates: 0`), reranks and keeps 15, with graph cues disabled in the reader context. `graph_only` has a config but is not among the three variants the paper reports.
- **Full-context** (`config/systems/full_context.yaml`): a 128,000-token context window, a 256-token safety margin and `head_tail` truncation with 4,096 output tokens, matching the paper's bounded-history policy.
- **Diagnostics.** `evaluation/scripts` holds the analysis code behind the paper's Section 5: coverage and utilization significance tests (`analyze_mab_coverage_significance.py`, `analyze_mab_utilization_significance.py`), MEME result and path assessment (`analyze_meme_result_path_gap.py`, `judge_meme_reasoning_evidence.py`), complete-store oracles (`build_meme_complete_store_oracle_runs.py`, `run_meme_complete_store_uncapped.py`), the 5,000-token controls (`build_rag_5k_intervention_runs.py`, `cap_mab_formatted_context.py`) and the BEAM timing converter and runner (`convert_beam_1m_sequence.py`, `speed_sequence_cli.py`).
- **Reproduction.** Python 3.12 and PowerShell 7 are required; benchmark files go under `evaluation/data` (LoCoMo `locomo10.json`, LongMemEval `longmemeval_s_cleaned.json`, MEME `meme_filler32k.json`; MemoryAgentBench downloads itself); credentials come from `methods/EverCore/.env` (`LLM_*`, `VECTORIZE_*`, `RERANK_*`, `DEEPSEEK_*`). Commands: `pwsh -File scripts/paper/run_rawrag.ps1 -Group Main -Tag paper`, or `python -m evaluation.cli --dataset locomo --system rag`. Runs must be sequential within one checkout.
- **Community reproduction** (README, not verified here): the GoodMem team reproduced the LoCoMo evaluation with the embedding model, reranker and retrieval depths from the paper's Table 10 and reports 88.68 (GPT-4o-mini reader) and 93.48 (GPT-4.1-mini) against the paper's 89.07 and 93.70. Their repository (PAIR-Systems-Inc/goodmem-memory-benchmarks) is linked, not ingested.
- **Tests**: `tests/test_paper_profiles.py` and `tests/test_rawrag_regressions.py` check the profiles and the baseline; others cover each baseline adapter, the oracle builders, the analysis scripts, and Mem0 sharding and audit logging. They were not run here.

## Code vs paper
| Paper mechanism | In code |
|---|---|
| 256-token windows, 32 overlap, GPT-4 tokenizer, flat per-conversation index | implemented (`rag.yaml`, `_create_token_chunks`) |
| 128 dense candidates, cross-encoder rerank, top 15 to the reader | implemented; all 128 are reranked in one call |
| Turn expansion for LoCoMo, LongMemEval, MEME; none for MemoryAgentBench; chronological order for MEME | implemented as dataset overrides |
| Retrieval query is the original question | implemented (only the question string is embedded and reranked) |
| Question-date temporal visibility | implemented at date granularity before candidate selection |
| Reranker failure must not fall back to dense order | implemented: it raises after 3 attempts |
| Mem0 ADD/NONE-only control | implemented in code, 1.0.11 pinned |
| Atomic-fact, raw-summary and graph-expanded variants | implemented; same stack, LLM extraction at gpt-4o-mini-2024-07-18 |
| Full-context with bounded history | implemented (128,000 tokens, head-tail truncation) |
| Coverage, utilization, path, complete-store and 5k diagnostics | analysis and run-builder scripts present; data and per-question results are not in the repository |
| Dynamic top-k selection | present in the adapter (`dynamic_top_k`, score threshold 0.5, fallback 3) but **disabled by default** and not described in the paper |
| Default `rag.yaml` reranker | model unset (`RERANK_MODEL`), base URL defaults to Jina; the paper's Cohere and Qwen3 settings live only in `scripts/paper/configs` |
| Hosted model snapshots (GPT-4o-mini-2024-07-18, GPT-4o-2024-11-20, DeepSeek-V4-Flash) | named in the profiles; outputs depend on provider state |

## Entities and concepts
- [[raw-rag]] — the baseline this code implements
- [[retrieval-augmented-memory]], [[reranking]], [[memory-mutation]], [[evidence-coverage-and-utilization]] — the ideas its adapters and scripts implement
- [[locomo]], [[longmemeval]], [[meme-benchmark]], [[memoryagentbench]] — the benchmarks its dataset configs load
- [[mem0]] — the add-only control

## Open questions
- No benchmark data, per-question outputs or result tables ship with the repository, so the paper's numbers cannot be checked without the datasets and paid API access to the named hosted models.
- The community reproduction is the repository's own report; the GoodMem repository was not read, and it covers LoCoMo only (the 0.22 to 0.39 point gaps it reports are small but are one run each).
- The reader-visible `similarity=` and `rerank=` values in each memory header are not mentioned in the paper; whether they affect answers is untested.
- The vendored EverCore tree (about 5 MB, Apache-2.0 metadata inside an MIT repository) is not explained in the README; which of its parts the experiments actually use was not traced.
- Whether temporal filtering at date granularity changes results against the paper's description ("where supported") was not tested.
