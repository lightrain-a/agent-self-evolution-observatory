from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

OBJECT_ID = "SUCC-C-BEHAVIOR2026-TWO-FAMILY-SHARED-MULTITASK-PANEL"
CHILD_ID = "SUCC-C-BEHAVIOR2026-SHARED26-PI05-SINGLE-GPU-ACCUMULATION"
EXPECTED_DIRECT_STATUS = "PI05_DIRECT_DEVICE_NO_UPDATE_MODEL_LOAD_PASS"
EXPECTED_ATTEMPT1_RESULT_SHA = "9202758ef8e25fa079f340bff74da4749115e536bf166b6017c8c3ceefe4a0bb"
EXPECTED_ADJ_SHA = "7fce8b714c2b46c1561930c34f0c2e5b67987ddaa63e4868f42f752e076afad8"
EXPECTED_DESIGN_SHA = "750346375ded94237cca5f8f5eb68f69b664fa819ee1074097b67257672cc43d"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--direct-result", type=Path, required=True)
    ap.add_argument("--runner", type=Path, required=True)
    ap.add_argument("--worker", type=Path, required=True)
    ap.add_argument("--launcher", type=Path, required=True)
    ap.add_argument("--design", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    paths = {k: Path(v).resolve() for k, v in vars(a).items()}
    out = paths["output"]
    if out.exists():
        raise RuntimeError(f"authority already exists; compiler is exactly-once: {out}")

    direct = json.loads(paths["direct_result"].read_text(encoding="utf-8"))
    if direct.get("status") != EXPECTED_DIRECT_STATUS:
        raise RuntimeError(f"direct-device gate is not PASS: {direct.get('status')}")
    if direct.get("object_id") != OBJECT_ID or not direct.get("model_loaded") or direct.get("initialized_step") != 0:
        raise RuntimeError("direct-device model-load identity/step drift")
    forbidden_true = [
        "dataset_accessed", "tokenizer_executed", "forward_pass_executed", "loss_computed",
        "backward_pass_executed", "optimizer_update", "checkpoint_written", "policy_rollouts_started",
        "policy_outcomes_read", "training_started", "formal_training_topology_authorized", "scientific_authority",
    ]
    bad = [k for k in forbidden_true if direct.get(k) not in (False, None)]
    if bad:
        raise RuntimeError(f"direct-device result crossed forbidden boundary: {bad}")
    if sha(paths["design"]) != EXPECTED_DESIGN_SHA:
        raise RuntimeError("streaming repair design SHA drift")

    repo = out.parent.parent
    attempt1 = repo / "generated/behavior-formal-goal-coupling-shared26-pi05-accum8x8-dry-gradient-result-20260902.json"
    adjudication = repo / "generated/behavior-formal-goal-coupling-shared26-pi05-accum8x8-attempt1-host-exit-adjudication-20260902.json"
    if sha(attempt1) != EXPECTED_ATTEMPT1_RESULT_SHA or sha(adjudication) != EXPECTED_ADJ_SHA:
        raise RuntimeError("consumed 8x8 attempt lineage drift")

    payload = {
        "schema_version": "behavior-formal-goal-coupling-shared26-pi05-streaming-accum8x8-safe69-authority-v1",
        "object_id": OBJECT_ID,
        "child_id": CHILD_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "AUTHORIZED_PI05_STREAMING_ACCUM8X8_DIRECT_DEVICE_NO_UPDATE_DRY_GRADIENT_REPAIR1",
        "scope": "outcome-blind resource-only dry-gradient qualification on canonical host-69 data; no optimizer or scientific training authority",
        "direct_device_model_load_result": {
            "path": str(paths["direct_result"].relative_to(repo)),
            "sha256": sha(paths["direct_result"]),
            "status": EXPECTED_DIRECT_STATUS,
        },
        "consumed_attempt1": {
            "result_path": str(attempt1.relative_to(repo)),
            "result_sha256": EXPECTED_ATTEMPT1_RESULT_SHA,
            "adjudication_path": str(adjudication.relative_to(repo)),
            "adjudication_sha256": EXPECTED_ADJ_SHA,
        },
        "repair_design": {"path": str(paths["design"].relative_to(repo)), "sha256": EXPECTED_DESIGN_SHA},
        "runner_path": str(paths["runner"].relative_to(repo)),
        "runner_sha256": sha(paths["runner"]),
        "worker_path": str(paths["worker"].relative_to(repo)),
        "worker_sha256": sha(paths["worker"]),
        "launcher_path": str(paths["launcher"].relative_to(repo)),
        "launcher_sha256": sha(paths["launcher"]),
        "candidate": {"physical_micro_batch": 8, "accumulation_steps": 8, "effective_batch": 64, "seed": 42},
        "resource_scope": {
            "host": "222.20.126.69",
            "gpu": "1x NVIDIA A100-SXM4-80GB",
            "memory_max_gib": 20,
            "memory_swap_max_gib": 0,
            "tasks_max": 512,
            "cpu_affinity": "0-63",
            "num_workers": 0,
            "jax_platforms": "cuda",
            "xla_python_client_mem_fraction": 0.9,
        },
        "admission_wait": {
            "gpu_compute_apps_required": 0,
            "gpu_memory_used_max_mib": 1024,
            "host_mem_available_min_gib": 24,
            "memory_psi_avg10_max_percent": 1.0,
            "io_psi_avg10_max_percent": 5.0,
            "attempt_consumed_while_waiting": False,
        },
        "scientific_invariants": {
            "effective_batch": 64,
            "seed": 42,
            "episode_subset": 5200,
            "action_horizon": 32,
            "model_checkpoint_optimizer_schedule_normalization": "unchanged",
            "optimizer_updates_authorized": 0,
        },
        "forbidden_operations": [
            "optimizer update", "parameter or EMA mutation", "checkpoint write", "policy rollout",
            "policy outcome read", "loss retention/reporting", "automatic advance to 4x16 after failure",
        ],
        "formal_training_authorized": False,
        "scientific_authority": False,
        "next_gate_if_pass": "AUTHORIZE_SINGLE_GPU_STREAMING_ACCUM8X8_DIRECT_DEVICE_FORMAL_TRAINING_IMPLEMENTATION",
        "next_gate_if_fail": "STREAMING_ACCUM8X8_FAILURE_ADJUDICATION_BEFORE_ANY_4X16_ADVANCE",
        "compiler_path": str(Path(__file__).resolve().relative_to(repo)),
        "compiler_sha256": sha(Path(__file__).resolve()),
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, out)
    print(json.dumps({"status": payload["status"], "authority_sha256": sha(out)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
