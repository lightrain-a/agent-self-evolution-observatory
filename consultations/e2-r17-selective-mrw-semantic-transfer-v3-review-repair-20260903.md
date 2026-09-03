# E2-R17 Selective-MRW Semantic-Transfer V3 — Review Repair / Pre-F0

Date: 2026-09-03
Status: `PRE_F0_V3_ZERO_PROVIDER_DESIGN_ONLY`
Parent V2: `4894f4f5622d02c8515687f00e110dd57955c47f`
Independent review: `REVISE_BEFORE_STAGE_A`

## 0. Scientific lineage and supersession

The closed DeepSeek result remains immutable:

`HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS`.

Semantic-Transfer V2 observed **zero** Stage-A scientific pools and had no Stage-A execution authorization. V3 therefore supersedes V2 prospectively, before provider execution. V2 files, contracts, preflights, review-readiness artifacts, task materialization and all historical DeepSeek outcomes remain immutable provenance and are never rewritten or pooled into V3 inference.

V3 is a review-driven identification repair, not a result rescue. It makes four verdict-changing changes before any provider call:

1. genuinely cross semantic class within common task skeleton/templates;
2. remove hidden generator metadata from the deployable router;
3. move mechanism inference to independent matched-skeleton interactions and remove the invalid within-stream power claim;
4. fully specify MRW4 selection, update order and stochastic pairing semantics.

## 1. Scientific question

Search produces `T_K={tau_1,...,tau_K}`. Acting uses verifier-selected `a(T_K)`. Persistent learning uses evidence projection `g(T_K)`.

The state-level causal question is unchanged:

> Holding the exact search pool and acting decision fixed, can changing only the learner-visible projection change future persistent skill utility?

The V3 mechanism question is narrower and prospectively falsifiable:

> Within the same structural task skeleton, is rejected-witness learning relatively more useful when the task requires reusable multi-step transformation than when it requires instance-specific binding/localization?

The V3 method question is separate:

> Can a router using only information observable before the update select between WIN-C and MRW4 without privileged family/template/semantic metadata?

Phenomenon, causal intervention, mechanism and method are adjudicated separately. Failure of the mechanism or router cannot rewrite the state-level causal estimand.

## 2. Exact causal intervention

For every update task:

`S0 -> K=8 pool T_K -> deterministic verifier -> served winner a(T_K)`.

Acting is identical across learning arms.

### WIN-C

Updater-visible evidence is the served winner on all eight update pools.

### MRW4

A pool is `mixed` iff it contains at least one verifier-success trajectory and at least one verifier-failure trajectory.

For every mixed pool, define the candidate rejected witness as:

> the verifier-failure trajectory with the **lowest original rollout index** among trajectories that are not the served winner.

No score, later outcome, semantic label, family ID, error taxonomy or post-update information may enter this witness selector.

After all Stage-A pools are sealed, a stream is support-qualified only if at least four of its eight pools are mixed. For a qualified stream, choose exactly four treated pools by ascending

`SHA256("semantic-transfer-mrw4-v3|stream_id|task_id")`.

On those four pools, MRW4 exposes the frozen lowest-index failed nonwinner. On the other four pools, MRW4 exposes exactly the same winner evidence as WIN-C.

MRW4 is branch replacement, not `winner + failure`.

The final updater-visible evidence window is rendered to the same frozen token budget in both arms. Truncation side, renderer, serialization and system/user prompts are identical across arms.

## 3. Genuine crossed semantic construction

V3 uses **five independent matched skeletons**. Each skeleton has one common generator/template that can instantiate both semantic cells while preserving the same workbook topology, row-count schedule, distractor schedule, output locations and nuisance-profile grid.

Within each skeleton:

- `PROCEDURAL_TRANSFORMATION`: binding is unique/explicit; uncertainty is concentrated in an ordered reusable transformation sequence;
- `INSTANCE_BINDING_LOCALIZATION`: transformation is short/simple; uncertainty is concentrated in choosing the authoritative current object among multiple plausible bindings.

The semantic cell is therefore crossed *inside* the skeleton generator rather than implemented as two unrelated family generators.

Frozen skeleton set:

1. `cross_join_ledger`
2. `cross_measure_panel`
3. `cross_snapshot_bundle`
4. `cross_group_window`
5. `cross_lookup_reconcile`

Each skeleton has exactly two hidden experimental cell labels, procedural and binding. Those hidden labels are used only for blinded experimental stratification and confirmatory mechanism analysis.

## 4. New suite namespace and size

V3 uses a fresh b21-b23 namespace and a new suite root:

`/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-semantic-transfer-v3`

Frozen structure:

- update blocks: `b21`, `b22`;
- heldout block: `b23`;
- 5 independent crossed skeletons;
- 2 semantic cells/skeleton;
- 2 update streams/cell (one per update block);
- 20 update streams total;
- 8 update tasks/stream;
- 160 scientific update tasks;
- 2 heldout tasks/cell;
- 20 common heldout tasks total;
- all task IDs and all scientific XLSX hashes must have zero overlap with every prior E2-R17 suite, including V1/V2.

The suite builder may generate reserve instances for deterministic integrity checks, but reserves have zero replacement authority after any scientific pool is observed.

### Frozen generation runtime

The content-addressed XLSX suite is generated only under the runtime that produced the frozen bytes:

- implementation: `CPython`;
- Python: `3.12.3`;
- `openpyxl`: `3.1.5`;
- zlib compile/runtime: `1.3 / 1.3`.

This is a reproducibility constraint, not a scientific factor. XLSX ZIP bytes were observed to differ under Python 3.11 with zlib 1.2.13 despite the same `openpyxl` version. Therefore the V3 builder fails closed on runtime fingerprint drift, and the suite manifest plus zero-provider audit must record the exact fingerprint before any provider authority can be granted.

## 5. Observable router: no privileged metadata

The following are **forbidden router inputs**:

- `semantic_type`;
- `family_id` / family code;
- `matched_skeleton` / template ID;
- task ID or block ID;
- `reusable_transform_steps`;
- `binding_candidate_count`;
- hidden generator expected values;
- heldout outcomes;
- Stage-B updater or evaluation outcomes;
- any lookup table keyed by the above.

The deployable V3 router receives only a frozen `ObservableTaskView` available before persistent update:

1. the exact natural-language instruction shown to the actor;
2. the workbook's model-visible sheet names and header strings;
3. Stage-A search summaries that are already available before update, if and only if the feature is explicitly declared below.

### Frozen visible structural features

The zero-provider parser computes only from `ObservableTaskView`:

- `visible_operation_clause_count`: number of distinct ordered transformation clauses recognized from a fixed operation lexicon;
- `visible_binding_alternative_count`: number of distinct current/candidate/previous/legacy/forecast/estimate alternatives visible in the task instruction or schema;
- `visible_cross_sheet_reference_count`: number of explicitly referenced source sheets beyond Result.

The lexicon and parser implementation are content-addressed before Stage A. They may not contain family names, skeleton names or task IDs.

### Frozen automatic route

For a stream, aggregate the three features by median across its eight update tasks.

Route to MRW4 iff:

`median_visible_operation_clause_count >= 3`

and

`median_visible_binding_alternative_count <= 1`.

Route to WIN-C iff:

`median_visible_binding_alternative_count >= 2`

and

`median_visible_operation_clause_count <= 2`.

Any stream satisfying neither rule yields

`HOLD_V3_ROUTER_UNCLASSIFIED`

before Stage-B execution. There is no family/template fallback.

The hidden semantic label may be used to audit prospective router agreement, but agreement is an implementation qualification, not an input to the route.

## 6. Stage A — acquisition only

Requested model: `deepseek-v4-pro`.
Resolved identity must be exactly: `deepseek-v4-pro-ga-260813`.

Frozen acquisition:

- K=8;
- 160 update tasks;
- 160 pools;
- 1280 actor rollouts;
- zero updater calls;
- zero learned states;
- zero heldout evaluations;
- zero treatment-effect inference.

All 160 pools must be sealed and content-addressed before mixed-support inspection.

### Equal-dose support gate

Every one of the 20 streams must have at least four mixed pools. If any stream fails:

`HOLD_SEMANTIC_TRANSFER_V3_INSUFFICIENT_EQUAL_DOSE_SUPPORT`.

No task, stream, skeleton, semantic cell, model or K replacement is permitted after support inspection.

If all pass, freeze exactly four treated pools per stream using the V3 hash rule in Section 2. Total treated pools: `20 × 4 = 80`.

This changes the estimand to the support-qualified regime. V3 makes no unconditional claim outside streams satisfying this frozen positivity condition.

## 7. Stage B — paired learning

For each of 20 streams, execute both learning projections from the same S0 and exact Stage-A pools:

- WIN-C;
- MRW4.

Freeze `R=4` paired stochastic replicates per stream.

Total:

- 20 streams;
- 80 paired stream-replicate units;
- 160 learned states;
- 20 common K=1 heldout tasks/state;
- 3200 heldout evaluations.

R=4 is **measurement replication only**. It is not counted as semantic replication and carries no standalone power claim.

## 8. Update order and stochastic semantics

For stream `s`, replicate `r`, arm order is the ascending hash order of:

`SHA256("semantic-transfer-v3-update-order|s|r|arm")`.

Heldout arm evaluation order for task `q` is the ascending hash order of:

`SHA256("semantic-transfer-v3-eval-order|s|r|q|arm")`.

If the provider API exposes a reproducible seed field for the frozen updater path, both arms of a pair use the same frozen replicate seed:

`seed_sr = uint32(SHA256("semantic-transfer-v3-replicate-seed|s|r")[:8])`.

If the provider path does **not** expose a seed field, the protocol must record `provider_seed_control=false`; it may not claim common-random-number pairing. Pairing then means same S0, same pools, same prompt/configuration and contemporaneous hash-balanced execution under temperature-zero settings, with R=4 absorbing residual hosted stochasticity.

No retry may silently create an extra stochastic replicate.

## 9. Independent scientific units

For stream `s`:

`D_s = mean_r[J_s,r(MRW4)-J_s,r(WIN-C)]`.

For skeleton `h` and semantic cell `z`, average the two frozen stream effects in that cell:

`D_h,z = mean_{s in (h,z)} D_s`.

Primary mechanism interaction:

`I_h = D_h,PROCEDURAL - D_h,BINDING`.

The **five `I_h` values are the independent confirmatory mechanism units**.

The 20 stream effects are repeated within-skeleton cell measurements. The 80 paired replicates and 3200 heldout evaluations are not independent semantic units.

## 10. Primary mechanism gate

The preregistered mechanism claim is directional interaction, not two disconnected pooled family tests.

Require:

1. `mean_h I_h > 0`;
2. every one of the five independent skeleton interactions satisfies `I_h > 0`;
3. exact one-sided sign test over the five skeleton directions gives `p = 1/32 = 0.03125` under the all-positive outcome.

Zeros count as non-positive for this gate.

A skeleton bootstrap interval for the mean interaction is reported as descriptive uncertainty only; it does not create or rescue the exact gate.

Pass verdict:

`GO_V3_CROSSED_PROJECTION_INTERACTION_SUPPORTED`.

Otherwise:

`STOP_V3_SEMANTIC_INTERACTION_NOT_SUPPORTED`.

This gate supports only the frozen five-skeleton controlled interaction. It does not establish a universal semantic law.

## 11. Directional component and method diagnostics

After, and only after, the primary interaction gate is evaluated, report:

- `D_h,PROCEDURAL` for all five skeletons;
- `D_h,BINDING` for all five skeletons;
- automatic observable-router utility;
- always-WIN utility;
- universal-MRW4 utility;
- difficulty-only and mixedness-only router utilities derived from the already-frozen states.

### Method authority

A stronger automatic-method claim requires all of the following without changing the primary mechanism verdict:

1. router used only the frozen ObservableTaskView;
2. no stream was routed through hidden label/template fallback;
3. observable-router mean utility exceeds always-WIN;
4. observable-router mean utility exceeds universal-MRW4;
5. its advantage over each fixed policy is positive in all five skeletons.

If this method gate fails but the interaction gate passes, retain the mechanism result and do **not** claim an autonomous router.

If the semantic interaction fails but an empirical router comparison looks favorable, the router result is exploratory only and cannot rescue the mechanism claim.

## 12. Failure-trace diagnosticity alternative

The strongest preregistered alternative explanation is that rejected traces differ in diagnostic information content rather than semantic class itself.

V3 therefore records, without using them for routing or sample selection, zero-outcome descriptors of the chosen failed witness such as verifier-visible completed-subgoal count and binding-conflict count when these can be computed deterministically from the existing task/verifier state.

These descriptors are secondary mechanism diagnostics only. No threshold or subgroup may be selected from V3 outcomes. If they explain the pattern better than the hidden semantic interaction, the paper must prefer the diagnosticity interpretation in discussion and any subsequent experiment must be separately preregistered.

## 13. Power statement

V3 deliberately removes the V2 claim that pooled within-stream replicate SD establishes ~79% power for semantic generalization.

The design has the **minimum exact directional resolution** needed for a five-skeleton one-sided sign test to cross `.05`: all five positive gives `p=0.03125`.

R=4 is chosen only to reduce updater/hosted stochastic measurement noise at bounded cost. No 80% power claim is made for the interaction or method gate because no independent pre-outcome estimate of between-skeleton interaction variance exists.

## 14. Claim boundaries

If the primary interaction gate passes:

> Holding acting fixed, the effect of exposing rejected search evidence to persistent learning differs prospectively by task structure across five independently crossed spreadsheet skeletons: rejected-witness learning has a consistently larger future-skill effect in reusable-transformation cells than in binding/localization cells.

Only if the separate observable-router method gate also passes:

> A pre-update router using only task-visible information selects the learning projection better than either fixed projection policy on the frozen controlled suite.

Never claim from V3 alone:

- failures are generically beneficial;
- procedural-vs-binding is a universal law;
- hidden family/template labels are deployable method inputs;
- cross-backbone or public-benchmark generality;
- exact randomization inference from hosted model randomness;
- a power level unsupported by between-skeleton variation.

## 15. Fail-closed governance

- V2 is `SUPERSEDED_PRE_PROVIDER_BY_V3_REVIEW_REPAIR` and remains immutable;
- no old DeepSeek outcome enters V3 confirmatory statistics;
- no provider call before V3 suite/static/router/leakage/control-plane audit and independent review;
- all 20 streams retained regardless of Stage-B outcome;
- no reserve substitution after scientific acquisition starts;
- no b23 heldout access before learned states freeze;
- no partial Stage-B effect reads;
- no automatic provider retry;
- interrupted scientific execution requires separate outcome-blind resume adjudication;
- no second-backbone/public-benchmark rescue after a failed V3 gate;
- current document grants zero Stage-A authority.

## 16. Current authority

`PRE_F0_V3_ZERO_PROVIDER_DESIGN_ONLY`.

Allowed:

- V3 builder implementation;
- deterministic suite materialization;
- overlap/static/nuisance/router/leakage audits;
- tests and preflight code that perform zero provider I/O;
- independent design review.

Forbidden:

- Stage-A actor/provider calls;
- updater calls;
- learned-state construction;
- heldout evaluation;
- treatment-effect analyzer;
- paper claim promotion;
- second backbone/public benchmark/submission authority.
