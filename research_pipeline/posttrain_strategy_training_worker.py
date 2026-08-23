from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

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


def main() -> int:
    parser = argparse.ArgumentParser(description="One-step zero-API engineering training worker")
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--learning-rate", type=float, required=True)
    parser.add_argument("--max-tokens", type=int, default=48)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not (0.0 < args.learning_rate <= 0.01):
        raise ValueError("engineering learning rate must be in (0, 0.01]")
    if not (8 <= args.max_tokens <= 128):
        raise ValueError("engineering max_tokens must be in [8, 128]")

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable")
    torch.manual_seed(0)
    started = time.time()
    model_path = args.model_path.resolve()
    tokenizer = AutoTokenizer.from_pretrained(str(model_path), local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        str(model_path), local_files_only=True, torch_dtype=torch.bfloat16
    ).cuda().train()
    ids = tokenizer(
        "A zero API engineering update verifies the orchestrator training boundary on the local base model.",
        return_tensors="pt",
    ).input_ids.cuda()[:, : args.max_tokens]

    probes = []
    for name, parameter in model.named_parameters():
        if parameter.requires_grad and parameter.ndim >= 2:
            probes.append((name, parameter, parameter.detach().view(-1)[:4096].clone()))
            if len(probes) >= 6:
                break
    if not probes:
        raise RuntimeError("no trainable matrix probes found")

    optimizer = torch.optim.SGD(model.parameters(), lr=args.learning_rate)
    output = model(input_ids=ids, labels=ids)
    loss = float(output.loss.detach().float().cpu())
    output.loss.backward()
    grad_nonzero = any(
        parameter.grad is not None and bool(torch.any(parameter.grad != 0).item())
        for _, parameter, _ in probes
    )
    optimizer.step()

    changed = 0
    max_abs_delta = 0.0
    for _name, parameter, before in probes:
        after = parameter.detach().view(-1)[:4096]
        changed += int(torch.count_nonzero(after != before).cpu())
        delta = (after.float() - before.float()).abs()
        max_abs_delta = max(max_abs_delta, float(delta.max().cpu()))

    receipt = {
        "artifact_kind": "V19R003_ENGINEERING_TRAINING_WORKER_RECEIPT",
        "scientific_use_forbidden": True,
        "training_semantics": "ONE_STEP_SGD_ENGINEERING_SURROGATE_NOT_SFT_OR_RL",
        "external_api_calls": 0,
        "deepseek_calls": 0,
        "model_path": str(model_path),
        "device": torch.cuda.get_device_name(0),
        "dtype": "bfloat16",
        "learning_rate": args.learning_rate,
        "tokens": int(ids.numel()),
        "loss": loss,
        "gradient_nonzero": grad_nonzero,
        "changed_probe_elements": changed,
        "max_abs_delta": max_abs_delta,
        "parameter_update_verified": bool(grad_nonzero and changed > 0),
        "elapsed_sec": round(time.time() - started, 3),
        "peak_gpu_allocated_gib": round(torch.cuda.max_memory_allocated() / 1024**3, 3),
        "checkpoint_persisted": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt["parameter_update_verified"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
