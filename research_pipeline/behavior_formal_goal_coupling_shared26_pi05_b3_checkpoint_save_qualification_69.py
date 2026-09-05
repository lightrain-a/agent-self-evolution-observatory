from __future__ import annotations

import argparse
import dataclasses
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
from typing import Any

import jax
import orbax.checkpoint as ocp
from orbax.checkpoint._src.handlers import checkpoint_handler

from research_pipeline.behavior_formal_goal_coupling_shared26_pi05_b1_serial_item_checkpoint_save import (
    atomic_json, cgroup_snapshot, gpu_snapshot, host_snapshot, sha256_file, tree_bytes, validate_base,
)
from research_pipeline.behavior_formal_goal_coupling_shared26_pi05_b3_writeback_aware_orbax import (
    DEFAULT_D2H_BATCH_BYTES,
    clone_global_registry_with_writeback_aware_leaf_batched_array_handler,
)
from research_pipeline.behavior_formal_goal_coupling_shared26_pi05_b3_writeback_cache import self_cgroup_memory_snapshot

OBJECT_ID = "SUCC-C-BEHAVIOR2026-TWO-FAMILY-SHARED-MULTITASK-PANEL"
CHILD_ID = "SUCC-C-BEHAVIOR2026-SHARED26-PI05-PRACTICAL-SINGLE-GPU-BATCH"
CONFIG_NAME = "pi05_b1k_shared26_frozen"
EXP_NAME = "shared26-seed42-b3-writeback-checkpoint-qualification"
BATCH, SEED, SAVE_LABEL = 16, 42, 10000
EXPECTED_PARENT_COMMIT = "0cc8e355f7bac0976db1cc3139b1ff0379feea60"
EXPECTED_CONFIG_SHA256 = "4a50bb5f3579ed0035e19d2fc2a5d33821c0cc115c6e8c441eac497e74b02e99"
EXPECTED_NORM_SHA256 = "5e4159ec0986ad9fc87cc9a265eed9ac67fc9d2d0df233db6130acf0ebff52ce"
EXPECTED_MACHINE_ID = "c4046d3ca4454a958f5de081aac4dc2e"
EXPECTED_MEMORY_MAX_GIB = 52
EXPECTED_MEMORY_MAX_BYTES = EXPECTED_MEMORY_MAX_GIB * 1024**3
EXPECTED_TRAIN_LEAVES, EXPECTED_TRAIN_NBYTES = 156, 40_241_206_476
EXPECTED_PARAMS_LEAVES, EXPECTED_PARAMS_NBYTES = 51, 13_413_735_488
EXPECTED_MAX_LEAF_BYTES = 4_831_838_208
MIN_AVAILABLE_KIB, MAX_GPU_USED_MIB = 104_857_600, 1024
STABLE_CHECKS, STABLE_INTERVAL_SECONDS = 3, 30


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def require_binding(authority: dict[str, Any], key: str, path: Path) -> str:
    binding = authority.get("bindings", {}).get(key)
    if not isinstance(binding, dict):
        raise RuntimeError(f"missing authority binding: {key}")
    actual = sha256_file(path)
    if binding.get("path") != str(path) or binding.get("sha256") != actual:
        raise RuntimeError(f"authority binding drift: {key}")
    return actual


def compute_app_count() -> int:
    out = subprocess.run(["nvidia-smi", "--query-compute-apps=pid", "--format=csv,noheader,nounits"], text=True, capture_output=True, check=False).stdout
    return sum(1 for line in out.splitlines() if line.strip())


def mem_available_kib() -> int:
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1])
    raise RuntimeError("MemAvailable unavailable")


def paraphrase_process_present() -> bool:
    return subprocess.run(["pgrep", "-f", "[d]ualiats_paraphrase"], capture_output=True, check=False).returncode == 0


def wait_for_stable_gpu() -> list[dict[str, Any]]:
    observations: list[dict[str, Any]] = []
    stable = 0
    while stable < STABLE_CHECKS:
        snap = gpu_snapshot()
        if len(snap["gpus"]) != 1:
            raise RuntimeError(f"expected exactly one GPU: {snap}")
        g0 = snap["gpus"][0]
        apps, avail, paraphrase = compute_app_count(), mem_available_kib(), paraphrase_process_present()
        eligible = (
            "A100" in g0["name"] and g0["memory_total_mib"] >= 80_000 and apps == 0
            and g0["memory_used_mib"] <= MAX_GPU_USED_MIB and avail >= MIN_AVAILABLE_KIB and not paraphrase
        )
        stable = stable + 1 if eligible else 0
        row = {"at": datetime.now(timezone.utc).isoformat(), "eligible": eligible, "stable_count": stable,
               "compute_apps": apps, "mem_available_kib": avail, "paraphrase_process_present": paraphrase, "gpu": g0}
        observations.append(row)
        print(json.dumps({"b3_gpu_gate": row}, sort_keys=True), flush=True)
        if stable < STABLE_CHECKS:
            time.sleep(STABLE_INTERVAL_SECONDS)
    return observations


class BlockingHandler(checkpoint_handler.CheckpointHandler):
    def __init__(self, name: str, inner, serial_lock: threading.Lock):
        self.name, self.inner, self.serial_lock = name, inner, serial_lock
        self.events: list[dict[str, Any]] = []

    def save(self, directory, *args, **kwargs):
        with self.serial_lock:
            start = time.monotonic_ns()
            try:
                return self.inner.save(directory, *args, **kwargs)
            finally:
                self.events.append({"item": self.name, "start_ns": start, "end_ns": time.monotonic_ns()})

    def restore(self, directory, *args, **kwargs): return self.inner.restore(directory, *args, **kwargs)
    def metadata(self, directory): return self.inner.metadata(directory)
    def finalize(self, directory): return self.inner.finalize(directory)
    def close(self): return self.inner.close()


def fingerprint_summary(rows: list[dict[str, Any]]) -> tuple[int, int, int]:
    return len(rows), sum(int(x.get("nbytes", 0)) for x in rows), max((int(x.get("nbytes", 0)) for x in rows), default=0)


def main() -> int:
    ap = argparse.ArgumentParser()
    for name in ["authority", "review", "d0d1d3", "d2-result", "b2-terminal-adjudication", "host67-revocation",
                 "serializer", "cache", "openpi-child-root", "params-root", "base-receipt", "norm-stats", "output-root", "result"]:
        ap.add_argument(f"--{name}", type=Path, required=True)
    args = ap.parse_args()
    p = {k: Path(v).resolve() if isinstance(v, Path) else v for k, v in vars(args).items()}

    authority = load_json(p["authority"])
    if authority.get("status") != "AUTHORIZED_PI05_B3_WRITEBACK_AWARE_CHECKPOINT_QUALIFICATION_69":
        raise RuntimeError("B3 authority status drift")
    if authority.get("formal_run3_authorized") is not False or authority.get("policy_evaluation_authorized") is not False:
        raise RuntimeError("B3 authority illegally opens downstream science")
    resource = authority.get("resource_scope", {})
    if resource.get("memory_max_gib") != EXPECTED_MEMORY_MAX_GIB or resource.get("memory_swap_max_gib") != 0:
        raise RuntimeError("B3 memory scope drift")
    if resource.get("d2h_batch_bytes") != DEFAULT_D2H_BATCH_BYTES:
        raise RuntimeError("B3 D2H batch drift")
    if authority.get("host", {}).get("machine_id") != EXPECTED_MACHINE_ID:
        raise RuntimeError("B3 host binding drift")
    outputs = authority.get("output_paths", {})
    if outputs.get("checkpoint_root") != str(p["output_root"]) or outputs.get("save_result") != str(p["result"]):
        raise RuntimeError("B3 output path drift")

    require_binding(authority, "save_runner", Path(__file__).resolve())
    for key in ["review", "d0d1d3", "d2_result", "b2_terminal_adjudication", "host67_revocation", "serializer", "cache"]:
        require_binding(authority, key, p[key])
    require_binding(authority, "base_receipt", p["base_receipt"])
    require_binding(authority, "norm_stats", p["norm_stats"])

    review = load_json(p["review"])
    if review.get("verdict") != "APPROVE_ONE_B3_S_V1_V2_QUALIFICATION":
        raise RuntimeError("independent B3 model review drift")
    if review.get("clarification", {}).get("reviewer_exact_line") != "V1_CONTRACT=PRESERVE_DIRECT_SHA_THEN_STANDARD_RESTORE":
        raise RuntimeError("B3 V1 contract drift")
    if load_json(p["d0d1d3"]).get("status") != "PI05_B3_D0_D1_D3_PASS":
        raise RuntimeError("B3 D0/D1/D3 not PASS")
    d2 = load_json(p["d2_result"])
    if d2.get("status") != "PI05_B3_D2_CACHE_ACCOUNTING_PASS" or d2.get("exact_sha256_roundtrip") is not True:
        raise RuntimeError("B3 D2 not PASS")
    if load_json(p["b2_terminal_adjudication"]).get("status") != "PI05_B2_HOST69_REPAIR1_SAVE_CGROUP_OOM_TERMINAL_HOLD":
        raise RuntimeError("B2 terminal lineage drift")
    revocation = load_json(p["host67_revocation"])
    if revocation.get("status") != "HOST67_USER_EXCLUDED_AND_SPLIT_HARNESS_AUTHORITY_REVOKED" or (revocation.get("host_exclusion") or {}).get("host") != "222.20.126.67":
        raise RuntimeError("host67 exclusion drift")

    if Path("/etc/machine-id").read_text().strip() != EXPECTED_MACHINE_ID:
        raise RuntimeError("B3 may run only on host69 machine-id")
    if p["result"].exists() or p["output_root"].exists():
        raise RuntimeError("B3 qualification already consumed or stale output exists")
    if sha256_file(p["norm_stats"]) != EXPECTED_NORM_SHA256:
        raise RuntimeError("normalization SHA drift")

    child_root = p["openpi_child_root"]
    child_head = subprocess.check_output(["git", "-C", str(child_root), "rev-parse", "HEAD"], text=True).strip()
    if child_head != EXPECTED_PARENT_COMMIT:
        raise RuntimeError(f"portable child parent drift: {child_head}")
    changed = sorted(line[3:] for line in subprocess.check_output(["git", "-C", str(child_root), "status", "--porcelain"], text=True).splitlines() if line.strip())
    if changed != ["src/openpi/training/config.py"]:
        raise RuntimeError(f"portable child changed-path drift: {changed}")
    config_sha = sha256_file(child_root / "src/openpi/training/config.py")
    if config_sha != EXPECTED_CONFIG_SHA256:
        raise RuntimeError("portable config SHA drift")

    # Expensive immutable-input validation occurs before waiting for a stable GPU.
    base_sha, base_count, base_bytes = validate_base(p["base_receipt"], p["params_root"])
    os.chdir(child_root)
    sys.path.insert(0, str(child_root))
    sys.path.insert(0, str(child_root / "src"))
    import openpi.models.model as model_lib
    import openpi.shared.normalize as normalize
    import openpi.training.checkpoints as checkpoints
    import openpi.training.config as config_lib
    import openpi.training.sharding as sharding
    import openpi.training.weight_loaders as weight_loaders
    from scripts.b1k import train_b1k

    stable_observations = wait_for_stable_gpu()
    gpu_before = gpu_snapshot()
    if compute_app_count() != 0:
        raise RuntimeError("GPU race after stable gate before qualification consumption")
    g0 = gpu_before["gpus"][0]
    if "A100" not in g0["name"] or g0["memory_total_mib"] < 80_000 or g0["memory_used_mib"] > MAX_GPU_USED_MIB:
        raise RuntimeError(f"B3 final GPU admission failed: {g0}")

    initial = {
        "schema_version": "behavior-formal-goal-coupling-shared26-pi05-b3-checkpoint-save-qualification-v1",
        "object_id": OBJECT_ID, "child_id": CHILD_ID, "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PI05_B3_CHECKPOINT_SAVE_QUALIFICATION_STARTED", "qualification_consumed": True,
        "authority_sha256": sha256_file(p["authority"]), "serializer_sha256": sha256_file(p["serializer"]),
        "cache_helper_sha256": sha256_file(p["cache"]), "host": "69", "machine_id": EXPECTED_MACHINE_ID,
        "memory_max_gib": EXPECTED_MEMORY_MAX_GIB, "memory_swap_max_gib": 0, "d2h_batch_bytes": DEFAULT_D2H_BATCH_BYTES,
        "enable_async_checkpointing": False, "serial_large_items": True, "save_label": SAVE_LABEL,
        "base_receipt_sha256": base_sha, "base_object_count_rehashed": base_count, "base_bytes_rehashed": base_bytes,
        "portable_openpi_parent_commit": child_head, "portable_openpi_config_sha256": config_sha,
        "stable_gpu_gate": stable_observations, "resource_scope_before": cgroup_snapshot(EXPECTED_MEMORY_MAX_BYTES),
        "resource_memory_stat_before": self_cgroup_memory_snapshot(), "host_before": host_snapshot(), "gpu_before": gpu_before,
        "train_state_ready": False, "checkpoint_save_started": False, "checkpoint_save_completed": False,
        "dataset_accessed": False, "forward_pass_executed": False, "backward_pass_executed": False,
        "optimizer_update_executed": False, "real_scientific_optimizer_updates": 0, "loss_values_read_or_reported": False,
        "policy_outcomes_read": False, "formal_run3_authorized": False,
    }
    atomic_json(p["result"], initial)

    status = "PI05_B3_CHECKPOINT_SAVE_QUALIFICATION_HOLD"
    error = None
    manager_steps: list[int] = []
    save_started = save_completed = False
    item_names: list[str] = []
    tmp_paths: list[str] = []
    output_files = output_bytes = 0
    fingerprints: dict[str, list[dict[str, Any]]] = {}
    batch_manifests: dict[str, list[dict[str, Any]]] = {}
    reclamation_manifests: dict[str, list[dict[str, Any]]] = {}
    reclamation_endpoint: dict[str, Any] = {}
    item_events: list[dict[str, Any]] = []
    snapshots: dict[str, Any] = {}

    try:
        class DirectDeviceCheckpointWeightLoader:
            def __init__(self, params_path: str): self.params_path = params_path
            def load(self, params):
                loaded = model_lib.restore_params(self.params_path, restore_type=jax.Array)
                if not all(isinstance(x, jax.Array) for x in jax.tree.leaves(loaded)):
                    raise RuntimeError("direct-device restore returned non-JAX leaves")
                return weight_loaders._merge_params(loaded, params, missing_regex=".*lora.*")

        @dataclasses.dataclass
        class DataConfigStub:
            norm_stats: object
            asset_id: object

        class LoaderStub:
            def __init__(self, stats): self._stats = stats
            def data_config(self): return DataConfigStub(norm_stats=self._stats, asset_id="b1k_shared26_frozen")

        devices = jax.devices()
        if len(devices) != 1 or devices[0].platform != "gpu":
            raise RuntimeError(f"JAX GPU device drift: {devices}")
        src = config_lib.get_config(CONFIG_NAME)
        cfg = dataclasses.replace(src, exp_name=EXP_NAME,
            weight_loader=DirectDeviceCheckpointWeightLoader(str(p["params_root"])),
            batch_size=BATCH, num_workers=0, wandb_enabled=False, resume=False, overwrite=False)
        if src.batch_size != 64 or cfg.batch_size != BATCH or cfg.seed != SEED or cfg.num_train_steps != 50_000 or cfg.model.action_horizon != 32 or cfg.fsdp_devices != 1:
            raise RuntimeError("practical batch16 config drift")

        mesh = sharding.make_mesh(cfg.fsdp_devices)
        rng = jax.random.key(cfg.seed)
        _train_rng, init_rng = jax.random.split(rng)
        state, _state_sharding = train_b1k.init_train_state(cfg, init_rng, mesh, resume=False)
        jax.block_until_ready(state)
        if int(jax.device_get(state.step)) != 0:
            raise RuntimeError("step-0 state drift")
        snapshots["after_state"] = {"cgroup": cgroup_snapshot(EXPECTED_MEMORY_MAX_BYTES),
            "memory_stat": self_cgroup_memory_snapshot(), "host": host_snapshot(), "gpu": gpu_snapshot()}

        train_registry, train_array_handler = clone_global_registry_with_writeback_aware_leaf_batched_array_handler(d2h_batch_bytes=DEFAULT_D2H_BATCH_BYTES)
        params_registry, params_array_handler = clone_global_registry_with_writeback_aware_leaf_batched_array_handler(d2h_batch_bytes=DEFAULT_D2H_BATCH_BYTES)
        serial_lock = threading.Lock()
        train_block = BlockingHandler("train_state", ocp.PyTreeCheckpointHandler(save_concurrent_gb=8, restore_concurrent_gb=8, type_handler_registry=train_registry), serial_lock)
        params_block = BlockingHandler("params", ocp.PyTreeCheckpointHandler(save_concurrent_gb=8, restore_concurrent_gb=8, type_handler_registry=params_registry), serial_lock)

        p["output_root"].mkdir(parents=True, exist_ok=False)
        manager = ocp.CheckpointManager(p["output_root"], item_handlers={
            "assets": checkpoints.CallbackHandler(), "train_state": train_block, "params": params_block},
            options=ocp.CheckpointManagerOptions(max_to_keep=1, keep_period=cfg.keep_period, create=False, enable_async_checkpointing=False))
        if isinstance(manager._checkpointer, ocp.AsyncCheckpointer):
            raise RuntimeError("B3 manager resolved to AsyncCheckpointer")

        save_started = True
        progress = dict(initial)
        progress.update({"generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "PI05_B3_CHECKPOINT_SAVE_QUALIFICATION_SAVE_STARTED", "train_state_ready": True,
            "checkpoint_save_started": True, "snapshots": snapshots})
        atomic_json(p["result"], progress)

        norm_stats = normalize.load(p["norm_stats"].parent)
        checkpoints.save_state(manager, state, LoaderStub(norm_stats), SAVE_LABEL)
        manager.wait_until_finished()
        save_completed = True
        manager_steps = list(manager.all_steps())
        if manager_steps != [SAVE_LABEL]:
            raise RuntimeError(f"manager step drift: {manager_steps}")

        fingerprints = {"train_state": train_array_handler.fingerprints, "params": params_array_handler.fingerprints}
        batch_manifests = {"train_state": train_array_handler.batch_manifest, "params": params_array_handler.batch_manifest}
        reclamation_manifests = {"train_state": train_array_handler.reclamation_manifest, "params": params_array_handler.reclamation_manifest}
        t_count, t_bytes, t_max = fingerprint_summary(fingerprints["train_state"])
        p_count, p_bytes, p_max = fingerprint_summary(fingerprints["params"])
        if (t_count, t_bytes) != (EXPECTED_TRAIN_LEAVES, EXPECTED_TRAIN_NBYTES):
            raise RuntimeError(f"train_state fingerprint aggregate drift: {t_count}/{t_bytes}")
        if (p_count, p_bytes) != (EXPECTED_PARAMS_LEAVES, EXPECTED_PARAMS_NBYTES):
            raise RuntimeError(f"params fingerprint aggregate drift: {p_count}/{p_bytes}")
        if max(t_max, p_max) != EXPECTED_MAX_LEAF_BYTES:
            raise RuntimeError(f"max leaf drift: {t_max}/{p_max}")
        if any(int(b["device_bytes"]) > DEFAULT_D2H_BATCH_BYTES for rows in batch_manifests.values() for b in rows):
            raise RuntimeError("D2H batch exceeded fixed 8GB bound")
        if len({x["name"] for x in fingerprints["train_state"]}) != t_count or len({x["name"] for x in fingerprints["params"]}) != p_count:
            raise RuntimeError("duplicate or missing fingerprint names")

        blobs = [blob for rows in reclamation_manifests.values() for batch in rows for blob in batch.get("blobs", [])]
        if not blobs:
            raise RuntimeError("B3 reclamation mechanism did not execute on any eligible OCDBT blob")
        if any(blob.get("durability_barrier") != "fsync" or blob.get("advice") != "POSIX_FADV_DONTNEED" for blob in blobs):
            raise RuntimeError("B3 reclamation event contract drift")
        file_drops = []
        for blob in blobs:
            before = int(blob["memory_after_fsync"]["memory_stat"]["file"])
            after = int(blob["memory_after_fadvise"]["memory_stat"]["file"])
            file_drops.append(max(0, before - after))
        reclamation_endpoint = {"eligible_blob_count": len(blobs), "reclaimed_bytes": sum(int(x.get("size", 0)) for x in blobs),
            "positive_file_drop_events": sum(x > 0 for x in file_drops), "max_file_drop_bytes": max(file_drops, default=0),
            "total_nonnegative_file_drop_bytes": sum(file_drops), "activity_gate_pass": True}

        item_events = train_block.events + params_block.events
        large = sorted(item_events, key=lambda x: x["start_ns"])
        if len(large) != 2 or large[1]["start_ns"] < large[0]["end_ns"]:
            raise RuntimeError(f"large item saves overlapped or missing: {large}")

        step_dir = p["output_root"] / str(SAVE_LABEL)
        item_names = sorted(x.name for x in step_dir.iterdir())
        if item_names != ["_CHECKPOINT_METADATA", "assets", "params", "train_state"]:
            raise RuntimeError(f"checkpoint item names drift: {item_names}")
        tmp_paths = [str(x) for x in p["output_root"].rglob("*orbax-checkpoint-tmp*")]
        if tmp_paths:
            raise RuntimeError(f"temporary paths remain: {tmp_paths[:8]}")
        asset = step_dir / "assets" / "b1k_shared26_frozen" / "norm_stats.json"
        if not asset.is_file() or sha256_file(asset) != EXPECTED_NORM_SHA256:
            raise RuntimeError("checkpoint normalization asset drift")
        output_files, output_bytes = tree_bytes(p["output_root"])
        snapshots["after_save"] = {"cgroup": cgroup_snapshot(EXPECTED_MEMORY_MAX_BYTES),
            "memory_stat": self_cgroup_memory_snapshot(), "host": host_snapshot(), "gpu": gpu_snapshot()}
        peak = int(snapshots["after_save"]["cgroup"]["memory_peak_bytes"])
        if peak >= EXPECTED_MEMORY_MAX_BYTES:
            raise RuntimeError(f"B3 cgroup peak reached/exceeded ceiling: {peak}")
        manager.close()
        status = "PI05_B3_CHECKPOINT_SAVE_QUALIFICATION_PASS"
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        try:
            snapshots["after_error"] = {"cgroup": cgroup_snapshot(EXPECTED_MEMORY_MAX_BYTES),
                "memory_stat": self_cgroup_memory_snapshot(), "host": host_snapshot(), "gpu": gpu_snapshot()}
        except Exception:
            pass
    finally:
        if p["output_root"].exists():
            output_files, output_bytes = tree_bytes(p["output_root"])
        final = dict(initial)
        final.update({
            "generated_at": datetime.now(timezone.utc).isoformat(), "status": status,
            "train_state_ready": bool(snapshots.get("after_state")), "checkpoint_save_started": save_started,
            "checkpoint_save_completed": save_completed, "manager_steps": manager_steps, "checkpoint_item_names": item_names,
            "temporary_paths": tmp_paths, "checkpoint_file_count": output_files, "checkpoint_bytes": output_bytes,
            "fingerprints": fingerprints, "batch_manifests": batch_manifests,
            "reclamation_manifests": reclamation_manifests, "reclamation_endpoint": reclamation_endpoint,
            "large_item_events": item_events, "snapshots": snapshots, "error": error,
            "dataset_accessed": False, "forward_pass_executed": False, "backward_pass_executed": False,
            "optimizer_update_executed": False, "real_scientific_optimizer_updates": 0,
            "loss_values_read_or_reported": False, "policy_outcomes_read": False, "formal_run3_authorized": False,
            "next_gate": "PI05_B3_BOUNDED_DISK_VERIFY" if status.endswith("PASS") else "STOP_B3_NO_AUTOMATIC_RETRY",
        })
        atomic_json(p["result"], final)

    print(json.dumps({"status": status, "manager_steps": manager_steps, "checkpoint_bytes": output_bytes,
        "reclamation_endpoint": reclamation_endpoint, "error": error}, sort_keys=True))
    return 0 if status.endswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
