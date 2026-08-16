from __future__ import annotations

import json
import re
import unittest

from .asset_first_stri_p0e_supplement_receipt import build_receipt


class AssetFirstSTRIP0ESupplementReceiptTest(unittest.TestCase):
    def test_receipt_matches_frozen_p0e_boundary(self) -> None:
        state = build_receipt()
        self.assertEqual(state["competence_calibration"]["pristine_success"], 18)
        self.assertEqual(state["competence_calibration"]["episodes"], 24)
        self.assertEqual(state["paired_causal_result"]["paired_units"], 24)
        self.assertEqual(state["paired_causal_result"]["arm_episodes"], 96)
        self.assertEqual(set(state["paired_causal_result"]["success_rate"].values()), {0.75})
        self.assertEqual(set(state["paired_causal_result"]["paired_disagreement"].values()), {0.0})
        self.assertEqual(state["trajectory_boundary"]["B_vs_A_action_sequence_disagreement"], 11)
        self.assertEqual(state["trajectory_boundary"]["C_vs_A_action_sequence_disagreement"], 15)
        self.assertEqual(state["trajectory_boundary"]["D_vs_A_exact_trajectory_units"], 24)
        self.assertFalse(state["trajectory_boundary"]["any_simple_B_over_C_dominance_supported"])
        self.assertEqual(state["statistical_resolution"]["effect_floor_unidirectional_flips"], 3)
        self.assertEqual(state["statistical_resolution"]["two_sided_exact_mcnemar_p_at_effect_floor"], 0.25)
        self.assertEqual(state["statistical_resolution"]["minimum_unidirectional_discordances_for_p_lt_0_05"], 6)
        self.assertTrue(state["final_disposition"]["experimental_stop_valid"])
        self.assertFalse(state["final_disposition"]["persistent_principle_dead_end_certified"])
        self.assertTrue(state["final_disposition"]["broader_STRI_N1_N2_N3_unchanged"])
        self.assertTrue(state["final_disposition"]["stage2_locked"])
        self.assertFalse(state["final_disposition"]["new_gpu_authorized"])

    def test_receipt_is_anonymous_and_path_sanitized(self) -> None:
        text = json.dumps(build_receipt(), ensure_ascii=False)
        forbidden = [r"/home/", r"/data/", r"\bwyt\b", r"222\.20", r"10\.42", r"hf_[A-Za-z0-9]{20,}"]
        for pattern in forbidden:
            self.assertIsNone(re.search(pattern, text, flags=re.I), pattern)

    def test_source_receipts_are_content_addressed(self) -> None:
        state = build_receipt()
        self.assertEqual(len(state["source_sha256"]), 7)
        self.assertTrue(all(re.fullmatch(r"[0-9a-f]{64}", value) for value in state["source_sha256"].values()))


if __name__ == "__main__":
    unittest.main()
