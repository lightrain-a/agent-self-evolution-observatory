from __future__ import annotations
import copy,json,tempfile,unittest
from pathlib import Path
from .reopened_scientific_experiment_blueprint import *
from .reopened_scientific_method_design import build_reopen_method_design,build_reopen_method_review,publish_reopen_method_receipt
from .test_reopened_scientific_method_design import ReopenedScientificMethodDesignTest

class ReopenedScientificExperimentBlueprintTest(unittest.TestCase):
 def fixture(self,root:Path):
  h=ReopenedScientificMethodDesignTest(methodName='test_independent_review_pass_only_unlocks_blueprint_design_eligibility'); contract,gate=h.fixture(root); design=build_reopen_method_design(contract=contract,problem_gate_receipt=gate,method_spec=h.spec()); publish_reopen_method_receipt(root,design); review=build_reopen_method_review(method_design=design,review_packet=h.review()); publish_reopen_method_receipt(root,review); return contract,design,review
 def spec(self):
  return {"experiment_id":"reopen-f0-001","registered_prediction":"Intervention-control delta is positive on held-out qualified units.","unit_definition":"One frozen task/context instance with matched intervention and control execution.","qualification_rule":"Qualify before outcomes using frozen support and replay requirements.","arms":["intervention","matched-control"],"truth_source":"environment success plus frozen external evaluator","metrics":["paired effect","coverage"],"same_information_baselines":["generic matched effect","context-stratified delta"],"sample_plan":{"requested_units":20,"minimum_qualified_units":12,"replicates_per_arm":2},"statistical_plan":{"estimator":"paired mean delta","test":"exact paired permutation","alpha":0.05},"budget":{"max_provider_calls":80,"max_gpu_hours":3.0},"go_stop_rules":["GO if preregistered effect and alpha gates pass.","STOP local realization if matched simple baseline is equivalent or effect gate fails."],"compute_graph":"qualification -> paired arms -> frozen evaluator -> analysis","observability_recovery":"append raw traces and deterministic replay receipts; runtime failure is typed separately","outcome_semantics":"screening signal only; cannot emit method fail from support/runtime failure","provider_plan":"bounded provider calls under frozen prompts; no post-outcome selection","gpu_plan":"optional single-card local F0 only after separate authority review","p0_escalation_rule":"P0 requires a separate scientific/experiment authority after valid local evidence","selection_before_outcome":True,"core_method_frozen":True}
 def review(self,fail=''):
  checks={k:True for k in REVIEW_CHECKS};
  if fail: checks[fail]=False
  return {"reviewer_role":REVIEWER_ROLE,"reviewer_ref":"independent-blueprint-reviewer:private","reviewed_at":"2027-04-04T12:00:00+00:00","checks":checks,"risk_analysis":"The local plan is bounded, falsifiable, and separates support/runtime failures from scientific outcomes.","failure_if_blocked":"Repair the blueprint only; do not launch local validation."}
 def test_method_review_pass_required(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); c,d,r=self.fixture(root); bad=dict(r); bad['status']='REOPEN_METHOD_REVIEW_BLOCKED'
   with self.assertRaisesRegex(RuntimeError,'method review PASS'): build_reopen_experiment_blueprint(contract=c,method_design=d,method_review=bad,blueprint_spec=self.spec())
 def test_blueprint_frozen_no_execution_authority(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); c,d,r=self.fixture(root); b=build_reopen_experiment_blueprint(contract=c,method_design=d,method_review=r,blueprint_spec=self.spec()); self.assertTrue(validate_reopen_experiment_blueprint(b)); self.assertFalse(b['execution_authorized']); self.assertFalse(b['local_validation_authority']); self.assertFalse(b['gpu_authority']); row=publish_reopen_blueprint_receipt(root,b); self.assertEqual(validate_reopen_blueprint_ledger(row),[])
 def test_budget_cannot_exceed_method_cap(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); c,d,r=self.fixture(root); s=self.spec(); s['budget']['max_gpu_hours']=10
   with self.assertRaisesRegex(RuntimeError,'exceeds frozen method cap'): build_reopen_experiment_blueprint(contract=c,method_design=d,method_review=r,blueprint_spec=s)
 def test_review_pass_only_grants_authorization_review_eligibility(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); c,d,r=self.fixture(root); b=build_reopen_experiment_blueprint(contract=c,method_design=d,method_review=r,blueprint_spec=self.spec()); publish_reopen_blueprint_receipt(root,b); q=build_reopen_blueprint_review(blueprint=b,review_packet=self.review()); self.assertTrue(validate_reopen_blueprint_review(q)); self.assertEqual(q['status'],REVIEW_PASS); self.assertTrue(q['local_validation_authorization_review_eligible']); self.assertTrue(q['pre_experiment_compiler_input_eligible']); self.assertFalse(q['execution_authorized']); row=publish_reopen_blueprint_receipt(root,q); self.assertEqual(validate_reopen_blueprint_ledger(row),[])
 def test_single_failed_check_blocks(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); c,d,r=self.fixture(root); b=build_reopen_experiment_blueprint(contract=c,method_design=d,method_review=r,blueprint_spec=self.spec()); q=build_reopen_blueprint_review(blueprint=b,review_packet=self.review('outcome_semantics_typed_pass')); self.assertEqual(q['status'],REVIEW_BLOCK); self.assertFalse(q['local_validation_authorization_review_eligible'])
 def test_private_reviewer_ref_redacted_and_tamper_detected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); c,d,r=self.fixture(root); b=build_reopen_experiment_blueprint(contract=c,method_design=d,method_review=r,blueprint_spec=self.spec()); publish_reopen_blueprint_receipt(root,b); q=build_reopen_blueprint_review(blueprint=b,review_packet=self.review()); publish_reopen_blueprint_receipt(root,q); pub=public_reopen_blueprint_summary(root,c['contract_id']); text=json.dumps(pub); self.assertNotIn('independent-blueprint-reviewer:private',text); self.assertTrue(pub['reviewer_ref_sha256']); bad=copy.deepcopy(q); bad['gpu_authority']=True; self.assertFalse(validate_reopen_blueprint_review(bad))

if __name__=='__main__': unittest.main()
