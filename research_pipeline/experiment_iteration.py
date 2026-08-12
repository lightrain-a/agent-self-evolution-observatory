from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import StorageSettings


DIAGNOSIS_TAXONOMY: dict[str, dict[str, str]] = {
    "infrastructure-error": {
        "layer": "execution",
        "meaning": "The run did not test the scientific mechanism because the harness/runtime failed.",
    },
    "budget-plan-mismatch": {
        "layer": "execution",
        "meaning": "Actual execution exceeded the preregistered cost model or execution path.",
    },
    "substrate-degenerate": {
        "layer": "experiment",
        "meaning": "The base system is too easy, too hard, or otherwise lacks the variation required to test the mechanism.",
    },
    "no-label-variation": {
        "layer": "experiment",
        "meaning": "The target variable has insufficient variation, so no learner can identify the claimed decision boundary.",
    },
    "underfit": {
        "layer": "optimization",
        "meaning": "The learner has not reached the preregistered fit/convergence gate; more optimization may be justified within budget.",
    },
    "representation-signal-mismatch": {
        "layer": "mechanism",
        "meaning": "Optimization converged but the proposed representation/signal does not predict the scientific target.",
    },
    "objective-claim-mismatch": {
        "layer": "mechanism",
        "meaning": "The training objective can be optimized, but success on that objective does not identify the quantity required by the paper claim.",
    },
    "matched-simplification-tie": {
        "layer": "scientific-boundary",
        "meaning": "The proposed mechanism is empirically indistinguishable from a simpler matched baseline on the pilot.",
    },
    "positive-signal": {
        "layer": "scientific-boundary",
        "meaning": "The mechanism clears fit, identifiability, and matched-baseline gates; scale-up may be proposed but requires human approval.",
    },
    "true-negative": {
        "layer": "scientific-boundary",
        "meaning": "The experiment is identifiable and adequately optimized, yet the mechanism fails its preregistered scientific test.",
    },
}


REPAIR_OPERATORS: dict[str, dict[str, Any]] = {
    "debug-only": {
        "changes": "implementation",
        "scientific_change": False,
        "rule": "Repair only the runtime/harness defect; preserve the scientific protocol and hidden split.",
    },
    "substrate-requalification": {
        "changes": "experimental substrate",
        "scientific_change": False,
        "rule": "Change only the substrate/task generator until the preregistered variation and competence gates are satisfied.",
    },
    "target-variation-design": {
        "changes": "pilot construction",
        "scientific_change": False,
        "rule": "Create or select cases spanning the target decision boundary before training; verify label entropy before model fitting.",
    },
    "optimization-extension": {
        "changes": "training budget",
        "scientific_change": False,
        "rule": "Increase epochs/steps only when the learning curve has not converged and the target has adequate variation.",
    },
    "representation-child": {
        "changes": "one representation or feature family",
        "scientific_change": True,
        "rule": "Create an atomic child changing only the representation/signal while preserving candidate pool, truth, and evaluation budget.",
    },
    "objective-child": {
        "changes": "one learning objective",
        "scientific_change": True,
        "rule": "Replace the misaligned objective with one that directly matches the paper claim; keep representation and data fixed where possible.",
    },
    "disagreement-mining": {
        "changes": "pilot case selection",
        "scientific_change": False,
        "rule": "Before another GPU run, find cases where the proposed mechanism and strongest simplification make different decisions; merge if none exist.",
    },
    "merge-simplification": {
        "changes": "claim boundary",
        "scientific_change": True,
        "rule": "Merge the idea into the simpler parent/baseline when a matched pilot cannot expose a distinct decision or effect.",
    },
}


POLICY: dict[str, Any] = {
    "schema_version": "1.0",
    "pre_pilot_readiness_gates": [
        "novelty_locked",
        "substrate_qualified",
        "intervention_variation",
        "target_variation",
        "objective_matches_claim",
        "baseline_discriminability",
        "budget_precomputed",
        "streaming_trace_enabled",
    ],
    "atomic_child_only": True,
    "max_children_per_node": 2,
    "max_repair_depth": 3,
    "best_leaf_only_hill_climb_forbidden": True,
    "preserve_alternative_explanatory_branches": True,
    "negative_result_requires_layered_consultation_before_core_stop": True,
    "bug_fix_is_not_scientific_revision": True,
    "underfit_cannot_be_called_scientific_fail": True,
    "nonidentifiable_pilot_cannot_update_scientific_belief": True,
    "method_level_true_negative_does_not_automatically_falsify_principle": True,
    "principle_level_update_requires_principle_adjudicator": True,
    "hidden_split_reuse_after_exposure_forbidden": True,
    "automatic_scale_up_forbidden": True,
    "human_approval_required_after_positive_p0": True,
}


REFERENCES = [
    {
        "system": "AI Scientist-v2",
        "url": "https://github.com/SakanaAI/AI-Scientist-v2",
        "adopted": "multiple initial drafts, progressive experiment tree, bounded debug depth",
    },
    {
        "system": "AIDE",
        "url": "https://github.com/WecoAI/aideml",
        "adopted": "simple first draft, atomic single-change improvements, separate debug vs improvement branches",
    },
    {
        "system": "R&D-Agent",
        "url": "https://github.com/microsoft/RD-Agent",
        "adopted": "separate performance feedback for research hypotheses from error feedback for implementation",
    },
    {
        "system": "ML-Master",
        "url": "https://github.com/sjtu-sai-agents/ML-Master",
        "adopted": "persist experiment outcomes as scoped research memory for later exploration",
    },
    {
        "system": "AI Research Agents / AIRA",
        "url": "https://arxiv.org/abs/2507.02554",
        "adopted": "treat search policy, operators, and evaluation/final-node selection as separate design variables",
    },
    {
        "system": "Agent Laboratory",
        "url": "https://github.com/SamuelSchmidgall/AgentLaboratory",
        "adopted": "stage-separated literature/planning/experimentation with explicit human feedback checkpoints",
    },
]


@dataclass(frozen=True, slots=True)
class ArtifactBundle:
    idea_id: str
    path: Path
    plan: dict[str, Any]
    protocol: dict[str, Any]
    qualification: dict[str, Any]
    decision: dict[str, Any]


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _candidate_run_roots() -> list[Path]:
    roots: list[Path] = []
    try:
        roots.append(StorageSettings.from_env().run_dir)
    except Exception:
        pass
    for path in (
        Path("/data/wyt/agent-self-evolution-observatory/runs"),
        Path("/home/hdd/yutong/agent-evolution-p0-data/runs"),
    ):
        if path not in roots:
            roots.append(path)
    return roots


def find_latest_canonical_round1(run_roots: list[Path] | None = None) -> Path | None:
    candidates: list[Path] = []
    for root in run_roots or _candidate_run_roots():
        if not root.exists():
            continue
        candidates.extend(path for path in root.glob("round1-canonical-*") if path.is_dir())
    if not candidates:
        return None
    return max(candidates, key=lambda path: (path.stat().st_mtime, path.name))


def _bundle(root: Path, subdir: str, idea_id: str) -> ArtifactBundle:
    path = root / subdir
    return ArtifactBundle(
        idea_id=idea_id,
        path=path,
        plan=_read_json(path / "plan.json"),
        protocol=_read_json(path / "protocol.json"),
        qualification=_read_json(path / "qualification.json"),
        decision=_read_json(path / "decision.json"),
    )


def _trace_readiness(bundle: ArtifactBundle) -> dict[str, bool]:
    plan_prompts = int(bundle.plan.get("estimated_unique_prompts") or 0)
    actual = int(((bundle.decision.get("cost") or {}).get("new_prompt_scores")) or 0)
    return {
        "budget_precomputed": plan_prompts > 0,
        "streaming_trace_enabled": (bundle.path / "events.jsonl").exists() and (bundle.path / "score-cache.jsonl").exists(),
        "plan_matches_execution": bool(plan_prompts and actual and plan_prompts == actual),
        "provenance_frozen": bool(bundle.protocol.get("code_commit") and bundle.protocol.get("source_hash")),
    }


def _base_node(bundle: ArtifactBundle, code: str) -> dict[str, Any]:
    qualification_pass = bool(bundle.qualification.get("pass"))
    trace = _trace_readiness(bundle)
    return {
        "idea_id": bundle.idea_id,
        "code": code,
        "artifact_dir": str(bundle.path),
        "qualification_pass": qualification_pass,
        "trace_readiness": trace,
        "experiment_identifiable": False,
        "scientific_belief_update_allowed": False,
        "scale_up_allowed": False,
        "diagnosis": "infrastructure-error",
        "diagnosis_layer": DIAGNOSIS_TAXONOMY["infrastructure-error"]["layer"],
        "evidence": {},
        "repair_children": [],
    }


def _finalize(node: dict[str, Any], diagnosis: str, *, identifiable: bool, evidence: dict[str, Any], children: list[dict[str, Any]], belief_update: bool = False) -> dict[str, Any]:
    node.update({
        "diagnosis": diagnosis,
        "diagnosis_layer": DIAGNOSIS_TAXONOMY[diagnosis]["layer"],
        "experiment_identifiable": bool(identifiable),
        "scientific_belief_update_allowed": bool(belief_update),
        "scale_up_allowed": diagnosis == "positive-signal",
        "evidence": evidence,
        "repair_children": children[: int(POLICY["max_children_per_node"])],
    })
    return node


def diagnose_a1(bundle: ArtifactBundle) -> dict[str, Any]:
    node = _base_node(bundle, "A-1")
    q = bundle.qualification
    a1 = bundle.decision.get("a1") or {}
    fit = a1.get("fit") or {}
    table = a1.get("table") or []
    if not q.get("pass"):
        return _finalize(node, "substrate-degenerate", identifiable=False, evidence={"qualification": q}, children=[{
            "operator": "substrate-requalification",
            "changed_variable": "substrate only",
            "precondition": "qualification task success must lie strictly between degenerate floor/ceiling",
        }])
    if not (bundle.decision.get("cost") or {}).get("new_prompt_scores"):
        return node
    epochs = int(fit.get("epochs_ran") or 0)
    converged = bool(fit.get("converged"))
    auc = float(fit.get("val_auc") or 0.0)
    baseline = {str(row.get("policy")): row for row in table}
    if not bool(a1.get("fit_gate")) and converged and epochs >= 40 and auc <= 0.55:
        return _finalize(node, "representation-signal-mismatch", identifiable=False, evidence={
            "epochs": epochs,
            "converged": converged,
            "validation_auc": auc,
            "raw_drift_baseline": baseline.get("gain+raw-drift"),
            "fitted_gate": baseline.get("fitted-cross-surface-drift"),
        }, children=[
            {
                "operator": "representation-child",
                "child": "A1-R1 contextual-divergence",
                "changed_variable": "add task/update-surface conditional divergence; keep truth/candidate pool/budget fixed",
                "precondition": "retrospective leave-one-update-out AUC > 0.65 before new GPU execution",
            },
            {
                "operator": "merge-simplification",
                "child": "A1-S raw-drift simplification",
                "changed_variable": "remove learned gate and test whether monotone raw drift is sufficient",
                "precondition": "if raw drift matches on a larger frozen update pool, stop learned-gate claim",
            },
        ])
    return _finalize(node, "true-negative", identifiable=True, evidence={"fit": fit, "table": table}, children=[], belief_update=True)


def diagnose_a2(bundle: ArtifactBundle) -> dict[str, Any]:
    node = _base_node(bundle, "A-2")
    q = bundle.qualification
    a2 = bundle.decision.get("a2") or {}
    fit = a2.get("fit") or {}
    if not q.get("pass"):
        return _finalize(node, "substrate-degenerate", identifiable=False, evidence={"qualification": q}, children=[{
            "operator": "substrate-requalification", "changed_variable": "substrate only"
        }])
    if str(fit.get("reason") or "") == "no-label-variation":
        return _finalize(node, "no-label-variation", identifiable=False, evidence={
            "fit_reason": fit.get("reason"),
            "validation_auc": fit.get("val_auc"),
        }, children=[
            {
                "operator": "target-variation-design",
                "child": "A2-R1 sequence-archetype qualification",
                "changed_variable": "update-sequence generator only",
                "precondition": "before fitting, frozen sequences must contain early-stop, late-stop, and rollback-optimal cases with label entropy >= 0.6 bits",
            },
            {
                "operator": "objective-child",
                "child": "A2-R2 marginal-value controller",
                "changed_variable": "predict next-round marginal value instead of categorical optimal round",
                "precondition": "use the same frozen sequence pool; proceed only if marginal targets have non-trivial variance",
            },
        ])
    return _finalize(node, "true-negative", identifiable=True, evidence={"fit": fit}, children=[], belief_update=True)


def diagnose_b1(bundle: ArtifactBundle) -> dict[str, Any]:
    node = _base_node(bundle, "B-1")
    q = bundle.qualification
    table = list(bundle.decision.get("table") or [])
    estimation = bundle.decision.get("estimation_gate") or {}
    if not q.get("pass"):
        return _finalize(node, "substrate-degenerate", identifiable=False, evidence={"qualification": q}, children=[{
            "operator": "substrate-requalification", "changed_variable": "substrate only"
        }])
    if not estimation.get("pass"):
        return _finalize(node, "substrate-degenerate", identifiable=False, evidence={"estimation_gate": estimation}, children=[{
            "operator": "substrate-requalification", "changed_variable": "process-family/effect-variation qualification"
        }])
    selections = [tuple(row.get("lessons") or []) for row in table]
    effects = [round(float(row.get("mean_hidden_effect") or 0.0), 10) for row in table]
    if selections and len(set(selections)) == 1 and len(set(effects)) == 1:
        return _finalize(node, "matched-simplification-tie", identifiable=True, belief_update=True, evidence={
            "all_policy_selection": list(selections[0]),
            "all_policy_hidden_effect": effects[0],
            "policies": [row.get("policy") for row in table],
        }, children=[
            {
                "operator": "disagreement-mining",
                "child": "B1-R1 disagreement-case miner",
                "changed_variable": "case selection only; no new model mechanism",
                "precondition": "find held-out cases where utility-only and cross-process robustness rank different lessons before another GPU run",
            },
            {
                "operator": "merge-simplification",
                "child": "B1-S merge into utility admission",
                "changed_variable": "claim boundary only",
                "precondition": "merge if retrospective + newly mined cases still produce identical decisions",
            },
        ])
    return _finalize(node, "positive-signal" if bundle.decision.get("method_go") else "true-negative", identifiable=True, belief_update=True, evidence={"table": table}, children=[])


def diagnose_e1(bundle: ArtifactBundle) -> dict[str, Any]:
    node = _base_node(bundle, "E-1")
    q = bundle.qualification
    table = bundle.decision.get("table") or {}
    fit = table.get("fit") or {}
    if not q.get("pass"):
        return _finalize(node, "substrate-degenerate", identifiable=False, evidence={"qualification": q}, children=[{
            "operator": "substrate-requalification", "changed_variable": "substrate only"
        }])
    auc = float(fit.get("val_auc") or 0.0)
    top1 = float(fit.get("calibration_top1_accuracy") or 0.0)
    global_top1 = float(fit.get("global_best_accuracy") or 0.0)
    converged = bool(fit.get("converged"))
    epochs = int(fit.get("epochs_ran") or 0)
    if not bool(table.get("fit_gate")) and converged and epochs >= 40 and auc >= 0.8 and top1 <= global_top1:
        return _finalize(node, "objective-claim-mismatch", identifiable=False, evidence={
            "epochs": epochs,
            "converged": converged,
            "binary_validation_auc": auc,
            "calibration_top1_accuracy": top1,
            "global_best_accuracy": global_top1,
        }, children=[
            {
                "operator": "objective-child",
                "child": "E1-R1 pairwise edit ranking",
                "changed_variable": "replace binary positive-effect loss with pairwise delta-ranking loss; keep edit representation/workflows fixed",
                "precondition": "calibration top-1 must exceed global-best by >=25pp before opening fresh hidden workflows",
            },
            {
                "operator": "objective-child",
                "child": "E1-R2 listwise regret prediction",
                "changed_variable": "predict normalized edit regret within each workflow rather than binary effect",
                "precondition": "same frozen source workflows and edit library; no hidden access during objective selection",
            },
        ])
    return _finalize(node, "true-negative", identifiable=True, belief_update=True, evidence={"fit": fit, "table": table}, children=[])


def _missing_node(idea_id: str, code: str, root: Path | None) -> dict[str, Any]:
    return {
        "idea_id": idea_id,
        "code": code,
        "artifact_dir": str(root or ""),
        "qualification_pass": False,
        "trace_readiness": {},
        "experiment_identifiable": False,
        "scientific_belief_update_allowed": False,
        "scale_up_allowed": False,
        "diagnosis": "infrastructure-error",
        "diagnosis_layer": "execution",
        "evidence": {"reason": "canonical Round-1 artifacts not found"},
        "repair_children": [],
    }


def build_experiment_iteration_state(*, round1_root: Path | None = None) -> dict[str, Any]:
    root = round1_root or find_latest_canonical_round1()
    if root is None:
        nodes = [
            _missing_node("update-trust-region", "A-1", None),
            _missing_node("budgeted-evolution-controller", "A-2", None),
            _missing_node("outcome-equivalent-trajectory-contrast", "B-1", None),
            _missing_node("workflow-generalization-certificate", "E-1", None),
        ]
    else:
        a12_a1 = _bundle(root, "a12", "update-trust-region")
        a12_a2 = _bundle(root, "a12", "budgeted-evolution-controller")
        b1 = _bundle(root, "b1", "outcome-equivalent-trajectory-contrast")
        e1 = _bundle(root, "e1", "workflow-generalization-certificate")
        nodes = [diagnose_a1(a12_a1), diagnose_a2(a12_a2), diagnose_b1(b1), diagnose_e1(e1)]
    counts = Counter(node["diagnosis"] for node in nodes)
    repair_children = sum(len(node.get("repair_children") or []) for node in nodes)
    return {
        "schema_version": "1.0",
        "round1_root": str(root or ""),
        "policy": POLICY,
        "taxonomy": DIAGNOSIS_TAXONOMY,
        "repair_operators": REPAIR_OPERATORS,
        "references": REFERENCES,
        "summary": {
            "nodes": len(nodes),
            "identifiable": sum(bool(node["experiment_identifiable"]) for node in nodes),
            "belief_updates_allowed": sum(bool(node["scientific_belief_update_allowed"]) for node in nodes),
            "scale_up_allowed": sum(bool(node["scale_up_allowed"]) for node in nodes),
            "repair_children": repair_children,
            "diagnosis_counts": dict(counts.most_common()),
        },
        "nodes": nodes,
    }
