# Result Analysis and Distillation

Tags: #ResearchOS #experiment #result-analysis #memory #failure-asset #discovery-lesson

## Core rule

A completed run is **not** a completed scientific iteration.

The minimum closed loop is:

`execution artifact -> result analysis -> failure-layer / claim interpretation -> next scientific routing -> reusable memory -> system regression`

A table, p-value, plot, run receipt, or terminal status records **what happened**. It does not by itself establish **what the result means**.

## Required result-analysis contract

Before a registered result may be treated as distilled terminal evidence, record all of the following:

1. **Observed findings bound to evidence.** State the measured facts and exact receipts/artifacts.
2. **Estimand / scientific object.** Name what variable, intervention, mechanism, or measurement the result actually identifies.
3. **Positive implication.** State what the evidence supports.
4. **Negative boundary.** State what remains unproven or is contradicted.
5. **Strongest alternative explanation.** Give the strongest same-information explanation and its disposition.
6. **Typed failure layer.** For HOLD/STOP, locate the failure at `execution`, `experiment_identifiability`, `optimization`, `operationalization`, `method_realization`, `assumption_scope`, or `core_principle`.
7. **Does-not-imply boundary.** Explicitly prevent a lower-layer failure from becoming a method-effect, whole-paper, or principle failure.
8. **Next action + reusable lesson.** Route the paper/experiment and compile a precheck that future research can retrieve.

If these fields are absent, the result is **observed but not distilled**.

## Separation rules exposed by C1

The C1 reward→memory study produced three reusable separations.

### 1. Persistent-state divergence != behavioral authority

A same-trajectory reward-branch intervention robustly changes durable memory, but natural downstream propagation can attenuate at retrieval, action uptake, or terminal outcome. Therefore persistent-update studies should measure the chain stage by stage:

`write/state -> exposure -> uptake/action -> outcome`

Do not use a large state-distance metric as a substitute for downstream behavioral effect.

### 2. Evidence location != semantic validity != authority

An exact source span or high-similarity anchor makes a claim auditable; it does not determine whether the evidence supports or contradicts the claim. Even semantic support does not automatically grant behavioral authority.

Keep three separate states:

`located / unlocated`

`SUPPORTED / CONTRADICTED / UNVERIFIABLE`

`authority granted / authority withheld`

A locator, embedding similarity, treatment label, terminal reward, or downstream outcome cannot silently skip the validity layer.

### 3. Qualification/support STOP != method-effect failure

If a proposed method requires a validity signal that cannot be independently qualified before execution, STOP/MERGE the **current realization** rather than inventing a verifier after seeing the failure.

That STOP does not imply:

- the unrun method effect is negative;
- the underlying phenomenon is false;
- independently established measurement/mechanism evidence is invalid;
- the method family is globally impossible.

The paper may legitimately change archetype—for example from mechanism→intervention to identification/measurement—without losing valid evidence.

## Memory projection

Every distilled terminal result may emit zero-authority institutional memory:

- **Failure Asset:** a layer-typed reusable precheck for the failure mode;
- **Discovery Lesson:** a cross-project scientific or methodological separation with an explicit reopen condition;
- **Paper routing guidance:** how the result changes contribution hierarchy or paper archetype without changing scientific authority.

Memory is context, not a verdict. It cannot authorize ProblemGate, Method, Experiment, provider calls, GPU use, claim expansion, or submission.

## Anti-patterns

Do not:

- report numbers and immediately mark the branch complete;
- call missing infrastructure a negative method effect;
- call a null downstream effect proof that an upstream intervention did not occur;
- turn evidence retrieval/similarity into semantic truth;
- invent a validator after observing the result in order to rescue a preferred method;
- let a method-extension STOP erase an independently supported phenomenon/measurement paper;
- store a Failure Asset without `does_not_imply` and a reopen/precheck boundary.

## Machine binding

`research_pipeline.result_analysis` is the zero-authority compiler for this contract.

The canonical C1 instance is `RA-C1-CBRG-CLOSURE-20260825`. It must remain valid before the corresponding Failure Asset and Discovery Lessons can enter Research Memory.

Research System health requires:

- the registered analysis ledger to validate with zero errors;
- all registered terminal result analyses to be distilled;
- result-derived failure assets to appear in Failure Asset Library;
- result-derived lessons to appear in Research Memory Wiki;
- the standalone Wiki and embedded Research System memory counts to agree after projection.
