#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

PAPER_ID = 'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE'
EXPERIMENT_ID = 'D2-PROXY-B11-OUTCOME-BLIND-PROCEDURAL-WRITER'
MODEL = 'doubao-seed-2.0-mini'
RESOLVED = 'doubao-seed-2-0-mini-260215'
BASE_URL = 'https://ark.cn-beijing.volces.com/api/plan/v3'
N = 4
TOTAL = 144


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tsha(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def load(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(obj, dict):
        raise RuntimeError(f'JSON root must be object: {path}')
    return obj


def writej(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    os.replace(tmp, path)


def req(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def clean(answer: str | None) -> str:
    value = str(answer or '').strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        value = value[1:-1]
    return re.sub(r'(\w+)[\u2010-\u2015\u2212-](\w+)', r'\1-\2', value).lower()


def score(prediction: str, refs: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    p = clean(prediction)
    score_value = 1.0
    checks: dict[str, Any] = {}
    if 'exact_match' in refs:
        ref = str(refs['exact_match'])
        v = float(p == clean(ref))
        score_value *= v
        checks['exact_match'] = {'ref': ref, 'score': v}
    if 'must_include' in refs:
        out = []
        for ref in refs['must_include']:
            v = float(clean(str(ref)) in p)
            score_value *= v
            out.append({'ref': str(ref), 'score': v})
        checks['must_include'] = out
    return score_value, checks


def evidence(trajectory_json: str) -> tuple[str, list[str]]:
    trajectory = json.loads(trajectory_json)
    states: list[str] = []
    hashes: list[str] = []
    seen: set[str] = set()
    for step in (trajectory.get('steps') or {}).values():
        contents = ((step.get('input_messages') or {}).get('contents') or [])
        if not contents:
            continue
        text = str(contents[-1].get('content') or '')
        if '[Current state starts here]' not in text:
            continue
        text = text.split('[Current state starts here]', 1)[1].strip()
        digest = tsha(text)
        if digest in seen:
            continue
        seen.add(digest)
        states.append(text)
        hashes.append(digest)
    return '\n\n--- RELEASED BROWSER STATE ---\n\n'.join(states), hashes


def prompt(task: str, ev: str, wrapper: str) -> str:
    return f"""{wrapper.rstrip()}

You are answering a WebArena read-only benchmark task from a frozen released evidence packet.

RULES:
- Treat the memory above as procedural guidance from a past task, not task-specific ground truth.
- Use only the RELEASED BROWSER EVIDENCE below as factual evidence for the current task.
- Do not invent names, prices, order values, product facts, ratings, or quotes absent from the evidence.
- Return only the final answer to the benchmark task. Do not return JSON, browser actions, analysis, or commentary.

BENCHMARK TASK:
{task}

RELEASED BROWSER EVIDENCE:
{ev}

FINAL ANSWER:"""


def stage(unit: dict[str, Any], rollout: int) -> str:
    return f"neutral-terminal-{unit['future_task']}-source-{unit['selected_source_task']}-r{rollout}"


def validate(contract: dict[str, Any], manifest: dict[str, Any]) -> None:
    req(contract.get('paper_id') == PAPER_ID and contract.get('experiment_id') == EXPERIMENT_ID, 'contract identity drift')
    req(contract.get('status') == 'FROZEN_BEFORE_ANY_B11_PROVIDER_CALLS', 'master contract not frozen')
    t = contract['terminal_stage']
    req(t['expected_provider_calls'] == TOTAL and t['future_task_count'] == 36 and t['rollouts_per_task'] == N, 'terminal geometry drift')
    model = t['model']
    req(model['requested'] == MODEL and model['expected_resolved'] == RESOLVED and float(model['temperature']) == 0.2 and int(model['max_output_tokens']) == 900 and model['thinking'] == 'disabled' and int(model['provider_retries']) == 0 and model['substitution_allowed'] is False, 'terminal model drift')
    gate = t['primary_gate']
    req(gate['min_mean_absolute_reward_conditioned_vs_neutral_effect'] == 0.15 and gate['permutation_p_lt'] == 0.05 and gate['permutation_repetitions'] == 100000 and gate['permutation_seed'] == 20260824, 'primary gate drift')
    authority = contract['authority']
    req(authority['experiment_authority'] is True and authority['provider_call_authority'] is True and authority['claim_expansion_authority'] is False, 'authority drift')
    for key in ['trajectory_parquet', 'b4_contract', 'b4_result', 'b5_result', 'b8_result', 'human_authority']:
        row = contract['source_bindings'][key]
        path = Path(row['path'])
        req(path.is_file() and sha(path) == row['sha256'], f'source binding drift: {key}')
    runner = Path(contract['code']['terminal_runner']['path'])
    req(runner.resolve() == Path(__file__).resolve() and sha(runner) == contract['code']['terminal_runner']['sha256'], 'terminal runner SHA drift')
    req(manifest.get('paper_id') == PAPER_ID and manifest.get('experiment_id') == EXPERIMENT_ID, 'manifest identity drift')
    req(manifest.get('status') == 'B11_NEUTRAL_MEMORY_MANIFEST_READY' and manifest.get('terminal_stage_may_activate') is True, 'manifest not terminal-ready')
    req(manifest.get('contract_sha256') == contract.get('contract_sha256'), 'manifest master-contract binding drift')
    req(manifest.get('required_native_source_count') == 11 and manifest.get('memory_object_count') == 20, 'manifest geometry drift')


def runtime(contract: dict[str, Any]):
    root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(Path(contract['vendor_path'])))
    import pyarrow.parquet as pq  # type: ignore
    from research_pipeline.config import load_env_file
    from research_pipeline.ark_provider import ArkResponseStateError, ArkResponsesClient, ArkSettings

    load_env_file(Path(contract['provider_env_file']))
    base = ArkSettings.from_env()
    req(bool(base.api_key), 'provider credential unavailable')
    req(base.base_url == BASE_URL, 'provider base URL drift')
    settings = ArkSettings(api_key=base.api_key, base_url=base.base_url, default_model=base.default_model, timeout_seconds=180.0, max_retries=0)
    return pq, ArkResponseStateError, ArkResponsesClient(settings), settings.safe_summary()


def task_data(contract: dict[str, Any], manifest: dict[str, Any], pq) -> dict[int, dict[str, Any]]:
    parquet = Path(contract['source_bindings']['trajectory_parquet']['path'])
    rows = {int(x['task_id']): x for x in pq.read_table(parquet, columns=['task_id', 'trajectory_json']).to_pylist()}
    neutral = {int(x['source_task']): x for x in manifest['objects']}
    out: dict[int, dict[str, Any]] = {}
    for unit in contract['terminal_stage']['task_units']:
        tid = int(unit['future_task'])
        source = int(unit['selected_source_task'])
        req(tid in rows and source in neutral, f'task/source missing: {tid}/{source}')
        ev, state_hashes = evidence(str(rows[tid]['trajectory_json']))
        req(tsha(ev) == unit['evidence_sha256'] and state_hashes == unit['released_state_sha256'], f'evidence drift: {tid}')
        wrapper_path = Path(neutral[source]['native_wrapper_path'])
        req(wrapper_path.is_file() and tsha(wrapper_path.read_text(encoding='utf-8')) == neutral[source]['native_wrapper_sha256'], f'neutral wrapper drift: {source}')
        out[tid] = {'task_prompt': unit['task_prompt'], 'evidence': ev, 'refs': unit['reference_answers'], 'wrapper': wrapper_path.read_text(encoding='utf-8')}
    return out


def run_one(client, error_type, unit: dict[str, Any], rollout: int, data: dict[str, Any], root: Path) -> tuple[dict[str, Any], bool]:
    name = stage(unit, rollout)
    stage_path = root / 'stages' / f'{name}.json'
    if stage_path.is_file():
        return load(stage_path), False
    pr = prompt(data['task_prompt'], data['evidence'], data['wrapper'])
    base = {
        'stage': name,
        'future_task': int(unit['future_task']),
        'selected_source_task': int(unit['selected_source_task']),
        'condition': 'outcome_blind_procedural',
        'rollout': rollout,
        'prompt_sha256': tsha(pr),
        'requested_model': MODEL,
    }
    try:
        response = client.respond(pr, model=MODEL, max_output_tokens=900, temperature=0.2, thinking='disabled', store=True, allow_thinking_compatibility_fallback=False)
        answer = str(response.get('text') or '').strip()
        writej(root / 'provider-responses' / f'{name}.json', {
            **base,
            'response_id': response.get('response_id'),
            'provider_status': response.get('status'),
            'requested_model_returned': response.get('requested_model'),
            'resolved_model': response.get('resolved_model'),
            'usage': response.get('usage') or {},
            'answer': answer,
            'answer_sha256': tsha(answer) if answer else '',
            'thinking_compatibility_fallback': response.get('thinking_compatibility_fallback'),
        })
        req(str(response.get('requested_model')) == MODEL and str(response.get('resolved_model')) == RESOLVED, 'model resolution drift')
        req(response.get('thinking_compatibility_fallback') is False and bool(answer), 'empty/fallback response')
        benchmark_score, checks = score(answer, data['refs'])
        row = {
            **base,
            'status': 'complete',
            'provider_status': response.get('status'),
            'resolved_model': response.get('resolved_model'),
            'usage': response.get('usage') or {},
            'answer_sha256': tsha(answer),
            'benchmark_score': benchmark_score,
            'evaluator_checks': checks,
        }
    except error_type as exc:
        row = {**base, 'status': 'provider_state_failure_no_text', 'error_type': type(exc).__name__, 'provider_receipt': exc.receipt()}
    except Exception as exc:
        row = {**base, 'status': 'provider_or_runtime_failure', 'error_type': type(exc).__name__, 'error': str(exc)[:1000]}
    writej(stage_path, row)
    return row, True


def all_rows(contract: dict[str, Any], root: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for unit in contract['terminal_stage']['task_units']:
        for rollout in range(1, N + 1):
            path = root / 'stages' / f'{stage(unit, rollout)}.json'
            if path.is_file():
                out.append(load(path))
    return out


def existing_arms(contract: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    return load(Path(contract['source_bindings']['b4_result']['path'])), load(Path(contract['source_bindings']['b5_result']['path'])), load(Path(contract['source_bindings']['b8_result']['path']))


def combined_cells(contract: dict[str, Any], neutral_rows: list[dict[str, Any]]) -> tuple[float, list[dict[str, Any]]]:
    b4, b5, b8 = existing_arms(contract)
    cells = []
    for unit in contract['terminal_stage']['task_units']:
        tid = int(unit['future_task'])
        success = [float(x['benchmark_score']) for x in b4['rollouts'] if int(x['future_task']) == tid and x['condition'] == 'success']
        failure = [float(x['benchmark_score']) for x in b4['rollouts'] if int(x['future_task']) == tid and x['condition'] == 'failure']
        neutral = [float(x['benchmark_score']) for x in neutral_rows if int(x['future_task']) == tid and x.get('status') == 'complete']
        no_memory = [float(x['benchmark_score']) for x in b5['rollouts'] if int(x['future_task']) == tid]
        raw = [float(x['benchmark_score']) for x in b8['rollouts'] if int(x['future_task']) == tid]
        req(len(success) == len(failure) == len(neutral) == len(no_memory) == len(raw) == N, f'arm count drift: {tid}')
        ps, pf, pn, p0, pr = (sum(success) / N, sum(failure) / N, sum(neutral) / N, sum(no_memory) / N, sum(raw) / N)
        primary = (abs(ps - pn) + abs(pf - pn)) / 2
        distances = {
            'success_memory': abs(pn - ps),
            'failure_memory': abs(pn - pf),
            'raw_trajectory': abs(pn - pr),
            'no_memory': abs(pn - p0),
        }
        minimum = min(distances.values())
        closest = sorted([name for name, value in distances.items() if abs(value - minimum) < 1e-12])
        cells.append({
            'future_task': tid,
            'selected_source_task': int(unit['selected_source_task']),
            'intent_template_id': int(unit['intent_template_id']),
            'success_memory_rate': round(ps, 6),
            'failure_memory_rate': round(pf, 6),
            'neutral_memory_rate': round(pn, 6),
            'raw_trajectory_rate': round(pr, 6),
            'no_memory_rate': round(p0, 6),
            'reward_conditioned_vs_neutral_effect': round(primary, 6),
            'neutral_vs_raw_absolute_difference': round(abs(pn - pr), 6),
            'neutral_vs_no_memory_absolute_difference': round(abs(pn - p0), 6),
            'neutral_closest_arms_tie_aware': closest,
        })
    observed = sum(x['reward_conditioned_vs_neutral_effect'] for x in cells) / len(cells)
    return observed, cells


def permutation(contract: dict[str, Any], neutral_rows: list[dict[str, Any]], observed: float) -> float:
    b4, _, _ = existing_arms(contract)
    pools = []
    for unit in contract['terminal_stage']['task_units']:
        tid = int(unit['future_task'])
        success = [float(x['benchmark_score']) for x in b4['rollouts'] if int(x['future_task']) == tid and x['condition'] == 'success']
        failure = [float(x['benchmark_score']) for x in b4['rollouts'] if int(x['future_task']) == tid and x['condition'] == 'failure']
        neutral = [float(x['benchmark_score']) for x in neutral_rows if int(x['future_task']) == tid]
        pools.append(success + failure + neutral)
    rng = random.Random(20260824)
    ge = 0
    repetitions = int(contract['terminal_stage']['primary_gate']['permutation_repetitions'])
    for _ in range(repetitions):
        values = []
        for pool in pools:
            z = list(pool)
            rng.shuffle(z)
            ps, pf, pn = sum(z[:4]) / 4, sum(z[4:8]) / 4, sum(z[8:12]) / 4
            values.append((abs(ps - pn) + abs(pf - pn)) / 2)
        if sum(values) / len(values) >= observed - 1e-12:
            ge += 1
    return (ge + 1) / (repetitions + 1)


def report(contract: dict[str, Any], manifest: dict[str, Any], root: Path, provider: dict[str, Any], new_calls: int) -> dict[str, Any]:
    rows = all_rows(contract, root)
    failures = [r for r in rows if r.get('status') != 'complete']
    full = len(rows) == TOTAL and not failures
    observed = pvalue = None
    cells: list[dict[str, Any]] = []
    gate_pass = False
    secondary: dict[str, Any] = {}
    if full:
        observed, cells = combined_cells(contract, rows)
        pvalue = permutation(contract, rows, observed)
        gate = contract['terminal_stage']['primary_gate']
        gate_pass = observed >= float(gate['min_mean_absolute_reward_conditioned_vs_neutral_effect']) and pvalue < float(gate['permutation_p_lt'])
        secondary = {
            'mean_absolute_neutral_vs_raw': round(sum(x['neutral_vs_raw_absolute_difference'] for x in cells) / len(cells), 6),
            'mean_absolute_neutral_vs_no_memory': round(sum(x['neutral_vs_no_memory_absolute_difference'] for x in cells) / len(cells), 6),
            'all_five_arms_equal_tasks': sum(x['success_memory_rate'] == x['failure_memory_rate'] == x['neutral_memory_rate'] == x['raw_trajectory_rate'] == x['no_memory_rate'] for x in cells),
            'neutral_equals_success_tasks': sum(x['neutral_memory_rate'] == x['success_memory_rate'] for x in cells),
            'neutral_equals_failure_tasks': sum(x['neutral_memory_rate'] == x['failure_memory_rate'] for x in cells),
            'neutral_equals_raw_tasks': sum(x['neutral_memory_rate'] == x['raw_trajectory_rate'] for x in cells),
            'neutral_equals_no_memory_tasks': sum(x['neutral_memory_rate'] == x['no_memory_rate'] for x in cells),
            'neutral_closest_arms_tie_aware_counts': dict(Counter('+'.join(x['neutral_closest_arms_tie_aware']) for x in cells)),
            'by_selected_source_mean_effect': {str(source): round(sum(x['reward_conditioned_vs_neutral_effect'] for x in cells if x['selected_source_task'] == source) / sum(x['selected_source_task'] == source for x in cells), 6) for source in sorted({x['selected_source_task'] for x in cells})},
            'interpretation_guard': 'Secondary five-arm geometry is descriptive. Only the preregistered S/F-versus-neutral statistic and dual gate have confirmatory authority.',
        }
    decision = 'SUPPORT_PRACTICALLY_LARGE_REWARD_CONDITIONED_EFFECT_BEYOND_NEUTRAL_REWRITE' if gate_pass else ('REWARD_CONDITIONED_EFFECT_BEYOND_NEUTRAL_REWRITE_NOT_ESTABLISHED' if full else 'B11_TERMINAL_INCOMPLETE_NO_SCIENTIFIC_VERDICT')
    return {
        'schema_version': '1.0',
        'experiment_id': EXPERIMENT_ID,
        'paper_id': PAPER_ID,
        'status': 'B11_TERMINAL_EXECUTION_COMPLETE' if full else 'B11_TERMINAL_EXECUTION_PARTIAL',
        'contract_sha256': contract['contract_sha256'],
        'neutral_manifest_sha256': sha(Path(manifest['_loaded_from_path'])) if manifest.get('_loaded_from_path') else None,
        'provider': provider,
        'summary': {
            'provider_calls_expected': TOTAL,
            'provider_calls_attempted_total': len(rows),
            'provider_calls_complete': sum(r.get('status') == 'complete' for r in rows),
            'provider_failures': len(failures),
            'new_provider_calls_this_invocation': new_calls,
            'future_tasks': 36,
            'observed_mean_absolute_reward_conditioned_vs_neutral_effect': None if observed is None else round(observed, 6),
            'permutation_p_ge_observed': None if pvalue is None else round(pvalue, 6),
            'practical_effect_floor': 0.15,
            'primary_gate_pass': gate_pass,
        },
        'writer_geometry': manifest['writer_geometry'],
        'secondary': secondary,
        'cell_results': cells,
        'rollouts': [{k: r.get(k) for k in ('future_task', 'selected_source_task', 'condition', 'rollout', 'answer_sha256', 'benchmark_score', 'provider_status', 'resolved_model', 'usage')} for r in rows if r.get('status') == 'complete'],
        'failures': [{k: r.get(k) for k in ('future_task', 'selected_source_task', 'condition', 'rollout', 'stage', 'status', 'error_type', 'provider_receipt', 'error')} for r in failures],
        'decision': decision,
        'claim_boundary': contract['claim_boundary'],
        'scientific_authority': False,
        'experiment_authority': True,
        'claim_expansion_authority': False,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--contract', required=True, type=Path)
    ap.add_argument('--neutral-manifest', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--private-root', required=True, type=Path)
    ap.add_argument('--max-new-calls', type=int, default=8)
    args = ap.parse_args()
    contract = load(args.contract)
    manifest = load(args.neutral_manifest)
    manifest['_loaded_from_path'] = str(args.neutral_manifest.resolve())
    validate(contract, manifest)
    req(1 <= args.max_new_calls <= TOTAL, 'invalid max-new-calls')
    args.private_root.mkdir(parents=True, exist_ok=True)
    lock = (args.private_root / 'transaction.lock').open('a+')
    try:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print(json.dumps({'status': 'TRANSACTION_ALREADY_RUNNING', 'provider_calls_executed_by_this_process': 0}))
        return 3
    try:
        pq, error_type, client, provider_summary = runtime(contract)
        data = task_data(contract, manifest, pq)
        new_calls = 0
        stop = False
        for unit in contract['terminal_stage']['task_units']:
            if stop:
                break
            task = data[int(unit['future_task'])]
            for rollout in range(1, N + 1):
                stage_path = args.private_root / 'stages' / f'{stage(unit, rollout)}.json'
                if not stage_path.is_file() and new_calls >= args.max_new_calls:
                    stop = True
                    break
                row, is_new = run_one(client, error_type, unit, rollout, task, args.private_root)
                new_calls += int(is_new)
                writej(args.output, report(contract, manifest, args.private_root, provider_summary, new_calls))
                if is_new:
                    print(json.dumps({'stage': row['stage'], 'status': row['status'], 'new_calls_this_invocation': new_calls, 'attempted_total': len(all_rows(contract, args.private_root))}), flush=True)
                if row.get('status') != 'complete':
                    stop = True
                    break
        out = report(contract, manifest, args.private_root, provider_summary, new_calls)
        writej(args.output, out)
        print(json.dumps({'status': out['status'], 'summary': out['summary'], 'decision': out['decision']}, indent=2))
        return 2 if any(r.get('status') != 'complete' for r in all_rows(contract, args.private_root)) else 0
    finally:
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        lock.close()


if __name__ == '__main__':
    raise SystemExit(main())
