# E2-R17 E3 D0 — Development-Only Calibration Design Draft

Date: 2026-09-01
Status: **DRAFT_ZERO_AUTHORITY_AWAITING_INDEPENDENT_REVIEW**
Parent: `E2-R17-E3-FAMILY-WISE-PROSPECTIVE-PREDICTION-20260901`

## 1. Scope

D0 is a development/calibration analysis proposal only. It is not E3 confirmation and it does not authorize provider calls, updater execution, new search pools, held-out evaluation, or any new scientific trajectory.

The sole purpose of D0 is to convert the already-completed V2 sample into a **fixed prediction table** for a future, independent E3 confirmatory sample that was reserved before V2 outcomes existed.

P0 has established the structural substrate:

- 12 pre-reserved E3 update streams;
- six predeclared failure families, two streams per family;
- 96 update tasks;
- 36 previously-unsplit B4 tasks available in full as an independent E3 held-out set;
- zero historical run-name consumption;
- 264 task files verified against the original suite manifest;
- no E3 execution authority.

Statistical adequacy remains intentionally unresolved until D0 is independently reviewed and separately authorized.

## 2. Development data boundary

D0 may use only the completed DeepSeek V2 Repair2 sample as development data.

The 12 V2 streams are permanently development-only for E3:

- `e1-agj-00`, `e1-agj-01`
- `e1-fmv-00`, `e1-fmv-01`
- `e1-ioc-00`, `e1-ioc-01`
- `e1-msp-00`, `e1-msp-01`
- `e1-ska-00`, `e1-ska-01`
- `e1-tsr-00`, `e1-tsr-01`

Their V2 confirmatory meaning is unchanged: the global V2 result remains `HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS`.

D0 may not reinterpret V2 as a successful confirmatory family result.

## 3. Pre-treatment moderator

For each V2 development stream `s`, define:

`m_s = (# update pools in stream s that are mixed at K=8) / 8`.

A pool is mixed if the already-frozen exact K=8 pool contains at least one successful trajectory and at least one failed trajectory.

`m_s` is a **pre-treatment support variable**. It is determined entirely from the frozen search pool that existed before MRW/WIN-C skill updating and before held-out future-skill outcomes.

D0 must bind every `m_s` to the corresponding frozen pool manifest and content hashes. It may not regenerate pools or substitute tasks.

## 4. Development response

For each V2 development stream, use the already-frozen stream-level effect from the completed V2 adjudication:

`D_s = mean_r [ J_sr(MRW) - J_sr(WIN-C) ]`, with the same four replicates and 18 held-out probes already used by V2.

No probe-level or replicate-level pseudoreplication is permitted in D0 fitting.

## 5. Frozen family estimator

For each predeclared family `z`, with exactly two V2 development streams `S_z`, fit the no-intercept family slope:

`delta_hat_z = sum_{s in S_z} m_s D_s / sum_{s in S_z} m_s^2`.

This is the direct least-squares estimator under the prospective model:

`D_s ≈ m_s * delta_z`.

No intercept, ridge penalty, shrinkage, clipping, sign constraint, family deletion, outcome-based regrouping, or hyperparameter selection is allowed.

### Zero-support fallback

If `sum_{s in S_z} m_s^2 = 0`, `delta_z` is not identified from development data.

In that case:

- mark the family `DEVELOPMENT_UNIDENTIFIED_ZERO_SUPPORT`;
- do not invent a family coefficient;
- the future family-conditioned predictor for that family must fall back mechanically to the pooled coefficient defined below;
- the family remains in E3 confirmation and cannot be deleted.

## 6. Frozen pooled comparator

Fit one family-agnostic slope using all 12 development streams:

`delta_hat_pool = sum_s m_s D_s / sum_s m_s^2`.

Future pooled prediction:

`D_hat_pool,s = m_s * delta_hat_pool`.

Future family prediction:

`D_hat_family,s = m_s * delta_hat_z(s)`,

except for a development-unidentified zero-support family, where the family prediction equals the pooled prediction by the frozen fallback rule.

The pooled model is the only confirmatory comparator. D0 may not search over alternate baselines after seeing development values.

## 7. Frozen leave-one-stream-out diagnostic

D0 should compute a leave-one-stream-out (LOSO) development diagnostic strictly for design adequacy, not as a new scientific claim.

For each development stream `s`:

1. exclude `s`;
2. re-fit its family slope using only the other development stream in that family, applying the same zero-support fallback;
3. re-fit the pooled slope on the other 11 streams;
4. predict the held-out development stream from its pre-treatment `m_s`;
5. calculate:
   - `L_family,s = (D_s - D_hat_family,-s)^2`
   - `L_pool,s = (D_s - D_hat_pool,-s)^2`
   - `G_s = L_pool,s - L_family,s`.

The 12 `G_s` values are development-only diagnostics of whether the fixed family rule has plausible out-of-sample value relative to the pooled rule.

No family or stream may be removed based on LOSO performance.

## 8. Design-adequacy gate must be reviewed before D0 execution

This draft intentionally does **not** choose a numerical power or LOSO threshold after inspecting family-wise D0 values.

Before D0 is authorized, an independent review must freeze one of the following:

1. a prospective design-adequacy rule that maps the 12 LOSO `G_s` values and the fixed 12-stream E3 substrate to `C0_ELIGIBLE` or `HOLD`; or
2. a decision to run the already-reserved 12-stream C0 regardless of D0 apparent effect size, treating C0 as the definitive prospective test and accepting potentially low power.

The review must occur before D0 family coefficients, mixed-support values by family, or LOSO `G_s` values are generated in a D0 artifact.

This prevents a threshold from being selected after development performance is known.

## 9. Future C0 prediction freeze

If a later D0 adjudication permits C0, then before any E3 confirmatory held-out outcome is generated, the following must be frozen for all 12 E3 streams:

- stream identity;
- family;
- exact eight update-task identities;
- exact K=8 search-pool manifests;
- pre-treatment `m_s`;
- `delta_hat_pool`;
- six family coefficient statuses/values;
- `D_hat_pool,s`;
- `D_hat_family,s`;
- the full 36-task E3 held-out set;
- the C0 primary statistic and exact inference rule.

No E3 stream may be replaced for weak mixed support or inconvenient predicted sign.

## 10. Current authority

This D0 draft grants zero authority.

Not authorized:

- reading V2 effects by family for D0;
- computing `m_s` by V2 stream;
- generating family coefficients;
- generating LOSO diagnostics;
- provider calls;
- new pool acquisition;
- E3 updater execution;
- E3 held-out evaluation;
- second backbone;
- public benchmark;
- paper promotion;
- submission.

Current gate:

`D0_DRAFT_AWAITING_INDEPENDENT_PREOUTCOME_RULE_REVIEW`
