from __future__ import annotations

import unittest

from .config import PROJECT_ROOT
from .reproduction_gate import (
    build_reproduction_contract,
    evaluate_reproduction_contract,
    reproduction_from_candidate,
    run_three_case_local_falsifier,
)


class ReproductionGateTest(unittest.TestCase):
    def test_not_required_by_default(self) -> None:
        contract, audit = reproduction_from_candidate({"candidate_id": "C1"})
        self.assertFalse(contract["implementation_decisive_for_novelty"])
        self.assertEqual(audit["status"], "NOT_REQUIRED")
        self.assertTrue(audit["qualification_satisfied"])
        self.assertFalse(audit["scientific_authority"])

    def test_decisive_implementation_without_receipt_holds(self) -> None:
        contract = build_reproduction_contract(
            candidate_id="C1", implementation_decisive_for_novelty=True,
            paper_ref="arXiv:1", question="Does implementation change the treatment?",
            minimal_target="inspect or minimally execute the decisive path",
            verification_mode="SOURCE_INSPECTION", source_faithful_assets_available=True,
        )
        audit = evaluate_reproduction_contract(contract)
        self.assertEqual(audit["status"], "HOLD_REPRODUCTION_REQUIRED")
        self.assertFalse(audit["qualification_satisfied"])

    def test_missing_source_faithful_assets_is_support_hold(self) -> None:
        contract = build_reproduction_contract(
            candidate_id="C1", implementation_decisive_for_novelty=True,
            paper_ref="arXiv:1", question="Can the paper treatment be reproduced?",
            minimal_target="source-faithful trained object", verification_mode="MINIMAL_EXECUTION",
            source_faithful_assets_available=False, artifact_refs=["audit.json"],
        )
        audit = evaluate_reproduction_contract(contract)
        self.assertEqual(audit["status"], "HOLD_SOURCE_FAITHFUL_ASSETS_UNAVAILABLE")
        self.assertTrue(audit["support_hold"])
        self.assertFalse(audit["scientific_authority"])

    def test_source_inspection_can_sharpen_structural_boundary(self) -> None:
        contract = build_reproduction_contract(
            candidate_id="C1", implementation_decisive_for_novelty=True,
            paper_ref="arXiv:1", implementation_ref="repo:abc", question="Who performs constraint construction?",
            minimal_target="inspect released path", verification_mode="SOURCE_INSPECTION",
            source_faithful_assets_available=True, artifact_refs=["repo:abc:file.py"], result="SHARPENED_BOUNDARY",
        )
        audit = evaluate_reproduction_contract(contract)
        self.assertEqual(audit["status"], "REPRODUCTION_SHARPENED_BOUNDARY")
        self.assertTrue(audit["qualification_satisfied"])
        self.assertFalse(audit["machine_actionable"])

    def test_three_real_cases_cover_sharpen_and_support_hold_without_full_training(self) -> None:
        replay = run_three_case_local_falsifier(PROJECT_ROOT)
        self.assertEqual(replay["status"], "PASS")
        self.assertEqual(replay["cases"], 3)
        self.assertEqual(replay["matched"], 3)
        self.assertEqual(replay["full_retraining_cases"], 0)
        self.assertEqual([r["status"] for r in replay["results"]], [
            "REPRODUCTION_SHARPENED_BOUNDARY",
            "REPRODUCTION_SHARPENED_BOUNDARY",
            "HOLD_SOURCE_FAITHFUL_ASSETS_UNAVAILABLE",
        ])
        self.assertFalse(replay["scientific_authority"])


if __name__ == "__main__":
    unittest.main()
