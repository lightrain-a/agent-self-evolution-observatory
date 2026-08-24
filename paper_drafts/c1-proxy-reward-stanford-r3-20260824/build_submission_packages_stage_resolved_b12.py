#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,shutil,tempfile,zipfile
from pathlib import Path
from typing import Any
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[1];SRC=HERE/'source';DL=REPO/'downloads'
RUN=Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b12-crossdomain-qualification-20260824')
PDF=DL/'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE-stage-resolved-b12-crossdomain-20260824.pdf';SOURCE=DL/'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE-stage-resolved-b12-crossdomain-20260824-source.zip';SUPP=DL/'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE-stage-resolved-b12-crossdomain-20260824-supplement.zip'
FORBIDDEN=['/home/','/data/','wyt@','222.20.','202.69.','10.42.','ARK_API_KEY','source_message_ref','resp_']
PRIVATE=('path','run_root','artifact_path','provider_env_file','source_message_ref','response_id','raw_sha256','answer_sha256','prompt_sha256','wrapper_sha256','memory_wrapper_sha256')
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->Any:return json.loads(p.read_text(encoding='utf-8'))
def writej(p:Path,x:Any):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def sanitize(v:Any)->Any:
 if isinstance(v,dict):
  out={}
  for k,x in v.items():
   lk=str(k).lower()
   if lk in {'api_key_in_output'}:continue
   if any(f in lk for f in PRIVATE) and not lk.endswith('file_sha256') and not lk.endswith('contract_sha256'):continue
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
def project_csv(src:Path,dst:Path,fields:list[str]):
 rows=list(csv.DictReader(src.open(encoding='utf-8')));dst.parent.mkdir(parents=True,exist_ok=True)
 with dst.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows([{k:r.get(k,'') for k in fields} for r in rows])
 return len(rows)
def build_supp(root:Path,source_sha:str,pdf_sha:str):
 ev=root/'evidence';ev.mkdir(parents=True,exist_ok=True)
 local={'manuscript-qa.json':HERE/'manuscript-qa.json','b12-crossdomain-reddit-evidence.json':HERE/'b12-crossdomain-reddit-evidence.json','stage-resolved-b12-revision-receipt.json':HERE/'stage-resolved-b12-revision-receipt.json','story-v4-argument-search.json':HERE/'story-v4-argument-search-20260824.json','story-v5-crossdomain-adjudication.json':HERE/'story-v5-crossdomain-adjudication-20260824.json','b11-scientific-evidence.json':HERE/'b11-scientific-evidence.json','working-memory-posthoc-evidence.json':HERE/'b11-working-memory-localization-evidence.json','transport-localization-evidence.json':HERE/'transport-localization-evidence.json'}
 for n,p in local.items():writej(ev/n,sanitize(load(p)))
 remote={'b12-qualification-public.json':RUN/'b12-reddit-qualification-result.json','b12-parent-public.json':RUN/'b12-reddit-execution-result.json','b12-r1-contract-public.json':RUN/'b12-reddit-r1-contract.json','b12-r1-result-public.json':RUN/'b12-reddit-r1-result.json'}
 for n,p in remote.items():writej(ev/n,public(p))
 counts={
  'qualification_csv_rows':project_csv(RUN/'b12-reddit-retrieval.csv',ev/'b12-reddit-retrieval.csv',['task_id','intent_template_id','trajectory_available','original_outcome','top1_source_task','top1_similarity','runner_up_source_task','runner_up_similarity','top1_margin','threshold_hit','offline_eligible_retrieval_hit']),
  'writer_csv_rows':project_csv(RUN/'b12-r1-writer.csv',ev/'b12-r1-writer.csv',['source_task','condition','status','memory_item_count','resolved_model']),
  'terminal_csv_rows':project_csv(RUN/'b12-r1-terminal.csv',ev/'b12-r1-terminal.csv',['future_task','selected_source_task','condition','rollout','status','benchmark_score','resolved_model'])}
 q=load(HERE/'manuscript-qa.json');b=load(HERE/'b12-crossdomain-reddit-evidence.json');rec=load(HERE/'stage-resolved-b12-revision-receipt.json');wm=load(HERE/'b11-working-memory-localization-evidence.json')
 proj={'schema_version':'1.0','receipt_type':'supplement-current-projection','paper_id':rec['paper_id'],'revision':'iclr-stage-resolved-b12-crossdomain-20260824','title':rec['title'],'current_pdf_sha256':pdf_sha,'current_source_zip_sha256':source_sha,'claim_expansion':False,'external_review_calls_current_revision':0,'story_winner_changed':False,'shopping_write_complete_pairs':20,'shopping_native_effect':.020833,'reddit_qualified_futures':b['qualification']['offline_eligible_retrieval_hits'],'reddit_selected_sources':b['qualification']['distinct_selected_source_tasks'],'reddit_write_pairs':b['writer_stage']['complete_pairs'],'reddit_write_jaccard':b['writer_stage']['mean_token_jaccard_distance'],'reddit_native_effect':b['terminal_stage']['mean_absolute_success_rate_difference'],'reddit_native_p':b['terminal_stage']['permutation_p'],'reddit_native_floor':b['terminal_stage']['practical_effect_floor'],'reddit_native_gate_pass':b['terminal_stage']['gate_pass'],'reddit_zero_tasks':b['terminal_stage']['zero_effect_tasks'],'reddit_leave_one_out_range':b['terminal_stage']['leave_one_task_out_mean_range'],'b12_observable_provider_posts':b['execution_accounting']['b12_observable_provider_posts_total'],'b12_scientifically_usable_calls':b['execution_accounting']['b12_scientifically_usable_calls'],'working_memory_posthoc_provider_calls':0,'working_memory_pair_relative_shift':wm['branch_specific_uptake']['mean_pair_relative_shift'],'working_memory_p':wm['branch_specific_uptake']['posthoc_permutation_p'],'working_memory_first_action_linkage_r':wm['transport_linkage']['pearson_working_memory_shift_vs_first_action_tv'],'full_paper_observable_provider_posts_lower_bound':q['updated_full_paper_observable_provider_posts_lower_bound'],'main_text_pages':q['main_text_pages'],'references_begin_page':q['references_begin_page'],'pdf_pages_total':q['pdf_pages_total'],'csv_rows':counts,'canonical_stable_registry_overwritten':False,'scientific_authority':False,'experiment_authority':False,'submission_authority':False}
 writej(root/'CURRENT-PROJECTION.json',proj)
 (root/'README.md').write_text('''# Reward Errors Change Memory Before They Change Policy — B12 cross-domain supplement\n\nThis anonymous supplement adds a bounded WebArena Reddit replication to the stage-resolved C1 evidence. Support is qualified before writer execution: eight deterministic retrieval-hit futures across two intent templates select four source identities. The first 4,096-token writer parent has one length/no-text support failure; no parent success contributes scientifically. A single uniform 8,192-token repair regenerates all eight writer units fresh. All four source pairs then diverge in content/title (mean token Jaccard 0.652342).\n\nAll 64 frozen Reddit terminal calls complete. Mean native |S-F| is 0.125 with permutation p=0.225268, below the unchanged 0.15 practical floor; six of eight tasks are zero, and the two nonzero cells have opposite signs. Every leave-one-task-out mean remains below 0.15. Reddit therefore strengthens cross-domain write divergence while preserving a bounded native-transport non-pass and showing that native magnitude is domain/task heterogeneous rather than universally equal to Shopping's 0.020833.\n\nB12 adds 80 observable provider POSTs, of which 72 are scientifically usable (8 fresh repaired writer calls and 64 terminal rollouts). The full-paper observable POST lower bound is at least 2,159. Qualification uses zero provider calls. The integrated supplement also retains the zero-call Shopping working-memory attribution (pair-relative shift 0.003347, p=0.2052) as post-hoc supporting localization only; it adds no provider calls and is not confirmatory mediation. Public CSV projections are included for retrieval qualification, writer execution, and terminal execution; private response IDs, raw outputs, credentials, and host paths are excluded. Run `python verify_current_supplement.py` to validate the projection.\n''',encoding='utf-8')
 verifier=r'''from pathlib import Path
import csv,json,sys
R=Path(__file__).resolve().parent;E=R/'evidence'
def L(n):return json.load(open(E/n))
q=L('manuscript-qa.json');b=L('b12-crossdomain-reddit-evidence.json');rec=L('stage-resolved-b12-revision-receipt.json');wm=L('working-memory-posthoc-evidence.json');qual=L('b12-qualification-public.json')['payload'];par=L('b12-parent-public.json')['payload'];r1=L('b12-r1-result-public.json')['payload'];p=json.load(open(R/'CURRENT-PROJECTION.json'))
counts={n:sum(1 for _ in csv.DictReader(open(E/n,encoding='utf-8'))) for n in ['b12-reddit-retrieval.csv','b12-r1-writer.csv','b12-r1-terminal.csv']}
checks=[q['status']=='PASS',q['revision']=='ICLR-STAGE-RESOLVED-B12-CROSSDOMAIN-20260824',sum(q['checks'].values())==len(q['checks'])==47,q['main_text_pages']==9,q['references_begin_page']==10,q['pdf_pages_total']==20,q['new_provider_calls_exact']==80,q['new_scientifically_usable_provider_calls']==72,q['updated_full_paper_observable_provider_posts_lower_bound']==2159,
b['status']=='B12_REDDIT_CROSSDOMAIN_REPLICATION_COMPLETE',b['qualification']['offline_eligible_retrieval_hits']==8,b['qualification']['eligible_intent_templates']==2,b['qualification']['distinct_selected_source_tasks']==4,b['writer_stage']['complete_pairs']==4,b['writer_stage']['exact_content_change_pairs']==4,b['writer_stage']['title_set_change_pairs']==4,abs(b['writer_stage']['mean_token_jaccard_distance']-.652342)<1e-12,b['terminal_stage']['scientific_calls']==64,abs(b['terminal_stage']['mean_absolute_success_rate_difference']-.125)<1e-12,abs(b['terminal_stage']['permutation_p']-.225268)<1e-12,b['terminal_stage']['gate_pass'] is False,b['terminal_stage']['zero_effect_tasks']==6,b['terminal_stage']['nonzero_effect_tasks']==2,b['terminal_stage']['all_leave_one_task_out_means_below_floor'] is True,b['terminal_stage']['leave_one_task_out_mean_range']==[.071429,.142857],
qual['status']=='B12_REDDIT_QUALIFIED_FOR_FROZEN_FOLLOWUP',qual['provider_calls']==0,qual['summary']['qualification_pass'] is True,par['status']=='B12_REDDIT_WRITER_PARTIAL',par['summary']['writer_calls_complete']==7,par['summary']['writer_failures']==1,par['summary']['terminal_calls_complete']==0,r1['status']=='B12_REDDIT_R1_EXECUTION_COMPLETE',r1['summary']['writer_calls_complete']==8,r1['summary']['writer_failures']==0,r1['summary']['terminal_calls_complete']==64,r1['summary']['terminal_failures']==0,abs(r1['summary']['observed_mean_absolute_success_rate_difference']-.125)<1e-12,r1['summary']['primary_gate_pass'] is False,
wm['status']=='B11_WORKING_MEMORY_LOCALIZATION_COMPLETE_STOP',wm['provider_calls']==0,abs(wm['branch_specific_uptake']['mean_pair_relative_shift']-.0033469072206773693)<1e-12,abs(wm['branch_specific_uptake']['posthoc_permutation_p']-.2051979480205198)<1e-12,rec['status']=='STAGE_RESOLVED_B12_INTEGRATED_QA_PASS',rec['story_winner_changed'] is False,rec['external_review_calls_current_revision']==0,rec['canonical_stable_registry_overwritten'] is False,p['revision']=='iclr-stage-resolved-b12-crossdomain-20260824',p['claim_expansion'] is False,p['story_winner_changed'] is False,p['reddit_native_gate_pass'] is False,p['working_memory_posthoc_provider_calls']==0,abs(p['working_memory_pair_relative_shift']-.0033469072206773693)<1e-12,p['full_paper_observable_provider_posts_lower_bound']==2159,p['canonical_stable_registry_overwritten'] is False,counts['b12-reddit-retrieval.csv']==129,counts['b12-r1-writer.csv']==8,counts['b12-r1-terminal.csv']==64]
print({'checks':len(checks),'passed':sum(checks),'pass':all(checks)});sys.exit(0 if all(checks) else 1)
'''
 (root/'verify_current_supplement.py').write_text(verifier,encoding='utf-8')
def main()->int:
 q=load(HERE/'manuscript-qa.json');
 if q.get('status')!='PASS' or q.get('revision')!='ICLR-STAGE-RESOLVED-B12-CROSSDOMAIN-20260824':raise RuntimeError('B12 QA not pass')
 DL.mkdir(parents=True,exist_ok=True);shutil.copy2(HERE/'paper.pdf',PDF)
 with tempfile.TemporaryDirectory(prefix='c1-b12-package-') as td:
  tmp=Path(td);src=tmp/'source';copy_source(src);zip_tree(src,SOURCE);ss=sha(SOURCE);ps=sha(PDF);supp=tmp/'supplement';build_supp(supp,ss,ps);hits=scan(supp)
  if hits:raise RuntimeError('supplement privacy scan failed: '+'; '.join(hits[:20]))
  zip_tree(supp,SUPP)
 print(json.dumps({'pdf':{'path':str(PDF),'sha256':sha(PDF)},'source_zip':{'path':str(SOURCE),'sha256':sha(SOURCE)},'supplement_zip':{'path':str(SUPP),'sha256':sha(SUPP)},'privacy_scan':'PASS'},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
