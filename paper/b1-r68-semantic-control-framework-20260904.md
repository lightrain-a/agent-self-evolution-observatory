# B1 R68/R69 — Fresh Semantic-Control Experiment Framework

Date: 2026-09-04
Status: ZERO-PROVIDER / PRE-EXECUTION HOLD
Paper: `D2-PAPER-FAILURE-MEMORY-PROVENANCE`

## Scientific goal

Test whether truthful source-outcome information adds value beyond a format-matched field when retrieved memory content is identical.

This is a new prospective object. It does not reuse the observed R56/R61 32-task outcomes as primary data.

## Fresh panel

R54 originally froze 106 outcome-blind eligible fresh OSInteraction skill-signature clusters before any validation treatment outcome.

Historical use:
- first 32 eligible clusters: R56/R61 primary A/B;
- next 8 eligible clusters: R55/R60 utilization.

R68 uses **all remaining 66 eligible clusters**. The selection rule is therefore deterministic and exhaustive: `eligible[40:]`. There is no new ranking, task replacement, outcome filtering, or tuned cutoff.

Frozen representative-ID SHA256:

`7c2b84aee347faba6d369abb403eb3a25afb164b8f5c6800ba867c25d1017187`

The panel has zero overlap with the historical 32 primary + 8 utilization units.

## Five-arm baseline family

| Arm | Memory content | Explicit field | Value | Main role |
|---|---|---|---|---|
| `N0_no_memory` | none | none | — | contextual no-memory baseline |
| `M1_masked` | frozen retrieved content | omitted | — | same-content masked baseline |
| `P2_unknown` | identical | present | `UNKNOWN` | format/prompt-surface placebo |
| `T3_truthful` | identical | present | truthful bool | semantic-information treatment |
| `R4_reversed` | identical | present | complemented bool | correctness-sensitivity control |

`P2_unknown`, `T3_truthful`, and `R4_reversed` use the same field key and row structure. `T3_truthful` and `R4_reversed` both use boolean values. Retrieval membership/order and memory content are frozen for `M/P/T/R`.

## Prespecified contrasts

Primary:
- `T3_truthful - P2_unknown`: incremental terminal value of truthful source-outcome information beyond a format-matched field.

Secondary:
- `T3_truthful - R4_reversed`: correctness sensitivity;
- `P2_unknown - M1_masked`: generic field-presence / prompt-surface effect;
- `M1_masked - N0_no_memory`: contextual value of the retrieved content;
- `T3_truthful - M1_masked`: fresh replication of the legacy total explicit-field contrast.

Primary endpoint: paired native OSInteraction terminal success.

Secondary diagnostics:
- normalized first-executable-action divergence;
- paired step-count difference.

First-action divergence alone may not be interpreted as proof of semantic provenance reasoning.

## Executors

- Primary executor: Qwen2.5-7B-Instruct.
- Executor-only replication: Meta-Llama-3.1-8B-Instruct.

The source bank, retriever, task surface, renderer, and evaluation substrate are shared. Cross-model estimates are reported separately and are never pooled.

## Planned workload

- 66 independent fresh clusters / executor;
- 5 arms / cluster;
- 2 executors;
- **660 planned trajectories**.

Temperature remains 0.0. Every arm gets a fresh OSInteraction Docker reset. Retrieval is never rerun between arms.

## Analysis freeze

No effect inspection is allowed until all 660 scheduled arm runs are terminal.

For each model and contrast:
- paired risk difference;
- two-sided exact sign test over discordant pairs;
- 100,000-resample paired percentile bootstrap CI;
- conservative sparse-discordance paired-risk-difference interval using Bonferroni-combined 97.5% Clopper-Pearson component intervals.

No equivalence claim is allowed without a separately prospective equivalence procedure.

## Failure / resume rules

- schedule is frozen before execution;
- no task replacement or panel shrinkage;
- no arm change after first exposure;
- no new model after first exposure;
- once an arm is durably `STARTED`, execution failure is exposed and receives no ad-hoc retry;
- resume may continue only from the never-started suffix;
- partial outcomes cannot change the protocol or open analysis.

## Current authority

`generated/d2-failure-memory-provenance-r68-semantic-control-execution-hold.json`

is intentionally closed:
- semantic-control execution: false;
- Qwen execution: false;
- Llama execution: false;
- GPU authority: false;
- PSMG claim: false;
- L3 claim: false;
- paper-claim change: false.

The next gate is an independent pre-execution methodology review of the frozen R68 objects. Only a later content-addressed authority object may open R69 execution.

## Key implementation files

- `research_pipeline/failure_memory_semantic_control_r68.py` — zero-provider panel/renderer/protocol freeze.
- `research_pipeline/failure_memory_semantic_control_r69.py` — fail-closed execution and complete-only analyzer.
- `research_pipeline/test_failure_memory_semantic_control_r68.py` — renderer/panel/authority regression tests.
- `generated/d2-failure-memory-provenance-r68-semantic-control-panel.json`
- `generated/d2-failure-memory-provenance-r68-semantic-control-renderer-audit.json`
- `generated/d2-failure-memory-provenance-r68-semantic-control-protocol.json`
- `generated/d2-failure-memory-provenance-r68-semantic-control-execution-hold.json`

## Static validation command

The execution runner supports `--validate-only`; this validates the protocol, panel, parent manifests, and bound R54 frozen retrieval without touching a model.

Current result:

`R69_STATIC_PREFLIGHT_PASS_EXECUTION_STILL_CLOSED`
