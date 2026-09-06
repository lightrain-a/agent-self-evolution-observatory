from __future__ import annotations
import hashlib,json,pathlib,unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
AUTH=ROOT/'generated/d2-failure-memory-provenance-r84-final-pt-only-analysis-authority.json'
R85=ROOT/'research_pipeline/failure_memory_semantic_control_r85_final_pt_analysis.py'

def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"),default=str)
def digest(v):return hashlib.sha256(canonical(v).encode()).hexdigest()

class R84R85Tests(unittest.TestCase):
 def test_authority_receipt_and_scope(self):
  x=json.loads(AUTH.read_text());self.assertEqual(x['receipt_sha256'],digest({k:v for k,v in x.items() if k!='receipt_sha256'}));a=x['authority'];self.assertTrue(a['analysis']);self.assertTrue(a['qwen_PT_read']);self.assertTrue(a['llama_PT_read']);self.assertFalse(a['qwen_TS_read']);self.assertFalse(a['paper_claim_change']);self.assertFalse(a['strong_model_execution'])
 def test_stage_sha_bindings(self):
  x=json.loads(AUTH.read_text());b=x['bindings'];self.assertEqual(b['qwen_terminal_ledger_sha256'],'58d0ece1be8911817bfd38c28619797c5c9bec3714c135ce9c00c85ce7cfb829');self.assertEqual(b['llama_terminal_ledger_sha256'],'461cc8ee3e203adb9f693fd0dbaf3b35460e456ebe5fdb8eac1bad5eb481841c');self.assertEqual(b['qwen_terminal_rows'],189);self.assertEqual(b['llama_terminal_rows'],132)
 def test_r85_filters_s_before_analysis(self):
  s=R85.read_text();self.assertIn('q=pt_only(q_all);l=pt_only(l_all)',s);self.assertIn('if any(str(x.get("arm"))=="S_shuffled" for x in q)',s);self.assertIn('"S_rows_read_by_R85":False',s)

if __name__=='__main__':unittest.main()
