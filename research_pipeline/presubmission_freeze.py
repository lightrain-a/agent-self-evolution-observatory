from __future__ import annotations
import fcntl, hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence
from .paper_acceptance_ledger import validate_paper_ledger
from .paper_preparation_protocol import validate_paper_preparation_receipt

ROOT=Path('/data/wyt/agent-self-evolution-observatory')
EXCLUDE_SUFFIXES={'.aux','.bbl','.blg','.log','.out','.fls','.fdb_latexmk'}

def now()->str:return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def digest(v:Any)->str:return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def fsha(p:Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def latest(row:Mapping[str,Any],kind:str)->dict[str,Any]:
 for e in reversed(row.get('events') or []):
  if isinstance(e,dict) and e.get('event_type')==kind:return e
 return {}
def artifact(label:str,path:Path,tree:bool=False)->dict[str,Any]:
 path=path.resolve()
 if not path.exists():raise FileNotFoundError(path)
 if not tree:
  if not path.is_file():raise TypeError(path)
  return {'label':label,'kind':'file','path':str(path),'sha256':fsha(path),'bytes':path.stat().st_size}
 entries=[]
 for p in sorted(x for x in path.rglob('*') if x.is_file() and x.suffix not in EXCLUDE_SUFFIXES):
  entries.append({'path':str(p.relative_to(path)),'sha256':fsha(p),'bytes':p.stat().st_size})
 if not entries:raise RuntimeError(f'empty source tree: {path}')
 return {'label':label,'kind':'tree','path':str(path),'files':len(entries),'bytes':sum(x['bytes'] for x in entries),'sha256':digest(entries),'entries':entries}
def validate_freeze(row:Mapping[str,Any])->list[str]:
 errors=[]
 if (row.get('authority') or {})!={'scientific':False,'experiment':False,'gpu':False,'submission':False}:errors.append('freeze-ledger-authority-leak')
 for e in row.get('events') or []:
  if not isinstance(e,dict):errors.append('freeze-event-not-object');continue
  if any(e.get(k) is True for k in ('scientific_authority','experiment_authority','gpu_authority','submission_authority')):errors.append('freeze-event-authority-leak')
  if e.get('event_type')=='pre-submission-freeze':
   r=e.get('receipt') or {};identity={k:r.get(k) for k in ('paper_id','contract_sha256','paper_preparation_receipt_sha256','venue_policy_snapshot_sha256','frozen_artifacts','status','human_signoff_status')}
   if r.get('freeze_sha256')!=digest(identity):errors.append('invalid-freeze-receipt-hash')
 return list(dict.fromkeys(errors))
def build_freeze(paper_id:str,artifacts:Sequence[dict[str,Any]],venue_policy:Mapping[str,Any],root:Path=ROOT)->dict[str,Any]:
 lp=root/'paper-acceptance'/f'{paper_id}.json';row=json.loads(lp.read_text());contract_sha=str(row.get('contract_sha256') or '')
 if digest(row.get('contract') or {})!=contract_sha:raise RuntimeError('paper-contract-integrity-failed')
 le=validate_paper_ledger(row)
 if le:raise RuntimeError(f'paper-ledger-replay-failed:{le}')
 if row.get('current_state')!='SUBMISSION_READY':raise RuntimeError('paper-not-submission-ready')
 pe=latest(row,'paper-preparation');prep=pe.get('receipt') if isinstance(pe.get('receipt'),dict) else {}
 if not prep or not validate_paper_preparation_receipt(prep) or prep.get('pass') is not True:raise RuntimeError('paper-preparation-not-pass')
 venue_sha=str(venue_policy.get('snapshot_sha256') or '')
 check=dict(venue_policy);check.pop('snapshot_sha256',None)
 if not venue_sha or digest(check)!=venue_sha:raise RuntimeError('venue-policy-snapshot-integrity-failed')
 identity={'paper_id':paper_id,'contract_sha256':contract_sha,'paper_preparation_receipt_sha256':prep['receipt_sha256'],'venue_policy_snapshot_sha256':venue_sha,'frozen_artifacts':list(artifacts),'status':'MACHINE_FROZEN_HUMAN_SIGNOFF_PENDING','human_signoff_status':'PENDING_HUMAN'}
 return {**identity,'freeze_sha256':digest(identity),'frozen_at':now(),'human_checklist':['confirm complete author list and OpenReview profiles','confirm author quota and reciprocal-reviewing obligations','confirm dual-submission compliance','acknowledge ICLR Code of Ethics','review and approve mandatory AI-use disclosure','verify final PDF/source/supplement hashes immediately before upload'],'external_human_submission_authority_required':True,'scientific_authority':False,'experiment_authority':False,'gpu_authority':False,'submission_authority':False}
def publish_freeze(receipt:Mapping[str,Any],root:Path=ROOT)->dict[str,Any]:
 d=root/'paper-submission-freezes';d.mkdir(parents=True,exist_ok=True);pid=str(receipt['paper_id']);path=d/f'{pid}.json';lock=d/f'.{pid}.lock'
 with lock.open('a+') as h:
  fcntl.flock(h.fileno(),fcntl.LOCK_EX);row=json.loads(path.read_text()) if path.exists() else {'schema_version':'1.0','paper_id':pid,'events':[],'authority':{'scientific':False,'experiment':False,'gpu':False,'submission':False}}
  prior=latest(row,'pre-submission-freeze')
  if (prior.get('receipt') or {}).get('freeze_sha256')==receipt.get('freeze_sha256'):return row
  e={'event_type':'pre-submission-freeze','receipt':dict(receipt),'recorded_at':now(),'scientific_authority':False,'experiment_authority':False,'gpu_authority':False,'submission_authority':False};e['event_id']=digest([pid,len(row['events']),e])[:24];row['events'].append(e);row['updated_at']=e['recorded_at']
  errors=validate_freeze(row)
  if errors:raise RuntimeError(errors)
  q=path.with_suffix('.json.tmp');q.write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n');os.replace(q,path);return row
