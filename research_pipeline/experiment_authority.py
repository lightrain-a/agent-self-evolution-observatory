from __future__ import annotations
import fcntl, hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

def _now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def _slug(s:str)->str: return ''.join(c if c.isalnum() or c in '-_.' else '-' for c in s)[:120]
def _paths(root:Path,idea_id:str):
 d=Path(root)/'experiment-authority'; d.mkdir(parents=True,exist_ok=True); stem=_slug(idea_id); return d/f'{stem}.json',d/f'.{stem}.lock'
def _read(path:Path)->dict[str,Any]:
 try: return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
 except (OSError,json.JSONDecodeError): return {}
def _atomic(path:Path,row:dict[str,Any]):
 tmp=path.with_suffix(path.suffix+'.tmp'); tmp.write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); os.replace(tmp,path)
def acquire_authority(root:Path,idea_id:str,plan_hash:str,actor:str,phase:str,run_id:str)->dict[str,Any]:
 path,lock=_paths(root,idea_id)
 with lock.open('a+') as fh:
  fcntl.flock(fh.fileno(),fcntl.LOCK_EX); old=_read(path)
  if old.get('status')=='active':
   if old.get('plan_hash')==plan_hash and old.get('run_id')==run_id: return old
   raise RuntimeError(f"experiment authority already active for {idea_id}: epoch={old.get('authority_epoch')} run={old.get('run_id')}")
  epoch=int(old.get('authority_epoch') or 0)+1
  aid=hashlib.sha256(f'{idea_id}|{plan_hash}|{run_id}|{epoch}'.encode()).hexdigest()[:24]
  row={'schema_version':'1.0','idea_id':idea_id,'plan_hash':plan_hash,'run_id':run_id,'phase':phase,'actor':actor,'authority_epoch':epoch,'authority_id':aid,'status':'active','acquired_at':_now(),'single_writer':True,'method_result_authority':False}
  _atomic(path,row); return row
def validate_authority(root:Path,idea_id:str,authority_id:str,plan_hash:str='')->dict[str,Any]:
 path,_=_paths(root,idea_id); row=_read(path)
 ok=row.get('status')=='active' and row.get('authority_id')==authority_id and (not plan_hash or row.get('plan_hash')==plan_hash)
 return {'valid':bool(ok),'authority':row}

def reconcile_authority(root:Path,idea_id:str,active_run_ids:set[str],grace_seconds:int=300)->dict[str,Any]:
 path,lock=_paths(root,idea_id)
 with lock.open('a+') as fh:
  fcntl.flock(fh.fileno(),fcntl.LOCK_EX); row=_read(path)
  if row.get('status')!='active' or str(row.get('run_id') or '') in active_run_ids: return row
  try: acquired=datetime.fromisoformat(str(row.get('acquired_at') or ''))
  except ValueError: return row
  if (datetime.now(timezone.utc)-acquired).total_seconds()<grace_seconds: return row
  row={**row,'status':'released','release_outcome':'reconciled-no-active-run','released_at':_now()}; _atomic(path,row); return row
def release_authority(root:Path,idea_id:str,authority_id:str,outcome:str='released')->dict[str,Any]:
 path,lock=_paths(root,idea_id)
 with lock.open('a+') as fh:
  fcntl.flock(fh.fileno(),fcntl.LOCK_EX); row=_read(path)
  if row.get('status')!='active' or row.get('authority_id')!=authority_id: raise RuntimeError(f'authority release mismatch for {idea_id}')
  row={**row,'status':'released','release_outcome':outcome,'released_at':_now()}; _atomic(path,row); return row
