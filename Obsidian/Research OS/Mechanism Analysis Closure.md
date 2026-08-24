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
5. **Novelty-residual ledger.** Split the proposal into `baseline-only` components and the exact `nonbaseline scientific residual`. Anything already absorbed by closest work or a strongest reduction stays a baseline unless new primary collision evidence explicitly reopens it; renaming or composing baselines does not create novelty.
6. **Evidence-authority test.** If the method gates a treatment-specific residual, the treatment label itself cannot validate that residual. Semantic similarity/applicability can define a baseline or eligibility signal, but cannot by itself grant evidence authority. The candidate must name an outcome-independent validity signal and why it adds information beyond the strongest same-information baseline.
7. **Claim-binding test.** A receipt-level evidence packet hash is not claim-level evidence binding. Before semantic validity is adjudicated, each candidate atom must first have explicit treatment/residual identity and exact evidence refs/hashes. A parsed field, embedding residual, or packet SHA cannot be silently upgraded into a supported mechanism claim.
8. **Operational-contrast vs causal-purity test.** A same-input paired branch difference can be a valid operational scientific object without proving that every textual delta atom is a pure causal effect. Atom-level causal language requires an explicit decoding seed or a same-condition same-input replication/noise-floor control. Without that control, preserve the paired contrast but downgrade the terminology rather than inventing causal certainty.
9. **Zero/low-cost D0.** Before expensive execution, verify that the residual is measurable/manipulable on outcome-independent support, the proposed gate/representation is non-degenerate, and the added validity signal is incrementally informative beyond demoted baselines.
10. **Go/Stop symmetry.** Both success and failure must change the next paper decision.

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

`closest-work collision -> baseline-only ledger -> nonbaseline scientific residual -> evidence-authority check -> operational contrast identity -> causal-purity boundary -> claim-specific evidence binding -> zero/low-cost D0 -> frozen fresh experiment contract -> bounded execution -> claim audit`

Passing the novelty-residual reviewer gate or D0 creates **design eligibility only**. Neither state grants scientific, provider, GPU, claim-expansion, or submission authority. Those permissions remain separate gates.

For paper-specific residuals, this rule must be executable rather than prose-only: the versioned revision artifact supplies canonical component IDs, collision references, evidence-authority semantics, D0 budget, and zero-authority fields; a fail-closed machine adjudicator rejects missing baseline demotions, novelty-set drift, self-validating treatment labels, unreceipted evidence authority, or any execution-authority escalation. C1's `C1_EXECUTABLE_CLOSURE_REVIEWER_GATE_V3` is the first bound implementation of this contract.

C1 also exposes a stricter four-layer distinction that Research OS must preserve: **receipt-envelope integrity != operational branch-contrast identity != atom-level causal purity != claim-level evidence validity**. A content-addressed trajectory/evidence packet can prove provenance without proving that a parsed memory atom belongs to the paired branch contrast. A paired branch contrast can be reproducible while still mixing treatment effect with residual writer nondeterminism unless seed/noise-floor controls exist. And neither contrast identity nor causal purity proves that a residual rule is true or useful. Semantic authority is therefore illegal until exact claim-specific evidence is bound; nonzero behavioral authority is illegal until semantic validity is separately adjudicated. Structural bindability or pairwise difference alone is never scientific support.

Existing negative/null results remain visible. A failed method extension never retroactively invalidates a valid mechanism/measurement result.
