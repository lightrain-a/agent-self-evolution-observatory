from __future__ import annotations
import unittest
from .paper_first_idea_incubation import build_paper_first_idea_incubation, validate_paper_first_idea_incubation

class PaperFirstIdeaIncubationTest(unittest.TestCase):
 def setUp(self): self.state=build_paper_first_idea_incubation()
 def test_premortem_is_valid_and_has_no_unverified_p0_promotion(self):
  self.assertEqual(validate_paper_first_idea_incubation(self.state),[])
  s=self.state['summary']; self.assertEqual((s['candidates'],s['advance_to_paper_design'],s['revise_novelty_boundary'],s['blocked_collision']),(9,4,3,2))
  self.assertEqual((s['p0_authorized'],s['gpu_authorized']),(0,0))
  self.assertTrue(self.state['policy']['explicit_human_promotion_required_for_p0'])
  self.assertTrue(self.state['policy']['p0_lifecycle_does_not_equal_execution_authority'])
 def test_every_candidate_is_paper_first_and_collision_aware(self):
  ids=set()
  for row in self.state['candidates']:
   self.assertTrue(row['id'].startswith('PF-')); self.assertNotIn(row['id'],ids); ids.add(row['id'])
   for key in ('paper_problem','novelty_boundary','principle','method','strongest_baseline','local_falsifier','nearest_work','collision_risk'): self.assertTrue(row[key],(row['id'],key))
   self.assertFalse(row['p0_authorized']); self.assertFalse(row['gpu_authorized'])
 def test_batch_has_breadth_and_explicit_collision_memory(self):
  self.assertGreaterEqual(self.state['summary']['themes'],6)
  blocked=[r for r in self.state['candidates'] if r['verdict']=='BLOCK_COLLISION']
  self.assertEqual([r['id'] for r in blocked],['PF-8','PF-9'])
  by_id={r['id']:r for r in blocked}
  self.assertTrue(any('2607.24300' in x['ref'] for x in by_id['PF-8']['nearest_work']))
  self.assertTrue(any('2606.11559' in x['ref'] for x in by_id['PF-9']['nearest_work']))
  self.assertEqual(by_id['PF-9']['theme'],'protocol-validity')
  self.assertFalse(by_id['PF-9']['p0_authorized']); self.assertFalse(by_id['PF-9']['gpu_authorized'])

if __name__=='__main__': unittest.main()
