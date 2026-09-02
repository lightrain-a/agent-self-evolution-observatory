# E2-R17 E3 D0 — Development-Only Calibration Design V2

Date: 2026-09-02
Status: **DRAFT_V2_ZERO_AUTHORITY_AWAITING_GENUINE_INDEPENDENT_REVIEW**
Parent: `E2-R17-E3-FAMILY-WISE-PROSPECTIVE-PREDICTION-20260901`
Supersedes for future review: `e2-r17-e3-d0-development-design-draft-20260901`

## 1. Why V2 exists

The internal adversarial review of the original D0 draft returned:

`HOLD_D0_DESIGN_REQUIRES_PREOUTCOME_REVISION`.

No D0 family coefficient, V2 mixed-support-by-stream table, or LOSO development result was generated before this revision.

V2 repairs five pre-outcome issues:

1. separates the pool-level theoretical `delta_z` from the stream-level predictive coefficient;
2. adds deterministic endpoint-feasibility projection to both predictors;
3. freezes unconditional execution of all 12 pre-reserved C0 streams after mechanical D0 completion;
4. replaces the proposed exact sign-flip mean-loss test with a finite-sample exact stream-win test;
5. explicitly defines C0 as cross-stream plus cross-heldout-panel generalization.

## 2. Scientific interpretation boundary

The pre-outcome theory contains an exact mixed-gated pool-level factorization:

`Delta_K = M_K * delta_K`.

That factorization motivates family-conditioned prediction, but it does **not** identify a linear stream-level mechanism coefficient after a nonlinear updater consumes eight pool-derived evidence units.

Therefore D0 V2 reserves `delta_z` for the theoretical latent diagnostic-value quantity and introduces a separate predictive coefficient:

`beta_z`.

The D0 working model is:

`D_s ≈ m_s * beta_z(s)`.

This is a frozen predictive model motivated by the theory, not a claim that `beta_z` is an unbiased or structurally identified estimator of theoretical `delta_z`.

C0 tests whether this family-conditioned predictive model generalizes prospectively to untouched streams and an untouched held-out panel.

## 3. Development-only data boundary

D0 may use only the completed DeepSeek V2 Repair2 sample as development data.

Development streams:

- `e1-agj-00`, `e1-agj-01`
- `e1-fmv-00`, `e1-fmv-01`
- `e1-ioc-00`, `e1-ioc-01`
- `e1-msp-00`, `e1-msp-01`
- `e1-ska-00`, `e1-ska-01`
- `e1-tsr-00`, `e1-tsr-01`

They remain V2 confirmatory evidence with the immutable global verdict:

`HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS`.

For E3 they are development-only and can never enter C0 confirmatory statistics.

## 4. Pre-treatment support variable

For development or future confirmatory stream `s`:

`m_s = mixed_pool_count_at_K8 / 8`.

A pool is mixed if its frozen exact K=8 pool contains at least one success and at least one failure.

For D0 development streams, every `m_s` must be computed only from already-existing frozen V2 search-pool artifacts and bound to content hashes.

For C0 streams, every `m_s` must be frozen from its future exact K=8 search pools **before** any C0 updater or held-out outcome is generated.

No stream or task may be replaced because its `m_s` is low, high, or inconvenient.

## 5. Development response

For V2 development stream `s`:

`D_s = mean_r [J_sr(MRW) - J_sr(WIN-C)]`.

Use exactly the already-frozen four V2 replicates and V2 endpoint definition.

No task-level or replicate-level pseudoreplication is allowed in coefficient fitting.

## 6. Frozen predictive estimators

For family `z`, with exactly two V2 development streams `S_z`, fit the no-intercept predictive slope:

`beta_hat_z = sum_{s in S_z} m_s D_s / sum_{s in S_z} m_s^2`.

Pooled comparator:

`beta_hat_pool = sum_s m_s D_s / sum_s m_s^2`.

No intercept, ridge penalty, shrinkage, sign constraint, family deletion, family merge, nonlinear transform, or hyperparameter search is allowed.

### Zero-support fallback

If a family's development denominator is exactly zero:

`sum_{s in S_z} m_s^2 = 0`,

then mark the family:

`DEVELOPMENT_UNIDENTIFIED_ZERO_SUPPORT`.

The family remains in C0 and its future family-conditioned prediction mechanically uses the pooled coefficient.

No positive support threshold may be introduced after D0 values are observed.

## 7. Deterministic feasible-outcome projection

For every development diagnostic and every C0 frozen prediction, both models use the same deterministic endpoint projection:

`clip(x) = min(1, max(-1, x))`.

Family prediction:

`D_hat_family,s = clip(m_s * beta_hat_z(s))`.

Pooled prediction:

`D_hat_pool,s = clip(m_s * beta_hat_pool)`.

For a zero-support-unidentified family, `beta_hat_z(s)` is replaced by `beta_hat_pool` before applying the same projection.

The interval `[-1,1]` is not tuned: it is the mathematical support of the stream-level MRW-WIN-C success-rate difference. Under squared error, projecting a prediction to the feasible target interval cannot worsen its error for a target inside that interval.

## 8. D0 LOSO diagnostic

D0 may compute leave-one-stream-out development diagnostics after the estimators are frozen.

For each development stream `s`:

1. exclude `s`;
2. refit its family coefficient using the other development stream in the same family, with the exact zero-support rule;
3. refit the pooled coefficient on the other 11 streams;
4. apply the same `[-1,1]` prediction projection;
5. compute squared prediction losses and their difference.

These LOSO values are **diagnostic only**.

They have no authority to:

- cancel C0;
- trigger C0;
- resize C0;
- remove a family;
- remove a stream;
- change an estimator;
- change the inference rule.

## 9. C0 continuation policy — frozen Option A

After a future D0 authorization is validly executed, C0 eligibility is mechanical, not effect-conditioned.

If D0:

- passes provenance/integrity checks;
- successfully emits the frozen family/pooled prediction coefficients;
- preserves all six families;
- makes no unauthorized provider or E3 outcome calls;

then **all 12 pre-reserved E3 streams proceed to C0**, subject only to separate resource/runtime qualification and a new C0 execution authorization.

D0 coefficient signs, magnitudes, LOSO results, or apparent predictive quality cannot change this rule.

## 10. C0 held-out panel — explicit cross-panel generalization

V2 development `D_s` values were measured on 18 outcome-blind selected B4 held-out tasks.

P0 identified the complete untouched complement:

- 36 previously-unsplit B4 tasks;
- six tasks per failure family;
- zero overlap with V2 held-out tasks;
- all task files pre-existed in the 2026-08-27 content-addressed suite.

C0 uses **all 36** untouched tasks. No subsampling is permitted.

Therefore C0 is explicitly a:

> cross-stream **and cross-heldout-panel** prospective generalization test.

The 18-task V2 panel and 36-task C0 panel are complementary subsets of the same pre-outcome 54-task B4 candidate universe, but their profile/factor composition is not identical.

Consequences for interpretation:

- C0 tests whether the frozen family-conditioned predictor survives both new update streams and a new outcome panel;
- a C0 failure cannot be localized uniquely to family heterogeneity versus held-out-profile shift;
- the C0 preregistration must publish the frozen metadata distributions of both B4 panels;
- both family and pooled predictors are always evaluated on the exact same 36-task C0 panel.

## 11. C0 loss comparison

For confirmatory stream `s` after its outcome is validly completed:

`L_family,s = (D_s - D_hat_family,s)^2`

`L_pool,s = (D_s - D_hat_pool,s)^2`

`G_s = L_pool,s - L_family,s`.

Positive `G_s` means the family-conditioned predictor has lower squared prediction error on that stream.

## 12. Primary finite-sample C0 decision rule

Define:

`W_s = 1[L_family,s < L_pool,s]`.

A tie is conservatively counted as a non-win.

Primary null:

`P(W_s = 1) <= 0.5`.

Primary test:

- exact one-sided binomial sign test;
- fixed `n = 12` pre-reserved streams;
- `alpha = 0.05`;
- at least **10/12 family-predictor wins** are required for statistical PASS.

Additional directional requirement:

`mean_s G_s > 0`.

Confirmatory GO requires both:

1. exact binomial p-value <= 0.05; and
2. positive mean squared-loss improvement.

This intentionally demands broad cross-stream generalization instead of allowing one or two extreme squared-error reductions to dominate the conclusion.

## 13. Secondary C0 effect-size analyses

Freeze before C0 execution:

- mean `G_s`;
- median `G_s`;
- win/tie/loss counts;
- paired stream bootstrap 95% CI for mean `G_s`, with fixed seed and fixed bootstrap repetitions;
- family and pooled MSE;
- family and pooled RMSE;
- family and pooled MAE;
- per-family two-stream descriptive summaries.

These are secondary effect-size/uncertainty analyses and cannot rescue a failed primary exact stream-win test.

No additional arbitrary minimum MSE threshold is introduced.

## 14. C0 prediction freeze before outcomes

Before any C0 updater or held-out outcome is generated, a content-addressed C0 prediction-freeze object must bind all 12 streams to:

- stream identity;
- family label;
- exact eight update tasks;
- exact K=8 pool manifests;
- `m_s`;
- D0 V2 artifact hashes;
- `beta_hat_pool`;
- family coefficient status/value;
- clipped `D_hat_pool,s`;
- clipped `D_hat_family,s`;
- full 36-task held-out set;
- exact primary binomial decision rule;
- exact secondary bootstrap seed/repetitions;
- fixed treatment/runtime configuration.

No prediction may be changed after C0 outcomes begin.

## 15. D0 execution authority boundary

This V2 design draft grants zero execution authority.

A future separately minted D0 authorization, if independently approved, may only:

- read the already-complete V2 sample for E3 development;
- compute pre-treatment `m_s` from existing frozen V2 pool artifacts;
- compute the fixed `beta_hat_z` and `beta_hat_pool` coefficients;
- apply the fixed feasibility projection;
- compute diagnostic-only LOSO quantities;
- emit a content-addressed D0 freeze artifact.

It may not authorize:

- provider calls;
- new pool acquisition;
- E3 updater execution;
- E3 held-out evaluation;
- second backbone;
- public benchmark;
- paper promotion;
- submission.

## 16. Current gate

`D0_V2_DRAFT_AWAITING_GENUINE_INDEPENDENT_PREOUTCOME_REVIEW`
