from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import pickle
import sys
import types
from pathlib import Path
from typing import Any

EXPECTED = {
    "bedroom_sgdiffusion_vq_objfeat_epoch_01999.pth": {
        "sha256": "9a69ad6a057face435e537f0fce292ec04e4491334d0a94f20166ee0cdd48217",
        "size": 818933394,
    },
    "bedroom_sg2scdiffusion_objfeat_epoch_01999.pth": {
        "sha256": "1ba66bad5b1e158681c0d251bbcdeadd305a0e666a6b71ac764d691dc3a950d0",
        "size": 411813716,
    },
    "threedfront_objfeat_vqvae_epoch_01999.pth": {
        "sha256": "e1c577fd55681138c7191394db5113cedcb4da5ffab2eac7272d399c33bb9cb4",
        "size": 365619721,
    },
    "objfeat_bounds.pkl": {
        "sha256": "e2f290af3fe934443fce03f8d2f34adbffaf7974dcab349d517723205d4d0d30",
        "size": 159,
    },
}
EXPECTED_SOURCE_REVISION = "a9097a62c484c56ac7be5ec2928ef497cbbaaf24"
EXPECTED_DATASET_REVISION = "c8cf0bd282699d56a7940ac588ea5e961b1260cb"
CASE_COUNT_MIN = 3
CASE_COUNT_MAX = 10
PREDICATES = [
    "above",
    "left of",
    "in front of",
    "closely left of",
    "closely in front of",
    "below",
    "right of",
    "behind",
    "closely right of",
    "closely behind",
]


def sha256_file(path: Path) -> str:
    block = 4 * 1024 * 1024
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(block):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    payload = json.dumps(value, sort_keys=True, indent=2) + "\n"
    tmp.write_text(payload, encoding="utf-8")
    os.replace(tmp, path)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_inputs(args: argparse.Namespace) -> dict[str, Any]:
    import subprocess

    if not CASE_COUNT_MIN <= args.case_count <= CASE_COUNT_MAX:
        raise SystemExit(
            f"case count must be {CASE_COUNT_MIN}-{CASE_COUNT_MAX}, got {args.case_count}"
        )
    construct = load_json(args.construct_artifact)
    if construct.get("object_id") != "RELATIONAL-CONSTRAINT-CAPACITY-20260830":
        raise SystemExit("construct object identity drift")
    qualification = construct.get("construct_qualification_v2") or {}
    if qualification.get("verdict") != "PASS":
        raise SystemExit("construct qualification v2 is not PASS")
    if any((construct.get("authority") or {}).values()):
        raise SystemExit("construct authority drifted open")

    source_head = subprocess.check_output(
        ["git", "-C", str(args.source_repo), "rev-parse", "HEAD"], text=True
    ).strip()
    if source_head != EXPECTED_SOURCE_REVISION:
        raise SystemExit(f"source revision drift: {source_head}")

    assets = {}
    for filename, expected in EXPECTED.items():
        path = args.asset_dir / filename
        if not path.is_file():
            raise SystemExit(f"missing smoke asset: {path}")
        actual_size = path.stat().st_size
        actual_hash = sha256_file(path)
        if actual_size != expected["size"] or actual_hash != expected["sha256"]:
            raise SystemExit(f"asset drift: {filename}")
        assets[filename] = {"size": actual_size, "sha256": actual_hash}
    return {
        "construct_artifact_sha256": sha256_file(args.construct_artifact),
        "source_revision": source_head,
        "dataset_repository_revision": EXPECTED_DATASET_REVISION,
        "assets": assets,
    }


def build_case_specs(case_count: int) -> list[dict[str, Any]]:
    return [
        {
            "case_id": f"smoke-{index:03d}",
            "seed": 2026083000 + index,
            "synthetic_conditioning": True,
            "target_evaluator_predicate": PREDICATES[index % len(PREDICATES)],
        }
        for index in range(case_count)
    ]


def case_input_hash(spec: dict[str, Any], manifest: dict[str, Any]) -> str:
    stable = {
        "case_spec": spec,
        "source_revision": manifest["source_revision"],
        "asset_hashes": {
            key: value["sha256"] for key, value in manifest["assets"].items()
        },
        "pipeline_label": "NON_SCIENTIFIC_EXECUTION_SMOKE",
    }
    return sha256_bytes(canonical_json(stable))


def load_compute_loc_rel(source_repo: Path):
    module_path = source_repo / "src" / "data" / "utils_text.py"
    fake_nltk = types.ModuleType("nltk")
    fake_corpus = types.ModuleType("nltk.corpus")
    fake_corpus.cmudict = types.SimpleNamespace(dict=lambda: {})
    fake_nltk.corpus = fake_corpus
    previous_nltk = sys.modules.get("nltk")
    previous_corpus = sys.modules.get("nltk.corpus")
    sys.modules["nltk"] = fake_nltk
    sys.modules["nltk.corpus"] = fake_corpus
    try:
        spec = importlib.util.spec_from_file_location(
            "_instructscene_utils_text_smoke", module_path
        )
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot load official evaluator module")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        if previous_nltk is None:
            sys.modules.pop("nltk", None)
        else:
            sys.modules["nltk"] = previous_nltk
        if previous_corpus is None:
            sys.modules.pop("nltk.corpus", None)
        else:
            sys.modules["nltk.corpus"] = previous_corpus
    return module.compute_loc_rel, sha256_file(module_path)


def trs_to_corners(translation, angle: float, size):
    import numpy as np

    template = np.array(
        [
            [-1, -1, -1],
            [-1, -1, 1],
            [-1, 1, -1],
            [-1, 1, 1],
            [1, -1, -1],
            [1, -1, 1],
            [1, 1, -1],
            [1, 1, 1],
        ]
    )
    rotation = np.zeros((3, 3))
    rotation[0, 0] = np.cos(angle)
    rotation[0, 2] = -np.sin(angle)
    rotation[2, 0] = np.sin(angle)
    rotation[2, 2] = np.cos(angle)
    rotation[1, 1] = 1.0
    return (template * size).dot(rotation) + translation


def apply_ema(model, checkpoint: dict[str, Any]) -> int:
    import torch

    shadow = checkpoint["ema_states"]["shadow_params"]
    parameters = list(model.parameters())
    if len(shadow) != len(parameters):
        raise RuntimeError(
            f"EMA parameter count mismatch: {len(shadow)} != {len(parameters)}"
        )
    with torch.no_grad():
        for target, source in zip(parameters, shadow):
            target.copy_(source.to(device=target.device, dtype=target.dtype))
    return len(shadow)


def install_stats_logger_shim(source_repo: Path) -> str:
    """Load only the official logger, avoiding visualization-only data imports."""
    import src

    utils_path = source_repo / "src" / "utils"
    package = types.ModuleType("src.utils")
    package.__path__ = [str(utils_path)]
    package.__package__ = "src.utils"
    sys.modules["src.utils"] = package

    logger_path = utils_path / "logger.py"
    spec = importlib.util.spec_from_file_location("src.utils.logger", logger_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load official StatsLogger")
    module = importlib.util.module_from_spec(spec)
    sys.modules["src.utils.logger"] = module
    spec.loader.exec_module(module)
    package.logger = module
    return sha256_file(logger_path)


def load_models(args: argparse.Namespace):
    import torch

    sys.path.insert(0, str(args.source_repo))
    logger_sha = install_stats_logger_shim(args.source_repo)
    from src.models import ObjectFeatureVQVAE, model_from_config
    from src.models.sg2sc_diffusion import Sg2ScDiffusion

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    if device.type != "cuda":
        raise RuntimeError("GPU unavailable for checkpoint smoke")

    bounds_path = args.asset_dir / "objfeat_bounds.pkl"
    with bounds_path.open("rb") as handle:
        bounds = pickle.load(handle)

    vqvae = ObjectFeatureVQVAE("openshape_vitg14", "gumbel", **bounds)
    vq_checkpoint = torch.load(
        args.asset_dir / "threedfront_objfeat_vqvae_epoch_01999.pth",
        map_location="cpu",
        weights_only=True,
        mmap=True,
    )
    vqvae.load_state_dict(vq_checkpoint["model"], strict=True)
    vq_ema_count = apply_ema(vqvae, vq_checkpoint)
    del vq_checkpoint
    vqvae = vqvae.to(device).eval()

    sg = model_from_config(
        {"name": "vq_objfeat_sg_gtf"},
        num_objs=21,
        num_preds=10,
        text_emb_dim=512,
    )
    sg_checkpoint = torch.load(
        args.asset_dir / "bedroom_sgdiffusion_vq_objfeat_epoch_01999.pth",
        map_location="cpu",
        weights_only=True,
        mmap=True,
    )
    sg.load_state_dict(sg_checkpoint["model"], strict=True)
    sg_ema_count = apply_ema(sg, sg_checkpoint)
    del sg_checkpoint
    sg = sg.to(device).eval()

    sg2sc = Sg2ScDiffusion(21, 10, use_objfeat=True)
    sg2sc_checkpoint = torch.load(
        args.asset_dir / "bedroom_sg2scdiffusion_objfeat_epoch_01999.pth",
        map_location="cpu",
        weights_only=True,
        mmap=True,
    )
    sg2sc.load_state_dict(sg2sc_checkpoint["model"], strict=True)
    sg2sc_ema_count = apply_ema(sg2sc, sg2sc_checkpoint)
    del sg2sc_checkpoint
    sg2sc = sg2sc.to(device).eval()

    return (
        torch,
        device,
        vqvae,
        sg,
        sg2sc,
        {
            "vqvae_ema_parameters": vq_ema_count,
            "sg_ema_parameters": sg_ema_count,
            "sg2sc_ema_parameters": sg2sc_ema_count,
            "stats_logger_source_sha256": logger_sha,
            "visualization_import_shim": (
                "Loaded official src/utils/logger.py directly; visualization and licensed "
                "dataset imports are outside this synthetic smoke."
            ),
        },
    )


def execute_batch(args: argparse.Namespace, specs: list[dict[str, Any]]):
    torch, device, vqvae, sg, sg2sc, load_audit = load_models(args)
    import torch.nn.functional as F
    from src.models.sg_diffusion_vq_objfeat import scatter_trilist_to_matrix

    compute_loc_rel, evaluator_sha = load_compute_loc_rel(args.source_repo)
    batch_size = len(specs)
    num_nodes = 12

    conditions = []
    pooled = []
    for spec in specs:
        generator = torch.Generator(device="cpu").manual_seed(spec["seed"])
        conditions.append(torch.randn(77, 512, generator=generator))
        pooled.append(torch.randn(512, generator=generator))
    text_hidden = torch.stack(conditions).to(device)
    text_pooled = torch.stack(pooled).to(device)

    torch.manual_seed(20260830)
    torch.cuda.manual_seed_all(20260830)
    with torch.no_grad():
        node_logits, edge_logits, objfeat_indices = sg.generate_samples(
            batch_size,
            num_nodes,
            text_hidden,
            text_pooled,
            cfg_scale=1.0,
            skip_step=99,
        )
    if node_logits.shape != (batch_size, num_nodes, 22):
        raise RuntimeError(f"unexpected SG node shape: {tuple(node_logits.shape)}")
    if edge_logits.shape != (
        batch_size,
        num_nodes * (num_nodes - 1) // 2,
        11,
    ):
        raise RuntimeError(f"unexpected SG edge shape: {tuple(edge_logits.shape)}")

    objs = node_logits.argmax(dim=-1)
    fixture_patch_count = 0
    for index in range(batch_size):
        active = (objs[index] != 21).nonzero(as_tuple=False).flatten()
        if len(active) < 2:
            objs[index, 0] = index % 21
            objs[index, 1] = (index + 1) % 21
            fixture_patch_count += 1
    obj_masks = (objs != 21).long()
    replacement = torch.randint_like(objfeat_indices, 0, 64)
    objfeat_indices = torch.where(
        objfeat_indices == 64, replacement, objfeat_indices
    )

    edges = edge_logits.argmax(dim=-1)
    edges = F.one_hot(edges, num_classes=11).float()
    edges = scatter_trilist_to_matrix(edges, num_nodes)
    edge_mask_1 = obj_masks.unsqueeze(1).unsqueeze(-1)
    edge_mask_2 = obj_masks.unsqueeze(2).unsqueeze(-1)
    edges = edges * edge_mask_1 * edge_mask_2
    reverse_index = [5, 6, 7, 8, 9, 0, 1, 2, 3, 4, 10]
    edges_reverse = edges[..., reverse_index]
    edges = edges + edges_reverse.permute(0, 2, 1, 3)
    diagonal = torch.eye(num_nodes, device=device).bool().unsqueeze(0).unsqueeze(-1)
    edge_mask = ((~diagonal).float() * edge_mask_1 * edge_mask_2).squeeze(-1)
    empty = edges.sum(dim=-1) == 0
    edges_empty = edges[empty]
    edges_empty[..., -1] = 1.0
    edges[empty] = edges_empty
    edges = edges.argmax(dim=-1)
    if not torch.all((edges != 10).long() <= edge_mask.long()):
        raise RuntimeError("edge masking invariant failed")

    torch.manual_seed(20260831)
    torch.cuda.manual_seed_all(20260831)
    with torch.no_grad():
        boxes = sg2sc.generate_samples(
            objs,
            edges,
            objfeat_indices,
            obj_masks,
            vqvae,
            num_timesteps=2,
            cfg_scale=1.0,
        )
    if boxes.shape != (batch_size, num_nodes, 8):
        raise RuntimeError(f"unexpected SG2SC shape: {tuple(boxes.shape)}")
    if not torch.isfinite(boxes).all():
        raise RuntimeError("non-finite SG2SC output")

    case_audits = []
    boxes_cpu = boxes.detach().cpu().numpy()
    objs_cpu = objs.detach().cpu().numpy()
    masks_cpu = obj_masks.detach().cpu().numpy()
    for index, spec in enumerate(specs):
        active = [i for i, value in enumerate(masks_cpu[index]) if value]
        if len(active) < 2:
            raise RuntimeError(f"case {spec['case_id']} has fewer than two active nodes")
        a, b = active[:2]
        ta = boxes_cpu[index, a, :3]
        tb = boxes_cpu[index, b, :3]
        sa = abs(boxes_cpu[index, a, 3:6]) + 0.05
        sb = abs(boxes_cpu[index, b, 3:6]) + 0.05
        ra = math.atan2(
            float(boxes_cpu[index, a, 6]), float(boxes_cpu[index, a, 7])
        )
        rb = math.atan2(
            float(boxes_cpu[index, b, 6]), float(boxes_cpu[index, b, 7])
        )
        corners_a = trs_to_corners(ta, ra, sa)
        corners_b = trs_to_corners(tb, rb, sb)
        evaluator_value = compute_loc_rel(
            corners_a,
            corners_b,
            f"object_{int(objs_cpu[index, a])}",
            f"object_{int(objs_cpu[index, b])}",
        )
        if evaluator_value is not None and evaluator_value not in PREDICATES:
            raise RuntimeError(f"official evaluator returned invalid relation: {evaluator_value}")
        tensor_digest = hashlib.sha256(
            boxes[index].detach().cpu().contiguous().numpy().tobytes()
        ).hexdigest()
        case_audits.append(
            {
                "case_id": spec["case_id"],
                "input_hash": None,
                "component_checks": {
                    "sg_checkpoint_forward": True,
                    "sg2sc_checkpoint_forward": True,
                    "official_compute_loc_rel_called": True,
                    "official_evaluator_return_in_vocabulary_or_none": True,
                },
                "technical_output": {
                    "sg_node_shape": list(node_logits[index].shape),
                    "sg_edge_shape": list(edge_logits[index].shape),
                    "sg2sc_box_shape": list(boxes[index].shape),
                    "sg2sc_tensor_sha256": tensor_digest,
                    "evaluator_value_redacted": True,
                },
                "synthetic_fixture_patch_applied": len(
                    (node_logits[index].argmax(dim=-1) != 21)
                    .nonzero(as_tuple=False)
                    .flatten()
                )
                < 2,
            }
        )
    return case_audits, {
        **load_audit,
        "device": str(device),
        "torch_version": torch.__version__,
        "cuda_device_name": torch.cuda.get_device_name(device),
        "evaluator_source_sha256": evaluator_sha,
        "sg_fast_sampling_network_steps": 2,
        "sg2sc_ddpm_steps": 2,
        "fixture_patch_case_count": fixture_patch_count,
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    manifest = verify_inputs(args)
    specs = build_case_specs(args.case_count)
    args.run_dir.mkdir(parents=True, exist_ok=True)
    case_dir = args.run_dir / "cases"
    case_dir.mkdir(parents=True, exist_ok=True)

    missing_specs = []
    skipped = 0
    pre_hashes = {}
    for spec in specs:
        expected_input_hash = case_input_hash(spec, manifest)
        path = case_dir / f"{spec['case_id']}.json"
        if path.exists():
            existing = load_json(path)
            if existing.get("input_hash") != expected_input_hash:
                raise SystemExit(f"resume input hash mismatch: {spec['case_id']}")
            if existing.get("pipeline_label") != "NON_SCIENTIFIC_EXECUTION_SMOKE":
                raise SystemExit(f"resume label mismatch: {spec['case_id']}")
            skipped += 1
            pre_hashes[spec["case_id"]] = sha256_file(path)
        else:
            missing_specs.append(spec)

    execution_audit = None
    if missing_specs:
        audits, execution_audit = execute_batch(args, missing_specs)
        by_id = {row["case_id"]: row for row in audits}
        for spec in missing_specs:
            row = by_id[spec["case_id"]]
            row["input_hash"] = case_input_hash(spec, manifest)
            row.update(
                {
                    "pipeline_label": "NON_SCIENTIFIC_EXECUTION_SMOKE",
                    "scientific_evidence_eligible": False,
                    "p1_projection_forbidden": True,
                    "official_reproduction_evidence": False,
                    "metric_projection": {
                        "relation_level_iRecall": "FORBIDDEN",
                        "exact_all_success": "FORBIDDEN",
                    },
                }
            )
            atomic_json(case_dir / f"{spec['case_id']}.json", row)

    post_hashes = {
        spec["case_id"]: sha256_file(case_dir / f"{spec['case_id']}.json")
        for spec in specs
    }
    for case_id, before in pre_hashes.items():
        if post_hashes[case_id] != before:
            raise RuntimeError(f"resume mutated completed case: {case_id}")

    summary_path = args.run_dir / "run-summary.json"
    previous = load_json(summary_path) if summary_path.exists() else {}
    history = list(previous.get("invocations") or [])
    invocation = {
        "invocation_index": len(history) + 1,
        "processed_cases": len(missing_specs),
        "resume_skipped_cases": skipped,
        "case_hashes_after": post_hashes,
        "completed_case_count": len(post_hashes),
        "execution_audit": execution_audit,
    }
    history.append(invocation)
    first_forward_pass = any(
        row.get("processed_cases") == args.case_count for row in history
    )
    resume_pass = any(
        row.get("processed_cases") == 0
        and row.get("resume_skipped_cases") == args.case_count
        for row in history
    )
    overall = first_forward_pass and resume_pass
    summary = {
        "schema_version": "non-scientific-execution-smoke-v1",
        "object_id": "RELATIONAL-CONSTRAINT-CAPACITY-20260830",
        "run_id": args.run_id,
        "pipeline_label": "NON_SCIENTIFIC_EXECUTION_SMOKE",
        "case_count": args.case_count,
        "manifest": manifest,
        "components": {
            "checkpoint_hash_and_load": "PASS" if first_forward_pass else "PENDING",
            "sg_inference": "PASS" if first_forward_pass else "PENDING",
            "sg2sc_inference": "PASS" if first_forward_pass else "PENDING",
            "official_evaluator_call": "PASS" if first_forward_pass else "PENDING",
            "atomic_per_case_checkpoint": "PASS" if first_forward_pass else "PENDING",
            "resume_idempotency": "PASS" if resume_pass else "PENDING",
        },
        "invocations": history,
        "verdict": "PASS" if overall else "PENDING_SECOND_RESUME_INVOCATION",
        "scientific_evidence_eligible": False,
        "p1_projection_forbidden": True,
        "official_reproduction_evidence": False,
        "scientific_metrics_exported": [],
        "data_archives_downloaded_or_used": [],
        "authority": {
            "provider": False,
            "scientific_execution": False,
            "p1": False,
            "official_training": False,
        },
    }
    atomic_json(summary_path, summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--source-repo", required=True, type=Path)
    parser.add_argument("--asset-dir", required=True, type=Path)
    parser.add_argument("--construct-artifact", required=True, type=Path)
    parser.add_argument("--case-count", type=int, default=5)
    args = parser.parse_args()
    summary = run(args)
    print(
        json.dumps(
            {
                "run_id": summary["run_id"],
                "verdict": summary["verdict"],
                "case_count": summary["case_count"],
                "invocation_count": len(summary["invocations"]),
                "components": summary["components"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
