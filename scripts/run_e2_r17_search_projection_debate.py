#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.ark_provider import (
    ArkResponseStateError,
    ArkResponsesClient,
    ArkSettings,
    extract_json_object,
)
from research_pipeline.config import load_env_file

PLAN_BASE_URL = "https://ark.cn-beijing.volces.com/api/plan/v3"
REQUESTED_MODELS = ("deepseek-v4-pro", "kimi-k3")
OUT_ROOT = ROOT / "generated/e2-r17-search-projection-debate-20260827"
IDENTITY = ROOT / "generated/e2-r17-search-projection-consultation-model-identity-adjudication-20260827.json"
DOSSIER_FILES = (
    ROOT / "consultations/e2-r17-search-projection-censoring-literature-synthesis-20260825.md",
    ROOT / "generated/e2-r17-search-projection-f0-r4-design-20260825.json",
    ROOT / "consultations/e2-r17-search-projection-current-source-and-theory-audit-20260827.md",
    ROOT / "generated/e2-r17-r3-assets-provenance-and-r4-supersession-20260827.json",
    ROOT / "generated/e2-r17-compute-shielding-f0-r3-gate-20260825.json",
)


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_text(text: str) -> str:
    return sha_bytes(text.encode("utf-8"))


def safe_model_slug(model: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", model)


def sanitize_error(message: str) -> str:
    text = re.sub(r"resp_[A-Za-z0-9_]+", "resp_[REDACTED]", str(message))
    text = re.sub(r"Request id:\s*[A-Za-z0-9_]+", "Request id: [REDACTED]", text)
    return text[:1000]


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(text, encoding="utf-8")
    temp.replace(path)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    atomic_text(path, json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def dossier() -> tuple[str, dict[str, str]]:
    sections: list[str] = []
    hashes: dict[str, str] = {}
    for path in DOSSIER_FILES:
        raw = path.read_bytes()
        rel = str(path.relative_to(ROOT))
        hashes[rel] = sha_bytes(raw)
        sections.append(f"\n===== SOURCE FILE: {rel} =====\n{raw.decode('utf-8')}\n")
    return "".join(sections), hashes


def load_review(round_number: int, requested_model: str) -> dict[str, Any]:
    path = OUT_ROOT / f"round{round_number}" / f"{safe_model_slug(requested_model)}.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("status") != "COMPLETED" or not payload.get("parse_valid"):
        raise RuntimeError(f"required prior review is not complete: {path}")
    return payload


def review_excerpt(payload: dict[str, Any]) -> str:
    return json.dumps(
        {
            "requested_model": payload.get("requested_model"),
            "resolved_model": payload.get("resolved_model"),
            "round": payload.get("round"),
            "review": payload.get("review"),
        },
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )


def required_fields(round_number: int) -> tuple[str, ...]:
    if round_number == 1:
        return (
            "thesis_reduction_verdict",
            "strongest_direct_reduction",
            "irreducible_novelty",
            "formula_or_mechanism_that_is_pretty_but_empty",
            "decisive_kill_experiment",
            "deeper_scientific_object",
            "theory_attacks",
            "causal_identification_attacks",
            "method_collision_assessment",
            "recommendation",
            "single_sentence_verdict",
        )
    if round_number == 2:
        return (
            "strongest_attack_on_other_review",
            "concessions_to_other_review",
            "novelty_adjudication",
            "causal_identification_adjudication",
            "theoretical_assumption_adjudication",
            "strongest_baseline",
            "experimental_leakage_risks",
            "selective_labels_or_distillation_reduction",
            "revised_recommendation",
            "single_sentence_verdict",
        )
    if round_number == 3:
        return (
            "central_scientific_object",
            "single_causal_chain",
            "strongest_theoretical_prediction",
            "decisive_intervention",
            "mechanism_derived_method",
            "explicit_stop_condition",
            "claims_to_delete",
            "recommendation",
            "single_sentence_verdict",
        )
    return (
        "overall_score_1_to_10",
        "recommendation",
        "strongest_reject_reason",
        "fatal_or_verdict_changing_issues",
        "repairs_that_could_change_verdict",
        "issues_not_worth_chasing",
        "novelty_after_skillcat_topocurate",
        "causal_identification_verdict",
        "theory_depth_verdict",
        "experiment_sufficiency_verdict",
        "single_sentence_verdict",
    )


def schema_instruction(round_number: int) -> str:
    fields = required_fields(round_number)
    skeleton = {field: "" for field in fields}
    if round_number == 1:
        skeleton.update(
            {
                "theory_attacks": [""],
                "causal_identification_attacks": [""],
                "method_collision_assessment": {"SkillCAT": "", "TopoCurate": "", "other": [""]},
                "deeper_scientific_object": {"exists": False, "object": "", "why_deeper": ""},
            }
        )
    elif round_number == 2:
        skeleton.update(
            {
                "concessions_to_other_review": [""],
                "experimental_leakage_risks": [""],
            }
        )
    elif round_number == 3:
        skeleton.update({"claims_to_delete": [""]})
    else:
        skeleton.update(
            {
                "overall_score_1_to_10": 0,
                "fatal_or_verdict_changing_issues": [
                    {"issue": "", "severity": "fatal|major", "cheapest_decisive_repair": ""}
                ],
                "repairs_that_could_change_verdict": [""],
                "issues_not_worth_chasing": [""],
            }
        )
    return json.dumps(skeleton, ensure_ascii=False, indent=2)


def build_prompt(round_number: int, requested_model: str, dossier_text: str) -> str:
    common = f"""You are one member of an independent Kimi × DeepSeek scientific red-team for a prospective ICLR-level paper. This is an INTERNAL, zero-authority consultation. You cannot authorize experiments, GPU use, paper promotion, or submission. Be adversarial, concrete, and willing to recommend STOP. Do not reward engineering volume or polished wording.

The candidate is E2-R17 / Search-Projection Censoring. The supplied dossier contains the full current R17 design artifacts, historical F0 state, a current-source collision audit through 2026-08-27, and a zero-provider theory strengthening proposal. Treat the primary-source facts and exact artifact boundaries as binding. In particular, SkillCAT is a direct method collision, TopoCurate is a representation/selection collision, and the old R3 runner is not an executable R4 implementation.

Requested endpoint: {requested_model}. Your actual resolved identity is recorded outside this prompt and is the source of truth.

Do not invent citations or claim to have browsed beyond the supplied primary-source dossier. Separate: (i) what follows mathematically, (ii) what is only a modeling assumption, (iii) what requires experiment, and (iv) what is already reduced by prior work.
"""
    if round_number == 1:
        task = """
ROUND 1 — BLIND INDEPENDENT SCIENTIFIC REVIEW
You have not seen the other model's review. Answer all of the following:
1. Can the current thesis be directly reduced to existing work? Name the strongest reduction, not a literature list.
2. What is the truly irreducible novelty, if any?
3. Which formula or mechanism is currently attractive but scientifically empty or underidentified?
4. What single decisive experiment could kill the paper?
5. Is there a deeper and more unified object than Search-Projection Censoring? Say no if there is not.
6. Attack independence/correlation, continuous verifier, diagnostic-value identifiability, family overlap, and the exact Gamma-times-delta factorization.
7. Judge whether SkillCAT/TopoCurate/search distillation leave enough novelty.

Return exactly one JSON object and no markdown, using this shape:
""" + schema_instruction(1)
        prior = "\nINDEPENDENCE FLAG: independent=true; exposed_to_other_review=false.\n"
    elif round_number == 2:
        own = load_review(1, requested_model)
        other_model = next(model for model in REQUESTED_MODELS if model != requested_model)
        other = load_review(1, other_model)
        task = f"""
ROUND 2 — CROSS-EXPOSED MUTUAL ATTACK
You now see both blind Round-1 reviews. Attack the other review's novelty boundary, causal identification, assumptions, strongest baseline, leakage risks, and any attempt to rebrand selective labels/distillation/curriculum. Concede points that survive attack. Do not expand into a feature or benchmark zoo.

YOUR ROUND-1 REVIEW:
{review_excerpt(own)}

OTHER MODEL'S ROUND-1 REVIEW:
{review_excerpt(other)}

Return exactly one JSON object and no markdown, using this shape:
{schema_instruction(2)}
"""
        prior = "\nINDEPENDENCE FLAG: independent=false; exposed_to_other_review=true; exposure_scope=both_round1_reviews.\n"
    elif round_number == 3:
        reviews = []
        for prior_round in (1, 2):
            for model in REQUESTED_MODELS:
                reviews.append(review_excerpt(load_review(prior_round, model)))
        task = f"""
ROUND 3 — SINGLE-OBJECT CONVERGENCE
You have seen both models' Round-1 and Round-2 outputs. You are forbidden to return a feature zoo, benchmark zoo, router, frontier, or module collection. Retain exactly:
- one central scientific object;
- one causal chain;
- one strongest falsifiable theoretical prediction;
- one decisive intervention;
- one method that follows naturally from the mechanism (prefer the simpler Rejected Witness if sufficient);
- one explicit STOP condition.
Delete claims already occupied by SkillCAT, TopoCurate, sibling distillation, SkillOpt, and failure-only skill evolution.

PRIOR REVIEWS:
{chr(10).join(reviews)}

Return exactly one JSON object and no markdown, using this shape:
{schema_instruction(3)}
"""
        prior = "\nINDEPENDENCE FLAG: independent=false; exposed_to_other_review=true; exposure_scope=round1_and_round2_panel.\n"
    else:
        reviews = [review_excerpt(load_review(3, model)) for model in REQUESTED_MODELS]
        task = f"""
ROUND 4 — ICLR PAPER-PC RED TEAM
Assume the paper is written around the strongest Round-3 consensus, but no scientific experiment has yet been run. Give the strongest reject case. Identify only fatal or verdict-changing issues and the cheapest repairs that could truly change the verdict. Do not request extra models, benchmarks, tables, or ablations merely for volume. Judge novelty after SkillCAT and TopoCurate, causal identification, theory depth, experiment sufficiency, and whether the proposed method is necessary.

ROUND-3 OUTPUTS:
{chr(10).join(reviews)}

Return exactly one JSON object and no markdown, using this shape:
{schema_instruction(4)}
"""
        prior = "\nINDEPENDENCE FLAG: independent=false; exposed_to_other_review=true; exposure_scope=round3_consensus_candidates.\n"
    return common + task + prior + "\nFULL DOSSIER START\n" + dossier_text + "\nFULL DOSSIER END\n"


def call_model(
    client: ArkResponsesClient,
    *,
    round_number: int,
    requested_model: str,
    expected_resolved: str,
    dossier_text: str,
    dossier_hashes: dict[str, str],
    max_output_tokens: int,
) -> dict[str, Any]:
    prompt = build_prompt(round_number, requested_model, dossier_text)
    round_dir = OUT_ROOT / f"round{round_number}"
    slug = safe_model_slug(requested_model)
    prompt_path = round_dir / f"{slug}-prompt.md"
    atomic_text(prompt_path, prompt)
    created = datetime.now(timezone.utc).isoformat(timespec="seconds")
    base: dict[str, Any] = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-search-projection-scientific-debate-response",
        "round": round_number,
        "created_at_utc": created,
        "requested_model": requested_model,
        "expected_resolved_model_from_qualification": expected_resolved,
        "route": client.settings.base_url,
        "provider_retry_limit": client.settings.max_retries,
        "provider_generation_attempts": 1,
        "hidden_provider_retry_used": False,
        "thinking_requested": "disabled",
        "automatic_thinking_compatibility_fallback_allowed": False,
        "max_output_tokens": max_output_tokens,
        "prompt_path": str(prompt_path.relative_to(ROOT)),
        "prompt_sha256": sha_text(prompt),
        "dossier_file_sha256": dossier_hashes,
        "independent": round_number == 1,
        "exposed_to_other_review": round_number > 1,
        "scientific_authority": False,
        "experiment_authority": False,
        "submission_authority": False,
    }
    try:
        try:
            result = client.respond(
                prompt,
                model=requested_model,
                max_output_tokens=max_output_tokens,
                temperature=0,
                thinking="disabled",
                allow_thinking_compatibility_fallback=False,
            )
        except ArkResponseStateError as exc:
            state = exc.receipt()
            base["initial_response_state"] = {
                "status": state.get("status"),
                "requested_model": state.get("requested_model"),
                "resolved_model": state.get("resolved_model"),
                "incomplete_reason": state.get("incomplete_reason"),
                "response_id_sha256": sha_text(str(state.get("response_id") or "")),
            }
            if not exc.response_id:
                raise
            try:
                polled = client.poll_response(exc.response_id, max_polls=4, interval_seconds=1.0)
            except Exception as poll_error:
                return {
                    **base,
                    "status": "HOLD_PROVIDER_RESPONSE_RETRIEVAL",
                    "poll_error_type": type(poll_error).__name__,
                    "poll_error_message_sanitized": sanitize_error(str(poll_error)),
                    "poll_error_sha256": sha_text(str(poll_error)),
                }
            if not polled.get("text"):
                return {
                    **base,
                    "status": "HOLD_PROVIDER_RESPONSE_STATE",
                    "polled_status": polled.get("status"),
                    "poll_count": polled.get("poll_count"),
                }
            result = {
                "requested_model": requested_model,
                "resolved_model": polled.get("resolved_model"),
                "text": polled.get("text"),
                "usage": polled.get("usage") or {},
                "response_id": polled.get("response_id") or exc.response_id,
                "status": polled.get("status"),
                "get_poll_recovery": True,
                "poll_count": polled.get("poll_count"),
            }
        raw = str(result.get("text") or "")
        resolved = str(result.get("resolved_model") or "")
        base.update(
            {
                "resolved_model": resolved,
                "resolved_model_matches_qualification": resolved == expected_resolved,
                "provider_status": result.get("status"),
                "response_id_sha256": sha_text(str(result.get("response_id") or "")),
                "usage": result.get("usage") or {},
                "raw_text": raw,
                "raw_text_sha256": sha_text(raw),
                "get_poll_recovery": bool(result.get("get_poll_recovery", False)),
                "poll_count": result.get("poll_count", 0),
            }
        )
        if resolved != expected_resolved:
            base["status"] = "FAIL_RESOLVED_MODEL_DRIFT"
            return base
        try:
            review = extract_json_object(raw)
            missing = [field for field in required_fields(round_number) if field not in review]
            base.update(
                {
                    "review": review,
                    "parse_valid": not missing,
                    "missing_required_fields": missing,
                    "status": "COMPLETED" if not missing else "FAIL_SCHEMA",
                }
            )
        except Exception as exc:
            base.update(
                {
                    "status": "FAIL_PARSE",
                    "parse_valid": False,
                    "parse_error": f"{type(exc).__name__}: {exc}",
                }
            )
    except Exception as exc:
        message = str(exc)
        subscription = "InvalidSubscription" in message or "valid AgentPlan subscription" in message
        base.update(
            {
                "status": "HOLD_PROVIDER_SUBSCRIPTION" if subscription else "FAIL_PROVIDER_PROTOCOL",
                "error_type": type(exc).__name__,
                "error_message_sanitized": (
                    "Ark Plan subscription unavailable" if subscription else sanitize_error(message)
                ),
                "error_sha256": sha_text(message),
            }
        )
    return base


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--round", type=int, choices=(1, 2, 3, 4), required=True)
    parser.add_argument("--models", nargs="*", default=list(REQUESTED_MODELS))
    parser.add_argument("--max-output-tokens", type=int, default=7000)
    args = parser.parse_args()

    unknown = set(args.models) - set(REQUESTED_MODELS)
    if unknown:
        raise SystemExit(f"unsupported models: {sorted(unknown)}")
    identity = json.loads(IDENTITY.read_text(encoding="utf-8"))
    expected = {
        model: identity["requested_and_resolved"][model]["resolved"]
        for model in REQUESTED_MODELS
    }
    if len(set(expected.values())) != len(expected):
        raise RuntimeError("resolved reviewer identities are not independent")

    load_env_file(args.env_file)
    source = ArkSettings.from_env(required=True)
    if source.base_url.rstrip("/") != PLAN_BASE_URL:
        raise RuntimeError("R17 debate refuses non-Plan Ark route")
    settings = ArkSettings(
        api_key=source.api_key,
        base_url=source.base_url,
        default_model=source.default_model,
        timeout_seconds=240.0,
        max_retries=0,
    )
    client = ArkResponsesClient(settings)
    dossier_text, dossier_hashes = dossier()
    rows = []
    for model in args.models:
        row = call_model(
            client,
            round_number=args.round,
            requested_model=model,
            expected_resolved=expected[model],
            dossier_text=dossier_text,
            dossier_hashes=dossier_hashes,
            max_output_tokens=args.max_output_tokens,
        )
        path = OUT_ROOT / f"round{args.round}" / f"{safe_model_slug(model)}.json"
        atomic_json(path, row)
        rows.append(
            {
                "requested_model": model,
                "resolved_model": row.get("resolved_model"),
                "status": row.get("status"),
                "parse_valid": row.get("parse_valid"),
                "raw_text_sha256": row.get("raw_text_sha256"),
                "usage": row.get("usage") or {},
                "artifact": str(path.relative_to(ROOT)),
                "artifact_sha256": sha_bytes(path.read_bytes()),
            }
        )
        print(json.dumps(rows[-1], ensure_ascii=False))

    summary = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-search-projection-scientific-debate-round-summary",
        "round": args.round,
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "COMPLETED" if all(row["status"] == "COMPLETED" for row in rows) else "INCOMPLETE",
        "route": settings.base_url,
        "provider_retry_limit": settings.max_retries,
        "reviews": rows,
        "resolved_identity_independence": len({row.get("resolved_model") for row in rows}) == len(rows),
        "scientific_authority": False,
        "experiment_authority": False,
        "submission_authority": False,
    }
    summary_path = OUT_ROOT / f"round{args.round}" / "summary.json"
    atomic_json(summary_path, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if summary["status"] == "COMPLETED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
