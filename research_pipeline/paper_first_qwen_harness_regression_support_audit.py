from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

SOURCE_REF = "arXiv:2607.03691"
SOURCE_FULLTEXT_SHA256 = "0ddcd56681c80b1d0b483ca7581de85fd143625ad125ff1e9b727a27c3e8fb16"
TOKEN_REVERSAL_ID = "cb77635e719c0bb77e64e86690c8db49a7e38b25508ea685a045c716c51faacc"
QUALITY_PLATEAU_ID = "8e81f6a0255f3165206886f73a7745c82db6c89fcb778fc0e65a5673aa124346"
CANDIDATE_ID = "QWEN-HARNESS-BUDGETED-REGRESSION-SENTINEL"
PRIMARY_STATE = PROJECT_ROOT / "generated" / "paper-first-primary-evidence-state.json"
DEFAULT_AUDIT_JSON = PROJECT_ROOT / "generated" / "qwen-harness-regression-support-audit-20260818.json"
TOKEN_HOLD_JSON = PROJECT_ROOT / "generated" / "qwen-harness-token-reversal-fresh-phenomenon-support-hold-20260818.json"
PLATEAU_HOLD_JSON = PROJECT_ROOT / "generated" / "qwen-harness-quality-plateau-fresh-phenomenon-support-hold-20260818.json"

PACKAGE_DECLARATION = "To be made publicly available upon acceptance."
PACKAGE_DECLARATION_SHA256 = hashlib.sha256(" ".join(PACKAGE_DECLARATION.split()).encode()).hexdigest()

REQUIRED_UNIT = (
    "A provenance-audited per-version × task × run table for the paper's 35 Qwen Code releases and 50 SWE-bench Verified tasks, "
    "including release/version or commit identity, task identity, run identity, resolved/pass outcome, token consumption, tool-call "
    "count, conversation-turn count, and enough pre-outcome release metadata to reconstruct the paper's project/component change "
    "features. The unit must permit temporal train/validation/test splits and simulation of a small probe subset against the full "
    "50-task outcome so random/stratified probes, historical task-sensitivity, and change-risk-only baselines can be matched without "
    "reading held-out release outcomes."
)
REOPEN_CONDITION = (
    "Reopen when the authors publish the promised replication package, or an equivalent first-party export, containing joinable raw "
    "per-version × task × run outcomes and execution-cost logs sufficient to evaluate a preregistered budgeted regression sentinel "
    "prospectively across held-out releases. Aggregate Figure 6/8 values, isolated case studies, future-running scripts without the "
    "paper-run outputs, or inferred values from plots are insufficient. A release-surface change requests re-audit only and does not "
    "automatically authorize Problem Gate, Method, P0, or GPU."
)

PHENOMENA = {
    TOKEN_REVERSAL_ID: {
        "title": "Qwen harness token-efficiency reversal support hold",
        "target": "The mid-cycle ~217K-token trough followed by renewed token growth in later harness releases.",
    },
    QUALITY_PLATEAU_ID: {
        "title": "Qwen harness quality-plateau regression support hold",
        "target": "The post-v0.3.0 quality plateau with isolated regressions such as the v0.5.0 regression.",
    },
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected object: {path}")
    return payload


def build_support_audit() -> dict[str, Any]:
    primary = _load(PRIMARY_STATE)
    record = next((row for row in primary.get("records") or [] if isinstance(row, dict) and row.get("ref") == SOURCE_REF), None)
    if not isinstance(record, dict):
        raise ValueError("Qwen harness primary record unavailable")
    if record.get("fulltext_sha256") != SOURCE_FULLTEXT_SHA256:
        raise ValueError("Qwen harness fulltext provenance drift")
    if str((primary.get("policy") or {}).get("typed_evidence_extraction_version") or "") != "typed-v2":
        raise ValueError("support audit requires typed-v2 primary projection")
    return {
        "schema_version": "1.0",
        "status": "HOLD_SUPPORT_NO_RELEASED_REQUIRED_UNIT",
        "candidate_id": CANDIDATE_ID,
        "source_ref": SOURCE_REF,
        "source_fulltext_sha256": SOURCE_FULLTEXT_SHA256,
        "phenomenon_ids": sorted(PHENOMENA),
        "primary_package_declaration": PACKAGE_DECLARATION,
        "primary_package_declaration_sha256": PACKAGE_DECLARATION_SHA256,
        "primary_declared_package_contents": [
            "all 35 Qwen Code CLI versions",
            "inference and evaluation scripts",
            "raw results",
        ],
        "primary_declared_release_timing": "upon acceptance",
        "audit_scope": "frozen-primary-release-declaration-only",
        "network_release_check_executed": False,
        "current_web_release_absence_claimed": False,
        "required_unit": REQUIRED_UNIT,
        "reopen_only_if": REOPEN_CONDITION,
        "why_hold": (
            "The frozen primary paper reports 35 releases × 50 tasks × 2 runs and says its replication package includes all versions, "
            "inference/evaluation scripts, and raw results, but the same primary version states that the package is to be made publicly "
            "available upon acceptance. The aggregate release curves and hand-traced PR case studies are enough to establish the "
            "regression phenomena and several source-internal explanations, but not enough to simulate a low-budget held-out probe "
            "policy or compare it fairly with random/stratified probes and pre-outcome change-risk baselines. Missing released raw units "
            "is therefore an execution/support hold, not scientific negative evidence."
        ),
        "policy": {
            "support_availability_is_not_scientific_failure": True,
            "primary_release_declaration_is_frozen_provenance_not_current_web_claim": True,
            "aggregate_release_curves_cannot_support_budgeted_probe_replay": True,
            "plot_digitization_is_not_an_acceptable_substitute_for_raw_units": True,
            "release_change_requires_reaudit_before_clearing_hold": True,
            "automatic_problem_gate_authority": False,
            "automatic_method_authority": False,
            "automatic_experiment_authority": False,
            "automatic_p0_authority": False,
            "automatic_gpu_authority": False,
        },
        "scientific_authority": False,
        "source_artifact_sha256": {"primary_state": _sha(PRIMARY_STATE)},
    }


def validate_support_audit(audit: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if audit.get("status") != "HOLD_SUPPORT_NO_RELEASED_REQUIRED_UNIT" or audit.get("scientific_authority") is not False:
        errors.append("Qwen harness support audit status/authority invalid")
    if audit.get("candidate_id") != CANDIDATE_ID or audit.get("source_ref") != SOURCE_REF:
        errors.append("Qwen harness support audit identity mismatch")
    if sorted(audit.get("phenomenon_ids") or []) != sorted(PHENOMENA):
        errors.append("Qwen harness support audit phenomenon set mismatch")
    if audit.get("source_fulltext_sha256") != SOURCE_FULLTEXT_SHA256 or audit.get("primary_package_declaration_sha256") != PACKAGE_DECLARATION_SHA256:
        errors.append("Qwen harness support audit source provenance mismatch")
    if audit.get("audit_scope") != "frozen-primary-release-declaration-only" or audit.get("network_release_check_executed") is not False or audit.get("current_web_release_absence_claimed") is not False:
        errors.append("Qwen harness support audit must not overclaim current web release absence")
    if audit.get("required_unit") != REQUIRED_UNIT or audit.get("reopen_only_if") != REOPEN_CONDITION:
        errors.append("Qwen harness support audit contract drift")
    policy = audit.get("policy") or {}
    if policy.get("support_availability_is_not_scientific_failure") is not True or policy.get("release_change_requires_reaudit_before_clearing_hold") is not True:
        errors.append("Qwen harness support audit policy invalid")
    return errors


def build_support_hold(*, phenomenon_id: str, audit: dict[str, Any], audit_file_sha256: str) -> dict[str, Any]:
    errors = validate_support_audit(audit)
    if errors:
        raise ValueError("invalid Qwen harness support audit: " + ";".join(errors))
    spec = PHENOMENA.get(phenomenon_id)
    if not spec:
        raise ValueError("unknown Qwen harness phenomenon")
    return {
        "schema_version": "1.0",
        "status": "HOLD_SUPPORT_NO_RELEASED_REQUIRED_UNIT",
        "candidate_id": f"{CANDIDATE_ID}:{phenomenon_id[:12]}",
        "title": spec["title"],
        "source_ref": SOURCE_REF,
        "phenomenon_id": phenomenon_id,
        "required_unit": REQUIRED_UNIT,
        "reason": str(audit.get("why_hold") or "") + " Exact held target: " + spec["target"],
        "reopen_only_if": REOPEN_CONDITION,
        "support_audit_artifact": "generated/qwen-harness-regression-support-audit-20260818.json",
        "support_audit_sha256": audit_file_sha256,
        "scientific_authority": False,
        "authority": {"dead_end": False, "problem_gate": False, "paper_design": False, "method": False, "experiment": False, "p0": False, "gpu": False, "automatic_release_reopen": False},
    }


def validate_support_hold(hold: dict[str, Any], *, audit_path: Path = DEFAULT_AUDIT_JSON) -> list[str]:
    errors: list[str] = []
    phenomenon_id = str(hold.get("phenomenon_id") or "")
    if hold.get("status") != "HOLD_SUPPORT_NO_RELEASED_REQUIRED_UNIT" or hold.get("scientific_authority") is not False:
        errors.append("Qwen harness support hold status/authority invalid")
    if hold.get("source_ref") != SOURCE_REF or phenomenon_id not in PHENOMENA:
        errors.append("Qwen harness support hold identity mismatch")
    if hold.get("required_unit") != REQUIRED_UNIT or hold.get("reopen_only_if") != REOPEN_CONDITION:
        errors.append("Qwen harness support hold contract drift")
    if hold.get("support_audit_artifact") != "generated/qwen-harness-regression-support-audit-20260818.json":
        errors.append("Qwen harness support hold audit path invalid")
    if not audit_path.is_file():
        errors.append("Qwen harness support audit artifact missing")
    elif str(hold.get("support_audit_sha256") or "") != _sha(audit_path):
        errors.append("Qwen harness support hold audit digest mismatch")
    if any(value is not False for value in (hold.get("authority") or {}).values()):
        errors.append("Qwen harness support hold cannot grant authority")
    return errors


def write_support_state(
    *,
    audit_path: Path = DEFAULT_AUDIT_JSON,
    token_hold_path: Path = TOKEN_HOLD_JSON,
    plateau_hold_path: Path = PLATEAU_HOLD_JSON,
) -> dict[str, Any]:
    audit = build_support_audit()
    errors = validate_support_audit(audit)
    if errors:
        raise ValueError("invalid Qwen harness support audit: " + ";".join(errors))
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit_sha = _sha(audit_path)
    holds = {
        TOKEN_REVERSAL_ID: (token_hold_path, build_support_hold(phenomenon_id=TOKEN_REVERSAL_ID, audit=audit, audit_file_sha256=audit_sha)),
        QUALITY_PLATEAU_ID: (plateau_hold_path, build_support_hold(phenomenon_id=QUALITY_PLATEAU_ID, audit=audit, audit_file_sha256=audit_sha)),
    }
    for _, (path, hold) in holds.items():
        path.write_text(json.dumps(hold, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        hold_errors = validate_support_hold(hold, audit_path=audit_path)
        if hold_errors:
            raise ValueError("invalid Qwen harness support hold: " + ";".join(hold_errors))
    return {"audit": audit, "support_holds": [hold for _, hold in holds.values()]}


if __name__ == "__main__":
    print(json.dumps(write_support_state(), ensure_ascii=False, indent=2))
