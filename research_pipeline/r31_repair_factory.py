from __future__ import annotations

import argparse
import concurrent.futures
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .ark_provider import ArkResponsesClient
from .config import PROJECT_ROOT
from .r3_final_audit import build_r3_final_audit

DEFAULT_JSON = PROJECT_ROOT / "generated" / "r31-repair-candidates.json"
GENERATOR_MODELS = ("glm-5.2", "kimi-k3", "deepseek-v4-pro")
CRITIC_MODEL = "doubao-seed-evolving"
SOURCE_BANKS = (
    (PROJECT_ROOT / "generated" / "iclr-low-resource-ideas.json", "passed_ideas"),
    (PROJECT_ROOT / "generated" / "idea-discovery-v4.json", "all_candidates"),
    (PROJECT_ROOT / "generated" / "idea-discovery-v5.json", "all_candidates"),
    (PROJECT_ROOT / "generated" / "idea-discovery-v51.json", "children"),
    (PROJECT_ROOT / "generated" / "idea-discovery-v52.json", "children"),
    (PROJECT_ROOT / "generated" / "idea-discovery-v53.json", "children"),
)


def _text(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("en") or value.get("zh") or "")
    return str(value or "")


def _records() -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for path, key in SOURCE_BANKS:
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload.get(key) or []
        if key == "all_candidates" and not rows:
            rows = payload.get("finalists") or payload.get("review_ranked_finalists") or []
        for row in rows:
            if isinstance(row, dict) and row.get("id"):
                out.setdefault(row["id"], row)
    return out


def _dossier(idea_id: str, record: dict[str, Any], r3: dict[str, Any]) -> dict[str, Any]:
    review = (record.get("external_reviews") or [{}])[-1]
    direct = review.get("direct_collision") or {}
    return {
        "idea_id": idea_id,
        "title": record.get("title"),
        "problem": _text(record.get("purpose") or record.get("problem") or record.get("real_problem")),
        "current_core_idea": _text(record.get("core_idea") or record.get("exact_mechanism") or record.get("method_logic")),
        "current_persistent_object": _text(record.get("persistent_update_object") or record.get("update_surface")),
        "current_learning_signal": _text(record.get("learning_signal")),
        "current_independent_truth": _text(record.get("independent_ground_truth") or record.get("decisive_metric") or record.get("hypothesis")),
        "current_strongest_baseline": _text(record.get("strongest_baseline") or record.get("simplest_baseline") or review.get("strongest_baseline")),
        "current_pilot": _text(record.get("decisive_pilot") or record.get("pilot") or review.get("decisive_pilot")),
        "current_stop": _text(record.get("stop_condition") or review.get("stop_rule")),
        "nearest_work": (record.get("nearest_work") or direct.get("closest_work") or [])[:5],
        "r3_finding": r3["finding"],
        "r3_required_action": r3["required_action"],
    }


def repair_tool(count: int) -> list[dict[str, Any]]:
    fields = {
        "idea_id": {"type": "string"},
        "child_title": {"type": "string"},
        "material_change": {"type": "string"},
        "repaired_mechanism": {"type": "string"},
        "persistent_frozen_object": {"type": "string"},
        "learning_signal": {"type": "string"},
        "independent_truth": {"type": "string"},
        "strongest_matched_baseline": {"type": "string"},
        "shared_information_budget": {"type": "string"},
        "decisive_pilot": {"type": "string"},
        "stop_rule": {"type": "string"},
        "surviving_claim": {"type": "string"},
        "why_r3_boundary_is_closed": {"type": "string"},
        "remaining_risk": {"type": "string"},
    }
    return [{
        "type": "function",
        "name": "submit_repairs",
        "description": "Submit material R3.1 repairs.",
        "parameters": {
            "type": "object",
            "properties": {
                "repairs": {
                    "type": "array",
                    "minItems": count,
                    "maxItems": count,
                    "items": {"type": "object", "properties": fields, "required": list(fields), "additionalProperties": False},
                }
            },
            "required": ["repairs"],
            "additionalProperties": False,
        },
    }]


def build_prompt(cases: list[dict[str, Any]]) -> str:
    return f"""Act as a strict ICLR method designer repairing ideas after a FINAL PRE-ADVISOR R3 audit.

Each supplied idea had exactly one material boundary in R3. Produce the smallest R3.1 child that closes that boundary without drifting to a different problem. Do not reward the parent and do not preserve a mechanism merely for lineage.

Hard rules:
- Make a material mechanism change when R3 says the mechanism is not identifiable; do not repair only prose.
- Give the strongest simplification exactly the same observations, labels, traces, intervention outcomes, model capacity, calls, tokens, optimizer/minibatches/steps, and wall-clock wherever meaningful.
- A persistent learned object must be frozen before held-out evaluation and reused without hidden relearning.
- Independent truth must come from execution/programmatic/external truth, not the same learned scorer or judge.
- Prefer a crossed/factorial decisive pilot that isolates the claimed factor or interaction.
- If the simpler baseline can represent the same function, do not falsely claim representational impossibility; the surviving claim must be an empirically falsifiable inductive-bias/efficiency/transfer claim or the idea should narrow.
- Preserve the original real problem and page-facing importance unless the R3 repair logically requires narrowing.
- Do not invent new paper citations. Nearest work is evidence context only.
- Call `submit_repairs` exactly once and do not emit prose.

Cases:
{json.dumps(cases, ensure_ascii=False, indent=2)}
"""


def _load_existing(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": "1.0", "generated_at": None, "generator_models": list(GENERATOR_MODELS), "candidates": {}}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"schema_version": "1.0", "generated_at": None, "generator_models": list(GENERATOR_MODELS), "candidates": {}}
    payload.setdefault("candidates", {})
    return payload


def _write(payload: dict[str, Any], path: Path = DEFAULT_JSON) -> None:
    payload["generated_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _validate(rows: list[dict[str, Any]], expected_ids: list[str]) -> None:
    if len(rows) != len(expected_ids) or {row.get("idea_id") for row in rows} != set(expected_ids):
        raise ValueError("model repair ids do not match requested ids")
    for row in rows:
        for key in ("material_change", "repaired_mechanism", "persistent_frozen_object", "strongest_matched_baseline", "decisive_pilot", "stop_rule", "why_r3_boundary_is_closed"):
            if len(str(row.get(key) or "").strip()) < 30:
                raise ValueError(f"weak field {key} for {row.get('idea_id')}")


def generate(*, batch_size: int = 4, models: tuple[str, ...] = GENERATOR_MODELS, max_workers: int = 3, output: Path = DEFAULT_JSON) -> dict[str, Any]:
    r3_rows = [row for row in build_r3_final_audit()["ideas"] if row["verdict"] == "revise"]
    r3_by_id = {row["idea_id"]: row for row in r3_rows}
    records = _records()
    ids = [row["idea_id"] for row in r3_rows]
    store = _load_existing(output)
    store["generator_models"] = list(dict.fromkeys([*(store.get("generator_models") or []), *models]))
    candidates = store.setdefault("candidates", {})

    batches = [ids[index:index + batch_size] for index in range(0, len(ids), batch_size)]
    jobs: list[tuple[str, list[str]]] = []
    for model in models:
        for batch in batches:
            if all(model in (candidates.get(idea_id) or {}) for idea_id in batch):
                continue
            jobs.append((model, batch))

    def one(job: tuple[str, list[str]]) -> tuple[str, list[str], list[dict[str, Any]], dict[str, Any]]:
        model, batch = job
        cases = [_dossier(idea_id, records.get(idea_id, {}), r3_by_id[idea_id]) for idea_id in batch]
        client = ArkResponsesClient()
        response = client.respond(build_prompt(cases), model=model, max_output_tokens=12000, tools=repair_tool(len(batch)), thinking="disabled")
        calls = [call for call in response.get("function_calls", []) if call.get("name") == "submit_repairs"]
        if len(calls) != 1:
            raise ValueError(f"{model}: expected one submit_repairs function call, got {len(calls)}")
        rows = json.loads(calls[0].get("arguments") or "{}").get("repairs") or []
        _validate(rows, batch)
        return model, batch, rows, response.get("usage") or {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        future_map = {pool.submit(one, job): job for job in jobs}
        for future in concurrent.futures.as_completed(future_map):
            model, batch = future_map[future]
            try:
                resolved_model, _, rows, usage = future.result()
                for row in rows:
                    idea_id = row["idea_id"]
                    candidates.setdefault(idea_id, {})[resolved_model] = {"repair": row, "usage": usage}
            except Exception as error:
                store.setdefault("errors", []).append({"model": model, "ids": batch, "error": str(error)})
            _write(store, output)

    store["summary"] = {
        "r3_revise_ideas": len(ids),
        "models": len(models),
        "candidate_repairs": sum(len(by_model) for by_model in candidates.values()),
        "complete_ideas": sum(all(model in (candidates.get(idea_id) or {}) for model in models) for idea_id in ids),
    }
    _write(store, output)
    return store


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--models", nargs="*", default=list(GENERATOR_MODELS))
    parser.add_argument("--max-workers", type=int, default=3)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    args = parser.parse_args()
    payload = generate(batch_size=args.batch_size, models=tuple(args.models), max_workers=args.max_workers, output=args.json)
    print(json.dumps(payload.get("summary") or {}, ensure_ascii=False))
    if payload.get("errors"):
        print(json.dumps(payload["errors"][-10:], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
