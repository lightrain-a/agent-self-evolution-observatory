# E2-R17 Selective-MRW Prospective V3 — Pre-F0

## 1. Scientific status inherited from the closed experiment

The completed DeepSeek Repair2 / Continuation V2 result remains immutable:

`HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS`

WIN-C = 683/864 = 79.05%, MRW = 703/864 = 81.37%, raw difference = +2.31pp, one-sided stream sign-flip p = 0.171875, 95% paired-stream bootstrap CI crosses zero, and practical equivalence is not established.

V3 is a **new prospective child hypothesis**. The closed 48-pair sample is calibration/development evidence only. It may motivate and parameterize V3, but it cannot be pooled with V3 TEST for a new confirmatory p-value and V3 cannot retrospectively convert the old HOLD into GO.

## 2. Calibration observation and frozen semantic taxonomy

The six controlled failure families were defined before the closed outcomes. After closeout, their CAL family effects are:

- aggregation_join: +0.0417
- formula_materialization: +0.0903
- multi_step_pipeline: +0.0903
- input_output_contract: 0.0000
- schema_key_alignment: -0.0625
- target_sheet_range: -0.0208

Freeze the following semantic grouping **before any E3 future pool or learning outcome is generated**:

### PROCEDURAL_TRANSFORMATION

- aggregation_join
- formula_materialization
- multi_step_pipeline

These families require reusable operation sequences / transformations across workbook instances.

### INSTANCE_BINDING_LOCALIZATION

- input_output_contract
- schema_key_alignment
- target_sheet_range

These families primarily identify which input/output key, schema element, sheet, or range should be bound for the current instance.

CAL descriptive contrast:

- procedural family mean = +0.07407
- binding/localization family mean = -0.02778
- contrast = +0.10185
- the three procedural CAL family means are all above the three binding/localization means (exact 3-vs-3 label-permutation probability 1/20 = 0.05).

This is **calibration**, not confirmatory evidence. The classification was frozen after seeing CAL outcomes and must therefore survive untouched TEST to acquire scientific authority.

## 3. Why the earlier family-rank V2 route is superseded

A sibling leave-one-stream-out check on the closed CAL sample uses one stream in each family to predict its sister stream, with mixed-pool availability scaling. It gives only approximately:

- Spearman rho = 0.316
- direction agreement = 6/12

Therefore the earlier continuous family-rank prediction is not internally stable enough to justify an expensive 18-cell CAL+TEST expansion. V3 tests the much simpler pre-frozen two-class semantic hypothesis instead.

## 4. Untouched TEST substrate

Use the original controlled suite's already-frozen `e3_future_streams`:

- 12 streams total;
- 2 streams per failure family;
- 8 update tasks per stream;
- all task IDs are in blocks b5/b6;
- historical run-artifact scan before V3 found zero `r17-b5-*` / `r17-b6-*` run files and zero b5/b6 trajectory refs.

These are the only update streams eligible for V3 TEST. No b0-b4 task may replace them after outcomes.

## 5. New heldout endpoint panel

Do not reuse the exposed b4 heldout panel for V3 TEST.

Use only the 18-task `common_heldout_probe` from the zero-provider prospective suite:

`/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-ph-v2`

Bound static suite artifacts:

- suite manifest SHA256: `2e04956e72dbc56fe029fa99eded91953c9775f10a3425f10a085d7d52497868`
- split manifest SHA256: `bbc24277c717f7499d9f9e30ccb254ad98229bcd61bd17e484310a8397fb2d46`
- metadata SHA256: `40cb56082903ed5ad2fb7ed6cf55b813c8fb80f3ec43e8535cb02af2d0953853`

The 18 heldout tasks are three per failure family and orthogonally cover procedure depth, distractor level, and schema ambiguity levels 0/1/2. They must never be fed to the updater.

## 6. Stage A — future search-pool acquisition only

Before any V3 updater call:

- exact same DeepSeek actor identity as the closed DeepSeek experiment is required: requested `deepseek-v4-pro`, required resolved `deepseek-v4-pro-ga-260813`;
- if that resolved identity is unavailable, V3 is HOLD_PROVIDER_IDENTITY; no model substitution;
- K = 8;
- 12 streams x 8 tasks = 96 pools;
- 96 x 8 = 768 actor rollouts;
- pool generation has no updater, no learned state, no heldout evaluation, no V3 treatment-effect inference.

All 96 pools must be frozen and content-addressed before support is inspected.

Support gate before Stage B:

1. at least 24/96 pools are mixed (contain both success and failure);
2. at least 8/12 streams have at least two mixed pools;
3. the three procedural families are all represented by at least one exposed stream;
4. no technical failure or duplicate pool unit;
5. no heldout b13 task touched.

Failure of this support gate is SUPPORT HOLD, not permission to change K, model, families, or task selection.

## 7. Stage B — paired future learning TEST

For each of the 12 sealed E3 streams, use the same frozen search pools to create contemporaneous paired arms:

- WIN-C: updater sees the winner only;
- MRW: updater sees the same winner plus the frozen mixed rejected witness under the existing MRW projection rule.

Everything else is held fixed: initial skill, stream tasks, pool hashes, acting winner, updater implementation, model, prompt, budget, heldout panel, K=1 evaluation, verifier, and decoding settings.

Freeze `R = 8` paired replicates per stream before any V3 learning outcome.

Total Stage B design:

- 12 streams;
- 8 replicates;
- 96 paired units;
- 192 learned states;
- 18 heldout K=1 tasks per state;
- 3456 heldout evaluations.

R=8 is chosen from variance-only planning using the closed experiment's pooled within-stream replicate SD (~0.1633). Under the CAL procedural effects as a planning reference, R=8 gives roughly 77% probability of satisfying the selective-policy sign-flip + positive-bootstrap gate, versus roughly 67% at R=6. This planning calculation grants no scientific claim and cannot be revised from V3 TEST outcomes.

## 8. Selective-MRW requires no third execution arm

Define the policy before V3 TEST:

- if stream family is PROCEDURAL_TRANSFORMATION -> use that stream's MRW learned state;
- if stream family is INSTANCE_BINDING_LOCALIZATION -> use that stream's WIN-C learned state.

Because every controlled stream is family-homogeneous, Selective-MRW is a deterministic composition of the two already-executed arms. It requires **zero additional updater calls and zero additional heldout evaluations**.

For stream s:

`D_s = mean_r [J_s,r(MRW) - J_s,r(WIN-C)]`.

Selective-MRW vs WIN-C stream effect:

`S_s = D_s` for procedural streams, and `S_s = 0` for binding/localization streams.

## 9. Confirmatory statistics

### Gate A — selective policy superiority

Across all 12 frozen TEST stream effects `S_s`:

- mean `S_s > 0`;
- exact one-sided sign-flip/randomization test, alpha = .05;
- 95% paired-stream bootstrap lower bound > 0;
- all 12 streams retained.

If Gate A fails: `STOP_SELECTIVE_MRW_NOT_PROSPECTIVELY_SUPPORTED`.

### Gate B — semantic interaction falsifier

Only if Gate A passes, aggregate the two TEST streams within each of the six failure families to get six family effects `F_z`.

Compute:

`H = mean(F_z | procedural) - mean(F_z | binding/localization)`.

Use the exact one-sided 3-vs-3 label permutation over all `C(6,3)=20` assignments. Because the sample is deliberately small, alpha=.05 requires the predeclared procedural grouping to achieve the strongest possible rank separation under this exact test. No stream-level pseudoreplication is allowed for this family-level semantic claim.

If Gate B fails while Gate A passes: report a prospective selective-policy improvement without claiming the procedural-vs-binding mechanism.

### Secondary comparison — Selective-MRW vs universal MRW

Report the stream-wise difference between Selective-MRW and universal MRW:

- procedural streams: 0 by construction;
- binding/localization streams: `-D_s`.

This is secondary unless a later pre-outcome multiplicity contract is separately frozen. It cannot replace Gate A or Gate B.

## 10. Fail-closed rules

- no old E1 outcome enters TEST inference;
- no b5/b6 TEST outcome is read before all paired endpoints complete;
- no task/family/replicate dropped by outcome;
- no Qwen/GPT/Kimi second-backbone rescue;
- no K/model/threshold change after Stage A support;
- no third execution arm for Selective-MRW;
- no reuse of the old b4 heldout panel;
- any provider/runtime failure is sealed and adjudicated separately without reading partial treatment effect;
- failed V3 closes this child hypothesis; it does not reopen the closed DeepSeek average-effect claim.

## 11. Current authority

`PRE_F0_SELECTIVE_MRW_V3_STATIC_ONLY`

Allowed now:

- static evidence audit;
- exact task/manifest binding;
- untouched-E3 proof;
- current-provider identity qualification with development-only units;
- zero-provider Stage-A preflight.

Not yet allowed:

- the 768 search-pool actor rollouts;
- any V3 updater call;
- any V3 heldout evaluation;
- analyzer;
- second backbone;
- public benchmark;
- paper promotion.
