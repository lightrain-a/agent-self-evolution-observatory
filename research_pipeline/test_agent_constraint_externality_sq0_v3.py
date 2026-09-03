from __future__ import annotations

import json
import unittest
from pathlib import Path

from research_pipeline.agent_constraint_externality_runner_core import sha256_value
from research_pipeline.agent_constraint_externality_sq0_v3_build import CONTRACT_OUTPUT, QUAL_OUTPUT, load_cases
from research_pipeline.agent_constraint_externality_sq0_v3_live import (
    AUTH_OUTPUT, EXEC_CONTRACT, Q1_OUTPUT, MODEL_ROUND_CAP, _futility_status,
)


class SQ0V3Tests(unittest.TestCase):
    def test_static_design_is_fresh_semantic_and_publicly_reachable(self) -> None:
        c=json.loads(CONTRACT_OUTPUT.read_text());q=json.loads(QUAL_OUTPUT.read_text())
        for payload in (c,q):
            claimed=payload["content_sha256"];u=dict(payload);u.pop("content_sha256")
            self.assertEqual(claimed,sha256_value(u))
        self.assertEqual(c["status"],"SQ0_V3_STATIC_DESIGN_READY")
        self.assertEqual(q["status"],"SQ0_V3_PUBLIC_REACHABILITY_PASS")
        self.assertEqual(c["case_count"],12);self.assertEqual(q["case_count"],12)
        self.assertFalse(c["v2r1_case_reuse"]);self.assertFalse(c["confirmatory_reuse"])
        self.assertEqual(c["target_app_families"]["FG"],["file_system","gmail"])
        self.assertEqual(c["target_app_families"]["TNF"],["file_system","simple_note","todoist"])
        self.assertEqual(q["max_public_tool_calls"],30);self.assertGreaterEqual(q["minimum_headroom"],18)
        self.assertTrue(all(r["target_success"] and not r["private_fixture_ids_used"] for r in q["public_oracles"]))
        self.assertFalse(c["authority"]["sq0_v3_execution"])

    def test_cases_are_unique_and_terminal_newline_only_is_prospectively_normalized(self) -> None:
        cases=load_cases();self.assertEqual(len(cases),12);self.assertEqual(len({c["case_id"] for c in cases}),12)
        self.assertEqual(sum(c["kind"]=="FG_SEMANTIC_V3" for c in cases),6)
        self.assertEqual(sum(c["kind"]=="TNF_SEMANTIC_V3" for c in cases),6)
        self.assertTrue(all("terminal newline" in c["fixture"]["rows"][1]["values"].get("content","") for c in cases if c["kind"]=="TNF_SEMANTIC_V3"))

    def test_futility_rule_is_mathematical_and_only_stops_when_pass_range_impossible(self) -> None:
        success=lambda: {"target_success":True,"usable_target_failure":False,"non_semantic_failure":False}
        failure=lambda: {"target_success":False,"usable_target_failure":True,"non_semantic_failure":False}
        self.assertIsNone(_futility_status([success(),success(),success(),failure()]))
        self.assertEqual(_futility_status([success(),success(),success(),success()]),"SQ0_V3_FUTILITY_TOO_EASY_STOP")
        self.assertEqual(_futility_status([failure() for _ in range(11)]),"SQ0_V3_FUTILITY_TOO_HARD_STOP")
        self.assertEqual(_futility_status([{"target_success":False,"usable_target_failure":False,"non_semantic_failure":True}]),"SQ0_V3_QUALIFICATION_INVALID_NON_SEMANTIC_FAILURE_STOP")

    def test_execution_freeze_is_zero_request_and_keeps_f0_closed(self) -> None:
        a=json.loads(AUTH_OUTPUT.read_text());q=json.loads(Q1_OUTPUT.read_text());c=json.loads(EXEC_CONTRACT.read_text())
        for payload in (a,q,c):
            claimed=payload["content_sha256"];u=dict(payload);u.pop("content_sha256");self.assertEqual(claimed,sha256_value(u))
        self.assertEqual(a["status"],"USER_AUTHORIZED_SQ0_V3_AFTER_TRANSPORT_QUALIFICATION_PASS")
        self.assertEqual(q["status"],"SQ0_V3_MIMO25PRO_MCP_PREDISPATCH_PASS");self.assertEqual(q["codingplan_model_requests"],0);self.assertFalse(q["scientific_dispatch_sent"])
        self.assertEqual(c["status"],"SQ0_V3_MIMO25PRO_EXECUTION_AUTHORIZED");self.assertEqual(c["harness"]["model_round_cap_per_case"],MODEL_ROUND_CAP)
        self.assertTrue(c["transport_inherited_without_new_model_request"])
        self.assertEqual(c["execution_policy"]["futility_early_stop"]["acceptable_final_failure_counts"],[9,10])
        self.assertTrue(c["authority"]["sq0_v3_execution"]);self.assertFalse(c["authority"]["f0_r1"]);self.assertFalse(c["authority"]["p1"])


if __name__=="__main__":unittest.main()
