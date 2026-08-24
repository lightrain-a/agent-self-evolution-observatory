#!/usr/bin/env python3
"""Content-address the prospective B1/L2B ReasoningBank writer model realization.

This is a support-only preflight. It does not issue a model generation request.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

EXPECTED_TAG = "qwen2.5:32b"
EXPECTED_FAMILY = "qwen2"
EXPECTED_PARAMETER_SIZE = "32.8B"
EXPECTED_QUANTIZATION = "Q4_K_M"
EXPECTED_MODEL_LAYER = "sha256:eabc98a9bcbfce7fd70f3e07de599f8fda98120fefed5881934161ede8bd1a41"
EXPECTED_MANIFEST = "sha256:9f13ba1299afea09d9a956fc6a85becc99115a6d596fae201a5487a03bdc4368"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_sha(obj: Any) -> str:
    return hashlib.sha256(
        json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def parse_manifest(manifest_path: Path, blobs_dir: Path, *, verify_blobs: bool = True) -> dict[str, Any]:
    raw = manifest_path.read_bytes()
    manifest = json.loads(raw)
    manifest_sha = hashlib.sha256(raw).hexdigest()
    if manifest_sha != EXPECTED_MANIFEST.removeprefix("sha256:"):
        raise RuntimeError(f"unexpected model manifest sha256: {manifest_sha}")

    layers = [manifest["config"], *manifest["layers"]]
    rows = []
    for layer in layers:
        digest = layer["digest"]
        if not digest.startswith("sha256:"):
            raise RuntimeError(f"non-sha256 layer digest: {digest}")
        blob = blobs_dir / digest.replace(":", "-")
        if not blob.is_file():
            raise RuntimeError(f"missing model blob: {digest}")
        actual_size = blob.stat().st_size
        if actual_size != int(layer["size"]):
            raise RuntimeError(f"blob size mismatch for {digest}: {actual_size} != {layer['size']}")
        actual_sha = sha256(blob) if verify_blobs else digest.removeprefix("sha256:")
        if actual_sha != digest.removeprefix("sha256:"):
            raise RuntimeError(f"blob sha256 mismatch for {digest}")
        rows.append(
            {
                "media_type": layer["mediaType"],
                "digest": digest,
                "size_bytes": actual_size,
                "sha256_verified": bool(verify_blobs),
            }
        )
    model_rows = [r for r in rows if r["media_type"] == "application/vnd.ollama.image.model"]
    if len(model_rows) != 1 or model_rows[0]["digest"] != EXPECTED_MODEL_LAYER:
        raise RuntimeError("unexpected Ollama model layer")
    return {"manifest_sha256": manifest_sha, "layers": rows}


def build_receipt(
    parent_r13: dict[str, Any],
    parent_r13_sha: str,
    parsed_manifest: dict[str, Any],
    show: dict[str, Any],
    show_sha: str,
    v1_models: dict[str, Any],
    v1_models_sha: str,
    ollama_version: str,
) -> dict[str, Any]:
    details = show.get("details", {})
    if details.get("family") != EXPECTED_FAMILY:
        raise RuntimeError(f"unexpected model family: {details.get('family')}")
    if details.get("parameter_size") != EXPECTED_PARAMETER_SIZE:
        raise RuntimeError(f"unexpected parameter size: {details.get('parameter_size')}")
    if details.get("quantization_level") != EXPECTED_QUANTIZATION:
        raise RuntimeError(f"unexpected quantization: {details.get('quantization_level')}")
    model_ids = [x.get("id") for x in v1_models.get("data", [])]
    if model_ids != [EXPECTED_TAG]:
        raise RuntimeError(f"unexpected OpenAI-compatible model registry: {model_ids}")
    if parent_r13["writer_contract"]["writer_model_family"] != "Qwen2.5-32B":
        raise RuntimeError("R13 writer model family drift")
    if parent_r13["writer_contract"]["temperature"] != 0.0:
        raise RuntimeError("R13 writer temperature drift")
    if parent_r13["summary"]["source_tasks"] != 36:
        raise RuntimeError("R13 source count drift")
    if parent_r13["summary"]["model_calls_executed"] != 0:
        raise RuntimeError("R13 unexpectedly contains writer calls")

    return {
        "schema_version": "1.0",
        "paper_id": "D2-PAPER-FAILURE-MEMORY-PROVENANCE",
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-L2B-WRITER-MODEL-R14",
        "recorded_date": "2026-08-24",
        "status": "WRITER_MODEL_REALIZATION_CONTENT_ADDRESSED_NO_INFERENCE",
        "role": "PRE_OUTCOME_SUPPORT_ONLY",
        "parent_r13": {
            "contract": "generated/d2-failure-memory-provenance-l2b-writer-input-contract-r13.json",
            "sha256": parent_r13_sha,
            "source_tasks": 36,
            "writer_model_family": "Qwen2.5-32B",
            "temperature": 0.0,
        },
        "prospective_writer_realization": {
            "runtime": "Ollama OpenAI-compatible local service",
            "ollama_version": ollama_version,
            "model_tag": EXPECTED_TAG,
            "manifest_digest": EXPECTED_MANIFEST,
            "manifest_sha256_verified": True,
            "format": details["format"],
            "family": details["family"],
            "parameter_size": details["parameter_size"],
            "parameter_count": show.get("model_info", {}).get("general.parameter_count"),
            "quantization": details["quantization_level"],
            "model_layer_digest": EXPECTED_MODEL_LAYER,
            "all_manifest_blobs_sha256_verified": all(x["sha256_verified"] for x in parsed_manifest["layers"]),
            "manifest_layers": parsed_manifest["layers"],
            "show_metadata_sha256": show_sha,
            "openai_v1_models_registry_sha256": v1_models_sha,
            "openai_v1_model_ids": model_ids,
        },
        "historical_relationship": {
            "R6_model_family_match": True,
            "R6_temperature_match": True,
            "R6_exact_binary_or_quantization_was_archived": False,
            "claim_exact_binary_identity_with_R6": False,
            "claim_exact_quantization_identity_with_R6": False,
            "prospective_realization_label": "QWEN25_32B_Q4_K_M_OLLAMA_MANIFEST_9F13BA12",
            "interpretation": "This is a new prospectively pinned realization of the R6 Qwen2.5-32B family, not a recovered binary-identical R6 writer artifact.",
        },
        "writer_execution_policy": {
            "uniform_same_model_for_all_36_sources": True,
            "temperature": 0.0,
            "request_count_if_scientifically_authorized": 36,
            "prompt_and_compact_trace_inputs_frozen_by_R13": True,
            "automatic_model_or_quantization_substitution_forbidden": True,
            "first_complete_parseable_response_frozen": True,
            "semantic_retry_or_prompt_change_forbidden": True,
        },
        "openai_compatible_transport_preflight": {
            "model_registry_endpoint_checked": True,
            "model_visible_as": EXPECTED_TAG,
            "chat_completion_called": False,
            "generation_or_embedding_called": False,
        },
        "execution_gate": {
            "writer_inputs_frozen": True,
            "exact_writer_model_artifact_bound": True,
            "writer_model_transport_preflight_pass": True,
            "writer_calls_executed": 0,
            "writer_calls_permitted": False,
            "exact_memory_bytes_bound": False,
            "downstream_l2_outcomes_permitted": False,
            "scientific_authority": False,
            "experiment_model_call_authority": False,
        },
        "scientific_verdict": "NO_VERDICT_MODEL_REALIZATION_ONLY",
        "authority": {
            "scientific": False,
            "experiment": False,
            "model_calls": False,
            "browser_actions": False,
            "evaluator_calls": False,
            "gpu": False,
            "submission": False,
        },
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--parent-r13", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--blobs-dir", type=Path, required=True)
    p.add_argument("--show-json", type=Path, required=True)
    p.add_argument("--v1-models-json", type=Path, required=True)
    p.add_argument("--output", type=Path, default=Path("generated/d2-failure-memory-provenance-l2b-writer-model-r14.json"))
    p.add_argument("--skip-blob-rehash", action="store_true", help="For local debugging only; authoritative generation must omit this flag.")
    args = p.parse_args()

    parent = json.loads(args.parent_r13.read_text(encoding="utf-8"))
    parsed = parse_manifest(args.manifest, args.blobs_dir, verify_blobs=not args.skip_blob_rehash)
    show = json.loads(args.show_json.read_text(encoding="utf-8"))
    v1_models = json.loads(args.v1_models_json.read_text(encoding="utf-8"))
    try:
        ov = subprocess.check_output(["ollama", "--version"], text=True, stderr=subprocess.STDOUT).strip()
    except Exception:
        ov = "UNKNOWN"

    payload = build_receipt(
        parent,
        sha256(args.parent_r13),
        parsed,
        show,
        sha256(args.show_json),
        v1_models,
        sha256(args.v1_models_json),
        ov,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "manifest": payload["prospective_writer_realization"]["manifest_digest"],
        "quantization": payload["prospective_writer_realization"]["quantization"],
        "writer_calls": payload["execution_gate"]["writer_calls_executed"],
        "calls_permitted": payload["execution_gate"]["writer_calls_permitted"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
