from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .api_memory_search_smoke import _canonical, _sha_text, _usage
from .api_memory_search_smoke_staged import _client, _load, _lock, _write
from .api_research_memory import (
    record_api_memory_consumption,
    record_parsed_api_output,
    record_provider_failure,
    record_raw_api_output,
)
from .ark_provider import extract_json_object

HARD_REVIEWER_MODEL = "deepseek-v4-pro"
AGENT_REVIEWER_MODEL = "doubao-seed-2.1-turbo"
REDUCTION_REVIEWER_MODEL = "minimax-m3"


def _parse_review_payload(raw: str, *, run_root: Path, name: str, raw_sha256: str) -> tuple[dict[str, Any], dict[str, Any] | None]:
    try:
        return extract_json_object(raw), None
    except Exception as first_error:
        stripped = str(raw or "").strip()
        if not stripped.endswith('\"]}'):
            raise
        repaired = (stripped[:-2] + '}]}').strip()
        try:
            payload = extract_json_object(repaired)
        except Exception:
            raise first_error
        receipt = {
            "schema_version":"1.0",
            "status":"PARSE_REPAIRED_PUNCTUATION_ONLY_ZERO_AUTHORITY",
            "stage":f"memory-portfolio-{name}-review",
            "raw_sha256":raw_sha256,
            "repaired_sha256":_sha_text(repaired),
            "repair_type":"TRAILING_REVIEW_OBJECT_CLOSE_ONLY",
            "inserted_text":"}",
            "string_content_mutation_allowed":False,
            "scientific_authority":False,
            "belief_authority":False,
        }
        _write(run_root/f"repair-{name}-review-{raw_sha256[:12]}.json",receipt)
        return payload, receipt


def hard_prompt(prep: dict[str, Any]) -> str:
    return f'''You are the HARD search-control reviewer. Judge ONLY history near-duplication and bounded falsifier completeness. Do not judge agent-specificity or same-information reduction.

history_near_duplicate=true only if a supplied history object has substantially the same scientific object AND the same key prediction/reduction basin. This is pack-scoped, not literature novelty.
cheapest_falsifier_complete=true only if the candidate specifies a bounded comparison/intervention, an independently observable outcome, and a stopping interpretation that could distinguish two outcomes.

HISTORY_PACK_START
{prep["history_pack"]["text"]}
HISTORY_PACK_END
BLINDED_IDEAS={_canonical(prep["blinded"])}

Return JSON only with exactly {len(prep["blinded"])} reviews: {{"reviews":[{{"blind_id":"B...","history_near_duplicate":false,"cheapest_falsifier_complete":true,"matched_history_object_id":"","reason":"<=35 words"}}, ...]}}'''


def agent_prompt(prep: dict[str, Any]) -> str:
    return f'''You are an AGENT-SPECIFICITY adjudicator. Judge only whether each scientific object fundamentally requires persistent autonomous-agent state/history/memory/retrieval/self-evolution.

Use exactly one verdict:
- AGENT_SPECIFIC: the predicted phenomenon would cease to be the same object if persistent agent history/state/retrieval were removed.
- GENERIC_OR_MODEL_LEVEL: it is fundamentally generic optimization, representation, context-length, ordinary forgetting, RL convergence, or model behavior that does not require persistent agent evolution.
- UNCERTAIN: the candidate description does not identify the boundary clearly enough.
Do NOT decide reduction risk. A phenomenon may be agent-specific and still reducible by a baseline.

BLINDED_IDEAS={_canonical(prep["blinded"])}
Return JSON only with exactly {len(prep["blinded"])} reviews: {{"reviews":[{{"blind_id":"B...","agent_specificity":"AGENT_SPECIFIC|GENERIC_OR_MODEL_LEVEL|UNCERTAIN","reason":"<=40 words"}}, ...]}}'''


def reduction_prompt(prep: dict[str, Any]) -> str:
    return f'''You are an EXACT SAME-INFORMATION REDUCTION adjudicator. Judge only whether the candidate's stated baseline actually reduces the stated exact prediction.

Use exactly one verdict:
- EXACT_REDUCTION: the baseline receives the same observable information and can reproduce the candidate's exact directional/ordering/threshold prediction, leaving no distinct residual scientific object.
- RESIDUAL_PLAUSIBLE: the baseline is relevant but does not by itself imply the exact candidate prediction; a bounded falsifier can distinguish a residual.
- UNCERTAIN: the information lock or predicted contrast is underspecified.
A generic possible explanation is NOT enough for EXACT_REDUCTION. Do NOT judge whether the object is agent-specific or novel.

BLINDED_IDEAS={_canonical(prep["blinded"])}
Return JSON only with exactly {len(prep["blinded"])} reviews: {{"reviews":[{{"blind_id":"B...","reduction_verdict":"EXACT_REDUCTION|RESIDUAL_PLAUSIBLE|UNCERTAIN","same_information_match":true,"reason":"<=45 words"}}, ...]}}'''


def run_stage(
    *,
    root: Path,
    study: Path,
    name: str,
    model: str,
    prompt: str,
    expected_ids: set[str],
    memory_pack: dict[str, Any] | None = None,
) -> dict[str, Any]:
    output = study / f"review-{name}-result.json"
    prefix = str(_load(study / "state-prepared.json")["prefix"])
    run_id = f"{prefix}-{name}-review"
    lock = _lock(output, {"stage": f"review-{name}", "run_id": run_id, "model": model})
    try:
        run_root = root / "runs" / run_id
        run_root.mkdir(parents=True, exist_ok=True)
        try:
            response = _client().respond(
                prompt,
                model=model,
                max_output_tokens=6500,
                temperature=0.0,
                thinking="disabled",
                store=True,
            )
        except Exception as error:
            psha = _sha_text(prompt)
            fp = _sha_text(_canonical({
                "stage": f"memory-portfolio-{name}-review",
                "model": model,
                "prompt_sha256": psha,
                "error_type": type(error).__name__,
                "error": str(error)[:500],
            }))
            receipt = record_provider_failure(
                run_root=run_root,
                stage=f"memory-portfolio-{name}-review",
                payload={
                    "status": "PROVIDER_ERROR_ZERO_AUTHORITY",
                    "requested_model": model,
                    "error_fingerprint": fp,
                    "prompt_sha256": psha,
                },
                root=root,
            )
            failed = {
                "schema_version":"1.0",
                "status":"PROVIDER_FAILURE",
                "run_id":run_id,
                "error_type":type(error).__name__,
                "error":str(error)[:1200],
                "provider_failure":receipt,
                "scientific_authority":False,
                "belief_authority":False,
            }
            _write(output, failed)
            return failed
        raw = str(response.get("text") or "")
        raw_file = run_root / f"raw-{name}-review.txt"
        raw_file.write_text(raw, encoding="utf-8")
        psha = _sha_text(prompt)
        fingerprint = _sha_text(_canonical({
            "stage": f"memory-portfolio-{name}-review",
            "model": model,
            "prompt_sha256": psha,
            "history_pack_sha256": (memory_pack or {}).get("query_pack_sha256", ""),
        }))
        archived = record_raw_api_output(
            run_root=run_root,
            stage=f"memory-portfolio-{name}-review",
            raw_path=raw_file,
            requested_model=model,
            resolved_model=str(response.get("resolved_model") or model),
            request_fingerprint=fingerprint,
            prompt_sha256=psha,
            root=root,
        )
        parsed_payload, parse_repair = _parse_review_payload(raw, run_root=run_root, name=name, raw_sha256=archived["raw_sha256"])
        reviews = parsed_payload.get("reviews")
        if not isinstance(reviews, list) or len(reviews) != len(expected_ids):
            raise ValueError(f"{name} reviewer must return {len(expected_ids)} reviews")
        observed = {str(row.get("blind_id") or "") for row in reviews if isinstance(row, dict)}
        if observed != expected_ids:
            raise ValueError(f"{name} reviewer blind ids mismatch")
        structured = {
            "schema_version":"2.3",
            "study":"API_MEMORY_PORTFOLIO_SMOKE",
            "review_stage":name,
            "usage":_usage(response),
            "parse_repair":parse_repair or {},
            "reviews":reviews,
            "scientific_authority":False,
            "belief_authority":False,
        }
        record_parsed_api_output(
            run_root=run_root,
            stage=f"memory-portfolio-{name}-review",
            raw_sha256=archived["raw_sha256"],
            structured_payload=structured,
            requested_model=model,
            resolved_model=str(response.get("resolved_model") or model),
            research_objects=[],
            root=root,
        )
        if memory_pack is not None:
            record_api_memory_consumption(
                run_id=run_id,
                stage=f"memory-portfolio-{name}-review",
                pack=memory_pack,
                raw_sha256=archived["raw_sha256"],
                output_object_ids=sorted(expected_ids),
                outcome_status=f"PORTFOLIO_SMOKE_{name.upper()}_REVIEW_ZERO_AUTHORITY",
                root=root,
            )
        result = {
            "schema_version":"2.3",
            "status":f"{name.upper()}_REVIEW_COMPLETE",
            "run_id":run_id,
            "raw_sha256":archived["raw_sha256"],
            "prompt_sha256":psha,
            "resolved_model":str(response.get("resolved_model") or ""),
            "usage":_usage(response),
            "parse_repair":parse_repair or {},
            "reviews":reviews,
            "scientific_authority":False,
            "belief_authority":False,
        }
        result["stage_sha256"] = _sha_text(_canonical(result))
        _write(output, result)
        return result
    finally:
        if output.exists():
            lock.unlink(missing_ok=True)


def run_hard(*, root: Path, study: Path) -> dict[str, Any]:
    prep = _load(study / "review-prepared.json")
    return run_stage(
        root=root,
        study=study,
        name="hard",
        model=HARD_REVIEWER_MODEL,
        prompt=hard_prompt(prep),
        expected_ids={row["blind_id"] for row in prep["blinded"]},
        memory_pack=prep["history_pack"],
    )


def run_agent(*, root: Path, study: Path) -> dict[str, Any]:
    raise RuntimeError("18-item agent-specificity review is disabled after repeated length/protocol failures; use api_memory_portfolio_smoke_agent_items for 18x1 itemized review")


def run_reduction(*, root: Path, study: Path) -> dict[str, Any]:
    prep = _load(study / "review-prepared.json")
    return run_stage(
        root=root,
        study=study,
        name="reduction",
        model=REDUCTION_REVIEWER_MODEL,
        prompt=reduction_prompt(prep),
        expected_ids={row["blind_id"] for row in prep["blinded"]},
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("hard", "agent", "reduction"))
    parser.add_argument("--persistent-root", type=Path, required=True)
    parser.add_argument("--study", type=Path, required=True)
    args = parser.parse_args()
    if args.stage == "hard":
        result = run_hard(root=args.persistent_root, study=args.study)
    elif args.stage == "agent":
        result = run_agent(root=args.persistent_root, study=args.study)
    else:
        result = run_reduction(root=args.persistent_root, study=args.study)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
