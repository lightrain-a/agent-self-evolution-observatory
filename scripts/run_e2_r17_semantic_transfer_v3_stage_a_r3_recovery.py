#!/usr/bin/env python3
from __future__ import annotations

import argparse, json, os, socket, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_provider_budget import ProviderBudgetLedger
import scripts.run_e2_r17_e1_a_pool_support as legacy
import scripts.run_e2_r17_semantic_transfer_v3_stage_a as r2

ACTOR = ROOT / "scripts/run_e2_r17_semantic_transfer_v3_actor_pool_r3_recovery.py"
CONTRACT_STATUS = "FROZEN_SEMANTIC_TRANSFER_V3_STAGE_A_R3_MATCHED_CENSOR_RECOVERY"
AUTH_STATUS = "AUTHORIZED_SEMANTIC_TRANSFER_V3_STAGE_A_R3_RECOVERY"
BURNED = "r17-b21-cgwb-p0"
CENSOR = "r17-b21-cgwp-p0"
N_PROVIDER = 158

sha = r2.sha_file
load = r2.load_json
req = r2.require
atomic_json = r2.atomic_json
append_jsonl = r2.append_jsonl
exclusive = r2.acquire_exclusive_file
claim_paths = r2.task_claim_paths


def bound(raw: str) -> Path:
    p = Path(raw)
    return p if p.is_absolute() else ROOT / p


def geometry(contract: dict[str, Any]) -> tuple[dict[str, list[str]], list[str]]:
    item = contract["recovery_opportunity_manifest"]
    p = bound(item["path"])
    req(p.is_file() and sha(p) == item["sha256"], "R3 opportunity manifest drift")
    m = load(p)
    ids = [str(x) for x in m["ordered_stream_ids"]]
    streams = {str(k): [str(x) for x in v] for k, v in m["provider_task_ids_by_stream"].items()}
    req(list(streams) == ids and len(ids) == 20, "R3 stream universe drift")
    for sid, tasks in streams.items():
        n = 7 if sid in {"stv3-cgwb-00", "stv3-cgwp-00"} else 8
        req(len(tasks) == len(set(tasks)) == n, f"R3 opportunity drift: {sid}")
    tasks = [t for sid in ids for t in streams[sid]]
    req(len(tasks) == len(set(tasks)) == N_PROVIDER, "R3 provider universe must be 158 unique tasks")
    req(BURNED not in tasks and CENSOR not in tasks, "R3 excluded task leaked into provider universe")
    return streams, tasks


def verify_parent(contract: dict[str, Any]) -> None:
    p = contract["failed_r2_parent"]
    for label, row in p["immutable_files"].items():
        path = Path(row["path"])
        req(path.is_file() and sha(path) == row["sha256"], f"failed-R2 artifact drift: {label}")
    root = Path(p["run_root"])
    req(root.is_dir() and (root / ".exclusive.lock").is_file(), "failed-R2 lock/root not preserved")
    req(not (root / "cases" / BURNED / "pool_k8.json").exists(), "burned R2 task unexpectedly has K8 pool")
    a, s = claim_paths(root / "checkpoints/stage_a_task_claims", BURNED)
    req(a.is_file() and not s.exists(), "burned R2 exact-once state drift")
    ca, cs = claim_paths(root / "checkpoints/stage_a_task_claims", CENSOR)
    req(not ca.exists() and not cs.exists(), "matched censor had prior R2 attempt")


def verify_receipts(contract: dict[str, Any], run_root: Path, tasks: list[str], csha: str, asha: str) -> dict[str, Any]:
    x = contract["exact_once_acquisition"]
    req(int(x["unit_count"]) == N_PROVIDER and x["replay_allowed"] is False, "R3 exact-once policy drift")
    mp = bound(x["unit_manifest_path"])
    req(mp.is_file() and sha(mp) == x["unit_manifest_sha256"], "R3 exact-once manifest drift")
    req([str(v) for v in load(mp)["ordered_task_ids"]] == tasks, "R3 exact-once task order drift")
    cr = Path(x["claim_root"])
    req(cr.resolve() == (run_root / "checkpoints/stage_a_task_claims").resolve(), "R3 claim-root drift")
    req(len(list(cr.glob("*.attempt.json"))) == N_PROVIDER, "R3 attempt count drift")
    req(len(list(cr.glob("*.sealed.json"))) == N_PROVIDER, "R3 seal count drift")
    for task in tasks:
        ap, sp = claim_paths(cr, task)
        req(ap.is_file() and sp.is_file(), f"R3 exact-once receipt missing: {task}")
        a, s = load(ap), load(sp)
        req(a["task_id"] == s["task_id"] == task, f"R3 receipt task drift: {task}")
        req(a["contract_sha256"] == s["contract_sha256"] == csha, f"R3 receipt contract drift: {task}")
        req(a["authorization_sha256"] == s["authorization_sha256"] == asha, f"R3 receipt auth drift: {task}")
        pool = run_root / "cases" / task / "pool_k8.json"
        req(pool.is_file() and s["pool_k8_sha256"] == sha(pool), f"R3 pool seal drift: {task}")
    return {"planned_units":160,"provider_units":158,"attempted_units":158,"sealed_units":158,"terminal_technical_missing":1,"matched_no_provider_censor":1,"replay_allowed":False,"replacement_sampling_allowed":False}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", type=Path, required=True)
    ap.add_argument("--authorization", type=Path, required=True)
    ap.add_argument("--env-file", type=Path, required=True)
    args = ap.parse_args()

    contract, auth = load(args.contract), load(args.authorization)
    csha, asha = sha(args.contract), sha(args.authorization)
    req(contract["status"] == CONTRACT_STATUS and auth["status"] == AUTH_STATUS, "R3 contract/auth status invalid")
    req(auth["contract_sha256"] == csha, "R3 auth contract drift")
    req(auth["authority"]["stage_a_provider_execution"] is True, "R3 provider authority absent")
    for k in ("stage_b_learning_execution","updater","heldout_evaluation","analyzer","second_backbone","public_benchmark","paper_promotion"):
        req(auth["authority"][k] is False, f"R3 auth overbroad: {k}")
    for label, row in contract["bound_code"].items():
        p = ROOT / row["path"]
        req(p.is_file() and sha(p) == row["sha256"], f"R3 bound-code drift: {label}")
    verify_parent(contract)
    streams, tasks = geometry(contract)
    scope = auth["execution_scope"]
    req(scope["recovery_mode"] == "MATCHED_CENSOR_158" and [str(x) for x in scope["allowed_task_ids"]] == tasks, "R3 auth task scope drift")
    req(scope["recovery_exceptions"]["terminal_technical_missing"] == BURNED, "R3 burn scope drift")
    req(scope["recovery_exceptions"]["matched_no_provider_censor"] == CENSOR, "R3 censor scope drift")
    req(scope["recovery_exceptions"]["additional_attempted_but_unsealed_policy"] == "STOP", "R3 STOP invariant missing")

    suite = Path(contract["suite"]["root"])
    split = load(suite / "r17_split_manifest.json")
    heldout = [str(x) for x in split["e1_common_heldout_probe"]]
    req(set(heldout).isdisjoint(tasks), "R3 heldout overlap")
    env = Path(contract["env_file_path"]).resolve()
    req(args.env_file.resolve() == env and env.is_file(), "R3 env drift")
    fi = auth["fresh_model_identity"]
    identity = bound(fi["path"])
    req(identity.is_file() and sha(identity) == fi["sha256"], "R3 identity binding drift")
    ident = load(identity)
    req(ident["status"] == "PASS_CURRENT_REVIEW_TRANCHE", "R3 identity not passing")
    req(ident["requested_and_resolved"]["deepseek-v4-pro"]["resolved"] == "deepseek-v4-pro-ga-260813", "R3 resolved model drift")
    py, runtime_env = legacy.validate_runtime(contract)
    mind = Path(contract["mindmemos"]["root"])
    head = subprocess.run(["git","-C",str(mind),"rev-parse","HEAD"],check=True,capture_output=True,text=True).stdout.strip()
    req(head == contract["mindmemos"]["commit"], "R3 MindMemOS commit drift")

    run_root = Path(contract["run_root"]); lease = Path(contract["global_lease_path"])
    req(not run_root.exists() and not lease.exists(), "R3 recovery lineage already exists")
    lease_payload = {"schema_version":"1.0","artifact_type":"e2-r17-v3-stage-a-r3-recovery-lease","status":"RUNNING_STAGE_A_V3_R3_RECOVERY","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"pid":os.getpid(),"pgid":os.getpgrp(),"hostname":socket.gethostname(),"contract_sha256":csha,"authorization_sha256":asha,"run_root":str(run_root),"provider_execution_units":158,"partial_effect_read":False}
    fd = exclusive(lease, lease_payload); os.close(fd)
    lock_fd = None; success = False
    try:
        run_root.mkdir(parents=True, exist_ok=False)
        lock_fd = exclusive(run_root / ".exclusive.lock", {"contract_sha256":csha,"authorization_sha256":asha,"recovery_mode":"MATCHED_CENSOR_158","pid":os.getpid()})
        completed_path = run_root / "checkpoints/completed_streams.jsonl"
        budget_path = run_root / "checkpoints/provider_budget.sqlite3"
        budget = ProviderBudgetLedger(path=budget_path,contract_sha256=csha,authorization_sha256=asha,total_limit=int(contract["budget"]["max_provider_calls"]),per_unit_limit=int(contract["budget"]["provider_calls_per_rollout_limit"]),allow_create=True)
        completed = {}
        for sid, tids in streams.items():
            out = run_root / "summary/streams" / f"{sid}.json"
            cmd=[str(py),str(ACTOR),"--env-file",str(env),"--suite-root",str(suite),"--mindmemos-root",str(mind),"--run-root",str(run_root),"--identity",str(identity),"--authorization",str(args.authorization),"--mode","e1","--model","deepseek-v4-pro"]
            for tid in tids: cmd += ["--task-id",tid]
            cmd += ["--k","8","--prefix-ks","1,2,4,8","--max-turns",str(contract["actor"]["max_turns"]),"--max-output-tokens",str(contract["actor"]["max_output_tokens"]),"--concurrency",str(contract["actor"]["concurrency"]),"--provider-budget-ledger",str(budget_path),"--provider-total-call-limit",str(contract["budget"]["max_provider_calls"]),"--provider-per-unit-call-limit",str(contract["budget"]["provider_calls_per_rollout_limit"]),"--output",str(out)]
            res=subprocess.run(cmd,cwd=ROOT,env=runtime_env,capture_output=True,text=True)
            if res.returncode:
                cr=Path(contract["exact_once_acquisition"]["claim_root"]); na=len(list(cr.glob("*.attempt.json"))) if cr.exists() else 0; ns=len(list(cr.glob("*.sealed.json"))) if cr.exists() else 0
                atomic_json(run_root / "checkpoints/failures" / f"{sid}.json", {"status":"FAIL_CLOSED_R3_RECOVERY","stream_id":sid,"returncode":res.returncode,"stdout_tail":res.stdout[-3000:],"stderr_tail":res.stderr[-3000:],"attempt_markers":na,"sealed_receipts":ns,"additional_attempted_but_unsealed_policy":"STOP","resume_authority":False,"support_read_authority":False,"stage_b_authority":False})
                raise RuntimeError(f"R3 recovery stream failed closed: {sid}")
            req(out.is_file(), f"R3 actor output missing: {sid}")
            row={"stream_id":sid,"summary_path":str(out),"summary_sha256":sha(out),"task_ids":tids,"task_count":len(tids)}
            append_jsonl(completed_path,row); completed[sid]=row

        total_rollouts=0; total_receipts=0
        for sid,tids in streams.items():
            row=completed[sid]; legacy.verify_stream_receipt(row,run_root,budget)
            s=load(Path(row["summary_path"])); rows=s.get("tasks") or []
            req([str(x["task_id"]) for x in rows] == tids, f"R3 stream task drift: {sid}")
            req(s["resolved_model"] == "deepseek-v4-pro-ga-260813", f"R3 stream model drift: {sid}")
            total_rollouts += 8*len(rows); total_receipts += sum(int(x.get("provider_calls") or 0) for x in rows)
        req(total_rollouts == 1264, "R3 rollout total drift")
        snap=budget.snapshot(); req(snap.total_claimed <= int(contract["budget"]["max_provider_calls"]), "R3 provider budget exceeded")
        exact=verify_receipts(contract,run_root,tasks,csha,asha)
        req(not (run_root/"cases"/BURNED).exists() and not (run_root/"cases"/CENSOR).exists(), "R3 excluded case created")
        req(not [x for x in heldout if (run_root/"cases"/x).exists()], "R3 heldout touched")
        summary=run_root/"summary/stage_a_r3_recovery_pool_freeze_summary.json"
        final={"schema_version":"1.0","artifact_type":"e2-r17-v3-stage-a-r3-recovery-pool-freeze-summary","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":"COMPLETED_158_POOLS_PLUS_TWO_FROZEN_EXCEPTIONS_PENDING_R3_EQUAL_DOSE_ADJUDICATION","contract_sha256":csha,"authorization_sha256":asha,"planned_tasks":160,"provider_executable_tasks":158,"sealed_k8_pools":158,"terminal_technical_missing":1,"matched_no_provider_censor":1,"actor_rollouts":total_rollouts,"provider_receipts":total_receipts,"provider_budget":snap.to_dict(),"exact_once_acquisition":exact,"updater_calls":0,"heldout_evaluations":0,"partial_effect_read":False,"scientific_scores_read":False,"support_inspected":False,"stage_b_authority":False,"completed_stream_manifest_path":str(completed_path),"completed_stream_manifest_sha256":sha(completed_path)}
        atomic_json(summary,final)
        atomic_json(lease,{**lease_payload,"status":"COMPLETED_STAGE_A_V3_R3_RECOVERY_PENDING_EQUAL_DOSE_ADJUDICATION","sealed_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"summary_path":str(summary),"summary_sha256":sha(summary)})
        success=True; print(json.dumps(final,ensure_ascii=False,indent=2,sort_keys=True)); return 0
    finally:
        if lock_fd is not None: os.close(lock_fd)
        if success: (run_root/".exclusive.lock").unlink(missing_ok=True)
        # Failure preserves the R3 lease and lock. No automatic recovery from recovery.

if __name__ == "__main__":
    raise SystemExit(main())
