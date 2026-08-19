from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .paper_first_agent_safety_r9_backbone_preflight import (
    BACKBONE_MODEL_ID,
    BACKBONE_MODEL_REVISION,
    DEFAULT_JSON as PREREG_PATH,
    REALIZATION_ID,
    validate_preregistration,
)
from scripts.capture_r9_gemma4_hf_official_metadata import validate_capture

SCHEMA_VERSION = "1.0"
DEFAULT_CAPTURE = PROJECT_ROOT / "generated" / "agent-safety-r9-gemma4-official-hf-metadata-capture.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "generated" / "agent-safety-r9-gemma4-asset-download-authorization-20260819.json"
DEFAULT_DESTINATION = Path("/data/wyt/agent-safety-discovery-20260818/model-assets/gemma4-26B-A4B-it-4d7ae4984b7db7de8f8457170b3f1a419ee76d52")
MIRROR_ENDPOINT = "https://hf-mirror.com"
MIN_FREE_HEADROOM_BYTES = 10 * 1024**3


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _canonical_sha(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _contract_sha(payload: dict[str, Any]) -> str:
    body = dict(payload); body.pop("generated_at", None)
    return _canonical_sha(body)


def _repo_rel(path: Path) -> str:
    return str(Path(path).resolve().relative_to(PROJECT_ROOT.resolve()))


def _load_prereg(path: Path) -> dict[str, Any]:
    state = json.loads(Path(path).read_text(encoding="utf-8")); errors = validate_preregistration(state)
    if errors:
        raise ValueError("invalid Gemma4 preregistration:" + ";".join(errors))
    return state


def build_download_authorization(
    *, prereg_path: Path = PREREG_PATH, capture_path: Path = DEFAULT_CAPTURE,
    destination: Path = DEFAULT_DESTINATION, generated_at: str | None = None,
) -> dict[str, Any]:
    prereg = _load_prereg(prereg_path); capture = validate_capture(capture_path)
    if capture.get("contract_sha256") != prereg.get("contract_sha256"):
        raise ValueError("official capture does not bind to preregistered contract")
    model = capture.get("model") or {}; manifest = model.get("source_manifest") or []
    if model.get("model_id") != BACKBONE_MODEL_ID or model.get("revision") != BACKBONE_MODEL_REVISION or not manifest:
        raise ValueError("official capture model identity/manifest drift")
    total_bytes = sum(int(row.get("size") or 0) for row in manifest)
    lfs_bytes = int(model.get("lfs_total_bytes") or 0)
    if total_bytes <= 0 or lfs_bytes <= 0:
        raise ValueError("official capture asset sizes invalid")
    destination = Path(destination)
    disk_probe = destination.parent if destination.parent.exists() else Path("/data")
    free_bytes = shutil.disk_usage(disk_probe).free
    required_free = total_bytes + MIN_FREE_HEADROOM_BYTES
    if free_bytes < required_free:
        raise ValueError(f"insufficient disk for exact Gemma4 snapshot:{free_bytes}<{required_free}")
    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "AUTHORIZED_CONTENT_ADDRESSED_ASSET_DOWNLOAD_ONLY",
        "realization_id": REALIZATION_ID,
        "contract_sha256": prereg["contract_sha256"],
        "model_id": BACKBONE_MODEL_ID,
        "exact_revision": BACKBONE_MODEL_REVISION,
        "destination": str(destination),
        "official_capture": {
            "repo_path": _repo_rel(capture_path),
            "sha256": _sha(capture_path),
            "source_manifest_sha256": model.get("source_manifest_sha256"),
            "manifest_file_count": int(model.get("manifest_file_count") or len(manifest)),
            "manifest_total_bytes": total_bytes,
            "lfs_total_bytes": lfs_bytes,
        },
        "transport_policy": {
            "authoritative_source": "literal huggingface.co exact-revision metadata capture only",
            "preferred_endpoint": "https://huggingface.co",
            "non_authoritative_transport_fallback": MIRROR_ENDPOINT,
            "mirror_may_transport_bytes_but_never_establish_provenance": True,
            "exact_revision_required": True,
            "partial_resume_allowed": True,
            "concurrent_duplicate_download_forbidden": True,
        },
        "verification_contract": {
            "verify_every_manifest_file": True,
            "lfs_files": "sha256 must equal official HF lfs.sha256",
            "git_blob_files": "git blob sha1 must equal official HF blobId",
            "missing_extra_or_digest_mismatch": "PROTOCOL_STOP_ASSET_INTEGRITY",
            "formal_asset_verified_only_after_all_files_pass": True,
        },
        "disk_preflight": {"free_bytes": free_bytes, "required_free_bytes": required_free, "headroom_bytes": MIN_FREE_HEADROOM_BYTES, "passed": True},
        "authority": {
            "model_weight_download": True,
            "model_loading": False,
            "model_inference": False,
            "benign_capability_execution": False,
            "development_safety_execution": False,
            "persistent_state_construction": False,
            "fresh_qualification_execution": False,
            "heldout_future": False,
            "scientific_claim": False,
            "gpu_scientific": False,
        },
        "next_gate": "LOCAL_GEMMA4_FULL_MANIFEST_CONTENT_VERIFICATION",
        "scientific_authority": False,
        "provenance": {"preregistration_repo_path": _repo_rel(prereg_path), "preregistration_sha256": _sha(prereg_path), "official_capture_sha256": _sha(capture_path)},
    }
    return {**body, "authorization_sha256": _contract_sha(body)}


def validate_download_authorization(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if state.get("status") != "AUTHORIZED_CONTENT_ADDRESSED_ASSET_DOWNLOAD_ONLY" or state.get("realization_id") != REALIZATION_ID:
        errors.append("Gemma4 download authorization identity/status drift")
    if state.get("model_id") != BACKBONE_MODEL_ID or state.get("exact_revision") != BACKBONE_MODEL_REVISION:
        errors.append("Gemma4 download authorization model pin drift")
    transport = state.get("transport_policy") or {}
    if transport.get("mirror_may_transport_bytes_but_never_establish_provenance") is not True or transport.get("exact_revision_required") is not True:
        errors.append("Gemma4 transport provenance policy drift")
    verify = state.get("verification_contract") or {}
    if verify.get("verify_every_manifest_file") is not True or verify.get("formal_asset_verified_only_after_all_files_pass") is not True:
        errors.append("Gemma4 verification contract drift")
    authority = state.get("authority") or {}
    if authority.get("model_weight_download") is not True or any(v is True for k, v in authority.items() if k != "model_weight_download"):
        errors.append("Gemma4 download authorization over-authorizes execution")
    body = dict(state); observed = str(body.pop("authorization_sha256", ""))
    if observed != _contract_sha(body):
        errors.append("Gemma4 download authorization digest mismatch")
    if state.get("scientific_authority") is not False:
        errors.append("Gemma4 download authorization must remain zero-authority")
    return sorted(set(errors))


def write_download_authorization(*, output: Path = DEFAULT_OUTPUT, **kwargs: Any) -> dict[str, Any]:
    state = build_download_authorization(**kwargs); errors = validate_download_authorization(state)
    if errors:
        raise ValueError("invalid Gemma4 download authorization:" + ";".join(errors))
    output.parent.mkdir(parents=True, exist_ok=True); output.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return state


def main() -> None:
    p = argparse.ArgumentParser(); p.add_argument("--prereg", type=Path, default=PREREG_PATH); p.add_argument("--capture", type=Path, default=DEFAULT_CAPTURE)
    p.add_argument("--destination", type=Path, default=DEFAULT_DESTINATION); p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); a = p.parse_args()
    state = write_download_authorization(prereg_path=a.prereg, capture_path=a.capture, destination=a.destination, output=a.output)
    print(json.dumps({"status": state["status"], "authorization_sha256": state["authorization_sha256"], "destination": state["destination"],
                      "manifest_file_count": state["official_capture"]["manifest_file_count"], "weight_download_authorized": state["authority"]["model_weight_download"],
                      "model_loading": state["authority"]["model_loading"], "model_inference": state["authority"]["model_inference"]}))


if __name__ == "__main__":
    main()
