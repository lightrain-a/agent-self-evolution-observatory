from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .paper_first_design_adjudication import build_paper_first_design_adjudication

DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-pf2-method-design.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "paper-first-pf2-method-design.js"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_pf2_method_design() -> dict[str, Any]:
    adjudication = build_paper_first_design_adjudication()
    pf2 = next(row for row in adjudication["rows"] if row["id"] == "PF-2")
    if pf2["verdict"] != "ADVANCE_TO_METHOD_DESIGN":
        raise RuntimeError("PF-2 revised paper problem is not authorized to enter method design")
    if pf2["paper_problem_id"] != "repair-surface-identifiability-under-persistent-agent-updates":
        raise RuntimeError("PF-2 method design must use the repair-surface-identifiability revision")

    return {
        "schema_version": "2.0",
        "generated_at": _now(),
        "paper_id": "repair-surface-identifiability-under-persistent-agent-updates",
        "incubation_id": "PF-2",
        "method_name": "Repair-Surface Identification Certificate",
        "short_name": "RSIC",
        "method_status": "METHOD_DESIGN_DRAFT_AWAITING_INDEPENDENT_PREMORTEM",
        "paper_problem": pf2["paper_problem"],
        "novelty_boundary": pf2["irreducible_boundary"],
        "method_thesis": (
            "A failed trace and even a causally responsible module need not identify where a persistent repair should be committed. "
            "RSIC represents the set of repair-surface causal models still compatible with pre-intervention evidence and reversible probe outcomes, "
            "certifies a surface only when every compatible model agrees on the same minimal sufficient repair locus, and otherwise abstains or requests additional reversible evidence."
        ),
        "formal_objects": {
            "failure_context": "x = (task state, failed trajectory, versioned agent artifacts, external environment facts) observed before any candidate persistent repair outcome is opened",
            "surface_set": "S = {prompt/context, memory/skill, workflow/control, tool/harness-code, weights}; exact registered surfaces may be a strict subset but are frozen before evidence collection",
            "surface_intervention_class": "I_s contains bounded persistent repairs that change only the declared update surface s; generation access and evaluation budget are matched by the frozen repair contract",
            "outcome_vector": "Y_s = (task repair utility, persistence, collateral regression, diagnosability preservation, failure-quality risk, cost) under a candidate intervention at surface s",
            "sufficiency": "surface s is causally sufficient only if a registered intervention class at s can meet frozen repair-utility and persistence requirements without violating collateral/diagnosability/risk constraints",
            "scope_relation": "pre-registered partial order or dominance relation over repair surfaces; heterogeneous/incomparable surfaces are allowed and must not be forced into one total order",
            "minimal_sufficient_surface_set": "for causal model M, A*(M) is the antichain of sufficient surfaces not dominated by another sufficient surface under the frozen scope relation",
            "compatible_model_set": "C(E) is the set of causal repair models/effect intervals consistent with the pre-intervention evidence E plus any already-observed reversible diagnostic probes",
            "identified_surface": "IDENTIFIED(s) iff for every M in C(E), A*(M) is the same singleton {s}; otherwise the repair locus is not point identified",
            "partial_identification_set": "PI(E) = union over M in C(E) of A*(M); report this set rather than hallucinating a unique surface when |PI(E)| > 1",
        },
        "non_identifiability_claim": {
            "statement": (
                "There exist pairs of persistent-agent causal models with identical failed trajectories, observable artifacts, and responsibility attribution, "
                "but different minimal sufficient repair surfaces because downstream co-adaptation and cross-surface substitution alter intervention outcomes. "
                "Therefore attribution alone cannot identify the repair locus."
            ),
            "proof_obligation": [
                "construct two SCMs that induce the same pre-intervention observable distribution and responsibility score",
                "show the SCMs disagree on A*(M)",
                "show at least one reversible surface probe has different outcome distributions and can separate the models",
            ],
            "paper_role": "load-bearing theoretical motivation; if this construction cannot be made non-degenerate under realistic agent modularity assumptions, stop the standalone method paper",
        },
        "assumptions": [
            {"id": "A1-registered-surfaces", "text": "The candidate persistent repair surfaces and their boundaries are versioned before repair outcomes are observed."},
            {"id": "A2-modular-intervention", "text": "A diagnostic or repair intervention declares exactly which persistent surface it changes; downstream behavioral consequences may propagate but direct write scope is auditable."},
            {"id": "A3-independent-truth", "text": "Task repair, persistence, collateral, diagnosability, and failure-quality outcomes are measured by external/environment or frozen evaluators rather than the evolving agent."},
            {"id": "A4-comparable-budget", "text": "Surface comparisons use matched information access and a preregistered generation/evaluation budget appropriate to each intervention contract."},
            {"id": "A5-probe-reversibility", "text": "PROBE_MORE uses non-committing sandbox/replay interventions whose persistent effects are discarded before the final commit decision."},
            {"id": "A6-no-hidden-outcome-peeking", "text": "Hidden persistent repair outcomes cannot be opened before the identification certificate; exhaustive hidden-time repair trials are forbidden."},
            {"id": "A7-overlap", "text": "A surface can be certified only inside the support region where its relevant intervention/effect bounds are estimable; otherwise RSIC must abstain."},
        ],
        "method": {
            "stage_1_surface_hypothesis_registry": (
                "Compile candidate surface hypotheses H_s from the versioned agent dependency/harness contract. Each H_s specifies a repair surface, allowed intervention family, "
                "scope relation, persistence semantics, and which outcome components it can affect. This registry is structural input, not a learned surface label."
            ),
            "stage_2_compatibility_bounds": (
                "From source interventional evidence, fit or compute surface-specific partial effect bounds rather than a point surface score. At evaluation, update the compatible set C(E) using only "
                "pre-intervention failure evidence and any allowed reversible-probe outcomes. Generic partial-identification machinery is permitted here and must be included as a baseline."
            ),
            "stage_3_identification_certificate": (
                "Compute PI(E). Return IDENTIFIED(s) only when all compatible models/effect bounds imply the same singleton minimal sufficient surface. Return UNIDENTIFIABLE(PI) when multiple loci remain "
                "or when overlap/support is insufficient. False unique certification is treated as the primary scientific error."
            ),
            "stage_4_probe_more_contract": (
                "If repair locus is not identified, enumerate only preregistered reversible probes q. A probe is eligible only if, under the current compatibility set, at least one possible outcome strictly removes a repair-surface hypothesis "
                "without itself committing a persistent repair. RSIC may expose the eligible probe set and expected/worst-case elimination; an active probe policy is secondary and not required for the core certificate claim."
            ),
            "stage_5_commit_boundary": (
                "Commit is outside the certificate. If IDENTIFIED(s) is returned, a separate frozen repair generator may instantiate a repair at s. RSIC does not claim that repair generation itself is novel. "
                "If UNIDENTIFIABLE remains after the allowed probe budget, the required action is abstention/human escalation rather than a guessed surface."
            ),
        },
        "certificate_states": {
            "IDENTIFIED": "all compatible causal models/effect intervals agree on one minimal sufficient repair surface",
            "UNIDENTIFIABLE": "two or more repair loci remain compatible, or support/assumptions are insufficient for a unique certificate",
            "PROBE_MORE": "at least one allowed reversible probe can reduce the compatible repair-surface set; no persistent repair has yet been authorized",
            "OUT_OF_SCOPE": "failure does not lie inside the frozen surface/intervention/support registry; no repair-surface claim is emitted",
        },
        "why_this_is_not_existing_repair_localization": {
            "Diagnosis_Is_Not_Prescription": "treated as a load-bearing collision/motivation: responsibility need not equal prescription. RSIC does not claim this observation; it formalizes when prescription remains non-identifiable and when evidence is sufficient to certify one locus.",
            "HarnessFix": "provides harness-layer attribution and scoped repair operators; RSIC must still distinguish multiple observationally compatible persistent surfaces and may explicitly return UNIDENTIFIABLE instead of mapping every diagnosis to one operator.",
            "WML": "localizes node/mechanism and smallest valid edit target within structured skills; RSIC's claim is cross-surface partial identification, not within-workflow localization.",
            "CausalFlow_CAR": "step-level counterfactual attribution/minimal trace repair are baselines; trajectory cause is not equated with persistent repair surface.",
            "MOSS": "source-level repair is a broad repair option/ceiling, not evidence that source-level is the minimal or identifiable repair locus.",
        },
        "same_information_baselines": [
            {
                "name": "generic-partial-identification",
                "access": "identical causal variables, source intervention table, pre-intervention evidence, reversible probe outcomes, support assumptions, and thresholds",
                "method": "enumerate/fits the same compatible models/effect intervals and reports all repair surfaces not ruled out, without RSIC-specific minimal-sufficiency certificate structure",
                "role": "primary generic causal baseline; if this produces identical certification/abstention decisions under the same formal objects, the standalone method novelty collapses",
            },
            {
                "name": "generic-active-diagnosis",
                "access": "identical current hypothesis set, probe set, probe costs, and outcome likelihoods/bounds",
                "method": "information-gain / expected-elimination or worst-case-elimination probe selection",
                "role": "ensures active probing is not smuggled in as novelty",
            },
            {
                "name": "diagnosis-is-not-prescription-score",
                "access": "same failed trace, component graph, and source repair outcomes where available",
                "method": "responsibility/co-adaptation based intervention-locus heuristic",
                "role": "strongest diagnosis-versus-prescription collision baseline",
            },
            {
                "name": "HarnessFix",
                "access": "same failure traces and harness artifacts within supported harness layers",
                "method": "layer attribution to scoped repair operators with patch validation",
                "role": "strongest harness repair-localization baseline",
            },
            {
                "name": "WML",
                "access": "same failure evidence inside structured skill/workflow scope",
                "method": "node/mechanism attribution and smallest valid edit target",
                "role": "strongest structured-skill minimal-edit baseline",
            },
            {
                "name": "CausalFlow-CAR",
                "access": "same replay/intervention budget for trace-level causal attribution",
                "method": "counterfactual step attribution/minimal trace repair",
                "role": "causal attribution baseline",
            },
            {
                "name": "always-broad-MOSS-style",
                "access": "same failed evidence and broad code/source repair capability where applicable",
                "method": "always use the most expressive available source/harness repair surface",
                "role": "broad-surface ceiling / minimality baseline",
            },
        ],
        "load_bearing_claims": [
            {
                "id": "C1-NONIDENT",
                "claim": "Failure evidence and causal responsibility can be insufficient to point-identify the minimal persistent repair surface; observationally equivalent agent states can require different repair loci.",
                "type": "problem/theory",
                "failure_consequence": "If responsibility/pre-intervention evidence already determines the minimal surface under realistic assumptions, stop the paper problem.",
            },
            {
                "id": "C2-CERT",
                "claim": "RSIC's certificate controls false unique surface certification by returning partial-identification sets/abstention when the repair locus is not identified.",
                "type": "method",
                "failure_consequence": "If generic partial identification with the same formal objects gives identical decisions and guarantees, reduce RSIC to an evaluation protocol or stop the standalone method claim.",
            },
            {
                "id": "C3-PROBE",
                "claim": "Reversible cross-surface probes can resolve a nontrivial subset of otherwise non-identified repair loci without performing hidden-time persistent repair search.",
                "type": "mechanism/secondary",
                "failure_consequence": "If allowed probes do not shrink PI(E) beyond generic active diagnosis or require effectively trying repairs, drop this claim; C1/C2 may still survive.",
            },
            {
                "id": "C4-DECISION",
                "claim": "At matched evidence/repair budget, an identification-aware commit policy avoids harmful guessed-surface commits while retaining useful coverage relative to always-route/localization baselines.",
                "type": "decision consequence",
                "failure_consequence": "If abstention adds no decision value at matched coverage/cost, stop the practical method claim.",
            },
        ],
        "primary_metrics_for_future_blueprint": {
            "false_unique_certification_rate": "fraction of IDENTIFIED(s) certificates where the frozen cross-surface intervention truth does not support s as the unique minimal sufficient locus",
            "identified_coverage": "fraction of eligible failures receiving a correct unique certificate at a frozen false-certification constraint",
            "partial_set_size": "size of PI(E) when unique certification is impossible",
            "probe_cost_to_identification": "reversible probe cost required to turn UNIDENTIFIABLE into correct IDENTIFIED",
            "guessed_commit_harm_avoided": "harm/collateral avoided relative to forced-routing baselines at matched useful-commit coverage",
        },
        "cross_cutting_invariants": {
            "PF-4_diagnosability": "a repair surface cannot be declared sufficient if the committed update destroys the frozen interventional/provenance channel needed for later diagnosis; secondary invariant only",
            "PF-6_failure_quality": "failure-class substitution risk is part of the sufficiency outcome vector; secondary risk analysis only, not a standalone transport method",
        },
        "method_stop_rules_before_local_validation": [
            "STOP if the non-identifiability construction is degenerate or disappears once realistic observable agent state is included.",
            "STOP standalone method novelty if generic partial-identification under the same formal objects yields the same certificate states and decision guarantees.",
            "DROP the probe claim if PROBE_MORE is merely generic active diagnosis with renamed hypotheses and contributes no repair-surface-specific constraint or guarantee.",
            "RETURN TO PAPER DESIGN if unique surface truth cannot be defined independently using matched cross-surface interventions and frozen collateral/persistence constraints.",
            "RETURN TO PAPER DESIGN if the primary protocol requires opening hidden persistent repair outcomes before certification.",
        ],
        "method_freeze_requirements": [
            "freeze exact registered repair surfaces and intervention families",
            "freeze surface boundaries, persistence semantics, reversibility contract, and scope/dominance relation",
            "freeze causal variables / compatibility model family / effect-bound estimator",
            "freeze task-repair, persistence, collateral, diagnosability, risk, and support thresholds",
            "freeze IDENTIFIED / UNIDENTIFIABLE / PROBE_MORE / OUT_OF_SCOPE semantics",
            "freeze allowable reversible probe library and probe budget",
            "freeze same-information generic partial-identification and active-diagnosis baselines",
            "freeze all theorem/identifiability assumptions before any local falsifier",
        ],
        "authority": {
            "paper_problem_authorized": True,
            "method_design_authorized": True,
            "method_frozen": False,
            "experiment_blueprint_authorized_to_design": False,
            "local_validation_authorized": False,
            "p0_authorized": False,
            "gpu_authorized": False,
            "full_experiment_authorized": False,
            "premature_pf_f0_used": False,
        },
        "next_action": "Run an independent method-level premortem against generic partial-identification, active diagnosis, Diagnosis Is Not Prescription, HarnessFix, WML, CausalFlow/CAR, and MOSS. Only if the certificate remains irreducible may an experiment blueprint be designed; local validation remains locked.",
    }


def validate_pf2_method_design(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if state.get("incubation_id") != "PF-2": errors.append("wrong incubation id")
    if state.get("paper_id") != "repair-surface-identifiability-under-persistent-agent-updates": errors.append("wrong PF-2 revised paper id")
    if state.get("method_status") != "METHOD_DESIGN_DRAFT_AWAITING_INDEPENDENT_PREMORTEM": errors.append("unexpected method status")
    if len(state.get("same_information_baselines") or []) < 7: errors.append("insufficient same-information baseline coverage")
    names = {row.get("name") for row in state.get("same_information_baselines") or []}
    for required in ("generic-partial-identification", "generic-active-diagnosis", "diagnosis-is-not-prescription-score", "HarnessFix", "WML", "CausalFlow-CAR"):
        if required not in names: errors.append(f"missing baseline:{required}")
    if len(state.get("load_bearing_claims") or []) != 4: errors.append("PF-2 method must expose four load-bearing claims")
    if not (state.get("non_identifiability_claim") or {}).get("proof_obligation"): errors.append("missing repair-surface non-identifiability proof obligation")
    identified = (state.get("formal_objects") or {}).get("identified_surface", "").lower()
    if "for every" not in identified and "all compatible" not in identified: errors.append("unique certificate must quantify over all compatible models")
    authority = state.get("authority") or {}
    if authority.get("method_design_authorized") is not True: errors.append("method design should be authorized")
    for key in ("method_frozen", "experiment_blueprint_authorized_to_design", "local_validation_authorized", "p0_authorized", "gpu_authorized", "full_experiment_authorized", "premature_pf_f0_used"):
        if authority.get(key) is not False: errors.append(f"{key} must remain false")
    return errors


def write_pf2_method_design(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    state = build_pf2_method_design()
    errors = validate_pf2_method_design(state)
    if errors:
        raise ValueError("Invalid PF-2 method design:\n- " + "\n- ".join(errors))
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.PAPER_FIRST_PF2_METHOD_DESIGN = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    print(json.dumps(write_pf2_method_design(), ensure_ascii=False))
