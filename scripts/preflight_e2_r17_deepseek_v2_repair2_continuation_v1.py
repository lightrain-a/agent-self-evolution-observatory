#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, sqlite3, subprocess, sys, tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from research_pipeline.e2_r17_provider_budget import ProviderBudgetLedger
from scripts.run_e2_r17_e1_a_pool_support import validate_runtime as validate_actor_runtime
from scripts.run_e2_r17_e1_b_transition_runtime_pilot import atomic_json,load_json,require,sha_file
from scripts.run_e2_r17_deepseek_v2_repair2_continuation_v1 import validate_contract_auth,validate_evidence

ACTOR=ROOT/"scripts/run_e2_r17_actor_pool_repair2_continuation_v1.py"
EXPECTED_V3_CONTRACT="312e970520794c564b23a9717f4c40d4baeb0674619da334c8fcc20ee95fc045"
EXPECTED_V3_AUTH="7aa826db915b40840fb54ca2c269a23c4f74807bae74fd99285eac6875ee5b74"
EXPECTED_PARENT_CONTRACT="9e38bdbfc71186e3e58587169d8c619bff4ae24de4145fefafa63e49a6f148a3"
EXPECTED_PARENT_AUTH="9643a0a30d0acc4f32607b217701b368a895b2fe1e86a0aa84da24aa0a80898b"

def process_matches()->list[str]:
 matches=[]
 for p in Path("/proc").iterdir():
  if not p.name.isdigit() or int(p.name)==os.getpid(): continue
  try: cmd=(p/"cmdline").read_bytes().replace(b"\0",b" ").decode(errors="replace")
  except (FileNotFoundError,PermissionError): continue
  if "run_e2_r17_deepseek_v2_repair2_continuation_v1.py" in cmd or "run_e2_r17_actor_pool_repair2_continuation_v1.py" in cmd:
   matches.append(f"{p.name}:{cmd}")
 return matches

def db_claims(path:Path)->int:
 with sqlite3.connect(path) as conn:
  return int(conn.execute("select count(*) from claims").fetchone()[0])

def main()->int:
 p=argparse.ArgumentParser(); p.add_argument("--contract",type=Path,required=True); p.add_argument("--authorization",type=Path,required=True)
 p.add_argument("--output",type=Path,required=True); args=p.parse_args()
 c,a=validate_contract_auth(args.contract,args.authorization); csha,asha=sha_file(args.contract),sha_file(args.authorization)
 inherit,remaining=validate_evidence(c)
 require(c["v3_parent"]["contract_sha256"]==EXPECTED_V3_CONTRACT and c["v3_parent"]["authorization_sha256"]==EXPECTED_V3_AUTH,"V3 lineage drift")
 require(c["repair2_stopped_parent"]["contract_sha256"]==EXPECTED_PARENT_CONTRACT and c["repair2_stopped_parent"]["authorization_sha256"]==EXPECTED_PARENT_AUTH,"original Repair2 lineage drift")
 for item in (c["v3_parent"]["contract"],c["v3_parent"]["authorization"],c["repair2_stopped_parent"]["contract_path"],c["repair2_stopped_parent"]["authorization_path"]):
  path=ROOT/item if not str(item).startswith("/") else Path(item)
  require(path.is_file(),"lineage artifact missing")
 require(sha_file(ROOT/c["v3_parent"]["contract"])==EXPECTED_V3_CONTRACT,"V3 contract SHA drift")
 require(sha_file(ROOT/c["v3_parent"]["authorization"])==EXPECTED_V3_AUTH,"V3 auth SHA drift")
 require(sha_file(ROOT/c["repair2_stopped_parent"]["contract_path"])==EXPECTED_PARENT_CONTRACT,"Repair2 contract SHA drift")
 require(sha_file(ROOT/c["repair2_stopped_parent"]["authorization_path"])==EXPECTED_PARENT_AUTH,"Repair2 auth SHA drift")
 require(not process_matches(),"continuation runner/actor already alive")
 require(not Path(c["run_root"]).exists(),"new continuation run root already exists")
 require(inherit["v3_provider_claims"]==609,"pre-continuation provider claim count drift")
 require(inherit["replay_provider"] is False and inherit["recompute_provider"] is False,"replay/recompute boundary drift")
 require(remaining["intersection"]==[] and remaining["union_equals_frozen_design"] is True,"set partition drift")
 require(len(remaining["completed_set"])==17 and len(remaining["remaining_set"])==31,"set cardinality drift")
 identity=ROOT/c["model_identity"]["path"]; require(identity.is_file() and sha_file(identity)==c["model_identity"]["sha256"],"identity drift")
 idp=load_json(identity); require(idp.get("status")=="PASS_CURRENT_REVIEW_TRANCHE","identity not qualified")
 row=idp["requested_and_resolved"][c["actor"]["requested_model"]]
 require(str(row["resolved"])==c["actor"]["resolved_model"],"resolved model drift")
 actor_python,actor_env=validate_actor_runtime({"runtime":c["actor_runtime"]}); actor_env["LITELLM_LOCAL_MODEL_COST_MAP"]="True"
 boundary=inherit["partial_boundary"]; heldout=c["heldout"]["task_ids"]; results=[]
 with tempfile.TemporaryDirectory(prefix="e2-r17-repair2-cont-v1-preflight-") as tmp:
  temp=Path(tmp)
  for arm in ("win_c","mrw"):
   x=boundary["arms"][arm]; done={str(r["task_id"]) for r in x["heldout_tasks"]}
   tasks=[task for task in heldout if task not in done]; require(len(tasks)==6,f"boundary remaining tasks drift: {arm}")
   binding=a["execution_scope"]["boundary_learned_states_by_arm"][arm]
   require(tasks==binding["remaining_task_ids"],f"authorized boundary task order drift: {arm}")
   total=int(binding["child_total_limit"]); require(total==191-int(x["parent_claim_count"]),f"residual budget drift: {arm}")
   for task in tasks:
    unit=temp/arm/task; ledger=unit/"provider_budget.sqlite3"; output=unit/"preflight.json"
    cmd=[str(actor_python),str(ACTOR),"--env-file",c["env_file"],"--suite-root",c["suite"]["root"],
     "--mindmemos-root",c["mindmemos"]["root"],"--run-root",str(unit/"actor"),"--identity",str(identity),
     "--authorization",str(args.authorization),"--skill-source",str(Path(x["skill_path"]).parent),
     "--updater-receipt",x["update_receipt_path"],"--mode","e1","--model",c["actor"]["requested_model"],
     "--task-id",task,"--k","1","--prefix-ks","1","--max-turns",str(c["actor"]["max_turns"]),
     "--max-output-tokens",str(c["actor"]["max_output_tokens"]),"--concurrency","1",
     "--provider-budget-ledger",str(ledger),"--provider-total-call-limit",str(total),
     "--provider-per-unit-call-limit","11","--stop-before-provider-io","--output",str(output)]
    run=subprocess.run(cmd,cwd=ROOT,env=actor_env,capture_output=True,text=True)
    require(run.returncode==0,f"actual actor preflight failed: {arm}/{task}: {run.stderr[-1000:]}")
    require(output.is_file(),"actor preflight output missing")
    payload=load_json(output); require(payload.get("status")=="STOPPED_IMMEDIATELY_BEFORE_PROVIDER_IO","actor did not stop before I/O")
    require(payload.get("provider_claims")==0 and payload.get("provider_calls")==0,"actor preflight made provider call")
    require(db_claims(ledger)==0,f"preflight ledger claimed provider: {arm}/{task}")
    results.append({"arm":arm,"task_id":task,"status":"PASS","provider_claims":0,"provider_calls":0})
 require(len(results)==12,"actual actor preflight cardinality drift")
 receipt={"schema_version":"1.0","artifact_type":"e2-r17-deepseek-v2-repair2-continuation-v1-preflight",
  "created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":"PREFLIGHT_PASS",
  "contract_sha256":csha,"authorization_sha256":asha,"original_v3_contract_sha256":EXPECTED_V3_CONTRACT,
  "original_v3_authorization_sha256":EXPECTED_V3_AUTH,"inherited_pairs":17,"immutable_learned_states":36,
  "immutable_heldout_units":636,"remaining_pairs":31,"remaining_new_learned_states":60,
  "remaining_heldout_units":1092,"first_continuation_unit":"e1-ioc-00/rep1",
  "completed_intersection_remaining":[],"union_equals_frozen_design":True,
  "actual_actor_authorization_path_preflight":{"passed":12,"expected":12,"results":results},
  "provider_claims_before_preflight":609,"preflight_provider_claims":0,"preflight_provider_calls":0,
  "completed_unit_replay":False,"partial_effect_read":False,"analyzer_run":False}
 atomic_json(args.output,receipt); print(json.dumps(receipt,indent=2,sort_keys=True)); return 0

if __name__=="__main__": raise SystemExit(main())
