"""Execute the prospectively authorized one-channel Full-P1 acquisition repair."""

from __future__ import annotations

import json
import subprocess
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

CONTRACT = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-acquisition-repair-contract-20260831.json"
POPULATION = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-population-and-image-freeze-20260831.json"
OUTPUT = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-runtime-acquisition-repair-result-20260831.json"
LAYOUT_ROOT = Path("/data/wyt/e1-stri-reasoningbank-runtime/full-p1-oci-layouts")
EXPECTED_CONTRACT_SHA256 = "f9794dd404ab9e8f16495156a0f8f6d4e99e941013e1c28eee368e540ddf3779"
EXPECTED_POPULATION_SHA256 = "6ca2a6831e01db63961db3d5c337c17ee790755046c68bbcb6c056e136d8bbe8"
MISSING_DIGEST = "sha256:90046bcf0aab9c523973ff07859cb84058dbaac249b5d3b77122aaacd56e73bc"
MISSING_SIZE = 103_220_401
SOURCE_URL = (
    "https://docker.1panel.live/v2/"
    "swebench/sweb.eval.x86_64.django_1776_django-15695/blobs/"
    + MISSING_DIGEST
)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def image_specs(population: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for item in population:
        digest = item["image_amd64_manifest_digest"].removeprefix("sha256:")
        rows.append({
            "label": f"rank-{item['selection_rank']:03d}",
            "selection_rank": item["selection_rank"],
            "instance_id": item["instance_id"],
            "repo": item["image_mirror_tag"].removesuffix(":latest"),
            "tag": f"e1fullp1fixed-{digest[:12]}",
            "manifest": ROOT / item["manifest_path"],
            "digest": digest,
        })
    return rows


def descriptors(specs: list[dict[str, Any]]) -> dict[str, int]:
    result = {}
    for spec in specs:
        if sha256_file(spec["manifest"]) != spec["digest"]:
            raise RuntimeError(f"manifest drift for {spec['instance_id']}")
        manifest = load(spec["manifest"])
        for item in [manifest["config"], *manifest["layers"]]:
            size = int(item["size"])
            if item["digest"] in result and result[item["digest"]] != size:
                raise RuntimeError("shared descriptor size drift")
            result[item["digest"]] = size
    return result


def acquire_missing() -> dict[str, Any]:
    aria.CACHE.mkdir(parents=True, exist_ok=True)
    target = aria.CACHE / MISSING_DIGEST.removeprefix("sha256:")
    if (
        target.exists()
        and target.stat().st_size == MISSING_SIZE
        and aria.file_digest(target) == MISSING_DIGEST.removeprefix("sha256:")
    ):
        return {
            "digest": MISSING_DIGEST,
            "size": MISSING_SIZE,
            "status": "verified-existing-from-authorized-repair-channel",
            "sha256_verified": True,
        }
    partial = target.with_suffix(".repair.part")
    command = [
        "aria2c",
        "--continue=true",
        "--allow-overwrite=true",
        "--auto-file-renaming=false",
        "--file-allocation=none",
        "--max-connection-per-server=8",
        "--split=8",
        "--min-split-size=4M",
        "--connect-timeout=10",
        "--timeout=20",
        "--max-tries=10",
        "--retry-wait=2",
        "--console-log-level=warn",
        "--dir",
        str(aria.CACHE),
        "--out",
        partial.name,
        SOURCE_URL,
    ]
    completed = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=1800,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"authorized mirror repair download failed: {completed.stdout[-1200:]}")
    if partial.stat().st_size != MISSING_SIZE:
        raise RuntimeError("authorized mirror repair size mismatch")
    actual = aria.file_digest(partial)
    if actual != MISSING_DIGEST.removeprefix("sha256:"):
        raise RuntimeError(f"authorized mirror repair SHA mismatch: {actual}")
    partial.replace(target)
    return {
        "digest": MISSING_DIGEST,
        "size": MISSING_SIZE,
        "status": "downloaded-from-docker.1panel.live-and-verified",
        "sha256_verified": True,
    }


def safe_import(row: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    inspect_output = ((row.get("inspect") or {}).get("output") or "")
    return {
        "selection_rank": spec["selection_rank"],
        "instance_id": spec["instance_id"],
        "digest_ref": row.get("digest_ref"),
        "status": row.get("status"),
        "pass": row.get("pass"),
        "archive": row.get("archive"),
        "archive_sha256": row.get("archive_sha256"),
        "inspect_output": inspect_output,
        "exact_manifest_digest_visible": "sha256:" + spec["digest"] in inspect_output,
        "architecture_amd64_visible": "amd64" in inspect_output,
    }


def run(output: Path = OUTPUT) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError("refusing duplicate Full-P1 acquisition repair")
    if sha256_file(CONTRACT) != EXPECTED_CONTRACT_SHA256:
        raise RuntimeError("Full-P1 acquisition repair contract SHA drift")
    if sha256_file(POPULATION) != EXPECTED_POPULATION_SHA256:
        raise RuntimeError("Full-P1 population SHA drift")
    contract = load(CONTRACT)
    if contract["decision"] != "FULL_P1_ACQUISITION_SINGLE_VARIABLE_REPAIR_AUTHORIZED":
        raise RuntimeError("Full-P1 acquisition repair is unauthorized")
    population = load(POPULATION)["population"]
    specs = image_specs(population)
    blob_sizes = descriptors(specs)
    if blob_sizes.get(MISSING_DIGEST) != MISSING_SIZE or len(blob_sizes) != 40:
        raise RuntimeError("Full-P1 repair descriptor set drift")
    failures = []
    repair_receipt = None
    try:
        repair_receipt = acquire_missing()
    except Exception as error:
        failures.append({
            "stage": "single_blob_channel_repair",
            "digest": MISSING_DIGEST,
            "error_type": type(error).__name__,
            "message": str(error),
        })
    verified = []
    if not failures:
        for digest, size in sorted(blob_sizes.items()):
            path = aria.CACHE / digest.removeprefix("sha256:")
            actual = aria.file_digest(path) if path.exists() and path.stat().st_size == size else None
            row = {
                "digest": digest,
                "size": size,
                "actual_sha256": actual,
                "pass": actual == digest.removeprefix("sha256:"),
            }
            verified.append(row)
            if not row["pass"]:
                failures.append({
                    "stage": "all_descriptor_reverification",
                    "digest": digest,
                    "error_type": "DigestVerificationError",
                    "message": "frozen descriptor absent, wrong size, or SHA mismatch",
                })
                break
    imports = []
    if not failures:
        oci.LAYOUT_ROOT = LAYOUT_ROOT
        for spec in specs:
            try:
                row = oci.import_one(spec)
                receipt = safe_import(row, spec)
                imports.append(receipt)
                print(json.dumps(receipt, sort_keys=True), flush=True)
            except Exception as error:
                failures.append({
                    "stage": "exact_image_import",
                    "selection_rank": spec["selection_rank"],
                    "instance_id": spec["instance_id"],
                    "error_type": type(error).__name__,
                    "message": str(error),
                })
                break
    all_verified = len(verified) == 40 and all(row["pass"] for row in verified)
    all_imported = (
        len(imports) == 8
        and all(
            row["pass"]
            and row["exact_manifest_digest_visible"]
            and row["architecture_amd64_visible"]
            for row in imports
        )
    )
    passed = not failures and all_verified and all_imported
    payload = {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-FULL-P1-ACQUISITION-REPAIR-RESULT-20260831",
        "created_at_utc": utcnow(),
        "decision": (
            "FULL_P1_EXACT_IMAGES_READY_AFTER_SINGLE_CHANNEL_REPAIR"
            if passed
            else "FULL_P1_ACQUISITION_REPAIR_HOLD"
        ),
        "contract": str(CONTRACT.relative_to(ROOT)),
        "contract_sha256": sha256_file(CONTRACT),
        "single_changed_variable": contract["single_changed_variable"],
        "repair_receipt": repair_receipt,
        "unique_blob_count": len(blob_sizes),
        "unique_blob_bytes": sum(blob_sizes.values()),
        "all_descriptor_rows": verified,
        "all_blobs_sha256_verified": all_verified,
        "import_rows": imports,
        "all_images_imported_by_exact_digest": all_imported,
        "runtime_image_references": {
            row["instance_id"]: row["digest_ref"] for row in imports
        },
        "failures": failures,
        "scientific_boundary": {
            "task_outcomes_observed": False,
            "model_calls": 0,
            "evaluator_calls": 0,
            "behavioral_execution_authorized": False,
        },
        "credential_material_present": False,
    }
    return {
        "decision": payload["decision"],
        "file_sha256": write_json(output, payload),
        "image_count": len(imports),
        "failure_count": len(failures),
    }


def main() -> None:
    print(json.dumps(run(), sort_keys=True))


if __name__ == "__main__":
    main()
