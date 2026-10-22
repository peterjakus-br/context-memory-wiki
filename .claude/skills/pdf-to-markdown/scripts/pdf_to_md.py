#!/usr/bin/env python3
"""Convert PDFs (academic papers) to Markdown with embedded images, using IBM Docling.

    ~/.cache/pdf-to-markdown/venv/bin/python .claude/skills/pdf-to-markdown/scripts/pdf_to_md.py paper.pdf
    ... pdf_to_md.py a.pdf b.pdf --out converted/
    ... pdf_to_md.py scanned.pdf --ocr
    ... pdf_to_md.py paper.pdf --no-formula      # faster, but equations become <!-- formula-not-decoded -->

For every input `<stem>.pdf` the script writes, next to the PDF unless --out is given:

    <stem>.md          headings as `##`, tables as GFM pipe tables, formulas as $$LaTeX$$,
                       figures as ![Figure N](<stem>_images/fig-NNN.png) at their position in the text
    <stem>_images/     one PNG per figure, rendered at --scale x the PDF's 72 dpi

Run it with the venv created by setup.sh (CPU-only torch + docling). Conversion is
CPU-bound: expect roughly 3-5 seconds per page on 4 cores, plus a one-off model load.
Existing output is skipped when it is newer than the PDF; pass --force to redo it.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import shutil
import sys
import time
from pathlib import Path

DEFAULT_HOME = Path(os.environ.get("PDF2MD_HOME", Path.home() / ".cache" / "pdf-to-markdown"))
IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")


def build_converter(formula: bool, ocr: bool, scale: float, models: Path | None):
    from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption

    opts = PdfPipelineOptions()
    opts.do_ocr = ocr
    opts.do_table_structure = True
    opts.table_structure_options.do_cell_matching = True
    opts.do_formula_enrichment = formula
    opts.generate_picture_images = True
    opts.images_scale = scale
    opts.accelerator_options = AcceleratorOptions(
        num_threads=os.cpu_count() or 4, device=AcceleratorDevice.CPU)
    if models is not None and models.is_dir() and any(models.iterdir()):
        opts.artifacts_path = models
    return DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)})


def header(pdf: Path, pages: int, formula: bool, ocr: bool, scale: float, seconds: float) -> str:
    import docling
    return "\n".join([
        "<!--",
        f"converted-from: {pdf.name}",
        f"converter: pdf-to-markdown skill (IBM Docling {docling.__version__})",
        f"options: formula={'on' if formula else 'off'} ocr={'on' if ocr else 'off'} images_scale={scale}",
        f"pages: {pages}",
        f"converted: {dt.date.today().isoformat()} ({seconds:.0f}s)",
        "note: generated file. Do not hand-edit; re-run the converter instead.",
        "-->",
        "",
        "",
    ])


def tidy_images(md_text: str, md_path: Path, images_dir: Path) -> tuple[str, int]:
    """Rename Docling's hash-named images to fig-NNN.png in order of appearance and
    rewrite the references relative to the markdown file. Returns (text, image count)."""
    mapping: dict[str, str] = {}
    counter = 0

    def repl(m: re.Match) -> str:
        nonlocal counter
        src = m.group(2)
        src_path = (md_path.parent / src) if not Path(src).is_absolute() else Path(src)
        if src not in mapping:
            counter += 1
            new_name = f"fig-{counter:03d}{src_path.suffix.lower() or '.png'}"
            mapping[src] = new_name
            if src_path.is_file():
                target = images_dir / new_name
                if src_path.resolve() != target.resolve():
                    shutil.move(str(src_path), str(target))
        n = int(mapping[src][4:7])
        return f"![Figure {n}]({images_dir.name}/{mapping[src]})"

    text = IMG_RE.sub(repl, md_text)
    # Remove whatever Docling left behind in its own artifacts folder, if any.
    for leftover in images_dir.glob("image_*"):
        leftover.unlink()
    return text, counter


def convert_one(converter, pdf: Path, out_dir: Path, formula: bool, ocr: bool, scale: float) -> Path:
    from docling_core.types.doc import ImageRefMode

    out_dir.mkdir(parents=True, exist_ok=True)
    md_path = out_dir / f"{pdf.stem}.md"
    images_dir = out_dir / f"{pdf.stem}_images"
    if images_dir.exists():
        shutil.rmtree(images_dir)
    images_dir.mkdir()

    t0 = time.time()
    result = converter.convert(str(pdf))
    status = getattr(result, "status", None)
    if status is not None and str(status).lower().endswith("failure"):
        raise RuntimeError(f"docling failed on {pdf}: {status}")
    doc = result.document

    # artifacts_dir is resolved relative to the markdown file's folder and written into
    # the references verbatim, so a bare relative name keeps the links relative.
    doc.save_as_markdown(md_path, image_mode=ImageRefMode.REFERENCED,
                         artifacts_dir=Path(images_dir.name))
    text, n_images = tidy_images(md_path.read_text(encoding="utf-8"), md_path, images_dir)
    pages = len(getattr(doc, "pages", {}) or {})
    md_path.write_text(header(pdf, pages, formula, ocr, scale, time.time() - t0) + text.rstrip() + "\n",
                       encoding="utf-8")
    undecoded = text.count("<!-- formula-not-decoded -->")
    print(f"wrote {md_path} ({pages} pages, {n_images} images, {time.time() - t0:.0f}s)"
          + (f"; {undecoded} formulas not decoded, re-run without --no-formula" if undecoded else ""))
    return md_path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("pdfs", nargs="+", type=Path, help="PDF file(s) to convert")
    ap.add_argument("--out", type=Path, help="output directory (default: next to each PDF)")
    ap.add_argument("--no-formula", action="store_true",
                    help="skip the CodeFormula model (faster; equations are left as placeholders)")
    ap.add_argument("--ocr", action="store_true", help="run OCR (only for scanned PDFs; slow)")
    ap.add_argument("--scale", type=float, default=2.0, help="figure render scale, 1.0 = 72 dpi (default 2.0)")
    ap.add_argument("--force", action="store_true", help="re-convert even if the .md is newer than the PDF")
    ap.add_argument("--models", type=Path, default=DEFAULT_HOME / "models",
                    help="pre-downloaded Docling models from setup.sh (default: %(default)s)")
    args = ap.parse_args(argv)

    todo: list[Path] = []
    for pdf in args.pdfs:
        if not pdf.is_file() or pdf.suffix.lower() != ".pdf":
            print(f"skip (not a PDF file): {pdf}", file=sys.stderr)
            continue
        out_dir = args.out or pdf.parent
        md = out_dir / f"{pdf.stem}.md"
        if md.exists() and not args.force and md.stat().st_mtime >= pdf.stat().st_mtime:
            print(f"up to date, skipping (use --force): {md}")
            continue
        todo.append(pdf)
    if not todo:
        return 0

    try:
        import docling  # noqa: F401
    except ImportError:
        print("docling is not importable. Run the skill's setup.sh and use its venv python:\n"
              f"  {DEFAULT_HOME / 'venv' / 'bin' / 'python'} {Path(__file__)} ...", file=sys.stderr)
        return 2

    converter = build_converter(not args.no_formula, args.ocr, args.scale, args.models)
    failures = 0
    for pdf in todo:
        try:
            convert_one(converter, pdf, args.out or pdf.parent, not args.no_formula, args.ocr, args.scale)
        except Exception as exc:  # keep going with the other files
            failures += 1
            print(f"FAILED {pdf}: {exc}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
