from __future__ import annotations

import json
import unittest

from research_pipeline.agent_constraint_externality_runner_core import sha256_value
from research_pipeline.agent_constraint_externality_sq0_build import TOOL_CALL_CAP, load_cases
from research_pipeline.agent_constraint_externality_sq0_live import AUTH_OUTPUT, EXEC_CONTRACT, MODEL_ID, MODEL_PROFILE, MODEL_ROUND_CAP, Q1_OUTPUT


class SQ0MiMo25ProLiveTest(unittest.TestCase):
    def _verified(self, path):
        x=json.loads(path.read_text()); claimed=x["content_sha256"]; u=dict(x); u.pop("content_sha256")
        self.assertEqual(claimed,sha256_value(u)); return x

    def test_authorization_opens_only_sq0(self):
        x=self._verified(AUTH_OUTPUT)
        self.assertEqual(x["status"],"USER_AUTHORIZED_SQ0_TARGET_FAILURE_QUALIFICATION_AFTER_F0_UPTAKE_FAIL")
        self.assertTrue(x["authority"]["sq0_execution"])
        for key in ["f0_r1","probe","p1","toolsandbox","appworld_ul","paper_claim"]: self.assertFalse(x["authority"][key])

    def test_q1_is_zero_request_real_mcp(self):
        x=self._verified(Q1_OUTPUT)
        self.assertEqual(x["status"],"SQ0_MIMO25PRO_MCP_PREDISPATCH_PASS")
        self.assertEqual(x["codingplan_model_requests"],0)
        self.assertFalse(x["scientific_dispatch_sent"])
        self.assertEqual(x["session_mcp_progress_status"],"TOOLS_LISTED")
        self.assertGreater(x["session_mcp_tool_count"],0)

    def test_execution_contract_is_exact_and_nonconfirmatory(self):
        x=self._verified(EXEC_CONTRACT)
        self.assertEqual(x["status"],"SQ0_MIMO25PRO_V1_EXECUTION_AUTHORIZED")
        self.assertEqual(x["model"]["id"],MODEL_ID); self.assertEqual(x["model"]["profile"],MODEL_PROFILE)
        self.assertEqual(x["harness"]["tool_call_cap"],TOOL_CALL_CAP); self.assertEqual(x["harness"]["model_round_cap_per_case"],MODEL_ROUND_CAP)
        self.assertFalse(x["harness"]["retry_allowed"]); self.assertFalse(x["harness"]["replacement_allowed"])
        self.assertEqual(x["panel"]["case_count"],12); self.assertEqual(x["panel"]["case_ids"],[r["case_id"] for r in load_cases()])
        self.assertFalse(x["panel"]["confirmatory_reuse"])
        self.assertTrue(x["authority"]["sq0_execution"]); self.assertFalse(x["authority"]["f0_r1"]); self.assertFalse(x["authority"]["probe"]); self.assertFalse(x["authority"]["p1"])


if __name__=="__main__": unittest.main()
