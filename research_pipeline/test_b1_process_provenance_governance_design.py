from __future__ import annotations

import json
import unittest
from pathlib import Path

from .config import PROJECT_ROOT


DESIGN = PROJECT_ROOT / "research_pipeline" / "b1_process_provenance_governance_design_20260827.json"


class B1ProcessProvenanceGovernanceDesignTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(DESIGN.read_text(encoding="utf-8"))

    def test_zero_authority_hold(self) -> None:
        self.assertEqual(self.payload["status"], "FROZEN_DESIGN_HOLD")
        self.assertEqual(
            self.payload["authority"],
            {"scientific": False, "experiment": False, "provider": False, "gpu": False, "submission": False},
        )

    def test_mechanism_is_information_value_not_fixed_outcome_quality(self) -> None:
        laws = {row["id"] for row in self.payload["mechanism_laws"]}
        self.assertEqual(laws, {"NO_CHANNEL_LAW", "CONTENT_SUFFICIENCY_LAW", "PROVENANCE_INFORMATION_LAW"})
        non_claims = " ".join(self.payload["scientific_object"]["non_claims"])
        self.assertIn("failure-derived memory is inherently low quality", non_claims)
        self.assertIn("success-derived memory is inherently trustworthy", non_claims)

    def test_fresh_confirmation_cannot_reuse_legacy_units(self) -> None:
        boundary = self.payload["historical_evidence_boundary"]
        self.assertIn("do not revive", boundary["R19"])
        self.assertIn("non-confirmatory", boundary["legacy_27"])
        gates = self.payload["fresh_substrate_gate"]
        self.assertEqual(len(gates), 8)
        self.assertTrue(any("disjoint from historical R19" in gate for gate in gates))

    def test_experiment_program_separates_utilization_and_governance(self) -> None:
        program = self.payload["experiment_program"]
        self.assertTrue(any("utilization first stage" in row for row in program["E0_measurement_qualification"]))
        self.assertIn("A3 governor-visible provenance only", program["E2_channel_factorial"])
        self.assertIn("A7 backend-only relabel equivalence control", program["E2_channel_factorial"])
        self.assertIn("CONTENT_SUFFICIENT", program["E3_regime_law"]["allowed_outcomes"])


if __name__ == "__main__":
    unittest.main()
