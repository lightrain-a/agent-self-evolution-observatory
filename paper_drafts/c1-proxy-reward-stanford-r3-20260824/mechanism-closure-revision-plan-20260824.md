# C1 mechanism-to-intervention revision plan — 2026-08-24

Paper: `D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE`

Current title: **Reward Errors Change Memory Before They Change Policy**

Plan status: `DESIGN_ONLY / ZERO_EXECUTION_AUTHORITY`

Current scientific candidate remains the B12 stage-resolved manuscript; this plan does not reinterpret or overwrite any completed experiment.

## 1. Revision decision

C1 is no longer bottlenecked by same-support experiment volume. The current evidence already includes write breadth, wording reduction, forced leverage, exact retrieval exposure, native terminal transport, raw/no-memory/outcome-blind controls, first-action uptake, post-hoc working-memory localization, cross-writer evidence, and a second-domain Reddit replication.

The remaining ICLR-level weakness is **closure**: the paper identifies that reward-conditioned state divergence attenuates before broad policy uptake, but does not yet turn that mechanism into a falsifiable system intervention.

Do **not** reopen by adding Shopping rollout depth, selecting known nonzero cells, lowering the 0.15/0.20 floors, rescuing the old DeepSeek transfer, or searching for a third domain with a larger post-hoc effect.

## 2. Mechanism-derived actionable variable

Current mechanism:

`label-only intervention -> large write divergence -> broad exposure possible -> weak branch-specific working-state/action uptake -> sparse/domain-dependent terminal transport`

The actionable variable is therefore **the authority given to reward-conditioned semantic residuals inside an otherwise reusable procedural memory**.

A whole reward-conditioned reflection currently mixes two objects:

- an outcome-insensitive procedural core that often remains useful across branches; and
- an outcome-conditioned residual whose validity and future applicability are uncertain.

The method extension should intervene on that decomposition rather than invent a generic memory router.

## 3. Working method hypothesis: Outcome-Decoupled Memory (name not frozen)

Let an episode be `(x, tau, r_hat)`, where `r_hat` is the observed terminal label and may be wrong. The released baseline writes

`M_r = W(x, tau; r)`.

The proposed extension first generates a counterfactual reflection pair independent of which label was observed:

`M_plus = W(x, tau; success)`

`M_minus = W(x, tau; failure)`.

A contrastive compiler then produces

`(C, D_plus, D_minus) = F(M_plus, M_minus, tau)`,

where:

- `C` is the label-invariant reusable procedural core;
- `D_plus / D_minus` contain branch-exclusive rules;
- every residual carries an explicit applicability predicate and source-evidence anchors.

### V1 — source-evidence validator

`V_src(tau, D_r) -> {SUPPORTED, CONTRADICTED, UNVERIFIABLE}`

The reward bit is not evidence. Only source-supported residuals can receive actionable authority; rejected/unverifiable residuals may remain as provenance but are quarantined from operative memory.

### V2 — target-applicability gate

For current query/state `(q,o)`:

`g(q,o,D_r) in {0,1}`.

The policy receives

`M*(q,o) = C + g(q,o,D_r) * D_r`.

This targets the observed sparse decision-bottleneck: a branch residual should only become operative when the future state actually instantiates its decision predicate.

## 4. Why the components are scientifically necessary

1. **Counterfactual pair / compiler** is motivated by the robust label-only write divergence; it identifies what changes because of the reward branch.
2. **Source-evidence validation** is motivated by the fact that a possibly wrong reward currently receives write authority over persistent state.
3. **Target applicability** is motivated by the Shopping/Reddit result that branch-specific effects are sparse and task-dependent even after retrieval.

If a strongest simple baseline eliminates the need for any component, remove the component. Method length is not a success criterion.

## 5. Current-source collision boundaries

The method must survive a fresh primary-source scan before ProblemGate.

- **Beyond Retrieval / QCR** already separates retrieval from reuse and uses target-bound procedure/applicability/verification support. Therefore generic query-conditioned reuse or an applicability gate is not novelty. C1 must remain specifically about reward-conditioned write errors and label-invariant-core / reward-residual decomposition.
- **AttriMem** addresses coarse outcome credit by token-level process feedback for memory-policy RL. C1 cannot claim that fine-grained feedback for memory learning is new; its question is robustness when terminal feedback itself may be wrong.
- **Memory Provenance Laundering / PPMF** already provides provenance-preserving memory authorization. C1 cannot sell generic provenance firewalls; source evidence is only a validator input.
- **MutMem** already authorizes memory mutation and stores signed positive/negative outcome evidence. C1 cannot sell authorized mutation or signed outcome logging.
- **DELTAMEM / delta-mem** names are occupied by multiple 2026 memory systems and must not be used. More importantly, DELTAMEM already represents generalized experience with root/common content plus residual nodes, so a generic core+residual representation is not novelty. C1 must bind the residual specifically to counterfactual success/failure reflection of the same trajectory and to reward-error authority.
- **Live-Evo** already decouples what happened from how to use it through an Experience Bank and task-adaptive Meta-Guideline Bank. Generic experience/guidance decoupling is therefore not novelty either.
- **ReasoningBank** itself already distills both successful and failed experiences; success/failure reflection is substrate, not contribution.

Reopen only if a fresh scan leaves the residual object intact.

## 6. Phase 0 — zero-provider support and identifiability preflight

Before any method call:

1. Scan all available released WebArena/AWM domains for fresh trajectory + deterministic evaluator + exact native-retrieval support.
2. Exclude current C1 source/future units and do not select by B4/B10/B11/B12 outcome.
3. Require enough independent source identities, intent templates, and future tasks for at least a bounded D0.
4. Freeze model/prompt/compiler schema/validators/metrics/corruption schedule/budgets/stopping rule before outcomes.
5. If support cannot realize reward-conditioned behavioral headroom without outcome-driven selection, STOP the method extension and retain C1 as an identification/negative-boundary paper.

## 7. Phase 1 — decisive D0

Question:

> Does separating label-invariant core from reward-conditioned residual authority reduce controlled reward-error regret while preserving clean memory utility?

Use an independent benchmark/programmatic source outcome as reference label `r*`; generate the observed label `r_hat` with a preregistered random flip schedule.

Recommended dose curve:

- `q=0` clean;
- `q=0.10`;
- `q=0.25` primary corruption condition;
- `q=0.50` stress condition.

The q values are controlled intervention doses, not estimates of real-world reward-error prevalence.

### Baseline ladder

1. no memory;
2. raw trajectory;
3. released ReasoningBank reward-conditioned memory;
4. outcome-blind core only;
5. core + selected residual, no validator;
6. core + source validator;
7. full core + source validator + applicability gate;
8. matched-information / matched-cost QCR-style target-bound reuse baseline;
9. matched-cost ReasoningBank/self-consistency baseline;
10. oracle applicability/true-label upper bound where appropriate.

### Primary metrics

- clean utility at `q=0`;
- corruption regret `R(q)=U(r*)-U(r_hat)`;
- harmful-update rate under corrupted labels;
- retained positive-memory utility;
- worst-case/tail regression;
- first-action decision change / uptake diagnostics;
- delta activation, validator abstention, calls, tokens, latency.

### D0 GO

GO only if, on fresh outcome-independent support:

1. the full method improves the robustness–utility frontier versus the strongest matched-information/matched-cost baseline;
2. clean utility satisfies a preregistered non-inferiority margin;
3. robustness is not obtained by simply rejecting almost all reward-conditioned residuals;
4. at least one mechanism-required component has a reproducible nontrivial contribution;
5. the result is not driven by one source/task/template.

### D0 STOP / MERGE

Stop the standalone method claim if:

- outcome-blind core-only ties the full method;
- matched-cost QCR ties it;
- a simple similarity/applicability rule ties it;
- the validator only rejects more memory without improving the robustness–utility frontier;
- fresh native support again has almost no reward-error behavioral headroom;
- the apparent advantage exists only on units selected from old positive C1 cells.

A STOP does not invalidate the existing C1 analysis paper.

## 8. If D0 passes — full ICLR evidence matrix

Target at least:

- two fresh domains;
- two downstream policy families;
- clean plus multiple corruption doses;
- matched information, calls/tokens, and environment evidence;
- independent source/task units rather than rollout count alone.

Ablations:

- no counterfactual pair;
- no source-evidence validator;
- no target-applicability gate;
- core-only / residual-only / full;
- evidence anchors removed;
- hard/soft gate only if both are scientifically motivated.

Mechanism analyses:

- whether residualization concentrates branch differences into decision-relevant rules;
- whether gate activation predicts first-action change beyond retrieval similarity;
- whether correct residuals preserve useful uptake;
- whether corrupted residuals are selectively quarantined rather than blanket-rejected;
- failure analysis across headroom, task difficulty, retrieval similarity, source identity, and intent template.

Sensitivity:

- q curve;
- gate threshold curve;
- memory-bank scale;
- retrieval-similarity bins;
- floor/ceiling headroom;
- leave-one-source/template/domain-out;
- second-policy transfer;
- cost/latency.

## 9. Manuscript redesign if the method passes

New argument chain:

1. phenomenon — reward labels robustly change persistent state;
2. strongest reductions — wording, raw, omission, outcome-blind structured control, endpoint headroom;
3. mechanism — common procedural information transports more readily than branch-specific reward residuals;
4. insufficiency of the current design — one reward-conditioned reflection gives the terminal label undifferentiated authority over actionable memory while providing no explicit residual applicability boundary;
5. method — separate core and reward residual, verify residual against source evidence, activate it only at relevant decision contexts;
6. controlled corruption — demonstrate a better robustness–utility frontier under matched information/cost;
7. generalization — domains, policy families, corruption doses, component ablations;
8. engineering rule — terminal reward may guide memory, but should not automatically own the entire actionable memory state.

Recommended main visual portfolio:

- Fig.1 stage-resolved phenomenon;
- Fig.2 Shopping/Reddit native boundary and concentration;
- Fig.3 method overview (counterfactual pair -> core/residual -> V1 -> V2);
- Fig.4 clean-utility vs corruption-robustness frontier / q curve;
- Fig.5 ablation, gate calibration, and failure regimes.

## 10. If the method stops

Do not manufacture a replacement method. Keep the current paper as a mechanism/identification paper and strengthen the evaluation contribution:

- make the stage-resolved boundary the formal evaluation object;
- add a main-text boundary figure rather than more rollouts;
- explicitly state the design rule that write divergence cannot stand in for behavioral transport;
- preserve the clean negative result as an engineering warning;
- use the failed method-extension contract as evidence that a simple method does not follow automatically from the phenomenon.

## 11. Immediate order

1. freeze this plan as design-only;
2. current-source collision scan for the method residual;
3. zero-call fresh-support qualification;
4. Problem/Economy/identifiability gate;
5. only then authorize a bounded D0;
6. no same-support C1 experimental expansion before that gate.
