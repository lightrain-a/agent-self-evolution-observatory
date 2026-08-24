#!/usr/bin/env python3
"""Build a public-safe no-interim-inference status projection for authorized R19."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path


def sha(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()

def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--authority-receipt',type=Path,required=True)
    ap.add_argument('--support-receipt',type=Path,required=True)
    ap.add_argument('--synthetic-smokes',type=Path,required=True)
    ap.add_argument('--checkpoint',type=Path,required=True)
    ap.add_argument('--output',type=Path,default=Path('generated/d2-failure-memory-provenance-l2b-public-execution-status-r22.json'))
    a=ap.parse_args()
    auth=json.loads(a.authority_receipt.read_text())
    support=json.loads(a.support_receipt.read_text())
    smokes=json.loads(a.synthetic_smokes.read_text())
    ck=json.loads(a.checkpoint.read_text())
    assert auth['status']=='R19_EXTERNAL_HUMAN_BOUNDED_SCIENTIFIC_EXECUTION_AUTHORITY_VALID'
    assert support['status']=='R19_PREBENCHMARK_ZERO_COMPLETION_SUPPORT_GATE_PASS'
    assert smokes['status']=='R19_TWO_FIXED_NONBENCHMARK_SYNTHETIC_COMPLETION_SMOKES_PASS'
    assert ck['status']=='R19_CONFIRMATORY_PREFIX_CHECKPOINT_NO_INTERIM_INFERENCE'
    assert ck['interim_policy']['task_deltas_computed'] is False
    out={
      'schema_version':'1.0','paper_id':'D2-PAPER-FAILURE-MEMORY-PROVENANCE',
      'status':'R19_AUTHORIZED_CONFIRMATORY_EXECUTION_IN_PROGRESS_NO_INTERIM_INFERENCE',
      'authority':{
        'bounded_r19_scientific_execution_authority_valid':True,
        'scientific_claim_authority':False,
        'r18_retry_authorized':False,
        'l3_authorized':False,
        'authority_receipt_sha256':sha(a.authority_receipt),
      },
      'prebenchmark_support':{
        'zero_completion_support_gate_pass':True,
        'synthetic_transport_smokes_pass':True,
        'successful_synthetic_completions':2,
        'support_receipt_sha256':sha(a.support_receipt),
        'synthetic_smokes_sha256':sha(a.synthetic_smokes),
      },
      'execution_prefix':{
        'episodes_expected':ck['execution']['episodes_expected'],
        'episodes_complete':ck['execution']['episodes_complete'],
        'complete_independent_tasks':ck['execution']['complete_independent_tasks'],
        'next_sequence_index':ck['execution']['next_sequence_index'],
        'agent_completions':ck['execution']['agent_completions'],
        'agent_completion_budget':ck['execution']['agent_completion_budget'],
        'fuzzy_evaluator_completions':ck['execution']['fuzzy_evaluator_completions'],
        'fuzzy_evaluator_completion_budget':ck['execution']['fuzzy_evaluator_completion_budget'],
        'post_started_failure':ck['execution']['post_started_failure'],
        'in_flight_episode':ck['execution']['in_flight_episode'],
      },
      'pre_exposure_retry_state':{
        'sequence26_exact_retry_consumed':bool((ck.get('retry_state') or {}).get('sequence26_exact_retry_consumed',False)),
        'sequence26_additional_retry_permitted':bool((ck.get('retry_state') or {}).get('sequence26_additional_retry_permitted',False)),
        'sequence26_retry_adjudication_sha256':(ck.get('integrity') or {}).get('seq026_retry_adjudication_sha256'),
      },
      'interim_policy':{
        'terminal_scores_exposed_in_projection':False,
        'task_deltas_computed':False,'effect_mean_computed':False,'p_value_computed':False,'confidence_interval_computed':False,
        'claim_update_allowed':False,'full_140_required_for_confirmatory_analysis':True,
        'resume_only_exact_frozen_sequence':ck['execution']['next_sequence_index'],
      },
      'stanford_o5':{
        'disposition':'REQUIRES_SCIENTIFIC_REOPEN',
        'scientific_reopen_status':'AUTHORIZED_EXECUTION_IN_PROGRESS',
        'current_verdict':'NO_VERDICT_INCOMPLETE_CONFIRMATORY_EXECUTION',
      },
      'redaction':{'terminal_scores':False,'browser_actions':False,'raw_memory_text':False,'internal_run_paths':False,'authority_source_message':False},
    }
    a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':out['status'],'episodes_complete':out['execution_prefix']['episodes_complete'],'next':out['execution_prefix']['next_sequence_index'],'interim_inference':False},ensure_ascii=False))
if __name__=='__main__': main()
