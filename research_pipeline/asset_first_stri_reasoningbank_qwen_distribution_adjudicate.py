"""Scientifically adjudicate the complete frozen Qwen confirmatory experiment."""
from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from statistics import mean
from typing import Any, Mapping, Sequence

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT, sha256_file, utcnow, write_json,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_analysis import (
    bootstrap_ci, missingness_gate, paired_task_sign_flip, permutation_test,
    seed_from_contract, task_statistics,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_behavioral_runner import (
    receipt_path,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_edit_targets import (
    atoms_from_signature,
)

EXPERIMENT_ID = "E1-STRI-REASONINGBANK-QWEN-DISTRIBUTION-V3-20260901"
MANIFEST = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-confirmatory-manifest-20260901.json"
SCHEDULE = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-confirmatory-schedule-20260901.json"
AUTHORITY = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-resource-authority-20260901.json"
STRUCTURAL = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-structural-result-20260901.json"
INDEX = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-confirmatory-index-20260901.json"
RECEIPT_DIR = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-confirmatory-runs-20260901"
OUTPUT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-confirmatory-adjudication-20260901.json"
PERMUTATIONS = 100_000
BOOTSTRAPS = 100_000


def behavior_blocks(receipts: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, list[set[tuple[str, str]]]]]:
    blocks: dict[str, dict[str, list[set[tuple[str, str]]]]] = defaultdict(
        lambda: defaultdict(list))
    for row in receipts:
        if not row["behavior_valid"]:
            continue
        signature = row["behavior_observables"]["edit_target_set"]
        blocks[str(row["instance_id"])][str(row["arm"])].append(
            atoms_from_signature(signature))
    return blocks


def valid_counts(receipts: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, int]]:
    counts = Counter((str(row["instance_id"]), str(row["arm"]))
                     for row in receipts if row["behavior_valid"])
    tasks = sorted({str(row["instance_id"]) for row in receipts})
    return {task: {arm: counts[(task, arm)] for arm in ("A", "D", "N")}
            for task in tasks}


def arm_failure_summary(receipts: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for arm in ("A", "D", "N"):
        rows = [row for row in receipts if row["arm"] == arm]
        valid = sum(bool(row["behavior_valid"]) for row in rows)
        result[arm] = {
            "planned": len(rows), "valid": valid, "missing_or_invalid": len(rows) - valid,
            "failure_rate": (len(rows) - valid) / len(rows),
            "execution_status_counts": dict(sorted(Counter(
                str(row["execution_status"]) for row in rows).items())),
        }
    return result


def r2_summary(receipts: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    result = {}
    for arm in ("A", "D", "N"):
        rows = [row["behavior_observables"]["first_action"] for row in receipts
                if row["arm"] == arm and row["behavior_valid"]]
        result[arm] = {
            "valid_trial_count": len(rows),
            "parse_valid_count": sum(bool(row["parse_valid"]) for row in rows),
            "action_class_counts": dict(sorted(Counter(
                str(row["action_class"]) for row in rows).items())),
            "first_path_counts": dict(sorted(Counter(
                str(row["first_referenced_path"]) for row in rows).items())),
            "first_python_target_counts": dict(sorted(Counter(
                str(row["first_referenced_python_symbol_or_module"]) for row in rows).items())),
        }
    return result


def numeric_summary(values: Sequence[float]) -> dict[str, float | int | None]:
    if not values:
        return {"count": 0, "mean": None, "minimum": None, "maximum": None}
    return {"count": len(values), "mean": mean(values),
            "minimum": min(values), "maximum": max(values)}


def equality_fraction(values: Sequence[str]) -> dict[str, float | int | None]:
    pairs = list(combinations(values, 2))
    if not pairs:
        return {"pair_count": 0, "equal_count": 0, "equal_fraction": None}
    equal = sum(left == right for left, right in pairs)
    return {"pair_count": len(pairs), "equal_count": equal,
            "equal_fraction": equal / len(pairs)}


def r3_summary(receipts: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    result = {}
    numeric_fields = (
        "modified_file_count", "diff_hunk_count", "model_call_count",
        "shell_action_count", "tests_run_count", "trajectory_length",
    )
    for arm in ("A", "D", "N"):
        rows = [row["behavior_observables"] for row in receipts
                if row["arm"] == arm and row["behavior_valid"]]
        by_task: dict[str, list[str]] = defaultdict(list)
        for receipt in receipts:
            if receipt["arm"] == arm and receipt["behavior_valid"]:
                by_task[str(receipt["instance_id"])].append(
                    str(receipt["behavior_observables"]["final_patch_sha256"]))
        result[arm] = {
            "valid_trial_count": len(rows),
            "numeric": {field: numeric_summary(
                [float(row[field]) for row in rows]) for field in numeric_fields},
            "tests_run_trial_count": sum(bool(row["tests_run_indicator"]) for row in rows),
            "submission_state_counts": dict(sorted(Counter(
                str(row["submission_state"]) for row in rows).items())),
            "modified_file_set_counts": dict(sorted(Counter(
                json.dumps(row["modified_file_set"], separators=(",", ":"))
                for row in rows).items())),
            "within_task_exact_patch_equality": {
                task: equality_fraction(values) for task, values in sorted(by_task.items())
            },
        }
    return result


def r4_proportions(receipts: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    grouped: dict[str, dict[str, list[bool]]] = defaultdict(lambda: defaultdict(list))
    for row in receipts:
        r4 = row.get("R4_terminal_outcome") or {}
        if row["behavior_valid"] and r4.get("valid"):
            grouped[str(row["instance_id"])][str(row["arm"])].append(bool(r4["resolved"]))
    tasks = sorted({str(row["instance_id"]) for row in receipts})
    return {
        task: {
            arm: {
                "valid_trials": len(grouped[task][arm]),
                "resolved_trials": sum(grouped[task][arm]),
                "resolution_proportion": (
                    sum(grouped[task][arm]) / len(grouped[task][arm])
                    if grouped[task][arm] else None),
            } for arm in ("A", "D", "N")
        } for task in tasks
    }


def r4_contrast(proportions: Mapping[str, Mapping[str, Mapping[str, Any]]],
                left: str, right: str, manifest_sha: str) -> dict[str, Any]:
    differences = {}
    for task, arms in sorted(proportions.items()):
        if arms[left]["valid_trials"] >= 4 and arms[right]["valid_trials"] >= 4:
            differences[task] = (
                float(arms[left]["resolution_proportion"])
                - float(arms[right]["resolution_proportion"]))
    if not differences:
        return {"decision": "R4_INSUFFICIENT_PAIRED_TASKS", "task_count": 0}
    permutation = paired_task_sign_flip(
        differences, replicates=PERMUTATIONS,
        seed=seed_from_contract(EXPERIMENT_ID, manifest_sha, f"R4-{left}-{right}-sign-flip"))
    ci = bootstrap_ci(
        differences, replicates=BOOTSTRAPS,
        seed=seed_from_contract(EXPERIMENT_ID, manifest_sha, f"R4-{left}-{right}-bootstrap"))
    return {"decision": "R4_TASK_BLOCKED_ANALYSIS_COMPLETE",
            "permutation": permutation, "task_bootstrap_CI": ci}


def average_ranks(values: Sequence[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda index: values[index])
    ranks = [0.0] * len(values)
    start = 0
    while start < len(order):
        end = start + 1
        while end < len(order) and values[order[end]] == values[order[start]]:
            end += 1
        rank = (start + 1 + end) / 2
        for index in order[start:end]:
            ranks[index] = rank
        start = end
    return ranks


def spearman(rows: Sequence[tuple[float, float]]) -> float | None:
    if len(rows) < 3:
        return None
    x, y = [row[0] for row in rows], [row[1] for row in rows]
    rx, ry = average_ranks(x), average_ranks(y)
    mx, my = mean(rx), mean(ry)
    numerator = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    denominator = math.sqrt(sum((a - mx) ** 2 for a in rx)
                            * sum((b - my) ** 2 for b in ry))
    return None if denominator == 0 else numerator / denominator


def failure_differential(decision: str, artifact_refs: list[str]) -> dict[str, Any]:
    if decision == "CONFIRMATORY_SCIENTIFIC_HOLD_INSUFFICIENT_COMPLETE_TASK_BLOCKS":
        observed, layer = "fewer than 20 of 24 complete A/D task blocks", "missingness"
    else:
        observed, layer = "A/D arm-correlated missingness exceeded both frozen thresholds", "missingness"
    return {
        "experiment_id": EXPERIMENT_ID, "stage": "CONFIRMATORY_ADJUDICATION",
        "hypothesis_or_qualification_goal": "task-blocked A-v-D behavioral distribution inference",
        "observed_failure": observed, "failure_layer": layer,
        "root_cause": "reported from immutable exactly-once run receipts",
        "scientific_belief_update": "primary causal interpretation held; descriptive evidence preserved",
        "repair_allowed": False, "repair_scope": None,
        "prohibited_repairs": ["retry", "replacement", "task substitution", "arm reclassification"],
        "artifact_refs": artifact_refs, "authorized_next_action": "report bounded hold without rescue",
    }


def adjudicate(output: Path = OUTPUT) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError("refusing duplicate confirmatory adjudication")
    manifest = json.loads(MANIFEST.read_text())
    schedule = json.loads(SCHEDULE.read_text())
    authority = json.loads(AUTHORITY.read_text())
    structural = json.loads(STRUCTURAL.read_text())
    index = json.loads(INDEX.read_text())
    if not index["execution_complete"] or index["completed_count"] != 432:
        raise RuntimeError("confirmatory execution is not complete")
    if not authority["execution_authorized"]:
        raise RuntimeError("confirmatory execution lacked resource authority")
    receipts = [json.loads(receipt_path(RECEIPT_DIR, unit).read_text())
                for unit in schedule["units"]]
    if len(receipts) != 432 or any(row["attempt_count"] != 1 for row in receipts):
        raise RuntimeError("confirmatory receipt count/attempt drift")
    manifest_sha = sha256_file(MANIFEST)
    blocks = behavior_blocks(receipts)
    counts = valid_counts(receipts)
    failures = arm_failure_summary(receipts)
    missingness = missingness_gate(
        planned_a=failures["A"]["planned"], valid_a=failures["A"]["valid"],
        planned_d=failures["D"]["planned"], valid_d=failures["D"]["valid"])
    ti_ad = task_statistics(blocks, "A", "D")
    analyzable = len(ti_ad)
    insufficient = analyzable < 20
    inference_held = insufficient or missingness["decision"] == "MISSINGNESS_ARM_IMBALANCED"

    primary = None
    primary_ci = None
    if ti_ad:
        primary = permutation_test(
            blocks, left="A", right="D", replicates=PERMUTATIONS,
            seed=seed_from_contract(EXPERIMENT_ID, manifest_sha, "primary-A-D-permutation"))
        primary_ci = bootstrap_ci(
            ti_ad, replicates=BOOTSTRAPS,
            seed=seed_from_contract(EXPERIMENT_ID, manifest_sha, "primary-A-D-bootstrap"))

    ti_an = task_statistics(blocks, "A", "N")
    uptake = None
    uptake_ci = None
    if ti_an:
        uptake = permutation_test(
            blocks, left="A", right="N", replicates=PERMUTATIONS,
            seed=seed_from_contract(EXPERIMENT_ID, manifest_sha, "secondary-A-N-permutation"))
        uptake_ci = bootstrap_ci(
            ti_an, replicates=BOOTSTRAPS,
            seed=seed_from_contract(EXPERIMENT_ID, manifest_sha, "secondary-A-N-bootstrap"))

    high_ids = set(manifest["secondary"]["relevance_sensitivity"])
    high_blocks = {task: arms for task, arms in blocks.items() if task in high_ids}
    high_ti = task_statistics(high_blocks, "A", "D")
    high_analysis = None
    if high_ti:
        high_analysis = permutation_test(
            high_blocks, left="A", right="D", replicates=PERMUTATIONS,
            seed=seed_from_contract(EXPERIMENT_ID, manifest_sha,
                                    "high-relevance-A-D-permutation"))

    proportions = r4_proportions(receipts)
    r4_ad = r4_contrast(proportions, "A", "D", manifest_sha)
    r4_an = r4_contrast(proportions, "A", "N", manifest_sha)
    primary_supported = bool(
        not inference_held and primary
        and primary["observed_global_T"] > 0
        and primary["monte_carlo_p_value"] < .05)
    uptake_supported = bool(
        uptake and uptake["observed_global_T"] > 0
        and uptake["monte_carlo_p_value"] < .05)
    r4_detected = bool(
        r4_ad["decision"] == "R4_TASK_BLOCKED_ANALYSIS_COMPLETE"
        and r4_ad["permutation"]["two_sided_monte_carlo_p_value"] < .05)

    if insufficient:
        decision = "CONFIRMATORY_SCIENTIFIC_HOLD_INSUFFICIENT_COMPLETE_TASK_BLOCKS"
    elif missingness["decision"] == "MISSINGNESS_ARM_IMBALANCED":
        decision = "MISSINGNESS_ARM_IMBALANCED"
    elif (primary_supported
          and r4_ad["decision"] == "R4_TASK_BLOCKED_ANALYSIS_COMPLETE"
          and not r4_detected):
        decision = "BEHAVIORAL_PROPAGATION_WITH_TERMINAL_ATTENUATION"
    elif primary_supported:
        decision = "REPRESENTATION_BOUNDARY_PROPAGATES_TO_BEHAVIOR_DISTRIBUTION"
    else:
        decision = (
            "REPRESENTATION_BOUNDARY_LOCALIZED_AT_MODEL_VISIBLE_STATE;"
            "NO_QUALIFIED_BEHAVIORAL_SEPARATION_UNDER_TESTED_BACKEND")

    relevance = {
        task: float(manifest["per_task_frozen_state"][task]["retrieval"]["top1_relevance"])
        for task in manifest["evaluation_population"]["task_ids"]
    }
    receipt_hashes = [{
        "ordinal": unit["ordinal"], "run_id": unit["run_id"],
        "sha256": sha256_file(receipt_path(RECEIPT_DIR, unit))}
        for unit in schedule["units"]]
    artifacts = [str(MANIFEST.relative_to(ROOT)), str(SCHEDULE.relative_to(ROOT)),
                 str(INDEX.relative_to(ROOT))]
    payload = {
        "schema_version": 1, "experiment_id": EXPERIMENT_ID,
        "stage": "QWEN_CONFIRMATORY_SCIENTIFIC_ADJUDICATION",
        "created_at_utc": utcnow(), "decision": decision,
        "input_hashes": {
            "manifest": manifest_sha, "schedule": sha256_file(SCHEDULE),
            "resource_authority": sha256_file(AUTHORITY),
            "structural": sha256_file(STRUCTURAL), "execution_index": sha256_file(INDEX),
        },
        "execution_integrity": {
            "planned": 432, "completed": len(receipts), "journal_records": index["journal_record_count"],
            "attempt_count_values": sorted(set(row["attempt_count"] for row in receipts)),
            "automatic_retries": sum(bool(row.get("automatic_retry")) for row in receipts),
            "replacements": sum(bool(row.get("replacement")) for row in receipts),
            "receipt_hashes": receipt_hashes,
        },
        "structural": {
            "task_count": len(manifest["evaluation_population"]["task_ids"]),
            "A_B_E_exact_R1_equal_count": sum(
                structural["structural_receipts"][task]["checks"]["A_B_E_sha256_equal"]
                for task in manifest["evaluation_population"]["task_ids"]),
            "D_R1_differs_A_count": sum(
                structural["structural_receipts"][task]["checks"]["D_sha256_differs_from_A"]
                for task in manifest["evaluation_population"]["task_ids"]),
        },
        "valid_counts_by_task_arm": counts, "missingness_by_arm": failures,
        "missingness_gate": missingness, "N_analyzable_AD": analyzable,
        "primary_A_vs_D": {
            "inference_held": inference_held, "permutation": primary,
            "task_bootstrap_CI": primary_ci,
        },
        "secondary_A_vs_N": {
            "uptake_supported": uptake_supported, "permutation": uptake,
            "task_bootstrap_CI": uptake_ci,
        },
        "R2": r2_summary(receipts), "R3": r3_summary(receipts),
        "R4": {
            "per_task_resolution_proportions": proportions,
            "A_vs_D": r4_ad, "A_vs_N": r4_an,
            "terminal_difference_detected": r4_detected,
        },
        "relevance_sensitivity": {
            "frozen_task_ids": sorted(high_ids), "A_vs_D": high_analysis,
            "exploratory_spearman_top1_relevance_vs_T_AD": spearman(
                [(relevance[task], value) for task, value in ti_ad.items()]),
            "exploratory_spearman_top1_relevance_vs_T_AN": spearman(
                [(relevance[task], value) for task, value in ti_an.items()]),
        },
        "POWER_LIMITED": manifest["power"]["POWER_LIMITED"],
        "MDE80": manifest["power"]["MDE80"],
        "scientific_adjudication": {
            "primary_behavioral_propagation_supported": primary_supported,
            "memory_behavioral_uptake_supported": uptake_supported,
            "R3_does_not_require_R4_difference": True,
            "strongest_supported_claim": (
                "Under the frozen Qwen-generated ReasoningBank and qwen3-coder-next backend, "
                "cross-case partitioning shifted edit-target behavior beyond same-state "
                "stochastic dispersion." if primary_supported else
                "The representation boundary reached exact model-visible state, but no qualified "
                "behavioral distribution separation was established under the tested backend."
            ),
            "bounded_null_wording": (
                "no detectable behavioral distribution shift larger than the qualified precision range"
                if manifest["power"]["POWER_LIMITED"] else
                "no qualified behavioral distribution separation under the tested backend"
            ),
            "prohibited_claims": manifest["claim_boundary"]["prohibited"],
        },
        "failure_differential": (
            failure_differential(decision, artifacts) if inference_held else None),
        "claim_boundary": manifest["claim_boundary"],
        "credential_material_present": False,
    }
    return {"decision": decision, "file_sha256": write_json(output, payload),
            "N_analyzable_AD": analyzable,
            "primary_p": None if primary is None else primary["monte_carlo_p_value"]}


def main() -> None:
    print(json.dumps(adjudicate(), sort_keys=True))


if __name__ == "__main__":
    main()
