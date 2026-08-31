"""Freeze fresh Full-P1 ranks and exact amd64 OCI manifests without outcomes."""

from __future__ import annotations

import base64
import hashlib
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT, canonical_json, sha256_file, sha256_text, utcnow, write_json,
)

DATASET = Path(
    "/data/wyt/agent-self-evolution-observatory/external/"
    "stri-swebench-verified-78f471bf655a3137b2e8a75af1501690ec009ec3/"
    "data/test-00000-of-00001.parquet"
)
DATASET_REVISION = "78f471bf655a3137b2e8a75af1501690ec009ec3"
DATASET_SHA256 = "030cfd7f2a704c4c0226e7f104c725a3b41230b1d3517f9c915ad7ea5be3fa25"
START_RANK = 7
TASK_COUNT = 8
ELIGIBLE_PARSERS = {"parse_log_django", "parse_log_sphinx"}
MANIFEST_DIR = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-image-manifests-20260831"
OUTPUT = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-population-and-image-freeze-20260831.json"


def normalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): normalize(child) for key, child in sorted(value.items())}
    if isinstance(value, (list, tuple)):
        return [normalize(child) for child in value]
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return value


def ranked_rows() -> list[tuple[int, dict[str, Any]]]:
    if sha256_file(DATASET) != DATASET_SHA256:
        raise RuntimeError("Full-P1 dataset SHA drift")
    rows = pq.read_table(DATASET).to_pylist()
    if len(rows) != 500:
        raise RuntimeError("Full-P1 dataset row count drift")
    ranked = sorted(
        rows,
        key=lambda row: (
            sha256_text(str(row["instance_id"])),
            str(row["instance_id"]),
        ),
    )
    selected = [
        (rank, row)
        for rank, row in enumerate(ranked)
        if rank >= START_RANK and row["log_parser"] in ELIGIBLE_PARSERS
    ][:TASK_COUNT]
    if len(selected) != TASK_COUNT:
        raise RuntimeError("insufficient Full-P1 eligible fresh population")
    expected = [7, 8, 9, 11, 12, 13, 14, 19]
    if [rank for rank, _ in selected] != expected:
        raise RuntimeError("Full-P1 deterministic population selection drift")
    return selected


def fixture(rank: int, row: dict[str, Any]) -> dict[str, Any]:
    model_visible = {
        "instance_id": row["instance_id"],
        "problem_statement": row["problem_statement"],
        "base_commit": row["base_commit"],
        "repo": row["repo"],
        "version": row["version"],
    }
    evaluator_only = {
        "eval_type": row["eval_type"],
        "eval_script": row["eval_script"],
        "log_parser": row["log_parser"],
        "FAIL_TO_PASS": row["FAIL_TO_PASS"],
        "PASS_TO_PASS": row["PASS_TO_PASS"],
        "test_patch": row["test_patch"],
    }
    payload = {
        "selection_rank": rank,
        "instance_id": row["instance_id"],
        "model_visible": normalize(model_visible),
        "evaluator_only": normalize(evaluator_only),
        "gold_patch_sha256": sha256_text(str(row["patch"])),
        "full_public_record_sha256": sha256_text(canonical_json(normalize(row))),
        "model_visible_task_sha256": sha256_text(canonical_json(normalize(model_visible))),
        "evaluator_fixture_sha256": sha256_text(canonical_json(normalize(evaluator_only))),
        "image_tag": row["image"],
        "visibility_invariant": {
            "evaluator_only_fields_never_enter_model_messages": True,
            "gold_patch_content_persisted": False,
        },
    }
    return payload


def fetch_manifest(fixture_row: dict[str, Any]) -> tuple[dict[str, Any], bytes]:
    image_tag = str(fixture_row["image_tag"])
    mirror_tag = "docker.1ms.run/" + image_tag
    completed = subprocess.run(
        ["docker", "manifest", "inspect", "--verbose", mirror_tag],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=300,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"manifest query failed for {fixture_row['instance_id']}: "
            f"{completed.stdout[-800:]}"
        )
    records = json.loads(completed.stdout)
    if isinstance(records, dict):
        records = [records]
    matches = [
        row for row in records
        if (row.get("Descriptor") or {}).get("platform", {}).get("architecture") == "amd64"
        and (row.get("Descriptor") or {}).get("platform", {}).get("os") == "linux"
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"expected one linux/amd64 manifest for {fixture_row['instance_id']}"
        )
    selected = matches[0]
    descriptor = selected["Descriptor"]
    raw = base64.b64decode(selected["Raw"])
    actual = "sha256:" + hashlib.sha256(raw).hexdigest()
    if actual != descriptor["digest"]:
        raise RuntimeError(f"manifest digest mismatch for {fixture_row['instance_id']}")
    manifest = json.loads(raw)
    if manifest.get("schemaVersion") != 2:
        raise RuntimeError("unexpected OCI manifest schema")
    return {
        "image_mirror_tag": mirror_tag,
        "image_amd64_manifest_digest": actual,
        "manifest_media_type": descriptor["mediaType"],
        "manifest_size": descriptor["size"],
        "image_pull_reference": mirror_tag.rsplit(":latest", 1)[0] + "@" + actual,
        "config_digest": manifest["config"]["digest"],
        "layer_count": len(manifest["layers"]),
        "layer_bytes": sum(int(row["size"]) for row in manifest["layers"]),
    }, raw


def freeze(output: Path = OUTPUT) -> dict[str, Any]:
    if output.exists() or MANIFEST_DIR.exists():
        raise RuntimeError("refusing to overwrite immutable Full-P1 population/image freeze")
    selected = [(rank, fixture(rank, row)) for rank, row in ranked_rows()]
    results: dict[str, tuple[dict[str, Any], bytes]] = {}
    failures = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {
            pool.submit(fetch_manifest, row): (rank, row)
            for rank, row in selected
        }
        for future in as_completed(futures):
            rank, row = futures[future]
            try:
                results[row["instance_id"]] = future.result()
            except Exception as error:
                failures.append({
                    "selection_rank": rank,
                    "instance_id": row["instance_id"],
                    "error_type": type(error).__name__,
                    "message": str(error),
                })
    if failures:
        payload = {
            "schema_version": 1,
            "experiment_id": "E1-STRI-REASONINGBANK-FULL-P1-POPULATION-IMAGE-FREEZE-20260831",
            "created_at_utc": utcnow(),
            "decision": "FULL_P1_POPULATION_IMAGE_FREEZE_HOLD",
            "failures": sorted(failures, key=lambda row: row["selection_rank"]),
            "task_outcomes_observed": False,
            "credential_material_present": False,
        }
        return {
            "decision": payload["decision"],
            "file_sha256": write_json(output, payload),
            "failure_count": len(failures),
        }
    MANIFEST_DIR.mkdir(parents=True)
    population = []
    for rank, row in selected:
        image, raw = results[row["instance_id"]]
        label = row["instance_id"].replace("__", "-").replace("_", "-")
        manifest_path = MANIFEST_DIR / f"{rank:03d}-{label}-amd64.json"
        manifest_path.write_bytes(raw)
        if "sha256:" + sha256_file(manifest_path) != image["image_amd64_manifest_digest"]:
            raise RuntimeError("persisted manifest digest drift")
        item = dict(row)
        item.update(image)
        item["manifest_path"] = str(manifest_path.relative_to(ROOT))
        item["manifest_file_sha256"] = sha256_file(manifest_path)
        population.append(item)
    payload = {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-FULL-P1-POPULATION-IMAGE-FREEZE-20260831",
        "created_at_utc": utcnow(),
        "decision": "FULL_P1_FRESH_POPULATION_AND_IMAGES_FROZEN",
        "dataset": {
            "id": "SWE-bench/SWE-bench_Verified",
            "revision": DATASET_REVISION,
            "parquet_sha256": DATASET_SHA256,
            "row_count": 500,
            "download_channel": "hf-mirror.com fixed revision",
        },
        "selection_rule": {
            "definition": (
                "Starting at frozen SHA256(instance_id) rank 7, select the first "
                "eight previously unexposed cases whose parser family is one of "
                "the Q10-qualified parse_log_django or parse_log_sphinx families."
            ),
            "start_rank": START_RANK,
            "eligible_parsers": sorted(ELIGIBLE_PARSERS),
            "selected_ranks": [row["selection_rank"] for row in population],
            "uses_task_outcome": False,
            "uses_gold_patch": False,
            "no_replacement": True,
        },
        "task_count": TASK_COUNT,
        "population": population,
        "checks": {
            "task_count_exact": len(population) == TASK_COUNT,
            "rank_order_exact": [row["selection_rank"] for row in population]
            == [7, 8, 9, 11, 12, 13, 14, 19],
            "all_ids_unique": len({row["instance_id"] for row in population})
            == TASK_COUNT,
            "qualification_ids_excluded": not {
                "sphinx-doc__sphinx-9230", "django__django-11880"
            }.intersection(row["instance_id"] for row in population),
            "pilot_and_source_ids_excluded": not {
                "sympy__sympy-13798",
                "pytest-dev__pytest-5631",
                "sympy__sympy-17318",
            }.intersection(row["instance_id"] for row in population),
            "all_manifest_sha256_exact": all(
                row["manifest_file_sha256"]
                == row["image_amd64_manifest_digest"].removeprefix("sha256:")
                for row in population
            ),
            "gold_patch_content_absent": all(
                "patch" not in row for row in population
            ),
            "task_outcomes_unexposed": True,
        },
        "scientific_boundary": {
            "task_outcomes_observed": False,
            "behavioral_execution_authorized": False,
            "paper_claim_authorized": False,
        },
        "credential_material_present": False,
    }
    if not all(payload["checks"].values()):
        raise RuntimeError("Full-P1 population/image freeze invariant failed")
    return {
        "decision": payload["decision"],
        "file_sha256": write_json(output, payload),
        "failure_count": 0,
    }


def main() -> None:
    print(json.dumps(freeze(), sort_keys=True))


if __name__ == "__main__":
    main()
