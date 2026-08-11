from __future__ import annotations

import fcntl, hashlib, json, os, re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

def _now(): return datetime.now(timezone.utc).replace(microsecond=0)
def _iso(dt): return dt.isoformat()
def _slug(s:str): return re.sub(r"[^A-Za-z0-9_.-]+","-",s).strip("-")[:160] or "resource"
def _paths(root:Path,server_id:str,gpu_uuid:str):
 d=root/"resource-leases"; d.mkdir(parents=True,exist_ok=True); stem=_slug(f"{server_id}-{gpu_uuid}"); return d/f"{stem}.json",d/f".{stem}.lock"
def _read(path:Path)->dict[str,Any]:
 try: return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
 except (OSError,json.JSONDecodeError): return {}
def _atomic(path:Path,row:dict[str,Any]):
 tmp=path.with_suffix(path.suffix+".tmp"); tmp.write_text(json.dumps(row,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); os.replace(tmp,path)
def _active(row:dict[str,Any])->bool:
 if row.get("status")!="active": return False
 try: return datetime.fromisoformat(str(row.get("expires_at")))>_now()
 except ValueError: return True

def acquire_gpu_lease(root:Path,server_id:str,gpu_uuid:str,run_id:str,owner:str,ttl_minutes:int=720)->dict[str,Any]:
 path,lock=_paths(root,server_id,gpu_uuid)
 with lock.open("a+") as handle:
  fcntl.flock(handle.fileno(),fcntl.LOCK_EX); old=_read(path)
  if _active(old):
   if old.get("run_id")==run_id: return old
   raise RuntimeError(f"GPU lease already active on {server_id}:{gpu_uuid}: run={old.get('run_id')}")
  epoch=int(old.get("lease_epoch") or 0)+1; now=_now(); lid=hashlib.sha256(f"{server_id}|{gpu_uuid}|{run_id}|{epoch}".encode()).hexdigest()[:24]
  row={"schema_version":"1.0","server_id":server_id,"gpu_uuid":gpu_uuid,"run_id":run_id,"owner":owner,"lease_epoch":epoch,"lease_id":lid,"status":"active","acquired_at":_iso(now),"expires_at":_iso(now+timedelta(minutes=max(10,ttl_minutes)))}
  _atomic(path,row); return row

def release_gpu_lease(root:Path,server_id:str,gpu_uuid:str,lease_id:str,outcome:str="released")->dict[str,Any]:
 path,lock=_paths(root,server_id,gpu_uuid)
 with lock.open("a+") as handle:
  fcntl.flock(handle.fileno(),fcntl.LOCK_EX); row=_read(path)
  if row.get("status")!="active" or row.get("lease_id")!=lease_id: raise RuntimeError("GPU lease release mismatch")
  row={**row,"status":"released","release_outcome":outcome,"released_at":_iso(_now())}; _atomic(path,row); return row

def list_gpu_leases(root:Path,active_only:bool=True)->list[dict[str,Any]]:
 d=root/"resource-leases"; rows=[]
 if not d.exists(): return rows
 for path in sorted(d.glob("*.json")):
  row=_read(path)
  if not row: continue
  if active_only and not _active(row): continue
  rows.append({"path":str(path),**row})
 return rows

def active_gpu_uuids(root:Path)->set[str]:
 return {str(row.get("gpu_uuid")) for row in list_gpu_leases(root,True) if row.get("gpu_uuid")}

def reconcile_gpu_leases(root:Path,active_run_ids:set[str],grace_seconds:int=300)->list[dict[str,Any]]:
 released=[]; now=_now()
 for row in list_gpu_leases(root,True):
  if str(row.get("run_id")) in active_run_ids: continue
  try: acquired=datetime.fromisoformat(str(row.get("acquired_at")))
  except ValueError: continue
  if (now-acquired).total_seconds()<grace_seconds: continue
  try: released.append(release_gpu_lease(root,str(row.get("server_id")),str(row.get("gpu_uuid")),str(row.get("lease_id")),"reconciled-no-active-run"))
  except RuntimeError: pass
 return released
