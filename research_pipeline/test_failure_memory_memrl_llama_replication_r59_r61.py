from __future__ import annotations
import hashlib, json, pathlib, unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]

def load(rel): return json.loads((ROOT/rel).read_text())
def sha(rel): return hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
def digest(v): return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def valid(v):
    x=dict(v); got=x.pop('receipt_sha256'); return got==digest(x)

class LlamaReplicationR59R61Test(unittest.TestCase):
    def setUp(self):
        self.ident=load('generated/d2-failure-memory-provenance-r59-llama-model-identity.json')
        self.man=load('generated/d2-failure-memory-provenance-r59-llama-executor-replication-manifest.json')
        self.prog=load('generated/d2-failure-memory-provenance-r59-r61-llama-executor-replication-contract.json')
        self.pa=load('generated/d2-failure-memory-provenance-r59-llama-parser-authority.json')
        self.u=load('generated/d2-failure-memory-provenance-r60-llama-utilization-authority.json')
        self.c=load('generated/d2-failure-memory-provenance-r61-llama-ab-replication-contract.json')
        self.a=load('generated/d2-failure-memory-provenance-r61-llama-ab-conditional-authority.json')
    def test_receipts_sealed(self):
        for x in [self.ident,self.man,self.prog,self.pa,self.u,self.c,self.a]: self.assertTrue(valid(x))
    def test_model_identity_canonical(self):
        self.assertEqual(self.ident['manifest_sha256'],'8071d53a4509c0404328b791800ba79657556490b276b8383e1e8b2f0f63e104')
        self.assertEqual(self.ident['file_count'],10); self.assertEqual(self.ident['bytes'],16069722669)
        self.assertEqual(digest(self.ident['files']),self.ident['manifest_sha256'])
    def test_only_executor_backbone_changes(self):
        e=self.man['execution_manifest']; self.assertEqual(e['models']['llm']['family'],'Meta-Llama-3.1-8B-Instruct')
        self.assertEqual(e['external_runtime_adapter']['llm_model_id'],'B1-Meta-Llama-3.1-8B-Instruct-r59')
        self.assertTrue(self.man['replication_boundary']['same_R54_primary_and_utilization_ids'])
        self.assertTrue(self.man['replication_boundary']['same_frozen_retrieval_content_and_order'])
        self.assertEqual(self.man['replication_boundary']['only_scientific_factor_changed'],'executor backbone')
    def test_probe_is_source_side_and_exact(self):
        self.assertEqual(self.prog['parser_gate']['probe_ids'],['103','256','54'])
        self.assertEqual(self.pa['probe_ids'],['103','256','54']); self.assertEqual(self.pa['attempts'],1)
        self.assertFalse(self.pa['validation_units_opened']); self.assertFalse(self.pa['primary_units_opened'])
    def test_fresh_units_identical_to_qwen(self):
        old=load('generated/d2-failure-memory-provenance-r56-fresh-ab-confirmatory-contract.json')
        self.assertEqual(self.c['units']['representative_ids'],old['units']['representative_ids'])
        self.assertEqual(self.c['analysis'],old['analysis']); self.assertEqual(self.c['renderer'],old['renderer'])
        self.assertFalse(self.c['replication_analysis']['pool_with_Qwen'])
    def test_runner_bindings_current(self):
        self.assertEqual(self.pa['bindings']['parser_runner_sha256'],sha('research_pipeline/failure_memory_memrl_llama_parser_qualification_r59.py'))
        self.assertEqual(self.u['bindings']['runner_sha256'],sha('research_pipeline/failure_memory_memrl_llama_utilization_r60.py'))
        self.assertEqual(self.a['bindings']['runner_sha256'],sha('research_pipeline/failure_memory_memrl_llama_ab_r61.py'))
        self.assertEqual(self.man['execution_manifest']['external_runtime_adapter']['loopback_server_sha256'],sha('research_pipeline/failure_memory_memrl_local_openai_server_r59_llama.py'))
    def test_conditional_gates(self):
        self.assertEqual(self.u['conditional_on'],'R59 parser receipt PASS from exact frozen runner/probe IDs')
        self.assertEqual(self.a['conditional_on'],'R60 Llama utilization PASS from exact frozen 40-arm schedule')
        self.assertTrue(self.a['authority']['A_B_execution_conditionally_after_R60_PASS'])
        self.assertFalse(self.a['authority']['C_D_execution'])

if __name__=='__main__': unittest.main()
