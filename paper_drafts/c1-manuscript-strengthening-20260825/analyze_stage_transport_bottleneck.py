#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STAGE = HERE / "stage-resolved-evidence-reinterpretation.json"
RESULT_ANALYSIS = ROOT / "research_pipeline" / "result_analysis_ledger_20260825.json"
OUT = HERE / "stage-transport-bottleneck-analysis-20260825.json"

EXPECTED = {
    "stage_sha256": "02e39f14e99eca61bc687890c1bb501e540d87395c6887f39b125538cae570be",
    "result_analysis_sha256": "aa106470adbe11707ad62d13e698cbe252bf7c7989450d94106c2df086f66c7a",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def require(ok: bool, msg: str) -> None:
    if not ok:
        raise RuntimeError(msg)


def main() -> None:
    require(sha(STAGE) == EXPECTED["stage_sha256"], "stage reinterpretation SHA drift")
    require(sha(RESULT_ANALYSIS) == EXPECTED["result_analysis_sha256"], "result-analysis SHA drift")
    stage = load(STAGE)
    result = load(RESULT_ANALYSIS)
    obs = stage.get("observations") or {}
    write = obs.get("write_stage") or {}
    forced = obs.get("forced_leverage") or {}
    shopping = obs.get("native_shopping") or {}
    reddit = obs.get("native_reddit") or {}

    require((write.get("shopping_complete_pairs"), write.get("shopping_diverged_pairs")) == (20, 20), "Shopping write breadth drift")
    require(abs(float(write.get("pooled_token_jaccard")) - 0.673) < 1e-12, "Shopping Jaccard drift")
    require(abs(float((write.get("same_mode_control") or {}).get("paired_excess")) - 0.105) < 1e-12, "same-mode control drift")
    require(abs(float((write.get("same_mode_control") or {}).get("exact_p")) - 0.0078) < 1e-12, "same-mode p drift")
    require(abs(float(forced.get("terminal_abs_delta")) - 0.15625) < 1e-12, "forced leverage drift")
    require(abs(float(forced.get("permutation_p")) - 0.00074) < 1e-12, "forced leverage p drift")
    require((shopping.get("retrieval_hits"), shopping.get("retrieval_opportunities")) == (125, 172), "native retrieval drift")
    require(abs(float(shopping.get("first_action_tv")) - 0.06944) < 1e-12, "first-action TV drift")
    require(abs(float(shopping.get("first_action_p")) - 0.5801) < 1e-12, "first-action p drift")
    require(shopping.get("modal_action_changes") == "0/36", "modal action drift")
    require(abs(float(shopping.get("terminal_abs_delta")) - 0.02083) < 1e-12, "Shopping terminal drift")
    require(abs(float(shopping.get("terminal_p")) - 0.4289) < 1e-12, "Shopping terminal p drift")
    require(shopping.get("terminal_zero_cells") == "34/36", "Shopping sparsity drift")
    require(reddit.get("write_diverged_pairs") == "4/4", "Reddit write drift")
    require(abs(float(reddit.get("terminal_abs_delta")) - 0.125) < 1e-12, "Reddit terminal drift")
    require(abs(float(reddit.get("terminal_p")) - 0.2253) < 1e-12, "Reddit terminal p drift")
    require(reddit.get("terminal_zero_cells") == "6/8" and reddit.get("nonzero_signs") == "opposite", "Reddit heterogeneity drift")

    analyses = result.get("analyses") or []
    c1 = next((row for row in analyses if isinstance(row, dict) and row.get("paper_id") == "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE"), None)
    require(isinstance(c1, dict), "C1 result analysis missing")
    require((c1.get("analysis") or {}).get("failure_layer") == "method_realization", "C1 method-extension failure-layer drift")

    retrieval_rate = float(shopping["retrieval_hits"]) / float(shopping["retrieval_opportunities"])

    payload = {
        "schema_version": "1.0",
        "artifact_type": "c1-stage-transport-bottleneck-analysis",
        "paper_id": "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE",
        "analysis_id": "C1-STAGE-TRANSPORT-BOTTLENECK-R2-20260825",
        "status": "SUPPORTED_OPERATIONAL_POST_EXPOSURE_ATTENUATION_LOCALIZATION",
        "question": "Given a reward-conditioned persistent-state intervention, where does the observable branch contrast stop behaving like native behavioral transport?",
        "source_bindings": [
            {"path": str(STAGE.relative_to(ROOT)), "sha256": EXPECTED["stage_sha256"]},
            {"path": str(RESULT_ANALYSIS.relative_to(ROOT)), "sha256": EXPECTED["result_analysis_sha256"]},
        ],
        "scientific_object": {
            "native_chain": ["persistent_write", "retrieval_exposure", "first_action_uptake", "terminal_outcome"],
            "side_control": "forced_fixed_evidence_leverage",
            "why_side_control_not_chain_stage": "Forced fixed-evidence injection bypasses native retrieval/exposure. It probes whether memory content can affect downstream behavior when supplied, not whether the native system transports it.",
            "forbidden_scalarization": "W, exposure rate, first-action TV, and terminal |Delta| live on different scales and must not be divided into a transport-efficiency or mediation coefficient.",
        },
        "observed_pattern": {
            "write": {"shopping_diverged": "20/20", "pooled_token_jaccard": 0.673, "same_mode_excess": 0.105, "same_mode_exact_p": 0.0078},
            "forced_capacity_control": {"terminal_abs_delta": 0.15625, "permutation_p": 0.00074},
            "native_exposure": {"retrieval_hits": 125, "retrieval_opportunities": 172, "rate": retrieval_rate},
            "native_first_action": {"tv": 0.06944, "p": 0.5801, "modal_changes": "0/36"},
            "native_terminal_shopping": {"abs_delta": 0.02083, "p": 0.4289, "zero_cells": "34/36"},
            "native_terminal_reddit": {"write_diverged": "4/4", "abs_delta": 0.125, "p": 0.2253, "zero_cells": "6/8", "nonzero_signs": "opposite"},
        },
        "alternative_explanation_audit": [
            {
                "id": "A1_NO_PERSISTENT_STATE_INTERVENTION",
                "status": "INCONSISTENT_WITH_FROZEN_EVIDENCE",
                "evidence": "20/20 Shopping and 4/4 Reddit reward-conditioned writes diverge; the same-mode control leaves a 0.105 paired excess (p=0.0078).",
                "meaning": "The native null cannot be explained by the writer simply failing to create branch-specific persistent state.",
            },
            {
                "id": "A2_DOWNSTREAM_POLICY_GLOBALLY_INSENSITIVE_TO_MEMORY_CONTENT",
                "status": "WEAKENED_NOT_ELIMINATED",
                "evidence": "Forced fixed-evidence exposure yields terminal |Delta|=0.15625 (p=0.00074).",
                "meaning": "The frozen downstream system can respond to supplied branch-specific memory content under the forced surface; native attenuation is therefore not well summarized as global memory insensitivity.",
            },
            {
                "id": "A3_NATIVE_FAILURE_IS_ONLY_RETRIEVAL_ABSENCE",
                "status": "WEAKENED_NOT_ELIMINATED",
                "evidence": "Native Shopping records 125 retrieval hits in 172 held-out opportunities while first-action TV is 0.06944 (p=0.5801) with 0/36 modal changes.",
                "meaning": "Availability alone does not account for the weak action-level contrast; substantial exposure coexists with weak measured uptake.",
            },
            {
                "id": "A4_RETRIEVAL_HIT_IS_A_VALID_SURROGATE_FOR_POLICY_UPTAKE",
                "status": "REJECTED_AS_EVALUATION_EQUIVALENCE",
                "evidence": "Substantial native exposure coexists with weak first-action distributional change and no modal action changes in 36 matched Shopping targets.",
                "meaning": "Retrieval success should be reported as an exposure variable, not counted as evidence that the policy used the retrieved branch-specific content.",
            },
            {
                "id": "A5_BRANCH_SPECIFIC_MEMORY_HAS_UNIVERSAL_DIRECTIONAL_TERMINAL_TRANSPORT",
                "status": "NOT_SUPPORTED",
                "evidence": "Shopping has 34/36 zero terminal cells; Reddit has 6/8 zero cells and its two nonzero cells have opposite signs.",
                "meaning": "A single signed harm/benefit coefficient or universal attenuation constant is not supported by the frozen native data.",
            },
            {
                "id": "A6_OBSERVED_ATTENUATION_IS_A_CERTIFIED_CAUSAL_MEDIATOR_EFFECT",
                "status": "UNRESOLVED_AND_FORBIDDEN_AS_CLAIM",
                "evidence": "The frozen pool lacks per-atom decoding-seed binding and same-condition same-trajectory noise-floor replication, and forced/native surfaces are not the same intervention.",
                "meaning": "The paper may localize an operational bottleneck pattern but may not estimate a causal mediation coefficient or atom-level causal purity.",
            },
        ],
        "localization": {
            "verdict": "POST_EXPOSURE_PRE_ACTION_ATTENUATION_IS_THE_STRONGEST_SUPPORTED_OPERATIONAL_LOCALIZATION",
            "logic": [
                "A reward-mode intervention robustly creates persistent-state divergence.",
                "Forced exposure shows nonzero downstream leverage when memory evidence is mechanically supplied.",
                "Native retrieval exposure remains substantial rather than collapsing to zero.",
                "The first measured action boundary is weak and does not pass its frozen gate.",
                "Native terminal transport is sparse, small in Shopping, and sign-heterogeneous across Reddit cells.",
            ],
            "claim_strength": "SUPPORTED_OPERATIONAL_LOCALIZATION_NOT_CAUSAL_MEDIATION",
            "paper_consequence": "Make the exposure-to-uptake boundary the main mechanism/measurement result; use forced leverage only as a side control that weakens the global-insensitivity alternative.",
        },
        "claim_hierarchy": [
            {
                "level": 1,
                "claim": "Reward-conditioned writing creates a reproducible durable state contrast under the frozen same-trajectory controls.",
                "role": "intervention establishment",
            },
            {
                "level": 2,
                "claim": "The downstream system has measurable leverage under mechanically supplied branch-specific memory content.",
                "role": "capacity control",
            },
            {
                "level": 3,
                "claim": "Under native reuse, substantial exposure does not translate into comparably stable first-action or terminal branch differences; the strongest supported attenuation boundary is after exposure and before stable action uptake.",
                "role": "main stage-resolved localization",
            },
            {
                "level": 4,
                "claim": "The native terminal effect is sparse and sign-heterogeneous across domains/tasks, so no universal directional transport coefficient is supported.",
                "role": "boundary/generalization",
            },
        ],
        "does_not_imply": [
            "retrieval exposure is policy uptake",
            "forced fixed-evidence leverage is native end-to-end transport",
            "the exposure-to-uptake boundary is a causal mediation coefficient",
            "every branch-specific memory sentence is causally pure",
            "CBRG has a positive or negative behavioral method effect",
            "the observed attenuation is universal across writers, models, tasks, or domains",
        ],
        "execution": {"new_scientific_provider_calls": 0, "new_gpu_runs": 0, "new_scientific_experiments": 0},
        "authority": {"scientific": False, "experiment": False, "provider": False, "gpu": False, "claim_expansion": False, "submission": False},
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "localization": payload["localization"]["verdict"],
        "retrieval_rate": retrieval_rate,
        "alternative_explanations": len(payload["alternative_explanation_audit"]),
        "provider_calls": 0,
        "gpu_runs": 0,
    }, indent=2))


if __name__ == "__main__":
    main()
