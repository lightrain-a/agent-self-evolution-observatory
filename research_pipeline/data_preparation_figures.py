"""Data-shaped chart candidates, four per row. Independent SVG recipes, no vendor code."""
from __future__ import annotations
import math
from typing import Any
from .data_preparation_tables import digest

CATALOG = (
    ('dot', 'categorical', '点图 / Dot plot', '比较类别水平，保留零值'),
    ('lollipop', 'categorical', '棒棒糖 / Lollipop', '以轻量线段突出类别差异'),
    ('bar', 'categorical', '横向条形 / Horizontal bar', '绝对值从零起画'),
    ('tile', 'categorical', '数值条带 / Value tiles', '颜色与精确值并列'),
    ('dumbbell', 'paired', '哑铃 / Dumbbell', '同对象前后配对变化'),
    ('slope', 'paired', '斜率 / Slope', '两个条件之间的方向与交叉'),
    ('parity', 'paired', '配对一致性 / Parity', '以恒等线区分改善与回归'),
    ('delta', 'paired', '配对差值 / Paired delta', '相同对象 after−before；保留负值'),
    ('ecdf', 'samples', '经验累积分布 / ECDF', '原始样本的尾部和整体分布'),
    ('box', 'samples', '箱线 / Box plot', '原始样本四分位与全范围'),
    ('histogram', 'samples', '直方 / Histogram', '原始样本共享分箱，不能编样本'),
    ('strip', 'samples', '样本点分布 / Strip', '保留每个样本，横向抖动不代表额外量'),
    ('line', 'series', '趋势 / Line', '只连接实际观测点'),
    ('step', 'series', '阶梯 / Step', '有序观测；右连续展示，不等于测量中间值'),
    ('scatter', 'xy', '二维权衡 / Scatter', '两个有单位的真实指标'),
    ('bubble', 'xy', '量纲气泡 / Bubble', '面积编码第三个真实非负变量'),
    ('heatmap', 'matrix', '热力矩阵 / Heatmap', '缺失值留空，不当零'),
    ('bubble_matrix', 'matrix', '气泡矩阵 / Bubble matrix', '绝对值面积与正负编码'),
    ('forest', 'interval', '区间 / Forest', '明确的 SD/SE/CI 来源，不能虚构'),
)
BY_ID = {x[0]: {'id':x[0], 'kind':x[1], 'label':x[2], 'purpose':x[3]} for x in CATALOG}


def _finite(v: Any) -> bool:
    return type(v) in (int, float) and math.isfinite(v)


def validate_asset(asset: dict) -> list[str]:
    errors = []
    for key in ('id', 'kind', 'unit', 'analysis_unit', 'scope', 'claim_id', 'question'):
        if not isinstance(asset.get(key), str) or not asset[key].strip(): errors.append('missing-'+key)
    if asset.get('status') != 'COMPLETE': errors.append('asset-not-complete')
    if not asset.get('_bound_ref'): errors.append('unbound-asset')
    if asset.get('data_role') not in {'EXPLORATORY', 'CONFIRMATORY', 'HISTORICAL_REPLAY', 'SYNTHETIC_DEMO'}:
        errors.append('data-role-missing')
    kind = asset.get('kind'); rows = asset.get('rows', [])
    if kind == 'matrix':
        vals, row_labels, col_labels = asset.get('values'), asset.get('row_labels'), asset.get('column_labels')
        if not isinstance(vals, list) or not vals or not isinstance(row_labels, list) or not isinstance(col_labels, list) or not col_labels or len(vals) != len(row_labels):
            return errors + ['invalid-matrix-shape']
        if any(not isinstance(r, list) or len(r) != len(col_labels) for r in vals): return errors + ['ragged-matrix']
        if any(v is not None and not _finite(v) for r in vals for v in r): errors.append('nonfinite-matrix')
        if not any(v is not None for r in vals for v in r): errors.append('empty-matrix')
        return errors
    required = {'categorical': ('value',), 'paired': ('before','after'), 'samples': ('value',), 'series': ('x','y'), 'xy': ('x','y'), 'interval': ('value','lower','upper')}
    if kind not in required: return errors + ['unsupported-data-kind']
    if not isinstance(rows, list) or not rows: return errors + ['missing-rows']
    ids = []
    for row in rows:
        if not isinstance(row, dict): errors.append('invalid-row'); continue
        ids.append(row.get('id'))
        if any(not _finite(row.get(k)) for k in required[kind]): errors.append('missing-or-nonfinite-numeric-field')
        if kind in {'categorical','paired','interval'} and not row.get('label'): errors.append('missing-row-label')
        if kind in {'samples','series'} and not row.get('group'): errors.append('missing-group')
        if kind == 'interval' and all(_finite(row.get(k)) for k in required[kind]):
            if not row['lower'] <= row['value'] <= row['upper']: errors.append('invalid-interval-order')
    if any(not isinstance(v,str) or not v for v in ids) or len(set(ids)) != len(ids): errors.append('missing-or-duplicate-unit-ids')
    if kind == 'paired' and not asset.get('pairing_definition'): errors.append('pairing-not-declared')
    if kind == 'interval':
        if asset.get('interval_kind') not in {'SD','SE','CI'} or not asset.get('interval_source'): errors.append('interval-definition-missing')
        if asset.get('interval_kind') == 'CI' and (not _finite(asset.get('confidence_level')) or not 0 < asset['confidence_level'] < 1): errors.append('ci-level-missing')
    if kind in {'series','xy'}:
        if not asset.get('x_unit') or not asset.get('y_unit'): errors.append('axis-units-missing')
    if kind == 'series' and not errors:
        keys = [(r['group'], r['x']) for r in rows]
        if len(keys) != len(set(keys)): errors.append('duplicate-series-x-requires-explicit-aggregation')
    return sorted(set(errors))


def plan_candidates(assets: list[dict], *, rounds: int = 3, columns: int = 4, style: dict | None = None) -> dict:
    """Choose distinct structural recipes, not four palettes of the same plot."""
    if columns != 4: raise ValueError('candidate-contact-sheet-requires-four-columns')
    if type(rounds) is not int or not 1 <= rounds <= 12: raise ValueError('rounds-must-be-1-to-12')
    style = style or {'font_family':'Georgia, serif', 'theme':'paper-vivid'}
    groups, blocked, unused = [], [], []
    ids = [a.get('id') for a in assets]
    if len(set(ids)) != len(ids): raise ValueError('duplicate-asset-ids')
    for asset in assets:
        errors = validate_asset(asset)
        if errors:
            blocked.append({'asset_id':asset.get('id'), 'reasons':errors}); continue
        eligible = [r[0] for r in CATALOG if r[1] == asset['kind']]
        if 'bubble' in eligible and (not asset.get('size_unit') or not all(_finite(r.get('size')) and r['size'] >= 0 for r in asset['rows'])): eligible.remove('bubble')
        if len(groups) >= rounds:
            unused.append(asset['id']); continue
        data_sha = digest(asset)
        candidates = []
        for recipe in eligible[:columns]:
            ident = digest({'asset_id':asset['id'], 'data':data_sha, 'recipe':recipe, 'style':style})
            candidates.append({'id':'FIG-'+ident[:14], 'recipe':recipe, 'recipe_label':BY_ID[recipe]['label'],
                'asset_id':asset['id'], 'claim_id':asset['claim_id'], 'question':asset['question'], 'scope':asset['scope'],
                'data_role':asset['data_role'], 'data_sha256':data_sha, 'spec_sha256':ident,
                'status':'CANDIDATE_NOT_SELECTED', 'style':style, 'source_ref':asset['_bound_ref']})
        groups.append({'id':'GROUP-'+digest({'asset':asset['id'], 'data':data_sha})[:12],
                       'label':asset['question'], 'comparison_mode':'SAME_DATA_DIFFERENT_ENCODING',
                       'candidates':candidates, 'unfilled_slots':columns-len(candidates),
                       'reason_if_short':'Insufficient compatible distinct chart types; no fabricated data.' if len(candidates)<columns else ''})
    return {'groups':groups, 'blocked_assets':blocked, 'not_rendered_due_to_round_budget':unused,
            'columns':4, 'rounds_requested':rounds, 'scientific_authority':False,
            'no_forced_distribution_or_uncertainty':True}
