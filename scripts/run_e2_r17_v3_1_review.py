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
REPAIR = ROOT / "generated/e2-r17-v3-1-causal-purity-repair-20260828.json"
IDENTITY = ROOT / "generated/e2-r17-v3-1-model-identity-qualification-20260828.json"
OUT_ROOT = ROOT / "generated/e2-r17-v3-1-review-20260828"
MINDMEMOS_ROOT = Path("/data/wyt/evidence-substrates/MindMemOS-20260817")

DOSSIER: tuple[tuple[str, Path], ...] = (
    ("v3_1_repair_json", REPAIR),
    ("v3_1_repair_md", ROOT / "consultations/e2-r17-v3-1-causal-purity-repair-20260828.md"),
    ("v3_1_upstream_audit", ROOT / "generated/e2-r17-v3-1-upstream-prompt-dataflow-audit-20260828.json"),
    ("v3_1_mechanical_draft_contract", ROOT / "generated/e2-r17-v3-1-mechanical-pilot-draft-contract-20260828.json"),
    ("v3_failure_adjudication", ROOT / "generated/e2-r17-v3-runtime-pilot-failure-adjudication-20260828.json"),
    ("v3_plan", ROOT / "consultations/e2-r17-experiment-plan-v3-20260828.md"),
    ("published_baseline_audit", ROOT / "consultations/e2-r17-published-baseline-audit-v2-20260828.md"),
    ("renderer_v31", ROOT / "research_pipeline/e2_r17_evidence_window_v2.py"),
    ("renderer_v31_tests", ROOT / "research_pipeline/test_e2_r17_evidence_window_v2.py"),
    ("updater_wrapper_v31", ROOT / "research_pipeline/e2_r17_mindmemos_updater.py"),
    ("updater_wrapper_v31_tests", ROOT / "research_pipeline/test_e2_r17_mindmemos_updater_v31.py"),
    ("search_projection_runner", ROOT / "research_pipeline/e2_r17_search_projection_runner.py"),
    ("search_projection_theory", ROOT / "research_pipeline/e2_r17_search_projection_theory.py"),
    ("mechanical_pilot_runner", ROOT / "scripts/run_e2_r17_v3_1_mechanical_pilot.py"),
    ("review_model_identity", IDENTITY),
    ("mindmemos_evolution_first_party", MINDMEMOS_ROOT / "src/mindmemos/mindmemos/pipelines/skill/evolution.py"),
    ("mindmemos_trajectory_summary_prompt_first_party", MINDMEMOS_ROOT / "src/mindmemos/mindmemos/prompts/EN/skills/trajectory_summary.py"),
    ("mindmemos_skill_patch_prompt_first_party", MINDMEMOS_ROOT / "src/mindmemos/mindmemos/prompts/EN/skills/skill_patch.py"),
)


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_text(text: str) -> str:
    return sha_bytes(text.encode("utf-8"))


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


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
    text = re.sub(r"resp_[A-Za-z0-9_]+", "resp_[REDACTED]", str(value))
    text = re.sub(r"Request id:\s*[A-Za-z0-9_]+", "Request id: [REDACTED]", text)
    return text[:1200]


def identity_map() -> dict[str, str]:
    payload = json.loads(IDENTITY.read_text(encoding="utf-8"))
    if payload.get("status") != "PASS":
        raise RuntimeError("V3.1 reviewer identity qualification is not PASS")
    rows = {row["requested_model"]: row for row in payload.get("models") or []}
    resolved = {model: str(rows[model]["resolved_model"]) for model in MODELS}
    if len(set(resolved.values())) != len(MODELS):
        raise RuntimeError("V3.1 reviewer identities are not distinct")
    return resolved


def dossier() -> tuple[str, dict[str, str]]:
    chunks: list[str] = []
    hashes: dict[str, str] = {}
    for label, path in DOSSIER:
        if not path.exists():
            raise FileNotFoundError(path)
        raw = path.read_bytes()
        hashes[label] = sha_bytes(raw)
        chunks.append(f"\n===== BOUND ARTIFACT: {label} | {path} =====\n{raw.decode('utf-8')}\n")
    return "".join(chunks), hashes


def schema() -> dict[str, Any]:
    return {
        "repair_sha256_acknowledged": "",
        "verdict": "PASS_TO_FRESH_ZERO_PROVIDER_MECHANICAL_PILOT|REVISE_V31_BEFORE_PILOT|STOP_PROGRAM",
        "stream_level_theory_assessment": "",
        "same_pool_estimand_assessment": "",
        "selected_evidence_score_semantics_assessment": "",
        "arm_blinding_and_upstream_dataflow_assessment": "",
        "exact_retokenized_parity_assessment": "",
        "source_budget_asymmetry_assessment": "",
        "downstream_truncation_assessment": "",
        "reasoningbank_novelty_boundary_assessment": "",
        "mechanical_pilot_scope_assessment": "",
        "checkpoint_resume_assessment": "",
        "remaining_blockers": [
            {"priority": "P0|P1", "issue": "", "why_blocking": "", "exact_repair": ""}
        ],
        "nonblocking_notes": [""],
        "mechanical_pilot_recommendation": "ALLOW_FRESH_ZERO_PROVIDER_MECHANICAL_PILOT|HOLD|STOP",
        "provider_runtime_pilot_recommendation": "HOLD|STOP",
        "e1_a_recommendation": "HOLD|STOP",
        "e1_b_recommendation": "HOLD|STOP",
        "paper_claim_authority": False,
        "single_sentence_verdict": "",
    }


def prompt_for(model: str, bound: str, repair_sha: str) -> str:
    spec = json.dumps(schema(), ensure_ascii=False, indent=2)
    return f"""You are an independent adversarial pre-execution reviewer for E2-R17 / Search-Projection Censoring. You are blind to the other reviewer. This consultation has zero scientific-experiment, GPU, provider-runtime, paper-promotion, frontend, or submission authority.

Requested reviewer endpoint: {model}
Exact V3.1 repair SHA-256: {repair_sha}

Context: V3's zero-provider mechanical Pilot correctly failed before scientific-effect evaluation because nominal source-token parity became unequal after final BPE re-tokenization, and because legacy updater-visible packet labels could reveal arm identity. V3.1 is a new design; the failed V3 contract/root cannot be retried.

Published novelty threat: ReasoningBank/MaTTS (ICLR 2026) already learns from successful and failed experiences produced with test-time scaling. Do NOT grant novelty merely because R17 uses failures. R17 survives only if the exact-same-realized-pool acting-selection -> learner-visible-evidence -> future-skill causal object is genuinely distinct and identified.

Audit the actual bound code and the pinned first-party MindMemOS source, not only the authors' prose. In particular:

1. STREAM-LEVEL THEORY: E1 updates eight task packets jointly into one potentially nonlinear skill state. Is V3.1 correct to retract the task-level `Delta=M*delta` expression as an exact learning theorem and instead define `R_s=sum_j M_sj` only as treatment dose/support and `D_s=J_s(MRW)-J_s(WIN)` as the paired stream endpoint? Is `R_s=0 => identical learner inputs` the right exact implication, with no linearity/monotonicity assumed for `R_s>0`?

2. SAME-POOL IDENTIFICATION: under the frozen design, are task, initial skill, exact generated K=8 pools, acting winner, executor, updater implementation, and held-out probes fixed while learner-visible selected evidence changes? Is this enough to identify a learning-projection effect at stream level once hosted-updater stochasticity is screened by WIN-A/WIN-B?

3. SCORE SEMANTICS: inspect first-party MindMemOS `evolution.py` and `skill_patch.py`. The legacy wrapper used the served winner's acting score even for a failed MRW transcript. V3.1 instead places the selected evidence trajectory's verifier score into `payload['score']` while retaining served acting score only in provenance. Is this the scientifically correct treatment semantics, or does it create an impermissible second treatment beyond the evidence projection? Explain precisely. Consider that first-party scored patch prompts explicitly use the score as the primary outcome signal.

4. ARM BLINDING: verify from first-party source whether only `payload.messages` enters the trajectory transcript and whether R17 `r17_*` provenance fields remain outside model-visible prompts. Does the new `BlindedEvidenceUnit` path remove arm/projection/rollout/provenance labels from the actual transcript? Flag any remaining treatment cue.

5. TOKEN PARITY: does `ExactMatchedEvidenceBlockRenderer` correctly solve the V3 BPE splice bug by matching the actual final re-tokenized evidence blocks rather than nominal source slices? Is no-padding deterministic search acceptable?

6. SOURCE-BUDGET ASYMMETRY: historical replay sometimes needs a one-token difference in selected pre-decoding source budget to obtain exact equal final provider-visible token counts. Is the final provider-visible evidence token count the correct fairness budget, or does unequal source slicing create a P0 content-quantity confound requiring a stricter construction? If a repair is needed, specify it before Pilot.

7. DOWNSTREAM TRUNCATION: is freezing `transcript_max_chars>=100000` plus a per-unit assertion sufficient to prevent first-party `_render_transcript` from silently destroying token parity? Is there another truncation or transformation later in the summary/patch path that invalidates the causal comparison?

8. NEGATIVE CONTROL / SCORE: WIN-A and WIN-B are byte-identical treatments before independent hosted-model calls. Does changing selected-evidence scores in MRW interact with the negative-control logic in any problematic way? Negative-control equivalence must be evaluated before MRW.

9. NOVELTY: given the published ReasoningBank collision, is it defensible to position R17 as causal identification of acting-oriented selection changing the experience distribution available to persistent learning, rather than generic failure learning? State if this still looks cosmetic.

10. MECHANICAL PILOT: inspect the draft contract and runner. The fresh Pilot must use only the 12 frozen historical E0 pools, zero provider calls, zero new actor rollouts, no held-out future-skill evaluation, immediate content-addressed checkpointing, SHA-validated missing-unit resume, and a fresh root. Does the code respect this scope? This review may at most allow that fresh zero-provider Pilot.

11. AUTHORITY: even PASS must keep provider runtime Pilot, E1-A, E1-B, scientific outcomes, and paper promotion on HOLD. A later immutable contract is required for each.

Return exactly one JSON object and no markdown using this schema:
{spec}

Set `repair_sha256_acknowledged` exactly to the SHA above. Keep `paper_claim_authority` false. A PASS authorizes only creation/execution of a separately SHA-bound fresh zero-provider mechanical Pilot contract. It does not authorize E1-A or E1-B.

INDEPENDENCE: independent=true; exposed_to_other_review=false.

BOUND DOSSIER START
{bound}
BOUND DOSSIER END
"""


def validate_review_schema(review: dict[str, Any], expected_sha: str) -> list[str]:
    schema_fields = schema()
    missing = [field for field in schema_fields.keys() if field not in review]
    acknowledgement_fields = [
        field for field in schema_fields.keys() if field.endswith("_sha256_acknowledged")
    ]
    if not acknowledgement_fields:
        missing.append("sha256_acknowledgement_field_missing_from_schema")
    for field in acknowledgement_fields:
        if str(review.get(field) or "") != expected_sha:
            missing.append(f"{field}_exact")
    if review.get("paper_claim_authority") is not False:
        missing.append("paper_claim_authority_false")
    return missing


def call(
    client: ArkResponsesClient,
    *,
    model: str,
    expected_resolved: str,
    bound: str,
    hashes: dict[str, str],
    repair_sha: str,
    max_output_tokens: int,
) -> dict[str, Any]:
    prompt = prompt_for(model, bound, repair_sha)
    prompt_path = OUT_ROOT / f"{slug(model)}-prompt.md"
    atomic_text(prompt_path, prompt)
    base: dict[str, Any] = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-v3-1-independent-review",
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
        "repair_sha256": repair_sha,
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
        missing = validate_review_schema(review, repair_sha)
        base.update({
            "review": review,
            "parse_valid": not missing,
            "missing_required_fields": missing,
            "status": "COMPLETED" if not missing else "FAIL_SCHEMA",
        })
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
    repair_sha = sha_file(REPAIR)
    load_env_file(args.env_file)
    source = ArkSettings.from_env(required=True)
    if source.base_url.rstrip("/") != PLAN_BASE_URL:
        raise RuntimeError("V3.1 review refuses any non-Ark-Plan route")
    settings = ArkSettings(
        api_key=source.api_key,
        base_url=source.base_url,
        default_model=source.default_model,
        timeout_seconds=300.0,
        max_retries=0,
    )
    client = ArkResponsesClient(settings)

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for model in args.models:
        row = call(
            client,
            model=model,
            expected_resolved=expected[model],
            bound=bound,
            hashes=hashes,
            repair_sha=repair_sha,
            max_output_tokens=args.max_output_tokens,
        )
        atomic_json(OUT_ROOT / f"{slug(model)}.json", row)
        rows.append(row)

    completed = [row for row in rows if row.get("status") == "COMPLETED"]
    verdicts = {row["requested_model"]: row.get("review", {}).get("verdict") for row in completed}
    recommendations = {
        row["requested_model"]: row.get("review", {}).get("mechanical_pilot_recommendation")
        for row in completed
    }
    summary = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-v3-1-dual-review-summary",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repair_sha256": repair_sha,
        "reviewers": [row["requested_model"] for row in rows],
        "resolved_models": {row["requested_model"]: row.get("resolved_model") for row in rows},
        "statuses": {row["requested_model"]: row.get("status") for row in rows},
        "verdicts": verdicts,
        "mechanical_pilot_recommendations": recommendations,
        "independent": True,
        "exposed_to_other_review": False,
        "scientific_authority": False,
        "experiment_authority": False,
        "paper_claim_authority": False,
        "all_completed": len(completed) == len(rows),
        "all_allow_fresh_zero_provider_mechanical_pilot": (
            len(completed) == len(rows)
            and all(
                row.get("review", {}).get("verdict") == "PASS_TO_FRESH_ZERO_PROVIDER_MECHANICAL_PILOT"
                and row.get("review", {}).get("mechanical_pilot_recommendation") == "ALLOW_FRESH_ZERO_PROVIDER_MECHANICAL_PILOT"
                and row.get("review", {}).get("provider_runtime_pilot_recommendation") == "HOLD"
                and row.get("review", {}).get("e1_a_recommendation") == "HOLD"
                and row.get("review", {}).get("e1_b_recommendation") == "HOLD"
                for row in completed
            )
        ),
    }
    atomic_json(OUT_ROOT / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if summary["all_completed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
