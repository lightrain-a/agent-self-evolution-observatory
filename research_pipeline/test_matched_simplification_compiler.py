from __future__ import annotations
import unittest
from .matched_simplification_compiler import compile_matched_simplifications, compile_simplification_attribution

class MatchedSimplificationCompilerTest(unittest.TestCase):
 def test_compiles_domain_specific_and_shallow_controls(self):
  m=compile_matched_simplifications('x','causal memory controller with rollback search','declared baseline')
  keys={r['key'] for r in m['compiled_baselines']}
  self.assertIn('declared-strongest',keys)
  self.assertIn('same-representation-shallow',keys)
  self.assertIn('memory-policy-simple',keys)
  self.assertIn('noncausal-same-input',keys)
  self.assertIn('standard-algorithm',keys)
  self.assertGreaterEqual(m['baseline_count'],m['minimum_required_baselines'])
  self.assertEqual([r['tier'] for r in m['complexity_ladder']],[0,1,2,3])
  self.assertEqual(m['complexity_ladder'][-1]['key'],'proposed-mechanism')
  self.assertTrue(m['complexity_ladder_policy']['required_before_gpu'])
  self.assertEqual(m['complexity_ladder_policy']['minimum_empirical_lower_tiers'],3)
  self.assertEqual(m['complexity_ladder_policy']['no_headroom_action'],'stop_or_merge_before_expensive_transition')
  self.assertTrue(m['hidden_outcome_retuning_forbidden'])
  self.assertTrue(m['simplification_attribution_policy']['method_reduction_is_not_whole_paper_reduction'])
  self.assertTrue(m['complexity_ladder_policy']['live_economy_semantics_unchanged_during_shadow_validation'])

 def test_method_tie_can_be_attributed_without_mutating_live_economy_decision(self):
  s=compile_simplification_attribution(idea_id='x',primary_contribution_type='insight',claimed_layers=['problem','insight','method'],reproduced_layers=['method'],baseline_ref='same-information threshold',same_information=True)
  self.assertEqual(s['status'],'SECONDARY_OR_METHOD_REDUCTION_ONLY')
  self.assertEqual(s['attribution']['recommended_paper_effect'],'KEEP_PRIMARY_CONTRIBUTION_REVIEW')
  self.assertFalse(s['live_economy_decision_mutated'])
  self.assertFalse(s['scientific_authority'])

if __name__=='__main__': unittest.main()
