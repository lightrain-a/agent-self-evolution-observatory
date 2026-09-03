"""Zero-outcome host-migration equivalence gate for B1 R45-M1.

Uses fixed prompts, synthetic memories, and OSInteraction train unit 0 only.
No validation unit is initialized or evaluated.
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
PINNED = "c1b322ca43de36ddf64c6712f89d0095bfc35ce0"
TRAIN_SHA = "d33513493856e6cdce2377a951a48a42686463eee1c92acb9d6b0a0320601e62"
TRAIN_INSTRUCTION_SHA = "8fc812b7186dc37112abd0ada02236e9bf78c513ba07856caf3610fa110b287c"
LLM = "B1-Qwen2.5-7B-Instruct-r43"
EMBED = "B1-all-mpnet-base-v2-isometric3072-r43"
KEY = "local-b1-r43"
BASE_URL = "http://127.0.0.1:18143/v1"
IMAGE = "b1-memrl-r45m1-osinteraction:20260901"
SOURCE = pathlib.Path("/data/wyt/b1-memrl-r45m1-source-c1b322ca")
QWEN = pathlib.Path("/data/lry/models/Qwen2.5-7B-Instruct")
REPEATS = 3


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def file_sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def norm(vector: list[float]) -> float:
    return math.sqrt(sum(float(x) ** 2 for x in vector))


def cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b)) / (norm(a) * norm(b))


def embedding_evidence(vectors: list[list[float]]) -> dict[str, Any]:
    if not vectors or any(len(row) != 3072 for row in vectors):
        raise RuntimeError("Q2-dimension")
    norms = [norm(row) for row in vectors]
    if any(abs(value - 1.0) >= 1e-3 for value in norms):
        raise RuntimeError(f"Q2-norm:{norms}")
    native: list[list[float]] = []
    for row in vectors:
        chunks = [row[i:i + 768] for i in range(0, 3072, 768)]
        if any(chunk != chunks[0] for chunk in chunks[1:]):
            raise RuntimeError("Q2-repeat-bridge")
        native.append([x * 2.0 for x in chunks[0]])
    errors = []
    cosines = []
    for i in range(len(vectors)):
        for j in range(i + 1, len(vectors)):
            expanded = cosine(vectors[i], vectors[j])
            base = cosine(native[i], native[j])
            cosines.append(expanded)
            errors.append(abs(expanded - base))
    if any(error >= 1e-12 for error in errors):
        raise RuntimeError(f"Q2-cosine-bridge:{errors}")
    return {
        "vectors_sha256": digest(vectors), "norms": norms,
        "pairwise_cosines_sha256": digest(cosines),
        "max_cosine_bridge_error": max(errors, default=0.0),
    }


def ids(rows: list[dict[str, Any]]) -> list[str]:
    result = [str(row.get("memory_id") or "") for row in rows]
    if not result or any(not value for value in result):
        raise RuntimeError("Q3-missing-id")
    return result


def mos_config(outdir: pathlib.Path, base_url: str) -> dict[str, Any]:
    model = {"backend": "openai", "config": {
        "model_name_or_path": LLM, "api_key": KEY, "api_base": base_url}}
    return {
        "chat_model": model,
        "mem_reader": {"backend": "simple_struct", "config": {
            "llm": model,
            "embedder": {"backend": "universal_api", "config": {
                "provider": "openai", "model_name_or_path": EMBED,
                "api_key": KEY, "base_url": base_url}},
            "chunker": {"backend": "sentence", "config": {
                "tokenizer_or_token_counter": "character", "chunk_size": 500,
                "chunk_overlap": 128, "min_sentences_per_chunk": 1}}}},
        "user_manager": {"backend": "sqlite", "config": {
            "db_path": str(outdir / "users.db")}}, "top_k": 5,
    }


def memory_service(config_path: pathlib.Path, base_url: str):
    from memrl.providers.embedding import OpenAIEmbedder
    from memrl.providers.llm import OpenAILLM
    from memrl.service.memory_service import MemoryService
    from memrl.service.strategies import BuildStrategy, RetrieveStrategy, StrategyConfiguration, UpdateStrategy
    from memrl.service.value_driven import RLConfig
    return MemoryService(
        mos_config_path=str(config_path),
        llm_provider=OpenAILLM(api_key=KEY, base_url=base_url, model=LLM,
                              default_temperature=0.0, default_max_tokens=512,
                              provider="openai"),
        embedding_provider=OpenAIEmbedder(api_key=KEY, base_url=base_url,
                                          model=EMBED, provider="openai"),
        strategy_config=StrategyConfiguration(BuildStrategy.PROCEDURALIZATION,
            RetrieveStrategy.QUERY, UpdateStrategy.ADJUSTMENT),
        user_id="b1_r45m1_equivalence_support", num_workers=1,
        db_max_concurrency=1, max_keywords=8, memory_confidence=100.0,
        add_similarity_threshold=0.99, enable_value_driven=True,
        rl_config=RLConfig(epsilon=0.01, tau=0.35, alpha=0.3, gamma=0.0,
            q_init_pos=0.5, q_init_neg=0.5, success_reward=1.0,
            failure_reward=0.0, sim_threshold=0.50, topk=5,
            novelty_threshold=0.85, weight_sim=0.5, weight_q=0.5),
        use_z_score_normalization=True, dedup_by_task_id=False,
        sim_norm_mean=0.39, sim_norm_std=0.14)


def q1(client: Any, qwen: pathlib.Path, parse: Any) -> dict[str, Any]:
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(str(qwen), local_files_only=True,
                                               trust_remote_code=False)
    prompt = ("Return one OSInteraction action that creates /tmp/b1_q1_replay. "
              "Use exactly Act: bash with one fenced bash block. Do not add prose.")
    rows = []
    for _ in range(REPEATS):
        reply = client.chat.completions.create(model=LLM,
            messages=[{"role": "user", "content": prompt}], temperature=0,
            max_tokens=64).choices[0].message.content or ""
        parsed = parse(reply)
        rows.append({"text": reply,
                     "tokens": tokenizer.encode(reply, add_special_tokens=False),
                     "action": str(parsed.action), "content": parsed.content})
    if any(row != rows[0] for row in rows[1:]) or rows[0]["action"] != "execute" or not rows[0]["content"]:
        raise RuntimeError(f"Q1-replay:{rows}")
    return {"pass": True, "repetitions": REPEATS,
            "token_sequence_stable": True, "executable_action_parse_stable": True,
            "response_sha256": hashlib.sha256(rows[0]["text"].encode()).hexdigest(),
            "token_ids_sha256": digest(rows[0]["tokens"]),
            "parsed_content_sha256": hashlib.sha256(rows[0]["content"].encode()).hexdigest()}


def q2(client: Any) -> dict[str, Any]:
    strings = ["create a directory and verify it exists",
               "copy a file and check its permissions",
               "count ERROR lines in application logs"]
    evidence = []
    for _ in range(REPEATS):
        reply = client.embeddings.create(model=EMBED, input=strings)
        evidence.append(embedding_evidence([list(map(float, row.embedding)) for row in reply.data]))
    if any(row["vectors_sha256"] != evidence[0]["vectors_sha256"] for row in evidence[1:]):
        raise RuntimeError("Q2-repeat-vector-drift")
    return {"pass": True, "repetitions": REPEATS,
            "repeated_vectors_stable": True, "dimension": 3072,
            "native_dimension": 768, **evidence[0]}


def q3(service: Any) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    bank = [
        ("Create a directory named /tmp/b1_migration_q5 and verify it exists.",
         "Run mkdir -p /tmp/b1_migration_q5, write SUPPORT_OK to /tmp/b1_migration_q5/result.txt, then test both.", True, "directory"),
        ("Count ERROR lines in synthetic logs.",
         "Use grep to select ERROR lines and wc -l to count them.", False, "logs"),
        ("Copy a synthetic file and set permissions.",
         "Use cp followed by chmod 644 and test -f.", True, "copy")]
    built = []
    for task, trajectory, success, task_id in bank:
        memory_id = service.build_memory(task, trajectory, metadata={
            "source_benchmark": "synthetic_support_only", "success": success,
            "task_id": task_id})
        if not memory_id:
            raise RuntimeError(f"Q3-build:{task_id}")
        built.append(str(memory_id))
    query = bank[0][0]
    repeats = [service.retrieve(query, k=3, threshold=0.0) for _ in range(REPEATS)]
    orders = [ids(rows) for rows in repeats]
    if any(order != orders[0] for order in orders[1:]) or not set(orders[0]) <= set(built):
        raise RuntimeError(f"Q3-order:{orders}")
    return ({"pass": True, "repetitions": REPEATS,
             "synthetic_memory_count": 3, "retrieval_order_stable": True,
             "built_ids_sha256": digest(built), "retrieved_ids_sha256": digest(orders[0])},
            repeats[0])


def cmd(raw: dict[str, Any]):
    from src.tasks.instance.os_interaction.utility import CommandItem
    return CommandItem.model_validate(raw)


def q4(source: pathlib.Path, image: str) -> dict[str, Any]:
    from src.tasks.instance.os_interaction.container import OSInteractionContainer
    train_path = source / "data/llb/os_interaction_train.json"
    if file_sha(train_path) != TRAIN_SHA:
        raise RuntimeError("Q4-train-drift")
    unit = json.loads(train_path.read_text())["0"]
    if hashlib.sha256(unit["instruction"].encode()).hexdigest() != TRAIN_INSTRUCTION_SHA:
        raise RuntimeError("Q4-unit-drift")
    init = cmd(unit["initialization_command_item"])
    evaluate = cmd(unit["evaluation_info"]["evaluation_command_item"])
    truth = cmd(unit["evaluation_info"]["ground_truth_command_item"])
    rows = []
    for _ in range(REPEATS):
        box = OSInteractionContainer(10, image=image)
        try:
            a = box.execute_independent(init.model_copy(deep=True))
            b = box.execute_independent(evaluate.model_copy(deep=True))
            c = box.execute_independent(truth.model_copy(deep=True))
            d = box.execute_independent(evaluate.model_copy(deep=True))
            e = box.execute_independent(evaluate.model_copy(deep=True))
            rows.append([a.exit_code, a.timeout_flag, b.exit_code, b.timeout_flag,
                         c.exit_code, c.timeout_flag, d.exit_code, d.timeout_flag,
                         e.exit_code, e.timeout_flag])
        finally:
            box.terminate()
    expected = [0, False, 1, False, 0, False, 0, False, 0, False]
    if any(row != expected for row in rows):
        raise RuntimeError(f"Q4-replay:{rows}")
    return {"pass": True, "repetitions": REPEATS, "unit_id": "0",
            "split": "data/llb/os_interaction_train.json", "split_sha256": TRAIN_SHA,
            "evaluator_verdict_stable": True, "reset_reproducible": True,
            "validation_split_used": False, "expected_replay": expected}


def q5(client: Any, service: Any, parse: Any, image: str) -> dict[str, Any]:
    from src.tasks.instance.os_interaction.container import OSInteractionContainer
    query = "Create a directory named /tmp/b1_migration_q5 and verify it exists."
    rows = []
    for _ in range(REPEATS):
        retrieved = service.retrieve(query, k=3, threshold=0.0)
        context = json.dumps([{"memory_id": str(r.get("memory_id") or ""),
                               "memory": r.get("memory"), "content": r.get("content")}
                              for r in retrieved], ensure_ascii=False, sort_keys=True)
        prompt = ("Use this retrieved synthetic support memory to perform the instruction. "
                  "Return exactly one Act: bash fenced bash action, with no prose. "
                  "Create /tmp/b1_migration_q5, write SUPPORT_OK to result.txt, and verify it.\n"
                  f"Instruction: {query}\nMemory: {context}")
        text = client.chat.completions.create(model=LLM,
            messages=[{"role": "user", "content": prompt}], temperature=0,
            max_tokens=128).choices[0].message.content or ""
        parsed = parse(text)
        if str(parsed.action) != "execute" or not parsed.content:
            raise RuntimeError(f"Q5-parse:{text!r}")
        box = OSInteractionContainer(10, image=image)
        try:
            action = box.execute_independent(cmd({"command_name": "bash", "script": parsed.content}))
            verdict = box.execute_independent(cmd({"command_name": "bash", "script":
                "test -d /tmp/b1_migration_q5 && test \"$(cat /tmp/b1_migration_q5/result.txt)\" = SUPPORT_OK"}))
        finally:
            box.terminate()
        rows.append({"retrieval_sha256": digest(ids(retrieved)),
                     "response_sha256": hashlib.sha256(text.encode()).hexdigest(),
                     "action_sha256": hashlib.sha256(parsed.content.encode()).hexdigest(),
                     "action_exit": action.exit_code, "action_timeout": action.timeout_flag,
                     "verdict_exit": verdict.exit_code, "verdict_timeout": verdict.timeout_flag})
    if any(row != rows[0] for row in rows[1:]) or any(
            row["action_exit"] != 0 or row["action_timeout"] or
            row["verdict_exit"] != 0 or row["verdict_timeout"] for row in rows):
        raise RuntimeError(f"Q5-chain:{rows}")
    return {"pass": True, "repetitions": REPEATS,
            "chain": ["query", "embedding", "retrieval", "Qwen", "action", "environment"],
            "full_chain_stable": True, "fresh_environment_each_repetition": True,
            "validation_unit_used": False, "row": rows[0]}


def receipt(script: pathlib.Path, source: pathlib.Path, image: str, base_url: str,
            gates: dict[str, Any], wall: float) -> dict[str, Any]:
    import docker
    payload = {
        "schema_version": "1.0", "paper_id": PAPER_ID,
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-R45M1-HOST-MIGRATION-EQUIVALENCE",
        "recorded_date": "2026-09-01", "status": "PASS",
        "role": "ZERO_CONFIRMATORY_OUTCOME_INFRASTRUCTURE_EQUIVALENCE_QUALIFICATION",
        "host": {"logical_name": "ubuntu", "ssh_identity": "wyt@222.20.126.231"},
        "source": {"root": str(source), "revision": PINNED, "train_split_sha256": TRAIN_SHA},
        "script": {"path": str(script), "sha256": file_sha(script)},
        "loopback": {"base_url": base_url, "network_scope": "loopback-only",
                     "llm_model": LLM, "embedding_model": EMBED, "external_provider_calls": 0},
        "runtime_image": {"tag": image, "id": docker.from_env().images.get(image).id},
        "qualification": gates, "all_q1_q5_pass": all(row.get("pass") is True for row in gates.values()),
        "access_accounting": {"training_support_units_initialized": REPEATS,
            "training_support_evaluator_calls": REPEATS * 3,
            "training_support_ground_truth_calls": REPEATS,
            "synthetic_memory_builds": 3, "synthetic_retrieval_calls": REPEATS * 2,
            "validation_units_initialized": 0, "validation_evaluator_calls": 0,
            "validation_ground_truth_calls": 0, "confirmatory_treatment_outcomes_observed": 0,
            "external_provider_calls": 0},
        "scientific_authority": False, "experiment_authority": False,
        "support_only": True, "failure_route": "HOLD_HOST_MIGRATION_EQUIVALENCE_FAILED",
        "wall_seconds": wall}
    if not payload["all_q1_q5_pass"]:
        raise RuntimeError("not-all-pass")
    payload["receipt_sha256"] = digest({k: v for k, v in payload.items() if k != "receipt_sha256"})
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=pathlib.Path, required=True)
    parser.add_argument("--source-root", type=pathlib.Path, default=SOURCE)
    parser.add_argument("--qwen-root", type=pathlib.Path, default=QWEN)
    parser.add_argument("--image", default=IMAGE)
    parser.add_argument("--base-url", default=BASE_URL)
    parser.add_argument("--script-copy", type=pathlib.Path)
    args = parser.parse_args()
    outdir = args.output_dir.resolve()
    if outdir.exists() and any(outdir.iterdir()):
        raise SystemExit("qualification-output-dir-must-be-empty")
    outdir.mkdir(parents=True, exist_ok=True)
    os.chdir(outdir)  # MemoryOS creates .memos relative to cwd; cwd must be writable.
    source = args.source_root.resolve()
    script = args.script_copy.resolve() if args.script_copy else pathlib.Path(__file__).resolve()
    if not args.base_url.startswith("http://127.0.0.1:"):
        raise SystemExit("loopback-required")
    if file_sha(source / "data/llb/os_interaction_train.json") != TRAIN_SHA:
        raise SystemExit("train-drift")
    from openai import OpenAI
    from src.tasks.instance.os_interaction.task import OSInteraction
    client = OpenAI(api_key=KEY, base_url=args.base_url, timeout=180, max_retries=0)
    start = time.time()
    gates = {"Q1": q1(client, args.qwen_root.resolve(), OSInteraction._parse_agent_response),
             "Q2": q2(client)}
    config_path = outdir / "mos_config.json"
    config_path.write_text(json.dumps(mos_config(outdir, args.base_url), indent=2) + "\n")
    service = memory_service(config_path, args.base_url)
    gates["Q3"], _ = q3(service)
    gates["Q4"] = q4(source, args.image)
    gates["Q5"] = q5(client, service, OSInteraction._parse_agent_response, args.image)
    result = receipt(script, source, args.image, args.base_url, gates, time.time() - start)
    (outdir / "host-migration-equivalence.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
