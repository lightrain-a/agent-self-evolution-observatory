from __future__ import annotations
import copy,json,tempfile,unittest
from pathlib import Path
from .reopened_p0_authorization import build_p0_authorization,publish_p0_authorization
from .reopened_p0_plan import *
from .test_reopened_p0_authorization import ReopenedP0AuthorizationTest

class ReopenedP0PlanTest(unittest.TestCase):
 def fixture(self,root:Path):
  h=ReopenedP0AuthorizationTest(methodName='test_human_authorization_opens_lifecycle_only_not_execution');b,br,a=h.signal_fixture(root);auth=build_p0_authorization(adjudication=a,blueprint=b,blueprint_review=br,external_authority_ref='pi:p0-plan',authorized_at='2027-04-08T12:00:00+00:00',p0_budget=h.budget());publish_p0_authorization(root,auth);return auth,a
 def spec(self):return {'plan_id':'p0-confirm-001','confirmatory_prediction':'The preregistered intervention-control effect remains positive on fresh held-out confirmatory units.','unit_definition':'Fresh held-out task/context unit qualified before outcomes.','qualification_rule':'Freeze support/competence before outcomes; no local-F0 outcome reuse.','arms':['intervention','matched-control'],'truth_source':'frozen external environment/evaluator','primary_metric':'paired effect on held-out units','analysis_plan':'exact paired permutation test with preregistered effect-size reporting','evaluation_split':'fresh-heldout-confirmatory','exclusion_rules':'exclude only preregistered protocol-invalid units, never outcome-based exclusions','stop_rules':'stop for protocol/support failure or budget cap; do not reinterpret as method failure','same_information_baselines':['generic matched effect','context-stratified delta'],'seeds':[101,202,303],'alpha':0.05,'requested_units':48,'expected_provider_calls':192,'estimated_gpu_hours':6.0,'frozen_before_p0_outcomes':True,'local_f0_data_excluded_from_confirmatory_statistic':True,'outcome_driven_selection_forbidden':True,'frozen_at':'2027-04-08T13:00:00+00:00'}
 def test_plan_requires_p0_authority_and_is_frozen_without_execution(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);auth,a=self.fixture(root);r=build_p0_plan(p0_authorization=auth,adjudication=a,spec=self.spec());self.assertTrue(validate_p0_plan(r));self.assertEqual(r['status'],STATUS);self.assertTrue(r['confirmatory_plan_frozen']);self.assertFalse(r['execution_authorized']);self.assertFalse(r['p0_result_authorized']);self.assertTrue(r['local_f0_data_excluded_from_confirmatory_statistic']);row=publish_p0_plan(root,r);row2=publish_p0_plan(root,r);self.assertEqual(len(row['events']),1);self.assertEqual(len(row2['events']),1);self.assertFalse(any(json.loads(p.read_text()).get('status')=='active' for p in (root/'experiment-authority').glob('*.json')))
 def test_fresh_split_and_local_f0_exclusion_are_required(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);auth,a=self.fixture(root);s=self.spec();s['evaluation_split']='screening'
   with self.assertRaisesRegex(RuntimeError,'fresh and held out'):build_p0_plan(p0_authorization=auth,adjudication=a,spec=s)
   s=self.spec();s['local_f0_data_excluded_from_confirmatory_statistic']=False
   with self.assertRaisesRegex(RuntimeError,'preregistration safeguards'):build_p0_plan(p0_authorization=auth,adjudication=a,spec=s)
 def test_plan_budget_cannot_exceed_human_p0_cap(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);auth,a=self.fixture(root);s=self.spec();s['requested_units']=65
   with self.assertRaisesRegex(RuntimeError,'exceeds authorized'):build_p0_plan(p0_authorization=auth,adjudication=a,spec=s)
 def test_public_summary_and_tamper(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);auth,a=self.fixture(root);r=build_p0_plan(p0_authorization=auth,adjudication=a,spec=self.spec());publish_p0_plan(root,r);pub=public_p0_plan(root,a['contract_id']);self.assertEqual(pub['status'],STATUS);self.assertEqual(pub['requested_units'],48);self.assertFalse(pub['execution_authorized']);bad=copy.deepcopy(r);bad['plan_spec']['alpha']=0.1;self.assertFalse(validate_p0_plan(bad));self.assertNotIn('pi:p0-plan',json.dumps(pub))
if __name__=='__main__':unittest.main()
