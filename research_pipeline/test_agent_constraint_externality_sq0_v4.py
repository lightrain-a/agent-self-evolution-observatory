from __future__ import annotations

import json
import unittest

from research_pipeline.agent_constraint_externality_runner_core import sha256_value
from research_pipeline.agent_constraint_externality_sq0_v4_build import CONTRACT_OUTPUT, QUAL_OUTPUT, load_cases
from research_pipeline.agent_constraint_externality_sq0_v4_live import (
    AUTH_OUTPUT, EXEC_CONTRACT, Q1_OUTPUT, MODEL_ROUND_CAP, _futility_status, _unit_id,
)


class SQ0V4Tests(unittest.TestCase):
    def _check_hash(self, payload: dict) -> None:
        claimed = payload["content_sha256"]
        unsigned = dict(payload); unsigned.pop("content_sha256")
        self.assertEqual(claimed, sha256_value(unsigned))

    def test_static_design_is_fresh_publicly_reachable_and_localized(self) -> None:
        contract = json.loads(CONTRACT_OUTPUT.read_text())
        qual = json.loads(QUAL_OUTPUT.read_text())
        self._check_hash(contract); self._check_hash(qual)
        self.assertEqual(contract["status"], "SQ0_V4_STATIC_DESIGN_READY")
        self.assertEqual(qual["status"], "SQ0_V4_PUBLIC_REACHABILITY_AND_FRESHNESS_PASS")
        self.assertEqual(contract["case_count"], 12)
        self.assertEqual(contract["case_kinds"], {"FG_SEMANTIC_V4": 6, "TNF_SEMANTIC_V4": 6})
        self.assertEqual(contract["design_change"]["FG_SEMANTIC_V4"], "V3_FG_MECHANISM_UNCHANGED_FRESH_PARAMETERIZATION_ONLY")
        self.assertTrue(contract["design_change"]["difficulty_not_from_tool_budget"])
        freshness = contract["freshness_audit"]
        self.assertTrue(freshness["case_ids_unique"])
        for key in ("case_id_overlap_count", "instruction_hash_overlap_count", "fixture_hash_overlap_count", "target_local_resource_hash_overlap_count"):
            self.assertEqual(freshness[key], 0)
        self.assertEqual(qual["max_public_tool_calls"], 48)
        self.assertEqual(qual["minimum_headroom"], 32)
        self.assertTrue(all(row["target_success"] and not row["private_fixture_ids_used"] for row in qual["public_oracles"]))
        self.assertFalse(contract["authority"]["sq0_v4_execution"])
        self.assertFalse(contract["authority"]["f0_r1"])

    def test_cases_and_unit_ids_are_fresh_v4_namespace(self) -> None:
        cases = load_cases()
        self.assertEqual(len(cases), 12)
        self.assertEqual(len({case["case_id"] for case in cases}), 12)
        self.assertEqual(sum(case["kind"] == "FG_SEMANTIC_V4" for case in cases), 6)
        self.assertEqual(sum(case["kind"] == "TNF_SEMANTIC_V4" for case in cases), 6)
        for case in cases:
            self.assertTrue(_unit_id(case["case_id"]).startswith("sq0v4:mimo-v2.5-pro|SQ0V4-"))

    def test_futility_rule_is_unchanged_and_mathematical(self) -> None:
        success = lambda: {"target_success": True, "usable_target_failure": False, "non_semantic_failure": False}
        failure = lambda: {"target_success": False, "usable_target_failure": True, "non_semantic_failure": False}
        self.assertIsNone(_futility_status([success(), success(), success(), failure()]))
        self.assertEqual(_futility_status([success(), success(), success(), success()]), "SQ0_V4_FUTILITY_TOO_EASY_STOP")
        self.assertEqual(_futility_status([failure() for _ in range(11)]), "SQ0_V4_FUTILITY_TOO_HARD_STOP")
        self.assertEqual(_futility_status([{"target_success": False, "usable_target_failure": False, "non_semantic_failure": True}]), "SQ0_V4_QUALIFICATION_INVALID_NON_SEMANTIC_FAILURE_STOP")

    def test_execution_freeze_is_zero_request_and_downstream_closed(self) -> None:
        auth = json.loads(AUTH_OUTPUT.read_text())
        q1 = json.loads(Q1_OUTPUT.read_text())
        contract = json.loads(EXEC_CONTRACT.read_text())
        for payload in (auth, q1, contract): self._check_hash(payload)
        self.assertEqual(auth["status"], "USER_AUTHORIZED_SQ0_V4_AFTER_V3_FUTILITY_CLOSEOUT_AND_STATIC_PASS")
        self.assertTrue(auth["authority"]["sq0_v4_execution"])
        self.assertFalse(auth["authority"]["f0_r1"])
        self.assertEqual(q1["status"], "SQ0_V4_MIMO25PRO_MCP_PREDISPATCH_PASS")
        self.assertEqual(q1["codingplan_model_requests"], 0)
        self.assertFalse(q1["scientific_dispatch_sent"])
        self.assertGreater(q1["session_mcp_tool_count"], 0)
        self.assertEqual(contract["status"], "SQ0_V4_MIMO25PRO_EXECUTION_AUTHORIZED")
        self.assertEqual(contract["harness"]["model_round_cap_per_case"], MODEL_ROUND_CAP)
        self.assertEqual(contract["harness"]["tool_call_cap"], 80)
        self.assertEqual(contract["execution_policy"]["futility_early_stop"]["acceptable_final_failure_counts"], [9, 10])
        self.assertTrue(contract["authority"]["sq0_v4_execution"])
        for key in ("f0_r1", "probe", "p1", "toolsandbox", "appworld_ul", "paper_claim"):
            self.assertFalse(contract["authority"][key])


if __name__ == "__main__":
    unittest.main()
