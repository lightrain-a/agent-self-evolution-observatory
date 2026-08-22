from __future__ import annotations
import copy,hashlib,json,tempfile,unittest
from pathlib import Path
from .experiment_authority import validate_authority
from .resource_lease import list_gpu_leases
from .reopened_local_f0_completion import *
from .reopened_local_f0_run import start_and_publish_reopened_local_f0_run
from .test_reopened_local_f0_run import ReopenedLocalF0RunTest

class ReopenedLocalF0CompletionTest(unittest.TestCase):
 def running(self,root:Path):
  h=ReopenedLocalF0RunTest(methodName='test_start_acquires_resource_lease_and_creates_run_root_without_scientific_authority'); kw=h.start_kwargs(root); run,_=start_and_publish_reopened_local_f0_run(**kw); return kw,run
 def artifacts(self,run):
  rr=Path(run['run_root']); rows=[]
  for name,role,data in [('raw.jsonl','raw-trace','{"unit":1}\n'),('progress.json','progress','{"completed":1}\n'),('execution-summary.json','execution-summary','{"status":"complete"}\n')]:
   p=rr/name;p.write_text(data);rows.append({'relative_path':name,'role':role,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
  return rows
 def complete(self,root:Path,outcome='SCREENING-SIGNAL',units=10,calls=40,gpu=1.0):
  kw,run=self.running(root); return kw,run,complete_run(root=root,run_start=run,local_authorization=kw['local_authorization'],typed_execution_outcome=outcome,completed_units=units,provider_calls=calls,gpu_hours_used=gpu,artifact_manifest=self.artifacts(run),completed_at='2027-04-06T12:00:00+00:00')
 def packet(self,fail=''):
  checks={k:True for k in CHECKS}
  if fail:checks[fail]=False
  return {'adjudicator_role':ADJUDICATOR_ROLE,'adjudicator_ref':'independent-f0-adjudicator:private','adjudicated_at':'2027-04-06T13:00:00+00:00','checks':checks}
 def blueprint(self,kw):
  return kw['pre_experiment_receipt']['blueprint_sha256']
 def load_blueprint_receipts(self,root,contract_id):
  row=json.loads((root/'scientific-contract-experiment-blueprints'/f'{contract_id}.json').read_text()); receipts=[e['receipt'] for e in row['events']]; return receipts[0],receipts[1]
 def test_completion_releases_resource_and_experiment_authority_before_adjudication(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);kw,run,c=self.complete(root);self.assertTrue(validate_completion(c));self.assertEqual(c['status'],COMPLETION_READY);self.assertTrue(c['resource_lease_released']);self.assertTrue(c['experiment_authority_released']);self.assertFalse(validate_authority(root,run['contract_id'],run['experiment_authority_id'],run['plan_hash'])['valid']);self.assertFalse(any(x.get('lease_id')==run['gpu_lease_id'] for x in list_gpu_leases(root,True)));self.assertFalse(c['scientific_interpretation_authorized']);self.assertFalse(c['p0_authorization_review_eligible'])
 def test_signal_only_opens_p0_authorization_review_not_p0_or_claim_update(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);kw,run,c=self.complete(root,'SCREENING-SIGNAL');b,br=self.load_blueprint_receipts(root,run['contract_id']);a=adjudicate_evidence(completion=c,blueprint=b,blueprint_review=br,packet=self.packet());self.assertTrue(validate_adjudication(a));self.assertEqual(a['status'],SIGNAL);self.assertTrue(a['p0_authorization_review_eligible']);self.assertFalse(a['p0_authorized']);self.assertFalse(a['claim_update_authorized']);self.assertFalse(a['method_verdict_authorized']);self.assertTrue(a['parent_claim_status_unchanged'])
 def test_valid_no_signal_has_zero_negative_scientific_authority(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);kw,run,c=self.complete(root,'SCREENING-NO-SIGNAL');b,br=self.load_blueprint_receipts(root,run['contract_id']);a=adjudicate_evidence(completion=c,blueprint=b,blueprint_review=br,packet=self.packet());self.assertEqual(a['status'],NO_SIGNAL);self.assertFalse(a['p0_authorization_review_eligible']);self.assertFalse(a['scientific_authority']);self.assertFalse(a['method_verdict_authorized'])
 def test_support_protocol_runtime_budget_and_baseline_are_typed_separately(self):
  cases=[('SCREENING-SIGNAL','support_qualification_pass',SUPPORT_STOP),('SCREENING-SIGNAL','protocol_validity_pass',PROTOCOL_STOP),('RUNTIME-ERROR','',RUNTIME_STOP),('IMPLEMENTATION-ERROR','',IMPLEMENTATION_STOP),('BUDGET-STOP','',BUDGET_STOP),('BASELINE-FLOOR','',BASELINE_BOUNDARY)]
  for outcome,fail,expected in cases:
   with self.subTest(expected=expected),tempfile.TemporaryDirectory() as td:
    root=Path(td);kw,run,c=self.complete(root,outcome);b,br=self.load_blueprint_receipts(root,run['contract_id']);a=adjudicate_evidence(completion=c,blueprint=b,blueprint_review=br,packet=self.packet(fail));self.assertEqual(a['status'],expected);self.assertFalse(a['p0_authorization_review_eligible']);self.assertFalse(a['scientific_authority'])
 def test_manifest_or_budget_violation_forces_protocol_hold_before_scientific_interpretation(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);kw,run=self.running(root);manifest=self.artifacts(run)[:-1];c=complete_run(root=root,run_start=run,local_authorization=kw['local_authorization'],typed_execution_outcome='SCREENING-SIGNAL',completed_units=10,provider_calls=40,gpu_hours_used=1.0,artifact_manifest=manifest);self.assertEqual(c['status'],COMPLETION_HOLD);b,br=self.load_blueprint_receipts(root,run['contract_id']);a=adjudicate_evidence(completion=c,blueprint=b,blueprint_review=br,packet=self.packet());self.assertEqual(a['status'],PROTOCOL_STOP)
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);kw,run=self.running(root);c=complete_run(root=root,run_start=run,local_authorization=kw['local_authorization'],typed_execution_outcome='SCREENING-SIGNAL',completed_units=13,provider_calls=40,gpu_hours_used=1.0,artifact_manifest=self.artifacts(run));self.assertEqual(c['status'],COMPLETION_HOLD)
 def test_append_only_ledger_requires_completion_before_adjudication_and_redacts_private_reviewer(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);kw,run,c=self.complete(root);b,br=self.load_blueprint_receipts(root,run['contract_id']);a=adjudicate_evidence(completion=c,blueprint=b,blueprint_review=br,packet=self.packet())
   with self.assertRaisesRegex(RuntimeError,'published completion'):publish_receipt(root,a)
   first=publish_receipt(root,c);row=publish_receipt(root,a);row2=publish_receipt(root,a);self.assertEqual(len(first['events']),1);self.assertEqual(len(row['events']),2);self.assertEqual(len(row2['events']),2);self.assertEqual(validate_completion_ledger(row2),[]);pub=public_completion(root,run['contract_id']);self.assertEqual(pub['status'],SIGNAL);self.assertTrue(pub['p0_authorization_review_eligible']);self.assertNotIn('independent-f0-adjudicator:private',json.dumps(pub))
 def test_tamper_is_detected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);kw,run,c=self.complete(root);bad=copy.deepcopy(c);bad['completed_units']=99;self.assertFalse(validate_completion(bad));b,br=self.load_blueprint_receipts(root,run['contract_id']);a=adjudicate_evidence(completion=c,blueprint=b,blueprint_review=br,packet=self.packet());bad2=copy.deepcopy(a);bad2['p0_authorized']=True;self.assertFalse(validate_adjudication(bad2))
if __name__=='__main__':unittest.main()
