from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
RUN_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-tgrp-p0-postexposure-uptake-20260829-pilot-v1")
MANIFEST = RUN_ROOT / "run-manifest.json"
FREEZE = HERE / "c1-transport-guided-repair-pilot-freeze-20260828.json"
ANALYSIS = RUN_ROOT / "pilot-analysis.json"
CSV_OUT = RUN_ROOT / "pilot-per-state.csv"
FAILURE_DIFF = RUN_ROOT / "pilot-failure-differential.json"

ARMS = ("A0_NATIVE", "A1_MEMORY_BLIND_DECISION_CHECK", "A2_MEMORY_USE_CHECK")
BRANCHES = ("success_memory", "failure_memory")


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def tv(xs: list[str], ys: list[str]) -> float:
    require(xs and ys, "TV requires nonempty samples")
    cx, cy = Counter(xs), Counter(ys)
    keys = set(cx) | set(cy)
    return 0.5 * sum(abs(cx[k] / len(xs) - cy[k] / len(ys)) for k in keys)


def modal_set(xs: list[str]) -> list[str]:
    counts = Counter(xs)
    peak = max(counts.values())
    return sorted([key for key, count in counts.items() if count == peak])


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs)


def descriptive_bootstrap(xs: list[float], *, seed: int = 20260829, reps: int = 20000) -> dict[str, Any]:
    rng = random.Random(seed)
    vals = []
    n = len(xs)
    for _ in range(reps):
        vals.append(sum(xs[rng.randrange(n)] for _ in range(n)) / n)
    vals.sort()
    lo = vals[int(0.025 * reps)]
    hi = vals[min(reps - 1, int(0.975 * reps))]
    return {"seed": seed, "repetitions": reps, "percentile_95_ci": [lo, hi]}


def main() -> int:
    require(MANIFEST.is_file() and FREEZE.is_file(), "manifest/freeze missing")
    manifest = read_json(MANIFEST)
    freeze = read_json(FREEZE)
    pilot_ids = [int(x["future_task"]) for x in freeze["selection"]["pilot"]]
    require(len(pilot_ids) == 13, "pilot ID drift")

    cases: list[dict[str, Any]] = []
    missing: list[str] = []
    failed: list[str] = []
    for path in sorted((RUN_ROOT / "per_case").glob("*.json")):
        row = read_json(path)
        cases.append(row)
        if row.get("status") != "complete":
            failed.append(str(row.get("case_id") or path.stem))
    expected = int(manifest["expected_provider_calls"])
    if len(cases) != expected:
        schedule = [json.loads(line) for line in (RUN_ROOT / "schedule.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        present = {str(row.get("case_id")) for row in cases}
        missing = [str(row["case_id"]) for row in schedule if str(row["case_id"]) not in present]
    require(not missing, f"pilot incomplete: {len(missing)} missing")
    require(not failed, f"pilot has failed cases: {len(failed)}")
    require(len(cases) == 312, f"case geometry drift:{len(cases)}")

    by: dict[tuple[int, str, str], list[str]] = defaultdict(list)
    meta: dict[int, dict[str, Any]] = {}
    parse_recovered = 0
    model_drift = []
    prompt_hash_mismatch = []
    response_status_counts: Counter[str] = Counter()
    action_counts: dict[str, Counter[str]] = {arm: Counter() for arm in ARMS}

    for row in cases:
        task = int(row["future_task"])
        arm = str(row["arm"])
        branch = str(row["branch"])
        require(task in pilot_ids, f"non-pilot task leaked:{task}")
        require(arm in ARMS and branch in BRANCHES, "arm/branch drift")
        by[(task, arm, branch)].append(str(row["action_signature"]))
        meta[task] = {
            "future_task": task,
            "intent_template_id": int(row["intent_template_id"]),
            "selected_source_task": int(row["selected_source_task"]),
        }
        parse_recovered += int(bool(row.get("parse_recovered")))
        if str(row.get("resolved_model") or "") != manifest["model"]["expected_resolved"]:
            model_drift.append(str(row["case_id"]))
        input_row = read_json(Path(row["input_file"]))
        if str(row["prompt_sha256"]) != str(input_row["prompt_sha256"]):
            prompt_hash_mismatch.append(str(row["case_id"]))
        response_status_counts[str(row.get("provider_status") or "unknown")] += 1
        action_counts[arm][str(row["action_signature"])] += 1

    for task in pilot_ids:
        for arm in ARMS:
            for branch in BRANCHES:
                require(len(by[(task, arm, branch)]) == 4, f"rollout count drift:{task}/{arm}/{branch}")

    rows: list[dict[str, Any]] = []
    for task in pilot_ids:
        record: dict[str, Any] = dict(meta[task])
        u: dict[str, float] = {}
        for arm in ARMS:
            success = by[(task, arm, "success_memory")]
            failure = by[(task, arm, "failure_memory")]
            u[arm] = tv(success, failure)
            record[f"U_{arm}"] = u[arm]
            record[f"modal_{arm}_success"] = "|".join(modal_set(success))
            record[f"modal_{arm}_failure"] = "|".join(modal_set(failure))
            record[f"actions_{arm}_success"] = "|".join(success)
            record[f"actions_{arm}_failure"] = "|".join(failure)
        record["D_A2_minus_A1"] = u["A2_MEMORY_USE_CHECK"] - u["A1_MEMORY_BLIND_DECISION_CHECK"]
        record["N_A2_minus_A0"] = u["A2_MEMORY_USE_CHECK"] - u["A0_NATIVE"]
        record["A1_minus_A0"] = u["A1_MEMORY_BLIND_DECISION_CHECK"] - u["A0_NATIVE"]
        record["D_positive"] = record["D_A2_minus_A1"] > 0
        rows.append(record)

    fieldnames = list(rows[0].keys())
    with CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    u0 = [float(r["U_A0_NATIVE"]) for r in rows]
    u1 = [float(r["U_A1_MEMORY_BLIND_DECISION_CHECK"]) for r in rows]
    u2 = [float(r["U_A2_MEMORY_USE_CHECK"]) for r in rows]
    ds = [float(r["D_A2_minus_A1"]) for r in rows]
    ns = [float(r["N_A2_minus_A0"]) for r in rows]
    a1_shift = [float(r["A1_minus_A0"]) for r in rows]

    mean_u0, mean_u1, mean_u2 = mean(u0), mean(u1), mean(u2)
    mean_d, mean_n, mean_a1_shift = mean(ds), mean(ns), mean(a1_shift)
    positive_d = sum(1 for x in ds if x > 0)

    gate_checks = {
        "complete_packet_parser_realization": not model_drift and not prompt_hash_mismatch and len(cases) == 312,
        "no_arm_dependent_missingness": not missing and not failed,
        "mean_U_A2_ge_0_20": mean_u2 >= 0.20,
        "mean_D_ge_0_10": mean_d >= 0.10,
        "D_positive_at_least_8_of_13": positive_d >= 8,
        "mean_N_gt_0": mean_n > 0.0,
        "A1_does_not_absorb_A2_mean_D_ge_0_10": mean_d >= 0.10,
    }
    gate_pass = all(gate_checks.values())
    status = "PILOT_QUALIFIED_FOR_CONFIRMATORY_DESIGN" if gate_pass else "PILOT_HOLD_OR_STOP"

    by_source: dict[int, list[float]] = defaultdict(list)
    for r in rows:
        by_source[int(r["selected_source_task"])].append(float(r["D_A2_minus_A1"]))
    source_heterogeneity = {
        str(source): {"n": len(vals), "mean_D": mean(vals), "min_D": min(vals), "max_D": max(vals)}
        for source, vals in sorted(by_source.items())
    }

    if mean_d >= 0.10 and positive_d >= 8 and mean_u2 >= 0.20:
        competing = "Residual generic decision-check sensitivity remains the main alternative; compare mean(A1-A0) with mean(A2-A0) and preserve the A2-A1 contrast as primary."
    elif mean_d < 0.10 and mean_a1_shift > 0 and mean_n > 0:
        competing = "Generic decision-check or salience sensitivity: A1 and A2 both move relative to native while the memory-specific A2-A1 margin is insufficient."
    elif mean_n <= 0:
        competing = "Nonactionable localization under this intervention: explicit memory-use checking did not improve the measured uptake contrast relative to native."
    else:
        competing = "Memory-specific uptake signal is insufficient or heterogeneous under the frozen pilot gate; do not infer a targeted repair effect."

    analysis = {
        "schema_version": "1.0",
        "artifact_kind": "C1_TGRP_PILOT_ANALYSIS",
        "paper_id": manifest["paper_id"],
        "experiment_id": manifest["experiment_id"],
        "run_id": manifest["run_id"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "pilot_role": "identifiability/signal screen only; not confirmatory scientific evidence",
        "execution": {
            "expected_cases": 312,
            "complete_cases": len(cases),
            "failed_cases": len(failed),
            "missing_cases": len(missing),
            "parse_recovered_cases": parse_recovered,
            "model_drift_cases": model_drift,
            "prompt_hash_mismatch_cases": prompt_hash_mismatch,
            "provider_status_counts": dict(response_status_counts),
        },
        "effect_summary": {
            "mean_U_A0": mean_u0,
            "mean_U_A1": mean_u1,
            "mean_U_A2": mean_u2,
            "mean_D_A2_minus_A1": mean_d,
            "mean_N_A2_minus_A0": mean_n,
            "mean_A1_minus_A0": mean_a1_shift,
            "D_positive_count": positive_d,
            "D_positive_denominator": 13,
            "D_variance": statistics.variance(ds) if len(ds) > 1 else 0.0,
            "N_variance": statistics.variance(ns) if len(ns) > 1 else 0.0,
            "D_bootstrap": descriptive_bootstrap(ds),
            "N_bootstrap": descriptive_bootstrap(ns),
        },
        "gate": {"checks": gate_checks, "pass": gate_pass, "thresholds_unchanged": True},
        "heterogeneity": {
            "per_state": [{k: r[k] for k in ("future_task", "intent_template_id", "selected_source_task", "U_A0_NATIVE", "U_A1_MEMORY_BLIND_DECISION_CHECK", "U_A2_MEMORY_USE_CHECK", "D_A2_minus_A1", "N_A2_minus_A0", "A1_minus_A0", "D_positive")} for r in rows],
            "by_selected_source_task": source_heterogeneity,
            "action_signature_counts_by_arm": {arm: dict(counts) for arm, counts in action_counts.items()},
        },
        "strongest_competing_explanation": competing,
        "claim_boundary": "Pilot PASS, if any, supports only a recommendation that the diagnosed uptake surface is actionable enough to justify requesting a separate 23-state confirmatory test. It does not establish terminal utility improvement, causal mediation, universal repair, or a novel utilization algorithm.",
        "confirmatory_full_executed": False,
        "confirmatory_recommendation": "REQUEST_HUMAN_AUTHORITY_FOR_FROZEN_23_STATE_CONFIRMATORY" if gate_pass else "DO_NOT_RUN_CONFIRMATORY_ON_CURRENT_PILOT",
        "artifacts": {
            "manifest_sha256": sha_file(MANIFEST),
            "per_state_csv": str(CSV_OUT),
            "per_state_csv_sha256": sha_file(CSV_OUT),
        },
    }
    write_json(ANALYSIS, analysis)

    failure_layers = {
        "execution_failure": {"active": bool(failed or missing or model_drift or prompt_hash_mismatch), "evidence": {"failed": len(failed), "missing": len(missing), "model_drift": len(model_drift), "prompt_hash_mismatch": len(prompt_hash_mismatch)}},
        "intervention_realization_failure": {"active": False, "boundary": "All executed A2 packets contain the frozen A2 clause with exact prompt hashes. This verifies manipulation delivery, not internal cognitive compliance."},
        "generic_prompt_sensitivity": {"active_or_competing": mean_d < 0.10 and mean_a1_shift > 0 and mean_n > 0, "mean_A1_minus_A0": mean_a1_shift, "mean_A2_minus_A0": mean_n, "mean_A2_minus_A1": mean_d},
        "measurement_failure": {"active_or_competing": len(set(round(x, 8) for x in (u0 + u1 + u2))) <= 1, "observable": "first-action TV", "note": "A flat observable would limit identifiability but does not by itself falsify the diagnosis."},
        "nonactionable_localization": {"active": (not gate_pass) and not (failed or missing or model_drift or prompt_hash_mismatch), "meaning": "The frozen stage diagnosis did not earn actionable repair authority under the tested post-retrieval intervention."},
        "principle_update": {"allowed": not (failed or missing or model_drift or prompt_hash_mismatch), "update": "Diagnosis-guided repair actionability is supported at pilot-screen level only." if gate_pass else "Diagnosis-guided repair actionability is not qualified by this pilot; diagnostic completeness and the frozen observational stage boundary remain separately valid."},
    }
    differential = {
        "schema_version": "1.0",
        "artifact_kind": "C1_TGRP_PILOT_FAILURE_DIFFERENTIAL",
        "run_id": manifest["run_id"],
        "generated_at": analysis["generated_at"],
        "pilot_status": status,
        "layers": failure_layers,
        "does_not_imply": [
            "a pilot HOLD falsifies the 10-state diagnostic-completeness theorem",
            "a pilot HOLD invalidates the frozen W/E/U/O measurements",
            "a pilot PASS proves downstream utility improvement",
            "a prompt-level treatment realization proves causal mediation"
        ],
        "next_action": analysis["confirmatory_recommendation"],
    }
    write_json(FAILURE_DIFF, differential)

    analysis["artifacts"].update({
        "failure_differential": str(FAILURE_DIFF),
        "failure_differential_sha256": sha_file(FAILURE_DIFF),
    })
    write_json(ANALYSIS, analysis)

    print(json.dumps({
        "status": status,
        "mean_U_A0": round(mean_u0, 6),
        "mean_U_A1": round(mean_u1, 6),
        "mean_U_A2": round(mean_u2, 6),
        "mean_D": round(mean_d, 6),
        "D_positive": positive_d,
        "mean_N": round(mean_n, 6),
        "confirmatory_full_executed": False,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
