from __future__ import annotations

import unittest

from research_pipeline import agent_constraint_externality_atomgit_repeat_dev_reserve_source as runner
from research_pipeline import agent_constraint_externality_atomgit_repeat_dev_reserve_source_common as common


class RepeatDevReserveSourceTest(unittest.TestCase):
    def test_ranked_reserve_is_complete(self) -> None:
        ranks = common.ranked_ids()
        self.assertEqual(set(ranks), {"FG", "TNF"})
        self.assertEqual(len(ranks["FG"]), 8)
        self.assertEqual(len(ranks["TNF"]), 8)
        self.assertEqual(len(set(ranks["FG"] + ranks["TNF"])), 16)
        self.assertEqual(len(common.family_index()), 16)

    def test_first_candidate_uses_frozen_round_robin_rank(self) -> None:
        fid, selected = runner.next_candidate({}, [])
        self.assertEqual(fid, common.ranked_ids()["FG"][0])
        self.assertEqual(selected, {"FG": [], "TNF": []})

    def test_target_success_is_attrition_not_terminal(self) -> None:
        ranks = common.ranked_ids()
        completion = [
            {"family_id": ranks["FG"][0], "target_success": True, "usable_semantic_failure": False},
            {"family_id": ranks["TNF"][0], "target_success": False, "usable_semantic_failure": True},
        ]
        states = {common.unit_id(row["family_id"]): "COMPLETION" for row in completion}
        fid, selected = runner.next_candidate(states, completion)
        self.assertEqual(selected["FG"], [])
        self.assertEqual(selected["TNF"], [ranks["TNF"][0]])
        self.assertEqual(fid, ranks["FG"][1])

    def test_first_three_failures_per_category_freeze_panel(self) -> None:
        ranks = common.ranked_ids()
        completion = []
        for cat in ("FG", "TNF"):
            completion.extend([
                {"family_id": ranks[cat][0], "target_success": True, "usable_semantic_failure": False},
                {"family_id": ranks[cat][1], "target_success": False, "usable_semantic_failure": True},
                {"family_id": ranks[cat][2], "target_success": False, "usable_semantic_failure": True},
                {"family_id": ranks[cat][3], "target_success": True, "usable_semantic_failure": False},
                {"family_id": ranks[cat][4], "target_success": False, "usable_semantic_failure": True},
            ])
        selected = runner.selected_from(completion)
        self.assertEqual(selected["FG"], [ranks["FG"][1], ranks["FG"][2], ranks["FG"][4]])
        self.assertEqual(selected["TNF"], [ranks["TNF"][1], ranks["TNF"][2], ranks["TNF"][4]])
        states = {common.unit_id(row["family_id"]): "COMPLETION" for row in completion}
        fid, selected2 = runner.next_candidate(states, completion)
        self.assertIsNone(fid)
        self.assertEqual(selected2, selected)

    def test_post_dispatch_noncompletion_is_not_replayed(self) -> None:
        fid = common.ranked_ids()["FG"][0]
        with self.assertRaisesRegex(RuntimeError, "replay forbidden"):
            runner.next_candidate({common.unit_id(fid): "DISPATCH"}, [])

    def test_execution_authority_is_absent_in_readiness_stage(self) -> None:
        self.assertFalse(common.AUTH_OUTPUT.exists())
        self.assertFalse(common.EXEC_CONTRACT.exists())
        self.assertFalse(common.RESULT_OUTPUT.exists())

    def test_q1_and_readiness_prove_zero_local_dispatch(self) -> None:
        q1 = common.readj(common.Q1_OUTPUT)
        self.assertEqual(q1["codingplan_model_requests"], 0)
        self.assertEqual(q1["live_message_submit_count"], 0)
        self.assertEqual(q1["atomcode_session_jsonl_count"], 0)
        self.assertEqual(q1["trajectory_tool_event_count"], 0)
        self.assertTrue(q1["account_usage_delta_is_not_request_attribution"])
        preflight = common.readj(common.PREFLIGHT_OUTPUT)
        readiness = common.readj(common.READINESS_OUTPUT)
        self.assertTrue(all(value is False for value in preflight["authority"].values()))
        self.assertTrue(all(value is False for value in readiness["authority"].values()))
        self.assertEqual(readiness["executor_sha256"], preflight["executor_sha256"])
        self.assertEqual(readiness["common_sha256"], preflight["common_sha256"])
        self.assertEqual(readiness["bridge_sha256"], preflight["bridge_sha256"])
        self.assertFalse(common.LEDGER.exists())


if __name__ == "__main__":
    unittest.main()
