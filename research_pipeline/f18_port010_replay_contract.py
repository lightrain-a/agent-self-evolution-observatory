from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = PROJECT_ROOT / "generated" / "paper-first-pre-f0-evidence-acquisition-plan.json"

FAILURE_ID = "F18"
RESEARCH_OBJECT_ID = "PORT-010"
EXPECTED_TITLE = "Complex-description boundary in end-to-end 3D world construction"
EXPECTED_HOLD = "HOLD_EVIDENCE_REVIEW_BLOCKED"
EXPECTED_REVIEW = "BLOCK_BAKE_IN"
ZERO_AUTHORITY_CLASS = "ZERO_AUTHORITY"


def _sha256_json(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _load_plan(path: Path = PLAN_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _current_row(plan: dict[str, Any]) -> dict[str, Any]:
    rows = [row for row in plan.get("entries") or [] if row.get("candidate_id") == RESEARCH_OBJECT_ID]
    if len(rows) != 1:
        raise ValueError(f"expected exactly one current {RESEARCH_OBJECT_ID} row, got {len(rows)}")
    row = rows[0]
    # PORT-010 has been reused historically. Candidate id alone is not an object identity.
    if row.get("title") != EXPECTED_TITLE:
        raise ValueError("PORT-010 id collision: current row is not the frozen VWE research object")
    return row


def build_binding(plan: dict[str, Any] | None = None) -> dict[str, Any]:
    plan = deepcopy(plan) if plan is not None else _load_plan()
    row = _current_row(plan)
    review = row.get("evidence_review") or {}
    adjudication = row.get("release_change_adjudication") or {}
    watch = row.get("release_watch_contract") or {}
    targets = watch.get("targets") or []
    if len(targets) != 1:
        raise ValueError("PORT-010 release watch must have exactly one frozen first-party target")
    target = targets[0]

    f0_material = {
        "candidate_id": row.get("candidate_id"),
        "candidate_snapshot_sha256": watch.get("candidate_snapshot_sha256"),
        "title": row.get("title"),
        "status": row.get("status"),
        "evidence_review_verdict": review.get("verdict"),
        "release_watch_contract_sha256": watch.get("contract_sha256"),
        "source_ref": target.get("source_ref"),
        "source_url": target.get("url"),
        "source_revision": target.get("baseline_revision"),
        "required_reopen_components": adjudication.get("required_reopen_components"),
        "materialized_reopen_components": adjudication.get("materialized_reopen_components"),
        "remaining_reopen_components": adjudication.get("remaining_reopen_components"),
    }
    f0_sha256 = _sha256_json(f0_material)
    authority_source = (
        f"PORT-010:VWE:{watch.get('candidate_snapshot_sha256')}@"
        f"{watch.get('contract_sha256')}"
    )
    return {
        "schema_version": "f18-port010-replay-contract-v1",
        "failure": {
            "failure_id": FAILURE_ID,
            "failure_observation": "source-specific evidence/replay cannot create the authority required to validate itself",
            "replay_request": "reproduce only the frozen zero-modification reference state and record deltas",
            "linked_research_object": RESEARCH_OBJECT_ID,
            "replay_outcome": "UNEXECUTED",
            "may_create_authority": False,
        },
        "research_object": {
            "candidate_id": RESEARCH_OBJECT_ID,
            "title": row.get("title"),
            "candidate_snapshot_sha256": watch.get("candidate_snapshot_sha256"),
            "problem_definition": (row.get("source_specific_design") or {}).get("reproduction_target"),
            "source_artifact": {
                "source_ref": target.get("source_ref"),
                "url": target.get("url"),
                "frozen_revision": target.get("baseline_revision"),
                "release_watch_contract_sha256": watch.get("contract_sha256"),
            },
            "authorization_scope": {
                "authority_class": adjudication.get("authority_class"),
                "authority_source": authority_source,
                "offline_replay_tier_authorized": adjudication.get("offline_replay_tier_authorized"),
                "provider_authority": adjudication.get("provider_authority"),
                "gpu_authority": adjudication.get("gpu_authority"),
                "scientific_execution_authority": adjudication.get("scientific_execution_authority"),
                "scientific_authority": row.get("scientific_authority"),
            },
            "replay_eligibility": {
                "local_rollout_as_author_outcome": adjudication.get("local_rollout_as_author_outcome"),
                "required_reopen_components": adjudication.get("required_reopen_components"),
                "materialized_reopen_components": adjudication.get("materialized_reopen_components"),
                "remaining_reopen_components": adjudication.get("remaining_reopen_components"),
            },
        },
        "exact_f0": {
            "definition": "frozen replayable zero-modification reference state; never a best-baseline selector",
            "material": f0_material,
            "sha256": f0_sha256,
            "mutation_from_replay_allowed": False,
        },
        "scientific_state": {
            "status": row.get("status"),
            "evidence_review_verdict": review.get("verdict"),
            "scientific_release": "HOLD",
        },
    }


def validate_binding(binding: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    failure = binding.get("failure") or {}
    obj = binding.get("research_object") or {}
    scope = obj.get("authorization_scope") or {}
    replay = obj.get("replay_eligibility") or {}
    f0 = binding.get("exact_f0") or {}
    science = binding.get("scientific_state") or {}

    if failure.get("failure_id") != FAILURE_ID or failure.get("linked_research_object") != RESEARCH_OBJECT_ID:
        errors.append("F18 must bind exactly to PORT-010")
    if failure.get("may_create_authority") is not False:
        errors.append("F18 cannot create authority")
    if obj.get("candidate_id") != RESEARCH_OBJECT_ID or obj.get("title") != EXPECTED_TITLE:
        errors.append("PORT-010 object identity/scope mismatch")
    if not str(obj.get("candidate_snapshot_sha256") or "").strip():
        errors.append("PORT-010 candidate snapshot provenance missing")
    source = obj.get("source_artifact") or {}
    for key in ("source_ref", "url", "frozen_revision", "release_watch_contract_sha256"):
        if not str(source.get(key) or "").strip():
            errors.append(f"source artifact provenance missing: {key}")
    if scope.get("authority_class") != ZERO_AUTHORITY_CLASS:
        errors.append("PORT-010 authority class must remain ZERO_AUTHORITY")
    for key in ("offline_replay_tier_authorized", "provider_authority", "gpu_authority", "scientific_execution_authority", "scientific_authority"):
        if scope.get(key) is not False:
            errors.append(f"zero-authority inversion: {key}")
    if not str(scope.get("authority_source") or "").startswith("PORT-010:VWE:"):
        errors.append("authority_source must bind the external frozen PORT-010 VWE contract")
    if replay.get("local_rollout_as_author_outcome") != "PROHIBITED":
        errors.append("local replay cannot be represented as author-released outcome")
    if f0.get("mutation_from_replay_allowed") is not False:
        errors.append("exact-F0 must be immutable under replay")
    if _sha256_json(f0.get("material")) != f0.get("sha256"):
        errors.append("exact-F0 content hash mismatch")
    if science.get("status") != EXPECTED_HOLD or science.get("evidence_review_verdict") != EXPECTED_REVIEW:
        errors.append("frozen scientific HOLD/review state drifted")
    if science.get("scientific_release") != "HOLD":
        errors.append("system validation cannot auto-release the scientific object")
    return errors


def validate_replay_receipt(
    binding: dict[str, Any],
    receipt: dict[str, Any],
    artifact_root: Path = PROJECT_ROOT,
) -> dict[str, Any]:
    errors = validate_binding(binding)
    scope = (binding.get("research_object") or {}).get("authorization_scope") or {}
    exact_f0 = binding.get("exact_f0") or {}

    if receipt.get("failure_id") != FAILURE_ID or receipt.get("candidate_id") != RESEARCH_OBJECT_ID:
        errors.append("receipt identity mismatch")
    if receipt.get("candidate_snapshot_sha256") != (binding.get("research_object") or {}).get("candidate_snapshot_sha256"):
        errors.append("receipt candidate snapshot mismatch")
    if receipt.get("exact_f0_sha256") != exact_f0.get("sha256"):
        errors.append("receipt is not an exact-F0 replay")
    authority_binding_violation = receipt.get("authority_source") != scope.get("authority_source")
    if authority_binding_violation:
        errors.append("receipt authority_source is not the frozen external contract")
    canonical_review = (binding.get("scientific_state") or {}).get("evidence_review_verdict")
    if receipt.get("evidence_review_status") != canonical_review:
        errors.append("receipt evidence review status cannot override canonical review")
    authority_violation = False
    if receipt.get("authority") is True:
        authority_violation = True
        errors.append("receipt cannot self-authorize")
    authority = receipt.get("authority")
    if isinstance(authority, dict) and any(value is not False for value in authority.values()):
        authority_violation = True
        errors.append("receipt carries non-zero authority")

    artifacts = receipt.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        errors.append("replay artifact provenance missing")
    else:
        for index, artifact in enumerate(artifacts):
            if not isinstance(artifact, dict):
                errors.append(f"artifact[{index}] malformed")
                continue
            relpath = str(artifact.get("path") or "").strip()
            expected_sha = str(artifact.get("sha256") or "").strip()
            if not relpath or not expected_sha:
                errors.append(f"artifact[{index}] path/hash provenance missing")
            else:
                path = (artifact_root / relpath).resolve()
                try:
                    path.relative_to(artifact_root.resolve())
                except ValueError:
                    errors.append(f"artifact[{index}] escapes artifact root")
                else:
                    if not path.is_file():
                        errors.append(f"artifact[{index}] does not exist")
                    elif hashlib.sha256(path.read_bytes()).hexdigest() != expected_sha:
                        errors.append(f"artifact[{index}] content hash mismatch")
            provenance = artifact.get("provenance") or {}
            if not str(provenance.get("frozen_ref") or "").strip():
                errors.append(f"artifact[{index}] frozen provenance missing")
            if provenance.get("generated_by_replay") is not True:
                errors.append(f"artifact[{index}] must declare replay generation provenance")

    replay_pass = receipt.get("replay_status") == "PASS"
    evidence_review_pass = receipt.get("evidence_review_status") == "PASS"
    scientific_release = "RELEASED" if replay_pass and evidence_review_pass and not errors else "HOLD"
    # Current PORT-010 is BLOCK_BAKE_IN. A receipt cannot overwrite the canonical review verdict.
    if (binding.get("scientific_state") or {}).get("evidence_review_verdict") != "PASS":
        scientific_release = "HOLD"
    return {
        "F18_PORT010_BINDING_PASS": not validate_binding(binding),
        "receipt_integrity": "PASS" if not errors else "REJECT",
        "exact_F0_replay": "PASS" if receipt.get("exact_f0_sha256") == exact_f0.get("sha256") else "REJECT",
        "zero_authority_check": "REJECT" if (authority_violation or authority_binding_violation) else "PASS",
        "hold_preservation": "PASS" if scientific_release == "HOLD" else "REJECT",
        "scientific_release": scientific_release,
        "errors": errors,
    }
