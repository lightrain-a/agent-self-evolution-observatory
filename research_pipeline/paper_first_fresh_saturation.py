from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-fresh-saturation.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "paper-first-fresh-saturation.js"

REDUCTION_PATTERNS: tuple[dict[str, Any], ...] = (
    {"key":"update-order-path-dependence","mature_theories":["interaction effects","co-evolutionary dynamics","non-stationary online learning"],"veto":"Do not promote update-order/non-commutativity claims unless a formal object survives those same-information theories."},
    {"key":"snapshot-validity-horizon","mature_theories":["non-stationary model selection","optimal stopping","adaptive validation"],"veto":"A time-varying best checkpoint/half-life is not a new problem by itself."},
    {"key":"feedback-view-intransitivity","mature_theories":["multi-objective optimization","preference cycles","social choice / ranking"],"veto":"Different validation/test/robustness rankings are not novel without a non-reducible decision object."},
    {"key":"operator-closure-reachability","mature_theories":["automata reachability","typed operator algebra","self-modifying program semantics"],"veto":"Versioned agent-resource operator closure is not novel when the protocol already defines the state/operator algebra."},
    {"key":"stream-instability","mature_theories":["dynamical systems","Lyapunov stability","non-stationary learning"],"veto":"Naming a self-evolution stream Lyapunov exponent is domain transfer unless the dynamics add a new structural constraint."},
    {"key":"self-generated-supervision-information-limit","mature_theories":["recursive self-training collapse","closed-loop self-evolution generalization gap","information bottleneck"],"veto":"An information ceiling for self-generated supervision is already occupied unless a distinct information source/constraint changes the theorem."},
    {"key":"validation-filter-information-loss","mature_theories":["Bayesian optimization","information bottleneck","selective sampling"],"veto":"Sparse validation/filtering tradeoffs are not a new scientific object."},
    {"key":"verifier-exogeneity","mature_theories":["adaptive data analysis","conditional independence / d-separation","co-training correlated errors","recursive self-gating collapse"],"veto":"Shared evaluator-policy ancestry is not new unless same-information causal/statistical dependence models cannot express the prediction."},
    {"key":"evolution-induced-task-non-equivalence","mature_theories":["inter-MDP generalized bisimulation","MDP homomorphism","behavioral equivalence"],"veto":"Pre/post scaffold semantics comparability is domain transfer when generalized inter-MDP equivalence solves the same question."},
    {"key":"persistent-update-vs-test-time-compute","mature_theories":["amortized inference","test-time scaling","search-vs-learning evaluation"],"veto":"Persistent update necessity is already an explicit harness/skill evaluation question; require a new structural prediction, not another comparison."},
    {"key":"typed-epistemic-authority","mature_theories":["filtered/source-sensitive belief revision","Bayesian source-reliability networks","dynamic epistemic/justification logic"],"veto":"NO-AUTHORITY evidence transitions are not novel if typed credibility partitions or conditional independence reproduce the same belief update."},
    {"key":"model-scaffold-enactability","mature_theories":["cross-model prompt transfer","instruction following / compliance","model-artifact compatibility"],"veto":"A harness/skill that is valid but not activated or faithfully followed by a target model is not a new object unless it escapes cross-model prompt/artifact compatibility under the same information."},
    {"key":"artifact-uptake-after-retrieval","mature_theories":["retrieval-versus-utilization diagnostics","instruction following","externalized skill execution"],"veto":"Retrieved experience that fails to change behavior is already a utilization/uptake bottleneck; require a new causal object beyond retrieval and instruction-following decomposition."},
    {"key":"environment-mediated-history","mature_theories":["POMDP state sufficiency","causal mediation through physical state","state-conditioned embodied memory"],"veto":"Past actions affecting future behavior through the current world state are not evidence of internal memory; this distinction is mature state/mediation theory unless a new embodied-only prediction survives."},
    {"key":"multimodal-procedural-compression","mature_theories":["multimodal representation","rate-distortion / information preservation","visual grounding and domain adaptation"],"veto":"Visual details that cannot be compressed into text are not a new self-evolution problem when multimodal skills already preserve state cards/keyframes and rate-distortion captures information loss."},
    {"key":"externalization-internalization-portability","mature_theories":["parametric-versus-externalized capability tradeoff","skill distillation / internalization","cross-model prompt and skill transfer","multivariate information decomposition"],"veto":"A component becoming internalized in one policy while remaining useful to another is not a new object when externalization/internalization and component-wise transfer are expressible under the same information."},
    {"key":"horizon-censored-attribution","mature_theories":["right-censored causal inference","partial identification","adaptive follow-up / active sequential testing"],"veto":"Finite-horizon nulls, horizon-stability certificates, or frontier-first continuation are not novel when censoring bounds plus target-specific active testing express the same decision."},
    {"key":"self-model-lineage-desynchronization","mature_theories":["behavioral self-awareness","self-preference / own-output bias","anchoring and context interference","configuration/cache invalidation"],"veto":"A SELF-vs-static prediction gap is not a self-evolution problem if retained authorship/history context or ordinary interface comprehension explains it."},
    {"key":"future-evolvability-debt","mature_theories":["loss of plasticity","evolvability in evolutionary computation","software technical debt / changeability"],"veto":"Reduced future response to a frozen updater is not novel when the same object is plasticity/evolvability or future change cost."},
    {"key":"persistent-world-gain-decomposition","mature_theories":["2x2 factorial decomposition / difference-in-differences","longitudinal mediation / g-methods","counterfactual replay"],"veto":"Internal-version versus inherited-world contributions are not novel when frozen version x world snapshots or longitudinal mediation identify the same quantities."},
    {"key":"cross-module-longitudinal-stability","mature_theories":["coupled optimization / game dynamics","component-interference consolidation","identity-preserving continual evolution"],"veto":"Locally valid module updates failing to compose globally are not novel without a structural constraint beyond generic coupled-dynamics stability."},
    {"key":"autonomous-goal-extension","mature_theories":["requirements refinement","BDI goal revision","temporal-logic/specification consistency"],"veto":"Autonomously added goals are not a new scientific object if ordinary contract/refinement checking decides legitimacy."},
    {"key":"self-play-evidence-endogeneity","mature_theories":["performative prediction / endogenous distribution shift","curriculum coverage / active learning","self-play mode collapse / diversity measurement","data gating"],"veto":"Self-generated evidence blind spots are not novel if coverage, diversity, performative-shift, or data-gating baselines express the same failure."},
    {"key":"lineage-conditioned-communication-semantics","mature_theories":["emergent-language drift","semantic interoperability / protocol negotiation","versioned interface contracts"],"veto":"Private evolving conventions are not novel when semantic alignment/versioning solves same-schema different-meaning failures."},
    {"key":"embodiment-task-comparability","mature_theories":["morphology-conditioned feasibility/control","cross-embodiment transfer","task-space/benchmark normalization"],"veto":"Changing embodiment does not create a new task-identity problem if feasibility and embodiment-invariant outcome normalization solve comparability."},
    {"key":"population-lineage-generic-evolution","mature_theories":["genetic hitchhiking / linkage","epistasis / crossover incompatibility","winner's curse / adaptive selection","heritability / catastrophic forgetting"],"veto":"Population, fork, recombination, selection, or inheritance claims are not novel when classical evolutionary/statistical objects give the same prediction."},
    {"key":"cross-layer-behavior-persistence","mature_theories":["skill distillation/internalization","unlearning / persistent contamination","descendant inheritance / source-deletion persistence"],"veto":"External-to-internal migration and ghost behavior after source removal are not novel when cross-layer promotion and descendant contamination already predict persistence."},
    {"key":"experience-sharing-sign-reversal","mature_theories":["diversity-consensus tradeoff","negative transfer / distributed heterogeneity","information redundancy / correlation","portfolio/submodular diversity"],"veto":"Sharing-helpful versus sharing-collapse contradictions are not novel if complementarity/redundancy under matched budget predicts the sign."},
    {"key":"feedback-polarity-by-update-surface","mature_theories":["supervised imitation / behavioral cloning","error-driven and corrective learning","positive-only versus positive+negative concept learning","information gain / active learning"],"veto":"Success-only versus failure-containing feedback is not a new Agent object when imitation learns positive behavior while corrective/rule learning uses failures as counterexamples that expose missing applicability boundaries."},
    {"key":"harness-update-scope-heterogeneity","mature_theories":["conditional average treatment effects / effect heterogeneity","invariant causal prediction / invariant risk minimization","domain generalization","software configuration scoping"],"veto":"Task-, pathology-, executor-, or trace-conditioned harness validity is not a new Agent object when the candidate condition is simply an effect modifier and the minimal invariant is a CATE/ICP/IRM target."},
    {"key":"durable-runtime-improvement-vs-aging","mature_theories":["non-stationary stochastic dynamical systems / Lyapunov stability","continual-memory interference and stability-plasticity","reliability and maintenance engineering","state-space system identification"],"veto":"Fixed-weight durable runtime state producing either compounding improvement or aging is not a new Agent object when the sign is expressible as monotonicity/contraction or interference/drift of a state-transition operator with respect to task value."},
    {"key":"scientific-claim-decomposition-dependence","mature_theories":["claim decomposition and verifier alignment","compositional verification / constraint coverage","specification refinement","proof/decomposition traceability"],"veto":"Scientific verification that changes with a legal subclaim decomposition is not a new self-evolution object when decomposition quality, compositional infeasibility, and verifier alignment already determine downstream claim judgments under the same evidence."},
    {"key":"agent-version-rollback-vs-external-effects","mature_theories":["semantic transactions for agent workflows","irreversible-effect safety / execution fidelity","checkpoint-restore and semantic rollback semantics","compensating transactions and recovery"],"veto":"Rolling back an agent version while external side effects persist is not a new self-evolution object when semantic transactions, irreversible-transition safety, and checkpoint-recovery already formalize commit, rollback, replay, fork, compensation, and audit of external state."},
    {"key":"procedural-memory-nonmonotonicity","mature_theories":["nonmonotonic / defeasible logic","belief revision / AGM-style belief change","rule-conflict and priority semantics"],"veto":"Adding a relevant memory, skill, or procedural rule that retracts, suppresses, or harms previously correct behavior is not a new self-evolution object when nonmonotonic reasoning or belief revision expresses the same retraction under the same conflict information."},
)


# Ledger entries are candidate reduction hypotheses, not automatic scientific vetoes.
# Even a VALID_HARD_VETO pattern may block only after the concrete candidate
# satisfies the Reduction Falsifiability Contract below.
_REDUCTION_AUDIT_CLASS: dict[str, str] = {
    "operator-closure-reachability":"VALID_HARD_VETO",
    "evolution-induced-task-non-equivalence":"VALID_HARD_VETO",
    "environment-mediated-history":"VALID_HARD_VETO",
    "autonomous-goal-extension":"VALID_HARD_VETO",
    "embodiment-task-comparability":"VALID_HARD_VETO",
    "agent-version-rollback-vs-external-effects":"VALID_HARD_VETO",

    "typed-epistemic-authority":"SOFT_COLLISION",
    "persistent-update-vs-test-time-compute":"SOFT_COLLISION",
    "model-scaffold-enactability":"SOFT_COLLISION",
    "artifact-uptake-after-retrieval":"SOFT_COLLISION",
    "multimodal-procedural-compression":"SOFT_COLLISION",
    "externalization-internalization-portability":"SOFT_COLLISION",
    "cross-layer-behavior-persistence":"SOFT_COLLISION",
    "scientific-claim-decomposition-dependence":"SOFT_COLLISION",

    "update-order-path-dependence":"TOO_GENERIC_TO_VETO",
    "feedback-view-intransitivity":"TOO_GENERIC_TO_VETO",
    "stream-instability":"TOO_GENERIC_TO_VETO",
    "validation-filter-information-loss":"TOO_GENERIC_TO_VETO",
    "cross-module-longitudinal-stability":"TOO_GENERIC_TO_VETO",
    "population-lineage-generic-evolution":"TOO_GENERIC_TO_VETO",
    "experience-sharing-sign-reversal":"TOO_GENERIC_TO_VETO",
    "harness-update-scope-heterogeneity":"TOO_GENERIC_TO_VETO",
    "durable-runtime-improvement-vs-aging":"TOO_GENERIC_TO_VETO",

    "snapshot-validity-horizon":"NEEDS_EXACT_REDUCTION_TEST",
    "self-generated-supervision-information-limit":"NEEDS_EXACT_REDUCTION_TEST",
    "verifier-exogeneity":"NEEDS_EXACT_REDUCTION_TEST",
    "horizon-censored-attribution":"NEEDS_EXACT_REDUCTION_TEST",
    "self-model-lineage-desynchronization":"NEEDS_EXACT_REDUCTION_TEST",
    "future-evolvability-debt":"NEEDS_EXACT_REDUCTION_TEST",
    "persistent-world-gain-decomposition":"NEEDS_EXACT_REDUCTION_TEST",
    "self-play-evidence-endogeneity":"NEEDS_EXACT_REDUCTION_TEST",
    "lineage-conditioned-communication-semantics":"NEEDS_EXACT_REDUCTION_TEST",
    "feedback-polarity-by-update-surface":"NEEDS_EXACT_REDUCTION_TEST",
    "procedural-memory-nonmonotonicity":"NEEDS_EXACT_REDUCTION_TEST",
}

REDUCTION_FALSIFIABILITY_CONTRACT: dict[str, Any] = {
    "same_observable_information_required": True,
    "ex_ante_exact_prediction_required": True,
    "testable_distinguishing_prediction_required": True,
    "explicit_scope_boundary_required": True,
    "generic_theory_name_is_not_a_veto": True,
    "pattern_match_alone_blocks": False,
    "unresolved_exact_reduction_blocks_problem_gate": True,
}

def reduction_pattern_audit() -> list[dict[str, Any]]:
    rows=[]
    for row in REDUCTION_PATTERNS:
        key=str(row["key"])
        rows.append({**row,"audit_class":_REDUCTION_AUDIT_CLASS[key],"automatic_veto":False})
    return rows

if set(_REDUCTION_AUDIT_CLASS) != {str(row["key"]) for row in REDUCTION_PATTERNS}:
    raise RuntimeError("reduction audit classification must cover every current reduction pattern exactly")

DRAFTS: tuple[dict[str, Any], ...] = (
    {"id":"G1","title":"Non-Commutativity of Update Trajectories Under Live Evaluator Drift","decision":"STOP_REDUCTION","reduction":"update-order-path-dependence"},
    {"id":"G2","title":"Temporal Validity Kernel of Intermediate Harness Snapshots","decision":"STOP_REDUCTION","reduction":"snapshot-validity-horizon"},
    {"id":"G3","title":"Topological Torsion in Skill Memory Co-Evolution","decision":"STOP_REDUCTION","reduction":"update-order-path-dependence"},
    {"id":"G4","title":"Information Imbalance Between Step-Level and Multi-Step Optimizer Rankings","decision":"STOP_REDUCTION","reduction":"sequential ranking / credit assignment"},
    {"id":"G5","title":"Intransitivity of Feedback Views Under Scaling","decision":"STOP_REDUCTION","reduction":"feedback-view-intransitivity"},
    {"id":"G6","title":"Algebraic Closure of Versioned Resource Interfaces","decision":"STOP_REDUCTION","reduction":"operator-closure-reachability"},
    {"id":"G7","title":"Lyapunov Instability of Sequential Evolution Streams","decision":"STOP_REDUCTION","reduction":"stream-instability"},
    {"id":"G8","title":"Non-Isomorphic Failure Embeddings Across Memory and Skill Co-Evolution","decision":"STOP_REDUCTION","reduction":"representation/topology relabeling without decision consequence"},
    {"id":"G9","title":"Information Horizon of In-Distribution Process Supervision","decision":"STOP_REDUCTION","reduction":"self-generated-supervision-information-limit"},
    {"id":"G10","title":"Sparse Search Validation Filter Information Loss","decision":"STOP_REDUCTION","reduction":"validation-filter-information-loss"},
    {"id":"X1","title":"Verifier Endogeneity / Exogeneity Budget","decision":"STOP_REDUCTION","reduction":"verifier-exogeneity"},
    {"id":"X2","title":"Evolution-Induced Task Non-Equivalence","decision":"STOP_REDUCTION","reduction":"evolution-induced-task-non-equivalence"},
    {"id":"X3","title":"Persistent-Update Necessity / Compute Substitutability","decision":"STOP_COLLISION","reduction":"persistent-update-vs-test-time-compute"},
    {"id":"X4","title":"Epistemic Authority of Autonomous Experiment Outcomes","decision":"STOP_REDUCTION","reduction":"typed-epistemic-authority"},
    {"id":"X5","title":"Model-Scaffold Enactability Across Policy Models","decision":"STOP_REDUCTION","reduction":"model-scaffold-enactability"},
    {"id":"X6","title":"Persistent Artifact Uptake After Successful Retrieval","decision":"STOP_REDUCTION","reduction":"artifact-uptake-after-retrieval"},
    {"id":"X7","title":"Environment-Mediated History Versus Internal Embodied Memory","decision":"STOP_REDUCTION","reduction":"environment-mediated-history"},
    {"id":"X8","title":"Irreducible Visual Detail in Multimodal Procedural Consolidation","decision":"STOP_REDUCTION","reduction":"multimodal-procedural-compression"},
    {"id":"X9","title":"Harness-Internalization vs. Harness-Transfer: When Annealing Reduces Cross-Model Reusability","decision":"STOP_REDUCTION","reduction":"externalization-internalization-portability"},
    {"id":"H1","title":"Horizon-Censored Causal Attribution","decision":"STOP_REDUCTION","reduction":"horizon-censored-attribution"},
    {"id":"H2","title":"Horizon-Valid Ordered Causal Locus","decision":"STOP_REDUCTION","reduction":"horizon-censored-attribution"},
    {"id":"H3","title":"Post-Self-Modification Self-Model Desynchronization","decision":"STOP_REDUCTION","reduction":"self-model-lineage-desynchronization"},
    {"id":"H4","title":"Evolvability Debt of Accepted Agent Updates","decision":"STOP_REDUCTION","reduction":"future-evolvability-debt"},
    {"id":"H5","title":"Internal Adaptation versus Persistent-World Shaping","decision":"STOP_REDUCTION","reduction":"persistent-world-gain-decomposition"},
    {"id":"H6","title":"Cross-Module Identity Drift under Local Update Gates","decision":"STOP_REDUCTION","reduction":"cross-module-longitudinal-stability"},
    {"id":"N1","title":"Autonomous Goal Conservative Extension","decision":"STOP_REDUCTION","reduction":"autonomous-goal-extension"},
    {"id":"N2","title":"Self-Play Evidence Endogeneity","decision":"STOP_REDUCTION","reduction":"self-play-evidence-endogeneity"},
    {"id":"N3","title":"Lineage-Specific Communication Semantics","decision":"STOP_REDUCTION","reduction":"lineage-conditioned-communication-semantics"},
    {"id":"N4","title":"Task Semantics under Embodiment Evolution","decision":"STOP_REDUCTION","reduction":"embodiment-task-comparability"},
    {"id":"L1","title":"Component Hitchhiking under Whole-Agent Selection","decision":"STOP_REDUCTION","reduction":"population-lineage-generic-evolution"},
    {"id":"L2","title":"Cross-Lineage Recombination Epistasis","decision":"STOP_REDUCTION","reduction":"population-lineage-generic-evolution"},
    {"id":"L3","title":"Winner-Lineage Selection Bias","decision":"STOP_REDUCTION","reduction":"population-lineage-generic-evolution"},
    {"id":"L4","title":"Heritability of Self-Evolved Capability","decision":"STOP_REDUCTION","reduction":"population-lineage-generic-evolution"},
    {"id":"D1","title":"Dual-Residency Ghost Effect after External Skill Internalization","decision":"STOP_COLLISION","reduction":"cross-layer-behavior-persistence"},
    {"id":"C1","title":"Experience Sharing: Complementarity versus Diversity Collapse","decision":"STOP_REDUCTION","reduction":"experience-sharing-sign-reversal"},
    {"id":"C2","title":"Does Update Surface Change the Scientific Value of Success versus Failure Feedback?","decision":"STOP_REDUCTION","reduction":"feedback-polarity-by-update-surface"},
    {"id":"C3","title":"Task Identity versus Failure Pathology as the Scope of Harness Updates","decision":"STOP_REDUCTION","reduction":"harness-update-scope-heterogeneity"},
    {"id":"C4","title":"Compounding Self-Evolution versus Agent Aging in Fixed-Weight Durable Runtimes","decision":"STOP_REDUCTION","reduction":"durable-runtime-improvement-vs-aging"},
    {"id":"C5","title":"Decomposition-Dependent Verification of Autonomous Scientific Claims","decision":"STOP_REDUCTION","reduction":"scientific-claim-decomposition-dependence"},
    {"id":"C6","title":"Why Agent-Version Rollback Cannot Undo Irreversible External Consequences","decision":"STOP_REDUCTION","reduction":"agent-version-rollback-vs-external-effects"},
    {"id":"C7","title":"Non-Monotone Coverage after Adding Relevant Procedural Memory","decision":"STOP_REDUCTION","reduction":"procedural-memory-nonmonotonicity"},
)

POLICY: dict[str, Any] = {
    "schema_version":"1.1",
    "problem_first_not_method_first":True,
    "mathematical_renaming_is_not_novelty":True,
    "mature_domain_transfer_is_hard_veto":True,
    "same_information_theory_baseline_required":True,
    "latest_primary_source_collision_required":True,
    "endpoint_headroom_required_before_interpreting_terminal_outcomes":True,
    "invalid_or_malformed_ai_generation_has_zero_scientific_authority":True,
    "zero_survivors_is_valid_and_preferred_to_forced_shortlist":True,
    "local_validation_authorized":False,
    "p0_authorized":False,
    "gpu_authorized":False,
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_fresh_saturation_state() -> dict[str, Any]:
    return {
        "schema_version":"1.0",
        "generated_at":_now(),
        "review_id":"fresh-problem-saturation-20260813-r2",
        "policy":POLICY,
        "summary":{
            "drafts_reviewed":len(DRAFTS),
            "survivors":0,
            "stopped":len(DRAFTS),
            "reduction_patterns":len(REDUCTION_PATTERNS),
            "local_validation_authorized":0,
            "p0_authorized":0,
        },
        "drafts":[dict(row) for row in DRAFTS],
        "reduction_patterns":[dict(row) for row in REDUCTION_PATTERNS],
        "generator_revision":{
            "old_failure":"Free-form generators produced mathematically named versions of mature problems and malformed long JSON; formatting repair was treated as advisory-only and never as scientific evidence.",
            "historical_rule":"The historical scan used four empirically grounded lanes and immediate mature-theory reduction; its zero-survivor outcome remains diagnostic rather than a mandatory search policy.",
            "new_rule":"Keep the four empirical discovery lanes as the only live Problem-Gate types and allow at most one live generator call for each new content-addressed evidence pool. A ten-primitive Search Portfolio may expand and evolve branches only as a zero-authority shadow search lab and may apply the Reduction Falsifiability Contract after formulation; it cannot publish canonical Generator/Queue state, change source exposure, or grant Paper Design eligibility.",
            "required_fields":["discovery lane","two primary evidence items","lane-specific machine evidence","irreducible object","mature-theory non-reducibility","same-information baseline","cheapest problem falsifier","endpoint headroom"],
        },
        "decision":"NO_FRESH_SURVIVOR_CURRENT_SCAN",
        "next_action":"When source coverage is exhausted, keep the live weekly transaction at zero calls until new freshness/relevance-qualified lane-grounded evidence changes the content-addressed pool. Use Search Portfolio only for shadow breadth exploration; no shadow result can create a live candidate, Paper Design eligibility, Method, Experiment, P0, or GPU authority.",
    }


def write_fresh_saturation_state(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    state=build_fresh_saturation_state(); json_path.parent.mkdir(parents=True,exist_ok=True)
    json_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    js_path.write_text("window.PAPER_FIRST_FRESH_SATURATION = "+json.dumps(state,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    return state


if __name__ == "__main__":
    print(json.dumps(write_fresh_saturation_state(),ensure_ascii=False))
