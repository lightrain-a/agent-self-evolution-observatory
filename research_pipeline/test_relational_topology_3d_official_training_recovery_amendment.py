from __future__ import annotations
import hashlib,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OBJ='RELATIONAL-TOPOLOGY-STAGE-3D-20260831'; D=ROOT/'experiments/3d_official_training'/f'{OBJ}-official-training-recovery-amendment-v17a'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
class RecoveryAmendmentTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.x=json.loads((D/'runtime_amendment.json').read_text()); cls.code=(ROOT/'research_pipeline/relational_topology_official_training_dev_run_v17a.py').read_text()
 def test_zero_step_and_scope(self):
  self.assertEqual(self.x['observed_gap']['optimizer_steps_committed'],0); self.assertEqual(self.x['observed_gap']['scientific_outcomes'],0)
  r=self.x['repair']
  for k in ('scientific_change','training_math_change','model_change','data_change','seed_change','batch_size_change','optimizer_change','step_budget_change','mandatory_checkpoint_cadence_change','step0_anchor_is_scientific_checkpoint'): self.assertFalse(r[k],k)
  self.assertFalse(self.x['authority']['p1'])
 def test_wrapper_has_no_optimizer_math(self):
  self.assertNotIn('opt.step()',self.code); self.assertNotIn('total.backward()',self.code); self.assertIn('persist.train(',self.code); self.assertIn('base.save_checkpoint(',self.code)
 def test_step0_and_resume_guards(self):
  self.assertIn('step=0',self.code); self.assertIn('another matching training process is still alive',self.code); self.assertIn('resume path is not claim latest checkpoint',self.code); self.assertIn('resume checkpoint hash drift',self.code)
 def test_hashes(self):
  c=self.x['child_code']; self.assertEqual(c['recovery_wrapper_sha256'],sha(ROOT/'research_pipeline/relational_topology_official_training_dev_run_v17a.py')); self.assertEqual(c['entrypoint_sha256'],sha(ROOT/'scripts/run_relational_topology_3d_official_training_developmental_v17a.py'))
if __name__=='__main__': unittest.main()
