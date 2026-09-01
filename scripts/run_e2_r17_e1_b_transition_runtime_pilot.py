#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import fcntl
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
from research_pipeline.e2_r17_mindmemos_ark_adapter import MindMemOSArkPlanChatAdapter, PLAN_BASE_URL
from research_pipeline.e2_r17_mindmemos_updater import run_projection_update
from research_pipeline.e2_r17_provider_budget import ProviderBudgetLedger
from research_pipeline.e2_r17_search_projection_runner import ProjectionName, project_stream
from scripts.run_e2_r17_e1_a_pool_support import validate_runtime as validate_actor_runtime
from scripts.run_e2_r17_v31_provider_runtime_pilot import (
    bind_mindmemos,
    evidence_units,
    load_selected_pools,
    validate_updater_runtime,
)


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def validate_contract_auth(contract_path: Path, auth_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    contract = load_json(contract_path)
    auth = load_json(auth_path)
    require(contract.get("status") == "FROZEN_E1_B_TRANSITION_RUNTIME_PILOT", "transition Pilot contract not frozen")
    require(auth.get("status") == "AUTHORIZED_E1", "transition Pilot authorization must use AUTHORIZED_E1")
    require(auth.get("contract_sha256") == sha_file(contract_path), "transition authorization/contract SHA mismatch")
    authority = auth.get("authority") or {}
    require(authority.get("scientific_experiment") is True, "actor runner requires scoped scientific execution authority")
    require(authority.get("e1_b") is True, "transition Pilot requires E1-B noninitial-skill loading authority")
    require(authority.get("e1_b_transition_runtime_pilot") is True, "transition runtime Pilot authority bit absent")
    require(authority.get("e1_b_negative_control") is False, "transition Pilot must not authorize negative-control inference")
    require(authority.get("mrw_causal_comparison") is False, "transition Pilot must not authorize MRW science")
    require(authority.get("paper_promotion") is False, "transition Pilot cannot promote paper")
    scope = auth.get("execution_scope") or {}
    require(scope.get("allowed_modes") == ["e1"], "transition Pilot mode scope drift")
    require(scope.get("allowed_task_ids") == [contract["development_evaluation"]["task_id"]], "transition Pilot task scope drift")
    require(int(scope.get("exact_k")) == 1, "transition Pilot must bind K=1 evaluation")
    require(scope.get("allow_noninitial_skill") is True, "transition Pilot must explicitly allow receipt-bound noninitial skill")
    budget_scope = scope.get("provider_budget") or {}
    require(budget_scope.get("required") is True, "transition Pilot must require provider budget ledger")
    require(int(budget_scope.get("total_limit")) == int(contract["budget"]["max_provider_calls"]), "transition total budget drift")
    require(int(budget_scope.get("per_unit_limit")) == int(contract["budget"]["max_provider_calls_per_unit"]), "transition per-unit budget drift")
    return contract, auth


async def main_async(args: argparse.Namespace) -> dict[str, Any]:
    contract, auth = validate_contract_auth(args.contract, args.authorization)
    contract_sha = sha_file(args.contract)
    auth_sha = sha_file(args.authorization)

    updater_runtime_contract = {"runtime": contract["updater_runtime"], "mindmemos": contract["mindmemos"]}
    updater_python, updater_env = validate_updater_runtime(updater_runtime_contract)
    require(Path(sys.executable) == updater_python, "transition Pilot must itself run under dedicated updater runtime")
    actor_python, actor_env = validate_actor_runtime({"runtime": contract["actor_runtime"]})

    for label, item in contract["bound_code"].items():
        path = ROOT / item["path"]
        require(path.is_file() and sha_file(path) == item["sha256"], f"bound code drift: {label}")

    mind_root = Path(contract["mindmemos"]["root"])
    head = subprocess.check_output(["git", "-C", str(mind_root), "rev-parse", "HEAD"], text=True).strip()
    require(head == contract["mindmemos"]["commit"], "MindMemOS commit drift")
    require(not subprocess.check_output(["git", "-C", str(mind_root), "status", "--short"], text=True).strip(), "MindMemOS checkout dirty")
    bind_mindmemos(mind_root)

    identity_path = ROOT / contract["model_identity"]["path"]
    require(identity_path.is_file() and sha_file(identity_path) == contract["model_identity"]["sha256"], "transition model identity drift")
    identity = load_json(identity_path)
    require(identity.get("status") == "PASS_CURRENT_REVIEW_TRANCHE", "transition model identity not qualified")
    model_row = identity["requested_and_resolved"][contract["updater"]["requested_model"]]
    requested = str(model_row["requested"])
    resolved = str(model_row["resolved"])
    require(resolved == contract["updater"]["resolved_model"], "transition resolved model drift")

    pools = load_selected_pools({"historical_inputs": contract["historical_inputs"]})
    initial_skill_path = Path(contract["initial_skill"]["path"])
    require(initial_skill_path.is_file() and sha_file(initial_skill_path) == contract["initial_skill"]["sha256"], "transition initial skill drift")
    initial_skill = initial_skill_path.read_text(encoding="utf-8")
    initial_sha = sha_file(initial_skill_path)
    win_units, _, evidence_receipts = evidence_units(
        pools,
        final_block_cap_tokens=int(contract["renderer"]["final_block_cap_tokens"]),
        transcript_max_chars=int(contract["updater"]["transcript_max_chars"]),
    )
    win_stream = project_stream(
        stream_id="e1-b-transition-runtime-pilot",
        initial_skill_sha256=initial_sha,
        pools=pools,
        projection=ProjectionName.WINNER_ONLY,
    )

    run_root = Path(contract["run_root"])
    run_root.mkdir(parents=True, exist_ok=True)
    lock_path = run_root / ".exclusive.lock"
    lock_handle = lock_path.open("a+", encoding="utf-8")
    try:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        raise RuntimeError("transition Pilot lock already held; inspect before resume") from exc
    lock_handle.seek(0)
    lock_handle.truncate()
    lock_handle.write(json.dumps({"pid": os.getpid(), "contract_sha256": contract_sha, "authorization_sha256": auth_sha}, sort_keys=True))
    lock_handle.flush(); os.fsync(lock_handle.fileno())

    ledger_path = run_root / "checkpoints/provider_budget.sqlite3"
    ledger = ProviderBudgetLedger(
        path=ledger_path,
        contract_sha256=contract_sha,
        authorization_sha256=auth_sha,
        total_limit=int(contract["budget"]["max_provider_calls"]),
        per_unit_limit=int(contract["budget"]["max_provider_calls_per_unit"]),
        allow_create=not ledger_path.exists(),
    )
    success = False
    try:
        update_dir = run_root / "update/win"
        update_receipt = update_dir / "update_receipt.json"
        skill_path = update_dir / "skill_post/SKILL.md"
        update_checkpoint = run_root / "checkpoints/update_completed.json"
        if update_checkpoint.exists():
            cp = load_json(update_checkpoint)
            require(update_receipt.is_file() and skill_path.is_file(), "transition completed update artifacts missing")
            require(sha_file(update_receipt) == cp["update_receipt_sha256"], "transition update receipt SHA drift")
            require(sha_file(skill_path) == cp["skill_post_sha256"], "transition skill SHA drift")
        else:
            if update_dir.exists() and any(update_dir.rglob("*")):
                raise RuntimeError("partial ambiguous transition update exists; do not auto-rerun")
            load_env_file(args.env_file)
            raw = ArkSettings.from_env(required=True)
            require(raw.base_url.rstrip("/") == PLAN_BASE_URL, "transition updater refuses non-Ark-Plan route")
            settings = ArkSettings(api_key=raw.api_key, base_url=raw.base_url, default_model=raw.default_model, timeout_seconds=300.0, max_retries=0)
            adapter = MindMemOSArkPlanChatAdapter(
                settings=settings,
                requested_model=requested,
                required_resolved_model=resolved,
                max_parse_attempts=int(contract["updater"]["max_parse_attempts"]),
                record_dir=update_dir / "provider_calls",
                provider_budget_ledger=ledger,
                provider_budget_unit_id="e1-b-transition/update_win",
            )
            result = await run_projection_update(
                stream=win_stream,
                pools=pools,
                initial_skill_md=initial_skill,
                run_dir=update_dir,
                llm_adapter=adapter,
                mindmemos_commit=head,
                contract_sha256=contract_sha,
                authorization_sha256=auth_sha,
                transcript_max_chars=int(contract["updater"]["transcript_max_chars"]),
                blinded_evidence_units=win_units,
            )
            receipts = adapter.public_receipts()
            require(result.provider_calls == 10 and len(receipts) == 10, "transition updater must use exact nominal 10 calls")
            require(not any(row.get("parse_error") for row in receipts), "transition updater parse error")
            atomic_json(update_checkpoint, {
                "status": "COMPLETED",
                "update_receipt_path": result.update_receipt_path,
                "update_receipt_sha256": result.update_receipt_sha256,
                "skill_post_path": result.skill_post_path,
                "skill_post_sha256": result.skill_post_sha256,
                "provider_calls": result.provider_calls,
                "provider_tokens": result.provider_total_tokens,
            })

        eval_root = run_root / "evaluation"
        eval_summary = eval_root / "evaluation_summary.json"
        if eval_summary.exists():
            summary = load_json(eval_summary)
            require(summary.get("status") == "COMPLETED", "transition evaluation summary incomplete")
        else:
            if eval_root.exists() and any(eval_root.rglob("*")):
                raise RuntimeError("partial ambiguous transition evaluation exists; do not auto-rerun")
            command = [
                str(actor_python), str(ROOT / "scripts/run_e2_r17_actor_pool.py"),
                "--env-file", str(args.env_file),
                "--suite-root", contract["suite"]["root"],
                "--mindmemos-root", str(mind_root),
                "--run-root", str(eval_root),
                "--identity", str(identity_path),
                "--authorization", str(args.authorization),
                "--skill-source", str(skill_path.parent),
                "--updater-receipt", str(update_receipt),
                "--mode", "e1",
                "--model", contract["updater"]["requested_model"],
                "--task-id", contract["development_evaluation"]["task_id"],
                "--k", "1",
                "--prefix-ks", "1",
                "--max-turns", str(contract["actor"]["max_turns"]),
                "--max-output-tokens", str(contract["actor"]["max_output_tokens"]),
                "--concurrency", "1",
                "--provider-budget-ledger", str(ledger_path),
                "--provider-total-call-limit", str(contract["budget"]["max_provider_calls"]),
                "--provider-per-unit-call-limit", str(contract["budget"]["max_provider_calls_per_unit"]),
                "--output", str(eval_summary),
            ]
            env = actor_env.copy()
            env["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
            completed = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True)
            if completed.returncode != 0:
                atomic_json(run_root / "checkpoints/evaluation_failure.json", {
                    "status": "TECHNICAL_FAILURE",
                    "returncode": completed.returncode,
                    "stdout_tail": completed.stdout[-3000:],
                    "stderr_tail": completed.stderr[-3000:],
                    "provider_relaunch_authorized": False,
                })
                raise RuntimeError("transition noninitial-skill evaluation failed; stale lock preserved")
            require(eval_summary.is_file(), "transition actor returned without evaluation summary")
            summary = load_json(eval_summary)
            require(summary.get("status") == "COMPLETED", "transition evaluation summary incomplete")

        budget = ledger.snapshot()
        require(budget.total_claimed <= int(contract["budget"]["max_provider_calls"]), "transition total provider budget exceeded")
        require(summary.get("skill_pre_sha256") == sha_file(skill_path), "transition actor did not load receipt-bound learned skill")
        require(summary.get("updater_receipt_sha256") == sha_file(update_receipt), "transition actor updater receipt binding drift")
        require(summary.get("k") == 1, "transition evaluation K drift")
        require([row["task_id"] for row in summary.get("tasks") or []] == [contract["development_evaluation"]["task_id"]], "transition development task drift")

        final = {
            "schema_version": "1.0",
            "artifact_type": "e2-r17-e1-b-transition-runtime-pilot-summary",
            "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "status": "PASS_UPDATE_TO_NONINITIAL_SKILL_EVALUATION_HANDOFF",
            "contract_sha256": contract_sha,
            "authorization_sha256": auth_sha,
            "historical_update_pools": [pool.pool_id for pool in pools],
            "development_evaluation_task_id": contract["development_evaluation"]["task_id"],
            "development_task_outcome_used_for_promotion": False,
            "evidence_receipts": evidence_receipts,
            "update_receipt_sha256": sha_file(update_receipt),
            "skill_post_sha256": sha_file(skill_path),
            "evaluation_summary_sha256": sha_file(eval_summary),
            "provider_budget": budget.to_dict(),
            "heldout_evaluation_calls": 0,
            "e1_common_heldout_accessed": False,
            "mrw_executed": False,
            "negative_control_inference_performed": False,
            "scientific_effectiveness_evaluated": False,
            "authority": {"prepare_e1_b_negative_control_full_contract": True, "execute_e1_b_negative_control": False, "mrw_causal_comparison": False, "paper_promotion": False},
        }
        atomic_json(run_root / "summary/transition_runtime_pilot_summary.json", final)
        success = True
        return final
    finally:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
        lock_handle.close()
        if success:
            try:
                lock_path.unlink()
            except FileNotFoundError:
                pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--env-file", type=Path, required=True)
    args = parser.parse_args()
    payload = asyncio.run(main_async(args))
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["status"] == "PASS_UPDATE_TO_NONINITIAL_SKILL_EVALUATION_HANDOFF" else 2


if __name__ == "__main__":
    raise SystemExit(main())
