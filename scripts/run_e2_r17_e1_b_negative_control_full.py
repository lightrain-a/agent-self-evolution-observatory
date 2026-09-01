#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.ark_provider import ArkSettings
from research_pipeline.config import load_env_file
from research_pipeline.e2_r17_actor_pool import load_frozen_pool
from research_pipeline.e2_r17_mindmemos_ark_adapter import MindMemOSArkPlanChatAdapter, PLAN_BASE_URL
from research_pipeline.e2_r17_mindmemos_updater import run_projection_update
from research_pipeline.e2_r17_provider_budget import ProviderBudgetLedger
from research_pipeline.e2_r17_search_projection_runner import ProjectionName, project_stream
from scripts.run_e2_r17_e1_a_pool_support import validate_runtime as validate_actor_runtime
from scripts.run_e2_r17_v31_provider_runtime_pilot import bind_mindmemos, evidence_units, validate_updater_runtime
from scripts.run_e2_r17_e1_b_transition_runtime_pilot import sha_file, load_json, atomic_json, require

ARMS = ("win_a", "win_b")
UPDATE_ORDER_SALT = "E2-R17-E1B-NC-UPDATE-ORDER-v1"
EVAL_ORDER_SALT = "E2-R17-E1B-NC-EVAL-PAIR-ORDER-v1"


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def rows_by(path: Path, key: str) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    out: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            out[str(row[key])] = row
    return out


def canonical_sha(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def ordered_arms(stream_id: str, salt: str, task_id: str = "") -> list[str]:
    return sorted(ARMS, key=lambda arm: hashlib.sha256(f"{salt}|{stream_id}|{task_id}|{arm}".encode()).hexdigest())


def acquire_lock(path: Path, contract_sha: str, auth_sha: str) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise RuntimeError(f"negative-control lock exists: {path}; inspect checkpoints before resume") from exc
    os.write(fd, (json.dumps({"pid": os.getpid(), "contract_sha256": contract_sha, "authorization_sha256": auth_sha}, sort_keys=True) + "\n").encode())
    os.fsync(fd)
    return fd


def validate_contract_auth(contract_path: Path, auth_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    contract = load_json(contract_path)
    auth = load_json(auth_path)
    require(contract.get("status") == "FROZEN_E1_B_NEGATIVE_CONTROL_FULL", "negative-control contract not frozen")
    require(auth.get("status") == "AUTHORIZED_E1", "negative-control authorization invalid")
    require(auth.get("contract_sha256") == sha_file(contract_path), "authorization/contract mismatch")
    authority = auth.get("authority") or {}
    require(authority.get("scientific_experiment") is True, "negative-control scientific authority absent")
    require(authority.get("e1_b") is True and authority.get("e1_b_negative_control") is True, "negative-control authority bit absent")
    require(authority.get("mrw_causal_comparison") is False, "negative-control must not authorize MRW")
    require(authority.get("paper_promotion") is False, "negative-control cannot promote paper")
    scope = auth.get("execution_scope") or {}
    require(scope.get("allowed_modes") == ["e1"], "mode scope drift")
    require(scope.get("allowed_task_ids") == contract["heldout"]["task_ids"], "heldout scope drift")
    require(int(scope.get("exact_k")) == 1 and scope.get("allow_noninitial_skill") is True, "K/noninitial scope drift")
    bscope = scope.get("provider_budget") or {}
    require(bscope.get("required") is True, "provider budget must be required")
    require(int(bscope.get("total_limit")) == int(contract["budget"]["max_provider_calls_per_state"]), "state total budget drift")
    require(int(bscope.get("per_unit_limit")) == int(contract["budget"]["max_provider_calls_per_unit"]), "state unit budget drift")
    return contract, auth


def load_stream_pools(contract: dict[str, Any], stream_id: str, split: dict[str, Any], support: dict[str, Any]) -> list[Any]:
    pools = []
    for task_id in map(str, split["e1_update_streams"][stream_id]):
        path = Path(contract["e1_a_pool_root"]) / "cases" / task_id / "pool_k8.json"
        require(path.is_file() and sha_file(path) == support["pool_sha256"][task_id], f"E1-A pool SHA drift: {task_id}")
        pool = load_frozen_pool(path)
        require(pool.task_id == task_id and pool.k == 8, f"invalid frozen pool: {task_id}")
        pools.append(pool)
    require(len(pools) == 8, f"stream {stream_id} must have eight pools")
    return pools


def verify_update(path: Path, contract_sha: str, auth_sha: str) -> dict[str, Any]:
    row = load_json(path)
    receipt = Path(row["update_receipt_path"]); skill = Path(row["skill_post_path"])
    require(receipt.is_file() and skill.is_file(), "completed update artifacts missing")
    require(sha_file(receipt) == row["update_receipt_sha256"] and sha_file(skill) == row["skill_post_sha256"], "completed update SHA drift")
    payload = load_json(receipt)
    require(payload.get("contract_sha256") == contract_sha and payload.get("authorization_sha256") == auth_sha, "update receipt binding drift")
    require(payload.get("causal_purity_mode") == "arm_blinded_selected_evidence" and payload.get("arm_metadata_visible_in_transcript") is False, "update causal-purity drift")
    return row


async def ensure_update(*, contract: dict[str, Any], contract_sha: str, auth_sha: str, stream_id: str, arm: str, pools: list[Any], win_units: list[Any], initial_skill: str, initial_sha: str, mind_head: str, requested: str, resolved: str, settings: ArkSettings, state_root: Path, ledger: ProviderBudgetLedger) -> dict[str, Any]:
    checkpoint = state_root / "checkpoints/update_completed.json"
    if checkpoint.exists():
        return verify_update(checkpoint, contract_sha, auth_sha)
    update_dir = state_root / "update"
    if update_dir.exists() and any(update_dir.rglob("*")):
        raise RuntimeError(f"partial ambiguous update exists: {stream_id}/{arm}; no auto-rerun")
    stream = project_stream(stream_id=stream_id, initial_skill_sha256=initial_sha, pools=pools, projection=ProjectionName.WINNER_ONLY)
    adapter = MindMemOSArkPlanChatAdapter(settings=settings, requested_model=requested, required_resolved_model=resolved, max_parse_attempts=int(contract["updater"]["max_parse_attempts"]), record_dir=update_dir / "provider_calls", provider_budget_ledger=ledger, provider_budget_unit_id=f"{stream_id}/{arm}/update")
    result = await run_projection_update(stream=stream, pools=pools, initial_skill_md=initial_skill, run_dir=update_dir, llm_adapter=adapter, mindmemos_commit=mind_head, contract_sha256=contract_sha, authorization_sha256=auth_sha, transcript_max_chars=int(contract["updater"]["transcript_max_chars"]), blinded_evidence_units=win_units)
    receipts = adapter.public_receipts()
    require(result.provider_calls == 10 and len(receipts) == 10, "WIN update must use exact nominal 10 calls")
    require(not any(r.get("parse_error") for r in receipts), "WIN update parse error")
    row = {"status":"COMPLETED","stream_id":stream_id,"arm":arm,"update_receipt_path":result.update_receipt_path,"update_receipt_sha256":result.update_receipt_sha256,"skill_post_path":result.skill_post_path,"skill_post_sha256":result.skill_post_sha256,"provider_calls":result.provider_calls,"provider_tokens":result.provider_total_tokens}
    atomic_json(checkpoint, row)
    return verify_update(checkpoint, contract_sha, auth_sha)

def verify_eval(row: dict[str, Any], state_root: Path, skill_sha: str, receipt_sha: str) -> None:
    summary_path = Path(row["summary_path"])
    require(summary_path.is_file() and sha_file(summary_path) == row["summary_sha256"], "eval summary SHA drift")
    summary = load_json(summary_path)
    require(summary.get("status") == "COMPLETED" and summary.get("k") == 1, "eval summary status/K drift")
    require(summary.get("skill_pre_sha256") == skill_sha and summary.get("updater_receipt_sha256") == receipt_sha, "eval learned-skill/receipt binding drift")
    require([str(x["task_id"]) for x in summary.get("tasks") or []] == [row["task_id"]], "eval task drift")
    ref = state_root / "evaluation" / row["task_id"] / "cases" / row["task_id"] / "rollout_0" / "r17_trajectory_ref.json"
    require(ref.is_file() and sha_file(ref) == row["trajectory_ref_sha256"], "eval trajectory-ref SHA drift")
    ref_payload = load_json(ref); trajectory = Path(ref_payload["trajectory_path"])
    require(trajectory.is_file() and sha_file(trajectory) == ref_payload["trajectory_sha256"], "eval trajectory SHA drift")


def ensure_eval(*, contract: dict[str, Any], auth_path: Path, identity_path: Path, actor_python: Path, actor_env: dict[str, str], stream_id: str, arm: str, task_id: str, state_root: Path, update: dict[str, Any], ledger_path: Path) -> dict[str, Any]:
    manifest = state_root / "checkpoints/completed_eval_tasks.jsonl"
    existing = rows_by(manifest, "task_id")
    if task_id in existing:
        verify_eval(existing[task_id], state_root, update["skill_post_sha256"], update["update_receipt_sha256"])
        return existing[task_id]
    eval_root = state_root / "evaluation" / task_id
    summary_path = eval_root / "evaluation_summary.json"
    if eval_root.exists() and any(eval_root.rglob("*")):
        raise RuntimeError(f"partial ambiguous evaluation exists: {stream_id}/{arm}/{task_id}; no auto-rerun")
    command = [str(actor_python), str(ROOT / "scripts/run_e2_r17_actor_pool.py"), "--env-file", contract["env_file"], "--suite-root", contract["suite"]["root"], "--mindmemos-root", contract["mindmemos"]["root"], "--run-root", str(eval_root), "--identity", str(identity_path), "--authorization", str(auth_path), "--skill-source", str(Path(update["skill_post_path"]).parent), "--updater-receipt", update["update_receipt_path"], "--mode", "e1", "--model", contract["actor"]["requested_model"], "--task-id", task_id, "--k", "1", "--prefix-ks", "1", "--max-turns", str(contract["actor"]["max_turns"]), "--max-output-tokens", str(contract["actor"]["max_output_tokens"]), "--concurrency", "1", "--provider-budget-ledger", str(ledger_path), "--provider-total-call-limit", str(contract["budget"]["max_provider_calls_per_state"]), "--provider-per-unit-call-limit", str(contract["budget"]["max_provider_calls_per_unit"]), "--output", str(summary_path)]
    result = subprocess.run(command, cwd=ROOT, env=actor_env, capture_output=True, text=True)
    if result.returncode != 0:
        atomic_json(state_root / "checkpoints" / f"eval_failure_{task_id}.json", {"status":"TECHNICAL_FAILURE","stream_id":stream_id,"arm":arm,"task_id":task_id,"returncode":result.returncode,"stdout_tail":result.stdout[-3000:],"stderr_tail":result.stderr[-3000:],"provider_relaunch_authorized":False})
        raise RuntimeError(f"heldout evaluation technical failure: {stream_id}/{arm}/{task_id}")
    require(summary_path.is_file(), "actor returned without eval summary")
    ref = eval_root / "cases" / task_id / "rollout_0" / "r17_trajectory_ref.json"
    require(ref.is_file(), "actor returned without trajectory ref")
    row = {"task_id":task_id,"summary_path":str(summary_path),"summary_sha256":sha_file(summary_path),"trajectory_ref_path":str(ref),"trajectory_ref_sha256":sha_file(ref),"completed_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds")}
    verify_eval(row, state_root, update["skill_post_sha256"], update["update_receipt_sha256"])
    append_jsonl(manifest, row)
    return row


async def main_async(args: argparse.Namespace) -> dict[str, Any]:
    contract, auth = validate_contract_auth(args.contract, args.authorization)
    contract_sha = sha_file(args.contract); auth_sha = sha_file(args.authorization)
    updater_python, _ = validate_updater_runtime({"runtime":contract["updater_runtime"],"mindmemos":contract["mindmemos"]})
    require(Path(sys.executable) == updater_python, "negative-control runner must use dedicated updater runtime")
    actor_python, actor_env = validate_actor_runtime({"runtime":contract["actor_runtime"]}); actor_env["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
    for label, item in contract["bound_code"].items():
        path = ROOT / item["path"]; require(path.is_file() and sha_file(path) == item["sha256"], f"bound code drift: {label}")
    suite_root = Path(contract["suite"]["root"]); split_path = suite_root / "r17_split_manifest.json"
    require(sha_file(suite_root / "suite_manifest.json") == contract["suite"]["suite_manifest_sha256"] and sha_file(split_path) == contract["suite"]["split_manifest_sha256"], "suite/split drift")
    split = load_json(split_path)
    require(list(split["e1_update_streams"].keys()) == contract["streams"], "stream manifest drift")
    require([str(x) for x in split["e1_common_heldout_probe"]] == contract["heldout"]["task_ids"], "heldout list drift")
    support_path = ROOT / contract["e1_a_support"]["path"]; require(support_path.is_file() and sha_file(support_path) == contract["e1_a_support"]["sha256"], "E1-A support artifact drift")
    support = load_json(support_path); require(support.get("status") == "PASS_E1_A_SUPPORT_READY_FOR_SEPARATE_E1_B_CONTRACT", "E1-A support no longer passing")
    mind_root = Path(contract["mindmemos"]["root"]); mind_head = subprocess.check_output(["git","-C",str(mind_root),"rev-parse","HEAD"],text=True).strip()
    require(mind_head == contract["mindmemos"]["commit"] and not subprocess.check_output(["git","-C",str(mind_root),"status","--short"],text=True).strip(), "MindMemOS drift/dirty")
    bind_mindmemos(mind_root)
    identity_path = ROOT / contract["model_identity"]["path"]; require(identity_path.is_file() and sha_file(identity_path) == contract["model_identity"]["sha256"], "identity artifact drift")
    identity = load_json(identity_path); require(identity.get("status") == "PASS_CURRENT_REVIEW_TRANCHE", "model identity not qualified")
    model_row = identity["requested_and_resolved"][contract["updater"]["requested_model"]]; requested=str(model_row["requested"]); resolved=str(model_row["resolved"])
    require(resolved == contract["updater"]["resolved_model"] == contract["actor"]["resolved_model"], "resolved-model drift")
    load_env_file(Path(contract["env_file"])); raw=ArkSettings.from_env(required=True); require(raw.base_url.rstrip("/") == PLAN_BASE_URL, "non-Ark-Plan route")
    settings=ArkSettings(api_key=raw.api_key,base_url=raw.base_url,default_model=raw.default_model,timeout_seconds=300.0,max_retries=0)
    initial_path=Path(contract["initial_skill"]["path"]); require(initial_path.is_file() and sha_file(initial_path)==contract["initial_skill"]["sha256"], "initial skill drift")
    initial_skill=initial_path.read_text(encoding="utf-8"); initial_sha=sha_file(initial_path)
    run_root=Path(contract["run_root"]); lock_path=run_root/".exclusive.lock"; lock_fd=acquire_lock(lock_path,contract_sha,auth_sha); success=False
    stream_manifest=run_root/"checkpoints/completed_streams.jsonl"; completed_streams=rows_by(stream_manifest,"stream_id")

    try:
        for row in completed_streams.values():
            path=Path(row["summary_path"]); require(path.is_file() and sha_file(path)==row["summary_sha256"], f"completed stream summary drift: {row['stream_id']}")
        for stream_id in contract["streams"]:
            if stream_id in completed_streams:
                continue
            pools=load_stream_pools(contract,stream_id,split,support)
            win_units,_,evidence_receipts=evidence_units(pools,final_block_cap_tokens=int(contract["renderer"]["final_block_cap_tokens"]),transcript_max_chars=int(contract["updater"]["transcript_max_chars"]))
            stream_root=run_root/"states"/stream_id; evidence_path=stream_root/"evidence_windows.json"; bundle_sha=canonical_sha([u.__dict__ for u in win_units])
            if evidence_path.exists():
                require(load_json(evidence_path).get("evidence_bundle_sha256")==bundle_sha, "frozen evidence-window drift")
            else:
                atomic_json(evidence_path,{"stream_id":stream_id,"evidence_bundle_sha256":bundle_sha,"receipts":evidence_receipts,"mrw_provider_execution_authorized":False})
            updates: dict[str,dict[str,Any]]={}
            for arm in ordered_arms(stream_id,UPDATE_ORDER_SALT):
                state_root=stream_root/arm; ledger_path=state_root/"checkpoints/provider_budget.sqlite3"
                ledger=ProviderBudgetLedger(path=ledger_path,contract_sha256=contract_sha,authorization_sha256=auth_sha,total_limit=int(contract["budget"]["max_provider_calls_per_state"]),per_unit_limit=int(contract["budget"]["max_provider_calls_per_unit"]),allow_create=not ledger_path.exists())
                updates[arm]=await ensure_update(contract=contract,contract_sha=contract_sha,auth_sha=auth_sha,stream_id=stream_id,arm=arm,pools=pools,win_units=win_units,initial_skill=initial_skill,initial_sha=initial_sha,mind_head=mind_head,requested=requested,resolved=resolved,settings=settings,state_root=state_root,ledger=ledger)
            for task_id in contract["heldout"]["task_ids"]:
                for arm in ordered_arms(stream_id,EVAL_ORDER_SALT,task_id):
                    state_root=stream_root/arm
                    ensure_eval(contract=contract,auth_path=args.authorization,identity_path=identity_path,actor_python=actor_python,actor_env=actor_env,stream_id=stream_id,arm=arm,task_id=task_id,state_root=state_root,update=updates[arm],ledger_path=state_root/"checkpoints/provider_budget.sqlite3")
            states=[]
            for arm in ARMS:
                state_root=stream_root/arm; eval_manifest=state_root/"checkpoints/completed_eval_tasks.jsonl"; eval_rows=rows_by(eval_manifest,"task_id")
                require(set(eval_rows)==set(contract["heldout"]["task_ids"]), f"heldout completion set invalid: {stream_id}/{arm}")
                for row in eval_rows.values(): verify_eval(row,state_root,updates[arm]["skill_post_sha256"],updates[arm]["update_receipt_sha256"])
                ledger=ProviderBudgetLedger(path=state_root/"checkpoints/provider_budget.sqlite3",contract_sha256=contract_sha,authorization_sha256=auth_sha,total_limit=int(contract["budget"]["max_provider_calls_per_state"]),per_unit_limit=int(contract["budget"]["max_provider_calls_per_unit"]),allow_create=False)
                states.append({"arm":arm,"update_receipt_sha256":updates[arm]["update_receipt_sha256"],"skill_post_sha256":updates[arm]["skill_post_sha256"],"completed_heldout_tasks":len(eval_rows),"eval_manifest_path":str(eval_manifest),"eval_manifest_sha256":sha_file(eval_manifest),"provider_budget":ledger.snapshot().to_dict()})
            stream_summary={"schema_version":"1.0","artifact_type":"e2-r17-e1-b-negative-control-stream","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":"COMPLETED","stream_id":stream_id,"pool_ids":[p.pool_id for p in pools],"evidence_windows_sha256":sha_file(evidence_path),"update_order":ordered_arms(stream_id,UPDATE_ORDER_SALT),"heldout_task_ids":contract["heldout"]["task_ids"],"states":states,"mrw_executed":False,"paper_promotion_authority":False}
            stream_summary_path=run_root/"summary/streams"/f"{stream_id}.json"; atomic_json(stream_summary_path,stream_summary)
            manifest_row={"stream_id":stream_id,"summary_path":str(stream_summary_path),"summary_sha256":sha_file(stream_summary_path),"completed_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds")}; append_jsonl(stream_manifest,manifest_row); completed_streams[stream_id]=manifest_row
        require(set(completed_streams)==set(contract["streams"]), "negative-control did not complete all streams")
        final={"schema_version":"1.0","artifact_type":"e2-r17-e1-b-negative-control-full-summary","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":"COMPLETED_PENDING_SEPARATE_NEGATIVE_CONTROL_ADJUDICATION","contract_sha256":contract_sha,"authorization_sha256":auth_sha,"streams":len(contract["streams"]),"arms":list(ARMS),"learned_states":len(contract["streams"])*2,"heldout_tasks_per_state":len(contract["heldout"]["task_ids"]),"heldout_rollout_units":len(contract["streams"])*2*len(contract["heldout"]["task_ids"]),"mrw_executed":False,"negative_control_inference_performed":False,"paper_promotion_authority":False,"completed_stream_manifest":str(stream_manifest),"completed_stream_manifest_sha256":sha_file(stream_manifest)}
        atomic_json(run_root/"summary/e1_b_negative_control_full_summary.json",final); success=True; return final
    finally:
        os.close(lock_fd)
        if success: lock_path.unlink(missing_ok=True)


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--contract",type=Path,required=True); parser.add_argument("--authorization",type=Path,required=True); args=parser.parse_args()
    payload=asyncio.run(main_async(args)); print(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)); return 0 if payload["status"]=="COMPLETED_PENDING_SEPARATE_NEGATIVE_CONTROL_ADJUDICATION" else 2


if __name__ == "__main__":
    raise SystemExit(main())
