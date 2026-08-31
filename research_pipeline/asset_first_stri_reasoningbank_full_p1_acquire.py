"""Acquire SHA-verified Full-P1 OCI blobs and import eight exact images."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from research_pipeline import asset_first_stri_swebench_aria2_acquire as aria
from research_pipeline import asset_first_stri_swebench_oci_import as oci
from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT,
    sha256_file,
    utcnow,
    write_json,
)

POPULATION = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-population-and-image-freeze-20260831.json"
PREREGISTRATION = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-behavioral-propagation-preregistration-20260831.json"
OUTPUT = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-runtime-acquisition-result-20260831.json"
LAYOUT_ROOT = Path("/data/wyt/e1-stri-reasoningbank-runtime/full-p1-oci-layouts")
EXPECTED_POPULATION_SHA256 = "6ca2a6831e01db63961db3d5c337c17ee790755046c68bbcb6c056e136d8bbe8"
EXPECTED_PREREGISTRATION_SHA256 = "af8e9efb53ad5df5e846329b289ce791bc8ffe7c581f810c0ade1067d09fe7dd"


def load_population() -> list[dict[str, Any]]:
    if sha256_file(POPULATION) != EXPECTED_POPULATION_SHA256:
        raise RuntimeError("Full-P1 population artifact SHA drift")
    if sha256_file(PREREGISTRATION) != EXPECTED_PREREGISTRATION_SHA256:
        raise RuntimeError("Full-P1 preregistration SHA drift")
    document = json.loads(POPULATION.read_text(encoding="utf-8"))
    if document["decision"] != "FULL_P1_FRESH_POPULATION_AND_IMAGES_FROZEN":
        raise RuntimeError("Full-P1 population is not frozen")
    if len(document["population"]) != 8:
        raise RuntimeError("Full-P1 population count drift")
    return document["population"]


def specs(population: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for item in population:
        manifest = ROOT / item["manifest_path"]
        digest = item["image_amd64_manifest_digest"].removeprefix("sha256:")
        if sha256_file(manifest) != digest:
            raise RuntimeError(f"manifest SHA drift for {item['instance_id']}")
        mirror_repo = item["image_mirror_tag"].removesuffix(":latest")
        download_repo = mirror_repo.removeprefix("docker.1ms.run/")
        rows.append({
            "label": f"rank-{item['selection_rank']:03d}",
            "selection_rank": item["selection_rank"],
            "instance_id": item["instance_id"],
            "download_repo": download_repo,
            "repo": mirror_repo,
            "tag": f"e1fullp1fixed-{digest[:12]}",
            "manifest": manifest,
            "digest": digest,
        })
    return rows


def descriptors(image_specs: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for spec in image_specs:
        manifest = json.loads(spec["manifest"].read_text(encoding="utf-8"))
        for item in [manifest["config"], *manifest["layers"]]:
            row = {"size": int(item["size"]), "repo": spec["download_repo"]}
            if item["digest"] in result and result[item["digest"]]["size"] != row["size"]:
                raise RuntimeError("shared Full-P1 blob size drift")
            result.setdefault(item["digest"], row)
    return result


def safe_import(row: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    inspect_output = ((row.get("inspect") or {}).get("output") or "")
    return {
        "selection_rank": spec["selection_rank"],
        "instance_id": spec["instance_id"],
        "label": row.get("label"),
        "digest_ref": row.get("digest_ref"),
        "status": row.get("status"),
        "pass": row.get("pass"),
        "archive": row.get("archive"),
        "archive_sha256": row.get("archive_sha256"),
        "inspect_output": inspect_output,
        "exact_manifest_digest_visible": (
            "sha256:" + spec["digest"] in inspect_output
        ),
        "architecture_amd64_visible": "amd64" in inspect_output,
    }


def run(output: Path = OUTPUT) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError("refusing to overwrite immutable Full-P1 acquisition result")
    population = load_population()
    image_specs = specs(population)
    blobs = descriptors(image_specs)
    downloads: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {
            pool.submit(aria.acquire_one, digest, row["size"], row["repo"]): digest
            for digest, row in blobs.items()
        }
        for future in as_completed(futures):
            digest = futures[future]
            try:
                row = future.result()
                receipt = {
                    "digest": digest,
                    "size": row["size"],
                    "status": row["status"],
                    "sha256_verified": True,
                }
                downloads.append(receipt)
                print(json.dumps(receipt, sort_keys=True), flush=True)
            except Exception as error:
                receipt = {
                    "stage": "blob_acquisition",
                    "digest": digest,
                    "error_type": type(error).__name__,
                    "message": str(error),
                }
                failures.append(receipt)
                print(json.dumps(receipt, sort_keys=True), flush=True)
    imports: list[dict[str, Any]] = []
    if not failures:
        oci.LAYOUT_ROOT = LAYOUT_ROOT
        for spec in image_specs:
            try:
                row = oci.import_one(spec)
                receipt = safe_import(row, spec)
                imports.append(receipt)
                print(json.dumps(receipt, sort_keys=True), flush=True)
            except Exception as error:
                receipt = {
                    "stage": "image_import",
                    "selection_rank": spec["selection_rank"],
                    "instance_id": spec["instance_id"],
                    "error_type": type(error).__name__,
                    "message": str(error),
                }
                failures.append(receipt)
                print(json.dumps(receipt, sort_keys=True), flush=True)
                break
    all_downloads = not failures and len(downloads) == len(blobs)
    all_imports = (
        not failures
        and len(imports) == len(image_specs)
        and all(
            row["pass"]
            and row["exact_manifest_digest_visible"]
            and row["architecture_amd64_visible"]
            for row in imports
        )
    )
    payload = {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-FULL-P1-RUNTIME-ACQUISITION-20260831",
        "created_at_utc": utcnow(),
        "mirror": "docker.1ms.run",
        "population_artifact": str(POPULATION.relative_to(ROOT)),
        "population_artifact_sha256": sha256_file(POPULATION),
        "preregistration_artifact": str(PREREGISTRATION.relative_to(ROOT)),
        "preregistration_artifact_sha256": sha256_file(PREREGISTRATION),
        "image_count": len(image_specs),
        "unique_blob_count": len(blobs),
        "unique_blob_bytes": sum(row["size"] for row in blobs.values()),
        "blob_workers": 2,
        "download_rows": sorted(downloads, key=lambda row: row["digest"]),
        "import_rows": imports,
        "failures": failures,
        "all_blobs_sha256_verified": all_downloads,
        "all_images_imported_by_exact_digest": all_imports,
        "decision": (
            "FULL_P1_EXACT_IMAGES_READY"
            if all_downloads and all_imports
            else "FULL_P1_IMAGE_ACQUISITION_HOLD"
        ),
        "failure_policy": {
            "no_task_replacement": True,
            "no_scientific_run_started": True,
            "failed_acquisition_requires_separate_authority": True,
        },
        "scientific_boundary": {
            "task_outcomes_observed": False,
            "model_calls": 0,
            "behavioral_execution_authorized": False,
        },
        "credential_material_present": False,
    }
    file_sha = write_json(output, payload)
    return {
        "decision": payload["decision"],
        "file_sha256": file_sha,
        "image_count": len(imports),
        "failure_count": len(failures),
    }


def main() -> None:
    print(json.dumps(run(), sort_keys=True))


if __name__ == "__main__":
    main()
