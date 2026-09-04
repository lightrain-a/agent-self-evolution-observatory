# Independent adversarial review — latest E2-R17 experiment plan + frontend projection

Date: 2026-09-04
Role: independent senior ICLR/NeurIPS/ICML agent-systems methodology reviewer

## 0. Review rule

Review the **latest paper-level experiment plan and its frontend projection** as a fresh zero-provider object. Do not infer any V3 Stage-A, Stage-B, Public-P1, baseline, or transport outcome: none exists. Do not reopen the already independently reviewed V3/R2 causal protocol unless the latest paper plan requires a claim that R2 cannot identify. Do not request broad model/benchmark expansion merely for volume.

The purpose is to decide whether the current experiment package is scientifically sufficient, efficient, reviewer-facing, and faithfully represented in the frontend before the existing fresh-identity -> separately authorized Stage-A boundary.

## 1. Exact objects

Live repository HEAD before this review:

`423560da` — `Update frontend for E2-R17 experiment plan`

Frozen scientific V3/R2 object remains:

- scientific commit: `29799c83c662887694db52acba4bb19e83131bb0`
- contract: `generated/e2-r17-semantic-transfer-v3-stage-a-contract-r2-20260903.json`
- contract SHA256: `f5382c552f2e6644e4cbda408510119664a8c6f8502628586c9ff5583abd1234`
- preflight: `generated/e2-r17-semantic-transfer-v3-stage-a-preflight-r2-20260903.json`
- preflight SHA256: `e257438bd482d4f2209a8321d4a222bd97acf2c03bff46a1d5513b55a42ca766`

Latest plan files:

- `consultations/e2-r17-experiment-plan-v4-20260904.md`
  - SHA256 `cf3300b0ccf5d0a608b35f586a41c867ed45c962e614a5cde675bbd074385aea`
- `consultations/e2-r17-experiment-plan-v4-execution-map-20260904.md`
  - SHA256 `79888661586fea484dcad54902ead80b3275e8279710b66276adddf87f579218`

Latest frontend projection:

- `generated/e2-r17-frontend-status.js`
  - SHA256 `9e02c537b3242e0f2733e6b37fe30da178595d0ce02c6c75b0226cc6f5d3b21d`
- `e2-r17-frontend-view.js`
  - SHA256 `c8c8f7959c81285d76a68e4a3f2409cc7ed628bb924e035dca5decc2db827557`

Current authority remains:

- fresh DeepSeek identity call: not executed
- V3/R2 scientific provider calls in this continuation: 0
- Stage-A authority: false
- Stage-B authority: false
- Public-P1 authority: false
- baseline scientific execution: false

## 2. Current paper identity

The paper is deliberately framed as a **causal systems/interface paper**, not a generic failure-learning method paper.

Scientific object:

```text
T_K
 ├── a(T_K) -> current served behavior
 └── g(T_K) -> persistent updater evidence
```

Core identification device:

> Hold the exact realized `T_K`, current acting/served winner, initial state, updater/config/budget, update order, and heldout evaluation fixed; change only learner-visible projection `g(T_K)`.

The strongest novelty is the exact-same-pool, acting-fixed causal identification of the serving-to-persistent-learning projection interface. `Act–Learn Dual Projection` and `Search-Projection Censoring` are organizing terminology, not standalone novelty claims.

## 3. Evidence ladder

### A — already completed; no rerun

A1 availability/censoring support:

- 96 exact K=8 pools
- 768 rollout references
- 78/96 mixed pools
- 12/12 exposed streams
- 6/6 failure families
- no updater calls

Claim boundary: evidence availability only, not learning value.

A2 closed global exact-same-pool causal study:

- 12 streams
- 48 paired replicate units
- 96 learned states
- 1728 heldout units
- WIN-C ~79.05%
- universal MRW ~81.37%
- difference +2.3148pp
- paired bootstrap interval crosses zero
- exact historical one-sided sign-flip p=0.171875
- frozen verdict `HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS`

Permitted interpretation: reliable global universal-MRW benefit was not established; result is compatible with underpower, heterogeneity, or both.

### B — mandatory controlled V3

B0 fresh identity gate: exactly one DeepSeek identity qualification, then local adjudication, then separate single-use Stage-A authorization if PASS.

B1 Stage A support acquisition:

- 5 independent matched skeletons
- 2 semantic cells/skeleton
- 2 streams/cell
- 20 streams total
- 8 update tasks/stream
- 160 scientific update tasks
- K=8
- 1280 actor rollouts
- 160 sealed pools
- zero updater calls
- zero heldout access

Support condition: every one of the 20 streams must have >=4 mixed pools. Any failure -> HOLD; no task/stream/skeleton/model/K replacement.

B2 Stage B primary mechanism, only after separate authority:

- both WIN-C and MRW4 use exact same Stage-A pools/state
- R=4 measurement replication only
- 80 paired stream-replicate units
- 160 learned states
- 20 common heldout K=1 tasks/state
- 3200 heldout evaluations
- independent mechanism units: five matched-skeleton interactions

Primary interaction:

`I_h = D_h,PROCEDURAL - D_h,BINDING`.

Primary gate is the already-frozen five-skeleton directional interaction gate. If it fails, public benchmark, router, aggregate replicate significance, favorable subset, or second model cannot rescue the standalone strong mechanism story.

B3 secondary controlled-divergence claim gate, no new data:

Evaluate only after B2 primary PASS. PASS iff:

`D_h,PROCEDURAL > 0` for all five frozen skeletons.

This is a prospective finite-suite claim-adjudication rule, not a newly asserted exact p=1/32 inferential test. PASS unlocks only the bounded controlled-suite statement that an alternative learner projection outperformed WIN-C across all five preregistered procedural-transformation skeletons while exact pools and acting were fixed. FAIL leaves primary interaction PASS intact but keeps the stronger act/learn-divergence thesis locked.

### C — mandatory paper-completion lane after B2 PASS

Public P1 unifies **natural transport and closest-method baseline comparison** in one lane rather than duplicating experiments.

Primary substrate:

`SpreadsheetBench Verified-400`

Preferred unified split policy:

- 80 evolution/train
- 40 validation
- 280 heldout test

Exact IDs are explicitly NOT yet frozen; they must be pinned from audited public source or deterministic pre-outcome rule before any public scientific call.

Primary common model/harness first:

- DeepSeek V4-Pro exact qualified release, when source semantics permit
- one common actor/updater/harness/evaluator/accounting surface
- no 4x4 model cross-product

Unified main-table anchors:

- No Skill
- Initial / Parent Skill
- WIN-C
- Universal MRW4

Mandatory closest feedback/skill baselines:

- RethinkSkill Normal
- RethinkSkill Success-only
- RethinkSkill Fail-only
- SkillOpt

Trajectory-to-skill / contrastive reduction:

- require at least one credible baseline
- prefer source-faithful Trace2Skill if runtime qualification passes
- otherwise use clearly labeled SkillCAT-style reconstruction
- do not automatically run both unless they remove distinct alternative explanations

Conditional E2 policy row:

- only if pre-update observable extraction is frozen
- no hidden family/template/semantic labels
- no public outcome leakage into eligibility/router selection

Public evaluation:

- all final frozen artifacts evaluated on same 280 heldout tasks
- report point estimate, deltas vs Parent/WIN-C/strongest baseline, paired uncertainty, evolution cost, and learner evidence/update token budget
- one frozen evolution/selection run per baseline by default
- if heldout execution is stochastic, repeat the heldout panel 3 times on the same frozen artifact; those are measurement repeats, not independent evolution units

Transport endpoint:

`Delta_transport = U_future(E2 alternative projection) - U_future(WIN-C)`

for prospectively eligible natural units under the frozen public analysis rule. If unsupported: no benchmark swap, eligibility retuning, subgroup mining, or second-model rescue.

### D — optional only after required evidence ladder

- one second-model robustness lane: Qwen sparse 35B-class OR Kimi K3, choose one by outcome-blind runtime qualification
- failure-specific diagnostic only if the paper explicitly wants a failure-specific causal claim
- source-faithful appendix reproductions for adapter fidelity
- SpreadsheetBench 2 only if it answers a new workflow-level question

## 4. Effective-workload rule

Experiment volume counts only when it buys identifiable scientific information. A new tranche is admitted only if it does at least one of:

1. tests a paper-level claim not already identified;
2. removes a material alternative explanation/confound;
3. supplies external validity/transport unavailable from controlled data;
4. supplies a fair closest-method comparison needed to interpret the contribution;
5. reduces measurement uncertainty enough to change a predeclared decision boundary.

Rollout count, GPU hours, provider calls, learned-state count, heldout evaluations, number of models, and number of benchmarks are not by themselves scientific workload.

## 5. Frontend contract

The frontend now projects the latest plan into:

- `experiments.html`: full A/B/C/D execution map and hard gates
- `paper-ideas.html`: project-track portfolio addendum
- `selected-paper.html`: project-paper addendum with RQ1-RQ5 and claim boundary

Frontend status explicitly says:

- paper identity = `CAUSAL_SYSTEMS_INTERFACE_PAPER`
- current execution authority = 0/5 relevant authorities
- current next step = exactly one fresh DeepSeek identity qualification -> local adjudication -> separate Stage-A authorization if PASS
- Public P1 exact IDs not frozen
- global MRW benefit not established
- V3 interaction has no outcome
- stronger “best to act != best to learn” claim requires primary PASS plus 5/5 positive procedural simple effects
- controlled workload already sufficient; missing evidence type is public externality/baseline lane

The frontend is a project-track projection only and must not override canonical R2 scientific state or imply authorization.

## 6. Audit questions

Audit all of the following explicitly.

### A. Scientific ladder

Is A -> B -> C -> D the correct minimal evidence ladder for a standalone causal systems/interface paper? Is any required layer redundant, missing, or incorrectly ordered?

### B. Controlled workload sufficiency

Given the completed support/global study plus planned 1280 Stage-A rollouts, 160 learned states and 3200 Stage-B heldout evaluations, is additional controlled synthetic volume scientifically required before Public P1, or would that mostly be low-value repetition?

### C. Five independent skeletons

Is five independently crossed skeleton interactions defensible for the bounded mechanism claim if the frozen gate passes, provided magnitudes are shown and no population-generalization claim is made? If not, specify the smallest verdict-changing fix; do not request expansion merely for convention.

### D. Secondary 5/5 procedural gate

Is the secondary gate valid and appropriately separated from the primary interaction? Does it overconstrain the stronger paper thesis, or is that conservatism appropriate given only five frozen skeletons?

### E. Public P1 design

Is combining natural transport and closest-method comparison in one SpreadsheetBench Verified lane scientifically efficient and valid? Does the 80/40/280 policy create any obvious leakage or fairness flaw before exact IDs are frozen?

### F. Baseline sufficiency

Is the proposed public baseline set sufficient for reviewer-facing comparison? In particular, are RethinkSkill Normal/Success-only/Fail-only + SkillOpt + at least one credible trajectory-to-skill/contrastive baseline enough, or is one additional baseline truly verdict-changing? Do not propose a long list.

### G. Baseline fairness and replication

Is one frozen evolution/selection run per baseline plus repeated heldout evaluation of the same final artifact acceptable for the unified main table, or must full evolution itself be replicated for a fair claim? Distinguish measurement stability from optimizer/evolution stochasticity, and recommend the smallest necessary rule.

### H. Transport endpoint

Does the public transport endpoint actually test external validity of the interface claim rather than merely router performance? Identify any fatal mismatch.

### I. Optional experiments

Are second backbone, failure-specificity, source-faithful appendix reproductions, and SpreadsheetBench 2 correctly optional/non-rescue items?

### J. Frontend fidelity

Does the frontend status accurately represent planning vs evidence vs authority? Identify any wording that would mislead a reader into thinking a result, authorization, public split, or method superiority already exists.

### K. Paper identity and likely reviewer objection

After these revisions, what is the single strongest remaining reviewer objection *before outcomes*? Is it a reason to redesign now, or appropriately left to the prospective evidence ladder?

### L. Immediate action

Choose exactly one:

1. `PROCEED_EXISTING_FRESH_IDENTITY_BOUNDARY`
2. `ONE_ZERO_PROVIDER_FIX_BEFORE_IDENTITY`
3. `REOPEN_R2_BEFORE_EXECUTION`
4. `STOP_OR_PIVOT_NOW`

If choosing option 2 or 3, give only fixes that could change the verdict.

## 7. Required synthesis

End with:

- `controlled_workload`: SUFFICIENT / INSUFFICIENT
- `public_baseline_surface`: SUFFICIENT_IF_EXECUTED / NEEDS_ONE_FIX / INSUFFICIENT
- `frontend_fidelity`: PASS / REVISE
- `r2_redesign_required`: YES / NO
- `additional_pre_stage_a_experiment_required`: YES / NO
- `immediate_action`: exactly one option from Section 6L
- at most THREE verdict-changing recommendations

Then end with exactly one verdict token:

`PASS_LATEST_E2_R17_PLAN_AND_FRONTEND`
`REVISE_ZERO_PROVIDER_PLAN_OR_FRONTEND`
`REOPEN_R2_BEFORE_EXECUTION`
`STOP_E2_R17`
