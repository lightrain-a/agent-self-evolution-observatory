from __future__ import annotations

from typing import Any

from .paper_first_global_relation_recall import load_global_relation_recall_state
from .paper_first_primary_evidence import load_primary_evidence_state
from .paper_first_problem_generator import load_problem_generator_state
from .paper_first_relation_coverage import relation_recall_freshness
from .paper_first_relation_delta_preflight import load_private_relation_delta_preflight, public_relation_delta_preflight_summary


def build_global_relation_scan_admission(
    *,
    primary_state: dict[str, Any] | None = None,
    generator_state: dict[str, Any] | None = None,
    relation_state: dict[str, Any] | None = None,
    delta_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Deterministic preconditions for an explicitly requested relation-model scan.

    Passing this contract never authorizes a model call by itself. It only says
    the current search-control state makes a manual scan non-redundant and
    auditable. The caller must still be in manual mode with an explicit operator
    flag. No scientific or downstream authority is granted here.
    """
    primary = primary_state if primary_state is not None else load_primary_evidence_state()
    generator = generator_state if generator_state is not None else load_problem_generator_state()
    relation = relation_state if relation_state is not None else load_global_relation_recall_state()
    delta_private = delta_state if delta_state is not None else load_private_relation_delta_preflight()
    delta = public_relation_delta_preflight_summary(delta_private)
    freshness = relation_recall_freshness(generator, relation)

    ps = primary.get("summary") or {}
    fs = freshness.get("summary") or {}
    ds = delta.get("summary") or {}
    typed_delta = sum(int(ds.get(key) or 0) for key in (
        "new_empirical_sources",
        "new_assumption_sources",
        "new_failure_sources",
        "new_boundary_sources",
    ))
    checks = [
        {"key":"live-primary-ready","pass":primary.get("status")=="READY"},
        {"key":"live-retrieval-complete","pass":ps.get("source_retrieval_complete") is True},
        {"key":"live-source-coverage-exhausted","pass":ps.get("source_coverage_exhausted") is True},
        {"key":"carrier-probe-complete","pass":ps.get("carrier_probe_complete",True) is True},
        {"key":"canonical-generator-terminal-zero-call","pass":generator.get("status")=="SKIPPED_SOURCE_COVERAGE_SATURATED" and int((generator.get("summary") or {}).get("generated") or 0)==0},
        {"key":"relation-universe-stale","pass":freshness.get("status")=="STALE_RELATION_UNIVERSE" and fs.get("universe_stale") is True},
        {"key":"relation-blind-spot-remains","pass":fs.get("current_relation_blind_spot") is True},
        {"key":"current-relation-result-unknown","pass":fs.get("current_not_reduced_unknown") is True},
        {"key":"no-focused-reopen-already-authorized","pass":fs.get("focused_problem_generator_reopen_allowed") is False},
        {"key":"typed-delta-preflight-complete","pass":delta.get("status")=="RELATION_DELTA_TYPED_PREFLIGHT_COMPLETE"},
        {"key":"relation-delta-cache-complete","pass":int(ds.get("cache_missing_sources") or 0)==0},
        {"key":"new-reviewed-source-delta-nonzero","pass":int(ds.get("new_reviewed_sources") or 0)>0},
        {"key":"new-typed-evidence-delta-nonzero","pass":typed_delta>0},
        {"key":"delta-has-zero-model-authority","pass":ds.get("model_scan_authorized") is False},
        {"key":"delta-has-zero-reopen-authority","pass":ds.get("focused_generator_reopen_authorized") is False},
    ]
    failed = [row["key"] for row in checks if row["pass"] is not True]
    eligible = not failed
    return {
        "schema_version":"1.0",
        "status":"ELIGIBLE_FOR_EXPLICIT_MANUAL_RELATION_SCAN" if eligible else "HOLD_MANUAL_RELATION_SCAN",
        "policy":{
            "scientific_authority":False,
            "automatic_model_scan_authority":False,
            "manual_execution_requires_explicit_operator_flag":True,
            "manual_eligibility_is_not_scientific_authority":True,
            "relation_scan_cannot_authorize_problem_gate":True,
            "relation_scan_cannot_authorize_method_experiment_p0_gpu":True,
            "preconditions_are_deterministic_search_control_only":True,
        },
        "summary":{
            "checks":len(checks),
            "passed":len(checks)-len(failed),
            "failed":len(failed),
            "manual_scan_eligible":eligible,
            "automatic_model_scan_authorized":False,
            "new_reviewed_sources":int(ds.get("new_reviewed_sources") or 0),
            "new_empirical_sources":int(ds.get("new_empirical_sources") or 0),
            "new_assumption_sources":int(ds.get("new_assumption_sources") or 0),
            "new_failure_sources":int(ds.get("new_failure_sources") or 0),
            "new_boundary_sources":int(ds.get("new_boundary_sources") or 0),
            "current_reviewed_sources":int(fs.get("current_reviewed_sources") or 0),
            "last_scanned_sources":int(fs.get("last_scanned_sources") or 0),
        },
        "checks":checks,
        "failed_checks":failed,
        "freshness_status":freshness.get("status"),
        "delta_status":delta.get("status"),
        "scientific_authority":False,
    }
