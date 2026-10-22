# context-memory-wiki

An **LLM wiki**: a knowledge base that an LLM agent builds and maintains from
raw sources you curate, following Andrej Karpathy's
[`llm-wiki` idea file](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
(April 2026).

The pitch: RAG rediscovers knowledge on every question and nothing
accumulates. Here the LLM compiles sources once into an interlinked markdown
wiki and keeps it current. You curate sources and ask questions; the LLM does
the rest.

**Topic:** context management and memory for LLMs and agents — compaction,
retrieval, paging and offloading, memory systems, long-context models,
multi-agent and cross-session context sharing, harness context policies, and
how context and memory are evaluated.

## Layout

```
CLAUDE.md          the schema — conventions and the three operations (read this first)
raw/               immutable sources, YYYY-MM-DD-slug.ext
wiki/
  index.md         catalog of every page, read first on every query
  log.md           append-only operation log
  overview.md      the big picture
  sources/         one page per raw source
  entities/        people, tools, orgs, projects
  concepts/        ideas, patterns, terms
  synthesis/       filed answers and comparisons
scripts/lint.py    mechanical health check
scripts/add_source.py   copy a file into raw/ with a dated name
scripts/add_repo.py     snapshot a code repository (e.g. a memory framework) into raw/repos/
scripts/find_papers.py  find and rank open-access papers for a topic
scripts/fetch_papers.py download selected papers into raw/
.claude/commands/  /ingest, /query, /lint for Claude Code
.claude/skills/    pdf-to-markdown: PDF → markdown + figures (IBM Docling, CPU only)
```

## Quick start

```bash
# 1. add a source (never edit raw/ afterwards)
python3 scripts/add_source.py ~/Downloads/some-article.md --url https://example.com/article

# 1b. for a PDF, convert it first (one-off setup, then ~1 min per paper)
bash .claude/skills/pdf-to-markdown/scripts/setup.sh
~/.cache/pdf-to-markdown/venv/bin/python .claude/skills/pdf-to-markdown/scripts/pdf_to_md.py raw/2026-10-16-paper.pdf

# 2. in Claude Code
/ingest raw/2026-10-16-some-article.md
/query what does the article claim about X?
/lint

# 3. check health any time
python3 scripts/lint.py
```

Any agent that reads `CLAUDE.md` (Claude Code, Cursor, Codex with a symlinked
`AGENTS.md`) can run the operations; the slash commands are just shortcuts.

## The three operations

- **Ingest** — read a raw source in full, write a factual source page, then
  create or update the entity and concept pages it touches, the overview, the
  index and the log. A rich source touches 5–15 pages.
- **Query** — read `wiki/index.md`, drill into pages, answer with
  `[[wikilinks]]` as citations. Substantial answers are filed back into
  `wiki/synthesis/`.
- **Lint** — `scripts/lint.py` catches the mechanical problems (broken links,
  orphans, index coverage, un-ingested sources, stale pages, log format);
  the LLM then does the judgment pass (contradictions, unsupported claims,
  missing concept pages).

## Principles

- `raw/` is immutable. Disagree with a source in the wiki, never by editing it.
- Every wiki claim is traceable to a source page. Numbers and quotes are
  verbatim from raw.
- Contradictions are recorded, not silently resolved. Superseded claims stay,
  marked as superseded. Git is the audit trail.
- The schema evolves. When a convention fails, change `CLAUDE.md`.

## Browsing

The repo is plain markdown. Open it as an Obsidian vault for graph view and
wikilink navigation. Past a few hundred pages, add a local search tool and
keep `index.md` as the human catalog.

## Tests

```bash
python3 -m unittest discover -s tests
```
