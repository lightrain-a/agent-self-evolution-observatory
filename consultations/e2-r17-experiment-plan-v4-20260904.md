# E2-R17 Experiment Plan V4 — Controlled Causal Core + Public Baseline/Transport Lane

Date: 2026-09-04
Status: `ZERO_PROVIDER_OUTCOME_BLIND_ROADMAP_ONLY`
Live branch before this plan: `1bbc94220f2744b65f9e45b32461a45b2ccda159`
Frozen V3/R2 scientific commit: `29799c83c662887694db52acba4bb19e83131bb0`
Frozen R2 contract SHA256: `f5382c552f2e6644e4cbda408510119664a8c6f8502628586c9ff5583abd1234`
Frozen R2 preflight SHA256: `e257438bd482d4f2209a8321d4a222bd97acf2c03bff46a1d5513b55a42ca766`

This plan is the current **paper-level experiment roadmap**. It supersedes older V1/V2/V3 roadmap documents for future planning only. It does not rewrite historical experiments or modify the already-reviewed V3/R2 controlled experiment. It grants no provider call, Stage-A, Stage-B, public-benchmark, analyzer, or paper-claim authority.

For day-to-day execution, use the compact map `consultations/e2-r17-experiment-plan-v4-execution-map-20260904.md`. The canonical sequence is: **A completed evidence -> B mandatory controlled V3 -> C one unified public transport/baseline lane -> D optional robustness only after the required ladder is complete.**

---

## 1. Paper-level experimental objective

E2-R17 is now a **causal systems/interface paper**, not a generic failure-learning method paper.

The scientific object is a realized test-time search object `T_K` with two consumers:

```text
T_K
 ├── a(T_K) -> current served behavior
 └── g(T_K) -> persistent updater evidence
```

The paper must establish, in order:

1. **availability/censoring:** serving can make already-generated evidence unavailable to winner-coupled persistent learning;
2. **causal consequence:** changing only `g(T_K)` under exact same `T_K` and fixed acting can change future frozen-skill utility;
3. **prospective structural effect modification:** that projection effect differs across the frozen procedural-transformation vs instance-binding/localization manipulation;
4. **controlled act/learn divergence:** a preregistered region actually has positive alternative-projection simple effects, not only a positive interaction;
5. **public transport + method comparison:** the effect survives one realistic public substrate and is competitive with closest self-evolving-skill baselines under one unified rerun harness.

No experiment later in the ladder may rescue failure of an earlier scientific gate.

---

# 2. Evidence ladder and hard authority boundaries

## Level 0 — historical/support evidence: already completed

### E0/E1-A availability support

Use only as treatment-support / phenomenon evidence:

- 96 exact K=8 pools;
- 768 rollout references;
- 78/96 mixed pools;
- 12/12 exposed streams;
- 6/6 failure families;
- no updater calls in the support tranche.

Claim boundary:

> evidence existed in the search object that was absent from winner-coupled learner visibility.

Do not infer learning value from this tranche.

### Closed global exact-same-pool causal study

Fixed result:

- 12 streams;
- 48 paired replicate units;
- 96 learned states;
- 1728 heldout rollout units;
- WIN-C ≈ 79.05%;
- universal MRW ≈ 81.37%;
- difference +2.3148 pp;
- paired-bootstrap CI crosses zero;
- exact one-sided historical sign-flip `p=0.171875`;
- frozen verdict `HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS`.

Permitted interpretation:

> a reliable global universal-MRW advantage was not established; the result motivated a fresh prospective moderator hypothesis.

It must not be rewritten as already proving heterogeneity or non-universality.

---

# 3. Controlled V3/R2 core — do not redesign

## 3.1 Stage A — support acquisition only

Existing frozen design remains authoritative.

Planned scale:

- 5 independent matched skeletons;
- 2 semantic cells/skeleton;
- 2 streams/cell;
- 20 update streams total;
- 8 update tasks/stream;
- 160 scientific update tasks;
- K=8;
- 1280 actor rollouts;
- 160 sealed K8 pools;
- zero updater calls;
- zero heldout access.

### Stage-A support gate

Every stream must contain at least four mixed pools. Exactly four treated pools per qualified stream are selected by the frozen mixed-only hash rule.

If any stream fails support:

`HOLD_V3_SUPPORT_NOT_ESTABLISHED`

Hard STOP:

- do not replace tasks;
- do not replace streams;
- do not add skeletons;
- do not change K;
- do not switch actor/model because support looked weak;
- do not enter Stage B.

Stage-A failure is a positivity/support failure, not evidence that the mechanism is false.

## 3.2 Stage B — primary controlled causal mechanism, only after separate authorization

Existing frozen plan:

- 20 streams;
- both WIN-C and MRW4 learned from exact same Stage-A pools/state;
- R=4 paired stochastic measurement replicates;
- 80 paired stream-replicate units;
- 160 learned states;
- 20 common heldout K=1 tasks/state;
- 3200 heldout evaluations.

`R=4` is measurement replication only.

### Primary mechanism unit

For stream `s`:

`D_s = mean_r[J_s,r(MRW4)-J_s,r(WIN-C)]`.

For skeleton `h`, semantic cell `z`:

`D_h,z = mean_{s in (h,z)} D_s`.

Primary interaction:

`I_h = D_h,PROCEDURAL - D_h,BINDING`.

The five `I_h` are the independent confirmatory mechanism units.

### Primary V3 gate

PASS iff the already-frozen primary gate passes, including all five interaction directions positive.

If FAIL:

`STOP_E2_R17_STANDALONE_STRONG_MECHANISM_STORY`

Consequences:

- router performance cannot rescue it;
- aggregate replicate significance cannot rescue it;
- favorable skeleton subsets cannot rescue it;
- second backbone cannot rescue it;
- public benchmark cannot be opened as a rescue experiment;
- preserve the interface/censoring/negative evidence for merge or narrower diagnostic use.

---

# 4. Secondary controlled-divergence claim gate — no new data collection

Machine-readable freeze:

`generated/e2-r17-v3-secondary-controlled-divergence-claim-gate-20260903.json`

Evaluate only after primary V3 PASS.

PASS iff:

```text
D_h,PROCEDURAL > 0
for all five frozen skeletons.
```

This is a prospective finite-suite claim-adjudication rule, not a newly claimed exact `p=1/32` inferential test.

### If secondary PASS

Unlock only the bounded controlled-suite statement:

> across all five preregistered procedural-transformation skeletons, the alternative learner projection produced higher future frozen-skill utility than WIN-C while exact search pools and current acting were held fixed.

This is the controlled act/learn-divergence witness.

### If secondary FAIL but primary V3 PASS

Retain:

> projection effect is prospectively structure-dependent on the controlled suite.

Do not claim:

> the served-winner projection is actually inferior for persistent learning in the controlled procedural region.

No favorable cell may be selected post-outcome.

The only allowed paper-strength claim-expansion experiment is the public lane below, and only if the authors choose to continue the standalone paper.

---

# 5. Public Lane P1 — unify natural transport and closest-method baseline comparison

## 5.1 Entry conditions

Public Lane P1 may be opened only if:

1. V3 Stage A support PASS;
2. V3 Stage B primary interaction PASS;
3. all V3 outcomes and claim gates are frozen/read-only before P1 design execution;
4. exact public benchmark version, workbook hashes, split IDs, evaluator, actor, updater role, tool harness, turn budget, formula-recalculation policy, and method adapters are frozen before the first public scientific updater call;
5. an independent zero-provider review approves the final P1 packet.

If V3 primary interaction FAILS, P1 is **not** opened to rescue the paper.

## 5.2 Public substrate

Primary public substrate:

**SpreadsheetBench Verified-400**.

Reasons:

- realistic forum-derived spreadsheet tasks;
- exact deterministic workbook/evaluator artifacts already locally pinned;
- direct overlap with closest skill-evolution literature;
- enough size for one development/evolution block, one validation block, and a large heldout test block;
- avoids a benchmark zoo.

### Split policy

Use one **unified rerun split** for all quantitative main-table methods.

Preferred plan:

- 80 evolution/train tasks;
- 40 validation/selection tasks;
- 280 heldout test tasks.

This 80/40/280 structure aligns with an existing public SkillOpt SpreadsheetBench Verified protocol and avoids inventing a result-conditioned split. Exact IDs must be pinned from the audited public source or deterministically frozen before any P1 outcomes.

No public task may change split after any method result is visible.

## 5.3 Primary public model/harness

Primary unified rerun should use **one common qualified model/harness first**, not a cross-product.

Preferred primary executor/updater family:

- actor/executor: DeepSeek V4-Pro exact resolved release, after fresh role-specific qualification;
- persistent updater: one frozen qualified strong updater, preferably the same DeepSeek V4-Pro release when method semantics permit;
- identical tool harness, spreadsheet runtime, turn limit, evaluator, recalculation policy, task IDs, and accounting for every unified-rerun row.

Reason:

- DeepSeek V4-Pro already appears in the closest feedback-dynamics work;
- current E2 infrastructure has stable identity/adapters;
- one common model isolates method differences more cleanly than a multi-model main table.

### Optional robustness model

Only after the primary public table is frozen:

- one qualified Qwen sparse 35B-class model **or** Kimi K3;
- choose based on outcome-blind runtime qualification/availability, never based on which gives a larger E2 gain.

This second model is robustness only. It is not required to rescue a weak primary result.

---

# 6. Unified public main-table baselines

The public main table must distinguish **method baselines** from controlled V3 mechanism arms.

## 6.1 Mandatory simple anchors

### B0 — No Skill

No persistent learned skill/memory.

Purpose: absolute task/harness capability anchor.

### B1 — Initial / Parent Skill

Use the frozen initial skill before evolution.

Purpose: show whether any evolution improves future utility.

### B2 — WIN-C

Current served-winner projection as persistent learner evidence.

Purpose: tied serving/learning default.

### B3 — Universal MRW4 / nearest public-compatible rejected-witness projection

Use the prospectively frozen public-compatible projection rule under matched evidence budget.

Purpose: fixed alternative-projection extreme.

## 6.2 Mandatory closest feedback/skill baselines

### B4 — RethinkSkill Normal

Success + failure feedback under the source-semantic-compatible unified harness.

### B5 — RethinkSkill Success-only

Success feedback only.

### B6 — RethinkSkill Fail-only

Failure feedback only.

These three are mandatory because they directly test the strongest nearby explanation: feedback composition matters, without exact same-pool serving/learning separation.

### B7 — SkillOpt

Use the official implementation adapted to the unified rerun harness with:

- same public split;
- same target actor;
- one frozen qualified optimizer/updater role;
- matched rollout/edit/validation budget as closely as source semantics permit;
- exact adapter receipt.

SkillOpt is mandatory because it is a strong current external-skill optimizer with official code and broad public evaluation.

### B8 — trajectory-to-skill / contrastive baseline slot

At least **one** credible trajectory-to-skill / contrastive baseline is mandatory in the unified public main table.

Preferred order:

1. **Trace2Skill** if its official/public implementation passes runtime qualification under the common public harness;
2. otherwise a clearly labeled **SkillCAT-style contrast** reconstruction under the frozen common harness.

Run both only if they answer materially different alternative explanations at acceptable marginal cost. Do not spend a second full evolution lane merely to duplicate the same scientific reduction.

Never label a SkillCAT-style row as an exact SkillCAT reproduction without a source-faithful pinned implementation/runtime.

Purpose: test the strongest direct reduction of E2 into generic trajectory-to-skill or success/failure contrastive skill extraction.

## 6.3 Conditional E2 method row

### M-E2 — Frozen E2 observable projection policy

Include in the public method ranking only if:

1. V3 primary mechanism PASS;
2. the policy's pre-update observable feature extractor is frozen before P1 outcomes;
3. no hidden controlled-suite family/template/semantic label is available;
4. public policy eligibility is determined only from ordinary pre-update task/search observables;
5. public policy execution does not inspect validation/test outcome labels.

If the E2 policy adapter cannot be made source-neutral without semantic leakage, omit the method row rather than inventing a new router after seeing outcomes. The paper can remain a causal interface paper.

---

# 7. Public P1 scientific unit and evaluation protocol

## 7.1 Evolution unit

The evolution/training task is the update opportunity. Methods may use their source-semantic-compatible internal procedure, but all receive the exact same evolution task IDs and common compute/accounting ceilings.

## 7.2 Validation

The 40 validation tasks may be used only for the method's prospectively permitted selection/early-stopping behavior.

No test task may influence:

- skill selection;
- router threshold;
- evidence eligibility;
- baseline hyperparameters;
- prompt variants;
- model choice.

## 7.3 Heldout test

All final selected/frozen persistent artifacts are evaluated on the same 280 heldout test tasks.

Primary public endpoint:

- task success / official SpreadsheetBench evaluation utility on the 280 heldout tasks.

Report:

- point estimate;
- paired per-task difference versus WIN-C/Parent and strongest closest baseline;
- paired bootstrap confidence interval across the 280 frozen test tasks;
- per-category/task-type breakdown only if categories are defined independently of model outcomes.

## 7.4 Measurement replication

Do **not** multiply full evolution runs by R=4 for every public baseline.

Cost-efficient design:

- one frozen evolution/selection run per baseline under the unified split;
- final selected artifact frozen/content-addressed;
- 3 repeated heldout evaluation panels of the same frozen artifact if the executor/evaluator remains stochastic.

These repeats quantify measurement variance; they are not independent evolution units.

If a baseline's source method intrinsically requires multiple evolution seeds, those seeds must be declared before execution and reported separately, not added selectively after a poor result.

---

# 8. Natural transport endpoint inside P1

P1 simultaneously serves as the natural/out-of-family transport test.

The E2 transport claim is not “our router beats every baseline.” It is narrower:

> under ordinary pre-update observables on public out-of-family tasks, changing the learner-visible projection while keeping current acting/search conditions appropriately matched can produce a positive future-skill effect in a prospectively identified region.

### Transport-specific primary endpoint

For the predeclared E2-eligible public units:

`Delta_transport = U_future(E2 alternative projection) - U_future(WIN-C)`.

Required for strong transport claim:

`Delta_transport > 0` under the preregistered public analysis rule.

Hard STOP if not supported:

- do not change eligibility after viewing outcomes;
- do not swap to a different public benchmark;
- do not mine task categories for a positive subgroup;
- do not add a second model as rescue;
- keep only the controlled V3 claim.

---

# 9. Source-faithful reproduction appendix lane

Unified rerun is the only place where direct method ranking is permitted.

A separate appendix lane may reproduce methods under their original source protocols to validate adapter fidelity:

- SkillOpt official split/config when feasible;
- RethinkSkill official feedback/evolution protocol;
- Trace2Skill official settings;
- SkillCAT paper-spec settings only when exact source implementation remains unavailable.

These results are **not** directly ranked against each other when splits/models/harnesses differ.

Purpose:

> demonstrate that our adapters preserve the source method rather than silently weakening baselines.

No source-faithful appendix result can rescue a negative unified-rerun result.

---

# 10. Reduction and ablation package

Avoid cosmetic module ablations. Include only claim-bearing reductions.

## Controlled V3 reductions — already frozen / zero extra scientific calls when composable

- always WIN-C;
- universal MRW4;
- difficulty-only routing;
- mixedness-only routing;
- frozen observable router.

## Optional diagnostic after positive projection effect

One generic-alternative / successful-nonwinner control may be added only if the paper explicitly wants to claim **failure-specific** causal value.

It is not required for the projection-interface paper and must not consume the single mandatory public transport/baseline lane.

## No required second backbone

A second model/backbone is robustness only after the main causal + public evidence is complete.

Do not use model breadth as a substitute for missing causal/public evidence.

---

# 11. Main-paper experiment tables

## Table 1 — controlled causal mechanism

One row per frozen skeleton:

| Skeleton | `D_PROC` | `D_BIND` | `I_h` | primary interaction sign | secondary procedural sign |

Purpose: RQ3/RQ4.

## Table 2 — public unified method comparison

Rows:

- No Skill;
- Parent Skill;
- WIN-C;
- Universal MRW4;
- RethinkSkill Normal;
- RethinkSkill Success-only;
- RethinkSkill Fail-only;
- SkillOpt;
- one mandatory trajectory-to-skill / contrastive baseline slot: Trace2Skill if source-faithful qualification passes, otherwise clearly labeled SkillCAT-style contrast; optionally both only if scientifically nonredundant;
- E2 policy, only if its gate passes.

Columns should include at least:

- public heldout success/utility;
- delta vs Parent;
- delta vs WIN-C;
- paired uncertainty;
- update/evolution cost;
- learner evidence/update token budget or comparable accounting.

## Table 3 — current acting vs future persistent learning

Show that the causal V3 comparison holds current acting fixed while future skill changes.

This table prevents readers from confusing current pass@K with persistent learning quality.

---

# 12. Resource and workload policy

The controlled experiment already has enough raw workload. Do not expand V3 for appearance.

### Effective-workload rule

Experiment volume is counted only when it buys identifiable scientific information. A new tranche is justified only if it does at least one of the following:

1. tests a paper-level claim that is not already identified by an existing tranche;
2. removes a material alternative explanation or confound;
3. establishes transport/external validity that controlled data cannot provide;
4. supplies a fair closest-method comparison required to interpret the contribution;
5. reduces measurement uncertainty enough to change a predeclared decision boundary.

GPU hours, provider calls, rollout counts, learned-state counts, heldout evaluations, models, and benchmarks are **not** independent measures of scientific workload by themselves. Replicates that only shrink already-adequate measurement noise do not substitute for new independent scientific units or a missing evidence type.

Every future experiment proposal must therefore state, before execution: `claim_served`, `alternative_explanation_removed`, `independent_scientific_unit`, `primary_endpoint`, `decision_changed_if_pass`, `decision_changed_if_fail`, and `stop_rule`. If these fields cannot be answered prospectively, the experiment is not admitted into the main paper plan.

### Do not add before public P1

- more synthetic skeletons;
- R=8 instead of R=4;
- larger heldout panel merely for scale;
- 4×4 actor/updater model cross-product;
- multiple public benchmarks;
- second backbone;
- failure-specificity arm.

### Spend remaining budget on

1. executing already-frozen V3 correctly;
2. one unified SpreadsheetBench Verified public lane;
3. strongest closest-method baselines in that lane;
4. only then one optional robustness model.

### SkillZip Pro workload cross-check

A targeted audit of SkillZip Pro reinforces this resource allocation. That paper earns systems-level empirical depth primarily through one production content-moderation harness plus a multi-entry bundle, while testing orthogonal dimensions such as protected vs unprotected compression, routing preservation, public-entry independence, One-Shot vs Continual updates, and Persistent vs Transient deployment. Its strength does not come from a large benchmark/model matrix.

The analogous E2-R17 requirement is therefore **evidence-type depth rather than benchmark breadth**:

- availability/censoring;
- exact-same-pool causal consequence;
- prospective structural effect modification;
- positive controlled divergence as a separate gate;
- one realistic public transport/baseline lane;
- explicit negative/failure boundary.

Current V3 already supplies more than enough controlled execution volume. The missing analogue of SkillZip Pro's industrial production evidence is the planned SpreadsheetBench Verified P1 lane. Do not substitute additional synthetic skeletons or extra models for that realistic evidence.

See `consultations/e2-r17-skillzip-pro-workload-comparison-20260904.md`.

---

# 13. Complete execution decision tree

```text
Current state
  |
  v
fresh DeepSeek identity qualification
  |
  +-- FAIL -> HOLD identity; no Stage A
  |
  v
separate single-use Stage-A authorization
  |
  v
V3 Stage A support acquisition
  |
  +-- support FAIL -> HOLD support; no replacements; no Stage B
  |
  v
separate Stage-B authorization
  |
  v
V3 primary interaction
  |
  +-- FAIL -> STOP standalone strong E2-R17; no public rescue
  |
  v
primary PASS
  |
  +--> secondary 5/5 procedural divergence gate
  |       |
  |       +-- PASS -> controlled act/learn divergence unlocked
  |       |
  |       +-- FAIL -> interaction-only controlled claim remains
  |
  v
freeze Public P1 packet + independent zero-provider review
  |
  v
SpreadsheetBench Verified unified transport + baseline lane
  |
  +-- transport unsupported -> retain controlled claim only; no benchmark/model rescue
  |
  v
public result frozen
  |
  +--> optional one-model robustness only if scientifically useful
```

---

# 14. Paper-completeness criterion

For a strong standalone causal systems/interface submission, the target package is:

### Required

- historical censoring/support evidence;
- closed global exact-same-pool result reported honestly;
- V3 primary controlled mechanism result;
- secondary controlled-divergence gate reported separately;
- one public SpreadsheetBench Verified lane;
- unified closest-method main table with RethinkSkill feedback arms, SkillOpt, and at least one credible trajectory-to-skill / contrastive baseline;
- cost/accounting and paired uncertainty;
- no benchmark shopping.

### Optional robustness

- second model/backbone;
- source-faithful appendix reproductions;
- failure-specificity decomposition;
- SpreadsheetBench 2 workflow transfer.

None of the optional items is allowed to rescue failure of the required scientific ladder.

---

# 15. Current execution authority

This V4 document is planning only.

Current status remains:

- V3/R2 provider calls: `0` in the current continuation;
- fresh identity qualification: not executed;
- Stage-A authorization: absent;
- Stage-A scientific execution: false;
- Stage-B authority: false;
- Public P1 authority: false;
- baseline scientific execution: false.

Next executable gate remains the existing exactly-one fresh DeepSeek identity qualification, followed by local adjudication and separate single-use Stage-A authorization if it passes.
