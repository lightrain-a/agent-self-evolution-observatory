from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-fresh-phenomenon-portfolio-20260817.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "paper-first-fresh-phenomenon-portfolio-20260817.js"
EVIDENCE_ECHO_JSON = PROJECT_ROOT / "generated" / "paper-first-evidence-echo-retrospective-20260817.json"
EVIDENCE_ECHO_F0 = PROJECT_ROOT / "research_pipeline" / "paper_first_evidence_echo_f0.py"
EXPECTED_EVIDENCE_ECHO_F0_SHA256 = "8f3b04d09c4101335434fa7a8a50bba965ab95ce244cf24c5fe9e53ba6feadf6"
PRIMARY_STATE_JSON = PROJECT_ROOT / "generated" / "paper-first-primary-evidence-state.json"
DEAD_END_MEMORY_JSON = PROJECT_ROOT / "generated" / "paper-first-search-portfolio-design-adjudication.json"

SCHEMA_VERSION = "1.0"
ACTIVE_F0_LIMIT = 1
ALLOWED_STATUSES = {
    "ACTIVE_F0",
    "SCOUT_ASSET",
    "HOLD_SUPPORT",
    "HOLD_REDUCTION",
    "READY_FOR_PROBLEM_REVIEW",
    "STOP_REDUCTION",
    "ARCHIVED",
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else ""


def _candidate(
    *,
    candidate_id: str,
    title: str,
    source_refs: list[str],
    phenomenon: str,
    strongest_reduction: str,
    cheapest_falsifier: str,
    support_status: str,
    status: str,
    priority: int,
    why_now: str,
    substrate: dict[str, Any] | None = None,
    evidence: dict[str, Any] | None = None,
    reopen_only_if: str = "",
) -> dict[str, Any]:
    return {
        "candidate_id": candidate_id,
        "title": title,
        "source_refs": source_refs,
        "phenomenon": phenomenon,
        "strongest_reduction": strongest_reduction,
        "cheapest_falsifier": cheapest_falsifier,
        "support_status": support_status,
        "status": status,
        "priority": priority,
        "why_now": why_now,
        "substrate": substrate or {},
        "evidence": evidence or {},
        "reopen_only_if": reopen_only_if,
        "paper_problem_claimed": False,
        "scientific_authority": False,
        "authority": {
            "problem_gate": False,
            "paper_design": False,
            "method": False,
            "experiment": False,
            "p0": False,
            "gpu": False,
            "full_experiment": False,
        },
    }


def _memory_hold(memory: dict[str, Any], source_candidate_id: str) -> dict[str, Any]:
    dead = memory.get("shadow_dead_end_memory") or {}
    rows = [row for row in dead.get("hold_objects") or [] if isinstance(row, dict)]
    return next((row for row in rows if str(row.get("source_candidate_id") or "") == source_candidate_id), {})


def build_fresh_phenomenon_portfolio(
    *,
    evidence_echo: dict[str, Any] | None = None,
    primary_state: dict[str, Any] | None = None,
    dead_end_memory: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compile multiple paper scouts without letting unsupported ideas consume experiment slots.

    This portfolio is search/execution control only. It intentionally sits outside the
    canonical Problem Queue. A candidate can occupy the single ACTIVE_F0 slot only when
    a provenance-audited substrate and a frozen same-information falsifier already exist.
    A positive F0 does not grant Problem-Gate or Paper-Design authority; it merely moves
    the candidate to READY_FOR_PROBLEM_REVIEW on the next explicit adjudication pass.
    """

    evidence_echo = evidence_echo or _load(EVIDENCE_ECHO_JSON)
    primary_state = primary_state or _load(PRIMARY_STATE_JSON)
    dead_end_memory = dead_end_memory or _load(DEAD_END_MEMORY_JSON)
    ps = primary_state.get("summary") or {}

    echo_signal = evidence_echo.get("observed_signal") or {}
    echo_f0 = evidence_echo.get("next_f0") or {}
    echo_ready = bool(
        evidence_echo.get("decision") == "KEEP_AS_ACTIVE_F0_NOT_PAPER_IDEA"
        and int((evidence_echo.get("scope") or {}).get("units") or 0) >= 128
        and int(echo_signal.get("naive_summary_induced_false_answers") or 0) >= 7
        and int(echo_signal.get("naive_summary_fixed_false_answers") or 0) == 0
        and float(echo_signal.get("naive_summary_exact_paired_p") or 1.0) <= 0.05
        and len(echo_f0.get("required_arms") or []) >= 5
        and echo_f0.get("gpu_authorized") is False
        and _sha(EVIDENCE_ECHO_F0) == EXPECTED_EVIDENCE_ECHO_F0_SHA256
    )

    harness_hold = _memory_hold(dead_end_memory, "SHADOW-P07-C01")
    defense_hold = _memory_hold(dead_end_memory, "SHADOW-P11-C02")
    spatial_hold = next(
        (
            row
            for row in ((dead_end_memory.get("shadow_dead_end_memory") or {}).get("hold_objects") or [])
            if isinstance(row, dict)
            and str(row.get("title") or "").startswith("Procedural-composition transfer-calibration boundary")
        ),
        {},
    )

    candidates = [
        _candidate(
            candidate_id="PA-01-EVIDENCE-ECHO",
            title=str(evidence_echo.get("title") or "Evidence Echo in Agent Notes"),
            source_refs=[str(evidence_echo.get("source_primary_ref") or "arXiv:2608.07527")],
            phenomenon=(
                "On 64 benchmark-unanswerable units with raw visible pages locked across policies, "
                "adding an extractive persistent note raised false-answer rate from 10.9% to 21.9%; "
                "the paired naive-summary transition was 7 induced versus 0 repaired false answers "
                "(exact p=0.015625), with zero net exact-accuracy gain on the 64 answerable units."
            ),
            strongest_reduction=(
                "generic prompt salience/repetition, correlated-evidence double counting, extra decision "
                "opportunity, context-length effects, or ordinary calibration shift under redundant context"
            ),
            cheapest_falsifier=(
                "Keep raw pages, retrieval ranking, model, temperature, and two-step budget fixed; compare "
                "RAW_ONLY vs ECHO_EXTRACTIVE vs VERBATIM_DUPLICATE vs TOKEN_MATCHED_NEUTRAL vs DEDUP_WARNING "
                "on the frozen unanswerable/answerable units."
            ),
            support_status="PROVENANCE_AUDITED_LOCAL_SUBSTRATE" if echo_ready else "INCOMPLETE_RECEIPT",
            status="ACTIVE_F0" if echo_ready else "HOLD_SUPPORT",
            priority=100,
            why_now=(
                "This is the only current scout with a real matched substrate, a nonzero paired residual, "
                "and a falsifier that changes one representation axis without requiring a new benchmark."
            ),
            substrate={
                "host": ((evidence_echo.get("source_substrate") or {}).get("host")),
                "run": ((evidence_echo.get("source_substrate") or {}).get("run")),
                "aggregate_jsonl_sha256": ((evidence_echo.get("source_substrate") or {}).get("aggregate_jsonl_sha256")),
                "raw_visible_pages_locked_across_policies": ((evidence_echo.get("source_substrate") or {}).get("raw_visible_pages_locked_across_policies")),
                "second_retrieval_ranking_locked_across_active_policies": ((evidence_echo.get("source_substrate") or {}).get("second_retrieval_ranking_locked_across_active_policies")),
            },
            evidence={
                "baseline_false_answer_rate": echo_signal.get("negative_evidence_baseline_unanswerable_false_answer_rate"),
                "naive_summary_false_answer_rate": echo_signal.get("naive_summary_unanswerable_false_answer_rate"),
                "induced_false": echo_signal.get("naive_summary_induced_false_answers"),
                "repaired_false": echo_signal.get("naive_summary_fixed_false_answers"),
                "paired_p": echo_signal.get("naive_summary_exact_paired_p"),
                "answerable_exact_net_delta": echo_signal.get("naive_summary_answerable_exact_net_delta"),
            },
            reopen_only_if=(
                "If the F0 is reduced by token-matched neutral padding or the paired effect disappears, archive. "
                "If redundant evidence remains uniquely harmful and DEDUP_WARNING selectively recovers safety, "
                "then run current-source collision review before any Problem-Gate submission."
            ),
        ),
        _candidate(
            candidate_id="PA-02-DEFENSE-RESTRICTIVENESS",
            title="Failure-Driven Defense Can Improve Security While Collapsing Utility",
            source_refs=["arXiv:2608.12977"],
            phenomenon=(
                "Under the same five-round defense-evolution budget, the reported backbone ablation lowers attack "
                "success while one backbone yields only 7.2% utility accuracy, showing a sharp security/utility mismatch."
            ),
            strongest_reduction="ordinary constrained optimization / security-utility Pareto trade-off and conservative policy bias",
            cheapest_falsifier=(
                "Requires paired evolution histories with matched current ASR/utility and candidate patch benefit but "
                "different accumulated restrictiveness; no such current released unit is available."
            ),
            support_status=str(defense_hold.get("support_status") or "SUPPORT_UNAVAILABLE"),
            status="HOLD_SUPPORT",
            priority=70,
            why_now="Strong quantitative failure boundary, but it must not consume compute before the required history-level asset exists.",
            reopen_only_if=str(defense_hold.get("reopen_only_if") or "Author release exposes replayable evolution histories with rule/patch lineage."),
        ),
        _candidate(
            candidate_id="PA-03-HARNESS-SELECTION-INVERSION",
            title="Train-Selected Harnesses Need Not Be the Harnesses That Generalize Best",
            source_refs=["arXiv:2607.13683"],
            phenomenon=(
                "HarnessBank reports a GDPval train/test ranking disagreement and 62-76% phantom-progress rounds "
                "under weaker crediting rules after convergence, suggesting a selection-stability boundary."
            ),
            strongest_reduction="small-n ranking noise, winner's curse, adaptive validation, and ordinary selection bias",
            cheapest_falsifier=(
                "Sweep the frozen verification rule on released paired gene histories while matching candidate count, "
                "selection pressure, and deployment n; the required histories are not released."
            ),
            support_status=str(harness_hold.get("support_status") or "SUPPORT_UNAVAILABLE"),
            status="HOLD_SUPPORT",
            priority=60,
            why_now="Potentially strong self-evolution-specific selection phenomenon, but support is still source-only.",
            reopen_only_if=str(harness_hold.get("reopen_only_if") or "HarnessBank releases paired run histories/outcomes."),
        ),
        _candidate(
            candidate_id="PA-04-SPATIAL-MEMORY-CONFLICT",
            title="High-Relevance Procedure Memory Can Still Fail When Visual Grounding or Procedure Compatibility Breaks",
            source_refs=["arXiv:2608.12743"],
            phenomenon=(
                "Spatial Memory Agent reports baseline and memory-agent failures even with high-quality relevant memories "
                "(TRS >= 0.6), separating memory relevance from executability/grounding."
            ),
            strongest_reduction="base-model visual grounding failure or ordinary retrieval/execution mismatch",
            cheapest_falsifier=(
                "Needs query-level retrieved lesson identities/text, TRS/relevance metadata, and outcomes to construct "
                "matched conflicting versus non-conflicting procedure sets."
            ),
            support_status=str(spatial_hold.get("support_status") or "SUPPORT_UNAVAILABLE"),
            status="HOLD_SUPPORT",
            priority=50,
            why_now="Good reserve phenomenon but no independent query-level support asset is currently available.",
            reopen_only_if=str(spatial_hold.get("reopen_only_if") or "Authors release query-level retrieval logs and outcomes."),
        ),
    ]

    active = [row for row in candidates if row["status"] == "ACTIVE_F0"]
    if len(active) > ACTIVE_F0_LIMIT:
        active.sort(key=lambda row: (-int(row.get("priority") or 0), row["candidate_id"]))
        keep = {row["candidate_id"] for row in active[:ACTIVE_F0_LIMIT]}
        for row in candidates:
            if row["status"] == "ACTIVE_F0" and row["candidate_id"] not in keep:
                row["status"] = "SCOUT_ASSET"
                row["why_now"] += " Demoted because the single ACTIVE_F0 slot is already occupied by a higher-priority matched substrate."

    summary = {
        "candidates": len(candidates),
        "active_f0": sum(row["status"] == "ACTIVE_F0" for row in candidates),
        "scout_asset": sum(row["status"] == "SCOUT_ASSET" for row in candidates),
        "hold_support": sum(row["status"] == "HOLD_SUPPORT" for row in candidates),
        "hold_reduction": sum(row["status"] == "HOLD_REDUCTION" for row in candidates),
        "ready_for_problem_review": sum(row["status"] == "READY_FOR_PROBLEM_REVIEW" for row in candidates),
        "stop_reduction": sum(row["status"] == "STOP_REDUCTION" for row in candidates),
        "primary_verified": int(ps.get("verified") or 0),
        "primary_empirical_fact_candidates": int(ps.get("empirical_fact_candidates") or 0),
        "canonical_problem_gate_added": 0,
        "method_authorized": 0,
        "experiment_authorized": 0,
        "p0_authorized": 0,
        "gpu_authorized": 0,
    }

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": _now(),
        "status": "ACTIVE_F0_EXISTS" if summary["active_f0"] else "NO_ACTIVE_F0",
        "policy": {
            "portfolio_is_outside_canonical_problem_queue": True,
            "fresh_quantitative_phenomenon_precedes_method_ideation": True,
            "one_active_f0_slot_max": ACTIVE_F0_LIMIT,
            "active_f0_requires_provenance_audited_substrate": True,
            "active_f0_requires_frozen_same_information_falsifier": True,
            "source_only_candidates_cannot_consume_experiment_slot": True,
            "support_unavailable_is_hold_not_scientific_failure": True,
            "positive_f0_does_not_grant_problem_gate_or_paper_design": True,
            "f0_must_test_strongest_generic_reduction_before_novelty_claim": True,
            "failed_f0_is_archived_as_negative_search_control": True,
            "paper_problem_claim_requires_separate_current_source_collision_review": True,
            "scientific_authority": False,
        },
        "summary": summary,
        "candidates": sorted(candidates, key=lambda row: (-int(row["priority"]), row["candidate_id"])),
        "source_bindings": {
            "evidence_echo_receipt": {
                "path": str(EVIDENCE_ECHO_JSON.relative_to(PROJECT_ROOT)),
                "sha256": _sha(EVIDENCE_ECHO_JSON),
            },
            "evidence_echo_f0_harness": {
                "path": str(EVIDENCE_ECHO_F0.relative_to(PROJECT_ROOT)),
                "sha256": _sha(EVIDENCE_ECHO_F0),
            },
            "primary_state": {
                "path": str(PRIMARY_STATE_JSON.relative_to(PROJECT_ROOT)),
                "sha256": _sha(PRIMARY_STATE_JSON),
            },
            "dead_end_memory": {
                "path": str(DEAD_END_MEMORY_JSON.relative_to(PROJECT_ROOT)),
                "sha256": _sha(DEAD_END_MEMORY_JSON),
            },
        },
        "scientific_authority": False,
    }


def validate_fresh_phenomenon_portfolio(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    policy = state.get("policy") or {}
    summary = state.get("summary") or {}
    rows = [row for row in state.get("candidates") or [] if isinstance(row, dict)]
    if state.get("scientific_authority") is not False:
        errors.append("portfolio cannot carry scientific authority")
    if policy.get("portfolio_is_outside_canonical_problem_queue") is not True:
        errors.append("portfolio must stay outside canonical problem queue")
    if policy.get("active_f0_requires_provenance_audited_substrate") is not True:
        errors.append("active F0 must require audited substrate")
    if policy.get("source_only_candidates_cannot_consume_experiment_slot") is not True:
        errors.append("source-only candidate may not consume F0 slot")
    if policy.get("positive_f0_does_not_grant_problem_gate_or_paper_design") is not True:
        errors.append("positive F0 cannot grant downstream scientific authority")
    active = [row for row in rows if row.get("status") == "ACTIVE_F0"]
    if len(active) > ACTIVE_F0_LIMIT:
        errors.append("too many ACTIVE_F0 candidates")
    if int(summary.get("active_f0") or 0) != len(active):
        errors.append("ACTIVE_F0 summary mismatch")
    if int(summary.get("candidates") or 0) != len(rows):
        errors.append("candidate summary mismatch")
    for row in rows:
        if row.get("status") not in ALLOWED_STATUSES:
            errors.append(f"invalid status:{row.get('candidate_id')}")
        if row.get("scientific_authority") is not False or row.get("paper_problem_claimed") is not False:
            errors.append(f"candidate illegally carries scientific claim authority:{row.get('candidate_id')}")
        authority = row.get("authority") or {}
        if any(bool(authority.get(key)) for key in ("problem_gate", "paper_design", "method", "experiment", "p0", "gpu", "full_experiment")):
            errors.append(f"candidate illegally carries downstream authority:{row.get('candidate_id')}")
        if row.get("status") == "ACTIVE_F0":
            if row.get("support_status") != "PROVENANCE_AUDITED_LOCAL_SUBSTRATE":
                errors.append(f"ACTIVE_F0 lacks audited substrate:{row.get('candidate_id')}")
            if not str(row.get("cheapest_falsifier") or "").strip():
                errors.append(f"ACTIVE_F0 lacks falsifier:{row.get('candidate_id')}")
    if int(summary.get("canonical_problem_gate_added") or 0) != 0:
        errors.append("portfolio cannot add canonical Problem-Gate rows")
    if any(int(summary.get(key) or 0) != 0 for key in ("method_authorized", "experiment_authorized", "p0_authorized", "gpu_authorized")):
        errors.append("portfolio cannot authorize downstream execution")
    return errors


def write_fresh_phenomenon_portfolio(
    *,
    json_path: Path = DEFAULT_JSON,
    js_path: Path = DEFAULT_JS,
) -> dict[str, Any]:
    state = build_fresh_phenomenon_portfolio()
    errors = validate_fresh_phenomenon_portfolio(state)
    if errors:
        raise ValueError("; ".join(errors))
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.PAPER_FIRST_FRESH_PHENOMENON_PORTFOLIO = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    print(json.dumps(write_fresh_phenomenon_portfolio(), ensure_ascii=False, indent=2))
