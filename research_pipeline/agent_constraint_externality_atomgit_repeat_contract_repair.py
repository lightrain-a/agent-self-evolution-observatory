from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline import agent_constraint_externality_atomgit_repeat_common as c
from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value

ROOT = Path(__file__).resolve().parents[1]
G = ROOT / "generated"
RECEIPT = G / "agent-constraint-externality-atomgit-repeat-r2-contract-interface-repair-20260906.json"
RUNNER = ROOT / "research_pipeline/agent_constraint_externality_atomgit_repeat_execute.py"
BRIDGE = ROOT / "research_pipeline/agent_constraint_externality_atomgit_repeat_mcp_bridge.py"


class RepairError(RuntimeError):
    pass


def readj(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def writej(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verified(path: Path, status: str) -> dict[str, Any]:
    payload = readj(path)
    if payload.get("object_id") != OBJECT_ID or payload.get("status") != status:
        raise RepairError(f"identity/status mismatch: {path}")
    claimed = payload.get("content_sha256")
    unsigned = dict(payload); unsigned.pop("content_sha256", None)
    if claimed != sha256_value(unsigned):
        raise RepairError(f"content hash mismatch: {path}")
    return payload


def build() -> dict[str, Any]:
    if RECEIPT.exists():
        raise RepairError("repair receipt already exists")
    auth = verified(c.AUTH, "USER_AUTHORIZED_ATOMGIT_REPEAT_DEV_R2_ONLY")
    contract = verified(c.CONTRACT, "ATOMGIT_REPEAT_DEV_R2_EXECUTION_AUTHORIZED")
    old_contract = dict(contract)
    run_root = c.RUN_ROOT
    ledger_exists = c.LEDGER.exists()
    runtime_unit_dirs = []
    if run_root.exists():
        runtime_unit_dirs = [p.name for p in run_root.iterdir() if p.is_dir()]
    if ledger_exists or runtime_unit_dirs:
        raise RepairError("contract interface repair is permitted only before any repeat dispatch/runtime unit")
    if contract["human_authorization_content_sha256"] != auth["content_sha256"]:
        raise RepairError("human authorization binding drift")
    rb = contract.get("runtime_bindings") or {}
    panel = contract.get("panel") or {}
    expected_runner = sha256_file(RUNNER)
    expected_bridge = sha256_file(BRIDGE)
    if rb.get("runner_sha256") != expected_runner or rb.get("bridge_sha256") != expected_bridge:
        raise RepairError("existing nested runtime binding drift")
    if not isinstance(panel.get("unit_ids_sha256"), str):
        raise RepairError("panel unit hash missing")

    scientific_before = {
        "execution_id": contract["execution_id"],
        "model": contract["model"],
        "panel": contract["panel"],
        "execution_policy": contract["execution_policy"],
        "analysis_policy": contract["analysis_policy"],
        "authority": contract["authority"],
        "repair_closeout_content_sha256": contract["repair_closeout_content_sha256"],
        "repair_manifest_content_sha256": contract["repair_manifest_content_sha256"],
        "preexec_freeze_content_sha256": contract["preexec_freeze_content_sha256"],
    }
    contract["runner_sha256"] = expected_runner
    contract["bridge_sha256"] = expected_bridge
    contract["unit_ids_sha256"] = panel["unit_ids_sha256"]
    contract["schema_version"] = "ace-repeat-dev-r2-execution-contract-v1-interface-repair1"
    contract.pop("content_sha256", None)
    contract["content_sha256"] = sha256_value(contract)
    writej(c.CONTRACT, contract)

    scientific_after = {
        "execution_id": contract["execution_id"],
        "model": contract["model"],
        "panel": contract["panel"],
        "execution_policy": contract["execution_policy"],
        "analysis_policy": contract["analysis_policy"],
        "authority": contract["authority"],
        "repair_closeout_content_sha256": contract["repair_closeout_content_sha256"],
        "repair_manifest_content_sha256": contract["repair_manifest_content_sha256"],
        "preexec_freeze_content_sha256": contract["preexec_freeze_content_sha256"],
    }
    if sha256_value(scientific_before) != sha256_value(scientific_after):
        raise RepairError("scientific contract content changed during interface repair")

    receipt: dict[str, Any] = {
        "schema_version": "ace-repeat-dev-r2-contract-interface-repair-v1",
        "object_id": OBJECT_ID,
        "status": "ATOMGIT_REPEAT_DEV_R2_CONTRACT_INTERFACE_REPAIR_PASS_ZERO_DISPATCH",
        "reason": "Frozen executor reads runner_sha256, bridge_sha256, and unit_ids_sha256 at the contract top level; the authorized contract stored the same already-frozen values only in nested audit objects.",
        "old_contract_content_sha256": old_contract["content_sha256"],
        "new_contract_content_sha256": contract["content_sha256"],
        "human_authorization_content_sha256": auth["content_sha256"],
        "scientific_contract_sha256_before": sha256_value(scientific_before),
        "scientific_contract_sha256_after": sha256_value(scientific_after),
        "scientific_contract_unchanged": True,
        "fields_copied_without_recomputation": {
            "runner_sha256": rb["runner_sha256"],
            "bridge_sha256": rb["bridge_sha256"],
            "unit_ids_sha256": panel["unit_ids_sha256"],
        },
        "repeat_ledger_existed_before_repair": ledger_exists,
        "repeat_runtime_unit_count_before_repair": len(runtime_unit_dirs),
        "provider_requests_created": 0,
        "scientific_repeat_outcomes_created": 0,
        "authority": auth["authority"],
        "downstream_authority_opened": False,
    }
    receipt["content_sha256"] = sha256_value(receipt)
    writej(RECEIPT, receipt)
    return receipt


def main() -> None:
    print(json.dumps(build(), sort_keys=True))


if __name__ == "__main__":
    main()
