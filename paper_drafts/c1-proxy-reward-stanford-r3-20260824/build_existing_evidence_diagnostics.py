from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

PAPER_ID = "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE"
TAXONOMY = {
    "navigation": [r"open ", r"navigat", r"section"],
    "pagination_coverage": [r"paginat", r"all pages", r"next-page", r"page revisits", r"unsearched content", r"page size"],
    "query_expansion": [r"keyword", r"search terms", r"synonym", r"paraphrase"],
    "semantic_matching": [r"semantic", r"target criterion", r"user.?s intent", r"true matches", r"relevant mentions", r"indicators"],
    "evidence_capture": [r"direct quote", r"quote", r"reviewer identity", r"supporting evidence", r"record"],
    "extraction": [r"extract", r"extraction", r"snippet"],
    "verification_completeness": [r"verify", r"incomplete", r"complete ", r"clean before", r"concluding absence", r"declaring task done"],
    "temporal_filtering": [r"date range", r"past month"],
    "status_filtering": [r"fulfilled", r"status keywords", r"non-fulfilled"],
}
COMPILED = {key: [re.compile(p, re.I) for p in patterns] for key, patterns in TAXONOMY.items()}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    return json.loads(path.read_text())


def slots(titles: list[str]) -> set[str]:
    found: set[str] = set()
    for title in titles:
        for key, patterns in COMPILED.items():
            if any(pattern.search(title) for pattern in patterns):
                found.add(key)
    return found or {"other"}


def jaccard_distance(a: set[str], b: set[str]) -> float:
    union = a | b
    return 1.0 - (len(a & b) / len(union) if union else 1.0)


def task_metadata(benchmark_rows: list[dict], task_id: str) -> dict:
    row = next(item for item in benchmark_rows if str(item.get("task_id")) == str(task_id))
    ref = row.get("eval", {}).get("reference_answers", {})
    if isinstance(ref.get("must_include"), list):
        answer_cardinality = len(ref["must_include"])
    elif "fuzzy_match" in ref:
        answer_cardinality = 0 if str(ref.get("fuzzy_match")).upper() == "N/A" else 1
    else:
        answer_cardinality = None
    start_url = row.get("start_url", "")
    return {
        "task_id": str(task_id),
        "intent": row.get("intent", ""),
        "start_context": "shopping_home" if start_url == "__SHOPPING__" else "product_page",
        "answer_cardinality": answer_cardinality,
        "eval_types": row.get("eval", {}).get("eval_types", []),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--webarena-test-raw", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    f0_path = args.artifact_root / "f0-write-channel.json"
    f0c_path = args.artifact_root / "f0c-prompt-control.json"
    f2_path = args.artifact_root / "f2r1-confirmatory.json"
    hetero_path = args.artifact_root / "f2r1-heterogeneity-bootstrap.json"
    f0, f0c, f2, hetero = map(load, [f0_path, f0c_path, f2_path, hetero_path])
    benchmark = load(args.webarena_test_raw)

    complete_pairs = [pair for pair in f0["pairs"] if pair.get("failure_titles")]
    f0_rows = []
    success_only_counts: dict[str, int] = {}
    failure_only_counts: dict[str, int] = {}
    for pair in complete_pairs:
        s = slots(pair["success_titles"])
        f = slots(pair["failure_titles"])
        s_only, f_only = sorted(s - f), sorted(f - s)
        for key in s_only:
            success_only_counts[key] = success_only_counts.get(key, 0) + 1
        for key in f_only:
            failure_only_counts[key] = failure_only_counts.get(key, 0) + 1
        f0_rows.append({
            "task_id": pair["task_id"],
            "success_slots": sorted(s),
            "failure_slots": sorted(f),
            "success_only_slots": s_only,
            "failure_only_slots": f_only,
            "slot_jaccard_distance": round(jaccard_distance(s, f), 6),
        })

    receipts = {}
    for row in f0["provider_receipts"]:
        if row.get("status") != "completed":
            continue
        task_id = row["engine_id"].replace("task-", "")
        label = "success" if "success" in row["stage"] else "failure"
        receipts[(task_id, label)] = row
    writer_length_rows = []
    for pair in complete_pairs:
        tid = pair["task_id"]
        success = receipts[(tid, "success")]["usage"]
        failure = receipts[(tid, "failure")]["usage"]
        s_reason = success.get("output_tokens_details", {}).get("reasoning_tokens", 0)
        f_reason = failure.get("output_tokens_details", {}).get("reasoning_tokens", 0)
        writer_length_rows.append({
            "task_id": tid,
            "success_output_tokens": success["output_tokens"],
            "failure_output_tokens": failure["output_tokens"],
            "failure_minus_success_output_tokens": failure["output_tokens"] - success["output_tokens"],
            "success_reasoning_tokens": s_reason,
            "failure_reasoning_tokens": f_reason,
            "failure_minus_success_reasoning_tokens": f_reason - s_reason,
        })

    control_rows = []
    for row in f0c["rows"]:
        title_sets = row["title_sets"]
        so = slots(title_sets["success_original"])
        sp = slots(title_sets["success_paraphrase"])
        fo = slots(title_sets["failure_original"])
        fp = slots(title_sets["failure_paraphrase"])
        between = jaccard_distance(so, fo)
        within_success = jaccard_distance(so, sp)
        within_failure = jaccard_distance(fo, fp)
        within_mean = (within_success + within_failure) / 2.0
        control_rows.append({
            "task_id": row["task_id"],
            "between_reward_modes_slot_distance": round(between, 6),
            "within_success_rewording_slot_distance": round(within_success, 6),
            "within_failure_rewording_slot_distance": round(within_failure, 6),
            "within_mode_mean_slot_distance": round(within_mean, 6),
            "between_minus_within_slot_distance": round(between - within_mean, 6),
        })

    cell_rows = f2["cell_results"]
    sources = sorted({row["source_memory_task"] for row in cell_rows}, key=int)
    futures = sorted({row["future_task"] for row in cell_rows}, key=int)
    y = {(row["source_memory_task"], row["future_task"]): row["signed_failure_minus_success"] for row in cell_rows}
    grand = sum(y.values()) / len(y)
    source_mean = {s: sum(y[(s, f)] for f in futures) / len(futures) for s in sources}
    future_mean = {f: sum(y[(s, f)] for s in sources) / len(sources) for f in futures}
    ss_total = sum((value - grand) ** 2 for value in y.values())
    ss_source = len(futures) * sum((source_mean[s] - grand) ** 2 for s in sources)
    ss_future = len(sources) * sum((future_mean[f] - grand) ** 2 for f in futures)
    ss_interaction = sum((y[(s, f)] - source_mean[s] - future_mean[f] + grand) ** 2 for s in sources for f in futures)

    total_sq_mass = sum(value ** 2 for value in y.values())
    future_rows = []
    for future in futures:
        rows = [row for row in cell_rows if row["future_task"] == future]
        sq_mass = sum(row["signed_failure_minus_success"] ** 2 for row in rows)
        future_rows.append({
            **task_metadata(benchmark, future),
            "mean_absolute_effect": round(sum(row["absolute_rate_difference"] for row in rows) / len(rows), 6),
            "squared_effect_mass": round(sq_mass, 6),
            "share_of_squared_effect_mass": round(sq_mass / total_sq_mass if total_sq_mass else 0.0, 6),
            "all_cells_joint_ceiling": all(row["success_memory_rate"] == 1.0 and row["failure_memory_rate"] == 1.0 for row in rows),
            "signed_effects_by_source": {row["source_memory_task"]: row["signed_failure_minus_success"] for row in rows},
        })

    source_rows = []
    for source in sources:
        rows = [row for row in cell_rows if row["source_memory_task"] == source]
        sq_mass = sum(row["signed_failure_minus_success"] ** 2 for row in rows)
        signs = {0 if row["signed_failure_minus_success"] == 0 else (1 if row["signed_failure_minus_success"] > 0 else -1) for row in rows}
        source_rows.append({
            "source_memory_task": source,
            "mean_signed_effect": round(source_mean[source], 6),
            "mean_absolute_effect": round(sum(row["absolute_rate_difference"] for row in rows) / len(rows), 6),
            "squared_effect_mass": round(sq_mass, 6),
            "share_of_squared_effect_mass": round(sq_mass / total_sq_mass if total_sq_mass else 0.0, 6),
            "contains_both_nonzero_signs": -1 in signs and 1 in signs,
            "signed_effects_by_future": {row["future_task"]: row["signed_failure_minus_success"] for row in rows},
        })

    payload = {
        "schema_version": "1.0",
        "analysis_id": "D2-PROXY-REWARD-STANFORD-R3-EXISTING-EVIDENCE-DIAGNOSTICS",
        "paper_id": PAPER_ID,
        "status": "EXISTING_EVIDENCE_DIAGNOSTICS_COMPLETE",
        "analysis_scope": "Post-ready diagnostic analysis over already frozen F0, F0C, and F2R1 artifacts plus released WebArena task metadata. No provider calls, no new rollouts, no new cells, no claim expansion.",
        "source_bindings": {
            "f0_write_channel_sha256": sha256(f0_path),
            "f0c_prompt_control_sha256": sha256(f0c_path),
            "f2r1_confirmatory_sha256": sha256(f2_path),
            "f2r1_heterogeneity_sha256": sha256(hetero_path),
            "webarena_test_raw_sha256": sha256(args.webarena_test_raw),
        },
        "writer_structure": {
            "complete_pairs": len(complete_pairs),
            "mean_token_jaccard_distance": f0["summary"]["mean_token_jaccard_distance"],
            "mean_strategy_slot_jaccard_distance": round(sum(row["slot_jaccard_distance"] for row in f0_rows) / len(f0_rows), 6),
            "strategy_slot_set_change_rate": sum(row["success_slots"] != row["failure_slots"] for row in f0_rows) / len(f0_rows),
            "success_only_slot_pair_counts": dict(sorted(success_only_counts.items())),
            "failure_only_slot_pair_counts": dict(sorted(failure_only_counts.items())),
            "failure_only_verification_completeness_pairs": failure_only_counts.get("verification_completeness", 0),
            "success_only_evidence_navigation_or_query_pairs": sum(any(key in row["success_only_slots"] for key in ("evidence_capture", "navigation", "query_expansion")) for row in f0_rows),
            "pair_rows": f0_rows,
            "writer_output_length": {
                "failure_longer_output_pairs": sum(row["failure_minus_success_output_tokens"] > 0 for row in writer_length_rows),
                "mean_failure_minus_success_output_tokens": round(sum(row["failure_minus_success_output_tokens"] for row in writer_length_rows) / len(writer_length_rows), 6),
                "failure_longer_reasoning_pairs": sum(row["failure_minus_success_reasoning_tokens"] > 0 for row in writer_length_rows),
                "mean_failure_minus_success_reasoning_tokens": round(sum(row["failure_minus_success_reasoning_tokens"] for row in writer_length_rows) / len(writer_length_rows), 6),
                "rows": writer_length_rows,
                "interpretation": "Descriptive response-structure asymmetry only; token length is not a semantic-quality metric.",
            },
        },
        "strategy_prompt_control": {
            "taxonomy_reused_without_change_from_stanford_r2": True,
            "tasks": len(control_rows),
            "mean_between_reward_modes_slot_distance": round(sum(row["between_reward_modes_slot_distance"] for row in control_rows) / len(control_rows), 6),
            "mean_within_mode_rewording_slot_distance": round(sum(row["within_mode_mean_slot_distance"] for row in control_rows) / len(control_rows), 6),
            "mean_between_minus_within_slot_distance": round(sum(row["between_minus_within_slot_distance"] for row in control_rows) / len(control_rows), 6),
            "positive_excess_tasks": sum(row["between_minus_within_slot_distance"] > 0 for row in control_rows),
            "tie_tasks": sum(row["between_minus_within_slot_distance"] == 0 for row in control_rows),
            "negative_excess_tasks": sum(row["between_minus_within_slot_distance"] < 0 for row in control_rows),
            "rows": control_rows,
            "interpretation": "The same fixed operation-slot taxonomy shows larger average structural separation across reward modes than under semantic-preserving same-mode rewordings. This is descriptive and not an embedding-semantic equivalence test.",
        },
        "terminal_heterogeneity": {
            "cells": len(cell_rows),
            "zero_effect_cells": hetero["heterogeneity"]["zero_effect_cells"],
            "positive_failure_minus_success_cells": hetero["heterogeneity"]["positive_failure_minus_success_cells"],
            "negative_failure_minus_success_cells": hetero["heterogeneity"]["negative_failure_minus_success_cells"],
            "mean_absolute_effect": f2["summary"]["observed_mean_absolute_success_rate_difference"],
            "mean_squared_effect": hetero["heterogeneity"]["observed_mean_squared_effect"],
            "top_two_share_of_squared_effect_mass": hetero["heterogeneity"]["top_two_share_of_squared_effect_mass"],
            "two_way_centered_effect_decomposition": {
                "grand_mean_signed_effect": round(grand, 6),
                "ss_total": round(ss_total, 6),
                "ss_source_main": round(ss_source, 6),
                "ss_future_main": round(ss_future, 6),
                "ss_source_future_interaction": round(ss_interaction, 6),
                "source_main_share": round(ss_source / ss_total, 6),
                "future_main_share": round(ss_future / ss_total, 6),
                "source_future_interaction_share": round(ss_interaction / ss_total, 6),
                "note": "Descriptive finite 4x4 decomposition of centered signed effects; no inferential ANOVA claim is made.",
            },
            "future_task_breakdown": future_rows,
            "source_memory_breakdown": source_rows,
            "interaction_examples": {
                "same_source_opposite_signs": [row["source_memory_task"] for row in source_rows if row["contains_both_nonzero_signs"]],
                "future_387_signed_effects": next(row["signed_effects_by_source"] for row in future_rows if row["task_id"] == "387"),
                "future_388_signed_effects": next(row["signed_effects_by_source"] for row in future_rows if row["task_id"] == "388"),
            },
            "interpretation": "Effect magnitude and sign are primarily source-by-future-cell specific in this frozen matrix. Source-only and future-only additive summaries leave most centered signed-effect variation in the interaction residual. Future task 164 is a joint 1.0/1.0 ceiling in all four cells; all observed squared-effect mass lies in the three non-ceiling future tasks. These are descriptive attributes, not a learned predictor of transfer.",
        },
        "claim_boundary": {
            "semantic_embedding_claim_supported": False,
            "large_effect_predictor_claim_supported": False,
            "no_memory_claim_supported": False,
            "cross_model_claim_supported": False,
            "live_loop_claim_supported": False,
            "provider_missingness_resolved": False,
        },
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "writer": payload["writer_structure"],
        "strategy_control": {k: v for k, v in payload["strategy_prompt_control"].items() if k != "rows"},
        "heterogeneity": payload["terminal_heterogeneity"]["two_way_centered_effect_decomposition"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
