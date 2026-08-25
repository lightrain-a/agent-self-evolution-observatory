from __future__ import annotations

import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source"
AUDIT = HERE / "closest-work-stress-audit-r3b-20260825.json"


class ClosestWorkBoundaryR3BTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        cls.intro = (SOURCE / "sections" / "01_intro.tex").read_text(encoding="utf-8")
        cls.related = (SOURCE / "sections" / "05_related.tex").read_text(encoding="utf-8")
        cls.abstract = (SOURCE / "sections" / "00_abstract.tex").read_text(encoding="utf-8")
        cls.refs = (SOURCE / "references.bib").read_text(encoding="utf-8")

    def test_audit_is_zero_authority_and_narrows_novelty(self) -> None:
        self.assertEqual(self.audit["status"], "TARGETED_COLLISION_AUDIT_PASSED_WITH_NOVELTY_NARROWING")
        self.assertEqual(len(self.audit["demoted_novelty_claims"]), 3)
        self.assertFalse(self.audit["scientific_authority"])
        self.assertFalse(self.audit["experiment_authority"])
        self.assertFalse(self.audit["claim_expansion_authority"])
        self.assertFalse(self.audit["submission_authority"])

    def test_qcr_is_cited_and_retrieval_use_novelty_is_disclaimed(self) -> None:
        self.assertIn("li2026qcr", self.related)
        self.assertIn("do \\emph{not} claim the retrieval-versus-reuse distinction as novel", self.related)
        self.assertIn("eprint={2608.12847}", self.refs)

    def test_lifecycle_stage_novelty_is_disclaimed(self) -> None:
        self.assertIn("lin2026memorylifecycle", self.related)
        self.assertIn("do not claim that stage names or retrieval-versus-use are new", self.related)
        self.assertIn("eprint={2604.16548}", self.refs)

    def test_intro_claim_is_intervention_specific(self) -> None:
        self.assertIn("same-trajectory stage-resolved intervention", self.intro)
        self.assertIn("hold the source trajectory fixed", self.intro)

    def test_no_first_retrieval_use_claim(self) -> None:
        joined = (self.abstract + "\n" + self.intro).lower()
        forbidden = [
            "first to distinguish retrieval",
            "first work to distinguish retrieval",
            "first to separate retrieval from use",
            "first to separate retrieval from reuse",
        ]
        self.assertFalse(any(x in joined for x in forbidden))


if __name__ == "__main__":
    unittest.main()
