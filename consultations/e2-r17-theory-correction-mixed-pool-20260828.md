# E2-R17 Theory Correction — Rescue Censoring vs Mixed-Pool Learning Support

Date: 2026-08-28
Status: **THEORY_CORRECTION_BEFORE_E1**
Authority: planning/theory only; no E1 outcome authority

## 1. Why this correction is necessary

The frozen E0 analysis correctly established the rescue-censoring identity, but the subsequent V1 planning gate used **rescue-event count** as if it were the support set for the Rejected-Witness learning intervention. That is too narrow.

There are two distinct scientific quantities:

1. **Rescue censoring**: a precommitted failure is rescued by search and hidden by winner-only serving. This quantity exactly explains best-of-K acting gain relative to rollout-0.
2. **Mixed-pool censoring**: the generated pool contains both successful and failed trajectories, while winner-only learning exposes only the successful winner. This is the support set on which a failure-aware learning projection can differ from winner-only.

The first is an acting-side identity. The second is the treatment-support quantity for E1. They coincide only in a special subset of pools and must not be conflated.

This correction does **not** alter, delete, or reinterpret the frozen E0 receipts. It supersedes only the future support gate used to decide whether an updater-side intervention is identifiable.

## 2. Formal object

For a fixed task, initial persistent state, actor, verifier, and nested best-of-K search pool, let

- `T_1, ..., T_K` be the generated trajectories,
- `Y_i in {0,1}` be the binary verifier outcome,
- `W_K` be the served winner, chosen as a success whenever any success exists,
- `U(S, g(T_1:K))` be a frozen updater applied to learning projection `g`,
- `J(.)` be future frozen-skill value on held-out tasks.

The acting projection and learning projection are separate functions of the same frozen search object.

## 3. Theorem A — exact rescue-censoring identity

Let rollout-0/`T_1` be the precommitted no-search action. For an arbitrary joint law over the K rollouts, without independence or exchangeability,

`A_K - A_1 = P(Y_1=0, max_i Y_i=1)`.

Winner-only failure visibility is `P(max_i Y_i=0)`, while precommitted failure visibility is `P(Y_1=0)`. Therefore

`A_K - A_1 = V_pre(K) - V_winner(K)`.

This is the exact identity already validated by the frozen E0 analysis and by the unit tests in `research_pipeline/test_e2_r17_search_projection_theory.py`.

Under i.i.d. success probability `p`,

`Gamma_K(p) = (1-p) - (1-p)^K`.

This quantity peaks at `p* = 1 - K^(-1/(K-1))` for `K>1`.

**Interpretation:** every unit of best-of-K acting gain over the precommitted rollout corresponds to a rescued precommitted failure that winner-only serving no longer exposes.

## 4. Theorem B — nested-search evidence shielding

Define four events/quantities for the exact K-pool:

- `A_K = P(any success)` — acting success,
- `W_K = P(all fail)` — winner-visible failure,
- `F_K = P(any failure)` — full-pool failure availability,
- `M_K = P(any success AND any failure)` — mixed-pool contrast support.

For **nested pools**, pointwise set inclusion gives, with no i.i.d. assumption:

- `A_K` is non-decreasing in K,
- `W_K` is non-increasing in K,
- `F_K` is non-decreasing in K,
- `M_K` is non-decreasing in K.

Thus increasing search compute can simultaneously improve served outcomes while making failure nearly disappear from winner-only learning, even though failed counterevidence remains present in the generated pool.

Under i.i.d. success probability `p`:

- `A_K = 1 - (1-p)^K`,
- `W_K = (1-p)^K`,
- `F_K = 1 - p^K`,
- `M_K = 1 - p^K - (1-p)^K`.

For every fixed `p in (0,1)`, as `K -> infinity`:

- `A_K -> 1`,
- `W_K -> 0`,
- `F_K -> 1`,
- `M_K -> 1`.

This is the core **compute-shielding** regime: user-facing failures vanish while same-task success/failure contrast becomes almost surely available inside the discarded search pool.

`M_K(p)` is symmetric around `p=1/2` and peaks at `p=1/2`. This is different from the rescue-censoring peak `p*` above.

## 5. Expected hidden failed-branch mass

Under i.i.d. rollouts, the expected number of failed branches omitted on pools where the served winner succeeds is

`H_K(p) = K[(1-p) - (1-p)^K] = K Gamma_K(p)`.

This counts available failed branches, not their diagnostic utility. More failed branches do not imply better learning if they are redundant or misleading.

## 6. Theorem C — exact mixed-gated learning factorization

Define a deterministic one-slot projection `g_RW`:

- if the pool is not mixed, `g_RW = g_WIN`;
- if the pool is mixed, `g_RW` selects the lowest-rollout-index failed non-winner, according to a rule frozen before held-out outcomes;
- acting always serves the exact same winner in both arms.

Let

`D = J(U(S, g_RW(T_1:K))) - J(U(S, g_WIN(T_1:K)))`.

Because the two projections are identical outside the mixed event,

`Delta_K = E[D] = M_K * delta_K`,

where

`delta_K = E[D | mixed pool]`.

This factorization is exact by conditioning; it does not assume that `delta_K > 0`.

This separates the paper into two independently testable mechanisms:

1. **availability mechanism:** search changes `M_K`; E0/theory can establish this;
2. **diagnostic-value mechanism:** the censored witness changes future skill, i.e. `delta_K != 0`; only E1 can establish this.

The central learning claim requires `delta_K > 0` in a predeclared regime. If `delta_K = 0`, projection censoring is behaviorally real but learning-irrelevant. If `delta_K < 0`, failure-aware projection is harmful and the proposed repair is rejected.

## 7. Family-wise prospective prediction

For controlled tasks with one predeclared failure family `z` per task, define

- `M_z(K)` = mixed-pool support for family z,
- `delta_z` = conditional future-skill advantage of the mixed-gated witness over winner-only.

For a mutually exclusive family partition,

`Delta(K) = sum_z pi_z M_z(K) delta_z`.

This supports a prospective E3 test: estimate `delta_z` only on development/calibration streams, freeze signs/ranking/K-ordering, then predict held-out confirmatory effects from measured `M_z(K)`.

If failure-family labels overlap, this additive decomposition must not be used without a predeclared partition or another identified attribution scheme.

## 8. Reinterpretation of the frozen E0 pilot

The frozen E0 K=8 result is:

- acting success: `12/12`,
- winner-visible failure: `0/12`,
- mixed pools: `8/12`,
- rescue events: `1/12`,
- hidden failed non-winner trajectories: `16`,
- mixed/failure support spans `5/6` predeclared failure families.

Therefore:

- the **rescue identity** has only one observed task of support;
- the **mixed-pool learning intervention** has eight observed task pools of support;
- using `>=6 rescue tasks` as the E1 treatment-support gate is theoretically misaligned.

The previous E0 `HOLD` remains historically valid under its frozen contract. It must not be silently rewritten. Instead, V2 should record that the old rescue-count gate is superseded for the new mixed-gated estimand before any E1 updater outcome is generated.

## 9. Collision boundary with published ReasoningBank

ReasoningBank (ICLR 2026) already establishes that a memory system can distill from both successful and failed trajectories, and MaTTS aggregates successful and failed trajectories produced by test-time scaling. Its reported failure-trajectory ablation means E2-R17 cannot claim novelty from the statement “failed trajectories are useful.”

The defensible E2-R17 novelty target is narrower and more causal:

1. formally separate acting projection from learning projection on the **same generated search pool**;
2. quantify selection-induced evidence shielding as K changes;
3. keep the served winner, actor calls, initial persistent state, updater, and held-out evaluation fixed while changing only updater-visible evidence;
4. identify `M_K * delta_K` with precommitted projection rules;
5. test whether a **single budget-matched rejected witness** captures the useful information, rather than assuming that full-pool aggregation is necessary;
6. prospectively predict where the effect should vanish or strengthen.

If E1 only reproduces “success+failure memory beats success-only memory,” novelty is insufficient relative to ReasoningBank.

## 10. Null regimes and falsifiers

The theory explicitly predicts no useful R17 effect when any of the following holds:

- `M_K = 0` (all-success or all-failure pool; no success/failure contrast),
- `delta_K = 0` (failed witness is not reusable for future tasks),
- `delta_K < 0` (failed witness is misleading or updater cannot interpret it),
- the production learner already consumes the full search pool or equivalent contrastive evidence,
- future tasks do not share the latent failure mechanism exposed by the witness.

These are scientific boundaries, not implementation failures.

## 11. V2 design consequence

The 42-task E0-full tranche proposed only to satisfy the rescue-count quota should **not** be launched under the old rationale.

V2 should instead use a pre-treatment support gate on the exact pools that would feed E1, with no updater calls before the gate is evaluated. A defensible initial gate is:

- 12 streams x 8 controlled tasks, K=8, all pools frozen first;
- at least `24/96` pools are mixed;
- at least `8/12` streams contain at least two mixed pools;
- mixed support spans at least `4/6` predeclared failure families;
- no pool/task replacement after observing support;
- if the gate fails, stop before any updater call and redesign only under a new protocol.

These thresholds are support/identifiability thresholds, not effect thresholds. They must be independently reviewed before authorization.

## 12. Current scientific state after correction

- Search-induced visibility shift: **SUPPORTED**.
- Exact rescue-censoring identity: **SUPPORTED**.
- Mixed-pool compute-shielding law: **THEORETICALLY ESTABLISHED; E0 CONSISTENT**.
- Positive diagnostic value `delta_K`: **UNKNOWN**.
- Learning regret from winner-only projection: **UNKNOWN**.
- Final repair method: **UNDECIDED**.

The next verdict-changing experiment is still E1, but E1 should be a **mixed-pool-gated exact-same-pool intervention**, not a rescue-event-only intervention.
