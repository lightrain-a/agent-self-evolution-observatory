from __future__ import annotations
import json
import tempfile
import unittest
from unittest import mock
from pathlib import Path
from . import p06_docatlas_evidence_runtime as p06

class P06DocAtlasRuntimeTest(unittest.TestCase):
    def test_bm25_prefers_matching_page(self):
        pages=['apple pear','unrelated appendix','cobalt target fact']
        self.assertEqual(p06.bm25('cobalt target',pages)[0],3)

    def test_policy_prompts_share_raw_observation(self):
        pages=['alpha evidence','beta evidence','gamma appendix','delta']
        ids=[1,2,3];hashes=[];prompts=[]
        for policy in p06.POLICIES:
            text,raw_hash=p06.prompt('question',pages,ids,policy,1);hashes.append(raw_hash);prompts.append(text)
        self.assertEqual(len(set(hashes)),1)
        self.assertEqual(len(set(prompts)),len(p06.POLICIES))
        self.assertTrue(all('not answerable' not in text.lower() for text in prompts))

    def test_parser_and_exact_pair_test(self):
        self.assertEqual(p06.parse('{"action":"ANSWER","answer":"Cobalt"}')['action'],'ANSWER')
        self.assertEqual(p06.parse('ABSTAIN')['action'],'ABSTAIN')
        self.assertFalse(p06.parse('nonsense')['valid'])
        p,b,c=p06.mcnemar([0,0,0,1],[1,1,1,1])
        self.assertEqual((b,c),(3,0));self.assertGreater(p,0);self.assertLessEqual(p,1)

    def test_answer_normalization_is_deterministic(self):
        self.assertTrue(p06.exact('New-York','new york'))
        self.assertFalse(p06.exact('42','43'))

    def test_official_document_path_does_not_double_suffix_pdf(self):
        doc='example.pdf'
        self.assertEqual(p06.pdf_path(Path('/tmp/pdfs'),doc),Path('/tmp/pdfs/example.pdf'))
        self.assertTrue(p06.pdf_url(doc).endswith('/data/documents/example.pdf'))
        self.assertNotIn('.pdf.pdf',p06.pdf_url(doc))

    def test_top3_and_top6_share_fixed_raw_context_budget(self):
        self.assertEqual(p06.raw_page_chars([1,2,3]),3600)
        self.assertEqual(p06.raw_page_chars([1,2,3])*3,p06.RAW_CONTEXT_CHARS)
        self.assertEqual(p06.raw_page_chars([1,2,3,4,5,6]),1800)
        self.assertEqual(p06.raw_page_chars([1,2,3,4,5,6])*6,p06.RAW_CONTEXT_CHARS)

    def test_generation_fails_closed_before_silent_truncation(self):
        class Shape:
            shape=(1,p06.MAX_INPUT_TOKENS+1)
        class FakeTokenizer:
            def apply_chat_template(self,*args,**kwargs):
                return 'rendered'
            def __call__(self,*args,**kwargs):
                return {'input_ids':Shape()}
        with self.assertRaisesRegex(RuntimeError,'input-token-budget-exceeded'):
            p06.gen(None,FakeTokenizer(),None,['oversized'])

    def test_four_shard_aggregate_enforces_exact_ranges_and_global_budget(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            plan={'units':[{'unit_id':f'U{i:03d}'} for i in range(128)]}
            plan_path=root/'plan.json';plan_path.write_text(json.dumps(plan),encoding='utf-8')
            plan_sha=p06.sha(plan_path);runs=[]
            with mock.patch.object(p06,'PLAN_SHA',plan_sha):
                for shard,start in enumerate((0,32,64,96)):
                    raw=root/f'shard-{shard}.jsonl';rows=[]
                    for unit in plan['units'][start:start+32]:
                        rows.append({'unit_id':unit['unit_id'],'policy':'negative_evidence_baseline'})
                    raw.write_text(''.join(json.dumps(r)+'\n' for r in rows),encoding='utf-8')
                    run=root/f'shard-{shard}.json'
                    payload={'candidate_id':p06.CANDIDATE_ID,'contract_sha256':p06.CONTRACT_SHA,'plan_sha256':plan_sha,'unit_start_index':start,'unit_stop_index':start+32,'unit_ids':[u['unit_id'] for u in plan['units'][start:start+32]],'cost':{'batch_calls':64,'generation_gpu_seconds':100.0,'gpu_allocation_seconds':800.0,'wall_seconds':780.0,'within_budget':True},'raw_rows_path':str(raw)}
                    run.write_text(json.dumps(payload),encoding='utf-8');runs.append(run)
                out=root/'aggregate.json';result=p06.aggregate_shards(plan_path,runs,out)
            self.assertTrue(result['planned_ranges_exact'])
            self.assertTrue(result['cost']['within_budget'])
            self.assertEqual(result['cost']['completed_units'],128)
            self.assertEqual(result['cost']['batch_calls'],256)
            self.assertEqual(result['cost']['gpu_allocation_seconds'],3200.0)

if __name__=='__main__':unittest.main()
