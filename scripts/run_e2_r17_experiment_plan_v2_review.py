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
PLAN_PATH = ROOT / "generated/e2-r17-experiment-plan-v2-20260828.json"
IDENTITY_PATH = ROOT / "generated/e2-r17-experiment-plan-v2-model-identity-qualification-20260828.json"
OUT_ROOT = ROOT / "generated/e2-r17-experiment-plan-v2-review-20260828"
DOSSIER_PATHS = (
    PLAN_PATH,
    ROOT / "consultations/e2-r17-experiment-plan-v2-20260828.md",
    ROOT / "generated/e2-r17-theory-correction-mixed-pool-20260828.json",
    ROOT / "consultations/e2-r17-theory-correction-mixed-pool-20260828.md",
    ROOT / "generated/e2-r17-published-baseline-audit-v2-20260828.json",
    ROOT / "consultations/e2-r17-published-baseline-audit-v2-20260828.md",
    ROOT / "generated/e2-r17-e0-analysis-20260828.json",
    ROOT / "generated/e2-r17-e0-go-hold-stop-20260828.json",
    IDENTITY_PATH,
)


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_text(text: str) -> str:
    return sha_bytes(text.encode("utf-8"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(path)


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(text, encoding="utf-8")
    temp.replace(path)


def slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value)


def sanitize_error(value: str) -> str:
    text = re.sub(r"resp_[A-Za-z0-9_]+", "resp_[REDACTED]", str(value))
    text = re.sub(r"Request id:\s*[A-Za-z0-9_]+", "Request id: [REDACTED]", text)
    return text[:1200]


def identity_map() -> dict[str, str]:
    payload = json.loads(IDENTITY_PATH.read_text(encoding="utf-8"))
    if payload.get("status") != "PASS":
        raise RuntimeError("V2 reviewer model identity qualification is not PASS")
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
        "verdict": "PASS_TO_RUNTIME_PILOT|REVISE_V2_BEFORE_PILOT|STOP_PROGRAM",
        "novelty_against_reasoningbank": "",
        "theory_estimand_assessment": "",
        "historical_e0_preservation_assessment": "",
        "mixed_support_gate_assessment": "",
        "stream_unit_and_statistics_assessment": "",
        "equivalence_stop_rule_assessment": "",
        "evidence_token_budget_assessment": "",
        "published_baseline_fidelity_assessment": "",
        "source_faithful_vs_unified_lane_assessment": "",
        "benchmark_selection_assessment": "",
        "model_selection_assessment": "",
        "checkpoint_resume_assessment": "",
        "budget_assessment": "",
        "fatal_or_blocking_issues": [
            {"priority": "P0|P1", "issue": "", "why_blocking": "", "exact_v3_repair": ""}
        ],
        "required_v3_changes": [
            {"priority": "P0|P1|P2", "target": "", "change": "", "verdict_relevance": ""}
        ],
        "nonblocking_improvements": [""],
        "runtime_pilot_recommendation": "ALLOW_OUTCOME_BLIND_RUNTIME_PILOTS|HOLD|STOP",
        "e1_pool_support_phase_recommendation": "ALLOW_ONLY_AFTER_V3_CONTRACT|HOLD|STOP",
        "e1_updater_recommendation": "HOLD_UNTIL_SUPPORT_GATE_AND_V3|STOP",
        "paper_claim_authority": False,
        "single_sentence_verdict": "",
    }


def prompt_for(model: str, bound: str, plan_sha: str) -> str:
    spec = json.dumps(schema(), ensure_ascii=False, indent=2)
    return f"""You are an independent adversarial experiment-design reviewer for E2-R17 / Compute Shielding, a prospective top-conference paper. You are blind to the other reviewer. This consultation has zero scientific-experiment, GPU, paper-promotion, frontend, or submission authority.

Requested reviewer endpoint: {model}
Exact Experiment Plan V2 SHA-256: {plan_sha}

Review only the bound dossier. Recommend STOP if the remaining contribution collapses to the already-published statement that failed trajectories can help memory. Do not reward experiment volume. Do not invent literature beyond the bound published-baseline audit.

The V2 theory correction distinguishes:
- rescue censoring, which exactly explains acting gain versus the precommitted rollout; and
- mixed-pool support M_K, on which a failure-aware learning projection can differ from winner-only even when rollout-0 already succeeds.

The proposed primary intervention is one-slot Mixed-Rejected-Witness (MRW): on mixed pools it exposes the deterministic lowest-index failed nonwinner to the updater; on non-mixed pools it equals Winner-only. Acting always serves the exact same winner. Therefore Delta_K = M_K * delta_K by conditioning, but theory does NOT assume delta_K > 0.

Published collision: ReasoningBank/MaTTS is ICLR 2026 and already learns from successful and failed trajectories generated with test-time scaling. Headline published baselines are ReasoningBank, PolySkill, ACE, and AWM, with SAGE extended. ArXiv-only works are related/collision context, not headline baselines.

Audit these exact issues:
1. Is the proposed novelty actually distinct from ReasoningBank, or is the exact-same-pool selector framing cosmetic?
2. Is mixed-pool mass M_K the correct treatment-support quantity for MRW? Is the factorization Delta=M*delta causal/identified under the stated cloned-stream design?
3. Does preserving the old E0 HOLD while superseding only the future support estimand avoid post-hoc rewriting?
4. Are the pre-treatment support thresholds (24/96 mixed, 8/12 exposed streams, 4/6 families) defensible, or arbitrary enough to require a different predeclared support rule?
5. Is 12 paired streams with 18 common held-out probes a valid independent-unit design? Is the exact 2^12 sign-flip test valid, and is there pseudoreplication anywhere?
6. Is +/-1/18 as the practical-equivalence margin scientifically defensible? Distinguish qualified STOP from merely underpowered HOLD.
7. Can the one-slot WIN vs MRW contrast still be explained by evidence-token length or truncation? State the cleanest pre-Pilot repair.
8. Are post-GO diagnostic controls (Full Pool, random nonwinner, success nonwinner, ReasoningBank-style aggregation) sufficient to distinguish failure-specific value from generic branch diversity or extra information?
9. Is the published baseline hierarchy fair and current? Are implementation caveats for ReasoningBank and PolySkill handled honestly?
10. Is splitting source-faithful reproduction from unified reruns necessary and sufficient given no common published model? Does current Ark-only credential availability create a fatal blocker or merely a source-lane blocker?
11. Are WebArena primary and AppWorld secondary the right external benchmarks after E1 GO? Should SpreadsheetBench remain additional rather than headline-only?
12. Does V2 keep model selection outcome-blind and avoid pretending Qwen/DeepSeek are common published models?
13. Are checkpoint, missing-unit resume, and no-relaunch-after-502 rules sufficient?
14. What exact P0/P1 changes must be made before any runtime Pilot or E1 pool-generation authorization?

Return exactly one JSON object and no markdown using this schema:
{spec}

Set `plan_sha256_acknowledged` exactly to the SHA above. Keep `paper_claim_authority` false. `PASS_TO_RUNTIME_PILOT` authorizes only separate outcome-blind runtime Pilot contracts; it never authorizes E1 scientific execution.

INDEPENDENCE: independent=true; exposed_to_other_review=false.

BOUND DOSSIER START
{bound}
BOUND DOSSIER END
"""


def call(client: ArkResponsesClient, *, model: str, expected_resolved: str, bound: str, hashes: dict[str, str], plan_sha: str, max_output_tokens: int) -> dict[str, Any]:
    prompt = prompt_for(model, bound, plan_sha)
    prompt_path = OUT_ROOT / f"{slug(model)}-prompt.md"
    atomic_text(prompt_path, prompt)
    base: dict[str, Any] = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-experiment-plan-v2-independent-review",
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
                "resolved_model": receipt.get("resolved_model"),
                "incomplete_reason": receipt.get("incomplete_reason"),
                "response_id_sha256": sha_text(str(receipt.get("response_id") or "")),
            }
            if not exc.response_id:
                raise
            polled = client.poll_response(exc.response_id, max_polls=4, interval_seconds=1.0)
            if not polled.get("text"):
                return {**base, "status": "HOLD_PROVIDER_RESPONSE_STATE", "polled_status": polled.get("status"), "poll_count": polled.get("poll_count")}
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
        base.update({
            "resolved_model": resolved,
            "resolved_model_matches_qualification": resolved == expected_resolved,
            "provider_status": result.get("status"),
            "response_id_sha256": sha_text(str(result.get("response_id") or "")),
            "usage": result.get("usage") or {},
            "raw_text": raw,
            "raw_text_sha256": sha_text(raw),
            "get_poll_recovery": bool(result.get("get_poll_recovery", False)),
            "poll_count": result.get("poll_count", 0),
        })
        if resolved != expected_resolved:
            base["status"] = "FAIL_RESOLVED_MODEL_DRIFT"
            return base
        review = extract_json_object(raw)
        missing = [field for field in schema().keys() if field not in review]
        if str(review.get("plan_sha256_acknowledged") or "") != plan_sha:
            missing.append("plan_sha256_acknowledged_exact")
        if review.get("paper_claim_authority") is not False:
            missing.append("paper_claim_authority_false")
        base.update({"review": review, "parse_valid": not missing, "missing_required_fields": missing, "status": "COMPLETED" if not missing else "FAIL_SCHEMA"})
    except Exception as exc:  # noqa: BLE001
        message = str(exc)
        subscription = "InvalidSubscription" in message or "valid AgentPlan subscription" in message
        base.update({
            "status": "HOLD_PROVIDER_SUBSCRIPTION" if subscription else "FAIL_PROVIDER_PROTOCOL",
            "error_type": type(exc).__name__,
            "error_message_sanitized": "Ark Plan subscription unavailable" if subscription else sanitize_error(message),
            "error_sha256": sha_text(message),
        })
    return base


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--models", nargs="+", choices=MODELS, default=list(MODELS))
    parser.add_argument("--max-output-tokens", type=int, default=6000)
    args = parser.parse_args()

    expected = identity_map()
    bound, hashes = dossier()
    plan_sha = hashes[str(PLAN_PATH.relative_to(ROOT))]
    load_env_file(args.env_file)
    source = ArkSettings.from_env(required=True)
    if source.base_url.rstrip("/") != PLAN_BASE_URL:
        raise RuntimeError("V2 review refuses any non-Ark-Plan route")
    settings = ArkSettings(api_key=source.api_key, base_url=source.base_url, default_model=source.default_model, timeout_seconds=300.0, max_retries=0)
    client = ArkResponsesClient(settings)

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    rows = []
    for model in args.models:
        row = call(client, model=model, expected_resolved=expected[model], bound=bound, hashes=hashes, plan_sha=plan_sha, max_output_tokens=args.max_output_tokens)
        atomic_json(OUT_ROOT / f"{slug(model)}.json", row)
        rows.append(row)

    completed = [row for row in rows if row.get("status") == "COMPLETED"]
    verdicts = {row["requested_model"]: row.get("review", {}).get("verdict") for row in completed}
    summary = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-experiment-plan-v2-dual-review-summary",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "plan_sha256": plan_sha,
        "reviewers": [row["requested_model"] for row in rows],
        "resolved_models": {row["requested_model"]: row.get("resolved_model") for row in rows},
        "statuses": {row["requested_model"]: row.get("status") for row in rows},
        "verdicts": verdicts,
        "independent": True,
        "exposed_to_other_review": False,
        "scientific_authority": False,
        "experiment_authority": False,
        "paper_claim_authority": False,
        "all_completed": len(completed) == len(rows),
        "all_allow_runtime_pilot": len(completed) == len(rows) and all(row.get("review", {}).get("runtime_pilot_recommendation") == "ALLOW_OUTCOME_BLIND_RUNTIME_PILOTS" for row in completed),
    }
    atomic_json(OUT_ROOT / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if summary["all_completed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
