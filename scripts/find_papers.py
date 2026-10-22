#!/usr/bin/env python3
"""Discover open-access papers for a topic and rank them for the wiki.

Standard library only. Talks to free, keyless APIs:

  arxiv     export.arxiv.org/api   full text always OA; HTML at arxiv.org/html/<id>
  arxiv_web arxiv.org/search       same index via the website (needs bs4); use when the
                                   API times out or answers 429 from a shared egress IP
  crossref  api.crossref.org       DOI metadata + citation counts (is-referenced-by-count)
  openalex  api.openalex.org       citation counts + oa_url (rate-limited from shared
                                   egress IPs; retried with backoff)
  openaire  api.openaire.eu/graph  OA-only filter, citation counts, full-text URLs and
                                   licences. Best keyless source for "cited classics".

Usage
    python3 scripts/find_papers.py search  -q "agent context management" -q "LLM long-term memory" \
        --source arxiv --source crossref --out candidates.json
    python3 scripts/find_papers.py existing --out existing.json     # titles already in raw/
    python3 scripts/find_papers.py dedupe candidates.json existing.json --out new.json
    python3 scripts/find_papers.py rank new.json --classics 25 --recent 25 --since 2023

`search` writes one JSON record per hit: {source, id, doi, arxiv_id, title, authors,
year, venue, cited_by, abstract, url, oa_url}. `dedupe` drops records whose normalised
title, DOI or arXiv id is already in raw/ (or appears twice in the candidate list).
`rank` splits by year into a classics bucket and a recent bucket and sorts each by
citations. Nothing here downloads anything; see fetch_papers.py.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

UA = "context-memory-wiki-find-papers/0.1 (+https://github.com/peterjakus-br/context-memory-wiki)"


def get(url: str, tries: int = 4, pause: float = 3.0) -> bytes:
    last = None
    for i in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:  # 429 / 5xx: back off
            last = e
            if e.code not in (429, 500, 502, 503, 504):
                raise
        except (urllib.error.URLError, TimeoutError) as e:
            last = e
        time.sleep(pause * (2 ** i))
    raise RuntimeError(f"giving up on {url}: {last}")


def norm_title(t: str) -> str:
    t = re.sub(r"<[^>]+>", "", t or "")
    t = re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()
    return t


# ---------------------------------------------------------------- sources
ATOM = "{http://www.w3.org/2005/Atom}"
ARXIV = "{http://arxiv.org/schemas/atom}"


def search_arxiv(query: str, n: int) -> list[dict]:
    q = urllib.parse.quote(f'(ti:"{query}" OR abs:"{query}")')
    url = (f"https://export.arxiv.org/api/query?search_query={q}"
           f"&start=0&max_results={n}&sortBy=relevance&sortOrder=descending")
    root = ET.fromstring(get(url))
    out = []
    for e in root.findall(ATOM + "entry"):
        aid = e.findtext(ATOM + "id", "").rsplit("/abs/", 1)[-1]
        base = re.sub(r"v\d+$", "", aid)
        doi = e.findtext(ARXIV + "doi")
        out.append({
            "source": "arxiv", "id": f"arxiv:{base}", "arxiv_id": base,
            "doi": doi.lower() if doi else None,
            "title": " ".join(e.findtext(ATOM + "title", "").split()),
            "authors": [a.findtext(ATOM + "name", "") for a in e.findall(ATOM + "author")],
            "year": int(e.findtext(ATOM + "published", "0000")[:4] or 0),
            "venue": e.findtext(ARXIV + "journal_ref") or "arXiv",
            "cited_by": None,
            "abstract": " ".join(e.findtext(ATOM + "summary", "").split()),
            "url": f"https://arxiv.org/abs/{base}",
            "oa_url": f"https://arxiv.org/html/{aid}",
            "query": query,
        })
    time.sleep(3)  # arXiv asks for ~1 request / 3 s
    return out


def search_arxiv_web(query: str, n: int) -> list[dict]:
    """Scrape arxiv.org/search (relevance order). Needs beautifulsoup4."""
    from bs4 import BeautifulSoup  # optional dependency
    url = (f"https://arxiv.org/search/?query={urllib.parse.quote(chr(34) + query + chr(34))}"
           f"&searchtype=all&abstracts=show&order=&size={next(s for s in (25, 50, 100, 200) if s >= min(n, 200))}")
    soup = BeautifulSoup(get(url).decode("utf-8", "ignore"), "html.parser")
    out = []
    for li in soup.select("li.arxiv-result"):
        a = li.select_one("p.list-title a")
        if not a:
            continue
        aid = a.get_text(strip=True).replace("arXiv:", "")
        base = re.sub(r"v\d+$", "", aid)
        title = " ".join(li.select_one("p.title").get_text(" ", strip=True).split())
        authors = [x.get_text(strip=True) for x in li.select("p.authors a")]
        abs_el = li.select_one("span.abstract-full") or li.select_one("span.abstract-short")
        abstract = " ".join(abs_el.get_text(" ", strip=True).split()) if abs_el else ""
        abstract = re.sub(r"\s*(△ Less|▽ More)\s*$", "", abstract)
        m = re.search(r"Submitted\s+\d+\s+\w+,?\s+(\d{4})", li.get_text(" ", strip=True))
        year = int(m.group(1)) if m else 0
        jref = li.select_one("p.comments .has-text-black-bis")
        doi_el = li.select_one("div.tags + div a[href*='doi.org']") or li.select_one("a[href*='doi.org']")
        doi = doi_el["href"].split("doi.org/")[-1].lower() if doi_el else None
        out.append({
            "source": "arxiv", "id": f"arxiv:{base}", "arxiv_id": base, "doi": doi,
            "title": title, "authors": authors, "year": year,
            "venue": "arXiv",
            "cited_by": None, "abstract": abstract,
            "url": f"https://arxiv.org/abs/{base}", "oa_url": f"https://arxiv.org/html/{aid}",
            "query": query,
        })
    time.sleep(3)
    return out


def search_crossref(query: str, n: int) -> list[dict]:
    url = (f"https://api.crossref.org/works?query.bibliographic={urllib.parse.quote(query)}"
           f"&rows={n}"  # relevance order; rank by citations locally
           "&select=DOI,title,author,issued,container-title,is-referenced-by-count,"
           "abstract,URL,link,license,type")
    items = json.loads(get(url))["message"]["items"]
    out = []
    for it in items:
        if not it.get("title"):
            continue
        year = (it.get("issued", {}).get("date-parts") or [[0]])[0][0] or 0
        oa = None
        for lk in it.get("link", []) or []:
            if lk.get("content-type") in ("application/pdf", "text/html") and \
                    lk.get("intended-application") == "text-mining":
                oa = lk.get("URL")
                break
        out.append({
            "source": "crossref", "id": f"doi:{it['DOI'].lower()}", "arxiv_id": None,
            "doi": it["DOI"].lower(),
            "title": " ".join(it["title"][0].split()),
            "authors": [f"{a.get('given', '')} {a.get('family', '')}".strip()
                        for a in it.get("author", [])],
            "year": int(year),
            "venue": (it.get("container-title") or [""])[0],
            "cited_by": it.get("is-referenced-by-count"),
            "abstract": re.sub(r"<[^>]+>", "", it.get("abstract", "") or ""),
            "url": it.get("URL"),
            "oa_url": oa,
            "type": it.get("type"),
            "query": query,
        })
    time.sleep(1)
    return out


def search_openalex(query: str, n: int) -> list[dict]:
    url = (f"https://api.openalex.org/works?search={urllib.parse.quote(query)}"
           f"&per-page={n}&sort=cited_by_count:desc&filter=is_oa:true"
           "&select=id,doi,title,authorships,publication_year,primary_location,"
           "cited_by_count,open_access,ids")
    items = json.loads(get(url))["results"]
    out = []
    for it in items:
        ids = it.get("ids", {})
        arx = ids.get("arxiv") or None
        doi = (it.get("doi") or "").replace("https://doi.org/", "").lower() or None
        out.append({
            "source": "openalex", "id": it["id"], "arxiv_id": arx,
            "doi": doi, "title": it.get("title") or "",
            "authors": [a["author"]["display_name"] for a in it.get("authorships", [])],
            "year": it.get("publication_year") or 0,
            "venue": ((it.get("primary_location") or {}).get("source") or {}).get("display_name", ""),
            "cited_by": it.get("cited_by_count"),
            "abstract": "",
            "url": it.get("doi") or it["id"],
            "oa_url": (it.get("open_access") or {}).get("oa_url"),
            "query": query,
        })
    time.sleep(1)
    return out


def search_openaire(query: str, n: int) -> list[dict]:
    """OpenAIRE Graph API: open-access publications whose title has the phrase,
    most cited first. https://graph.openaire.eu/docs/apis/graph-api/"""
    url = ("https://api.openaire.eu/graph/v1/researchProducts?type=publication"
           f"&mainTitle={urllib.parse.quote(chr(34) + query + chr(34))}"
           "&bestOpenAccessRightLabel=OPEN&sortBy=citationCount%20DESC"
           f"&pageSize={min(n, 100)}")
    data = json.loads(get(url))
    out = []
    for it in data.get("results", []):
        pids = {p["scheme"]: p["value"] for p in reversed(it.get("pids") or [])}
        doi = (pids.get("doi") or "").lower() or None
        arx = pids.get("arxiv") or pids.get("arXiv")
        if not arx:
            for inst in it.get("instances") or []:
                for u in inst.get("urls") or []:
                    m = re.search(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})", u)
                    if m:
                        arx = m.group(1)
        urls, lic = [], None
        for inst in it.get("instances") or []:
            lic = lic or inst.get("license")
            for u in inst.get("urls") or []:
                if u not in urls:
                    urls.append(u)
        pdfs = [u for u in urls if u.lower().endswith(".pdf") or "/pdf" in u.lower()]
        year = int((it.get("publicationDate") or "0")[:4] or 0)
        cit = ((it.get("indicators") or {}).get("citationImpact") or {}).get("citationCount")
        out.append({
            "source": "openaire", "id": it["id"], "arxiv_id": arx, "doi": doi,
            "title": " ".join((it.get("mainTitle") or "").split()),
            "authors": [a.get("fullName", "") for a in it.get("authors") or []],
            "year": year, "venue": (it.get("container") or {}).get("name") or "",
            "cited_by": int(cit) if cit is not None else None,
            "abstract": " ".join((it.get("descriptions") or [""])[0].split())[:3000],
            "url": f"https://doi.org/{doi}" if doi else (urls[0] if urls else None),
            "oa_url": (f"https://arxiv.org/html/{arx}" if arx else (pdfs[0] if pdfs else (urls[0] if urls else None))),
            "all_urls": urls[:8], "license": lic, "query": query,
        })
    time.sleep(1)
    return out


SOURCES = {"arxiv": search_arxiv, "arxiv_web": search_arxiv_web,
           "crossref": search_crossref, "openalex": search_openalex,
           "openaire": search_openaire}


# ---------------------------------------------------------------- commands
def cmd_search(a) -> int:
    recs: list[dict] = []
    for src in a.source:
        for q in a.query:
            try:
                hits = SOURCES[src](q, a.n)
            except Exception as e:  # keep going; report at the end
                print(f"[{src}] {q!r}: {e}", file=sys.stderr)
                continue
            print(f"[{src}] {q!r}: {len(hits)} hits", file=sys.stderr)
            recs.extend(hits)
    Path(a.out).write_text(json.dumps(recs, indent=1, ensure_ascii=False))
    print(f"wrote {len(recs)} records to {a.out}")
    return 0


def cmd_existing(a) -> int:
    """Collect identifiers of everything already under raw/."""
    import subprocess
    raw = Path(a.root) / "raw"
    rows = []
    for p in sorted(raw.iterdir()):
        if p.name == "README.md" or p.name.endswith(".meta.md"):
            continue
        rec = {"file": p.name, "titles": [], "doi": None, "arxiv_id": None}
        head = ""
        if p.suffix == ".pdf":
            info = subprocess.run(["pdfinfo", str(p)], capture_output=True, text=True).stdout
            m = re.search(r"^Title:\s*(.+)$", info, re.M)
            if m:
                rec["titles"].append(m.group(1).strip())
            head = subprocess.run(["pdftotext", "-l", "2", str(p), "-"],
                                  capture_output=True, text=True).stdout
            rec["titles"].append(" ".join(head.split()[:25]))
        else:
            head = p.read_text(errors="ignore")[:4000]
            m = re.search(r"^title:\s*(.+)$", head, re.M)
            if m:
                rec["titles"].append(m.group(1).strip())
        meta = p.with_suffix(p.suffix + ".meta.md")
        if meta.exists():
            m = re.search(r"^title:\s*(.+)$", meta.read_text(), re.M)
            if m:
                rec["titles"].append(m.group(1).strip())
        m = re.search(r"arXiv:(\d{4}\.\d{4,5})", head)
        if m:
            rec["arxiv_id"] = m.group(1)
        m = re.search(r"(\d{4}\.\d{4,5})", p.name)
        if m and not rec["arxiv_id"]:
            rec["arxiv_id"] = m.group(1)
        m = re.search(r"\b(10\.\d{4,9}/[^\s\"<>]+)", head)
        if m:
            rec["doi"] = m.group(1).rstrip(".,;)").lower()
        rec["norm"] = [norm_title(t) for t in rec["titles"] if t]
        rows.append(rec)
    Path(a.out).write_text(json.dumps(rows, indent=1, ensure_ascii=False))
    print(f"wrote {len(rows)} existing records to {a.out}")
    return 0


def _title_match(nt: str, existing_norms: list[str]) -> bool:
    if not nt or len(nt) < 15:
        return False
    for en in existing_norms:
        if nt == en or nt in en or (len(en) > 15 and en in nt):
            return True
    return False


def cmd_dedupe(a) -> int:
    cands = json.loads(Path(a.candidates).read_text())
    existing = json.loads(Path(a.existing).read_text())
    ex_norms = [n for r in existing for n in r["norm"]]
    ex_dois = {r["doi"] for r in existing if r.get("doi")}
    ex_arx = {r["arxiv_id"] for r in existing if r.get("arxiv_id")}
    seen: dict[str, dict] = {}
    dropped = 0
    for c in cands:
        nt = norm_title(c["title"])
        if (c.get("doi") in ex_dois) or (c.get("arxiv_id") in ex_arx) or _title_match(nt, ex_norms):
            dropped += 1
            c["dup_of_raw"] = True
            continue
        key = c.get("arxiv_id") or c.get("doi") or nt
        # also merge arXiv and DOI records of the same title
        by_title = {norm_title(v["title"]): k for k, v in seen.items()}
        key = by_title.get(nt, key)
        if key in seen:
            prev = seen[key]
            prev.setdefault("queries", []).append(c.get("query"))
            if prev.get("cited_by") is None and c.get("cited_by") is not None:
                prev["cited_by"] = c["cited_by"]
            if not prev.get("doi") and c.get("doi"):
                prev["doi"] = c["doi"]
            if not prev.get("arxiv_id") and c.get("arxiv_id"):
                prev["arxiv_id"], prev["oa_url"] = c["arxiv_id"], c["oa_url"]
            if not prev.get("abstract") and c.get("abstract"):
                prev["abstract"] = c["abstract"]
            continue
        c["queries"] = [c.pop("query", None)]
        seen[key] = c
    out = list(seen.values())
    Path(a.out).write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(f"{len(cands)} candidates -> {len(out)} unique new ({dropped} already in raw/)")
    return 0


def cmd_rank(a) -> int:
    recs = json.loads(Path(a.candidates).read_text())
    recent = [r for r in recs if r.get("year", 0) >= a.since]
    classics = [r for r in recs if 0 < r.get("year", 0) < a.since]
    key = lambda r: (r.get("cited_by") or 0, r.get("year", 0))
    recent.sort(key=key, reverse=True)
    classics.sort(key=key, reverse=True)
    for label, rows, n in (("CLASSICS", classics, a.classics), ("RECENT", recent, a.recent)):
        print(f"\n== {label} (top {n} of {len(rows)})")
        for r in rows[:n]:
            print(f"{r.get('cited_by') or '-':>6}  {r.get('year')}  {r['title'][:90]}  "
                  f"[{r.get('arxiv_id') or r.get('doi') or r['id']}]")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search"); s.add_argument("-q", "--query", action="append", required=True)
    s.add_argument("--source", action="append", choices=SOURCES, default=None)
    s.add_argument("-n", type=int, default=40); s.add_argument("--out", required=True)
    s.set_defaults(fn=cmd_search)
    e = sub.add_parser("existing"); e.add_argument("--root", default=".")
    e.add_argument("--out", required=True); e.set_defaults(fn=cmd_existing)
    d = sub.add_parser("dedupe"); d.add_argument("candidates"); d.add_argument("existing")
    d.add_argument("--out", required=True); d.set_defaults(fn=cmd_dedupe)
    r = sub.add_parser("rank"); r.add_argument("candidates")
    r.add_argument("--classics", type=int, default=25); r.add_argument("--recent", type=int, default=25)
    r.add_argument("--since", type=int, default=2023); r.set_defaults(fn=cmd_rank)
    a = ap.parse_args(argv)
    if a.cmd == "search" and not a.source:
        a.source = ["arxiv", "crossref"]
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
