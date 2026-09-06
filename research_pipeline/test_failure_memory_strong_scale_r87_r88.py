from __future__ import annotations
import hashlib,json,pathlib,unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
R87=ROOT/'generated/d2-failure-memory-provenance-r87-strong-scale-12run-protocol.json'
SERVER=ROOT/'research_pipeline/failure_memory_strong_scale_r88_server.py'
RUNNER=ROOT/'research_pipeline/failure_memory_strong_scale_r88_runner.py'

def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"),default=str)
def digest(v):return hashlib.sha256(canonical(v).encode()).hexdigest()

class StrongScaleR87R88Tests(unittest.TestCase):
 def test_r87_receipt_and_schedule(self):
  x=json.loads(R87.read_text());self.assertEqual(x['receipt_sha256'],digest({k:v for k,v in x.items() if k!='receipt_sha256'}));self.assertEqual(x['panel']['trajectory_count'],12);self.assertEqual(len(x['panel']['schedule']),12);self.assertFalse(x['authority']['strong_model_execution']);self.assertEqual(x['model']['repository'],'Qwen/Qwen2.5-32B-Instruct')
 def test_server_is_exact_float16_provider_path(self):
  s=SERVER.read_text();self.assertIn('Qwen2.5-32B-Instruct-c53f76495664',s);self.assertIn('LocalQwenProvider',s);self.assertNotIn('4bit',s.lower());self.assertNotIn('8bit',s.lower());self.assertIn('temperature=float(payload.get("temperature") or 0.0)',s)
 def test_runner_reuses_r73_execution_and_has_no_analysis(self):
  s=RUNNER.read_text();self.assertIn('r73.run_attempt',s);self.assertIn('r72.render_contexts',s);self.assertIn('r73.prompt_for',s);self.assertIn('if a.validate_only:',s);self.assertNotIn('effect_detected',s);self.assertNotIn('paired_risk_difference',s)

if __name__=='__main__':unittest.main()
