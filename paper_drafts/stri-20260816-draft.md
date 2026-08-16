# Self-Evolution Should Not Depend on How Skills Are Split

> STRI — body-level ICLR draft. C1/C2 are currently supported; C3/C4 remain explicitly locked behind the frozen P0-A/P0-B/P0-C chain. Numerical result placeholders marked `TBD-P0` must not be filled from exploratory or invalid runs.

## Abstract

Self-evolving language-model agents increasingly treat reusable skills as persistent control objects: a skill identity can determine which tasks are generated, which experiences are retrieved, where feedback is credited, and which artifacts are refined next. This creates a basic invariance question that existing skill systems do not explicitly enforce: if two skill taxonomies expose the same executable semantic capabilities but differ only in how those capabilities are split, cloned, or grouped into package identities, should the resulting self-evolution process change?

We study **Skill-Taxonomy Representation Invariance (STRI)**. Two released self-evolving skill systems provide independent first-party witnesses of representation sensitivity. In Skill Self-Play (Skill-SP), 183 of 348 released-validator-covered API-Bank tasks belong to multiple released skills, and the released text duplicate filter misses all five observed specific–generic support-overlap pairs. Exact-coverage whole-package pruning still leaves 71 overlapping rows. More strongly, on the irreducible released support graph, no nonnegative pre-context package weighting can equalize additive semantic exposure: two independent mandatory-overlap witnesses force a tight max/min exposure ratio of at least 2. In SkillRL, exact-content skills with fresh dynamic identities are accepted by the released updater interface and alter the fixed-budget semantic retrieval set for 11 of 12 tested released general skills.

These observations motivate **Support-Quotient Control (SQC)**, which moves allocation and credit from mutable package identities to a taxonomy-independent quotient defined by frozen content-addressed primitive support. We prove static exposure and credit-conservation properties under the claimed semantics-preserving transformation class. We then preregister a faithful Qwen3-8B Skill-SP P0 and a leakage-safe heldout factorial that separate three questions: whether representation sensitivity propagates through the native task-generation pipeline, whether the quotient can be realized at matched proposer/validator cost, and whether invariance can be achieved without utility or coverage loss. The dynamic and utility claims are intentionally left conditional until those frozen experiments run.

## 1. Introduction

A growing class of agents improves without changing foundation-model weights. Instead, the agent accumulates or evolves external state: memories, skills, workflows, tools, prompts, routing policies, or harness code. Skills are especially attractive because they package reusable procedural knowledge into an object that can be retrieved, evaluated, revised, and composed. Recent systems use skills not only as passive context but as **control units of evolution**. A sampled skill may condition the next generated task; a skill ID may receive success/failure credit; dynamic IDs may receive retrieval priority; repeated evidence may trigger refinement or retirement.

This makes the representation of the skill library scientifically consequential. Suppose two packages expose the same executable primitive, or one macro package groups two unchanged primitives that were previously separate. If no new capability, validator support, or executable content has been introduced, should an agent's future training curriculum or retrieval budget change merely because the package representation changed?

Existing work gives strong reasons to care about redundancy, but does not answer this invariance question. SkillClone studies semantic clones and clone propagation [arXiv:2603.22447]. SkillsVote governs redundant and environment-sensitive skills [arXiv:2605.18401]. SkillMisevo studies unsafe skill evolution and later reuse [arXiv:2608.12851]. Agent Skills Can Be Harmful attributes functional and efficiency regressions to loaded skills [arXiv:2608.11888]. ERSkill co-evolves retrieval skills and a router [arXiv:2608.12720], while Skill Self-Play co-evolves a proposer, solver, and skill controller [arXiv:2607.22529]. SkillZip compresses repeated internal skill structure [arXiv:2608.11079]. These systems motivate better skill governance, but a system can detect duplicates, route adaptively, or compress aggressively and still assign evolution mass to package identities in a way that changes under a semantics-preserving reparameterization.

We start from released implementations rather than a proposed method. **Skill-SP provides a partial-overlap witness.** Across 530 bundled API-Bank Level-1/3 rows, released validators cover 348. Of these, 183 (52.6%) are accepted by multiple released skills. The released name+description Jaccard duplicate filter misses all five observed support-overlap pairs. Removing redundant whole packages as aggressively as possible while preserving complete released support still leaves 71 overlapping tasks. Even allowing arbitrary nonnegative global package weights cannot equalize exposure over all covered tasks: the optimal max/min exposure ratio is 2.0.

**SkillRL provides an independent identity witness.** Its released template-mode SkillBank admits a fresh dynamic skill whenever the new `skill_id` is distinct. For each of 12 released general skills, we add an exact-content copy with a fresh dynamic ID through the official interface. All 12 are accepted. Across 223 released ALFWorld task descriptions, 11/12 counterfactual targets change the unique semantic retrieval set under fixed `top_k=6`, and 5/12 reduce the number of unique general-skill contents returned.

The important residual is therefore narrower than “redundant skills are harmful.” The scientific object is the **invariance of an endogenous self-evolution controller to semantics-preserving taxonomy representation**.

We make four claims, two current and two conditional:

1. **C1 — Real representation sensitivity.** Released self-evolving skill controllers can change curriculum or retrieval control when only skill identity/grouping changes while semantic support is held fixed.
2. **C2 — A structural residual beyond package fixes.** On the released Skill-SP support graph, text deduplication, exact-coverage package pruning, and the entire frozen-state pre-context single-package controller class cannot remove mandatory partial-overlap exposure distortion.
3. **C3 — Support-quotient control.** *Locked until P0/full experiments.* SQC should remove taxonomy-representation dependence without sacrificing semantic coverage, matched resource efficiency, or heldout utility.
4. **C4 — Dynamic consequence.** *Locked until P0/full experiments.* Native representation sensitivity should propagate to realized qualified tasks or later evolution outcomes under a faithful author workflow.

The key methodological move is to change the object that carries mass and credit. SQC defines a frozen content-addressed primitive basis and a quotient over semantic context according to identical primitive-support signatures. Curriculum mass is allocated over quotient cells; implementation responsibility then maps that mass to unchanged primitives and finally to the current package representation. Package duplication can change labels, but cannot create new semantic mass or duplicate verified credit.

Our experiments are deliberately failure-first. A faithful Qwen3-8B Skill-SP P0 must first show that two real mandatory-overlap merge/split transformations change the realized qualified semantic task distribution. If that qualified dynamic effect is absent, C4 stops on the preregistered backbone and no second-backbone rescue is permitted. If the effect is present, a zero-extra-generation P0 tests whether a shared validator-gated rejection backend can realize the support quotient within the identical 72-call source bank. Only after both gates pass does the heldout method comparison execute.

## 2. Problem: Representation Invariance of Self-Evolution

Let `U` denote a frozen set of **content-addressed executable semantic primitives**. A primitive is not a package ID. Its fingerprint contains immutable skill content and executable/verification contract material, while excluding mutable sampling and evolution statistics. For each primitive `u`, let `V_u(x)` be a frozen first-party support predicate and `A_u={x:V_u(x)=1}`.

A taxonomy `T` contains package identities `S_T` and a grouping relation `M_T(s) subseteq U`: package `s` exposes one or more unchanged primitives. The claimed semantics-preserving transformation class includes identity duplication, package grouping/merge, and package ungrouping. It excludes transformations that modify primitive content, modify `V_u`, invent semantic subskills, or add executable support.

At frozen pre-task state `z`, let `p_T(s|z)` be the probability of choosing package `s`. For macro packages we define a normalized within-package responsibility `rho_T(u|s,z)` supported on `M_T(s)` and summing to one. The induced primitive mass is

`m_T(u|z) = sum_s p_T(s|z) rho_T(u|s,z)`.

Define the semantic quotient by

`x ~_U x' iff V_u(x)=V_u(x') for every frozen primitive u`.

This yields `C_U = X / ~_U`; each support cell `c` is identified by the primitive support signature `sigma_U(c)`. Because `U` and `V_u` are frozen, the quotient is invariant to package duplication/grouping/ungrouping in the claimed class.

We distinguish four levels of STRI: **STRI-E**, additive eligibility/control exposure; **STRI-Q**, the realized qualified semantic-task distribution emitted by the proposer; **STRI-G**, conservation of semantic feedback/credit; and **STRI-D**, the longitudinal/end-of-evolution process. The static theory establishes only the first and conditional credit properties. STRI-Q and STRI-D remain empirical.

## 3. Structural Mechanism

### 3.1 Mandatory-overlap lower bound

For a support cell `c`, define additive eligibility exposure

`E_T(c|z) = sum_{u in sigma_U(c)} m_T(u|z)`.

This is a control-opportunity measure, not a probability distribution over tasks and not task utility.

**Theorem 1 (mandatory-overlap additive-exposure lower bound).** Suppose two frozen primitives `u_a,u_b` each have a globally singleton support cell—support signatures exactly `{u_a}` and `{u_b}` over the full frozen primitive universe—and also share an overlap cell containing both. Let `r=min_c E(c)>0` over the focal cells. Then every nonnegative normalized primitive-mass vector obeys

`max_c E(c) / min_c E(c) >= 2`.

**Proof.** Because the singleton cells contain no other supported primitive, their exposures equal `m(u_a)` and `m(u_b)`; therefore `m(u_a)>=r` and `m(u_b)>=r`. Their shared cell has exposure at least `m(u_a)+m(u_b)>=2r`. Therefore the max/min ratio is at least two. □

The released Skill-SP support graph supplies two independent witnesses: `(skill_003, skill_015)` and `(skill_004, skill_015)`. A linear program that may set redundant package weights to zero and freely reweight every remaining package attains ratio exactly `2.0`, so the bound is tight on the released graph.

The theorem is deliberately narrow: it proves a structural property of additive eligibility exposure and does not imply lower task accuracy, regret, or end-of-evolution utility.

### 3.2 Decision-time controller-class reduction

A natural objection is that global weights are too weak and that an expressive learned router could escape the bound. The released causal order closes this objection for the upstream decision at a frozen state.

Skill-SP executes `sample_skill()` before `build_questioner_messages(skill)` and before the proposer task exists. The upstream action is exactly one current package identity. Therefore at frozen state `z`, every randomized same-information controller—rule, MLP, bandit, or neural policy—induces one categorical `p_T(s|z)`. Combined with the fixed representation channel `rho_T`, it induces one nonnegative primitive-mass vector and remains in the class covered by Theorem 1.

**Theorem 2 (frozen-state pre-context single-package controller reduction).** At a frozen pre-task state with a single-package action space, any randomized same-information controller is pointwise characterized by a categorical distribution over package identities and is therefore subject to Theorem 1 whenever the mandatory-overlap assumptions hold.

This result is pointwise. It does not identify an entire longitudinal adaptive policy with one fixed vector. Longitudinal state evolution is exactly why STRI-D remains empirical.

## 4. Support-Quotient Control

SQC changes the control object rather than proposing a more expressive package router.

### 4.1 Freeze primitive semantics

Before method outcomes are observed, SQC freezes the content-addressed primitive basis, first-party support predicates, and semantic quotient. Mutable attempts, quality estimates, and evolution statistics cannot change primitive identity.

### 4.2 Allocate mass on quotient cells

Let `mu(c)` be a frozen distribution over support cells. In the confirmatory experiment, `mu` is estimated only from a calibration partition and cannot be updated from heldout atom frequencies.

SQC first targets a support cell under `mu`, then chooses primitive responsibility

`alpha(u|c,theta), u in sigma_U(c), sum_u alpha(u|c,theta)=1`,

using only pre-decision evidence available to the matched baseline. State `theta` is keyed by content-addressed primitive or support cell rather than independently by cloned package IDs. The joint semantic mass is

`P(c,u)=mu(c) alpha(u|c,theta)`.

If package grouping changes but the primitive basis, quotient, prior, and primitive state are fixed, package labels may change while `P(c,u)` does not.

### 4.3 Realization is shared infrastructure

A generative curriculum still needs to turn a target support cell into a task. When no native support-conditioned proposer exists, we use validator-gated rejection under a preregistered call budget. This backend is **not** a novelty claim. It is shared identically with the strongest matched package baseline, and every rejected candidate consumes proposer/validator budget.

### 4.4 Quotient credit

For independently verified feedback `g(c,y)`, SQC distributes primitive credit as

`Delta_u = alpha(u|c) g(c,y)`.

Because responsibilities sum to one, total primitive credit equals `g(c,y)`. Package duplication or regrouping therefore cannot multiply total semantic credit when package bookkeeping is derived from the conserved primitive update.

## 5. First-Party Evidence Before Method Evaluation

### 5.1 Skill-SP: real partial support overlap

We audit all 530 API-Bank Level-1/3 rows bundled with the released Skill-SP repository at commit `bb693c89...`. Released validators accept 348 rows; 183 are multi-membership. The observed overlaps span five specific–generic pairs and 14 answer tools.

The released name+description Jaccard duplicate filter at threshold `0.33` misses all five support-overlap pairs, whose textual similarities are only `0.1429–0.20`. Thus the overlap is not a trivial text-duplicate artifact.

A stronger baseline deletes as many packages as possible while preserving the entire released support. Minimum-cardinality exact-coverage pruning reduces the active set to seven skills but still leaves `71/348` covered rows multi-membership. The residual overlap cannot be removed by deleting whole packages without losing uniquely supported regions.

Finally, arbitrary nonnegative global package reweighting under positive coverage of every task yields optimal max/min exposure ratio `2.0`. The theorem witnesses explain why no context-independent package allocation can improve on that optimum.

### 5.2 SkillRL: exact-content identity multiplicity affects retrieval

We independently audit SkillRL at released commit `8e66726e...`. In template mode, dynamic general skills receive priority and the remaining `top_k=6` budget is filled with static skills. The released `add_skills()` path rejects duplicate IDs rather than duplicate semantic content.

For each of 12 released general skills independently, we add an exact content clone with a fresh `dyn_NNN` identity. All 12 are admitted. Across 223 released ALFWorld task descriptions, 11/12 clone targets change the unique semantic general-skill retrieval set and 5/12 reduce the number of unique general-skill contents returned under the same fixed budget.

The two systems expose different mechanisms—upstream curriculum overlap in Skill-SP and fixed-budget retrieval identity in SkillRL—but the shared scientific phenomenon is representation sensitivity.

## 6. Relation to Existing Work

We explicitly concede neighboring claims. SkillClone [arXiv:2603.22447] directly studies semantic skill clones and clone propagation; STRI does not claim clone prevalence or duplicate detection. SkillsVote [arXiv:2605.18401] governs redundant/environment-sensitive skills; STRI asks whether semantics-preserving taxonomy reparameterization changes the control law at all. SkillMisevo [arXiv:2608.12851] and Agent Skills Can Be Harmful [arXiv:2608.11888] study unsafe or harmful skill content; our transformations hold primitive content/support fixed. ERSkill [arXiv:2608.12720], Skill-SP [arXiv:2607.22529], and SHAPER [arXiv:2608.11350] establish evolving skills, routers, and harnesses; they are evidence systems rather than the method novelty. SkillZip [arXiv:2608.11079] compresses repeated internal structure, whereas STRI concerns invariance of the external evolution controller.

Classical similarity-aware contextual-bandit and stochastic-expert theory remains an important mature reduction. Our claim is narrower: in the released pre-context single-package action space, any same-information randomized controller induces a categorical package distribution at a frozen state, so the real mandatory-overlap lower bound applies pointwise. We do not claim new generic online-learning theory.

## 7. Decisive Experiments

The experiment chain is frozen before P0 outcomes.

### 7.1 P0-A: faithful native dynamic propagation

P0-A uses the released Skill-SP tool-call workflow, author commit `bb693c89...`, a single Qwen3-8B backbone, the author questioner prompt builder, vLLM generation, and all 15 released validators. The substrate preflight binds code, model, tokenizer, runtime, prompt, and validator hashes.

We generate exactly 24 tasks conditioned on each of `skill_003`, `skill_004`, and `skill_015`—72 generations total—with released settings: temperature `1.0`, top-p `0.95`, and max tokens `4096`. These three source-conditioned banks are generated once. Every taxonomy arm reuses the same bank; there is no arm-specific generation.

The split representation assigns source weights `(1/3,1/3,1/3)`. The two semantics-preserving mandatory-overlap merges use:

- `merge(003,015)`: `(0.25,0.5,0.25)` over source banks 003/004/015;
- `merge(004,015)`: `(0.5,0.25,0.25)`.

The macro exposes exactly the same underlying implementation prompts and validator support. Qualification requires at least 16 contract-valid samples per source. Qualification failure is INVALID and cannot update scientific belief.

For each merge, native sensitivity requires all three preregistered conditions: validator-pattern TV `>=0.05`; bootstrap lower-95% TV `>=0.025`; maximum single-pattern probability shift `>=0.04`.

**P0-A GO:** both merges pass.
**P0-A STOP:** neither passes.
**P0-A INCONCLUSIVE:** exactly one passes.

**Observed frozen P0-A:** `INCONCLUSIVE_PROPOSER_QUALIFICATION_FAILED`. All 72 preregistered generations completed, but contract-valid counts were `14/24`, `5/24`, and `8/24` for `skill_003`, `skill_004`, and `skill_015`, below the frozen `16/source` qualification gate. The merge witnesses were therefore not evaluated, and this run is neither P0-A GO nor scientific STOP. We do not retune or rerun the same P0-A contract.

### 7.2 P0-B: zero-extra-generation quotient feasibility

Only after P0-A GO, P0-B reuses the exact raw 72-record bank and requires no additional model calls. It asks whether the five-cell quotient can be realized under the original finite source-call budget using a shared online rejection backend.

The five frozen atoms are `003`, `004`, `015`, `003+015`, and `004+015`. P0-B targets each atom exactly three times under a preregistered source-responsibility schedule. Within each source, records are consumed in recorded order. Invalid or wrong-atom candidates still consume a proposer call. No future candidate may be inspected when deciding whether to accept the current one.

**GO:** all 15 targets are realized before any source exhausts its 24 calls.
**STOP:** at least one target cannot be realized within the frozen calls.

P0-B is local feasibility only. It cannot establish method superiority or downstream utility.

`TBD-P0-B: consumed calls by source/atom, rejections, feasibility decision.`

### 7.3 P0-C: optional one-step solver consequence

If P0-A GO, every contract-valid task in the same bank may be evaluated by the frozen author-style Qwen3-8B base solver, with three solver samples per task and independent reference tool-call grading. Split/merge expected correctness reuses the same task-level solver outcomes; there are no arm-specific solver calls.

P0-C is intentionally coarse. A consequence is considered clear only if the bootstrap interval of the representation-induced expected-correctness change lies entirely outside `+/-5` percentage points. It does not replace the stricter heldout 2pp non-inferiority test.

`TBD-P0-C: optional one-step expected-correctness contrast.`

### 7.4 Leakage-safe heldout confirmatory experiment

If P0-A and P0-B pass, we run a tool-disjoint API-Bank Level-1 evaluation.

Calibration tools: `AppointmentRegistration`, `ModifyRegistration`, `QueryHealthData`, `RecordHealthData`.

Heldout tools: `CancelRegistration`, `EmergencyKnowledge`, `QueryRegistration`, `SymptomSearch`.

The calibration partition has 49 rows and the heldout partition 54. Both contain all five semantic atoms and both theorem witnesses. The empirical calibration prior is frozen at `[0.1702,0.0638,0.0638,0.3617,0.3404]`. Heldout frequencies cannot change this prior, the quotient structure, thresholds, or stop rules.

The primary matched factorial is controller x taxonomy:

- **controller:** optimal-global package allocation vs SQC;
- **taxonomy:** split, merge(003,015), merge(004,015).

Both controllers use the identical validator-gated/rejection realization backend, proposer, validators, solver, seeds, update budget, and resource caps. The comparison therefore isolates the control-mass allocation law.

C3 requires all primary gates jointly:

1. Native/optimal representation sensitivity remains meaningful under both merges.
2. SQC invariance: bootstrap upper-95% TV `<=0.025` and max pattern shift `<=0.02` for both merges.
3. Heldout utility: within each taxonomy, lower-95% of `SQC_success - optimal_global_success > -0.02`.
4. Coverage: all five semantic atoms retained.
5. Resources: no larger primary proposer/validator/solver budget.

No secondary endpoint can rescue a failed primary gate.

`TBD-FULL: 2x3 factorial table, paired/cluster bootstrap, resource frontier.`

## 8. Falsifiability and Stop Rules

The design is intentionally easy to kill.

- If faithful P0-A is qualified but neither mandatory-overlap merge changes the realized semantic task distribution, C4 stops on the preregistered backbone. We do not switch to another backbone.
- If P0-B cannot realize all five atoms at matched call budget, the current SQC realization fails. We do not expand the source bank after observing failure.
- If SQC is invariant only because it drops a semantic atom, C3 fails.
- If SQC needs extra proposer, validator, or solver calls to meet the invariance gate, the primary C3 claim fails; only a secondary cost frontier may be reported.
- If optimal-global allocation matches SQC on invariance and utility under the same shared backend, SQC is unnecessary.
- If heldout information changes the semantic prior, quotient, or thresholds after unblinding, the confirmatory experiment is invalid.

These stop rules are not auxiliary safeguards; they define the paper's claim boundary.

## 9. Discussion

STRI separates **semantic capability** from **artifact multiplicity**. The problem is not that multiple skills may be useful for the same task. Overlap can be intentional and necessary. Indeed, the strongest Skill-SP witness survives exact-coverage pruning precisely because both specific and generic skills have unique regions while also sharing contexts. The failure is assigning additive control opportunity and independent evolution state to representation units in a way that makes this intentional overlap alter the induced semantic process.

This perspective explains why deduplication is incomplete. Exact clones can be quotiented cheaply, but partial overlap is not a duplicate relation. Removing a generic skill may delete a unique support region; removing a specific skill may do the same. A representation-invariant controller needs a conserved semantic object through which mass and credit factor.

The primitive basis is therefore a central assumption. Our current theory uses first-party validator support as an independently frozen semantic contract. This gives unusually strong observability on Skill-SP, but many real skill libraries will not expose exact validators. Approximate or learned support estimation introduces a new identification problem and is outside the present core claim.

Static STRI-E is also not sufficient evidence of practical harm. The actual proposer may wash out eligibility differences, or downstream solver performance may be insensitive to the resulting task mixture. We therefore refuse to infer C4 from the factor-2 theorem alone. P0-A is designed to test exactly whether the structural effect propagates to the realized task distribution.

## 10. Limitations

1. **Validator-defined semantics.** The strongest current evidence uses released validators to define support. Systems without reliable applicability contracts may require uncertainty-aware quotient construction.
2. **Transformation class.** We cover identity duplication and grouping/ungrouping of unchanged content-addressed primitives. We do not claim arbitrary semantic decomposition or learned ontology induction.
3. **Pointwise controller theorem.** The controller-class reduction is pointwise at a frozen pre-task state. It does not collapse a longitudinal adaptive policy to one static vector.
4. **Dynamic evidence unresolved.** The preregistered Qwen3 P0-A completed its 72-call bank but failed the frozen proposer-qualification gate before any dynamic witness was admissible. C3/C4 therefore remain locked; the failed bank is treated as a substrate failure asset rather than a negative STRI result, and the same P0-A is not rerun.
5. **Two-system control-plane replication, one primary dynamic substrate.** SkillRL supplies an independent representation-sensitivity witness, while the decisive dynamic method experiment uses Skill-SP because it exposes first-party support/validation suitable for matched counterfactuals.

## 11. Claim/Evidence Status

| Claim | Current status | Evidence required before final paper |
|---|---|---|
| C1: real representation sensitivity | Supported | retain exact first-party provenance on Skill-SP + SkillRL |
| C2: irreducible package-only residual | Supported | theorem + real graph witnesses + tight LP |
| C3: SQC removes dependence without loss | **LOCKED** | current P0-A is inconclusive; requires a different faithful dynamic substrate before any method-success claim |
| C4: dynamic/utility propagation | **LOCKED** | current native P0-A failed proposer qualification; requires a different faithful dynamic/independent-truth substrate |

## Planned Figures and Tables

1. **Fig. 1:** Same primitive semantic basis, different package taxonomies; package mass changes while quotient cells remain fixed.
2. **Fig. 2:** Released Skill-SP support graph with two mandatory-overlap factor-2 witnesses.
3. **Fig. 3:** Decision-time timeline showing skill sampling precedes task generation.
4. **Table 1:** Two-system control-plane replication (Skill-SP and SkillRL).
5. **Table 2:** Reduction tournament: text dedup, exact-clone dedup, full-coverage pruning, optimal global weights, theorem.
6. **Table 3:** P0-A/P0-B/P0-C with invalid/stop/go distinctions explicit.
7. **Table 4 / Fig. 4:** Heldout controller x taxonomy invariance/utility/resource comparison, only if P0 gates permit execution.
