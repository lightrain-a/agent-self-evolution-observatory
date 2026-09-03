from __future__ import annotations
import json,unittest
from research_pipeline.agent_constraint_externality_runner_core import sha256_value
from research_pipeline.agent_constraint_externality_sq0_v2r1_build import CONTRACT_OUTPUT,QUAL_OUTPUT,build_cases,load_cases
from research_pipeline.agent_constraint_externality_sq0_v2r1_transport import CONTRACT_OUTPUT as TQ_CONTRACT,build_case
from research_pipeline.agent_constraint_externality_sq0_v2_void import OUTPUT as V2_VOID

class SQ0V2R1Test(unittest.TestCase):
 def _v(self,p):
  x=json.loads(p.read_text());c=x['content_sha256'];u=dict(x);u.pop('content_sha256');self.assertEqual(c,sha256_value(u));return x
 def test_v2_void_is_non_scientific_contamination(self):
  x=self._v(V2_VOID);self.assertEqual(x['status'],'SQ0_V2_VOID_NATIVE_READ_FILE_SCHEMA_CONTAMINATION');self.assertEqual(x['valid_sq0_v2_measurements'],0);self.assertEqual(x['appworld_tool_calls_executed'],0);self.assertEqual(x['codingplan_account_window_requests_spent'],1);self.assertFalse(x['authority']['sq0_v2_r1_execution'])
 def test_fresh_v2r1_cases_and_static_reachability(self):
  rows=build_cases();self.assertEqual(len(rows),12);self.assertEqual(len({r['case_id'] for r in rows}),12);self.assertTrue(all(r['case_id'].startswith('SQ0V2R1-') for r in rows));self.assertEqual(sha256_value(rows),sha256_value(load_cases()))
  c=self._v(CONTRACT_OUTPUT);q=self._v(QUAL_OUTPUT);self.assertEqual(c['status'],'SQ0_V2R1_STATIC_DESIGN_READY');self.assertFalse(c['v2_case_reuse']);self.assertFalse(c['confirmatory_reuse']);self.assertEqual(q['status'],'SQ0_V2R1_PUBLIC_REACHABILITY_PASS');self.assertEqual(q['provider_requests'],0);self.assertGreaterEqual(q['minimum_headroom'],15);self.assertTrue(all(r['target_success'] for r in q['public_oracles']))
 def test_transport_contract_is_non_scientific_and_pre_execution(self):
  c=self._v(TQ_CONTRACT);self.assertEqual(c['status'],'SQ0_V2R1_TRANSPORT_QUALIFICATION_AUTHORIZED');self.assertTrue(c['public_oracle_pass']);self.assertTrue(c['authority']['transport_qualification']);self.assertFalse(c['authority']['sq0_v2r1_execution']);self.assertFalse(c['authority']['f0_r1']);self.assertEqual(c['provider_requests_before_execution'],0);self.assertEqual(build_case()['case_id'],'SQ0V2R1-TRANSPORT-TQ0')
if __name__=='__main__':unittest.main()
