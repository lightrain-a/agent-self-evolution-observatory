# ICLR Agent Self-Evolution Manuscript & Experiment Template v1

Canonical machine object: `ICLR-AGENT-SELF-EVOLUTION-MANUSCRIPT-V1` in `generated/iclr-agent-paper-template.json/js`.

This template is a **paper-development and experiment-planning scaffold**. It does not create scientific claims and does not authorize model calls, experiments, GPU use, or submission. The current five papers remain scientifically governed by their canonical ledgers; the template applies on the next material manuscript revision.

## What we learned from the ICLR exemplars

The template distills recurring design choices from AFlow, AgentSquare, AMemGym, Reward Is Enough, Self-RAG, ReasoningBank, Agentic Context Engineering, and Darwin Gödel Machine.

The useful common pattern is not a shared set of section names. It is a shared sequence of **argument jobs**:

1. Make a real problem and its consequence visible immediately.
2. Explain what the current paradigm already does well before attacking it.
3. Give a concrete failure and decompose why the problem is hard.
4. Name the missing scientific object and the simplest intuition.
5. Show the whole method/protocol early enough that the reader can restate it.
6. Use strong baselines plus method-specific ablation/mechanism/boundary tests.
7. Keep negative regimes and cost visible because they define the claim.

## Default nine-page main-body budget

| Main-body job | Target pages | What must be accomplished |
| --- | ---: | --- |
| Abstract + Introduction | 1.5 | necessity, challenge, missing object, intuition, method, decisive evidence, bounded contributions |
| Problem Setup + Related Work | 1.0 | define the object and show why closest approaches do not already cover it |
| Method / Protocol | 2.0 | intuition → requirements → overview → components → algorithm → assumptions/cost/failure |
| Experimental Setup | 0.8 | RQs, data, models, strongest baselines, units, metrics, statistics, parity |
| Main Results | 1.3 | directly answer the headline RQs |
| Analysis | 1.6 | ablation, mechanism, robustness/transfer, failure, efficiency |
| Discussion + Limitations + Conclusion | 0.8 | scientific lesson, non-claims, evidence debt, practical implication |

The fractions are defaults, not venue law. The argument jobs are the contract.

## Introduction: seven paragraph jobs

**I1 · Concrete setting and stake.** Name the agent/task and the consequence of failure.

**I2 · Current paradigm.** Explain how the dominant approach works and concede what it already solves.

**I3 · Failure and challenge.** Give one concrete failure, then name 2–3 observable challenges: information, identification, optimization, longitudinal, compositional, or systems constraints.

**I4 · Missing object + intuition.** Name the missing variable, estimand, invariant, control, certificate, or decision object. Explain the key idea in ordinary language.

**I5 · Method overview.** Explain the complete input → operation → persistent object/state → output flow in 4–7 sentences.

**I6 · Evidence preview.** Give the decisive main comparison and one mechanism/boundary result. Mention an important null if it bounds the claim.

**I7 · Contributions.** Use 2–4 bullets: scientific object/problem, method/protocol, evidence/analysis. Implementation housekeeping is not a contribution.

## Related Work contract

Organize by **approach family or scientific distinction**, not by publication chronology.

For each family answer:
- How does it actually work?
- What does it already solve?
- What overlaps our method/object?
- What remains missing?
- Which claim must we therefore stop making?

End Related Work with the residual scientific object. “No prior work uses our module name” is not a novelty argument.

## Method contract

The order is:
1. problem object / minimum notation if needed;
2. plain-language core intuition;
3. design requirements derived from the failure;
4. one end-to-end overview figure;
5. components in execution order;
6. algorithm/protocol/update rule;
7. assumptions, held-fixed variables, complexity/cost, and failure boundary.

Every load-bearing component must answer six questions:
1. What exact input does it receive?
2. What operation does it perform?
3. What state/object does it read or change?
4. Why is it necessary for the scientific claim?
5. What measurable signature should change if it is removed or replaced?
6. What is the simplest alternative implementation, and which part of the claim is implementation/container-independent?

Every equation gets one ordinary-language sentence explaining the quantity, the decision, and its scientific role.

## Experiment program: fixed slots

**E1 · Main comparison — required.** Does the scientific object/method/protocol change the load-bearing outcome beyond the strongest fair baseline?

**E2 · Component / simplification ablation — required.** Which component carries the claim, and can a simpler same-information method reproduce the result?

**E3 · Mechanism-aligned analysis — required.** Does the effect appear where the proposed mechanism predicts rather than only in aggregate?

**E4 · Robustness / transfer / boundary — required.** Where does the result persist, vanish, hit a ceiling, or reverse across model/task/seed/release/domain regimes?

**E5 · Negative and failure cases — required.** What fails, which competing explanation remains possible, and what explicit non-claim follows?

**E6 · Efficiency / cost / scale — required.** What extra calls, tokens, latency, memory, search, or compute are consumed, and what is the quality–cost frontier?

**E7 · Case study / trajectory — optional.** Use one trace to make the mechanism understandable; never substitute an anecdote for statistical evidence.

A paper archetype may mark a required lane `NOT_APPLICABLE_WITH_ARCHETYPE_REASON` only when its scientific object genuinely replaces the lane. This is a planning decision, not experiment authority.

## Archetype adapters

- **Theory / certificate:** prioritize exact necessity/sufficiency, positive/negative regimes, sensitivity, and a bounded systems witness. Do not force a leaderboard claim.
- **Evaluation protocol:** validate the evaluator/simulator first; then show old-vs-new protocol disagreement, diagnostic decomposition, robustness, and a proof-of-concept optimization use.
- **Causal identification:** prioritize treatment/control definition, information parity, independent units, power/resolution, placebo and confound sensitivity.
- **Causal mechanism:** show intervention → intermediate witness → downstream outcome while ruling out simpler explanations.
- **Mechanism intervention:** targeted must beat both original and strong generic control in the predicted non-ceiling regime; keep transfer, ceiling, and null boundaries visible.

## Fixed result-paragraph recipe

Every load-bearing result paragraph follows:

**Answer → Evidence → Interpretation → Boundary**

1. Say the answer in ordinary language.
2. Give only the decisive numbers, unit, comparison, and uncertainty.
3. Say which claim or competing explanation changes.
4. State the caveat, null regime, or non-claim that remains.

## Writing rules

Use concrete subjects and ordinary verbs. Define new terms once in plain language. One sentence should have one main logical job. Say what every number counts and what the independent unit is. Use “we find/show/observe” for evidence, “we hypothesize/predict” for unresolved mechanisms, and “we do not test” for missing evidence.

Avoid chronological project diaries, noun stacks, novelty-sounding names for standard operations, using one aggregate score to claim both effect and mechanism, and hiding null/support/cost evidence that bounds the main conclusion.

Reader test: a technically literate reader with no Research OS history should be able to restate the **problem, challenge, intuition, method flow, decisive experiment, and claim boundary** after one read.
