from __future__ import annotations

import json
import unittest
from pathlib import Path

from .d2_proxy_reward_memory_f1 import _falsifier_result


ROOT = Path(__file__).resolve().parent.parent


class ProxyRewardMemoryF1AuthorityTest(unittest.TestCase):
    def test_divergence_witness_survives_even_before_full_completion(self) -> None:
        self.assertEqual(
            _falsifier_result(paired_complete=1, paired_divergent=1, required_aligned=12),
            "SURVIVES_F1",
        )

    def test_zero_divergence_falsifies_only_after_frozen_falsifier_is_complete(self) -> None:
        self.assertEqual(
            _falsifier_result(paired_complete=12, paired_divergent=0, required_aligned=12),
            "FALSIFIED_F1",
        )
        self.assertEqual(
            _falsifier_result(paired_complete=0, paired_divergent=0, required_aligned=12),
            "SUPPORT_INCOMPLETE_NO_SCIENTIFIC_AUTHORITY",
        )
        self.assertEqual(
            _falsifier_result(paired_complete=11, paired_divergent=0, required_aligned=12),
            "SUPPORT_INCOMPLETE_NO_SCIENTIFIC_AUTHORITY",
        )

    def test_current_f1_support_failure_carries_no_zero_rate_pseudoevidence(self) -> None:
        artifact = json.loads((ROOT / "generated/d2-proxy-reward-memory-f1.json").read_text(encoding="utf-8"))
        summary = artifact["summary"]
        self.assertEqual(artifact["status"], "F1_SUPPORT_INCOMPLETE")
        self.assertEqual(artifact["falsifier_result"], "SUPPORT_INCOMPLETE_NO_SCIENTIFIC_AUTHORITY")
        self.assertEqual(summary["aligned_success_failure_rollouts"], 0)
        self.assertEqual(summary["required_aligned_success_failure_rollouts"], 12)
        self.assertFalse(summary["falsifier_evaluable"])
        self.assertIsNone(summary["paired_action_signature_divergence_rate"])
        self.assertIsNone(summary["modal_action_signature_difference_rate"])
        self.assertIsNone(summary["memory_condition_shift_from_no_memory"])


if __name__ == "__main__":
    unittest.main()
