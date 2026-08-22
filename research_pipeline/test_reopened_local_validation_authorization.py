from __future__ import annotations
import copy,json,tempfile,unittest
from pathlib import Path
from .reopened_local_validation_authorization import *
from .reopened_scientific_experiment_blueprint import build_reopen_experiment_blueprint,build_reopen_blueprint_review,publish_reopen_blueprint_receipt
from .test_reopened_scientific_experiment_blueprint import ReopenedScientificExperimentBlueprintTest

class ReopenedLocalValidationAuthorizationTest(unittest.TestCase):
 def fixture(self,root:Path):
  h=ReopenedScientificExperimentBlueprintTest(methodName='test_review_pass_only_grants_authorization_review_eligibility'); c,d,m=h.fixture(root); b=build_reopen_experiment_blueprint(contract=c,method_design=d,method_review=m,blueprint_spec=h.spec()); publish_reopen_blueprint_receipt(root,b); r=build_reopen_blueprint_review(blueprint=b,review_packet=h.review()); publish_reopen_blueprint_receipt(root,r); return c,b,r
 def budget(self): return {"max_units":12,"max_provider_calls":60,"max_gpu_hours":2.0}
 def test_blueprint_review_pass_required(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); c,b,r=self.fixture(root); bad=dict(r); bad['status']='REOPEN_BLUEPRINT_REVIEW_BLOCKED'
   with self.assertRaisesRegex(RuntimeError,'blueprint review PASS'): build_local_validation_authorization(blueprint=b,blueprint_review=bad,external_authority_ref='human:auth',authorized_at='2027-04-05T12:00:00+00:00',authorized_budget=self.budget())
 def test_authorization_binds_budget_but_does_not_authorize_execution(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); c,b,r=self.fixture(root); a=build_local_validation_authorization(blueprint=b,blueprint_review=r,external_authority_ref='human:private-local-f0',authorized_at='2027-04-05T12:00:00+00:00',authorized_budget=self.budget()); self.assertTrue(validate_local_validation_authorization(a)); self.assertEqual(a['status'],STATUS); self.assertTrue(a['local_validation_authorized']); self.assertTrue(a['pre_experiment_compiler_required']); self.assertFalse(a['execution_authorized']); self.assertFalse(a['experiment_authority']); self.assertFalse(a['gpu_authority']); row=publish_local_validation_authorization(root,a); row2=publish_local_validation_authorization(root,a); self.assertEqual(len(row['events']),1); self.assertEqual(len(row2['events']),1); self.assertEqual(validate_local_validation_authority_ledger(row2),[]); self.assertFalse((root/'experiment-authority').exists())
 def test_authorized_budget_cannot_exceed_blueprint(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); c,b,r=self.fixture(root)
   for budget,regex in [({"max_units":21,"max_provider_calls":60,"max_gpu_hours":2},'max_units'),({"max_units":12,"max_provider_calls":81,"max_gpu_hours":2},'max_provider_calls'),({"max_units":12,"max_provider_calls":60,"max_gpu_hours":4},'max_gpu_hours')]:
    with self.assertRaisesRegex(RuntimeError,regex): build_local_validation_authorization(blueprint=b,blueprint_review=r,external_authority_ref='human:x',authorized_at='2027-04-05T12:00:00+00:00',authorized_budget=budget)
 def test_external_authority_is_required_and_public_projection_redacts_it(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); c,b,r=self.fixture(root)
   with self.assertRaisesRegex(RuntimeError,'authority reference'): build_local_validation_authorization(blueprint=b,blueprint_review=r,external_authority_ref='',authorized_at='2027-04-05T12:00:00+00:00',authorized_budget=self.budget())
   a=build_local_validation_authorization(blueprint=b,blueprint_review=r,external_authority_ref='human:private-local-f0',authorized_at='2027-04-05T12:00:00+00:00',authorized_budget=self.budget()); publish_local_validation_authorization(root,a); pub=public_local_validation_authorization(root,c['contract_id']); text=json.dumps(pub); self.assertEqual(pub['status'],STATUS); self.assertTrue(pub['external_authority_ref_sha256']); self.assertNotIn('human:private-local-f0',text); self.assertNotIn('external_authority_ref"',text); self.assertFalse(pub['execution_authorized'])
 def test_tamper_or_ledger_authority_leak_is_detected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); c,b,r=self.fixture(root); a=build_local_validation_authorization(blueprint=b,blueprint_review=r,external_authority_ref='human:x',authorized_at='2027-04-05T12:00:00+00:00',authorized_budget=self.budget()); bad=copy.deepcopy(a); bad['execution_authorized']=True; self.assertFalse(validate_local_validation_authorization(bad)); row=publish_local_validation_authorization(root,a); row['authority']['local_validation']=True; self.assertIn('local-validation-authority-ledger-must-not-own-execution-authority',validate_local_validation_authority_ledger(row))
 def test_local_authorization_does_not_create_compiler_card_or_lease(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); c,b,r=self.fixture(root); a=build_local_validation_authorization(blueprint=b,blueprint_review=r,external_authority_ref='human:x',authorized_at='2027-04-05T12:00:00+00:00',authorized_budget=self.budget()); publish_local_validation_authorization(root,a); self.assertFalse((root/'pre-experiment').exists()); self.assertFalse((root/'experiment-authority').exists())

if __name__=='__main__': unittest.main()
