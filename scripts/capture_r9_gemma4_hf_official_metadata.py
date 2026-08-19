#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.paper_first_agent_safety_r9_backbone_preflight import (
    BACKBONE_MODEL_ID,
    BACKBONE_MODEL_REVISION,
    DEFAULT_JSON as PREREG_PATH,
    REALIZATION_ID,
    validate_preregistration,
)
from research_pipeline.paper_first_agent_safety_r9_harness import _hf_metadata_identity, _hf_revision_api_url

ARTIFACT_CLASS = "OFFICIAL_HF_EXACT_REVISION_METADATA_CAPTURE_GEMMA4_BACKBONE_PREFLIGHT"
DEFAULT_OUTPUT = ROOT / "generated" / "agent-safety-r9-gemma4-official-hf-metadata-capture.json"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical_sha(value: object) -> str:
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def source_manifest(metadata: dict) -> tuple[list[dict], str]:
    rows: list[dict] = []
    for item in metadata.get("siblings") or metadata.get("files") or []:
        if not isinstance(item, dict):
            continue
        name = str(item.get("rfilename") or item.get("path") or "").strip()
        if not name:
            continue
        lfs = item.get("lfs") if isinstance(item.get("lfs"), dict) else {}
        lfs_sha = str(lfs.get("sha256") or "").lower()
        blob = str(item.get("blobId") or item.get("blob_id") or "").lower()
        size = lfs.get("size") if isinstance(lfs.get("size"), int) else item.get("size")
        if re.fullmatch(r"[0-9a-f]{64}", lfs_sha):
            kind, digest = "lfs-sha256", lfs_sha
        elif re.fullmatch(r"[0-9a-f]{40}", blob):
            kind, digest = "git-blob-sha1", blob
        else:
            raise RuntimeError(f"HF metadata lacks content identity:{name}")
        if not isinstance(size, int) or size <= 0:
            raise RuntimeError(f"HF metadata lacks positive size:{name}")
        rows.append({"path": name, "size": size, "source_kind": kind, "source_digest": digest})
    rows.sort(key=lambda row: row["path"])
    names = {row["path"] for row in rows}
    if "config.json" not in names or "tokenizer.json" not in names or not any(name.endswith(".safetensors") for name in names):
        raise RuntimeError("Gemma4 HF manifest lacks required runtime asset classes")
    return rows, canonical_sha(rows)


def fetch_literal_hf() -> tuple[int, str, bytes]:
    url = _hf_revision_api_url(BACKBONE_MODEL_ID, BACKBONE_MODEL_REVISION)
    request = urllib.request.Request(url, headers={"User-Agent": "Agent-Self-Evolution-Observatory/R9-Gemma4-Provenance"})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(request, timeout=30) as response:
        status = int(getattr(response, "status", 0) or response.getcode() or 0)
        final = str(response.geturl() or "")
        raw = response.read()
    parsed = urllib.parse.urlparse(final)
    if status != 200 or parsed.scheme != "https" or (parsed.hostname or "").lower() != "huggingface.co" or final.split("#", 1)[0] != url:
        raise RuntimeError(f"literal HF capture failed:HTTP={status} final={final}")
    return status, final, raw


def load_prereg() -> dict:
    prereg = json.loads(PREREG_PATH.read_text(encoding="utf-8"))
    errors = validate_preregistration(prereg)
    if errors:
        raise RuntimeError("invalid Gemma4 preregistration:" + ";".join(errors))
    if prereg.get("realization_id") != REALIZATION_ID or (prereg.get("asset_gate") or {}).get("official_metadata_capture_authorized") is not True:
        raise RuntimeError("Gemma4 preregistration does not authorize metadata capture")
    return prereg


def build_capture() -> dict:
    prereg = load_prereg()
    repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    github_sha = os.environ.get("GITHUB_SHA", "").strip().lower()
    run_id = os.environ.get("GITHUB_RUN_ID", "").strip()
    if repo != "lightrain-a/agent-self-evolution-observatory" or not re.fullmatch(r"[0-9a-f]{40}", github_sha) or not run_id.isdigit():
        raise RuntimeError("invalid GitHub capture environment")
    status, final, raw = fetch_literal_hf()
    metadata = json.loads(raw.decode("utf-8"))
    if _hf_metadata_identity(metadata)[:2] != (BACKBONE_MODEL_ID, BACKBONE_MODEL_REVISION):
        raise RuntimeError("Gemma4 official HF identity mismatch")
    manifest, manifest_sha = source_manifest(metadata)
    lfs_bytes = sum(int(row["size"]) for row in manifest if row["source_kind"] == "lfs-sha256")
    return {
        "schema_version": "1.0", "artifact_class": ARTIFACT_CLASS,
        "captured_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "realization_id": REALIZATION_ID, "contract_sha256": prereg["contract_sha256"],
        "preregistration_sha256": sha(PREREG_PATH.read_bytes()),
        "capture_environment": {"github_repository": repo, "github_run_id": run_id, "github_sha": github_sha,
                                "github_workflow": os.environ.get("GITHUB_WORKFLOW", ""), "runner_os": os.environ.get("RUNNER_OS", "")},
        "model": {"model_id": BACKBONE_MODEL_ID, "revision": BACKBONE_MODEL_REVISION,
                  "source_url": _hf_revision_api_url(BACKBONE_MODEL_ID, BACKBONE_MODEL_REVISION), "source_final_url": final,
                  "source_http_status": status, "raw_metadata_sha256": sha(raw), "raw_metadata_base64": base64.b64encode(raw).decode("ascii"),
                  "source_manifest": manifest, "source_manifest_sha256": manifest_sha,
                  "manifest_file_count": len(manifest), "lfs_total_bytes": lfs_bytes},
        "capture_is_transport_provenance_only": True, "weight_download_authorized": False,
        "model_loading_authorized": False, "model_inference_authorized": False, "scientific_authority": False,
    }


def validate_capture(path: Path) -> dict:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    prereg = load_prereg()
    if payload.get("artifact_class") != ARTIFACT_CLASS or payload.get("realization_id") != REALIZATION_ID or payload.get("contract_sha256") != prereg["contract_sha256"]:
        raise RuntimeError("Gemma4 HF capture identity/contract mismatch")
    if payload.get("preregistration_sha256") != sha(PREREG_PATH.read_bytes()):
        raise RuntimeError("Gemma4 HF capture preregistration digest mismatch")
    if payload.get("weight_download_authorized") is not False or payload.get("model_loading_authorized") is not False or payload.get("model_inference_authorized") is not False or payload.get("scientific_authority") is not False:
        raise RuntimeError("Gemma4 HF capture over-authorizes execution")
    row = payload.get("model") or {}; raw = base64.b64decode(str(row.get("raw_metadata_base64") or ""), validate=True)
    if sha(raw) != row.get("raw_metadata_sha256"):
        raise RuntimeError("Gemma4 HF capture raw digest mismatch")
    metadata = json.loads(raw.decode("utf-8"))
    if _hf_metadata_identity(metadata)[:2] != (BACKBONE_MODEL_ID, BACKBONE_MODEL_REVISION):
        raise RuntimeError("Gemma4 HF capture raw identity mismatch")
    manifest, manifest_sha = source_manifest(metadata)
    expected_url = _hf_revision_api_url(BACKBONE_MODEL_ID, BACKBONE_MODEL_REVISION)
    if manifest != row.get("source_manifest") or manifest_sha != row.get("source_manifest_sha256") or row.get("source_url") != expected_url or row.get("source_final_url") != expected_url or row.get("source_http_status") != 200:
        raise RuntimeError("Gemma4 HF capture manifest/url drift")
    return payload


def main() -> None:
    p = argparse.ArgumentParser(); p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); p.add_argument("--validate", type=Path); a = p.parse_args()
    if a.validate:
        state = validate_capture(a.validate); print(json.dumps({"status": "VALID", "artifact_class": state["artifact_class"]})); return
    state = build_capture(); a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"); validate_capture(a.output)
    print(json.dumps({"status": "CAPTURED", "output": str(a.output), "artifact_sha256": sha(a.output.read_bytes()),
                      "files": state["model"]["manifest_file_count"], "lfs_total_bytes": state["model"]["lfs_total_bytes"]}))


if __name__ == "__main__":
    main()
