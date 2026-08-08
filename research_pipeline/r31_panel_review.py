from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .ark_provider import ArkResponsesClient
from .config import PROJECT_ROOT
from .r3_final_audit import build_r3_final_audit
from .r31_finalizer import DEFAULT_JSON as DEFAULT_FINAL_JSON

DEFAULT_JSON = PROJECT_ROOT / "generated" / "r31-panel-reviews.json"
REVIEW_MODELS = ("glm-5.2", "deepseek-v4-pro")


def review_tool(count: int) -> list[dict[str, Any]]:
    props = {
        "idea_id": {"type": "string"},
        "verdict": {"type": "string", "enum": ["pass", "revise", "block"]},
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
        "finding": {"type": "string"},
        "required_action": {"type": "string"},
        "problem_method_alignment": {"type": "string"},
        "mechanism_identifiability": {"type": "string"},
        "simplification_challenge": {"type": "string"},
        "persistent_learning": {"type": "string"},
        "independent_truth": {"type": "string"},
        "baseline_fairness": {"type": "string"},
        "pilot_decisiveness": {"type": "string"},
        "collision_boundary_consistency": {"type": "string"},
        "decisive_falsifier": {"type": "string"},
    }
    return [{
        "type": "function",
        "name": "submit_reviews",
        "description": "Submit strict internal R3.1 pre-audit reviews.",
        "parameters": {
            "type": "object",
            "properties": {
                "ideas": {
                    "type": "array",
                    "minItems": count,
                    "maxItems": count,
                    "items": {"type": "object", "properties": props, "required": list(props), "additionalProperties": False},
                }
            },
            "required": ["ideas"],
            "additionalProperties": False,
        },
    }]


def prompt(rows: list[dict[str, Any]]) -> str:
    return f"""Act as a strict ICLR area chair performing an INTERNAL R3.1 PRE-AUDIT.

The supplied objects are frozen page-facing R3.1 versions produced after a previous strict R3 REVISE. You are not the generator. Review each independently; do not reward effort, lineage, or prior PASS/REVISE status.

This stage deliberately does NOT claim a fresh web literature search. Use only the supplied collision boundary/nearest-work context for collision-consistency checking. A later web-grounded GPT audit will re-search official primary sources. Your task is to decide whether the INTERNAL scientific boundary is now closed.

PASS only if all are true:
1. The method still solves the stated real problem after repair.
2. The exact previous R3 boundary is materially closed, not merely moved into the experiment section.
3. The strongest simplification gets the same information, capacity, calls/tokens, optimization, and wall-clock where applicable.
4. The proposed mechanism is identifiable against that simplification by the preregistered pilot.
5. A persistent learned/fitted object is frozen before held-out evaluation and reused without hidden relearning.
6. Independent truth is external/programmatic/execution truth, not the learned scorer or its own judge.
7. The decisive pilot can directly kill the surviving claim and the stop rule actually terminates/collapses it.
8. The page does not overclaim beyond what the mechanism and supplied collision boundary support.

REVISE if exactly one repairable internal boundary remains. BLOCK if the mechanism is still reducible/circular, the repair drifted to another problem, or the claimed learning object is not meaningful.

If PASS, set `required_action` to exactly `none before external collision verification`. Do not invent citations. Call `submit_reviews` exactly once and emit no prose.

Frozen ideas:
{json.dumps(rows, ensure_ascii=False, indent=2)}
"""


def _load_final() -> list[dict[str, Any]]:
    payload = json.loads(DEFAULT_FINAL_JSON.read_text(encoding="utf-8"))
    return payload.get("ideas") or []


def _load_store() -> dict[str, Any]:
    if not DEFAULT_JSON.exists():
        return {"schema_version": "1.0", "review_models": list(REVIEW_MODELS), "reviews": {}, "errors": []}
    try:
        payload = json.loads(DEFAULT_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"schema_version": "1.0", "review_models": list(REVIEW_MODELS), "reviews": {}, "errors": []}
    payload.setdefault("reviews", {})
    payload.setdefault("errors", [])
    return payload


def _write(payload: dict[str, Any]) -> None:
    payload["updated_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    final_ids = [row["idea_id"] for row in _load_final()]
    verdict_counts = {"pass": 0, "revise": 0, "block": 0, "pending": 0}
    unanimous_pass = 0
    for idea_id in final_ids:
        by_model = payload.get("reviews", {}).get(idea_id, {})
        if len(by_model) < len(REVIEW_MODELS):
            verdict_counts["pending"] += 1
            continue
        verdicts = [by_model[m]["verdict"] for m in REVIEW_MODELS if m in by_model]
        if verdicts and all(v == "pass" for v in verdicts):
            unanimous_pass += 1
            verdict_counts["pass"] += 1
        elif "block" in verdicts:
            verdict_counts["block"] += 1
        else:
            verdict_counts["revise"] += 1
    payload["summary"] = {
        "total": len(final_ids),
        "review_models": len(REVIEW_MODELS),
        "unanimous_pass": unanimous_pass,
        **verdict_counts,
    }
    DEFAULT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _validate(rows: list[dict[str, Any]], expected: list[str]) -> None:
    if len(rows) != len(expected) or {row.get("idea_id") for row in rows} != set(expected):
        raise ValueError("review ids do not match requested ideas")
    for row in rows:
        if row.get("verdict") not in {"pass", "revise", "block"}:
            raise ValueError(f"bad verdict {row.get('idea_id')}")
        if len(str(row.get("finding") or "")) < 20:
            raise ValueError(f"weak finding {row.get('idea_id')}")


def run(model: str, *, batch_size: int = 2, limit: int | None = None) -> dict[str, Any]:
    if model not in REVIEW_MODELS:
        raise ValueError(f"unsupported review model: {model}")
    final_rows = _load_final()
    r3 = {row["idea_id"]: row for row in build_r3_final_audit()["ideas"]}
    store = _load_store()
    reviews = store.setdefault("reviews", {})
    pending = [row for row in final_rows if model not in (reviews.get(row["idea_id"]) or {})]
    if limit is not None:
        pending = pending[:limit]
    batches = [pending[i:i + batch_size] for i in range(0, len(pending), batch_size)]
    client = ArkResponsesClient()
    for batch in batches:
        ids = [row["idea_id"] for row in batch]
        packets = []
        for row in batch:
            prior = r3.get(row["idea_id"], {})
            packets.append({
                "idea_id": row["idea_id"],
                "previous_r3_finding": prior.get("finding", ""),
                "previous_r3_required_action": prior.get("required_action", ""),
                "page_final_version": row,
            })
        try:
            response = client.respond(prompt(packets), model=model, max_output_tokens=9000, tools=review_tool(len(batch)), thinking="disabled")
            calls = [call for call in response.get("function_calls", []) if call.get("name") == "submit_reviews"]
            if len(calls) != 1:
                raise ValueError(f"expected one submit_reviews call, got {len(calls)}")
            rows = json.loads(calls[0].get("arguments") or "{}").get("ideas") or []
            _validate(rows, ids)
            for review in rows:
                reviews.setdefault(review["idea_id"], {})[model] = {
                    **review,
                    "resolved_model": response.get("resolved_model"),
                    "usage": response.get("usage") or {},
                }
        except Exception as error:
            store.setdefault("errors", []).append({"model": model, "ids": ids, "error": str(error)})
        _write(store)
    _write(store)
    return store


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, choices=REVIEW_MODELS)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    payload = run(args.model, batch_size=args.batch_size, limit=args.limit)
    print(json.dumps(payload.get("summary") or {}, ensure_ascii=False))
    if payload.get("errors"):
        print(json.dumps(payload["errors"][-5:], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
