# E2-R17 E3 — Family-Wise Prospective Prediction Proposal

Date: 2026-09-01
Status: **PRE_F0_PROPOSAL_ONLY / ZERO EXECUTION AUTHORITY**
Scientific object: `E2-R17-E3-FAMILY-WISE-PROSPECTIVE-PREDICTION-20260901`

## 1. Why E3 exists

DeepSeek V2 Repair2 Continuation V2 is complete and immutable at 48/48 paired units, 96/96 learned states, and 1728/1728 held-out measurements. Its frozen adjudication is:

`HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS`

The V2 result is valid. It must not be rescued by adding samples to the same confirmatory object, adding a second backbone, adding public benchmarks, changing the practical-null margin, deleting streams, or changing the primary statistic.

E3 is therefore **not a V2 extension** and is not an attempt to make the V2 p-value smaller. It asks a different question that was already specified in the pre-outcome theory correction dated 2026-08-28:

> Can heterogeneity in the effect of rejected-witness learning be predicted prospectively from pre-treatment mixed-pool support and a predeclared failure-family partition?

The pre-outcome theory defines

`Delta(K) = sum_z pi_z M_z(K) delta_z`

and explicitly proposes a future family-wise prospective test: estimate `delta_z` only on development/calibration streams, freeze the family prediction rule, and then predict effects on independent held-out confirmatory streams.

That pre-outcome statement is the scientific justification for E3. The observed V2 stream signs may motivate executing the already-defined E3 idea, but **they may not be used to choose which families, streams, thresholds, or prediction rule survive into confirmation**.

## 2. Frozen historical evidence boundary

E3 inherits the following only as immutable historical evidence:

- V2 closeout SHA-256: `f51e8267923ca2e50f70d6fbe931e01cebed470c6597160bca4d964ef7529d7a`
- V2 scientific adjudication SHA-256: `1a71d0c32536c65987dc960d1f1f4cf40a41127f3f9cfe30d3fe73295ce9268a`
- pre-outcome mixed-pool theory SHA-256: `9a45b28c33081a88e7453a9b3a608736e7b60e4ddcdde559d981321156a2f0db`
- V2 protocol SHA-256: `546981b691fda58a700d2b3c5af458eace92391810080d2b531c5ae111cf0300`

The V2 48 pairs remain V2 confirmatory evidence forever. If E3 later uses them for development/calibration, they must be relabeled **development only for E3** and can never enter E3 confirmatory statistics.

## 3. Scientific question

For a stream `s` belonging to a predeclared mutually exclusive failure family `z(s)`, define:

- `M_s(8)`: pre-treatment mixed-pool support at K=8, measured from the frozen search pools before any updater or held-out E3 outcome is generated;
- `delta_z`: family-specific diagnostic value of exposing one budget-matched rejected witness instead of the acting winner;
- `D_s`: held-out paired future-skill effect of MRW versus WIN-C.

The E3 prediction model at K=8 is:

`D_hat_s = M_s(8) * delta_hat_z(s)`.

The confirmatory question is not whether the grand mean is positive. It is:

> Does a family-conditioned prediction frozen on development data predict independent held-out stream effects better than a pooled, family-agnostic prediction?

This directly tests the family-wise mechanism already stated before V2 outcomes existed.

## 4. Predeclared family set

Keep **all six** controlled failure families already defined before V2 outcomes:

- `agj`
- `fmv`
- `ioc`
- `msp`
- `ska`
- `tsr`

No family may be dropped because its V2 effect was inconvenient.

Before any E3 outcome-bearing execution, a substrate audit must prove that these labels are mutually exclusive for the proposed E3 confirmatory streams. If they overlap, E3 must HOLD and define a new attribution scheme under a new version; it may not improvise after outcomes.

## 5. E3 stages

### Stage P0 — zero-outcome substrate sufficiency audit

No provider calls and no scientific outcomes.

Inventory candidate **new independent streams** for all six families and prove:

1. no E3 confirmatory stream duplicates any of the 12 V2 streams;
2. no E3 confirmatory held-out unit is reused from the V2 confirmatory sample;
3. family labels are defined from task construction / failure semantics, not V2 effects;
4. K=8 mixed-pool support can be measured before updater execution;
5. the same WIN-C/MRW projection semantics can be applied without changing updater, verifier, actor harness, prompt, or metric;
6. there is enough independent stream support to power a prediction-comparison test at the stream level;
7. no candidate is selected or rejected using E3 outcomes, which do not yet exist.

If independent confirmatory support is insufficient, stop at:

`PRE_F0_HOLD_E3_INSUFFICIENT_INDEPENDENT_STREAM_SUPPORT`

Do not recycle V2 confirmatory streams to fill the quota.

### Stage D0 — development/calibration only

Requires a separate explicit authorization that does **not** authorize confirmatory provider execution.

Permitted development source:

- the completed V2 sample, treated only as historical development data for E3.

D0 may estimate, for each predeclared family, a fixed `delta_hat_z` using only V2 development streams and their already-frozen pre-treatment mixed-pool support. It must also estimate a pooled `delta_hat_pool` using the same development data.

D0 must freeze before E3 confirmatory outcomes:

- the exact estimator for `delta_hat_z`;
- the pooled comparator estimator;
- handling of `M_s(8)=0` without deletion;
- all shrinkage / regularization, if any;
- prediction clipping, if any;
- the family partition;
- the confirmatory sample-size rule;
- the primary statistic and exact randomization/sign-flip rule;
- all secondary diagnostics.

No family-specific sign or magnitude may be manually edited after seeing D0 values.

D0 is calibration, not a new confirmatory claim.

### Stage C0 — new independent confirmatory prediction test

Requires a new frozen contract and independent review after P0 and D0.

For every new confirmatory stream `s`:

1. freeze stream identity and family before outcomes;
2. freeze / acquire its exact K=8 search pools;
3. compute `M_s(8)` before updater execution;
4. generate `D_hat_family_s = M_s(8) * delta_hat_z(s)` using the frozen D0 table;
5. generate `D_hat_pool_s = M_s(8) * delta_hat_pool` using the frozen pooled comparator;
6. freeze both predictions before any E3 held-out MRW/WIN-C outcome is read;
7. run the same paired WIN-C/MRW treatment semantics under the same primary DeepSeek family unless a new independently reviewed protocol explicitly changes the backbone;
8. compute the observed stream-level `D_s` only after all confirmatory streams are complete.

## 6. Proposed primary confirmatory estimand

For each independent E3 confirmatory stream, define squared prediction losses:

`L_family,s = (D_s - D_hat_family_s)^2`

`L_pool,s = (D_s - D_hat_pool_s)^2`

and improvement:

`G_s = L_pool,s - L_family,s`.

Primary estimand:

`G = mean_s G_s`.

Primary scientific claim:

> The pre-frozen family-conditioned mixed-support predictor generalizes better to new streams than the pre-frozen family-agnostic mixed-support predictor.

A later frozen C0 contract should use an exact one-sided stream-level sign-flip/randomization test on `G_s` with alpha fixed prospectively. Confirmatory streams, not probes or replicates, remain the independent units.

The exact test implementation and minimum independent-stream count must be frozen only after P0 establishes what independent substrate actually exists and D0 supplies development-only residual variance. No E3 confirmatory outcomes may exist at that point.

## 7. Secondary confirmatory quantities

Secondary only; they cannot rescue a failed primary prediction test:

- calibration error of `D_hat_family_s`;
- directional agreement between frozen prediction and `D_s`;
- family-wise held-out residuals;
- global held-out mean MRW-WIN-C effect;
- relation between `M_s(8)` and absolute treatment effect;
- runtime reliability and updater correction counts.

No post-hoc family deletion or regrouping.

## 8. Falsifiers

E3 is falsified / held if any of the following occurs under the future frozen contract:

- family-conditioned predictions do not outperform the pooled predictor on independent streams;
- prediction error is not materially lower under the prospectively frozen criterion;
- family labels cannot be made mutually exclusive without outcome-dependent decisions;
- new independent confirmatory streams are unavailable;
- the projection semantics cannot be kept identical to the V2 causal treatment;
- a new result requires changing the family set after outcomes;
- only V2 streams can be used, leaving no independent confirmatory sample.

A failed E3 must not be rescued by public benchmark execution or a second backbone.

## 9. Why this is scientifically cleaner than adding more V2 replicates

V2's independent unit is the stream (`n=12`); its four replicates reduce hosted nuisance but do not create new independent causal units. The completed V2 result has a positive but inconclusive grand mean and a wide stream-level interval. Adding more within-stream replicates after seeing that result would mainly chase precision inside the same 12 units and would violate the explicit V2 failure discipline if framed as a rescue.

E3 instead tests a pre-existing mechanistic prediction on **new independent streams**. Its primary target is out-of-sample prediction of heterogeneity, not retrospective significance of the V2 grand mean.

## 10. Authority at creation

This proposal grants **zero scientific execution authority**.

Specifically, it does not authorize:

- provider calls;
- new search-pool acquisition;
- updater execution;
- held-out evaluation;
- GPU use;
- analysis of V2 by family;
- D0 calibration;
- C0 confirmatory execution;
- a second backbone;
- public benchmark execution;
- paper promotion;
- submission.

The only allowed next action is **P0 zero-outcome substrate sufficiency auditing** and preparation of a separately reviewed D0/C0 design if P0 passes.

## 11. Current state

`E2-R17-E3-FAMILY-WISE-PROSPECTIVE-PREDICTION-20260901`

Current gate:

`PRE_F0_PROPOSAL_ONLY`

Execution authority:

`ZERO_AUTHORITY`
