from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNNER = HERE / "analyze_stage_evidence_ladder.py"
OUT = HERE / "stage-evidence-ladder-analysis-20260825.json"


class StageEvidenceLadderAnalysisTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(["python3", str(RUNNER)], check=True, cwd=HERE)
        cls.data = json.loads(OUT.read_text(encoding="utf-8"))

    def test_boundary_is_first_action(self) -> None:
        self.assertEqual(self.data["localization"]["first_unsupported_native_stage"], "native_first_action_uptake")
        self.assertEqual(self.data["localization"]["strength"], "OPERATIONAL_ORDINAL_LOCALIZATION_NOT_CAUSAL_MEDIATION")

    def test_native_order_and_side_control_are_separate(self) -> None:
        obj = self.data["scientific_object"]
        self.assertEqual(obj["native_order"], ["persistent_write", "native_retrieval_exposure", "native_first_action_uptake", "native_terminal_outcome"])
        self.assertEqual(obj["side_control"], "forced_capacity_side_control")
        self.assertTrue(obj["ordinal_not_scalar"])
        self.assertTrue(obj["cross_stage_ratio_forbidden"])

    def test_evidence_states_preserve_measurement_semantics(self) -> None:
        rows = {row["stage"]: row for row in self.data["evidence_ladder"]}
        self.assertEqual(rows["persistent_write"]["evidence_state"], "SUPPORTED")
        self.assertEqual(rows["forced_capacity_side_control"]["evidence_state"], "SUPPORTED_SIDE_CONTROL")
        self.assertEqual(rows["native_retrieval_exposure"]["evidence_state"], "DIRECTLY_OBSERVED")
        self.assertEqual(rows["native_first_action_uptake"]["evidence_state"], "NOT_SUPPORTED_AT_FROZEN_PRIMARY_TEST")
        self.assertEqual(rows["native_terminal_outcome"]["evidence_state"], "SPARSE_HETEROGENEOUS_NOT_UNIVERSALLY_SUPPORTED")

    def test_zero_authority(self) -> None:
        self.assertEqual(self.data["execution"], {"new_gpu_runs": 0, "new_scientific_experiments": 0, "new_scientific_provider_calls": 0})
        self.assertFalse(any(self.data["authority"].values()))


if __name__ == "__main__":
    unittest.main()
