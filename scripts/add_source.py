#!/usr/bin/env python3
"""Copy a file into raw/ with a dated, kebab-case name and a metadata header.

    python3 scripts/add_source.py notes.md
    python3 scripts/add_source.py paper.pdf --title "Attention is all you need"
    python3 scripts/add_source.py article.md --url https://example.com/x --date 2026-04-04
    cat clipboard.txt | python3 scripts/add_source.py - --title "Chat with Alice"

Text-like files (.md, .txt) get a small header recording title, origin and
the date added. Binary files (pdf, images) are copied unchanged and get a
sidecar `<name>.meta.md` with the same header. Nothing under raw/ is ever
overwritten; the script refuses if the target exists.

After adding, run the ingest workflow from CLAUDE.md.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import date
from pathlib import Path

TEXT_EXT = {".md", ".txt", ".markdown"}


def slugify(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return re.sub(r"-{2,}", "-", s) or "source"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("file", help="path to copy, or '-' for stdin (markdown)")
    ap.add_argument("--title", help="human title (default: derived from filename)")
    ap.add_argument("--url", help="where the source came from")
    ap.add_argument("--date", default=date.today().isoformat(),
                    help="YYYY-MM-DD prefix (default: today)")
    ap.add_argument("--slug", help="override the generated slug")
    ap.add_argument("--root", default=".", help="repo root (default: .)")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    raw = root / "raw"
    raw.mkdir(exist_ok=True)

    if args.file == "-":
        if not args.title:
            ap.error("--title is required when reading from stdin")
        content = sys.stdin.read()
        ext = ".md"
        src_path = None
    else:
        src_path = Path(args.file)
        if not src_path.is_file():
            ap.error(f"not a file: {src_path}")
        ext = src_path.suffix.lower() or ".md"
        content = None

    title = args.title or (src_path.stem.replace("_", " ").replace("-", " ")
                           if src_path else "source")
    slug = args.slug or slugify(title)
    target = raw / f"{args.date}-{slug}{ext}"
    if target.exists():
        print(f"refusing to overwrite existing raw file: {target}", file=sys.stderr)
        return 1

    header = "\n".join(
        line for line in [
            "<!--",
            f"title: {title}",
            f"added: {args.date}",
            f"origin: {args.url}" if args.url else (f"origin: {src_path}" if src_path else None),
            "note: raw source, immutable. Do not edit.",
            "-->",
            "",
        ] if line is not None
    )

    if ext in TEXT_EXT:
        body = content if content is not None else src_path.read_text(encoding="utf-8")
        target.write_text(header + body, encoding="utf-8")
    else:
        shutil.copyfile(src_path, target)
        side = target.with_suffix(target.suffix + ".meta.md")
        side.write_text(header + f"# {title}\n\nBinary source: `{target.name}`\n",
                        encoding="utf-8")
        print(f"wrote sidecar {side.relative_to(root)}")

    print(f"wrote {target.relative_to(root)}")
    print("next: ingest it (see CLAUDE.md → Operations → Ingest)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
