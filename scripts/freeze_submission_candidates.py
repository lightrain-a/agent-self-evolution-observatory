from __future__ import annotations
import argparse, json, shutil, sys
from pathlib import Path
PROJECT_ROOT=Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:sys.path.insert(0,str(PROJECT_ROOT))
from research_pipeline.paper_anonymity_audit import validate_anonymity_audit_receipt
from research_pipeline.paper_portfolio_audit import build as build_audit
from research_pipeline.presubmission_freeze import ROOT, artifact, build_freeze, digest, publish_freeze, validate_freeze

POLICY=PROJECT_ROOT/'generated'/'venue-policy-iclr2027-current.json'
PROFILES={
 'AGENT-SAFETY-R9':[
  ('paper_pdf','submission-packages/agent-safety-r9-paper-prep-v2-20260822/agent-safety-r9-iclr2027.pdf'),
  ('submission_bundle','submission-packages/agent-safety-r9-paper-prep-v3-anonymized-20260823.zip'),
 ],
 'D2-PAPER-FAILURE-MEMORY-PROVENANCE':[
  ('paper_pdf','submission-packages/d2-failure-memory-provenance-submission-ready-20260822-0281fc40/main.pdf'),
  ('source_zip','submission-packages/d2-failure-memory-provenance-submission-ready-20260822-0281fc40/source.zip'),
  ('supplement_zip','submission-packages/d2-failure-memory-provenance-submission-ready-20260822-0281fc40/supplement.zip'),
  ('package_manifest','submission-packages/d2-failure-memory-provenance-submission-ready-20260822-0281fc40/package-manifest.json'),
 ],
 'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE':[
  ('paper_pdf','submission-packages/d2-proxy-reward-memory-variance-anonymized-20260823/main.pdf'),
  ('source_zip','submission-packages/d2-proxy-reward-memory-variance-anonymized-20260823/source.zip'),
  ('supplement_zip','submission-packages/d2-proxy-reward-memory-variance-anonymized-20260823/supplement.zip'),
  ('package_manifest','submission-packages/d2-proxy-reward-memory-variance-anonymized-20260823/package-manifest.json'),
 ],
 'STRI-ICLR2027':[
  ('paper_pdf','submission-packages/STRI-ICLR2027-20260816.pdf'),
  ('source_zip','submission-packages/STRI-ICLR2027-20260816-source.zip'),
  ('supplement_zip','submission-packages/STRI-ICLR2027-20260816-supplement.zip'),
 ],
}

def latest_preparation(ledger):
 for e in reversed(ledger.get('events') or []):
  if isinstance(e,dict) and e.get('event_type')=='paper-preparation' and isinstance(e.get('receipt'),dict):return e['receipt']
 return {}

def deep_anonymity_binding(pid):
 ledger=json.loads((ROOT/'paper-acceptance'/f'{pid}.json').read_text());prep=latest_preparation(ledger);packet_sha=str(prep.get('packet_sha256') or '')
 if not packet_sha:raise RuntimeError(f'{pid} latest preparation receipt lacks packet SHA')
 candidates=sorted((ROOT/'paper-acceptance-artifacts'/pid).glob('paper-preparation-packet-anonymity-v1-*.json'))
 for path in candidates:
  packet=json.loads(path.read_text())
  if digest(packet)!=packet_sha:continue
  sub=((packet.get('gates') or {}).get('submission-package') or {});audit=sub.get('double_blind_audit_receipt') or {}
  if str(sub.get('anonymity_audit_version') or '')!='1.0' or not validate_anonymity_audit_receipt(audit) or audit.get('pass') is not True:raise RuntimeError(f'{pid} current preparation packet lacks valid PASS deep-anonymity audit')
  if str(sub.get('anonymity_audit_sha256') or '')!=str(audit.get('anonymity_audit_sha256') or ''):raise RuntimeError(f'{pid} anonymity audit SHA binding mismatch')
  return audit
 raise RuntimeError(f'{pid} current preparation packet has no matching deep-anonymity packet artifact')

def verify_freeze_artifacts_are_anonymity_audited(pid,arts,audit):
 covered={(str(x.get('filename') or ''),str(x.get('sha256') or '')) for x in audit.get('artifact_manifest') or [] if isinstance(x,dict)}
 missing=[a['label'] for a in arts if (Path(str(a.get('path') or '')).name,str(a.get('sha256') or '')) not in covered]
 if missing:raise RuntimeError(f'{pid} freeze artifacts not covered by current deep-anonymity audit: {missing}')

def run(root:Path,policy_path:Path,validate_only:bool=False):
 global ROOT
 ROOT=Path(root).resolve();policy_path=Path(policy_path).resolve();policy=json.loads(policy_path.read_text());fd=ROOT/'paper-submission-freezes';results=[]
 if not validate_only:
  fd.mkdir(parents=True,exist_ok=True);shutil.copy2(policy_path,fd/'venue-policy-iclr2027-20260822.json')
 audit=build_audit(ROOT);by={p['paper_id']:p for p in audit['papers']}
 for pid,p in by.items():
  if not p['submission_freeze_eligible']:
   results.append({'paper_id':pid,'status':'SKIPPED_NOT_ELIGIBLE','paper_preparation_status':p['paper_preparation_status'],'blocker_groups':p['blocker_groups']});continue
  if pid not in PROFILES:raise RuntimeError(f'eligible paper lacks freeze profile: {pid}')
  anon=deep_anonymity_binding(pid);arts=[artifact(label,ROOT/rel) for label,rel in PROFILES[pid]];verify_freeze_artifacts_are_anonymity_audited(pid,arts,anon);receipt=build_freeze(pid,arts,policy,ROOT)
  if validate_only:
   results.append({'paper_id':pid,'status':'PASS_VALIDATE_ONLY','freeze_sha256':receipt['freeze_sha256'],'deep_anonymity_audit_sha256':anon['anonymity_audit_sha256'],'deep_anonymity_warning_count':int(anon.get('warning_count') or 0),'ledger_validation_errors':[]});continue
  row=publish_freeze(receipt,ROOT);errors=validate_freeze(row);results.append({'paper_id':pid,'status':receipt['status'],'freeze_sha256':receipt['freeze_sha256'],'events':len(row['events']),'deep_anonymity_audit_sha256':anon['anonymity_audit_sha256'],'deep_anonymity_warning_count':int(anon.get('warning_count') or 0),'ledger_validation_errors':errors})
 index={'schema_version':'1.0','mode':'VALIDATE_ONLY' if validate_only else 'PUBLISH','venue_policy_snapshot_sha256':policy['snapshot_sha256'],'results':results,'authority':{'scientific':False,'experiment':False,'gpu':False,'submission':False}}
 if not validate_only:(fd/'current-freeze-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')
 return index

def main():
 parser=argparse.ArgumentParser(description='Freeze current submission-ready paper artifacts only after the latest Paper Preparation packet binds a PASS deep-anonymity audit covering every artifact SHA.')
 parser.add_argument('--root',type=Path,default=ROOT);parser.add_argument('--venue-policy',type=Path,default=POLICY);parser.add_argument('--validate-only',action='store_true');args=parser.parse_args();print(json.dumps(run(args.root,args.venue_policy,args.validate_only),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
