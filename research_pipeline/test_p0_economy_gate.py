from __future__ import annotations
import unittest
from .p0_admission import build_p0_admission_state
from .p0_economy_gate import evaluate_economy_card

class P0EconomyGateTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.state=build_p0_admission_state()['economy_gate']
 def test_retrospective_failure_classes_are_front_loaded(self):
  s=self.state['summary']
  self.assertEqual(s['ideas'],20)
  self.assertEqual(s['economy_ready'],0)
  self.assertEqual(s['matched_simplification_stops'],12)
  self.assertEqual(s['substrate_stops'],4)
  self.assertEqual(s['voi_stops'],0)
 def test_compiler_and_authority_are_required_before_future_pass(self):
  self.assertTrue(self.state['policy']['all_five_required_before_execution_compilation'])
  for row in self.state['rows']:
   self.assertEqual(row['gate_count'],5)
   simpl=next(g for g in row['gates'] if g['key']=='matched_simplification')
   compiler=(simpl.get('evidence') or {}).get('compiler') or {}
   self.assertGreaterEqual(compiler.get('baseline_count',0),2)
   self.assertTrue(compiler.get('hidden_outcome_retuning_forbidden'))
 def test_future_contract_requires_real_inventory_and_aggregation_ack(self):
  offline={'gpu0':{'status':'pass'},'checks':{'baseline_disagreement':{'status':'pass'},'effect_variation':{'status':'pass'},'competence_window':{'status':'pass'}},'updater_competence':{'passed':True}}
  setup={'exclusive_output_lock':True,'authority_mode':'single-writer-lease'}
  econ={'causal_unit':'memory x state','prediction_unit':'memory x task','effect_observable':'delta action','effect_moderators':'task context','effect_stability_scope':'same decision state','aggregation_risk':'','cheapest_falsifier':'cpu replay','decision_changing_outcomes':'pass->micro-p0; fail->stop','abandonment_condition':'simple baseline tie','substrate_inventory':{'effective_candidates_min':8,'fresh_heldout_min':12,'reserve_fraction_min':0.3,'target_variation_rule':'both signs','observed_effective_candidates':8,'observed_fresh_heldout':12,'observed_reserve_fraction':0.3}}
  row=evaluate_economy_card('x',offline,{'mechanism':'memory gate','baseline':'mean rule','economy':econ},setup)
  causal=next(g for g in row['gates'] if g['key']=='causal_unit_observable')
  self.assertFalse(causal['pass'])
  econ['aggregation_risk']='task aggregation can flip sign; validate state-local effect first'
  row=evaluate_economy_card('x',offline,{'mechanism':'memory gate','baseline':'mean rule','economy':econ},setup)
  self.assertTrue(next(g for g in row['gates'] if g['key']=='causal_unit_observable')['pass'])
  econ['substrate_inventory']['observed_fresh_heldout']=5
  row=evaluate_economy_card('x',offline,{'mechanism':'memory gate','baseline':'mean rule','economy':econ},setup)
  self.assertEqual(next(g for g in row['gates'] if g['key']=='substrate_inventory')['status'],'fail')

if __name__=='__main__': unittest.main()
