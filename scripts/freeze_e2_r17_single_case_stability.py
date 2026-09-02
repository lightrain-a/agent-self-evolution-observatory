#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

def sha(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->dict[str,Any]: return json.loads(p.read_text(encoding="utf-8"))
def req(x:bool,m:str)->None:
    if not x: raise RuntimeError(m)
def atomic(p:Path,d:dict[str,Any])->None:
    p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+".tmp"); t.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8"); t.replace(p)

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--design",type=Path,required=True); ap.add_argument("--s1-contract",type=Path,required=True); ap.add_argument("--s1-authorization",type=Path,required=True); ap.add_argument("--s1-summary",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); a=ap.parse_args(); req(not a.output.exists(),"stability contract exists")
    d=load(a.design); c=load(a.s1_contract); auth=load(a.s1_authorization); s=load(a.s1_summary)
    req(d.get("status")=="DESIGN_ONLY_ZERO_AUTHORITY" and not any((d.get("authority") or {}).values()),"stability design not zero-authority")
    req(c.get("status")=="FROZEN_E2_R17_SINGLE_CASE_DIAGNOSTIC_WITNESS_S1" and auth.get("status")=="AUTHORIZED_E2_R17_SINGLE_CASE_DIAGNOSTIC_WITNESS_S1","S1 parent drift")
    req(s.get("status")=="COMPLETED_PENDING_SEPARATE_S1_ANALYSIS" and int(s.get("heldout_rollout_units",-1))==72,"S1 summary drift")
    s1csha=sha(a.s1_contract); s1asha=sha(a.s1_authorization); req(s.get("contract_sha256")==s1csha and s.get("authorization_sha256")==s1asha,"S1 summary parent binding drift")
    arms={row["arm"]:row for row in s["arms"]}; req({"win_c","first_fail"}.issubset(arms),"S1 states missing")
    states=[]
    for arm in ("win_c","first_fail"):
        row=arms[arm]; state=Path(row["state_root"]); skill=state/"update/skill_post/SKILL.md"; receipt=Path(row["update_receipt_path"])
        req(skill.is_file() and sha(skill)==row["skill_post_sha256"],f"state skill drift {arm}"); req(receipt.is_file() and sha(receipt)==row["update_receipt_sha256"],f"state receipt drift {arm}")
        ur=load(receipt); req(ur.get("contract_sha256")==s1csha and ur.get("authorization_sha256")==s1asha,"state parent authority drift")
        states.append({"arm":arm,"state_root":str(state),"skill_post_path":str(skill),"skill_post_sha256":sha(skill),"update_receipt_path":str(receipt),"update_receipt_sha256":sha(receipt)})
    code={
      "actor_wrapper":"scripts/run_e2_r17_actor_pool_single_case_stability.py",
      "compat_actor":"scripts/run_e2_r17_actor_pool_measurement_compat_v1.py",
      "runner":"scripts/run_e2_r17_single_case_stability.py",
      "provider_budget":"research_pipeline/e2_r17_provider_budget.py",
      "preflight":"scripts/preflight_e2_r17_single_case_stability.py",
      "authorizer":"scripts/authorize_e2_r17_single_case_stability.py",
    }
    bound={k:{"path":v,"sha256":sha(ROOT/v)} for k,v in code.items()}
    payload={"schema_version":"1.0","artifact_type":"e2-r17-single-case-first-fail-frozen-state-stability-contract","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":"FROZEN_E2_R17_SINGLE_CASE_FIRST_FAIL_STABILITY","scientific_object":d["scientific_object"],"case_stream":"e1-tsr-00","arms":["win_c","first_fail"],"measurement_replicates":[1,2],"heldout_task_ids":c["heldout_task_ids"],"scientific_scope":{"new_learned_states":0,"measurement_states":4,"heldout_units":72},"authority":{"scientific_experiment":False,"measurement_only":False,"provider_io":False,"updater":False,"heldout_evaluation":False,"analyzer":False,"second_backbone":False,"public_benchmark":False,"e3_confirmation":False,"paper_promotion":False,"submission":False},"design":{"path":str(a.design.relative_to(ROOT)),"sha256":sha(a.design)},"parent_s1":{"contract_path":str(a.s1_contract.relative_to(ROOT)),"contract_sha256":s1csha,"authorization_path":str(a.s1_authorization.relative_to(ROOT)),"authorization_sha256":s1asha,"run_summary_path":str(a.s1_summary),"run_summary_sha256":sha(a.s1_summary)},"learned_states":states,"suite":c["suite"],"mindmemos":c["mindmemos"],"model_identity":c["model_identity"],"actor_runtime":c["actor_runtime"],"actor":c["actor"],"env_file":c["env_file"],"budget":{"max_provider_calls_per_unit":11,"max_provider_calls_per_measurement_state":191},"bound_code":bound,"run_root":"/data/wyt/e2-r17-search-projection/runs/single-case-first-fail-stability-20260902","lineage_lease_path":"/data/wyt/e2-r17-search-projection/lineage-leases/e2-r17-single-case-first-fail-stability-v1.json","outcome_embargo":{"before_72_heldout":True,"partial_effect_read":False,"analyzer_authorized":False},"git_commit_at_freeze":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()}
    atomic(a.output,payload); print(json.dumps({"status":payload["status"],"sha256":sha(a.output),"learned_states":0,"measurement_states":4,"heldout":72},indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
