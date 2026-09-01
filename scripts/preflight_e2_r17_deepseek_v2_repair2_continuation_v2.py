#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
import sys
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from research_pipeline.e2_r17_provider_budget import ProviderBudgetLedger
from scripts.run_e2_r17_deepseek_v2_repair2_continuation_v2 import validate_contract_auth,validate_v2_inheritance,sha_file,load_json,atomic_json,require
from scripts.run_e2_r17_e1_a_pool_support import validate_runtime as validate_actor_runtime
from scripts.run_e2_r17_v31_provider_runtime_pilot import validate_updater_runtime

def main()->int:
 p=argparse.ArgumentParser();p.add_argument("--contract",type=Path,required=True);p.add_argument("--authorization",type=Path,required=True);p.add_argument("--root",type=Path,required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
 c,auth=validate_contract_auth(a.contract,a.authorization);cs,aus=sha_file(a.contract),sha_file(a.authorization)
 require(not a.root.exists(),"V2 preflight root exists");require(not Path(c["run_root"]).exists(),"V2 run root exists");require(not Path(c["global_lineage_lease"]["path"]).exists(),"global lineage lease already exists")
 out=subprocess.check_output(["ps","-eo","args="],text=True)
 needles=("run_e2_r17_deepseek_v2_repair2_continuation_v2.py","run_e2_r17_actor_pool_repair2_continuation_v2.py")
 require(not [x for x in out.splitlines() if any(n in x for n in needles) and "preflight_e2_r17" not in x],"V2 actor/runner already alive")
 inherited=validate_v2_inheritance(c);require(len(inherited)==29,"V2 inheritance count")
 rem=load_json(ROOT/c["remaining_set_manifest"]["path"]);require(rem.get("status")=="PASS_CONTINUATION_V2_REMAINING_SET_19_PAIRS" and len(rem["remaining_units"])==19,"V2 remaining set")
 completed={x["unit_id"] for x in inherited};remaining=set(rem["remaining_units"]);expected={f"{s}/rep{r}" for s in c["streams"] for r in range(4)}
 require(not completed&remaining and completed|remaining==expected,"V2 partition proof")
 updater_py,_=validate_updater_runtime({"runtime":c["updater_runtime"],"mindmemos":c["mindmemos"]});require(updater_py.is_file(),"updater runtime")
 actor_py,env=validate_actor_runtime({"runtime":c["actor_runtime"]});env["LITELLM_LOCAL_MODEL_COST_MAP"]="True"
 a.root.mkdir(parents=True);rr=[]
 for task in c["heldout"]["task_ids"]:
  ur=a.root/task;led=ur/"provider_budget.sqlite3";receipt=ur/"pre-provider-stop.json"
  cmd=[str(actor_py),str(ROOT/c["bound_code"]["actor_runner_v2"]["path"]),"--env-file",c["env_file"],"--suite-root",c["suite"]["root"],"--mindmemos-root",c["mindmemos"]["root"],"--run-root",str(ur/"actor"),"--identity",str(ROOT/c["model_identity"]["path"]),"--authorization",str(a.authorization),"--mode","e1","--model",c["actor"]["requested_model"],"--task-id",task,"--k","1","--prefix-ks","1","--max-turns",str(c["actor"]["max_turns"]),"--max-output-tokens",str(c["actor"]["max_output_tokens"]),"--concurrency","1","--provider-budget-ledger",str(led),"--provider-total-call-limit","191","--provider-per-unit-call-limit","11","--stop-before-provider-io","--output",str(receipt)]
  z=subprocess.run(cmd,cwd=ROOT,env=env,text=True,capture_output=True)
  require(z.returncode==0,f"V2 actual actor-path preflight failed: {task}")
  x=load_json(receipt);require(x.get("status")=="STOPPED_IMMEDIATELY_BEFORE_PROVIDER_IO" and x.get("provider_claims")==0 and x.get("provider_calls")==0,f"V2 actor did not stop: {task}")
  snap=ProviderBudgetLedger(path=led,contract_sha256=cs,authorization_sha256=aus,total_limit=191,per_unit_limit=11,allow_create=False).snapshot();require(snap.total_claimed==0,f"V2 preflight claim: {task}")
  rr.append({"task_id":task,"status":x["status"],"provider_claims":0,"provider_calls":0,"receipt_path":str(receipt),"receipt_sha256":sha_file(receipt)})
 result={"schema_version":"1.0","artifact_type":"e2-r17-deepseek-v2-repair2-continuation-v2-preflight","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":"PASS_CONTINUATION_V2_COLLISION_PROOF_PREFLIGHT_18_OF_18","contract_sha256":cs,"authorization_sha256":aus,"inherited_pairs":29,"remaining_pairs":19,"new_learned_states":38,"new_heldout_units":684,"partition_intersection":0,"partition_union":48,"global_lineage_lease_absent_before_start":True,"run_root_absent":True,"actor_combinations":18,"provider_claims":0,"provider_calls":0,"partial_effect_read":False,"scientific_scores_read":False,"analyzer_run":False,"units":rr}
 atomic_json(a.output,result);print(json.dumps({k:result[k] for k in ("status","inherited_pairs","remaining_pairs","provider_calls","partial_effect_read")},indent=2,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
