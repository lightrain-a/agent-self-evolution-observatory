from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .paper_first_p0_config_factory import CONFIG_NAMES
from .paper_quality_gate import audit_paper_evidence_plan

STRI_QUALITY = PROJECT_ROOT / "generated" / "asset-first-stri-paper-quality-v2-20260816.json"

POLICY = {
    "schema_version": "1.0",
    "visual_portfolio_is_design_and_manuscript_state_only": True,
    "visual_portfolio_has_zero_scientific_authority": True,
    "visual_plan_cannot_authorize_experiment_p0_or_gpu": True,
    "main_visuals_are_reviewer_question_driven_not_decorative": True,
    "visual_completion_requires_data_script_figure_caption_binding": True,
}


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _planned_rows(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idea_id, filename in CONFIG_NAMES.items():
        config = _load(root / "research_pipeline" / filename)
        paper_design = ((config.get("pre_experiment") or {}).get("paper_design") or {})
        quality = paper_design.get("evidence_quality") or {}
        method = paper_design.get("method") or {}
        audit = audit_paper_evidence_plan(quality, method_components=len(method.get("components") or []))
        summary = audit.get("summary") or {}
        visuals = [row for row in quality.get("visualizations") or [] if isinstance(row, dict)]
        rows.append({
            "paper_id": idea_id,
            "source": f"research_pipeline/{filename}",
            "status": "PLANNED_VISUAL_EVIDENCE_READY" if audit.get("passed") is True else "VISUAL_EVIDENCE_REPAIR_REQUIRED",
            "paper_archetype": summary.get("paper_archetype"),
            "planned_visualizations": int(summary.get("visualizations") or 0),
            "planned_main_visualizations": int(summary.get("main_visualizations") or 0),
            "main_visual_roles": list(summary.get("main_visual_roles") or []),
            "reviewer_questions": [str(row.get("reviewer_question") or "") for row in visuals if str(row.get("reviewer_question") or "").strip()],
            "scientific_authority": False,
            "authority": {"method": False, "experiment": False, "p0": False, "gpu": False},
        })
    return rows


def _stri_row(root: Path) -> dict[str, Any]:
    state = _load(root / "generated" / "asset-first-stri-paper-quality-v2-20260816.json")
    plan = (((state.get("audit") or {}).get("plan") or {}).get("summary") or {})
    completion = state.get("completion") or {}
    completed_visuals = [row for row in completion.get("visualizations") or [] if isinstance(row, dict)]
    return {
        "paper_id": "STRI",
        "source": "generated/asset-first-stri-paper-quality-v2-20260816.json",
        "status": "COMPLETED_VISUAL_EVIDENCE_PASS" if state.get("paper_quality_gate_passed") is True else "VISUAL_EVIDENCE_REPAIR_REQUIRED",
        "paper_archetype": plan.get("paper_archetype"),
        "planned_visualizations": int(plan.get("visualizations") or 0),
        "planned_main_visualizations": int(plan.get("main_visualizations") or 0),
        "completed_main_visualizations": sum(str(row.get("status") or "") in {"PASS", "FAIL", "INCONCLUSIVE"} for row in completed_visuals),
        "main_visual_roles": list(plan.get("main_visual_roles") or []),
        "reviewer_questions": [str(row.get("reviewer_question") or "") for row in ((state.get("quality_contract") or {}).get("visualizations") or []) if isinstance(row, dict) and str(row.get("reviewer_question") or "").strip()],
        "source_bound": bool(state.get("source_sha256")) and not ((state.get("evidence_debt") or {}).get("missing_or_incomplete_ids") or []),
        "scientific_authority": False,
        "authority": {"method": False, "experiment": False, "p0": False, "gpu": False},
    }


def build_paper_visual_evidence_portfolio(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    planned = _planned_rows(project_root)
    stri = _stri_row(project_root)
    papers = planned + [stri]
    role_union = sorted({role for row in papers for role in row.get("main_visual_roles") or []})
    return {
        "schema_version": "1.0",
        "status": "VISUAL_EVIDENCE_PORTFOLIO_READY" if all("REPAIR" not in str(row.get("status")) for row in papers) else "VISUAL_EVIDENCE_PORTFOLIO_REPAIR_REQUIRED",
        "summary": {
            "papers": len(papers),
            "paper_first_designs": len(planned),
            "planned_main_visualizations": sum(int(row.get("planned_main_visualizations") or 0) for row in planned),
            "planned_main_visualizations_per_paper_min": min((int(row.get("planned_main_visualizations") or 0) for row in planned), default=0),
            "stri_completed_main_visualizations": int(stri.get("completed_main_visualizations") or 0),
            "main_visual_roles": role_union,
            "repair_required": sum("REPAIR" in str(row.get("status")) for row in papers),
        },
        "papers": papers,
        "policy": dict(POLICY),
        "scientific_authority": False,
        "authority": {"paper_design": False, "method": False, "experiment": False, "p0": False, "gpu": False},
    }
