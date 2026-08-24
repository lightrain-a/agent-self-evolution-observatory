#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,shutil,tempfile,zipfile
from pathlib import Path
from typing import Any
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[1];SRC=HERE/'source';DL=REPO/'downloads'
RUN10=Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b10-native-first-action-transport-20260824')
PDF=DL/'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE-transport-localization-20260824.pdf'
SOURCE=DL/'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE-transport-localization-20260824-source.zip'
SUPP=DL/'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE-transport-localization-20260824-supplement.zip'
FORBIDDEN=['/home/','/data/','wyt@','222.20.','202.69.','10.42.','ARK_API_KEY','source_message_ref','resp_']
PRIVATE=('path','run_root','artifact_path','provider_env_file','source_message_ref','response_id','raw_sha256','next_goal_sha256')
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->Any:return json.loads(p.read_text(encoding='utf-8'))
def writej(p:Path,x:Any):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def sanitize(v:Any)->Any:
 if isinstance(v,dict):
  out={}
  for k,x in v.items():
   lk=str(k).lower()
   if lk in {'raw_sha256','next_goal_sha256'}:continue
   if any(f in lk for f in PRIVATE) and not lk.endswith('sha256'):continue
   if lk in {'api_key_in_output'}:continue
   out[k]=sanitize(x)
  return out
 if isinstance(v,list):return [sanitize(x) for x in v]
 if isinstance(v,str) and any(t in v for t in FORBIDDEN):return '<private-redacted>'
 return v
def public(p:Path)->dict[str,Any]:return {'schema_version':'1.0','projection_type':'anonymous-public-projection','source_artifact_sha256':sha(p),'payload':sanitize(load(p))}
def copy_source(dst:Path):
 dst.mkdir(parents=True,exist_ok=True)
 for n in ['main.tex','references.bib','iclr2027_conference.bst','iclr2027_conference.sty','natbib.sty','fancyhdr.sty','build_figures.py']:shutil.copy2(SRC/n,dst/n)
 shutil.copytree(SRC/'figures',dst/'figures');shutil.copytree(SRC/'sections',dst/'sections')
def zip_tree(root:Path,out:Path):
 out.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted(root.rglob('*')):
   if p.is_file():z.write(p,p.relative_to(root.parent))
def scan(root:Path)->list[str]:
 hits=[]
 for p in root.rglob('*'):
  if not p.is_file() or p.suffix.lower() in {'.pdf','.png','.jpg','.jpeg','.zip'}:continue
  try:s=p.read_text(encoding='utf-8')
  except UnicodeDecodeError:continue
  for t in FORBIDDEN:
   if t in s:hits.append(f'{p.relative_to(root)}::{t}')
 return hits
def build_supp(root:Path,source_sha:str,pdf_sha:str):
 ev=root/'evidence';ev.mkdir(parents=True,exist_ok=True)
 locals={
 'manuscript-qa.json':HERE/'manuscript-qa.json',
 'baseline-aligned-expansion-evidence.json':HERE/'baseline-aligned-expansion-evidence.json',
 'baseline-aligned-followup-evidence.json':HERE/'baseline-aligned-followup-evidence.json',
 'transport-localization-evidence.json':HERE/'transport-localization-evidence.json',
 'transport-localization-revision-receipt.json':HERE/'transport-localization-revision-receipt.json',
 'b10-process-diagnostics.json':HERE/'b10-process-diagnostics.json',
 'f2r1-chronology-receipt.json':HERE/'f2r1-chronology-receipt.json',
 'o5-manuscript-evidence.json':HERE/'o5-manuscript-evidence.json',
 'o6-final-evidence.json':HERE/'o6-final-evidence.json',
 'o6-full-bank-corruption-reduction.json':HERE/'o6-full-bank-corruption-reduction.json'}
 for n,p in locals.items():writej(ev/n,sanitize(load(p)))
 for n,p in {'b10-contract-public.json':RUN10/'b10-contract.json','b10-result-public.json':RUN10/'b10-result.json'}.items():writej(ev/n,public(p))
 q=load(HERE/'manuscript-qa.json');loc=load(HERE/'transport-localization-evidence.json');rec=load(HERE/'transport-localization-revision-receipt.json');b10=loc['experiments']['B10_native_first_action_transport'];d=loc['experiments']['B10D_zero_call_process_diagnostic']
 proj={'schema_version':'1.0','receipt_type':'supplement-current-projection','paper_id':rec['paper_id'],'revision':'iclr-transport-localization-b10-20260824','title':rec['title'],'current_pdf_sha256':pdf_sha,'current_source_zip_sha256':source_sha,'claim_expansion':False,'external_review_calls_current_revision':0,'write_complete_pairs':20,'expanded_bank_retrieval_hits':'125/172','native_terminal_branch_effect':.020833,'native_terminal_branch_p':.428866,'native_first_action_sf_tv':b10['mean_success_failure_first_action_tv'],'native_first_action_p':b10['permutation_p'],'native_first_action_floor':b10['practical_tv_floor'],'native_first_action_gate_pass':b10['gate_pass'],'native_first_action_nonzero_states':b10['states_with_nonzero_success_failure_tv'],'native_first_action_modal_branch_differences':b10['states_with_modal_success_failure_difference'],'descriptive_memory_presence_first_action_tv':b10['mean_memory_presence_first_action_tv'],'descriptive_memory_presence_modal_shift_states':b10['states_where_either_memory_modal_differs_from_no_memory'],'coarse_action_family_sf_tv_posthoc':d['coarse_action_family_mean_success_failure_tv'],'next_goal_branch_excess_posthoc':d['mean_next_goal_success_failure_excess_over_within'],'generic_memory_presence_first_action_effect_confirmatory':False,'model_theory_cause_established':False,'new_provider_calls_exact':q['new_provider_calls_exact'],'new_process_rollouts':q['new_process_rollouts'],'new_terminal_rollouts':q['new_terminal_rollouts'],'baseline_program_provider_posts_total':q['baseline_program_provider_posts_total'],'baseline_program_usable_completions_total':q['baseline_program_scientifically_usable_completions_total'],'baseline_program_terminal_rollouts_total':q['baseline_program_terminal_rollouts_total'],'baseline_program_process_rollouts_total':q['baseline_program_process_rollouts_total'],'full_paper_observable_provider_posts_lower_bound':q['updated_full_paper_observable_provider_posts_lower_bound'],'main_text_pages':q['main_text_pages'],'references_begin_page':q['references_begin_page'],'pdf_pages_total':q['pdf_pages_total'],'canonical_stable_registry_overwritten':False,'scientific_authority':False,'experiment_authority':False,'submission_authority':False}
 writej(root/'CURRENT-PROJECTION.json',proj)
 (root/'README.md').write_text('''# Reward Errors Become Persistent State — transport-localization supplement\n\nThis anonymous supplement adds B10, a preregistered pre-terminal first-action transport test on the same 36 native-retrieval-hit tasks used by B4/B5. All 432 calls complete with zero provider or unrecoverable parse failures. The registered success/failure first-action mean TV is 0.069444 with permutation p=0.580094, below the inherited 0.20 process floor; 9/36 states have any S/F TV and 0/36 change modal branch action. A larger memory-versus-no-memory TV of 0.170139 with six modal shifts is secondary/descriptive only because no confirmatory presence gate was preregistered.\n\nA zero-call post-hoc diagnostic removes click indices (coarse S/F action-family TV 0.027778) and compares next-goal text: cross-branch distance 0.464370 versus within-branch 0.447776, for only 0.016593 branch-specific excess. Memory-versus-no-memory next-goal distance is 0.554403. These diagnostics cannot rescue B10; together with the earlier raw-trajectory and fractional-reference controls they localize the dominant attenuation before or at branch-specific policy uptake.\n\nB10 adds 432 process-level provider POSTs and 432 scientifically usable process calls, but zero new terminal rollouts. The baseline program now contains 1,074 observable POSTs and 1,040 scientifically usable completions (32 writer, 576 terminal, 432 first-action). The full-paper observable provider-POST lower bound is at least 1,915. No training or local GPU fine-tuning is used. Stable canonical PaperRegistry is not overwritten, and no daytime external review is triggered.\n\nPrivate host paths, credentials, raw provider text, response IDs, and private content-addressed output identifiers are excluded. Run `python verify_current_supplement.py` to validate this public projection.\n''',encoding='utf-8')
 verifier=r'''from pathlib import Path
import json,sys
R=Path(__file__).resolve().parent;E=R/'evidence'
def L(n):return json.load(open(E/n))
q=L('manuscript-qa.json');loc=L('transport-localization-evidence.json');rec=L('transport-localization-revision-receipt.json');diag=L('b10-process-diagnostics.json');b10=L('b10-result-public.json')['payload'];p=json.load(open(R/'CURRENT-PROJECTION.json'))
x=loc['experiments']['B10_native_first_action_transport'];d=loc['experiments']['B10D_zero_call_process_diagnostic'];a=loc['execution_accounting'];c=loc['claim_boundary']
checks=[q['status']=='PASS',q['revision']=='ICLR-TRANSPORT-LOCALIZATION-B10-20260824',sum(q['checks'].values())==len(q['checks'])==39,q['main_text_pages']==9,q['references_begin_page']==10,q['pdf_pages_total']==18,q['new_provider_calls_exact']==432,q['new_process_rollouts']==432,q['new_terminal_rollouts']==0,q['updated_full_paper_observable_provider_posts_lower_bound']==1915,
loc['status']=='TRANSPORT_LOCALIZATION_COMPLETE',x['complete_calls']==432,x['provider_failures_or_parse_failures']==0,abs(x['mean_success_failure_first_action_tv']-.069444)<1e-12,abs(x['permutation_p']-.580094)<1e-12,abs(x['practical_tv_floor']-.2)<1e-12,x['gate_pass'] is False,x['states_with_nonzero_success_failure_tv']==9,x['states_with_modal_success_failure_difference']==0,abs(x['mean_memory_presence_first_action_tv']-.170139)<1e-12,x['states_where_either_memory_modal_differs_from_no_memory']==6,
diag['status']=='B10_PROCESS_DIAGNOSTIC_COMPLETE',diag['provider_calls']==0,abs(d['coarse_action_family_mean_success_failure_tv']-.027778)<1e-12,abs(d['mean_next_goal_success_failure_excess_over_within']-.016593)<1e-12,abs(d['mean_next_goal_memory_vs_no_memory_distance']-.554403)<1e-12,
b10['status']=='B10_EXECUTION_COMPLETE',b10['summary']['provider_calls_complete']==432,b10['summary']['provider_failures_or_parse_failures']==0,abs(b10['summary']['observed_mean_success_failure_tv']-.069444)<1e-12,abs(b10['summary']['permutation_p_ge_observed']-.580094)<1e-12,b10['summary']['primary_gate_pass'] is False,
a['b10_new_provider_posts']==432,a['b10_scientifically_usable_process_calls']==432,a['full_paper_observable_provider_posts_lower_bound_after_b10']==1915,c['B10_native_first_action_branch_transport_supported'] is False,c['generic_memory_presence_first_action_effect_confirmatory'] is False,c['model_theory_cause_established'] is False,
rec['status']=='TRANSPORT_LOCALIZATION_INTEGRATED_QA_PASS',rec['external_review_calls_current_revision']==0,rec['canonical_stable_registry_overwritten'] is False,
p['revision']=='iclr-transport-localization-b10-20260824',p['claim_expansion'] is False,p['native_first_action_gate_pass'] is False,abs(p['native_first_action_sf_tv']-.069444)<1e-12,abs(p['descriptive_memory_presence_first_action_tv']-.170139)<1e-12,p['generic_memory_presence_first_action_effect_confirmatory'] is False,p['model_theory_cause_established'] is False,p['full_paper_observable_provider_posts_lower_bound']==1915,p['canonical_stable_registry_overwritten'] is False]
print({'checks':len(checks),'passed':sum(checks),'pass':all(checks)});sys.exit(0 if all(checks) else 1)
'''
 (root/'verify_current_supplement.py').write_text(verifier,encoding='utf-8')
def main()->int:
 q=load(HERE/'manuscript-qa.json');
 if q.get('status')!='PASS' or q.get('revision')!='ICLR-TRANSPORT-LOCALIZATION-B10-20260824':raise RuntimeError('B10 QA not pass')
 DL.mkdir(parents=True,exist_ok=True);shutil.copy2(HERE/'paper.pdf',PDF)
 with tempfile.TemporaryDirectory(prefix='c1-b10-package-') as td:
  tmp=Path(td);src=tmp/'source';copy_source(src);zip_tree(src,SOURCE);ss=sha(SOURCE);ps=sha(PDF);supp=tmp/'supplement';build_supp(supp,ss,ps);hits=scan(supp)
  if hits:raise RuntimeError('supplement privacy scan failed: '+'; '.join(hits[:20]))
  zip_tree(supp,SUPP)
 print(json.dumps({'pdf':{'path':str(PDF),'sha256':sha(PDF)},'source_zip':{'path':str(SOURCE),'sha256':sha(SOURCE)},'supplement_zip':{'path':str(SUPP),'sha256':sha(SUPP)},'privacy_scan':'PASS'},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
