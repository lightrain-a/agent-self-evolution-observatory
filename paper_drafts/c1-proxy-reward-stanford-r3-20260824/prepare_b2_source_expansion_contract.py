#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PAPER_ID = 'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE'
EXPERIMENT_ID = 'D2-PROXY-B2-SOURCE-EXPANSION'
AUTHORITY_TYPE = 'human-c1-proxy-reward-stanford-repair-experiment-program'
EXPECTED_SOURCE_MESSAGE_SHA = '7699d234bb5fc874d57ee418a2e0aabf6c49ffc8dcc52685ce5b9bcc86282e62'
EXPECTED_MODEL = {'requested':'deepseek-v4-flash','temperature':0.0,'max_output_tokens':2200,'thinking':None,'provider_retries':0,'store':True,'substitution_allowed':False}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jsha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',',':')).encode('utf-8')).hexdigest()


def load(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(obj, dict):
        raise RuntimeError(f'JSON root must be object: {path}')
    return obj


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    tmp.replace(path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--master-authority', required=True, type=Path)
    ap.add_argument('--selection', required=True, type=Path)
    ap.add_argument('--baseline-program', required=True, type=Path)
    ap.add_argument('--b1-result', required=True, type=Path)
    ap.add_argument('--runner', required=True, type=Path)
    ap.add_argument('--input-root', required=True, type=Path)
    ap.add_argument('--env-file', required=True, type=Path)
    ap.add_argument('--run-root', required=True, type=Path)
    args = ap.parse_args()

    master = load(args.master_authority)
    require(master.get('authority_type') == AUTHORITY_TYPE and master.get('decision') == 'approve', 'master authority invalid')
    require(master.get('paper_id') == PAPER_ID and master.get('source_message_sha256') == EXPECTED_SOURCE_MESSAGE_SHA, 'master authority binding mismatch')
    future = master.get('future_repair_experiments') or {}
    require(future.get('human_program_authorized') is True, 'future experiment program not authorized')
    require(future.get('requires_per_experiment_preregistration') is True and future.get('requires_budget_and_stop_rule') is True, 'master requires frozen sub-contract')
    require(future.get('automatic_execution_without_frozen_subcontract') is False and future.get('outcome_driven_scope_expansion_authorized') is False, 'master authority is not fail-closed')
    require(master.get('provider_credential_use_authorized_if_required_by_a_frozen_subcontract') is True, 'provider credential use not authorized')
    require(master.get('claim_expansion_authorized') is False and master.get('submission_authority') is False, 'master authority scope expanded')

    selection = load(args.selection)
    require(selection.get('paper_id') == PAPER_ID and selection.get('experiment_id') == EXPERIMENT_ID, 'selection identity drift')
    require(selection.get('status') == 'FROZEN_SELECTION_BEFORE_PROVIDER_CALLS', 'selection not frozen')
    require(selection['summary']['selected'] == 16 and selection['summary']['original_failure'] == 8 and selection['summary']['original_success'] == 8, 'selection balance drift')
    require(len(selection['summary']['reserved_B1_hit_tasks']) == 8, 'B1 heldout reservation drift')
    source_tasks = [str(r['task_id']) for r in selection['selected_sources']]
    require(len(source_tasks) == 16 and len(set(source_tasks)) == 16, 'source support invalid')

    baseline = load(args.baseline_program)
    require(baseline.get('paper_id') == PAPER_ID and baseline.get('status') == 'FROZEN_BEFORE_NEW_EXPERIMENTS' and baseline.get('artifact_type') == 'baseline-aligned-scientific-experiment-program', 'baseline program drift')
    b1 = load(args.b1_result)
    require(b1.get('experiment_id') == 'D2-PROXY-B1-EXACT-RETRIEVAL-EXPOSURE' and b1.get('status') == 'COMPLETE_ZERO_PROVIDER_CALLS', 'B1 result drift')

    source_root = args.input_root / 'generated/research-data/paper-yield-d5-c01'
    paths = {
        'parquet': source_root / 'parquet-cache/wa_awm_shuffle1-shopping_run1.parquet',
        'task_config': source_root / 'self-improve-fragility/webarena/src/walt/benchmarks/wa/test_configs/test.raw.json',
        'success_prompt': source_root / 'self-improve-fragility/webarena/src/walt/browser_use/custom/prompts/reasoningbank_pass.md',
        'failure_prompt': source_root / 'self-improve-fragility/webarena/src/walt/browser_use/custom/prompts/reasoningbank_fail.md',
        'selection': args.selection,
        'baseline_program': args.baseline_program,
        'B1_retrieval_exposure': args.b1_result,
    }
    for key, path in paths.items():
        require(path.is_file(), f'missing source artifact: {key}')
    require(args.runner.is_file(), 'runner missing')
    require(args.env_file.is_file(), 'env file missing')
    vendor = source_root / 'vendor'
    require(vendor.is_dir(), 'vendor runtime missing')

    source_metadata = {str(r['task_id']): {
        'original_is_successful': bool(r['original_is_successful']),
        'intent_template_id': r['intent_template_id'],
        'task_prompt': r['task_prompt'],
        'trajectory_summary_sha256': r['trajectory_summary_sha256'],
    } for r in selection['selected_sources']}

    run_root = args.run_root.resolve()
    contract: dict[str, Any] = {
        'schema_version':'1.0',
        'paper_id':PAPER_ID,
        'experiment_id':EXPERIMENT_ID,
        'status':'FROZEN_BEFORE_PROVIDER_CALLS',
        'frozen_at':datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        'question':'Does the reward-conditioned write-time state divergence replicate over a broader, outcome-balanced, intent-template-diverse set of released Shopping trajectories under the exact original F0 writer contract?',
        'relationship_to_primary_claim':'breadth replication of the upstream write channel only; does not alter the primary F2R1 estimand or claim cross-domain/downstream generalization',
        'source_tasks':source_tasks,
        'source_metadata':source_metadata,
        'source_artifacts':{key:{'path':str(path.resolve()),'sha256':sha(path)} for key,path in paths.items()},
        'vendor_path':str(vendor.resolve()),
        'provider_env_file':str(args.env_file.resolve()),
        'human_authority':{'path':str(args.master_authority.resolve()),'sha256':sha(args.master_authority),'source_message_sha256':EXPECTED_SOURCE_MESSAGE_SHA},
        'code':{'runner':{'path':str(args.runner.resolve()),'sha256':sha(args.runner)}},
        'writer_model':EXPECTED_MODEL,
        'conditions':['success','failure'],
        'expected_provider_calls':32,
        'breadth_gate':{'min_complete_pairs':14,'min_exact_content_change_rate':0.9,'min_title_set_change_rate':0.8},
        'gate_interpretation':{
            'pass':'supports broader replication of the write-time channel on this frozen 16-source expansion; it does not upgrade downstream or domain generalization',
            'fail':'the broadened write-channel replication is not established; preserve original four-pair result with its existing boundary',
        },
        'missingness_policy':{
            'provider_retries':0,
            'attempt_all_32_frozen_units_even_if_some_provider_calls_fail':True,
            'top_up_failed_units':False,
            'replace_source_tasks':False,
            'impute_missing_memory':False,
            'report_label_specific_missingness':True,
        },
        'selection_guards':{
            'B1_native_retrieval_hits_reserved_as_heldout':selection['summary']['reserved_B1_hit_tasks'],
            'selection_uses_B2_writer_outputs':False,
            'selection_uses_downstream_terminal_outcomes':False,
            'outcome_used_only_for_8_8_balance':True,
        },
        'execution_guards':{
            'single_writer_transaction_lock_required':True,
            'response_first_archival_required':True,
            'content_addressed_raw_memory_archive':True,
            'resumable_stage_cache':True,
        },
        'authority':{
            'scientific_reopen_authority':True,
            'experiment_authority':True,
            'provider_call_authority':True,
            'gpu_authority':False,
            'claim_expansion_authority':False,
            'submission_authority':False,
        },
    }
    contract['contract_sha256'] = jsha(contract)
    contract_path = run_root / 'b2-source-expansion-contract.json'
    atomic_json(contract_path, contract)
    receipt = {
        'schema_version':'1.0',
        'receipt_type':'scoped-experiment-authorization',
        'paper_id':PAPER_ID,
        'experiment_id':EXPERIMENT_ID,
        'status':'B2_SOURCE_EXPANSION_AUTHORIZED',
        'master_authority_sha256':sha(args.master_authority),
        'selection_sha256':sha(args.selection),
        'baseline_program_sha256':sha(args.baseline_program),
        'B1_result_sha256':sha(args.b1_result),
        'contract_payload_sha256':contract['contract_sha256'],
        'contract_file_sha256':sha(contract_path),
        'runner_sha256':contract['code']['runner']['sha256'],
        'provider_call_ceiling':32,
        'breadth_gate':contract['breadth_gate'],
        'authority':contract['authority'],
    }
    atomic_json(run_root / 'b2-source-expansion-authorization-receipt.json', receipt)
    print(json.dumps({'status':receipt['status'],'contract_file_sha256':receipt['contract_file_sha256'],'source_tasks':source_tasks,'provider_call_ceiling':32,'breadth_gate':receipt['breadth_gate']}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
