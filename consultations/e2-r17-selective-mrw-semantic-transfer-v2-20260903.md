# E2-R17 Selective-MRW Semantic-Transfer V2 — Pre-F0

Date: 2026-09-03

## 0. Scientific lineage

The closed DeepSeek Repair2 / Continuation V2 result remains immutable:

`HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS`.

Semantic-Transfer V1 and its Stage-A R2 control plane observed no Stage-A scientific pools and had no Stage-A execution authorization. V1 is superseded before provider execution for a prospective power-allocation repair: increase independent streams from 12 to 18 while reducing Stage-B replicates from 8 to 7. No V1 outcome is available to tune V2.

V2 is a new prospective child using a fully new b17–b20 task namespace. Old outcomes remain discovery/calibration evidence only and are never pooled into V2 confirmatory inference.

## 1. Paper question

Search produces a trajectory pool `T_K`. Current acting consumes a verifier-selected trajectory `a(T_K)`. Persistent learning consumes a possibly different evidence projection `g(T_K)`.

The paper asks:

> Is the branch worth serving necessarily the branch worth learning from, and can a pre-outcome structural rule determine when rejected evidence should replace winner evidence for persistent learning?

The prospective semantic hypothesis is:

> Rejected evidence is more useful when it exposes a reusable transformation procedure, while winner evidence is safer when the main uncertainty is an instance-specific binding/localization choice.

This is not a claim that failures are universally useful and not a production-ready classifier for arbitrary tasks.

## 2. Actual data flow

For every update task:

`initial skill S0 -> K=8 search pool T_K -> deterministic verifier -> served winner a(T_K)`.

The acting channel is identical in all learning arms.

Learning projections:

- `WIN-C`: updater-visible evidence is the served winner;
- `MRW4`: on exactly four hash-frozen mixed pools per stream, updater-visible evidence is the deterministic failed nonwinner selected by the existing MRW rule; on all other pools, updater-visible evidence is the winner.

MRW4 is a matched-budget branch replacement, not `winner + failure`. The frozen matched-window renderer must equalize final updater-visible token length across paired evidence blocks.

Then:

`{g_WIN(T_K), g_MRW4(T_K)} -> same SkillEvolver -> frozen {S_WIN, S_MRW4} -> same unseen K=1 heldout panel`.

The only scientific treatment is which already-generated branch is exposed to the persistent updater on the four frozen treated pool positions.

## 3. Structural semantic rule

The route is defined from two pre-outcome structural quantities:

- `reusable_transform_steps`;
- `binding_candidate_count`.

Frozen rule:

- `PROCEDURAL_TRANSFORMATION` iff `reusable_transform_steps >= 2` and `binding_candidate_count == 1`;
- `INSTANCE_BINDING_LOCALIZATION` iff `binding_candidate_count >= 2` and `reusable_transform_steps <= 1`.

Selective-MRW:

- procedural -> MRW4;
- binding/localization -> WIN-C.

The old six failure-family IDs do not occur in this child.

## 4. Six new families crossed by three matched skeletons

| matched skeleton | PROCEDURAL_TRANSFORMATION | INSTANCE_BINDING_LOCALIZATION |
|---|---|---|
| two-table join | `ordered_filter_rollup` | `foreign_key_binding` |
| single-table measure | `normalize_then_rank` | `header_source_binding` |
| snapshot table | `reconcile_then_aggregate` | `named_region_binding` |

The match is structural rather than lexical: both sides use comparable workbook organization, while procedural variants concentrate uncertainty in reusable operation sequences and binding variants concentrate uncertainty in choosing the current/authoritative object among plausible candidates.

Candidate key/column/region positions are deterministically randomized. Experiment-only semantic type, family code, skeleton label and task ID are not model-visible prompt text.

## 5. New V2 suite and independent scientific units

Suite root:

`/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-semantic-transfer-v2`

Static design:

- update blocks: b17, b18, b19;
- heldout block: b20;
- 6 families;
- 3 independent update streams per family;
- 18 update streams total;
- 8 update tasks per stream;
- 144 update tasks;
- 18 common heldout tasks, 3 per family;
- 9 procedural streams;
- 9 binding streams;
- 6 streams per matched skeleton;
- task-ID overlap with all prior suites = 0;
- XLSX SHA-256 overlap with all prior suites = 0.

The stream is the independent confirmatory unit. Replicates and heldout probes are repeated measurements.

## 6. Stage A — search-pool acquisition and equal-dose support

Before any updater call:

- requested model `deepseek-v4-pro`;
- resolved model must be exactly `deepseek-v4-pro-ga-260813`;
- K = 8;
- 144 update tasks -> 144 K=8 pools -> 1152 actor rollouts;
- no updater;
- no learned state;
- no heldout evaluation;
- no learning-effect inference.

All 144 pools are sealed and content-addressed before support is inspected.

### Equal-dose support gate

Every one of the 18 streams must have at least four mixed pools. If any stream has fewer than four:

`HOLD_SEMANTIC_TRANSFER_V2_INSUFFICIENT_EQUAL_DOSE_SUPPORT`.

No K/model/task/family replacement is allowed.

For every passing stream, choose exactly four mixed pools by the lowest SHA256 of:

`semantic-transfer-mrw4-v2|stream_id|task_id`.

Freeze the 72 treated pool IDs before any Stage-B updater call.

Thus every stream receives exactly four failure-branch replacements and four winner evidences. Extra mixed pools do not increase treatment dose.

Historical planning note only: the closed support sample averaged 6.5 mixed pools per eight-task stream. Under an iid reference with mixed probability 0.8125, the probability that all 18 streams have >=4 mixed pools is roughly 0.87. This is not an assumption and does not relax the all-stream support gate.

## 7. Stage-A-only reduction routers frozen before Stage B

These are same-information reduction baselines. They are computed only from Stage-A acting/search summaries and are hash-frozen before any updater outcome.

### Difficulty-only router

For stream `s`, compute:

`A_s = total successful rollouts / 64`.

Rank streams by increasing `A_s` (harder first), tie-breaking by SHA256(`semantic-transfer-difficulty-v2|stream_id`). Route exactly the lowest-success 9 streams to MRW4 and the other 9 to WIN-C.

### Mixedness-only router

For stream `s`, compute:

`M_s = number of mixed pools / 8`.

Rank streams by decreasing `M_s`, tie-breaking by SHA256(`semantic-transfer-mixedness-v2|stream_id`). Route exactly the highest-mixedness 9 streams to MRW4 and the other 9 to WIN-C.

These routers require zero additional updater calls and zero additional heldout evaluations because they deterministically compose the same WIN-C and MRW4 learned states.

They are reduction diagnostics, not alternate primary hypotheses. If a simpler router matches or exceeds the semantic router, semantic-specific mechanism claims must be downgraded.

## 8. Stage B — paired prospective learning TEST

For each of the 18 sealed streams, execute contemporaneous paired learning from the same initial skill and exact Stage-A pools:

- WIN-C;
- MRW4.

Freeze `R = 7` paired replicates per stream before any learning outcome.

Total Stage B:

- 18 streams;
- 7 paired replicates per stream;
- 126 paired units;
- 252 learned states;
- 18 common K=1 heldout tasks per state;
- 4536 heldout evaluations.

Everything except learning projection is matched: exact search pools, acting winner, initial skill, updater implementation, model identity, prompt, evidence-token budget, verifier, heldout panel, K=1 evaluation and decoding settings.

For stream `s`:

`D_s = mean_r [J_s,r(MRW4) - J_s,r(WIN-C)]`.

## 9. Why R=7

Planning uses only the closed experiment's pooled within-stream replicate SD (~0.1633), never V2 outcomes.

With nine independent streams per semantic group, a paired-t planning approximation gives roughly 79% one-sided power for a component effect of `1/18 ~= 5.56pp` at R=7. R=8 would raise component power only modestly while adding 18 paired units.

This design is explicitly cost-bounded. Because the final method claim requires two component gates to pass, V2 does not claim 80% joint power at the practical margin. A small binding-protection effect comparable to the closed descriptive value (~2.78pp) is expected to remain difficult to confirm; if so, the correct scientific outcome is a procedural-only result rather than relaxing the gate.

## 10. Primary confirmatory gates

### Gate A — procedural benefit over always-WIN

Use the nine procedural stream effects `D_s`.

Require all:

1. mean procedural `D_s > 0`;
2. exact one-sided sign-flip over all `2^9` stream sign assignments, alpha=.05;
3. paired-stream bootstrap 95% lower bound > 0.

Failure:

`STOP_NO_PROSPECTIVE_PROCEDURAL_MRW_BENEFIT`.

### Gate B — binding protection over universal MRW

Use the nine binding stream effects with sign reversed, `-D_s`.

Require all:

1. mean binding `-D_s > 0`;
2. exact one-sided sign-flip over all `2^9` stream sign assignments, alpha=.05;
3. paired-stream bootstrap 95% lower bound > 0.

If Gate A passes and Gate B fails, retain only the procedural-MRW transport claim. Do not claim the semantic selector beats universal MRW.

### Joint selector verdict

Only if both gates pass:

`GO_SELECTIVE_MRW_SEMANTIC_TRANSFER_V2_SUPPORTED`.

This is an intersection-union claim: both component inequalities must hold simultaneously. Neither component can rescue the other.

## 11. Matched-skeleton mechanism consistency

For each matched skeleton, compute the mean `D_s` over its three procedural streams and over its three binding streams.

Directional consistency criterion:

`mean(D_proc | skeleton) > mean(D_binding | skeleton)`

must hold for all three skeletons to support a skeleton-robust procedural-vs-binding mechanism interpretation.

No n=3 significance test is created. If a skeleton reverses while Gates A/B pass, retain the pooled selective-policy result but downgrade the semantic mechanism claim to substrate-specific pooled routing.

## 12. Reduction diagnostics after Stage B

Derive, without extra execution:

- Selective-MRW utility;
- always-WIN utility;
- universal-MRW4 utility;
- difficulty-only router utility;
- mixedness-only router utility.

For semantic-specific mechanism authority, require the semantic router point estimate to exceed both difficulty-only and mixedness-only routers. Report paired stream differences and bootstrap intervals as secondary diagnostics, without converting these reduction comparisons into additional primary alpha gates.

If a simpler router matches/exceeds the semantic router, the selective policy may still be empirically useful, but the paper must not attribute its advantage specifically to reusable-procedure vs binding semantics.

## 13. Heldout endpoint

All 252 learned states use the same 18-task common K=1 heldout panel. The primary endpoint remains full-panel future skill utility.

Semantic-matched heldout subsets may be reported only as secondary mechanism diagnostics. They cannot replace the common-panel primary endpoint or rescue a failed Gate A/B.

## 14. Claim boundaries

If both gates and mechanism-consistency/reduction checks support the story:

> Acting selection and learning projection should be decoupled. Under equal rejected-evidence dose and unseen family identities, reusable procedural deficiencies benefit from rejected-witness learning while instance-binding deficiencies are better protected by winner learning; a pre-frozen structural selector therefore outperforms both fixed projection policies on the controlled suite.

Still not supported:

- a universal law for arbitrary agent tasks;
- a production-ready online semantic classifier;
- cross-backbone universality;
- public-benchmark generality;
- the claim that failure trajectories are generically better learning data.

## 15. Fail-closed rules

- old outcomes are never pooled into V2 inference;
- V1 and its Stage-A R2 control plane remain preserved and superseded pre-provider;
- all 18 streams are retained regardless of Stage-B outcome;
- if any Stage-A stream has <4 mixed pools, the entire child HOLDS;
- no task/family/model/K replacement after support inspection;
- no b20 heldout access before learned states freeze;
- no partial Stage-B treatment-effect read;
- no automatic provider retry;
- any interrupted scientific execution requires separate resume adjudication and authorization;
- no second-backbone/public-benchmark rescue after a failed V2 confirmatory gate.

## 16. Current authority

`PRE_F0_SEMANTIC_TRANSFER_V2_STATIC_ONLY`.

Allowed now:

- zero-provider suite/static/leakage/power audits;
- current-provider identity qualification;
- zero-provider Stage-A actual-path preflight;
- independent pre-execution review.

Not yet allowed:

- 1152 Stage-A scientific actor rollouts;
- Stage-B updater execution;
- heldout evaluation;
- analyzer;
- second backbone;
- paper promotion.
