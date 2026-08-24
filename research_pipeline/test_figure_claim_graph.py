from __future__ import annotations

import copy
import json
import unittest

from .config import PROJECT_ROOT
from .figure_claim_graph import build_figure_claim_graph, writer_claim_surface


class FigureClaimGraphTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state = json.loads((PROJECT_ROOT / "generated" / "asset-first-stri-paper-quality-v2-20260816.json").read_text(encoding="utf-8"))

    def test_stri_compiles_evidence_first_graph(self) -> None:
        graph = build_figure_claim_graph(self.state)
        self.assertEqual(graph["status"], "PASS_FIGURE_CLAIM_GRAPH")
        self.assertEqual(graph["summary"]["claims"], 3)
        self.assertEqual(graph["summary"]["visuals"], 4)
        self.assertGreaterEqual(graph["summary"]["evidence"], 17)
        self.assertEqual(graph["summary"]["affirmative_prose_claims"], 3)
        self.assertEqual(graph["summary"]["blockers"], 0)
        self.assertFalse(graph["scientific_authority"])

    def test_writer_reads_supported_claims_but_cannot_create_evidence(self) -> None:
        surface = writer_claim_surface(build_figure_claim_graph(self.state))
        self.assertEqual(len(surface["affirmative_claims"]), 3)
        self.assertFalse(surface["writer_can_create_evidence"])
        self.assertFalse(surface["scientific_authority"])

    def test_missing_claim_evidence_fails_closed(self) -> None:
        state = copy.deepcopy(self.state)
        state["audit"]["claim_ledger"][0]["evidence_ids"].append("MISSING-EVIDENCE")
        graph = build_figure_claim_graph(state)
        self.assertEqual(graph["status"], "BLOCK_FIGURE_CLAIM_GRAPH")
        self.assertTrue(any(x.startswith("claim-evidence-unregistered:N1:MISSING-EVIDENCE") for x in graph["blockers"]))

    def test_uncertainty_required_visual_must_show_uncertainty(self) -> None:
        state = copy.deepcopy(self.state)
        visual = next(x for x in state["completion"]["visualizations"] if x["id"] == "V-ABLATION-ROBUSTNESS")
        visual["visual_review"]["uncertainty_visible"] = False
        graph = build_figure_claim_graph(state)
        self.assertIn("required-uncertainty-not-visible:V-ABLATION-ROBUSTNESS", graph["blockers"])

    def test_refuted_claim_never_enters_affirmative_writer_surface(self) -> None:
        state = copy.deepcopy(self.state)
        row = state["audit"]["claim_ledger"][0]
        row["adjudication_status"] = "REFUTED"
        row["affirmative_claim_allowed"] = False
        row["must_preserve_negative_or_inconclusive"] = True
        surface = writer_claim_surface(build_figure_claim_graph(state))
        self.assertNotIn("N1", [x["claim_id"] for x in surface["affirmative_claims"]])
        self.assertIn("N1", [x["claim_id"] for x in surface["must_preserve_negative_or_inconclusive"]])


if __name__ == "__main__":
    unittest.main()
