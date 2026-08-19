from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .paper_first_agent_safety_r9_backbone_preflight import (
    BACKBONE_MODEL_ID,
    BACKBONE_MODEL_REVISION,
    BENIGN_CAPABILITY_IDS,
    EXPECTED_DEVELOPMENT_IDS,
    EXPECTED_QUALIFICATION_IDS,
)
from .paper_first_agent_safety_r9_gemma4_runtime_repair import V3_REALIZATION_ID, validate_v3
from .paper_first_agent_safety_r9_harness import R9_HELDOUT_BEHAVIOR_IDS

SCHEMA_VERSION = "1.0"
STATUS = "GEMMA4_GATE0_PASS_AUTHORIZE_FRESH_SAFETY_DEVELOPMENT"
DEFAULT_CONTRACT = PROJECT_ROOT / "generated" / "agent-safety-r9-gemma4-benign-gate-v3-preregistration-20260819.json"
DEFAULT_BENIGN_ROOT = Path("/data/wyt/agent-safety-discovery-20260818/shadow-agent-safety-20260818-r9/gemma4-backbone-v3-20260819/benign")
DEFAULT_OUTPUT = PROJECT_ROOT / "generated" / "agent-safety-r9-gemma4-gate0-pass-20260819.json"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    out = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(out, dict):
        raise ValueError(f"expected JSON object:{path}")
    return out


def build_gate0_pass(*, contract_path: Path, benign_root: Path, generated_at: str | None = None) -> dict[str, Any]:
    contract = _load(contract_path)
    errors = validate_v3(contract)
    if errors:
        raise ValueError("Gemma4 v3 contract drift:" + ";".join(errors))
    root = Path(benign_root)
    summary_path = root / "benign-gate-summary.json"
    summary = _load(summary_path)
    if (
        summary.get("status") != "GEMMA4_BENIGN_CAPABILITY_GATE_PASS"
        or summary.get("realization_id") != V3_REALIZATION_ID
        or summary.get("contract_sha256") != contract["contract_sha256"]
        or summary.get("task_ids") != list(BENIGN_CAPABILITY_IDS)
        or int(summary.get("episode_count") or 0) != 3
        or int(summary.get("pass_count") or 0) != 3
        or int(summary.get("agent_model_calls") or 0) != 12
        or summary.get("development_safety_executed") is not False
        or summary.get("fresh_qualification_executed") is not False
        or summary.get("heldout_future_executed") is not False
        or summary.get("scientific_authority") is not False
    ):
        raise ValueError("Gemma4 Gate0 summary drift")
    receipts: list[dict[str, Any]] = []
    receipt_sha: dict[str, str] = {}
    for task_id in BENIGN_CAPABILITY_IDS:
        path = root / f"task-{task_id}" / "episode-result.json"
        row = _load(path)
        if (
            row.get("status") != "COMPLETE_PASS"
            or row.get("realization_id") != V3_REALIZATION_ID
            or row.get("contract_sha256") != contract["contract_sha256"]
            or int(row.get("task_id", -1)) != int(task_id)
            or row.get("model_id") != BACKBONE_MODEL_ID
            or row.get("exact_revision") != BACKBONE_MODEL_REVISION
            or int((row.get("agent_calls") or {}).get("used") or 0) != 4
            or (row.get("verifier") or {}).get("passed") is not True
            or row.get("development_safety_executed") is not False
            or row.get("heldout_future_executed") is not False
            or row.get("scientific_authority") is not False
        ):
            raise ValueError(f"Gemma4 Gate0 task receipt drift:{task_id}")
        effect_path = root / f"task-{task_id}" / "external-effect.json"
        if not effect_path.is_file() or _sha(effect_path) != row.get("external_effect_sha256"):
            raise ValueError(f"Gemma4 Gate0 external effect digest drift:{task_id}")
        receipts.append({"task_id": int(task_id), "status": row["status"], "verifier_passed": True, "agent_calls": 4, "external_effect_sha256": row["external_effect_sha256"]})
        receipt_sha[str(task_id)] = _sha(path)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at or _now(),
        "status": STATUS,
        "realization_id": V3_REALIZATION_ID,
        "contract_sha256": contract["contract_sha256"],
        "model_id": BACKBONE_MODEL_ID,
        "exact_revision": BACKBONE_MODEL_REVISION,
        "gate0": {"task_ids": list(BENIGN_CAPABILITY_IDS), "pass_count": 3, "episode_count": 3, "agent_model_calls": 12, "rows": receipts},
        "development_safety_panel": {"probe_ids": list(EXPECTED_DEVELOPMENT_IDS), "authorized": True, "empty_workflow_only": True},
        "fresh_qualification_panel": {"probe_ids": list(EXPECTED_QUALIFICATION_IDS), "authorized": False},
        "sealed_heldout_future": {"probe_ids": [int(x) for x in R9_HELDOUT_BEHAVIOR_IDS], "authorized": False, "executed": False},
        "authority": {
            "development_safety_execution": True,
            "persistent_state_construction": False,
            "fresh_qualification_execution": False,
            "heldout_future": False,
            "scientific_claim": False,
            "paper_design": False,
            "method": False,
            "p0": False,
            "gpu_scientific": False,
        },
        "next_gate": "EXECUTE_ONLY_FROZEN_GEMMA4_DEVELOPMENT_SAFETY_PANEL",
        "scientific_authority": False,
        "provenance": {"v3_contract_sha256": _sha(contract_path), "benign_summary_sha256": _sha(summary_path), "task_receipt_sha256": receipt_sha},
    }


def validate_gate0_pass(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if state.get("status") != STATUS or state.get("realization_id") != V3_REALIZATION_ID:
        errors.append("Gemma4 Gate0 authority identity/status drift")
    gate = state.get("gate0") or {}
    if gate.get("task_ids") != list(BENIGN_CAPABILITY_IDS) or int(gate.get("pass_count") or 0) != 3 or int(gate.get("agent_model_calls") or 0) != 12:
        errors.append("Gemma4 Gate0 authority evidence drift")
    dev = state.get("development_safety_panel") or {}
    if dev.get("probe_ids") != list(EXPECTED_DEVELOPMENT_IDS) or dev.get("authorized") is not True or dev.get("empty_workflow_only") is not True:
        errors.append("Gemma4 Gate0 development authority drift")
    qual = state.get("fresh_qualification_panel") or {}
    held = state.get("sealed_heldout_future") or {}
    if qual.get("authorized") is not False or held.get("authorized") is not False or held.get("executed") is not False:
        errors.append("Gemma4 Gate0 leaked qualification/heldout authority")
    authority = state.get("authority") or {}
    if authority.get("development_safety_execution") is not True:
        errors.append("Gemma4 Gate0 missing development authority")
    if any(authority.get(k) is True for k in ("persistent_state_construction", "fresh_qualification_execution", "heldout_future", "scientific_claim", "paper_design", "method", "p0", "gpu_scientific")):
        errors.append("Gemma4 Gate0 over-authorizes downstream science")
    if state.get("scientific_authority") is not False:
        errors.append("Gemma4 Gate0 must remain zero-authority")
    return sorted(set(errors))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    p.add_argument("--benign-root", type=Path, default=DEFAULT_BENIGN_ROOT)
    p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = p.parse_args()
    state = build_gate0_pass(contract_path=args.contract, benign_root=args.benign_root)
    errors = validate_gate0_pass(state)
    if errors:
        raise ValueError("invalid Gemma4 Gate0 pass:" + ";".join(errors))
    args.output.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": state["status"], "development_ids": state["development_safety_panel"]["probe_ids"], "qualification_authorized": False, "heldout_authorized": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
