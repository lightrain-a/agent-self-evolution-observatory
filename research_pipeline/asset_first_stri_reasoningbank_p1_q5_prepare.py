"""Freeze the Q4 failure differential and Q5 evaluator-verbosity repair preregistration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    MODEL, ROOT, canonical_json, sha256_file, sha256_text, utcnow, write_json,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_eval import parse_pytest_v2
from research_pipeline.asset_first_stri_reasoningbank_p1_q3_parser_qualification import (
    WHEEL_SHA256, load_official,
)

Q2_ADJUDICATION = ROOT / "generated/asset-first-stri-reasoningbank-p1-q2-adjudication-20260830.json"
Q3_CONTRACT = ROOT / "generated/asset-first-stri-reasoningbank-p1-q3-qualification-contract-20260830.json"
Q3_RUNTIME_HOLD = ROOT / "generated/asset-first-stri-reasoningbank-p1-q3-runtime-qualification-result-20260830.json"
Q4_CONTRACT = ROOT / "generated/asset-first-stri-reasoningbank-p1-q4-base-normalization-contract-20260830.json"
Q4_RUNTIME = ROOT / "generated/asset-first-stri-reasoningbank-p1-q4-runtime-qualification-result-20260830.json"
Q4_INDEX = ROOT / "generated/asset-first-stri-reasoningbank-p1-q4-index-20260830.json"
Q4_ADJUDICATION = ROOT / "generated/asset-first-stri-reasoningbank-p1-q4-adjudication-20260830.json"
FIXTURES = ROOT / "generated/asset-first-stri-reasoningbank-p1-q3-task-fixtures-20260830.json"
TREATMENTS = ROOT / "generated/asset-first-stri-reasoningbank-p1-treatment-manifest-20260829.json"
PARSER_QUALIFICATION = ROOT / "generated/asset-first-stri-reasoningbank-p1-q3-parser-qualification-20260830.json"
MANIFEST = ROOT / "generated/asset-first-stri-reasoningbank-p1-q4-artifact-manifest-20260830.json"
DIFFERENTIAL = ROOT / "generated/asset-first-stri-reasoningbank-p1-q4-failure-differential-20260830.json"
MEMORY = ROOT / "generated/asset-first-stri-reasoningbank-p1-q2-q3-q4-scientific-memory-20260830.json"
CONTRACT = ROOT / "generated/asset-first-stri-reasoningbank-p1-q5-evaluator-verbosity-repair-contract-20260830.json"

EXPECTED_HASHES = {
    Q2_ADJUDICATION: "019cba107a4251a8791ab4b2edae8a916b48f55776fec98180b0ea914c8413bc",
    Q3_CONTRACT: "a203da329f05e50c64aefd495e39d971b1865eb8816839be1c0dffd0f939cf79",
    Q3_RUNTIME_HOLD: "41646106382f7acda2564d74410ec537bc61c606cfe2155bc3e95b9a9c2bd949",
    Q4_CONTRACT: "20fdd28863a5904c4f929d45e445ffa425c8e0d88fb93260030c9b7ce956a57e",
    Q4_RUNTIME: "cfeafc8152a86111f1197045ed210e488b4f59d58f243a7c2fe1ae40f05ed7ed",
    Q4_INDEX: "f6ce4e4a345fa8e105ddca934faa1c85af14b039497768ebef1bd0222409a0bf",
    Q4_ADJUDICATION: "c3fe8f239a4128f89ed8c851cc0af8d061aec02333a60c4c9f397f3027908b26",
    FIXTURES: "b35c9b7a798b371818b25774c129d77c74f7dc90217b3f54f7e4e1d474d15519",
    TREATMENTS: "35b5f8dab0606ca930a237a6248c9b0aac8a5b6f5564e3ba57217a34dfd92ad7",
    PARSER_QUALIFICATION: "b4bec669fb87160b251c123947d9dd8c3819f0c03c2e729aaa4c83c5670d6eca",
}
EXPECTED_ORDER = [
    *[(5, "sphinx-doc__sphinx-9230", arm) for arm in "ABCDE"],
    *[(6, "django__django-11880", arm) for arm in "ABCDE"],
]
SPHINX_BEFORE = "tox --current-env -epy39 -v -- tests/test_domain_py.py"
SPHINX_AFTER = "tox --current-env -epy39 -v -- -rA tests/test_domain_py.py"
CANONICAL_LESSON = (
    "implementation/operationalization failure -> no scientific belief update -> "
    "prospective repaired qualification"
)


def load_payload(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    expected = value.pop("payload_sha256")
    if expected != sha256_text(canonical_json(value)):
        raise RuntimeError(f"payload digest drift: {path}")
    return value


def verify_frozen_inputs() -> dict[str, Any]:
    checks = {}
    for path, expected in EXPECTED_HASHES.items():
        actual = sha256_file(path)
        checks[str(path.relative_to(ROOT))] = {
            "expected": expected, "actual": actual, "pass": actual == expected,
        }
    index = load_payload(Q4_INDEX)
    adjudication = load_payload(Q4_ADJUDICATION)
    journal_order = [
        (r["selection_rank"], r["instance_id"], r["arm"])
        for r in index["run_journal"]
    ]
    completed_order = [
        (r["selection_rank"], r["instance_id"], r["arm"])
        for r in index["completed_runs"]
    ]
    checks["q4_terminal_exactly_once"] = {"pass": (
        index["execution_complete"] is True
        and len(index["run_journal"]) == len(index["completed_runs"]) == 10
        and journal_order == completed_order == EXPECTED_ORDER
        and all(r["attempt_count"] == 1 for r in index["run_journal"])
        and all(r["attempt_count"] == 1 for r in index["completed_runs"])
        and all(r["status"] == "persisted" for r in index["run_journal"])
        and index["automatic_retry"] == "forbidden"
        and index["replacement_sampling"] == "forbidden"
    )}
    checks["q4_adjudication_hold"] = {"pass": (
        adjudication["decision"] == "P1_Q4_IMPLEMENTATION_UNQUALIFIED_FULL_P1_HOLD"
        and adjudication["implementation_qualified"] is False
        and adjudication["authorization"]["full_p1_execution_authorized"] is False
    )}
    if not all(r["pass"] for r in checks.values()):
        raise RuntimeError("Q5 preregistration input verification failed")
    return checks


def artifact_rows(index: dict[str, Any]) -> list[dict[str, Any]]:
    paths = [Q4_CONTRACT, Q4_RUNTIME, Q4_INDEX, Q4_ADJUDICATION]
    paths += [ROOT / r["path"] for r in index["completed_runs"]]
    expected = {
        str((ROOT / r["path"]).resolve()): r["file_sha256"]
        for r in index["completed_runs"]
    }
    rows = []
    for path in paths:
        actual = sha256_file(path)
        receipt = expected.get(str(path.resolve()))
        rows.append({
            "path": str(path.relative_to(ROOT)), "sha256": actual,
            "bytes": path.stat().st_size,
            "index_expected_sha256": receipt,
            "index_hash_matches": receipt is None or receipt == actual,
        })
    return rows


def parser_differential(index: dict[str, Any]) -> list[dict[str, Any]]:
    official, _ = load_official()
    rows = []
    for receipt in index["completed_runs"]:
        if receipt["instance_id"] != "sphinx-doc__sphinx-9230":
            continue
        run = load_payload(ROOT / receipt["path"])
        raw_execution = run["R4_terminal_outcome"]["raw_execution"]
        raw = raw_execution["output"]
        sliced = raw.split(">>>>> Start Test Output", 1)[1].split(
            ">>>>> End Test Output", 1
        )[0]
        official_map = official["parse_log_pytest_v2"](sliced, None)
        local_map = parse_pytest_v2(sliced)
        rows.append({
            "ordinal": receipt["ordinal"], "run_id": receipt["run_id"],
            "arm": receipt["arm"], "run_file_sha256": receipt["file_sha256"],
            "raw_log_sha256": sha256_text(raw),
            "evaluator_returncode": raw_execution["returncode"],
            "evaluator_timed_out": raw_execution["timed_out"],
            "valid_markers": (
                ">>>>> Start Test Output" in raw and ">>>>> End Test Output" in raw
            ),
            "official_status_count": len(official_map),
            "local_status_count": len(local_map),
            "official_local_exact": official_map == local_map,
            "descriptive_summary_contains_45_passed": "45 passed" in sliced,
            "descriptive_task_outcome_used_to_choose_repair": False,
        })
    return rows


def replay_sources(
    index: dict[str, Any], fixtures: dict[str, Any],
) -> list[dict[str, Any]]:
    fixture_by_id = {r["instance_id"]: r for r in fixtures["fixtures"]}
    rows = []
    for receipt in index["completed_runs"]:
        run = load_payload(ROOT / receipt["path"])
        fixture = fixture_by_id[receipt["instance_id"]]
        patch = run["result"]
        if not patch.strip():
            raise RuntimeError(f"missing frozen Q4 patch: {receipt['run_id']}")
        script = fixture["evaluator_only"]["eval_script"]
        if receipt["instance_id"] == "sphinx-doc__sphinx-9230":
            if script.count(SPHINX_BEFORE) != 1:
                raise RuntimeError("Sphinx evaluator invocation drift")
            repaired = script.replace(SPHINX_BEFORE, SPHINX_AFTER)
        else:
            repaired = script
        rows.append({
            "ordinal": receipt["ordinal"],
            "selection_rank": receipt["selection_rank"],
            "instance_id": receipt["instance_id"], "arm": receipt["arm"],
            "source_run_id": receipt["run_id"],
            "source_run_path": receipt["path"],
            "source_run_sha256": receipt["file_sha256"],
            "source_patch_sha256": sha256_text(patch),
            "task_sha256": run["task_sha256"],
            "image": fixture["image_pull_reference"],
            "image_amd64_manifest_digest": fixture["image_amd64_manifest_digest"],
            "base_commit": fixture["model_visible"]["base_commit"],
            "log_parser": fixture["evaluator_only"]["log_parser"],
            "original_eval_script_sha256": sha256_text(script),
            "repaired_eval_script_sha256": sha256_text(repaired),
            "evaluator_script_changed": repaired != script,
            "model_calls_authorized": False,
        })
    return rows


def prepare() -> dict[str, Any]:
    for output in (MANIFEST, DIFFERENTIAL, MEMORY, CONTRACT):
        if output.exists():
            raise RuntimeError(f"refusing to overwrite immutable Q5 artifact: {output}")
    verification = verify_frozen_inputs()
    index = load_payload(Q4_INDEX)
    adjudication = load_payload(Q4_ADJUDICATION)
    fixtures = load_payload(FIXTURES)

    artifacts = artifact_rows(index)
    if len(artifacts) != 14 or not all(r["index_hash_matches"] for r in artifacts):
        raise RuntimeError("Q4 artifact manifest verification failed")
    manifest_sha = write_json(MANIFEST, {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-P1-Q4-ARTIFACT-MANIFEST-20260830",
        "created_at_utc": utcnow(),
        "execution_head": "2d0a026a1ded46b6c1a4a9063f507fe05d4ff867",
        "artifact_count": len(artifacts), "artifacts": artifacts,
        "all_artifacts_sha256_verified": True,
        "q4_execution_complete": True, "credential_material_present": False,
    })

    parser_rows = parser_differential(index)
    if len(parser_rows) != 5 or not all(
        r["official_local_exact"] and r["official_status_count"] == 0
        and r["evaluator_returncode"] == 0 and not r["evaluator_timed_out"]
        and r["valid_markers"] for r in parser_rows
    ):
        raise RuntimeError("Q4 evaluator differential evidence drift")

    differential_sha = write_json(DIFFERENTIAL, {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-P1-Q4-FAILURE-DIFFERENTIAL-20260830",
        "created_at_utc": utcnow(),
        "q4_adjudication_sha256": sha256_file(Q4_ADJUDICATION),
        "q4_artifact_manifest_sha256": manifest_sha,
        "only_failed_qualification_check": "all_runs_implementation_valid",
        "failed_run_count": 5,
        "failed_run_identity": "sphinx-doc__sphinx-9230 A/B/C/D/E",
        "failed_per_run_check": "valid_swebench_evaluator_output",
        "parser_replay": parser_rows,
        "classification": {
            "implementation_runtime": False, "provider": False,
            "parser": False, "evaluator": True,
            "base_state_normalization": False, "environment": False,
            "artifact_integrity": False, "treatment_invariant_failure": False,
            "genuine_non_implementation_issue": False,
            "primary_failure_layer": "evaluator",
            "primary_failure_class": "EVALUATOR_LOG_VERBOSITY_NOT_PARSEABLE",
        },
        "diagnosis": (
            "The frozen Sphinx evaluator emitted pytest dot-progress output. Both "
            "the SHA-frozen official SWE-bench 5.0.2 parse_log_pytest_v2 and the "
            "local conformant parser returned an empty status map despite valid "
            "markers, returncode 0, and no timeout."
        ),
        "single_variable_repair": {
            "variable": "Sphinx evaluator pytest report verbosity",
            "before": SPHINX_BEFORE, "after": SPHINX_AFTER,
            "other_eval_scripts_unchanged": True,
            "task_outcomes_used_to_choose_repair": False,
            "repair_falsifier": (
                "Any Q5 Sphinx replay lacks a nonempty official-parser status map, "
                "or any unchanged Django replay changes implementation validity."
            ),
        },
        "scientific_disposition": {
            "q4_implementation_qualified": False,
            "q4_mechanism_negative_authorized": False,
            "scientific_belief_update": "none",
            "full_p1_planning_gate_open": False,
            "full_p1_execution_authorized": False,
        },
        "credential_material_present": False,
    })

    memory_sha = write_json(MEMORY, {
        "schema_version": 1,
        "memory_id": "E1-STRI-REASONINGBANK-Q2-Q3-Q4-FAILURE-DIFFERENTIAL-20260830",
        "created_at_utc": utcnow(), "canonical_lesson": CANONICAL_LESSON,
        "sequence": [
            {
                "stage": "Q2", "evidence_sha256": sha256_file(Q2_ADJUDICATION),
                "event": "Unsupported Django parser caused implementation disqualification.",
                "scientific_disposition": "Evidence preserved; no mechanism conclusion.",
            },
            {
                "stage": "Q3", "contract_sha256": sha256_file(Q3_CONTRACT),
                "runtime_hold_sha256": sha256_file(Q3_RUNTIME_HOLD),
                "event": (
                    "Runtime stopped before model outcome because the base-state "
                    "tree-equivalence rule rejected an image-builder descendant."
                ),
                "scientific_disposition": (
                    "Q3 did not constitute a mechanism negative and caused no "
                    "scientific belief update."
                ),
            },
            {
                "stage": "Q4", "contract_sha256": sha256_file(Q4_CONTRACT),
                "runtime_qualification_sha256": sha256_file(Q4_RUNTIME),
                "index_sha256": sha256_file(Q4_INDEX),
                "adjudication_sha256": sha256_file(Q4_ADJUDICATION),
                "event": (
                    "The outcome-blind exact-base repair completed exactly once; "
                    "evaluator log verbosity still blocked implementation qualification."
                ),
                "scientific_disposition": (
                    "Q4 is implementation-unqualified; task outcomes are descriptive "
                    "and Full-P1 remains unauthorized."
                ),
            },
        ],
        "reusable_decision_rule": (
            "Do not update belief in STRI propagation until provider, runtime, "
            "parser, evaluator, artifact, and treatment invariants all qualify."
        ),
        "failure_differential_sha256": differential_sha,
        "scientific_authority": False, "experiment_authority": False,
        "credential_material_present": False,
    })

    sources = replay_sources(index, fixtures)
    contract_sha = write_json(CONTRACT, {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-P1-Q5-EVALUATOR-VERBOSITY-REPAIR-20260830",
        "created_at_utc": utcnow(),
        "purpose": (
            "Prospectively qualify one evaluator-only repair without rerunning Q4, "
            "calling the model, changing tasks, treatments, patches, or using task "
            "success to select the repair."
        ),
        "bindings": {
            "q4_artifact_manifest_sha256": manifest_sha,
            "q4_adjudication_sha256": sha256_file(Q4_ADJUDICATION),
            "q4_failure_differential_sha256": differential_sha,
            "scientific_memory_sha256": memory_sha,
            "fixtures_sha256": sha256_file(FIXTURES),
            "treatment_manifest_sha256": sha256_file(TREATMENTS),
            "parser_qualification_sha256": sha256_file(PARSER_QUALIFICATION),
            "official_swebench_wheel_sha256": WHEEL_SHA256,
        },
        "population": {
            "task_count": 2, "replay_unit_count": 10,
            "ranks": [5, 6],
            "instance_ids": ["sphinx-doc__sphinx-9230", "django__django-11880"],
            "arms": list("ABCDE"),
            "order": "rank 5 A/B/C/D/E then rank 6 A/B/C/D/E",
            "source_selection": "all ten frozen Q4 runs in index order",
            "replacement_sampling": "forbidden", "automatic_retry": "forbidden",
        },
        "frozen_replay_sources": sources,
        "single_variable_repair": {
            "variable": "Sphinx evaluator pytest report verbosity",
            "before": SPHINX_BEFORE, "after": SPHINX_AFTER,
            "scope": "Sphinx eval_script only",
            "django_eval_script_byte_identical": True,
            "model_patch_byte_identical_to_q4": True,
            "model_visible_requests_reused_not_reissued": True,
            "model_calls": 0, "provider_calls": 0,
        },

        "replay_protocol": {
            "fresh_exact_digest_container_per_replay": True,
            "exact_base_normalization_same_as_q4": True,
            "apply_exact_q4_result_patch": True,
            "apply_frozen_test_patch": True,
            "official_parser": "SWE-bench 5.0.2 SHA-frozen parse_log callable",
            "persist_raw_output_and_status_map": True,
            "attempt_count": 1,
            "stopping_rule": "execute all ten once unless an integrity precondition fails",
            "failure_policy": "HOLD; no retry, replacement, or Q4 reclassification",
        },
        "qualification": {
            "primary": "all ten replays yield valid official-parser evaluator output",
            "secondary": [
                "all run, patch, fixture, image, and base hashes remain exact",
                "Sphinx official status maps are nonempty",
                "Django implementation validity is unchanged",
            ],
            "negative_task_outcome_does_not_fail_qualification": True,
            "q4_reclassification_forbidden": True,
            "mechanism_claim_authorized": False,
        },
        "claim_boundary": {
            "q5_is_implementation_qualification_only": True,
            "r0_r1_r2_r3_behavioral_claim_authorized": False,
            "r4_performance_claim_authorized": False,
            "full_p1_planning_gate_open": False,
            "full_p1_execution_authorized": False,
        },
        "authorization": {
            "q5_replay_runner_implementation_authorized": True,
            "q5_replay_execution_authorized": False,
            "full_p1_preregistration_authorized": False,
            "full_p1_execution_authorized": False,
            "paper_result_claim_authorized": False,
        },
        "preoutcome_verification": verification,
        "credential_material_present": False,
    })
    return {
        "decision": "P1_Q5_EVALUATOR_VERBOSITY_REPAIR_PREREGISTERED",
        "manifest_sha256": manifest_sha,
        "failure_differential_sha256": differential_sha,
        "scientific_memory_sha256": memory_sha,
        "contract_sha256": contract_sha,
        "q5_replay_execution_authorized": False,
        "full_p1_execution_authorized": False,
    }


def validate_existing() -> list[str]:
    errors = []
    manifest = load_payload(MANIFEST)
    differential = load_payload(DIFFERENTIAL)
    memory = load_payload(MEMORY)
    contract = load_payload(CONTRACT)
    if manifest["artifact_count"] != 14:
        errors.append("Q4 artifact count drift")
    if not manifest["all_artifacts_sha256_verified"]:
        errors.append("Q4 artifact verification drift")
    if differential["classification"]["primary_failure_layer"] != "evaluator":
        errors.append("Q4 failure layer drift")
    if differential["classification"]["parser"] is not False:
        errors.append("Q4 parser differential drift")
    if memory["canonical_lesson"] != CANONICAL_LESSON:
        errors.append("scientific memory lesson drift")
    if len(contract["frozen_replay_sources"]) != 10:
        errors.append("Q5 replay population drift")
    if contract["single_variable_repair"]["before"] != SPHINX_BEFORE:
        errors.append("Q5 repair before-state drift")
    if contract["single_variable_repair"]["after"] != SPHINX_AFTER:
        errors.append("Q5 repair after-state drift")
    if contract["authorization"]["q5_replay_execution_authorized"] is not False:
        errors.append("Q5 execution authority must remain closed")
    if contract["authorization"]["full_p1_execution_authorized"] is not False:
        errors.append("Full-P1 execution authority must remain closed")
    if any(r["model_calls_authorized"] for r in contract["frozen_replay_sources"]):
        errors.append("Q5 model-call boundary drift")
    return errors


if __name__ == "__main__":
    print(json.dumps(prepare(), sort_keys=True))


