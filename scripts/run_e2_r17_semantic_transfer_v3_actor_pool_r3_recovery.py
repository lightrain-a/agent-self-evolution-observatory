#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "scripts/run_e2_r17_semantic_transfer_v3_actor_pool.py"

spec = importlib.util.spec_from_file_location("e2_r17_v3_actor_r2_base", BASE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot load base V3 actor: {BASE_PATH}")
base = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = base
spec.loader.exec_module(base)

EXPECTED_AUTH_STATUS = "AUTHORIZED_SEMANTIC_TRANSFER_V3_STAGE_A_R3_RECOVERY"
EXPECTED_LEASE_STATUS = "RUNNING_STAGE_A_V3_R3_RECOVERY"
EXPECTED_UNIT_COUNT = 158


def validate_authority(
    *,
    mode: str,
    authorization: Path | None,
    task_ids: list[str],
    split: dict[str, Any],
    k: int,
) -> tuple[dict[str, Any] | None, str | None]:
    development = {str(item) for item in split.get("development") or []}
    if mode == "protocol_smoke":
        if not set(task_ids).issubset(development):
            raise RuntimeError("protocol smoke may access development tasks only")
        if authorization is not None:
            raise RuntimeError("protocol smoke must not borrow scientific authorization")
        return None, None
    if authorization is None:
        raise RuntimeError("R3 recovery actor execution requires --authorization")
    payload = json.loads(authorization.read_text(encoding="utf-8"))
    if payload.get("status") != EXPECTED_AUTH_STATUS:
        raise RuntimeError("R3 recovery actor requires the exact R3 recovery authorization status")
    authority = payload.get("authority") or {}
    if authority.get("stage_a_provider_execution") is not True:
        raise RuntimeError("R3 recovery Stage-A provider execution authority absent")
    for forbidden in (
        "stage_b_learning_execution",
        "updater",
        "heldout_evaluation",
        "analyzer",
        "second_backbone",
        "public_benchmark",
        "paper_promotion",
    ):
        if authority.get(forbidden) is not False:
            raise RuntimeError(f"R3 recovery authorization is overbroad or underspecified: {forbidden}")
    scope = payload.get("execution_scope") or {}
    if scope.get("recovery_mode") != "MATCHED_CENSOR_158":
        raise RuntimeError("R3 recovery authorization mode drift")
    allowed_modes = {str(value) for value in scope.get("allowed_modes") or []}
    if mode not in allowed_modes:
        raise RuntimeError(f"R3 recovery authorization does not allow mode={mode}")
    allowed_tasks = {str(value) for value in scope.get("allowed_task_ids") or []}
    if len(allowed_tasks) != EXPECTED_UNIT_COUNT:
        raise RuntimeError("R3 recovery authorization task universe is not 158 unique IDs")
    if not set(task_ids).issubset(allowed_tasks):
        raise RuntimeError("requested task is outside the R3 recovery execution universe")
    if int(scope.get("exact_k") or 0) != int(k):
        raise RuntimeError("R3 recovery exact K drift")
    if scope.get("allow_noninitial_skill") is not False:
        raise RuntimeError("R3 recovery must forbid non-initial skills")
    return payload, base.sha256(authorization)


def validate_stage_a_runner_context(
    *,
    authorization_payload: dict[str, Any] | None,
    authorization_sha: str | None,
    run_root: Path,
    prefix_ks: tuple[int, ...],
    concurrency: int,
) -> dict[str, Any] | None:
    if authorization_payload is None:
        return None
    if not authorization_sha:
        raise RuntimeError("R3 recovery invocation lacks authorization SHA")
    scope = authorization_payload.get("execution_scope") or {}
    required_run_root = Path(str(scope.get("required_run_root") or ""))
    if not str(required_run_root) or run_root.resolve() != required_run_root.resolve():
        raise RuntimeError("R3 recovery actor run-root drift")
    if tuple(int(v) for v in scope.get("exact_prefix_ks") or []) != tuple(prefix_ks):
        raise RuntimeError("R3 recovery prefix-K drift")
    if int(scope.get("exact_concurrency") or 0) != int(concurrency):
        raise RuntimeError("R3 recovery concurrency drift")
    if scope.get("runner_lease_required") is not True:
        raise RuntimeError("R3 recovery authorization lacks runner lease requirement")
    lease_path = Path(str(scope.get("global_lease_path") or ""))
    if not lease_path.is_file():
        raise RuntimeError("R3 recovery actor requires active recovery lease")
    lease = json.loads(lease_path.read_text(encoding="utf-8"))
    if lease.get("status") != EXPECTED_LEASE_STATUS:
        raise RuntimeError("R3 recovery global lease is not running")
    if lease.get("contract_sha256") != authorization_payload.get("contract_sha256"):
        raise RuntimeError("R3 recovery lease contract binding drift")
    if lease.get("authorization_sha256") != authorization_sha:
        raise RuntimeError("R3 recovery lease authorization binding drift")
    if Path(str(lease.get("run_root") or "")).resolve() != run_root.resolve():
        raise RuntimeError("R3 recovery lease run-root binding drift")
    return lease


def validate_exact_once_acquisition_scope(
    *,
    authorization_payload: dict[str, Any] | None,
    run_root: Path,
    requested_task_ids: list[str],
) -> dict[str, Any] | None:
    if authorization_payload is None:
        return None
    scope = authorization_payload.get("execution_scope") or {}
    policy = scope.get("exact_once_acquisition") or {}
    if policy.get("required") is not True:
        raise RuntimeError("R3 recovery lacks actor-enforced exact-once acquisition")
    if policy.get("attempt_before_any_provider_io") is not True:
        raise RuntimeError("R3 recovery does not burn task before provider I/O")
    if policy.get("replay_allowed") is not False or policy.get("ambiguous_recollection_allowed") is not False:
        raise RuntimeError("R3 recovery permits replay or ambiguous recollection")
    if int(policy.get("unit_count") or 0) != EXPECTED_UNIT_COUNT:
        raise RuntimeError("R3 recovery exact-once unit count must be 158")
    manifest_path = base._scope_path(str(policy.get("unit_manifest_path") or ""))
    manifest_sha = str(policy.get("unit_manifest_sha256") or "")
    if not manifest_path.is_file() or base.sha256(manifest_path) != manifest_sha:
        raise RuntimeError("R3 recovery exact-once manifest drift")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_task_ids = [str(value) for value in manifest.get("ordered_task_ids") or []]
    if len(manifest_task_ids) != EXPECTED_UNIT_COUNT or len(set(manifest_task_ids)) != EXPECTED_UNIT_COUNT:
        raise RuntimeError("R3 recovery manifest is not 158 unique task IDs")
    allowed_task_ids = [str(value) for value in scope.get("allowed_task_ids") or []]
    if manifest_task_ids != allowed_task_ids:
        raise RuntimeError("R3 recovery manifest/order differs from authorization universe")
    if not set(requested_task_ids).issubset(set(manifest_task_ids)):
        raise RuntimeError("requested task absent from R3 recovery exact-once universe")
    claim_root = Path(str(policy.get("required_claim_root") or ""))
    if claim_root.resolve() != (run_root / "checkpoints/stage_a_task_claims").resolve():
        raise RuntimeError("R3 recovery exact-once claim root drift")
    return {
        "claim_root": claim_root,
        "manifest_path": manifest_path,
        "manifest_sha256": manifest_sha,
        "unit_ids": tuple(manifest_task_ids),
    }


base.validate_authority = validate_authority
base.validate_stage_a_runner_context = validate_stage_a_runner_context
base.validate_exact_once_acquisition_scope = validate_exact_once_acquisition_scope


if __name__ == "__main__":
    raise SystemExit(base.main())
