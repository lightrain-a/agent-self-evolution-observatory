"""Turn selected, bound experiment surfaces into allowed LaTeX insertions.

Gallery references never become result figures. SVG-to-PDF conversion must already
have happened in the project's export pipeline; this module does not claim to do it.
"""
from __future__ import annotations
from pathlib import Path
import re
from .paper_writing_sources import read_bound
from .data_preparation_tables import table_exports


def compile_placements(root:Path,bridge:dict|None,placements:list[dict])->dict:
    figures={f['id']:f for f in (bridge or {}).get('figures',[])}
    tables={t['id']:t for t in (bridge or {}).get('tables',[])}
    snippets=[];refs=[];labels=set();allowed={'labels':[],'references':[],'inputs':[],'graphics':[]}
    for p in placements:
        label=p.get('label','')
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9:_-]*',label) or label in labels:raise ValueError('invalid-or-duplicate-visual-label')
        labels.add(label)
        caption=p.get('caption','')
        if not caption or re.search(r'\\(?:input|include|write|end|begin|label|usepackage)\b',caption):raise ValueError('caption-fact-text-required')
        if p.get('kind')=='figure':
            figure=figures.get(p.get('visual_id'))
            if not figure:raise ValueError('figure-not-in-current-operator-selection')
            ref=p.get('latex_artifact_ref') or figure['artifact_ref']
            if Path(ref.get('path','')).suffix.lower() not in {'.pdf','.png','.jpg','.jpeg'}:
                raise ValueError('latex-figure-export-required-svg-is-not-pdflatex-ready')
            read_bound(root,ref,text=False)
            if ref['sha256']!=figure['artifact_ref']['sha256'] and p.get('derived_from_sha256')!=figure['artifact_ref']['sha256']:
                raise ValueError('figure-export-provenance-missing')
            width=p.get('width_fraction',1.0)
            if type(width) not in (int,float) or not 0<width<=1:raise ValueError('figure-width-invalid')
            filename=ref['path']
            if any(c in filename for c in '{}\\\n'):raise ValueError('unsafe-tex-asset-path')
            tex='\\begin{figure}[t]\n\\centering\n\\includegraphics[width='+str(width)+'\\linewidth]{'+filename+'}\n\\caption{'+caption+'}\n\\label{'+label+'}\n\\end{figure}\n'
            refs.append(ref);allowed['graphics'].append(filename)
        elif p.get('kind')=='table':
            table=tables.get(p.get('visual_id'))
            if not table:raise ValueError('table-not-in-current-handoff')
            _,body=table_exports(table)
            tex='\\begin{table}[t]\n\\centering\n\\caption{'+caption+'}\n\\label{'+label+'}\n'+body+'\\end{table}\n'
        else:raise ValueError('placement-must-be-figure-or-table')
        allowed['labels'].append(label);allowed['references'].append(label)
        snippets.append({'visual_id':p['visual_id'],'kind':p['kind'],'label':label,'latex':tex,
                         'caption_status':'OPERATOR_SUPPLIED_FACTS_REQUIRE_REVIEW','must_preserve_numeric_body':True})
    return {'snippets':snippets,'allowed_additions':allowed,'watch_refs':refs,'data_recomputed_by_writer':False}
