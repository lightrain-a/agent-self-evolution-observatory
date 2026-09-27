"""Current-source inventory and version-bound evidence/visual handoff for writing.

Reads only explicitly selected local files. Never fetches citations, compiles TeX,
executes embedded code, or promotes a gallery example to experimental evidence.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
from typing import Any

REFERENCE_ROLES = {'writing_exemplar','scientific_related_work','baseline','method_source','venue_template','notation','protocol','result_analysis'}


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def safe_path(root: Path, relative: str) -> Path:
    if not isinstance(relative,str) or not relative or Path(relative).is_absolute():
        raise ValueError('relative-path-required')
    path=(root.resolve()/relative).resolve()
    if not path.is_relative_to(root.resolve()): raise ValueError('path-outside-root')
    return path


def file_ref(root: Path, relative: str) -> dict:
    path=safe_path(root,relative)
    return {'path':relative,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def read_bound(root: Path, ref: dict, *, text: bool=True):
    path=safe_path(root,ref.get('path'))
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=ref.get('sha256'): raise ValueError('source-drift:'+str(ref.get('path')))
    return raw.decode('utf-8') if text else raw


def bound_json(root: Path, ref: dict) -> dict:
    value=json.loads(read_bound(root,ref))
    if not isinstance(value,dict):raise ValueError('bound-json-object-required')
    return value


def active_tex(text: str) -> str:
    """Remove unescaped line comments; this is not a complete TeX macro evaluator."""
    return '\n'.join(re.split(r'(?<!\\)%',line,maxsplit=1)[0] for line in text.splitlines())


def tex_symbols(text: str) -> dict:
    active=active_tex(text)
    def collect(pattern):
        return sorted({v.strip() for match in re.findall(pattern,active) for v in match.split(',') if v.strip()})
    return {
        'citations':collect(r'\\(?:cite\w*)\*?(?:\[[^\]]*\]){0,2}\{([^}]+)\}'),
        'references':collect(r'\\(?:ref|eqref|autoref|cref|Cref|pageref)\*?\{([^}]+)\}'),
        'labels':collect(r'\\label\{([^}]+)\}'),
        'inputs':list(dict.fromkeys(re.findall(r'\\(?:input|include)\s*\{([^}]+)\}',active))),
        'graphics':collect(r'\\includegraphics\*?(?:\[[^\]]*\])?\{([^}]+)\}'),
        'headings':re.findall(r'\\(?:section|subsection|subsubsection)\*?(?:\[[^\]]*\])?\{([^}]+)\}',active),
    }


def manuscript_inventory(root: Path, main: str='main.tex') -> dict:
    visited={};order=[];pending=[];cycle=[]
    def walk(relative,stack):
        if relative in stack:cycle.append(relative);return
        if relative in visited:return
        path=safe_path(root,relative)
        if not path.is_file():pending.append({'path':relative,'reason':'missing-static-include'});return
        text=path.read_text(encoding='utf-8');symbols=tex_symbols(text)
        visited[relative]={'ref':file_ref(root,relative),'symbols':symbols};order.append(relative)
        for child in symbols['inputs']:
            if any(c in child for c in ('\\','#','$','{')):
                pending.append({'path':child,'reason':'dynamic-include-needs-review'});continue
            name=child if child.endswith('.tex') else child+'.tex'
            # TeX includes are normally relative to the compilation root. The fallback is explicit.
            if not safe_path(root,name).exists():
                local=str(Path(relative).parent/name)
                if safe_path(root,local).exists():name=local
            walk(name,stack+[relative])
    walk(main,[])
    rows=[{'path':p,**visited[p]} for p in order]
    main_text=active_tex(safe_path(root,main).read_text(encoding='utf-8')) if main in visited else ''
    return {'main':main,'files':rows,'include_order':order,'unresolved':pending,'cycles':cycle,
            'static_include_scan_only':True,'conditional_tex_requires_review':bool(re.search(r'\\(?:ifdefined|ifnum|ifx|iftrue|iffalse)\b',main_text)),
            'snapshot_sha256':digest(rows),'manuscript_was_not_modified':True}


def load_visual_handoff(root: Path, preparation_ref: dict, handoff_ref: dict, *, evidence_root_relative: str='.') -> dict:
    prep=bound_json(root,preparation_ref);handoff=bound_json(root,handoff_ref)
    if prep.get('paper_id')!=handoff.get('paper_id') or prep.get('snapshot_sha256')!=handoff.get('snapshot_sha256'):
        raise ValueError('visual-handoff-snapshot-mismatch')
    if handoff.get('status')!='MATERIALS_SELECTED_VISUAL_REVIEW_PENDING' or handoff.get('blockers'):
        raise ValueError('visual-handoff-not-ready-for-writing-packet')
    bundle=Path(preparation_ref['path']).parent
    candidates={c['id']:c for g in (prep.get('figures') or {}).get('groups',[]) for c in g.get('candidates',[])}
    selected=[];seen=set()
    for row in handoff.get('selected_figures',[]):
        cid=row.get('candidate_id');candidate=candidates.get(cid)
        if not candidate or cid in seen:raise ValueError('unknown-or-duplicate-selected-figure')
        seen.add(cid)
        if candidate.get('data_role')=='SYNTHETIC_DEMO':raise ValueError('synthetic-demo-cannot-be-paper-evidence')
        relative=str(bundle/row['path'])
        ref={'path':relative,'sha256':row['sha256']};read_bound(root,ref,text=False)
        if prep.get('artifact_sha256',{}).get(row['path'])!=row['sha256']:
            raise ValueError('selected-figure-artifact-mismatch')
        source=candidate.get('source_ref') or {}
        selected.append({'id':cid,'claim_id':candidate.get('claim_id'),'question':candidate.get('question'),
                         'scope':candidate.get('scope'),'data_role':candidate.get('data_role'),
                         'data_sha256':candidate.get('data_sha256'),'artifact_ref':ref,'source_ref':source,
                         'visual_review':'PENDING_ACTUAL_SIZE_REVIEW','is_design_reference':False})
    if not selected:raise ValueError('no-selected-experiment-figures')
    tables=[]
    for table in prep.get('tables',[]):
        if table.get('gaps'):raise ValueError('selected-table-has-unresolved-gaps')
        tables.append({'id':table['id'],'label':table.get('label'),'rows':table['rows'],'columns':table['columns'],
                       'cells':[{k:c.get(k) for k in ('row_id','column_id','status','value','delta','display','source_ref')} for c in table['cells']],
                       'snapshot_sha256':table['snapshot_sha256']})
    evidence_refs={}
    original_refs=[f['source_ref'] for f in selected]+[c['source_ref'] for t in tables for c in t['cells'] if c.get('source_ref')]
    for original in original_refs:
        if not original or not original.get('path') or not original.get('sha256'):raise ValueError('original-visual-data-source-unbound')
        if Path(original['path']).is_absolute():raise ValueError('original-source-relative-path-required')
        ref={**original,'path':str(Path(evidence_root_relative)/original['path'])}
        read_bound(root,ref,text=False);evidence_refs[ref['path']]=ref
    return {'paper_id':prep['paper_id'],'preparation_ref':preparation_ref,'handoff_ref':handoff_ref,'original_source_refs':list(evidence_refs.values()),
            'snapshot_sha256':prep['snapshot_sha256'],'figures':selected,'tables':tables,
            'writer_may_invent_or_replot_data':False,'figure_knowledge_references_are_not_results':True,
            'actual_size_review':'PENDING'}


def reference_packet(root: Path, entries: list[dict]) -> list[dict]:
    rows=[];ids=set()
    for row in entries:
        if not row.get('id') or row['id'] in ids:raise ValueError('reference-id-invalid')
        ids.add(row['id'])
        if row.get('role') not in REFERENCE_ROLES:raise ValueError('reference-role-invalid')
        content=read_bound(root,row['ref'])
        start,end=row.get('start_line',1),row.get('end_line')
        lines=content.splitlines()
        if type(start) is not int or start<1 or (end is not None and (type(end) is not int or end<start)):
            raise ValueError('reference-line-range-invalid')
        end=end or len(lines)
        if start>len(lines) or end>len(lines):raise ValueError('reference-line-range-outside-source')
        excerpt='\n'.join(lines[start-1:end])
        if len(excerpt)>row.get('max_chars',18000):raise ValueError('reference-too-long-select-lines-explicitly')
        rows.append({'id':row['id'],'role':row['role'],'ref':row['ref'],'start_line':start,'end_line':end,
                     'content':excerpt,'permitted_use':row.get('permitted_use','Read in its declared role; do not transfer exemplar facts.')})
    return rows
