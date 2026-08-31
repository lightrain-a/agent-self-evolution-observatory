from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

OBJECT_ID = "SUCC-C-BEHAVIOR2026-TWO-FAMILY-SHARED-MULTITASK-PANEL"
OPENPI_REVISION = "0cc8e355f7bac0976db1cc3139b1ff0379feea60"
PREREG_SHA256 = "483235155b6fec941969a4a766cbe15e50f2807b06828e625942f3d731d0e231"
SOURCE_QUALIFICATION_SHA256 = "cda384bf9944c4ef6271a31d0d618d22abc27a0dbdbe700266ab656c6b9497e4"
MATERIALIZATION_MANIFEST_SHA256 = "9ee70726fb70750b23053e2358d3d42d4089238cd0bd52e5b74329279e961df4"
EPISODE_INDICES_SHA256 = "0a10d07f216ac51f8cb0c3d2c1be07aaeb543e64070dd6c3cea235d49ab84b17"
SOURCE_HASHES = {
    "docs/b1k.md": "d984a4bed60f7c50b05caebb662e4c148fc95601cd1dd176c8ea2cff18e40adf",
    "scripts/b1k/train_b1k.py": "9e1ac351c8f491d0c5307963d11ab07b008548da2bcd29a4670e88622eae6507",
    "src/openpi/training/config.py": "46763413af168cde21084070ef93f2b9b00b9466caa0d09ba3bf2ba8d12222ae",
    "src/openpi/training/data_loader.py": "3818273c09d5fa46d8d5cfe8081c5c16c6bd9bb70fd1f1c1eff73bc0725d50b1",
    "src/openpi/configs/robots/b1k.py": "d3d5af8ab4c5eca57cd33cdf81fdbc23dea78aa2cb7932736c8722687d0d1e1c",
    "uv.lock": "75657cfbac40473237a6eaebc994fe998b249b44a4671d38129af198f00e4ed6",
}
CHILD_CONFIG_NAME = "pi05_b1k_shared26_frozen"
CHILD_EXP_NAME = "shared26-seed42-run1"
CHILD_REPO_ID = "b1k_shared26_frozen"
DEFAULT_DATASET_ROOT = "/data/wyt/behavior-2026-shared26-v3.0"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def derive_episode_indices(prereg: dict) -> list[int]:
    indices: list[int] = []
    for row in prereg["dataset_subset"]["task_rows"]:
        lo = int(row["episode_index_min"])
        hi = int(row["episode_index_max"])
        if hi - lo + 1 != 200:
            raise ValueError(f"task {row['task_index']} does not contain exactly 200 frozen episodes")
        indices.extend(range(lo, hi + 1))
    if len(indices) != 5200 or len(set(indices)) != 5200:
        raise ValueError("expected exactly 5200 unique frozen episode indices")
    digest = hashlib.sha256(("\n".join(map(str, indices)) + "\n").encode("utf-8")).hexdigest()
    if digest != EPISODE_INDICES_SHA256:
        raise ValueError(f"episode index digest drift: {digest}")
    return indices


def validate_openpi_source(repo: Path) -> dict:
    revision = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    if revision != OPENPI_REVISION:
        raise ValueError(f"OpenPI revision drift: {revision}")
    observed = {rel: sha256_file(repo / rel) for rel in SOURCE_HASHES}
    if observed != SOURCE_HASHES:
        raise ValueError("OpenPI source hash drift")
    config_text = (repo / "src/openpi/training/config.py").read_text(encoding="utf-8")
    loader_text = (repo / "src/openpi/training/data_loader.py").read_text(encoding="utf-8")
    docs_text = (repo / "docs/b1k.md").read_text(encoding="utf-8")
    required_config_markers = [
        'name="pi05_b1k"',
        'Pi0Config(action_horizon=32, pi05=True)',
        'repo_id="turning_on_radio"',
        'dataset_kwargs={"tolerance_s": 5e-4}',
        'robot_config_name="b1k/R1Pro"',
        'CheckpointWeightLoader("gs://openpi-assets/checkpoints/pi05_base/params")',
        'num_train_steps=50_000',
    ]
    for marker in required_config_markers:
        if marker not in config_text:
            raise ValueError(f"pinned pi05_b1k marker missing: {marker}")
    required_loader_markers = [
        'dataset_kwargs = {"repo_id": data_config.repo_id, **data_config.dataset_kwargs}',
        'dataset = data_config.data_cls(',
        '**dataset_kwargs,',
    ]
    for marker in required_loader_markers:
        if marker not in loader_text:
            raise ValueError(f"B1K dataset_kwargs forwarding marker missing: {marker}")
    if "--batch_size=64" not in docs_text or "--num_train_steps=50000" not in docs_text:
        raise ValueError("official B1K launch defaults drift")
    return {"revision": revision, "source_hashes": observed}


def compile_spec(prereg_path: Path, source_q_path: Path, materialization_path: Path, openpi_repo: Path, dataset_root: str) -> dict:
    bindings = {
        "preregistration_sha256": sha256_file(prereg_path),
        "source_qualification_sha256": sha256_file(source_q_path),
        "pi05_materialization_manifest_sha256": sha256_file(materialization_path),
    }
    expected = {
        "preregistration_sha256": PREREG_SHA256,
        "source_qualification_sha256": SOURCE_QUALIFICATION_SHA256,
        "pi05_materialization_manifest_sha256": MATERIALIZATION_MANIFEST_SHA256,
    }
    if bindings != expected:
        raise ValueError(f"upstream binding drift: {bindings}")
    prereg = load_json(prereg_path)
    source_q = load_json(source_q_path)
    materialization = load_json(materialization_path)
    if prereg.get("object_id") != OBJECT_ID or source_q.get("object_id") != OBJECT_ID or materialization.get("object_id") != OBJECT_ID:
        raise ValueError("object identity mismatch")
    if materialization.get("status") != "PI05_REQUIRED_FEATURE_MATERIALIZATION_FROZEN_ZERO_DOWNLOAD":
        raise ValueError("materialization gate not frozen")
    source = validate_openpi_source(openpi_repo)
    episode_indices = derive_episode_indices(prereg)
    return {
        "schema_version": "behavior-formal-goal-coupling-shared-multitask-pi05-child-config-v1",
        "object_id": OBJECT_ID,
        "status": "PI05_SHARED26_CHILD_CONFIG_FROZEN_ZERO_UPDATE",
        "scientific_authority": False,
        "execution_authority": False,
        "gpu_authority": False,
        "payload_materialization_authorized": False,
        "model_load_authorized": False,
        "forward_authorized": False,
        "backward_authorized": False,
        "optimizer_update_authorized": False,
        "policy_rollouts_authorized": False,
        "policy_outcomes_read": False,
        "bindings": bindings,
        "openpi": source,
        "parent_config": "pi05_b1k",
        "child_config": {
            "name": CHILD_CONFIG_NAME,
            "exp_name": CHILD_EXP_NAME,
            "repo_id": CHILD_REPO_ID,
            "dataset_root": dataset_root,
            "dataset_kwargs": {
                "tolerance_s": 0.0005,
                "episodes": episode_indices,
            },
            "batch_size": 64,
            "num_train_steps": 50000,
            "seed": 42,
            "resume": False,
            "overwrite": True,
        },
        "episode_subset": {
            "count": len(episode_indices),
            "sha256": EPISODE_INDICES_SHA256,
            "task_count": 26,
            "selection": "all 200 episodes from each frozen structure-selected task; no dropping or replacement",
        },
        "inherited_unchanged": {
            "model": "pi0.5 base from parent pi05_b1k",
            "base_checkpoint": "gs://openpi-assets/checkpoints/pi05_base/params",
            "action_horizon": 32,
            "robot_config": "b1k/R1Pro",
            "prompt_from_task": True,
            "normalization": "z-score via source B1K config; statistics must be computed on exactly the same 5200 episodes",
            "optimizer": "parent pi05_b1k / pinned source defaults",
            "lr_schedule": "parent pi05_b1k / pinned source defaults",
            "ema": "parent pi05_b1k",
            "terminal_checkpoint_rule": "source-emitted terminal step label 49999 only",
            "validation_during_training": False,
        },
        "scientific_change_boundary": {
            "only_method_change": "one shared pi0.5 checkpoint is trained on the frozen 26-task subset instead of 26 task-specific pi0.5 checkpoints",
            "allowed_config_differences": [
                "config name / experiment name",
                "local combined dataset root",
                "dataset repo identifier used for assets",
                "dataset_kwargs.episodes = frozen 5200 indices",
                "official B1K launch batch_size=64 made explicit",
            ],
            "forbidden_differences": [
                "model architecture or base checkpoint",
                "optimizer or learning-rate schedule",
                "training step horizon",
                "seed",
                "R1Pro observation/action transforms",
                "action horizon",
                "checkpoint selection by validation or policy outcome",
            ],
        },
        "execution_guard": {
            "checkpoint_directory_must_not_exist_before_launch": True,
            "exactly_once_launch_required": True,
            "automatic_retry_for_scientific_training": False,
            "preemption_recovery_requires_separate_exact-state_receipt": True,
        },
        "next_gate": "materialize only the frozen 220.24 GiB required-feature dataset, then compute/freeze source-faithful normalization stats and run zero-update data-loader/config smoke before any model load",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prereg", type=Path, required=True)
    parser.add_argument("--source-qualification", type=Path, required=True)
    parser.add_argument("--materialization", type=Path, required=True)
    parser.add_argument("--openpi-repo", type=Path, required=True)
    parser.add_argument("--dataset-root", default=DEFAULT_DATASET_ROOT)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    payload = compile_spec(args.prereg, args.source_qualification, args.materialization, args.openpi_repo, args.dataset_root)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "episode_count": payload["episode_subset"]["count"],
        "episode_sha256": payload["episode_subset"]["sha256"],
        "dataset_root": payload["child_config"]["dataset_root"],
        "artifact_sha256": sha256_file(args.out),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
