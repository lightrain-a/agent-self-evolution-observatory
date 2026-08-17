from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Callable

from .config import PROJECT_ROOT
from .paper_first_shadow_continuation_frontier import validate_shadow_continuation_frontier
from .paper_first_problem_discovery_contract import DISCOVERY_OPERATOR_VERSION
from .paper_first_shadow_search_admission import validate_shadow_search_admission
from .problem_search_control_snapshot import compute_control_snapshot, memory_sha256
from .problem_search_shadow_launcher import NO_FRESH_TARGET_STATUS, prepare_shadow_run, shadow_search_target_inventory

READY_FRONTIER = "READY_FOR_ZERO_PROVIDER_SHADOW_QUALIFICATION"
QUALIFIED_STATUS = "READY_FOR_SHADOW_EXPANSION_ZERO_PROVIDER_HANDOFF"
DEFAULT_PUBLIC_STATE = PROJECT_ROOT / "generated" / "research-system-state.json"
DEFAULT_CANONICAL_PRIVATE_POOL = Path("/home/wyt/code/agent-self-evolution-observatory/generated/research-data/paper-first-problem-discovery/primary-evidence-pool.json")
DEFAULT_WORKTREE_PARENT = Path("/home/wyt/code")
SHADOW_MEMORY_RELATIVE = Path("generated/paper-first-search-portfolio-design-adjudication.json")


def _load(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _git_head(repo: Path) -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True, stderr=subprocess.DEVNULL).strip()


def _create_pinned_worktree(repo: Path, target: Path, commit: str) -> None:
    subprocess.check_call(["git", "worktree", "add", "--detach", str(target), commit], cwd=repo)


def _request_id(
    source_set_sha256: str,
    primary_content_sha256: str,
    discovery_operator_version: str,
    memory_sha256_value: str,
    control_snapshot_sha256: str,
    main_commit: str,
) -> str:
    identity = "\n".join((
        source_set_sha256,
        primary_content_sha256,
        discovery_operator_version,
        memory_sha256_value,
        control_snapshot_sha256,
        main_commit,
    ))
    return hashlib.sha256(identity.encode()).hexdigest()[:16]


def _qualification_identity(
    *,
    source_repo: Path,
    source_set_sha256: str,
    primary_content_sha256: str,
    discovery_operator_version: str,
) -> dict[str, str]:
    commit = _git_head(source_repo)
    memory_path = source_repo / SHADOW_MEMORY_RELATIVE
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("shadow qualification source repository HEAD is unavailable")
    if not memory_path.is_file():
        raise ValueError(f"shadow qualification memory artifact unavailable: {memory_path}")
    memory_sha = memory_sha256(memory_path)
    control_sha = str(compute_control_snapshot(project_root=source_repo).get("control_snapshot_sha256") or "")
    if not re.fullmatch(r"[0-9a-f]{64}", memory_sha) or not re.fullmatch(r"[0-9a-f]{64}", control_sha):
        raise ValueError("shadow qualification control or memory identity is invalid")
    request_id = _request_id(
        source_set_sha256,
        primary_content_sha256,
        discovery_operator_version,
        memory_sha,
        control_sha,
        commit,
    )
    return {
        "request_id": request_id,
        "main_commit": commit,
        "discovery_operator_version": discovery_operator_version,
        "memory_sha256": memory_sha,
        "control_snapshot_sha256": control_sha,
    }


def _bounded_result(status: str, *, reason: str, request_id: str = "", worktree: Path | None = None, run_root: Path | None = None, commit: str = "", qualification: dict[str, Any] | None = None, target_inventory: dict[str, Any] | None = None) -> dict[str, Any]:
    qualification = qualification or {}
    target_inventory = target_inventory or {}
    prepared = status in {"SHADOW_QUALIFICATION_PREPARED_ZERO_PROVIDER", "SHADOW_QUALIFICATION_ALREADY_PREPARED"}
    return {
        "schema_version": "1.0",
        "status": status,
        "reason": reason[:1200],
        "request_id": request_id,
        "summary": {
            "qualification_prepared": int(prepared),
            "worktree_created": int(status == "SHADOW_QUALIFICATION_PREPARED_ZERO_PROVIDER"),
            "model_calls_executed": 0,
            "automatic_provider_calls_authorized": 0,
            "expansion_started": 0,
            "active_inversion_asset_count": int(target_inventory.get("active_inversion_asset_count", 0) or 0),
            "active_positive_residual_asset_count": int(target_inventory.get("active_positive_residual_asset_count", 0) or 0),
            "fresh_phenomenon_target_count": int(target_inventory.get("fresh_phenomenon_target_count", 0) or 0),
            "fresh_fallback_required": bool(target_inventory.get("fresh_fallback_required", False)),
            "scientific_authority": 0,
            "generator_reopen_authorized": 0,
            "problem_gate_authorized": 0,
            "method_authorized": 0,
            "experiment_authorized": 0,
            "p0_authorized": 0,
            "gpu_authorized": 0,
        },
        "provenance": {
            "qualified_commit": commit,
            "stage_runner_required_schema": str(qualification.get("stage_runner_required_schema") or ""),
            "control_snapshot_sha256": str(qualification.get("control_snapshot_sha256") or ""),
            "source_set_sha256": str(qualification.get("source_set_sha256") or ""),
            "source_primary_content_sha256": str(qualification.get("source_primary_content_sha256") or ""),
            "frozen_pool_sha256": str(qualification.get("frozen_pool_sha256") or ""),
            "memory_sha256": str(qualification.get("memory_sha256") or ""),
            "worktree_path": str(worktree or ""),
            "run_root": str(run_root or ""),
        },
        "policy": {
            "scientific_authority": False,
            "git_handoff_is_control_plane_only": True,
            "consumer_requires_ready_shadow_continuation_frontier": True,
            "consumer_creates_pinned_worktree_before_qualification": True,
            "consumer_uses_canonical_private_primary_pool": True,
            "consumer_can_only_prepare_zero_provider_qualification": True,
            "consumer_requires_nonempty_target_inventory_before_worktree_creation": True,
            "consumer_cannot_start_expansion_or_model_provider": True,
            "consumer_cannot_qualify_support_or_reopen_problem_gate": True,
            "consumer_cannot_authorize_method_experiment_p0_gpu": True,
        },
        "scientific_authority": False,
        "authority": {"canonical_generator": False, "problem_gate": False, "paper_design": False, "method": False, "experiment": False, "p0": False, "gpu": False},
    }


def _existing_qualification(run_root: Path, expected_set: str, expected_content: str, identity: dict[str, str]) -> dict[str, Any] | None:
    receipt = _load(run_root / "shadow-run-qualification.json")
    if not receipt:
        return None
    if receipt.get("status") != "READY_FOR_SHADOW_EXPANSION" or receipt.get("scientific_authority") is not False:
        return None
    required = {
        "source_set_sha256": expected_set,
        "source_primary_content_sha256": expected_content,
        "discovery_operator_version": str(identity.get("discovery_operator_version") or ""),
        "memory_sha256": str(identity.get("memory_sha256") or ""),
        "control_snapshot_sha256": str(identity.get("control_snapshot_sha256") or ""),
        "main_commit": str(identity.get("main_commit") or ""),
    }
    if any(str(receipt.get(key) or "") != value for key, value in required.items()):
        return None
    if str(receipt.get("stage_runner_required_schema") or "") != "1.4":
        return None
    return receipt


def consume_shadow_qualification_handoff(
    *,
    public_state_path: Path = DEFAULT_PUBLIC_STATE,
    source_repo: Path = PROJECT_ROOT,
    canonical_private_pool: Path = DEFAULT_CANONICAL_PRIVATE_POOL,
    worktree_parent: Path = DEFAULT_WORKTREE_PARENT,
    create_worktree: Callable[[Path, Path, str], None] = _create_pinned_worktree,
    qualifier: Callable[..., dict[str, Any]] = prepare_shadow_run,
    identity_builder: Callable[..., dict[str, str]] = _qualification_identity,
    target_preflight: Callable[..., dict[str, Any]] = shadow_search_target_inventory,
) -> dict[str, Any]:
    state = _load(public_state_path)
    if not state:
        return _bounded_result("HOLD_PUBLIC_SHADOW_STATE_UNAVAILABLE", reason=f"Public research state unavailable: {public_state_path}")
    frontier = state.get("paper_first_shadow_continuation_frontier") or {}
    admission = state.get("paper_first_shadow_search_admission") or {}
    frontier_errors = validate_shadow_continuation_frontier(frontier) if frontier else ["missing frontier"]
    admission_errors = validate_shadow_search_admission(admission) if admission else ["missing admission"]
    if frontier_errors or admission_errors:
        return _bounded_result("HOLD_PUBLIC_SHADOW_CONTROL_INVALID", reason=";".join(frontier_errors + admission_errors))
    if frontier.get("status") != READY_FRONTIER:
        return _bounded_result("SKIPPED_SHADOW_QUALIFICATION_FRONTIER_NOT_READY", reason=f"Current frontier is {frontier.get('status')}; no qualification is created.")
    if frontier.get("next_control_action") != "canonical-private-pool-shadow-qualification" or int((frontier.get("summary") or {}).get("shadow_qualification_ready") or 0) != 1:
        return _bounded_result("HOLD_SHADOW_QUALIFICATION_FRONTIER_INCONSISTENT", reason="READY frontier lacks the unique zero-provider qualification action.")
    admission_summary = admission.get("summary") or {}
    source = admission.get("source_identity") or {}
    if admission.get("status") != "READY_FOR_SHADOW_QUALIFICATION" or admission_summary.get("qualification_allowed") is not True:
        return _bounded_result("HOLD_SHADOW_QUALIFICATION_ADMISSION_INCONSISTENT", reason="Frontier is READY but admission is not qualification-ready.")
    source_set = str(source.get("current_source_set_sha256") or "")
    source_content = str(source.get("current_primary_content_sha256") or "")
    operator_version = str(admission_summary.get("current_discovery_operator_version") or "")
    if not re.fullmatch(r"[0-9a-f]{64}", source_set) or not re.fullmatch(r"[0-9a-f]{64}", source_content):
        return _bounded_result("HOLD_SHADOW_QUALIFICATION_SOURCE_IDENTITY_INVALID", reason="Qualification-ready admission lacks bounded source-set/content digests.")
    if operator_version != DISCOVERY_OPERATOR_VERSION:
        return _bounded_result("HOLD_SHADOW_QUALIFICATION_OPERATOR_IDENTITY_INVALID", reason=f"Qualification-ready admission operator {operator_version!r} does not match current control operator {DISCOVERY_OPERATOR_VERSION!r}.")
    if not canonical_private_pool.is_file():
        return _bounded_result("HOLD_CANONICAL_PRIVATE_POOL_UNAVAILABLE", reason=f"Canonical private primary pool unavailable: {canonical_private_pool}")
    try:
        target_inventory = target_preflight(
            private_pool_path=canonical_private_pool,
            memory_path=source_repo / SHADOW_MEMORY_RELATIVE,
            admission_state=admission,
        )
    except Exception as error:
        return _bounded_result("HOLD_SHADOW_QUALIFICATION_TARGET_PREFLIGHT_INVALID", reason=f"{type(error).__name__}:{str(error)[:900]}")
    if target_inventory.get("fresh_fallback_required") is True and int(target_inventory.get("fresh_phenomenon_target_count") or 0) == 0:
        return _bounded_result(
            NO_FRESH_TARGET_STATUS,
            reason="No active search asset remains and the current private Primary plus persistent memory contains zero eligible v13 fresh phenomena. Qualification stops before worktree creation and provider expansion remains forbidden.",
            target_inventory=target_inventory,
        )
    try:
        identity = identity_builder(
            source_repo=source_repo,
            source_set_sha256=source_set,
            primary_content_sha256=source_content,
            discovery_operator_version=operator_version,
        )
    except Exception as error:
        return _bounded_result("HOLD_SHADOW_QUALIFICATION_CONTROL_IDENTITY_INVALID", reason=f"{type(error).__name__}:{str(error)[:900]}")
    commit = str(identity.get("main_commit") or "")
    request_id = str(identity.get("request_id") or "")
    if not re.fullmatch(r"[0-9a-f]{40}", commit) or not re.fullmatch(r"[0-9a-f]{16}", request_id):
        return _bounded_result("HOLD_SHADOW_QUALIFICATION_CONTROL_IDENTITY_INVALID", reason="Qualification identity lacks a valid pinned commit or request digest.")
    worktree = worktree_parent / f"agent-self-evolution-shadow-qual-{request_id}"
    run_id = f"shadow-auto-{request_id}"
    run_root = worktree / "generated" / "research-data" / "paper-first-problem-discovery" / "search-portfolios" / run_id
    if worktree.exists():
        receipt = _existing_qualification(run_root, source_set, source_content, identity)
        if receipt:
            return _bounded_result("SHADOW_QUALIFICATION_ALREADY_PREPARED", reason="A matching pinned qualification already exists; no duplicate worktree or provider call is created.", request_id=request_id, worktree=worktree, run_root=run_root, commit=str(receipt.get("main_commit") or ""), qualification=receipt, target_inventory=target_inventory)
        return _bounded_result("HOLD_EXISTING_SHADOW_QUALIFICATION_WORKTREE_INVALID", reason=f"Deterministic worktree already exists without a matching READY qualification: {worktree}", request_id=request_id, worktree=worktree, run_root=run_root, commit=commit)
    create_worktree(source_repo, worktree, commit)
    memory_path = worktree / "generated" / "paper-first-search-portfolio-design-adjudication.json"
    try:
        result = qualifier(
            run_root=run_root,
            private_pool_path=canonical_private_pool,
            memory_path=memory_path,
            project_root=worktree,
            admission_state=admission,
        )
    except Exception as error:
        return _bounded_result("HOLD_SHADOW_QUALIFICATION_PREPARE_ERROR", reason=f"{type(error).__name__}:{str(error)[:900]}", request_id=request_id, worktree=worktree, run_root=run_root, commit=commit)
    if result.get("status") != QUALIFIED_STATUS or int((result.get("summary") or {}).get("model_calls_executed") or 0) != 0:
        return _bounded_result("HOLD_SHADOW_QUALIFICATION_LAUNCHER_RESULT_INVALID", reason=f"Zero-provider launcher returned unexpected state: {result.get('status')}", request_id=request_id, worktree=worktree, run_root=run_root, commit=commit)
    receipt = _existing_qualification(run_root, source_set, source_content, identity)
    if not receipt:
        return _bounded_result("HOLD_SHADOW_QUALIFICATION_RECEIPT_INVALID", reason="Launcher completed but a matching schema-1.4 qualification receipt was not found.", request_id=request_id, worktree=worktree, run_root=run_root, commit=commit)
    return _bounded_result("SHADOW_QUALIFICATION_PREPARED_ZERO_PROVIDER", reason="Git-mediated handoff created one pinned worktree and one zero-provider schema-1.4 qualification. Expansion remains unstarted and unauthorized by this consumer.", request_id=request_id, worktree=worktree, run_root=run_root, commit=commit, qualification=receipt, target_inventory=target_inventory)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--public-state", type=Path, default=DEFAULT_PUBLIC_STATE)
    parser.add_argument("--source-repo", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--private-pool", type=Path, default=DEFAULT_CANONICAL_PRIVATE_POOL)
    parser.add_argument("--worktree-parent", type=Path, default=DEFAULT_WORKTREE_PARENT)
    args = parser.parse_args()
    state = consume_shadow_qualification_handoff(public_state_path=args.public_state, source_repo=args.source_repo, canonical_private_pool=args.private_pool, worktree_parent=args.worktree_parent)
    print(json.dumps(state, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
