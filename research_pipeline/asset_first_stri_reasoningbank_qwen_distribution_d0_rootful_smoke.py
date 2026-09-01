"""Non-scientific rootful-Docker smoke before resuming Qwen STRI D0 ordinal 117."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import ROOT, sha256_file, utcnow, write_json
from research_pipeline import asset_first_stri_reasoningbank_qwen_distribution_d0_qualify as d0
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_d0_rootful_runtime import (
    CONTRACT as REPAIR_CONTRACT,
    CONTRACT_SHA256,
    ROOTFUL_DOCKER_HOST,
    activate,
    verify_contract,
)

OUTPUT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-d0-rootful-runtime-smoke-20260901.json"
TARGET_ORDINAL = 117
TARGET_INSTANCE = "matplotlib__matplotlib-24026"


def smoke(output: Path = OUTPUT) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError("refusing to overwrite immutable D0 rootful runtime smoke")
    contract = verify_contract()
    parent_index = ROOT / contract["parent_index"]
    if sha256_file(parent_index) != contract["parent_index_sha256"]:
        raise RuntimeError("D0 rootful smoke parent index SHA drift")
    index = json.loads(parent_index.read_text(encoding="utf-8"))
    blocker = index.get("operational_blocker") or {}
    if (
        blocker.get("ordinal") != TARGET_ORDINAL
        or blocker.get("instance_id") != TARGET_INSTANCE
        or index.get("completed_qualification_count") != 49
    ):
        raise RuntimeError("D0 rootful smoke parent blocker/state drift")
    completed = d0.existing_receipts(d0.candidate_schedule())
    unit = d0.next_unit(d0.candidate_schedule(), completed)
    if not unit or unit["ordinal"] != TARGET_ORDINAL or unit["instance_id"] != TARGET_INSTANCE:
        raise RuntimeError("D0 rootful smoke next untouched unit drift")
    activate_receipt = activate()
    rows = d0.dataset_rows()
    manifest = d0.fetch_manifest(unit)
    image = d0.acquire_and_import(unit, manifest)
    container = d0.QualificationDockerRun(
        image=image["image_pull_reference"],
        base_commit=str(rows[TARGET_INSTANCE]["base_commit"]),
        run_id="qwen-d0-rootful-smoke-117-matplotlib-24026",
    )
    runtime: dict[str, Any] | None = None
    probe: dict[str, Any] | None = None
    cleanup: dict[str, Any] | None = None
    try:
        runtime = container.start()
        probe = container.exec(
            "uname -m && git rev-parse HEAD && test -z \"$(git status --porcelain=v1 --untracked-files=all)\"",
            timeout=30,
        )
    finally:
        cleanup = container.close()
    checks = {
        "repair_contract_exact": sha256_file(REPAIR_CONTRACT) == CONTRACT_SHA256,
        "rootful_docker_host_exact": activate_receipt["docker_host"] == ROOTFUL_DOCKER_HOST,
        "target_unit_exact": unit["ordinal"] == TARGET_ORDINAL and unit["instance_id"] == TARGET_INSTANCE,
        "exact_digest_visible": image["exact_digest_visible"] is True,
        "architecture_amd64_visible": image["architecture_amd64_visible"] is True,
        "runtime_started": bool(runtime),
        "base_commit_exact": bool(runtime) and runtime["base_commit_receipt"]["observed_head"].strip() == str(rows[TARGET_INSTANCE]["base_commit"]),
        "probe_pass": bool(probe) and probe["returncode"] == 0 and probe["timed_out"] is False and probe["output"].splitlines()[0].strip() in {"x86_64", "amd64"},
        "cleanup_accepted": bool(cleanup) and cleanup.get("accepted") is True,
        "gold_patch_not_applied": True,
        "evaluator_not_run": True,
        "model_calls_zero": True,
        "provider_calls_zero": True,
    }
    passed = all(checks.values())
    payload = {
        "schema_version": 1,
        "experiment_id": contract["experiment_id"],
        "created_at_utc": utcnow(),
        "stage": "NON_SCIENTIFIC_D0_ROOTFUL_RUNTIME_SMOKE",
        "decision": "D0_ROOTFUL_RUNTIME_SMOKE_PASS" if passed else "D0_ROOTFUL_RUNTIME_SMOKE_HOLD",
        "repair_contract": str(REPAIR_CONTRACT.relative_to(ROOT)),
        "repair_contract_sha256": CONTRACT_SHA256,
        "parent_index_sha256": contract["parent_index_sha256"],
        "target": {"ordinal": TARGET_ORDINAL, "instance_id": TARGET_INSTANCE},
        "docker_host": ROOTFUL_DOCKER_HOST,
        "image_runtime": image,
        "runtime_receipt": runtime,
        "probe_receipt": probe,
        "cleanup_receipt": cleanup,
        "checks": checks,
        "scientific_authority": False,
        "task_qualification_attempt_consumed": False,
        "gold_patch_model_visible": False,
        "behavioral_outcomes_observed": False,
        "model_calls": 0,
        "provider_calls": 0,
        "credential_material_present": False,
    }
    file_sha = write_json(output, payload)
    return {"decision": payload["decision"], "passed": passed, "file_sha256": file_sha}


if __name__ == "__main__":
    print(json.dumps(smoke(), sort_keys=True))
