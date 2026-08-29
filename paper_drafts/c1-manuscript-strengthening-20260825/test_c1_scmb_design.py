from __future__ import annotations
import json, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
OLD={26,124,126,142,143,144,147,149,150,164,165,167,190,192,227,228,229,230,233,279,280,281,282,319,320,321,322,323,329,330,331,333,358,360,362,384}
class TestSCMB(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.c=json.loads((HERE/'c1-scmb-pilot-contract-20260829.json').read_text())
  cls.f=json.loads((HERE/'c1-scmb-pilot-freeze-20260829.json').read_text())
  cls.p=json.loads((HERE/'c1-scmb-data-preflight-20260829.json').read_text())
 def test_fresh(self):
  ids={x['future_task'] for x in self.f['selection']['pilot']}; hold={x['future_task'] for x in self.f['selection']['template_holdout']}
  self.assertEqual(len(ids),12); self.assertEqual(len(hold),19); self.assertFalse(ids&hold); self.assertFalse((ids|hold)&OLD)
 def test_preflight(self):
  self.assertEqual(self.p['status'],'PASS_ZERO_PROVIDER_FRESH_PACKET_PREFLIGHT'); self.assertEqual(self.p['checks']['provider_calls'],0); self.assertEqual(self.p['checks']['pilot_unique_templates'],12); self.assertGreaterEqual(self.p['checks']['pilot_unique_sources'],8)
 def test_arms_and_gate(self):
  self.assertEqual(set(self.c['arms']),{'A0_NATIVE','A1_MEMORY_ONLY_ADAPTER','A2_STATE_CONDITIONED_BINDING'}); self.assertIn('mean(D) >= 0.05',self.c['primary']['pilot_gate']); self.assertIn('D>0 in at least 6/12 states',self.c['primary']['pilot_gate'])
 def test_novelty_boundary(self):
  self.assertTrue(self.c['literature_boundary']['not_novel_method']); self.assertIn('SAMem',self.c['literature_boundary']['nearest_work'][0]); self.assertFalse(self.c['authority']['confirmatory'])
if __name__=='__main__':unittest.main()
