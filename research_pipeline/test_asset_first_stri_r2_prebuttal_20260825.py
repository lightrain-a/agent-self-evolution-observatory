from __future__ import annotations

import unittest

from .asset_first_stri_r2_prebuttal_20260825 import build


class STRIR2PrebuttalTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = build()

    def test_packet_is_ready_but_does_not_promote(self) -> None:
        self.assertEqual(self.result["decision"], "READY_FOR_INDEPENDENT_REVIEW_WITH_ONE_OPEN_EXTERNAL_VALIDITY_HOLD")
        self.assertFalse(self.result["summary"]["canonical_r19_replacement_authorized"])
        self.assertTrue(self.result["summary"]["independent_model_review_still_required_for_promotion"])

    def test_exactly_one_objection_requires_new_outcome_evidence(self) -> None:
        self.assertEqual(self.result["summary"]["decision_critical_objections"], 6)
        self.assertEqual(self.result["summary"]["paper_only_closed_or_scoped"], 5)
        self.assertEqual(self.result["summary"]["requires_new_outcome_or_runtime_evidence"], 1)
        self.assertEqual(self.result["summary"]["open_major_hold_ids"], ["PB-O5-NATURAL-PREVALENCE"])

    def test_threshold_toy_attack_is_closed_by_p3(self) -> None:
        row = next(x for x in self.result["objections"] if x["id"] == "PB-O2-THRESHOLD-TOY")
        self.assertEqual(row["disposition"], "CLOSED_BY_ARBITRARY_PARTITION_GEOMETRY")
        self.assertEqual(row["headline"]["cells"], 205)
        self.assertEqual(row["headline"]["formula_mismatches"], 0)
        self.assertEqual(row["headline"]["guaranteed_region_failures"], 0)

    def test_all_authority_remains_zero(self) -> None:
        self.assertFalse(self.result["scientific_authority"])
        self.assertFalse(self.result["experiment_authority"])
        self.assertFalse(self.result["gpu_authority"])
        self.assertFalse(self.result["submission_authority"])


if __name__ == "__main__":
    unittest.main()
