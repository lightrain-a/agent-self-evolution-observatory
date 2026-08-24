#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=Path('/data/wyt/agent-self-evolution-observatory/paper-acceptance/source-native-replay/D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK')
SETS={
'historical_benign':DATA/'20260824-extension-benign-generic-deepseek',
'eia_clean':DATA/'20260824-extension-eia-future-nonceiling',
'eia_repeat':DATA/'20260824-extension-eia-future-nonceiling/repeat-robustness-r1',
'bls_cpi':DATA/'20260824-extension-bls-cpi-crossdomain',
'bls_repeat':DATA/'20260824-extension-bls-cpi-crossdomain/repeat-robustness-r1',
'multiturn':DATA/'20260824-extension-multiturn-tool-vs-context',
'eia_planning_repeat':DATA/'20260824-extension-multiturn-base-repeat-r1',
'bls_planning':DATA/'20260824-extension-bls-cpi-planning-base',
'bls_planning_repeat':DATA/'20260824-extension-bls-cpi-planning-base-repeat-r1',
'fed_fomc':DATA/'20260824-extension-fed-fomc-planning-prospective',
'fed_planning':DATA/'20260824-extension-fed-fomc-planning-prospective/planning-base',
'multiturn_protocol_smoke':DATA/'20260824-extension-multiturn-protocol-smoke/v2',
}
def sha(p:Path):return hashlib.sha256(p.read_bytes()).hexdigest()
def record(root:Path):
 files=[]
 for p in sorted(root.rglob('*')):
  if not p.is_file():continue
  if p.name=='.env' or 'token' in p.name.lower():raise RuntimeError(f'forbidden file:{p}')
  files.append({'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':sha(p)})
 return {'root':str(root),'files':files,'file_count':len(files),'raw_json_count':sum('/raw/' in '/'+x['path'] or x['path'].startswith('raw/') for x in files),'csv_count':sum(x['path'].endswith('.csv') for x in files),'checkpoint_count':sum(x['path'].endswith('checkpoint.json') for x in files)}
def main():
 payload={'schema_version':'1.0','paper_id':'D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK','artifact_type':'extension-evidence-content-addressed-manifest','sets':{k:record(v) for k,v in SETS.items()},'adjudication_sha256':sha(ROOT/'generated/temporal-skill-extension-adjudication-20260824.json'),'endpoint_summary_sha256':sha(ROOT/'generated/temporal-skill-extension-endpoint-summary-20260824.csv'),'provider_route':'Ark Plan /api/plan/v3','required_resolved_model':'deepseek-v4-pro-260425','private_credentials_included':False,'scientific_authority':False,'submission_authority':False}
 out=ROOT/'generated/temporal-skill-extension-evidence-manifest-20260824.json';out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'sets':len(payload['sets']),'files':sum(x['file_count'] for x in payload['sets'].values()),'raw':sum(x['raw_json_count'] for x in payload['sets'].values()),'csv':sum(x['csv_count'] for x in payload['sets'].values()),'checkpoint':sum(x['checkpoint_count'] for x in payload['sets'].values()),'sha256':sha(out)},indent=2))
if __name__=='__main__':main()
