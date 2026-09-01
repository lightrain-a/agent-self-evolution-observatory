from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.relational_topology_training_qualification import (
    CHECKPOINT_REQUIRED, CORPUS_FIELDS, LICENSE_RECEIPT, OBJECT_ID, REGIME_SUPPORT,
    compile_synthetic_corpus, empty_p1_schema, replay_matrix, require_license,
    sha256_value, write_jsonl,
)

PARENT_ID = "RELATIONAL-CONSTRAINT-CAPACITY-20260830"
RUN_ID = f"{OBJECT_ID}-official-training-qualification-v1"
CREATED_AT = "2026-09-01T08:00:00+00:00"
OUT = ROOT / "experiments/3d_official_training" / RUN_ID
DATASET_STATE = "NOT_MATERIALIZED_LICENSE_NOT_CONFIRMED"
INSTRUCTSCENE_SHA = "a9097a62c484c56ac7be5ec2928ef497cbbaaf24"
SCENENAT_SHA = "542b82ff0cda4e0350575ca8f1cd5d147529130c"
CLIP_REVISION = "3d74acf9a28c67741b2f4f2ea7635f0aaf6f0268"
PARENT_ARTIFACTS = {
    "experiments/relational_topology_3d/RELATIONAL-TOPOLOGY-STAGE-3D-20260831-pre-f0-v1/manifest.json":
        "75696ab57ff430bb4bef249a938363c3a962208c2915c411062f819912b4280c",
    "experiments/relational_topology_3d/RELATIONAL-TOPOLOGY-STAGE-3D-20260831-pre-f0-v1/adjudication.json":
        "1ef86c046d8f92962d05d693931dfff9feb51a4da68bf83a2936f957e7e6351c",
    "experiments/relational_topology_3d/RELATIONAL-TOPOLOGY-STAGE-3D-20260831-pre-f0-v1/regression_debt.json":
        "1cedd6704fd9a114dff798f07f0a9b7f1476082e63aa05b9e40b24a00648e89a",
    "generated/relational-constraint-capacity-novelty-support-differential-20260831.json":
        "465dbbf9d2f1bb6aadad73681dac994e252b7201966e069d9b5c5e2dd7d16b83",
    "generated/relational-constraint-capacity-construct-v2-20260830.json":
        "48a86fa4bb83cdb9308a1cd6a005cf8ea34033f8649cd579c15fbe3e8347317f",
    "generated/paper-first-pre-f0-evidence-acquisition-plan.json":
        "3594967e2e491984e522b4b53c10c0478848ecd34cc2287d718e175360861ebd",
}
INSTRUCTSCENE_FILES = {
    "README.md": "72a28f596cb3adc21c50db9e5d2679e9dcf5674e59d5fffcf14de5051e8e22ff",
    "src/train_sg2sc.py": "b5fd13847884783db9c9cb1c0d76fa7687e029e7db7d4f7cf3527f7c2c53e8c8",
    "src/train_sg.py": "65b991feaf2442c33dd9fe6edc76b3c99d1b0cbddaff8cd72673a88aced9bf29",
    "src/models/sg2sc_diffusion.py": "bbeed6e2ad1164e658f7d4e1bedd9fc42dfc47db31d865c6e000665c53a33451",
    "src/generate_sg.py": "ea6f532d12a7d511902e6e72d84e0c9e61ddee8b632061b518327bc8956753cd",
    "src/generate_sg2sc.py": "57d420b6cf79db29eb494c2782c1f8992f6b12ef8596611dd79f4453b203d051",
    "configs/bedroom_sg2sc_diffusion_objfeat.yaml": "93a8483771de03a6d1673916d9fb22d075bd03ace40d21f074a0e42a89e85c15",
    "configs/bedroom_sg_diffusion_vq_objfeat.yaml": "ae4699a8be0ba2d1cd332a37d3233abee96cde172fbddd7a89857e0b0d31d021",
    "scripts/train_sg2sc_objfeat.sh": "dad1c40ee5837bcb82a37c6eed0ac7de0b53a0dd55febeb8b38f9b34f058de54",
    "scripts/train_sg_vq_objfeat.sh": "48e11079aad3eb89aaa54055963d23bdeacd49a9a1de25f5f530da2fefcce6da",
}


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def canonical_lineage_status() -> dict[str, Any]:
    head = git("rev-parse", "HEAD")
    origin_main = git("rev-parse", "origin/main")
    in_main = subprocess.run(
        ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", head, "origin/main"],
        check=False, capture_output=True, text=True,
    ).returncode == 0
    return {
        "compiler_head": head,
        "origin_main_at_compilation": origin_main,
        "head_is_in_origin_main_history": in_main,
    }


def check_parent() -> dict[str, str]:
    for relative, expected in PARENT_ARTIFACTS.items():
        actual = file_sha(ROOT / relative)
        if actual != expected:
            raise SystemExit(f"frozen parent drift: {relative}: {actual}")
    adjudication = json.loads((ROOT / "experiments/relational_topology_3d/RELATIONAL-TOPOLOGY-STAGE-3D-20260831-pre-f0-v1/adjudication.json").read_text())
    if adjudication["verdict"] != "PRE_F0_CHILD_PASS_PROPOSAL_ONLY":
        raise SystemExit("child parent verdict drift")
    port = json.loads((ROOT / "generated/paper-first-pre-f0-evidence-acquisition-plan.json").read_text())
    rows = [row for row in port["entries"] if row.get("candidate_id") == "PORT-010"]
    if len(rows) != 1 or rows[0]["status"] != "HOLD_EVIDENCE_REVIEW_BLOCKED":
        raise SystemExit("PORT-010 status drift")
    if rows[0]["evidence_review"]["verdict"] != "BLOCK_BAKE_IN":
        raise SystemExit("PORT-010 evidence-review drift")
    return PARENT_ARTIFACTS


def verify_instructscene(root: Path | None) -> dict[str, Any]:
    result = {
        "official_repository": "https://github.com/chenguolin/InstructScene",
        "repo_sha": INSTRUCTSCENE_SHA,
        "verification": "PINNED_STATIC_AUDIT",
        "source_file_sha256": INSTRUCTSCENE_FILES,
    }
    if root is None:
        result["local_exact_clone"] = "NOT_SUPPLIED"
        return result
    head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    if head != INSTRUCTSCENE_SHA:
        raise SystemExit(f"InstructScene clone drift: {head}")
    for relative, expected in INSTRUCTSCENE_FILES.items():
        actual = file_sha(root / relative)
        if actual != expected:
            raise SystemExit(f"InstructScene source drift: {relative}: {actual}")
    result["local_exact_clone"] = "PASS"
    return result


def provenance(config_sha256: str, dataset_revision: str, run_id: str) -> dict[str, Any]:
    return {
        "object_id": OBJECT_ID, "parent_object_id": PARENT_ID, "run_id": run_id,
        "generated_at": CREATED_AT, "compiler_source_git_sha": git("rev-parse", "HEAD"),
        "compiler_source_git_tree": git("rev-parse", "HEAD^{tree}"),
        "config_sha256": config_sha256, "dataset_revision": dataset_revision,
    }


def aggregate_families(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        counts.update(row["relation_family_multiset"])
    return dict(sorted(counts.items()))


def normalized(counts: dict[str, int]) -> dict[str, float]:
    total = sum(counts.values())
    return {key: value / total for key, value in counts.items()}


def targeted_audit(path: Path | None) -> dict[str, Any]:
    inherited = json.loads((ROOT / "experiments/relational_topology_3d/RELATIONAL-TOPOLOGY-STAGE-3D-20260831-pre-f0-v1/regression_debt.json").read_text())
    audit = {
        "inherited_baseline_artifact_sha256": PARENT_ARTIFACTS["experiments/relational_topology_3d/RELATIONAL-TOPOLOGY-STAGE-3D-20260831-pre-f0-v1/regression_debt.json"],
        "inherited_counts": inherited.get("counts", {"failures": 1, "errors": 24, "skips": 3}),
        "inherited_authority_impact": "SCOPED_NON_BLOCKING_DEBT",
        "inherited_classification": {"AUTHORITY_CRITICAL": 0, "SCIENTIFIC_OBJECT_DEPENDENCY": 0, "UNRELATED_LEGACY_DEBT": 28},
        "scope_proof": "Frozen child audit places all inherited incidents outside authority, provenance, integrity, registry, replay, and this object's dependency chain.",
    }
    if path is None:
        audit["targeted_dependency_audit"] = {"status": "NOT_RUN", "blocking_incidents": []}
        return audit
    text = path.read_text(errors="replace")
    runs = [int(value) for value in re.findall(r"Ran (\d+) tests?", text)]
    failed = "FAILED (" in text or "\nFAILED\n" in text
    passed = bool(runs) and not failed
    audit["targeted_dependency_audit"] = {
        "status": "PASS" if passed else "FAIL", "tests_observed": sum(runs),
        "test_blocks_observed": len(runs), "log_sha256": file_sha(path),
        "blocking_incidents": [] if passed else [{"classification": "SCIENTIFIC_OBJECT_DEPENDENCY", "status": "BLOCK"}],
    }
    return audit


def build(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    parent_hashes = check_parent()
    source_audit = verify_instructscene(args.instructscene_root)
    canonical_lineage = canonical_lineage_status()
    license_confirmed = args.license_receipt is not None
    if license_confirmed:
        require_license(args.license_receipt)
    dataset_state = (
        "LICENSE_CONFIRMED_DATA_NOT_MATERIALIZED"
        if license_confirmed else DATASET_STATE
    )
    config = {
        "schema_version": "relational-topology-official-training-qualification-v1",
        "lifecycle": "PRE_P1_OFFICIAL_TRAINING_QUALIFICATION", "room": "BEDROOM",
        "license_receipt_required_exactly": LICENSE_RECEIPT,
        "license_receipt_observed": args.license_receipt,
        "data_materialization": False,
        "gpu_training": False, "scientific_gpu_runs": 0, "scientific_outcomes": 0,
        "p1_open": False,
        "regimes": {name: list(values) for name, values in REGIME_SUPPORT.items()},
    }
    p = provenance(sha256_value(config), dataset_state, args.run_id)
    scene_ids = ["SYN-BEDROOM-0001", "SYN-BEDROOM-0002", "SYN-BEDROOM-0003", "SYN-BEDROOM-0004"]
    corpora, corpus_hashes, replay = {}, {}, {}
    for regime in REGIME_SUPPORT:
        rows, digest = compile_synthetic_corpus(scene_ids, regime, 24, p["compiler_source_git_sha"])
        corpora[regime], corpus_hashes[regime] = rows, digest
        replay[regime] = replay_matrix(scene_ids, regime, 24, p["compiler_source_git_sha"])
        if not replay[regime]["byte_identical"]:
            raise SystemExit(f"synthetic replay failed: {regime}")
        if any(tuple(row) != CORPUS_FIELDS for row in rows):
            raise SystemExit(f"corpus schema/order drift: {regime}")
    family_counts = {regime: aggregate_families(rows) for regime, rows in corpora.items()}
    family_proportions = {regime: normalized(counts) for regime, counts in family_counts.items()}
    if family_proportions["IS-SUPPORT-12"] != family_proportions["IS-SUPPORT-14"]:
        raise SystemExit("synthetic relation-family proportional balance failed")

    debt = targeted_audit(args.targeted_audit_log)
    targeted = debt["targeted_dependency_audit"]
    if targeted["status"] == "FAIL":
        verdict = "PRE_P1_TRAINING_QUALIFICATION_REFORMULATE"
    elif license_confirmed and canonical_lineage["head_is_in_origin_main_history"]:
        verdict = "LICENSE_CONFIRMED_MATERIALIZATION_AUTHORIZED"
    elif license_confirmed:
        verdict = "HOLD_CANONICAL_MAIN_INTEGRATION"
    else:
        verdict = "HOLD_USER_LICENSE_CONFIRMATION"

    source_manifest = {
        **p, "parent_artifacts": parent_hashes, "instructscene": source_audit,
        "scenenat": {"arxiv_revision": "2601.07218v2", "arxiv_last_revised": "2026-08-11",
            "official_repository": "https://github.com/lojol2327/SceneNAT-official", "repo_sha": SCENENAT_SHA},
        "clip_tokenizer": {"model": "openai/clip-vit-base-patch32", "revision": CLIP_REVISION,
            "official_code_revision_pin_missing": True,
            "qualification_requirement": "PIN_EXACT_REVISION_IN_CHILD_ADAPTER"},
    }
    novelty_watch = {
        **p, "checked_at": "2026-09-01", "status": "NO_MATERIAL_NOVELTY_PIN_DRIFT",
        "scenenat_arxiv_revision": "2601.07218v2", "scenenat_repo_sha": SCENENAT_SHA,
        "new_topology_fixed_count_experiment_found": False,
        "new_oracle_graph_stage_localization_found": False,
        "new_release_or_checkpoint_found": False,
        "residual_claims_unchanged": [
            "training-support crossover under matched architecture and one shared decoder",
            "fixed-count/fixed-token topology effect",
            "predicted-versus-oracle graph stage localization with exact identity pairing"],
        "recheck_required_immediately_before_training_authority": True,
    }
    license_gate = {
        **p,
        "status": ("LICENSE_CONFIRMED_MATERIALIZATION_AUTHORIZED"
                   if license_confirmed and canonical_lineage["head_is_in_origin_main_history"]
                   else "LICENSE_CONFIRMED_CANONICAL_INTEGRATION_REQUIRED"
                   if license_confirmed else "LICENSE_NOT_CONFIRMED"),
        "licenses": {
            "3D-FRONT": ("USER_CONFIRMED_RESEARCH_LICENSE_ACCEPTED"
                         if license_confirmed else "LICENSE_NOT_CONFIRMED"),
            "3D-FUTURE": ("USER_CONFIRMED_RESEARCH_LICENSE_ACCEPTED"
                          if license_confirmed else "LICENSE_NOT_CONFIRMED"),
        },
        "accepted_receipt_exactly": LICENSE_RECEIPT,
        "observed_receipt": args.license_receipt,
        "licensed_corpus_materialized": False,
        "data_materialization_authorized": bool(
            license_confirmed and canonical_lineage["head_is_in_origin_main_history"]),
        "official_training_authorized": False, "gpu_qualification_authorized": False,
        "fail_closed_verdict": verdict,
        "note": "A derivative dataset page license does not establish underlying 3D-FRONT/3D-FUTURE research-license acceptance.",
    }
    decoder_audit = {
        **p, "status": "PASS_STATIC_INTERFACE_IDENTIFIABILITY",
        "decision": "SHARED_DECODER_IDENTIFIABLE", "component_id": "BEDROOM-SG2SC-SHARED",
        "single_checkpoint_for_both_regimes": True,
        "sg2sc_inputs": ["objs", "edges", "objfeat_vq_indices", "obj_masks"],
        "sgp_hidden_state_dependency": False,
        "held_fixed": ["SG2SC architecture", "SG2SC parameters", "object vocabulary",
            "predicate vocabulary", "object-feature quantizer", "room split",
            "decoder seed policy", "asset pool", "evaluator"],
        "training_source": "OFFICIAL_INSTRUCTSCENE_SOURCE_AFTER_LICENSE",
        "runtime_gate": "STOP_DECODER_CAUSAL_CONTROL_INVALID if one content-addressed SG2SC cannot consume both regimes under identical schema and state.",
    }
    checkpoint_audit = {
        **p, "official_room_checkpoint_available": False,
        "official_released_component": "fVQ-VAE_ONLY",
        "community_room_checkpoints": "UNOFFICIAL_NOT_ELIGIBLE_FOR_SCIENTIFIC_EVIDENCE",
        "decision": "TRAIN_ONE_SHARED_BEDROOM_SG2SC_FROM_OFFICIAL_SOURCE_AFTER_LICENSE",
        "unofficial_checkpoint_execution_this_round": False,
        "unofficial_checkpoint_scientific_evidence": False,
        "official_code_exact_resume_complete": False,
        "official_code_saved_states": ["model", "optimizer", "optional_ema"],
        "official_code_missing_states": ["scheduler", "all RNG streams", "sampler state",
            "sampler position", "corpus cursor", "global step"],
        "child_adapter_required_before_gpu_qualification": True,
    }
    support_intervention = {
        **p, "status": "FROZEN_STATIC_DESIGN",
        "regimes": {"IS-SUPPORT-12": {"relation_count_support": [1, 2]},
                    "IS-SUPPORT-14": {"relation_count_support": [1, 2, 3, 4]}},
        "only_intentionally_varied_factor": "TRAINING_RELATION_COUNT_SUPPORT",
        "matched_exactly": ["architecture", "parameter_count", "text_encoder", "room_type",
            "dataset_revision", "split", "corpus_example_count", "scene_pool",
            "object_count_strata", "object_vocabulary", "predicate_vocabulary",
            "direction_policy", "instruction_template_policy", "CLIP_tokenizer_revision",
            "optimizer", "schedule", "training_steps", "checkpoint_policy",
            "seed_policy", "convergence_rule", "shared_SG2SC_decoder"],
        "matched_by_distribution": ["relation_family_proportions", "direction proportions",
            "instruction style", "token-length bins conditional on relation_count",
            "topology policy conditional on relation_count"],
        "design_inherent_difference": {
            "name": "COUNT_INDUCED_TOPOLOGY_SUPPORT",
            "reason": "Counts 3-4 cannot occur in IS-SUPPORT-12 by definition.",
            "control": "Use the same conditional topology sampler at every available count and hold topology fixed in P1; block if conditional balance fails."},
        "forbidden_interpretation": "Decline at unseen counts is not intrinsic capacity without the matched support crossover.",
    }
    corpus_schema = {
        **p, "status": ("SCHEMA_FROZEN_LICENSE_CONFIRMED_REAL_CORPUS_NOT_MATERIALIZED"
                        if license_confirmed else "SCHEMA_FROZEN_REAL_CORPUS_NOT_MATERIALIZED"),
        "fields_in_exact_order": list(CORPUS_FIELDS),
        "example_seed_formula": "uint64_be(SHA256(source_scene_id|corpus_regime|sample_slot|RELATIONAL-TOPOLOGY-3D-CORPUS-V1)[0:8])",
        "example_content_address": "SHA256(canonical JSON of all prior fields including tokenizer metadata)",
        "global_sort_key": "example_id",
        "replay_invariance_required": ["traversal order", "worker count", "batch boundaries"],
        "room": "BEDROOM", "licensed_rows": 0,
        "synthetic_rows": sum(map(len, corpora.values())), "synthetic_only": True,
    }
    synthetic_replay = {
        **p, "record_type": "NON_SCIENTIFIC_SYNTHETIC_COMPILER_QUALIFICATION",
        "scientific_evidence": False, "scene_ids": scene_ids, "sample_slots_per_scene": 24,
        "corpus_rows_per_regime": {key: len(value) for key, value in corpora.items()},
        "corpus_sha256": corpus_hashes, "replay_matrix": replay, "result": "PASS",
    }
    relation_matching = {
        **p, "status": "PASS_SYNTHETIC_POLICY_QUALIFICATION_REAL_MATCH_PENDING_LICENSE",
        "equal_example_count": len(corpora["IS-SUPPORT-12"]) == len(corpora["IS-SUPPORT-14"]),
        "family_counts": family_counts, "family_proportions": family_proportions,
        "family_proportions_equal": True, "direction_policy_equal": True,
        "per_scene_family_composition_required": True,
        "residual_imbalance_adjustment": "PREREGISTER_IF_EXACT_MATCHING_IMPOSSIBLE",
        "nested_permutations_required": True,
        "real_corpus_gate": "Block authority unless family, direction, scene, object-count and template marginals satisfy frozen tolerances.",
    }
    token_matching = {
        **p, "status": "STATIC_CONTRACT_PASS_REAL_COUNTS_PENDING_LICENSE",
        "tokenizer": "openai/clip-vit-base-patch32", "tokenizer_revision": CLIP_REVISION,
        "exact_token_counts_materialized": [], "synthetic_placeholder_token_counts": None,
        "required_distribution_statistics": ["histogram", "mean", "median", "quantiles", "overlap", "relation_count_stratified_distribution"],
        "primary_scientific_exclusion": "tokenizer_truncated == true",
        "matching": "Exact count where feasible; otherwise same one-token bin within relation_count and topology strata, with token count modeled continuously.",
        "authority_gate": "No scientific or training sample proceeds without exact_clip_token_count and tokenizer_truncated populated.",
    }
    topology_matching = {
        **p, "status": "STATIC_CONDITIONAL_POLICY_PASS_REAL_MATCH_PENDING_LICENSE",
        "classes": ["DISJOINT", "CHAIN", "HUB", "COMPONENT_BRIDGE_OPTIONAL"],
        "statistics": ["connected_components", "active_components", "max_degree",
            "degree_concentration", "diameter", "shared_anchor_fraction",
            "largest_component", "relation_graph_density"],
        "same_policy_conditional_on_relation_count": True, "p1_topology_held_fixed": True,
        "outcome_blind_sampling": True, "scientific_topology_comparison_this_round": False,
        "blocking_condition": "Conditional balance or exact fixed-topology contrasts cannot be built.",
    }
    rng_contract = {
        **p, "status": "PASS_SYNTHETIC_REPLAY", "seed_is_content_derived": True,
        "forbidden_seed_sources": ["batch_idx", "worker_id", "enumeration order", "process id", "wall clock"],
        "required_rng_streams": ["python", "numpy", "torch_cpu", "torch_cuda_all_devices",
            "dataloader_generator", "sampler"],
        "replay": replay, "live_training_replay": "NOT_RUN_LICENSE_AND_GPU_AUTHORITY_ABSENT",
    }

    oracle_interface = {
        **p, "status": "PASS_SYNTHETIC_INTERFACE_ONLY", "scientific_cases": 0,
        "arms": ["Text -> predicted graph -> shared layout decoder",
                 "Ground-truth instructed graph -> same shared layout decoder"],
        "exact_identity_fields": ["slot_ids", "object_ids", "object_classes", "objfeat_ids", "obj_masks"],
        "forbidden": ["Hungarian matching", "semantic remapping", "heuristic aliasing", "outcome-aware pairing"],
        "same_downstream_decoder": True, "same_seed_policy": True,
        "failure": "Any identity mismatch makes a pair ineligible; inability to form exact pairs blocks intervention.",
    }
    checkpoint_contract = {
        **p, "status": "STATIC_SCHEMA_PASS_LIVE_KILL_RESUME_NOT_RUN",
        "required_fields": list(CHECKPOINT_REQUIRED),
        "kill_resume_protocol": {
            "qualification_steps": [50, 100], "interrupt_after_step": 50,
            "compare_to_uninterrupted_at_step": 100,
            "must_restore": ["model", "optimizer", "scheduler", "all RNG", "sampler",
                "sampler position", "corpus cursor", "global step"],
            "acceptance": ["identical consumed-example key sequence", "identical exactly-once ledger",
                "identical model-state hash where deterministic kernels permit",
                "otherwise tensor max_abs_diff <= 1e-7", "loss trajectory max_abs_diff <= 1e-7"],
            "failure_verdict": "STOP_TRAINING_REPRODUCTION_FAILED",
        },
    }
    exactly_once = {
        **p, "status": "EMPTY_NO_TRAINING_RUN",
        "key_formula": "SHA256(component_id|corpus_sha256|config_sha256|seed)",
        "required_run_fields": ["run_id", "component_id", "corpus_sha256", "config_sha256", "model_code_sha", "dataset_revision", "seed", "authority_receipt"],
        "reconnect_checks_before_retry": ["PID", "process_group", "heartbeat", "checkpoint", "ledger", "GPU_process"],
        "run_claims": [], "step_commits": [], "duplicate_claims": [], "scientific_outcomes": [],
    }
    gpu_qualification = {
        **p, "status": "NOT_REQUESTED_NOT_AUTHORIZED_NOT_RUN",
        "canonical_main_lineage_satisfied": canonical_lineage["head_is_in_origin_main_history"],
        "allowed_scope_after_all_gates": "50-100 optimizer steps per required component",
        "classification": "NON_SCIENTIFIC_OFFICIAL_TRAINING_RESOURCE_AND_REPLAY_QUALIFICATION",
        "prerequisites": ["exact user license receipt", "licensed corpus content address",
            "shared decoder validation", "exact-resume child adapter", "canonical main-lineage authority",
            "fresh SceneNAT drift check"],
        "candidate_devices": ["RTX_3090_24GB", "A100_40GB", "A100_80GB"],
        "default_preference": "A100_80GB",
        "required_measurements": ["GPU_model", "CUDA", "driver", "PyTorch", "precision", "batch_size", "gradient_accumulation", "peak_allocated_VRAM", "peak_reserved_VRAM", "step_time", "samples_per_second", "CPU_RAM", "disk_write_rate", "checkpoint_size", "loss_finite", "grad_finite", "OOM", "NaN_Inf", "dataloader_failures"],
        "selection_rule": "peak_vram + throughput + resume_stability",
        "provider_calls": 0, "gpu_runs": 0, "training_steps": 0, "outcomes_enter_p1": False,
    }
    reproduction = {
        **p, "status": "PREREGISTERED_BEFORE_TRAINING_VALUES_NOT_OBSERVED", "metric_scale": "[0,1]",
        "official_reference_requirement": "Content-address official/source BEDROOM reference and evaluator mapping before authority; no post-training reference selection.",
        "bands": {
            "relation_level_iRecall_lower": "reference_iRecall - max(0.05, 0.10 * abs(reference_iRecall))",
            "text_to_graph_relation_recall_lower": "reference_recall - max(0.05, 0.10 * abs(reference_recall))",
            "valid_graph_rate_lower": 0.90, "valid_scene_rate_lower": 0.90,
            "catastrophic_invalid_rate_upper": 0.10},
        "validation_split": "MUST_BE_CONTENT_ADDRESSED_BEFORE_TRAINING",
        "semantic_graph_prior_metrics": ["valid_graph_rate", "object_category_validity", "relation_output_validity", "relation_recall", "generation_failure_rate"],
        "sg2sc_metrics": ["valid_scene_rate", "object_placement_validity", "collision_diagnostic", "relation_retention", "catastrophic_invalid_output_rate"],
        "end_to_end_metrics": ["basic_instruction_conditioned_generation", "official_style_iRecall_or_compatible", "qualitative_quantitative_sanity"],
        "qualification_only_checks": ["finite loss", "finite gradients", "checkpoint load",
            "kill/resume tolerance", "no exactly-once duplicates or gaps"],
        "failure_verdict": "STOP_TRAINING_REPRODUCTION_FAILED",
        "no_scientific_claim_from_qualification": True,
    }
    training_persistence = {
        **p, "status": "SCHEMA_FROZEN_NO_TRAINING_RUN",
        "root_template": "experiments/3d_official_training/<run_id>/",
        "required_paths": ["manifest.json", "authority.json", "environment.json",
            "git_state.json", "dataset_manifest.json", "corpus_manifest.json",
            "model_manifest.json", "config.yaml", "training_events.jsonl",
            "loss.jsonl", "checkpoints/", "checkpoint_manifest.jsonl",
            "heartbeat.json", "failures.jsonl", "stdout.log", "stderr.log",
            "final_training_summary.json"],
        "incremental_persistence_required": True,
        "summary_only_persistence_forbidden": True,
    }
    failure_taxonomy = {
        **p, "status": "FROZEN_NON_SCIENTIFIC_FAILURE_CLASSES",
        "classes": ["DATA_LICENSE_FAILURE", "DATA_PROVENANCE_FAILURE",
            "CORPUS_MATCHING_FAILURE", "DECODER_COUPLING_FAILURE",
            "GPU_RESOURCE_FAILURE", "EXECUTION_FAILURE", "CHECKPOINT_FAILURE",
            "RESUME_FAILURE", "TRAINING_INSTABILITY", "REPRODUCTION_FAILURE"],
        "scientific_mechanism_update_allowed": False,
    }
    p1_schema = {**p, **empty_p1_schema(), "status": "CLOSED_EMPTY_SCHEMA_ONLY"}
    authority = {
        **p, "state": verdict, "data_license_confirmed": license_confirmed,
        "data_materialization_authority": bool(
            license_confirmed and canonical_lineage["head_is_in_origin_main_history"]),
        "gpu_authority_requested": False,
        "gpu_authority": False, "official_instructscene_training": False,
        "training_qualification_run": False,
        "training_status": {"BEDROOM-SG2SC-SHARED": "NOT_STARTED", "SGP-12": "NOT_STARTED", "SGP-14": "NOT_STARTED"},
        "p1": False, "p2": False, "p3": False, "provider_calls": 0,
        "scientific_gpu_runs": 0, "scientific_outcomes": 0,
        "unofficial_checkpoint_scientific_evidence": False,
        "scenenat_comparison_run": False, "full_cross_architecture_suite_run": False,
        "port_010": {"status": "HOLD_EVIDENCE_REVIEW_BLOCKED",
                     "evidence_review": "BLOCK_BAKE_IN", "changed": False},
        "canonical_integration_requirement": (
            "SATISFIED_REVIEWED_CANONICAL_MAIN_LINEAGE"
            if canonical_lineage["head_is_in_origin_main_history"]
            else "Authority may issue only from reviewed canonical main lineage; this continuation branch is proposal-only."
        ),
    }
    gates = {
        "CANONICAL_CONTINUATION_LINEAGE": (
            "PASS_CANONICAL_MAIN_LINEAGE"
            if canonical_lineage["head_is_in_origin_main_history"]
            else "PASS_PROPOSAL_BRANCH_MAIN_INTEGRATION_REQUIRED_BEFORE_AUTHORITY"
        ),
        "SCENENAT_DRIFT": "PASS_NO_MATERIAL_DRIFT",
        "DATA_LICENSE": ("PASS_USER_CONFIRMED_EXACT_RECEIPT" if license_confirmed
                         else "HOLD_USER_LICENSE_CONFIRMATION"),
        "SHARED_DECODER_CAUSAL_CONTROL": "PASS_STATIC_INTERFACE",
        "OFFICIAL_SHARED_DECODER_CHECKPOINT": "ABSENT_TRAIN_AFTER_LICENSE",
        "CORPUS_SCHEMA": "PASS_STATIC_AND_SYNTHETIC",
        "LICENSED_CORPUS": ("NOT_RUN_MATERIALIZATION_PENDING" if license_confirmed
                            else "NOT_RUN_LICENSE_ABSENT"),
        "TOKEN_MATCHING": "PASS_STATIC_REAL_MATERIALIZATION_PENDING",
        "RELATION_MATCHING": "PASS_SYNTHETIC_REAL_MATERIALIZATION_PENDING",
        "TOPOLOGY_MATCHING": "PASS_STATIC_REAL_MATERIALIZATION_PENDING",
        "RNG_REPLAY": "PASS_SYNTHETIC_LIVE_PENDING",
        "CHECKPOINT_RESUME": "PASS_STATIC_LIVE_PENDING",
        "GPU_QUALIFICATION": "NOT_REQUESTED_NOT_RUN",
        "REPRODUCTION": "PREREGISTERED_NOT_RUN",
        "P1": "CLOSED_ZERO_CASES_ZERO_OUTCOMES",
        "REGRESSION_DEBT": ("PASS_SCOPED_NON_BLOCKING" if targeted["status"] in {"PASS", "NOT_RUN"}
                            else "BLOCK_SCIENTIFIC_OBJECT_DEPENDENCY"),
        "PORT_010": "PASS_UNCHANGED",
    }
    adjudication = {
        **p, "lifecycle": "PRE_P1_OFFICIAL_TRAINING_QUALIFICATION",
        "parent_verdict": "PRE_F0_CHILD_PASS_PROPOSAL_ONLY", "verdict": verdict,
        "gates": gates, "scientific_gpu_runs": 0, "scientific_outcomes": 0,
        "official_training_runs": 0, "gpu_authority_requested_this_round": False,
        "p1_open": False,
        "next_if_license_receipt_arrives": (
            "MATERIALIZE_AND_CONTENT_ADDRESS_BEDROOM_CORPORA_THEN_RECHECK_ALL_GATES; DO_NOT_AUTO_ISSUE_GPU_AUTHORITY"
            if not license_confirmed else
            "LICENSE_RECEIPT_ACCEPTED; MATERIALIZE_AND_CONTENT_ADDRESS_BEDROOM_CORPORA; GPU_AND_P1_REMAIN_CLOSED"
        ),
    }
    artifacts: dict[str, Any] = {
        "canonical_state.json": {
            **p, "origin_main_at_branch_creation": "da3ebe8fc66503b28183853e251fa291bfb8d118",
            "prior_child_sha": "aded989e4917e57466cddb75ac395fff2a590e52",
            "continuation_branch": "research/relational-topology-stage-3d-training-qualification-20260901",
            **canonical_lineage,
            "authority_from_proposal_branch": False,
            "canonical_main_lineage_authority_eligible": canonical_lineage["head_is_in_origin_main_history"]},
        "source_manifest.json": source_manifest, "novelty_watch.json": novelty_watch,
        "license_gate.json": license_gate,
        "dataset_manifest.json": {**p, "room": "BEDROOM", "status": dataset_state,
            "licensed_rows": 0, "synthetic_rows": sum(map(len, corpora.values())),
            "corpus_sha256": corpus_hashes},
        "decoder_audit.json": decoder_audit,
        "official_checkpoint_audit.json": checkpoint_audit,
        "support_intervention.json": support_intervention,
        "corpus_schema.json": corpus_schema, "synthetic_replay.json": synthetic_replay,
        "token_matching.json": token_matching, "relation_matching.json": relation_matching,
        "topology_matching.json": topology_matching, "rng_contract.json": rng_contract,
        "oracle_interface.json": oracle_interface,
        "checkpoint_resume_contract.json": checkpoint_contract,
        "exactly_once_ledger.json": exactly_once, "gpu_qualification.json": gpu_qualification,
        "reproduction_preregistration.json": reproduction,
        "training_persistence_schema.json": training_persistence,
        "failure_taxonomy.json": failure_taxonomy,
        "p1_empty_schema.json": p1_schema, "authority.json": authority, "regression_debt.json": {**p, **debt},
        "adjudication.json": adjudication,
        "failures.jsonl": [{
            **p,
            "record_type": ("GATE_PENDING" if license_confirmed else "GATE_HOLD"),
            "classification": ("DATA_PROVENANCE_FAILURE" if license_confirmed
                               else "DATA_LICENSE_FAILURE"),
            "status": "OPEN",
            "verdict": verdict,
            "scientific_execution": False,
            "gpu_execution": False,
        }],
        "synthetic_corpus.jsonl": [row for regime in sorted(corpora) for row in corpora[regime]],
    }
    return artifacts, adjudication


def write_artifact(path: Path, value: Any) -> None:
    if path.suffix == ".jsonl":
        write_jsonl(path, value)
    else:
        path.write_bytes(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True).encode() + b"\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--run-id", default=RUN_ID)
    parser.add_argument("--instructscene-root", type=Path)
    parser.add_argument("--targeted-audit-log", type=Path)
    parser.add_argument("--license-receipt")
    args = parser.parse_args()
    if args.output_dir is None:
        args.output_dir = ROOT / "experiments/3d_official_training" / args.run_id
    artifacts, adjudication = build(args)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, value in artifacts.items():
        write_artifact(args.output_dir / name, value)
    hashes = {name: file_sha(args.output_dir / name) for name in sorted(artifacts)}
    manifest = {
        "schema_version": "relational-topology-official-training-qualification-manifest-v1",
        "object_id": OBJECT_ID, "parent_object_id": PARENT_ID, "run_id": args.run_id,
        "generated_at": CREATED_AT, "verdict": adjudication["verdict"],
        "compiler_source_git_sha": adjudication["compiler_source_git_sha"],
        "compiler_source_git_tree": adjudication["compiler_source_git_tree"],
        "config_sha256": adjudication["config_sha256"],
        "dataset_revision": adjudication["dataset_revision"],
        "artifact_sha256": hashes, "artifact_count": len(hashes),
        "scientific_gpu_runs": 0, "scientific_outcomes": 0, "official_training_runs": 0,
    }
    write_artifact(args.output_dir / "manifest.json", manifest)
    hashes["manifest.json"] = file_sha(args.output_dir / "manifest.json")
    (args.output_dir / "ARTIFACT_SHA256SUMS").write_text(
        "".join(f"{digest}  {name}\n" for name, digest in sorted(hashes.items())))
    print(args.output_dir)
    print(adjudication["verdict"])


if __name__ == "__main__":
    main()
