from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    value=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value,dict): raise ValueError(f"{path} must contain an object")
    return value

def load_jsonl(path: Path) -> list[dict[str,Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
def sha256(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def atomic_json(path:Path,value:Any)->None:
    path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');os.replace(tmp,path)
def append_jsonl(path:Path,value:Any)->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a',encoding='utf-8') as f:f.write(json.dumps(value,ensure_ascii=False,separators=(',',':'))+'\n')
def percentile(values:list[float],q:float)->float:
    if not values:return float('nan')
    xs=sorted(values);pos=(len(xs)-1)*q;lo=int(pos);hi=min(len(xs)-1,lo+1);frac=pos-lo
    return xs[lo]*(1-frac)+xs[hi]*frac


def validate_contract(contract:dict[str,Any])->dict[str,Any]:
    repo=Path(contract['execution_substrate']['author_repo']);model=Path(contract['execution_substrate']['model_path']);a=contract['author_asset'];checks={}
    commit=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip();checks['repo_commit']=commit==a['repo_commit']
    checks['evaluate_sha']=sha256(repo/'question_evaluate/evaluate.py')==a['evaluate_py_sha256']
    checks['grading_sha']=sha256(repo/'tool_call/grading.py')==a['grading_py_sha256']
    checks['prompts_sha']=sha256(repo/'tool_call/prompts.py')==a['prompts_py_sha256']
    checks['parsing_sha']=sha256(repo/'tool_call/parsing.py')==a['parsing_py_sha256']
    checks['contracts_sha']=sha256(repo/'tool_call/contracts.py')==a['contracts_py_sha256']
    for name,digest in contract['execution_substrate']['model_hashes'].items():checks[f'model_{name}_sha']=sha256(model/name)==digest
    checks['skill_mode_false']=contract['solver']['skill_mode'] is False
    checks['training_false']=contract['solver']['training'] is False
    checks['second_backbone_false']=contract['solver']['second_backbone'] is False
    checks['n3']=int(contract['solver']['samples_per_task'])==3
    return {'pass':all(checks.values()),'checks':checks,'commit':commit}


def preflight(contract:dict[str,Any],output_dir:Path)->dict[str,Any]:
    review=validate_contract(contract)
    if not review['pass']:raise RuntimeError(f"contract/hash preflight failed:{review}")
    repo=Path(contract['execution_substrate']['author_repo'])
    if str(repo) not in sys.path:sys.path.insert(0,str(repo))
    import torch,transformers,vllm
    from tool_call.grading import summarize_tool_call_predictions
    from tool_call.prompts import default_solver_system_prompt
    from tool_call.parsing import parse_task_sample
    from tool_call.contracts import check_task_sample_contract
    grading_probe=summarize_tool_call_predictions([], {})
    checks=dict(review['checks'])
    checks.update({
      'vllm_version':str(vllm.__version__)==str(contract['execution_substrate']['vllm_version']),
      'torch_version':str(torch.__version__)==str(contract['execution_substrate']['torch_version']),
      'transformers_version':str(transformers.__version__)==str(contract['execution_substrate']['transformers_version']),
      'grading_callable':callable(summarize_tool_call_predictions),
      'grading_summary_toolcallstats_shape':all(hasattr(grading_probe,name) for name in ('p_hat','consistency','valid_answer_count','total_samples')),
      'solver_prompt_callable':callable(default_solver_system_prompt),
      'parser_callable':callable(parse_task_sample),'contract_callable':callable(check_task_sample_contract),
    })
    out={'schema_version':'1.0','pass':all(checks.values()),'checks':checks,'gpu_work_started':False,'scientific_authority':False}
    atomic_json(output_dir/'preflight.json',out);return out


def validate_p0a_inputs(contract:dict[str,Any],p0a_result:dict[str,Any],raw_path:Path):
    errors=[]
    if p0a_result.get('decision')!='DYNAMIC_PARTIAL_OVERLAP_REPRESENTATION_SENSITIVITY_SUPPORTED':errors.append('p0a-not-go')
    if p0a_result.get('protocol_valid_for_scientific_update') is not True:errors.append('p0a-protocol-invalid')
    actual=sha256(raw_path)
    if actual!=str(p0a_result.get('raw_sha256') or ''):errors.append('raw-sha-mismatch')
    rows=load_jsonl(raw_path)
    if len(rows)!=72:errors.append(f'raw-count-{len(rows)}')
    return {'pass':not errors,'errors':errors,'raw_sha256':actual,'rows':rows}


def mixture_mean(source_means:dict[str,float],weights:dict[str,float])->float:
    return sum(float(weights[s])*source_means[s] for s in source_means)


def analyze(source_values:dict[str,list[float]],contract:dict[str,Any])->dict[str,Any]:
    means={s:sum(v)/len(v) for s,v in source_values.items()}
    cf=contract['counterfactual_reuse'];split=cf['split_weights'];merge_a=cf['merge_003_015_weights'];merge_b=cf['merge_004_015_weights']
    expected={'split':mixture_mean(means,split),'merge_003_015':mixture_mean(means,merge_a),'merge_004_015':mixture_mean(means,merge_b)}
    point={'merge_003_015':expected['merge_003_015']-expected['split'],'merge_004_015':expected['merge_004_015']-expected['split']}
    stats=contract['statistics'];rng=random.Random(int(stats['bootstrap_seed']));boot={k:[] for k in point}
    for _ in range(int(stats['bootstrap_replicates'])):
        bmeans={}
        for source,vals in source_values.items():
            sample=[vals[rng.randrange(len(vals))] for __ in range(len(vals))];bmeans[source]=sum(sample)/len(sample)
        bs=mixture_mean(bmeans,split)
        boot['merge_003_015'].append(mixture_mean(bmeans,merge_a)-bs);boot['merge_004_015'].append(mixture_mean(bmeans,merge_b)-bs)
    margin=float(stats['meaningful_effect_margin_absolute_p_hat']);witness={}
    for name,delta in point.items():
        lo,hi=percentile(boot[name],.025),percentile(boot[name],.975);passed=lo>margin or hi<(-margin)
        witness[name]={'delta_p_hat':delta,'bootstrap_lower95':lo,'bootstrap_upper95':hi,'absolute_margin':margin,'pass':passed}
    n=sum(int(v['pass']) for v in witness.values())
    decision='STRONG_ONE_STEP_SOLVER_CONSEQUENCE' if n==2 else 'PARTIAL_ONE_STEP_SOLVER_CONSEQUENCE' if n==1 else 'STOP_ONE_STEP_UTILITY_CONSEQUENCE'
    return {'decision':decision,'source_mean_p_hat':means,'expected_p_hat':expected,'witness_results':witness}


def solver_result_receipt(row:dict[str,Any],summary:Any)->dict[str,Any]:
    """Serialize the pinned author's ToolCallStats dataclass into replayable rows."""
    p_hat=float(summary.p_hat);total_samples=int(summary.total_samples)
    return {
        'source_skill_id':str(row['source_skill_id']),
        'source_index':int(row['source_index']),
        'p_hat':p_hat,
        'consistency':float(summary.consistency),
        'candidate_count':int(summary.valid_answer_count),
        'correct_count':int(round(p_hat*total_samples)),
    }


def run(contract:dict[str,Any],p0a_result_path:Path,raw_path:Path,output_dir:Path)->dict[str,Any]:
    pf=preflight(contract,output_dir)
    if not pf['pass']:raise RuntimeError('preflight failed')
    p0a=load_json(p0a_result_path);binding=validate_p0a_inputs(contract,p0a,raw_path)
    if not binding['pass']:
        out={'schema_version':'1.0','experiment_id':contract['experiment_id'],'candidate_id':contract['candidate_id'],'decision':'INVALID_P0C_INPUT_BINDING','scientific_result_available':False,'input_binding':{k:v for k,v in binding.items() if k!='rows'},'scientific_authority':False}
        atomic_json(output_dir/'result.json',out);return out
    repo=Path(contract['execution_substrate']['author_repo'])
    if str(repo) not in sys.path:sys.path.insert(0,str(repo))
    import vllm
    from transformers import AutoTokenizer
    from tool_call.grading import summarize_tool_call_predictions
    from tool_call.prompts import default_solver_system_prompt
    from tool_call.parsing import parse_task_sample
    from tool_call.contracts import check_task_sample_contract
    from utils.vllm_utils import llm_context_kwargs,trust_remote_code_enabled

    tokenizer=AutoTokenizer.from_pretrained(contract['execution_substrate']['model_path'],local_files_only=True,trust_remote_code=trust_remote_code_enabled())
    if tokenizer.pad_token is None:tokenizer.pad_token=tokenizer.eos_token
    valid=[];source_counts={s:0 for s in contract['units']['source_skill_ids']}
    for row in binding['rows']:
        try:sample=parse_task_sample(str(row.get('raw_text') or ''))
        except Exception:continue
        if sample is None:continue
        c=check_task_sample_contract(sample)
        if float(c.get('contract_valid',0.0))<1.0:continue
        source=str(row.get('source_skill_id') or '')
        if source not in source_counts:continue
        source_counts[source]+=1;valid.append((row,sample))
    min_valid=min(source_counts.values())
    if min_valid<16:
        out={'schema_version':'1.0','experiment_id':contract['experiment_id'],'candidate_id':contract['candidate_id'],'decision':'INVALID_P0C_REPARSE_QUALIFICATION_FAILED','scientific_result_available':False,'source_valid_counts':source_counts,'scientific_authority':False};atomic_json(output_dir/'result.json',out);return out

    prompts=[]
    for _,sample in valid:
        system_prompt=str(sample.get('system') or default_solver_system_prompt());user=str(sample.get('user') or '')
        prompts.append(tokenizer.apply_chat_template([{'role':'system','content':system_prompt},{'role':'user','content':user}],tokenize=False,add_generation_prompt=True,add_special_tokens=True))
    started=time.monotonic();model=vllm.LLM(model=contract['solver']['model_path'],tokenizer=contract['solver']['model_path'],seed=int(contract['solver']['seed']),trust_remote_code=trust_remote_code_enabled(),**llm_context_kwargs(require_enable_env=True))
    params=vllm.SamplingParams(max_tokens=int(contract['solver']['max_tokens']),temperature=float(contract['solver']['temperature']),top_p=float(contract['solver']['top_p']),top_k=int(contract['solver']['top_k']),n=int(contract['solver']['samples_per_task']),stop_token_ids=[tokenizer.eos_token_id])
    completions=model.generate(prompts,sampling_params=params);gpu_hours=(time.monotonic()-started)/3600.0
    raw_solver=output_dir/'solver-results.jsonl';raw_solver.unlink(missing_ok=True);source_values={s:[] for s in source_counts}
    for (row,sample),completion in zip(valid,completions,strict=True):
        predictions=[str(o.text) for o in completion.outputs];summary=summarize_tool_call_predictions(predictions,sample.get('answer'))
        receipt=solver_result_receipt(row,summary);source=str(receipt['source_skill_id']);source_values[source].append(float(receipt['p_hat']))
        append_jsonl(raw_solver,receipt)
    if gpu_hours>float(contract['budget']['gpu_hours_cap']):
        out={'schema_version':'1.0','experiment_id':contract['experiment_id'],'candidate_id':contract['candidate_id'],'decision':'INVALID_P0C_BUDGET_EXCEEDED','scientific_result_available':False,'gpu_hours':gpu_hours,'source_valid_counts':source_counts,'scientific_authority':False};atomic_json(output_dir/'result.json',out);return out
    analysis=analyze(source_values,contract);out={'schema_version':'1.0','experiment_id':contract['experiment_id'],'candidate_id':contract['candidate_id'],**analysis,'scientific_result_available':True,'protocol_valid_for_scientific_update':True,'source_valid_counts':source_counts,'evaluated_tasks':len(valid),'solver_sequences':len(valid)*int(contract['solver']['samples_per_task']),'gpu_hours':gpu_hours,'p0a_raw_sha256':binding['raw_sha256'],'solver_result_sha256':sha256(raw_solver),'new_questioner_generations':0,'training_steps':0,'second_backbone':0,'paper_claim_C4_end_of_evolution':False,'scientific_authority':False};atomic_json(output_dir/'result.json',out);return out


def main()->None:
    ap=argparse.ArgumentParser();ap.add_argument('--contract',type=Path,required=True);ap.add_argument('--p0a-result',type=Path);ap.add_argument('--raw',type=Path);ap.add_argument('--output-dir',type=Path,required=True);ap.add_argument('--preflight-only',action='store_true');a=ap.parse_args();contract=load_json(a.contract)
    if a.preflight_only:print(json.dumps({'preflight':preflight(contract,a.output_dir)['pass']}));return
    if not a.p0a_result or not a.raw:raise SystemExit('--p0a-result and --raw are required')
    out=run(contract,a.p0a_result,a.raw,a.output_dir);print(json.dumps({'decision':out['decision'],'gpu_hours':out.get('gpu_hours'),'witness_results':out.get('witness_results')},ensure_ascii=False))
if __name__=='__main__':main()
