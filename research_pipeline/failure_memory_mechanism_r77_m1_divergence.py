#!/usr/bin/env python3
from __future__ import annotations
import json, hashlib
from pathlib import Path
from typing import Any

ROOT=Path('/data/wyt/b1-memrl-r59-llama-execution/ab-r61')
COMPLETED=ROOT/'completed-ab-arms.jsonl'
OUT=Path('/data/wyt/b1-memrl-r77-mechanism')
TASKS=['125','136','193','327']
ARMS=['A_content_only','B_raw_provenance']

def sha_bytes(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def sha_file(p:Path)->str:return sha_bytes(p.read_bytes())
def digest(v:Any)->str:return sha_bytes(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
def load_json(p:Path):return json.loads(p.read_text())
def normobs(s:str)->str:return '\n'.join(line.rstrip() for line in str(s).strip().splitlines())

def agent_msg_index(action_index:int)->int:return 3+2*action_index
def observation_after(trace:dict[str,Any],action_index:int)->str|None:
    i=4+2*action_index
    msgs=trace['chat_messages']
    if i>=len(msgs):return None
    m=msgs[i]
    return str(m.get('content')) if m.get('role')=='user' else None

def main():
    rows=[json.loads(x) for x in COMPLETED.read_text().splitlines() if x.strip()]
    ledger={(str(r['task_id']),str(r['arm'])):r for r in rows}
    audit=[];probe_states=[]
    for tid in TASKS:
        traces={a:load_json(Path(ledger[(tid,a)]['trace_file'])) for a in ARMS}
        A,B=traces[ARMS[0]],traces[ARMS[1]]
        n=min(len(A['actions']),len(B['actions']))
        first_response_div=None;first_action_div=None;common_action_prefix=0;common_external_prefix=0
        for i in range(n):
            aa,bb=A['actions'][i],B['actions'][i]
            if first_response_div is None and str(aa.get('response'))!=str(bb.get('response')):first_response_div=i
            same_action=(aa.get('parsed')==bb.get('parsed') and aa.get('normalized')==bb.get('normalized'))
            if first_action_div is None and not same_action:first_action_div=i
            if i==common_action_prefix and same_action:common_action_prefix+=1
            oa,ob=observation_after(A,i),observation_after(B,i)
            same_obs=(oa is not None and ob is not None and normobs(oa)==normobs(ob)) or (oa is None and ob is None)
            if i==common_external_prefix and same_action and same_obs:common_external_prefix+=1
        if first_action_div is None:
            first_action_div=n if len(A['actions'])!=len(B['actions']) else None
        if first_action_div is None:raise RuntimeError(f'no action divergence:{tid}')
        target=first_action_div
        msgidx=agent_msg_index(target)
        histA=A['chat_messages'][:msgidx];histB=B['chat_messages'][:msgidx]
        exact_anchor=(histA==histB)
        anchors=[('common',histA)] if exact_anchor else [('A_history',histA),('B_history',histB)]
        naturalA=A['actions'][target] if target<len(A['actions']) else {'response':'<NO_ACTION>','normalized':None,'parsed':'<NO_ACTION>'}
        naturalB=B['actions'][target] if target<len(B['actions']) else {'response':'<NO_ACTION>','normalized':None,'parsed':'<NO_ACTION>'}
        row={
            'task_id':tid,
            'historical_terminal':{'A':bool(A['terminal_success']),'B':bool(B['terminal_success'])},
            'action_counts':{'A':len(A['actions']),'B':len(B['actions'])},
            'first_full_assistant_response_divergence_action_index':first_response_div,
            'first_normalized_action_divergence_action_index':target,
            'common_normalized_action_prefix_count':common_action_prefix,
            'common_external_transition_prefix_count':common_external_prefix,
            'target_agent_chat_message_index':msgidx,
            'history_exactly_shared_at_target':exact_anchor,
            'anchor_names':[x[0] for x in anchors],
            'natural_target':{
                'A':{'parsed':naturalA.get('parsed'),'normalized':naturalA.get('normalized'),'response_sha256':sha_bytes(str(naturalA.get('response')).encode()),'response':naturalA.get('response')},
                'B':{'parsed':naturalB.get('parsed'),'normalized':naturalB.get('normalized'),'response_sha256':sha_bytes(str(naturalB.get('response')).encode()),'response':naturalB.get('response')},
            },
            'system_prompt_sha256':{'A':sha_bytes(A['full_system_prompt'].encode()),'B':sha_bytes(B['full_system_prompt'].encode())},
            'trace_file_sha256':{'A':sha_file(Path(ledger[(tid,ARMS[0])]['trace_file'])),'B':sha_file(Path(ledger[(tid,ARMS[1])]['trace_file']))},
        }
        audit.append(row)
        probe_states.append({
            'task_id':tid,
            'target_action_index':target,
            'history_exactly_shared_at_target':exact_anchor,
            'system_prompts':{'A':A['full_system_prompt'],'B':B['full_system_prompt']},
            'natural_responses':{'A':str(naturalA.get('response') or ''),'B':str(naturalB.get('response') or '')},
            'natural_normalized_actions':{'A':naturalA.get('normalized'),'B':naturalB.get('normalized')},
            'anchors':[{'name':name,'chat_messages':hist,'chat_history_sha256':digest(hist)} for name,hist in anchors],
        })
    receipt={
        'schema_version':'1.0','paper_id':'D2-PAPER-FAILURE-MEMORY-PROVENANCE',
        'receipt_id':'D2-FAILURE-MEMORY-PROVENANCE-R77-M1-DIVERGENCE-LOCALIZATION',
        'status':'R77_M1_DIVERGENCE_LOCALIZATION_COMPLETE_ZERO_MODEL',
        'role':'POST_HOC_MECHANISM_DIAGNOSTIC_NOT_PRIMARY_INFERENCE',
        'bindings':{'r61_completed_ledger_sha256':sha_file(COMPLETED)},
        'task_ids':TASKS,'rows':audit,
        'summary':{
            'task_125':'Five identical normalized actions and external transitions precede the first executable divergence; the target history is byte-identical across A/B.',
            'task_136':'The first assistant wording differs, but the first executable command and resulting OS observation are the same; executable divergence begins at action index 1, so two natural-history anchors are retained.',
            'task_193':'Executable divergence occurs immediately at the first response; the pre-response history is byte-identical.',
            'task_327':'An initial non-executable/empty parsed action and observation are shared; the first executable command then differs, so two natural-history anchors are retained.',
        },
        'new_model_trajectories':0,'changes_R72_R73_primary_inference':False,
    }
    receipt['receipt_sha256']=digest(receipt)
    states={'schema_version':'1.0','paper_id':receipt['paper_id'],'receipt_id':'D2-FAILURE-MEMORY-PROVENANCE-R77-M2-FROZEN-PROBE-STATES','status':'R77_M2_SAME_STATE_PROBE_STATES_FROZEN','source_m1_receipt_sha256':receipt['receipt_sha256'],'probe_count':sum(len(x['anchors']) for x in probe_states),'tasks':probe_states,'model_inference_authority':'logit_forward_only_no_generation_no_environment_execution','changes_R72_R73_primary_inference':False}
    states['receipt_sha256']=digest(states)
    (OUT/'R77_M1_DIVERGENCE_LOCALIZATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    (OUT/'R77_M2_FROZEN_PROBE_STATES.json').write_text(json.dumps(states,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':receipt['status'],'M1_receipt_sha256':receipt['receipt_sha256'],'probe_states':states['probe_count'],'M2_states_receipt_sha256':states['receipt_sha256'],'rows':[{k:r[k] for k in ['task_id','first_full_assistant_response_divergence_action_index','first_normalized_action_divergence_action_index','common_normalized_action_prefix_count','common_external_transition_prefix_count','history_exactly_shared_at_target','anchor_names']} for r in audit]},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
