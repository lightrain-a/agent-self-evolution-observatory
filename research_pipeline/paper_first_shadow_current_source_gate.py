from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REVIEWER = "web-gpt-current-source-review"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_receipt(payload: dict[str, Any], *, candidate_id: str) -> dict[str, Any]:
    declared_reviewer = str(payload.get("reviewer") or "").strip()
    raw_sha256 = str(payload.get("raw_sha256") or "").strip().lower()
    provenance_ok = declared_reviewer == REVIEWER and bool(re.fullmatch(r"[0-9a-f]{64}", raw_sha256))
    verdict = str(payload.get("verdict") or "BLOCK").strip().upper()
    reduction_class = str(payload.get("reduction_class") or "NEEDS_EXACT_REDUCTION_TEST").strip().upper()
    if verdict not in {"CLEAR", "BLOCK"}:
        verdict = "BLOCK"
    if reduction_class not in {"NONE", "SOFT_COLLISION", "NEEDS_EXACT_REDUCTION_TEST", "VALID_HARD_VETO"}:
        reduction_class = "NEEDS_EXACT_REDUCTION_TEST"
        verdict = "BLOCK"
    if reduction_class in {"NEEDS_EXACT_REDUCTION_TEST", "VALID_HARD_VETO"}:
        verdict = "BLOCK"
    if not provenance_ok:
        verdict = "BLOCK"
    sources = []
    for row in payload.get("sources") or []:
        if not isinstance(row, dict):
            continue
        url = str(row.get("url") or "").strip()
        if not url.startswith(("https://", "http://")):
            continue
        sources.append({
            "ref": str(row.get("ref") or "").strip(),
            "title": str(row.get("title") or "").strip(),
            "url": url,
            "claim": " ".join(str(row.get("claim") or "").split())[:800],
        })
    return {
        "reviewer": declared_reviewer or "missing-reviewer",
        "status": "complete" if provenance_ok else "invalid-provenance",
        "review_origin": str(payload.get("review_origin") or "").strip(),
        "raw_sha256": raw_sha256,
        "candidate_id": candidate_id,
        "verdict": verdict,
        "risk_level": str(payload.get("risk_level") or "high").strip().lower(),
        "current_source_collision_found": bool(payload.get("current_source_collision_found")),
        "provenance_valid": provenance_ok,
        "sources": sources,
        "reduction_class": reduction_class,
        "strongest_reduction": " ".join(str(payload.get("strongest_reduction") or "").split())[:1200],
        "reason": " ".join(str(payload.get("reason") or "").split())[:1800],
        "scientific_authority": False,
        "authority": {"live_problem_gate": False, "paper_design": False, "method": False, "experiment": False, "p0": False, "gpu": False},
    }


def missing_receipt(candidate_id: str, error: str) -> dict[str, Any]:
    return {
        "reviewer": REVIEWER,
        "status": "missing",
        "candidate_id": candidate_id,
        "verdict": None,
        "error": error[-1200:],
        "scientific_authority": False,
        "authority": {"live_problem_gate": False, "paper_design": False, "method": False, "experiment": False, "p0": False, "gpu": False},
    }


def compile_terminal(shadow_final: dict[str, Any], current_reviews: list[dict[str, Any]]) -> dict[str, Any]:
    reviews = {str(row.get("candidate_id") or ""): row for row in current_reviews if isinstance(row, dict)}
    rows = []
    semantic_clear = current_clear = current_blocked = current_missing = 0
    for item in shadow_final.get("rows") or []:
        if not isinstance(item, dict):
            continue
        candidate_id = str(item.get("candidate_id") or "")
        shadow_clear = item.get("shadow_clear") is True
        semantic_clear += int(shadow_clear)
        review = reviews.get(candidate_id) if shadow_clear else None
        if shadow_clear and review is None:
            review = missing_receipt(candidate_id, "current-source-review-not-run")
        terminal_clear = bool(shadow_clear and review and review.get("status") == "complete" and review.get("verdict") == "CLEAR")
        if shadow_clear:
            current_clear += int(terminal_clear)
            current_missing += int(bool(review and review.get("status") != "complete"))
            current_blocked += int(bool(review and review.get("status") == "complete" and review.get("verdict") != "CLEAR"))
        rows.append({
            "candidate_id": candidate_id,
            "search_primitive": item.get("search_primitive"),
            "semantic_shadow_clear": shadow_clear,
            "current_source_review": review,
            "terminal_shadow_clear": terminal_clear,
            "live_problem_gate_compatible": bool(item.get("live_problem_gate_compatible")) and terminal_clear,
            "live_paper_design_eligible": False,
        })
    return {
        "schema_version": "1.0-shadow",
        "generated_at": _now(),
        "status": "SHADOW_TERMINAL_COMPLETE" if current_missing == 0 else "SHADOW_TERMINAL_INCOMPLETE_CURRENT_SOURCE_REVIEW",
        "summary": {
            "semantic_shadow_clear": semantic_clear,
            "current_source_clear": current_clear,
            "current_source_blocked": current_blocked,
            "current_source_missing": current_missing,
            "terminal_shadow_survivors": current_clear,
            "live_problem_gate_compatible_survivors": sum(row["live_problem_gate_compatible"] for row in rows),
            "live_paper_design_eligible": 0,
        },
        "rows": rows,
        "policy": {
            "current_source_web_receipt_required_after_semantic_clear": True,
            "missing_or_failed_current_source_reviewer_is_not_pass": True,
            "historical_closest_work_may_be_older_than_candidate_evidence_freshness": True,
            "current_source_review_is_block_only": True,
            "shadow_survival_is_not_live_problem_gate_pass": True,
            "canonical_generator_and_queue_untouched": True,
        },
        "scientific_authority": False,
        "authority": {"live_problem_gate": False, "paper_design": False, "method": False, "experiment": False, "p0": False, "gpu": False},
    }


def write_terminal(*, shadow_final_path: Path, receipt_paths: list[Path], output_path: Path) -> dict[str, Any]:
    shadow_final = json.loads(shadow_final_path.read_text(encoding="utf-8"))
    receipts = []
    for path in receipt_paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        candidate_id = str(payload.get("candidate_id") or "")
        receipts.append(normalize_receipt(payload, candidate_id=candidate_id))
    state = compile_terminal(shadow_final, receipts)
    output_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return state
