# E2-R17 V2 Dual-Review Adjudication

Date: 2026-08-28
Status: **REVISE_BEFORE_RUNTIME_PILOT**
Scientific authority: **ZERO**

## Bound V2 review

Experiment Plan V2 SHA-256:

`3a620eb791b2515b8498d9313698c51a50d59a0b03fb1684379b535e3a73ff08`

Independent reviewers:

- `deepseek-v4-pro` -> `deepseek-v4-pro-ga-260813`
- `kimi-k3` -> `kimi-k3`

Both reviews completed after a transport-level MCP 502. The process and output directory were inspected before any relaunch; both reviewer JSONs and the summary were already complete, so **no duplicate provider call was issued**.

Both verdicts:

`REVISE_V2_BEFORE_PILOT`

No E1 actor pool, updater outcome, held-out evaluation, public benchmark result, paper-promotion decision, or submission action was authorized by these consultations.

## Findings accepted as verdict-changing

### P0-1 — evidence budget must be frozen before Pilot

Both reviewers independently identified trajectory-length/truncation as a causal confound. V2 allowed choosing an evidence policy after runtime Pilot, which is too late.

**V3 repair:** freeze before Pilot:

- tokenizer package: `tiktoken==0.11.0`;
- encoding: `cl100k_base`;
- cap: `3072` tokens per source trajectory;
- canonical evidence excludes the common system prompt and provenance/provider metadata, but retains branch-specific user/assistant/tool messages and verifier score/message;
- for each exact WIN/MRW pair, matched budget `B_pair=min(3072, tokens(WIN), tokens(MRW))`;
- if truncation is needed, retain exactly one-third head and two-thirds tail tokens;
- no padding or extra semantic material;
- both arms receive exactly `B_pair` source-evidence tokens;
- every rendered artifact receives a hash-bound token-window receipt.

The renderer is implemented in `research_pipeline/e2_r17_evidence_window.py`. It refuses to run if the exact tokenizer dependency is unavailable or version-drifted.

### P0-2 — stream support gate must be internally consistent and non-waivable

The theory-correction artifact required at least two mixed pools per exposed stream, while V2 said at least one. This discrepancy is real.

**V3 repair:** use the stricter rule:

- `mixed_pool_count >= 24/96`;
- `>=8/12 streams` each contain `>=2/8 mixed pools`;
- all 96 exact pools frozen before evaluating the gate;
- no threshold rounding, relaxation, or task/pool replacement after support is observed;
- a borderline value such as 23/96 or 7/12 is a gate failure, not an adjudication opportunity.

Failure-family coverage is removed from the **primary causal-identifiability gate** because the pooled stream-level causal contrast is identified without requiring four families. Family support remains a separate generalization qualification:

- `>=4/6 families` with mixed support permits family-heterogeneity / prospective-family claims;
- `<4/6` does not prevent the pooled E1 causal test, but blocks broad family-generalization claims and E3 family-ranking promotion.

### P1-1 — ReasoningBank collision must be adjudicable regardless of MRW GO/HOLD

ReasoningBank/MaTTS is already an ICLR 2026 published method that learns from successful and failed trajectories generated with test-time scaling. A positive MRW result alone cannot be advertised as the novelty “failures help memory.”

**V3 repair:** predeclare a secondary `RB-AGG` semantic adapter on the same frozen pool and run it in the causal tranche regardless of MRW GO/HOLD, once its paper-spec semantics and evidence accounting pass runtime Pilot. This is **not** called an official source-faithful ReasoningBank reproduction on the spreadsheet substrate; official source-faithful reproduction remains a separate WebArena lane.

The role of `RB-AGG` is collision diagnosis:

- if MRW and RB-AGG both beat WIN, compare whether one witness is practically equivalent to richer aggregation;
- if MRW is null/equivalent but RB-AGG beats WIN, reject the minimal-witness repair and narrow the claim to aggregation-sensitive projection;
- if both are equivalent to WIN, the learning-consequence mechanism is unsupported/STOP subject to the frozen equivalence rule.

### P1-2 — updater stochasticity must be measured, not assumed away

MindMemOS SkillEvolver's first-party summary/patch calls do not currently supply an explicit temperature to the adapter.

**V3 repair:** future V3 updater calls freeze unspecified temperature to `0.0`, retry to zero, thinking disabled, and resolved model identity to a tranche-qualified value. In addition, create a separate `WIN-B` cloned updater stream with the **same one-slot WIN input as WIN-A**. WIN-A vs WIN-B is an identical-treatment negative control. If their future frozen skills fail the predeclared equivalence/noise criterion, the MRW contrast is not interpreted.

The temperature default is now explicit in `research_pipeline/e2_r17_mindmemos_ark_adapter.py`; historical receipts are not regenerated.

### P1-3 — equivalence STOP must be operational

**V3 repair:** practical equivalence margin remains `epsilon=1/18=0.055555...` absolute held-out success. Use paired TOST at alpha=0.05; equivalently, the 90% paired-mean confidence interval must lie wholly inside `[-epsilon,+epsilon]`. A paired bootstrap 90% CI is reported as robustness. Superiority remains a separate one-sided exact sign-flip test plus 95% paired bootstrap.

- equivalence supported -> qualified null/STOP for that contrast;
- significant negative -> STOP/reject repair;
- neither superiority nor equivalence -> HOLD/underpowered, never “no effect.”

### P1-4 — 12-stream power limitation must be explicit

For `n=12` paired stream units, one-sided alpha=.05 and 80% power under a paired t approximation requires standardized effect `d ~= 0.7664`. With equal-magnitude signs, 10/12 positive pairs are required before a one-sided sign test falls below .05. Therefore E1 is designed to identify moderate-to-large repeatable effects; a wide null interval is HOLD rather than evidence of absence.

### P1-5 — source-faithful vs unified baseline fallback

Current 69 environment exposes Ark credentials but not Google/OpenAI/Anthropic/SambaNova credentials. V3 explicitly treats this as a source-faithful-lane blocker rather than silently substituting models.

If a source-faithful lane remains unavailable at submission time, the paper must state that limitation and report only the clearly labeled unified rerun for that method. Source-faithful and unified results never share one ranking column.

### P1-6 — minimum unified model breadth

Cross-model robustness claims require at least two independently qualified executor models and at least two model families where feasible. If only one unified model qualifies, the paper reports a single-model result and makes no cross-model robustness claim.

## Findings accepted as nonblocking but frozen for V3

- updater token/call ceilings must be measured in runtime Pilot before E1-B authorization;
- resume must re-hash completed units before trusting the completed manifest;
- E1 alone can establish `delta_K` under exact same-pool control, but prospective compute-shielding regime-law claims require later E3 to pass;
- family effects with two streams/family remain descriptive in E1; no family-specific significance claim.

## Adjudication

`V2 = REVISE_BEFORE_RUNTIME_PILOT`

The theory is not rejected. The next legitimate artifact is V3 with the above repairs. No scientific execution may use V2 as authority.
