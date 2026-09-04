# Self-Evolution Should Not Depend on How Skills Are Split

**STRI — current ICLR paper-first outline**

Status: **narrow scientific object is submission-ready; no new experiment is required for the current claim.**
Future iterative-agent P0/P1 is claim expansion only.

## 1. One-sentence thesis

A skill-using agent should not receive different **semantic capability at a skill-access boundary** merely because the same underlying capability is physically packaged with different IDs, counts, partitions, or wrappers.

STRI turns this into an auditable representation-invariance object and separates three levels that must not be conflated:

1. **Runtime Local STRI** — does equivalent repackaging change semantic access?
2. **Structural realizability** — can package-only control realize the same semantic target in principle?
3. **Downstream propagation** — if local access changes, does it alter later behavior?

Current evidence supports (1), gives an exact certificate for the package-only specialization in (2), and provides only one bounded positive witness for (3).

---

## 2. Correct runtime object

At skill-access opportunity t:

```text
E_t^(r) = A_theta(H_t, U_t, P_t^(r), B_t, xi_t)
```

Compare the preregistered semantic projection:

```text
phi(E_t^(r))
```

Where:

- `H_t`: complete pre-access agent/controller state;
- `U_t`: optional access request/control signal — query, planned subtask, `load_skill`, router signal, or null;
- `P_t^(r)`: physical package realization under representation r;
- `B_t`: frozen resource budget;
- `xi_t`: paired stochastic state;
- `E_t^(r)`: information/callable capability crossing into the actor interface.

A semantics-preserving intervention freezes the **semantic candidate support and semantic payload**, but physical package identity/count/partition/multiplicity may change because they are the treatment.

Representation-derived access state is a mediator, not a pretreatment covariate. Embeddings, BM25/IDF state, ANN indexes, package metadata, router records, manifests, tokenized records, and representation-conditioned caches are rebuilt independently per arm using the same frozen construction procedure/configuration/randomness.

### Why this abstraction matters

Do not universalize any single schedule:

- task-level prefetch;
- per-turn retrieval;
- planner → subtask → retrieval;
- actor-triggered `load_skill`;
- progressive disclosure.

Explicit `q_t` and whole-task Top-k are special cases, not the definition.

---

## 3. Structural specialization: package-only exposure

For released systems with independent support truth, freeze support matrix A. Package mass `w >= 0` induces structural semantic exposure:

```text
e = A w
```

This is an **offline structural specialization**, not every agent's runtime algorithm.

For representation-independent target `q > 0`:

```text
R*(A;q) = min t
s.t. q <= A w <= t q,  w >= 0
```

Key boundary:

- `R*=1` iff `q` lies in the package support cone;
- `R*>1` is the tight package-only residual for that target/control class.

Exact clone duplication does not change the support cone. Partial-overlap geometry can still make a target unrealizable even after arbitrary global package reweighting.

### Human-readable witness

Global singleton supports for two packages plus a shared support cell force a factor-2 lower bound. The released Skill-SP Level-1 optimum is exactly 2.

### Negative regimes

- Skill-SP Level-3: `R*=1`;
- logical compiler: 127/128 multi-membership yet `R*=1`.

Therefore overlap prevalence is not the structural explanation.

---

## 4. Three research questions and evidence

### RQ1 — Can equivalent packaging change local semantic access?

**Main evidence**

1. **Skill-SP**: same-state package identity reparameterization changes package-class mass / prompt mixture; quotient conservation restores it.
2. **SkillRL**: fresh-ID exact clones change semantic retrieval for 11/12 targets under finite package budget; placebo/quotient controls are invariant; the effect disappears when capacity is sufficient.
3. **AutoSkill held-out qualification**: representation-sensitive retrieval appears in 9/9 outcome-blind held-out units.

**Interpretation**

Local representation-sensitive access is supported. Do not call this task-success or utility harm.

### RQ2 — Is the structural residual really support geometry rather than duplicate count, overlap, or bad tuning?

**Main evidence**

- Skill-SP Level-1: neutral `R*=2` on full, calibration, and tool-disjoint heldout support matrices;
- calibration-fitted exact weights transfer to heldout without refitting;
- uniform already reaches the exact worst-case optimum;
- inverse-support / NNLS can improve some average-fit quantities while worsening worst-case ratio;
- Level-3 and logical compiler are equalizable negative controls.

**Supporting evidence — supplement, not separate paper claims**

- target-ray sensitivity;
- exact edit radii;
- witness peeling;
- degree-preserving rewirings;
- concentration constraints;
- solver runtime.

These exist to harden RQ2, not create an E4/E5/E6 laundry list.

### RQ3 — Does local access divergence propagate downstream?

**P19 bounded positive witness**

Frozen AutoSkill prefetch substrate:

```text
Original: 6/6 behavior-signature positive
Split-4:  0/6
ID placebo: 3/3
Quotient:   3/3
```

Mediator isolation under Split-4:

```text
specific post-checkout add-back: 3/3
matched cleanup add-back:        0/3
```

Thus P19 supports:

```text
representation
→ local semantic access
→ model-visible mediator
→ one mechanically defined executed behavior
```

**Held-out negative boundary**

A preregistered 2-unit / 8-valid-run behavior pilot did not meet the split-specific gate and stopped.

Correct statement:

> **Behavioral propagation beyond P19 is not established.**

Do not rewrite the STOP as “propagation is conditional,” because no propagation condition has been identified.

---

## 5. Relation to SkillZip / SkillZip Pro — what we learn and what we do NOT claim

### Research-method lesson

SkillZip treats a skill as a structured behavioral contract rather than a paragraph. SkillZip Pro further treats production skills as progressively loaded bundles with routing/entrypoint structure.

STRI adopts the same **object-first discipline**:

> define the real runtime object before proposing an experiment.

For STRI that object is the skill-access boundary, not a universal whole-task Top-k.

### Experimental-design lesson

Do not present many ablations as peer-level findings. Organize evidence around the paper's load-bearing RQs:

```text
RQ1 Local phenomenon
→ RQ2 mechanism / exact boundary
→ RQ3 downstream propagation + negative boundary
```

Robustness, cost, edit radii, null ensembles, and solver timing are supporting analyses.

### Writing lesson

The paper should read:

```text
real runtime mismatch
→ missing invariant
→ exact object/formulation
→ structural certificate
→ local system evidence
→ bounded behavior witness
→ failed generalization / claim boundary
```

Do not read:

```text
E1 / E2 / E3 / E4 / E5 / E6 evidence inventory
```

### Scientific distinction

SkillZip/Pro asks how to **rewrite/compress skill artifacts faithfully**.

STRI asks whether a **fixed access mechanism remains semantically invariant under equivalent physical package realization**.

STRI is not a compression method, MMR/diversity selector, or deduplication algorithm.

---

## 6. Main paper architecture

### Abstract

1. Real agents have heterogeneous skill-access schedules.
2. Define representation-invariance at the common access interface.
3. Introduce runtime Local STRI and separate structural `R*` specialization.
4. Give Skill-SP / SkillRL local evidence.
5. Give P19 bounded propagation witness.
6. Give 9/9 held-out Local qualification + stopped held-out behavior pilot.
7. End with exact boundary: P19-beyond behavior propagation not established.

### Introduction

1. Skills are structured persistent artifacts; production systems may progressively load them.
2. Package realization can nevertheless enter control.
3. State the missing invariant.
4. State three RQs.
5. Give compact released evidence / boundary.
6. Three contributions only.

### Related Work

Group by scientific object, not chronology:

- representation/routing/composition;
- SkillZip/SkillZip Pro contract-preserving compression;
- self-evolving controllers;
- exposure/convex optimization boundary.

### Problem Formulation

1. Runtime skill-access boundary `A_theta(H,U,P,B,xi)->E` and `phi(E)`.
2. Representation-derived access state is rebuilt per arm.
3. Local STRI vs downstream propagation.
4. Structural package-only specialization `e=Aw`.
5. Quotient / exact-refinement result.
6. `R*(A;q)` primal/dual and human-readable factor-2 witness.

### Experimental Setup

Only three load-bearing RQs.

### Results

- RQ1/RQ2 Skill-SP;
- RQ2 negative regimes;
- RQ1 SkillRL budget boundary;
- RQ1/RQ3 AutoSkill P19 + held-out STOP;
- compact supporting robustness paragraph.

### Discussion

- Runtime and structural layers are complementary but neither predicts the other.
- P19 is the only bounded behavioral propagation witness.
- No population utility/safety/regret claim.
- Future non-clone repeated-access P0 is claim expansion, not required for current narrow paper.

---

## 7. Main figures and tables

### Main text

1. **Figure 1 — STRI overview**: same semantic capability, different physical taxonomy, access/control may change.
2. **Figure 2 — R* boundary**: residual vs equalizable geometries + SkillRL finite-budget identity sensitivity.
3. **Table 1 — released-system identity sensitivity / audit role**.
4. **Table 2 — practical package-weight baselines / no-refit transfer**.
5. **Table 3 — first-party support-regime boundary**.

### Supplement

- factor-2 witness visualization;
- structural robustness figure;
- external SkillRouter / AgentSkillOS analogue tables;
- target rays / edit radii / witness peeling / null ensemble;
- conditional solver runtime;
- full P19 and held-out receipts.

Every main-text visual must answer one of RQ1--RQ3. Supporting stress tests do not get equal visual prominence.

---

## 8. Current claim boundaries

Do claim:

- package representation can change identity-indexed/local semantic access;
- exact clone invariance has a quotient characterization;
- package-only target realizability has an exact `R*(A;q)` boundary;
- P19 demonstrates one bounded representation→access→behavior chain;
- held-out retrieval sensitivity is observed in 9/9 qualified units.

Do not claim:

- all skill systems violate STRI;
- arbitrary realistic partial-overlap decompositions have been empirically tested;
- `R*(A)>1` causes AutoSkill crowd-out;
- Local STRI implies general behavioral propagation;
- STRI improves task utility/safety;
- semantic-first control is a validated repair;
- a new LP/cone theorem;
- a new compression/dedup/MMR method.

---

## 9. Optional future claim-expansion protocol V2.1 — independently reviewed PASS, not required for current paper

V2.1 is a **prospective design only**. Execution authority remains CLOSED. Independent GPT-5.6 Sol + Extra High review first returned `REVISE_BEFORE_EXECUTION`; after four verdict-changing repairs, the same reviewer returned `PASS_MINIMUM_CLAIM_EXPANSION_DESIGN` and explicitly required no extra models, benchmarks, checkpoints, trajectories, or MMR-style main baselines.

### Source checkpoint acquisition

Freeze one route before execution:

- `FROZEN_POOL`: pre-existing untouched Original-only natural trajectories fixed before P0 treatment outcomes; or
- `FINITE_NEW_POOL`: exactly 8 Original-only natural source trajectories under a finite preregistered task×seed schedule, covering >=2 task/workflow instances.

No adaptive extension. If the frozen pool/block cannot yield 8 eligible checkpoints from >=4 independent trajectories and >=2 workflows, return `STOP_INSUFFICIENT_ELIGIBLE` before O/R/I replay.

### P0 — non-clone Local STRI

Freeze exactly 8 outcome-blind natural access checkpoints, max 2 per source trajectory.

Required arms:

1. `O` Original;
2. `R` non-clone Repacked, e.g. canonical `A+B` macro versus separate `A` / `B` packages with identical primitive bytes/hashes and multiplicity one;
3. `I` ID-placebo preserving package boundaries while regenerating IDs and representation-derived state through the same pipeline.

Identification contract:

- retain the native physical-package ranker;
- do not use physical-package Top-k;
- admit the longest native-ranked prefix under frozen canonical semantic capacity `C_sem`;
- certify actor-visible `C_vis` is non-binding;
- rebuild representation-derived embeddings/indexes/router/search/load/package-conditioned cache state per arm;
- primary `D_sem = 1 - Jaccard(Phi(O), Phi(R))`;
- required placebo `D_ID = 1 - Jaccard(Phi(O), Phi(I))`.

Workload:

```text
P0 = 8 checkpoints × 3 arms = 24 access replays
source acquisition = 0 or exactly 8 separately reported Original trajectories
```

Any `D_ID>0` stops package-partition attribution. P0 may report valid access divergence even if it is gain-only, but P1 requires a loss-bearing deficit.

### P0 → P1 loss-bearing gate

P1 opens only if at least four checkpoints have:

- `L0 = Phi(O) \ Phi(R) != empty`;
- corresponding `D_ID=0`;
- all contracts valid;
- the four span >=2 independent source trajectories.

If fewer than four qualify: `STOP_DYNAMIC_INSUFFICIENT_LOSS`.
If more than four qualify: choose exactly four by a frozen deterministic hash, never by effect size or behavior.

### P1 — exactly four checkpoints / 12 full trajectories

Required arms:

1. `O`: Original throughout;
2. `S`: one-shot Repacked at t0, then before the next access purge/rebuild all representation-controlled package/index/embedding/router/search/load/cache state to Original;
3. `P`: persistent Repacked representation-controlled state at t0 and later accesses.

The one-shot reset **does not erase endogenous historical consequences** of t0: task/environment state, observations/actions, planner/actor history, and model-visible conversation including the t0 skill exposure remain.

At later accesses all arms keep the same ranker/model, reconstruction config, `C_sem`, non-binding `C_vis`, access budget, and tie-break policy.

Primary dynamic readouts:

- primitive reacquisition `tau_v` / complete `tau_all`;
- reacquisition fraction;
- persistence in subsequent access opportunities.

Programmatic final task outcome and machine-checkable functional compensation are secondary.

Workload:

```text
P1 = exactly 4 qualified checkpoints × 3 arms = 12 full trajectories
```

No adaptive expansion to 5–8 checkpoints. Heterogeneity/no interpretable dynamic separation weakens or stops the claim rather than triggering more trajectories.

### P2 — optional second access architecture only

P2 is **not** required for P0 or P1 and is not automatically triggered by P1. Run it only if the paper explicitly pursues an additional claim that P0 access sensitivity reproduces under a meaningfully different access schedule, e.g. per-turn retrieval versus progressive disclosure / actor-triggered `load_skill`.

```text
P2 = 8 checkpoints × O/R/I = 24 access replays
```

No P2 full trajectories by default. A second backbone with the same access schedule is lower-value than a genuinely different access architecture.

### Maximum base workload

```text
existing frozen source pool: 24 P0 + 12 P1 + optional 24 P2 = max 60
new finite source pool:      8 source + 24 P0 + 12 P1 + optional 24 P2 = max 68
```

Fail early at every gate. This workload is intentionally smaller than SkillZip Pro-style broad evaluations because every execution maps to a specific STRI claim/objection.

This remains future claim expansion, not missing confirmation for the current narrow submission.

---

## 10. Current submission state

- Current narrow paper: **scientifically submission-ready** under the existing claim scope.
- Independent Oracle GPT-5.6 Sol + Extra High review: `READY_NARROW_NO_NEW_EXPERIMENT` / `KEEP_CURRENT_NARROW`.
- Main text architecture has been rewritten around runtime object → structural certificate → RQ-driven evidence → negative propagation boundary.
- SkillZip / SkillZip Pro are now cited as the closest structured-artifact / progressive-loading representation neighbors, with the distinction stated explicitly.
- ICLR main-text page budget remains a hard gate; supporting robustness belongs in supplement rather than expanding the main story.
