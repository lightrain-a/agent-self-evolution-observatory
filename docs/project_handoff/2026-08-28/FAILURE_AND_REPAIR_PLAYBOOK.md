# Failure and Repair Playbook

This file preserves the most reusable failure patterns learned in the project so a new project does not repeat them.

## 1. Main failure: losing the scientific question

### Symptom
As an agent performs more experiments, locally interesting results accumulate and gradually redefine the paper. Later writing then treats off-mainline results as if they were central evidence.

### Repair
Maintain an explicit paper invariant:

```text
scientific question
core claim(s)
required evidence
forbidden drift
```

Before every new stage, map the proposed run to one core claim. If there is no direct mapping, park it as exploratory rather than letting it mutate the main line.

When an old result is declared off-mainline, mark it as **revoked from current narrative authority** without deleting the artifact. Preserve it for audit/history, but do not let future synthesis tools automatically count it as current evidence.

## 2. “More experiments” mistaken for “more depth”

### Symptom
The project accumulates extra metrics, model rows, thresholds, or datasets, but the strongest reviewer objection is unchanged.

### Repair
Depth should come from sharper causal/mechanistic discrimination:
- specify competing explanations;
- derive different predictions;
- run a controlled intervention or boundary test;
- state a regime law or exact claim boundary;
- let evidence change the scientific model.

Breadth is valuable after the core mechanism is identifiable.

## 3. Niche substrate / weak audience bridge

### Symptom
The scientific idea may be valid, but nearly the entire experiment depends on a method that is unpublished, obscure, or unfamiliar to the target venue.

### Risk
Reviewers may interpret the work as a local patch to a niche method rather than a general scientific contribution.

### Repair
- abstract the scientific object away from the niche implementation;
- survey strong top-venue methods that instantiate the same object;
- prefer public benchmark/code/checkpoints;
- run a pilot on a broader substrate;
- keep the original substrate as one case study if useful, not the sole foundation.

## 4. Stage ladder / evaluation coarsening artifact

### Symptom
An effect appears stronger/weaker at successive evaluation stages, but the stages also change the metric or aggregation granularity.

### Reviewer attack
“You are just reporting the same outcome under coarser/finer metrics.”

### Repair
Use a controlled stage-specific intervention, matched trajectory, fixed evaluator, or another design that distinguishes pipeline location from evaluation transformation.

Claim “operational localization” unless a true mechanism intervention supports stronger wording.

## 5. Multi-factor treatment confound

### Symptom
A branch simultaneously changes reward semantics, reflection prompt, memory-write instructions, model, decoding, or other factors.

### Risk
The result cannot support an atom-level causal claim.

### Repair
Factor the intervention. Change one interpretable variable at a time, or explicitly describe the treatment as a bundled system intervention and narrow the claim.

## 6. Broken writer / substrate mistaken for scientific null

### Symptom
The memory writer fails to materialize valid artifacts, imports require hidden credentials, or runtime dependencies fail before the intended intervention occurs.

### Repair
Classify as execution/substrate failure first. Prove intervention realization and writer artifact health before interpreting missing downstream effect as principle evidence.

## 7. Receipt/metadata inflation

### Symptom
A JSON receipt says PASS, test metadata exists, or a dataset publishes query units, and the system treats that as behavioral evidence or execution authority.

### Repair
Trace to the exact primary artifact and required fields. For behavioral claims, check per-case outcomes/trajectories and replay provenance. Authority must be explicitly granted by the corresponding gate.

## 8. Stale “current state” pollution

### Symptom
A file named `current-*` or an old chat recap is treated as the live state even after newer dated artifacts exist.

### Repair
Use `CURRENT_STATE_RECOVERY.md`: compare timestamps, source revisions, object identity, and reconciliation authority. Do not trust filenames.

## 9. Outcome-conditioned guard/threshold shopping

### Symptom
After seeing results, thresholds, task filters, guard rules, metrics, seeds, or exclusions are repeatedly changed until the desired conclusion appears.

### Repair
Preserve the original outcome; label post-hoc exploration; diagnose the failure; freeze one justified repair; run it as a new confirmatory version.

## 10. Simple baseline absorbs the gain

### Symptom
A sophisticated mechanism appears useful until a simple/common baseline achieves the same effect.

### Repair
Treat this as scientific information. Determine whether:
- the observable was too weak;
- the proposed mechanism was unnecessary;
- the paper should narrow to a regime where the mechanism matters;
- the contribution is actually a diagnostic/boundary result rather than a new method.

Never hide the simple baseline.

## 11. Theory/diagnostic not behaviorally validated

### Symptom
A mathematically attractive construct predicts or characterizes something, but it has not been tested against actual behavior.

### Repair
Call it a diagnostic/theoretical characterization, not a validated repair mechanism. Add the smallest behavioral validation that can falsify its prediction before elevating the claim.

## 12. External-validity overreach

### Symptom
Evidence comes from one writer, one backbone, one benchmark family, synthetic examples, or a bounded released artifact, but the paper speaks generically about agents/self-evolution/safety.

### Repair
Scope the claim to the tested substrate. Expand only with independently motivated replication. Make limitations an explicit scientific boundary, not a footnote apology.

## 13. “HOLD” treated as unfinished PASS

### Symptom
Pressure to complete a paper causes an evidence hold to be described as nearly resolved or implicitly positive.

### Repair
Treat HOLD as a terminally valid current state. State exactly what evidence would reopen it. Do not execute or claim beyond the frozen authority.

## 14. Agent/model consensus mistaken for evidence

### Symptom
Several reviewer models agree on a plan/claim and that agreement is treated as validation.

### Repair
Use model consultations to generate objections, alternative hypotheses, and experiment designs. Scientific belief should update from admissible evidence, not reviewer-model vote counts.

## 15. Recovery template after any important failure

Create a compact record:

```text
failed experiment/design:
expected prediction:
observed outcome:
realization check:
leading failure layers (1–3):
evidence distinguishing those layers:
simplest competing baseline/explanation:
single-variable repair:
what would falsify the repair:
claim status before/after:
mainline / exploratory / revoked-from-narrative:
lesson added to system:
```

This record prevents the same failure from being rediscovered in later sessions and prevents invalid evidence from silently returning during paper writing.
