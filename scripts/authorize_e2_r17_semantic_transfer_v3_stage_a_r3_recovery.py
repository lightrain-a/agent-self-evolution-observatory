#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
CONTRACT_STATUS="FROZEN_SEMANTIC_TRANSFER_V3_STAGE_A_R3_MATCHED_CENSOR_RECOVERY"
PREFLIGHT_STATUS="PASS_ZERO_PROVIDER_SEMANTIC_TRANSFER_V3_STAGE_A_R3_RECOVERY_PREFLIGHT"
REVIEW_VERDICT="PASS_TO_SEPARATE_R3_RECOVERY_AUTHORIZATION"
BURNED="r17-b21-cgwb-p0"; CENSOR="r17-b21-cgwp-p0"

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->dict[str,Any]:return json.loads(p.read_text(encoding="utf-8"))
def req(c:bool,m:str)->None:
    if not c:raise RuntimeError(m)
def bound(raw:str)->Path:
    p=Path(raw);return p if p.is_absolute() else ROOT/p
def atomic(p:Path,x:dict[str,Any])->None:
    p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+".tmp");t.write_text(json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8");os.replace(t,p)

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument("--contract",type=Path,required=True);ap.add_argument("--preflight",type=Path,required=True);ap.add_argument("--review",type=Path,required=True);ap.add_argument("--fresh-identity",type=Path,required=True);ap.add_argument("--output",type=Path,required=True);a=ap.parse_args()
    req(not a.output.exists(),"R3 recovery authorization already exists")
    c,p,r,i=load(a.contract),load(a.preflight),load(a.review),load(a.fresh_identity);csha=sha(a.contract)
    req(c["status"]==CONTRACT_STATUS,"R3 recovery contract not frozen")
    req(p["status"]==PREFLIGHT_STATUS and p["contract_sha256"]==csha,"R3 preflight not passing/bound")
    req(p["provider_calls"]==0 and p["scientific_execution"] is False and p["support_inspected"] is False,"R3 preflight crossed science boundary")
    req(p["provider_execution_task_count"]==158 and p["planned_task_count"]==160,"R3 preflight geometry drift")
    for key in ("parent_incident_binding_pass","matched_censor_binding_pass","provider_manifest_pass","opportunity_geometry_pass","actor_scope_guards_pass","runner_compile_pass","adjudicator_compile_pass","stage_b_order_7_8_pass"):
        req(p["checks"].get(key) is True,f"R3 preflight check missing: {key}")
    req(r["status"]=="COMPLETED" and r["surface"]=="ChatGPT web" and r["model"]=="GPT-5.6 Sol","R3 independent review provenance drift")
    req(r["verdict"]==REVIEW_VERDICT and r["execution_recommendation"]=="ALLOW_SEPARATE_R3_RECOVERY_AUTHORIZATION","R3 independent review not executable PASS")
    req(r["contract_sha256_acknowledged"]==csha and r["remaining_blockers"]==[],"R3 independent review contract/blocker drift")
    req(r["stage_b_authority"] is False and r["scientific_authority"] is False,"R3 review authority overbroad")
    ct=datetime.fromisoformat(c["created_at_utc"]);rt=datetime.fromisoformat(r["created_at_utc"])
    req(rt>ct,"R3 independent review must follow contract freeze")
    req(i["status"]=="PASS_CURRENT_REVIEW_TRANCHE","fresh R3 identity not passing")
    row=i["requested_and_resolved"]["deepseek-v4-pro"]
    req(row["resolved"]=="deepseek-v4-pro-ga-260813" and row["thinking"]=="disabled" and int(row["provider_retry_limit"])==0,"fresh R3 identity drift")
    it=datetime.fromisoformat(i["created_at_utc"]);req(it>rt,"fresh R3 identity must be qualified after exact-hash preexecution review")

    ex=c["exact_once_acquisition"];mp=bound(ex["unit_manifest_path"]);req(mp.is_file() and sha(mp)==ex["unit_manifest_sha256"],"R3 provider manifest drift")
    tasks=[str(x) for x in load(mp)["ordered_task_ids"]];req(len(tasks)==len(set(tasks))==158,"R3 provider universe must be 158 unique tasks")
    req(BURNED not in tasks and CENSOR not in tasks,"excluded task leaked into R3 provider universe")
    om=c["recovery_opportunity_manifest"];op=bound(om["path"]);req(op.is_file() and sha(op)==om["sha256"],"R3 opportunity manifest drift")
    opp=load(op);req(len(opp["provider_task_ids_by_stream"]["stv3-cgwb-00"])==7 and len(opp["provider_task_ids_by_stream"]["stv3-cgwp-00"])==7,"R3 matched opportunity geometry drift")
    req(not Path(c["run_root"]).exists() and not Path(c["global_lease_path"]).exists(),"R3 recovery lineage already exists")

    authority={"stage_a_provider_execution":True,"stage_b_learning_execution":False,"updater":False,"heldout_evaluation":False,"analyzer":False,"second_backbone":False,"public_benchmark":False,"paper_promotion":False,"submission":False}
    payload={
      "schema_version":"1.0","artifact_type":"e2-r17-semantic-transfer-v3-stage-a-r3-recovery-authorization","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":"AUTHORIZED_SEMANTIC_TRANSFER_V3_STAGE_A_R3_RECOVERY",
      "contract_path":str(a.contract),"contract_sha256":csha,"preflight_path":str(a.preflight),"preflight_sha256":sha(a.preflight),
      "independent_review":{"path":str(a.review),"sha256":sha(a.review),"surface":r["surface"],"model":r["model"],"thinking_level":r["thinking_level"],"verdict":r["verdict"]},
      "fresh_model_identity":{"path":str(a.fresh_identity),"sha256":sha(a.fresh_identity),"status":i["status"],"created_at_utc":i["created_at_utc"],"requested_model":"deepseek-v4-pro","resolved_model":row["resolved"]},
      "single_use":True,"exactly_once":True,"automatic_retry":False,"authority":authority,
      "execution_scope":{"recovery_mode":"MATCHED_CENSOR_158","allowed_modes":["e1"],"allowed_task_ids":tasks,"exact_k":8,"exact_prefix_ks":[1,2,4,8],"exact_concurrency":c["actor"]["concurrency"],"required_run_root":c["run_root"],"runner_lease_required":True,"allow_noninitial_skill":False,"required_skill_pre_sha256":c["mindmemos"]["initial_skill_sha256"],"required_resolved_model":"deepseek-v4-pro-ga-260813","identity_artifact_sha256":sha(a.fresh_identity),"suite_manifest_sha256":c["suite"]["suite_manifest_sha256"],"split_manifest_sha256":c["suite"]["split_manifest_sha256"],"max_turns":c["actor"]["max_turns"],"max_output_tokens":c["actor"]["max_output_tokens"],"provider_budget":{"required":True,"total_limit":c["budget"]["max_provider_calls"],"per_unit_limit":c["budget"]["provider_calls_per_rollout_limit"]},"exact_once_acquisition":{"required":True,"unit_manifest_path":ex["unit_manifest_path"],"unit_manifest_sha256":ex["unit_manifest_sha256"],"unit_count":158,"required_claim_root":ex["claim_root"],"attempt_before_any_provider_io":True,"replay_allowed":False,"ambiguous_recollection_allowed":False},"global_lease_path":c["global_lease_path"],"recovery_exceptions":{"terminal_technical_missing":BURNED,"matched_no_provider_censor":CENSOR,"matched_censor_provider_calls":0,"replacement_allowed":False,"additional_attempted_but_unsealed_policy":"STOP"}},
      "interpretation_boundary":"Single-use authority for the 158-task R3 Stage-A matched-censor recovery only. No support read, updater, heldout, Stage B, public benchmark, or paper claim is authorized. Any additional attempted-but-unsealed recovery unit causes STOP."
    }
    atomic(a.output,payload);print(json.dumps({"status":payload["status"],"contract_sha256":csha,"allowed_tasks":158,"authority":authority},ensure_ascii=False,indent=2,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
