#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

PAPER_ID = 'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE'
EXPERIMENT_ID = 'D2-PROXY-B11-OUTCOME-BLIND-PROCEDURAL-WRITER'


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


def items(text: str) -> list[dict[str, str]]:
    blocks = re.split(r'(?m)^# Memory Item \d+\s*$', text)
    out: list[dict[str, str]] = []
    for block in blocks:
        if not block.strip():
            continue
        m1 = re.search(r'(?m)^## Title:\s*(.+?)\s*$', block)
        m2 = re.search(r'(?m)^## Description:\s*(.+?)\s*$', block)
        m3 = re.search(r'(?ms)^## Content:\s*(.+?)\s*$', block)
        req(bool(m1 and m2 and m3), 'memory item parse failure')
        out.append({'title': m1.group(1).strip(), 'description': m2.group(1).strip(), 'content': m3.group(1).strip()})
    req(1 <= len(out) <= 3, 'invalid memory item count')
    return out


def native_wrapper(source_intent: str, text: str) -> str:
    preamble = "\nBelow are some memory items that I accumulated from past interaction from the environment that may be helpful to solve the task. You can use it when you feel it's relevant.\n\n"
    result = preamble + f'[Retrieved from past task: "{source_intent}"]\n'
    for item in items(text):
        result += f"Title: {item['title']}\nDescription: {item['description']}\nContent: {item['content']}\n\n"
    return result


def token_set(text: str) -> set[str]:
    return set(re.findall(r"[A-Za-z0-9_'-]+", str(text or '').lower()))


def jaccard_distance(a: str, b: str) -> float:
    aa, bb = token_set(a), token_set(b)
    union = aa | bb
    return 0.0 if not union else 1.0 - len(aa & bb) / len(union)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--contract', required=True, type=Path)
    ap.add_argument('--writer-result', required=True, type=Path)
    ap.add_argument('--writer-private-root', required=True, type=Path)
    ap.add_argument('--private-root', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    args = ap.parse_args()

    contract = load(args.contract)
    writer = load(args.writer_result)
    req(contract.get('paper_id') == PAPER_ID and contract.get('experiment_id') == EXPERIMENT_ID, 'contract identity drift')
    req(writer.get('paper_id') == PAPER_ID and writer.get('experiment_id') == EXPERIMENT_ID, 'writer result identity drift')
    req(writer.get('contract_sha256') == contract.get('contract_sha256'), 'writer contract binding drift')
    req(writer.get('summary', {}).get('provider_calls_attempted_total') == 20, 'writer attempts incomplete')
    req(writer.get('terminal_stage_may_activate') is True, 'required neutral sources incomplete')
    req(contract['activation_policy']['terminal_requires_all_11_native_sources_complete'] is True, 'activation policy drift')

    b4_manifest_path = Path(contract['source_bindings']['b4_memory_manifest']['path'])
    b4_manifest = load(b4_manifest_path)
    req(sha(b4_manifest_path) == contract['source_bindings']['b4_memory_manifest']['sha256'], 'B4 manifest drift')
    b4_objects = {(int(x['source_task']), str(x['condition'])): x for x in b4_manifest['objects']}
    req(len(b4_objects) == 40, 'B4 object geometry drift')
    task_units = {int(x['source_task']): x for x in contract['writer_stage']['source_units']}
    writer_rows = {int(x['source_task']): x for x in writer['writer_outputs']}
    req(len(writer_rows) == 20, 'neutral writer output count drift')

    args.private_root.mkdir(parents=True, exist_ok=True)
    objects = []
    comparisons = []
    for source in sorted(task_units):
        row = writer_rows[source]
        digest = str(row['raw_sha256'])
        raw = args.writer_private_root / 'raw' / digest[:2] / f'{digest}.txt'
        req(raw.is_file() and sha(raw) == digest, f'neutral raw missing/drift: {source}')
        text = raw.read_text(encoding='utf-8')
        parsed = items(text)
        intent = str(task_units[source]['task_description'])
        wrapper = native_wrapper(intent, text)
        wrapper_path = args.private_root / f'{source}-neutral-native-wrapper.txt'
        wrapper_path.write_text(wrapper, encoding='utf-8')
        objects.append({
            'source_task': source,
            'condition': 'outcome_blind_procedural',
            'task_description': intent,
            'raw_path': str(raw.resolve()),
            'raw_sha256': digest,
            'native_wrapper_path': str(wrapper_path.resolve()),
            'native_wrapper_sha256': tsha(wrapper),
            'memory_item_count': len(parsed),
            'titles': [x['title'] for x in parsed],
            'required_by_native_36_support': source in set(contract['terminal_stage']['required_neutral_source_tasks']),
        })
        s_obj = b4_objects[(source, 'success')]
        f_obj = b4_objects[(source, 'failure')]
        s_text = Path(s_obj['raw_path']).read_text(encoding='utf-8')
        f_text = Path(f_obj['raw_path']).read_text(encoding='utf-8')
        comparisons.append({
            'source_task': source,
            'neutral_to_success_token_jaccard_distance': round(jaccard_distance(text, s_text), 6),
            'neutral_to_failure_token_jaccard_distance': round(jaccard_distance(text, f_text), 6),
            'success_to_failure_token_jaccard_distance': round(jaccard_distance(s_text, f_text), 6),
            'neutral_title_set_equals_success': set(x['title'] for x in parsed) == set(x['title'] for x in items(s_text)),
            'neutral_title_set_equals_failure': set(x['title'] for x in parsed) == set(x['title'] for x in items(f_text)),
        })

    required = set(int(x) for x in contract['terminal_stage']['required_neutral_source_tasks'])
    required_objects = [x for x in objects if x['source_task'] in required]
    req(len(objects) == 20 and len(required_objects) == len(required) == 11, 'manifest geometry drift')
    payload = {
        'schema_version': '1.0',
        'artifact_type': 'b11-neutral-native-memory-manifest',
        'paper_id': PAPER_ID,
        'experiment_id': EXPERIMENT_ID,
        'status': 'B11_NEUTRAL_MEMORY_MANIFEST_READY',
        'contract_sha256': contract['contract_sha256'],
        'writer_result_sha256': sha(args.writer_result),
        'source_task_count': 20,
        'required_native_source_count': 11,
        'memory_object_count': 20,
        'native_wrapper_contract': b4_manifest['native_wrapper_contract'],
        'objects': objects,
        'writer_geometry': {
            'mean_neutral_to_success_token_jaccard_distance': round(sum(x['neutral_to_success_token_jaccard_distance'] for x in comparisons) / len(comparisons), 6),
            'mean_neutral_to_failure_token_jaccard_distance': round(sum(x['neutral_to_failure_token_jaccard_distance'] for x in comparisons) / len(comparisons), 6),
            'mean_success_to_failure_token_jaccard_distance_recomputed': round(sum(x['success_to_failure_token_jaccard_distance'] for x in comparisons) / len(comparisons), 6),
            'neutral_closer_to_success_sources': sum(x['neutral_to_success_token_jaccard_distance'] < x['neutral_to_failure_token_jaccard_distance'] for x in comparisons),
            'neutral_closer_to_failure_sources': sum(x['neutral_to_failure_token_jaccard_distance'] < x['neutral_to_success_token_jaccard_distance'] for x in comparisons),
            'neutral_equidistant_sources': sum(x['neutral_to_failure_token_jaccard_distance'] == x['neutral_to_success_token_jaccard_distance'] for x in comparisons),
            'neutral_title_set_equals_success_sources': sum(x['neutral_title_set_equals_success'] for x in comparisons),
            'neutral_title_set_equals_failure_sources': sum(x['neutral_title_set_equals_failure'] for x in comparisons),
            'comparisons': comparisons,
            'interpretation_guard': 'Descriptive writer-state geometry only. Text distance is not a downstream-effect predictor and has no confirmatory gate.',
        },
        'source_bindings': {
            'b4_memory_manifest_sha256': sha(b4_manifest_path),
            'writer_result_sha256': sha(args.writer_result),
        },
        'provider_calls': 0,
        'terminal_stage_may_activate': True,
        'scientific_authority': False,
        'experiment_authority': True,
        'claim_expansion_authority': False,
    }
    writej(args.output, payload)
    print(json.dumps({
        'status': payload['status'],
        'source_task_count': payload['source_task_count'],
        'required_native_source_count': payload['required_native_source_count'],
        'writer_geometry': {k: v for k, v in payload['writer_geometry'].items() if k != 'comparisons'},
        'provider_calls': 0,
    }, indent=2))


if __name__ == '__main__':
    main()
