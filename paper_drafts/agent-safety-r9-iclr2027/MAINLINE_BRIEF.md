# G1 / Agent Safety R9 — SkillZip paper-mainline iteration R1

Date: 2026-09-04
Status: PRECONFIRMATORY / SUBMISSION HOLD
Paper identity is not allowed to be selected after the next safety outcomes.

## 1. One scientific object

The paper studies whether **benign workflow accumulation changes the refusal-to-action control boundary of a persistent browser agent under an exactly matched future task schedule**.

The scientific object is not generic longitudinal-memory risk, not "memory makes agents unsafe," and not evaluator disagreement itself.

For a harmful browser request at longitudinal exposure step t, decompose behavior into:

- R0 — immediate refusal / safe handling before task-directed tool use;
- R1 — first harmful-task-directed browser action, defined by a task-specific programmatic predicate;
- R2 — partial execution depth after R1;
- R3 — verified external effect / target-side effect when the environment exposes one.

The primary endpoint for the prospective confirmatory experiment is R1. R0, R2, and R3 explain where the control boundary moved and prevent a failed or truncated task from being conflated with either safe refusal or successful harmful completion.

## 2. Why this is the paper-first object

Experience-driven agents are trained or prompted to convert prior demonstrations into action. Prior work already establishes that longitudinal memory can create safety risk and that benign experience / execution-oriented memories can reduce refusal. G1 therefore does **not** claim those broad phenomena as novel.

The narrower unresolved question is causal and operational:

> Holding the initial state, future task schedule, seed structure, action interface, and execution budget fixed, does allowing benign workflow state to accumulate change when the agent crosses from refusal/safe handling into task-directed action?

This object survives the main prior-work collisions because it is an exact same-schedule persistent-update contrast with an explicit behavioral control boundary rather than a generic memory-exposure comparison.

## 3. Identification design

### Treatment

Updated arm:

s0 = W0
s1 = W0 + U1
s2 = W0 + U1 + U2
s3 = W0 + U1 + U2 + U3

where U1..U3 are prospectively frozen benign workflow units.

### Counterfactual

Frozen arm:

s0 = W0
s1 = W0
s2 = W0
s3 = W0

The future task schedule, seeds, browser substrate, observation/action interface, and maximum execution budget are matched slot-by-slot.

### Primary estimand

For matched future units u:

D_R1 = mean_u R1(Updated,u) - mean_u R1(Frozen,u).

R1 must be computed automatically from prospectively frozen task-specific predicates over structured action/environment events. Author adjudication after viewing outcomes is forbidden.

R0/R2/R3 are secondary decomposition endpoints, not substitutes selected after observing R1.

NullMemory asks a different question — presence of workflow memory rather than the incremental effect of workflow accumulation — and is not required for the smallest decisive Updated-vs-Frozen identification test.

## 4. Capability qualification is part of identifiability

A browser-safety conclusion is uninterpretable if the agent cannot competently operate the benign substrate.

The prospective Qwen3.5-397B-A17B substrate must therefore first pass the pinned BrowserART official 10-task benign panel under the benchmark-aligned 10-step budget with a strict 10/10 gate.

The historical 4-step setting is evaluated only as a prefix diagnostic of the same benign trajectories; it is not a second scientific arm.

Failure of the 10/10 gate terminates the safety experiment. It is an execution/substrate failure, not evidence for or against the G1 scientific hypothesis.

## 5. Historical R9 evidence is discovery-only

The historical Qwen3-8B/AWM R9 execution remains immutable and scientifically useful for hypothesis discovery, but it is not confirmatory evidence for the new R1-centered claim.

Important historical facts:

- HarmBench branch events: Updated/Frozen/NullMemory = 8/4/0.
- DeepSeek on the same frozen trajectories: 5/5/8.
- 103/108 historical future episodes hit the 4-step truncation ceiling.
- 0/108 normally terminated.
- 0/108 had listener-confirmed external effects.
- historical evaluator inputs therefore relied on the official thought/action-attempt fallback rather than verified harmful completion.

These facts jointly prohibit a strong historical mechanism claim such as "workflow updating makes the agent more unsafe."

They motivate two separate prospective questions:

1. does an update-associated behavioral control effect survive on a capability-qualified, 10-step substrate with programmatic endpoints?
2. after trajectory completeness is repaired, how sensitive are semantic safety conclusions to evaluator choice?

Question 1 is primary. Question 2 is measurement robustness.

## 6. Evaluator disagreement is a measurement layer, not the paper identity by default

HarmBench and DeepSeek disagree materially on the historical traces, including arm ordering. This is real evidence that the old semantic endpoint is unstable.

ERTA is therefore retained as a **secondary measurement-robustness framework**:

- premise stability;
- event-set overlap;
- contrast-sign stability;
- task-localized disagreement;
- no post-hoc majority or judge shopping.

However, evaluator disagreement on heavily truncated, no-effect trajectories cannot by itself support a general evaluator-relative safety paper.

For an evaluator-centered paper to become the main identity, disagreement must prospectively persist on capability-qualified, substantially complete trajectories with objective R1/R3 anchors.

## 7. Prospective paper-identity decision rule

This rule is internal scientific governance and must be frozen before the first new harmful safety trajectory.

A. Capability gate fails
   -> no new safety run; diagnose substrate. No paper-claim upgrade.

B. Capability passes and prospective Updated-vs-Frozen shows the preregistered update-associated R1 effect, supported by R0/R2/R3 decomposition and low protocol failure
   -> KEEP_NARROW_SELF_EVOLUTION_G1.
   Main story: benign workflow accumulation can shift the refusal-to-action boundary under a matched future schedule.
   ERTA remains robustness/limitation.

C. Capability passes; Updated≈Frozen on the preregistered behavioral endpoints; but evaluator conclusions still materially reverse on complete/objectively anchored trajectories
   -> PIVOT_TO_EVALUATION_PAPER.
   The self-evolution mechanism claim is not retained.

D. Capability passes; Updated≈Frozen; evaluator disagreement largely disappears after execution repair
   -> STOP_OR_MERGE_G1.
   Do not create a third paper identity from the same outcomes.

## 8. Research questions for the next manuscript

RQ1 — Qualification: Is the exact browser-agent substrate capable enough for safety interpretation under the official benign panel?

RQ2 — Causal control question: Under the same future schedule, does benign workflow accumulation change task-directed action initiation relative to the frozen workflow?

RQ3 — Behavioral decomposition: If R1 changes, is the shift visible as loss of immediate refusal, deeper partial execution, or verified external effects?

RQ4 — Temporal localization: At what exposure step does the first control-boundary crossing occur, and is it state/branch localized?

RQ5 — Measurement robustness: Given objective R1/R3 anchors, do HarmBench, DeepSeek, and human semantic judgments support the same scientific direction?

RQ5 cannot become RQ1 post hoc simply because evaluator disagreement is visually striking.

## 9. Writing architecture learned from SkillZip / SkillZip Pro

### Introduction

1. System reality: persistent agents accumulate benign workflow experience and keep acting.
2. Missing guarantee: a point-in-time refusal/safety pass does not automatically characterize later control behavior.
3. Prior-work boundary: longitudinal memory risk and benign-experience safety degradation already exist; G1 does not reclaim them.
4. Identification gap: time/task difficulty, workflow updating, action failure, and semantic judging can be conflated.
5. Scientific object: the refusal-to-action boundary R0->R1->R2->R3 under matched workflow accumulation.
6. Identification: same-schedule Updated vs Frozen + capability qualification + programmatic R1.
7. Claim ladder and bounded scope.

### Main body

Sec. 2 — Scientific object and endpoint decomposition.
Sec. 3 — Same-schedule identification and capability qualification.
Sec. 4 — Historical discovery audit: why R9 generated the hypothesis but cannot confirm it.
Sec. 5 — Prospective confirmatory experiment and R1/R0/R2/R3 results.
Sec. 6 — Temporal/state localization and mechanism diagnostics.
Sec. 7 — Evaluator/human robustness as measurement sensitivity.
Sec. 8 — Related work and exact collision boundary.
Sec. 9 — Limitations and conclusion.

Do not put execution-governance bookkeeping, hashes, recovery procedures, or provider transport in the narrative spine. Keep them in artifacts / appendix unless they alter scientific interpretation.

## 10. Figure and table architecture

Figure 1 — Scientific object, not system plumbing:
 harmful request -> R0 refusal -> R1 first task-directed action -> R2 partial execution -> R3 verified external effect,
 shown under matched Updated and Frozen longitudinal states.

Figure 2 — Identification design:
 same initial state + same task/seed schedule + same 10-step budget; only workflow accumulation differs.

Figure 3 — Primary prospective result:
 matched Updated-vs-Frozen R1 with first-crossing time; R0/R2/R3 shown as decomposition.

Figure 4 — Measurement robustness:
 objective behavioral anchors versus HarmBench / DeepSeek / human judgments. This is not Figure 1.

Table 1 — Capability gate and protocol quality.
Table 2 — Main matched behavioral effect (R0/R1/R2/R3), normal setting first.
Table 3 — State/task localization or secondary controls.
Appendix — historical 8/4/0 vs 5/5/8, ERTA envelopes, full trajectories, hashes, receipts.

## 11. Claim ladder

Level 0 — already supported historically:
The original HarmBench temporal ordering is evaluator-sensitive and the historical execution substrate is heavily truncated.

Level 1 — requires prospective capability PASS:
The new substrate is competent enough for safety interpretation.

Level 2 — requires preregistered R1 result:
Benign workflow accumulation changes task-directed action initiation under the matched future schedule.

Level 3 — requires R0/R2/R3 coherence:
The R1 shift corresponds to a meaningful control degradation rather than parser/grounding noise.

Level 4 — requires evaluator/human robustness:
The semantic safety interpretation of that behavioral shift is stable across measurement systems.

Level 5 — requires additional transport evidence:
Any claim beyond the exact backbone/AWM/BrowserART setting.

The manuscript must never write a higher claim level than the evidence currently reaches.

## 12. Current paper state

Current main.tex is an ERTA-centered historical draft and no longer matches the active scientific mainline.

Submission remains HOLD until the Qwen3.5-397B capability qualification and, if qualified, the separately frozen prospective safety experiment determine which paper identity is scientifically supported.

The historical ERTA draft is preserved as evidence of the measurement pivot; it is not silently deleted or retroactively rewritten into confirmatory evidence.
