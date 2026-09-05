#!/usr/bin/env python3
from __future__ import annotations
import json, hashlib, sys
from pathlib import Path
from typing import Any
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

ROOT=Path('/data/wyt/b1-memrl-r77-mechanism')
STATES=ROOT/'R77_M2_FROZEN_PROBE_STATES.json'
MODEL_IDENTITY=Path('/data/wyt/b1-memrl-r59-overlay-44960f8c/generated/d2-failure-memory-provenance-r59-llama-model-identity.json')
MODEL_ROOT=Path('/data/lry/models/Meta-Llama-3.1-8B-Instruct')
PINNED_SOURCE=Path('/data/wyt/b1-r77-clean-memrl')
LLB=PINNED_SOURCE/'3rdparty'/'LifelongAgentBench'
EXPECTED_MODEL_MANIFEST='8071d53a4509c0404328b791800ba79657556490b276b8383e1e8b2f0f63e104'
EXPECTED_MODEL_IDENTITY_RECEIPT='60811d80b379c1beabc7e48287bc4e1380801df0aea00a25ce2a1b934072a5c1'
EXPECTED_SOURCE_COMMIT='c1b322ca43de36ddf64c6712f89d0095bfc35ce0'

def sha_bytes(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def sha_file(p:Path)->str:return sha_bytes(p.read_bytes())
def digest(v:Any)->str:return sha_bytes(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
def valid_receipt(v:dict[str,Any])->bool:
    r=v.get('receipt_sha256');return isinstance(r,str) and r==digest({k:x for k,x in v.items() if k!='receipt_sha256'})
def norm_action(x):
    if not x:return None
    ls=[z.strip() for z in str(x).replace('\r\n','\n').splitlines() if z.strip() and not z.strip().startswith('#')]
    return '\n'.join(ls) or None
def convert_history(hist):
    out=[]
    for x in hist:
        role='assistant' if x['role']=='agent' else x['role']
        if role not in {'user','assistant'}:raise RuntimeError(f'bad-role:{role}')
        out.append({'role':role,'content':str(x['content'])})
    return out
def exact_base(tok,messages):
    text=tok.apply_chat_template(messages,tokenize=False,add_generation_prompt=True)
    enc=tok(text,return_tensors='pt')
    return enc['input_ids'].to('cuda:0'),enc['attention_mask'].to('cuda:0'),text
def common_prefix(a,b):
    n=0
    for x,y in zip(a,b):
        if x!=y:break
        n+=1
    return n
def score_tokens(model,base,base_mask,ids):
    if not ids:return {'token_count':0,'total_logprob':float('-inf'),'mean_logprob':float('-inf')}
    t=torch.tensor([ids],device=base.device,dtype=base.dtype);x=torch.cat([base,t],dim=1)
    mask=torch.cat([base_mask,torch.ones_like(t,dtype=base_mask.dtype)],dim=1)
    with torch.inference_mode():logits=model(input_ids=x,attention_mask=mask).logits
    p=logits[:,base.shape[1]-1:base.shape[1]-1+len(ids),:]
    lp=torch.log_softmax(p.float(),dim=-1).gather(-1,t.unsqueeze(-1)).squeeze(-1)
    return {'token_count':len(ids),'total_logprob':float(lp.sum()),'mean_logprob':float(lp.mean())}
def js(x,y):
    px=torch.softmax(x.float(),-1);py=torch.softmax(y.float(),-1);m=(px+py)/2;eps=1e-30
    return float((.5*(px*(torch.log(px+eps)-torch.log(m+eps))).sum()+.5*(py*(torch.log(py+eps)-torch.log(m+eps))).sum()).item())
def topk(logits,tok,k=8):
    lp=torch.log_softmax(logits.float(),-1);v,i=torch.topk(lp,k)
    return [{'token_id':int(ii),'token':tok.decode([int(ii)]),'logprob':float(vv)} for vv,ii in zip(v.tolist(),i.tolist())]

def main():
    states=json.loads(STATES.read_text());identity=json.loads(MODEL_IDENTITY.read_text())
    if not valid_receipt(states):raise RuntimeError('states-invalid')
    if not valid_receipt(identity) or identity['receipt_sha256']!=EXPECTED_MODEL_IDENTITY_RECEIPT or identity['manifest_sha256']!=EXPECTED_MODEL_MANIFEST:raise RuntimeError('model-identity-invalid')
    import subprocess
    head=subprocess.check_output(['git','-C',str(PINNED_SOURCE),'rev-parse','HEAD'],text=True).strip();dirty=subprocess.check_output(['git','-C',str(PINNED_SOURCE),'status','--porcelain'],text=True).strip()
    if head!=EXPECTED_SOURCE_COMMIT or dirty:raise RuntimeError('pinned-source-not-clean')
    for p in [PINNED_SOURCE,LLB]:
        if str(p) not in sys.path:sys.path.insert(0,str(p))
    from src.tasks.instance.os_interaction.task import OSInteraction
    from src.tasks.task import AgentAction

    tok=AutoTokenizer.from_pretrained(str(MODEL_ROOT),local_files_only=True,trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(str(MODEL_ROOT),local_files_only=True,trust_remote_code=False,torch_dtype=torch.float16,low_cpu_mem_usage=True).to('cuda:0');model.eval()

    # Phase A: exact-runtime greedy open-loop replay for the two historical natural branches.
    replay={};replay_rows=[]
    for task in states['tasks']:
        tid=str(task['task_id']);anchors={a['name']:a for a in task['anchors']}
        for arm in ['A','B']:
            aname='common' if 'common' in anchors else f'{arm}_history';anchor=anchors[aname]
            messages=[{'role':'system','content':task['system_prompts'][arm]}]+convert_history(anchor['chat_messages'])
            base,base_mask,rendered=exact_base(tok,messages)
            with torch.inference_mode():
                generated=model.generate(input_ids=base,attention_mask=base_mask,max_new_tokens=512,do_sample=False,pad_token_id=tok.eos_token_id,eos_token_id=tok.eos_token_id)
            new_ids=[int(x) for x in generated[0,base.shape[1]:].tolist()]
            text=tok.decode(new_ids,skip_special_tokens=True).strip()
            parsed=OSInteraction._parse_agent_response(text);content=parsed.content if parsed.action==AgentAction.EXECUTE else None;normalized=norm_action(content)
            expected=task['natural_normalized_actions'][arm]
            action_match=(normalized==expected)
            row={'task_id':tid,'arm':arm,'anchor':aname,'base_prompt_tokens':int(base.shape[1]),'rendered_prompt_sha256':sha_bytes(rendered.encode()),'generated_token_ids':new_ids,'generated_text':text,'generated_text_sha256':sha_bytes(text.encode()),'parsed_action':str(parsed.action),'normalized_action':normalized,'historical_normalized_action':expected,'normalized_action_matches_historical':action_match}
            replay[(tid,arm)]=row;replay_rows.append(row)
    failures=[{'task_id':r['task_id'],'arm':r['arm'],'observed':r['normalized_action'],'expected':r['historical_normalized_action']} for r in replay_rows if not r['normalized_action_matches_historical']]
    replay_receipt={'schema_version':'1.0','paper_id':'D2-PAPER-FAILURE-MEMORY-PROVENANCE','receipt_id':'D2-FAILURE-MEMORY-PROVENANCE-R77-M2A-EXACT-GREEDY-REPLAY','status':'R77_M2A_EXACT_GREEDY_REPLAY_PASS' if not failures else 'R77_M2A_EXACT_GREEDY_REPLAY_FAIL','role':'OPEN_LOOP_REPLAY_FIDELITY_GATE_NO_ENVIRONMENT','bindings':{'probe_states_receipt_sha256':states['receipt_sha256'],'model_identity_receipt_sha256':identity['receipt_sha256'],'pinned_source_commit':head},'generation_calls':len(replay_rows),'environment_interactions':0,'temperature':0.0,'do_sample':False,'rows':replay_rows,'failures':failures,'changes_R72_R73_primary_inference':False}
    replay_receipt['receipt_sha256']=digest(replay_receipt);(ROOT/'R77_M2A_EXACT_GREEDY_REPLAY.json').write_text(json.dumps(replay_receipt,ensure_ascii=False,indent=2)+'\n')
    if failures:raise RuntimeError('R77_M2A_REPLAY_FIDELITY_FAIL:'+json.dumps(failures,ensure_ascii=False))

    # Phase B: use the native replay token IDs as branch candidates under each frozen same-state anchor.
    probe_rows=[]
    for task in states['tasks']:
        tid=str(task['task_id']);idsA=replay[(tid,'A')]['generated_token_ids'];idsB=replay[(tid,'B')]['generated_token_ids'];cp=common_prefix(idsA,idsB)
        if cp>=min(len(idsA),len(idsB)):raise RuntimeError(f'branch-not-distinct:{tid}')
        atok,btok=idsA[cp],idsB[cp]
        for anchor in task['anchors']:
            hist=convert_history(anchor['chat_messages']);cond={};lg={}
            for arm in ['A','B']:
                messages=[{'role':'system','content':task['system_prompts'][arm]}]+hist;base,base_mask,_=exact_base(tok,messages)
                sA=score_tokens(model,base,base_mask,idsA);sB=score_tokens(model,base,base_mask,idsB)
                prefix=torch.tensor([idsA[:cp]],device='cuda:0',dtype=base.dtype) if cp else torch.empty((1,0),device='cuda:0',dtype=base.dtype);bp=torch.cat([base,prefix],dim=1)
                bp_mask=torch.cat([base_mask,torch.ones_like(prefix,dtype=base_mask.dtype)],dim=1)
                with torch.inference_mode():z=model(input_ids=bp,attention_mask=bp_mask).logits[0,-1,:].float().cpu()
                lp=torch.log_softmax(z,-1);arg=int(torch.argmax(z))
                cond[arm]={'base_prompt_tokens':int(base.shape[1]),'score_A_replay':sA,'score_B_replay':sB,'mean_logprob_branch_preference_B_minus_A':float(sB['mean_logprob']-sA['mean_logprob']),'branchpoint_logprob_A_token':float(lp[atok]),'branchpoint_logprob_B_token':float(lp[btok]),'branchpoint_logodds_B_minus_A':float(lp[btok]-lp[atok]),'branchpoint_argmax_token_id':arg,'branchpoint_argmax_text':tok.decode([arg]),'branchpoint_top8':topk(z,tok)};lg[arm]=z
            checks={}
            if anchor['name'] in {'common','A_history'}:checks['A_natural_branch_token_is_argmax']=(cond['A']['branchpoint_argmax_token_id']==atok)
            if anchor['name'] in {'common','B_history'}:checks['B_natural_branch_token_is_argmax']=(cond['B']['branchpoint_argmax_token_id']==btok)
            probe_rows.append({'task_id':tid,'anchor':anchor['name'],'target_action_index':task['target_action_index'],'candidate_replay_token_counts':{'A':len(idsA),'B':len(idsB),'common_prefix':cp},'first_differing_native_replay_token':{'A_id':atok,'A_text':tok.decode([atok]),'B_id':btok,'B_text':tok.decode([btok])},'conditions':cond,'natural_greedy_consistency':checks,'branchpoint_JS_A_vs_B_prompt':js(lg['A'],lg['B']),'treatment_shift_branchpoint_logodds_toward_B':cond['B']['branchpoint_logodds_B_minus_A']-cond['A']['branchpoint_logodds_B_minus_A'],'treatment_shift_mean_replay_preference_toward_B':cond['B']['mean_logprob_branch_preference_B_minus_A']-cond['A']['mean_logprob_branch_preference_B_minus_A'],'prompt_swap_flips_A_vs_B_candidate_token_preference':cond['A']['branchpoint_logodds_B_minus_A']*cond['B']['branchpoint_logodds_B_minus_A']<0})
    consistency_fail=[{'task_id':r['task_id'],'anchor':r['anchor'],'check':k} for r in probe_rows for k,v in r['natural_greedy_consistency'].items() if v is not True]
    if consistency_fail:raise RuntimeError('native-token-greedy-consistency-fail:'+json.dumps(consistency_fail))
    summary=[]
    for tid in sorted({r['task_id'] for r in probe_rows},key=int):
        rr=[r for r in probe_rows if r['task_id']==tid]
        summary.append({'task_id':tid,'anchors':len(rr),'branchpoint_shift_values':[r['treatment_shift_branchpoint_logodds_toward_B'] for r in rr],'all_anchor_branchpoint_shifts_toward_B':all(r['treatment_shift_branchpoint_logodds_toward_B']>0 for r in rr),'candidate_preference_flip_count':sum(int(r['prompt_swap_flips_A_vs_B_candidate_token_preference']) for r in rr),'mean_replay_preference_shift_values':[r['treatment_shift_mean_replay_preference_toward_B'] for r in rr],'all_anchor_mean_replay_shifts_toward_B':all(r['treatment_shift_mean_replay_preference_toward_B']>0 for r in rr)})
    out={'schema_version':'1.0','paper_id':replay_receipt['paper_id'],'receipt_id':'D2-FAILURE-MEMORY-PROVENANCE-R77-M2B-EXACT-SAME-STATE-LOGIT-PROBE','status':'R77_M2B_EXACT_SAME_STATE_LOGIT_PROBE_COMPLETE','role':'POST_HOC_MECHANISM_DIAGNOSTIC_NOT_PRIMARY_INFERENCE','bindings':{'M2A_replay_receipt_sha256':replay_receipt['receipt_sha256'],'probe_states_receipt_sha256':states['receipt_sha256'],'model_identity_receipt_sha256':identity['receipt_sha256']},'execution':{'same_state_anchors':len(probe_rows),'forward_conditions':len(probe_rows)*2,'environment_interactions':0,'new_task_trajectories':0,'dtype':'float16'},'rows':probe_rows,'task_summary':summary,'interpretation_boundary':'Measures local prompt-conditioned probability shifts between faithfully replayed historical branch actions/responses at frozen transcript states. Does not estimate population effect or mediation of terminal outcome.','changes_R72_R73_primary_inference':False}
    out['receipt_sha256']=digest(out);(ROOT/'R77_M2B_EXACT_SAME_STATE_LOGIT_PROBE.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'M2A_status':replay_receipt['status'],'M2A_receipt':replay_receipt['receipt_sha256'],'M2B_status':out['status'],'M2B_receipt':out['receipt_sha256'],'task_summary':summary},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
