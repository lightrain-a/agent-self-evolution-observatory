from __future__ import annotations

import json
import unittest

from research_pipeline.agent_constraint_externality_backbone_search_b3 import MIMO_CLOSEOUT, SEARCH_B3
from research_pipeline.agent_constraint_externality_runner_core import sha256_value


class CapabilityBackboneSearchB3Tests(unittest.TestCase):
    def _verified(self, path):
        payload = json.loads(path.read_text(encoding="utf-8"))
        claimed = payload["content_sha256"]
        unsigned = dict(payload); unsigned.pop("content_sha256")
        self.assertEqual(claimed, sha256_value(unsigned))
        return payload

    def test_mimo25_ceiling_closeout_is_exact(self):
        payload = self._verified(MIMO_CLOSEOUT)
        self.assertEqual(payload["status"], "CODINGPLAN_MIMO25_B2_CEILING_CLOSEOUT")
        self.assertEqual(payload["verdict"], "CAPABILITY_CALIBRATION_FAIL_CEILING_STOP")
        self.assertEqual(payload["gate"]["tool_loop_completion_rate"], 1.0)
        self.assertEqual(payload["gate"]["target_success_rate"], 1.0)
        self.assertEqual(payload["gate"]["non_target_preservation_rate"], 1.0)
        self.assertEqual(payload["accounting"]["scientific_model_round_count"], 69)
        self.assertEqual(payload["accounting"]["codingplan_account_window_request_delta"], 69)
        self.assertEqual(payload["accounting"]["account_level_unattributed_request_count"], 0)
        self.assertFalse(payload["authority"]["f0"])

    def test_final_predeclared_candidate_is_mimo25pro(self):
        payload = self._verified(SEARCH_B3)
        self.assertEqual(payload["status"], "CAPABILITY_BACKBONE_SEARCH_CONTINUE_MIMO25PRO_NEXT")
        self.assertEqual(payload["remaining_frozen_order"], ["mimo-v2.5-pro"])
        self.assertEqual(payload["next_candidate"], {"model_id": "mimo-v2.5-pro", "profile": "AtomGit-mimo-v2.5-pro"})
        self.assertEqual(payload["advance_reason"], "PREDECLARED_PRE_MIMO25_RULE_APPLIED_AFTER_MIMO25_CEILING")
        self.assertFalse(payload["authority"]["f0"])


if __name__ == "__main__":
    unittest.main()
