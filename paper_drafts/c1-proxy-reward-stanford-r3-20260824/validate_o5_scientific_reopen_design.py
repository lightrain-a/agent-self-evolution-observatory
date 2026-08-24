#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DESIGN = HERE / "o5-scientific-reopen-design.json"
QA = HERE / "o5-scientific-reopen-design-qa.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path: Path):
    return json.loads(path.read_text())


def find_objection(obj):
    if isinstance(obj, dict):
        if obj.get("id") == "PROXY-O5" or obj.get("objection_id") == "PROXY-O5":
            return obj
        for value in obj.values():
            hit = find_objection(value)
            if hit is not None:
                return hit
    elif isinstance(obj, list):
        for value in obj:
            hit = find_objection(value)
            if hit is not None:
                return hit
    return None


def main() -> int:
    d = load(DESIGN)
    checks: dict[str, bool] = {}

    checks["paper_and_objection_identity"] = (
        d["paper_id"] == "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE"
        and d["objection_id"] == "PROXY-O5"
    )
    checks["proposal_only_no_design_authority"] = (
        d["authority"]["design_proposal_ready"] is True
        and d["authority"]["design_authority"] is False
    )
    checks["zero_execution_authority"] = (
        d["authority"]["scientific_reopen_authority"] is False
        and d["authority"]["experiment_authority"] is False
        and d["authority"]["provider_call_authority"] is False
        and d["next_gate"]["provider_calls_now"] == 0
        and d["next_gate"]["may_execute_from_this_artifact_alone"] is False
    )
    checks["requires_content_addressed_human_authority"] = (
        "content-addressed human authorization" in d["authority"]["required_before_execution"]
        and d["next_gate"]["state"] == "AWAIT_EXTERNAL_CONTENT_ADDRESSED_HUMAN_AUTHORITY"
    )

    bindings = d["source_bindings"]
    for name, row in bindings.items():
        path = Path(row["path"])
        if not path.is_absolute():
            path = ROOT / path
        checks[f"binding_{name}"] = path.exists() and sha256(path) == row["sha256"]

    matrix = load(ROOT / "generated/stanford-r2-objection-matrix.json")
    o5 = find_objection(matrix)
    checks["o5_still_requires_scientific_reopen"] = bool(
        o5
        and o5.get("d") == "REQUIRES_SCIENTIFIC_REOPEN"
        and o5.get("action") == "SCIENTIFIC_REOPEN_REQUIRED"
    )

    f2r1_contract_path = Path(bindings["f2r1_contract"]["path"])
    f2r1_result_path = Path(bindings["f2r1_confirmatory"]["path"])
    f2_initial_path = Path(bindings["f2_initial_exploratory"]["path"])
    f2r1_contract = load(f2r1_contract_path)
    f2r1 = load(f2r1_result_path)
    f2_initial = load(f2_initial_path)

    sci = d["scientific_contract"]
    fresh = sci["fresh_units"]
    model = sci["model"]
    frozen_model = f2r1_contract["model"]

    checks["future_tasks_frozen"] = sci["frozen_future_tasks"] == f2r1_contract["future_tasks"] == ["164", "385", "387", "388"]
    checks["source_tasks_comparison_only_frozen"] = sci["frozen_source_memory_tasks_for_comparison_only"] == f2r1_contract["source_memory_tasks"] == ["21", "22", "23", "25"]
    checks["f2r1_had_no_confirmatory_no_memory"] = (
        f2r1_contract["design"]["no_memory_rollouts_per_task"] == 0
        and f2r1["summary"]["requested_no_memory_calls"] == 0
    )
    checks["old_no_memory_is_exploratory_only"] = (
        f2_initial["summary"]["requested_no_memory_calls"] == 12
        and fresh["existing_exploratory_no_memory_calls_reused"] == 0
        and fresh["existing_exploratory_no_memory_calls_excluded"] == 12
    )
    checks["minimal_32_call_scope"] = (
        fresh["rollouts_per_future_task"] == 8
        and fresh["future_task_count"] == 4
        and fresh["total_new_provider_calls"] == 32
        and fresh["source_dimension_duplicated"] is False
        and d["economy"]["new_provider_calls_if_authorized"] == 32
        and d["economy"]["avoided_redundant_calls_vs_naive_16_cell_replication"] == 96
    )
    checks["exact_model_match"] = all([
        model["requested"] == frozen_model["requested"] == "doubao-seed-2.0-mini",
        model["temperature"] == frozen_model["temperature"] == 0.2,
        model["max_output_tokens"] == frozen_model["max_output_tokens"] == 900,
        model["thinking"] == frozen_model["thinking"] == "disabled",
        model["allow_thinking_compatibility_fallback"] is frozen_model["allow_thinking_compatibility_fallback"] is False,
        model["provider_retries"] == frozen_model["provider_retries"] == 0,
        model["store"] is frozen_model["store"] is True,
        model["substitution_allowed"] is False,
    ])
    evidence = sci["evidence_and_evaluator"]
    src = f2r1_contract["source_artifacts"]
    checks["exact_evidence_and_evaluator_match"] = all([
        evidence["fixed_evidence_support_sha256"] == src["support_sha256"],
        evidence["parquet_sha256"] == src["parquet_sha256"],
        evidence["task_config_sha256"] == src["task_config_sha256"],
        evidence["evaluator_source_sha256"] == src["evaluator_source_sha256"],
        evidence["must_match_f2r1"] is True,
    ])
    checks["primary_estimand_unchanged"] = (
        sci["primary_f2r1_estimand_unchanged"] == f2r1_contract["terminal_gate"]["primary_statistic"]
        and sci["o5_estimand_class"] == "secondary control / branch-location diagnostic"
        and sci["o5_does_not_replace_primary_gate"] is True
        and sci["o5_does_not_create_three_arm_method_claim"] is True
    )
    checks["no_pseudoreplication"] = (
        "must never be counted four times as independent evidence" in sci["source_independence"]
        and d["analysis_contract"]["global_p_value_required"] is False
        and "pseudo-independent" in d["analysis_contract"]["reason_no_global_gate"]
    )
    checks["missingness_fail_closed"] = all([
        sci["missingness_policy"]["provider_retries"] == 0,
        sci["missingness_policy"]["regenerate_failed_units"] is False,
        sci["missingness_policy"]["impute_failed_units"] is False,
        sci["missingness_policy"]["replace_future_task"] is False,
    ])
    checks["no_claim_expansion"] = (
        d["authority"]["claim_expansion_authority"] is False
        and any("three-arm randomized causal effect" in x for x in d["claim_boundary"]["forbidden"])
        and any("cross-model" in x for x in d["claim_boundary"]["forbidden"])
    )
    checks["no_training_or_gpu"] = d["economy"]["new_training_runs"] == 0 and d["economy"]["new_gpu_finetuning_runs"] == 0

    passed = all(checks.values())
    out = {
        "schema_version": "1.0",
        "artifact_type": "targeted-scientific-reopen-design-qa",
        "paper_id": d["paper_id"],
        "objection_id": d["objection_id"],
        "design_sha256": sha256(DESIGN),
        "status": "PASS" if passed else "FAIL",
        "checks": checks,
        "summary": {
            "passed": sum(checks.values()),
            "total": len(checks),
            "new_provider_calls_permitted_now": 0,
            "new_provider_call_ceiling_if_separately_authorized": 32,
        },
    }
    QA.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
