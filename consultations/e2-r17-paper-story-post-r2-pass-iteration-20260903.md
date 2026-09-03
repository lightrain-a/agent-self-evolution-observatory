# E2-R17 Paper Story Iteration after V3 Stage-A R2 PASS

Date: 2026-09-03
Status: `ZERO_PROVIDER_PAPER_STORY_ITERATION_ONLY`
Frozen scientific object: V3 Stage-A R2 contract SHA256 `f5382c552f2e6644e4cbda408510119664a8c6f8502628586c9ff5583abd1234`
Frozen R2 scientific commit: `29799c83c662887694db52acba4bb19e83131bb0`
Independent R2 review: `PASS_TO_SEPARATE_STAGE_A_AUTHORIZATION`

This note does **not** modify the frozen R2 experiment, authorize the fresh DeepSeek identity call, authorize Stage A, or infer any new scientific outcome. Its purpose is to separate experiment-validity from paper-strength and freeze a clearer paper narrative before scientific execution.

## 1. Main decision

**Do not redesign V3/R2 again before Stage A.**

The independent review has already established that the current crossed semantic experiment is scientifically executable. Additional pre-Stage-A redesign would mainly create researcher degrees of freedom rather than repair a remaining causal defect.

However, **do not make Selective-MRW or the hand-engineered instruction router the paper's central novelty.**

The strongest paper object is now:

> **Act–Learn Dual Projection / Search-Projection Censoring:** test-time search generates a richer experience object, while acting and persistent learning consume potentially different projections of that object. Serving-optimal selection can remove already-generated evidence from the learner-visible stream, and the learning-optimal projection need not equal the acting-optimal projection.

Selective-MRW is one controlled intervention / policy instance inside this larger object.

## 2. Why the paper must move above “learn from failures”

By September 2026, several close works already occupy the generic experience-utilization territory:

- ReasoningBank / MaTTS (ICLR 2026): learns reusable reasoning memories from successful **and failed** trajectories; test-time scaling produces multiple experiences and contrastive signals.
- SkillCAT (arXiv:2606.13317): explicitly samples same-task multiple trajectories and compares success/failure pairs to extract skill edits.
- SkillRevise (arXiv:2606.01139): performs trace-conditioned, execution-grounded skill revision with validation.
- Rethinking Self-Evolving Agent Skills (arXiv:2608.02636): directly studies feedback conditions involving successes/failures and shows sparse, model/benchmark-dependent skill-evolution returns.
- WikiSkill (arXiv:2608.27454): separates raw execution experience, persistent compiled knowledge, and executable skills, and accumulates experience across iterations.

Therefore E2-R17 must **not** claim novelty from:

- failure feedback being useful;
- using rejected rollouts;
- comparing successful and failed siblings;
- multi-trajectory contrast;
- validated textual skill editing;
- persistent experience accumulation;
- “more test-time search can interact with learning” in the generic sense.

The surviving distinctive question is upstream of those methods:

> **Given a search object that already contains rich experiences, what observation/projection crosses the serving-to-learning interface?**

ReasoningBank/MaTTS and SkillCAT can be interpreted as examples of richer learning projections. Winner-only logging/learning is a narrower projection. E2-R17 studies the causal and statistical consequences of this interface choice itself.

## 3. Current evidence map

### 3.1 Already-established phenomenon / motivation

The historical E0 and support work supplies motivation that should be retained but bounded:

- best-of-K serving can make a failure that existed in the generated search object invisible to a winner-only learner;
- the core search-projection censoring event is empirically nonzero;
- historical E1-A support showed abundant mixed pools on the earlier controlled substrate (78/96 mixed pools, 12/12 exposed streams, 6/6 families), establishing treatment support rather than method effect.

This is the **availability/censoring** layer, not proof that censored evidence is useful.

### 3.2 Closed DeepSeek causal study

The completed 12-stream / 48 paired-replicate DeepSeek study should be presented as a key negative/heterogeneity result rather than hidden:

- WIN-C: approximately 79.05%;
- universal MRW: approximately 81.37%;
- mean difference: +2.3148 percentage points;
- exact one-sided sign-flip p = 0.171875;
- paired-bootstrap 95% CI approximately [-1.85pp, +6.60pp];
- frozen verdict: `HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS`.

Scientific implication:

> The simple story “always replace winner evidence with a failed witness” is not supported. The learning consequence is heterogeneous enough that the relevant question becomes **which projection should be used when**, not whether failures are universally better.

This negative/inconclusive result is useful because it motivates the mechanism test without pretending the method already works.

### 3.3 What V3/R2 uniquely adds

The new V3/R2 controlled experiment tests the missing moderator prospectively:

- same structural skeleton;
- byte-identical paired initial workbook;
- semantic-blind nuisance profile selection;
- crossed `PROCEDURAL_TRANSFORMATION` vs `INSTANCE_BINDING_LOCALIZATION` cells;
- same acting process and exact search-pool generation;
- later WIN-C vs MRW4 learning projections from the same pool/state;
- five independent skeleton-level interactions;
- R=4 only as measurement replication;
- no hidden family/template label in the deployed observable router.

The scientific target is not “MRW wins.” It is:

> **The effect of changing the learning projection has a reproducible, prospectively specified interaction with task/evidence structure.**

That is substantially more defensible and more novel than another global success/failure comparison.

## 4. Recommended paper thesis

### 4.1 One-sentence thesis

> **The trajectory that is optimal to serve is not necessarily the evidence that is optimal to learn from: test-time search should expose acting and persistent learning as separate projections over the same generated experience object.**

### 4.2 Formal object

For search object `T_K`:

```text
T_K
 ├── acting projection   a(T_K) -> served behavior
 └── learning projection g(T_K) -> persistent updater evidence
```

The standard coupling `g(T_K) = a(T_K)` is one design choice, not a law.

The paper studies when serving-induced selection/coarsening of `T_K` changes future persistent learning.

### 4.3 Causal estimand

The cleanest experiment remains:

```text
same S0
same exact T_K
same verifier
same served winner a(T_K)
same updater/config/budget
same update sequence
only g(T_K) changes
        ↓
future frozen skill utility
```

This same-pool intervention is the central empirical identification device.

## 5. Recommended paper contribution hierarchy

Do not present five unrelated contributions. Use a three-level hierarchy.

### Contribution 1 — first-class system object

**Act–Learn Dual Projection:** formalize test-time search as a shared experience-generation process whose acting and persistent-learning observation kernels may differ.

This is the conceptual contribution.

### Contribution 2 — mechanism and causal evidence

**Search-Projection Censoring + same-pool causal intervention:** characterize when serving selection removes evidence from the learning channel, and causally test future persistent-skill consequences by changing only `g(T_K)`.

The closed global MRW result is part of this contribution because it demonstrates that the consequence is not a universal monotonic “failures help” law.

### Contribution 3 — prospective projection heterogeneity

**Projection policy depends on task/evidence structure:** V3 prospectively tests a crossed structural moderator rather than fitting family IDs after seeing effects.

If the interaction passes, this is the strongest new scientific result. The observable router is then only an engineered demonstration that the structural distinction can be implemented using pre-update, actor-visible information.

Do **not** call the router learned semantic discovery.

## 6. Reframe Selective-MRW

Current risk: the name “Selective-MRW” makes the work sound like a heuristic routing method.

Recommended role:

- `WIN-C`: served-winner learning projection;
- `MRW4`: controlled rejected-witness projection;
- `Projection Router`: pre-update policy selecting a projection;
- `Selective-MRW`: optional shorthand for one policy instance, not the paper title or scientific object.

The method section should first define a general projection policy

```text
pi_g(x_pre) -> {g_WIN, g_MRW, ...}
```

where `x_pre` contains only information observable before persistent update.

The current hand-engineered router is a **controlled proof-of-implementability**, not the main methodological novelty.

## 7. Current V3 semantic router: how to write it without overclaiming

The router perfectly separates the constructed semantic cells using visible operation-clause and binding-alternative counts. This is useful for implementation qualification but dangerous as a headline method result because the features are tightly aligned with the controlled generator.

If the V3 interaction passes, permissible claim:

> A frozen task-visible structural rule can implement the projection distinction on the controlled suite and outperform fixed projection policies if the separate method gate passes.

Impermissible claim:

> The agent automatically discovered a general semantic law for choosing failures.

The semantic interaction can be scientifically meaningful even if the router is not publishable as a standalone machine-learning method.

## 8. Important remaining paper risks after R2 PASS

These are **paper-strength risks**, not Stage-A blockers.

### Risk A — failure-specific value versus generic alternative-trajectory value

WIN-C vs MRW4 changes winner evidence to a failed nonwinner. Even with token matching, a positive effect could reflect:

- failure-specific diagnostic information;
- generic nonwinner diversity;
- alternative reasoning-path information.

Therefore the primary R2 result should initially support **learning-projection / rejected-evidence** claims, not automatically “failure information is uniquely causal.”

Only if the primary V3 interaction passes should a later diagnostic control distinguish failed nonwinner from a suitable nonwinner-success / neutral-alternative projection. This is a claim-expansion experiment, not a prerequisite for Stage A.

### Risk B — controlled semantic construction is still synthetic

The five crossed skeletons are excellent for mechanism identification but not sufficient for broad deployment/generalization claims.

If V3 passes, the next useful experiment is **one transport test**, not a benchmark zoo:

- natural/public tasks or naturally occurring skill-evolution traces;
- projection choice made from ordinary pre-update observable features;
- family/template identity unavailable;
- outcome-blind freeze before execution.

A failed transport test should downgrade deployment/generalization while preserving the controlled causal mechanism.

### Risk C — only five independent mechanism units

The exact all-positive directional sign gate is mathematically valid for the frozen five skeletons, but it is minimum-resolution evidence.

Therefore report:

- all five `I_h` individually;
- their magnitudes;
- descriptive mean/uncertainty;
- exact finite-five-unit sign interpretation.

Do not write population-level power/generalization language.

### Risk D — existing rich-experience methods are not enemies; they are boundary cases

ReasoningBank/MaTTS, SkillCAT and WikiSkill should not be framed simply as baselines that “miss our idea.” Their richer experience channels help define the projection axis:

- winner-only / served-trace projection: high censoring risk;
- multi-trajectory / success-failure contrast: richer learning projection;
- persistent compiled knowledge: downstream representation after experience selection.

This makes E2-R17 a unifying interface analysis rather than a claim that every prior method discards failures.

## 9. Related-work positioning table for the eventual paper

| Work | Search / experience multiplicity | Persistent object | Learner-visible experience | What it does NOT directly identify relative to R17 |
|---|---|---|---|---|
| ReasoningBank / MaTTS | multi-rollout parallel/sequential scaling | reasoning memory | successful + failed / contrastive search experience | causal effect of serving projection while holding exact search object and acting fixed |
| SkillCAT | same-task multi-seed trajectories | textual skill | explicit success/failure contrast | serving-induced censoring as a first-class act/learn interface |
| SkillRevise | execution traces across revision loop | textual skill | trace-conditioned repair evidence | exact same-pool acting-fixed learning-projection intervention |
| Rethinking Self-Evolving Agent Skills | controlled success/failure feedback sets | textual skill | experimenter-selected feedback view | how best-of-K serving determines which already-generated evidence reaches learner |
| WikiSkill | accumulated agent experience | wiki + executable skills | experience compiled into persistent wiki | outcome-dependent serving projection over one shared search object |
| **E2-R17** | exact shared K-pool | persistent external skill | independently controlled `g(T_K)` | focuses on the serving-to-learning projection interface itself |

This table should be used to sharpen the distinction, not to overclaim that all prior works use winner-only learning.

## 10. Paper empirical arc after this iteration

Recommended main-text order:

### Experiment 1 — Phenomenon / law

Show the serving-selection censoring object exists and is measurable.

This can use historical E0/support evidence plus exact theoretical identity where valid.

### Experiment 2 — Global causal test and its failure of universality

Show the closed exact-same-pool DeepSeek result:

- global point estimate positive;
- uncertainty overlaps zero;
- clear heterogeneity;
- reject universal MRW story.

This is scientifically stronger than hiding an inconclusive experiment because it motivates the next prospective mechanism test.

### Experiment 3 — Prospective crossed moderator test

V3/R2 is the key confirmatory experiment:

```text
projection × operationalized task/evidence structure
```

The five skeleton interactions are the confirmatory scientific units.

### Experiment 4 — policy consequence, only if Experiment 3 passes

Compare the frozen observable projection policy with:

- always WIN-C;
- universal MRW4;
- difficulty-only routing;
- mixedness-only routing.

Do not let policy success rescue a failed mechanism interaction.

### Experiment 5 — one claim-expansion transport test, only after controlled GO

Use one natural/public substrate or unseen natural family set.

This is where a method/deployment claim is earned, not in the synthetic router qualification.

## 11. Conditional post-V3 decision tree

### If V3 primary interaction PASSES

Main conclusion:

> Acting-optimal serving and learning-optimal evidence are separable, and the effect of learning projection varies prospectively with controlled task/evidence structure.

Then authorize at most two targeted claim-expansion steps:

1. **generic-alternative diagnostic control** if the paper wants a failure-specific mechanism claim;
2. **one natural/out-of-family transport test** if the paper wants a deployable projection-policy claim.

Second backbone can follow as robustness, but should not be used to rescue a failed transport or mechanism result.

### If V3 primary interaction FAILS

Do not rescue it with router tuning, more skeletons, or another model.

The paper can still survive as a narrower scientific paper if the earlier causal/heterogeneity evidence is strong enough:

> winner-only serving creates measurable search-to-learning censoring, but the tested procedural-vs-binding moderator does not explain the heterogeneous future-learning effect.

Then the paper becomes primarily a **diagnostic/interface paper**, not a method paper. Selective-MRW and the semantic router should be removed or moved to negative analysis.

### If Stage A support FAILS before Stage B

Do not interpret that as mechanism failure. It means the planned MRW4 treatment lacks positivity on the frozen V3 substrate. Close this child as `support HOLD`; do not replace tasks after inspecting support.

## 12. Recommended title direction

Prefer titles centered on the scientific object rather than the policy name.

Strong candidates:

1. **The Best Trajectory to Act On Is Not Always the Best to Learn From**
   - subtitle: *Decoupling Acting and Learning Projections in Self-Evolving Agents*

2. **When Serving Hides Learning Signals**
   - subtitle: *Search-Projection Censoring in Self-Evolving Agents*

3. **Act from the Winner, Learn from the Search**
   - subtitle: *Dual Projections for Persistent Agent Self-Evolution*

Avoid a title centered on `Selective-MRW`, because that undersells the general object and overstates the current router as the contribution.

## 13. Main figure recommendation

One figure should explain the entire paper before any result table:

```text
                      search generates T_K
                            /       \
                           /         \
                  a(T_K): serving   g(T_K): learning
                       |                 |
                  current action     persistent update
                       |                 |
                  immediate utility  future frozen skill

winner-only coupling:       g = a
R17 intervention:           hold a fixed, change g only
```

Then show one mixed-pool example where the served winner succeeds while a rejected branch exposes a reusable deficiency.

The current semantic moderator belongs in a later panel, not in the first conceptual figure.

## 14. Immediate execution recommendation

From a paper-design perspective, **R2 is sufficiently specified to proceed to Stage A**. No further scientific redesign is justified before seeing the prospectively frozen support data.

The only remaining executable gate is the already-prepared fresh DeepSeek identity qualification, followed by separate single-use Stage-A authorization if identity passes.

This note grants neither.

## 15. Frozen writing boundary before outcomes

Before V3 outcomes exist, the draft may state:

- search serving and persistent learning consume different projections in principle;
- winner-only coupling can censor already-generated evidence;
- the closed global replacement result is heterogeneous/inconclusive;
- V3 prospectively tests a structural moderator;
- the current router is hand-engineered and task-visible.

The draft may **not** state:

- V3 semantic interaction is supported;
- Selective-MRW is superior;
- failures are generically better learning signals;
- procedural vs binding is a universal semantic law;
- the router is learned or generally deployable;
- cross-model/public-benchmark generality exists.

These boundaries should remain frozen until the corresponding prospective gates are opened.
