from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUNNER = ROOT / "analyze_evaluation_coarsening.py"
OUT = ROOT / "evaluation-coarsening-analysis-20260825.json"
RECEIPT = ROOT / "manuscript-strengthening-r4-receipt.json"


class EvaluationCoarseningAnalysisTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run([sys.executable, str(RUNNER)], check=True, capture_output=True, text=True)
        cls.state = json.loads(OUT.read_text(encoding="utf-8"))

    def test_coarse_views_are_explicit_and_stage_signature_is_non_scalar(self) -> None:
        self.assertEqual(self.state["status"], "SUPPORTED_DIAGNOSTIC_VALUE_OF_STAGE_RESOLUTION")
        views = {row["view"]: row for row in self.state["coarsened_views"]}
        self.assertEqual(set(views), {"write_only", "retrieval_only", "native_endpoint_only", "forced_endpoint_only", "stage_resolved_signature"})
        self.assertIn("behavioral authority", views["write_only"]["miscredit_risk"])
        self.assertIn("availability", views["retrieval_only"]["miscredit_risk"])
        self.assertIn("failed stage", views["native_endpoint_only"]["miscredit_risk"])
        self.assertIn("native end-to-end", views["forced_endpoint_only"]["miscredit_risk"])
        self.assertFalse(self.state["analysis_conclusion"]["causal_mediation_claim"])
        self.assertFalse(self.state["analysis_conclusion"]["new_method_claim"])

    def test_hypothesis_aliasing_matrix_preserves_claim_boundaries(self) -> None:
        hypotheses = {row["id"]: row for row in self.state["hypothesis_aliasing_matrix"]}
        self.assertEqual(len(hypotheses), 5)
        self.assertIn("inconsistent", hypotheses["H_WRITE_INERT"]["full_signature"])
        self.assertIn("weakened", hypotheses["H_GLOBAL_MEMORY_INSENSITIVITY"]["full_signature"])
        self.assertIn("weakened", hypotheses["H_RETRIEVAL_ABSENCE"]["full_signature"])
        self.assertIn("rejected", hypotheses["H_EXPOSURE_EQUALS_UPTAKE"]["full_signature"])
        self.assertIn("not supported", hypotheses["H_UNIVERSAL_DIRECTIONAL_TRANSPORT"]["full_signature"])
        self.assertFalse(any(self.state["authority"].values()))
        self.assertEqual(self.state["execution"], {"new_scientific_provider_calls": 0, "new_gpu_runs": 0, "new_scientific_experiments": 0})

    def test_r4_receipt_binds_analysis_and_keeps_historical_result_analysis_immutable(self) -> None:
        import hashlib
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        self.assertEqual(receipt["status"], "PAPER_ONLY_R4_EVALUATION_COARSENING_ANALYZED")
        self.assertEqual(receipt["analysis_binding"]["sha256"], hashlib.sha256(OUT.read_bytes()).hexdigest())
        self.assertFalse(receipt["result_analysis_binding"]["mutated_by_r4"])
        self.assertEqual(receipt["artifacts"]["pdf"]["pages"], 14)
        self.assertEqual(receipt["artifacts"]["pdf"]["undefined_references"], 0)
        self.assertEqual(receipt["artifacts"]["pdf"]["undefined_citations"], 0)
        self.assertEqual(receipt["artifacts"]["pdf"]["overfull_boxes"], 0)
        self.assertFalse(any(receipt["authority"].values()))


if __name__ == "__main__":
    unittest.main()
