from __future__ import annotations
import json, shutil
from pathlib import Path
from research_pipeline.paper_portfolio_audit import build as build_audit
from research_pipeline.presubmission_freeze import ROOT, artifact, build_freeze, publish_freeze, validate_freeze

POLICY=Path('generated/venue-policy-iclr2027-current.json')
PROFILES={
 'AGENT-SAFETY-R9':[
  ('paper_pdf','submission-packages/agent-safety-r9-paper-prep-v2-20260822/agent-safety-r9-iclr2027.pdf'),
  ('submission_bundle','submission-packages/agent-safety-r9-paper-prep-v2-20260822.zip'),
 ],
 'D2-PAPER-FAILURE-MEMORY-PROVENANCE':[
  ('paper_pdf','submission-packages/d2-failure-memory-provenance-submission-ready-20260822-0281fc40/main.pdf'),
  ('source_zip','submission-packages/d2-failure-memory-provenance-submission-ready-20260822-0281fc40/source.zip'),
  ('supplement_zip','submission-packages/d2-failure-memory-provenance-submission-ready-20260822-0281fc40/supplement.zip'),
  ('package_manifest','submission-packages/d2-failure-memory-provenance-submission-ready-20260822-0281fc40/package-manifest.json'),
 ],
 'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE':[
  ('paper_pdf','submission-packages/d2-proxy-reward-memory-variance-submission-freeze-20260822/main.pdf'),
  ('source_zip','submission-packages/d2-proxy-reward-memory-variance-submission-freeze-20260822/source.zip'),
  ('supplement_zip','submission-packages/d2-proxy-reward-memory-variance-submission-freeze-20260822/supplement.zip'),
  ('package_manifest','submission-packages/d2-proxy-reward-memory-variance-submission-freeze-20260822/package-manifest.json'),
 ],
 'STRI-ICLR2027':[
  ('paper_pdf','submission-packages/STRI-ICLR2027-20260816.pdf'),
  ('source_zip','submission-packages/STRI-ICLR2027-20260816-source.zip'),
  ('supplement_zip','submission-packages/STRI-ICLR2027-20260816-supplement.zip'),
 ],
}

def main():
 policy=json.loads(POLICY.read_text());fd=ROOT/'paper-submission-freezes';fd.mkdir(parents=True,exist_ok=True);shutil.copy2(POLICY,fd/'venue-policy-iclr2027-20260822.json')
 audit=build_audit(ROOT);by={p['paper_id']:p for p in audit['papers']};results=[]
 for pid,p in by.items():
  if not p['submission_freeze_eligible']:
   results.append({'paper_id':pid,'status':'SKIPPED_NOT_ELIGIBLE','paper_preparation_status':p['paper_preparation_status'],'blocker_groups':p['blocker_groups']});continue
  if pid not in PROFILES:raise RuntimeError(f'eligible paper lacks freeze profile: {pid}')
  arts=[artifact(label,ROOT/rel) for label,rel in PROFILES[pid]];receipt=build_freeze(pid,arts,policy,ROOT);row=publish_freeze(receipt,ROOT);errors=validate_freeze(row)
  results.append({'paper_id':pid,'status':receipt['status'],'freeze_sha256':receipt['freeze_sha256'],'events':len(row['events']),'ledger_validation_errors':errors})
 index={'schema_version':'1.0','venue_policy_snapshot_sha256':policy['snapshot_sha256'],'results':results,'authority':{'scientific':False,'experiment':False,'gpu':False,'submission':False}}
 (fd/'current-freeze-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n');print(json.dumps(index,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
