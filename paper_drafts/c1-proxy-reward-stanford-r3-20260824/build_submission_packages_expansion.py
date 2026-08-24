#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,shutil,tempfile,zipfile
from pathlib import Path
from typing import Any

HERE=Path(__file__).resolve().parent;REPO=HERE.parents[1];SRC=HERE/'source';DOWNLOADS=REPO/'downloads'
ART=Path('/data/wyt/agent-self-evolution-observatory/paper-acceptance-artifacts/D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE')
B1=Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b1-exact-retrieval-exposure-20260824/b1-exact-retrieval-exposure.json')
B3=Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b3-expanded-retrieval-exposure-20260824/b3-expanded-retrieval-exposure.json')
B4=Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b4-retrieval-matched-fixed-evidence-20260824/b4-result.json')
B5=Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b5-no-memory-native-support-20260824/b5-result.json')
PDF_OUT=DOWNLOADS/'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE-stanford-r3-20260824.pdf';SOURCE_OUT=DOWNLOADS/'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE-stanford-r3-20260824-source.zip';SUPP_OUT=DOWNLOADS/'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE-stanford-r3-20260824-supplement.zip'
FORBIDDEN=['/home/','/data/','wyt@','222.20.','202.69.','10.42.','ARK_API_KEY','source_message_ref','resp_']
PRIVATE_FRAGS=('path','run_root','artifact_path','provider_env_file','source_message_ref','response_id')

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->Any:return json.loads(p.read_text(encoding='utf-8'))
def writej(p:Path,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def sanitize(v:Any)->Any:
 if isinstance(v,dict):
  out={}
  for k,x in v.items():
   lk=str(k).lower()
   if any(f in lk for f in PRIVATE_FRAGS) and not lk.endswith('sha256'):continue
   if lk=='api_key_in_output':continue
   out[k]=sanitize(x)
  return out
 if isinstance(v,list):return [sanitize(x) for x in v]
 if isinstance(v,str) and any(t in v for t in FORBIDDEN):return '<private-redacted>'
 return v
def public_projection(p:Path):return {'schema_version':'1.0','projection_type':'anonymous-public-projection','source_artifact_sha256':sha(p),'payload':sanitize(load(p))}
def copy_source(dst:Path):
 dst.mkdir(parents=True,exist_ok=True)
 for n in ['main.tex','references.bib','iclr2027_conference.bst','iclr2027_conference.sty','natbib.sty','fancyhdr.sty','build_figures.py']:shutil.copy2(SRC/n,dst/n)
 shutil.copytree(SRC/'figures',dst/'figures');shutil.copytree(SRC/'sections',dst/'sections')
def zip_tree(root:Path,out:Path):
 out.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted(root.rglob('*')):
   if p.is_file():z.write(p,p.relative_to(root.parent))
def privacy_scan(root:Path):
 hits=[]
 for p in root.rglob('*'):
  if not p.is_file() or p.suffix.lower() in {'.pdf','.png','.jpg','.jpeg','.zip'}:continue
  try:t=p.read_text(encoding='utf-8')
  except UnicodeDecodeError:continue
  for token in FORBIDDEN:
   if token in t:hits.append(f'{p.relative_to(root)}::{token}')
 return hits

def build_supp(tree:Path,source_sha:str,pdf_sha:str):
 E=tree/'evidence';E.mkdir(parents=True,exist_ok=True)
 frozen={'f0-write-channel.json':ART/'f0-write-channel.json','f0c-prompt-control.json':ART/'f0c-prompt-control.json','f1d-distributional-audit.json':ART/'f1d-distributional-audit.json','f2-initial-terminal.json':ART/'f2-initial-terminal.json','f2r1-confirmatory.json':ART/'f2r1-confirmatory.json','f2r1-derived-corruption-variance.json':ART/'f2r1-derived-corruption-variance.json','f2r1-heterogeneity-bootstrap.json':ART/'f2r1-heterogeneity-bootstrap.json'}
 for n,p in frozen.items():writej(E/n,sanitize(load(p)))
 for n,p in {'manuscript-qa.json':HERE/'manuscript-qa.json','baseline-aligned-expansion-evidence.json':HERE/'baseline-aligned-expansion-evidence.json','baseline-aligned-expansion-revision-receipt.json':HERE/'baseline-aligned-expansion-revision-receipt.json','b2-breadth-evidence.json':HERE/'b2-breadth-evidence.json','f2r1-chronology-receipt.json':HERE/'f2r1-chronology-receipt.json','o5-manuscript-evidence.json':HERE/'o5-manuscript-evidence.json','o6-final-evidence.json':HERE/'o6-final-evidence.json','o6-full-bank-corruption-reduction.json':HERE/'o6-full-bank-corruption-reduction.json'}.items():writej(E/n,sanitize(load(p)))
 for n,p in {'b1-original-bank-retrieval-public.json':B1,'b3-expanded-bank-retrieval-public.json':B3,'b4-native-branch-transport-public.json':B4,'b5-native-no-memory-public.json':B5}.items():writej(E/n,public_projection(p))
 q=load(HERE/'manuscript-qa.json');x=load(HERE/'baseline-aligned-expansion-evidence.json');rev=load(HERE/'baseline-aligned-expansion-revision-receipt.json')
 proj={'schema_version':'1.0','receipt_type':'supplement-current-projection','paper_id':'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE','revision':'iclr-baseline-aligned-experiment-expansion-20260824','title':rev['title'],'current_pdf_sha256':pdf_sha,'current_source_zip_sha256':source_sha,'new_experiment':True,'scientific_values_changed':True,'claim_expansion':False,'new_provider_calls_exact':q['new_provider_calls_exact'],'new_scientifically_usable_provider_calls':q['new_scientifically_usable_provider_calls'],'new_scientifically_usable_writer_calls':q['new_scientifically_usable_writer_calls'],'new_terminal_rollouts':q['new_terminal_rollouts'],'cross_policy_support_failure_posts':q['cross_policy_support_failure_posts'],'updated_full_paper_observable_provider_posts_lower_bound':q['updated_full_paper_observable_provider_posts_lower_bound'],'main_text_pages':q['main_text_pages'],'references_begin_page':q['references_begin_page'],'write_complete_pairs':x['experiments']['B2_write_breadth']['combined_complete_pairs'],'write_pooled_jaccard':x['experiments']['B2_write_breadth']['pooled_20_pair_mean_token_jaccard_distance'],'forced_swap_mean_abs_effect':0.15625,'forced_swap_p':0.00074,'original_bank_retrieval_hits':'8/188','expanded_bank_retrieval_hits':'125/172','native_transport_mean_abs_effect':x['experiments']['B4_native_retrieval_matched_branch_transport']['mean_absolute_success_rate_difference'],'native_transport_p':x['experiments']['B4_native_retrieval_matched_branch_transport']['permutation_p'],'native_transport_zero_cells':x['experiments']['B4_native_retrieval_matched_branch_transport']['zero_cells'],'native_presence_effect':x['experiments']['B5_native_support_no_memory']['mean_absolute_memory_presence_effect'],'native_presence_p':x['experiments']['B5_native_support_no_memory']['permutation_p'],'cross_policy_status':x['claim_boundary']['cross_policy_terminal_transfer_status'],'external_review_calls_current_revision':0,'canonical_stable_registry_overwritten':False,'scientific_authority':False,'experiment_authority':False,'submission_authority':False}
 writej(tree/'CURRENT-PROJECTION.json',proj)
 (tree/'README.md').write_text("""# Reward Errors Become Persistent State — baseline-aligned expansion supplement

This anonymous supplement binds the expanded evidence for **Reward Errors Become Persistent State: Write-Time Causality and Transport Boundaries in Agent Memory**.

The evidence is deliberately separated into three layers. (1) Write identification: the original four complete source pairs plus sixteen fresh outcome-balanced breadth pairs give 20/20 persistent-memory divergences. (2) Forced intervention sensitivity: the frozen 4x4 terminal swap remains a same-support replication after an initial non-pass and yields mean |delta|=0.15625, p=0.00074. (3) Realized transport: exact released all-MiniLM-L6-v2 top-1/.3 retrieval hits 8/188 held-out Shopping tasks with the original bank and 125/172 after expansion to twenty sources. On all 36 pre-outcome native-hit tasks with deterministic offline evaluators, the 288-call success/failure contrast is 0.02083 (p=0.4289); a 144-call no-memory arm gives presence effect 0.04514 (p=0.00147), below the unchanged 0.15 practical floor.

The DeepSeek-V4-Flash cross-policy line is a provider-support stop, not a scientific null: the first frozen unit returns no assistant text at both the 900-token parent and sole preregistered 2200-token repair, producing zero scientific units. The current expansion adds 498 observable provider POSTs, of which 464 are scientifically usable completions, and raises the full-paper observable lower bound to at least 1,339. No training or GPU fine-tuning is used.

Private provider response IDs, raw model text, host paths, credentials, and human-authorization files are excluded. Run `python verify_current_supplement.py` to validate the public numerical and claim-boundary contract.
""",encoding='utf-8')
 verifier=r'''from pathlib import Path
import json,sys
R=Path(__file__).resolve().parent;E=R/'evidence'
def L(n):return json.load(open(E/n))
q=L('manuscript-qa.json');x=L('baseline-aligned-expansion-evidence.json');rev=L('baseline-aligned-expansion-revision-receipt.json');f0=L('f0-write-channel.json');f2=L('f2r1-confirmatory.json');chron=L('f2r1-chronology-receipt.json');o5=L('o5-manuscript-evidence.json');o6=L('o6-final-evidence.json');red=L('o6-full-bank-corruption-reduction.json');b1=L('b1-original-bank-retrieval-public.json')['payload'];b3=L('b3-expanded-bank-retrieval-public.json')['payload'];b4=L('b4-native-branch-transport-public.json')['payload'];b5=L('b5-native-no-memory-public.json')['payload'];p=json.load(open(R/'CURRENT-PROJECTION.json'))
checks=[
 q['status']=='PASS',q['revision']=='ICLR-BASELINE-ALIGNED-EXPERIMENT-EXPANSION-20260824',sum(q['checks'].values())==len(q['checks'])==33,q['abstract_words_approx']==220,q['main_text_pages']==9,q['references_begin_page']==9,
 f0['summary']['paired_trajectories_complete']==4,abs(f2['summary']['observed_mean_absolute_success_rate_difference']-.15625)<1e-12,abs(f2['summary']['permutation_p_ge_observed']-.00074)<1e-12,
 chron['status']=='CHRONOLOGY_AND_UNIFORM_REPLICATION_VERIFIED',chron['relationship']['confirmatory_was_designed_after_initial_nonpass'] is True,chron['relationship']['same_4x4_support'] is True,chron['relationship']['effect_floor_changed'] is False,chron['relationship']['alpha_changed'] is False,
 x['status']=='BASELINE_ALIGNED_EXPANSION_COMPLETE_WITH_CROSS_POLICY_SUPPORT_STOP',x['experiments']['B2_write_breadth']['combined_complete_pairs']==20,x['experiments']['B2_write_breadth']['combined_exact_content_change_rate']==1.0,abs(x['experiments']['B2_write_breadth']['pooled_20_pair_mean_token_jaccard_distance']-.673014)<1e-12,
 b1['status']=='COMPLETE_ZERO_PROVIDER_CALLS',b1['summary']['shopping_threshold_hits']==8,b1['summary']['shopping_heldout_tasks']==188,b1['summary']['frozen_future_hits']==0,
 b3['status']=='COMPLETE_ZERO_PROVIDER_CALLS',b3['summary']['shopping_threshold_hits']==125,b3['summary']['shopping_heldout_tasks']==172,b3['summary']['offline_eligible_retrieval_matched_tasks']==36,
 b4['status']=='B4_EXECUTION_COMPLETE',b4['summary']['provider_calls_complete']==288,b4['summary']['provider_failures']==0,abs(b4['summary']['observed_mean_absolute_success_rate_difference']-.020833)<1e-12,abs(b4['summary']['permutation_p_ge_observed']-.428866)<1e-12,b4['summary']['breadth_gate_pass'] is False,b4['secondary']['zero_cells']==34,
 b5['status']=='B5_EXECUTION_COMPLETE',b5['summary']['provider_calls_complete']==144,b5['summary']['provider_failures']==0,abs(b5['summary']['observed_mean_absolute_memory_presence_effect']-.045139)<1e-12,abs(b5['summary']['omnibus_permutation_p_ge_observed']-.00147)<1e-12,b5['summary']['memory_presence_gate_pass'] is False,b5['summary']['geometry_counts']=={'CLOSER_TO_FAILURE':1,'CLOSER_TO_SUCCESS':1,'EQUIDISTANT':34},
 o5['status']=='O5_FRESH_NO_MEMORY_CONTROL_COMPLETE',o6['status']=='O6_CROSS_WRITER_BOUNDARY_COMPLETE',o6['terminal_stage']['joint_gate_pass'] is False,red['released_mechanism_facts']['default_top_k']==1,abs(red['released_mechanism_facts']['default_similarity_threshold']-.3)<1e-12,
 x['claim_boundary']['native_retrieval_matched_branch_transport_supported'] is False,x['claim_boundary']['native_memory_presence_practical_effect_supported'] is False,x['claim_boundary']['cross_policy_terminal_transfer_status']=='SUPPORT_STOP_ZERO_SCIENTIFIC_UNITS',
 x['execution_accounting']['new_provider_posts']==498,x['execution_accounting']['new_scientifically_usable_provider_completions']==464,x['execution_accounting']['new_scientifically_usable_terminal_rollouts']==432,x['execution_accounting']['updated_full_paper_observable_provider_posts_lower_bound']==1339,x['execution_accounting']['training_runs']==0,x['execution_accounting']['gpu_runs']==0,
 rev['status']=='BASELINE_ALIGNED_EXPERIMENT_EXPANSION_INTEGRATED',rev['new_provider_calls_exact']==498,rev['new_scientifically_usable_provider_calls']==464,rev['new_terminal_rollouts']==432,rev['external_review_calls']==0,rev['canonical_stable_registry_overwritten'] is False,
 p['revision']=='iclr-baseline-aligned-experiment-expansion-20260824',p['new_experiment'] is True,p['scientific_values_changed'] is True,p['claim_expansion'] is False,p['new_provider_calls_exact']==498,p['new_scientifically_usable_provider_calls']==464,p['new_terminal_rollouts']==432,p['updated_full_paper_observable_provider_posts_lower_bound']==1339,p['write_complete_pairs']==20,p['original_bank_retrieval_hits']=='8/188',p['expanded_bank_retrieval_hits']=='125/172',abs(p['native_transport_mean_abs_effect']-.020833)<1e-12,abs(p['native_presence_effect']-.045139)<1e-12,p['cross_policy_status']=='SUPPORT_STOP_ZERO_SCIENTIFIC_UNITS',p['external_review_calls_current_revision']==0,p['canonical_stable_registry_overwritten'] is False,
]
print({'checks':len(checks),'passed':sum(checks),'pass':all(checks)});sys.exit(0 if all(checks) else 1)
'''
 (tree/'verify_current_supplement.py').write_text(verifier,encoding='utf-8')

def main():
 DOWNLOADS.mkdir(parents=True,exist_ok=True);shutil.copy2(HERE/'paper.pdf',PDF_OUT)
 with tempfile.TemporaryDirectory(prefix='c1-expansion-package-') as td:
  tmp=Path(td);src=tmp/'source';copy_source(src);zip_tree(src,SOURCE_OUT);source_sha=sha(SOURCE_OUT);pdf_sha=sha(PDF_OUT);supp=tmp/'supplement';build_supp(supp,source_sha,pdf_sha);hits=privacy_scan(supp)
  if hits:raise RuntimeError('supplement privacy scan failed: '+'; '.join(hits[:20]))
  zip_tree(supp,SUPP_OUT)
 print(json.dumps({'pdf':{'path':str(PDF_OUT),'sha256':sha(PDF_OUT)},'source_zip':{'path':str(SOURCE_OUT),'sha256':sha(SOURCE_OUT)},'supplement_zip':{'path':str(SUPP_OUT),'sha256':sha(SUPP_OUT)}},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
