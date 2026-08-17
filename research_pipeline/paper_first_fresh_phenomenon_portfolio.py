from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .paper_first_skill_validation_transfer_scout import (
    DEFAULT_JSON as SKILL_VALIDATION_SCOUT_JSON,
    F0_HARNESS as SKILL_VALIDATION_F0_HARNESS,
    validate_skill_validation_transfer_scout,
)

DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-fresh-phenomenon-portfolio-20260817.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "paper-first-fresh-phenomenon-portfolio-20260817.js"
EVIDENCE_ECHO_JSON = PROJECT_ROOT / "generated" / "paper-first-evidence-echo-retrospective-20260817.json"
EVIDENCE_ECHO_F0 = PROJECT_ROOT / "research_pipeline" / "paper_first_evidence_echo_f0.py"
EVIDENCE_ECHO_F0_REPAIR = PROJECT_ROOT / "generated" / "paper-first-evidence-echo-f0-operationalization-repair-20260817.json"
EVIDENCE_ECHO_F0_GOVERNANCE_GUARD = PROJECT_ROOT / "generated" / "paper-first-evidence-echo-f0-governance-guard-20260817.json"
EVIDENCE_ECHO_F0_RESULT = PROJECT_ROOT / "generated" / "paper-first-evidence-echo-f0-authorized-result-20260817.json"
EXPECTED_EVIDENCE_ECHO_F0_RESULT_SHA256 = "274d6b12e321895e96c47324811e2c80b4c9b2e3a94d31a2a5942ae9ee68fafb"
DEFENSE_RESTRICTIVENESS_READJUDICATION = PROJECT_ROOT / "generated" / "hard-security-utility-collapse-principle-readjudication-20260817.json"
SPATIAL_MEMORY_READJUDICATION = PROJECT_ROOT / "generated" / "spatial-memory-high-trs-grounding-principle-readjudication-20260817.json"
HARNESSBANK_SUPPORT_AUDIT = PROJECT_ROOT / "generated" / "harnessbank-support-audit-20260817.json"
EXPECTED_EVIDENCE_ECHO_F0_ORIGINAL_SHA256 = "8f3b04d09c4101335434fa7a8a50bba965ab95ce244cf24c5fe9e53ba6feadf6"
EXPECTED_EVIDENCE_ECHO_F0_REVIEWED_SHA256 = "f64ae7c42f5e02b2f18abd67e4a784e3790b3c75107a4140666d9faa1c39842e"
EXPECTED_EVIDENCE_ECHO_F0_GUARDED_SHA256 = "5c5e25957388b723a301cac7e78c81d972b77eb0dc62b8bb53343318c6ea6ab3"
EXPECTED_EVIDENCE_ECHO_F0_REPAIR_SHA256 = "8965c54594356a87e642ebe3cc4cd76eb899ece5e6436eb96f097d09473aad30"
EXPECTED_EVIDENCE_ECHO_F0_GOVERNANCE_GUARD_SHA256 = "2be69a4968575dcb4e4cab5cde686709f15bc3375f52eb68b34f8b2781589a87"
EXPECTED_EVIDENCE_ECHO_F0_PLAN_SHA256 = "f7c1b8cce177a0efff84cfcf404ef436cf89ead1648548bcd6d633aa3c80a621"
PRIMARY_STATE_JSON = PROJECT_ROOT / "generated" / "paper-first-primary-evidence-state.json"
DEAD_END_MEMORY_JSON = PROJECT_ROOT / "generated" / "paper-first-search-portfolio-design-adjudication.json"
DEFENSE_PRINCIPLE_REDUCTION_JSON = PROJECT_ROOT / "generated" / "hard-security-utility-collapse-principle-readjudication-20260817.json"

SCHEMA_VERSION = "1.0"
AUDITED_SUBSTRATE_STATUSES = {
    "PROVENANCE_AUDITED_LOCAL_SUBSTRATE",
    "PROVENANCE_AUDITED_FIRST_PARTY_EXECUTABLE_SUBSTRATE",
}
ACTIVE_F0_LIMIT = 1
ALLOWED_STATUSES = {
    "ACTIVE_F0",
    "SCOUT_ASSET",
    "HOLD_SUPPORT",
    "HOLD_EXECUTION",
    "HOLD_REDUCTION",
    "READY_FOR_PROBLEM_REVIEW",
    "STOP_REDUCTION",
    "ARCHIVED",
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else ""


def _candidate(
    *,
    candidate_id: str,
    title: str,
    source_refs: list[str],
    phenomenon: str,
    strongest_reduction: str,
    cheapest_falsifier: str,
    support_status: str,
    status: str,
    priority: int,
    why_now: str,
    substrate: dict[str, Any] | None = None,
    evidence: dict[str, Any] | None = None,
    reopen_only_if: str = "",
) -> dict[str, Any]:
    return {
        "candidate_id": candidate_id,
        "title": title,
        "source_refs": source_refs,
        "phenomenon": phenomenon,
        "strongest_reduction": strongest_reduction,
        "cheapest_falsifier": cheapest_falsifier,
        "support_status": support_status,
        "status": status,
        "priority": priority,
        "why_now": why_now,
        "substrate": substrate or {},
        "evidence": evidence or {},
        "reopen_only_if": reopen_only_if,
        "paper_problem_claimed": False,
        "scientific_authority": False,
        "authority": {
            "problem_gate": False,
            "paper_design": False,
            "method": False,
            "experiment": False,
            "p0": False,
            "gpu": False,
            "full_experiment": False,
        },
    }


def _memory_hold(memory: dict[str, Any], source_candidate_id: str) -> dict[str, Any]:
    dead = memory.get("shadow_dead_end_memory") or {}
    rows = [row for row in dead.get("hold_objects") or [] if isinstance(row, dict)]
    return next((row for row in rows if str(row.get("source_candidate_id") or "") == source_candidate_id), {})


def build_fresh_phenomenon_portfolio(
    *,
    evidence_echo: dict[str, Any] | None = None,
    evidence_echo_f0_result: dict[str, Any] | None = None,
    primary_state: dict[str, Any] | None = None,
    dead_end_memory: dict[str, Any] | None = None,
    execution_capability: dict[str, Any] | None = None,
    defense_readjudication: dict[str, Any] | None = None,
    spatial_readjudication: dict[str, Any] | None = None,
    harnessbank_support_audit: dict[str, Any] | None = None,
    skill_validation_scout: dict[str, Any] | None = None,
    skill_execution_capability: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compile multiple paper scouts without letting unsupported ideas consume experiment slots.

    This portfolio is search/execution control only. It intentionally sits outside the
    canonical Problem Queue. A candidate can occupy the single ACTIVE_F0 slot only when
    a provenance-audited substrate, a frozen same-information falsifier, and a separate
    controller-verified execution capability already exist. Design-ready candidates that
    lack matching experiment authority (and GPU leases only for GPU-backed execution) remain
    HOLD_EXECUTION. A positive F0 does not
    grant Problem-Gate or Paper-Design authority; it merely moves the candidate to
    READY_FOR_PROBLEM_REVIEW on the next explicit adjudication pass.
    """

    evidence_echo = evidence_echo or _load(EVIDENCE_ECHO_JSON)
    if evidence_echo_f0_result is None:
        evidence_echo_f0_result = _load(EVIDENCE_ECHO_F0_RESULT)
    primary_state = primary_state or _load(PRIMARY_STATE_JSON)
    dead_end_memory = dead_end_memory or _load(DEAD_END_MEMORY_JSON)
    execution_capability = execution_capability or {}
    defense_readjudication = defense_readjudication or _load(DEFENSE_RESTRICTIVENESS_READJUDICATION)
    spatial_readjudication = spatial_readjudication or _load(SPATIAL_MEMORY_READJUDICATION)
    harnessbank_support_audit = harnessbank_support_audit or _load(HARNESSBANK_SUPPORT_AUDIT)
    skill_validation_scout = _load(SKILL_VALIDATION_SCOUT_JSON) if skill_validation_scout is None else skill_validation_scout
    skill_execution_capability = skill_execution_capability or {}
    ps = primary_state.get("summary") or {}
    defense_reduction = _load(DEFENSE_PRINCIPLE_REDUCTION_JSON)
    defense_reduction_certified = bool(
        defense_reduction.get("principle_dead_end_certified") is True
        and ((defense_reduction.get("principle_diagnosis") or {}).get("status")) == "PRINCIPLE_DEAD_END_CERTIFIED"
        and ((((defense_reduction.get("principle_diagnosis") or {}).get("counter_explanation") or {}).get("same_information_reduction_verified")) is True)
    )

    defense_closure = defense_readjudication.get("fresh_phenomenon_closure") or {}
    defense_diagnosis = ((defense_readjudication.get("principle_diagnosis") or {}).get("counter_explanation") or {})
    defense_principle_closed = bool(
        defense_readjudication.get("principle_dead_end_certified") is True
        and defense_readjudication.get("experiment_run_for_this_readjudication") is False
        and defense_closure.get("source_ref") == "arXiv:2608.12977"
        and str(defense_closure.get("closure_scope") or "").strip()
        and defense_diagnosis.get("same_information_or_scope_matched") is True
        and defense_diagnosis.get("same_information_reduction_verified") is True
        and defense_diagnosis.get("positive_support") is True
        and ((defense_readjudication.get("authority") or {}).get("experiment_alone_authorizes_dead_end") is False)
    )
    spatial_closure = spatial_readjudication.get("fresh_phenomenon_closure") or {}
    spatial_diagnosis = ((spatial_readjudication.get("principle_diagnosis") or {}).get("counter_explanation") or {})
    spatial_principle_closed = bool(
        spatial_readjudication.get("principle_dead_end_certified") is True
        and spatial_readjudication.get("experiment_run_for_this_readjudication") is False
        and spatial_closure.get("source_ref") == "arXiv:2608.12743"
        and str(spatial_closure.get("closure_scope") or "").strip()
        and spatial_diagnosis.get("same_information_or_scope_matched") is True
        and spatial_diagnosis.get("same_information_reduction_verified") is True
        and spatial_diagnosis.get("positive_support") is True
        and ((spatial_readjudication.get("authority") or {}).get("experiment_alone_authorizes_dead_end") is False)
    )

    echo_signal = evidence_echo.get("observed_signal") or {}
    echo_f0 = evidence_echo.get("next_f0") or {}
    echo_repair = _load(EVIDENCE_ECHO_F0_REPAIR)
    echo_repair_source = echo_repair.get("source_state") or {}
    echo_reviewer = echo_repair.get("independent_review") or {}
    echo_repair_clear = bool(
        _sha(EVIDENCE_ECHO_F0_REPAIR) == EXPECTED_EVIDENCE_ECHO_F0_REPAIR_SHA256
        and echo_repair.get("status") == "CLEAR_FOR_BOUNDED_F0_EXECUTION"
        and echo_repair.get("pre_execution_only") is True
        and echo_repair.get("model_outcomes_inspected_before_repair") is False
        and echo_repair_source.get("original_runtime_sha256") == EXPECTED_EVIDENCE_ECHO_F0_ORIGINAL_SHA256
        and echo_repair_source.get("repaired_runtime_sha256") == EXPECTED_EVIDENCE_ECHO_F0_REVIEWED_SHA256
        and echo_reviewer.get("verdict") == "CLEAR_FOR_EXECUTION"
        and echo_reviewer.get("same_scientific_object") is True
        and echo_reviewer.get("unit_arm_gate_identity_preserved") is True
        and echo_reviewer.get("outcome_blind_repair") is True
        and echo_reviewer.get("new_information_advantage_created") is False
        and echo_reviewer.get("hidden_tuning_detected") is False
        and not list(echo_reviewer.get("blockers") or [])
    )
    echo_guard = _load(EVIDENCE_ECHO_F0_GOVERNANCE_GUARD)
    echo_guard_source = echo_guard.get("source_state") or {}
    echo_guard_rule = echo_guard.get("guard") or {}
    echo_guard_clear = bool(
        _sha(EVIDENCE_ECHO_F0_GOVERNANCE_GUARD) == EXPECTED_EVIDENCE_ECHO_F0_GOVERNANCE_GUARD_SHA256
        and echo_guard.get("status") == "PREMODEL_EXECUTION_CAPABILITY_ENFORCED"
        and echo_guard.get("pre_execution_only") is True
        and echo_guard.get("model_outcomes_inspected_during_guard_repair") is False
        and echo_guard.get("scientific_treatment_changed") is False
        and echo_guard_source.get("reviewed_scientific_runtime_sha256") == EXPECTED_EVIDENCE_ECHO_F0_REVIEWED_SHA256
        and echo_guard_source.get("guarded_runtime_sha256") == EXPECTED_EVIDENCE_ECHO_F0_GUARDED_SHA256
        and echo_guard_source.get("repaired_plan_canonical_sha256") == EXPECTED_EVIDENCE_ECHO_F0_PLAN_SHA256
        and _sha(EVIDENCE_ECHO_F0) == EXPECTED_EVIDENCE_ECHO_F0_GUARDED_SHA256
        and echo_guard_rule.get("plan_hash_checked_before_model_load") is True
        and echo_guard_rule.get("active_experiment_authority_required_before_model_load") is True
        and echo_guard_rule.get("matching_active_gpu_lease_required_before_model_load") is True
        and echo_guard_rule.get("visible_gpu_uuid_set_must_equal_leased_gpu_uuid_set") is True
        and echo_guard_rule.get("runner_can_acquire_authority") is False
        and echo_guard_rule.get("runner_can_acquire_gpu_lease") is False
    )
    echo_result_integrity = evidence_echo_f0_result.get("execution_integrity") or {}
    echo_result_binding = evidence_echo_f0_result.get("frozen_contract") or {}
    echo_result_gate = evidence_echo_f0_result.get("preregistered_gate_diagnosis") or {}
    echo_f0_reduced = bool(
        evidence_echo_f0_result.get("candidate_id") == "PA-01-EVIDENCE-ECHO"
        and evidence_echo_f0_result.get("execution_status") == "AUTHORIZED_BOUNDED_F0_EXECUTION_COMPLETED"
        and evidence_echo_f0_result.get("scientific_status") == "STOP_GENERIC_PROMPT_REDUCTION_NOT_BEATEN"
        and _sha(EVIDENCE_ECHO_F0_RESULT) == EXPECTED_EVIDENCE_ECHO_F0_RESULT_SHA256
        and echo_result_binding.get("runtime_sha256") == EXPECTED_EVIDENCE_ECHO_F0_REVIEWED_SHA256
        and echo_result_binding.get("operationalization_repair_sha256") == EXPECTED_EVIDENCE_ECHO_F0_REPAIR_SHA256
        and int(echo_result_integrity.get("rc") if echo_result_integrity.get("rc") is not None else -1) == 0
        and int(echo_result_integrity.get("units") or 0) == 96
        and int(echo_result_integrity.get("rows") or 0) == 480
        and int(echo_result_integrity.get("unanswerable_units") or 0) == 64
        and int(echo_result_integrity.get("answerable_units") or 0) == 32
        and echo_result_integrity.get("unauthorized_prior_rows_reused") is False
        and echo_result_integrity.get("permit_status") == "consumed-completed"
        and echo_result_integrity.get("experiment_authority_released") is True
        and echo_result_integrity.get("gpu_lease_released") is True
        and echo_result_gate.get("strongest_generic_reduction_beaten") is False
        and echo_result_gate.get("echo_specific_effect_threshold_met") is False
        and evidence_echo_f0_result.get("scientific_authority") is False
    )
    echo_design_ready = bool(
        not echo_f0_reduced
        and evidence_echo.get("decision") == "KEEP_AS_ACTIVE_F0_NOT_PAPER_IDEA"
        and int((evidence_echo.get("scope") or {}).get("units") or 0) >= 128
        and int(echo_signal.get("naive_summary_induced_false_answers") or 0) >= 7
        and int(echo_signal.get("naive_summary_fixed_false_answers") or 0) == 0
        and float(echo_signal.get("naive_summary_exact_paired_p") or 1.0) <= 0.05
        and len(echo_f0.get("required_arms") or []) >= 5
        and echo_f0.get("gpu_authorized") is False
        and echo_repair_clear
        and echo_guard_clear
    )
    echo_execution_ready = bool(
        echo_design_ready
        and execution_capability.get("controller_verified") is True
        and execution_capability.get("valid") is True
        and execution_capability.get("idea_id") == "PA-01-EVIDENCE-ECHO"
        and execution_capability.get("plan_hash") == EXPECTED_EVIDENCE_ECHO_F0_PLAN_SHA256
        and str(execution_capability.get("authority_id") or "")
        and str(execution_capability.get("run_id") or "")
        and str(execution_capability.get("server_id") or "")
        and len(list(execution_capability.get("gpu_lease_ids") or [])) > 0
    )

    skill_scout_errors = validate_skill_validation_transfer_scout(skill_validation_scout) if skill_validation_scout else ["missing-scout-receipt"]
    skill_f0 = skill_validation_scout.get("f0") or {}
    skill_env = skill_validation_scout.get("execution_environment") or {}
    skill_design_ready = bool(
        not skill_scout_errors
        and skill_f0.get("design_ready") is True
        and int(skill_f0.get("families") or 0) == 30
        and skill_f0.get("arms") == ["raw_trajectory_rag", "selfgen_experience_always"]
        and int(skill_f0.get("model_calls_executed") or 0) == 0
        and int(skill_f0.get("task_trials_executed") or 0) == 0
    )
    # PA-05's frozen execution substrate is API + Docker. It does not load a local
    # model or consume CUDA, so a GPU lease would be an unrelated capability. The
    # controller-issued experiment authority remains mandatory, while vague generic
    # resource_lease_ids are deliberately rejected rather than accepted as unverifiable
    # strings. Any later GPU-backed revision is a new execution contract.
    skill_execution_ready = bool(
        skill_design_ready
        and skill_env.get("execution_ready") is True
        and skill_execution_capability.get("controller_verified") is True
        and skill_execution_capability.get("valid") is True
        and skill_execution_capability.get("idea_id") == "PA-05-SKILL-VALIDATION-TRANSFER"
        and skill_execution_capability.get("plan_hash") == skill_f0.get("plan_sha256")
        and skill_execution_capability.get("execution_kind") == "api_docker"
        and skill_execution_capability.get("requires_gpu") is False
        and not list(skill_execution_capability.get("gpu_lease_ids") or [])
        and not list(skill_execution_capability.get("resource_lease_ids") or [])
        and str(skill_execution_capability.get("authority_id") or "")
        and str(skill_execution_capability.get("run_id") or "")
        and str(skill_execution_capability.get("server_id") or "")
    )

    harness_hold = _memory_hold(dead_end_memory, "SHADOW-P07-C01")
    defense_hold = _memory_hold(dead_end_memory, "SHADOW-P11-C02")
    spatial_hold = next(
        (
            row
            for row in ((dead_end_memory.get("shadow_dead_end_memory") or {}).get("hold_objects") or [])
            if isinstance(row, dict)
            and str(row.get("title") or "").startswith("Procedural-composition transfer-calibration boundary")
        ),
        {},
    )

    candidates = [
        _candidate(
            candidate_id="PA-01-EVIDENCE-ECHO",
            title=str(evidence_echo.get("title") or "Evidence Echo in Agent Notes"),
            source_refs=[str(evidence_echo.get("source_primary_ref") or "arXiv:2608.07527")],
            phenomenon=(
                "On 64 benchmark-unanswerable units with raw visible pages locked across policies, "
                "adding an extractive persistent note raised false-answer rate from 10.9% to 21.9%; "
                "the paired naive-summary transition was 7 induced versus 0 repaired false answers "
                "(exact p=0.015625), with zero net exact-accuracy gain on the 64 answerable units."
            ),
            strongest_reduction=(
                "generic prompt salience/repetition, correlated-evidence double counting, extra decision "
                "opportunity, context-length effects, or ordinary calibration shift under redundant context"
            ),
            cheapest_falsifier=(
                "Keep raw pages, retrieval ranking, model, temperature, and two-step budget fixed; compare "
                "RAW_ONLY vs ECHO_EXTRACTIVE vs VERBATIM_DUPLICATE vs TOKEN_MATCHED_NEUTRAL vs DEDUP_WARNING "
                "on the frozen unanswerable/answerable units."
            ),
            support_status=(
                "F0_REDUCED_BY_GENERIC_PROMPT_EFFECT"
                if echo_f0_reduced
                else ("PROVENANCE_AUDITED_LOCAL_SUBSTRATE" if echo_design_ready else "INCOMPLETE_RECEIPT")
            ),
            status=(
                "STOP_REDUCTION"
                if echo_f0_reduced
                else ("ACTIVE_F0" if echo_execution_ready else ("HOLD_EXECUTION" if echo_design_ready else "HOLD_SUPPORT"))
            ),
            priority=100,
            why_now=(
                "The authorized five-arm F0 is complete and does not support a distinct Evidence-Echo mechanism: "
                "ECHO_EXTRACTIVE is only +3.125pp over RAW_ONLY/TOKEN_MATCHED_NEUTRAL with paired p=0.6875, while "
                "VERBATIM_DUPLICATE is +9.375pp with paired p=0.03125 and DEDUP_WARNING does not recover safety."
                if echo_f0_reduced
                else "This is the only current scout with a real matched substrate, a nonzero paired residual, and a falsifier that changes one representation axis without requiring a new benchmark."
            ),
            substrate={
                "host": ((evidence_echo.get("source_substrate") or {}).get("host")),
                "run": ((evidence_echo.get("source_substrate") or {}).get("run")),
                "aggregate_jsonl_sha256": ((evidence_echo.get("source_substrate") or {}).get("aggregate_jsonl_sha256")),
                "raw_visible_pages_locked_across_policies": ((evidence_echo.get("source_substrate") or {}).get("raw_visible_pages_locked_across_policies")),
                "second_retrieval_ranking_locked_across_active_policies": ((evidence_echo.get("source_substrate") or {}).get("second_retrieval_ranking_locked_across_active_policies")),
            },
            evidence=(
                {
                    "f0_scientific_status": evidence_echo_f0_result.get("scientific_status"),
                    "false_answer_rate": evidence_echo_f0_result.get("false_answer_rate"),
                    "effects": evidence_echo_f0_result.get("effects"),
                    "paired_tests": evidence_echo_f0_result.get("paired_tests"),
                    "analysis_sha256": echo_result_binding.get("analysis_sha256"),
                    "rows_sha256": echo_result_binding.get("rows_sha256"),
                }
                if echo_f0_reduced
                else {
                    "baseline_false_answer_rate": echo_signal.get("negative_evidence_baseline_unanswerable_false_answer_rate"),
                    "naive_summary_false_answer_rate": echo_signal.get("naive_summary_unanswerable_false_answer_rate"),
                    "induced_false": echo_signal.get("naive_summary_induced_false_answers"),
                    "repaired_false": echo_signal.get("naive_summary_fixed_false_answers"),
                    "paired_p": echo_signal.get("naive_summary_exact_paired_p"),
                    "answerable_exact_net_delta": echo_signal.get("naive_summary_answerable_exact_net_delta"),
                }
            ),
            reopen_only_if=(
                "Reopen only with a preregistered matched intervention that holds evidence content, repetition count, token budget, ordering, and generic instruction effects fixed while changing only the hypothesized representation, and shows a replicated residual plus mechanism-specific recovery."
                if echo_f0_reduced
                else "Execution requires a controller-verified experiment authority bound to the repaired F0 plan plus matching active GPU lease(s), with CUDA-visible GPU UUIDs exactly covered by those leases. If the F0 is reduced by token-matched neutral padding or the paired effect disappears, archive. If redundant evidence remains uniquely harmful and DEDUP_WARNING selectively recovers safety, then run current-source collision review before any Problem-Gate submission."
            ),
        ),
        _candidate(
            candidate_id="PA-05-SKILL-VALIDATION-TRANSFER",
            title="Does Local Skill Validation Identify Deployment-Time Procedural Transfer?",
            source_refs=["arXiv:2605.24117", "arXiv:2603.25158", "arXiv:2605.23904", "arXiv:2605.08693", "arXiv:2603.02766"],
            phenomenon=(
                "SkillEvolBench supplies 30 matched latent families with T1-T3 acquisition/replay and frozen T4 context-shift, "
                "T5 adversarial, and T6 composition deployment. Current skill-evolution systems commonly use local/held-out validation "
                "or related probe utility to accept/select skill edits, while SkillEvolBench reports that raw trajectory reuse can outperform "
                "distilled skills and that skill gains are unstable under frozen deployment. The unresolved object is whether local validation "
                "is an identifying selection statistic for which persistent representation actually transfers."
            ),
            strongest_reduction=(
                "one representation globally dominates; ordinary family difficulty; raw trajectories are simply globally stronger; "
                "local replay already predicts deployment; or one-seed model variance explains apparent inversions"
            ),
            cheapest_falsifier=(
                "On the exact SkillEvolBench commit, run only raw_trajectory_rag and selfgen_experience_always with one model and seed A. "
                "For each of 30 families, compare frozen T1-T3 within-env replay preference with T4-T6 deployment preference. Require both arms "
                "to win nontrivial family subsets, >=10 joint-decisive families, >=40% preference inversions, and a bootstrap-positive oracle-vs-local "
                "selection regret while local selection fails to beat the best global arm by >0.03."
            ),
            support_status="PROVENANCE_AUDITED_FIRST_PARTY_EXECUTABLE_SUBSTRATE" if skill_design_ready else "INCOMPLETE_RECEIPT",
            status="ACTIVE_F0" if skill_execution_ready else ("HOLD_EXECUTION" if skill_design_ready else "HOLD_SUPPORT"),
            priority=90,
            why_now=(
                "Unlike source-only scouts, this direction has an exact first-party benchmark commit, 180 validated tasks, two matched canonical arms, "
                "a 270-task dry-run for each arm, per-family replay/deployment truth, and a frozen analyzer. It is held only by execution environment/authority."
            ),
            substrate={
                "repository": ((skill_validation_scout.get("source") or {}).get("repository")),
                "commit_sha": ((skill_validation_scout.get("source") or {}).get("commit_sha")),
                "archive_sha256": ((skill_validation_scout.get("source") or {}).get("archive_sha256")),
                "tasks": (((skill_validation_scout.get("source") or {}).get("asset_validation") or {}).get("tasks")),
                "families": skill_f0.get("families"),
                "tasks_per_arm": skill_f0.get("tasks_per_arm"),
                "primary_tasks_per_arm": skill_f0.get("primary_tasks_per_arm"),
                "learning_replays_per_arm": skill_f0.get("learning_replays_per_arm"),
            },
            evidence={
                "design_ready": skill_design_ready,
                "plan_sha256": skill_f0.get("plan_sha256"),
                "harness_sha256": skill_f0.get("harness_sha256"),
                "current_source_boundary": ((skill_validation_scout.get("current_source_boundary") or {}).get("status")),
                "model_calls_executed": skill_f0.get("model_calls_executed"),
                "task_trials_executed": skill_f0.get("task_trials_executed"),
            },
            reopen_only_if=(
                (
                    f"On audited runtime host {skill_env.get('host')}, load the frozen Gemini credential shared by the agent and host-side SkillAuthor route, "
                    "then obtain a separate controller-issued execution capability bound to the frozen plan. A seed-A GO only authorizes seed-B replication plus "
                    "current-source review; it never authorizes Problem Gate, method design, or full experiments by itself."
                )
                if skill_env.get("runtime_infrastructure_ready") is True
                else (
                    "Provision an exact first-party benchmark runtime (Harbor + agent-runtime image + strict preflight), then load the frozen Gemini credential "
                    "and obtain a separate controller-issued execution capability bound to the frozen plan. A seed-A GO only authorizes seed-B replication plus "
                    "current-source review; it never authorizes Problem Gate, method design, or full experiments by itself."
                )
            ),
        ),
        _candidate(
            candidate_id="PA-02-DEFENSE-RESTRICTIVENESS",
            title="Failure-Driven Defense Can Improve Security While Collapsing Utility",
            source_refs=["arXiv:2608.12977"],
            phenomenon=(
                "Under the same five-round defense-evolution budget, the reported backbone ablation lowers attack "
                "success while one backbone yields only 7.2% utility accuracy, showing a sharp security/utility mismatch."
            ),
            strongest_reduction="ordinary constrained optimization / security-utility Pareto trade-off and conservative policy bias",
            cheapest_falsifier=(
                "Requires paired evolution histories with matched current ASR/utility and candidate patch benefit but "
                "different accumulated restrictiveness; no such current released unit is available."
            ),
            support_status=(
                "PRINCIPLE_CLOSED_SAME_INFORMATION_REDUCTION"
                if defense_principle_closed
                else str(defense_hold.get("support_status") or "SUPPORT_UNAVAILABLE")
            ),
            status="STOP_REDUCTION" if defense_principle_closed else "HOLD_SUPPORT",
            priority=70,
            why_now=(
                "Scoped principle readjudication already reduces the reported 7.2% utility point to a same-information "
                "security-utility Pareto/overblocking operating point; spending compute on the same standalone claim is forbidden."
                if defense_principle_closed
                else "Strong quantitative failure boundary, but it must not consume compute before the required history-level asset exists."
            ),
            reopen_only_if=(
                str(defense_diagnosis.get("reopen_condition") or "")
                if defense_principle_closed
                else str(defense_hold.get("reopen_only_if") or "Author release exposes replayable evolution histories with rule/patch lineage.")
            ),
        ),
        _candidate(
            candidate_id="PA-03-HARNESS-SELECTION-INVERSION",
            title="Train-Selected Harnesses Need Not Be the Harnesses That Generalize Best",
            source_refs=["arXiv:2607.13683"],
            phenomenon=(
                "HarnessBank reports a GDPval train/test ranking disagreement and 62-76% phantom-progress rounds "
                "under weaker crediting rules after convergence, suggesting a selection-stability boundary."
            ),
            strongest_reduction="small-n ranking noise, winner's curse, adaptive validation, and ordinary selection bias",
            cheapest_falsifier=(
                "Sweep the frozen verification rule on released paired gene histories while matching candidate count, "
                "selection pressure, and deployment n; the required histories are not released."
            ),
            support_status=(
                str(harnessbank_support_audit.get("status") or "")
                if harnessbank_support_audit.get("candidate_id") == "PA-03-HARNESS-SELECTION-INVERSION"
                else str(harness_hold.get("support_status") or "SUPPORT_UNAVAILABLE")
            ),
            status="HOLD_SUPPORT",
            priority=60,
            why_now=(
                "Primary-source code disclosure remains future/conditional, and the bounded current release audit found no "
                "first-party replay substrate exposing the paired gene histories required to distinguish verification-selection inversion from survivorship/selection bias."
                if harnessbank_support_audit.get("status") == "HOLD_SUPPORT_NO_RELEASED_REQUIRED_UNIT"
                else "Potentially strong self-evolution-specific selection phenomenon, but support is still source-only."
            ),
            reopen_only_if=str(
                harnessbank_support_audit.get("reopen_only_if")
                or harness_hold.get("reopen_only_if")
                or "HarnessBank releases paired run histories/outcomes."
            ),
        ),
        _candidate(
            candidate_id="PA-04-SPATIAL-MEMORY-CONFLICT",
            title="High-Relevance Procedure Memory Can Still Fail When Visual Grounding or Procedure Compatibility Breaks",
            source_refs=["arXiv:2608.12743"],
            phenomenon=(
                "Spatial Memory Agent reports baseline and memory-agent failures even with high-quality relevant memories "
                "(TRS >= 0.6), separating memory relevance from executability/grounding."
            ),
            strongest_reduction="base-model visual grounding failure or ordinary retrieval/execution mismatch",
            cheapest_falsifier=(
                "Needs query-level retrieved lesson identities/text, TRS/relevance metadata, and outcomes to construct "
                "matched conflicting versus non-conflicting procedure sets."
            ),
            support_status=(
                "PRINCIPLE_CLOSED_VISUAL_GROUNDING_REDUCTION"
                if spatial_principle_closed
                else str(spatial_hold.get("support_status") or "SUPPORT_UNAVAILABLE")
            ),
            status="STOP_REDUCTION" if spatial_principle_closed else "HOLD_SUPPORT",
            priority=50,
            why_now=(
                "The primary paper itself isolates the cited TRS>=0.6 cases as base-model visual-grounding failures: both baseline and SMA fail after the response attempts to use the retrieved procedure. The high-relevance failure therefore does not establish a separate procedure-conflict mechanism."
                if spatial_principle_closed
                else "Good reserve phenomenon but no independent query-level support asset is currently available."
            ),
            reopen_only_if=(
                str(spatial_diagnosis.get("reopen_condition") or "")
                if spatial_principle_closed
                else str(spatial_hold.get("reopen_only_if") or "Authors release query-level retrieval logs and outcomes.")
            ),
        ),
    ]

    echo_row = next(row for row in candidates if row["candidate_id"] == "PA-01-EVIDENCE-ECHO")
    echo_row["f0_design_ready"] = echo_design_ready
    echo_row["execution_readiness"] = {
        "operationalization_ready": echo_design_ready,
        "controller_verified_capability_present": echo_execution_ready,
        "execution_ready": echo_execution_ready,
        "required_plan_sha256": EXPECTED_EVIDENCE_ECHO_F0_PLAN_SHA256,
        "active_experiment_authority_required": True,
        "matching_gpu_leases_required": True,
        "visible_gpu_uuid_set_must_equal_leased_gpu_uuid_set": True,
        "unauthorized_partial_run_ingestable": False,
        "status": "EXECUTION_READY" if echo_execution_ready else "HOLD_EXECUTION_AUTHORITY_REQUIRED",
    }
    skill_row = next(row for row in candidates if row["candidate_id"] == "PA-05-SKILL-VALIDATION-TRANSFER")
    skill_row["f0_design_ready"] = skill_design_ready
    skill_row["execution_readiness"] = {
        "operationalization_ready": skill_design_ready,
        "runtime_host": skill_env.get("host"),
        "runtime_environment_ready": bool(skill_env.get("runtime_infrastructure_ready")),
        "runtime_infrastructure_ready": bool(skill_env.get("runtime_infrastructure_ready")),
        "provider_credential_ready": bool(skill_env.get("provider_credential_ready")),
        "runtime_image_status": skill_env.get("runtime_image_status"),
        "controller_verified_capability_present": skill_execution_ready,
        "execution_ready": skill_execution_ready,
        "required_plan_sha256": skill_f0.get("plan_sha256"),
        "active_experiment_authority_required": True,
        "execution_kind": "api_docker",
        "requires_gpu": False,
        "matching_gpu_leases_required": False,
        "generic_resource_lease_ids_accepted": False,
        "unauthorized_partial_run_ingestable": False,
        "status": (
            "EXECUTION_READY"
            if skill_execution_ready
            else (
                "HOLD_CONTROLLER_AUTHORITY_REQUIRED"
                if skill_env.get("execution_ready") is True
                else (
                    "HOLD_PROVIDER_CREDENTIAL_AND_AUTHORITY_REQUIRED"
                    if skill_env.get("runtime_infrastructure_ready") is True
                    and skill_env.get("provider_credential_ready") is not True
                    else "HOLD_RUNTIME_INFRASTRUCTURE_AND_AUTHORITY_REQUIRED"
                )
            )
        ),
        "hold_reason": list(skill_env.get("hold_reason") or []),
    }

    active = [row for row in candidates if row["status"] == "ACTIVE_F0"]
    if len(active) > ACTIVE_F0_LIMIT:
        active.sort(key=lambda row: (-int(row.get("priority") or 0), row["candidate_id"]))
        keep = {row["candidate_id"] for row in active[:ACTIVE_F0_LIMIT]}
        for row in candidates:
            if row["status"] == "ACTIVE_F0" and row["candidate_id"] not in keep:
                row["status"] = "SCOUT_ASSET"
                row["why_now"] += " Demoted because the single ACTIVE_F0 slot is already occupied by a higher-priority matched substrate."

    summary = {
        "candidates": len(candidates),
        "active_f0": sum(row["status"] == "ACTIVE_F0" for row in candidates),
        "design_ready_f0": sum(bool(row.get("f0_design_ready")) for row in candidates),
        "scout_asset": sum(row["status"] == "SCOUT_ASSET" for row in candidates),
        "hold_support": sum(row["status"] == "HOLD_SUPPORT" for row in candidates),
        "hold_execution": sum(row["status"] == "HOLD_EXECUTION" for row in candidates),
        "hold_reduction": sum(row["status"] == "HOLD_REDUCTION" for row in candidates),
        "ready_for_problem_review": sum(row["status"] == "READY_FOR_PROBLEM_REVIEW" for row in candidates),
        "stop_reduction": sum(row["status"] == "STOP_REDUCTION" for row in candidates),
        "primary_verified": int(ps.get("verified") or 0),
        "primary_empirical_fact_candidates": int(ps.get("empirical_fact_candidates") or 0),
        "canonical_problem_gate_added": 0,
        "method_authorized": 0,
        "experiment_authorized": 0,
        "p0_authorized": 0,
        "gpu_authorized": 0,
    }

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": _now(),
        "status": "ACTIVE_F0_EXISTS" if summary["active_f0"] else ("F0_EXECUTION_HOLD" if summary["hold_execution"] else "NO_ACTIVE_F0"),
        "policy": {
            "portfolio_is_outside_canonical_problem_queue": True,
            "fresh_quantitative_phenomenon_precedes_method_ideation": True,
            "one_active_f0_slot_max": ACTIVE_F0_LIMIT,
            "active_f0_requires_provenance_audited_substrate": True,
            "active_f0_requires_frozen_same_information_falsifier": True,
            "active_f0_requires_controller_verified_execution_capability": True,
            "direct_gpu_execution_without_experiment_authority_and_matching_leases_is_forbidden": True,
            "non_gpu_api_docker_f0_requires_experiment_authority_but_not_gpu_lease": True,
            "unverifiable_generic_resource_lease_ids_are_not_execution_authority": True,
            "unauthorized_partial_runs_cannot_be_ingested_as_f0_evidence": True,
            "preexecution_operationalization_repair_requires_hash_chain_and_independent_review": True,
            "source_only_candidates_cannot_consume_experiment_slot": True,
            "multiple_design_ready_f0s_may_wait_behind_one_execution_slot": True,
            "support_unavailable_is_hold_not_scientific_failure": True,
            "positive_f0_does_not_grant_problem_gate_or_paper_design": True,
            "f0_must_test_strongest_generic_reduction_before_novelty_claim": True,
            "failed_f0_is_archived_as_negative_search_control": True,
            "paper_problem_claim_requires_separate_current_source_collision_review": True,
            "scientific_authority": False,
        },
        "summary": summary,
        "candidates": sorted(candidates, key=lambda row: (-int(row["priority"]), row["candidate_id"])),
        "source_bindings": {
            "evidence_echo_receipt": {
                "path": str(EVIDENCE_ECHO_JSON.relative_to(PROJECT_ROOT)),
                "sha256": _sha(EVIDENCE_ECHO_JSON),
            },
            "evidence_echo_f0_harness": {
                "path": str(EVIDENCE_ECHO_F0.relative_to(PROJECT_ROOT)),
                "sha256": _sha(EVIDENCE_ECHO_F0),
            },
            "evidence_echo_f0_operationalization_repair": {
                "path": str(EVIDENCE_ECHO_F0_REPAIR.relative_to(PROJECT_ROOT)),
                "sha256": _sha(EVIDENCE_ECHO_F0_REPAIR),
                "review_verdict": echo_reviewer.get("verdict"),
            },
            "evidence_echo_f0_governance_guard": {
                "path": str(EVIDENCE_ECHO_F0_GOVERNANCE_GUARD.relative_to(PROJECT_ROOT)),
                "sha256": _sha(EVIDENCE_ECHO_F0_GOVERNANCE_GUARD),
                "status": echo_guard.get("status"),
                "guarded_runtime_sha256": echo_guard_source.get("guarded_runtime_sha256"),
                "repaired_plan_canonical_sha256": echo_guard_source.get("repaired_plan_canonical_sha256"),
            },
            "evidence_echo_f0_authorized_result": {
                "path": str(EVIDENCE_ECHO_F0_RESULT.relative_to(PROJECT_ROOT)),
                "sha256": _sha(EVIDENCE_ECHO_F0_RESULT),
                "scientific_status": evidence_echo_f0_result.get("scientific_status"),
                "execution_complete": evidence_echo_f0_result.get("execution_status") == "AUTHORIZED_BOUNDED_F0_EXECUTION_COMPLETED",
                "generic_reduction_beaten": echo_result_gate.get("strongest_generic_reduction_beaten"),
            },
            "defense_restrictiveness_principle_readjudication": {
                "path": str(DEFENSE_RESTRICTIVENESS_READJUDICATION.relative_to(PROJECT_ROOT)),
                "sha256": _sha(DEFENSE_RESTRICTIVENESS_READJUDICATION),
                "principle_dead_end_certified": defense_readjudication.get("principle_dead_end_certified") is True,
                "same_information_reduction_verified": defense_diagnosis.get("same_information_reduction_verified") is True,
            },
            "spatial_memory_principle_readjudication": {
                "path": str(SPATIAL_MEMORY_READJUDICATION.relative_to(PROJECT_ROOT)),
                "sha256": _sha(SPATIAL_MEMORY_READJUDICATION),
                "principle_dead_end_certified": spatial_readjudication.get("principle_dead_end_certified") is True,
                "same_information_reduction_verified": spatial_diagnosis.get("same_information_reduction_verified") is True,
            },
            "harnessbank_support_audit": {
                "path": str(HARNESSBANK_SUPPORT_AUDIT.relative_to(PROJECT_ROOT)),
                "sha256": _sha(HARNESSBANK_SUPPORT_AUDIT),
                "status": harnessbank_support_audit.get("status"),
                "required_unit": harnessbank_support_audit.get("required_unit"),
            },
            "primary_state": {
                "path": str(PRIMARY_STATE_JSON.relative_to(PROJECT_ROOT)),
                "sha256": _sha(PRIMARY_STATE_JSON),
            },
            "dead_end_memory": {
                "path": str(DEAD_END_MEMORY_JSON.relative_to(PROJECT_ROOT)),
                "sha256": _sha(DEAD_END_MEMORY_JSON),
            },
            "defense_principle_reduction": {
                "path": str(DEFENSE_PRINCIPLE_REDUCTION_JSON.relative_to(PROJECT_ROOT)),
                "sha256": _sha(DEFENSE_PRINCIPLE_REDUCTION_JSON),
                "certified": defense_reduction_certified,
            },
            "skill_validation_transfer_scout": {
                "path": str(SKILL_VALIDATION_SCOUT_JSON.relative_to(PROJECT_ROOT)),
                "sha256": _sha(SKILL_VALIDATION_SCOUT_JSON),
                "status": skill_validation_scout.get("status"),
                "plan_sha256": skill_f0.get("plan_sha256"),
            },
            "skill_validation_transfer_f0_harness": {
                "path": str(SKILL_VALIDATION_F0_HARNESS.relative_to(PROJECT_ROOT)),
                "sha256": _sha(SKILL_VALIDATION_F0_HARNESS),
            },
        },
        "scientific_authority": False,
    }


def validate_fresh_phenomenon_portfolio(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    policy = state.get("policy") or {}
    summary = state.get("summary") or {}
    rows = [row for row in state.get("candidates") or [] if isinstance(row, dict)]
    if state.get("scientific_authority") is not False:
        errors.append("portfolio cannot carry scientific authority")
    if policy.get("portfolio_is_outside_canonical_problem_queue") is not True:
        errors.append("portfolio must stay outside canonical problem queue")
    if policy.get("active_f0_requires_provenance_audited_substrate") is not True:
        errors.append("active F0 must require audited substrate")
    if policy.get("active_f0_requires_controller_verified_execution_capability") is not True:
        errors.append("active F0 must require controller-verified execution capability")
    if policy.get("direct_gpu_execution_without_experiment_authority_and_matching_leases_is_forbidden") is not True:
        errors.append("direct GPU execution must remain behind experiment authority and resource leases")
    if policy.get("non_gpu_api_docker_f0_requires_experiment_authority_but_not_gpu_lease") is not True:
        errors.append("non-GPU API/Docker F0 must require experiment authority without inventing a GPU lease")
    if policy.get("unverifiable_generic_resource_lease_ids_are_not_execution_authority") is not True:
        errors.append("generic resource lease ids cannot substitute for verified execution authority")
    if policy.get("unauthorized_partial_runs_cannot_be_ingested_as_f0_evidence") is not True:
        errors.append("unauthorized partial runs must remain non-ingestable")
    if policy.get("preexecution_operationalization_repair_requires_hash_chain_and_independent_review") is not True:
        errors.append("F0 operationalization repair must require a frozen hash chain plus independent review")
    if policy.get("source_only_candidates_cannot_consume_experiment_slot") is not True:
        errors.append("source-only candidate may not consume F0 slot")
    if policy.get("positive_f0_does_not_grant_problem_gate_or_paper_design") is not True:
        errors.append("positive F0 cannot grant downstream scientific authority")
    active = [row for row in rows if row.get("status") == "ACTIVE_F0"]
    if len(active) > ACTIVE_F0_LIMIT:
        errors.append("too many ACTIVE_F0 candidates")
    if int(summary.get("active_f0") or 0) != len(active):
        errors.append("ACTIVE_F0 summary mismatch")
    execution_holds = [row for row in rows if row.get("status") == "HOLD_EXECUTION"]
    if int(summary.get("hold_execution") or 0) != len(execution_holds):
        errors.append("HOLD_EXECUTION summary mismatch")
    if int(summary.get("design_ready_f0") or 0) != sum(bool(row.get("f0_design_ready")) for row in rows):
        errors.append("design-ready F0 summary mismatch")
    if int(summary.get("candidates") or 0) != len(rows):
        errors.append("candidate summary mismatch")
    bindings = state.get("source_bindings") or {}
    repair_binding = bindings.get("evidence_echo_f0_operationalization_repair") or {}
    guard_binding = bindings.get("evidence_echo_f0_governance_guard") or {}
    echo_rows = [row for row in rows if row.get("candidate_id") == "PA-01-EVIDENCE-ECHO"]
    if echo_rows and echo_rows[0].get("f0_design_ready") is True:
        if repair_binding.get("sha256") != EXPECTED_EVIDENCE_ECHO_F0_REPAIR_SHA256 or repair_binding.get("review_verdict") != "CLEAR_FOR_EXECUTION":
            errors.append("design-ready Evidence Echo F0 lacks the reviewed operationalization-repair binding")
        if (
            guard_binding.get("sha256") != EXPECTED_EVIDENCE_ECHO_F0_GOVERNANCE_GUARD_SHA256
            or guard_binding.get("status") != "PREMODEL_EXECUTION_CAPABILITY_ENFORCED"
            or guard_binding.get("guarded_runtime_sha256") != EXPECTED_EVIDENCE_ECHO_F0_GUARDED_SHA256
            or guard_binding.get("repaired_plan_canonical_sha256") != EXPECTED_EVIDENCE_ECHO_F0_PLAN_SHA256
        ):
            errors.append("design-ready Evidence Echo F0 lacks the execution-governance guard binding")
    skill_binding = bindings.get("skill_validation_transfer_scout") or {}
    skill_harness_binding = bindings.get("skill_validation_transfer_f0_harness") or {}
    skill_rows = [row for row in rows if row.get("candidate_id") == "PA-05-SKILL-VALIDATION-TRANSFER"]
    if skill_rows and skill_rows[0].get("f0_design_ready") is True:
        bound_skill_scout = _load(SKILL_VALIDATION_SCOUT_JSON)
        skill_f0 = bound_skill_scout.get("f0") or {}
        if (
            validate_skill_validation_transfer_scout(bound_skill_scout)
            or skill_binding.get("sha256") != _sha(SKILL_VALIDATION_SCOUT_JSON)
            or skill_binding.get("status") != bound_skill_scout.get("status")
            or skill_binding.get("plan_sha256") != skill_f0.get("plan_sha256")
        ):
            errors.append("design-ready Skill Validation Transfer F0 lacks the bound scout receipt")
        if skill_harness_binding.get("sha256") != _sha(SKILL_VALIDATION_F0_HARNESS):
            errors.append("design-ready Skill Validation Transfer F0 lacks the bound analyzer")
        if (skill_rows[0].get("evidence") or {}).get("plan_sha256") != skill_f0.get("plan_sha256"):
            errors.append("Skill Validation Transfer candidate plan binding drift")
        skill_readiness = skill_rows[0].get("execution_readiness") or {}
        if not str(skill_readiness.get("runtime_host") or "").strip():
            errors.append("Skill Validation Transfer runtime host is missing")
        if skill_readiness.get("runtime_environment_ready") is not skill_readiness.get("runtime_infrastructure_ready"):
            errors.append("Skill Validation Transfer runtime environment/infrastructure readiness drift")
        if skill_readiness.get("runtime_infrastructure_ready") is True and skill_readiness.get("runtime_image_status") != "PRESENT":
            errors.append("Skill Validation Transfer infrastructure-ready state lacks a present runtime image")
        if skill_readiness.get("status") == "HOLD_PROVIDER_CREDENTIAL_AND_AUTHORITY_REQUIRED" and not (
            skill_readiness.get("runtime_infrastructure_ready") is True
            and skill_readiness.get("provider_credential_ready") is False
        ):
            errors.append("Skill Validation Transfer provider-credential hold is inconsistent")
    for row in rows:
        if row.get("status") not in ALLOWED_STATUSES:
            errors.append(f"invalid status:{row.get('candidate_id')}")
        if row.get("scientific_authority") is not False or row.get("paper_problem_claimed") is not False:
            errors.append(f"candidate illegally carries scientific claim authority:{row.get('candidate_id')}")
        authority = row.get("authority") or {}
        if any(bool(authority.get(key)) for key in ("problem_gate", "paper_design", "method", "experiment", "p0", "gpu", "full_experiment")):
            errors.append(f"candidate illegally carries downstream authority:{row.get('candidate_id')}")
        if row.get("status") in {"ACTIVE_F0", "HOLD_EXECUTION"}:
            if row.get("support_status") not in AUDITED_SUBSTRATE_STATUSES:
                errors.append(f"design-ready F0 lacks audited substrate:{row.get('candidate_id')}")
            if not str(row.get("cheapest_falsifier") or "").strip():
                errors.append(f"design-ready F0 lacks falsifier:{row.get('candidate_id')}")
        if row.get("status") == "ACTIVE_F0":
            readiness = row.get("execution_readiness") or {}
            if readiness.get("controller_verified_capability_present") is not True or readiness.get("execution_ready") is not True:
                errors.append(f"ACTIVE_F0 lacks controller-verified execution capability:{row.get('candidate_id')}")
            if row.get("candidate_id") == "PA-05-SKILL-VALIDATION-TRANSFER" and (
                readiness.get("execution_kind") != "api_docker"
                or readiness.get("requires_gpu") is not False
                or readiness.get("matching_gpu_leases_required") is not False
                or readiness.get("generic_resource_lease_ids_accepted") is not False
            ):
                errors.append("Skill Validation Transfer execution contract drift")
        if row.get("status") == "HOLD_EXECUTION":
            readiness = row.get("execution_readiness") or {}
            if readiness.get("execution_ready") is not False or readiness.get("unauthorized_partial_run_ingestable") is not False:
                errors.append(f"HOLD_EXECUTION readiness drift:{row.get('candidate_id')}")
    if int(summary.get("canonical_problem_gate_added") or 0) != 0:
        errors.append("portfolio cannot add canonical Problem-Gate rows")
    if any(int(summary.get(key) or 0) != 0 for key in ("method_authorized", "experiment_authorized", "p0_authorized", "gpu_authorized")):
        errors.append("portfolio cannot authorize downstream execution")
    return errors


def write_fresh_phenomenon_portfolio(
    *,
    json_path: Path = DEFAULT_JSON,
    js_path: Path = DEFAULT_JS,
) -> dict[str, Any]:
    state = build_fresh_phenomenon_portfolio()
    errors = validate_fresh_phenomenon_portfolio(state)
    if errors:
        raise ValueError("; ".join(errors))
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.PAPER_FIRST_FRESH_PHENOMENON_PORTFOLIO = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    print(json.dumps(write_fresh_phenomenon_portfolio(), ensure_ascii=False, indent=2))
