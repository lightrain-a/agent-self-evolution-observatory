from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import random
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch

from research_pipeline.run_scienceworld_base_headroom_q1_shard import replay, rollout
from research_pipeline.scienceworld_qwen_adapter import ScienceWorldQwenPolicy, normalize_action
from research_pipeline.scienceworld_sapd_f0_runtime import attach_lora, base_fingerprint, encode_example, unit_seed


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def atom(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    os.replace(tmp, path)


def tensor_hash(model) -> str:
    h = hashlib.sha256()
    for name, param in sorted(model.named_parameters(), key=lambda x: x[0]):
        if not param.requires_grad:
            continue
        t = param.detach().cpu().contiguous()
        h.update(name.encode())
        h.update(str(tuple(t.shape)).encode())
        h.update(t.view(torch.uint8).numpy().tobytes())
    return h.hexdigest()


def deterministic_seed(seed: int) -> None:
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def examples_from_pairs(pairs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for pair in pairs:
        ex = dict(pair)
        ex["gold_action"] = str(pair["repair_action"])
        out.append(ex)
    return out


def train_and_eval_arm(policy, env, unit: dict[str, Any], pairs: list[dict[str, Any]], update: dict[str, Any], arm: str, outdir: Path, base_fp: str) -> dict[str, Any]:
    uid = unit["unit_id"]
    examples = examples_from_pairs(pairs)
    if len(examples) != int(unit["pair_count"]):
        raise RuntimeError(f"{uid} {arm}: pair count mismatch")

    seed = unit_seed(uid)
    deterministic_seed(seed)
    lora_cfg = {
        "lora": {
            "r": int(update["lora_r"]),
            "alpha": int(update["alpha"]),
            "dropout": float(update["dropout"]),
            "bias": "none",
            "target_modules": list(update["target_modules"]),
            "layers": list(update["layers"]),
        }
    }
    attach_lora(policy, lora_cfg)
    model = policy.model
    initial_adapter_sha256 = tensor_hash(model)
    model.train()
    model.config.use_cache = False
    optimizer = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad],
        lr=float(update["learning_rate"]),
        weight_decay=float(update["weight_decay"]),
    )
    encoded = [encode_example(policy, ex) for ex in examples]
    losses: list[float] = []
    steps = int(update["steps"])
    for step in range(steps):
        batch = encoded[step % len(encoded)]
        optimizer.zero_grad(set_to_none=True)
        loss = model(**batch).loss
        loss.backward()
        optimizer.step()
        losses.append(float(loss.detach().cpu()))
    model.eval()
    model.config.use_cache = True
    final_adapter_sha256 = tensor_hash(model)

    training_eval = []
    exact = 0
    with torch.no_grad():
        for ex in examples:
            pred, raw = policy.choose(
                ex["task_desc"], ex["observation"], ex["inventory"], ex["history"], ex["templates"], ex["objects"]
            )
            ok = normalize_action(pred) == normalize_action(ex["gold_action"])
            exact += int(ok)
            training_eval.append({
                "observation_sha256": ex["observation_sha256"],
                "repair_action": ex["gold_action"],
                "pred_action": pred,
                "exact": ok,
                "raw": raw,
            })

    obs, info, attempts = replay(env, unit)
    if obs is None:
        raise RuntimeError(f"{uid} {arm}: exact initial-state replay failed")
    trace, final_score = rollout(env, policy, obs, info, 50)
    success = int(final_score >= 100)
    supervised = {str(ex["observation_sha256"]) for ex in examples}
    visited = {str(r.get("observation_sha256")) for r in trace}
    overlap = sorted(supervised & visited)
    parser_rejections = sum(
        "no known action matches that input" in str(r.get("next_observation") or "").lower() for r in trace
    )

    adapter_dir = outdir / "adapters" / uid / arm.lower()
    adapter_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(adapter_dir, safe_serialization=True)
    adapter_file = adapter_dir / "adapter_model.safetensors"
    adapter_file_sha256 = sha(adapter_file)

    peft_model = policy.model
    policy.model = peft_model.unload()
    del peft_model
    if hasattr(policy.model, "peft_config"):
        try:
            delattr(policy.model, "peft_config")
        except Exception:
            pass
    torch.cuda.empty_cache()
    rollback_fp = base_fingerprint(policy.model)
    rollback_exact = rollback_fp == base_fp
    if not rollback_exact:
        raise RuntimeError(f"{uid} {arm}: base rollback fingerprint mismatch")

    return {
        "arm": arm,
        "pair_count": len(examples),
        "seed": seed,
        "initial_adapter_sha256": initial_adapter_sha256,
        "final_adapter_sha256": final_adapter_sha256,
        "adapter_file_sha256": adapter_file_sha256,
        "training": {
            "steps": steps,
            "loss_first": losses[0],
            "loss_last": losses[-1],
            "losses": losses,
            "training_top1": exact / len(examples),
            "training_eval": training_eval,
        },
        "source_eval": {
            "replay_attempts": attempts,
            "final_score": final_score,
            "success": success,
            "steps": len(trace),
            "parser_rejections": parser_rejections,
            "supervised_state_overlap_count": len(overlap),
            "supervised_state_overlap": overlap,
            "trace": trace,
        },
        "rollback_exact": rollback_exact,
        "rollback_base_fingerprint": rollback_fp,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", type=Path, required=True)
    ap.add_argument("--shard", type=int, required=True)
    ap.add_argument("--num-shards", type=int, default=3)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--gpu-uuid", required=True)
    ap.add_argument("--model-path", type=Path, default=Path("/home/hdd/qinglinji/models/Qwen2.5-7B-Instruct"))
    args = ap.parse_args()

    if os.environ.get("CUDA_VISIBLE_DEVICES", "") != args.gpu_uuid:
        raise RuntimeError("GPU binding mismatch")
    if args.num_shards != 3:
        raise RuntimeError("frozen execution uses exactly three GPU shards")

    plan = json.loads(args.plan.read_text())
    units = [u for i, u in enumerate(plan["units"]) if i % args.num_shards == args.shard]
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        raise RuntimeError("non-empty output directory")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    lock_path = args.output_dir.parent / (args.output_dir.name + ".lock")
    lock = lock_path.open("a+")
    fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

    deterministic_seed(0)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.use_deterministic_algorithms(True)

    from scienceworld import ScienceWorldEnv

    policy = ScienceWorldQwenPolicy(args.model_path)
    env = ScienceWorldEnv("", envStepLimit=50)
    base_fp = base_fingerprint(policy.model)
    started = time.monotonic()
    rows: list[dict[str, Any]] = []
    atom(args.output_dir / "manifest.json", {
        "schema_version": "1.0",
        "experiment_id": plan["experiment_id"],
        "contract_sha256": plan["contract_sha256"],
        "amendment_sha256": plan["amendment_sha256"],
        "plan_file_sha256": sha(args.plan),
        "plan_hash": plan["plan_hash"],
        "runner_sha256": sha(Path(__file__)),
        "gpu_uuid": args.gpu_uuid,
        "shard": args.shard,
        "num_shards": args.num_shards,
        "unit_ids": [u["unit_id"] for u in units],
        "base_model_fingerprint": base_fp,
        "gold_access_at_training": False,
        "gold_access_at_eval": False,
        "teacher_access_at_training_or_eval": False,
        "batch_experiment_authorized": False,
    })

    try:
        for unit in units:
            obs, info, attempts = replay(env, unit)
            if obs is None:
                raise RuntimeError(f"{unit['unit_id']}: base exact initial-state replay failed")
            base_trace, base_score = rollout(env, policy, obs, info, 50)
            base_success = int(base_score >= 100)
            if base_score != int(unit["frozen_base_final_score"]):
                raise RuntimeError(
                    f"{unit['unit_id']}: frozen BASE mismatch {base_score} != {unit['frozen_base_final_score']}"
                )
            if base_success != int(unit["frozen_base_success"]):
                raise RuntimeError(f"{unit['unit_id']}: frozen BASE success mismatch")

            off = train_and_eval_arm(
                policy, env, unit, unit["offpolicy_pairs"], plan["update_surface"], "OFFPOLICY_SHARED_TEACHER", args.output_dir, base_fp
            )
            on = train_and_eval_arm(
                policy, env, unit, unit["onpolicy_pairs"], plan["update_surface"], "ONPOLICY_SHARED_TEACHER", args.output_dir, base_fp
            )
            same_initialization = off["initial_adapter_sha256"] == on["initial_adapter_sha256"]
            if not same_initialization:
                raise RuntimeError(f"{unit['unit_id']}: OFF/ON LoRA initialization mismatch")

            result = {
                "unit_id": unit["unit_id"],
                "task_family": unit["task_family"],
                "variation": unit["variation"],
                "initial_state_key": unit["initial_state_key"],
                "pair_count": unit["pair_count"],
                "base": {
                    "replay_attempts": attempts,
                    "final_score": base_score,
                    "success": base_success,
                    "steps": len(base_trace),
                    "trace": base_trace,
                },
                "offpolicy": off,
                "onpolicy": on,
                "same_seed": off["seed"] == on["seed"],
                "same_initialization": same_initialization,
                "off_improved_vs_base": off["source_eval"]["final_score"] > base_score,
                "on_improved_vs_base": on["source_eval"]["final_score"] > base_score,
                "on_regressed_vs_base": on["source_eval"]["final_score"] < base_score,
                "on_strictly_better_than_off": on["source_eval"]["final_score"] > off["source_eval"]["final_score"],
                "on_minus_off_score": on["source_eval"]["final_score"] - off["source_eval"]["final_score"],
            }
            rows.append(result)
            atom(args.output_dir / "unit-results.json", rows)
            atom(args.output_dir / "progress.json", {
                "status": "running",
                "completed_units": len(rows),
                "total_units": len(units),
                "current_unit": unit["unit_id"],
                "updated_at": now(),
            })
    finally:
        policy.close()
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        lock.close()

    if len(rows) != len(units):
        raise RuntimeError("incomplete shard")
    atom(args.output_dir / "progress.json", {
        "status": "complete",
        "completed_units": len(rows),
        "total_units": len(units),
        "elapsed_hours": (time.monotonic() - started) / 3600,
        "updated_at": now(),
    })


if __name__ == "__main__":
    main()
