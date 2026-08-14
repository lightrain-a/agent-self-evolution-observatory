from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

SPEC_PATH = PROJECT_ROOT / "research_pipeline" / "paper_first_shadow_near_miss_preflight.json"
DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-shadow-near-miss-preflight.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "paper-first-shadow-near-miss-preflight.js"
ALLOWED_DISPOSITIONS = {"HOLD_SUPPORT_UNAVAILABLE", "STOP_CURRENT_PRIMARY_COLLISION"}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load(path: Path = SPEC_PATH) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def build_shadow_near_miss_preflight(spec_path: Path = SPEC_PATH) -> dict[str, Any]:
    spec = _load(spec_path)
    receipts = [dict(row) for row in spec.get("receipts") or [] if isinstance(row, dict)]
    state = {
        "schema_version": "1.0",
        "generated_at": _now(),
        "audit_id": str(spec.get("audit_id") or ""),
        "policy": {
            "shadow_search_control_only": True,
            "current_primary_collision_and_support_absence_are_distinct_dispositions": True,
            "support_absence_is_not_scientific_falsification": True,
            "current_primary_collision_can_stop_a_shadow_basin": True,
            "receipt_reopen_condition_required": True,
            "cannot_mutate_canonical_generator_or_queue": True,
            "cannot_grant_live_paper_design_authority": True,
            "automatic_problem_gate_authority": False,
            "automatic_method_authority": False,
            "automatic_experiment_authority": False,
            "automatic_p0_authority": False,
            "automatic_gpu_authority": False,
        },
        "summary": {
            "receipts": len(receipts),
            "support_holds": sum(str(row.get("disposition") or "") == "HOLD_SUPPORT_UNAVAILABLE" for row in receipts),
            "current_primary_stops": sum(str(row.get("disposition") or "") == "STOP_CURRENT_PRIMARY_COLLISION" for row in receipts),
            "problem_gate_authorized": 0,
            "method_authorized": 0,
            "experiment_authorized": 0,
            "p0_authorized": 0,
            "gpu_authorized": 0,
        },
        "receipts": receipts,
        "scientific_authority": False,
    }
    errors = validate_shadow_near_miss_preflight(state)
    if errors:
        raise ValueError("Invalid shadow near-miss preflight:\n- " + "\n- ".join(errors))
    return state


def validate_shadow_near_miss_preflight(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    policy = state.get("policy") or {}
    summary = state.get("summary") or {}
    receipts = [row for row in state.get("receipts") or [] if isinstance(row, dict)]
    if state.get("scientific_authority") is not False:
        errors.append("near-miss preflight must have zero scientific authority")
    if policy.get("shadow_search_control_only") is not True or policy.get("cannot_mutate_canonical_generator_or_queue") is not True or policy.get("cannot_grant_live_paper_design_authority") is not True:
        errors.append("near-miss preflight must remain shadow-only search control")
    if any(policy.get(key) is not False for key in ("automatic_problem_gate_authority", "automatic_method_authority", "automatic_experiment_authority", "automatic_p0_authority", "automatic_gpu_authority")):
        errors.append("near-miss preflight cannot authorize downstream work")
    ids: set[str] = set()
    for row in receipts:
        cid = str(row.get("source_candidate_id") or "").strip()
        disposition = str(row.get("disposition") or "").strip()
        refs = [str(ref) for ref in row.get("evidence_basis") or [] if str(ref)]
        if not cid or cid in ids:
            errors.append("near-miss receipt candidate ids must be unique and nonempty")
        ids.add(cid)
        if disposition not in ALLOWED_DISPOSITIONS:
            errors.append(f"near-miss disposition invalid:{cid}:{disposition}")
        if not str(row.get("search_primitive") or "").strip() or not str(row.get("strongest_reduction") or "").strip() or not str(row.get("reason") or "").strip() or not str(row.get("reopen_only_if") or "").strip():
            errors.append(f"near-miss receipt incomplete:{cid}")
        if not refs or any(not ref.startswith("arXiv:") for ref in refs):
            errors.append(f"near-miss receipt requires primary refs:{cid}")
        if row.get("scientific_authority") is not False or any(row.get(key) is not False for key in ("automatic_problem_gate_authority", "automatic_method_authority", "automatic_experiment_authority", "automatic_p0_authority", "automatic_gpu_authority")):
            errors.append(f"near-miss receipt illegally authoritative:{cid}")
    if int(summary.get("receipts") or 0) != len(receipts) or int(summary.get("support_holds") or 0) + int(summary.get("current_primary_stops") or 0) != len(receipts):
        errors.append("near-miss preflight summary accounting mismatch")
    if any(int(summary.get(key) or 0) != 0 for key in ("problem_gate_authorized", "method_authorized", "experiment_authorized", "p0_authorized", "gpu_authorized")):
        errors.append("near-miss preflight summary cannot authorize downstream work")
    return sorted(set(errors))


def compile_shadow_dead_end_rows(state: dict[str, Any]) -> list[dict[str, Any]]:
    errors = validate_shadow_near_miss_preflight(state)
    if errors:
        raise ValueError("Invalid shadow near-miss preflight:\n- " + "\n- ".join(errors))
    rows = []
    for receipt in state.get("receipts") or []:
        disposition = str(receipt.get("disposition") or "")
        rows.append({
            "source_candidate_id": str(receipt.get("source_candidate_id") or ""),
            "basin": "near-miss-support-hold" if disposition == "HOLD_SUPPORT_UNAVAILABLE" else "near-miss-current-primary-collision",
            "search_primitive": str(receipt.get("search_primitive") or ""),
            "disposition": disposition,
            "avoid": [str(value) for value in receipt.get("avoid") or [] if str(value)],
            "strongest_reduction": str(receipt.get("strongest_reduction") or ""),
            "current_source_refs": [str(ref) for ref in receipt.get("evidence_basis") or [] if str(ref)],
            "support_status": str(receipt.get("support_status") or ""),
            "reason": str(receipt.get("reason") or ""),
            "reopen_only_if": str(receipt.get("reopen_only_if") or ""),
            "scientific_authority": False,
        })
    return rows


def write_shadow_near_miss_preflight(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    state = build_shadow_near_miss_preflight()
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.PAPER_FIRST_SHADOW_NEAR_MISS_PREFLIGHT = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    print(json.dumps(write_shadow_near_miss_preflight(), ensure_ascii=False, indent=2))
