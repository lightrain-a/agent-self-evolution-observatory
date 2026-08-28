# Durable Research Portfolio

This file records the **identity, scientific question, durable evidence lessons, and claim boundaries** of the principal tracks. It intentionally avoids asserting that an old execution state is still current.

## E1 — STRI / Representation-Invariance Line

### Durable scientific object
Whether a self-evolving/skill-based agent changes semantic control or downstream behavior merely because equivalent implementation content is represented, split, packaged, indexed, or normalized differently.

### Strongest scientific framing
The interesting object is not “a taxonomy metric” by itself. The paper should identify when a representation change alters the induced control distribution, characterize the boundary/regime where invariance can or cannot hold, and test whether the representation-level change propagates into actual behavior.

### Durable lessons
- A technically valid result can still be a weak paper if it depends on a niche/non-mainstream base method that few reviewers recognize.
- Prefer a strong, peer-reviewed/top-conference base method and a public benchmark with public baselines when extending the experimental substrate.
- Do not make the novelty “we add several evaluation metrics to Method X.” Abstract the general scientific object and use existing methods as substrates.
- Public/released artifacts are useful for cheap-first analysis, but evidence scope must be stated exactly.
- Distinguish representational invariance, realizability, and behavioral consequence. Do not silently move between these claim levels.

### New-substrate rule
Before a large rerun:
1. identify 2–4 broad candidate base methods from strong venues;
2. verify public code/data/checkpoints and reproducible benchmark protocol;
3. map the STRI scientific object to each substrate without changing its meaning;
4. run a small pilot that tests identifiability, not merely code execution;
5. scale only if the pilot can discriminate the competing hypotheses.

### Do not infer
Do not infer current submission readiness, current claim counts, or current execution authority from this handoff. Recover latest STRI artifacts from `generated/` and manuscript sources.

---

## E2 — Temporal Skill / Order-Sensitive Evolution Line

### Durable scientific object
Whether apparently equivalent skill/evolution transformations are sensitive to temporal order, stage, or conversion path, and where the sensitivity actually enters the behavior-generation pipeline.

### Durable lessons
- Public benchmark and baseline alignment are mandatory for persuasive comparison.
- Model/backbone selection should follow the conventions of relevant baseline papers rather than an arbitrary local convenience set.
- Run **pilot → adjudicate → full experiment**. The pilot must test scientific separability and expected signal, not just whether the runner finishes.
- Every full run must persist per-case results, raw outputs, seeds, logs, intermediate artifacts, configuration, code revision, and a resume path while it is running.
- A “stage ladder” can be criticized as merely reporting the same behavior at different metric granularities. The design must show a controlled stage-specific intervention or another falsifiable mechanism test.
- Operational localization (“attenuation appears between stages A and B”) is not automatically mechanistic localization (“stage B causes attenuation”).

### Required reviewer question
What observation could distinguish genuine temporal/path dependence from an evaluation/coarsening artifact?

---

## C1 — Proxy Reward / Memory-Write / Feedback Amplification

### Durable scientific object
How feedback/reward semantics interact with persistent memory or write mechanisms, and whether an observed downstream gain/loss is a direct feedback effect or amplification through memory.

### Essential causal control
Include a **no-memory / no-write terminal control** where appropriate. Without it, direct reward/feedback effects can be confounded with memory-mediated amplification.

### Durable lessons
- A writer branch that changes both reflection/instruction semantics and reward semantics cannot support an atom-level “reward bit caused X” claim.
- Writer health and artifact integrity must be checked before treating missing/non-changing memory as scientific evidence.
- Heterogeneity analysis across tasks/conditions/backbones can establish regime structure, but it should be motivated by a mechanism hypothesis rather than appended after the fact.
- A failed writer substrate is a substrate/execution failure until shown otherwise; it is not automatically a negative result about the scientific principle.

### Key causal decomposition
Prefer reasoning of the form:

```text
feedback intervention
  → immediate action/policy effect
  → write/admission effect
  → persistent-state effect
  → later reuse/behavior effect
```

Each arrow requires its own observable or controlled intervention if a causal claim is made.

---

## B1 — Failure Memory / Resampling Line

### Durable scientific object
When failure-derived experience or resampling changes future behavior, and whether the effect survives an independently motivated substrate rather than a single favorable implementation.

### Durable lessons
- Do not loosen scientific gates merely to add experiment volume.
- When an initial story is internally closed, the next high-value experiment is usually independent-substrate confirmation or a boundary test, not another local parameter sweep.
- Negative evidence can be scientifically valuable if it distinguishes principle failure from implementation/substrate failure.
- If a new substrate is chosen, its motivation should be frozen before outcomes are observed.

---

## C06 — Controlled Intervention / Stagewise Counterfactual Line

### Durable scientific object
Use controlled interventions to locate which transformation/stage is necessary or sufficient for an observed effect, without overclaiming mechanistic causality from correlations across stages.

### Durable lessons
- Prefer same-trajectory or tightly matched counterfactual branches when feasible.
- Change one scientifically interpretable variable at a time.
- Separate **where the effect changes** from **why it changes**.
- If the intervention changes multiple semantics simultaneously, explicitly downgrade the causal claim.
- Validate theoretical/diagnostic constructs against behavior before presenting them as a repair mechanism or causal explanation.

---

## R9 / PORT-010 — Embodied/Safety Evidence-Authority Line

### Durable scientific object
How to evaluate safety/reliability claims about agent self-evolution or embodied behavior when released artifacts, replay assets, and execution authority are incomplete or heterogeneous.

### Non-negotiable evidence rule
**Artifact existence is not execution/scientific authority.**

Examples of insufficient evidence by themselves:
- test metadata;
- query units without per-case outcomes;
- a submission/receipt saying PASS;
- an evaluator interface without released trajectories;
- a runner that cannot be replayed against the claimed evidence boundary.

### Durable lessons
- Per-case behavioral outcomes and replay provenance matter when the claim is behavioral.
- If the released evidence is incomplete, `HOLD / ZERO_AUTHORITY` can be the scientifically correct disposition.
- Never turn self-generated rollouts into “author-released outcome evidence” by wording.
- Candidate identifiers can be historically reused; binding must include the exact research object/artifact identity, not just a short ID string.
- Reopen rules should be based on explicitly materialized evidence requirements, not “a dataset changed” or “new metadata appeared.”

### Current-state caution
PORT-010 evolved through multiple evidence/replay discussions. Always recover its latest exact object binding and dated artifacts before stating the current disposition.

---

## Research-System / Scientific Control Plane

### Durable purpose
A versioned control plane for turning open-ended agent research into auditable scientific state: problem discovery, evidence acquisition, experiment authorization, claim adjudication, paper state, and explicit stopping conditions.

### Durable design principles
- Treat hypotheses, experiments, claims, reviews, and authority as typed objects rather than prose only.
- Preserve negative results and closed branches so later agents do not rediscover or accidentally resurrect them.
- Keep a distinction between `problem interesting`, `experiment identifiable`, `method supported`, `paper ready`, and `execution authorized`.
- Make “do not run” states first-class.
- Machine-generated dashboards are navigation surfaces; content-addressed evidence and explicit adjudication are higher authority.

---

## Related Embodied Self-Evolution / Memory Research Program

Some work in and around this project also developed a broader embodied-memory program. When that line is continued, preserve these stable distinctions:

- persistent memory influence vs faithful replay vs downstream task success are different observables;
- admission/write is not equivalent to successful reuse;
- effect attribution should distinguish source-consistent behavior from generic policy drift;
- memory mechanisms should eventually be tested across more than one VLA/memory substrate if broad claims are desired;
- physical-loop claims require task success/recovery/rejoin evidence, not decoded-action shift alone;
- experiments must stay anchored to the named paper question rather than absorbing audit machinery as the paper's main contribution.

If this line is moved into a separate repository/project, create a dedicated handoff rather than continuing to overload this package.
