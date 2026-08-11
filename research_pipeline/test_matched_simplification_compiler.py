from __future__ import annotations
import unittest
from .matched_simplification_compiler import compile_matched_simplifications

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

if __name__=='__main__': unittest.main()
