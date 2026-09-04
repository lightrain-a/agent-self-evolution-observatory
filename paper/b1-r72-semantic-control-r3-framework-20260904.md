# B1 R72/R73 — Semantic-Control R3 Framework After Fresh R2 Review

Date: 2026-09-04  
Status: ZERO-PROVIDER / EXECUTION HOLD  
Paper: `D2-PAPER-FAILURE-MEMORY-PROVENANCE`

## Lineage

- R68: 660-trajectory five-arm proposal; independent review returned `REDUCE_OR_REDIRECT`.
- R70/R71: reduced 321-trajectory P/T/S + executor-replication protocol; fresh independent R2 review returned `REVISE_R70_BEFORE_EXECUTION`.
- R72/R73: versioned successor that fixes only the two R2 blockers. The panel, executors, arms, and 321-trajectory workload do not change.

R70 remains immutable historical evidence. R72 binds the exact R70 protocol file and receipt that R2 reviewed.

## R2 verdict

Fresh GPT-5.6 Sol + Extra High project review accepted:

- Qwen `T_truthful - P_neutral` causal target;
- representation/type/token-footprint matching;
- count-preserving shuffled correctness control;
- deleting fresh No-Memory / Masked / broad SOTA memory-system baselines;
- Llama P/T-only executor replication;
- n=66 per executor;
- the 321-trajectory matrix as minimal for the three declared information targets;
- treatment-exposure retry boundary and up to three logged pre-exposure attempts.

It found exactly two remaining blockers.

## Fix 1 — exact-test robustness under technical missingness

R70 required:

- complete-case exact paired sign-test p<.05; and
- a worst/best paired-risk-difference missing-pair bound excluding zero.

R2 showed this can still falsely declare an effect. Example:

- observed T-only/P-only discordances = 6/0;
- one technical-missing planned pair;
- complete-case exact p = .03125;
- worst-case RD remains positive: 5/66;
- but the missing pair can be P-only, producing 6/1 and exact p = .125.

R73 now enumerates **every admissible completion** of the missing pairs into left-only, right-only, or concordant outcomes and takes the maximum exact two-sided sign-test p-value.

A confirmatory detection requires both:

1. the paired-RD worst/best bound excludes zero in the observed direction; and
2. the worst-case exact sign-test p-value remains <.05.

This same rule applies to:

- Qwen T-P primary;
- gate-kept Qwen T-S correctness claim;
- any Llama result labelled successful executor replication.

The reviewer counterexample is encoded as an automated regression test and now correctly returns `effect_detected = false`.

## Fix 2 — exact S_shuffled treatment realization frozen

For each of the 57 mixed-provenance units, R72 content-addresses:

- truthful S/F code sequence;
- truthful-sequence SHA;
- exact shuffled S/F code sequence;
- shuffled-sequence SHA.

The protocol also freezes:

- deterministic algorithm;
- seed `B1-R70-SHUFFLE-20260904`;
- 57-row assignment object SHA.

R73 rebinds the original R54 memory content/outcomes and rejects execution if the recomputed S sequence differs from the protocol.

Pre-exposure retries render the treatment context once outside the retry loop, so every retry uses the identical frozen S treatment.

## Workload remains unchanged

| Executor | P neutral | T truthful | S shuffled | Total |
|---|---:|---:|---:|---:|
| Qwen2.5-7B-Instruct | 66 | 66 | 57 | 189 |
| Meta-Llama-3.1-8B-Instruct | 66 | 66 | 0 | 132 |
| **Total** | **132** | **132** | **57** | **321** |

No new baseline, task, executor, or substrate is introduced.

## Scientific interpretation remains unchanged

Primary:
- Qwen T-P, n=66.

Gate-kept mechanism:
- Qwen T-S, n=57, confirmatory only if T-P first detects an effect.

Executor-only replication:
- Llama T-P, n=66, frozen before Qwen exposure and reported separately.

Diagnostics:
- first action / steps / subgroups remain descriptive.

`NO_EFFECT_DETECTED` remains an inconclusive/no-resolved-increment state, not equivalence, practical smallness, prompt-format-only proof, or provenance irrelevance.

## Current gate

Execution remains CLOSED:

`generated/d2-failure-memory-provenance-r72-semantic-control-r3-execution-hold.json`

All execution/analysis/GPU/PSMG/L3/paper-claim authorities remain false.

The next and only gate before any provider execution is a fresh independent R3 pre-execution review of the two R2 repairs. No experiment should run before R3 PASS and a separate content-addressed execution authority is generated.
