from __future__ import annotations

import argparse
import hashlib
import importlib.resources
import json
import os
import tempfile
from pathlib import Path
from typing import Any

EXPECTED_WALT_CONFIG_SHA = "d25e83078ec728adc82bd43871338a24a3907e101b5a5fdb1ae81bb7f72f36a6"
MAX_STEPS = 30
EPISODES_PER_TASK = 4


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def normalize_eval(ev: Any) -> Any:
    if not isinstance(ev, dict):
        return ev
    out = json.loads(json.dumps(ev))
    refs = out.get("reference_answers")
    if isinstance(refs, dict) and "fuzzy_match" in refs:
        value = refs["fuzzy_match"]
        if isinstance(value, str):
            refs["fuzzy_match"] = [value]
    return out


def semantic_config_equal(a: dict[str, Any], b: dict[str, Any]) -> bool:
    fields = ("task_id", "intent_template_id", "intent", "sites", "start_url", "geolocation")
    if any(a.get(k) != b.get(k) for k in fields):
        return False
    return normalize_eval(a.get("eval")) == normalize_eval(b.get("eval"))


def build_preflight(candidate: dict[str, Any], walt_configs: list[dict[str, Any]]) -> dict[str, Any]:
    # libwebarena asserts that all site URL variables are non-empty at import
    # time, even though this preflight constructs evaluator objects only and
    # never sends a request. Use loopback placeholders solely to satisfy that
    # import-side effect; the selected R19 task configs are separately required
    # to be Shopping-only, and no evaluator is invoked below.
    import_only_env = {
        "REDDIT": "http://127.0.0.1:9999",
        "SHOPPING": "http://127.0.0.1:7770",
        "SHOPPING_ADMIN": "http://127.0.0.1:7780/admin",
        "GITLAB": "http://127.0.0.1:8023",
        "WIKIPEDIA": "http://127.0.0.1:8888",
        "MAP": "http://127.0.0.1:3000",
        "HOMEPAGE": "http://127.0.0.1:4399",
    }
    for key, value in import_only_env.items():
        os.environ.setdefault(key, value)
    import webarena
    from webarena.evaluation_harness.evaluators import evaluator_router

    installed_path = importlib.resources.files(webarena).joinpath("test.raw.json")
    installed_bytes = installed_path.read_bytes()
    installed_configs = json.loads(installed_bytes)
    a = {str(x["task_id"]): x for x in walt_configs}
    b = {str(x["task_id"]): x for x in installed_configs}

    rows: list[dict[str, Any]] = []
    fuzzy_tasks: list[str] = []
    schema_normalized_tasks: list[str] = []
    for unit in candidate["cohort"]:
        tid = str(unit["r19_downstream_task_id"])
        if tid not in a or tid not in b:
            raise RuntimeError(f"task {tid} missing from WALT or installed WebArena config")
        wa, ib = a[tid], b[tid]
        raw_equal = wa == ib
        semantic_equal = semantic_config_equal(wa, ib)
        if not semantic_equal:
            raise RuntimeError(f"task {tid} WALT/installed WebArena semantic config mismatch")
        if not raw_equal:
            schema_normalized_tasks.append(tid)

        ev = ib.get("eval") or {}
        refs = ev.get("reference_answers") or {}
        fuzzy = isinstance(refs, dict) and "fuzzy_match" in refs
        if fuzzy:
            fuzzy_tasks.append(tid)

        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json") as f:
            json.dump(ib, f)
            f.flush()
            evaluator = evaluator_router(f.name)
            evaluator_class = type(evaluator).__name__
        rows.append(
            {
                "task_id": tid,
                "sites": ib.get("sites"),
                "eval_types": ev.get("eval_types"),
                "reference_answer_keys": sorted(refs.keys()) if isinstance(refs, dict) else [],
                "potential_llm_fuzzy_evaluator": fuzzy,
                "walt_vs_installed_raw_equal": raw_equal,
                "walt_vs_installed_semantic_equal_after_fuzzy_scalar_list_normalization": semantic_equal,
                "native_evaluator_constructed": True,
                "native_evaluator_class": evaluator_class,
                "native_evaluator_called": False,
            }
        )

    if len(rows) != 35:
        raise RuntimeError("R19 evaluator preflight expected 35 tasks")
    if any(x["sites"] != ["shopping"] for x in rows):
        raise RuntimeError("non-Shopping task in R19 evaluator preflight")
    if len(fuzzy_tasks) != 5:
        raise RuntimeError(f"unexpected fuzzy-evaluator count: {len(fuzzy_tasks)}")

    max_fuzzy_calls = len(fuzzy_tasks) * EPISODES_PER_TASK * MAX_STEPS
    return {
        "schema_version": "1.0",
        "paper_id": "D2-PAPER-FAILURE-MEMORY-PROVENANCE",
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-L2B-R19-EVALUATOR-PREFLIGHT",
        "recorded_date": "2026-08-24",
        "status": "R19_35_OF_35_NATIVE_EVALUATORS_CONSTRUCTED_ZERO_CALL",
        "role": "ZERO_MODEL_ZERO_ACTION_PRE_OUTCOME_EVALUATOR_TRANSPORT_AUDIT",
        "installed_webarena_config": {
            "path": str(installed_path),
            "sha256": sha256_bytes(installed_bytes),
            "tasks_total": len(installed_configs),
        },
        "walt_frozen_config": {
            "sha256": EXPECTED_WALT_CONFIG_SHA,
            "semantic_comparison_fields": ["task_id", "intent_template_id", "intent", "sites", "start_url", "geolocation", "eval"],
            "normalization": "Only reference_answers.fuzzy_match scalar-versus-singleton-list is normalized. No answer string, note, URL, program, task intent, site, or evaluator type may differ.",
            "schema_normalized_task_ids": schema_normalized_tasks,
        },
        "import_only_environment": {
            "purpose": "Satisfy libwebarena import-time non-empty URL assertions only; evaluator construction sends no network request.",
            "loopback_placeholders": import_only_env,
            "network_requests_executed": False,
        },
        "summary": {
            "R19_tasks": len(rows),
            "shopping_only": True,
            "native_evaluators_constructed": len(rows),
            "native_evaluators_called": 0,
            "semantic_config_matches": len(rows),
            "potential_llm_fuzzy_evaluator_tasks": len(fuzzy_tasks),
            "potential_llm_fuzzy_evaluator_task_ids": fuzzy_tasks,
            "deterministic_or_non_fuzzy_evaluator_tasks": len(rows) - len(fuzzy_tasks),
            "maximum_fuzzy_evaluator_model_calls_under_4_episodes_x_30_steps": max_fuzzy_calls,
        },
        "tasks": rows,
        "support_rule": {
            "gpt_4_1106_preview_alias_must_be_manifest_identical_to_executor_before_future_execution": True,
            "fuzzy_evaluator_calls_are_evaluator_calls_not_independent_samples": True,
            "fuzzy_evaluator_call_budget_must_be_separate_from_agent_completion_budget": True,
            "no_native_evaluator_was_called_in_this_preflight": True,
        },
        "scientific_verdict": "NO_VERDICT_EVALUATOR_PREFLIGHT_ONLY",
        "authority": {
            "scientific": False,
            "experiment": False,
            "model_calls": False,
            "browser_actions": False,
            "evaluator_calls": False,
            "submission": False,
        },
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--candidate", type=Path, required=True)
    p.add_argument("--walt-config", type=Path, required=True)
    p.add_argument("--output", type=Path, default=Path("generated/d2-failure-memory-provenance-l2b-r19-evaluator-preflight.json"))
    args = p.parse_args()
    if sha256_file(args.walt_config) != EXPECTED_WALT_CONFIG_SHA:
        raise RuntimeError("WALT config digest mismatch")
    candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
    configs = json.loads(args.walt_config.read_text(encoding="utf-8"))
    receipt = build_preflight(candidate, configs)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": receipt["status"],
        "tasks": receipt["summary"]["R19_tasks"],
        "fuzzy_tasks": receipt["summary"]["potential_llm_fuzzy_evaluator_tasks"],
        "max_fuzzy_calls": receipt["summary"]["maximum_fuzzy_evaluator_model_calls_under_4_episodes_x_30_steps"],
        "evaluator_calls": receipt["summary"]["native_evaluators_called"],
    }))


if __name__ == "__main__":
    main()
