#!/usr/bin/env python3
"""Validate a bounded external human authority artifact for the new B1/R19 experiment.

The authority permits scientific execution under the frozen R19 contract. It does
not pre-authorize a positive/negative scientific claim, manuscript claim expansion,
L3 transport, external paid APIs, or any post-outcome design change.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
AUTHORITY_ENV = "B1_R19_HUMAN_EXECUTION_AUTHORITY"
AUTHORITY_TYPE = "human-b1-r19-bounded-scientific-execution"
EXPECTED_SOURCE_MESSAGE_SHA256 = "36c33de30c5a14be5a0902f7b7320b7b59c8e979f213f23c315ca5967d6946cd"
EXPECTED = {
    "r19_contract_sha256": "ed803f0958002ab2095563a56cff6328a054ff4c4d7bd9fc18fc97bb3bdc3282",
    "r19_readiness_sha256": "606b6f68377777ad9b9d1794df95c69d6ad3ae3005b397cbee080396ffa24133",
    "r19_claim_policy_sha256": "6c45274d59ec91865bd48b5ab4afe5358a5fe60dd57657da24cce569b87a9e86",
    "r19_authority_packet_sha256": "92a59337bb32bca7e0ffea45aed6085d447707f57fe58ddc8ac5a7a0eac80655",
    "r17_writer_realization_sha256": "58de4f998b16aace4ddfeef0693d88a347b293c032d997e0da471e6b92c69235",
    "executor_manifest_digest": "sha256:5bce411d829007ce344871ae10ea7f02f91d86c932617a7f982e2380bbb1c216",
    "independent_tasks": 35,
    "terminal_episode_budget": 140,
    "agent_completion_budget": 4200,
    "fuzzy_evaluator_completion_budget": 600,
    "synthetic_support_completion_budget": 2,
    "total_local_model_completion_budget": 4802,
}
_SHA = re.compile(r"^[0-9a-f]{64}$")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _deny(errors: list[str]) -> dict[str, Any]:
    return {
        "valid": False,
        "r19_scientific_execution_authorized": False,
        "experiment_authorized": False,
        "model_completions_authorized": False,
        "browser_actions_authorized": False,
        "evaluator_calls_authorized": False,
        "gpu_authorized": False,
        "scientific_claim_authority": False,
        "l3_authorized": False,
        "errors": errors,
    }


def load_authority(path: str | Path | None = None, *, repo_root: Path | None = None) -> dict[str, Any]:
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
    except Exception as exc:
        return _deny(errors + [f"authority-artifact-unreadable:{type(exc).__name__}"])
    if not isinstance(obj, dict):
        return _deny(errors + ["authority-artifact-root-must-be-object"])

    required = [
        "authority_type", "decision", "reviewed_by", "reviewed_at", "source_message_ref",
        "source_message_sha256", "paper_id", *EXPECTED.keys(),
        "r19_scientific_execution_authorized", "experiment_authorized",
        "model_completions_authorized", "browser_actions_authorized",
        "evaluator_calls_authorized", "gpu_authorized", "single_confirmatory_attempt",
        "external_api_authorized", "r18_retry_authorized", "l3_authorized",
        "task_replacement_authorized", "memory_regeneration_authorized",
        "model_or_provider_switch_authorized", "threshold_change_authorized",
        "endpoint_change_authorized", "statistical_change_authorized",
        "outcome_adaptive_extension_authorized", "claim_expansion_authorized",
        "scientific_claim_authority", "submission_authority",
    ]
    for key in required:
        if key not in obj:
            errors.append(f"missing:{key}")

    if obj.get("authority_type") != AUTHORITY_TYPE:
        errors.append("invalid-authority-type")
    if obj.get("decision") != "approve":
        errors.append("decision-not-approve")
    if str(obj.get("reviewed_by") or "") not in {"user", "human-user"}:
        errors.append("reviewer-not-human-user")
    if obj.get("paper_id") != PAPER_ID:
        errors.append("paper-id-mismatch")
    source_sha = str(obj.get("source_message_sha256") or "").lower()
    if not _SHA.fullmatch(source_sha):
        errors.append("invalid-source-message-sha256")
    if source_sha != EXPECTED_SOURCE_MESSAGE_SHA256:
        errors.append("source-message-sha256-mismatch")

    for key, value in EXPECTED.items():
        if obj.get(key) != value:
            errors.append(f"binding-mismatch:{key}")

    for key in [
        "r19_scientific_execution_authorized", "experiment_authorized",
        "model_completions_authorized", "browser_actions_authorized",
        "evaluator_calls_authorized", "gpu_authorized", "single_confirmatory_attempt",
    ]:
        if obj.get(key) is not True:
            errors.append(f"required-true:{key}")
    for key in [
        "external_api_authorized", "r18_retry_authorized", "l3_authorized",
        "task_replacement_authorized", "memory_regeneration_authorized",
        "model_or_provider_switch_authorized", "threshold_change_authorized",
        "endpoint_change_authorized", "statistical_change_authorized",
        "outcome_adaptive_extension_authorized", "claim_expansion_authorized",
        "scientific_claim_authority", "submission_authority",
    ]:
        if obj.get(key) is not False:
            errors.append(f"required-false:{key}")

    artifact_sha = hashlib.sha256(raw).hexdigest()
    if errors:
        out = _deny(errors)
        out.update({"artifact_sha256": artifact_sha, "source_message_sha256": source_sha})
        return out
    return {
        "valid": True,
        "r19_scientific_execution_authorized": True,
        "experiment_authorized": True,
        "model_completions_authorized": True,
        "browser_actions_authorized": True,
        "evaluator_calls_authorized": True,
        "gpu_authorized": True,
        "single_confirmatory_attempt": True,
        "scientific_claim_authority": False,
        "l3_authorized": False,
        "artifact_path": str(p),
        "artifact_sha256": artifact_sha,
        "source_message_ref": str(obj["source_message_ref"]),
        "source_message_sha256": source_sha,
        "reviewed_at": str(obj["reviewed_at"]),
        "budgets": {k: obj[k] for k in [
            "independent_tasks", "terminal_episode_budget", "agent_completion_budget",
            "fuzzy_evaluator_completion_budget", "synthetic_support_completion_budget",
            "total_local_model_completion_budget",
        ]},
        "errors": [],
    }


def require_authority(path: str | Path | None = None) -> dict[str, Any]:
    row = load_authority(path)
    if row.get("valid") is not True:
        raise RuntimeError("B1 R19 execution locked: " + ";".join(row.get("errors") or []))
    return row


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--authority", type=Path, default=None)
    ap.add_argument("--output", type=Path, default=Path("generated/d2-failure-memory-provenance-l2b-r19-execution-authority-r21.json"))
    a = ap.parse_args()
    row = require_authority(a.authority)
    payload = {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-L2B-R19-EXECUTION-AUTHORITY-R21",
        "recorded_date": "2026-08-24",
        "status": "R19_EXTERNAL_HUMAN_BOUNDED_SCIENTIFIC_EXECUTION_AUTHORITY_VALID",
        "authority_artifact_sha256": row["artifact_sha256"],
        "source_message_ref": row["source_message_ref"],
        "source_message_sha256": row["source_message_sha256"],
        "reviewed_at": row["reviewed_at"],
        "bindings": {k: EXPECTED[k] for k in [
            "r19_contract_sha256", "r19_readiness_sha256", "r19_claim_policy_sha256",
            "r19_authority_packet_sha256", "r17_writer_realization_sha256", "executor_manifest_digest",
        ]},
        "budgets": row["budgets"],
        "scope": {
            "r19_scientific_execution_authorized": True,
            "experiment_authorized": True,
            "model_completions_authorized": True,
            "browser_actions_authorized": True,
            "evaluator_calls_authorized": True,
            "gpu_authorized": True,
            "single_confirmatory_attempt": True,
            "external_api_authorized": False,
            "r18_retry_authorized": False,
            "l3_authorized": False,
            "task_replacement_authorized": False,
            "memory_regeneration_authorized": False,
            "model_or_provider_switch_authorized": False,
            "threshold_change_authorized": False,
            "endpoint_change_authorized": False,
            "statistical_change_authorized": False,
            "outcome_adaptive_extension_authorized": False,
            "claim_expansion_authorized": False,
        },
        "scientific_claim_authority": False,
        "submission_authority": False,
        "rule": "This authority permits exactly one R19 scientific execution under the frozen R19 contract. Scientific claim support remains determined only by the pre-outcome R19 claim-impact policy.",
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "artifact_sha256": payload["authority_artifact_sha256"], "scientific_claim_authority": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
