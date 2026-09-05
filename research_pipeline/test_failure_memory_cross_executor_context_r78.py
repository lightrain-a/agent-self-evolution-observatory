from __future__ import annotations
import hashlib,json,pathlib,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
P=ROOT/'generated/d2-failure-memory-provenance-r78-cross-executor-discordant-context.json'
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
class R78Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.x=json.loads(P.read_text())
 def test_receipt(self):
  y=dict(self.x);r=y.pop('receipt_sha256');self.assertEqual(r,digest(y))
 def test_all_llama_flips_are_qwen_concordant(self):
  self.assertEqual(len(self.x['rows']),4)
  self.assertTrue(all(r['Llama_terminal_discordant'] for r in self.x['rows']))
  self.assertTrue(all(not r['Qwen_terminal_discordant'] for r in self.x['rows']))
 def test_not_scalar_strength_claim(self):
  s=self.x['summary'];self.assertEqual(s['Qwen_both_success_task_ids'],['125','193']);self.assertEqual(s['Qwen_both_fail_task_ids'],['136','327']);self.assertFalse(s['scalar_model_strength_explanation_supported']);self.assertFalse(self.x['changes_R72_R73_primary_inference'])
if __name__=='__main__':unittest.main()
