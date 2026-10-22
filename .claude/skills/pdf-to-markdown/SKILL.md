---
name: pdf-to-markdown
description: Convert a PDF (academic paper, report, whitepaper) into clean Markdown with headings, GFM tables, LaTeX formulas and the figures extracted as PNG files referenced inline. Use when the user adds a PDF to raw/, asks to ingest/read/summarise a PDF, or asks to convert a PDF to Markdown. CPU-only, works in Claude Code cloud sessions.
---

# pdf-to-markdown

Turns `paper.pdf` into `paper.md` plus `paper_images/fig-001.png …`, using
[IBM Docling](https://github.com/docling-project/docling): layout model for
reading order and headings, TableFormer for tables, CodeFormula for equations,
figure crops rendered from the page. Everything runs on CPU, nothing is sent
to an external service.

Do **not** use `markitdown` or `pdftotext` for papers: they drop images, lose
headings and mangle two-column layouts.

## 1. Setup (once per machine or cloud container)

```bash
bash .claude/skills/pdf-to-markdown/scripts/setup.sh
```

Creates `~/.cache/pdf-to-markdown/venv` (CPU torch + docling, ~2 GB) and
downloads the three models (~0.7 GB) to `~/.cache/pdf-to-markdown/models`.
Takes a few minutes on a fresh container; re-running is a no-op. Cloud
containers are ephemeral, so expect to run it again in a new session. Needs
outbound access to pypi.org, download.pytorch.org and huggingface.co.

## 2. Convert

```bash
PY=~/.cache/pdf-to-markdown/venv/bin/python
$PY .claude/skills/pdf-to-markdown/scripts/pdf_to_md.py raw/2026-10-16-some-paper.pdf
```

Output lands next to the PDF (`--out DIR` to put it elsewhere):

```
raw/2026-10-16-some-paper.md            the markdown (headings are `##`, tables are pipe tables,
                                        formulas are $$…$$, figures are ![Figure N](…) in place)
raw/2026-10-16-some-paper_images/       fig-001.png, fig-002.png, …
```

Options: `--ocr` for scanned PDFs (much slower, off by default), `--no-formula`
to skip the equation model (about 35 % faster; equations then appear as
`<!-- formula-not-decoded -->`, so keep it on for papers), `--scale 3`
for higher-resolution figures, `--force` to redo an up-to-date file. Several
PDFs can be passed at once; the models load only once.

Budget roughly 3–5 s per page on a 4-core CPU container (a 15-page paper is
about a minute, plus ~10 s model load).

## 3. Read and check the result

Open the `.md`, not the PDF. Then look for the known rough edges and mention
them to the user when they matter:

- **Heading levels are flat.** Docling emits every section header as `##`;
  numbering in the title (`3.2.1 …`) carries the hierarchy.
- **Figure labels leaking as headings or text.** Text drawn inside vector
  figures (axis labels, box names) can surface as a stray `## …` line or a
  short paragraph next to the image. Ignore it; the figure PNG is correct.
- **`<!-- formula-not-decoded -->`** means the run had `--no-formula`, or the
  model gave up on that equation. Re-run, or read the equation from the PDF.
- **Footnotes and references** are plain paragraphs; citation brackets `[12]`
  are preserved as text.
- **Scanned PDFs** come out nearly empty without `--ocr`.

To answer a question about a chart or diagram, open the PNG under
`<stem>_images/` with the Read tool; do not guess from the caption.

## 4. In this wiki

`raw/` stays immutable: the PDF is the source, the generated `.md` and
`_images/` folder are its companions, written once by this script and never
hand-edited. Add the PDF with `scripts/add_source.py`, convert it, then run the
normal ingest with `source: raw/<name>.pdf` in the source page and read the
companion `.md`. `scripts/lint.py` treats `<name>.md`, `<name>.pdf.meta.md`
and `<name>_images/` as part of `<name>.pdf`. Commit the companions together
with the PDF so later sessions (and other agents) do not have to reconvert.

## Why Docling (tested 2026-10-16 in a Claude Code cloud container, 4 CPU cores, no GPU)

| Tool | 15-page paper | Headings | Tables | Formulas | Figures |
|---|---|---|---|---|---|
| Docling 2.140 (this skill) | 45 s, 69 s with formulas | all `##`, clean | correct | LaTeX with `--enrich-formula`, else dropped | 7 crops, in place, captions kept |
| Marker 2.0 (CPU, OCR off) | 15 s | hierarchy but inconsistent | broken cells | plain text | 5 crops, in place; reference list mashed into one paragraph; OCR needs a llama.cpp binary |
| PyMuPDF4LLM 1.28 | 10 s | hierarchy with bold noise, stray figure text | second table broken | rendered as images | figures and every equation as PNG, OCR text dumps |
| MarkItDown 0.1.7 | fast | mostly lost | partial | plain text | none |
