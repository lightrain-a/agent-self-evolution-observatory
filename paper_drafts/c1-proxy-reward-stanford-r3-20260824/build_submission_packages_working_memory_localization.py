#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,shutil,tempfile,zipfile
from pathlib import Path
from typing import Any
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[1];SRC=HERE/'source';DL=REPO/'downloads'
BASE='D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE-working-memory-localization-20260824'
PDF=DL/f'{BASE}.pdf';SOURCE=DL/f'{BASE}-source.zip';SUPP=DL/f'{BASE}-supplement.zip'
REV='ICLR-WORKING-MEMORY-LOCALIZATION-B11-20260824'
FORBIDDEN=['/home/','/data/','wyt@','222.20.','202.69.','10.42.','ARK_API_KEY','source_message_ref','resp_']
PRIVATE=('path','run_root','artifact_path','provider_env_file','source_message_ref','response_id','raw_sha256','next_goal_sha256')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def writej(p,x):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def sanitize(v:Any)->Any:
 if isinstance(v,dict):
  o={}
  for k,x in v.items():
   lk=str(k).lower()
   if lk in {'raw_sha256','next_goal_sha256'}:continue
   if any(f in lk for f in PRIVATE) and not lk.endswith('sha256'):continue
   if lk=='api_key_in_output':continue
   o[k]=sanitize(x)
  return o
 if isinstance(v,list):return [sanitize(x) for x in v]
 if isinstance(v,str) and any(t in v for t in FORBIDDEN):return '<private-redacted>'
 return v
def copy_source(dst):
 dst.mkdir(parents=True,exist_ok=True)
 for n in ['main.tex','references.bib','iclr2027_conference.bst','iclr2027_conference.sty','natbib.sty','fancyhdr.sty','build_figures.py']:shutil.copy2(SRC/n,dst/n)
 shutil.copytree(SRC/'figures',dst/'figures');shutil.copytree(SRC/'sections',dst/'sections')
def zip_tree(root,out):
 with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted(Path(root).rglob('*')):
   if p.is_file():z.write(p,p.relative_to(Path(root).parent))
def scan(root):
 hits=[]
 for p in Path(root).rglob('*'):
  if not p.is_file() or p.suffix.lower() in {'.pdf','.png','.jpg','.jpeg','.zip'}:continue
  try:s=p.read_text()
  except:continue
  for t in FORBIDDEN:
   if t in s:hits.append(f'{p.relative_to(root)}::{t}')
 return hits
def main():
 q=load(HERE/'manuscript-qa.json');b=load(HERE/'b11-working-memory-localization-evidence.json');raw=load(HERE/'b11-working-memory-attribution.json');rec=load(HERE/'working-memory-localization-revision-receipt.json')
 if q.get('status')!='PASS' or q.get('revision')!=REV or sum(q['checks'].values())!=len(q['checks']) or len(q['checks'])!=40:raise RuntimeError('B11 QA drift')
 if b.get('status')!='B11_WORKING_MEMORY_LOCALIZATION_COMPLETE_STOP' or b['stop_decision']['B12_provider_experiment_authorized'] is not False:raise RuntimeError('B11 boundary drift')
 DL.mkdir(parents=True,exist_ok=True);shutil.copy2(HERE/'paper.pdf',PDF)
 with tempfile.TemporaryDirectory(prefix='c1-b11-package-') as td:
  tmp=Path(td);src=tmp/'source';copy_source(src);zip_tree(src,SOURCE);ss=sha(SOURCE);ps=sha(PDF);supp=tmp/'supplement';ev=supp/'evidence';ev.mkdir(parents=True)
  locals={'manuscript-qa.json':HERE/'manuscript-qa.json','baseline-aligned-expansion-evidence.json':HERE/'baseline-aligned-expansion-evidence.json','baseline-aligned-followup-evidence.json':HERE/'baseline-aligned-followup-evidence.json','transport-localization-evidence.json':HERE/'transport-localization-evidence.json','b11-working-memory-attribution.json':HERE/'b11-working-memory-attribution.json','b11-working-memory-localization-evidence.json':HERE/'b11-working-memory-localization-evidence.json','working-memory-localization-revision-receipt.json':HERE/'working-memory-localization-revision-receipt.json','f2r1-chronology-receipt.json':HERE/'f2r1-chronology-receipt.json','o5-manuscript-evidence.json':HERE/'o5-manuscript-evidence.json','o6-final-evidence.json':HERE/'o6-final-evidence.json'}
  for n,p in locals.items():writej(ev/n,sanitize(load(p)))
  a=b['branch_specific_uptake'];g=b['generic_common_core_tendency'];link=b['transport_linkage'];sim=b['simple_similarity_falsifier']
  proj={'schema_version':'1.0','receipt_type':'supplement-current-projection','paper_id':b['paper_id'],'revision':'iclr-working-memory-localization-b11-20260824','title':rec['title'],'current_pdf_sha256':ps,'current_source_zip_sha256':ss,'claim_expansion':False,'new_provider_calls_exact':0,'new_rollouts':0,'full_paper_observable_provider_posts_lower_bound':1915,'working_memory_outputs_reused':432,'working_memory_complete_fields':432,'branch_shift':a['mean_pair_relative_shift'],'branch_shift_p_posthoc':a['posthoc_permutation_p'],'branch_shift_dz':a['paired_dz'],'common_centroid_uptake':g['mean_common_centroid_uptake'],'common_centroid_p_posthoc':g['posthoc_signflip_p'],'working_memory_vs_first_action_pearson':link['pearson_working_memory_shift_vs_first_action_tv'],'working_memory_vs_terminal_pearson':link['pearson_working_memory_shift_vs_terminal_effect'],'input_memory_distance_mean':sim['input_memory_cosine_distance_mean'],'input_distance_vs_working_memory_shift':sim['pearson_distance_vs_working_memory_shift'],'B12_provider_experiment_authorized':False,'main_text_pages':q['main_text_pages'],'references_begin_page':q['references_begin_page'],'pdf_pages_total':q['pdf_pages_total'],'canonical_stable_registry_overwritten':False,'scientific_authority':False,'experiment_authority':False,'submission_authority':False}
  writej(supp/'CURRENT-PROJECTION.json',proj)
  (supp/'README.md').write_text('''# Reward Errors Become Persistent State — working-memory localization supplement\n\nB11 is a zero-provider-call, post-hoc mechanism diagnostic over the 432 already archived B10 first-action outputs. The BrowserUse-style response schema emits `current_state.memory` before the first action; all 432 fields are recoverable (405 strict JSON, 27 narrow string recoveries). Pair-relative semantic attribution is computed with the exact cached all-MiniLM-L6-v2 encoder against the success/failure input-memory pair.\n\nThe mean branch-specific working-memory shift is 0.003347 (paired dz=0.148; post-hoc within-state permutation p=0.2052), so branch-specific internalization is not established. Common-centroid uptake is 0.02233 (post-hoc sign-flip p=0.0664), suggestive only. Working-memory branch shift correlates descriptively with first-action TV (Pearson r=0.464; Spearman rho=0.419; leave-one-out Pearson 0.358--0.515) but not terminal absolute effect (r=-0.023). Input S/F memory distance does not explain these stages monotonically.\n\nNo new provider calls, terminal rollouts, process rollouts, training, or GPU runs are added by B11. The full-paper observable provider-POST lower bound remains at least 1,915. B12 provider execution is explicitly not authorized from this post-hoc result; positive B10/B11 cells may not be selected for follow-up. Stable canonical PaperRegistry remains unchanged, and no daytime external review is triggered.\n\nPrivate raw working-memory text, host paths, credentials, provider response IDs, and private content-addressed identifiers are excluded. Run `python verify_current_supplement.py` to validate the public projection.\n''')
  verifier=r'''from pathlib import Path
import json,sys
R=Path(__file__).resolve().parent;E=R/'evidence'
def L(n):return json.load(open(E/n))
q=L('manuscript-qa.json');b=L('b11-working-memory-localization-evidence.json');a=L('b11-working-memory-attribution.json');r=L('working-memory-localization-revision-receipt.json');p=json.load(open(R/'CURRENT-PROJECTION.json'))
x=b['branch_specific_uptake'];g=b['generic_common_core_tendency'];t=b['transport_linkage'];s=b['simple_similarity_falsifier']
checks=[q['status']=='PASS',q['revision']=='ICLR-WORKING-MEMORY-LOCALIZATION-B11-20260824',sum(q['checks'].values())==len(q['checks'])==40,q['main_text_pages']==9,q['references_begin_page']==10,q['pdf_pages_total']==19,q['new_provider_calls_exact']==0,q['new_process_rollouts']==0,q['updated_full_paper_observable_provider_posts_lower_bound']==1915,
b['status']=='B11_WORKING_MEMORY_LOCALIZATION_COMPLETE_STOP',b['provider_calls']==0,b['new_rollouts']==0,b['stop_decision']['B12_provider_experiment_authorized'] is False,b['working_memory_observable']['complete_fields']==432,abs(x['mean_pair_relative_shift']-.0033469072206773693)<1e-12,abs(x['posthoc_permutation_p']-.2051979480205198)<1e-12,abs(x['paired_dz']-.1479075191935324)<1e-12,abs(g['mean_common_centroid_uptake']-.022332304099109024)<1e-12,abs(g['posthoc_signflip_p']-.06639933600663993)<1e-12,abs(t['pearson_working_memory_shift_vs_first_action_tv']-.46437044778212805)<1e-12,abs(t['pearson_working_memory_shift_vs_terminal_effect']+.022965905301220373)<1e-12,abs(s['pearson_distance_vs_working_memory_shift']-.09547663332085542)<1e-12,
a['status']=='B11_POSTHOC_ZERO_PROVIDER_DIAGNOSTIC_COMPLETE',a['provider_calls']==0,a['confirmatory_gate'] is None,a['extraction']['complete_fields']==432,
r['status']=='WORKING_MEMORY_LOCALIZATION_INTEGRATED_QA_PASS',r['current_revision_new_provider_calls']==0,r['stop_decision']['B12_provider_experiment_authorized'] is False,r['external_review_calls_current_revision']==0,r['canonical_stable_registry_overwritten'] is False,
p['revision']=='iclr-working-memory-localization-b11-20260824',p['claim_expansion'] is False,p['new_provider_calls_exact']==0,p['B12_provider_experiment_authorized'] is False,abs(p['branch_shift']-.0033469072206773693)<1e-12,abs(p['common_centroid_uptake']-.022332304099109024)<1e-12,p['full_paper_observable_provider_posts_lower_bound']==1915,p['canonical_stable_registry_overwritten'] is False]
print({'checks':len(checks),'passed':sum(checks),'pass':all(checks)});sys.exit(0 if all(checks) else 1)
'''
  (supp/'verify_current_supplement.py').write_text(verifier)
  hits=scan(supp)
  if hits:raise RuntimeError('supplement privacy scan failed: '+'; '.join(hits[:20]))
  zip_tree(supp,SUPP)
 print(json.dumps({'pdf':{'path':str(PDF),'sha256':sha(PDF)},'source_zip':{'path':str(SOURCE),'sha256':sha(SOURCE)},'supplement_zip':{'path':str(SUPP),'sha256':sha(SUPP)},'privacy_scan':'PASS'},indent=2))
if __name__=='__main__':main()
