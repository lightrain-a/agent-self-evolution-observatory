# B1 R70/R71 — Precision-Driven Semantic-Control R2 Framework

Date: 2026-09-04  
Status: ZERO-PROVIDER / REVISED PRE-EXECUTION HOLD  
Paper: `D2-PAPER-FAILURE-MEMORY-PROVENANCE`

## Why R68 was reduced

R68 froze a 660-trajectory five-arm plan over 66 fresh outcome-blind R54 clusters and two executors. An independent GPT-5.6 Sol + Extra High pre-execution review returned `REDUCE_OR_REDIRECT`.

The reviewer found that the problem was not insufficient workload. The problem was allocation:

- fresh no-memory and fresh masked arms did not buy identification for the current provenance question;
- exact label reversal changed the prompt-level success/failure prevalence and was a worse correctness control than a count-preserving shuffle;
- Llama did not need to replicate every secondary control;
- the original `UNKNOWN` string versus boolean truthful/reversed values was not representation-matched;
- retry authority should begin at treatment exposure, not at a scheduler `STARTED` marker.

R70 preserves the 66 independent unused clusters and removes only trajectories that do not change the central causal identification.

## Scientific object

Primary question:

> With retrieved memory content, retrieval membership/order, task, renderer schema, and token footprint fixed, does truthful source-outcome information change closed-loop OSInteraction terminal success relative to a neutral explicit-field control?

R70 does **not** test whether memory itself is useful, whether provenance-aware governance is effective, or whether semantic provenance effects generalize to independent writers/retrievers/substrates.

## Fresh panel

The panel is unchanged from R68:

- R54 outcome-blind eligible fresh clusters: 106;
- historical R56/R61 primary: first 32;
- historical R55/R60 utilization: next 8;
- R70: exhaustive remaining suffix `eligible[40:]` = 66 clusters;
- zero overlap with historical treatment units;
- 57/66 retrievals contain both success-derived and failure-derived memories.

No new ranking, cutoff, replacement, or outcome filtering is introduced.

## Representation-matched explicit field

All explicit-field arms use the same schema and value type:

```text
source_outcome_status: "S" | "F" | "U"
```

Shared legend:

```text
S=success, F=failure, U=unknown
```

Arms:

- `P_neutral`: every retrieved memory gets `"U"`;
- `T_truthful`: each memory gets truthful `"S"` or `"F"`;
- `S_shuffled`: on mixed-provenance retrievals only, the truthful S/F multiset is permuted non-identically across the frozen memory slots.

Static tokenizer audit over the actual 66 R54 frozen retrievals:

- Qwen2.5-7B: P/T token count identical on 66/66; P/T/S identical on 57/57 mixed tasks;
- Llama-3.1-8B: P/T token count identical on 66/66; P/T/S identical on 57/57 mixed tasks;
- token-count mismatch: 0;
- model inference calls: 0;
- task outcomes observed: 0.

## Final run matrix

| Executor | P neutral | T truthful | S shuffled | Total |
|---|---:|---:|---:|---:|
| Qwen2.5-7B-Instruct | 66 | 66 | 57 | 189 |
| Meta-Llama-3.1-8B-Instruct | 66 | 66 | 0 | 132 |
| **Total** | **132** | **132** | **57** | **321** |

Compared with rejected R68:

- R68: 660 trajectories;
- R70: 321 trajectories;
- removed: 339 trajectories (51.4%).

The reduction does not shrink the primary statistical unit count: Qwen T-P remains 66 paired clusters and Llama T-P remains 66 paired clusters.

## Confirmatory hierarchy

### Qwen primary

`T_truthful - P_neutral`, n=66.

Endpoint: native paired OSInteraction terminal success.

`EFFECT_DETECTED` requires:

1. two-sided exact paired sign test `p < .05`; and
2. the prespecified worst/best technical-missing sensitivity bound excludes zero in the same direction.

Otherwise the state is `NO_EFFECT_DETECTED`.

`NO_EFFECT_DETECTED` means only that no truthful-information increment was resolved. It is **not**:

- equivalence;
- proof of practical smallness;
- proof that only prompt format matters;
- proof that provenance is unused.

### Qwen gate-kept correctness analysis

`T_truthful - S_shuffled`, n=57 mixed-provenance clusters.

This receives confirmatory interpretation only if the Qwen T-P primary first detects an effect. Same-direction exact detection plus technical-missing sensitivity is required before the paper may call the effect correctness-sensitive.

### Llama executor-only replication

`T_truthful - P_neutral`, n=66.

The Llama panel, renderer, hypothesis, statistics, failure rules, and commitment to execute are frozen before any Qwen R70 outcome is opened. Llama may execute after the Qwen seal opens, but the design and run commitment cannot change as a function of Qwen results.

No cross-model pooling.

### Descriptive diagnostics only

- first executable action divergence;
- step-count differences;
- subgroup decompositions.

These cannot rescue a failed terminal primary endpoint.

## Execution staging

### Stage Q

189 Qwen trajectories. No Qwen effect inspection until all scheduled Qwen arms are terminal or prospectively classified technical-missing.

### Stage L

132 Llama trajectories. Its design is frozen before Qwen exposure; it may execute after Qwen analysis because its design and run commitment are non-adaptive.

A global 321-run analysis seal is not required.

## Failure and retry boundary

The scientific boundary is **treatment exposure**, not a durable `STARTED` ledger row.

### Pre-exposure infrastructure failure

Examples:

- Docker/reset failure before treatment-conditioned inference dispatch;
- transport/runtime failure provably before model dispatch.

Policy:

- same unit/arm only;
- fresh reset each attempt;
- maximum 3 total attempts;
- no replacement;
- every attempt logged.

### Post-exposure

Once the treatment prompt is dispatched for inference:

- no rerun;
- native model/environment failure scored by the native evaluator remains a scientific outcome;
- genuine external technical failure becomes `TECHNICAL_MISSING`, not a model failure and not a rerun.

Primary paired reporting includes complete pairs plus a conservative worst/best missing-pair risk-difference bound over the full planned n. A confirmatory conclusion must survive this bound.

## Why no fresh No-Memory / Masked / SOTA memory baseline

The paper's current scientific object is the incremental effect of truthful source-outcome information given fixed retrieved content.

- No-Memory answers whether memory content itself helps; this is a different object.
- Fresh Masked would estimate neutral-field presence relative to field absence; useful context, but unnecessary for T-P identification and unnecessary if the paper does not claim `NO_EFFECT_DETECTED => only prompt format matters`.
- Broad AWM / ReasoningBank / MemRL / other memory-system baselines change content, writers, retrieval, or consolidation and therefore weaken rather than strengthen this exact-content causal comparison.

The baseline family follows the same design principle seen in strong systems papers such as SkillZip Pro: each retained baseline exists because it removes a specific alternative explanation, not because more rows look stronger.

## Current authority

Execution remains CLOSED.

`generated/d2-failure-memory-provenance-r70-semantic-control-r2-execution-hold.json`

keeps false authority for:

- Qwen execution;
- Llama execution;
- GPU;
- analysis;
- PSMG;
- L3;
- paper claim change.

The next gate is a fresh independent R2 pre-execution review of the revised R70/R71 object. Only a later content-addressed authority receipt may open Stage Q/Stage L execution.
