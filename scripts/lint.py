#!/usr/bin/env python3
"""Mechanical health check for the LLM wiki.

Checks the things a script can check so the LLM lint pass can spend its
attention on judgment (contradictions, stale claims, missing concepts).

    python3 scripts/lint.py            # human-readable report
    python3 scripts/lint.py --json     # machine-readable
    python3 scripts/lint.py --root DIR # lint a different checkout

Exit status is 1 when any error is found, 0 otherwise (warnings do not fail).
Standard library only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import date
from pathlib import Path

PAGE_TYPES = {"source", "entity", "concept", "synthesis", "overview"}
DIR_TYPES = {
    "sources": "source",
    "entities": "entity",
    "concepts": "concept",
    "synthesis": "synthesis",
}
SPECIAL = {"index.md", "log.md"}
REQUIRED_KEYS = ("title", "type", "created", "updated")
LOG_OPS = ("ingest", "query", "lint", "schema")

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
MDLINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s#]+)(?:#[^)]*)?\)")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LOG_HEADING_RE = re.compile(r"^## \[(\d{4}-\d{2}-\d{2})\] (\w+) \| (.+)$")
FENCE_RE = re.compile(r"^(```|~~~)")


@dataclass
class Page:
    path: Path
    rel: str
    slug: str
    section: str  # top-level dir under wiki/ or "" for root
    front: dict = field(default_factory=dict)
    body: str = ""
    wikilinks: list[str] = field(default_factory=list)
    mdlinks: list[str] = field(default_factory=list)


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


# --------------------------------------------------------------------------
# parsing
# --------------------------------------------------------------------------

def parse_frontmatter(text: str) -> tuple[dict | None, str]:
    """Return (frontmatter dict or None, body). Minimal YAML: scalars, [a, b]
    inline lists and '- item' block lists. Good enough for the schema."""
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---", 4)
    if end == -1:
        return None, text
    raw = text[4:end]
    body = text[end + 4 :].lstrip("\n")
    data: dict = {}
    key = None
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")) or line.startswith("- "):
            item = line.strip()
            if item.startswith("- ") and key is not None:
                data.setdefault(key, [])
                if not isinstance(data[key], list):
                    data[key] = []
                data[key].append(_scalar(item[2:]))
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if value == "":
            data[key] = []
        elif value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            data[key] = [_scalar(v) for v in inner.split(",")] if inner else []
        else:
            data[key] = _scalar(value)
    return data, body


def _scalar(v: str) -> str:
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1]
    return v


def strip_code(body: str) -> str:
    """Drop fenced code blocks and inline code so example links don't count."""
    out, in_fence = [], False
    for line in body.splitlines():
        if FENCE_RE.match(line.strip()):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(re.sub(r"`[^`]*`", "", line))
    return "\n".join(out)


def load_pages(wiki: Path) -> list[Page]:
    pages = []
    for path in sorted(wiki.rglob("*.md")):
        rel = path.relative_to(wiki).as_posix()
        parts = rel.split("/")
        section = parts[0] if len(parts) > 1 else ""
        text = path.read_text(encoding="utf-8")
        front, body = parse_frontmatter(text)
        p = Page(path=path, rel=rel, slug=path.stem, section=section,
                 front=front or {}, body=body if front is not None else text)
        prose = strip_code(p.body)
        p.wikilinks = [m.strip() for m in WIKILINK_RE.findall(prose)]
        p.mdlinks = [m for m in MDLINK_RE.findall(prose)
                     if not m.startswith(("http://", "https://", "mailto:"))]
        pages.append(p)
    return pages


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------

def check_frontmatter(pages: list[Page], rep: Report) -> None:
    for p in pages:
        if p.path.name in SPECIAL and p.section == "":
            continue
        if not p.front:
            rep.error(f"{p.rel}: missing frontmatter")
            continue
        for k in REQUIRED_KEYS:
            if k not in p.front or p.front[k] in ("", []):
                rep.error(f"{p.rel}: frontmatter missing '{k}'")
        t = p.front.get("type")
        if t not in PAGE_TYPES:
            rep.error(f"{p.rel}: unknown type '{t}'")
        elif p.section in DIR_TYPES and DIR_TYPES[p.section] != t:
            rep.error(f"{p.rel}: type '{t}' does not match directory "
                      f"'{p.section}/' (expected '{DIR_TYPES[p.section]}')")
        elif p.section == "" and t != "overview":
            rep.error(f"{p.rel}: only type 'overview' may live at wiki/ root")
        for k in ("created", "updated"):
            v = p.front.get(k)
            if isinstance(v, str) and v and not DATE_RE.match(v):
                rep.error(f"{p.rel}: '{k}' is not YYYY-MM-DD: {v!r}")
        c, u = p.front.get("created"), p.front.get("updated")
        if isinstance(c, str) and isinstance(u, str) and DATE_RE.match(c) \
                and DATE_RE.match(u) and u < c:
            rep.error(f"{p.rel}: 'updated' ({u}) is before 'created' ({c})")
        if t == "source" and not p.front.get("source"):
            rep.error(f"{p.rel}: source page needs a 'source:' raw path")
        if t in ("concept", "synthesis"):
            conf = p.front.get("confidence")
            if conf not in ("high", "medium", "low"):
                rep.warn(f"{p.rel}: confidence should be high|medium|low "
                         f"(got {conf!r})")


def check_slugs(pages: list[Page], rep: Report) -> dict[str, Page]:
    by_slug: dict[str, Page] = {}
    for p in pages:
        if p.slug in by_slug:
            rep.error(f"duplicate slug '{p.slug}': {by_slug[p.slug].rel} and "
                      f"{p.rel} (wikilinks resolve by basename)")
        else:
            by_slug[p.slug] = p
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", p.slug):
            rep.warn(f"{p.rel}: filename is not a kebab-case slug")
    return by_slug


def check_links(pages: list[Page], by_slug: dict[str, Page], wiki: Path,
                rep: Report) -> dict[str, set[str]]:
    """Return inbound map slug -> {slugs that link to it}."""
    inbound: dict[str, set[str]] = {s: set() for s in by_slug}
    root = wiki.parent
    for p in pages:
        for target in p.wikilinks:
            slug = target.rsplit("/", 1)[-1]
            if slug.endswith(".md"):
                slug = slug[:-3]
            if slug in by_slug:
                if slug != p.slug:
                    inbound[slug].add(p.slug)
            else:
                rep.error(f"{p.rel}: broken wikilink [[{target}]]")
        for target in p.mdlinks:
            cand = (p.path.parent / target).resolve()
            if not cand.exists():
                cand2 = (root / target).resolve()
                if not cand2.exists():
                    rep.error(f"{p.rel}: broken relative link ({target})")
                    continue
                cand = cand2
            try:
                rel = cand.relative_to(wiki.resolve())
                slug = rel.stem
                if slug in by_slug and slug != p.slug:
                    inbound[slug].add(p.slug)
            except ValueError:
                pass  # link outside wiki/ (e.g. raw/) — fine
    return inbound


def check_orphans(pages: list[Page], inbound: dict[str, set[str]],
                  rep: Report) -> None:
    nav = {"index", "log", "overview"}
    for p in pages:
        if p.slug in nav:
            continue
        linkers = inbound.get(p.slug, set()) - nav
        if not linkers:
            rep.warn(f"{p.rel}: orphan (no inbound links other than index/log/overview)")


def check_index(pages: list[Page], by_slug: dict[str, Page], wiki: Path,
                rep: Report) -> None:
    index = by_slug.get("index")
    if index is None or index.section != "":
        rep.error("wiki/index.md is missing")
        return
    linked = set()
    for t in index.wikilinks:
        linked.add(t.rsplit("/", 1)[-1].removesuffix(".md"))
    for t in index.mdlinks:
        linked.add(Path(t).stem)
    for p in pages:
        if p.slug in ("index", "log"):
            continue
        if p.slug not in linked:
            rep.error(f"index.md: does not list {p.rel}")


def check_raw(pages: list[Page], root: Path, rep: Report) -> None:
    raw = root / "raw"
    if not raw.is_dir():
        rep.warn("raw/ directory is missing")
        return
    cited: set[str] = set()
    for p in pages:
        if p.front.get("type") == "source":
            src = p.front.get("source")
            if isinstance(src, str) and src:
                if not (root / src).exists():
                    rep.error(f"{p.rel}: source path does not exist: {src}")
                cited.add(src)
    index = next((p for p in pages if p.slug == "index" and p.section == ""), None)
    unprocessed = _unprocessed_from_index(index) if index else set()
    # Companions of a binary source (raw/x.pdf): the converted raw/x.md, the
    # raw/x.pdf.meta.md sidecar and raw/x_images/* belong to x.pdf and are
    # neither cited nor listed on their own.
    stems = {_stem(c) for c in cited | unprocessed if not c.endswith(".md")}
    # A repository manifest (raw/repos/x.md, scripts/add_repo.py) owns the
    # code snapshot in raw/repos/x/ the same way.
    dirs = {_stem(c) + "/" for c in cited | unprocessed if (root / _stem(c)).is_dir()}
    for f in sorted(raw.rglob("*")):
        if not f.is_file() or f.name in ("README.md", ".gitkeep"):
            continue
        rel = f.relative_to(root).as_posix()
        if rel not in cited and rel not in unprocessed and (
                _is_companion(rel, stems) or any(rel.startswith(d) for d in dirs)):
            continue
        if rel not in cited:
            if rel in unprocessed:
                rep.warn(f"{rel}: not ingested yet (listed under Unprocessed)")
            else:
                rep.warn(f"{rel}: not ingested and not listed in index.md "
                         f"'## Unprocessed'")
        elif rel in unprocessed:
            rep.error(f"index.md: {rel} is ingested but still listed under "
                      f"'## Unprocessed'")


def _stem(rel: str) -> str:
    """raw/2026-01-02-b.pdf -> raw/2026-01-02-b"""
    return rel.rsplit(".", 1)[0] if "." in rel.rsplit("/", 1)[-1] else rel


def _is_companion(rel: str, stems: set[str]) -> bool:
    return any(rel.startswith(stem + ".") or rel.startswith(stem + "_") for stem in stems)


def _unprocessed_from_index(index: Page) -> set[str]:
    text = index.body
    m = re.search(r"^## Unprocessed\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m:
        return set()
    found = set()
    for line in m.group(1).splitlines():
        for tok in re.findall(r"`([^`]+)`|\(([^)\s]+)\)|(raw/\S+)", line):
            val = next(v for v in tok if v)
            found.add(val.strip())
    return found


def check_stale(pages: list[Page], by_slug: dict[str, Page], rep: Report) -> None:
    """A page is possibly stale if a source page that cites it (via wikilink)
    was updated after the page itself."""
    for src in pages:
        if src.front.get("type") != "source":
            continue
        su = src.front.get("updated")
        if not (isinstance(su, str) and DATE_RE.match(su)):
            continue
        for target in src.wikilinks:
            slug = target.rsplit("/", 1)[-1].removesuffix(".md")
            tp = by_slug.get(slug)
            if not tp or tp.front.get("type") not in ("entity", "concept"):
                continue
            tu = tp.front.get("updated")
            if isinstance(tu, str) and DATE_RE.match(tu) and tu < su:
                rep.warn(f"{tp.rel}: possibly stale — cited by {src.rel} "
                         f"(updated {su}) but last updated {tu}")


def check_sources_field(pages: list[Page], by_slug: dict[str, Page],
                        rep: Report) -> None:
    for p in pages:
        srcs = p.front.get("sources")
        if not srcs:
            if p.front.get("type") in ("entity", "concept", "synthesis"):
                rep.warn(f"{p.rel}: no 'sources:' in frontmatter")
            continue
        if isinstance(srcs, str):
            srcs = [srcs]
        for s in srcs:
            tp = by_slug.get(str(s))
            if tp is None:
                rep.error(f"{p.rel}: sources entry '{s}' is not a wiki page")
            elif tp.front.get("type") != "source":
                rep.warn(f"{p.rel}: sources entry '{s}' is not a source page")


def check_log(wiki: Path, rep: Report) -> None:
    log = wiki / "log.md"
    if not log.exists():
        rep.error("wiki/log.md is missing")
        return
    last = None
    for n, line in enumerate(log.read_text(encoding="utf-8").splitlines(), 1):
        if not line.startswith("## "):
            continue
        m = LOG_HEADING_RE.match(line)
        if not m:
            rep.error(f"log.md:{n}: heading not in form "
                      f"'## [YYYY-MM-DD] <op> | <title>': {line!r}")
            continue
        d, op, _ = m.groups()
        if op not in LOG_OPS:
            rep.error(f"log.md:{n}: unknown operation '{op}' "
                      f"(expected one of {', '.join(LOG_OPS)})")
        if last and d < last:
            rep.warn(f"log.md:{n}: entry dated {d} appears after {last} "
                     f"(log should be chronological)")
        last = d


def check_future_dates(pages: list[Page], rep: Report) -> None:
    today = date.today().isoformat()
    for p in pages:
        for k in ("created", "updated"):
            v = p.front.get(k)
            if isinstance(v, str) and DATE_RE.match(v) and v > today:
                rep.warn(f"{p.rel}: '{k}' is in the future ({v})")


# --------------------------------------------------------------------------

def run(root: Path) -> Report:
    rep = Report()
    wiki = root / "wiki"
    if not wiki.is_dir():
        rep.error("wiki/ directory is missing")
        return rep
    pages = load_pages(wiki)
    check_frontmatter(pages, rep)
    by_slug = check_slugs(pages, rep)
    inbound = check_links(pages, by_slug, wiki, rep)
    check_orphans(pages, inbound, rep)
    check_index(pages, by_slug, wiki, rep)
    check_raw(pages, root, rep)
    check_sources_field(pages, by_slug, rep)
    check_stale(pages, by_slug, rep)
    check_future_dates(pages, rep)
    check_log(wiki, rep)
    return rep


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".", help="repo root (default: .)")
    ap.add_argument("--json", action="store_true", help="JSON output")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    rep = run(root)
    if args.json:
        print(json.dumps(asdict(rep), indent=2))
    else:
        pages = len(list((root / "wiki").rglob("*.md"))) if (root / "wiki").is_dir() else 0
        print(f"lint: {pages} wiki pages, {len(rep.errors)} errors, "
              f"{len(rep.warnings)} warnings")
        for e in rep.errors:
            print(f"  ERROR  {e}")
        for w in rep.warnings:
            print(f"  warn   {w}")
        if not rep.errors and not rep.warnings:
            print("  clean")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
