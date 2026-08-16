from __future__ import annotations
import unittest
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

if __name__=='__main__':unittest.main()
