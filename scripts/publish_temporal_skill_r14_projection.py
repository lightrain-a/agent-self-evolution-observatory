#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, shutil, sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from research_pipeline.research_item_state import build_paper_registry
from research_pipeline.paper_acceptance_ledger import build_paper_ledger_index
PID="D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK"; TITLE="Do Temporal Skills Really Repair Agents? An Intervention Audit of Repair and Attribution"
PDF="0fef51f15bb188fc669411be8d6dedaeae7d83389cec3f5d917f9a120fe2906e"; SRC="809fd3a52b5263bc8944b361ebc5bafcc2da7d615fec2b4a900a39127f485c0f"; SUP="0cd9aee6f5a23bc0d5818bb42300c437a8c12df822d03230510e6073af127b0d"
GEN=ROOT/'generated'; DL=ROOT/'downloads'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_pair(name,var,payload):
 (GEN/f'{name}.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (GEN/f'{name}.js').write_text(f'window.{var} = '+json.dumps(payload,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
def registry_summary(rows,old):
 s=dict(old); s['papers']=len(rows); s['submission_ready']=sum(r.get('submission_ready') is True for r in rows); s['gate_clean_submission_ready']=sum(r.get('gate_clean_submission_ready') is True for r in rows); s['paper_preparation_failed']=sum((r.get('latest_paper_preparation') or {}).get('required_gates',0)>0 and (r.get('latest_paper_preparation') or {}).get('pass') is not True for r in rows); s['immediate_submission_holds']=sum(r.get('immediate_submission_hold') is True for r in rows); s['internal_action_required']=sum((r.get('primary_next_action') or {}).get('action_class')!='NO_INTERNAL_ACTION' for r in rows); s['no_internal_action']=len(rows)-s['internal_action_required']; s['by_internal_action']=dict(sorted(Counter((r.get('primary_next_action') or {}).get('action_class') or 'UNKNOWN' for r in rows).items())); s['scientific_holds']=sum(str(r.get('scientific_status'))!='READY' for r in rows); s['by_stage']=dict(sorted(Counter(r.get('paper_stage') or r.get('current_state') or 'UNKNOWN' for r in rows).items())); return s
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--data-root',type=Path,default=Path('/data/wyt/agent-self-evolution-observatory')); a=ap.parse_args()
 srcs=[(DL/'E2-Temporal-Skill-r14-20260824.pdf',DL/'E2-Temporal-Skill.pdf',PDF),(DL/'E2-Temporal-Skill-r14-20260824.pdf',DL/f'{PID}.pdf',PDF),(DL/'E2-Temporal-Skill-r14-20260824-source.zip',DL/f'{PID}-source.zip',SRC),(DL/'E2-Temporal-Skill-r14-20260824-supplement.zip',DL/f'{PID}-supplement.zip',SUP)]
 for s,d,h in srcs:
  if sha(s)!=h: raise RuntimeError(f'revision artifact mismatch {s}')
  shutil.copyfile(s,d)
  if sha(d)!=h: raise RuntimeError(f'stable alias mismatch {d}')
 live=build_paper_ledger_index(a.data_root); pub=next(r for r in live['entries'] if r['paper_id']==PID)
 if pub['title']!=TITLE or (pub.get('source_native_evidence') or {}).get('runtime_valid_rows')!=2056: raise RuntimeError('live E2 projection not R14')
 candidate_full=build_paper_registry(); candidate=next(r for r in candidate_full['papers'] if r['paper_id']==PID)
 old=json.loads((GEN/'paper-registry.json').read_text()); rows=list(old['papers']); rows=[candidate if r.get('paper_id')==PID else r for r in rows]
 if sum(r.get('paper_id')==PID for r in rows)!=1: raise RuntimeError('paper registry E2 cardinality error')
 old['papers']=rows; old['generated_at']=candidate_full.get('generated_at') or datetime.now(timezone.utc).isoformat(timespec='seconds'); old['source_revision']=candidate_full.get('source_revision') or old.get('source_revision'); old['summary']=registry_summary(rows,old.get('summary') or {})
 write_pair('paper-registry','PAPER_REGISTRY',old)
 state=json.loads((GEN/'research-system-state.json').read_text()); pa=state.get('paper_acceptance') or {}; idx=pa.get('ledger_index') or {}; entries=list(idx.get('entries') or []); entries=[pub if r.get('paper_id')==PID else r for r in entries]
 if sum(r.get('paper_id')==PID for r in entries)!=1: raise RuntimeError('research-system ledger E2 cardinality error')
 idx['entries']=entries; pa['ledger_index']=idx; state['paper_acceptance']=pa
 (GEN/'research-system-state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); (GEN/'research-system-state.js').write_text('window.RESEARCH_SYSTEM_STATE = '+json.dumps(state,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
 out={'schema_version':'1.0','status':'E2_R14_SELECTIVE_PROJECTION_PUBLISHED','paper_id':PID,'title':TITLE,'runtime_valid_rows':2056,'stable_hashes':{'pdf':sha(DL/'E2-Temporal-Skill.pdf'),'source_zip':sha(DL/f'{PID}-source.zip'),'supplement_zip':sha(DL/f'{PID}-supplement.zip')},'other_paper_rows_preserved':True,'scientific_authority':False,'submission_authority':False}
 out['receipt_sha256']=hashlib.sha256(json.dumps(out,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest(); (GEN/'temporal-skill-r14-publication-projection-20260824.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n'); print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
