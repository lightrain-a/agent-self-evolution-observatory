from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_confirmatory_preexec import (
    N_CANDIDATES,
    OBJECT_ID,
    PLANNING_SE_MAX,
    R2_STABILITY_MAX,
    R3_STABILITY_MAX,
    TO_V_UPTAKE_MIN,
    sha256_file,
    sha256_value,
)

ROOT = Path(__file__).resolve().parents[1]
FREEZE = ROOT / "generated/agent-constraint-externality-confirmatory-preexec-freeze-20260904.json"
PLAN = ROOT / "generated/agent-constraint-externality-minimum-effective-plan-r2-20260904.json"
REVIEW = ROOT / "generated/agent-constraint-externality-minimum-r2-review-closeout-20260904.json"
PROPOSAL = ROOT / "generated/agent-constraint-externality-confirmatory-execution-proposal-20260904.json"
ADDENDUM = ROOT / "consultations/agent-constraint-externality-confirmatory-preexec-freeze-20260904.md"
OUTPUT = ROOT / "generated/agent-constraint-externality-confirmatory-preexec-audit-20260904.json"


class AuditError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def audit() -> dict[str, Any]:
    for path in (FREEZE, PLAN, REVIEW, PROPOSAL, ADDENDUM):
        require(path.is_file(), f"missing audit input: {path}")
    freeze, plan, review, proposal = map(load, (FREEZE, PLAN, REVIEW, PROPOSAL))

    checks: dict[str, bool] = {}
    checks["review_pass"] = review.get("independent_review", {}).get("verdict") == "PASS_MINIMUM_AGENT_CONSTRAINT_DESIGN"
    checks["review_no_verdict_changing_fixes"] = review.get("independent_review", {}).get("verdict_changing_fixes") == []
    checks["review_receipt_hash_matches"] = review.get("reviewed_receipt_sha256") == sha256_file(PLAN)
    checks["freeze_parent_plan_hash_matches"] = freeze.get("parents", {}).get("minimum_effective_plan_file_sha256") == sha256_file(PLAN)
    checks["freeze_parent_review_hash_matches"] = freeze.get("parents", {}).get("review_closeout_file_sha256") == sha256_file(REVIEW)
    checks["freeze_parent_proposal_hash_matches"] = freeze.get("parents", {}).get("execution_proposal_file_sha256") == sha256_file(PROPOSAL)
    checks["freeze_content_hash_self_consistent"] = freeze.get("content_sha256") == sha256_value({k: v for k, v in freeze.items() if k != "content_sha256"})

    tov = freeze.get("target_only_verification", {})
    checks["tov_before_topology"] = tov.get("timing") == "strictly before INDEPENDENT/LOW/HIGH exposure"
    checks["tov_same_snapshot"] = "identical common_pre_update_snapshot_sha256" in str(tov.get("snapshot_rule"))
    checks["tov_exact_repair"] = "exact frozen repair bytes" in str(tov.get("repair_rule"))
    checks["tov_target_only_evaluator"] = tov.get("evaluator") == "existing AppWorld semantic target evaluator only"
    checks["tov_threshold_frozen"] = float(tov.get("eligibility_uptake_delta_min")) == TO_V_UPTAKE_MIN == 0.50
    checks["tov_no_post_topology_reselection"] = tov.get("post_topology_target_outcomes_may_change_eligibility") is False

    repeat = freeze.get("repeat_qualification", {})
    checks["repeat_dev_count_within_reviewed_range"] = int(repeat.get("development_family_count")) == 6
    checks["repeat_r2_threshold"] = f"{R2_STABILITY_MAX:.2f}" in str(repeat.get("R2_rule"))
    checks["repeat_r3_threshold"] = f"{R3_STABILITY_MAX:.2f}" in str(repeat.get("R3_rule"))
    checks["repeat_r_gt_3_forbidden"] = "R>3 forbidden" in str(repeat.get("hard_stop"))
    checks["repeat_direction_blind"] = repeat.get("selection_uses_treatment_direction") is False

    precision = freeze.get("precision_freeze", {})
    checks["precision_N_candidates_unchanged"] = precision.get("N_candidates") == list(N_CANDIDATES) == plan.get("confirmatory_panel", {}).get("N_candidates")
    checks["precision_se_threshold"] = float(precision.get("planning_se_max")) == PLANNING_SE_MAX == 0.10
    checks["precision_no_mean_sign"] = precision.get("development_means_or_signs_in_decision_artifact") is False
    checks["precision_N24_hard_stop"] = "STOP_PRECISION_QUALIFICATION" in str(precision.get("if_N24_fails"))

    panel = freeze.get("panel_selection", {})
    checks["panel_reserve_24"] = int(panel.get("reserve_family_count")) == 24 == int(plan.get("confirmatory_panel", {}).get("reserve_family_count"))
    checks["panel_pre_topology_only"] = "pre-topology eligibility attrition only" in str(panel.get("reserve_activation"))
    checks["panel_no_post_topology_backfill"] = panel.get("post_topology_backfill_allowed") is False

    guard = freeze.get("post_treatment_guard", {})
    checks["guard_retain_all_frozen_families"] = guard.get("retain_every_frozen_family_in_every_I_L_H_arm") is True
    checks["guard_no_target_deletion"] = guard.get("topology_specific_target_success_used_for_deletion") is False

    checks["proposal_authority_still_false"] = all(value is False for value in proposal.get("authority", {}).values())
    checks["freeze_authority_all_false"] = all(value is False for value in freeze.get("authority", {}).values())
    checks["zero_provider_calls"] = int(freeze.get("scientific_provider_calls_created")) == 0
    checks["zero_scientific_outcomes"] = int(freeze.get("scientific_outcomes_created")) == 0

    failed = sorted(name for name, ok in checks.items() if not ok)
    status = "PASS_PREEXEC_CONSISTENCY_EXECUTION_AUTHORITY_CLOSED" if not failed else "FAIL_PREEXEC_CONSISTENCY"
    result = {
        "schema_version": 1,
        "object_id": "AGENT-CONSTRAINT-EXTERNALITY-CONFIRMATORY-PREEXEC-AUDIT-20260904",
        "recorded_date": "2026-09-04",
        "status": status,
        "review_scope": "mechanical narrow consistency only; does not reopen the independently passed R2 scientific design",
        "preexec_object_id": OBJECT_ID,
        "checks": checks,
        "failed_checks": failed,
        "verdict_changing_scientific_repairs_introduced": 0,
        "new_scientific_workload_introduced": 0,
        "authority": {
            "provider_execution": False,
            "development_repeat_qualification": False,
            "target_only_verification": False,
            "rq1_rq2": False,
            "rq3": False,
            "rq4": False,
            "paper_claim": False,
        },
        "scientific_provider_calls_created": 0,
        "scientific_outcomes_created": 0,
        "inputs": {
            "freeze_file_sha256": sha256_file(FREEZE),
            "addendum_file_sha256": sha256_file(ADDENDUM),
            "review_closeout_file_sha256": sha256_file(REVIEW),
            "proposal_file_sha256": sha256_file(PROPOSAL),
        },
        "next_required_action": "SEPARATE_HUMAN_EXECUTION_AUTHORITY_ONLY_AFTER_PROVIDER_READINESS" if not failed else "REPAIR_PREEXEC_FREEZE_BEFORE_ANY_AUTHORITY",
    }
    result["content_sha256"] = sha256_value(result)
    return result


def main() -> None:
    result = audit()
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "failed_checks": result["failed_checks"], "content_sha256": result["content_sha256"]}, sort_keys=True))
    if result["failed_checks"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
