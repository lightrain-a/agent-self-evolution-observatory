from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

OBJECT_ID = "SUCC-C-BEHAVIOR2026-TWO-FAMILY-SHARED-MULTITASK-PANEL"
CHILD_ID = "SUCC-C-BEHAVIOR2026-SHARED26-PI05-PRACTICAL-SINGLE-GPU-BATCH"
PRACTICAL_PREREG_SHA = "382449b4320bacd85f736c0df9342f9677b3c755f2daeedcd680212aed2a503a"
SYNTHETIC_RESULT_SHA = "3914b1f2a3fd5e7964524eac7f625b64b4f089c0048a12dc5ebe9b79ba9bd86e"
RUNNER_SHA = "9102f1cf4f34efdccce5b78b4769bf5c14dfd983cded8c21e0c96be9725d8027"
EXPECTED_FILES = 1380
EXPECTED_BYTES = 236480375583


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset-seal", type=Path, required=True)
    ap.add_argument("--runner", type=Path, required=True)
    ap.add_argument("--launcher", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args(); seal_path = a.dataset_seal.resolve(); runner = a.runner.resolve(); launcher = a.launcher.resolve(); output = a.output.resolve()
    if output.exists():
        raise RuntimeError(f"smoke authority already exists: {output}")
    repo = output.parent.parent
    prereg = repo / "generated/behavior-formal-goal-coupling-shared26-pi05-practical-single-gpu-batch-preregistration-20260903.json"
    synth_path = repo / "generated/behavior-formal-goal-coupling-shared26-pi05-practical-batch16-synthetic-full-step-result-20260903.json"
    if sha(prereg) != PRACTICAL_PREREG_SHA or json.loads(prereg.read_text()).get("status") != "PREREGISTERED_PRACTICAL_SINGLE_GPU_BATCH_LADDER_NO_OUTCOME_ACCESS":
        raise RuntimeError("practical prereg drift")
    if sha(synth_path) != SYNTHETIC_RESULT_SHA:
        raise RuntimeError("batch16 synthetic result SHA drift")
    synth = json.loads(synth_path.read_text())
    if synth.get("status") != "PI05_PRACTICAL_BATCH16_SYNTHETIC_FULL_STEP_PASS" or synth.get("synthetic_step_after") != 1 or synth.get("real_scientific_optimizer_updates") != 0:
        raise RuntimeError("batch16 synthetic result not eligible")
    if sha(runner) != RUNNER_SHA:
        raise RuntimeError("smoke runner SHA drift")
    seal = json.loads(seal_path.read_text())
    if seal.get("status") != "WHOLE_MANIFEST_FINAL_SEAL_PASS" or seal.get("verified_file_count") != EXPECTED_FILES or seal.get("verified_bytes") != EXPECTED_BYTES:
        raise RuntimeError("dataset seal not PASS")
    if seal.get("missing_file_count") or seal.get("size_mismatch_count") or seal.get("sha_mismatch_count") or seal.get("partial_file_count"):
        raise RuntimeError("dataset seal mismatch counters nonzero")
    payload = {
        "schema_version": "behavior-formal-goal-coupling-shared26-pi05-practical-batch16-real-data-zero-update-smoke-authority-v1",
        "object_id": OBJECT_ID, "child_id": CHILD_ID, "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "AUTHORIZED_PI05_PRACTICAL_BATCH16_REAL_DATA_ZERO_UPDATE_SMOKE",
        "runner_path": str(runner.relative_to(repo)), "runner_sha256": RUNNER_SHA,
        "launcher_path": str(launcher.relative_to(repo)), "launcher_sha256": sha(launcher),
        "practical_preregistration_sha256": PRACTICAL_PREREG_SHA,
        "synthetic_batch16_result_sha256": SYNTHETIC_RESULT_SHA,
        "dataset_seal_path": str(seal_path), "dataset_seal_sha256": sha(seal_path),
        "dataset_root": "/data/wyt/behavior-2026-shared26-v3.0",
        "projection_root": "/data/wyt/behavior-2026-shared26-v3.0-rgb-runtime-repair2",
        "openpi_data_home": "/data/wyt/formal-goal-openpi-cache-v1",
        "candidate": {"physical_batch": 16, "effective_optimizer_batch": 16, "gradient_accumulation": 1, "seed": 42, "num_workers": 0},
        "resource_scope": {"host": "222.20.126.231", "gpu": "1x NVIDIA A100-SXM4-80GB", "memory_max_gib": 40, "memory_swap_max_gib": 0, "tasks_max": 512, "cpu_affinity": "0-63"},
        "authorized_operations": ["restore step0 checkpoint directly to GPU", "construct exactly one real transformed batch16 from frozen shared26 data", "inspect only structural shape/dtype and resource counters"],
        "forbidden_operations": ["model forward", "loss computation", "backward", "optimizer update", "parameter/EMA mutation", "checkpoint write", "policy rollout", "policy outcome read", "batch selection using data values"],
        "formal_training_authorized": False, "scientific_authority": False,
        "next_gate_if_pass": "COMPILE_PI05_PRACTICAL_BATCH16_FORMAL_TRAINING_AUTHORITY",
        "next_gate_if_fail": "REAL_DATA_BATCH16_PRETRAINING_REVIEW",
    }
    output.parent.mkdir(parents=True, exist_ok=True); tmp = output.with_suffix(output.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n"); os.replace(tmp, output)
    print(json.dumps({"status": payload["status"], "authority_sha256": sha(output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
