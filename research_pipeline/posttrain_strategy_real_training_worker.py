from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import time
from pathlib import Path
from typing import Any

_PROVIDER_KEYS = (
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "CLAUDE_CODE_OAUTH_TOKEN",
    "OPENAI_API_KEY",
    "DEEPSEEK_API_KEY",
    "ARK_API_KEY",
    "VOLCENGINE_API_KEY",
    "GOOGLE_API_KEY",
    "GEMINI_API_KEY",
)
for _key in _PROVIDER_KEYS:
    os.environ.pop(_key, None)
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

_NUMBER_RE = re.compile(r"[-+]?\d+(?:,\d{3})*(?:\.\d+)?")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                row = json.loads(line)
                if not isinstance(row, dict) or not row.get("question") or not row.get("answer"):
                    raise ValueError("training JSONL rows require question and answer")
                rows.append(row)
    if not rows:
        raise ValueError("empty training dataset")
    return rows


def _answer_value(answer: str) -> str | None:
    marker = answer.rsplit("####", 1)[-1] if "####" in answer else answer
    matches = _NUMBER_RE.findall(marker)
    if not matches:
        return None
    return matches[-1].replace(",", "").lstrip("+")


def _generated_value(text: str) -> str | None:
    matches = _NUMBER_RE.findall(text)
    if not matches:
        return None
    return matches[-1].replace(",", "").lstrip("+")


def _reward(text: str, reference_answer: str) -> tuple[float, dict[str, Any]]:
    gold = _answer_value(reference_answer)
    pred = _generated_value(text)
    nonempty = bool(text.strip())
    parseable = pred is not None
    exact = bool(gold is not None and pred == gold)
    value = (0.02 if nonempty else 0.0) + (0.08 if parseable else 0.0) + (1.0 if exact else 0.0)
    return value, {"nonempty": nonempty, "parseable_numeric": parseable, "exact_numeric": exact}


def _probe_parameters(model: Any, count: int = 6) -> list[tuple[str, Any, Any]]:
    probes = []
    for name, parameter in model.named_parameters():
        if parameter.requires_grad and parameter.ndim >= 2:
            probes.append((name, parameter, parameter.detach().view(-1)[:4096].clone()))
            if len(probes) >= count:
                break
    if not probes:
        raise RuntimeError("no trainable matrix probes found")
    return probes


def _probe_delta(probes: list[tuple[str, Any, Any]]) -> dict[str, Any]:
    import torch

    changed = 0
    max_abs_delta = 0.0
    rows = []
    for name, parameter, before in probes:
        after = parameter.detach().view(-1)[:4096]
        delta = (after.float() - before.float()).abs()
        local_changed = int(torch.count_nonzero(after != before).cpu())
        changed += local_changed
        local_max = float(delta.max().cpu())
        max_abs_delta = max(max_abs_delta, local_max)
        rows.append({"name": name, "changed_elements": local_changed, "max_abs_delta": local_max})
    return {"changed_probe_elements": changed, "max_abs_delta": max_abs_delta, "probes": rows}


def _format_prompt(question: str) -> str:
    return "Problem:\n" + question.strip() + "\n\nSolution:\n"


def _sft_step(model: Any, tokenizer: Any, row: dict[str, Any], optimizer: Any, max_seq_tokens: int) -> float:
    import torch

    prompt = _format_prompt(str(row["question"]))
    answer = str(row["answer"]).strip()
    prompt_ids = tokenizer(prompt, add_special_tokens=True, return_tensors="pt").input_ids[0]
    answer_ids = tokenizer(answer, add_special_tokens=False, return_tensors="pt").input_ids[0]
    eos = tokenizer.eos_token_id
    if eos is not None:
        answer_ids = torch.cat([answer_ids, torch.tensor([eos], dtype=answer_ids.dtype)])
    full = torch.cat([prompt_ids, answer_ids])[:max_seq_tokens].unsqueeze(0).cuda()
    labels = full.clone()
    labels[:, : min(prompt_ids.numel(), labels.shape[1])] = -100
    output = model(input_ids=full, labels=labels)
    loss = output.loss
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    optimizer.step()
    return float(loss.detach().float().cpu())


def _rl_step(
    model: Any,
    tokenizer: Any,
    row: dict[str, Any],
    optimizer: Any,
    *,
    max_prompt_tokens: int,
    max_new_tokens: int,
    rollouts: int,
    seed: int,
) -> dict[str, Any]:
    import torch

    prompt = _format_prompt(str(row["question"]))
    encoded = tokenizer(prompt, return_tensors="pt", add_special_tokens=True, truncation=True, max_length=max_prompt_tokens)
    input_ids = encoded.input_ids.cuda()
    attention_mask = encoded.attention_mask.cuda()
    prompt_len = input_ids.shape[1]
    pad_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else tokenizer.eos_token_id
    if pad_id is None:
        pad_id = 0

    rollout_rows = []
    losses = []
    model.eval()
    for rollout_idx in range(rollouts):
        # transformers 4.51 does not accept a per-call ``generator`` kwarg for this model.
        # Reset both RNGs immediately before each rollout to keep the capability probe reproducible.
        torch.manual_seed(seed + rollout_idx)
        torch.cuda.manual_seed_all(seed + rollout_idx)
        with torch.no_grad():
            generated = model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                do_sample=True,
                temperature=0.8,
                top_p=0.95,
                max_new_tokens=max_new_tokens,
                pad_token_id=pad_id,
                eos_token_id=tokenizer.eos_token_id,
            )
        completion = generated[:, prompt_len:]
        if completion.numel() == 0:
            continue
        text = tokenizer.decode(completion[0], skip_special_tokens=True)
        reward, reward_parts = _reward(text, str(row["answer"]))

        model.train()
        full = torch.cat([input_ids, completion], dim=1)
        attn = torch.ones_like(full)
        logits = model(input_ids=full, attention_mask=attn).logits
        shift_logits = logits[:, :-1, :].float()
        shift_targets = full[:, 1:]
        token_logprobs = torch.log_softmax(shift_logits, dim=-1).gather(-1, shift_targets.unsqueeze(-1)).squeeze(-1)
        completion_start = max(prompt_len - 1, 0)
        selected = token_logprobs[:, completion_start:]
        if selected.numel() == 0:
            continue
        policy_loss = -float(reward) * selected.mean()
        losses.append(policy_loss)
        rollout_rows.append(
            {
                "reward": reward,
                "reward_parts": reward_parts,
                "completion_tokens": int(completion.numel()),
                "completion_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            }
        )

    if not losses:
        raise RuntimeError("RL produced no trainable rollout")
    loss = sum(losses) / len(losses)
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    optimizer.step()
    return {
        "loss": float(loss.detach().float().cpu()),
        "rollouts": rollout_rows,
        "mean_reward": sum(r["reward"] for r in rollout_rows) / len(rollout_rows),
        "exact_reward_count": sum(1 for r in rollout_rows if r["reward_parts"]["exact_numeric"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Real zero-API SFT/RL capability worker for V19R-003")
    parser.add_argument("--method", choices=["sft", "rl"], required=True)
    parser.add_argument("--input-model-path", type=Path, required=True)
    parser.add_argument("--output-model-path", type=Path, required=True)
    parser.add_argument("--train-data", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--steps", type=int, default=1)
    parser.add_argument("--examples", type=int, default=2)
    parser.add_argument("--max-seq-tokens", type=int, default=256)
    parser.add_argument("--rl-rollouts", type=int, default=2)
    parser.add_argument("--rl-max-new-tokens", type=int, default=48)
    parser.add_argument("--seed", type=int, default=19003)
    args = parser.parse_args()

    if not (0.0 < args.learning_rate <= 0.01):
        raise ValueError("learning rate must be in (0, 0.01]")
    if not (1 <= args.steps <= 8):
        raise ValueError("capability steps must be in [1, 8]")
    if not (1 <= args.examples <= 16):
        raise ValueError("capability examples must be in [1, 16]")
    if not (64 <= args.max_seq_tokens <= 1024):
        raise ValueError("max_seq_tokens must be in [64, 1024]")
    if not (1 <= args.rl_rollouts <= 4):
        raise ValueError("rl_rollouts must be in [1, 4]")

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable")
    started = time.time()
    random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)

    input_model = args.input_model_path.resolve()
    output_model = args.output_model_path.resolve()
    train_data = args.train_data.resolve()
    rows = _read_jsonl(train_data)
    chosen = rows[: args.examples]
    tokenizer = AutoTokenizer.from_pretrained(str(input_model), local_files_only=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        str(input_model), local_files_only=True, torch_dtype=torch.bfloat16
    ).cuda().train()
    probes = _probe_parameters(model)
    optimizer = torch.optim.SGD(model.parameters(), lr=args.learning_rate)

    step_receipts = []
    for step in range(args.steps):
        row = chosen[step % len(chosen)]
        if args.method == "sft":
            step_receipts.append(
                {
                    "step": step,
                    "source_index": row.get("source_index"),
                    "loss": _sft_step(model, tokenizer, row, optimizer, args.max_seq_tokens),
                }
            )
        else:
            info = _rl_step(
                model,
                tokenizer,
                row,
                optimizer,
                max_prompt_tokens=min(args.max_seq_tokens, 256),
                max_new_tokens=args.rl_max_new_tokens,
                rollouts=args.rl_rollouts,
                seed=args.seed + step * 100,
            )
            step_receipts.append({"step": step, "source_index": row.get("source_index"), **info})

    delta = _probe_delta(probes)
    parameter_update_verified = delta["changed_probe_elements"] > 0
    if not parameter_update_verified:
        raise RuntimeError("real training method completed without observable parameter delta")

    output_model.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(output_model), safe_serialization=True, max_shard_size="4GB")
    tokenizer.save_pretrained(str(output_model))
    config_file = output_model / "config.json"
    if not config_file.is_file():
        raise RuntimeError("persistent checkpoint missing config.json")
    tensor_files = sorted(output_model.glob("*.safetensors"))
    if not tensor_files:
        raise RuntimeError("persistent checkpoint missing safetensors weights")

    receipt = {
        "artifact_kind": "V19R003_REAL_TRAINING_CAPABILITY_RECEIPT",
        "scientific_authority": False,
        "scientific_arm_executed": False,
        "capability_preflight_only": True,
        "method": args.method.upper(),
        "method_semantics": "TOKEN_RESPONSE_SUPERVISED_FINE_TUNING" if args.method == "sft" else "ON_POLICY_SAMPLED_REINFORCE_WITH_SCALAR_MATH_REWARD",
        "input_model_path": str(input_model),
        "output_model_path": str(output_model),
        "train_data_path": str(train_data),
        "train_data_sha256": _sha256(train_data),
        "external_api_calls": 0,
        "deepseek_calls": 0,
        "device": torch.cuda.get_device_name(0),
        "dtype": "bfloat16",
        "learning_rate": args.learning_rate,
        "steps": args.steps,
        "examples_available_to_worker": args.examples,
        "seed": args.seed,
        "step_receipts": step_receipts,
        "parameter_update_verified": parameter_update_verified,
        **delta,
        "checkpoint_persisted": True,
        "checkpoint_config_sha256": _sha256(config_file),
        "checkpoint_tensor_files": [
            {"name": path.name, "bytes": path.stat().st_size, "sha256": _sha256(path)} for path in tensor_files
        ],
        "elapsed_sec": round(time.time() - started, 3),
        "peak_gpu_allocated_gib": round(torch.cuda.max_memory_allocated() / 1024**3, 3),
        "interpretation_boundary": (
            "Capability-only real training. It proves that the frozen local substrate can execute and persist the named "
            "training method without an external API; it is not an autonomous-agent arm and does not support the paper claim."
        ),
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "method": receipt["method"],
        "parameter_update_verified": parameter_update_verified,
        "changed_probe_elements": delta["changed_probe_elements"],
        "checkpoint_files": len(tensor_files),
        "elapsed_sec": receipt["elapsed_sec"],
        "peak_gpu_allocated_gib": receipt["peak_gpu_allocated_gib"],
        "external_api_calls": 0,
        "deepseek_calls": 0,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
