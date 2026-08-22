from __future__ import annotations
import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from .reopened_p0_authorization import build_p0_authorization,publish_p0_authorization
from .reopened_p0_plan import build_p0_plan,publish_p0_plan
from .reopened_p0_pre_experiment_adapter import *
from .test_reopened_p0_plan import ReopenedP0PlanTest
from .test_reopened_pre_experiment_adapter import ReopenedPreExperimentAdapterTest

class ReopenedP0PreExperimentAdapterTest(unittest.TestCase):
 def fixture(self,root:Path):
  h=ReopenedP0PlanTest(methodName='test_plan_requires_p0_authority_and_is_frozen_without_execution');auth,a=h.fixture(root);plan=build_p0_plan(p0_authorization=auth,adjudication=a,spec=h.spec());publish_p0_plan(root,plan);return auth,plan
 def runtime(self):
  r=ReopenedPreExperimentAdapterTest(methodName='test_adapter_budget_is_derived_from_human_authorization').runtime();r=copy.deepcopy(r);r['scope']['confirmatory_split_id']='fresh-heldout-confirmatory';r['scope']['uses_local_f0_data_in_confirmatory_statistic']=False;r['scope']['worst_case_environment_episodes']=96;r['scope']['expected_environment_episodes']=96;r['pre_experiment']['outcomes']['allowed']=['METHOD-PASS','METHOD-FAIL','INCONCLUSIVE','BASELINE-FLOOR','BASELINE-CEILING','RUNTIME-ERROR','IMPLEMENTATION-ERROR','BUDGET-STOP'];return r
 def test_fresh_confirmatory_split_and_local_f0_exclusion_required(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);auth,plan=self.fixture(root);r=self.runtime();r['scope']['confirmatory_split_id']='screening'
   with self.assertRaisesRegex(RuntimeError,'exactly match'):build_p0_config(p0_plan=plan,p0_authorization=auth,runtime_supplement=r)
   r=self.runtime();r['scope']['uses_local_f0_data_in_confirmatory_statistic']=True
   with self.assertRaisesRegex(RuntimeError,'exclude local-F0'):build_p0_config(p0_plan=plan,p0_authorization=auth,runtime_supplement=r)
 def test_config_is_p0_and_uses_fresh_plan_lineage(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);auth,plan=self.fixture(root);cfg=build_p0_config(p0_plan=plan,p0_authorization=auth,runtime_supplement=self.runtime());self.assertEqual(cfg['phase'],'P0');self.assertEqual(cfg['scope']['confirmatory_split_id'],'fresh-heldout-confirmatory');self.assertTrue(cfg['reopen_p0_lineage']['local_f0_data_excluded']);self.assertTrue(cfg['reopen_p0_lineage']['local_f0_pre_experiment_reuse_forbidden']);self.assertEqual(cfg['resource_cap']['episodes'],96)
 def test_real_native_compiler_block_is_preserved(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);auth,plan=self.fixture(root);out=compile_p0_pre_experiment(p0_plan=plan,p0_authorization=auth,runtime_supplement=self.runtime(),data_root=root);self.assertTrue(validate_p0_pre_experiment(out));self.assertIn(out['status'],{PASS,BLOCK});self.assertFalse(out['effective_execution_authorized']);self.assertFalse(any(json.loads(p.read_text()).get('status')=='active' for p in (root/'experiment-authority').glob('*.json')))
 def test_compiler_pass_still_requires_fresh_lease_and_run(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);auth,plan=self.fixture(root);fake={'status':'pass','execution_authorized':True,'passed_gates':8,'gate_count':8,'blockers':[],'research_execution_plan':{'plan_hash':'8'*64},'config_hash':'p0'}
   with patch('research_pipeline.reopened_p0_pre_experiment_adapter.compile_pre_experiment_card',return_value=fake):out=compile_p0_pre_experiment(p0_plan=plan,p0_authorization=auth,runtime_supplement=self.runtime(),data_root=root)
   self.assertEqual(out['status'],PASS);self.assertTrue(out['compiler_execution_ready']);self.assertFalse(out['effective_execution_authorized']);self.assertTrue(out['fresh_experiment_lease_required']);self.assertTrue(out['fresh_run_lineage_required']);self.assertTrue(out['local_f0_card_reuse_forbidden']);row=publish_p0_pre_experiment(root,out);self.assertEqual(len(row['events']),1);pub=public_p0_pre_experiment(root,plan['contract_id']);self.assertEqual(pub['status'],PASS);self.assertFalse(pub['effective_execution_authorized']);self.assertFalse(any(json.loads(p.read_text()).get('status')=='active' for p in (root/'experiment-authority').glob('*.json')))
 def test_tamper_and_public_redaction(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);auth,plan=self.fixture(root);fake={'status':'blocked','execution_authorized':False,'passed_gates':7,'gate_count':8,'blockers':['private-runtime:/tmp/x'],'research_execution_plan':{'plan_hash':'8'*64}}
   with patch('research_pipeline.reopened_p0_pre_experiment_adapter.compile_pre_experiment_card',return_value=fake):out=compile_p0_pre_experiment(p0_plan=plan,p0_authorization=auth,runtime_supplement=self.runtime(),data_root=root)
   publish_p0_pre_experiment(root,out);pub=public_p0_pre_experiment(root,plan['contract_id']);self.assertNotIn('private-runtime',json.dumps(pub));bad=copy.deepcopy(out);bad['effective_execution_authorized']=True;self.assertFalse(validate_p0_pre_experiment(bad))
if __name__=='__main__':unittest.main()
