"""Prospective rootful-Docker runtime repair for Qwen STRI D0 only."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline import asset_first_stri_reasoningbank_p1_core as p1_core
from research_pipeline import asset_first_stri_swebench_oci_import as oci

ROOTFUL_DOCKER_HOST = "unix:///var/run/docker.sock"
CONTRACT = p1_core.ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-d0-rootful-runtime-repair-contract-20260901.json"
CONTRACT_SHA256 = "2d13126881bf2ce61f1bad23028e537504c578a8ce85816dbb78e0c7ad7da236"


def verify_contract() -> dict[str, Any]:
    if p1_core.sha256_file(CONTRACT) != CONTRACT_SHA256:
        raise RuntimeError("D0 rootful runtime repair contract SHA drift")
    document = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if document.get("decision") != "D0_ROOTFUL_DOCKER_RUNTIME_REPAIR_PREREGISTERED":
        raise RuntimeError("D0 rootful runtime repair decision drift")
    repair = document.get("single_variable_repair") or {}
    if repair.get("after") != ROOTFUL_DOCKER_HOST:
        raise RuntimeError("D0 rootful Docker host drift")
    if any(
        repair.get(key) is not False
        for key in (
            "candidate_schedule_changed",
            "task_identity_changed",
            "task_order_changed",
            "image_manifest_changed",
            "image_digest_changed",
            "architecture_changed",
            "base_commit_changed",
            "gold_patch_changed",
            "test_patch_changed",
            "evaluator_changed",
            "parser_changed",
            "qualification_rule_changed",
        )
    ):
        raise RuntimeError("D0 rootful repair changes scientific/evaluator inputs")
    if repair.get("model_calls") != 0 or repair.get("provider_calls") != 0:
        raise RuntimeError("D0 rootful repair cannot authorize model/provider calls")
    return document


def activate() -> dict[str, str]:
    """Bind D0/Q10 helper calls and OCI import to the preregistered rootful daemon."""
    verify_contract()
    p1_core.DOCKER_HOST = ROOTFUL_DOCKER_HOST
    oci.DOCKER_HOST = ROOTFUL_DOCKER_HOST
    return {
        "docker_host": ROOTFUL_DOCKER_HOST,
        "repair_contract_sha256": CONTRACT_SHA256,
    }
