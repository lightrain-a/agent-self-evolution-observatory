# Fresh independent paper-strength discussion — E2-R17 after paper-story re-review PASS

Date: 2026-09-03
Role: independent senior ICLR/NeurIPS/ICML agent-systems reviewer and research strategist

## Purpose

This is NOT a third protocol review and NOT a request to protect the current story because prior reviewers passed it. The V3 Stage-A R2 execution protocol is already frozen and independently reviewed; the revised paper-story object also passed a fresh re-review after three claim-level fixes. No V3 Stage-A or Stage-B outcome exists. Do not infer one.

Your task is to pressure-test the *remaining paper strength* from first principles: even if the current V3 mechanism experiment later passes exactly as preregistered, what is the strongest technically credible reason a top-conference reviewer could still reject the paper? Then determine the smallest evidence arc that would turn the current controlled mechanism into a compelling paper without a benchmark zoo.

## Frozen anchors

- live branch before this discussion: `966088327f52f13ce45fb53cd626a91b4ba9b329`
- frozen scientific R2 commit: `29799c83c662887694db52acba4bb19e83131bb0`
- frozen R2 contract SHA256: `f5382c552f2e6644e4cbda408510119664a8c6f8502628586c9ff5583abd1234`
- revised paper-story commit: `773ac34691a81399581fa4728779b764c3ccfadc`
- revised paper-story SHA256: `40880034542a7dd28e9eece2ac38036659c5be790dbd6977267cae31175015ab`
- fresh paper-story re-review verdict: `PASS_PAPER_STORY_TO_EXISTING_STAGE_A_BOUNDARY`
- provider calls for V3/R2 so far: 0
- Stage-A authority: false
- Stage-B authority: false

Do not reopen already-passed execution mechanics unless the paper-strength argument requires a claim that R2 cannot identify.

## Current paper object after the accepted fixes

The paper no longer claims novelty for merely learning from failures, rejected rollouts, sibling contrast, multi-trajectory learning, persistent textual skill updates, or generic experience diversity.

The current scientific object is:

> **Causal identification of the serving-to-persistent-learning projection interface over an exact shared test-time search object.** Test-time search realizes a common experience pool `T_K`. Acting consumes `a(T_K)` and persistent updating consumes `g(T_K)`. E2-R17 holds the exact realized pool and served behavior fixed and intervenes only on the learner-visible projection, then measures future frozen-skill utility.

`Act–Learn Dual Projection` is only the organizing abstraction. `Search-Projection Censoring` is the motivating observable phenomenon. The claimed irreducible novelty is the exact-same-pool, acting-fixed causal interface plus prospective effect modification if V3 passes.

The outcome-neutral thesis currently frozen before V3 outcomes is:

> Test-time search creates a shared experience object whose serving and persistent-learning projections are distinct causal interfaces; exact-same-pool interventions can isolate the learning consequence of that projection and prospectively test whether it is modified by task structure.

The memorable sentence “the best trajectory to act on is not always the best to learn from” is explicitly LOCKED until a prespecified simple effect actually shows an alternative learning projection improving future skill over the served-winner projection.

## Existing completed evidence that is fixed

Historical availability/support evidence establishes that winner-coupled learning can omit already-generated evidence and that mixed pools exist. It is treatment-support/motivation, not proof that the omitted evidence is useful.

The completed DeepSeek global exact-same-pool study is fixed as:

- 12 streams / 48 paired replicates
- WIN-C ≈ 79.05%
- universal MRW ≈ 81.37%
- mean difference +2.3148pp
- paired-bootstrap 95% CI ≈ [-1.85pp, +6.60pp]
- exact one-sided sign-flip p = 0.171875
- frozen verdict: `HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS`

The corrected interpretation is ONLY:

> A reliable global MRW benefit was not established. The result is compatible with underpower, effect heterogeneity, or both. It generated several possible explanations; V3 prospectively freezes one moderator explanation on fresh units.

It must NOT be described as already demonstrating heterogeneity or non-universality.

## Prospective V3/R2 scientific target

Five independent matched skeletons are the confirmatory scientific units. Within each skeleton the design crosses:

- `PROCEDURAL_TRANSFORMATION`
- `INSTANCE_BINDING_LOCALIZATION`

while holding the specified structural nuisance factors fixed. R=4 is measurement replication only.

The primary skeleton interaction is conceptually:

`I_h = effect(MRW4 - WIN-C | procedural) - effect(MRW4 - WIN-C | binding)`.

A V3 PASS means only that the prespecified interaction direction is supported across all five frozen controlled skeletons (finite-five directional resolution 1/32), with all five magnitudes reported. It does NOT automatically establish:

- MRW4 > WIN-C in either cell;
- failures are uniquely useful;
- population-level procedural-vs-binding generality;
- deployability;
- cross-model generality;
- a universal semantic routing law.

A V3 FAIL rejects this moderator explanation. Router performance, replicate-level significance, subsets, aggregate averaging, or R=4 cannot rescue it.

The frozen observable router is hand-engineered and task-visible. It is proof-of-implementability / policy consequence only, not semantic discovery and not a top-level contribution.

## Closest-work collision boundary

Generic experience utilization is already crowded by ReasoningBank/MaTTS, SkillCAT, SkillRevise, Rethinking Self-Evolving Agent Skills, WikiSkill, and related success/failure or multi-trajectory persistent-learning work. The paper must survive only on the more specific interface/identification object.

A reviewer can also analogize the abstraction to logging policy, replay/data selection, selective labels, experience curation, and train/serve interface design. Therefore “two projections” terminology alone is weak novelty.

## The remaining unresolved scientific questions

Please discuss these adversarially and explicitly.

### 1. Strongest remaining rejection case

Assume V3 passes exactly as frozen. What is the single strongest *scientific* reason a top-conference reviewer could still reject the paper? Choose one dominant objection rather than listing generic weaknesses.

Possible threats to consider, but do not mechanically accept them:

- exact-same-pool causal identification is clean but too substrate-specific / synthetic to matter;
- the structural moderator is author-constructed and may merely expose generator semantics;
- the interaction could be statistically positive while all simple effects still favor WIN-C, leaving no actionable act/learn mismatch;
- the work may still reduce to a careful logging/data-selection experiment rather than a novel agent-learning principle;
- failure-vs-generic-alternative remains under-identified;
- five independent mechanism units may be too small for a main-track empirical claim.

### 2. Is a V3 PASS without any positive MRW simple effect actually enough?

Suppose all five interaction directions are positive, but MRW4 is worse than WIN-C in both semantic cells for every skeleton, merely *less bad* in procedural than binding. Is that still a strong top-conference scientific result, or only a moderator curiosity? State exactly what paper thesis survives in that case.

### 3. What simple-effect pattern would unlock the stronger thesis?

Define the minimum result pattern needed to legitimately state an existential version of:

> acting-optimal served evidence and learning-preferred evidence can diverge.

Do not require universal MRW superiority. Specify whether one prespecified cell/skeleton, all procedural cells, an aggregate procedural effect, or another criterion is scientifically appropriate.

### 4. If exactly ONE post-V3 experiment can be afforded, choose one

Conditional on V3 PASS, choose exactly ONE of these directions or propose a better single experiment:

A. failure-specificity control: failed nonwinner versus matched successful nonwinner / neutral alternative;
B. one natural/out-of-family transport test with identity unavailable and projection choice based on ordinary pre-update observables;
C. a simple-effect confirmation tranche focused on establishing an actual MRW4 > WIN-C region under the already-frozen moderator;
D. one second backbone on the same controlled design;
E. no extra experiment; write the controlled causal paper as-is.

For your chosen experiment specify: treatment, controls, scientific unit, primary endpoint, the exact claim it can unlock, and a hard stop rule. Do not recommend broad benchmark/model expansion.

### 5. Natural transport versus mechanism purity

Previous review judged natural/out-of-family transport unnecessary for the controlled causal paper itself. Challenge that conclusion. Would a skeptical main-track reviewer accept five author-constructed matched skeletons as the principal confirmatory mechanism evidence, or is one natural transport result practically verdict-changing even if not logically required for causal identification?

### 6. Failure-specificity versus projection-specificity

Can the paper remain scientifically strong if it never identifies failure-specific value and only claims that *alternative learner-visible projections of a fixed search object have structure-dependent effects*? Or does closest-work collision make failure-specific decomposition necessary for novelty?

### 7. Novelty against generic logging / replay / curation

Give the strongest reduction of E2-R17 to established logging/data-selection concepts. Then state the exact empirical/theoretical ingredient that prevents that reduction, if any. If no ingredient prevents it, say so and recommend a pivot.

### 8. Theory burden

Does the rescue/search-projection censoring identity add real predictive content, or is it mostly obvious accounting once winner-only projection is assumed? What theoretical result or prospective prediction should be emphasized so the theory is not decorative?

### 9. Best final paper identity if V3 PASS

Choose exactly one dominant identity:

- causal systems/interface paper;
- mechanism paper;
- method/policy paper;
- negative/diagnostic paper;
- another precise identity.

Do not call it several things at once.

### 10. Best final paper identity if V3 FAIL

Would the remaining interface + censoring + negative causal evidence plausibly justify a standalone main-track paper, a workshop/short paper, a merge into a broader self-evolution paper, or STOP? Choose one and justify.

### 11. Contribution hierarchy

Give the final 2–3 contributions you would permit in the abstract if V3 passes. Delete any contribution that is mostly terminology or already occupied by closest work.

### 12. Immediate action

Given that Stage-A R2 and the revised paper-story already passed independent pre-outcome review, choose exactly one:

1. PROCEED_EXISTING_STAGE_A — no further pre-Stage-A scientific redesign;
2. ADD_ONE_ZERO_PROVIDER_FIX_BEFORE_STAGE_A — specify it precisely;
3. STOP_OR_PIVOT_BEFORE_STAGE_A — scientific object is still too weak.

Do not use future V3 outcomes to justify changing the frozen R2 design.

## Required final synthesis

End with all of the following:

- `single_biggest_remaining_risk`: one sentence;
- `v3_pass_without_positive_simple_effect`: STRONG_ENOUGH / NARROW_BUT_PUBLISHABLE / TOO_WEAK;
- `one_post_v3_experiment`: exactly one experiment name;
- `paper_identity_if_pass`: exactly one identity;
- `paper_identity_if_fail`: exactly one identity/action;
- `immediate_action`: exactly one of PROCEED_EXISTING_STAGE_A / ADD_ONE_ZERO_PROVIDER_FIX_BEFORE_STAGE_A / STOP_OR_PIVOT_BEFORE_STAGE_A;
- at most THREE verdict-changing recommendations.

Then end with exactly one verdict token:

`KEEP_AND_PROCEED_STAGE_A`
`PROCEED_STAGE_A_BUT_PAPER_NEEDS_POST_V3_CLAIM_EXPANSION`
`REVISE_BEFORE_STAGE_A`
`PIVOT_NOW`
`STOP_E2_R17`
