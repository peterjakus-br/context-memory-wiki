---
description: Run the wiki health check and fix what it finds (Karpathy LLM-wiki lint op)
---
Run the **Lint** operation from CLAUDE.md.

1. Run `python3 scripts/lint.py`. Fix every error and every warning that can be fixed safely (broken links, missing index rows, orphans that should be linked from a related page, missing `sources:` entries).
2. Then do the judgment pass the script cannot do: read the concept and entity pages and look for
   - contradictions between pages that neither page acknowledges,
   - claims not backed by any cited source page,
   - concepts named repeatedly in prose that lack their own page,
   - entity pages out of date relative to newer sources,
   - missing `## Related` links a reader would expect,
   - data gaps: unanswered questions and single-source claims, with the web search or new source that could settle each. Do not fetch during lint; record them under `## Gaps` in `wiki/overview.md`.
3. Fix what is safe to fix. List anything needing a human decision.
4. Append a `lint` entry to `wiki/log.md`, then run `python3 scripts/lint.py` again; it should be clean.
