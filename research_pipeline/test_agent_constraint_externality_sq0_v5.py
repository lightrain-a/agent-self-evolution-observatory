from __future__ import annotations

import json
import unittest

from research_pipeline.agent_constraint_externality_runner_core import sha256_value
from research_pipeline.agent_constraint_externality_sq0_v5_build import CONTRACT_OUTPUT, QUAL_OUTPUT, load_cases
from research_pipeline.agent_constraint_externality_sq0_v5_live import AUTH_OUTPUT, EXEC_CONTRACT, Q1_OUTPUT, MODEL_ROUND_CAP, _futility_status, _unit_id


class SQ0V5Tests(unittest.TestCase):
    def _hash(self,payload:dict)->None:
        c=payload["content_sha256"];u=dict(payload);u.pop("content_sha256");self.assertEqual(c,sha256_value(u))

    def test_static_design_is_final_fresh_and_publicly_reachable(self)->None:
        c=json.loads(CONTRACT_OUTPUT.read_text());q=json.loads(QUAL_OUTPUT.read_text());self._hash(c);self._hash(q)
        self.assertEqual(c["status"],"SQ0_V5_STATIC_DESIGN_READY_FINAL_CALIBRATION")
        self.assertTrue(c["final_sq0_calibration_iteration"]);self.assertEqual(c["failure_to_pass_disposition"],"STOP_SQ0_DEVELOPMENT_NO_V6")
        self.assertEqual(q["status"],"SQ0_V5_PUBLIC_REACHABILITY_AND_FRESHNESS_PASS_FINAL_CALIBRATION")
        self.assertEqual(c["case_kinds"],{"FG_SEMANTIC_V5":6,"TNF_SEMANTIC_V5":6})
        self.assertEqual(c["design_change"]["TNF_SEMANTIC_V5"],"V4_SEMANTIC_DECISION_GRAPH_UNCHANGED_PLUS_EXPLICIT_OUTPUT_FIELD_MAPPING")
        f=c["freshness_audit"];self.assertTrue(f["case_ids_unique"])
        for k in ("case_id_overlap_count","instruction_hash_overlap_count","fixture_hash_overlap_count","target_local_resource_hash_overlap_count"):self.assertEqual(f[k],0)
        self.assertEqual(q["max_public_tool_calls"],48);self.assertEqual(q["minimum_headroom"],32)
        self.assertTrue(all(r["target_success"] and not r["private_fixture_ids_used"] for r in q["public_oracles"]))
        self.assertFalse(c["authority"]["sq0_v5_execution"]);self.assertFalse(c["authority"]["f0_r1"])

    def test_cases_and_unit_namespace_are_v5(self)->None:
        cases=load_cases();self.assertEqual(len(cases),12);self.assertEqual(len({c["case_id"] for c in cases}),12)
        self.assertEqual(sum(c["kind"]=="FG_SEMANTIC_V5" for c in cases),6);self.assertEqual(sum(c["kind"]=="TNF_SEMANTIC_V5" for c in cases),6)
        for c in cases:self.assertTrue(_unit_id(c["case_id"]).startswith("sq0v5:mimo-v2.5-pro|SQ0V5-"))
        for c in cases:
            if c["kind"]=="TNF_SEMANTIC_V5":
                route=next(r for r in c["fixture"]["rows"] if r["app"]=="simple_note" and str(r["values"].get("title","")).startswith("sq0v5-route-tnf-"))
                self.assertIn("EXACT_OUTPUT_MAPPING",route["values"]["content"])
                self.assertIn("POLICY=<POLICY_CODE>",route["values"]["content"])

    def test_futility_window_is_unchanged(self)->None:
        s=lambda:{"target_success":True,"usable_target_failure":False,"non_semantic_failure":False};f=lambda:{"target_success":False,"usable_target_failure":True,"non_semantic_failure":False}
        self.assertEqual(_futility_status([s(),s(),s(),s()]),"SQ0_V5_FUTILITY_TOO_EASY_STOP")
        self.assertEqual(_futility_status([f() for _ in range(11)]),"SQ0_V5_FUTILITY_TOO_HARD_STOP")
        self.assertEqual(_futility_status([{"target_success":False,"usable_target_failure":False,"non_semantic_failure":True}]),"SQ0_V5_QUALIFICATION_INVALID_NON_SEMANTIC_FAILURE_STOP")

    def test_execution_freeze_is_zero_request_and_final_stop_rule(self)->None:
        a=json.loads(AUTH_OUTPUT.read_text());q=json.loads(Q1_OUTPUT.read_text());c=json.loads(EXEC_CONTRACT.read_text())
        for x in (a,q,c):self._hash(x)
        self.assertEqual(a["status"],"USER_AUTHORIZED_SQ0_V5_AFTER_V4_TOO_HARD_CLOSEOUT_AND_STATIC_PASS")
        self.assertEqual(q["status"],"SQ0_V5_MIMO25PRO_MCP_PREDISPATCH_PASS");self.assertEqual(q["codingplan_model_requests"],0);self.assertFalse(q["scientific_dispatch_sent"])
        self.assertEqual(c["status"],"SQ0_V5_MIMO25PRO_EXECUTION_AUTHORIZED");self.assertEqual(c["harness"]["model_round_cap_per_case"],MODEL_ROUND_CAP)
        self.assertEqual(c["execution_policy"]["failure_to_pass_disposition"],"STOP_SQ0_DEVELOPMENT_NO_V6")
        self.assertEqual(c["execution_policy"]["futility_early_stop"]["acceptable_final_failure_counts"],[9,10])
        self.assertTrue(c["authority"]["sq0_v5_execution"])
        for k in ("f0_r1","probe","p1","toolsandbox","appworld_ul","paper_claim"):self.assertFalse(c["authority"][k])

if __name__=="__main__":unittest.main()
