#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path

PAPER_ID = 'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE'
EXPERIMENT_ID = 'D2-PROXY-B9-PARTIAL-REFERENCE-COVERAGE'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    obj = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(obj, dict):
        raise RuntimeError(f'JSON root must be object: {path}')
    return obj


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    os.replace(tmp, path)


def clean(answer: str | None) -> str:
    a = str(answer or '').strip()
    if len(a) >= 2 and a[0] == a[-1] and a[0] in "'\"":
        a = a[1:-1]
    return re.sub(r'(\w+)[\u2010-\u2015\u2212-](\w+)', r'\1-\2', a).lower()


def partial_score(answer: str, refs: dict) -> tuple[float, dict]:
    p = clean(answer)
    family_scores: list[float] = []
    checks: dict = {}
    if 'exact_match' in refs:
        ref = str(refs['exact_match'])
        v = float(p == clean(ref))
        family_scores.append(v)
        checks['exact_match'] = {'reference': ref, 'score': v}
    if 'must_include' in refs:
        values = []
        for ref in refs['must_include']:
            v = float(clean(str(ref)) in p)
            values.append({'reference': str(ref), 'score': v})
        fam = sum(x['score'] for x in values) / len(values) if values else 1.0
        family_scores.append(fam)
        checks['must_include'] = {'coverage': fam, 'items': values}
    score = 1.0
    for v in family_scores:
        score *= v
    return score, checks


def manifest_digest(directory: Path) -> tuple[int, str]:
    files = sorted(directory.glob('*.json'))
    rows = [{'name': p.name, 'sha256': sha(p)} for p in files]
    digest = hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return len(files), digest


def validate_contract(contract: dict, contract_path: Path) -> None:
    require(contract.get('paper_id') == PAPER_ID and contract.get('experiment_id') == EXPERIMENT_ID, 'identity drift')
    require(contract.get('status') == 'FROZEN_BEFORE_DIAGNOSTIC_COMPUTATION', 'contract not frozen')
    require(contract.get('inference_policy', {}).get('confirmatory_gate') is None, 'confirmatory gate unexpectedly added')
    require(contract.get('inference_policy', {}).get('p_value_claim') is False, 'p-value authority drift')
    require(contract.get('support', {}).get('provider_calls') == 0, 'provider call drift')
    for key in ['b4_contract', 'b4_result', 'b5_contract', 'b5_result', 'analyzer']:
        row = contract['source_bindings'][key]
        p = Path(row['path'])
        require(p.is_file() and sha(p) == row['sha256'], f'source binding drift: {key}')
    for key in ['b4_responses', 'b5_responses']:
        row = contract['source_bindings'][key]
        n, digest = manifest_digest(Path(row['path']))
        require(n == row['file_count'] and digest == row['manifest_sha256'], f'response manifest drift: {key}')
    analyzer = Path(contract['source_bindings']['analyzer']['path'])
    require(analyzer.resolve() == Path(__file__).resolve(), 'analyzer path drift')
    require(sha(analyzer) == contract['source_bindings']['analyzer']['sha256'], 'analyzer SHA drift')


def response_index(directory: Path, condition_map: dict[str, str]) -> dict[tuple[int, str, int], dict]:
    out: dict[tuple[int, str, int], dict] = {}
    for p in sorted(directory.glob('*.json')):
        r = load(p)
        raw_cond = str(r.get('condition') or '')
        if raw_cond not in condition_map:
            continue
        key = (int(r['future_task']), condition_map[raw_cond], int(r['rollout']))
        require(key not in out, f'duplicate response key: {key}')
        require(bool(str(r.get('answer') or '').strip()), f'empty archived answer: {p}')
        out[key] = r
    return out


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def r6(x: float) -> float:
    return round(float(x), 6)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--contract', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    args = ap.parse_args()
    c = load(args.contract)
    validate_contract(c, args.contract)

    b4c = load(Path(c['source_bindings']['b4_contract']['path']))
    b4r = load(Path(c['source_bindings']['b4_result']['path']))
    b5r = load(Path(c['source_bindings']['b5_result']['path']))
    b4_idx = response_index(Path(c['source_bindings']['b4_responses']['path']), {'success': 'success_memory', 'failure': 'failure_memory'})
    b5_idx = response_index(Path(c['source_bindings']['b5_responses']['path']), {'no_memory': 'no_memory'})
    idx = {**b4_idx, **b5_idx}
    require(len(b4_idx) == 288 and len(b5_idx) == 144 and len(idx) == 432, 'archive geometry drift')

    binary: dict[tuple[int, str, int], float] = {}
    for r in b4r['rollouts']:
        binary[(int(r['future_task']), f"{r['condition']}_memory", int(r['rollout']))] = float(r['benchmark_score'])
    for r in b5r['rollouts']:
        binary[(int(r['future_task']), 'no_memory', int(r['rollout']))] = float(r['benchmark_score'])
    require(len(binary) == 432, 'binary rollout geometry drift')

    refs_by_task = {int(u['future_task']): u['reference_answers'] for u in b4c['task_units']}
    source_by_task = {int(u['future_task']): int(u['selected_source_task']) for u in b4c['task_units']}
    template_by_task = {int(u['future_task']): int(u['intent_template_id']) for u in b4c['task_units']}
    rows = []
    for key in sorted(idx):
        tid, cond, rollout = key
        score, checks = partial_score(str(idx[key]['answer']), refs_by_task[tid])
        rows.append({
            'future_task': tid,
            'selected_source_task': source_by_task[tid],
            'intent_template_id': template_by_task[tid],
            'condition': cond,
            'rollout': rollout,
            'binary_score': binary[key],
            'partial_reference_coverage': r6(score),
            'answer_sha256': idx[key]['answer_sha256'],
            'checks': checks,
        })

    by_task_cond: dict[tuple[int, str], list[dict]] = {}
    for row in rows:
        by_task_cond.setdefault((row['future_task'], row['condition']), []).append(row)

    cells = []
    binary_same_partial_diff = 0
    binary_joint_floor = binary_joint_ceiling = 0
    partial_joint_floor = partial_joint_ceiling = 0
    for u in b4c['task_units']:
        tid = int(u['future_task'])
        vals = {}
        for cond in ['success_memory', 'failure_memory', 'no_memory']:
            rr = by_task_cond[(tid, cond)]
            require(len(rr) == 4, f'rollout count drift: {tid}/{cond}')
            vals[cond] = {
                'binary': mean([float(x['binary_score']) for x in rr]),
                'partial': mean([float(x['partial_reference_coverage']) for x in rr]),
            }
        binary_sf_same = abs(vals['success_memory']['binary'] - vals['failure_memory']['binary']) < 1e-12
        partial_sf_diff = abs(vals['success_memory']['partial'] - vals['failure_memory']['partial']) > 1e-12
        if binary_sf_same and partial_sf_diff:
            binary_same_partial_diff += 1
        if vals['success_memory']['binary'] == 0 and vals['failure_memory']['binary'] == 0:
            binary_joint_floor += 1
        if vals['success_memory']['binary'] == 1 and vals['failure_memory']['binary'] == 1:
            binary_joint_ceiling += 1
        if vals['success_memory']['partial'] == 0 and vals['failure_memory']['partial'] == 0:
            partial_joint_floor += 1
        if vals['success_memory']['partial'] == 1 and vals['failure_memory']['partial'] == 1:
            partial_joint_ceiling += 1
        refs = u.get('reference_answers') or {}
        nrefs = len(refs.get('must_include') or []) if 'must_include' in refs else 1
        cells.append({
            'future_task': tid,
            'selected_source_task': int(u['selected_source_task']),
            'intent_template_id': int(u['intent_template_id']),
            'reference_count': nrefs,
            'multi_reference': nrefs > 1,
            'success_binary': r6(vals['success_memory']['binary']),
            'failure_binary': r6(vals['failure_memory']['binary']),
            'no_memory_binary': r6(vals['no_memory']['binary']),
            'success_partial': r6(vals['success_memory']['partial']),
            'failure_partial': r6(vals['failure_memory']['partial']),
            'no_memory_partial': r6(vals['no_memory']['partial']),
            'success_minus_failure_partial': r6(vals['success_memory']['partial'] - vals['failure_memory']['partial']),
            'success_minus_no_memory_partial': r6(vals['success_memory']['partial'] - vals['no_memory']['partial']),
            'failure_minus_no_memory_partial': r6(vals['failure_memory']['partial'] - vals['no_memory']['partial']),
            'binary_sf_same_partial_diff': binary_sf_same and partial_sf_diff,
        })

    def summarize(subset: list[dict]) -> dict:
        return {
            'task_count': len(subset),
            'mean_absolute_success_failure_partial_difference': r6(mean([abs(x['success_partial'] - x['failure_partial']) for x in subset])),
            'mean_signed_success_minus_failure_partial': r6(mean([x['success_partial'] - x['failure_partial'] for x in subset])),
            'mean_absolute_memory_presence_partial_difference': r6(mean([(abs(x['success_partial'] - x['no_memory_partial']) + abs(x['failure_partial'] - x['no_memory_partial'])) / 2 for x in subset])),
            'mean_success_partial': r6(mean([x['success_partial'] for x in subset])),
            'mean_failure_partial': r6(mean([x['failure_partial'] for x in subset])),
            'mean_no_memory_partial': r6(mean([x['no_memory_partial'] for x in subset])),
            'nonzero_success_failure_partial_cells': sum(abs(x['success_partial'] - x['failure_partial']) > 1e-12 for x in subset),
        }

    all_summary = summarize(cells)
    multi_cells = [x for x in cells if x['multi_reference']]
    multi_summary = summarize(multi_cells)
    changed = sorted([x for x in cells if x['binary_sf_same_partial_diff']], key=lambda z: abs(z['success_minus_failure_partial']), reverse=True)

    result = {
        'schema_version': '1.0',
        'experiment_id': EXPERIMENT_ID,
        'paper_id': PAPER_ID,
        'status': 'B9_DIAGNOSTIC_COMPLETE',
        'contract_file_sha256': sha(args.contract),
        'contract_sha256': c['contract_sha256'],
        'provider_calls': 0,
        'rollout_count': len(rows),
        'summary_all_36': all_summary,
        'summary_multi_reference_16': multi_summary,
        'headroom': {
            'binary_joint_floor_cells': binary_joint_floor,
            'binary_joint_ceiling_cells': binary_joint_ceiling,
            'partial_joint_floor_cells': partial_joint_floor,
            'partial_joint_ceiling_cells': partial_joint_ceiling,
            'binary_same_but_partial_success_failure_diff_cells': binary_same_partial_diff,
        },
        'largest_binary_hidden_success_failure_partial_differences': changed[:12],
        'cell_results': cells,
        'rollouts': rows,
        'interpretation_guard': 'Post-hoc endpoint-headroom diagnostic only. Partial coverage does not replace the released binary evaluator, does not relax B4/B5 gates, and cannot retroactively establish native terminal transport.',
        'scientific_authority': False,
        'claim_expansion_authority': False,
        'submission_authority': False,
    }
    write_json(args.output, result)
    print(json.dumps({
        'status': result['status'],
        'provider_calls': 0,
        'summary_all_36': all_summary,
        'summary_multi_reference_16': multi_summary,
        'headroom': result['headroom'],
    }, indent=2))


if __name__ == '__main__':
    main()
