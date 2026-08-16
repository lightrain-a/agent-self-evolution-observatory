from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any


AUTHORITY_ENV = "PAPER_FIRST_FRESH_F0_HUMAN_AUTHORITY"
AUTHORITY_TYPE = "human-paper-first-fresh-f0-execution"
CANDIDATE_ID = "PA-01-EVIDENCE-ECHO"
CONTRACT_VERSION = "evidence-echo-f0-v2-full-prompt-parity"
EXPECTED_RUNTIME_SHA256 = "f64ae7c42f5e02b2f18abd67e4a784e3790b3c75107a4140666d9faa1c39842e"
EXPECTED_REPAIR_SHA256 = "8965c54594356a87e642ebe3cc4cd76eb899ece5e6436eb96f097d09473aad30"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_REPO_ROOT = Path(__file__).resolve().parents[1]


def _no_authority(errors: list[str] | None = None) -> dict[str, Any]:
    return {
        "bounded_f0_execution_authorized": False,
        "gpu_lease_authorized": False,
        "single_attempt": False,
        "candidate_id": "",
        "contract_version": "",
        "runtime_sha256": "",
        "operationalization_repair_sha256": "",
        "problem_gate_authorized": False,
        "paper_design_authorized": False,
        "method_authorized": False,
        "p0_authorized": False,
        "full_experiment_authorized": False,
        "authority_status": "NO_EXPLICIT_USER_FRESH_F0_EXECUTION_AUTHORITY",
        "artifact_path": "",
        "artifact_sha256": "",
        "source_message_ref": "",
        "source_message_sha256": "",
        "errors": list(errors or []),
        "rule": (
            "Fresh-phenomenon F0 execution is fail-closed. A valid external human permit may authorize exactly one bounded "
            "technical execution and its matching GPU lease, but never Problem-Gate, Paper Design, Method, P0, or full-experiment authority."
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
        "runtime_sha256",
        "operationalization_repair_sha256",
        "bounded_f0_execution_authorized",
        "gpu_lease_authorized",
        "single_attempt",
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
    runtime_sha = str(payload.get("runtime_sha256") or "").lower()
    repair_sha = str(payload.get("operationalization_repair_sha256") or "").lower()
    if not _SHA256_RE.fullmatch(source_sha):
        errors.append("invalid-source-message-sha256")
    if not _SHA256_RE.fullmatch(runtime_sha):
        errors.append("invalid-runtime-sha256")
    if not _SHA256_RE.fullmatch(repair_sha):
        errors.append("invalid-operationalization-repair-sha256")

    if str(payload.get("candidate_id") or "") != CANDIDATE_ID:
        errors.append("candidate-not-covered")
    if str(payload.get("contract_version") or "") != CONTRACT_VERSION:
        errors.append("contract-version-mismatch")
    if runtime_sha != EXPECTED_RUNTIME_SHA256:
        errors.append("runtime-sha256-mismatch")
    if repair_sha != EXPECTED_REPAIR_SHA256:
        errors.append("operationalization-repair-sha256-mismatch")

    bounded = payload.get("bounded_f0_execution_authorized") is True
    gpu = payload.get("gpu_lease_authorized") is True
    single_attempt = payload.get("single_attempt") is True
    if not bounded:
        errors.append("bounded-f0-execution-not-authorized")
    if not gpu:
        errors.append("gpu-lease-not-authorized")
    if not single_attempt:
        errors.append("single-attempt-required")

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
                "candidate_id": str(payload.get("candidate_id") or ""),
                "contract_version": str(payload.get("contract_version") or ""),
                "runtime_sha256": runtime_sha,
                "operationalization_repair_sha256": repair_sha,
            }
        )
        return row

    return {
        "bounded_f0_execution_authorized": True,
        "gpu_lease_authorized": True,
        "single_attempt": True,
        "candidate_id": CANDIDATE_ID,
        "contract_version": CONTRACT_VERSION,
        "runtime_sha256": runtime_sha,
        "operationalization_repair_sha256": repair_sha,
        "problem_gate_authorized": False,
        "paper_design_authorized": False,
        "method_authorized": False,
        "p0_authorized": False,
        "full_experiment_authorized": False,
        "authority_status": "EXTERNAL_HUMAN_FRESH_F0_EXECUTION_AUTHORITY_VALID",
        "artifact_path": str(authority_path),
        "artifact_sha256": artifact_sha,
        "source_message_ref": str(payload["source_message_ref"]),
        "source_message_sha256": source_sha,
        "reviewed_at": str(payload["reviewed_at"]),
        "errors": [],
        "rule": (
            "This permit authorizes one bounded PA-01 Evidence Echo F0 execution plus its matching technical GPU lease only. "
            "Scientific promotion remains controlled by the preregistered F0 reductions and later independent gates."
        ),
    }


def require_bounded_f0_execution_authority(
    *,
    authority: dict[str, Any] | None = None,
    candidate_id: str = CANDIDATE_ID,
    contract_version: str = CONTRACT_VERSION,
    runtime_sha256: str = EXPECTED_RUNTIME_SHA256,
    operationalization_repair_sha256: str = EXPECTED_REPAIR_SHA256,
) -> dict[str, Any]:
    authority = authority or load_human_authority()
    if authority.get("bounded_f0_execution_authorized") is not True or authority.get("gpu_lease_authorized") is not True:
        raise RuntimeError("fresh F0 execution is locked: valid external human execution authority is required")
    expected = {
        "candidate_id": candidate_id,
        "contract_version": contract_version,
        "runtime_sha256": runtime_sha256,
        "operationalization_repair_sha256": operationalization_repair_sha256,
    }
    for key, value in expected.items():
        if str(authority.get(key) or "") != str(value):
            raise RuntimeError(f"fresh F0 execution authority binding mismatch: {key}")
    if authority.get("single_attempt") is not True:
        raise RuntimeError("fresh F0 execution authority requires single_attempt=true")
    for key in (
        "problem_gate_authorized",
        "paper_design_authorized",
        "method_authorized",
        "p0_authorized",
        "full_experiment_authorized",
    ):
        if authority.get(key) is not False:
            raise RuntimeError(f"fresh F0 execution authority illegally expands downstream scope: {key}")
    return authority
