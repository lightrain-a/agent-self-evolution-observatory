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

from research_pipeline.ark_provider import ArkResponseStateError, ArkResponsesClient, ArkSettings, extract_json_object
from research_pipeline.config import load_env_file

PLAN_BASE_URL = "https://ark.cn-beijing.volces.com/api/plan/v3"
MODELS = ("deepseek-v4-pro", "kimi-k3")
PLAN_PATH = ROOT / "generated/e2-r17-experiment-plan-v1-20260828.json"
IDENTITY_PATH = ROOT / "generated/e2-r17-experiment-plan-v1-model-identity-qualification-20260828.json"
OUT_ROOT = ROOT / "generated/e2-r17-experiment-plan-v1-review-20260828"
DOSSIER_PATHS = (
    PLAN_PATH,
    ROOT / "consultations/e2-r17-experiment-plan-v1-20260828.md",
    ROOT / "generated/e2-r17-baseline-model-choice-audit-20260828.json",
    ROOT / "consultations/e2-r17-baseline-model-choice-audit-20260828.md",
    ROOT / "generated/e2-r17-e0-analysis-20260828.json",
    ROOT / "generated/e2-r17-e0-pilot-analysis-20260828.json",
    ROOT / "generated/e2-r17-e0-go-hold-stop-20260828.json",
    ROOT / "generated/e2-r17-f0-r4-frozen-candidate-contract-20260828.json",
    ROOT / "consultations/e2-r17-public-dataset-and-baseline-audit-20260828.md",
    IDENTITY_PATH,
)


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_text(text: str) -> str:
    return sha_bytes(text.encode("utf-8"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value)


def sanitize_error(value: str) -> str:
    value = re.sub(r"resp_[A-Za-z0-9_]+", "resp_[REDACTED]", str(value))
    value = re.sub(r"Request id:\s*[A-Za-z0-9_]+", "Request id: [REDACTED]", value)
    return value[:1000]


def identity_map() -> dict[str, str]:
    payload = json.loads(IDENTITY_PATH.read_text(encoding="utf-8"))
    if payload.get("status") != "PASS":
        raise RuntimeError("review-tranche identity qualification is not PASS")
    rows = {row["requested_model"]: row for row in payload.get("models") or []}
    resolved = {model: str(rows[model]["resolved_model"]) for model in MODELS}
    if len(set(resolved.values())) != len(MODELS):
        raise RuntimeError("reviewer identities are not distinct")
    return resolved


def dossier() -> tuple[str, dict[str, str]]:
    chunks: list[str] = []
    hashes: dict[str, str] = {}
    for path in DOSSIER_PATHS:
        if not path.exists():
            raise FileNotFoundError(path)
        raw = path.read_bytes()
        rel = str(path.relative_to(ROOT))
        hashes[rel] = sha_bytes(raw)
        chunks.append(f"\n===== BOUND ARTIFACT: {rel} =====\n{raw.decode('utf-8')}\n")
    return "".join(chunks), hashes


def schema() -> dict[str, Any]:
    return {
        "plan_sha256_acknowledged": "",
        "verdict": "PASS_TO_V2|REVISE_BEFORE_ANY_PILOT|STOP_PROGRAM",
        "scientific_chain_coherent": False,
        "pilot_is_outcome_blind": False,
        "e0_hold_respected": False,
        "model_selection_assessment": "",
        "baseline_fidelity_assessment": "",
        "benchmark_and_split_assessment": "",
        "sample_size_and_statistics_assessment": "",
        "checkpoint_and_resume_assessment": "",
        "budget_and_matrix_assessment": "",
        "decisive_experiment_and_stop_assessment": "",
        "fatal_or_blocking_issues": [
            {"priority": "P0|P1", "issue": "", "why_blocking": "", "exact_v2_repair": ""}
        ],
        "required_v2_changes": [
            {"priority": "P0|P1|P2", "target": "", "change": "", "verdict_relevance": ""}
        ],
        "nonblocking_improvements": [""],
        "pilot_recommendation_after_v2": "ALLOW_OUTCOME_BLIND_RUNTIME_PILOTS|HOLD|STOP",
        "e0_full_extension_recommendation": "REVIEW_SEPARATE_CONTRACT|HOLD|STOP",
        "e1_recommendation": "HOLD_UNTIL_E0_FULL_AND_V3|STOP",
        "paper_claim_authority": False,
        "single_sentence_verdict": "",
    }


def prompt_for(model: str, bound: str, plan_sha: str) -> str:
    spec = json.dumps(schema(), ensure_ascii=False, indent=2)
    return f"""You are an independent adversarial experiment-design reviewer for E2-R17, a prospective ICLR paper. You are blind to the other reviewer. This consultation has zero experiment, GPU, paper-promotion, front-end, or submission authority.

Requested reviewer endpoint: {model}
Exact Experiment Plan V1 SHA-256: {plan_sha}

Evaluate the bound plan, not an imagined broader project. Recommend STOP when the central chain is incoherent. Do not reward experiment volume. Do not invent citations or claim outside web access; the bound primary-source audit is the literature record for this review.

Central object: a best-of-K acting selector and an updater-visible learning projection operate on the same generated trajectory pool. E0 has one rescue task in one family, so E1 is HOLD pending the predeclared 54-task support gate. The plan proposes E1 exact-same-pool causality, public benchmark transport, prospective prediction, multi-round closure, and topology controls.

Audit these exact issues:
1. Is V1 genuinely sequential, or can later public results leak back to rescue E1?
2. Does model selection follow baseline/common-model/capability-spread logic without choosing models by R17 gain?
3. Are actor and updater roles separated and is freezing DeepSeek as updater justified or confounded?
4. Which baselines are exact official implementations versus paper-spec reconstructions, and are labels fair?
5. Is the proposed Verified-400 16/160/24/200 split defensible and non-shopping? Does the one-step 20-stream design estimate the claimed public effectiveness?
6. Is SkillEvolBench scientifically compatible with the same-pool object, especially because it uses a native updater?
7. Are scientific units, sample sizes, paired tests, hierarchical bootstrap, repeated partitions/seeds, and cross-model averages valid without pseudoreplication?
8. Are Pilot thresholds outcome-blind and sufficient? Flag any threshold that still permits model cherry-picking.
9. Is checkpoint/resume granular enough to prevent duplicated provider calls and lost results?
10. Are call/token/GPU/API budgets realistic enough to decide scope? Identify any hidden multiplicative cost.
11. Are E0, E1, public, prediction, multi-round, and topology STOP conditions decisive rather than movable?
12. Name only verdict-relevant V2 changes. Do not demand a benchmark/model zoo for breadth.

Return exactly one JSON object and no markdown using this schema:
{spec}

Set `plan_sha256_acknowledged` to the exact SHA above. Keep `paper_claim_authority` false. A PASS_TO_V2 verdict means the plan may be revised and then receive separate Pilot contracts; it does not authorize any scientific execution.

INDEPENDENCE: independent=true; exposed_to_other_review=false.

BOUND DOSSIER START
{bound}
BOUND DOSSIER END
"""


def required_fields() -> tuple[str, ...]:
    return tuple(schema().keys())


def call(
    client: ArkResponsesClient,
    *,
    model: str,
    expected_resolved: str,
    bound: str,
    hashes: dict[str, str],
    plan_sha: str,
    max_output_tokens: int,
) -> dict[str, Any]:
    prompt = prompt_for(model, bound, plan_sha)
    prompt_path = OUT_ROOT / f"{slug(model)}-prompt.md"
    atomic_text(prompt_path, prompt)
    base: dict[str, Any] = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-experiment-plan-v1-independent-review",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "requested_model": model,
        "expected_resolved_model": expected_resolved,
        "route": client.settings.base_url,
        "provider_retry_limit": client.settings.max_retries,
        "provider_generation_attempts": 1,
        "hidden_provider_retry_used": False,
        "thinking_requested": "disabled",
        "temperature": 0,
        "max_output_tokens": max_output_tokens,
        "prompt_path": str(prompt_path.relative_to(ROOT)),
        "prompt_sha256": sha_text(prompt),
        "plan_sha256": plan_sha,
        "dossier_file_sha256": hashes,
        "independent": True,
        "exposed_to_other_review": False,
        "scientific_authority": False,
        "experiment_authority": False,
        "paper_promotion_authority": False,
        "submission_authority": False,
    }
    try:
        try:
            result = client.respond(
                prompt,
                model=model,
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
        missing = [field for field in required_fields() if field not in review]
        if str(review.get("plan_sha256_acknowledged") or "") != plan_sha:
            missing.append("plan_sha256_acknowledged_exact")
        if review.get("paper_claim_authority") is not False:
            missing.append("paper_claim_authority_false")
        base.update(
            {
                "review": review,
                "parse_valid": not missing,
                "missing_required_fields": missing,
                "status": "COMPLETED" if not missing else "FAIL_SCHEMA",
            }
        )
    except Exception as exc:  # noqa: BLE001
        message = str(exc)
        subscription = "InvalidSubscription" in message or "valid AgentPlan subscription" in message
        base.update(
            {
                "status": "HOLD_PROVIDER_SUBSCRIPTION" if subscription else "FAIL_PROVIDER_PROTOCOL",
                "error_type": type(exc).__name__,
                "error_message_sanitized": "Ark Plan subscription unavailable" if subscription else sanitize_error(message),
                "error_sha256": sha_text(message),
            }
        )
    return base


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--models", nargs="+", choices=MODELS, default=list(MODELS))
    parser.add_argument("--max-output-tokens", type=int, default=6500)
    args = parser.parse_args()

    expected = identity_map()
    bound, hashes = dossier()
    plan_sha = hashes[str(PLAN_PATH.relative_to(ROOT))]
    load_env_file(args.env_file)
    source = ArkSettings.from_env(required=True)
    if source.base_url.rstrip("/") != PLAN_BASE_URL:
        raise RuntimeError("V1 review refuses any non-Ark-Plan route")
    client = ArkResponsesClient(
        ArkSettings(
            api_key=source.api_key,
            base_url=source.base_url,
            default_model=source.default_model,
            timeout_seconds=max(300.0, source.timeout_seconds),
            max_retries=0,
        )
    )

    for model in args.models:
        path = OUT_ROOT / f"{slug(model)}.json"
        if path.exists():
            print(json.dumps({"requested_model": model, "status": "SKIP_EXISTING_NO_REPOST", "artifact": str(path.relative_to(ROOT))}))
            continue
        payload = call(
            client,
            model=model,
            expected_resolved=expected[model],
            bound=bound,
            hashes=hashes,
            plan_sha=plan_sha,
            max_output_tokens=args.max_output_tokens,
        )
        atomic_json(path, payload)
        print(json.dumps({
            "requested_model": model,
            "resolved_model": payload.get("resolved_model"),
            "status": payload.get("status"),
            "verdict": (payload.get("review") or {}).get("verdict"),
            "artifact": str(path.relative_to(ROOT)),
            "artifact_sha256": sha_bytes(path.read_bytes()),
        }, ensure_ascii=False))

    rows: list[dict[str, Any]] = []
    for model in MODELS:
        path = OUT_ROOT / f"{slug(model)}.json"
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows.append({
            "requested_model": model,
            "resolved_model": payload.get("resolved_model"),
            "status": payload.get("status"),
            "parse_valid": payload.get("parse_valid"),
            "verdict": (payload.get("review") or {}).get("verdict"),
            "pilot_recommendation_after_v2": (payload.get("review") or {}).get("pilot_recommendation_after_v2"),
            "e0_full_extension_recommendation": (payload.get("review") or {}).get("e0_full_extension_recommendation"),
            "artifact": str(path.relative_to(ROOT)),
            "artifact_sha256": sha_bytes(path.read_bytes()),
            "raw_text_sha256": payload.get("raw_text_sha256"),
            "usage": payload.get("usage") or {},
        })
    complete = len(rows) == len(MODELS) and all(row["status"] == "COMPLETED" for row in rows)
    summary = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-experiment-plan-v1-independent-review-summary",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "plan_sha256": plan_sha,
        "identity_qualification_sha256": hashes[str(IDENTITY_PATH.relative_to(ROOT))],
        "route": client.settings.base_url,
        "provider_retry_limit": 0,
        "reviews": rows,
        "resolved_identity_independence": len(rows) == 2 and len({row["resolved_model"] for row in rows}) == 2,
        "status": "COMPLETED" if complete else "INCOMPLETE",
        "authority": {
            "planning_revision": complete,
            "runtime_pilot": False,
            "e0_full_calls": False,
            "e1_calls": False,
            "paper_promotion": False,
            "submission": False,
        },
    }
    atomic_json(OUT_ROOT / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
