# E2-R17 Prospective Heterogeneity — Pre-F0 V2

## Decision

V1 is blocked before provider execution because its prediction label varies at six-family level while the proposed permutation test treated 12 TEST streams as freely exchangeable labels. V2 repairs the scientific unit rather than weakening the threshold.

## Frozen scientific question

Can rejected-witness learning value be prospectively predicted across pre-outcome structural regimes, and does a CAL-derived diagnostic-value score predict untouched TEST effects better than evidence availability alone?

The closed DeepSeek result remains immutable: `HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS`.

## Prediction unit

Define the regime cell before any new outcome as:

`z = (primary_failure_family, procedure_depth_level)`

There are 6 deterministic failure families x 3 procedure-depth levels = 18 cells.

Procedure depth is taken directly from the original orthogonal L9 generator. Distractor level and schema ambiguity are not outcome-selected moderators; they remain balanced/nuisance factors within each cell.

## New fully disjoint substrate

Create a prospective suite extension with new task IDs only:

- blocks 7-12: prospective update candidates;
- block 13: prospective common heldout candidates.

No task ID, init workbook, golden workbook, update task, or heldout task may overlap the closed b0-b6 suite.

For every one of the 18 cells, blocks 7-12 expose 18 candidate update tasks (three L9 profiles at that depth in each of six blocks). Outcome-blind SHA selection partitions them into:

- 8 CAL update tasks;
- 8 TEST update tasks;
- 2 integrity reserve tasks.

Thus V2 has exactly:

- 18 CAL streams;
- 18 TEST streams;
- 8 tasks per stream;
- 18 new common heldout tasks (3 per failure family) selected from block 13;
- no old E1 or E3 task used as a scientific unit.

## Replication policy

Replicate count is not inferred from old effect signs/ranks. Variance-only planning from the closed sample shows pooled within-stream replicate SD about 0.1633; averaging two replicates leaves about 0.1155 SD from replicate noise, while four replicates leaves about 0.0816.

Therefore the default confirmatory design is `R=4` per stream unless a zero-outcome power audit proves a smaller R meets the frozen target. Replicate count must be frozen before CAL scientific execution and cannot be changed from CAL effect magnitude/sign.

At R=4 the full study would contain:

- 36 streams;
- 144 paired units;
- 288 learned states;
- 5184 heldout K=1 evaluations.

Execution is gated: CAL is completed and its prediction artifact frozen before TEST authority. If CAL prediction-support fails, TEST provider cost is zero.

## CAL prediction

For each CAL cell z, compute the mean stream effect over its frozen CAL stream replicates:

`C_z = mean_r [J(MRW)-J(WIN-C)]`.

Freeze all 18 continuous `C_z` values and their ranks. Do not drop or merge cells from their sign.

Also compute pre-treatment availability features from the exact CAL search pools, including at minimum mixed-pool fraction `M_z` using the same frozen K and pool semantics.

The strongest availability-only baseline receives the same CAL tranche but may use only availability variables. Its direction/orientation and any one-dimensional calibration mapping must be fitted on CAL and hash-frozen before TEST. It may not use failure-family identity, depth identity, witness text, or TEST outcomes.

## TEST primary endpoint

For every TEST cell z, compute one cell effect `T_z` by averaging its frozen TEST stream replicates.

Primary mechanism-prediction statistic:

`rho_diag = Spearman(C_z, T_z)` over all 18 cells.

Use a fixed-seed 100,000-label permutation test over the 18 TEST cell effects, with the 18 CAL scores frozen before any TEST outcome access. Primary prospective prediction requires:

1. `rho_diag > 0`;
2. one-sided permutation p <= .05;
3. 95% cell bootstrap lower bound for rho > 0;
4. all 18 cells retained;
5. protocol integrity PASS.

This does not turn the old global HOLD into GO. It establishes only prospective stability/predictability of regime-dependent learning value.

## Same-information simplification test

Let `rho_avail` be the TEST rank correlation produced by the CAL-fitted availability-only predictor.

Freeze a paired predictive comparison before TEST. The diagnostic-value mechanism is not promoted unless its TEST prediction improves over availability-only. At minimum report:

- `rho_diag - rho_avail`;
- paired absolute prediction error after CAL-only scale calibration;
- all cell-level failures.

If availability-only matches diagnostic prediction under the frozen comparison, downgrade to availability stratification; do not claim diagnostic-value mechanism.

## Secondary outputs

- TEST sign concordance between CAL and TEST cell effects;
- family-aggregated description only;
- depth-aggregated description only;
- no cell-specific p-values;
- no favorable subset selection;
- no post-hoc family x depth regrouping.

## Stop rules

- Any b0-b6 task/content overlap => PROTOCOL STOP before provider I/O.
- CAL support/precision inadequate under frozen gate => SUPPORT HOLD; no TEST.
- TEST prospective correlation fails => prospective heterogeneity thesis not established.
- Availability-only matches the diagnostic predictor => diagnostic-value interpretation removed.
- No second model/public benchmark may rescue a failed V2 prospective test.

## Current authority

`PRE_F0_V2_STATIC_CONSTRUCTION_ONLY`

Allowed now: static generator implementation, deterministic suite materialization, uniqueness/content-addressing checks, power/statistical-contract review, zero-provider preflight.

Forbidden now: actor/updater scientific calls, CAL outcomes, TEST outcomes, analyzer, second backbone, public benchmark, paper promotion.
