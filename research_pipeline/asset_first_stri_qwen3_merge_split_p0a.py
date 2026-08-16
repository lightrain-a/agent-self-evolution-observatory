from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import json
import math
import os
import random
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package_bundle_sha(package_dir: Path) -> str:
    h = hashlib.sha256()
    for path in sorted(p for p in package_dir.iterdir() if p.is_file()):
        h.update(path.name.encode("utf-8") + b"\0" + sha256(path).encode("ascii") + b"\n")
    return h.hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def append_jsonl(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")


def load_validator(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load validator: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    fn = getattr(module, "validate_sample", None)
    if not callable(fn):
        raise RuntimeError(f"missing validate_sample: {path}")
    return fn


def distribution(items: list[str]) -> dict[str, float]:
    if not items:
        return {}
    counts = collections.Counter(items)
    n = float(len(items))
    return {key: value / n for key, value in counts.items()}


def mix_distributions(source: dict[str, dict[str, float]], weights: dict[str, float]) -> dict[str, float]:
    keys = set().union(*(set(value) for value in source.values()))
    return {
        key: sum(float(weights.get(source_id, 0.0)) * source[source_id].get(key, 0.0) for source_id in source)
        for key in keys
    }


def tv(left: dict[str, float], right: dict[str, float]) -> float:
    keys = set(left) | set(right)
    return 0.5 * sum(abs(left.get(key, 0.0) - right.get(key, 0.0)) for key in keys)


def percentile(values: list[float], q: float) -> float:
    if not values:
        return float("nan")
    xs = sorted(values)
    pos = (len(xs) - 1) * q
    lo, hi = int(math.floor(pos)), int(math.ceil(pos))
    if lo == hi:
        return xs[lo]
    return xs[lo] * (hi - pos) + xs[hi] * (pos - lo)


def pattern_key(skill_ids: list[str]) -> str:
    return "+".join(sorted(skill_ids)) if skill_ids else "NONE"


def tool_name(sample: dict[str, Any]) -> str:
    answer = sample.get("answer")
    if isinstance(answer, dict):
        return str(answer.get("name") or answer.get("function") or "UNKNOWN")
    if isinstance(answer, list) and len(answer) == 1 and isinstance(answer[0], dict):
        return str(answer[0].get("name") or answer[0].get("function") or "UNKNOWN")
    return "UNKNOWN"


def decide(*, qualification_pass: bool, witness_passes: dict[str, bool], budget_pass: bool = True) -> tuple[str, bool]:
    if not qualification_pass:
        return "INCONCLUSIVE_PROPOSER_QUALIFICATION_FAILED", False
    if not budget_pass:
        return "INCONCLUSIVE_BUDGET_EXCEEDED", False
    passed = sum(bool(value) for value in witness_passes.values())
    if passed == len(witness_passes) and passed > 0:
        return "DYNAMIC_PARTIAL_OVERLAP_REPRESENTATION_SENSITIVITY_SUPPORTED", True
    if passed == 0:
        return "STOP_DYNAMIC_PARTIAL_OVERLAP_PROPAGATION_GATE_NOT_MET", True
    return "INCONCLUSIVE_ONE_OF_TWO_WITNESSES_ONLY", True


def validate_contract(contract: dict[str, Any]) -> dict[str, Any]:
    repo = Path(contract["execution_substrate"]["author_repo"])
    model = Path(contract["execution_substrate"]["model_path"])
    commit = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    expected = contract["author_asset"]
    checks: dict[str, bool] = {
        "repo_commit": commit == expected["repo_commit"],
        "question_generate_sha": sha256(repo / "question_generate/question_generate.py") == expected["question_generate_sha256"],
        "skill_library_sha": sha256(repo / "skill_library/library.py") == expected["skill_library_sha256"],
        "tool_prompts_sha": sha256(repo / "tool_call/prompts.py") == expected["tool_prompts_sha256"],
        "tool_parsing_sha": sha256(repo / "tool_call/parsing.py") == expected["tool_parsing_sha256"],
        "tool_contracts_sha": sha256(repo / "tool_call/contracts.py") == expected["tool_contracts_sha256"],
        "arm_specific_generation_false": contract["generation"]["arm_specific_generation"] is False,
        "training_false": contract["generation"]["training"] is False,
        "single_backbone": int(contract["budget"]["second_backbone"]) == 0,
        "one_model_load": int(contract["budget"]["model_loads"]) == 1,
    }
    package_root = repo / "tool_call/packages"
    for skill_id, digest in expected["package_hashes"].items():
        checks[f"package_{skill_id}_sha"] = package_bundle_sha(package_root / skill_id) == digest
    for filename, digest in contract["execution_substrate"]["model_hashes"].items():
        checks[f"model_{filename}_sha"] = sha256(model / filename) == digest
    source_ids = list(contract["generation"]["source_skill_ids"])
    checks["three_frozen_sources"] = source_ids == ["skill_003", "skill_004", "skill_015"]
    for arm_name, arm in contract["representation_counterfactuals"].items():
        if not isinstance(arm, dict) or "source_mixture_weights" not in arm:
            continue
        weights = arm["source_mixture_weights"]
        checks[f"{arm_name}_weights_sum_one"] = abs(sum(float(weights[s]) for s in source_ids) - 1.0) < 1e-12
        checks[f"{arm_name}_all_sources_bound"] = set(weights) == set(source_ids)
    return {"pass": all(checks.values()), "checks": checks, "commit": commit}


def build_assets(contract: dict[str, Any]):
    repo = Path(contract["execution_substrate"]["author_repo"])
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    from skill_library.package_library import load_generation_skill_library, expand_skill_for_disclosure
    from tool_call.prompts import build_questioner_messages
    from tool_call.parsing import parse_task_sample
    from tool_call.contracts import check_task_sample_contract

    package_root = repo / "tool_call/packages"
    skills = load_generation_skill_library(str(repo / "tool_call/skills.json"), package_root=str(package_root))
    by_id = {str(skill["id"]): skill for skill in skills}
    prompts: dict[str, list[dict[str, str]]] = {}
    for skill_id in contract["generation"]["source_skill_ids"]:
        expanded = expand_skill_for_disclosure(
            by_id[skill_id],
            contract["generation"]["disclosure_level"],
            package_root=str(package_root),
            library_path=str(repo / "tool_call/skills.json"),
        )
        prompts[skill_id] = build_questioner_messages(expanded, disclosure_level=contract["generation"]["disclosure_level"])
    validators = {}
    for directory in sorted(package_root.glob("skill_*")):
        path = directory / "validator.py"
        if path.exists():
            validators[directory.name] = load_validator(path, f"stri_p0a_validator_{directory.name}")
    return prompts, parse_task_sample, check_task_sample_contract, validators


def preflight(contract: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    review = validate_contract(contract)
    if not review["pass"]:
        raise RuntimeError(f"contract/hash preflight failed: {review}")
    repo = Path(contract["execution_substrate"]["author_repo"])
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    import torch
    import transformers
    import vllm
    from transformers import AutoTokenizer

    checks = dict(review["checks"])
    checks.update({
        "vllm_version": str(vllm.__version__) == str(contract["execution_substrate"]["vllm_version"]),
        "torch_version": str(torch.__version__) == str(contract["execution_substrate"]["torch_version"]),
        "transformers_version": str(transformers.__version__) == str(contract["execution_substrate"]["transformers_version"]),
    })
    prompts, _, _, validators = build_assets(contract)
    tokenizer = AutoTokenizer.from_pretrained(contract["execution_substrate"]["model_path"], local_files_only=True, trust_remote_code=True)
    rendered = {}
    for skill_id, messages in prompts.items():
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, add_special_tokens=True)
        rendered[skill_id] = {
            "roles": [message["role"] for message in messages],
            "chars": len(text),
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        }
    checks["validator_count_15"] = len(validators) == 15
    checks["prompt_count_3"] = len(prompts) == 3
    result = {
        "schema_version": "1.0",
        "pass": all(checks.values()),
        "checks": checks,
        "commit": review["commit"],
        "validator_count": len(validators),
        "source_prompts": rendered,
        "gpu_work_started": False,
        "scientific_authority": False,
    }
    atomic_json(output_dir / "preflight.json", result)
    return result


def _evaluate_witness(
    *,
    source_rows: dict[str, list[dict[str, Any]]],
    split_weights: dict[str, float],
    merge_weights: dict[str, float],
    gate: dict[str, Any],
    bootstrap_replicates: int,
    seed: int,
) -> dict[str, Any]:
    pattern_dists = {source: distribution([row["validator_pattern"] for row in rows]) for source, rows in source_rows.items()}
    split = mix_distributions(pattern_dists, split_weights)
    merged = mix_distributions(pattern_dists, merge_weights)
    distance = tv(split, merged)
    shifts = {key: merged.get(key, 0.0) - split.get(key, 0.0) for key in set(split) | set(merged)}
    max_shift = max((abs(value) for value in shifts.values()), default=0.0)

    rng = random.Random(seed)
    boot = []
    for _ in range(bootstrap_replicates):
        resampled = {}
        for source, rows in source_rows.items():
            values = [rows[rng.randrange(len(rows))]["validator_pattern"] for __ in range(len(rows))]
            resampled[source] = distribution(values)
        boot.append(tv(mix_distributions(resampled, split_weights), mix_distributions(resampled, merge_weights)))
    lower95, upper95 = percentile(boot, 0.025), percentile(boot, 0.975)
    checks = {
        "validator_pattern_tv": {"actual": distance, "required_min": float(gate["validator_pattern_tv_distance_min"]), "pass": distance >= float(gate["validator_pattern_tv_distance_min"])},
        "validator_pattern_tv_bootstrap_lower95": {"actual": lower95, "required_min": float(gate["validator_pattern_tv_bootstrap_lower95_min"]), "pass": lower95 >= float(gate["validator_pattern_tv_bootstrap_lower95_min"])},
        "max_single_pattern_shift": {"actual": max_shift, "required_min": float(gate["max_single_pattern_probability_shift_min"]), "pass": max_shift >= float(gate["max_single_pattern_probability_shift_min"])},
    }
    return {
        "split_distribution": split,
        "merged_distribution": merged,
        "validator_pattern_tv_distance": distance,
        "validator_pattern_tv_bootstrap_lower95": lower95,
        "validator_pattern_tv_bootstrap_upper95": upper95,
        "max_single_pattern_probability_shift": max_shift,
        "pattern_probability_shifts": dict(sorted(shifts.items(), key=lambda item: -abs(item[1]))),
        "checks": checks,
        "pass": all(check["pass"] for check in checks.values()),
    }


def run(contract: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    pf = preflight(contract, output_dir)
    if not pf["pass"]:
        raise RuntimeError(f"preflight failed: {pf}")

    repo = Path(contract["execution_substrate"]["author_repo"])
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    import torch
    import transformers
    import vllm
    from transformers import AutoTokenizer
    from utils.vllm_utils import llm_context_kwargs, trust_remote_code_enabled

    prompts_by_source, parse_task_sample, check_task_contract, validators = build_assets(contract)
    model_path = contract["execution_substrate"]["model_path"]
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True, trust_remote_code=trust_remote_code_enabled())
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id

    source_ids = list(contract["generation"]["source_skill_ids"])
    n = int(contract["generation"]["samples_per_source"])
    prompts: list[str] = []
    metadata: list[tuple[str, int]] = []
    for source_id in source_ids:
        rendered = tokenizer.apply_chat_template(
            prompts_by_source[source_id], tokenize=False, add_generation_prompt=True, add_special_tokens=True
        )
        for index in range(n):
            prompts.append(rendered)
            metadata.append((source_id, index))

    started = time.monotonic()
    model = vllm.LLM(
        model=model_path,
        tokenizer=model_path,
        seed=int(contract["generation"]["global_seed"]),
        trust_remote_code=trust_remote_code_enabled(),
        **llm_context_kwargs(require_enable_env=True),
    )
    params = vllm.SamplingParams(
        max_tokens=int(contract["generation"]["max_tokens"]),
        temperature=float(contract["generation"]["temperature"]),
        top_p=float(contract["generation"]["top_p"]),
        n=int(contract["generation"]["n"]),
        stop_token_ids=[tokenizer.eos_token_id],
    )
    completions = model.generate(prompts, sampling_params=params)
    gpu_hours = (time.monotonic() - started) / 3600.0

    raw_path = output_dir / "raw-generations.jsonl"
    raw_path.unlink(missing_ok=True)
    source_rows: dict[str, list[dict[str, Any]]] = {source: [] for source in source_ids}
    counts = {source: {"generated": 0, "parsed": 0, "contract_valid": 0} for source in source_ids}
    for completion, (source_id, source_index) in zip(completions, metadata, strict=True):
        counts[source_id]["generated"] += 1
        text = str(completion.outputs[0].text if completion.outputs else "")
        record: dict[str, Any] = {"source_skill_id": source_id, "source_index": source_index, "raw_text": text}
        try:
            sample = parse_task_sample(text)
        except Exception as exc:
            sample = None
            record["parse_exception"] = f"{type(exc).__name__}: {exc}"
        if sample is not None:
            counts[source_id]["parsed"] += 1
            contract_result = check_task_contract(sample)
            record["parsed"] = True
            record["contract"] = contract_result
            if float(contract_result.get("contract_valid", 0.0)) >= 1.0:
                counts[source_id]["contract_valid"] += 1
                accepted = []
                validator_errors = {}
                for validator_id, fn in validators.items():
                    try:
                        result = fn(sample)
                        if bool(result.get("valid")):
                            accepted.append(validator_id)
                    except Exception as exc:
                        validator_errors[validator_id] = f"{type(exc).__name__}: {exc}"
                row = {
                    "source_skill_id": source_id,
                    "source_index": source_index,
                    "validator_pattern": pattern_key(accepted),
                    "accepted_skill_ids": sorted(accepted),
                    "tool_name": tool_name(sample),
                }
                if validator_errors:
                    row["validator_errors"] = validator_errors
                source_rows[source_id].append(row)
                record.update(row)
        else:
            record["parsed"] = False
        append_jsonl(raw_path, record)

    min_valid = min(counts[source]["contract_valid"] for source in source_ids)
    qualification_required = int(contract["qualification_gate"]["contract_valid_per_source_min"])
    qualification_pass = min_valid >= qualification_required
    budget_pass = gpu_hours <= float(contract["budget"]["gpu_hours_cap"])
    qualification = {
        "minimum_contract_valid_per_source": min_valid,
        "required_min": qualification_required,
        "pass": qualification_pass,
        "budget_gpu_hours": gpu_hours,
        "budget_gpu_hours_cap": float(contract["budget"]["gpu_hours_cap"]),
        "budget_pass": budget_pass,
    }
    if not qualification_pass or not budget_pass:
        decision, protocol_valid = decide(qualification_pass=qualification_pass, witness_passes={}, budget_pass=budget_pass)
        result = {
            "schema_version": "1.0",
            "experiment_id": contract["experiment_id"],
            "candidate_id": contract["candidate_id"],
            "decision": decision,
            "scientific_result_available": False,
            "protocol_valid_for_scientific_update": False,
            "qualification": qualification,
            "generation_counts": counts,
            "gpu_hours": gpu_hours,
            "raw_sha256": sha256(raw_path),
            "paper_design_authorized": False,
            "method_authorized": False,
            "second_backbone": 0,
            "scientific_authority": False,
        }
        atomic_json(output_dir / "result.json", result)
        return result

    transforms = contract["representation_counterfactuals"]
    split_weights = transforms["split"]["source_mixture_weights"]
    gate = contract["per_witness_dynamic_gate"]
    bootstrap_n = int(gate["bootstrap_replicates"])
    witness_results = {}
    for offset, witness_name in enumerate(("merge_003_015", "merge_004_015")):
        witness_results[witness_name] = _evaluate_witness(
            source_rows=source_rows,
            split_weights=split_weights,
            merge_weights=transforms[witness_name]["source_mixture_weights"],
            gate=gate,
            bootstrap_replicates=bootstrap_n,
            seed=2026081700 + offset,
        )

    witness_passes = {name: result["pass"] for name, result in witness_results.items()}
    decision, scientific_available = decide(
        qualification_pass=True, witness_passes=witness_passes, budget_pass=True
    )
    tool_dists = {source: distribution([row["tool_name"] for row in rows]) for source, rows in source_rows.items()}
    split_tools = mix_distributions(tool_dists, split_weights)
    secondary_tool_tv = {
        name: tv(split_tools, mix_distributions(tool_dists, transforms[name]["source_mixture_weights"]))
        for name in witness_results
    }
    result = {
        "schema_version": "1.0",
        "experiment_id": contract["experiment_id"],
        "candidate_id": contract["candidate_id"],
        "decision": decision,
        "scientific_result_available": scientific_available,
        "protocol_valid_for_scientific_update": True,
        "qualification": qualification,
        "generation_counts": counts,
        "witness_results": witness_results,
        "witness_passes": witness_passes,
        "secondary_tool_name_tv": secondary_tool_tv,
        "matched_source_bank_replay": True,
        "arm_specific_model_generation": False,
        "gpu_hours": gpu_hours,
        "raw_sha256": sha256(raw_path),
        "next_action": contract["next_if_go"] if decision.startswith("DYNAMIC_") else contract["next_if_stop"] if decision.startswith("STOP_") else contract["next_if_inconclusive"],
        "paper_design_authorized": False,
        "method_authorized": False,
        "second_backbone": 0,
        "scientific_authority": False,
    }
    atomic_json(output_dir / "result.json", result)
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--preflight-only", action="store_true")
    args = ap.parse_args()
    contract = load_json(args.contract)
    if args.preflight_only:
        result = preflight(contract, args.output_dir)
        print(json.dumps({"preflight_pass": result["pass"], "validator_count": result["validator_count"], "source_prompts": result["source_prompts"]}, ensure_ascii=False))
    else:
        result = run(contract, args.output_dir)
        print(json.dumps({"decision": result["decision"], "qualification": result["qualification"], "witness_passes": result.get("witness_passes")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
