# E2-R17 V3 Stage-A R3C — external signed support-capability exact-code review

Date: 2026-09-06
Role: fresh independent adversarial senior ICLR/NeurIPS/ICML agent-systems methodology/control-plane reviewer
Scope: ZERO-PROVIDER closure review of ONLY the two remaining R3B authority-provenance blockers.

## 0. Review rule

The valid R3B review already concluded:
- scientific equivalence to parent R3: PASS;
- single-use O_EXCL semantics: PASS;
- minter structural-only behavior: PASS;
- provider/Stage-B/scientific authority expansion: false;
- R3 scientific redesign required: false;
- new scientific experiment required: false.

R3B nevertheless failed because caller-writable review/permit/marker JSON had only content/hash consistency, not an origin-authenticated trust root. A field-complete caller could fabricate the full chain.

R3C changes ONLY that control plane. It introduces a dedicated Ed25519 trust root whose private key exists only on the independent host52 controller as a root-owned 0600 file; the repository and host69 contain only the public key. A support authorization is now structural only. Actual point-of-use authority is an externally signed capability that binds the exact contract, recovery authorization, terminal summary, support authorization, accepted control review, minter/gate/adjudicator hashes, run root, output path, single-use scope, and the hard provider boundary. The adjudicator itself verifies the signature and atomically consumes the capability before reading pool semantics. Therefore gate origin/marker origin is no longer a trust assumption.

Do NOT infer Stage-A support or Stage-B outcomes. Do NOT reopen the already-passed 158 provider tasks + one matched no-provider censor + one terminal technical missing, K=8, 7/7/8 opportunity geometry, >=4 mixed-pool threshold, no-replay/replacement, or Stage-B design unless exact R3C code changed those fields. Do NOT request more workload for appearance.

Hard gate remains: `NO_PROVIDER_CALL_BEFORE_2026-09-07 00:00:00 +0800`. PASS here creates no provider authority and cannot relax that time boundary.

Final verdict token must be exactly one:
- `PASS_TO_SEPARATE_R3C_RECOVERY_AUTHORIZATION`
- `REVISE_R3C_BEFORE_PROVIDER_RECOVERY`
- `STOP_R3_RECOVERY`

Also return `support_control_verdict` exactly one:
- `PASS_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE`
- `FAIL_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE`

## 1. Frozen hashes, parent equality, and prior blockers

```json
{
  "canonical_commit": "b77a8de00dd117de5051fd629164859a5de77542",
  "r3c_contract_sha256": "03b2608872424da2bdf78408266a69b28ff565bc9d84bf929aa82ba7bc11e030",
  "r3c_preflight_sha256": "5a82c3916fd883cdfe5fcfc542d531e16592b03fe65a74db8fa68c663d2bb021",
  "parent_r3_sha256": "3d0db7078c073613a27bc643675aa8755c7b2f241345ef6371570be48f2dd085",
  "parent_r3b_sha256": "7454608db38e58f2b39b412045e5a2ffe6f2b26db0d012bb2983e37259cb2da9",
  "r3b_review_sha256": "d89b4abfff996eece666b3e0ad3378982b1f7666ca9a39902fcd2d496b3bc64a",
  "r3b_review_verdict": "REVISE_R3B_BEFORE_PROVIDER_RECOVERY",
  "r3b_blockers": [
    "support authorization and consumption marker are content-validated but not origin-authenticated; field-complete caller-fabricated artifacts can satisfy the R3B adjudicator without proving passage through the reviewed minter/gate",
    "control-review receipt lacks an independently trusted provenance anchor; the regression suite lacks the fully populated forged-review + forged-permit + forged-marker direct-invocation adversarial path"
  ],
  "control_plane_revision": "R3C_EXTERNAL_SIGNED_SUPPORT_CAPABILITY",
  "trusted_external_signer": {
    "algorithm": "Ed25519",
    "private_key_in_repository": false,
    "private_key_location_class": "external controller only; root-owned on host52",
    "public_key_path": "generated/e2-r17-r3c-support-signing-public-key-20260906.pem",
    "public_key_sha256": "f4b73b89716bee28902feb699d9ab81822a986ac8b89235cf768407c3e01fda0",
    "signature_context": "E2-R17-R3C-POST-TERMINAL-SUPPORT-CAPABILITY-V1",
    "signer_host_role": "independent Research OS control-plane signer"
  },
  "science_key_equality_parent_r3": {
    "failed_r2_parent": true,
    "suite": true,
    "mindmemos": true,
    "provider_route": true,
    "model_identity_policy": true,
    "recovery_exceptions": true,
    "recovery_opportunity_manifest": true,
    "exact_once_acquisition": true,
    "equal_dose_support": true,
    "actor": true,
    "budget": true,
    "analysis_boundary": true,
    "stage_b_plan_no_authority": true,
    "runtime": true,
    "env_file_path": true,
    "run_root": true,
    "global_lease_path": true
  },
  "provider_runner_same_parent_r3": true,
  "recovery_authorizer_same_parent_r3": true,
  "authority_equal_parent_r3": true,
  "r3c_authority": {
    "analyzer": false,
    "heldout_evaluation": false,
    "paper_promotion": false,
    "public_benchmark": false,
    "second_backbone": false,
    "stage_a_provider_execution": false,
    "stage_b_learning_execution": false,
    "submission": false,
    "updater": false
  },
  "hard_provider_time_gate": "NO_PROVIDER_CALL_BEFORE_2026-09-07 00:00:00 +0800"
}
```

## 2. Cryptographic trust primitive — exact verifier/signer helper

### `research_pipeline/e2_r17_r3c_signed_support_capability.py` exact lines 1-133
Whole-file SHA256: `20b589917ea2ae8b8e00fb40cc008f11ce6d1f3853816fb30eb3cc56928f269a`

```python
from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

CAPABILITY_ARTIFACT_TYPE = "e2-r17-v3-stage-a-r3c-externally-signed-support-read-capability"
SIGNATURE_ALGORITHM = "Ed25519"
SIGNATURE_CONTEXT = "E2-R17-R3C-POST-TERMINAL-SUPPORT-CAPABILITY-V1"
CONTROL_PLANE_REVISION = "R3C_EXTERNAL_SIGNED_SUPPORT_CAPABILITY"
HARD_PROVIDER_NOT_BEFORE = "2026-09-07T00:00:00+08:00"
OPENSSL = "/usr/bin/openssl"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_payload_bytes(payload: dict[str, Any]) -> bytes:
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return SIGNATURE_CONTEXT.encode("utf-8") + b"\x00" + body


def public_key_fingerprint(path: Path) -> str:
    return sha256_file(path)


def _openssl(args: list[str], *, input_bytes: bytes | None = None) -> subprocess.CompletedProcess[bytes]:
    cmd = [OPENSSL, *args]
    result = subprocess.run(cmd, input=input_bytes, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"OpenSSL command failed ({result.returncode}): {' '.join(cmd)}; stderr={result.stderr.decode(errors='replace')[-1200:]}")
    return result


def _derived_public_key(private_key_path: Path) -> bytes:
    return _openssl(["pkey", "-in", str(private_key_path), "-pubout"]).stdout


def sign_document(*, payload: dict[str, Any], private_key_path: Path, public_key_path: Path) -> dict[str, Any]:
    if not private_key_path.is_file() or not public_key_path.is_file():
        raise RuntimeError("R3C signing key material absent")
    if _derived_public_key(private_key_path) != public_key_path.read_bytes():
        raise RuntimeError("R3C private/public signing key mismatch")
    raw = canonical_payload_bytes(payload)
    with tempfile.TemporaryDirectory(prefix="e2-r17-r3c-sign-") as tmp:
        msg = Path(tmp) / "message.bin"
        sig = Path(tmp) / "signature.bin"
        msg.write_bytes(raw)
        _openssl(["pkeyutl", "-sign", "-rawin", "-inkey", str(private_key_path), "-in", str(msg), "-out", str(sig)])
        signature = sig.read_bytes()
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
    raw = canonical_payload_bytes(payload)
    with tempfile.TemporaryDirectory(prefix="e2-r17-r3c-verify-") as tmp:
        msg = Path(tmp) / "message.bin"
        sig = Path(tmp) / "signature.bin"
        msg.write_bytes(raw)
        sig.write_bytes(signature)
        result = subprocess.run(
            [OPENSSL, "pkeyutl", "-verify", "-rawin", "-pubin", "-inkey", str(public_key_path), "-in", str(msg), "-sigfile", str(sig)],
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError("R3C signed capability signature verification failed")
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
```

## 3. External controller signer — exact code

### `scripts/sign_e2_r17_semantic_transfer_v3_stage_a_r3c_support_capability.py` exact lines 1-148
Whole-file SHA256: `aefdf214c92e2fbc6fb3735682de693368bc430dbf0c728a5bfb45b3a9472713`

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_r3c_signed_support_capability import (
    CONTROL_PLANE_REVISION,
    HARD_PROVIDER_NOT_BEFORE,
    public_key_fingerprint,
    sign_document,
)
EXPECTED_PUBLIC_KEY_SHA256 = "f4b73b89716bee28902feb699d9ab81822a986ac8b89235cf768407c3e01fda0"
SUPPORT_AUTH_STATUS = "AUTHORIZED_E2_R17_V3_R3_POST_TERMINAL_SUPPORT_READ"
CONTROL_REVIEW_VERDICT = "PASS_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def req(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        os.write(fd, raw)
        os.fsync(fd)
    finally:
        os.close(fd)


def build_payload(
    *,
    contract_path: Path,
    recovery_authorization_path: Path,
    summary_path: Path,
    support_authorization_path: Path,
    control_review_path: Path,
    public_key_path: Path,
    adjudication_output_path: Path,
    issued_at_utc: str | None = None,
    nonce: str | None = None,
) -> dict[str, Any]:
    contract = load(contract_path)
    support_auth = load(support_authorization_path)
    review = load(control_review_path)
    req(contract.get("control_plane_revision") == CONTROL_PLANE_REVISION, "R3C contract revision drift")
    signer = ((contract.get("post_terminal_support_read_control") or {}).get("trusted_external_signer") or {})
    req(signer.get("algorithm") == "Ed25519", "R3C contract signer algorithm drift")
    req(signer.get("public_key_sha256") == EXPECTED_PUBLIC_KEY_SHA256, "R3C contract signer public-key SHA drift")
    req(public_key_fingerprint(public_key_path) == EXPECTED_PUBLIC_KEY_SHA256, "R3C signer public key drift")
    req(support_auth.get("status") == SUPPORT_AUTH_STATUS, "R3C support authorization status drift")
    req(support_auth.get("contract_sha256") == sha(contract_path), "R3C support authorization contract SHA drift")
    req(support_auth.get("recovery_authorization_sha256") == sha(recovery_authorization_path), "R3C support authorization recovery-auth SHA drift")
    req(support_auth.get("terminal_summary_sha256") == sha(summary_path), "R3C support authorization terminal-summary SHA drift")
    review_row = support_auth.get("control_review") or {}
    req(review_row.get("sha256") == sha(control_review_path), "R3C support authorization/control-review SHA drift")
    req(review.get("status") == "COMPLETED" and review.get("surface") == "ChatGPT web" and review.get("model") == "GPT-5.6 Sol", "R3C control-review provenance drift")
    req(review.get("verdict") == CONTROL_REVIEW_VERDICT, "R3C control review did not PASS")
    req(review.get("control_plane_revision") == CONTROL_PLANE_REVISION, "R3C control-review revision drift")
    control = support_auth.get("bound_control_plane") or {}
    scope = support_auth.get("execution_scope") or {}
    req(Path(str(scope.get("required_adjudication_output") or "")).resolve() == adjudication_output_path.resolve(), "R3C adjudication output path drift")
    authority = support_auth.get("authority") or {}
    req(authority.get("stage_a_support_read") is True, "R3C support authorization lacks support-read authority")
    for key in ("stage_a_provider_execution", "stage_b_learning_execution", "updater", "heldout_evaluation", "analyzer", "second_backbone", "public_benchmark", "paper_promotion", "submission"):
        req(authority.get(key) is False, f"R3C support authorization overbroad: {key}")
    return {
        "capability_id": nonce or secrets.token_hex(32),
        "issued_at_utc": issued_at_utc or datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "control_plane_revision": CONTROL_PLANE_REVISION,
        "hard_provider_not_before": HARD_PROVIDER_NOT_BEFORE,
        "contract_sha256": sha(contract_path),
        "recovery_authorization_sha256": sha(recovery_authorization_path),
        "terminal_summary_sha256": sha(summary_path),
        "support_authorization_sha256": sha(support_authorization_path),
        "control_review_sha256": sha(control_review_path),
        "minter_sha256": str(control.get("minter_sha256") or ""),
        "gate_sha256": str(control.get("gate_sha256") or ""),
        "support_adjudicator_sha256": str(control.get("support_adjudicator_sha256") or ""),
        "required_adjudication_output": str(adjudication_output_path.resolve()),
        "required_run_root": str(Path(str(scope.get("required_run_root") or "")).resolve()),
        "single_use": True,
        "stage_a_support_read": True,
        "stage_a_provider_execution": False,
        "stage_b_learning_execution": False,
        "updater": False,
        "heldout_evaluation": False,
        "analyzer": False,
        "second_backbone": False,
        "public_benchmark": False,
        "paper_promotion": False,
        "submission": False,
        "scientific_authority": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--private-key", type=Path, required=True)
    ap.add_argument("--public-key", type=Path, required=True)
    ap.add_argument("--contract", type=Path, required=True)
    ap.add_argument("--recovery-authorization", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    ap.add_argument("--support-authorization", type=Path, required=True)
    ap.add_argument("--control-review", type=Path, required=True)
    ap.add_argument("--adjudication-output", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    req(not args.output.exists(), "R3C signed support capability already exists")
    payload = build_payload(
        contract_path=args.contract,
        recovery_authorization_path=args.recovery_authorization,
        summary_path=args.summary,
        support_authorization_path=args.support_authorization,
        control_review_path=args.control_review,
        public_key_path=args.public_key,
        adjudication_output_path=args.adjudication_output,
    )
    document = sign_document(payload=payload, private_key_path=args.private_key, public_key_path=args.public_key)
    atomic(args.output, document)
    print(json.dumps({"status": "SIGNED_R3C_SUPPORT_CAPABILITY", "capability_id": payload["capability_id"], "public_key_sha256": public_key_fingerprint(args.public_key), "provider_calls": 0, "scientific_authority": False}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## 4. Structural support request / minter — decisive exact code

### `scripts/authorize_e2_r17_semantic_transfer_v3_stage_a_r3_support_read.py` exact lines 75-110
Whole-file SHA256: `2c9af8fca89916e928b2219c6f87a455568ec1bb55db1494bcbe8bc6ddb71e67`

```python
    recovery_authorization_path: Path,
    summary_path: Path,
) -> dict[str, Any]:
    contract = load(contract_path)
    recovery_auth = load(recovery_authorization_path)
    summary = load(summary_path)
    csha = sha(contract_path)
    asha = sha(recovery_authorization_path)
    ssha = sha(summary_path)

    req(contract.get("status") == CONTRACT_STATUS, "R3 recovery contract status drift")
    req(contract.get("control_plane_revision") == CONTROL_PLANE_REVISION, "R3C support-control revision absent")
    trusted = ((contract.get("post_terminal_support_read_control") or {}).get("trusted_external_signer") or {})
    req(trusted.get("algorithm") == "Ed25519", "R3C trusted signer algorithm drift")
    expected_signer_sha = str(trusted.get("public_key_sha256") or "")
    trusted_key = bound(str(trusted.get("public_key_path") or ""))
    req(bool(expected_signer_sha) and trusted_key.is_file(), "R3C trusted signer public-key path/SHA absent")
    req(sha(trusted_key) == expected_signer_sha, "R3C trusted signer public-key content drift")
    req(trusted.get("private_key_in_repository") is False, "R3C trusted signer private key must remain external")
    req(recovery_auth.get("status") == RECOVERY_AUTH_STATUS, "R3 recovery authorization status drift")
    req(recovery_auth.get("contract_sha256") == csha, "R3 recovery authorization contract SHA drift")
    req(recovery_auth.get("single_use") is True and recovery_auth.get("exactly_once") is True, "R3 recovery authorization single-use drift")
    authority = recovery_auth.get("authority") or {}
    req(authority.get("stage_a_provider_execution") is True, "R3 recovery authorization provider authority absent")
    for key in (
        "stage_b_learning_execution",
        "updater",
        "heldout_evaluation",
        "analyzer",
        "second_backbone",
        "public_benchmark",
        "paper_promotion",
        "submission",
    ):
        req(authority.get(key) is False, f"R3 recovery authorization overbroad: {key}")

```
### `scripts/authorize_e2_r17_semantic_transfer_v3_stage_a_r3_support_read.py` exact lines 217-312
Whole-file SHA256: `2c9af8fca89916e928b2219c6f87a455568ec1bb55db1494bcbe8bc6ddb71e67`

```python
    gate_sha = sha(EXPECTED_GATE)
    support_adjudicator_sha = sha(EXPECTED_SUPPORT_ADJUDICATOR)
    state = validate_terminal_structure(
        contract_path=contract_path,
        recovery_authorization_path=recovery_authorization_path,
        summary_path=summary_path,
    )
    contract = state["contract"]
    bound_code = contract.get("bound_code") or {}
    trusted_signer = ((contract.get("post_terminal_support_read_control") or {}).get("trusted_external_signer") or {})
    for key, path, expected_sha in (
        ("post_terminal_support_minter", Path(__file__), minter_sha),
        ("post_terminal_support_gate", EXPECTED_GATE, gate_sha),
        ("equal_dose_adjudicator", EXPECTED_SUPPORT_ADJUDICATOR, support_adjudicator_sha),
    ):
        row = bound_code.get(key) or {}
        req(bound(str(row.get("path") or "")).resolve() == path.resolve(), f"R3B contract {key} path drift")
        req(row.get("sha256") == expected_sha, f"R3B contract {key} SHA drift")
    review = validate_control_review(
        control_review_path,
        minter_sha=minter_sha,
        gate_sha=gate_sha,
        support_adjudicator_sha=support_adjudicator_sha,
    )
    req(not adjudication_output_path.exists(), "R3 support adjudication output already exists")

    timestamp = created_at_utc or datetime.now(timezone.utc).isoformat(timespec="seconds")
    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-v3-stage-a-r3-post-terminal-support-read-authorization",
        "created_at_utc": timestamp,
        "status": SUPPORT_AUTH_STATUS,
        "single_use": True,
        "provider_calls": 0,
        "scientific_execution": False,
        "contract_path": str(contract_path),
        "contract_sha256": state["contract_sha256"],
        "recovery_authorization_path": str(recovery_authorization_path),
        "recovery_authorization_sha256": state["recovery_authorization_sha256"],
        "terminal_summary_path": str(summary_path),
        "terminal_summary_sha256": state["summary_sha256"],
        "terminal_lease_path": str(state["lease_path"]),
        "terminal_lease_sha256": sha(state["lease_path"]),
        "control_review": {
            "path": str(control_review_path.resolve()),
            "sha256": sha(control_review_path),
            "verdict": review["verdict"],
            "model": review["model"],
            "surface": review["surface"],
        },
        "bound_control_plane": {
            "minter_path": str(Path(__file__).resolve()),
            "minter_sha256": minter_sha,
            "gate_path": str(EXPECTED_GATE),
            "gate_sha256": gate_sha,
            "support_adjudicator_path": str(EXPECTED_SUPPORT_ADJUDICATOR),
            "support_adjudicator_sha256": support_adjudicator_sha,
        },
        "trusted_external_signer": {
            "algorithm": trusted_signer["algorithm"],
            "public_key_path": str(bound(str(trusted_signer["public_key_path"])).resolve()),
            "public_key_sha256": trusted_signer["public_key_sha256"],
            "private_key_in_repository": False,
            "signed_capability_required_at_point_of_use": True,
        },
        "execution_scope": {
            "required_adjudication_output": str(adjudication_output_path),
            "required_run_root": str(state["run_root"]),
            "provider_execution_tasks": 158,
            "sealed_k8_pools": 158,
            "terminal_technical_missing": BURNED,
            "matched_no_provider_censor": CENSOR,
            "support_required_mixed_pools_per_stream": 4,
            "opportunity_geometry": "7/7/8",
            "support_read_may_open_k8_pool_semantics": True,
            "support_read_before_terminal_recovery": False,
        },
        "authority": {
            "stage_a_support_read": True,
            "stage_a_provider_execution": False,
            "stage_b_learning_execution": False,
            "updater": False,
            "heldout_evaluation": False,
            "analyzer": False,
            "second_backbone": False,
            "public_benchmark": False,
            "paper_promotion": False,
            "submission": False,
        },
        "interpretation_boundary": "Structural post-terminal support-read request only. It is not sufficient authority by itself: point-of-use execution additionally requires an externally Ed25519-signed single-use capability from the separately trusted controller key. It grants no provider execution, updater, heldout, Stage-B execution, public benchmark, analyzer, or paper-claim authority.",
        "authority_requires_external_signed_capability": True,
    }
    return payload


def main() -> int:
```

## 5. Point-of-use adjudicator — authority verification + atomic consume

### `scripts/adjudicate_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py` exact lines 35-205
Whole-file SHA256: `93006d803f27b79142d803b1a43fe7210f876c20d7c518be8ef6e54a67b3b90c`

```python
def req(c: bool, m: str) -> None:
    if not c: raise RuntimeError(m)

def atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp=path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    os.replace(tmp,path)


def exclusive_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw=(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+"\n").encode("utf-8")
    fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    try:
        os.write(fd,raw); os.fsync(fd)
    finally:
        os.close(fd)
    dfd=os.open(path.parent,os.O_RDONLY)
    try: os.fsync(dfd)
    finally: os.close(dfd)

def bound(raw: str) -> Path:
    p=Path(raw); return p if p.is_absolute() else ROOT/p

def choose_four(stream_id: str, mixed: list[str]) -> list[str]:
    req(len(mixed)>=4,f"insufficient mixed pools: {stream_id}")
    return sorted(mixed,key=lambda t:hashlib.sha256(f"semantic-transfer-mrw4-v3|{stream_id}|{t}".encode()).hexdigest())[:4]

def choose_ten(scores: dict[str,float], *, descending: bool, salt: str) -> list[str]:
    req(len(scores)==20,"router stream universe drift")
    def key(s: str):
        primary=-scores[s] if descending else scores[s]
        return primary,hashlib.sha256(f"{salt}|{s}".encode()).hexdigest()
    return sorted(scores,key=key)[:10]

def failed_witness(rows: list[dict[str,Any]], winner: int) -> dict[str,Any]:
    xs=[r for r in rows if float(r["score"])==0.0 and int(r["rollout_index"])!=winner]
    req(bool(xs),"mixed pool lacks failed nonwinner")
    r=min(xs,key=lambda x:int(x["rollout_index"]))
    return {"rollout_index":int(r["rollout_index"]),"trajectory_path":str(r["trajectory_path"]),"trajectory_sha256":str(r["trajectory_sha256"]),"score":0.0,"selector":"lowest original rollout index among verifier-failure nonwinner trajectories"}


def validate_support_read_gate(*, contract: dict[str,Any], contract_path: Path, recovery_authorization_path: Path, summary_path: Path, support_authorization_path: Path, signed_capability_path: Path, output_path: Path, csha: str, asha: str) -> dict[str,Any]:
    req(contract.get("control_plane_revision")==CONTROL_PLANE_REVISION,"R3C support-control revision absent")
    support_auth=load(support_authorization_path)
    req(support_auth.get("status")==SUPPORT_AUTH_STATUS and support_auth.get("single_use") is True,"R3C support-read authorization invalid")
    req(support_auth.get("authority_requires_external_signed_capability") is True,"R3C support authorization does not require external capability")
    req(support_auth.get("contract_sha256")==csha,"R3C support-read contract SHA drift")
    req(support_auth.get("recovery_authorization_sha256")==asha,"R3C support-read recovery-authorization SHA drift")
    req(support_auth.get("terminal_summary_sha256")==sha(summary_path),"R3C support-read terminal-summary SHA drift")
    req(Path(str(support_auth.get("contract_path") or "")).resolve()==contract_path.resolve(),"R3C support-read contract path drift")
    req(Path(str(support_auth.get("recovery_authorization_path") or "")).resolve()==recovery_authorization_path.resolve(),"R3C support-read recovery-authorization path drift")
    req(Path(str(support_auth.get("terminal_summary_path") or "")).resolve()==summary_path.resolve(),"R3C support-read terminal-summary path drift")
    authority=support_auth.get("authority") or {}
    req(authority.get("stage_a_support_read") is True,"R3C Stage-A support-read authority absent")
    for key in ("stage_a_provider_execution","stage_b_learning_execution","updater","heldout_evaluation","analyzer","second_backbone","public_benchmark","paper_promotion","submission"):
        req(authority.get(key) is False,f"R3C support-read authorization overbroad: {key}")

    control=support_auth.get("bound_control_plane") or {}
    minter_path=Path(str(control.get("minter_path") or "")); gate_path=Path(str(control.get("gate_path") or "")); adjudicator_path=Path(str(control.get("support_adjudicator_path") or ""))
    req(minter_path.is_file() and control.get("minter_sha256")==sha(minter_path),"R3C minter provenance drift")
    req(gate_path.is_file() and control.get("gate_sha256")==sha(gate_path),"R3C gate provenance drift")
    req(adjudicator_path.resolve()==Path(__file__).resolve() and control.get("support_adjudicator_sha256")==sha(Path(__file__)),"R3C guarded adjudicator provenance drift")
    for key,path in (("post_terminal_support_minter",minter_path),("post_terminal_support_gate",gate_path),("equal_dose_adjudicator",Path(__file__))):
        row=(contract.get("bound_code") or {}).get(key) or {}
        req(bound(str(row.get("path") or "")).resolve()==path.resolve() and row.get("sha256")==sha(path),f"R3C contract bound-code drift: {key}")

    review_row=support_auth.get("control_review") or {}; review_path=Path(str(review_row.get("path") or ""))
    req(review_path.is_file() and review_row.get("sha256")==sha(review_path),"R3C control-review receipt binding drift")
    review=load(review_path)
    req(review.get("status")=="COMPLETED" and review.get("surface")=="ChatGPT web" and review.get("model")=="GPT-5.6 Sol","R3C control-review provenance drift")
    req(review.get("verdict")==CONTROL_REVIEW_VERDICT and review_row.get("verdict")==CONTROL_REVIEW_VERDICT,"R3C control-review verdict drift")
    req(review.get("control_plane_revision")==CONTROL_PLANE_REVISION,"R3C control-review revision drift")
    req(review.get("minter_sha256_acknowledged")==control.get("minter_sha256"),"R3C review/minter SHA drift")
    req(review.get("gate_sha256_acknowledged")==control.get("gate_sha256"),"R3C review/gate SHA drift")
    req(review.get("support_adjudicator_sha256_acknowledged")==control.get("support_adjudicator_sha256"),"R3C review/adjudicator SHA drift")
    req(review.get("stage_b_authority") is False and review.get("scientific_authority") is False,"R3C control review grants forbidden authority")

    scope=support_auth.get("execution_scope") or {}
    req(Path(str(scope.get("required_adjudication_output") or "")).resolve()==output_path.resolve(),"R3C support-adjudication output path drift")
    run_root=Path(str(scope.get("required_run_root") or "")); req(run_root.resolve()==Path(contract["run_root"]).resolve(),"R3C support-read run-root drift")

    trusted=((contract.get("post_terminal_support_read_control") or {}).get("trusted_external_signer") or {})
    req(trusted.get("algorithm")=="Ed25519","R3C trusted signer algorithm drift")
    pub_path=bound(str(trusted.get("public_key_path") or ""))
    expected_pub_sha=str(trusted.get("public_key_sha256") or "")
    req(pub_path.is_file() and sha(pub_path)==expected_pub_sha,"R3C trusted signer public-key binding drift")
    req(trusted.get("private_key_in_repository") is False,"R3C trusted signer private key must remain external")
    req(signed_capability_path.is_file(),"R3C externally signed support capability absent")
    capability_doc=load(signed_capability_path)
    expected_capability={
        "contract_sha256":csha,
        "recovery_authorization_sha256":asha,
        "terminal_summary_sha256":sha(summary_path),
        "support_authorization_sha256":sha(support_authorization_path),
        "control_review_sha256":sha(review_path),
        "minter_sha256":control.get("minter_sha256"),
        "gate_sha256":control.get("gate_sha256"),
        "support_adjudicator_sha256":control.get("support_adjudicator_sha256"),
        "required_adjudication_output":str(output_path.resolve()),
        "required_run_root":str(run_root.resolve()),
    }
    capability_payload=verify_document(capability_doc,public_key_path=pub_path,expected_public_key_sha256=expected_pub_sha,expected_payload_fields=expected_capability)
    req(bool(str(capability_payload.get("capability_id") or "").strip()),"R3C signed capability id absent")
    return {
        "support_authorization":support_auth,
        "support_authorization_sha256":sha(support_authorization_path),
        "control_review_sha256":sha(review_path),
        "signed_capability_sha256":sha(signed_capability_path),
        "signed_capability_payload":capability_payload,
        "trusted_public_key_sha256":expected_pub_sha,
        "run_root":run_root,
    }

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--contract",type=Path,required=True)
    ap.add_argument("--authorization",type=Path,required=True)
    ap.add_argument("--summary",type=Path,required=True)
    ap.add_argument("--support-authorization",type=Path,required=True)
    ap.add_argument("--signed-capability",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args(); req(not a.output.exists(),"R3 support adjudication already exists")
    c,auth,s=load(a.contract),load(a.authorization),load(a.summary)
    csha,asha=sha(a.contract),sha(a.authorization)
    req(c["status"]==CONTRACT_STATUS and auth["status"]==AUTH_STATUS,"R3 contract/auth status invalid")
    req(auth["contract_sha256"]==csha,"R3 auth contract drift")
    req(s["status"]==SUMMARY_STATUS and s["contract_sha256"]==csha and s["authorization_sha256"]==asha,"R3 terminal summary binding drift")
    req(s["planned_tasks"]==160 and s["provider_executable_tasks"]==158 and s["sealed_k8_pools"]==158,"R3 terminal accounting drift")
    req(s["terminal_technical_missing"]==1 and s["matched_no_provider_censor"]==1,"R3 exception accounting drift")
    req(s["support_inspected"] is False and s["updater_calls"]==0 and s["heldout_evaluations"]==0,"R3 crossed support/learning boundary")
    guard=validate_support_read_gate(contract=c,contract_path=a.contract,recovery_authorization_path=a.authorization,summary_path=a.summary,support_authorization_path=a.support_authorization,signed_capability_path=a.signed_capability,output_path=a.output,csha=csha,asha=asha)

    # Point-of-use authority is the externally signed capability, not the origin
    # of any caller-writable JSON permit/marker. Consume it atomically before
    # reading any pool semantics; an unexpected failure remains consumed.
    run_root:Path=guard["run_root"]
    control_root=run_root/"checkpoints/post_terminal_support_read"
    consumption=control_root/CONSUMPTION_NAME
    completion=control_root/COMPLETION_NAME
    req(not consumption.exists(),"R3C signed support capability already consumed; retry forbidden")
    req(not completion.exists(),"R3C support adjudication completion already exists")
    capability_payload=guard["signed_capability_payload"]
    consumption_payload={
        "schema_version":"1.0",
        "artifact_type":"e2-r17-v3-stage-a-r3c-signed-support-capability-consumption",
        "created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status":"CONSUMED_IN_FLIGHT_DO_NOT_RETRY",
        "capability_id":capability_payload["capability_id"],
        "signed_capability_path":str(a.signed_capability),
        "signed_capability_sha256":guard["signed_capability_sha256"],
        "trusted_public_key_sha256":guard["trusted_public_key_sha256"],
        "support_authorization_sha256":guard["support_authorization_sha256"],
        "terminal_summary_sha256":sha(a.summary),
        "required_output":str(a.output.resolve()),
        "adjudicator_sha256":sha(Path(__file__)),
        "hard_provider_not_before":HARD_PROVIDER_NOT_BEFORE,
        "automatic_retry":False,
        "stage_b_authority":False,
        "scientific_authority":False,
    }
    exclusive_json(consumption,consumption_payload)

    om=c["recovery_opportunity_manifest"]; opath=bound(om["path"])
    req(opath.is_file() and sha(opath)==om["sha256"],"R3 opportunity manifest drift")
    o=load(opath); stream_ids=[str(x) for x in o["ordered_stream_ids"]]
    streams={str(k):[str(x) for x in v] for k,v in o["support_eligible_task_ids_by_stream"].items()}
    req(list(streams)==stream_ids and len(stream_ids)==20,"R3 support stream order drift")
    req(len(streams["stv3-cgwb-00"])==len(streams["stv3-cgwp-00"])==7,"R3 matched 7/7 geometry drift")
    req(BURNED not in sum(streams.values(),[]) and CENSOR not in sum(streams.values(),[]),"excluded task leaked into R3 support")
```

## 6. Gate wrapper — validation and completion semantics

### `scripts/run_e2_r17_semantic_transfer_v3_stage_a_r3_support_adjudication_gate.py` exact lines 55-270
Whole-file SHA256: `0abd0325414838bc0692caeed7908f5ab4be1d36126c44cca1ed587d2f343752`

```python
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def validate_support_authorization(
    *,
    support_authorization_path: Path,
    contract_path: Path,
    recovery_authorization_path: Path,
    summary_path: Path,
    signed_capability_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    support_auth = load(support_authorization_path)
    contract = load(contract_path)
    req(support_auth.get("status") == SUPPORT_AUTH_STATUS, "post-terminal support-read authorization status drift")
    req(support_auth.get("single_use") is True, "post-terminal support-read authorization is not single-use")
    req(support_auth.get("provider_calls") == 0, "post-terminal support-read authorization provider-call drift")
    req(support_auth.get("scientific_execution") is False, "post-terminal support-read authorization incorrectly records scientific execution")
    req(support_auth.get("authority_requires_external_signed_capability") is True, "R3C support authorization does not require external signed capability")
    req(contract.get("control_plane_revision") == CONTROL_PLANE_REVISION, "R3C contract revision drift")

    authority = support_auth.get("authority") or {}
    req(authority.get("stage_a_support_read") is True, "Stage-A support-read authority absent")
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
    ):
        req(authority.get(key) is False, f"post-terminal support-read authorization overbroad: {key}")

    req(support_auth.get("contract_sha256") == sha(contract_path), "post-terminal support-read contract SHA drift")
    req(support_auth.get("recovery_authorization_sha256") == sha(recovery_authorization_path), "post-terminal support-read recovery-authorization SHA drift")
    req(support_auth.get("terminal_summary_sha256") == sha(summary_path), "post-terminal support-read summary SHA drift")
    req(Path(str(support_auth.get("contract_path") or "")).resolve() == contract_path.resolve(), "post-terminal support-read contract path drift")
    req(Path(str(support_auth.get("recovery_authorization_path") or "")).resolve() == recovery_authorization_path.resolve(), "post-terminal support-read recovery-authorization path drift")
    req(Path(str(support_auth.get("terminal_summary_path") or "")).resolve() == summary_path.resolve(), "post-terminal support-read summary path drift")

    summary = load(summary_path)
    req(summary.get("status") == SUMMARY_STATUS, "terminal summary no longer at pending-support boundary")
    req(summary.get("support_inspected") is False, "terminal summary indicates support already inspected")
    req(summary.get("stage_b_authority") is False, "terminal summary grants Stage-B authority")

    control = support_auth.get("bound_control_plane") or {}
    minter_path = Path(str(control.get("minter_path") or ""))
    gate_path = Path(str(control.get("gate_path") or ""))
    adjudicator_path = Path(str(control.get("support_adjudicator_path") or ""))
    req(minter_path.is_file() and control.get("minter_sha256") == sha(minter_path), "support-read minter provenance drift")
    req(gate_path.resolve() == Path(__file__).resolve() and control.get("gate_sha256") == sha(Path(__file__)), "support-read gate SHA drift")
    req(adjudicator_path.resolve() == EXPECTED_SUPPORT_ADJUDICATOR.resolve(), "support adjudicator path drift")
    req(EXPECTED_SUPPORT_ADJUDICATOR.is_file() and control.get("support_adjudicator_sha256") == sha(EXPECTED_SUPPORT_ADJUDICATOR), "guarded support adjudicator SHA drift")

    review_row = support_auth.get("control_review") or {}
    review_path = Path(str(review_row.get("path") or ""))
    req(review_path.is_file() and review_row.get("sha256") == sha(review_path), "support-read control-review receipt binding drift")
    review = load(review_path)
    req(review.get("status") == "COMPLETED" and review.get("surface") == "ChatGPT web" and review.get("model") == "GPT-5.6 Sol", "support-read control-review provenance drift")
    req(review.get("verdict") == CONTROL_REVIEW_VERDICT and review_row.get("verdict") == CONTROL_REVIEW_VERDICT, "support-read control-review verdict drift")
    req(review.get("control_plane_revision") == CONTROL_PLANE_REVISION, "support-read control-review revision drift")
    req(review.get("minter_sha256_acknowledged") == control.get("minter_sha256"), "support-read review/minter SHA drift")
    req(review.get("gate_sha256_acknowledged") == control.get("gate_sha256"), "support-read review/gate SHA drift")
    req(review.get("support_adjudicator_sha256_acknowledged") == control.get("support_adjudicator_sha256"), "support-read review/adjudicator SHA drift")
    req(review.get("stage_b_authority") is False and review.get("scientific_authority") is False, "support-read control review grants forbidden authority")

    scope = support_auth.get("execution_scope") or {}
    req(Path(str(scope.get("required_adjudication_output") or "")).resolve() == output_path.resolve(), "support adjudication output path drift")
    req(scope.get("provider_execution_tasks") == 158 and scope.get("sealed_k8_pools") == 158, "post-terminal support-read geometry drift")
    req(scope.get("opportunity_geometry") == "7/7/8", "post-terminal support-read opportunity geometry drift")
    req(scope.get("support_required_mixed_pools_per_stream") == 4, "post-terminal support threshold drift")

    run_root = Path(str(scope.get("required_run_root") or ""))
    req(run_root.is_dir(), "post-terminal support-read run root absent")
    lease_path = Path(str(support_auth.get("terminal_lease_path") or ""))
    req(lease_path.is_file() and support_auth.get("terminal_lease_sha256") == sha(lease_path), "post-terminal support-read lease binding drift")

    trusted = ((contract.get("post_terminal_support_read_control") or {}).get("trusted_external_signer") or {})
    req(trusted.get("algorithm") == "Ed25519", "R3C trusted signer algorithm drift")
    public_key_path = Path(str(trusted.get("public_key_path") or ""))
    if not public_key_path.is_absolute():
        public_key_path = ROOT / public_key_path
    expected_public_sha = str(trusted.get("public_key_sha256") or "")
    req(public_key_path.is_file() and sha(public_key_path) == expected_public_sha, "R3C trusted signer public-key binding drift")
    req(trusted.get("private_key_in_repository") is False, "R3C trusted signer private key must remain external")
    req(signed_capability_path.is_file(), "R3C signed support capability absent")
    capability_document = load(signed_capability_path)
    capability_payload = verify_document(
        capability_document,
        public_key_path=public_key_path,
        expected_public_key_sha256=expected_public_sha,
        expected_payload_fields={
            "contract_sha256": sha(contract_path),
            "recovery_authorization_sha256": sha(recovery_authorization_path),
            "terminal_summary_sha256": sha(summary_path),
            "support_authorization_sha256": sha(support_authorization_path),
            "control_review_sha256": review_row["sha256"],
            "minter_sha256": control.get("minter_sha256"),
            "gate_sha256": control.get("gate_sha256"),
            "support_adjudicator_sha256": control.get("support_adjudicator_sha256"),
            "required_adjudication_output": str(output_path.resolve()),
            "required_run_root": str(run_root.resolve()),
        },
    )
    return {"support_authorization": support_auth, "summary": summary, "run_root": run_root, "lease_path": lease_path, "signed_capability_payload": capability_payload, "signed_capability_sha256": sha(signed_capability_path), "trusted_public_key_sha256": expected_public_sha}


def default_invoke(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)


def run_gate(
    *,
    support_authorization_path: Path,
    contract_path: Path,
    recovery_authorization_path: Path,
    summary_path: Path,
    signed_capability_path: Path,
    output_path: Path,
    invoke: Callable[[list[str]], subprocess.CompletedProcess[str]] = default_invoke,
    python_executable: str = sys.executable,
) -> dict[str, Any]:
    req(not output_path.exists(), "R3 support adjudication output already exists")
    state = validate_support_authorization(
        support_authorization_path=support_authorization_path,
        contract_path=contract_path,
        recovery_authorization_path=recovery_authorization_path,
        summary_path=summary_path,
        signed_capability_path=signed_capability_path,
        output_path=output_path,
    )
    run_root: Path = state["run_root"]
    control_root = run_root / "checkpoints/post_terminal_support_read"
    consumption = control_root / CONSUMPTION_NAME
    completion = control_root / COMPLETION_NAME
    req(not consumption.exists(), "post-terminal support-read authorization already consumed; retry forbidden")
    req(not completion.exists(), "post-terminal support adjudication completion receipt already exists")

    auth_sha = sha(support_authorization_path)
    summary_sha = sha(summary_path)
    support_auth = state["support_authorization"]

    # The gate is now an orchestration wrapper. Point-of-use authorization and
    # one-shot consumption are enforced inside the adjudicator against the
    # externally signed capability, so caller-writable marker origin is no
    # longer a trust boundary.
    command = [
        python_executable,
        str(EXPECTED_SUPPORT_ADJUDICATOR),
        "--contract",
        str(contract_path),
        "--authorization",
        str(recovery_authorization_path),
        "--summary",
        str(summary_path),
        "--support-authorization",
        str(support_authorization_path),
        "--signed-capability",
        str(signed_capability_path),
        "--output",
        str(output_path),
    ]
    result = invoke(command)
    if result.returncode not in {0, 3}:
        raise RuntimeError(
            "R3 support adjudicator failed outside terminal PASS/HOLD states; externally signed support capability remains consumed and manual review is required. "
            f"returncode={result.returncode}; stdout_tail={result.stdout[-1200:]}; stderr_tail={result.stderr[-1200:]}"
        )
    req(output_path.is_file(), "R3 support adjudicator returned terminal code without output artifact")
    req(consumption.is_file(), "R3C adjudicator returned without signed-capability consumption artifact")
    consumption_row = load(consumption)
    req(consumption_row.get("signed_capability_sha256") == state["signed_capability_sha256"], "R3C consumption/capability SHA drift")
    req(consumption_row.get("trusted_public_key_sha256") == state["trusted_public_key_sha256"], "R3C consumption trusted-key drift")
    adjudication = load(output_path)
    expected_statuses = {
        0: "PASS_SEMANTIC_TRANSFER_V3_R3_MATCHED_CENSOR_EQUAL_DOSE_SUPPORT_READY_FOR_STAGE_B_DESIGN",
        3: "HOLD_SEMANTIC_TRANSFER_V3_R3_INSUFFICIENT_EQUAL_DOSE_SUPPORT",
    }
    req(adjudication.get("status") == expected_statuses[result.returncode], "R3 support adjudicator terminal status/returncode mismatch")
    authority = adjudication.get("authority") or {}
    req(authority.get("execute_stage_b") is False, "R3 support adjudication improperly grants Stage-B execution")
    req(authority.get("heldout_evaluation") is False, "R3 support adjudication improperly grants heldout evaluation")
    req(authority.get("analyzer") is False, "R3 support adjudication improperly grants analyzer authority")
    req(authority.get("paper_promotion") is False, "R3 support adjudication improperly grants paper-promotion authority")

    completion_payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-v3-stage-a-r3-post-terminal-support-read-completion",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "COMPLETED_POST_TERMINAL_SUPPORT_READ",
        "support_authorization_sha256": auth_sha,
        "signed_capability_path": str(signed_capability_path),
        "signed_capability_sha256": state["signed_capability_sha256"],
        "trusted_public_key_sha256": state["trusted_public_key_sha256"],
        "consumption_path": str(consumption),
        "consumption_sha256": sha(consumption),
        "terminal_summary_sha256": summary_sha,
        "adjudication_output": str(output_path),
        "adjudication_output_sha256": sha(output_path),
        "adjudication_status": adjudication["status"],
        "adjudicator_returncode": result.returncode,
        "stage_b_authority": False,
        "automatic_retry": False,
    }
    _exclusive_json(completion, completion_payload)
    return {
        "status": completion_payload["status"],
        "adjudication_status": adjudication["status"],
        "returncode": result.returncode,
        "consumption_path": str(consumption),
        "completion_path": str(completion),
```

## 7. Verdict-changing regression tests

### `research_pipeline/test_e2_r17_semantic_transfer_v3_r3_support_read_control.py` exact lines 220-529
Whole-file SHA256: `34ba48994eb8c9c208b6c16a1bc8be7aa7e41fa730f317cee98bcf3513852749`

```python
            adjudication_output_path=fixture["adjudication_output"],
            created_at_utc="2026-09-07T00:01:00+08:00",
        )
        write_json(fixture["support_auth"], payload)
        return payload

    def build_signed_capability(self, fixture: dict[str, Path]) -> dict:
        support_auth = json.loads(fixture["support_auth"].read_text())
        control = support_auth["bound_control_plane"]
        scope = support_auth["execution_scope"]
        payload = {
            "capability_id": "test-capability-r3c",
            "issued_at_utc": "2026-09-07T00:01:00+08:00",
            "control_plane_revision": minter.CONTROL_PLANE_REVISION,
            "hard_provider_not_before": HARD_PROVIDER_NOT_BEFORE,
            "contract_sha256": sha(fixture["contract"]),
            "recovery_authorization_sha256": sha(fixture["recovery_auth"]),
            "terminal_summary_sha256": sha(fixture["summary"]),
            "support_authorization_sha256": sha(fixture["support_auth"]),
            "control_review_sha256": sha(fixture["control_review"]),
            "minter_sha256": control["minter_sha256"],
            "gate_sha256": control["gate_sha256"],
            "support_adjudicator_sha256": control["support_adjudicator_sha256"],
            "required_adjudication_output": str(fixture["adjudication_output"].resolve()),
            "required_run_root": str(Path(scope["required_run_root"]).resolve()),
            "single_use": True,
            "stage_a_support_read": True,
            "stage_a_provider_execution": False,
            "stage_b_learning_execution": False,
            "updater": False,
            "heldout_evaluation": False,
            "analyzer": False,
            "second_backbone": False,
            "public_benchmark": False,
            "paper_promotion": False,
            "submission": False,
            "scientific_authority": False,
        }
        document = sign_document(payload=payload, private_key_path=fixture["private_key"], public_key_path=fixture["public_key"])
        write_json(fixture["signed_capability"], document)
        return document

    def test_minter_rejects_absent_or_nonterminal_summary(self) -> None:
        fixture = self.make_fixture()
        missing = fixture["root"] / "missing-summary.json"
        with self.assertRaises(FileNotFoundError):
            minter.build_support_authorization(
                contract_path=fixture["contract"],
                recovery_authorization_path=fixture["recovery_auth"],
                summary_path=missing,
                control_review_path=fixture["control_review"],
                output_path=fixture["support_auth"],
                adjudication_output_path=fixture["adjudication_output"],
            )
        summary = json.loads(fixture["summary"].read_text())
        summary["status"] = "RUNNING"
        write_json(fixture["summary"], summary)
        with self.assertRaisesRegex(RuntimeError, "terminal summary status drift"):
            self.build_auth(fixture)

    def test_minter_rejects_support_already_inspected(self) -> None:
        fixture = self.make_fixture()
        summary = json.loads(fixture["summary"].read_text())
        summary["support_inspected"] = True
        write_json(fixture["summary"], summary)
        with self.assertRaisesRegex(RuntimeError, "already inspected support"):
            self.build_auth(fixture)

    def test_minter_rejects_recovery_authorization_hash_drift(self) -> None:
        fixture = self.make_fixture()
        auth = json.loads(fixture["recovery_auth"].read_text())
        auth["tampered"] = True
        write_json(fixture["recovery_auth"], auth)
        with self.assertRaisesRegex(RuntimeError, "summary authorization SHA drift"):
            self.build_auth(fixture)

    def test_minter_grants_only_stage_a_support_read(self) -> None:
        fixture = self.make_fixture()
        payload = self.build_auth(fixture)
        self.assertTrue(payload["authority"]["stage_a_support_read"])
        self.assertFalse(payload["authority"]["stage_a_provider_execution"])
        self.assertFalse(payload["authority"]["stage_b_learning_execution"])
        self.assertFalse(payload["authority"]["heldout_evaluation"])
        self.assertEqual(payload["provider_calls"], 0)
        self.assertFalse(payload["scientific_execution"])

    def test_gate_refuses_invalid_support_authorization(self) -> None:
        fixture = self.make_fixture()
        payload = self.build_auth(fixture)
        payload["authority"]["stage_a_support_read"] = False
        write_json(fixture["support_auth"], payload)
        with self.assertRaisesRegex(RuntimeError, "support-read authority absent"):
            gate.run_gate(
                support_authorization_path=fixture["support_auth"],
                contract_path=fixture["contract"],
                recovery_authorization_path=fixture["recovery_auth"],
                summary_path=fixture["summary"],
                signed_capability_path=fixture["signed_capability"],
                output_path=fixture["adjudication_output"],
            )
        consumption = fixture["run"] / "checkpoints/post_terminal_support_read" / gate.CONSUMPTION_NAME
        self.assertFalse(consumption.exists())

    def test_gate_rejects_forged_permit_without_review_provenance(self) -> None:
        fixture = self.make_fixture()
        payload = self.build_auth(fixture)
        forged_review = fixture["root"] / "forged-review.json"
        write_json(forged_review, {"status": "COMPLETED", "surface": "ChatGPT web", "model": "GPT-5.6 Sol", "verdict": minter.CONTROL_REVIEW_VERDICT})
        payload["control_review"]["path"] = str(forged_review)
        payload["control_review"]["sha256"] = sha(forged_review)
        write_json(fixture["support_auth"], payload)
        with self.assertRaisesRegex(RuntimeError, "review/minter SHA drift|control-review revision drift|control-review receipt binding drift"):
            gate.run_gate(
                support_authorization_path=fixture["support_auth"],
                contract_path=fixture["contract"],
                recovery_authorization_path=fixture["recovery_auth"],
                summary_path=fixture["summary"],
                signed_capability_path=fixture["signed_capability"],
                output_path=fixture["adjudication_output"],
            )

    def test_guarded_adjudicator_rejects_direct_invocation_without_support_permit(self) -> None:
        fixture = self.make_fixture()
        command = [
            sys.executable,
            str(minter.EXPECTED_SUPPORT_ADJUDICATOR),
            "--contract",
            str(fixture["contract"]),
            "--authorization",
            str(fixture["recovery_auth"]),
            "--summary",
            str(fixture["summary"]),
            "--output",
            str(fixture["adjudication_output"]),
        ]
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--support-authorization", result.stderr)
        self.assertFalse(fixture["adjudication_output"].exists())

    def test_full_forged_review_permit_and_capability_cannot_directly_invoke_adjudicator(self) -> None:
        fixture = self.make_fixture()
        support_auth = self.build_auth(fixture)

        # Construct the verdict-changing adversarial path from the R3B reviewer:
        # a field-complete forged review plus a field-complete forged permit.
        genuine_review = json.loads(fixture["control_review"].read_text())
        forged_review = fixture["root"] / "field-complete-forged-review.json"
        write_json(forged_review, genuine_review)
        support_auth["control_review"]["path"] = str(forged_review.resolve())
        support_auth["control_review"]["sha256"] = sha(forged_review)
        write_json(fixture["support_auth"], support_auth)

        control = support_auth["bound_control_plane"]
        scope = support_auth["execution_scope"]
        payload = {
            "capability_id": "attacker-fabricated-capability",
            "issued_at_utc": "2026-09-07T00:01:00+08:00",
            "control_plane_revision": minter.CONTROL_PLANE_REVISION,
            "hard_provider_not_before": HARD_PROVIDER_NOT_BEFORE,
            "contract_sha256": sha(fixture["contract"]),
            "recovery_authorization_sha256": sha(fixture["recovery_auth"]),
            "terminal_summary_sha256": sha(fixture["summary"]),
            "support_authorization_sha256": sha(fixture["support_auth"]),
            "control_review_sha256": sha(forged_review),
            "minter_sha256": control["minter_sha256"],
            "gate_sha256": control["gate_sha256"],
            "support_adjudicator_sha256": control["support_adjudicator_sha256"],
            "required_adjudication_output": str(fixture["adjudication_output"].resolve()),
            "required_run_root": str(Path(scope["required_run_root"]).resolve()),
            "single_use": True,
            "stage_a_support_read": True,
            "stage_a_provider_execution": False,
            "stage_b_learning_execution": False,
            "updater": False,
            "heldout_evaluation": False,
            "analyzer": False,
            "second_backbone": False,
            "public_benchmark": False,
            "paper_promotion": False,
            "submission": False,
            "scientific_authority": False,
        }
        wrong_private_path = fixture["root"] / "attacker-private.pem"
        wrong_public_path = fixture["root"] / "attacker-public.pem"
        subprocess.run([OPENSSL, "genpkey", "-algorithm", "ED25519", "-out", str(wrong_private_path)], check=True, capture_output=True)
        with wrong_public_path.open("wb") as handle:
            subprocess.run([OPENSSL, "pkey", "-in", str(wrong_private_path), "-pubout"], check=True, stdout=handle, stderr=subprocess.PIPE)
        forged_capability = sign_document(payload=payload, private_key_path=wrong_private_path, public_key_path=wrong_public_path)
        # The attacker can copy every public metadata field, including the trusted
        # public-key fingerprint, but cannot create a signature verifiable by it.
        forged_capability["signature"]["public_key_sha256"] = sha(fixture["public_key"])
        write_json(fixture["signed_capability"], forged_capability)

        command = [
            sys.executable,
            str(minter.EXPECTED_SUPPORT_ADJUDICATOR),
            "--contract", str(fixture["contract"]),
            "--authorization", str(fixture["recovery_auth"]),
            "--summary", str(fixture["summary"]),
            "--support-authorization", str(fixture["support_auth"]),
            "--signed-capability", str(fixture["signed_capability"]),
            "--output", str(fixture["adjudication_output"]),
        ]
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("signature verification failed", result.stderr)
        self.assertFalse(fixture["adjudication_output"].exists())
        consumption = fixture["run"] / "checkpoints/post_terminal_support_read" / gate.CONSUMPTION_NAME
        self.assertFalse(consumption.exists())

    def test_gate_consumes_once_and_fail_closes_on_unexpected_adjudicator_error(self) -> None:
        fixture = self.make_fixture()
        self.build_auth(fixture)
        self.build_signed_capability(fixture)

        def failed_invoke(command: list[str]) -> subprocess.CompletedProcess[str]:
            self.assertIn("--signed-capability", command)
            control = fixture["run"] / "checkpoints/post_terminal_support_read"
            write_json(
                control / gate.CONSUMPTION_NAME,
                {
                    "artifact_type": "e2-r17-v3-stage-a-r3c-signed-support-capability-consumption",
                    "status": "CONSUMED_IN_FLIGHT_DO_NOT_RETRY",
                    "signed_capability_sha256": sha(fixture["signed_capability"]),
                    "trusted_public_key_sha256": sha(fixture["public_key"]),
                    "stage_b_authority": False,
                    "scientific_authority": False,
                },
            )
            return subprocess.CompletedProcess(command, 2, stdout="", stderr="synthetic failure")

        with self.assertRaisesRegex(RuntimeError, "signed support capability remains consumed"):
            gate.run_gate(
                support_authorization_path=fixture["support_auth"],
                contract_path=fixture["contract"],
                recovery_authorization_path=fixture["recovery_auth"],
                summary_path=fixture["summary"],
                signed_capability_path=fixture["signed_capability"],
                output_path=fixture["adjudication_output"],
                invoke=failed_invoke,
            )
        control = fixture["run"] / "checkpoints/post_terminal_support_read"
        self.assertTrue((control / gate.CONSUMPTION_NAME).is_file())
        self.assertFalse((control / gate.COMPLETION_NAME).exists())
        with self.assertRaisesRegex(RuntimeError, "already consumed"):
            gate.run_gate(
                support_authorization_path=fixture["support_auth"],
                contract_path=fixture["contract"],
                recovery_authorization_path=fixture["recovery_auth"],
                summary_path=fixture["summary"],
                signed_capability_path=fixture["signed_capability"],
                output_path=fixture["adjudication_output"],
                invoke=failed_invoke,
            )

    def test_gate_accepts_terminal_pass_without_stage_b_authority(self) -> None:
        fixture = self.make_fixture()
        self.build_auth(fixture)
        self.build_signed_capability(fixture)

        def passed_invoke(command: list[str]) -> subprocess.CompletedProcess[str]:
            self.assertIn("--support-authorization", command)
            self.assertIn("--signed-capability", command)
            control = fixture["run"] / "checkpoints/post_terminal_support_read"
            write_json(
                control / gate.CONSUMPTION_NAME,
                {
                    "artifact_type": "e2-r17-v3-stage-a-r3c-signed-support-capability-consumption",
                    "status": "CONSUMED_IN_FLIGHT_DO_NOT_RETRY",
                    "signed_capability_sha256": sha(fixture["signed_capability"]),
                    "trusted_public_key_sha256": sha(fixture["public_key"]),
                    "stage_b_authority": False,
                    "scientific_authority": False,
                },
            )
            output = Path(command[command.index("--output") + 1])
            write_json(
                output,
                {
                    "status": "PASS_SEMANTIC_TRANSFER_V3_R3_MATCHED_CENSOR_EQUAL_DOSE_SUPPORT_READY_FOR_STAGE_B_DESIGN",
                    "authority": {
                        "prepare_stage_b_contract": True,
                        "execute_stage_b": False,
                        "heldout_evaluation": False,
                        "analyzer": False,
                        "paper_promotion": False,
                    },
                },
            )
            return subprocess.CompletedProcess(command, 0, stdout="synthetic pass", stderr="")

        result = gate.run_gate(
            support_authorization_path=fixture["support_auth"],
            contract_path=fixture["contract"],
            recovery_authorization_path=fixture["recovery_auth"],
            summary_path=fixture["summary"],
            signed_capability_path=fixture["signed_capability"],
            output_path=fixture["adjudication_output"],
            invoke=passed_invoke,
        )
        self.assertEqual(result["status"], "COMPLETED_POST_TERMINAL_SUPPORT_READ")
        self.assertFalse(result["stage_b_authority"])
        completion = fixture["run"] / "checkpoints/post_terminal_support_read" / gate.COMPLETION_NAME
        self.assertTrue(completion.is_file())
        self.assertFalse(json.loads(completion.read_text())["stage_b_authority"])


if __name__ == "__main__":
    unittest.main()
```

## 8. Frozen zero-provider preflight

Preflight SHA256: `5a82c3916fd883cdfe5fcfc542d531e16592b03fe65a74db8fa68c663d2bb021`

```json
{
  "actual_signed_capability_minted": false,
  "actual_support_read_authorization_minted": false,
  "artifact_type": "e2-r17-semantic-transfer-v3-stage-a-r3c-external-signed-capability-zero-provider-preflight",
  "authority": {
    "heldout": false,
    "paper_claim": false,
    "provider_recovery": false,
    "stage_a_support_read": false,
    "stage_b_execution": false
  },
  "checks": {
    "all_bound_code_hashes_match": true,
    "external_ed25519_trust_root_bound_and_private_key_untracked": true,
    "fresh_r3c_recovery_lineage_absent": true,
    "full_field_complete_forged_chain_negative_test_present": true,
    "provider_recovery_runner_and_authorizer_unchanged": true,
    "support_control_compile_pass": true,
    "support_control_tests_10_of_10_pass": true,
    "support_read_and_signed_capability_artifacts_absent": true
  },
  "contract_path": "generated/e2-r17-semantic-transfer-v3-stage-a-contract-r3c-signed-support-capability-20260906.json",
  "contract_sha256": "03b2608872424da2bdf78408266a69b28ff565bc9d84bf929aa82ba7bc11e030",
  "created_at_utc": "2026-09-05T16:55:59+00:00",
  "fresh_identity_qualified": false,
  "hard_provider_time_gate": "NO_PROVIDER_CALL_BEFORE_2026-09-07 00:00:00 +0800",
  "next_gate": "FRESH_GPT56_SOL_EXTRA_HIGH_R3C_EXACT_CODE_REVIEW_THEN_PROVIDER_RESET_THEN_FRESH_IDENTITY_THEN_SEPARATE_RECOVERY_AUTHORIZATION",
  "parent_r3_contract_path": "generated/e2-r17-semantic-transfer-v3-stage-a-contract-r3-recovery-20260905.json",
  "parent_r3_contract_sha256": "3d0db7078c073613a27bc643675aa8755c7b2f241345ef6371570be48f2dd085",
  "parent_r3b_contract_path": "generated/e2-r17-semantic-transfer-v3-stage-a-contract-r3b-support-guard-20260905.json",
  "parent_r3b_contract_sha256": "7454608db38e58f2b39b412045e5a2ffe6f2b26db0d012bb2983e37259cb2da9",
  "provider_calls": 0,
  "r3b_review_path": "generated/e2-r17-v3-r3b-support-control-gpt56-review-v2-20260906.json",
  "r3b_review_sha256": "d89b4abfff996eece666b3e0ad3378982b1f7666ca9a39902fcd2d496b3bc64a",
  "r3c_recovery_authorization_minted": false,
  "schema_version": "1.0",
  "science_keys_equal_parent_r3": [
    "failed_r2_parent",
    "suite",
    "mindmemos",
    "provider_route",
    "model_identity_policy",
    "recovery_exceptions",
    "recovery_opportunity_manifest",
    "exact_once_acquisition",
    "equal_dose_support",
    "actor",
    "budget",
    "analysis_boundary",
    "stage_b_plan_no_authority",
    "runtime",
    "env_file_path",
    "run_root",
    "global_lease_path"
  ],
  "scientific_execution": false,
  "stage_b_authority": false,
  "status": "PASS_ZERO_PROVIDER_SEMANTIC_TRANSFER_V3_STAGE_A_R3C_EXTERNAL_SIGNED_CAPABILITY_PREFLIGHT",
  "support_inspected": false,
  "trusted_public_key_path": "/data/wyt/agent-self-evolution-observatory/worktrees/e2-r17-semantic-transfer-v3-review-repair-20260903/generated/e2-r17-r3c-support-signing-public-key-20260906.pem",
  "trusted_public_key_sha256": "f4b73b89716bee28902feb699d9ab81822a986ac8b89235cf768407c3e01fda0",
  "unit_tests": {
    "passed": 10,
    "suite": "research_pipeline.test_e2_r17_semantic_transfer_v3_r3_support_read_control",
    "total": 10
  }
}
```

## 9. Audit questions

A. **Trust root.** Given the exact code, is the Ed25519 public key independently pinned by the R3C contract while the matching private key is absent from the repository/host69 trust domain? Does a caller who can fabricate arbitrary JSON on 69 still lack the ability to mint a capability accepted by `verify_document`?

B. **Full-chain forgery.** Does the regression `test_full_forged_review_permit_and_capability_cannot_directly_invoke_adjudicator` actually instantiate the prior reviewer’s decisive case in the R3C architecture: field-complete forged review + field-complete forged support request + attacker-generated signed-capability document with copied public metadata? Does it fail specifically at signature verification before output or consumption?

C. **Direct invocation semantics.** In R3C, should a direct adjudicator invocation carrying a *valid externally signed capability* be considered an authorized point-of-use call rather than a bypass, because the capability itself is now the authority and the adjudicator validates/consumes it? Conversely, is direct invocation without a valid signed capability fail-closed?

D. **Single use / retry.** Is consumption now stronger than R3B because the adjudicator itself does `O_CREAT|O_EXCL` only after full signature/binding validation and before any pool-semantic read? On unexpected post-consumption failure, is automatic retry still forbidden?

E. **Binding completeness.** Does the signed payload bind enough immutable context: contract SHA, recovery-auth SHA, terminal-summary SHA, support-request SHA, control-review SHA, exact minter/gate/adjudicator hashes, run root, output path, hard provider timestamp, single-use/support-read-only authority? Is any verdict-changing substitution/replay path still visible?

F. **External signer implementation.** Does the signer refuse a wrong private/public pair and hard-pin the production public-key SHA? Is it acceptable that possession/use of the root-only host52 private key is the trust root, rather than trying to prove origin through caller-writable JSON?

G. **Scientific equivalence / authority.** Do the contract/preflight equality checks and unchanged provider runner/authorizer establish that R3C did not change the R3 scientific geometry? Does any R3C path mint provider, Stage-B, heldout, updater, analyzer, paper, or submission authority?

H. **Next consequence.** If PASS, is the only consequence: wait for Sep-7 reset, run a fresh identity qualification, then allow a *separate* R3C provider-recovery authorization decision; after terminal recovery, support request + externally signed capability are still separately required, and Stage B remains unauthorized?

## 10. Required synthesis

Return exactly these fields before the final token:
- `contract_sha256_acknowledged`: exact R3C contract SHA
- `preflight_sha256_acknowledged`: exact R3C preflight SHA
- `control_plane_revision`: `R3C_EXTERNAL_SIGNED_SUPPORT_CAPABILITY`
- `trusted_public_key_sha256_acknowledged`: exact public-key SHA
- `capability_verifier_sha256_acknowledged`: exact verifier-module SHA
- `external_signer_sha256_acknowledged`: exact signer-script SHA
- `minter_sha256_acknowledged`: exact minter SHA
- `gate_sha256_acknowledged`: exact gate SHA
- `support_adjudicator_sha256_acknowledged`: exact adjudicator SHA
- `tests_sha256_acknowledged`: exact tests SHA
- `scientific_equivalence_to_parent_r3`: PASS/FAIL
- `external_trust_root_closed`: PASS/FAIL
- `full_forged_chain_closed`: PASS/FAIL
- `direct_bypass_closed`: PASS/FAIL
- `single_use_gate`: PASS/FAIL
- `review_provenance_closed`: PASS/FAIL
- `runtime_compatibility`: PASS/FAIL
- `tests_preflight`: PASS/FAIL
- `provider_recovery_authority_affected`: true/false
- `r3_contract_redesign_required`: true/false
- `new_scientific_experiment_required`: true/false
- `stage_b_authority`: false
- `scientific_authority`: false
- `support_control_verdict`: exact PASS/FAIL token from Section 0
- `execution_recommendation`: `ALLOW_SEPARATE_R3C_RECOVERY_AUTHORIZATION_AFTER_HARD_RESET_AND_FRESH_IDENTITY` or `DO_NOT_AUTHORIZE_R3C_RECOVERY`
- `remaining_blockers`: [] or exact blockers

Then end with exactly one final verdict token from Section 0.
