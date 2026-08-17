from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

from .paper_first_skill_validation_transfer_f0 import (
    CANDIDATE_ID,
    CONTRACT_VERSION,
    SOURCE_COMMIT,
    build_plan,
)

AUTHORITY_ENV = "PAPER_FIRST_SKILL_VALIDATION_TRANSFER_F0_HUMAN_AUTHORITY"
AUTHORITY_TYPE = "human-paper-first-skill-validation-transfer-f0-execution"
SERVER_ID = "52"
EXPECTED_PLAN_SHA256 = build_plan()["plan_sha256"]
EXPECTED_F0_HARNESS_SHA256 = "daaad83e507806a66c1c4dd5911c40b8db5781df4cd22b8f44916e228d4e224c"
EXPECTED_RUNTIME_CONTRACT_SHA256 = "82c2755d937b67f15b9d09fe65343ce717146cd87c88aca1513e409df95ddb7f"
EXPECTED_SOURCE_TREE_SHA256 = "a73332f07cdb0863b748ad26797a0491af2ae27f7ff5c164c1d637985cc04f02"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_REPO_ROOT = Path(__file__).resolve().parents[1]


def _no_authority(errors: list[str] | None = None) -> dict[str, Any]:
    return {
        "bounded_f0_execution_authorized": False,
        "api_docker_execution_authorized": False,
        "provider_credential_use_authorized": False,
        "gpu_lease_authorized": False,
        "single_attempt": False,
        "provider_price_rechecked_at_review": False,
        "provider_price_source": "",
        "candidate_id": "",
        "contract_version": "",
        "plan_sha256": "",
        "f0_harness_sha256": "",
        "runtime_contract_sha256": "",
        "source_tree_sha256": "",
        "source_commit": "",
        "server_id": "",
        "problem_gate_authorized": False,
        "paper_design_authorized": False,
        "method_authorized": False,
        "p0_authorized": False,
        "full_experiment_authorized": False,
        "authority_status": "NO_EXPLICIT_USER_SKILL_VALIDATION_TRANSFER_F0_EXECUTION_AUTHORITY",
        "artifact_path": "",
        "artifact_sha256": "",
        "source_message_ref": "",
        "source_message_sha256": "",
        "errors": list(errors or []),
        "rule": (
            "PA-05 execution is fail-closed. A valid external human permit may authorize exactly one bounded "
            "API/Docker F0 attempt on the frozen host/runtime/plan and use of the configured Gemini credential, "
            "but never Problem-Gate, Paper Design, Method, P0, GPU, or full-experiment authority."
        ),
    }


def load_human_authority(path: str | Path | None = None) -> dict[str, Any]:
    raw_path = str(path or os.environ.get(AUTHORITY_ENV, "")).strip()
    if not raw_path:
        return _no_authority([f"missing-external-authority:{AUTHORITY_ENV}"])

    authority_path = Path(raw_path).expanduser().resolve()
    errors: list[str] = []
    try:
        authority_path.relative_to(_REPO_ROOT)
        errors.append("authority-artifact-must-be-external-to-repository")
    except ValueError:
        pass

    try:
        raw = authority_path.read_bytes()
        payload = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        return _no_authority(errors + [f"authority-artifact-unreadable:{type(error).__name__}"])
    if not isinstance(payload, dict):
        return _no_authority(errors + ["authority-artifact-root-must-be-object"])

    required = (
        "authority_type",
        "decision",
        "reviewed_by",
        "reviewed_at",
        "source_message_ref",
        "source_message_sha256",
        "candidate_id",
        "contract_version",
        "plan_sha256",
        "f0_harness_sha256",
        "runtime_contract_sha256",
        "source_tree_sha256",
        "source_commit",
        "server_id",
        "bounded_f0_execution_authorized",
        "api_docker_execution_authorized",
        "provider_credential_use_authorized",
        "gpu_lease_authorized",
        "single_attempt",
        "provider_price_rechecked_at_review",
        "provider_price_source",
        "problem_gate_authorized",
        "paper_design_authorized",
        "method_authorized",
        "p0_authorized",
        "full_experiment_authorized",
    )
    for key in required:
        if key not in payload:
            errors.append(f"missing:{key}")

    if payload.get("authority_type") != AUTHORITY_TYPE:
        errors.append("invalid-authority-type")
    if payload.get("decision") != "approve":
        errors.append("decision-not-approve")
    if str(payload.get("reviewed_by") or "") not in {"user", "human-user"}:
        errors.append("reviewer-not-human-user")

    source_sha = str(payload.get("source_message_sha256") or "").lower()
    if not _SHA256_RE.fullmatch(source_sha):
        errors.append("invalid-source-message-sha256")

    expected_text = {
        "candidate_id": CANDIDATE_ID,
        "contract_version": CONTRACT_VERSION,
        "plan_sha256": EXPECTED_PLAN_SHA256,
        "f0_harness_sha256": EXPECTED_F0_HARNESS_SHA256,
        "runtime_contract_sha256": EXPECTED_RUNTIME_CONTRACT_SHA256,
        "source_tree_sha256": EXPECTED_SOURCE_TREE_SHA256,
        "source_commit": SOURCE_COMMIT,
        "server_id": SERVER_ID,
    }
    for key, expected in expected_text.items():
        if str(payload.get(key) or "") != expected:
            errors.append(f"binding-mismatch:{key}")

    for key in (
        "plan_sha256",
        "f0_harness_sha256",
        "runtime_contract_sha256",
        "source_tree_sha256",
    ):
        if not _SHA256_RE.fullmatch(str(payload.get(key) or "").lower()):
            errors.append(f"invalid-sha256:{key}")

    if payload.get("bounded_f0_execution_authorized") is not True:
        errors.append("bounded-f0-execution-not-authorized")
    if payload.get("api_docker_execution_authorized") is not True:
        errors.append("api-docker-execution-not-authorized")
    if payload.get("provider_credential_use_authorized") is not True:
        errors.append("provider-credential-use-not-authorized")
    if payload.get("gpu_lease_authorized") is not False:
        errors.append("gpu-lease-must-remain-unauthorized")
    if payload.get("single_attempt") is not True:
        errors.append("single-attempt-required")
    if payload.get("provider_price_rechecked_at_review") is not True:
        errors.append("provider-price-recheck-required-at-human-review")
    if not str(payload.get("provider_price_source") or "").strip():
        errors.append("provider-price-source-required")

    forbidden = (
        "problem_gate_authorized",
        "paper_design_authorized",
        "method_authorized",
        "p0_authorized",
        "full_experiment_authorized",
    )
    for key in forbidden:
        if payload.get(key) is not False:
            errors.append(f"forbidden-downstream-authority:{key}")

    artifact_sha = hashlib.sha256(raw).hexdigest()
    if errors:
        row = _no_authority(errors)
        row.update(
            {
                "artifact_path": str(authority_path),
                "artifact_sha256": artifact_sha,
                "source_message_ref": str(payload.get("source_message_ref") or ""),
                "source_message_sha256": source_sha,
                **{key: str(payload.get(key) or "") for key in expected_text},
            }
        )
        return row

    return {
        "bounded_f0_execution_authorized": True,
        "api_docker_execution_authorized": True,
        "provider_credential_use_authorized": True,
        "gpu_lease_authorized": False,
        "single_attempt": True,
        "provider_price_rechecked_at_review": True,
        "provider_price_source": str(payload["provider_price_source"]),
        **expected_text,
        "problem_gate_authorized": False,
        "paper_design_authorized": False,
        "method_authorized": False,
        "p0_authorized": False,
        "full_experiment_authorized": False,
        "authority_status": "EXTERNAL_HUMAN_SKILL_VALIDATION_TRANSFER_F0_EXECUTION_AUTHORITY_VALID",
        "artifact_path": str(authority_path),
        "artifact_sha256": artifact_sha,
        "source_message_ref": str(payload["source_message_ref"]),
        "source_message_sha256": source_sha,
        "reviewed_at": str(payload["reviewed_at"]),
        "errors": [],
        "rule": (
            "This permit authorizes one bounded PA-05 API/Docker seed-A F0 attempt on host 52 and use of the "
            "already configured Gemini credential only. Scientific promotion remains controlled by the frozen F0 gates."
        ),
    }


def require_bounded_f0_execution_authority(*, authority: dict[str, Any] | None = None) -> dict[str, Any]:
    authority = authority or load_human_authority()
    required_true = (
        "bounded_f0_execution_authorized",
        "api_docker_execution_authorized",
        "provider_credential_use_authorized",
        "single_attempt",
        "provider_price_rechecked_at_review",
    )
    if any(authority.get(key) is not True for key in required_true):
        raise RuntimeError("PA-05 execution is locked: valid external human execution authority is required")
    if authority.get("gpu_lease_authorized") is not False:
        raise RuntimeError("PA-05 execution authority must remain non-GPU")
    if not str(authority.get("provider_price_source") or "").strip():
        raise RuntimeError("PA-05 execution authority requires a provider price source")
    expected = {
        "candidate_id": CANDIDATE_ID,
        "contract_version": CONTRACT_VERSION,
        "plan_sha256": EXPECTED_PLAN_SHA256,
        "f0_harness_sha256": EXPECTED_F0_HARNESS_SHA256,
        "runtime_contract_sha256": EXPECTED_RUNTIME_CONTRACT_SHA256,
        "source_tree_sha256": EXPECTED_SOURCE_TREE_SHA256,
        "source_commit": SOURCE_COMMIT,
        "server_id": SERVER_ID,
    }
    for key, value in expected.items():
        if str(authority.get(key) or "") != value:
            raise RuntimeError(f"PA-05 execution authority binding mismatch: {key}")
    for key in (
        "problem_gate_authorized",
        "paper_design_authorized",
        "method_authorized",
        "p0_authorized",
        "full_experiment_authorized",
    ):
        if authority.get(key) is not False:
            raise RuntimeError(f"PA-05 execution authority illegally expands downstream scope: {key}")
    return authority
