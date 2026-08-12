from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .human_terminal_state import build_human_terminal_state
from .p0_admission import build_p0_admission_state
from .p0_decision_ledger import build_p0_decision_ledger
from .p0_four_direction_iteration import build_four_direction_iteration
from .p0_offline_qualification import build_p0_offline_qualification_state
from .paper_design_contract import audit_paper_design_contract
from .paper_first_collision_review import build_fresh_collision_review

DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-stop-triage.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "paper-first-stop-triage.js"

POLICY = {
    "schema_version": "1.0",
    "paper_first_after_terminal_f0": True,
    "old_method_reactivation_forbidden": True,
    "matched_simplification_stop_cannot_be_repaired_by_more_compute": True,
    "substrate_stop_requires_new_paper_contract_before_substrate_change": True,
    "new_child_requires_genuinely_new_problem_or_irreducible_novelty_axis": True,
    "novelty_review_precedes_local_validation": True,
    "local_validation_cannot_discover_or_redefine_the_method": True,
    "ai_consultation_is_advisory_only": True,
}

# Curated dispositions encode the scientific meaning of already-frozen terminal
# evidence.  They do not change the parent lifecycle or authorize execution.
PAPER_NOVELTY_HOLD = {
    "budgeted-evolution-controller",
    "regression-gated-self-evolution",
    "contradiction-preserving-consolidation",
    "retrieval-interference-auditor",
    "workflow-generalization-certificate",
}

DIAGNOSTIC_ARCHIVE = {
    "self-label-confidence-flow": "Strong cross-round error inheritance is real, but the frozen lineage-aware decision changes only 2.5% of candidates and current self-training literature already targets confirmation bias and pseudo-label reliability.",
    "self-correction-collapse-detector": "Correction-order effects are real, but the learned transition controller is nearly reproduced by a depth-3 CART and current work already learns state-conditioned correction actions.",
}

NEW_PROBLEM_ID = "trajectory-mediated-memory-effect-transport"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _paper_candidate() -> dict[str, Any]:
    collision_review = build_fresh_collision_review()
    replay_path = PROJECT_ROOT / "generated" / "paper-first-replay-feasibility.json"
    try:
        replay_feasibility = json.loads(replay_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        replay_feasibility = {}
    replay_pass = replay_feasibility.get("decision") == "ENVIRONMENT_REPLAY_FEASIBILITY_PASS"
    paper_design = {
        "novelty": {
            "paper_problem": (
                "Persistent agent memory can reproducibly steer an early trajectory branch while the final utility sign flips across downstream contexts, "
                "making endpoint-level memory admission and effect transport potentially non-identifiable."
            ),
            "closest_work": [
                {
                    "identity": "Causal Agent Replay: Counterfactual Attribution for LLM-Agent Failures",
                    "difference": "CAR intervenes on trajectory steps to attribute failures; this paper treats persistent memory as the treatment, the earliest branch divergence as a mediator, and asks whether the treatment effect is transportable across downstream contexts rather than which step caused a failure.",
                    "source_ref": "arXiv:2606.08275",
                },
                {
                    "identity": "CausalFlow: Causal Attribution and Counterfactual Repair for LLM Agent Failures",
                    "difference": "CausalFlow already performs step-level counterfactual interventions and run-forward repair, so replay or branch intervention is not claimed as novel here. The surviving axis is whether a persistent-memory treatment has a context-stable mediated effect that may be transported to new downstream contexts.",
                    "source_ref": "arXiv:2605.25338",
                },
                {
                    "identity": "Causal Intervention-Based Memory Selection for Long-Horizon LLM Agents",
                    "difference": "CMI estimates endpoint usefulness of candidate memories for selection; this paper does not claim memory selection and instead asks whether the treatment effect itself is transportable after conditioning on the trajectory mediator and downstream context.",
                    "source_ref": "arXiv:2605.17641",
                },
                {
                    "identity": "ShiftBench: Measuring Recovery of Agent Memory Under Distribution Shift",
                    "difference": "ShiftBench demonstrates ranking reversals under distribution shift; this paper targets within-intervention trajectory mediation and same-branch-sign reversals rather than post-shift recovery as an evaluation axis.",
                    "source_ref": "OpenReview:CCSztIjmOy",
                },
                {
                    "identity": "When Continual Learning Moves to Memory: A Study of Experience Reuse in LLM Agents",
                    "difference": "This work establishes memory-level negative transfer and representation/retrieval trade-offs; this paper adds a causal trajectory-level identifiability test for why one memory intervention changes sign across contexts.",
                    "source_ref": "arXiv:2604.27003",
                },
                {
                    "identity": "From Player to Master: Enhancing Test-Time Learning of LLM Agents via Reinforcement Learning over Memory",
                    "difference": "MemoPilot learns the memory-update process from downstream performance; this paper does not reopen memory-updater learning and instead studies whether an already-observed memory treatment effect is identifiable and transportable across contexts.",
                    "source_ref": "OpenReview:gNWNtstp3r",
                },
                {
                    "identity": "Trajectory-Informed Memory Generation for Self-Improving Agent Systems",
                    "difference": "Trajectory-informed memory extracts and attributes reusable guidance from executions; this paper treats the trajectory branch as a causal mediator of a fixed memory intervention rather than as a memory-generation signal.",
                    "source_ref": "arXiv:2603.10600",
                },
            ],
            "novelty_axis": "context-conditioned transportability of a controlled mediator-action contrast induced by a persistent-memory treatment",
            "contribution_claim": (
                "A transportability certificate for a controlled mediator-action contrast induced by persistent memory: use counterfactual replay only as a measurement instrument, force the two earliest divergent actions from the same reconstructed pre-divergence state, remove memory, and test whether the resulting action contrast remains sign-stable across pre-treatment/external downstream-context descriptors."
            ),
            "irreducible_difference": (
                "CAR/CausalFlow-style step interventions can estimate which step or edit changes an outcome, and CMI can estimate endpoint causal usefulness of a memory, but neither alone supplies a same-information certificate that a memory treatment's mediated effect is stable enough to transport across downstream contexts. The paper survives only if this certificate beats a composed CAR-style attribution + endpoint CMI + context-stratification baseline."
            ),
            "collision_status": collision_review["decision"],
        },
        "method": {
            "method_name": "Context-Conditioned Controlled-Mediator Transport Certificate",
            "core_mechanism": (
                "Treat persistent memory ON/OFF as treatment T used only to reveal the two earliest divergent admissible actions A0/A1. Deterministic prefix replay reconstructs a common pre-divergence state S*. From S*, force A0 or A1, remove memory from both arms, and continue with one frozen memory-free policy pi0. The estimand is the controlled mediator-action contrast tau_A(C)=E[Y|do(A=A1),S*,pi0,C]-E[Y|do(A=A0),S*,pi0,C], not a natural indirect effect. Context C must be pre-treatment or externally frozen before the branch. Fit/freeze a certificate that predicts sign stability of tau_A on held-out contexts."
            ),
            "novelty_to_method_mapping": [
                {"novelty": "persistent-memory-induced controlled mediator-action contrast", "component": "T/S*/A0/A1/C/Y contract plus paired forced-action intervention"},
                {"novelty": "context-conditioned contrast transportability", "component": "candidate-held-out and context-held-out sign-stability certificate using pre-treatment/external context only"},
                {"novelty": "separate treatment mediation from continued memory exposure", "component": "shared frozen memory-free continuation after mediator intervention"},
            ],
            "components": [
                "deterministic prefix-replay state reconstruction",
                "paired divergence-action intervention",
                "shared memory-free continuation",
                "controlled mediator-action contrast / downstream-amplification estimator",
                "held-out transportability certificate",
            ],
            "strongest_simplification": (
                "A composed same-information baseline combining endpoint CMI-style memory effect, CAR/CausalFlow-style step attribution at the retrieval/divergence step, target/context-family stratification, and first-divergence timing/signature features under the identical replay budget."
            ),
            "method_change_rule": (
                "Any change to treatment unit, common-state definition, A0/A1 mediator-action definition, prefix-replay intervention, memory-free continuation policy, allowed context variables, or transportability statistic returns the work to novelty/method design and invalidates local-validation authority."
            ),
        },
        "experiment_blueprint": {
            "claim_experiment_matrix": [
                {
                    "claim_id": "C1",
                    "claim": "Action-prefix replay reconstructs the same branch-point environment state without a snapshot/restore API.",
                    "local_test": "Replay 5-step prefixes on at least 20 branch points spanning >=4 ALFWorld task families and compare the stable public environment state exposed by the project wrapper: observation, reward, done, and admissible commands after every step. Symbolic state facts are not exposed through a stable public API and are not claimed.",
                    "full_test": "Audit every branch point used by any later experiment and exclude any unit whose replayed public-state sequence or frozen-action admissibility fails.",
                    "metric": "exact public-state replay equivalence rate; local GO requires 100% equality of observation/reward/done/admissible commands and zero frozen-action admissibility failures",
                    "strongest_baseline": "fresh reset without exact prefix replay",
                },
                {
                    "claim_id": "C2",
                    "claim": "Persistent memory induces a reproducible controlled mediator-action contrast at the earliest divergence that can be separated from continued memory exposure; this is not claimed as a natural indirect effect and replay itself is not novel.",
                    "local_test": "Use exactly the frozen 10 route-reproducible units from paper_first_c2_support_inventory_20260812.json; no unit replacement. Reconstruct S*, force A0/A1, remove memory, continue with the identical frozen parent no-memory policy pi0, and repeat each forced branch twice before any aggregate tau_A decision.",
                    "full_test": "Locked. A larger candidate/context-held-out experiment may be designed only after C2_GO and a new paper/AI adjudication; no current >=100-unit collection is authorized.",
                    "metric": "C2_GO iff valid_units=10 AND nonzero_tau_A>=9 AND parent-sign-concordant tau_A>=9 AND the frozen three-context memory candidate reproduces the required cross-context sign reversal; same-action repeat/null and pi0 support checks are binding preconditions",
                    "strongest_baseline": "endpoint CMI-style memory effect plus CAR/CausalFlow-style step attribution and first-divergence timing/signature heuristic at matched replay cost",
                },
                {
                    "claim_id": "C3",
                    "claim": "The context-conditioned controlled-action certificate detects non-transportable persistent-memory-induced action contrasts beyond a composed endpoint + step-attribution + context-stratification baseline, using only pre-treatment/external context variables.",
                    "local_test": "Require >=4 observed sign-reversal context pairs and compare the frozen certificate with endpoint variance, target-family prior, and CAR-style attribution using identical units.",
                    "full_test": "Candidate-held-out x context-family-held-out evaluation on two environments only after the local test passes and the method is frozen.",
                    "metric": "non-transportability AUROC / false-certification rate; GO requires >=0.10 AUROC advantage over the strongest same-information simplification and zero threshold relaxation",
                    "strongest_baseline": "composed same-information CMI-style endpoint effect + CAR/CausalFlow-style step attribution + context-family model",
                },
            ],
            "local_validation_scope": (
                "One frozen Qwen2.5-7B-Instruct backbone and ALFWorld only. Environment-only replay fidelity has passed. C2 is exactly the 10 strict route-reproducible parent units on the original parent host/runtime; no unit replacement, second backbone, new updater training, certificate training, or paper-scale table."
            ),
            "full_experiment_scope": (
                "Currently locked. Only after C2_GO plus a new paper-design/AI adjudication may the system freeze a paper-scale candidate/context-held-out experiment with the composed CMI+CAR/CausalFlow baseline, efficiency accounting, and any replication environment. C2 itself cannot authorize that scope."
            ),
            "baseline_matrix": [
                "endpoint memory ON/OFF treatment effect",
                "target-family stratified endpoint effect",
                "first-divergence timing/signature heuristic",
                "CMI-style endpoint causal usefulness",
                "CAR-style step attribution adapted to the retrieval/intervention step",
                "CausalFlow-style counterfactual step-responsibility features",
                "composed endpoint + step-attribution + context-family baseline",
            ],
            "ablation_matrix": [
                "remove branch intervention and use endpoint effect only",
                "keep branch intervention but allow memory during continuation",
                "replace held-out transport certificate with target-family lookup",
                "remove downstream-context interaction",
            ],
            "freeze_rule": (
                "Freeze treatment unit, common-state contract, strict 10-unit pool, A0/A1 definition, admissibility/overlap checks, replay equality checks, memory-free continuation policy, allowed pre-treatment/external context variables, estimator, composed baselines, holdouts, and GO/STOP thresholds before opening local branch-effect outcomes; any core change returns to paper novelty/method design."
            ),
            "experimental_integrity": {
                "model_and_inference": {
                    "C2_host": "222.20.126.60",
                    "gpu_uuid": "GPU-814cd021-31d8-2c6f-76a5-b8d4739b34d1",
                    "model": "/home/hdd/qinglinji/models/Qwen2.5-7B-Instruct",
                    "model_config_sha256": "7463bb0ea78315365e6c6b74de4e73bbcc8359dfb0c5a737584e077d42c0b03c",
                    "model_index_sha256": "624bf7c47cd12468fdc16e38a47cf4f19e0415b859a223ba3c027eed2f0e1028",
                    "python": "/home/hdd/yutong/envs/vlm_fp_231_exact/bin/python",
                    "python_version": "3.11.15",
                    "torch": "2.4.0+cu121",
                    "transformers": "5.12.1",
                    "textworld": "1.7.0",
                    "actor": "HFAdmissiblePolicy(policy_mode='react-family')",
                    "decoding": "deterministic greedy generation exactly as the frozen parent actor implementation",
                    "max_total_steps": 50,
                    "adapter_sha256": "7cb65832fefd882e560f47acbc7e8df9629fa6322115c375bed3fe31b41e030b",
                    "runtime_rule": "Any version, hash, model, actor, GPU-UUID, or parent-raw mismatch blocks C2 before model load."
                },
                "prompt_tool_policy": {
                    "scaffold": "Frozen parent react-family ALFWorld scaffold; no prompt editing or tool-policy changes are allowed.",
                    "memory_treatment_use": "Parent memory/placebo traces are historical evidence only for identifying A1/A0. After the forced branch action, both C2 arms use an empty memory patch.",
                    "continuation_policy": "The identical memory-free pi0 chooses only from the current admissible commands in both arms.",
                    "forbidden": ["new system prompt", "new retrieval logic", "tool changes", "memory re-injection", "test-time adaptation", "candidate-specific prompting"]
                },
                "task_sample_split": {
                    "C1_environment_feasibility": "Frozen 20 historical source traces across 6 families; already completed and cannot be used to tune C2 outcomes.",
                    "C2_pool": "Exactly 10 route-reproducible controlled-nonzero parent units from the frozen 72-unit/216-trajectory table; the sole route/sign mismatch is excluded before C2 outcomes and cannot be replaced.",
                    "paper_authority_discrepancy": "Paper-level authority records 12 stable controlled-nonzero effects, but only 11 are raw-trace-addressable and 10 are strict route-reproducible; the missing/mismatched units are forbidden as support rescue.",
                    "C3_hidden": "No C3 certificate-training or held-out-context split is opened by C2. A new split must be frozen only after C2_GO and a new paper adjudication."
                },
                "metric_analysis_plan": {
                    "C1": "20/20 exact public-state replay and frozen-action admissibility across >=4 families.",
                    "C2_precheck": "valid_units must equal 10; branchpoint hash, repeated A0 branch, repeated A1 branch, forced-action admissibility, and pi0 continuation support must all pass per unit.",
                    "C2_GO": "valid_units==10 AND nonzero_tau_A_units>=9 AND parent_sign_concordant_units>=9 AND required same-memory cross-context tau_A sign reversal is true.",
                    "C2_STOP": "valid_units<=9 OR nonzero_tau_A_units<=8 OR parent_sign_concordant_units<=8 OR required sign reversal is false.",
                    "C3": "No C3 metric is currently executable; the historical >=0.10 AUROC target is not an authorization and must be re-audited if C2_GO occurs.",
                    "threshold_rule": "No post-outcome threshold relaxation, metric substitution, family pooling change, or unit rescue."
                },
                "randomness_replication_plan": {
                    "actor_randomness": "Parent actor uses deterministic greedy decoding; no sampling seed is introduced for C2.",
                    "branch_repeats": "A0 and A1 are each executed twice from independent fresh resets for every unit before aggregate tau_A adjudication.",
                    "repeat_purpose": "Repetition is a deterministic consistency/null gate, not a statistical seed search.",
                    "failure_semantics": "Any repeat mismatch invalidates that unit and therefore triggers C2_STOP because all 10 units are required.",
                    "seed_rescue_forbidden": True
                },
                "stopping_exclusion_rules": {
                    "pre_outcome_exclusion": ["the single matched-hardware route/sign mismatch unit", "any unit failing frozen runtime hash checks"],
                    "C2_exclusion_after_start": "No unit may be replaced. Any admissibility, branchpoint, repeated-branch, or pi0-support failure counts as invalid and forces valid_units<=9, hence STOP.",
                    "early_stop": "The runner may stop before aggregate tau_A reporting when runtime/precheck fails because C2_GO is then mathematically impossible.",
                    "forbidden_rescue": ["new full table", "new model", "second backbone", "new unit", "new seed", "threshold relaxation", "post-hoc context regrouping"]
                },
                "allowed_adaptations": {
                    "execution_only": "A runtime/serialization/monitoring bug may be fixed only if the frozen scientific contract, source hashes, model/runtime hashes, strict unit set, actions, pi0 policy, metrics, and thresholds remain identical.",
                    "scientific_change": "Any change to estimand, context definition, unit pool, A0/A1 definition, replay rule, pi0 policy, baseline family, metric, or threshold returns the work to paper novelty/method design and invalidates C2 execution authority.",
                    "documentation_only": "Clarifying prose or adding missing provenance fields is allowed if it does not reinterpret outcomes."
                },
                "hidden_evaluation_access_policy": {
                    "known_parent_evidence": "Parent endpoint controlled deltas, historical trajectories, first-divergence actions, and the pre-identified same-memory sign-flip example are allowed inputs because they define the paper problem and frozen C2 support inventory.",
                    "C2_hidden_outcome": "Forced-action tau_A outcomes must remain unopened until the C2 contract, strict unit pool, runtime, prechecks, and numeric GO/STOP are frozen and committed.",
                    "C3_hidden_outcome": "Certificate labels, held-out-context outcomes, and any paper-scale second-environment results remain sealed and unavailable for method/baseline/threshold tuning during C2.",
                    "leakage_rule": "Only pre-treatment or externally frozen context variables may enter any future transport certificate; post-treatment trajectory features are forbidden as C."
                }
            },
        },
    }
    audit = audit_paper_design_contract({"pre_experiment": {"paper_design": paper_design}})
    return {
        "paper_id": NEW_PROBLEM_ID,
        "title": "When Do Agent Memory Effects Transport Across Contexts?",
        "parent_evidence": ["B-8 replicated-effect-memory-gate", "B-9 cross-task-effect-transport-certificate"],
        "relationship_to_closed_program": (
            "Genuinely new research problem: causal identifiability/effect transport of memory interventions. It does not reopen a prompt/memory updater, admission gate, LoRA, reranker, second-backbone rescue, or threshold repair from the closed persistent-updater program."
        ),
        "paper_design": paper_design,
        "paper_design_audit": audit,
        "fresh_collision_review": collision_review,
        "feasibility": {
            "prefix_replay_smoke": {
                "status": replay_feasibility.get("decision") or "unverified-no-raw-artifact",
                "artifact": str(replay_path) if replay_feasibility else None,
                "selected_tasks": (replay_feasibility.get("summary") or {}).get("selected_tasks", 0),
                "task_families": (replay_feasibility.get("summary") or {}).get("task_families", 0),
                "prefix_steps_per_task": 5,
                "all_public_steps_equal": bool(replay_pass and (replay_feasibility.get("summary") or {}).get("failed_units", 1) == 0),
                "historical_observation_match": (replay_feasibility.get("summary") or {}).get("historical_observation_match", 0),
                "fresh_replay_public_state_match": (replay_feasibility.get("summary") or {}).get("fresh_replay_public_state_match", 0),
                "checked_fields": ["observation", "reward", "done", "admissible_commands"],
                "state_facts_available": bool((replay_feasibility.get("summary") or {}).get("state_facts_available", False)),
                "authority": "environment-only feasibility; cannot establish novelty or authorize C2/C3",
            },
            "snapshot_restore_required": False if replay_pass else "unknown-until-replay-gate",
            "runtime_patch_required": False if replay_pass else "unknown-until-replay-gate",
        },
        "fresh_collision_review_required_before_local_validation": True,
        "fresh_collision_review_complete": collision_review["decision"].startswith("PASS_"),
        "ai_premortem_required_before_local_validation": True,
        "environment_feasibility_complete": replay_pass,
        "local_validation_authorized": False,
        "full_experiment_authorized": False,
    }


def build_paper_first_stop_triage() -> dict[str, Any]:
    admission = build_p0_admission_state()
    offline = build_p0_offline_qualification_state()
    human = build_human_terminal_state()
    iteration = build_four_direction_iteration()
    ledger = build_p0_decision_ledger(admission, offline, human, iteration)
    rows: list[dict[str, Any]] = []
    for row in ledger.get("rows") or []:
        idea_id = str(row.get("idea_id") or "")
        state = str(row.get("current_state") or "")
        stop_class = str(row.get("economy_stop_class") or "")
        if idea_id in {"replicated-effect-memory-gate", "cross-task-effect-transport-certificate"}:
            disposition = "PARENT_EVIDENCE_FOR_NEW_PAPER_PROBLEM"
            reason = "Reuse only the frozen trajectory-branch phenomenon as evidence; do not reactivate either old method."
        elif idea_id in DIAGNOSTIC_ARCHIVE:
            disposition = "ARCHIVE_PHENOMENON_MERGE_COMPONENT"
            reason = DIAGNOSTIC_ARCHIVE[idea_id]
        elif state == "experiment-merge":
            disposition = "MERGE_COMPONENT"
            reason = "The latest experiment authority already merges this realization; no new paper method is created from the same mechanism."
        elif idea_id in PAPER_NOVELTY_HOLD:
            disposition = "PAPER_NOVELTY_HOLD_NO_SUBSTRATE_RESCUE"
            reason = "The method is not cleanly falsified on a qualified substrate, but paper novelty/claim must be re-established before changing substrate or running more compute."
        elif stop_class == "matched-simplification" or state in {"experiment-stop-await-human-review", "method-development-stop"}:
            disposition = "TERMINATE_OR_MERGE_CURRENT_REALIZATION"
            reason = "The current realization has no irreducible headroom under its strongest matched simplification or is explicitly development-stopped. More compute cannot repair the same claim."
        elif state == "upstream-hold":
            disposition = "PROBLEM_HOLD_NO_METHOD"
            reason = "Keep the problem only; no method or experiment may reopen without a new paper-first contract."
        else:
            disposition = "NO_ACTION"
            reason = "No paper-first transition is authorized from the current state."
        rows.append({
            "idea_id": idea_id,
            "code": row.get("code"),
            "current_state": state,
            "economy_stop_class": stop_class or None,
            "disposition": disposition,
            "reason": reason,
            "execution_authorized": False,
        })

    candidate = _paper_candidate()
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["disposition"]] = counts.get(row["disposition"], 0) + 1
    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "policy": POLICY,
        "summary": {
            "active_p0_rows": len(rows),
            "paper_redesign_candidates": 1,
            "old_methods_reactivated": 0,
            "local_validation_authorized": int(bool(candidate.get("local_validation_authorized"))),
            "full_experiment_authorized": 0,
            "disposition_counts": counts,
        },
        "rows": rows,
        "paper_candidates": [candidate],
    }


def write_paper_first_stop_triage(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    state = build_paper_first_stop_triage()
    candidate = state["paper_candidates"][0]
    if not (candidate.get("paper_design_audit") or {}).get("passed"):
        raise ValueError("paper-first candidate contract is structurally incomplete")
    if state["summary"]["old_methods_reactivated"] != 0:
        raise ValueError("old stopped methods must not be reactivated by paper-first triage")
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.PAPER_FIRST_STOP_TRIAGE = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    print(json.dumps(write_paper_first_stop_triage(), ensure_ascii=False, indent=2))
