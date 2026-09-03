from __future__ import annotations

import argparse
import dataclasses
import functools
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

OBJECT_ID = "SUCC-C-BEHAVIOR2026-TWO-FAMILY-SHARED-MULTITASK-PANEL"
CHILD_ID = "SUCC-C-BEHAVIOR2026-SHARED26-PI05-SINGLE-GPU-ACCUMULATION"
AUTH_STATUS = "AUTHORIZED_PI05_SINGLE_GPU_STREAMING_ACCUM8X8_FORMAL_TRAINING"
SYNTHETIC_PASS = "PI05_SYNTHETIC_FUSED_ACCUM8X8_DIRECT_DEVICE_PASS"
REAL_DATA_PASS = "PI05_STREAMING_ACCUM8X8_DIRECT_DEVICE_NO_UPDATE_DRY_GRADIENT_PASS"
CONFIG_NAME = "pi05_b1k_shared26_frozen"
EXP_NAME = "shared26-seed42-run1"
SOURCE_BATCH = 64
MICRO_BATCH = 8
ACCUM_STEPS = 8
EFFECTIVE_BATCH = 64
SEED = 42
ACTION_HORIZON = 32
EPISODE_COUNT = 5200
NUM_EFFECTIVE_UPDATES = 50_000
FSDP_DEVICES = 1
SOURCE_NUM_WORKERS = 8
RUNTIME_NUM_WORKERS = 0
TRAINABLE_ELEMENTS = 3_353_433_872
GRAD_BYTES = 13_413_735_488
EXPECTED_CONFIG_SHA = "4a50bb5f3579ed0035e19d2fc2a5d33821c0cc115c6e8c441eac497e74b02e99"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require_bound_file(authority: dict, key: str, path: Path, required_status: str | None = None) -> dict:
    binding = authority.get(key) or {}
    expected = binding.get("sha256")
    if not expected:
        raise RuntimeError(f"authority missing SHA binding for {key}")
    observed = sha256_file(path)
    if observed != expected:
        raise RuntimeError(f"{key} SHA drift: {observed}/{expected}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if required_status is not None and payload.get("status") != required_status:
        raise RuntimeError(f"{key} status drift: {payload.get('status')}/{required_status}")
    return payload


def validate_authority(authority_path: Path, runner_path: Path) -> dict:
    authority = json.loads(authority_path.read_text(encoding="utf-8"))
    if authority.get("status") != AUTH_STATUS:
        raise RuntimeError(f"formal training authority is not active: {authority.get('status')}")
    if authority.get("object_id") != OBJECT_ID or authority.get("child_id") != CHILD_ID:
        raise RuntimeError("formal training authority object drift")
    if authority.get("runner_sha256") != sha256_file(runner_path):
        raise RuntimeError("formal training runner SHA binding drift")
    candidate = authority.get("candidate") or {}
    expected = {
        "physical_micro_batch": MICRO_BATCH,
        "accumulation_steps": ACCUM_STEPS,
        "effective_batch": EFFECTIVE_BATCH,
        "effective_optimizer_updates": NUM_EFFECTIVE_UPDATES,
        "seed": SEED,
    }
    if candidate != expected:
        raise RuntimeError(f"formal training candidate drift: {candidate}/{expected}")
    return authority


def validate_child_source(child_root: Path) -> None:
    config_path = child_root / "src/openpi/training/config.py"
    if sha256_file(config_path) != EXPECTED_CONFIG_SHA:
        raise RuntimeError("OpenPI shared26 child config SHA drift")


def tree_structure_stats(tree) -> tuple[int, int]:
    import jax

    leaves = jax.tree.leaves(tree)
    elements = int(sum(np.prod(tuple(x.shape), dtype=np.int64) for x in leaves))
    bytes_ = int(sum(np.prod(tuple(x.shape), dtype=np.int64) * np.dtype(x.dtype).itemsize for x in leaves))
    return elements, bytes_


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--synthetic-result", type=Path, required=True)
    parser.add_argument("--real-data-result", type=Path, required=True)
    parser.add_argument("--openpi-child-root", type=Path, required=True)
    parser.add_argument("--params-root", type=Path, required=True)
    parser.add_argument("--progress", type=Path, required=True)
    args = parser.parse_args()

    runner_path = Path(__file__).resolve()
    authority_path = args.authority.resolve()
    child_root = args.openpi_child_root.resolve()
    params_root = args.params_root.resolve()
    progress_path = args.progress.resolve()
    authority = validate_authority(authority_path, runner_path)
    synthetic = require_bound_file(authority, "synthetic_gate", args.synthetic_result.resolve(), SYNTHETIC_PASS)
    real_data = require_bound_file(authority, "real_data_gate", args.real_data_result.resolve(), REAL_DATA_PASS)
    for payload, label in [(synthetic, "synthetic"), (real_data, "real-data")]:
        if payload.get("optimizer_update") not in (False, 0, None):
            raise RuntimeError(f"{label} prerequisite crossed optimizer boundary")
        if payload.get("policy_outcomes_read") not in (False, None):
            raise RuntimeError(f"{label} prerequisite crossed outcome boundary")
    validate_child_source(child_root)

    checkpoint_dir = child_root / "outputs/checkpoints" / CONFIG_NAME / EXP_NAME
    if checkpoint_dir.exists():
        raise RuntimeError(f"fresh formal checkpoint directory must be absent: {checkpoint_dir}")
    if progress_path.exists():
        raise RuntimeError(f"formal training progress already exists; exactly-once launch refused: {progress_path}")

    # Persistent exactly-once launch claim.  This is created before model/data initialization and is never
    # automatically removed after a crash.  Any recovery must therefore be separately adjudicated rather than
    # silently launching a second scientific run.
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    launch_claim = {
        "status": "PI05_ACCUM8X8_FORMAL_TRAINING_LAUNCH_CLAIMED",
        "object_id": OBJECT_ID,
        "child_id": CHILD_ID,
        "authority_sha256": sha256_file(authority_path),
        "effective_updates_completed": 0,
        "micro_batches_completed": 0,
        "optimizer_updates_completed": 0,
        "policy_outcomes_read": False,
        "checkpoint_written": False,
        "automatic_retry_authorized": False,
    }
    fd = os.open(progress_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(json.dumps(launch_claim, indent=2, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())

    os.chdir(child_root)
    sys.path.insert(0, str(child_root))
    sys.path.insert(0, str(child_root / "src"))

    import flax.nnx as nnx
    import jax
    import jax.numpy as jnp
    import optax
    import openpi.models.model as model_lib
    import openpi.shared.array_typing as at
    import openpi.training.checkpoints as checkpoints
    import openpi.training.config as config_lib
    import openpi.training.data_loader as data_loader
    import openpi.training.sharding as sharding
    import openpi.training.weight_loaders as weight_loaders
    from scripts.b1k import train_b1k

    devices = jax.devices()
    if len(devices) != 1 or devices[0].platform != "gpu":
        raise RuntimeError(f"formal training requires exactly one CUDA device, got {devices}")

    class DirectDeviceCheckpointWeightLoader:
        def __init__(self, path: str):
            self.params_path = path

        def load(self, params):
            loaded = model_lib.restore_params(self.params_path, restore_type=jax.Array)
            leaves = jax.tree.leaves(loaded)
            if not leaves or not all(isinstance(x, jax.Array) for x in leaves):
                raise RuntimeError("direct-device checkpoint restore returned non-jax.Array leaves")
            return weight_loaders._merge_params(loaded, params, missing_regex=".*lora.*")

    source_config = config_lib.get_config(CONFIG_NAME)
    if source_config.batch_size != SOURCE_BATCH or source_config.num_workers != SOURCE_NUM_WORKERS:
        raise RuntimeError("source shared26 batch/worker config drift")
    config = dataclasses.replace(
        source_config,
        exp_name=EXP_NAME,
        weight_loader=DirectDeviceCheckpointWeightLoader(str(params_root)),
        batch_size=MICRO_BATCH,
        num_workers=RUNTIME_NUM_WORKERS,
        wandb_enabled=False,
        resume=False,
        overwrite=True,
    )
    episodes = list(config.data.base_config.dataset_kwargs.get("episodes", []))
    if (
        config.seed != SEED
        or config.model.action_horizon != ACTION_HORIZON
        or config.fsdp_devices != FSDP_DEVICES
        or config.num_train_steps != NUM_EFFECTIVE_UPDATES
        or len(episodes) != EPISODE_COUNT
        or len(set(episodes)) != EPISODE_COUNT
    ):
        raise RuntimeError("formal training scientific config drift")

    mesh = sharding.make_mesh(config.fsdp_devices)
    data_sharding = jax.sharding.NamedSharding(mesh, jax.sharding.PartitionSpec(sharding.DATA_AXIS))
    replicated_sharding = jax.sharding.NamedSharding(mesh, jax.sharding.PartitionSpec())

    # Resource-lifetime rule: direct-device state first, real video/tokenizer loader second.
    rng = jax.random.key(config.seed)
    train_rng, init_rng = jax.random.split(rng)
    state, state_sharding = train_b1k.init_train_state(config, init_rng, mesh, resume=False)
    jax.block_until_ready(state)
    if int(jax.device_get(state.step)) != 0:
        raise RuntimeError("formal training initial state is not step 0")

    loader = data_loader.create_b1k_data_loader(
        config,
        sharding=data_sharding,
        shuffle=True,
        skip_norm_stats=False,
    )
    loader_iter = iter(loader)

    checkpoint_manager, resuming = checkpoints.initialize_checkpoint_dir(
        config.checkpoint_dir,
        keep_period=config.keep_period,
        overwrite=True,
        resume=False,
    )
    if resuming:
        raise RuntimeError("formal training unexpectedly entered resume mode")

    @at.typecheck
    def scaled_grad(config_arg, rng_arg: at.KeyArrayLike, state_arg, batch_arg):
        model = nnx.merge(state_arg.model_def, state_arg.params)
        model.train()

        @at.typecheck
        def loss_fn(m, r, observation, actions):
            loss = m.compute_loss(r, observation, actions, train=True)
            return jnp.mean(loss)

        observation, actions = batch_arg
        diff_state = nnx.DiffState(0, config_arg.trainable_filter)
        discarded_loss, grads = nnx.value_and_grad(loss_fn, argnums=diff_state)(model, rng_arg, observation, actions)
        del discarded_loss
        return jax.tree.map(lambda x: x / ACCUM_STEPS, grads)

    @at.typecheck
    def add_grad(config_arg, rng_arg: at.KeyArrayLike, state_arg, batch_arg, accumulator):
        grads = scaled_grad(config_arg, rng_arg, state_arg, batch_arg)
        return jax.tree.map(lambda a, g: a + g, accumulator, grads)

    @at.typecheck
    def final_grad_and_update(config_arg, rng_arg: at.KeyArrayLike, state_arg, batch_arg, accumulator):
        model = nnx.merge(state_arg.model_def, state_arg.params)
        model.train()

        @at.typecheck
        def loss_fn(m, r, observation, actions):
            loss = m.compute_loss(r, observation, actions, train=True)
            return jnp.mean(loss)

        observation, actions = batch_arg
        diff_state = nnx.DiffState(0, config_arg.trainable_filter)
        discarded_loss, last_grads = nnx.value_and_grad(loss_fn, argnums=diff_state)(model, rng_arg, observation, actions)
        del discarded_loss
        grads = jax.tree.map(lambda a, g: a + g / ACCUM_STEPS, accumulator, last_grads)
        params = state_arg.params.filter(config_arg.trainable_filter)
        updates, new_opt_state = state_arg.tx.update(grads, state_arg.opt_state, params)
        new_params = optax.apply_updates(params, updates)
        nnx.update(model, new_params)
        new_params = nnx.state(model)
        new_state = dataclasses.replace(
            state_arg,
            step=state_arg.step + 1,
            params=new_params,
            opt_state=new_opt_state,
        )
        if state_arg.ema_decay is not None:
            new_state = dataclasses.replace(
                new_state,
                ema_params=jax.tree.map(
                    lambda old, new: state_arg.ema_decay * old + (1 - state_arg.ema_decay) * new,
                    state_arg.ema_params,
                    new_params,
                ),
            )
        return new_state

    pfirst = jax.jit(
        functools.partial(scaled_grad, config),
        in_shardings=(replicated_sharding, state_sharding, data_sharding),
        out_shardings=None,
    )
    padd = jax.jit(
        functools.partial(add_grad, config),
        in_shardings=(replicated_sharding, state_sharding, data_sharding, None),
        out_shardings=None,
        donate_argnums=(3,),
    )
    pfinal = jax.jit(
        functools.partial(final_grad_and_update, config),
        in_shardings=(replicated_sharding, state_sharding, data_sharding, None),
        out_shardings=state_sharding,
        donate_argnums=(1, 3),
    )

    progress = {
        "status": "PI05_ACCUM8X8_FORMAL_TRAINING_STARTED",
        "object_id": OBJECT_ID,
        "child_id": CHILD_ID,
        "authority_sha256": sha256_file(authority_path),
        "effective_updates_completed": 0,
        "micro_batches_completed": 0,
        "optimizer_updates_completed": 0,
        "policy_outcomes_read": False,
        "checkpoint_selection_rule": "terminal source-emitted label 49999 only",
    }
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    progress_path.write_text(json.dumps(progress, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    started = time.monotonic()
    for effective_step in range(NUM_EFFECTIVE_UPDATES):
        step_rng = jax.random.fold_in(train_rng, state.step)
        accumulator = None
        for micro_index in range(ACCUM_STEPS):
            batch = next(loader_iter)
            if batch[1].shape[0] != MICRO_BATCH:
                raise RuntimeError(f"microbatch shape drift at {effective_step}/{micro_index}: {batch[1].shape}")
            micro_rng = jax.random.fold_in(step_rng, micro_index)
            if micro_index == 0:
                accumulator = pfirst(micro_rng, state, batch)
                jax.tree.map(lambda x: x.block_until_ready(), accumulator)
                elements, bytes_ = tree_structure_stats(accumulator)
                if elements != TRAINABLE_ELEMENTS or bytes_ != GRAD_BYTES:
                    raise RuntimeError(f"formal accumulator structure drift: {elements}/{bytes_}")
            elif micro_index < ACCUM_STEPS - 1:
                accumulator = padd(micro_rng, state, batch, accumulator)
                jax.tree.map(lambda x: x.block_until_ready(), accumulator)
            else:
                state = pfinal(micro_rng, state, batch, accumulator)
                jax.block_until_ready(state)
                accumulator = None

        if int(jax.device_get(state.step)) != effective_step + 1:
            raise RuntimeError("formal effective-step counter drift")

        # Keep operational progress only; do not expose or use loss/gradient values.
        progress.update(
            {
                "status": "PI05_ACCUM8X8_FORMAL_TRAINING_RUNNING",
                "effective_updates_completed": effective_step + 1,
                "micro_batches_completed": (effective_step + 1) * ACCUM_STEPS,
                "optimizer_updates_completed": effective_step + 1,
                "elapsed_seconds": time.monotonic() - started,
            }
        )
        if effective_step % 10 == 0 or effective_step == NUM_EFFECTIVE_UPDATES - 1:
            tmp = progress_path.with_suffix(progress_path.suffix + ".tmp")
            tmp.write_text(json.dumps(progress, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            os.replace(tmp, progress_path)

        # Preserve source checkpoint labels: 10000, 20000, 30000, 40000, terminal 49999.
        if (effective_step % config.save_interval == 0 and effective_step > 0) or effective_step == NUM_EFFECTIVE_UPDATES - 1:
            checkpoints.save_state(checkpoint_manager, state, loader, effective_step)

    checkpoint_manager.wait_until_finished()
    progress.update(
        {
            "status": "PI05_ACCUM8X8_FORMAL_TRAINING_COMPLETE",
            "effective_updates_completed": NUM_EFFECTIVE_UPDATES,
            "optimizer_updates_completed": NUM_EFFECTIVE_UPDATES,
            "terminal_checkpoint_label": 49_999,
        }
    )
    tmp = progress_path.with_suffix(progress_path.suffix + ".tmp")
    tmp.write_text(json.dumps(progress, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, progress_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
