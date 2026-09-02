# E2-R17 Selective-MRW Semantic-Transfer V1 — Pre-F0

Date: 2026-09-02

## 0. Scientific lineage

The closed DeepSeek Repair2 / Continuation V2 result remains immutable:

`HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS`.

The earlier same-family Selective-MRW V3 design reached only zero-provider static audit. It made zero provider calls and observed zero new TEST outcomes. It is superseded **before provider execution** because its TEST reused the same six failure-family identities as the discovery sample, leaving a family-ID lookup explanation unresolved.

Semantic-Transfer V1 is a new prospective child hypothesis. Old outcomes are discovery/calibration evidence only and can never be pooled with this child for confirmatory inference.

## 1. Paper question

Search produces a pool of candidate trajectories `T_K`. Current acting consumes a verifier-selected trajectory `a(T_K)`. Persistent learning consumes a possibly different evidence projection `g(T_K)`.

The paper asks:

> Is the branch worth serving necessarily the branch worth learning from, and can a pre-outcome structural rule determine when rejected evidence should replace winner evidence for persistent learning?

The child hypothesis is deliberately narrower than "failure trajectories help":

> Rejected evidence is more useful when it exposes a reusable transformation procedure, but not when it primarily exposes an instance-specific binding/localization choice.

This is a prospective hypothesis discovered from the closed sample and must transport to completely new failure-family identities to acquire authority.

## 2. Actual learning-projection data flow

For every update task:

`initial skill S0 -> K=8 search pool T_K -> deterministic verifier -> served winner a(T_K)`.

The acting channel is identical in all learning arms.

Learning arms are matched-budget branch projections:

- `WIN-C`: updater-visible evidence is the served winner;
- `MRW4`: on exactly four pre-frozen mixed pools per stream, updater-visible evidence is the deterministic failed nonwinner selected by the existing MRW rule; on every other pool, updater-visible evidence is the winner.

MRW4 is **not** `winner + failure`. It replaces the updater-visible winner branch on exactly four mixed pools while holding acting behavior fixed. The existing exact matched-window renderer must equalize final updater-visible token length for every paired evidence block.

Then:

`{g_WIN(T_K), g_MRW4(T_K)} -> same SkillEvolver -> frozen {S_WIN, S_MRW4} -> same unseen K=1 heldout panel`.

The only scientific treatment is which already-generated branch is shown to the updater on the four frozen mixed-pool positions.

## 3. Structural semantic rule — no old family lookup

The router is defined from two pre-outcome structural quantities:

- `reusable_transform_steps`: number of reusable state-transform operations required once bindings are explicit;
- `binding_candidate_count`: number of plausible instance-specific bindings among which the task must select.

Frozen routing rule:

- `PROCEDURAL_TRANSFORMATION` iff `reusable_transform_steps >= 2` and `binding_candidate_count == 1`;
- `INSTANCE_BINDING_LOCALIZATION` iff `binding_candidate_count >= 2` and `reusable_transform_steps <= 1`.

Selective-MRW policy:

- procedural -> use MRW4 learned state;
- binding/localization -> use WIN-C learned state.

The old six family IDs never occur in Semantic-Transfer TEST, so an old-family lookup table cannot route a TEST task.

## 4. Fully new TEST family identities with crossed structural skeletons

Use six new failure families arranged as three matched skeletons. No family occurred in the closed sample or same-family V3 TEST.

| matched skeleton | PROCEDURAL_TRANSFORMATION | INSTANCE_BINDING_LOCALIZATION |
|---|---|---|
| two-table join | `ordered_filter_rollup` | `foreign_key_binding` |
| single-table measure | `normalize_then_rank` | `header_source_binding` |
| snapshot table | `reconcile_then_aggregate` | `named_region_binding` |

Interpretation of the match:

- both sides operate on similar spreadsheet structures;
- procedural variants have explicit/unambiguous bindings and require multiple reusable transformation steps;
- binding variants have a simple post-binding computation but multiple plausible current/legacy/candidate binding choices;
- candidate key/column/region order is deterministically randomized to prevent a fixed-position shortcut.

This design changes failure-family identity while preserving the semantic distinction, so successful prediction is semantic transport rather than same-family replication.

## 5. Zero-provider semantic-transfer suite

Bound generator: `scripts/build_e2_r17_semantic_transfer_suite_v1.py`.

Output root:

`/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-semantic-transfer-v1`

Static shape:

- blocks b14/b15: update candidates;
- block b16: heldout candidates;
- 6 new families;
- 12 update streams, 2 per family;
- 8 update tasks per stream;
- 96 update tasks total;
- 18 common heldout tasks, 3 per family;
- 6 procedural streams and 6 binding streams;
- 4 streams per matched skeleton;
- old-suite task-ID overlap = 0;
- old-suite XLSX SHA-256 overlap = 0;
- provider calls = 0.

The heldout panel is never shown to the updater.

## 6. Stage A — search-pool acquisition and equal-dose qualification

Before any updater call:

- exact same DeepSeek identity is required: requested `deepseek-v4-pro`, resolved exactly `deepseek-v4-pro-ga-260813`;
- K = 8;
- 96 update tasks -> 96 K=8 pools -> 768 actor rollouts;
- no updater;
- no learned states;
- no heldout evaluation;
- no treatment-effect inference.

All pools are sealed and content-addressed before support inspection.

### Equal-dose support gate

Every one of the 12 streams must contain at least four mixed pools. If any stream has fewer than four, STOP with:

`HOLD_SEMANTIC_TRANSFER_INSUFFICIENT_EQUAL_DOSE_SUPPORT`.

No K/model/task/family replacement is allowed.

For every passing stream, choose exactly four mixed pools by the lowest SHA256 value of:

`semantic-transfer-mrw4-v1|stream_id|task_id`.

Freeze these 48 treated pool IDs before any Stage-B updater call.

Consequences:

- every stream receives exactly four MRW branch replacements;
- procedural and binding streams have identical treatment dose;
- extra mixed pools do not create extra MRW exposure;
- availability `M_z(K)` cannot by itself explain a semantic difference in Stage B.

Also require zero duplicate pool units, zero technical failures, and zero b16 heldout access.

## 7. Stage B — paired learning TEST

For each of the 12 new streams, run contemporaneous paired learning from the same initial skill and exact Stage-A pools:

- WIN-C;
- MRW4.

Freeze `R = 8` paired replicates per stream before any learning outcome.

Total Stage B:

- 12 streams;
- 8 paired replicates per stream;
- 96 paired units;
- 192 learned states;
- 18 common K=1 heldout tasks per state;
- 3456 heldout evaluations.

All arms share actor pools, acting winner, initial skill, updater implementation, provider identity, prompt, matched evidence tokens, verifier, heldout panel, K=1 evaluation, and decoding settings.

For stream `s`:

`D_s = mean_r [J_s,r(MRW4) - J_s,r(WIN-C)]`.

## 8. Selective-MRW is derived without a third execution arm

For procedural streams, Selective-MRW uses the already-created MRW4 learned state.

For binding streams, Selective-MRW uses the already-created WIN-C learned state.

Thus no third updater/evaluator arm is needed.

The selector must beat **both fixed policies** to earn a method claim.

### Gate A — procedural benefit over always-WIN

Use the six procedural stream effects `D_s`.

Require all:

1. mean procedural `D_s > 0`;
2. exact one-sided sign-flip test over the six procedural stream effects, alpha=.05;
3. paired-stream bootstrap 95% lower bound > 0.

Failure -> `STOP_NO_PROSPECTIVE_PROCEDURAL_MRW_BENEFIT`.

### Gate B — binding protection over universal MRW

Use the six binding stream effects with sign reversed, `-D_s`.

Require all:

1. mean binding `-D_s > 0` (WIN-C better than MRW4 in binding streams);
2. exact one-sided sign-flip test over the six binding stream effects, alpha=.05;
3. paired-stream bootstrap 95% lower bound > 0.

Failure after Gate A passes -> retain only procedural-MRW transport; **do not** claim a selective router beats universal MRW.

### Joint method verdict

Only if Gate A and Gate B both pass:

`GO_SELECTIVE_MRW_SEMANTIC_TRANSFER_SUPPORTED`.

Because the method claim requires both inequalities simultaneously, this is an intersection-union decision: both component tests must pass at alpha=.05. Neither component can rescue the other.

The joint claim is:

> On completely new failure-family identities and equal rejected-evidence dose, the frozen structural selector prospectively chooses the better learning projection: MRW4 for reusable procedural deficiencies and WIN-C for instance-binding deficiencies, outperforming both always-WIN and universal-MRW policies.

## 9. Secondary mechanism checks

Report without replacing the joint gates:

- stream-level effects for all 12 streams;
- per-family means;
- matched-skeleton procedural-minus-binding contrasts;
- global MRW4 vs WIN-C mean;
- Selective-MRW mean utility vs both fixed policies;
- failures and counterexamples retained.

Do not create family-specific significance claims from two streams/family.

The three matched skeletons are mechanism diagnostics, not independent confirmatory n for a 3-pair significance test.

## 10. Interpretation boundaries

If both gates pass:

- supported: semantic transport of the selective projection rule to unseen family identities under the controlled suite;
- supported: selection is not explainable by old-family lookup or unequal MRW dose;
- not yet supported: a production-ready classifier for arbitrary natural tasks;
- not yet supported: cross-backbone universality or public-benchmark generality.

If Gate A passes but Gate B fails:

- supported only: MRW4 benefits new procedural families;
- not supported: Selective-MRW beats universal MRW.

If Gate A fails:

- close this semantic-transfer child; do not add families/models/threshold changes as rescue.

## 11. Fail-closed execution rules

- closed 48-pair outcome remains HOLD and is never pooled into TEST inference;
- old six family IDs are forbidden from Semantic-Transfer scientific TEST;
- all 12 TEST streams are retained regardless of outcome;
- Stage-A mixedness may only determine equal-dose support and the predeclared four treated pool IDs;
- no b16 heldout task may be touched before learned states are frozen;
- no partial Stage-B treatment effect read;
- no automatic retry after provider/runtime failure;
- no second-backbone/public-benchmark rescue;
- no threshold/K/family modification after Stage A starts;
- full integrity audit precedes any analyzer.

## 12. Current authority

`PRE_F0_SEMANTIC_TRANSFER_ZERO_PROVIDER_ONLY`.

Allowed now:

- builder/static verification;
- deterministic regeneration check;
- old-suite disjointness audit;
- untouched-run-artifact audit;
- method/data-flow review;
- development-only current-provider identity qualification after static audit passes.

Not yet allowed:

- Stage-A 768 actor rollouts;
- Stage-B updater calls;
- heldout evaluation;
- analyzer;
- paper promotion;
- second backbone/public benchmark.
