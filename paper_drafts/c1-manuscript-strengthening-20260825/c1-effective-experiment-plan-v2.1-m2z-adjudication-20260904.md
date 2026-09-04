# C1 V2.1 M2-Z adjudication — no default first-action top-up

Date: 2026-09-04
Status: **M2-Z COMPLETE / KEEP MEASUREMENT CLAIM / PROSPECTIVE TOP-UP CLOSED BY DEFAULT**

Pre-outcome design seal: `dc3e5c4b297c4598b65669e5e68c7d7a2d9cff2d`
Implementation checkpoint: `ccbcabe8ee4fe5727552fb9f9ae8cd47c79ce0dc`
Raw-replay receipt SHA256: `2bac711b6ebec8b77568bdca3cd0ea47d62d2dde52add8e34f44493703ff88d7`
M2-Z result SHA256: `65901eaf5188fd2ffb071f7f4359e78dc26b71b1f0a1439e4f7e81410c1e9c56`
New provider calls: `0`

## 1. Frozen question

> Does the historical success-memory versus failure-memory first-action contrast remain supported after explicitly correcting the categorical comparison for same-condition stochastic concentration?

This adjudication uses the exact-match-kernel unbiased collision/MMD2 statistic frozen before its outcome was opened. The scientific unit is the frozen matched Shopping state (`n=36`), with four success-memory and four failure-memory repeated first-action draws nested within each state.

## 2. Result

The zero-provider diagnostic returns:

- mean collision `MMD2_u = -6.17e-18`, numerically zero;
- median `MMD2_u = 0`;
- mean within-success collision `0.935185`;
- mean within-failure collision `0.898148`;
- mean between-branch collision `0.916667`;
- state signs: `1 positive / 33 zero / 2 negative`;
- one-sided state-stratified randomization `p = 0.5800941991`;
- fixed-state descriptive bootstrap 95% interval `[-0.018519, 0.023148]`;
- pre-frozen support rule `mean U > 0 and p < 0.05`: **FAIL**.

The only positive state has `U=+1/3`; two states have `U=-1/6` each; they cancel exactly at the panel mean. Several cells with nonzero historical plug-in TV collapse to `U=0` once within-condition collision/concentration is accounted for.

## 3. Scientific interpretation

The correct result is:

> **Stochasticity-adjusted success/failure first-action distribution separation is not supported on the replay-qualified frozen 36-state B10 panel.**

This is more diagnostic than merely observing a nonsignificant plug-in TV because the collision U-statistic uses within-condition repeated draws directly and has zero expectation under identical action distributions. It therefore addresses the reviewer alternative that sparse/high-cardinality empirical TV can be inflated by finite-sample categorical concentration.

However, this remains a post-hoc zero-provider reanalysis of prospectively collected historical B10 draws. It is **not** an independent prospective replication, and it does not establish equality, a zero effect, latent irrelevance, or latent authority failure.

## 4. Verdict-changing consequence

For the current narrow measurement paper, no new first-action provider experiment is mandatory.

The manuscript can retain:

> Stable branch-conditioned first-action uptake was not established on the frozen Shopping panel after durable write divergence and observed native source-item exposure.

It may additionally report, with post-hoc status explicit:

> A replay-qualified collision/MMD2 diagnostic that corrects for within-condition stochastic concentration also yields no supported aggregate S/F first-action separation.

It must not say that success- and failure-conditioned memories are behaviorally equivalent.

## 5. Why prospective top-up is CLOSED by default

A fresh `144/288/432/576`-call first-action block would currently buy neither a necessary identification distinction nor a necessary claim upgrade. Running it simply because more repeats look stronger would violate the minimum-sufficient-evidence rule.

`M2-P` reopens only if a fresh independent submission review concludes that the **post-hoc status itself** is a verdict-changing blocker for the intended first-action claim and that a prospective stochasticity-controlled replicate is required. If reopened, sample size must be calibrated and frozen before fresh outcomes, and the fresh block must remain independent rather than adaptively topping up B10.

## 6. Remaining experiment program

### Mandatory zero-provider work

1. **M1 — baseline packaging:** put write-only, retrieval-only, native-endpoint-only, forced-only, and full stage-resolved evaluation on the same reviewer-facing comparison, alongside the already completed matched controls.
2. **M3 — claim/figure audit:** add the replay-qualified stochasticity diagnostic with its post-hoc boundary and re-run machine claim/evidence checks.
3. **M3 — independent submission review:** ask only whether any remaining objection is verdict-changing for the current narrow measurement claim.

### Conditional only

- **Reddit E/U completion:** only if cross-domain stage-boundary replication remains a verdict-changing objection after M3.
- **One second executor:** only if model specificity remains verdict-changing after M3.
- **PACTA-MSR:** independent method-expansion project; not required to rescue C1.

## 7. Workload conclusion

The current experimental program is not underpowered merely because it is smaller than SkillZip Pro. For the current claim, the right next move is **better evidence packaging and independent claim review, not more provider volume**.
