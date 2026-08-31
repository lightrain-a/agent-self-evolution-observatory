"""Frozen outcome-blind adjudicator and evidence packager for Q5."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT, canonical_json, sha256_file, sha256_text, utcnow, write_json,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q5_core import (
    CONTRACT_SHA256, EXPECTED_ORDER, verify_q5_contract,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q5_prepare import (
    CONTRACT, DIFFERENTIAL as Q4_DIFFERENTIAL, MEMORY as Q4_MEMORY,
    Q4_ADJUDICATION, Q4_INDEX, load_payload,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q5_runner import INDEX
from research_pipeline.asset_first_stri_reasoningbank_p1_q7_smoke import (
    AUTHORITY, SMOKE,
)

OUTPUT = ROOT / "generated/asset-first-stri-reasoningbank-p1-q5-adjudication-20260831.json"
MANIFEST = ROOT / "generated/asset-first-stri-reasoningbank-p1-q5-artifact-manifest-20260831.json"
FAILURE_DIFFERENTIAL = ROOT / "generated/asset-first-stri-reasoningbank-p1-q5-failure-differential-20260831.json"
MEMORY = ROOT / "generated/asset-first-stri-reasoningbank-p1-q2-q3-q4-q5-scientific-memory-20260831.json"
PASS_DECISION = "P1_Q5_EVALUATOR_REPAIR_QUALIFIED_FULL_P1_PLANNING_GATE_OPEN_EXECUTION_UNAUTHORIZED"
FAIL_DECISION = "P1_Q5_EVALUATOR_REPAIR_UNQUALIFIED_FULL_P1_HOLD"
CANONICAL_LESSON = (
    "implementation/operationalization failure -> no scientific belief update -> "
    "prospective repaired qualification"
)
EVALUATOR_LESSON = (
    "A benchmark command may terminate successfully and report aggregate test "
    "success while remaining scientifically unusable when the official evaluator "
    "requires per-test status records hidden by the selected verbosity."
)


def _artifact_rows(index: dict[str, Any]) -> list[dict[str, Any]]:
    paths = [CONTRACT, SMOKE, AUTHORITY, INDEX]
    paths.extend(ROOT / row["path"] for row in index["completed_runs"])
    expected = {
        str((ROOT / row["path"]).resolve()): row["file_sha256"]
        for row in index["completed_runs"]
    }
    rows = []
    for path in paths:
        actual = sha256_file(path)
        expected_sha = expected.get(str(path.resolve()))
        rows.append({
            "path": str(path.relative_to(ROOT)),
            "sha256": actual,
            "bytes": path.stat().st_size,
            "index_expected_sha256": expected_sha,
            "hash_matches": expected_sha is None or expected_sha == actual,
        })
    return rows


def adjudicate(
    index_path: Path = INDEX, output: Path = OUTPUT,
) -> dict[str, Any]:
    for path in (output, MANIFEST, FAILURE_DIFFERENTIAL, MEMORY):
        if path.exists():
            raise RuntimeError(f"refusing to overwrite immutable Q5 evidence: {path}")
    verify_q5_contract()
    index = load_payload(index_path)
    authority = load_payload(AUTHORITY)
    completed = index["completed_runs"]
    journal = index["run_journal"]
    actual_order = [
        (r["selection_rank"], r["instance_id"], r["arm"]) for r in completed
    ]
    journal_order = [
        (r["selection_rank"], r["instance_id"], r["arm"]) for r in journal
    ]
    summaries = []
    artifact_checks = []
    for receipt in completed:
        path = (ROOT / receipt["path"]).resolve()
        if not path.is_relative_to(ROOT.resolve()):
            raise RuntimeError("Q5 run path escapes repository")
        actual_sha = sha256_file(path)
        run = load_payload(path)
        hash_pass = actual_sha == receipt["file_sha256"]
        artifact_checks.append({
            "run_id": receipt["run_id"],
            "expected_sha256": receipt["file_sha256"],
            "actual_sha256": actual_sha,
            "pass": hash_pass,
        })
        checks = run.get("implementation_checks") or {}
        summaries.append({
            "ordinal": receipt["ordinal"],
            "selection_rank": receipt["selection_rank"],
            "instance_id": receipt["instance_id"],
            "arm": receipt["arm"],
            "run_id": receipt["run_id"],
            "run_file_sha256": actual_sha,
            "implementation_checks": checks,
            "implementation_valid": bool(
                hash_pass and run.get("implementation_valid") is True
                and checks and all(checks.values())
            ),
            "official_status_count": len(run.get("official_parser_status_map") or {}),
            "resolved": run.get("resolved"),
            "task_outcome_affects_qualification": False,
            "model_calls": run.get("model_calls"),
            "provider_calls": run.get("provider_calls"),
            "failure": run.get("failure"),
        })
    sphinx = [r for r in summaries if r["instance_id"] == "sphinx-doc__sphinx-9230"]
    django = [r for r in summaries if r["instance_id"] == "django__django-11880"]
    q4 = load_payload(Q4_ADJUDICATION)
    q4_django = [
        r for r in q4["run_summaries"] if r["instance_id"] == "django__django-11880"
    ]
    checks = {
        "contract_exact": index["contract_sha256"] == CONTRACT_SHA256,
        "smoke_and_authority_exact": (
            index["smoke_sha256"] == sha256_file(SMOKE)
            and index["execution_authority_sha256"] == sha256_file(AUTHORITY)
            and authority["q5_replay_execution_authorized"] is True
        ),
        "all_ten_started_once_in_frozen_order": (
            len(journal) == 10
            and journal_order == EXPECTED_ORDER
            and all(r["attempt_count"] == 1 and r["status"] == "persisted" for r in journal)
        ),
        "all_ten_persisted_once_in_frozen_order": (
            index["execution_complete"] is True
            and len(completed) == 10
            and actual_order == EXPECTED_ORDER
            and len({r["run_id"] for r in completed}) == 10
            and all(r["attempt_count"] == 1 for r in completed)
        ),
        "all_artifact_hashes_valid": (
            len(artifact_checks) == 10 and all(r["pass"] for r in artifact_checks)
        ),
        "all_ten_implementation_valid": (
            len(summaries) == 10 and all(r["implementation_valid"] for r in summaries)
        ),
        "all_sphinx_official_status_maps_nonempty": (
            len(sphinx) == 5 and all(r["official_status_count"] > 0 for r in sphinx)
        ),
        "django_validity_unchanged_from_q4": (
            len(django) == len(q4_django) == 5
            and all(r["implementation_valid"] for r in django)
            and all(r["implementation_pass"] for r in q4_django)
        ),
        "no_model_or_provider_calls": (
            index["model_calls"] == index["provider_calls"] == 0
            and all(r["model_calls"] == r["provider_calls"] == 0 for r in summaries)
        ),
        "no_retry_or_replacement": (
            index["automatic_retry"] == "forbidden"
            and index["replacement_sampling"] == "forbidden"
        ),
        "task_outcomes_excluded_from_qualification": True,
        "q4_not_reclassified": (
            q4["decision"] == "P1_Q4_IMPLEMENTATION_UNQUALIFIED_FULL_P1_HOLD"
        ),
    }
    qualified = all(checks.values())
    decision = PASS_DECISION if qualified else FAIL_DECISION
    payload = {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-P1-Q5-ADJUDICATION-20260831",
        "created_at_utc": utcnow(),
        "contract_sha256": CONTRACT_SHA256,
        "index_sha256": sha256_file(index_path),
        "smoke_sha256": sha256_file(SMOKE),
        "execution_authority_sha256": sha256_file(AUTHORITY),
        "artifact_checks": artifact_checks,
        "run_summaries": summaries,
        "qualification_checks": checks,
        "implementation_qualified": qualified,
        "descriptive_task_outcomes": {
            "resolved_count": sum(r["resolved"] is True for r in summaries),
            "unresolved_count": sum(r["resolved"] is False for r in summaries),
            "missing_or_invalid_count": sum(r["resolved"] is None for r in summaries),
            "sphinx": {r["arm"]: r["resolved"] for r in sphinx},
            "django": {r["arm"]: r["resolved"] for r in django},
            "used_for_implementation_qualification": False,
        },
        "decision": decision,
        "authorization": {
            "full_p1_preregistration_authorized": qualified,
            "full_p1_execution_authorized": False,
            "paper_result_claim_authorized": False,
            "q4_reclassified": False,
        },
        "scientific_boundary": {
            "q5_is_evaluator_implementation_qualification_only": True,
            "r0_r1_r2_r3_behavioral_claim_authorized": False,
            "r4_performance_claim_authorized": False,
            "scientific_belief_update": "none",
        },
        "credential_material_present": False,
    }
    output_sha = write_json(output, payload)

    manifest_rows = _artifact_rows(index)
    manifest_sha = write_json(MANIFEST, {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-P1-Q5-ARTIFACT-MANIFEST-20260831",
        "created_at_utc": utcnow(),
        "artifact_count": len(manifest_rows),
        "artifacts": manifest_rows,
        "all_artifacts_sha256_verified": all(r["hash_matches"] for r in manifest_rows),
        "adjudication_sha256": output_sha,
        "credential_material_present": False,
    })
    failed = [
        {"run_id": r["run_id"], "failed_checks": [
            key for key, value in r["implementation_checks"].items() if not value
        ], "failure": r["failure"]}
        for r in summaries if not r["implementation_valid"]
    ]
    differential_sha = write_json(FAILURE_DIFFERENTIAL, {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-P1-Q5-FAILURE-DIFFERENTIAL-20260831",
        "created_at_utc": utcnow(),
        "q5_adjudication_sha256": output_sha,
        "q5_artifact_manifest_sha256": manifest_sha,
        "implementation_qualified": qualified,
        "failed_runs": failed,
        "classification": (
            {"failure_present": False, "primary_failure_layer": None}
            if qualified else {
                "failure_present": True,
                "primary_failure_layer": "implementation/evaluator",
            }
        ),
        "scientific_belief_update": "none",
        "task_outcomes_used_for_classification": False,
        "q4_preserved_unchanged": True,
        "credential_material_present": False,
    })
    memory_sha = write_json(MEMORY, {
        "schema_version": 1,
        "memory_id": "E1-STRI-REASONINGBANK-Q2-Q3-Q4-Q5-FAILURE-DIFFERENTIAL-20260831",
        "created_at_utc": utcnow(),
        "canonical_lesson": CANONICAL_LESSON,
        "evaluator_specific_lesson": EVALUATOR_LESSON,
        "operational_lessons": [
            "returncode 0 is not sufficient evaluator qualification",
            "parser equivalence cannot repair missing observability",
            "evaluator logging is part of the measurement contract",
            (
                "observability-only changes can be valid prospective implementation "
                "repairs when test semantics remain invariant"
            ),
        ],
        "bindings": {
            "q4_scientific_memory_sha256": sha256_file(Q4_MEMORY),
            "q4_failure_differential_sha256": sha256_file(Q4_DIFFERENTIAL),
            "q4_adjudication_sha256": sha256_file(Q4_ADJUDICATION),
            "q5_contract_sha256": CONTRACT_SHA256,
            "q5_smoke_sha256": sha256_file(SMOKE),
            "q5_authority_sha256": sha256_file(AUTHORITY),
            "q5_index_sha256": sha256_file(index_path),
            "q5_adjudication_sha256": output_sha,
            "q5_failure_differential_sha256": differential_sha,
        },
        "sequence": [
            {"stage": "Q2", "disposition": "implementation failure; no scientific conclusion"},
            {"stage": "Q3", "disposition": "stopped before model outcome; no scientific conclusion"},
            {"stage": "Q4", "disposition": "evaluator output unparseable; no scientific conclusion"},
            {
                "stage": "Q5",
                "disposition": (
                    "prospective evaluator-only repair qualified"
                    if qualified else "prospective repair failed; no scientific conclusion"
                ),
            },
        ],
        "scientific_authority": False,
        "experiment_authority": False,
        "credential_material_present": False,
    })
    return {
        "decision": decision,
        "implementation_qualified": qualified,
        "file_sha256": output_sha,
        "manifest_sha256": manifest_sha,
        "failure_differential_sha256": differential_sha,
        "scientific_memory_sha256": memory_sha,
        "resolved_count": payload["descriptive_task_outcomes"]["resolved_count"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", type=Path, default=INDEX)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    print(json.dumps(adjudicate(args.index, args.output), sort_keys=True))


if __name__ == "__main__":
    main()
