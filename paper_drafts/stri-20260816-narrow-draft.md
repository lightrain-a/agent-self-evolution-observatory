# Self-Evolution Should Not Depend on How Skills Are Split

> Narrow ICLR draft after the preregistered dynamic P0-A failed proposer qualification. Submission claims are restricted to representation-invariance problem definition, exact support-geometry certificate, released-system control evidence, and real positive/negative mechanism boundaries. SQC and dynamic utility claims are future work.

## Abstract

Self-evolving language-model agents increasingly use skill identities as control objects: a sampled skill can determine the next training task, a dynamic ID can receive retrieval priority, and feedback is often written back to the selected package. This creates a basic representation question. If two skill libraries expose the same semantic capabilities but differ only in how those capabilities are split, cloned, or grouped into package identities, should the induced self-evolution control change?

We formulate **Skill-Taxonomy Representation Invariance (STRI)** and show that released self-evolving skill systems can violate it. In Skill Self-Play (Skill-SP), 183 of 348 released-validator-covered API-Bank tasks belong to multiple released skills; the release's text duplicate filter misses all observed specific–generic support-overlap pairs, and exact-coverage package pruning still leaves 71 overlapping tasks. In SkillRL, exact-content skills with fresh dynamic IDs are accepted 12/12 times, and 11/12 such identity changes alter the unique semantic contents returned under a fixed retrieval budget.

We then identify the mechanism more precisely than "overlap." For a frozen context-by-package support matrix `A`, define the exact package-only exposure distortion

`R*(A) = min_{w>=0,t} t  subject to  1 <= A w <= t 1`.

We prove that `R*=1` iff nonnegative package weights can equalize additive semantic exposure over all covered contexts, while `R*>1` is the tight minimum multiplicative distortion. A simple global-singleton-plus-overlap pattern gives the interpretable lower bound `R*>=2`. On Skill-SP API-Bank Level-1, `R*=2`; the same value independently holds on a preregistered calibration subset and a tool-disjoint heldout subset. Two real negative regimes sharpen the boundary: Level-3 has `R*=1` with disjoint support, while Skill-SP's released logical-reasoning compilers yield 127/128 multi-membership tasks yet still have `R*=1` because an umbrella support permits exact equalization. Thus overlap prevalence is not the cause; **non-equalizable support geometry** is.

We operationalize this result as **STRI-Cert**, a sound audit protocol that computes the exact certificate and optional human-readable lower-bound witnesses from independently defined support contracts. We do not claim that the LP solver itself is novel, nor that static representation distortion implies downstream task harm. A faithful Qwen3 dynamic pilot completed its frozen generation budget but failed the author-native qualification gate, so it provides no dynamic scientific update and is not rerun. Our contribution is therefore an exact representation-invariance criterion and released-system evidence for a previously unmeasured control property of self-evolving agents.

## 1. Introduction

Many self-evolving agents adapt without changing foundation-model weights. Instead, they accumulate and revise external state: memories, skills, workflows, tools, prompts, retrieval policies, or harness code. Skills are especially attractive because a skill can package a reusable procedure together with metadata, examples, applicability information, and verification logic. Recent systems go further and make the skill identity itself a control variable. Skill Self-Play samples a skill before generating a training task. SkillRL gives dynamically created skill IDs priority in a fixed retrieval budget. Other systems attach feedback, refinement, retirement, or safety decisions to persistent skill objects.

This architecture makes the **representation** of the skill library consequential. Consider two taxonomies that expose the same executable semantic capability. One stores a primitive once; another stores an exact clone under a fresh ID. One represents a generic and a specific capability separately; another groups unchanged primitives behind a macro package. If no new primitive behavior or support region has been added, should the agent's future curriculum, retrieval exposure, or credit allocation change solely because the package bookkeeping changed?

Existing work motivates but does not answer this question. SkillClone studies semantic clone detection and propagation. SkillsVote studies governance of redundant and environment-sensitive skills. SkillMisevo studies unsafe evolution and later reuse. Agent Skills Can Be Harmful attributes functional and efficiency regressions to loaded skills. ERSkill co-evolves retrieval skills and a router; Skill-SP co-evolves a proposer, solver, and skill controller; SkillZip compresses repeated internal structure. These works establish that skill quality, redundancy, and routing matter. They do not establish a representation-invariance property for an endogenous evolution controller.

We approach the question asset-first. Instead of proposing a normalization method and manufacturing an experiment, we ask whether released systems expose a real representation-sensitive control surface, whether the effect survives simple reductions, and what support structure distinguishes positive from negative regimes.

### Released Skill-SP: necessary partial overlap

Across 530 API-Bank Level-1/3 rows bundled with the released Skill-SP repository, 348 are accepted by at least one released validator and 183 are accepted by multiple skills. The release's name+description Jaccard duplicate filter at threshold 0.33 misses all five observed specific–generic support-overlap pairs. More aggressively, if we delete as many whole packages as possible while preserving the complete released support, the active library can be reduced to seven skills—but 71 overlapping tasks remain. Some specific and generic packages each cover unique tasks while also sharing other tasks, so simple deletion would remove semantic support.

### Released SkillRL: exact identity multiplicity

SkillRL exposes a different representation channel. Its released `add_skills` path rejects duplicate skill IDs rather than duplicate semantic content. In the released template retrieval mode, dynamic general skills are included before the remaining fixed `top_k=6` budget is filled with static skills. We add an exact-content fresh-ID copy of each of 12 released general skills, one counterfactual at a time. All 12 are accepted. Across 223 released ALFWorld task descriptions, 11/12 clone targets change the unique semantic retrieval set and 5/12 reduce the number of unique general-skill contents returned.

These two systems already show that package identity can alter self-evolution control without adding semantic content. But **representation sensitivity is not equivalent to overlap prevalence**. Our central result is an exact support-geometry criterion that separates irreducible and equalizable regimes.

### Contributions

1. **STRI problem and evidence.** We formulate Skill-Taxonomy Representation Invariance and document representation sensitivity in two independent released self-evolving skill systems.
2. **Exact package-only certificate.** For a finite independently defined support matrix, we derive `R*(A)`, an exact iff criterion for whether nonnegative package weights can equalize additive semantic exposure. We also give a simple global-singleton overlap theorem yielding an interpretable factor-2 lower bound.
3. **Mechanism boundary on real assets.** Skill-SP Level-1, a frozen calibration subset, and a tool-disjoint heldout subset all have `R*=2`. Level-3 has `R*=1`. More surprisingly, 127/128 first-party logical compiler tasks have overlapping support but `R*=1`, proving that overlap count itself is not the mechanism.
4. **STRI-Cert audit protocol.** We package the exact criterion and closed-form witness search into a fail-closed diagnostic protocol. We do not claim LP computational novelty or downstream performance improvement.

## 2. From Package Identity to Semantic Exposure

### 2.1 Frozen support matrix

Let `X={x_1,...,x_n}` be a finite set of semantic contexts or tasks with independent first-party support truth, and let `S={s_1,...,s_m}` be the current skill packages. Define the binary incidence matrix

`A_ij = 1` iff released support/validation says package `s_j` applies to context `x_i`.

The support definition must be frozen before looking at the STRI certificate. In our tool-call study, support comes from released Skill-SP validators. In the logical-reasoning study, tasks are generated by released compiler specifications, independently validated by the author CSP/contract code, and cross-skill support is defined by the released `compiler_sample_alignment_errors` predicate.

We study **package-only pre-context control**: at a frozen state, the controller chooses nonnegative package mass `w>=0` before the semantic task to be generated exists. The additive eligibility/control exposure of context `x_i` is

`e_i = (A w)_i`.

This is a control-opportunity quantity, not task probability and not utility. Its purpose is to ask whether package bookkeeping alone can create unavoidable semantic exposure imbalance.

### 2.2 Why the entire pre-task single-package controller class reduces to package mass

In released Skill-SP, `sample_skill()` runs before `build_questioner_messages(skill)`, and therefore before the generated task exists. At that decision point the action is exactly one current package identity. For any fixed pre-task state `z`, every randomized same-information rule, bandit, MLP, or neural controller induces a categorical distribution over packages. Hence pointwise it induces one nonnegative package-mass vector `w(z)`.

This matters for baseline parity. A baseline cannot be given the future generated task and still be called same-information for upstream curriculum sampling. Conversely, our theorem is only pointwise: it does not assert that a longitudinal adaptive controller is one globally fixed vector.

## 3. Exact Equalizability and the STRI Certificate

### 3.1 Exact finite-support criterion

The max/min exposure ratio is invariant to positive scaling of `w`. We therefore normalize every covered context to exposure at least one and solve

`R*(A) = min_{w>=0,t>=0} t`

subject to

`1 <= A w <= t 1`.

**Theorem 1 (finite-support package-only equalizability).** `R*(A)=1` if and only if there exists a nonnegative package-only controller that gives exactly equal additive exposure to every covered context. If `R*(A)>1`, no such package weighting exists, and `R*(A)` is the tight minimum achievable max/min exposure ratio.

**Proof.** If exact equalization exists, rescale its positive common exposure to one, giving a feasible solution with `t=1`. The constraints always imply `t>=1`, so `R*=1`. Conversely, `R*=1` implies `1<=Aw<=1`, hence `Aw=1`. For any positive exposure vector generated by `w`, divide `w` by `min_i (Aw)_i`; the resulting feasible `t` equals `max_i(Aw)_i/min_i(Aw)_i`. Minimizing over `w` therefore gives exactly the tight multiplicative distortion. □

This theorem is deliberately elementary. The contribution is not a new LP algorithm; it is the representation-invariance object it exactly decides for a released self-evolution control surface.

### 3.2 Human-readable factor-2 witness

An exact LP is useful but can be opaque. A common support pattern yields a closed-form certificate.

**Theorem 2 (global-singleton overlap lower bound).** Suppose two packages/primitives `a,b` each have a context supported by exactly that one package over the full frozen support universe, and there is another context supported by both `a` and `b` (possibly with additional packages). If both singleton contexts retain positive exposure, then every nonnegative package mass satisfies `R*(A)>=2` on the focal contexts.

**Proof.** Let `r>0` be the minimum exposure among the two globally singleton contexts and the shared context. Because the first singleton support signature is exactly `{a}` over the full frozen package universe, its exposure is exactly `w_a`, so `w_a>=r`. Likewise the second singleton context has exposure exactly `w_b`, hence `w_b>=r`. The shared context contains both `a` and `b`; if it contains additional packages their nonnegative weights can only increase its exposure. Therefore its exposure is at least `w_a+w_b>=2r`. Thus the maximum focal exposure is at least twice the minimum focal exposure. Because restricting to the focal rows cannot make the global max/min ratio larger than the full-matrix optimum's best achievable distortion, every globally feasible package-only weighting satisfies `R*(A)>=2`. □

The released Skill-SP Level-1 graph gives two independent instances: `skill_003`–`skill_015` and `skill_004`–`skill_015`. The exact LP reaches `R*=2`, so the closed-form lower bound is tight rather than merely qualitative.

### 3.3 STRI-Cert

STRI-Cert is a diagnostic protocol, not a learned predictor:

1. freeze an independently defined context-by-package support matrix;
2. solve the exact package-only LP for `R*(A)`;
3. if `R*=1`, report **package-only equalizable**;
4. if `R*>1`, report **irreducible package-only representation residual** and its tight distortion;
5. search for globally valid singleton-overlap witnesses to provide an interpretable lower bound when available;
6. if support truth or optimization fails, return unresolved rather than infer a result.

The strongest same-information reduction is therefore built into the certificate itself: arbitrary nonnegative global package reweighting receives the complete frozen support matrix. Text deduplication, exact-clone removal, uniform routing, and fixed scalar retuning are strictly weaker controls.

## 4. Released-System Evidence

### 4.1 Skill-SP tool-call support: positive regime

On API-Bank Level-1, 314 rows are accepted by at least one released Skill-SP validator and 183 have multiple memberships. The exact certificate gives `R*=2.0`.

This is not driven by a particular tool subset. We preregistered a tool-disjoint split before the later certificate analysis:

- calibration: `AppointmentRegistration`, `ModifyRegistration`, `QueryHealthData`, `RecordHealthData`;
- heldout: `CancelRegistration`, `EmergencyKnowledge`, `QueryRegistration`, `SymptomSearch`.

The calibration subset contains 47 covered tasks and 33 multi-membership rows; `R*=2`. The tool-disjoint heldout subset contains 52 covered tasks and 38 multi-membership rows; again `R*=2`. Both subsets independently contain the two globally valid factor-2 witness structures.

Thus the positive mechanism is not an artifact of fitting package weights to the complete Level-1 table.

### 4.2 Level-3: disjoint-support negative control

Level-3 provides a natural released negative regime. Thirty-four rows are covered, every covered row has exactly one skill membership, and the exact optimum is `R*=1`. Equal weights on the four active packages equalize every covered task.

This demonstrates that STRI-Cert does not declare every released Skill-SP taxonomy problematic.

### 4.3 Logical compiler domain: high overlap without an irreducible residual

A stronger negative test asks whether high overlap alone is enough to trigger the certificate. Skill-SP's logical-reasoning release contains eight skill packages with programmatic compiler specifications. The author code can generate a zebra puzzle from a compiler and verify it with a fixed CSP solver; it also exposes a package-specific alignment predicate based on each compiler's required relation types and minimum counts.

We freeze the author's default compiler-validation grid sizes `(3x3,4x4,5x5,6x6)` and seeds `0..3` for every one of the eight released logical skills: 128 source units. No language model is used. All 128/128 compile and pass the author's puzzle contract and uniqueness verifier. We then cross-evaluate each task against all eight released compiler support specifications.

The resulting support matrix is extremely overlapping: **127/128** tasks have more than one supported skill, with 38 distinct support patterns. Yet `R*=1`. The LP assigns weight one to `skill_008` and zero to the other packages because `skill_008`'s released alignment contract supports every generated unit. In other words, an umbrella support makes the whole high-overlap matrix exactly equalizable.

This result falsifies the tempting mechanism "more overlap implies more representation dependence." The correct object is whether the support geometry admits an equalizing nonnegative package mixture.

### 4.4 SkillRL: independent identity-sensitivity witness

SkillRL supplies evidence that the issue is not confined to one controller implementation. In its released template-mode skill memory, fresh dynamic identities receive priority in the fixed general-skill budget. An exact-content clone with a new `dyn_NNN` ID is accepted for all 12 tested general skills. For 11/12 clone targets, the unique semantic retrieval set changes on released task descriptions; for 5/12, the number of unique contents decreases under the same `top_k=6` budget.

We use SkillRL only as an independent representation-sensitivity witness. The exact `R*` analysis is defined on Skill-SP's released support contracts, where support is directly observable.

## 5. Relation to Existing Work

**Skill redundancy and clone detection.** SkillClone directly studies semantic skill clones and clone propagation. STRI therefore does not claim that duplicate skills exist or that exact duplicates should be detected. The focal Skill-SP positive regime survives exact-clone reasoning because the mandatory specific and generic packages each have unique support regions as well as shared contexts.

**Redundancy-aware governance.** SkillsVote and related lifecycle governance methods recommend, attribute, suppress, or update redundant/environment-sensitive skills. Such policies may improve performance, but they do not by themselves answer whether a frozen taxonomy admits representation-invariant package-only control. STRI-Cert is a property test of the control/support geometry, not a competing recommendation algorithm.

**Skill safety and failures.** SkillMisevo and Agent Skills Can Be Harmful show that learned or retrieved skill content can propagate unsafe or inefficient behavior. Our primary transformations hold semantic support fixed and make no claim that a positive STRI certificate implies harmful content or failure.

**Adaptive routing and evolving skills.** ERSkill [arXiv:2608.12720] co-evolves retrieval skills and a query-dependent router; Skill-SP [arXiv:2607.22529] co-evolves a proposer, solver, and dynamic skill controller; SHAPER [arXiv:2608.11350] evolves external skills and harnesses. These works absorb any generic claim that adaptive skill routing or skill evolution is novel. They motivate our question because skill identities become endogenous actions/state, but they do not test invariance to a semantics-preserving reparameterization of that action/state representation. The frozen-state decision-time result says only that an upstream single-package controller induces some package distribution at that instant; it does not reduce a complete longitudinal learner to static weights.

**Compression and structural sharing.** SkillZip [arXiv:2608.11079] reduces repeated internal skill structure while preserving a skill contract. This absorbs the idea that duplicated procedural structure should be factored or shared. STRI instead asks whether the external evolution control law changes when the same semantic support is represented differently, including partial-overlap cases that cannot be removed by exact deduplication.

**Similarity-aware bandits and experts.** Classical structured online-learning methods exploit similarity or information sharing across actions. We concede this mature idea. Our contribution is not a new optimizer over similar arms: it is the exact representation-invariance property of a changing artifact taxonomy and a certificate on independently defined semantic support. If a future system uses a semantic action space rather than package identities, it may satisfy STRI by construction.

## 6. Dynamic Evidence: A Preregistered Failure to Qualify

Static support distortion need not propagate through a real task generator. We therefore preregistered a faithful Qwen3-8B Skill-SP pilot before using any dynamic outcome. The contract fixed three source skills (`003`, `004`, `015`), 24 generations per source, author prompts and validators, released-style decoding, and a minimum of 16 contract-valid tasks per source before any merge/split distribution statistic could update belief.

All 72 frozen generations completed within budget. However, only 14/24, 5/24, and 8/24 outputs for the three sources satisfied the author-native task contract. The formal outcome is therefore **INCONCLUSIVE_PROPOSER_QUALIFICATION_FAILED**: no dynamic witness statistic is scientifically admissible.

This is not a negative STRI result. The dominant failures are requirements implemented by the author questioner contract itself, especially omission of the required solver `<tool_call>...</tool_call>` output contract. The released training pipeline uses the same contract checks before solver evaluation. We therefore classify the result as proposer/substrate competence insufficiency rather than a wrong observable.

We do not lower the `16/source` gate, add generations, change decoding, rerun the same contract, or switch backbone. The failed bank is reported because it prevents a hidden positive-results bias: the current narrow paper does **not** claim dynamic propagation or downstream utility harm.

A separately frozen SkillRL fixed-task experiment can test whether an exact-clone retrieval displacement changes final ALFWorld success under an author-released SFT warm-start. It is evidence-only, not paper novelty, and is not required for the claims above. Its outcome cannot rescue or invalidate the support-geometry certificate.

## 7. What STRI-Cert Does and Does Not Tell Us

The certificate answers a precise question: *given an independently defined finite support matrix and package-only nonnegative mass, is exact additive exposure equality achievable?* This is useful for auditing an evolving skill controller before interpreting package-level sampling or credit statistics.

A positive certificate (`R*>1`) says that every package-only global weighting leaves a representation-dependent exposure distortion on the audited support domain. It does not say which package should be deleted, whether the taxonomy is semantically bad, or whether downstream utility decreases. A negative certificate (`R*=1`) says that the support geometry is equalizable by some package mixture; it does not guarantee that the released controller actually uses that mixture or that all longitudinal dynamics are invariant.

The logical compiler result illustrates why this distinction matters. Its 127/128 overlap rate looks worse than the tool-call overlap rate if one counts redundancy. STRI-Cert reaches the opposite mechanism conclusion because the logical support family contains an umbrella package that permits exact equalization. This is the kind of boundary a redundancy count or text-similarity score misses.

A natural repair direction is to factor control through semantic support cells rather than current package IDs—our earlier Support-Quotient Control design. We leave this as future work because its faithful dynamic evaluation did not clear the preregistered proposer qualification gate. The current paper is about identifying when such a repair is structurally necessary, not claiming that one particular repair wins.

### Claim boundary checklist

The narrow claim is intentionally smaller than the original dynamic paper design. We **do** claim that released control surfaces can depend on skill-package representation, that `R*(A)` exactly characterizes package-only additive exposure equalizability on a frozen finite support matrix, and that the audited residual tracks support geometry rather than overlap prevalence. We **do not** claim that a positive certificate causes task failure, that static exposure predicts longitudinal utility, that STRI-Cert is computationally novel relative to linear programming, that high overlap is harmful in general, that Support-Quotient Control has been empirically validated, or that the unqualified Qwen3 bank provides evidence for or against dynamic STRI. These boundaries are part of the scientific result, not caveats to be relaxed in later sections.

## 8. Limitations

1. **Support truth is required.** STRI-Cert assumes a frozen, independently defined support matrix. Tool-call support comes from released validators; logical support comes from released compiler alignment contracts. Learned or uncertain support estimators would add another identification problem.
2. **Additive package exposure is a static object.** `R*` does not by itself establish realized task-distribution change or downstream performance harm.
3. **Finite audited contexts.** The certificate is exact on the frozen support matrix, not on unobserved semantic contexts outside the audit domain.
4. **Package-only action class.** The certificate targets controllers whose pre-context action is package mass. Systems that directly act on semantic support cells or generate new actions conditioned on richer pre-decision state require a different analysis.
5. **Dynamic qualification failed.** Our faithful Skill-SP Qwen3 pilot did not meet the author-native valid-task support gate. We expose this failure and keep all dynamic/utility claims out of the narrow submission.

## 9. Conclusion

Self-evolving agents should not change their semantic control process merely because the same capability is packaged differently. Released systems show that skill identity can nevertheless alter curriculum and retrieval control. The relevant mechanism is not redundancy in the abstract. It is whether the support incidence geometry can be equalized by package-only control.

The exact quantity `R*(A)` turns this principle into a falsifiable audit. Skill-SP tool-call support yields a tight factor-2 residual that replicates on tool-disjoint heldout tools. Real negative regimes demonstrate the boundary: disjoint Level-3 support is equalizable, and a logical skill library remains equalizable despite nearly universal overlap. These results support STRI as a representation-invariance property of self-evolving skill systems while keeping dynamic performance claims explicitly separate.

## Claim / Evidence Table

| Claim | Status | Evidence |
|---|---|---|
| N1: released self-evolving skill controls can be representation-sensitive | Supported | Skill-SP released support/controller; SkillRL exact fresh-ID clone audit |
| N2: `R*(A)` exactly decides finite package-only exposure equalizability | Supported | theorem + exact LP |
| N3: non-equalizable support geometry, not overlap prevalence, tracks the audited residual | Supported | Level-1/calibration/heldout `R*=2`; Level-3 `R*=1`; logical 127/128-overlap `R*=1` |
| SQC improves utility / achieves dynamic STRI | **Not claimed** | dynamic P0 did not qualify |
| static STRI causes downstream task harm | **Not claimed** | no qualified dynamic evidence |

## Planned Figures / Tables

- **Fig. 1:** Two package representations over the same semantic support basis and the definition of package exposure.
- **Fig. 2:** Skill-SP Level-1 support graph with the two global-singleton factor-2 witnesses.
- **Fig. 3:** `R*` mechanism boundary: Level-1/calibration/heldout = 2 versus Level-3/logical = 1 despite 127/128 logical overlap.
- **Table 1:** Released-system representation-sensitivity evidence: Skill-SP and SkillRL.
- **Table 2:** Reduction tournament: text dedup, exact-coverage pruning, optimal global weights, closed-form witness, exact certificate.
- **Table 3:** Real support-regime comparison with covered rows, overlap fraction, witness count, `R*`, and certificate result.
- **Appendix table:** faithful Qwen3 P0-A qualification outcome and no-rescue interpretation.
