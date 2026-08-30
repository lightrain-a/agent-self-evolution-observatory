from __future__ import annotations
import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PAPER=ROOT/"paper_drafts"/"c1-manuscript-strengthening-20260825"
class TestC1PactaV2Closure(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.closure=json.loads((PAPER/"c1-pacta-v2-pilot-closure-20260830.json").read_text())
  cls.audit=json.loads((PAPER/"c1-pacta-v2-claim-audit-20260830.json").read_text())
  cls.asset=json.loads((ROOT/"research_pipeline"/"c1_pacta_v2_policy_surface_measurement_failure_asset_20260830.json").read_text())["asset"]
  cls.registry=json.loads((ROOT/"research_pipeline"/"external_failure_assets.json").read_text())
 def test_fresh_split_and_shadow_realization(self):
  self.assertEqual(self.closure["fresh_pool"]["pilot_ids"],[352,239,271,437,506,261])
  self.assertEqual(self.closure["shadow"]["completed_calls"],144)
  self.assertEqual(self.closure["shadow"]["failed_calls"],0)
  self.assertEqual(self.closure["gate"]["open_ids"],[271,506,261])
  self.assertEqual(self.closure["gate"]["geometry_verdict"],"PASS_NON_DEGENERATE")
 def test_final_measurement_stop(self):
  final=self.closure["final_policy"]
  self.assertEqual(final["complete_calls"],60); self.assertEqual(final["failed_calls"],1)
  self.assertEqual(final["unattempted_calls"],227); self.assertEqual(final["failure_type"],"JSONDecodeError")
  self.assertEqual(final["retry_topup_imputation_replacement"],0)
  self.assertTrue(all(v is None for k,v in self.closure["effects"].items() if k!="reason"))
 def test_claim_boundary(self):
  authority=self.closure["claim_authority"]
  self.assertTrue(authority["gate_realization_claim"]); self.assertFalse(authority["preliminary_mechanism_effect_signal"])
  self.assertFalse(authority["utility_improvement_claim"]); self.assertEqual(authority["active_manuscript"],"R9")
  self.assertEqual(self.audit["status"],"PASS_CLAIM_BOUNDARIES")
 def test_research_os_writeback(self):
  expected="When the scientific claim concerns behavioral transport, a standalone semantic projector may be a poor proxy for the downstream policy. Counterfactual actionability should be measured at the policy surface itself and separated from same-condition stochasticity."
  self.assertEqual(self.asset["institutional_lesson"],expected)
  entry={"source_path":"research_pipeline/c1_pacta_v2_policy_surface_measurement_failure_asset_20260830.json","source_key":"asset"}
  self.assertEqual(self.registry["assets"].count(entry),1)
  self.assertFalse(self.asset["scientific_authority"])
if __name__=="__main__": unittest.main()
