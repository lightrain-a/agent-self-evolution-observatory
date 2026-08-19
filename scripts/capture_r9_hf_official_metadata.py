#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from research_pipeline.paper_first_agent_safety_r9_harness import (
    R9_AGENT_MODEL_ID,
    R9_AGENT_MODEL_REVISION,
    R9_EVALUATOR_MODEL_ID,
    R9_EVALUATOR_MODEL_REVISION,
    R9_OFFICIAL_HF_CAPTURE_CLASS,
    R9_REQUIRED_MODEL_FILES,
    _hf_metadata_identity,
    _hf_revision_api_url,
    _hf_source_manifest,
)


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _fetch_literal_hf(model_id: str, revision: str) -> tuple[int, str, bytes]:
    url = _hf_revision_api_url(model_id, revision)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Agent-Self-Evolution-Observatory/R9-GitHub-Provenance-Capture"},
    )
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(request, timeout=30) as response:
        status = int(getattr(response, "status", 0) or response.getcode() or 0)
        final_url = str(response.geturl() or "")
        raw = response.read()
    parsed = urllib.parse.urlparse(final_url)
    if status != 200 or parsed.scheme != "https" or (parsed.hostname or "").lower() != "huggingface.co":
        raise RuntimeError(f"literal Hugging Face capture failed for {model_id}: HTTP={status} final={final_url}")
    if final_url.split("#", 1)[0] != url:
        raise RuntimeError(f"literal Hugging Face capture redirected or changed URL for {model_id}: {final_url}")
    return status, final_url, raw


def _capture_role(role: str, model_id: str, revision: str) -> dict:
    status, final_url, raw = _fetch_literal_hf(model_id, revision)
    try:
        metadata = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"invalid Hugging Face JSON for {role}") from error
    if _hf_metadata_identity(metadata)[:2] != (model_id, revision):
        raise RuntimeError(f"Hugging Face identity mismatch for {role}")
    required = set(R9_REQUIRED_MODEL_FILES[role])
    source_manifest, source_manifest_sha = _hf_source_manifest(metadata, required)
    return {
        "role": role,
        "model_id": model_id,
        "revision": revision,
        "source_url": _hf_revision_api_url(model_id, revision),
        "source_final_url": final_url,
        "source_http_status": status,
        "raw_metadata_sha256": _sha(raw),
        "raw_metadata_base64": base64.b64encode(raw).decode("ascii"),
        "source_manifest": source_manifest,
        "source_manifest_sha256": source_manifest_sha,
        "required_file_count": len(required),
    }


def build_capture() -> dict:
    github_sha = os.environ.get("GITHUB_SHA", "").strip().lower()
    github_run_id = os.environ.get("GITHUB_RUN_ID", "").strip()
    github_repository = os.environ.get("GITHUB_REPOSITORY", "").strip()
    if github_repository != "lightrain-a/agent-self-evolution-observatory":
        raise RuntimeError(f"unexpected GITHUB_REPOSITORY: {github_repository!r}")
    if len(github_sha) != 40 or any(ch not in "0123456789abcdef" for ch in github_sha):
        raise RuntimeError("GITHUB_SHA must be a 40-hex commit")
    if not github_run_id.isdigit():
        raise RuntimeError("GITHUB_RUN_ID must be numeric")
    models = {
        "agent": _capture_role("agent", R9_AGENT_MODEL_ID, R9_AGENT_MODEL_REVISION),
        "evaluator": _capture_role("evaluator", R9_EVALUATOR_MODEL_ID, R9_EVALUATOR_MODEL_REVISION),
    }
    return {
        "schema_version": "1.0",
        "artifact_class": R9_OFFICIAL_HF_CAPTURE_CLASS,
        "captured_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "capture_environment": {
            "github_repository": github_repository,
            "github_run_id": github_run_id,
            "github_sha": github_sha,
            "github_workflow": os.environ.get("GITHUB_WORKFLOW", ""),
            "runner_name": os.environ.get("RUNNER_NAME", ""),
            "runner_os": os.environ.get("RUNNER_OS", ""),
        },
        "models": models,
        "capture_is_transport_provenance_only": True,
        "formal_gate_eligible_as_transport": True,
        "execution_authorized": False,
        "scientific_authority": False,
    }


def validate_capture(path: Path) -> dict:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("artifact_class") != R9_OFFICIAL_HF_CAPTURE_CLASS:
        raise RuntimeError("capture artifact class mismatch")
    if payload.get("execution_authorized") is not False or payload.get("scientific_authority") is not False:
        raise RuntimeError("capture must carry zero science/execution authority")
    expected = {
        "agent": (R9_AGENT_MODEL_ID, R9_AGENT_MODEL_REVISION),
        "evaluator": (R9_EVALUATOR_MODEL_ID, R9_EVALUATOR_MODEL_REVISION),
    }
    for role, (model_id, revision) in expected.items():
        row = (payload.get("models") or {}).get(role) or {}
        raw = base64.b64decode(str(row.get("raw_metadata_base64") or "").encode("ascii"), validate=True)
        if _sha(raw) != row.get("raw_metadata_sha256"):
            raise RuntimeError(f"capture raw digest mismatch:{role}")
        metadata = json.loads(raw.decode("utf-8"))
        if _hf_metadata_identity(metadata)[:2] != (model_id, revision):
            raise RuntimeError(f"capture identity mismatch:{role}")
        manifest, manifest_sha = _hf_source_manifest(metadata, set(R9_REQUIRED_MODEL_FILES[role]))
        if manifest != row.get("source_manifest") or manifest_sha != row.get("source_manifest_sha256"):
            raise RuntimeError(f"capture manifest mismatch:{role}")
        expected_url = _hf_revision_api_url(model_id, revision)
        if row.get("source_url") != expected_url or row.get("source_final_url") != expected_url or row.get("source_http_status") != 200:
            raise RuntimeError(f"capture URL/status mismatch:{role}")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("generated/agent-safety-r9-official-hf-metadata-capture.json"),
    )
    parser.add_argument("--validate", type=Path)
    args = parser.parse_args()
    if args.validate:
        payload = validate_capture(args.validate)
        print(json.dumps({"status": "VALID", "artifact_class": payload["artifact_class"]}))
        return
    payload = build_capture()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    validate_capture(args.output)
    print(
        json.dumps(
            {
                "status": "CAPTURED",
                "output": str(args.output),
                "artifact_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
                "roles": sorted(payload["models"]),
                "execution_authorized": False,
                "scientific_authority": False,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
