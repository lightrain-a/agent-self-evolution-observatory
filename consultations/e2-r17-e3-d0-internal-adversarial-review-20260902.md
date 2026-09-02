# E2-R17 E3 D0 — Internal Adversarial Pre-Outcome Review

Date: 2026-09-02
Status: **INTERNAL_REVIEW / NOT THE REQUIRED INDEPENDENT REVIEW**
Verdict: **HOLD_D0_DESIGN_REQUIRES_PREOUTCOME_REVISION**

This review is intentionally performed before D0 family coefficients, V2 family-wise mixed-support values, or D0 LOSO diagnostics are generated. It does not satisfy the project's separate independent-review requirement because the same research process prepared the design. Its purpose is to remove avoidable reviewer attack surfaces before requesting a genuinely independent verdict.

## 1. V2 result review

The completed V2 result remains scientifically valid and should not be reopened:

- 48/48 paired units;
- 96/96 learned states;
- 1728/1728 held-out measurements;
- outcome-blind completion audit passed before analyzer access;
- global result: `HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS`;
- no authority to rescue the V2 result by adding samples, models, public benchmarks, or changing thresholds.

The V2 HOLD is the correct frozen interpretation: positive global point estimate alone is insufficient for superiority, while the practical-null criterion also did not pass.

## 2. R1 — Scientific independence

**PASS.**

E3 is prospectively defensible because:

- the family-wise factorization and explicit E3 idea were written before V2 outcomes;
- all six families are retained;
- the original suite reserved the 12 E3 streams before V2 outcomes;
- V2 streams are development-only for E3;
- the E3 confirmatory task substrate is disjoint from V2 execution.

E3 must continue to be described as a new heterogeneity-prediction object, never as a V2 significance rescue.

## 3. R2 — Estimator fidelity

**HOLD — revision required.**

The current draft states that

`D_s ≈ m_s * delta_z`

is a direct stream-level consequence of the pre-outcome exact factorization.

That wording is too strong.

The exact pre-outcome factorization is defined for a mixed-gated intervention on a search pool. The V2 stream-level updater consumes evidence from eight pools and is a nonlinear learned update operator. Therefore the fraction of mixed pools in a stream does not mathematically imply that the final skill effect must be linear in that fraction.

Required revision:

- reserve `delta_z` for the theoretical latent diagnostic-value quantity;
- rename the D0 fitted coefficient to a predictive parameter, e.g. `beta_z`;
- state that `D_s ≈ m_s beta_z` is a **pre-frozen predictive working model motivated by**, but not identified by, the exact pool-level factorization;
- make C0 an out-of-sample test of this predictive model, not a direct estimator-validation claim for the theorem's `delta_z`.

This keeps the E3 idea scientifically useful while avoiding an invalid mechanism-identification claim.

## 4. R3 — Comparator validity

**PASS with the R2 reinterpretation.**

The pooled no-intercept slope is a clean primary comparator for the question:

> Does the predeclared failure-family label add predictive information beyond mixed-support alone?

No alternate comparator search should be allowed after D0 values are exposed.

A family-only predictor may be reported later as a secondary diagnostic if it is frozen before C0, but it must not replace the pooled mixed-support comparator as the primary baseline.

## 5. R4 — Development scarcity and bounded predictions

**HOLD — one deterministic repair required.**

Two development streams per family are deliberately sparse. That is acceptable only because the coefficients are development-only and judged on independent C0 streams.

However, the current draft forbids prediction clipping. This is not defensible under squared-error loss because the true stream effect is bounded:

`D_s in [-1, 1]`.

With two streams per family and potentially low mixed support, an unconstrained no-intercept slope can produce predictions outside the feasible outcome range. Under squared loss, projecting any prediction onto `[-1, 1]` cannot increase error for a true target in `[-1, 1]`.

Required revision:

- fit the same unregularized slope;
- apply the same deterministic feasibility projection to both predictors:
  - `D_hat_family = clip(m_s beta_hat_z, -1, 1)`;
  - `D_hat_pool = clip(m_s beta_hat_pool, -1, 1)`;
- do not tune the clipping interval; it is fixed by the mathematical endpoint support.

No ridge, shrinkage, family deletion, sign constraint, or hyperparameter tuning is authorized.

## 6. R5 — Zero-support rule

**PASS.**

The pooled fallback for a family with exactly zero development mixed support is conservative and non-selective.

The family must remain in C0 and cannot be dropped.

The deterministic `[-1,1]` feasibility projection from R4 is sufficient to control near-zero-support extrapolation without introducing a tuned support threshold.

## 7. R6 — Confirmatory independent unit

**PASS.**

The 12 pre-reserved E3 streams are the correct confirmatory independent units for the primary predictive comparison.

Tasks and stochastic replicates remain repeated measurements within stream and must not be promoted to independent units.

## 8. R7 — C0 continuation rule

**PASS only under Option A: unconditional reserved C0.**

D0 LOSO performance, coefficient signs, coefficient magnitudes, or apparent family separation must have zero authority over whether C0 runs.

Once D0 is mechanically complete and provenance-valid, all 12 pre-reserved E3 streams should enter C0, subject only to pre-execution integrity/resource gates.

This removes development-conditioned optional continuation.

D0 LOSO may remain diagnostic only and cannot trigger, cancel, resize, or redesign C0.

## 9. R8 — C0 inference rule

**HOLD — current exact sign-flip proposal should be rejected.**

The draft proposes an exact one-sided sign-flip test over the 12 stream-level squared-loss improvements `G_s`.

A sign-flip permutation test is exact only under an appropriate sign-exchangeability/symmetry null. Equal mean predictive loss by itself does not guarantee that the loss-difference signs are exchangeable, especially when the 12 streams are deliberately stratified across six different failure families and may be heteroskedastic.

Required replacement before D0 values are exposed:

### Primary finite-sample test

Define a stream-level win indicator:

`W_s = 1[L_family,s < L_pool,s]`.

Treat ties conservatively as non-wins.

Primary null:

`P(W_s = 1) <= 0.5`.

Use the exact one-sided binomial sign test over the 12 independent pre-reserved streams.

At alpha 0.05, with 12 streams, a PASS requires at least 10 family-predictor wins out of 12.

Also require:

`mean_s G_s > 0`.

This makes the confirmatory claim intentionally strong: family conditioning must improve prediction broadly across streams, not merely through one or two extreme squared-error reductions.

### Secondary effect-size analysis

Report:

- mean `G_s`;
- median `G_s`;
- family-predictor win count;
- paired stream bootstrap 95% CI for mean `G_s` with a frozen seed and replication count;
- pooled and family RMSE/MAE.

The bootstrap is effect-size uncertainty, not the exact primary p-value.

## 10. R9 — Practical effect criterion

**PASS with no additional arbitrary magnitude threshold.**

Do not invent a minimum MSE improvement from D0 values.

The combination of:

- exact majority-style generalization criterion (at least 10/12 wins for alpha 0.05), and
- positive mean loss improvement,

is already a stringent prospective requirement.

Effect magnitudes and confidence intervals must be reported even if the binary decision passes.

## 11. R10 — D0 execution boundary

**PASS.**

A future D0 authorization may only:

- read the already-complete V2 sample for development;
- compute pre-treatment `m_s` from existing frozen pool artifacts;
- compute the frozen family and pooled predictive coefficients;
- compute the frozen LOSO diagnostic;
- emit a content-addressed D0 prediction/calibration artifact.

It must not authorize provider calls, pool regeneration, E3 updater/evaluator execution, second backbone, public benchmark, paper promotion, or submission.

## 12. Additional blocker — held-out panel shift

**HOLD — interpretation revision required before D0.**

V2 development stream effects were measured on 18 common B4 held-out tasks. P0 proposes all 36 previously-unsplit B4 tasks for C0.

Metadata audit shows that both panels are family-balanced, but their profile/factor composition is not identical: the 36-task C0 set is the pre-existing complement of the 18-task V2 set inside the original 54-task B4 candidate universe.

This is not outcome leakage, but it changes the measurement panel.

Required revision:

- explicitly define C0 as **cross-stream plus cross-heldout-panel prospective generalization**;
- state that D0 coefficients are trained on one outcome-blind B4 panel and tested on its untouched complementary B4 panel;
- do not claim that C0 isolates family heterogeneity from held-out-profile shift;
- report the frozen V2-vs-C0 B4 profile/factor distributions in the C0 preregistration;
- keep all 36 complementary tasks; do not subsample after V2 outcomes to manufacture a closer match.

The relative family-vs-pooled prediction comparison remains valid because both predictors are evaluated on the exact same C0 panel, but the scientific interpretation must acknowledge the stronger cross-panel generalization target.

## 13. Final internal verdict

`HOLD_D0_DESIGN_REQUIRES_PREOUTCOME_REVISION`

Required repairs before requesting the genuine independent review:

1. replace causal-looking `delta_hat_z` with predictive `beta_hat_z` language;
2. add deterministic `[-1,1]` feasibility projection to both predictors;
3. select Option A unconditional all-12-stream C0;
4. replace the proposed exact sign-flip mean-loss test with the exact one-sided binomial stream-win test plus positive mean `G_s`;
5. explicitly preregister C0 as cross-heldout-panel generalization over all 36 untouched B4 tasks.

All five repairs can be made now without reading any D0 family coefficient, per-stream mixed-support value, or LOSO result.

After those revisions, the design should be sent for a genuinely independent pre-outcome review. This internal review does not itself authorize D0.
