from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
INITIAL = Path('/data/wyt/agent-self-evolution-observatory/paper-acceptance-artifacts/D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE/f2-initial-terminal.json')
F2R1_RUN = Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-memory-variance-f2r1-20260822')
CONTRACT = F2R1_RUN / 'f2r1-contract.json'
AUTH = F2R1_RUN / 'scoped-authorization-receipt.json'
CONFIRM = Path('/data/wyt/agent-self-evolution-observatory/paper-acceptance-artifacts/D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE/f2r1-confirmatory.json')
INITIAL_COMMIT = '730c2bc3cb54db02c84a7379e0c780b98d6c992c'
INITIAL_GIT_RESULT = 'generated/d2-proxy-reward-terminal-fixed-evidence.json'
INITIAL_GIT_CONTRACT = 'generated/d2-proxy-reward-terminal-fixed-evidence-contract.json'
EXPECTED_INITIAL_SHA = 'f4bd5428887db58f7e2651248ba13458b686786bd80f71cf669bcd440655aeb6'
EXPECTED_F2R1_CONTRACT_SHA = 'ea9a2260858c9da50ddfea0c6cec7722112953a437853b6e4d55c4013dec01f5'
EXPECTED_F2R1_RESULT_SHA = '04db52a9c2a1eac28df4213e5041e2f20e8e4b3591d5941f9e6d889a8b8dc2e9'
EXPECTED_AUTH_SHA = '3cc970ee2e5d2f2570be13c1076054855d3b1a347f5648d3fa161bbee4142081'


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(p: Path) -> dict:
    d = json.loads(p.read_text(encoding='utf-8'))
    if not isinstance(d, dict):
        raise RuntimeError(f'JSON root not object: {p}')
    return d


def git_show(path: str) -> bytes:
    return subprocess.check_output(['git', 'show', f'{INITIAL_COMMIT}:{path}'])


def git_text(*args: str) -> str:
    return subprocess.check_output(['git', *args], text=True).strip()


def main() -> int:
    initial = load(INITIAL)
    contract = load(CONTRACT)
    auth = load(AUTH)
    confirm = load(CONFIRM)
    if sha(INITIAL) != EXPECTED_INITIAL_SHA:
        raise RuntimeError('initial result SHA drift')
    if sha(CONTRACT) != EXPECTED_F2R1_CONTRACT_SHA:
        raise RuntimeError('F2R1 contract SHA drift')
    if sha(CONFIRM) != EXPECTED_F2R1_RESULT_SHA:
        raise RuntimeError('F2R1 result SHA drift')
    if sha(AUTH) != EXPECTED_AUTH_SHA:
        raise RuntimeError('F2R1 auth SHA drift')

    git_initial_result = git_show(INITIAL_GIT_RESULT)
    git_initial_contract = git_show(INITIAL_GIT_CONTRACT)
    if hashlib.sha256(git_initial_result).hexdigest() != EXPECTED_INITIAL_SHA:
        raise RuntimeError('git-committed initial result differs from acceptance artifact')
    initial_contract = json.loads(git_initial_contract)
    if initial_contract['terminal_gate']['alpha'] != 0.05 or initial_contract['terminal_gate']['min_mean_absolute_success_rate_difference'] != 0.15:
        raise RuntimeError('initial gate drift')
    if initial_contract['source_memory_tasks'] != contract['source_memory_tasks'] or initial_contract['future_tasks'] != contract['future_tasks']:
        raise RuntimeError('support changed between initial and F2R1')
    if contract['terminal_gate']['alpha'] != 0.05 or contract['terminal_gate']['min_mean_absolute_success_rate_difference'] != 0.15:
        raise RuntimeError('F2R1 gate drift')
    if contract['design']['no_source_or_future_task_selection_after_outcomes'] is not True:
        raise RuntimeError('F2R1 selection guard missing')

    commit_time = git_text('show', '-s', '--format=%aI', INITIAL_COMMIT)
    receipts = []
    for p in (F2R1_RUN / 'provider-cache/provider-receipts').rglob('*.json'):
        try:
            d = load(p)
            t = str(d.get('generated_at') or '')
            if t:
                receipts.append((t, p))
        except Exception:
            pass
    if not receipts:
        raise RuntimeError('no F2R1 provider receipts')
    first_time, first_path = min(receipts, key=lambda x: x[0])

    imap = {(str(r['source_memory_task']), str(r['future_task'])): r for r in initial['cell_results']}
    cmap = {(str(r['source_memory_task']), str(r['future_task'])): r for r in confirm['cell_results']}
    expected = {(s, f) for s in contract['source_memory_tasks'] for f in contract['future_tasks']}
    if set(imap) != expected or set(cmap) != expected:
        raise RuntimeError('cell support mismatch')
    cells = []
    for s in contract['source_memory_tasks']:
        for f in contract['future_tasks']:
            a, b = imap[(s, f)], cmap[(s, f)]
            cells.append({
                'source_memory_task': s,
                'future_task': f,
                'initial_success_rate_n3': a['success_memory_rate'],
                'initial_failure_rate_n3': a['failure_memory_rate'],
                'initial_abs_delta': a['absolute_rate_difference'],
                'initial_signed_failure_minus_success': a['signed_failure_minus_success'],
                'confirm_success_rate_n8': b['success_memory_rate'],
                'confirm_failure_rate_n8': b['failure_memory_rate'],
                'confirm_abs_delta': b['absolute_rate_difference'],
                'confirm_signed_failure_minus_success': b['signed_failure_minus_success'],
            })

    payload = {
        'schema_version': '1.0',
        'artifact_type': 'f2-to-f2r1-confirmatory-chronology-receipt',
        'paper_id': 'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE',
        'status': 'CHRONOLOGY_AND_UNIFORM_REPLICATION_VERIFIED',
        'initial_stage': {
            'experiment_id': initial['experiment_id'],
            'result_sha256': EXPECTED_INITIAL_SHA,
            'contract_sha256_recorded_by_result': initial['contract_sha256'],
            'git_commit': INITIAL_COMMIT,
            'git_commit_time': commit_time,
            'git_contract_path': INITIAL_GIT_CONTRACT,
            'git_result_path': INITIAL_GIT_RESULT,
            'rollouts_per_cell_per_condition': 3,
            'source_memory_tasks': initial_contract['source_memory_tasks'],
            'future_tasks': initial_contract['future_tasks'],
            'effect_floor': initial_contract['terminal_gate']['min_mean_absolute_success_rate_difference'],
            'alpha': initial_contract['terminal_gate']['alpha'],
            'mean_absolute_effect': initial['summary']['observed_mean_absolute_success_rate_difference'],
            'permutation_p': initial['summary']['permutation_p_ge_observed'],
            'gate_pass': initial['summary']['gate_pass'],
        },
        'confirmatory_stage': {
            'experiment_id': contract['experiment_id'],
            'authorization_sha256': EXPECTED_AUTH_SHA,
            'contract_sha256': EXPECTED_F2R1_CONTRACT_SHA,
            'result_sha256': EXPECTED_F2R1_RESULT_SHA,
            'first_provider_receipt_generated_at': first_time,
            'first_provider_receipt_sha256': sha(first_path),
            'rollouts_per_cell_per_condition': contract['rollouts_per_cell'],
            'source_memory_tasks': contract['source_memory_tasks'],
            'future_tasks': contract['future_tasks'],
            'effect_floor': contract['terminal_gate']['min_mean_absolute_success_rate_difference'],
            'alpha': contract['terminal_gate']['alpha'],
            'permutation_repetitions': contract['terminal_gate']['permutation_repetitions'],
            'no_source_or_future_task_selection_after_outcomes': contract['design']['no_source_or_future_task_selection_after_outcomes'],
            'mean_absolute_effect': confirm['summary']['observed_mean_absolute_success_rate_difference'],
            'permutation_p': confirm['summary']['permutation_p_ge_observed'],
            'gate_pass': confirm['summary']['gate_pass'],
        },
        'relationship': {
            'confirmatory_was_designed_after_initial_nonpass': True,
            'same_4x4_support': True,
            'source_selection_changed': False,
            'future_task_selection_changed': False,
            'effect_floor_changed': False,
            'alpha_changed': False,
            'replication_depth_changed': '3 -> 8 per cell per condition',
            'correct_interpretation': 'F2R1 is a targeted uniform replication after an initial non-pass, intended to increase statistical resolution on the same frozen support. It is not the first outcome-blind terminal experiment, and it did not select cells or relax the dual gate after seeing initial outcomes.',
        },
        'cell_comparison': cells,
        'scientific_authority': False,
        'experiment_authority': False,
        'claim_expansion_authority': False,
        'new_provider_calls': 0,
    }
    out = HERE / 'f2r1-chronology-receipt.json'
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({
        'status': payload['status'],
        'initial_commit_time': commit_time,
        'f2r1_first_provider_receipt': first_time,
        'same_4x4_support': True,
        'effect_floor_unchanged': True,
        'alpha_unchanged': True,
        'cells': len(cells),
    }, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
