from __future__ import annotations

import argparse
import collections
import copy
import glob
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")


def _validator_bundle_sha(package_root: Path) -> str:
    h = hashlib.sha256()
    for path in sorted(package_root.glob("skill_*/validator.py")):
        rel = path.relative_to(package_root).as_posix()
        file_sha = _sha(path)
        h.update((rel + "\0" + file_sha + "\n").encode("utf-8"))
    return h.hexdigest()


def _skill_metadata(skill_md: Path) -> dict[str, Any]:
    text = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.S)
    if not match:
        raise RuntimeError(f"missing JSON front matter: {skill_md}")
    metadata = json.loads(match.group(1))
    stats = _json(skill_md.parent / "stats.json")
    examples_path = skill_md.parent / "examples.jsonl"
    example = ""
    if examples_path.exists():
        first = next((line for line in examples_path.read_text(encoding="utf-8").splitlines() if line.strip()), "")
        if first:
            example = str(json.loads(first).get("example") or "")
    return {
        "id": str(metadata["id"]),
        "name": str(metadata.get("name") or metadata["id"]),
        "description": str(metadata.get("description") or ""),
        "example": example,
        "added_iteration": int(metadata.get("added_iteration", 0)),
        "stats": stats,
    }


def validate_contract(contract: dict[str, Any]) -> dict[str, Any]:
    repo = Path(contract["author_asset"]["repo"])
    package_root = repo / "tool_call/packages"
    commit = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    library_py = repo / "skill_library/library.py"
    package_library_py = repo / "skill_library/package_library.py"
    level_1 = repo / "benchmarks/API-Bank/level-1-api_processed.json"
    level_3 = repo / "benchmarks/API-Bank/level-3-api_processed.json"
    checks = {
        "repo_exists": repo.is_dir(),
        "author_commit": commit == contract["author_asset"]["commit"],
        "library_sha": _sha(library_py) == contract["author_asset"]["library_py_sha256"],
        "package_library_sha": _sha(package_library_py) == contract["author_asset"]["package_library_py_sha256"],
        "validator_bundle_sha": _validator_bundle_sha(package_root) == contract["author_asset"]["validator_bundle_sha256"],
        "api_bank_level_1_sha": _sha(level_1) == contract["author_asset"]["api_bank_level_1_sha256"],
        "api_bank_level_3_sha": _sha(level_3) == contract["author_asset"]["api_bank_level_3_sha256"],
        "all_rows_selected": contract["selection"]["all_rows_selected"] is True,
        "selection_outcome_blind": contract["selection"]["selection_reads_validator_outcomes"] is False and contract["selection"]["selection_reads_model_outcomes"] is False,
        "fifteen_skills": len(contract["selection"]["skill_ids"]) == 15,
        "gpu_zero": int(contract["budget"]["gpu_hours"]) == 0,
        "model_calls_zero": int(contract["budget"]["model_calls"]) == 0,
        "new_task_generation_zero": int(contract["budget"]["new_task_generation"]) == 0,
        "authority_locked": all(value is False for value in contract["authority"].values()),
    }
    return {"checks": checks, "pass": all(checks.values()), "actual_commit": commit}


def _load_validators(repo: Path, skill_ids: list[str]) -> dict[str, Any]:
    validators: dict[str, Any] = {}
    for skill_id in skill_ids:
        path = repo / "tool_call/packages" / skill_id / "validator.py"
        if not path.exists():
            raise RuntimeError(f"validator missing: {skill_id}")
        spec = importlib.util.spec_from_file_location(f"skillsp_validator_{skill_id}", path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"cannot load validator: {skill_id}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if not hasattr(module, "validate_sample"):
            raise RuntimeError(f"validate_sample missing: {skill_id}")
        validators[skill_id] = module.validate_sample
    return validators


def _load_rows(repo: Path, levels: list[int]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for level in levels:
        path = repo / f"benchmarks/API-Bank/level-{level}-api_processed.json"
        data = _json(path)
        if not isinstance(data, list):
            raise RuntimeError(f"benchmark is not a list: {path}")
        for index, original in enumerate(data):
            answer = original.get("answer")
            if not (isinstance(answer, list) and len(answer) == 1 and isinstance(answer[0], dict)):
                raise RuntimeError(f"frozen adapter precondition failed at level={level} index={index}")
            adapted = dict(original)
            adapted["answer"] = dict(answer[0])
            rows.append({
                "level": level,
                "index": index,
                "tool": str(answer[0].get("name") or ""),
                "adapted": adapted,
            })
    return rows


def _evaluate_membership(
    rows: list[dict[str, Any]],
    validators: dict[str, Any],
    specific_ids: set[str],
    generic_ids: set[str],
    raw_path: Path,
) -> dict[str, Any]:
    pair_counts: collections.Counter[tuple[str, str]] = collections.Counter()
    tool_multi_counts: collections.Counter[str] = collections.Counter()
    cardinality: collections.Counter[int] = collections.Counter()
    skill_coverage: collections.Counter[str] = collections.Counter()
    covered = 0
    multi = 0
    specific_generic_rows = 0
    distinct_specific_generic_pairs: set[tuple[str, str]] = set()
    raw_path.unlink(missing_ok=True)

    for row in rows:
        accepted: list[str] = []
        diagnostics: dict[str, Any] = {}
        for skill_id, validate_sample in validators.items():
            try:
                result = validate_sample(row["adapted"])
                valid = bool(result.get("valid"))
                diagnostics[skill_id] = {"valid": valid, "errors": list(result.get("errors") or [])}
                if valid:
                    accepted.append(skill_id)
            except Exception as exc:  # fail closed and retain provenance
                diagnostics[skill_id] = {"valid": False, "exception": type(exc).__name__, "message": str(exc)}
        accepted = sorted(accepted)
        cardinality[len(accepted)] += 1
        if accepted:
            covered += 1
        if len(accepted) > 1:
            multi += 1
            tool_multi_counts[row["tool"]] += 1
        for skill_id in accepted:
            skill_coverage[skill_id] += 1
        for i, left in enumerate(accepted):
            for right in accepted[i + 1 :]:
                pair_counts[(left, right)] += 1
        specific = sorted(set(accepted) & specific_ids)
        generic = sorted(set(accepted) & generic_ids)
        if specific and generic:
            specific_generic_rows += 1
            for left in specific:
                for right in generic:
                    distinct_specific_generic_pairs.add((left, right))
        _append_jsonl(raw_path, {
            "level": row["level"],
            "index": row["index"],
            "tool": row["tool"],
            "accepted_skill_ids": accepted,
            "membership_cardinality": len(accepted),
            "specific_skill_ids": specific,
            "generic_skill_ids": generic,
            "validator_diagnostics": diagnostics,
        })

    top_pairs = [
        {"left": pair[0], "right": pair[1], "count": count}
        for pair, count in pair_counts.most_common(30)
    ]
    return {
        "rows_total": len(rows),
        "covered_rows": covered,
        "uncovered_rows": len(rows) - covered,
        "multi_membership_rows": multi,
        "multi_membership_fraction_of_all": multi / max(1, len(rows)),
        "multi_membership_fraction_of_covered": multi / max(1, covered),
        "specific_generic_overlap_rows": specific_generic_rows,
        "specific_generic_overlap_fraction_of_covered": specific_generic_rows / max(1, covered),
        "distinct_specific_generic_overlap_pairs": len(distinct_specific_generic_pairs),
        "specific_generic_pairs": [list(pair) for pair in sorted(distinct_specific_generic_pairs)],
        "distinct_answer_tools_with_multi_membership": len(tool_multi_counts),
        "multi_membership_tool_counts": dict(tool_multi_counts.most_common()),
        "membership_cardinality_histogram": {str(key): value for key, value in sorted(cardinality.items())},
        "skill_coverage": dict(sorted(skill_coverage.items())),
        "top_overlap_pairs": top_pairs,
    }


def _representation_counterfactual(repo: Path, skill_ids: list[str], current_iteration: int) -> dict[str, Any]:
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    from skill_library.library import sampling_weights

    skills = [_skill_metadata(repo / "tool_call/packages" / skill_id / "SKILL.md") for skill_id in skill_ids]
    base_weights = sampling_weights(
        skills,
        current_iteration=current_iteration,
        use_quality=True,
        use_exploration=True,
        use_decay=False,
    )
    base_total = float(sum(base_weights))
    base_probs = {skill["id"]: float(weight) / base_total for skill, weight in zip(skills, base_weights)}
    trials: list[dict[str, Any]] = []

    for target_id in skill_ids:
        index = next(i for i, skill in enumerate(skills) if skill["id"] == target_id)
        clone = copy.deepcopy(skills[index])
        clone["id"] = target_id + "__exact_clone"
        split_skills = skills + [clone]
        split_weights = sampling_weights(
            split_skills,
            current_iteration=current_iteration,
            use_quality=True,
            use_exploration=True,
            use_decay=False,
        )
        split_total = float(sum(split_weights))
        split_prob_by_id = {skill["id"]: float(weight) / split_total for skill, weight in zip(split_skills, split_weights)}
        before = base_probs[target_id]
        after = split_prob_by_id[target_id] + split_prob_by_id[clone["id"]]
        relative = (after / before) - 1.0 if before > 0 else 0.0
        trials.append({
            "skill_id": target_id,
            "base_skill_probability": before,
            "split_original_probability": split_prob_by_id[target_id],
            "split_clone_probability": split_prob_by_id[clone["id"]],
            "equivalence_class_probability_after_split": after,
            "relative_equivalence_class_mass_inflation": relative,
            "semantic_support_changed": False,
            "stats_changed": False,
        })

    return {
        "author_sampling_weights": [float(value) for value in base_weights],
        "base_probabilities": base_probs,
        "clone_trials": trials,
        "minimum_relative_class_mass_inflation": min(t["relative_equivalence_class_mass_inflation"] for t in trials),
        "maximum_relative_class_mass_inflation": max(t["relative_equivalence_class_mass_inflation"] for t in trials),
        "all_clone_counterfactuals_change_mass": all(t["relative_equivalence_class_mass_inflation"] > 0 for t in trials),
    }


def run(contract_path: Path, output_dir: Path) -> dict[str, Any]:
    started = time.monotonic()
    contract = _json(contract_path)
    review = validate_contract(contract)
    if not review["pass"]:
        raise RuntimeError(f"contract validation failed: {review}")
    output_dir.mkdir(parents=True, exist_ok=True)
    _atomic_json(output_dir / "preflight.json", {**review, "contract_sha256": _sha(contract_path)})

    repo = Path(contract["author_asset"]["repo"])
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    skill_ids = list(contract["selection"]["skill_ids"])
    validators = _load_validators(repo, skill_ids)
    rows = _load_rows(repo, list(contract["selection"]["levels"]))
    if len(rows) != int(contract["selection"]["rows_total"]):
        raise RuntimeError(f"row count drift: {len(rows)}")

    membership = _evaluate_membership(
        rows,
        validators,
        set(contract["selection"]["specific_skill_ids"]),
        set(contract["selection"]["generic_skill_ids"]),
        output_dir / "membership.jsonl",
    )
    counterfactual = _representation_counterfactual(
        repo,
        skill_ids,
        int(contract["released_control_plane"]["test_current_iteration"]),
    )

    gate = contract["frozen_gate"]
    checks = {
        "validator_coverage": {
            "actual": membership["covered_rows"],
            "required_min": int(gate["validator_covered_rows_min"]),
            "pass": membership["covered_rows"] >= int(gate["validator_covered_rows_min"]),
        },
        "multi_membership": {
            "actual": membership["multi_membership_fraction_of_covered"],
            "required_min": float(gate["multi_membership_fraction_of_covered_min"]),
            "pass": membership["multi_membership_fraction_of_covered"] >= float(gate["multi_membership_fraction_of_covered_min"]),
        },
        "specific_generic_overlap_rows": {
            "actual": membership["specific_generic_overlap_rows"],
            "required_min": int(gate["specific_generic_overlap_rows_min"]),
            "pass": membership["specific_generic_overlap_rows"] >= int(gate["specific_generic_overlap_rows_min"]),
        },
        "specific_generic_overlap_pairs": {
            "actual": membership["distinct_specific_generic_overlap_pairs"],
            "required_min": int(gate["distinct_specific_generic_overlap_pairs_min"]),
            "pass": membership["distinct_specific_generic_overlap_pairs"] >= int(gate["distinct_specific_generic_overlap_pairs_min"]),
        },
        "multi_membership_tool_diversity": {
            "actual": membership["distinct_answer_tools_with_multi_membership"],
            "required_min": int(gate["distinct_answer_tools_with_multi_membership_min"]),
            "pass": membership["distinct_answer_tools_with_multi_membership"] >= int(gate["distinct_answer_tools_with_multi_membership_min"]),
        },
        "exact_clone_mass_inflation": {
            "actual": counterfactual["minimum_relative_class_mass_inflation"],
            "required_min": float(gate["exact_clone_relative_class_mass_inflation_min"]),
            "pass": counterfactual["minimum_relative_class_mass_inflation"] >= float(gate["exact_clone_relative_class_mass_inflation_min"]),
        },
        "all_clone_trials_change_mass": {
            "actual": counterfactual["all_clone_counterfactuals_change_mass"],
            "required": bool(gate["all_15_clone_counterfactuals_must_change_mass"]),
            "pass": counterfactual["all_clone_counterfactuals_change_mass"] is bool(gate["all_15_clone_counterfactuals_must_change_mass"]),
        },
    }
    positive = all(item["pass"] for item in checks.values())
    decision = "PROVISIONAL_SEMANTIC_MULTIPLICITY_BIAS_SUPPORTED" if positive else "STOP_SEMANTIC_MULTIPLICITY_GATE_NOT_MET"
    result = {
        "schema_version": "1.0",
        "experiment_id": contract["experiment_id"],
        "candidate_id": contract["candidate_id"],
        "decision": decision,
        "scientific_result_available": True,
        "primary_mechanism_positive": positive,
        "scientific_disposition": "POSITIVE_MECHANISM_NOVELTY_UNRESOLVED" if positive else "A_OR_D_GATE_FAILURE",
        "membership": membership,
        "representation_counterfactual": counterfactual,
        "checks": checks,
        "strongest_same_information_reduction": contract["strongest_same_information_reduction"],
        "paper_design_authorized": False,
        "method_authorized": False,
        "p0_authorized": False,
        "gpu_authorized": False,
        "second_backbone_authorized": False,
        "gpu_hours": 0,
        "model_calls": 0,
        "new_task_generation": 0,
        "contract_sha256": _sha(contract_path),
        "author_commit": review["actual_commit"],
        "elapsed_seconds": time.monotonic() - started,
        "next_action": contract["next_if_positive"] if positive else contract["next_if_negative"],
    }
    _atomic_json(output_dir / "result.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.contract, args.output_dir)
    print(json.dumps({
        "decision": result["decision"],
        "covered_rows": result["membership"]["covered_rows"],
        "multi_membership_fraction_of_covered": result["membership"]["multi_membership_fraction_of_covered"],
        "specific_generic_overlap_rows": result["membership"]["specific_generic_overlap_rows"],
        "distinct_specific_generic_overlap_pairs": result["membership"]["distinct_specific_generic_overlap_pairs"],
        "distinct_answer_tools_with_multi_membership": result["membership"]["distinct_answer_tools_with_multi_membership"],
        "minimum_clone_mass_inflation": result["representation_counterfactual"]["minimum_relative_class_mass_inflation"],
        "checks": result["checks"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
