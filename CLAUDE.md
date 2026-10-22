# context-memory-wiki — schema

This repository is an **LLM wiki** in the sense of Andrej Karpathy's `llm-wiki`
idea file (April 2026). Instead of re-deriving answers from raw documents on
every question (RAG), the LLM incrementally builds and maintains a persistent,
interlinked markdown wiki. Knowledge is compiled once and kept current.

**Topic:** context management and memory for LLMs and agents: what goes into
the context window and how it is chosen (compaction, summarisation,
retrieval, paging, offloading, context engineering), long-term and episodic
memory systems, long-context models, multi-agent and cross-session context
sharing, agent harnesses and their context policies, and how context and
memory are evaluated.

This file is the **schema**: it defines the layers, page types, conventions and
the three operations. It is the most important file in the repo. Read it
before touching anything under `wiki/`. When conventions here turn out to be
wrong or incomplete, propose a change to this file rather than working around it.

## The three layers

| Layer | Path | Owner | Mutability |
|---|---|---|---|
| Raw sources | `raw/` | human | **immutable** — the LLM reads, never edits |
| Wiki | `wiki/` | LLM | freely rewritten by the LLM, read by humans |
| Schema | `CLAUDE.md` | human + LLM | evolves slowly, by agreement |

Rules:

- Never modify, rename or delete anything under `raw/`. If a source is wrong,
  say so in the wiki page that summarises it.
- Everything under `wiki/` is derived from `raw/`. Any claim in the wiki must
  be traceable to a raw source through a `[[wikilink]]` to a source page or a
  `sources:` frontmatter entry. If you cannot cite it, label it as inference.
- The human curates sources and asks questions. The LLM does everything else.

## Layout

```
raw/                      immutable sources (YYYY-MM-DD-slug.ext)
  repos/                  code repositories: <date>-<owner>-<repo>.md manifest + optional snapshot dir
wiki/
  index.md                catalog of every page; read first, updated on every change
  log.md                  append-only operation log
  overview.md             the big picture across all sources
  sources/                one page per raw source (summary + takeaways)
  entities/               people, tools, organisations, projects, repos
  concepts/               ideas, patterns, techniques, terms
  synthesis/              answers to queries, comparisons, position pieces
scripts/lint.py           mechanical health check (run before and after lint)
scripts/add_source.py     copies a file into raw/ with a dated name and header
scripts/add_repo.py       snapshots a public code repository into raw/repos/
scripts/find_papers.py    discovers and ranks open-access papers for a topic (no downloads)
scripts/fetch_papers.py   downloads selected open-access papers into raw/
.claude/skills/pdf-to-markdown/   converts a raw PDF to markdown + images (Docling)
```

Each wiki page is one markdown file. Filenames are kebab-case slugs and are
**unique across all of `wiki/`**, because wikilinks resolve by basename.

## Page conventions

Every page under `wiki/` (except `index.md` and `log.md`) starts with YAML
frontmatter:

```yaml
---
title: Human readable title
type: source | entity | concept | synthesis | overview
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [a, b]
# source pages only:
source: raw/2026-04-04-example.md
# entity / concept / synthesis pages:
sources: [llm-wiki-pattern-research]     # slugs of source pages this draws on
confidence: high | medium | low          # concept and synthesis pages
---
```

- `type` must match the directory the page lives in.
- `updated` marks the last change to what the page *says*. Adding a
  cross-link, or a note about a repository that implements the source (a
  bullet citing a `repo-…` page, e.g. "Code vs paper: …"), to a source page
  does not bump it: lint's staleness check reads a newer source page as
  "pages it cites may need revising", which such a note does not warrant.
  Revising the summary, key points or open questions about the work does.
- Link with `[[slug]]` or `[[slug|display text]]`. Link generously: every
  entity or concept named in prose that has a page should be linked at least
  once per page.
- Source pages are **factual**: what the source says, in its own terms. Put
  interpretation and cross-source synthesis in concept and synthesis pages.
- When two sources disagree, do not overwrite. Add a `## Contradictions`
  section to the concept page naming both sources and what each claims.
- When a claim is superseded, keep the old claim, mark it `(superseded by
  [[newer-source]])` and state the new one. Git is the audit trail.
- Numbers, dates and direct quotes must appear in the raw source they are
  attributed to. Do not round, extrapolate or paraphrase a quote.
- Prefer extending an existing page over creating a near-duplicate. Before
  creating a page, grep `wiki/` for the term.
- Duplicate raw files: when a raw file is another copy of a source that
  already has a page (same paper, second download), write a short source page
  that says so and links the primary page, so every raw file stays accounted
  for. Do not summarise it twice. A preprint and the published version of the
  same study both get full pages, cross-linked in `## Open questions`, with
  the earlier one marked `(superseded by [[later-slug]])`; they count as one
  source when judging confidence.
- Typing: techniques, policies, architectural patterns and phenomena
  (compaction, retrieval-augmented memory, context offloading, KV-cache reuse,
  unknown unknowns, context rot) are concepts. Named frameworks, memory
  systems, agent harnesses, models, benchmarks, datasets, projects, labs and
  organisations are entities. A person gets an entity page only when at least
  two sources discuss them; otherwise name them in plain text.
- System entity pages (tag `memory-system`, `harness` or `framework`) state,
  as far as the sources say: what is stored, how context is selected (who
  decides — the agent via tools, the harness, a separate component — and when),
  granularity and eviction, single- vs multi-agent scope, integrations, and
  known limitations, each with a citation.
- Benchmark entity pages (tag `benchmark`) state what capability is measured,
  task format and size, scoring metric, who built it and when, and known
  problems, each with a citation.
- Reported scores are never free-floating. Every number names the model (and
  version or date where the source gives it), the benchmark and split, the
  setting (shots, tools, scaffold, judge) and the source it comes from.
  Scores from different sources or settings are not compared in one sentence
  without saying so.

- Code repositories: a repository that implements a paper is a source like
  any other. `scripts/add_repo.py <url>` writes a manifest
  `raw/repos/<date>-<owner>-<repo>.md` (URL, commit, licence, file tree,
  README verbatim) and, when the code without data is small (default cap
  3 MB), a filtered snapshot directory of the same name; lint treats that
  directory as the manifest's companion. Big repositories are manifest-only:
  summarised and pointed to. The source page (tag `repository`) says what
  the code implements, whether it is the paper authors' **official** code or
  a **community** implementation, and how faithful it is to the paper; the
  paper's source page and entity page link to it.

### Page templates

**Source page** (`wiki/sources/<slug>.md`)

```markdown
## Summary
Two to five sentences: what this source is and what it argues.

## Key points
- Bulleted, factual, each point attributable to the source.

## Entities and concepts
- [[entity-slug]] — one-line role in this source
- [[concept-slug]] — one-line role in this source

## Open questions
- Things the source raises but does not answer, or that you doubt.
```

A long source (book, course, proceedings volume) adds a `## Chapter guide`
section between Key points and Entities and concepts: one bullet per chapter
or part saying what it covers, so a reader can find where a topic lives.
Errors found in the source itself go under Open questions, never corrected
silently.

**Entity page** (`wiki/entities/<slug>.md`)

```markdown
One paragraph: who/what this is and why it matters here.

## Facts
- Fact ([[source-slug]])

## Related
- [[other-slug]] — relationship
```

**Concept page** (`wiki/concepts/<slug>.md`)

```markdown
One paragraph definition.

## What the sources say
- Claim ([[source-slug]])

## Contradictions
(omit the section if there are none)

## Related
- [[other-slug]]
```

**Synthesis page** (`wiki/synthesis/<slug>.md`): free-form, but open with the
question it answers and close with a `## Sources` list of wikilinks.

## index.md

`wiki/index.md` is the catalog. It has one table per section (Sources,
Entities, Concepts, Synthesis) with columns `Page | One-line description`, and
a final `## Unprocessed` list of raw files that have no source page yet. Every
page under `wiki/` must appear in it. It is read first on every query. A
`Pages:` count line under the heading is optional.

## log.md

`wiki/log.md` is append-only. Each entry is:

```markdown
## [YYYY-MM-DD] <operation> | <short title>
- what was read
- pages created / updated (as wikilinks)
- anything notable: contradictions found, schema changes proposed
```

`<operation>` is one of `ingest`, `query`, `lint`, `schema`. Never edit or
reorder earlier entries. `grep "^## \[" wiki/log.md | tail` shows recent work.
A batch ingest writes one `ingest` entry per source, one per merge batch and
one summary entry naming what needs a human decision.

## Operations

### Ingest

Trigger: the user adds a file to `raw/` or asks you to ingest something.

1. If the source is not yet under `raw/`, put it there with
   `python3 scripts/add_source.py <file> [--title ...] [--url ...]`.
   Never edit it afterwards.
2. Read the **whole** raw file. Do not summarise from the first screen.
   A PDF is first converted with the `pdf-to-markdown` skill, which writes
   `raw/<name>.md` and `raw/<name>_images/` next to `raw/<name>.pdf`. Read
   that `.md` (open the PNGs for figures). These companions are generated,
   never hand-edited, and are committed with the PDF. `source:` in the
   source page cites the `.pdf`; lint treats the companions as part of it.
   A PDF too large for one Docling run (several hundred pages) is split into
   parts with pypdf, each part converted by the skill script, and the outputs
   concatenated with figures renumbered; the `.md` header records the split.
   A converted source too long for one reading context is split at `##`
   headings into chunks; each chunk is read in full and noted, and the source
   page (with its chapter guide) is assembled from the notes.
3. Triage: is this new material, an update to known material, a contradiction
   of known material, or nothing new? Say which, briefly, before writing.
4. Discuss the key takeaways with the user before writing: what the source
   adds, what it challenges, what you plan to emphasise and which pages you
   expect to touch. When a human is present, stop and wait for their steer.
   When running unattended (a scheduled job, a batch the user asked for),
   state the takeaways in the transcript and proceed. Ingest one source at
   a time unless the user asked for a batch.
5. Write `wiki/sources/<slug>.md` using the source template.
6. For each entity and concept the source mentions substantively: create the
   page if missing, otherwise update it (new facts, new `sources:` entry,
   bump `updated`). Add contradictions explicitly. A rich source typically
   touches 5–15 pages; a thin one may touch only its own source page.
7. Update `wiki/overview.md` if the big picture changed.
8. Update `wiki/index.md`: add new pages, refresh descriptions, remove the raw
   file from `## Unprocessed`.
9. Append to `wiki/log.md`.
10. Run `python3 scripts/lint.py` and fix anything it reports.

### Batch ingest

Trigger: many raw files arrive at once (a folder of papers, a discovery run).
One agent per source cannot safely edit shared pages in parallel, so the
operation is staged:

1. Convert every PDF first (one Docling process per batch, smallest first).
2. One reader per source. It reads the whole converted file, writes only its
   own `wiki/sources/<slug>.md`, and writes a *proposals* file outside the
   repo listing the entities and concepts it would create or extend, each
   fact with its `([[source-slug]])` citation, plus relations and tensions
   with existing pages. Readers never touch entity, concept, index, log or
   overview pages; their wikilinks may dangle until the merge. All readers
   get the same list of canonical slugs so they converge on the same names.
3. Merge, one topic cluster at a time, never two in parallel: fold the
   cluster's proposals into entity and concept pages, reconcile synonyms
   (retarget the source pages' wikilinks rather than create duplicates),
   drop slugs with a single passing mention, add `## Contradictions`, set
   confidence, and clear every broken link the cluster introduced.
4. The coordinator then rebuilds `index.md`, rewrites `overview.md`, appends
   the log entries, runs the lint judgment pass and commits.

Keep the wiki committed after every stage; a reclaimed cloud container loses
only the stage in flight.

### Query

Trigger: the user asks a question about the material.

1. Read `wiki/index.md`. Pick the relevant pages. Grep `wiki/` for terms the
   index does not surface, including synonyms.
2. Read the wiki pages, not the raw sources. Go to `raw/` only to verify a
   quote or number, or when the wiki is silent.
3. Answer with `[[wikilinks]]` as citations. Distinguish what the sources say
   from your own inference.
4. If the answer is substantial (a comparison, a position, a multi-source
   synthesis) and the user agrees, file it as `wiki/synthesis/<slug>.md`,
   add it to the index and append a `query` log entry. A trivial lookup
   writes nothing.

### Lint

Trigger: periodically, or when the user asks, or after a large batch ingest.

1. Run `python3 scripts/lint.py`. It checks the mechanical things: frontmatter,
   broken links, orphans, index coverage, un-ingested raw files, duplicate
   slugs, log format, pages that look stale relative to their sources.
2. Fix every error it reports. Fix warnings you can fix safely.
3. Then do the judgment pass the script cannot:
   - contradictions between pages that neither page acknowledges,
   - claims in concept pages not backed by any cited source,
   - concepts named repeatedly in prose that lack their own page,
   - entity pages that have drifted out of date relative to newer sources,
   - missing `## Related` links that an attentive reader would expect,
   - data gaps: questions the wiki raises but cannot answer, and claims
     resting on a single source. For each, say what a web search or a new
     source could settle. Do not fetch anything during lint; list the
     candidate sources and questions under `## Gaps` in `wiki/overview.md`
     so the human can curate them into `raw/`.
4. Report what you fixed and what needs a human decision. Append a `lint`
   log entry. Run the script again; it should be clean.

## Scale notes

The index-first approach works to roughly a hundred sources and a few hundred
pages without embeddings. Beyond that, add a local full-text or hybrid search
tool (for example `qmd`) and keep `index.md` as the human catalog. The wiki is
plain markdown in git; Obsidian can open the repo root as a vault for graph
view and wikilink navigation.
