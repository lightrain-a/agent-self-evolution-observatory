"""Frozen PACTA/Qwen397 preflight primitives; no scientific execution on import."""
from __future__ import annotations
import hashlib,json,os,re,tempfile,urllib.error,urllib.request
from collections import Counter
from pathlib import Path
from typing import Any

AA_BASE_URL="https://api.aa.com.cn/api/v1"
MODEL_FAMILY="qwen3.5-397b-a17b"
FIRST_ACTION_RE=re.compile(r"```bash\n(.*?)\n```",re.DOTALL)
PILOT_SALT="C1-PACTA-RB-QWEN35-397B-P0-v1"
RANDOM_SALT="C1-PACTA-RB-QWEN35-397B-RANDOM-v1"
BUDGET_LADDER=(512,1024,2048,4096)
ARMS=("A0_NATIVE","A1_SCB_ALWAYS","A2_RATE_MATCHED_RANDOM","A3_PACTA")
BRANCHES=("success","failure")

def sha256_text(value:str)->str:
 return hashlib.sha256(value.encode("utf-8")).hexdigest()
def sha256_file(path:Path)->str:
 return hashlib.sha256(path.read_bytes()).hexdigest()
def canonical(value:Any)->str:
 return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"))

def atomic_json(path:Path,payload:dict[str,Any])->None:
 path.parent.mkdir(parents=True,exist_ok=True)
 body=dict(payload);body["payload_sha256"]=sha256_text(canonical(payload))
 fd,name=tempfile.mkstemp(prefix=path.name+".",suffix=".tmp",dir=path.parent)
 try:
  with os.fdopen(fd,"w",encoding="utf-8") as h:
   json.dump(body,h,ensure_ascii=False,indent=2,sort_keys=True);h.write("\n");h.flush();os.fsync(h.fileno())
  os.replace(name,path)
  dfd=os.open(path.parent,os.O_RDONLY)
  try:os.fsync(dfd)
  finally:os.close(dfd)
 except Exception:
  try:os.unlink(name)
  except FileNotFoundError:pass
  raise

class AAProvider:
 def __init__(self,api_key:str|None=None,base_url:str=AA_BASE_URL,timeout:float=180):
  self.api_key=api_key or os.environ.get("AA_API_KEY","")
  if not self.api_key:raise RuntimeError("AA_API_KEY is not configured")
  self.base_url=base_url.rstrip("/");self.timeout=timeout
 def _request(self,method:str,path:str,body:dict[str,Any]|None=None)->tuple[bytes,dict[str,Any]]:
  data=None if body is None else canonical(body).encode()
  req=urllib.request.Request(self.base_url+path,data=data,method=method,headers={
   "Authorization":"Bearer "+self.api_key,"Content-Type":"application/json"})
  try:
   with urllib.request.urlopen(req,timeout=self.timeout) as response:raw=response.read()
  except urllib.error.HTTPError as e:
   raw=e.read();raise RuntimeError(f"AA HTTP {e.code}; body_sha256={hashlib.sha256(raw).hexdigest()}") from e
  try:parsed=json.loads(raw)
  except Exception as e:raise RuntimeError(f"AA non-JSON response; body_sha256={hashlib.sha256(raw).hexdigest()}") from e
  return raw,parsed
 def models(self)->tuple[bytes,dict[str,Any]]:
  return self._request("GET","/models")
 def chat(self,*,model:str,messages:list[dict[str,str]],max_completion_tokens:int,temperature:float,enable_thinking:bool)->tuple[bytes,dict[str,Any]]:
  return self._request("POST","/chat/completions",{"model":model,"messages":messages,"stream":False,"n":1,
   "max_completion_tokens":max_completion_tokens,"temperature":temperature,"enable_thinking":enable_thinking,
   "enable_search":False})

def discover_qwen397(model_ids:list[str])->str:
 exact=[x for x in model_ids if x.lower()==MODEL_FAMILY]
 dated=sorted(x for x in model_ids if x.lower().startswith(MODEL_FAMILY+"-") and re.search(r"\d{4}[-_]?\d{2}[-_]?\d{2}|\d{6,8}$",x))
 if dated:return dated[-1]
 if exact:return exact[0]
 raise ValueError("STOP_QWEN397_MODEL_UNAVAILABLE")

def freeze_model_binding(rows:list[dict[str,Any]])->dict[str,str]:
 if len(rows)!=3:raise ValueError("model binding requires exactly three probes")
 requested={str(r.get("requested_model") or "") for r in rows};resolved={str(r.get("resolved_model") or "") for r in rows};endpoint={str(r.get("endpoint") or "") for r in rows}
 if len(requested)!=1 or len(resolved)!=1 or len(endpoint)!=1:raise ValueError("STOP_MODEL_DRIFT")
 if any(r.get("fallback") for r in rows):raise ValueError("fallback observed")
 return {"requested_model":requested.pop(),"resolved_or_returned_model":resolved.pop(),"endpoint":endpoint.pop()}

def parse_first_decision(text:str)->str:
 found=FIRST_ACTION_RE.findall(text)
 if len(found)!=1:raise ValueError(f"expected exactly one fenced bash action, found {len(found)}")
 action=found[0].strip()
 if not action:raise ValueError("empty first action")
 return action

def choose_budget(rows_by_budget:dict[int,list[dict[str,Any]]])->int:
 for budget in BUDGET_LADDER:
  rows=rows_by_budget.get(budget,[])
  if len(rows)==20 and all(r.get("provider_success") and r.get("status")=="completed" and r.get("parse_success")
                           and r.get("persisted_before_parse") and not r.get("model_drift")
                           and not r.get("fallback") and not r.get("ambiguous") for r in rows):
   return budget
 raise ValueError("STOP_ACTION_BEFORE_BUDGET")

def trajectory_backed(unit:dict[str,Any])->tuple[bool,str]:
 path=unit.get("source_trajectory_path");expected=unit.get("source_trajectory_sha256")
 if not path or not expected:return False,"missing trajectory path/hash"
 p=Path(path)
 if not p.is_file():return False,"trajectory file absent"
 if sha256_file(p)!=expected:return False,"trajectory hash mismatch"
 return True,"pass"

def validate_fresh_pool(units:list[dict[str,Any]])->dict[str,Any]:
 rows=[]
 for unit in units:
  ok,reason=trajectory_backed(unit)
  rows.append({"unit_id":unit["unit_id"],"task_family":unit["task_family"],"trajectory_backed":ok,"reason":reason,
   "prior_scientific_output":bool(unit.get("prior_reasoningbank_scientific_output"))})
 valid=[r for r in rows if r["trajectory_backed"] and not r["prior_scientific_output"]]
 repos={r["task_family"] for r in valid}
 return {"rows":rows,"valid_unit_count":len(valid),"valid_repository_count":len(repos),
  "status":"FRESH_SUPPORT_PASS" if len(valid)>=6 and len(repos)>=6 else "HOLD_FRESH_SUPPORT_INSUFFICIENT"}

def pilot_split(units:list[dict[str,Any]])->dict[str,Any]:
 eligible=[u for u in units if trajectory_backed(u)[0] and not u.get("prior_reasoningbank_scientific_output")]
 ranked=sorted(eligible,key=lambda u:(sha256_text(PILOT_SALT+"|"+u["unit_id"]),u["unit_id"]))
 if len(ranked)<6:return {"status":"NOT_REALIZED_FRESH_SUPPORT_INSUFFICIENT","pilot":[],"sealed":[u["unit_id"] for u in units]}
 return {"status":"FROZEN","pilot":[u["unit_id"] for u in ranked[:6]],"sealed":[u["unit_id"] for u in ranked[6:]]}

def writer_twins_valid(success:dict[str,Any],failure:dict[str,Any])->bool:
 same=("trajectory_sha256","source_task_sha256","requested_model","resolved_model","temperature","context_sha256")
 return all(success.get(k)==failure.get(k) for k in same) and success.get("branch")=="success" and failure.get("branch")=="failure" and success.get("memory_sha256")!=failure.get("memory_sha256")

def build_shadow_schedule(units:list[dict[str,Any]])->list[dict[str,Any]]:
 rows=[]
 for u in units:
  for branch in BRANCHES:
   for block in (1,2):
    for replicate in range(1,7):
     case=f"{u['unit_id']}__{branch}__b{block}__r{replicate}"
     rows.append({"case_id":case,"unit_id":u["unit_id"],"repository":u["task_family"],"branch":branch,
      "block":block,"replicate":replicate,"order_key":sha256_text("C1-PACTA-RB-QWEN397-SHADOW|"+case)})
 rows.sort(key=lambda r:r["order_key"])
 if len(rows)!=len(units)*24:raise AssertionError("shadow geometry")
 return rows

def tv(left:list[str],right:list[str])->float:
 if not left or not right:raise ValueError("empty distribution")
 a,b=Counter(left),Counter(right);keys=set(a)|set(b)
 return .5*sum(abs(a[k]/len(left)-b[k]/len(right)) for k in keys)

def gate(samples:dict[str,list[str]])->dict[str,Any]:
 for key in ("S1","S2","F1","F2"):
  if len(samples.get(key,[]))!=6:raise ValueError("HOLD_SHADOW_CALIBRATION")
 b1=tv(samples["S1"],samples["F1"]);b2=tv(samples["S2"],samples["F2"])
 ws=tv(samples["S1"],samples["S2"]);wf=tv(samples["F1"],samples["F2"])
 return {"B1":b1,"B2":b2,"WS":ws,"WF":wf,"G":min(b1,b2)>max(ws,wf)}

def rate_matched_random(unit_ids:list[str],k:int)->list[str]:
 return sorted(unit_ids,key=lambda x:(sha256_text(RANDOM_SALT+"|"+x),x))[:k]

def build_final_schedule(units:list[dict[str,Any]],pacta_open:set[str],random_open:set[str])->list[dict[str,Any]]:
 rows=[]
 for u in units:
  for arm in ARMS:
   for branch in BRANCHES:
    for replicate in range(1,7):
     use_scb=arm=="A1_SCB_ALWAYS" or (arm=="A2_RATE_MATCHED_RANDOM" and u["unit_id"] in random_open) or (arm=="A3_PACTA" and u["unit_id"] in pacta_open)
     case=f"{u['unit_id']}__{arm}__{branch}__r{replicate}"
     rows.append({"case_id":case,"unit_id":u["unit_id"],"arm":arm,"branch":branch,"replicate":replicate,
      "uses_scb":use_scb,"order_key":sha256_text("C1-PACTA-RB-QWEN397-FINAL|"+case)})
 rows.sort(key=lambda r:r["order_key"])
 if len(rows)!=len(units)*48:raise AssertionError("final geometry")
 return rows
