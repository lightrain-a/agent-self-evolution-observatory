from __future__ import annotations

import json
import unittest
from pathlib import Path

from .d2_proxy_reward_terminal_fixed_evidence import _must_include_score, build_support


ROOT = Path(__file__).resolve().parent.parent


class ProxyRewardTerminalFixedEvidenceTest(unittest.TestCase):
    def test_frozen_support_tasks_are_evidence_complete_and_deterministic(self) -> None:
        support = build_support()
        self.assertEqual(support["status"], "SUPPORT_QUALIFIED")
        self.assertEqual([row["task_id"] for row in support["tasks"]], ["164", "385", "387", "388"])
        for row in support["tasks"]:
            self.assertTrue(row["qualified"])
            self.assertEqual(row["blockers"], [])
            self.assertGreaterEqual(len(row["reference_answers"]), 2)
            self.assertTrue(all(item["visible"] for item in row["reference_visibility"]))
            self.assertTrue(row["evidence_sha256"])

    def test_selected_must_include_evaluator_matches_multi_reference_semantics(self) -> None:
        score, checks = _must_include_score("Dry; Uneven color", ["Dry", "Uneven color"])
        self.assertEqual(score, 1.0)
        self.assertEqual([row["score"] for row in checks], [1.0, 1.0])
        score, checks = _must_include_score("Dry only", ["Dry", "Uneven color"])
        self.assertEqual(score, 0.0)
        self.assertEqual([row["score"] for row in checks], [1.0, 0.0])

    def test_current_f2_result_fails_closed_without_negative_authority(self) -> None:
        result = json.loads((ROOT / "generated/d2-proxy-reward-terminal-fixed-evidence.json").read_text(encoding="utf-8"))
        summary = result["summary"]
        self.assertEqual(result["status"], "TERMINAL_FIXED_EVIDENCE_COMPLETE")
        self.assertEqual(summary["complete_primary_calls"], 96)
        self.assertEqual(summary["complete_no_memory_calls"], 12)
        self.assertEqual(summary["provider_failures"], 0)
        self.assertAlmostEqual(summary["observed_mean_absolute_success_rate_difference"], 0.145833, places=6)
        self.assertAlmostEqual(summary["permutation_p_ge_observed"], 0.160128, places=6)
        self.assertFalse(summary["gate_pass"])
        self.assertEqual(result["decision"], "INCONCLUSIVE_NO_NEGATIVE_AUTHORITY")
        self.assertFalse(result["scientific_authority"])


if __name__ == "__main__":
    unittest.main()
