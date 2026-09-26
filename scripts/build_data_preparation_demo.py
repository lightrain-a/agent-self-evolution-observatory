#!/usr/bin/env python3
"""Build a clearly labeled synthetic integration demo, never scientific results."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from research_pipeline.data_preparation_examples import create_demo_inputs
from research_pipeline.experiment_data_preparation import build_bundle


def main():
    evidence=ROOT/'data-preparation-demo'/'synthetic-inputs'
    manifest=create_demo_inputs(evidence)
    state,path=build_bundle(manifest,evidence,ROOT/'data-preparation-demo'/'previews')
    figures=[]
    for group in state['figures']['groups']:
        for c in group['candidates']:
            figures.append({'id':c['id'],'recipe':c['recipe'],'label':c['recipe_label'],'url':str((path/'figures'/(c['id']+'.svg')).relative_to(ROOT)),'role':'SYNTHETIC_DEMO'})
    receipt={'schema_version':'1.0','is_synthetic':True,'not_heirs_data':True,'not_current_paper_results':True,
             'snapshot_sha256':state['snapshot_sha256'],'url':str((path/'index.html').relative_to(ROOT)),
             'groups':len(state['figures']['groups']),'figures':figures,'scientific_authority':False}
    (ROOT/'generated'/'data-preparation-demo.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/'generated'/'data-preparation-demo.js').write_text('window.DATA_PREPARATION_DEMO='+json.dumps(receipt,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    print(json.dumps({'demo_url':receipt['url'],'groups':receipt['groups'],'synthetic_figures':len(figures)},ensure_ascii=False))

if __name__=='__main__':main()
