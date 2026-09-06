# E2-R17 AtomGit State-Regeneration Model Panel — 2026-09-06

## Bottom line

AtomGit is useful here as a **model-subject pool**, not as a coding agent and not as a rescue path for the frozen E2 experiment.

The most informative shadow experiment so far is a same-evidence state-regeneration panel: give `qwen3.8-27b`, `GLM-5.2`, and `deepseek-v4-flash` the exact same synthetic evidence package six times each and ask each model to write a reusable persistent skill state.

The result is clean at the transport level after a harness-only output-budget repair:

| Model | Clean requests | Different state SHA | Core reusable primitives retained | Erroneous `SAME_INSTANCE_BINDING` | Literal instance ID leak | Format pass |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3.8-27B | 6/6 | 6/6 | 6/6 | 5/6 | 0/6 | 6/6 |
| GLM-5.2 | 6/6 | 6/6 | 6/6 | 0/6 | 0/6 | 6/6 |
| DeepSeek-V4-Flash | 6/6 | 6/6 | 6/6 | 5/6 | 0/6 | 4/6 |

The important observation is **not** that one model is globally better. It is that all three produce byte-distinct free-form states from byte-identical evidence, while all three still retain the core verification / tool-recovery / completion semantics on every draw. Surface/state realization is therefore highly non-deterministic in this harness even when core semantic content survives.

## Why the Qwen / DeepSeek leakage matters

The synthetic evidence contains one historical instance-only fact and explicitly says it must not become a reusable rule. The output contract exposes four candidate primitive names, including `SAME_INSTANCE_BINDING`, but only three are reusable for a different workbook.

Qwen and DeepSeek retain the three correct reusable primitives in all six draws, yet also include `SAME_INSTANCE_BINDING` in five of six draws. They do **not** copy the literal workbook or cell identifier. GLM excludes the binding primitive in all six draws.

This should be read together with the earlier relevance-classification panel. There, Qwen and DeepSeek correctly distinguish procedural evidence from instance binding. The new result therefore raises a more specific possibility:

> A model may understand the evidence distinction when explicitly classifying it, yet still fail to preserve that abstraction boundary when serializing the same evidence into a free-form persistent state.

That is directly relevant to the state-regeneration story: **diagnosis/classification competence and persistent-state synthesis competence are not obviously the same object.**

However, the current prompt names the forbidden binding primitive in the candidate set. That creates a label-salience confound. Therefore this result is a mechanism lead, not a paper claim.

## Harness lessons

### V1: local parser failure — zero provider use

The first isolated config used an unsupported `tools.todo.eager="off"` value. All attempted CLI invocations failed during local config parsing with zero usage rows. No model request was consumed and no sample was counted.

### V2: output budget was too small

With `max_tokens=2048`, reasoning-heavy Qwen and DeepSeek sometimes reached exactly 2048 completion tokens and AtomCode terminated the one-round invocation as `MaxRounds`. This is a harness confound, not evidence that the model cannot write the state.

### V3: output-budget-only repair

V3 kept the prompt, evidence, models, draw count, one-round cap, no-tools policy, and no-retry policy fixed; only `max_tokens` changed from 2048 to 8192. Because CodingPlan is request-count limited, this prevents hidden reasoning from consuming the entire completion allowance without increasing the planned request count.

V3 also used an exclusive run lock plus terminal marker so an outer MCP/network retry cannot silently launch a second panel. The completed terminal records 18 raw units, 18 state units, and 18 usage rows.

## Exact provenance

Raw root:

`/data/wyt/e2-r17-shadow-state-regeneration-panel-20260906/v3`

Frozen prompt SHA-256:

`d9995ace7e7274ec1fb1d7823c09e9d64011a7c32d66917f0c6c2910b78751e9`

Frozen V3 plan SHA-256:

`3111e32599f953c0c0e71d84932ac89a73b61bb825d6cea645dbcb7e7a147c70`

V3 result SHA-256:

`5edfb277c0ab9a6a8d2154758136434df020975df53138052c0a826a8e0019c0`

Offline raw-to-result audit: `18/18 state SHA MATCH`, zero mismatches.

## What this panel supports

It supports only these shadow observations:

1. byte-identical synthetic evidence can regenerate into byte-distinct free-form state text across repeated calls for all three AtomGit models tested;
2. the core reusable verification / tool-recovery / completion semantics can survive that byte-level drift in this panel;
3. Qwen and DeepSeek show a candidate-label / abstraction-boundary leakage pattern that GLM does not show in this particular free-form synthesis task;
4. the model ranking is task-dependent: the earlier 18-case diagnosis panel favored Qwen (`16/18`) over GLM (`14/18`) and DeepSeek (`13/18`), whereas this state-synthesis boundary test favors GLM.

This panel does **not** establish a population state-generation variance component, downstream utility variance, Search-Projection Censoring, a benchmark effect, or general model superiority.

## V4 mechanism falsifier: candidate/schema sensitivity

The proposed salience test has now been executed as a post-hoc shadow falsifier. It keeps the synthetic evidence and the three reusable primitives fixed, but replaces the fourth candidate name `SAME_INSTANCE_BINDING` with a neutral `P4_LOCAL_ONLY` definition stating that it applies only to the same historical workbook.

The transport is clean: 18/18 requests, 18 usage rows, zero tool calls, zero retries/replacements.

| Model | V3 named binding selected | V4 neutral P4 selected | Core primitives retained | Literal ID leak | Format pass |
|---|---:|---:|---:|---:|---:|
| Qwen3.8-27B | 5/6 | **0/6** | 6/6 | 0/6 | 5/6 |
| GLM-5.2 | 0/6 | **0/6** | 6/6 | 1/6* | 5/6 |
| DeepSeek-V4-Flash | 5/6 | **0/6** | 6/6 | 0/6 | 2/6 |

`*` The GLM literal-ID case is not a promoted binding rule: the state added an unnecessary explanatory note saying that the historical identifiers had been excluded, thereby repeating them verbatim. It is a literal output-contract violation, not a `P4_LOCAL_ONLY` selection.

DeepSeek's V4 format failures are likewise mostly verbosity/length violations (>1200 characters); the three core reusable primitives remain present in all six draws.

### Revised mechanism judgment

V4 changes the interpretation of V3. The earlier Qwen/DeepSeek 5/6 selection of `SAME_INSTANCE_BINDING` should **not** be used as evidence that those models fundamentally fail to understand instance binding. When the same non-transferable concept is presented through the neutral `P4_LOCAL_ONLY` contract, all three models exclude it in all six draws.

The safer conclusion is:

> Persistent-state synthesis is highly sensitive to the serialization schema and candidate presentation. A model can preserve the same core evidence while changing which boundary labels enter the persistent state as the output contract changes.

V4 does not isolate a purely lexical name effect because both the candidate label and its explicit definition changed. Therefore the supported diagnosis is **schema/candidate-presentation sensitivity**, not “the token string `SAME_INSTANCE_BINDING` alone caused the error.”

This is a useful system lesson because the scientific object is the persistent state actually written, not merely the model's latent ability to classify evidence correctly. The interface used to serialize state can itself become part of the update mechanism.

Exact V4 provenance:

- plan SHA-256: `be7d7b0e7d0e62b53e614cd9ac5458781ff4d6a920c7b3d14d614f06215677b7`
- prompt SHA-256: `14b36ac25c50c30b38a78fc465ecc84e221d7dc2441a74853ec50c6bd07f27b1`
- result SHA-256: `70902f0fbf4a397ddc54d593ce8a8c12d6ea3eb5c15c28165ce10de97d37fca5`
- raw root: `/data/wyt/e2-r17-shadow-state-regeneration-panel-20260906/v4-salience`
- offline raw/result SHA mismatch: `0/18`

## V5 FREE vs TYPED state-interface panel

The next proposed test was executed without rerunning the FREE arm. Frozen V4 remains the FREE parent; V5 adds only 18 TYPED draws (three models × six draws) using the same synthetic evidence, same model pool, same single-round/no-tools/no-retry transport, and the same 8192-token transport allowance.

The typed interface compiles the evidence into six fixed fields: scope, verification rule, tool-recovery rule, completion gate, local-fact policy, and the reusable primitive set. The expected semantic state is therefore explicit, but the model still has to decide which allowed value belongs in each slot.

Transport is fully clean: 18/18 requests, 18 usage rows, zero tool calls, zero retries/replacements.

| Model | FREE V4 unique state SHA | TYPED raw unique SHA | TYPED canonical JSON unique | TYPED semantic exact | Carry-forward errors | Literal-ID leaks |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3.8-27B | 6 | **1** | **1** | 6/6 | 0/6 | 0/6 |
| GLM-5.2 | 6 | 2 | **1** | 6/6 | 0/6 | 0/6 |
| DeepSeek-V4-Flash | 6 | 2 | **1** | 6/6 | 0/6 | 0/6 |

For GLM and DeepSeek, the two raw SHA values are only formatting variants (pretty-printed versus compact JSON / whitespace). After canonical JSON serialization, every draw of every model maps to the same semantic state. Qwen is byte-identical even before canonicalization.

### V5 mechanism judgment

This is stronger evidence for **state-interface / serialization sensitivity**, but the claim must stay precise. Corrected FREE V4 was already semantically good at the coarse endpoints: all three models retained the three reusable primitives in 6/6 draws and selected the local-only P4 candidate in 0/6. Therefore V5 does **not** establish an additional coarse semantic-accuracy gain over V4.

What V5 does establish in this shadow package is a large reduction in state-realization variability:

> The same evidence generated six different free-form state texts per model, while the typed interface collapsed all six draws of all three models to one canonical semantic representation.

This supports the hypothesis that persistent-state representation is partly a systems-interface object rather than only an intrinsic model-sampling object. It still does not show that typed state improves downstream task utility, and it does not estimate a population state-generation variance component.

Exact V5 provenance:

- plan SHA-256: `865937d6ce65823c8178401ae74cf37165fc5774ce4e344c75feabd7cdc8bdce`
- prompt SHA-256: `f662bcd6d25b3c46ec0e26bcce189b661f40c2a698a839af9758fe4f0aa34216`
- result SHA-256: `fca858dea2931e012dbce7edf88d325754a35a8c2bdcedb8479552b790ae1e1f`
- raw root: `/data/wyt/e2-r17-shadow-state-regeneration-panel-20260906/v5-typed`
- terminal: 18 raw units / 18 state units / 18 usage rows

## V6 downstream state-consumption propagation panel

The proposed downstream falsifier was executed prospectively. For each V4 generator model, the two FREE states with minimum pairwise text similarity were selected before any V6 actor result. One canonical V5 TYPED state was added. This yields seven frozen state conditions. A fixed Qwen3.8-27B actor then evaluates four synthetic future situations three times per state, for 21 total invocations.

The actor is deliberately state-bound: it must use only rules explicitly present in the supplied persistent state and return `UNKNOWN` when the state does not explicitly support a decision. This makes V6 a controlled state-entailment/consumption test rather than a test of the actor's own spreadsheet world knowledge.

Transport and within-state repeatability are clean:

- 21/21 transport-clean;
- 21 usage rows;
- zero tool calls;
- zero retry/replacement;
- zero state condition shows actor-response variability across its three repeats.

The three core procedural behaviors are invariant across all seven states:

- verification after save: 21/21 `RELOAD_VERIFY`;
- stale-sheet recovery: 21/21 `REFRESH_REPAIR_RETRY_ONCE`;
- completion before reload verification: 21/21 `NOT_COMPLETE`.

The cross-workbook local-fact boundary, however, follows the actual state content exactly:

| State content class | Actor responses |
|---|---:|
| FREE state explicitly says local instance facts must not transfer | **9/9 `DO_NOT_TRANSFER`** |
| FREE state omits an explicit cross-workbook local-fact rule | **9/9 `UNKNOWN`** |
| Canonical TYPED state has `local_fact_policy=exclude_from_cross_workbook_state` | **3/3 `DO_NOT_TRANSFER`** |

### V6 mechanism judgment

V6 rules out the weakest interpretation of the earlier state-SHA drift. At least for this controlled state-consumption task, free-form state realization is not merely cosmetic: whether a cross-instance boundary is explicitly serialized can change what the future actor is willing to conclude, while the core procedural behavior remains unchanged.

The strongest safe statement is:

> Under a frozen state-only consumption rule, omission versus explicit preservation of a local-fact boundary in free-form persistent state propagates into different future decisions; the canonical typed state preserves the boundary and yields stable behavior.

This is still a synthetic state-entailment result, not downstream benchmark utility. The `UNKNOWN` policy is intentionally conservative, so V6 does not show that an unconstrained deployment actor would fail a real task, nor that typed state improves task success. It shows that persistent-state content variation can be behaviorally consequential under controlled consumption.

Exact V6 provenance:

- plan SHA-256: `4e4c6097aed6bd44b23924fd29c69c5f2e854823de81f06a1a4b99ba5ab39fc7`
- result SHA-256: `0f55923718cd84de16f02ef3b23027d52c20edf2db36c237203c9b02c90e0847`
- raw root: `/data/wyt/e2-r17-shadow-state-regeneration-panel-20260906/v6-actor-consumption`
- terminal: 21 raw units / 21 usage rows

## What AtomGit should be used for next

The next high-value falsifier is now **cross-actor**, not more state draws. Reuse the same seven frozen V6 state conditions and the exact same four-task consumption contract, but run one outcome-blind repeat with GLM-5.2 and one with DeepSeek-V4-Flash as the fixed actor. This directly tests whether the explicit-boundary versus omitted-boundary behavior pattern is specific to Qwen's instruction-following style.

If both additional actors preserve the same separation, the serialization-to-behavior mechanism becomes more credible across actor families. If they fill missing rules from their own world knowledge instead of returning `UNKNOWN`, the conclusion must narrow to actor-policy-dependent state consumption.

The cross-actor panel remains shadow-only and may not read R3D support, Stage-B heldout/effects, or be used to rescue/replace the primary E2 model.
