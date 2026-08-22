from __future__ import annotations
import copy,json,tempfile,unittest
from pathlib import Path
from .reopened_local_f0_completion import adjudicate_evidence, NO_SIGNAL
from .reopened_p0_authorization import *
from .test_reopened_local_f0_completion import ReopenedLocalF0CompletionTest

class ReopenedP0AuthorizationTest(unittest.TestCase):
 def signal_fixture(self,root:Path):
  h=ReopenedLocalF0CompletionTest(methodName='test_signal_only_opens_p0_authorization_review_not_p0_or_claim_update');kw,run,c=h.complete(root,'SCREENING-SIGNAL');b,br=h.load_blueprint_receipts(root,run['contract_id']);a=adjudicate_evidence(completion=c,blueprint=b,blueprint_review=br,packet=h.packet());return b,br,a
 def budget(self):return {'max_units':64,'max_provider_calls':256,'max_gpu_hours':8.0}
 def test_signal_required_and_no_signal_cannot_enter_p0(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);h=ReopenedLocalF0CompletionTest(methodName='test_valid_no_signal_has_zero_negative_scientific_authority');kw,run,c=h.complete(root,'SCREENING-NO-SIGNAL');b,br=h.load_blueprint_receipts(root,run['contract_id']);a=adjudicate_evidence(completion=c,blueprint=b,blueprint_review=br,packet=h.packet());self.assertEqual(a['status'],NO_SIGNAL)
   with self.assertRaisesRegex(RuntimeError,'screening signal'):build_p0_authorization(adjudication=a,blueprint=b,blueprint_review=br,external_authority_ref='pi:p0',authorized_at='2027-04-08T12:00:00+00:00',p0_budget=self.budget())
 def test_human_authorization_opens_lifecycle_only_not_execution(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);b,br,a=self.signal_fixture(root);r=build_p0_authorization(adjudication=a,blueprint=b,blueprint_review=br,external_authority_ref='pi:private-p0-authority',authorized_at='2027-04-08T12:00:00+00:00',p0_budget=self.budget());self.assertTrue(validate_p0_authorization(r));self.assertEqual(r['status'],STATUS);self.assertTrue(r['p0_lifecycle_authorized']);self.assertTrue(r['confirmatory_p0_plan_required']);self.assertTrue(r['fresh_pre_experiment_compiler_required']);self.assertTrue(r['fresh_experiment_lease_required']);self.assertTrue(r['local_f0_lease_reuse_forbidden']);self.assertTrue(r['local_f0_run_reuse_forbidden']);self.assertFalse(r['p0_execution_authorized']);self.assertFalse(r['claim_update_authorized']);self.assertFalse(r['experiment_authority']);self.assertFalse(r['gpu_authority']);row=publish_p0_authorization(root,r);row2=publish_p0_authorization(root,r);self.assertEqual(len(row['events']),1);self.assertEqual(len(row2['events']),1);self.assertEqual(validate_p0_authority_ledger(row2),[]);self.assertFalse(any(json.loads(p.read_text()).get('status')=='active' for p in (root/'experiment-authority').glob('*.json')))
 def test_p0_budget_must_not_shrink_below_frozen_local_requested_units(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);b,br,a=self.signal_fixture(root)
   with self.assertRaisesRegex(RuntimeError,'must not be smaller'):build_p0_authorization(adjudication=a,blueprint=b,blueprint_review=br,external_authority_ref='pi:p0',authorized_at='2027-04-08T12:00:00+00:00',p0_budget={'max_units':10,'max_provider_calls':256,'max_gpu_hours':8})
 def test_public_summary_redacts_private_authority_and_tamper_is_detected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);b,br,a=self.signal_fixture(root);r=build_p0_authorization(adjudication=a,blueprint=b,blueprint_review=br,external_authority_ref='pi:private-p0-authority',authorized_at='2027-04-08T12:00:00+00:00',p0_budget=self.budget());publish_p0_authorization(root,r);pub=public_p0_authorization(root,a['contract_id']);text=json.dumps(pub);self.assertEqual(pub['status'],STATUS);self.assertNotIn('pi:private-p0-authority',text);self.assertTrue(pub['external_authority_ref_sha256']);self.assertFalse(pub['p0_execution_authorized']);bad=copy.deepcopy(r);bad['p0_execution_authorized']=True;self.assertFalse(validate_p0_authorization(bad))

if __name__=='__main__':unittest.main()
