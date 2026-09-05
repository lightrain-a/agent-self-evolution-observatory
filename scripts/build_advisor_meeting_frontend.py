#!/usr/bin/env python3
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
GENERATED=ROOT/'generated'
OUT=GENERATED/'advisor-meeting-data.js'
manifest=json.loads((GENERATED/'advisor-paper-pack-manifest.json').read_text())

order=['E1','B1','C1','G1','E2','PAPER_A','CONSTRAINT_EXTERNALITY','PAPER_B','3D']
decision_fields={}
for source in sorted((GENERATED/'advisor-decision-cards').glob('*.json')):
    card=json.loads(source.read_text())
    decision_fields[card['paper_id']]=card
missing_cards=[pid for pid in order if pid not in decision_fields]
if missing_cards:
    raise RuntimeError(f'missing advisor decision cards: {missing_cards}')
papers=[]
for d in manifest['papers']:
    pid=d['paper_id']
    review_path=GENERATED/f"stanford-{pid.lower()}-review.json"
    review=json.loads(review_path.read_text()) if review_path.exists() else None
    public_pdf='downloads/advisor-20260906/'+d['filename']
    row={
      'paper_id':pid,'order':order.index(pid)+1,'title':d['title'],'paper_status':d['paper_status'],
      'pages':d['pages'],'pdf_sha256':d['pdf_sha256'],'pdf':public_pdf,
      'paper_candidate_ref':d['paper_candidate_ref'],'scientific_canonical_ref':d['scientific_canonical_ref'],
      'science_delta':d['delta'],**decision_fields[pid],
      'stanford':{'status':'PROCESSING'}
    }
    if review:
      row['stanford']={k:review.get(k) for k in ['status','numerical_score','textual_signal','review_date','advisor_digest','token_fingerprint_sha256_16']}
      if review.get('status')=='SUBMITTED': row['stanford']['status']='PROCESSING'
    papers.append(row)

shared=[
 {'id':'persistent-memory-object','label':'Persistent-memory object / state semantics','papers':['B1','C1','E2','PAPER_A','PAPER_B'],'question':'这些论文是否共享了一个未经充分验证的 persistent-state / memory semantics 前提？一个 closure 是否能同时给多篇降风险？'},
 {'id':'provenance-fidelity','label':'Provenance / source-fidelity distinction','papers':['B1','PAPER_A','PAPER_B'],'question':'provenance、source fidelity 与 longitudinal persistent utility 是否应拆成三篇，还是应形成 parent-child / merge 结构？'},
 {'id':'controlled-update','label':'Controlled update and capability preservation','papers':['G1','CONSTRAINT_EXTERNALITY'],'question':'安全 capability confound 与 update collateral 是否共享一个更高层 controlled-update scientific object？'},
 {'id':'representation-support','label':'Representation / identity support','papers':['E1','E2','C1'],'question':'identity/representation changes 是否只是各自 substrate artifact，还是 self-evolution control surface 的共同系统问题？'}]

schedule=[['14:00','14:15','Portfolio Dashboard + Common-Cause Risk Scan'],['14:15','14:40','E1'],['14:40','15:30','Memory / Provenance / Evolution family'],['15:30','15:55','G1 + Constraint Externality'],['15:55','16:10','3D'],['16:10','16:35','Exception-based nine-paper closure sweep'],['16:35','16:53','Cost / Dependencies / Scheduling'],['16:53','17:00','Read-back']]
route_summary={route:sum(p.get('route')==route for p in papers) for route in ['FREEZE_SUBMIT','EXECUTE_FROZEN','QUALIFY_FIRST','FORMALIZE_FIRST']}
data={'schema_version':'2.0','generated_at':'2026-09-05','meeting':{'id':'2026-09-06-advisor','main_ref':manifest['meeting_candidate_main'],'status':manifest.get('paper_pack_status'),'review_route':'exception-and-boundary-review'},'route_summary':route_summary,'papers':papers,'shared_risks':shared,'schedule':[{'start':a,'end':b,'label':c} for a,b,c in schedule]}
OUT.write_text('window.ADVISOR_MEETING_DATA = '+json.dumps(data,ensure_ascii=False,indent=2)+';\n')
print(OUT)
print('papers',len(papers),'review_ready',sum((p['stanford'].get('status')=='READY') for p in papers))
