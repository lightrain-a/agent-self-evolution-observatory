from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from research_pipeline.b3_minteval_support import score_factorial_outcome
from research_pipeline.b3_minteval_wiki_support import build_wiki_history_candidates, select_source_disjoint_wiki_candidates


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _norm(value: Any) -> str:
    return "".join(re.findall(r"[A-Za-z0-9]+", str(value or "").casefold()))


def _parse_answer(text: str) -> str:
    raw = str(text or "").strip()
    start, end = raw.find("{"), raw.rfind("}")
    if 0 <= start < end:
        try:
            payload = json.loads(raw[start : end + 1])
            if isinstance(payload, dict) and "answer" in payload:
                return _norm(payload.get("answer"))
        except Exception:
            pass
    first = raw.splitlines()[0] if raw else ""
    return _norm(first)


def _rows_from_parquet(path: Path) -> list[dict[str, Any]]:
    import pandas as pd

    frame = pd.read_parquet(path)
    rows = []
    for _, series in frame.iterrows():
        row = series.to_dict()
        row["contexts"] = list(row.get("contexts") if row.get("contexts") is not None else [])
        row["questions"] = list(row.get("questions") if row.get("questions") is not None else [])
        rows.append(row)
    return rows


def _reserve_candidates(rows: list[dict[str, Any]], freeze: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = build_wiki_history_candidates(rows)
    source_disjoint = select_source_disjoint_wiki_candidates(candidates, limit=10_000)
    by_id = {str(row.get("candidate_id") or ""): row for row in source_disjoint}
    reserve_ids = [str(value) for value in freeze.get("formal_reserve_candidate_ids") or []]
    screen_ids = set(str(value) for value in freeze.get("provider_screen_candidate_ids") or [])
    if not reserve_ids or screen_ids & set(reserve_ids):
        raise RuntimeError("invalid provider-screen/formal-reserve split")
    missing = [candidate_id for candidate_id in reserve_ids if candidate_id not in by_id]
    if missing:
        raise RuntimeError(f"reserve reconstruction mismatch: {missing[:5]}")
    return [dict(by_id[candidate_id]) for candidate_id in reserve_ids]


def build_prompt(candidate: dict[str, Any], arm: str) -> str:
    memories = list((candidate.get("arm_memories") or {}).get(arm) or [])
    if len(memories) != 3:
        raise RuntimeError(f"arm {arm} is not a three-memory intervention")
    target_index = int(candidate.get("target_index"))
    n_steps = int(candidate.get("n_steps_back"))
    # target_index + n_steps + 1 is exactly the total revision count implied by MINTEval metadata.
    total_revisions = target_index + n_steps + 1
    blocks = []
    for slot, memory in enumerate(memories, 1):
        blocks.append(
            f"MEMORY {slot}\n"
            f"revision_index={int(memory.get('index'))} of 0..{total_revisions - 1} (oldest to newest)\n"
            f"revision_timestamp={memory.get('timestamp') or 'unknown'}\n"
            f"excerpt={memory.get('text') or ''}"
        )
    return (
        "You are answering one historical Wikipedia question from a controlled memory-retrieval experiment. "
        f"The article has {total_revisions} revisions indexed 0..{total_revisions - 1}, oldest to newest. "
        f"The requested revision is index {target_index}, which is {n_steps} edits before the latest revision. "
        "All three memories are authentic excerpts, but some may come from other revisions and are distractors. "
        "Use the explicit revision provenance; do not infer that display order means chronology. "
        "Copy the answer exactly when possible and return JSON only as {\"answer\":\"...\"}, with no explanation.\n\n"
        + "\n\n".join(blocks)
        + f"\n\nQUESTION: {candidate.get('question')}"
    )


def _model_manifest(path: Path) -> dict[str, Any]:
    out: dict[str, Any] = {
        "path": str(path),
        "revision": path.name if re.fullmatch(r"[0-9a-f]{40}", path.name) else "",
    }
    for name in ("config.json", "tokenizer_config.json", "model.safetensors.index.json", "generation_config.json"):
        file = path / name
        if file.exists():
            out[name] = {"bytes": file.stat().st_size, "sha256": _sha256(file)}
    return out


def _generate_batch(model: Any, tokenizer: Any, prompts: list[str], device: str, max_new_tokens: int) -> list[str]:
    import torch

    rendered = [
        tokenizer.apply_chat_template([{"role": "user", "content": prompt}], tokenize=False, add_generation_prompt=True)
        for prompt in prompts
    ]
    enc = tokenizer(rendered, return_tensors="pt", padding=True, truncation=True, max_length=4096)
    enc = {key: value.to(device) for key, value in enc.items()}
    input_len = enc["input_ids"].shape[1]
    with torch.inference_mode():
        output = model.generate(
            **enc,
            do_sample=False,
            max_new_tokens=max_new_tokens,
            use_cache=True,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
    return tokenizer.batch_decode(output[:, input_len:], skip_special_tokens=True)


def run(candidates: list[dict[str, Any]], model_path: Path, *, device: str, batch_size: int, max_new_tokens: int, required: int) -> dict[str, Any]:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True, trust_remote_code=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id
    tokenizer.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        local_files_only=True,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
        low_cpu_mem_usage=True,
    ).to(device)
    model.eval()

    jobs: list[tuple[int, str, str]] = []
    for index, candidate in enumerate(candidates):
        for arm in ("none", "A", "B", "AB"):
            jobs.append((index, arm, build_prompt(candidate, arm)))
    outputs: dict[tuple[int, str], str] = {}
    for start in range(0, len(jobs), max(1, batch_size)):
        batch = jobs[start : start + max(1, batch_size)]
        texts = _generate_batch(model, tokenizer, [row[2] for row in batch], device, max_new_tokens)
        for row, text in zip(batch, texts):
            outputs[(row[0], row[1])] = text

    results = []
    positives = 0
    eligible = 0
    patterns: dict[str, int] = {}
    for index, candidate in enumerate(candidates):
        gold = _norm(candidate.get("gold_answer"))
        binary: dict[str, int] = {}
        arm_rows: dict[str, Any] = {}
        for arm in ("none", "A", "B", "AB"):
            raw = outputs[(index, arm)]
            answer = _parse_answer(raw)
            correct = int(bool(gold) and answer == gold)
            binary[arm] = correct
            arm_rows[arm] = {"answer_key": answer, "gold_key": gold, "correct": bool(correct), "raw_text": raw[:800]}
        score = score_factorial_outcome(binary)
        base_single_ok = binary["none"] == 1 and binary["A"] == 1 and binary["B"] == 1
        eligible += int(base_single_ok)
        positives += int(bool(score.get("mechanism_support")))
        pattern = "".join(str(binary[name]) for name in ("none", "A", "B", "AB"))
        patterns[pattern] = patterns.get(pattern, 0) + 1
        results.append({
            "candidate_id": candidate.get("candidate_id"),
            "history_id": candidate.get("history_id"),
            "question": candidate.get("question"),
            "target_index": candidate.get("target_index"),
            "n_steps_back": candidate.get("n_steps_back"),
            "gold_answer": candidate.get("gold_answer"),
            "eligible_base_and_singles": base_single_ok,
            "arms": arm_rows,
            "score": score,
        })
    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "idea_id": "B3-CO-RETRIEVAL-INTERACTION",
        "mode": "FIXED_OPEN_WEIGHT_OUTCOME_BLIND_WIKI_CONFIRMATION",
        "model": _model_manifest(model_path),
        "runtime": {"torch": torch.__version__, "device": device, "dtype": "bfloat16", "do_sample": False, "batch_size": batch_size, "max_new_tokens": max_new_tokens},
        "prompt_contract": {
            "target_revision_provenance_explicit": True,
            "private_gold_not_in_prompt": True,
            "revision_index_and_timestamp_visible": True,
            "display_order_not_chronology_instruction": True,
            "same_information_across_factorial_arms_except_A_B_retrieval": True,
        },
        "units_executed": len(candidates),
        "base_and_single_arms_correct": eligible,
        "joint_only_interaction_positive": positives,
        "required_interaction_positive_support": required,
        "pattern_counts": patterns,
        "support_gate_met": positives >= required,
        "support_qualified": positives >= required,
        "selection_used_model_outputs": False,
        "selection_used_gold_answer": False,
        "scientific_authority": False,
        "authority": {"problem_gate": False, "method": False, "experiment": False, "p0": False, "gpu": False},
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parquet", type=Path, required=True)
    parser.add_argument("--reserve-freeze", type=Path, required=True)
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--max-new-tokens", type=int, default=64)
    parser.add_argument("--required-support", type=int, default=6)
    args = parser.parse_args()

    freeze = json.loads(args.reserve_freeze.read_text(encoding="utf-8"))
    if freeze.get("formal_reserve_outputs_seen") is not False:
        raise RuntimeError("formal reserve already exposed to outputs")
    if freeze.get("selection_used_model_outputs") is not False or freeze.get("selection_used_gold_answer") is not False:
        raise RuntimeError("reserve freeze is not outcome-blind")
    candidates = _reserve_candidates(_rows_from_parquet(args.parquet), freeze)
    result = run(candidates, args.model_path, device=args.device, batch_size=args.batch_size, max_new_tokens=args.max_new_tokens, required=args.required_support)
    result["dataset_snapshot"] = {"repository": "dinobby/MINTEval", "split": "wiki_revisions", "bytes": args.parquet.stat().st_size, "sha256": _sha256(args.parquet)}
    result["reserve_freeze"] = {"path": str(args.reserve_freeze), "sha256": _sha256(args.reserve_freeze), "candidate_count": len(candidates)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "units": result["units_executed"],
        "eligible": result["base_and_single_arms_correct"],
        "joint_positive": result["joint_only_interaction_positive"],
        "required": result["required_interaction_positive_support"],
        "support_gate_met": result["support_gate_met"],
        "patterns": result["pattern_counts"],
        "model_revision": result["model"].get("revision"),
        "dataset_sha256": result["dataset_snapshot"]["sha256"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
