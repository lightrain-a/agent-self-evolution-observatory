#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
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


def response_manifest(directory: Path) -> dict:
    files = sorted(directory.glob('*.json'))
    require(files, f'no provider response files: {directory}')
    rows = [{'name': p.name, 'sha256': sha(p)} for p in files]
    digest = hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return {'path': str(directory.resolve()), 'file_count': len(files), 'manifest_sha256': digest, 'files': rows}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--b4-contract', required=True, type=Path)
    ap.add_argument('--b4-result', required=True, type=Path)
    ap.add_argument('--b4-responses', required=True, type=Path)
    ap.add_argument('--b5-contract', required=True, type=Path)
    ap.add_argument('--b5-result', required=True, type=Path)
    ap.add_argument('--b5-responses', required=True, type=Path)
    ap.add_argument('--analyzer', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    args = ap.parse_args()

    b4c, b4r = load(args.b4_contract), load(args.b4_result)
    b5c, b5r = load(args.b5_contract), load(args.b5_result)
    require(b4c.get('paper_id') == PAPER_ID and b4r.get('paper_id') == PAPER_ID, 'B4 paper identity drift')
    require(b5c.get('paper_id') == PAPER_ID and b5r.get('paper_id') == PAPER_ID, 'B5 paper identity drift')
    require(b4r.get('status') == 'B4_EXECUTION_COMPLETE' and b4r.get('summary', {}).get('provider_calls_complete') == 288, 'B4 incomplete')
    require(b5r.get('status') == 'B5_EXECUTION_COMPLETE' and b5r.get('summary', {}).get('provider_calls_complete') == 144, 'B5 incomplete')
    require(len(b4c.get('task_units') or []) == 36 and len(b5c.get('task_units') or []) == 36, 'task support drift')
    require([u['future_task'] for u in b4c['task_units']] == [u['future_task'] for u in b5c['task_units']], 'B4/B5 task order drift')
    require(args.analyzer.is_file(), 'analyzer missing')

    b4m = response_manifest(args.b4_responses)
    b5m = response_manifest(args.b5_responses)
    require(b4m['file_count'] == 288 and b5m['file_count'] == 144, 'response archive incomplete')

    multi = []
    for u in b4c['task_units']:
        refs = u.get('reference_answers') or {}
        n = len(refs.get('must_include') or [])
        if n > 1:
            multi.append(int(u['future_task']))

    contract = {
        'schema_version': '1.0',
        'experiment_id': EXPERIMENT_ID,
        'paper_id': PAPER_ID,
        'status': 'FROZEN_BEFORE_DIAGNOSTIC_COMPUTATION',
        'frozen_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        'diagnostic_class': 'POST_HOC_ENDPOINT_HEADROOM_DIAGNOSTIC',
        'question': 'Does the exact-match/all-references binary evaluator hide condition-associated partial correctness on the same archived B4/B5 rollouts?',
        'motivation_boundary': 'B4/B5 binary endpoint saturation was observed before this metric was introduced; therefore this unit is diagnostic only and cannot retroactively rescue the preregistered binary terminal gates.',
        'metric': {
            'name': 'partial_reference_coverage',
            'must_include': 'fraction of required reference strings contained after the same normalization used by the binary evaluator',
            'exact_match': 'unchanged binary exact-match score',
            'mixed_reference_policy': 'multiplicative across reference families if both are present; current 36-task support is audited explicitly',
            'range': [0.0, 1.0],
        },
        'support': {
            'future_task_count': 36,
            'multi_reference_task_count': len(multi),
            'multi_reference_tasks': multi,
            'conditions': ['success_memory', 'failure_memory', 'no_memory'],
            'rollouts_per_task_per_condition': 4,
            'provider_calls': 0,
        },
        'planned_outputs': [
            'per-rollout partial-reference coverage',
            'per-task arm means',
            'mean absolute success-vs-failure coverage difference over all 36 tasks',
            'mean absolute memory-presence coverage difference relative to no-memory over all 36 tasks',
            'the same two statistics over the frozen multi-reference subset',
            'count of cells where binary arm means are identical but partial-reference means differ',
            'joint binary floor/ceiling versus partial-reference headroom summary',
        ],
        'inference_policy': {
            'confirmatory_gate': None,
            'p_value_claim': False,
            'effect_threshold_claim': False,
            'use': 'mechanism/endpoint diagnostic and future-experiment design only',
        },
        'source_bindings': {
            'b4_contract': {'path': str(args.b4_contract.resolve()), 'sha256': sha(args.b4_contract)},
            'b4_result': {'path': str(args.b4_result.resolve()), 'sha256': sha(args.b4_result)},
            'b5_contract': {'path': str(args.b5_contract.resolve()), 'sha256': sha(args.b5_contract)},
            'b5_result': {'path': str(args.b5_result.resolve()), 'sha256': sha(args.b5_result)},
            'b4_responses': b4m,
            'b5_responses': b5m,
            'analyzer': {'path': str(args.analyzer.resolve()), 'sha256': sha(args.analyzer)},
        },
        'authority': {
            'provider_call_authority_required': False,
            'experiment_authority': True,
            'scientific_authority': False,
            'claim_expansion_authority': False,
            'submission_authority': False,
        },
        'scope_boundary': {
            'does_not_change_binary_evaluator': True,
            'does_not_relax_B4_or_B5_gate': True,
            'does_not_select_tasks_using_partial_coverage': True,
            'does_not_establish_live_browser_transport': True,
            'does_not_establish_population_effect': True,
        },
    }
    raw = dict(contract)
    contract['contract_sha256'] = hashlib.sha256(json.dumps(raw, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    write_json(args.output, contract)
    print(json.dumps({
        'status': contract['status'],
        'contract_sha256': contract['contract_sha256'],
        'future_task_count': 36,
        'multi_reference_task_count': len(multi),
        'provider_calls': 0,
    }, indent=2))


if __name__ == '__main__':
    main()
