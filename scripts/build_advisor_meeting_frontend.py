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
final_sufficiency=json.loads((GENERATED/'advisor-final-decision-sufficiency-review-20260906.json').read_text())
agenda=json.loads((GENERATED/'advisor-meeting-agenda-20260906.json').read_text())

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
      row['stanford']={k:review.get(k) for k in ['status','numerical_score','textual_signal','review_date','advisor_digest','token_fingerprint_sha256_16']}
      if review.get('status')=='SUBMITTED': row['stanford']['status']='PROCESSING'
    papers.append(row)

claim_ownership_map=agenda['claim_ownership_map']
shared=agenda['shared_risks']
shared_risk_reopen_rules=agenda['shared_risk_reopen_rules']
meeting_outputs=agenda['meeting_outputs']
schedule=agenda['schedule']

route_summary={route:sum(p.get('route')==route for p in papers) for route in ['FREEZE_SUBMIT','EXECUTE_FROZEN','QUALIFY_FIRST','FORMALIZE_FIRST']}
data={'schema_version':'3.2','generated_at':'2026-09-06','meeting':{'id':'2026-09-06-advisor','main_ref':manifest['meeting_candidate_main'],'status':manifest.get('paper_pack_status'),'review_route':'exception-and-boundary-review','freeze_status':freeze_receipt.get('status'),'candidate_hash':freeze_receipt.get('meeting_candidate_hash')},'route_summary':route_summary,'papers':papers,'shared_risks':shared,'claim_ownership_map':claim_ownership_map,'shared_risk_reopen_rules':shared_risk_reopen_rules,'meeting_outputs':meeting_outputs,'resource_pricing_basis':resource_bundle.get('pricing_basis',{}),'portfolio_schedule':resource_bundle.get('portfolio_schedule',[]),'overlay_audit':{'independent_verdict':overlay_review.get('response',{}).get('final_verdict'),'postfix_status':overlay_fix.get('status'),'verification_path':overlay_fix.get('postfix_verification_path'),'final_sufficiency_verdict':final_sufficiency.get('verdict'),'final_sufficiency_status':final_sufficiency.get('status'),'model_slug':overlay_review.get('browser_evidence',{}).get('message_model_slug'),'extra_high':overlay_review.get('browser_evidence',{}).get('extra_high_visible'),'authority':overlay_review.get('authority',{})},'do_not_spend_advisor_time_on':agenda.get('do_not_spend_advisor_time_on',[]),'schedule':schedule}
OUT.write_text('window.ADVISOR_MEETING_DATA = '+json.dumps(data,ensure_ascii=False,indent=2)+';\n')
print(OUT)
print('papers',len(papers),'review_ready',sum((p['stanford'].get('status')=='READY') for p in papers))
