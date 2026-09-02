# E2-R17 Method / Data-Flow / Paper-Story Audit

Date: 2026-09-02
Scope: outcome-blind audit of the current Selective-MRW V3 before any V3 provider execution.

## Verdict

`REVISE_SEMANTIC_IDENTIFICATION_BEFORE_STAGE_A_PROVIDER_EXECUTION`

The core Search-Projection data flow is coherent and causally clean after correcting one prose bug, but the current Selective-MRW V3 does not yet identify the proposed `PROCEDURAL_TRANSFORMATION` versus `INSTANCE_BINDING_LOCALIZATION` semantic mechanism against the simpler same-information alternative of memorizing the six existing failure-family identities.

No V3 provider call has been made; no b5/b6 or b13 scientific outcome has been accessed. This is therefore a pre-outcome design audit, not a result-driven repair.

## 1. Correct frozen data flow

For each update task and frozen initial skill `S0`:

1. generate one K=8 search pool `T_K` from `S0`;
2. deterministic verifier scores the eight branches;
3. acting projection `a(T_K)` serves the same verifier-selected winner in every learning arm;
4. learning projection changes only the updater-visible branch:
   - `g_WIN(T_K) = winner`;
   - `g_MRW(T_K) = deterministic first failed nonwinner` on mixed pools, and `winner` otherwise;
5. WIN and MRW evidence are rendered with the exact matched-window renderer so the final updater-visible token budget is equal;
6. the same pinned SkillEvolver updates cloned copies of `S0` to produce `S_WIN` and `S_MRW`;
7. both learned skills are frozen;
8. both are evaluated at K=1 on the same unseen heldout panel that never enters the updater.

Thus the causal object is the updater observation kernel / learning projection, not acting compute, acting choice, extra evidence volume, or a third method call.

Important correction: MRW is a matched-budget **branch replacement**, not an additive `winner + failure` packet. The V3 prose was corrected before provider execution.

## 2. What the closed DeepSeek study established

The closed 48-pair DeepSeek study remains:

`HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS`

It provides calibration/development evidence only for V3:

- WIN-C 79.05%;
- universal MRW 81.37%;
- raw +2.31pp;
- stream-level superiority not established;
- practical equivalence not established;
- harm not established;
- substantial family/stream heterogeneity observed.

This result rejects the simple paper story `rejected failures are universally better learning evidence`.

## 3. Strongest coherent scientific story

The scientifically coherent story is:

1. Search and serving optimize immediate acting, whereas persistent learning optimizes future behavior.
2. Using the same winner-only projection for both channels is an unexamined design assumption.
3. Best-of-K selection creates an observation bottleneck: nonwinner evidence can disappear from the learning channel even though it already exists in the generated pool.
4. Censoring alone does not imply harm. The future learning effect factors into evidence availability and the updater-conditional reusable value of the censored evidence.
5. The complete DeepSeek causal test shows that a universal failed-witness replacement is not a stable global solution: the point estimate is positive but heterogeneous/inconclusive.
6. Therefore the next mechanistic question is not `should agents learn from failures?`, but `which generated evidence should cross the acting-learning boundary?`
7. A selective learning projection is justified only if a pre-outcome property of the evidence/task predicts future learning value on untouched data.

This keeps novelty away from the already-collided claim that failures can help learning. The residual object is the **decoupling of acting projection and learning projection, plus prospective identification of when the learning projection should differ from the acting projection**.

## 4. Critical remaining identification problem in current V3

The current V3 semantic taxonomy was formed on the exposed closed sample:

- procedural: aggregation_join, formula_materialization, multi_step_pipeline;
- binding/localization: input_output_contract, schema_key_alignment, target_sheet_range.

The grouping is semantically plausible: the first group is dominated by reusable transformation procedures, while the second is dominated by resolving concrete schema/sheet/range/input-output bindings. However, the current untouched V3 TEST uses **new instances from the same six family identities**.

Therefore a same-information baseline can implement:

`lookup(family_id) -> {MRW, WIN-C}`

and reproduce the Selective-MRW policy exactly, without using the proposed semantic abstraction at all.

Consequently:

- Gate A can establish that a precommitted six-family selective policy replicates on untouched instances;
- Gate B can establish that the frozen 3-vs-3 grouping separates the same six families on untouched instances;
- neither gate by itself proves that `procedural transformation vs instance binding/localization` is a reusable semantic moderator beyond those family identities.

This is the main paper-story risk.

## 5. Routing / deployability boundary

Current Selective-MRW also consumes a benchmark-native failure-family label. In a general deployed agent, that oracle label is not automatically available.

Therefore the current policy should be described as a **controlled mechanistic routing probe**, not yet a general-purpose deployable selector.

A method-level claim requires either:

- an explicit pre-outcome router from ordinary task/evidence features, frozen before TEST; or
- an out-of-family prospective test showing the semantic abstraction transports to failure families whose identities were never observed in calibration.

## 6. Recommended repair before expensive Stage A

Do not change the closed DeepSeek result and do not use a second backbone as rescue.

Preferred scientific repair: add **semantic transport** rather than more same-family replicates.

### Option A — cheapest, weaker

Keep current b5/b6 V3 unchanged and explicitly narrow the claim to:

> A family-precommitted selective learning projection replicates on untouched instances of the same six controlled families.

This can validate a policy but not a general semantic mechanism.

### Option B — recommended for paper mechanism

Before any new outcome, construct new controlled failure-family identities that instantiate the same two semantic classes, and reserve them entirely for confirmatory TEST. Calibration may use the original six family identities; TEST must contain family identities absent from calibration.

The critical comparison becomes semantic class versus family-identity lookup. Family-ID lookup has no defined prediction for unseen families; the frozen semantic rule does.

### Option C — strongest causal moderator test

Construct matched task skeletons where the dominant deficiency type is crossed while surface complexity is held fixed:

- procedural-transformation variant: concrete bindings are explicit; reusable operation sequence is the challenge;
- binding/localization variant: operation sequence is fixed/simple; resolving concrete instance referents is the challenge.

Then test the `projection x deficiency-type` interaction prospectively. This isolates the moderator more directly than grouping six heterogeneous families.

## 7. Paper claim ladder

If only the closed DeepSeek HOLD exists:

- claim the observation-bottleneck problem and unresolved heterogeneous learning consequence;
- do not claim MRW as an effective method.

If current same-family V3 Gate A passes but semantic transport is not added:

- claim a precommitted selective policy replicates within the six controlled families;
- describe procedural/binding interpretation as a calibrated hypothesis, not a general mechanism.

If an out-of-family or crossed semantic TEST passes:

- claim that the optimal learning projection depends prospectively on reusable evidence type;
- Selective-MRW becomes a mechanism-derived policy instance;
- still do not claim generic `failures help` novelty.

If a later ordinary-feature router also transports:

- a method-level deployment claim becomes credible.

## 8. Recommended paper narrative

Hook:

> The trajectory worth serving is not necessarily the trajectory worth learning from.

Formal object:

`search pool T_K -> acting projection a(T_K)` and independently `learning projection g(T_K)`.

Mechanism:

winner selection changes the updater-visible observation kernel; the consequence depends on both censoring availability and the reusable value of censored evidence.

Causal intervention:

same pool, same served winner, same initial state, same updater, same budget; change only `g(T_K)` and evaluate future frozen skill at K=1.

Empirical arc:

1. establish censoring/availability;
2. show universal MRW is positive but heterogeneous/inconclusive;
3. use that closed study only to formulate a selective hypothesis;
4. prospectively test whether a pre-outcome semantic moderator predicts when rejected evidence should replace winner evidence;
5. only after semantic transport passes, move to external/public transport and a second backbone.

## 9. Immediate gate

Current V3 provider identity qualification and Stage A execution should remain paused until the semantic-identification scope is explicitly chosen. Zero-provider design work is allowed; scientific provider execution is not recommended yet.
