#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ANALYSIS = HERE / "stage-transport-bottleneck-analysis-20260825.json"
RUNNER = HERE / "analyze_stage_transport_bottleneck.py"
RECEIPT = HERE / "manuscript-strengthening-r2-receipt.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class StageTransportBottleneckAnalysisTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run([sys.executable, str(RUNNER)], check=True, capture_output=True, text=True)
        cls.row = json.loads(ANALYSIS.read_text(encoding="utf-8"))

    def test_localization_is_operational_not_mediation(self) -> None:
        self.assertEqual(self.row["status"], "SUPPORTED_OPERATIONAL_POST_EXPOSURE_ATTENUATION_LOCALIZATION")
        loc = self.row["localization"]
        self.assertEqual(loc["verdict"], "POST_EXPOSURE_PRE_ACTION_ATTENUATION_IS_THE_STRONGEST_SUPPORTED_OPERATIONAL_LOCALIZATION")
        self.assertEqual(loc["claim_strength"], "SUPPORTED_OPERATIONAL_LOCALIZATION_NOT_CAUSAL_MEDIATION")
        self.assertIn("causal mediation coefficient", " ".join(self.row["does_not_imply"]))

    def test_forced_leverage_is_side_control_not_native_stage(self) -> None:
        obj = self.row["scientific_object"]
        self.assertEqual(obj["native_chain"], ["persistent_write", "retrieval_exposure", "first_action_uptake", "terminal_outcome"])
        self.assertEqual(obj["side_control"], "forced_fixed_evidence_leverage")
        self.assertIn("bypasses native retrieval", obj["why_side_control_not_chain_stage"])
        self.assertIn("must not be divided", obj["forbidden_scalarization"])

    def test_alternative_explanations_are_typed(self) -> None:
        rows = {row["id"]: row for row in self.row["alternative_explanation_audit"]}
        self.assertEqual(len(rows), 6)
        self.assertEqual(rows["A1_NO_PERSISTENT_STATE_INTERVENTION"]["status"], "INCONSISTENT_WITH_FROZEN_EVIDENCE")
        self.assertEqual(rows["A2_DOWNSTREAM_POLICY_GLOBALLY_INSENSITIVE_TO_MEMORY_CONTENT"]["status"], "WEAKENED_NOT_ELIMINATED")
        self.assertEqual(rows["A3_NATIVE_FAILURE_IS_ONLY_RETRIEVAL_ABSENCE"]["status"], "WEAKENED_NOT_ELIMINATED")
        self.assertEqual(rows["A4_RETRIEVAL_HIT_IS_A_VALID_SURROGATE_FOR_POLICY_UPTAKE"]["status"], "REJECTED_AS_EVALUATION_EQUIVALENCE")
        self.assertEqual(rows["A5_BRANCH_SPECIFIC_MEMORY_HAS_UNIVERSAL_DIRECTIONAL_TERMINAL_TRANSPORT"]["status"], "NOT_SUPPORTED")
        self.assertEqual(rows["A6_OBSERVED_ATTENUATION_IS_A_CERTIFIED_CAUSAL_MEDIATOR_EFFECT"]["status"], "UNRESOLVED_AND_FORBIDDEN_AS_CLAIM")

    def test_frozen_numbers_and_zero_authority(self) -> None:
        pattern = self.row["observed_pattern"]
        self.assertEqual(pattern["write"]["shopping_diverged"], "20/20")
        self.assertAlmostEqual(pattern["forced_capacity_control"]["terminal_abs_delta"], 0.15625)
        self.assertEqual((pattern["native_exposure"]["retrieval_hits"], pattern["native_exposure"]["retrieval_opportunities"]), (125, 172))
        self.assertAlmostEqual(pattern["native_first_action"]["tv"], 0.06944)
        self.assertAlmostEqual(pattern["native_terminal_shopping"]["abs_delta"], 0.02083)
        self.assertEqual(pattern["native_terminal_reddit"]["nonzero_signs"], "opposite")
        self.assertEqual(self.row["execution"], {"new_gpu_runs": 0, "new_scientific_experiments": 0, "new_scientific_provider_calls": 0})
        self.assertFalse(any(self.row["authority"].values()))

    def test_r2_receipt_is_content_addressed_and_zero_execution(self) -> None:
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        self.assertEqual(receipt["status"], "PAPER_ONLY_BOTTLENECK_LOCALIZATION_STRENGTHENING_COMPLETE")
        self.assertEqual(receipt["scientific_deepening"]["claim_strength"], "SUPPORTED_OPERATIONAL_LOCALIZATION_NOT_CAUSAL_MEDIATION")
        for key in ("pdf", "source_zip", "stage_figure"):
            row = receipt["artifacts"][key]
            path = HERE.parents[1] / row["path"]
            self.assertTrue(path.is_file(), key)
            self.assertEqual(sha256(path), row["sha256"], key)
        analysis = receipt["analysis_binding"]
        self.assertEqual(sha256(HERE.parents[1] / analysis["path"]), analysis["sha256"])
        self.assertEqual(sha256(HERE.parents[1] / analysis["runner"]), analysis["runner_sha256"])
        self.assertEqual(receipt["pdf_qa"]["latex_undefined_references"], 0)
        self.assertEqual(receipt["pdf_qa"]["latex_overfull_boxes"], 0)
        self.assertEqual(receipt["pdf_qa"]["raster_edge_risk_pages"], 0)
        self.assertFalse(any(receipt["authority"].values()))
        self.assertEqual(receipt["execution"]["new_scientific_provider_calls"], 0)
        self.assertEqual(receipt["execution"]["new_gpu_scientific_runs"], 0)
        self.assertEqual(receipt["execution"]["new_scientific_experiments"], 0)

    def test_manuscript_preserves_capacity_transport_and_localization_boundaries(self) -> None:
        source = HERE / "source" / "sections"
        mechanism = (source / "02_mechanism.tex").read_text(encoding="utf-8")
        results = (source / "04_variance_protocol.tex").read_text(encoding="utf-8")
        conclusion = (source / "06_limitations_conclusion.tex").read_text(encoding="utf-8")
        figure_script = (HERE / "source" / "build_stage_transport_figure.py").read_text(encoding="utf-8")
        joined = "\n".join((mechanism, results, conclusion))
        self.assertIn("Forced leverage is a capacity control, not a native stage", mechanism)
        self.assertIn("after exposure and before stable action uptake", joined)
        self.assertIn("not a causal mediation coefficient", joined)
        self.assertIn("Retrieval hit is a surrogate for policy use", results)
        self.assertIn("bypasses native retrieval", figure_script)
        self.assertNotIn("FORCED LEVERAGE", figure_script)
        self.assertIn("FORCED CAPACITY CONTROL", figure_script)


if __name__ == "__main__":
    unittest.main()
