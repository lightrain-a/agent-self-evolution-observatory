from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .paper_first_agent_safety_r9_qualification import (
    ListenerState,
    load_contract,
    serialize_messages,
)
from .paper_first_agent_safety_r9_harness import (
    CANDIDATE_ID,
    CONTRACT_SHA256,
    R9_HELDOUT_BEHAVIOR_IDS,
    R9_QUALIFICATION_BEHAVIOR_IDS,
)


class Msg:
    def __init__(self, t, c): self.type=t; self.content=c


class R9QualificationRunnerTest(unittest.TestCase):
    def test_listener_mirrors_browserart_twitter_and_email_formatters(self):
        s=ListenerState(); s.reset('x')
        s.record('/saveTweet',{'tweetText':'a'}); s.record('/saveTweet',{'tweetText':'ab'})
        self.assertEqual(s.output('twitter'),'a\nab\n')
        s.reset('y'); first=s.record('/saveEmail',{'to':'x','body':'one'})
        s.record('/saveEmail',{'id':first['id'],'to':'x','body':'two'})
        self.assertEqual(json.loads(s.output('email'))['body'],'two')

    def test_message_serialization_preserves_roles_and_hashes_without_network(self):
        payload,digest=serialize_messages([Msg('system','s'),Msg('human','u'),Msg('ai','a')])
        self.assertEqual([x['role'] for x in payload],['system','user','assistant'])
        self.assertEqual(len(digest),64)

    def test_canonical_contract_refuses_probe_drift(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); states=[]
            for i in range(4):
                p=root/f's{i}.txt'; p.write_text(f'state{i}')
                import hashlib
                states.append({'state_id':f's{i}','workflow_path':str(p),'workflow_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
            cfg={
                'candidate_id':CANDIDATE_ID,'contract_sha256':CONTRACT_SHA256,
                'state_construction':{'states':states},
                'safety_probe_split':{'qualification_ids':[int(x) for x in R9_QUALIFICATION_BEHAVIOR_IDS], 'heldout_ids':[int(x) for x in R9_HELDOUT_BEHAVIOR_IDS], 'disjoint':True},
                'budget':{'states':4,'qualification_probes_per_state':3,'qualification_episodes':12,'total_model_evaluations_upper_bound':240,'contract_max_model_calls':256,'agent_model_calls_cap_per_episode':4},
                'agent':{'backbone':'Qwen/Qwen3-8B'},'evaluator':{'hf_model':'cais/HarmBench-Llama-2-13b-cls'}
            }
            path=root/'c.json'; path.write_text(json.dumps(cfg)); self.assertEqual(len(load_contract(path)['states']),4)
            cfg['safety_probe_split']['qualification_ids'][0]=34; path.write_text(json.dumps(cfg))
            with self.assertRaisesRegex(ValueError,'probe split drift'): load_contract(path)


if __name__=='__main__': unittest.main()
