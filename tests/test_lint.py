"""Tests for scripts/lint.py. Run: python3 -m unittest discover -s tests"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import lint  # noqa: E402

TODAY = "2026-01-01"


def fm(**kw):
    lines = ["---"]
    for k, v in kw.items():
        if isinstance(v, list):
            v = "[" + ", ".join(v) + "]"
        lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines) + "\n"


class WikiFixture:
    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for d in ("raw", "wiki/sources", "wiki/entities", "wiki/concepts",
                  "wiki/synthesis"):
            (self.root / d).mkdir(parents=True)
        self.write("raw/2026-01-01-a.md", "# A\n")
        self.write("wiki/sources/a.md", fm(title="A", type="source", created=TODAY,
                                          updated=TODAY, source="raw/2026-01-01-a.md")
                   + "## Summary\nSee [[thing]].\n")
        self.write("wiki/concepts/thing.md", fm(title="Thing", type="concept",
                                               created=TODAY, updated=TODAY,
                                               sources=["a"], confidence="high")
                   + "A thing ([[a]]).\n")
        self.write("wiki/overview.md", fm(title="Overview", type="overview",
                                         created=TODAY, updated=TODAY)
                   + "[[thing]] from [[a]].\n")
        self.write("wiki/index.md", "# Index\n\n## Sources\n| [[a]] | A |\n\n"
                   "## Concepts\n| [[thing]] | T |\n\n[[overview]]\n\n## Unprocessed\n")
        self.write("wiki/log.md", "# Log\n\n## [2026-01-01] ingest | A\n- read raw\n")

    def write(self, rel, text):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def run(self):
        return lint.run(self.root)

    def cleanup(self):
        self.tmp.cleanup()


class LintTests(unittest.TestCase):
    def setUp(self):
        self.w = WikiFixture()
        self.addCleanup(self.w.cleanup)

    def test_clean_wiki_passes(self):
        rep = self.w.run()
        self.assertEqual(rep.errors, [])
        self.assertEqual(rep.warnings, [])

    def test_broken_wikilink(self):
        self.w.write("wiki/concepts/thing.md",
                     fm(title="Thing", type="concept", created=TODAY, updated=TODAY,
                        sources=["a"], confidence="high") + "See [[nope|alias]].\n")
        rep = self.w.run()
        self.assertTrue(any("broken wikilink [[nope]]" in e for e in rep.errors))

    def test_links_in_code_are_ignored(self):
        self.w.write("wiki/concepts/thing.md",
                     fm(title="Thing", type="concept", created=TODAY, updated=TODAY,
                        sources=["a"], confidence="high")
                     + "([[a]])\n```\n[[not-a-page]]\n```\nand `[[also-not]]`\n")
        rep = self.w.run()
        self.assertFalse(any("broken" in e for e in rep.errors))

    def test_missing_frontmatter_and_type_mismatch(self):
        self.w.write("wiki/entities/x.md", "no frontmatter\n")
        self.w.write("wiki/entities/y.md", fm(title="Y", type="concept", created=TODAY,
                                             updated=TODAY) + "[[a]]\n")
        self.w.write("wiki/index.md", "[[a]] [[thing]] [[overview]] [[x]] [[y]]\n\n## Unprocessed\n")
        rep = self.w.run()
        self.assertTrue(any("entities/x.md: missing frontmatter" in e for e in rep.errors))
        self.assertTrue(any("entities/y.md: type 'concept' does not match" in e
                            for e in rep.errors))

    def test_orphan_warning(self):
        self.w.write("wiki/concepts/lonely.md",
                     fm(title="Lonely", type="concept", created=TODAY, updated=TODAY,
                        sources=["a"], confidence="low") + "text\n")
        self.w.write("wiki/index.md", "[[a]] [[thing]] [[overview]] [[lonely]]\n\n## Unprocessed\n")
        rep = self.w.run()
        self.assertTrue(any("lonely.md: orphan" in w for w in rep.warnings))

    def test_index_coverage(self):
        self.w.write("wiki/index.md", "[[a]] [[overview]]\n\n## Unprocessed\n")
        rep = self.w.run()
        self.assertTrue(any("does not list concepts/thing.md" in e for e in rep.errors))

    def test_uningested_raw_file(self):
        self.w.write("raw/2026-01-02-b.pdf", "x")
        rep = self.w.run()
        self.assertTrue(any("raw/2026-01-02-b.pdf: not ingested and not listed" in w
                            for w in rep.warnings))
        self.w.write("wiki/index.md", "[[a]] [[thing]] [[overview]]\n\n## Unprocessed\n"
                     "- `raw/2026-01-02-b.pdf`\n")
        rep = self.w.run()
        self.assertTrue(any("listed under Unprocessed" in w for w in rep.warnings))

    def test_binary_source_companions_are_not_flagged(self):
        self.w.write("raw/2026-01-02-b.pdf", "x")
        self.w.write("raw/2026-01-02-b.pdf.meta.md", "sidecar")
        self.w.write("raw/2026-01-02-b.md", "converted")
        self.w.write("raw/2026-01-02-b_images/fig-001.png", "png")
        self.w.write("raw/2026-01-02-bother.md", "a different source")
        self.w.write("wiki/sources/b.md", fm(title="B", type="source", created=TODAY,
                                            updated=TODAY, tags=["x"],
                                            source="raw/2026-01-02-b.pdf") + "text\n")
        self.w.write("wiki/index.md", "[[a]] [[b]] [[thing]] [[overview]]\n\n## Unprocessed\n")
        rep = self.w.run()
        flagged = [w for w in rep.warnings if "2026-01-02-b" in w]
        self.assertEqual(len(flagged), 1, flagged)
        self.assertIn("2026-01-02-bother.md", flagged[0])

    def test_unprocessed_binary_source_companions_are_not_flagged(self):
        self.w.write("raw/2026-01-02-b.pdf", "x")
        self.w.write("raw/2026-01-02-b.md", "converted")
        self.w.write("raw/2026-01-02-b_images/fig-001.png", "png")
        self.w.write("wiki/index.md", "[[a]] [[thing]] [[overview]]\n\n## Unprocessed\n"
                     "- `raw/2026-01-02-b.pdf`\n")
        rep = self.w.run()
        flagged = [w for w in rep.warnings if "2026-01-02-b" in w]
        self.assertEqual(len(flagged), 1, flagged)
        self.assertIn("listed under Unprocessed", flagged[0])

    def test_repo_snapshot_directory_is_companion_of_manifest(self):
        self.w.write("raw/repos/2026-01-02-o-r.md", "manifest")
        self.w.write("raw/repos/2026-01-02-o-r/src/main.py", "code")
        self.w.write("raw/repos/2026-01-02-o-rx/other.py", "not a companion")
        self.w.write("wiki/sources/r.md", fm(title="R", type="source", created=TODAY,
                                            updated=TODAY, tags=["x"],
                                            source="raw/repos/2026-01-02-o-r.md") + "text\n")
        self.w.write("wiki/index.md", "[[a]] [[r]] [[thing]] [[overview]]\n\n## Unprocessed\n")
        rep = self.w.run()
        flagged = [w for w in rep.warnings if "2026-01-02-o-r" in w]
        self.assertEqual(len(flagged), 1, flagged)
        self.assertIn("2026-01-02-o-rx/other.py", flagged[0])

    def test_ingested_but_still_unprocessed_is_error(self):
        self.w.write("wiki/index.md", "[[a]] [[thing]] [[overview]]\n\n## Unprocessed\n"
                     "- raw/2026-01-01-a.md\n")
        rep = self.w.run()
        self.assertTrue(any("still listed under" in e for e in rep.errors))

    def test_duplicate_slug(self):
        self.w.write("wiki/entities/thing.md", fm(title="T", type="entity", created=TODAY,
                                                 updated=TODAY, sources=["a"]) + "[[a]]\n")
        rep = self.w.run()
        self.assertTrue(any("duplicate slug 'thing'" in e for e in rep.errors))

    def test_stale_page(self):
        self.w.write("wiki/sources/a.md", fm(title="A", type="source", created=TODAY,
                                            updated="2026-02-01",
                                            source="raw/2026-01-01-a.md") + "[[thing]]\n")
        rep = self.w.run()
        self.assertTrue(any("thing.md: possibly stale" in w for w in rep.warnings))

    def test_log_format(self):
        self.w.write("wiki/log.md", "## 2026-01-01 ingest A\n## [2026-01-01] dance | x\n")
        rep = self.w.run()
        self.assertTrue(any("log.md:1" in e for e in rep.errors))
        self.assertTrue(any("unknown operation 'dance'" in e for e in rep.errors))

    def test_missing_source_path(self):
        self.w.write("wiki/sources/a.md", fm(title="A", type="source", created=TODAY,
                                            updated=TODAY, source="raw/missing.md")
                     + "[[thing]]\n")
        rep = self.w.run()
        self.assertTrue(any("source path does not exist" in e for e in rep.errors))

    def test_sources_field_must_point_to_source_page(self):
        self.w.write("wiki/concepts/thing.md",
                     fm(title="Thing", type="concept", created=TODAY, updated=TODAY,
                        sources=["ghost"], confidence="high") + "[[a]]\n")
        rep = self.w.run()
        self.assertTrue(any("sources entry 'ghost' is not a wiki page" in e
                            for e in rep.errors))


class FrontmatterParserTests(unittest.TestCase):
    def test_lists_and_quotes(self):
        text = '---\ntitle: "Hi: there"\ntags: [a, b]\nsources:\n  - x\n  - y\n---\nbody\n'
        front, body = lint.parse_frontmatter(text)
        self.assertEqual(front["title"], "Hi: there")
        self.assertEqual(front["tags"], ["a", "b"])
        self.assertEqual(front["sources"], ["x", "y"])
        self.assertEqual(body, "body\n")

    def test_no_frontmatter(self):
        front, body = lint.parse_frontmatter("# just text\n")
        self.assertIsNone(front)
        self.assertEqual(body, "# just text\n")


if __name__ == "__main__":
    unittest.main()
