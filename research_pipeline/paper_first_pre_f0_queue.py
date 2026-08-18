from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .paper_first_problem_generator import DEFAULT_JSON as GENERATOR_JSON, load_problem_generator_state

DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-pre-f0-queue.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "paper-first-pre-f0-queue.js"

AUTHORITY = {
    "problem_gate": False,
    "paper_design": False,
    "method": False,
    "experiment": False,
    "p0": False,
    "gpu": False,
}

POLICY = {
    "canonical_double_funnel_pre_f0_queue": True,
    "source_must_be_canonical_problem_generator": True,
    "queue_accepts_only_reduction_limited_candidates": True,
    "cheap_falsifier_is_evidence_acquisition_not_problem_gate": True,
    "principle_reduction_may_leave_non_principle_paperability_axis_open": True,
    "principle_reduction_does_not_by_itself_authorize_non_principle_claim": True,
    "support_unavailable_is_support_stop_not_scientific_negative": True,
    "protocol_failure_is_protocol_stop_not_scientific_negative": True,
    "realization_failure_is_realization_stop_not_scientific_negative": True,
    "positive_f0_requires_exact_same_information_reduction_recheck": True,
    "exact_reduction_required_before_problem_gate": True,
    "pre_f0_cannot_enter_persistent_dead_end_memory": True,
    "automatic_provider_calls_authorized": False,
    "automatic_method_authority": False,
    "automatic_experiment_authority": False,
    "automatic_p0_authority": False,
    "automatic_gpu_authority": False,
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_pre_f0_queue(generator: dict[str, Any]) -> dict[str, Any]:
    policy = generator.get("policy") or {}
    source_rows = [row for row in generator.get("pre_f0_candidates") or [] if isinstance(row, dict)]
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for source in source_rows:
        candidate_id = str(source.get("candidate_id") or "").strip()
        if not candidate_id or candidate_id in seen:
            raise ValueError("pre-F0 candidate ids must be nonempty and unique")
        seen.add(candidate_id)
        authority = source.get("authority") or {}
        if source.get("scientific_authority") is not False or any(authority.get(key) is not False for key in ("paper_design", "method", "experiment", "p0", "gpu")):
            raise ValueError(f"pre-F0 source candidate leaks downstream authority: {candidate_id}")
        falsifier = " ".join(str(source.get("cheapest_problem_falsifier") or "").split())
        strongest = " ".join(str(source.get("strongest_same_information_baseline") or "").split())
        prediction = " ".join(str(source.get("exact_prediction") or "").split())
        surviving = [str(axis) for axis in source.get("surviving_paperability_axes") or [] if str(axis) in {"P", "M", "E", "B", "T", "S"}]
        blockers = [str(value) for value in source.get("reduction_blockers") or [] if str(value)]
        primary_refs=sorted({str(ref).strip() for ref in source.get("primary_refs") or [] if str(ref).strip().startswith("arXiv:")})
        if not falsifier or not strongest or not prediction or not surviving or not blockers or not primary_refs:
            raise ValueError(f"pre-F0 source candidate is incomplete: {candidate_id}")
        if str(source.get("post_f0_requirement") or "") != "RERUN_EXACT_SAME_INFORMATION_REDUCTION_BEFORE_PROBLEM_GATE":
            raise ValueError(f"pre-F0 candidate misses post-F0 exact-reduction obligation: {candidate_id}")
        rows.append({
            "candidate_id": candidate_id,
            "title": str(source.get("title") or "").strip(),
            "discovery_lane": str(source.get("discovery_lane") or "").strip(),
            "source_branch_id": str(source.get("source_branch_id") or "").strip(),
            "primary_refs": primary_refs,
            "paperability_axes": dict(source.get("paperability_axes") or {}),
            "surviving_paperability_axes": surviving,
            "non_principle_surviving_axes": [str(axis) for axis in source.get("non_principle_surviving_axes") or [] if str(axis) in {"M", "E", "B", "T", "S"}],
            "route_reason": str(source.get("route_reason") or "").strip(),
            "reduction_blockers": blockers,
            "exact_prediction": prediction,
            "strongest_same_information_baseline": strongest,
            "cheapest_problem_falsifier": falsifier,
            "endpoint_headroom_requirement": " ".join(str(source.get("endpoint_headroom_requirement") or "").split()),
            "next_if_positive": "RERUN_EXACT_SAME_INFORMATION_REDUCTION",
            "next_if_support_missing": "SUPPORT_STOP_OR_BOUNDED_SUPPORT_ACQUISITION",
            "next_if_protocol_invalid": "PROTOCOL_STOP_AND_REPAIR",
            "next_if_realization_fails": "REALIZATION_STOP_AND_REPAIR",
            "scientific_authority": False,
            "authority": dict(AUTHORITY),
        })
    if rows and policy.get("search_portfolio_enabled") is not True:
        raise ValueError("pre-F0 queue cannot be sourced from a non-double-funnel generator")
    if rows and policy.get("exact_reduction_required_before_final_problem_gate") is not True:
        raise ValueError("source generator does not preserve final exact-reduction gate")
    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "source_generator_run_id": str(generator.get("run_id") or ""),
        "source_generator_status": str(generator.get("status") or ""),
        "status": "PRE_F0_QUEUE_READY" if rows else "PRE_F0_QUEUE_EMPTY",
        "policy": dict(POLICY),
        "summary": {
            "queued": len(rows),
            "problem_gate_authorized": 0,
            "paper_design_authorized": 0,
            "method_authorized": 0,
            "experiment_authorized": 0,
            "p0_authorized": 0,
            "gpu_authorized": 0,
        },
        "rows": rows,
        "scientific_authority": False,
        "authority": dict(AUTHORITY),
    }


def write_pre_f0_queue(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS, *, generator_state: dict[str, Any] | None = None) -> dict[str, Any]:
    state = build_pre_f0_queue(generator_state if generator_state is not None else load_problem_generator_state(GENERATOR_JSON))
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.PAPER_FIRST_PRE_F0_QUEUE = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return state


def load_pre_f0_queue(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    if not path.exists():
        return build_pre_f0_queue({"policy": {}, "pre_f0_candidates": []})
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"schema_version": "1.0", "status": "STATE_UNREADABLE", "policy": dict(POLICY), "summary": {"queued": 0}, "rows": [], "scientific_authority": False, "authority": dict(AUTHORITY)}
    return payload if isinstance(payload, dict) else {"schema_version": "1.0", "status": "STATE_INVALID", "policy": dict(POLICY), "summary": {"queued": 0}, "rows": [], "scientific_authority": False, "authority": dict(AUTHORITY)}


if __name__ == "__main__":
    print(json.dumps(write_pre_f0_queue(), ensure_ascii=False, indent=2))
