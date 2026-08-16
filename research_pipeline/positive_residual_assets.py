from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

SUPPORT_INVENTORY = PROJECT_ROOT / "research_pipeline" / "paper_first_c2_support_inventory_20260812.json"
POST_C2_ADJUDICATION = PROJECT_ROOT / "generated" / "paper-first-post-c2-adjudication.json"
LOCAL_MECHANISM_READJUDICATION = PROJECT_ROOT / "generated" / "positive-residual-memory-local-mechanism-readjudication-20260816.json"
EXPECTED_SUPPORT_INVENTORY_SHA256 = "00fd656673a86ec92445930628fb4a171547148d8fe9b60666701bd4dee11683"
EXPECTED_POST_C2_SHA256 = "1d21e65d260e6be77c86b86e75db19e3d50a56d588caffb926e9a0b9863f2df5"
EXPECTED_LOCAL_MECHANISM_READJUDICATION_SHA256 = "60a5f330049613f7163e2fee5bfa5f82e32283fed1951e32da83e9f11e712552"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _memory_effect_transport_residual() -> dict[str, Any]:
    if _sha(SUPPORT_INVENTORY) != EXPECTED_SUPPORT_INVENTORY_SHA256:
        raise ValueError("B-9/C2 support inventory provenance drift")
    if _sha(POST_C2_ADJUDICATION) != EXPECTED_POST_C2_SHA256:
        raise ValueError("B-9/C2 post-C2 adjudication provenance drift")
    if _sha(LOCAL_MECHANISM_READJUDICATION) != EXPECTED_LOCAL_MECHANISM_READJUDICATION_SHA256:
        raise ValueError("B-9/C2 local-mechanism readjudication provenance drift")
    inventory = json.loads(SUPPORT_INVENTORY.read_text(encoding="utf-8"))
    post = json.loads(POST_C2_ADJUDICATION.read_text(encoding="utf-8"))
    local = json.loads(LOCAL_MECHANISM_READJUDICATION.read_text(encoding="utf-8"))
    summary = inventory.get("summary") or {}
    c2 = (post.get("c2_result") or {}).get("metrics") or {}
    validity = post.get("decision_context_validity") or {}
    if int(summary.get("raw_controlled_nonzero_units") or 0) != 11:
        raise ValueError("B-9 raw controlled-nonzero count drift")
    if int(summary.get("strict_route_reproducible_units") or 0) != 10:
        raise ValueError("B-9 strict route-reproducible count drift")
    if str(post.get("broad_parent_phenomenon_status") or "") != "SURVIVES_AS_ARCHIVED_PARENT_EVIDENCE":
        raise ValueError("B-9 parent phenomenon no longer survives")
    if int(c2.get("valid_units") or 0) != 10 or int(c2.get("nonzero_tau_units") or 0) != 2:
        raise ValueError("C2 controlled-action mechanism result drift")
    if validity.get("pass") is not True or int(validity.get("valid_units") or 0) != 10:
        raise ValueError("C2 decision-context validity drift")
    if str(local.get("decision") or "") != "LOCAL_STATE_ACTION_APPLICABILITY_EXPLANATIONS_NOT_SUPPORTED_KEEP_BROAD_PHENOMENON_RESIDUAL":
        raise ValueError("B-9/C2 local-mechanism readjudication decision drift")
    local_rows = local.get("failed_or_insufficient_explanations") or []
    if len(local_rows) != 4:
        raise ValueError("B-9/C2 local-mechanism readjudication must bind four failed explanations")

    provenance = {
        "support_inventory": {
            "path": str(SUPPORT_INVENTORY.relative_to(PROJECT_ROOT)),
            "sha256": EXPECTED_SUPPORT_INVENTORY_SHA256,
        },
        "post_c2_adjudication": {
            "path": str(POST_C2_ADJUDICATION.relative_to(PROJECT_ROOT)),
            "sha256": EXPECTED_POST_C2_SHA256,
        },
        "local_mechanism_readjudication": {
            "path": str(LOCAL_MECHANISM_READJUDICATION.relative_to(PROJECT_ROOT)),
            "sha256": EXPECTED_LOCAL_MECHANISM_READJUDICATION_SHA256,
        },
        "frozen_raw_traces_sha256": str(((inventory.get("raw_trace_authority") or {}).get("raw_traces") or {}).get("sha256") or ""),
        "frozen_main_table_sha256": str(((inventory.get("raw_trace_authority") or {}).get("main_table") or {}).get("sha256") or ""),
        "c2_decision_sha256": str((post.get("c2_result") or {}).get("decision_sha256") or ""),
        "decision_context_validity_sha256": str(validity.get("sha256") or ""),
    }
    facts = [
        "The frozen 72-unit, three-arm memory-effect table contains 11 raw controlled nonzero effects; 10 units retain exact first-divergence route and effect-sign reproducibility on matched hardware.",
        "The historical B-9 transport representation was stopped at method development because its nonzero-sign AUC was 0.3214 versus 0.6429 for the strongest simple same-information baseline; the parent effect phenomenon was not rejected.",
        "Candidate-local applicability/scope was not a successful rescue: its future MSE was 0.1883, worse than the zero predictor at 0.1389 and source-family candidate-free baseline at 0.1265, with only 20% future-nonzero coverage.",
        "The subsequent C2 earliest-divergent-action mechanism had 10 execution-valid strict units but only 2/10 nonzero controlled action contrasts and no preregistered same-memory cross-context sign reversal; decision-context validity passed 10/10.",
        "A preregistered CPU-only pre-divergence symbolic admissible-option falsifier also stopped: same-information baseline future AUC 0.5935 versus 0.5742 after adding memory-consistent admissible overlap, AUC advantage -0.0194, with all four decision gates false.",
    ]
    failed_mechanisms = [
        "source/target transport representation used by the historical B-9 method realization",
        "candidate-local applicability/scope and structural-cart predictors",
        "earliest-divergent-action controlled mediator used by trajectory-mediated-memory-effect-transport C2",
        "pre-divergence symbolic memory-consistent admissible-option collapse",
    ]
    search_contract = {
        "question": "What prospective mechanism can explain context-dependent persistent-memory endpoint effects after transport representation, static applicability, earliest-action mediation, and symbolic pre-divergence option-overlap explanations all fail?",
        "must_explain": [
            "a real sparse controlled memory-effect phenomenon",
            "failure of the historical transport representation to beat simple same-information baselines",
            "failure of candidate-local applicability/scope and structural-cart predictors",
            "failure of the earliest divergent action to carry the parent endpoint effect",
            "failure of static pre-divergence symbolic admissible-option overlap to improve a same-information predictor",
        ],
        "prospective_prediction_required": True,
        "pre_outcome_information_only": True,
        "must_beat_or_condition_on": [
            "target-family/context baseline",
            "source-family and source-target relation baseline",
            "first-divergence timing/action signature baseline",
            "candidate-local applicability/scope baseline",
            "static pre-divergence symbolic option-overlap baseline",
        ],
        "mandatory_reduction_before_temporal_exposure_experiment": [
            "time-varying treatment effects / distributed-lag causal models",
            "sequential mediation / longitudinal causal inference",
            "ordinary repeated policy conditioning by a persistent prompt or memory",
            "generic cumulative exposure or dose-response"
        ],
        "prohibited_rescues": [
            "endpoint success, terminal length, or any feature determined by the final outcome",
            "full-trajectory distances computed after success/failure is known",
            "renaming first-action mediation as K-step mediation without independent pre-outcome evidence",
            "reviving the historical B-9 transport representation without a new distinguishing prediction",
            "retuning symbolic action-skeleton overlap or selecting another post hoc local state feature on the same endpoint labels",
            "K-step mediation without an independently specified temporal exposure intervention",
            "calling persistence or repeated exposure itself novel without defeating longitudinal causal reductions",
            "treating this asset as novelty, Problem-Gate, Method, P0, GPU, or full-experiment authority",
        ],
        "opposite_search_seed": "Test whether the persistent-memory treatment requires a temporally distributed exposure window across multiple downstream decisions rather than being carried by one local state or one divergent action, while first defeating generic longitudinal-treatment reductions.",
        "cheapest_next_step": "Search/formulate the temporal-exposure residual against longitudinal causal baselines before authorizing any scheduled-ablation rollout.",
    }
    source_manifest = {
        "provenance": provenance,
        "empirical_facts": facts,
        "failed_mechanisms": failed_mechanisms,
        "search_contract": search_contract,
    }
    return {
        "asset_ref": "positive-residual-asset:memory-effect-transport-b9-c2-20260816",
        "title": "Persistent memory effects survive two failed mechanism realizations",
        "source_kind": "provenance-audited-internal-positive-residual",
        "primary_url": "https://github.com/lightrain-a/agent-self-evolution-observatory/blob/main/research_pipeline/paper_first_c2_support_inventory_20260812.json",
        "source_sha256": _canonical_sha(source_manifest),
        "provenance": provenance,
        "empirical_facts": facts,
        "failed_mechanisms": failed_mechanisms,
        "search_contract": search_contract,
        "phenomenon_status": "SURVIVES_AS_ARCHIVED_PARENT_EVIDENCE",
        "mechanism_status": "FOUR_LOCAL_OR_REPRESENTATIONAL_EXPLANATIONS_STOPPED",
        "scientific_authority": False,
        "authority": {
            "novelty": False,
            "problem_gate": False,
            "method": False,
            "experiment": False,
            "p0": False,
            "gpu": False,
            "full_experiment": False,
        },
    }


def build_positive_residual_asset_registry() -> dict[str, Any]:
    assets = [_memory_effect_transport_residual()]
    return {
        "schema_version": "1.0",
        "registry_id": "positive-residual-search-assets-v2",
        "assets": assets,
        "asset_count": len(assets),
        "scientific_authority": False,
        "policy": {
            "phenomenon_support_does_not_authorize_a_new_problem": True,
            "failed_mechanisms_are_constraints_not_reasons_to_relax_gates": True,
            "positive_residual_assets_are_search_priors_only": True,
            "prospective_pre_outcome_prediction_required": True,
            "outcome_leakage_forbidden": True,
        },
    }
