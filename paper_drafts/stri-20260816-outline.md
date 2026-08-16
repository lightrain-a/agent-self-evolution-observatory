# Self-Evolution Should Not Depend on How Skills Are Split

**STRI — ICLR paper-first outline**
Status: C1/C2 supported. C3/C4 locked behind frozen P0-A/P0-B.

## Thesis
Self-evolving skill systems often use package IDs as curriculum, retrieval, credit, and refinement units. If the content-addressed primitive executable basis is unchanged, duplicating package identities or grouping/ungrouping those same primitives should not change the induced semantic evolution process merely because the package representation changed. We call this Skill-Taxonomy Representation Invariance (STRI).

## Evidence already established

### Skill Self-Play
- 530 released API-Bank Level-1/3 rows; 348 are covered by released validators.
- 183/348 covered rows have multiple released skill memberships.
- Released text/name Jaccard dedup misses all observed specific–generic overlap pairs used in the audit.
- Minimum-cardinality whole-package pruning preserving exact support still leaves 71/348 overlap rows.
- Arbitrary nonnegative global package weighting cannot equalize semantic-context exposure: optimal max/min ratio = 2.0.

### SkillRL
- Exact-content fresh-ID clones accepted for 12/12 released general skills.
- Across 223 released ALFWorld task descriptions, 11/12 clone targets change the unique semantic retrieval set at fixed top-k=6.
- 5/12 reduce the number of unique general-skill contents returned.

## Formal setup
Let X be semantic contexts. Let U be a frozen **content-addressed primitive semantic basis**, not a set of package IDs. A primitive fingerprint hashes immutable implementation/contract material (skill content, rules, validator and validator specification) and excludes mutable sampling statistics. Each primitive u has a frozen first-party support predicate V_u(x) and applicability A_u={x:V_u(x)=1}.

A taxonomy T consists of package identities S_T plus a grouping map M_T(s) subseteq U. A claimed semantics-preserving transformation may duplicate a package identity that points to the same primitive, or group/ungroup unchanged primitives into macro packages. It may not modify primitive content/support predicates, invent a semantic subskill, or add capability.

Package selection p_T(s|z) is mapped to primitive mass through an explicit within-package responsibility rho_T(u|s,z), supported on M_T(s) and summing to one. Thus

m_T(u|z)=sum_s p_T(s|z) rho_T(u|s,z).

This is necessary for macro packages: selecting one macro does not give its full probability independently to every constituent primitive.

The semantic quotient is defined on context space, independently of package grouping:

x ~_U x' iff V_u(x)=V_u(x') for every frozen primitive u.

The quotient C_U=X/~_U consists of support-signature cells sigma_U(c)={u:V_u(x)=1}. Because U and V_u are frozen/content-addressed, these cells are unchanged by the claimed package duplication/grouping transformations.

For a support cell c, additive **eligibility exposure** is

E_T(c|z)=sum_{u in sigma_U(c)} m_T(u|z).

E is a control-opportunity measure, not a probability distribution and not task utility. Separately, Q_T(c|z) denotes the actual qualified task distribution emitted by the proposer/realization pipeline. Static theory concerns E; P0-A tests whether representation changes propagate to Q; longitudinal utility is C4 and remains empirical.

## Theorem 1 — Mandatory-overlap lower bound
Suppose frozen primitives u_a,u_b each have an exclusive support cell and share an overlap cell. Let m be the minimum positive additive eligibility exposure. Exclusive cells require primitive masses m(u_a) >= m and m(u_b) >= m; therefore the overlap cell has exposure at least m(u_a)+m(u_b) >= 2m. Hence every nonnegative primitive-mass vector induced by a pre-context single-package controller obeys

max_x E(x) / min_x E(x) >= 2.

The released Skill-SP graph has two independent witnesses: (skill_003, skill_015) and (skill_004, skill_015). The LP optimum is exactly 2, so the lower bound is tight.

## Theorem 2 — Frozen-state decision-time controller-class reduction
Released Skill-SP executes `sample_skill()` before `build_questioner_messages(skill)` and before the proposer task exists. At a **frozen pre-task state z**, the action is exactly one package identity. Therefore every randomized same-information controller over that unchanged action space is characterized pointwise by one categorical p_T(s|z); combined with the fixed responsibility channel rho_T it induces one nonnegative primitive-mass vector m_T(.|z), which lies in the additive exposure class constrained by Theorem 1.

This closes the generic learned pre-context single-package reduction **at a frozen state**. It does not say that a longitudinal adaptive bandit/neural controller is globally equivalent to one fixed categorical vector, nor does it prove long-run utility harm. State evolution and propagation are exactly why C4/P0 remain empirical. Contextual routers remain valid for post-context retrieval/credit surfaces.

## Method hypothesis — Support-Quotient Control
SQC changes the control object rather than claiming a new proposer or validator. Its quotient is the actual equivalence relation on context space induced by the frozen content-addressed primitive support signatures.

1. Freeze U and V_u independently of method outcomes; mutable package statistics are not part of primitive identity.
2. Construct C_U=X/~_U from equal primitive-support signatures.
3. Allocate curriculum/control mass mu(c) on support cells under a frozen calibration prior, not on current package identities.
4. Choose primitive implementation responsibility alpha(u|c) only for u in sigma_U(c), with total responsibility one.
5. Map the chosen unchanged primitive through the current taxonomy representation. Use validator-gated rejection only as a **shared non-novel realization backend**; rejected candidates consume budget.
6. Write verified feedback once to the semantic cell/primitive responsibility and conserve total credit before package-specific bookkeeping.

Exact clone identities therefore do not create new primitive dimensions; macro grouping changes only the representation channel. C3 is not established until dynamic/heldout experiments show realized invariance without utility, coverage, or cost loss.

## Current-source boundary
Concede:
- SkillClone: clone prevalence/detection/dedup.
- SkillsVote: redundant/environment-sensitive skill governance.
- Skill-SP / ERSkill: dynamic skill controllers and co-evolution.
- SkillMisevo / Agent Skills Can Be Harmful: unsafe/harmful skill content and reuse.
- SkillZip: internal skill compression.
- fixed-arm contextual-bandit/overlapping-expert theory: similarity-aware control for fixed action sets.

Residual: representation invariance of an **endogenously evolving taxonomy whose package identities themselves define upstream control units**, especially mandatory partial overlap that cannot be removed by package pruning/global weighting.

## Decisive P0

### P0-A — faithful dynamic propagation
- Author Skill-SP commit bb693c89...
- Single author-published backbone: Qwen3-8B.
- Exact vLLM/runtime/model/prompt/validator preflight PASS on host 231.
- Generate 24 source-conditioned tasks each for skill_003, skill_004, skill_015 exactly once.
- Reuse the same 72-output banks for split and two merge counterfactuals; no arm-specific generation.
- Qualification: >=16 contract-valid samples per source; failure is INVALID, never scientific STOP.
- Both real mandatory-overlap merges must pass frozen TV/lower95/max-shift gates for GO.

### P0-B — zero-extra-GPU quotient feasibility
Only after P0-A GO. Reuse exact P0-A raw SHA; no new model calls. Online/no-lookahead validator rejection must realize all five semantic cells 3 times each within the original 72 total / 24-per-source calls. GO is local feasibility only, not utility evidence.

## Leakage-safe full experiment
Frozen tool-disjoint Level-1 split:

Calibration tools: AppointmentRegistration, ModifyRegistration, QueryHealthData, RecordHealthData.
Heldout tools: CancelRegistration, EmergencyKnowledge, QueryRegistration, SymptomSearch.

Both partitions contain all five semantic cells and both theorem witnesses; tool and row identities are disjoint.

Calibration empirical semantic prior is frozen before heldout outcomes:
[0.1702, 0.0638, 0.0638, 0.3617, 0.3404].
Heldout atom frequencies cannot change this prior or the quotient structure.

Primary matched factorial after P0:
- controller: optimal-global package allocation vs SQC;
- taxonomy: split vs merge(003,015) vs merge(004,015).

Both controllers share the identical validator-rejection backend, proposer/validator/solver/update budgets, and seeds. Author-native Skill-SP is a separate deployment reference because its realization differs.

Frozen confirmatory gates:
- native meaningful sensitivity: TV >=0.05, bootstrap lower95 >=0.025, max pattern shift >=0.04 for both merges;
- SQC invariance: bootstrap upper95 TV <=0.025 and max pattern shift <=0.02 for both merges;
- heldout utility: SQC non-inferior within 2 absolute percentage points in every taxonomy cell;
- semantic coverage: 5/5 cells, no atom loss;
- no extra primary proposer/validator/solver budget.

## Paper figures/tables
1. Figure: same primitive support, different package taxonomy; package mass changes, semantic quotient does not.
2. Figure: real Skill-SP support graph with two tight factor-2 witnesses.
3. Figure: decision-time timeline showing task context unavailable at upstream sampling.
4. Table: two-system control-plane replication.
5. Table: reduction tournament (dedup, pruning, global weights, theorem).
6. Table: P0-A/P0-B.
7. Table/Figure: heldout controller x taxonomy utility/invariance/resource frontier — only after results exist.

## Failure-first interpretation
- P0-A qualified negative -> keep C1/C2, drop C4 and do not rescue with another backbone.
- P0-B STOP -> current SQC realization insufficient; no adaptive P0 repair.
- SQC fails either merge equivalence -> stop C3.
- SQC loses heldout utility/coverage or needs more primary resource -> stop C3.
- Any heldout leakage into prior/atoms/thresholds -> invalidate confirmatory run.

## Current execution state
All pre-outcome scientific design is frozen in Git. P0-A is READY_EXCEPT_GPU_RESOURCE_BUSY on host 231; unrelated Aegis processes currently occupy the A100. No preemption, model migration, second backbone, or runtime substitution is authorized.
