from __future__ import annotations
import hashlib,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OBJ='RELATIONAL-TOPOLOGY-STAGE-3D-20260831'
D=ROOT/'experiments/3d_official_training'/f'{OBJ}-official-training-persistence-amendment-v16a'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
class PersistenceAmendmentTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.x=json.loads((D/'runtime_amendment.json').read_text()); cls.code=(ROOT/'research_pipeline/relational_topology_official_training_dev_run_v16a.py').read_text()
 def test_zero_step_gap(self): self.assertEqual(self.x['observed_gap']['optimizer_steps_committed'],0); self.assertEqual(self.x['observed_gap']['scientific_outcomes'],0)
 def test_scope_unchanged(self):
  r=self.x['repair']
  for k in ('scientific_change','training_math_change','model_change','data_change','seed_change','batch_size_change','optimizer_change','step_budget_change','checkpoint_change'): self.assertFalse(r[k],k)
  self.assertFalse(self.x['authority']['p1']); self.assertEqual(self.x['authority']['scientific_outcomes'],0)
 def test_wrapper_contains_no_training_math(self):
  self.assertNotIn('opt.step()',self.code); self.assertNotIn('total.backward()',self.code); self.assertNotIn('ema.step(',self.code)
  self.assertIn('base.train(',self.code)
 def test_required_paths_are_frozen(self):
  req=set(self.x['required_root_paths_created_before_step1'])
  expected={'manifest.json','authority.json','environment.json','git_state.json','dataset_manifest.json','corpus_manifest.json','model_manifest.json','config.yaml','resource_preflight.json','training_events.jsonl','loss.jsonl','checkpoint_manifest.jsonl','heartbeat.json','failures.jsonl','stdout.log','stderr.log','final_training_summary.json'}
  self.assertEqual(req,expected)
  for name in expected-{ 'resource_preflight.json'}: self.assertIn(name,self.code)
 def test_child_hashes(self):
  c=self.x['child_code']; self.assertEqual(c['persistence_wrapper_sha256'],sha(ROOT/'research_pipeline/relational_topology_official_training_dev_run_v16a.py')); self.assertEqual(c['entrypoint_sha256'],sha(ROOT/'scripts/run_relational_topology_3d_official_training_developmental_v16a.py'))
if __name__=='__main__': unittest.main()
