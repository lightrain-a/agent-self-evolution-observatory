from __future__ import annotations
import hashlib,json,pathlib,unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]

def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"),default=str)
def valid(v):return v.get("receipt_sha256")==hashlib.sha256(canonical({k:x for k,x in v.items() if k!="receipt_sha256"}).encode()).hexdigest()
def load(name):return json.loads((ROOT/"generated"/name).read_text())

class R82AnalysisPrepTests(unittest.TestCase):
    def setUp(self):
        self.lm=load("d2-failure-memory-provenance-r82-llama-path-equivalent-execution-manifest.json")
        self.la=load("d2-failure-memory-provenance-r82-llama-nonadaptive-execution-authority.json")
        self.qa=load("d2-failure-memory-provenance-r82-qwen-interim-analysis-authority.json")
    def test_receipts(self):
        self.assertTrue(valid(self.lm));self.assertTrue(valid(self.la));self.assertTrue(valid(self.qa))
    def test_llama_is_frozen_before_qwen_open(self):
        self.assertTrue(self.lm["created_before_qwen_terminal_outcomes_opened"])
        self.assertFalse(self.la["qwen_terminal_outcomes_opened_when_authority_created"])
        self.assertEqual(self.la["bindings"]["llama_frozen_schedule_rows"],132)
        self.assertEqual(self.la["bindings"]["llama_frozen_schedule_sha256"],"4aff80e45e07d339dd26769f82d485c1b8920079641a8174711d4f8e0c58f179")
    def test_authorities_are_separated(self):
        self.assertEqual(self.la["authority"]["llama_execution"],True)
        self.assertEqual(self.la["authority"]["analysis"],False)
        self.assertEqual(self.qa["authority"]["analysis"],True)
        self.assertEqual(self.qa["authority"]["llama_execution"],False)
        self.assertEqual(self.qa["authority"]["qwen_execution"],False)
    def test_qwen_ledger_binding(self):
        want="58d0ece1be8911817bfd38c28619797c5c9bec3714c135ce9c00c85ce7cfb829"
        self.assertEqual(self.la["bindings"]["qwen_sealed_terminal_file_sha256"],want)
        self.assertEqual(self.qa["bindings"]["qwen_sealed_terminal_file_sha256"],want)
        self.assertEqual(self.qa["scope"]["primary_contrast"],"T_truthful-P_neutral")
        self.assertTrue(self.qa["scope"]["gatekept_correctness"].startswith("T_truthful-S_shuffled"))

if __name__=="__main__":unittest.main()
