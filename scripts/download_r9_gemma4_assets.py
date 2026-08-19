#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.paper_first_agent_safety_r9_backbone_preflight import BACKBONE_MODEL_ID, BACKBONE_MODEL_REVISION, REALIZATION_ID
from research_pipeline.paper_first_agent_safety_r9_gemma4_asset_gate import DEFAULT_CAPTURE, DEFAULT_OUTPUT as AUTH_PATH, MIRROR_ENDPOINT, validate_download_authorization
from scripts.capture_r9_gemma4_hf_official_metadata import validate_capture

RECEIPT_NAME = ".r9-gemma4-formal-asset-verification.json"
RECEIPT_CLASS = "FORMAL_HF_EXACT_REVISION_CONTENT_ADDRESSED_VERIFICATION_GEMMA4"


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(16 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob_sha1(path: Path) -> str:
    size = Path(path).stat().st_size
    h = hashlib.sha1(); h.update(f"blob {size}\0".encode("ascii"))
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(16 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_snapshot(destination: Path, manifest: list[dict]) -> list[dict]:
    destination = Path(destination); verified: list[dict] = []
    expected_paths = {str(row["path"]) for row in manifest}
    for row in manifest:
        rel = str(row["path"]); path = destination / rel
        if not path.is_file():
            raise RuntimeError(f"missing manifest file:{rel}")
        size = path.stat().st_size
        if size != int(row["size"]):
            raise RuntimeError(f"size mismatch:{rel}:{size}!={row['size']}")
        kind = str(row["source_kind"]); expected = str(row["source_digest"])
        observed = sha_file(path) if kind == "lfs-sha256" else git_blob_sha1(path) if kind == "git-blob-sha1" else ""
        if observed != expected:
            raise RuntimeError(f"digest mismatch:{rel}:{observed}!={expected}")
        verified.append({"path": rel, "size": size, "source_kind": kind, "expected_digest": expected, "observed_digest": observed, "verified": True})
        print(json.dumps({"verified": rel, "size": size}, ensure_ascii=False), flush=True)
    extras = []
    for path in destination.rglob("*"):
        if not path.is_file():
            continue
        rel = str(path.relative_to(destination))
        if rel == RECEIPT_NAME or rel.startswith(".cache/"):
            continue
        if rel not in expected_paths:
            extras.append(rel)
    if extras:
        raise RuntimeError("unexpected non-cache files:" + ",".join(sorted(extras)))
    return verified


def load_authority(path: Path) -> dict:
    state = json.loads(Path(path).read_text(encoding="utf-8")); errors = validate_download_authorization(state)
    if errors:
        raise RuntimeError("invalid download authorization:" + ";".join(errors))
    return state


def validate_existing_receipt(receipt: Path, *, auth: dict, capture: dict) -> dict | None:
    if not receipt.is_file():
        return None
    state = json.loads(receipt.read_text(encoding="utf-8"))
    if (state.get("receipt_class") != RECEIPT_CLASS or state.get("status") != "FORMAL_LOCAL_ASSET_VERIFIED" or
        state.get("realization_id") != REALIZATION_ID or state.get("contract_sha256") != auth.get("contract_sha256") or
        state.get("official_source_manifest_sha256") != (capture.get("model") or {}).get("source_manifest_sha256") or
        state.get("model_loading_authorized") is not False or state.get("model_inference_authorized") is not False):
        raise RuntimeError("existing Gemma4 asset receipt is not safely resumable")
    return state


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--authorization", type=Path, default=AUTH_PATH)
    p.add_argument("--capture", type=Path, default=DEFAULT_CAPTURE)
    p.add_argument("--endpoint", default=MIRROR_ENDPOINT)
    p.add_argument("--max-workers", type=int, default=2)
    a = p.parse_args()
    auth = load_authority(a.authorization); capture = validate_capture(a.capture); model = capture["model"]
    if auth["official_capture"]["sha256"] != sha_file(a.capture) or auth["official_capture"]["source_manifest_sha256"] != model["source_manifest_sha256"]:
        raise RuntimeError("download authority/capture digest mismatch")
    destination = Path(auth["destination"]); destination.mkdir(parents=True, exist_ok=True); receipt = destination / RECEIPT_NAME
    existing = validate_existing_receipt(receipt, auth=auth, capture=capture)
    if existing is not None:
        print(json.dumps({"status": existing["status"], "receipt": str(receipt), "resumed": True})); return
    from huggingface_hub import snapshot_download
    manifest = model["source_manifest"]; patterns = [str(row["path"]) for row in manifest]
    print(json.dumps({"status": "DOWNLOAD_START", "model": BACKBONE_MODEL_ID, "revision": BACKBONE_MODEL_REVISION,
                      "endpoint": a.endpoint, "destination": str(destination), "file_count": len(patterns)}, ensure_ascii=False), flush=True)
    try:
        snapshot_download(repo_id=BACKBONE_MODEL_ID, revision=BACKBONE_MODEL_REVISION, local_dir=destination,
                          allow_patterns=patterns, max_workers=a.max_workers, endpoint=a.endpoint, token=False)
        verified = verify_snapshot(destination, manifest)
    except Exception as exc:
        stop = {"schema_version": "1.0", "status": "PROTOCOL_STOP_ASSET_TRANSPORT_OR_INTEGRITY", "realization_id": REALIZATION_ID,
                "contract_sha256": auth["contract_sha256"], "model_id": BACKBONE_MODEL_ID, "exact_revision": BACKBONE_MODEL_REVISION,
                "transport_endpoint": a.endpoint, "error_type": type(exc).__name__, "error_message": str(exc)[:1000],
                "partial_resume_allowed": True, "model_loading_authorized": False, "model_inference_authorized": False,
                "scientific_authority": False, "recorded_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat()}
        stop_path = destination / ".r9-gemma4-asset-protocol-stop.json"
        stop_path.write_text(json.dumps(stop, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": stop["status"], "stop_receipt": str(stop_path), "error_type": stop["error_type"]}), flush=True)
        raise
    state = {"schema_version": "1.0", "receipt_class": RECEIPT_CLASS, "status": "FORMAL_LOCAL_ASSET_VERIFIED",
             "realization_id": REALIZATION_ID, "contract_sha256": auth["contract_sha256"], "model_id": BACKBONE_MODEL_ID,
             "exact_revision": BACKBONE_MODEL_REVISION, "destination": str(destination), "transport_endpoint": a.endpoint,
             "transport_is_non_authoritative": a.endpoint != "https://huggingface.co", "official_capture_sha256": sha_file(a.capture),
             "official_source_manifest_sha256": model["source_manifest_sha256"], "verified_file_count": len(verified),
             "verified_files": verified, "formal_asset_verified": True, "model_loading_authorized": False,
             "model_inference_authorized": False, "scientific_authority": False,
             "verified_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat()}
    receipt.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": state["status"], "receipt": str(receipt), "verified_file_count": len(verified),
                      "model_loading_authorized": False, "model_inference_authorized": False}), flush=True)


if __name__ == "__main__":
    main()
