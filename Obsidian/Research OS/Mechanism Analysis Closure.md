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
9. **Evidence-locator vs validity test.** Exact evidence location is still not semantic support. A deterministic locator may bind a claim to an exact pre-outcome state span, but similarity/lexical overlap only establishes a candidate anchor. Missing anchors must remain unlocated/fail-closed; they may not receive imputed support. A separately versioned adjudicator must decide support/contradiction/unverifiable.
10. **Adjudicator-qualification test.** A semantic classifier or NLI model does not become evidence authority merely because it exists locally or emits entailment labels. Before it touches the scientific pool, it must be content-addressed, have explicit decision semantics, carry an independent task-specific pre-outcome qualification receipt, and demonstrate information beyond the strongest same-information similarity/applicability baseline. If no qualified adjudicator exists, first record a **readiness HOLD**, not fabricated labels and not a scientific failure.
11. **Bounded availability-closure test.** After a readiness HOLD, a zero/low-cost bounded inventory may ask whether an already-frozen qualified adjudicator/receipt exists in the permitted local/repository evidence set. If none exists and inventing a new post-outcome rule would violate the qualification contract, STOP/MERGE the **current method extension**. This terminal routing must retain any independently valid phenomenon/measurement result, must not declare scientific failure, and must not automatically reopen from a generic NLI model, renamed baseline, or self-authored verifier.
12. **Heterogeneous-stage localization test.** When a mechanism chain is measured with non-commensurate observables (for example representation distance, retrieval/event rate, action-distribution distance, and endpoint effect), do not manufacture a cross-stage ratio merely to obtain a scalar mechanism score. Preserve each stage's own evidence semantics (`SUPPORTED`, `DIRECTLY_OBSERVED`, `NOT_SUPPORTED`, or an explicitly typed heterogeneous boundary state) and localize the first unsupported native stage after supported/observed prerequisites. Side controls that bypass a native stage may weaken alternative explanations but cannot make the bypassed native stage pass. This ordinal localization is an operational measurement result, not causal mediation.
13. **Zero/low-cost D0.** Before expensive execution, verify that the residual is measurable/manipulable on outcome-independent support, the proposed gate/representation is non-degenerate, and the added validity signal is incrementally informative beyond demoted baselines.
14. **Go/Stop symmetry.** Both success and failure must change the next paper decision.

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
- **Evaluation/measurement:** a decomposition shows an old metric conflates distinct scientific stages and changes real conclusions. If stage observables use different units, prefer an ordinal evidence ladder over a post-hoc scalarization.

## Research OS execution rule

No mechanism-derived method receives provider/GPU authority from story quality alone. Required order:

`closest-work collision -> baseline-only ledger -> nonbaseline scientific residual -> evidence-authority check -> operational contrast identity -> causal-purity boundary -> exact evidence locator -> adjudicator qualification -> {qualified: semantic validity adjudication | unavailable: bounded availability closure -> STOP/MERGE current extension} -> zero/low-cost D0 -> frozen fresh experiment contract -> bounded execution -> claim audit`

Passing the novelty-residual reviewer gate or an intermediate D0 creates **historical design eligibility only**. A later terminal closure gate overrides current eligibility. Neither historical GO nor terminal STOP grants scientific, provider, GPU, claim-expansion, or submission authority; those permissions remain separate gates.

For paper-specific residuals, this rule must be executable rather than prose-only: the versioned revision artifact supplies canonical component IDs, collision references, evidence-authority semantics, D0 budget, and zero-authority fields; a fail-closed machine adjudicator rejects missing baseline demotions, novelty-set drift, self-validating treatment labels, unreceipted evidence authority, or any execution-authority escalation. C1's `C1_EXECUTABLE_CLOSURE_REVIEWER_GATE_V3` is the first bound implementation of this contract.

C1 also exposes a stricter six-layer distinction that Research OS must preserve: **receipt-envelope integrity != operational branch-contrast identity != atom-level causal purity != exact evidence location != adjudicator qualification != semantic evidence validity**. A content-addressed trajectory/evidence packet can prove provenance without proving that a parsed memory atom belongs to the paired branch contrast. A paired branch contrast can be reproducible while still mixing treatment effect with residual writer nondeterminism unless seed/noise-floor controls exist. An exact source-span locator can then make a unit auditable, but lexical/semantic proximity to that span still does not prove support. Even an entailment-capable model is not validity authority until its own task-specific pre-outcome qualification is bound. Missing anchors and missing adjudicators stay fail-closed. Semantic authority is illegal until the qualified support/contradiction/unverifiable layer passes; nonzero behavioral authority is illegal until that validity layer is established. Structural bindability, pairwise difference, locator similarity, or generic NLI availability alone is never scientific support.

C1 v4 additionally establishes the terminal-routing invariant: **historical D0 eligibility != current execution eligibility**. A content-addressed bounded inventory may close the current extension when no qualified adjudicator/receipt exists, but that closure is scoped to the extension. Reopen requires new qualified content-addressed evidence plus the original non-reducibility/collision gates; merely discovering a generic NLI checkpoint or renaming similarity/common-residual logic is insufficient.

C1 R3 adds the heterogeneous-stage measurement invariant: **mechanistic order != metric commensurability**. Its native chain uses memory-state contrast, retrieval exposure, action-distribution contrast, and terminal outcome, which cannot be meaningfully divided into one attenuation/mediation coefficient. The reusable protocol is therefore an ordinal stage-evidence ladder: retain each stage's valid evidence type, keep forced capacity as a side control because it bypasses retrieval, and report the first unsupported native stage after supported/directly observed prerequisites. This makes bottleneck localization reproducible without manufacturing numerical depth.

Existing negative/null results remain visible. A failed or stopped method extension never retroactively invalidates a valid mechanism/measurement result.
