#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];G=ROOT/'generated'
ORDER=['E1','B1','C1','G1','E2','PAPER_A','CONSTRAINT_EXTERNALITY','PAPER_B','3D']
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical_hash(paths):
 rows=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted(paths,key=lambda x:str(x.relative_to(ROOT)))]
 payload=json.dumps(rows,ensure_ascii=False,separators=(',',':'),sort_keys=True).encode()
 return hashlib.sha256(payload).hexdigest(),rows
manifest=load(G/'advisor-paper-pack-manifest.json'); reality=load(G/'advisor-reality-support.json'); resources=load(G/'advisor-resource-ledger.json'); agenda=load(G/'advisor-meeting-agenda-20260906.json')
cards={};card_paths=[]
for p in sorted((G/'advisor-decision-cards').glob('*.json')):
 d=load(p); cards[d['paper_id']]=d; card_paths.append(p)
review_paths=[G/f'stanford-{pid.lower()}-review.json' for pid in ORDER]
sources=[G/'advisor-paper-pack-manifest.json',G/'advisor-reality-support.json',G/'advisor-resource-ledger.json',G/'advisor-meeting-agenda-20260906.json',*card_paths,*review_paths,G/'stanford-g2-mcta-review.json']
hash_,rows=canonical_hash(sources)
manifest_by={x['paper_id']:x for x in manifest['papers']}
papers=[]
for pid in ORDER:
 c=cards[pid]; rr=resources['papers'][pid]; r=load(G/f'stanford-{pid.lower()}-review.json'); m=manifest_by[pid]
 papers.append({
  'paper_id':pid,'title':m['title'],'paper_status':m['paper_status'],'pdf_sha256':m['pdf_sha256'],'route':c['route'],
  'best_case':c['best_case'],'story':c['story'],'premise':c['premise'],'risk':c['risk'],'strongest_simplification':c['strongest_simplification'],
  'evidence_state':c['evidence_state'],'next_closure':c['next_closure'],'cost_class':c['cost_class'],'cost_to_next_decision':c['cost_to_next_decision'],
  'dependencies':c['dependencies'],'default_action':c['default_action'],'override_trigger':c['override_trigger'],'cross_paper_leverage':c['cross_paper_leverage'],'advisor_question':c['advisor_question'],
  'reality_support':reality['papers'][pid],'resource_plan':rr,
  'stanford':{'status':r.get('status'),'numerical_score':r.get('numerical_score'),'textual_signal':r.get('textual_signal'),'reviewed_pdf_sha256':r.get('pdf_sha256'),'exact_current_pdf':r.get('pdf_sha256')==m['pdf_sha256'],'advisor_digest':r.get('advisor_digest')},
  'science_delta':m['delta']})
out={
 'schema_version':'1.0','review_scope':'advisor-meeting decision sufficiency only; no scientific authority','decision_surface_hash':hash_,
 'paper_count':9,'route_summary':{route:sum(cards[x]['route']==route for x in ORDER) for route in ['FREEZE_SUBMIT','EXECUTE_FROZEN','QUALIFY_FIRST','FORMALIZE_FIRST']},
 'papers':papers,'claim_ownership_map':agenda['claim_ownership_map'],'shared_risks':agenda['shared_risks'],'shared_risk_reopen_rules':agenda['shared_risk_reopen_rules'],
 'meeting_outputs':agenda['meeting_outputs'],'do_not_spend_advisor_time_on':agenda['do_not_spend_advisor_time_on'],'schedule':agenda['schedule'],
 'source_hashes':rows,'authority':{'scientific':False,'experiment':False,'submission':False,'advisor_meeting_projection_only':True}}
path=G/'advisor-final-sufficiency-review-packet-20260906.json';path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'output':str(path.relative_to(ROOT)),'decision_surface_hash':hash_,'papers':9,'source_count':len(rows)},ensure_ascii=False,indent=2))
