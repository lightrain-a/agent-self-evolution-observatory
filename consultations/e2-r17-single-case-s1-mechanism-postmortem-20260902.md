# E2-R17 Single-Case S1 — Mechanism Postmortem

Date: 2026-09-02
Status: **DEVELOPMENT_ONLY / POST-OUTCOME MECHANISM DIAGNOSIS / ZERO NEW EXECUTION AUTHORITY**

## Frozen S1 result

The development-only single-case S1 completed 4 learned states and 72/72 held-out measurements with zero technical failures. The frozen analyzer returned:

`S1_SIGNAL_FAIL_STOP_NO_S2`

Success counts over the same 18 held-out tasks:

- WIN-C: 13/18 = 0.7222
- First-Fail: 17/18 = 0.9444
- Progress-Fail: 14/18 = 0.7778
- Progress-Contrast: 14/18 = 0.7778

The frozen S1 candidate tie-break selected Progress-Fail because Progress-Fail and Progress-Contrast tied, but the candidate was 3/18 worse than First-Fail. Therefore the preregistered S1 gate correctly blocks S2.

This result rejects the simple development hypothesis that a failure branch closer to the successful winner in execution progress is necessarily a more useful learning witness.

## What the task-level outcomes show

Relative to WIN-C, First-Fail fixed four held-out tasks that WIN-C missed:

- `r17-b4-fmv-p8`
- `r17-b4-ioc-p6`
- `r17-b4-ska-p8`
- `r17-b4-tsr-p6`

and introduced no new held-out failure relative to WIN-C. Its only failed held-out task was `r17-b4-ioc-p1`, which WIN-C also failed.

Progress-Fail lost three tasks that First-Fail solved:

- `r17-b4-fmv-p8`
- `r17-b4-msp-p0`
- `r17-b4-ska-p4`

Progress-Contrast fixed `r17-b4-ioc-p1` relative to First-Fail but lost four First-Fail successes:

- `r17-b4-msp-p0`
- `r17-b4-msp-p8`
- `r17-b4-ska-p4`
- `r17-b4-ska-p5`

The losses are cross-family; they do not support a simple same-family transfer account.

## Skill-patch diagnosis

The frozen First-Fail skill patch generalized the failure evidence into broad procedural safeguards:

- complete the full `inspect -> read -> compute -> write -> save -> verify` pipeline;
- do not stop after workbook inspection;
- after a failed tool invocation, retry immediately with a clean minimal command;
- reload the saved workbook and verify written cells.

By contrast, the Progress-Fail / Progress-Contrast patches included more local endpoint rules, including a specific Python rounding convention, while still adding a generic completion checklist. In this S1 replicate, that additional specificity did not improve future success and coincided with losses on several unrelated MSP/SKA held-out tasks.

This suggests a different mechanism than the pre-S1 near-miss hypothesis:

> Raw witness proximity is not the target. The useful intermediate variable may be the **generality and correctness of the repair rule distilled by the updater from the witness**.

An early failure can be more useful than a near-miss when it exposes a high-level bottleneck (for example, premature termination after inspection) that transfers broadly. A near-miss can be less useful when it encourages a narrow or brittle endpoint rule.

## Why the 17/18 result is not yet a stable method effect

The same `e1-tsr-00` stream had four historical V2 replicate differences:

`[-2/18, -3/18, +2/18, +2/18]`

whose mean was approximately -0.0139. The new S1 fresh First-Fail minus WIN-C difference is +4/18.

Therefore the new 17/18 versus 13/18 result is scientifically useful but cannot be interpreted as stable evidence that First-Fail is truly superior on this stream. Hosted evaluation stochasticity and updater stochasticity were already known nuisance sources.

The cheapest next question is not another updater comparison. It is:

> Holding the newly learned First-Fail and WIN-C skill states fixed, does First-Fail remain better under fresh repeated held-out measurements?

That separates **measurement/evaluator noise** from **learned-state quality** without spending any additional updater calls.

## Next object

Create a development-only frozen-state stability check:

`E2-R17-SINGLE-CASE-FIRST-FAIL-FROZEN-STATE-STABILITY-20260902`

Use exactly the S1 WIN-C and First-Fail learned skill states. No updater calls. Run two additional fresh held-out measurement replicates on the same 18 development held-out tasks, interleaved across the two states.

Prospective gate based only on the two new replicates:

- each new replicate must have `J(First-Fail) - J(WIN-C) >= 1/18`;
- mean of the two new replicate differences must be at least `1/18`;
- zero unresolved technical failures.

The original S1 replicate is descriptive context only and is not used to satisfy the new stability gate.

If this passes, the First-Fail skill state becomes a credible mechanism asset for studying **repair-rule abstraction**. If it fails, the 17/18 S1 result is classified as measurement-instability evidence and no method promotion follows.

## Authority

This postmortem grants no provider, updater, evaluator, second-backbone, E3, paper, or submission authority.
