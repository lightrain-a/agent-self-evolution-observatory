# E2-R17 — Lessons, Mechanism Diagnosis, and Next Experiment

Date: 2026-09-02
Status: **DEVELOPMENT STRATEGY / NO NEW SCIENTIFIC EXECUTION AUTHORITY**

## 1. What must be preserved from V2

The completed DeepSeek V2 Repair2 result is scientifically valid and immutable:

`HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS`

It is not a failed experiment. It establishes that replacing winner evidence with the deterministic first failed non-winner is **not a uniformly beneficial intervention** on the 12 controlled streams under the frozen MindMemOS updater and DeepSeek actor.

The result must remain in the paper even if a later repair works, because it identifies the boundary of the naive rejected-witness hypothesis.

## 2. Execution lessons to institutionalize

1. A dead runner does not create new continuation authority.
2. Scientific continuation requires a global lineage lease plus unit-level exactly-once protection.
3. HTTP 429 recovery must be logical-measurement scoped; never replay a completed pair or updater state.
4. Outcome embargo must remain closed until the full canonical sample is complete and integrity-audited.
5. Historical duplicate lineages remain permanently quarantined and are never averaged into the canonical sample.
6. A valid noisy endpoint is a scientific result; do not add samples/models/threshold changes to rescue significance inside the same confirmatory object.
7. Every new mechanism hypothesis discovered from completed outcomes must be labeled development/post-hoc and tested on a new prospective sample.

## 3. Scientific lessons from the completed sample

The reproducible development artifact is:

`generated/e2-r17-v2-posthoc-mechanism-development-analysis-20260902.json`

These are **exploratory development diagnostics**, not confirmatory claims.

### 3.1 Availability is not utility

Across the 12 streams, pre-treatment mixed-pool fraction has essentially no linear association with V2 stream effect:

`r(mixed_pool_fraction, D_s) ≈ -0.091`

All 12 streams had sufficient mixed support; total mixed-pool support was 78/96. Yet the stream effects ranged from clearly negative to strongly positive.

Therefore the next experiment should not spend its main budget asking whether failed evidence is merely available. That mechanism has already been separated from behavioral utility.

### 3.2 Failure-family label is too coarse

Exploratory same-family transfer is not stronger than off-family transfer:

- mean same-family held-out effect: `0.0000`
- mean off-family held-out effect: `+0.02778`
- mean same-minus-off contrast: `-0.02778`

With only two update streams per family this is not a definitive null, but it is enough to reject the strategy of making family identity the primary next mechanism without a stronger intermediate variable.

Family remains useful as a blocking/coverage factor, not as the leading causal explanation.

### 3.3 Diagnostic quality of the selected failure is a stronger candidate mechanism

The current MRW rule selects the **first failed non-winner** from a mixed pool. This is deterministic and clean, but it does not ask whether the failure is informative.

Post-hoc structural diagnostics show that streams where the selected failed trajectory progressed closer to the winner tended to have more positive V2 effects.

Examples of coarse progress/proximity associations:

- correlation between selected failure-minus-winner provider-call gap and V2 effect: `r ≈ +0.542`
- correlation between selected failure-minus-winner tool-call gap and V2 effect: `r ≈ +0.583`
- correlation between selected failure/winner evidence-length proximity and V2 effect is positive in the same direction

Splitting the 12 streams by the selected-failure/winner evidence-length ratio for a descriptive check:

- lower six progress-proximity streams: mean V2 effect `≈ -0.0139`
- upper six progress-proximity streams: mean V2 effect `≈ +0.0602`

These numbers are post-hoc and small-n. They justify a new hypothesis; they do not validate it.

### 3.4 The failure can change the skill in the wrong way

Inspection of the evolved skills shows a qualitative difference between useful and harmful updates.

Positive examples such as FMV/MSP often add general procedural guidance such as completing the full Inspect → Compute/Transform → Write → Verify cycle and not stopping after inspection.

A negative SKA example instead compressed/reframed an existing verification section. This illustrates a plausible failure mode: a weak or premature rejected witness can cause the updater to allocate context capacity to an over-specific or distorted lesson rather than a transferable repair.

Thus the bottleneck is likely not "can the updater see a failure?" but:

> **does the selected failure expose a causally local, transferable divergence from a successful trajectory?**

## 4. Mechanism reinterpretation

The useful causal chain should now be written as:

`search pool contains failures`

→ `a diagnostic failure is identifiable`

→ `the failure is sufficiently close to a successful route to expose a local divergence`

→ `the updater can convert that divergence into a transferable skill change`

→ `future held-out utility improves`.

V2 tested only a weak proxy for the middle of this chain: "first failed non-winner".

The next experiment should intervene directly on **diagnosticity / counterfactual proximity** and then on **success-reference availability**.

## 5. How previous experiments remain useful

### Reusable as development evidence

- all 48 V2 paired units and 96 evolved states;
- per-stream and per-replicate V2 effects;
- exact frozen K=8 pools and all 96 pool trajectories;
- V1 identical-treatment nuisance variation for planning;
- updater reliability/correction rates;
- skill-post artifacts for patch-level qualitative and structural diagnostics;
- the 12 V2 streams for new development-only method pilots.

### Reusable as untouched confirmatory substrate

The pre-reserved E3 future substrate remains valuable because it predates V2 outcomes:

- 12 future streams;
- six families × two streams;
- 96 update tasks;
- 36 previously-unsplit B4 held-out tasks;
- zero historical consumption.

This should be preserved for the final confirmatory test of whichever mechanism repair survives development.

### Not reusable as new confirmation

The 12 V2 streams and their 18-task panel cannot become confirmatory evidence for a method chosen using V2 diagnostics. They are development-only for the repaired method.

## 6. Recommended next scientific object

Create a new object rather than extending V2 or the family-prediction E3 object:

`E2-R17-DIAGNOSTIC-WITNESS-REPAIR`

Central hypothesis:

> A rejected trajectory improves self-evolution only when it is a counterfactually proximal, diagnostically useful failure; pairing that failure with the successful anchor may further improve the updater's ability to distill the local repair.

The experiment is designed so that every arm answers a mechanism question even if no final method wins.

## 7. Stage M0 — completed existing-data mechanism analysis

No provider calls.

Status: completed as exploratory development analysis.

Main finding used only to motivate the next intervention:

- mixed availability alone is weak;
- family transfer is not clearly privileged;
- failure/winner progress proximity is a more promising moderator.

## 8. Stage M1 — four-arm prospective mechanism pilot on development streams

Use V2 streams only as development substrate. Do not use the untouched E3 future streams yet.

### Stream selection

Use six of the 12 V2 streams, exactly one per failure family, selected by a deterministic SHA ordering of stream IDs fixed before new M1 outcomes.

The other six V2 streams remain an internal development-validation tranche.

### Replication

Two fresh contemporaneous replicates per selected stream.

### Arms

#### A0 — WIN-C

Matched-window acting-winner evidence. Fresh contemporaneous baseline.

#### A1 — FIRST-FAIL

Exact historical MRW rule: first failed non-winner on mixed pools, WIN-C on non-mixed pools.

Purpose: reproduce the naive rejected-witness mechanism contemporaneously.

#### A2 — PROXIMAL-FAIL

On a mixed pool, choose the failed trajectory most counterfactually proximal to the acting winner using a **fully deterministic pre-treatment selector**.

Recommended selector, with no learned threshold:

1. maximize longest common prefix of normalized tool-call function-name sequence with the winner;
2. tie-break by minimizing absolute total tool-call-count difference from the winner;
3. tie-break by minimizing absolute provider-call-count difference from the winner;
4. final tie-break by lower rollout index.

On a non-mixed pool, identical to WIN-C.

Purpose: isolate whether witness selection/diagnosticity is the missing variable.

#### A3 — PROXIMAL-CONTRAST

Use the same proximal failure selected in A2, but expose both the successful winner anchor and proximal rejected witness in one budget-matched contrast evidence unit.

Total updater-visible evidence budget must remain equal to the other arms. A straightforward implementation is an exact total block budget split deterministically between success anchor and rejected witness.

Purpose: test whether a failure is useful only when the updater can contrast it against what worked.

### Primary development contrasts

- `A2 - A1`: diagnostic witness-selection effect.
- `A3 - A2`: success-anchor / contrast effect conditional on proximal selection.
- `A3 - A0`: end-to-end repaired method value.

A1 is mechanistic, not the final baseline.

### Cost

Six streams × two replicates × four arms = **48 learned states**.

With the existing 18 held-out tasks:

48 × 18 = **864 held-out rollout units**.

This is approximately half the held-out workload of V2 while testing two distinct mechanism repairs.

## 9. Stage M2 — untouched development validation

Before seeing M1 outcomes, freeze the candidate-selection rule.

Recommended rule:

1. A1 is never selected as the final repaired method; it is historical/mechanistic reference.
2. Choose between A2 and A3 by the larger mean improvement over contemporaneous A0 across the six M1 streams.
3. Ties choose A2 because it changes fewer scientific variables.
4. No family deletion or stream deletion.

Then run the chosen candidate against fresh A0 on the **other six V2 development streams**, again with two contemporaneous replicates.

M2 cost:

6 streams × 2 replicates × 2 arms × 18 heldout = **432 held-out rollout units**.

A candidate is eligible for final confirmation only if the frozen M2 gate passes. A conservative development gate is:

- positive mean candidate-minus-WIN effect; and
- positive effect on at least 4/6 validation streams; and
- no unresolved technical/provenance failure.

This is a development gate, not a paper claim.

If M2 fails, stop the repair branch. Do not consume the untouched E3 future substrate.

## 10. Stage C0 — final independent confirmation only after M2 PASS

Use the prospectively reserved E3 substrate:

- 12 independent future streams;
- all six failure families, two streams each;
- 96 update tasks;
- all 36 previously-unsplit B4 tasks as the new held-out panel;
- no task replacement.

First acquire/freeze K=8 pools under a separate outcome-blind pool contract and apply the already-defined mixed-support identifiability gate. Never replace a low-support stream.

### Confirmatory arms

Only:

- WIN-C;
- the single M2-qualified repaired method.

Do not carry the four-arm development search into confirmation.

### Suggested replication/cost

Two contemporaneous replicates per stream.

12 streams × 2 replicates × 2 arms × 36 heldout = **1728 held-out rollout units**.

This matches V2's held-out workload while using twice the held-out task panel and half the number of learned states.

### Robust finite-sample primary

Treat stream as the independent unit.

For each stream, average replicate-level repaired-minus-WIN effect to get `D_s`.

A robust primary criterion can combine:

- exact one-sided binomial sign test on `I[D_s > 0]`, ties non-win;
- require at least `10/12` positive streams for alpha < .05 under p=0.5;
- require positive overall mean effect;
- optionally freeze a practical mean-effect threshold before C0 pool acquisition.

Report effect size and bootstrap intervals as estimation, not as a substitute for the frozen primary.

## 11. Why this plan has a better chance of working

The old MRW treatment chose a failure because it was the first deterministic failure, not because it was the most instructive failure.

The new design targets two bottlenecks that are both mechanistically plausible and supported by development evidence:

1. **diagnostic selection** — choose a failure that followed the successful route far enough to expose a local mistake rather than an early generic collapse;
2. **contrast anchoring** — give the updater enough successful context to infer the failure-to-repair delta rather than asking it to generalize from the failure in isolation.

The method remains tightly connected to the original paper story: search generates hidden counterevidence, but hidden counterevidence is useful only after a diagnostic projection selects and structures it correctly.

## 12. Stop conditions

Stop this repair direction if:

- proximal selection does not beat FIRST-FAIL in M1;
- proximal contrast does not improve over proximal failure and neither beats WIN in M2;
- the M2 validation gate fails;
- the future E3 pool-support gate fails;
- the final C0 confirmatory test fails.

Negative outcomes remain useful:

- A2≈A1 says witness selection is not the bottleneck;
- A3≈A2 says successful anchoring/contrast is not the bottleneck;
- all failure arms≤WIN says failure-aware projection is not behaviorally useful under this updater/substrate;
- development success but C0 failure says the repair did not generalize prospectively.

No failed gate should be repaired by changing streams, families, thresholds, or backbones inside the same scientific object.

## 13. Current recommendation

Do **not** spend the next major budget on the family-conditioned predictor as the primary paper mechanism.

Keep the family-prediction E3 work as a useful analysis/design asset, but demote family from the primary causal story to a blocking/coverage variable.

Prioritize the diagnostic-witness mechanism pilot because it directly attempts to turn the V2 HOLD into a causal explanation and a stronger method.

Current authority remains zero. The next permissible action should be to freeze and review the M1 contract before any provider call.
