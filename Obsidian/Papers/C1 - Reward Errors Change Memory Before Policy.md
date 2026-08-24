# C1 · Reward Errors Change Memory Before They Change Policy

Tags: #C1 #agent-memory #reward-error #mechanism #ICLR

Latest executable-closure knowledge version: [[C1 - Executable Closure Gate v3 - 2026-08-24]] (`C1-CLOSURE-v3-20260824`). This page keeps the paper-level evidence summary; the versioned page is authoritative for the current method residual and D0 authority boundary.

## Current paper thesis

The paper separates a persistent-memory error into stages:

`reward label -> durable write -> retrieval exposure -> branch-specific policy uptake -> outcome`

The key result is not simply that reward errors alter text. It is that these stages are empirically separable:

- Shopping write: 20/20 complete success/failure pairs diverge; pooled token Jaccard 0.673.
- Strong same-mode wording reduction: reward divergence 0.700 vs wording 0.595; excess 0.105, p=0.0078.
- Forced injection: terminal |Delta|=0.15625, p=0.00074, passing the frozen 0.15 practical floor.
- Native Shopping exposure: 125/172 held-out retrieval hits after bank expansion.
- Native Shopping terminal: |S-F|=0.02083, p=0.4289; 34/36 zero.
- First-action uptake: TV=0.06944, p=0.5801; 0/36 modal branch-action differences.
- Post-hoc working-memory branch shift: 0.00335, p=0.2052.
- Outcome-blind structured control: 0.04514, p=0.0048, but below the 0.15 floor and 32/36 zero.
- Reddit replication: write 4/4 diverges; native terminal |S-F|=0.125, p=0.2253; 6/8 zero and the two nonzero cells have opposite signs.

The bounded scientific statement is:

> Memory divergence is not behavioral divergence. Reward-conditioned writing is robust; realized branch-specific transport is sparse, stage-dependent, and domain/task dependent.

## Why the current paper still feels unfinished

C1 has moved beyond a shallow phenomenon report, but its current contribution sits between two mature top-tier archetypes:

1. it is not yet as theoretically/causally deep as a pure mechanism paper such as a causal-mediation or mathematical-mechanism study;
2. it has not yet converted the diagnosed failure into a tested intervention.

Therefore its current **paper-development** state is:

`ANALYSIS_INCOMPLETE_FOR_TOP_TIER -> SOLUTION_CLOSURE_DESIGN`

This does not downgrade the validity of the existing analysis.

## Collision audit: what is NOT the new method

- Retrieval vs post-retrieval reuse is already an explicit research object in **Beyond Retrieval / QCR**.
- Generic provenance-preserving authorization is already covered by **Memory Provenance Laundering / PPMF** and **MutMem**-style authorized mutation.
- Generic common-root + residual memory representations are already covered by **DeltaMem**.
- Generic `what happened` vs `how to use it` decomposition is already covered by **Live-Evo**.
- Success/failure reflection itself is ReasoningBank substrate, not novelty.
- Neutral/outcome-blind memory, generic reward/provenance metadata, and metadata-conditioned reuse are **strong simple baselines**, not contributions.

Primary-source anchors for the current collision audit:

- Beyond Retrieval / QCR: https://arxiv.org/abs/2608.12847
- DeltaMem: https://arxiv.org/abs/2606.03083
- Live-Evo: https://arxiv.org/abs/2602.02369
- MutMem: https://arxiv.org/abs/2608.02843
- Memory Provenance Laundering / PPMF: https://arxiv.org/abs/2607.29167
- Function Vectors (mechanism archetype): https://openreview.net/forum?id=AwyxtyMwaG
- PINE (mechanism-to-intervention archetype): https://openreview.net/forum?id=fvkElsJOsN
- CRISP / Fixing the Broken Compass: https://openreview.net/forum?id=hsBBYOqph2

## Mechanism-derived diagnosis

A single potentially wrong reward bit currently receives **undifferentiated write authority** over an entire actionable memory item.

Yet C1's evidence suggests two different components are mixed:

- a branch-invariant procedural core that can remain useful;
- a reward-branch-specific residual whose future validity/applicability is sparse and uncertain.

The repair should target that authority mismatch rather than inventing a generic router.

## Surviving candidate: Counterfactual Branch Residual Gating (CBRG)

For the same byte-identical trajectory `tau`, construct both counterfactual reflections:

`M_S = W_S(tau)`

`M_F = W_F(tau)`

Factorize them into:

`C(tau) = Core(M_S, M_F)`

`D_S, D_F = Residual(M_S, M_F)`

where `C` contains branch-invariant actionable procedure and `D_r` contains claims/rules introduced by the reward branch.

For target query/state `o` and evidence metadata `z_r`, use:

`M_r(tau;o) = C(tau) + g(o, D_r, z_r) * D_r`

The common core remains available; only the branch residual receives conditional actionable authority.

The novelty candidate is **not** core/residual factorization alone, **not** neutral/metadata memory, **not** provenance alone, and **not** semantic applicability routing. Those are baseline-only components. The residual object being tested is narrower:

> the semantic residual induced by counterfactual success/failure reflection of the same byte-identical trajectory, plus **outcome-independent evidence-gated trigger authority** over that residual.

Target similarity/applicability may decide whether a residual is relevant enough to inspect, but it cannot by itself decide that the reward branch is valid. The reward/success/failure label also cannot serve as evidence for its own residual.
A fresh source scan must still verify that no direct prior work subsumes this exact object.

Enforcement is machine-bound, not note-bound: `C1_EXECUTABLE_CLOSURE_REVIEWER_GATE_V3` rejects any revision that promotes the demoted baselines back into novelty, drops same-trajectory/byte-identical pairing, omits claim-bound outcome-independent evidence or its receipt requirement, or grants provider/GPU/scientific authority. A gate PASS allows D0-B design work only.

## Zero-provider D0 before any method experiment

Use already archived 20 Shopping + 4 Reddit paired memories and all frozen native target support. Do not select known positive cells.

D0 asks only whether CBRG is identifiable and non-degenerate:

- Can common core and branch residual be deterministically/reproducibly extracted?
- Is the residual meaningfully smaller/more branch-specific than full memory?
- Does a target-state applicability function vary across the full frozen support rather than always-on/off?
- Does simple neutral-core memory already absorb essentially all actionable content?
- Can evidence/provenance needed by the residual gate be defined without reward outcome leakage?

No provider call, no terminal performance claim, no new scientific authority.

### D0 observed · 2026-08-24

The frozen threshold-free diagnostic has now been executed on 24 archived Shopping+Reddit S/F pairs and 44 native targets, with **0 provider calls**.

- common-core strength mean: **0.6340**;
- residual energy mean: **0.3660**;
- target residual applicability: mean **0.1449**, range **0.0458–0.2729**;
- 8/9 multi-target sources show nonzero target-relevance variation;
- S/F residual-applicability gap: mean only **0.0300**, max **0.0768**.

Interpretation: the representation is not obviously degenerate, and residual relevance varies by target, but **semantic relevance alone is weak at deciding which reward branch deserves authority**. Therefore similarity/applicability-only gating is now a baseline, not the method. This closes D0-A only. Provider execution remains HOLD. D0-B is contract-only and must require an outcome-independent, claim-bound branch-validity signal (for example source/trajectory evidence support/contradiction), with zero-call incremental information beyond semantic relevance before any fresh run.

### D0 STOP

Stop the method extension if:

- neutral/core-only captures essentially all actionable content;
- residual extraction is unstable or mostly restates the common procedure;
- the gate degenerates to always-on/off;
- a simple similarity/applicability rule subsumes the proposed gate;
- current literature directly covers the exact counterfactual branch-residual intervention.

### D0 GO

Only if the above survives, preregister a fresh experiment comparing matched information/cost:

1. original full reward-conditioned memory;
2. outcome-blind neutral/core-only memory;
3. factorized core + residual always-on;
4. **CBRG gated residual**;
5. raw/no-memory controls;
6. clean-label/oracle upper bound where valid.

Primary target: improve the clean-utility vs corrupted-label robustness frontier, not merely reject more memories.

## Manuscript closure if CBRG passes

`phenomenon -> stage-resolved mechanism -> undifferentiated write-authority diagnosis -> CBRG -> controlled reward corruption -> robustness/utility frontier -> design rule`

Engineering rule:

> Terminal reward may guide persistent memory, but a possibly wrong terminal bit should not automatically own the entire actionable memory state.

## If CBRG stops

Do not manufacture another method. Keep C1 as an identification/measurement paper, promote the stage-resolved boundary to the formal contribution, and add a main-text boundary figure. A failed method extension would strengthen the claim that the phenomenon does not automatically imply a useful complex repair.
