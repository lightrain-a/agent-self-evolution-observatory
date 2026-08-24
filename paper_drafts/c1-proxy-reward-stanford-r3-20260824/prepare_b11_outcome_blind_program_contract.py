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
EXPERIMENT_ID = 'D2-PROXY-B11-OUTCOME-BLIND-PROCEDURAL-WRITER'
ORIGINAL_COMPLETE = [21, 22, 23, 25]
MASTER_AUTH_SHA = 'ddc5bd50487ed431f5d24ee84cda4e422f36216b4191a02db21db18ae821161f'
WRITER_MODEL = {
    'requested': 'deepseek-v4-flash',
    'temperature': 0.0,
    'max_output_tokens': 4096,
    'thinking': None,
    'provider_retries': 0,
    'store': True,
    'allow_thinking_compatibility_fallback': False,
    'substitution_allowed': False,
}
TERMINAL_MODEL = {
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


def jsha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()


def load(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(obj, dict):
        raise RuntimeError(f'JSON root must be object: {path}')
    return obj


def req(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def writej(path: Path, obj: dict[str, Any]) -> None:
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
    for name in [
        'master_authority', 'f0', 'b2_selection', 'b2_r1_contract', 'b2_breadth', 'b4_contract', 'b4_result',
        'b4_memory_manifest', 'b5_result', 'b8_result', 'neutral_prompt', 'writer_runner', 'manifest_builder',
        'terminal_runner', 'parquet', 'task_config', 'env_file', 'run_root'
    ]:
        ap.add_argument('--' + name.replace('_', '-'), required=True, type=Path)
    args = ap.parse_args()

    req(sha(args.master_authority) == MASTER_AUTH_SHA, 'master authority drift')
    authority = load(args.master_authority)
    req(authority.get('paper_id') == PAPER_ID and authority.get('decision') == 'approve', 'master authority invalid')
    future = authority.get('future_repair_experiments') or {}
    req(future.get('human_program_authorized') is True and future.get('requires_per_experiment_preregistration') is True, 'future experiment authority missing')
    req(future.get('automatic_execution_without_frozen_subcontract') is False and future.get('outcome_driven_scope_expansion_authorized') is False, 'scope policy drift')
    req(authority.get('provider_credential_use_authorized_if_required_by_a_frozen_subcontract') is True, 'provider credential authority missing')
    req(authority.get('claim_expansion_authorized') is False and authority.get('submission_authority') is False, 'authority expanded')

    for path in [args.f0, args.b2_selection, args.b2_r1_contract, args.b2_breadth, args.b4_contract, args.b4_result, args.b4_memory_manifest, args.b5_result, args.b8_result, args.neutral_prompt, args.writer_runner, args.manifest_builder, args.terminal_runner, args.parquet, args.task_config, args.env_file]:
        req(path.is_file(), f'missing artifact: {path}')

    f0 = load(args.f0)
    selection = load(args.b2_selection)
    b2c = load(args.b2_r1_contract)
    b2b = load(args.b2_breadth)
    b4c = load(args.b4_contract)
    b4r = load(args.b4_result)
    b4m = load(args.b4_memory_manifest)
    b5r = load(args.b5_result)
    b8r = load(args.b8_result)
    req(f0.get('summary', {}).get('paired_trajectories_complete') == 4, 'F0 drift')
    req(selection.get('status') == 'FROZEN_SELECTION_BEFORE_PROVIDER_CALLS' and len(selection.get('selected_sources') or []) == 16, 'B2 selection drift')
    req(b2c.get('status') == 'FROZEN_BEFORE_PROVIDER_CALLS' and len(b2c.get('source_tasks') or []) == 16, 'B2 R1 contract drift')
    req(b2b.get('status') == 'B2_BROAD_WRITE_CHANNEL_SUPPORTED' and b2b.get('combined_complete_pairs') == 20, 'B2 breadth drift')
    req(b4c.get('status') == 'FROZEN_BEFORE_PROVIDER_CALLS' and len(b4c.get('task_units') or []) == 36, 'B4 contract drift')
    req(b4r.get('status') == 'B4_EXECUTION_COMPLETE' and b4r.get('summary', {}).get('provider_calls_complete') == 288, 'B4 result drift')
    req(b4m.get('status') == 'B4_MEMORY_MANIFEST_READY' and b4m.get('memory_object_count') == 40, 'B4 memory manifest drift')
    req(b5r.get('status') == 'B5_EXECUTION_COMPLETE' and b5r.get('summary', {}).get('provider_calls_complete') == 144, 'B5 result drift')
    req(b8r.get('status') == 'B8_EXECUTION_COMPLETE' and b8r.get('summary', {}).get('provider_calls_complete') == 144, 'B8 result drift')

    neutral_prompt = args.neutral_prompt.read_text(encoding='utf-8')
    lower = neutral_prompt.lower()
    leak_terms = ['success', 'successful', 'failure', 'failed', 'reward', 'score', 'outcome']
    leaked = [term for term in leak_terms if term in lower]
    req(not leaked, f'neutral prompt contains outcome semantics: {leaked}')

    import pyarrow.parquet as pq  # type: ignore
    rows = {int(x['task_id']): x for x in pq.read_table(args.parquet, columns=['task_id', 'task_prompt', 'trajectory_json']).to_pylist()}
    task_config = json.loads(args.task_config.read_text(encoding='utf-8'))
    req(isinstance(task_config, list), 'task config root must be list')
    task_by = {int(x['task_id']): x for x in task_config}
    f0_pairs = {int(x['task_id']): x for x in f0['pairs']}
    selected = {int(x['task_id']): x for x in selection['selected_sources']}
    breadth_sources = [int(x) for x in b2c['source_tasks']]
    req(set(breadth_sources) == set(selected), 'B2 source task set mismatch')
    source_order = ORIGINAL_COMPLETE + breadth_sources
    req(len(source_order) == 20 and len(set(source_order)) == 20, '20-source geometry drift')
    b4_desc = {int(x['source_task']): str(x['task_description']) for x in b4m['objects']}

    source_units = []
    for tid in source_order:
        req(tid in rows and tid in task_by and tid in b4_desc, f'source unavailable: {tid}')
        summary = action_summary(str(rows[tid]['trajectory_json']))
        digest = jsha(summary)
        expected = f0_pairs[tid]['trajectory_summary_sha256'] if tid in ORIGINAL_COMPLETE else selected[tid]['trajectory_summary_sha256']
        req(digest == expected, f'action-summary binding drift: {tid}')
        expected_prompt = str(f0_pairs[tid]['task_prompt']) if tid in ORIGINAL_COMPLETE else str(selected[tid]['task_prompt'])
        req(str(rows[tid]['task_prompt']) == expected_prompt, f'task prompt drift: {tid}')
        source_units.append({
            'source_task': tid,
            'source_kind': 'original_f0_complete' if tid in ORIGINAL_COMPLETE else 'b2_breadth_r1',
            'task_prompt': expected_prompt,
            'task_description': b4_desc[tid],
            'action_summary_sha256': digest,
            'original_is_successful': bool(f0_pairs[tid]['original_is_successful']) if tid in ORIGINAL_COMPLETE else bool(selected[tid]['original_is_successful']),
            'intent_template_id': None if tid in ORIGINAL_COMPLETE else int(selected[tid]['intent_template_id']),
        })

    terminal_units = []
    for unit in b4c['task_units']:
        terminal_units.append({k: unit[k] for k in [
            'future_task', 'selected_source_task', 'intent_template_id', 'task_prompt', 'reference_answers',
            'evidence_sha256', 'released_state_sha256', 'retrieval_similarity', 'retrieval_margin'
        ]})
    required_sources = sorted({int(x['selected_source_task']) for x in terminal_units})
    req(required_sources == [25, 141, 146, 148, 163, 188, 189, 225, 226, 231, 232], f'unexpected required source set: {required_sources}')
    req(set(required_sources).issubset(set(source_order)), 'native support source not in 20-source writer set')

    primary_gate = {
        'statistic': 'mean over 36 frozen tasks of 0.5*(|p_success_memory-p_neutral_memory|+|p_failure_memory-p_neutral_memory|)',
        'min_mean_absolute_reward_conditioned_vs_neutral_effect': 0.15,
        'permutation_p_lt': 0.05,
        'permutation_repetitions': 100000,
        'permutation_seed': 20260824,
        'interpretation': 'Both practical magnitude and the within-task three-arm permutation criterion must pass. A small p-value alone is insufficient.',
    }
    source_bindings = {
        'human_authority': {'path': str(args.master_authority.resolve()), 'sha256': sha(args.master_authority)},
        'f0_write_channel': {'path': str(args.f0.resolve()), 'sha256': sha(args.f0)},
        'b2_selection': {'path': str(args.b2_selection.resolve()), 'sha256': sha(args.b2_selection)},
        'b2_r1_contract': {'path': str(args.b2_r1_contract.resolve()), 'sha256': sha(args.b2_r1_contract)},
        'b2_breadth_evidence': {'path': str(args.b2_breadth.resolve()), 'sha256': sha(args.b2_breadth)},
        'b4_contract': {'path': str(args.b4_contract.resolve()), 'sha256': sha(args.b4_contract)},
        'b4_result': {'path': str(args.b4_result.resolve()), 'sha256': sha(args.b4_result)},
        'b4_memory_manifest': {'path': str(args.b4_memory_manifest.resolve()), 'sha256': sha(args.b4_memory_manifest)},
        'b5_result': {'path': str(args.b5_result.resolve()), 'sha256': sha(args.b5_result)},
        'b8_result': {'path': str(args.b8_result.resolve()), 'sha256': sha(args.b8_result)},
        'trajectory_parquet': {'path': str(args.parquet.resolve()), 'sha256': sha(args.parquet)},
        'task_config': {'path': str(args.task_config.resolve()), 'sha256': sha(args.task_config)},
        'neutral_prompt': {'path': str(args.neutral_prompt.resolve()), 'sha256': sha(args.neutral_prompt)},
    }
    contract: dict[str, Any] = {
        'schema_version': '1.0',
        'experiment_id': EXPERIMENT_ID,
        'paper_id': PAPER_ID,
        'status': 'FROZEN_BEFORE_ANY_B11_PROVIDER_CALLS',
        'frozen_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        'scientific_question': 'After holding structured procedural rewriting itself fixed, does reward-conditioned writer semantics produce a practically large downstream terminal effect relative to an outcome-blind procedural rewrite on the exact native-retrieval support?',
        'changed_assumption': 'B8 compared rewritten memory to raw trajectory evidence. B11 instead gives the same trajectory to the same writer family and requests the same memory-item schema without outcome-conditioned reflection semantics, isolating branch-specific semantics from generic structured rewriting.',
        'neutral_prompt': {
            'path': str(args.neutral_prompt.resolve()),
            'sha256': sha(args.neutral_prompt),
            'contains_success_failure_label': False,
            'contains_numeric_reward_or_score': False,
            'outcome_semantics_string_audit_terms': leak_terms,
            'leaked_terms_found': [],
            'same_max_memory_items_as_reasoningbank': 3,
            'same_markdown_fields_as_reasoningbank': ['Memory Item', 'Title', 'Description', 'Content'],
        },
        'writer_stage': {
            'role': 'construct the strongest same-information structured-rewrite control; no downstream scientific verdict at this stage',
            'source_units': source_units,
            'source_task_count': 20,
            'expected_provider_calls': 20,
            'model': WRITER_MODEL,
            'prompt_rule': 'Same task_prompt and deterministic action_summary bytes used by the reward-conditioned writer evidence; no success/failure label, reward, score, or outcome semantics; same at-most-three Title/Description/Content memory schema.',
            'descriptive_only_metrics': ['neutral-to-success token Jaccard distance', 'neutral-to-failure token Jaccard distance', 'title-set geometry'],
            'missingness_policy': {
                'attempt_all_20_frozen_units': True,
                'provider_retries': 0,
                'top_up_failed_units': False,
                'replace_source_tasks': False,
                'impute_missing_memory': False,
                'no_output_cap_repair': True,
            },
        },
        'terminal_stage': {
            'role': 'confirmatory same-support test of reward-conditioned branch specificity beyond generic structured rewriting',
            'task_units': terminal_units,
            'future_task_count': 36,
            'required_neutral_source_tasks': required_sources,
            'required_neutral_source_count': 11,
            'condition': 'outcome_blind_procedural',
            'rollouts_per_task': 4,
            'expected_provider_calls': 144,
            'model': TERMINAL_MODEL,
            'existing_reward_conditioned_arms': 'reuse exact B4 success/failure outcomes on the same 36 frozen tasks; no new S/F calls',
            'primary_gate': primary_gate,
            'secondary_descriptives': ['neutral versus raw trajectory', 'neutral versus no-memory', 'five-arm task-level equality/geometry', 'by-source mean effect'],
            'missingness_policy': {
                'provider_retries': 0,
                'stop_after_first_no_text_or_parse_failure': True,
                'top_up_failed_units': False,
                'replace_future_tasks': False,
                'no_model_substitution': True,
            },
        },
        'activation_policy': {
            'terminal_requires_all_20_writer_units_attempted': True,
            'terminal_requires_all_11_native_sources_complete': True,
            'terminal_task_support_and_gate_are_already_frozen_before_writer_calls': True,
            'writer_text_may_not_change_terminal_task_selection_or_retrieval_identity': True,
        },
        'program_budget': {
            'writer_provider_call_ceiling': 20,
            'terminal_provider_call_ceiling': 144,
            'total_provider_call_ceiling': 164,
            'gpu_runs': 0,
            'training_runs': 0,
        },
        'execution_guards': {
            'response_first_archival_required': True,
            'content_addressed_writer_memory_archive': True,
            'per_provider_post_stage_json': True,
            'result_json_refreshed_after_each_provider_post': True,
            'resumable_stage_cache': True,
            'single_writer_transaction_lock_per_stage': True,
            'fixed_order_chunking_allowed': True,
            'chunking_cannot_depend_on_outcomes': True,
        },
        'claim_boundary': {
            'no_new_memory_architecture_claim': True,
            'no_neutral_writer_superiority_claim': True,
            'no_live_browser_transport_claim': True,
            'no_population_causal_effect_claim': True,
            'no_policy_invariance_claim': True,
            'no_retrieval_threshold_or_task_support_change': True,
            'no_outcome_driven_scope_expansion': True,
            'B4_native_branch_nonpass_preserved_regardless_of_B11': True,
            'B8_raw_baseline_boundary_preserved_regardless_of_B11': True,
        },
        'source_bindings': source_bindings,
        'vendor_path': b4c['vendor_path'],
        'provider_env_file': str(args.env_file.resolve()),
        'code': {
            'writer_runner': {'path': str(args.writer_runner.resolve()), 'sha256': sha(args.writer_runner)},
            'manifest_builder': {'path': str(args.manifest_builder.resolve()), 'sha256': sha(args.manifest_builder)},
            'terminal_runner': {'path': str(args.terminal_runner.resolve()), 'sha256': sha(args.terminal_runner)},
            'contract_preparer': {'path': str(Path(__file__).resolve()), 'sha256': sha(Path(__file__).resolve())},
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
    contract['contract_sha256'] = hashlib.sha256(json.dumps(raw, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()
    args.run_root.mkdir(parents=True, exist_ok=True)
    contract_path = args.run_root / 'b11-program-contract.json'
    writej(contract_path, contract)
    receipt = {
        'schema_version': '1.0',
        'receipt_type': 'scoped-experiment-authorization',
        'paper_id': PAPER_ID,
        'experiment_id': EXPERIMENT_ID,
        'status': 'B11_OUTCOME_BLIND_PROGRAM_AUTHORIZED',
        'contract_file_sha256': sha(contract_path),
        'contract_sha256': contract['contract_sha256'],
        'writer_calls': 20,
        'terminal_calls': 144,
        'total_provider_call_ceiling': 164,
        'primary_gate': primary_gate,
        'required_native_source_tasks': required_sources,
        'authority': contract['authority'],
    }
    writej(args.run_root / 'b11-authorization-receipt.json', receipt)
    print(json.dumps({
        'status': receipt['status'],
        'contract_file_sha256': receipt['contract_file_sha256'],
        'contract_sha256': receipt['contract_sha256'],
        'writer_calls': 20,
        'terminal_calls': 144,
        'total_provider_call_ceiling': 164,
        'required_native_source_tasks': required_sources,
        'primary_gate': primary_gate,
    }, indent=2))


if __name__ == '__main__':
    main()
