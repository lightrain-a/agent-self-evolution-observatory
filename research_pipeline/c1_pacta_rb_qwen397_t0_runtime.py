"""T0 native MiniSWEAgent-compatible runtime with persist-before-parse."""
from __future__ import annotations
import json, os, re, subprocess, urllib.error, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from jinja2 import Template
from research_pipeline.c1_pacta_rb_qwen397 import AA_BASE_URL, atomic_bytes, atomic_json, canonical, render_writer_input, sha256_file, sha256_text, t0_validity

DOCKER_HOST="unix:///run/user/1006/e1-reasoningbank-docker.sock"
ROOTFUL_DOCKER_HOST="unix:///var/run/docker.sock"
ACTION_RE=re.compile(r"```bash\n(.*?)\n```",re.DOTALL)

def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def append_jsonl(path:Path,value:Any)->None:
 path.parent.mkdir(parents=True,exist_ok=True);raw=(canonical(value)+"\n").encode()
 with path.open("ab") as h:h.write(raw);h.flush();os.fsync(h.fileno())

def render(template:str,variables:dict[str,Any],**kwargs:Any)->str:
 return Template(template).render(**kwargs,**variables)

def parse_action(content:str)->str:
 actions=ACTION_RE.findall(content)
 if len(actions)!=1:raise ValueError(f"expected exactly one action, found {len(actions)}")
 action=actions[0].strip()
 if not action:raise ValueError("empty action")
 return action

class RawProvider:
 def __init__(self,key:str,root:Path,requested:str,resolved:str):
  if not key:raise RuntimeError("AA_API_KEY is not configured")
  self.key,self.root,self.requested,self.resolved=key,root,requested,resolved
  self.calls=self.prompt_tokens=self.output_tokens=0
 def call(self,messages:list[dict[str,str]],label:str)->dict[str,Any]:
  self.calls+=1
  packet={"model":self.requested,"messages":messages,"stream":False,"n":1,
   "max_completion_tokens":512,"temperature":0.0,"enable_thinking":False,"enable_search":False}
  safe={"endpoint":AA_BASE_URL+"/chat/completions","method":"POST","body":packet,
   "authorization_material_persisted":False,"transport_attempt":1,"provider_retries":0}
  req_path=self.root/"raw"/f"request-{self.calls:04d}.json"
  res_path=self.root/"raw"/f"response-{self.calls:04d}.json"
  req_sha=atomic_bytes(req_path,(canonical(safe)+"\n").encode())
  request=urllib.request.Request(AA_BASE_URL+"/chat/completions",data=canonical(packet).encode(),method="POST",
   headers={"Authorization":"Bearer "+self.key,"Content-Type":"application/json"})
  status=None
  try:
   with urllib.request.urlopen(request,timeout=240) as response:status=int(response.status);raw=response.read()
  except urllib.error.HTTPError as error:status=int(error.code);raw=error.read()
  res_sha=atomic_bytes(res_path,raw)
  base={"timestamp_utc":now(),"label":label,"step_index":self.calls,"status_code":status,
   "request_path":str(req_path),"request_sha256":req_sha,"response_path":str(res_path),
   "response_sha256":res_sha,"response_bytes":len(raw),"persisted_before_parse":True,
   "transport_attempt_count":1,"provider_retries":0}
  if status is None or not 200<=status<300:
   atomic_json(self.root/"calls"/f"{self.calls:04d}.json",{**base,"parse_status":"NOT_PARSED_HTTP_ERROR"})
   raise RuntimeError(f"provider HTTP {status}; raw preserved {res_sha}")
  try:payload=json.loads(raw.decode())
  except Exception:
   atomic_json(self.root/"calls"/f"{self.calls:04d}.json",{**base,"parse_status":"JSON_PARSE_FAILED"});raise
  model=str(payload.get("model") or "");usage=payload.get("usage") if isinstance(payload.get("usage"),dict) else {}
  self.prompt_tokens+=int(usage.get("prompt_tokens") or usage.get("input_tokens") or 0)
  self.output_tokens+=int(usage.get("completion_tokens") or usage.get("output_tokens") or 0)
  content=str(payload["choices"][0]["message"]["content"])
  call={**base,"parse_status":"JSON_PARSED","response_id":str(payload.get("id") or ""),
   "requested_model":self.requested,"resolved_model":model,"model_drift":model!=self.resolved,
   "usage":usage,"content_sha256":sha256_text(content)}
  atomic_json(self.root/"calls"/f"{self.calls:04d}.json",call)
  if model!=self.resolved:raise RuntimeError("STOP_PROVIDER_IDENTITY_DRIFT")
  return {"content":content,"provider":call}

class Container:
 def __init__(self,digest_ref:str,*,docker_host:str=DOCKER_HOST,base_commit:str|None=None,
  provenance_root:Path|None=None):
  self.env=os.environ.copy();self.env["DOCKER_HOST"]=docker_host;self.docker_host=docker_host;self.digest_ref=digest_ref
  name="c1-t0-"+os.urandom(6).hex()
  p=subprocess.run(["docker","run","-d","--name",name,"-w","/testbed","--rm",digest_ref,"sleep","2h"],
   text=True,capture_output=True,timeout=120,env=self.env,check=True)
  self.container_id=p.stdout.strip()
  if base_commit is not None:
   if provenance_root is None:
    self.cleanup();raise RuntimeError("provenance_root is required for exact-base normalization")
   try:self._normalize_exact_base(base_commit,provenance_root)
   except Exception:self.cleanup();raise
 def _git(self,*args:str,check:bool=True)->subprocess.CompletedProcess[str]:
  return subprocess.run(["docker","exec","-w","/testbed",self.container_id,"git",*args],text=True,
   capture_output=True,timeout=120,env=self.env,check=check)
 def _normalize_exact_base(self,base_commit:str,provenance_root:Path)->None:
  initial_head=self._git("rev-parse","HEAD").stdout.strip()
  initial_status=self._git("status","--porcelain").stdout
  exists=self._git("cat-file","-e",base_commit+"^{commit}",check=False).returncode==0
  ancestor=exists and self._git("merge-base","--is-ancestor",base_commit,initial_head,check=False).returncode==0
  precondition=not initial_status and exists and ancestor
  reset=self._git("reset","--hard",base_commit,check=False) if precondition else None
  post_head=self._git("rev-parse","HEAD").stdout.strip()
  post_status=self._git("status","--porcelain").stdout
  passed=bool(precondition and reset and reset.returncode==0 and post_head==base_commit and not post_status)
  audit={"schema_version":1,"created_at_utc":now(),"docker_host":self.docker_host,
   "digest_ref":self.digest_ref,"frozen_base_commit":base_commit,
   "observed_initial_head":initial_head,"initial_working_tree_clean":not bool(initial_status),
   "base_commit_exists":exists,"base_is_ancestor":ancestor,"reset_attempted":precondition,
   "reset_returncode":None if reset is None else reset.returncode,
   "reset_stdout":None if reset is None else reset.stdout,"reset_stderr":None if reset is None else reset.stderr,
   "post_reset_head":post_head,"post_reset_head_exact":post_head==base_commit,
   "post_reset_working_tree_clean":not bool(post_status),"exact_base_normalization_pass":passed,
   "persisted_before_provider_call":True}
  atomic_json(provenance_root/"exact-base-normalization.json",audit)
  if not passed:raise RuntimeError("STOP_EXACT_BASE_NORMALIZATION_FAILED")
 def execute(self,action:str)->dict[str,Any]:
  try:
   p=subprocess.run(["docker","exec","-w","/testbed",self.container_id,"bash","-lc",action],
    text=True,encoding="utf-8",errors="replace",stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
    timeout=60,env=self.env,check=False)
   return {"output":p.stdout,"returncode":p.returncode,"timeout":False}
  except subprocess.TimeoutExpired as e:
   out=e.stdout if isinstance(e.stdout,str) else (e.stdout or b"").decode("utf-8",errors="replace")
   return {"output":out,"returncode":None,"timeout":True}
 def cleanup(self):
  subprocess.run(["docker","rm","-f",self.container_id],text=True,capture_output=True,timeout=90,env=self.env,check=False)

def initial_messages(task:str,config:dict[str,Any])->list[dict[str,str]]:
 variables={"task":task,"selected_memory":""};agent=config["agent"]
 return [{"role":"system","content":render(agent["system_template"],variables)},
  {"role":"user","content":render(agent["instance_template"],variables)}]

def execute_trajectory(instance:str,task:str,digest_ref:str,unit_root:Path,config:dict[str,Any],
 key:str,requested:str,resolved:str,*,docker_host:str=DOCKER_HOST,base_commit:str|None=None)->dict[str,Any]:
 if unit_root.exists():raise RuntimeError(f"exactly-once unit root exists: {unit_root}")
 unit_root.mkdir(parents=True)
 provider=RawProvider(key,unit_root,requested,resolved)
 container=Container(digest_ref,docker_host=docker_host,base_commit=base_commit,provenance_root=unit_root)
 messages=initial_messages(task,config);variables={"task":task,"selected_memory":""}
 append_jsonl(unit_root/"step-journal.jsonl",{"event":"trajectory_start","timestamp":now(),"messages":messages,"selected_memory":""})
 terminal="LimitsExceeded";result_text="";corrupt=False
 try:
  for step in range(1,int(config["agent"]["step_limit"])+1):
   response=provider.call(messages,f"{instance}-step-{step}");content=response["content"]
   messages.append({"role":"assistant","content":content})
   try:action=parse_action(content)
   except Exception:
    error=render(config["agent"]["format_error_template"],variables,actions=ACTION_RE.findall(content))
    messages.append({"role":"user","content":error})
    append_jsonl(unit_root/"step-journal.jsonl",{"event":"format_error","step_index":step,
     "response_sha256":response["provider"]["response_sha256"],"error_message_sha256":sha256_text(error)})
    continue
   observation=container.execute(action)
   obs_path=unit_root/"raw"/f"observation-{step:04d}.json"
   obs_sha=atomic_bytes(obs_path,(json.dumps(observation,ensure_ascii=False,sort_keys=True)+"\n").encode())
   lines=observation["output"].lstrip().splitlines(keepends=True)
   if not observation["timeout"] and lines and lines[0].strip() in ("MINI_SWE_AGENT_FINAL_OUTPUT","COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT"):
    terminal="Submitted";result_text="".join(lines[1:]);messages.append({"role":"user","content":result_text});event="submitted"
   elif observation["timeout"]:
    user=render(config["agent"]["timeout_template"],variables,action={"action":action},output=observation["output"])
    messages.append({"role":"user","content":user});event="timeout"
   else:
    user=render(config["agent"]["action_observation_template"],variables,output=observation)
    messages.append({"role":"user","content":user});event="observation"
   append_jsonl(unit_root/"step-journal.jsonl",{"event":event,"step_index":step,
    "response_sha256":response["provider"]["response_sha256"],"parsed_action":action,
    "canonical_action_signature":action.strip(),"observation_path":str(obs_path),
    "observation_sha256":obs_sha,"returncode":observation["returncode"]})
   if terminal=="Submitted":break
 except Exception as error:
  terminal=type(error).__name__;result_text=str(error);corrupt="IDENTITY_DRIFT" in result_text
  append_jsonl(unit_root/"step-journal.jsonl",{"event":"trajectory_exception","timestamp":now(),
   "error_type":terminal,"error":result_text[:1000]})
  raise
 finally:
  container.cleanup()
  trajectory={"schema_version":1,"trajectory_format":"mini-swe-agent-1","instance_id":instance,
   "messages":messages,"exit_status":terminal,"result":result_text,
   "model_stats":{"n_calls":provider.calls,"prompt_tokens":provider.prompt_tokens,"completion_tokens":provider.output_tokens}}
  traj_path=unit_root/"source_trajectory.json";atomic_json(traj_path,trajectory)
  writer_path=unit_root/"writer_input_trajectory.txt"
  writer_sha=atomic_bytes(writer_path,render_writer_input(messages).encode("utf-8"))
  hashes={"source_trajectory_path":str(traj_path),"source_trajectory_sha256":sha256_file(traj_path),
   "writer_input_trajectory_path":str(writer_path),"writer_input_trajectory_sha256":writer_sha}
  atomic_json(unit_root/"hashes.json",hashes)
 unit={"unit_id":instance,"source_task_id":instance,"native_trajectory_executed":True,
  "model_call_count":provider.calls,"all_raw_responses_persisted":provider.calls==len(list((unit_root/"raw").glob("response-*.json"))),
  "model_drift":False,"provider_packet_drift":False,"instrumentation_corruption":corrupt,**hashes}
 valid,reason=t0_validity(unit)
 run={**unit,"schema_version":1,"created_at_utc":now(),"task_sha256":sha256_text(task),"digest_ref":digest_ref,
  "requested_model":requested,"resolved_model":resolved,"enable_thinking":False,"max_completion_tokens":512,
  "temperature":0.0,"provider_retries":0,"logical_attempt":1,"selected_memory":"",
  "docker_host":docker_host,"frozen_base_commit":base_commit,
  "input_tokens":provider.prompt_tokens,"output_tokens":provider.output_tokens,"terminal_status":terminal,
  "source_evaluator_outcome":None,"validity_status":"TRAJECTORY_BACKED_VALID" if valid else "INVALID",
  "invalid_reason":None if valid else reason,"writer_calls":0,"binder_calls":0,"shadow_calls":0,
  "final_measurement_calls":0,"future_task_executions":0}
 atomic_json(unit_root/"run.json",run);return run
