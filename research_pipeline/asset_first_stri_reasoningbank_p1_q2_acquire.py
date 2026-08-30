"""Acquire and import the two SHA-frozen Q2 images."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from research_pipeline import asset_first_stri_swebench_aria2_acquire as aria
from research_pipeline import asset_first_stri_swebench_oci_import as oci
from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT, sha256_file, utcnow, write_json,
)

MANIFEST_DIR = ROOT / "generated/asset-first-stri-reasoningbank-p1-q2-image-manifests-20260830"
OUTPUT = ROOT / "generated/asset-first-stri-reasoningbank-p1-q2-runtime-acquisition-result-20260830.json"
LAYOUT_ROOT = Path("/data/wyt/e1-stri-reasoningbank-runtime/q2-oci-layouts")
SPECS = (
    {
        "label": "django16100",
        "download_repo": "swebench/sweb.eval.x86_64.django_1776_django-16100",
        "repo": "docker.1ms.run/swebench/sweb.eval.x86_64.django_1776_django-16100",
        "tag": "e1q2fixed-07524a70",
        "manifest": MANIFEST_DIR / "django16100-amd64.json",
        "digest": "07524a702c042e0baa5725c35e2e1ae8c8f50a221682b5bf21ff26438fc46fdd",
    },
    {
        "label": "sympy18211",
        "download_repo": "swebench/sweb.eval.x86_64.sympy_1776_sympy-18211",
        "repo": "docker.1ms.run/swebench/sweb.eval.x86_64.sympy_1776_sympy-18211",
        "tag": "e1q2fixed-c92da16c",
        "manifest": MANIFEST_DIR / "sympy18211-amd64.json",
        "digest": "c92da16cfc8ba1c304c3fd0bf991aba569cc5eaa99a85fb3953c60f09de2c7ca",
    },
)


def descriptors() -> dict[str, dict[str, Any]]:
    result = {}
    for spec in SPECS:
        if sha256_file(spec["manifest"]) != spec["digest"]:
            raise RuntimeError(f"{spec['label']} manifest digest drift")
        manifest = json.loads(spec["manifest"].read_text(encoding="utf-8"))
        for item in [manifest["config"], *manifest["layers"]]:
            row = {"size": int(item["size"]), "repo": spec["download_repo"]}
            if item["digest"] in result and result[item["digest"]]["size"] != row["size"]:
                raise RuntimeError("shared blob size drift")
            result.setdefault(item["digest"], row)
    return result


def safe_import(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "label": row.get("label"), "digest_ref": row.get("digest_ref"),
        "status": row.get("status"), "pass": row.get("pass"),
        "archive": row.get("archive"), "archive_sha256": row.get("archive_sha256"),
        "inspect_output": ((row.get("inspect") or {}).get("output") or ""),
    }


def run() -> dict[str, Any]:
    blobs = descriptors()
    downloads, failures = [], []
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {
            pool.submit(aria.acquire_one, digest, row["size"], row["repo"]): digest
            for digest, row in blobs.items()
        }
        for future in as_completed(futures):
            digest = futures[future]
            try:
                row = future.result()
                downloads.append({
                    "digest": digest, "size": row["size"], "status": row["status"]
                })
                print(json.dumps(downloads[-1], sort_keys=True), flush=True)
            except Exception as error:
                failures.append({
                    "stage": "blob_acquisition", "digest": digest,
                    "error_type": type(error).__name__, "message": str(error),
                })
                print(json.dumps(failures[-1], sort_keys=True), flush=True)
    imports = []
    if not failures:
        oci.LAYOUT_ROOT = LAYOUT_ROOT
        for spec in SPECS:
            try:
                row = oci.import_one({
                    "label": spec["label"], "repo": spec["repo"], "tag": spec["tag"],
                    "manifest": spec["manifest"], "digest": spec["digest"],
                })
                imports.append(safe_import(row))
                print(json.dumps(imports[-1], sort_keys=True), flush=True)
            except Exception as error:
                failures.append({
                    "stage": "image_import", "label": spec["label"],
                    "error_type": type(error).__name__, "message": str(error),
                })
                print(json.dumps(failures[-1], sort_keys=True), flush=True)
                break
    passed = (
        not failures and len(downloads) == len(blobs)
        and len(imports) == len(SPECS) and all(row["pass"] for row in imports)
    )
    payload = {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-P1-Q2-ACQUISITION-20260830",
        "created_at_utc": utcnow(), "mirror": "docker.1ms.run",
        "manifest_bindings": [
            {
                "label": spec["label"],
                "manifest": str(spec["manifest"].relative_to(ROOT)),
                "manifest_sha256": "sha256:" + sha256_file(spec["manifest"]),
            }
            for spec in SPECS
        ],
        "unique_blob_count": len(blobs),
        "unique_blob_bytes": sum(row["size"] for row in blobs.values()),
        "download_rows": sorted(downloads, key=lambda row: row["digest"]),
        "import_rows": imports, "failures": failures,
        "all_blobs_sha256_verified": not failures and len(downloads) == len(blobs),
        "all_images_imported_by_exact_digest": passed,
        "decision": "P1_Q2_FIXED_IMAGES_READY" if passed else "P1_Q2_IMAGE_ACQUISITION_HOLD",
        "credential_material_present": False,
        "scientific_boundary": {"q2_task_outcome_observed": False},
    }
    file_sha = write_json(OUTPUT, payload)
    return {
        "decision": payload["decision"], "output": str(OUTPUT.relative_to(ROOT)),
        "file_sha256": file_sha, "failure_count": len(failures),
    }


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
