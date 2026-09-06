from __future__ import annotations

import base64
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

ATTESTATION_ARTIFACT_TYPE = "e2-r17-v3-stage-a-r3d-recovery-authorization-adapter-host69-runtime-replay-attestation"
SIGNATURE_ALGORITHM = "Ed25519"
SIGNATURE_CONTEXT = "E2-R17-R3D-HOST69-AUTH-ADAPTER-RUNTIME-REPLAY-V1"
OPENSSL = "/usr/bin/openssl"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_payload_bytes(payload: dict[str, Any]) -> bytes:
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return SIGNATURE_CONTEXT.encode("utf-8") + b"\x00" + body


def _openssl(args: list[str]) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run([OPENSSL, *args], capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"OpenSSL command failed ({result.returncode}): stderr={result.stderr.decode(errors='replace')[-1200:]}")
    return result


def _derived_public_key(private_key_path: Path) -> bytes:
    return _openssl(["pkey", "-in", str(private_key_path), "-pubout"]).stdout


def sign_document(*, payload: dict[str, Any], private_key_path: Path, public_key_path: Path) -> dict[str, Any]:
    if not private_key_path.is_file() or not public_key_path.is_file():
        raise RuntimeError("R3D runtime replay signing key material absent")
    if _derived_public_key(private_key_path) != public_key_path.read_bytes():
        raise RuntimeError("R3D runtime replay private/public signing key mismatch")
    raw = canonical_payload_bytes(payload)
    with tempfile.TemporaryDirectory(prefix="e2-r17-r3d-replay-sign-") as tmp:
        message = Path(tmp) / "message.bin"
        signature = Path(tmp) / "signature.bin"
        message.write_bytes(raw)
        result = subprocess.run(
            [OPENSSL, "pkeyutl", "-sign", "-rawin", "-inkey", str(private_key_path), "-in", str(message), "-out", str(signature)],
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(f"R3D runtime replay signing failed: {result.stderr.decode(errors='replace')[-1200:]}")
        sig_bytes = signature.read_bytes()
    return {
        "schema_version": "1.0",
        "artifact_type": ATTESTATION_ARTIFACT_TYPE,
        "payload": payload,
        "signature": {
            "algorithm": SIGNATURE_ALGORITHM,
            "context": SIGNATURE_CONTEXT,
            "public_key_sha256": sha256_file(public_key_path),
            "signature_base64": base64.b64encode(sig_bytes).decode("ascii"),
        },
    }


def verify_document(
    document: dict[str, Any],
    *,
    public_key_path: Path,
    expected_public_key_sha256: str,
    expected_payload_fields: dict[str, Any],
) -> dict[str, Any]:
    if document.get("artifact_type") != ATTESTATION_ARTIFACT_TYPE:
        raise RuntimeError("R3D runtime replay attestation artifact type drift")
    payload = document.get("payload")
    signature_row = document.get("signature")
    if not isinstance(payload, dict) or not isinstance(signature_row, dict):
        raise RuntimeError("R3D runtime replay attestation payload/signature absent")
    if not public_key_path.is_file():
        raise RuntimeError("R3D runtime replay trusted public key absent")
    actual_public_sha = sha256_file(public_key_path)
    if actual_public_sha != expected_public_key_sha256:
        raise RuntimeError("R3D runtime replay trusted public-key SHA drift")
    if signature_row.get("algorithm") != SIGNATURE_ALGORITHM or signature_row.get("context") != SIGNATURE_CONTEXT:
        raise RuntimeError("R3D runtime replay signature metadata drift")
    if signature_row.get("public_key_sha256") != expected_public_key_sha256:
        raise RuntimeError("R3D runtime replay signature public-key fingerprint drift")
    try:
        signature = base64.b64decode(str(signature_row.get("signature_base64") or ""), validate=True)
    except Exception as exc:
        raise RuntimeError("R3D runtime replay signature encoding invalid") from exc
    raw = canonical_payload_bytes(payload)
    with tempfile.TemporaryDirectory(prefix="e2-r17-r3d-replay-verify-") as tmp:
        message = Path(tmp) / "message.bin"
        sig = Path(tmp) / "signature.bin"
        message.write_bytes(raw)
        sig.write_bytes(signature)
        result = subprocess.run(
            [OPENSSL, "pkeyutl", "-verify", "-rawin", "-pubin", "-inkey", str(public_key_path), "-in", str(message), "-sigfile", str(sig)],
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError("R3D runtime replay attestation signature verification failed")
    for key, expected in expected_payload_fields.items():
        if payload.get(key) != expected:
            raise RuntimeError(f"R3D runtime replay attestation binding drift: {key}")
    return payload
