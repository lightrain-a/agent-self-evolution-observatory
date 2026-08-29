from __future__ import annotations
import hashlib,json,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
class T(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=json.loads((HERE/'c1-r9-scmb-package-manifest-20260829.json').read_text());cls.c=json.loads((HERE/'c1-scmb-pilot-closure-20260829.json').read_text());cls.v=json.loads((HERE/'c1-scmb-independent-verification-20260829.json').read_text());cls.res=(HERE/'source-r9/sections/04_variance_protocol.tex').read_text();cls.rel=(HERE/'source-r9/sections/05_related.tex').read_text();cls.con=(HERE/'source-r9/sections/06_limitations_conclusion.tex').read_text()
 def test_result(self):
  self.assertAlmostEqual(self.v['means']['U_A0_NATIVE'],.125);self.assertAlmostEqual(self.v['means']['U_A1_MEMORY_ONLY_ADAPTER'],1/12);self.assertAlmostEqual(self.v['means']['U_A2_STATE_CONDITIONED_BINDING'],5/24);self.assertAlmostEqual(self.v['means']['D'],.125);self.assertEqual(self.v['D_signs'],{'positive':3,'negative':4,'zero':5})
 def test_gate_not_upgraded(self):
  self.assertFalse(self.c['primary_result']['pre_registered_gate_pass']);self.assertIn('heterogeneous',self.m['result_boundary'].lower());self.assertIn('does not earn universal repair authority',self.res.lower());self.assertNotIn('validated general repair',self.res.lower())
 def test_novelty(self):
  self.assertIn('SAMem',self.rel);self.assertIn('not our novelty',self.rel);self.assertIn('do not claim this adapter as method novelty',self.res)
 def test_holdout(self):
  self.assertEqual(self.c['execution']['fresh_19_holdout_calls'],0);self.assertFalse(self.c['authority']['fresh_19_confirmatory']);self.assertIn('19-template holdout untouched',self.res)
 def test_pdf_hash(self):
  p=HERE/'C1-stage-resolved-r9-state-binding.pdf';self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),self.m['files']['pdf']['sha256']);self.assertTrue(self.m['paper_qa']['fonts_embedded']);self.assertTrue(self.m['paper_qa']['conclusion_on_page9'])
 def test_claim_boundary(self):
  joined=(self.res+'\n'+self.con).lower();self.assertIn('proof of concept',joined);self.assertIn('fails the preregistered consistency gate',joined);self.assertIn('does not earn universal repair authority',joined)
if __name__=='__main__':unittest.main()
