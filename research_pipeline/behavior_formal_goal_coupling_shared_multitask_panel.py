from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

PARENT_OBJECT_ID = "SUCC-C-BEHAVIOR2026-TWO-FAMILY-STRICT-MATCHED-PANEL"
OBJECT_ID = "SUCC-C-BEHAVIOR2026-TWO-FAMILY-SHARED-MULTITASK-PANEL"
PARENT_PREREG_SHA256 = "0738573af073aafd9a14f220f5f729d85adb16593cfc73043abf71e7f74f2327"
DEMO_HORIZON_RESULT_SHA256 = "0c23f7905036275cdd141e99b3de7acaa498601daa2377a88793968ad5b33a39"
OPENPI_REVISION = "0cc8e355f7bac0976db1cc3139b1ff0379feea60"
LEROBOT_REVISION = "c43f58116b975ae79af62714e1417b38facd4e37"
DATASET_REPO_ID = "behavior-1k/2026-challenge-demos"
DATASET_REVISION = "4f50b44796641a4d526a19d9aeadc8aa51e2f2c2"
GR00T_PUBLIC_REPO_ID = "kmy17518/gr00t-n1.7-b1k-multitask"
GR00T_FROZEN_CHECKPOINT = "checkpoint-238000"
EPISODES_PER_TASK = 200

OPENPI_SOURCE_HASHES = {
    "src/openpi/training/config.py": "46763413af168cde21084070ef93f2b9b00b9466caa0d09ba3bf2ba8d12222ae",
    "src/openpi/training/data_loader.py": "3818273c09d5fa46d8d5cfe8081c5c16c6bd9bb70fd1f1c1eff73bc0725d50b1",
    "src/openpi/training/lerobot_compat.py": "0e51b404471b26e5f0e139e46971e34fadf1eaa08844a7dc9e990058fd81970b",
    "scripts/compute_norm_stats.py": "af3d46e40af8162ea11d942fe5010b5fe33fff7639cc1e5ab317fc22efb09655",
    "scripts/b1k/train_b1k.py": "9e1ac351c8f491d0c5307963d11ab07b008548da2bcd29a4670e88622eae6507",
    "uv.lock": "75657cfbac40473237a6eaebc994fe998b249b44a4671d38129af198f00e4ed6",
    "README.md": "567fc57766bd736664f50126cab8145af4071ca16cc5e238f2b11e369169c3b5",
    "docs/b1k.md": "d984a4bed60f7c50b05caebb662e4c148fc95601cd1dd176c8ea2cff18e40adf",
}
LEROBOT_SOURCE_HASHES = {
    "src/lerobot/datasets/lerobot_dataset.py": "e3817ee2beb81d763afe77cdf8867d3fb3ff57b1fd8ceaee1384cd5ee8b39b82",
    "src/lerobot/datasets/multi_dataset.py": "022b41031bd10d98747fd909336ec79ea94135375fa82c90eb1d2cb5e8774fd6",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_parent(path: Path) -> dict:
    actual = sha256_file(path)
    if actual != PARENT_PREREG_SHA256:
        raise ValueError(f"strict parent preregistration drift: {actual}")
    parent = load_json(path)
    if parent.get("object_id") != PARENT_OBJECT_ID:
        raise ValueError("strict parent object mismatch")
    panel = parent.get("panel") or {}
    if panel.get("pair_count") != 13 or panel.get("task_count") != 26:
        raise ValueError("strict parent panel cardinality drift")
    if len(panel.get("pairs") or []) != 13 or len(panel.get("task_indices") or []) != 26:
        raise ValueError("strict parent panel content drift")
    return parent


def expected_episode_ranges(task_indices: list[int]) -> list[dict]:
    return [
        {
            "task_index": int(t),
            "episode_index_min": int(t) * EPISODES_PER_TASK,
            "episode_index_max": int(t) * EPISODES_PER_TASK + EPISODES_PER_TASK - 1,
            "episode_count": EPISODES_PER_TASK,
        }
        for t in task_indices
    ]


def selected_episode_ids(task_indices: list[int]) -> list[int]:
    out: list[int] = []
    for row in expected_episode_ranges(task_indices):
        out.extend(range(row["episode_index_min"], row["episode_index_max"] + 1))
    return out


def episode_digest(task_indices: list[int]) -> str:
    raw = "\n".join(map(str, selected_episode_ids(task_indices))) + "\n"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def compile_source_qualification(openpi_root: Path) -> dict:
    observed = {}
    for rel, expected in OPENPI_SOURCE_HASHES.items():
        actual = sha256_file(openpi_root / rel)
        if actual != expected:
            raise ValueError(f"OpenPI source drift for {rel}: {actual}")
        observed[rel] = actual

    config_text = (openpi_root / "src/openpi/training/config.py").read_text(encoding="utf-8")
    loader_text = (openpi_root / "src/openpi/training/data_loader.py").read_text(encoding="utf-8")
    norm_text = (openpi_root / "scripts/compute_norm_stats.py").read_text(encoding="utf-8")
    train_text = (openpi_root / "scripts/b1k/train_b1k.py").read_text(encoding="utf-8")
    uv_text = (openpi_root / "uv.lock").read_text(encoding="utf-8")
    readme_text = (openpi_root / "README.md").read_text(encoding="utf-8")
    gates = {
        "dataset_kwargs_exposed": "dataset_kwargs: dict[str, Any]" in config_text,
        "b1k_loader_forwards_dataset_kwargs": "**data_config.dataset_kwargs" in loader_text,
        "b1k_loader_uses_lerobot_metadata": "LeRobotDatasetMetadata" in loader_text,
        "norm_stats_reuses_b1k_dataset": "create_b1k_dataset" in norm_text,
        "device_count_not_hardcoded": "jax.device_count()" in train_text,
        "lerobot_exact_revision_locked": LEROBOT_REVISION in uv_text,
        "single_a100_full_finetune_documented": "A100 (80GB)" in readme_text,
    }
    if not all(gates.values()):
        raise ValueError(f"source qualification failed: {gates}")

    return {
        "schema_version": "behavior-formal-goal-coupling-shared-multitask-source-qualification-v1",
        "object_id": OBJECT_ID,
        "status": "SOURCE_QUALIFIED_SHARED_CHILD_PREFLIGHT_ONLY",
        "scientific_authority": False,
        "execution_authority": False,
        "gpu_authority": False,
        "model_load_authorized": False,
        "policy_training_authorized": False,
        "policy_rollouts_authorized": False,
        "policy_outcomes_read": False,
        "openpi": {
            "revision": OPENPI_REVISION,
            "source_hashes": observed,
            "semantic_gates": gates,
            "source_native_capability": (
                "B1K DataConfig forwards dataset constructor kwargs; B1K normalization uses the same dataset path; "
                "training data parallelism is sized from visible JAX devices. A child may therefore select a frozen "
                "episode subset by configuration without changing the model, optimizer, transforms, or training loop."
            ),
        },
        "lerobot": {
            "revision": LEROBOT_REVISION,
            "source_hashes_verified_on_independent_source_audit_host": LEROBOT_SOURCE_HASHES,
            "episode_subset_semantics": (
                "Pinned LeRobotDataset accepts an explicit episodes list, retains full dataset metadata/task mapping, "
                "and passes the subset to DatasetReader before selective file loading."
            ),
            "multi_dataset_wrapper_required": False,
        },
        "dataset": {
            "repo_id": DATASET_REPO_ID,
            "revision": DATASET_REVISION,
            "layout": "one official LeRobot v3 dataset containing all 100 challenge tasks",
        },
        "method_change_boundary": {
            "exact_parent_replication": False,
            "only_scientific_change": "train one shared pi0.5 checkpoint on the frozen 26-task subset instead of 26 task-specific pi0.5 checkpoints",
            "unchanged": [
                "pi0.5 base model/checkpoint",
                "B1K R1Pro observation/action transforms",
                "optimizer and learning-rate schedule",
                "seed 42",
                "batch size 64",
                "50000 update horizon",
                "terminal checkpoint selection",
                "official evaluator and public instances 0..9",
            ],
        },
        "next_gate": "qualify the outcome-blind 5200-episode subset and freeze the child preregistration",
    }


def qualify_subset(parent_path: Path, metadata_root: Path) -> dict:
    parent = validate_parent(parent_path)
    task_indices = [int(x) for x in parent["panel"]["task_indices"]]
    try:
        import pyarrow.parquet as pq
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("pyarrow is required for metadata-only subset qualification") from exc

    activity_by_index = {}
    for pair in parent["panel"]["pairs"]:
        activity_by_index[int(pair["low_task_index"])] = str(pair["low_activity"])
        activity_by_index[int(pair["high_task_index"])] = str(pair["high_activity"])

    rows = []
    all_ids: list[int] = []
    for expected in expected_episode_ranges(task_indices):
        t = int(expected["task_index"])
        path = metadata_root / f"chunk-{t:03d}" / "file-000.parquet"
        table = pq.read_table(path, columns=["episode_index", "task_index", "tasks"])
        data = table.to_pydict()
        ids = [int(x) for x in data["episode_index"]]
        task_set = {int(x) for x in data["task_index"]}
        task_strings = sorted({str(v) for row in data["tasks"] for v in row})
        if len(ids) != EPISODES_PER_TASK or task_set != {t}:
            raise ValueError(f"task {t} metadata cardinality/task-index mismatch")
        if ids != list(range(expected["episode_index_min"], expected["episode_index_max"] + 1)):
            raise ValueError(f"task {t} global episode range mismatch")
        if task_strings != [activity_by_index[t]]:
            raise ValueError(f"task {t} activity mismatch: {task_strings} vs {activity_by_index[t]}")
        all_ids.extend(ids)
        rows.append({**expected, "activity": task_strings[0], "metadata_sha256": sha256_file(path)})

    if len(all_ids) != 5200 or len(set(all_ids)) != 5200:
        raise ValueError("selected subset must contain exactly 5200 unique episodes")
    return {
        "schema_version": "behavior-formal-goal-coupling-shared-multitask-subset-qualification-v1",
        "object_id": OBJECT_ID,
        "status": "EPISODE_SUBSET_METADATA_QUALIFIED_PAYLOAD_MANIFEST_HOLD",
        "scientific_authority": False,
        "execution_authority": False,
        "gpu_authority": False,
        "model_load_authorized": False,
        "payload_materialization_authorized": False,
        "policy_outcomes_read": False,
        "dataset": {"repo_id": DATASET_REPO_ID, "revision": DATASET_REVISION},
        "parent_preregistration_sha256": PARENT_PREREG_SHA256,
        "selection_outcome_blind": True,
        "task_count": 26,
        "episode_count": 5200,
        "episode_indices_sha256": episode_digest(task_indices),
        "task_rows": rows,
        "metadata_columns_read": ["episode_index", "task_index", "tasks"],
        "explicitly_not_read": ["length", "reward/success/done", "policy outcomes"],
        "next_gate": "derive an exact selected data/video LFS path+OID+size manifest before any payload materialization",
    }


def compile_preregistration(parent_path: Path, source_path: Path, subset_path: Path, demo_path: Path) -> dict:
    parent = validate_parent(parent_path)
    source = load_json(source_path)
    subset = load_json(subset_path)
    if source.get("object_id") != OBJECT_ID or source.get("status") != "SOURCE_QUALIFIED_SHARED_CHILD_PREFLIGHT_ONLY":
        raise ValueError("source qualification mismatch")
    if subset.get("object_id") != OBJECT_ID or subset.get("status") != "EPISODE_SUBSET_METADATA_QUALIFIED_PAYLOAD_MANIFEST_HOLD":
        raise ValueError("subset qualification mismatch")
    if sha256_file(demo_path) != DEMO_HORIZON_RESULT_SHA256:
        raise ValueError("demo-horizon negative-control artifact drift")
    task_indices = [int(x) for x in parent["panel"]["task_indices"]]
    if subset.get("episode_indices_sha256") != episode_digest(task_indices):
        raise ValueError("episode subset digest drift")

    return {
        "schema_version": "behavior-formal-goal-coupling-shared-multitask-panel-preregistration-v1",
        "object_id": OBJECT_ID,
        "parent_object_id": PARENT_OBJECT_ID,
        "status": "PREREGISTERED_SHARED_CHILD_PAYLOAD_MANIFEST_HOLD",
        "scientific_authority": False,
        "execution_authority": False,
        "gpu_authority": False,
        "model_load_authorized": False,
        "policy_training_authorized": False,
        "policy_rollouts_authorized": False,
        "policy_outcomes_read": False,
        "scientific_question": (
            "Within two frozen shared multi-task VLA policy units, is official BEHAVIOR task Q lower on the "
            "higher-coupling member of exact structure-matched task pairs?"
        ),
        "claim_boundary": {
            "allowed_if_supported": "narrow two-family shared-checkpoint association on the frozen 13-pair/26-task panel",
            "forbidden": [
                "three-family or broad cross-policy generalization",
                "projection to the task-specific strict parent",
                "lowering or reopening the frozen three-family confirmatory gate",
                "PORT-010 reopening",
                "causal wording",
            ],
        },
        "panel": parent["panel"],
        "dataset_subset": {
            "repo_id": DATASET_REPO_ID,
            "revision": DATASET_REVISION,
            "task_count": 26,
            "episode_count": 5200,
            "episode_indices_sha256": subset["episode_indices_sha256"],
            "task_rows": subset["task_rows"],
            "selection_rule": "all 200 official public demonstrations for each of the 26 outcome-blind structure-selected tasks; no dropping/replacement",
        },
        "policy_units": {
            "pi0.5": {
                "role": "ONE_SHARED_26_TASK_PROSPECTIVE_CHECKPOINT",
                "repo_revision": OPENPI_REVISION,
                "base_checkpoint": "gs://openpi-assets/checkpoints/pi05_base/params",
                "training_jobs": 1,
                "seed": 42,
                "batch_size": 64,
                "num_train_steps": 50000,
                "action_horizon": 32,
                "checkpoint_selection": "terminal source label 49999 only",
                "dataset": "official combined BEHAVIOR 2026 LeRobot v3 dataset restricted to the frozen 5200 episodes",
                "normalization": "source B1K z-score statistics computed over exactly the same 5200-episode subset and frozen before model update",
                "config_change_only": True,
                "model_or_training_loop_change": False,
            },
            "GR00T N1.7": {
                "role": "ONE_PUBLIC_SHARED_100_TASK_CHECKPOINT_EVALUATED_ON_FROZEN_26_TASK_PANEL",
                "public_repo_id": GR00T_PUBLIC_REPO_ID,
                "checkpoint": GR00T_FROZEN_CHECKPOINT,
                "training_jobs": 0,
                "selection_reason": "freeze the public model-card terminal/final snapshot before any local policy evaluation; no late-snapshot shopping",
                "content_address_status": "PENDING_EXACT_HF_REVISION_AND_REQUIRED_FILE_OID_SIZE_FREEZE",
                "lineage": "same admitted GR00T N1.7 family; never counted as a third family",
            },
        },
        "primary_analysis": {
            "task_score": "official evaluator Q averaged over exactly public instances 0..9 for each task/policy unit",
            "pair_contrast_per_family": "Q(high-coupling) - Q(low-coupling)",
            "pair_contrast_primary": "mean of the pi0.5 and GR00T pair contrasts for each pair",
            "primary_statistic": "mean of the 13 two-family pair contrasts",
            "exact_test": "two-sided sign-flip randomization over all 2^13 = 8192 pair-label assignments",
            "direction_required": "primary mean < 0",
            "alpha": 0.05,
            "corroboration": "median within-family pair contrast < 0 separately for pi0.5 and GR00T N1.7",
            "support_rule": "primary mean < 0 AND exact two-sided p < 0.05 AND both family medians < 0",
            "no_pair_weighting": True,
            "no_covariate_search": True,
            "no_pair_dropping": True,
            "no_task_replacement": True,
            "no_checkpoint_shopping": True,
        },
        "negative_control": {
            "artifact": str(demo_path),
            "sha256": DEMO_HORIZON_RESULT_SHA256,
            "frozen_result": "DEMO_HORIZON_PRIMARY_NOT_SUPPORTED",
            "use": "interpretive negative control only; never a covariate, exclusion rule, or rescue analysis",
        },
        "resource_reduction": {
            "task_specific_parent_training_jobs": 52,
            "shared_child_training_jobs": 1,
            "training_job_reduction": 51,
            "GR00T_reuses_public_checkpoint": True,
            "evaluation_rollouts_if_later_authorized": 520,
        },
        "pre_execution_gates": [
            "exact selected data/video LFS path+OID+size manifest",
            "exact content-addressed freeze of public GR00T terminal checkpoint",
            "pi0.5 26-task configuration patch hash and zero-update config/data-loader smoke",
            "pi0.5 selected-subset normalization artifact hash",
            "single-A100 model-load/memory preflight if separately authorized",
            "explicit execution authority before optimizer update or policy rollout",
        ],
        "allowed_now": [
            "source-only and metadata-only qualification",
            "exact LFS payload budget/manifest computation without payload download",
            "GR00T repository metadata/OID freeze without weight download",
            "compile/test pi0.5 child configuration without model load",
        ],
        "forbidden_now": [
            "policy model download/load",
            "forward/backward pass",
            "optimizer update",
            "policy rollout",
            "policy success/Q/reward read",
            "changing task/pair selection using future performance",
            "using this child as evidence that the old three-family gate passed",
        ],
        "bindings": {
            "parent_preregistration_sha256": PARENT_PREREG_SHA256,
            "source_qualification_sha256": sha256_file(source_path),
            "subset_qualification_sha256": sha256_file(subset_path),
            "demo_horizon_result_sha256": DEMO_HORIZON_RESULT_SHA256,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("source-qualify")
    p.add_argument("--openpi-root", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("subset-qualify")
    p.add_argument("--parent", type=Path, required=True)
    p.add_argument("--metadata-root", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("preregister")
    p.add_argument("--parent", type=Path, required=True)
    p.add_argument("--source-qualification", type=Path, required=True)
    p.add_argument("--subset", type=Path, required=True)
    p.add_argument("--demo-result", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "source-qualify":
        payload = compile_source_qualification(args.openpi_root)
    elif args.command == "subset-qualify":
        payload = qualify_subset(args.parent, args.metadata_root)
    else:
        payload = compile_preregistration(args.parent, args.source_qualification, args.subset, args.demo_result)
    write_json(args.out, payload)
    print(json.dumps({"object_id": payload["object_id"], "status": payload["status"], "sha256": sha256_file(args.out)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
