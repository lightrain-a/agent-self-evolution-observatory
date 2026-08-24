#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,shutil,sys
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from research_pipeline.research_item_state import build_paper_registry
from research_pipeline.paper_acceptance_ledger import build_paper_ledger_index
PID='D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK';TITLE='Do Temporal Skills Really Repair Agents? An Intervention Audit of Repair and Attribution'
PDF='e7bc48efde7914ee415936b101f980d7ca885f29288a532b068225b4cf14b0a9';SRC='510d93f3be4fc60c993b4fec3852b2012295ab2031cf70673b434a154aef6aa0';SUP='e2a19cbe6e9bb12fa1696ee5770f0ff33ed4835a25dfb8c26b8bbea54e1acb0a';GEN=ROOT/'generated';DL=ROOT/'downloads'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def write_pair(name,var,payload):
 (GEN/f'{name}.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(GEN/f'{name}.js').write_text(f'window.{var} = '+json.dumps(payload,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
def summary(rows,old):
 s=dict(old);s['papers']=len(rows);s['submission_ready']=sum(r.get('submission_ready') is True for r in rows);s['gate_clean_submission_ready']=sum(r.get('gate_clean_submission_ready') is True for r in rows);s['paper_preparation_failed']=sum((r.get('latest_paper_preparation') or {}).get('required_gates',0)>0 and (r.get('latest_paper_preparation') or {}).get('pass') is not True for r in rows);s['immediate_submission_holds']=sum(r.get('immediate_submission_hold') is True for r in rows);s['internal_action_required']=sum((r.get('primary_next_action') or {}).get('action_class')!='NO_INTERNAL_ACTION' for r in rows);s['no_internal_action']=len(rows)-s['internal_action_required'];s['by_internal_action']=dict(sorted(Counter((r.get('primary_next_action') or {}).get('action_class') or 'UNKNOWN' for r in rows).items()));s['scientific_holds']=sum(str(r.get('scientific_status'))!='READY' for r in rows);s['by_stage']=dict(sorted(Counter(r.get('paper_stage') or r.get('current_state') or 'UNKNOWN' for r in rows).items()));return s
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--data-root',type=Path,default=Path('/data/wyt/agent-self-evolution-observatory'));a=ap.parse_args()
 oldreg=json.loads((GEN/'paper-registry.json').read_text());old_other={r['paper_id']:r for r in oldreg['papers'] if r.get('paper_id')!=PID};oldstate=json.loads((GEN/'research-system-state.json').read_text());oldidx=((oldstate.get('paper_acceptance') or {}).get('ledger_index') or {}).get('entries') or [];old_state_other={r['paper_id']:r for r in oldidx if r.get('paper_id')!=PID}
 srcs=[(DL/'E2-Temporal-Skill-r16-20260824.pdf',DL/'E2-Temporal-Skill.pdf',PDF),(DL/'E2-Temporal-Skill-r16-20260824.pdf',DL/f'{PID}.pdf',PDF),(DL/'E2-Temporal-Skill-r16-20260824-source.zip',DL/f'{PID}-source.zip',SRC),(DL/'E2-Temporal-Skill-r16-20260824-supplement.zip',DL/f'{PID}-supplement.zip',SUP)]
 for s,d,h in srcs:
  if sha(s)!=h:raise RuntimeError(f'revision artifact mismatch {s}')
  shutil.copyfile(s,d)
  if sha(d)!=h:raise RuntimeError(f'stable alias mismatch {d}')
 live=build_paper_ledger_index(a.data_root);pub=next(r for r in live['entries'] if r['paper_id']==PID)
 if pub['title']!=TITLE or (pub.get('source_native_evidence') or {}).get('runtime_valid_rows')!=2056 or (pub.get('latest_claim_audit') or {}).get('checks')!=13 or (pub.get('latest_paper_preparation') or {}).get('protocol_version')!='1.0+r16-extension-appendix':raise RuntimeError('live E2 projection not R16')
 candidate_full=build_paper_registry();candidate=next(r for r in candidate_full['papers'] if r['paper_id']==PID);rows=[candidate if r.get('paper_id')==PID else r for r in oldreg['papers']]
 if sum(r.get('paper_id')==PID for r in rows)!=1:raise RuntimeError('paper registry E2 cardinality error')
 oldreg['papers']=rows;oldreg['generated_at']=candidate_full.get('generated_at') or datetime.now(timezone.utc).isoformat(timespec='seconds');oldreg['source_revision']=candidate_full.get('source_revision') or oldreg.get('source_revision');oldreg['summary']=summary(rows,oldreg.get('summary') or {});write_pair('paper-registry','PAPER_REGISTRY',oldreg)
 state=oldstate;pa=state.get('paper_acceptance') or {};idx=pa.get('ledger_index') or {};entries=[pub if r.get('paper_id')==PID else r for r in (idx.get('entries') or [])]
 if sum(r.get('paper_id')==PID for r in entries)!=1:raise RuntimeError('research-system ledger E2 cardinality error')
 idx['entries']=entries;pa['ledger_index']=idx;state['paper_acceptance']=pa;(GEN/'research-system-state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(GEN/'research-system-state.js').write_text('window.RESEARCH_SYSTEM_STATE = '+json.dumps(state,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
 new_other={r['paper_id']:r for r in oldreg['papers'] if r.get('paper_id')!=PID};new_state_other={r['paper_id']:r for r in entries if r.get('paper_id')!=PID}
 if old_other!=new_other or old_state_other!=new_state_other:raise RuntimeError('non-E2 paper projection changed')
 out={'schema_version':'1.0','status':'E2_R16_SELECTIVE_PROJECTION_PUBLISHED','paper_id':PID,'title':TITLE,'current_revision':'R16','runtime_valid_rows_core':2056,'extension_scientific_model_calls':114,'planning_spin_off':'STOP_PROSPECTIVE_FED_NO_EFFECT','external_review_textual_verdict_for_R14':'Accept','external_review_numeric_nonofficial_for_R14':6.0,'r16_externally_rescored':False,'stable_hashes':{'pdf':sha(DL/'E2-Temporal-Skill.pdf'),'source_zip':sha(DL/f'{PID}-source.zip'),'supplement_zip':sha(DL/f'{PID}-supplement.zip')},'other_paper_rows_preserved':True,'other_paper_registry_digest':digest(new_other),'other_research_system_paper_digest':digest(new_state_other),'scientific_authority':False,'submission_authority':False};out['receipt_sha256']=digest(out);(GEN/'temporal-skill-r16-publication-projection-20260824.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
