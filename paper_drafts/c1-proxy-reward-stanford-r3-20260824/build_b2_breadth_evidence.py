#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
F0=Path('/data/wyt/agent-self-evolution-observatory/paper-acceptance-artifacts/D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE/f0-write-channel.json')
SEL=HERE/'b2-source-expansion-selection.json'
PARENT=Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b2-source-expansion-20260824/b2-source-expansion-result.json')
R1=Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b2-source-expansion-r1-4096-20260824/b2-source-expansion-r1-result.json')
OUT=HERE/'b2-breadth-evidence.json'
EXPECTED={'f0':'f2e4f3424faf1e3a9ec7aba7958e538eac457e89308552ef7a9c3d69c6a914f9','selection':'8ee0eeee70adb35612b6bb8dcb04c70d8d5da75be324b93f7ce7bce3c193ebf1','parent':'fd59a0d61c40a28e1c59bcf1452fc66e6ef2fa4d05d5c9830f4c57d18ee9fff1','r1':'42d655b7c55d615356bf1ceb048ebc69ba1a403d2c8e10e33e89149298684d3b'}

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path):return json.loads(p.read_text())
def req(x,msg):
 if not x: raise RuntimeError(msg)

def main():
 for k,p in [('f0',F0),('selection',SEL),('parent',PARENT),('r1',R1)]: req(p.is_file() and sha(p)==EXPECTED[k],f'{k} SHA drift')
 f0,sel,parent,r1=map(load,[F0,SEL,PARENT,R1])
 req(f0['summary']['paired_trajectories_complete']==4,'original F0 drift')
 req(sel['summary']['selected']==16 and sel['summary']['original_failure']==8 and sel['summary']['original_success']==8,'selection drift')
 req(parent['summary']['provider_calls_attempted']==32 and parent['summary']['provider_calls_complete']==29 and parent['summary']['provider_failures']==3,'parent accounting drift')
 req({(x['task_id'],x['label'],(x.get('provider_receipt') or {}).get('incomplete_reason')) for x in parent['failures']}=={('118','failure','length'),('125','failure','length'),('232','failure','length')},'parent failure pattern drift')
 req(r1['status']=='B2_EXECUTION_COMPLETE' and r1['decision']=='SUPPORT_BROAD_WRITE_CHANNEL','R1 not complete/pass')
 s=r1['summary']; req(s['provider_calls_attempted']==32 and s['provider_calls_complete']==32 and s['provider_failures']==0 and s['complete_pairs']==16,'R1 accounting drift')
 req(s['complete_pairs_original_failure']==8 and s['complete_pairs_original_success']==8 and s['paired_exact_content_change_rate']==1.0 and s['paired_title_set_change_rate']==1.0 and s['breadth_gate_pass'] is True,'R1 breadth gate drift')
 pooled=(4*float(f0['summary']['mean_token_jaccard_distance'])+16*float(s['mean_token_jaccard_distance']))/20
 payload={'schema_version':'1.0','artifact_type':'c1-write-channel-breadth-evidence','paper_id':'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE','status':'B2_BROAD_WRITE_CHANNEL_SUPPORTED','source_bindings':{k:EXPECTED[k] for k in EXPECTED},'original_complete_pairs':4,'new_complete_pairs':16,'combined_complete_pairs':20,'new_source_balance':{'original_failure':8,'original_success':8},'new_distinct_intent_templates':sel['summary']['distinct_intent_templates'],'new_pair_results':r1['pairs'],'summary':{'combined_exact_content_changed_pairs':20,'combined_title_set_changed_pairs':20,'combined_exact_content_change_rate':1.0,'combined_title_set_change_rate':1.0,'original_mean_token_jaccard_distance':f0['summary']['mean_token_jaccard_distance'],'new_mean_token_jaccard_distance':s['mean_token_jaccard_distance'],'pooled_20_pair_mean_token_jaccard_distance':round(pooled,6)},'execution_accounting':{'parent_2200_provider_posts':32,'parent_2200_complete':29,'parent_2200_failure_branch_length_censoring':3,'r1_4096_provider_posts':32,'r1_4096_complete':32,'total_b2_provider_posts':64,'scientifically_usable_r1_provider_posts':32},'repair_interpretation':'The 2200-token parent is execution-censored in three failure-branch units and has zero breadth-gate authority. R1 changes only max_output_tokens 2200->4096 uniformly, regenerates all 32 units fresh, and is the sole scientifically usable B2 breadth replication.','claim_boundary':'Supports broader upstream write-time divergence on 20 complete paired sources total. It does not establish native retrieval transport, cross-policy downstream transfer, or a population effect.','new_provider_calls_after_r1_completion':0,'scientific_authority':False,'experiment_authority':True,'claim_expansion_authority':False}
 OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'status':payload['status'],'summary':payload['summary'],'execution_accounting':payload['execution_accounting']},indent=2))
if __name__=='__main__':main()
