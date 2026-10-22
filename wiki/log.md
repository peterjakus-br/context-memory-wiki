# Log

Append-only. One entry per operation, newest at the bottom.
`grep "^## \[" wiki/log.md | tail -5` shows recent work.

## [2026-10-22] schema | Bootstrap the wiki from evals-bench-wiki
- Forked the structure of peterjakus-br/evals-bench-wiki (itself forked from peterjakus-br/semantic-wiki): CLAUDE.md schema, raw/ and wiki/ layout, scripts (lint, add_source, add_repo, find_papers, fetch_papers), tests, the /ingest, /query, /lint commands and the pdf-to-markdown skill.
- Topic changed to context management and memory for LLMs and agents.
- Schema changes: typing rule rewritten (techniques, policies and phenomena are concepts; frameworks, memory systems, harnesses, models, benchmarks are entities); system entity pages record what is stored, who selects context and when, granularity, scope, integrations and limitations. The evals-specific score rule is kept: every reported number names model, task, setting and source.
