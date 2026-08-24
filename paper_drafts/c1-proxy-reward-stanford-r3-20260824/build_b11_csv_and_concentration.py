#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Any

EXPECTED_WRITER_SHA = '2efc0a19c356043e6f3f0f991d47121c3bfbdcf5a1e425a7633ea949d67acdb0'
EXPECTED_TERMINAL_SHA = 'c13afbb4ce983f9a643cc8e1aa908f6189bc59984f60cae81de89ad82e66ec4c'
PAPER_ID = 'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE'
EXPERIMENT_ID = 'D2-PROXY-B11-OUTCOME-BLIND-PROCEDURAL-WRITER'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    with tmp.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    os.replace(tmp, path)


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--writer-result', required=True, type=Path)
    ap.add_argument('--terminal-result', required=True, type=Path)
    ap.add_argument('--run-root', required=True, type=Path)
    args = ap.parse_args()

    require(sha(args.writer_result) == EXPECTED_WRITER_SHA, 'B11 writer SHA drift')
    require(sha(args.terminal_result) == EXPECTED_TERMINAL_SHA, 'B11 terminal SHA drift')
    writer = load(args.writer_result)
    terminal = load(args.terminal_result)
    require(writer.get('paper_id') == PAPER_ID and writer.get('experiment_id') == EXPERIMENT_ID, 'writer identity drift')
    require(terminal.get('paper_id') == PAPER_ID and terminal.get('experiment_id') == EXPERIMENT_ID, 'terminal identity drift')
    require(writer.get('status') == 'B11_WRITER_COMPLETE' and writer['summary']['provider_calls_complete'] == 20, 'writer incomplete')
    require(terminal.get('status') == 'B11_TERMINAL_EXECUTION_COMPLETE' and terminal['summary']['provider_calls_complete'] == 144, 'terminal incomplete')

    writer_rows: list[dict[str, Any]] = []
    for row in writer['writer_outputs']:
        writer_rows.append({
            'source_task': int(row['source_task']),
            'condition': row['condition'],
            'provider_status': row['provider_status'],
            'resolved_model': row['resolved_model'],
            'memory_item_count': int(row['memory_item_count']),
            'raw_sha256': row['raw_sha256'],
            'titles_json': json.dumps(row.get('titles') or [], ensure_ascii=False),
            'input_tokens': int((row.get('usage') or {}).get('input_tokens') or 0),
            'output_tokens': int((row.get('usage') or {}).get('output_tokens') or 0),
            'reasoning_tokens': int((((row.get('usage') or {}).get('output_tokens_details') or {}).get('reasoning_tokens')) or 0),
            'total_tokens': int((row.get('usage') or {}).get('total_tokens') or 0),
        })

    rollout_rows: list[dict[str, Any]] = []
    for row in terminal['rollouts']:
        rollout_rows.append({
            'future_task': int(row['future_task']),
            'selected_source_task': int(row['selected_source_task']),
            'condition': row['condition'],
            'rollout': int(row['rollout']),
            'benchmark_score': float(row['benchmark_score']),
            'provider_status': row['provider_status'],
            'resolved_model': row['resolved_model'],
            'answer_sha256': row['answer_sha256'],
            'input_tokens': int((row.get('usage') or {}).get('input_tokens') or 0),
            'output_tokens': int((row.get('usage') or {}).get('output_tokens') or 0),
            'reasoning_tokens': int((((row.get('usage') or {}).get('output_tokens_details') or {}).get('reasoning_tokens')) or 0),
            'total_tokens': int((row.get('usage') or {}).get('total_tokens') or 0),
        })

    cell_rows: list[dict[str, Any]] = []
    for cell in terminal['cell_results']:
        cell_rows.append({
            'future_task': int(cell['future_task']),
            'selected_source_task': int(cell['selected_source_task']),
            'intent_template_id': int(cell['intent_template_id']),
            'success_memory_rate': float(cell['success_memory_rate']),
            'failure_memory_rate': float(cell['failure_memory_rate']),
            'neutral_memory_rate': float(cell['neutral_memory_rate']),
            'raw_trajectory_rate': float(cell['raw_trajectory_rate']),
            'no_memory_rate': float(cell['no_memory_rate']),
            'reward_conditioned_vs_neutral_effect': float(cell['reward_conditioned_vs_neutral_effect']),
            'neutral_vs_raw_absolute_difference': float(cell['neutral_vs_raw_absolute_difference']),
            'neutral_vs_no_memory_absolute_difference': float(cell['neutral_vs_no_memory_absolute_difference']),
            'neutral_closest_arms_tie_aware': '+'.join(cell['neutral_closest_arms_tie_aware']),
        })

    write_csv(args.run_root / 'b11-writer-calls.csv', [
        'source_task','condition','provider_status','resolved_model','memory_item_count','raw_sha256','titles_json',
        'input_tokens','output_tokens','reasoning_tokens','total_tokens'
    ], writer_rows)
    write_csv(args.run_root / 'b11-terminal-rollouts.csv', [
        'future_task','selected_source_task','condition','rollout','benchmark_score','provider_status','resolved_model','answer_sha256',
        'input_tokens','output_tokens','reasoning_tokens','total_tokens'
    ], rollout_rows)
    write_csv(args.run_root / 'b11-cell-results.csv', [
        'future_task','selected_source_task','intent_template_id','success_memory_rate','failure_memory_rate','neutral_memory_rate',
        'raw_trajectory_rate','no_memory_rate','reward_conditioned_vs_neutral_effect','neutral_vs_raw_absolute_difference',
        'neutral_vs_no_memory_absolute_difference','neutral_closest_arms_tie_aware'
    ], cell_rows)

    effects = [float(x['reward_conditioned_vs_neutral_effect']) for x in terminal['cell_results']]
    observed = mean(effects)
    nonzero = [x for x in terminal['cell_results'] if float(x['reward_conditioned_vs_neutral_effect']) > 0]
    ranked = sorted(nonzero, key=lambda x: float(x['reward_conditioned_vs_neutral_effect']), reverse=True)
    loo = []
    for cell in terminal['cell_results']:
        rest = [float(x['reward_conditioned_vs_neutral_effect']) for x in terminal['cell_results'] if int(x['future_task']) != int(cell['future_task'])]
        loo.append({
            'left_out_future_task': int(cell['future_task']),
            'left_out_source_task': int(cell['selected_source_task']),
            'left_out_effect': float(cell['reward_conditioned_vs_neutral_effect']),
            'mean_effect_without_task': round(mean(rest), 6),
        })
    min_loo = min(loo, key=lambda x: x['mean_effect_without_task'])
    max_loo = max(loo, key=lambda x: x['mean_effect_without_task'])

    by_source: dict[int, list[float]] = defaultdict(list)
    by_source_nonzero: dict[int, int] = defaultdict(int)
    for cell in terminal['cell_results']:
        src = int(cell['selected_source_task'])
        effect = float(cell['reward_conditioned_vs_neutral_effect'])
        by_source[src].append(effect)
        by_source_nonzero[src] += int(effect > 0)
    source_rows = []
    for src in sorted(by_source):
        source_rows.append({
            'selected_source_task': src,
            'future_task_count': len(by_source[src]),
            'nonzero_effect_tasks': by_source_nonzero[src],
            'mean_effect': round(mean(by_source[src]), 6),
            'absolute_effect_mass': round(sum(by_source[src]), 6),
        })

    total_mass = sum(effects)
    top1 = float(ranked[0]['reward_conditioned_vs_neutral_effect']) if ranked else 0.0
    top2 = sum(float(x['reward_conditioned_vs_neutral_effect']) for x in ranked[:2])
    sq_total = sum(v*v for v in effects)
    sq_top1 = top1*top1
    sq_top2 = sum(float(x['reward_conditioned_vs_neutral_effect'])**2 for x in ranked[:2])
    concentration = {
        'schema_version': '1.0',
        'artifact_type': 'b11-zero-call-concentration-and-csv-projection',
        'paper_id': PAPER_ID,
        'experiment_id': EXPERIMENT_ID,
        'status': 'B11_ZERO_CALL_CONCENTRATION_COMPLETE',
        'source_bindings': {
            'writer_result_sha256': EXPECTED_WRITER_SHA,
            'terminal_result_sha256': EXPECTED_TERMINAL_SHA,
            'builder_sha256': sha(Path(__file__).resolve()),
        },
        'provider_calls': 0,
        'new_rollouts': 0,
        'csv_projection': {
            'writer_calls_csv': {'path': str((args.run_root/'b11-writer-calls.csv').resolve()), 'rows': len(writer_rows), 'sha256': sha(args.run_root/'b11-writer-calls.csv')},
            'terminal_rollouts_csv': {'path': str((args.run_root/'b11-terminal-rollouts.csv').resolve()), 'rows': len(rollout_rows), 'sha256': sha(args.run_root/'b11-terminal-rollouts.csv')},
            'cell_results_csv': {'path': str((args.run_root/'b11-cell-results.csv').resolve()), 'rows': len(cell_rows), 'sha256': sha(args.run_root/'b11-cell-results.csv')},
            'provenance_note': 'CSV rows are deterministic projections from immutable per-call/stage-backed B11 aggregate artifacts; they do not introduce or replace scientific units.',
        },
        'summary': {
            'observed_mean_effect': round(observed, 6),
            'nonzero_tasks': len(ranked),
            'zero_tasks': len(effects) - len(ranked),
            'top1_effect_task': int(ranked[0]['future_task']) if ranked else None,
            'top1_effect': round(top1, 6),
            'top1_share_of_absolute_effect_mass': round(top1/total_mass, 6) if total_mass else 0.0,
            'top2_share_of_absolute_effect_mass': round(top2/total_mass, 6) if total_mass else 0.0,
            'top1_share_of_squared_effect_mass': round(sq_top1/sq_total, 6) if sq_total else 0.0,
            'top2_share_of_squared_effect_mass': round(sq_top2/sq_total, 6) if sq_total else 0.0,
            'minimum_leave_one_task_out_mean_effect': min_loo['mean_effect_without_task'],
            'minimum_leave_one_task_out_trigger': min_loo,
            'maximum_leave_one_task_out_mean_effect': max_loo['mean_effect_without_task'],
            'sources_with_nonzero_effect': sum(x['nonzero_effect_tasks'] > 0 for x in source_rows),
            'native_selected_source_count': len(source_rows),
        },
        'by_source': source_rows,
        'leave_one_task_out': loo,
        'interpretation': 'Descriptive concentration audit only. It tests whether the small B11 aggregate is broadly distributed or dominated by a small number of cells; it does not alter the preregistered B11 gate or permutation result.',
        'inferential_authority': False,
        'scientific_authority': False,
        'claim_expansion_authority': False,
    }
    write_json(args.run_root / 'b11-concentration-diagnostic.json', concentration)
    print(json.dumps({
        'status': concentration['status'],
        'csv_rows': {k:v['rows'] for k,v in concentration['csv_projection'].items() if isinstance(v,dict) and 'rows' in v},
        'summary': concentration['summary'],
        'by_source_nonzero': [x for x in source_rows if x['nonzero_effect_tasks'] > 0],
    }, indent=2))


if __name__ == '__main__':
    main()
