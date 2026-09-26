"""Version-bound table skeletons and incremental result filling; no experiments."""
from __future__ import annotations
import csv
import hashlib
import io
import json
import math
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

SCHEMA_VERSION = '1.0'
STATUSES = {'PENDING', 'RUNNING', 'PARTIAL', 'COMPLETE', 'INVALID', 'NOT_APPLICABLE'}


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def load_bound_json(root: Path, ref: dict[str, Any]) -> Any:
    """Only a supplied JSON file beneath root, exact SHA256 and JSON pointer."""
    root = root.resolve()
    relative = ref.get('path')
    if not isinstance(relative, str) or Path(relative).is_absolute():
        raise ValueError('source-path-must-be-relative')
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or path.suffix != '.json':
        raise ValueError('source-path-outside-evidence-root-or-not-json')
    content = path.read_bytes()
    if hashlib.sha256(content).hexdigest() != ref.get('sha256'):
        raise ValueError('source-sha256-mismatch')
    value = json.loads(content, parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite-json')))
    pointer = ref.get('pointer', '')
    if pointer:
        if not isinstance(pointer, str) or not pointer.startswith('/'):
            raise ValueError('invalid-json-pointer')
        for part in pointer[1:].split('/'):
            part = part.replace('~1', '/').replace('~0', '~')
            value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def _ids(rows: list[dict], what: str) -> None:
    values = [r.get('id') for r in rows]
    if not rows or any(not isinstance(v, str) or not v for v in values) or len(set(values)) != len(values):
        raise ValueError(f'{what}-ids-missing-or-duplicate')


def validate_table_spec(spec: dict) -> None:
    _ids(spec.get('rows', []), 'row')
    _ids(spec.get('columns', []), 'column')
    columns = {r['id']: r for r in spec['columns']}
    for col in columns.values():
        if col.get('aggregate'):
            members = col.get('members', [])
            if col['aggregate'] not in {'macro', 'micro'} or not members or len(set(members)) != len(members):
                raise ValueError('invalid-aggregate-members-or-mode')
            if any(x not in columns or columns[x].get('aggregate') for x in members):
                raise ValueError('aggregate-requires-existing-leaf-columns')
            units = {columns[x].get('unit') for x in members}
            metrics = {columns[x].get('metric_id') for x in members}
            if len(units) != 1 or len(metrics) != 1:
                raise ValueError('aggregate-incompatible-unit-or-metric')
        else:
            for field in ('dataset_id', 'condition_id', 'protocol_id', 'split_id', 'cohort_sha256', 'metric_id', 'unit', 'analysis_unit'):
                if not col.get(field): raise ValueError('column-missing-' + field)
            if col.get('direction') not in {'higher', 'lower'}:
                raise ValueError('metric-direction-missing')
    if spec.get('delta_reference') and spec['delta_reference'] not in {r['id'] for r in spec['rows']}:
        raise ValueError('unknown-delta-reference')


def _raw_value(record: dict, col: dict) -> tuple[float, int | None, int | None]:
    if record.get('kind') == 'rate':
        k, n = record.get('successes'), record.get('total')
        if type(k) is not int or type(n) is not int or n <= 0 or not 0 <= k <= n:
            raise ValueError('invalid-rate-counts')
        if col.get('expected_total') is not None and n != col['expected_total']:
            raise ValueError('total-does-not-match-frozen-panel')
        if col['unit'] != 'percent': raise ValueError('rate-unit-must-be-percent')
        return 100 * k / n, k, n
    value = record.get('value')
    if record.get('kind') != 'scalar' or type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError('invalid-scalar')
    return float(value), None, None


def display_value(value: float, digits: int = 1) -> str:
    return format(Decimal(str(value)).quantize(Decimal('1').scaleb(-digits), rounding=ROUND_HALF_UP), f'.{digits}f')


def compile_table(spec: dict, records: list[dict]) -> dict:
    """Results are already loaded from bound files. Missing coverage never becomes 0."""
    validate_table_spec(spec)
    index = {}
    valid_keys = {(r['id'], c['id']) for r in spec['rows'] for c in spec['columns'] if not c.get('aggregate')}
    for rec in records:
        key = (rec.get('method_id'), rec.get('column_id'))
        if key not in valid_keys: raise ValueError('unregistered-result-cell:' + str(key))
        if key in index: raise ValueError('duplicate-result-cell:' + str(key))
        index[key] = rec
    cells, gaps = [], []
    by_key = {}
    for row in spec['rows']:
        for col in spec['columns']:
            if col.get('aggregate'): continue
            rec = index.get((row['id'], col['id']))
            cell = {'row_id': row['id'], 'column_id': col['id'], 'status': 'PENDING', 'value': None,
                    'successes': None, 'total': None, 'source_ref': None, 'delta': None, 'display': '—'}
            if rec is not None:
                status = rec.get('status')
                cell['status'] = status if status in STATUSES else 'INVALID'
                cell['result_id'] = rec.get('result_id', '')
                cell['source_ref'] = rec.get('_bound_ref')
                if status == 'COMPLETE':
                    try:
                        if not rec.get('_bound_ref'): raise ValueError('unbound-result')
                        for field in ('dataset_id', 'condition_id', 'protocol_id', 'split_id', 'cohort_sha256', 'metric_id', 'unit', 'analysis_unit'):
                            if rec.get(field) != col.get(field): raise ValueError('result-mismatch-' + field)
                        cell['value'], cell['successes'], cell['total'] = _raw_value(rec, col)
                    except ValueError as exc:
                        cell.update(status='INVALID', reason=str(exc), value=None)
                elif status == 'NOT_APPLICABLE':
                    if not rec.get('reason'): cell.update(status='INVALID', reason='missing-not-applicable-reason')
                    else: cell['display'] = 'N/A'
            if cell['status'] != 'COMPLETE': gaps.append({'row_id': row['id'], 'column_id': col['id'], 'status': cell['status'], 'reason': cell.get('reason', '')})
            by_key[row['id'], col['id']] = cell
    for row in spec['rows']:
        for col in spec['columns']:
            if not col.get('aggregate'): continue
            members = [by_key[row['id'], x] for x in col['members']]
            complete = [m for m in members if m['status'] == 'COMPLETE']
            cell = {'row_id': row['id'], 'column_id': col['id'], 'status': 'PENDING', 'value': None,
                    'delta': None, 'display': '—', 'coverage': [len(complete), len(members)], 'members': list(col['members'])}
            if len(complete) == len(members):
                if col['aggregate'] == 'micro':
                    if any(m['total'] is None for m in members): raise ValueError('micro-requires-rate-counts')
                    cell['value'] = 100 * sum(m['successes'] for m in members) / sum(m['total'] for m in members)
                else: cell['value'] = sum(m['value'] for m in members) / len(members)
                cell['status'] = 'COMPLETE'
            by_key[row['id'], col['id']] = cell
    for row in spec['rows']:
        for col in spec['columns']:
            cell = by_key[row['id'], col['id']]
            if cell['status'] == 'COMPLETE':
                cell['display'] = display_value(cell['value'], spec.get('digits', 1))
                ref = by_key.get((spec.get('delta_reference'), col['id']))
                if ref and ref['status'] == 'COMPLETE' and row['id'] != spec['delta_reference']:
                    cell['delta'] = cell['value'] - ref['value']
                    sign = '+' if cell['delta'] >= 0 else ''
                    cell['display'] += f" ({sign}{display_value(cell['delta'], spec.get('digits', 1))})"
            cells.append(cell)
    return {'id': spec['id'], 'label': spec.get('label', spec['id']), 'spec_sha256': digest(spec),
            'snapshot_sha256': digest({'spec': spec, 'records': records}), 'rows': spec['rows'], 'columns': spec['columns'],
            'cells': cells, 'gaps': gaps, 'delta_reference': spec.get('delta_reference'),
            'status': 'TABLE_NUMBERS_COMPLETE_REVIEW_PENDING' if not gaps else 'TABLE_PARTIAL',
            'scientific_authority': False}


def layout_change(old: dict, new: dict, reason: str) -> dict:
    """Report whether a requested small edit changes scientific cell identities."""
    def identities(spec):
        return {(r['id'], c['id']): {k: c.get(k) for k in ('dataset_id', 'condition_id', 'protocol_id', 'split_id', 'cohort_sha256', 'metric_id', 'unit', 'analysis_unit', 'expected_total', 'direction', 'aggregate', 'members')}
                for r in spec['rows'] for c in spec['columns']}
    a, b = identities(old), identities(new)
    added, removed = sorted(b.keys()-a.keys()), sorted(a.keys()-b.keys())
    changed = [key for key in a.keys() & b.keys() if a[key] != b[key]]
    return {'kind': 'EXPERIMENT_DESIGN_CHANGE' if added or removed or changed else 'LAYOUT_ONLY',
            'added': added, 'removed': removed, 'changed': sorted(changed), 'reason': reason,
            'requires_experiment_change_ledger': bool(added or removed or changed), 'automatic_rerun': False}


def table_exports(table: dict) -> tuple[str, str]:
    rows, columns = table['rows'], table['columns']
    index = {(c['row_id'], c['column_id']): c['display'] for c in table['cells']}
    out = io.StringIO(); writer = csv.writer(out)
    def safe_csv(v):
        s = str(v)
        return "'"+s if s.startswith(('=', '+', '-', '@')) else s
    writer.writerow(['Method'] + [safe_csv(c.get('label', c['id'])) for c in columns])
    for row in rows: writer.writerow([safe_csv(row.get('label', row['id']))] + [safe_csv(index[row['id'], c['id']]) for c in columns])
    def tex(v):
        escaped = {'&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}', '\\': r'\textbackslash{}', '~': r'\textasciitilde{}', '^': r'\textasciicircum{}', '—': '--'}
        return ''.join(escaped.get(c, c) for c in str(v))
    lines = [r'% Generated from a bound snapshot; requires booktabs.', '% snapshot: '+table['snapshot_sha256'], r'\begin{tabular}{l'+('r'*len(columns))+'}', r'\toprule']
    groups = []
    for c in columns:
        group = c.get('group', '')
        if groups and groups[-1][0] == group: groups[-1][1] += 1
        else: groups.append([group, 1])
    if any(g for g, _ in groups): lines.append(' & '+' & '.join(r'\multicolumn{'+str(n)+'}{c}{'+tex(g)+'}' for g,n in groups)+r' \\')
    lines += ['Method & '+' & '.join(tex(c.get('label', c['id'])) for c in columns)+r' \\', r'\midrule']
    for row in rows: lines.append(tex(row.get('label', row['id']))+' & '+' & '.join(tex(index[row['id'], c['id']]) for c in columns)+r' \\')
    lines += [r'\bottomrule', r'\end{tabular}']
    return out.getvalue(), '\n'.join(lines)+'\n'
