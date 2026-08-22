# Paper Story V3 · Scientific Argument Contract

`selected-paper.html` is a reader-facing scientific argument surface, not a second PaperState ledger. Every paper that appears in `PaperRegistry` must also have one complete **Paper Story V3** entry. The story is a zero-authority projection over the canonical manuscript, claim ledger, and evidence. It may explain evidence; it may never create a new claim, authorize an experiment, change a scientific state, or infer a result that was not actually executed.

## 1. The argument chain

A paper should not be narrated as “we first tried A, then B, then C.” The reader should be able to follow this chain without learning Research OS internals first:

1. **Concrete scene** — who/what agent is doing which concrete task, and what goes wrong?
2. **Practical stake** — why does the failure matter in an actual deployment or research setting?
3. **Current paradigm** — how do the closest 2–4 approach families actually work, and what do they already solve?
4. **Concrete failure mode** — where exactly does the current paradigm break? Give a real failure before abstraction.
5. **Missing scientific object** — which variable, estimand, invariant, control, certificate, or decision object is not explicitly represented by prior work?
6. **Falsifiable research question** — what question follows from that missing object and can be contradicted by evidence?
7. **Design requirements** — what must any valid solution satisfy before it can answer that question?
8. **Gap → component mapping** — which component addresses which gap, and what confound/failure returns if the component is removed?
9. **Mechanism prediction** — if the proposed explanation is correct, which specific experimental signature should appear in which regime?
10. **Evaluation contract** — strongest same-information baseline, held-fixed variables, scientific/statistical unit, success rule, and falsifier.
11. **Main effect** — what is the load-bearing observation, exactly what does each number count, and why does it change the scientific judgment?
12. **Mechanism-aligned stress test** — does the effect strengthen, disappear, or reverse where the proposed mechanism predicts?
13. **Component / alternative-explanation tests** — which component actually matters, and do simpler explanations survive matched controls?
14. **Generalization and failure boundary** — where does the result transfer, what does it cost, and where is the claim explicitly null or unsupported?
15. **Final bounded claim** — what new knowledge is established, and what broader statement is still forbidden?

`Chain of Evidence` is cross-cutting: each load-bearing claim should trace to an experiment/RQ, figure/table, and a canonical evidence/artifact reference whenever available.

## 2. Choose the paper archetype before judging its evidence

The page must not force every paper into “our method beats a baseline.” The current archetypes are:

| Archetype | What counts as strong evidence |
| --- | --- |
| `theory_certificate` | The scientific object is necessary and well defined; theorem/certificate is exact; positive and negative boundaries agree with it; a bounded system instantiation follows the predicted invariant. |
| `evaluation_protocol` | A prior evaluation object is genuinely missing; the new measurement/control isolates it; the new protocol changes the scientific conclusion under matched conditions. |
| `causal_identification` | Confounds are explicitly isolated; information parity and statistical units are valid; power/resolution is honest; multiple endpoints do not get cherry-picked when the sign is unresolved. |
| `causal_mechanism` | A controlled intervention propagates through an explicit mechanism chain; strong alternative explanations are ruled out; intermediate witnesses and downstream outcomes are separately tested. |
| `mechanism_intervention` | A targeted intervention beats both the original system and a strong generic control in the predicted regime; ceiling, transfer, and null boundaries remain visible. |

A new archetype requires an explicit schema update and reviewer-facing rationale. Do not invent a new label merely because a paper does not fit the current evidence.

## 3. Required Paper Story V3 fields

Every current `PaperRegistry` paper must have these fields in its `paper-story-*.js` object:

- `paper_archetype`
- `thesis`
- `scene`
- `value`
- `failure_example`
- `approaches`
- `gaps`
- `missing_scientific_object`
- `research_question`
- `design_requirements`
- `motivation`
- `components`
- `mechanism_predictions`
- `alternative_explanations`
- `evaluation_contract`
- `experiments`
- `mechanism_tests`
- `component_evidence`
- `generalization`
- `failure_regimes`
- `boundary`
- `chain_of_evidence`
- `outline`

The authoritative machine-readable list is `PAPER_STORY_DATA.blueprint.required_fields` in `paper-story-blueprint.js`. `scripts/validate_paper_story_contract.js` checks the current PaperRegistry↔PaperStory one-to-one mapping and fails closed if required reasoning objects are missing.

## 4. Writing rules

**Concrete before abstract.** If a real task, environment, model, agent, or failure artifact exists, name it. Do not replace the scene with a term such as “memory provenance” or “representation invariance.” If the experiment was not run, say that it was not run; never fabricate an example for readability.

**Explain how baselines work.** A closest work or simple baseline needs an input → mechanism → output explanation and a reason it remains insufficient. A paper name alone is not a comparison.

**The missing scientific object is mandatory.** “Existing methods perform poorly” is not enough. State what prior work does not define, control, identify, certify, or measure. This object is the bridge from Related Work to the Research Question.

**Requirements precede components.** Do not start Method with module names. State what a valid solution must satisfy, then map each component back to a requirement/gap.

**Motivation must imply a prediction.** A component is not justified merely because it sounds plausible. Specify a mechanism-aligned signature: where an effect should grow, disappear, invert, or remain invariant if the explanation is correct.

**Use the strongest same-information comparison.** Controls should receive the same pre-outcome information, task evidence, budget, and relevant observable state whenever the claim depends on a residual mechanism. Never create novelty by withholding information from the baseline.

**Every number needs semantics.** State what is being counted, the independent scientific/statistical unit, and why the number changes the claim. Repeated rollouts are not automatically independent units.

**Nulls and counterexamples stay visible.** A ceiling cell, failed stress test, opposite-sign endpoint, provider/support failure, or incompatible transfer regime must not disappear merely because the headline result is positive.

**Separate effect from mechanism.** Main-effect evidence answers whether something changes. Ablation/control/mediator/stress evidence answers why. Do not use a single aggregate gain to claim both.

**End with Claim → Evidence → Boundary.** The page must distinguish supported claims, active-unrefuted hypotheses, unsupported broader claims, and external/support debt. Reader-friendly prose never overrides the append-only ledger.

## 5. Recommended manuscript argument order

The default paper outline is:

1. **Abstract** — setting/stake → missing object → method → decisive result → bounded takeaway.
2. **Introduction** — scene/value → current paradigm → concrete failure → missing scientific object → question → requirements → contributions.
3. **Problem & Closest Work** — define treatment/estimand/invariant and organize related work by what it does and what object remains missing.
4. **Method / Protocol** — requirement → component → mechanism prediction.
5. **Evaluation Contract** — RQs, strongest baseline, held-fixed variables, statistical unit, success rule, falsifier.
6. **Main Results** — answer RQs; lead with the answer and explain what each number means.
7. **Mechanism / Stress / Ablation** — predicted signatures, controls, mediators, negative regimes, nulls.
8. **Generalization / Efficiency / Failure** — transfer, OOD, cost/capability frontier, explicit failure regimes.
9. **Discussion & Claim Boundary** — what was learned, why it matters, what surprised us, and what is still unsupported.
10. **Appendix / Chain of Evidence** — full protocol, prompts/skills, data processing, statistics, failure results, reproduction commands, and claim→artifact bindings.

A paper may merge or rename sections for venue constraints, but the argument responsibilities must remain covered.

## 6. Adding a new paper to PaperRegistry

When a new canonical paper is added:

1. Create/update the canonical Paper Acceptance ledger independently. Paper Story never creates PaperState.
2. Add a Paper Story object, normally in a dedicated `paper-story-<slug>.js` file.
3. Register that script in `selected-paper.html` before `paper-story-view.js`.
4. Choose a `paper_archetype` based on the actual contribution, not the desired venue impression.
5. Fill all V3 required fields from the current manuscript/claim/evidence state. If a field is scientifically absent, write an explicit null/unsupported statement rather than inventing evidence.
6. Ensure every `components[].solves` reference points to a declared Gap ID.
7. Add at least one mechanism prediction, one strongest alternative-explanation control, one mechanism-aligned test, one failure regime, and one Chain-of-Evidence row.
8. Run `node scripts/validate_paper_story_contract.js`.
9. Run the static/site/browser gates. The public build must fail closed if the PaperRegistry paper set and Paper Story paper set diverge.
10. Only after the story and canonical PaperState agree should the page be published.

## 7. Authority boundary

Paper Story is a **read-only explanatory projection**. It has zero scientific, method, experiment, P0, GPU, and submission authority. Updating a story may improve explanation, but it cannot:

- broaden a frozen claim;
- convert an active-unrefuted hypothesis into a supported claim;
- reinterpret a support/runtime failure as scientific evidence;
- authorize a new experiment or resource;
- change Paper Preparation / Mock-PC / Claim Audit / PaperState status;
- create a real submission state.

If Paper Story prose and the canonical ledger disagree, the ledger wins and the public validator should block publication until the prose is repaired.
