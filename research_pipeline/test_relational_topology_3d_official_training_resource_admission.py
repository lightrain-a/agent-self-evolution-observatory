from __future__ import annotations
import hashlib,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OBJ='RELATIONAL-TOPOLOGY-STAGE-3D-20260831'
D=ROOT/'experiments/3d_official_training'/f'{OBJ}-official-training-resource-admission-v16'
V13=ROOT/'experiments/3d_official_training'/f'{OBJ}-official-training-developmental-authority-v13'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
class AdmissionTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.x=json.loads((D/'admission.json').read_text())
 def test_parent_authority(self): self.assertEqual(self.x['authority']['parent_sha256'],sha(V13/'authority_grant.json'))
 def test_all_pass_zero_step(self):
  self.assertTrue(self.x['admission']['all_required_components'])
  for c,r in self.x['components'].items():
   self.assertEqual(r['status'],'RESOURCE_PREFLIGHT_PASS',c); self.assertEqual(r['optimizer_steps'],0,c); self.assertTrue(r['loss_finite']); self.assertTrue(r['grad_finite']); self.assertEqual(r['batch_size'],128)
 def test_sgp_pair_exact(self):
  a,b=self.x['components']['SGP-12'],self.x['components']['SGP-14']
  for k in ('initial_model_state_sha256','parameter_count','config_sha256','first_batch_keys_sha256','peak_allocated_vram_bytes','peak_reserved_vram_bytes'): self.assertEqual(a[k],b[k],k)
  self.assertEqual(a['initial_model_state_sha256'],'efd8ee84bf36e5ebfc9a191155495d5c540f289e20a117356c4b490a4c2fb3f3')
 def test_science_stays_closed(self):
  self.assertFalse(self.x['admission']['reproduction_may_start']); self.assertFalse(self.x['admission']['p1_may_start']); self.assertEqual(self.x['scientific_outcomes'],0)
  self.assertEqual(self.x['port_010']['status'],'HOLD_EVIDENCE_REVIEW_BLOCKED')
if __name__=='__main__': unittest.main()
