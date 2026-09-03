from __future__ import annotations

import json
import unittest

from research_pipeline.agent_constraint_externality_runner_core import sha256_value
from research_pipeline.agent_constraint_externality_sq0_v2_build import CONTRACT_OUTPUT, OUTPUT_BUNDLE, QUAL_OUTPUT, TOOL_CALL_CAP, build_cases, load_cases
from research_pipeline.agent_constraint_externality_sq0_v2_live import AUTH_OUTPUT, EXEC_CONTRACT, MODEL_ID, MODEL_PROFILE, MODEL_ROUND_CAP, Q1_OUTPUT

class SQ0V2Test(unittest.TestCase):
    def _v(self,path):
        x=json.loads(path.read_text()); c=x['content_sha256']; u=dict(x); u.pop('content_sha256'); self.assertEqual(c,sha256_value(u)); return x
    def test_static_cases_are_fresh_and_reachable(self):
        rows=build_cases(); self.assertEqual(len(rows),12); self.assertEqual(len({r['case_id'] for r in rows}),12); self.assertTrue(all(r['case_id'].startswith('SQ0V2-') for r in rows)); self.assertEqual(sha256_value(rows),sha256_value(load_cases(OUTPUT_BUNDLE)))
        c=self._v(CONTRACT_OUTPUT); q=self._v(QUAL_OUTPUT); self.assertEqual(c['status'],'SQ0_V2_TARGET_CHALLENGE_STATIC_DESIGN_READY'); self.assertFalse(c['v1_case_reuse']); self.assertFalse(c['confirmatory_reuse']); self.assertEqual(c['tool_call_cap'],TOOL_CALL_CAP); self.assertEqual(q['status'],'SQ0_V2_PUBLIC_REACHABILITY_PASS'); self.assertLessEqual(q['max_public_tool_calls'],26); self.assertGreaterEqual(q['minimum_headroom'],10); self.assertEqual(q['provider_requests'],0)
    def test_q1_and_authority_are_v2_only(self):
        q=self._v(Q1_OUTPUT); a=self._v(AUTH_OUTPUT); c=self._v(EXEC_CONTRACT)
        self.assertEqual(q['status'],'SQ0_V2_MIMO25PRO_MCP_PREDISPATCH_PASS'); self.assertEqual(q['codingplan_model_requests'],0); self.assertFalse(q['scientific_dispatch_sent'])
        self.assertEqual(a['status'],'USER_AUTHORIZED_SQ0_V2_DEVELOPMENT_ITERATION_AFTER_V1_TOO_EASY'); self.assertTrue(a['authority']['sq0_v2_execution']); self.assertFalse(a['authority']['f0_r1']); self.assertFalse(a['authority']['p1'])
        self.assertEqual(c['status'],'SQ0_V2_MIMO25PRO_EXECUTION_AUTHORIZED'); self.assertEqual(c['model']['id'],MODEL_ID); self.assertEqual(c['model']['profile'],MODEL_PROFILE); self.assertEqual(c['harness']['tool_call_cap'],TOOL_CALL_CAP); self.assertEqual(c['harness']['model_round_cap_per_case'],MODEL_ROUND_CAP); self.assertFalse(c['harness']['retry_allowed']); self.assertFalse(c['harness']['replacement_allowed']); self.assertFalse(c['authority']['f0_r1']); self.assertFalse(c['authority']['probe']); self.assertFalse(c['authority']['p1'])

if __name__=='__main__': unittest.main()
