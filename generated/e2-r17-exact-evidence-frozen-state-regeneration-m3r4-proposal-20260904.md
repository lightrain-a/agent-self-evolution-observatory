# E2-R17 M3R4 — fully prospective frozen-state actor-noise localization with cross-task factorization gate

Status: **REVISED_AFTER_M3R3_GPT56_PREEXECUTION_REREVIEW / PROPOSAL_ONLY / ZERO_PROVIDER / NO_EXECUTION_AUTHORITY**

Base M3R3 commit: `85a35740f201ac5095cfb9078e59420d2be1fd20`.

Independent rereview: Oracle Browser / GPT-5.6 Sol / Extra High, conversation `6a9a187e-91d8-83ee-b21b-5dfbf3d1a63d`. M3R3 verdict: `REVISE_BEFORE_EXECUTION` with exactly one remaining blocker: the aggregate conditional law `X | n_2 ~ Binomial(n_2,1/3)` requires explicit conditional independence/factorization across informative task blocks. Equal task success probabilities and exchangeability of task identities are not required.

M3R4 fixes only that inference assumption. It adds **zero** actor units, **zero** updater calls, zero states, zero tasks, zero models, and zero E3 authority relative to M3R3.

## 1. Scientific question — unchanged

M3R4 asks only:

> For the two already-existing FF_R1 and FF_R2 persistent states produced from reconstructed byte-identical learner-visible First-Fail evidence, does fully prospective frozen-state actor evaluation show more cross-state outcome disagreement than within-state actor disagreement on the fixed selected development panel?

This remains a **selected-case development localization**. It is not independent confirmation and does not estimate a population state-generation variance component.

## 2. Frozen persistent states — unchanged

Primary localization uses exactly two existing persistent states:

- `FF_R1`: SHA-256 `596bd30b49935d16f35d51e9eed36e19567332cd8a9104ae50d832f91ffdf04f`;
- `FF_R2`: SHA-256 `fb5454a27faf8182ba1b0d722273c4377d4762815cd1898c3780cc8ff336615e`.

No new state synthesis is allowed and no alternate state may replace either artifact after actor outcomes.

Historical `FF_HIST` and `WIN_COMMON` remain descriptive/background only. They receive no new M3R4 actor execution and do not enter the M3R4 statistic or exact conditional gate.

## 3. Frozen task panel — unchanged

Use the same 18 historically selected development held-out tasks:

- `r17-b4-agj-p2`, `r17-b4-agj-p3`, `r17-b4-agj-p8`;
- `r17-b4-fmv-p1`, `r17-b4-fmv-p2`, `r17-b4-fmv-p8`;
- `r17-b4-ioc-p1`, `r17-b4-ioc-p4`, `r17-b4-ioc-p6`;
- `r17-b4-msp-p0`, `r17-b4-msp-p7`, `r17-b4-msp-p8`;
- `r17-b4-ska-p4`, `r17-b4-ska-p5`, `r17-b4-ska-p8`;
- `r17-b4-tsr-p0`, `r17-b4-tsr-p6`, `r17-b4-tsr-p8`.

The panel remains outcome-selected historically. All inference is conditional on this fixed panel and actor randomness. Tasks are not promoted to independent population samples.

## 4. Measurement allocation — unchanged 72 actor units

Generate exactly two fresh post-freeze actor realizations for each frozen state × task:

- FF_R1: 18 tasks × 2 replicates = 36 units;
- FF_R2: 18 tasks × 2 replicates = 36 units;
- total = **72 new actor units**.

For task `q`, denote:

- `A1(q)`, `A2(q)` for FF_R1;
- `B1(q)`, `B2(q)` for FF_R2.

All four observations entering the scientific statistic are generated after M3R4 is frozen. Historical exact-replay actor results are excluded from the gate.

No updater call is allowed.

## 5. Actor/runtime contract — unchanged plus explicit two-level inference qualification

For every logical actor unit:

- requested model: `deepseek-v4-pro`;
- required resolved model: `deepseek-v4-pro-ga-260813`;
- thinking disabled;
- temperature 0;
- K=1;
- max turns 10;
- max output tokens 8192;
- provider retry 0;
- same deterministic SpreadsheetBench verifier/runtime;
- fresh/reset runtime for every logical unit;
- no conversation/context carryover;
- no task-state cache reuse across replicates;
- no outcome-conditioned retry/replacement;
- logical-unit order fixed before execution and hash-interleaved across state/replicate/task;
- completed units never replayed.

M3R4 distinguishes **two separate stochastic qualifications**.

### 5.1 Within-task iid/stationarity qualification

For the squared-propensity interpretation and task-wise conditional state-label enumeration, assume that conditional on frozen state, task, resolved model, and runtime, the four actor calls for a task behave as iid/independent Bernoulli draws with stationary state-specific success probabilities.

Logs can support but cannot prove this model. Concrete shared-state/context/model/evaluator/provider coupling blocks the inferential label.

### 5.2 Cross-task conditional factorization qualification — new M3R4 repair

For the aggregate exact Binomial tail, additionally assume that **conditional on the fixed panel and each task's observed total-success count, the state-label allocation indicators for distinct informative tasks factorize/are conditionally independent across task blocks**.

Equivalently, among tasks with exactly two successes, the indicator

`Z_q = 1{the two successes occur within the same frozen state}`

must have conditional probability `1/3` task-wise and the joint conditional law over informative tasks must factorize as the product of the task-wise laws.

This assumption does **not** require:

- equal `p_A(q)` or `p_B(q)` across tasks;
- exchangeability of task identities;
- treating tasks as a population sample.

Arbitrary cross-task dependence, shared provider shocks, common hidden task/runtime state, batch-level caching, or other coupling that makes the `Z_q` indicators non-factorizing invalidates the Binomial aggregation.

Execution must record runtime/provider ordering and coupling diagnostics prospectively. If a concrete cross-task coupling violation is detected, classify `M3R4_CROSS_TASK_FACTORIZATION_BLOCKED`; do not promote the exact Binomial p-value and do not automatically rerun.

## 6. Observed excess-disagreement statistic — unchanged

For each task:

`D_X(q) = 1/4 * [ |A1-B1| + |A1-B2| + |A2-B1| + |A2-B2| ]`

`D_A(q) = 1/2 * [ |A1-A2| + |B1-B2| ]`

`E_REAL(q) = D_X(q) - D_A(q)`.

Aggregate:

`D_X = mean_q D_X(q)`

`D_A = mean_q D_A(q)`

`E_REAL = D_X - D_A`.

If the two state artifacts are byte-identical, define `E_REAL=0` and the localization gate fails. Their currently frozen SHAs are distinct.

Under the within-task iid/stationary Bernoulli model:

`E[E_REAL] = mean_q [p_A(q)-p_B(q)]^2`.

Without that model, `E_REAL` remains only an observed cross-state-minus-within-state disagreement statistic.

## 7. Exact one-sided conditional state-label test — repaired assumption boundary

For each task, condition on the total number of successes among `(A1,A2,B1,B2)`.

Under the task-wise equal-propensity null `p_A(q)=p_B(q)` and within-task iid Bernoulli model:

- totals 0, 1, 3, or 4 are conditionally uninformative for `E_REAL(q)`;
- with exactly two successes, all `C(4,2)=6` state-label allocations are equiprobable;
- 2/6 allocations put both successes in one state, giving `E_REAL(q)=1`;
- 4/6 split successes across states, giving `E_REAL(q)=-1/2`.

Let:

- `n_2` = number of tasks with exactly two successes;
- `X = sum_q Z_q` over those informative tasks.

Then **only if the cross-task conditional factorization qualification also holds**:

`X | n_2, {task totals} ~ Binomial(n_2, 1/3)`.

The exact one-sided p-value is

`p_exact = P[X_null >= X_observed | n_2, {task totals}]`.

No equal task probability or task exchangeability assumption is used. The Binomial law comes from task-wise `1/3` allocation probability plus conditional factorization across informative task blocks.

The numerical Binomial tail may be computed for audit continuity even if factorization is not qualified, but it is then **non-inferential** and cannot enter a PASS label.

## 8. Frozen M3R4 decision

### 8.1 Bounded localization PASS

Require all five conditions:

1. state SHA(FF_R1) != state SHA(FF_R2);
2. `E_REAL > 0`;
3. raw numerical `p_exact <= 0.05`;
4. within-task iid/stationarity qualification passes;
5. cross-task conditional factorization qualification passes.

Then classify:

`M3R4_SELECTED_CASE_STATE_REALIZATION_LOCALIZATION_PASS`.

Allowed claim:

> On this fixed selected development panel, two distinct persistent states produced from the same reconstructed evidence show prospective cross-state outcome disagreement exceeding within-state actor disagreement, with a one-sided exact conditional state-label result against equal state-specific actor success propensities under the frozen within-task iid/stationary and cross-task factorization assumptions.

This remains selected-case evidence only. It is not population generalization, not a variance-component estimate, and not proof that variance reduction causally mediates a compiler effect.

### 8.2 Positive observed excess but uncertainty gate fails

If `E_REAL > 0` but raw `p_exact > 0.05`:

`M3R4_OBSERVED_EXCESS_ONLY_NO_PROPENSITY_LOCALIZATION`.

### 8.3 Nonpositive observed excess

If `E_REAL <= 0`:

`ACTOR_NOISE_NOT_EXCLUDED / DOWNGRADE_STATE_REGENERATION_MECHANISM`.

### 8.4 Within-task iid/stationarity qualification fails

`M3R4_WITHIN_TASK_INFERENCE_ASSUMPTION_BLOCKED`.

Observed `E_REAL` may be archived descriptively. Squared-propensity and exact-test interpretations are not promoted.

### 8.5 Cross-task factorization qualification fails

`M3R4_CROSS_TASK_FACTORIZATION_BLOCKED`.

Observed `E_REAL` and task-wise conditional counts may be archived descriptively, but the Binomial p-value cannot be used as an exact inferential gate.

No blocked inference path grants an automatic rerun.

## 9. Historical context — descriptive only

Historical FF_HIST remeasurements, original exact-replay FF_R1/FF_R2 outcomes, WIN_COMMON identity/outcomes, and historical FF_R1>FF_R2 ordering remain already-consumed background evidence only. They do not enter M3R4 gate arithmetic or exact p-value.

## 10. Supersession and cost boundary

M3R4 supersedes M3R3 before any M3R3 provider execution.

Compared with M3R3:

- actor units: **72 -> 72**;
- updater calls: **0 -> 0**;
- new states: **0 -> 0**;
- task artifacts: **18 -> 18**;
- model/backbone: unchanged;
- E3/public benchmark: none;
- only change: explicit cross-task conditional factorization qualification is added to the exact Binomial inferential gate.

No M3R3 outcome exists. This is a reviewer-required pre-execution inference repair.

## 11. Authority

M3R4 grants zero authority for:

- provider calls;
- actor execution;
- updater calls;
- Recovery V3 modification;
- Bridge/M4 execution;
- Semantic-Transfer execution;
- E3;
- second backbone;
- public benchmark;
- paper promotion/submission.

Before execution, M3R4 still requires a content-addressed execution contract, unit-order manifest, runtime/preflight qualification, exactly-once provider budget, explicit measurement authorization, completion audit, and analysis authorization.
