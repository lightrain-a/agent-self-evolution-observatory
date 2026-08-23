from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from .paper_venue_compliance_projection import add_ai_use_statement_projection, validate_projection_receipt


STATEMENT = r"""\section*{AI Use Statement}
AI tools assisted literature triage and manuscript editing. The authors reviewed the final content.
"""


class PaperVenueComplianceProjectionTest(unittest.TestCase):
    def source(self, root: Path, *, existing_ai: bool = False) -> Path:
        path = root / "source.zip"
        with zipfile.ZipFile(path, "w") as z:
            main = "\\title{Paper}\n\\begin{document}\n"
            if existing_ai:
                main += "\\section*{AI Use Statement}Already present.\n"
            main += "\\bibliography{references}\n\\end{document}\n"
            z.writestr("main.tex", main)
            z.writestr("references.bib", "")
        return path

    def test_projection_is_deterministic_and_only_adds_disclosure(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = self.source(root)
            first = root / "a.zip"
            second = root / "b.zip"
            r1 = add_ai_use_statement_projection(paper_id="P", source_zip=source, output_zip=first, statement_text=STATEMENT)
            r2 = add_ai_use_statement_projection(paper_id="P", source_zip=source, output_zip=second, statement_text=STATEMENT)
            self.assertTrue(validate_projection_receipt(r1))
            self.assertEqual(r1["projected_sha256"], r2["projected_sha256"])
            self.assertTrue(r1["canonical_scientific_artifacts_unchanged"])
            self.assertEqual([x["entry"] for x in r1["changed_entries"]], ["main.tex", "sections/08_ai_use_statement.tex"])
            with zipfile.ZipFile(first) as z:
                main = z.read("main.tex").decode()
                statement = z.read("sections/08_ai_use_statement.tex").decode()
                self.assertLess(main.index("\\input{sections/08_ai_use_statement}"), main.index("\\bibliography"))
                self.assertIn("AI Use Statement", statement)

    def test_projection_never_overwrites_source_or_duplicates_ai_section(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = self.source(root)
            with self.assertRaisesRegex(RuntimeError, "must not overwrite"):
                add_ai_use_statement_projection(paper_id="P", source_zip=source, output_zip=source, statement_text=STATEMENT)
            existing_root = root / "existing"
            existing_root.mkdir()
            existing = self.source(existing_root, existing_ai=True)
            with self.assertRaisesRegex(RuntimeError, "already contains"):
                add_ai_use_statement_projection(paper_id="P", source_zip=existing, output_zip=root / "out.zip", statement_text=STATEMENT)


if __name__ == "__main__":
    unittest.main()
