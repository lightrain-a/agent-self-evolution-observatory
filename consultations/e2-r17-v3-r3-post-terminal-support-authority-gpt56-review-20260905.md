# Independent GPT-5.6 Sol review — E2-R17 V3 R3 post-terminal support-read authority

Date: 2026-09-05
Surface: ChatGPT web
Model: GPT-5.6 Sol
Thinking: Extra High 4/5
Conversation: https://chatgpt.com/c/6a9c2771-d188-83ee-a1fd-75c4555db896
Prompt packet: `oracle_briefs/E2_R17_V3_R3_POST_TERMINAL_SUPPORT_AUTHORITY_REVIEW_20260905.md`
Prompt packet SHA256: `a7f3fba7b7d9783b09a170e95ef5587e5eccb51aecc925f5822374bc6ad30670`
Response SHA256: `bd0bafba2d32ee6630b44ad8a44b83c72dc20658cc3310b9c6c9157ec0184dbf`
Oracle transcript SHA256: `78f22396d9c8dbaf974ff8d623f15b78aaced803c55699ae5343434acd362ced`

## Reviewer response

### A. Correct reading

**Reading B — separate support-read authority is required.**

The frozen authorization language is explicit and global: `Single-use authority for the 158-task R3 Stage-A matched-censor recovery only` followed by `No support read ... is authorized.` Nothing in that text limits the prohibition to the provider-facing runner.

Accordingly, the existing R3 recovery authorization terminates at the sealed recovery summary. It cannot itself authorize the subsequent operation that opens K8 pools and computes mixed-pool support.

### B. Does the exact-hash review implicitly scope the adjudicator?

**No.**

The exact-hash review establishes that the support adjudicator is the **pre-reviewed, scientifically correct implementation** of the intended post-terminal Stage-A transition. It does not grant execution/read authority that the actual authorization artifact explicitly withholds.

These are separate control-plane predicates:

- **implementation eligibility:** already satisfied by the exact-hash review;
- **support-read authority:** not satisfied by the provider-recovery authorization.

Treating the review receipt as silently overriding `No support read ... is authorized` would weaken the fail-closed authority model and make review approval function as an implicit capability grant. That is methodologically undesirable.

### C. Can the missing authority be purely zero-provider?

**Yes.**

A separate post-terminal support-read authorization can be a purely zero-provider control-plane artifact. It should be mintable only after mechanically establishing all frozen terminal prerequisites, including the exact R3 contract/authentication chain, exact terminal-summary identity/hash, 158 sealed pools, the two frozen exceptions, `support_inspected=false`, zero updater/heldout access, and the frozen 7/7/8 geometry.

This does **not** require changing the scientific experiment, task universe, recovery geometry, R3 contract, provider runner, support threshold, or Stage-B rules.

The existing exact-hash-reviewed support adjudicator can remain the bound scientific implementation; the missing element is an explicit authorization gate for invoking it. An additive zero-provider minter/gate is sufficient and does not constitute redesign of the bound R3 scientific code.

### D. Must this be resolved before provider recovery?

**Yes.**

The ambiguity should be resolved **before any R3 provider recovery begins**, even though the actual post-terminal support-read authorization must not be minted until the terminal summary exists.

The correct sequence is therefore:

1. before provider execution, freeze the separate post-terminal authorization schema/minter and its gating semantics;
2. run the separately authorized 158-task recovery;
3. reach and verify the exact terminal state;
4. only then mint the single-use zero-provider support-read authorization;
5. invoke the already-bound adjudicator.

Deferring the authority decision until after provider outcomes exist would create avoidable post-outcome discretion and pressure precisely where the control plane is intended to be fail-closed.

This sequencing requirement does not invalidate or broaden the provider-recovery authorization itself.

### E. Stage-B authority

**NO.**

Neither the provider-recovery authorization nor the proposed post-terminal support-read authorization grants Stage-B execution authority. A successful adjudication may permit `prepare_stage_b_contract=true`; it must continue to leave `execute_stage_b=false`.

`post_terminal_support_read_authority`: `SEPARATE_AUTH_REQUIRED`
`provider_recovery_authority_affected`: false
`r3_contract_redesign_required`: false
`bound_code_change_required`: false
`new_scientific_experiment_required`: false
`stage_b_authority`: false
`must_resolve_before_provider_recovery`: true
`required_action`: Freeze before provider recovery an additive zero-provider post-terminal support-read authorization minter/gate bound to the exact R3 contract, existing recovery authorization, and exact terminal-summary hash/state; mint that single-use authorization only after the terminal 158-pool recovery state is verified, and require it before invoking the already exact-hash-reviewed support adjudicator. Do not modify the frozen R3 scientific geometry or grant Stage-B execution authority.

REQUIRE_SEPARATE_POST_TERMINAL_SUPPORT_READ_AUTHORIZATION
