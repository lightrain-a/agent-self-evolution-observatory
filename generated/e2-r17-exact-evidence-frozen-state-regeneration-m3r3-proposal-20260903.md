# E2-R17 M3R3 — fully prospective frozen-state actor-noise localization

Status: **REVISED_AFTER_GPT56_PREEXECUTION_REVIEW / PROPOSAL_ONLY / ZERO_PROVIDER / NO_EXECUTION_AUTHORITY**

Base repaired M3R2 commit: `f8fb39d2289fdc3af2baa7bec23fe9c12087c1d1`.

Independent combined pre-execution review: Oracle Browser, GPT-5.6 Sol, Extra High, session `e2-r17-v4r1-m3r2-preexec`, conversation `6a999791-67c8-83e8-8b9a-8390f0ed20eb`, M3R2 verdict `REVISE_M3R2_BEFORE_EXECUTION`.

M3R3 repairs M3R2 without increasing scientific provider cost. The new budget remains exactly **72 actor units** and **0 updater calls**. The change is allocation and inference: all four actor observations entering the localization statistic are generated after this protocol is frozen, and a one-sided exact conditional randomization criterion is predeclared using the same 72 observations.

## 1. Scientific question

M3R3 asks only:

> For the two already-existing FF_R1 and FF_R2 persistent states produced from reconstructed byte-identical learner-visible First-Fail evidence, does fully prospective frozen-state actor evaluation show more cross-state outcome disagreement than within-state actor disagreement on the fixed selected development panel?

This remains a **selected-case development localization**. It does not create independent task/stream confirmation and does not estimate a population state-generation variance component.

## 2. Frozen persistent states

Primary localization uses exactly two already-existing states:

- `FF_R1`: SHA-256 `596bd30b49935d16f35d51e9eed36e19567332cd8a9104ae50d832f91ffdf04f`;
- `FF_R2`: SHA-256 `fb5454a27faf8182ba1b0d722273c4377d4762815cd1898c3780cc8ff336615e`.

They were produced by the already-consumed exact-evidence updater replay from reconstructed byte-identical learner-visible evidence. M3R3 makes **no new state synthesis** and cannot select a different state after actor outcomes.

Historical `FF_HIST` and `WIN_COMMON` remain background/descriptive artifacts only. They receive no new M3R3 actor execution and do not enter the M3R3 localization statistic or randomization gate.

This supersedes M3R2's plan to allocate new calls across four states; it does not change the total 72-unit budget.

## 3. Frozen task panel

Use the exact same 18 development held-out tasks as the exact-evidence replay:

- `r17-b4-agj-p2`, `r17-b4-agj-p3`, `r17-b4-agj-p8`;
- `r17-b4-fmv-p1`, `r17-b4-fmv-p2`, `r17-b4-fmv-p8`;
- `r17-b4-ioc-p1`, `r17-b4-ioc-p4`, `r17-b4-ioc-p6`;
- `r17-b4-msp-p0`, `r17-b4-msp-p7`, `r17-b4-msp-p8`;
- `r17-b4-ska-p4`, `r17-b4-ska-p5`, `r17-b4-ska-p8`;
- `r17-b4-tsr-p0`, `r17-b4-tsr-p6`, `r17-b4-tsr-p8`.

Suite root and manifests remain those already frozen by M3R/M3R2.

The panel is outcome-selected historically. Randomization inference below is conditional on this fixed panel and actor randomness; it does not justify treating the 18 tasks as independent population samples.

## 4. Actor/runtime independence contract

For every new M3R3 actor unit:

- requested model: `deepseek-v4-pro`;
- required resolved model: `deepseek-v4-pro-ga-260813`;
- thinking: disabled;
- temperature: 0;
- K=1;
- max turns: 10;
- max output tokens: 8192;
- provider retry limit: 0;
- same deterministic SpreadsheetBench verifier/runtime;
- fresh/reset task runtime for every logical unit;
- no conversation/context carryover across logical units;
- no shared user-specified random seed or cached task state across replicates;
- no outcome-conditioned retry or replacement;
- exact logical-unit order fixed before execution by a content-addressed salt.

The inferential model additionally assumes that, conditional on frozen state, task, resolved model, and runtime, the four actor executions for a task are iid/independent Bernoulli draws with stationary state-specific success probabilities. Logs can verify reset/context/model invariants but cannot prove absence of hidden provider-level correlation. Therefore:

- the **observed** `E_REAL` statistic remains valid descriptively regardless;
- the squared-propensity identity and exact randomization p-value receive their inferential interpretation only under the declared iid/stationarity assumption;
- any observed provider/runtime coupling, model-identity drift, evaluator drift, shared execution state, or other violation blocks the inferential label rather than being repaired by rerun.

## 5. Measurement allocation — exactly 72 new actor units

Generate exactly two fresh post-freeze actor realizations for each frozen state × task:

- FF_R1: 18 tasks × 2 replicates = 36 units;
- FF_R2: 18 tasks × 2 replicates = 36 units;
- total = **72 units**.

For task `q`, denote the four post-freeze observations:

- `A1(q)`, `A2(q)` for FF_R1;
- `B1(q)`, `B2(q)` for FF_R2.

Historical exact-replay actor results are not aliases for A1/B1 and are not inputs to the scientific gate.

The four logical units per task are hash-balanced under a frozen order salt so state and replicate are interleaved rather than grouped by time. Completed logical units are never replayed. Any quota/provider ambiguity fails closed under a separately authorized recovery object; no partial M3R3 effect is read before completion audit.

## 6. Observed excess-disagreement statistic

For each task:

`D_X(q) = 1/4 * [ |A1-B1| + |A1-B2| + |A2-B1| + |A2-B2| ]`

`D_A(q) = 1/2 * [ |A1-A2| + |B1-B2| ]`

`E_REAL(q) = D_X(q) - D_A(q)`.

Aggregate over the 18 frozen tasks:

`D_X = mean_q D_X(q)`

`D_A = mean_q D_A(q)`

`E_REAL = D_X - D_A`.

Because the two frozen state SHAs are distinct, no state-alias collapse is currently expected. If a future audit somehow resolves them to identical full persistent-state bytes, define `E_REAL=0` and the localization gate fails.

Under the declared conditionally iid/stationary Bernoulli model:

`E[E_REAL] = mean_q [p_A(q)-p_B(q)]^2`.

Without that model, M3R3 describes only observed cross-state-minus-within-state actor disagreement.

## 7. Exact one-sided conditional randomization gate

Raw `E_REAL>0` alone is not sufficient for latent propensity language because a positive finite-sample estimate can arise under the null.

M3R3 therefore freezes an exact conditional state-label randomization test using the **same 72 observations**.

For each task, condition on the observed total number of successes among `(A1,A2,B1,B2)`.

Under the task-wise null `p_A(q)=p_B(q)` and the iid Bernoulli actor model:

- totals 0, 1, 3, or 4 yield `E_REAL(q)=0` for every state-label assignment and are conditionally uninformative;
- with exactly two successes, all `C(4,2)=6` assignments are equiprobable;
- 2/6 assignments put both successes in one state, yielding `E_REAL(q)=1`;
- 4/6 split successes across states, yielding `E_REAL(q)=-1/2`.

Let:

- `n_2` = number of tasks with exactly two of four successes;
- `X` = number of those tasks whose two successes both occur within the same frozen state.

Then under the conditional null:

`X | n_2 ~ Binomial(n_2, 1/3)`.

The exact one-sided p-value is:

`p_exact = P[X_null >= X_observed | n_2]`.

This tail is monotone in aggregate `E_REAL` conditional on the observed task totals. No Monte Carlo seed or asymptotic approximation is required.

## 8. Frozen M3R3 decision

### 8.1 Bounded localization PASS

Require **both**:

1. `E_REAL > 0`;
2. `p_exact <= 0.05`.

If the iid/stationarity runtime assumption remains qualified, classify:

`M3R3_SELECTED_CASE_STATE_REALIZATION_LOCALIZATION_PASS`.

Allowed manuscript claim:

> On this fixed selected development panel, two distinct persistent states produced from the same reconstructed evidence show prospective cross-state outcome disagreement exceeding within-state actor disagreement, with a one-sided exact conditional randomization result against equal state-specific actor success propensities under the frozen iid/stationary actor model.

This is still not population generalization, not a variance-component estimate, and not proof that variance reduction causally mediates any compiler effect.

### 8.2 Observed excess positive but randomization gate fails

If `E_REAL > 0` but `p_exact > 0.05`:

`M3R3_OBSERVED_EXCESS_ONLY_NO_PROPENSITY_LOCALIZATION`.

The paper may report the observed excess disagreement but must not promote it as evidence that latent state-specific success propensities differ beyond actor noise.

### 8.3 Nonpositive excess

If `E_REAL <= 0`:

`ACTOR_NOISE_NOT_EXCLUDED / DOWNGRADE_STATE_REGENERATION_MECHANISM`.

The manuscript must remove the claim that the exact-evidence case demonstrates state-realization instability beyond actor disagreement. M2 manual-state semantics cannot rescue this mechanistic claim.

### 8.4 Runtime/iid qualification failure

If the execution audit detects shared task state, context carryover, model/evaluator identity drift, provider behavior that invalidates the frozen replicate contract, or another concrete independence/stationarity violation:

`M3R3_INFERENCE_ASSUMPTION_BLOCKED`.

Observed results may be archived descriptively, but neither `p_exact` nor the squared-propensity interpretation is promoted. No rerun is automatically authorized.

## 9. Descriptive historical context

The following remain reportable as already-consumed background evidence but do not enter M3R3 gate arithmetic:

- historical FF_HIST frozen-state remeasurements;
- original exact-replay FF_R1 and FF_R2 outcomes;
- byte-identical WIN-C state identity and its historical/fresh prior evaluations;
- original FF_R1 > FF_R2 aggregate ordering.

M3R3 must not call these prospective replicates or mix them into the exact p-value.

## 10. Supersession and cost boundary

M3R3 supersedes M3R2 before any M3R2 provider execution.

Compared with M3R2:

- new actor units: **72 → 72**;
- updater calls: **0 → 0**;
- persistent states synthesized: **0 → 0**;
- task artifacts: **18 → 18**;
- model/backbone: unchanged;
- public benchmark/E3: none;
- main change: 72 units are concentrated on two fully prospective frozen states rather than spread over four states, and exact conditional randomization is added at zero call cost.

Historical A1/B1 are removed from the scientific gate specifically because they are outcome-consumed in an outcome-selected case. This is a pre-execution repair required by independent review, not outcome-dependent sample replacement.

## 11. Authority

This proposal grants zero authority for:

- provider calls;
- M3R3 actor execution;
- updater calls;
- Recovery V3 modification;
- M4/Bridge execution;
- Semantic-Transfer execution;
- E3;
- second backbone;
- public benchmark;
- paper promotion or submission.

Before execution, M3R3 requires a content-addressed contract, unit-order manifest, runtime/preflight qualification, exactly-once provider budget, explicit measurement authorization, completion audit, and analysis authorization.
