from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .api_memory_portfolio_smoke_staged import ARMS, GENERATOR_MODEL
from .api_memory_portfolio_smoke_reviewers import (
    AGENT_REVIEWER_MODEL,
    HARD_REVIEWER_MODEL,
    REDUCTION_REVIEWER_MODEL,
)
from .api_memory_search_smoke import _canonical, _diversity, _max_cross_similarity, _sha_text
from .api_memory_search_smoke_staged import _load, _lock, _write
from .api_research_memory import record_api_memory_consumption, record_parsed_api_output


def _successful_review(study: Path, name: str, expected_status: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    paths = [study / f"review-{name}-result.json"] + sorted(study.glob(f"review-{name}-result-r*.json"))
    attempts: list[dict[str, Any]] = []
    successes: list[dict[str, Any]] = []
    for path in paths:
        if not path.is_file():
            continue
        payload = _load(path)
        attempts.append({"path": path.name, "status": payload.get("status"), "run_id": payload.get("run_id", "")})
        if payload.get("status") == expected_status:
            successes.append(payload)
    if len(successes) != 1:
        raise RuntimeError(f"expected exactly one successful {name} review, found {len(successes)}: {attempts}")
    return successes[0], attempts


def finalize(*, root: Path, study: Path) -> dict[str, Any]:
    output = study / "report.json"
    lock = _lock(output, {"stage": "finalize"})
    try:
        prep = _load(study / "state-prepared.json")
        rprep = _load(study / "review-prepared.json")
        hard, hard_attempts = _successful_review(study, "hard", "HARD_REVIEW_COMPLETE")
        agent, agent_attempts = _successful_review(study, "agent", "AGENT_REVIEW_COMPLETE")
        reduction, reduction_attempts = _successful_review(study, "reduction", "REDUCTION_REVIEW_COMPLETE")

        hard_by = {str(row["blind_id"]): row for row in hard["reviews"]}
        agent_by = {str(row["blind_id"]): row for row in agent["reviews"]}
        reduction_by = {str(row["blind_id"]): row for row in reduction["reviews"]}
        mapping = {row["blind_id"]: (row["arm"], row["idea_id"]) for row in rprep["mapping"]}
        per: dict[str, list[dict[str, Any]]] = {arm: [] for arm in ARMS}
        for blind_id, (arm, idea_id) in mapping.items():
            per[arm].append({
                "blind_id": blind_id,
                "idea_id": idea_id,
                "hard": hard_by[blind_id],
                "agent": agent_by[blind_id],
                "reduction": reduction_by[blind_id],
            })

        gens = {arm: _load(study / f"generation-{arm}.json") for arm in ARMS}
        for arm in ARMS:
            gen = gens[arm]
            pack = prep["packs"][arm]
            structured = {
                "schema_version": "2.3",
                "study": "API_MEMORY_PORTFOLIO_SMOKE",
                "arm": arm,
                "query_pack_sha256": pack["query_pack_sha256"],
                "selected_memory_ids": pack["selected_memory_ids"],
                "selected_memory_roles": pack.get("selected_memory_roles") or [],
                "usage": gen["usage"],
                "ideas": gen["ideas"],
                "criterion_reviews": sorted(per[arm], key=lambda row: row["idea_id"]),
                "scientific_authority": False,
                "belief_authority": False,
            }
            record_parsed_api_output(
                run_root=root / "runs" / gen["run_id"],
                stage="memory-portfolio-smoke",
                raw_sha256=gen["raw_sha256"],
                structured_payload=structured,
                requested_model=GENERATOR_MODEL,
                resolved_model=gen["resolved_model"],
                research_objects=[],
                root=root,
            )
            record_api_memory_consumption(
                run_id=gen["run_id"],
                stage="memory-portfolio-smoke",
                pack=pack,
                raw_sha256=gen["raw_sha256"],
                output_object_ids=[f"{arm}:{row['id']}" for row in gen["ideas"]],
                outcome_status="PORTFOLIO_SMOKE_GENERATED_ZERO_AUTHORITY",
                root=root,
            )

        metrics: dict[str, dict[str, Any]] = {}
        for arm in ARMS:
            rows = per[arm]
            ideas = gens[arm]["ideas"]
            panel_clear = sum(
                (not bool(row["hard"]["history_near_duplicate"]))
                and bool(row["hard"]["cheapest_falsifier_complete"])
                and row["agent"]["agent_specificity"] == "AGENT_SPECIFIC"
                and row["reduction"]["reduction_verdict"] == "RESIDUAL_PLAUSIBLE"
                for row in rows
            )
            others = [idea for other in ARMS if other != arm for idea in gens[other]["ideas"]]
            metrics[arm] = {
                "n": len(rows),
                "history_pack_duplicate_rate": sum(bool(row["hard"]["history_near_duplicate"]) for row in rows) / len(rows),
                "falsifier_complete_rate": sum(bool(row["hard"]["cheapest_falsifier_complete"]) for row in rows) / len(rows),
                "agent_specific_rate": sum(row["agent"]["agent_specificity"] == "AGENT_SPECIFIC" for row in rows) / len(rows),
                "agent_uncertain_rate": sum(row["agent"]["agent_specificity"] == "UNCERTAIN" for row in rows) / len(rows),
                "exact_reduction_rate": sum(row["reduction"]["reduction_verdict"] == "EXACT_REDUCTION" for row in rows) / len(rows),
                "residual_plausible_rate": sum(row["reduction"]["reduction_verdict"] == "RESIDUAL_PLAUSIBLE" for row in rows) / len(rows),
                "reduction_uncertain_rate": sum(row["reduction"]["reduction_verdict"] == "UNCERTAIN" for row in rows) / len(rows),
                "criterion_panel_clear_count": panel_clear,
                "criterion_panel_clear_rate": panel_clear / len(rows),
                "within_arm_lexical_diversity": _diversity(ideas),
                "mean_max_cross_arm_lexical_similarity": _max_cross_similarity(ideas, others),
                "generation_input_tokens": gens[arm]["usage"]["input_tokens"],
                "generation_output_tokens": gens[arm]["usage"]["output_tokens"],
                "selected_memory_items": int((prep["packs"][arm].get("summary") or {}).get("selected") or 0),
                "selected_memory_characters": int((prep["packs"][arm].get("summary") or {}).get("characters") or 0),
            }

        primary = {
            "portfolio_vs_relevant_panel_clear_delta": metrics["portfolio"]["criterion_panel_clear_rate"] - metrics["relevant"]["criterion_panel_clear_rate"],
            "portfolio_vs_random_panel_clear_delta": metrics["portfolio"]["criterion_panel_clear_rate"] - metrics["random"]["criterion_panel_clear_rate"],
            "portfolio_vs_relevant_exact_reduction_delta": metrics["portfolio"]["exact_reduction_rate"] - metrics["relevant"]["exact_reduction_rate"],
            "all_arms_matched_memory_items": len({metrics[arm]["selected_memory_items"] for arm in ARMS}) == 1,
            "all_arms_matched_memory_characters": len({metrics[arm]["selected_memory_characters"] for arm in ARMS}) == 1,
            "interpretation": "search-policy smoke only; criterion-separated panel clear is not Problem Gate, scientific truth, or publication-success evidence",
        }
        report = {
            "schema_version": "2.3",
            "status": "API_MEMORY_PORTFOLIO_SMOKE_COMPLETE",
            "study": "API_MEMORY_PORTFOLIO_SMOKE_V23",
            "memory_instance_id": prep["packs"]["portfolio"]["memory_instance_id"],
            "frozen_ablation_plan_sha256": prep["plan"]["plan_sha256"],
            "history_pool_available_objects": int((prep["packs"]["portfolio"].get("summary") or {}).get("available") or 0),
            "generator_model": GENERATOR_MODEL,
            "reviewers": {
                "hard": {"requested": HARD_REVIEWER_MODEL, "resolved": hard["resolved_model"], "usage": hard["usage"], "attempts": hard_attempts},
                "agent": {"requested": AGENT_REVIEWER_MODEL, "resolved": agent["resolved_model"], "usage": agent["usage"], "attempts": agent_attempts},
                "reduction": {"requested": REDUCTION_REVIEWER_MODEL, "resolved": reduction["resolved_model"], "usage": reduction["usage"], "attempts": reduction_attempts},
            },
            "metrics": metrics,
            "primary_comparison": primary,
            "generated_outputs_promoted_to_research_objects": False,
            "scientific_authority": False,
            "belief_authority": False,
        }
        report["report_sha256"] = _sha_text(_canonical(report))
        _write(output, report)
        return report
    finally:
        if output.exists():
            lock.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--persistent-root", type=Path, required=True)
    parser.add_argument("--study", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(finalize(root=args.persistent_root, study=args.study), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
