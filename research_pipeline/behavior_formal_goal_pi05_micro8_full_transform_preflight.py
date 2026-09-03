from __future__ import annotations

import dataclasses
import json
import os
import resource
import sys
from datetime import datetime, timezone
from pathlib import Path


def meminfo() -> dict[str, int]:
    wanted = {"MemTotal", "MemAvailable", "SwapTotal", "SwapFree"}
    out = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        key, rest = line.split(":", 1)
        if key in wanted:
            out[f"{key}_kib"] = int(rest.strip().split()[0])
    out["process_maxrss_kib"] = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return out


def main() -> int:
    if len(sys.argv) != 4:
        raise SystemExit("usage: script OPENPI_ROOT OPENPI_DATA_HOME RECEIPT")
    root = Path(sys.argv[1]).resolve()
    data_home = Path(sys.argv[2]).resolve()
    receipt = Path(sys.argv[3]).resolve()
    if receipt.exists():
        raise RuntimeError(f"preflight receipt already exists: {receipt}")
    if os.environ.get("JAX_PLATFORMS") != "cpu":
        raise RuntimeError("preflight must be CPU-only")
    if Path(os.environ.get("OPENPI_DATA_HOME", "")).resolve() != data_home:
        raise RuntimeError("OPENPI_DATA_HOME drift")
    os.chdir(root)
    sys.path.insert(0, str(root / "src"))

    import jax
    import openpi.training.config as config_lib
    import openpi.training.data_loader as data_loader

    src = config_lib.get_config("pi05_b1k_shared26_frozen")
    if src.batch_size != 64 or src.num_workers != 8 or src.seed != 42:
        raise RuntimeError("source config drift")
    cfg = dataclasses.replace(src, batch_size=8, num_workers=0)
    before = meminfo()
    loader = data_loader.create_b1k_data_loader(
        cfg, sharding=None, shuffle=True, num_batches=1, skip_norm_stats=False
    )
    observation, actions = next(iter(loader))
    jax.tree.map(lambda x: x.block_until_ready() if hasattr(x, "block_until_ready") else x, (observation, actions))
    after = meminfo()
    image_shapes = {k: list(v.shape) for k, v in observation.images.items()}
    payload = {
        "schema_version": "behavior-formal-goal-pi05-micro8-full-transform-preflight-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PI05_MICRO8_FULL_TRANSFORM_PREFLIGHT_PASS",
        "role": "OUTCOME_BLIND_RESOURCE_PREFLIGHT_ONLY",
        "config_name": "pi05_b1k_shared26_frozen",
        "source_batch_size": 64,
        "physical_micro_batch": 8,
        "num_workers": 0,
        "seed": 42,
        "episode_count": len(cfg.data.base_config.dataset_kwargs.get("episodes", [])),
        "action_horizon": cfg.model.action_horizon,
        "actions_shape": list(actions.shape),
        "image_shapes": image_shapes,
        "jax_devices": [str(d) for d in jax.devices()],
        "host_memory_before": before,
        "host_memory_after": after,
        "model_loaded": False,
        "forward_pass_executed": False,
        "backward_pass_executed": False,
        "optimizer_update": False,
        "policy_rollouts_started": False,
        "policy_outcomes_read": False,
        "scientific_authority": False,
    }
    receipt.parent.mkdir(parents=True, exist_ok=True)
    tmp = receipt.with_suffix(receipt.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, receipt)
    print(json.dumps({"status": payload["status"], "actions_shape": payload["actions_shape"], "process_maxrss_kib": after["process_maxrss_kib"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
