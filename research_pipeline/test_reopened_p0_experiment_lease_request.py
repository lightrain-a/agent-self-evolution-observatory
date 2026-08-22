from __future__ import annotations
import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from .reopened_local_f0_run import validate_reopened_local_f0_run_start
from .reopened_p0_experiment_lease_request import *
from .reopened_p0_pre_experiment_adapter import compile_p0_pre_experiment
from .test_reopened_p0_pre_experiment_adapter import ReopenedP0PreExperimentAdapterTest

class ReopenedP0ExperimentLeaseRequestTest(unittest.TestCase):
 def fixture(self,root:Path,p0_pass=True):
  h=ReopenedP0PreExperimentAdapterTest(methodName='test_compiler_pass_still_requires_fresh_lease_and_run');auth,plan=h.fixture(root);fake={'status':'pass' if p0_pass else 'blocked','execution_authorized':p0_pass,'passed_gates':8 if p0_pass else 7,'gate_count':8,'blockers':[] if p0_pass else ['x'],'research_execution_plan':{'plan_hash':'8'*64},'expected_runtime':{'model_names':['Qwen-Test'],'competence_model_name':'Qwen-Test','policy_mode':'frozen-test'},'gates':[]}
  with patch('research_pipeline.reopened_p0_pre_experiment_adapter.compile_pre_experiment_card',return_value=fake):pre=compile_p0_pre_experiment(p0_plan=plan,p0_authorization=auth,runtime_supplement=h.runtime(),data_root=root)
  row=json.loads((root/'scientific-contract-run-starts'/f"{plan['contract_id']}.json").read_text());local=next(e['receipt'] for e in reversed(row['events']) if validate_reopened_local_f0_run_start(e.get('receipt') or {}));return auth,plan,pre,local
 def test_p0_pre_experiment_pass_required(self):
  with tempfile.TemporaryDirectory() as td:
   auth,plan,pre,local=self.fixture(Path(td),False)
   with self.assertRaisesRegex(RuntimeError,'P0 Pre-Experiment compiler PASS'):build_p0_lease_request(p0_pre_experiment=pre,p0_plan=plan,p0_authorization=auth,local_f0_run_start=local)
 def test_request_binds_fresh_p0_plan_and_historical_local_lineage(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);auth,plan,pre,local=self.fixture(root,True);r=build_p0_lease_request(p0_pre_experiment=pre,p0_plan=plan,p0_authorization=auth,local_f0_run_start=local);self.assertTrue(validate_p0_lease_request(r));self.assertEqual(r['p0_plan_hash'],'8'*64);self.assertEqual(r['local_f0_plan_hash'],'7'*64);self.assertNotEqual(r['p0_plan_hash'],r['local_f0_plan_hash']);self.assertEqual(r['local_f0_lease_request_sha256'],local['lease_request_sha256']);self.assertTrue(r['fresh_from_local_f0']);self.assertFalse(r['experiment_authority_acquired']);self.assertFalse(r['execution_authorized']);row=publish_p0_lease_request(root,r);row2=publish_p0_lease_request(root,r);self.assertEqual(len(row['events']),1);self.assertEqual(len(row2['events']),1);pub=public_p0_lease_request(root,plan['contract_id']);self.assertEqual(pub['status'],STATUS);self.assertFalse(pub['experiment_authority_acquired'])
 def test_reusing_local_plan_hash_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);auth,plan,pre,local=self.fixture(root,True);bad=copy.deepcopy(pre);bad['pre_experiment_card']['research_execution_plan']['plan_hash']=local['plan_hash'];bad['pre_experiment_card_sha256']=__import__('hashlib').sha256(json.dumps(bad['pre_experiment_card'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest();
   # Recompute adapter identity through module private digest-compatible fields by using a fresh compile mock.
   h=ReopenedP0PreExperimentAdapterTest(methodName='test_compiler_pass_still_requires_fresh_lease_and_run');
   fake={'status':'pass','execution_authorized':True,'passed_gates':8,'gate_count':8,'blockers':[],'research_execution_plan':{'plan_hash':local['plan_hash']}}
   with patch('research_pipeline.reopened_p0_pre_experiment_adapter.compile_pre_experiment_card',return_value=fake):same=compile_p0_pre_experiment(p0_plan=plan,p0_authorization=auth,runtime_supplement=h.runtime(),data_root=root)
   with self.assertRaisesRegex(RuntimeError,'must be fresh'):build_p0_lease_request(p0_pre_experiment=same,p0_plan=plan,p0_authorization=auth,local_f0_run_start=local)
 def test_contract_or_p0_lineage_mismatch_is_blocked(self):
  with tempfile.TemporaryDirectory() as td:
   auth,plan,pre,local=self.fixture(Path(td),True);bad=copy.deepcopy(plan);bad['p0_plan_sha256']='0'*64
   with self.assertRaisesRegex(RuntimeError,'valid P0 plan'):build_p0_lease_request(p0_pre_experiment=pre,p0_plan=bad,p0_authorization=auth,local_f0_run_start=local)
 def test_tamper_and_public_redaction(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);auth,plan,pre,local=self.fixture(root,True);r=build_p0_lease_request(p0_pre_experiment=pre,p0_plan=plan,p0_authorization=auth,local_f0_run_start=local);bad=copy.deepcopy(r);bad['p0_plan_hash']=bad['local_f0_plan_hash'];self.assertFalse(validate_p0_lease_request(bad));publish_p0_lease_request(root,r);pub=public_p0_lease_request(root,plan['contract_id']);text=json.dumps(pub);self.assertNotIn(local['lease_request_sha256'],text);self.assertNotIn(local['plan_hash'],text);self.assertTrue(pub['fresh_from_local_f0'])
if __name__=='__main__':unittest.main()
