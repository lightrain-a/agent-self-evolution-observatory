from __future__ import annotations
import unittest
from .p0_admission import build_p0_admission_state
from .p0_economy_gate import evaluate_economy_card

class P0EconomyGateTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.state=build_p0_admission_state()['economy_gate']
 def test_retrospective_failure_classes_are_front_loaded(self):
  s=self.state['summary']
  self.assertEqual(s['ideas'],27)
  self.assertEqual(s['economy_ready'],0)
  self.assertEqual(s['matched_simplification_stops'],19)
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
 def test_support_hold_cannot_be_relabelled_as_simplification_stop(self):
  offline={'decision':'HOLD_F0_SUPPORT_INSUFFICIENT','gpu0':{'status':'hold-f0-support-insufficient'},'checks':{'baseline_disagreement':{'status':'fail'},'effect_variation':{'status':'fail'},'competence_window':{'status':'pass'}},'updater_competence':{'passed':False,'status':'hold-support-insufficient'},'substrate_inventory':{'observed_effective_candidates':18,'observed_fresh_heldout':9,'observed_reserve_fraction':0.5}}
  setup={'exclusive_output_lock':True,'authority_mode':'single-writer-lease'}
  econ={'causal_unit':'fault x repair','prediction_unit':'fault x repair','effect_observable':'repair gain','effect_moderators':'fault','effect_stability_scope':'local','aggregation_risk':'macro can hide local support','cheapest_falsifier':'local f0','decision_changing_outcomes':'support pass -> method admission','abandonment_condition':'support remains insufficient','substrate_inventory':{'effective_candidates_min':18,'fresh_heldout_min':9,'reserve_fraction_min':0.25,'target_variation_rule':'heterogeneous repair ownership'}}
  row=evaluate_economy_card('support-hold',offline,{'mechanism':'router','baseline':'fixed surface','economy':econ},setup)
  self.assertEqual(next(g for g in row['gates'] if g['key']=='matched_simplification')['status'],'pending')
  self.assertEqual(next(g for g in row['gates'] if g['key']=='substrate_inventory')['status'],'pending')
  self.assertEqual(row['primary_stop_class'],'')

if __name__=='__main__': unittest.main()
