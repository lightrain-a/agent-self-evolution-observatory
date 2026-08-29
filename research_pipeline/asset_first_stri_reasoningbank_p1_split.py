#!/usr/bin/env python3
"""Freeze the outcome-independent SWE-bench source/evaluation split for E1 P1."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq


DATASET_ID = "SWE-bench/SWE-bench_Verified"
DATASET_REVISION = "78f471bf655a3137b2e8a75af1501690ec009ec3"
PARQUET_SHA256 = "030cfd7f2a704c4c0226e7f104c725a3b41230b1d3517f9c915ad7ea5be3fa25"
DEFAULT_DATASET = Path(
    "/data/wyt/agent-self-evolution-observatory/external/"
    "stri-swebench-verified-78f471bf655a3137b2e8a75af1501690ec009ec3/"
    "data/test-00000-of-00001.parquet"
)
DEFAULT_OUTPUT = Path(
    "generated/asset-first-stri-reasoningbank-p1-source-eval-split-20260829.json"
)
IMAGE_DIGESTS = {
    "sympy__sympy-13798": {
        "index_digest": "sha256:c4a643ffd7be41525c113d0fb9a1c1e8d655e4cca30def373fbac04188cc91f1",
        "amd64_manifest_digest": "sha256:4111da8b069bc23cc67ef24f2f433f82601518941052faebd3c4a621d3748cd6",
    },
    "pytest-dev__pytest-5631": {
        "index_digest": "sha256:c76510e12a1765211e064f6e8de09e51ac0f7839f60d72305b374e004308b6a1",
        "amd64_manifest_digest": "sha256:22a1a81b8e937a1ff52cef4f38bf59e6a8baa0648ef3b115e6206bfc5c5de68f",
    },
    "sympy__sympy-17318": {
        "index_digest": "sha256:dac5e27382a309b8dd1e6bc6aa4fe4dc3cb8c8384c6d5d516ea4c18e08fa06fd",
        "amd64_manifest_digest": "sha256:4d18e6a31fb1d68a8232f3c78a5a4c97e9c7a2d001765dcc90f228cef4b4e39f",
    },
}


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


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        normalize(value), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def receipt(row: dict[str, Any], rank: int, role: str) -> dict[str, Any]:
    instance_id = str(row["instance_id"])
    visible = {
        "instance_id": instance_id,
        "problem_statement": row["problem_statement"],
        "base_commit": row["base_commit"],
        "repo": row["repo"],
        "version": row["version"],
        "image": row["image"],
    }
    image = IMAGE_DIGESTS[instance_id]
    return {
        "role": role,
        "sha256_rank": rank,
        "instance_id": instance_id,
        "instance_id_sha256": sha256_bytes(instance_id.encode("utf-8")),
        "full_dataset_record_sha256": sha256_bytes(canonical_bytes(row)),
        "model_visible_task_fields_sha256": sha256_bytes(canonical_bytes(visible)),
        "repo": row["repo"],
        "base_commit": row["base_commit"],
        "environment_setup_commit": row["environment_setup_commit"],
        "image_tag_from_dataset": row["image"],
        "image_index_digest": image["index_digest"],
        "image_amd64_manifest_digest": image["amd64_manifest_digest"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    actual_sha = sha256_file(args.dataset)
    if actual_sha != PARQUET_SHA256:
        raise SystemExit(
            f"dataset SHA-256 mismatch: expected {PARQUET_SHA256}, got {actual_sha}"
        )
    rows = pq.read_table(args.dataset).to_pylist()
    if len(rows) != 500:
        raise SystemExit(f"expected 500 rows, got {len(rows)}")
    ranked = sorted(
        rows,
        key=lambda row: (
            sha256_bytes(str(row["instance_id"]).encode("utf-8")),
            str(row["instance_id"]),
        ),
    )
    source = [receipt(ranked[0], 0, "source_induction")]
    pilot = [
        receipt(row, rank, "held_out_pilot_evaluation")
        for rank, row in enumerate(ranked[1:3], start=1)
    ]
    source_ids = {row["instance_id"] for row in source}
    eval_ids = {row["instance_id"] for row in pilot}
    output = {
        "schema_version": 1,
        "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "experiment_id": "E1-STRI-REASONINGBANK-P1-SPLIT-20260829",
        "dataset": {
            "id": DATASET_ID,
            "revision": DATASET_REVISION,
            "parquet_sha256": PARQUET_SHA256,
            "row_count": len(rows),
            "split": "test",
            "subset": "verified",
            "download_channel": "hf-mirror.com fixed revision",
            "official_identity": "SWE-bench Verified",
        },
        "selection_rule": {
            "definition": (
                "Sort all 500 instance IDs by SHA-256(instance_id) ascending, break "
                "the impossible hash tie by instance_id ascending; rank 0 is the sole "
                "source case and ranks 1-2 are the held-out minimal-pilot cases."
            ),
            "uses_task_outcome": False,
            "uses_gold_patch": False,
            "replacement_sampling": "forbidden",
            "failed_source_policy": (
                "Preserve the failed source artifact and do not replace the source case."
            ),
            "failed_evaluation_policy": (
                "Preserve every failed arm/case artifact and do not replace the case."
            ),
        },
        "source_cases": source,
        "held_out_pilot_cases": pilot,
        "checks": {
            "source_eval_disjoint": source_ids.isdisjoint(eval_ids),
            "source_count": len(source),
            "pilot_eval_count": len(pilot),
            "all_image_digests_frozen": all(
                row["image_amd64_manifest_digest"].startswith("sha256:")
                for row in source + pilot
            ),
        },
        "scientific_boundary": {
            "task_outcome_observed": False,
            "memory_induction_executed": False,
            "p1_behavior_executed": False,
            "full_population_authorized": False,
        },
    }
    if not all(
        [
            output["checks"]["source_eval_disjoint"],
            output["checks"]["all_image_digests_frozen"],
            output["checks"]["source_count"] == 1,
            output["checks"]["pilot_eval_count"] == 2,
        ]
    ):
        raise SystemExit("split invariant failed")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "source": [row["instance_id"] for row in source],
                "pilot": [row["instance_id"] for row in pilot],
                "output": str(args.output),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
