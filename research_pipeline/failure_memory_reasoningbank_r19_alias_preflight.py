from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.request
from pathlib import Path
from typing import Any

EXPECTED_EXECUTOR_MANIFEST = "5bce411d829007ce344871ae10ea7f02f91d86c932617a7f982e2380bbb1c216"
EXPECTED_TAGS = {
    "b1-qwen25-32b-l2b-executor:latest",
    "gpt-4:latest",
    "gpt-4-1106-preview:latest",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def get_json(url: str) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=5) as r:
        return json.load(r)


def build_preflight(ollama_base: str, helper_functions_py: Path) -> dict[str, Any]:
    import tiktoken

    tags_payload = get_json(ollama_base.rstrip("/") + "/api/tags")
    tags = {
        str(x["name"]): str(x["digest"])
        for x in tags_payload.get("models", [])
        if str(x.get("name")) in EXPECTED_TAGS
    }
    if set(tags) != EXPECTED_TAGS:
        raise RuntimeError(f"required executor/evaluator aliases missing: {EXPECTED_TAGS - set(tags)}")
    if len(set(tags.values())) != 1 or next(iter(tags.values())) != EXPECTED_EXECUTOR_MANIFEST:
        raise RuntimeError("alias manifest digest mismatch")

    v1 = get_json(ollama_base.rstrip("/") + "/v1/models")
    model_ids = sorted(str(x["id"]) for x in v1.get("data", []))
    for tag in EXPECTED_TAGS:
        if tag not in model_ids:
            raise RuntimeError(f"OpenAI-compatible registry missing {tag}")

    tokenizer_rows = []
    for model in ("gpt-4", "gpt-4-1106-preview"):
        enc = tiktoken.encoding_for_model(model)
        tokenizer_rows.append({"model_name": model, "encoding": enc.name, "lookup_pass": True})

    text = helper_functions_py.read_text(encoding="utf-8")
    matches = re.findall(r"gpt-4-1106-preview", text)
    if not matches:
        raise RuntimeError("installed WebArena helper no longer references gpt-4-1106-preview")

    return {
        "schema_version": "1.0",
        "paper_id": "D2-PAPER-FAILURE-MEMORY-PROVENANCE",
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-L2B-R19-ALIAS-TOKENIZER-PREFLIGHT",
        "recorded_date": "2026-08-24",
        "status": "R19_AGENT_EVALUATOR_ALIASES_AND_TOKENIZERS_PREFLIGHT_PASS_ZERO_COMPLETION",
        "role": "ZERO_COMPLETION_TRANSPORT_PREFLIGHT",
        "ollama_registry": {
            "base": ollama_base,
            "aliases": tags,
            "all_required_aliases_present": True,
            "all_required_aliases_manifest_identical": True,
            "executor_manifest_digest": "sha256:" + EXPECTED_EXECUTOR_MANIFEST,
            "openai_v1_models_checked": True,
            "completion_endpoint_called": False,
            "generation_endpoint_called": False,
        },
        "tokenizer": {
            "rows": tokenizer_rows,
            "all_lookup_pass": True,
            "tokenizer_only_no_model_call": True,
        },
        "installed_webarena_evaluator_source": {
            "helper_functions_py": str(helper_functions_py),
            "sha256": sha256_file(helper_functions_py),
            "gpt_4_1106_preview_literal_count": len(matches),
            "hardcoded_evaluator_alias_preflighted": True,
        },
        "future_execution_precondition": {
            "repeat_registry_and_tokenizer_preflight_immediately_before_any_new_benchmark_episode": True,
            "after_new_execution_authority_but_before_benchmark_outcome_run_two_fixed_synthetic_nonbenchmark_completion_smokes": [
                "agent alias gpt-4",
                "evaluator alias gpt-4-1106-preview",
            ],
            "synthetic_completion_smokes_executed_now": False,
            "reason": "R18c demonstrated that registry/tokenizer checks alone do not prove every downstream model-name transport path. A new experiment should consume two explicitly authorized nonbenchmark support completions before scientific exposure.",
        },
        "scientific_verdict": "NO_VERDICT_TRANSPORT_PREFLIGHT_ONLY",
        "authority": {
            "scientific": False,
            "experiment": False,
            "model_completions": False,
            "browser_actions": False,
            "evaluator_calls": False,
            "submission": False,
        },
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--ollama-base", required=True)
    p.add_argument("--helper-functions-py", type=Path, required=True)
    p.add_argument("--output", type=Path, default=Path("generated/d2-failure-memory-provenance-l2b-r19-alias-preflight.json"))
    args = p.parse_args()
    receipt = build_preflight(args.ollama_base, args.helper_functions_py)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": receipt["status"],
        "aliases": receipt["ollama_registry"]["aliases"],
        "tokenizers": receipt["tokenizer"]["rows"],
        "completion_called": receipt["ollama_registry"]["completion_endpoint_called"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
