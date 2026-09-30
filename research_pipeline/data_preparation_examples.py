"""Explicit SYNTHETIC_DEMO fixtures. Never experiment results or HEIRS data."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path


def create_demo_inputs(root: Path) -> dict:
    root.mkdir(parents=True,exist_ok=True)
    refs=[]
    common={'protocol_id':'DEMO-P1','split_id':'DEMO-ONLY','metric_id':'success','unit':'percent','analysis_unit':'synthetic task','cohort_sha256':'synthetic-panel'}
    columns=[]
    for cid,n,group in [('within-a',20,'Within group'),('within-b',20,'Within group'),('cross-a',20,'Cross group')]:
        columns.append({'id':cid,'label':cid,**common,'dataset_id':'SYNTHETIC','condition_id':cid,'expected_total':n,'group':group,'direction':'higher'})
    columns.insert(2,{'id':'within-avg','label':'Within Avg','aggregate':'macro','members':['within-a','within-b'],'group':'Within group'})
    columns.append({'id':'cross-avg','label':'Cross Avg','aggregate':'macro','members':['cross-a'],'group':'Cross group'})
    rows=[{'id':x,'label':x} for x in ('Reference','Variant A','Variant B')]
    results=[]
    for i,row in enumerate(rows):
        for j,col in enumerate(c for c in columns if not c.get('aggregate')):
            results.append({**common,'result_id':f'DEMO-{i}-{j}','method_id':row['id'],'column_id':col['id'],
                           'dataset_id':'SYNTHETIC','condition_id':col['id'],'status':'COMPLETE','kind':'rate','successes':8+i*3-j,'total':20})
    def asset(aid,kind,question,**kwargs):
        return dict(id=aid,kind=kind,question=question,scope='Synthetic workflow demonstration only',claim_id='DEMO-NO-SCIENTIFIC-CLAIM',
                    unit='percent',analysis_unit='synthetic observation',status='COMPLETE',data_role='SYNTHETIC_DEMO',**kwargs)
    assets=[
        asset('DEMO-categories','categorical','SYNTHETIC DEMO: category comparison',rows=[{'id':str(i),'label':x,'value':v} for i,(x,v) in enumerate([('Reference',40),('Variant A',55),('Variant B',70),('Stress',0)])]),
        asset('DEMO-paired','paired','SYNTHETIC DEMO: paired improvements and regressions',pairing_definition='same synthetic ID in both conditions',rows=[{'id':str(i),'label':'Unit '+str(i+1),'before':a,'after':b} for i,(a,b) in enumerate([(40,65),(55,50),(30,50),(70,68),(50,76)])]),
        asset('DEMO-samples','samples','SYNTHETIC DEMO: distribution and tail behavior',rows=[{'id':str(i)+'-'+g,'group':g,'value':v} for g,vs in [('Reference',[31,38,41,47,53,56,63,67,71,75,78,82]),('Variant',[39,43,49,52,61,66,68,73,77,82,85,89])] for i,v in enumerate(vs)]),
        asset('DEMO-series','series','SYNTHETIC DEMO: observed budget sequence',x_unit='logical evaluations',y_unit='percent',rows=[{'id':str(i)+'-'+g,'group':g,'x':x,'y':v} for g,vs in [('Reference',[40,45,46,47]),('Variant',[40,50,59,63])] for i,(x,v) in enumerate(zip([4,8,16,32],vs))]),
        asset('DEMO-xy','xy','SYNTHETIC DEMO: cost and utility',x_unit='logical evaluations',y_unit='percent',size_unit='synthetic count',rows=[{'id':str(i),'label':str(i),'x':x,'y':y,'size':s} for i,(x,y,s) in enumerate([(10,30,4),(20,46,8),(30,57,12),(50,63,15)])]),
        asset('DEMO-matrix','matrix','SYNTHETIC DEMO: heterogeneous effects',row_labels=['Reference','Variant A','Variant B'],column_labels=['Task A','Task B','Task C','Task D'],values=[[0,3,-2,1],[2,6,None,3],[4,7,-1,5]]),
        asset('DEMO-interval','interval','SYNTHETIC DEMO: declared confidence intervals',interval_kind='CI',interval_source='Constructed interval fixture, not inferred uncertainty',confidence_level=.95,rows=[{'id':str(i),'label':'Case '+str(i+1),'value':v,'lower':v-3,'upper':v+4} for i,v in enumerate([1,-2,7,4])]),
    ]
    source=root/'synthetic-evidence.json'
    source.write_text(json.dumps({'notice':'SYNTHETIC_DEMO — not scientific data','results':results,'assets':assets},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    sha=hashlib.sha256(source.read_bytes()).hexdigest()
    bind=lambda pointer:{'path':source.name,'sha256':sha,'pointer':pointer}
    manifest={'schema_version':'1.0','paper_id':'SYNTHETIC-DEMO-NOT-HEIRS','title':'Synthetic demo · tables and four-column figure alternatives',
              'preview_rounds':3,'preview_columns':4,'figure_style':{'font_family':'Georgia, serif','theme':'paper-vivid'},
              'tables':[{'id':'DEMO-TABLE-1','label':'Synthetic demo table — not research results','rows':rows,'columns':columns,'digits':1,'delta_reference':'Reference','result_refs':[bind('/results/'+str(i)) for i in range(len(results))]}],
              'figure_asset_refs':[bind('/assets/'+str(i)) for i in range(len(assets))]}
    (root/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return manifest
