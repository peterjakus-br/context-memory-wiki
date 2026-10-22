#!/usr/bin/env python3
"""Download selected open-access papers into raw/ via add_source.py.

Input is a JSON list of records (the output of find_papers.py, optionally
hand-trimmed). For each record it tries, in order:

  1. arXiv HTML (arxiv.org/html/<id>, then ar5iv.labs.arxiv.org/html/<id>)
     -> converted to Markdown with pandoc, saved as raw/<date>-<slug>.md
  2. Europe PMC full text (JATS XML, looked up by DOI) -> Markdown via pandoc
  3. a PDF at oa_url / all_urls / arxiv.org/pdf/<id> -> raw/<date>-<slug>.pdf
     (landing pages are scanned for a citation_pdf_url / .pdf link)

Only LaTeXML pages (arXiv, ar5iv) are converted from HTML: publisher landing
pages look like full text to a generic extractor but are not.

Markdown is preferred because the wiki's ingest step reads Markdown directly;
a PDF needs the pdf-to-markdown skill first. The origin URL and the licence
are recorded in the file header (or the .meta.md sidecar for PDFs).

    python3 scripts/fetch_papers.py selected.json [--date YYYY-MM-DD] [--dry-run]
    python3 scripts/fetch_papers.py selected.json --only arxiv:2407.11417

Needs: pandoc, beautifulsoup4 (for HTML cleanup). Stdlib otherwise.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import time
import urllib.request
from datetime import date
from pathlib import Path

UA = "context-memory-wiki-fetch-papers/0.1 (+https://github.com/peterjakus-br/context-memory-wiki)"
ROOT = Path(__file__).resolve().parent.parent


def fetch(url: str, timeout: int = 90) -> tuple[bytes, str, str]:
    """Return (body, content_type, final_url)."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/pdf,*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), r.headers.get("Content-Type", ""), r.geturl()


def slugify(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return re.sub(r"-{2,}", "-", s)


def html_to_markdown(html: str) -> str | None:
    """Keep only the LaTeXML article body of an arXiv/ar5iv page, strip chrome,
    and convert with pandoc to GFM. Returns None for anything that is not a
    rendered paper (error pages, abstract pages, publisher landing pages)."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    body = soup.select_one("article.ltx_document") or soup.select_one("div.ltx_document") \
        or soup.select_one("article .ltx_page_content") or soup.select_one(".ltx_page_main")
    if body is None or len(body.get_text(" ", strip=True)) < 3000:
        return None  # error page or abstract-only page
    for t in body.select("script, style, nav, header, footer, .ltx_page_navbar, .ltx_page_footer, "
                         ".package-alerts, .ltx_note_outer, .ltx_role_footnote, #footer, .ltx_tocentry, "
                         ".ltx_bibliography .ltx_bibitem .ltx_tag"):
        t.decompose()
    for sp in body.find_all("span"):
        sp.unwrap()
    md = subprocess.run(["pandoc", "-f", "html", "-t", "gfm-raw_html", "--wrap=none"],
                        input=str(body), capture_output=True, text=True, check=True).stdout
    md = re.sub(r"!\[[^\]]*\]\(data:[^)]*\)", "", md)  # inline icons (ORCID badges etc.)
    md = re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"
    return md if len(md) > 3000 else None


def try_html(url: str) -> str | None:
    try:
        body, ctype, final = fetch(url)
    except Exception as e:
        print(f"    html {url}: {e}", file=sys.stderr)
        return None
    if "html" not in ctype.lower() or "arxiv.org/abs/" in final:
        return None  # ar5iv redirects to the abstract page when it has no render
    text = body.decode("utf-8", "ignore")
    if "No HTML for" in text[:20000] and "arxiv.org" in url:
        return None
    return html_to_markdown(text)


def try_epmc(doi: str | None) -> tuple[str, str] | None:
    """Europe PMC: DOI -> PMCID -> JATS full text -> Markdown. Returns (md, url)."""
    if not doi:
        return None
    import urllib.parse
    q = urllib.parse.quote(f"DOI:{doi}")
    try:
        body, _, _ = fetch(f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={q}&format=json&resultType=lite")
        hits = json.loads(body)["resultList"]["result"]
        pmc = next((h["pmcid"] for h in hits if h.get("pmcid") and h.get("isOpenAccess") == "Y"), None)
        if not pmc:
            return None
        url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextXML"
        xml, _, _ = fetch(url)
    except Exception as e:
        print(f"    epmc {doi}: {e}", file=sys.stderr)
        return None
    if b"<article" not in xml[:2000]:
        return None
    md = subprocess.run(["pandoc", "-f", "jats", "-t", "gfm-raw_html", "--wrap=none"],
                        input=xml, capture_output=True, check=True).stdout.decode("utf-8", "ignore")
    md = re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"
    return (md, url) if len(md) > 3000 else None


def try_pdf(url: str) -> bytes | None:
    try:
        body, ctype, final = fetch(url)
    except Exception as e:
        print(f"    pdf {url}: {e}", file=sys.stderr)
        return None
    if body[:5] == b"%PDF-":
        return body
    if "html" in ctype.lower():  # landing page: look for a PDF link
        m = re.search(r'(?:citation_pdf_url"\s+content=|href=)"([^"]+\.pdf[^"]*)"', body.decode("utf-8", "ignore"))
        if m:
            u = m.group(1)
            if u.startswith("/"):
                from urllib.parse import urljoin
                u = urljoin(final, u)
            try:
                body2, _, _ = fetch(u)
                if body2[:5] == b"%PDF-":
                    return body2
            except Exception as e:
                print(f"    pdf {u}: {e}", file=sys.stderr)
    return None


def candidate_urls(rec: dict) -> tuple[list[str], list[str]]:
    html, pdf = [], []
    arx = rec.get("arxiv_id")
    if arx:
        html += [f"https://arxiv.org/html/{arx}", f"https://ar5iv.labs.arxiv.org/html/{arx}"]
        pdf += [f"https://arxiv.org/pdf/{arx}"]
    for u in [rec.get("oa_url")] + list(rec.get("all_urls") or []) + [rec.get("url")]:
        if not u or "arxiv.org" in u or "doi.org/10.48550" in u or "dblp.org" in u:
            continue
        pdf.append(u)  # direct PDFs first, landing pages are scanned for a PDF link
    pdf.sort(key=lambda u: 0 if (".pdf" in u.lower() or "/pdf" in u.lower()) else 1)
    dedup = lambda xs: list(dict.fromkeys(xs))
    return dedup(html), dedup(pdf)


def add_source(path: Path, title: str, url: str, when: str, slug: str) -> bool:
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "add_source.py"), str(path),
                        "--title", title, "--url", url, "--date", when, "--slug", slug, "--root", str(ROOT)],
                       capture_output=True, text=True)
    print("    " + (r.stdout.strip().splitlines() or [""])[0] + (r.stderr.strip() and "  " + r.stderr.strip()))
    return r.returncode == 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("selected")
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", action="append", help="record id(s) to process")
    ap.add_argument("--report", help="write a JSON report of what was saved where")
    a = ap.parse_args(argv)

    recs = json.loads(Path(a.selected).read_text())
    if a.only:
        recs = [r for r in recs if r.get("id") in a.only]
    report = []
    for i, rec in enumerate(recs, 1):
        title = rec["title"]
        slug = rec.get("slug") or slugify(title)
        if len(slug) > 80:  # cut at a word boundary
            slug = slug[:80].rsplit("-", 1)[0]
        print(f"[{i}/{len(recs)}] {title[:80]}")
        html_urls, pdf_urls = candidate_urls(rec)
        entry = {"id": rec.get("id"), "title": title, "slug": slug, "saved": None, "format": None, "origin": None}
        if a.dry_run:
            print("    html:", html_urls, "\n    pdf:", pdf_urls)
            continue
        if any((ROOT / "raw").glob(f"*-{slug}.*")):
            print("    already in raw/, skipping")
            entry["saved"] = "exists"
            report.append(entry)
            continue
        with tempfile.TemporaryDirectory() as td:
            done = False
            for u in html_urls:
                md = try_html(u)
                if md:
                    extra = f"licence: {rec['license']}\n" if rec.get("license") else ""
                    body = (f"<!-- doi: {rec.get('doi')} | arxiv: {rec.get('arxiv_id')} | "
                            f"year: {rec.get('year')} | venue: {rec.get('venue')} | "
                            f"converted-from: {u} (HTML -> Markdown via pandoc) -->\n{extra}\n" + md)
                    p = Path(td) / f"{slug}.md"
                    p.write_text(body, encoding="utf-8")
                    if add_source(p, title, rec.get("url") or u, a.date, slug):
                        entry.update(saved=f"raw/{a.date}-{slug}.md", format="md", origin=u)
                        done = True
                    break
            if not done:
                got = try_epmc(rec.get("doi"))
                if got:
                    md, u = got
                    head = f"# {title}\n\n" + ", ".join(rec.get("authors") or []) + "\n\n"
                    body = (f"<!-- doi: {rec.get('doi')} | year: {rec.get('year')} | venue: {rec.get('venue')} | "
                            f"converted-from: {u} (Europe PMC JATS XML -> Markdown via pandoc) -->\n\n" + head + md)
                    p = Path(td) / f"{slug}.md"
                    p.write_text(body, encoding="utf-8")
                    if add_source(p, title, rec.get("url") or u, a.date, slug):
                        entry.update(saved=f"raw/{a.date}-{slug}.md", format="md", origin=u)
                        done = True
            if not done:
                for u in pdf_urls:
                    pdf = try_pdf(u)
                    if pdf:
                        p = Path(td) / f"{slug}.pdf"
                        p.write_bytes(pdf)
                        if add_source(p, title, rec.get("url") or u, a.date, slug):
                            entry.update(saved=f"raw/{a.date}-{slug}.pdf", format="pdf", origin=u)
                            done = True
                        break
            if not done:
                print("    FAILED: no usable full text found")
        report.append(entry)
        time.sleep(1.5)
    if a.report:
        Path(a.report).write_text(json.dumps(report, indent=1, ensure_ascii=False))
    ok = sum(1 for e in report if e["saved"])
    print(f"\nsaved {ok}/{len(report)}")
    return 0 if ok == len(report) else 1


if __name__ == "__main__":
    sys.exit(main())
