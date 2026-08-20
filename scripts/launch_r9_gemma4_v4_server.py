#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.paper_first_agent_safety_r9_gemma4_v4_development import (
    DEFAULT_LAUNCH_RECEIPT,
    DEFAULT_V3_CONTRACT,
    DEFAULT_V4_CONTRACT,
    V4_REALIZATION_ID,
    _sha,
    expected_server_command,
    load_v3_and_asset,
    load_v4,
)


def assert_port_free(host: str, port: int) -> None:
    with socket.socket() as sock:
        try:
            sock.bind((host, port))
        except OSError as error:
            raise RuntimeError(f"Gemma4 V4 frozen server port in use:{host}:{port}") from error


def main() -> None:
    parser = argparse.ArgumentParser(description="Launch Gemma4 V4 using the unchanged V3 runtime command")
    parser.add_argument("--v4-contract", type=Path, default=DEFAULT_V4_CONTRACT)
    parser.add_argument("--v3-contract", type=Path, default=DEFAULT_V3_CONTRACT)
    parser.add_argument("--launch-receipt", type=Path, default=DEFAULT_LAUNCH_RECEIPT)
    args = parser.parse_args()
    v4 = load_v4(args.v4_contract)
    v3, asset, asset_receipt = load_v3_and_asset(args.v3_contract, v4)
    command = expected_server_command(v3, asset)
    launch = v3["runtime_launch"]
    assert_port_free(str(launch["host"]), int(launch["port"]))
    receipt = {
        "schema_version": "1.0",
        "status": "GEMMA4_V4_SERVER_EXEC_PLANNED_UNCHANGED_V3_RUNTIME",
        "realization_id": V4_REALIZATION_ID,
        "v4_preregistration_sha256": _sha(args.v4_contract),
        "parent_v3_contract_sha256": _sha(args.v3_contract),
        "formal_asset_receipt_sha256": _sha(asset_receipt),
        "server_command": command,
        "runtime_changed_from_v3": False,
        "model_changed_from_v3": False,
        "secureclaw_changed_from_v3": False,
        "harmbench_execution_authorized": False,
        "fresh_qualification_execution_authorized": False,
        "heldout_future_authorized": False,
        "scientific_authority": False,
        "planned_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }
    args.launch_receipt.parent.mkdir(parents=True, exist_ok=True)
    args.launch_receipt.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.execv(command[0], command)


if __name__ == "__main__":
    main()
