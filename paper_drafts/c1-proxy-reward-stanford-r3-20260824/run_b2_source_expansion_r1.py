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
EXPERIMENT_ID = 'D2-PROXY-B2-SOURCE-EXPANSION-R1-4096'
EXPECTED_MODEL = 'deepseek-v4-flash'
EXPECTED_CALLS = 32
EXPECTED_MAX_OUTPUT_TOKENS = 4096
EXPECTED_BASE_URL = 'https://ark.cn-beijing.volces.com/api/plan/v3'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def jsha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()


def load(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(obj, dict):
        raise RuntimeError(f'JSON root must be object: {path}')
    return obj


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    os.replace(tmp, path)


def archive_text(root: Path, text: str) -> str:
    digest = text_sha(text)
    path = root / 'raw' / digest[:2] / f'{digest}.txt'
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding='utf-8') != text:
        raise RuntimeError('content-address collision')
    if not path.exists():
        path.write_text(text, encoding='utf-8')
    return digest


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def normalize_text(text: str) -> str:
    return ' '.join(str(text or '').split())


def tokens(text: str) -> set[str]:
    return set(re.findall(r"[A-Za-z0-9_'-]+", str(text or '').lower()))


def jaccard_distance(a: str, b: str) -> float:
    aa, bb = tokens(a), tokens(b)
    union = aa | bb
    return 0.0 if not union else 1.0 - len(aa & bb) / len(union)


def titles(text: str) -> list[str]:
    values = re.findall(r'^##\s*Title:\s*(.+?)\s*$', str(text or ''), flags=re.MULTILINE)
    return [normalize_text(v) for v in values]


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


def normalized_model(value: str) -> str:
    return re.sub(r'[^a-z0-9]', '', str(value or '').lower())


def validate_contract(contract_path: Path, c: dict[str, Any]) -> None:
    require(c.get('schema_version') == '1.0', 'schema drift')
    require(c.get('paper_id') == PAPER_ID and c.get('experiment_id') == EXPERIMENT_ID, 'identity drift')
    require(c.get('status') == 'FROZEN_BEFORE_PROVIDER_CALLS', 'contract not frozen')
    require(c.get('expected_provider_calls') == EXPECTED_CALLS, 'call budget drift')
    model = c.get('writer_model') or {}
    require(model.get('requested') == EXPECTED_MODEL, 'writer model drift')
    require(float(model.get('temperature')) == 0.0, 'temperature drift')
    require(int(model.get('max_output_tokens')) == EXPECTED_MAX_OUTPUT_TOKENS, 'output cap drift')
    require(model.get('thinking') is None and int(model.get('provider_retries')) == 0, 'provider semantics drift')
    require(model.get('substitution_allowed') is False, 'model substitution forbidden')
    gate = c.get('breadth_gate') or {}
    require(gate == {'min_complete_pairs':14,'min_exact_content_change_rate':0.9,'min_title_set_change_rate':0.8}, 'breadth gate drift')
    a = c.get('authority') or {}
    require(a.get('experiment_authority') is True and a.get('provider_call_authority') is True, 'execution authority missing')
    require(a.get('claim_expansion_authority') is False and a.get('submission_authority') is False, 'authority scope expanded')
    for key, row in (c.get('source_artifacts') or {}).items():
        path = Path(row['path'])
        require(path.is_file() and sha(path) == row['sha256'], f'source binding drift: {key}')
    hp = Path(c['human_authority']['path'])
    require(hp.is_file() and sha(hp) == c['human_authority']['sha256'], 'human authority drift')
    runner = Path(c['code']['runner']['path'])
    require(runner.resolve() == Path(__file__).resolve() and sha(runner) == c['code']['runner']['sha256'], 'runner SHA drift')
    selection = load(Path(c['source_artifacts']['selection']['path']))
    require(selection['status'] == 'FROZEN_SELECTION_BEFORE_PROVIDER_CALLS', 'selection not frozen')
    require(len(selection['selected_sources']) == 16, 'selection size drift')
    require([str(x['task_id']) for x in selection['selected_sources']] == c['source_tasks'], 'source task list drift')


def import_runtime(c: dict[str, Any]):
    root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(Path(c['vendor_path'])))
    import pyarrow.parquet as pq  # type: ignore
    from research_pipeline.config import load_env_file
    from research_pipeline.ark_provider import ArkResponseStateError, ArkResponsesClient, ArkSettings

    load_env_file(Path(c['provider_env_file']))
    base = ArkSettings.from_env()
    require(bool(base.api_key), 'provider credential unavailable')
    require(base.base_url == EXPECTED_BASE_URL, f'provider base URL drift: {base.base_url}')
    settings = ArkSettings(api_key=base.api_key, base_url=base.base_url, default_model=base.default_model, timeout_seconds=180.0, max_retries=0)
    return pq, ArkResponseStateError, ArkResponsesClient(settings), settings.safe_summary()


def load_sources(c: dict[str, Any], pq) -> dict[str, dict[str, Any]]:
    selection = load(Path(c['source_artifacts']['selection']['path']))
    selected = {str(r['task_id']): r for r in selection['selected_sources']}
    parquet = Path(c['source_artifacts']['parquet']['path'])
    rows = {str(r['task_id']): r for r in pq.read_table(parquet, columns=['task_id','task_prompt','is_successful','trajectory_json']).to_pylist()}
    out: dict[str, dict[str, Any]] = {}
    for task in c['source_tasks']:
        require(task in selected and task in rows, f'source missing: {task}')
        row = rows[task]
        summary = action_summary(str(row['trajectory_json']))
        require(jsha(summary) == selected[task]['trajectory_summary_sha256'], f'action summary drift: {task}')
        require(str(row['task_prompt']) == selected[task]['task_prompt'], f'task prompt drift: {task}')
        require(bool(row['is_successful']) is bool(selected[task]['original_is_successful']), f'outcome stratum drift: {task}')
        out[task] = {'task_prompt': str(row['task_prompt']), 'action_summary': summary, 'original_is_successful': bool(row['is_successful']), 'intent_template_id': selected[task]['intent_template_id']}
    return out


def stage_name(task: str, label: str) -> str:
    return f'writer-{task}-{label}'


def run_one(*, client, error_type, task: str, label: str, source: dict[str, Any], system_prompt: str, private_root: Path) -> dict[str, Any]:
    stage = stage_name(task, label)
    stage_path = private_root / 'stages' / f'{stage}.json'
    if stage_path.is_file():
        cached = load(stage_path)
        require(cached.get('stage') == stage, f'cached stage identity drift: {stage}')
        return cached
    prompt = writer_prompt(system_prompt, source['task_prompt'], source['action_summary'])
    base = {'stage': stage, 'task_id': task, 'label': label, 'prompt_sha256': text_sha(prompt), 'requested_model': EXPECTED_MODEL}
    try:
        response = client.respond(prompt, model=EXPECTED_MODEL, max_output_tokens=EXPECTED_MAX_OUTPUT_TOKENS, temperature=0.0, thinking=None, store=True, allow_thinking_compatibility_fallback=False)
        text = str(response.get('text') or '')
        atomic_json(private_root / 'provider-responses' / f'{stage}.json', {
            **base,
            'response_id': response.get('response_id'),
            'provider_status': response.get('status'),
            'requested_model_returned': response.get('requested_model'),
            'resolved_model': response.get('resolved_model'),
            'usage': response.get('usage') or {},
            'text': text,
            'text_sha256': text_sha(text) if text else '',
            'thinking_compatibility_fallback': response.get('thinking_compatibility_fallback'),
        })
        require(str(response.get('requested_model')) == EXPECTED_MODEL, 'requested model drift in response')
        require(normalized_model(str(response.get('resolved_model'))).startswith('deepseekv4flash'), f"resolved model family drift: {response.get('resolved_model')}")
        require(response.get('thinking_compatibility_fallback') is not True, 'provider thinking fallback')
        require(bool(text.strip()), 'empty assistant text')
        raw_sha = archive_text(private_root, text)
        row = {**base, 'status':'complete', 'provider_status':response.get('status'), 'resolved_model':response.get('resolved_model'), 'usage':response.get('usage') or {}, 'raw_sha256':raw_sha, 'titles':titles(text)}
    except error_type as exc:
        row = {**base, 'status':'provider_state_failure_no_text', 'error_type':type(exc).__name__, 'provider_receipt':exc.receipt()}
    except Exception as exc:
        row = {**base, 'status':'provider_or_runtime_failure', 'error_type':type(exc).__name__, 'error':str(exc)[:1000]}
    atomic_json(stage_path, row)
    return row


def build_report(c: dict[str, Any], rows: list[dict[str, Any]], private_root: Path, provider_summary: dict[str, Any]) -> dict[str, Any]:
    by = {(str(r.get('task_id')), str(r.get('label'))): r for r in rows}
    pairs = []
    for task in c['source_tasks']:
        s = by.get((task,'success'), {})
        f = by.get((task,'failure'), {})
        complete = s.get('status') == 'complete' and f.get('status') == 'complete'
        st = ft = ''
        if complete:
            st = (private_root / 'raw' / s['raw_sha256'][:2] / f"{s['raw_sha256']}.txt").read_text(encoding='utf-8')
            ft = (private_root / 'raw' / f['raw_sha256'][:2] / f"{f['raw_sha256']}.txt").read_text(encoding='utf-8')
        pairs.append({
            'task_id': task,
            'original_is_successful': c['source_metadata'][task]['original_is_successful'],
            'intent_template_id': c['source_metadata'][task]['intent_template_id'],
            'complete_pair': complete,
            'success_memory_sha256': s.get('raw_sha256') if s.get('status') == 'complete' else None,
            'failure_memory_sha256': f.get('raw_sha256') if f.get('status') == 'complete' else None,
            'exact_content_changed': bool(complete and normalize_text(st) != normalize_text(ft)),
            'token_jaccard_distance': round(jaccard_distance(st, ft), 6) if complete else None,
            'success_titles': titles(st) if complete else [],
            'failure_titles': titles(ft) if complete else [],
            'title_set_changed': bool(complete and set(titles(st)) != set(titles(ft))),
        })
    complete = [p for p in pairs if p['complete_pair']]
    complete_n = len(complete)
    exact_rate = sum(p['exact_content_changed'] for p in complete) / complete_n if complete_n else 0.0
    title_rate = sum(p['title_set_changed'] for p in complete) / complete_n if complete_n else 0.0
    mean_j = sum(float(p['token_jaccard_distance']) for p in complete) / complete_n if complete_n else None
    gate = c['breadth_gate']
    gate_pass = complete_n >= gate['min_complete_pairs'] and exact_rate >= gate['min_exact_content_change_rate'] and title_rate >= gate['min_title_set_change_rate']
    attempted = len(rows)
    failures = [r for r in rows if r.get('status') != 'complete']
    return {
        'schema_version':'1.0',
        'experiment_id':EXPERIMENT_ID,
        'paper_id':PAPER_ID,
        'status':'B2_EXECUTION_COMPLETE' if attempted == EXPECTED_CALLS else 'B2_EXECUTION_PARTIAL',
        'contract_sha256':c['contract_sha256'],
        'provider':provider_summary,
        'summary':{
            'selected_source_pairs':16,
            'provider_calls_expected':EXPECTED_CALLS,
            'provider_calls_attempted':attempted,
            'provider_calls_complete':sum(r.get('status') == 'complete' for r in rows),
            'provider_failures':len(failures),
            'complete_pairs':complete_n,
            'complete_pairs_original_failure':sum(p['complete_pair'] and not p['original_is_successful'] for p in pairs),
            'complete_pairs_original_success':sum(p['complete_pair'] and p['original_is_successful'] for p in pairs),
            'paired_exact_content_change_rate':round(exact_rate,6) if complete_n else None,
            'paired_title_set_change_rate':round(title_rate,6) if complete_n else None,
            'mean_token_jaccard_distance':round(mean_j,6) if mean_j is not None else None,
            'min_token_jaccard_distance':min((p['token_jaccard_distance'] for p in complete), default=None),
            'max_token_jaccard_distance':max((p['token_jaccard_distance'] for p in complete), default=None),
            'breadth_gate_pass':gate_pass,
        },
        'breadth_gate':gate,
        'pairs':pairs,
        'failures':[{k:r.get(k) for k in ('task_id','label','status','error_type','provider_receipt','error')} for r in failures],
        'decision':'SUPPORT_BROAD_WRITE_CHANNEL' if gate_pass else ('BROAD_WRITE_CHANNEL_NOT_ESTABLISHED' if attempted == EXPECTED_CALLS else 'B2_INCOMPLETE_NO_SCIENTIFIC_VERDICT'),
        'selection_sha256':c['source_artifacts']['selection']['sha256'],
        'new_provider_calls_this_experiment':attempted,
        'new_rollouts':0,
        'scientific_authority':False,
        'experiment_authority':True,
        'claim_expansion_authority':False,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--contract', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--private-root', required=True, type=Path)
    args = ap.parse_args()
    c = load(args.contract)
    validate_contract(args.contract, c)
    args.private_root.mkdir(parents=True, exist_ok=True)
    lock = (args.private_root / 'transaction.lock').open('a+')
    try:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print(json.dumps({'status':'TRANSACTION_ALREADY_RUNNING','provider_calls_executed_by_this_process':0}))
        return 3
    try:
        pq, error_type, client, provider_summary = import_runtime(c)
        sources = load_sources(c, pq)
        success_prompt = Path(c['source_artifacts']['success_prompt']['path']).read_text(encoding='utf-8')
        failure_prompt = Path(c['source_artifacts']['failure_prompt']['path']).read_text(encoding='utf-8')
        rows: list[dict[str, Any]] = []
        for task in c['source_tasks']:
            for label, system_prompt in (('success',success_prompt),('failure',failure_prompt)):
                row = run_one(client=client, error_type=error_type, task=task, label=label, source=sources[task], system_prompt=system_prompt, private_root=args.private_root)
                rows.append(row)
                report = build_report(c, rows, args.private_root, provider_summary)
                atomic_json(args.output, report)
                print(json.dumps({'stage':row['stage'],'status':row['status'],'attempted':len(rows),'complete':sum(r.get('status')=='complete' for r in rows)}), flush=True)
        out = build_report(c, rows, args.private_root, provider_summary)
        atomic_json(args.output, out)
        print(json.dumps({'status':out['status'],'summary':out['summary'],'decision':out['decision']}, indent=2), flush=True)
        return 0 if out['status'] == 'B2_EXECUTION_COMPLETE' else 2
    finally:
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        lock.close()


if __name__ == '__main__':
    raise SystemExit(main())
