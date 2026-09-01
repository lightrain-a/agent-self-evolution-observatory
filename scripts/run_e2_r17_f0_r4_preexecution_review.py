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
OUT_ROOT = ROOT / "generated/e2-r17-f0-r4-preexecution-review-20260828"
IDENTITY_PATH = ROOT / "generated/e2-r17-current-plan-model-identity-adjudication-20260828.json"
DOSSIER_PATHS = (
    ROOT / "generated/e2-r17-f0-r4-frozen-candidate-contract-20260828.json",
    ROOT / "consultations/e2-r17-public-dataset-and-baseline-audit-20260828.md",
    ROOT / "generated/e2-r17-search-projection-debate-adjudication-20260827.json",
    ROOT / "generated/e2-r17-cloned-state-first-party-updater-qualification-20260828.json",
    ROOT / "generated/e2-r17-actor-protocol-smoke-20260828.json",
    ROOT / "generated/e2-r17-current-plan-model-identity-adjudication-20260828.json",
    ROOT / "generated/e2-r17-e0-pilot-manifest-20260828.json",
)


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_text(text: str) -> str:
    return sha_bytes(text.encode("utf-8"))


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    atomic_text(path, json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def safe_slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", text)


def sanitize_error(text: str) -> str:
    value = re.sub(r"resp_[A-Za-z0-9_]+", "resp_[REDACTED]", str(text))
    value = re.sub(r"Request id:\s*[A-Za-z0-9_]+", "Request id: [REDACTED]", value)
    return value[:1000]


def load_dossier() -> tuple[str, dict[str, str]]:
    sections: list[str] = []
    hashes: dict[str, str] = {}
    for path in DOSSIER_PATHS:
        raw = path.read_bytes()
        rel = str(path.relative_to(ROOT))
        hashes[rel] = sha_bytes(raw)
        sections.append(f"\n===== BOUND ARTIFACT: {rel} =====\n{raw.decode('utf-8')}\n")
    return "".join(sections), hashes


def expected_models() -> dict[str, str]:
    payload = json.loads(IDENTITY_PATH.read_text(encoding="utf-8"))
    return {
        requested: str(payload["requested_and_resolved"][requested]["resolved"])
        for requested in REQUESTED_MODELS
    }


def round1_schema() -> dict[str, Any]:
    return {
        "contract_sha256_acknowledged": "",
        "verdict": "GO|HOLD|STOP",
        "experiment_identifiable": False,
        "main_claim_falsifiable": False,
        "strongest_simpler_explanation_controlled": False,
        "blocking_collision_present": False,
        "scientific_object_assessment": "",
        "causal_identification_assessment": "",
        "statistics_assessment": "",
        "public_dataset_assessment": "",
        "baseline_assessment": "",
        "fatal_or_blocking_issues": [
            {"issue": "", "why_blocking": "", "minimal_repair": ""}
        ],
        "nonblocking_improvements": [""],
        "e0_pilot_recommendation": "GO|HOLD|STOP",
        "single_sentence_verdict": "",
    }


def round2_schema() -> dict[str, Any]:
    return {
        "contract_sha256_acknowledged": "",
        "other_review_understood": False,
        "final_verdict": "GO|HOLD|STOP",
        "agreements": [""],
        "disagreements": [""],
        "issues_that_remain_blocking": [""],
        "issues_resolved_by_existing_controls": [""],
        "exact_preexecution_conditions": [""],
        "e0_pilot_authorization_recommendation": "GO|HOLD|STOP",
        "e1_authorization_recommendation": "HOLD_UNTIL_E0|GO|STOP",
        "paper_claim_authority": False,
        "single_sentence_verdict": "",
    }


def load_round1(requested_model: str) -> dict[str, Any]:
    path = OUT_ROOT / "round1" / f"{safe_slug(requested_model)}.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("status") != "COMPLETED" or not payload.get("parse_valid"):
        raise RuntimeError(f"incomplete round1 artifact: {path}")
    return payload


def compact_review(payload: dict[str, Any]) -> str:
    return json.dumps(
        {
            "requested_model": payload.get("requested_model"),
            "resolved_model": payload.get("resolved_model"),
            "review": payload.get("review"),
        },
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )


def build_prompt(round_number: int, requested_model: str, dossier: str, contract_sha: str) -> str:
    preamble = f"""You are an independent pre-execution scientific reviewer for E2-R17, a prospective ICLR paper. This consultation has zero experiment, GPU, paper-promotion, or submission authority. Be adversarial and recommend STOP when warranted. Do not reward engineering volume. Do not invent citations or claim web access; the bound public-source audit is the only literature evidence available to you.

Requested model endpoint: {requested_model}. The provider-resolved model is recorded outside the prompt.
Exact candidate contract SHA-256: {contract_sha}

The narrow surviving object is the serving-induced observation kernel of an external persistent skill updater. The exact causal intervention keeps the task, initial skill, K=8 generated pool, served winner, actor, verifier, updater, and K=1 probes fixed, and changes only the learning projection. Rejected-Witness is a minimal intervention, not a claimed novel algorithm. SkillCAT-style contrast, duplicated-winner, random-nonwinner, precommitted rollout-0, winner-only, and longitudinal RethinkSkill feedback views are mandatory controls or baselines.

Judge the exact contract, not an imagined broader paper. Distinguish protocol qualification from scientific evidence. No scientific outcome has been run yet.
"""
    if round_number == 1:
        schema = json.dumps(round1_schema(), ensure_ascii=False, indent=2)
        task = f"""
ROUND 1 — BLIND EXACT-CONTRACT REVIEW
You have not seen the other reviewer. Determine whether this exact F0-R4 contract is sufficiently identifiable and falsifiable to authorize only the 12-task E0 pilot. In particular:
1. Does identical-pool cloned-state design isolate the learning projection despite provider stochasticity?
2. Are rescue-support and family gates pre-outcome and non-selective?
3. Is the evidence packet the only treatment after accounting for parser/validation behavior?
4. Do duplicated-winner, random-nonwinner, precommitted, and SkillCAT-style controls address token, diversity, and direct-method reductions?
5. Is n=12 stream-level inference adequate for the E1 decision, or does the contract overclaim?
6. Are SpreadsheetBench Verified-400 and SpreadsheetBench 2 assigned non-shopping roles?
7. Name only blocking issues. Do not demand extra benchmarks or models for volume.

Return exactly one JSON object and no markdown using this schema:
{schema}

INDEPENDENCE: independent=true; exposed_to_other_review=false.
"""
    else:
        other_model = next(model for model in REQUESTED_MODELS if model != requested_model)
        own = compact_review(load_round1(requested_model))
        other = compact_review(load_round1(other_model))
        schema = json.dumps(round2_schema(), ensure_ascii=False, indent=2)
        task = f"""
ROUND 2 — CROSS-EXPOSED FINAL PRE-EXECUTION ADJUDICATION
You now see both blind reviews. Attack the other review, concede valid points, and give a final GO/HOLD/STOP recommendation for only the E0 pilot. E1 must remain conditional on E0 support and integrity. Do not authorize paper claims.

YOUR BLIND REVIEW:
{own}

OTHER BLIND REVIEW:
{other}

Return exactly one JSON object and no markdown using this schema:
{schema}

EXPOSURE: independent=false; exposed_to_other_review=true; exposure_scope=both_round1_reviews.
"""
    return preamble + task + "\nBOUND DOSSIER START\n" + dossier + "\nBOUND DOSSIER END\n"


def required_fields(round_number: int) -> tuple[str, ...]:
    if round_number == 1:
        return tuple(round1_schema().keys())
    return tuple(round2_schema().keys())


def call_model(
    client: ArkResponsesClient,
    *,
    round_number: int,
    requested_model: str,
    expected_resolved: str,
    dossier: str,
    dossier_hashes: dict[str, str],
    contract_sha: str,
    max_output_tokens: int,
) -> dict[str, Any]:
    prompt = build_prompt(round_number, requested_model, dossier, contract_sha)
    round_dir = OUT_ROOT / f"round{round_number}"
    prompt_path = round_dir / f"{safe_slug(requested_model)}-prompt.md"
    atomic_text(prompt_path, prompt)
    base: dict[str, Any] = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-f0-r4-preexecution-review-response",
        "round": round_number,
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "requested_model": requested_model,
        "expected_resolved_model": expected_resolved,
        "route": client.settings.base_url,
        "provider_retry_limit": client.settings.max_retries,
        "provider_generation_attempts": 1,
        "hidden_provider_retry_used": False,
        "thinking_requested": "disabled",
        "automatic_thinking_compatibility_fallback_allowed": False,
        "temperature": 0,
        "max_output_tokens": max_output_tokens,
        "prompt_path": str(prompt_path.relative_to(ROOT)),
        "prompt_sha256": sha_text(prompt),
        "contract_sha256": contract_sha,
        "dossier_file_sha256": dossier_hashes,
        "independent": round_number == 1,
        "exposed_to_other_review": round_number > 1,
        "scientific_authority": False,
        "experiment_authority": False,
        "paper_promotion_authority": False,
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
            receipt = exc.receipt()
            base["initial_response_state"] = {
                "status": receipt.get("status"),
                "requested_model": receipt.get("requested_model"),
                "resolved_model": receipt.get("resolved_model"),
                "incomplete_reason": receipt.get("incomplete_reason"),
                "response_id_sha256": sha_text(str(receipt.get("response_id") or "")),
            }
            if not exc.response_id:
                raise
            polled = client.poll_response(exc.response_id, max_polls=4, interval_seconds=1.0)
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
        review = extract_json_object(raw)
        missing = [field for field in required_fields(round_number) if field not in review]
        ack = str(review.get("contract_sha256_acknowledged") or "")
        if ack != contract_sha:
            missing.append("contract_sha256_acknowledged_exact")
        base.update(
            {
                "review": review,
                "parse_valid": not missing,
                "missing_required_fields": missing,
                "status": "COMPLETED" if not missing else "FAIL_SCHEMA",
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
    parser.add_argument("--round", type=int, choices=(1, 2), required=True)
    parser.add_argument("--models", nargs="*", default=list(REQUESTED_MODELS))
    parser.add_argument("--max-output-tokens", type=int, default=5000)
    args = parser.parse_args()

    unknown = set(args.models) - set(REQUESTED_MODELS)
    if unknown:
        raise SystemExit(f"unsupported models: {sorted(unknown)}")
    expected = expected_models()
    if len(set(expected.values())) != len(expected):
        raise RuntimeError("reviewer resolved identities are not distinct")

    load_env_file(args.env_file)
    source = ArkSettings.from_env(required=True)
    if source.base_url.rstrip("/") != PLAN_BASE_URL:
        raise RuntimeError("preexecution review refuses non-Plan Ark route")
    settings = ArkSettings(
        api_key=source.api_key,
        base_url=source.base_url,
        default_model=source.default_model,
        timeout_seconds=max(240.0, source.timeout_seconds),
        max_retries=0,
    )
    client = ArkResponsesClient(settings)
    dossier, dossier_hashes = load_dossier()
    contract_rel = "generated/e2-r17-f0-r4-frozen-candidate-contract-20260828.json"
    contract_sha = dossier_hashes[contract_rel]

    rows: list[dict[str, Any]] = []
    for model in args.models:
        payload = call_model(
            client,
            round_number=args.round,
            requested_model=model,
            expected_resolved=expected[model],
            dossier=dossier,
            dossier_hashes=dossier_hashes,
            contract_sha=contract_sha,
            max_output_tokens=args.max_output_tokens,
        )
        path = OUT_ROOT / f"round{args.round}" / f"{safe_slug(model)}.json"
        atomic_json(path, payload)
        row = {
            "requested_model": model,
            "resolved_model": payload.get("resolved_model"),
            "status": payload.get("status"),
            "parse_valid": payload.get("parse_valid"),
            "verdict": (payload.get("review") or {}).get(
                "verdict" if args.round == 1 else "final_verdict"
            ),
            "usage": payload.get("usage") or {},
            "artifact": str(path.relative_to(ROOT)),
            "artifact_sha256": sha_bytes(path.read_bytes()),
            "raw_text_sha256": payload.get("raw_text_sha256"),
        }
        rows.append(row)
        print(json.dumps(row, ensure_ascii=False))

    # Rebuild the round summary from every available model artifact. This keeps
    # one-model invocations resumable without overwriting an earlier review.
    summary_rows: list[dict[str, Any]] = []
    for model in REQUESTED_MODELS:
        path = OUT_ROOT / f"round{args.round}" / f"{safe_slug(model)}.json"
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        summary_rows.append(
            {
                "requested_model": model,
                "resolved_model": payload.get("resolved_model"),
                "status": payload.get("status"),
                "parse_valid": payload.get("parse_valid"),
                "verdict": (payload.get("review") or {}).get(
                    "verdict" if args.round == 1 else "final_verdict"
                ),
                "usage": payload.get("usage") or {},
                "artifact": str(path.relative_to(ROOT)),
                "artifact_sha256": sha_bytes(path.read_bytes()),
                "raw_text_sha256": payload.get("raw_text_sha256"),
            }
        )
    expected_count = len(REQUESTED_MODELS)
    complete = (
        len(summary_rows) == expected_count
        and all(row.get("status") == "COMPLETED" for row in summary_rows)
    )
    summary = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-f0-r4-preexecution-review-round-summary",
        "round": args.round,
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "contract_sha256": contract_sha,
        "route": settings.base_url,
        "provider_retry_limit": settings.max_retries,
        "reviews": summary_rows,
        "resolved_identity_independence": (
            len(summary_rows) == expected_count
            and len({row.get("resolved_model") for row in summary_rows}) == expected_count
        ),
        "status": "COMPLETED" if complete else "INCOMPLETE",
        "scientific_authority": False,
        "experiment_authority": False,
        "paper_promotion_authority": False,
        "submission_authority": False,
    }
    summary_path = OUT_ROOT / f"round{args.round}" / "summary.json"
    atomic_json(summary_path, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if summary["status"] == "COMPLETED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
