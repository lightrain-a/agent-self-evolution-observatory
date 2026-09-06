from __future__ import annotations

import unittest
from pathlib import Path

import research_pipeline.agent_constraint_externality_direct_sfq_atomgit_mimo25pro as lane


class DirectSFQAtomGitMiMo25ProTest(unittest.TestCase):
    def test_static_inputs_are_frozen_and_fresh(self) -> None:
        static, qual, selected, transport, v5 = lane.inputs()
        self.assertEqual(static["case_count"], 12)
        self.assertEqual(static["acceptable_final_failure_counts"], [9, 10])
        self.assertEqual(qual["case_count"], 12)
        self.assertEqual(selected["selected_backbone"]["model_id"], "mimo-v2.5-pro")
        self.assertEqual(transport["native_tool_attempts"], [])
        self.assertFalse(v5["authority"]["sq0_v6"])

    def test_shared_quota_gate_preserves_g1_reserve(self) -> None:
        self.assertEqual(lane.MODEL_ROUND_CAP, 56)
        self.assertEqual(lane.SHARED_RESERVE, 100)
        self.assertEqual(lane.MARGIN, 5)
        self.assertEqual(lane.MIN_REMAINING, 161)

    def test_futility_is_preregistered(self) -> None:
        success = lambda: {"target_success": True, "usable_target_failure": False, "non_semantic_failure": False}
        failure = lambda: {"target_success": False, "usable_target_failure": True, "non_semantic_failure": False}
        self.assertIsNone(lane.futility([failure() for _ in range(9)]))
        self.assertEqual(lane.futility([success() for _ in range(4)]), "DIRECT_SFQ_A0_ATOMGIT_FUTILITY_TOO_EASY_STOP")
        self.assertEqual(lane.futility([failure() for _ in range(11)]), "DIRECT_SFQ_A0_ATOMGIT_FUTILITY_TOO_HARD_STOP")
        self.assertEqual(lane.futility([{"non_semantic_failure": True}]), "DIRECT_SFQ_A0_ATOMGIT_INVALID_NON_SEMANTIC_FAILURE_STOP")

    def test_adapter_does_not_open_mainline_or_mechanism_authority(self) -> None:
        self.assertNotEqual(lane.EXECUTION_ID, "ACE-DIRECT-SFQ-A0-20260903")
        self.assertIn("atomgit-mimo25pro", lane.EXECUTION_ID.lower())
        self.assertTrue(Path(lane.BRIDGE).name.endswith("direct_sfq_atomgit_mcp_bridge.py"))


if __name__ == "__main__":
    unittest.main()
