#!/usr/bin/env python3
"""Extract content-addressed public SWE-bench fixtures for the frozen E1 P1 tasks."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq


PARQUET_SHA256 = "030cfd7f2a704c4c0226e7f104c725a3b41230b1d3517f9c915ad7ea5be3fa25"
DEFAULT_DATASET = Path(
    "/data/wyt/agent-self-evolution-observatory/external/"
    "stri-swebench-verified-78f471bf655a3137b2e8a75af1501690ec009ec3/"
    "data/test-00000-of-00001.parquet"
)
DEFAULT_SPLIT = Path(
    "generated/asset-first-stri-reasoningbank-p1-source-eval-split-20260829.json"
)
DEFAULT_OUTPUT = Path(
    "generated/asset-first-stri-reasoningbank-p1-task-fixtures-20260829.json"
)


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


def canonical(value: Any) -> str:
    return json.dumps(
        normalize(value), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )


def sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def fixture(row: dict[str, Any], role: str, image_digest: str) -> dict[str, Any]:
    full = normalize(row)
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
    return {
        "role": role,
        "instance_id": row["instance_id"],
        "model_visible": normalize(model_visible),
        "evaluator_only": normalize(evaluator_only),
        "gold_patch_sha256": sha(str(row["patch"])),
        "full_public_record_sha256": sha(canonical(full)),
        "image_tag": row["image"],
        "image_amd64_manifest_digest": image_digest,
        "image_pull_reference": (
            "docker.1ms.run/" + str(row["image"]).split(":latest", 1)[0] + "@" + image_digest
        ),
        "visibility_invariant": {
            "evaluator_only_fields_never_enter_model_messages": True,
            "gold_patch_content_persisted_in_fixture": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--split", type=Path, default=DEFAULT_SPLIT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if sha_file(args.dataset) != PARQUET_SHA256:
        raise SystemExit("dataset hash mismatch")
    split = json.loads(args.split.read_text(encoding="utf-8"))
    selected = split["source_cases"] + split["held_out_pilot_cases"]
    selected_by_id = {row["instance_id"]: row for row in selected}
    table = pq.read_table(args.dataset)
    rows = {str(row["instance_id"]): row for row in table.to_pylist()}
    fixtures = [
        fixture(
            rows[item["instance_id"]],
            item["role"],
            item["image_amd64_manifest_digest"],
        )
        for item in selected
    ]
    if {item["instance_id"] for item in fixtures} != set(selected_by_id):
        raise SystemExit("fixture selection mismatch")
    output = {
        "schema_version": 1,
        "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "experiment_id": "E1-STRI-REASONINGBANK-P1-FIXTURES-20260829",
        "dataset_revision": "78f471bf655a3137b2e8a75af1501690ec009ec3",
        "dataset_parquet_sha256": PARQUET_SHA256,
        "split_artifact": str(args.split),
        "split_artifact_sha256": sha_file(args.split),
        "fixtures": fixtures,
        "checks": {
            "fixture_count": len(fixtures),
            "all_selected_ids_exact": len(fixtures) == 3,
            "source_eval_disjoint": len({item["instance_id"] for item in fixtures}) == 3,
            "gold_patch_content_absent": all("patch" not in item for item in fixtures),
        },
        "scientific_boundary": {
            "task_outcome_observed": False,
            "memory_induction_executed": False,
            "p1_behavior_executed": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"fixtures": [x["instance_id"] for x in fixtures]}, sort_keys=True))


if __name__ == "__main__":
    main()
