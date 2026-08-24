from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

SCHEMA_VERSION = "1.0"
DEFAULT_JSON = PROJECT_ROOT / "generated" / "ai4ai-strategy-reopen-contradiction-screen-20260824.json"
PRIMARY_EVIDENCE = PROJECT_ROOT / "generated" / "paper-first-primary-evidence-state.json"
STRATEGY_OBJECT = PROJECT_ROOT / "research_pipeline" / "strategy_reopen_c01_scientific_object.json"
STRATEGY_QUALIFICATION = PROJECT_ROOT / "research_pipeline" / "strategy_reopen_c01_same_substrate_qualification.json"
V19_FAILURE_ASSETS = PROJECT_ROOT / "research_pipeline" / "v19r003_forced_switch_failure_assets_20260824.json"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _ai4ai_record(primary: dict[str, Any]) -> dict[str, Any]:
    rows = [row for row in primary.get("records") or [] if row.get("ref") == "arXiv:2608.20318"]
    if len(rows) != 1:
        raise ValueError(f"expected exactly one AI4AI-Bench primary record, got {len(rows)}")
    return rows[0]


def build_ai4ai_strategy_reopen_contradiction(*, generated_at: str | None = None) -> dict[str, Any]:
    primary = _load(PRIMARY_EVIDENCE)
    source = _ai4ai_record(primary)
    strategy = _load(STRATEGY_OBJECT)
    qualification = _load(STRATEGY_QUALIFICATION)
    v19 = _load(V19_FAILURE_ASSETS)

    strategy_object = strategy.get("scientific_object") or {}
    source_facts = {
        "paper": {
            "ref": source["ref"],
            "title": source["title"],
            "publication_date": source["publication_date"],
            "primary_url": source["primary_url"],
            "primary_sha256": source["source_sha256"],
            "fulltext_sha256": source["fulltext_sha256"],
        },
        "protocol": {
            "development_window": "4 hours on one B300 per task",
            "submission_boundary": "Only the final source-code patch crosses into the fresh formal run; exploration weights/cache/notes do not.",
            "formal_verification": "Submitted source is rerun from a clean start for up to 12 hours and scored by a fixed evaluator unavailable during exploration.",
        },
        "outcome_independent_action_surface": {
            "classifiable_submissions": 263,
            "run_side_only": 141,
            "touch_learning_procedure": 122,
            "learning_families": ["loss/objective", "supervision", "update rule", "training data"],
            "interpretation": "The source-patch structure makes whether a submission reaches the learning procedure checkable without using its final benchmark score.",
        },
        "aggregate_effort_delta": {
            "lowest_to_highest_effort_learning_touch_share": [0.08, 0.64],
            "lowest_to_highest_effort_mean_score": [0.094, 0.196],
            "codex_median_evaluations_per_task": [4, 16],
            "codex_median_edited_lines": [18, 246],
            "codex_median_output_tokens": [11000, 109000],
            "codex_median_exploration_cost_usd": [1.69, 34.60],
            "interpretation": "Reasoning-effort variation changes search/compute intensity by large factors, so the 8%-to-64% learning-layer shift is not a matched decision-surface intervention.",
        },
    }

    qualification_tests = [
        {
            "key": "OUTCOME_INDEPENDENT_STRATEGY_FAMILY_ENDPOINT",
            "pass": True,
            "finding": "PASS",
            "reason": (
                "The final source patch can be structurally classified as run-side-only versus touching the learning procedure before consulting the hidden final evaluator. "
                "This is a substantially cleaner high-level action-family endpoint than endpoint utility or post-hoc success labels."
            ),
            "scientific_consequence": "AI4AI-Bench is a legitimate future substrate lead for the strategy-family endpoint layer.",
        },
        {
            "key": "INDEPENDENT_RECOGNITION_POSITIVE_PREFIX",
            "pass": False,
            "finding": "FAIL_CURRENT_SOURCE_SUPPORT",
            "reason": (
                "The current primary paper/repository evidence establishes what the submitted patch changes, but the present audit does not provide source-authored frozen prefixes proving that a low-effort agent had already recognized a mechanism-level reason to abandon the current strategy before it nevertheless stayed run-side-only. "
                "A task instruction to improve the training algorithm is not equivalent to independent recognition that the current high-level strategy is disconfirmed."
            ),
            "scientific_consequence": "The observation cannot distinguish failure to recognize from failure to reopen after recognition.",
        },
        {
            "key": "MATCHED_COMPUTE_SEARCH_AND_ACTION_SUPPORT",
            "pass": False,
            "finding": "FAIL_CONFOUNDED_BY_REASONING_EFFORT",
            "reason": (
                "Lowest-to-highest reasoning effort changes not only willingness to touch the learning layer but also the number of evaluations, edited lines, output tokens, and cost. "
                "Those are direct changes in search depth/compute, so ordinary capability/search-budget explanations receive the same observed evidence and remain sufficient."
            ),
            "scientific_consequence": "The aggregate effort comparison cannot identify a strategy-reopening decision-surface residual beyond more search/test-time compute.",
        },
    ]

    strongest_reduction = {
        "status": "REDUCED_FOR_CURRENT_REOPEN_CLAIM",
        "reducer": "reasoning-compute/search-depth plus recognition uncertainty",
        "prediction": (
            "With more tokens, evaluations, edits, and spend, an agent explores a larger part of the available code/action space and is therefore more likely to reach an algorithmic-change family even if there is no distinct KEEP-versus-REOPEN control bottleneck. "
            "Without an independently recognition-positive prefix, low-effort run-side behavior is also compatible with failure to diagnose the need for a strategy change."
        ),
        "why_ai4ai_does_not_contradict_the_reducer": (
            "AI4AI-Bench varies reasoning effort together with search intensity; it does not hold the decision-call/search budget fixed while manipulating only whether the current high-level strategy is exposed as a decision variable."
        ),
    }

    reopen_path = {
        "status": "SUPPORT_LEAD_ONLY",
        "required_public_or_provenance_audited_unit": (
            "A source/reviewable AI4AI trajectory prefix in which the agent explicitly and correctly diagnoses a mechanism-level defect requiring a learning-side strategy change before the final patch, paired with a matched prefix/continuation under identical model, harness, task, evidence, proxy observations, action support, wall-clock/evaluation budget, token/decision budget, and proposal interface."
        ),
        "decisive_intervention": (
            "On independently recognition-positive prefixes, compare explicit content-free STRATEGY_REOPEN against GENERIC_REFLECTION and the local KEEP-versus-RETUNE placebo under the same information and call/search budget; score only the next committed source-defined strategy-family action, before final task outcome is opened."
        ),
        "go_condition": (
            "A replicated strategy-family switch residual survives both generic reflection and local menu-salience controls under matched compute/search support across multiple task families."
        ),
        "stop_condition": (
            "Recognition cannot be independently reconstructed, compute/search cannot be matched, or the switch delta is reproduced by generic reflection/local decision-menu salience."
        ),
    }

    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at or _now(),
        "candidate_id": "AI4AI-STRATEGY-REOPEN-CONTRADICTION-20260824",
        "title": "AI4AI-Bench as contradictory evidence for strategy reopening",
        "status": "HOLD_SUPPORT_LEAD_NO_SCIENTIFIC_REOPEN",
        "target_existing_object": strategy.get("candidate_id"),
        "target_existing_object_status": strategy.get("status"),
        "source_facts": source_facts,
        "qualification_tests": qualification_tests,
        "strongest_same_information_reduction": strongest_reduction,
        "reopen_path": reopen_path,
        "existing_contract": {
            "estimand": strategy_object.get("estimand"),
            "same_information_reducer": strategy_object.get("same_information_reducer"),
            "prespecified_stop_rule": strategy_object.get("prespecified_stop_rule"),
            "same_substrate_qualification_status": qualification.get("status"),
        },
        "v19_boundary": {
            "closure_status": v19.get("closure_status"),
            "reopen_condition": v19.get("reopen_condition"),
            "semantic_observability_asset": (v19.get("semantic_observability_asset") or {}).get("signature"),
            "interpretation": "AI4AI-Bench does not repair V19's support/protocol failure and does not authorize reuse of prior NO_EVIDENCE units.",
        },
        "policy": {
            "new_primary_evidence_may_reopen_a_scientific_closure_only_after_exact_contract_collision": True,
            "outcome_independent_endpoint_is_necessary_not_sufficient": True,
            "recognition_positive_qualification_is_mandatory": True,
            "reasoning_effort_is_not_a_matched_reopening_intervention": True,
            "aggregate_success_association_cannot_authorize_reopen": True,
            "support_lead_is_not_problem_gate_authority": True,
            "zero_paid_execution_for_this_screen": True,
            "sealed_v19_units_remain_unconsumed": True,
        },
        "summary": {
            "qualification_tests": len(qualification_tests),
            "qualification_passed": sum(row["pass"] is True for row in qualification_tests),
            "qualification_failed": sum(row["pass"] is False for row in qualification_tests),
            "outcome_independent_endpoint_supported": 1,
            "recognition_positive_units_verified": 0,
            "compute_search_matched": 0,
            "support_lead": 1,
            "contradictory_evidence_sufficient": 0,
            "scientific_reopen_authorized": 0,
            "problem_gate_eligible": 0,
            "research_item_eligible": 0,
            "provider_calls_authorized": 0,
            "gpu_authorized": 0,
            "sealed_v19_units_consumed": 0,
        },
        "scientific_authority": False,
        "authority": {
            "scientific_reopen": False,
            "problem_gate": False,
            "research_item": False,
            "paper_design": False,
            "method": False,
            "experiment": False,
            "provider": False,
            "gpu": False,
        },
        "source_refs": [
            "arXiv:2608.20318v1",
            f"primary-fulltext:arXiv:2608.20318#sha256={source['fulltext_sha256']}",
            "https://github.com/Einsia/AI4AI-Bench",
            "repo:research_pipeline/strategy_reopen_c01_scientific_object.json",
            "repo:research_pipeline/strategy_reopen_c01_same_substrate_qualification.json",
            "repo:research_pipeline/v19r003_forced_switch_failure_assets_20260824.json",
        ],
    }
    payload["screen_sha256"] = _sha({k: v for k, v in payload.items() if k != "generated_at"})
    return payload


def validate_ai4ai_strategy_reopen_contradiction(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    summary = payload.get("summary") or {}
    policy = payload.get("policy") or {}
    if payload.get("status") != "HOLD_SUPPORT_LEAD_NO_SCIENTIFIC_REOPEN":
        errors.append("status-must-remain-support-hold")
    if payload.get("scientific_authority") is not False:
        errors.append("scientific-authority-leak")
    tests = payload.get("qualification_tests") or []
    by_key = {row.get("key"): row for row in tests}
    if len(tests) != 3:
        errors.append("three-qualification-tests-required")
    if (by_key.get("OUTCOME_INDEPENDENT_STRATEGY_FAMILY_ENDPOINT") or {}).get("pass") is not True:
        errors.append("endpoint-support-must-be-preserved")
    if (by_key.get("INDEPENDENT_RECOGNITION_POSITIVE_PREFIX") or {}).get("pass") is not False:
        errors.append("recognition-cannot-be-upgraded")
    if (by_key.get("MATCHED_COMPUTE_SEARCH_AND_ACTION_SUPPORT") or {}).get("pass") is not False:
        errors.append("compute-match-cannot-be-upgraded")
    required_true = (
        "new_primary_evidence_may_reopen_a_scientific_closure_only_after_exact_contract_collision",
        "outcome_independent_endpoint_is_necessary_not_sufficient",
        "recognition_positive_qualification_is_mandatory",
        "reasoning_effort_is_not_a_matched_reopening_intervention",
        "aggregate_success_association_cannot_authorize_reopen",
        "support_lead_is_not_problem_gate_authority",
        "zero_paid_execution_for_this_screen",
        "sealed_v19_units_remain_unconsumed",
    )
    if any(policy.get(key) is not True for key in required_true):
        errors.append("policy-incomplete")
    if int(summary.get("qualification_tests") or 0) != 3 or int(summary.get("qualification_passed") or 0) != 1 or int(summary.get("qualification_failed") or 0) != 2:
        errors.append("qualification-summary-drift")
    for key in (
        "contradictory_evidence_sufficient",
        "scientific_reopen_authorized",
        "problem_gate_eligible",
        "research_item_eligible",
        "provider_calls_authorized",
        "gpu_authorized",
        "sealed_v19_units_consumed",
    ):
        if int(summary.get(key) or 0) != 0:
            errors.append(f"authority-leak:{key}")
    if int(summary.get("recognition_positive_units_verified") or 0) != 0:
        errors.append("recognition-unit-count-must-remain-zero")
    if int(summary.get("compute_search_matched") or 0) != 0:
        errors.append("compute-match-must-remain-zero")
    if int(summary.get("support_lead") or 0) != 1 or int(summary.get("outcome_independent_endpoint_supported") or 0) != 1:
        errors.append("support-lead-endpoint-summary-drift")
    if (payload.get("strongest_same_information_reduction") or {}).get("status") != "REDUCED_FOR_CURRENT_REOPEN_CLAIM":
        errors.append("same-information-reduction-missing")
    if (payload.get("reopen_path") or {}).get("status") != "SUPPORT_LEAD_ONLY":
        errors.append("reopen-path-must-remain-support-only")
    return errors


def load_ai4ai_strategy_reopen_contradiction(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    if path.exists():
        return _load(path)
    return build_ai4ai_strategy_reopen_contradiction()


def write_ai4ai_strategy_reopen_contradiction(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    payload = build_ai4ai_strategy_reopen_contradiction()
    errors = validate_ai4ai_strategy_reopen_contradiction(payload)
    if errors:
        raise ValueError("invalid AI4AI strategy-reopen contradiction screen: " + ";".join(errors))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    payload = write_ai4ai_strategy_reopen_contradiction() if args.write else build_ai4ai_strategy_reopen_contradiction()
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "screen_sha256": payload["screen_sha256"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
