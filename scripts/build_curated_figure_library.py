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
    # One manually reviewed method schematic, originating from a paper rather
    # than the four-repository figure archive. The displayed SVG is authored
    # locally; the publisher's original Figure 1 is linked, never mirrored.
    preview_path = root / 'figure-reference-assets/rote-learning-fig1-schematic.svg'
    contract_path = root / 'figure-reference-assets/rote-learning-fig1-inputs.json'
    contract = json.loads(contract_path.read_text(encoding='utf-8'))
    if contract['figure_id'] != 'iclr26-rote-learning-fig1' or contract['numeric_data_required_for_schematic'] is not False:
        raise ValueError('Rote Figure 1 contract must remain a conceptual, non-numeric figure')
    version = hashlib.sha256(preview_path.read_bytes() + contract_path.read_bytes()).hexdigest()
    entries.insert(0, {
        'id':'iclr26-rote-learning-fig1',
        'title':'先记忆，再理解：两阶段方法总图',
        'title_en':'Memorize, then generalize: two-stage overview',
        'group':'method',
        'question':'先记住不带语义的关联，再学会关系含义，如何让旧关联支持三种泛化？',
        'question_en':'How does learning a relation later unlock old associations in three ways?',
        'learn':'两个训练阶段用对照色，少量关系示例连接三个泛化出口：新关联、改写提问、跨语言。图仅讲机制，不暗示任何准确率。',
        'learn_en':'Contrast two phases, then branch into new associations, paraphrases and languages. This schematic contains no accuracy measurements.',
        'required_fields':['phase1 subject–[X]–object pairs','phase2 semantic example(s)','held-out association probe','paraphrase probe','cross-language probe'],
        'chart':'two_phase_method_schematic',
        'source_name':'ICLR 2026 · Rote Learning Considered Useful',
        'source_path':'Paper Figure 1, page 2',
        'source_url':contract['source']['figure_url'],
        'paper_url':contract['source']['paper_url'],
        'commit':'ICLR2026-PAPER-FIGURE-1',
        'preview_url':'figure-reference-assets/rote-learning-fig1-schematic.svg',
        'preview_origin':'INDEPENDENT_EXPLANATORY_REDRAW_NOT_ORIGINAL_FIGURE',
        'preview_blob_sha':hashlib.sha256(preview_path.read_bytes()).hexdigest(),
        'code_url':contract['source']['code_url'],
        'code_role':'EXPERIMENT_CODE_NOT_FIGURE_SOURCE',
        'license':'Publisher/author rights apply to Figure 1; the gallery preview is an independent schematic.',
        'license_url':contract['source']['paper_url'],
        'content_version':version,
        'reference_only':True,
        'input_contract_url':'figure-reference-assets/rote-learning-fig1-inputs.json',
        'input_contract':contract['data_fields_required'],
        'numeric_data_required':False,
        'optional_measured_fields':contract['extra_data_if_claiming_measured_generalization'],
        'review':{'scope':'visually checked official Figure 1 (PDF page 2); independent redraw',
                  'reviewer':'assistant','human_requested':True,'human_approved':False,'final_size_qa':'NOT_RUN'}
    })
    # Nature Human Behaviour 2026 Figure 4b/c/e: three distinct visual grammars.
    # SVGs are original layout sketches with illustrative points, never the paper's measured values or pixels.
    nhb_contract_path = root / 'figure-reference-assets/nhb-fig4-bce-inputs.json'
    nhb_contract = json.loads(nhb_contract_path.read_text(encoding='utf-8'))
    if nhb_contract['figure_id'] != 'nhb26-figure4-bce' or not nhb_contract['original_data_required_for_real_plot']:
        raise ValueError('NHB Figure 4 must require real experimental measurements')
    nhb_panels = [
        ('b','nhb26-f4b-individual-strips','个体散点 + 三指标均值对照','Individual distributions and three-outcome comparisons',
         'comparison','为什么两种课程在规则、记忆与冲突选择上不同？',
         'Which strategy tests reveal a curriculum difference?',
         '小点呈现全部个体、大点/须呈现统计量；分面按同一概率尺度；预注册检验单独标明。',
         'Show raw individuals and clear group estimates on a shared scale; flag preregistered contrasts.',
         'nhb-fig4b-strip.svg','individual_strip_plus_group_estimate',
         ['learner_id','curriculum_id','test_type','accuracy','contrast_test']),
        ('c','nhb26-f4c-joint-learning','双能力指数 · 个体与组统计','Joint-learning index with individuals and group estimate',
         'comparison','一个学习者是否真的同时掌握记忆与规则？',
         'Does each learner retain both memory and rule use?',
         '综合指标须由同一个体两个独立测试计算，个体散点与组估计分开展示；不能只用群体平均。',
         'Derive joint index per participant; plot individuals and group estimates separately.',
         'nhb-fig4c-index.svg','individual_joint_metric',
         ['learner_id','context_accuracy','memory_accuracy','chance_accuracy','dli']),
        ('e','nhb26-f4e-state-trajectory','二维能力轨迹 · 沿训练方向观察遗忘','Two-ability training trajectories with temporal arrows',
         'trend','模型先学会一种策略，再学另一种时，旧策略什么时候消失？',
         'When does training the second strategy erase the first?',
         '规则正确率横轴、历史记忆正确率纵轴，按checkpoint连线并用箭头标时序；不能用示意点替代训练日志。',
         'Plot measured checkpoint sequences in rule-vs-memory space, with arrowed temporal direction.',
         'nhb-fig4e-trajectory.svg','two_ability_checkpoint_trajectory',
         ['model_id','seed','curriculum_id','training_step','rule_test_accuracy','memory_test_accuracy'])
    ]
    nhb_version = hashlib.sha256(nhb_contract_path.read_bytes()).hexdigest()
    for pos,(panel,id_,title,title_en,group,question,question_en,learn,learn_en,svg,chart,fields) in enumerate(nhb_panels,1):
        preview = root / 'figure-reference-assets' / svg
        if not preview.is_file(): raise FileNotFoundError(preview)
        contract_panel=nhb_contract['figure4_visual_patterns'][panel]
        entries.insert(pos,{
            'id':id_,'title':title,'title_en':title_en,'group':group,
            'question':question,'question_en':question_en,'learn':learn,'learn_en':learn_en,
            'required_fields':fields,'chart':chart,
            'source_name':'Nature Human Behaviour 2026 · Figure 4'+panel,
            'source_path':'Figure 4'+panel,'source_url':nhb_contract['source']['figure_url'],
            'paper_url':nhb_contract['source']['paper_url'],
            'commit':'NHB2026-SOURCE-FIGURE-4'+panel.upper(),
            'preview_url':'figure-reference-assets/'+svg,
            'preview_origin':'INDEPENDENT_ILLUSTRATIVE_LAYOUT_NOT_ORIGINAL_FIGURE_OR_DATA',
            'preview_blob_sha':hashlib.sha256(preview.read_bytes()).hexdigest(),
            'code_url':nhb_contract['source']['experiment_code_url'],
            'code_role':'EXPERIMENT_CODE_NOT_FIGURE_SOURCE',
            'license':'Original paper is open access CC BY 4.0; preview is a separate illustrative schematic, no measured datapoints.',
            'license_url':nhb_contract['source']['paper_url'],
            'content_version':hashlib.sha256((nhb_version+preview.name+str(preview.stat().st_size)).encode()).hexdigest(),
            'reference_only':True,'input_contract_url':'figure-reference-assets/nhb-fig4-bce-inputs.json',
            'input_contract':[{'name':k,'fields':v,'reason':contract_panel['query']}
                              for k,v in [('observations',contract_panel['required_fields']),('statistics',contract_panel['statistics'])]],
            'numeric_data_required':True,
            'visual_pitfalls':contract_panel['pitfall'],
            'review':{'scope':'Nature Figure4 b/c/e layout inspected; independent schematic and measured-data schema',
                      'reviewer':'assistant','human_requested':True,'human_approved':False,'final_size_qa':'NOT_RUN'}
        })
    selected = {e['id'] for e in entries if e['source_name']=='Figures4Papers'}
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
    payload = {'schema_version': '2.1', 'curated_on': '2026-10-29',
        'scope': 'Six Figures4Papers references, an ICLR 2026 method schematic, and three independent NHB 2026 Figure 4b/c/e pattern sketches; not a universal chart taxonomy',
        'source_archive_sha256': hashlib.sha256(raw_path.read_bytes()).hexdigest(),
        'summary': {'active_examples': len(entries), 'archived_entries': len(audit)-len(selected),
                    'original_entries': len(audit), 'additional_paper_figures': 4, 'primary_sources': 3},
        'policy': {'archive_loaded_by_default': False, 'recommendations_default': 2,
                   'recommendations_max': 3, 'references_max': 2, 'force_four_candidates': False,
                   'reference_scope_not_experimental_scope': True,
                   'primary_style': 'Figures4Papers quantitative references plus a source-cited ICLR conceptual method example; preserve established manuscript style'},
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
