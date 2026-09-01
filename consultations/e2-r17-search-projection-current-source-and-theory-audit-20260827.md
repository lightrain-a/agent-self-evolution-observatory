# E2-R17 Search-Projection Censoring — current-source collision and theory audit

Date: 2026-08-27
Status: ZERO-AUTHORITY PRE-DEBATE AUDIT
Branch: `research/e2-r17-compute-shielding-20260825`
Parent design commit: `21799444`
Historical-asset preservation commit: `10e2ae2b`

This note refreshes the closest-work boundary through 2026-08-27 and strengthens the mathematical object before blind Kimi/DeepSeek debate. It does **not** freeze F0-R4, authorize provider/GPU experiments, mutate R16, or claim novelty.

## 1. Current object under review

Search produces a structured object

\[
T_K\sim Q_K(\cdot\mid x,S_t),
\]

while acting and persistent learning consume different projections:

\[
\tau_t^+=a(T_K),\qquad E_t=g(T_K),\qquad S_{t+1}=U(S_t,E_t).
\]

The questionable default is `g_win=a`: only the trajectory selected for serving is shown to the persistent learner. The candidate thesis is therefore not that more test-time compute inherently harms learning. It is:

> Better search does not inherently teach less; learning only from what search serves can.

## 2. Strongest current collisions

### 2.1 Direct method collision: SkillCAT

**Chen et al., 2026, SkillCAT: Contrastive, Assessment-Augmented and Topology-Aware Skill Self-Evolution for LLM Agents, arXiv:2606.13317v2 (2026-07-29).**

Primary-source facts:

- It runs each evolution task multiple times and labels traces by the official evaluator.
- It forms same-task success/failure pairs.
- It identifies the meaningful divergence between paired trajectories and extracts a skill-editable lesson.
- It validates candidate patches by replaying the source task before merging.
- It explicitly frames single-trajectory evidence as unreliable.

Collision judgment: **CADP cannot claim novelty from success/failure pairing, first-divergence extraction, contrastive skill editing, or replay validation.** Those elements are already combined in a persistent external-skill pipeline.

Residual not directly tested by SkillCAT:

1. whether a serving-time winner selector endogenously removes the exact diagnostic evidence available in the generated search set;
2. an exact acting-gain/failure-visibility identity indexed by `K` and difficulty;
3. a cloned-state, exact-same-pool intervention that changes only the learning projection while holding the acting winner fixed;
4. prospective prediction of future learning deficits from pre-outcome censoring mass and diagnostic value;
5. a longitudinal online-acting/frozen-skill reversal induced by binding acting and learning projections.

Implication: SkillCAT is a mandatory strongest method baseline and closest-work discussion. If R17 reduces to “use a success/failure contrast to update a skill,” R17 is not novel.

### 2.2 Direct representation/selection collision: TopoCurate

**Yang et al., 2026, TopoCurate: Modeling Interaction Topology for Tool-Use Agent Training, arXiv:2603.01714.**

Primary-source facts:

- It argues that outcome-based filtering of successful trajectories ignores interaction dynamics.
- It projects multiple same-task trials into a semantic quotient topology containing effective and failure branches.
- It uses branch/error structure to choose SFT trajectories and RL tasks.

Collision judgment: the broad statement “winner/success filtering discards useful branch structure” is already present in parametric tool-agent training. R17 must distinguish its external persistent-updater setting, selection-induced observation law, same-pool intervention, and future frozen-skill endpoint.

### 2.3 Direct feedback-dynamics collision: Rethinking Self-Evolving Agent Skills

**Liu et al., 2026, Rethinking Self-Evolving Agent Skills: Feedback Dynamics over Multiple Rounds, arXiv:2608.02636.**

Primary-source facts:

- It holds executor/optimizer/revision/validation/round budget fixed while varying Normal, Fail-only, and Success-only feedback.
- Every selected evolved skill in its primary study uses failed trajectories; Success-only is never selected.
- It separately evaluates oracle parallel sampling and sequential refinement as test-time-scaling controls.
- On SpreadsheetBench, parallel sampling recovers little of the persistent-skill gain.

Collision judgment: “failed trajectories matter for skill evolution” and “test-time scaling differs from persistent skill improvement” are no longer novel. The surviving question is whether **search serving itself changes which failures reach the updater**, and whether that selective projection causes a future-skill deficit.

### 2.4 Sibling-contrast and divergence collisions

The following primary works already exploit multiple trajectories or success/failure divergence:

- **Search-E1**, arXiv:2605.22511: sibling trajectories with sharply different quality; efficient correct trajectory supplies privileged reference for offline self-distillation.
- **Sibling-Guided Credit Distillation**, arXiv:2606.12634: mixed successful/failed sibling groups; an external model summarizes contrast and divergence to reweight token credit.
- **Outcome-Verified Comparative Self-Distillation**, arXiv:2607.27937: failed student branches, outcome-verified successful continuations, and first state-aligned divergence.
- **SKILL-KD**, arXiv:2607.28048: student failure versus teacher trajectory on the same task, distilled into a validated textual skill patch.
- **SkillCAT**, arXiv:2606.13317: same-task multi-seed success/failure contrast directly into an external skill.

Collision judgment: neither “sibling evidence,” “first divergence,” “contrastive packet,” nor “validated textual patch” is independently defensible novelty.

### 2.5 Search experience reuse collisions

- **Do Not Waste Your Rollouts / Recycling Search Experience**, arXiv:2601.21684: distills positive intermediate conclusions and negative failure patterns from search rollouts into a shared test-time experience bank.
- **TSR**, arXiv:2602.11767: search-guided rollouts are directly used inside the training loop.
- **Expert Iteration / AlphaZero-style search distillation**: search is a policy-improvement operator whose improved distribution is projected back into a learner.
- **On-Policy Distillation with Best-of-N Teacher Rollout Selection**, arXiv:2605.09725: best-of-N can generate improved training targets.

Collision judgment: search often teaches **more**, not less. Any universal “more search hurts learning” thesis is false. R17 must condition the claim on the learning projection `g`, not on search budget alone.

### 2.6 Skill optimizer and diagnostic-search collisions

- **SkillOpt**, arXiv:2605.23904: scored success/failure rollout batches, bounded text edits, held-out acceptance, rejected-edit buffer.
- **SkillHEX**, arXiv:2608.05628: falsifiable failure hypotheses, executable diagnostic evidence, and evidence-guided search over persistent skill revisions.
- **StarHarness**, arXiv:2608.24804 (submitted 2026-08-25): stratified harness-evolution search with hidden selection and held-out evaluation.
- **Evo-Bench**, arXiv:2608.09096: benchmark construction and stratified splitting for harness evolution.
- **SESA**, arXiv:2607.29468: informative failures are distilled into persistent skills that alter the future training distribution.

Collision judgment: bounded validation, rejected-edit memory, diagnostic evidence, and multi-round harness/skill evolution are established ingredients. R17 needs a mechanism-level causal result rather than an optimizer feature bundle.

### 2.7 Mature conceptual reductions

- **Selective labels**, arXiv:1807.00905: historical decisions selectively hide outcomes and induce partial blindness. R17 is related but differs because the nonserved rollout outcomes and trajectories were generated and verifiable; the pipeline chooses not to expose them to the persistent updater.
- **Performative prediction**, arXiv:2002.06673: deployed decisions alter the future data distribution. R17 is a specialized performative data-generation loop in which the acting selector alters the updater-visible experience distribution.
- **DAgger**, arXiv:1011.0686: sequential decisions induce the observation distribution used for learning. R17 is not novel merely because execution changes future training data.

Residual boundary: **outcome-dependent serving selection over a shared search set, coupled to an external persistent updater through a winner-only logging/projection policy.**

## 3. Theory strengthening before debate

### 3.1 Exact binary identity without rollout independence

Let `Y_1,...,Y_K in {0,1}` be arbitrary jointly distributed verifier outcomes. Let the actor succeed whenever any rollout succeeds:

\[
A_K=\mathbb E[\max_i Y_i],\qquad A_1=\mathbb E[Y_1].
\]

Let failure visibility under a precommitted rollout and winner-only projection be

\[
V_{\mathrm{pre}}=\Pr(Y_1=0),\qquad
V_{\mathrm{win}}=\Pr(\max_iY_i=0).
\]

Then, with no independence or exchangeability assumption,

\[
A_K-A_1
=\Pr(Y_1=0,\max_iY_i=1)
=V_{\mathrm{pre}}-V_{\mathrm{win}}.
\]

Define the joint-distribution rescue-censoring mass

\[
\Gamma_K(Q)=\Pr_Q(Y_1=0,\max_iY_i=1).
\]

The i.i.d. Bernoulli model is only a closed-form specialization:

\[
\Gamma_K(p)=(1-p)-(1-p)^K.
\]

Its interior maximizer is

\[
p^*(K)=1-K^{-1/(K-1)}.
\]

This removes the strongest avoidable theoretical weakness in the current draft: independence is not required for the identity itself, only for the one-parameter curve and peak formula.

### 3.2 Correlated-rollout prediction

For a conditionally i.i.d. mixture `Y_i | Theta ~ Bernoulli(Theta)`,

\[
\Gamma_K=\mathbb E[(1-\Theta)-(1-\Theta)^K].
\]

Because this function is concave in `Theta`, heterogeneity/positive exchangeable dependence weakly reduces rescue-censoring mass relative to the i.i.d. curve evaluated at `p=E[Theta]`.

Prospective prediction: parallel rollouts with high shared-mode correlation should show smaller censoring mass than independent samples at the same marginal pass rate. R17 should estimate the empirical joint event directly and use the i.i.d. curve only as a reference model.

### 3.3 Exact continuous-verifier extension

Let verifier scores `R_i in [0,1]` be arbitrarily dependent and let the actor choose `max_i R_i`. For threshold `t`, define

\[
V_{\mathrm{pre}}(t)=\Pr(R_1<t),\qquad
V_{\mathrm{win}}(t)=\Pr(\max_iR_i<t).
\]

By the layer-cake identity,

\[
\mathbb E[\max_iR_i-R_1]
=\int_0^1\left[V_{\mathrm{pre}}(t)-V_{\mathrm{win}}(t)\right]dt.
\]

Thus acting gain equals **integrated threshold-level censoring mass** even for continuous verifiers and correlated rollouts. This is more natural than binarizing every score, although deterministic task completion remains the cleanest F0 endpoint.

### 3.4 When `Gamma times delta` is exact

Let the mixed rescue event be

\[
M=\{Y_1=0,\max_iY_i=1\}.
\]

Define a gated alternative projection that equals winner-only outside `M` and supplies a preregistered diagnostic witness inside `M`. Let

\[
D(T)=J(U(S,g_{\mathrm{alt}}(T)))-J(U(S,g_{\mathrm{win}}(T))).
\]

Then

\[
\mathbb E[D(T)]
=\Pr(M)\,\mathbb E[D(T)\mid M]
=\Gamma_K(Q)\,\delta.
\]

This factorization is exact only because the two projections are identical outside the event whose evidence is claimed to be censored.

For failure families, use a **mutually exclusive, precommitted partition** `Z` of mixed pools—e.g. deterministic first meaningful divergence family:

\[
\mathbb E[D(T)]
=\sum_z \Pr(M,Z=z)\,\delta_z.
\]

Under an i.i.d. within-family model this becomes

\[
\sum_z \pi_z\Gamma_K(p_z)\delta_z.
\]

Overlapping post-hoc failure tags cannot simply be summed; that double-counts mixed pools. The R4 contract must freeze a disjoint assignment or an explicit overlap allocation.

### 3.5 Information-theoretic statement and its limit

For latent reusable failure family `Z`, winner-only is a deterministic coarsening of the full search object, so by data processing

\[
I(Z;g_{\mathrm{win}}(T_K))\le I(Z;T_K).
\]

Under a Bayes-optimal unconstrained learner, the richer object has weakly greater value of information because the learner can ignore irrelevant evidence. This does **not** prove a fixed LLM updater benefits from the full pool: context overload and noisy evidence can make a practical updater worse. Therefore the method should be a bounded, validation-gated diagnostic projection, not “always feed the whole pool.”

This information statement is supporting intuition, not the main causal theorem.

## 4. Surviving novelty candidate after collision review

The strongest defensible object is narrower than the current method pitch:

> **Serving-induced selective trajectory logging in persistent self-evolution:** a search system generates a shared set of candidate trajectories, an acting selector improves current reward, and a tied winner-only learning projection endogenously censors diagnostic failures from an external persistent updater.

Potential irreducible package:

1. exact binary and continuous rescue-censoring identities, with no independence assumption for the core equality;
2. a prospective intermediate/rescueable-regime prediction and a correlation correction;
3. exact-same-pool cloned-state intervention with acting winner fixed;
4. pre-outcome prediction of held-out learning gaps using disjoint-family censoring mass times diagnostic value;
5. longitudinal demonstration that online acting and frozen persistent skill can move in opposite directions;
6. the simplest validated repair—possibly only a Rejected Witness, not CADP.

If any paper is found that already studies this complete coupling, R17 should be reduced or stopped.

## 5. Decisive experimental falsifiers

1. **Projection-null:** on exact same pools, initial skill, updater, verifier, and update seed, changing winner-only to a preregistered failed witness does not change future frozen skill in the predicted direction. Central mechanism STOP.
2. **No prospective law:** empirical mixed-pool mass and calibrated diagnostic value do not predict held-out family/regime ranking or sign. Mechanism claim downgrade/STOP.
3. **No longitudinal reversal:** high-K winner-only does not produce weaker frozen skill than the low-K reference under planned independent streams. Headline STOP, even if one-step edits differ.
4. **Token/context explanation:** duplicated-winner or token-matched neutral evidence matches the failed-witness effect. Diagnostic-evidence mechanism fails.
5. **Simpler method dominance:** Rejected-Witness matches all CADP variants. Keep the simpler method and delete CADP-specific novelty.
6. **SkillCAT reduction:** a source-faithful SkillCAT-style same-task contrast baseline explains the full effect without the serving-selection causal chain. R17 becomes an application/replication unless the law and intervention remain independently novel.

## 6. Required changes before an executable R4 contract

- Add SkillCAT and TopoCurate as mandatory closest work and baselines.
- Rewrite the identity as independence-free; retain i.i.d. only for the analytic curve and `p*`.
- Define the continuous-verifier integral extension.
- Freeze the mixed-pool event and make alternative projections identical outside it for exact `Gamma times delta` interpretation.
- Freeze a mutually exclusive failure-family assignment before outcomes.
- Replace the historical independent-shadow runner with an exact-same-pool prefix runner.
- Rename historical `H/H-hardmine`; it is not the R4 Rejected-Witness arm.
- Include duplicated-winner, random-nonwinner, and SkillCAT-style contrast controls.
- Do not claim novelty for success/failure pairing, first divergence, bounded editing, replay validation, or rejected-edit memory.

## 7. Current decision before model debate

`REVISE_BUT_SURVIVES_FOR_BLIND_DEBATE`

Reason: the mechanism-level object remains distinguishable, but the provisional CADP method is much less novel than the 2026-08-25 synthesis implied. R17 should proceed to blind Kimi/DeepSeek debate only with this tightened collision boundary. No scientific experiment is authorized.
