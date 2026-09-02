# E2-R18 Diagnostic-Value Transport — Pre-F0 Design

## Parent boundary

R17 is complete and remains `HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS`.
R18 does **not** add samples to make the parent superiority test significant and cannot change the R17 verdict.
The parent complete result is used only as a calibration dataset for a new prospective question.

## New scientific question

Can family-conditioned reusable diagnostic value, calibrated on completed R17 data, prospectively predict the direction/ranking of MRW-vs-WIN-C learning-projection effects on untouched future streams?

The predictor is frozen as

`Rhat_z = M_z_future * delta_hat_z_R17`,

where `delta_hat_z_R17` is the already-observed R17 family effect and `M_z_future` is pre-treatment mixed-pool availability measured on future K=8 pools before any updater runs.

## Frozen calibration values

- aggregation_join: +0.04166666666666664
- formula_materialization: +0.09027777777777778
- input_output_contract: 0
- multi_step_pipeline: +0.09027777777777776
- schema_key_alignment: -0.06249999999999998
- target_sheet_range: -0.020833333333333315

These values are never refit after R18 Stage A begins.

## Untouched future substrate

R18 may reuse only the task assets/split from the old `e3_future_streams`, not any old E3 authority.
The split was selected outcome-blind before R17 outcomes and contains 12 single-family streams × 8 tasks = 96 tasks.
A zero-provider audit found 0 matching claims across 140 provider ledgers and 0 future-task execution directories.

## Fresh heldout evaluation

R18 does not reuse the R17 18-probe heldout set.
A new deterministic suite contains 54 fresh `r18-b7-*` tasks and freezes 18 common probes, 3 per family, by SHA selection.
The suite is bit-for-bit reproducible and the real MindMemOS SpreadsheetBench verifier scores all 18 golden workbooks as 1.0.

## Stage A — pre-treatment pool support

Run the frozen DeepSeek route at K=8 on the 96 untouched future update tasks only.
No updater or heldout evaluation is permitted.
For each stream, record `M_s = mixed_pool_count/8`; for each family, average the two stream values to `M_z_future`.
Then run the mechanical prediction-freeze script. It refuses to run if any updater/evaluation has already occurred.
If fewer than four distinct family `Rhat_z` values remain, stop before updater as predictor-support degeneracy.

## Stage B — prospective confirmatory transport

Only after Stage A prediction freeze and a separate authorization:

- arms: WIN-C and MRW
- 12 streams, 4 fresh replicate pairs per stream
- 48 paired units / 96 learned states
- 18 fresh common heldout probes per state, K=1
- 1728 heldout evaluations

Primary stream effect: `D_s = mean_r(J_MRW - J_WIN-C)`.
Primary family effect: mean of the two future stream effects in each family.

## Primary prediction test

Exact one-sided permutation test of Spearman correlation between the six frozen `Rhat_z` predictions and the six observed family effects, enumerating all `6!` family-label permutations.

GO requires:

- Spearman rho > 0
- exact one-sided p <= 0.05
- all six families retained
- prediction artifact frozen before first updater call

Sign accuracy, calibration slope, failed predictions, stream-level scatter, and pooled MRW-WIN-C effect are secondary only.

## Forbidden rescue paths

- no pooling R18 into R17 to re-test parent superiority
- no favorable-family subset as primary
- no family-specific significance claims
- no threshold tuning after future outcomes
- no second-backbone/public-benchmark rescue
- no old E3 contract/authorization reuse

If R18 prediction fails, the regime-law claim is not supported and R17 remains HOLD.
If R18 prediction passes, it supports a conditional prospective mechanism; a later selective-routing method would require a separate child and cannot be inferred retrospectively from R18.
