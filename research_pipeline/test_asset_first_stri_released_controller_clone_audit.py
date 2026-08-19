from __future__ import annotations

import unittest

from .asset_first_stri_released_controller_clone_audit import (
    audit_clone,
    exact_clone_probabilities,
    normalized_profile_tv,
    probabilities_from_raw_weights,
    quotient_conserved_clone_probabilities,
    semantic_exposures,
)


class STRIReleasedControllerCloneAuditTest(unittest.TestCase):
    def test_exact_clone_reallocates_identity_weight_without_semantic_change(self) -> None:
        ids = ["a", "b", "c"]
        weights = [2.0, 2.0, 2.0]
        base = probabilities_from_raw_weights(ids, weights)
        cloned = exact_clone_probabilities(ids, weights, target_id="a", clone_id="a_clone")
        self.assertAlmostEqual(base["a"], 1.0 / 3.0)
        self.assertAlmostEqual(cloned["a"] + cloned["a_clone"], 0.5)
        self.assertAlmostEqual(cloned["b"], 0.25)

    def test_quotient_conserved_clone_preserves_semantic_family_mass(self) -> None:
        base = {"a": 1.0 / 3.0, "b": 1.0 / 3.0, "c": 1.0 / 3.0}
        repaired = quotient_conserved_clone_probabilities(base, target_id="a", clone_id="a_clone")
        self.assertAlmostEqual(repaired["a"], 1.0 / 6.0)
        self.assertAlmostEqual(repaired["a_clone"], 1.0 / 6.0)
        self.assertAlmostEqual(repaired["a"] + repaired["a_clone"], base["a"])
        self.assertAlmostEqual(repaired["b"], base["b"])
        self.assertAlmostEqual(sum(repaired.values()), 1.0)

    def test_semantic_exposure_counts_clone_as_same_support_implementation(self) -> None:
        rows = [
            {"accepted_skill_ids": ["a"]},
            {"accepted_skill_ids": ["b"]},
            {"accepted_skill_ids": ["a", "b"]},
        ]
        base = {"a": 1.0 / 3.0, "b": 1.0 / 3.0, "c": 1.0 / 3.0}
        cloned = {"a": 0.25, "b": 0.25, "c": 0.25, "a_clone": 0.25}
        before = semantic_exposures(rows, base)
        after = semantic_exposures(rows, cloned, clone_target="a", clone_id="a_clone")
        self.assertEqual(before, [1.0 / 3.0, 1.0 / 3.0, 2.0 / 3.0])
        self.assertEqual(after, [0.5, 0.25, 0.75])
        self.assertGreater(normalized_profile_tv(before, after), 0.0)

    def test_audit_reports_positive_and_negative_control_reallocation(self) -> None:
        rows = [
            {"accepted_skill_ids": ["a"]},
            {"accepted_skill_ids": ["b"]},
            {"accepted_skill_ids": ["a", "b"]},
        ]
        base = {"a": 1.0 / 3.0, "b": 1.0 / 3.0, "c": 1.0 / 3.0}
        cloned = {"a": 0.25, "b": 0.25, "c": 0.25, "a_clone": 0.25}
        out = audit_clone(rows, base, cloned, target_id="a", clone_id="a_clone")
        self.assertEqual(out["target_support_rows"], 2)
        self.assertEqual(out["rows_with_positive_exposure_change"], 2)
        self.assertEqual(out["rows_with_negative_exposure_change"], 1)
        self.assertAlmostEqual(out["semantic_family_relative_change"], 0.5)
        self.assertGreater(out["normalized_exposure_profile_tv"], 0.0)


if __name__ == "__main__":
    unittest.main()
