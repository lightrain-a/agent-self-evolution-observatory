#!/usr/bin/env python3
"""Validate a bounded external human execution permit for B1/L2B.

The permit authorizes one pre-registered local execution only. It never grants
scientific claim authority, threshold changes, L3 transport, or submission.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

AUTHORITY_ENV = "B1_L2B_HUMAN_EXECUTION_AUTHORITY"
AUTHORITY_TYPE = "human-b1-l2b-bounded-execution"
PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
EXPECTED_SOURCE_MESSAGE_SHA256 = "35edf038b45e1b1048bc37d565212140b39ef307a8700b3efd4d658a7e80599f"
EXPECTED_R13_SHA256 = "ffbe9baad45ae9e79b9c3eddb8eb54bf57734d6095810e97a45d3cc4b452aa8f"
EXPECTED_R14_SHA256 = "b0743822c6fe8e06895997bacce8951b26ee00281dcaf68f9bd426920dac3507"
EXPECTED_R15_SHA256 = "707d2f630ef4a6d40f607ff156348223a424e7a76df96c6c6925747fb66b3c59"
EXPECTED_WRITER_MANIFEST = "sha256:9f13ba1299afea09d9a956fc6a85becc99115a6d596fae201a5487a03bdc4368"
EXPECTED_EXECUTOR_MANIFEST = "sha256:5bce411d829007ce344871ae10ea7f02f91d86c932617a7f982e2380bbb1c216"
_SHA = re.compile(r"^[0-9a-f]{64}$")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _deny(errors: list[str] | None = None) -> dict[str, Any]:
    return {
        "valid": False,
        "execution_authorized": False,
        "writer_generation_authorized": False,
        "downstream_l2b_authorized": False,
        "local_model_calls_authorized": False,
        "browser_actions_authorized": False,
        "evaluator_calls_authorized": False,
        "gpu_lease_authorized": False,
        "single_confirmatory_attempt": False,
        "scientific_authority": False,
        "l3_authorized": False,
        "artifact_sha256": "",
        "source_message_ref": "",
        "source_message_sha256": "",
        "errors": list(errors or []),
    }


def load_human_authority(path: str | Path | None = None, *, repo_root: Path | None = None) -> dict[str, Any]:
    raw_path = str(path or os.environ.get(AUTHORITY_ENV, "")).strip()
    if not raw_path:
        return _deny([f"missing-external-authority:{AUTHORITY_ENV}"])
    p = Path(raw_path).expanduser().resolve()
    repo_root = (repo_root or Path(__file__).resolve().parents[1]).resolve()
    errors: list[str] = []
    try:
        p.relative_to(repo_root)
        errors.append("authority-artifact-must-be-external-to-repository")
    except ValueError:
        pass
    try:
        raw = p.read_bytes()
        obj = json.loads(raw.decode("utf-8"))
    except Exception as e:
        return _deny(errors + [f"authority-artifact-unreadable:{type(e).__name__}"])
    if not isinstance(obj, dict):
        return _deny(errors + ["authority-artifact-root-must-be-object"])

    required = [
        "authority_type", "decision", "reviewed_by", "reviewed_at",
        "source_message_ref", "source_message_sha256", "paper_id",
        "r13_writer_input_sha256", "r14_writer_model_sha256", "r15_executor_contract_sha256",
        "execution_authorized", "writer_generation_authorized", "downstream_l2b_authorized",
        "local_model_calls_authorized", "browser_actions_authorized", "evaluator_calls_authorized",
        "gpu_lease_authorized", "single_confirmatory_attempt",
        "writer_request_budget", "terminal_episode_budget", "executor_completion_budget",
        "total_local_model_request_budget", "allowed_writer_manifest_digest", "allowed_executor_manifest_digest",
        "external_api_authorized", "l3_authorized", "threshold_change_authorized",
        "task_replacement_authorized", "outcome_adaptive_extension_authorized",
        "claim_expansion_authorized", "scientific_authority", "submission_authority",
    ]
    for k in required:
        if k not in obj:
            errors.append(f"missing:{k}")

    if obj.get("authority_type") != AUTHORITY_TYPE: errors.append("invalid-authority-type")
    if obj.get("decision") != "approve": errors.append("decision-not-approve")
    if str(obj.get("reviewed_by") or "") not in {"user", "human-user"}: errors.append("reviewer-not-human-user")
    if obj.get("paper_id") != PAPER_ID: errors.append("paper-id-mismatch")
    source_sha = str(obj.get("source_message_sha256") or "").lower()
    if not _SHA.fullmatch(source_sha): errors.append("invalid-source-message-sha256")
    if source_sha != EXPECTED_SOURCE_MESSAGE_SHA256: errors.append("source-message-sha256-mismatch")

    expected = {
        "r13_writer_input_sha256": EXPECTED_R13_SHA256,
        "r14_writer_model_sha256": EXPECTED_R14_SHA256,
        "r15_executor_contract_sha256": EXPECTED_R15_SHA256,
        "allowed_writer_manifest_digest": EXPECTED_WRITER_MANIFEST,
        "allowed_executor_manifest_digest": EXPECTED_EXECUTOR_MANIFEST,
        "writer_request_budget": 36,
        "terminal_episode_budget": 144,
        "executor_completion_budget": 4320,
        "total_local_model_request_budget": 4356,
    }
    for k, v in expected.items():
        if obj.get(k) != v:
            errors.append(f"binding-mismatch:{k}")

    must_true = [
        "execution_authorized", "writer_generation_authorized", "downstream_l2b_authorized",
        "local_model_calls_authorized", "browser_actions_authorized", "evaluator_calls_authorized",
        "gpu_lease_authorized", "single_confirmatory_attempt",
    ]
    for k in must_true:
        if obj.get(k) is not True: errors.append(f"required-true:{k}")
    must_false = [
        "external_api_authorized", "l3_authorized", "threshold_change_authorized",
        "task_replacement_authorized", "outcome_adaptive_extension_authorized",
        "claim_expansion_authorized", "scientific_authority", "submission_authority",
    ]
    for k in must_false:
        if obj.get(k) is not False: errors.append(f"required-false:{k}")

    artifact_sha = hashlib.sha256(raw).hexdigest()
    if errors:
        row = _deny(errors)
        row.update({"artifact_sha256": artifact_sha, "source_message_ref": str(obj.get("source_message_ref") or ""), "source_message_sha256": source_sha})
        return row
    return {
        "valid": True,
        "execution_authorized": True,
        "writer_generation_authorized": True,
        "downstream_l2b_authorized": True,
        "local_model_calls_authorized": True,
        "browser_actions_authorized": True,
        "evaluator_calls_authorized": True,
        "gpu_lease_authorized": True,
        "single_confirmatory_attempt": True,
        "scientific_authority": False,
        "l3_authorized": False,
        "artifact_path": str(p),
        "artifact_sha256": artifact_sha,
        "source_message_ref": str(obj["source_message_ref"]),
        "source_message_sha256": source_sha,
        "reviewed_at": str(obj["reviewed_at"]),
        "budgets": {k: obj[k] for k in ["writer_request_budget", "terminal_episode_budget", "executor_completion_budget", "total_local_model_request_budget"]},
        "errors": [],
    }


def require_authority(path: str | Path | None = None) -> dict[str, Any]:
    row = load_human_authority(path)
    if row.get("valid") is not True:
        raise RuntimeError("B1 L2B execution locked: valid external bounded human authority is required: " + ";".join(row.get("errors") or []))
    return row


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--authority", type=Path, default=None)
    ap.add_argument("--output", type=Path, default=Path("generated/d2-failure-memory-provenance-l2b-execution-authority-r16.json"))
    a = ap.parse_args()
    row = require_authority(a.authority)
    payload = {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-L2B-EXECUTION-AUTHORITY-R16",
        "recorded_date": "2026-08-24",
        "status": "EXTERNAL_HUMAN_BOUNDED_EXECUTION_AUTHORITY_VALID",
        "authority_artifact_sha256": row["artifact_sha256"],
        "source_message_ref": row["source_message_ref"],
        "source_message_sha256": row["source_message_sha256"],
        "reviewed_at": row["reviewed_at"],
        "bindings": {
            "r13_writer_input_sha256": EXPECTED_R13_SHA256,
            "r14_writer_model_sha256": EXPECTED_R14_SHA256,
            "r15_executor_contract_sha256": EXPECTED_R15_SHA256,
            "writer_manifest_digest": EXPECTED_WRITER_MANIFEST,
            "executor_manifest_digest": EXPECTED_EXECUTOR_MANIFEST,
        },
        "budgets": row["budgets"],
        "scope": {
            "writer_generation_authorized": True,
            "downstream_l2b_authorized": True,
            "local_model_calls_authorized": True,
            "browser_actions_authorized": True,
            "evaluator_calls_authorized": True,
            "gpu_lease_authorized": True,
            "single_confirmatory_attempt": True,
            "external_api_authorized": False,
            "l3_authorized": False,
            "threshold_change_authorized": False,
            "task_replacement_authorized": False,
            "outcome_adaptive_extension_authorized": False,
            "claim_expansion_authorized": False,
        },
        "scientific_authority": False,
        "submission_authority": False,
        "rule": "Execution permission allows exactly the preregistered bounded R13-R15 experiment. Scientific claim support remains determined only by the frozen R15 analysis gate.",
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "artifact_sha256": payload["authority_artifact_sha256"], "scientific_authority": False}))


if __name__ == "__main__":
    main()
