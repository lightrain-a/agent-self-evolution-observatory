#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEBATE = ROOT / "generated/e2-r17-search-projection-debate-20260827"
IDENTITY = ROOT / "generated/e2-r17-search-projection-consultation-model-identity-adjudication-20260827.json"
OUT_JSON = ROOT / "generated/e2-r17-search-projection-debate-adjudication-20260827.json"
OUT_MD = ROOT / "consultations/e2-r17-search-projection-debate-adjudication-20260827.md"
MODELS = ("deepseek-v4-pro", "kimi-k3")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(text, encoding="utf-8")
    temp.replace(path)


def load(round_number: int, model: str) -> tuple[Path, dict[str, Any]]:
    path = DEBATE / f"round{round_number}" / f"{model}.json"
    return path, json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    identity = json.loads(IDENTITY.read_text(encoding="utf-8"))
    expected = {
        model: identity["requested_and_resolved"][model]["resolved"]
        for model in MODELS
    }
    calls: list[dict[str, Any]] = []
    checks: dict[str, bool] = {
        "eight_responses_present": True,
        "all_completed": True,
        "all_parse_valid": True,
        "provider_retry_zero": True,
        "no_hidden_retry": True,
        "resolved_models_match_qualification": True,
        "resolved_model_independence": len(set(expected.values())) == 2,
        "round1_blind": True,
        "round2_to_4_cross_exposed": True,
        "all_zero_scientific_authority": True,
        "all_zero_experiment_authority": True,
    }
    totals = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "calls": 0}
    reviews: dict[int, dict[str, dict[str, Any]]] = {}
    for round_number in range(1, 5):
        reviews[round_number] = {}
        for model in MODELS:
            path, row = load(round_number, model)
            reviews[round_number][model] = row["review"]
            usage = row.get("usage") or {}
            call = {
                "round": round_number,
                "requested_model": model,
                "resolved_model": row.get("resolved_model"),
                "independent": row.get("independent"),
                "exposed_to_other_review": row.get("exposed_to_other_review"),
                "prompt_path": row.get("prompt_path"),
                "prompt_sha256": row.get("prompt_sha256"),
                "response_sha256": row.get("raw_text_sha256"),
                "artifact_path": str(path.relative_to(ROOT)),
                "artifact_sha256": sha(path),
                "usage": usage,
                "status": row.get("status"),
                "parse_valid": row.get("parse_valid"),
                "provider_generation_attempts": row.get("provider_generation_attempts"),
                "provider_retry_limit": row.get("provider_retry_limit"),
                "hidden_provider_retry_used": row.get("hidden_provider_retry_used"),
            }
            calls.append(call)
            totals["calls"] += 1
            for field in ("input_tokens", "output_tokens", "total_tokens"):
                totals[field] += int(usage.get(field) or 0)
            checks["all_completed"] &= row.get("status") == "COMPLETED"
            checks["all_parse_valid"] &= row.get("parse_valid") is True
            checks["provider_retry_zero"] &= row.get("provider_retry_limit") == 0
            checks["no_hidden_retry"] &= row.get("hidden_provider_retry_used") is False
            checks["resolved_models_match_qualification"] &= row.get("resolved_model") == expected[model]
            checks["all_zero_scientific_authority"] &= row.get("scientific_authority") is False
            checks["all_zero_experiment_authority"] &= row.get("experiment_authority") is False
            if round_number == 1:
                checks["round1_blind"] &= row.get("independent") is True and row.get("exposed_to_other_review") is False
            else:
                checks["round2_to_4_cross_exposed"] &= row.get("independent") is False and row.get("exposed_to_other_review") is True
    checks["eight_responses_present"] = len(calls) == 8

    round4_scores = {
        model: {
            "score": reviews[4][model].get("overall_score_1_to_10"),
            "recommendation": reviews[4][model].get("recommendation"),
            "strongest_reject_reason": reviews[4][model].get("strongest_reject_reason"),
        }
        for model in MODELS
    }
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-search-projection-four-round-debate-adjudication",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "branch": subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=ROOT, text=True).strip(),
        "branch_head_before_adjudication": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "status": "SURVIVES_AS_NARROW_F0_R4_CANDIDATE_NOT_EXPERIMENT_AUTHORIZED",
        "checks": checks,
        "models": {
            "deepseek": {"requested": "deepseek-v4-pro", "resolved": expected["deepseek-v4-pro"]},
            "kimi": {"requested": "kimi-k3", "resolved": expected["kimi-k3"]},
            "release_drift": {
                "historical_deepseek": identity.get("historical_deepseek_resolved"),
                "current_deepseek": identity.get("current_deepseek_resolved"),
                "explicitly_adjudicated": identity.get("release_drift_detected") is True,
            },
        },
        "call_ledger": calls,
        "token_ledger": totals,
        "round_outcomes": {
            "round1_blind": {
                "agreement": "The broad phenomenon and CADP components are reduced, but the serving-induced observation-kernel mechanism is not directly reduced.",
                "disagreement": "DeepSeek named TopoCurate the strongest conceptual reduction; Kimi named SkillCAT the strongest direct method/pipeline reduction.",
            },
            "round2_mutual_attack": {
                "agreement": "SkillCAT is the mandatory method baseline; TopoCurate is a mandatory representation/selection collision; one-step and longitudinal estimands must be separated; rollout-0 is an alternative observation kernel, not no censoring.",
                "additional_gates": [
                    "precommit a deterministic rejected-witness rule before outcomes",
                    "freeze a mutually exclusive failure-family partition",
                    "treat validation-gate acceptance as part of the treatment and report it",
                    "replace the historical independent-shadow runner",
                ],
            },
            "round3_single_object": {
                "scientific_object": "Serving-induced selective trajectory logging / the serving-induced observation kernel of an external persistent skill updater.",
                "causal_chain": "best-of-K rescue -> winner-only learning projection removes a rescued failure witness -> positive updater-conditional diagnostic value -> weaker one-step frozen skill",
                "theoretical_prediction": "A precommitted disjoint-family censoring-mass-times-diagnostic-value score must prospectively predict held-out sign and rank; the i.i.d. peak is only a reference model.",
                "decisive_intervention": "Exact same pool, same served winner, same initial skill, updater, verifier and update seed; change only the learning projection; evaluate all resulting skill states with common frozen K=1 held-out probes.",
                "method": "Minimal Rejected-Witness projection. CADP is optional only after the mechanism passes and only if it beats Rejected-Witness under matched budgets.",
                "stop_condition": "STOP on projection-null, duplicated-winner equivalence, prospective prediction failure, or complete reduction by a source-faithful SkillCAT-style baseline.",
            },
            "round4_pc_red_team": {
                "scores": round4_scores,
                "consensus_reject_reason": "No scientific result exists yet; the only defensible mechanism claim depends entirely on the unrun exact-same-pool cloned-state intervention, while CADP and broad failure/branch claims collide with prior work.",
                "verdict_changing_repair": "Freeze a narrow R4 contract, implement and validate a same-pool runner, then run only the decisive cloned-state projection-null experiment first.",
            },
        },
        "final_scientific_adjudication": {
            "surviving_object": "SERVING_INDUCED_OBSERVATION_KERNEL_FOR_PERSISTENT_SKILL_LEARNING",
            "paper_level_claim_not_yet_allowed": True,
            "identity_role": "Definitional measurement identity; not theorem-level novelty.",
            "method_role": "Rejected-Witness is the minimal causal intervention, not an independent algorithmic novelty claim.",
            "deleted_or_demoted_claims": [
                "universal more-search-harms-learning claim",
                "CADP as headline method contribution",
                "novel success/failure pairing",
                "novel first-divergence extraction",
                "novel bounded validation-gated skill editing",
                "mutual-information retention as a substantive contribution",
                "continuous layer-cake identity as a substantive extension",
                "i.i.d. p-star as a natural-task empirical law",
                "one-step projection effect as proof of multi-round reversal",
            ],
            "mandatory_closest_work_and_controls": [
                "SkillCAT-style same-task contrast on the same pools/updater",
                "TopoCurate closest-work boundary",
                "winner-only",
                "precommitted same-pool rollout-0",
                "Rejected-Witness",
                "duplicated-winner token control",
                "random nonwinner control",
            ],
            "next_gate": "F0_R4_CONTRACT_AND_SAME_POOL_RUNNER_PREEXECUTION_REVIEW",
            "experiment_order": [
                "E0 deterministic/pool-law qualification only",
                "E1/F2 exact-same-pool cloned-state projection-null decisive intervention",
                "only on GO: prospective held-out prediction",
                "only on GO: multi-round persistent evolution",
                "only on GO: topology and externality",
            ],
            "stop_without_rescue": [
                "no directional same-pool projection effect",
                "duplicated winner matches Rejected-Witness",
                "effect depends on post-outcome witness/family selection",
                "SkillCAT-style contrast fully reduces the serving-selection interpretation",
                "held-out sign/rank prediction fails",
            ],
            "r16_unchanged": True,
        },
        "authority": {
            "write_f0_r4_candidate": True,
            "freeze_f0_r4_without_final_preexecution_reviews": False,
            "scientific_experiment": False,
            "gpu": False,
            "paper_promotion": False,
            "submission": False,
        },
        "private_credentials_included": False,
        "raw_response_ids_included": False,
    }
    payload["body_sha256"] = csha(payload)
    atomic(OUT_JSON, json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")

    lines = [
        "# E2-R17 Search-Projection Censoring — four-round Kimi × DeepSeek adjudication",
        "",
        f"Date: {payload['created_at_utc']}",
        f"Status: `{payload['status']}`",
        "",
        "## Decision",
        "",
        "R17 survives only as a narrow, pre-experimental mechanism candidate: **serving-induced selective trajectory logging / the serving-induced observation kernel of an external persistent skill updater**. It does not yet qualify as an independent paper, method, or experiment-authorized program.",
        "",
        "The four-round panel removed CADP as the center of the paper. The minimal mechanism-derived intervention is **Rejected-Witness**: keep the served winner fixed, and on a precommitted mixed rescue event route one frozen-rule nonserved failure witness from the same search pool to the updater. The method has no separate novelty claim; it exists to identify the observation-kernel mechanism.",
        "",
        "## Debate integrity",
        "",
        f"- Eight Ark Plan calls completed: {totals['input_tokens']} input tokens, {totals['output_tokens']} output tokens, {totals['total_tokens']} total tokens.",
        f"- DeepSeek resolved identity: `{expected['deepseek-v4-pro']}`; Kimi resolved identity: `{expected['kimi-k3']}`.",
        "- Round 1 was blind and independent; Rounds 2–4 were explicitly cross-exposed.",
        "- Provider retry was zero; no hidden compatibility retry occurred in debate calls.",
        "- Every prompt, response, model identity, usage record, and artifact is content-addressed in the JSON adjudication.",
        "",
        "## Scientific convergence",
        "",
        "**Object.** Search creates `T_K`; acting consumes `a(T_K)`; persistent learning consumes `g(T_K)`. The disputed default is `g=a=winner-only`, which may make updater-visible evidence missing-not-at-random.",
        "",
        "**Causal chain.** Best-of-K rescue improves current acting; winner-only learning hides the rescued failure witness; only if that witness has positive updater-conditional reusable value can future frozen skill become weaker.",
        "",
        "**Theory boundary.** The rescue-censoring equality is an exact measurement identity, not theorem-level novelty. The i.i.d. curve and `p*` are reference calculations. `Gamma × delta` has scientific content only as a precommitted, gated, prospective prediction over a disjoint failure-family partition.",
        "",
        "**Decisive experiment.** Use the exact same search pool, acting winner, initial skill state, updater, verifier, update seed, and held-out K=1 evaluation. Change only `g(T_K)`. A projection-null result stops R17.",
        "",
        "## Mandatory deletions and controls",
        "",
        "Delete novelty claims for success/failure pairing, first divergence, contrastive skill editing, bounded validation, rejected-edit memory, and generic failure utility. SkillCAT is the strongest direct method baseline; TopoCurate is the strongest branch-selection collision. Include duplicated-winner and random-nonwinner controls before attributing an effect to diagnostic evidence.",
        "",
        "## Current verdict",
        "",
        f"DeepSeek PC score: {round4_scores['deepseek-v4-pro']['score']}/10, `{round4_scores['deepseek-v4-pro']['recommendation']}`. Kimi PC score: {round4_scores['kimi-k3']['score']}/10, `{round4_scores['kimi-k3']['recommendation']}`. Both reject the current state because it has zero scientific outcomes, not because the narrow mechanism has already been fully reduced.",
        "",
        "## Next gate",
        "",
        "Create a formal R4 candidate contract and a new same-pool projection runner. Submit both to a final blind pre-execution review by the current resolved Kimi and DeepSeek models. Only if identifiability, falsifiability, strongest reduction control, and leakage prevention all pass may the decisive cloned-state experiment be authorized. R16 remains unchanged.",
        "",
    ]
    atomic(OUT_MD, "\n".join(lines))
    print(json.dumps({"status": payload["status"], "checks": checks, "tokens": totals, "json": str(OUT_JSON.relative_to(ROOT)), "markdown": str(OUT_MD.relative_to(ROOT)), "body_sha256": payload["body_sha256"]}, ensure_ascii=False, indent=2))
    if not all(checks.values()):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
