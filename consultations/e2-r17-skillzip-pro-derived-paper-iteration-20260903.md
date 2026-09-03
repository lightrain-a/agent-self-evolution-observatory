# E2-R17 — SkillZip & SkillZip Pro Derived Paper Iteration

Date: 2026-09-03
Status: `ZERO_PROVIDER_PAPER_ITERATION_ONLY`
Frozen R2 scientific commit: `29799c83c662887694db52acba4bb19e83131bb0`
Frozen R2 contract SHA256: `f5382c552f2e6644e4cbda408510119664a8c6f8502628586c9ff5583abd1234`

This note applies three lessons from SkillZip/SkillZip Pro—research methodology, experiment design, and writing architecture—to E2-R17. It does not change R2 treatments, units, provider budget, primary interaction gate, or execution authority.

## 1. Scientific-object upgrade

SkillZip moves from “compress a long prompt” to “represent an evolved skill as a typed procedural contract.” SkillZip Pro moves again from “one text document” to “a progressively loaded resource bundle whose root, path, deployment and per-run costs differ.”

E2-R17 should make the analogous move:

```text
weak:      are failed trajectories better learning data?
stronger:  a realized search object T_K feeds two interfaces

           T_K
            ├── a(T_K) -> current served behavior
            └── g(T_K) -> persistent updater evidence
```

The paper identity is therefore `CAUSAL_SYSTEMS_INTERFACE_PAPER`. `Act–Learn Dual Projection` is an organizing abstraction; `Search-Projection Censoring` is the motivating phenomenon; Selective-MRW/router is secondary.

## 2. Separate availability, causal consequence, and policy

Do not collapse three questions:

1. **Availability/censoring:** did `T_K` contain evidence that `g_WIN(T_K)` omitted?
2. **Causal consequence:** holding exact `T_K` and acting fixed, does changing only `g(T_K)` change future frozen-skill utility?
3. **Policy:** can a pre-update observable rule choose projections usefully?

Censoring/support is not proof of useful evidence. Router success cannot rescue a failed causal mechanism.

Pre-outcome wording should be:

> winner-coupled learning can make already-generated evidence unavailable; whether that omitted evidence improves persistent learning is a separate causal question.

## 3. One metric is not enough

SkillZip Pro rejects one compression ratio because an edit may reduce storage while worsening always-loaded or per-run cost. E2-R17 has the same systems mistake if it reports only current task success.

The paper should separate four layers:

| Layer | Object | Question |
|---|---|---|
| Generated | `T_K` | What evidence existed? |
| Served | `a(T_K)` | What was used for current behavior? |
| Learner-visible | `g(T_K)` | What crossed into persistent learning? |
| Persistent outcome | `U_future` | What was learned for later tasks? |

Main figures/tables should display current acting and future learning together, making clear that the R17 intervention holds the former fixed and changes the latter.

## 4. Use the two wrong extremes to motivate the interface

### Extreme A — serving-only winner coupling

Best-of-K improves/currently selects the served trajectory but can remove nonwinner evidence from learner visibility. This establishes an observation boundary, not harm.

### Extreme B — universal rejected-witness learning

The completed DeepSeek study did not establish reliable universal-MRW benefit:

- WIN-C ≈ 79.05%;
- universal MRW ≈ 81.37%;
- +2.3148 pp;
- 95% bootstrap interval crosses zero;
- exact one-sided sign-flip `p=0.171875`;
- frozen verdict `HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS`.

Therefore neither “learn only from the served winner” nor “always replace winner evidence with rejected failure evidence” is justified as a universal learning rule.

The natural question is:

> **When should the persistent-learning projection differ from the serving projection?**

This is the direct narrative bridge into V3.

## 5. Repair the simple-effect claim ambiguity before outcomes

The frozen V3 protocol already declares that all five `D_h,PROCEDURAL` and all five `D_h,BINDING` will be reported after the primary interaction gate. But reporting all ten measurements does not make a later cherry-picked positive cell a prospective confirmatory witness.

A prior reviewer suggested `mean_h D_h,PROCEDURAL > 0` plus an exact `2^5` sign-flip test with `p<=1/32`. With five skeleton effects and the mean/sum statistic, the minimum one-sided `1/32` requires all five observed procedural effects to be positive; any negative effect can be sign-flipped to yield a larger statistic, making `p>=2/32`.

Freeze the claim-adjudication rule explicitly:

```text
SECONDARY_CONTROLLED_DIVERGENCE_GATE = PASS
iff
  primary V3 interaction gate == PASS
  AND
  D_h,PROCEDURAL > 0 for all five frozen skeletons.
```

Interpretation: `5/5` procedural simple effects positive; the all-positive configuration is one of the `2^5 = 32` possible sign patterns. This is a finite-suite directional claim gate, not a newly claimed inferential `p=1/32` test.

This gate does **not** alter the primary V3 mechanism verdict. If it passes, the controlled-suite paper may state that the alternative learner projection outperformed WIN-C across all five preregistered procedural-transformation skeletons while exact search pools and acting were held fixed. If it fails, no favorable skeleton may be selected after outcomes to unlock the stronger act/learn-divergence thesis.

## 6. Reorganize experiments as research questions

### RQ1 — Does serving create a measurable learning-observation boundary?

Measure generated evidence versus winner-coupled learner visibility, mixed-pool support, and the valid rescue/censoring identity. Claim only availability/support.

### RQ2 — Does learner projection causally matter?

Use exact-same-pool, acting-fixed intervention. The completed global DeepSeek result belongs here and must remain inconclusive: global benefit not established.

### RQ3 — Is the projection effect prospectively structure-dependent?

This is V3/R2: five matched skeleton interactions `I_h`; `R=4` is measurement replication only; primary 5/5 interaction gate.

### RQ4 — Is there a controlled regime of genuine act/learn divergence?

Use the frozen secondary procedural simple-effect gate above. Keep interaction and simple effect as separate scientific questions.

### RQ5 — Does the effect transport outside the author-constructed suite?

Only after the controlled branch warrants expansion. Run exactly one `OUT_OF_FAMILY_OBSERVABLE_PROJECTION_TRANSPORT_TEST`: natural/public or naturally occurring task units; identity unavailable; eligibility from ordinary pre-update observables; exact same realized pool and acting fixed; primary endpoint is positive future-skill simple effect. If it fails, do not switch family, tune eligibility, mine subsets, or start a benchmark zoo.

## 7. Baseline logic

Mechanism comparison:

- `WIN-C`: tied serving/learning projection;
- `MRW4`: exact same serving, alternative learner projection.

Policy comparison only after mechanism PASS:

- Always WIN-C;
- Universal MRW4;
- Difficulty-only routing;
- Mixedness-only routing;
- Frozen observable router.

Closest work should be compared by scientific intervention object: whether it identifies the learning-projection effect while holding the exact realized search pool and served behavior fixed. Do not force unrelated source-faithful methods into an artificial benchmark table merely to create breadth.

## 8. Theory should predict experiment outcomes

Do not sell “there are two projections” or “winner-only removes nonwinners” as theoretical novelty.

Emphasize predictions that can fail:

1. **availability:** search-projection censoring peaks in the rescueable/intermediate regime under the assumptions where the analytic identity applies;
2. **value/moderation:** alternative learner evidence has a larger future-skill effect in reusable procedural-transformation cells than in instance-binding/localization cells.

The second is exactly what V3 tests prospectively.

## 9. Main-figure plan

### Figure 1 — scientific object

Show `T_K -> a(T_K)` and `T_K -> g(T_K)`; keep `T_K` and acting fixed while changing only `g`. Add one mixed-pool example. Router stays out of Figure 1.

### Figure 2 — one metric is not enough

Show the four layers: generated evidence -> served/current behavior -> learner-visible evidence -> future frozen skill. Explain why current pass@K cannot characterize persistent self-evolution.

### Figure 3 — V3 crossed mechanism

Five skeletons × procedural/binding cells; same pool/acting; WIN-C vs MRW4; define `D_h,z` and `I_h`; show primary interaction gate and secondary procedural-divergence gate separately.

## 10. Main-table plan

### Table 1 — closest-work object comparison

Columns: multi-trajectory search; persistent object; explicit learner-visible experience selection; served behavior fixed; exact realized pool fixed; causal projection intervention; prospective moderator. Put E2-R17 last.

### Table 2 — acting and learning read together

Columns: condition; same `T_K`; same served winner; learner projection; current acting utility; future frozen-skill utility.

### Table 3 — do not average away the five mechanism units

One row per skeleton with `D_h,PROCEDURAL`, `D_h,BINDING`, `I_h`, primary sign, and secondary procedural-divergence sign.

## 11. Introduction architecture

1. **System practice:** self-evolving agents increasingly combine test-time search with persistent skill/memory updates.
2. **Hidden unit mismatch:** search generates a richer object, but serving one trajectory can also determine what the learner sees.
3. **Why obvious extremes fail:** winner-only may censor evidence; universal rejected-witness replacement has no established global advantage.
4. **Scientific object:** define `T_K`, `a(T_K)`, `g(T_K)` and exact-same-pool causal intervention.
5. **Mechanism hypothesis:** structural effect modification, tested on five matched skeletons.
6. **Claim ladder:** primary interaction; separately frozen positive simple-effect gate; later one natural transport test only if warranted.

Do not open with Selective-MRW or the router.

## 12. Method-section architecture

1. Search object and serving/learning interfaces.
2. Search-projection censoring as availability, without assuming utility.
3. Exact-same-pool causal intervention and invariants.
4. Prospective structural moderator and five independent units.
5. Observable router only as downstream proof-of-implementability.

## 13. What to learn from SkillZip Pro's upgrade over SkillZip

The important move is not “more modules.” The predecessor solved a smaller object; Pro argues that the real production object is a progressively loaded bundle. E2-R17 should make the same closest-work distinction:

```text
closest work:
  how should an agent learn from successes/failures/multiple trajectories?

E2-R17:
  once search already generated multiple trajectories and serving selected one,
  what projection of that exact realized search object reaches persistent learning?
```

The novelty comparison should therefore be about the **causal interface/intervention object**, not about whether prior work contains MRW, a router, or the same failure labels.

## 14. Evidence ladder

- **Level 0:** censoring/support measurable; exact-same-pool design valid; global universal-MRW benefit not established.
- **Level 1:** V3 primary five-skeleton interaction gate. FAIL -> no standalone strong mechanism rescue.
- **Level 2:** secondary `5/5 D_h,PROCEDURAL>0` controlled-divergence gate. PASS -> unlock controlled act/learn-divergence statement.
- **Level 3:** one natural/out-of-family observable transport experiment if needed for standalone paper strength. FAIL -> no replacement family/benchmark zoo.
- **Level 4:** second backbone is robustness only and cannot rescue Levels 1–3.

## 15. Title ladder

Before positive simple-effect evidence:

**Decoupling Serving and Persistent Learning over Test-Time Search**

Subtitle: *Exact-Same-Pool Causal Tests of Search-Projection Censoring in Self-Evolving Agents*

Only after the controlled-divergence gate passes:

**The Best Trajectory to Act On Is Not Always the Best to Learn From**

The paper should never be titled around Selective-MRW.

## 16. Immediate action

1. Freeze the secondary procedural simple-effect rule as a zero-provider claim-adjudication artifact.
2. Rewrite the paper outline around RQ1–RQ5 and the four-layer system object.
3. Keep the existing R2 fresh-identity -> separately authorized Stage-A path unchanged.
4. Do not run natural transport, failure-specificity controls, or a second backbone before the V3 gates warrant them.

Current Stage-A and Stage-B scientific authority remain false.
