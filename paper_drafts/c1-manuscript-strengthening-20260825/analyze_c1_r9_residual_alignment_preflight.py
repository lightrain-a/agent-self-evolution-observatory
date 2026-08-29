#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
import re
import statistics
from pathlib import Path

MANIFEST = Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b4-retrieval-matched-fixed-evidence-20260824/b4-memory-manifest.json')
OUT = Path(__file__).with_name('c1-r9-residual-alignment-preflight-20260829.json')
THRESHOLDS = [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50]


def parse_items(text: str) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    parts = re.split(r'(?m)^Title:\s*', text)
    for part in parts[1:]:
        lines = part.splitlines()
        title = lines[0].strip() if lines else ''
        desc_match = re.search(r'(?m)^Description:\s*(.*)$', part)
        content_match = re.search(r'(?m)^Content:\s*(.*(?:\n(?!Title:).*)*)', part)
        description = desc_match.group(1).strip() if desc_match else ''
        content = content_match.group(1).strip() if content_match else ''
        content = content.split('\n\nTitle:')[0].strip()
        items.append({
            'title': title,
            'description': description,
            'content': content,
            'text': ' '.join([title, description, content]),
        })
    return items


def tokens(text: str) -> set[str]:
    return set(re.findall(r'[a-z0-9]+', text.lower()))


def jaccard(a: str, b: str) -> float:
    left, right = tokens(a), tokens(b)
    union = left | right
    return len(left & right) / len(union) if union else 1.0


def best_matching(success_items: list[dict[str, str]], failure_items: list[dict[str, str]]) -> list[float]:
    if not success_items or not failure_items:
        return []
    n = min(len(success_items), len(failure_items))
    matrix = [[jaccard(x['text'], y['text']) for y in failure_items] for x in success_items]
    best_score = -1.0
    best_scores: list[float] = []
    for success_indices in itertools.combinations(range(len(success_items)), n):
        for failure_indices in itertools.permutations(range(len(failure_items)), n):
            scores = [matrix[i][j] for i, j in zip(success_indices, failure_indices)]
            score = sum(scores) / n
            if score > best_score:
                best_score = score
                best_scores = scores
    return best_scores


def main() -> None:
    obj = json.loads(MANIFEST.read_text(encoding='utf-8'))
    objects = {(int(row['source_task']), row['condition']): row for row in obj['objects']}
    tasks = sorted({task for task, _ in objects})
    rows = []
    all_scores: list[float] = []
    for task in tasks:
        success_text = Path(objects[(task, 'success')]['native_wrapper_path']).read_text(encoding='utf-8')
        failure_text = Path(objects[(task, 'failure')]['native_wrapper_path']).read_text(encoding='utf-8')
        success_items = parse_items(success_text)
        failure_items = parse_items(failure_text)
        scores = best_matching(success_items, failure_items)
        all_scores.extend(scores)
        rows.append({
            'source_task': task,
            'success_items': len(success_items),
            'failure_items': len(failure_items),
            'matched_items': len(scores),
            'matched_jaccards': scores,
            'mean_matched_jaccard': sum(scores) / len(scores) if scores else None,
            'min_matched_jaccard': min(scores) if scores else None,
            'max_matched_jaccard': max(scores) if scores else None,
        })

    sweep = []
    for threshold in THRESHOLDS:
        fully_aligned = 0
        matched_above = 0
        total_matched = 0
        for row in rows:
            scores = row['matched_jaccards']
            total_matched += len(scores)
            count = sum(score >= threshold for score in scores)
            matched_above += count
            if scores and count == len(scores):
                fully_aligned += 1
        sweep.append({
            'threshold': threshold,
            'source_pairs_fully_aligned': fully_aligned,
            'source_pairs_total': len(rows),
            'matched_items_above_threshold': matched_above,
            'matched_items_total': total_matched,
        })

    payload = {
        'schema_version': '1.0',
        'artifact_kind': 'C1_R9_RESIDUAL_ALIGNMENT_PREFLIGHT',
        'paper_id': 'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE',
        'parent_revision': 'R8_NEGATIVE_REPAIR_BOUNDARY',
        'status': 'HOLD_REPRESENTATION_NOT_IDENTIFIED',
        'question': 'Can the 20 frozen success/failure memory pairs support a deterministic lexical decomposition into a stable shared core and branch-specific residual without outcome-informed threshold tuning?',
        'source_manifest': str(MANIFEST),
        'source_pairs': len(rows),
        'parsed_memory_objects': len(obj['objects']),
        'matched_item_pairs': len(all_scores),
        'structural_asymmetry_pairs': [row['source_task'] for row in rows if row['success_items'] != row['failure_items']],
        'summary': {
            'mean_of_pair_mean_matched_jaccard': statistics.mean(row['mean_matched_jaccard'] for row in rows if row['mean_matched_jaccard'] is not None),
            'median_of_pair_mean_matched_jaccard': statistics.median(row['mean_matched_jaccard'] for row in rows if row['mean_matched_jaccard'] is not None),
            'min_pair_mean_matched_jaccard': min(row['mean_matched_jaccard'] for row in rows if row['mean_matched_jaccard'] is not None),
            'max_pair_mean_matched_jaccard': max(row['mean_matched_jaccard'] for row in rows if row['mean_matched_jaccard'] is not None),
        },
        'threshold_sweep': sweep,
        'rows': rows,
        'adjudication': {
            'failure_layer': 'representation_operationalization',
            'scientific_principle_update': 'NONE',
            'reason': 'Lexical item alignment is moderate and threshold-sensitive, with one 3-item versus 1-item pair. Any shared-core/residual split would currently add an outcome-sensitive representation degree of freedom unless an independent operationalization is qualified first.',
            'forbidden_next_step': 'Do not choose a lexical similarity threshold by looking at downstream action or outcome effects, and do not consume the sealed 23-state confirmatory holdout to tune a residual representation.',
            'reopen_condition': 'A residual-exposure object may reopen only after an independently justified and frozen residual representation is qualified without downstream outcome access, with a matched deletion/salience control and fresh evaluation units.',
        },
        'execution': {
            'provider_calls': 0,
            'model_actions': 0,
            'new_outcomes_read': 0,
            'sealed_23_state_holdout_consumed': False,
        },
        'authority': {
            'new_repair_experiment': False,
            'provider': False,
            'gpu': False,
            'confirmatory_full': False,
            'submission': False,
        },
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    print(json.dumps({
        'status': payload['status'],
        'source_pairs': payload['source_pairs'],
        'matched_item_pairs': payload['matched_item_pairs'],
        'mean_pair_match': payload['summary']['mean_of_pair_mean_matched_jaccard'],
        'structural_asymmetry_pairs': payload['structural_asymmetry_pairs'],
        'provider_calls': 0,
    }))


if __name__ == '__main__':
    main()
