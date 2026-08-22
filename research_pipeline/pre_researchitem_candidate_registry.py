#!/usr/bin/env python3
"""Read-only registry for ProblemGate-passed candidates not yet promoted to ResearchItem/PaperState.

The purpose of this projection is to close a control-plane blind spot: a paper-design
candidate may already be canonical and visible on a consumer surface while remaining
correctly absent from the A-G ResearchItem and PaperState ledgers.  Such objects must
be enumerable without changing their scientific or execution authority.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _contains_exact_id(value: Any, candidate_id: str) -> bool:
    if isinstance(value, dict):
        return any(_contains_exact_id(item, candidate_id) for item in value.values())
    if isinstance(value, list):
        return any(_contains_exact_id(item, candidate_id) for item in value)
    return isinstance(value, str) and value == candidate_id


def _js_global(js_path: Path) -> str | None:
    if not js_path.exists():
        return None
    match = re.match(r"\s*window\.([A-Za-z0-9_]+)\s*=", js_path.read_text(encoding="utf-8"))
    return match.group(1) if match else None


def _title(value: Any) -> dict[str, str]:
    if isinstance(value, dict):
        return {"zh": str(value.get("zh") or value.get("en") or ""), "en": str(value.get("en") or value.get("zh") or "")}
    text = str(value or "")
    return {"zh": text, "en": text}


def build_pre_researchitem_candidate_registry(root: Path) -> dict[str, Any]:
    generated = root / "generated"
    research_items = _load_json(generated / "research-items.json")
    paper_registry = _load_json(generated / "paper-registry.json")
    paper_ideas_html = (root / "paper-ideas.html").read_text(encoding="utf-8") if (root / "paper-ideas.html").exists() else ""
    app_js = (root / "app.js").read_text(encoding="utf-8") if (root / "app.js").exists() else ""

    candidates: list[dict[str, Any]] = []
    promoted: list[dict[str, Any]] = []
    for sidecar in sorted(generated.glob("*paper*design*.json")):
        state = _load_json(sidecar)
        candidate_id = str(state.get("candidate_id") or "").strip()
        problem_gate_status = str(state.get("problem_gate_status") or "").strip()
        paper_design_status = str(state.get("paper_design_status") or "").strip()
        if not candidate_id or not paper_design_status or "PASS" not in problem_gate_status.upper():
            continue

        research_item_promoted = _contains_exact_id(research_items.get("research_items") or [], candidate_id)
        paper_state_entered = _contains_exact_id(paper_registry.get("papers") or [], candidate_id)
        js_sidecar = sidecar.with_suffix(".js")
        global_name = _js_global(js_sidecar)
        script_loaded = js_sidecar.exists() and f'generated/{js_sidecar.name}' in paper_ideas_html
        consumer_bound = bool(global_name and f"window.{global_name}" in app_js)
        consumer_live = bool(script_loaded and consumer_bound)

        f0 = state.get("f0_contract") or {}
        runtime = state.get("runtime_support") or {}
        source_integrity = state.get("source_integrity") or {}
        design_audit = state.get("paper_design_audit") or {}
        authority = state.get("authority") or {}
        row = {
            "candidate_id": candidate_id,
            "title": _title(state.get("title")),
            "lifecycle_status": state.get("status"),
            "problem_gate_status": problem_gate_status,
            "paper_design_status": paper_design_status,
            "paper_design_audit_passed": bool(design_audit.get("passed", False)),
            "source_integrity_passed": bool(source_integrity.get("passed", False)),
            "source_sidecar": str(sidecar.relative_to(root)),
            "contract_sha256": state.get("contract_sha256"),
            "canonical_consumer_surface": {
                "live": consumer_live,
                "page": "paper-ideas.html" if consumer_live else None,
                "script_loaded": script_loaded,
                "consumer_bound": consumer_bound,
                "js_global": global_name,
            },
            "promotion": {
                "research_item": research_item_promoted,
                "paper_state": paper_state_entered,
                "paper_registry": paper_state_entered,
                "promotion_decision_required": not research_item_promoted and not paper_state_entered,
            },
            "experiment_gate": {
                "status": state.get("execution_status") or runtime.get("status"),
                "stage": f0.get("stage"),
                "units": int(f0.get("units") or 0),
                "arms_per_unit": int(f0.get("arms_per_unit") or 0),
                "episodes": int(f0.get("episodes") or 0),
                "full_audit_unlock": f0.get("full_audit_unlock"),
                "blocker": runtime.get("status"),
                "required_official_stack": list(runtime.get("required_official_stack") or []),
                "proxy_policy": runtime.get("proxy_policy"),
            },
            "authority": {
                "scientific": bool(authority.get("scientific", False)),
                "method": bool(authority.get("method", False)),
                "experiment": bool(authority.get("experiment_blueprint_execution", authority.get("experiment", False))),
                "local_validation": bool(authority.get("local_validation", False)),
                "p0": bool(authority.get("p0", False)),
                "gpu": bool(authority.get("gpu", False)),
                "full_experiment": bool(authority.get("full_experiment", False)),
            },
        }
        if research_item_promoted or paper_state_entered:
            promoted.append(row)
        else:
            candidates.append(row)

    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "policy": {
            "read_only_projection": True,
            "scientific_authority": False,
            "experiment_authority": False,
            "promotion_authority": False,
            "problem_gate_pass_does_not_imply_research_item": True,
            "canonical_consumer_surface_does_not_imply_paper_state": True,
            "promotion_requires_explicit_source_ledger_transition": True,
        },
        "summary": {
            "problem_gate_passed_paper_design_sidecars": len(candidates) + len(promoted),
            "pre_researchitem_candidates": len(candidates),
            "canonical_consumer_surface_live": sum(bool(row["canonical_consumer_surface"]["live"]) for row in candidates),
            "research_item_promoted": sum(bool(row["promotion"]["research_item"]) for row in promoted),
            "paper_state_entered": sum(bool(row["promotion"]["paper_state"]) for row in promoted),
            "experiment_holds": sum("HOLD" in str(row["experiment_gate"]["status"]).upper() for row in candidates),
        },
        "candidates": candidates,
        "promoted": promoted,
    }


def validate_pre_researchitem_candidate_registry(registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    policy = registry.get("policy") or {}
    if policy.get("read_only_projection") is not True:
        errors.append("registry must be read-only")
    for key in ("scientific_authority", "experiment_authority", "promotion_authority"):
        if policy.get(key) is not False:
            errors.append(f"{key} must remain false")
    seen: set[str] = set()
    for row in registry.get("candidates") or []:
        candidate_id = str(row.get("candidate_id") or "")
        if not candidate_id or candidate_id in seen:
            errors.append(f"invalid/duplicate candidate_id: {candidate_id!r}")
            continue
        seen.add(candidate_id)
        if "PASS" not in str(row.get("problem_gate_status") or "").upper():
            errors.append(f"{candidate_id}: candidate is not ProblemGate-passed")
        promotion = row.get("promotion") or {}
        if promotion.get("research_item") is not False or promotion.get("paper_state") is not False:
            errors.append(f"{candidate_id}: pre-ResearchItem row cannot already be promoted")
        if not (row.get("canonical_consumer_surface") or {}).get("live", False):
            errors.append(f"{candidate_id}: canonical candidate is not bound to a live consumer surface")
        if any(bool(v) for v in (row.get("authority") or {}).values()):
            errors.append(f"{candidate_id}: sidecar candidate unexpectedly grants execution/scientific authority")
    summary = registry.get("summary") or {}
    if int(summary.get("pre_researchitem_candidates") or 0) != len(registry.get("candidates") or []):
        errors.append("pre_researchitem candidate count is stale")
    return errors
