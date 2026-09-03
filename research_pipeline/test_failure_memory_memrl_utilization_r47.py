from __future__ import annotations
import copy,json,unittest
from pathlib import Path
from .failure_memory_memrl_utilization_r47 import ARMS,analyze,arm_order,plan,reverse_blocks,u4_map
ROOT=Path(__file__).resolve().parents[1]
class R47UtilizationContractTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=json.loads((ROOT/'generated/d2-failure-memory-provenance-r43-memrl-g8-execution-manifest.json').read_text())
  # Synthetic frozen rows reproduce only the R47 scheduling contract; no validation outcome is read.
  ids=cls.m['execution_manifest']['utilization_qualification']['representative_ids']
  cls.q={'status':'SOURCE_QUALIFICATION_PASS_RETRIEVAL_FROZEN_VALIDATION_STILL_SEALED'}
  cls.f={'rows':[{'cohort':'utilization','validation_task_id':x,'selected':([] if x=='483' else [{'content':f'memory-{x}','source_task_id':f's-{x}','source_outcome_success':True}])} for x in ids]}
 def test_schedule_is_complete_deterministic_and_preoutcome(self):
  a=plan(self.m,self.q,self.f);b=plan(self.m,self.q,self.f)
  self.assertEqual(a['plan_sha256'],b['plan_sha256']);self.assertEqual(a['utilization_outcomes_observed_when_plan_created'],0);self.assertFalse(a['primary_confirmatory_units_opened'])
  self.assertEqual(len(a['schedule']),8);self.assertTrue(all(sorted(x['arm_order'])==sorted(ARMS) for x in a['schedule']))
 def test_u4_never_self_and_null_target_is_not_replaced_in_primary_arm(self):
  ids=self.m['execution_manifest']['utilization_qualification']['representative_ids'];by={r['validation_task_id']:r for r in self.f['rows']};mp=u4_map(20260825,by,ids)
  self.assertTrue(all(k!=v for k,v in mp.items()));self.assertIn('483',mp);self.assertNotEqual(mp['483'],'483')
 def test_arm_order_deterministic(self):
  self.assertEqual(arm_order(20260825,'350'),arm_order(20260825,'350'));self.assertEqual(set(arm_order(20260825,'350')),set(ARMS))
 def test_reverse_control_preserves_all_blocks(self):
  x='Task: x\n\n1. first\n\n2. second\n\n3. third';y=reverse_blocks(x);self.assertTrue(all(z in y for z in ['Task: x','1. first','2. second','3. third']));self.assertNotEqual(x,y)
 def test_promotion_uses_first_action_not_terminal_success(self):
  pl=plan(self.m,self.q,self.f);rows=[]
  for tid in pl['utilization_ids']:
   for arm in ARMS:
    action='TRUE' if arm=='U1_true_memory' and tid in pl['utilization_ids'][:3] else 'BASE'
    rows.append({'task_id':tid,'arm':arm,'status':'COMPLETE','first_executable_action':action,'terminal_success_diagnostic':arm=='U0_no_memory'})
  out=analyze(pl,rows);self.assertTrue(out['pass']);self.assertEqual(out['u1_specific_first_action_units'],3);self.assertEqual(out['u2_vs_u0_divergence_units'],0);self.assertFalse(out['terminal_success_used_for_promotion'])
 def test_placebo_divergence_can_block_promotion(self):
  pl=plan(self.m,self.q,self.f);rows=[]
  for i,tid in enumerate(pl['utilization_ids']):
   for arm in ARMS:
    action='U1' if arm=='U1_true_memory' and i<3 else ('P' if arm=='U2_null_memory' and i<3 else 'BASE')
    rows.append({'task_id':tid,'arm':arm,'status':'COMPLETE','first_executable_action':action,'terminal_success_diagnostic':True})
  out=analyze(pl,rows);self.assertFalse(out['pass']);self.assertEqual(out['u1_specific_first_action_units'],3);self.assertEqual(out['u2_vs_u0_divergence_units'],3)
if __name__=='__main__':unittest.main()
