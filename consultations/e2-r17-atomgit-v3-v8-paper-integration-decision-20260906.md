# E2-R17 AtomGit V3–V8 paper-integration decision — 2026-09-06

## Decision

The AtomGit V3–V8 sequence is **shadow mechanism evidence and execution-design rationale**, not a new confirmatory result block for the current manuscript.

Do not change the current completed-evidence headline, the V4-R2 primary estimand, the SCREEN/VALIDATION gates, or the main DeepSeek V4-Pro scientific model because of these shadow panels.

The sequence is useful because it separates five surfaces that the phrase “state regeneration instability” could otherwise conflate:

1. **free-form write realization** — identical synthetic evidence can produce different persistent-state text;
2. **typed storage canonicalization** — a fixed typed writer can collapse those realizations to one canonical semantic state;
3. **behavioral propagation** — omission versus explicit preservation of a state boundary can change a future state-bound actor decision;
4. **consumer heterogeneity** — different actor backbones need not interpret the same stored field identically;
5. **consumer-contract closure** — deterministic schema-aware consumption can remove one observed interpretation gap.

These distinctions sharpen the system design but do not establish real-task utility.

## Frozen shadow evidence

### V3 — same-evidence free-form regeneration

Three AtomGit models × six draws. All clean draws retain the core reusable verification/recovery/completion semantics, while each model produces six byte-distinct free-form states.

Result SHA-256:

`5edfb277c0ab9a6a8d2154758136434df020975df53138052c0a826a8e0019c0`

### V4 — candidate/salience falsifier

Replacing a salient `SAME_INSTANCE_BINDING` candidate label with neutral `P4_LOCAL_ONLY` removes the earlier Qwen/DeepSeek 5/6 admission pattern without harming core semantics. The earlier result therefore cannot support a deep “models do not understand binding” claim.

Result SHA-256:

`70902f0fbf4a397ddc54d593ce8a8c12d6ea3eb5c15c28165ce10de97d37fca5`

### V5 — FREE vs TYPED writer

The frozen V4 FREE arm remains six byte-distinct states per model. Under the typed writer, all six draws of all three models canonicalize to exactly one JSON semantic state; Qwen is also byte-identical before canonicalization.

Result SHA-256:

`fca858dea2931e012dbce7edf88d325754a35a8c2bdcedb8479552b790ae1e1f`

Interpret only as reduced representational/state-realization variability on the synthetic package. Corrected FREE V4 was already coarse-semantically correct, so V5 is not evidence of downstream utility improvement.

### V6 — state content to behavior

A frozen Qwen actor receives six maximally separated FREE states plus one canonical TYPED state. Core verification/recovery/completion decisions remain invariant. For the local-fact boundary, FREE states that explicitly preserve non-transfer produce 9/9 `DO_NOT_TRANSFER`; FREE states omitting that boundary produce 9/9 `UNKNOWN`; the TYPED state produces 3/3 `DO_NOT_TRANSFER`.

Result SHA-256:

`0f55923718cd84de16f02ef3b23027d52c20edf2db36c237203c9b02c90e0847`

This is controlled state-entailment behavior, not benchmark task success.

### V7 — cross-actor falsifier

DeepSeek replicates the Qwen state-consumption pattern. GLM does not: it returns `UNKNOWN` even for explicitly stored non-transfer state and for the raw typed `local_fact_policy` field, while still consuming all three core procedural rules correctly.

Result SHA-256:

`552c10296acabfed443f992e4a090ee16a2edcbf9b964927bac4d154c67b463e`

This falsifies a universal “typed storage automatically yields cross-backbone equivalent behavior” claim.

### V8 — schema-aware consumer closure

A deterministic fail-closed typed-state consumer maps validated typed fields to explicit actor directives. Zero-provider tests: 8/8 PASS. With those compiled directives, the previously unresolved GLM path is 3/3 exact and 3/3 `DO_NOT_TRANSFER`, with one response SHA.

Result SHA-256:

`9d54aceaae93fdad38c67e246dace7b33a4e9b4ee899c2e5d45233004c1bab0f`

This supports a producer–consumer interface interpretation on the synthetic probe. It does not establish real-task utility.

## Consequence for formal Bridge V4-R2

The shadow sequence does **not** require reopening the already-reviewed V4-R2 scientific protocol.

Reason: formal Bridge V4-R2 does not define the actor treatment as raw typed JSON. `research_pipeline/e2_r17_state_compiler_bridge.py` uses `TypedDiagnosis` only as an internal deterministic representation and compiles it through `compile_skill()` into canonical Markdown repair blocks. The intended actor-visible treatment is the resulting `CompiledState.skill_markdown` / `SKILL.md` bytes.

Current compiler checks remain 15/15 PASS and establish byte-deterministic rendering plus exact reproduction of the frozen G1/G2/G3 skill surfaces.

However, the V4-R2 execution-preparation branch does not yet contain the final Stage-A execution runner. Therefore one execution binding must be frozen before provider execution:

> deterministic compiler/control state → exact `compile_skill().skill_markdown` bytes → materialized `SKILL.md` → SHA verification against `CompiledState.skill_sha256` → standard actor `skill_source`, with no raw diagnosis exposure and no second LLM/free-form rendering step.

This requirement is frozen separately on branch:

`research/e2-r17-bridge-v4r2-execution-prep-20260906`

commit:

`cfcaaa89` — `research: bind Bridge V4R2 compiler-to-actor handoff`

artifact:

`generated/e2-r17-bridge-v4r2-post-atomgit-consumer-handoff-addendum-20260906.json`

artifact SHA-256:

`a6f75059b11e27ca5b019a79c87a99914e8e56902eb9a8cb4b253be2fa1c2d53`

The addendum changes no estimand, task, arm, model, primitive, gate, provider budget, or authority. It is an execution-faithfulness requirement for the future Stage-A runner.

## Manuscript placement

For the current paper:

- **Main results:** do not add V3–V8 as confirmatory evidence.
- **Method motivation / discussion:** it is legitimate to mention that preliminary cross-model shadow diagnostics motivated explicit separation of write representation and consumption semantics, without reporting them as scientific support for Q1.
- **Appendix / supplementary diagnostics:** V3–V8 can later appear as clearly labeled synthetic shadow diagnostics if space and narrative need justify it.
- **Claim language:** never say AtomGit establishes a typed-compiler utility gain, cross-backbone generalization, or the causal M4 generator effect.

## Stop rule

Do not spend more AtomGit quota on extra models, draws, or synthetic cases now.

Reopen this line only when a prospectively frozen experiment adds a new paper-level evidence type, such as:

1. real-task downstream utility under a matched FREE versus deterministic-compiler state treatment; or
2. a separately authorized second-backbone/public transport question after the primary gate.

Until then, AtomGit remains a shadow model-subject pool with zero authority over the primary E2 scientific lineage.
