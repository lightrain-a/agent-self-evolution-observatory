from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT, StorageSettings, resolve_experiment_data_root
from .paper_design_contract import audit_paper_design_contract

DEFAULT_JSON = PROJECT_ROOT / "generated" / "memento-joint-identifiability-paper-design.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "memento-joint-identifiability-paper-design.js"
CANDIDATE_ID = "MEMENTO-JOINT-BOUNDARY-CONTROL"
OFFICIAL_REVISION = "85cdc513961b3792f6430c8ad90d671cd5caf09a"
FROZEN_IDS = [str(10000 + i) for i in range(12)]
EXPECTED_SHA = {
    "problem_gate": "13b0d91eaf0edfd02b7e44815d8daf4849b8a4f7c5f0c63839fd43863e4ce567",
    "review": "0a3d85ee57350c630c1aa7a83f375405a5dac899a75bb439e2a2240e14ed23e9",
    "substrate": "48c63a15397f545d16aae1bde7ea0f8fb613a620173d23f5e1956334a648e019",
    "acquisition": "bad6ebf4ba1d654b6ae90264b41f4916818c81582f53c76e79eeb17c3a460235",
    "single": "c2b594fbe9d03f37d6f08876d688cd9e96590c9e9b135881f306192dda171757",
    "joint": "252c8b7d37f08264fe947732c181c98c341a8fa516f48233225a767af3d2a34f",
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _stable(x: Any) -> str:
    return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash(x: Any) -> str:
    return hashlib.sha256(_stable(x).encode()).hexdigest()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _paths(root: Path) -> dict[str, Path]:
    runs = root / "runs"
    ds = root / "cache/substrates/MEMENTO-official/resource/datasets"
    return {
        "problem_gate": runs / "memento-joint-live-gate-20260822T120002Z/public-live-gate.json",
        "review": runs / "memento-joint-id-review-v2-20260822T112204Z/public-review.json",
        "substrate": runs / "b3-memento-substrate-f6a59bec9fd9/substrate-receipt.json",
        "acquisition": ds / "memory_acquisition_stage.json",
        "single": ds / "single_memory_utilization_stage.json",
        "joint": ds / "joint_memory_utilization_stage.json",
    }


def source_integrity(root: Path) -> dict[str, Any]:
    rows = {}
    for key, path in _paths(root).items():
        actual = _sha(path) if path.is_file() else ""
        rows[key] = {"path": str(path), "expected_sha256": EXPECTED_SHA[key], "actual_sha256": actual, "match": actual == EXPECTED_SHA[key]}
    ok = all(r["match"] for r in rows.values())
    return {"passed": ok, "status": "PASS_PINNED_SOURCES" if ok else "HOLD_SOURCE_DRIFT", "sources": rows}


def _quality() -> dict[str, Any]:
    claim = "C1"
    return {
        "schema_version": "2.1", "paper_archetype": "empirical_analysis",
        "claims": [{
            "id": claim, "claim_type": "empirical_analysis",
            "statement": "A practically meaningful share of MEMENTO joint-memory degradation is ordinary same-scene task-composition cost rather than memory coordination.",
            "why_better_or_why_matters": "The published acquisition-average reference changes task composition together with memory count; a same-composed-goal explicit control is needed before calling the full joint drop a coordination cost.",
            "alternative_explanations": ["longer composed execution", "instruction-length effect", "released-result QC filtering", "runtime/model-version drift"],
            "baseline_ids": ["B-PUBLISHED", "B-EXPLICIT", "B-METADATA"], "ablation_ids": [],
            "analysis_ids": ["A-UNCERTAINTY", "A-FAILURE", "A-SENSITIVITY", "A-ALT", "A-STRATA"],
            "output_ids": ["O-MAIN", "O-DECOMP", "O-FAIL", "O-SENS"],
            "visualization_ids": ["V-MAIN", "V-DECOMP", "V-FAIL", "V-SENS"],
        }],
        "baselines": [
            {"id": "B-PUBLISHED", "role": "current_system", "evidence_type": "empirical", "target_claim_ids": [claim], "purpose": "Reproduce the published joint-versus-parent-average attribution surface.", "matched_dimensions": ["MEMENTO scene", "joint unit", "planner family", "metric"]},
            {"id": "B-EXPLICIT", "role": "simple_control", "evidence_type": "empirical", "target_claim_ids": [claim], "purpose": "Measure ordinary composition cost with the same scene and composed goals while resolving both personalized references explicitly.", "matched_dimensions": ["scene", "two subgoals", "target objects", "goal order", "planner/runtime", "metric"]},
            {"id": "B-METADATA", "role": "analytical_simplification", "evidence_type": "analytical", "target_claim_ids": [claim], "purpose": "Use released goal/object/scene metadata as the strongest no-new-control generic task-complexity explanation."},
        ],
        "ablations": [],
        "analyses": [
            {"id": "A-UNCERTAINTY", "analysis_type": "uncertainty", "target_claim_ids": [claim], "purpose": "Quantify paired uncertainty over the frozen 12 units.", "decision_rule": "Apply the registered bootstrap95 gate at -0.05 PC; point estimates cannot advance."},
            {"id": "A-FAILURE", "analysis_type": "failure", "target_claim_ids": [claim], "purpose": "Expose all frozen units, including four absent from the released complete-condition intersection.", "decision_rule": "Missing/invalid/censored units stay visible and cannot be replaced."},
            {"id": "A-SENSITIVITY", "analysis_type": "sensitivity", "target_claim_ids": [claim], "purpose": "Check leave-one-unit/scene-out stability and secondary SR.", "decision_rule": "Sensitivity may narrow the claim but never move the registered PC threshold."},
            {"id": "A-ALT", "analysis_type": "alternative_explanation", "target_claim_ids": [claim], "purpose": "Separate composition, instruction-length, QC, and runtime-drift explanations.", "decision_rule": "Any unmatched runtime/model difference blocks a coordination interpretation."},
            {"id": "A-STRATA", "analysis_type": "stratified", "target_claim_ids": [claim], "purpose": "Describe effects by memory-subtype pair without tuning strata.", "decision_rule": "Subtype patterns are descriptive only before replication."},
        ],
        "planned_outputs": [
            {"id": "O-MAIN", "output_type": "main_comparison", "purpose": "Frozen paired headroom table."},
            {"id": "O-DECOMP", "output_type": "mechanism", "purpose": "Composition-versus-residual attribution after Stage-1 GO."},
            {"id": "O-FAIL", "output_type": "failure", "purpose": "Unit-level failures/censoring/QC-missing cases."},
            {"id": "O-SENS", "output_type": "sensitivity", "purpose": "Leave-one-out and PC-versus-SR checks."},
        ],
        "visualizations": [
            {"id": "V-MAIN", "placement": "main", "visual_type": "multi_panel", "panel_roles": ["main_comparison", "uncertainty"], "target_claim_ids": [claim], "source_evidence_ids": ["B-PUBLISHED", "B-EXPLICIT", "A-UNCERTAINTY", "O-MAIN"], "reviewer_question": "Does composition cost exceed the frozen five-point PC margin?", "takeaway": "Show the paired effect and bootstrap95 before any coordination residual.", "quantitative": True, "uncertainty_required": True, "negative_or_failure_visible": False},
            {"id": "V-DECOMP", "placement": "main", "visual_type": "flow", "panel_roles": ["mechanism"], "target_claim_ids": [claim], "source_evidence_ids": ["B-PUBLISHED", "B-EXPLICIT", "A-ALT", "O-DECOMP"], "reviewer_question": "How much published joint drop remains after composition matching?", "takeaway": "Separate composition from residual memory-specific burden without estimator novelty.", "quantitative": True, "uncertainty_required": False, "negative_or_failure_visible": False},
            {"id": "V-FAIL", "placement": "main", "visual_type": "distribution", "panel_roles": ["failure"], "target_claim_ids": [claim], "source_evidence_ids": ["A-FAILURE", "O-FAIL"], "reviewer_question": "Are failures or release filtering hidden?", "takeaway": "Keep every frozen unit visible.", "quantitative": True, "uncertainty_required": False, "negative_or_failure_visible": True},
            {"id": "V-SENS", "placement": "main", "visual_type": "line", "panel_roles": ["sensitivity"], "target_claim_ids": [claim], "source_evidence_ids": ["A-SENSITIVITY", "A-STRATA", "O-SENS"], "reviewer_question": "Is attribution stable to registered sensitivity checks?", "takeaway": "Show sensitivity without moving the threshold.", "quantitative": True, "uncertainty_required": False, "negative_or_failure_visible": False},
        ],
    }


def paper_design_config() -> dict[str, Any]:
    return {
        "schema_version": "2.3",
        "pre_experiment": {"paper_design": {
            "novelty": {
                "paper_problem": "MEMENTO joint-memory changes both memory coordination and task composition. Without a same-scene, same-composed-goal, fully specified joint control, the published joint degradation does not identify ordinary task-composition cost versus memory-specific coordination cost.",
                "closest_work": [{"identity": "MEMENTO: Embodied Agents Meet Personalization", "difference": "MEMENTO exposes acquisition, single-memory and joint-memory conditions and a no-memory joint condition, but the audited paper/code/results expose no paired same-scene same-composed-goal fully specified joint control; its no-memory joint instruction remains personalized and underspecified.", "source_ref": "arXiv:2505.16348"}],
                "novelty_axis": "benchmark identifiability and empirical attribution correction",
                "contribution_claim": "Audit whether MEMENTO's joint-memory coordination attribution survives a missing composition-matched control; no new estimator, memory model, or interaction mechanism is claimed.",
                "irreducible_difference": "Published conditions cannot reveal the MEMENTO-specific composition term. The new observation Y_joint_explicit holds scene and the composed two-goal task fixed while resolving both personalized references explicitly.",
                "collision_status": "ProblemGate CLEAR with SOFT_COLLISION to generic partial identification; independent review rates paperability MEDIUM and makes empirical headroom decisive.",
            },
            "method": {
                "method_name": "Composition-Controlled Joint-Memory Audit",
                "core_mechanism": "For each frozen unit, rerun two fully specified parent acquisition tasks and one fully specified composition of the same goals in the same scene, then measure the paired composition penalty before interpreting joint-memory loss.",
                "novelty_to_method_mapping": [{"novelty": "missing composition-matched observation", "component": "same-scene same-composed-goal fully specified joint control"}],
                "components": ["fully specified composed-goal control", "paired composition-versus-residual decomposition"],
                "strongest_simplification": "Generic task-complexity/goal-count prediction plus every released score and task metadata; it can predict a direction but cannot quantify the missing MEMENTO-specific composition term without the new control.",
                "method_change_rule": "Changing frozen units, control construction, PC definition, paired bootstrap procedure, or the -0.05 PC margin invalidates Stage 1 and returns to Paper Design review.",
            },
            "evidence_quality": _quality(),
            "experiment_blueprint": {
                "claim_experiment_matrix": [{
                    "claim_id": "C1", "claim": "A material portion of the MEMENTO joint drop is ordinary composition cost, so the unadjusted drop is not itself a coordination estimate.",
                    "local_test": "Exactly 36 no-memory episodes: for each frozen joint ID 10000-10011, rerun both fully specified acquisition parents plus one fully specified composed joint task.",
                    "full_test": "Only after Stage-1 GO, combine or rerun matched acquisition, single-memory, fully specified joint and joint-memory conditions to report a composition-adjusted residual coordination cost.",
                    "metric": "Primary PC: C_u = Y_joint_explicit - mean(Y_acq_i,Y_acq_j), paired bootstrap95 over 12 units; SR is secondary descriptive evidence.",
                    "strongest_baseline": "Published acquisition-average attribution plus metadata-only generic task complexity, neither of which observes Y_joint_explicit.",
                }],
                "local_validation_scope": "12 outcome-blind frozen joint units (10000-10011), 36 no-memory episodes, exact official MEMENTO scene/task definitions; the four units missing from the released complete-condition intersection cannot be dropped.",
                "full_experiment_scope": "Conditional on Stage-1 GO only: estimate composition-adjusted coordination residual across the official MEMENTO planner/backbone family while preserving unit and control rules.",
                "baseline_matrix": ["published acquisition-average reference", "same-scene same-composed-goal fully specified control", "metadata-only task-complexity explanation"],
                "ablation_matrix": ["remove composition matching and recover the published attribution", "PC primary versus SR secondary without changing the PC gate"],
                "freeze_rule": "Unit IDs, source revision/hashes, explicit-control constructor, 36-episode scope, PC estimator, bootstrap procedure and -0.05 margin are immutable; implementation fixes may restore runtime fidelity only.",
                "experimental_integrity": {
                    "model_and_inference": "Use the exact official MEMENTO planner/runtime configuration for the audited backbone. The primary script names gpt-4o; never silently substitute a newer provider model, open-weight proxy, or different planner. If exact inference identity is unavailable, hold execution.",
                    "prompt_tool_policy": "Keep official planner prompt, tools, parser, step policy and environment fixed. Only resolve the two personalized references in the composed instruction from frozen acquisition-parent text.",
                    "task_sample_split": "Outcome-blind frozen joint IDs 10000-10011, each tied to its two official acquisition parents and same scene; all 12 remain in analysis.",
                    "metric_analysis_plan": "C_u = PC_joint_explicit - mean(PC_acq_i,PC_acq_j). GO iff upper bootstrap95(mean C_u) <= -0.05; STOP iff lower95 >= -0.05; otherwise HOLD. SR cannot override PC.",
                    "randomness_replication_plan": "Preserve official evaluation randomness controls; if stochastic, use the same registered seed/replication policy for all three arms and aggregate within unit before paired bootstrap.",
                    "stopping_exclusion_rules": "No outcome-driven exclusion, no replacing release-filtered units, no threshold tuning, and no full audit before GO. Runtime-invalid/censored episodes are support failures, not scientific negatives.",
                    "allowed_adaptations": "Only installation/runtime repairs that restore pinned MEMENTO fidelity; no scientific-object, unit, control, model, metric, threshold or prompt changes.",
                    "hidden_evaluation_access_policy": "Released historical outcomes may be context only; no hidden/full-audit joint-memory outcome may select units or tune the explicit control.",
                },
            },
        }},
    }


def f0_contract() -> dict[str, Any]:
    return {
        "stage": "F0_COMPOSITION_HEADROOM", "frozen_joint_episode_ids": list(FROZEN_IDS),
        "units": 12, "arms_per_unit": 3, "episodes": 36,
        "arms": ["fully_specified_parent_i", "fully_specified_parent_j", "fully_specified_composed_joint"],
        "primary_metric": "task_percent_complete", "secondary_metric": "task_state_success",
        "unit_effect": "C_u = PC_joint_explicit - mean(PC_acq_i, PC_acq_j)", "decision_margin": -0.05,
        "uncertainty": "paired bootstrap95 over 12 frozen unit effects",
        "go": "upper_bootstrap95(mean_C_u) <= -0.05",
        "stop": "lower_bootstrap95(mean_C_u) >= -0.05",
        "hold": "lower_bootstrap95(mean_C_u) < -0.05 < upper_bootstrap95(mean_C_u)",
        "full_audit_unlock": "GO only",
        "selection_policy": "outcome-blind frozen 12; never shrink to the 8 released-complete rows",
        "failure_typing": "runtime/setup/censoring failures are execution-support failures, not C_u=0 evidence",
    }


def runtime_support() -> dict[str, Any]:
    return {
        "status": "HOLD_EXACT_MEMENTO_RUNTIME_ASSETS_MISSING", "checked_host": "root@10.42.8.52", "checked_at": "2026-08-22",
        "observed": {"docker_available": True, "free_gpu_indices_at_check": [3, 4, 6, 7], "exact_memento_image_present": False, "hssd_hab_assets_present": False, "partnr_episode_assets_present": False, "habitat_lab_checkout_present": False, "objects_ovmm_assets_present": False, "data_disk_free_approx_tb": 30},
        "required_official_stack": ["pinned MEMENTO code", "Habitat-Sim 0.3.3", "Habitat-Lab/PARTNR", "HSSD scenes", "PARTNR episodes", "OVMM objects", "audited exact planner/model"],
        "interpretation": "Compute capacity exists, but exact benchmark assets are not installed. This blocks execution only and is not scientific evidence.",
        "proxy_policy": "Do not replace MEMENTO with ALFWorld, text-only proxy, or a different backbone merely to get Stage-1 numbers.",
    }


def build_state(data_root: Path | None = None) -> dict[str, Any]:
    root = data_root or resolve_experiment_data_root(StorageSettings.from_env())
    integrity = source_integrity(root)
    config = paper_design_config()
    audit = audit_paper_design_contract(config)
    f0 = f0_contract()
    runtime = runtime_support()
    core = {"candidate_id": CANDIDATE_ID, "official_revision": OFFICIAL_REVISION, "source_sha256": EXPECTED_SHA, "paper_design": config["pre_experiment"]["paper_design"], "f0_contract": f0}
    contract_sha = _hash(core)
    ready = integrity["passed"] and audit["passed"]
    return {
        "schema_version": "1.0", "generated_at": _now(), "candidate_id": CANDIDATE_ID,
        "title": {"zh": "MEMENTO 多记忆协调成本是否被任务组合难度混淆？", "en": "Joint-Memory Degradation Is Not a Coordination Estimate: A Composition-Controlled Audit of Agent Memory Evaluation"},
        "status": "PAPER_DESIGN_FROZEN_EXACT_RUNTIME_SUPPORT_HOLD" if ready else "PAPER_DESIGN_REPAIR_REQUIRED",
        "paper_design_status": "FROZEN_FOR_HUMAN_REVIEW" if ready else "REPAIR_REQUIRED",
        "execution_status": runtime["status"], "problem_gate_status": "PROBLEM_GATE_PASS_AWAIT_HUMAN_PAPER_DESIGN",
        "paperability": "MEDIUM_EMPIRICAL_RESULT_DEPENDENT", "contract_sha256": contract_sha,
        "source_integrity": integrity, "paper_design_audit": audit, "paper_design": config["pre_experiment"]["paper_design"],
        "f0_contract": f0, "runtime_support": runtime,
        "plain_language": {
            "scene_zh": "MEMENTO 让 Agent 先记住两条个性化信息，再把两个原本分开的任务合成一个 joint task。论文看到 joint-memory 掉得更多，并把它解释为协调多条记忆很难。但 joint task 同时也变成了更长、更复杂的组合任务，所以我们先保持同一场景和同两个子任务，只把个性化指代直接说清楚；此时完全不需要 memory，测到的额外下降就是任务组合本身的成本。",
            "observed_zh": "已确认 36/36 joint unit 都能构造 fully-specified composed control；冻结 12 个 unit 覆盖 12 个 scene。官方 no-memory joint 对照仍使用隐式 personalized instruction，公开结果中没有暴露与 36 个 joint episode 一一配对的 same-composed-goal fully-specified control。新的 36-episode F0 尚未运行，因此目前没有 composition penalty 数值。",
            "simple_baseline_zh": "最简单的解释是‘两个任务一起做天然更难’：只看目标数、对象数、场景和已有分数就预测 joint 会掉，但它不能告诉我们 MEMENTO 里到底因为组合本身掉了多少。新控制只多做一件事：joint task 不变，但把两条个性化信息直接写进指令，让 memory coordination 因素消失。",
            "decision_zh": "只有 fully-specified joint 相对两个 parent 平均的 PC 损失，其 95% bootstrap 区间整体至少达到 5 个百分点，才继续完整 coordination audit；否则 STOP 或 HOLD。",
        },
        "prior_provider_support_failures": [
            {"run_id": "memento-joint-id-review-20260822T112017Z", "type": "provider_incomplete_length", "scientific_authority": False},
            {"run_id": "memento-joint-paper-design-20260822T113316Z", "type": "provider_incomplete_length", "scientific_authority": False},
            {"run_id": "memento-joint-paper-design-20260822T113522Z", "type": "empty_attempt_directory", "scientific_authority": False},
        ],
        "policy": {"deterministic_design_reuses_only_frozen_reviewed_evidence": True, "provider_retry_required": False, "numeric_gate_inherited_unchanged_from_problem_gate": True, "paper_design_is_not_execution_authority": True, "support_hold_is_not_scientific_failure": True, "proxy_substrate_forbidden": True, "full_audit_before_f0_go_forbidden": True},
        "authority": {"scientific": False, "method": False, "experiment_blueprint_execution": False, "local_validation": False, "p0": False, "gpu": False, "full_experiment": False},
    }


def write_state(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    state = build_state()
    json_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_core = {
        "schema_version": "1.0", "candidate_id": CANDIDATE_ID, "contract_sha256": state["contract_sha256"],
        "status": state["status"], "source_sha256": EXPECTED_SHA,
        "paper_design_audit": {"passed": state["paper_design_audit"]["passed"], "status": state["paper_design_audit"]["status"], "blockers": state["paper_design_audit"]["blockers"]},
        "f0_decision_rule": {"margin": state["f0_contract"]["decision_margin"], "go": state["f0_contract"]["go"], "stop": state["f0_contract"]["stop"], "hold": state["f0_contract"]["hold"]},
        "runtime_support_status": state["runtime_support"]["status"], "authority": state["authority"], "scientific_authority": False,
    }
    receipt_sha = _hash(receipt_core)
    root = resolve_experiment_data_root(StorageSettings.from_env())
    receipt_path = root / "runs" / f"memento-joint-paper-design-frozen-{receipt_sha[:12]}" / "paper-design-receipt.json"
    payload = {**receipt_core, "receipt_sha256": receipt_sha}
    if receipt_path.exists():
        if json.loads(receipt_path.read_text(encoding="utf-8")) != payload:
            raise RuntimeError(f"append-only receipt mismatch: {receipt_path}")
    else:
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    state["receipt"] = {"path": str(receipt_path), "receipt_sha256": receipt_sha}
    json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.MEMENTO_JOINT_IDENTIFIABILITY_PAPER_DESIGN = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    print(json.dumps(write_state(), ensure_ascii=False, indent=2))
