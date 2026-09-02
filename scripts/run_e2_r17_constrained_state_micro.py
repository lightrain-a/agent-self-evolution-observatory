#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_provider_budget import ProviderBudgetLedger
from scripts.run_e2_r17_e1_a_pool_support import validate_runtime as validate_actor_runtime

ARMS = ("g0_base", "g1_verify", "g2_complete", "g3_complete_recover")
ORDER_SALT = "E2-R17-CONSTRAINED-STATE-MICRO-EVAL-ORDER-v1"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise RuntimeError(msg)


def atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def append(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush(); os.fsync(handle.fileno())


def rows(path: Path, key: str) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line); value = str(row[key]); require(value not in out, f"duplicate {key}: {value}"); out[value] = row
    return out


def ordered(task: str) -> list[str]:
    return sorted(ARMS, key=lambda arm: hashlib.sha256(f"{ORDER_SALT}|{task}|{arm}".encode()).hexdigest())


def validate(contract_path: Path, auth_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    c = load(contract_path); a = load(auth_path); csha = sha(contract_path)
    require(c.get("status") == "FROZEN_E2_R17_SINGLE_CASE_CONSTRAINED_STATE_MICRO", "contract drift")
    require(a.get("status") == "AUTHORIZED_E2_R17_SINGLE_CASE_CONSTRAINED_STATE_MICRO_MEASUREMENT", "authorization drift")
    require(a.get("contract_sha256") == csha, "authorization/contract mismatch")
    authority = a.get("authority") or {}
    require(authority.get("scientific_experiment") is True and authority.get("measurement_only") is True, "measurement authority absent")
    require(authority.get("updater") is False and authority.get("analyzer") is False, "authority overbroad")
    for label, item in c["bound_code"].items():
        path = ROOT / item["path"]; require(path.is_file() and sha(path) == item["sha256"], f"bound code drift: {label}")
    return c, a


def acquire_lease(path: Path, csha: str, asha: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schema_version":"1.0","artifact_type":"e2-r17-constrained-state-micro-lineage-lease","status":"RUNNING_CONSTRAINED_STATE_MICRO","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"pid":os.getpid(),"pgid":os.getpgrp(),"contract_sha256":csha,"authorization_sha256":asha,"exactly_once":True,"partial_effect_read":False}
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        os.write(fd, (json.dumps(payload, sort_keys=True)+"\n").encode()); os.fsync(fd)
    finally:
        os.close(fd)


def seal(path: Path, status: str) -> None:
    payload = load(path); payload["status"] = status; payload["sealed_at_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds"); atomic(path, payload)


def state_receipt(*, run_root: Path, state: dict[str, Any], csha: str, asha: str) -> Path | None:
    if state["arm"] == "g0_base":
        return None
    out = run_root / "state_receipts" / state["arm"] / "update_receipt.json"
    payload = {
        "schema_version":"1.0",
        "artifact_type":"e2-r17-deterministic-state-construction-receipt",
        "created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status":"COMPLETED",
        "arm":state["arm"],
        "construction":"initial_skill_plus_frozen_literal_append",
        "provider_calls":0,
        "updater_calls":0,
        "contract_sha256":csha,
        "authorization_sha256":asha,
        "skill_post_path":str((ROOT / state["skill_path"]).resolve()),
        "skill_post_sha256":state["skill_sha256"],
    }
    atomic(out, payload)
    return out


def verify_eval(row: dict[str, Any], state: dict[str, Any], receipt: Path | None) -> None:
    summary = Path(row["summary_path"]); ref = Path(row["trajectory_ref_path"])
    require(summary.is_file() and sha(summary)==row["summary_sha256"], "eval summary drift")
    require(ref.is_file() and sha(ref)==row["trajectory_ref_sha256"], "eval ref drift")
    payload = load(summary); require(payload.get("status")=="COMPLETED" and int(payload.get("k"))==1, "eval status/K drift")
    require(payload.get("skill_pre_sha256") == state["skill_sha256"], "eval skill binding drift")
    if receipt is None:
        require(payload.get("updater_receipt_sha256") in (None, ""), "G0 unexpectedly has updater receipt")
    else:
        require(payload.get("updater_receipt_sha256") == sha(receipt), "state receipt binding drift")
    ref_payload=load(ref); traj=Path(ref_payload["trajectory_path"]); require(traj.is_file() and sha(traj)==ref_payload["trajectory_sha256"], "trajectory drift")
    # Outcome embargo: never read score here.


def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--contract",type=Path,required=True); ap.add_argument("--authorization",type=Path,required=True); args=ap.parse_args()
    c,_=validate(args.contract,args.authorization); csha=sha(args.contract); asha=sha(args.authorization); run=Path(c["run_root"]); lease=Path(c["lineage_lease_path"])
    require(not run.exists(), "run root must be fresh"); require(not lease.exists(), "lineage lease exists"); acquire_lease(lease,csha,asha); success=False
    try:
        run.mkdir(parents=True)
        actor_python, actor_env = validate_actor_runtime({"runtime":c["actor_runtime"]}); actor_env["LITELLM_LOCAL_MODEL_COST_MAP"]="True"
        identity=ROOT/c["model_identity"]["path"]; require(identity.is_file() and sha(identity)==c["model_identity"]["sha256"], "identity drift")
        states={row["arm"]:row for row in c["states"]}; require(tuple(states)==ARMS, "state order drift")
        receipts={arm:state_receipt(run_root=run,state=states[arm],csha=csha,asha=asha) for arm in ARMS}
        for task in c["heldout_task_ids"]:
            for arm in ordered(task):
                state_root=run/"measurement"/arm; manifest=state_root/"completed_eval_tasks.jsonl"; existing=rows(manifest,"task_id")
                if task in existing:
                    verify_eval(existing[task],states[arm],receipts[arm]); continue
                eval_root=state_root/"evaluation"/task; require(not eval_root.exists(), f"partial ambiguous eval {arm}/{task}")
                ledger=state_root/"provider_budget.sqlite3"; summary=eval_root/"evaluation_summary.json"
                state=states[arm]; skill_path=Path(state["skill_path"]); skill_dir=skill_path.parent if arm=="g0_base" else (ROOT/skill_path).resolve().parent
                cmd=[str(actor_python),str(ROOT/"scripts/run_e2_r17_actor_pool_constrained_state_micro.py"),"--env-file",c["env_file"],"--suite-root",c["suite"]["root"],"--mindmemos-root",c["mindmemos"]["root"],"--run-root",str(eval_root),"--identity",str(identity),"--authorization",str(args.authorization.resolve()),"--skill-source",str(skill_dir),"--mode","e1","--model",c["actor"]["requested_model"],"--task-id",task,"--k","1","--prefix-ks","1","--max-turns",str(c["actor"]["max_turns"]),"--max-output-tokens",str(c["actor"]["max_output_tokens"]),"--concurrency","1","--provider-budget-ledger",str(ledger),"--provider-total-call-limit","191","--provider-per-unit-call-limit","11","--output",str(summary)]
                if receipts[arm] is not None:
                    cmd += ["--updater-receipt",str(receipts[arm])]
                result=subprocess.run(cmd,cwd=ROOT,env=actor_env,capture_output=True,text=True)
                if result.returncode!=0:
                    atomic(state_root/f"eval_failure_{task}.json",{"status":"TECHNICAL_FAILURE","arm":arm,"task_id":task,"returncode":result.returncode,"stdout_tail":result.stdout[-3000:],"stderr_tail":result.stderr[-3000:],"provider_relaunch_authorized":False}); raise RuntimeError(f"eval failed {arm}/{task}")
                ref=eval_root/"cases"/task/"rollout_0/r17_trajectory_ref.json"; require(summary.is_file() and ref.is_file(), "actor missing output")
                row={"task_id":task,"summary_path":str(summary),"summary_sha256":sha(summary),"trajectory_ref_path":str(ref),"trajectory_ref_sha256":sha(ref),"completed_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds")}; verify_eval(row,states[arm],receipts[arm]); append(manifest,row)
        out=[]
        for arm in ARMS:
            state_root=run/"measurement"/arm; manifest=state_root/"completed_eval_tasks.jsonl"; erows=rows(manifest,"task_id"); require(list(erows)==c["heldout_task_ids"],f"completion drift {arm}")
            ledger=ProviderBudgetLedger(path=state_root/"provider_budget.sqlite3",contract_sha256=csha,authorization_sha256=asha,total_limit=191,per_unit_limit=11,allow_create=False)
            out.append({"arm":arm,"skill_sha256":states[arm]["skill_sha256"],"state_receipt_sha256":sha(receipts[arm]) if receipts[arm] else None,"eval_manifest_path":str(manifest),"eval_manifest_sha256":sha(manifest),"completed_heldout_tasks":len(erows),"provider_budget":ledger.snapshot().to_dict()})
        summary={"schema_version":"1.0","artifact_type":"e2-r17-single-case-constrained-state-micro-summary","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":"COMPLETED_PENDING_SEPARATE_CONSTRAINED_STATE_ANALYSIS","contract_sha256":csha,"authorization_sha256":asha,"case_stream":"e1-tsr-00","arms":list(ARMS),"rows":out,"new_updater_calls":0,"deterministic_states":4,"heldout_rollout_units":72,"inference_performed":False,"partial_effect_read":False,"analyzer_run":False,"paper_promotion_authority":False}; atomic(run/"summary/constrained_state_micro_summary.json",summary); success=True; print(json.dumps(summary,ensure_ascii=False,indent=2,sort_keys=True)); return 0
    finally:
        if lease.exists(): seal(lease,"COMPLETED_CONSTRAINED_STATE_MICRO" if success else "FAIL_CLOSED_CONSTRAINED_STATE_MICRO")


if __name__=="__main__":
    raise SystemExit(main())
