from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "generated/asset-first-stri-r2-selection-credit-decomposition-contract-20260825.json"
RESULT = ROOT / "generated/asset-first-stri-r2-selection-credit-decomposition-result-20260825.json"
NOVELTY = ROOT / "generated/asset-first-stri-r2-credit-fragmentation-novelty-reduction-20260825.json"


class SelectionCreditDecompositionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.novelty = json.loads(NOVELTY.read_text(encoding="utf-8"))

    def test_parent_gate_authorizes_only_zero_model_decomposition(self) -> None:
        self.assertEqual(self.novelty["gate"]["decision"], "GO_ZERO_MODEL_2X2_CONTROLLER_DECOMPOSITION")
        self.assertEqual(self.result["new_model_calls"], 0)
        self.assertEqual(self.result["new_agent_runs"], 0)
        self.assertEqual(self.result["new_gpu_runs"], 0)
        self.assertFalse(self.result["claim_expansion"])

    def test_canonical_reference_is_recovered(self) -> None:
        h = self.result["headline"]
        self.assertAlmostEqual(h["canonical_focal_selection_probability"], 0.5, places=12)
        self.assertTrue(h["canonical_retired_after_eight_feedback"])

    def test_native_split_fails_both_invariance_endpoints(self) -> None:
        cell = self.result["cells"]["S_native__C_native"]
        self.assertAlmostEqual(cell["focal_semantic_selection_probability"], 2.0 / 3.0, places=12)
        self.assertFalse(cell["selection_matches_canonical"])
        self.assertFalse(cell["focal_semantic_class_retired_after_feedback"])
        self.assertFalse(cell["post_credit_lifecycle_matches_canonical"])

    def test_repairs_are_orthogonal(self) -> None:
        s_only = self.result["cells"]["S_quotient__C_native"]
        c_only = self.result["cells"]["S_native__C_quotient"]
        self.assertTrue(s_only["selection_matches_canonical"])
        self.assertFalse(s_only["post_credit_lifecycle_matches_canonical"])
        self.assertFalse(c_only["selection_matches_canonical"])
        self.assertTrue(c_only["post_credit_lifecycle_matches_canonical"])

    def test_both_repairs_restore_both_endpoints(self) -> None:
        both = self.result["cells"]["S_quotient__C_quotient"]
        self.assertAlmostEqual(both["focal_semantic_selection_probability"], 0.5, places=12)
        self.assertTrue(both["selection_matches_canonical"])
        self.assertTrue(both["post_credit_lifecycle_matches_canonical"])
        self.assertTrue(both["both_invariance_endpoints_match_canonical"])

    def test_identical_feedback_is_bound_across_credit_cells(self) -> None:
        hashes = {cell["feedback_sha256"] for cell in self.result["cells"].values()}
        self.assertEqual(len(hashes), 1)
        self.assertEqual(self.result["split_factor_realizations"]["native_credit"]["feedback_records"], 8)
        self.assertEqual(self.result["split_factor_realizations"]["quotient_credit"]["feedback_records"], 8)
        native_stats = self.result["split_factor_realizations"]["native_credit"]["pre_prune_stats"]
        self.assertEqual(sorted(int(row["attempts"]) for row in native_stats.values()), [4, 4])
        self.assertEqual(self.result["split_factor_realizations"]["quotient_credit"]["class_representative_stats"]["attempts"], 8)

    def test_frozen_cell_predictions_match_exactly(self) -> None:
        for key, pred in self.contract["frozen_cell_predictions"].items():
            cell = self.result["cells"][key]
            self.assertIs(cell["selection_matches_canonical"], pred["initial_selection_matches_canonical"])
            self.assertIs(cell["post_credit_lifecycle_matches_canonical"], pred["post_credit_lifecycle_matches_canonical"])
        self.assertEqual(self.result["decision"], "PASS_TWO_CHANNEL_SELECTION_CREDIT_DECOMPOSITION")
        self.assertTrue(self.result["pass_gate"])


if __name__ == "__main__":
    unittest.main()
