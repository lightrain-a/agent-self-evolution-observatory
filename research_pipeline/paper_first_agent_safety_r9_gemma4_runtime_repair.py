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
from .paper_first_agent_safety_r9_gemma4_benign_protocol import (
    V2_REALIZATION_ID,
    validate_v2_preregistration,
)
from .paper_first_agent_safety_r9_harness import R9_HELDOUT_BEHAVIOR_IDS

SCHEMA_VERSION = "1.0"
V2_STOP_STATUS = "STOP_PROTOCOL_GEMMA4_MM_BATCH_TOKEN_FLOOR"
V3_REALIZATION_ID = "R9-FRESH-BACKBONE-GEMMA4-26B-A4B-IT-V3"
V3_STATUS = "PREREGISTERED_GEMMA4_RUNTIME_MM_BATCH_TOKEN_REPAIR"
V3_MAX_NUM_BATCHED_TOKENS = 2496
EXPECTED_ERROR = "max_tokens_per_mm_item (2496) is larger than max_num_batched_tokens (2048)"

DEFAULT_V2 = PROJECT_ROOT / "generated" / "agent-safety-r9-gemma4-benign-gate-v2-preregistration-20260819.json"
DEFAULT_STOP = PROJECT_ROOT / "generated" / "agent-safety-r9-gemma4-benign-v2-runtime-protocol-stop-20260819.json"
DEFAULT_V3 = PROJECT_ROOT / "generated" / "agent-safety-r9-gemma4-benign-gate-v3-preregistration-20260819.json"
DEFAULT_LOG = Path("/data/wyt/agent-safety-discovery-20260818/r9-gemma4-benign-v2-server-20260819.log")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _canonical_sha(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _contract_sha(payload: dict[str, Any]) -> str:
    body = dict(payload)
    body.pop("generated_at", None)
    body.pop("contract_sha256", None)
    return _canonical_sha(body)


def _load(path: Path) -> dict[str, Any]:
    out = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(out, dict):
        raise ValueError(f"expected JSON object:{path}")
    return out


def build_v2_runtime_stop(*, v2_path: Path, log_path: Path, generated_at: str | None = None) -> dict[str, Any]:
    v2 = _load(v2_path)
    errors = validate_v2_preregistration(v2)
    if errors:
        raise ValueError("Gemma4 v2 preregistration drift:" + ";".join(errors))
    text = Path(log_path).read_text(encoding="utf-8", errors="replace")
    if EXPECTED_ERROR not in text:
        raise ValueError("Gemma4 v2 expected deterministic vLLM compatibility error missing")
    if "POST " in text:
        raise ValueError("Gemma4 v2 log contains HTTP POST; zero-generation protocol-stop no longer valid")
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at or _now(),
        "status": V2_STOP_STATUS,
        "stop_class": "PROTOCOL_STOP",
        "failure_layer": "protocol_validity",
        "realization_id": V2_REALIZATION_ID,
        "contract_sha256": v2["contract_sha256"],
        "protocol_valid": False,
        "model_id": BACKBONE_MODEL_ID,
        "exact_revision": BACKBONE_MODEL_REVISION,
        "model_loading_started": False,
        "model_inference_calls_executed": 0,
        "benign_tasks_executed": 0,
        "development_safety_executed": False,
        "fresh_qualification_executed": False,
        "heldout_future_executed": False,
        "root_cause": "Frozen vLLM 0.20 resolves Gemma4 max model length 262144 and disables chunked multimodal input; its default max_num_batched_tokens=2048 is below Gemma4 max_tokens_per_mm_item=2496, so server construction fails before model weights or any request are processed.",
        "minimal_protocol_repair": {"parameter": "max_num_batched_tokens", "from": 2048, "to": V3_MAX_NUM_BATCHED_TOKENS, "source": "deterministic vLLM error lower bound", "outcome_selected": False},
        "principle_dead_end_certified": False,
        "principle_falsified": False,
        "scientific_authority": False,
        "provenance": {"v2_preregistration_sha256": _sha(v2_path), "server_log_sha256": _sha(log_path)},
    }


def build_v3(*, v2_path: Path, stop_path: Path, generated_at: str | None = None) -> dict[str, Any]:
    v2 = _load(v2_path)
    if validate_v2_preregistration(v2):
        raise ValueError("Gemma4 v2 preregistration drift")
    stop = _load(stop_path)
    if stop.get("status") != V2_STOP_STATUS or stop.get("stop_class") != "PROTOCOL_STOP" or int(stop.get("model_inference_calls_executed", -1)) != 0:
        raise ValueError("Gemma4 v2 runtime-stop drift")
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at or _now(),
        "status": V3_STATUS,
        "realization_id": V3_REALIZATION_ID,
        "parent_realization_id": V2_REALIZATION_ID,
        "parent_contract_sha256": v2["contract_sha256"],
        "parent_stop_class": "PROTOCOL_STOP",
        "scientific_object_unchanged": True,
        "single_changed_axis": "runtime_operationalization",
        "model": v2["model"],
        "frozen_axes": v2["frozen_axes"],
        "probe_selection": v2["probe_selection"],
        "benign_gate": v2["benign_gate"],
        "formal_asset": v2["formal_asset"],
        "runtime_launch": {
            "host": "127.0.0.1",
            "port": 18002,
            "dtype": "bfloat16",
            "served_model_name": BACKBONE_MODEL_ID,
            "max_num_batched_tokens": V3_MAX_NUM_BATCHED_TOKENS,
            "max_model_len_override": None,
            "gpu_memory_utilization_override": None,
            "quantization": None,
            "repair_is_exact_error_lower_bound": True,
            "other_runtime_overrides_forbidden": True,
        },
        "future_gates": {
            "development_safety_ids": list(EXPECTED_DEVELOPMENT_IDS),
            "fresh_qualification_ids": list(EXPECTED_QUALIFICATION_IDS),
            "sealed_heldout_future_ids": [int(x) for x in R9_HELDOUT_BEHAVIOR_IDS],
            "development_safety_authorized": False,
            "fresh_qualification_authorized": False,
            "heldout_future_authorized": False,
        },
        "authority": {
            "model_loading": True,
            "benign_capability_execution": True,
            "development_safety_execution": False,
            "persistent_state_construction": False,
            "fresh_qualification_execution": False,
            "heldout_future": False,
            "scientific_claim": False,
            "paper_design": False,
            "method": False,
            "p0": False,
            "gpu_scientific": False,
        },
        "scientific_authority": False,
        "provenance": {"v2_preregistration_sha256": _sha(v2_path), "v2_runtime_stop_sha256": _sha(stop_path)},
    }
    payload["contract_sha256"] = _contract_sha(payload)
    return payload


def validate_v3(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if state.get("status") != V3_STATUS or state.get("realization_id") != V3_REALIZATION_ID:
        errors.append("Gemma4 v3 identity/status drift")
    if state.get("single_changed_axis") != "runtime_operationalization" or state.get("scientific_object_unchanged") is not True:
        errors.append("Gemma4 v3 scientific-object drift")
    launch = state.get("runtime_launch") or {}
    if launch.get("max_num_batched_tokens") != V3_MAX_NUM_BATCHED_TOKENS or launch.get("max_model_len_override") is not None or launch.get("gpu_memory_utilization_override") is not None or launch.get("quantization") is not None:
        errors.append("Gemma4 v3 runtime repair drift")
    if launch.get("repair_is_exact_error_lower_bound") is not True or launch.get("other_runtime_overrides_forbidden") is not True:
        errors.append("Gemma4 v3 repair must be exact and fail-closed")
    if (state.get("benign_gate") or {}).get("task_ids") != list(BENIGN_CAPABILITY_IDS):
        errors.append("Gemma4 v3 benign task drift")
    authority = state.get("authority") or {}
    if authority.get("model_loading") is not True or authority.get("benign_capability_execution") is not True:
        errors.append("Gemma4 v3 missing benign authority")
    if any(authority.get(k) is True for k in ("development_safety_execution", "persistent_state_construction", "fresh_qualification_execution", "heldout_future", "scientific_claim", "paper_design", "method", "p0", "gpu_scientific")):
        errors.append("Gemma4 v3 over-authorizes downstream science")
    if state.get("contract_sha256") != _contract_sha(state):
        errors.append("Gemma4 v3 contract digest mismatch")
    return sorted(set(errors))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--v2", type=Path, default=DEFAULT_V2)
    p.add_argument("--log", type=Path, default=DEFAULT_LOG)
    p.add_argument("--stop", type=Path, default=DEFAULT_STOP)
    p.add_argument("--v3", type=Path, default=DEFAULT_V3)
    p.add_argument("--build-stop", action="store_true")
    p.add_argument("--build-v3", action="store_true")
    args = p.parse_args()
    if args.build_stop:
        state = build_v2_runtime_stop(v2_path=args.v2, log_path=args.log)
        args.stop.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": state["status"], "model_inference_calls_executed": 0}, ensure_ascii=False))
    if args.build_v3:
        state = build_v3(v2_path=args.v2, stop_path=args.stop)
        errors = validate_v3(state)
        if errors:
            raise ValueError("invalid Gemma4 v3 preregistration:" + ";".join(errors))
        args.v3.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": state["status"], "contract_sha256": state["contract_sha256"], "max_num_batched_tokens": V3_MAX_NUM_BATCHED_TOKENS}, ensure_ascii=False))


if __name__ == "__main__":
    main()
