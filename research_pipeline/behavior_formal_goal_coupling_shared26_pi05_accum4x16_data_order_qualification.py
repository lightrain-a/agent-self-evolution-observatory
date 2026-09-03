from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

OBJECT_ID = "SUCC-C-BEHAVIOR2026-TWO-FAMILY-SHARED-MULTITASK-PANEL"
CONFIG_NAME = "pi05_b1k_shared26_frozen"
SOURCE_BATCH = 64
MICRO_BATCH = 4
ACCUM_STEPS = 16
EFFECTIVE_UPDATES_TO_COMPARE = 32
EXPECTED_DATASET_FRAMES = 50_852_705
EXPECTED_TRAIN_UPDATES = 50_000


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def sampler_iter(torch_loader):
    # Creating the iterator consumes the same loader-generator base-seed draw as real
    # DataLoader iteration, but reading _sampler_iter does not decode dataset samples.
    iterator = iter(torch_loader)
    return iterator, iterator._sampler_iter


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--openpi-child-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()

    child_root = args.openpi_child_root.resolve()
    receipt_path = args.receipt.resolve()
    os.chdir(child_root)
    sys.path.insert(0, str(child_root / "src"))

    import openpi.training.config as config_lib
    import openpi.training.data_loader as data_loader

    source = config_lib.get_config(CONFIG_NAME)
    if source.batch_size != SOURCE_BATCH or source.seed != 42:
        raise RuntimeError(f"source config drift: batch={source.batch_size}, seed={source.seed}")

    source_cfg = dataclasses.replace(source, num_workers=0)
    micro_cfg = dataclasses.replace(source, batch_size=MICRO_BATCH, num_workers=0)

    loader64 = data_loader.create_b1k_data_loader(source_cfg, sharding=None, shuffle=True, num_batches=1)
    loader16 = data_loader.create_b1k_data_loader(micro_cfg, sharding=None, shuffle=True, num_batches=1)
    torch64 = loader64._data_loader.torch_loader
    torch16 = loader16._data_loader.torch_loader

    dataset_len64 = len(torch64.dataset)
    dataset_len16 = len(torch16.dataset)
    if dataset_len64 != dataset_len16 or dataset_len64 != EXPECTED_DATASET_FRAMES:
        raise RuntimeError(f"dataset length drift: {dataset_len64}/{dataset_len16}/{EXPECTED_DATASET_FRAMES}")

    owner64, indices64 = sampler_iter(torch64)
    owner16, indices16 = sampler_iter(torch16)
    del owner64, owner16

    compared = []
    all_equal = True
    for effective_step in range(EFFECTIVE_UPDATES_TO_COMPARE):
        batch64 = list(next(indices64))
        micros = [list(next(indices16)) for _ in range(ACCUM_STEPS)]
        concat16 = [idx for micro in micros for idx in micro]
        equal = batch64 == concat16
        all_equal = all_equal and equal
        compared.append(
            {
                "effective_step": effective_step,
                "equal": equal,
                "source_first_index": int(batch64[0]),
                "source_last_index": int(batch64[-1]),
                "micro_first_index": int(concat16[0]),
                "micro_last_index": int(concat16[-1]),
            }
        )

    source_batches_per_epoch = dataset_len64 // SOURCE_BATCH
    source_tail = dataset_len64 % SOURCE_BATCH
    micro_batches_per_epoch = dataset_len16 // MICRO_BATCH
    micro_tail = dataset_len16 % MICRO_BATCH
    matched_micro_batches = source_batches_per_epoch * ACCUM_STEPS
    extra_full_micro_batches_at_epoch_tail = micro_batches_per_epoch - matched_micro_batches
    frames_consumed_by_50k = EXPECTED_TRAIN_UPDATES * SOURCE_BATCH
    reaches_epoch_boundary = EXPECTED_TRAIN_UPDATES >= source_batches_per_epoch

    payload = {
        "schema_version": "behavior-formal-goal-coupling-shared26-pi05-accum-data-order-qualification-v1",
        "object_id": OBJECT_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PI05_ACCUM_4X16_DATA_ORDER_QUALIFICATION_PASS" if all_equal and not reaches_epoch_boundary else "PI05_ACCUM_4X16_DATA_ORDER_QUALIFICATION_HOLD",
        "openpi_child_root": str(child_root),
        "config_name": CONFIG_NAME,
        "seed": source.seed,
        "source_batch_size": SOURCE_BATCH,
        "micro_batch_size": MICRO_BATCH,
        "accumulation_steps": ACCUM_STEPS,
        "effective_batch_size": MICRO_BATCH * ACCUM_STEPS,
        "dataset_frames": dataset_len64,
        "compared_effective_updates": EFFECTIVE_UPDATES_TO_COMPARE,
        "sampler_groups_exactly_equal": all_equal,
        "comparison": compared,
        "epoch_accounting": {
            "source_batches_per_epoch": source_batches_per_epoch,
            "source_tail_frames_dropped": source_tail,
            "micro_batches_per_epoch": micro_batches_per_epoch,
            "micro_tail_frames_dropped": micro_tail,
            "matched_micro_batches_per_epoch": matched_micro_batches,
            "extra_full_micro_batches_at_epoch_tail_if_uncontrolled": extra_full_micro_batches_at_epoch_tail,
            "required_future_epoch_rule": "If a run ever reaches an epoch boundary, discard the extra full micro-batches so each effective update remains aligned to the source batch-64 drop_last grouping.",
        },
        "formal_50k_accounting": {
            "optimizer_updates": EXPECTED_TRAIN_UPDATES,
            "frames_consumed": frames_consumed_by_50k,
            "source_epoch_boundary_reached": reaches_epoch_boundary,
            "conclusion": "The frozen 50k run remains within the first source epoch, so no microbatch-tail special case is reached during this experiment.",
        },
        "dataset_samples_decoded": False,
        "model_loaded": False,
        "gpu_used": False,
        "optimizer_update": False,
        "policy_rollouts_started": False,
        "policy_outcomes_read": False,
        "next_gate": "ACCUM4X16_SYNTHETIC_FUSED_NO_UPDATE_RESOURCE_QUALIFICATION" if all_equal and not reaches_epoch_boundary else "DATA_ORDER_REPAIR_ADJUDICATION",
    }
    write_json(receipt_path, payload)
    print(json.dumps({"status": payload["status"], "exact": all_equal, "source_batches_per_epoch": source_batches_per_epoch, "formal_50k_reaches_epoch_boundary": reaches_epoch_boundary}, sort_keys=True))
    return 0 if payload["status"].endswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
