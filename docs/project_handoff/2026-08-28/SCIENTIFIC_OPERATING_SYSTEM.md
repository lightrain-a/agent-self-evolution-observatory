# Scientific Operating System

This file captures the reusable research method learned across the project. It should govern new work even when the paper, benchmark, model, or server changes.

## 1. Start from a scientific object, not an experiment menu

Every track should be expressible as:

```text
Scientific object
→ competing mechanism hypotheses
→ observable predictions / regime boundary
→ controlled intervention
→ adjudication rule
→ bounded claim
```

A table of metrics is not a mechanism model. More experiments do not automatically create depth.

Before execution, write down:
- the scientific question in one sentence;
- the strongest alternative explanation;
- the smallest experiment that discriminates them;
- what PASS, FAIL, and ambiguous/HOLD each mean;
- which paper claim changes under each outcome.

## 2. Experimental lifecycle: smoke → pilot → full

### Smoke
Purpose: runner/schema/dependency sanity only.

A smoke PASS means the pipeline executes and artifacts are structurally valid. It does **not** imply scientific identifiability.

### Pilot
Purpose: test whether the proposed observable/intervention can distinguish the scientific alternatives at small cost.

A pilot must answer:
- is the manipulation actually present?;
- is the measurement sensitive to the manipulation?;
- are key controls clean?;
- is the effect distinguishable from trivial baselines/artifacts?;
- are raw/per-case outputs recoverable?;
- would a null result at full scale be interpretable?

### Full
Run only after a qualified pilot and explicit authorization. Freeze the important protocol before outcome inspection.

## 3. Atomic experiment contract

Each experiment should have an independent, replayable contract containing:

- experiment ID and scientific question;
- parent hypothesis/claim;
- exact code revision;
- data/benchmark identity and split;
- model/checkpoint identity;
- prompts/configuration/hyperparameters;
- seeds and sampling rules;
- treatment/control arms;
- primary metric and secondary diagnostics;
- statistical test/CI rule if applicable;
- expected raw and derived artifacts;
- output directory;
- execution host/accelerator when relevant;
- logs, PID/job ID, start/end timestamps;
- resume/restart instructions;
- failure semantics;
- adjudication authority.

Reruns should not silently overwrite old outputs. Create a new run/version and link it to the prior attempt.

## 4. Evidence hierarchy and authority separation

Keep these concepts separate:

```text
artifact exists
≠ artifact is valid
≠ artifact supports the claim
≠ claim has been adjudicated
≠ experiment is authorized
≠ GPU/provider execution is authorized
≠ paper is ready
```

A PASS string in a receipt is not evidence unless the referenced artifact/runner is real, replayable where required, and bound to the exact scientific object.

When a claim is behavioral, prefer per-case behavioral evidence over metadata/proxy-only evidence.

## 5. Claim discipline

Every positive claim needs:
- exact population/substrate scope;
- exact intervention and observable;
- uncertainty/replication as appropriate;
- strongest ruled-out alternative;
- explicit forbidden extrapolation.

Common downgrades:
- “we locate where attenuation occurs” rather than “we identify the mechanism”;
- “supports a bounded behavioral consequence on this substrate” rather than “shows general safety/utility”;
- “consistent with mediation” rather than “proves mediation” when the mediator is not independently intervened on.

## 6. Baseline and substrate selection

For papers whose contribution builds on another method/system:

1. Prefer **recognized, peer-reviewed/top-venue** base methods when scientifically appropriate.
2. Prefer public code, public checkpoints, public benchmark, and reproducible evaluation.
3. Prefer a substrate with a broad enough audience that reviewers understand why the phenomenon matters.
4. Use multiple baselines representing genuinely different explanatory families, not cosmetic variants.
5. Include the simplest plausible baseline capable of absorbing the apparent gain.
6. Freeze the reason for choosing a new substrate **before** looking at its outcome.
7. Do not change the scientific object merely to fit an easy-to-run benchmark.

A paper may extend an existing method, but the contribution should normally be phrased at the level of a general scientific problem or mechanism, not “Method X + our engineering additions.”

## 7. Controlled intervention rules

For mechanistic evidence:
- change one interpretable variable when possible;
- prefer matched/same-trajectory counterfactuals;
- keep evaluation identical across arms;
- verify the intervention was actually realized;
- isolate writer/reward/reflection/model/config changes rather than bundling them;
- distinguish necessary, sufficient, mediating, and correlational evidence;
- if multiple semantics change at once, narrow the causal wording.

## 8. Reviewer gate before scaling

Before a costly run, attack the plan with the strongest likely reviewer objections:

- Is the effect definitional or created by metric granularity?
- Can a simple baseline explain the gain?
- Does the treatment change more than one factor?
- Is a purported mediator merely correlated with the outcome?
- Is the benchmark/base method too niche for the claimed audience?
- Is external validity broader than the tested substrate?
- Are synthetic/toy artifacts being used to imply real behavior?
- Does the proposed theory/diagnostic predict actual behavior?
- Are exclusions, thresholds, or guards outcome-conditioned?
- Does the experiment preserve the original paper question?

If the objection cannot be answered by the design, fix the design before spending compute.

## 9. Failure differential before repair

When an experiment fails, classify the failure before changing anything:

- **formulation failure** — scientific question/prediction was not identifiable;
- **substrate failure** — benchmark/system does not realize the necessary conditions;
- **representation/measurement failure** — observable is wrong/coarsened;
- **optimization failure** — implementation cannot realize the proposed intervention;
- **baseline failure** — simpler baseline absorbs the apparent effect;
- **execution failure** — code/runtime/provider failure;
- **principle failure** — qualified experiment contradicts the scientific prediction.

Do not call every failed run a principle failure, and do not rescue every principle with an implementation excuse. State what evidence distinguishes the layers.

## 10. Single-variable repair rule

A repair should be falsifiable and minimal. Prefer one change that tests a diagnosed failure layer.

Examples:
- repair a broken writer without also changing reward semantics;
- change an unsuitable representation observable without changing the scientific intervention;
- add a no-memory arm to separate direct reward effect from persistence;
- move to a broader substrate after independently establishing substrate mismatch;
- add a behavioral validation arm for a theoretical diagnostic.

A repair becomes a new experiment/version; it does not retroactively alter the interpretation of the old result.

## 11. Outcome-conditioned tuning prohibition

Do not repeatedly alter guards, thresholds, seeds, exclusions, metrics, or task subsets until a desired result appears.

If a post-hoc change is scientifically justified:
- label it exploratory;
- preserve the original result;
- preregister/freeze the repaired confirmatory protocol;
- rerun independently where feasible.

## 12. Negative results, HOLD, and narrowing

Valid terminal states include:
- supported;
- unsupported under qualified test;
- method realization failed;
- evidence insufficient / HOLD;
- narrow/reframe;
- terminate flawed premise.

A HOLD is not “almost PASS.” A negative result can be paper-relevant when the design distinguishes why the prediction failed and constrains the regime.

## 13. Runtime persistence

For any nontrivial run, persist results **during execution**, not only at process end:
- per-case outputs;
- incremental metrics;
- checkpoints when useful;
- stdout/stderr logs;
- environment/config manifest;
- heartbeat/progress state;
- recoverable partial results.

A long experiment that finishes but loses per-case evidence is not equivalent to a successful scientific run.

## 14. Analysis is part of execution

After obtaining results, do not stop at “numbers look good/bad.” Record:
- expected vs observed pattern;
- alternative explanations;
- heterogeneity/regime structure;
- contradictions with prior evidence;
- claim updates;
- failure lessons;
- whether the next experiment is necessary;
- what should be added to the system so the mistake is not repeated.

The output of an experiment is both evidence and an update to the research process.

## 15. Anti-drift checkpoint

Before each new experimental stage, answer:

> If this experiment succeeds, does it directly strengthen the paper's named scientific question? If it fails, will it still distinguish an important competing explanation?

If neither is true, do not run it merely because it is available or easy.
