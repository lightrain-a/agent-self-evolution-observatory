"""Outcome-blind Full-P1 integrity adjudication and paired R0-R4 analysis."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from scipy.stats import beta, binomtest

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT,
    canonical_json,
    sha256_file,
    sha256_text,
    utcnow,
    write_json,
)

INDEX = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-index-20260831.json"
PREREGISTRATION = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-behavioral-propagation-preregistration-20260831.json"
AUTHORITY = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-execution-authority-20260831.json"
OUTPUT = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-adjudication-20260831.json"
MANIFEST = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-artifact-manifest-20260831.json"
MEMORY = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-scientific-memory-20260831.json"
ARMS = ("A", "B", "C", "D", "E")
CONTRASTS = {
    "A_vs_B": {"arms": ("A", "B"), "designation": "primary", "theory": "native within-case reunion robustness"},
    "A_vs_D": {"arms": ("A", "D"), "designation": "primary", "theory": "cross-case partition boundary"},
    "A_vs_E": {"arms": ("A", "E"), "designation": "secondary", "theory": "case-ID placebo"},
    "A_vs_C": {"arms": ("A", "C"), "designation": "secondary", "theory": "order-sensitivity boundary probe"},
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def interval(successes: int, n: int, alpha: float = 0.05) -> list[float]:
    if n <= 0:
        return [0.0, 1.0]
    low = 0.0 if successes == 0 else float(beta.ppf(alpha / 2, successes, n - successes + 1))
    high = 1.0 if successes == n else float(beta.ppf(1 - alpha / 2, successes + 1, n - successes))
    return [low, high]


def r2_signature(run: dict[str, Any]) -> str:
    row = run.get("R2_first_behavior_action")
    if row is None:
        return sha256_text("null")
    stable = {
        key: row.get(key)
        for key in (
            "step",
            "type",
            "action",
            "candidate_action_count",
            "assistant_output_empty",
            "returncode",
            "timed_out",
            "submission_marker",
        )
        if key in row
    }
    return sha256_text(canonical_json(stable))


def r3_signature(run: dict[str, Any]) -> str:
    actions = []
    for row in run.get("R3_actions", []):
        actions.append({
            key: row.get(key)
            for key in (
                "step",
                "type",
                "action",
                "candidate_action_count",
                "assistant_output_empty",
                "returncode",
                "timed_out",
                "raw_output",
                "model_visible_observation",
                "submission_marker",
            )
            if key in row
        })
    stable = {
        "actions": actions,
        "patch_and_status": (run.get("patch_and_status") or {}).get("output"),
        "exit_status": run.get("exit_status"),
    }
    return sha256_text(canonical_json(stable))


def exact_r4(a_values: list[bool], b_values: list[bool]) -> dict[str, Any]:
    a_only = sum(a and not b for a, b in zip(a_values, b_values))
    b_only = sum(b and not a for a, b in zip(a_values, b_values))
    discordant = a_only + b_only
    p = 1.0 if discordant == 0 else float(binomtest(a_only, discordant, 0.5).pvalue)
    differences = [int(a) - int(b) for a, b in zip(a_values, b_values)]
    return {
        "arm_a_resolved": sum(a_values),
        "arm_b_resolved": sum(b_values),
        "paired_rate_difference": sum(differences) / len(differences),
        "a_only": a_only,
        "b_only": b_only,
        "discordant_pairs": discordant,
        "exact_mcnemar_two_sided_pvalue": p,
    }


def holm(values: dict[str, float]) -> dict[str, float]:
    ordered = sorted(values, key=values.get)
    adjusted: dict[str, float] = {}
    running = 0.0
    m = len(ordered)
    for index, name in enumerate(ordered):
        candidate = min(1.0, values[name] * (m - index))
        running = max(running, candidate)
        adjusted[name] = running
    return adjusted


def stable_pair_analysis(
    runs: dict[tuple[str, str], dict[str, Any]]
) -> dict[str, Any]:
    instance_ids = sorted({instance_id for instance_id, _ in runs})
    output: dict[str, Any] = {}
    primary_p = {}
    for name, spec in CONTRASTS.items():
        arm_a, arm_b = spec["arms"]
        rows = [(runs[(instance_id, arm_a)], runs[(instance_id, arm_b)]) for instance_id in instance_ids]
        r1_equal = [
            a.get("R1_exact_model_visible_request_sha256")
            == b.get("R1_exact_model_visible_request_sha256")
            for a, b in rows
        ]
        r2_equal = [r2_signature(a) == r2_signature(b) for a, b in rows]
        r3_equal = [r3_signature(a) == r3_signature(b) for a, b in rows]
        a_r4 = [bool((a.get("R4_terminal_outcome") or {}).get("resolved")) for a, _ in rows]
        b_r4 = [bool((b.get("R4_terminal_outcome") or {}).get("resolved")) for _, b in rows]
        r4 = exact_r4(a_r4, b_r4)
        row = {
            "arms": [arm_a, arm_b],
            "designation": spec["designation"],
            "theory": spec["theory"],
            "pair_count": len(rows),
            "R1_exact_request_equal_count": sum(r1_equal),
            "R1_exact_request_equal_proportion": sum(r1_equal) / len(rows),
            "R2_first_action_divergence_count": len(rows) - sum(r2_equal),
            "R2_first_action_divergence_proportion": (len(rows) - sum(r2_equal)) / len(rows),
            "R2_divergence_95pct_clopper_pearson": interval(len(rows) - sum(r2_equal), len(rows)),
            "R3_trajectory_divergence_count": len(rows) - sum(r3_equal),
            "R3_trajectory_divergence_proportion": (len(rows) - sum(r3_equal)) / len(rows),
            "R3_divergence_95pct_clopper_pearson": interval(len(rows) - sum(r3_equal), len(rows)),
            "R4": r4,
            "localization_rule": "R2/R3 mechanism interpretation does not require an R4 difference",
        }
        output[name] = row
        if spec["designation"] == "primary":
            primary_p[name] = r4["exact_mcnemar_two_sided_pvalue"]
    adjusted = holm(primary_p)
    for name, value in adjusted.items():
        output[name]["R4"]["holm_adjusted_primary_pvalue"] = value
    return output


def adjudicate() -> dict[str, Any]:
    for path in (OUTPUT, MANIFEST, MEMORY):
        if path.exists():
            raise RuntimeError("refusing duplicate Full-P1 adjudication")
    index = load(INDEX)
    prereg = load(PREREGISTRATION)
    authority = load(AUTHORITY)
    completed = index.get("completed_runs", [])
    journal = index.get("run_journal", [])
    artifact_rows = []
    runs: dict[tuple[str, str], dict[str, Any]] = {}
    for receipt in completed:
        path = ROOT / receipt["path"]
        actual = sha256_file(path)
        artifact_rows.append({
            "path": receipt["path"],
            "expected_sha256": receipt["file_sha256"],
            "actual_sha256": actual,
            "hash_matches": actual == receipt["file_sha256"],
        })
        run = load(path)
        runs[(run["instance_id"], run["arm"])] = run
    planned_pairs = [
        (row["instance_id"], row["arm"])
        for row in prereg["execution_contract"]["journal_units"]
    ]
    journal_pairs = [(row["instance_id"], row["arm"]) for row in journal]
    completed_pairs = [(row["instance_id"], row["arm"]) for row in completed]
    run_pairs = list(runs)
    implementation_failures = [
        {
            "instance_id": run["instance_id"],
            "arm": run["arm"],
            "execution_status": run.get("execution_status"),
            "failure": run.get("failure"),
        }
        for run in runs.values()
        if run.get("execution_status") != "TERMINAL_PERSISTED"
        or run.get("failure") is not None
    ]
    invalid_evaluators = [
        {"instance_id": run["instance_id"], "arm": run["arm"]}
        for run in runs.values()
        if not (run.get("R4_terminal_outcome") or {}).get("valid")
    ]
    runtime_invalid = [
        {"instance_id": run["instance_id"], "arm": run["arm"]}
        for run in runs.values()
        if not (
            ((run.get("runtime") or {}).get("receipt") or {})
            .get("q10_start_reconciliation", {})
            .get("client_start_invocations") == 1
            and ((run.get("runtime") or {}).get("receipt") or {})
            .get("q10_start_reconciliation", {})
            .get("second_start_invoked") is False
            and (run.get("docker_cleanup_receipt") or {}).get("accepted") is True
        )
    ]
    checks = {
        "execution_authority_exact": (
            index["execution_authority_sha256"] == sha256_file(AUTHORITY)
            and authority["decision"] == "FULL_P1_BEHAVIORAL_EXECUTION_AUTHORIZED"
            and authority["execution_authorized"] is True
        ),
        "preregistration_exact": (
            index["preregistration_sha256"] == sha256_file(PREREGISTRATION)
            and prereg["execution_contract"]["unit_count"] == 40
        ),
        "execution_complete": index.get("execution_complete") is True,
        "counts_exact": len(journal) == len(completed) == len(runs) == 40,
        "frozen_order_preserved": journal_pairs == completed_pairs == planned_pairs and run_pairs == planned_pairs,
        "attempt_counts_exactly_one": (
            all(row.get("attempt_count") == 1 for row in journal)
            and all(row.get("attempt_count") == 1 for row in completed)
            and all(run.get("attempt_count") == 1 for run in runs.values())
        ),
        "every_journal_item_persisted": all(row.get("status") == "persisted" for row in journal),
        "all_run_hashes_match": all(row["hash_matches"] for row in artifact_rows),
        "no_replacement_no_retry": (
            index.get("automatic_retry") == "forbidden"
            and index.get("manual_retry") == "forbidden"
            and index.get("replacement_sampling") == "forbidden"
        ),
        "all_runtime_receipts_exact": not runtime_invalid,
        "all_evaluators_valid": not invalid_evaluators,
        "no_implementation_failures": not implementation_failures,
        "all_R1_R3_observables_present": all(
            run.get("R1_exact_model_visible_request_sha256")
            and run.get("R3_complete_trajectory_sha256")
            for run in runs.values()
        ),
        "credential_material_absent": all(
            run.get("credential_material_present") is False for run in runs.values()
        ),
    }
    integrity_pass = all(checks.values())
    analyses = stable_pair_analysis(runs) if integrity_pass else {}
    outcomes = [
        {
            "selection_rank": run["selection_rank"],
            "instance_id": run["instance_id"],
            "arm": run["arm"],
            "exit_status": run.get("exit_status"),
            "evaluator_valid": (run.get("R4_terminal_outcome") or {}).get("valid"),
            "resolved": (run.get("R4_terminal_outcome") or {}).get("resolved"),
            "model_calls": (run.get("resource_accounting") or {}).get("model_calls", 0),
        }
        for run in runs.values()
    ]
    outcomes.sort(key=lambda row: (row["selection_rank"], ARMS.index(row["arm"])))
    manifest_payload = {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-FULL-P1-ARTIFACT-MANIFEST-20260831",
        "created_at_utc": utcnow(),
        "index": str(INDEX.relative_to(ROOT)),
        "index_sha256": sha256_file(INDEX),
        "artifact_count": len(artifact_rows),
        "artifacts": artifact_rows,
        "all_artifacts_sha256_verified": all(row["hash_matches"] for row in artifact_rows),
        "credential_material_present": False,
    }
    manifest_sha = write_json(MANIFEST, manifest_payload)
    decision = (
        "FULL_P1_BEHAVIORAL_PROPAGATION_ADJUDICATED_BOUNDED_CLAIMS_AUTHORIZED"
        if integrity_pass
        else "FULL_P1_BEHAVIORAL_PROPAGATION_ADJUDICATION_HOLD"
    )
    adjudication_payload = {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-FULL-P1-ADJUDICATION-20260831",
        "created_at_utc": utcnow(),
        "decision": decision,
        "integrity_pass": integrity_pass,
        "checks": checks,
        "implementation_failures": implementation_failures,
        "runtime_invalid": runtime_invalid,
        "invalid_evaluators": invalid_evaluators,
        "descriptive_task_outcomes": outcomes,
        "paired_analyses": analyses,
        "artifact_manifest": str(MANIFEST.relative_to(ROOT)),
        "artifact_manifest_sha256": manifest_sha,
        "claim_boundary": {
            "population": "eight prospectively frozen unseen SWE-bench Verified tasks in Q10-qualified Django/Sphinx parser families",
            "primary_contrasts": ["A_vs_B", "A_vs_D"],
            "secondary_contrasts": ["A_vs_E", "A_vs_C"],
            "R2_R3_mechanism_does_not_require_R4_difference": True,
            "implementation_qualification_is_not_scientific_evidence": True,
            "negative_R4_outcomes_do_not_invalidate_implementation": True,
            "absence_of_significance_is_not_equivalence": True,
            "generalization_beyond_frozen_population_authorized": False,
            "paper_claim_authorized": integrity_pass,
        },
        "credential_material_present": False,
    }
    adjudication_sha = write_json(OUTPUT, adjudication_payload)
    memory_payload = {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-FULL-P1-SCIENTIFIC-MEMORY-20260831",
        "created_at_utc": utcnow(),
        "decision": "FULL_P1_SCIENTIFIC_MEMORY_DEPOSITED",
        "adjudication_sha256": adjudication_sha,
        "failure_differential_lesson": (
            "implementation/operationalization failure -> no scientific belief update "
            "-> prospective repaired qualification"
        ),
        "sequence": [
            "Q2 evidence preserved",
            "Q3 stopped before model outcome because its runtime base-state rule was overly strict",
            "Q3 therefore was not a mechanism negative",
            "Q4 was an outcome-blind implementation repair",
            "Q5-Q10 prospectively localized and repaired evaluator/runtime acknowledgement semantics without treatment redesign",
            "Full-P1 was separately preregistered and separately authorized only after qualification",
        ],
        "reuse_rule": (
            "When a run stops before a valid model-visible behavior or has invalid implementation/evaluation, "
            "classify the failure layer first; do not update the scientific mechanism belief from that run."
        ),
        "task_outcomes_preserved_descriptively": True,
        "credential_material_present": False,
    }
    memory_sha = write_json(MEMORY, memory_payload)
    return {
        "decision": decision,
        "integrity_pass": integrity_pass,
        "adjudication_sha256": adjudication_sha,
        "manifest_sha256": manifest_sha,
        "memory_sha256": memory_sha,
        "implementation_failure_count": len(implementation_failures),
    }


def main() -> None:
    print(json.dumps(adjudicate(), sort_keys=True))


if __name__ == "__main__":
    main()
