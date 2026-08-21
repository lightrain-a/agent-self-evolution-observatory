from __future__ import annotations
import argparse, hashlib, json, os, re, subprocess, sys
from pathlib import Path
from statistics import mean
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from research_pipeline.ark_provider import ArkResponsesClient,ArkSettings,ArkResponseStateError
from research_pipeline.config import load_env_file
from research_pipeline.paper_acceptance import MockReviewMode,ObjectionEvidenceState,PaperContract,PaperState,ReviewerObjection,ScientificPaperStatus,StoryCandidate,paper_contract_payload
from research_pipeline.paper_acceptance_ledger import advance_paper_ledger,build_paper_ledger_index,initialize_paper_ledger,load_paper_ledger,record_mock_review,record_story_search,validate_paper_ledger
CANON_ENV=Path('/home/wyt/code/agent-self-evolution-observatory/.env')
PAPERSTATE=ROOT/'generated/d2-active-paperstates-20260821.json'
SOURCE_SCAN=ROOT/'generated/d2-active-paper-current-source-scan-20260821.json'
OUTDIR=ROOT/'generated/d2-active-paper-mock-pc-20260821'
MODELS={MockReviewMode.BLIND_MANUSCRIPT:'deepseek-v4-pro',MockReviewMode.ARTIFACT_AWARE:'kimi-k3'}
QUESTIONS={
'D2-PAPER-FAILURE-MEMORY-PROVENANCE':'Does failure-derived trajectory provenance causally sustain future error when future task difficulty and actionable memory guidance are matched?',
'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE':'Can an erroneous reward label become persistent agent state by changing the memory written from an otherwise identical trajectory, and does that perturbation reach later behavior?',
'D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK':'Are recurring temporal-validity and exogenous-context failures caused by missing reusable procedures that targeted skills can repair beyond generic skill assistance?'}
UNSUPPORTED={
'D2-PAPER-FAILURE-MEMORY-PROVENANCE':{'U1':'Failure-derived provenance universally causes future error across agents and domains.','U2':'Provenance-aware governance has already been shown to improve downstream performance.'},
'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE':{'U1':'The four-pair F0 alone proves downstream run-level variance amplification.','U2':'The write-channel effect size is universal across writers, tasks, and agents.'},
'D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK':{'U1':'All recurring TimeSage-EV failures are caused by missing reusable skills.','U2':'Targeted skills have already beaten matched generic-skill and no-skill controls.'}}
CLAIM_PATHS={
'D2-PAPER-FAILURE-MEMORY-PROVENANCE':'generated/d2-failure-memory-provenance-claim-ledger.json',
'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE':'generated/d2-proxy-reward-memory-variance-claim-ledger.json',
'D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK':'generated/d2-temporal-skill-bottleneck-claim-ledger.json'}
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def aref(p:Path)->str:return 'artifact:sha256:'+sha(p)
def states()->dict[str,dict[str,Any]]:
 p=json.loads(PAPERSTATE.read_text());return {r['paper_id']:r for r in p['papers']}
def claim_path(pid:str)->Path:return ROOT/CLAIM_PATHS[pid]
def qa_path(s:dict)->Path:return ROOT/s['paper_qa_artifact']
def manuscript_text(s:dict)->str:
 p=ROOT/s['manuscript_dir']/ 'main.pdf';return subprocess.run(['pdftotext',str(p),'-'],check=True,text=True,capture_output=True).stdout
def limitations(s:dict)->tuple[str,...]:
 p=ROOT/s['manuscript_dir']/'sections/06_limitations_conclusion.tex';raw=p.read_text().split('\\section{Conclusion}',1)[0];raw=re.sub(r'^\\section\{Limitations\}\s*','',raw.strip());return tuple(re.sub(r'\s+',' ',x).strip() for x in re.split(r'\n\s*\n',raw) if x.strip())
def contract(s:dict)->PaperContract:
 pid=s['paper_id'];cl=json.loads(claim_path(pid).read_text())['claims'];sup={};act={};debt={}
 for r in cl:
  cid=str(r.get('claim_id') or '');v=str(r.get('verdict') or '');text=str(r.get('claim') or '')
  if v in {'SUPPORTED','SUPPORTED_ACTIVE','PASS'}:sup[cid]=text
  elif v=='ACTIVE_UNREFUTED_HYPOTHESIS':act[cid]=text;debt[cid]=tuple(r.get('experiment_debt') or s.get('experiment_debt') or [])
 pdir=ROOT/s['manuscript_dir'];refs=[aref(claim_path(pid)),aref(qa_path(s)),aref(pdir/'main.pdf')]
 if pid=='D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE':refs.append(aref(ROOT/'generated/d2-proxy-reward-memory-f0.json'))
 lim=list(limitations(s))+['Support debt: '+x for x in s.get('support_debt') or []]
 return PaperContract(paper_id=pid,title=s['title'],central_question=QUESTIONS[pid],supported_claims=sup,active_unrefuted_claims=act,active_claim_experiment_debt=debt,unsupported_claims=UNSUPPORTED[pid],limitations=tuple(lim),evidence_refs=tuple(refs),scientific_status=ScientificPaperStatus.READY)
def stories(c:PaperContract)->list[StoryCandidate]:
 sup=tuple(c.supported_claims);act=tuple(c.active_unrefuted_claims);allc=sup+act
 out=[StoryCandidate('S1-CURRENT-CHAIN','Current mechanism chain','Observed phenomenon and mechanism first; downstream active hypothesis follows with explicit debt.',allc,allc),StoryCandidate('S2-EVIDENCE-FIRST','Evidence-first ordering','Direct evidence first; active hypothesis follows as the next causal link.',allc,sup),StoryCandidate('S3-HYPOTHESIS-FIRST','Problem-first ordering','Scientific question first, then immediately anchor it with observed mechanism and frozen boundary.',act+sup,allc)]
 uid=next(iter(c.unsupported_claims));out.append(StoryCandidate('S9-OVERCLAIM-CONTROL','Overclaim control','Invalid control that must be rejected by Story Search.',allc+(uid,),(uid,)));return out
def schema()->list[dict[str,Any]]:
 es=[x.value for x in ObjectionEvidenceState];obj={'type':'object','properties':{'objection_id':{'type':'string'},'category':{'type':'string'},'text':{'type':'string'},'decision_critical':{'type':'boolean'},'evidence_state':{'type':'string','enum':es},'claim_ids':{'type':'array','items':{'type':'string'}}},'required':['objection_id','category','text','decision_critical','evidence_state','claim_ids'],'additionalProperties':False}
 props={'recommendation':{'type':'string','enum':['strong_reject','reject','weak_reject','borderline','weak_accept','accept','strong_accept']},'score_1_to_10':{'type':'integer','minimum':1,'maximum':10},'confidence_1_to_5':{'type':'integer','minimum':1,'maximum':5},'novelty_1_to_5':{'type':'integer','minimum':1,'maximum':5},'significance_1_to_5':{'type':'integer','minimum':1,'maximum':5},'technical_quality_1_to_5':{'type':'integer','minimum':1,'maximum':5},'empirical_sufficiency_1_to_5':{'type':'integer','minimum':1,'maximum':5},'clarity_1_to_5':{'type':'integer','minimum':1,'maximum':5},'strengths':{'type':'array','items':{'type':'string'}},'weaknesses':{'type':'array','items':{'type':'string'}},'decision_critical_objections':{'type':'array','items':obj},'strongest_reject_reason':{'type':'string'},'highest_value_next_action':{'type':'string'},'extra_experiment_needed_before_submission':{'type':'boolean'},'submission_advice':{'type':'string','enum':['freeze','minor_revision','major_revision','new_experiment','hold_support']}}
 return [{'type':'function','name':'submit_mock_pc_review','description':'Return the structured Mock PC review.','parameters':{'type':'object','properties':{'review':{'type':'object','properties':props,'required':list(props),'additionalProperties':False}},'required':['review'],'additionalProperties':False}}]
def artifact_packet(s:dict,c:PaperContract)->dict[str,Any]:
 pid=s['paper_id'];p={'paper_contract':paper_contract_payload(c),'paper_state':s,'claim_ledger':json.loads(claim_path(pid).read_text()),'manuscript_qa':json.loads(qa_path(s).read_text()),'current_source_scan':json.loads(SOURCE_SCAN.read_text())['papers'][pid]}
 if pid=='D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE':
  p['f0']=json.loads((ROOT/'generated/d2-proxy-reward-memory-f0.json').read_text())
  p['prompt_control']=json.loads((ROOT/'generated/d2-proxy-reward-memory-f0c-prompt-control.json').read_text())
  p['f1_r1_support_state']=json.loads((ROOT/'generated/d2-proxy-reward-memory-f1.json').read_text())
  p['f1_r2']=json.loads((ROOT/'generated/d2-proxy-reward-memory-f1-r2.json').read_text())
  p['f1c_deterministic_audit']=json.loads((ROOT/'generated/d2-proxy-reward-memory-f1c-deterministic-audit.json').read_text())
  p['f1d_distributional_audit']=json.loads((ROOT/'generated/d2-proxy-reward-memory-f1d-distributional-audit.json').read_text())
 return p
def prompt(mode:MockReviewMode,text:str,s:dict,c:PaperContract)->str:
 base=f'''Act as a strict independent ICLR program-committee reviewer. Judge whether this manuscript is competitive today. Be skeptical and evidence-sensitive. Do not reward proposed experiments as completed evidence. Do not punish a registered active unrefuted hypothesis merely for being active; judge whether its missing evidence is decision-critical for acceptance. Support/provider failure has zero scientific authority and is never counterevidence. Frozen unsupported claims are out of scope. Return exactly one submit_mock_pc_review tool call.\n\nPAPER ID: {c.paper_id}\nTITLE: {c.title}\nCENTRAL QUESTION: {c.central_question}\n\nMANUSCRIPT:\n{text}\n'''
 if mode==MockReviewMode.BLIND_MANUSCRIPT:return base+'\nBLIND_MANUSCRIPT mode: use only the manuscript above. Do not assume hidden receipts or experiments.'
 return base+'\nARTIFACT_AWARE mode: audit against the frozen claim/evidence boundary and current-source novelty context. Distinguish scientific evidence debt, support debt, and narrative repair.\n\nARTIFACT PACKET:\n'+json.dumps(artifact_packet(s,c),ensure_ascii=False)
def client(model:str)->ArkResponsesClient:
 load_env_file(CANON_ENV);key=os.environ.get('ARK_API_KEY','').strip()
 if not key:raise RuntimeError('ARK_API_KEY missing')
 b=ArkSettings.from_env();return ArkResponsesClient(ArkSettings(api_key=key,base_url=b.base_url,default_model=model,timeout_seconds=300.0,max_retries=0))
def review_path(pid:str,mode:MockReviewMode)->Path:return OUTDIR/f'{pid}__{mode.value}.json'
def run_review(s:dict,c:PaperContract,mode:MockReviewMode)->dict[str,Any]:
 OUTDIR.mkdir(parents=True,exist_ok=True);target=review_path(c.paper_id,mode)
 if target.exists():return json.loads(target.read_text())
 text=manuscript_text(s);pr=prompt(mode,text,s,c);ph=hashlib.sha256(pr.encode()).hexdigest();model=MODELS[mode]
 try:
  resp=client(model).respond(pr,model=model,max_output_tokens=7000,tools=schema(),thinking='disabled',store=True,allow_thinking_compatibility_fallback=True);calls=[x for x in resp.get('function_calls') or [] if x.get('name')=='submit_mock_pc_review']
  if len(calls)!=1:raise RuntimeError(f'expected one review call, got {len(calls)}')
  rv=json.loads(calls[0].get('arguments') or '{}').get('review') or {};rid=str(resp.get('response_id') or '');payload={'schema_version':'1.0','paper_id':c.paper_id,'mode':mode.value,'requested_model':model,'resolved_model':resp.get('resolved_model'),'provider_response_id_archived_privately':bool(rid),'provider_response_id_sha256':hashlib.sha256(rid.encode()).hexdigest() if rid else '','status':resp.get('status'),'usage':resp.get('usage') or {},'packet_sha256':ph,'review':rv,'scientific_authority':False,'experiment_authority':False}
 except ArkResponseStateError as e:payload={'schema_version':'1.0','paper_id':c.paper_id,'mode':mode.value,'requested_model':model,'status':'NONVOTING_PROVIDER_STATE_FAILURE','packet_sha256':ph,'provider_receipt':e.receipt(),'scientific_authority':False,'experiment_authority':False}
 target.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n');return payload
def objections(p:dict[str,Any],mode:MockReviewMode)->list[ReviewerObjection]:
 out=[];prefix='B' if mode==MockReviewMode.BLIND_MANUSCRIPT else 'A'
 for i,x in enumerate((p.get('review') or {}).get('decision_critical_objections') or [],1):
  try:es=ObjectionEvidenceState(str(x.get('evidence_state') or 'UNCERTAIN'))
  except ValueError:es=ObjectionEvidenceState.UNCERTAIN
  out.append(ReviewerObjection(f"{prefix}-{x.get('objection_id') or 'R'+str(i)}",str(x.get('category') or 'review'),str(x.get('text') or ''),bool(x.get('decision_critical')),es,tuple(str(z) for z in x.get('claim_ids') or [])))
 return out
def has_receipt(row:dict,event_type:str,mode:str='')->bool:
 for e in row.get('events') or []:
  if e.get('event_type')!=event_type:continue
  r=e.get('receipt') or {}
  if not mode or r.get('mode')==mode:return True
 return False
def advance_to_mock(root:Path,c:PaperContract)->dict:
 row=initialize_paper_ledger(root,c,actor='d2-paper-acceptance')
 if row.get('current_state')==PaperState.PAPER_EVIDENCE.value:
  z=advance_paper_ledger(root,c,PaperState.PAPER_DESIGN,actor='d2-paper-acceptance')
  if not z['receipt']['allowed']:raise RuntimeError(f"{c.paper_id} PAPER_DESIGN blocked: {z['receipt']['blockers']}")
  row=z['ledger']
 if row.get('current_state')==PaperState.PAPER_DESIGN.value and not has_receipt(row,'story-search'):row=record_story_search(root,c,stories(c),actor='d2-story-search')
 if row.get('current_state')==PaperState.PAPER_DESIGN.value:
  z=advance_paper_ledger(root,c,PaperState.MANUSCRIPT,actor='d2-paper-acceptance',artifact_refs=c.evidence_refs)
  if not z['receipt']['allowed']:raise RuntimeError(f"{c.paper_id} MANUSCRIPT blocked: {z['receipt']['blockers']}")
  row=z['ledger']
 if row.get('current_state')==PaperState.MANUSCRIPT.value:
  z=advance_paper_ledger(root,c,PaperState.MOCK_PC,actor='d2-paper-acceptance',artifact_refs=c.evidence_refs)
  if not z['receipt']['allowed']:raise RuntimeError(f"{c.paper_id} MOCK_PC blocked: {z['receipt']['blockers']}")
  row=z['ledger']
 return row
def run_paper(root:Path,s:dict)->dict[str,Any]:
 c=contract(s);row=advance_to_mock(root,c);reviews=[]
 for mode in (MockReviewMode.BLIND_MANUSCRIPT,MockReviewMode.ARTIFACT_AWARE):
  p=run_review(s,c,mode);reviews.append(p)
  if p.get('review') and not has_receipt(row,'mock-pc-review',mode.value):row=record_mock_review(root,c,mode,objections(p,mode),actor='d2-mock-pc-'+mode.value.lower())
 row=load_paper_ledger(root,c.paper_id)
 if row.get('current_state')==PaperState.MOCK_PC.value:row=advance_paper_ledger(root,c,PaperState.TARGETED_REPAIR,actor='d2-paper-acceptance')['ledger']
 err=validate_paper_ledger(row)
 if err:raise RuntimeError(c.paper_id+' invalid ledger: '+'; '.join(err))
 voting=[p for p in reviews if p.get('review')];scores=[int(p['review']['score_1_to_10']) for p in voting];emp=[int(p['review']['empirical_sufficiency_1_to_5']) for p in voting];missing=0
 for p in voting:
  for x in p['review'].get('decision_critical_objections') or []:
   if x.get('decision_critical') and x.get('evidence_state')==ObjectionEvidenceState.MISSING_DECISIVE_EVIDENCE.value:missing+=1
 return {'paper_id':c.paper_id,'title':c.title,'current_state':row.get('current_state'),'voting_reviews':len(voting),'mean_score_1_to_10':round(mean(scores),3) if scores else None,'mean_empirical_sufficiency_1_to_5':round(mean(emp),3) if emp else None,'recommendations':[p['review']['recommendation'] for p in voting],'submission_advice':[p['review']['submission_advice'] for p in voting],'decision_critical_missing_evidence':missing,'highest_value_next_actions':[p['review']['highest_value_next_action'] for p in voting],'extra_experiment_votes':sum(bool(p['review']['extra_experiment_needed_before_submission']) for p in voting),'review_artifacts':[str(review_path(c.paper_id,MockReviewMode(p['mode'])).relative_to(ROOT)) for p in voting],'scientific_authority':False,'experiment_authority':False}
def run(root:Path)->dict[str,Any]:
 ss=states();rows=[run_paper(root,ss[k]) for k in sorted(ss)];ranked=sorted(rows,key=lambda x:(-(x['mean_score_1_to_10'] or 0),x['decision_critical_missing_evidence'],-(x['mean_empirical_sufficiency_1_to_5'] or 0),x['paper_id']))
 for i,x in enumerate(ranked,1):x['mock_pc_rank']=i
 out={'schema_version':'1.0','status':'D2_ACTIVE_PAPERS_MOCK_PC_COMPLETE' if all(x['voting_reviews']==2 for x in rows) else 'D2_ACTIVE_PAPERS_MOCK_PC_SUPPORT_INCOMPLETE','ranking_rule':'Descending mean reviewer score; then fewer decision-critical missing-evidence objections; then higher empirical-sufficiency score.','papers':ranked,'ledger_index':build_paper_ledger_index(root),'scientific_authority':False,'experiment_authority':False,'gpu_authority':False,'submission_authority':False}
 (ROOT/'generated/d2-active-paper-mock-pc-ranking-20260821.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');return out
def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('--ledger-root',type=Path,default=Path('/data/wyt/agent-self-evolution-observatory'));a=ap.parse_args();r=run(a.ledger_root);print(json.dumps(r,ensure_ascii=False,indent=2));return 0 if r['status']=='D2_ACTIVE_PAPERS_MOCK_PC_COMPLETE' else 2
if __name__=='__main__':raise SystemExit(main())
