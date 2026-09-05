# Independent control-plane review — E2-R17 V3 R3 post-terminal support-read authority

Date: 2026-09-05
Role: fresh independent senior ICLR/NeurIPS/ICML agent-systems methodology/control-plane reviewer
Scope: ZERO-PROVIDER authority semantics only

## 0. Review rule

Review only one narrow ambiguity discovered during the provider-reset readiness audit. Do not infer Stage-A support, Stage-B effect, or any paper outcome. No R3 provider execution has started. Do not reopen the already-passed R3 matched-censor recovery design, no-replay/matched-censor geometry, provider budget, exact-hash review, or workload unless this authority ambiguity makes them internally inconsistent.

End with exactly one verdict token:

- `PASS_POST_TERMINAL_SUPPORT_ADJUDICATOR_ALREADY_SCOPED`
- `REQUIRE_SEPARATE_POST_TERMINAL_SUPPORT_READ_AUTHORIZATION`
- `REVISE_R3_CONTROL_PLANE_BEFORE_PROVIDER_RECOVERY`

Then list only verdict-changing required actions.

## 1. Frozen R3 object

R3 recovery contract:
`generated/e2-r17-semantic-transfer-v3-stage-a-contract-r3-recovery-20260905.json`
SHA256:
`3d0db7078c073613a27bc643675aa8755c7b2f241345ef6371570be48f2dd085`

R3 zero-provider preflight:
`generated/e2-r17-semantic-transfer-v3-stage-a-preflight-r3-recovery-20260905.json`
SHA256:
`56208e171b2524a01ec429618c7b018a4fee1a9a785028f024fee5a40bd10df2`

Exact-hash independent review receipt:
`generated/e2-r17-v3-stage-a-r3-exact-hash-gpt56-review-20260905.json`
SHA256:
`6fb37037cb6cb850a99da155fd65aff42b7fffb9a4a8e3bb658f32d557835c99`

Exact-hash review verdict:
`PASS_TO_SEPARATE_R3_RECOVERY_AUTHORIZATION`

Provider reset hard gate:
`NO_PROVIDER_CALL_BEFORE_2026-09-07 00:00:00 +0800`

Current state:
- R3 run root absent;
- R3 lease absent;
- fresh R3 identity absent;
- R3 recovery authorization absent;
- R3 provider execution absent;
- Stage-A support unread;
- Stage-B closed.

## 2. Already-passed recovery geometry

The frozen R3 object contains:

- 160 original Stage-A task opportunities;
- terminal technical missing: `r17-b21-cgwb-p0`;
- exact semantic-counterpart matched no-provider censor: `r17-b21-cgwp-p0`;
- 158 unique original provider-facing recovery task IDs;
- no replacement;
- no replay;
- K=8, therefore 1264 actor rollouts if all provider-facing recovery tasks seal;
- 7/7 opportunities for the exact matched affected streams and 8 elsewhere;
- absolute support threshold remains >=4 mixed pools per stream;
- Stage B remains separately unauthorized.

Do not reopen these items.

## 3. The narrow authority ambiguity

The frozen R3 contract says under `analysis_boundary`:

```text
stage_a_support_only = true
support_read_before_terminal_recovery = false
heldout_access = false
partial_learning_effect_read = false
scientific_learning_effect_read = false
stage_b_effect_inference = false
```

Under `equal_dose_support` it says:

```text
all_158_provider_pools_must_be_sealed_before_support_read = true
required_mixed_pools_per_stream = 4
support_read_excludes_burned_and_matched_censor = true
```

Its `scientific_role` is:

```text
versioned fail-closed Stage-A recovery only; one terminal post-dispatch missing plus one deterministic matched no-provider censor; support remains closed until terminal recovery
```

The exact-hash preexecution review packet explicitly described the bound R3 support adjudicator as follows:

```text
R3 runner:
- ...
- no support read

R3 support adjudicator:
- runs only after terminal 158-pool recovery summary
- verifies 7/7/8 opportunity geometry
- keeps absolute >=4 support
- freezes exactly four treated mixed pools per stream if PASS
- emits 80 treated pools total if PASS
- never grants Stage-B execution authority
```

The independent exact-hash review PASSed the implemented object without identifying a blocker in that sequence.

However, the frozen R3 authorization minter creates an authorization whose final interpretation boundary is:

```text
Single-use authority for the 158-task R3 Stage-A matched-censor recovery only.
No support read, updater, heldout, Stage B, public benchmark, or paper claim is authorized.
Any additional attempted-but-unsealed recovery unit causes STOP.
```

The bound R3 support adjudicator accepts the same `--authorization` artifact plus the terminal recovery summary, then reads the frozen K8 pools to compute mixed-pool support. It requires:

- the exact R3 contract and authorization;
- terminal summary status exactly `COMPLETED_158_POOLS_PLUS_TWO_FROZEN_EXCEPTIONS_PENDING_R3_EQUAL_DOSE_ADJUDICATION`;
- 158 sealed K8 pools;
- exactly one terminal technical missing and one matched no-provider censor;
- runner summary says `support_inspected=false`, updater calls 0, heldout 0;
- 7/7/8 frozen opportunity geometry;
- absolute support threshold 4.

It never grants Stage-B execution authority. If support passes, it grants only `prepare_stage_b_contract=true`, while `execute_stage_b=false`.

## 4. Why this matters

There are two plausible readings:

### Reading A — already scoped terminal transition

The phrase `No support read ... is authorized` in the recovery authorization means **the provider-recovery runner itself** cannot inspect support. Once that authorization reaches its exact terminal summary, the already contract-bound support adjudicator is the predefined Stage-A terminal transition. The contract's `support_read_before_terminal_recovery=false` and exact review's explicit support-adjudicator sequence provide the authority boundary.

### Reading B — separate support-read authority required

The authorization's interpretation boundary is literal for the entire artifact: it authorizes only provider recovery, not any support read. Therefore, after terminal recovery, a new zero-provider support-read authorization should be minted before invoking the bound support adjudicator. This would not change scientific design or code; it would only make the authority transition explicit.

The current code does not mint such a separate post-terminal support authorization.

## 5. Audit questions

A. Which reading is methodologically/control-plane correct given the exact frozen text?

B. Does the already-passed exact-hash review of the support adjudicator suffice to treat it as an automatically scoped post-terminal Stage-A transition, despite the authorization's explicit `No support read` wording?

C. If a separate post-terminal support-read authorization is required, can it be a pure zero-provider control-plane artifact minted only after verifying the exact terminal summary/hash and existing R3 authorization, without changing the R3 contract, runner, support adjudicator, task universe, or scientific rules?

D. Must this ambiguity be resolved before provider recovery starts, or is it sufficient to execute provider recovery now and decide only after terminal summary? Prefer the stricter fail-closed answer if ambiguity could create pressure after outcomes exist.

E. Does any answer here imply Stage-B authority? The answer must be NO.

## 6. Required synthesis

Return exactly these fields before the final verdict:

- `post_terminal_support_read_authority`: `ALREADY_SCOPED` or `SEPARATE_AUTH_REQUIRED` or `R3_REVISION_REQUIRED`
- `provider_recovery_authority_affected`: true/false
- `r3_contract_redesign_required`: true/false
- `bound_code_change_required`: true/false
- `new_scientific_experiment_required`: true/false
- `stage_b_authority`: false
- `must_resolve_before_provider_recovery`: true/false
- `required_action`

Then end with exactly one verdict token from Section 0.
