#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any

PAPER_ID = 'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE'
EXPERIMENT_ID = 'D2-PROXY-B8-RAW-TRAJECTORY-BASELINE'


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


def eq(a: float, b: float) -> bool:
    return abs(float(a) - float(b)) < 1e-12


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--contract', required=True, type=Path)
    ap.add_argument('--result', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    args = ap.parse_args()

    contract, result = load(args.contract), load(args.result)
    require(contract.get('paper_id') == PAPER_ID and contract.get('experiment_id') == EXPERIMENT_ID, 'contract identity drift')
    require(result.get('paper_id') == PAPER_ID and result.get('experiment_id') == EXPERIMENT_ID, 'result identity drift')
    require(result.get('status') == 'B8_EXECUTION_COMPLETE', 'B8 not complete')
    require(result.get('summary', {}).get('provider_calls_complete') == 144 and result.get('summary', {}).get('provider_failures') == 0, 'B8 execution geometry drift')
    cells = result.get('cell_results') or []
    require(len(cells) == 36, 'B8 cell count drift')

    tie_counts: Counter[str] = Counter()
    equality_counts: Counter[str] = Counter()
    rows = []
    for cell in cells:
        s = float(cell['success_memory_rate'])
        f = float(cell['failure_memory_rate'])
        r = float(cell['raw_trajectory_rate'])
        n = float(cell['no_memory_rate'])
        distances = {'success_memory': abs(r - s), 'failure_memory': abs(r - f), 'no_memory': abs(r - n)}
        minimum = min(distances.values())
        closest = sorted([name for name, value in distances.items() if abs(value - minimum) < 1e-12])
        tie_counts['+'.join(closest)] += 1

        if eq(s, f) and eq(f, r) and eq(r, n):
            pattern = 'S=F=R=N'
        elif eq(s, f) and eq(f, n) and not eq(r, n):
            pattern = 'S=F=N!=R'
        elif eq(s, f) and eq(f, r) and not eq(n, r):
            pattern = 'S=F=R!=N'
        elif eq(f, r) and eq(r, n) and not eq(s, r):
            pattern = 'F=R=N!=S'
        elif eq(s, r) and eq(r, n) and not eq(f, r):
            pattern = 'S=R=N!=F'
        else:
            pattern = 'OTHER'
        equality_counts[pattern] += 1
        rows.append({
            'future_task': int(cell['future_task']),
            'selected_source_task': int(cell['selected_source_task']),
            'rates': {'S': s, 'F': f, 'R': r, 'N': n},
            'raw_distance_to_arms': distances,
            'raw_closest_arms_tie_aware': closest,
            'four_arm_equality_pattern': pattern,
        })

    raw_equals_no_memory = sum(eq(float(x['raw_trajectory_rate']), float(x['no_memory_rate'])) for x in cells)
    raw_equals_success = sum(eq(float(x['raw_trajectory_rate']), float(x['success_memory_rate'])) for x in cells)
    raw_equals_failure = sum(eq(float(x['raw_trajectory_rate']), float(x['failure_memory_rate'])) for x in cells)
    any_raw_deviation = [x for x in rows if not (eq(x['rates']['R'], x['rates']['S']) and eq(x['rates']['R'], x['rates']['F']) and eq(x['rates']['R'], x['rates']['N']))]

    receipt = {
        'schema_version': '1.0',
        'artifact_type': 'b8-tie-aware-derived-geometry',
        'paper_id': PAPER_ID,
        'experiment_id': EXPERIMENT_ID,
        'status': 'DERIVED_GEOMETRY_COMPLETE_ZERO_PROVIDER_CALLS',
        'source_bindings': {
            'b8_contract': {'path': str(args.contract.resolve()), 'sha256': sha(args.contract)},
            'b8_result': {'path': str(args.result.resolve()), 'sha256': sha(args.result)},
            'builder': {'path': str(Path(__file__).resolve()), 'sha256': sha(Path(__file__).resolve())},
        },
        'provider_calls': 0,
        'purpose': 'Replace the runner secondary field raw_closest_arm_counts for interpretation because that field uses deterministic label tie-breaking and is therefore not tie-aware.',
        'runner_secondary_field_disposition': {
            'field': 'secondary.raw_closest_arm_counts',
            'use_in_manuscript': False,
            'reason': 'The runner selects one label with min(..., key=(distance,label)); exact distance ties are resolved lexicographically, which can make failure_memory appear uniquely closest when several arms are tied.',
            'scientific_primary_result_affected': False,
        },
        'tie_aware_closest_arm_counts': dict(sorted(tie_counts.items())),
        'four_arm_equality_pattern_counts': dict(sorted(equality_counts.items())),
        'exact_rate_equalities': {
            'raw_equals_no_memory_tasks': raw_equals_no_memory,
            'raw_equals_success_memory_tasks': raw_equals_success,
            'raw_equals_failure_memory_tasks': raw_equals_failure,
            'all_four_equal_tasks': equality_counts.get('S=F=R=N', 0),
            'any_raw_deviation_from_at_least_one_other_arm_tasks': len(any_raw_deviation),
        },
        'nontrivial_cells': any_raw_deviation,
        'primary_result_preserved': {
            'mean_absolute_rewrite_vs_raw_effect': result['summary']['observed_mean_absolute_rewrite_vs_raw_effect'],
            'permutation_p': result['summary']['three_arm_permutation_p_ge_observed'],
            'practical_effect_floor': result['summary']['practical_effect_floor'],
            'gate_pass': result['summary']['primary_gate_pass'],
            'decision': result['decision'],
        },
        'claim_expansion_authority': False,
        'scientific_authority': False,
        'submission_authority': False,
    }
    write_json(args.output, receipt)
    print(json.dumps({
        'status': receipt['status'],
        'tie_aware_closest_arm_counts': receipt['tie_aware_closest_arm_counts'],
        'four_arm_equality_pattern_counts': receipt['four_arm_equality_pattern_counts'],
        'exact_rate_equalities': receipt['exact_rate_equalities'],
        'primary_result_preserved': receipt['primary_result_preserved'],
    }, indent=2))


if __name__ == '__main__':
    main()
