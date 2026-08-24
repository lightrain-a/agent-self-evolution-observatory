#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

PAPER_ID = 'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE'
EXPERIMENT_ID = 'D2-PROXY-B11-OUTCOME-BLIND-PROCEDURAL-WRITER'
MODEL = 'deepseek-v4-flash'
BASE_URL = 'https://ark.cn-beijing.volces.com/api/plan/v3'
EXPECTED_WRITER_CALLS = 20
MAX_OUTPUT_TOKENS = 4096


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


def writej(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    os.replace(tmp, path)


def req(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


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


def writer_prompt(system_prompt: str, task: str, trajectory: str) -> str:
    return f"""{system_prompt.strip()}\n\nTask: {task}\n\nTrajectory:\n{trajectory}\n\nCreate memory items for the task above. Return only the requested Markdown memory-item format."""


def parse_items(text: str) -> list[dict[str, str]]:
    blocks = re.split(r'(?m)^# Memory Item \d+\s*$', str(text or ''))
    out: list[dict[str, str]] = []
    for block in blocks:
        if not block.strip():
            continue
        m1 = re.search(r'(?m)^## Title:\s*(.+?)\s*$', block)
        m2 = re.search(r'(?m)^## Description:\s*(.+?)\s*$', block)
        m3 = re.search(r'(?ms)^## Content:\s*(.+?)\s*$', block)
        if m1 and m2 and m3:
            out.append({'title': m1.group(1).strip(), 'description': m2.group(1).strip(), 'content': m3.group(1).strip()})
    return out


def normalized_model(value: str) -> str:
    return re.sub(r'[^a-z0-9]', '', str(value or '').lower())


def validate_contract(contract: dict[str, Any]) -> None:
    req(contract.get('schema_version') == '1.0', 'schema drift')
    req(contract.get('paper_id') == PAPER_ID and contract.get('experiment_id') == EXPERIMENT_ID, 'identity drift')
    req(contract.get('status') == 'FROZEN_BEFORE_ANY_B11_PROVIDER_CALLS', 'contract not frozen')
    req(contract.get('writer_stage', {}).get('expected_provider_calls') == EXPECTED_WRITER_CALLS, 'writer call geometry drift')
    model = contract['writer_stage']['model']
    req(model['requested'] == MODEL and float(model['temperature']) == 0.0 and int(model['max_output_tokens']) == MAX_OUTPUT_TOKENS, 'writer model drift')
    req(model['thinking'] is None and int(model['provider_retries']) == 0 and model['substitution_allowed'] is False, 'writer provider semantics drift')
    req(len(contract['writer_stage']['source_units']) == EXPECTED_WRITER_CALLS, 'source unit count drift')
    req(contract['neutral_prompt']['contains_success_failure_label'] is False, 'neutral prompt label leakage contract drift')
    req(contract['neutral_prompt']['contains_numeric_reward_or_score'] is False, 'neutral prompt reward leakage contract drift')
    authority = contract['authority']
    req(authority['experiment_authority'] is True and authority['provider_call_authority'] is True, 'execution authority missing')
    req(authority['claim_expansion_authority'] is False and authority['submission_authority'] is False, 'authority scope expanded')
    for key, row in contract['source_bindings'].items():
        if key in {'b4_result', 'b5_result', 'b8_result'}:
            continue
        path = Path(row['path'])
        req(path.is_file() and sha(path) == row['sha256'], f'source binding drift: {key}')
    runner = Path(contract['code']['writer_runner']['path'])
    req(runner.resolve() == Path(__file__).resolve() and sha(runner) == contract['code']['writer_runner']['sha256'], 'writer runner SHA drift')


def import_runtime(contract: dict[str, Any]):
    root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(Path(contract['vendor_path'])))
    import pyarrow.parquet as pq  # type: ignore
    from research_pipeline.config import load_env_file
    from research_pipeline.ark_provider import ArkResponseStateError, ArkResponsesClient, ArkSettings

    load_env_file(Path(contract['provider_env_file']))
    base = ArkSettings.from_env()
    req(bool(base.api_key), 'provider credential unavailable')
    req(base.base_url == BASE_URL, f'provider base URL drift: {base.base_url}')
    settings = ArkSettings(api_key=base.api_key, base_url=base.base_url, default_model=base.default_model, timeout_seconds=180.0, max_retries=0)
    return pq, ArkResponseStateError, ArkResponsesClient(settings), settings.safe_summary()


def source_data(contract: dict[str, Any], pq) -> dict[int, dict[str, Any]]:
    parquet = Path(contract['source_bindings']['trajectory_parquet']['path'])
    rows = {int(r['task_id']): r for r in pq.read_table(parquet, columns=['task_id', 'task_prompt', 'trajectory_json']).to_pylist()}
    out: dict[int, dict[str, Any]] = {}
    for unit in contract['writer_stage']['source_units']:
        tid = int(unit['source_task'])
        req(tid in rows, f'source task missing: {tid}')
        row = rows[tid]
        summary = action_summary(str(row['trajectory_json']))
        req(jsha(summary) == unit['action_summary_sha256'], f'action summary drift: {tid}')
        req(str(row['task_prompt']) == unit['task_prompt'], f'task prompt drift: {tid}')
        out[tid] = {'task_prompt': str(row['task_prompt']), 'action_summary': summary}
    return out


def stage_name(task: int) -> str:
    return f'neutral-writer-{task}'


def archive_text(root: Path, text: str) -> str:
    digest = tsha(text)
    path = root / 'raw' / digest[:2] / f'{digest}.txt'
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        req(path.read_text(encoding='utf-8') == text, 'content-address collision')
    else:
        path.write_text(text, encoding='utf-8')
    return digest


def run_one(*, client, error_type, unit: dict[str, Any], source: dict[str, Any], system_prompt: str, private_root: Path) -> tuple[dict[str, Any], bool]:
    tid = int(unit['source_task'])
    stage = stage_name(tid)
    stage_path = private_root / 'stages' / f'{stage}.json'
    if stage_path.is_file():
        cached = load(stage_path)
        req(cached.get('stage') == stage, f'cached stage identity drift: {stage}')
        return cached, False
    prompt = writer_prompt(system_prompt, source['task_prompt'], source['action_summary'])
    base = {
        'stage': stage,
        'source_task': tid,
        'condition': 'outcome_blind_procedural',
        'prompt_sha256': tsha(prompt),
        'action_summary_sha256': unit['action_summary_sha256'],
        'requested_model': MODEL,
    }
    try:
        response = client.respond(prompt, model=MODEL, max_output_tokens=MAX_OUTPUT_TOKENS, temperature=0.0, thinking=None, store=True, allow_thinking_compatibility_fallback=False)
        text = str(response.get('text') or '').strip()
        writej(private_root / 'provider-responses' / f'{stage}.json', {
            **base,
            'response_id': response.get('response_id'),
            'provider_status': response.get('status'),
            'requested_model_returned': response.get('requested_model'),
            'resolved_model': response.get('resolved_model'),
            'usage': response.get('usage') or {},
            'text': text,
            'text_sha256': tsha(text) if text else '',
            'thinking_compatibility_fallback': response.get('thinking_compatibility_fallback'),
        })
        req(str(response.get('requested_model')) == MODEL, 'requested model drift in response')
        req(normalized_model(str(response.get('resolved_model'))).startswith('deepseekv4flash'), f"resolved model family drift: {response.get('resolved_model')}")
        req(response.get('thinking_compatibility_fallback') is not True, 'thinking fallback')
        req(bool(text), 'empty assistant text')
        parsed = parse_items(text)
        req(1 <= len(parsed) <= 3, f'memory schema parse/count failure: {len(parsed)}')
        raw_sha = archive_text(private_root, text)
        row = {
            **base,
            'status': 'complete',
            'provider_status': response.get('status'),
            'resolved_model': response.get('resolved_model'),
            'usage': response.get('usage') or {},
            'raw_sha256': raw_sha,
            'memory_item_count': len(parsed),
            'titles': [x['title'] for x in parsed],
        }
    except error_type as exc:
        row = {**base, 'status': 'provider_state_failure_no_text', 'error_type': type(exc).__name__, 'provider_receipt': exc.receipt()}
    except Exception as exc:
        row = {**base, 'status': 'provider_or_runtime_failure', 'error_type': type(exc).__name__, 'error': str(exc)[:1000]}
    writej(stage_path, row)
    return row, True


def all_rows(contract: dict[str, Any], root: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for unit in contract['writer_stage']['source_units']:
        p = root / 'stages' / f'{stage_name(int(unit["source_task"]))}.json'
        if p.is_file():
            out.append(load(p))
    return out


def report(contract: dict[str, Any], root: Path, provider: dict[str, Any], new_calls: int) -> dict[str, Any]:
    rows = all_rows(contract, root)
    complete = [r for r in rows if r.get('status') == 'complete']
    failures = [r for r in rows if r.get('status') != 'complete']
    required = set(int(x) for x in contract['terminal_stage']['required_neutral_source_tasks'])
    completed_required = {int(r['source_task']) for r in complete if int(r['source_task']) in required}
    all_attempted = len(rows) == EXPECTED_WRITER_CALLS
    terminal_support_ready = required == completed_required
    status = 'B11_WRITER_COMPLETE' if all_attempted and not failures else ('B11_WRITER_ATTEMPTS_COMPLETE_WITH_MISSINGNESS' if all_attempted else 'B11_WRITER_PARTIAL')
    return {
        'schema_version': '1.0',
        'experiment_id': EXPERIMENT_ID,
        'paper_id': PAPER_ID,
        'status': status,
        'contract_sha256': contract['contract_sha256'],
        'provider': provider,
        'summary': {
            'provider_calls_expected': EXPECTED_WRITER_CALLS,
            'provider_calls_attempted_total': len(rows),
            'provider_calls_complete': len(complete),
            'provider_failures': len(failures),
            'new_provider_calls_this_invocation': new_calls,
            'required_native_source_count': len(required),
            'required_native_sources_complete': len(completed_required),
            'terminal_support_ready': terminal_support_ready,
            'memory_item_count_distribution': {str(k): sum(int(r.get('memory_item_count') or 0) == k for r in complete) for k in range(1, 4)},
        },
        'writer_outputs': [{k: r.get(k) for k in ('source_task', 'condition', 'raw_sha256', 'memory_item_count', 'titles', 'provider_status', 'resolved_model', 'usage')} for r in complete],
        'failures': [{k: r.get(k) for k in ('source_task', 'stage', 'status', 'error_type', 'provider_receipt', 'error')} for r in failures],
        'terminal_stage_may_activate': terminal_support_ready and all_attempted,
        'scientific_interpretation': 'Writer-stage output is a control construction artifact. No downstream scientific verdict is authorized by this file alone.',
        'scientific_authority': False,
        'experiment_authority': True,
        'claim_expansion_authority': False,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--contract', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--private-root', required=True, type=Path)
    ap.add_argument('--max-new-calls', type=int, default=4)
    args = ap.parse_args()
    contract = load(args.contract)
    validate_contract(contract)
    req(1 <= args.max_new_calls <= EXPECTED_WRITER_CALLS, 'invalid max-new-calls')
    args.private_root.mkdir(parents=True, exist_ok=True)
    lock = (args.private_root / 'transaction.lock').open('a+')
    try:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print(json.dumps({'status': 'TRANSACTION_ALREADY_RUNNING', 'provider_calls_executed_by_this_process': 0}))
        return 3
    try:
        pq, error_type, client, provider_summary = import_runtime(contract)
        sources = source_data(contract, pq)
        system_prompt = Path(contract['neutral_prompt']['path']).read_text(encoding='utf-8')
        new_calls = 0
        for unit in contract['writer_stage']['source_units']:
            tid = int(unit['source_task'])
            stage_path = args.private_root / 'stages' / f'{stage_name(tid)}.json'
            if not stage_path.is_file() and new_calls >= args.max_new_calls:
                break
            row, is_new = run_one(client=client, error_type=error_type, unit=unit, source=sources[tid], system_prompt=system_prompt, private_root=args.private_root)
            new_calls += int(is_new)
            writej(args.output, report(contract, args.private_root, provider_summary, new_calls))
            if is_new:
                print(json.dumps({'stage': row['stage'], 'status': row['status'], 'new_calls_this_invocation': new_calls, 'attempted_total': len(all_rows(contract, args.private_root))}), flush=True)
        out = report(contract, args.private_root, provider_summary, new_calls)
        writej(args.output, out)
        print(json.dumps({'status': out['status'], 'summary': out['summary'], 'terminal_stage_may_activate': out['terminal_stage_may_activate']}, indent=2))
        return 0
    finally:
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        lock.close()


if __name__ == '__main__':
    raise SystemExit(main())
