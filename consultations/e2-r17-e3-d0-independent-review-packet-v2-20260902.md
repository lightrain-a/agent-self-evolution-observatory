# E2-R17 E3 D0 V2 — Genuine Independent Pre-Outcome Review Packet

Date: 2026-09-02
Status: **REVIEW_PACKET_V2_ONLY / NOT AN ADJUDICATION / ZERO EXECUTION AUTHORITY**

## Review target

Review only the revised frozen design:

- `consultations/e2-r17-e3-d0-development-design-v2-20260902.md`
- `generated/e2-r17-e3-d0-development-design-v2-20260902.json`

The original D0 draft remains preserved as history but is superseded for future review.

The preparing process performed an internal adversarial review and returned HOLD. That review is useful provenance but is **not** the independent verdict required by this gate.

Do not compute or request:

- per-stream V2 mixed-support values;
- family coefficients;
- family-wise V2 effects beyond the already frozen global V2 adjudication;
- LOSO D0 diagnostics.

The independent review must finish before those D0 values are exposed in a D0 artifact.

## Facts already frozen before D0 V2

1. V2 completed 48/48 paired units, 96/96 learned states, 1728/1728 held-out measurements.
2. V2 global verdict is `HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS`.
3. The pool-level family factorization and the idea of a future E3 family-wise prospective prediction test predate V2 outcomes.
4. The 2026-08-27 suite already reserved 12 E3 streams: six families x two streams x eight update tasks.
5. P0 identified 36 untouched B4 tasks, six per family, as the complete previously-unsplit complement of the 18-task V2 B4 panel.
6. All 264 task files needed for the 96 E3 update tasks plus 36 E3 held-out tasks match the original content-addressed suite manifest.
7. No historical E3 run exists.

## V2 repairs that the independent reviewer must verify

### A. Mechanism/prediction separation

V2 no longer claims the stream slope is the theoretical causal `delta_z`.

It defines a predictive working coefficient `beta_z`:

`D_s ≈ m_s * beta_z`.

Question: Is this a defensible prospective predictive model motivated by the pre-outcome family theory, provided the paper never treats `beta_z` as structurally identified `delta_z`?

### B. Feasible prediction projection

Both family and pooled predictions are deterministically projected to `[-1,1]`, the support of the stream-level treatment effect.

Question: Is this non-tuned projection acceptable and preferable to allowing impossible squared-loss predictions?

### C. Comparator

Primary comparator remains the pooled mixed-support model:

`D_hat_pool = clip(m_s * beta_hat_pool, -1, 1)`.

Question: Does this cleanly isolate the incremental predictive value of the predeclared family label beyond mixed support?

### D. Sparse development

There are exactly two V2 development streams per family.

Question: Is this acceptable because coefficients are development-only and C0 is independent/unconditional, while instability is allowed to hurt the family model honestly in C0?

### E. C0 continuation

D0 performance has zero continuation authority.

If D0 is mechanically valid, all 12 pre-reserved E3 streams proceed to separately authorized C0.

Question: Does this adequately remove development-conditioned optional continuation?

### F. Cross-heldout-panel target

C0 uses all 36 untouched B4 tasks, whereas D0 development effects came from the complementary 18-task B4 panel.

C0 is therefore explicitly defined as cross-stream plus cross-heldout-panel generalization.

Question: Is this interpretation scientifically acceptable if both predictors are evaluated on the same untouched C0 panel and no claim is made that C0 isolates family effects from held-out-profile shift?

### G. Primary finite-sample decision

For each of 12 C0 streams:

`G_s = L_pool,s - L_family,s`.

`W_s = 1[L_family,s < L_pool,s]`, with ties counted as non-wins.

Primary null:

`P(W_s=1) <= 0.5`.

Primary test:

- exact one-sided binomial sign test;
- alpha 0.05;
- fixed n=12;
- at least 10/12 wins required;
- additionally require `mean_s G_s > 0`.

Question: Is this finite-sample rule appropriately conservative and aligned with the claim of broad cross-stream predictive improvement?

### H. Secondary effect magnitude

Secondary only:

- mean/median `G_s`;
- win/tie/loss count;
- fixed paired-stream bootstrap 95% CI of mean `G_s`;
- MSE/RMSE/MAE;
- per-family descriptive summaries.

Question: Is it acceptable to omit an arbitrary minimum MSE-effect threshold while still requiring the exact stream-win test plus positive mean `G_s`?

### I. D0 authority boundary

A later D0 authorization may only read historical V2 development artifacts and compute the frozen support/coefficient/LOSO objects.

No provider calls, new search pools, E3 updater/evaluator execution, second backbone, public benchmark, paper promotion, or submission.

Question: Is this boundary sufficiently narrow?

## Required independent verdict

Return exactly one:

- `PASS_D0_V2_DESIGN_FOR_DEVELOPMENT_ONLY_AUTHORIZATION`
- `HOLD_D0_V2_REQUIRES_FURTHER_PREOUTCOME_REVISION`
- `STOP_E3_NOT_PROSPECTIVELY_IDENTIFIED`

A PASS must explicitly approve or reject items A-I and bind the exact hashes of:

- the D0 V2 markdown;
- the D0 V2 JSON;
- this V2 review packet;
- the E3 P0 substrate audit.

A PASS grants no C0 execution authority by itself. It only permits a separate D0 development-only authorization to be prepared.

## Current state

`D0_V2_DRAFT_AWAITING_GENUINE_INDEPENDENT_PREOUTCOME_REVIEW`
