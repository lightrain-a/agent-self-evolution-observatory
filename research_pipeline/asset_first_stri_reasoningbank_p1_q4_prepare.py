"""Preregister the outcome-blind Q4 exact-base normalization qualification."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    BASE_URL,
    COMMAND_TIMEOUT_SECONDS,
    MAX_RETRIES,
    MODEL,
    OFFICIAL_COMMIT,
    PID_NAMESPACE,
    ROOT,
    STEP_LIMIT,
    sha256_file,
    utcnow,
    write_json,
)

Q3_FIXTURES = ROOT / "generated/asset-first-stri-reasoningbank-p1-q3-task-fixtures-20260830.json"
Q3_CONTRACT = ROOT / "generated/asset-first-stri-reasoningbank-p1-q3-qualification-contract-20260830.json"
Q3_PARSER_QUALIFICATION = ROOT / "generated/asset-first-stri-reasoningbank-p1-q3-parser-qualification-20260830.json"
Q3_ACQUISITION = ROOT / "generated/asset-first-stri-reasoningbank-p1-q3-runtime-acquisition-result-20260830.json"
Q3_RUNTIME_HOLD = ROOT / "generated/asset-first-stri-reasoningbank-p1-q3-runtime-qualification-result-20260830.json"
Q3_INDEX = ROOT / "generated/asset-first-stri-reasoningbank-p1-q3-index-20260830.json"
Q3_RUN_DIR = ROOT / "generated/asset-first-stri-reasoningbank-p1-q3-runs-20260830"
TREATMENTS = ROOT / "generated/asset-first-stri-reasoningbank-p1-treatment-manifest-20260829.json"
SOURCE_MEMORY = ROOT / "generated/asset-first-stri-reasoningbank-p1-source-memory-20260829.json"
CONTRACT = ROOT / "generated/asset-first-stri-reasoningbank-p1-q4-base-normalization-contract-20260830.json"

EXPECTED_HASHES = {
    Q3_FIXTURES: "b35c9b7a798b371818b25774c129d77c74f7dc90217b3f54f7e4e1d474d15519",
    Q3_CONTRACT: "a203da329f05e50c64aefd495e39d971b1865eb8816839be1c0dffd0f939cf79",
    Q3_PARSER_QUALIFICATION: "b4bec669fb87160b251c123947d9dd8c3819f0c03c2e729aaa4c83c5670d6eca",
    Q3_ACQUISITION: "b500b1a4a7d9561cbf0c0f2901c71469171ff70a92615bf98ab1144ed3d595ff",
    Q3_RUNTIME_HOLD: "41646106382f7acda2564d74410ec537bc61c606cfe2155bc3e95b9a9c2bd949",
    TREATMENTS: "35b5f8dab0606ca930a237a6248c9b0aac8a5b6f5564e3ba57217a34dfd92ad7",
    SOURCE_MEMORY: "0451d0346ab5df749df6c1f1d1ea3abbcde3f913958149be9671fce1bfbf2239",
}
EXPECTED_IDENTITIES = [
    [5, "sphinx-doc__sphinx-9230"],
    [6, "django__django-11880"],
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_preoutcome_inputs() -> dict[str, Any]:
    checks: dict[str, Any] = {}
    for path, expected in EXPECTED_HASHES.items():
        actual = sha256_file(path)
        checks[str(path.relative_to(ROOT))] = {
            "expected": expected,
            "actual": actual,
            "pass": actual == expected,
        }
    fixtures = load_json(Q3_FIXTURES)
    runtime = load_json(Q3_RUNTIME_HOLD)
    identities = [
        [row["selection_rank"], row["instance_id"]]
        for row in fixtures["fixtures"]
    ]
    checks["same_unrun_q3_identities"] = {
        "expected": EXPECTED_IDENTITIES,
        "actual": identities,
        "pass": identities == EXPECTED_IDENTITIES,
    }
    checks["q3_runtime_hold_was_outcome_blind"] = {
        "pass": (
            runtime["decision"] == "P1_Q3_RUNTIME_HOLD"
            and runtime["scientific_boundary"]["q3_task_outcome_observed"] is False
            and runtime["scientific_boundary"]["full_p1_execution_authorized"] is False
            and len(runtime["rows"]) == 2
            and runtime["rows"][0]["instance_id"] == "sphinx-doc__sphinx-9230"
            and runtime["rows"][0]["error_type"] == "RuntimeError"
            and "base state is not an exact or clean tree-equivalent descendant"
            in runtime["rows"][0]["message"]
            and runtime["rows"][1]["instance_id"] == "django__django-11880"
            and runtime["rows"][1]["pass"] is True
        ),
    }
    checks["no_q3_model_execution_artifacts"] = {
        "pass": not Q3_INDEX.exists() and not Q3_RUN_DIR.exists(),
    }
    if not all(row["pass"] for row in checks.values()):
        raise RuntimeError("Q4 pre-outcome input verification failed")
    return checks


def prepare(output: Path = CONTRACT) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError(f"refusing to overwrite immutable Q4 contract: {output}")
    verification = verify_preoutcome_inputs()
    treatments = load_json(TREATMENTS)
    payload = {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-P1-Q4-BASE-NORMALIZATION-20260830",
        "created_at_utc": utcnow(),
        "purpose": (
            "Prospectively qualify an exact-base runtime normalization after the "
            "outcome-blind Q3 runtime gate rejected an image-builder descendant. "
            "Q3 remains HOLD; Q4 reuses the same still-unrun fixed tasks and images."
        ),
        "preoutcome_input_verification": verification,
        "bindings": {
            "q3_fixtures": str(Q3_FIXTURES.relative_to(ROOT)),
            "q3_fixtures_sha256": sha256_file(Q3_FIXTURES),
            "q3_contract": str(Q3_CONTRACT.relative_to(ROOT)),
            "q3_contract_sha256": sha256_file(Q3_CONTRACT),
            "q3_parser_qualification": str(Q3_PARSER_QUALIFICATION.relative_to(ROOT)),
            "q3_parser_qualification_sha256": sha256_file(Q3_PARSER_QUALIFICATION),
            "q3_fixed_image_acquisition": str(Q3_ACQUISITION.relative_to(ROOT)),
            "q3_fixed_image_acquisition_sha256": sha256_file(Q3_ACQUISITION),
            "q3_runtime_hold": str(Q3_RUNTIME_HOLD.relative_to(ROOT)),
            "q3_runtime_hold_sha256": sha256_file(Q3_RUNTIME_HOLD),
            "treatment_manifest": str(TREATMENTS.relative_to(ROOT)),
            "treatment_manifest_sha256": sha256_file(TREATMENTS),
            "source_memory": str(SOURCE_MEMORY.relative_to(ROOT)),
            "source_memory_sha256": sha256_file(SOURCE_MEMORY),
            "official_reasoningbank_commit": OFFICIAL_COMMIT,
        },
        "selection": {
            "ranks": [5, 6],
            "instance_ids": [row[1] for row in EXPECTED_IDENTITIES],
            "same_still_unrun_q3_tasks": True,
            "uses_task_outcome": False,
            "uses_gold_patch": False,
            "replacement_sampling": "forbidden",
            "automatic_model_run_retry": "forbidden",
        },
        "backend": {
            "base_url": BASE_URL,
            "model": MODEL,
            "behavior_temperature": 0.0,
            "max_output_tokens": "omitted",
            "seed": "omitted",
            "top_p": "omitted",
            "max_retries": MAX_RETRIES,
            "workers": 1,
            "step_limit": STEP_LIMIT,
            "environment_timeout_seconds": COMMAND_TIMEOUT_SECONDS,
        },
        "treatments": {
            "arms": list("ABCDE"),
            "treatment_sha256": {
                arm: treatments["arms"][arm]["treatment_sha256"]
                for arm in "ABCDE"
            },
            "ordered_execution": "rank 5 A/B/C/D/E then rank 6 A/B/C/D/E",
            "fresh_container_each_run": True,
            "session_reuse_across_arms": False,
        },
        "runtime_normalization": {
            "platform": "linux/amd64",
            "pid_namespace": PID_NAMESPACE,
            "image_identity": "exact frozen amd64 manifest digest",
            "applies_to_every_q4_container": True,
            "preconditions": [
                "frozen expected base commit object exists in /testbed",
                "frozen expected base commit is an ancestor of initial HEAD",
                "initial /testbed worktree and index are clean",
                "no task test, evaluator, model request, or task outcome has occurred",
            ],
            "action": "git reset --hard <frozen expected base commit>",
            "git_clean_invoked": False,
            "postconditions": [
                "HEAD equals the frozen expected base commit",
                "worktree and index remain clean",
                "image digest and installed environment remain unchanged",
            ],
            "failure_policy": "HOLD without model call; no automatic retry or replacement",
        },
        "qualification": {
            "planned_runs": 10,
            "requires": [
                "outcome-blind Q4 runtime normalization qualifies both fixed images once",
                "all ten model runs persist once in frozen order without replacement",
                "no provider, provider-identity, runtime, or implementation failure",
                "no blank model-visible message content",
                "all completed responses resolve to the exact frozen model",
                "valid SWE-bench evaluator output for every run",
                "official parser conformance remains exact",
                "A/B and B/E selected memory plus first R1 request equal per task",
            ],
            "negative_task_outcome_does_not_fail_qualification": True,
            "pass_opens_only_a_separate_full-P1 planning gate": True,
            "full_p1_execution_authorized": False,
        },
        "outcome_discipline": {
            "q1_q2_q3_artifacts_immutable": True,
            "q3_runtime_hold_preserved": True,
            "q3_model_run_count": 0,
            "q3_task_outcome_observed": False,
            "q4_contract_frozen_before_runtime_implementation": True,
            "no_parameter_or_task_change_after_any_q4_task_outcome": True,
        },
        "authorization": {
            "q4_runtime_qualification_authorized": True,
            "q4_model_execution_authorized_only_after_runtime_pass": True,
            "full_p1_execution_authorized": False,
            "paper_result_claim_authorized": False,
        },
        "credential_material_present": False,
    }
    file_sha = write_json(output, payload)
    return {
        "decision": "P1_Q4_BASE_NORMALIZATION_PREREGISTERED",
        "contract": str(output.relative_to(ROOT)),
        "contract_file_sha256": file_sha,
        "instance_ids": payload["selection"]["instance_ids"],
    }


def validate_existing(path: Path = CONTRACT) -> list[str]:
    errors: list[str] = []
    contract = load_json(path)
    if contract["selection"]["ranks"] != [5, 6]:
        errors.append("Q4 ranks drift")
    if contract["selection"]["instance_ids"] != [
        "sphinx-doc__sphinx-9230", "django__django-11880"
    ]:
        errors.append("Q4 identities drift")
    if contract["outcome_discipline"]["q3_model_run_count"] != 0:
        errors.append("Q3 model run count drift")
    if contract["outcome_discipline"]["q3_task_outcome_observed"] is not False:
        errors.append("Q3 task outcome boundary drift")
    if contract["runtime_normalization"]["git_clean_invoked"] is not False:
        errors.append("Q4 reset scope drift")
    if contract["authorization"]["full_p1_execution_authorized"] is not False:
        errors.append("Q4 cannot authorize full P1")
    if contract["bindings"]["q3_runtime_hold_sha256"] != sha256_file(Q3_RUNTIME_HOLD):
        errors.append("Q3 runtime HOLD binding drift")
    return errors


if __name__ == "__main__":
    print(json.dumps(prepare(), ensure_ascii=False, sort_keys=True))
