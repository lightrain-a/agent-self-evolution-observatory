from __future__ import annotations

import unittest

from .asset_first_stri_r2_natural_prevalence_qualification_20260825 import build


class STRIR2NaturalPrevalenceQualificationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state = build()

    def test_release_mechanism_is_operational(self) -> None:
        self.assertTrue(self.state["pass_code_path_operational"])
        loop = self.state["released_loop"]
        self.assertEqual(loop["default_prune_min_attempts_per_identity"], 8)
        self.assertEqual(loop["default_self_play_iterations"], 5)
        self.assertEqual(loop["default_solver_dataset_target_total_records"], 8000)
        self.assertTrue(loop["stats_updated_before_pruning"])
        self.assertTrue(loop["stats_are_identity_local"])

    def test_prevalence_fails_closed_without_evolved_state(self) -> None:
        self.assertEqual(
            self.state["decision"],
            "HOLD_NATURAL_PREVALENCE_UNRESOLVED_RUNTIME_OUTPUT_NOT_RELEASED",
        )
        self.assertFalse(self.state["natural_prevalence_established"])
        inv = self.state["release_inventory"]
        self.assertEqual(inv["tracked_runtime_state_count"], 0)
        self.assertEqual(inv["released_initial_stats_with_nonzero_attempts"], 0)
        self.assertTrue(all(row.get("evolved_runtime_state_file_count", 0) == 0 for row in inv["local_first_party_mirrors_checked"] if row.get("present")))

    def test_no_authority_or_claim_expansion(self) -> None:
        self.assertEqual(self.state["new_model_calls"], 0)
        self.assertEqual(self.state["new_agent_runs"], 0)
        self.assertEqual(self.state["new_gpu_runs"], 0)
        self.assertFalse(self.state["claim_expansion"])
        self.assertFalse(self.state["scientific_authority"])
        self.assertFalse(self.state["experiment_authority"])
        self.assertFalse(self.state["gpu_authority"])
        self.assertFalse(self.state["submission_authority"])


if __name__ == "__main__":
    unittest.main()
