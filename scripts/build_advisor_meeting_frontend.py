#!/usr/bin/env python3
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
GENERATED=ROOT/'generated'
OUT=GENERATED/'advisor-meeting-data.js'
manifest=json.loads((GENERATED/'advisor-paper-pack-manifest.json').read_text())
reality_bundle=json.loads((GENERATED/'advisor-reality-support.json').read_text())
resource_bundle=json.loads((GENERATED/'advisor-resource-ledger.json').read_text())
overlay_review=json.loads((GENERATED/'advisor-reality-cost-independent-review-20260905.json').read_text())
overlay_fix=json.loads((GENERATED/'advisor-reality-cost-fix-closure-20260905.json').read_text())
freeze_path=GENERATED/'advisor-meeting-freeze-20260906.json'
freeze_receipt=json.loads(freeze_path.read_text()) if freeze_path.exists() else {}

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
    if pid not in reality_bundle.get('papers',{}):
        raise RuntimeError(f'missing reality support for {pid}')
    if pid not in resource_bundle.get('papers',{}):
        raise RuntimeError(f'missing resource ledger for {pid}')
    row={
      'paper_id':pid,'order':order.index(pid)+1,'title':d['title'],'paper_status':d['paper_status'],
      'pages':d['pages'],'pdf_sha256':d['pdf_sha256'],'pdf':public_pdf,
      'paper_candidate_ref':d['paper_candidate_ref'],'scientific_canonical_ref':d['scientific_canonical_ref'],
      'science_delta':d['delta'],**decision_fields[pid],
      'reality_support':reality_bundle['papers'][pid],
      'resource_plan':resource_bundle['papers'][pid],
      'stanford':{'status':'PROCESSING'}
    }
    if review:
      exact_sha = review.get('pdf_sha256') == d['pdf_sha256']
      row['stanford']={k:review.get(k) for k in ['status','numerical_score','textual_signal','review_date','advisor_digest','token_fingerprint_sha256_16']}
      row['stanford']['reviewed_pdf_sha256']=review.get('pdf_sha256')
      row['stanford']['exact_current_pdf']=exact_sha
      if review.get('status')=='SUBMITTED':
        row['stanford']['status']='PROCESSING'
      elif not exact_sha:
        row['stanford']['status']='PRIOR_VERSION'
        row['stanford']['prior_version_note']='External review is for the immediately preceding PDF SHA, not the current meeting candidate.'
    papers.append(row)

shared=[
 {'id':'persistent-memory-object','label':'Persistent-memory object / state semantics','papers':['B1','C1','E2','PAPER_A','PAPER_B'],'question':'这些论文是否共享了一个未经充分验证的 persistent-state / memory semantics 前提？一个 closure 是否能同时给多篇降风险？'},
 {'id':'provenance-fidelity','label':'Provenance / source-fidelity distinction','papers':['B1','PAPER_A','PAPER_B'],'question':'provenance、source fidelity 与 longitudinal persistent utility 是否应拆成三篇，还是应形成 parent-child / merge 结构？'},
 {'id':'measurement-validity','label':'Measurement / evaluator validity','papers':['G1','C1','B1'],'question':'这些论文都在区分 observed measurement surface 与真正 scientific property；是否存在一个共享的 evaluator/measurement assumption 一旦失效会同时改变多篇结论？'},
 {'id':'representation-support','label':'Representation / identity support','papers':['E1','E2','C1'],'question':'identity/representation changes 是否只是各自 substrate artifact，还是 self-evolution control surface 的共同系统问题？'}]

schedule=[['14:00','14:15','Portfolio Dashboard + Common-Cause Risk Scan'],['14:15','14:40','E1'],['14:40','15:30','Memory / Provenance / Evolution family'],['15:30','15:55','G1 + Constraint Externality'],['15:55','16:10','3D'],['16:10','16:35','Exception-based nine-paper closure sweep'],['16:35','16:53','Cost / Dependencies / Scheduling'],['16:53','17:00','Read-back']]
route_summary={route:sum(p.get('route')==route for p in papers) for route in ['FREEZE_SUBMIT','EXECUTE_FROZEN','QUALIFY_FIRST','FORMALIZE_FIRST']}
g2_path=GENERATED/'stanford-g2-mcta-review.json'
g2=json.loads(g2_path.read_text()) if g2_path.exists() else None
spinoffs=[]
if g2:
    spinoffs.append({
      'paper_id':'G2_CANDIDATE','title':g2.get('title'),'status':'HOLD_FOR_IDENTIFICATION',
      'relation':'Separate MCTA capability-matching protocol candidate; not a later revision of G1/ERTA.',
      'stanford':{k:g2.get(k) for k in ['numerical_score','textual_signal','review_date','advisor_digest']}
    })
data={'schema_version':'3.2','generated_at':'2026-09-06','meeting':{'id':'2026-09-06-advisor','main_ref':manifest['meeting_candidate_main'],'status':manifest.get('paper_pack_status'),'review_route':'exception-and-boundary-review','freeze_status':freeze_receipt.get('status'),'candidate_hash':freeze_receipt.get('meeting_candidate_hash')},'route_summary':route_summary,'papers':papers,'spinoffs':spinoffs,'shared_risks':shared,'resource_pricing_basis':resource_bundle.get('pricing_basis',{}),'portfolio_schedule':resource_bundle.get('portfolio_schedule',[]),'overlay_audit':{'independent_verdict':overlay_review.get('response',{}).get('final_verdict'),'postfix_status':overlay_fix.get('status'),'verification_path':overlay_fix.get('postfix_verification_path'),'model_slug':overlay_review.get('browser_evidence',{}).get('message_model_slug'),'extra_high':overlay_review.get('browser_evidence',{}).get('extra_high_visible'),'authority':overlay_review.get('authority',{}),'stale_for_papers':['C1','G1'],'stale_reason':'C1 story and G1 lineage were materially corrected after the prior reality/cost overlay review; their current decision cards supersede the old object.'},'schedule':[{'start':a,'end':b,'label':c} for a,b,c in schedule]}
OUT.write_text('window.ADVISOR_MEETING_DATA = '+json.dumps(data,ensure_ascii=False,indent=2)+';\n')
print(OUT)
print('papers',len(papers),'review_ready',sum((p['stanford'].get('status')=='READY') for p in papers))
