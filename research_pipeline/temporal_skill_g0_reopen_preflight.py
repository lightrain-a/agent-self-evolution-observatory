from __future__ import annotations

import argparse
import collections
import hashlib
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PAPER_ID = "D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
DATA_ROOT = Path("/data/wyt/agent-self-evolution-observatory")
LEDGER = DATA_ROOT / "paper-acceptance" / f"{PAPER_ID}.json"
REPLAY_ROOT = DATA_ROOT / "paper-acceptance" / "source-native-replay" / PAPER_ID
R3 = REPLAY_ROOT / "20260822-r3"
R4 = REPLAY_ROOT / "20260822-r4-postreview-eia"

REQUESTED_MODEL = "ark-code-latest"
REQUIRED_PLAN_TARGET_MODEL = "deepseek-v4-pro"
REQUIRED_RESOLVED_MODEL = "deepseek-v4-pro-260425"
REQUIRED_PLAN_BASE_URL = "https://ark.cn-beijing.volces.com/api/plan/v3"
RUNNER_PATH = PROJECT_ROOT / "research_pipeline" / "temporal_skill_g0_execute.py"
ANALYZER_PATH = PROJECT_ROOT / "research_pipeline" / "temporal_skill_g0_analyze.py"
REPEATS = 2
ARMS = ("N_FRESH", "G0_NOOP", "T_FROZEN")
ORDER_SEED = "TEMP-O4-G0-20260824-v1"
BOOTSTRAP_SEED = 20260824
BOOTSTRAP_DRAWS = 20000
EQUIVALENCE_MARGIN = 0.10

# The candidate intentionally exposes the callable-wrapper fact while adding no
# task/evidence information. It must not read package or context.
G0_SOURCE = "def skill(package, context):\n    return {}\n"


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha_bytes(raw)


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def percentile(values: list[float], p: float) -> float:
    xs = sorted(values)
    idx = (len(xs) - 1) * p
    lo = int(idx)
    hi = min(lo + 1, len(xs) - 1)
    frac = idx - lo
    return xs[lo] * (1.0 - frac) + xs[hi] * frac


def collect_frozen_deepseek_n0() -> tuple[dict[str, dict[int, int]], dict[str, dict[str, str]], list[dict[str, Any]]]:
    by_endpoint: dict[str, dict[int, int]] = collections.defaultdict(dict)
    meta: dict[str, dict[str, str]] = {}
    usage_rows: list[dict[str, Any]] = []

    r3_files = ["ark_f0_c3_r.json", "ark_f0_c4_r.json"] + [f"repeat_{i}_deepseek_all.json" for i in range(1, 5)]
    for name in r3_files:
        for row in read_json(R3 / name).get("rows", []):
            if row.get("status") != "completed":
                continue
            if row.get("condition_id") == "N0":
                eid = str(row["endpoint_id"])
                by_endpoint[eid][int(row.get("repeat_id", 0))] = int(bool(row.get("success")))
                meta[eid] = {"failure_family": str(row["failure_family"]), "phase": str(row["phase"]), "source": "R3"}
            if row.get("condition_id") == "N0" or str(row.get("condition_id") or "").startswith("T"):
                usage_rows.append(row)

    for row in read_json(R4 / "r4_deepseek_results.json").get("rows", []):
        if not row.get("runtime_valid"):
            continue
        if row.get("condition_id") == "N0":
            eid = str(row["endpoint_id"])
            by_endpoint[eid][int(row.get("repeat_id", 0))] = int(bool(row.get("family_success")))
            meta[eid] = {"failure_family": str(row["failure_family"]), "phase": str(row["phase"]), "source": "R4-EIA"}
        if row.get("condition_id") == "N0" or str(row.get("condition_id") or "").startswith("T"):
            usage_rows.append(row)

    return dict(by_endpoint), meta, usage_rows


def load_endpoints() -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    r3_raw = read_json(R3 / "endpoints.json")
    r3_rows = r3_raw.get("endpoints", r3_raw) if isinstance(r3_raw, dict) else r3_raw
    for row in r3_rows:
        out[str(row["endpoint_id"])] = row
    r4_raw = read_json(R4 / "endpoints.json")
    r4_rows = r4_raw.get("endpoints", r4_raw) if isinstance(r4_raw, dict) else r4_raw
    for row in r4_rows:
        out[str(row["endpoint_id"])] = row
    return out


def targeted_condition(family: str) -> str:
    return {
        "temporal_cutoff": "T1",
        "release_alignment": "T2",
        "exogenous_grounding": "T3",
    }[family]


def build_plan(endpoints: dict[str, dict[str, Any]], meta: dict[str, dict[str, str]]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    # Hash-sort endpoint-repeat units once, then apply a 3x3 Latin rotation.
    # Over 70 units, each arm occupies each condition position 23 or 24 times;
    # no arm is systematically early/late in the provider queue.
    units = [(eid, repeat_id) for repeat_id in range(REPEATS) for eid in sorted(endpoints)]
    units.sort(key=lambda x: hashlib.sha256(f"{ORDER_SEED}|{x[0]}|{x[1]}".encode("utf-8")).hexdigest())
    latin_orders = (
        ARMS,
        (ARMS[1], ARMS[2], ARMS[0]),
        (ARMS[2], ARMS[0], ARMS[1]),
    )
    for unit_index, (eid, repeat_id) in enumerate(units):
        family = str(endpoints[eid]["failure_family"])
        order = latin_orders[unit_index % len(latin_orders)]
        for position, arm in enumerate(order):
            rows.append(
                {
                    "endpoint_id": eid,
                    "failure_family": family,
                    "phase": meta[eid]["phase"],
                    "repeat_id": repeat_id,
                    "arm": arm,
                    "condition_id": "N0" if arm == "N_FRESH" else ("G0N" if arm == "G0_NOOP" else targeted_condition(family)),
                    "condition_position": position,
                    "requested_model": REQUESTED_MODEL,
                    "required_resolved_model": REQUIRED_RESOLVED_MODEL,
                }
            )
    counts = collections.Counter(row["arm"] for row in rows)
    positions = {arm: collections.Counter(row["condition_position"] for row in rows if row["arm"] == arm) for arm in ARMS}
    return {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "plan_id": "TEMP-O4-G0-NEUTRALITY-FRESH-3ARM-V1",
        "created_at": now(),
        "rows": rows,
        "summary": {
            "independent_endpoints": len(endpoints),
            "repeats": REPEATS,
            "arms": list(ARMS),
            "planned_model_calls": len(rows),
            "calls_by_arm": dict(counts),
            "condition_position_counts": {arm: {str(k): v for k, v in sorted(c.items())} for arm, c in positions.items()},
        },
        "model_identity": {
            "requested_model": REQUESTED_MODEL,
            "required_plan_base_url": REQUIRED_PLAN_BASE_URL,
            "required_plan_target_model": REQUIRED_PLAN_TARGET_MODEL,
            "required_resolved_model": REQUIRED_RESOLVED_MODEL,
            "plan_only_billing_route_required": True,
            "direct_extra_billed_model_route_forbidden": True,
            "ark_code_latest_counts_as_same_model_evidence_only_if_provider_resolves_exact_required_model": True,
        },
        "g0": {
            "source": G0_SOURCE,
            "source_sha256": sha_bytes(G0_SOURCE.encode("utf-8")),
            "output": {},
            "reads_package": False,
            "reads_context": False,
            "same_callable_signature": True,
            "same_wrapper_exposure": True,
            "same_helper_execution_count": True,
        },
        "authority": {
            "scientific": False,
            "experiment": False,
            "gpu": False,
            "execution_authorized": False,
        },
    }


def simulate_null_width(by_endpoint: dict[str, dict[int, int]]) -> dict[str, Any]:
    rng = random.Random(BOOTSTRAP_SEED)
    p_hat = {eid: sum(v.values()) / len(v) for eid, v in by_endpoint.items()}
    eids = sorted(p_hat)
    samples: list[float] = []
    for _ in range(50000):
        ds = []
        for eid in eids:
            p = p_hat[eid]
            a = sum(rng.random() < p for _ in range(REPEATS)) / REPEATS
            b = sum(rng.random() < p for _ in range(REPEATS)) / REPEATS
            ds.append(a - b)
        samples.append(sum(ds) / len(ds))
    return {
        "simulation_only_zero_scientific_authority": True,
        "source": "frozen five-repeat N0 endpoint frequencies only",
        "seed": BOOTSTRAP_SEED,
        "draws": 50000,
        "fresh_repeats_per_arm": REPEATS,
        "null_global_delta_percentile_90": [percentile(samples, 0.05), percentile(samples, 0.95)],
        "null_global_delta_percentile_95": [percentile(samples, 0.025), percentile(samples, 0.975)],
        "p_abs_delta_le_0_10": sum(abs(x) <= 0.10 for x in samples) / len(samples),
    }


def safe_ark_summary() -> dict[str, Any]:
    try:
        from research_pipeline.ark_provider import ArkSettings

        return ArkSettings.from_env(required=False).safe_summary()
    except Exception as exc:
        return {"configured": False, "error_type": type(exc).__name__, "api_key_in_output": False}


def build_receipt() -> tuple[dict[str, Any], dict[str, Any]]:
    ledger = read_json(LEDGER)
    endpoints = load_endpoints()
    by_endpoint, meta, usage_rows = collect_frozen_deepseek_n0()

    if set(endpoints) != set(by_endpoint):
        missing = sorted(set(endpoints) - set(by_endpoint))
        extra = sorted(set(by_endpoint) - set(endpoints))
        raise RuntimeError(f"endpoint/N0 mismatch missing={missing} extra={extra}")
    if any(len(v) != 5 for v in by_endpoint.values()):
        raise RuntimeError("every endpoint must have exactly five frozen N0 repeats for this preflight")

    families = collections.Counter(meta[eid]["failure_family"] for eid in endpoints)
    varying = [eid for eid, values in by_endpoint.items() if len(set(values.values())) > 1]
    repeat_mae: dict[str, Any] = {}
    for r in (1, 2, 3, 4):
        diffs = []
        for eid, values in by_endpoint.items():
            vec = [values[k] for k in sorted(values)]
            full = sum(vec) / len(vec)
            partial = sum(vec[:r]) / r
            diffs.append(abs(partial - full))
        repeat_mae[str(r)] = {"mae_to_five_repeat_mean": sum(diffs) / len(diffs), "max": max(diffs)}

    n_usage = [row.get("usage") or {} for row in usage_rows if row.get("condition_id") == "N0"]
    t_usage = [row.get("usage") or {} for row in usage_rows if str(row.get("condition_id") or "").startswith("T")]
    mean_n = sum(float(x.get("total_tokens") or 0) for x in n_usage) / len(n_usage)
    mean_t = sum(float(x.get("total_tokens") or 0) for x in t_usage) / len(t_usage)
    rough_total_tokens = len(endpoints) * REPEATS * (mean_n + mean_t + mean_n + 30.0)

    plan = build_plan(endpoints, meta)
    plan_body_sha = canonical_sha({k: v for k, v in plan.items() if k != "created_at"})
    plan["plan_body_sha256"] = plan_body_sha

    ledger_authority = ledger.get("authority") or {}
    authority_open = bool(ledger_authority.get("scientific") and ledger_authority.get("experiment"))
    ark = safe_ark_summary()

    receipt = {
        "schema_version": "1.0",
        "receipt_type": "temporal-skill-g0-scientific-reopen-preflight",
        "paper_id": PAPER_ID,
        "generated_at": now(),
        "status": "HOLD_EXPLICIT_SCIENTIFIC_REOPEN_AND_EXPERIMENT_AUTHORITY",
        "purpose": "Freeze Stage A: a behavior-neutral second generic control for the registered DeepSeek primary track before any new provider/model outcome is generated.",
        "canonical_ledger_snapshot": {
            "path": str(LEDGER),
            "sha256": sha_file(LEDGER),
            "current_state": ledger.get("current_state"),
            "scientific_status": ledger.get("scientific_status"),
            "updated_at": ledger.get("updated_at"),
            "authority": ledger_authority,
            "scientific_reopen_required_in_latest_r10": True,
            "authority_open": authority_open,
        },
        "frozen_support_inventory": {
            "r3_endpoints_path": str(R3 / "endpoints.json"),
            "r3_endpoints_sha256": sha_file(R3 / "endpoints.json"),
            "r4_endpoints_path": str(R4 / "endpoints.json"),
            "r4_endpoints_sha256": sha_file(R4 / "endpoints.json"),
            "independent_endpoints": len(endpoints),
            "family_endpoint_counts": dict(sorted(families.items())),
            "frozen_n0_rows": sum(len(v) for v in by_endpoint.values()),
            "n0_repeats_per_endpoint": 5,
            "n0_repeat_varying_endpoints": len(varying),
            "n0_repeat_stable_endpoints": len(endpoints) - len(varying),
            "varying_endpoint_ids": sorted(varying),
            "repeat_subsample_diagnostic": repeat_mae,
            "support_sufficient_for_fixed_two_repeat_fresh_factorial": True,
        },
        "design_delta_from_r12": {
            "r12_candidate": "identity projection",
            "preflight_candidate": "empty-output no-op helper",
            "changed_before_new_outcomes": True,
            "reason": "A family-uniform identity projection is ill-defined for release alignment and may duplicate evidence/salience. Empty output preserves wrapper/call exposure while adding no evidence transformation or task information.",
            "r12_historical_receipt_mutated": False,
        },
        "g0_static_contract": plan["g0"],
        "frozen_execution_code": {
            "runner_path": str(RUNNER_PATH.relative_to(PROJECT_ROOT)),
            "runner_sha256": sha_file(RUNNER_PATH),
            "analyzer_path": str(ANALYZER_PATH.relative_to(PROJECT_ROOT)),
            "analyzer_sha256": sha_file(ANALYZER_PATH),
        },
        "fresh_execution_contract": {
            "plan_id": plan["plan_id"],
            "plan_body_sha256": plan_body_sha,
            "independent_unit": "endpoint",
            "endpoints": len(endpoints),
            "arms": list(ARMS),
            "repeats_per_arm": REPEATS,
            "planned_model_calls": plan["summary"]["planned_model_calls"],
            "fresh_n_required": True,
            "fresh_t_required": True,
            "historical_N_or_T_not_substituted_for_fresh_pairing": True,
            "condition_order_seed": ORDER_SEED,
            "condition_position_counts": plan["summary"]["condition_position_counts"],
            "requested_model": REQUESTED_MODEL,
            "required_resolved_model": REQUIRED_RESOLVED_MODEL,
            "stop_on_resolved_model_drift": True,
            "provider_failure_policy": "No outcome-driven replacement. A provider object with no assistant text may be GET-recovered only; do not re-POST the same unit as a hidden replacement.",
        },
        "neutrality_contract": {
            "estimand": "mean across 35 endpoints of [repeat-mean family_success(G0_NOOP) - repeat-mean family_success(N_FRESH)]",
            "equivalence_margin_absolute_risk_difference": [-EQUIVALENCE_MARGIN, EQUIVALENCE_MARGIN],
            "confidence_interval": "90% endpoint-stratified bootstrap by failure_family",
            "bootstrap_draws": BOOTSTRAP_DRAWS,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "go": "90% CI strictly inside [-0.10,+0.10] and no family non-neutrality guardrail fires",
            "nonneutral_stop": "global |point estimate| >= 0.10 with 90% CI excluding 0, or a family has |mean delta| >= 0.20 with a one-sided exact sign p <= 0.05 in that direction",
            "otherwise": "HOLD_INCONCLUSIVE_DO_NOT_CALL_G0_NEUTRAL",
            "family_guardrail": "temporal_cutoff, release_alignment, and exogenous_grounding evaluated separately; small cells remain guardrails, not population-effect claims",
        },
        "operation_specificity_contract": {
            "stage": "A_DEEPSEEK_PRIMARY_ONLY",
            "only_evaluated_if_g0_neutrality_go": True,
            "fresh_contrasts": ["T_FROZEN - G0_NOOP", "T_FROZEN - N_FRESH"],
            "same_preexisting_family_phase_cells": True,
            "no_omnibus_universal_skill_claim": True,
            "claim_rule": "Any currently claimed DeepSeek-primary positive cell that becomes non-positive against either fresh G0 or fresh N is downgraded; null/ceiling cells remain visible.",
            "paper_level_TEMP_O4_full_closure_not_automatic": True,
            "residual_support_layer": "Kimi held-out alignment/grounding remains without a behavior-neutral G0 unless separately authorized as Stage B.",
        },
        "zero_call_design_evidence": simulate_null_width(by_endpoint),
        "cost_preflight": {
            "historical_N_total_tokens_mean": mean_n,
            "historical_T_total_tokens_mean": mean_t,
            "rough_planned_total_tokens": rough_total_tokens,
            "rough_planned_total_tokens_millions": rough_total_tokens / 1_000_000.0,
            "pricing_not_inferred": True,
            "provider_billing_authority": False,
        },
        "runtime_readiness": {
            "ark": ark,
            "credential_ready_in_this_isolated_worktree": bool(ark.get("configured")),
            "model_identity_route_requires_ark_plan_target_deepseek_v4_pro": True,
            "ark_plan_base_url_required": REQUIRED_PLAN_BASE_URL,
            "direct_deepseek_v4_pro_route_forbidden_by_cost_policy": True,
            "ark_code_latest_must_resolve_exact_required_model": True,
        },
        "authority": {
            "scientific": False,
            "experiment": False,
            "gpu": False,
            "provider_spend": False,
            "execution_authorized": False,
            "required_before_execution": [
                "explicit external-human scientific reopen scoped to TEMP-O4/G0",
                "experiment authority bound to this plan_body_sha256",
                "provider-spend authorization / credential-bearing execution environment",
                "Ark Plan target explicitly set to deepseek-v4-pro and allowed to propagate before execution",
            ],
        },
        "deferred_stage_b": {
            "model": "kimi-k3",
            "source_native_endpoints": 23,
            "would_require_fresh_authorization": True,
            "not_part_of_stage_a": True,
            "estimated_calls_if_same_3arm_2repeat_design": 138,
            "rough_historical_token_estimate_millions": 0.308,
        },
        "policy": {
            "new_model_calls": 0,
            "new_provider_calls": 0,
            "new_gpu_execution": 0,
            "preflight_has_zero_scientific_result_authority": True,
            "cannot_resolve_primary_track_TEMP_O4_without_fresh_outcomes": True,
            "paper_level_TEMP_O4_full_closure_requires_residual_support_layer_adjudication": True,
            "TEMP_O5_retrieval_baseline_deferred": True,
        },
    }
    receipt["receipt_body_sha256"] = canonical_sha({k: v for k, v in receipt.items() if k not in {"generated_at", "receipt_body_sha256"}})
    return receipt, plan


def build_authorization_request(receipt: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    request = {
        "schema_version": "1.0",
        "request_type": "explicit-external-human-scientific-reopen-and-experiment-authorization",
        "paper_id": PAPER_ID,
        "request_id": "TEMP-O4-G0-STAGE-A-DEEPSEEK-EXECUTION-AUTH-REQUEST-20260824",
        "status": "AWAIT_EXPLICIT_HUMAN_AUTHORIZATION",
        "requested_scope": ["TEMP-O4_STAGE_A_DEEPSEEK_PRIMARY", "G0_NOOP_BEHAVIOR_NEUTRALITY", "FRESH_N_T_REPLICATION_FOR_SAME_UNITS"],
        "explicitly_not_requested": ["TEMP-O4_STAGE_B_KIMI", "TEMP-O5_RETRIEVAL_BASELINE", "NEW_CLAIM", "NEW_MODEL", "GPU_EXECUTION"],
        "bound_plan_body_sha256": plan["plan_body_sha256"],
        "bound_preflight_receipt_body_sha256": receipt["receipt_body_sha256"],
        "bound_runner_sha256": receipt["frozen_execution_code"]["runner_sha256"],
        "bound_analyzer_sha256": receipt["frozen_execution_code"]["analyzer_sha256"],
        "budget": {
            "independent_endpoints": plan["summary"]["independent_endpoints"],
            "arms": plan["summary"]["arms"],
            "repeats_per_arm": plan["summary"]["repeats"],
            "model_calls_upper_bound": plan["summary"]["planned_model_calls"],
            "rough_total_tokens_upper_planning_estimate": receipt["cost_preflight"]["rough_planned_total_tokens"],
            "reruns_allowed": False,
            "outcome_driven_replacement_allowed": False,
        },
        "model_identity": plan["model_identity"],
        "analysis_contract": {
            "neutrality_margin": receipt["neutrality_contract"]["equivalence_margin_absolute_risk_difference"],
            "neutrality_confidence_interval": receipt["neutrality_contract"]["confidence_interval"],
            "neutrality_go": receipt["neutrality_contract"]["go"],
            "nonneutral_stop": receipt["neutrality_contract"]["nonneutral_stop"],
            "operation_specificity_only_after_neutrality_go": True,
        },
        "authorization_semantics": {
            "generic_continue_instruction_is_not_interpreted_as_new_scientific_execution_authority": True,
            "required_human_directive": "Explicitly authorize reopening TEMP-O4 Stage A on the DeepSeek primary track and executing the bound 210-call fresh N/G0/T plan through Ark Plan.",
            "required_runtime_confirmation": {
                "ark_plan_base_url": REQUIRED_PLAN_BASE_URL,
                "ark_plan_target_model": REQUIRED_PLAN_TARGET_MODEL,
                "ark_plan_target_confirmed_and_propagated": True,
            },
            "any_scope_or_budget_change_requires_new_plan_hash_and_new_authorization": True,
        },
        "execution_authorized": False,
        "scientific_authority": False,
        "experiment_authority": False,
        "provider_spend_authority": False,
    }
    request["request_body_sha256"] = canonical_sha({k: v for k, v in request.items() if k != "request_body_sha256"})
    return request


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, default=Path("generated/temporal-skill-g0-reopen-preflight-20260824.json"))
    parser.add_argument("--plan", type=Path, default=Path("generated/temporal-skill-g0-fresh-factorial-plan-20260824.json"))
    parser.add_argument("--authorization-request", type=Path, default=Path("generated/temporal-skill-g0-authorization-request-20260824.json"))
    args = parser.parse_args()
    receipt, plan = build_receipt()
    request = build_authorization_request(receipt, plan)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.plan.parent.mkdir(parents=True, exist_ok=True)
    args.authorization_request.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.plan.write_text(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.authorization_request.write_text(json.dumps(request, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": receipt["status"],
        "receipt": str(args.receipt),
        "plan": str(args.plan),
        "authorization_request": str(args.authorization_request),
        "receipt_body_sha256": receipt["receipt_body_sha256"],
        "plan_body_sha256": plan["plan_body_sha256"],
        "authorization_request_sha256": request["request_body_sha256"],
        "planned_model_calls": plan["summary"]["planned_model_calls"],
        "execution_authorized": receipt["authority"]["execution_authorized"],
    }, indent=2))


if __name__ == "__main__":
    main()
