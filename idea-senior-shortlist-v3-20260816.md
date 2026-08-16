# Senior-Discussion Idea Shortlist v3 — 2026-08-16

This shortlist is deliberately stricter than the earlier version. It uses the current paper-evidence-quality rule: a direction is not promoted because the story is attractive; it must expose a load-bearing scientific object, strongest same-information reduction, a ruling-out experiment, visible failure/boundary cases, and a realistic evidence substrate. None of the rows below has canonical Problem-Gate, Method, P0, or GPU authority.

## A1 — Frozen Evaluator Anchors Cause Actor-Shifted Held-Out Selection Regret

**Status: strongest new candidate. `REDUCTION_PENDING` → bounded evidence design PASS → independent evidence review `CLEAR_FOR_SUBSTRATE_PREFLIGHT`. Local substrate competence qualification is frozen but has not yet run because all 52 GPUs are occupied by another project.**

**Scientific problem.** Double Ratchet evolves an evaluator on outputs produced before skill evolution, then uses that evaluator to grade later skill evolution. Once the actor changes, the output/error distribution can move while the metric-selection anchor remains fixed. The question is not merely “the evaluator is stale,” but whether this creates *selection regret*: the frozen-anchor evaluator chooses a different metric/update than a same-information selector that is allowed to observe actor-shifted outputs, and that disagreement predicts held-out loss.

**Exact prediction.** Holding candidate metrics, model, query/task distribution, compute budget, and held-out evaluation fixed, the released frozen-anchor selection rule will incur greater actor-shifted held-out metric-selection regret than a same-information online-refresh/reweighting baseline. The gap should increase with measured actor-output movement. A reciprocal arm that refreshes metric-selection data with skill-phase outputs should reduce the gap.

**Strongest reductions to beat.** Covariate shift / online adaptation / stale-supervisor calibration using the same actor outputs and outcomes; snapshot-validity/adaptive-validation theory.

**Ruling-out falsifier.** Three matched arms on the same Double Ratchet first-party code path: released frozen anchor; same-information online refresh/reweight; reciprocal skill-output→metric-data refresh. Compare chosen metric, held-out agreement/regret, ranking disagreement, and actor-distribution movement. If the generic online-adaptation baseline explains the full gap, STOP.

**First-party grounding.** Amazon Double Ratchet commit `0f14e910d361196422d9b938f45280919952d4fd`. The code freezes `dev_items/train` before alternation and later metric phases reuse them while skill outputs do not enter the metric-selection data.

**Current execution boundary.** Evidence contract passed all nine independent checks. Local Qwen injection through the released `ctx['llm']` / role-client seams has passed non-scientific skill-side + metric-side smoke. Final local-model competence qualification is preregistered on MBPP task IDs 17–32 and must show both an authored active skill and a nonempty selectable evolved metric before any scientific arm runs. No repair of its rounds/thresholds is allowed after outcome.

**Why show the senior collaborator.** This is the cleanest current self-evolution problem: endogenous actor change makes the evaluator's training support stale, and the scientific claim is about a downstream decision error rather than the mere existence of a missing feedback edge.

## A2 — One-Way Metric→Skill Co-Evolution Produces Delayed Held-Out Regret

**Status: `REDUCTION_PENDING` → evidence design PASS → independent evidence review `CLEAR_FOR_SUBSTRATE_PREFLIGHT`; same frozen substrate qualification as A1.**

**Scientific problem.** In the released Double Ratchet update graph, the current evolved metric changes the skill learner, but skill-phase outputs do not refresh future metric-training examples. This one-way coupling can create a longitudinal divergence: the in-loop metric-graded skill signal continues to improve while locked held-out quality begins to reverse.

**Exact prediction.** Across matched co-evolution histories, early metric-graded skill performance improves under the one-way loop, but after sufficient actor shift, held-out `eval_locked` agreement/performance falls even when the in-loop signal does not. A reciprocal-refresh arm should delay or reduce this reversal more than a generic stale-anchor/nonstationary control matched on rounds, output divergence, candidate diversity, and compute.

**Strongest reductions to beat.** Non-stationary learning; stale-supervisor / anchor-aging; alternating optimization; generic distribution-shift adaptation.

**Ruling-out falsifier.** Longitudinal matched histories under released one-way coupling, stale-anchor control, and reciprocal refresh. Pre-register the crossover/reversal criterion and measure whether held-out degradation remains after conditioning on ordinary output drift and calibration variables.

**Boundary relative to A1.** A1 is a decision/selection-regret object at a frozen comparison point. A2 is a longitudinal emergence object: when and whether an initially useful one-way evaluator–actor loop turns into delayed held-out regret. They can ultimately merge if one experiment shows they are the same phenomenon.

**Why show the senior collaborator.** Strong ICLR-style mechanism story, but it should be treated as a sibling of A1 until the first bounded falsifier proves a distinct longitudinal residual.

## B1 — Matched-Uptake Residual in Persistent Skill Carryover

**Status: first-party-asset-grounded opposite-search seed, not yet a provisional Problem candidate. No current matched residual has been observed.**

**Scientific problem.** A previous AutoSkill × SkillMisevo smoke produced a real persistent-library effect, but the selective P19 harm was already explained by task-conditioned artifact uptake: P19 executed the injected hook-like procedure while P20/P21 largely did not. A new carryover mechanism is justified only if harm differs after holding *actual uptake* fixed.

**Exact search target.** Find provenance-audited fresh-session units with the same frozen persistent library, matched task–artifact compatibility, and the same action-level/selected-for-use uptake state, but different harm outcomes; or harm without the corresponding artifact uptake. Then ask whether retrieval-utilization/instruction-following plus task-conditioned effect-heterogeneity baselines still explain the result.

**First-party grounding added to main.** AutoSkill commit `94c47ca488d4ba4117d20272e66d49b9877e68cf` now has a zero-authority inversion asset manifest. Its OpenClaw runtime separately records retrieval hits, `selected_for_context_ids`, `selected_for_use_ids`, explicit/inferred `used_skill_ids`, session success/task_success, and SkillEvo lineage/replay provenance.

**Current evidence boundary.** Existing P19/P20/P21 probes do *not* satisfy the reopen condition: P19 has strong hook-action uptake and harm, while P20 and P21 do not provide a matched same-uptake harmful/non-harmful pair. Therefore this is a genuine future search direction, not a claimed positive result.

**Strongest reductions to beat.** Retrieval-versus-utilization diagnostics; instruction following; task-conditioned effect heterogeneity/CATE; ordinary artifact applicability.

**Why show the senior collaborator.** It is a distinct safety/memory line with a real first-party measurement surface. If a same-uptake/different-harm pair exists, the residual would be much more interesting than generic “unsafe memory persists.”

## B2 — Functional Equivalence Does Not Imply Diagnostic Equivalence

**Status: paper problem remains interesting; current P0 realization is `INCONCLUSIVE_FUNCTIONAL_EQUIVALENCE_QUALIFICATION_FAILED`, so no scientific positive/negative has been authorized.**

**Scientific problem.** Two repair realizations can be functionally equivalent on current tasks while leaving different future diagnostic observability. A system choosing between equally successful repairs may therefore need a diagnostic-equivalence criterion, not just current utility.

**Strongest reductions to beat.** Generic diagnosability/observability; simple repair complexity and logging richness; current-task utility tie-breaks.

**Decisive experiment.** First qualify truly functionally equivalent repair pairs under the frozen repair contract and baseline noninferiority, then expose matched future faults and test whether diagnostic distinguishability changes a pre-registered tie-break commit decision.

**Current boundary.** The latest run failed the *repair qualification* gate; the future-fault phase was correctly locked. The contract forbids tuning the same realization after seeing this failure. It needs a new paper-design/operationalization decision, not another retry.

**Why show the senior collaborator.** Conceptually clean and different from evaluator staleness, but currently lower priority because the first realization failed before the scientific test.

## C — Attractive but currently HOLD / DEAD (do not sell as passing Ideas)

### C1 — Shared-Budget vs Fixed-Width Latent Retrieval (LOPD)
The interaction surface is clean, but the author release exposes final Qwen/OLMo model weights and code only; the required QFormer/compressor checkpoint, memory bank, and EnvScaler scenario/meta assets are not published. Author-faithful latent-allocation evidence is therefore source-specific HOLD.

### C2 — Raw-VLA vs Skill-Harness Test-Time Selection Sign Reversal (SHAPER)
Strong embodied story, but the current primary source/full text exposes no author code/project release and 52 has no SHAPER/OpenVLA candidate substrate. Matched candidate-quality/diversity/verifier falsifier remains support HOLD.

### C3 — Router-Capacity Saturation in Co-Evolving Skill Libraries
The first formulation was promising, but an independent evidence reviewer correctly BLOCKED the self-contained simulation: defining router capacity and semantically confusable skills in the simulator bakes the predicted crossover into the data-generating process. Reopen only with real first-party checkpoints/outputs, not a designed simulation.

### C4 — Relevance-Conditioned Evidence Debt
Principle dead end. DocAtlas already represents unresolved relevance-conditioned gaps in `Note=(found,evidence,plan)` plus mutable Search/Read state. A separate evidence-debt score has no residual unless same full information-gap/search states require different optimal answer/continue actions and survive value-of-information baselines.

## Recommended discussion order

1. **A1 Frozen evaluator anchors → actor-shifted selection regret.** Best current new problem and closest to a legitimate bounded falsifier.
2. **A2 Delayed held-out regret in one-way metric→skill co-evolution.** Strong longitudinal sibling; merge with A1 if evidence says so.
3. **B1 Matched-uptake carryover residual.** Best distinct safety/memory direction; first-party measurement surface now exists, but residual not yet observed.
4. **B2 Functional vs diagnostic equivalence.** Strong conceptual problem, current realization inconclusive.
5. Mention C1/C2 only as high-potential support holds if the senior collaborator likes the themes; do not present C3/C4 as live directions.

## Evidence-quality rule for all next steps

A direction is promoted only if it has: (i) an empirical/analytical matched baseline with an explicit role; (ii) at least one experiment that can rule out the strongest alternative explanation; (iii) visible negative/boundary regimes; (iv) a sensitivity/robustness plan; and (v) completed evidence rather than “planned experiments” before paper-ready status. More experiment count is not itself evidence quality.
