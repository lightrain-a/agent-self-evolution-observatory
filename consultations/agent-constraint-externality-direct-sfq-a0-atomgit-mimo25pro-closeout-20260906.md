# Agent Constraint Externality — AtomGit MiMo-V2.5-Pro Direct-SFQ-A0 closeout

Date: 2026-09-06
Scientific object: `AGENT-CONSTRAINT-EXTERNALITY-20260831`
Execution: `DIRECT-SFQ-A0-ATOMGIT-MIMO25PRO-20260906`

## Verdict

`DIRECT_SFQ_A0_ATOMGIT_TARGET_FAILURE_QUALIFICATION_PASS`

This is a **development-only source-failure qualification PASS**. It does not replace or satisfy the frozen `qwen3.7-flash` mainline Gate 1, and it opens no F0-R1, TARGET_ONLY_VERIFICATION, RQ1/RQ2, RQ3, RQ4, or paper-claim authority.

## Frozen object and rationale

The run reused two pre-existing assets without rerunning the expensive capability ladder:

1. the predeclared AtomGit backbone selection in which `mimo-v2.5-pro` was the first candidate to pass the frozen capability interval; and
2. the never-executed, freshness-qualified 12-case Direct-SFQ-A0 panel.

The child changed only the provider/harness binding required to run those fresh target-local challenge cases through the already-qualified AtomCode/AppWorld MCP transport. It remained separate from the `qwen3.7-flash` mainline.

## Pre-dispatch integrity

- prelaunch Git SHA: `91e67f75a70f83ccb51ab9a0921cb2e125e76c43`
- Q1 MCP predispatch: PASS with **0 model requests**
- AtomCode model: `AtomGit-mimo-v2.5-pro`
- AppWorld tool cap: 80 per case
- model-round cap: 56 per case
- retries: 0
- replacements/top-ups: forbidden
- shared CodingPlan reserve for G1: 100 requests
- minimum account remaining before each new case: 161

The run bound the same frozen AppWorld 0.2.0 substrate and normalized only the already-preregistered terminal-newline formatting convention.

## Exactly-once completion

Run root:
`/data/wyt/agent-constraint-externality/runs/direct-sfq-a0-atomgit-mimo25pro-20260906-v1`

Ledger SHA256:
`4b2e73ed85616e43ddc9243a7d130b1e5b71d2c67b702b9b7549a5949ec36249`

Integrity audit:

- 24 durable ledger rows
- 12 DISPATCH
- 12 COMPLETION
- 0 FAILURE
- 12 unique dispatched units
- 12 unique completed units
- dispatch/completion unit sets identical
- 0 replay
- 0 replacement
- 0 non-semantic failure

## Frozen Direct-SFQ result

| Case | Target result | Classification | Model rounds | AppWorld tool calls |
|---|---:|---|---:|---:|
| FG-01 | fail | usable semantic failure | 11 | 29 |
| FG-02 | success | target success | 9 | 26 |
| FG-03 | fail | usable semantic failure | 8 | 29 |
| FG-04 | fail | usable semantic failure | 13 | 30 |
| FG-05 | fail | usable semantic failure | 13 | 32 |
| FG-06 | fail | usable semantic failure | 13 | 32 |
| TNF-01 | fail | usable semantic failure | 13 | 42 |
| TNF-02 | fail | usable semantic failure | 11 | 48 |
| TNF-03 | success | target success | 17 | 41 |
| TNF-04 | fail | usable semantic failure | 13 | 48 |
| TNF-05 | fail | usable semantic failure | 17 | 41 |
| TNF-06 | success | target success | 17 | 42 |

Aggregate:

- usable target failures: **9/12 = 0.75**
- target successes: **3/12**
- non-semantic failures: **0/12**
- preregistered acceptable final failure counts: `{9, 10}`
- total scientific AtomGit model rounds: **155**
- total AppWorld tool calls: **440**

The frozen source-failure geometry therefore passes exactly at the lower boundary of the preregistered interval.

## Shared CodingPlan accounting

Terminal account observation:

- rolling limit: 500
- used: 161
- remaining: 339
- next reset: 2026-09-06 18:04:58 local server time

The Constraint lane stayed well above the 100-request reserve for G1.

## Interpretation boundary

What this result supports:

> Under the bound AtomGit MiMo-V2.5-Pro + AppWorld MCP development configuration, the fresh Direct-SFQ-A0 challenge panel produces the preregistered mixture of normal semantic target failures and target successes required for a useful repair-opportunity substrate.

What it does **not** support:

- no collateral externality result exists;
- no HIGH vs INDEPENDENT topology result exists;
- no repair uptake result exists;
- no TARGET_ONLY_VERIFICATION result exists;
- no RQ1/RQ2/RQ3/RQ4 claim is opened;
- the result is not a substitute for the frozen `qwen3.7-flash` mainline Gate 1;
- the 12 development cases may not be reused as future confirmatory F0-R1 units.

## Frozen artifacts

- result file SHA256: `43d5896e2fe56b96f73ecb75884011dce6427d1e0aa37393ecc5c1f3e13f2bc9`
- result content SHA256: `71fa4fd8f22bd473d656d2d2a51396b57711caaf78c823bbb39b5af672b47108`
- operational state SHA256: `640c83fa7fbffaf5611e9c68eff6df9223a0cdc5da7a96bd75d79a5595b93a8c`
- integrity-audit content SHA256: `3c5ebdc1f9e0d407429a91259e2e018764946551ab84a667ca7d243b1334f51e`

## Next legal action

Do not automatically promote this development panel into the paper's main confirmatory chain. The next use of AtomGit should be chosen by the shared-plan scheduler:

1. first honor any already-authorized, non-burned G1 successor work within the reserved quota;
2. if no such G1 work exists, prepare a **fresh, disjoint AtomGit confirmatory source/repair child** for this paper and subject it to its own outcome-blind protocol/authority before provider dispatch;
3. the current `qwen3.7-flash` mainline remains separately blocked until its provider-readiness condition is repaired.
