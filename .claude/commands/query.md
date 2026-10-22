---
description: Answer a question from the wiki with citations (Karpathy LLM-wiki query op)
argument-hint: <question>
---
Answer this question using the wiki, following the **Query** operation in CLAUDE.md:

> $ARGUMENTS

1. Read `wiki/index.md` first. Grep `wiki/` for terms and synonyms the index does not surface.
2. Read the relevant wiki pages. Go to `raw/` only to verify a quote or number or when the wiki is silent.
3. Answer with `[[wikilinks]]` as citations. Separate what the sources say from your own inference. Say plainly when the wiki does not cover something.
4. If the answer is substantial (comparison, position, multi-source synthesis), offer to file it as `wiki/synthesis/<slug>.md`; if filed, add it to `wiki/index.md` and append a `query` entry to `wiki/log.md`.
