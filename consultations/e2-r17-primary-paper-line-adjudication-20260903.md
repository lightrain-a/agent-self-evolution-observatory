# E2-R17 Primary Paper-Line Adjudication — 2026-09-03

Status: `PRIMARY_STATE_GENERATION_BOTTLENECK / PARK_SEMANTIC_TRANSFER`

## Decision

The primary E2-R17 paper line is now:

> **Persistent skill self-evolution can fail at the state-generation step even when the learner is shown the same evidence. We therefore separate evidence selection from persistent-state synthesis and test whether a variance-controlled typed compiler converts trajectory evidence into more reliable reusable state than a free-form updater.**

The previously prepared Selective-MRW Semantic-Transfer V3 branch is retained as a zero-provider secondary hypothesis, but it must not receive Stage-A provider authority while the state-generation bridge is unresolved.

This decision is a scientific prioritization, not deletion of historical work.

## Why the primary line changed

### 1. Universal rejected-witness evidence did not establish a stable effect

The closed DeepSeek Repair2 study remains:

`HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS`.

Across 48 pairs / 96 learned states / 1728 heldout units, the mean MRW−WIN-C effect was positive but small and heterogeneous, with the frozen superiority test not passing. This is useful negative evidence against the paper claim that rejected failures are universally superior learning evidence.

### 2. Progress/diagnostic witness selection did not repair the problem

The single-case S1 witness-selector development pilot failed its pre-frozen gate:

`S1_SIGNAL_FAIL_STOP_NO_S2`.

Thus the simple story “choose a more diagnostic / later-progress failure and the learning effect becomes stable” did not survive direct intervention.

### 3. A strong frozen state itself was stable

The exact strong First-Fail learned state remained useful when frozen and remeasured:

`FIRST_FAIL_FROZEN_STATE_STABILITY_PASS`.

This localizes at least part of the instability away from downstream execution alone.

### 4. Byte-identical evidence did not regenerate the strong state

The strongest current localization is the exact-evidence updater replay. The updater received reconstructed byte-identical evidence, but fresh updater realizations failed to reproduce the historical strong downstream effect.

Frozen verdict:

`FIRST_FAIL_EXACT_EVIDENCE_UPDATER_REPLICATION_FAIL_STATE_GENERATION_VARIANCE`.

This is the key scientific pivot. It makes the state-generation realization itself a first-class experimental variable:

`trajectory evidence -> state generator -> persistent state -> future behavior`.

### 5. The deterministic G0/G1/G2/G3 micro directly targets the newly localized bottleneck

The current Recovery V3 does not attempt another evidence-selector rescue. It asks whether compact persistent-state semantics such as output verification, completion closure and clean error recovery are sufficient when represented deterministically.

This is a state-level mechanism gate, not a method claim.

## Why Semantic-Transfer V3 is parked rather than executed now

The semantic-transfer branch is scientifically coherent as a separate hypothesis:

> the relative value of rejected evidence may depend on reusable transformation versus instance binding/localization.

Its V3 repair is prospective and zero-provider. It has no Stage-A scientific pools and no provider authority.

However, it is not the highest-information next experiment after the exact-evidence replay result. It spends substantial provider budget to refine *which evidence* is useful before resolving the newly identified question of *whether the same evidence can be converted into a stable persistent state at all*.

Therefore:

- preserve Semantic-Transfer V3 artifacts and zero-provider audits;
- do not declare them scientifically invalid;
- do not authorize their Stage A while the state-generator bridge remains unresolved;
- revisit only if the state-generator bridge shows that generator choice is not the bottleneck, or as a later moderator experiment after a stable automatic state generator exists.

## Current primary causal decomposition

The paper should use four layers explicitly:

1. **Evidence availability / selection**: which generated trajectory+score package is learner-visible?
2. **State generation**: how is that evidence converted into persistent state?
3. **State semantics**: what procedural constraints are represented by that persistent state?
4. **Downstream behavior**: what future task utility does the frozen state induce?

Current evidence strength:

- evidence-source superiority: unresolved / heterogeneous;
- state-generation variance: directly observed locally through exact-evidence replay;
- persistent-state behavioral effect: strongest local evidence through frozen-state remeasurement;
- automatic constrained-generation method: not yet established;
- confirmatory generalization: absent.

## Literature collision boundary

The new paper must not claim novelty for generic trajectory diagnosis or generic experience-to-skill compilation.

### SkillRevise (arXiv:2606.01139)

SkillRevise already performs trace-conditioned defect diagnosis, retrieves reusable repair principles, and uses a revision operator to edit skills with execution anchors. Therefore `trajectory -> structured diagnosis -> skill edit` is not our novelty.

### WikiSkill (arXiv:2608.27454)

WikiSkill already separates raw execution traces, accumulated persistent knowledge and executable skills, and uses accumulated knowledge to guide later skill evolution. Therefore `compile experience into persistent knowledge` is not our novelty.

### Rethinking Self-Evolving Agent Skills (arXiv:2608.02636)

This work already shows that skill evolution is sparse and feedback-dependent and that conditions including failed trajectories can outperform success-only feedback, with strong model/benchmark heterogeneity. Therefore `failures can help skill evolution` is not our novelty.

## Residual novelty target

The defensible residual object is:

> **State-generation variance as an independently identified bottleneck in persistent skill self-evolution, plus a controlled factorization of evidence source and state-generation method.**

The proposed method is narrower:

> **Variance-controlled typed state compilation:** map learner-visible trajectory+score evidence to a finite diagnosis/repair representation and compile that representation canonically into persistent state, rather than asking a free-form LLM writer to synthesize the entire state realization.

This should be distinguished from SkillRevise by the causal question and interface:

- SkillRevise asks how to revise a weak skill from execution-grounded diagnosis and principles;
- E2-R17 asks whether free-form state synthesis itself is a stochastic bottleneck under matched evidence, and tests free-form versus canonical typed compilation while independently crossing the evidence source.

The typed vocabulary itself is not sufficient novelty. The paper-level contribution requires the evidence×generator experiment to show that controlling the generator changes reproducibility/utility prospectively.

## New primary experiment ladder

### M0 — closed evidence-source study

Already complete:

`HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS`.

Purpose: motivates why evidence selection alone is insufficient.

### M1 — single-case mechanism localization

Already complete components:

- S1 witness-selector failure;
- frozen strong-state stability;
- exact-evidence updater replay exposing state-generation variance.

Purpose: localizes the candidate bottleneck.

### M2 — deterministic state-semantic intervention

Active object: G0/G1/G2/G3 constrained-state micro Recovery V3.

Purpose: test whether compact deterministic state semantics are sufficient locally.

No method claim.

### M3 — frozen-state stability

Only if M2 passes original gate + provider-era veto:

- G0 + simplest selected deterministic arm;
- exactly two complete fresh remeasurements;
- no outcome-conditioned extra replicate.

Purpose: rule out one-off actor realization.

### M4 — prospective automatic bridge

Only if M2/M3 survive.

Fresh development 2×2:

`Evidence source ∈ {Winner, First-Fail-4}`

×

`State generator ∈ {native free-form updater, constrained typed compiler}`.

Primary causal objects:

- evidence-package effect;
- complete state-generation-method effect;
- evidence×generator interaction.

Strong falsifier:

`SCORE_ONLY_GENERIC_MAX`, which receives the same selected score pattern but no trajectory text.

SCREEN and VALIDATION use disjoint heldout panels.

### M5 — untouched confirmation

Only after M4 passes its frozen SCREEN and VALIDATION gates:

- separate E3 proposal;
- no automatic promotion from M4;
- later second backbone/public benchmark only if mechanism survives.

## Paper claim ladder

### Claim currently supportable

> In a controlled development case, identical trajectory evidence did not reliably regenerate the same useful persistent skill state, while a previously generated strong state retained downstream utility when frozen. This localizes a candidate bottleneck at persistent-state generation rather than evidence availability alone.

### Claim after deterministic micro + stability

> A compact deterministic persistent-state intervention encoding specific procedural semantics reproducibly improves the selected development case.

Still not an automatic learning-method claim.

### Claim after prospective bridge

If generator effect passes but First-Fail source does not:

> Canonical persistent-state compilation improves reliability/utility relative to free-form skill synthesis, while the hypothesis that rejected failure evidence is uniquely beneficial is unsupported.

If generator, source and interaction all pass:

> The usefulness of trajectory evidence depends on the state-generation interface: constrained compilation can convert selected rejected evidence into useful persistent behavior more reliably than the native free-form updater.

### Claim only after untouched E3

> The identified state-generation bottleneck and compiler benefit generalize beyond the development streams/panels used to construct the mechanism.

## Provisional title direction

Preferred working title:

> **Same Evidence, Different Skill: Diagnosing State-Generation Variance in Self-Evolving Agents**

Method-positive title, only if the bridge later passes:

> **Same Evidence, Different Skill: Variance-Controlled State Compilation for Self-Evolving Agents**

Avoid:

- “Learning Better from Failures”;
- “Compiling Agent Experience into Persistent Knowledge”;
- “Structured Diagnosis for Skill Revision”;

because those are either no longer supported as the central finding or collide directly with recent related work.

## Current authority

This adjudication grants no provider authority.

- Recovery V3 remains frozen and unchanged.
- State-compiler bridge remains zero-provider proposal only.
- Semantic-Transfer V3 remains parked zero-provider design only.
- No E3, second backbone, public benchmark or paper result promotion is authorized.
