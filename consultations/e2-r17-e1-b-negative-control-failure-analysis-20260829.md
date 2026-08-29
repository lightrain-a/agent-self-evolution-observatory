# E2-R17 E1-B Negative-Control Failure Analysis

Date: 2026-08-29  
Status: **TERMINAL SCIENTIFIC_IDENTIFIABILITY HOLD**  
New provider calls for this analysis: **0**

## Outcome

The frozen WIN-A/WIN-B negative control completed all 12 paired streams, 24 learned states, and 432 held-out K=1 evaluations with no failure artifact. The preregistered endpoint was not practically equivalent:

- Mean (N_s = J_s(mathrm{WIN	ext{-}B)-J_s(mathrm{WIN	ext{-}A})): (-0.023148)
- Fixed equivalence margin: (pm 1/18 = pm 0.055556)
- 90% paired-t CI: ([-0.095239, 0.048943])
- Paired TOST equivalence: **FAIL**
- Paired bootstrap 90% CI: ([-0.087963, 0.041667]), 100,000 replicates, seed 1717; robustness only

The legal terminal state is:

```text
HOLD_UPDATER_OR_EVALUATOR_STOCHASTICITY
```

This is a scientific-identifiability result. It is not an implementation failure, and it is not evidence for or against the central Search-Projection mechanism.

## Differential diagnosis

| Layer | Verdict | Evidence |
|---|---|---|
| Implementation | Not supported as root cause | 12/12 streams, 24/24 updates, and 432/432 evaluations completed; hashes and manifests agree; no failure artifact |
| Runtime infrastructure | Not a terminal failure | Hosted latency varied and one MCP monitoring request failed, but the locked remote process continued and completed without relaunch |
| Measurement / analysis | Valid | Frozen analyzer used 12 paired streams—not 216 pseudo-independent probes—the fixed 1/18 margin, paired TOST, and the predeclared bootstrap |
| Protocol causal purity | Pass for the negative-control endpoint | WIN-A and WIN-B received the same winner-only treatment; MRW was never executed |
| Scientific identifiability | Terminal HOLD | Identical-treatment variation was not shown equivalent within the fixed margin |
| Scientific mechanism | Not adjudicated | No MRW effectiveness endpoint was executed or observed |

## Zero-provider localization

The existing artifacts narrow the nuisance source without changing the primary gate:

- 12/12 pairs have the same stream SHA.
- 12/12 pairs have the same initial skill SHA.
- 12/12 pairs have the same first-eight updater summary prompt-SHA bundle.
- Only 6/12 pairs have the same final skill SHA; therefore updater-side byte variation is present.
- In the 6 pairs with byte-identical final skills, 6/6 still have nonzero held-out success differences.
- The largest absolute difference among those same-skill pairs is (4/18 = 0.2222), four times the practical-equivalence margin.

Thus evaluator/actor hosted stochasticity is directly observed and is already large enough to threaten identifiability. Updater stochasticity is also present, but this experiment varies updater and evaluator calls together, so their separate variance components cannot be estimated. The evidence does not justify blaming only one component.

## Calls, tokens, and cost

| Phase | Provider calls | Input/prompt tokens | Output/completion tokens | Total tokens |
|---|---:|---:|---:|---:|
| Updater | 240 | 564,180 | 82,931 | 647,111 |
| Held-out evaluation | 2,499 | 7,649,896 | 497,707 | 8,147,603 |
| Total | **2,739** | **8,214,076** | **580,638** | **8,794,714** |

The receipts contain no billed-cost field, so observed USD cost is unavailable and is not post-hoc estimated. Evaluation receipts contain 2,495 `completed` and four `incomplete` provider responses; the latter reached the 4,096-output-token cap without hidden retry, but their rollout artifacts and verifier endpoints completed, so the frozen runner did not classify them as technical failures.

## Scientific consequence

- Central mechanism: **OPEN / UNKNOWN**
- MRW contract preparation: **forbidden**
- MRW execution: **forbidden**
- Published-baseline and public-benchmark expansion: **forbidden**
- Same-protocol rerun, margin widening, noisy-stream removal, model/probe substitution, or favorable-subset averaging: **forbidden**

Any future attempt must be a new versioned nuisance-control protocol with an independently justified single-variable intervention that isolates evaluator or updater variability before MRW can be reconsidered.

## Evidence

- Contract: `generated/e2-r17-e1-b-negative-control-full-contract-20260829.json` — `6c84a98d5987e40bde26a41f18cb6cd68f3e7d2ffb0ede69d176128185782c03`
- Authorization: `generated/e2-r17-e1-b-negative-control-full-authorization-20260829.json` — `e62770ac9531001c2c4adf1fade5b617498c26e1bae8dedb108967c7a698d8a4`
- Run summary: `/data/wyt/e2-r17-search-projection/runs/e1-b-negative-control-v1-20260829/summary/e1_b_negative_control_full_summary.json` — `b1a7a18e41527eb7cd5405ba86af4780632228afcd4d64b64ec058dfa4a2ca98`
- Adjudication: `generated/e2-r17-e1-b-negative-control-adjudication-20260829.json` — `758d7514518216c6913d623b9175f237a35a63c4f2f523fa24a3097d07515a2e`
- Terminal registry V7: `generated/e2-r17-failure-differential-registry-v7-20260829.json` — `b2b8aaffc2a1f3c9fd0c55a1961a4a119e684f8bb972853c5201e07992498c27`
