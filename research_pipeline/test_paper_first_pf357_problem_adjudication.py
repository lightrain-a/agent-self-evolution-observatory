from __future__ import annotations
import unittest
from .paper_first_pf357_problem_adjudication import build_pf357_problem_adjudication,validate_pf357_problem_adjudication

class PF357ProblemAdjudicationTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.state=build_pf357_problem_adjudication(); cls.by={r['id']:r for r in cls.state['rows']}
 def test_all_three_standalone_problems_stop(self):
  self.assertEqual(validate_pf357_problem_adjudication(self.state),[])
  self.assertEqual(self.state['summary']['stopped_standalone'],3)
  self.assertTrue(all(r['decision'].startswith('STOP_PF') for r in self.state['rows']))
 def test_pf3_reduces_to_rate_distortion_and_compression_lifecycle(self):
  r=self.by['PF-3']; self.assertIn('COMPRESSION_LIFECYCLE_CONTROL',r['decision']); self.assertIn('RATE_DISTORTION_COLLISION',r['paper_problem_status']); self.assertIn('rate-distortion',r['why_stop']); self.assertIn('compression-lifecycle-control',r['surviving_system_role'])
 def test_pf5_reduces_to_differential_testing(self):
  r=self.by['PF-5']; self.assertIn('DIFFERENTIAL_VERIFICATION',r['decision']); self.assertIn('differential behavioral testing',r['why_stop']); self.assertIn('DiffTestGen',r['strongest_collisions'][0])
 def test_pf7_reduces_to_change_impact_analysis(self):
  r=self.by['PF-7']; self.assertIn('EVIDENCE_IMPACT_REVALIDATION',r['decision']); self.assertIn('change-impact analysis',r['why_stop']); self.assertTrue(any('NameRTS' in x for x in r['strongest_collisions']))
 def test_no_downstream_authority_and_ai_is_advisory(self):
  self.assertFalse(self.state['policy']['local_validation_authorized'])
  self.assertTrue(all(all(v is False for v in r['authority'].values()) for r in self.state['rows']))
  self.assertTrue(all(r['authority']=='advisory-only' for r in self.state['reviews'].values()))

if __name__=='__main__': unittest.main()
