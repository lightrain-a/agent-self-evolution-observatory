from __future__ import annotations
import hashlib,json,os,subprocess
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path
import pyarrow.parquet as pq

ROOT=Path(__file__).resolve().parents[2]
PAPER=ROOT/"paper_drafts/c1-manuscript-strengthening-20260825"
OFFICIAL=Path("/data/wyt/agent-self-evolution-observatory/external/stri-reasoningbank-iclr2026")
DATASET=Path("/data/wyt/agent-self-evolution-observatory/external/stri-swebench-verified-78f471bf655a3137b2e8a75af1501690ec009ec3/data/test-00000-of-00001.parquet")
Q0=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-deepseek-q0-20260831-v1")
P0=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-deepseek-p0-20260831-v1")
EXP="C1-PACTA-RB-DEEPSEEK-P0-20260831"; REQ="deepseek-v4-pro"; RES="deepseek-v4-pro-260425"
OFFICIAL_COMMIT="ed80611788292ea739f1effd31f16c53823b8a0d"
PRIOR={"sympy__sympy-13798","pytest-dev__pytest-5631","sympy__sympy-17318","sympy__sympy-18211","django__django-16100","django__django-11880","sphinx-doc__sphinx-9230"}
SCB=("Given the reusable memory, the ultimate software-engineering task, and the current decision context, "
     "produce one concise current-state action implication. Use the memory only when relevant, do not invent "
     "facts, and state what the agent should prioritize next. Output one sentence, at most 60 words, with no explanation.")
LADDER=[900,1200,1600,2048]; FORMAT=r"```bash\n(.*?)\n```"

now=lambda:datetime.now(timezone.utc).replace(microsecond=0).isoformat()
sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
shaf=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
canon=lambda x:json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def git(*a):return subprocess.check_output(["git",*a],cwd=ROOT,text=True).strip()
def dump(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);y=dict(x);y["payload_sha256"]=sha(canon(x));t=p.with_suffix(p.suffix+".tmp")
 with t.open("w",encoding="utf-8") as f:f.write(json.dumps(y,ensure_ascii=False,indent=2,sort_keys=True)+"\n");f.flush();os.fsync(f.fileno())
 t.replace(p);return shaf(p)

def official_files():
 rel={
  "config":"third_party/src/minisweagent/config/extra/swebench.yaml",
  "agent":"third_party/src/minisweagent/agents/default.py",
  "writer":"third_party/src/minisweagent/memory/instruction.py",
  "retrieval":"third_party/src/minisweagent/memory/memory_management.py",
  "runner":"third_party/src/minisweagent/run/extra/swebench.py"}
 return {k:{"path":str(OFFICIAL/v),"sha256":shaf(OFFICIAL/v)} for k,v in rel.items()}

def collision():
 needles=["min(B1","max(WS","rate-matched","rate_matched","shadow-policy","shadow policy","within-condition"]
 hits={}
 for p in OFFICIAL.rglob("*.py"):
  s=p.read_text(errors="ignore");f=[n for n in needles if n.lower() in s.lower()]
  if f:hits[str(p.relative_to(OFFICIAL))]=f
 joint=any(any("rate" in z.lower() for z in f) and any(("shadow" in z.lower() or "within" in z.lower()) for z in f) for f in hits.values())
 return {"search_terms":needles,"hits":hits,"complete_joint_signature_found":joint,
         "verdict":"STOP_CARRIER_METHOD_COLLISION" if joint else "NOVELTY_RESIDUAL_INHERITED_CARRIER_CLEAR"}

def pool():
 rows=pq.read_table(DATASET,columns=["instance_id","repo","problem_statement","base_commit"]).to_pylist();by=defaultdict(list)
 for r in rows:
  if r["instance_id"] not in PRIOR:by[str(r["repo"])].append(r)
 out=[]
 for repo,rs in sorted(by.items()):
  if len(rs)<2:continue
  s=min(rs,key=lambda r:(sha("C1-PACTA-RB-DEEPSEEK-SOURCE-v1|"+r["instance_id"]),r["instance_id"]))
  f=min((r for r in rs if r["instance_id"]!=s["instance_id"]),key=lambda r:(sha("C1-PACTA-RB-DEEPSEEK-FUTURE-v1|"+s["instance_id"]+"|"+r["instance_id"]),r["instance_id"]))
  uid=s["instance_id"]+"=>"+f["instance_id"]
  out.append({"unit_id":uid,"task_family":repo,"source_trajectory_id":"one-step-native-"+s["instance_id"],
   "source_task_id":s["instance_id"],"source_task":s["problem_statement"],"source_task_sha256":sha(s["problem_statement"]),"source_base_commit":s["base_commit"],
   "future_task_id":f["instance_id"],"future_task":f["problem_statement"],"future_task_sha256":sha(f["problem_statement"]),"future_base_commit":f["base_commit"],
   "pilot_rank":sha("C1-PACTA-RB-DEEPSEEK-P0-v1|"+uid),"random_gate_rank":sha("C1-PACTA-RB-DEEPSEEK-RANDOM-v1|"+uid),
   "prior_reasoningbank_scientific_output":False})
 return sorted(out,key=lambda r:(r["pilot_rank"],r["unit_id"]))

def main():
 live=git("rev-parse","origin/main");head=git("rev-parse","HEAD");off=git("-C",str(OFFICIAL),"rev-parse","HEAD");units=pool();col=collision()
 if off!=OFFICIAL_COMMIT:raise RuntimeError("official commit drift")
 if len(units)<6:raise RuntimeError("fresh support below six")
 if col["complete_joint_signature_found"]:raise RuntimeError("STOP_CARRIER_METHOD_COLLISION")
 rule=("one deterministic source/future pair per repository using frozen SHA salts; candidates ranked by "
       "SHA256('C1-PACTA-RB-DEEPSEEK-P0-v1'|unit_id); select first six with byte-distinct official writer twins")
 carrier={"schema_version":1,"experiment_id":EXP,"created_at_utc":now(),"live_origin_main":live,"design_git_sha":head,
  "selected_carrier":"SWE-bench Verified / official MiniSWEAgent","official_commit":off,"official_files":official_files(),
  "dataset":{"path":str(DATASET),"sha256":shaf(DATASET),"rows":500},
  "selection_basis":["implementation completeness","official provenance","existing shortest parser","fresh support","deterministic replayability"],
  "four_hard_conditions":{
   "A":"official SUCCESSFUL_SI and FAILED_SI on identical one-step native trace bytes; bundled writer-branch intervention",
   "B":"at least six byte-distinct memory pairs before binder",
   "C":"direct official selected_memory injection at identical position for both branches",
   "D":{"surface":"exactly one fenced bash command","regex":FORMAT,"canonical":"strip captured command","llm_judge":False}},
  "source_trajectory_scope":"one-step native policy trace; no environment execution, evaluator, gold patch, terminal, or full trajectory",
  "collision":col,"verdict":"C1_PACTA_RB_DEEPSEEK_CARRIER_QUALIFICATION_PRE_PROVIDER_PASS"}
 contract={"schema_version":1,"experiment_id":EXP,"created_at_utc":now(),"method":"PACTA-v2 unchanged; carrier adaptation only",
  "active_manuscript":"R9","shopping":"STOP_PACTA_ON_SHOPPING",
  "model":{"requested":REQ,"expected_resolved":RES,"all_roles_same":True,"thinking":"disabled","retries":0,"substitution":False},
  "qualification":{"fixtures":12,"budget_ladder":LADDER,"rule":"smallest budget with 12/12 completed+parsed, no drift/fallback"},
  "writer":{"official_branches_only":True,"same_trajectory_bytes":True,"temperature":0.2},
  "scb":{"instruction":SCB,"temperature":0.0,"max_output_tokens":180},
  "shadow":{"calls":144,"branches":2,"blocks":2,"replicates":6,"temperature":0.2,"gate":"min(B1,B2) > max(WS,WF)","geometry":"2..5 open"},
  "random_gate":{"ranking":"SHA256('C1-PACTA-RB-DEEPSEEK-RANDOM-v1'|unit_id)","rate_matched":True},
  "arms":{"A0":"native raw memory","A1":"SCB always","A2":"rate-matched random SCB","A3":"PACTA-selected SCB"},
  "final":{"calls":288,"fresh":True,"temperature":0.2},
  "primary":{"contrast":"A3-A2","thresholds":["mean>=0.05","positive>negative","A3-A0>0","A3-A1>=0"]},
  "persistence":"atomic fsync provider record before first-command parse",
  "locked":["terminal","second model","same-carrier confirmatory","R10"]}
 fresh={"schema_version":1,"experiment_id":EXP,"created_at_utc":now(),"prior_exclusion_ids":sorted(PRIOR),
  "selection_rule":rule,"candidate_count":len(units),"selected":"PENDING_WRITER_DIVERGENCE_ONLY","units":units,"outcome_fields_read":False}
 freeze={"schema_version":1,"experiment_id":EXP,"created_at_utc":now(),"live_origin_main":live,"design_git_sha":head,
  "official_commit":off,"contract_sha256":sha(canon(contract)),"carrier_sha256":sha(canon(carrier)),"fresh_pool_sha256":sha(canon(fresh)),
  "selection_rule":rule,"SCB_instruction_sha256":sha(SCB),"first_action_regex_sha256":sha(FORMAT),
  "budget_ladder":LADDER,"scientific_budget":"PENDING_QUALIFICATION","no_provider_output_observed":True,
  "random_gate_ranking":[{"unit_id":r["unit_id"],"rank":r["random_gate_rank"]} for r in sorted(units,key=lambda x:x["random_gate_rank"])]}
 artifacts={
  PAPER/"c1-pacta-rb-deepseek-carrier-audit-20260831.json":carrier,
  PAPER/"c1-pacta-rb-carrier-selection-20260831.json":carrier,
  PAPER/"c1-pacta-rb-deepseek-fresh-pool-20260831.json":fresh,
  PAPER/"c1-pacta-rb-deepseek-contract-20260831.json":contract,
  PAPER/"c1-pacta-rb-deepseek-pilot-freeze-20260831.json":freeze,
  Q0/"manifest.json":{"status":"FROZEN_PRE_PROVIDER","experiment_id":EXP,"created_at_utc":now(),"design_git_sha":head,"live_origin_main":live,"budget_ladder":LADDER},
  Q0/"contract.json":contract,Q0/"fresh-pool.json":fresh,
  P0/"manifest.json":{"status":"LOCKED_PENDING_QUALIFICATION","experiment_id":EXP,"created_at_utc":now(),"design_git_sha":head,"candidate_count":len(units)},
  P0/"contract.json":contract,P0/"fresh-pool.json":fresh,P0/"freeze.json":freeze,
  P0/"random-gate-ranking.json":{"status":"FROZEN_BEFORE_SHADOW_OUTPUT","ranking":freeze["random_gate_ranking"]}}
 for p,x in artifacts.items():dump(p,x)
 print(json.dumps({"status":carrier["verdict"],"live_origin_main":live,"candidates":len(units),"collision":col["verdict"]}))

if __name__=="__main__":main()
