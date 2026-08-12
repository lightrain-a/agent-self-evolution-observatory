from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .paper_first_idea_incubation import CANDIDATES
from .paper_first_p0_promotions import AUTHORITY, PROMOTIONS
from .principle_adjudication import COMMON_FAILURE_UPDATE_RULES, COMMON_FALSIFICATION_REQUIRES

ROOT = Path(__file__).resolve().parent
CONFIG_NAMES = {
    "future-learnability-preserving-self-evolution": "p0_pf1_future_learnability_config.json",
    "cross-surface-repair-routing": "p0_pf2_cross_surface_config.json",
    "diagnosability-preserving-self-evolution": "p0_pf4_diagnosability_config.json",
    "failure-mode-transport-under-self-evolution": "p0_pf6_failure_transport_config.json",
}

INCUBATION_BY_ID = {str(row["id"]): row for row in CANDIDATES}

COMMON_PROTOCOL = {
    "applies_to_persistent_update": True,
    "post_update_effect_realization": {"passed": True, "evidence": "Any future authorized local validation must verify recurrence of the full post-update policy decision context and actual realization of the intended intervention before downstream task failure is interpreted as method evidence; observation-only recurrence is insufficient."},
    "hidden_evaluation_sealed": {"passed": True, "evidence": "Local validation freezes task/fault splits before metric inspection; held-out cases are never used to construct candidate repairs or thresholds."},
    "evaluation_artifacts_inaccessible": {"passed": True, "evidence": "Environment success labels and held-out fault ownership are withheld from the policy/update generator; only the independent analyzer sees them."},
    "independent_truth_source": {"passed": True, "evidence": "ALFWorld environment execution and preregistered controlled-fault labels define truth; the evolving agent never grades itself."},
    "same_information_baselines": {"passed": True, "evidence": "Matched baselines receive identical tasks, candidate updates/fault traces, calls, held-out budget, and observable features."},
    "claim_metric_alignment": {"passed": True, "evidence": "Primary metrics directly instantiate the registered paper claim and are frozen before local validation."},
    "versioned_evaluator": {"passed": True, "evidence": "Config hash, source commit, task split, parser, failure taxonomy, and analysis code are versioned in each run manifest."},
    "shortcut_audit": {"passed": True, "evidence": "Hidden answer/benchmark lookup, fault metadata leakage to the router, post-hoc split changes, and cached hidden outcomes are forbidden."},
}

RECOVERY = {
    "incremental_trace": True,
    "atomic_progress": True,
    "heartbeat_state": True,
    "online_budget_watchdog": True,
    "per_run_lock": True,
    "gpu_uuid_binding": True,
    "restart_policy": "Preserve completed atomic rows and restart only incomplete rows under the identical config/source/runtime hash.",
    "partial_artifact_policy": "Partial rows remain diagnostic only and cannot register a scientific method result.",
}

OUTCOMES = {
    "allowed": ["METHOD-PASS", "METHOD-FAIL", "INCONCLUSIVE", "BASELINE-FLOOR", "BASELINE-CEILING", "RUNTIME-ERROR", "IMPLEMENTATION-ERROR", "BUDGET-STOP"],
    "budget_stop_registers_scientific_result": False,
    "floor_or_ceiling_counts_as_method_fail": False,
}

THROUGHPUT = {
    "measurement_id": "qwen25-react-family-id24-server60-20260810",
    "reference": "Qwen2.5-7B-Instruct react-family on server60 RTX3090, 24 ALFWorld episodes",
    "calibration_episodes": 24,
    "calibration_model_calls": 969,
    "calibration_gpu_hours": 0.22905,
    "calls_per_gpu_hour": 4230.5,
    "mean_steps_per_episode": 40.375,
}


def _paper_design(idea_id: str, spec: dict[str, Any]) -> dict[str, Any]:
    inc = INCUBATION_BY_ID[str(spec["incubation_id"])]
    nearest = [
        {"identity": str(row["title"]), "difference": str(spec["novelty_boundary"]), "source_ref": str(row["ref"])}
        for row in inc.get("nearest_work") or []
    ]
    components = {
        "future-learnability-preserving-self-evolution": ["matched-current/retention filter", "sealed second-stage adaptation probe", "future-learnability commit gate"],
        "cross-surface-repair-routing": ["declared repair-surface registry", "matched causal intervention table", "minimum-sufficient surface selector"],
        "diagnosability-preserving-self-evolution": ["sealed diagnostic probes", "frozen external cause observer", "diagnosability-preserving commit constraint"],
        "failure-mode-transport-under-self-evolution": ["preregistered failure taxonomy", "paired before/after transport matrix", "transport-risk commit rule"],
    }[idea_id]
    claim = {
        "future-learnability-preserving-self-evolution": "Future learnability can vary across persistent updates even after matching current utility and old-task retention.",
        "cross-surface-repair-routing": "Repair ownership is heterogeneous across persistent agent update surfaces and can be identified from causal intervention outcomes.",
        "diagnosability-preserving-self-evolution": "Updates with similar utility can differ in how well future failures remain externally diagnosable.",
        "failure-mode-transport-under-self-evolution": "Paired failure-mode transport contains decision-relevant information not captured by aggregate success or static failure risk.",
    }[idea_id]
    metric = {
        "future-learnability-preserving-self-evolution": "future-adaptation AUC / improvement-per-example at matched current+retention",
        "cross-surface-repair-routing": "held-out correct-surface selection + repair benefit - collateral regression at matched cost",
        "diagnosability-preserving-self-evolution": "held-out frozen-observer fault localization accuracy/AUROC at matched utility",
        "failure-mode-transport-under-self-evolution": "paired failure transport matrix + preregistered risk delta",
    }[idea_id]
    return {
        "novelty": {
            "paper_problem": spec["paper_problem"],
            "closest_work": nearest,
            "novelty_axis": "mechanism-and-problem-formulation",
            "contribution_claim": claim,
            "irreducible_difference": spec["novelty_boundary"],
            "collision_status": "2026-08-12 paper-first premortem ADVANCE; exact boundary frozen before implementation",
        },
        "method": {
            "method_name": spec["title"]["en"],
            "core_mechanism": spec["mechanism"],
            "novelty_to_method_mapping": [{"novelty": spec["novelty_boundary"], "component": components[-1]}],
            "components": components,
            "strongest_simplification": spec["baseline"],
            "method_change_rule": "Changing the causal quantity, update surface set, primary metric, or commit rule is a core-method change and returns to Paper Novelty/Method review.",
        },
        "experiment_blueprint": {
            "claim_experiment_matrix": [{"claim_id": "C1", "claim": claim, "local_test": spec["minimum_p0"], "full_test": "Frozen multi-seed / second-backbone / natural-failure evidence matrix after Method Freeze", "metric": metric, "strongest_baseline": spec["baseline"]}],
            "local_validation_scope": spec["minimum_p0"],
            "full_experiment_scope": "Only after local validation and Method Freeze: >=3 seeds, second open backbone, stronger natural-failure/task-family coverage, full baseline/ablation/efficiency matrix.",
            "baseline_matrix": [spec["baseline"], "constant/majority or best-fixed policy", "shallow same-feature baseline where applicable"],
            "ablation_matrix": [f"remove {components[-1]}", "replace outcome-derived quantity with direct aggregate utility"],
            "freeze_rule": "Freeze method hash, split hash, metric/taxonomy, prompt/tool policy, and experiment-blueprint hash before any full experiment.",
            "experimental_integrity": {
                "model_and_inference": "Qwen2.5-7B-Instruct, deterministic decoding, react-family ALFWorld scaffold, max_steps=50; model/checkpoint frozen per run.",
                "prompt_tool_policy": "Prompt patches, injected faults, tool/workflow wrappers, and allowed repair surfaces are versioned; hidden labels are never placed in prompts.",
                "task_sample_split": "Discovery/development and sealed held-out task files are frozen before result inspection; no task moves after launch.",
                "metric_analysis_plan": f"Primary metric: {metric}; report per-unit/family outcomes before macro aggregation and compare strongest same-information baselines.",
                "randomness_replication_plan": "Local P0 uses seed 42 deterministic generation; threshold-near cases may repeat <=3 times only under the frozen rule. Full experiments require >=3 seeds.",
                "stopping_exclusion_rules": "Runtime/implementation invalid rows are excluded with explicit typed status; no performance-based row exclusion. Budget stop cannot register a method result.",
                "allowed_adaptations": "Only execution/runtime repair that leaves the frozen method, tasks, metrics, baselines, and analysis unchanged; core changes require a new Paper Design Contract.",
                "hidden_evaluation_access_policy": "No web search, benchmark solution lookup, hidden-label inspection, or evaluator introspection during execution; search trajectory is disabled for local P0.",
            },
        },
    }


def _principle(idea_id: str, spec: dict[str, Any]) -> dict[str, Any]:
    pid = f"{idea_id}-principle-v1"
    phenomenon = {
        "future-learnability-preserving-self-evolution": "At least some candidate updates matched on current utility/retention produce nonzero future-adaptation differences.",
        "cross-surface-repair-routing": "Different failures have different minimum sufficient persistent repair surfaces under matched interventions.",
        "diagnosability-preserving-self-evolution": "Candidate updates can change external fault-cause separability independently of task utility.",
        "failure-mode-transport-under-self-evolution": "Persistent updates induce nontrivial paired transitions among preregistered failure modes.",
    }[idea_id]
    mechanism_pred = {
        "future-learnability-preserving-self-evolution": "A future-learnability probe improves commit decisions beyond current-gain/retention-only gating on held-out future adaptation.",
        "cross-surface-repair-routing": "Outcome-based minimum-surface routing beats the strongest fixed/simple selector at matched information and cost.",
        "diagnosability-preserving-self-evolution": "A diagnosability constraint rejects updates that preserve/improve utility but cause measurable future diagnosis degradation, and the degradation predicts repair difficulty.",
        "failure-mode-transport-under-self-evolution": "Transport-aware decisions differ from aggregate-success/static-risk decisions on held-out updates and better avoid preregistered high-risk substitutions.",
    }[idea_id]
    return {
        "principle_id": pid,
        "primitives": ["persistent agent update", "paired held-out intervention", "independent environment truth", "matched baseline"],
        "scope_conditions": ["base policy is competent but imperfect", "candidate updates/fault probes induce nontrivial variation", "held-out truth is independent of update construction"],
        "assumptions": [
            {"id": "A-VAR", "statement": "The local substrate contains enough effect variation to identify the registered quantity.", "observable_check": "F0 support counts and target/effect variation."},
            {"id": "A-IND", "statement": "Environment/fault truth is independent of the method decision rule.", "observable_check": "sealed task/fault labels and same-information baseline audit."},
        ],
        "mechanism": spec["principle"],
        "predictions": [
            {"id": "P0-PHENOMENON", "statement": phenomenon, "observable": spec["economy"]["effect_observable"], "role": "phenomenon-prerequisite"},
            {"id": "P1-MECHANISM", "statement": mechanism_pred, "observable": "held-out method-vs-matched-baseline decision/effect difference", "role": "mechanism-test"},
        ],
        "operationalization": [
            {"concept": "registered causal quantity", "measure": spec["economy"]["effect_observable"], "validity_check": spec["minimum_p0"]},
            {"concept": "method headroom", "measure": "same-information disagreement plus held-out outcome difference", "validity_check": f"compare against {spec['baseline']}"},
        ],
        "falsification": {"prediction_ids": ["P1-MECHANISM"], "requires": list(COMMON_FALSIFICATION_REQUIRES), "contradiction_rule": spec["stop"]},
        "failure_update_rules": dict(COMMON_FAILURE_UPDATE_RULES),
    }


def build_config(idea_id: str, authority: dict[str, Any] | None = None) -> dict[str, Any]:
    authority = authority or AUTHORITY
    spec = PROMOTIONS[idea_id]
    mode, substrate, units = spec["setup"]
    expected = 48 if idea_id == "future-learnability-preserving-self-evolution" else 36
    worst = 72 if idea_id == "future-learnability-preserving-self-evolution" else 72
    primary_metric = spec["economy"]["effect_observable"]
    f0_result = "runs/paper-first-p0-20260812/future-learnability/result.json" if idea_id == "future-learnability-preserving-self-evolution" else "runs/paper-first-p0-20260812/shared-surface/result.json"
    return {
        "schema_version": "2.3",
        "idea_id": idea_id,
        "phase": "P0",
        "human_authority": {"authority_status": authority.get("authority_status"), "artifact_sha256": authority.get("artifact_sha256"), "source_message_sha256": authority.get("source_message_sha256"), "p0_lifecycle_authorized": authority.get("promotion_authorized") is True, "local_validation_authorized": authority.get("local_validation_authorized") is True},
        "historical_unauthorized_f0_reuse_forbidden": True,
        "governance": {"schema_version": "2.2", "scientific_stage": "p0-support", "substrate_id": substrate},
        "models": ["Qwen2.5-7B-Instruct"],
        "datasets": ["ALFWorld"],
        "seeds": [42],
        "scope": {"policy_mode": "react-family", "max_steps": 50, "expected_environment_episodes": expected, "worst_case_environment_episodes": worst, "expected_extra_model_calls": 32 if idea_id == "future-learnability-preserving-self-evolution" else 0, "screening_units": units},
        "analysis": {"primary_metric": primary_metric, "bootstrap_confidence": 0.95, "screening_only": False},
        "resource_cap": {"max_gpus": 1, "gpu_hours": 1.25, "wall_hours": 3, "episodes": worst},
        "pre_experiment": {
            "paper_design": _paper_design(idea_id, spec),
            "principle_certificate": _principle(idea_id, spec),
            "protocol_validity": dict(COMMON_PROTOCOL),
            "updater_competence": {"required": True, "is_formal_gate": False, "passed": False, "status": "pending-local-f0", "surface": mode, "evidence": {"artifact": f0_result}, "reason": "Local F0 must establish nontrivial support/variation before method interpretation.", "scientific_role": "hard prerequisite before Gate 1; failure blocks this local realization without rejecting the paper problem"},
            "parameter_provenance": {
                "critical_parameters": ["scope.max_steps", "scope.expected_environment_episodes", "resource_cap.gpu_hours", "analysis.primary_metric"],
                "entries": [
                    {"parameter": "scope.max_steps", "value": 50, "source_type": "literature", "basis": "ALFWorld/ReAct-style text-agent evaluation uses a 50-step horizon; do not shorten the task for convenience."},
                    {"parameter": "scope.expected_environment_episodes", "value": expected, "source_type": "statistical-calculation", "basis": "Local F0 balances >=3 fault/task families with held-out units while keeping the test below 20% of a paper-scale experiment."},
                    {"parameter": "resource_cap.gpu_hours", "value": 1.25, "source_type": "measured-throughput", "basis": "Server60 measured throughput is 4230.5 model calls/GPUh; cap covers the frozen worst-case call graph plus margin."},
                    {"parameter": "analysis.primary_metric", "value": primary_metric, "source_type": "explicit-protocol-choice", "basis": "The metric is the direct observable registered by the Principle Certificate and Paper Claim C1."},
                ],
            },
            "competence": {"evidence_id": "qwen25-react-family-ood134", "model_name": "Qwen2.5-7B-Instruct", "policy_mode": "react-family", "minimum_success_rate": 0.30, "maximum_success_rate": 0.90, "minimum_task_types_with_success": 5},
            "identifiability": {"synthetic_true_false_separation": True, "true_false_question": spec["minimum_p0"]},
            "statistics": {},
            "compute": {"minimum_gpu_hour_margin": 1.10},
            "throughput": dict(THROUGHPUT),
            "recovery": dict(RECOVERY),
            "outcomes": dict(OUTCOMES),
        },
    }


def write_configs(root: Path = ROOT, *, preserve_evolved: bool = True, authority: dict[str, Any] | None = None) -> dict[str, str]:
    authority = authority or AUTHORITY
    out: dict[str, str] = {}
    for idea_id, name in CONFIG_NAMES.items():
        path = root / name
        if preserve_evolved and path.exists():
            try:
                existing = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                existing = {}
            status = str((((existing.get("pre_experiment") or {}).get("updater_competence") or {}).get("status") or ""))
            existing_authority = existing.get("human_authority") or {}
            same_authority = bool(authority.get("promotion_authorized") is True and authority.get("local_validation_authorized") is True and authority.get("artifact_sha256") and existing_authority.get("artifact_sha256") == authority.get("artifact_sha256"))
            if status and status != "pending-local-f0" and same_authority:
                out[idea_id] = str(path)
                continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(build_config(idea_id, authority), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        out[idea_id] = str(path)
    return out


if __name__ == "__main__":
    print(json.dumps(write_configs(), ensure_ascii=False, indent=2))
