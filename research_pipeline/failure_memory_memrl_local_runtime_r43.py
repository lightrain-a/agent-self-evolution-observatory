"""Frozen local providers for the B1 MemRL confirmatory program.

This module is deliberately external to the pinned MemRL checkout.  The MemRL
source revision remains byte-clean; the experiment injects duck-typed provider
objects through the public MemoryService/LLBRunner interfaces.

No benchmark task is executed merely by importing this module.
"""
from __future__ import annotations

import re
import threading
from pathlib import Path
from typing import Any

LLM_ROOT = Path("/home/hdd/yutong/agent_p0_runtime/models/Qwen2.5-7B-Instruct")
EMBED_ROOT = Path("/home/hdd/yutong/models/models--sentence-transformers--all-mpnet-base-v2/snapshots/e8c3b32edf5434bc2275fc9bab85f82640a19130")
LLM_MANIFEST_SHA256 = "c7e4242ce0f2ebd0700ce3c0ff8e24044a2dddc29f68ef8358993f66e60c153c"
EMBED_MANIFEST_SHA256 = "ddd2853514c3aadf62ae9efd1751aac4ea3a7b8414b0da654b45f6915894a9e0"


class LocalQwenProvider:
    """Deterministic Qwen2.5-7B-Instruct provider with the MemRL BaseLLM surface."""

    def __init__(self, model_root: Path = LLM_ROOT, device: str = "cuda:0", max_new_tokens: int = 512) -> None:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.model_root = Path(model_root)
        self.device = device
        self.default_temperature = 0.0
        self.default_max_tokens = int(max_new_tokens)
        self._lock = threading.Lock()
        self._usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        self.tokenizer = AutoTokenizer.from_pretrained(str(self.model_root), local_files_only=True, trust_remote_code=False)
        self.model = AutoModelForCausalLM.from_pretrained(
            str(self.model_root),
            local_files_only=True,
            trust_remote_code=False,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
        ).to(self.device)
        self.model.eval()

    def generate(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        import torch

        temperature = float(kwargs.get("temperature", self.default_temperature) or 0.0)
        max_new_tokens = int(kwargs.get("max_tokens", kwargs.get("max_completion_tokens", self.default_max_tokens)) or self.default_max_tokens)
        max_new_tokens = max(1, min(max_new_tokens, self.default_max_tokens))
        with self._lock, torch.inference_mode():
            text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            batch = self.tokenizer(text, return_tensors="pt").to(self.device)
            prompt_tokens = int(batch["input_ids"].shape[-1])
            do_sample = temperature > 0
            generation_kwargs = {
                "max_new_tokens": max_new_tokens,
                "do_sample": do_sample,
                "pad_token_id": self.tokenizer.eos_token_id,
                "eos_token_id": self.tokenizer.eos_token_id,
            }
            if do_sample:
                generation_kwargs["temperature"] = temperature
            generated = self.model.generate(**batch, **generation_kwargs)
            new_ids = generated[0, prompt_tokens:]
            completion_tokens = int(new_ids.shape[-1])
            self._usage["prompt_tokens"] += prompt_tokens
            self._usage["completion_tokens"] += completion_tokens
            self._usage["total_tokens"] += prompt_tokens + completion_tokens
            return self.tokenizer.decode(new_ids, skip_special_tokens=True).strip()

    def extract_keywords(self, text: str, max_keywords: int = 8) -> list[str]:
        # The frozen B1 runtime uses MemRL retrieve_strategy=query, so this method
        # is only an interface-completeness fallback and never drives the primary run.
        seen: set[str] = set()
        out: list[str] = []
        for token in re.findall(r"[A-Za-z0-9_./-]{3,}", text.lower()):
            if token in seen:
                continue
            seen.add(token)
            out.append(token)
            if len(out) >= max_keywords:
                break
        return out

    def generate_script(self, trajectory: str) -> str:
        prompt = (
            "Convert the following OSInteraction trajectory into a concise actionable procedure. "
            "Preserve commands, preconditions, and failure-relevant details; do not infer success beyond the trajectory.\n\n"
            + trajectory
        )
        return self.generate([{"role": "user", "content": prompt}], temperature=0.0, max_tokens=384)

    def get_token_usage(self) -> dict[str, int]:
        return dict(self._usage)


class LocalMPNetEmbedder:
    """all-mpnet-base-v2 mean-pooling + L2-normalization without sentence-transformers."""

    def __init__(self, model_root: Path = EMBED_ROOT, device: str = "cuda:1", max_text_len: int = 8196, output_dimension: int = 3072) -> None:
        import torch
        from transformers import AutoModel, AutoTokenizer

        self.model_root = Path(model_root)
        self.device = device
        self.max_text_len = int(max_text_len)
        self.output_dimension = int(output_dimension)
        self._lock = threading.Lock()
        self._usage = {"input_texts": 0, "input_chars": 0}
        self.tokenizer = AutoTokenizer.from_pretrained(str(self.model_root), local_files_only=True, trust_remote_code=False)
        self.model = AutoModel.from_pretrained(
            str(self.model_root),
            local_files_only=True,
            trust_remote_code=False,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
        ).to(self.device)
        self.model.eval()

    @staticmethod
    def _average(vectors: list[list[float]]) -> list[float]:
        if len(vectors) == 1:
            return vectors[0]
        width = len(vectors[0])
        return [sum(float(v[i]) for v in vectors) / len(vectors) for i in range(width)]

    @staticmethod
    def _isometric_expand(vector: list[float], output_dimension: int) -> list[float]:
        """Repeat a unit vector k times and divide by sqrt(k).

        When output_dimension is an integer multiple of the original dimension,
        this preserves both L2 norm and every pairwise cosine similarity exactly.
        It is used only to satisfy MemRL's source-pinned 3072-dimensional Qdrant
        schema while retaining MPNet's cosine geometry.
        """
        width = len(vector)
        if output_dimension == width:
            return list(vector)
        if width <= 0 or output_dimension <= 0 or output_dimension % width != 0:
            raise ValueError(f"non-isometric embedding dimension bridge:{width}->{output_dimension}")
        repeats = output_dimension // width
        scale = repeats ** -0.5
        return [float(x) * scale for _ in range(repeats) for x in vector]

    def embed(self, texts: list[str]) -> list[list[float]]:
        import torch
        import torch.nn.functional as F

        chunk_size = self.max_text_len if self.max_text_len > 0 else 0
        chunks: list[str] = []
        counts: list[int] = []
        for text in texts:
            parts = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)] if chunk_size and len(text) > chunk_size else [text]
            chunks.extend(parts)
            counts.append(len(parts))
        if not chunks:
            return []
        vectors: list[list[float]] = []
        with self._lock, torch.inference_mode():
            for start in range(0, len(chunks), 32):
                batch_text = chunks[start : start + 32]
                batch = self.tokenizer(batch_text, padding=True, truncation=True, max_length=384, return_tensors="pt").to(self.device)
                out = self.model(**batch).last_hidden_state
                mask = batch["attention_mask"].unsqueeze(-1).expand(out.size()).float()
                pooled = (out * mask).sum(1) / mask.sum(1).clamp(min=1e-9)
                pooled = F.normalize(pooled.float(), p=2, dim=1)
                vectors.extend(self._isometric_expand(v, self.output_dimension) for v in pooled.cpu().tolist())
        merged: list[list[float]] = []
        idx = 0
        for count in counts:
            merged.append(self._average(vectors[idx : idx + count]))
            idx += count
        self._usage["input_texts"] += len(texts)
        self._usage["input_chars"] += sum(len(t) for t in texts)
        return merged

    def embed_single(self, text: str) -> list[float]:
        return self.embed([text])[0]

    def get_token_usage(self) -> dict[str, int]:
        # MemRL only logs this value diagnostically; local embedding has no billed tokens.
        return {"total_tokens": 0, **self._usage}
