# B1 R76 — Llama Discordant-Task Repeatability Diagnostic

Date: 2026-09-05  
Role: post-hoc repeatability diagnostic only  
Primary R72/R73 inference: unchanged

## Question

The old R61 Llama A/B experiment had four terminal-discordant task IDs despite equal aggregate success counts (17/32 vs 17/32):

- 125: A success / B fail
- 136: A fail / B success
- 193: A fail / B success
- 327: A success / B fail

Because users may naturally suspect sampling randomness, R76 asks whether those four pair patterns reproduce under the exact historical executor substrate.

## Important decoding fact

R61 used local `Meta-Llama-3.1-8B-Instruct` with:

- `temperature = 0.0`
- `do_sample = false`
- greedy generation through the frozen local runtime

Therefore the historical flips were never ordinary nonzero-temperature sampling events.

## Exact-substrate rerun

R76 used the same:

- content-addressed Llama model artifact (`8071d53a...`)
- tokenizer and float16 runtime path
- R61 A/B renderer
- frozen R54 retrieval content/order
- system prompts (SHA checked against historical frozen plan)
- parser/evaluator
- `local-os/default:latest` Docker image identity
- fresh OSInteraction reset per arm
- local loopback model route

The historical MemRL checkout contained two unrelated untracked temp files, so it was not reused. R76 created a new clean detached worktree at the exact same `c1b322ca...` commit and rechecked the pinned source-file hashes and validation split before exposure.

## Prespecified sequential rule

Phase 1:

- four historical discordant tasks
- both A/B arms
- one fresh exact rerun per arm
- 8 new trajectories total

Only if a task failed to reproduce its historical A/B terminal pair pattern would that task expand to five total fresh repetitions per arm.

## Result

| Task | Historical A/B | R76 A/B | Pair reproduced? | Historical steps A/B | R76 steps A/B |
|---|---|---|---|---|---|
| 125 | success / fail | success / fail | yes | 10 / 16 | 10 / 16 |
| 136 | fail / success | fail / success | yes | 6 / 6 | 6 / 6 |
| 193 | fail / success | fail / success | yes | 10 / 6 | 8 / 6 |
| 327 | success / fail | success / fail | yes | 16 / 4 | 16 / 4 |

Aggregate repeatability:

- terminal arm outcomes: **8/8 reproduced**
- terminal pair patterns: **4/4 reproduced**
- first executable actions: **8/8 reproduced**
- step counts: **7/8 reproduced**
- full normalized action sequences: **7/8 reproduced**

The only full-trajectory difference was Task 193 A. Its first six normalized actions matched the historical run, then the rerun terminated in 8 rather than 10 steps. The terminal outcome remained failure.

## Interpretation

R76 does not support a temperature-sampling explanation for the historical flips. The executor was greedy in both R61 and R76, and all four post-hoc pair patterns reproduced.

The most defensible interpretation is narrower:

> The four historical flips are consistent with stable task-specific prompt-conditioned policy sensitivity near the executor capability boundary. A small metadata difference can place the closed-loop agent on a different action/recovery path, while limited runtime variation can still occur after the paths begin to unfold.

This is not evidence that all task-level effects are deterministic, and it is not a population estimate. The four tasks were selected after observing historical discordance, so R76 must remain a post-hoc mechanism/repeatability diagnostic.

## No expansion

Because all four pair patterns reproduced, the prespecified Phase-2 repeated-run expansion was not triggered. No additional trajectories are required by R76.

Raw R76 root on host 231:

`/data/wyt/b1-memrl-r76-llama-discordant-repeatability`

Canonical summary receipt:

`generated/d2-failure-memory-provenance-r76-llama-discordant-repeatability.json`
