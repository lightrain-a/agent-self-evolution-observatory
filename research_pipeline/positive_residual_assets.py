from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

SUPPORT_INVENTORY = PROJECT_ROOT / "research_pipeline" / "paper_first_c2_support_inventory_20260812.json"
POST_C2_ADJUDICATION = PROJECT_ROOT / "generated" / "paper-first-post-c2-adjudication.json"
LOCAL_MECHANISM_READJUDICATION = PROJECT_ROOT / "generated" / "positive-residual-memory-local-mechanism-readjudication-20260816.json"
TEMPORAL_EXPOSURE_READJUDICATION = PROJECT_ROOT / "generated" / "positive-residual-memory-temporal-exposure-principle-readjudication-20260816.json"
TREATMENT_SEMANTICS_READJUDICATION = PROJECT_ROOT / "generated" / "positive-residual-memory-treatment-semantics-principle-readjudication-20260816.json"
EXPECTED_SUPPORT_INVENTORY_SHA256 = "00fd656673a86ec92445930628fb4a171547148d8fe9b60666701bd4dee11683"
EXPECTED_POST_C2_SHA256 = "1d21e65d260e6be77c86b86e75db19e3d50a56d588caffb926e9a0b9863f2df5"
EXPECTED_LOCAL_MECHANISM_READJUDICATION_SHA256 = "60a5f330049613f7163e2fee5bfa5f82e32283fed1951e32da83e9f11e712552"
EXPECTED_TEMPORAL_EXPOSURE_READJUDICATION_SHA256 = "2656e6faf2132ebdac5842f8249eef90d5ae18aa3fef0a7c0956084c2dbaeff1"
EXPECTED_TREATMENT_SEMANTICS_READJUDICATION_SHA256 = "ed09316950002ca43b88c427da70dc22e30f6f17076ef7c3010c604ef6f1269e"


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
    if _sha(TEMPORAL_EXPOSURE_READJUDICATION) != EXPECTED_TEMPORAL_EXPOSURE_READJUDICATION_SHA256:
        raise ValueError("B-9/C2 temporal-exposure readjudication provenance drift")
    if _sha(TREATMENT_SEMANTICS_READJUDICATION) != EXPECTED_TREATMENT_SEMANTICS_READJUDICATION_SHA256:
        raise ValueError("B-9/C2 treatment-semantics readjudication provenance drift")
    inventory = json.loads(SUPPORT_INVENTORY.read_text(encoding="utf-8"))
    post = json.loads(POST_C2_ADJUDICATION.read_text(encoding="utf-8"))
    local = json.loads(LOCAL_MECHANISM_READJUDICATION.read_text(encoding="utf-8"))
    temporal = json.loads(TEMPORAL_EXPOSURE_READJUDICATION.read_text(encoding="utf-8"))
    semantics = json.loads(TREATMENT_SEMANTICS_READJUDICATION.read_text(encoding="utf-8"))
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
    if temporal.get("principle_dead_end_certified") is not True or temporal.get("broader_parent_phenomenon_falsified") is not False:
        raise ValueError("B-9/C2 temporal-exposure readjudication must close only the scoped mechanism")
    temporal_counter = (temporal.get("principle_diagnosis") or {}).get("counter_explanation") or {}
    if str(temporal_counter.get("opposite_principle") or "") != "Persistent context is a repeated intervention, not a new causal primitive.":
        raise ValueError("B-9/C2 temporal-exposure reduction principle drift")
    if semantics.get("principle_dead_end_certified") is not True or semantics.get("broader_parent_phenomenon_falsified") is not False:
        raise ValueError("B-9/C2 treatment-semantics readjudication must close only the scoped mechanism")
    semantics_counter = (semantics.get("principle_diagnosis") or {}).get("counter_explanation") or {}
    if not str(semantics_counter.get("opposite_principle") or "").startswith("Executable semantics is part of treatment identity"):
        raise ValueError("B-9/C2 treatment-semantics reduction principle drift")

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
        "temporal_exposure_readjudication": {
            "path": str(TEMPORAL_EXPOSURE_READJUDICATION.relative_to(PROJECT_ROOT)),
            "sha256": EXPECTED_TEMPORAL_EXPOSURE_READJUDICATION_SHA256,
        },
        "treatment_semantics_readjudication": {
            "path": str(TREATMENT_SEMANTICS_READJUDICATION.relative_to(PROJECT_ROOT)),
            "sha256": EXPECTED_TREATMENT_SEMANTICS_READJUDICATION_SHA256,
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
        "question": "The sparse context-dependent persistent-memory effect remains an archived phenomenon, but all current representation/local/temporal/treatment-semantics rescue classes are closed. What genuinely new primary evidence could introduce a structural object that survives same-information reduction?",
        "must_explain": [
            "a real sparse controlled memory-effect phenomenon",
            "failure of the historical transport representation to beat simple same-information baselines",
            "failure of candidate-local applicability/scope and structural-cart predictors",
            "failure of the earliest divergent action to carry the parent endpoint effect",
            "failure of static pre-divergence symbolic admissible-option overlap to improve a same-information predictor",
            "why any surviving object is not merely repeated, cumulative, or windowed longitudinal treatment exposure",
        ],
        "prospective_prediction_required": True,
        "pre_outcome_information_only": True,
        "temporal_exposure_standalone_branch_closed": True,
        "temporal_exposure_readjudication_sha256": EXPECTED_TEMPORAL_EXPOSURE_READJUDICATION_SHA256,
        "treatment_semantics_standalone_branch_closed": True,
        "treatment_semantics_readjudication_sha256": EXPECTED_TREATMENT_SEMANTICS_READJUDICATION_SHA256,
        "active_mechanism_seed": False,
        "must_beat_or_condition_on": [
            "target-family/context baseline",
            "source-family and source-target relation baseline",
            "first-divergence timing/action signature baseline",
            "candidate-local applicability/scope baseline",
            "static pre-divergence symbolic option-overlap baseline",
            "longitudinal treatment-history/state-history baseline for repeated or windowed memory exposure",
        ],
        "mandatory_reduction_before_treatment_semantics_experiment": [
            "nonstationary or versioned treatment models",
            "dynamic treatment or policy-regime changes with time-varying treatment identity",
            "intervention-mapping or treatment-definition drift",
            "concept drift, performative prediction, or adaptive data-collection explanations"
        ],
        "prohibited_rescues": [
            "endpoint success, terminal length, or any feature determined by the final outcome",
            "full-trajectory distances computed after success/failure is known",
            "renaming first-action mediation as K-step mediation without independent pre-outcome evidence",
            "reviving the historical B-9 transport representation without a new distinguishing prediction",
            "retuning symbolic action-skeleton overlap or selecting another post hoc local state feature on the same endpoint labels",
            "K-step mediation, ON/OFF windows, exposure duration, cumulative dose, or repeated memory conditioning as standalone novelty",
            "calling persistence or repeated exposure itself novel after the longitudinal-treatment same-information reduction",
            "calling a changed memory string a new causal primitive unless executable treatment semantics/version changes and versioned-treatment baselines fail",
            "treating this asset as novelty, Problem-Gate, Method, P0, GPU, or full-experiment authority",
        ],
        "opposite_search_seed": "No active mechanism seed remains on the current B-9/C2 substrate. Reopen only from new primary evidence that yields a preregistered ex-ante prediction after the strongest same-information baseline receives the same executable treatment map, version state, history, and schedule.",
        "cheapest_next_step": "Archive this positive phenomenon and move discovery budget to another substrate until a genuinely new primary structural constraint satisfies the treatment-semantics reopen condition; no further B-9/C2 rollout is authorized.",
    }
    source_manifest = {
        "provenance": provenance,
        "empirical_facts": facts,
        "failed_mechanisms": failed_mechanisms,
        "search_contract": search_contract,
    }
    return {
        "asset_ref": "positive-residual-asset:memory-effect-transport-b9-c2-20260816",
        "title": "Persistent memory effects remain archived after local, temporal, and treatment-semantics reductions",
        "source_kind": "provenance-audited-internal-positive-residual",
        "primary_url": "https://github.com/lightrain-a/agent-self-evolution-observatory/blob/main/research_pipeline/paper_first_c2_support_inventory_20260812.json",
        "source_sha256": _canonical_sha(source_manifest),
        "provenance": provenance,
        "empirical_facts": facts,
        "failed_mechanisms": failed_mechanisms,
        "search_contract": search_contract,
        "phenomenon_status": "SURVIVES_AS_ARCHIVED_PARENT_EVIDENCE",
        "mechanism_status": "NO_ACTIVE_MECHANISM_AFTER_LOCAL_TEMPORAL_AND_TREATMENT_SEMANTICS_REDUCTIONS",
        "search_status": "ARCHIVED_NO_ACTIVE_MECHANISM_SEED",
        "search_active": False,
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
        "registry_id": "positive-residual-search-assets-v4",
        "assets": assets,
        "asset_count": len(assets),
        "active_asset_count": sum(row.get("search_active") is True for row in assets),
        "scientific_authority": False,
        "policy": {
            "phenomenon_support_does_not_authorize_a_new_problem": True,
            "failed_mechanisms_are_constraints_not_reasons_to_relax_gates": True,
            "positive_residual_assets_are_search_priors_only": True,
            "prospective_pre_outcome_prediction_required": True,
            "outcome_leakage_forbidden": True,
            "temporal_exposure_relabeling_is_not_a_new_mechanism": True,
            "next_memory_seed_requires_treatment_semantics_or_version_change": False,
            "treatment_semantics_seed_requires_versioned_treatment_reduction_first": True,
            "closed_positive_residual_assets_remain_archived_but_do_not_enter_search": True,
            "new_primary_evidence_required_to_reopen_closed_positive_residual": True,
        },
    }
