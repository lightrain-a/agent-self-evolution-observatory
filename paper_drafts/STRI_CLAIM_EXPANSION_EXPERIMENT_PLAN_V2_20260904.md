# STRI Claim-Expansion Experiment Plan V2

Date: 2026-09-04
Status: PRE-EXECUTION DESIGN ONLY
Execution authority: CLOSED
Scientific role: optional claim expansion beyond the current submission-ready narrow paper

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

Every later stage is locked until the preceding gate passes.

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
- access latency/cost if obtained without changing the mechanism.

No task success or LLM semantic judge is a P0 primary endpoint.

## 11. P0 hard gates

### INVALID_CONTRACT

Any primitive/hash/metadata mismatch, partial primitive truncation, arm-specific semantic rewrite, or binding `C_vis` invalidates the unit/experiment before scientific interpretation.

### STOP_PLACEBO

If ID-placebo changes semantic exposure at any primary scientific checkpoint (`D_ID_i > 0`), stop package-partition attribution and repair the reconstruction pipeline before any new scientific run.

### STOP_NO_NONCLONE_LOCAL_EFFECT

If the non-clone treatment has no stable semantic divergence, stop architecture-general claim expansion.

### GO_P1

P1 opens only if:

- `D_sem_i > 0` occurs at checkpoints belonging to **at least two independent natural trajectories**;
- corresponding ID-placebos remain invariant;
- all contract checks pass.

A single-trajectory isolated divergence is not enough.

## 12. P0 workload

Base scientific execution:

```text
8 checkpoints × 3 required arms = 24 access replays
```

If the native access mechanism is stochastic, technical repeats may be added only under a frozen repeat rule and remain nested within checkpoint; do not count them as independent scientific units.

---

# P1 — Checkpoint-Forked Dynamic STRI

## 13. Entry condition

P1 is locked until P0 GO.

Use only P0-qualified checkpoints with a preregistered nonempty initial semantic deficit. Target scale:

```text
4–8 qualified checkpoints
```

No new checkpoint selection using P1 behavior outcomes.

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
- If no interpretable dynamic separation exists across at least two independent trajectories, STOP further dynamic claim expansion.

## 19. P1 workload

For 4–8 qualified checkpoints:

```text
3 arms × 4–8 checkpoints = 12–24 full trajectories
```

Nested technical seeds are allowed only under a frozen stochasticity rule and are not independent scientific units.

---

# P2 — Second Access Architecture Replication — OPTIONAL

## 20. Entry condition

P2 is optional and opens only if P0 demonstrates a clean non-clone local effect and P1 leaves an architecture-general claim scientifically relevant.

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

This document itself does **not** authorize execution. If later separately authorized and every gate passes, the base maximum before technical repeats is:

```text
P0: 24 access replays
P1: 12–24 full trajectories
P2: 24 access replays
--------------------------------
Total: 60–72 scientific executions
```

If P0 fails, stop after 24 access replays.

If P1 fails to yield an interpretable dynamic distinction, stop before P2.

The design intentionally spends evidence budget on claim gates rather than model/benchmark count.

---

# 25. Pre-execution review question

An independent reviewer should decide whether this is the smallest scientifically valid claim-expansion design and whether any of the following remain verdict-changing defects:

1. native-ranker + semantic-capacity prefix identification;
2. O/R/I placebo adequacy;
3. canonical primitive equivalence contract;
4. checkpoint sampling and independence;
5. 8-checkpoint mechanistic scale;
6. P1 O/S/P recovery estimand;
7. P2 second-architecture value versus unnecessary breadth;
8. baseline sufficiency versus MMR/RAG-redundancy reduction;
9. stop rules and interpretation boundaries.

Allowed review verdicts:

```text
PASS_MINIMUM_CLAIM_EXPANSION_DESIGN
REVISE_BEFORE_EXECUTION
REDUCE_OR_REDIRECT
STOP_CLAIM_EXPANSION
```
