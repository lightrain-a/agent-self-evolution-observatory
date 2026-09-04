# E2-R17 R2 REREVIEW INLINE PACKET

## FILE 1: rereview brief

# Independent adversarial R2 re-review — latest E2-R17 plan/frontend zero-provider repair

Date: 2026-09-04
Role: independent senior ICLR/NeurIPS/ICML agent-systems methodology reviewer

## 0. Review rule

This is a fresh re-review after the prior independent review returned `REVISE_ZERO_PROVIDER_PLAN_OR_FRONTEND` with exactly three verdict-changing zero-provider fixes. Review only whether those three blockers are actually repaired. Do not infer any V3/Public-P1 outcome; none exists. Do not reopen the already-reviewed V3/R2 causal protocol unless the repair introduces a new identification failure. Do not request broad extra models/benchmarks/experiments.

## 1. Frozen scientific object remains unchanged

- V3/R2 scientific commit: `29799c83c662887694db52acba4bb19e83131bb0`
- contract SHA256: `f5382c552f2e6644e4cbda408510119664a8c6f8502628586c9ff5583abd1234`
- preflight SHA256: `e257438bd482d4f2209a8321d4a222bd97acf2c03bff46a1d5513b55a42ca766`
- no V3 scientific provider call has run in this continuation
- fresh identity not executed
- Stage-A authority false
- Stage-B authority false
- Public-P1 authority false

Current repository HEAD before this re-review: `4b07559b68aabee5fcf37ec49f91d24dbec9cfa7`.

## 2. Prior independent verdict

Prior review conversation:
`https://chatgpt.com/g/g-p-6a6ad664d6508191bff6ecf4fde868f0-agent/c/6a9a38aa-7a10-83e8-b0c5-7d11683385db`

Prior verdict:
`REVISE_ZERO_PROVIDER_PLAN_OR_FRONTEND`

Prior audit also explicitly concluded:

- controlled workload: `SUFFICIENT`
- five independent skeletons: defensible for bounded claim
- B3 5/5 procedural gate: valid/conservative
- baseline method set: sufficient
- R2 redesign required: NO
- additional pre-Stage-A experiment required: NO
- immediate action after repair should return to existing fresh-identity boundary

Exactly three required fixes were:

1. repair Public-P1 C4 so causal transport preserves common starting state, same realized search/evidence object, same served action, and only `g(T_K)` changes; keep end-to-end method comparison separate;
2. distinguish stochastic full-evolution variance from repeated heldout measurement variance, requiring a small preregistered set of full-evolution replicates when evolution is stochastic;
3. repair frontend/paper semantics: remove global “best to act != best to learn”, rename aggregate 0/5 authority counter to execution/gate status, and qualify public MRW4 with a prospectively frozen public-compatible alternative.

## 3. Exact repaired objects

Zero-provider repair commit:
`1e3db1ec2d25addddde2112f7871223f1e3d0728`

Provenance-sync HEAD:
`4b07559b68aabee5fcf37ec49f91d24dbec9cfa7`

Repaired hashes:

- plan V4: `69f1d9d599eaca1ff0fcbf31a6a2d4a27c6432a302e2d25b2dc7b399fda60a91`
- execution map: `1e327f8736cb60e0d7ad8ed23b5f4cce837497709ee7d8146077f0edb44dc8bc`
- frontend status: `a9b15beecac846d46eb61f443ce4460bf7743bbaca22545ce634c6ac4f6648d6`
- frontend renderer: `94c5a679af79bb6e3303052f718bfc7b395c76d0ee47902052224d9ced6a9f30`
- revised paper story: `e77ccc28e5ea7955523025e2de3f767f1414d9cb868f663a6cba8a65e4279ea5`
- revised paper outline: `d637a7d4775ff94e936b3c875a459e3caefe45561f5575aa1f889f094adc05ff`
- repair receipt: `289dc8b18180a208f79ea25a7bf78bfa3b68abe9da56ea3ac72616e4eaac9d94`

## 4. Fix 1 — Public-P1 causal transport

Public P1 remains one SpreadsheetBench Verified lane but now explicitly contains two distinct estimands:

### 4.1 End-to-end method comparison

C1–C3 compare complete methods under one common public 80/40/280 harness.

### 4.2 Paired causal transport sub-experiment

C4 now requires, before outcomes:

- eligibility frozen from ordinary pre-treatment/pre-update observables;
- common starting persistent state `S0_public` for the paired natural unit;
- one common realized/content-addressed `T_K_public` acquired once;
- common verifier/selection result and common served action `a(T_K_public)`;
- common updater/configuration, evidence budget, update order, and downstream evaluation panel;
- WIN-C and the prospectively frozen public-compatible alternative learner projection both constructed from that same `T_K_public`;
- only learner-visible `g(T_K_public)` may differ.

C4 primary endpoint is now:

`Delta_transport = U_future(g_ALT(T_K_public)) - U_future(g_WIN(T_K_public))`

paired over the frozen eligible natural units.

The plan explicitly forbids second search acquisition, different served actions, different starting states, or method-history-specific pools inside this causal transport contrast.

Method-table success and causal transport PASS are explicitly separate claims.

## 5. Fix 2 — public evolution replication

The repaired rule is:

- if the **entire evolution procedure is deterministic** after model identity, decoding, seeds, candidate generation, validation selection, update order, and all other randomness are pinned, one evolution realization is sufficient;
- if **evolution itself remains stochastic**, use the same preregistered **3 paired full-evolution seeds** for every affected unified-rerun method;
- repeated heldout panels are used separately only for residual executor/evaluator stochasticity.

Full-evolution seeds estimate optimizer/evolution variance. Heldout repeats estimate measurement noise. No result-contingent seed addition is allowed.

## 6. Fix 3 — paper/frontend semantics

The repaired current paper story explicitly says:

> Do not use the global slogan “the best trajectory to act on is not always the best to learn from.” Even if the secondary procedural gate passes, the experiment does not optimize over all possible learner projections. The strongest bounded statement is that, on the five preregistered procedural skeletons with serving fixed, the tested alternative learner projection outperforms winner-coupled learning.

The paper outline likewise forbids a global best-to-act/best-to-learn title.

Frontend repair:

- aggregate `0/5` label is now `Current execution gates / status flags`, not scientific execution authority;
- portfolio aggregate uses `execution gates / status flags`;
- Public anchor is `Universal MRW4 / prospectively frozen public-compatible alternative`;
- frontend claim boundary says even B2+B3 PASS only establishes tested alternative > WIN-C on the five preregistered procedural skeletons with serving fixed, not a globally “best to learn” projection;
- Public-P1 frontend purpose says end-to-end method comparison and paired causal transport are separate estimands in one lane;
- frontend evaluation text distinguishes 3 paired full-evolution seeds for stochastic evolution from repeated heldout measurement panels.

## 7. Audit questions

Audit only these questions:

### A. Transport repair

Does repaired C4 now actually transport the same exact-same-pool, acting-fixed learner-projection estimand as B2 on natural units? Is any verdict-changing causal confound still introduced by the repaired design?

### B. Unified lane separation

Is it scientifically valid to keep end-to-end method ranking and causal transport in one public benchmark lane while analyzing them as separate estimands?

### C. Replication repair

Does the deterministic-vs-stochastic rule correctly separate full-evolution variance from heldout measurement variance? Is 3 paired full-evolution seeds a defensible minimal rule when evolution remains stochastic?

### D. Claim semantics

Are the paper story/outline now bounded correctly, or is there any remaining phrase that still implies global optimization over learner projections?

### E. Frontend fidelity

Do the repaired frontend status/view now accurately distinguish planning/evidence/authority/status and preserve the public-compatible-alternative qualification?

### F. Remaining pre-Stage-A blocker

After these fixes, is there any verdict-changing zero-provider issue that must still be repaired **before** the existing exactly-one fresh DeepSeek identity qualification? Do not request downstream Public-P1 packet details that are already scheduled to be frozen only after B2 PASS.

## 8. Required final synthesis

End with:

- `transport_identification`: PASS / REVISE
- `replication_rule`: PASS / REVISE
- `claim_semantics`: PASS / REVISE
- `frontend_fidelity`: PASS / REVISE
- `r2_redesign_required`: YES / NO
- `additional_pre_stage_a_experiment_required`: YES / NO
- `immediate_action`: `PROCEED_EXISTING_FRESH_IDENTITY_BOUNDARY` / `ONE_MORE_ZERO_PROVIDER_FIX` / `REOPEN_R2` / `STOP`
- at most TWO verdict-changing fixes if any

Then end with exactly one verdict token:

`PASS_REPAIRED_LATEST_E2_R17_PLAN_AND_FRONTEND`
`REVISE_REPAIR_BEFORE_IDENTITY`
`REOPEN_R2_BEFORE_EXECUTION`
`STOP_E2_R17`


## FILE 2: repaired execution map

# E2-R17 Experiment Plan V4 — Clean Execution Map

Date: 2026-09-04
Status: `ZERO_PROVIDER_EXECUTION_MAP_ONLY`
Parent plan: `consultations/e2-r17-experiment-plan-v4-20260904.md`
Frozen R2 contract SHA256: `f5382c552f2e6644e4cbda408510119664a8c6f8502628586c9ff5583abd1234`
Frozen R2 preflight SHA256: `e257438bd482d4f2209a8321d4a222bd97acf2c03bff46a1d5513b55a42ca766`

This is the compact execution-facing map. It does not modify the frozen R2 experiment or grant any scientific authority.

## A. What is already complete

### A1 — Availability / censoring support

Purpose: establish that search generates evidence that winner-coupled learning can fail to observe.

Existing evidence:

- 96 K=8 pools;
- 768 rollout references;
- 78/96 mixed pools;
- 12/12 exposed streams;
- 6/6 failure families.

Scientific role: treatment support / phenomenon only.

Not allowed: infer that omitted evidence is useful.

### A2 — Closed global causal study

Purpose: test a simple universal alternative-projection rule.

Existing evidence:

- 12 streams;
- 48 paired replicate units;
- 96 learned states;
- 1728 heldout units;
- WIN-C ≈ 79.05%;
- universal MRW ≈ 81.37%;
- +2.3148 pp;
- exact historical one-sided sign-flip p = 0.171875;
- paired CI crosses zero.

Scientific role: reliable global MRW benefit was not established.

Decision consequence: motivates a prospective moderator hypothesis; does not prove heterogeneity.

---

# B. Mandatory controlled experiment — V3/R2

This is the next scientific lane. Do not redesign it.

## B0 — Fresh model identity gate

Action:

- exactly one fresh DeepSeek V4-Pro identity qualification;
- local identity adjudication;
- if PASS, separately mint single-use Stage-A authorization.

Scientific data produced: none.

Current status: NOT EXECUTED / NOT AUTHORIZED.

## B1 — Stage A: support acquisition

Claim served: positivity / treatment support for the frozen V3 intervention.

Scale:

- 5 matched skeletons;
- 2 semantic cells/skeleton;
- 2 streams/cell;
- 20 streams;
- 8 update tasks/stream;
- 160 tasks;
- K=8;
- 1280 actor rollouts;
- 160 sealed pools;
- 0 updater calls;
- 0 heldout access.

Primary endpoint:

- every stream has >=4 mixed pools.

PASS:

- freeze exactly four treated mixed pools/stream under the existing hash rule;
- permit preparation of separate Stage-B authorization.

FAIL:

- `HOLD_V3_SUPPORT_NOT_ESTABLISHED`;
- no task/stream/skeleton/model/K replacement;
- no Stage B.

Independent scientific unit: stream for support; no mechanism claim yet.

## B2 — Stage B: exact-same-pool causal mechanism

Claim served: changing learner-visible projection while holding exact search pool and current acting fixed causally changes future persistent-skill utility in a structure-dependent way.

Scale:

- 20 streams;
- WIN-C and MRW4 from same Stage-A pools/state;
- R=4 measurement replicates;
- 80 paired stream-replicate units;
- 160 learned states;
- 20 common heldout tasks/state;
- 3200 heldout evaluations.

Independent confirmatory scientific unit:

- 5 matched skeleton interactions.

Estimands:

`D_s = mean_r[J_s,r(MRW4)-J_s,r(WIN-C)]`

`D_h,z = mean_{s in (h,z)} D_s`

`I_h = D_h,PROCEDURAL - D_h,BINDING`

Primary endpoint:

- frozen five-skeleton interaction gate.

PASS:

- structure-dependent projection effect is supported on the controlled suite;
- evaluate B3;
- public P1 may be designed/frozen.

FAIL:

- standalone strong E2-R17 mechanism story stops;
- no router, public benchmark, second model, subset, or extra replicate may rescue it.

## B3 — Secondary controlled-divergence gate

New data collection: NONE.

Claim served: determine whether the controlled experiment contains a genuinely positive procedural alternative-projection region, rather than only a positive difference-of-effects.

Endpoint:

`D_h,PROCEDURAL > 0` for all five frozen skeletons, evaluated only after B2 PASS.

PASS:

- unlock bounded statement that alternative learner projection beats WIN-C across all five preregistered procedural skeletons while exact pool and acting are fixed.

FAIL:

- retain B2 effect-modification claim;
- stronger controlled act/learn-divergence thesis remains locked;
- no favorable cell selection after outcomes.

---

# C. Mandatory paper-completion lane after B2 PASS — Public P1

One public lane should simultaneously provide:

1. natural/out-of-family transport;
2. closest-method baseline comparison;
3. realistic cost/accounting evidence.

Do not split these into separate benchmark campaigns.

## C0 — Outcome-blind public packet freeze

Before any public scientific updater call, freeze:

- SpreadsheetBench Verified-400 exact version/workbook hashes;
- exact 80/40/280 evolution/validation/test IDs;
- official evaluator;
- actor/updater identities;
- tool harness and turn budget;
- formula recalculation policy;
- method adapter versions;
- evidence/update budget accounting;
- public E2 eligibility/policy rule;
- primary endpoints and stop rules.

Then obtain an independent zero-provider review.

No public execution before this gate.

## C1 — Unified main-table evolution

Primary model/harness:

- one common qualified DeepSeek V4-Pro lane first.

Mandatory anchors:

1. No Skill;
2. Initial/Parent Skill;
3. WIN-C;
4. Universal MRW4 or nearest prospectively frozen public-compatible rejected-witness projection.

Mandatory closest methods:

5. RethinkSkill Normal;
6. RethinkSkill Success-only;
7. RethinkSkill Fail-only;
8. SkillOpt;
9. at least ONE trajectory-to-skill / contrastive baseline under a credible implementation:
   - prefer Trace2Skill if official runtime qualification succeeds;
   - otherwise use clearly labeled SkillCAT-style contrast;
   - run both only if they answer materially different claims at acceptable marginal cost.

Conditional E2 method row:

10. Frozen E2 observable projection policy, only if its pre-update observable rule can be transported without hidden controlled-suite semantics.

Fairness rule:

- same 80/40/280 IDs;
- same primary actor;
- same harness/evaluator/turn budget;
- same accounting ceilings;
- source-semantic-compatible updater role;
- no copied published score for direct ranking.

Scientific question:

> under a common realistic harness, how does E2 compare with the strongest nearby self-evolving-skill methods?

## C2 — Validation/selection

Use only the frozen 40 validation tasks for method-permitted selection/early stopping.

Never use test tasks for:

- model selection;
- prompt selection;
- router thresholds;
- eligibility rules;
- hyperparameter changes;
- baseline adapter changes.

Final persistent artifact for each method is content-addressed before test.

## C3 — Common heldout test

Evaluate every frozen final artifact on the same 280 heldout tasks.

Primary method-comparison endpoint:

- official SpreadsheetBench heldout success/utility.

Required reporting:

- point estimate;
- delta vs Parent;
- delta vs WIN-C;
- delta vs strongest closest baseline;
- paired per-task uncertainty;
- evolution/update cost;
- learner evidence/update token accounting.

Evolution versus measurement replication:

- if the full evolution procedure is deterministic after all randomness is pinned, one frozen evolution/selection realization is sufficient;
- if evolution itself remains stochastic, use the same preregistered **3 paired full-evolution seeds** for every affected unified-rerun method;
- after each final artifact is frozen, use up to 3 repeated heldout panels only for residual executor/evaluator stochasticity;
- full-evolution seeds estimate evolution variance; heldout repeats estimate measurement noise. They are reported separately.

## C4 — Paired natural-unit causal transport endpoint

Claim served: test whether the **exact-same-pool, acting-fixed learner-projection effect** has a prospectively identifiable positive counterpart on natural/out-of-family tasks.

C4 is a separate causal estimand inside the same Public-P1 lane; it is not the end-to-end method ranking from C1–C3.

Before outcomes, freeze eligibility using only pre-treatment observables. For every eligible natural unit, freeze:

- the same starting persistent state;
- one common realized/content-addressed search-evidence object `T_K_public`;
- the same verifier/served action;
- the same updater/configuration, evidence budget, update order, and downstream evaluation panel.

Construct WIN-C and the prospectively frozen public-compatible alternative projection from that **same `T_K_public`**. Only learner-visible `g(T_K_public)` may differ.

Primary endpoint:

`Delta_transport = U_future(g_ALT(T_K_public)) - U_future(g_WIN(T_K_public))`

paired over the frozen eligible public units.

PASS:

- unlock only the bounded causal natural-transport claim.

FAIL:

- preserve controlled V3 result only;
- do not reacquire alternate pools;
- no benchmark swap;
- no subgroup mining;
- no second model as rescue;
- no eligibility redesign after outcomes.

Note: method-table success and C4 transport PASS are distinct. A competitive E2 policy does not automatically establish causal transport, and a causal transport witness does not automatically imply end-to-end superiority over every baseline.

---

# D. Optional experiments — only after the required ladder is complete

## D1 — One second-model robustness lane

Candidate:

- qualified Qwen sparse 35B-class model OR Kimi K3.

Selection rule:

- runtime validity, availability, cost, and literature relevance only;
- never choose based on which model makes E2 look better.

Purpose:

- robustness/generalization, not rescue.

## D2 — Failure-specific diagnostic

Add matched successful-nonwinner / neutral-alternative control only if the paper wants to claim failure-specific unique value.

Not required for projection-interface novelty.

## D3 — Source-faithful appendix reproductions

Examples:

- SkillOpt official config/split;
- RethinkSkill original feedback protocol;
- Trace2Skill official settings;
- SkillCAT paper-spec reconstruction only when exact source implementation remains unavailable.

Purpose: adapter fidelity, not direct ranking.

## D4 — SpreadsheetBench 2 workflow transfer

Late externality only after the full required lane is complete and only if it answers a new workflow-level question.

---

# E. Main paper experiment mapping

| Paper question | Experiment | Required? | Independent unit | Primary endpoint |
|---|---|---:|---|---|
| RQ1 availability/censoring | historical support | complete | pool/stream support | mixed/evidence availability |
| RQ2 global causal consequence | closed global MRW | complete | 12 streams | paired future-skill contrast |
| RQ3 structural effect modification | V3 Stage B | yes | 5 skeletons | five `I_h` directions/magnitudes |
| RQ4 positive controlled divergence | secondary gate | yes, no new calls | 5 procedural effects | 5/5 `D_h,PROC>0` |
| RQ5 natural transport | Public P1 | yes after RQ3 PASS | frozen public eligible tasks | `Delta_transport` |
| Method competitiveness | Public P1 unified table | yes after RQ3 PASS | 280 heldout tasks | heldout utility + paired deltas |
| Cross-model robustness | second model | optional | same public task units | robustness of conclusions |

---

# F. Effective-workload rule

Do not add an experiment because the paper “looks small.” Admit a new tranche only if it prospectively:

1. tests a missing claim;
2. removes a material confound/alternative explanation;
3. supplies external validity unavailable from the controlled suite;
4. provides a necessary fair closest-method comparison; or
5. reduces uncertainty enough to change a frozen decision boundary.

Every new experiment must state:

- `claim_served`;
- `alternative_explanation_removed`;
- `independent_scientific_unit`;
- `primary_endpoint`;
- `decision_changed_if_pass`;
- `decision_changed_if_fail`;
- `stop_rule`.

GPU hours, provider calls, model count, benchmark count, rollout count, and heldout count are accounting variables, not scientific-workload units.

---

# G. Current exact state and next action

Current state at this map freeze:

- fresh identity qualification: absent;
- Stage-A authorization: absent;
- Stage-A run root: absent;
- Stage-B authority: false;
- Public P1 authority: false;
- baseline scientific execution: false.

Therefore the next executable boundary remains:

`exactly one fresh DeepSeek identity qualification -> local adjudication -> separate single-use Stage-A authorization if PASS`.

This map itself grants none of those authorities.


## FILE 3: repaired frontend status

```javascript
window.E2_R17_FRONTEND_STATUS = {
  schema_version: "1.0",
  as_of_date: "2026-09-04",
  project_track: "E2-R17",
  title: {
    zh: "解耦 Test-Time Search 的 Serving 与 Persistent Learning",
    en: "Decoupling Serving and Persistent Learning over Test-Time Search"
  },
  subtitle: {
    zh: "Exact-Same-Pool 因果识别 · Search-Projection Censoring · 当前为零执行权限",
    en: "Exact-same-pool causal identification · Search-Projection Censoring · zero execution authority"
  },
  paper_identity: "CAUSAL_SYSTEMS_INTERFACE_PAPER",
  scientific_object: {
    zh: "Search 先生成同一个 realized object T_K；当前行为消费 a(T_K)，持久学习消费 g(T_K)。核心实验固定 T_K 与 serving，只改变 learner-visible projection。",
    en: "Search first generates one realized object T_K; current behavior consumes a(T_K), while persistent learning consumes g(T_K). The core intervention fixes T_K and serving, changing only the learner-visible projection."
  },
  frozen_scientific_r2: {
    commit: "29799c83c662887694db52acba4bb19e83131bb0",
    contract_sha256: "f5382c552f2e6644e4cbda408510119664a8c6f8502628586c9ff5583abd1234",
    preflight_sha256: "e257438bd482d4f2209a8321d4a222bd97acf2c03bff46a1d5513b55a42ca766",
    changed_by_frontend: false
  },
  authority: {
    fresh_identity_called: false,
    stage_a: false,
    stage_b: false,
    public_p1: false,
    baseline_execution: false,
    provider_calls_current_continuation: 0
  },
  next_gate: {
    code: "ONE_FRESH_DEEPSEEK_IDENTITY_THEN_LOCAL_ADJUDICATION_THEN_SEPARATE_STAGE_A_AUTH",
    zh: "恰好 1 次 fresh DeepSeek identity qualification → 本地 adjudication → PASS 后另行签发一次性 Stage-A authorization。",
    en: "Exactly one fresh DeepSeek identity qualification → local adjudication → if PASS, separately mint single-use Stage-A authorization."
  },
  completed_evidence: [
    {
      id: "A1",
      title_zh: "Availability / censoring 支持",
      title_en: "Availability / censoring support",
      status: "COMPLETE",
      metrics_zh: "96 个 K=8 pools · 768 rollouts · 78/96 mixed pools · 12/12 exposed streams · 6/6 failure families",
      metrics_en: "96 K=8 pools · 768 rollouts · 78/96 mixed pools · 12/12 exposed streams · 6/6 failure families",
      claim_zh: "只证明 search object 中存在 winner-coupled learner 看不到的 evidence；不证明这些 evidence 有学习价值。",
      claim_en: "Shows that evidence exists in the search object but is hidden from winner-coupled learning; it does not establish learning value."
    },
    {
      id: "A2",
      title_zh: "Closed global exact-same-pool causal study",
      title_en: "Closed global exact-same-pool causal study",
      status: "COMPLETE_INCONCLUSIVE",
      metrics_zh: "12 streams · 48 paired replicates · 96 learned states · 1728 heldout units · MRW−WIN-C=+2.31pp · p=0.171875",
      metrics_en: "12 streams · 48 paired replicates · 96 learned states · 1728 heldout units · MRW−WIN-C=+2.31pp · p=0.171875",
      claim_zh: "可靠的 global universal-MRW benefit 未建立；结果与 underpower、heterogeneity 或两者兼容。",
      claim_en: "A reliable global universal-MRW benefit was not established; the result is compatible with underpower, heterogeneity, or both."
    }
  ],
  mandatory_controlled: [
    {
      id: "B0",
      title_zh: "Fresh model identity gate",
      title_en: "Fresh model identity gate",
      status: "NEXT_NOT_AUTHORIZED",
      scale_zh: "1 次 provider identity call；无科学 outcome",
      scale_en: "1 provider identity call; no scientific outcome",
      gate_zh: "identity PASS 才能另行 mint Stage-A authorization。",
      gate_en: "Only identity PASS permits a separately minted Stage-A authorization."
    },
    {
      id: "B1",
      title_zh: "V3 Stage A · support acquisition",
      title_en: "V3 Stage A · support acquisition",
      status: "PLANNED_LOCKED",
      scale_zh: "5 skeletons · 20 streams · 160 tasks · K=8 · 1280 actor rollouts · 0 updater · 0 heldout",
      scale_en: "5 skeletons · 20 streams · 160 tasks · K=8 · 1280 actor rollouts · 0 updater · 0 heldout",
      gate_zh: "20/20 streams 都必须至少有 4 个 mixed pools；任一失败即 HOLD，不换 task/model/K。",
      gate_en: "All 20 streams must have at least 4 mixed pools; any failure causes HOLD with no task/model/K replacement."
    },
    {
      id: "B2",
      title_zh: "V3 Stage B · exact-same-pool causal mechanism",
      title_en: "V3 Stage B · exact-same-pool causal mechanism",
      status: "CONDITIONAL_LOCKED",
      scale_zh: "20 streams · R=4 measurement reps · 80 paired units · 160 learned states · 3200 heldout evaluations · 5 independent skeleton interactions",
      scale_en: "20 streams · R=4 measurement reps · 80 paired units · 160 learned states · 3200 heldout evaluations · 5 independent skeleton interactions",
      gate_zh: "Primary gate 由 5 个 I_h 决定。FAIL 后 public benchmark、router、第二模型都不能 rescue。",
      gate_en: "The primary gate is decided by five I_h values. After FAIL, public benchmarks, router results, or a second model cannot rescue the mechanism claim."
    },
    {
      id: "B3",
      title_zh: "Secondary controlled-divergence gate",
      title_en: "Secondary controlled-divergence gate",
      status: "NO_NEW_DATA",
      scale_zh: "不新增调用；读取 B2 已冻结的 5 个 D_h,PROCEDURAL",
      scale_en: "No new calls; reads the five frozen D_h,PROCEDURAL values from B2",
      gate_zh: "Primary PASS 且 5/5 D_h,PROCEDURAL>0 才解锁 controlled act/learn divergence；不能事后挑正例。",
      gate_en: "Only primary PASS plus 5/5 D_h,PROCEDURAL>0 unlocks controlled act/learn divergence; no post-hoc positive-cell selection."
    }
  ],
  public_p1: {
    status: "CONDITIONAL_NOT_FROZEN",
    entry_zh: "只有 B2 primary interaction PASS 后才能冻结并独立预审 Public P1；绝不能用 public benchmark rescue V3 FAIL。",
    entry_en: "Public P1 may be frozen and independently prereviewed only after B2 primary interaction PASS; a public benchmark cannot rescue V3 FAIL.",
    substrate: "SpreadsheetBench Verified-400",
    split_policy: "80 evolution / 40 validation / 280 heldout test",
    exact_ids_frozen: false,
    purpose_zh: "同一条 public lane 承载两个分开的 estimand：统一 end-to-end closest-method comparison，以及 exact-same-pool / same-acting 的 paired causal transport；二者不能混为一个结果。",
    purpose_en: "One public lane carries two separate estimands: unified end-to-end closest-method comparison and paired exact-same-pool / same-acting causal transport; they must not be conflated.",
    primary_model_zh: "先只用一个统一主模型/harness：优先 DeepSeek V4-Pro exact qualified release；不做 4×4 模型矩阵。",
    primary_model_en: "Use one common primary model/harness first: preferably the exact qualified DeepSeek V4-Pro release; no 4×4 model matrix.",
    anchors: ["No Skill", "Initial / Parent Skill", "WIN-C", "Universal MRW4 / prospectively frozen public-compatible alternative"],
    closest_baselines: ["RethinkSkill Normal", "RethinkSkill Success-only", "RethinkSkill Fail-only", "SkillOpt"],
    contrastive_baseline_zh: "至少 1 个 credible trajectory-to-skill / contrastive baseline：优先 source-faithful Trace2Skill；否则清楚标注 SkillCAT-style reconstruction。",
    contrastive_baseline_en: "At least one credible trajectory-to-skill / contrastive baseline: prefer source-faithful Trace2Skill; otherwise clearly label a SkillCAT-style reconstruction.",
    evaluation_zh: "方法主表：所有最终 frozen artifacts 在同一 280 heldout tasks 上评估；若 evolution 本身随机，用预注册的 3 个 paired full-evolution seeds；heldout 重复只量化 measurement noise。Causal transport 另用同一自然 unit 的 common S0/T_K/served action，仅改变 g(T_K)。",
    evaluation_en: "Method table: evaluate all final frozen artifacts on the same 280 heldout tasks; if evolution itself is stochastic, use 3 preregistered paired full-evolution seeds, while heldout repeats quantify measurement noise only. Causal transport separately fixes common S0/T_K/served action per natural unit and changes only g(T_K).",
    transport_stop_zh: "transport 不支持时，不换 benchmark、不改 eligibility、不挖 subgroup、不用第二模型 rescue。",
    transport_stop_en: "If transport is unsupported, do not swap benchmark, alter eligibility, mine subgroups, or use a second model as rescue."
  },
  optional_after_required: [
    {id:"D1",zh:"一个第二模型 robustness：Qwen sparse 35B-class 或 Kimi K3，二选一。",en:"One second-model robustness lane: Qwen sparse 35B-class or Kimi K3, choose one."},
    {id:"D2",zh:"Failure-specific diagnostic：只有要声称 failure-specific causal value 才开。",en:"Failure-specific diagnostic only if the paper wants a failure-specific causal-value claim."},
    {id:"D3",zh:"Source-faithful appendix reproductions：验证 baseline adapter fidelity，不参与跨 split 直接排名。",en:"Source-faithful appendix reproductions to validate baseline-adapter fidelity; no direct cross-split ranking."},
    {id:"D4",zh:"SpreadsheetBench 2：只有回答新的 workflow-level question 才开。",en:"SpreadsheetBench 2 only if it answers a new workflow-level question."}
  ],
  rq: [
    {id:"RQ1",zh:"有没有 serving-induced censoring？",en:"Is serving-induced censoring measurable?"},
    {id:"RQ2",zh:"learner projection 是否具有 causal consequence？",en:"Does learner projection have a causal consequence?"},
    {id:"RQ3",zh:"projection effect 是否被 task/evidence structure 调节？",en:"Is the projection effect modified by task/evidence structure?"},
    {id:"RQ4",zh:"是否存在真正 positive 的 controlled act/learn divergence？",en:"Is there genuine positive controlled act/learn divergence?"},
    {id:"RQ5",zh:"能否 transport 到 natural public tasks，并与 closest methods 公平比较？",en:"Does the effect transport to natural public tasks and compare fairly with closest methods?"}
  ],
  workload_rule: {
    verdict: "CONTROLLED_WORKLOAD_SUFFICIENT_MISSING_PUBLIC_EVIDENCE_TYPE",
    zh: "Controlled workload 已经足够；后续不按 rollout/GPU/model/benchmark 数量堆工作量，只允许能新增可识别科学信息的 tranche。",
    en: "Controlled workload is already sufficient. Future workload is admitted only when it adds identifiable scientific information—not because it adds rollouts, GPU hours, models, or benchmarks.",
    admit_if_zh: ["服务新的 paper-level claim", "排除 verdict-changing alternative explanation", "补 external validity / transport", "提供 fair closest-method baseline", "把测量不确定性降到会改变预注册决策边界"],
    admit_if_en: ["serves a new paper-level claim", "removes a verdict-changing alternative explanation", "adds external validity / transport", "provides a fair closest-method baseline", "reduces measurement uncertainty enough to change a preregistered decision boundary"]
  },
  plan_artifacts: {
    roadmap: "consultations/e2-r17-experiment-plan-v4-20260904.md",
    execution_map: "consultations/e2-r17-experiment-plan-v4-execution-map-20260904.md",
    paper_outline: "paper_drafts/e2-r17-paper-outline-skillzip-iteration-20260903.md",
    plan_revision: "1e3db1ec2d25addddde2112f7871223f1e3d0728"
  }
};

```


## FILE 4: repaired frontend renderer

```javascript
(() => {
  const state = () => window.E2_R17_FRONTEND_STATUS || {};
  const pick = (zh, en) => language === "zh" ? zh : en;
  const text = (obj, key) => language === "zh" ? (obj?.[`${key}_zh`] ?? obj?.[key]?.zh ?? obj?.[key] ?? "") : (obj?.[`${key}_en`] ?? obj?.[key]?.en ?? obj?.[key] ?? "");
  const hash12 = value => String(value || "--").slice(0,12);
  const tone = status => {
    const s=String(status||"").toUpperCase();
    if(s.includes("COMPLETE") && !s.includes("INCONCLUSIVE")) return "pass";
    if(s.includes("PASS")) return "pass";
    if(s.includes("INCONCLUSIVE") || s.includes("NEXT") || s.includes("NO_NEW_DATA") || s.includes("CONDITIONAL")) return "check";
    if(s.includes("LOCKED") || s.includes("NOT_AUTHORIZED") || s.includes("NOT_FROZEN")) return "planned";
    if(s.includes("FAIL") || s.includes("STOP")) return "fail";
    return "planned";
  };
  const badge = (status,label) => `<span class="experiment-status-badge status-${tone(status)}">${esc(label || status || "--")}</span>`;
  const statusLabel = status => {
    if(language!=="zh") return String(status||"").replaceAll("_"," ");
    return ({
      COMPLETE:"已完成",
      COMPLETE_INCONCLUSIVE:"已完成 · 全局收益未建立",
      NEXT_NOT_AUTHORIZED:"下一门禁 · 未授权",
      PLANNED_LOCKED:"已冻结 · 未授权",
      CONDITIONAL_LOCKED:"条件开放 · 当前锁定",
      NO_NEW_DATA:"零新增数据 · 结果判定门",
      CONDITIONAL_NOT_FROZEN:"条件开放 · Public packet 未冻结"
    })[status] || String(status||"");
  };
  const authoritySummary = s => {
    const a=s.authority||{};
    const values=[a.fresh_identity_called,a.stage_a,a.stage_b,a.public_p1,a.baseline_execution];
    const enabled=values.filter(Boolean).length;
    return {enabled,total:values.length};
  };
  const stageCard = row => `<article class="e2r17-stage-card status-${tone(row.status)}"><header><span>${esc(row.id)}</span>${badge(row.status,statusLabel(row.status))}</header><h3 data-toc="false">${esc(text(row,"title"))}</h3><p class="e2r17-stage-scale">${esc(text(row,"scale"))}</p><p>${esc(text(row,"gate"))}</p></article>`;
  const evidenceCard = row => `<article class="e2r17-evidence-card status-${tone(row.status)}"><header><span>${esc(row.id)}</span>${badge(row.status,statusLabel(row.status))}</header><h3 data-toc="false">${esc(text(row,"title"))}</h3><p class="e2r17-stage-scale">${esc(text(row,"metrics"))}</p><p>${esc(text(row,"claim"))}</p></article>`;
  const rqStrip = s => `<div class="e2r17-rq-strip">${(s.rq||[]).map(row=>`<span><b>${esc(row.id)}</b>${esc(language==="zh"?row.zh:row.en)}</span>`).join("")}</div>`;
  const authorityBlock = s => {
    const a=s.authority||{}, x=authoritySummary(s);
    return `<div class="e2r17-authority"><div><b>${pick("当前执行门禁 / 状态","Current execution gates / status flags")}</b><strong>${x.enabled}/${x.total}</strong></div><span>${pick(`fresh identity=${a.fresh_identity_called?"已执行":"未执行"} · Stage A=${a.stage_a?"已授权":"未授权"} · Stage B=${a.stage_b?"已授权":"未授权"} · Public P1=${a.public_p1?"已授权":"未授权"} · baseline=${a.baseline_execution?"已执行":"未执行"}`,`fresh identity=${a.fresh_identity_called?"executed":"not executed"} · Stage A=${a.stage_a?"authorized":"not authorized"} · Stage B=${a.stage_b?"authorized":"not authorized"} · Public P1=${a.public_p1?"authorized":"not authorized"} · baseline=${a.baseline_execution?"executed":"not executed"}`)}</span></div>`;
  };
  const publicPanel = s => {
    const p=s.public_p1||{};
    const baselineRows=[...(p.anchors||[]).map(x=>["Anchor",x]),...(p.closest_baselines||[]).map(x=>["Closest",x])];
    return `<section class="e2r17-public-lane"><header><div><span>C · PUBLIC P1</span><h3 data-toc="false">${esc(p.substrate||"SpreadsheetBench Verified-400")}</h3><p>${esc(text(p,"purpose"))}</p></div>${badge(p.status,statusLabel(p.status))}</header><div class="e2r17-public-grid"><article><b>${pick("进入条件","Entry condition")}</b><p>${esc(text(p,"entry"))}</p><small>${pick("Exact public IDs 当前未冻结；任何 public outcome 前必须固定。","Exact public IDs are not yet frozen and must be pinned before any public outcome.")}</small></article><article><b>${pick("统一 split / 主模型","Unified split / primary model")}</b><p><strong>${esc(p.split_policy||"")}</strong></p><p>${esc(text(p,"primary_model"))}</p></article><article><b>${pick("一次完成两件事","One lane, two purposes")}</b><p>${pick("Natural transport + closest-method baseline comparison 共用同一 split、actor/updater role、harness、evaluator 与 heldout panel。","Natural transport and closest-method comparison share the same split, actor/updater role, harness, evaluator, and heldout panel.")}</p></article></div><div class="advisor-table-scroll"><table class="matrix e2r17-baseline-table"><thead><tr><th>${pick("层级","Type")}</th><th>Baseline</th><th>${pick("为什么需要","Why it is there")}</th></tr></thead><tbody>${baselineRows.map(([kind,name])=>`<tr><td>${esc(kind)}</td><td><strong>${esc(name)}</strong></td><td>${esc(kind==="Anchor"?pick("能力 / parent / tied-projection / fixed-alternative 锚点","Capability / parent / tied-projection / fixed-alternative anchor"):pick("与当前 self-evolving skill 文献做统一 harness 公平比较","Fair unified-harness comparison against current self-evolving-skill methods"))}</td></tr>`).join("")}<tr><td>Contrastive</td><td><strong>${pick("Trace2Skill（优先）或 SkillCAT-style","Trace2Skill (preferred) or SkillCAT-style")}</strong></td><td>${esc(text(p,"contrastive_baseline"))}</td></tr></tbody></table></div><div class="e2r17-public-footer"><span><b>${pick("统一 heldout","Unified heldout")}</b>${esc(text(p,"evaluation"))}</span><span><b>${pick("Transport STOP","Transport STOP")}</b>${esc(text(p,"transport_stop"))}</span></div></section>`;
  };
  const optionalPanel = s => `<details class="e2r17-optional"><summary><div><b>${pick("D · 可选 robustness / claim expansion","D · Optional robustness / claim expansion")}</b><span>${pick("只有 required ladder 完整后才考虑；不能 rescue earlier gate failure。","Consider only after the required ladder is complete; none may rescue an earlier gate failure.")}</span></div><strong>${(s.optional_after_required||[]).length}</strong></summary><div>${(s.optional_after_required||[]).map(row=>`<article><span>${esc(row.id)}</span><p>${esc(language==="zh"?row.zh:row.en)}</p></article>`).join("")}</div></details>`;
  const workloadPanel = s => {
    const w=s.workload_rule||{};
    const rules=language==="zh"?w.admit_if_zh:w.admit_if_en;
    return `<aside class="e2r17-workload"><header><span>${pick("有效工作量原则","EFFECTIVE WORKLOAD")}</span>${badge(w.verdict,pick("Controlled workload 已够","Controlled workload sufficient"))}</header><p>${esc(language==="zh"?w.zh:w.en)}</p><ul>${(rules||[]).map(x=>`<li>${esc(x)}</li>`).join("")}</ul></aside>`;
  };

  window.renderE2R17ExperimentPanel = function(){
    const s=state(); if(!s.project_track)return "";
    return `<section class="panel e2r17-project-panel" id="e2-r17-current-experiment"><header class="e2r17-project-head"><div><div class="eyebrow">${esc(s.project_track)} · ${pick("当前 Project Track · 实验执行图","CURRENT PROJECT TRACK · EXPERIMENT EXECUTION MAP")} · ${esc(s.as_of_date||"")}</div><h2 data-toc="false">${esc(text(s,"title"))}</h2><p>${esc(text(s,"scientific_object"))}</p></div>${badge("NEXT_NOT_AUTHORIZED",pick("Roadmap frozen · 0 authority","Roadmap frozen · 0 authority"))}</header>${authorityBlock(s)}<div class="e2r17-next-gate"><b>${pick("下一条真正可执行门禁","Next executable gate")}</b><span>${esc(language==="zh"?s.next_gate?.zh:s.next_gate?.en)}</span></div>${rqStrip(s)}<h3 class="e2r17-section-title" data-toc="false">${pick("A · 已完成证据：不再重复跑","A · Completed evidence: do not rerun")}</h3><div class="e2r17-evidence-grid">${(s.completed_evidence||[]).map(evidenceCard).join("")}</div><h3 class="e2r17-section-title" data-toc="false">${pick("B · 必跑 Controlled V3：每一层都有硬门","B · Mandatory controlled V3: every stage has a hard gate")}</h3><div class="e2r17-stage-grid">${(s.mandatory_controlled||[]).map(stageCard).join("")}</div>${publicPanel(s)}${optionalPanel(s)}${workloadPanel(s)}<footer class="e2r17-provenance"><span>${pick("Frozen R2","Frozen R2")} · commit ${esc(hash12(s.frozen_scientific_r2?.commit))}… · contract ${esc(hash12(s.frozen_scientific_r2?.contract_sha256))}… · preflight ${esc(hash12(s.frozen_scientific_r2?.preflight_sha256))}…</span><span>${pick("前端更新不改变 R2 scientific object，也不产生 provider / Stage-A / Stage-B / Public-P1 authority。","This frontend update does not change the R2 scientific object or create provider / Stage-A / Stage-B / Public-P1 authority.")}</span></footer></section>`;
  };

  window.renderE2R17PortfolioAddendum = function(){
    const s=state(); if(!s.project_track)return "";
    const a=authoritySummary(s), b2=(s.mandatory_controlled||[]).find(x=>x.id==="B2")||{}, p=s.public_p1||{};
    return `<section class="portfolio-decision-console e2r17-portfolio-addendum" id="e2-r17-project-addendum"><header class="portfolio-decision-head"><div><div class="eyebrow">${esc(s.project_track)} · ${pick("PROJECT TRACK ADDENDUM · 不覆盖 A–G canonical ledger","PROJECT TRACK ADDENDUM · DOES NOT OVERRIDE THE A–G CANONICAL LEDGER")}</div><h2 data-toc="false">${esc(text(s,"title"))}</h2><p>${esc(text(s,"scientific_object"))}</p></div><nav><a href="experiments.html#e2-r17-current-experiment">${pick("打开完整实验执行图 →","Open full experiment map →")}</a></nav></header><div class="portfolio-decision-metrics e2r17-portfolio-metrics"><span><b>2</b>${pick("已完成证据块","completed evidence blocks")}</span><span><b>4</b>${pick("Controlled V3 门禁","controlled V3 gates")}</span><span><b>${a.enabled}/${a.total}</b>${pick("执行门禁 / 状态","execution gates / status flags")}</span><span><b>1</b>${pick("计划中的 public lane","planned public lane")}</span></div><div class="e2r17-portfolio-summary"><article><b>${pick("论文身份","Paper identity")}</b><strong>${esc(s.paper_identity)}</strong><p>${pick("核心不是 failure-learning heuristic，而是 exact-same-pool、acting-fixed 的 serving→persistent-learning projection interface 因果识别。","The core is not a failure-learning heuristic, but exact-same-pool, acting-fixed causal identification of the serving→persistent-learning projection interface.")}</p></article><article><b>${pick("Controlled 主实验","Controlled main experiment")}</b>${badge(b2.status,statusLabel(b2.status))}<p>${esc(text(b2,"scale"))}</p></article><article><b>${pick("论文完整性缺口","Paper-completion gap")}</b>${badge(p.status,statusLabel(p.status))}<p>${pick(`${p.substrate||"SpreadsheetBench Verified-400"} 将 natural transport 与 closest-method baseline 主表合并成一条 public lane。`,`${p.substrate||"SpreadsheetBench Verified-400"} combines natural transport and the closest-method baseline table in one public lane.`)}</p></article></div><div class="e2r17-next-gate"><b>${pick("当前唯一下一步","Only current next step")}</b><span>${esc(language==="zh"?s.next_gate?.zh:s.next_gate?.en)}</span></div></section>`;
  };

  window.renderE2R17PaperAddendum = function(){
    const s=state(); if(!s.project_track)return "";
    return `<section class="paper-detail-section e2r17-paper-addendum" id="paper-e2-r17-project-track" data-paper-toc-root><header class="paper-detail-header"><div><div class="eyebrow">${esc(s.project_track)} · ${pick("PROJECT PAPER ADDENDUM · 尚未写入 canonical PaperRegistry","PROJECT PAPER ADDENDUM · NOT YET IN THE CANONICAL PAPERREGISTRY")}</div><h2>${esc(text(s,"title"))}</h2><p>${esc(text(s,"subtitle"))}</p></div>${badge("NEXT_NOT_AUTHORIZED",pick("ZERO AUTHORITY","ZERO AUTHORITY"))}</header><div class="e2r17-paper-story"><article><b>${pick("一句话科学对象","Scientific object")}</b><p>${esc(text(s,"scientific_object"))}</p></article><article><b>${pick("RQ1–RQ5 证据链","RQ1–RQ5 evidence ladder")}</b>${rqStrip(s)}</article><article><b>${pick("当前 claim 边界","Current claim boundary")}</b><p>${pick("全局 MRW benefit 未建立；V3 interaction 尚无 outcome。即使 primary PASS + 5/5 procedural positive，也只能说明在这 5 个预注册 procedural skeleton 上，测试的 alternative learner projection 优于 WIN-C learning，同时 serving 固定；不能写成全局的 “best to learn”。","Global MRW benefit is not established and V3 has no outcome yet. Even primary PASS plus 5/5 positive procedural effects would only show that the tested alternative learner projection beats WIN-C learning on the five preregistered procedural skeletons while serving is fixed; it does not establish a globally 'best to learn' projection.")}</p></article></div><div class="e2r17-paper-links"><a class="link-btn" href="experiments.html#e2-r17-current-experiment">${pick("实验执行图 →","Experiment execution map →")}</a><a class="link-btn" href="paper-ideas.html#e2-r17-project-addendum">${pick("Research Portfolio 项目卡 →","Research Portfolio addendum →")}</a></div><small class="e2r17-paper-boundary">${pick("这是一条 project-level paper track 投影，不会修改现有 STRI / A–G ResearchItem / PaperRegistry 的 canonical 状态。","This is a project-level paper-track projection and does not modify the canonical STRI / A–G ResearchItem / PaperRegistry state.")}</small></section>`;
  };
})();

```
