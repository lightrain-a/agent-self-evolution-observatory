# STRI Claim-Expansion Experiment Plan V2.1

Date: 2026-09-04
Status: REVISED PRE-EXECUTION DESIGN AFTER INDEPENDENT GPT-5.6 REVIEW
Execution authority: CLOSED
Scientific role: optional claim expansion beyond the current submission-ready narrow paper
Review provenance: V2 commit `2de8168f55f93078a4fbbe33d3a247b75bcd8022` received `REVISE_BEFORE_EXECUTION`; V2.1 applies only its verdict-changing fixes.

## 0. Design principle

This plan follows an objection/claim-gate rule rather than a workload-matching rule. The current narrow STRI paper does not require new experiments. New execution is justified only if it buys one of:

1. identification of a non-clone representation effect at a real repeated-access skill boundary;
2. separation of one-shot recovery from persistent-representation robustness;
3. one architecture-level replication showing that the access-boundary abstraction is not specific to one schedule.

No broad model × benchmark sweep is authorized by this plan.

## 1. Claim ladder and stop logic

### Current supported claim — unchanged

- Local representation-sensitive skill access exists on the frozen evidence base.
- P19 provides one bounded representation -> access -> mediator -> behavior witness.
- Behavioral propagation beyond P19 is not established.

### Optional expanded claims

- **P0 claim:** a non-clone, semantics-preserving package repartition can change semantic access at natural checkpoints of one genuinely repeated-access agent under representation-neutral capacity.
- **P1 claim:** after a qualified local divergence, one-shot and persistent repackaging have measurably different recovery/persistence behavior in the closed loop.
- **P2 claim:** the P0 access-level effect reproduces under a second, meaningfully different skill-access schedule.

P1 is locked behind a loss-bearing P0 gate. P2 is a separate optional access-level generalization branch after a clean P0 and is never automatic; it runs only if an explicit second-architecture claim is separately authorized.

---

# P0 — Non-clone Local STRI

## 2. Scientific question

At a natural skill-access checkpoint, with complete pre-access state, optional access request, underlying canonical semantic primitives, native physical-package ranker, budgets, and stochastic policy fixed, can changing only physical package partition alter the canonical semantic primitives actually exposed to the actor?

## 3. Scientific unit

One scientific unit is a frozen natural pre-access checkpoint:

```text
X_i = (H_ti, U_ti, S_ti, B_ti, xi_ti)
```

where:

- `H_ti`: complete pre-access state;
- `U_ti`: optional access request/control signal;
- `S_ti`: canonical primitive support available before representation-dependent ranking;
- `B_ti`: frozen representation-neutral resource contract;
- `xi_ti`: paired stochastic state/policy.

Technical repeats are nested inside `X_i`; they are not independent scientific units.

## 4. Minimum sample geometry

Freeze exactly:

- **8 checkpoints**;
- from **>=4 independent natural trajectories**;
- maximum **2 checkpoints per trajectory**;
- covering **>=2 distinct task/workflow instances**.

This is a mechanistic reproducibility gate, not a population-effect power claim.

## 5. Outcome-blind checkpoint selection

1. Generate untouched Original-only natural trajectories under a frozen task × seed schedule.
2. Enumerate every access boundary as `(task_id, seed, access_ordinal)`.
3. Apply only pre-access mechanical eligibility rules:
   - trajectory technically valid up to the boundary;
   - repeated-access substrate has already performed the required prior access event(s);
   - canonical primitive support contains the preregistered transformable primitive pair;
   - both representations satisfy the frozen capacity contract without truncation.
4. Never inspect:
   - future actions or task outcome;
   - Original retrieval scores;
   - Original admitted set;
   - eventual trajectory length except corruption;
   - any treated-arm output;
   - whether a checkpoint appears likely to diverge.
5. If more than 8 qualify, select by a frozen hash over `(task_id, seed, access_ordinal)`.
6. If multiple primitive pairs are eligible, select by a frozen hash over canonical primitive IDs, not retrieval rank or downstream relevance.

### 5.1 Source-trajectory acquisition contract

Checkpoint acquisition is a separate workload from the 24 O/R/I access replays.

Before any provider execution, freeze exactly one of two routes:

- **FROZEN_POOL:** use a pre-existing untouched Original-only trajectory pool whose task IDs, seeds, access traces, and content hashes were fixed before any P0 treatment outcome existed; or
- **FINITE_NEW_POOL:** execute exactly **8 Original-only natural source trajectories** under a preregistered finite task × seed schedule covering at least two task/workflow instances. The exact task IDs and seeds are frozen with the chosen substrate before execution authority opens.

The candidate acquisition block may not be extended adaptively. After the frozen pool or the 8-trajectory block is complete, apply the outcome-blind checkpoint eligibility/selection rules above.

If it does not yield at least 8 eligible checkpoints drawn from at least 4 independent source trajectories and at least 2 task/workflow instances, return:

```text
STOP_INSUFFICIENT_ELIGIBLE
```

and do not run the 24 O/R/I scientific access replays.

If `FINITE_NEW_POOL` is used, those 8 natural source trajectories are reported separately from the 24 P0 access replays; the phrase “P0 = 24 replays” never denotes total new provider burden.

## 6. Canonical primitive equivalence contract

Freeze a primitive table:

```text
C = {(id_j, bytes_j, sha256_j, description_j, metadata_j, semantic_cost_j)}
```

Primary non-clone transformation example:

```text
Original / macro:
P_AB -> [hash_A, hash_B]

Repacked / atomic:
P_A -> [hash_A]
P_B -> [hash_B]
```

Required programmatic equality:

```text
multiset_union(manifests_original)
==
multiset_union(manifests_repacked)
```

with multiplicity exactly one for every canonical primitive.

Forbidden:

- primitive rewriting;
- summarization/compression differences;
- added or deleted primitive bytes;
- LLM-generated per-arm package descriptions;
- arm-specific semantic metadata.

Package descriptions/metadata, when required by the native ranker, must be produced by one frozen deterministic composition function over primitive-level frozen descriptions/metadata.

## 7. Representation-derived state

Rebuild independently per arm, using the same frozen construction pipeline/configuration/randomness:

- dense/sparse package embeddings;
- BM25/IDF state;
- ANN indexes;
- package manifests and IDs;
- searchable metadata;
- package descriptions derived from contents;
- router/reranker records;
- package-conditioned caches;
- tokenized package records;
- package-package similarity structures.

These are mediators of the representation intervention and must not be frozen to identical realized values across arms.

## 8. P0 arms

### O — Original

Untouched physical package partition.

### R — Repacked

Exactly one preregistered non-clone partition transformation such as `A+B <-> A / B`, with identical canonical primitive bytes/support.

### I — ID-placebo — REQUIRED

Keep Original package boundaries and primitive allocation, but regenerate package IDs and every representation-derived state through the same reconstruction pipeline used by R.

Primary contrast:

```text
O vs R
```

Required falsification contrast:

```text
O vs I
```

Optional supporting controls only:

- exact-clone stress control;
- semantic quotient / semantic-first oracle reference;
- MMR/diversity-aware retrieval sanity baseline in supplement only, if reviewer positioning requires it.

These optional controls do not replace O/R/I and do not define the primary claim.

## 9. Representation-neutral capacity contract

Do not use physical-package Top-k for P0.

Freeze semantic capacity:

```text
C_sem
```

For package p:

```text
c_sem(p) = sum(canonical_primitive_cost(h) for h in manifest(p))
```

Keep the native physical-package scorer/ranker unchanged. For each arm, rank all eligible physical packages natively, then admit the **longest ranked prefix** whose cumulative `c_sem` is <= `C_sem`.

Rules:

- no package Top-k;
- no semantic reranking;
- no deduplication after ranking;
- no skipping an overflowing higher-ranked package to back-fill lower-ranked packages;
- no partial package/primitive truncation.

Also freeze a visible-context ceiling `C_vis`, but certify before execution that it is non-binding for every valid arm/checkpoint under `C_sem`. If it cannot be made non-binding, lower `C_sem` prospectively for all arms.

Unused semantic slack is allowed and reported.

Scientific interpretation: this is a **representation-neutral interface test preserving the native physical-package ranker**, not a native fixed-Top-k vulnerability test. P19 remains the native fixed-slot audit.

## 10. P0 endpoints

Let `Phi(E_i,r)` be the exact set of canonical primitive hashes exposed to the actor.

### Primary endpoint

```text
D_sem_i = 1 - Jaccard(Phi(E_i,O), Phi(E_i,R))
```

### Required placebo endpoint

```text
D_ID_i = 1 - Jaccard(Phi(E_i,O), Phi(E_i,I))
```

### Secondary programmatic diagnostics

- physical ranks of transformed packages;
- admitted canonical semantic bytes/tokens;
- unused semantic slack;
- actor-visible skill tokens;
- canonicalized semantic exposure order distance;
- access latency/cost if obtained without changing the mechanism;
- optional **no-new-execution mechanism decomposition** from the same P0 logs: label each `D_sem>0` case as involving changed native physical-package ranking versus identical relevant ranking with divergence introduced only by whole-package semantic-capacity prefix admission. This is descriptive only and never a gate.

No task success or LLM semantic judge is a P0 primary endpoint.

## 11. P0 hard gates

### INVALID_CONTRACT

Any primitive/hash/metadata mismatch, partial primitive truncation, arm-specific semantic rewrite, or binding `C_vis` invalidates the unit/experiment before scientific interpretation.

### STOP_PLACEBO

If ID-placebo changes semantic exposure at any primary scientific checkpoint (`D_ID_i > 0`), stop package-partition attribution and repair the reconstruction pipeline before any new scientific run.

### STOP_NO_NONCLONE_LOCAL_EFFECT

If the non-clone treatment has no stable semantic divergence, stop architecture-general claim expansion.

### STOP_DYNAMIC_INSUFFICIENT_LOSS

P0 can support its access-level claim with any valid non-clone semantic divergence, including gain-only cases. P1, however, studies reacquisition of **lost** primitives and therefore requires `L0 != ∅`.

If fewer than **4 checkpoints** satisfy all of:

- `L0 = Phi(E_i,O) \ Phi(E_i,R)` is nonempty;
- valid corresponding ID-placebo with `D_ID_i = 0`;
- all P0 contract checks pass;
- the 4 checkpoints span at least **2 independent natural trajectories**;

then stop dynamic expansion and do not run P1.

### GO_P1

P1 opens only with exactly **4 P1-qualified loss-bearing checkpoints** satisfying the conditions above.

If more than 4 checkpoints qualify, select exactly 4 by a preregistered deterministic hash over frozen checkpoint IDs. Do not choose by effect size, task outcome, downstream behavior, recovery prospects, or manual preference.

## 12. P0 workload

Scientific O/R/I replay block:

```text
8 checkpoints × 3 required arms = 24 access replays
```

Checkpoint-source acquisition is accounted separately:

```text
FROZEN_POOL:    0 new source trajectories
FINITE_NEW_POOL: exactly 8 new Original-only natural source trajectories
```

Thus the maximum new P0 burden before technical repeats is **24 access replays plus, only when needed, 8 separately reported source trajectories**. If the finite source block is insufficient, stop before O/R/I replay.

If the native access mechanism is stochastic, technical repeats may be added only under a frozen repeat rule and remain nested within checkpoint; do not count them as independent scientific units.

---

# P1 — Checkpoint-Forked Dynamic STRI

## 13. Entry condition

P1 is locked until P0 GO.

Use exactly the **4 P1-qualified loss-bearing checkpoints** selected by the frozen P0→P1 gate. They must span at least two independent source trajectories.

No additional P1 checkpoints may be accumulated adaptively. Heterogeneity across these four weakens or stops the dynamic claim rather than triggering sample expansion.

## 14. P1 arms

From the identical natural checkpoint `H_t0`:

### O — Original throughout

```text
Original -> Original -> Original -> ...
```

### S — One-shot repack

```text
Repack at qualifying access t0 -> canonical Original representation afterward
```

### P — Persistent repack

```text
Repack at t0 -> keep repacked representation for every later skill access
```

After treatment, planner/search/load/actor/environment states are allowed to diverge naturally. Do not state-align trajectories after t0.

### 14.1 P1 treatment-state boundary — REQUIRED

P1 distinguishes **treatment-controlled representation state** from **endogenous historical consequence state**.

Treatment-controlled representation state includes every object whose value is a deterministic/stochastic descendant of the currently active physical package realization and that is used to construct, rank, retrieve, route, load, or render future skill access:

- physical package store, IDs, manifests, derived package descriptions/metadata;
- dense/sparse embeddings, BM25/IDF state, ANN indexes;
- router/reranker/search/load package-conditioned records;
- package-conditioned caches whose keys/values depend on package identity/partition/content;
- tokenized package records and package-package similarity structures.

Endogenous historical consequence state includes what the agent/environment naturally remembers because of the t0 intervention:

- task/environment state;
- prior actions and observations;
- planner/actor working history causally produced after t0;
- model-visible conversation/history, including any skill information exposed at t0;
- non-package caches that are demonstrably independent of package representation.

Arm semantics are frozen as follows:

- **O:** treatment-controlled representation state is Original at t0 and every later access.
- **S:** use Repacked treatment-controlled state at t0 only. Immediately after the t0 access and **before the next skill-access opportunity**, purge every Repacked treatment-controlled representation object and rebuild/use the Original treatment-controlled state with the frozen construction procedure. Do **not** erase endogenous historical consequences of the t0 exposure.
- **P:** use Repacked treatment-controlled state at t0 and at every later skill-access opportunity; representation-derived state is rebuilt/updated only through the same frozen Repacked construction/update policy.

At every later access in all arms, hold fixed the access/ranker model and parameters, reconstruction code/configuration, `C_sem`, non-binding `C_vis`, access-operation budget, and stochastic/tie-break policy. Only the representation arm and its descendants differ.

This reset/persistence contract is part of the treatment definition. Without it, S vs P is not interpreted as one-shot vs persistent representation exposure.

## 15. P1 semantic deficit

At t0 define:

```text
L0 = Phi(E_t0,O) \ Phi(E_t0,R)
G0 = Phi(E_t0,R) \ Phi(E_t0,O)
```

P1 eligibility requires a nonempty preregistered local semantic divergence, not a downstream action difference.

## 16. P1 primary recovery endpoints

For each lost primitive `v in L0`:

```text
tau_v = first later skill-access event where v is re-exposed
```

Right-censor at episode termination if never reacquired.

Complete reacquisition time:

```text
tau_all = max_v tau_v
```

Report in number of subsequent skill-access opportunities; environment/decision steps are secondary.

Reacquisition fraction after j later access events:

```text
R_j = |L0 ∩ union_{i=1..j} Phi(E_ti)| / |L0|
```

Persistence is the number of later access opportunities before complete reacquisition, right-censored at termination.

## 17. P1 secondary endpoints

- frozen programmatic final task outcome / scalar evaluator;
- first action/tool-call divergence — descriptive only;
- functional compensation only when a preregistered machine-checkable subgoal predicate exists; otherwise omit rather than use retrospective semantic judging.

## 18. P1 decision rule

P1 is mechanistic/descriptive at this scale, not a population theorem.

- If one-shot repack is rapidly reacquired while persistent repack repeatedly suppresses the same primitives, report recovery-vs-persistent-exposure separation.
- If both treated arms rapidly recover and frozen final outcomes do not show stable downstream consequences, retain Local STRI and stop selling dynamic harm.
- If the four-checkpoint block is heterogeneous or yields no interpretable dynamic separation across at least two independent trajectories, STOP further dynamic claim expansion. Do not add checkpoints to rescue the claim.

## 19. P1 workload

Freeze one confirmatory mechanistic block:

```text
4 qualified checkpoints × 3 arms = 12 full trajectories
```

There is no automatic expansion to 5–8 checkpoints. Nested technical seeds are allowed only under a frozen stochasticity rule and are not independent scientific units.

---

# P2 — Second Access Architecture Replication — OPTIONAL

## 20. Entry condition

P2 is a separate optional access-level generalization branch. It opens only if P0 demonstrates a clean non-clone local effect **and** the authors explicitly choose to pursue the additional claim that the P0 effect reproduces under a meaningfully different access schedule.

P2 is not required for the P0 or P1 claims and is not automatically triggered by P1. If no second-architecture claim is desired, do not execute P2.

Do not add a second model merely to increase model count. Prefer a **meaningfully different access schedule**.

Examples:

- per-turn retrieval -> progressive disclosure / actor-triggered `load_skill`;
- planner/subtask router -> independent loader architecture.

The exact second architecture must be frozen prospectively before P2 execution.

## 21. P2 design

Repeat the P0 access-level O/R/I design with:

- 8 outcome-blind natural checkpoints;
- >=4 trajectories;
- >=2 task/workflow instances;
- the same canonical primitive/equivalence discipline;
- architecture-appropriate representation-neutral capacity;
- programmatic `D_sem` / `D_ID` endpoints.

No P2 full-trajectory Dynamic experiment is authorized by default.

## 22. P2 workload

```text
8 checkpoints × 3 arms = 24 access replays
```

---

# 23. Baseline policy

## Already sufficient structural baselines — do not expand

- released/uniform package allocation;
- inverse support / inverse-sqrt support;
- NNLS target fit;
- exact min-cover + uniform;
- max-min fair allocation;
- exact R* package optimum;
- semantic-first action-basis oracle/reference.

These already address the scalar-tuning / overlap / package-only repair objections.

## Runtime baselines required for new claim expansion

P0:

```text
Original / non-clone Repacked / ID-placebo
```

P1:

```text
Original / one-shot / persistent
```

P2:

```text
Original / non-clone Repacked / ID-placebo
```

Do not turn STRI into a generic reranker leaderboard. MMR/diversity retrieval is optional supplementary positioning, not the primary baseline family unless the paper starts claiming a new retrieval algorithm.

---

# 24. Maximum authorized workload implied by this design

This document itself does **not** authorize execution. If later separately authorized, the minimum claim-relevant blocks before technical repeats are:

```text
checkpoint source acquisition:
  FROZEN_POOL      = 0 new trajectories
  or FINITE_NEW_POOL = exactly 8 Original-only natural trajectories

P0: 24 access replays
P1: exactly 12 full trajectories, only after GO_P1
P2: 24 access replays, optional only for an explicit second-architecture claim
```

If every optional branch is pursued and a new source pool is required, the maximum base burden is:

```text
8 source trajectories + 24 P0 replays + 12 P1 trajectories + 24 P2 replays = 68 executions
```

With a pre-existing frozen source pool, the corresponding maximum is 60.

Stop logic:

- insufficient finite source pool -> stop after the 8 source trajectories and do not run P0 replay;
- P0 non-clone null -> stop after P0 (maximum 32 new executions when source acquisition was required, otherwise 24);
- fewer than 4 loss-bearing P1-qualified checkpoints -> do not run P1;
- P1 heterogeneity/no interpretable dynamic distinction -> stop dynamic claim expansion; do not add checkpoints;
- P2 runs only under a separately authorized second-architecture access claim, regardless of whether more workload would look stronger.

The design intentionally spends evidence budget on claim gates rather than model/benchmark count.

---

# 25. Pre-execution review question

An independent reviewer should decide whether this is the smallest scientifically valid claim-expansion design and whether any of the following remain verdict-changing defects:

1. native-ranker + semantic-capacity prefix identification;
2. O/R/I placebo adequacy;
3. canonical primitive equivalence contract;
4. finite checkpoint-source acquisition, sampling, and independence;
5. 8-checkpoint P0 mechanistic scale;
6. loss-bearing P0→P1 gate and exactly-four-checkpoint P1 scale;
7. P1 O/S/P treatment-state reset/persistence boundary and recovery estimand;
8. P2 second-architecture value versus unnecessary breadth;
9. baseline sufficiency versus MMR/RAG-redundancy reduction;
10. stop rules and interpretation boundaries.

Allowed review verdicts:

```text
PASS_MINIMUM_CLAIM_EXPANSION_DESIGN
REVISE_BEFORE_EXECUTION
REDUCE_OR_REDIRECT
STOP_CLAIM_EXPANSION
```
