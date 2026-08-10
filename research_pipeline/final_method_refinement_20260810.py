from __future__ import annotations

import argparse
import concurrent.futures
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .ark_provider import ArkResponsesClient
from .config import PROJECT_ROOT

OUTPUT = PROJECT_ROOT / "generated" / "final-method-refinement-20260810.json"
BANK = PROJECT_ROOT / "generated" / "iclr-low-resource-ideas.json"
MODELS = ("deepseek-v4-pro", "kimi-k3", "doubao-seed-evolving", "glm-5.2")
IDEA_IDS = (
    "regression-gated-self-evolution",
    "compositional-update-compatibility",
    "lineage-aware-rollback",
    "outcome-equivalent-trajectory-contrast",
    "contradiction-preserving-consolidation",
    "retrieval-interference-auditor",
    "causally-verified-experience-admission",
    "local-counterexample-memory-repair",
    "memory-half-life",
    "self-label-confidence-flow",
    "evaluator-coadaptation-guard",
    "counterexample-generating-curriculum",
    "workflow-generalization-certificate",
    "workflow-branch-credit",
    "world-model-error-gated-learning",
    "irreversible-action-counterfactuals",
    "recovery-conditioned-experience",
)
BATCHES = (IDEA_IDS[:4], IDEA_IDS[4:9], IDEA_IDS[9:13], IDEA_IDS[13:])


def _en(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("en") or value.get("zh") or "")
    return str(value or "")


def load_dossiers() -> dict[str, dict[str, Any]]:
    payload = json.loads(BANK.read_text(encoding="utf-8"))
    by_id = {row["id"]: row for row in payload.get("passed_ideas") or []}
    out: dict[str, dict[str, Any]] = {}
    for idea_id in IDEA_IDS:
        row = by_id[idea_id]
        redesign = row.get("redesign_iteration") or {}
        out[idea_id] = {
            "idea_id": idea_id,
            "title": row.get("title"),
            "problem": _en(row.get("purpose")),
            "core_intuition": _en(row.get("core_intuition")),
            "current_mechanism": _en(row.get("core_idea")),
            "current_collision_boundary": _en(row.get("collision_boundary")),
            "current_strongest_baseline": _en(row.get("strongest_baseline")),
            "current_stop_condition": _en(row.get("stop_condition")),
            "current_redesign_verdict": redesign.get("verdict"),
            "current_redesign_summary": _en(redesign.get("summary")),
            "nearest_work": (row.get("nearest_work") or [])[:5],
        }
    return out


def tool_schema(batch_size: int) -> list[dict[str, Any]]:
    fields = {
        "idea_id": {"type": "string"},
        "recommendation": {"type": "string", "enum": ["keep-and-refine", "merge", "hold", "stop"]},
        "changed_assumption": {"type": "string"},
        "mechanism": {"type": "string"},
        "persistent_object": {"type": "string"},
        "learning_signal": {"type": "string"},
        "why_mechanism_matches_problem": {"type": "string"},
        "strongest_simplification": {"type": "string"},
        "why_not_reducible": {"type": "string"},
        "independent_truth": {"type": "string"},
        "offline_pre_p0_gate": {"type": "string"},
        "small_p0": {"type": "string"},
        "merge_or_stop_rule": {"type": "string"},
        "plain_language_intuition": {"type": "string"},
        "remaining_risk": {"type": "string"},
    }
    return [{
        "type": "function",
        "name": "submit_method_refinements",
        "description": "Submit final mechanism-level refinements for the supplied research ideas.",
        "parameters": {
            "type": "object",
            "properties": {
                "refinements": {
                    "type": "array",
                    "minItems": batch_size,
                    "maxItems": batch_size,
                    "items": {"type": "object", "properties": fields, "required": list(fields), "additionalProperties": False},
                }
            },
            "required": ["refinements"],
            "additionalProperties": False,
        },
    }]


def build_prompt(batch: tuple[str, ...], dossiers: dict[str, dict[str, Any]]) -> str:
    cases = [dossiers[idea_id] for idea_id in batch]
    return f"""Act as an independent ICLR method designer, not a copy editor. Refine only the supplied ideas.

Goal: find the smallest scientifically meaningful mechanism that solves the stated real problem and survives a strongest-simplification challenge. The result must be readable by a researcher who is not already familiar with the idea.

Hard rules:
1. Do not solve a method problem by merely adding more data, a larger benchmark, or a larger teacher model.
2. Prefer one clear learned/persistent object and one causal or independently verifiable learning signal.
3. The method must have a strongest matched simplification that receives the same observations, labels, replay/intervention budget, capacity, calls/tokens, optimization steps, and wall-clock wherever applicable.
4. Independent truth cannot be produced by the same learner/evaluator that is being updated.
5. Before GPU P0, propose an offline/CPU/trace-based gate that can expose target variation, method-baseline disagreement, representability, objective-claim alignment, or phenomenon reality when relevant.
6. If the idea is actually a component of a simpler parent, recommend merge. If its real-world premise is unverified, recommend hold. If no mechanism survives, recommend stop.
7. Do not invent literature or claim novelty. Current nearest-work text is context only; novelty is checked separately with primary sources.
8. Explain the core intuition in plain language, then give a concrete mechanism. Avoid abstract renaming.
9. Each refinement must change the method materially, not just the evaluation protocol or wording.
10. Call submit_method_refinements exactly once and return no prose outside the tool call.

Cases:
{json.dumps(cases, ensure_ascii=False, indent=2)}
"""


def validate(batch: tuple[str, ...], payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    rows = payload.get("refinements")
    if not isinstance(rows, list) or len(rows) != len(batch):
        return [f"expected {len(batch)} refinements"]
    ids = [row.get("idea_id") for row in rows if isinstance(row, dict)]
    if set(ids) != set(batch):
        errors.append("idea ids do not match batch")
    required = (
        "changed_assumption", "mechanism", "persistent_object", "learning_signal",
        "why_mechanism_matches_problem", "strongest_simplification", "why_not_reducible",
        "independent_truth", "offline_pre_p0_gate", "small_p0", "merge_or_stop_rule",
        "plain_language_intuition", "remaining_risk",
    )
    for row in rows:
        if not isinstance(row, dict):
            errors.append("non-object refinement")
            continue
        for key in required:
            if len(str(row.get(key) or "").strip()) < 18:
                errors.append(f"{row.get('idea_id')} weak/missing {key}")
    return errors


def run_one(model: str, batch_index: int, batch: tuple[str, ...], dossiers: dict[str, dict[str, Any]]) -> dict[str, Any]:
    client = ArkResponsesClient()
    try:
        response = client.respond(
            build_prompt(batch, dossiers), model=model, max_output_tokens=6500,
            tools=tool_schema(len(batch)), thinking="disabled",
        )
        calls = [call for call in response.get("function_calls") or [] if call.get("name") == "submit_method_refinements"]
        if len(calls) != 1:
            raise ValueError(f"expected one submit_method_refinements call, got {len(calls)}")
        parsed = json.loads(calls[0].get("arguments") or "{}")
        errors = validate(batch, parsed)
        return {
            "model": model,
            "batch_index": batch_index,
            "idea_ids": list(batch),
            "valid": not errors,
            "validation_errors": errors,
            "usage": response.get("usage") or {},
            "resolved_model": response.get("resolved_model"),
            "response": parsed,
        }
    except Exception as error:
        return {
            "model": model, "batch_index": batch_index, "idea_ids": list(batch),
            "valid": False, "validation_errors": [str(error)], "response": {},
        }


def run(models: list[str], max_workers: int = 2) -> dict[str, Any]:
    dossiers = load_dossiers()
    jobs = [(model, index, batch) for model in models for index, batch in enumerate(BATCHES)]
    rows: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(run_one, model, index, batch, dossiers): (model, index) for model, index, batch in jobs}
        for future in concurrent.futures.as_completed(futures):
            rows.append(future.result())
    model_order = {model: idx for idx, model in enumerate(models)}
    rows.sort(key=lambda row: (model_order.get(row["model"], 999), row["batch_index"]))
    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "models": models,
        "idea_ids": list(IDEA_IDS),
        "summary": {
            "jobs": len(rows),
            "valid_jobs": sum(row.get("valid") is True for row in rows),
            "invalid_jobs": sum(row.get("valid") is not True for row in rows),
            "ideas": len(IDEA_IDS),
            "model_votes_per_idea": len(models),
        },
        "dossiers": dossiers,
        "results": rows,
    }


def merge_incremental(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    previous: dict[str, Any] = {}
    if path.exists():
        try:
            previous = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            previous = {}
    rows = {
        (str(row.get("model")), int(row.get("batch_index", -1))): row
        for row in previous.get("results") or [] if isinstance(row, dict)
    }
    for row in payload.get("results") or []:
        rows[(str(row.get("model")), int(row.get("batch_index", -1)))] = row
    models = list(dict.fromkeys([*(previous.get("models") or []), *(payload.get("models") or [])]))
    model_order = {model: idx for idx, model in enumerate(models)}
    merged_rows = sorted(rows.values(), key=lambda row: (model_order.get(str(row.get("model")), 999), int(row.get("batch_index", -1))))
    merged = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "models": models,
        "idea_ids": list(IDEA_IDS),
        "summary": {
            "jobs": len(merged_rows),
            "valid_jobs": sum(row.get("valid") is True for row in merged_rows),
            "invalid_jobs": sum(row.get("valid") is not True for row in merged_rows),
            "ideas": len(IDEA_IDS),
            "model_votes_per_idea": len(models),
        },
        "dossiers": payload.get("dossiers") or previous.get("dossiers") or load_dossiers(),
        "results": merged_rows,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return merged


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="*", default=list(MODELS))
    parser.add_argument("--max-workers", type=int, default=2)
    parser.add_argument("--model", default=None)
    parser.add_argument("--batch-index", type=int, default=None)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.model is not None or args.batch_index is not None:
        if args.model is None or args.batch_index is None:
            raise SystemExit("--model and --batch-index must be supplied together")
        if args.batch_index < 0 or args.batch_index >= len(BATCHES):
            raise SystemExit("invalid --batch-index")
        dossiers = load_dossiers()
        row = run_one(args.model, args.batch_index, BATCHES[args.batch_index], dossiers)
        payload = {"models": [args.model], "dossiers": dossiers, "results": [row]}
        merged = merge_incremental(args.output, payload)
        print(args.model, "batch", args.batch_index, "valid=" + str(row.get("valid")), row.get("validation_errors") or "")
        print(json.dumps(merged["summary"], ensure_ascii=False))
        return 0 if row.get("valid") else 2
    payload = run(args.models, max_workers=args.max_workers)
    merged = merge_incremental(args.output, payload)
    print(json.dumps(merged["summary"], ensure_ascii=False))
    for row in payload["results"]:
        print(row["model"], "batch", row["batch_index"], "valid=" + str(row["valid"]), row.get("validation_errors") or "")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
