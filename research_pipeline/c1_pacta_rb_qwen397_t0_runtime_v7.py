"""T0-v6 native MiniSWEAgent runtime with 16k source-only budget and bounded rate-limit transport recovery."""
from __future__ import annotations
import json, os, re, subprocess, time, urllib.error, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from jinja2 import Template
from research_pipeline.c1_pacta_rb_qwen397 import AA_BASE_URL, atomic_bytes, atomic_json, canonical, render_writer_input, sha256_file, sha256_text
from research_pipeline.asset_first_stri_reasoningbank_p1_core import load_agent_default

ROOTFUL_DOCKER_HOST="unix:///var/run/docker.sock"
SOURCE_MAX_COMPLETION_TOKENS=16384
PACTA_FIRST_DECISION_BUDGET=512
RATE_LIMIT_MAX_RETRIES=2
RATE_LIMIT_BACKOFF_SECONDS=(60,120)
ACTION_RE=re.compile(r"```bash\n(.*?)\n```",re.DOTALL)

def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def append_jsonl(path:Path,value:Any)->None:
    path.parent.mkdir(parents=True,exist_ok=True);raw=(canonical(value)+"\n").encode()
    with path.open("ab") as h:h.write(raw);h.flush();os.fsync(h.fileno())
def render(template:str,variables:dict[str,Any],**kwargs:Any)->str:return Template(template).render(**kwargs,**variables)
def parse_action(content:str)->str:
    found=ACTION_RE.findall(content)
    if len(found)!=1:raise ValueError(f"expected exactly one action, found {len(found)}")
    action=found[0].strip()
    if not action:raise ValueError("empty action")
    return action

def render_timeout_observation(config:dict[str,Any],action:str,output:str)->str:
    template=config["agent"].get("timeout_template") or load_agent_default("timeout_template")
    visible=render(template,{"task":"","selected_memory":""},action={"action":action},output=output)
    if not visible.strip():raise RuntimeError("official timeout observation rendered empty")
    return visible

def rate_limit_error(status:int|None,raw:bytes)->bool:
    if status not in (400,429):return False
    try:o=json.loads(raw.decode())
    except Exception:return False
    e=o.get("error") if isinstance(o,dict) else None
    return isinstance(e,dict) and str(e.get("code") or e.get("type") or "")=="rate_limit_exceeded"

class RawProvider:
    def __init__(self,key:str,root:Path,requested:str,resolved:str):
        if not key:raise RuntimeError("AA_API_KEY is not configured")
        self.key,self.root,self.requested,self.resolved=key,root,requested,resolved
        self.calls=self.transport_attempts=self.prompt_tokens=self.output_tokens=0
    def call(self,messages:list[dict[str,str]],label:str)->dict[str,Any]:
        self.calls+=1;logical=self.calls
        for attempt in range(1,RATE_LIMIT_MAX_RETRIES+2):
            self.transport_attempts+=1
            packet={"model":self.requested,"messages":messages,"stream":False,"n":1,
                "max_completion_tokens":SOURCE_MAX_COMPLETION_TOKENS,"temperature":0.0,
                "enable_thinking":False,"enable_search":False}
            safe={"endpoint":AA_BASE_URL+"/chat/completions","method":"POST","body":packet,
                "authorization_material_persisted":False,"logical_call":logical,"transport_attempt":attempt,
                "provider_retries_allowed":"rate_limit_only","max_rate_limit_retries":RATE_LIMIT_MAX_RETRIES}
            reqp=self.root/"raw"/f"request-{logical:04d}-attempt-{attempt:02d}.json"
            resp=self.root/"raw"/f"response-{logical:04d}-attempt-{attempt:02d}.json"
            reqsha=atomic_bytes(reqp,(canonical(safe)+"\n").encode())
            request=urllib.request.Request(AA_BASE_URL+"/chat/completions",data=canonical(packet).encode(),method="POST",
                headers={"Authorization":"Bearer "+self.key,"Content-Type":"application/json"})
            status=None
            try:
                with urllib.request.urlopen(request,timeout=360) as x:status=int(x.status);raw=x.read()
            except urllib.error.HTTPError as e:status=int(e.code);raw=e.read()
            ressha=atomic_bytes(resp,raw)
            base={"timestamp_utc":now(),"label":label,"logical_call":logical,"transport_attempt":attempt,
                "status_code":status,"request_path":str(reqp),"request_sha256":reqsha,"response_path":str(resp),
                "response_sha256":ressha,"response_bytes":len(raw),"persisted_before_parse":True,
                "requested_model":self.requested,"max_completion_tokens":SOURCE_MAX_COMPLETION_TOKENS}
            if status is None or not 200<=status<300:
                retryable=rate_limit_error(status,raw) and attempt<=RATE_LIMIT_MAX_RETRIES
                receipt={**base,"parse_status":"NOT_PARSED_HTTP_ERROR","rate_limit":rate_limit_error(status,raw),
                    "retryable":retryable,"model_content_observed":False}
                atomic_json(self.root/"calls"/f"{logical:04d}-attempt-{attempt:02d}.json",receipt)
                if retryable:
                    backoff=RATE_LIMIT_BACKOFF_SECONDS[attempt-1]
                    append_jsonl(self.root/"transport-journal.jsonl",{**receipt,"event":"rate_limit_backoff","backoff_seconds":backoff})
                    time.sleep(backoff);continue
                raise RuntimeError(f"provider HTTP {status}; raw preserved {ressha}")
            try:p=json.loads(raw.decode())
            except Exception:
                atomic_json(self.root/"calls"/f"{logical:04d}-attempt-{attempt:02d}.json",{**base,"parse_status":"JSON_PARSE_FAILED"});raise
            model=str(p.get("model") or "");u=p.get("usage") if isinstance(p.get("usage"),dict) else {}
            self.prompt_tokens+=int(u.get("prompt_tokens") or u.get("input_tokens") or 0);self.output_tokens+=int(u.get("completion_tokens") or u.get("output_tokens") or 0)
            content=str(p["choices"][0]["message"]["content"]);finish=str(p["choices"][0].get("finish_reason") or "")
            receipt={**base,"parse_status":"JSON_PARSED","response_id":str(p.get("id") or ""),"resolved_model":model,
                "model_drift":model!=self.resolved,"usage":u,"finish_reason":finish,"content_sha256":sha256_text(content),
                "model_content_observed":True}
            atomic_json(self.root/"calls"/f"{logical:04d}.json",receipt)
            atomic_json(self.root/"calls"/f"{logical:04d}-attempt-{attempt:02d}.json",receipt)
            if model!=self.resolved:raise RuntimeError("STOP_PROVIDER_IDENTITY_DRIFT")
            return {"content":content,"provider":receipt}
        raise AssertionError("unreachable")

class Container:
    def __init__(self,digest_ref:str,base_commit:str,root:Path):
        self.env=os.environ.copy();self.env["DOCKER_HOST"]=ROOTFUL_DOCKER_HOST;self.digest_ref=digest_ref
        self.name="c1-t0v6-"+os.urandom(6).hex()
        p=subprocess.run(["docker","run","-d","--name",self.name,"-w","/testbed","--rm",digest_ref,"sleep","2h"],text=True,capture_output=True,timeout=180,env=self.env,check=False)
        if p.returncode:raise RuntimeError(f"docker run failed: {p.stderr[-800:]}")
        self.container_id=p.stdout.strip()
        try:self._normalize(base_commit,root)
        except Exception:self.cleanup();raise
    def _git(self,*args:str,check=False):return subprocess.run(["docker","exec","-w","/testbed",self.container_id,"git",*args],text=True,capture_output=True,timeout=120,env=self.env,check=check)
    def _normalize(self,base:str,root:Path):
        initial=self._git("rev-parse","HEAD").stdout.strip();status=self._git("status","--porcelain").stdout
        exists=self._git("cat-file","-e",base+"^{commit}").returncode==0;ancestor=exists and self._git("merge-base","--is-ancestor",base,initial).returncode==0
        reset=self._git("reset","--hard",base) if exists and ancestor and not status else None
        post=self._git("rev-parse","HEAD").stdout.strip();post_status=self._git("status","--porcelain").stdout
        passed=bool(reset is not None and reset.returncode==0 and post==base and not post_status)
        atomic_json(root/"exact-base-normalization.json",{"schema_version":1,"created_at_utc":now(),"digest_ref":self.digest_ref,"observed_initial_head":initial,"frozen_base_commit":base,"base_commit_exists":exists,"base_is_ancestor":ancestor,"initial_working_tree_clean":not bool(status),"reset_returncode":None if reset is None else reset.returncode,"post_reset_head":post,"post_reset_head_exact":post==base,"post_reset_working_tree_clean":not bool(post_status),"exact_base_normalization_pass":passed,"persisted_before_provider_call":True})
        if not passed:raise RuntimeError("STOP_EXACT_BASE_NORMALIZATION_FAILED")
    def execute(self,action:str)->dict[str,Any]:
        try:
            p=subprocess.run(["docker","exec","-w","/testbed",self.container_id,"bash","-lc",action],text=True,encoding="utf-8",errors="replace",stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60,env=self.env,check=False)
            return {"output":p.stdout,"returncode":p.returncode,"timeout":False}
        except subprocess.TimeoutExpired as e:
            out=e.stdout if isinstance(e.stdout,str) else (e.stdout or b"").decode("utf-8",errors="replace");return {"output":out,"returncode":None,"timeout":True}
    def cleanup(self):subprocess.run(["docker","rm","-f",self.container_id],text=True,capture_output=True,timeout=90,env=self.env,check=False)

def initial_messages(task:str,config:dict[str,Any])->list[dict[str,str]]:
    v={"task":task,"selected_memory":""};a=config["agent"]
    return [{"role":"system","content":render(a["system_template"],v)},{"role":"user","content":render(a["instance_template"],v)}]

def execute_trajectory(instance:str,task:str,digest_ref:str,unit_root:Path,config:dict[str,Any],key:str,requested:str,resolved:str,base_commit:str)->dict[str,Any]:
    if unit_root.exists():raise RuntimeError(f"exactly-once unit root exists: {unit_root}")
    unit_root.mkdir(parents=True);provider=RawProvider(key,unit_root,requested,resolved);container=None
    messages=initial_messages(task,config);variables={"task":task,"selected_memory":""};terminal="NOT_STARTED";result_text="";failure_layer=None
    try:
        container=Container(digest_ref,base_commit,unit_root);append_jsonl(unit_root/"step-journal.jsonl",{"event":"trajectory_start","timestamp":now(),"messages":messages,"selected_memory":""})
        terminal="LimitsExceeded"
        for step in range(1,int(config["agent"]["step_limit"])+1):
            response=provider.call(messages,f"{instance}-step-{step}");content=response["content"];messages.append({"role":"assistant","content":content})
            try:action=parse_action(content)
            except Exception:
                error=render(config["agent"]["format_error_template"],variables,actions=ACTION_RE.findall(content));messages.append({"role":"user","content":error});append_jsonl(unit_root/"step-journal.jsonl",{"event":"format_error","step_index":step,"response_sha256":response["provider"]["response_sha256"],"finish_reason":response["provider"].get("finish_reason"),"error_message_sha256":sha256_text(error)});continue
            obs=container.execute(action);obsp=unit_root/"raw"/f"observation-{step:04d}.json";obssha=atomic_bytes(obsp,(json.dumps(obs,ensure_ascii=False,sort_keys=True)+"\n").encode())
            lines=obs["output"].lstrip().splitlines(keepends=True)
            if not obs["timeout"] and lines and lines[0].strip() in ("MINI_SWE_AGENT_FINAL_OUTPUT","COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT"):
                terminal="Submitted";result_text="".join(lines[1:]);messages.append({"role":"user","content":result_text});event="submitted"
            elif obs["timeout"]:
                user=render_timeout_observation(config,action,obs["output"]);messages.append({"role":"user","content":user});event="timeout"
            else:
                user=render(config["agent"]["action_observation_template"],variables,output=obs);messages.append({"role":"user","content":user});event="observation"
            append_jsonl(unit_root/"step-journal.jsonl",{"event":event,"step_index":step,"response_sha256":response["provider"]["response_sha256"],"parsed_action":action,"canonical_action_signature":action.strip(),"observation_path":str(obsp),"observation_sha256":obssha,"returncode":obs["returncode"]})
            if terminal=="Submitted":break
    except Exception as e:
        terminal=type(e).__name__;result_text=str(e);failure_layer="provider_identity" if "IDENTITY_DRIFT" in result_text else ("provider" if "provider HTTP" in result_text else "implementation")
        append_jsonl(unit_root/"step-journal.jsonl",{"event":"trajectory_exception","timestamp":now(),"error_type":terminal,"failure_layer":failure_layer,"error":result_text[:1000]})
    finally:
        if container is not None:container.cleanup()
        trajectory={"schema_version":1,"trajectory_format":"mini-swe-agent-1","instance_id":instance,"messages":messages,"exit_status":terminal,"result":result_text,"failure_layer":failure_layer,"model_stats":{"logical_calls":provider.calls,"transport_attempts":provider.transport_attempts,"prompt_tokens":provider.prompt_tokens,"completion_tokens":provider.output_tokens}}
        trajp=unit_root/"source_trajectory.json";atomic_json(trajp,trajectory);writerp=unit_root/"writer_input_trajectory.txt";writersha=atomic_bytes(writerp,render_writer_input(messages).encode("utf-8"))
        hashes={"source_trajectory_path":str(trajp),"source_trajectory_sha256":sha256_file(trajp),"writer_input_trajectory_path":str(writerp),"writer_input_trajectory_sha256":writersha};atomic_json(unit_root/"hashes.json",hashes)
        raw_responses=len(list((unit_root/"raw").glob("response-*-attempt-*.json")))
        valid=failure_layer is None and provider.calls>=1 and raw_responses==provider.transport_attempts
        run={"schema_version":1,"created_at_utc":now(),"source_task_id":instance,"task_sha256":sha256_text(task),"digest_ref":digest_ref,"frozen_base_commit":base_commit,"requested_model":requested,"resolved_model":resolved,"enable_thinking":False,"source_max_completion_tokens":SOURCE_MAX_COMPLETION_TOKENS,"pacta_first_decision_budget":PACTA_FIRST_DECISION_BUDGET,"temperature":0.0,"logical_attempt":1,"provider_logical_calls":provider.calls,"provider_transport_attempts":provider.transport_attempts,"input_tokens":provider.prompt_tokens,"output_tokens":provider.output_tokens,"terminal_status":terminal,"failure_layer":failure_layer,"validity_status":"TRAJECTORY_BACKED_VALID" if valid else "INVALID","invalid_reason":None if valid else (failure_layer or "provenance_incomplete"),"all_raw_responses_persisted":raw_responses==provider.transport_attempts,**hashes,"writer_calls":0,"binder_calls":0,"shadow_calls":0,"final_measurement_calls":0,"future_task_executions":0};atomic_json(unit_root/"run.json",run)
    return run
