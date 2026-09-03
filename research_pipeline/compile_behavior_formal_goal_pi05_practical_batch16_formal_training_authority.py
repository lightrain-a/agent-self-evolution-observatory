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
TRAINER_SHA = "ab211ff675de941f678e10b10b46f04fd6e8b1de684ef7b9a319f4c7526e816a"
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
    ap.add_argument("--real-data-smoke", type=Path, required=True)
    ap.add_argument("--trainer", type=Path, required=True)
    ap.add_argument("--launcher", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args(); seal_path = a.dataset_seal.resolve(); smoke_path = a.real_data_smoke.resolve(); trainer = a.trainer.resolve(); launcher = a.launcher.resolve(); output = a.output.resolve()
    if output.exists():
        raise RuntimeError(f"formal training authority already exists: {output}")
    repo = output.parent.parent
    prereg = repo / "generated/behavior-formal-goal-coupling-shared26-pi05-practical-single-gpu-batch-preregistration-20260903.json"
    synth_path = repo / "generated/behavior-formal-goal-coupling-shared26-pi05-practical-batch16-synthetic-full-step-result-20260903.json"
    if sha(prereg) != PRACTICAL_PREREG_SHA:
        raise RuntimeError("practical prereg SHA drift")
    if sha(synth_path) != SYNTHETIC_RESULT_SHA or json.loads(synth_path.read_text()).get("status") != "PI05_PRACTICAL_BATCH16_SYNTHETIC_FULL_STEP_PASS":
        raise RuntimeError("synthetic batch16 PASS drift")
    seal = json.loads(seal_path.read_text())
    if seal.get("status") != "WHOLE_MANIFEST_FINAL_SEAL_PASS" or seal.get("verified_file_count") != EXPECTED_FILES or seal.get("verified_bytes") != EXPECTED_BYTES:
        raise RuntimeError("dataset seal not PASS")
    smoke = json.loads(smoke_path.read_text())
    if smoke.get("status") != "PI05_PRACTICAL_BATCH16_REAL_DATA_ZERO_UPDATE_PASS" or not smoke.get("batch_ready") or smoke.get("optimizer_update") or smoke.get("forward_pass"):
        raise RuntimeError("real-data batch16 smoke not PASS")
    if sha(trainer) != TRAINER_SHA:
        raise RuntimeError("formal trainer SHA drift")
    payload = {
        "schema_version": "behavior-formal-goal-coupling-shared26-pi05-practical-batch16-formal-training-authority-v1",
        "object_id": OBJECT_ID, "child_id": CHILD_ID, "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "AUTHORIZED_PI05_PRACTICAL_BATCH16_FORMAL_TRAINING",
        "runner_path": str(trainer.relative_to(repo)), "runner_sha256": TRAINER_SHA,
        "launcher_path": str(launcher.relative_to(repo)), "launcher_sha256": sha(launcher),
        "practical_preregistration_sha256": PRACTICAL_PREREG_SHA,
        "synthetic_batch16_result_sha256": SYNTHETIC_RESULT_SHA,
        "real_data_smoke_path": str(smoke_path), "real_data_smoke_sha256": sha(smoke_path),
        "dataset_seal_path": str(seal_path), "dataset_seal_sha256": sha(seal_path),
        "openpi_data_home": "/data/wyt/formal-goal-openpi-cache-v1",
        "formal_run": {
            "host": "222.20.126.231", "config": "pi05_b1k_shared26_frozen", "exp_name": "shared26-seed42-practical-b16-run1",
            "physical_batch": 16, "effective_optimizer_batch": 16, "gradient_accumulation": 1,
            "seed": 42, "optimizer_updates": 50000, "num_workers": 0, "action_horizon": 32,
            "optimizer": "AdamW(b1=0.9,b2=0.95,eps=1e-8,weight_decay=1e-10,clip_gradient_norm=1.0)",
            "lr_schedule": "CosineDecaySchedule(warmup_steps=1000,peak_lr=2.5e-05,decay_steps=30000,decay_lr=2.5e-06)",
            "ema_decay": 0.99,
            "save_labels": [10000, 20000, 30000, 40000, 49999],
            "terminal_checkpoint_label_for_scientific_evaluation": 49999,
            "intermediate_checkpoints_role": "exact-state recovery only; forbidden for evaluation or selection",
            "validation": false, "wandb": false, "loss_logging_or_reading": false,
        },
        "resource_scope": {"gpu": "1x NVIDIA A100-SXM4-80GB", "memory_max_gib": 40, "memory_swap_max_gib": 0, "tasks_max": 512, "cpu_affinity": "0-63", "jax_platforms": "cuda", "xla_python_client_mem_fraction": 0.9},
        "exactly_once": {
            "fresh_checkpoint_directory_required": true,
            "automatic_retry": false,
            "automatic_restart_after_optimizer_updates": false,
            "future_recovery_allowed_only_by_separate_exact_state_adjudication": true
        },
        "forbidden": [
            "loss/grad-norm/param-norm reading or reporting", "validation", "W&B", "checkpoint shopping", "evaluating intermediate checkpoints",
            "changing batch, seed, optimizer, LR, EMA, dataset, normalization, action horizon, update count, or checkpoint rule after launch",
            "policy rollout or Q/reward/success read before terminal checkpoint content-address and serving qualification"
        ],
        "scientific_training_authorized": true, "policy_rollouts_authorized": false, "policy_outcomes_read": false,
        "next_gate_if_complete": "PI05_TERMINAL_CHECKPOINT_49999_CONTENT_ADDRESS_AND_SERVING_QUALIFICATION",
        "next_gate_if_failure": "FORMAL_TRAINING_FAILURE_EXACT_STATE_ADJUDICATION"
    }
    output.parent.mkdir(parents=True, exist_ok=True); tmp = output.with_suffix(output.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n"); os.replace(tmp, output)
    print(json.dumps({"status": payload["status"], "authority_sha256": sha(output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
