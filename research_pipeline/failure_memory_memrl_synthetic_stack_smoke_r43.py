"""Zero-benchmark-outcome synthetic stack smoke for B1 MemRL R43.

This script never reads LifelongAgentBench train/validation data. It only checks
that the frozen loopback OpenAI-compatible providers, MemoryOS, local Qdrant,
and pinned MemRL MemoryService can build/retrieve one synthetic memory and save
one synthetic checkpoint. It must run outside the pinned MemRL checkout.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import pathlib
import time
from typing import Any

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
PINNED_MEMRL = "c1b322ca43de36ddf64c6712f89d0095bfc35ce0"
BASE_URL = "http://127.0.0.1:18143/v1"
API_KEY = "local-b1-r43"
LLM_MODEL = "B1-Qwen2.5-7B-Instruct-r43"
EMBED_MODEL = "B1-all-mpnet-base-v2-isometric3072-r43"


def _sha_text(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _sha_file(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=pathlib.Path, required=True)
    parser.add_argument("--script-copy", type=pathlib.Path)
    args = parser.parse_args()
    outdir = args.output_dir.resolve()
    script_path = args.script_copy.resolve() if args.script_copy else pathlib.Path(__file__).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    os.chdir(outdir)

    from openai import OpenAI

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL, timeout=120, max_retries=0)
    start = time.time()
    t0 = time.time()
    chat = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": "Reply exactly B1_STACK_OK"}],
        temperature=0,
        max_tokens=16,
    )
    chat_seconds = time.time() - t0
    chat_text = chat.choices[0].message.content or ""
    if chat_text.strip() != "B1_STACK_OK":
        raise RuntimeError(f"loopback-chat-nondeterministic:{chat_text!r}")

    t0 = time.time()
    embedding = client.embeddings.create(model=EMBED_MODEL, input=["alpha beta", "alpha gamma"])
    embedding_seconds = time.time() - t0
    vectors = [row.embedding for row in embedding.data]
    if len(vectors) != 2 or any(len(v) != 3072 for v in vectors):
        raise RuntimeError("loopback-embedding-dimension-drift")
    norms = [math.sqrt(sum(float(x) * float(x) for x in v)) for v in vectors]
    if any(abs(value - 1.0) >= 1e-3 for value in norms):
        raise RuntimeError(f"loopback-embedding-norm-drift:{norms}")

    # Exact MemOS routing shape used by the pinned run/run_llb.py, with one
    # deliberate runtime freeze: the chunker uses Chonkie's deterministic
    # character tokenizer rather than its network-dependent gpt2 default.
    mos = {
        "chat_model": {
            "backend": "openai",
            "config": {"model_name_or_path": LLM_MODEL, "api_key": API_KEY, "api_base": BASE_URL},
        },
        "mem_reader": {
            "backend": "simple_struct",
            "config": {
                "llm": {
                    "backend": "openai",
                    "config": {"model_name_or_path": LLM_MODEL, "api_key": API_KEY, "api_base": BASE_URL},
                },
                "embedder": {
                    "backend": "universal_api",
                    "config": {
                        "provider": "openai",
                        "model_name_or_path": EMBED_MODEL,
                        "api_key": API_KEY,
                        "base_url": BASE_URL,
                    },
                },
                "chunker": {
                    "backend": "sentence",
                    "config": {
                        "tokenizer_or_token_counter": "character",
                        "chunk_size": 500,
                        "chunk_overlap": 128,
                        "min_sentences_per_chunk": 1,
                    },
                },
            },
        },
        "user_manager": {"backend": "sqlite", "config": {"db_path": str(outdir / "users.db")}},
        "top_k": 5,
    }
    mos_path = outdir / "mos_config.json"
    mos_path.write_text(json.dumps(mos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    from memrl.providers.embedding import OpenAIEmbedder
    from memrl.providers.llm import OpenAILLM
    from memrl.service.memory_service import MemoryService
    from memrl.service.strategies import BuildStrategy, RetrieveStrategy, StrategyConfiguration, UpdateStrategy
    from memrl.service.value_driven import RLConfig

    llm = OpenAILLM(
        api_key=API_KEY,
        base_url=BASE_URL,
        model=LLM_MODEL,
        default_temperature=0.0,
        default_max_tokens=512,
        provider="openai",
    )
    embedder = OpenAIEmbedder(
        api_key=API_KEY,
        base_url=BASE_URL,
        model=EMBED_MODEL,
        provider="openai",
    )
    rl = RLConfig(
        epsilon=0.01,
        tau=0.35,
        alpha=0.3,
        gamma=0.0,
        q_init_pos=0.5,
        q_init_neg=0.5,
        success_reward=1.0,
        failure_reward=0.0,
        sim_threshold=0.50,
        topk=5,
        novelty_threshold=0.85,
        weight_sim=0.5,
        weight_q=0.5,
    )

    t0 = time.time()
    service = MemoryService(
        mos_config_path=str(mos_path),
        llm_provider=llm,
        embedding_provider=embedder,
        strategy_config=StrategyConfiguration(
            BuildStrategy.PROCEDURALIZATION,
            RetrieveStrategy.QUERY,
            UpdateStrategy.ADJUSTMENT,
        ),
        user_id="b1_r43_synthetic",
        num_workers=1,
        db_max_concurrency=1,
        max_keywords=8,
        memory_confidence=100.0,
        add_similarity_threshold=0.99,
        enable_value_driven=True,
        rl_config=rl,
        use_z_score_normalization=True,
        dedup_by_task_id=False,
        sim_norm_mean=0.39,
        sim_norm_std=0.14,
    )
    memory_service_init_seconds = time.time() - t0

    synthetic_task = "Create a directory named /tmp/b1_r43_synthetic and verify it exists."
    synthetic_trajectory = (
        "Step 1: mkdir -p /tmp/b1_r43_synthetic\n"
        "Step 2: test -d /tmp/b1_r43_synthetic\n"
        "Result: synthetic support trace completed."
    )
    t0 = time.time()
    memory_id = service.build_memory(
        synthetic_task,
        synthetic_trajectory,
        metadata={
            "source_benchmark": "synthetic_support_only",
            "success": True,
            "task_id": "synthetic-r43",
        },
    )
    build_seconds = time.time() - t0
    if not memory_id:
        raise RuntimeError("synthetic-memory-not-built")

    t0 = time.time()
    retrieved = service.retrieve(synthetic_task, k=3, threshold=0.0)
    retrieve_seconds = time.time() - t0
    if not retrieved or not any(str(row.get("memory_id")) == str(memory_id) for row in retrieved):
        raise RuntimeError("synthetic-memory-not-retrieved")

    checkpoint_dir = outdir / "checkpoint"
    checkpoint = service.save_checkpoint_snapshot(str(checkpoint_dir), ckpt_id="synthetic")
    receipt: dict[str, Any] = {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-R43-SYNTHETIC-STACK-SMOKE",
        "recorded_date": "2026-08-29",
        "role": "ZERO_BENCHMARK_OUTCOME_MEMRL_MEMOS_LOOPBACK_STACK_SMOKE",
        "host": "workstation3090",
        "script": {"path": str(script_path), "sha256": _sha_file(script_path)},
        "loopback": {
            "base_url": BASE_URL,
            "llm_model": LLM_MODEL,
            "embedding_model": EMBED_MODEL,
            "chat_exact": True,
            "chat_seconds": chat_seconds,
            "embedding_seconds": embedding_seconds,
            "embedding_dimensions": [len(v) for v in vectors],
            "embedding_norms": norms,
        },
        "memory_service": {
            "init_seconds": memory_service_init_seconds,
            "build_seconds": build_seconds,
            "retrieve_seconds": retrieve_seconds,
            "memory_id_sha256": _sha_text(str(memory_id)),
            "retrieved_count": len(retrieved),
            "built_memory_retrieved": True,
            "checkpoint_visible_memories": checkpoint.get("visible_memories"),
            "checkpoint_textual_memory_md5": checkpoint.get("textual_memory_md5"),
        },
        "runtime_freezes": {
            "chunker_backend": "sentence",
            "chunker_tokenizer_or_token_counter": "character",
            "chunk_size": 500,
            "chunk_overlap": 128,
            "embedding_runtime_dimension": 3072,
            "loopback_only": True,
        },
        "config_sha256": _sha_file(mos_path),
        "pinned_memrl_revision": PINNED_MEMRL,
        "access_accounting": {
            "llb_train_tasks_initialized": 0,
            "llb_validation_tasks_initialized": 0,
            "llb_evaluator_calls": 0,
            "llb_ground_truth_calls": 0,
            "confirmatory_outcomes_observed": 0,
            "external_provider_calls": 0,
        },
        "scientific_authority": False,
        "experiment_authority": False,
        "support_only": True,
        "wall_seconds": time.time() - start,
    }
    receipt["receipt_sha256"] = _digest({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    output = outdir / "synthetic-stack-smoke.json"
    output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
