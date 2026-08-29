from __future__ import annotations

import hashlib, json, sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
B3 = Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b3-expanded-retrieval-exposure-20260824/b3-expanded-retrieval-exposure.json')
B4M = Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b4-retrieval-matched-fixed-evidence-20260824/b4-memory-manifest.json')
B10 = Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b10-native-first-action-transport-20260824/b10-contract.json')
FREEZE = HERE / 'c1-scmb-pilot-freeze-20260829.json'
CONTRACT = HERE / 'c1-scmb-pilot-contract-20260829.json'
PREFLIGHT = HERE / 'c1-scmb-data-preflight-20260829.json'
OLD36 = {26,124,126,142,143,144,147,149,150,164,165,167,190,192,227,228,229,230,233,279,280,281,282,319,320,321,322,323,329,330,331,333,358,360,362,384}
TEMPLATE_SALT='C1-SCMB-FRESH-TEMPLATE-v1'
PILOT_SALT='C1-SCMB-PILOT-v1'


def sha_bytes(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def sha_file(p:Path)->str:return sha_bytes(p.read_bytes())
def sha_text(s:str)->str:return sha_bytes(s.encode())
def load(p:Path):return json.loads(p.read_text(encoding='utf-8'))
def dump(p:Path,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def req(x,msg):
    if not x: raise RuntimeError(msg)


def main():
    b3=load(B3); b4=load(B4M); b10=load(B10)
    wrappers={(int(o['source_task']),str(o['condition'])):o for o in b4['objects']}
    rows=[]
    for r in b3['all_rows']:
        if not (r.get('is_shopping') and not r.get('is_source_task') and r.get('threshold_hit') and r.get('trajectory_available')): continue
        tid=int(r['task_id'])
        if tid in OLD36: continue
        x=dict(r); x['task_id']=tid; x['intent_template_id']=int(r['intent_template_id']); x['top1_source_task']=int(r['top1_source_task'])
        x['_template_hash']=sha_text(f"{TEMPLATE_SALT}|{x['intent_template_id']}|{tid}")
        rows.append(x)
    by=defaultdict(list)
    for r in rows: by[r['intent_template_id']].append(r)
    one=[min(v,key=lambda x:x['_template_hash']) for v in by.values()]
    for r in one:r['_pilot_hash']=sha_text(f"{PILOT_SALT}|{r['intent_template_id']}|{r['task_id']}")
    one=sorted(one,key=lambda x:x['_pilot_hash'])
    pilot,hold=one[:12],one[12:]
    req(len(pilot)==12 and len(hold)==19 and len(one)==31,'fresh template geometry drift')
    req(not ({x['task_id'] for x in one}&OLD36),'old36 leakage')
    # pyarrow from frozen B10 vendor path
    sys.path.insert(0,str(b10['vendor_path']))
    import pyarrow.parquet as pq
    par=Path(b10['source_bindings']['parquet']['path']); req(sha_file(par)==b10['source_bindings']['parquet']['sha256'],'parquet drift')
    table={int(r['task_id']):r for r in pq.read_table(par,columns=['task_id','task_prompt','trajectory_json']).to_pylist()}
    def materialize(r):
        tid=r['task_id']; src=r['top1_source_task']; raw=table[tid]
        tr=json.loads(str(raw['trajectory_json'])); step=(tr.get('steps') or {}).get('1'); req(step is not None,f'no step1:{tid}')
        contents=((step.get('input_messages') or {}).get('contents') or []); req(len(contents)>=2,f'bad inputs:{tid}')
        system=str(contents[0].get('content') or ''); last=str(contents[-1].get('content') or ''); marker='[Current state starts here]'; req(marker in last,f'no marker:{tid}')
        state=last.split(marker,1)[1].strip(); task=str(raw['task_prompt'])
        out={'future_task':tid,'intent_template_id':r['intent_template_id'],'selected_source_task':src,'retrieval_similarity':r['top1_similarity'],'retrieval_margin':r['top1_margin'],'evaluator_class':r['evaluator_class'],'selection_hash':r['_pilot_hash'],'task_prompt_sha256':sha_text(task),'system_instruction_sha256':sha_text(system),'current_state_sha256':sha_text(state)}
        for branch,cond in [('success','success'),('failure','failure')]:
            o=wrappers[(src,cond)]; p=Path(o['native_wrapper_path']); req(p.is_file() and sha_file(p)==o['native_wrapper_sha256'],f'wrapper drift {src}/{cond}')
            out[f'{branch}_memory_wrapper_path']=str(p); out[f'{branch}_memory_wrapper_sha256']=o['native_wrapper_sha256']
        return out
    p_rows=[materialize(r) for r in pilot]; h_rows=[materialize(r) for r in hold]
    contract={'schema_version':'1.0','artifact_kind':'C1_SCMB_PILOT_CONTRACT','paper_id':'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE','experiment_id':'C1-SCMB-P0-FRESH-UPTAKE-20260829','status':'FROZEN_DESIGN_AUTHORIZED_PILOT_ONLY','purpose':'Test whether a deliberately lightweight state-conditioned memory adapter yields a modest but memory-specific increase in first-action uptake on fresh states after a simple explicit-use reminder failed. This is proof-of-concept repair validation, not method novelty.','literature_boundary':{'not_novel_method':True,'nearest_work':['SAMem (Findings ACL 2026): state-aware memory','QCR (arXiv 2608.12847): target-bound reuse'],'claim_if_positive':'Stage-resolved diagnosis can select a mechanism-aligned repair family that produces a modest prospective uptake gain; state-conditioned adaptation itself is not claimed novel.'},'arms':{'A0_NATIVE':'raw retrieved memory only','A1_MEMORY_ONLY_ADAPTER':'binder rewrites the same retrieved memory into one concise procedural action note without seeing target task/state','A2_STATE_CONDITIONED_BINDING':'binder sees the same retrieved memory plus target task/current state and emits one concise current-state action implication'},'binder':{'model':'doubao-seed-2.0-mini','expected_resolved':'doubao-seed-2-0-mini-260215','temperature':0.0,'max_output_tokens':180,'thinking':'disabled','retries':0,'A1_instruction':'Convert the reusable memory into one concise procedural note for a browser agent. Do not use or infer any target task or target state. Preserve only reusable action guidance. Output one sentence, at most 60 words, with no explanation.','A2_instruction':'Given the reusable memory, the ultimate task, and the current browser state, produce one concise current-state action implication. Use the memory only when relevant, do not invent facts, and state what the agent should prioritize next. Output one sentence, at most 60 words, with no explanation.'},'policy':{'model':'doubao-seed-2.0-mini','expected_resolved':'doubao-seed-2-0-mini-260215','temperature':0.2,'max_output_tokens':900,'thinking':'disabled','retries':0,'rollouts_per_branch_per_arm_per_state':6},'primary':{'U':'empirical TV between success-memory and failure-memory first-action signature distributions within each state/arm','D':'U_A2 - U_A1','N':'U_A2 - U_A0','pilot_gate':['all 12 fresh states complete with packet/model/parser invariance','mean(D) >= 0.05','D>0 in at least 6/12 states','mean(N) > 0','mean(U_A2) > mean(U_A1) and mean(U_A0)'],'interpretation':'pilot signal only; no confirmatory p-value and no terminal utility claim'},'forbidden':['use any of prior 36 states','touch the prior sealed 23-state holdout','tune binder prompts after new outcomes','change threshold after execution','claim SCMB/SAMem/QCR-style state adaptation as novel','run terminal outcome or full confirmatory automatically'],'authority':{'pilot_binder_provider':True,'pilot_policy_provider':True,'confirmatory':False,'gpu':False,'submission':False}}
    freeze={'schema_version':'1.0','artifact_kind':'C1_SCMB_FRESH_PILOT_FREEZE','experiment_id':'C1-SCMB-P0-FRESH-UPTAKE-20260829','status':'FRESH_12_PILOT_19_TEMPLATE_HOLDOUT_FROZEN','source_pool':{'retrieval_hit_trajectory_available_excluding_old36':len(rows),'intent_templates':len(one),'old36_excluded':sorted(OLD36)},'selection':{'template_salt':TEMPLATE_SALT,'pilot_salt':PILOT_SALT,'rule':'Within each fresh intent template choose lexicographically smallest template hash, then choose 12 smallest pilot hashes across the 31 template representatives. No prior/new action or terminal outcome is used.','pilot':p_rows,'template_holdout':h_rows},'authority':contract['authority']}
    pre={'schema_version':'1.0','artifact_kind':'C1_SCMB_DATA_PREFLIGHT','status':'PASS_ZERO_PROVIDER_FRESH_PACKET_PREFLIGHT','checks':{'fresh_pool':len(rows),'template_representatives':len(one),'pilot_units':len(p_rows),'holdout_units':len(h_rows),'old36_overlap':len(({x['future_task'] for x in p_rows+h_rows}&OLD36)),'pilot_unique_templates':len({x['intent_template_id'] for x in p_rows}),'pilot_unique_sources':len({x['selected_source_task'] for x in p_rows}),'all_wrappers_hash_verified':True,'all_step1_states_materialized':True,'provider_calls':0},'source_bindings':{'b3_sha256':sha_file(B3),'b4_manifest_sha256':sha_file(B4M),'b10_contract_sha256':sha_file(B10),'parquet_sha256':sha_file(par)},'authority':contract['authority']}
    dump(CONTRACT,contract); dump(FREEZE,freeze); dump(PREFLIGHT,pre)
    print(json.dumps({'status':pre['status'],'fresh_pool':len(rows),'pilot':[x['future_task'] for x in p_rows],'holdout_n':len(h_rows),'pilot_unique_sources':pre['checks']['pilot_unique_sources'],'provider_calls':0}))

if __name__=='__main__':main()
