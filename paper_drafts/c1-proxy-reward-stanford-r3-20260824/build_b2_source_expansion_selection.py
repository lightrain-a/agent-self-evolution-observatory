#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
INPUT_ROOT = Path('/home/wyt/code/agent-self-evolution-observatory-discovery-benchmark-20260821')
PARQUET = INPUT_ROOT / 'generated/research-data/paper-yield-d5-c01/parquet-cache/wa_awm_shuffle1-shopping_run1.parquet'
TASK_CONFIG = INPUT_ROOT / 'generated/research-data/paper-yield-d5-c01/self-improve-fragility/webarena/src/walt/benchmarks/wa/test_configs/test.raw.json'
VENDOR = INPUT_ROOT / 'generated/research-data/paper-yield-d5-c01/vendor'
B1 = Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b1-exact-retrieval-exposure-20260824/b1-exact-retrieval-exposure.json')
OUT = HERE / 'b2-source-expansion-selection.json'

F0 = {'21','22','23','24','25','47'}
F0C = {'26','48','49','50','51','96','117','126'}
PRIMARY_FUTURES = {'164','385','387','388'}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
                lines.append(f"Step {step_id} evaluation: {' '.join(str(current['evaluation_previous_goal']).split())[:500]}")
            if current.get('next_goal'):
                lines.append(f"Step {step_id} next goal: {' '.join(str(current['next_goal']).split())[:500]}")
            for action in args.get('action') or []:
                lines.append(f"Step {step_id} action: {json.dumps(action, ensure_ascii=False, sort_keys=True)[:900]}")
        controller = (step or {}).get('controller_messages') or {}
        for result in controller.get('action_result') or []:
            content = result.get('content') if isinstance(result, dict) else str(result)
            if content:
                lines.append(f"Step {step_id} result: {' '.join(str(content).split())[:900]}")
        if len(lines) >= 36:
            break
    return '\n'.join(lines)


def main() -> int:
    import sys
    sys.path.insert(0, str(VENDOR))
    import pyarrow.parquet as pq  # type: ignore

    b1 = json.loads(B1.read_text(encoding='utf-8'))
    b1_hits = {str(r['task_id']) for r in b1['all_rows'] if r.get('threshold_hit') and 'shopping' in (r.get('sites') or []) and not r.get('is_source_task')}
    # These tasks are preserved as held-out retrieval-exposure support before any B2 writer call.
    exclude = F0 | F0C | PRIMARY_FUTURES | b1_hits

    configs = json.loads(TASK_CONFIG.read_text(encoding='utf-8'))
    config_by_id = {str(r['task_id']): r for r in configs}
    rows = pq.read_table(PARQUET, columns=['task_id','task_prompt','is_successful','trajectory_json']).to_pylist()
    candidates = []
    for row in rows:
        tid = str(row['task_id'])
        if tid in exclude or tid not in config_by_id:
            continue
        try:
            summary = action_summary(str(row['trajectory_json']))
        except Exception:
            continue
        if not summary.strip():
            continue
        cfg = config_by_id[tid]
        candidates.append({
            'task_id': tid,
            'task_prompt': str(row['task_prompt']),
            'original_is_successful': bool(row['is_successful']),
            'intent_template_id': int(cfg.get('intent_template_id')) if cfg.get('intent_template_id') is not None else None,
            'trajectory_summary_sha256': hashlib.sha256(json.dumps(summary, ensure_ascii=False, sort_keys=True, separators=(',',':')).encode()).hexdigest(),
        })

    selected = []
    for outcome in (False, True):
        subset = sorted([r for r in candidates if r['original_is_successful'] is outcome], key=lambda r: int(r['task_id']))
        used_templates = set()
        chosen = []
        for r in subset:
            template = r['intent_template_id']
            if template in used_templates:
                continue
            chosen.append(r); used_templates.add(template)
            if len(chosen) == 8:
                break
        if len(chosen) < 8:
            chosen_ids = {r['task_id'] for r in chosen}
            for r in subset:
                if r['task_id'] in chosen_ids:
                    continue
                chosen.append(r)
                if len(chosen) == 8:
                    break
        if len(chosen) != 8:
            raise RuntimeError(f'cannot select eight rows for outcome={outcome}')
        selected.extend(chosen)

    selected = sorted(selected, key=lambda r: (r['original_is_successful'], int(r['task_id'])))
    payload = {
        'schema_version': '1.0',
        'artifact_type': 'pre-outcome-source-expansion-selection',
        'paper_id': 'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE',
        'experiment_id': 'D2-PROXY-B2-SOURCE-EXPANSION',
        'status': 'FROZEN_SELECTION_BEFORE_PROVIDER_CALLS',
        'selection_rule': {
            'target_new_sources': 16,
            'balance': {'original_failure': 8, 'original_success': 8},
            'candidate_substrate': 'released AWM Shopping trajectories with parseable non-empty historical F0 action_summary',
            'within_outcome_order': 'lowest task ID, preferring distinct intent_template_id until eight are selected; if fewer than eight unique templates exist, fill by lowest remaining task ID',
            'exclusions': {
                'original_F0': sorted(F0, key=int),
                'prompt_control_F0C': sorted(F0C, key=int),
                'primary_fixed_evidence_futures': sorted(PRIMARY_FUTURES, key=int),
                'B1_native_retrieval_hits_reserved_as_heldout': sorted(b1_hits, key=int),
            },
            'selection_uses_memory_text': False,
            'selection_uses_B2_writer_outputs': False,
            'selection_uses_downstream_terminal_outcomes': False,
            'B1_retrieval_exposure_is_pre_outcome_heldout_partition': True,
        },
        'selected_sources': selected,
        'summary': {
            'selected': len(selected),
            'original_failure': sum(not r['original_is_successful'] for r in selected),
            'original_success': sum(r['original_is_successful'] for r in selected),
            'distinct_intent_templates': len({r['intent_template_id'] for r in selected}),
            'reserved_B1_hit_tasks': sorted(b1_hits, key=int),
        },
        'source_bindings': {
            'trajectory_parquet': {'path': str(PARQUET), 'sha256': sha(PARQUET)},
            'task_config': {'path': str(TASK_CONFIG), 'sha256': sha(TASK_CONFIG)},
            'B1_retrieval_exposure': {'path': str(B1), 'sha256': sha(B1)},
        },
        'provider_calls': 0,
        'new_rollouts': 0,
        'scientific_authority': False,
        'experiment_authority': False,
        'claim_expansion_authority': False,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({'status': payload['status'], 'summary': payload['summary'], 'task_ids':[r['task_id'] for r in selected]}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
