#!/usr/bin/env python3
"""Create the R30 no-interim checkpoint and bind all consumed pre-exposure retries."""
from __future__ import annotations
import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path

EPISODES_EXPECTED=140; AGENT_BUDGET=4200; EVAL_BUDGET=600
PAPER_ID="D2-PAPER-FAILURE-MEMORY-PROVENANCE"
RECEIPT_ID="D2-FAILURE-MEMORY-PROVENANCE-L2B-R19-PARTIAL-CHECKPOINT-R30"
SEQ26_FAILURE_SHA="6db0e08ef26006c07f18811833c613832df6196fc647e2e3fe807a6d08d33f2f"
R29_SHA="b59ce863db0af091fe2e914a2edffd3ef6dc1d32fc4a6bca8bf06529f40c0810"

def sha(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def now()->str: return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def read_jsonl(p:Path)->list[dict]: return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()] if p.exists() else []

def build(run_root:Path)->dict:
    attempts=read_jsonl(run_root/'attempts.jsonl'); progress=read_jsonl(run_root/'progress.jsonl')
    if len(attempts)!=len(progress): raise RuntimeError('checkpoint requires no in-flight STARTED episode')
    if [int(x['sequence_index']) for x in progress] != list(range(len(progress))): raise RuntimeError('progress is not an exact schedule prefix')
    if (run_root/'failure.json').exists(): raise RuntimeError('post-exposure failure exists; checkpoint not allowed')
    if len(progress)%4: raise RuntimeError('checkpoint must be at a complete four-episode task boundary')
    groups={}
    for row in progress: groups.setdefault(str(row['task_id']),[]).append(row)
    for tid,rows in groups.items():
        if len(rows)!=4: raise RuntimeError(f'incomplete task boundary: {tid}')
        if sorted((x['arm'],int(x['repeat_id'])) for x in rows) != [('STATUS_F',0),('STATUS_F',1),('STATUS_S',0),('STATUS_S',1)]: raise RuntimeError(f'arm/repeat coverage drift: {tid}')
    agent=sum(int(x.get('agent_completion_count') or 0) for x in progress); evaluator=sum(int(x.get('fuzzy_evaluator_completion_count') or 0) for x in progress)
    if agent>AGENT_BUDGET or evaluator>EVAL_BUDGET: raise RuntimeError('budget exceeded')
    seq0_fail=run_root/'pre-exposure-support-failures'/'seq000-attempt1.json'
    seq0_retry=Path('generated/d2-failure-memory-provenance-l2b-r19-seq000-preexposure-retry-r22.json')
    seq26_fail=run_root/'pre-exposure-support-failures'/'seq026-attempt1.json'
    seq26_retry=Path('generated/d2-failure-memory-provenance-l2b-r19-seq026-preexposure-retry-r29.json')
    if sha(seq26_fail)!=SEQ26_FAILURE_SHA or sha(seq26_retry)!=R29_SHA: raise RuntimeError('seq26 retry chain SHA drift')
    return {
      'schema_version':'1.0','paper_id':PAPER_ID,'receipt_id':RECEIPT_ID,'recorded_at':now(),
      'status':'R19_CONFIRMATORY_PREFIX_CHECKPOINT_NO_INTERIM_INFERENCE',
      'execution':{'episodes_expected':EPISODES_EXPECTED,'episodes_complete':len(progress),'complete_independent_tasks':len(groups),'next_sequence_index':len(progress),'agent_completions':agent,'agent_completion_budget':AGENT_BUDGET,'fuzzy_evaluator_completions':evaluator,'fuzzy_evaluator_completion_budget':EVAL_BUDGET,'post_started_failure':False,'in_flight_episode':False},
      'integrity':{'attempts_jsonl_sha256':sha(run_root/'attempts.jsonl'),'progress_jsonl_sha256':sha(run_root/'progress.jsonl'),'run_contract_sha256':sha(run_root/'run-contract.json'),'summary_sha256':sha(run_root/'summary.json'),'seq000_preexposure_failure_sha256':sha(seq0_fail) if seq0_fail.exists() else None,'seq000_retry_adjudication_sha256':sha(seq0_retry) if seq0_retry.exists() else None,'seq026_preexposure_failure_sha256':SEQ26_FAILURE_SHA,'seq026_retry_adjudication_sha256':R29_SHA},
      'retry_state':{'sequence26_exact_retry_consumed':True,'sequence26_additional_retry_permitted':False},
      'interim_policy':{'terminal_scores_in_public_checkpoint':False,'task_deltas_computed':False,'effect_mean_computed':False,'p_value_computed':False,'confidence_interval_computed':False,'outcome_adaptive_stop_or_extension':False,'next_execution_must_resume_exact_frozen_sequence':len(progress),'claim_update_allowed':False},
      'scientific_verdict':'NO_VERDICT_INCOMPLETE_CONFIRMATORY_EXECUTION','scientific_claim_authority':False}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--run-root',type=Path,required=True); ap.add_argument('--output',type=Path,default=Path('generated/d2-failure-memory-provenance-l2b-r19-partial-checkpoint-r30.json')); a=ap.parse_args(); out=build(a.run_root); a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps({'status':out['status'],**out['execution'],'interim_inference':False},ensure_ascii=False))
if __name__=='__main__': main()
