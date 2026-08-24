#!/usr/bin/env python3
"""Zero-outcome feasibility census for a post-R19 replacement experiment.

R33 is not an R19 resume. This census uses only frozen cohort/configuration
identity plus scientific-exposure bookkeeping; it never opens R19 outcomes.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from statistics import NormalDist

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
TARGET_EFFECT = 0.15
ALPHA = 0.05


def normal_two_sided_power(n: int, sd: float, effect: float = TARGET_EFFECT, alpha: float = ALPHA) -> float:
    nd = NormalDist()
    z = nd.inv_cdf(1 - alpha / 2)
    mu = effect * math.sqrt(n) / sd
    return (1 - nd.cdf(z - mu)) + nd.cdf(-z - mu)


def build(r9: dict, r19_contract: dict, r19_candidate: dict, r31: dict) -> dict:
    if r9.get("status") != "NATIVE_STATUS_FIELD_AND_36_UNIT_COHORT_VERIFIED_EXECUTION_BLOCKED":
        raise RuntimeError("R9 preflight drift")
    if r19_contract.get("status") != "R19_PREOUTCOME_CONTRACT_FROZEN_NEW_AUTHORITY_AND_SYNTHETIC_SMOKES_REQUIRED":
        raise RuntimeError("R19 contract drift")
    if r19_candidate.get("status") != "R19_35_TEMPLATE_HYBRID_FRESH_COHORT_AVAILABLE_NEW_AUTHORITY_REQUIRED":
        raise RuntimeError("R19 candidate drift")
    if r31.get("status") != "SEQ029_PREEXPOSURE_SUPPORT_FAILURE_EXACT_RETRY_EXHAUSTED_R19_STOPPED":
        raise RuntimeError("R31 stop drift")
    if r31["adjudication"]["current_R19_confirmatory_execution_stopped"] is not True:
        raise RuntimeError("R19 not stopped")

    all_templates = [str(x["template_id"]) for x in r9["cohort"]]
    if len(all_templates) != 36 or len(set(all_templates)) != 36:
        raise RuntimeError("R9 template universe drift")

    r18_exposed = str(r19_candidate["parent_state"]["prior_exposed_template_id"])
    last_complete_seq = int(r31["durable_prefix"]["last_complete_sequence_index"])
    r19_exposed = {
        str(x["template_id"])
        for x in r19_contract["rollouts"]["episode_schedule"]
        if int(x["sequence_index"]) <= last_complete_seq
    }
    # The stopped sequence 29 never crossed STARTED, so its template is already
    # included only because sequence 28 from the same template did complete.
    exposed = {r18_exposed} | r19_exposed
    remaining = [x for x in all_templates if x not in exposed]
    if len(exposed) != 9 or len(remaining) != 27:
        raise RuntimeError(f"unexpected post-R19 capacity: exposed={len(exposed)} remaining={len(remaining)}")

    remaining_r19_rows = [
        x for x in r19_candidate["cohort"] if str(x["template_id"]) in set(remaining)
    ]
    if len(remaining_r19_rows) != 27:
        raise RuntimeError("remaining R19 row capacity drift")

    sensitivities = [
        {"task_level_sd": sd, "independent_tasks": 27, "approx_two_sided_power": round(normal_two_sided_power(27, sd), 6)}
        for sd in (0.2, 0.3, 0.4)
    ]
    # Reference from the same normal approximation: first n reaching >=.80 at SD=.30.
    n80_sd03 = next(n for n in range(1, 200) if normal_two_sided_power(n, 0.3) >= 0.8)

    return {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-L2B-R33-REPLACEMENT-FEASIBILITY",
        "recorded_date": "2026-08-24",
        "status": "R33_SAME_ASSET_FULLY_UNEXPOSED_CAPACITY_27_NEW_SUBSTRATE_PREFERRED",
        "role": "ZERO_OUTCOME_POST_R19_STOP_REPLACEMENT_FEASIBILITY",
        "scientific_relationship": "NEW_EXPERIMENT_FEASIBILITY_NOT_R19_RESUME_NOT_R5_RESCUE",
        "parent_stop": {
            "r31_status": r31["status"],
            "r19_scientific_verdict": r31["scientific_verdict"],
            "r19_partial_prefix_episodes": 29,
            "r19_partial_outcomes_read_for_R33_selection": False,
            "r19_partial_outcomes_used_for_R33_selection": False,
        },
        "exposure_only_selection": {
            "eligible_template_universe": 36,
            "R18_exposed_templates": [r18_exposed],
            "R19_scientifically_exposed_templates": sorted(r19_exposed, key=int),
            "all_exposed_templates_excluded": sorted(exposed, key=int),
            "selection_uses_only_template_identity_and_scientific_exposure": True,
            "selection_uses_terminal_scores": False,
            "selection_uses_task_deltas": False,
            "selection_uses_p_values": False,
            "selection_uses_subgroups": False,
        },
        "same_asset_capacity": {
            "fully_unexposed_templates_remaining": 27,
            "remaining_template_ids": sorted(remaining, key=int),
            "fully_unexposed_existing_R17_memory_units_available": 27,
            "can_supply_fresh_35_task_cohort": False,
            "can_supply_medium_variance_80pct_reference_n": False,
            "medium_variance_80pct_reference_n": n80_sd03,
            "shortfall_vs_medium_variance_80pct_reference": n80_sd03 - 27,
            "shortfall_vs_35_task_target": 35 - 27,
            "remaining_units_are_automatically_authorized_as_R33": False,
        },
        "power_sensitivity_only": {
            "target_absolute_effect": TARGET_EFFECT,
            "alpha": ALPHA,
            "approximation": "normal approximation for a paired task-level mean; not confirmatory inference",
            "scenarios": sensitivities,
            "unconditional_80pct_power_claim": False,
            "interpretation": "n=27 retains high sensitivity only under the low-variance scenario; at SD=0.30 its approximate power is below 0.80, so a same-asset replacement would materially weaken the original confirmatory ambition.",
        },
        "recommended_replacement_direction": {
            "preferred": "NEW_TASK_UNIVERSE_OR_NEW_SUBSTRATE_WITH_NATIVE_OR_AUDITABLE_PROVENANCE_SURFACE",
            "reason": "The current frozen WebArena asset cannot supply enough fully unexposed template-independent units for the prior 35-task ambition or the medium-variance 80% planning reference.",
            "minimum_design_requirement": "Freeze a new independently sourced task/template universe prospectively, restore support reliability before benchmark exposure, and bind a new source-memory/provenance surface without reading R19 partial outcomes.",
            "same_asset_27_unit_fallback": "DESIGN_OPTION_ONLY_NOT_AUTHORIZED; would require an explicit lower-power contract and new authority, and must still exclude all exposed templates.",
        },
        "forbidden": [
            "resume current R19 at sequence29 or later",
            "reuse any R18/R19 scientifically exposed template in a fresh confirmatory sample",
            "use R19 terminal scores, deltas, p-values, or subgroups to select R33",
            "pool R19 partial outcomes into R33",
            "reinterpret the remaining 27 unexposed units as an already-authorized continuation",
            "execute PSMG mitigation as a rescue without a separate gate",
        ],
        "authority": {
            "scientific_execution": False,
            "experiment": False,
            "model_calls": False,
            "browser_actions": False,
            "evaluator_calls": False,
            "gpu": False,
            "claim_expansion": False,
            "submission": False,
        },
        "scientific_verdict": "NO_VERDICT_REPLACEMENT_FEASIBILITY_ONLY",
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--r9", type=Path, required=True)
    ap.add_argument("--r19-contract", type=Path, required=True)
    ap.add_argument("--r19-candidate", type=Path, required=True)
    ap.add_argument("--r31", type=Path, required=True)
    ap.add_argument("--output", type=Path, default=Path("generated/d2-failure-memory-provenance-l2b-r33-replacement-feasibility.json"))
    a = ap.parse_args()
    out = build(
        json.loads(a.r9.read_text(encoding="utf-8")),
        json.loads(a.r19_contract.read_text(encoding="utf-8")),
        json.loads(a.r19_candidate.read_text(encoding="utf-8")),
        json.loads(a.r31.read_text(encoding="utf-8")),
    )
    a.output.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": out["status"], "remaining": out["same_asset_capacity"]["fully_unexposed_templates_remaining"], "preferred": out["recommended_replacement_direction"]["preferred"], "execution_authorized": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
