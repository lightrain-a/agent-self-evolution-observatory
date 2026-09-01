# E2-R17 DeepSeek V2 — Replicated Contemporaneous Paired Protocol

Date: 2026-08-30
Status: DRAFT_PREOUTCOME_PROTOCOL
Scientific backbone: DeepSeek V4 Pro only

## Why V2 exists

Protocol V1 correctly established a scientific-identifiability HOLD: byte-identical WIN-A/WIN-B treatments did not establish practical equivalence when hosted updater and hosted task-solving actor randomness were allowed to vary jointly. That result is preserved and is not reinterpreted as implementation failure.

Subsequent audit corrected two design labels/assumptions before any MRW outcome had ever been generated:

1. SpreadsheetBench scoring is not an LLM evaluator. It is a deterministic openpyxl comparison against the golden workbook. The stochastic component is the hosted agent backbone and the hosted updater, not the verifier.
2. Published agent-learning baselines routinely use capable hosted backbones and statistical replication rather than requiring byte-level deterministic task execution. Therefore V2 treats hosted randomness as sampling variation and controls it with contemporaneous pairing plus preregistered replication.

V2 is a new protocol version, not a rerun of V1. V1 artifacts and HOLD remain authoritative for V1.

## Fixed scientific substrate

- E1-A exact K=8 pools: unchanged and content-addressed.
- 12 frozen update streams, two per controlled failure family.
- Initial skill SHA unchanged.
- Acting winner unchanged within each exact pool.
- Learning projection is the only scientific treatment:
  - WIN-C: matched-window acting-winner evidence.
  - MRW: matched-window deterministic first failed nonwinner on mixed pools; identical to WIN-C on nonmixed pools.
- Updater: first-party MindMemOS SkillEvolver, same pinned commit and V3.1 arm-blinded selected-evidence path.
- Verifier: deterministic SpreadsheetBench openpyxl workbook comparator; never changed across arms.
- Held-out evaluation: same 18 e1_common_heldout_probe tasks, K=1.

## Backbone and API transport

Only DeepSeek V4 Pro is scientific in this tranche.

- requested model: deepseek-v4-pro
- fresh resolved model: deepseek-v4-pro-ga-260813
- Ark OpenAI-compatible Agent Plan base: https://ark.cn-beijing.volces.com/api/plan/v3
- Responses endpoint: /responses
- provider retry: 0
- thinking: disabled
- actor temperature: 0
- actor max_output_tokens: 8192

The 8192 actor output ceiling is a transport/runtime repair relative to the earlier 4096 cap; it is frozen symmetrically for both arms and all replicates. It does not alter the search pools or learning treatment.

## Replication and power rationale

The completed V1 identical-treatment negative control estimated stream-level paired nuisance SD = 0.13905713715032014. This variance estimate is used only for prospective sample-size design; no MRW outcome exists.

With n=12 streams and R independent paired replicates per stream, averaging replicate differences approximately reduces nuisance SD by sqrt(R). At the practical scale epsilon=1/18:

- R=3 gives approximate one-sided alpha=.05 power ~0.73.
- R=4 gives approximate power ~0.83 and a typical 90% CI half-width ~0.036, below epsilon=0.0556.

V2 therefore freezes R=4.

## Scientific unit and estimand

For stream s, replicate r, arm a:

J_{s,r}(a) = mean binary success across the same 18 held-out K=1 probes.

Replicate paired effect:

d_{s,r} = J_{s,r}(MRW) - J_{s,r}(WIN-C).

Primary stream effect:

D_s = (1/4) sum_{r=1}^4 d_{s,r}.

Independent confirmatory units are the 12 D_s values. Replicates and probes are repeated measurements, not independent scientific units.

Primary estimand:

Delta = mean_s D_s.

## Time balancing

Each replicate is a fresh clone from the same initial skill and exact pools. WIN-C and MRW update order is hash-balanced by stream+replicate. Held-out evaluation order is hash-balanced by stream+replicate+task. Treatment arms must be interleaved inside the same contemporaneous tranche. Historical WIN-A/WIN-B are secondary nuisance evidence only and never enter the primary control.

## Statistics frozen before MRW outcomes

Primary superiority:

- exact one-sided sign-flip test over 2^12 assignments of the 12 D_s values;
- alpha=.05;
- mean D_s > 0;
- paired stream bootstrap 95% lower bound > 0.

Practical-null test:

- paired TOST at epsilon=1/18;
- equivalently 90% t-CI for mean D_s strictly inside [-1/18,+1/18].

Decision priority:

1. If TOST practical equivalence passes -> STOP_MRW_PRACTICALLY_NULL, even if superiority is statistically significant.
2. Else if mean>0, exact one-sided p<=.05, and 95% paired-bootstrap lower>0 -> GO_MRW_CAUSAL_EFFECT_SUPPORTED.
3. Else if mean<0 and exact negative-direction sign-flip p<=.05 -> STOP_MRW_HARMFUL.
4. Else -> HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS.

No task/stream/replicate may be deleted based on score. Missing/ambiguous provider units produce protocol HOLD, not outcome-conditioned substitution.

## Failure discipline

- Provider/API/runtime failure before a valid replicate endpoint: classify implementation/runtime and preserve artifacts; no scientific belief update.
- Valid but noisy V2 endpoint: HOLD is a valid scientific result; do not add models/tasks or widen thresholds to rescue it.
- Qualified practical null/harmful result: central DeepSeek R17 mechanism STOP for this substrate.
- Qualified GO: only then proceed to diagnostics/public benchmarks and later a second backbone.

## Second model

No second scientific backbone is selected or executed in V2. GPT is deferred until DeepSeek reaches a terminal GO/HOLD/STOP conclusion.
