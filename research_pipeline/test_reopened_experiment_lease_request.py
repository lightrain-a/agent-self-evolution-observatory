from __future__ import annotations
import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from .reopened_experiment_lease_request import *
from .reopened_pre_experiment_adapter import compile_reopened_pre_experiment
from .test_reopened_pre_experiment_adapter import ReopenedPreExperimentAdapterTest

class ReopenedExperimentLeaseRequestTest(unittest.TestCase):
 def fixture(self,root:Path,compiler_pass=True):
  h=ReopenedPreExperimentAdapterTest(methodName='test_compiler_pass_still_requires_experiment_lease'); c,b,r,a=h.fixture(root); fake={"status":"pass" if compiler_pass else "blocked","execution_authorized":compiler_pass,"passed_gates":8 if compiler_pass else 7,"gate_count":8,"blockers":[] if compiler_pass else ['x'],"research_execution_plan":{"plan_hash":"p"*64},"config_hash":"cfg"}
  with patch('research_pipeline.reopened_pre_experiment_adapter.compile_pre_experiment_card',return_value=fake): pe=compile_reopened_pre_experiment(contract=c,blueprint=b,blueprint_review=r,local_authorization=a,runtime_supplement=h.runtime(),data_root=root)
  return c,a,pe
 def test_pre_experiment_pass_required(self):
  with tempfile.TemporaryDirectory() as td:
   c,a,pe=self.fixture(Path(td),False)
   with self.assertRaisesRegex(RuntimeError,'compiler PASS'): build_experiment_lease_request(pre_experiment_receipt=pe,local_authorization=a)
 def test_request_binds_exact_plan_and_grants_no_authority(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);c,a,pe=self.fixture(root,True);r=build_experiment_lease_request(pre_experiment_receipt=pe,local_authorization=a);self.assertTrue(validate_experiment_lease_request(r));self.assertEqual(r['plan_hash'],'p'*64);self.assertFalse(r['execution_authorized']);self.assertFalse(r['experiment_authority_acquired']);self.assertTrue(r['single_writer_lease_required']);self.assertFalse(r['gpu_authority']);row=publish_experiment_lease_request(root,r);row2=publish_experiment_lease_request(root,r);self.assertEqual(len(row['events']),1);self.assertEqual(len(row2['events']),1);self.assertFalse((root/'experiment-authority').exists())
 def test_local_authority_lineage_mismatch_is_blocked(self):
  with tempfile.TemporaryDirectory() as td:
   c,a,pe=self.fixture(Path(td),True);bad=dict(a);bad['local_validation_authorization_sha256']='0'*64
   with self.assertRaisesRegex(RuntimeError,'valid local-validation'):build_experiment_lease_request(pre_experiment_receipt=pe,local_authorization=bad)
 def test_tamper_detected(self):
  with tempfile.TemporaryDirectory() as td:
   c,a,pe=self.fixture(Path(td),True);r=build_experiment_lease_request(pre_experiment_receipt=pe,local_authorization=a);bad=copy.deepcopy(r);bad['execution_authorized']=True;self.assertFalse(validate_experiment_lease_request(bad))
 def test_public_request_is_safe_and_not_active_lease(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);c,a,pe=self.fixture(root,True);r=build_experiment_lease_request(pre_experiment_receipt=pe,local_authorization=a);publish_experiment_lease_request(root,r);pub=public_experiment_lease_request(root,c['contract_id']);self.assertEqual(pub['status'],STATUS);self.assertFalse(pub['experiment_authority_acquired']);self.assertFalse(pub['execution_authorized']);self.assertEqual(pub['plan_hash'],'p'*64);self.assertFalse((root/'experiment-authority').exists())

if __name__=='__main__':unittest.main()
