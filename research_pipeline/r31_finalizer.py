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
from .r31_repair_factory import DEFAULT_JSON as DEFAULT_CANDIDATES_JSON
from .r31_repair_factory import _dossier, _records

DEFAULT_JSON = PROJECT_ROOT / "generated" / "r31-final-ideas.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "r31-final-ideas.js"
SYNTHESIZER_MODEL = "kimi-k3"


def _bi_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {"en": {"type": "string"}, "zh": {"type": "string"}},
        "required": ["en", "zh"],
        "additionalProperties": False,
    }


def final_tool(count: int) -> list[dict[str, Any]]:
    bi = _bi_schema()
    props = {
        "idea_id": {"type": "string"},
        "revision": {"type": "string"},
        "title": bi,
        "purpose": bi,
        "importance": bi,
        "core_idea": bi,
        "core_intuition": bi,
        "rationale": bi,
        "method_logic": bi,
        "persistent_update_object": {"type": "string"},
        "learning_signal": bi,
        "independent_ground_truth": bi,
        "strongest_baseline": bi,
        "matched_resources": {"type": "array", "items": {"type": "string"}},
        "decisive_pilot": bi,
        "stop_condition": bi,
        "surviving_claim": bi,
        "collision_boundary": bi,
        "r3_repair_summary": bi,
        "remaining_risk": bi,
    }
    return [{
        "type": "function",
        "name": "submit_final_versions",
        "description": "Submit the page-facing R3.1 final versions.",
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


def build_prompt(cases: list[dict[str, Any]]) -> str:
    return f"""You are the independent R3.1 synthesis editor for an ICLR agent self-evolution idea pipeline.

Each case contains the original page-facing dossier, the strict R3 finding/action, and 2–3 repair proposals from different models. Produce ONE final page-facing version per idea. The output will be independently re-reviewed by other models and then by a web-grounded GPT audit, so do not paper over a boundary.

Synthesis rules:
1. Preserve the original real problem and research importance unless R3 explicitly forces a narrower claim.
2. Choose the smallest material mechanism repair that closes R3. You may merge compatible pieces from proposals, but do not accumulate complexity.
3. If a stronger proposal correctly admits that the baseline can represent the same function, keep that honesty; make the claim about an identifiable inductive bias, transfer, efficiency, or factor only when a decisive experiment can falsify it.
4. The strongest simplification receives identical observations, labels, traces, interventions, model capacity, calls, tokens, optimizer/minibatches/steps, and wall-clock wherever meaningful. Enumerate these in `matched_resources`.
5. The persistent update object must be learned/fitted before held-out evaluation, frozen, and reused without test-time relearning. Ordinary deterministic decoding is allowed only when the claim is about the learned representation and the matched baseline receives the same decoder; otherwise include a search-free compiled control.
6. Independent truth must be external/programmatic/execution truth, never the same learned scorer or judge.
7. `decisive_pilot` must be a single preregistered crossed/factorial test that can kill the surviving claim.
8. `stop_condition` must explicitly terminate or collapse the claim if the strongest matched simplification reproduces it.
9. `collision_boundary` may only use the supplied nearest-work context; do not invent citations or claim that literature does not exist.
10. Use revision `R3.1`. Keep the exact supplied `idea_id` so the site can preserve lineage.
11. Return bilingual Simplified Chinese/English fields with equivalent meaning. Call `submit_final_versions` once; no prose.

Cases:
{json.dumps(cases, ensure_ascii=False, indent=2)}
"""


def _load_candidates() -> dict[str, Any]:
    return json.loads(DEFAULT_CANDIDATES_JSON.read_text(encoding="utf-8"))


def _load_existing(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": "1.0", "revision": "R3.1", "synthesizer_model": SYNTHESIZER_MODEL, "ideas": []}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"schema_version": "1.0", "revision": "R3.1", "synthesizer_model": SYNTHESIZER_MODEL, "ideas": []}


def _write(payload: dict[str, Any], json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> None:
    payload["generated_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.R31_FINAL_IDEAS = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")


def _validate(rows: list[dict[str, Any]], expected_ids: list[str]) -> None:
    if len(rows) != len(expected_ids) or {row.get("idea_id") for row in rows} != set(expected_ids):
        raise ValueError("R3.1 finalizer omitted or changed idea ids")
    required_bi = ("title", "purpose", "importance", "core_idea", "core_intuition", "rationale", "method_logic", "learning_signal", "independent_ground_truth", "strongest_baseline", "decisive_pilot", "stop_condition", "surviving_claim", "collision_boundary", "r3_repair_summary", "remaining_risk")
    for row in rows:
        if row.get("revision") != "R3.1":
            raise ValueError(f"wrong revision for {row.get('idea_id')}")
        if len(row.get("matched_resources") or []) < 6:
            raise ValueError(f"too few matched resources for {row.get('idea_id')}")
        if len(str(row.get("persistent_update_object") or "")) < 20:
            raise ValueError(f"weak persistent object for {row.get('idea_id')}")
        for key in required_bi:
            value = row.get(key) or {}
            min_en, min_zh = ((8, 4) if key == "title" else (24, 12))
            if len(str(value.get("en") or "")) < min_en or len(str(value.get("zh") or "")) < min_zh:
                raise ValueError(f"weak bilingual {key} for {row.get('idea_id')}")


def finalize(*, batch_size: int = 1, max_workers: int = 1, limit: int | None = None, output_json: Path = DEFAULT_JSON, output_js: Path = DEFAULT_JS) -> dict[str, Any]:
    candidates = _load_candidates().get("candidates") or {}
    r3_rows = [row for row in build_r3_final_audit()["ideas"] if row["verdict"] == "revise"]
    r3_by_id = {row["idea_id"]: row for row in r3_rows}
    records = _records()
    ids = [row["idea_id"] for row in r3_rows]
    payload = _load_existing(output_json)
    existing = {row["idea_id"]: row for row in payload.get("ideas") or [] if row.get("idea_id")}
    todo = [idea_id for idea_id in ids if idea_id not in existing]
    if limit is not None:
        todo = todo[:limit]
    batches = [todo[i:i + batch_size] for i in range(0, len(todo), batch_size)]

    def one(batch: list[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        cases = []
        for idea_id in batch:
            proposals = []
            for model, item in sorted((candidates.get(idea_id) or {}).items()):
                proposals.append({"source_model": model, **(item.get("repair") or {})})
            cases.append({
                "idea_id": idea_id,
                "original": _dossier(idea_id, records.get(idea_id, {}), r3_by_id[idea_id]),
                "repair_proposals": proposals,
            })
        client = ArkResponsesClient()
        response = client.respond(build_prompt(cases), model=SYNTHESIZER_MODEL, max_output_tokens=16000, tools=final_tool(len(batch)), thinking="disabled")
        calls = [call for call in response.get("function_calls", []) if call.get("name") == "submit_final_versions"]
        if len(calls) != 1:
            raise ValueError(f"expected one submit_final_versions call, got {len(calls)}")
        rows = json.loads(calls[0].get("arguments") or "{}").get("ideas") or []
        _validate(rows, batch)
        return rows, response.get("usage") or {}

    errors: list[dict[str, Any]] = list(payload.get("errors") or [])
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(one, batch): batch for batch in batches}
        for future in concurrent.futures.as_completed(futures):
            batch = futures[future]
            try:
                rows, usage = future.result()
                for row in rows:
                    row["synthesis_usage"] = usage
                    existing[row["idea_id"]] = row
            except Exception as error:
                errors.append({"ids": batch, "error": str(error)})
            payload.update({
                "schema_version": "1.0",
                "revision": "R3.1",
                "synthesizer_model": SYNTHESIZER_MODEL,
                "source_r3_review_date": "2026-08-08",
                "ideas": [existing[idea_id] for idea_id in ids if idea_id in existing],
                "errors": errors,
                "summary": {"target": len(ids), "complete": len(existing), "pending": len(ids) - len(existing)},
            })
            _write(payload, output_json, output_js)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--max-workers", type=int, default=1)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    payload = finalize(batch_size=args.batch_size, max_workers=args.max_workers, limit=args.limit)
    print(json.dumps(payload.get("summary") or {}, ensure_ascii=False))
    if payload.get("errors"):
        print(json.dumps(payload["errors"][-10:], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
