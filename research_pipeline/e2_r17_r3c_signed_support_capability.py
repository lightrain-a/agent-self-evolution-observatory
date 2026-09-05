from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

CAPABILITY_ARTIFACT_TYPE = "e2-r17-v3-stage-a-r3c-externally-signed-support-read-capability"
SIGNATURE_ALGORITHM = "Ed25519"
SIGNATURE_CONTEXT = "E2-R17-R3C-POST-TERMINAL-SUPPORT-CAPABILITY-V1"
CONTROL_PLANE_REVISION = "R3C_EXTERNAL_SIGNED_SUPPORT_CAPABILITY"
HARD_PROVIDER_NOT_BEFORE = "2026-09-07T00:00:00+08:00"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_payload_bytes(payload: dict[str, Any]) -> bytes:
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return SIGNATURE_CONTEXT.encode("utf-8") + b"\x00" + body


def public_key_fingerprint(path: Path) -> str:
    return sha256_file(path)


def sign_document(*, payload: dict[str, Any], private_key_path: Path, public_key_path: Path) -> dict[str, Any]:
    private = serialization.load_pem_private_key(private_key_path.read_bytes(), password=None)
    public = serialization.load_pem_public_key(public_key_path.read_bytes())
    if not isinstance(private, Ed25519PrivateKey) or not isinstance(public, Ed25519PublicKey):
        raise RuntimeError("R3C signer key type must be Ed25519")
    derived_public = private.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    if derived_public != public_key_path.read_bytes():
        raise RuntimeError("R3C private/public signing key mismatch")
    signature = private.sign(canonical_payload_bytes(payload))
    return {
        "schema_version": "1.0",
        "artifact_type": CAPABILITY_ARTIFACT_TYPE,
        "payload": payload,
        "signature": {
            "algorithm": SIGNATURE_ALGORITHM,
            "context": SIGNATURE_CONTEXT,
            "public_key_sha256": public_key_fingerprint(public_key_path),
            "signature_base64": base64.b64encode(signature).decode("ascii"),
        },
    }


def verify_document(
    document: dict[str, Any],
    *,
    public_key_path: Path,
    expected_public_key_sha256: str,
    expected_payload_fields: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if document.get("artifact_type") != CAPABILITY_ARTIFACT_TYPE:
        raise RuntimeError("R3C signed capability artifact type drift")
    payload = document.get("payload")
    signature_row = document.get("signature")
    if not isinstance(payload, dict) or not isinstance(signature_row, dict):
        raise RuntimeError("R3C signed capability payload/signature absent")
    if not public_key_path.is_file():
        raise RuntimeError("R3C trusted signer public key absent")
    actual_public_sha = public_key_fingerprint(public_key_path)
    if actual_public_sha != expected_public_key_sha256:
        raise RuntimeError("R3C trusted signer public-key SHA drift")
    if signature_row.get("algorithm") != SIGNATURE_ALGORITHM or signature_row.get("context") != SIGNATURE_CONTEXT:
        raise RuntimeError("R3C signed capability signature metadata drift")
    if signature_row.get("public_key_sha256") != expected_public_key_sha256:
        raise RuntimeError("R3C signed capability public-key fingerprint drift")
    try:
        signature = base64.b64decode(str(signature_row.get("signature_base64") or ""), validate=True)
    except Exception as exc:
        raise RuntimeError("R3C signed capability signature encoding invalid") from exc
    public = serialization.load_pem_public_key(public_key_path.read_bytes())
    if not isinstance(public, Ed25519PublicKey):
        raise RuntimeError("R3C trusted signer public key is not Ed25519")
    try:
        public.verify(signature, canonical_payload_bytes(payload))
    except InvalidSignature as exc:
        raise RuntimeError("R3C signed capability signature verification failed") from exc
    if payload.get("control_plane_revision") != CONTROL_PLANE_REVISION:
        raise RuntimeError("R3C signed capability revision drift")
    if payload.get("hard_provider_not_before") != HARD_PROVIDER_NOT_BEFORE:
        raise RuntimeError("R3C signed capability hard provider boundary drift")
    if payload.get("single_use") is not True or payload.get("stage_a_support_read") is not True:
        raise RuntimeError("R3C signed capability support-read/single-use scope invalid")
    for key in (
        "stage_a_provider_execution",
        "stage_b_learning_execution",
        "updater",
        "heldout_evaluation",
        "analyzer",
        "second_backbone",
        "public_benchmark",
        "paper_promotion",
        "submission",
        "scientific_authority",
    ):
        if payload.get(key) is not False:
            raise RuntimeError(f"R3C signed capability overbroad: {key}")
    if expected_payload_fields:
        for key, expected in expected_payload_fields.items():
            if payload.get(key) != expected:
                raise RuntimeError(f"R3C signed capability binding drift: {key}")
    return payload
