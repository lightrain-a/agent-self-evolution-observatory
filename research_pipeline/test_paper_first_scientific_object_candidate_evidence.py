from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from .config import StorageSettings
from .paper_first_scientific_object_candidate_evidence import (
    build_scientific_object_candidate_evidence_ledger,
    candidate_extra_records_from_ledger,
    public_scientific_object_candidate_evidence_summary,
)
from .paper_first_scientific_object_ontology import audit_scientific_object_ontology


class ScientificObjectCandidateEvidenceTest(unittest.TestCase):
    NOW=datetime(2026,8,14,tzinfo=timezone.utc)

    def storage(self,root:Path)->StorageSettings:
        return StorageSettings(data_root=root,corpus_dir=root/'corpora',dataset_dir=root/'datasets',paper_dir=root/'papers',index_dir=root/'indexes',run_dir=root/'runs',cache_dir=root/'cache',lock_dir=root/'locks',site_artifact_dir=root/'site')

    def write_cache(self,root:Path,aid:str,title:str,abstract:str,*,fulltext:bool=True)->None:
        src=root/'paper-first-problem-discovery'/'primary-sources';src.mkdir(parents=True,exist_ok=True)
        primary=f'<meta name="citation_title" content="{title}"><blockquote class="abstract mathjax">Abstract: {abstract}</blockquote>'.encode()
        sha=hashlib.sha256(primary).hexdigest();(src/f'arxiv-{aid}-{sha[:12]}.html').write_bytes(primary)
        if fulltext:
            body=b'<html><body><section><h2>Results</h2><p>We find the self-evolving knowledge graph improves held-out retrieval success by 12.0 percent, while the static graph fails on 4/10 cases.</p></section></body></html>'
            fsha=hashlib.sha256(body).hexdigest();(src/f'arxiv-full-{aid}-{fsha[:12]}.html').write_bytes(body)

    def retrieval(self,*,status:str='SHADOW_OBJECT_RETRIEVAL_AUDIT_COMPLETE')->dict:
        return {'status':status,'results':{'knowledge_retrieval_state':{'rows':[{'ref':'arXiv:2607.12764','title':'EvoGraph-R1: Self-Evolving Knowledge Graph','publication_date':'2026-07-14','already_reviewed':False},{'ref':'arXiv:2608.01904','title':'CoEvoKG','publication_date':'2026-08-03','already_reviewed':True}]}}}

    def test_cached_primary_and_fulltext_become_zero_authority_candidate_evidence(self)->None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);storage=self.storage(root);self.write_cache(root,'2607.12764','EvoGraph-R1: Self-Evolving Knowledge Graph','A self-evolving agent updates a knowledge graph for retrieval.')
            ledger=build_scientific_object_candidate_evidence_ledger(storage=storage,retrieval_state=self.retrieval(),now=self.NOW)
        self.assertEqual(ledger['status'],'SHADOW_CANDIDATE_EVIDENCE_COMPLETE')
        self.assertEqual(ledger['summary']['primary_verified'],1)
        self.assertEqual(ledger['summary']['fulltext_verified'],1)
        self.assertEqual(ledger['summary']['empirical_supported'],1)
        self.assertEqual(ledger['summary']['measured_failure_supported'],1)
        record=ledger['records'][0]
        self.assertEqual(record['candidate_key'],'knowledge_retrieval_state')
        self.assertTrue(record['direct_object_match'])
        self.assertFalse(record['source_exposure_effect'])
        self.assertFalse(record['live_query_effect'])
        self.assertFalse(record['scientific_authority'])
        self.assertEqual(len(record['source_sha256']),64)
        self.assertEqual(len(record['fulltext_sha256']),64)

    def test_missing_cache_is_partial_not_negative(self)->None:
        with tempfile.TemporaryDirectory() as td:
            ledger=build_scientific_object_candidate_evidence_ledger(storage=self.storage(Path(td)),retrieval_state=self.retrieval(),now=self.NOW)
        self.assertEqual(ledger['status'],'SHADOW_CANDIDATE_EVIDENCE_PARTIAL')
        self.assertEqual(ledger['summary']['primary_verified'],0)
        self.assertEqual(ledger['summary']['pending_cache'],1)
        self.assertEqual(ledger['errors'][0]['error'],'primary-cache-missing')
        self.assertFalse(ledger['scientific_authority'])

    def test_incomplete_retrieval_blocks_candidate_verification(self)->None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);self.write_cache(root,'2607.12764','EvoGraph-R1: Self-Evolving Knowledge Graph','A self-evolving agent updates a knowledge graph for retrieval.')
            ledger=build_scientific_object_candidate_evidence_ledger(storage=self.storage(root),retrieval_state=self.retrieval(status='SHADOW_OBJECT_RETRIEVAL_AUDIT_INCOMPLETE'),now=self.NOW)
        self.assertEqual(ledger['status'],'SHADOW_CANDIDATE_EVIDENCE_BLOCKED_RETRIEVAL_INCOMPLETE')
        self.assertEqual(ledger['summary']['primary_verified'],0)

    def test_public_summary_exposes_counts_without_private_records(self)->None:
        ledger={'status':'SHADOW_CANDIDATE_EVIDENCE_COMPLETE','summary':{'primary_verified':2,'fulltext_verified':2,'empirical_supported':2,'measured_failure_supported':2,'direct_object_verified':2,'pending_cache':0},'results':{'knowledge_retrieval_state':{'discovered_new_support_refs':2,'primary_verified':2,'fulltext_verified':2,'empirical_supported':2,'measured_failure_supported':2,'direct_object_verified':2,'pending_cache':0,'errors':[]}},'records':[{'ref':'arXiv:secret','abstract':'secret'}]}
        public=public_scientific_object_candidate_evidence_summary(ledger)
        self.assertEqual(public['summary']['primary_verified'],2)
        self.assertEqual(public['summary']['activation_authorized'],0)
        self.assertFalse(public['scientific_authority'])
        encoded=json.dumps(public)
        self.assertNotIn('arXiv:secret',encoded)
        self.assertNotIn('secret',encoded)
        self.assertNotIn('records',public)
        self.assertFalse(public['policy']['source_exposure_effect'])
        self.assertFalse(public['policy']['live_query_effect'])

    def test_candidate_extra_records_supplement_only_target_object(self)->None:
        base=[{'ref':'arXiv:base','title':'Co-evolving knowledge graph','abstract':'A co-evolving knowledge graph is updated by a self-evolving agent.','primary_source_verified':True,'lane_keys':['memory_continual'],'empirical_facts':[{'text':'result'}],'typed_evidence':{'operational_assumptions':[],'measured_failures':[{'text':'failure'}],'boundary_observations':[]}}]
        extra={'ref':'arXiv:extra','candidate_key':'knowledge_retrieval_state','title':'Self-evolving knowledge graph','abstract':'A self-evolving knowledge graph updates retrieval state.','primary_source_verified':True,'scientific_authority':False,'lane_keys':[],'empirical_facts':[{'text':'result'}],'typed_evidence':{'operational_assumptions':[],'measured_failures':[{'text':'failure'}],'boundary_observations':[]}}
        state=audit_scientific_object_ontology(base,candidate_extra_records={'knowledge_retrieval_state':[extra]})
        self.assertEqual(state['candidate_extra_primary_counts']['knowledge_retrieval_state'],1)
        self.assertEqual(state['candidates']['knowledge_retrieval_state']['observed']['reviewed_primary_refs'],2)
        self.assertEqual(state['candidates']['evaluator_reward_verifier']['observed']['reviewed_primary_refs'],0)
        self.assertEqual(state['summary']['shadow_candidate_primary_records'],1)
        self.assertEqual(state['summary']['activation_authorized'],0)


if __name__=='__main__':
    unittest.main()
