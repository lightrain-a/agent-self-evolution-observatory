from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .experiment_authority import validate_authority
from .paper_first_skill_validation_transfer_f0 import CANDIDATE_ID, build_plan
from .paper_first_skill_validation_transfer_f0_authority import (
    EXPECTED_RUNTIME_CONTRACT_SHA256,
    SERVER_ID,
    load_human_authority,
    require_bounded_f0_execution_authority,
)
from .paper_first_skill_validation_transfer_runtime_audit import (
    DEFAULT_JSON as RUNTIME_AUDIT_JSON,
    validate_runtime_audit,
)

CAPABILITY_ENV = "PAPER_FIRST_SKILL_VALIDATION_TRANSFER_EXECUTION_CAPABILITY"
CONTROL_ROOT_ENV = "PAPER_FIRST_SKILL_VALIDATION_TRANSFER_CONTROL_ROOT"
DEFAULT_CONTROL_ROOT = Path("/home/wyt/runtime/pa05-skill-validation-transfer-f0/control")
EXECUTION_KIND = "api_docker"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _canonical_sha(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def default_control_root() -> Path:
    raw = str(os.environ.get(CONTROL_ROOT_ENV, "")).strip()
    return Path(raw).expanduser() if raw else DEFAULT_CONTROL_ROOT


def default_capability_path() -> Path:
    return default_control_root() / "pa05-skill-validation-transfer-execution-capability.json"


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def build_execution_capability(
    *,
    human_authority: dict[str, Any],
    runtime_audit: dict[str, Any],
    run_id: str,
    authority_root: str | Path,
    experiment_authority_id: str,
    runtime_audit_path: str | Path = RUNTIME_AUDIT_JSON,
) -> dict[str, Any]:
    """Build a pre-model PA-05 execution capability bound to an active controller authority.

    Human approval alone is deliberately insufficient. A valid capability also requires
    a matching active ``experiment_authority`` row owned by the controller. This keeps
    the portfolio's ACTIVE_F0 transition tied to a live single-writer execution token
    rather than to a durable human permit or an arbitrary resource-lease string.
    """

    errors: list[str] = []
    try:
        human_authority = require_bounded_f0_execution_authority(authority=human_authority)
    except RuntimeError as error:
        errors.append(str(error))

    runtime_errors = validate_runtime_audit(runtime_audit)
    errors.extend(f"runtime-audit:{error}" for error in runtime_errors)

    plan_hash = build_plan()["plan_sha256"]
    server_id = str(runtime_audit.get("host") or "")
    runtime_contract_sha = str(runtime_audit.get("runtime_contract_sha256") or "")
    authority_root_path = Path(authority_root).expanduser().resolve()
    authority_validation = validate_authority(
        authority_root_path,
        CANDIDATE_ID,
        str(experiment_authority_id),
        plan_hash,
    )
    experiment_authority = authority_validation.get("authority") or {}

    if authority_validation.get("valid") is not True:
        errors.append("active-experiment-authority-required")
    if str(experiment_authority.get("run_id") or "") != str(run_id):
        errors.append("experiment-authority-run-mismatch")
    if runtime_contract_sha != EXPECTED_RUNTIME_CONTRACT_SHA256:
        errors.append("runtime-contract-sha256-mismatch")
    if server_id != SERVER_ID:
        errors.append("runtime-server-mismatch")
    if runtime_audit.get("runtime_infrastructure_ready") is not True:
        errors.append("runtime-infrastructure-not-ready")
    if runtime_audit.get("provider_credential_ready") is not True:
        errors.append("provider-credential-not-ready")
    if runtime_audit.get("execution_ready") is not True:
        errors.append("runtime-execution-not-ready")
    if not str(run_id).strip():
        errors.append("run-id-required")
    if not str(experiment_authority_id).strip():
        errors.append("experiment-authority-id-required")

    human_artifact_sha = str(human_authority.get("artifact_sha256") or "")
    human_artifact_path = str(human_authority.get("artifact_path") or "")
    runtime_path = Path(runtime_audit_path).expanduser()
    valid = not errors
    state: dict[str, Any] = {
        "schema_version": "1.1-private",
        "generated_at": _now(),
        "controller_verified": valid,
        "valid": valid,
        "idea_id": CANDIDATE_ID,
        "plan_hash": plan_hash,
        "run_id": str(run_id),
        "server_id": server_id or SERVER_ID,
        "execution_kind": EXECUTION_KIND,
        "requires_gpu": False,
        "gpu_lease_ids": [],
        "resource_lease_ids": [],
        "authority_kind": "controller-experiment-authority-backed-by-external-human-permit",
        "authority_id": str(experiment_authority_id),
        "experiment_authority_root": str(authority_root_path),
        "experiment_authority_epoch": experiment_authority.get("authority_epoch"),
        "human_authority_artifact_path": human_artifact_path,
        "human_authority_artifact_sha256": human_artifact_sha,
        "source_message_ref": str(human_authority.get("source_message_ref") or ""),
        "source_message_sha256": str(human_authority.get("source_message_sha256") or ""),
        "runtime_audit_path": str(runtime_path),
        "runtime_audit_sha256": hashlib.sha256(runtime_path.read_bytes()).hexdigest() if runtime_path.exists() else "",
        "runtime_contract_sha256": runtime_contract_sha,
        "runtime_infrastructure_ready": runtime_audit.get("runtime_infrastructure_ready") is True,
        "provider_credential_ready": runtime_audit.get("provider_credential_ready") is True,
        "single_attempt": human_authority.get("single_attempt") is True,
        "provider_price_rechecked_at_review": human_authority.get("provider_price_rechecked_at_review") is True,
        "provider_price_source": str(human_authority.get("provider_price_source") or ""),
        "secret_values_recorded": False,
        "model_calls_executed": 0,
        "task_trials_executed": 0,
        "scientific_authority": False,
        "errors": errors,
    }
    state["capability_sha256"] = _canonical_sha({k: v for k, v in state.items() if k != "capability_sha256"})
    return state


def validate_execution_capability_receipt(
    state: dict[str, Any],
    *,
    revalidate_external_authority: bool = True,
    revalidate_experiment_authority: bool = True,
) -> list[str]:
    errors: list[str] = []
    if not state:
        return ["missing-execution-capability"]
    if state.get("idea_id") != CANDIDATE_ID:
        errors.append("capability-candidate-drift")
    if state.get("plan_hash") != build_plan()["plan_sha256"]:
        errors.append("capability-plan-drift")
    if state.get("server_id") != SERVER_ID:
        errors.append("capability-server-drift")
    if state.get("execution_kind") != EXECUTION_KIND:
        errors.append("capability-execution-kind-drift")
    if state.get("requires_gpu") is not False or list(state.get("gpu_lease_ids") or []):
        errors.append("PA-05 capability must remain non-GPU")
    if list(state.get("resource_lease_ids") or []):
        errors.append("generic resource lease ids cannot authorize PA-05")
    if state.get("runtime_contract_sha256") != EXPECTED_RUNTIME_CONTRACT_SHA256:
        errors.append("capability-runtime-contract-drift")
    if state.get("secret_values_recorded") is not False:
        errors.append("execution capability must not record secrets")
    if int(state.get("model_calls_executed") or 0) != 0 or int(state.get("task_trials_executed") or 0) != 0:
        errors.append("execution capability must remain pre-model and pre-trial")
    if state.get("scientific_authority") is not False:
        errors.append("execution capability cannot carry scientific authority")

    valid = state.get("valid") is True
    controller_verified = state.get("controller_verified") is True
    if valid != controller_verified:
        errors.append("capability valid/controller_verified drift")
    if valid:
        if state.get("authority_kind") != "controller-experiment-authority-backed-by-external-human-permit":
            errors.append("valid capability lacks controller experiment authority kind")
        if not str(state.get("authority_id") or ""):
            errors.append("valid capability lacks experiment authority id")
        if not str(state.get("run_id") or ""):
            errors.append("valid capability lacks run id")
        if not str(state.get("experiment_authority_root") or ""):
            errors.append("valid capability lacks experiment authority root")
        if state.get("runtime_infrastructure_ready") is not True:
            errors.append("valid capability lacks runtime infrastructure")
        if state.get("provider_credential_ready") is not True:
            errors.append("valid capability lacks provider credential")
        if state.get("single_attempt") is not True:
            errors.append("valid capability must be single-attempt")
        if state.get("provider_price_rechecked_at_review") is not True or not str(state.get("provider_price_source") or "").strip():
            errors.append("valid capability lacks provider price recheck evidence")
        if list(state.get("errors") or []):
            errors.append("valid capability cannot contain errors")

    if revalidate_external_authority and str(state.get("human_authority_artifact_path") or ""):
        human_authority = load_human_authority(str(state["human_authority_artifact_path"]))
        if human_authority.get("bounded_f0_execution_authorized") is not True:
            errors.append("capability external human authority no longer validates")
        if str(human_authority.get("artifact_sha256") or "") != str(state.get("human_authority_artifact_sha256") or ""):
            errors.append("capability human authority artifact digest drift")
    elif valid and revalidate_external_authority:
        errors.append("valid capability lacks revalidatable external human authority path")

    if revalidate_experiment_authority and str(state.get("experiment_authority_root") or "") and str(state.get("authority_id") or ""):
        experiment = validate_authority(
            Path(str(state["experiment_authority_root"])),
            CANDIDATE_ID,
            str(state["authority_id"]),
            build_plan()["plan_sha256"],
        )
        row = experiment.get("authority") or {}
        if experiment.get("valid") is not True:
            errors.append("capability experiment authority is not active")
        if str(row.get("run_id") or "") != str(state.get("run_id") or ""):
            errors.append("capability experiment authority run drift")
        if state.get("experiment_authority_epoch") != row.get("authority_epoch"):
            errors.append("capability experiment authority epoch drift")
    elif valid and revalidate_experiment_authority:
        errors.append("valid capability lacks revalidatable experiment authority")

    expected_sha = _canonical_sha({k: v for k, v in state.items() if k != "capability_sha256"})
    if state.get("capability_sha256") != expected_sha:
        errors.append("execution capability receipt hash mismatch")
    return errors


def load_execution_capability(path: str | Path | None = None) -> dict[str, Any]:
    raw_path = str(path or os.environ.get(CAPABILITY_ENV, "")).strip()
    capability_path = Path(raw_path).expanduser() if raw_path else default_capability_path()
    if not capability_path.exists():
        return {}
    state = _load_json(capability_path)
    if validate_execution_capability_receipt(state):
        return {}
    return state


def write_execution_capability(
    *,
    human_authority_path: str | Path,
    run_id: str,
    authority_root: str | Path,
    experiment_authority_id: str,
    runtime_audit_path: str | Path = RUNTIME_AUDIT_JSON,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    human_authority = load_human_authority(human_authority_path)
    runtime_path = Path(runtime_audit_path)
    runtime_audit = _load_json(runtime_path)
    state = build_execution_capability(
        human_authority=human_authority,
        runtime_audit=runtime_audit,
        run_id=run_id,
        authority_root=authority_root,
        experiment_authority_id=experiment_authority_id,
        runtime_audit_path=runtime_path,
    )
    destination = Path(output_path) if output_path else default_capability_path()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return state
