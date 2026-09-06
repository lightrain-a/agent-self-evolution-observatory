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

## Next useful AtomGit experiment

The highest-value next shadow test is not “more draws.” It is one focused falsifier:

**Negative-Binding Salience / Serialization Ablation**

Hold the synthetic evidence fixed and change only how the non-transferable binding primitive is represented in the output contract. The goal is to separate two explanations:

- **candidate-label salience / serialization effect:** leakage disappears when the forbidden label is no longer presented as a selectable candidate;
- **deeper abstraction-boundary failure:** model still turns instance-only evidence into reusable state even when the output contract removes that candidate salience.

If the first explanation wins, the paper/system lesson narrows to state-schema/output-contract design. If the second survives, it becomes a stronger hypothesis about persistent-state synthesis itself.

This next test remains shadow-only unless it is prospectively connected to a paper-level claim gate.
