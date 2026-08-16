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


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(16 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def package_bundle_sha(package_dir: Path) -> str:
    h = hashlib.sha256()
    for path in sorted(p for p in package_dir.iterdir() if p.is_file()):
        h.update(path.name.encode("utf-8") + b"\0" + sha256(path).encode("ascii") + b"\n")
    return h.hexdigest()


def atomic_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def append_jsonl(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n")


def load_validator(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load validator: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    fn = getattr(module, "validate_sample", None)
    if not callable(fn):
        raise RuntimeError(f"missing validate_sample in {path}")
    return fn


def distribution(items: list[str]) -> dict[str, float]:
    c = collections.Counter(items)
    n = max(1, len(items))
    return {k: v / n for k, v in c.items()}


def mix_distributions(source_dists: dict[str, dict[str, float]], weights: dict[str, float]) -> dict[str, float]:
    keys = set().union(*(set(d) for d in source_dists.values()))
    return {k: sum(float(weights.get(s, 0.0)) * source_dists[s].get(k, 0.0) for s in source_dists) for k in keys}


def tv(p: dict[str, float], q: dict[str, float]) -> float:
    keys = set(p) | set(q)
    return 0.5 * sum(abs(p.get(k, 0.0) - q.get(k, 0.0)) for k in keys)


def pattern_key(skill_ids: list[str]) -> str:
    return "+".join(sorted(skill_ids)) if skill_ids else "NONE"


def tool_name(sample: dict[str, Any]) -> str:
    answer = sample.get("answer")
    if isinstance(answer, dict):
        return str(answer.get("name") or answer.get("function") or "UNKNOWN")
    if isinstance(answer, list) and len(answer) == 1 and isinstance(answer[0], dict):
        return str(answer[0].get("name") or answer[0].get("function") or "UNKNOWN")
    return "UNKNOWN"


def percentile(values: list[float], q: float) -> float:
    if not values:
        return float("nan")
    xs = sorted(values)
    pos = (len(xs) - 1) * q
    lo = int(math.floor(pos)); hi = int(math.ceil(pos))
    if lo == hi:
        return xs[lo]
    return xs[lo] * (hi - pos) + xs[hi] * (pos - lo)


def adjudicate_dynamic_gate(checks: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Separate proposer qualification from the scientific propagation gate.

    An empty/invalid generated-task bank cannot support either a positive or a
    negative scientific update. In particular, downstream distribution metrics
    computed from zero qualified units must never be interpreted as evidence
    for the no-propagation reduction.
    """
    qualification = bool((checks.get("contract_valid_per_source") or {}).get("pass"))
    if not qualification:
        return {
            "decision": "INCONCLUSIVE_PROPOSER_QUALIFICATION_FAILED",
            "scientific_result_available": False,
            "primary_mechanism_positive": False,
            "protocol_valid_for_scientific_update": False,
            "qualification_pass": False,
        }
    positive = all(bool(row.get("pass")) for row in checks.values())
    return {
        "decision": "DYNAMIC_CURRICULUM_REPRESENTATION_SENSITIVITY_SUPPORTED" if positive else "STOP_DYNAMIC_PROPAGATION_GATE_NOT_MET",
        "scientific_result_available": True,
        "primary_mechanism_positive": positive,
        "protocol_valid_for_scientific_update": True,
        "qualification_pass": True,
    }


def validate_contract(contract: dict[str, Any]) -> dict[str, Any]:
    repo = Path(contract["author_asset"]["repo"])
    model = Path(contract["proposer"]["model_path"])
    commit = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    checks = {
        "repo_commit": commit == contract["author_asset"]["commit"],
        "tool_prompts_sha": sha256(repo / "tool_call/prompts.py") == contract["author_asset"]["tool_prompts_sha256"],
        "tool_parsing_sha": sha256(repo / "tool_call/parsing.py") == contract["author_asset"]["tool_parsing_sha256"],
        "tool_contracts_sha": sha256(repo / "tool_call/contracts.py") == contract["author_asset"]["tool_contracts_sha256"],
        "model_config_sha": sha256(model / "config.json") == contract["proposer"]["model_config_sha256"],
        "generation_config_sha": sha256(model / "generation_config.json") == contract["proposer"]["generation_config_sha256"],
        "tokenizer_config_sha": sha256(model / "tokenizer_config.json") == contract["proposer"]["tokenizer_config_sha256"],
        "tokenizer_sha": sha256(model / "tokenizer.json") == contract["proposer"]["tokenizer_sha256"],
    }
    package_root = repo / "tool_call/packages"
    for skill_id, expected in contract["author_asset"]["package_hashes"].items():
        checks[f"package_{skill_id}_sha"] = package_bundle_sha(package_root / skill_id) == expected
    expected_lfs = contract["proposer"].get("expected_lfs_sha256") or {}
    safetensors_total = 0
    for name, expected in expected_lfs.items():
        path = model / name
        checks[f"model_file_{name}_exists"] = path.is_file()
        if path.is_file():
            checks[f"model_file_{name}_sha"] = sha256(path) == expected
            if name.endswith(".safetensors"):
                safetensors_total += path.stat().st_size
    expected_total = contract["proposer"].get("expected_total_safetensors_bytes")
    if expected_total is not None:
        checks["safetensors_total_bytes"] = safetensors_total == int(expected_total)
    checks["training_disabled"] = contract["proposer"]["training"] is False
    checks["single_model_load"] = int(contract["budget"]["model_loads"]) == 1
    checks["no_second_backbone"] = int(contract["budget"]["second_backbone"]) == 0
    return {"pass": all(checks.values()), "checks": checks, "commit": commit, "safetensors_total_bytes": safetensors_total}


def build_assets(contract: dict[str, Any]):
    repo = Path(contract["author_asset"]["repo"])
    sys.path.insert(0, str(repo)) if str(repo) not in sys.path else None
    from skill_library.package_library import load_generation_skill_library, expand_skill_for_disclosure
    from tool_call.prompts import build_questioner_messages
    from tool_call.parsing import parse_task_sample
    from tool_call.contracts import check_task_sample_contract

    package_root = repo / "tool_call/packages"
    # The release reconstructs the generation library from package_root even when
    # the legacy JSON path does not exist. This is the same author loader used by question generation.
    skills = load_generation_skill_library(
        str(repo / "tool_call/skills.json"),
        package_root=str(package_root),
    )
    by_id = {str(s["id"]): s for s in skills}
    prompts: dict[str, list[dict[str, str]]] = {}
    for skill_id in contract["proposer"]["source_skill_ids"]:
        expanded = expand_skill_for_disclosure(
            by_id[skill_id],
            contract["proposer"]["disclosure_level"],
            package_root=str(package_root),
            library_path=str(repo / "tool_call/skills.json"),
        )
        prompts[skill_id] = build_questioner_messages(expanded, disclosure_level=contract["proposer"]["disclosure_level"])

    validators = {}
    for d in sorted(package_root.glob("skill_*")):
        path = d / "validator.py"
        if path.exists():
            validators[d.name] = load_validator(path, f"stri_validator_{d.name}")
    return prompts, parse_task_sample, check_task_sample_contract, validators


def preflight(contract: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    review = validate_contract(contract)
    if not review["pass"]:
        raise RuntimeError(f"contract hash/authority preflight failed: {review}")
    prompts, _, _, validators = build_assets(contract)
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(contract["proposer"]["model_path"], local_files_only=True, trust_remote_code=True)
    rendered = {}
    template_kwargs = {}
    if "enable_thinking" in contract["proposer"]:
        template_kwargs["enable_thinking"] = bool(contract["proposer"]["enable_thinking"])
    for sid, messages in prompts.items():
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, add_special_tokens=True, **template_kwargs)
        rendered[sid] = {
            "message_roles": [m["role"] for m in messages],
            "message_chars": sum(len(m["content"]) for m in messages),
            "rendered_chars": len(text),
            "rendered_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        }
    result = {
        **review,
        "validator_count": len(validators),
        "source_prompts": rendered,
        "source_prompt_count": len(prompts),
        "model_path": contract["proposer"]["model_path"],
        "gpu_work_started": False,
    }
    result["pass"] = result["pass"] and len(validators) == 15 and len(prompts) == 3
    atomic_json(output_dir / "preflight.json", result)
    return result


def run(contract: dict[str, Any], output_dir: Path, *, qualification_only: bool = False) -> dict[str, Any]:
    pf = preflight(contract, output_dir)
    if not pf["pass"]:
        raise RuntimeError(f"preflight failed: {pf}")

    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    prompts, parse_task_sample, check_contract, validators = build_assets(contract)
    model_path = contract["proposer"]["model_path"]
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True, trust_remote_code=True)
    tokenizer.padding_side = "left"
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        local_files_only=True,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
        device_map={"": "cuda:0"},
    )
    model.eval()

    raw_path = output_dir / "raw-generations.jsonl"
    raw_path.unlink(missing_ok=True)
    valid_by_source: dict[str, list[dict[str, Any]]] = {sid: [] for sid in prompts}
    generation_counts = {}
    batch_size = int(contract["proposer"]["batch_size"])
    n = int(contract["proposer"]["samples_per_source_skill"])
    started = time.monotonic()

    template_kwargs = {}
    if "enable_thinking" in contract["proposer"]:
        template_kwargs["enable_thinking"] = bool(contract["proposer"]["enable_thinking"])
    for sid in contract["proposer"]["source_skill_ids"]:
        seed = int(contract["proposer"]["seed_by_source"][sid])
        random.seed(seed); torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
        prompt_text = tokenizer.apply_chat_template(prompts[sid], tokenize=False, add_generation_prompt=True, add_special_tokens=True, **template_kwargs)
        generated = 0; parsed = 0; contract_valid = 0
        for start in range(0, n, batch_size):
            b = min(batch_size, n - start)
            enc = tokenizer([prompt_text] * b, return_tensors="pt", padding=True).to(model.device)
            with torch.inference_mode():
                ids = model.generate(
                    **enc,
                    max_new_tokens=int(contract["proposer"]["max_new_tokens"]),
                    do_sample=bool(contract["proposer"]["do_sample"]),
                    temperature=float(contract["proposer"]["temperature"]),
                    top_p=float(contract["proposer"]["top_p"]),
                    pad_token_id=tokenizer.pad_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                )
            new_ids = ids[:, enc["input_ids"].shape[1]:]
            texts = tokenizer.batch_decode(new_ids, skip_special_tokens=True)
            for local_index, text in enumerate(texts):
                generated += 1
                row_index = start + local_index
                record: dict[str, Any] = {"source_skill_id": sid, "source_index": row_index, "raw_text": text}
                try:
                    sample = parse_task_sample(text)
                except Exception as exc:
                    sample = None; record["parse_exception"] = f"{type(exc).__name__}: {exc}"
                if sample is not None:
                    parsed += 1
                    c = check_contract(sample)
                    record["parsed"] = True
                    record["contract"] = c
                    if float(c.get("contract_valid", 0.0)) >= 1.0:
                        contract_valid += 1
                        accepted = []
                        validator_errors = {}
                        for vid, fn in validators.items():
                            try:
                                vr = fn(sample)
                                if bool(vr.get("valid")):
                                    accepted.append(vid)
                            except Exception as exc:
                                validator_errors[vid] = f"{type(exc).__name__}: {exc}"
                        row = {
                            "source_skill_id": sid,
                            "source_index": row_index,
                            "validator_pattern": pattern_key(accepted),
                            "accepted_skill_ids": sorted(accepted),
                            "tool_name": tool_name(sample),
                            "sample": sample,
                        }
                        if validator_errors:
                            row["validator_errors"] = validator_errors
                        valid_by_source[sid].append(row)
                        record.update({k: row[k] for k in ("validator_pattern", "accepted_skill_ids", "tool_name")})
                else:
                    record["parsed"] = False
                append_jsonl(raw_path, record)
        generation_counts[sid] = {"generated": generated, "parsed": parsed, "contract_valid": contract_valid}

    pattern_dists = {sid: distribution([r["validator_pattern"] for r in rows]) for sid, rows in valid_by_source.items()}
    tool_dists = {sid: distribution([r["tool_name"] for r in rows]) for sid, rows in valid_by_source.items()}
    original_w = contract["matched_mixture_replay"]["arm_original"]["mixture_weights"]
    split_w = contract["matched_mixture_replay"]["arm_semantic_split"]["mixture_weights_after_quotienting_identical_015_entries"]
    p0 = mix_distributions(pattern_dists, original_w); p1 = mix_distributions(pattern_dists, split_w)
    t0 = mix_distributions(tool_dists, original_w); t1 = mix_distributions(tool_dists, split_w)
    pattern_tv = tv(p0, p1); tool_tv = tv(t0, t1)
    pattern_shifts = {k: p1.get(k, 0.0)-p0.get(k, 0.0) for k in set(p0)|set(p1)}
    max_shift = max((abs(v) for v in pattern_shifts.values()), default=0.0)

    boot_n = int(contract["frozen_gate"]["bootstrap_replicates"])
    rng = random.Random(2026081699)
    boot_tv = []
    for _ in range(boot_n):
        bd = {}
        for sid, vals in valid_by_source.items():
            if not vals:
                bd[sid] = {}
                continue
            sampled = [vals[rng.randrange(len(vals))]["validator_pattern"] for __ in range(len(vals))]
            bd[sid] = distribution(sampled)
        boot_tv.append(tv(mix_distributions(bd, original_w), mix_distributions(bd, split_w)))
    lower95 = percentile(boot_tv, 0.025)

    gate = contract["frozen_gate"]
    min_valid = min(v["contract_valid"] for v in generation_counts.values())
    checks = {
        "contract_valid_per_source": {"actual": min_valid, "required_min": int(gate["contract_valid_per_source_min"]), "pass": min_valid >= int(gate["contract_valid_per_source_min"])},
        "validator_pattern_tv": {"actual": pattern_tv, "required_min": float(gate["validator_pattern_tv_distance_min"]), "pass": pattern_tv >= float(gate["validator_pattern_tv_distance_min"])},
        "validator_pattern_tv_bootstrap_lower95": {"actual": lower95, "required_min": float(gate["validator_pattern_tv_bootstrap_lower95_min"]), "pass": lower95 >= float(gate["validator_pattern_tv_bootstrap_lower95_min"])},
        "max_single_pattern_shift": {"actual": max_shift, "required_min": float(gate["max_single_pattern_probability_shift_min"]), "pass": max_shift >= float(gate["max_single_pattern_probability_shift_min"])},
    }
    adjudication = adjudicate_dynamic_gate(checks)
    if qualification_only:
        qualification_pass = min_valid >= 1
        adjudication = {
            "decision": "RUNTIME_QUALIFICATION_PASS" if qualification_pass else "RUNTIME_QUALIFICATION_FAIL",
            "scientific_result_available": False,
            "primary_mechanism_positive": False,
            "protocol_valid_for_scientific_update": False,
            "qualification_pass": qualification_pass,
        }
    result = {
        "schema_version": "1.1",
        "experiment_id": contract["experiment_id"],
        "candidate_id": contract["candidate_id"],
        **adjudication,
        "generation_counts": generation_counts,
        "source_conditional_validator_pattern_distributions": pattern_dists,
        "source_conditional_tool_distributions": tool_dists,
        "arm_original_validator_pattern_distribution": p0,
        "arm_split_validator_pattern_distribution": p1,
        "validator_pattern_probability_shifts": dict(sorted(pattern_shifts.items(), key=lambda kv: -abs(kv[1]))),
        "validator_pattern_tv_distance": pattern_tv,
        "tool_name_tv_distance": tool_tv,
        "validator_pattern_tv_bootstrap_lower95": lower95,
        "validator_pattern_tv_bootstrap_upper95": percentile(boot_tv, 0.975),
        "max_single_pattern_probability_shift": max_shift,
        "checks": checks,
        "matched_replay": True,
        "arm_specific_model_generation": False,
        "training_steps": 0,
        "second_backbone": 0,
        "gpu_hours": (time.monotonic()-started)/3600.0,
        "paper_design_authorized": False,
        "method_authorized": False,
        "paper_claim_authorized": False,
        "runtime_authority": contract.get("runtime_authority", "EXPLORATORY_TRANSFORMERS_NOT_FAITHFUL_VLLM"),
        "enable_thinking": contract["proposer"].get("enable_thinking", "AUTHOR_CODE_DEFAULT"),
        "qualification_only": qualification_only,
        "next_action": (
            ("Run the unchanged frozen 24-per-source exploratory contrast." if adjudication["qualification_pass"] else "Repair runtime/parser only; do not update STRI belief.")
            if qualification_only
            else (
                "Invalidate this execution as an operationalization/proposer-qualification failure. Do not update STRI scientific belief; permit at most one independently reviewed operationalization repair without changing the frozen scientific contrast."
                if not adjudication["qualification_pass"]
                else (contract["next_if_positive"] if adjudication["primary_mechanism_positive"] else contract["next_if_negative"])
            )
        ),
    }
    atomic_json(output_dir / "result.json", result)
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--preflight-only", action="store_true")
    ap.add_argument("--qualification-only", action="store_true")
    args = ap.parse_args()
    contract = load_json(args.contract)
    if args.preflight_only:
        out = preflight(contract, args.output_dir)
        print(json.dumps({"preflight_pass": out["pass"], "validator_count": out["validator_count"], "prompts": out["source_prompts"]}, ensure_ascii=False))
    else:
        if args.qualification_only:
            contract = json.loads(json.dumps(contract))
            contract["proposer"]["samples_per_source_skill"] = int(contract["proposer"].get("qualification_samples_per_source_skill", 2))
            contract["frozen_gate"]["contract_valid_per_source_min"] = 1
            contract["frozen_gate"]["validator_pattern_tv_distance_min"] = 0.0
            contract["frozen_gate"]["validator_pattern_tv_bootstrap_lower95_min"] = 0.0
            contract["frozen_gate"]["max_single_pattern_probability_shift_min"] = 0.0
        out = run(contract, args.output_dir, qualification_only=args.qualification_only)
        print(json.dumps({"decision": out["decision"], "generation_counts": out["generation_counts"], "pattern_tv": out["validator_pattern_tv_distance"], "lower95": out["validator_pattern_tv_bootstrap_lower95"], "max_shift": out["max_single_pattern_probability_shift"], "checks": out["checks"]}, ensure_ascii=False))

if __name__ == "__main__":
    main()
