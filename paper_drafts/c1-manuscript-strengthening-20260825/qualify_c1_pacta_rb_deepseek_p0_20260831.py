from __future__ import annotations
import argparse,copy,fcntl,hashlib,json,os,re,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(ROOT))
from research_pipeline.asset_first_stri_reasoningbank_ark_provider import ArkReasoningBankClient,ArkReasoningBankSettings,CANONICAL_SECRET_FILE
from research_pipeline.asset_first_stri_reasoningbank_p1_core import render_messages

Q0=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-deepseek-q0-20260831-v1")
P0=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-deepseek-p0-20260831-v1")
PAPER=HERE
REQ="deepseek-v4-pro";RES="deepseek-v4-pro-260425";LADDER=[900,1200,1600,2048]
PATTERN=re.compile(r"```bash\n(.*?)\n```",re.DOTALL)
FIXTURES=[
 "A Python package reports that a public function returns the wrong type. Inspect the repository and identify the first useful shell command.",
 "A regression appears in array indexing after a refactor. Begin by locating the relevant implementation and tests.",
 "Documentation generation fails on a new directive. Start investigating the repository with one shell command.",
 "An HTTP client mishandles an empty header value. Issue the first repository-inspection command.",
 "A plotting option is ignored when a legend is present. Begin a careful code search.",
 "A classifier validates a parameter too late. Start by locating the validation path.",
 "A linter emits a duplicate warning for nested functions. Choose the first diagnostic shell action.",
 "A web framework URL helper escapes a value twice. Start inspecting the implementation.",
 "A symbolic simplifier loses an assumption. Begin with a targeted repository search.",
 "A dataframe coordinate conversion changes dimension order. Choose the first code-inspection action.",
 "A test runner fixture finalizer is called twice. Start locating the fixture lifecycle code.",
 "A visualization library rejects a valid palette object. Begin with one shell command."
]

now=lambda:datetime.now(timezone.utc).replace(microsecond=0).isoformat()
sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
def canon(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def dump(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);y=dict(x);y["payload_sha256"]=sha(canon(x));t=p.with_suffix(p.suffix+".tmp")
 with t.open("w",encoding="utf-8") as f:f.write(json.dumps(y,ensure_ascii=False,indent=2,sort_keys=True)+"\n");f.flush();os.fsync(f.fileno())
 t.replace(p)
def git(*a):return subprocess.check_output(["git",*a],cwd=ROOT,text=True).strip()
def parse(text):
 found=PATTERN.findall(text)
 if len(found)!=1:raise ValueError(f"expected one native action, found {len(found)}")
 action=found[0].strip()
 if not action:raise ValueError("empty action")
 return action

def client():
 b=ArkReasoningBankSettings.from_env_file(CANONICAL_SECRET_FILE)
 return ArkReasoningBankClient(ArkReasoningBankSettings(api_key=b.api_key,base_url=b.base_url,model=REQ,timeout_seconds=180,max_retries=0))

def main():
 Q0.mkdir(parents=True,exist_ok=True)
 lock=(Q0/".lock").open("a+");fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 if git("status","--porcelain"):raise RuntimeError("qualification requires clean committed worktree")
 manifest=json.loads((Q0/"manifest.json").read_text());manifest.update({"status":"QUALIFICATION_RUNNING","execution_git_sha":git("rev-parse","HEAD"),"started_at_utc":now()});dump(Q0/"manifest.json",manifest)
 c=client();all_rows=[];selected=None;binding=None
 for budget in LADDER:
  rows=[]
  for idx,task in enumerate(FIXTURES,1):
   cid=f"budget-{budget}__fixture-{idx:02d}";messages=render_messages(task,"");prompt_sha=sha(canon(messages));path=Q0/"responses"/f"{cid}.json"
   if path.exists():raise RuntimeError("qualification artifacts already exist; no resume/retry")
   try:
    r=c.create_response(input_items=messages,model=REQ,max_output_tokens=budget,temperature=0.2,store=True,thinking="disabled")
    raw=str(r.get("raw_text",r.get("text","")))
    record={"schema_version":1,"case_id":cid,"fixture_id":idx,"non_scientific":True,"budget":budget,
      "prompt_sha256":prompt_sha,"response_id":r.get("response_id"),"status":r.get("status"),
      "requested_model":r.get("requested_model"),"resolved_model":r.get("resolved_model"),
      "thinking_requested":"disabled","thinking_compatibility_fallback":False,"usage":r.get("usage") or {},
      "incomplete_details":r.get("incomplete_details") or {},"raw_response":raw,"raw_response_sha256":sha(raw),
      "provider_returned_at_utc":now(),"persisted_before_parse":True}
    dump(path,record)
    if r.get("requested_model")!=REQ or r.get("resolved_model")!=RES:
     binding={"schema_version":1,"experiment_id":"C1-PACTA-RB-DEEPSEEK-P0-20260831","created_at_utc":now(),
      "status":"STOP_MODEL_BINDING","expected_requested_model":REQ,"expected_resolved_model":RES,
      "requested_model":r.get("requested_model"),"resolved_model":r.get("resolved_model"),"case_id":cid,
      "response_artifact":str(path),"response_artifact_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
      "scientific_provider_calls":0,"substitution_attempted":False}
     dump(PAPER/"c1-pacta-rb-deepseek-model-binding-20260831.json",binding)
     manifest.update({"status":"STOP_MODEL_BINDING","stop_case_id":cid,"actual_resolved_model":r.get("resolved_model"),"completed_at_utc":now()})
     dump(Q0/"manifest.json",manifest)
     raise RuntimeError("STOP_MODEL_BINDING")
    action=parse(raw);record["parse_status"]="PASS";record["first_action"]=action;record["first_action_sha256"]=sha(action);dump(path,record)
    row={"case_id":cid,"pass":r.get("status")=="completed","status":r.get("status"),"action_sha256":sha(action),"resolved_model":r.get("resolved_model")}
   except RuntimeError:raise
   except Exception as e:
    row={"case_id":cid,"pass":False,"failure_type":type(e).__name__,"failure":str(e)[:500]}
    if not path.exists():dump(path,{"case_id":cid,"status":"provider_failure","failure_type":type(e).__name__,"failure":str(e)[:500],"persisted_before_parse":False})
   rows.append(row);all_rows.append(row)
   dump(Q0/"progress.json",{"status":"RUNNING","tested":len(all_rows),"current_budget":budget,"updated_at_utc":now()})
  budget_pass=len(rows)==len(FIXTURES) and all(r["pass"] for r in rows)
  if budget_pass:selected=budget;break
 binding={"schema_version":1,"experiment_id":"C1-PACTA-RB-DEEPSEEK-P0-20260831","created_at_utc":now(),
  "status":"MODEL_BINDING_PASS" if selected else "MODEL_BINDING_NOT_ESTABLISHED","requested_model":REQ,"resolved_model":RES if selected else None,
  "all_roles_bound_to_same_model":True,"substitution":False}
 dump(PAPER/"c1-pacta-rb-deepseek-model-binding-20260831.json",binding)
 result={"schema_version":1,"experiment_id":"C1-PACTA-RB-DEEPSEEK-P0-20260831","created_at_utc":now(),
  "status":"DEEPSEEK_ACTION_AVAILABILITY_PASS" if selected else "STOP_DEEPSEEK_ACTION_AVAILABILITY",
  "fixture_count":len(FIXTURES),"budget_ladder":LADDER,"tested_rows":len(all_rows),"selected_scientific_max_output_tokens":selected,
  "requirements":{"provider_completed":"100% at selected budget","first_action":"100%","write_before_parse":"100%","deterministic_parser":"100%","model_drift":0,"thinking_fallback":0},
  "rows":all_rows}
 dump(Q0/"action-availability-qualification.json",result);dump(PAPER/"c1-pacta-rb-deepseek-action-availability-qualification-20260831.json",result)
 manifest.update({"status":result["status"],"selected_scientific_max_output_tokens":selected,"completed_at_utc":now()});dump(Q0/"manifest.json",manifest)
 if not selected:raise RuntimeError("STOP_DEEPSEEK_ACTION_AVAILABILITY")
 # Freeze selected budget in both run roots and paper artifact before any scientific call.
 freeze=json.loads((P0/"freeze.json").read_text());freeze["scientific_budget"]=selected;freeze["qualification_artifact_sha256"]=hashlib.sha256((Q0/"action-availability-qualification.json").read_bytes()).hexdigest();freeze["qualified_at_utc"]=now();dump(P0/"freeze.json",freeze)
 paper_freeze=PAPER/"c1-pacta-rb-deepseek-pilot-freeze-20260831.json";dump(paper_freeze,freeze)
 pman=json.loads((P0/"manifest.json").read_text());pman.update({"status":"QUALIFIED_LOCKED_PENDING_SCIENTIFIC_EXECUTION","scientific_max_output_tokens":selected,"qualification_git_sha":git("rev-parse","HEAD")});dump(P0/"manifest.json",pman)
 print(json.dumps({"status":result["status"],"selected_budget":selected,"requested":REQ,"resolved":RES}))

if __name__=="__main__":main()
