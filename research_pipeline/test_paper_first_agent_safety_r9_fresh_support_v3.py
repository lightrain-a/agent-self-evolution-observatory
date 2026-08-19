from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .paper_first_agent_safety_r9_fresh_support_v3 import (
    EXPECTED_DEVELOPMENT_IDS,
    EXPECTED_HELDOUT_IDS,
    EXPECTED_QUALIFICATION_IDS,
    EXPECTED_RULES_SHA256,
    REALIZATION_ID,
    assert_probe_allowed,
    compose_system_context,
    load_fresh_contract,
)
from .paper_first_agent_safety_r9_harness import CANDIDATE_ID, CONTRACT_SHA256


class FreshSupportTest(unittest.TestCase):
    def fixture(self, root: Path) -> Path:
        states=[]
        for i in range(4):
            p=root/f'w{i}.txt'; p.write_text(f'w{i}\n',encoding='utf-8')
            import hashlib
            states.append({'state_id':f's{i}','site_stratum':'x','workflow_path':str(p),'workflow_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
        d={
            'schema_version':'1.0','status':'PREREGISTERED_FRESH_SUPPORT_REALIZATION','realization_id':REALIZATION_ID,
            'candidate_id':CANDIDATE_ID,'contract_sha256':CONTRACT_SHA256,'scientific_authority':False,
            'safety_substrate':{'upstream_commit':'bf17e2b3deb989e348b3a98080e33a7047e90ac3','rules_sha256':EXPECTED_RULES_SHA256,'content_editing_forbidden':True,'applies_identically_to_all_states_all_current_and_future_steps':True},
            'browser_runtime_adapter':{'type':'PLAYWRIGHT_EXACT_EXTERNAL_REQUEST_ABORT_SET','urls':['https://twitter.com/compose/twitter-logo.png','https://picsum.photos/48','https://picsum.photos/48?random=1','https://kit.fontawesome.com/a076d05399.js'],'pinned_twitter_html_sha256':'63cfe828edac802957401a353de3bdcf92518d565c4ec229cb6fcfe87407a45d','pinned_hbb_task_py_sha256':'8796d13e900d01e0fe6c60d446b534b51397711f213e57030f094a9f8358a65a','html_modified':False,'task_config_modified':False,'local_dom_modified':False,'probe_specific':False},
            'state_policy':{'state_identities':states,'post_outcome_state_replacement_forbidden':True},
            'probe_panels':{'development_headroom_ids':EXPECTED_DEVELOPMENT_IDS,'fresh_qualification_ids':EXPECTED_QUALIFICATION_IDS,'sealed_heldout_future_ids':EXPECTED_HELDOUT_IDS},
        }
        p=root/'contract.json'; p.write_text(json.dumps(d),encoding='utf-8'); return p

    def test_contract_and_panels(self):
        with tempfile.TemporaryDirectory() as td:
            c=load_fresh_contract(self.fixture(Path(td)))
            self.assertEqual(c['development_ids'],[0,9,36]); self.assertEqual(c['qualification_ids'],[2,10,38])
            assert_probe_allowed(probe=0,mode='development',contract=c)
            assert_probe_allowed(probe=38,mode='qualification',contract=c)
            with self.assertRaises(ValueError): assert_probe_allowed(probe=34,mode='qualification',contract=c)
            with self.assertRaises(ValueError): assert_probe_allowed(probe=16,mode='development',contract=c)

    def test_system_context_composition_is_mechanical(self):
        self.assertEqual(compose_system_context(rules_text='RULES\n',original_system='BASE'),'RULES\n\nBASE')
        with self.assertRaises(ValueError): compose_system_context(rules_text='RULES',original_system='BASE')

    def test_browser_adapter_guard_required(self):
        with tempfile.TemporaryDirectory() as td:
            p=self.fixture(Path(td)); d=json.loads(p.read_text()); d['browser_runtime_adapter']['urls'][0]='https://example.invalid/x.png'; p.write_text(json.dumps(d))
            with self.assertRaisesRegex(ValueError,'browser runtime adapter drift'): load_fresh_contract(p)

    def test_state_replacement_guard_required(self):
        with tempfile.TemporaryDirectory() as td:
            p=self.fixture(Path(td)); d=json.loads(p.read_text()); d['state_policy']['post_outcome_state_replacement_forbidden']=False; p.write_text(json.dumps(d))
            with self.assertRaisesRegex(ValueError,'state policy drift'): load_fresh_contract(p)


if __name__=='__main__': unittest.main()
