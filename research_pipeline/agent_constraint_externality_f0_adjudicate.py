from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_f0_execute import (
    ARMS,
    F0_FAMILIES,
    enumerate_probe_units,
)
from research_pipeline.agent_constraint_externality_runner_core import (
    OBJECT_ID,
    AppendOnlyLedger,
    RunnerError,
    sha256_file,
    sha256_value,
)

PRIMARY_THRESHOLD = 0.05
ORDERED_FAMILY_FRACTION = 2 / 3


def _mean(values: list[float]) -> float:
    if not values:
        raise RunnerError("Cannot aggregate an empty metric.")
    return statistics.fmean(values)


def _terminal_results(
    ledger: AppendOnlyLedger, eligible: list[str]
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    units = enumerate_probe_units(eligible)
    ledger.assert_all_terminal(units)
    results: dict[str, dict[str, Any]] = {}
    failures: list[str] = []
    for row in ledger.rows():
        if row["event"] == "COMPLETION":
            results[row["unit_id"]] = row["result"]["evaluation"]
        elif row["event"] == "FAILURE":
            failures.append(row["unit_id"])
    expected = {unit.unit_id for unit in units}
    if set(results) | set(failures) != expected:
        raise RunnerError("Ledger terminal set differs from frozen scheduled units.")
    return results, failures


def compute_metrics(
    ledger: AppendOnlyLedger, eligible: list[str]
) -> dict[str, Any]:
    results, failures = _terminal_results(ledger, eligible)
    if failures:
        return {
            "aggregate_unlocked": True,
            "retained_failure_units": failures,
            "metrics_available": False,
        }
    units = enumerate_probe_units(eligible)
    by_key = {tuple(unit.key): results[unit.unit_id] for unit in units}
    family_arm: dict[str, dict[str, dict[str, float]]] = defaultdict(dict)
    family_target_gains: dict[str, float] = {}
    for family_id in eligible:
        arm_target_gains: list[float] = []
        for arm in ARMS:
            trgs: list[float] = []
            crr_update: list[float] = []
            crr_no_update: list[float] = []
            for seed in (1201, 1202, 1203):
                no_update = by_key[(family_id, arm, "NO_UPDATE", seed)]
                update = by_key[(family_id, arm, "UPDATE", seed)]
                no_target = _mean([float(value) for value in no_update["target"].values()])
                up_target = _mean([float(value) for value in update["target"].values()])
                trgs.append(up_target - no_target)
                baseline_ids = set(no_update["non_target"])
                if baseline_ids != set(update["non_target"]):
                    raise RunnerError("Paired non-target evaluator IDs drifted.")
                crr_no_update.append(_mean([
                    float(not no_update["non_target"][constraint_id])
                    for constraint_id in baseline_ids
                ]))
                crr_update.append(_mean([
                    float(not update["non_target"][constraint_id])
                    for constraint_id in baseline_ids
                ]))
            crr_no = _mean(crr_no_update)
            crr_up = _mean(crr_update)
            trg = _mean(trgs)
            family_arm[family_id][arm] = {
                "trg": trg,
                "crr_no_update": crr_no,
                "crr_update": crr_up,
                "ue": crr_up - crr_no,
            }
            arm_target_gains.append(trg)
        family_target_gains[family_id] = _mean(arm_target_gains)
    primary_by_family = {
        family_id: family_arm[family_id]["HIGH"]["ue"]
        - family_arm[family_id]["INDEPENDENT"]["ue"]
        for family_id in eligible
    }
    low_contrast = {
        family_id: family_arm[family_id]["LOW"]["ue"]
        - family_arm[family_id]["INDEPENDENT"]["ue"]
        for family_id in eligible
    }
    high_low = {
        family_id: family_arm[family_id]["HIGH"]["ue"]
        - family_arm[family_id]["LOW"]["ue"]
        for family_id in eligible
    }
    ordered = {
        family_id: (
            family_arm[family_id]["INDEPENDENT"]["ue"]
            <= family_arm[family_id]["LOW"]["ue"]
            <= family_arm[family_id]["HIGH"]["ue"]
        )
        for family_id in eligible
    }
    no_update_arm_means = {
        arm: _mean([
            family_arm[family_id][arm]["crr_no_update"] for family_id in eligible
        ])
        for arm in ARMS
    }
    loo_primary = {
        omitted: _mean([
            value for family_id, value in primary_by_family.items() if family_id != omitted
        ])
        for omitted in eligible
    }
    return {
        "aggregate_unlocked": True,
        "retained_failure_units": [],
        "metrics_available": True,
        "eligible_family_count": len(eligible),
        "family_arm_metrics": family_arm,
        "family_target_repair_gain": family_target_gains,
        "mean_target_repair_gain": _mean(list(family_target_gains.values())),
        "primary_ue_high_minus_independent_by_family": primary_by_family,
        "mean_primary_ue_high_minus_independent": _mean(list(primary_by_family.values())),
        "secondary_mean_ue_low_minus_independent": _mean(list(low_contrast.values())),
        "secondary_mean_ue_high_minus_low": _mean(list(high_low.values())),
        "ordered_direction_by_family": ordered,
        "ordered_direction_fraction": _mean([float(value) for value in ordered.values()]),
        "no_update_crr_by_arm": no_update_arm_means,
        "no_update_drift_arm_range": max(no_update_arm_means.values())
        - min(no_update_arm_means.values()),
        "leave_one_family_out_primary": loo_primary,
    }


def adjudicate(metrics: dict[str, Any], *, compiler_controls: dict[str, bool]) -> str:
    if not metrics["metrics_available"]:
        return "F0_INCONCLUSIVE_STOP"
    if metrics["eligible_family_count"] < 6 or metrics["mean_target_repair_gain"] <= 0:
        return "F0_UPDATE_UPTAKE_FAIL"
    primary = metrics["mean_primary_ue_high_minus_independent"]
    ordered = metrics["ordered_direction_fraction"] >= ORDERED_FAMILY_FRACTION
    controls_pass = all(compiler_controls.values())
    no_update_ok = metrics["no_update_drift_arm_range"] <= PRIMARY_THRESHOLD
    outlier_ok = min(metrics["leave_one_family_out_primary"].values()) > 0
    if (
        primary >= PRIMARY_THRESHOLD
        and ordered
        and controls_pass
        and no_update_ok
        and outlier_ok
    ):
        return "F0_MECHANISM_SUPPORT"
    if primary <= 0 and not ordered:
        return "F0_MECHANISM_NOT_SUPPORTED"
    return "F0_INCONCLUSIVE_STOP"


def build_adjudication(
    *,
    ledger_path: Path,
    repairs_manifest_path: Path,
    compiler_qualification_path: Path,
) -> dict[str, Any]:
    repairs = json.loads(repairs_manifest_path.read_text(encoding="utf-8"))
    eligible = list(repairs["eligible_families"])
    if len(eligible) < 6:
        return {
            "schema_version": "ace-f0-adjudication-v1",
            "object_id": OBJECT_ID,
            "verdict": "F0_UPDATE_UPTAKE_FAIL",
            "mandatory_stop": True,
            "eligible_family_count": len(eligible),
            "metrics": None,
        }
    compiler = json.loads(compiler_qualification_path.read_text(encoding="utf-8"))
    metrics = compute_metrics(AppendOnlyLedger(ledger_path), eligible)
    controls = {
        "constraint_count_matched": bool(
            compiler.get("global_checks", {}).get("constraint_count_matched", True)
        ),
        "obvious_difficulty_mismatch_absent": bool(
            compiler.get("global_checks", {}).get("instruction_matching", True)
        ),
    }
    verdict = adjudicate(metrics, compiler_controls=controls)
    result = {
        "schema_version": "ace-f0-adjudication-v1",
        "object_id": OBJECT_ID,
        "verdict": verdict,
        "mandatory_stop": True,
        "thresholds": {
            "eligible_family_min": 6,
            "mean_target_repair_gain_strictly_greater_than": 0,
            "primary_ue_high_minus_independent_min": PRIMARY_THRESHOLD,
            "ordered_direction_family_fraction_min": ORDERED_FAMILY_FRACTION,
        },
        "controls": controls,
        "metrics": metrics,
        "significance_claim": False,
        "further_execution_authority": False,
    }
    result["content_sha256"] = sha256_value(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--repairs-manifest", type=Path, required=True)
    parser.add_argument("--compiler-qualification", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build_adjudication(
        ledger_path=args.ledger,
        repairs_manifest_path=args.repairs_manifest,
        compiler_qualification_path=args.compiler_qualification,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "object_id": OBJECT_ID,
        "verdict": result["verdict"],
        "mandatory_stop": True,
        "output_sha256": sha256_file(args.output),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
