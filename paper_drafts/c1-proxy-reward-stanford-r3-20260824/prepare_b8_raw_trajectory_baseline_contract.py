#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PAPER_ID = 'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE'
EXPERIMENT_ID = 'D2-PROXY-B8-RAW-TRAJECTORY-BASELINE'
MASTER_AUTH_SHA = 'ddc5bd50487ed431f5d24ee84cda4e422f36216b4191a02db21db18ae821161f'
MODEL = {
    'requested': 'doubao-seed-2.0-mini',
    'expected_resolved': 'doubao-seed-2-0-mini-260215',
    'temperature': 0.2,
    'max_output_tokens': 900,
    'thinking': 'disabled',
    'provider_retries': 0,
    'store': True,
    'allow_thinking_compatibility_fallback': False,
    'substitution_allowed': False,
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tsha(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def load(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(obj, dict):
        raise RuntimeError(f'JSON root must be object: {path}')
    return obj


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def write_json(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    os.replace(tmp, path)


def normalize_text(text: str) -> str:
    return ' '.join(str(text or '').split())


def action_summary(trajectory_json: str) -> str:
    data = json.loads(trajectory_json)
    lines: list[str] = []
    for step_id, step in sorted((data.get('steps') or {}).items(), key=lambda kv: int(kv[0])):
        output = (step or {}).get('output_messages') or {}
        tool_call_message = output.get('tool_call_message') or {}
        calls = tool_call_message.get('tool_calls') or []
        if calls:
            args = calls[0].get('args') or {}
            current = args.get('current_state') or {}
            if current.get('evaluation_previous_goal'):
                lines.append(f"Step {step_id} evaluation: {normalize_text(current['evaluation_previous_goal'])[:500]}")
            if current.get('next_goal'):
                lines.append(f"Step {step_id} next goal: {normalize_text(current['next_goal'])[:500]}")
            for action in args.get('action') or []:
                lines.append(f"Step {step_id} action: {json.dumps(action, ensure_ascii=False, sort_keys=True)[:900]}")
        controller = (step or {}).get('controller_messages') or {}
        for result in controller.get('action_result') or []:
            content = result.get('content') if isinstance(result, dict) else str(result)
            if content:
                lines.append(f"Step {step_id} result: {normalize_text(content)[:900]}")
        if len(lines) >= 36:
            break
    return '\n'.join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    for name in ['master_authority', 'b4_contract', 'b4_result', 'b5_result', 'runner', 'env_file', 'run_root']:
        ap.add_argument('--' + name.replace('_', '-'), required=True, type=Path)
    args = ap.parse_args()

    require(sha(args.master_authority) == MASTER_AUTH_SHA, 'master authority drift')
    master = load(args.master_authority)
    require(master.get('paper_id') == PAPER_ID and master.get('decision') == 'approve', 'master authority invalid')
    future = master.get('future_repair_experiments') or {}
    require(future.get('human_program_authorized') is True, 'future repair program not authorized')
    require(future.get('requires_per_experiment_preregistration') is True, 'per-experiment preregistration requirement drift')
    require(future.get('automatic_execution_without_frozen_subcontract') is False, 'automatic execution policy drift')
    require(master.get('provider_credential_use_authorized_if_required_by_a_frozen_subcontract') is True, 'provider credential authority missing')
    require(master.get('claim_expansion_authorized') is False, 'claim expansion authority drift')

    b4c, b4r, b5r = load(args.b4_contract), load(args.b4_result), load(args.b5_result)
    require(b4c.get('paper_id') == PAPER_ID and b4r.get('paper_id') == PAPER_ID and b5r.get('paper_id') == PAPER_ID, 'source paper identity drift')
    require(b4r.get('status') == 'B4_EXECUTION_COMPLETE' and b4r.get('summary', {}).get('provider_calls_complete') == 288, 'B4 incomplete')
    require(b5r.get('status') == 'B5_EXECUTION_COMPLETE' and b5r.get('summary', {}).get('provider_calls_complete') == 144, 'B5 incomplete')
    require(len(b4c.get('task_units') or []) == 36, 'B4 support drift')
    require(args.runner.is_file() and args.env_file.is_file(), 'runner/env missing')

    import pyarrow.parquet as pq  # type: ignore
    parquet = Path(b4c['source_artifacts']['parquet']['path'])
    require(parquet.is_file() and sha(parquet) == b4c['source_artifacts']['parquet']['sha256'], 'parquet drift')
    source_ids = sorted({int(u['selected_source_task']) for u in b4c['task_units']})
    rows = {int(x['task_id']): x for x in pq.read_table(parquet, columns=['task_id', 'task_prompt', 'trajectory_json']).to_pylist()}
    require(all(t in rows for t in source_ids), 'selected source missing from parquet')

    raw_dir = args.run_root / 'private' / 'raw-trajectory-memory'
    raw_dir.mkdir(parents=True, exist_ok=True)
    source_summaries: dict[str, dict[str, Any]] = {}
    for tid in source_ids:
        summary = action_summary(str(rows[tid]['trajectory_json']))
        require(bool(summary.strip()), f'empty trajectory summary: {tid}')
        p = raw_dir / f'{tid}-writer-input-action-summary.txt'
        p.write_text(summary, encoding='utf-8')
        source_summaries[str(tid)] = {
            'source_task': tid,
            'source_task_prompt': str(rows[tid]['task_prompt']),
            'path': str(p.resolve()),
            'sha256': sha(p),
            'text_sha256': tsha(summary),
            'chars': len(summary),
            'lines': len(summary.splitlines()),
            'projection': 'same deterministic action_summary projection used by the B2 memory-writer input pipeline',
        }

    task_units = []
    for u in b4c['task_units']:
        row = dict(u)
        row['raw_trajectory_memory'] = source_summaries[str(int(u['selected_source_task']))]
        task_units.append(row)

    contract: dict[str, Any] = {
        'schema_version': '1.0',
        'experiment_id': EXPERIMENT_ID,
        'paper_id': PAPER_ID,
        'status': 'FROZEN_BEFORE_PROVIDER_CALLS',
        'frozen_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        'question': 'On the exact B4 36-task native retrieval support, does reward-conditioned memory rewriting produce a practically large terminal difference relative to the common raw trajectory evidence supplied to the writer?',
        'baseline_role': {
            'name': 'writer-input raw trajectory baseline',
            'literature_alignment': 'motivated by Trajectory Retrieval / long-context baselines used in ReasoningBank, MemAgents, and EvoMemBench',
            'replication_boundary': 'not claimed as a byte-for-byte reproduction of any external implementation; it reuses the exact compact trajectory projection that the C1 writer consumed before counterfactual reward-label conditioning',
            'counterfactual_reward_label_injected': False,
            'memory_rewrite_applied': False,
            'organic_runtime_evaluation_text_may_remain': True,
        },
        'relationship_to_existing_arms': 'same 36 future tasks, selected source identities, released evidence packets, evaluator, downstream policy, temperature, and rollout depth as B4/B5; only the persistent context is replaced by the common raw writer-input trajectory summary',
        'human_authority': {'path': str(args.master_authority.resolve()), 'sha256': MASTER_AUTH_SHA},
        'b4_contract': {'path': str(args.b4_contract.resolve()), 'sha256': sha(args.b4_contract)},
        'b4_result': {'path': str(args.b4_result.resolve()), 'sha256': sha(args.b4_result)},
        'b5_result': {'path': str(args.b5_result.resolve()), 'sha256': sha(args.b5_result)},
        'task_units': task_units,
        'source_summaries': source_summaries,
        'future_task_count': 36,
        'selected_source_count': len(source_ids),
        'condition': 'raw_trajectory',
        'rollouts_per_task': 4,
        'expected_provider_calls': 144,
        'model': MODEL,
        'source_artifacts': b4c['source_artifacts'],
        'vendor_path': b4c['vendor_path'],
        'provider_env_file': str(args.env_file.resolve()),
        'code': {'runner': {'path': str(args.runner.resolve()), 'sha256': sha(args.runner)}},
        'primary_gate': {
            'statistic': 'mean over 36 tasks of 0.5*(|p_success_memory-p_raw_trajectory| + |p_failure_memory-p_raw_trajectory|)',
            'min_mean_absolute_rewrite_vs_raw_effect': 0.15,
            'omnibus_three_arm_permutation_p_lt': 0.05,
            'permutation_repetitions': 100000,
            'permutation_seed': 20260824,
            'interpretation': 'Both the practical-effect floor and permutation criterion must pass to establish a practically large representation/rewrite effect relative to raw writer-input trajectory evidence on this support.',
        },
        'secondary_descriptives': [
            'raw trajectory minus no-memory rate per task',
            'four-arm task geometry over success/failure/raw/no-memory',
            'raw baseline distance to the success-memory and failure-memory branches',
            'joint floor/ceiling counts',
            'results grouped by selected source and intent template',
        ],
        'missingness_policy': {
            'provider_retries': 0,
            'stop_after_first_no_text_provider_failure': True,
            'top_up_failed_units': False,
            'replace_future_tasks': False,
        },
        'execution_guards': {
            'single_writer_transaction_lock_required': True,
            'response_first_archival_required': True,
            'resumable_stage_cache': True,
            'fixed_order_chunking_allowed': True,
            'chunking_cannot_depend_on_outcomes': True,
            'save_result_after_each_provider_post': True,
        },
        'scope_boundary': {
            'no_live_browser_claim': True,
            'no_population_causal_effect_claim': True,
            'no_threshold_relaxation': True,
            'B4_success_vs_failure_negative_boundary_preserved': True,
            'B5_no_memory_negative_boundary_preserved': True,
            'B7_partial_reference_diagnostic_does_not_change_gate': True,
            'no_outcome_driven_task_selection': True,
            'no_external_baseline_exact-replication_claim': True,
        },
        'authority': {
            'scientific_reopen_authority': True,
            'experiment_authority': True,
            'provider_call_authority': True,
            'gpu_authority': False,
            'claim_expansion_authority': False,
            'submission_authority': False,
        },
    }
    raw = dict(contract)
    contract['contract_sha256'] = hashlib.sha256(json.dumps(raw, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    out = args.run_root / 'b8-contract.json'
    write_json(out, contract)
    receipt = {
        'schema_version': '1.0',
        'receipt_type': 'scoped-experiment-authorization',
        'paper_id': PAPER_ID,
        'experiment_id': EXPERIMENT_ID,
        'status': 'B8_RAW_TRAJECTORY_BASELINE_AUTHORIZED',
        'contract_file_sha256': sha(out),
        'runner_sha256': contract['code']['runner']['sha256'],
        'future_task_count': 36,
        'selected_source_count': len(source_ids),
        'provider_call_ceiling': 144,
        'primary_gate': contract['primary_gate'],
        'authority': contract['authority'],
    }
    write_json(args.run_root / 'b8-authorization-receipt.json', receipt)
    print(json.dumps({
        'status': receipt['status'],
        'contract_file_sha256': receipt['contract_file_sha256'],
        'provider_call_ceiling': 144,
        'selected_source_count': len(source_ids),
        'source_summary_chars': {k: v['chars'] for k, v in source_summaries.items()},
    }, indent=2))


if __name__ == '__main__':
    main()
