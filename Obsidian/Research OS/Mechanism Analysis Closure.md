# Mechanism Analysis Closure

Tags: #ResearchOS #paper-design #mechanism #ICLR #closure

## Core rule

A top-tier paper does **not** need a new engineering method merely because many accepted papers contain one. Strong analysis-only archetypes exist: a new robust phenomenon, a deep causal mechanism, a mathematical theory/certificate, or a measurement object that changes scientific conclusions can itself be complete.

The failure mode to avoid is different: a paper may identify an interesting phenomenon, rule out easy explanations, and localize a bottleneck, yet stop just before that bottleneck implies an actionable decision. In that case the story is scientifically unfinished even if the manuscript is polished.

After `phenomenon -> strongest reduction -> mechanism/bottleneck`, run the closure gate:

1. **Analysis-only exception.** Is the phenomenon/mechanism/theory already deep and broad enough to be the contribution? If yes, state which measurement, evaluation rule, or engineering decision changes because of it.
2. **Actionable-variable test.** What variable did the mechanism expose that the current system controls incorrectly?
3. **Intervention derivation.** Does that variable naturally imply a preregistrable intervention?
4. **Strongest-simple-baseline test.** What same-information/same-budget simple method could make the intervention unnecessary?
5. **Zero/low-cost D0.** Before expensive execution, verify that the variable is measurable/manipulable on outcome-independent support and that the proposed gate/representation is non-degenerate.
6. **Go/Stop symmetry.** Both success and failure must change the next paper decision.

If an intervention is scientifically natural but has not yet been tested, mark the paper-development state:

`ANALYSIS_INCOMPLETE_FOR_TOP_TIER`

This is not a scientific failure of the existing phenomenon.

## Anti-pattern: decorative complexity

Do **not** use these as proxies for top-tier depth:

- more equations without a new estimand or prediction;
- more validators that do not isolate a diagnosed failure mode;
- more modules whose ablations do not map back to a gap;
- more model families or domains chosen after seeing outcomes;
- more rollout depth on the same support just to improve significance;
- a complicated router when a same-information rule works equally well.

Complexity is justified only when required by the mechanism and when it survives the strongest simple baseline.

## Useful archetypes

- **Strong phenomenon:** a surprising, broad, reproducible regularity that changes evaluation assumptions.
- **Causal mechanism:** interventions/mediation identify a concrete mechanism and rule out plausible alternatives.
- **Theory/certificate:** a mathematical object explains when the phenomenon can/cannot occur and predicts boundaries.
- **Mechanism -> intervention:** diagnosis exposes a controllable variable; the method changes exactly that variable and succeeds in predicted regimes.
- **Evaluation/measurement:** a decomposition shows an old metric conflates distinct scientific stages and changes real conclusions.

## Research OS execution rule

No mechanism-derived method receives provider/GPU authority from story quality alone. Required order:

`closest-work collision -> strongest simple baseline -> zero/low-cost D0 -> frozen fresh experiment contract -> bounded execution -> claim audit`

Existing negative/null results remain visible. A failed method extension never retroactively invalidates a valid mechanism/measurement result.
