"""Freeze the outcome-blind Full-P1 behavioral propagation preregistration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    BASE_URL,
    COMMAND_TIMEOUT_SECONDS,
    EVALUATOR_TIMEOUT_SECONDS,
    MAX_RETRIES,
    MODEL,
    PID_NAMESPACE,
    ROOT,
    STEP_LIMIT,
    canonical_json,
    sha256_file,
    sha256_text,
    utcnow,
    write_json,
)

POPULATION = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-population-and-image-freeze-20260831.json"
SOURCE_MEMORY = ROOT / "generated/asset-first-stri-reasoningbank-p1-source-memory-20260829.json"
TREATMENTS = ROOT / "generated/asset-first-stri-reasoningbank-p1-treatment-manifest-20260829.json"
Q10_ADJUDICATION = ROOT / "generated/asset-first-stri-reasoningbank-p1-q10-adjudication-20260831.json"
OUTPUT = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-behavioral-propagation-preregistration-20260831.json"

EXPECTED = {
    POPULATION: None,
    SOURCE_MEMORY: "0451d0346ab5df749df6c1f1d1ea3abbcde3f913958149be9671fce1bfbf2239",
    TREATMENTS: "35b5f8dab0606ca930a237a6248c9b0aac8a5b6f5564e3ba57217a34dfd92ad7",
    Q10_ADJUDICATION: "a92d394ee90ee6d1b5c65ca3deb17c9311649757a1e053ed94cc7c025b0f89c9",
}
EXPECTED_RANKS = [7, 8, 9, 11, 12, 13, 14, 19]
EXPECTED_IDS = [
    "django__django-13809",
    "django__django-11740",
    "django__django-15315",
    "django__django-15731",
    "django__django-16454",
    "django__django-14787",
    "sphinx-doc__sphinx-9711",
    "django__django-15695",
]
ARM_ORDER = ["A", "B", "C", "D", "E"]
EXPECTED_MEMORY_HASHES = {
    "A": "2f0241f1b46019d0bcf72317ebe6ff0561ef2241370aff4d04683af392290041",
    "B": "2f0241f1b46019d0bcf72317ebe6ff0561ef2241370aff4d04683af392290041",
    "C": "cbd9014f1d5f4309799dc5c36ede30daa71e2d0f23b60e69c0b50be41a594c77",
    "D": "05f4afe0b61207313fec240a53d288af31d9e5d697a78b13bcce17372816f9bf",
    "E": "2f0241f1b46019d0bcf72317ebe6ff0561ef2241370aff4d04683af392290041",
}
EXPECTED_TREATMENT_HASHES = {
    "A": "6094b0bc5e6ea7c87da86d7cd60594e823ffb84b04a6592016c5154b3968752a",
    "B": "1dbf10edf2710e256968d01fa64edcbb7df65a3dd92ca5b4511232dcd1f01a00",
    "C": "04c815b16d2d0f5e863470390d7298657f3560385eea036f98b6fbe2539c4b43",
    "D": "047fa9e7d69af1d455ac465816ae84d5e7234166420a29f9e3ce3aacf0873083",
    "E": "b475629a1a9fdff39a3d32c5bcfe449f9cceeb226919355e2a7d32fc22d49196",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def preregister(output: Path = OUTPUT) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError("refusing to overwrite immutable Full-P1 preregistration")
    for path, expected in EXPECTED.items():
        if not path.exists():
            raise RuntimeError(f"missing prerequisite: {path}")
        if expected is not None and sha256_file(path) != expected:
            raise RuntimeError(f"prerequisite SHA drift: {path}")

    population_doc = read_json(POPULATION)
    treatments_doc = read_json(TREATMENTS)
    q10_doc = read_json(Q10_ADJUDICATION)
    population = population_doc.get("population", [])
    if population_doc.get("decision") != "FULL_P1_FRESH_POPULATION_AND_IMAGES_FROZEN":
        raise RuntimeError("Full-P1 population/image gate is not open")
    if q10_doc.get("decision") != (
        "P1_Q10_RUNTIME_RECONCILIATION_QUALIFIED_"
        "FULL_P1_PLANNING_GATE_OPEN_EXECUTION_UNAUTHORIZED"
    ):
        raise RuntimeError("Q10 did not open Full-P1 preregistration gate")
    if [row["selection_rank"] for row in population] != EXPECTED_RANKS:
        raise RuntimeError("Full-P1 population rank drift")
    if [row["instance_id"] for row in population] != EXPECTED_IDS:
        raise RuntimeError("Full-P1 population identity drift")
    arms = treatments_doc.get("arms", {})
    if list(sorted(arms)) != ARM_ORDER:
        raise RuntimeError("Full-P1 treatment arm drift")
    for arm in ARM_ORDER:
        if arms[arm]["R0"]["selected_memory_sha256"] != EXPECTED_MEMORY_HASHES[arm]:
            raise RuntimeError(f"selected-memory SHA drift for arm {arm}")
        if arms[arm]["treatment_sha256"] != EXPECTED_TREATMENT_HASHES[arm]:
            raise RuntimeError(f"treatment SHA drift for arm {arm}")

    units = [
        {
            "journal_index": index,
            "selection_rank": task["selection_rank"],
            "instance_id": task["instance_id"],
            "arm": arm,
            "run_id": f"full-p1-{task['instance_id']}-{arm}",
            "attempt_count": 1,
            "model_visible_task_sha256": task["model_visible_task_sha256"],
            "evaluator_fixture_sha256": task["evaluator_fixture_sha256"],
            "image_amd64_manifest_digest": task["image_amd64_manifest_digest"],
            "selected_memory_sha256": EXPECTED_MEMORY_HASHES[arm],
            "treatment_sha256": EXPECTED_TREATMENT_HASHES[arm],
        }
        for index, (task, arm) in enumerate(
            (task, arm) for task in population for arm in ARM_ORDER
        )
    ]

    payload = {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-FULL-P1-BEHAVIORAL-PROPAGATION-20260831",
        "created_at_utc": utcnow(),
        "decision": "FULL_P1_BEHAVIORAL_PROPAGATION_PREREGISTERED_EXECUTION_UNAUTHORIZED",
        "gate_provenance": {
            "q10_adjudication_path": str(Q10_ADJUDICATION.relative_to(ROOT)),
            "q10_adjudication_sha256": sha256_file(Q10_ADJUDICATION),
            "q10_decision": q10_doc["decision"],
            "interpretation": (
                "Q10 qualifies implementation/runtime only and opens planning; "
                "it is not behavioral evidence and does not authorize execution."
            ),
        },
        "evaluation_population": {
            "artifact_path": str(POPULATION.relative_to(ROOT)),
            "artifact_sha256": sha256_file(POPULATION),
            "dataset": population_doc["dataset"],
            "selection_rule": population_doc["selection_rule"],
            "task_count": 8,
            "selected_ranks": EXPECTED_RANKS,
            "selected_instance_ids": EXPECTED_IDS,
            "fresh_unseen_before_execution": True,
            "qualification_parser_families_only": ["parse_log_django", "parse_log_sphinx"],
            "no_replacement": True,
        },
        "treatments": {
            "arm_order": ARM_ORDER,
            "source_memory_artifact_path": str(SOURCE_MEMORY.relative_to(ROOT)),
            "source_memory_artifact_sha256": sha256_file(SOURCE_MEMORY),
            "treatment_manifest_path": str(TREATMENTS.relative_to(ROOT)),
            "treatment_manifest_sha256": sha256_file(TREATMENTS),
            "arms": {
                arm: {
                    "definition": {
                        "A": "native one-case reunited memory item",
                        "B": "same native case split into original semantic items",
                        "C": "same native case semantic items in reversed order",
                        "D": "cross-case partition with deterministic tied retrieval selecting partition 1",
                        "E": "case-ID placebo; same semantic evidence as B under changed case identity",
                    }[arm],
                    "selected_memory_sha256": EXPECTED_MEMORY_HASHES[arm],
                    "treatment_sha256": EXPECTED_TREATMENT_HASHES[arm],
                    "R0_sha256": sha256_text(canonical_json(arms[arm]["R0"])),
                }
                for arm in ARM_ORDER
            },
            "invariants": {
                "A_equals_B_model_visible_semantic_evidence": True,
                "B_equals_E_model_visible_semantic_evidence": True,
                "C_is_order_only_probe": True,
                "D_is_partition_boundary_probe": True,
                "no_redesign_from_q10_outcomes": True,
            },
        },
        "provider_and_sampling": {
            "provider": "Volcengine Ark plan v3",
            "base_url": BASE_URL,
            "model": MODEL,
            "temperature": 0.0,
            "store": True,
            "request_timeout_seconds": 120.0,
            "max_output_tokens": "omitted",
            "seed": "unsupported_and_omitted",
            "top_p": "omitted",
            "provider_transport_max_retries": MAX_RETRIES,
            "provider_retry_scope": (
                "client transport handling inside the single run only; never a run-level "
                "retry, treatment replay, or replacement sample"
            ),
            "step_limit": STEP_LIMIT,
            "command_timeout_seconds": COMMAND_TIMEOUT_SECONDS,
            "evaluator_timeout_seconds": EVALUATOR_TIMEOUT_SECONDS,
            "pid_namespace": PID_NAMESPACE,
        },
        "execution_contract": {
            "task_count": 8,
            "arm_count": 5,
            "unit_count": 40,
            "repeat_policy": "exactly one persisted run per frozen task-arm unit",
            "attempt_count_each": 1,
            "automatic_retry": False,
            "manual_retry": False,
            "replacement_sampling": False,
            "execution_order": "selection_rank ascending; within rank A,B,C,D,E",
            "journal_units": units,
            "stopping_rule": (
                "Stop only after exactly 40 terminal persisted units, or enter a "
                "documented external-substrate hold without replacing, retrying, "
                "or changing any task or arm. No outcome-dependent stopping."
            ),
            "docker_runtime": (
                "Q10 DaemonReconciledDockerRun: one docker start; ambiguous start "
                "acknowledgement may trigger read-only inspect reconciliation only; "
                "a second docker start is forbidden"
            ),
            "base_state_rule": "exact_or_clean_tree_equivalent_descendant",
            "failure_handling": {
                "task_or_model_failure": "persist descriptively as the unit outcome; continue frozen order",
                "provider_failure": "persist terminal provider failure; no rerun or replacement",
                "runtime_failure": "persist terminal runtime failure; no rerun or replacement",
                "evaluator_failure": "persist terminal evaluator failure; no rerun or replacement",
                "external_substrate_blocker": (
                    "freeze current artifacts and enter hold; require separate prospective "
                    "authority for any action, never reuse this execution authority"
                ),
            },
        },
        "observables": {
            "R0": "representation and deterministic retrieval state before request rendering",
            "R1": "exact model-visible request messages and their canonical SHA-256",
            "R2": "first parsed model behavior and first shell action",
            "R3": "complete model/tool trajectory, actions, edits, and trajectory SHA-256",
            "R4": "terminal official SWE-Bench evaluator outcome and evaluator receipt",
            "localization_rule": (
                "A valid R2 or R3 behavioral mechanism result does not require an R4 "
                "performance difference. R4 is downstream and reported separately."
            ),
        },
        "contrasts": {
            "primary": [
                {
                    "arms": ["A", "B"],
                    "name": "native within-case reunion robustness",
                    "levels": ["R2", "R3", "R4"],
                },
                {
                    "arms": ["A", "D"],
                    "name": "cross-case partition boundary",
                    "levels": ["R2", "R3", "R4"],
                },
            ],
            "secondary": [
                {
                    "arms": ["A", "E"],
                    "name": "case-ID placebo",
                    "levels": ["R2", "R3", "R4"],
                },
                {
                    "arms": ["A", "C"],
                    "name": "order-sensitivity boundary probe",
                    "levels": ["R2", "R3", "R4"],
                },
            ],
        },
        "paired_statistical_analysis": {
            "pairing_key": "instance_id",
            "estimands": {
                "R2": "paired exact first-action equality/divergence proportion",
                "R3": "paired exact trajectory/action/edit equality/divergence proportion",
                "R4": "paired difference in binary SWE-Bench resolution rate",
            },
            "intervals": "two-sided 95% exact Clopper-Pearson intervals for binomial proportions",
            "R4_test": (
                "two-sided exact McNemar test, equivalently a two-sided exact binomial "
                "test on discordant pairs; report discordant counts even when zero"
            ),
            "multiplicity": (
                "A-v-B and A-v-D are separately designated primary; report raw exact "
                "p-values and Holm-adjusted primary-family p-values. Secondary contrasts "
                "are descriptive/exploratory with raw exact p-values."
            ),
            "small_n_boundary": (
                "N=8 supports exact paired descriptive inference; effect sizes and exact "
                "intervals lead. Absence of significance is not evidence of equivalence."
            ),
        },
        "artifact_schema": {
            "index": [
                "execution_complete",
                "completed_count",
                "journal",
                "attempt_counts",
                "frozen_order_sha256",
                "execution_authority_sha256",
            ],
            "per_run": [
                "run_id",
                "instance_id",
                "selection_rank",
                "arm",
                "attempt_count",
                "R0",
                "R1",
                "R2",
                "R3",
                "R4",
                "provider_receipts",
                "docker_start_receipt",
                "docker_cleanup_receipt",
                "model_visible_task_sha256",
                "evaluator_fixture_sha256",
                "selected_memory_sha256",
                "image_amd64_manifest_digest",
                "failure_classification",
                "credential_material_present",
            ],
            "credential_material_present": False,
        },
        "claim_boundary": {
            "question": "Where and how frozen retrieval structure propagates from R0 through R4",
            "implementation_qualification_is_not_scientific_evidence": True,
            "negative_task_outcomes_do_not_retroactively_invalidate_implementation": True,
            "R2_R3_mechanism_does_not_require_R4_difference": True,
            "paper_claim_authorized": False,
            "behavioral_execution_authorized": False,
        },
        "checks": {
            "population_exact": len(population) == 8,
            "unit_count_exact": len(units) == 40,
            "order_exact": [row["journal_index"] for row in units] == list(range(40)),
            "all_attempt_counts_one": all(row["attempt_count"] == 1 for row in units),
            "all_task_hashes_frozen": all(row["model_visible_task_sha256"] for row in units),
            "all_evaluator_hashes_frozen": all(row["evaluator_fixture_sha256"] for row in units),
            "all_image_digests_frozen": all(
                row["image_amd64_manifest_digest"].startswith("sha256:") for row in units
            ),
            "all_semantic_hashes_frozen": all(row["selected_memory_sha256"] for row in units),
            "no_replacement": True,
            "no_run_level_retry": True,
            "task_outcomes_unobserved": True,
            "execution_unauthorized": True,
        },
        "credential_material_present": False,
    }
    if not all(payload["checks"].values()):
        raise RuntimeError("Full-P1 preregistration invariant failed")
    return {
        "decision": payload["decision"],
        "file_sha256": write_json(output, payload),
        "unit_count": len(units),
    }


def main() -> None:
    print(json.dumps(preregister(), sort_keys=True))


if __name__ == "__main__":
    main()
