from __future__ import annotations
import unittest
from .p0_a12_soft_audit_f0 import DATA_ROOT,build
@unittest.skipUnless((DATA_ROOT/'first-divergence-audit-v1/state-table.csv').exists() and (DATA_ROOT/'full-support-table/raw-traces.jsonl').exists(),'frozen mem-xfer data unavailable')
class P0A12SoftAuditF0Test(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.a1,cls.a2=build()
 def test_a1_repair_is_simplified_not_promoted(self):
  a=self.a1; self.assertEqual(a['decision'],'STOP_REPAIR_SOFT_AUDIT_SIMPLE_TRIAGE_DOMINATES'); self.assertFalse(a['formal_p0_authorized']); self.assertFalse(a['harm_claim_authorized'])
  branch=a['future_branch_policy']; prior=a['matched_baselines']['target_family_prior']; trig=a['matched_baselines']['simple_h1_navigate_trigger']
  self.assertEqual(branch['nonzero_recall'],.4); self.assertGreater(prior['nonzero_recall'],branch['nonzero_recall']); self.assertLessEqual(prior['action_step_cost'],branch['action_step_cost']); self.assertEqual(trig['nonzero_recall'],branch['nonzero_recall']); self.assertLess(trig['action_step_cost'],branch['action_step_cost'])
  self.assertTrue(all(x['nonzero_recall']==.4 for x in a['context_signature_rescue'].values()))
 def test_a2_adaptive_depth_is_dominated_by_fixed_h1(self):
  a=self.a2; self.assertEqual(a['decision'],'STOP_REPAIR_FIXED_HORIZON_DOMINATES'); self.assertFalse(a['formal_p0_authorized']); ad=a['future_adaptive']; fixed=a['future_fixed_h1']; self.assertEqual(ad['nonzero_recall'],fixed['nonzero_recall']); self.assertGreater(ad['action_step_cost'],fixed['action_step_cost'])
  self.assertTrue(all(x['future']['nonzero_recall']==fixed['nonzero_recall'] and x['future']['cost_fraction']>=fixed['cost_fraction'] for x in a['categorical_adaptive_sweep']))
if __name__=='__main__': unittest.main()
