from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


class AdaptivePolicyV2Test(unittest.TestCase):
    def test_two_campaign_policy_and_paperstate_semantics(self) -> None:
        policy = json.loads((ROOT / "generated/discovery-engine-adaptive-policy.json").read_text(encoding="utf-8"))
        final_state = json.loads((ROOT / "generated/discovery-engine-terminal-replication-final-state-20260821.json").read_text(encoding="utf-8"))
        paperstates = json.loads((ROOT / "generated/d2-active-paperstates-20260821.json").read_text(encoding="utf-8"))

        self.assertEqual(policy["schema_version"], "2.0")
        self.assertAlmostEqual(sum(float(row["budget_share"]) for row in policy["birth_engines"]), 1.0, places=8)
        roles = {row["engine_id"]: row["role"] for row in policy["birth_engines"]}
        self.assertEqual(roles["D2"], "PRIMARY_BIRTH")
        self.assertEqual(roles["D5"], "PRIMARY_BIRTH")
        self.assertFalse(policy["global_observed_yield"]["winner_take_all_policy"])
        self.assertTrue(policy["objective_separation"]["manuscript_completion_is_separate_from_evidence_maturity"] if "manuscript_completion_is_separate_from_evidence_maturity" in policy["objective_separation"] else policy["objective_separation"]["manuscript_completion_is_separate_from_evidence_completion"])

        self.assertEqual(final_state["status"], "TERMINAL_COMPLETE")
        self.assertEqual(final_state["winner"], "D2")
        state = {row["engine_id"]: row for row in final_state["engine_state"]}
        self.assertEqual(state["D2"]["complete_unique_papers"], 3)
        self.assertEqual(state["D5"]["complete_unique_papers"], 0)
        self.assertEqual(state["D2"]["terminal_resolved"], 6)
        self.assertEqual(state["D5"]["terminal_resolved"], 6)

        self.assertEqual(len(paperstates["papers"]), 3)
        for paper in paperstates["papers"]:
            self.assertEqual(paper["status"], "MANUSCRIPT_COMPLETE_EXPERIMENT_DEBT")
            self.assertTrue(paper["manuscript_complete"])
            self.assertFalse(paper["evidence_complete"])
            self.assertTrue(paper["paper_qa_pass"])


if __name__ == "__main__":
    unittest.main()
