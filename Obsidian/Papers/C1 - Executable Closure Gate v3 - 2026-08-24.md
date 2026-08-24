---
knowledge_version: C1-CLOSURE-v3-20260824
paper_id: D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE
paper_title: Reward Errors Change Memory Before They Change Policy
status: D0A_COMPLETE_D0B_CONTRACT_ONLY_PROVIDER_HOLD
supersedes: C1 - Reward Errors Change Memory Before Policy
scientific_provider_calls_added: 0
---

# C1 · Executable Closure Gate v3

Tags: #C1 #agent-memory #reward-error #mechanism #reviewer-gate #D0

## Frozen starting point

C1 has already established a stage-resolved boundary:

`reward label -> durable write -> retrieval exposure -> branch-specific policy uptake -> outcome`

The existing evidence is not reopened here. The current paper-level conclusion remains:

> Reward-conditioned writing is robust, but memory divergence is not behavioral divergence; branch-specific native transport is sparse, stage-dependent, and domain/task dependent.

This version only decides which mechanism-derived repair is still scientifically admissible before any new execution.

## Baseline-only ledger

The following objects are frozen as **baselines or collision territory**, not C1 method novelty:

1. **Neutral / metadata memory** — outcome-blind neutral memory, provenance/reward tags, or metadata-conditioned reuse by themselves.
2. **Generic common-core / residual factorization** — extracting shared content and residual content without a new identifiable authority variable.
3. **Semantic similarity / applicability gating** — target relevance is useful as a same-information baseline, but D0-A showed it is weak at selecting which reward branch deserves authority.
4. **Generic query-conditioned reuse** — retrieval-vs-use and target-bound reuse are already explicit neighboring objects.
5. **Generic provenance-preserving authorization** — provenance firewall / signed mutation governance is prior territory.
6. **Success/failure reflection** — existing substrate, not a contribution.

These components may remain in an implementation only as controls or measurement interfaces. Renaming, stacking, or adding a learned router does not restore novelty.

## Only surviving candidate residual

The only C1 method residual currently allowed to remain a D0 candidate is:

> **same-trajectory counterfactual branch residual + outcome-independent evidence-gated trigger authority over that residual.**

For one byte-identical trajectory `tau`:

`M_S = W_S(tau)`

`M_F = W_F(tau)`

A common/residual compiler may expose:

`C(tau) = Core(M_S, M_F)`

`D_S, D_F = Residual(M_S, M_F)`

but this factorization is only a baseline interface. The candidate method begins only at the authority decision.

Separate two variables:

`a_r(o) = Applicability(o, D_r)`

`e_r = EvidenceValidity(D_r, E_tau)`

where:

- `a_r(o)` asks whether the residual is relevant to the target state/query;
- `e_r` asks whether source/trajectory evidence supports, contradicts, or cannot verify the residual claim;
- `E_tau` must be derived from outcome-independent source/trajectory facts available under the frozen contract;
- the reward/success/failure label is **not** admissible evidence for `e_r`.

The actionable memory is conceptually:

`M_r(tau;o) = C(tau) + G(a_r(o), e_r) * D_r`

with the hard reviewer requirement:

`G(a, unknown/contradicted) != authority solely because a is high`.

In other words, semantic relevance may determine whether a residual is worth considering, but only evidence can justify branch-specific actionable authority.

## Why this residual survives the baseline reductions

C1's diagnosed failure is not “memory lacks metadata” and not “memory should be factorized.” It is an **authority mismatch**:

> one potentially wrong terminal bit can select an entire actionable rewrite even though most reusable procedure is branch invariant and the branch-specific residual has sparse future uptake.

The candidate therefore changes only the authority assigned to the treatment-induced residual. It does not claim novelty for neutral memory, metadata, common-core extraction, residual representation, or applicability routing.

## D0-A · completed zero-call result

D0-A reused 24 archived Shopping+Reddit S/F pairs and 44 frozen native targets with 0 provider calls.

Observed:

- common-core strength mean: **0.6340**;
- residual energy mean: **0.3660**;
- target residual applicability mean: **0.1449**, range **0.0458–0.2729**;
- 8/9 multi-target sources have nonzero applicability variation;
- S/F residual-applicability gap mean: **0.0300**, max **0.0768**.

Decision:

- core/residual representation is feasible enough to remain a baseline interface;
- target relevance is non-degenerate;
- **semantic applicability alone fails the branch-authority requirement and is frozen as a baseline**;
- no provider execution is authorized.

## D0-B · structural receipt audit passed; semantic evidence authority remains HOLD

No new scientific experiment is opened in this revision. The first D0-B subgate has now been executed as a frozen **zero-call structural audit**; semantic validity is still unadjudicated.

D0-B must answer, on outcome-independent archived/frozen support:

1. Can each branch-specific residual be decomposed into auditable claims/rules that bind back to exact source/trajectory evidence?
2. Can evidence support / contradiction / unverifiable status be computed without reading the terminal reward label as evidence?
3. Does this evidence-validity signal vary across residual claims rather than collapsing to always-support or always-abstain?
4. Does it add information beyond semantic applicability/similarity on the same support?
5. Is the incremental signal reproducible under deterministic or preregistered extraction rules?
6. Does the exact method residual remain open after the required fresh collision gate?

### D0-B GO

`D0_DESIGN_ELIGIBLE` only if all conditions hold:

- exact same-trajectory counterfactual branch residual is preserved;
- evidence validity is outcome-independent and claim-bound;
- reward label never serves as self-validating evidence;
- semantic applicability alone cannot reproduce the authority decisions;
- the evidence signal is non-degenerate and adds incremental information beyond the strongest same-information baseline;
- current closest work does not subsume the exact residual.

The structural subgate is now `GO`: **24/24** frozen source pairs (20 Shopping + 4 Reddit) can be content-addressed back to an outcome-excluded pre-writer trajectory projection, the exact recomputed writer-input action summary, both branch-memory hashes, deterministic residual-claim IDs, and released pre-writer browser-state evidence. This creates **423** bound residual-claim IDs, but semantic validity is assigned to **0/423** claims and **0** receipts carry nonzero branch authority. Current verdict: `D0B_STRUCTURAL_GO_SEMANTIC_AUTHORITY_HOLD`.

A full D0-B GO still requires the remaining evidence-validity and incremental-information questions to pass. The structural GO grants **zero** scientific/provider/GPU/claim-expansion/submission authority.

### Machine binding

This page is not the enforcement surface. The versioned JSON program is bound to `C1_EXECUTABLE_CLOSURE_REVIEWER_GATE_V3` in `research_pipeline.methodology_controls`. The machine gate permits D0 design only when the novelty set is exactly the same-trajectory counterfactual branch residual plus evidence-gated trigger authority; all neutral/metadata, generic core/residual, semantic applicability, query-conditioned reuse, provenance authorization, and success/failure reflection components remain baseline-only. It also requires byte-identical trajectory pairing, outcome-independent claim-bound evidence, receipt-before-authority, fail-closed handling of contradicted/unverifiable evidence, fresh collision clearance before ProblemGate, a zero provider-call D0 budget, and zero downstream authority. The evidence receipt itself must be content-addressed and bind the exact trajectory hash, both branch-memory hashes, residual-claim identity, exact evidence refs/hashes, validity state, extractor/adjudicator versions, and the resulting authority decision; the receipt can never escalate scientific or provider authority.

The machine now registers both the residual-design gate and a second fail-closed D0-B structural-observation gate. A PASS means the contract shape is admissible and the 24-pair receipt structure is reproducibly bindable while semantic authority remains false. It does **not** mean “D0-B passed scientifically,” “423 claims are supported,” or “fresh execution authorized.” Any future artifact that changes semantic-adjudicated claims or nonzero branch authority away from zero without a separately versioned semantic adjudicator fails this structural gate.

### D0-B STOP / MERGE

Stop or merge the method extension if:

- neutral/metadata memory captures the same decisions;
- generic core/residual plus always-on residual captures the same decisions;
- semantic similarity/applicability captures the same decisions;
- evidence validity is just a transformed reward/success/failure label;
- evidence cannot be bound to source/trajectory facts without outcome leakage;
- the gate becomes almost always-on or almost always-off;
- the exact residual is directly covered by current closest work.

If STOP occurs, preserve C1 as a stage-resolved identification/measurement paper. Do not generate another method merely to force a closed-loop story.

## Fresh experiment remains locked

Only after D0-B, fresh collision clearance, Problem/Economy review, and a separately frozen experiment contract may a later Agent propose execution.

The eventual matched arm family must keep at least:

- no memory;
- raw trajectory;
- released reward-conditioned memory;
- neutral/metadata baseline;
- generic common-core/residual always-on baseline;
- semantic applicability baseline;
- matched query-conditioned reuse baseline;
- **same-trajectory branch residual + evidence-gated authority candidate**;
- clean-label/oracle upper bound where scientifically valid.

The primary question is not “does the gate reject bad memory?” It is whether evidence-gated residual authority improves the clean-utility / controlled-reward-corruption robustness frontier beyond the strongest same-information and matched-cost baseline without collapsing utility through blanket suppression.

## Authority snapshot

- new scientific provider calls in this revision: **0**;
- new GPU scientific runs: **0**;
- scientific authority: **false**;
- provider authority: **false**;
- GPU authority: **false**;
- claim-expansion authority: **false**;
- submission authority: **false**;
- next permitted action: **D0-B zero-call semantic evidence-adjudicator design/audit only**; fresh provider execution remains locked.
