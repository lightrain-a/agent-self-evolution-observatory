from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "generated" / "agent-safety-g1-mcta-p0-conditional-contract-20260904.json"


class MCTAP0ContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_execution_authority_remains_closed(self) -> None:
        self.assertTrue(all(value is False for value in self.contract["authority"].values()))

    def test_exact_eight_pair_panel_and_two_states(self) -> None:
        panel = self.contract["panel"]
        self.assertEqual(panel["pair_count"], 8)
        self.assertEqual(panel["state_count"], 2)
        self.assertEqual(panel["pair_state_units"], 16)
        self.assertEqual(len(set(panel["pair_ids"])), 8)

    def test_p0a_is_benign_only_and_freezes_pair_selection_before_harmful_outputs(self) -> None:
        p0a = self.contract["phase_p0a_capability_only"]
        self.assertEqual(p0a["episodes"], 16)
        self.assertFalse(p0a["harmful_calls_allowed"])
        self.assertEqual(p0a["proceed_gate"]["minimum_pair_ids_C1_in_both_states"], 6)
        self.assertIn("No harmful P0 outcome exists", p0a["selection_blinding"])

    def test_p0b_runs_all_eight_after_eligible_manifest_is_frozen(self) -> None:
        p0b = self.contract["phase_p0b_harmful_identification"]
        self.assertEqual(p0b["episodes"], 16)
        self.assertIn("all eight", p0b["pair_scope"].lower())
        self.assertIn("FORBIDDEN", p0b["p1_pair_selection_after_harmful_outputs"])

    def test_total_p0_episode_count_matches_workload_plan(self) -> None:
        total = self.contract["phase_p0a_capability_only"]["episodes"] + self.contract["phase_p0b_harmful_identification"]["episodes"]
        self.assertEqual(total, 32)

    def test_exact_once_and_failure_semantics(self) -> None:
        rules = self.contract["exact_once_and_failure_semantics"]
        self.assertEqual(rules["semantic_attempts_per_episode"], 1)
        self.assertFalse(rules["sample_replacement"])
        self.assertFalse(rules["failed_task_top_up"])
        self.assertFalse(rules["outcome_driven_pair_replacement"])
        self.assertTrue(rules["raw_provider_response_persist_before_parse"])
        self.assertFalse(rules["post_response_retry"])
        self.assertIn("never relabel as refusal", rules["parser_or_browser_failure"])

    def test_p1_never_opens_automatically(self) -> None:
        gate = self.contract["downstream_gate"]
        self.assertTrue(gate["P1_not_automatic"])
        self.assertIn("separate P1 execution authority", gate["P1_requires"])


if __name__ == "__main__":
    unittest.main()
