from __future__ import annotations

import unittest

from .asset_first_stri_qwen3_merge_split_p0a import decide, mix_distributions, tv


class Qwen3MergeSplitP0ATest(unittest.TestCase):
    def test_qualification_failure_is_not_scientific_stop(self) -> None:
        decision, scientific = decide(
            qualification_pass=False,
            witness_passes={"merge_003_015": False, "merge_004_015": False},
            budget_pass=True,
        )
        self.assertEqual(decision, "INCONCLUSIVE_PROPOSER_QUALIFICATION_FAILED")
        self.assertFalse(scientific)

    def test_two_witnesses_are_required_for_go(self) -> None:
        decision, scientific = decide(
            qualification_pass=True,
            witness_passes={"merge_003_015": True, "merge_004_015": False},
            budget_pass=True,
        )
        self.assertEqual(decision, "INCONCLUSIVE_ONE_OF_TWO_WITNESSES_ONLY")
        self.assertTrue(scientific)
        decision, scientific = decide(
            qualification_pass=True,
            witness_passes={"merge_003_015": True, "merge_004_015": True},
            budget_pass=True,
        )
        self.assertEqual(decision, "DYNAMIC_PARTIAL_OVERLAP_REPRESENTATION_SENSITIVITY_SUPPORTED")
        self.assertTrue(scientific)

    def test_zero_witnesses_is_valid_negative_only_after_qualification(self) -> None:
        decision, scientific = decide(
            qualification_pass=True,
            witness_passes={"merge_003_015": False, "merge_004_015": False},
            budget_pass=True,
        )
        self.assertEqual(decision, "STOP_DYNAMIC_PARTIAL_OVERLAP_PROPAGATION_GATE_NOT_MET")
        self.assertTrue(scientific)

    def test_mixture_replay_changes_distribution_without_regeneration(self) -> None:
        source = {
            "skill_003": {"A": 1.0},
            "skill_004": {"B": 1.0},
            "skill_015": {"C": 1.0},
        }
        split = mix_distributions(source, {"skill_003": 1/3, "skill_004": 1/3, "skill_015": 1/3})
        merged = mix_distributions(source, {"skill_003": 1/4, "skill_004": 1/2, "skill_015": 1/4})
        self.assertGreater(tv(split, merged), 0.0)


if __name__ == "__main__":
    unittest.main()
