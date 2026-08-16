from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import platform


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def run(model: pathlib.Path) -> dict:
    import torch
    import transformers
    import vllm
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams

    model = model.resolve()
    tokenizer = AutoTokenizer.from_pretrained(model, trust_remote_code=True)
    prompt = "Reply with exactly: OK"
    rendered = tokenizer.apply_chat_template(
        [{"role": "user", "content": prompt}], tokenize=False, add_generation_prompt=True
    )
    llm = LLM(
        model=str(model),
        tokenizer=str(model),
        tensor_parallel_size=1,
        gpu_memory_utilization=0.90,
        max_model_len=1024,
        trust_remote_code=True,
        enable_prefix_caching=False,
        enforce_eager=True,
    )
    out = llm.generate(
        [rendered], SamplingParams(temperature=0.0, max_tokens=8), use_tqdm=False
    )[0].outputs[0].text.strip()
    if not out:
        raise RuntimeError("vllm-smoke-empty")
    return {
        "schema_version": "1.0",
        "artifact_kind": "pre-outcome-vllm-smoke-receipt",
        "model_dir": str(model),
        "passed": True,
        "prompt_sha256": sha_text(prompt),
        "rendered_prompt_sha256": sha_text(rendered),
        "response_sha256": sha_text(out),
        "response_nonempty": True,
        "runtime": {
            "python": platform.python_version(),
            "torch": torch.__version__,
            "transformers": transformers.__version__,
            "vllm": vllm.__version__,
        },
        "environment_outcomes_read": False,
        "scientific_authority": False,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", type=pathlib.Path, required=True)
    ap.add_argument("--output", type=pathlib.Path, required=True)
    a = ap.parse_args()
    payload = run(a.model)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    tmp = a.output.with_suffix(a.output.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(a.output)
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
