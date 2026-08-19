from __future__ import annotations

import argparse
import copy
import hashlib
import importlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bundle_sha256(paths: list[Path], root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths):
        rel = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(len(rel).to_bytes(8, "big"))
        digest.update(rel)
        data = path.read_bytes()
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def probabilities_from_raw_weights(ids: list[str], weights: list[float]) -> dict[str, float]:
    if len(ids) != len(weights) or not ids:
        raise ValueError("ids and weights must be same nonzero length")
    if any(float(w) <= 0 for w in weights):
        raise ValueError("all sampling weights must be positive")
    total = sum(float(w) for w in weights)
    return {str(skill_id): float(weight) / total for skill_id, weight in zip(ids, weights, strict=True)}


def exact_clone_probabilities(
    ids: list[str],
    weights: list[float],
    *,
    target_id: str,
    clone_id: str,
) -> dict[str, float]:
    if target_id not in ids or clone_id in ids:
        raise ValueError("target must exist and clone_id must be fresh")
    target_index = ids.index(target_id)
    return probabilities_from_raw_weights(ids + [clone_id], weights + [float(weights[target_index])])


def quotient_conserved_clone_probabilities(
    base_probabilities: dict[str, float],
    *,
    target_id: str,
    clone_id: str,
) -> dict[str, float]:
    """Split one semantic family's existing mass across an exact clone pair.

    This is a controller-design control, not author behavior. The aggregate
    target-family mass is conserved, so exact cloning changes responsibility
    inside the quotient class but not semantic mass.
    """
    if target_id not in base_probabilities or clone_id in base_probabilities:
        raise ValueError("target must exist and clone_id must be fresh")
    out = dict(base_probabilities)
    family_mass = float(base_probabilities[target_id])
    out[target_id] = family_mass / 2.0
    out[clone_id] = family_mass / 2.0
    if abs(sum(out.values()) - 1.0) > 1e-12:
        raise ValueError("base probabilities must sum to one")
    return out


def semantic_exposures(
    rows: list[dict[str, Any]],
    probabilities: dict[str, float],
    *,
    clone_target: str | None = None,
    clone_id: str | None = None,
) -> list[float]:
    result: list[float] = []
    for row in rows:
        members = [str(value) for value in row.get("accepted_skill_ids") or []]
        exposure = sum(probabilities.get(skill_id, 0.0) for skill_id in members)
        if clone_target and clone_id and clone_target in members:
            exposure += probabilities[clone_id]
        result.append(float(exposure))
    return result


def normalized_profile_tv(left: list[float], right: list[float]) -> float:
    left_total = sum(left)
    right_total = sum(right)
    if left_total <= 0 or right_total <= 0:
        raise ValueError("profiles must have positive total mass")
    return 0.5 * sum(abs(a / left_total - b / right_total) for a, b in zip(left, right, strict=True))


def questioner_message_key(messages: list[dict[str, str]]) -> str:
    canonical = json.dumps(messages, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def prompt_mixture(
    skills: list[dict[str, Any]],
    probabilities: dict[str, float],
    *,
    build_questioner_messages: Any,
) -> dict[str, float]:
    mixture: dict[str, float] = {}
    for skill in skills:
        skill_id = str(skill["id"])
        messages = build_questioner_messages(skill, disclosure_level="full")
        key = questioner_message_key(messages)
        mixture[key] = mixture.get(key, 0.0) + float(probabilities.get(skill_id, 0.0))
    return mixture


def mapping_tv(left: dict[str, float], right: dict[str, float]) -> float:
    keys = set(left) | set(right)
    return 0.5 * sum(abs(float(left.get(key, 0.0)) - float(right.get(key, 0.0))) for key in keys)


def audit_clone(
    rows: list[dict[str, Any]],
    base_probabilities: dict[str, float],
    cloned_probabilities: dict[str, float],
    *,
    target_id: str,
    clone_id: str,
) -> dict[str, Any]:
    before = semantic_exposures(rows, base_probabilities)
    after = semantic_exposures(rows, cloned_probabilities, clone_target=target_id, clone_id=clone_id)
    if not before or min(before) <= 0:
        raise ValueError("audit rows must be covered under the base controller")

    changes = [new - old for old, new in zip(before, after, strict=True)]
    relative = [new / old - 1.0 for old, new in zip(before, after, strict=True)]
    target_mask = [target_id in [str(value) for value in row.get("accepted_skill_ids") or []] for row in rows]
    target_relative = [value for value, keep in zip(relative, target_mask, strict=True) if keep]
    family_before = float(base_probabilities[target_id])
    family_after = float(cloned_probabilities[target_id] + cloned_probabilities[clone_id])

    return {
        "target_skill_id": target_id,
        "base_target_package_probability": family_before,
        "cloned_target_package_probability_each": float(cloned_probabilities[target_id]),
        "cloned_semantic_family_probability": family_after,
        "semantic_family_relative_change": family_after / family_before - 1.0,
        "target_support_rows": int(sum(target_mask)),
        "covered_rows": len(rows),
        "rows_with_positive_exposure_change": sum(value > 1e-15 for value in changes),
        "rows_with_negative_exposure_change": sum(value < -1e-15 for value in changes),
        "rows_with_zero_exposure_change": sum(abs(value) <= 1e-15 for value in changes),
        "target_support_relative_exposure_change_min": min(target_relative) if target_relative else None,
        "target_support_relative_exposure_change_max": max(target_relative) if target_relative else None,
        "all_rows_relative_exposure_change_min": min(relative),
        "all_rows_relative_exposure_change_max": max(relative),
        "base_exposure_ratio": max(before) / min(before),
        "cloned_exposure_ratio": max(after) / min(after),
        "normalized_exposure_profile_tv": normalized_profile_tv(before, after),
        "maximum_absolute_exposure_change": max(abs(value) for value in changes),
    }


def run(author_repo: Path, membership: Path) -> dict[str, Any]:
    author_repo = author_repo.resolve()
    membership = membership.resolve()
    commit = subprocess.check_output(["git", "-C", str(author_repo), "rev-parse", "HEAD"], text=True).strip()
    library_py = author_repo / "skill_library" / "library.py"
    question_generate_py = author_repo / "question_generate" / "question_generate.py"
    package_root = author_repo / "tool_call" / "packages"
    package_files = [path for path in package_root.rglob("*") if path.is_file()]

    sys.path.insert(0, str(author_repo))
    try:
        library = importlib.import_module("skill_library.library")
        prompts = importlib.import_module("tool_call.prompts")
        initial_skills = library.load_initial_skills()
        raw_weights = library.sampling_weights(
            initial_skills,
            current_iteration=0,
            use_quality=True,
            use_exploration=True,
            use_decay=False,
        )
    finally:
        if sys.path and sys.path[0] == str(author_repo):
            sys.path.pop(0)

    ids = [str(skill["id"]) for skill in initial_skills]
    base_probabilities = probabilities_from_raw_weights(ids, [float(value) for value in raw_weights])
    base_prompt_mixture = prompt_mixture(
        initial_skills,
        base_probabilities,
        build_questioner_messages=prompts.build_questioner_messages,
    )
    level1 = [
        row for row in load_jsonl(membership)
        if int(row.get("level") or -1) == 1 and row.get("accepted_skill_ids")
    ]
    active_level1 = sorted({str(skill) for row in level1 for skill in row.get("accepted_skill_ids") or []})

    audits = []
    duplicate_filter_checks = []
    for target_id in active_level1:
        if target_id not in ids:
            raise RuntimeError(f"released support package missing from author initial library: {target_id}")
        target_index = ids.index(target_id)
        target_skill = initial_skills[target_index]
        clone_id = f"{target_id}__stri_exact_clone"

        # Counterfactual representation intervention at the released sampler input.
        # Re-run the author's own weighting function on an actual same-state clone;
        # do not infer the clone weight by hand from the base controller.
        clone_skill = copy.deepcopy(target_skill)
        clone_skill["id"] = clone_id
        augmented_skills = [copy.deepcopy(skill) for skill in initial_skills] + [clone_skill]
        augmented_weights = library.sampling_weights(
            augmented_skills,
            current_iteration=0,
            use_quality=True,
            use_exploration=True,
            use_decay=False,
        )
        augmented_ids = [str(skill["id"]) for skill in augmented_skills]
        cloned = probabilities_from_raw_weights(augmented_ids, [float(value) for value in augmented_weights])
        audit = audit_clone(level1, base_probabilities, cloned, target_id=target_id, clone_id=clone_id)
        quotient_conserved = quotient_conserved_clone_probabilities(
            base_probabilities,
            target_id=target_id,
            clone_id=clone_id,
        )
        quotient_audit = audit_clone(
            level1,
            base_probabilities,
            quotient_conserved,
            target_id=target_id,
            clone_id=clone_id,
        )
        target_messages = prompts.build_questioner_messages(target_skill, disclosure_level="full")
        clone_messages = prompts.build_questioner_messages(clone_skill, disclosure_level="full")
        augmented_prompt_mixture = prompt_mixture(
            augmented_skills,
            cloned,
            build_questioner_messages=prompts.build_questioner_messages,
        )
        target_prompt_key = questioner_message_key(target_messages)
        other_prompt_keys = sorted(set(base_prompt_mixture) - {target_prompt_key})
        quotient_prompt_mixture = prompt_mixture(
            augmented_skills,
            quotient_conserved,
            build_questioner_messages=prompts.build_questioner_messages,
        )
        audit.update(
            {
                "target_raw_sampling_weight": float(raw_weights[target_index]),
                "clone_raw_sampling_weight_recomputed_by_author": float(augmented_weights[-1]),
                "clone_raw_weight_equals_target_raw_weight": abs(float(augmented_weights[-1]) - float(raw_weights[target_index])) <= 1e-12,
                "questioner_prompt_control": {
                    "target_and_clone_messages_exactly_equal": target_messages == clone_messages,
                    "target_message_sha256": questioner_message_key(target_messages),
                    "clone_message_sha256": questioner_message_key(clone_messages),
                    "released_sampler_prompt_mixture_tv_after_clone": mapping_tv(base_prompt_mixture, augmented_prompt_mixture),
                    "base_distinct_prompt_classes": len(base_prompt_mixture),
                    "augmented_distinct_prompt_classes": len(augmented_prompt_mixture),
                    "target_prompt_class_probability_before": float(base_prompt_mixture[target_prompt_key]),
                    "target_prompt_class_probability_after_released_clone": float(augmented_prompt_mixture[target_prompt_key]),
                    "other_prompt_class_count": len(other_prompt_keys),
                    "other_prompt_class_probability_before_values": sorted({float(base_prompt_mixture[key]) for key in other_prompt_keys}),
                    "other_prompt_class_probability_after_values": sorted({float(augmented_prompt_mixture[key]) for key in other_prompt_keys}),
                    "exact_tv_decomposition": "0.5*(abs(2/16-1/15)+14*abs(1/16-1/15))=7/120",
                    "quotient_conserved_prompt_mixture_tv_after_clone": mapping_tv(base_prompt_mixture, quotient_prompt_mixture),
                },
                "quotient_conserved_control": {
                    "target_probability": float(quotient_conserved[target_id]),
                    "clone_probability": float(quotient_conserved[clone_id]),
                    "semantic_family_probability": float(quotient_conserved[target_id] + quotient_conserved[clone_id]),
                    "semantic_family_relative_change": quotient_audit["semantic_family_relative_change"],
                    "rows_with_nonzero_exposure_change": quotient_audit["rows_with_positive_exposure_change"] + quotient_audit["rows_with_negative_exposure_change"],
                    "exposure_ratio": quotient_audit["cloned_exposure_ratio"],
                    "normalized_exposure_profile_tv": quotient_audit["normalized_exposure_profile_tv"],
                },
            }
        )
        audits.append(audit)

        duplicate, duplicate_score = library.find_duplicate_skill(
            str(target_skill.get("name") or ""),
            str(target_skill.get("description") or ""),
            initial_skills,
            threshold=0.33,
        )
        duplicate_filter_checks.append(
            {
                "target_skill_id": target_id,
                "literal_exact_clone_detected_as_duplicate": duplicate is not None and str(duplicate.get("id") or "") == target_id,
                "duplicate_score": float(duplicate_score),
                "threshold": 0.33,
            }
        )

    all_weights_equal = max(raw_weights) - min(raw_weights) <= 1e-12
    all_stats_pristine = all(int((skill.get("stats") or {}).get("attempts", 0)) == 0 for skill in initial_skills)
    expected_uniform_probability = 1.0 / len(ids)
    checks = {
        "author_commit_matches_frozen_release": commit == "bb693c89fee66e1f824d6a777759a49b7a295a83",
        "fifteen_initial_packages": len(ids) == 15,
        "all_initial_package_sampling_weights_equal": all_weights_equal,
        "all_initial_package_stats_pristine": all_stats_pristine,
        "base_probabilities_uniform": all(abs(value - expected_uniform_probability) <= 1e-12 for value in base_probabilities.values()),
        "all_level1_active_packages_audited": len(audits) == len(active_level1) == 6,
        "every_exact_clone_changes_released_controller_exposure": all(row["rows_with_positive_exposure_change"] > 0 and row["rows_with_negative_exposure_change"] > 0 for row in audits),
        "every_exact_clone_raises_semantic_family_probability": all(row["semantic_family_relative_change"] > 0 for row in audits),
        "every_exact_clone_changes_normalized_exposure_profile": all(row["normalized_exposure_profile_tv"] > 0 for row in audits),
        "clone_weights_recomputed_by_author_sampling_function": all(row["clone_raw_weight_equals_target_raw_weight"] for row in audits),
        "author_duplicate_filter_would_reject_literal_exact_text_clone": all(
            row["literal_exact_clone_detected_as_duplicate"] and abs(row["duplicate_score"] - 1.0) <= 1e-12
            for row in duplicate_filter_checks
        ),
        "quotient_conserved_allocation_exactly_restores_base_exposure": all(
            row["quotient_conserved_control"]["rows_with_nonzero_exposure_change"] == 0
            and abs(row["quotient_conserved_control"]["semantic_family_relative_change"]) <= 1e-12
            and abs(row["quotient_conserved_control"]["normalized_exposure_profile_tv"]) <= 1e-12
            and abs(row["quotient_conserved_control"]["exposure_ratio"] - row["base_exposure_ratio"]) <= 1e-12
            for row in audits
        ),
        "same_content_clone_has_identical_author_questioner_messages": all(
            row["questioner_prompt_control"]["target_and_clone_messages_exactly_equal"] for row in audits
        ),
        "released_initialization_has_fifteen_distinct_questioner_prompt_classes": all(
            row["questioner_prompt_control"]["base_distinct_prompt_classes"] == 15
            and row["questioner_prompt_control"]["augmented_distinct_prompt_classes"] == 15
            and row["questioner_prompt_control"]["other_prompt_class_count"] == 14
            for row in audits
        ),
        "released_sampler_clone_changes_author_questioner_prompt_mixture": all(
            row["questioner_prompt_control"]["released_sampler_prompt_mixture_tv_after_clone"] > 0 for row in audits
        ),
        "quotient_conservation_exactly_restores_author_questioner_prompt_mixture": all(
            abs(row["questioner_prompt_control"]["quotient_conserved_prompt_mixture_tv_after_clone"]) <= 1e-12
            for row in audits
        ),
    }

    return {
        "schema_version": "1.0",
        "paper_id": "STRI",
        "analysis_type": "released-controller exact-clone allocation audit",
        "author_release": {
            "commit": commit,
            "library_py_sha256": sha256(library_py),
            "question_generate_py_sha256": sha256(question_generate_py),
            "initial_tool_call_package_bundle_sha256": bundle_sha256(package_files, author_repo),
            "initial_tool_call_package_file_count": len(package_files),
            "sampling_function": "skill_library.library.sample_skill -> sampling_weights -> random.choices",
            "question_generation_callsite": "question_generate.question_generate._build_prompts",
            "default_sampler_flags": {
                "use_quality": True,
                "use_exploration": True,
                "use_decay": False,
            },
        },
        "frozen_initial_controller": {
            "package_count": len(ids),
            "package_ids": ids,
            "raw_sampling_weights": {skill_id: float(weight) for skill_id, weight in zip(ids, raw_weights, strict=True)},
            "normalized_sampling_probabilities": base_probabilities,
            "all_initial_stats_pristine": all_stats_pristine,
            "interpretation": "At the released initial state, identical package-local statistics make the default quality-plus-exploration sampler uniform over the 15 package identities.",
        },
        "level1_support": {
            "covered_rows": len(level1),
            "active_package_ids": active_level1,
            "membership_sha256": sha256(membership),
        },
        "audit_intervention": {
            "kind": "counterfactual same-state exact-clone reparameterization applied directly to the released sampler input",
            "is_author_admission_path_claim": False,
            "author_induction_duplicate_threshold": 0.33,
            "literal_exact_clone_duplicate_filter_checks": duplicate_filter_checks,
            "interpretation": "The intervention audits whether the released identity-indexed sampler mapping is invariant to an exact representation refinement. It does not claim that the author's induction-time admission path would store a literal exact text clone; the released Jaccard duplicate filter detects such a literal duplicate.",
        },
        "exact_clone_audits": audits,
        "headline": {
            "base_package_probability": expected_uniform_probability,
            "released_pristine_singleton_eligibility_exposure": expected_uniform_probability,
            "released_pristine_double_support_eligibility_exposure": 2.0 * expected_uniform_probability,
            "released_pristine_double_to_singleton_exposure_ratio": 2.0,
            "exact_clone_family_probability": 2.0 / 16.0,
            "exact_clone_family_relative_change": (2.0 / 16.0) / (1.0 / 15.0) - 1.0,
            "untouched_package_probability_after_clone": 1.0 / 16.0,
            "untouched_package_relative_change": (1.0 / 16.0) / (1.0 / 15.0) - 1.0,
            "base_level1_exposure_ratio": audits[0]["base_exposure_ratio"] if audits else None,
            "clone_level1_exposure_ratio_all_targets": sorted({row["cloned_exposure_ratio"] for row in audits}),
            "normalized_exposure_profile_tv_range": [
                min(row["normalized_exposure_profile_tv"] for row in audits),
                max(row["normalized_exposure_profile_tv"] for row in audits),
            ] if audits else None,
            "quotient_conserved_clone_family_probability": expected_uniform_probability,
            "quotient_conserved_clone_probability_each": expected_uniform_probability / 2.0,
            "quotient_conserved_exposure_profile_tv_all_targets": sorted(
                {row["quotient_conserved_control"]["normalized_exposure_profile_tv"] for row in audits}
            ),
            "released_initialization_distinct_questioner_prompt_classes": len(base_prompt_mixture),
            "released_sampler_questioner_prompt_mixture_tv_after_clone_all_targets": sorted(
                {row["questioner_prompt_control"]["released_sampler_prompt_mixture_tv_after_clone"] for row in audits}
            ),
            "released_sampler_questioner_prompt_mixture_tv_exact_decomposition": "0.5*(abs(2/16-1/15)+14*abs(1/16-1/15))=7/120",
            "quotient_conserved_questioner_prompt_mixture_tv_after_clone_all_targets": sorted(
                {row["questioner_prompt_control"]["quotient_conserved_prompt_mixture_tv_after_clone"] for row in audits}
            ),
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "claim_boundary": {
            "supported": [
                "the released Skill-SP pre-task sampler assigns probability to package identities using package-local quality/exploration weights",
                "at the released pristine initial state the 15 package weights are equal, so the controller is uniform over identities and double-supported Level-1 rows receive twice the additive eligibility opportunity of singleton rows",
                "under a counterfactual same-state exact-clone reparameterization applied directly to the released sampler input, the author's own sampling_weights function changes controller allocation and the induced Level-1 additive eligibility-exposure profile without changing support semantics",
                "a same-content clone produces exactly the same released questioner message string as its source package, yet identity-normalized sampling changes the distribution over those actual questioner message classes",
                "a quotient-conserved allocation that splits the original semantic-family mass across the exact clone pair restores both the base Level-1 exposure profile and the released questioner prompt-mixture distribution exactly for all six audited clone targets",
            ],
            "not_supported": [
                "the author's induction-time admission path would accept a literal exact text clone; its released Jaccard duplicate filter detects the literal duplicate",
                "the controller-level exposure change necessarily changes generated task probabilities by the same amount",
                "the exposure change causes downstream utility degradation",
                "all later Skill-SP iterations remain uniform after package statistics diverge",
            ],
        },
        "model_calls": 0,
        "gpu_hours": 0.0,
        "scientific_authority": False,
        "authority": {"dynamic_claim": False, "downstream_utility_claim": False, "gpu": False},
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--author-repo", type=Path, required=True)
    ap.add_argument("--membership", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    result = run(args.author_repo, args.membership)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"all_checks_pass": result["all_checks_pass"], "headline": result["headline"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
