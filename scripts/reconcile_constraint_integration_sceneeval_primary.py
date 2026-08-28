from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "generated" / "constraint-integration-cross-substrate-proposal-20260828.json"
SCENEEVAL_AUDIT = ROOT / "generated" / "sceneeval500-outcome-blind-constraint-audit-20260828.json"
HSM_PREFLIGHT = ROOT / "generated" / "sceneeval500-hsm-released-output-preflight-20260828.json"
HSM_MANIFEST = ROOT / "generated" / "hsm-sceneeval500-release-manifest-20260828.json"
INDEPENDENT_REVIEW = ROOT / "generated" / "constraint-integration-sceneeval-independent-review-20260828.json"
PREREG_DRAFT = ROOT / "generated" / "sceneeval500-prerequisite-coupling-preregistration-draft-20260828.json"
TOPOLOGY_IMPLEMENTATION = ROOT / "generated" / "sceneeval500-logistic-normal-topology-implementation-preflight-20260828.json"
LEGO_AUDIT = ROOT / "generated" / "lego-bench-outcome-blind-construct-audit-20260828.json"
LEGO_EXEC = ROOT / "generated" / "constraint-integration-executability-preflight-20260828.json"

EXPECTED_SCENEEVAL_AUDIT_SHA = "a3eaaa0571d51928e70f0094de1d0d4542211de165d1a196135be55df1247e45"
EXPECTED_HSM_PREFLIGHT_SHA = "75053aea6c84b467431066edd6b9cf9e898cdf013adbe0c571dce16645009348"
EXPECTED_HSM_MANIFEST_SHA = "6475bdd1c73a4b810f4bb6ee03e65be85567d07e33c04a15dc272360a829cd55"
EXPECTED_INDEPENDENT_REVIEW_SHA = "cb82ab4531dd1a76f05af2f027f3213ffc06b9e771beb45007a9446a55186862"
EXPECTED_PREREG_DRAFT_SHA = "269412b2b0ac270de00d1cca60f4e429ca3b48aae5d62359be073a6095abc365"
EXPECTED_TOPOLOGY_IMPLEMENTATION_SHA = "4021b01498c5d6f18219fb1b3f34c4a77d2ed217f6dfeaba1a49cd7a83bb9f5a"
EXPECTED_LEGO_AUDIT_SHA = "f8e845bb66d5c3ae897e939bb9877c1ae85e0491955a4d099e45d6f8bd7d868d"
EXPECTED_LEGO_EXEC_SHA = "15cf610915f3d3cd1e144f81207ac240517d0e5969418dd8e13e86b719d49f13"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_digest(path: Path, expected: str) -> None:
    actual = sha256(path)
    if actual != expected:
        raise SystemExit(f"artifact digest drift: {path.name}: {actual} != {expected}")


def main() -> None:
    require_digest(SCENEEVAL_AUDIT, EXPECTED_SCENEEVAL_AUDIT_SHA)
    require_digest(HSM_PREFLIGHT, EXPECTED_HSM_PREFLIGHT_SHA)
    require_digest(HSM_MANIFEST, EXPECTED_HSM_MANIFEST_SHA)
    require_digest(INDEPENDENT_REVIEW, EXPECTED_INDEPENDENT_REVIEW_SHA)
    require_digest(PREREG_DRAFT, EXPECTED_PREREG_DRAFT_SHA)
    require_digest(TOPOLOGY_IMPLEMENTATION, EXPECTED_TOPOLOGY_IMPLEMENTATION_SHA)
    require_digest(LEGO_AUDIT, EXPECTED_LEGO_AUDIT_SHA)
    require_digest(LEGO_EXEC, EXPECTED_LEGO_EXEC_SHA)

    proposal = json.loads(PROPOSAL.read_text(encoding="utf-8"))
    sceneeval = json.loads(SCENEEVAL_AUDIT.read_text(encoding="utf-8"))
    hsm = json.loads(HSM_PREFLIGHT.read_text(encoding="utf-8"))
    independent_review = json.loads(INDEPENDENT_REVIEW.read_text(encoding="utf-8"))
    prereg = json.loads(PREREG_DRAFT.read_text(encoding="utf-8"))
    topology_implementation = json.loads(TOPOLOGY_IMPLEMENTATION.read_text(encoding="utf-8"))

    if proposal.get("proposal_id") != "CROSS-SUBSTRATE-CONSTRAINT-INTEGRATION-20260828":
        raise SystemExit("unexpected proposal identity")
    relation = proposal.get("relation_to_port010") or {}
    if relation.get("port010_effective_status") != "HOLD_EVIDENCE_REVIEW_BLOCKED" or relation.get("port010_reopen_effect") is not False:
        raise SystemExit("PORT-010 separation invariant drifted")
    if any(proposal.get("authority", {}).values()):
        raise SystemExit("proposal already carries authority")
    if sceneeval.get("scientific_authority") is not False or sceneeval.get("execution_authority") is not False:
        raise SystemExit("SceneEval audit leaked authority")
    if hsm.get("scientific_authority") is not False or hsm.get("execution_authority") is not False:
        raise SystemExit("HSM preflight leaked authority")
    if independent_review.get("status") != "REVISE_BEFORE_PREREGISTRATION" or independent_review.get("scientific_authority") is not False:
        raise SystemExit("independent SceneEval review did not preserve the revise gate")
    prereg_gates = prereg.get("gates_after_this_preflight") or {}
    if prereg.get("status") != "MODEL_REVISION_COMPILED_POWER_PREFLIGHT_ONLY" or prereg_gates.get("formal_preregistration_clear") is not False:
        raise SystemExit("SceneEval preregistration draft unexpectedly cleared the formal gate")
    if prereg.get("scientific_authority") is not False or prereg.get("execution_authority") is not False:
        raise SystemExit("SceneEval preregistration draft leaked authority")
    if topology_implementation.get("status") != "CORE_TOPOLOGY_LIKELIHOOD_SYNTHETIC_PASS":
        raise SystemExit("SceneEval topology implementation did not pass synthetic validation")
    if topology_implementation.get("scientific_authority") is not False or topology_implementation.get("execution_authority") is not False:
        raise SystemExit("SceneEval topology implementation leaked authority")

    proposal["status"] = "ZERO_EXECUTION_AUTHORITY_SCENEEVAL_CORE_IMPLEMENTED_HOLD_CALIBRATION_AND_ACCESS"
    proposal["canonical_candidate_id"] = None
    proposal["generator_admission"] = "PENDING"
    proposal["scientific_authority"] = False
    proposal["execution_authority"] = False
    proposal["provider_calls_executed"] = int((independent_review.get("provider_accounting") or {}).get("completed_voting_review_calls") or 0) + int((independent_review.get("provider_accounting") or {}).get("confirmed_nonvoting_provider_calls") or 0)
    proposal["review_provider_completed_voting_calls"] = int((independent_review.get("provider_accounting") or {}).get("completed_voting_review_calls") or 0)
    proposal["review_provider_nonvoting_confirmed_calls"] = int((independent_review.get("provider_accounting") or {}).get("confirmed_nonvoting_provider_calls") or 0)
    proposal["review_connector_indeterminate_invocations"] = int((independent_review.get("provider_accounting") or {}).get("connector_indeterminate_invocations") or 0)
    proposal["scientific_execution_provider_calls"] = 0
    proposal["gpu_calls_executed"] = 0

    proposal["scientific_object"] = {
        "title": "Cross-type constraint failure coupling in text-guided 3D scene generation",
        "question": "After conditioning on ordinary instruction load and each semantic requirement type's marginal difficulty, are requirement failures within one generated 3D scene still conditionally dependent across types, or is apparent collapse explained by independent multiplicative accumulation?",
        "irreducible_object": "A prerequisite-aware generator/evaluator-system residual: after separating the shared ObjMatching prerequisite stage, do downstream Object Attribute, Object-Object Relationship, and Object-Architecture Relationship failures exhibit type-specific dependence beyond ordinary load, calibrated marginal difficulty, and exchangeable scene-level generic failure propensity? Object Count is matching-derived and therefore a prerequisite/control channel, not a fourth peer downstream outcome.",
        "exact_ex_ante_prediction": "On frozen instruction-grouped held-out folds, a preregistered nonexchangeable downstream coupling model over prerequisite-eligible ObjAttr/OORel/OARel outcomes will improve predictive log loss/ELPD over N2: the same-information prerequisite-aware conditional-independent model plus exchangeable scene-level frailty/overdispersion. Residual type-specific dependence must survive verified matching/prerequisite conditioning; larger residual under higher pre-outcome type entropy is secondary.",
        "strongest_same_information_baseline": "N2: calibrated downstream marginals with generator identity, authored difficulty, instruction words, total/per-type loads and official matching/prerequisite state, plus exchangeable scene-level frailty/overdispersion and no type-specific downstream covariance/interaction.",
        "prediction_disagreement": "N2 predicts that after shared matching prerequisites and generic scene quality are accounted for, remaining downstream failures are conditionally independent across semantic types. The candidate predicts reproducible nonexchangeable type-specific residual dependence beyond N2.",
        "scope_boundary": "This is an independently proposed cross-substrate object. It is not a reproduction, completion, or reopen of VWE-specific PORT-010; it is not yet a causal representation-mechanism claim. Type entropy is a frozen moderator of coupling burden, not the primary scientific object."
    }

    proposal["substrate"] = {
        "primary_benchmark": "SceneEval-500",
        "primary_release": "SceneEval-500_v250610",
        "official_evaluator": "SceneEval",
        "evaluator_release": "SceneEval_v1.1.1",
        "benchmark_unit": "one released natural-language scene description with explicit typed semantic requirement annotations",
        "instruction_count": 500,
        "authored_difficulty_counts": {"easy": 150, "medium": 200, "hard": 150},
        "released_constraint_types": ["ObjCount", "ObjAttr", "OORel", "OARel"],
        "released_constraint_type_meanings": {
            "ObjCount": "Object Count",
            "ObjAttr": "Object Attribute",
            "OORel": "Object-Object Relationship",
            "OARel": "Object-Architecture Relationship"
        },
        "primary_endpoint": "binary validity of prerequisite-eligible ObjAttr/OORel/OARel requirements under a frozen evaluator lane; ObjCount/shared matching is prerequisite/control state",
        "secondary_endpoints": [
            "per-channel success rate",
            "scene-level all-requirements success",
            "SceneEval non-VLM physical metrics as orthogonal diagnostics only"
        ],
        "why_primary_now": "SceneEval-500 exposes 500 complete typed prompt annotations and a multi-generator evaluation adapter, providing substantially more pre-outcome structure than the 130-instruction LEGO substrate while preserving a same-information conditional-independence null."
    }

    proposal["construct_preflight"] = {
        "artifact": str(SCENEEVAL_AUDIT.relative_to(ROOT)),
        "artifact_sha256": EXPECTED_SCENEEVAL_AUDIT_SHA,
        "status": sceneeval["status"],
        "raw_total_spec_count": sceneeval["constructs"]["raw_total_spec_count"],
        "constraint_type_entropy": sceneeval["constructs"]["constraint_type_entropy"],
        "instruction_words": sceneeval["constructs"]["instruction_words"],
        "strict_matched_f0": {
            key: value
            for key, value in sceneeval["strict_matched_f0"].items()
            if key != "pairs"
        },
        "direct_collision": sceneeval["direct_collision"],
        "measurement_dependency_preflight": sceneeval["measurement_dependency_preflight"],
        "scientific_result": False
    }

    proposal["secondary_substrates"] = [
        {
            "name": "LEGO-Bench",
            "role": "secondary cross-substrate replication after primary SceneEval measurement validity clears",
            "construct_artifact": str(LEGO_AUDIT.relative_to(ROOT)),
            "construct_artifact_sha256": EXPECTED_LEGO_AUDIT_SHA,
            "execution_artifact": str(LEGO_EXEC.relative_to(ROOT)),
            "execution_artifact_sha256": EXPECTED_LEGO_EXEC_SHA,
            "status": "CONSTRUCT_CLEAR_RUNTIME_NOT_READY",
            "scientific_authority": False
        },
        {
            "name": "InstructScene / 3D-FRONT",
            "role": "structured-representation mechanism reference and later intervention/baseline substrate; generic scene-graph conditioning is prior art, not the claimed contribution",
            "repository_revision": "a9097a62c484c56ac7be5ec2928ef497cbbaaf24",
            "status": "SOURCE_PINNED_DATA_AND_TWO_STAGE_CHECKPOINT_EXECUTION_NOT_YET_FROZEN",
            "scientific_authority": False
        }
    ]

    proposal["current_source_collision_review"]["sceneeval_direct_collision"] = (
        "SceneEval-500 already supplies author-defined easy/medium/hard difficulty and its metadata audit shows total explicit requirement count and instruction length strongly track that axis. Therefore difficulty/count degradation is treated as prior benchmark structure, not a new contribution."
    )
    proposal["current_source_collision_review"]["surviving_primary_object"] = (
        "prerequisite-aware downstream semantic failure coupling beyond N2: same-information conditional independence plus exchangeable scene-level frailty"
    )

    proposal["independent_reduction_review"] = {
        "artifact": str(INDEPENDENT_REVIEW.relative_to(ROOT)),
        "artifact_sha256": EXPECTED_INDEPENDENT_REVIEW_SHA,
        "status": independent_review["status"],
        "voting_reviewer_count": len(independent_review.get("voting_reviews") or []),
        "consensus": independent_review["consensus"],
        "provider_accounting": independent_review["provider_accounting"],
        "scientific_authority": False,
        "execution_authority": False
    }

    proposal["measurement_model_revision"] = {
        "artifact": str(PREREG_DRAFT.relative_to(ROOT)),
        "artifact_sha256": EXPECTED_PREREG_DRAFT_SHA,
        "status": prereg["status"],
        "primary_channels": prereg["measurement_contract"]["stage_D_downstream"]["primary_channels"],
        "prerequisite_control": prereg["measurement_contract"]["stage_P_prerequisite"]["ObjCount_role"],
        "strongest_null": prereg["nested_model_contract"]["N2_strongest_null"],
        "candidate_model": prereg["nested_model_contract"]["candidate"],
        "annotated_all_three_scene_count": prereg["annotation_availability"]["annotated_all_three_scene_count"],
        "power_design_interpretation": prereg["power_design_preflight"]["design_interpretation"],
        "formal_preregistration_clear": False,
        "remaining_blockers": prereg_gates["why_not_clear"],
        "scientific_authority": False,
        "execution_authority": False
    }

    proposal["topology_implementation_preflight"] = {
        "artifact": str(TOPOLOGY_IMPLEMENTATION.relative_to(ROOT)),
        "artifact_sha256": EXPECTED_TOPOLOGY_IMPLEMENTATION_SHA,
        "status": topology_implementation["status"],
        "runtime": topology_implementation["runtime"],
        "implementation_contract": topology_implementation["implementation_contract"],
        "synthetic_validation_summary": {
            "nesting_error": topology_implementation["synthetic_validation"]["exact_nesting_loglik_absolute_error"],
            "null_heldout_candidate_minus_n2": topology_implementation["synthetic_validation"]["exchangeable_null"]["heldout_candidate_minus_n2_log_likelihood"],
            "null_topology_deviation": topology_implementation["synthetic_validation"]["exchangeable_null"]["candidate"]["max_exchangeability_deviation"],
            "alternative_heldout_candidate_minus_n2": topology_implementation["synthetic_validation"]["nonexchangeable_alternative"]["heldout_candidate_minus_n2_log_likelihood"],
            "alternative_topology_deviation": topology_implementation["synthetic_validation"]["nonexchangeable_alternative"]["candidate"]["max_exchangeability_deviation"],
        },
        "remaining_implementation_blockers": topology_implementation["remaining_implementation_blockers"],
        "scientific_authority": False,
        "execution_authority": False
    }

    proposal["executability_preflight"] = {
        "artifact": str(HSM_PREFLIGHT.relative_to(ROOT)),
        "artifact_sha256": EXPECTED_HSM_PREFLIGHT_SHA,
        "status": hsm["status"],
        "author_released_full_generator_output_identified": True,
        "generator": "HSM",
        "released_scene_count": 500,
        "release_manifest_artifact": str(HSM_MANIFEST.relative_to(ROOT)),
        "release_manifest_sha256": EXPECTED_HSM_MANIFEST_SHA,
        "current_69_content_access": "BLOCKED_BY_ORDINARY_HUGGINGFACE_GATED_ACCESS_403",
        "official_semantic_evaluator_provider_bound": True,
        "official_semantic_evaluator_model": "gpt-4o-2024-08-06",
        "local_qwen_substitution_is_official_metric": False,
        "execution_authority": False,
        "scientific_authority": False
    }

    proposal["outcome_exposure_control"] = {
        "per_case_generation_outputs_read": False,
        "per_case_sceneeval_metric_outputs_read": False,
        "per_case_baseline_scores_read": False,
        "performance_conditioned_pair_selection": False,
        "published_aggregate_baseline_results_seen_during_source_survey": True,
        "published_aggregate_results_used_to_choose_construct_or_pairs": False,
        "construct_selection_inputs": [
            "SceneEval Description",
            "SceneEval ObjCount",
            "SceneEval ObjAttr",
            "SceneEval OORel",
            "SceneEval OARel",
            "SceneEval benchmark-authored Difficulty"
        ],
        "legacy_lego_construct_was_also_outcome_blind": True
    }

    source = proposal.setdefault("source_provenance", {})
    source["sceneeval"] = {
        "repository": "https://github.com/3dlg-hcvc/SceneEval",
        "evaluator_release": "SceneEval_v1.1.1",
        "evaluator_release_commit_display": "5d999f2",
        "code_archive_sha256": sceneeval["source"]["code_archive_sha256"],
        "benchmark_release": "SceneEval-500_v250610",
        "benchmark_release_commit_display": "3b84b5e",
        "data_archive_sha256": sceneeval["source"]["data_archive_sha256"],
        "annotations_sha256": sceneeval["source"]["annotations_sha256"]
    }
    source["hsm_released_sceneeval_outputs"] = {
        "dataset": "https://huggingface.co/datasets/3dlg-hcvc/hsm",
        "dataset_revision": hsm["generator_output_surface"]["dataset_revision"],
        "generated_scenes_commit": hsm["generator_output_surface"]["generated_scenes_commit"],
        "manifest_sha256": EXPECTED_HSM_MANIFEST_SHA,
        "file_oid_size_root_sha256": hsm["generator_output_surface"]["file_oid_size_root_sha256"],
        "scene_count": 500,
        "access_status": "GATED_WAIT_AUTHORIZED_IDENTITY",
        "scientific_authority": False
    }

    proposal["candidate_generator_suite"] = {
        "primary_released_output_lane": {
            "method": "HSM",
            "scene_count": 500,
            "generator_rerun_required": False,
            "content_status": "WAIT_GATED_DATASET_ACCESS",
            "role": "first generator lane because author-released full SceneEval-500 outputs avoid generator rerun confounding"
        },
        "sceneeval_supported_method_families_for_later_extension": [
            "ATISS",
            "DiffuScene",
            "InstructScene",
            "LayoutGPT",
            "Holodeck",
            "LayoutVLM",
            "HSM"
        ],
        "execution_status": "NOT_AUTHORIZED",
        "note": "The complete HSM release manifest qualifies a promising no-generator-rerun lane but does not authorize access, evaluation, provider calls, GPU execution, or scientific interpretation. Other generators require separate source-faithful output/rerun qualification."
    }

    proposal["future_analysis_contract_if_authorized"] = sceneeval["future_analysis_contract_if_authorized"]
    proposal["future_analysis_contract_if_authorized"]["evaluator_lane_rule"] = (
        "Official SceneEval semantic results must use the frozen official evaluator/model contract; any independently qualified local evaluator must be named and reported as a separate evaluator variant and may not be aliased to official SceneEval scores."
    )
    proposal["future_analysis_contract_if_authorized"]["initial_generator_lane"] = (
        "HSM author-released 500-scene bundle after legitimate gated access; no generator rerun in the initial bounded P0 lane. A second independently qualified generator is mandatory before paper-level transport/generalization claims."
    )

    proposal["falsifiers"] = sceneeval["falsifiers"] + [
        "The effect is present only for HSM and does not survive a preregistered second generator lane once one becomes independently executable.",
        "The semantic evaluator cannot expose stable per-requirement outcomes without model-specific mapping artifacts dominating the residual."
    ]

    proposal["method_intervention"] = {
        "status": "DEFERRED_UNTIL_PREREGISTRATION_REVIEW_AND_PRIMARY_COUPLING_PASS",
        "candidate_only": "information-equivalent typed/structured representation intervention, evaluated by whether it specifically reduces the frozen cross-type coupling residual rather than merely improving mean score",
        "prior_art_boundary": "GraphDreamer and InstructScene already establish graph/semantic-graph conditioning; generic graph conditioning is not a standalone novelty claim.",
        "forbidden_now": "Do not design/tune an intervention from SceneEval outcomes before the primary problem gate is satisfied."
    }

    proposal["next_gate"] = {
        "name": "MARGINAL_CALIBRATION_UNCERTAINTY_AND_ASSET_ACCESS_PREFLIGHT",
        "required": True,
        "requirements": [
            "freeze and synthetic-test the high-dimensional same-information marginal metadata calibration that produces eta offsets inside each training fold",
            "freeze and synthetic-test the scene-level bootstrap/uncertainty and practical-equivalence implementation; the core N2/candidate topology likelihood is already synthetic-PASS",
            "preserve the already frozen two-stage prerequisite/downstream contract, metadata composition vocabulary, N0/N1/N2 ladder, 52-pair panel, and power thresholds without outcome-driven changes",
            "bind a new canonical candidate identity only after the independent REVISE gate is fully satisfied; never reuse PORT-010",
            "obtain legitimate HSM gated-dataset access or leave the bounded P0 lane waiting",
            "freeze official GPT-4o evaluator versus separately named local-evaluator lanes before reading per-case semantic outcomes",
            "qualify a second generator lane before any paper-level cross-generator/transport claim",
            "preserve the 52-pair outcome-blind SceneEval matched panel without outcome-based replacement"
        ]
    }

    proposal["authority"] = {
        "canonical_generator": False,
        "problem_gate": False,
        "paper_design": False,
        "method": False,
        "experiment": False,
        "local_validation": False,
        "p0": False,
        "provider": False,
        "gpu": False,
        "scientific": False
    }

    PROPOSAL.write_text(json.dumps(proposal, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "proposal_id": proposal["proposal_id"],
        "status": proposal["status"],
        "primary_benchmark": proposal["substrate"]["primary_benchmark"],
        "matched_pairs": proposal["construct_preflight"]["strict_matched_f0"]["selected_disjoint_pairs"],
        "initial_generator": proposal["candidate_generator_suite"]["primary_released_output_lane"]["method"],
        "initial_generator_content_status": proposal["candidate_generator_suite"]["primary_released_output_lane"]["content_status"],
        "generator_admission": proposal["generator_admission"],
        "authority": proposal["authority"]
    }, indent=2))


if __name__ == "__main__":
    main()
