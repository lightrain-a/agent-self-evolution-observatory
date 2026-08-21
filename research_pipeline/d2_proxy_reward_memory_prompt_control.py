from __future__ import annotations
import argparse, fcntl, itertools, json
from pathlib import Path
from statistics import mean
from typing import Any
from .ark_provider import ArkResponsesClient, ArkSettings
from .d2_proxy_reward_memory_f0 import _action_summary, _import_pyarrow, _jaccard_distance, _normalize_text, _prompt, _titles
from .d2_proxy_reward_memory_f1 import _cached_call
from .discovery_engine_terminal_replication import _jsha, _write_json

def _sign_flip_p(deltas:list[float])->float:
    observed=mean(deltas); vals=[]
    for signs in itertools.product((-1.0,1.0),repeat=len(deltas)):
        vals.append(mean([s*d for s,d in zip(signs,deltas)]))
    return sum(v>=observed-1e-12 for v in vals)/len(vals)

def run(contract:dict[str,Any],*,private_root:Path,output:Path)->dict[str,Any]:
    if contract.get('status')!='FROZEN_BEFORE_PROVIDER_CALLS': raise ValueError('control-contract-not-frozen')
    if not (contract.get('prompt_control_qualification') or {}).get('qualified'): raise ValueError('control-prompt-qualification-failed')
    source=contract['source']; pq=_import_pyarrow(Path('generated/research-data/paper-yield-d5-c01/vendor'))
    table=pq.read_table(Path(source['trajectory_parquet']),columns=['task_id','task_prompt','is_successful','trajectory_json']).to_pylist()
    by_id={str(r['task_id']):r for r in table}; task_ids=[str(x) for x in contract['fresh_sample']['task_ids']]
    if any(t in set(contract['fresh_sample']['excluded_original_f0_task_ids']) for t in task_ids): raise ValueError('original-f0-task-leaked-into-fresh-control')
    prompts={
        'success_original':Path(source['released_success_prompt']).read_text(),
        'success_paraphrase':Path(source['success_paraphrase']).read_text(),
        'failure_original':Path(source['released_failure_prompt']).read_text(),
        'failure_paraphrase':Path(source['failure_paraphrase']).read_text(),
    }
    model=contract['model']; base=ArkSettings.from_env(); client=ArkResponsesClient(ArkSettings(api_key=base.api_key,base_url=base.base_url,default_model=base.default_model,timeout_seconds=180,max_retries=0))
    def responder(**kw:Any)->dict[str,Any]:
        return client.respond(kw['prompt'],model=kw['model'],max_output_tokens=kw['max_output_tokens'],temperature=kw['temperature'],thinking=model['thinking'],store=True,allow_thinking_compatibility_fallback=bool(model['allow_thinking_compatibility_fallback']))
    rows=[]; receipts=[]; failures=[]
    for tid in task_ids:
        row=by_id[tid]; summary=_action_summary(row['trajectory_json'])
        if not summary.strip(): raise ValueError('fresh-control-action-summary-empty:'+tid)
        memories={}
        for condition in contract['conditions']:
            text_prompt=_prompt(prompts[condition],row['task_prompt'],summary)
            result,receipt=_cached_call(responder=responder,root=private_root,experiment_id=contract['experiment_id'],stage='memory-'+condition,engine_id='task-'+tid,prompt=text_prompt,model=model['requested'],tokens=int(model['max_output_tokens']),temp=float(model['temperature']),thinking=model['thinking'])
            receipts.append(receipt)
            if result is None:
                memories[condition]=''; failures.append({'task_id':tid,'condition':condition,**receipt})
            else: memories[condition]=str(result.get('text') or '')
        complete=all(memories[c].strip() for c in contract['conditions'])
        if complete:
            b=_jaccard_distance(memories['success_original'],memories['failure_original'])
            ws=_jaccard_distance(memories['success_original'],memories['success_paraphrase'])
            wf=_jaccard_distance(memories['failure_original'],memories['failure_paraphrase'])
            bv=_jaccard_distance(memories['success_paraphrase'],memories['failure_paraphrase'])
            w=(ws+wf)/2; delta=b-w
        else: b=ws=wf=bv=w=delta=None
        rows.append({'task_id':tid,'task_prompt':row['task_prompt'],'original_is_successful':bool(row['is_successful']),'complete':complete,'between_original_distance':round(b,6) if b is not None else None,'within_success_distance':round(ws,6) if ws is not None else None,'within_failure_distance':round(wf,6) if wf is not None else None,'within_mean_distance':round(w,6) if w is not None else None,'between_paraphrase_distance':round(bv,6) if bv is not None else None,'delta_between_minus_within':round(delta,6) if delta is not None else None,'title_sets':{c:_titles(memories[c]) for c in contract['conditions']},'exact_content_sha':{c:_jsha(_normalize_text(memories[c])) if memories[c] else '' for c in contract['conditions']},'scientific_authority':False})
    complete=[r for r in rows if r['complete']]; deltas=[float(r['delta_between_minus_within']) for r in complete]
    mean_b=mean([float(r['between_original_distance']) for r in complete]) if complete else None
    mean_w=mean([float(r['within_mean_distance']) for r in complete]) if complete else None
    mean_delta=mean(deltas) if deltas else None; pval=_sign_flip_p(deltas) if len(deltas)==len(task_ids) else None
    qualified=bool(contract['prompt_control_qualification']['qualified']); gate=qualified and len(complete)==len(task_ids) and mean_delta is not None and mean_delta>=0.10 and pval is not None and pval<0.05
    out={'schema_version':'1.0','experiment_id':contract['experiment_id'],'status':'PROMPT_CONTROL_COMPLETE' if len(complete)==len(task_ids) else 'PROMPT_CONTROL_SUPPORT_INCOMPLETE','contract_sha256':_jsha(contract),'hypothesis':contract['hypothesis'],'prompt_control_qualification':contract['prompt_control_qualification'],'summary':{'tasks_requested':len(task_ids),'tasks_complete':len(complete),'provider_failures':len(failures),'mean_between_original_distance':round(mean_b,6) if mean_b is not None else None,'mean_within_mode_distance':round(mean_w,6) if mean_w is not None else None,'mean_delta_between_minus_within':round(mean_delta,6) if mean_delta is not None else None,'exact_one_sided_sign_flip_p':round(pval,6) if pval is not None else None,'frozen_effect_margin':0.10,'frozen_alpha':0.05,'gate_pass':gate},'decision':'SUPPORT_REWARD_MODE_BEYOND_GENERIC_PROMPT_WORDING' if gate else ('INCONCLUSIVE_NO_NEGATIVE_AUTHORITY' if len(complete)==len(task_ids) else 'SUPPORT_INCOMPLETE_NO_SCIENTIFIC_AUTHORITY'),'rows':rows,'provider_receipts':receipts,'failures':failures,'scientific_authority':False,'experiment_authority':False}
    _write_json(output,out);return out

def main()->None:
    ap=argparse.ArgumentParser();ap.add_argument('--contract',type=Path,default=Path('generated/d2-proxy-reward-memory-f0c-prompt-control-contract.json'));ap.add_argument('--output',type=Path,default=Path('generated/d2-proxy-reward-memory-f0c-prompt-control.json'));ap.add_argument('--private-root',type=Path,default=Path('generated/research-data/d2-proxy-reward-memory-f0c-prompt-control'));a=ap.parse_args();c=json.loads(a.contract.read_text());a.private_root.mkdir(parents=True,exist_ok=True);lock=(a.private_root/'transaction.lock').open('a+');
    try: fcntl.flock(lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError: print(json.dumps({'status':'TRANSACTION_ALREADY_RUNNING','experiment_id':c['experiment_id']}));return
    if a.output.exists():
        old=json.loads(a.output.read_text())
        if old.get('status')=='PROMPT_CONTROL_COMPLETE' and old.get('contract_sha256')==_jsha(c): print(json.dumps({'status':'REPLAY_COMPLETED_PUBLIC_STATE','summary':old.get('summary'),'decision':old.get('decision')},indent=2));return
    r=run(c,private_root=a.private_root,output=a.output);print(json.dumps({'status':r['status'],'summary':r['summary'],'decision':r['decision']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
