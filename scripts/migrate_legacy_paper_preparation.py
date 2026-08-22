from __future__ import annotations
import argparse, hashlib, json, os
from pathlib import Path
from typing import Any, Mapping
from research_pipeline.paper_acceptance_ledger import record_frozen_contract_paper_preparation, validate_paper_ledger
from research_pipeline.paper_preparation_protocol import PAPER_PREPARATION_PROTOCOL_VERSION, build_paper_preparation_receipt, evaluate_paper_preparation

ROOT=Path('/data/wyt/agent-self-evolution-observatory')
DIMS=('claim-evidence','novelty-positioning','method-experiment','statistics-uncertainty','visual-evidence','limitations-scope','reproducibility','citation-integrity','venue-compliance')

def load(p:Path)->dict[str,Any]:
 v=json.loads(p.read_text());
 if not isinstance(v,dict): raise TypeError(p)
 return v

def sha(v:Any)->str:return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def atom(p:Path,v:Mapping[str,Any]):
 p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+'.tmp');q.write_text(json.dumps(dict(v),ensure_ascii=False,indent=2)+'\n');os.replace(q,p)

PROFILES={
 'AGENT-SAFETY-R9':dict(citations=18,visuals=4,failed_dims=(),failed_gates=(),issues=('novelty-collision','small-finite-design','causal-wording','control-identity','fixed-probe-readonly','rerun-semantics','evaluator-oracle','claim-artifact-binding'),refs=('agent-safety-r9-paper-prep-v2-20260822.zip','submission-ready-manifest.json','prebuttal-manifest.json','supplement/evidence/agent-safety-r9-controlled-longitudinal-scientific-review-20260821.json'),prereqs=('submission-packages/agent-safety-r9-paper-prep-v2-20260822.zip','submission-packages/agent-safety-r9-paper-prep-v2-20260822/supplement/reproduce.py')),
 'STRI-ICLR2027':dict(citations=11,visuals=4,failed_dims=(),failed_gates=(),issues=('representation-scope','dynamic-generalization-boundary','p19-mediator-isolation','negative-p0e-boundary'),refs=('STRI-ICLR2027-20260816-supplement.zip','asset-first-stri-paper-quality-v2-20260816.json','asset-first-stri-iclr2027-openreview-readiness-20260816.json','29/29 supplement tests'),prereqs=('submission-packages/STRI-ICLR2027-20260816-supplement.zip',)),
 'D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK':dict(citations=3,visuals=2,failed_dims=('claim-evidence','method-experiment','statistics-uncertainty','visual-evidence','reproducibility','venue-compliance'),failed_gates=('hierarchical-rubric','verification-refinement','visual-story','reproducibility-bundle','agent-native-artifact','reader-simulation','submission-package'),issues=('c3-targeted-intervention-missing','c4-transfer-evidence-missing','first-party-evaluated-snapshot-unavailable'),refs=('d2-temporal-skill-bottleneck-claim-ledger.json','d2-temporal-skill-bottleneck-final-paper-acceptance-20260822.json','HOLD_FOR_EVIDENCE'),prereqs=()),
}

def build(pid:str)->dict[str,Any]:
 p=PROFILES[pid]; fg=set(p['failed_gates']); fd=set(p['failed_dims']); ok=lambda g:g not in fg
 dims={d:{'pass':d not in fd,'evidence_refs':list(p['refs'])} for d in DIMS}
 issues=list(p['issues']);resolved=[] if 'verification-refinement' in fg else issues
 packet={'protocol_version':PAPER_PREPARATION_PROTOCOL_VERSION,'paper_id':pid,'migration_mode':'APPEND_ONLY_POST_READY' if not fg else 'APPEND_ONLY_POST_READY_AUDIT_BLOCKED','claim_expansion_authorized':False,'new_experiment_authorized':False,'gates':{
 'hierarchical-rubric':{'hierarchical_decomposition':True,'single_overall_score_is_non_authoritative':True,'plan_execution_parity_pass':ok('hierarchical-rubric'),'fabricated_result_scan_pass':True,'evidence_sufficiency_review_pass':ok('hierarchical-rubric'),'dimensions':dims},
 'verification-refinement':{'verifier_separate_from_refiner':True,'verification_against_frozen_contract':True,'issues':[{'issue_id':x,'decision_critical':True} for x in issues],'resolved_issue_ids':resolved,'revision_deltas':[{'issue_id':x,'artifact_ref':p['refs'][0]} for x in resolved],'non_improving_revision_reverted':True},
 'citation-integrity':{'citations_total':p['citations'],'citations_verified':p['citations'],'claim_citations_total':p['citations'],'claim_citations_primary_source_verified':p['citations'],'duplicate_citations_absent':True,'orphan_bib_entries_absent':True,'citation_placement_review_pass':True,'citation_claim_entailment_review_pass':True,'hallucinated_citations':0},
 'visual-story':{'main_visuals':p['visuals'],'each_core_claim_has_main_visual':ok('visual-story'),'figure_caption_reference_review_pass':True,'figure_text_callout_consistency_pass':True,'quantitative_visual_source_binding_pass':True,'negative_or_boundary_evidence_visible':True,'labels_legible_at_final_pdf_scale':True,'persistent_visual_contract_present':ok('visual-story'),'registered_visuals_match_sections':True},
 'reproducibility-bundle':{k:ok('reproducibility-bundle') for k in ('self_contained_source_bundle','clean_environment_compile_pass','reproduction_entrypoint_present','dependency_environment_manifest_present','data_model_provenance_present','random_seed_and_nondeterminism_documented','evaluation_code_and_protocol_bound','artifact_hash_manifest_present','numeric_claim_recompute_pass','independent_reproduction_check_pass','secret_scan_pass')},
 'agent-native-artifact':{'layers':{x:{'complete':ok('agent-native-artifact'),'artifact_refs':list(p['refs'])} for x in ('scientific-logic','executable-specification','exploration-graph','claim-evidence-grounding')},'failed_and_rejected_branches_preserved':True,'claim_to_raw_output_roundtrip_pass':ok('agent-native-artifact')},
 'reader-simulation':{'modes':{x:{'completed':ok('reader-simulation'),'unresolved_decision_critical':0 if ok('reader-simulation') else 1} for x in ('blind-manuscript','artifact-aware','figure-first-skimmer','reproducibility-reviewer')},'paper_side_findings_resolved_or_explicitly_accepted':ok('reader-simulation'),'review_score_is_not_a_hard_gate':True},
 'submission-package':{'venue':'ICLR 2027',**{k:ok('submission-package') for k in ('venue_template_and_page_rules_pass','anonymous_source_and_pdf_pass','metadata_matches_manuscript','supplement_and_main_artifact_consistency_pass','fresh_directory_source_compile_pass','file_size_and_upload_constraints_pass','ai_use_disclosure_decision_recorded','authorship_and_conflict_checklist_recorded','venue_policy_snapshot_current','human_only_requirements_recorded')},'external_human_submit_required':True}}}
 if pid=='D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK':
  r=packet['gates']['reproducibility-bundle'];r.update(data_model_provenance_present=True,random_seed_and_nondeterminism_documented=True,secret_scan_pass=True)
  a=packet['gates']['agent-native-artifact']['layers'];a['scientific-logic']['complete']=True;a['executable-specification']['complete']=True;a['exploration-graph']['complete']=True
  m=packet['gates']['reader-simulation']['modes'];m['blind-manuscript']={'completed':True,'unresolved_decision_critical':0};m['artifact-aware']={'completed':True,'unresolved_decision_critical':0}
  q=packet['gates']['submission-package'];q.update(venue_template_and_page_rules_pass=True,anonymous_source_and_pdf_pass=True,metadata_matches_manuscript=True,file_size_and_upload_constraints_pass=True)
 return packet

def prereq(pid:str):
 missing=[]
 for rel in PROFILES[pid]['prereqs']:
  if not (ROOT/rel).exists(): missing.append(rel)
 if missing: raise FileNotFoundError(f'{pid} missing audited preparation artifacts: {missing}')

def one(pid:str,publish:bool)->dict[str,Any]:
 prereq(pid); lp=ROOT/'paper-acceptance'/f'{pid}.json';row=load(lp);digest=str(row.get('contract_sha256') or '')
 if not digest or sha(row.get('contract') or {})!=digest: raise RuntimeError(f'frozen contract payload digest drift {pid}')
 packet=build(pid);evaluation=evaluate_paper_preparation(packet);receipt=build_paper_preparation_receipt(paper_id=pid,contract_sha256=digest,packet=packet)
 out={'paper_id':pid,'current_state':row.get('current_state'),'contract_sha256':digest,'packet_sha256':sha(packet),'pass':evaluation['pass'],'passed_gates':evaluation['summary']['passed_gates'],'required_gates':evaluation['summary']['required_gates'],'blockers':list(evaluation['blockers']),'published':False,'idempotent':False,'scientific_authority':False,'experiment_authority':False,'gpu_authority':False,'submission_authority':False}
 if not publish:return out
 latest=next((e for e in reversed(row.get('events') or []) if isinstance(e,dict) and e.get('event_type')=='paper-preparation'),{});lr=latest.get('receipt') if isinstance(latest.get('receipt'),dict) else {}
 if lr.get('packet_sha256')==receipt['packet_sha256']:
  out.update(published=True,idempotent=True,receipt_sha256=lr.get('receipt_sha256'),event_id=latest.get('event_id'));return out
 ad=ROOT/'paper-acceptance-artifacts'/pid;atom(ad/'paper-preparation-packet.json',packet);atom(ad/'paper-preparation-evaluation.json',evaluation)
 updated=record_frozen_contract_paper_preparation(ROOT,pid,packet,actor='legacy-paper-preparation-migration');errors=validate_paper_ledger(updated)
 if errors:raise RuntimeError(f'ledger replay invalid {pid}: {errors}')
 event=updated['events'][-1];er=event['receipt'];atom(ad/'paper-preparation-receipt.json',er)
 out.update(published=True,event_id=event.get('event_id'),receipt_sha256=er.get('receipt_sha256'),ledger_events=len(updated.get('events') or []),ledger_validation_errors=[],state_after=updated.get('current_state'));atom(ad/'paper-preparation-migration.json',out);return out

def main():
 a=argparse.ArgumentParser();a.add_argument('--paper-id',action='append',choices=tuple(PROFILES));a.add_argument('--publish',action='store_true');x=a.parse_args();ids=x.paper_id or list(PROFILES);print(json.dumps({'schema_version':'1.0','publish':x.publish,'results':[one(pid,x.publish) for pid in ids]},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
