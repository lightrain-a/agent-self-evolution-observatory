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
from research_pipeline.e2_r17_repair2_manifest import (
    validate_compatibility_manifest,
    validate_quarantine,
    validate_valid_rows,
)
from research_pipeline.e2_r17_search_projection_runner import ProjectionName, project_stream
from scripts.run_e2_r17_e1_a_pool_support import validate_runtime as validate_actor_runtime
from scripts.run_e2_r17_v31_provider_runtime_pilot import bind_mindmemos, evidence_units, validate_updater_runtime
from scripts.run_e2_r17_e1_b_transition_runtime_pilot import sha_file, load_json, atomic_json, require

ARMS = ("win_c", "mrw")
REPLICATES = (0, 1, 2, 3)
UPDATE_ORDER_SALT = "E2-R17-DEEPSEEK-V2-UPDATE-ORDER-v1"
EVAL_ORDER_SALT = "E2-R17-DEEPSEEK-V2-EVAL-PAIR-ORDER-v1"


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


def ordered_arms(stream_id: str, replicate: int, salt: str, task_id: str = "") -> list[str]:
    return sorted(ARMS, key=lambda arm: hashlib.sha256(f"{salt}|{stream_id}|rep{replicate}|{task_id}|{arm}".encode()).hexdigest())


def acquire_lock(path: Path, contract_sha: str, auth_sha: str) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise RuntimeError(f"MRW causal-tranche lock exists: {path}; inspect checkpoints before resume") from exc
    os.write(fd, (json.dumps({"pid": os.getpid(), "contract_sha256": contract_sha, "authorization_sha256": auth_sha}, sort_keys=True) + "\n").encode())
    os.fsync(fd)
    return fd


def validate_contract_auth(contract_path: Path, auth_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    contract = load_json(contract_path)
    auth = load_json(auth_path)
    require(contract.get("status") == "FROZEN_E2_R17_DEEPSEEK_V2_REPAIR2_CONTINUATION", "DeepSeek V2 Repair2 contract not frozen")
    require(auth.get("status") == "AUTHORIZED_E2_R17_DEEPSEEK_V2_REPAIR2", "Repair2 authorization invalid")
    require(auth.get("contract_sha256") == sha_file(contract_path), "authorization/contract mismatch")
    authority = auth.get("authority") or {}
    require(authority.get("scientific_experiment") is True, "MRW causal scientific authority absent")
    require(authority.get("deepseek_v2") is True, "DeepSeek V2 authority bit absent")
    require(authority.get("repair2_continuation") is True, "Repair2 continuation authority absent")
    require(authority.get("gpt_scientific_execution") is False and authority.get("kimi_scientific_execution") is False and authority.get("qwen_scientific_execution") is False, "second scientific backbone forbidden")
    require(authority.get("public_benchmark") is False, "public benchmark forbidden")
    require(authority.get("mrw_causal_comparison") is True, "DeepSeek V2 MRW comparison authority absent")
    require(authority.get("paper_promotion") is False, "MRW causal tranche cannot promote paper")
    scope = auth.get("execution_scope") or {}
    require(scope.get("allowed_modes") == ["e1"], "mode scope drift")
    require(scope.get("allowed_task_ids") == contract["heldout"]["task_ids"], "heldout scope drift")
    require(int(scope.get("exact_k")) == 1 and scope.get("allow_noninitial_skill") is True, "K/noninitial scope drift")
    require(int(scope.get("replicates_per_stream")) == len(REPLICATES), "replicate-count authorization drift")
    bscope = scope.get("provider_budget") or {}
    require(bscope.get("required") is True, "provider budget must be required")
    require(int(bscope.get("total_limit")) == int(contract["budget"]["max_provider_calls_per_state"]), "state total budget drift")
    require(int(bscope.get("per_unit_limit")) == int(contract["budget"]["max_provider_calls_per_unit"]), "state unit budget drift")
    require(int(contract["updater"]["max_parse_attempts"]) == 2, "Repair2 must allow exactly one explicit correction attempt")
    require(int(contract["budget"]["max_provider_calls_per_unit"]) == 11, "Repair2 updater unit limit must be 11")
    require(int(contract["budget"]["max_provider_calls_per_state"]) == 191, "Repair2 state limit must be 191")
    require(int(contract["actor"]["max_turns"]) == 10, "actor max_turns must remain 10")
    prior = contract["v1_identifiability_hold"]
    prior_path = ROOT / prior["path"]
    require(prior_path.is_file() and sha_file(prior_path) == prior["sha256"], "V1 identifiability artifact drift")
    prior_payload = load_json(prior_path)
    require(prior_payload.get("status") == "HOLD_UPDATER_OR_EVALUATOR_STOCHASTICITY", "V1 HOLD provenance drift")
    correction = contract["protocol_v2_correction"]
    correction_path = ROOT / correction["path"]
    require(correction_path.is_file() and sha_file(correction_path) == correction["sha256"], "V2 correction memo drift")
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


async def ensure_update(*, contract: dict[str, Any], contract_sha: str, auth_sha: str, base_stream_id: str, execution_stream_id: str, replicate: int, arm: str, pools: list[Any], evidence_units_for_arm: list[Any], projection: ProjectionName, initial_skill: str, initial_sha: str, mind_head: str, requested: str, resolved: str, settings: ArkSettings, state_root: Path, ledger: ProviderBudgetLedger) -> dict[str, Any]:
    checkpoint = state_root / "checkpoints/update_completed.json"
    if checkpoint.exists():
        return verify_update(checkpoint, contract_sha, auth_sha)
    update_dir = state_root / "update"
    if update_dir.exists() and any(update_dir.rglob("*")):
        raise RuntimeError(f"partial ambiguous update exists: {base_stream_id}/rep{replicate}/{arm}; no auto-rerun")
    stream = project_stream(stream_id=execution_stream_id, initial_skill_sha256=initial_sha, pools=pools, projection=projection)
    adapter = MindMemOSArkPlanChatAdapter(settings=settings, requested_model=requested, required_resolved_model=resolved, max_parse_attempts=int(contract["updater"]["max_parse_attempts"]), record_dir=update_dir / "provider_calls", provider_budget_ledger=ledger, provider_budget_unit_id=f"{base_stream_id}/rep{replicate}/{arm}/update")
    result = await run_projection_update(stream=stream, pools=pools, initial_skill_md=initial_skill, run_dir=update_dir, llm_adapter=adapter, mindmemos_commit=mind_head, contract_sha256=contract_sha, authorization_sha256=auth_sha, transcript_max_chars=int(contract["updater"]["transcript_max_chars"]), blinded_evidence_units=evidence_units_for_arm)
    receipts = adapter.public_receipts()
    require(result.provider_calls == len(receipts) and result.provider_calls in (10, 11), "Repair2 update must use 10 nominal calls or one explicit 11th correction call")
    parse_errors = [r for r in receipts if r.get("parse_error")]
    correction_used = result.provider_calls == 11
    if correction_used:
        require(len(parse_errors) == 1, "Repair2 correction path must contain exactly one parse error")
        require(parse_errors[0].get("task") == "skill_patch_apply" and int(parse_errors[0].get("attempt")) == 0, "Repair2 correction must follow patch-apply attempt0 failure")
        require(receipts[-1].get("task") == "skill_patch_apply" and int(receipts[-1].get("attempt")) == 1 and not receipts[-1].get("parse_error"), "Repair2 correction attempt1 must succeed")
    else:
        require(not parse_errors and all(int(r.get("attempt")) == 0 for r in receipts), "nominal Repair2 path must be attempt0-only")
    require(all(r.get("provider_status") == "completed" and r.get("hidden_provider_retry_used") is False for r in receipts), "Repair2 provider completion/retry drift")
    row = {"status":"COMPLETED","stream_id":base_stream_id,"execution_stream_id":execution_stream_id,"replicate":replicate,"arm":arm,"update_receipt_path":result.update_receipt_path,"update_receipt_sha256":result.update_receipt_sha256,"skill_post_path":result.skill_post_path,"skill_post_sha256":result.skill_post_sha256,"provider_calls":result.provider_calls,"provider_tokens":result.provider_total_tokens,"attempt0_success":not correction_used,"correction_required":correction_used,"correction_success":correction_used,"correction_failure":False}
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
    require(Path(sys.executable) == updater_python, "MRW causal runner must use dedicated updater runtime")
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
    repair1 = contract["repair1_parent"]
    compatibility_item = contract["compatibility_manifest"]
    quarantine_item = contract["technical_quarantine"]
    compatibility_path = ROOT / compatibility_item["path"]
    quarantine_path = ROOT / quarantine_item["path"]
    inherited_rows = validate_compatibility_manifest(
        path=compatibility_path,
        expected_sha=compatibility_item["sha256"],
        repair1_contract_sha=repair1["contract_sha256"],
        repair1_authorization_sha=repair1["authorization_sha256"],
        heldout_task_ids=contract["heldout"]["task_ids"],
    )
    quarantine = validate_quarantine(quarantine_path, quarantine_item["sha256"])
    run_root=Path(contract["run_root"]); lock_path=run_root/".exclusive.lock"; lock_fd=acquire_lock(lock_path,contract_sha,auth_sha); success=False
    unit_manifest=run_root/"checkpoints/completed_replicates.jsonl"
    valid_manifest=Path(contract["valid_replicate_manifest"]["path"])
    completed_units=rows_by(unit_manifest,"unit_id")
    valid_units=rows_by(valid_manifest,"unit_id")
    if not completed_units and not valid_units:
        for inherited in inherited_rows:
            append_jsonl(valid_manifest, inherited)
            valid_units[inherited["unit_id"]] = inherited
            completed = {"unit_id":inherited["unit_id"],"stream_id":inherited["stream_id"],"replicate":inherited["replicate_id"],"summary_path":inherited["pair_summary_path"],"summary_sha256":inherited["pair_summary_sha256"],"source":"repair1_inherited","completed_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds")}
            append_jsonl(unit_manifest, completed)
            completed_units[completed["unit_id"]] = completed
    require({row["unit_id"] for row in inherited_rows} == {unit_id for unit_id,row in valid_units.items() if row.get("source") == "repair1_inherited"}, "runtime inherited set differs from frozen compatibility manifest")
    validate_valid_rows(list(valid_units.values()), streams=contract["streams"], quarantine=quarantine, require_complete=False)

    try:
        for row in completed_units.values():
            path=Path(row["summary_path"]); require(path.is_file() and sha_file(path)==row["summary_sha256"], f"completed replicate summary drift: {row['unit_id']}")
        for stream_id in contract["streams"]:
            pools=load_stream_pools(contract,stream_id,split,support)
            win_units,mrw_units,evidence_receipts=evidence_units(pools,final_block_cap_tokens=int(contract["renderer"]["final_block_cap_tokens"]),transcript_max_chars=int(contract["updater"]["transcript_max_chars"]))
            stream_root=run_root/"states"/stream_id; evidence_path=stream_root/"evidence_windows.json"
            win_bundle_sha=canonical_sha([u.__dict__ for u in win_units]); mrw_bundle_sha=canonical_sha([u.__dict__ for u in mrw_units])
            evidence_payload={"stream_id":stream_id,"win_c_evidence_bundle_sha256":win_bundle_sha,"mrw_evidence_bundle_sha256":mrw_bundle_sha,"receipts":evidence_receipts,"mrw_provider_execution_authorized":True,"primary_control":"fresh_contemporaneous_win_c","replicates_per_stream":len(REPLICATES)}
            if evidence_path.exists():
                existing=load_json(evidence_path)
                require(existing.get("win_c_evidence_bundle_sha256")==win_bundle_sha and existing.get("mrw_evidence_bundle_sha256")==mrw_bundle_sha, "frozen evidence-window drift")
            else:
                atomic_json(evidence_path,evidence_payload)
            arm_inputs={
                "win_c": (win_units, ProjectionName.WINNER_ONLY),
                "mrw": (mrw_units, ProjectionName.MIXED_REJECTED_WITNESS),
            }
            for replicate in REPLICATES:
                unit_id=f"{stream_id}/rep{replicate}"
                if unit_id in completed_units:
                    continue
                rep_root=stream_root/f"replicate_{replicate}"
                execution_stream_id=f"{stream_id}::rep{replicate}"
                updates: dict[str,dict[str,Any]]={}
                for arm in ordered_arms(stream_id,replicate,UPDATE_ORDER_SALT):
                    state_root=rep_root/arm; ledger_path=state_root/"checkpoints/provider_budget.sqlite3"
                    ledger=ProviderBudgetLedger(path=ledger_path,contract_sha256=contract_sha,authorization_sha256=auth_sha,total_limit=int(contract["budget"]["max_provider_calls_per_state"]),per_unit_limit=int(contract["budget"]["max_provider_calls_per_unit"]),allow_create=not ledger_path.exists())
                    units_for_arm, projection_for_arm = arm_inputs[arm]
                    updates[arm]=await ensure_update(contract=contract,contract_sha=contract_sha,auth_sha=auth_sha,base_stream_id=stream_id,execution_stream_id=execution_stream_id,replicate=replicate,arm=arm,pools=pools,evidence_units_for_arm=units_for_arm,projection=projection_for_arm,initial_skill=initial_skill,initial_sha=initial_sha,mind_head=mind_head,requested=requested,resolved=resolved,settings=settings,state_root=state_root,ledger=ledger)
                for task_id in contract["heldout"]["task_ids"]:
                    for arm in ordered_arms(stream_id,replicate,EVAL_ORDER_SALT,task_id):
                        state_root=rep_root/arm
                        ensure_eval(contract=contract,auth_path=args.authorization,identity_path=identity_path,actor_python=actor_python,actor_env=actor_env,stream_id=execution_stream_id,arm=arm,task_id=task_id,state_root=state_root,update=updates[arm],ledger_path=state_root/"checkpoints/provider_budget.sqlite3")
                states=[]
                for arm in ARMS:
                    state_root=rep_root/arm; eval_manifest=state_root/"checkpoints/completed_eval_tasks.jsonl"; eval_rows=rows_by(eval_manifest,"task_id")
                    require(set(eval_rows)==set(contract["heldout"]["task_ids"]), f"heldout completion set invalid: {unit_id}/{arm}")
                    for row in eval_rows.values(): verify_eval(row,state_root,updates[arm]["skill_post_sha256"],updates[arm]["update_receipt_sha256"])
                    ledger=ProviderBudgetLedger(path=state_root/"checkpoints/provider_budget.sqlite3",contract_sha256=contract_sha,authorization_sha256=auth_sha,total_limit=int(contract["budget"]["max_provider_calls_per_state"]),per_unit_limit=int(contract["budget"]["max_provider_calls_per_unit"]),allow_create=False)
                    states.append({"arm":arm,"update_receipt_sha256":updates[arm]["update_receipt_sha256"],"skill_post_sha256":updates[arm]["skill_post_sha256"],"completed_heldout_tasks":len(eval_rows),"eval_manifest_path":str(eval_manifest),"eval_manifest_sha256":sha_file(eval_manifest),"provider_budget":ledger.snapshot().to_dict()})
                rep_summary={"schema_version":"1.0","artifact_type":"e2-r17-deepseek-v2-replicated-paired-unit","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":"COMPLETED","unit_id":unit_id,"stream_id":stream_id,"execution_stream_id":execution_stream_id,"replicate":replicate,"pool_ids":[p.pool_id for p in pools],"evidence_windows_sha256":sha_file(evidence_path),"update_order":ordered_arms(stream_id,replicate,UPDATE_ORDER_SALT),"heldout_task_ids":contract["heldout"]["task_ids"],"states":states,"mrw_executed":True,"primary_control":"win_c","paper_promotion_authority":False}
                rep_summary_path=run_root/"summary/replicates"/f"{stream_id}-rep{replicate}.json"; atomic_json(rep_summary_path,rep_summary)
                manifest_row={"unit_id":unit_id,"stream_id":stream_id,"replicate":replicate,"summary_path":str(rep_summary_path),"summary_sha256":sha_file(rep_summary_path),"source":"repair2_fresh","completed_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds")}
                valid_row={"unit_id":unit_id,"stream_id":stream_id,"replicate_id":replicate,"source":"repair2_fresh","pair_summary_path":str(rep_summary_path),"pair_summary_sha256":sha_file(rep_summary_path),"arms":{}}
                for arm in ARMS:
                    state_root=rep_root/arm
                    update=updates[arm]
                    valid_row["arms"][arm]={"state_root":str(state_root),"skill_sha256":update["skill_post_sha256"],"update_receipt_sha256":update["update_receipt_sha256"],"eval_manifest_path":str(state_root/"checkpoints/completed_eval_tasks.jsonl"),"eval_manifest_sha256":sha_file(state_root/"checkpoints/completed_eval_tasks.jsonl"),"updater_calls":int(update["provider_calls"]),"attempt0_success":bool(update.get("attempt0_success",int(update["provider_calls"])==10)),"correction_required":bool(update.get("correction_required",int(update["provider_calls"])==11))}
                if unit_id not in valid_units:
                    append_jsonl(valid_manifest,valid_row); valid_units[unit_id]=valid_row
                append_jsonl(unit_manifest,manifest_row); completed_units[unit_id]=manifest_row
        expected={f"{stream}/rep{rep}" for stream in contract["streams"] for rep in REPLICATES}
        require(set(completed_units)==expected, "DeepSeek V2 Repair2 did not complete all 48 paired replicate units")
        validate_valid_rows(list(valid_units.values()), streams=contract["streams"], quarantine=quarantine, require_complete=True)
        reliability={arm:{"attempt0_success_count":0,"correction_required_count":0,"correction_success_count":0,"correction_failure_count":0} for arm in ARMS}
        for row in valid_units.values():
            for arm in ARMS:
                a=row["arms"][arm]
                if a.get("correction_required"):
                    reliability[arm]["correction_required_count"]+=1; reliability[arm]["correction_success_count"]+=1
                else:
                    reliability[arm]["attempt0_success_count"]+=1
        final={"schema_version":"1.0","artifact_type":"e2-r17-deepseek-v2-repair2-continuation-summary","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":"COMPLETED_PENDING_SEPARATE_DEEPSEEK_V2_ADJUDICATION","contract_sha256":contract_sha,"authorization_sha256":auth_sha,"streams":len(contract["streams"]),"replicates_per_stream":len(REPLICATES),"paired_replicate_units":len(expected),"inherited_paired_units":sum(row.get("source")=="repair1_inherited" for row in valid_units.values()),"fresh_paired_units":sum(row.get("source")=="repair2_fresh" for row in valid_units.values()),"arms":list(ARMS),"learned_states":len(expected)*2,"heldout_tasks_per_state":len(contract["heldout"]["task_ids"]),"heldout_rollout_units":len(expected)*2*len(contract["heldout"]["task_ids"]),"mrw_executed":True,"primary_control":"win_c","inference_performed":False,"paper_promotion_authority":False,"completed_replicate_manifest":str(unit_manifest),"completed_replicate_manifest_sha256":sha_file(unit_manifest),"valid_replicate_manifest":str(valid_manifest),"valid_replicate_manifest_sha256":sha_file(valid_manifest),"runtime_reliability":reliability,"repair1_quarantined_patch_apply_failures":{"win_c":0,"mrw":1}}
        atomic_json(run_root/"summary/deepseek_v2_repair2_continuation_summary.json",final); success=True; return final
    finally:
        os.close(lock_fd)
        if success: lock_path.unlink(missing_ok=True)


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--contract",type=Path,required=True); parser.add_argument("--authorization",type=Path,required=True); args=parser.parse_args()
    payload=asyncio.run(main_async(args)); print(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)); return 0 if payload["status"]=="COMPLETED_PENDING_SEPARATE_DEEPSEEK_V2_ADJUDICATION" else 2


if __name__ == "__main__":
    raise SystemExit(main())
