from __future__ import annotations

import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARTIFACT = HERE / "c1-prerequisite-diagnostic-completeness-20260828.json"


class C1PrerequisiteDiagnosticCompletenessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_geometry_is_complete(self) -> None:
        self.assertEqual(self.data["model"]["coordinates"], ["W", "E", "U", "O", "F"])
        self.assertEqual(self.data["model"]["native_prerequisite_order"], "O => U => E => W")
        self.assertEqual(self.data["model"]["diagnostic_states"], 10)
        self.assertEqual(self.data["model"]["observed_surface_subsets"], 32)
        self.assertEqual(len(self.data["result"]["all_subsets"]), 32)

    def test_full_basis_is_unique_injective_projection(self) -> None:
        self.assertEqual(self.data["result"]["injective_subsets"], [["W", "E", "U", "O", "F"]])
        self.assertTrue(self.data["result"]["full_basis_is_unique_injective_subset"])
        self.assertEqual(self.data["result"]["unique_minimal_separating_basis"], ["W", "E", "U", "O", "F"])

    def test_omit_native_coordinate_aliases_adjacent_prefixes(self) -> None:
        expected = {
            "W": {frozenset(("p0-f0", "p1-f0")), frozenset(("p0-f1", "p1-f1"))},
            "E": {frozenset(("p1-f0", "p2-f0")), frozenset(("p1-f1", "p2-f1"))},
            "U": {frozenset(("p2-f0", "p3-f0")), frozenset(("p2-f1", "p3-f1"))},
            "O": {frozenset(("p3-f0", "p4-f0")), frozenset(("p3-f1", "p4-f1"))},
        }
        for coord, groups in expected.items():
            row = self.data["result"]["omit_one"][coord]
            self.assertEqual(row["ambiguous_pair_count"], 2)
            self.assertEqual({frozenset(group) for group in row["ambiguous_groups"]}, groups)

    def test_omit_forced_capacity_aliases_each_prefix(self) -> None:
        row = self.data["result"]["omit_one"]["F"]
        self.assertEqual(row["ambiguous_pair_count"], 5)
        expected = {frozenset((f"p{p}-f0", f"p{p}-f1")) for p in range(5)}
        self.assertEqual({frozenset(group) for group in row["ambiguous_groups"]}, expected)

    def test_claim_boundary_and_zero_execution(self) -> None:
        self.assertIn("paper-specific", self.data["claim_boundary"])
        self.assertIn("NOT-SUPPORTED", self.data["claim_boundary"])
        self.assertEqual(self.data["execution"]["provider_calls"], 0)
        self.assertEqual(self.data["execution"]["gpu_runs"], 0)
        self.assertEqual(self.data["execution"]["model_actions"], 0)
        self.assertEqual(self.data["execution"]["scientific_empirical_outcomes_read"], 0)
        self.assertFalse(any(self.data["authority"].values()))

    def test_theory_remains_evidence_only_until_next_versioned_paper_revision(self) -> None:
        reconciliation = json.loads((HERE / "c1-r7-engineering-version-reconciliation-20260829.json").read_text(encoding="utf-8"))
        self.assertIn("revoked from current narrative authority", reconciliation["narrative_authority"]["C1-stage-resolved-engineering-r2.pdf"])
        self.assertIn("independently verified theory evidence", reconciliation["narrative_authority"]["c1-prerequisite-diagnostic-completeness-20260828.json"])
        self.assertEqual(reconciliation["narrative_authority"]["source-r7/"], "latest canonical paper source on the execution base")
        self.assertFalse(reconciliation["pilot_boundary"]["paper_update_before_pilot_result"])
        self.assertFalse(reconciliation["pilot_boundary"]["confirmatory_full_authorized"])


if __name__ == "__main__":
    unittest.main()
