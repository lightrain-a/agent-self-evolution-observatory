# Agent Self-Evolution Observatory — Review Protocol

## Purpose

This protocol is used before treating a research direction as ready for a top-tier ML/CV submission. It separates literature coverage, novelty, scientific validity, experimental feasibility, paper-evidence completeness, and website integrity.

## Literature reviewer

The reviewer must:

1. Check the current survey-maintained Awesome Self-Improving Agents list.
2. Search CVF Open Access, OpenReview, official proceedings, and arXiv for new visual/multimodal work.
3. Distinguish persistent model/scaffold updates from retry-only self-correction.
4. Verify conference status and merge duplicate arXiv/conference versions.
5. Identify the closest three methods to each proposed contribution.
6. Report missing papers, malformed metadata, and taxonomy disagreements.

A direction fails novelty review if its main mechanism is already present after removing application-specific naming.

## CVPR reviewer

The reviewer must ask:

- Is visual information indispensable?
- Does a caption-only or task-ID-only version retain the same gain?
- Are visual interventions controlled and interpretable?
- Does the main table directly show the claimed advantage?
- Are at least two visual environments or a compelling benchmark contribution provided?
- Is the contribution more than general agent engineering?

## Experimental reviewer

The reviewer must verify:

- matched calls, tokens, rollouts, tools, resets, and update compute;
- independent experimental units rather than repeated generations;
- frozen development, sealed confirmation, and safety probes;
- forward transfer, backward transfer, harmful updates, and cost;
- stop/pivot conditions before expensive expansion;
- a feasible D0 study before multi-backbone training.

## Paper evidence quality reviewer

The paper evidence quality reviewer must verify that a paper is supported by a completed evidence package rather than by prose or formatting QA alone.

For every empirical performance, mechanism, system, robustness, or cost claim, require:

- a typed baseline ladder that distinguishes current system, direct competitor, strongest same-information simplification, simple control, and oracle/upper-bound when applicable;
- matched data, observable information, model/checkpoint, inference budget, environment interaction budget, and evaluation protocol for empirical comparisons;
- an explicit `why better / where better` hypothesis plus plausible alternative explanations;
- at least one ruling-out experiment for each material alternative explanation;
- component ablations for multi-component methods, and representation / information-budget / assumption-boundary ablations when those carry the novelty;
- explicit failure analysis, sensitivity or robustness analysis, and uncertainty for headline empirical comparisons;
- claim-to-artifact links for the main comparison, ablations, mechanism analysis, failure analysis, and sensitivity analysis.

A planned baseline or ablation does not count as manuscript evidence. Each planned evidence item must resolve to `PASS`, `FAIL`, `INCONCLUSIVE`, or justified `NOT_APPLICABLE` with a versioned artifact. Failed and inconclusive experiments remain visible in the evidence chain instead of being silently dropped.

For theory/certificate papers, an analytical simplification and assumption-boundary stress test may replace a conventional component ablation only when the non-applicability is explicit. Mechanical manuscript QA, venue-format QA, compilation, and supplement reproduction can never substitute for this scientific evidence review.

## Visual evidence reviewer

The visual evidence reviewer treats a figure as a scientific argument, not decoration. The design pattern follows strong autonomous-research papers: combine workflow/overview diagrams with quantitative comparison, ablation, mechanism/boundary, failure/sensitivity, and—when the scientific object is a research system—scaling/progression evidence. Multi-panel figures are preferred when several panels answer one reviewer question.

Every planned main-text visualization must bind:

- one explicit reviewer question and one sentence-level takeaway;
- the paper claim(s) it supports and the baseline/ablation/analysis evidence IDs it consumes;
- a versioned data artifact, a generation script/specification, the rendered figure artifact, and a manuscript caption/label;
- uncertainty/error bars or another preregistered uncertainty display when the quantitative claim requires it;
- negative, failure, boundary, or inconclusive regimes when those qualify the claim rather than hiding them in prose or appendix.

Before manuscript-ready, figure QA must verify caption/claim alignment, readable labels, direct labels or a legend, non-deceptive axes/scales, and versioned source data. A figure that is visually polished but cannot answer its registered reviewer question is evidence-incomplete. A table may remain for exact values, but it does not replace a required visual explanation of mechanism, heterogeneity, robustness, scaling, or failure boundaries.

For method papers, the main visual portfolio must cover at least main comparison, ablation, mechanism, failure, and sensitivity; an overview figure is recommended. For system papers, require overview, main comparison, failure, sensitivity, and scaling/progression; human evaluation is recommended when the claimed value includes research quality or usefulness. For theory/certificate papers, require boundary, mechanism, failure, and sensitivity views rather than theorem statements alone.

## Adversarial reviewer

The adversarial reviewer should try to reject the paper using these hypotheses:

1. The gain is only extra inference search.
2. A stronger visual critic matches the method.
3. Counterfactual changes alter task difficulty, not only causal evidence.
4. The controlled GUI result does not generalize.
5. The diagnostic identifies a causal factor but does not improve future tasks.
6. The benchmark generator leaks transformation templates that the gate can memorize.
7. Accuracy improves while visual grounding silently degrades.
8. Verification cost exceeds the future benefit.

## Consensus criterion

A direction is considered ready only when:

- no reviewer identifies a direct method collision;
- all blocking experimental objections have a planned test;
- the D0 continuation criteria are satisfied;
- Paper Evidence Quality v2.1 passes with completed claim-matched baseline/ablation/analysis artifacts and source-bound visual evidence;
- the claim is reduced to the lowest contribution level supported by evidence;
- unresolved limitations are documented rather than hidden.

Consensus means no blocking objection remains. It does not require identical implementation preferences.

## Current external-agent status

The configured CodexFlow service at `127.0.0.1:4318` is currently unavailable, and the installed Claude CLI has invalid authentication. Literature-collision, taxonomy, venue-fit, reliability, experiment-skeptic, and 2026-frontier collision reviews have been performed as role-separated review passes, but they are not represented as independent external-agent consensus. The first-paper scope is frozen as **GroundEvo-Admission**, a visual causal lesson-admission study; memory–skill–parameter routing remains a later roadmap. Once external agents are available, four independent sessions must execute the roles above and their reports must be committed to this repository.
