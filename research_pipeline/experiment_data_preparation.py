"""Paper-data preparation: tables, figure alternatives and versioned operator feedback.

No model invocation, experiment scheduling, claim adjudication or manuscript prose.
Default cycle execution reads only registered preparation bundles; rendering is explicit.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import tempfile
from typing import Any
from .data_preparation_tables import load_bound_json, compile_table, table_exports, digest, layout_change
from .data_preparation_figures import plan_candidates, CATALOG
from .data_preparation_svg import render_svg

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = '1.0'
ACTIONS = {'KEEP','REVISE','REJECT'}


def _write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.prep-', dir=path.parent)
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as f: f.write(text)
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)


def _json(path: Path, value):
    _write(path,json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n')


def _read(path: Path):
    value=json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value,dict): raise ValueError('expected-json-object')
    return value


def compile_bundle(manifest: dict, evidence_root: Path) -> tuple[dict,list[dict]]:
    if not manifest.get('paper_id'): raise ValueError('paper-id-required')
    tables,assets,errors=[],[],[]
    for spec in manifest.get('tables',[]):
        records=[]
        for ref in spec.get('result_refs',[]):
            try:
                raw=load_bound_json(evidence_root,ref)
                if not isinstance(raw,dict): raise ValueError('result-must-be-object')
                records.append({**raw,'_bound_ref':ref})
            except (ValueError,OSError,KeyError,IndexError,TypeError) as exc:
                errors.append({'surface':spec.get('id'),'kind':'RESULT_SOURCE_ERROR','reason':str(exc)})
        try: tables.append(compile_table(spec,records))
        except (ValueError,KeyError,TypeError) as exc:
            errors.append({'surface':spec.get('id'),'kind':'TABLE_SPEC_ERROR','reason':str(exc)})
    for ref in manifest.get('figure_asset_refs',[]):
        try:
            raw=load_bound_json(evidence_root,ref)
            if not isinstance(raw,dict): raise ValueError('figure-asset-must-be-object')
            assets.append({**raw,'_bound_ref':ref})
        except (ValueError,OSError,KeyError,IndexError,TypeError) as exc:
            errors.append({'surface':'figure','kind':'FIGURE_SOURCE_ERROR','reason':str(exc)})
    table_index={t['id']:t for t in tables}
    for asset in assets:
        row_index={r.get('id'):r for r in asset.get('rows',[]) if isinstance(r,dict)}
        for binding in asset.get('table_bindings',[]):
            try:
                table=table_index[binding['table_id']]
                cell=next(c for c in table['cells'] if c['row_id']==binding['row_id'] and c['column_id']==binding['column_id'])
                quantity=binding.get('quantity','value')
                if quantity not in {'value','delta'}: raise ValueError('unsupported-table-quantity')
                expected=cell.get(quantity); actual=row_index[binding['asset_row_id']][binding.get('field','value')]
                if cell['status']!='COMPLETE' or expected is None or type(actual) not in (int,float) or abs(expected-actual)>1e-10:
                    raise ValueError('table-figure-value-mismatch')
            except (KeyError,StopIteration,TypeError,ValueError) as exc:
                asset['status']='INVALID'
                errors.append({'surface':asset.get('id'),'kind':'TABLE_FIGURE_BINDING_ERROR','reason':str(exc)})
    renderer_sha=hashlib.sha256((Path(__file__).parent/'data_preparation_svg.py').read_bytes()).hexdigest()
    style={**manifest.get('figure_style',{}),'renderer_sha256':renderer_sha}
    figures=plan_candidates(assets,rounds=manifest.get('preview_rounds',1),columns=manifest.get('preview_columns',2),style=style)
    state={'schema_version':SCHEMA_VERSION,'paper_id':manifest['paper_id'],'title':manifest.get('title','Experiment data preparation'),
           'manifest_sha256':digest(manifest),'tables':tables,'figures':figures,'source_errors':errors,
           'stage':'EXPERIMENT_DATA_PREPARATION_NOT_MANUSCRIPT_WRITING','scientific_authority':False,
           'experiments_launched':0,'model_calls':0,'human_review_status':'NOT_REVIEWED',
           'formats':['CSV','LaTeX','SVG','HTML','JSON'], 'pdf_png_conversion':'USE_EXISTING_EXPORT_PIPELINE_NOT_IMPLEMENTED_HERE',
           'source_data_included':False,'renderer_sha256':renderer_sha}
    if manifest.get('figure_reference_brief'):
        from .figure_knowledge_base import validate_reference_selection, selection_brief
        kb=_read(ROOT/'generated'/'figure-knowledge-base.json')
        ids=validate_reference_selection(kb,manifest['figure_reference_brief'])
        state['external_reference_selection']=selection_brief(kb,ids,manifest.get('figure_question',''),manifest.get('available_data_fields',[]))
        state['external_reference_selection']['role']='DESIGN_REFERENCES_NOT_EXPERIMENTAL_RESULTS'
    state['snapshot_sha256']=digest(state)
    state['status']='PREVIEW_WITH_GAPS' if errors or figures['blocked_assets'] or any(t['gaps'] for t in tables) else 'PREVIEW_READY_FOR_OPERATOR_SELECTION'
    return state,assets


def render_bundle_html(state: dict) -> str:
    e=lambda v:html.escape(str(v),quote=True)
    body=[f'<h1>{e(state["title"])}</h1>',f'<p>Paper: {e(state["paper_id"])} · snapshot <code>{state["snapshot_sha256"][:16]}</code></p>',
          '<p class="notice">候选预览，不是论文定稿。浏览器选择仅保存在本机；请导出反馈并通过后端核对版本后持久化。Synthetic demo 不是研究结果。</p>']
    for table in state['tables']:
        idx={(x['row_id'],x['column_id']):x for x in table['cells']}
        body.append('<section><h2>'+e(table['label'])+'</h2><div class="table-wrap"><table><thead><tr><th>Method</th>')
        groups=[]
        for c in table['columns']:
            g=c.get('group','')
            if groups and groups[-1][0]==g:groups[-1][1]+=1
            else:groups.append([g,1])
        body.extend('<th colspan="'+str(n)+'">'+e(g)+'</th>' for g,n in groups)
        body.append('</tr><tr><th></th>'+''.join('<th>'+e(c.get('label',c['id']))+'</th>' for c in table['columns'])+'</tr></thead><tbody>')
        for row in table['rows']:
            body.append('<tr><th>'+e(row.get('label',row['id']))+'</th>')
            for c in table['columns']:
                cell=idx[row['id'],c['id']]
                body.append('<td title="'+e(cell['status'])+'">'+e(cell['display'])+'</td>')
            body.append('</tr>')
        body.append('</tbody></table></div><p>Missing/invalid cells: '+str(len(table['gaps']))+' · 平均只在预定成员齐全后计算。</p></section>')
    body.append('<h2>四联候选图 / Figure candidates</h2>')
    for gi,group in enumerate(state['figures']['groups'],1):
        body.append('<section><h3>'+e(group['label'])+'</h3><p>同一数据、不同表达 / Same data, different encodings</p><div class="figure-grid">')
        for fi,c in enumerate(group['candidates'],1):
            body.append('<article class="candidate"><a href="figures/'+c['id']+'.svg" target="_blank" rel="noopener"><img loading="lazy" src="figures/'+c['id']+'.svg" alt="'+e(c['recipe_label'])+'"></a>'+
                f'<h4>G{gi:02d}-F{fi:02d} · '+e(c['recipe_label'])+'</h4><p>'+e(c['data_role'])+' · '+e(c['scope'])+'</p><code>'+c['id']+'</code>'+
                '<label>选择 <select data-candidate="'+c['id']+'"><option value="">未选择</option><option value="KEEP">保留</option><option value="REVISE">重画 / 修改</option><option value="REJECT">不采用</option></select></label>'+
                '<label>修改意见 <textarea data-note="'+c['id']+'" rows="2" placeholder="只改图例、类型、布局；数据变化另行记录"></textarea></label></article>')
        body.append('</div>')
        if group['unfilled_slots']:body.append('<p>当前数据不足以支持更多合理图型，不为补数量添加候选。</p>')
        body.append('</section>')
    body.append('<button id="export-feedback">导出本地反馈 JSON</button><p id="save-state">未写入服务器。</p>')
    body.append('<details><summary>来源/缺口/版本记录</summary><pre>'+e(json.dumps({'source_errors':state['source_errors'],'blocked_assets':state['figures']['blocked_assets'],'snapshot':state['snapshot_sha256']},ensure_ascii=False,indent=2))+'</pre></details>')
    payload={'snapshot_sha256':state['snapshot_sha256'],'paper_id':state['paper_id'],'candidates':[{'id':c['id'],'spec_sha256':c['spec_sha256'],'data_sha256':c['data_sha256']} for g in state['figures']['groups'] for c in g['candidates']]}
    data_json=json.dumps(payload,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    script="""const bundle=JSON.parse(document.getElementById('bundle-data').textContent);
const key='paper-prep:'+bundle.snapshot_sha256;let draft={};try{draft=JSON.parse(localStorage.getItem(key)||'{}')}catch(_){}
for(const c of bundle.candidates){const s=document.querySelector('[data-candidate="'+c.id+'"]'),n=document.querySelector('[data-note="'+c.id+'"]');s.value=draft[c.id]?.action||'';n.value=draft[c.id]?.note||'';const save=()=>{draft[c.id]={action:s.value,note:n.value};try{localStorage.setItem(key,JSON.stringify(draft));document.getElementById('save-state').textContent='已保存到本机浏览器；尚未写服务器。'}catch(_){document.getElementById('save-state').textContent='本地保存不可用，请立即导出反馈。'}};s.addEventListener('change',save);n.addEventListener('input',save)}
document.getElementById('export-feedback').onclick=()=>{const events=bundle.candidates.filter(c=>draft[c.id]?.action).map(c=>({...c,...draft[c.id],at:new Date().toISOString()}));const payload={schema_version:'1.0',paper_id:bundle.paper_id,snapshot_sha256:bundle.snapshot_sha256,events,origin:'BROWSER_DRAFT_NOT_SERVER_ACCEPTED'};const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}));a.download='figure-feedback-'+bundle.snapshot_sha256.slice(0,12)+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)};"""
    css='body{font:15px/1.55 system-ui,sans-serif;color:#172033;background:#f5f7fb;margin:0;padding:28px}h1{font-size:30px}section{margin:28px 0}.notice{border-left:4px solid #2563eb;padding:12px;background:white}.figure-grid{display:grid;grid-template-columns:repeat(4,minmax(240px,1fr));gap:16px;overflow-x:auto;padding-bottom:12px}.candidate{background:white;border:1px solid #dce3ef;border-radius:12px;padding:12px;min-width:0}.candidate img{width:100%;display:block}.candidate h4{margin:10px 0}.candidate p{font-size:12px}.candidate code{font-size:11px;overflow-wrap:anywhere}label{display:block;margin-top:10px}select,textarea{box-sizing:border-box;width:100%;font:inherit}table{border-collapse:collapse;background:white;min-width:600px}td,th{padding:10px 14px;border-bottom:1px solid #dce3ef;text-align:right}th:first-child{text-align:left}.table-wrap{overflow:auto}button{padding:10px 20px;cursor:pointer}pre{white-space:pre-wrap;overflow-wrap:anywhere}'
    css=css.replace('repeat(4,', 'repeat('+str(state['figures']['columns'])+',')
    return '<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+e(state['title'])+'</title><style>'+css+'</style><body>'+''.join(body)+'<script id="bundle-data" type="application/json">'+data_json+'</script><script>'+script+'</script></body></html>'


def build_bundle(manifest: dict, evidence_root: Path, output_root: Path) -> tuple[dict,Path]:
    state,assets=compile_bundle(manifest,evidence_root)
    target=output_root/state['snapshot_sha256'][:16]
    target.mkdir(parents=True,exist_ok=True)
    amap={a['id']:a for a in assets}
    for table in state['tables']:
        csv_text,tex=table_exports(table)
        safe='TABLE-'+digest(table['id'])[:12]
        _write(target/(safe+'.csv'),csv_text);_write(target/(safe+'.tex'),tex)
    for g in state['figures']['groups']:
        for c in g['candidates']:
            _write(target/'figures'/(c['id']+'.svg'),render_svg(amap[c['asset_id']],c))
    state['artifact_sha256'] = {str(p.relative_to(target)):hashlib.sha256(p.read_bytes()).hexdigest() for p in target.glob('figures/*.svg')}
    _json(target/'preparation.json',state)
    _json(target/'input-manifest.json',manifest)
    if 'external_reference_selection' in state:
        _json(target/'figure-reference-selection.json',state['external_reference_selection'])
    _write(target/'index.html',render_bundle_html(state))
    source_refs=[r for t in manifest.get('tables',[]) for r in t.get('result_refs',[])]+manifest.get('figure_asset_refs',[])
    _json(target/'provenance.json',{'snapshot_sha256':state['snapshot_sha256'],'source_refs':source_refs,'source_data_included':False,'renderer_sha256':state['renderer_sha256'],'reproduce':'python3 -m research_pipeline.experiment_data_preparation --manifest input-manifest.json --evidence-root ORIGINAL_EVIDENCE_ROOT --output OUTPUT_ROOT','scientific_authority':False})
    return state,target


def import_feedback(state: dict, feedback: dict, ledger: dict | None = None) -> dict:
    """Explicit import, version matching and idempotent append; not approval authority."""
    if feedback.get('snapshot_sha256')!=state['snapshot_sha256'] or feedback.get('paper_id')!=state['paper_id']:
        raise ValueError('stale-feedback-requires-reconfirmation')
    candidates={c['id']:c for g in state['figures']['groups'] for c in g['candidates']}
    ledger=ledger or {'schema_version':SCHEMA_VERSION,'events':[]}
    events=list(ledger.get('events',[])); seen={e.get('event_sha256') for e in events}
    for event in feedback.get('events',[]):
        c=candidates.get(event.get('id'))
        if not c or event.get('action') not in ACTIONS:raise ValueError('unknown-candidate-or-action')
        if any(event.get(k)!=c[k] for k in ('spec_sha256','data_sha256')):raise ValueError('stale-candidate-selection')
        row={'paper_id':state['paper_id'],'snapshot_sha256':state['snapshot_sha256'],'candidate_id':c['id'],'action':event['action'],
             'note':str(event.get('note',''))[:3000],'at':str(event.get('at',''))[:80],
             'data_sha256':c['data_sha256'],'spec_sha256':c['spec_sha256'],'origin':'OPERATOR_IMPORTED_FEEDBACK','scientific_authority':False}
        row['event_sha256']=digest(row)
        if row['event_sha256'] not in seen:events.append(row);seen.add(row['event_sha256'])
    return {'schema_version':SCHEMA_VERSION,'events':events,'scientific_authority':False}


def feedback_summary(state: dict, ledger: dict) -> dict:
    candidates={c['id']:c for g in state['figures']['groups'] for c in g['candidates']}
    current={}; stale=0
    for row in ledger.get('events',[]):
        cid=row.get('candidate_id'); c=candidates.get(cid)
        if row.get('paper_id')!=state['paper_id']: continue
        if not c or row.get('snapshot_sha256')!=state['snapshot_sha256'] or row.get('spec_sha256')!=c['spec_sha256']:
            stale+=1; continue
        current[cid]=row
    return {'selected':[cid for cid,r in current.items() if r['action']=='KEEP'],
            'revision_queue':[r for r in current.values() if r['action']=='REVISE'],
            'rejected':[cid for cid,r in current.items() if r['action']=='REJECT'],
            'unreviewed':[cid for cid in candidates if cid not in current],
            'stale_events':stale,'scientific_authority':False}


def write_handoff(state: dict, bundle_path: Path, ledger: dict) -> dict:
    """Prepare selected surfaces for the writer; actual-size/paper review stays pending."""
    review=feedback_summary(state,ledger)
    blockers=[]
    if state['source_errors']:blockers.append('source-errors')
    if any(t['gaps'] for t in state['tables']):blockers.append('table-gaps')
    if not review['selected']:blockers.append('no-current-operator-selection')
    selected=[]
    for cid in review['selected']:
        name='figures/'+cid+'.svg';path=bundle_path/name
        expected=state.get('artifact_sha256',{}).get(name)
        if not expected or not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
            blockers.append('rendered-artifact-drift:'+cid)
        else:selected.append({'candidate_id':cid,'path':name,'sha256':expected})
    handoff={'schema_version':SCHEMA_VERSION,'paper_id':state['paper_id'],'snapshot_sha256':state['snapshot_sha256'],
             'status':'PREPARATION_HANDOFF_BLOCKED' if blockers else 'MATERIALS_SELECTED_VISUAL_REVIEW_PENDING',
             'selected_figures':selected,'tables':[{'id':t['id'],'snapshot_sha256':t['snapshot_sha256']} for t in state['tables']],
             'review':review,'blockers':blockers,'actual_size_visual_review':'PENDING',
             'manuscript_prose_written':False,'scientific_authority':False,'submission_authority':False}
    _json(bundle_path/'handoff.json',handoff)
    return handoff


def import_feedback_file(state: dict, feedback: dict, ledger_path: Path) -> dict:
    """Exclusive writer; a held lock fails visibly rather than losing another review."""
    lock=ledger_path.with_name(ledger_path.name+'.lock')
    lock.parent.mkdir(parents=True,exist_ok=True)
    try: lock.mkdir()
    except FileExistsError as exc:raise ValueError('feedback-ledger-locked-no-overwrite') from exc
    try:
        old=_read(ledger_path) if ledger_path.exists() else None
        value=import_feedback(state,feedback,old);_json(ledger_path,value);return value
    finally:lock.rmdir()


def build_preparation_portfolio(project_root: Path = ROOT) -> dict:
    registry_path=project_root/'research_pipeline'/'data_preparation_registry.json'
    registry=_read(registry_path) if registry_path.exists() else {'bundles':[]}
    rows=[]
    for item in registry.get('bundles',[]):
        try:
            bundle=load_bound_json(project_root,item['ref'])
            rows.append({'paper_id':bundle['paper_id'],'status':bundle['status'],'tables':len(bundle['tables']),
                         'figure_candidates':sum(len(g['candidates']) for g in bundle['figures']['groups']),
                         'snapshot_sha256':bundle['snapshot_sha256']})
        except (ValueError,OSError,KeyError,TypeError) as exc:
            rows.append({'paper_id':item.get('paper_id',''),'status':'SOURCE_REVIEW_REQUIRED','reason':type(exc).__name__})
    knowledge_path=project_root/'generated'/'figure-curated.json'
    knowledge=_read(knowledge_path) if knowledge_path.exists() else {}
    return {'schema_version':SCHEMA_VERSION,'stage':'EXPERIMENT_DATA_PREPARATION','status':'REGISTERED_BUNDLES' if rows else 'WAIT_BOUND_RESULT_MANIFEST',
            'figure_knowledge_base':{'page':'figure-knowledge-base.html','summary':knowledge.get('summary',{}),'catalog_ref':'generated/figure-curated.json','catalog_version':knowledge.get('catalog_version'),'default_scope':'CURATED_ONLY','full_index_precedes_local_renderer_selection':False,'archive_requires_explicit_opt_in':True},
            'rows':rows,'catalog':[{'id':r[0],'data_kind':r[1],'label':r[2],'purpose':r[3]} for r in CATALOG],
            'workflow':['结果与版本清点','主表骨架','逐批验证回填','小改表与依赖刷新','数据—问题映射','精选参考匹配','一个主方案与一个备选','沿用脚本与局部修订','实际尺寸复核','写作输入材料包'],
            'interaction_policy':{'preview_columns':2,'default_rounds':1,'reference_limit':2,'candidate_limit':3,'force_four_candidates':False,'prefer_distinct_types':True,'never_fabricate_to_fill_slots':True,'browser_draft_is_not_server_save':True,'stale_selection_requires_reconfirmation':True},
            'scientific_authority':False,'model_calls':0,'experiments_launched':0}


def write_preparation_portfolio(project_root: Path = ROOT) -> dict:
    state=build_preparation_portfolio(project_root)
    _json(project_root/'generated'/'experiment-data-preparation.json',state)
    _write(project_root/'generated'/'experiment-data-preparation.js','window.EXPERIMENT_DATA_PREPARATION='+json.dumps(state,ensure_ascii=False,separators=(',',':'))+';\n')
    return state


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest',type=Path);p.add_argument('--evidence-root',type=Path);p.add_argument('--output',type=Path)
    p.add_argument('--feedback',type=Path);p.add_argument('--ledger',type=Path);p.add_argument('--project-root',type=Path,default=ROOT)
    p.add_argument('--previous-manifest',type=Path,help='Record layout versus experiment-design changes against this previous manifest')
    p.add_argument('--reference-brief',type=Path,help='Version-checked upstream figure shortlist exported from the full knowledge base')
    args=p.parse_args()
    if args.manifest:
        if not args.evidence_root or not args.output:p.error('--manifest requires --evidence-root and --output')
        manifest=_read(args.manifest)
        if args.reference_brief:manifest['figure_reference_brief']=_read(args.reference_brief)
        state,path=build_bundle(manifest,args.evidence_root,args.output)
        if args.previous_manifest:
            previous=_read(args.previous_manifest); old={t['id']:t for t in previous.get('tables',[])}; new={t['id']:t for t in manifest.get('tables',[])}
            changes=[{'table_id':tid,**layout_change(old[tid],new[tid],manifest.get('change_reason','operator manifest update'))} for tid in sorted(old.keys()&new.keys())]
            _json(path/'layout-change.json',{'previous_manifest_sha256':digest(previous),'current_manifest_sha256':digest(manifest),'changes':changes,'new_tables':sorted(new.keys()-old.keys()),'removed_tables':sorted(old.keys()-new.keys()),'outcome_seen_before_change':manifest.get('outcome_seen_before_change'),'automatic_rerun':False})
        if args.feedback:
            if not args.ledger:p.error('--feedback requires --ledger')
            ledger=import_feedback_file(state,_read(args.feedback),args.ledger)
            write_handoff(state,path,ledger)
        print(json.dumps({'status':state['status'],'output':str(path),'snapshot':state['snapshot_sha256']},ensure_ascii=False))
    else:print(json.dumps(write_preparation_portfolio(args.project_root),ensure_ascii=False))


if __name__=='__main__':main()
