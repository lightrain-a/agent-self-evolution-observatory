from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from collections import Counter
from pathlib import Path
from typing import Any

EXPECTED_ANNOTATIONS_SHA256 = "d770886e249e7be04cc3e183ddd1b9e23c2aa6a7666226b5fe5da17236286ae3"
EXPECTED_CODE_ARCHIVE_SHA256 = "0a77ff7daa3bf65c583deb323d5f015f3da3f51c76726fda1d9ee878ab15b579"
EXPECTED_DATA_ARCHIVE_SHA256 = "2948037f497c81cb2ce8241010c8d93250248217ca9961aa33e59092196b3676"
EXPECTED_ROW_COUNT = 500
EXPECTED_DIFFICULTY_COUNTS = {"easy": 150, "medium": 200, "hard": 150}
CHANNELS = ("ObjCount", "ObjAttr", "OORel", "OARel")
DIFFICULTY_ORDINAL = {"easy": 0, "medium": 1, "hard": 2}
PAIR_MAX_WORD_DIFFERENCE = 10
PAIR_MIN_ENTROPY_DIFFERENCE_BITS = 0.35


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rankdata(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda idx: values[idx])
    ranks = [0.0] * len(values)
    start = 0
    while start < len(order):
        stop = start + 1
        while stop < len(order) and values[order[stop]] == values[order[start]]:
            stop += 1
        average_rank = (start + 1 + stop) / 2.0
        for pos in order[start:stop]:
            ranks[pos] = average_rank
        start = stop
    return ranks


def pearson(left: list[float], right: list[float]) -> float:
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    numerator = sum((x - left_mean) * (y - right_mean) for x, y in zip(left, right))
    left_ss = sum((x - left_mean) ** 2 for x in left)
    right_ss = sum((y - right_mean) ** 2 for y in right)
    if not left_ss or not right_ss:
        return 0.0
    return numerator / math.sqrt(left_ss * right_ss)


def spearman(left: list[float], right: list[float]) -> float:
    return pearson(rankdata(left), rankdata(right))


def spec_count(raw: str) -> int:
    return len([item for item in str(raw or "").split(";") if item.strip()])


def type_entropy(counts: dict[str, int]) -> float:
    total = sum(counts.values())
    if not total:
        return 0.0
    proportions = [value / total for value in counts.values() if value]
    return -sum(value * math.log2(value) for value in proportions)


def quantiles(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)

    def q(frac: float) -> float:
        return ordered[int(round((len(ordered) - 1) * frac))]

    return {
        "min": round(float(ordered[0]), 6),
        "q1": round(float(q(0.25)), 6),
        "median": round(float(statistics.median(ordered)), 6),
        "q3": round(float(q(0.75)), 6),
        "max": round(float(ordered[-1]), 6),
    }


def normalize_row(row: dict[str, str]) -> dict[str, Any]:
    counts = {channel: spec_count(row[channel]) for channel in CHANNELS}
    total = sum(counts.values())
    entropy = type_entropy(counts)
    description = row["Description"].strip()
    return {
        "id": int(row["ID"]),
        "description": description,
        "difficulty": row["Difficulty"].strip(),
        "instruction_words": len(description.split()),
        "type_counts": counts,
        "total_specs": total,
        "active_types": sum(value > 0 for value in counts.values()),
        "type_entropy_bits": entropy,
    }


def select_matched_pairs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates: list[tuple[float, int, int, int]] = []
    for left_idx, left in enumerate(rows):
        for right_idx in range(left_idx + 1, len(rows)):
            right = rows[right_idx]
            if left["total_specs"] != right["total_specs"]:
                continue
            if left["difficulty"] != right["difficulty"]:
                continue
            word_difference = abs(left["instruction_words"] - right["instruction_words"])
            if word_difference > PAIR_MAX_WORD_DIFFERENCE:
                continue
            entropy_difference = abs(left["type_entropy_bits"] - right["type_entropy_bits"])
            if entropy_difference < PAIR_MIN_ENTROPY_DIFFERENCE_BITS:
                continue
            candidates.append((entropy_difference, -word_difference, left_idx, right_idx))

    used: set[int] = set()
    selected: list[dict[str, Any]] = []
    for _, _, left_idx, right_idx in sorted(
        candidates,
        key=lambda item: (-item[0], -item[1], rows[item[2]]["id"], rows[item[3]]["id"]),
    ):
        if left_idx in used or right_idx in used:
            continue
        used.update({left_idx, right_idx})
        left, right = rows[left_idx], rows[right_idx]
        low, high = sorted((left, right), key=lambda row: (row["type_entropy_bits"], row["id"]))
        selected.append(
            {
                "low_entropy_id": low["id"],
                "high_entropy_id": high["id"],
                "difficulty": low["difficulty"],
                "total_specs": low["total_specs"],
                "low_words": low["instruction_words"],
                "high_words": high["instruction_words"],
                "word_difference": abs(low["instruction_words"] - high["instruction_words"]),
                "low_entropy_bits": round(low["type_entropy_bits"], 6),
                "high_entropy_bits": round(high["type_entropy_bits"], 6),
                "entropy_difference_bits": round(high["type_entropy_bits"] - low["type_entropy_bits"], 6),
                "low_type_counts": low["type_counts"],
                "high_type_counts": high["type_counts"],
            }
        )
    return selected


def fold_assignment(rows: list[dict[str, Any]]) -> dict[int, int]:
    result: dict[int, int] = {}
    for row in rows:
        material = f"{row['id']}\n{row['description']}".encode("utf-8")
        result[row["id"]] = int(hashlib.sha256(material).hexdigest()[:8], 16) % 5
    return result


def _measurement_dependency_preflight(code_root: Path | None) -> dict[str, Any]:
    if code_root is None:
        return {
            "verified": False,
            "reason": "code root not supplied",
            "scientific_authority": False,
        }
    required = {
        "main": code_root / "main.py",
        "obj_count": code_root / "metrics" / "obj_count.py",
        "obj_attribute": code_root / "metrics" / "obj_attribute.py",
        "obj_obj_relationship": code_root / "metrics" / "obj_obj_relationship.py",
        "obj_arch_relationship": code_root / "metrics" / "obj_arch_relationship.py",
        "vlm_config": code_root / "configs" / "vlms.yaml",
    }
    missing = [str(path) for path in required.values() if not path.is_file()]
    if missing:
        raise SystemExit("SceneEval measurement source missing: " + "; ".join(missing))
    text = {name: path.read_text(encoding="utf-8") for name, path in required.items()}
    checks = {
        "matching_result_saved_separately": "obj_matching_result.json" in text["main"],
        "eval_result_exports_matching_per_category": '"object_matching_per_category"' in text["main"],
        "eval_result_exports_not_matched_objects": '"not_matched_objects"' in text["main"],
        "obj_count_uses_shared_matching": "self.matching_result.per_category" in text["obj_count"],
        "obj_attribute_uses_shared_matching": "self.matching_result.per_category" in text["obj_attribute"],
        "obj_attribute_missing_category_auto_fails": "if num_objects_in_scene == 0:" in text["obj_attribute"] and 'evaluations[spec]["satisfied"] = False' in text["obj_attribute"],
        "obj_obj_relation_uses_shared_matching": "self.matching_result.per_category" in text["obj_obj_relationship"],
        "obj_obj_relation_missing_objects_auto_fail": "Specs that does not have all objects present in the scene are automatically unsatisfied" in text["obj_obj_relationship"],
        "obj_arch_relation_uses_shared_matching": "self.matching_result.per_category" in text["obj_arch_relationship"],
        "obj_arch_relation_missing_object_auto_fails": "if num_in_scene == 0:" in text["obj_arch_relationship"] and 'evaluations[spec]["satisfied"] = False' in text["obj_arch_relationship"],
        "semantic_metric_vlm_is_gpt4o": 'model_name: "gpt-4o-2024-08-06"' in text["vlm_config"],
        "obj_attribute_resets_vlm": "self.vlm.reset()" in text["obj_attribute"],
        "obj_obj_relation_resets_vlm": "self.vlm.reset()" in text["obj_obj_relationship"],
        "obj_arch_relation_resets_vlm": "self.vlm.reset()" in text["obj_arch_relationship"],
    }
    if not all(checks.values()):
        failed = [key for key, value in checks.items() if not value]
        raise SystemExit("SceneEval measurement dependency contract drifted: " + ", ".join(failed))
    return {
        "verified": True,
        "source_file_sha256": {name: sha256_file(path) for name, path in required.items()},
        "checks": checks,
        "shared_prerequisite": "VLM-produced ObjMatchingResults",
        "dependency_dag": {
            "ObjCount": "directly computed from shared object matching; prerequisite/control rather than a peer downstream coupling outcome",
            "ObjAttr": "requires matched object category; missing category deterministically fails before attribute judgment",
            "OORel": "requires all referenced objects present in shared matching; missing objects deterministically fail before geometric relation check",
            "OARel": "requires referenced object present in shared matching; missing object deterministically fails before architecture relation check",
        },
        "message_history_cross_metric_note": "Semantic metric constructors reset the VLM, so the primary shared dependency is ObjMatching/prerequisite state rather than inherited cross-metric chat history.",
        "raw_matching_observable": True,
        "raw_matching_artifacts": ["obj_matching_result.json", "eval_result.json:object_matching_per_category", "eval_result.json:not_matched_objects"],
        "official_semantic_vlm": "gpt-4o-2024-08-06",
        "local_vlm_substitution_is_official_sceneeval": False,
        "scientific_authority": False,
    }


def build_audit(annotations_path: Path, code_archive: Path | None, data_archive: Path | None, code_root: Path | None = None) -> dict[str, Any]:
    annotation_sha = sha256_file(annotations_path)
    if annotation_sha != EXPECTED_ANNOTATIONS_SHA256:
        raise SystemExit(f"SceneEval annotations digest drifted: {annotation_sha}")
    if code_archive is not None and sha256_file(code_archive) != EXPECTED_CODE_ARCHIVE_SHA256:
        raise SystemExit("SceneEval code release archive digest drifted")
    if data_archive is not None and sha256_file(data_archive) != EXPECTED_DATA_ARCHIVE_SHA256:
        raise SystemExit("SceneEval-500 release archive digest drifted")

    with annotations_path.open(newline="", encoding="utf-8-sig") as handle:
        raw_rows = list(csv.DictReader(handle))
    expected_fields = ["ID", "Description", "ObjCount", "ObjAttr", "OORel", "OARel", "Difficulty"]
    if not raw_rows or list(raw_rows[0].keys()) != expected_fields:
        raise SystemExit("unexpected SceneEval annotation schema")
    if len(raw_rows) != EXPECTED_ROW_COUNT:
        raise SystemExit(f"unexpected SceneEval row count: {len(raw_rows)}")
    rows = [normalize_row(row) for row in raw_rows]
    if [row["id"] for row in rows] != list(range(EXPECTED_ROW_COUNT)):
        raise SystemExit("SceneEval IDs are not the frozen 0..499 sequence")
    difficulty_counts = Counter(row["difficulty"] for row in rows)
    if dict(difficulty_counts) != EXPECTED_DIFFICULTY_COUNTS:
        raise SystemExit(f"SceneEval difficulty counts drifted: {dict(difficulty_counts)}")

    total_specs = [float(row["total_specs"]) for row in rows]
    active_types = [float(row["active_types"]) for row in rows]
    entropy = [float(row["type_entropy_bits"]) for row in rows]
    words = [float(row["instruction_words"]) for row in rows]
    difficulty = [float(DIFFICULTY_ORDINAL[row["difficulty"]]) for row in rows]
    pairs = select_matched_pairs(rows)
    folds = fold_assignment(rows)
    fold_counts = Counter(folds.values())
    fold_root = hashlib.sha256(
        "\n".join(f"{row_id}:{folds[row_id]}" for row_id in sorted(folds)).encode("utf-8")
    ).hexdigest()

    per_difficulty: dict[str, Any] = {}
    for label in ("easy", "medium", "hard"):
        subset = [row for row in rows if row["difficulty"] == label]
        per_difficulty[label] = {
            "n": len(subset),
            "total_specs": quantiles([float(row["total_specs"]) for row in subset]),
            "instruction_words": quantiles([float(row["instruction_words"]) for row in subset]),
            "active_types": quantiles([float(row["active_types"]) for row in subset]),
            "type_entropy_bits": quantiles([float(row["type_entropy_bits"]) for row in subset]),
        }

    pair_difficulty = Counter(pair["difficulty"] for pair in pairs)
    measurement = _measurement_dependency_preflight(code_root)
    return {
        "schema_version": "sceneeval500-outcome-blind-constraint-audit-v1",
        "status": "CLEAR_FOR_ZERO_AUTHORITY_GENERATOR_REVIEW",
        "scientific_authority": False,
        "execution_authority": False,
        "provider_calls_executed": 0,
        "gpu_calls_executed": 0,
        "outcome_exposure": {
            "generated_scene_outputs_read": False,
            "per_case_metric_outputs_read": False,
            "published_per_case_baseline_scores_read": False,
            "selection_conditioned_on_generator_performance": False,
            "consumed_fields": expected_fields,
            "note": "Only released prompt/constraint metadata and benchmark-authored difficulty labels are consumed. Difficulty labels are treated as metadata controls, never as generator outcomes.",
        },
        "source": {
            "benchmark": "SceneEval-500",
            "benchmark_release": "SceneEval-500_v250610",
            "benchmark_release_commit_display": "3b84b5e",
            "annotations_file": "annotations.csv",
            "annotations_bytes": annotations_path.stat().st_size,
            "annotations_sha256": annotation_sha,
            "data_archive_sha256": EXPECTED_DATA_ARCHIVE_SHA256,
            "evaluator_release": "SceneEval_v1.1.1",
            "evaluator_release_commit_display": "5d999f2",
            "code_archive_sha256": EXPECTED_CODE_ARCHIVE_SHA256,
            "instruction_count": len(rows),
            "difficulty_counts": dict(difficulty_counts),
            "constraint_channels": list(CHANNELS),
            "channel_semantics": {
                "ObjCount": "object-count requirements",
                "ObjAttr": "object-attribute requirements",
                "OORel": "object-object relationship requirements",
                "OARel": "object-architecture relationship requirements",
            },
        },
        "metadata_structure": {
            "nonempty_channel_rows": {
                channel: sum(row["type_counts"][channel] > 0 for row in rows) for channel in CHANNELS
            },
            "total_explicit_specs": int(sum(row["total_specs"] for row in rows)),
            "per_difficulty": per_difficulty,
        },
        "constructs": {
            "raw_total_spec_count": {
                "definition": "total semicolon-delimited released requirements across ObjCount, ObjAttr, OORel, and OARel",
                "spearman_with_instruction_words": round(spearman(total_specs, words), 6),
                "spearman_with_authored_difficulty": round(spearman(total_specs, difficulty), 6),
                "disposition": "DIRECT_DIFFICULTY_LOAD_AXIS_NOT_NOVEL_PRIMARY_OBJECT",
                "may_be_primary_scientific_object": False,
            },
            "active_constraint_type_count": {
                "definition": "number of non-empty released requirement channels among the four SceneEval semantic channels",
                "spearman_with_instruction_words": round(spearman(active_types, words), 6),
                "spearman_with_authored_difficulty": round(spearman(active_types, difficulty), 6),
                "role": "descriptive covariate only",
                "may_be_primary_scientific_object": False,
            },
            "constraint_type_entropy": {
                "definition": "Shannon entropy in bits over the four released per-instruction requirement-channel counts",
                "maximum_bits": 2.0,
                "spearman_with_instruction_words": round(spearman(entropy, words), 6),
                "spearman_with_authored_difficulty": round(spearman(entropy, difficulty), 6),
                "role": "pre-outcome moderator/stratifier for cross-type coupling residuals; not a standalone complexity law",
                "disposition": "ORTHOGONAL_ENOUGH_FOR_MATCHED_COUPLING_MODERATOR",
                "may_be_primary_scientific_object": False,
            },
            "instruction_words": {
                "spearman_with_authored_difficulty": round(spearman(words, difficulty), 6),
                "role": "mandatory load control",
            },
        },
        "direct_collision": {
            "finding": "Benchmark-authored difficulty is already strongly aligned with released requirement count and instruction length, so a result that merely recovers easy/medium/hard degradation or total-spec degradation cannot constitute the cross-substrate contribution.",
            "surviving_object": "prerequisite-aware residual coupling among downstream semantic requirement channels after controlling marginal type difficulty, total requirement load, instruction length, authored difficulty, generator identity, shared object-matching state, and scene-level generic failure propensity",
            "strongest_null": "prerequisite-aware conditional independence plus exchangeable scene-level frailty; a plain multiplicative marginal model is only the first null layer",
        },
        "measurement_dependency_preflight": measurement,
        "strict_matched_f0": {
            "selection_uses_outcomes": False,
            "same_total_spec_count": True,
            "same_authored_difficulty": True,
            "max_instruction_word_difference": PAIR_MAX_WORD_DIFFERENCE,
            "min_type_entropy_difference_bits": PAIR_MIN_ENTROPY_DIFFERENCE_BITS,
            "selection_rule": "greedy maximum-contrast disjoint pairing sorted by descending entropy difference, then ascending word difference and scene IDs; frozen before any generated-scene or metric output access",
            "selected_disjoint_pairs": len(pairs),
            "pairs_by_difficulty": dict(pair_difficulty),
            "pairs": pairs,
            "role": "pre-outcome robustness panel for independent-null residuals; raw success differences alone are not confirmatory",
        },
        "future_analysis_contract_if_authorized": {
            "primary_population": "all 500 SceneEval-500 instructions for every independently qualified generator with official raw object-matching/prerequisite state and per-requirement semantic outcomes",
            "primary_outcome_channels": ["ObjAttr", "OORel", "OARel"],
            "prerequisite_control_channel": "ObjCount / shared ObjMatching state",
            "outcome_unit": "prerequisite-eligible downstream semantic requirement spec nested within instruction, channel, and generator; missing-prerequisite outcomes are modeled as prerequisite failures, not treated as peer downstream interaction evidence",
            "null_ladder": {
                "N0": "calibrated independent downstream marginals using generator identity, authored difficulty, instruction words, total spec count, and per-channel loads",
                "N1": "N0 plus explicit official shared ObjMatching/prerequisite state for each downstream spec",
                "N2": "N1 plus exchangeable scene-level latent frailty/overdispersion absorbing generic scene quality; no type-specific downstream covariance/interaction"
            },
            "strongest_null_model": "N2 prerequisite-aware conditional independence plus exchangeable scene-level frailty",
            "candidate_model": "add preregistered type-specific downstream covariance/interaction topology among ObjAttr, OORel, and OARel beyond N2, with identifiability constraints frozen before outcomes",
            "primary_disagreement_test": "on frozen instruction-grouped held-out folds, the candidate must improve predictive log loss/ELPD over N2 and leave positive preregistered type-specific residual dependence on prerequisite-eligible outcomes",
            "entropy_moderation_test": "N2 residual coupling is larger at higher pre-outcome constraint-type entropy under frozen load/difficulty controls; secondary only",
            "held_out_fold_rule": "sha256(SceneEval ID + newline + Description) modulo 5",
            "held_out_fold_counts": {str(key): fold_counts[key] for key in sorted(fold_counts)},
            "held_out_fold_assignment_sha256": fold_root,
            "robustness_panel": "the frozen strict_matched_f0 pairs; compare prerequisite-aware N2 residual rather than raw success",
            "measurement_negative_control": "repeat the downstream residual analysis on an oracle/verified-object-matching subset or otherwise independently verified matching state; coupling that disappears after correct matching is evaluator-induced, not generator-side integration evidence",
            "no_outcome_rematching": True,
            "no_threshold_retuning_after_outcomes": True,
            "no_generator_dropping_after_outcomes": True,
            "no_metric_channel_dropping_after_outcomes": True,
        },
        "falsifiers": [
            "The prerequisite-aware N2 null matches held-out downstream failure behavior within the preregistered uncertainty criterion.",
            "Any apparent downstream cross-type coupling disappears after explicit shared ObjMatching/prerequisite conditioning or exchangeable scene-level frailty.",
            "The interaction advantage exists only under one evaluator implementation or disappears on an oracle/verified-matching negative control.",
            "The frozen matched panel fails to show the preregistered entropy moderation of N2 residuals.",
        ],
        "authority": {
            "canonical_generator": False,
            "problem_gate": False,
            "paper_design": False,
            "method": False,
            "experiment": False,
            "local_validation": False,
            "p0": False,
            "provider": False,
            "gpu": False,
            "scientific": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--code-archive", type=Path)
    parser.add_argument("--data-archive", type=Path)
    parser.add_argument("--code-root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    audit = build_audit(args.annotations, args.code_archive, args.data_archive, args.code_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": audit["status"],
        "annotation_sha256": audit["source"]["annotations_sha256"],
        "total_specs_word_rho": audit["constructs"]["raw_total_spec_count"]["spearman_with_instruction_words"],
        "total_specs_difficulty_rho": audit["constructs"]["raw_total_spec_count"]["spearman_with_authored_difficulty"],
        "entropy_word_rho": audit["constructs"]["constraint_type_entropy"]["spearman_with_instruction_words"],
        "matched_pairs": audit["strict_matched_f0"]["selected_disjoint_pairs"],
        "authority": audit["authority"],
    }, indent=2))


if __name__ == "__main__":
    main()
