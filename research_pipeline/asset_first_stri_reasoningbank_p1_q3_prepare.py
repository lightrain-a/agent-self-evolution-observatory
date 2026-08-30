"""Freeze the fresh, non-replacement Q3 qualification pilot before execution."""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    BASE_STATE_RULE, BASE_URL, COMMAND_TIMEOUT_SECONDS, MAX_RETRIES, MODEL,
    OFFICIAL_COMMIT, PID_NAMESPACE, ROOT, STEP_LIMIT, canonical_json,
    sha256_file, sha256_text, utcnow, write_json,
)

DATASET = Path(
    "/data/wyt/agent-self-evolution-observatory/external/"
    "stri-swebench-verified-78f471bf655a3137b2e8a75af1501690ec009ec3/"
    "data/test-00000-of-00001.parquet"
)
DATASET_REVISION = "78f471bf655a3137b2e8a75af1501690ec009ec3"
PARQUET_SHA256 = "030cfd7f2a704c4c0226e7f104c725a3b41230b1d3517f9c915ad7ea5be3fa25"
PRIOR_ADJUDICATION = ROOT / "generated/asset-first-stri-reasoningbank-p1-q2-adjudication-20260830.json"
SWEBENCH_WHEEL_SHA256 = "b7f0416a1e686eca22c2f749b5f816685a202835032f6683080e2b53545bbb62"
PARSER_SOURCE = {
    "parse_log_django": {
        "official_callable": "parse_log_django",
        "source_sha256": "3a4f69dccc4e44725c9e3580a323c131bafc434aed3b333126154469a41c5872",
    },
    "parse_log_sphinx": {
        "official_callable": "parse_log_pytest_v2",
        "source_sha256": "d3f4c2ef28b0005fd76df82beb06fb899aa77ae27a775273cc8579524fe8371d",
    },
}
TREATMENTS = ROOT / "generated/asset-first-stri-reasoningbank-p1-treatment-manifest-20260829.json"
SOURCE_MEMORY = ROOT / "generated/asset-first-stri-reasoningbank-p1-source-memory-20260829.json"
FIXTURES = ROOT / "generated/asset-first-stri-reasoningbank-p1-q3-task-fixtures-20260830.json"
CONTRACT = ROOT / "generated/asset-first-stri-reasoningbank-p1-q3-qualification-contract-20260830.json"
MANIFEST_DIR = ROOT / "generated/asset-first-stri-reasoningbank-p1-q3-image-manifests-20260830"
RUNTIME_MANIFEST_DIR = Path("/data/wyt/e1-stri-reasoningbank-runtime/q3-manifests")
SELECTION = (
    {
        "rank": 5,
        "instance_id": "sphinx-doc__sphinx-9230",
        "label": "sphinx9230",
        "index_digest": "sha256:2a18fa57b69c646bf0e1916f1df157a62de80ca8b55325738f9c9eeff9c38c86",
        "amd64_manifest_digest": "sha256:036fb5014ef0054831e7218af5addb8957f527fe4a01bf6d4b6e1eebfdd4fca1",
    },
    {
        "rank": 6,
        "instance_id": "django__django-11880",
        "label": "django11880",
        "index_digest": "sha256:ce0c7fd75b0fe8d24632c627359c5e2bc1a4922843d889870931f80f2f98c311",
        "amd64_manifest_digest": "sha256:4488d53c0526d3a4e679753beb3501d70253a1f687274ef9c2ed07e7225dde6c",
    },
)


def normalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): normalize(v) for k, v in sorted(value.items())}
    if isinstance(value, (list, tuple)):
        return [normalize(v) for v in value]
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return value


def record_sha(row: dict[str, Any]) -> str:
    return sha256_text(canonical_json(normalize(row)))


def visible_fields(row: dict[str, Any]) -> dict[str, Any]:
    return normalize({
        "instance_id": row["instance_id"], "problem_statement": row["problem_statement"],
        "base_commit": row["base_commit"], "repo": row["repo"], "version": row["version"],
    })


def copy_manifests() -> list[dict[str, Any]]:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    receipts = []
    for spec in SELECTION:
        row = {"label": spec["label"]}
        for kind, expected in (
            ("index", spec["index_digest"]), ("amd64", spec["amd64_manifest_digest"])
        ):
            source = RUNTIME_MANIFEST_DIR / f"{spec['label']}-{kind}.json"
            target = MANIFEST_DIR / source.name
            actual = "sha256:" + hashlib.sha256(source.read_bytes()).hexdigest()
            if actual != expected:
                raise RuntimeError(f"{source}: {actual} != {expected}")
            shutil.copyfile(source, target)
            row[f"{kind}_manifest"] = str(target.relative_to(ROOT))
            row[f"{kind}_manifest_sha256"] = actual
        receipts.append(row)
    return receipts


def make_fixture(row: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    evaluator = {
        "eval_type": row["eval_type"], "eval_script": row["eval_script"],
        "log_parser": row["log_parser"], "FAIL_TO_PASS": row["FAIL_TO_PASS"],
        "PASS_TO_PASS": row["PASS_TO_PASS"], "test_patch": row["test_patch"],
    }
    repo = str(row["image"]).split(":latest", 1)[0]
    return {
        "role": "fresh_q3_qualification_evaluation",
        "selection_rank": spec["rank"], "instance_id": row["instance_id"],
        "model_visible": visible_fields(row), "evaluator_only": normalize(evaluator),
        "gold_patch_sha256": sha256_text(str(row["patch"])),
        "full_public_record_sha256": record_sha(row),
        "image_tag": row["image"], "image_index_digest": spec["index_digest"],
        "image_amd64_manifest_digest": spec["amd64_manifest_digest"],
        "image_pull_reference": f"docker.1ms.run/{repo}@{spec['amd64_manifest_digest']}",
        "visibility_invariant": {
            "evaluator_only_fields_never_enter_model_messages": True,
            "gold_patch_content_persisted_in_fixture": False,
        },
    }


def prepare() -> dict[str, Any]:
    if sha256_file(DATASET) != PARQUET_SHA256:
        raise RuntimeError("dataset SHA-256 drift")
    prior = json.loads(PRIOR_ADJUDICATION.read_text(encoding="utf-8"))
    if (
        prior.get("decision")
        != "P1_Q2_IMPLEMENTATION_UNQUALIFIED_FULL_P1_HOLD"
    ):
        raise RuntimeError("prior adjudication drift")
    rows = pq.read_table(DATASET).to_pylist()
    ranked = sorted(
        rows,
        key=lambda row: (
            sha256_text(str(row["instance_id"])), str(row["instance_id"])
        ),
    )
    selected_rows = []
    for spec in SELECTION:
        row = ranked[spec["rank"]]
        if row["instance_id"] != spec["instance_id"]:
            raise RuntimeError("Q3 rank identity drift")
        selected_rows.append(make_fixture(row, spec))
    old_ids = {
        "sympy__sympy-13798", "pytest-dev__pytest-5631", "sympy__sympy-17318",
        "django__django-16100", "sympy__sympy-18211",
    }
    if old_ids & {row["instance_id"] for row in selected_rows}:
        raise RuntimeError("Q3 overlaps source or prior pilot")
    manifest_receipts = copy_manifests()
    fixtures_payload = {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-P1-Q3-FIXTURES-20260830",
        "created_at_utc": utcnow(),
        "dataset": {
            "id": "SWE-bench/SWE-bench_Verified", "revision": DATASET_REVISION,
            "parquet_sha256": PARQUET_SHA256, "row_count": len(rows),
            "download_channel": "hf-mirror.com fixed revision with SHA-256 verification",
        },
        "selection_rule": (
            "Reuse the pre-outcome SHA-256(instance_id) ascending order; after source, "
            "original pilot, and Q2 ranks 0-4, take exactly ranks 5-6 with no outcome, "
            "gold-patch, repository, parser, or image-availability filtering and no replacement."
        ),
        "fixtures": selected_rows,
        "checks": {
            "exact_ranks": [row["selection_rank"] for row in selected_rows] == [5, 6],
            "source_and_prior_pilot_disjoint": True,
            "gold_patch_content_absent": all("patch" not in row for row in selected_rows),
        },
        "credential_material_present": False,
    }
    fixture_file_sha = write_json(FIXTURES, fixtures_payload)
    treatment = json.loads(TREATMENTS.read_text(encoding="utf-8"))
    contract_payload = {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-P1-Q3-QUALIFICATION-20260830",
        "created_at_utc": utcnow(),
        "purpose": (
            "Prospectively qualify an official SWE-bench 5.0.2 parser expansion on fresh "
            "disjoint tasks; preserve Q2 as negative evidence and never treat Q3 as a retry."
        ),
        "bindings": {
            "prior_adjudication": str(PRIOR_ADJUDICATION.relative_to(ROOT)),
            "prior_adjudication_sha256": sha256_file(PRIOR_ADJUDICATION),
            "source_memory": str(SOURCE_MEMORY.relative_to(ROOT)),
            "source_memory_sha256": sha256_file(SOURCE_MEMORY),
            "treatment_manifest": str(TREATMENTS.relative_to(ROOT)),
            "treatment_manifest_sha256": sha256_file(TREATMENTS),
            "q3_fixtures": str(FIXTURES.relative_to(ROOT)),
            "q3_fixtures_sha256": fixture_file_sha,
            "image_manifests": manifest_receipts,
            "official_reasoningbank_commit": OFFICIAL_COMMIT,
            "swebench_wheel_sha256": SWEBENCH_WHEEL_SHA256,
            "official_parser_source": PARSER_SOURCE,
        },
        "selection": {
            "ranks": [5, 6],
            "instance_ids": [row["instance_id"] for row in selected_rows],
            "uses_task_outcome": False, "uses_gold_patch": False,
            "replacement_sampling": "forbidden", "automatic_retry": "forbidden",
        },
        "backend": {
            "base_url": BASE_URL, "model": MODEL, "behavior_temperature": 0.0,
            "max_output_tokens": "omitted", "seed": "omitted", "top_p": "omitted",
            "max_retries": MAX_RETRIES, "workers": 1,
            "step_limit": STEP_LIMIT,
            "environment_timeout_seconds": COMMAND_TIMEOUT_SECONDS,
        },
        "treatments": {
            "arms": list("ABCDE"),
            "treatment_sha256": {
                arm: treatment["arms"][arm]["treatment_sha256"] for arm in "ABCDE"
            },
            "ordered_execution": "rank 5 A/B/C/D/E then rank 6 A/B/C/D/E",
            "fresh_container_each_run": True, "session_reuse_across_arms": False,
        },
        "qualification": {
            "planned_runs": 10,
            "requires": [
                "all two images present by exact amd64 manifest digest",
                "all ten runs persisted once without replacement",
                "no provider, provider-identity, runtime, or implementation failure",
                "no blank model-visible message content",
                "all completed responses resolve to the exact frozen model",
                "valid SWE-bench evaluator output for every run",
                "official parser conformance for parse_log_sphinx and parse_log_django",
                "A/B and B/E selected memory plus first R1 request equal per task",
            ],
            "negative_task_outcome_does_not_fail_qualification": True,
            "pass_opens_only_a_separate_full-P1 planning gate": True,
            "full_p1_execution_authorized": False,
        },
        "runtime": {
            "base_state_rule": BASE_STATE_RULE, "pid_namespace": PID_NAMESPACE,
            "platform": "linux/amd64", "dataset_mirror": "hf-mirror.com",
            "image_mirror": "docker.1ms.run",
        },
        "outcome_discipline": {
            "old_ten_runs_immutable": True, "q2_runs_immutable": True,
            "failed_q2_runs_preserved": True,
            "parser_implementation_only_after_q3_preregistration": True,
            "no_parameter_or_task_change_after_any_q3_outcome": True,
        },
        "scientific_boundary": {
            "q3_task_outcome_observed": False, "full_population_authorized": False,
            "paper_result_claim_authorized": False,
        },
        "credential_material_present": False,
    }
    contract_file_sha = write_json(CONTRACT, contract_payload)
    return {
        "decision": "P1_Q3_QUALIFICATION_PREREGISTERED",
        "fixtures": str(FIXTURES.relative_to(ROOT)),
        "fixtures_file_sha256": fixture_file_sha,
        "contract": str(CONTRACT.relative_to(ROOT)),
        "contract_file_sha256": contract_file_sha,
        "instance_ids": contract_payload["selection"]["instance_ids"],
    }


def validate_existing() -> list[str]:
    errors = []
    fixture, contract = (
        json.loads(FIXTURES.read_text(encoding="utf-8")),
        json.loads(CONTRACT.read_text(encoding="utf-8")),
    )
    if [row["instance_id"] for row in fixture["fixtures"]] != [
        "sphinx-doc__sphinx-9230", "django__django-11880"
    ]:
        errors.append("Q3 fixture identities drift")
    if contract["selection"]["ranks"] != [5, 6]:
        errors.append("Q3 ranks drift")
    if contract["qualification"]["full_p1_execution_authorized"] is not False:
        errors.append("Q3 cannot authorize full P1 before execution")
    if contract["scientific_boundary"]["q3_task_outcome_observed"] is not False:
        errors.append("Q3 contract must remain pre-outcome")
    if contract["outcome_discipline"]["old_ten_runs_immutable"] is not True:
        errors.append("prior pilot immutability drift")
    if contract["outcome_discipline"]["q2_runs_immutable"] is not True:
        errors.append("Q2 immutability drift")
    if contract["bindings"]["swebench_wheel_sha256"] != SWEBENCH_WHEEL_SHA256:
        errors.append("SWE-bench parser source drift")
    if contract["bindings"]["q3_fixtures_sha256"] != sha256_file(FIXTURES):
        errors.append("Q3 fixture binding drift")
    return errors


if __name__ == "__main__":
    print(json.dumps(prepare(), ensure_ascii=False, sort_keys=True))
