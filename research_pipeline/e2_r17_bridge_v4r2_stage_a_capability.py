from __future__ import annotations

import base64
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CAPABILITY_ARTIFACT_TYPE = "e2-r17-bridge-v4r2-stage-a-r3-externally-signed-execution-capability"
SIGNATURE_ALGORITHM = "Ed25519"
SIGNATURE_CONTEXT = "E2-R17-BRIDGE-V4R2-STAGE-A-EXECUTION-CAPABILITY-V1"
CONTROL_PLANE_REVISION = "STAGE_A_R3_EXTERNAL_SIGNED_EXECUTION_CAPABILITY"
PRODUCTION_PUBLIC_KEY_RELATIVE = "generated/e2-r17-bridge-v4r2-stage-a-controller-public-key-20260907.pem"
PRODUCTION_PUBLIC_KEY_PATH = ROOT / PRODUCTION_PUBLIC_KEY_RELATIVE
PRODUCTION_PUBLIC_KEY_SHA256 = "f4b73b89716bee28902feb699d9ab81822a986ac8b89235cf768407c3e01fda0"
OPENSSL = "/usr/bin/openssl"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_payload_bytes(payload: dict[str, Any]) -> bytes:
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return SIGNATURE_CONTEXT.encode("utf-8") + b"\x00" + body


def _openssl(args: list[str]) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run([OPENSSL, *args], capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(
            f"OpenSSL command failed ({result.returncode}); stderr={result.stderr.decode(errors='replace')[-1200:]}"
        )
    return result


def _derived_public_key(private_key_path: Path) -> bytes:
    return _openssl(["pkey", "-in", str(private_key_path), "-pubout"]).stdout


def sign_document(*, payload: dict[str, Any], private_key_path: Path, public_key_path: Path) -> dict[str, Any]:
    if not private_key_path.is_file() or not public_key_path.is_file():
        raise RuntimeError("Bridge Stage-A signing key material absent")
    if _derived_public_key(private_key_path) != public_key_path.read_bytes():
        raise RuntimeError("Bridge Stage-A private/public signing key mismatch")
    raw = canonical_payload_bytes(payload)
    with tempfile.TemporaryDirectory(prefix="e2-r17-bridge-stage-a-sign-") as tmp:
        message = Path(tmp) / "message.bin"
        signature = Path(tmp) / "signature.bin"
        message.write_bytes(raw)
        _openssl(["pkeyutl", "-sign", "-rawin", "-inkey", str(private_key_path), "-in", str(message), "-out", str(signature)])
        signature_bytes = signature.read_bytes()
    return {
        "schema_version": "1.0",
        "artifact_type": CAPABILITY_ARTIFACT_TYPE,
        "payload": payload,
        "signature": {
            "algorithm": SIGNATURE_ALGORITHM,
            "context": SIGNATURE_CONTEXT,
            "public_key_sha256": PRODUCTION_PUBLIC_KEY_SHA256,
            "signature_base64": base64.b64encode(signature_bytes).decode("ascii"),
        },
    }


def verify_document(document: dict[str, Any], *, expected_payload_fields: dict[str, Any]) -> dict[str, Any]:
    if document.get("artifact_type") != CAPABILITY_ARTIFACT_TYPE:
        raise RuntimeError("Bridge Stage-A capability artifact type drift")
    payload = document.get("payload")
    signature_row = document.get("signature")
    if not isinstance(payload, dict) or not isinstance(signature_row, dict):
        raise RuntimeError("Bridge Stage-A capability payload/signature absent")
    if not PRODUCTION_PUBLIC_KEY_PATH.is_file():
        raise RuntimeError("Bridge Stage-A production public key absent")
    if sha256_file(PRODUCTION_PUBLIC_KEY_PATH) != PRODUCTION_PUBLIC_KEY_SHA256:
        raise RuntimeError("Bridge Stage-A production public-key SHA drift")
    if signature_row.get("algorithm") != SIGNATURE_ALGORITHM or signature_row.get("context") != SIGNATURE_CONTEXT:
        raise RuntimeError("Bridge Stage-A capability signature metadata drift")
    if signature_row.get("public_key_sha256") != PRODUCTION_PUBLIC_KEY_SHA256:
        raise RuntimeError("Bridge Stage-A capability public-key fingerprint drift")
    try:
        signature = base64.b64decode(str(signature_row.get("signature_base64") or ""), validate=True)
    except Exception as exc:
        raise RuntimeError("Bridge Stage-A capability signature encoding invalid") from exc
    raw = canonical_payload_bytes(payload)
    with tempfile.TemporaryDirectory(prefix="e2-r17-bridge-stage-a-verify-") as tmp:
        message = Path(tmp) / "message.bin"
        signature_path = Path(tmp) / "signature.bin"
        message.write_bytes(raw)
        signature_path.write_bytes(signature)
        result = subprocess.run(
            [
                OPENSSL,
                "pkeyutl",
                "-verify",
                "-rawin",
                "-pubin",
                "-inkey",
                str(PRODUCTION_PUBLIC_KEY_PATH),
                "-in",
                str(message),
                "-sigfile",
                str(signature_path),
            ],
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError("Bridge Stage-A capability signature verification failed")
    if payload.get("control_plane_revision") != CONTROL_PLANE_REVISION:
        raise RuntimeError("Bridge Stage-A capability revision drift")
    if payload.get("single_use") is not True:
        raise RuntimeError("Bridge Stage-A capability must be single-use")
    expected_authority = {
        "scientific_experiment": True,
        "provider_io": True,
        "search_pool_acquisition": True,
        "support_inspection": True,
        "free_updater": False,
        "deterministic_state_materialization": False,
        "actor_evaluation": False,
        "screen_outcome_opening": False,
        "validation_opening": False,
        "analysis": False,
        "paper_promotion": False,
    }
    if payload.get("authority") != expected_authority:
        raise RuntimeError("Bridge Stage-A capability authority surface drift")
    if set(payload) != {
        "capability_id",
        "issued_at_utc",
        "control_plane_revision",
        "contract_sha256",
        "preflight_sha256",
        "review_receipt_sha256",
        "structural_authorization_sha256",
        "runner_sha256",
        "runtime_sha256",
        "support_sha256",
        "identity_sha256",
        "run_root",
        "lineage_lease_path",
        "consumption_marker_path",
        "single_use",
        "authority",
    }:
        raise RuntimeError("Bridge Stage-A capability payload field surface drift")
    for key, expected in expected_payload_fields.items():
        if payload.get(key) != expected:
            raise RuntimeError(f"Bridge Stage-A capability binding drift: {key}")
    return payload


__all__ = [
    "CAPABILITY_ARTIFACT_TYPE",
    "SIGNATURE_ALGORITHM",
    "SIGNATURE_CONTEXT",
    "CONTROL_PLANE_REVISION",
    "PRODUCTION_PUBLIC_KEY_RELATIVE",
    "PRODUCTION_PUBLIC_KEY_PATH",
    "PRODUCTION_PUBLIC_KEY_SHA256",
    "canonical_payload_bytes",
    "sha256_file",
    "sign_document",
    "verify_document",
]
