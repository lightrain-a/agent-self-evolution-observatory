# E2-R17 M3R2 — exact-evidence frozen-state regeneration audit, commensurate metric repair

Status: **PROPOSAL_ONLY / ZERO_PROVIDER / NO_EXECUTION_AUTHORITY**

Base manuscript checkpoint: `acbaba5f0388832a6eb474e20fbfc73e01bb653d`.

M3R2 changes only the prospective primary localization statistic of the unused M3R proposal. It adds no state, task, actor replicate, provider call, model, benchmark, or E3 authority. The original M3R has never executed and grants no provider authority, so this repair is prospective rather than outcome-conditioned.

## 1. Scientific question

The scientific question is unchanged:

> Do the already-generated FF_R1 and FF_R2 persistent states, produced from reconstructed byte-identical learner-visible First-Fail evidence, induce behavioral separation beyond re-running the downstream actor on a frozen state?

The audit remains an outcome-selected development localization, not independent confirmation or a population variance-component estimate.

## 2. Frozen states — unchanged

- `FF_HIST`: `97e28b4862ed5817929fa6014eb1ba1401667875d80e03d18c0b54978a185252`
- `FF_R1`: `596bd30b49935d16f35d51e9eed36e19567332cd8a9104ae50d832f91ffdf04f`
- `FF_R2`: `fb5454a27faf8182ba1b0d722273c4377d4762815cd1898c3780cc8ff336615e`
- `WIN_COMMON`: `6df40f61707494793289aa95cc89f5ac99da9eb0aa062cf9ad0fbffd71c00649`

All state paths/receipts remain those in the superseded M3R proposal. No state synthesis is allowed.

## 3. Frozen task panel and actor contract — unchanged

Use the exact same 18 development held-out tasks and the same controlled-suite manifests as M3R.

Actor/runtime remains:

- requested model `deepseek-v4-pro`;
- required resolved model `deepseek-v4-pro-ga-260813`;
- thinking disabled;
- temperature 0;
- K=1;
- max turns 10;
- max output tokens 8192;
- provider retry 0;
- same deterministic SpreadsheetBench verifier/runtime;
- fresh/reset runtime for every state × task;
- hash-balanced frozen state order;
- no outcome-conditioned retry or extra replicate.

M3R2 additionally makes explicit that the original A1/B1 observations and new A2/B2 remeasurements are interpreted as exchangeable actor realizations only under the frozen resolved-model/runtime qualification. Any provider/model/evaluator identity drift that invalidates that assumption blocks the localization claim rather than being repaired by rerun.

## 4. Measurement budget — unchanged

Execute exactly one new contemporaneous actor remeasurement for every frozen state × task:

- 4 states × 18 tasks = **72 new actor units**.

No updater call is permitted. Historical and common-WIN measurements remain descriptive/localizing outputs; they do not create additional state draws.

## 5. Why M3R's `D_U-D_A` is superseded

M3R defined

`D_U = mean_q | mean(A1,A2) - mean(B1,B2) |`

and

`D_A = 0.5 * mean_q [ |A1-A2| + |B1-B2| ]`.

These quantities are not commensurate: `D_U` first averages two actor outcomes inside each state and then takes an absolute between-state difference, whereas `D_A` measures pairwise within-state actor disagreement. The subtraction therefore has an additional finite-realization shrinkage with no simple state-separation estimand.

No M3R outcome exists, so replacing this statistic cannot be outcome-driven.

## 6. Repaired primary localization statistic

For each task `q`:

- `A1(q)`: original actor result for `FF_R1`;
- `A2(q)`: new M3R2 frozen-state result for `FF_R1`;
- `B1(q)`: original actor result for `FF_R2`;
- `B2(q)`: new M3R2 frozen-state result for `FF_R2`.

Define cross-state disagreement

`D_X = 1/4 * mean_q [ |A1-B1| + |A1-B2| + |A2-B1| + |A2-B2| ]`

and within-state actor disagreement

`D_A = 1/2 * mean_q [ |A1-A2| + |B1-B2| ]`.

The repaired excess is

`E_REAL = D_X - D_A`.

For binary outcomes, under exchangeable conditional actor realizations with frozen-state success probabilities `p_A(q)` and `p_B(q)`, the expectation is exactly

`E[E_REAL] = mean_q [p_A(q)-p_B(q)]^2`.

Thus the two terms are pairwise-disagreement quantities on the same scale. The zero-provider unit test exhaustively verifies this identity for multiple Bernoulli parameter pairs.

If state SHA(`FF_R1`) == state SHA(`FF_R2`), define `E_REAL=0` exactly. The current frozen SHAs are distinct, but the alias rule prevents actor noise from manufacturing a state-realization contrast in any future reuse.

## 7. Frozen development gate

M3R2 supports the bounded localization only if

`E_REAL > 0`.

Because this is one outcome-selected development stream, no task-level or family-level majority is promoted to an independent scientific-unit count. The 18 task-level values and six family summaries are diagnostics only.

Also report without a separate claim gate:

- `D_X` and `D_A`;
- new-remeasurement utility for FF_HIST, FF_R1, FF_R2, WIN_COMMON;
- each First-Fail state minus contemporaneous WIN_COMMON;
- whether the new aggregate ordering FF_R1 > FF_R2 remains strict;
- task/family disagreement diagnostics;
- the superseded `D_U-D_A` only if needed for audit continuity, clearly labeled non-primary and non-authoritative.

## 8. Interpretation

### If `E_REAL > 0`

Supported claim:

> In this selected development case, two separately realized persistent states from reconstructed byte-identical evidence induce outcome-propensity variation beyond observed within-frozen-state actor disagreement under the frozen actor/runtime contract.

This strengthens the local regeneration-instability interpretation. It does not estimate a population variance component, prove that updater variance dominates actor variance generally, or establish that variance reduction causally mediates typed-compiler utility.

### If `E_REAL <= 0`

Classify:

`ACTOR_NOISE_NOT_EXCLUDED / DOWNGRADE_STATE_REGENERATION_MECHANISM`

The manuscript must drop any claim that the exact-evidence case demonstrates state-realization instability beyond actor disagreement. M2 manual semantics cannot rescue this claim. M4 may proceed only under its separately frozen complete-method eligibility and cannot use M3R2 failure as permission to redesign the generator.

## 9. Supersession boundary

M3R2 supersedes only the unused M3R primary statistic and its corresponding interpretation paragraphs.

Unchanged:

- four state identities;
- 18 tasks;
- 72 new actor units;
- actor/model/runtime/verifier settings;
- provider retry 0;
- no updater calls;
- common WIN comparator;
- outcome-selected development status;
- no E3/second-backbone/public-benchmark authority.

No scientific outcome was read to create this repair.

## 10. Authority

This document grants zero authority for provider calls, actor measurement, updater calls, Recovery V3 modification, M4 execution, Semantic-Transfer execution, E3, another backbone, public benchmark, paper promotion, or submission.

Future execution requires a separate content-addressed contract, zero-provider preflight, provider-budget authorization, exactly-once runner, completion audit, and analysis authorization.
