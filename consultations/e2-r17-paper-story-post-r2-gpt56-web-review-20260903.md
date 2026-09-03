# Independent GPT-5.6 Sol paper-story review — E2-R17 post-R2

Date: 2026-09-03
Role: independent adversarial ICLR/NeurIPS/ICML agent-systems paper-story reviewer
Review target: post-R2 E2-R17 paper object / novelty / claim ladder, **not** another Stage-A protocol review

## Provenance

- Frozen review brief: `oracle_briefs/E2_R17_PAPER_STORY_POST_R2_INDEPENDENT_REVIEW_20260903.md`
- Brief SHA256: `b8ed5543fa9f1c729b197ac6fb88f0b1c2de546633cbbb3509e9bb77528c1eb2`
- Paper-story source commit reviewed: `1eb852670551abb6649a796396c8ec93c1499860`
- Paper-story source SHA256: `f4d2e81a4f47895a490d69d3accf87c89b208cdc2a865d70b063a9d83f13ba5d`
- Frozen R2 scientific commit: `29799c83c662887694db52acba4bb19e83131bb0`
- Frozen R2 contract SHA256: `f5382c552f2e6644e4cbda408510119664a8c6f8502628586c9ff5583abd1234`
- Browser reviewer: ChatGPT web, `GPT-5.6 Sol`
- Thinking effort: `Extra High, 4 of 5`
- Model verification: model picker `GPT-5.6 Sol` had `aria-checked=true`; composer intelligence slider showed `Extra High, 4 of 5`
- Conversation URL: `https://chatgpt.com/c/6a9988c4-5d58-83e9-be48-012f36d6db42`
- Submitted user turns: exactly `1`
- Prompt resend after submission: `false`
- Raw reviewer response SHA256: `cd75be4d7c88298a8a714a4a97243977016476703cc91d11b05f535f9886c845`
- Raw response length: 21,699 characters / 539 lines as captured on Oracle host
- Oracle-host raw response path: `/root/e2_r17_paper_story_review_full.md`
- V3/R2 scientific provider calls caused by this review: `0`

### Browser-throttle incident

After the single prompt submission, the shared ChatGPT account briefly displayed a `Too many requests` overlay while another unrelated GPT-5.6 Sol / Extra-High Oracle job was active. The E2-R17 prompt was **not resubmitted**. The same conversation later hydrated one complete assistant turn; re-reading the same conversation recovered the full 21.7k-character answer. No second E2-R17 user turn was created.

## Exact verdict

`REVISE_PAPER_OBJECT_BEFORE_STAGE_A`

The reviewer explicitly did **not** request an R2 experiment redesign and did **not** request another experiment before Stage A. Its recommended control flow was:

`MAKE_ZERO_PROVIDER_STORY_FREEZE_THEN_PROCEED_WITH_EXISTING_R2_STAGE_A_BOUNDARY_WITHOUT_EXPERIMENT_REDIRECTION`

## Reviewer’s central diagnosis

There is a real paper, but the irreducible contribution is narrower than the pre-review story implied. `Act–Learn Dual Projection` as terminology is not enough: a reviewer can reduce that abstraction to familiar logging policy, replay/data selection, selective observation, or experience curation. Likewise, merely observing that best-of-K winner-only logging discards nonwinners is nearly tautological.

The strongest surviving scientific object is the **combination** of:

1. one shared realized search object `T_K`;
2. acting fixed through `a(T_K)`;
3. persistent-learning evidence independently manipulated through `g(T_K)`;
4. an exact-same-pool intervention that changes the learner-visible projection while holding search generation, served behavior, initial state, updater, budget, and update order fixed;
5. prospectively frozen structural effect modification if V3 succeeds.

The reviewer therefore recommends selling an **identification framework / causal interface**, not the dual-projection terminology itself and not generic “learning from failures.”

## A–L audit summary

### A — Scientific object / novelty

- Dual-projection terminology alone: weak novelty.
- Search-projection censoring as a measurable systems phenomenon: moderate conceptual value, insufficient alone.
- Exact-same-pool acting-fixed causal intervention: strongest surviving novelty.
- Prospectively specified effect modification of that intervention: potentially strong if V3 passes.

Irreducible object: in a persistent self-evolving agent with test-time search, serving induces an observation boundary over an already-realized experience pool, and that boundary is independently intervenable from both search generation and served behavior.

### B — What the same-pool intervention identifies

It can identify the controlled causal effect of changing the learner-visible projection of a fixed realized experience pool on subsequent persistent-skill utility under the frozen updater/environment. V3 can additionally test whether this effect differs across two prospectively specified structural conditions.

It cannot by itself identify failure-specific value, global MRW superiority, the globally optimal projection, long-run deployed self-evolution effects, population-level procedural-vs-binding moderation, natural-task transport, or even that the served winner is strictly worse learning evidence unless an appropriate simple effect shows that.

### C — Search-projection censoring

The trivial version (“best-of-K chooses one and does not use K-1 others”) is not a paper. The substantive version separates:

1. what evidence was generated in `T_K`;
2. what survives the serving-to-learning projection;
3. the causal consequence of changing that projection for the persistent update.

Censoring should be defined outcome-independently as identifiable evidence classes absent from a winner-coupled learning projection; usefulness is a later causal question.

### D — Closed global MRW result

The completed `+2.3148pp`, CI spanning zero, `p=0.171875`, `HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS` result should remain prominent, but only as:

> the completed study did not establish a reliable global MRW advantage.

It does **not** itself establish clear heterogeneity or non-universality. The proper chronology is: global benefit not established → several possible explanations generated, including heterogeneity → V3 freezes one moderator hypothesis and tests it prospectively on fresh units. This is acceptable post-result hypothesis generation because the old result stays frozen and V3 cannot be rescued after failure.

### E — V3 moderator validity

Internal causal validity is reasonably strong: the crossed matched-skeleton experiment is genuine experimental effect modification. Construct validity remains bounded because procedural-vs-binding cells are author-constructed. A PASS supports the moderator for these operationalizations; it does not establish a naturally occurring universal semantic law. External validity remains limited. The reviewer explicitly said this does **not** warrant redesigning R2.

### F — Router

Demote the hand-engineered observable router one notch further. It is not a primary method contribution. If V3 passes, it may show that the experimentally identified distinction can be instantiated using pre-update observable information — proof of implementability only. It cannot establish the moderator, and router performance cannot rescue a failed interaction.

### G — Five independent skeletons

Five is the absolute low end for a confirmatory mechanism claim. If all five prespecified interaction directions are positive, permissible wording is limited to the five controlled skeletons, with exact finite-set directional resolution `1/32` and all five magnitudes reported. `R=4` remains measurement replication and never creates 20 independent mechanism units. If the frozen primary gate fails, replicate-level significance, aggregate averaging, router performance, or subsets cannot rescue it.

### H — Failure-specific diagnostic value

Still under-identified because WIN-C vs failed-nonwinner MRW4 jointly changes winner/nonwinner, success/failure, selected/alternative path, diversity, and possibly error localization. A generic-alternative / successful-nonwinner control should be required **only after a positive V3 result**, and only if the paper wants the stronger failure-specific claim. It should not block Stage A.

### I — Natural/out-of-family transport

Not required for the controlled causal paper. It becomes required for stronger claims of generally useful routing, deployment, a natural semantic moderator, or ordinary-agent transport. It is a claim-expansion gate, not a Stage-A prerequisite.

### J — Contribution hierarchy

Strongly survives: exact-same-pool, acting-fixed causal identification.

Survives after rewrite: act/learn projection interface as organizing abstraction whose value is causal manipulability; search-projection censoring as measurable motivating phenomenon.

Conditional on V3: prospective structural effect modification.

Remove as novelty claims: learning from failures, rejected-rollout use, success/failure siblings, multi-trajectory learning, persistent textual updates, generic diversity, Selective-MRW as main method, hand-engineered router, universal MRW superiority, unique failure-specific value.

### K — PASS and FAIL stories

**If V3 passes:** the effect of changing the learning projection of the exact same realized search pool differs consistently across five frozen controlled operational structures. This is a coherent controlled causal story. The stronger statement that acting-optimal and learning-preferred evidence diverge is allowed only if a relevant prespecified simple effect actually shows an alternative projection improving future skill over WIN-C.

**If V3 fails:** the moderator is rejected. Search-projection censoring, interface formalization, and the exact-same-pool causal design survive, but the current strong moderator/mechanism thesis collapses. A narrower diagnostic/negative interface paper may remain, but it is not automatically main-track strength and must be treated as a genuine pivot rather than relabeling V3 as success.

### L — Immediate action

Choice `2`: make a specific zero-provider paper/claim freeze before Stage A. The experimental R2 contract is sufficiently strong to execute; no new experiment is required. After the story freeze, proceed through the existing fresh-identity qualification and separately authorized Stage-A boundary unchanged.

## Reviewer-recommended outcome-neutral thesis

> Test-time search creates a shared experience object whose serving and persistent-learning projections are distinct causal interfaces; exact-same-pool interventions can isolate the learning consequence of that projection and prospectively test whether it is modified by task structure.

The stronger sentence “the best trajectory to act on is not always the best to learn from” stays locked unless a corresponding simple effect warrants it.

## Reviewer-recommended title direction

**Decoupling Serving and Persistent Learning over Test-Time Search**

Possible subtitle: *Exact-Same-Pool Causal Tests of Search-Projection Censoring in Self-Evolving Agents*

## Exactly three verdict-changing fixes

1. **Align the headline thesis with the actual estimand.** Remove/freeze the pre-outcome acting-optimal-versus-learning-optimal mismatch assertion. An interaction alone does not establish it.
2. **Correct the closed global MRW interpretation.** Say global benefit was not established and the result is compatible with underpower, heterogeneity, or both; V3 prospectively tests one moderator hypothesis generated after that closed study.
3. **Freeze the five-unit V3 PASS/FAIL claim boundary before outcomes.** PASS means controlled structural effect modification across the five skeletons, not generality/failure-specificity/deployability or automatically a positive simple effect. FAIL rejects this moderator and cannot be rescued by router or `R=4`.

## Machine-readable decision copied from reviewer

```json
{
  "paper_object": "Causal identification of the serving-to-persistent-learning projection interface over an exact shared test-time search object, with search-projection censoring as the motivating observable phenomenon.",
  "novelty_status": "CONDITIONAL_BUT_REAL: weak as dual-projection terminology or failure-learning; strongest as exact-same-pool acting-fixed causal identification plus prospective structural effect modification.",
  "stage_a_recommendation": "MAKE_ZERO_PROVIDER_STORY_FREEZE_THEN_PROCEED_WITH_EXISTING_R2_STAGE_A_BOUNDARY_WITHOUT_EXPERIMENT_REDIRECTION",
  "v3_pass_story": "The causal effect of learner-visible projection differs prospectively across all five frozen controlled structural skeletons; this supports a structure-dependent act/learn projection mechanism on the controlled suite. Stronger claims that an alternative is actually better than the served winner require corresponding simple-effect evidence.",
  "v3_fail_story": "The proposed procedural-vs-binding moderator is rejected; search-projection censoring and the exact-same-pool diagnostic interface survive, but the current strong causal-mechanism thesis collapses and the work must be downgraded to a narrower diagnostic/negative interface paper rather than rescued by routing.",
  "required_fixes": [
    "Align headline thesis with the interaction estimand and remove pre-outcome acting-optimal-versus-learning-optimal mismatch claims.",
    "Describe the closed global MRW result as inconclusive rather than evidence of heterogeneity or non-universality.",
    "Freeze the five-unit V3 pass/fail claim boundary before any provider call."
  ],
  "verdict": "REVISE_PAPER_OBJECT_BEFORE_STAGE_A"
}
```

Final reviewer verdict: `REVISE_PAPER_OBJECT_BEFORE_STAGE_A`
