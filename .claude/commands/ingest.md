---
description: Ingest a raw source into the wiki (Karpathy LLM-wiki ingest op)
argument-hint: <path under raw/ or a file to add>
---
Ingest `$ARGUMENTS` into the wiki following the **Ingest** operation in CLAUDE.md.

Steps, in order:
1. If the path is not under `raw/`, add it with `python3 scripts/add_source.py $ARGUMENTS` first. Never edit files under `raw/`.
2. Read the entire raw file.
3. Triage out loud in one or two sentences: new material, update, contradiction, or nothing new.
4. Discuss the key takeaways with the user before writing: what the source adds, what it challenges, what you plan to emphasise, which pages you expect to touch. Stop and wait for their steer unless they asked for an unattended batch.
5. Write `wiki/sources/<slug>.md` with the source template.
6. Create or update entity and concept pages for everything the source discusses substantively. Add `## Contradictions` where it disagrees with existing pages. Bump `updated:` and `sources:` on touched pages.
7. Update `wiki/overview.md` if the big picture changed.
8. Update `wiki/index.md` (tables + remove from `## Unprocessed`).
9. Append an `ingest` entry to `wiki/log.md`.
10. Run `python3 scripts/lint.py` and fix every error.

Finish with a short list of pages created and updated.
