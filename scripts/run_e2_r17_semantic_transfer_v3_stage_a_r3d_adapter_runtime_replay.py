#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import socket
import stat
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_r3d_runtime_replay_attestation import sign_document

STATUS = "PASS_R3D_RECOVERY_AUTHORIZATION_ADAPTER_FROZEN_RUNTIME_REPLAY"
EXPECTED_CONTRACT_SHA256 = "21f7a50f4e14f48a139ecfa122f7c8a443d4195a1ade0267ccececcb6e424717"
EXPECTED_PREFLIGHT_SHA256 = "8894bf0e76d4f1b0a8f101ca55df0ff8728696bc29bf888e6287ab2046c724fa"
EXPECTED_R3D_REVIEW_SHA256 = "f97071244451d8e0f7ea1d30f31689948e03858665eeed983802670d38a522fb"
EXPECTED_PROVIDER_RUNNER_SHA256 = "491b2ae6e53fcfe732f15ef263cc365ce61846b3219d7a13fe70e3834f6d3c89"
EXPECTED_HOSTNAME = "ubuntu"
EXPECTED_HOST_IPV4 = "222.20.126.69"
HOST69_PRIVATE_KEY = Path("/home/wyt/.research-os/e2-r17-r3d-runtime-replay-attestation/ed25519-private.pem")
HOST69_PUBLIC_KEY = ROOT / "generated/e2-r17-r3d-host69-runtime-replay-public-key-20260906.pem"
HOST69_PUBLIC_KEY_SHA256 = "cc454f52d82b28c7eb33e0f938d3328b65427b3192d1a4992e96333298c1f270"
ADAPTER = ROOT / "scripts/authorize_e2_r17_semantic_transfer_v3_stage_a_r3d_recovery.py"
ADAPTER_TESTS = ROOT / "research_pipeline/test_e2_r17_semantic_transfer_v3_r3d_recovery_authorization_adapter.py"
PROVIDER_RUNNER = ROOT / "scripts/run_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py"
TEST_MODULE = "research_pipeline.test_e2_r17_semantic_transfer_v3_r3d_recovery_authorization_adapter"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def req(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _local_ipv4_addresses() -> set[str]:
    ip = shutil.which("ip")
    req(bool(ip), "R3D runtime replay cannot resolve ip utility")
    result = subprocess.run([str(ip), "-4", "-o", "addr", "show"], capture_output=True, text=True, check=False)
    req(result.returncode == 0, f"R3D runtime replay ip inspection failed: {result.stderr[-800:]}")
    addresses: set[str] = set()
    for line in result.stdout.splitlines():
        fields = line.split()
        for idx, value in enumerate(fields):
            if value == "inet" and idx + 1 < len(fields):
                addresses.add(fields[idx + 1].split("/", 1)[0])
    return addresses


def _validate_host69_signing_identity() -> None:
    req(socket.gethostname() == EXPECTED_HOSTNAME, f"R3D runtime replay hostname drift: {socket.gethostname()}")
    req(EXPECTED_HOST_IPV4 in _local_ipv4_addresses(), "R3D runtime replay host IPv4 drift")
    req(HOST69_PRIVATE_KEY.is_file(), "R3D host69 runtime replay private key absent")
    req(HOST69_PUBLIC_KEY.is_file(), "R3D host69 runtime replay public key absent")
    req(sha(HOST69_PUBLIC_KEY) == HOST69_PUBLIC_KEY_SHA256, "R3D host69 runtime replay public-key SHA drift")
    mode = stat.S_IMODE(HOST69_PRIVATE_KEY.stat().st_mode)
    req(mode == 0o600, f"R3D host69 runtime replay private-key mode drift: {oct(mode)}")
    req(HOST69_PRIVATE_KEY.stat().st_uid == os.geteuid(), "R3D host69 runtime replay private-key owner drift")


def build_replay(*, contract_path: Path, preflight_path: Path, r3d_review_path: Path) -> dict[str, Any]:
    contract = load(contract_path)
    csha = sha(contract_path)
    psha = sha(preflight_path)
    rsha = sha(r3d_review_path)
    req(csha == EXPECTED_CONTRACT_SHA256, "R3D runtime replay contract SHA drift")
    req(psha == EXPECTED_PREFLIGHT_SHA256, "R3D runtime replay preflight SHA drift")
    req(rsha == EXPECTED_R3D_REVIEW_SHA256, "R3D runtime replay accepted review SHA drift")
    req(sha(PROVIDER_RUNNER) == EXPECTED_PROVIDER_RUNNER_SHA256, "R3D runtime replay provider runner SHA drift")

    expected_python_path = Path(contract["runtime"]["python_executable"])
    expected_python = expected_python_path.resolve()
    actual_python = Path(sys.executable).resolve()
    req(actual_python == expected_python, f"R3D runtime replay must run under frozen Python: expected={expected_python} actual={actual_python}")
    freeze_path = Path(contract["runtime"]["freeze_path"])
    req(freeze_path.is_file() and sha(freeze_path) == contract["runtime"]["freeze_sha256"], "R3D runtime replay Python freeze drift")
    _validate_host69_signing_identity()

    compile_result = subprocess.run([str(actual_python), "-m", "py_compile", str(ADAPTER)], cwd=ROOT, text=True, capture_output=True, check=False)
    req(compile_result.returncode == 0, f"R3D adapter compile failed: {compile_result.stderr[-1200:]}")
    test_result = subprocess.run([str(actual_python), "-m", "unittest", "-q", TEST_MODULE], cwd=ROOT, text=True, capture_output=True, check=False)
    req(test_result.returncode == 0, f"R3D adapter frozen-runtime tests failed: {test_result.stdout[-1200:]} {test_result.stderr[-1200:]}")

    return {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-v3-stage-a-r3d-recovery-authorization-adapter-frozen-runtime-replay",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": STATUS,
        "execution_host_role": "HOST69_FROZEN_RUNTIME",
        "execution_host_origin": "HOST69_LOCAL_ED25519_PRIVATE_KEY",
        "hostname": socket.gethostname(),
        "execution_host_ipv4": EXPECTED_HOST_IPV4,
        "python_executable": str(expected_python_path),
        "python_freeze_path": str(freeze_path),
        "python_freeze_sha256": sha(freeze_path),
        "contract_sha256": csha,
        "preflight_sha256": psha,
        "r3d_review_sha256": rsha,
        "adapter_sha256": sha(ADAPTER),
        "adapter_tests_sha256": sha(ADAPTER_TESTS),
        "provider_runner_sha256": sha(PROVIDER_RUNNER),
        "runtime_replay_tool_sha256": sha(Path(__file__)),
        "host69_public_key_sha256": HOST69_PUBLIC_KEY_SHA256,
        "compile_pass": True,
        "unit_tests_pass": True,
        "unit_tests_failed": 0,
        "test_module": TEST_MODULE,
        "provider_calls": 0,
        "scientific_execution": False,
        "support_inspected": False,
        "stage_b_authority": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", type=Path, required=True)
    ap.add_argument("--preflight", type=Path, required=True)
    ap.add_argument("--r3d-review", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    req(not args.output.exists(), "R3D runtime replay attestation already exists")
    payload = build_replay(contract_path=args.contract, preflight_path=args.preflight, r3d_review_path=args.r3d_review)
    document = sign_document(payload=payload, private_key_path=HOST69_PRIVATE_KEY, public_key_path=HOST69_PUBLIC_KEY)
    atomic(args.output, document)
    print(json.dumps({
        "status": payload["status"],
        "execution_host_role": payload["execution_host_role"],
        "execution_host_origin": payload["execution_host_origin"],
        "hostname": payload["hostname"],
        "execution_host_ipv4": payload["execution_host_ipv4"],
        "output": str(args.output),
        "output_sha256": sha(args.output),
        "host69_public_key_sha256": HOST69_PUBLIC_KEY_SHA256,
        "provider_calls": 0,
        "scientific_execution": False,
        "stage_b_authority": False,
    }, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
