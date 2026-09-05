#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, importlib.util, json, os, subprocess, sys, tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
CONTRACT_STATUS="FROZEN_SEMANTIC_TRANSFER_V3_STAGE_A_R3_MATCHED_CENSOR_RECOVERY"
BURNED="r17-b21-cgwb-p0";CENSOR="r17-b21-cgwp-p0"

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->dict[str,Any]:return json.loads(p.read_text(encoding="utf-8"))
def req(c:bool,m:str)->None:
    if not c:raise RuntimeError(m)
def bound(raw:str)->Path:
    p=Path(raw);return p if p.is_absolute() else ROOT/p
def atomic(p:Path,x:dict[str,Any])->None:
    p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+".tmp");t.write_text(json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8");os.replace(t,p)
def imod(p:Path,name:str):
    s=importlib.util.spec_from_file_location(name,p);req(s is not None and s.loader is not None,f"cannot import {p}");m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument("--contract",type=Path,required=True);ap.add_argument("--output",type=Path,required=True);a=ap.parse_args();req(not a.output.exists(),"R3 preflight already exists")
    c=load(a.contract);csha=sha(a.contract);req(c["status"]==CONTRACT_STATUS,"R3 contract status invalid");req(c["authority"]["stage_a_provider_execution"] is False,"R3 draft contract self-authorizes")
    checks={}
    for label,row in c["bound_code"].items():
        p=ROOT/row["path"];req(p.is_file() and sha(p)==row["sha256"],f"R3 bound-code drift: {label}")
    for label,row in c["failed_r2_parent"]["immutable_files"].items():
        p=Path(row["path"]);req(p.is_file() and sha(p)==row["sha256"],f"R3 parent artifact drift: {label}")
    old=Path(c["failed_r2_parent"]["run_root"]);req(old.is_dir() and (old/".exclusive.lock").is_file(),"R2 fail-closed root/lock missing")
    req(not (old/"cases"/BURNED/"pool_k8.json").exists(),"burned task has complete R2 K8 pool");checks["parent_incident_binding_pass"]=True

    br=c["recovery_exceptions"]["burn_receipt"];bp=bound(br["path"]);req(bp.is_file() and sha(bp)==br["sha256"],"R3 burn receipt drift")
    cr=c["recovery_exceptions"]["matched_censor_receipt"];cp=bound(cr["path"]);req(cp.is_file() and sha(cp)==cr["sha256"],"R3 censor receipt drift")
    b,censor=load(bp),load(cp);req(b["task_id"]==BURNED and b["status"]=="TERMINAL_TECHNICAL_MISSING_POST_DISPATCH","burn receipt semantics drift");req(censor["task_id"]==CENSOR and censor["status"]=="PROSPECTIVE_MATCHED_EXPOSURE_CENSOR_NO_PROVIDER_EXECUTION","censor receipt semantics drift");req(censor["provider_calls_authorized"] is False and censor["support_eligible"] is False and censor["stage_b_update_eligible"] is False,"censor anti-use flags drift");checks["matched_censor_binding_pass"]=True

    ex=c["exact_once_acquisition"];mp=bound(ex["unit_manifest_path"]);req(mp.is_file() and sha(mp)==ex["unit_manifest_sha256"],"R3 provider manifest drift");tasks=[str(x) for x in load(mp)["ordered_task_ids"]];req(len(tasks)==len(set(tasks))==158 and BURNED not in tasks and CENSOR not in tasks,"R3 provider manifest shape drift");checks["provider_manifest_pass"]=True
    om=c["recovery_opportunity_manifest"];op=bound(om["path"]);req(op.is_file() and sha(op)==om["sha256"],"R3 opportunity manifest drift");o=load(op);streams=o["provider_task_ids_by_stream"];req(len(streams)==20,"R3 stream count drift");req(len(streams["stv3-cgwb-00"])==len(streams["stv3-cgwp-00"])==7,"R3 7/7 geometry drift");req(sum(len(v) for v in streams.values())==158,"R3 opportunity total drift");req(o["support_required_mixed_per_stream"]==4,"R3 support threshold drift");checks["opportunity_geometry_pass"]=True

    suite=Path(c["suite"]["root"]);split=suite/"r17_split_manifest.json";meta=suite/"r17_controlled_metadata.json";req(sha(split)==c["suite"]["split_manifest_sha256"] and sha(meta)==c["suite"]["metadata_sha256"],"R3 suite drift")
    m={r["id"]:r for r in load(meta)};req(m[BURNED]["pair_key"]==m[CENSOR]["pair_key"]==c["recovery_exceptions"]["pair_key"],"R3 pair-key drift");req(m[BURNED]["semantic_type"]=="INSTANCE_BINDING_LOCALIZATION" and m[CENSOR]["semantic_type"]=="PROCEDURAL_TRANSFORMATION","R3 semantic counterpart drift")
    init1=suite/"spreadsheetbench_verified_400/spreadsheet"/BURNED/f"{BURNED}_init.xlsx";init2=suite/"spreadsheetbench_verified_400/spreadsheet"/CENSOR/f"{CENSOR}_init.xlsx";req(sha(init1)==sha(init2)==c["recovery_exceptions"]["matched_initial_xlsx_sha256"],"R3 matched initial XLSX drift")

    req(not Path(c["run_root"]).exists() and not Path(c["global_lease_path"]).exists(),"R3 recovery lineage already exists")
    actor=imod(ROOT/c["bound_code"]["actor"]["path"],"e2_r17_r3_actor_preflight")
    synthetic={"status":"AUTHORIZED_SEMANTIC_TRANSFER_V3_STAGE_A_R3_RECOVERY","authority":{"stage_a_provider_execution":True,"stage_b_learning_execution":False,"updater":False,"heldout_evaluation":False,"analyzer":False,"second_backbone":False,"public_benchmark":False,"paper_promotion":False},"contract_sha256":csha,"execution_scope":{"recovery_mode":"MATCHED_CENSOR_158","allowed_modes":["e1"],"allowed_task_ids":tasks,"exact_k":8,"exact_prefix_ks":[1,2,4,8],"exact_concurrency":1,"required_run_root":c["run_root"],"runner_lease_required":True,"allow_noninitial_skill":False,"required_skill_pre_sha256":c["mindmemos"]["initial_skill_sha256"],"required_resolved_model":"deepseek-v4-pro-ga-260813","identity_artifact_sha256":"f"*64,"provider_budget":{"required":True,"total_limit":c["budget"]["max_provider_calls"],"per_unit_limit":10},"exact_once_acquisition":{"required":True,"unit_manifest_path":ex["unit_manifest_path"],"unit_manifest_sha256":ex["unit_manifest_sha256"],"unit_count":158,"required_claim_root":ex["claim_root"],"attempt_before_any_provider_io":True,"replay_allowed":False,"ambiguous_recollection_allowed":False},"global_lease_path":c["global_lease_path"],"recovery_exceptions":{"terminal_technical_missing":BURNED,"matched_no_provider_censor":CENSOR,"additional_attempted_but_unsealed_policy":"STOP"}}}
    sp=load(split)
    with tempfile.NamedTemporaryFile("w",suffix=".json",delete=False) as h:json.dump(synthetic,h);tmp=Path(h.name)
    try:
        actor.validate_authority(mode="e1",authorization=tmp,task_ids=tasks[:7],split=sp,k=8)
        actor.validate_exact_once_acquisition_scope(authorization_payload=synthetic,run_root=Path(c["run_root"]),requested_task_ids=tasks[:7])
        bad=False
        try:actor.validate_authority(mode="e1",authorization=tmp,task_ids=[BURNED],split=sp,k=8)
        except RuntimeError:bad=True
        req(bad,"R3 actor failed to reject burned task")
        bad=False
        try:actor.validate_authority(mode="e1",authorization=tmp,task_ids=[CENSOR],split=sp,k=8)
        except RuntimeError:bad=True
        req(bad,"R3 actor failed to reject matched censor")
        checks["actor_scope_guards_pass"]=True
    finally:tmp.unlink(missing_ok=True)

    py=Path(c["runtime"]["python_executable"]);req(py.is_file(),"R3 runtime python missing")
    for key,name in (("stage_a_runner","runner_compile_pass"),("equal_dose_adjudicator","adjudicator_compile_pass"),("authorization_minter","authorizer_compile_pass"),("actor","actor_compile_pass"),("stage_b_order_helper","stage_b_order_compile_pass")):
        p=ROOT/c["bound_code"][key]["path"];r=subprocess.run([str(py),"-m","py_compile",str(p)],capture_output=True,text=True);req(r.returncode==0,f"R3 compile failed: {key}");checks[name]=True
    order=imod(ROOT/c["bound_code"]["stage_b_order_helper"]["path"],"e2_r17_r3_order_preflight");req(len(order.update_pool_order("stv3-cgwb-00",0,[f"x{i}" for i in range(7)],expected_count=7))==7,"R3 7-pool order failed");req(len(order.update_pool_order("other",0,[f"x{i}" for i in range(8)],expected_count=8))==8,"R3 8-pool order failed");checks["stage_b_order_7_8_pass"]=True

    out={"schema_version":"1.0","artifact_type":"e2-r17-semantic-transfer-v3-stage-a-r3-recovery-zero-provider-preflight","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":"PASS_ZERO_PROVIDER_SEMANTIC_TRANSFER_V3_STAGE_A_R3_RECOVERY_PREFLIGHT","contract_path":str(a.contract),"contract_sha256":csha,"provider_calls":0,"scientific_execution":False,"support_inspected":False,"planned_task_count":160,"provider_execution_task_count":158,"terminal_technical_missing_count":1,"matched_no_provider_censor_count":1,"heldout_forbidden_count":20,"fresh_identity_qualified":False,"fresh_identity_required_after_exact_hash_review":True,"checks":checks,"authority":{"mint_recovery_authorization":False,"stage_a_provider_execution":False,"stage_b_learning_execution":False,"support_read":False},"next_gate":"FRESH_GPT56_SOL_EXTRA_HIGH_EXACT_HASH_R3_PREEXECUTION_REVIEW_THEN_FRESH_IDENTITY_THEN_SEPARATE_RECOVERY_AUTHORIZATION"}
    atomic(a.output,out);print(json.dumps({"status":out["status"],"contract_sha256":csha,"checks":checks,"next_gate":out["next_gate"]},indent=2,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
