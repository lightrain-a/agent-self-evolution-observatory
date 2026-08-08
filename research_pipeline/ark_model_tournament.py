from __future__ import annotations

import argparse
import concurrent.futures
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .ark_provider import ARK_MODELS, ArkResponsesClient
from .config import PROJECT_ROOT
from .r3_final_audit import build_r3_final_audit

DEFAULT_JSON = PROJECT_ROOT / "generated" / "ark-model-tournament.json"
REPRESENTATIVE_IDS = (
    "regression-gated-self-evolution",
    "certified-out-of-span-interaction-inverter-v53",
)
SOURCE_BANKS = (
    (PROJECT_ROOT / "generated" / "iclr-low-resource-ideas.json", "passed_ideas"),
    (PROJECT_ROOT / "generated" / "idea-discovery-v4.json", "all_candidates"),
    (PROJECT_ROOT / "generated" / "idea-discovery-v5.json", "all_candidates"),
    (PROJECT_ROOT / "generated" / "idea-discovery-v51.json", "children"),
    (PROJECT_ROOT / "generated" / "idea-discovery-v52.json", "children"),
    (PROJECT_ROOT / "generated" / "idea-discovery-v53.json", "children"),
)


def _load_records() -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for path, key in SOURCE_BANKS:
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload.get(key) or []
        if key == "all_candidates" and not rows:
            rows = payload.get("finalists") or payload.get("review_ranked_finalists") or []
        for row in rows:
            if isinstance(row, dict) and row.get("id"):
                records.setdefault(row["id"], row)
    return records


def _text(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("en") or value.get("zh") or "")
    return str(value or "")


def _compact_record(record: dict[str, Any]) -> dict[str, Any]:
    review = (record.get("external_reviews") or [{}])[-1]
    nearest = record.get("nearest_work") or (review.get("direct_collision") or {}).get("closest_work") or []
    return {
        "title": record.get("title"),
        "problem": _text(record.get("purpose") or record.get("problem") or record.get("real_problem")),
        "current_mechanism": _text(record.get("core_idea") or record.get("exact_mechanism") or record.get("method_logic")),
        "persistent_object": _text(record.get("persistent_update_object") or record.get("update_surface")),
        "learning_signal": _text(record.get("learning_signal")),
        "independent_truth": _text(record.get("independent_ground_truth") or record.get("decisive_metric") or record.get("hypothesis")),
        "strongest_baseline": _text(record.get("strongest_baseline") or record.get("simplest_baseline") or review.get("strongest_baseline")),
        "current_pilot": _text(record.get("decisive_pilot") or record.get("pilot") or review.get("decisive_pilot")),
        "stop_condition": _text(record.get("stop_condition") or review.get("stop_rule")),
        "nearest_work": nearest[:5],
    }


def build_prompt() -> str:
    records = _load_records()
    r3 = {row["idea_id"]: row for row in build_r3_final_audit()["ideas"]}
    cases = []
    for idea_id in REPRESENTATIVE_IDS:
        cases.append({
            "idea_id": idea_id,
            "dossier": _compact_record(records.get(idea_id, {})),
            "r3_final_finding": r3[idea_id]["finding"],
            "r3_required_action": r3[idea_id]["required_action"],
        })
    schema = {
        "model_role": "repair-designer",
        "repairs": [{
            "idea_id": "exact id",
            "child_title": "specific repaired child title",
            "material_change": "what changes in the mechanism, not just the experiment",
            "why_not_reducible": "why the strongest simpler method cannot implement the same learned object",
            "persistent_frozen_object": "state that is learned once and reused without hidden relearning",
            "strongest_matched_baseline": "the baseline most likely to erase the contribution",
            "shared_information_budget": "exactly what data/labels/traces/calls/tokens/optimization/wall-clock are equalized",
            "independent_truth": "truth source not produced by the repair learner or its judge",
            "decisive_pilot": "one crossed or factorial experiment that attributes the surviving mechanism",
            "stop_rule": "condition that kills or collapses the claim",
            "surviving_claim": "narrow claim allowed if the pilot wins",
            "remaining_risk": "the strongest unresolved concern after repair",
        }],
    }
    return f"""You are designing material repairs for a strict ICLR final pre-advisor audit.

The cases below deliberately expose two hard failure modes: reducibility to a simpler gate and formal-certificate overreach. Do not merely restate the reviewer request. Produce the smallest mechanism change that actually closes it.

Rules:
1. Do not add generic modules or complexity as camouflage.
2. The learned object must persist after the evolution context is removed.
3. The strongest simpler baseline gets the same observations, labels, intervention data, capacity, calls, tokens, optimization steps, and wall-clock wherever applicable.
4. Independent truth cannot come from the same learned scorer/judge.
5. The decisive experiment must identify the claimed mechanism, preferably with a crossed/factorial intervention.
6. If a case cannot be repaired without becoming a different problem, say so in `remaining_risk` and keep the surviving claim narrow.
7. Do not invent new literature citations; use only the supplied nearest-work context.
8. Call the `submit_repairs` function exactly once. Do not answer in prose.

Expected content shape:
{json.dumps(schema, ensure_ascii=False, indent=2)}

Cases:
{json.dumps(cases, ensure_ascii=False, indent=2)}
"""


def _validate(payload: dict[str, Any]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    rows = payload.get("repairs")
    if not isinstance(rows, list) or len(rows) != len(REPRESENTATIVE_IDS):
        errors.append("must return four repairs")
        return False, errors
    ids = [row.get("idea_id") for row in rows if isinstance(row, dict)]
    if set(ids) != set(REPRESENTATIVE_IDS):
        errors.append("repair ids do not match representative ids")
    required = (
        "material_change", "why_not_reducible", "persistent_frozen_object", "strongest_matched_baseline",
        "shared_information_budget", "independent_truth", "decisive_pilot", "stop_rule", "surviving_claim", "remaining_risk",
    )
    for row in rows:
        if not isinstance(row, dict):
            errors.append("non-object repair")
            continue
        for key in required:
            if len(str(row.get(key) or "").strip()) < 24:
                errors.append(f"{row.get('idea_id')} has weak/missing {key}")
    return not errors, errors


def _submit_tool() -> list[dict[str, Any]]:
    repair_properties = {
        "idea_id": {"type": "string"},
        "child_title": {"type": "string"},
        "material_change": {"type": "string"},
        "why_not_reducible": {"type": "string"},
        "persistent_frozen_object": {"type": "string"},
        "strongest_matched_baseline": {"type": "string"},
        "shared_information_budget": {"type": "string"},
        "independent_truth": {"type": "string"},
        "decisive_pilot": {"type": "string"},
        "stop_rule": {"type": "string"},
        "surviving_claim": {"type": "string"},
        "remaining_risk": {"type": "string"},
    }
    return [{
        "type": "function",
        "name": "submit_repairs",
        "description": "Submit the material ICLR idea repairs.",
        "parameters": {
            "type": "object",
            "properties": {
                "model_role": {"type": "string"},
                "repairs": {
                    "type": "array",
                    "minItems": len(REPRESENTATIVE_IDS),
                    "maxItems": len(REPRESENTATIVE_IDS),
                    "items": {"type": "object", "properties": repair_properties, "required": list(repair_properties), "additionalProperties": False},
                },
            },
            "required": ["model_role", "repairs"],
            "additionalProperties": False,
        },
    }]


def run(models: list[str] | None = None, *, max_workers: int = 4) -> dict[str, Any]:
    selected = models or list(ARK_MODELS)
    prompt = build_prompt()
    tools = _submit_tool()

    def one(model: str) -> dict[str, Any]:
        client = ArkResponsesClient()
        try:
            response = client.respond(prompt, model=model, max_output_tokens=8000, tools=tools, thinking="disabled")
            calls = [call for call in response.get("function_calls", []) if call.get("name") == "submit_repairs"]
            if len(calls) != 1:
                raise ValueError(f"expected one submit_repairs call, got {len(calls)}")
            parsed = json.loads(calls[0].get("arguments") or "{}")
            valid, errors = _validate(parsed)
            return {
                "requested_model": model,
                "resolved_model": response["resolved_model"],
                "valid": valid,
                "validation_errors": errors,
                "usage": response.get("usage") or {},
                "response": parsed,
            }
        except Exception as error:
            return {"requested_model": model, "valid": False, "validation_errors": [str(error)], "response": {}}

    results: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(one, model): model for model in selected}
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    order = {model: index for index, model in enumerate(selected)}
    results.sort(key=lambda row: order.get(row["requested_model"], 10_000))
    payload = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "benchmark_ids": list(REPRESENTATIVE_IDS),
        "models": selected,
        "summary": {
            "tested": len(results),
            "valid": sum(row.get("valid") is True for row in results),
            "invalid": sum(row.get("valid") is not True for row in results),
        },
        "results": results,
    }
    return payload


def write(payload: dict[str, Any], path: Path = DEFAULT_JSON) -> None:
    merged = payload
    if path.exists():
        try:
            previous = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            previous = {}
        prior_rows = {row.get("requested_model"): row for row in previous.get("results") or [] if isinstance(row, dict) and row.get("requested_model")}
        for row in payload.get("results") or []:
            prior_rows[row.get("requested_model")] = row
        model_order = list(dict.fromkeys([*(previous.get("models") or []), *(payload.get("models") or [])]))
        rows = [prior_rows[model] for model in model_order if model in prior_rows]
        merged = {
            **payload,
            "models": model_order,
            "summary": {
                "tested": len(rows),
                "valid": sum(row.get("valid") is True for row in rows),
                "invalid": sum(row.get("valid") is not True for row in rows),
            },
            "results": rows,
        }
    path.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="*", default=None)
    parser.add_argument("--max-workers", type=int, default=4)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    args = parser.parse_args()
    payload = run(args.models, max_workers=args.max_workers)
    write(payload, args.json)
    print(json.dumps(payload["summary"], ensure_ascii=False))
    for row in payload["results"]:
        usage = row.get("usage") or {}
        print(row["requested_model"], "=>", row.get("resolved_model"), "valid=" + str(row.get("valid")), "tokens=" + str(usage.get("total_tokens", "?")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
