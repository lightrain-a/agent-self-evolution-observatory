from __future__ import annotations

import unittest

from .paper_visual_evidence import build_paper_visual_evidence_portfolio


class PaperVisualEvidencePortfolioTest(unittest.TestCase):
    def test_current_portfolio_exposes_planned_and_completed_visuals_without_authority(self) -> None:
        state = build_paper_visual_evidence_portfolio()
        self.assertEqual(state["status"], "VISUAL_EVIDENCE_PORTFOLIO_READY")
        self.assertEqual(state["summary"]["paper_first_designs"], 4)
        self.assertEqual(state["summary"]["planned_main_visualizations"], 16)
        self.assertEqual(state["summary"]["planned_main_visualizations_per_paper_min"], 4)
        self.assertEqual(state["summary"]["stri_completed_main_visualizations"], 4)
        self.assertEqual(state["summary"]["repair_required"], 0)
        self.assertIn("failure", state["summary"]["main_visual_roles"])
        self.assertFalse(state["scientific_authority"])
        self.assertFalse(any(state["authority"].values()))
        self.assertTrue(all(len(row.get("reviewer_questions") or []) >= 4 for row in state["papers"]))


if __name__ == "__main__":
    unittest.main()
