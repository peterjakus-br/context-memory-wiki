#!/usr/bin/env python3
"""Snapshot a public code repository into raw/repos/ as an immutable source.

    python3 scripts/add_repo.py https://github.com/andylolu2/ollm
    python3 scripts/add_repo.py https://github.com/x/y --clone-dir /tmp/x-y --max-mb 3

Writes two things, both under raw/repos/ and both immutable afterwards:

- a manifest `raw/repos/<date>-<owner>-<repo>.md`: origin URL, commit, licence,
  sizes, the file tree (kept / skipped per file) and the README verbatim;
- when the repository's code is small enough, a filtered snapshot directory
  `raw/repos/<date>-<owner>-<repo>/` holding the kept files (no .git, no
  binaries, no data blobs over the per-file cap). When code plus small data
  exceeds --max-mb, the data files are dropped and the code kept
  ("code-only"); when even the code exceeds it (benchmark dumps, model
  weights, large Java systems), the manifest alone records the repository.

The snapshot directory is a companion of the manifest: lint treats its files
as part of the manifest's source, the way raw/x_images/ belongs to raw/x.pdf.
The clone itself is made with `git clone --depth 1` (LFS objects skipped) into
--clone-dir, which is left in place for inspection and is not part of raw/.
Nothing under raw/ is overwritten; the script refuses if the target exists.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "env", "dist",
             "build", ".ipynb_checkpoints", ".mypy_cache", ".pytest_cache", ".tox",
             "site-packages", ".idea", ".vscode", "wandb", "mlruns", "checkpoints"}
CODE_EXT = {".py", ".js", ".mjs", ".ts", ".tsx", ".jsx", ".java", ".kt", ".scala", ".rs",
            ".go", ".c", ".cc", ".cpp", ".h", ".hpp", ".rb", ".sh", ".bash", ".r", ".jl",
            ".pl", ".php", ".cs", ".swift", ".lua", ".sql", ".rq", ".sparql", ".shex",
            ".md", ".rst", ".txt", ".toml", ".yaml", ".yml", ".cfg", ".ini", ".tex",
            ".bib", ".cff", ".html", ".css", ".vue", ".svelte", ".j2", ".jinja", ".prompt"}
DATA_EXT = {".json", ".jsonl", ".ttl", ".owl", ".rdf", ".n3", ".nt", ".nq", ".trig", ".xml",
            ".csv", ".tsv", ".ipynb", ".obo", ".ofn", ".omn", ".jsonld"}
NAMED = {"Dockerfile", "Makefile", "LICENSE", "LICENCE", "COPYING", "NOTICE",
         "requirements.txt", "setup.py", "pyproject.toml", "environment.yml", ".gitignore"}
MAX_CODE_FILE = 256 * 1024       # bytes; larger code/text files are skipped
MAX_DATA_FILE = 128 * 1024       # bytes; data files are kept only when small
MAX_README = 60 * 1024           # characters of README copied into the manifest
MAX_TREE_LINES = 400
# Credentials committed upstream are not copied: the value is replaced and the
# manifest lists the files touched. Patterns: well-known token prefixes and a
# quoted value assigned to a key/token/secret/password name.
SECRET_RES = [
    re.compile(r"\b(sk-[A-Za-z0-9_-]{20,}|gsk_[A-Za-z0-9]{20,}|hf_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}"
               r"|AIza[0-9A-Za-z_-]{35}|gh[pousr]_[A-Za-z0-9]{30,}|xox[abprs]-[A-Za-z0-9-]{20,})"),
    re.compile(r"""((?:api[_-]?key|access[_-]?token|secret|password|auth[_-]?token)["']?\s*[:=]\s*["'])"""
               r"""((?=[^"'\s]*\d)[A-Za-z0-9_\-./+=]{16,})(["'])""", re.I),
]
REDACTED = "[REDACTED: credential removed on import]"


def redact(text: str) -> tuple[str, int]:
    text, n1 = SECRET_RES[0].subn(REDACTED, text)
    text, n2 = SECRET_RES[1].subn(lambda m: m.group(1) + REDACTED + m.group(3), text)
    return text, n1 + n2


def slugify(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return re.sub(r"-{2,}", "-", s)


def parse_url(url: str) -> tuple[str, str, str]:
    # GitLab allows nested groups (gitlab.com/group/sub/repo): owner = group path.
    m = re.match(r"https?://(github\.com|gitlab\.com|codeberg\.org|bitbucket\.org)/"
                 r"([^#?]+)/([^/#?]+?)(?:\.git)?/?$", url.strip())
    if m and "/" in m.group(2) and m.group(1) != "gitlab.com":
        m = None
    if not m:
        raise ValueError(f"not a recognised repository URL: {url}")
    return m.group(1), m.group(2), m.group(3)


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 900) -> str:
    env = dict(os.environ, GIT_LFS_SKIP_SMUDGE="1", GIT_TERMINAL_PROMPT="0")
    out = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True,
                         timeout=timeout)
    if out.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)} failed: {out.stderr.strip()[-400:]}")
    return out.stdout.strip()


def is_binary(path: Path) -> bool:
    try:
        with path.open("rb") as fh:
            return b"\0" in fh.read(8192)
    except OSError:
        return True


def classify(path: Path, rel: str) -> tuple[bool, str]:
    """(keep, reason) for one file of the working tree."""
    size = path.stat().st_size
    name, ext = path.name, path.suffix.lower()
    if path.is_symlink():
        return False, "symlink"
    if is_binary(path):
        return False, "binary"
    if name in NAMED or ext in CODE_EXT:
        return (size <= MAX_CODE_FILE,
                "kept" if size <= MAX_CODE_FILE else f"text file over {MAX_CODE_FILE // 1024} KB")
    if ext in DATA_EXT:
        return (size <= MAX_DATA_FILE,
                "kept" if size <= MAX_DATA_FILE else f"data file over {MAX_DATA_FILE // 1024} KB")
    return False, f"unlisted type {ext or '(none)'}"


def walk(repo: Path) -> list[tuple[str, int, bool, str]]:
    rows = []
    for dirpath, dirnames, filenames in os.walk(repo):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for fn in sorted(filenames):
            p = Path(dirpath) / fn
            rel = p.relative_to(repo).as_posix()
            try:
                size = p.lstat().st_size
            except OSError:
                continue
            keep, why = classify(p, rel)
            rows.append((rel, size, keep, why))
    return rows


def licence(repo: Path) -> str:
    for name in ("LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCE", "COPYING"):
        p = repo / name
        if p.is_file():
            head = " ".join(p.read_text(errors="replace").split()[:12])
            for key in ("MIT", "Apache License", "GNU GENERAL PUBLIC", "GNU LESSER",
                        "GNU AFFERO", "BSD", "Mozilla Public", "Creative Commons",
                        "Unlicense", "Eclipse Public", "CC0"):
                if key.lower() in head.lower():
                    return key + f" (from {name})"
            return f"see {name}: \"{head[:80]}\""
    return "none found"


def readme(repo: Path) -> tuple[str, str]:
    for p in sorted(repo.iterdir()):
        if p.is_file() and p.name.lower().startswith("readme"):
            text = p.read_text(errors="replace")
            if len(text) > MAX_README:
                text = text[:MAX_README] + f"\n\n[README truncated at {MAX_README} characters]\n"
            return p.name, text
    return "", ""


def human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return str(n)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("url")
    ap.add_argument("--title", help="human title (default: owner/repo)")
    ap.add_argument("--note", help="one line recorded in the manifest, e.g. which paper it implements")
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--clone-dir", help="where to clone (default: /tmp/repo-snapshots/<owner>/<repo>)")
    ap.add_argument("--max-mb", type=float, default=3.0,
                    help="snapshot only when the kept files total at most this (default 3 MB)")
    ap.add_argument("--manifest-only", action="store_true", help="never copy files")
    ap.add_argument("--root", default=".")
    ap.add_argument("--json", action="store_true", help="print a JSON summary for scripts")
    args = ap.parse_args(argv)

    host, owner, name = parse_url(args.url)
    url = f"https://{host}/{owner}/{name}"
    root = Path(args.root).resolve()
    stem = f"{args.date}-{slugify(owner)}-{slugify(name)}"
    out_dir = root / "raw" / "repos"
    manifest, snap = out_dir / f"{stem}.md", out_dir / stem
    if manifest.exists() or snap.exists():
        print(f"refusing to overwrite existing raw file: {manifest}", file=sys.stderr)
        return 1

    clone = Path(args.clone_dir or f"/tmp/repo-snapshots/{owner}/{name}")
    if not (clone / ".git").is_dir():
        clone.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", "--depth", "1", "--quiet", url, str(clone)])
    if run(["git", "remote", "get-url", "origin"], cwd=clone).rstrip("/").removesuffix(".git").lower() != url.lower():
        print(f"{clone} is not a clone of {url}", file=sys.stderr)
        return 1
    commit = run(["git", "rev-parse", "HEAD"], cwd=clone)
    commit_date = run(["git", "log", "-1", "--format=%cs"], cwd=clone)
    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=clone)

    rows = walk(clone)
    total = sum(r[1] for r in rows)
    cap = args.max_mb * 1024 * 1024
    kept_bytes = sum(r[1] for r in rows if r[2])
    code_only = False
    if kept_bytes > cap:
        # Too much with data files: keep the code and docs, drop data and notebooks.
        rows = [(rel, size, keep and Path(rel).suffix.lower() not in DATA_EXT,
                 why if not keep or Path(rel).suffix.lower() not in DATA_EXT
                 else "data file dropped (code-only snapshot)")
                for rel, size, keep, why in rows]
        kept_bytes = sum(r[1] for r in rows if r[2])
        code_only = True
    kept = [r for r in rows if r[2]]
    if args.manifest_only or kept_bytes > cap or not kept:
        mode = "manifest-only"
    elif code_only:
        mode = "code-only"
    elif len(kept) == len(rows):
        mode = "full"
    else:
        mode = "partial"

    lic = licence(clone)
    rname, rtext = readme(clone)
    title = args.title or f"{owner}/{name}"
    lines = [
        "<!--",
        f"title: {title} (code repository)",
        f"added: {args.date}",
        f"origin: {url}",
        f"commit: {commit} ({commit_date}, branch {branch})",
        f"snapshot: {mode}" + (f" -> raw/repos/{stem}/" if mode != "manifest-only" else ""),
        "note: raw source, immutable. Do not edit. Generated by scripts/add_repo.py.",
        "-->",
        f"# {title} — repository manifest",
        "",
    ]
    if args.note:
        lines += [args.note, ""]
    lines += [
        f"- URL: {url}",
        f"- Commit: `{commit}` ({commit_date}, branch `{branch}`), shallow clone, Git LFS objects not fetched",
        f"- Licence: {lic}",
        f"- Working tree: {len(rows)} files, {human(total)}",
        f"- Snapshot: **{mode}** — {len(kept)} files, {human(kept_bytes)} "
        + ("copied to `raw/repos/" + stem + "/`" if mode != "manifest-only"
           else f"would be kept; not copied (cap {args.max_mb} MB or --manifest-only)"),
        f"- Policy: code/text files ≤ {MAX_CODE_FILE // 1024} KB and data files ≤ {MAX_DATA_FILE // 1024} KB are kept; "
        "binaries, symlinks and the directories " + ", ".join(sorted(SKIP_DIRS)) + " are not.",
        "",
        "## File tree",
        "",
        "```",
    ]
    for rel, size, keep, why in rows[:MAX_TREE_LINES]:
        lines.append(f"{'+' if keep and mode != 'manifest-only' else '-'} {rel}  ({human(size)}"
                     + ("" if keep else f"; {why}") + ")")
    if len(rows) > MAX_TREE_LINES:
        lines.append(f"... {len(rows) - MAX_TREE_LINES} more files not listed")
    lines += ["```", "", "`+` copied into the snapshot, `-` not copied.", ""]
    lines += [f"## {rname or 'README'} (verbatim)", "", rtext or "_No README found._", ""]

    out_dir.mkdir(parents=True, exist_ok=True)
    manifest.write_text("\n".join(lines), encoding="utf-8")
    redacted = []
    if mode != "manifest-only":
        for rel, _, keep, _ in kept:
            dst = snap / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            text, n = redact((clone / rel).read_text(encoding="utf-8", errors="surrogateescape"))
            if n:
                redacted.append(f"{rel} ({n})")
                dst.write_text(text, encoding="utf-8", errors="surrogateescape")
            else:
                shutil.copyfile(clone / rel, dst)
        if redacted:
            with manifest.open("a", encoding="utf-8") as fh:
                fh.write("\n## Redactions\n\nCredential-like values replaced on import: "
                         + ", ".join(redacted) + "\n")

    summary = {"url": url, "manifest": manifest.relative_to(root).as_posix(),
               "snapshot": mode, "snapshot_dir": snap.relative_to(root).as_posix() if mode != "manifest-only" else None,
               "commit": commit, "commit_date": commit_date, "licence": lic,
               "files": len(rows), "bytes": total, "kept_files": len(kept), "kept_bytes": kept_bytes,
               "clone": str(clone), "redacted": redacted}
    if args.json:
        print(json.dumps(summary))
    else:
        print(f"wrote {summary['manifest']} ({mode}, {len(kept)}/{len(rows)} files, "
              f"{human(kept_bytes)} of {human(total)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
