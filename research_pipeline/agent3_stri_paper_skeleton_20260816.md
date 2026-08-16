# Self-Evolution Should Not Depend on How Skills Are Split

Status: pre-outcome paper skeleton. C1/C2 are supported; C3/C4 remain locked behind the frozen P0-A/P0-B entry gate. No dynamic or utility placeholder below may be converted into a claim before the corresponding frozen gate passes.

## One-sentence thesis

Self-evolving skill systems should be invariant to semantics-preserving reparameterizations of their evolving skill taxonomy; package-indexed controllers violate this principle because artifact identity multiplicity changes control mass, while Support-Quotient Control (SQC) factors control through semantic support before implementation identity.

## Abstract skeleton

Self-evolving agents increasingly maintain explicit skill libraries and use skill identities to control curriculum sampling, retrieval, credit assignment, refinement, and admission. We ask a basic invariance question: if two skill taxonomies expose the same executable semantic support but differ only in how that support is split or merged across package identities, should the future evolution process change? We identify **Identity-Mass Refinement Dependence**: package-indexed controllers place control mass on artifact identities, so semantics-preserving taxonomy refinements change the induced control process even when capability is unchanged. On released first-party skill systems, we observe representation sensitivity at the control plane. On the released Skill-SP support graph, the residual survives text/semantic deduplication and minimum full-coverage package pruning; moreover, two mandatory-overlap witnesses imply that every nonnegative context-independent package-weight controller has semantic-context exposure ratio at least 2, and the optimal LP attains this bound. We propose **Support-Quotient Control (SQC)**, which allocates mass to semantic support atoms and only then assigns implementation responsibility. [P0-A PLACEHOLDER: faithful Qwen3 dynamic representation sensitivity.] [P0-B PLACEHOLDER: same-bank quotient feasibility.] [FULL PLACEHOLDER: tool-disjoint matched factorial showing SQC invariance, 2pp heldout-utility non-inferiority, 5/5 semantic coverage, and matched resource use.] If the frozen dynamic or method gates fail, the paper must be narrowed or stopped according to the preregistered rules rather than rescued by new thresholds/backbones.

## 1. Introduction

### Motivation

A skill library is not merely a database: in self-evolving agents, its package identities become control units. The same underlying executable competence can therefore induce a different future evolution trajectory when the taxonomy is represented with one package, two overlapping packages, or a support-preserving merge.

### Scientific question

Does an endogenous skill-based self-evolution process depend on an arbitrary semantics-preserving taxonomy representation, and can a representation-invariant controller remove that dependence without sacrificing heldout evolution utility, semantic coverage, or matched resource efficiency?

### Why existing fixes are insufficient

- Text/name duplicate filtering cannot detect support overlap that is not textual duplication.
- Exact semantic clone deduplication removes exact clones but not irreducible partial overlap.
- Whole-package pruning cannot remove all overlap while preserving every uniquely supported region.
- Arbitrary global package weighting is still a package-indexed pre-context controller and is structurally lower-bounded on mandatory-overlap support graphs.
- A post-context router is not a same-information baseline for upstream curriculum sampling because the task context is generated after the package-selection decision.

### Contributions, gated

1. **Problem/principle (C1):** taxonomy representation invariance as a correctness criterion for self-evolving skill control; first-party control-plane evidence on Skill-SP and SkillRL.
2. **Mechanism/theory (C2):** Identity-Mass Refinement Dependence; clone/refinement lemma, decision-time controller-class reduction, and a tight partial-overlap lower bound of 2 on the released Skill-SP graph.
3. **Method (C3, pending P0-B/full):** SQC, which factors curriculum/retrieval/credit control through semantic support atoms before conditional implementation choice.
4. **Dynamic consequence (C4, pending P0-A/full):** faithful Qwen3 evidence that semantics-preserving merge/split control reparameterizations propagate to the generated semantic task distribution and, in the full experiment, end-of-evolution utility/control state.

## 2. Taxonomy Representation Invariance

Let X be semantic/task contexts. Freeze a content-addressed primitive basis U, where each primitive is an executable semantic contract fingerprinted from immutable skill content, examples/generator hints, solver rules, validator implementation, and validator specification; mutable sampling/evolution statistics and package IDs are excluded. For each primitive u, the frozen first-party predicate V_u defines support A_u={x:V_u(x)=1}. A taxonomy T only groups these unchanged primitives into current package identities S_T.

A semantics-preserving taxonomy transformation tau may duplicate package identities or group/ungroup unchanged primitives, but it may not change primitive content, validator predicates, or add executable support. The representation channel consists of package-selection mass p_T(s|z) and normalized within-package primitive responsibility rho_T(u|s,z), inducing primitive mass m_T(u|z)=sum_s p_T(s|z)rho_T(u|s,z).

The support quotient is the actual equivalence relation on context space: x ~_U x' iff V_u(x)=V_u(x') for every frozen u. Each cell c in C_U=X/~_U is identified by its primitive support signature sigma_U(c).

**STRI has four distinct levels.** STRI_E concerns additive eligibility/control exposure E_T(c|z)=sum_{u in sigma_U(c)}m_T(u|z); E is not a task-probability distribution and not utility. STRI_Q concerns the realized qualified semantic-task distribution produced by the first-party proposer/realization pipeline. STRI_G concerns semantic credit conservation. STRI_D concerns longitudinal/end-of-evolution outcomes. C1/C2 establish control-plane/theory evidence; STRI_Q/STRI_D remain empirical gates.

Important claim boundary: STRI is not a novelty claim about duplicate detection, generic diversity regularization, or contextual bandits. The object is invariance of an endogenous self-evolution control law to representation of its persistent skill taxonomy.

## 3. Identity-Mass Refinement Dependence

### 3.1 Clone/refinement dependence

A controller that allocates additive control mass to package identities can change primitive/control exposure under identity duplication even though the content-addressed primitive basis and executable support are unchanged. This is a representation-channel effect, not evidence that duplicated content itself is harmful.

### 3.2 Partial-overlap impossibility

At a frozen state, suppose two primitives u_a and u_b each have an exclusive-support cell and also share an overlap cell. For any nonnegative normalized primitive-mass vector that retains positive exposure on both exclusive cells, if r is the minimum focal-cell eligibility exposure, the exclusive cells force m(u_a)>=r and m(u_b)>=r while the overlap cell has E(c_ab)>=2r. Hence max_c E(c)/min_c E(c)>=2.

Released Skill-SP contains two independent witnesses:
- u_003 with u_015;
- u_004 with u_015.

The optimal global package-weight LP attains ratio 2.0, making the lower bound tight on the released graph. This theorem is only about additive eligibility exposure; it does not imply task-accuracy, regret, or longitudinal utility harm.

### 3.3 Decision-time controller-class reduction

Released Skill-SP samples one current package before the proposer task exists. At a **frozen pre-task state z**, any randomized same-information controller over that unchanged one-package action space is characterized pointwise by a categorical p_T(s|z); through the fixed responsibility channel it induces one nonnegative primitive-mass vector and therefore lies in the additive exposure class constrained above. This closes a generic learned pre-context single-package rescue at frozen z, but does not claim that a longitudinal adaptive neural/bandit policy is globally one fixed categorical vector. Dynamic propagation remains P0/C4's job.

## 4. Support-Quotient Control

SQC changes the control object from package identity to the frozen support quotient C_U.

1. **Freeze the primitive basis.** Content-address immutable primitive contracts and first-party support predicates independently of method outcomes.
2. **Construct the support quotient.** Use equality of frozen primitive-support signatures to define C_U; package duplication/grouping cannot create a new quotient dimension.
3. **Conserve primitive state.** Aggregate the same raw pre-task quality/exploration/decay evidence into content-addressed primitive/support-cell state. Duplicate package IDs may expose derived views, but cannot create independent scientific state or exploration counters.
4. **Support-first allocation.** Allocate a normalized control measure mu(c) over quotient cells under a frozen calibration prior rather than over current package IDs.
5. **Conditional implementation responsibility.** Choose alpha(u|c,theta) only from the quotient cell, conserved primitive state theta, and the same pre-decision evidence available to baselines; require total responsibility one. Then P(c,u)=mu(c)alpha(u|c,theta) is invariant to package regrouping even though package-label mass can change.
6. **Quotient credit.** Write independently verified feedback once to the semantic cell/primitive responsibility and distribute it with weights summing to one before package bookkeeping. A clone/grouping operation therefore cannot multiply total semantic credit or create an independent future state update.
7. **Transformation audit.** Measure representation sensitivity under frozen split/merge transformations before scaling the evolution run.

Validator-gated/rejection realization is a **shared non-novel backend**, not the method contribution. C3 is not established until P0/full experiments show realized invariance without utility, coverage, or resource loss.

## 5. Evidence Before Dynamic P0

### 5.1 First-party control-plane phenomenon

Skill-SP released validator-covered API-Bank rows: 348. Multi-membership rows: 183 (52.6%). Five specific/generic support-overlap pairs cover 14 answer tools. Exact semantic-ID splitting changes equivalence-class sampler mass for every released skill tested.

SkillRL independent first-party replication: exact-content fresh-ID clones are accepted, and fixed-budget retrieval composition changes for most clone interventions.

### 5.2 Strongest simplifications

Minimum-cardinality whole-package pruning preserving all 348 covered tasks reduces 10 active packages to 7 but leaves 71 multi-membership rows. Every retained package has globally unique support, so further deletion loses coverage.

Arbitrary nonnegative context-independent global package weighting cannot equalize semantic-context exposure. Optimum max/min ratio is 2.0; the two theorem witnesses certify the same lower bound without relying on the optimizer.

## 6. Decisive P0

### 6.1 P0-A: faithful dynamic phenomenon

Substrate: released Skill Self-Play tool-call workflow at author commit bb693c8, Qwen3-8B, frozen vLLM runtime on host 231.

Generate one shared bank of 24 outputs for each of skill_003, skill_004, skill_015 (72 model generations total). Reuse this exact bank for all counterfactual arms; no arm-specific generation.

Arms:
- split: weights (1/3, 1/3, 1/3);
- merge_003_015: weights (1/4, 1/2, 1/4);
- merge_004_015: weights (1/2, 1/4, 1/4).

Independent truth: author parser + question contract + all 15 released package validators.

Qualification: >=16/24 contract-valid per source. Qualification failure is INVALID/INCONCLUSIVE and cannot update scientific belief.

For **each** mandatory-overlap witness, require jointly:
- validator-pattern TV >= 0.05;
- bootstrap lower95 TV >= 0.025;
- max single-pattern probability shift >= 0.04.

GO only if both witnesses pass. STOP if neither passes. Exactly one passing witness is INCONCLUSIVE.

**P0-A result:** [LOCKED PLACEHOLDER]

### 6.2 P0-B: local SQC feasibility

Run only if P0-A GO. Reuse the identical frozen raw generation bank/SHA; zero additional proposer calls. Test whether quotient/rejection realization can meet the support-atom target within the same proposal/validator budget.

**P0-B result:** [LOCKED PLACEHOLDER]

### 6.3 Optional P0-C: frozen-solver one-step consequence

Run only if P0-A GO and bind the exact P0-A raw SHA. Evaluate every contract-valid generated task once with the same frozen Qwen3-8B author-style solver, using 3 solver samples per task and the sample's frozen reference tool-call truth. No arm-specific solver evaluation and no new questioner generation are allowed.

Compute each split/merge expected solver correctness by reweighting the same source-conditioned task/solver outcomes. For each merge, require the 95% task-bootstrap interval of the signed expected-correctness delta versus split to lie entirely above +0.05 or below -0.05. Both merges passing is STRONG_GO; exactly one is transformation-specific partial evidence; neither passing means no one-step utility consequence is established. P0-C does not unlock end-of-evolution C4 by itself.

**P0-C result:** [LOCKED PLACEHOLDER]

## 7. Leakage-safe Full Experiment, only after P0-A + P0-B GO

### 7.1 Frozen split

Tool-disjoint split STRI-API-BANK-L1-TOOL-DISJOINT-v1:
- calibration tools: AppointmentRegistration, ModifyRegistration, QueryHealthData, RecordHealthData;
- heldout tools: CancelRegistration, EmergencyKnowledge, QueryRegistration, SymptomSearch;
- calibration rows: 49;
- heldout rows: 54;
- both partitions contain all five semantic atoms and both mandatory-overlap witnesses.

Heldout frequencies may not update support atoms, prior, thresholds, or stop rules.

### 7.2 Primary matched factorial

2 controllers x 3 taxonomy representations:
- strongest optimal-global pre-context package allocation;
- SQC;

crossed with:
- split;
- merge_003_015;
- merge_004_015.

Same proposer, validators, implementation prompts, Qwen3 backbone, solver/evaluator, calibration data, heldout data, seeds, proposer/validator calls, solver rollouts, update steps, training tokens, wall-clock ceiling.

Primary causal contrast: controller x taxonomy interaction. Optimal-global should retain representation dependence; SQC must satisfy the frozen equivalence margin under both merges without utility, coverage, or resource loss.

### 7.3 Confirmatory gates

Native/optimal sensitivity, each merge:
- TV point >=0.05;
- bootstrap lower95 >=0.025;
- max pattern shift >=0.04.

SQC invariance, each merge:
- bootstrap upper95 TV <=0.025;
- max pattern shift <=0.02.

Heldout utility:
- in every taxonomy cell, paired/cluster-bootstrap lower95 of SQC_success - optimal_global_success > -0.02.

Coverage:
- 5/5 semantic atoms, zero loss.

Resources:
- identical primary proposer/validator/solver caps; rejected candidates consume budget.

### 7.4 Baselines

- author native controller/deployment reference;
- author text/name duplicate filter;
- exact-clone dedup;
- minimum full-coverage whole-package pruning;
- uniform package sampling;
- optimal global package reweighting;
- SkillsVote-style low-redundancy recommendation/attribution if reproducible;
- post-context context-conditioned simplex/router where the task context is legitimately available;
- SQC.

## 8. Main figures and tables

**Figure 1 — Representation dependence.** Same semantic support, different package partition. Show split versus merge and how package counting changes mass on the two mandatory-overlap regions.

**Figure 2 — Structural lower bound.** Minimal support hypergraph witness with exclusive rows and overlap row; theorem gives max/min >=2. Overlay the released Skill-SP witness counts and LP optimum 2.0.

**Figure 3 — Dynamic matched replay.** One Qwen3 source-conditioned generation bank feeds split and both merge mixtures. Plot validator-pattern distributions and preregistered TV/CI for both witnesses. [P0-A placeholder]

**Figure 4 — Full controller x taxonomy interaction.** Transformation distance for optimal-global versus SQC under both merges, with equivalence/sensitivity thresholds. [full placeholder]

**Table 1 — First-party evidence and simplifications.** Skill-SP + SkillRL phenomenon; dedup/pruning/global-weight reductions.

**Table 2 — Decisive P0.** Qualification, two witness TV/lower95/max-shift, P0-B realization feasibility/cost.

**Table 3 — Main 2x3 matched factorial.** Taxonomy, controller, transformation distance, heldout success, 5-atom coverage, proposer calls, validator calls, solver rollouts, wall/GPU hours.

**Table 4 — Ablations.** Remove quotient credit; uniform versus calibration prior; text/name Jaccard instead of released support; pruning/global-weight controls.

## 9. Reviewer-critical falsifiers

The standalone paper must be stopped or narrowed if any of the following occurs:

- P0-A qualified STOP: C4 dies; do not execute full experiment.
- P0-B STOP: current SQC realization dies; revise Paper Design rather than scaling.
- Native/deployment reference fails to retain representation sensitivity under both merges: narrow to control-plane/theory diagnosis.
- SQC fails frozen equivalence on either merge: C3 dies.
- SQC violates 2pp heldout utility non-inferiority in any taxonomy cell: C3 dies.
- SQC loses any heldout semantic atom: C3 dies.
- SQC needs a larger primary proposer/validator/solver budget: primary C3 fails.
- Heldout information changes support atoms, prior, thresholds, or stop rules after unblinding: invalidate confirmatory run.
- A same-information baseline at the same decision time matches SQC on invariance and utility/cost: stop standalone method novelty; retain STRI only as a diagnostic principle.

## 10. Current paper-convergence status

- Problem: FROZEN.
- Mechanism: FROZEN, with real support-graph witnesses and a tight lower bound.
- Strongest same-information baseline class: FROZEN by decision-time information boundary.
- Method: FROZEN at SQC principle/realization design, but C3 not yet authorized.
- Positive real evidence: C1/C2 YES.
- Faithful dynamic positive: PENDING P0-A.
- Method feasibility positive: PENDING P0-B.
- Full experiment: LOCKED.
- Paper claim C3/C4: LOCKED.

Target transition after a P0-A GO and P0-B PASS: **PAPER-CONVERGENCE-GO-CANDIDATE**, immediately start prose/results integration without reopening idea search or changing the frozen heldout design.
