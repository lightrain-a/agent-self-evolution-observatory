# C1 · Reward Errors Change Memory Before They Change Policy

Tags: #C1 #agent-memory #reward-error #mechanism #ICLR

Latest executable-closure knowledge version: [[C1 - Executable Closure Gate v4 - 2026-08-25]] (`C1-CLOSURE-v4-20260825`). This page keeps the paper-level evidence summary; the versioned page is authoritative for the current method residual and D0 authority boundary. The active manuscript route is now the stage-resolved identification/measurement story; the stopped CBRG extension is not a claimed method contribution.

## Current paper thesis

Manuscript strengthening status (2026-08-25): `STAGE_EVIDENCE_LADDER_R3B_COLLISION_AUDITED`. R1 separated the old one-step ``reward error -> future behavior'' interpretation into write/exposure/uptake/outcome. R2 added capacity-versus-native-transport control and a six-alternative explanation audit. R3 made the localization rule explicit and reproducible: because memory distance, retrieval rate, action TV, and terminal effect are not commensurate, the paper uses an **ordinal stage-evidence ladder** rather than a synthetic attenuation coefficient. Each native stage keeps its valid evidence state (`SUPPORTED`, `DIRECTLY_OBSERVED`, `NOT_SUPPORTED`, or a typed heterogeneous boundary); the first unsupported native stage after supported/observed prerequisites is the operational attenuation boundary. R3b then stress-tested novelty against current closest work: QCR already owns retrieval-versus-post-retrieval reuse as an explicit object, and recent memory-lifecycle work already names write/store/retrieve/execute/propagate stages. Those generic claims are now demoted. The surviving residual is the **same-trajectory reward-conditioned writer intervention + forced-capacity side control + native ordinal localization**. On the frozen evidence, the first unsupported native stage is `first-action uptake`, so the supported localization is **after exposure and before stable first-action uptake**, explicitly not causal mediation. Machine-readable analyses: `stage-transport-bottleneck-analysis-20260825.json`, `stage-evidence-ladder-analysis-20260825.json`, and `closest-work-stress-audit-r3b-20260825.json`.


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

> Memory divergence is not behavioral divergence. Reward-conditioned writing is robust; forced exposure shows downstream capacity; native retrieval remains substantial; the first stable measured attenuation appears after exposure and before action uptake; terminal transport is sparse and domain/task dependent.

## Current paper-depth diagnosis after R3

C1 should no longer be judged by whether it invents a rescue method. The CBRG route has already STOP/MERGE'd on its qualification contract. The active top-tier archetype is a controlled identification/measurement paper whose depth comes from **localizing a systematically mismeasured scientific object and eliminating simpler explanations**.

R3 now has a single tight inference chain plus an explicit localization operator:

1. **no-state-intervention** is inconsistent with 20/20 Shopping + 4/4 Reddit write divergence and the stronger same-mode control;
2. **global downstream memory insensitivity** is weakened by forced terminal leverage $|\Delta|=0.15625$;
3. **retrieval absence only** is weakened by 125/172 native exposure;
4. **retrieval = policy uptake** is rejected as an evaluation equivalence by TV=0.06944 and 0/36 modal action changes;
5. **universal directional transport** is unsupported by Shopping/Reddit sparsity and Reddit sign reversal;
6. **causal mediation** remains unresolved and is forbidden as a claim because the frozen seed/noise-floor and intervention-surface requirements are not met.

Ordinal localization rule: native stage order is `write -> exposure -> first-action uptake -> terminal outcome`. Write is `SUPPORTED`; exposure is `DIRECTLY_OBSERVED`; first-action uptake is `NOT_SUPPORTED_AT_FROZEN_PRIMARY_TEST`; terminal outcome is `SPARSE_HETEROGENEOUS_NOT_UNIVERSALLY_SUPPORTED`. Therefore the first unsupported native stage is first-action uptake. The forced-capacity arm can weaken global-insensitivity alternatives but cannot make a bypassed native stage pass.

The remaining paper-development debt is therefore presentation/coverage debt, not an unfilled method slot: make the stage-evidence ladder and alternative-explanation audit visually and narratively central, keep negative boundaries visible, and do not reopen CBRG without its four-part evidence contract.

## Collision audit: what is NOT the new method

- Retrieval vs post-retrieval reuse is already an explicit research object in **Beyond Retrieval / QCR**; C1 must not claim this distinction itself as novelty.
- Memory lifecycle decompositions already separate phases such as **Write / Store / Retrieve / Execute / Propagate / Rollback** in recent long-term-memory security work; C1 must not sell stage naming or lifecycle partitioning as novelty either.
- Generic provenance-preserving authorization is already covered by **Memory Provenance Laundering / PPMF** and **MutMem**-style authorized mutation.
- Generic common-root + residual memory representations are already covered by **DeltaMem**.
- Generic `what happened` vs `how to use it` decomposition is already covered by **Live-Evo**.
- Success/failure reflection itself is ReasoningBank substrate, not novelty.
- Neutral/outcome-blind memory, generic reward/provenance metadata, and metadata-conditioned reuse are **strong simple baselines**, not contributions.

Primary-source anchors for the current collision audit:

- Beyond Retrieval / QCR: https://arxiv.org/abs/2608.12847
- Long-Term Memory Security lifecycle survey: https://arxiv.org/abs/2604.16548
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

Enforcement is machine-bound, not note-bound: `C1_EXECUTABLE_CLOSURE_REVIEWER_GATE_V3` rejects any revision that promotes the demoted baselines back into novelty, drops same-trajectory pairing, omits claim-bound outcome-independent evidence or its receipt requirement, or grants provider/GPU/scientific authority. The historical D0-B receipt-envelope gate remains provenance-only; current fail-closed gates additionally enforce **packet-level evidence != claim-level evidence**, **parsed memory atom != certified branch residual**, and **operational branch contrast != atom-level causal purity**. Gate PASS allows zero-call D0 design/audit work only.

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

Interpretation: the representation is not obviously degenerate, and residual relevance varies by target, but **semantic relevance alone is weak at deciding which reward branch deserves authority**. Therefore similarity/applicability-only gating is now a baseline, not the method. D0-A is closed and D0-B0 envelope integrity passes for 24/24 source pairs. The v2 correction reconstructs all 423 memory atoms but finds **0/423 certified branch-residual identities, 0/423 exact claim-specific evidence refs, and 0/423 semantic validity decisions**.

D0-B1a establishes a narrower positive result without new calls: all **24/24** frozen S/F pairs share the same pre-writer trajectory projection, resolve to the same writer model within pair, use temperature 0, and produce different branch memories. The existing eight-task F0C control further shows a reward/reflection-mode effect beyond stronger same-mode prompt paraphrase (between-minus-within **0.104978**, exact one-sided sign-flip **p=0.007812**). This identifies an **operational branch contrast**, not pure causal atoms: the current pool has **0/24 explicit seed bindings** and **0/24 same-condition exact-trajectory replications**. The method therefore uses `Delta(W_success(tau), W_failure(tau))` as the scientific object and does not claim that each textual delta atom is purely caused by the reward label.

D0-B1c now makes that object executable. It compiles **423/423** directional same-field branch-contrast units and scans **58,230** outcome-excluded pre-writer browser-state lines for exact lexical evidence anchors. **397/423 (93.85%)** units bind a nonzero exact anchor; **26/423** remain unlocated and are deliberately not given similarity-only pseudo-evidence. This is locator coverage, not semantic support: validity remains **0/423 adjudicated** and branch authority remains zero.

D0-B2 readiness first reached **HOLD** rather than silently substituting similarity for validity. The bounded local asset audit finds **0** entailment+contradiction-labelled classifier configs, **0** C1 semantic-qualification receipts, and therefore **0** qualified semantic adjudicators. The frozen MiniLM model is an embedding-only `BertModel` with no classifier label map and stays baseline-only. Semantic execution remains locked: no `SUPPORTED`, `CONTRADICTED`, or `UNVERIFIABLE` label has been assigned.

The subsequent v4 zero-call repository inventory closes the current method route rather than inventing a verifier after the fact. Across **597** bounded text/code artifacts, all **12** three-state vocabulary hits and all **6** entailment+contradiction vocabulary hits are C1 self/gate contracts; there are **0 external executable adjudicator candidates** and **0 external semantic-qualification receipts**. Therefore the current CBRG extension is **`STOP_MERGE_CBRG_EXTENSION_NO_QUALIFIED_OUTCOME_INDEPENDENT_VALIDITY_SIGNAL`**. This STOP is scoped to the current frozen method extension: it does **not** invalidate the stage-resolved C1 measurement evidence and does **not** declare a C1 scientific failure. The provider method experiment is not authorized.

Latest versioned knowledge: [[C1 - Executable Closure Gate v4 - 2026-08-25]].

### D0 STOP — FIRED FOR CURRENT CBRG EXTENSION

Stop the method extension if:

- neutral/core-only captures essentially all actionable content;
- residual extraction is unstable or mostly restates the common procedure;
- the gate degenerates to always-on/off;
- a simple similarity/applicability rule subsumes the proposed gate;
- current literature directly covers the exact counterfactual branch-residual intervention.

### Historical D0 GO contract — superseded by terminal STOP

Only a future valid reopen satisfying the v4 four-part reopen contract may return to the following preregistered fresh-experiment design:

1. original full reward-conditioned memory;
2. outcome-blind neutral/core-only memory;
3. factorized core + residual always-on;
4. **CBRG gated residual**;
5. raw/no-memory controls;
6. clean-label/oracle upper bound where valid.

Primary target: improve the clean-utility vs corrupted-label robustness frontier, not merely reject more memories.

## Active manuscript closure after CBRG STOP/MERGE

Do not manufacture another method. Keep C1 as an identification/measurement paper and promote the stage-resolved boundary to the formal contribution:

`phenomenon -> strongest reductions -> forced leverage -> native boundary -> first-action uptake localization -> cross-domain heterogeneity -> evaluation/design rule`

Design implication:

> Reward-induced memory divergence is not equivalent to validated downstream behavioral authority; evaluation must resolve where the effect actually survives the write → exposure → uptake → outcome chain.

The stopped method extension is development evidence that the observed mechanism does not automatically imply a useful complex repair.
