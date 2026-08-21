from __future__ import annotations

import argparse
import hashlib
import json
import socket
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONTRACT = ROOT / "generated/d2-proxy-reward-live-terminal-contract.json"
DEFAULT_OUTPUT = ROOT / "generated/d2-proxy-reward-live-terminal-environment-preflight.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tcp_probe(url: str, timeout_seconds: float) -> dict[str, Any]:
    parsed = urlparse(url)
    host = str(parsed.hostname or "")
    if not host:
        return {"host": "", "port": None, "reachable": False, "error_class": "INVALID_URL"}
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    try:
        with socket.create_connection((host, port), timeout=timeout_seconds):
            return {"host": host, "port": port, "reachable": True, "error_class": ""}
    except Exception as error:
        return {"host": host, "port": port, "reachable": False, "error_class": type(error).__name__}


def run(contract_path: Path, *, timeout_seconds: float = 5.0) -> dict[str, Any]:
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    if contract.get("status") != "FROZEN_WAITING_ENVIRONMENT":
        raise ValueError("live-terminal-contract-not-frozen")

    asset_checks: list[dict[str, Any]] = []
    for key, value in (contract.get("source_artifacts") or {}).items():
        if not key.endswith("_sha256"):
            continue
        path_key = key[:-7]
        raw_path = (contract.get("source_artifacts") or {}).get(path_key)
        if not raw_path:
            asset_checks.append({"key": key, "path_key": path_key, "pass": False, "reason": "missing-path-binding"})
            continue
        path = ROOT / str(raw_path)
        actual = _sha(path) if path.is_file() else ""
        asset_checks.append({"key": key, "path_key": path_key, "pass": actual == value, "expected_sha256": value, "actual_sha256": actual})

    assets_pass = bool(asset_checks) and all(row["pass"] for row in asset_checks)
    env = contract["environment"]
    shopping = _tcp_probe(str(env["source_shopping_url"]), timeout_seconds)
    reset = _tcp_probe(str(env["source_reset_url"]), timeout_seconds)
    ports_ready = bool(shopping["reachable"] and reset["reachable"])
    ready = assets_pass and ports_ready

    return {
        "schema_version": "1.0",
        "preflight_id": "D2-PROXY-REWARD-LIVE-WEBARENA-TERMINAL-ENVIRONMENT-PREFLIGHT",
        "contract": str(contract_path.relative_to(ROOT)),
        "contract_sha256": _sha(contract_path),
        "status": "READY_FOR_STATE_FIDELITY_PREFLIGHT" if ready else "HOLD_ENVIRONMENT",
        "asset_gate": {"pass": assets_pass, "checks": asset_checks},
        "network_gate": {
            "method": "TCP_CONNECT_ONLY_NO_HTTP_RESET_OR_EPISODE_EXECUTION",
            "shopping": shopping,
            "reset": reset,
            "pass": ports_ready,
        },
        "next_if_ready": "Run reset plus frozen prefix replay for all four future tasks and require exact intervention-state SHA matches before any policy episode.",
        "on_hold": "No scientific update. Do not replace live execution with additional surrogate rollouts.",
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--timeout-seconds", type=float, default=5.0)
    args = parser.parse_args()
    payload = run(args.contract, timeout_seconds=args.timeout_seconds)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
