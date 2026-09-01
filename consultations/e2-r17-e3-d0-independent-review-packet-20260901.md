# E2-R17 E3 D0 — Independent Pre-Outcome Review Packet

Date: 2026-09-01
Status: **REVIEW_PACKET_ONLY / NOT AN ADJUDICATION / ZERO EXECUTION AUTHORITY**

## Review target

Review the frozen D0 development design:

- `consultations/e2-r17-e3-d0-development-design-draft-20260901.md`
- `generated/e2-r17-e3-d0-development-design-draft-20260901.json`

Do not compute or request D0 family coefficients, V2 family-wise effects, per-stream mixed-support values, or LOSO diagnostics while reviewing this packet.

The review must be completed **before** D0 exposes those development quantities.

## Historical facts the reviewer may use

The following are already public within the frozen research record and do not require family-wise D0 inspection:

1. V2 completed 48/48 paired units, 96/96 learned states, and 1728/1728 held-out measurements.
2. The V2 global verdict is `HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS`.
3. The pre-outcome theory, written before V2 outcomes, defines the family-wise mechanism `Delta(K)=sum_z pi_z M_z(K) delta_z` and explicitly proposes a future E3 development/confirmatory prediction test.
4. P0 proved that the original 2026-08-27 suite already reserved 12 independent E3 streams: six families x two streams, eight tasks per stream.
5. P0 also mechanically identified all 36 previously-unsplit B4 tasks as a balanced, zero-overlap E3 held-out candidate set, six tasks per family.
6. P0 verified 264 corresponding task files against the original content-addressed suite manifest and found no historical run-name consumption.

## Frozen D0 estimator under review

For V2 development stream `s`:

- `m_s = mixed_pool_count_at_K8 / 8`, measured only from its frozen pre-treatment search pools;
- `D_s` is the already-frozen V2 stream-level MRW-WIN-C effect.

For family `z`, with exactly two development streams:

`delta_hat_z = sum_{s in S_z}(m_s D_s) / sum_{s in S_z}(m_s^2)`.

Pooled comparator:

`delta_hat_pool = sum_s(m_s D_s) / sum_s(m_s^2)`.

No intercept, regularization, clipping, family deletion, regrouping, hyperparameter search, or manual sign editing is allowed.

If a family has zero development support, the family is retained and its future family-conditioned prediction mechanically falls back to the pooled coefficient.

## Frozen future C0 comparison

For a new E3 confirmatory stream `s`, predictions are frozen before confirmatory held-out outcomes:

- `D_hat_family,s = m_s * delta_hat_z(s)`;
- `D_hat_pool,s = m_s * delta_hat_pool`.

After all independent E3 confirmatory streams are complete:

- `L_family,s = (D_s - D_hat_family,s)^2`;
- `L_pool,s = (D_s - D_hat_pool,s)^2`;
- `G_s = L_pool,s - L_family,s`.

The proposed primary target is whether family-conditioned prediction improves out-of-sample prediction over the pooled comparator at the **stream level**.

## Required reviewer questions

The independent reviewer must answer every item below before any D0 coefficient or family-wise development quantity is generated.

### R1. Scientific independence

Is E3 genuinely a new prospective heterogeneity-prediction question rather than an outcome-conditioned attempt to rescue the V2 global mean?

Required evidence for PASS:

- the family factorization and E3 concept predate V2 outcomes;
- all six families are retained;
- V2 streams become development-only for E3;
- C0 uses only the pre-reserved independent E3 streams and new held-out tasks.

### R2. Estimator fidelity

Does the no-intercept estimator follow directly enough from the pre-outcome factorization `D_s ≈ m_s delta_z` to avoid post-hoc model search?

The reviewer should explicitly reject adding an intercept, regularizer, clipping, nonlinear transform, family merge, or tuned prior unless a new versioned proposal is created before D0 values are exposed.

### R3. Comparator validity

Is the pooled no-intercept slope an appropriate and sufficiently strong primary comparator for the exact scientific question "does failure-family information improve prediction beyond mixed-support alone"?

If not, the reviewer must specify a replacement **now**, before D0 runs. No later comparator search is permitted.

### R4. Development scarcity

With only two V2 development streams per family, is the family coefficient conceptually acceptable as a deliberately high-variance development estimate whose validity is judged only on independent C0 streams?

The reviewer must not mistake development coefficient stability for confirmatory evidence.

### R5. Zero-support rule

Is the frozen zero-support fallback to the pooled coefficient conservative and non-selective?

### R6. Confirmatory unit

Are the 12 new E3 streams, rather than their tasks/probes/replicates, the correct independent confirmatory units?

### R7. C0 continuation rule

Choose exactly one policy **before D0 values are exposed**:

#### Option A — recommended: unconditional reserved C0

If D0 is mechanically computable and all provenance checks pass, execute all 12 pre-reserved C0 streams regardless of apparent D0 LOSO performance or coefficient signs.

D0 LOSO remains diagnostic only and cannot prevent or trigger C0 based on apparent effect size.

Scientific advantage: this avoids development-conditioned optional continuation and preserves the strongest prospective interpretation.

Scientific cost: the fixed 12-stream C0 may have limited power, and a null result must be accepted.

#### Option B — pre-frozen adequacy gate

Freeze an explicit numerical D0 adequacy rule now, without seeing D0 family values, and allow C0 only if that rule passes.

If choosing Option B, the reviewer must define the exact threshold, statistic, tie behavior, and failure verdict in the review artifact. No threshold may be chosen later.

**Recommendation in this packet: Option A.** This is a design recommendation from the preparing agent, not an independent reviewer verdict.

### R8. C0 inference rule

Confirm whether the future primary inference should be an exact one-sided sign-flip test across the 12 independent `G_s` values at alpha 0.05.

If the reviewer rejects this, the replacement must be specified before D0 values are generated.

### R9. Practical effect criterion

Decide prospectively whether statistical superiority of family prediction over pooled prediction is sufficient, or whether C0 also needs a minimum practical improvement in mean squared prediction loss.

If a practical threshold is required, its exact numerical value/rationale must be frozen now. It cannot be calibrated from D0 LOSO performance after exposure.

### R10. Execution boundary

Confirm that D0 authorization, if later minted, may only:

- read the already-complete V2 sample for development;
- compute frozen pre-treatment `m_s` values from existing V2 pool artifacts;
- compute the frozen family/pooled coefficients;
- compute frozen LOSO development diagnostics;
- emit a D0 freeze artifact.

It must not authorize provider calls, new search pools, E3 updater execution, E3 held-out evaluation, second backbone, public benchmark, paper promotion, or submission.

## Suggested independent verdict schema

The reviewer should return one of:

- `PASS_D0_DESIGN_OPTION_A_UNCONDITIONAL_C0`
- `PASS_D0_DESIGN_OPTION_B_FROZEN_ADEQUACY_GATE`
- `HOLD_D0_DESIGN_REQUIRES_PREOUTCOME_REVISION`
- `STOP_E3_DESIGN_NOT_PROSPECTIVELY_IDENTIFIED`

A PASS must bind the exact SHA-256 of the D0 draft and this review packet, and must explicitly record the choices for R3, R7, R8, and R9.

## Current authority

This packet is not a review result and grants no authority.

Current state remains:

`D0_DRAFT_AWAITING_INDEPENDENT_PREOUTCOME_RULE_REVIEW`
