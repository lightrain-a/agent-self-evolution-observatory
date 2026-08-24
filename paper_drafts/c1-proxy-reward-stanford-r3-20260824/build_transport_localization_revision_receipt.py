#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[1]
PAPER='D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE';REV='ICLR-TRANSPORT-LOCALIZATION-B10-20260824'
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path):
 d=json.loads(p.read_text());
 if not isinstance(d,dict):raise RuntimeError(f'not object:{p}')
 return d
q=load(HERE/'manuscript-qa.json');loc=load(HERE/'transport-localization-evidence.json');follow=load(HERE/'baseline-aligned-followup-evidence.json')
if q.get('status')!='PASS' or q.get('revision')!=REV or not all(q['checks'].values()):raise RuntimeError('QA not pass')
if loc.get('status')!='TRANSPORT_LOCALIZATION_COMPLETE':raise RuntimeError('localization drift')
b10=loc['experiments']['B10_native_first_action_transport'];b10d=loc['experiments']['B10D_zero_call_process_diagnostic'];acct=loc['execution_accounting'];cb=loc['claim_boundary']
if not (b10['complete_calls']==432 and b10['gate_pass'] is False and abs(b10['mean_success_failure_first_action_tv']-.069444)<1e-9 and abs(b10['permutation_p']-.580094)<1e-9):raise RuntimeError('B10 drift')
if not (b10d['coarse_action_family_mean_success_failure_tv']==.027778 and b10d['mean_next_goal_success_failure_excess_over_within']==.016593):raise RuntimeError('B10D drift')
if cb['generic_memory_presence_first_action_effect_confirmatory'] is not False or cb['model_theory_cause_established'] is not False:raise RuntimeError('claim boundary drift')
receipt={'schema_version':'1.0','artifact_type':'transport-localization-revision-receipt','paper_id':PAPER,'status':'TRANSPORT_LOCALIZATION_INTEGRATED_QA_PASS','revision':REV,'title':'Reward Errors Become Persistent State: Write-Time Causality and Transport Boundaries in Agent Memory','paper_pdf_sha256':sha(HERE/'paper.pdf'),'manuscript_qa_sha256':sha(HERE/'manuscript-qa.json'),'transport_localization_evidence_sha256':sha(HERE/'transport-localization-evidence.json'),'b10_process_diagnostics_sha256':sha(HERE/'b10-process-diagnostics.json'),'prior_followup_evidence_sha256':sha(HERE/'baseline-aligned-followup-evidence.json'),'paper_story_sha256':sha(REPO/'paper-story-reward-memory.js'),'paper_reader_data_sha256':sha(REPO/'paper-reader-data.js'),'qa_checks_passed':sum(q['checks'].values()),'qa_checks_total':len(q['checks']),'abstract_words_approx':q['abstract_words_approx'],'main_text_pages':q['main_text_pages'],'references_begin_page':q['references_begin_page'],'pdf_pages_total':q['pdf_pages_total'],'b10':b10,'b10d':b10d,'mechanism_localization':loc['mechanism_localization'],'claim_boundary':cb,'execution_accounting':acct,'current_revision_new_provider_calls':432,'current_revision_new_scientifically_usable_process_calls':432,'current_revision_new_terminal_rollouts':0,'full_paper_observable_provider_posts_lower_bound':1915,'scientific_values_changed':True,'scientific_claims_expanded':False,'external_review_calls_current_revision':0,'external_review_deferred_to_evening':True,'canonical_stable_registry_overwritten':False,'canonical_note':'B10 remains a daytime candidate update; stable PaperRegistry/acceptance projection is intentionally unchanged pending the next external review.','scientific_authority':False,'experiment_authority':False,'claim_expansion_authority':False,'submission_authority':False}
out=HERE/'transport-localization-revision-receipt.json';out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':receipt['status'],'qa':f"{receipt['qa_checks_passed']}/{receipt['qa_checks_total']}",'pdf_sha256':receipt['paper_pdf_sha256'],'b10_calls':432,'full_lower_bound':1915,'external_review_calls':0},indent=2))