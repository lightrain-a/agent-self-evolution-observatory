"""Full upstream visual index + reusable selection knowledge (no upstream code execution).

Consumes complete, commit-pinned GitHub tree receipts; indexes every visual asset,
recipe card and tutorial within the declared scope. External images are direct source
references, never mirrored here. A filename-derived family remains provisional.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import hashlib
import json
from pathlib import Path,PurePosixPath
import re
from urllib.parse import quote
from .figure_knowledge_taxonomy import FAMILIES, classify, normalized

ROOT=Path(__file__).resolve().parents[1]
IMAGE_EXT={'.png','.jpg','.jpeg','.gif','.webp','.svg','.avif'}
VISUAL_EXT=IMAGE_EXT|{'.pdf'}
SOURCES={
 'vivid-figures-skill':{'id':'vivid','name':'Vivid Figures','repo':'yjz211/vivid-figures-skill','license':'Personal Non-Commercial License; restrictive; no template/code redistribution','author':'yjz211'},
 'figures4papers':{'id':'f4p','name':'figures4papers','repo':'ChenLiu-1996/figures4papers','license':'CC BY-NC 4.0','author':'Chen Liu'},
 'The-Python-Graph-Gallery':{'id':'pgg','name':'Python Graph Gallery','repo':'holtzy/The-Python-Graph-Gallery','license':'0BSD at repository level; individual examples may contain third-party content','author':'holtzy and gallery contributors'},
 'great-tables':{'id':'gt','name':'Great Tables','repo':'posit-dev/great-tables','license':'MIT at repository level; third-party illustrations retain their rights','author':'Posit and contributors'},
}


def sha(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()


def source_url(source,path,raw=False):
    base='https://raw.githubusercontent.com/' if raw else 'https://github.com/'
    return base+source['repo']+('/' if raw else '/blob/')+source['commit']+'/'+quote(path,safe='/')


def _title(path):
    stem=PurePosixPath(path).stem
    return re.sub(r'\s+',' ',re.sub(r'[_-]+',' ',stem)).strip()


def _aux(path,source_id):
    low=path.lower()
    if source_id=='vivid':return not low.startswith('catalog/previews/')
    if source_id=='pgg':return not low.startswith(('static/graph/','static/animations/','static/table/'))
    if source_id=='gt':
        return any(t in low for t in ('logo','icons/','sports-earnings/','metro_images/','discord','linkedin','pr-jerry','tablet','amtrak','routing','route2','route-bx1','cave_grids','computer_tables','visicalc','service-patterns','locations-map'))
    return False


def _related_code(path,source,files):
    """Only existing paths. Non-exact matches are candidates, not verified bindings."""
    stem=PurePosixPath(path).stem
    if source['id']=='vivid':
        rid=re.sub(r'-\d+$','',stem)
        direct=[p for p in (f'catalog/sources/{rid}/render.py',f'catalog/sources/{rid}/recipe.md',f'catalog/cards/{rid}.md') if p in files]
        return [{'path':p,'url':source_url(source,p),'relation':'RECIPE_ID_MATCH'} for p in direct]
    if source['id']=='pgg':
        number=re.match(r'^(\d+)',stem)
        candidates=[p for p in files if p.startswith('src/notebooks/') and p.endswith('.ipynb') and ((number and re.match(r'^'+re.escape(number[1])+r'[-_ ]',PurePosixPath(p).name)) or normalized(PurePosixPath(p).stem)==normalized(stem))]
        return [{'path':p,'url':source_url(source,p),'relation':'EXISTING_FILENAME_CANDIDATE_REVIEW_REQUIRED'} for p in sorted(candidates)]
    if source['id']=='f4p':
        project=path.split('/')[0]
        exact=[p for p in files if p.startswith(project+'/') and p.endswith('.py') and normalized(PurePosixPath(p).stem.replace('plot_',''))==normalized(stem)]
        candidates=exact or [p for p in files if p.startswith(project+'/') and p.endswith('.py')]
        return [{'path':p,'url':source_url(source,p),'relation':'EXACT_STEM_MATCH' if exact else 'PROJECT_SCRIPT_CANDIDATE_REVIEW_REQUIRED'} for p in sorted(candidates)]
    parent=str(PurePosixPath(path).parent)
    return [{'path':p,'url':source_url(source,p),'relation':'SAME_DIRECTORY_GUIDE'} for p in sorted(files) if p.startswith(parent+'/') and p.endswith('.qmd') and str(PurePosixPath(p).parent)==parent]


def _new_entry(source,path,kind,files):
    families=['table'] if source['id']=='gt' and kind in {'TABLE_GUIDE','TABLE_EXAMPLE'} else classify(_title(path),path)
    related=_related_code(path,source,files)
    if families==['unclassified'] and len(related)==1:
        families=classify(_title(related[0]['path']),related[0]['path'])
    if source['id']=='f4p' and families==['unclassified']:
        if any(x in path.lower() for x in ('comparison','correctness','rewriting','selfcorrection','results_')):families=['grouped_bar']
        elif 'contrastive' in path.lower():families=['schematic']
        elif path.startswith('scientific-figure-making/'):families=['layout']
    ident=source['id']+'-'+hashlib.sha256((kind+'|'+path).encode()).hexdigest()[:14]
    return {'id':ident,'source_id':source['id'],'source_name':source['name'],'kind':kind,
            'title':_title(path),'title_basis':'UPSTREAM_FILENAME_NOT_REWRITTEN_CAPTION',
            'path':path,'source_url':source_url(source,path),'commit':source['commit'],
            'families':families,'data_kinds':sorted({k for f in families for k in FAMILIES[f]['data_kinds']}),
            'annotation_status':'FILENAME_BASED_REVIEW_REQUIRED','visual_reviewed':False,
            'previews':[],'thumbnails':[],'documents':[],'source_files':[], 'related_code':related,
            'license':source['license'],'license_url':source_url(source,'LICENSE'),'author':source['author'],
            'local_recipes':sorted({FAMILIES[f]['local_recipe'] for f in families if FAMILIES[f]['local_recipe']}),
            'implementation_status':'REFERENCE_INDEX_NOT_INSTALLED','scientific_authority':False}


def build_knowledge_base(receipts:dict[str,dict])->dict:
    entries=[];sources=[];coverage=[]
    for key,policy in SOURCES.items():
        receipt=receipts[key]
        if receipt.get('repo')!=policy['repo']:raise ValueError('repository-identity-mismatch:'+key)
        tree=receipt['tree']
        if tree.get('truncated') is not False:raise ValueError('complete-tree-receipt-required:'+key)
        source={**policy,'commit':receipt['sha'],'commit_date':receipt['date'],'tree_sha':tree.get('sha'),'tree_truncated':False}
        if not re.fullmatch(r'[a-f0-9]{40}',source['commit']):raise ValueError('unpinned-repository:'+key)
        files={r['path']:r for r in tree['tree'] if r.get('type')=='blob'}
        visuals={p:r for p,r in files.items() if PurePosixPath(p).suffix.lower() in VISUAL_EXT}
        source_entries=[];mapped={};by_stem={}
        if source['id']=='vivid':
            cards=sorted(p for p in files if p.startswith('catalog/cards/') and p.endswith('.md'))
            for p in cards:
                e=_new_entry(source,p,'RECIPE_CARD',files);rid=PurePosixPath(p).stem
                e['title']=rid;by_stem['catalog/previews/'+rid]=e;source_entries.append(e)
        for p,r in sorted(visuals.items()):
            ext=PurePosixPath(p).suffix.lower();stem=str(PurePosixPath(p).with_suffix(''))
            is_vivid_thumb=source['id']=='vivid' and p.startswith('catalog/thumbnails/')
            vivid_preview=source['id']=='vivid' and p.startswith(('catalog/previews/','catalog/thumbnails/'))
            key_stem=re.sub(r'-\d+$','',stem.replace('catalog/thumbnails/','catalog/previews/')) if vivid_preview else stem
            e=by_stem.get(key_stem)
            if e is None:
                auxiliary=_aux(p,source['id'])
                kind='SUPPORT_ASSET' if auxiliary else ('TABLE_EXAMPLE' if source['id']=='gt' or p.startswith('static/table/') else 'FIGURE_EXAMPLE')
                e=_new_entry(source,p,kind,files);by_stem[key_stem]=e;source_entries.append(e)
            asset={'path':p,'blob_sha':r['sha'],'bytes':r.get('size'), 'url':source_url(source,p,raw=True),'source_url':source_url(source,p),'format':ext[1:]}
            e['thumbnails' if is_vivid_thumb else 'documents' if ext=='.pdf' else 'previews'].append(asset)
            e['source_files'].append({'path':p,'blob_sha':r['sha']});mapped[p]=e['id']
        # The notebook/tutorial corpus remains individually findable even when no preview is released.
        tutorials=[]
        if source['id']=='pgg':tutorials=[p for p in files if p.startswith('src/notebooks/') and p.endswith('.ipynb') and '.ipynb_checkpoints' not in p]
        elif source['id']=='gt':tutorials=[p for p in files if p.endswith('.qmd') and p.startswith(('examples/','user_guide/','blog/'))]
        elif source['id']=='f4p':tutorials=[p for p in files if p.startswith('scientific-figure-making/') and p.endswith('.md')]
        for p in sorted(tutorials):
            e=_new_entry(source,p,'TABLE_GUIDE' if source['id']=='gt' else 'TUTORIAL',files)
            e['source_files']=[{'path':p,'blob_sha':files[p]['sha']}]
            e['related_code']=[{'path':p,'url':source_url(source,p),'relation':'SELF_SOURCE'}]
            # Attach only previews explicitly associated to this existing code candidate; label the relation.
            for v in source_entries:
                if any(c['path']==p for c in v['related_code']):
                    e['previews'].extend(v['previews'])
            e['preview_association']='FILENAME_OR_DIRECTORY_CANDIDATE_VERIFY_BEFORE_USE'
            source_entries.append(e)
        exact_seen={}
        for e in source_entries:
            thumbs={PurePosixPath(t['path']).stem:t for t in e['thumbnails']}
            for preview in e['previews']:
                thumb=thumbs.get(PurePosixPath(preview['path']).stem)
                if thumb:preview['thumbnail_url']=thumb['url']
            blobs=tuple(sorted(f['blob_sha'] for f in e['source_files']))
            if blobs and blobs in exact_seen:e['exact_duplicate_of']=exact_seen[blobs]
            elif blobs:exact_seen[blobs]=e['id']
            e['content_version']=sha({'commit':source['commit'],'files':e['source_files'],'families':e['families']})
        missing=set(visuals)-set(mapped)
        if missing:raise ValueError('unindexed-visual-assets:'+key)
        kinds=Counter(e['kind'] for e in source_entries)
        coverage.append({'source_id':source['id'],'repo':source['repo'],'commit':source['commit'],'complete_tree':True,
                         'tree_files':len(files),'visual_files':len(visuals),'image_files':sum(PurePosixPath(p).suffix.lower() in IMAGE_EXT for p in visuals),
                         'pdf_files':sum(p.endswith('.pdf') for p in visuals),'indexed_visual_files':len(mapped),'unindexed_visual_files':0,
                         'entries':len(source_entries),'released_recipe_previews':sum(len(e['previews']) for e in source_entries if e['kind']=='RECIPE_CARD'),
                         'attached_thumbnails':sum(len(e['thumbnails']) for e in source_entries),'entry_kinds':dict(kinds),'exact_duplicate_entries':sum('exact_duplicate_of' in e for e in source_entries),
                         'path_to_entry':mapped})
        sources.append(source);entries.extend(source_entries)
    # More specific cards first, but all source records remain available to filters and show-all.
    order={s['id']:i for i,s in enumerate(sources)}
    kindorder={'RECIPE_CARD':0,'FIGURE_EXAMPLE':1,'TABLE_EXAMPLE':2,'TUTORIAL':3,'TABLE_GUIDE':4,'SUPPORT_ASSET':5}
    entries.sort(key=lambda e:(order[e['source_id']],kindorder[e['kind']],e['path']))
    counts=Counter(f for e in entries for f in e['families'])
    summary={'repositories':len(sources),'entries':len(entries),'selectable_examples':sum(e['kind'] in {'RECIPE_CARD','FIGURE_EXAMPLE','TABLE_EXAMPLE'} for e in entries),
             'tutorial_entries':sum(e['kind'] in {'TUTORIAL','TABLE_GUIDE'} for e in entries),'support_entries':sum(e['kind']=='SUPPORT_ASSET' for e in entries),
             'visual_files':sum(c['visual_files'] for c in coverage),'indexed_visual_files':sum(c['indexed_visual_files'] for c in coverage),
             'recipe_cards':sum(e['kind']=='RECIPE_CARD' for e in entries),'with_preview':sum(bool(e['previews']) for e in entries),
             'without_preview':sum(not e['previews'] for e in entries),'family_tags':len(FAMILIES)-1,'unclassified_entries':counts['unclassified'],
             'local_renderer_count':19,'upstream_code_executed':0,'images_mirrored':0}
    return {'schema_version':'1.0','checked_on':'2026-09-27','sources':sources,'families':list(FAMILIES.values()),'entries':entries,'coverage':coverage,'summary':summary,
            'policy':{'source_examples_are_not_local_renderers':True,'all_visual_assets_accounted_for':True,'support_assets_are_not_chart_types':True,
                      'filename_annotations_require_review':True,'no_private_result_data':True,'upstream_images_are_direct_references_not_mirrors':True,
                      'licenses_do_not_grant_automatic_template_reuse':True,'missing_previews_are_explicit':True},'scientific_authority':False}


def search_knowledge(kb:dict,query='',data_kinds=None,limit=20,include_support=False,source_id=None):
    tokens=normalized(query).split(); data_kinds=set(data_kinds or [])
    scored=[]
    for e in kb['entries']:
        if source_id and e['source_id']!=source_id:continue
        if not include_support and e['kind']=='SUPPORT_ASSET':continue
        if data_kinds and not data_kinds.intersection(e['data_kinds']):continue
        families=[FAMILIES[f] for f in e['families']]
        text=normalized(' '.join([e['title'],e['path'],e['source_name']]+[f['label']+' '+f['group']+' '+f['question']+' '+' '.join(f['terms']) for f in families]))
        words=set(text.split())
        if tokens and not all((t in text if re.search(r'[\u4e00-\u9fff]',t) else t in words) for t in tokens):continue
        score=sum(4 if t in normalized(e['title']) else 1 for t in tokens)+int(bool(e['previews']))*2+int(e['kind']=='RECIPE_CARD')
        scored.append((score,e))
    scored.sort(key=lambda item:(-item[0],item[1]['id']))
    return [e for _,e in scored[:limit]]


def selection_brief(kb:dict,entry_ids:list[str],question:str,data_fields:list[str]):
    index={e['id']:e for e in kb['entries']};entries=[]
    if len(entry_ids)!=len(set(entry_ids)):raise ValueError('duplicate-selection')
    for eid in entry_ids:
        if eid not in index:raise ValueError('unknown-entry:'+eid)
        e=index[eid]
        entries.append({'entry_id':eid,'content_version':e['content_version'],'source_url':e['source_url'],'commit':e['commit'],
                        'preview_urls':[p['url'] for p in e['previews']],'source_candidates':e['related_code'],
                        'family_guidance':[FAMILIES[f] for f in e['families']], 'license':e['license'],
                        'annotation_status':e['annotation_status'],'implementation_status':'ADAPTATION_AND_DATA_REVIEW_REQUIRED'})
    return {'schema_version':'1.0','purpose':question,'provided_data_fields':data_fields,'entries':entries,
            'requested_layout':{'columns':4,'prefer_distinct_types':True},'executes_code':False,'scientific_authority':False}


def validate_reference_selection(kb:dict,brief:dict)->list[str]:
    """Validate an exported reference selection, not experimental or reuse permission."""
    index={e['id']:e for e in kb['entries']};ids=[]
    for row in brief.get('entries',[]):
        eid=row.get('entry_id');entry=index.get(eid)
        if not entry:raise ValueError('unknown-reference-entry:'+str(eid))
        if row.get('content_version')!=entry['content_version'] or row.get('commit')!=entry['commit']:
            raise ValueError('reference-version-changed-reselect:'+eid)
        if eid in ids:raise ValueError('duplicate-reference-selection:'+eid)
        ids.append(eid)
    return ids


def write_knowledge(kb:dict,root:Path):
    generated=root/'generated';generated.mkdir(exist_ok=True)
    payload={k:v for k,v in kb.items() if k!='coverage'}
    compact={'schema_version':'1.0','checked_on':kb['checked_on'],'summary':kb['summary'],'sources':kb['sources'],'page':'figure-knowledge-base.html','scientific_authority':False}
    (generated/'figure-knowledge-summary.json').write_text(json.dumps(compact,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (generated/'figure-knowledge-summary.js').write_text('window.FIGURE_KNOWLEDGE_SUMMARY='+json.dumps(compact,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    (generated/'figure-knowledge-base.json').write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    (generated/'figure-knowledge-base.js').write_text('window.FIGURE_KNOWLEDGE_BASE='+json.dumps(payload,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    (generated/'figure-knowledge-coverage.json').write_text(json.dumps({'checked_on':kb['checked_on'],'summary':kb['summary'],'sources':kb['sources'],'coverage':kb['coverage']},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# 科研图表知识库：完整来源索引','', '> 图例数量、图片文件数、图型家族和本地渲染器数量分别统计。所有具体条目可在前端查看；文件名标签尚需逐图核对。','',
           '页面： https://agent-evolution.lightrain.asia/figure-knowledge-base.html','', '## 覆盖范围','', '| 仓库 | 条目 | 视觉文件 | 已索引 | 版本 |','|---|---:|---:|---:|---|']
    for c in kb['coverage']:lines.append(f"| {c['repo']} | {c['entries']} | {c['visual_files']} | {c['indexed_visual_files']} | `{c['commit'][:12]}` |")
    lines+=['','## 选图知识','']
    for f in kb['families']:
        lines += [f"### {f['label']}",f"用途：{f['question']}",f"输入：{', '.join(f['required_fields']) or '需查看具体资料'}",f"注意：{f['caution']}",'']
    lines+=['## 全部条目','']
    for source in kb['sources']:
        lines += [f"### {source['name']}",f"来源版本：`{source['commit']}`。许可：{source['license']}。",'']
        for e in kb['entries']:
            if e['source_id']!=source['id']:continue
            lines.append(f"- `{e['id']}` [{e['title']}]({e['source_url']}) · {e['kind']} · 预览 {len(e['previews'])} · {' / '.join(FAMILIES[f]['label'] for f in e['families'])}")
    doc=root/'docs'/'figure-knowledge-base-index.md';doc.parent.mkdir(exist_ok=True);doc.write_text('\n'.join(lines)+'\n',encoding='utf-8')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tree-receipts',type=Path);p.add_argument('--root',type=Path,default=ROOT)
    p.add_argument('--search');p.add_argument('--data-kind',action='append');p.add_argument('--limit',type=int,default=20)
    args=p.parse_args()
    if args.tree_receipts:
        receipts={k:json.loads((args.tree_receipts/(k+'.json')).read_text()) for k in SOURCES}
        kb=build_knowledge_base(receipts);write_knowledge(kb,args.root);print(json.dumps(kb['summary'],ensure_ascii=False))
    else:
        kb=json.loads((args.root/'generated'/'figure-knowledge-base.json').read_text());rows=search_knowledge(kb,args.search or '',args.data_kind,args.limit)
        print(json.dumps([{'id':e['id'],'title':e['title'],'families':e['families'],'source_url':e['source_url'],'previews':len(e['previews'])} for e in rows],ensure_ascii=False,indent=2))

if __name__=='__main__':main()
