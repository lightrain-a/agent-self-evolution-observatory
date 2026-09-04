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
