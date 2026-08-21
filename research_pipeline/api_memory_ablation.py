from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .api_memory_store import sha_json
from .api_research_memory import compile_api_memory_query_pack


SCHEMA_VERSION = "1.0"
VARIANTS = ("relevant", "random", "none")


def build_api_memory_ablation_plan(
    *,
    purpose: str,
    context: Any,
    run_id_prefix: str,
    stage: str,
    max_items: int = 16,
    max_chars: int = 6000,
    root: Path | None = None,
) -> dict[str, Any]:
    """Freeze matched A/B/C API-memory query packs without provider calls.

    The three arms differ only in memory selection policy. The downstream stage
    runner consumes the arm through RESEARCH_API_MEMORY_VARIANT. This object is
    zero-authority and is intended for search-efficiency evaluation only.
    """
    # Freeze the relevant arm first, then force the random arm to use the same
    # realized memory-item count. This removes the most important prompt-content
    # volume confound. The none arm is intentionally empty: relevant-vs-random
    # is the matched-overhead causal comparison, while relevant-vs-none measures
    # total memory utility and is reported separately rather than treated as a
    # token-matched comparison.
    relevant = compile_api_memory_query_pack(
        purpose=purpose,
        context=context,
        run_id=f"{run_id_prefix}-relevant",
        stage=stage,
        variant="relevant",
        max_items=max_items,
        max_chars=max_chars,
        required=True,
        record_query=False,
        root=root,
    )
    matched_items = int((relevant.get("summary") or {}).get("selected") or 0)
    random = compile_api_memory_query_pack(
        purpose=purpose,
        context=context,
        run_id=f"{run_id_prefix}-random",
        stage=stage,
        variant="random",
        max_items=matched_items,
        max_chars=max_chars,
        required=True,
        record_query=False,
        root=root,
    )
    none = compile_api_memory_query_pack(
        purpose=purpose,
        context=context,
        run_id=f"{run_id_prefix}-none",
        stage=stage,
        variant="none",
        max_items=0,
        max_chars=0,
        required=True,
        record_query=False,
        root=root,
    )
    packs: dict[str, dict[str, Any]] = {"relevant": relevant, "random": random, "none": none}
    available = {int((pack.get("summary") or {}).get("available") or 0) for pack in packs.values()}
    memory_instances = {str(pack.get("memory_instance_id") or "") for pack in packs.values()}
    plan = {
        "schema_version": SCHEMA_VERSION,
        "status": "API_MEMORY_ABLATION_READY",
        "purpose": str(purpose).upper(),
        "stage": stage,
        "context_sha256": sha_json(context if context is not None else {}),
        "budget": {"max_items": int(max_items), "max_chars": int(max_chars), "matched_nonzero_items": matched_items},
        "comparison_semantics": {
            "relevant_vs_random": "PRIMARY_CAUSAL_MEMORY_RELEVANCE_COMPARISON_WITH_MATCHED_REALIZED_ITEM_COUNT_AND_SHARED_CHARACTER_CAP",
            "relevant_vs_none": "TOTAL_MEMORY_UTILITY_COMPARISON_NOT_TOKEN_MATCHED",
            "random_vs_none": "MEMORY_OVERHEAD_AND_RANDOM_CONTEXT_DIAGNOSTIC_NOT_PRIMARY_EFFECT",
            "provider_prompt_tokens_must_be_reported_per_arm": True,
        },
        "arms": {
            variant: {
                "run_id": f"{run_id_prefix}-{variant}",
                "env": {"RESEARCH_API_MEMORY_VARIANT": variant},
                "query_id": pack.get("query_id"),
                "query_pack_sha256": pack.get("query_pack_sha256"),
                "memory_instance_id": pack.get("memory_instance_id"),
                "selected_memory_ids": pack.get("selected_memory_ids") or [],
                "selected_scientific_signatures": pack.get("selected_scientific_signatures") or [],
                "summary": pack.get("summary") or {},
                "scientific_authority": False,
            }
            for variant, pack in packs.items()
        },
        "metrics": [
            "semantic_unique_rate",
            "duplicate_rate",
            "same_information_reduction_rate",
            "preflight_ready_candidates",
            "problem_gate_compatible_candidates",
            "review_disagreement",
            "provider_calls_per_survivor",
            "prompt_characters_per_survivor",
            "idea_diversity",
        ],
        "invariants": {
            "same_memory_instance": len(memory_instances) == 1,
            "same_available_memory_pool": len(available) == 1,
            "same_nonzero_arm_realized_item_count": int((packs["relevant"].get("summary") or {}).get("selected") or 0) == int((packs["random"].get("summary") or {}).get("selected") or 0),
            "same_nonzero_arm_character_cap": True,
            "none_arm_has_zero_selected_memory": int((packs["none"].get("summary") or {}).get("selected") or 0) == 0,
            "none_arm_not_misreported_as_token_matched": True,
            "all_arms_zero_scientific_authority": all(pack.get("scientific_authority") is False for pack in packs.values()),
            "ablation_may_change_search_allocation_not_scientific_thresholds": True,
        },
        "scientific_authority": False,
        "authority": {
            "problem_gate": False,
            "paper_design": False,
            "method": False,
            "experiment": False,
            "p0": False,
            "gpu": False,
        },
    }
    plan["plan_sha256"] = sha_json({key: value for key, value in plan.items() if key != "plan_sha256"})
    if not all(plan["invariants"].values()):
        plan["status"] = "API_MEMORY_ABLATION_BLOCKED"
    return plan


def build_basin_aware_api_memory_ablation_plan(
    *,
    context: Any,
    run_id_prefix: str,
    stage: str,
    max_items: int = 4,
    max_chars: int = 8000,
    max_item_chars: int = 600,
    root: Path | None = None,
) -> dict[str, Any]:
    """Freeze portfolio/relevant/random arms for Research Memory 2.3.

    Portfolio is the treatment. Relevant reproduces the previous Top-K policy;
    random is a matched-context control. No arm can grant scientific authority.
    """
    portfolio = compile_api_memory_query_pack(
        purpose="IDEA_DISCOVERY",
        context=context,
        run_id=f"{run_id_prefix}-portfolio",
        stage=stage,
        variant="portfolio",
        max_items=max_items,
        max_chars=max_chars,
        max_item_chars=max_item_chars,
        required=True,
        record_query=False,
        root=root,
    )
    realized = int((portfolio.get("summary") or {}).get("selected") or 0)
    relevant = compile_api_memory_query_pack(
        purpose="IDEA_DISCOVERY",
        context=context,
        run_id=f"{run_id_prefix}-relevant",
        stage=stage,
        variant="relevant",
        max_items=realized,
        max_chars=max_chars,
        max_item_chars=max_item_chars,
        required=True,
        record_query=False,
        root=root,
    )
    random = compile_api_memory_query_pack(
        purpose="IDEA_DISCOVERY",
        context=context,
        run_id=f"{run_id_prefix}-random",
        stage=stage,
        variant="random",
        max_items=realized,
        max_chars=max_chars,
        max_item_chars=max_item_chars,
        required=True,
        record_query=False,
        root=root,
    )
    packs = {"portfolio": portfolio, "relevant": relevant, "random": random}
    roles = [str(row.get("role") or "") for row in portfolio.get("selected_memory_roles") or []]
    instances = {str(pack.get("memory_instance_id") or "") for pack in packs.values()}
    available = {int((pack.get("summary") or {}).get("available") or 0) for pack in packs.values()}
    counts = {int((pack.get("summary") or {}).get("selected") or 0) for pack in packs.values()}
    characters = {int((pack.get("summary") or {}).get("characters") or 0) for pack in packs.values()}
    plan = {
        "schema_version": "2.3",
        "status": "BASIN_AWARE_API_MEMORY_ABLATION_READY",
        "purpose": "IDEA_DISCOVERY",
        "stage": stage,
        "context_sha256": sha_json(context if context is not None else {}),
        "budget": {"max_items": int(max_items), "max_chars": int(max_chars), "max_item_chars": int(max_item_chars), "matched_realized_items": realized},
        "arms": {
            variant: {
                "run_id": f"{run_id_prefix}-{variant}",
                "env": {"RESEARCH_API_MEMORY_VARIANT": variant},
                "query_pack_sha256": pack.get("query_pack_sha256"),
                "memory_instance_id": pack.get("memory_instance_id"),
                "selected_memory_ids": pack.get("selected_memory_ids") or [],
                "selected_scientific_signatures": pack.get("selected_scientific_signatures") or [],
                "selected_memory_roles": pack.get("selected_memory_roles") or [],
                "summary": pack.get("summary") or {},
                "scientific_authority": False,
            }
            for variant, pack in packs.items()
        },
        "comparison_semantics": {
            "portfolio_vs_relevant": "PRIMARY_TEST_OF_BASIN_AWARE_COMPOSITION_VS_TOP_K_RELEVANCE_WITH_MATCHED_ITEM_COUNT_AND_SHARED_CHAR_CAP",
            "portfolio_vs_random": "MATCHED_CONTEXT_UTILITY_CONTROL",
            "reviewer_subjective_criteria_require_separate_adjudication": True,
        },
        "invariants": {
            "same_memory_instance": len(instances) == 1,
            "same_available_memory_pool": len(available) == 1,
            "same_realized_item_count": len(counts) == 1 and realized > 0,
            "same_realized_memory_characters": len(characters) == 1,
            "portfolio_has_all_four_primary_roles": all(role in roles for role in (
                "NEAREST_CLOSED_BASIN",
                "NEAREST_SURVIVING_CONTRACT",
                "DISTANT_REUSABLE_CONTRACT",
                "UNRESOLVED_BOUNDARY",
            )),
            "all_arms_zero_scientific_authority": all(pack.get("scientific_authority") is False for pack in packs.values()),
            "scientific_thresholds_unchanged": True,
        },
        "scientific_authority": False,
        "authority": {"problem_gate":False,"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False},
    }
    plan["plan_sha256"] = sha_json({key: value for key, value in plan.items() if key != "plan_sha256"})
    if not all(plan["invariants"].values()):
        plan["status"] = "BASIN_AWARE_API_MEMORY_ABLATION_BLOCKED"
    return plan


def build_relevant_escape_ablation_plan(
    *,
    context: Any,
    run_id_prefix: str,
    stage: str,
    max_items: int = 4,
    max_item_chars: int = 600,
    root: Path | None = None,
) -> dict[str, Any]:
    """Freeze identical Top-K objects with plain vs basin-escape framing."""
    max_chars = max_items * max_item_chars + max(0, max_items - 1) * 2
    packs = {
        variant: compile_api_memory_query_pack(
            purpose="IDEA_DISCOVERY", context=context,
            run_id=f"{run_id_prefix}-{variant}", stage=stage, variant=variant,
            max_items=max_items, max_chars=max_chars, max_item_chars=max_item_chars,
            required=True, record_query=False, root=root,
        )
        for variant in ("relevant_neutral", "relevant_escape")
    }
    plain, escape = packs["relevant_neutral"], packs["relevant_escape"]
    plan = {
        "schema_version": "2.4",
        "status": "RELEVANT_ESCAPE_ABLATION_READY",
        "purpose": "IDEA_DISCOVERY",
        "stage": stage,
        "context_sha256": sha_json(context if context is not None else {}),
        "budget": {"max_items": max_items, "max_item_chars": max_item_chars, "max_chars": max_chars},
        "arms": {
            variant: {
                "run_id": f"{run_id_prefix}-{variant}",
                "variant": variant,
                "query_pack_sha256": pack.get("query_pack_sha256"),
                "memory_instance_id": pack.get("memory_instance_id"),
                "selected_memory_ids": pack.get("selected_memory_ids") or [],
                "selected_scientific_signatures": pack.get("selected_scientific_signatures") or [],
                "selected_memory_roles": pack.get("selected_memory_roles") or [],
                "summary": pack.get("summary") or {},
                "scientific_authority": False,
            }
            for variant, pack in packs.items()
        },
        "invariants": {
            "same_memory_instance": plain.get("memory_instance_id") == escape.get("memory_instance_id"),
            "same_selected_object_ids": plain.get("selected_object_keys") == escape.get("selected_object_keys"),
            "same_scientific_signatures": plain.get("selected_scientific_signatures") == escape.get("selected_scientific_signatures"),
            "same_memory_characters": int((plain.get("summary") or {}).get("characters") or 0) == int((escape.get("summary") or {}).get("characters") or 0),
            "same_item_count": int((plain.get("summary") or {}).get("selected") or 0) == max_items == int((escape.get("summary") or {}).get("selected") or 0),
            "same_framing_prefix_lengths": [r.get("framing_prefix_chars") for r in plain.get("selected_memory_roles") or []] == [r.get("framing_prefix_chars") for r in escape.get("selected_memory_roles") or []],
            "same_visible_source_chars": [r.get("visible_source_chars") for r in plain.get("selected_memory_roles") or []] == [r.get("visible_source_chars") for r in escape.get("selected_memory_roles") or []],
            "same_visible_source_sha256": [r.get("visible_source_sha256") for r in plain.get("selected_memory_roles") or []] == [r.get("visible_source_sha256") for r in escape.get("selected_memory_roles") or []],
            "escape_has_role_annotations": len(escape.get("selected_memory_roles") or []) == max_items,
            "all_arms_zero_scientific_authority": all(pack.get("scientific_authority") is False for pack in packs.values()),
            "scientific_thresholds_unchanged": True,
        },
        "comparison_semantics": {
            "relevant_escape_vs_relevant_neutral": "SAME_TOP_K_OBJECTS_PREFIX_LENGTH_VISIBLE_SOURCE_AND_TOTAL_CHARACTERS_ONLY_ROLE_SEMANTICS_DIFFER",
            "closed_basin_annotation_is_search_control_not_scientific_truth": True,
        },
        "scientific_authority": False,
        "authority": {"problem_gate":False,"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False},
    }
    plan["plan_sha256"] = sha_json({k:v for k,v in plan.items() if k != "plan_sha256"})
    if not all(plan["invariants"].values()):
        plan["status"] = "RELEVANT_ESCAPE_ABLATION_BLOCKED"
    return plan


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze an API research-memory A/B/C ablation plan")
    parser.add_argument("--purpose", default="IDEA_DISCOVERY")
    parser.add_argument("--stage", default="expand")
    parser.add_argument("--run-id-prefix", required=True)
    parser.add_argument("--context-json", default="{}")
    parser.add_argument("--persistent-root", type=Path)
    parser.add_argument("--max-items", type=int, default=16)
    parser.add_argument("--max-chars", type=int, default=6000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    context = json.loads(args.context_json)
    plan = build_api_memory_ablation_plan(
        purpose=args.purpose,
        context=context,
        run_id_prefix=args.run_id_prefix,
        stage=args.stage,
        max_items=args.max_items,
        max_chars=args.max_chars,
        root=args.persistent_root,
    )
    text = json.dumps(plan, ensure_ascii=False, indent=2) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
