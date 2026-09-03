# E2-R17 manuscript R2 — independent-review repair — 2026-09-03

## Lineage

R1 manuscript commit reviewed independently:

`b93a93d084b4e84504fdcf2d2bb22fc489ea51a2`

Independent Oracle Browser review:

- model: GPT-5.6 Sol
- effort: Extra High (4/5 verified from ChatGPT DOM)
- conversation: `6a9976ea-7908-83e8-acf0-b57b0b203ca5`
- session: `e2-r17-manuscript-r1-review-3`
- verdict: `REVISE_DESIGN_BEFORE_NEXT_PROVIDER_STAGE`

The first two attempted manuscript-review sessions failed before conversation creation and are not scientific/reviewer results. The successful review used the logged-in Agent project URL on server 52.

## R2 working title

> Same Evidence, Different Skill: State-Regeneration Instability in Self-Evolving Agents

This replaces the stronger R1 wording:

> Diagnosing State-Generation Variance

because the current completed evidence has only two fresh updater realizations and their original actor evaluations were fresh as well.

## Strongest completed claim

> In one controlled outcome-selected development case, reconstructed byte-identical trajectory evidence did not reliably regenerate the historical behaviorally useful skill through the native free-form updater, while the historical state itself remained directionally useful when frozen and re-evaluated. This is local state-regeneration instability consistent with a persistent-state generation bottleneck; it is not a population variance decomposition and does not establish that updater variance dominates actor variance.

## Reviewer repairs applied in R2

1. **Claim/title repair** — remove population-like `state-generation variance/localization` wording; use state-regeneration instability / candidate bottleneck.
2. **Contribution repair** — E→G→S→Y is an operational factorization, not an independent novelty contribution.
3. **Method repair** — typed compiler is framed as a controlled generator intervention first, not a standalone universal algorithm.
4. **M3 repair** — supersede the planned G0+manual-arm rerun with a frozen-state audit of existing historical FF, fresh FF1, fresh FF2, and one common byte-identical WIN-C artifact; no new updater call.
5. **M4 authority repair** — matched-evidence generator validation no longer depends on First-Fail source superiority or the interaction.
6. **Generic-control repair** — add `SCOPE_MATCHED_GENERIC_MAX` alongside `SCORE_ONLY_GENERIC_MAX` before trajectory-conditioned diagnosis can be claimed.
7. **Regeneration probe** — if regeneration/reproducibility remains a central claim, VALIDATION contains exactly one pre-authorized second same-evidence FF4 free-form synthesis per stream plus a small frozen actor-remeasurement probe. It is not a retry and cannot replace the primary state.
8. **STOP rule** — fresh generator failure or failure to beat the scope-matched generic control stops the paper without E3, another backbone, or another benchmark as rescue.

## Exact existing states for revised M3

- Historical First-Fail:
  - SHA `97e28b4862ed5817929fa6014eb1ba1401667875d80e03d18c0b54978a185252`
- Fresh First-Fail 1:
  - SHA `596bd30b49935d16f35d51e9eed36e19567332cd8a9104ae50d832f91ffdf04f`
- Fresh First-Fail 2:
  - SHA `fb5454a27faf8182ba1b0d722273c4377d4762815cd1898c3780cc8ff336615e`
- Common WIN-C:
  - SHA `6df40f61707494793289aa95cc89f5ac99da9eb0aa062cf9ad0fbffd71c00649`

Historical, exact-replay rep1, and exact-replay rep2 WIN-C updater artifacts all have this same skill SHA, so common-comparator state identity is exact rather than nominal.

## Authority boundary

R2 is manuscript/design repair only.

It does not authorize:

- Recovery V3 execution or modification;
- revised M3 actor calls;
- M4 updater or actor calls;
- repeated FREE synthesis;
- E3;
- second backbone;
- public benchmark;
- submission.

Recovery V3 remains under its existing frozen exactly-once authority and scheduled quota-reset continuation. No partial M2 effect was read or imported into R2.
