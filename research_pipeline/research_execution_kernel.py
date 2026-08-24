from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = "1.0"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
GIT_REV = re.compile(r"^[0-9a-f]{7,64}$")
REOPEN_GATED_STATES = {"HOLD", "STOPPED", "MERGED", "PAPER_READY"}

POLICY: dict[str, Any] = {
    "schema_version": SCHEMA_VERSION,
    "research_state_is_recoverable_snapshot_not_scientific_authority": True,
    "execution_resume_requires_identical_execution_identity": True,
    "scientific_reopen_requires_recorded_reopen_condition_and_new_evidence": True,
    "reanchor_never_grants_scientific_experiment_p0_or_gpu_authority": True,
    "hold_stop_merge_and_paper_handoff_cannot_be_bypassed_by_state_rollback": True,
    "experiment_manifest_is_frozen_before_outcome_reads": True,
    "smoke_pilot_full_are_distinct_escalation_phases": True,
    "full_phase_never_follows_positive_pilot_automatically": True,
    "atomic_unit_is_persisted_before_next_unit_starts": True,
    "resume_restarts_only_incomplete_units_under_identical_identity": True,
    "planner_freezes_scientific_contract_executor_only_executes_it": True,
    "executor_receipt_cannot_self_acquit_scientific_validity": True,
    "evaluator_and_secret_surfaces_must_not_be_executor_writable": True,
    "metacognition_compares_intent_protocol_evidence_and_claim_before_transition": True,
    "infrastructure_and_support_failures_cannot_be_relabelled_as_scientific_negatives": True,
    "raw_chain_of_thought_is_not_required_or_persisted": True,
}

REFERENCES = [
    {"system": "ScienceFlow", "adopted": "recoverable executable research state and bounded re-anchoring"},
    {"system": "AutoResearchEval / ARFT", "adopted": "metacognitive transition checks and process-level failure typing"},
    {"system": "EurekAgent", "adopted": "permission, artifact, budget, and evaluator-surface environment contracts"},
    {"system": "TeLLAgent", "adopted": "planner/executor separation with explicit execution receipts"},
    {"system": "Claw AI Lab", "adopted": "artifact inspection plus rollback/resume without rewriting prior artifacts"},
    {"system": "AI Scientist / AI Scientist-v2", "adopted": "staged experiment progression without outcome-driven scientific selection"},
]


def canonical_sha256(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _phases(spec: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    out = {
        "smoke": {"required": True, "automatic_promotion": False},
        "pilot": {"required": True, "automatic_promotion": False},
        "full": {"required": True, "automatic_promotion": False},
    }
    for name, values in (spec or {}).items():
        if name in out and isinstance(values, dict):
            out[name].update(values)
            out[name]["automatic_promotion"] = False
    return out


def build_experiment_manifest(
    *, experiment_id: str, research_item_code: str, scientific_object: str,
    hypothesis: str, decisive_test: str, primary_metric: str,
    strongest_baseline: str, controls: Iterable[str], task_snapshot: Any,
    model_provider: str, seeds: Iterable[int], code_commit: str,
    config_sha256: str, runtime_sha256: str, unit_ids: Iterable[str],
    estimated_cost: dict[str, Any] | None = None,
    stop_conditions: Iterable[str] | None = None, artifact_root: str = "",
    phases: dict[str, Any] | None = None,
) -> dict[str, Any]:
    scientific_contract = {
        "research_item_code": str(research_item_code),
        "scientific_object": str(scientific_object),
        "hypothesis": str(hypothesis),
        "decisive_test": str(decisive_test),
        "primary_metric": str(primary_metric),
        "strongest_baseline": str(strongest_baseline),
        "controls": [str(value) for value in controls],
    }
    execution_identity = {
        "code_commit": str(code_commit),
        "config_sha256": str(config_sha256),
        "runtime_sha256": str(runtime_sha256),
        "task_snapshot_sha256": canonical_sha256(task_snapshot),
    }
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": str(experiment_id),
        "research_item_code": str(research_item_code),
        "scientific_contract": scientific_contract,
        "scientific_contract_sha256": canonical_sha256(scientific_contract),
        "task_snapshot": task_snapshot,
        "model_provider": str(model_provider),
        "seeds": [int(value) for value in seeds],
        "execution_identity": execution_identity,
        "execution_identity_sha256": canonical_sha256(execution_identity),
        "unit_ids": [str(value) for value in unit_ids],
        "estimated_cost": dict(estimated_cost or {}),
        "stop_conditions": [str(value) for value in (stop_conditions or [])],
        "artifact_root": str(artifact_root),
        "phases": _phases(phases),
        "atomic_progress": True,
        "restart_policy": "Preserve completed atomic rows and restart only incomplete rows under the identical code/config/runtime/task identity.",
        "result_stream": "jsonl-or-csv-per-atomic-unit",
        "outcome_read_before_freeze_allowed": False,
        "automatic_full_scale_authority": False,
        "scientific_authority": False,
        "experiment_authority": False,
        "p0_authority": False,
        "gpu_authority": False,
    }
    manifest["contract_sha256"] = canonical_sha256(manifest)
    return manifest


def validate_experiment_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    identity = manifest.get("execution_identity") or {}
    for key in ("config_sha256", "runtime_sha256", "task_snapshot_sha256"):
        if not HEX64.fullmatch(str(identity.get(key) or "")):
            blockers.append(f"invalid-execution-identity:{key}")
    if not GIT_REV.fullmatch(str(identity.get("code_commit") or "")):
        blockers.append("invalid-execution-identity:code_commit")
    if canonical_sha256(identity) != str(manifest.get("execution_identity_sha256") or ""):
        blockers.append("execution-identity-digest-mismatch")
    scientific = manifest.get("scientific_contract") or {}
    for key in ("scientific_object", "hypothesis", "decisive_test", "primary_metric", "strongest_baseline"):
        if not str(scientific.get(key) or "").strip(): blockers.append(f"missing-scientific-contract:{key}")
    if canonical_sha256(scientific) != str(manifest.get("scientific_contract_sha256") or ""):
        blockers.append("scientific-contract-digest-mismatch")
    units = [str(value) for value in (manifest.get("unit_ids") or [])]
    if not units: blockers.append("unit-ids-empty")
    if len(units) != len(set(units)): blockers.append("unit-ids-not-unique")
    phases = manifest.get("phases") or {}
    if list(phases) != ["smoke", "pilot", "full"]: blockers.append("phase-order-must-be-smoke-pilot-full")
    if any((phases.get(name) or {}).get("automatic_promotion") is not False for name in ("smoke", "pilot", "full")):
        blockers.append("automatic-phase-promotion-forbidden")
    if manifest.get("atomic_progress") is not True: blockers.append("atomic-progress-required")
    if manifest.get("automatic_full_scale_authority") is not False: blockers.append("automatic-full-scale-authority-forbidden")
    if any(manifest.get(key) is not False for key in ("scientific_authority", "experiment_authority", "p0_authority", "gpu_authority")):
        blockers.append("manifest-cannot-grant-authority")
    expected = canonical_sha256({key: value for key, value in manifest.items() if key != "contract_sha256"})
    if expected != str(manifest.get("contract_sha256") or ""): blockers.append("manifest-contract-digest-mismatch")
    return {"status": "PASS" if not blockers else "BLOCK", "passed": not blockers, "blockers": blockers, "scientific_authority": False}


def build_research_state(
    *, research_item_code: str, scientific_state: str, branch_status: str,
    workspace_ref: str, parent_state_id: str = "", code_commit: str = "",
    environment_sha256: str = "", config_sha256: str = "", task_snapshot: Any = None,
    memory_snapshot: Any = None, validated_evidence: Iterable[str] | None = None,
    unresolved_questions: Iterable[str] | None = None, failure_assets: Iterable[str] | None = None,
    resource_ledger: dict[str, Any] | None = None, authority_snapshot: dict[str, Any] | None = None,
    reopen_condition: str = "", experiment_execution_identity_sha256: str = "",
) -> dict[str, Any]:
    content = {
        "research_item_code": str(research_item_code), "scientific_state": str(scientific_state),
        "branch_status": str(branch_status), "workspace_ref": str(workspace_ref),
        "parent_state_id": str(parent_state_id), "code_commit": str(code_commit),
        "environment_sha256": str(environment_sha256), "config_sha256": str(config_sha256),
        "task_snapshot_sha256": canonical_sha256(task_snapshot),
        "memory_snapshot_sha256": canonical_sha256(memory_snapshot),
        "validated_evidence": [str(v) for v in (validated_evidence or [])],
        "unresolved_questions": [str(v) for v in (unresolved_questions or [])],
        "failure_assets": [str(v) for v in (failure_assets or [])],
        "resource_ledger": dict(resource_ledger or {}), "authority_snapshot": dict(authority_snapshot or {}),
        "reopen_condition": str(reopen_condition),
        "experiment_execution_identity_sha256": str(experiment_execution_identity_sha256),
    }
    digest = canonical_sha256(content)
    return {"schema_version": SCHEMA_VERSION, "state_id": f"RS-{digest[:20]}", "state_sha256": digest,
            **content, "state_object_has_scientific_authority": False, "state_object_has_execution_authority": False}


def validate_research_state(state: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    content = {key: value for key, value in state.items() if key not in {
        "schema_version", "state_id", "state_sha256", "state_object_has_scientific_authority", "state_object_has_execution_authority"}}
    digest = canonical_sha256(content)
    if state.get("state_sha256") != digest or state.get("state_id") != f"RS-{digest[:20]}": blockers.append("research-state-content-digest-mismatch")
    if not str(state.get("research_item_code") or ""): blockers.append("research-item-code-missing")
    if not str(state.get("scientific_state") or ""): blockers.append("scientific-state-missing")
    if str(state.get("scientific_state") or "") in REOPEN_GATED_STATES and not str(state.get("reopen_condition") or "").strip():
        blockers.append("reopen-gated-state-missing-reopen-condition")
    if state.get("state_object_has_scientific_authority") is not False or state.get("state_object_has_execution_authority") is not False:
        blockers.append("research-state-object-cannot-grant-authority")
    return {"status": "PASS" if not blockers else "BLOCK", "passed": not blockers, "blockers": blockers, "scientific_authority": False}


def evaluate_reanchor(archived_state: dict[str, Any], *, purpose: str,
                      current_execution_identity_sha256: str = "", reopen_receipt: dict[str, Any] | None = None) -> dict[str, Any]:
    blockers: list[str] = []
    scientific_state = str(archived_state.get("scientific_state") or "")
    if not validate_research_state(archived_state)["passed"]: blockers.append("archived-state-invalid")
    eligible = False
    if purpose == "execution_resume":
        expected = str(archived_state.get("experiment_execution_identity_sha256") or "")
        if not expected or expected != current_execution_identity_sha256: blockers.append("execution-identity-mismatch")
        if scientific_state in REOPEN_GATED_STATES: blockers.append("scientific-reopen-required-before-execution-resume")
        status = "RESUME_ALLOWED" if not blockers else "RESUME_BLOCKED"
    elif purpose == "scientific_reopen":
        receipt = reopen_receipt or {}
        if scientific_state not in REOPEN_GATED_STATES: blockers.append("scientific-state-does-not-require-reopen")
        if not str(archived_state.get("reopen_condition") or "").strip(): blockers.append("recorded-reopen-condition-missing")
        if receipt.get("condition_satisfied") is not True: blockers.append("reopen-condition-not-satisfied")
        if not [v for v in receipt.get("new_evidence_refs") or [] if str(v)]: blockers.append("new-reopen-evidence-required")
        if receipt.get("independent_scientific_review_required") is not True: blockers.append("independent-scientific-review-must-remain-required")
        eligible = not blockers
        status = "ELIGIBLE_FOR_SCIENTIFIC_REVIEW" if eligible else "REOPEN_BLOCKED"
    else:
        blockers.append("unknown-reanchor-purpose"); status = "REANCHOR_BLOCKED"
    return {"schema_version": SCHEMA_VERSION, "purpose": purpose, "source_state_id": archived_state.get("state_id"),
            "status": status, "blockers": blockers, "reanchor_allowed": not blockers,
            "eligible_for_scientific_review": eligible, "machine_actionable": False,
            "scientific_authority": False, "experiment_authority": False, "p0_authority": False, "gpu_authority": False}


def _contains_atomic_progress(value: Any) -> bool:
    if isinstance(value, dict):
        return value.get("atomic_progress") is True or any(_contains_atomic_progress(v) for v in value.values())
    if isinstance(value, list): return any(_contains_atomic_progress(v) for v in value)
    return False


def build_research_execution_kernel_state(config_dir: Path | None = None) -> dict[str, Any]:
    from .scientific_metacognition import build_failure_taxonomy_state

    root = config_dir or Path(__file__).resolve().parent
    legacy: list[str] = []
    for path in sorted(root.glob("*_config.json")):
        try: payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError): continue
        if _contains_atomic_progress(payload): legacy.append(path.name)
    return {
        "schema_version": SCHEMA_VERSION, "status": "KERNEL_CONTRACTS_INSTALLED", "policy": dict(POLICY),
        "references": [dict(row) for row in REFERENCES],
        "contracts": ["ResearchState", "ExperimentManifest", "AtomicCheckpoint+ResumeCursor", "ResearchSandboxContract", "PlannerExecutorJobReceipt", "MetaCognitionReceipt"],
        "failure_taxonomy": build_failure_taxonomy_state(),
        "migration": {"legacy_atomic_configs_detected": legacy, "migration_rule": "Migrate incrementally when a runner is created or modified; do not invalidate existing append-only receipts."},
        "summary": {"contracts": 6, "failure_families": 8, "legacy_atomic_configs_detected": len(legacy), "automatic_scientific_authority": 0,
                    "automatic_experiment_authority": 0, "automatic_p0_authority": 0, "automatic_gpu_authority": 0},
        "scientific_authority": False,
    }
