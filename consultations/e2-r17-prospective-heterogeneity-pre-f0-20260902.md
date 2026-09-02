# E2-R17 Prospective Heterogeneity Study — Pre-F0 Design

Date: 2026-09-02

## 0. Scientific boundary inherited from the closed DeepSeek confirmatory study

The completed DeepSeek V2 Repair2 experiment is immutable and remains:

`HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS`

Observed complete-sample descriptive result:

- WIN-C: 683/864 = 0.7905
- MRW: 703/864 = 0.8137
- aggregate point estimate: +0.02315
- one-sided stream-level sign-flip p = 0.171875
- paired-stream bootstrap 95% CI = [-0.0185, +0.0660]
- practical equivalence under +/-1/18 not established

This study MUST NOT reinterpret that HOLD as GO, must not select favorable families from those outcomes, and must not use a second model/public benchmark as rescue.

## 1. New scientific question

The prior paper asked whether exposing a rejected witness to the persistent updater is globally better than winner-only learning.

The new question is narrower and more mechanistic:

> Can the sign and magnitude ordering of the learning value of rejected evidence be predicted prospectively across failure regimes, before the confirmatory outcomes of those regimes are observed?

The key distinction is:

- `M_z(K)`: availability of mixed/rejected evidence in regime/family z;
- `delta_z`: conditional future-skill value of exposing that evidence rather than winner-only evidence.

The existing theory already fixed the decomposition

`Delta(K) = sum_z pi_z M_z(K) delta_z`.

The new study does not assume `delta_z > 0` for every family. Positive, null, and negative families are all admissible scientific outcomes.

## 2. Why this is not a post-hoc rescue

The moderator object is not chosen from the exposed 48-pair outcome table. The following ingredients all predate outcome reveal:

1. six deterministic failure families;
2. exact mixed-pool support `M_z(K)`;
3. the theory object `delta_z`;
4. the requirement that family/regime prediction be prospective;
5. the rule that family-specific effects are not inferred from the old sample.

The old 48-pair sample may be cited only as motivation and cost/power information. It is not calibration data for the new prediction rule.

## 3. Frozen family universe

All six existing deterministic families remain in scope; none may be dropped based on the old outcome:

1. aggregation_join
2. formula_materialization
3. input_output_contract
4. multi_step_pipeline
5. schema_key_alignment
6. target_sheet_range

New task instances/streams must be disjoint from every task/update/heldout unit used in the closed study.

## 4. Cheapest design that preserves a real prospective test

Use 24 NEW streams, two replicates per stream:

- 12 CAL streams: 2 per family
- 12 TEST streams: 2 per family
- 2 replicates per stream
- 2 arms per replicate: WIN-C and MRW
- 18 frozen K=1 heldout tasks per learned state

Total new paired units:

`24 streams × 2 replicates = 48 pairs`

Total new learned states:

`48 pairs × 2 arms = 96 states`

Total new heldout evaluations:

`96 states × 18 = 1728 heldout`

Thus the full prospective study costs approximately the same number of updater states and heldout evaluations as the completed 48-pair experiment, but half the streams are explicitly consumed as calibration and half remain untouched confirmatory prediction targets.

The scientific confirmatory units are the 12 TEST stream effects. Replicates and probes remain repeated measurements, not independent n.

## 5. CAL phase

For CAL stream s and replicate r:

`d_sr = J_sr(MRW) - J_sr(WIN-C)`

For each CAL stream:

`D_s = mean_r d_sr`

For each family z with two CAL streams:

`delta_hat_z_CAL = mean(D_s in CAL family z)`

CAL is not a paper-effect confirmation. Its only role is to freeze a prospective family prediction for TEST.

### 5.1 Prediction classes

Use a mechanically frozen three-class prediction rule:

- POSITIVE if both CAL stream effects are > 0;
- NEGATIVE if both CAL stream effects are < 0;
- NULL/UNSTABLE otherwise.

No effect-size threshold is tuned from CAL. No family is removed.

Additionally freeze:

- continuous family score `delta_hat_z_CAL`;
- family rank by `delta_hat_z_CAL`;
- sign class above.

If fewer than two families are POSITIVE or fewer than two families are NONPOSITIVE (`NEGATIVE` or `NULL/UNSTABLE`), stop before TEST with `CAL_HOLD_NO_HETEROGENEITY_CONTRAST_SUPPORT`. This is a support stop, not evidence that heterogeneity is false.

## 6. TEST phase — primary prospective prediction

TEST is never opened before the CAL prediction artifact is hashed and frozen.

For each of the 12 TEST streams compute the same stream effect `D_s` from two fresh paired replicates.

### Primary contrast

Each TEST stream inherits its family’s frozen CAL class.

Define:

`H = mean(D_s | family predicted POSITIVE) - mean(D_s | family predicted NONPOSITIVE)`

Primary hypothesis:

`H > 0`.

Use an exact permutation/randomization test over the 12 TEST stream effects with prediction labels frozen before TEST outcome access. Preserve the number of POSITIVE-labelled TEST streams under permutation. Alpha = 0.05.

Primary GO requires all of:

1. CAL support gate passed;
2. `H > 0`;
3. exact one-sided permutation p <= 0.05;
4. paired/cluster bootstrap 95% lower bound for H > 0;
5. no provenance/integrity failure.

This is a heterogeneity-prediction claim, NOT a global MRW-superiority claim.

### Secondary prospective outputs

Predeclare and report without changing the primary decision:

- sign accuracy on TEST streams;
- Spearman rank correlation between frozen `delta_hat_z_CAL` and the six TEST family means;
- calibration plot of CAL family score vs TEST family mean;
- all failed predictions retained;
- global TEST MRW-vs-WIN-C mean reported descriptively only unless separately powered/preregistered.

No family-specific p-values.

## 7. Strong falsifiers

The prospective heterogeneity thesis fails or downgrades if:

1. CAL produces no usable sign-class separation;
2. frozen CAL labels do not discriminate TEST effects (`H <= 0` or primary p > .05 / CI crosses 0);
3. TEST rank/sign prediction is no better than chance-compatible behavior;
4. prediction success requires dropping negative families, changing thresholds, regrouping families, or changing tasks after outcomes;
5. a same-information simpler predictor using only `M_z(K)` matches the prospective discrimination, in which case the story reduces to evidence availability rather than diagnostic value;
6. effect appears only in an outcome-selected subset.

## 8. Same-information baseline

The simplest competing predictor is availability-only:

`score_z = M_z(K)`

It receives the same family labels and pre-outcome pool support but no CAL learning-effect outcomes.

The prospective CAL-derived predictor earns a mechanism claim only if it predicts TEST heterogeneity better than this availability-only baseline under a predeclared comparison. Otherwise the result is interpreted as evidence-availability stratification, not learned diagnostic-value prediction.

A second simple baseline is family identity only with no ordered score; it can capture fixed categorical heterogeneity but cannot claim a reusable diagnostic-value law.

## 9. Backbone and substrate policy

Primary recommendation for the first prospective test:

- keep the same DeepSeek model identity and updater/runtime if still reproducibly available;
- use a NEW experiment object and NEW disjoint streams;
- do not call this a continuation/retry of the closed Repair2 sample;
- do not use Qwen as a rescue backbone.

If the exact DeepSeek route is unavailable, STOP at realization qualification and separately design a new-backbone study; do not silently substitute models.

## 10. Execution economics

Target full design is intentionally capped at the same scientific scale as the completed study:

- 48 new paired units
- 96 new learned states
- 1728 new heldout evaluations

To minimize wasted provider cost, execution is sequentially gated:

1. zero-provider static generation/uniqueness check for all NEW streams;
2. actor/updater qualification on non-scientific smoke units;
3. CAL 24 pairs only;
4. freeze CAL prediction;
5. only if CAL support passes, authorize TEST 24 pairs;
6. full integrity audit;
7. exactly-once TEST analyzer.

If CAL support fails, TEST provider cost is zero.

## 11. Paper story if the new study passes

The paper should not say “rejected failures are generally better training data.”

The stronger and more accurate story becomes:

> Acting and learning projections have different objectives. Search creates nonwinner evidence, but the persistent-learning value of that evidence is regime-dependent. A calibration phase can prospectively identify which failure regimes benefit from rejected-witness exposure, and those frozen predictions transfer to untouched streams.

This converts the old aggregate-HOLD result from an embarrassment into a boundary condition that motivated a prospective, falsifiable heterogeneity claim — without rewriting the old result.

## 12. Current authority

Status: `PRE_F0_PROSPECTIVE_HETEROGENEITY_DESIGN_ONLY`

Authorized now:

- static design review;
- dataset/stream construction planning;
- zero-provider uniqueness/integrity checks;
- cost estimation;
- external/adversarial review of the design.

Not authorized now:

- CAL scientific execution;
- TEST scientific execution;
- provider calls;
- updater calls;
- second backbone;
- public benchmark;
- paper promotion;
- changing the closed DeepSeek HOLD.
