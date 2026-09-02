# E2-R17 Single-Case Exact-Replay Mechanism Lesson

Date: 2026-09-02
Status: **DEVELOPMENT LESSON / ZERO FOLLOWUP AUTHORITY**

## What was tested

The single-case stream `e1-tsr-00` produced an initially surprising S1 result: the fresh First-Fail state scored 17/18 while contemporaneous WIN-C scored 13/18. Frozen-state remeasurement of that exact learned pair remained positive twice (15/18 vs 14/18; 16/18 vs 12/18), so the strong S1 state was not merely one lucky evaluator draw.

However, this did not establish that First-Fail evidence reliably produces a strong state. To isolate updater state generation, we reconstructed the exact S1 rendered evidence for both WIN-C and First-Fail and required all 16 rendered packet SHA-256 values to match the original S1 packets before provider I/O. Two new contemporaneous updater realizations were then generated and measured.

A deterministic authorization-schema failure occurred after the first pair of updater states and before any heldout provider I/O. The two rep1 states were preserved, rep2 states were generated under updater-only recovery, and all four frozen states were evaluated under measurement-only child authorities. No completed updater state was replayed.

## Final exact-evidence replication result

Replicate 1:

- WIN-C: 15/18 = 0.8333
- First-Fail: 15/18 = 0.8333
- difference: 0

Replicate 2:

- WIN-C: 12/18 = 0.6667
- First-Fail: 11/18 = 0.6111
- difference: -1/18

Mean First-Fail minus WIN-C difference across the two new updater realizations:

`-0.02778`

Frozen gate result:

`FIRST_FAIL_EXACT_EVIDENCE_UPDATER_REPLICATION_FAIL_STATE_GENERATION_VARIANCE`

## Mechanism interpretation

The evidence-treatment explanation is now too weak as the primary account.

The same byte-identical S1 rendered evidence can produce materially different learned skills under the hosted free-form updater. The original strong S1 First-Fail state is real and repeatedly measurable, but its advantage does not reproduce when the updater is re-realized from exactly the same evidence.

Therefore the current bottleneck is better described as:

`useful diagnostic evidence -> high-variance free-form state generation -> unstable downstream utility`

rather than simply:

`wrong rejected witness -> bad downstream utility`.

This also explains why Progress-Fail / Progress-Contrast did not rescue S1: improving evidence selection cannot guarantee an effective learned state when the writer itself has high outcome-relevant variance.

## Useful content of the strong state

The strong S1 First-Fail skill added a compact, task-general execution-completion repair:

- inspect -> read -> compute -> write -> save -> verify;
- do not stop after inspection;
- retry malformed/failed tool calls with a clean command;
- verify the saved workbook after writing.

The two exact-replay First-Fail states contained semantically similar ideas but varied in verbosity and incidental rules. This motivates testing whether a constrained/minimal repair representation can preserve the shared completion semantics while suppressing free-form updater variance.

This textual comparison is development evidence only and does not establish which clause causally produced the strong state.

## What not to do next

Do not:

- rerun Progress-Fail merely to obtain a positive number;
- add updater samples until one is successful and then report the selected sample;
- select a writer output using heldout task performance;
- touch the pre-reserved E3 confirmatory streams;
- add a second backbone or public benchmark;
- reinterpret the original S1 strong state as a reproducible First-Fail treatment effect.

## Highest-information next micro-experiment

The next single-case development experiment should target **state-generation stabilization**.

Use the same `e1-tsr-00` development stream and the same initial skill. Construct a small, pre-frozen constrained repair ladder whose states are deterministic and do not depend on a sampled free-form updater output:

1. `G0 BASE`: unchanged initial/WIN skill.
2. `G1 VERIFY`: add only an explicit save-and-reload verification guard.
3. `G2 COMPLETE`: add the canonical inspect -> read -> compute -> write -> save -> verify completion loop.
4. `G3 COMPLETE+RECOVER`: add the completion loop plus immediate retry-after-tool-error rule.

All text must be frozen before any new heldout measurement. The ladder is development-only and is intended to identify which minimal structural repair reproduces the useful behavior of the strong S1 state.

Recommended screen:

- one fresh measurement replicate for all four frozen states;
- same 18 development heldout tasks;
- no updater/provider calls for state generation;
- 72 heldout measurement units.

If one non-baseline arm exceeds G0 by at least 1/18, select the **simplest** passing arm (`G1 < G2 < G3`) and remeasure only G0 plus that arm twice more before declaring a single-case stabilization success.

A successful stabilization still remains development evidence and must later be validated on another V2 development stream before any untouched E3 confirmation.
