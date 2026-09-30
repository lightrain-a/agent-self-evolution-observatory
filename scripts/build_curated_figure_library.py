#!/usr/bin/env python3
"""Explicit publication-reference allowlist; never run or mirror upstream code/images."""
from __future__ import annotations
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Inspected source-image contact sheet, not a final-size PDF or scientific audit.
SELECTED = [
    ('f4p-52caded0a3f18f', '多指标方法比较', 'Multi-metric comparison', 'comparison',
     '在同一任务集合上，不同方法分别表现如何？', 'How do methods compare across the same metrics?',
     '共享方法编码与图例；各面板只回答一个指标。方法过多时改点图或拆面板。',
     'Reuse shared method encoding and legends. Use dots or split panels when categories get crowded.',
     ['method', 'metric', 'value', 'evaluation_set'], 'grouped_bar', 'figure_Brainteaser/plot_correctness_by_category.py'),
    ('f4p-95f2e8c63ee37a', '紧凑组件消融', 'Compact component ablation', 'comparison',
     '去掉哪个组件会改变结果？', 'Which component changes the outcome?',
     '少量变体直接比较；误差条必须有真实重复与定义，不能照搬示例。',
     'Keep few variants; intervals require actual repetitions and a defined uncertainty measure.',
     ['variant', 'metric', 'value', 'matched_budget'], 'ablation_bar', 'figure_CellSpliceNet/plot_ablation.py'),
    ('f4p-f1e5ddbcc161b3', '训练或优化进程', 'Training or optimization progress', 'trend',
     '效果随真实训练步数怎样变化？', 'How does performance change at measured training steps?',
     '这是折线图而不是柱状图；只连接有序实测点，同一方法的线型保持一致。',
     'This is a line plot, not a bar chart. Connect measured ordered steps only.',
     ['method', 'step', 'value', 'metric_unit'], 'line', 'figure_VIGIL/plot_posttraining.py'),
    ('f4p-25b81d41a820af', '异质性与组成矩阵', 'Heterogeneity and composition matrix', 'matrix',
     '哪些任务或方向存在差异，哪些没有？', 'Where do differences appear, and where do they not?',
     '保留完整行列和真实零；空缺不能涂成零。颜色与标注表达同一量。',
     'Keep predefined members and real zeros. Missing is not zero; labels and colors encode the same measure.',
     ['row_id', 'column_id', 'value', 'denominator'], 'heatmap', 'figure_ophthal_review/plot_composition.py'),
    ('f4p-6f16029887c7be', '参数敏感性与双面板', 'Sensitivity with separate panels', 'trend',
     '同一个参数怎样影响两个不同指标？', 'How does one parameter affect two distinct metrics?',
     '不同单位分小轴，避免双纵轴制造同步变化的错觉；共享参数范围与方法编码。',
     'Use separate axes for distinct units, with shared parameter range and method encoding.',
     ['parameter', 'metric', 'value', 'metric_unit'], 'paired_metric_panels', 'figure_RNAGenScape/plot_sweep.py'),
    ('f4p-35a1cf904b0987', '实测运行成本', 'Measured runtime cost', 'cost',
     '方法实际用了多少时间或资源？', 'What runtime or resources did each method actually consume?',
     '只借鉴紧凑成本比较；先核对量纲、归一化和坐标尺度。此图不是性能—成本散点。',
     'Reuse compact cost comparison after checking units and scales. This is not a performance–cost scatter.',
     ['method', 'measured_cost', 'cost_unit', 'cost_scope'], 'cost_bar', 'figure_RNAGenScape/plot_comparison.py'),
]


def build(root: Path = ROOT) -> dict:
    raw_path = root / 'generated/figure-knowledge-base.json'
    raw = json.loads(raw_path.read_text(encoding='utf-8'))
    lookup = {e['id']: e for e in raw['entries']}
    entries = []
    for entry_id, title, en, group, question, qe, learn, le, fields, chart, script in SELECTED:
        e = lookup[entry_id]
        if e['source_id'] != 'f4p' or e['kind'] != 'FIGURE_EXAMPLE' or not e['previews']:
            raise ValueError(f'Allowlisted source no longer matches: {entry_id}')
        prefix = f"https://github.com/ChenLiu-1996/figures4papers/blob/{e['commit']}/"
        entries.append({'id': entry_id, 'title': title, 'title_en': en, 'group': group,
            'question': question, 'question_en': qe, 'learn': learn, 'learn_en': le,
            'required_fields': fields, 'chart': chart, 'source_name': 'Figures4Papers',
            'source_path': e['path'], 'source_url': e['source_url'], 'commit': e['commit'],
            'preview_url': e['previews'][0]['url'], 'preview_blob_sha': e['previews'][0]['blob_sha'],
            'code_url': prefix + script, 'license': e['license'], 'license_url': e['license_url'],
            'content_version': e['content_version'], 'reference_only': True,
            'review': {'scope': 'thumbnail structure and publication relevance',
                       'reviewer': 'assistant', 'human_approved': False, 'final_size_qa': 'NOT_RUN'}})
    selected = {e['id'] for e in entries}
    audit = []
    for e in raw['entries']:
        if e['id'] in selected: reason = 'KEEP_PUBLICATION_REFERENCE'
        elif e['kind'] in ('SUPPORT_ASSET',): reason = 'SUPPORT_NOT_A_FIGURE_RECOMMENDATION'
        elif e['kind'] in ('TUTORIAL', 'TABLE_GUIDE'): reason = 'DOCUMENTATION_NOT_A_VISUAL_EXAMPLE'
        elif e.get('exact_duplicate_of'): reason = 'DUPLICATE_CONTENT'
        elif not e['previews']: reason = 'NO_PREVIEW_FOR_SELECTION'
        elif e['id'] == 'f4p-0bbfcc5dd7f9a8': reason = 'MULTI_AXIS_PATTERN_NOT_A_DEFAULT'
        elif e['id'] == 'f4p-e58841e406975d': reason = 'DENSE_DOMAIN_SPECIFIC_COMPOSITE'
        elif 'unclassified' in e['families']: reason = 'UNVERIFIED_SEMANTIC_CLASSIFICATION'
        elif e['source_id'] != 'f4p': reason = 'OUTSIDE_F4P_FIRST_DEFAULT_SCOPE'
        else: reason = 'REDUNDANT_OR_SPECIALIZED_FOR_THIS_SCOPE'
        audit.append({'id': e['id'], 'path': e['path'], 'reason': reason})
    counts = dict(Counter(x['reason'] for x in audit))
    payload = {'schema_version': '2.0', 'curated_on': '2026-09-30',
        'scope': 'ML-paper publication-reference shortlist, not a universal chart taxonomy',
        'source_archive_sha256': hashlib.sha256(raw_path.read_bytes()).hexdigest(),
        'summary': {'active_examples': len(entries), 'archived_entries': len(audit)-len(entries),
                    'original_entries': len(audit), 'primary_sources': 1},
        'policy': {'archive_loaded_by_default': False, 'recommendations_default': 2,
                   'recommendations_max': 3, 'references_max': 2, 'force_four_candidates': False,
                   'reference_scope_not_experimental_scope': True,
                   'primary_style': 'Figures4Papers with the established manuscript style preserved'},
        'entries': entries, 'exclusion_counts': counts, 'scientific_authority': False}
    version_bytes = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()
    payload['catalog_version'] = hashlib.sha256(version_bytes).hexdigest()
    dest = root / 'generated'
    text = json.dumps(payload, ensure_ascii=False, separators=(',', ':'))
    (dest/'figure-curated.json').write_text(text+'\n', encoding='utf-8')
    (dest/'figure-curated.js').write_text('window.FIGURE_CURATED='+text+';\n', encoding='utf-8')
    (dest/'figure-curation-audit.json').write_text(json.dumps({'catalog_version':payload['catalog_version'],
        'counts': counts, 'items': audit, 'note':'Archive-only is a scoped retrieval decision, not a claim that every excluded image is poor.'},ensure_ascii=False),encoding='utf-8')
    return payload


if __name__ == '__main__':
    p=build();print(json.dumps({'summary':p['summary'],'exclusion_counts':p['exclusion_counts'],'catalog_version':p['catalog_version']},ensure_ascii=False))
