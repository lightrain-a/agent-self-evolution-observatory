from __future__ import annotations

import json
import unittest

from research_pipeline.agent_constraint_externality_atomgit_repeat_dev_source_closeout import OUTPUT, build


class RepeatDevSourceCloseoutTest(unittest.TestCase):
    def test_support_stop_is_frozen_without_replacement(self) -> None:
        result = build()
        self.assertEqual(result["status"], "ATOMGIT_REPEAT_DEV_FIXED_SIX_SOURCE_SUPPORT_FAIL_STOP_NO_REPAIR")
        self.assertEqual(result["dispatched_family_count"], 3)
        self.assertEqual(result["semantic_target_failure_count"], 2)
        self.assertEqual(result["target_success_count"], 1)
        self.assertEqual(len(result["never_dispatched_family_ids"]), 3)
        self.assertFalse(result["repair_generation_executed"])
        self.assertFalse(result["topology_execution_executed"])
        self.assertFalse(result["current_fixed_six_reusable_for_repeat_panel"])
        self.assertFalse(result["replacement_or_top_up_allowed_under_consumed_contract"])
        self.assertFalse(result["authority"]["development_repeat_qualification"])
        replay = json.loads(OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(replay["content_sha256"], result["content_sha256"])


if __name__ == "__main__":
    unittest.main()
