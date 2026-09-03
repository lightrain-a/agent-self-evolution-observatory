# Independent adversarial pre-execution review — E2-R17 Semantic-Transfer V3 Stage-A R2

Date: 2026-09-03
Role: independent senior ICLR/NeurIPS/ICML agent-systems methodology reviewer

## 0. Exact frozen object

Review only this frozen R2 object. Do not infer any Stage-A or Stage-B scientific outcome; none exists.

- Branch: `research/e2-r17-semantic-transfer-v3-review-repair-20260903`
- Frozen R2 commit: `29799c83c662887694db52acba4bb19e83131bb0`
- R2 contract: `generated/e2-r17-semantic-transfer-v3-stage-a-contract-r2-20260903.json`
- R2 contract SHA256: `f5382c552f2e6644e4cbda408510119664a8c6f8502628586c9ff5583abd1234`
- R2 preflight SHA256: `e257438bd482d4f2209a8321d4a222bd97acf2c03bff46a1d5513b55a42ca766`
- R2 zero-provider repair audit SHA256: `a8b7ba15a533e2727a561d2457107f7e7c86bc5f702964e257220cb2977f54f5`
- R2 repair protocol SHA256: `952d302ae3777dfd8e2249eb8a1bd7248ded636eadda517b9aa572c7962ee580`
- R2 160-unit exact-once manifest SHA256: `43a5f77df10771e8029809d6ffc1c1a8ba9c12e3165dd20f957866a51e0aa9a9`
- Relevant tests: 22/22 PASS
- Provider calls: 0
- Scientific execution: false
- Stage-A provider authority: false
- Stage-B authority: false
- Updater / heldout / analyzer / paper authority: false
- R2 run root exists: false
- R2 global lease exists: false

A PASS from this review grants no provider authority itself. It means only that the team may next perform the separately required fresh actor-model identity qualification and, if that passes, mint the already-scoped single-use Stage-A authorization.

## 1. Scientific object and accepted claim boundary must still be audited

Search produces K=8 trajectory pool `T_K`. Acting always uses the deterministic verifier-selected winner `a(T_K)`. Persistent learning later receives a projection `g(T_K)`. WIN-C exposes the served winner on all update pools. MRW4 replaces winner evidence with one frozen verifier-failure nonwinner on exactly four support-qualified pools per stream; acting never changes.

The state-level causal question is narrow:

> Holding the exact search pool, acting decision, initial state, and update-pool sequence fixed, can changing only learner-visible projection change future persistent-skill utility?

The controlled semantic interaction uses five matched skeletons, each generating both `PROCEDURAL_TRANSFORMATION` and `INSTANCE_BINDING_LOCALIZATION` cells from a common generator. Paired cells use byte-identical init XLSX plus semantic-blind profile selection. The claim is only for these five frozen operationalized semantic contrasts, not a universal latent semantic taxonomy.

Primary later mechanism units are five skeleton interactions `I_h = D_h,procedural - D_h,binding`. Streams and R=4 stochastic replicates are measurement repetition, not extra semantic units. An all-positive five-unit directional gate has minimum exact sign resolution 1/32 under its narrow finite-unit assumptions; no broad population or 80%-power claim is permitted.

The observable router remains a frozen hand-engineered actor-visible instruction policy, not learned semantic discovery. A router success cannot rescue a failed mechanism gate.

## 2. Why R2 exists

The previous independent GPT-5.6 Sol / Extra High review of frozen R1 contract SHA

`6104caa0d797b3a6bdb94988626f8715ea697fe1c896ef839fa1837a80513fdd`

returned exactly:

`REVISE_BEFORE_STAGE_A`

It found three verdict-changing defects:

1. The frozen prose did not make it unambiguous that the four MRW4 treated pools are hash-selected **only from mixed pools**.
2. Global run/lease and provider-budget controls did not prove actor-level per-task exactly-once acquisition. A valid direct actor call could potentially replay an already attempted task, and a crash after provider success but before local sealing could lead to replacement sampling.
3. The prospective Stage-B update-order formula used `arm` but omitted `task_id`, so it could not define a common eight-pool order and could confound projection with update sequence.

R2 changes only these three verdict-changing points. The 270-task suite, 20 scientific streams, five skeletons, semantic crossing, actor model request, K=8, router, and equal failure dose remain unchanged. No R1 Stage-A provider call ever occurred.

## 3. R2 repair 1 — mixed-only treatment domain

After **all 160 Stage-A K=8 pools are sealed**, for each stream `s` define prospectively:

```text
C_s = { p in stream s : p contains >=1 verifier-success trajectory
                         and >=1 verifier-failure trajectory }
```

Support passes only if `|C_s| >= 4` for every one of the 20 frozen streams. If any stream fails, the only scientific result is

`HOLD_SEMANTIC_TRANSFER_V3_INSUFFICIENT_EQUAL_DOSE_SUPPORT`.

If all streams pass, the treated set is exactly:

```text
T_s = the four p in C_s with smallest
      SHA256("semantic-transfer-mrw4-v3|stream_id|task_id")
```

Contract invariants now explicitly state:

- candidate domain = `C_s = mixed K8 pools in stream s`;
- `unmixed_pool_eligible = false`;
- `hash_rank_applied_only_within_candidate_domain = true`.

The adjudicator code uses `mixed_candidate_domain = mixed_tasks_by_stream[stream_id]`, calls `choose_four(stream_id, mixed_candidate_domain)`, and then explicitly requires `set(selected).issubset(set(mixed_candidate_domain))`.

A zero-provider unit test supplies five mixed IDs and three unmixed IDs and verifies all four selected IDs are a subset of mixed IDs and disjoint from unmixed IDs.

## 4. R2 repair 2 — actor-enforced atomic per-task exactly-once acquisition

The Stage-A acquisition universe is predeclared by a content-addressed manifest containing exactly 160 unique update task IDs in frozen stream order. One scientific acquisition unit is one complete K=8 task-pool acquisition.

### 4.1 Authorization and scope

Any future scientific Stage-A authorization must bind:

- exact 160-unit manifest path + SHA;
- `unit_count = 160`;
- exact claim root inside the unique contract-bound R2 run root:
  `.../checkpoints/stage_a_task_claims`;
- `attempt_before_any_provider_io = true`;
- `replay_allowed = false`;
- `ambiguous_recollection_allowed = false`.

Actor-side scope validation independently verifies the manifest SHA, its 160 unique IDs, equality with authorization task universe, requested-task membership, and exact claim-root location.

### 4.2 Atomic attempt burn

For every scientific task `u`, before awaiting **any** task rollout/provider coroutine, actor code calls `burn_task_attempt(...)`.

The attempt marker is created with filesystem:

```text
O_CREAT | O_EXCL | O_WRONLY
```

then its JSON is written and `fsync(fd)` is called before returning. The attempt marker status is:

`ATTEMPTED_IN_FLIGHT_DO_NOT_REPLAY`.

It binds task ID, contract SHA, authorization SHA, K=8 and prefix K `[1,2,4,8]` and explicitly records provider relaunch/replacement/ambiguous recollection as false.

If a seal already exists, the actor rejects the invocation. If an attempt marker already exists, the exclusive create fails and the actor raises **before provider I/O**. There is no replay exception.

Source-order static audit confirms:

`burn_task_attempt(...)` occurs before `await asyncio.gather(...)`.

### 4.3 Immutable seal

Only after K=8 rollouts complete and `freeze_nested_pools(...)` has created the frozen `pool_k8.json`, actor code calls `seal_task_attempt(...)`.

The seal is also exclusive/immutable and binds:

- task ID;
- same contract and authorization SHA;
- immutable attempt path + attempt SHA;
- exact `pool_k8.json` path + pool SHA.

Static audit confirms `freeze_nested_pools(...)` occurs before `seal_task_attempt(...)`.

### 4.4 Crash / ambiguity semantics

If a process dies after the attempt marker is durably created but before the seal is written, that task is a burned ambiguous unit. The same authorization cannot recollect it because a second actor invocation hits the immutable attempt marker before provider I/O.

The run therefore fails closed. Its run root/global lineage lease remain preserved for separate adjudication; automatic retry and replacement sampling remain forbidden. The intended recovery is **not** “try the task again.”

### 4.5 Terminal completeness

The Stage-A runner is allowed to emit terminal `COMPLETED_ALL_160_POOLS_PENDING_EQUAL_DOSE_ADJUDICATION` only after verifying:

- exact manifest = 160 unique expected tasks in frozen order;
- exactly 160 `*.attempt.json` markers;
- exactly 160 `*.sealed.json` receipts;
- for every task, status/task/contract/auth bindings match;
- every seal binds its corresponding attempt SHA;
- every seal binds the exact frozen `pool_k8.json` SHA;
- expected filename sets equal actual filename sets, so no extra/substituted unit exists.

A duplicated A plus omitted B therefore cannot be hidden by the global provider budget.

Zero-provider tests verify:

- first burn succeeds;
- second burn for the same unsealed unit raises;
- an ambiguous burned unit remains unsealed and cannot be recollected;
- seal binds attempt SHA + pool SHA;
- replay after seal also raises.

## 5. R2 repair 3 — common arm-blind Stage-B update order

Stage B still has **zero execution authority**, but its prospective causal sequencing is now frozen before Stage A.

For every `(stream_id, replicate_index)`, both WIN-C and MRW4 consume the same eight frozen Stage-A task/pool IDs in the identical order:

```text
sort task_id by
SHA256("semantic-transfer-v3-update-order|stream_id|replicate_index|task_id")
```

Properties explicitly frozen:

- task ID is in the ordering key;
- treatment arm is **not** in the update-pool ordering key;
- order is identical across WIN-C and MRW4;
- exactly eight unique task IDs are required.

A separate function handles only wall-clock state-arm scheduling:

```text
SHA256("semantic-transfer-v3-state-arm-order|stream_id|replicate_index|arm")
```

It cannot alter the within-arm pool order.

Heldout evaluation is non-mutating but its call schedule is separately frozen over `(heldout_task_id, arm)` tuples:

```text
SHA256("semantic-transfer-v3-heldout-eval-order|stream_id|replicate_index|heldout_task_id|arm")
```

A zero-provider test proves the common update-pool order is invariant to input task-list ordering and exactly equals the predeclared task-ID keyed hash order. Static audit confirms the update-order function contains task ID and no arm key.

## 6. R2 fail-closed control plane retained from R1

Before any provider call, a future valid Stage-A invocation must also satisfy the existing controls:

- fresh independent review after the exact R2 contract freeze;
- fresh model-identity qualification after the R2 contract freeze resolving exactly `deepseek-v4-pro-ga-260813`;
- separately minted single-use Stage-A authorization;
- unique R2 run root and global lineage lease;
- mode exactly `e1`;
- exact 160 update task IDs only; heldout excluded;
- exact K=8 and prefix K `[1,2,4,8]`;
- exact concurrency=1;
- initial skill only; updater receipts forbidden;
- exact suite/split/runtime/model bindings;
- fail-closed provider-budget ledger;
- no Stage B/updater/heldout/analyzer/public benchmark/paper authority.

The actor independently requires the contract-bound run root plus an active global lease with `RUNNING_STAGE_A_V3`, bound to the same contract SHA, authorization SHA, and run root. Direct actor invocation cannot choose an alternate run root/prefix/concurrency/skill.

R2 uses a new run root and new global lease namespace, distinct from rejected R1. Both remain absent at review time.

## 7. Current R2 zero-provider evidence

- R2 preflight: `PASS_ZERO_PROVIDER_SEMANTIC_TRANSFER_V3_STAGE_A_PREFLIGHT`
- relevant regression/control tests: 22/22 PASS
- code compile/import checks: PASS
- actor exact-once scope preflight: PASS
- runner exact authorization schema: PASS
- Stage-B arm-blind task-order preflight: PASS
- wrong K rejected: PASS
- heldout rejected: PASS
- wrong mode rejected: PASS
- bound code hashes match contract: PASS
- R2 run root absent: PASS
- R2 global lease absent: PASS
- provider calls: 0
- scientific execution: false
- current Stage-A authority: false

The R2 zero-provider repair audit additionally verifies at source-order level that the attempt burn precedes rollout await and the seal follows frozen-pool creation.

## 8. Audit questions — answer each explicitly

A. Is the core projection-only scientific object still coherent and narrowly claimed, or does R2 introduce any new confound before Stage A?

B. Is the MRW4 four-pool candidate domain now unambiguous and prospectively frozen to mixed pools only? Is any route left for an unmixed pool to enter the treated set?

C. Does the actor-level `O_EXCL` attempt burn before provider I/O close the prior valid-context replay hole? Consider concurrent/direct invocations under the same valid authorization.

D. Are crash/ambiguous-call semantics scientifically fail-closed? In particular, is refusing to recollect an attempted-but-unsealed task the correct way to prevent replacement sampling, even though it means the Stage-A run may become unusable and require separate adjudication?

E. Does the immutable seal plus terminal 160-attempt/160-seal universe validation close “duplicate A + omit B,” post-provider crash, and substituted-unit completeness holes sufficiently for the planned first-run-only Stage A?

F. Is there any remaining race or exactly-once hole that would permit a second provider call for the same scientific task under the same authorization before the actor notices prior consumption?

G. Does the new Stage-B task-ID-keyed arm-blind update ordering actually ensure WIN-C/MRW4 differ only in projection rather than update sequence? Is separating wall-clock arm order from within-arm pool order scientifically correct?

H. Are the heldout ordering and R=4 stochasticity semantics sufficiently specified for a later separately authorized Stage B, without converting measurement repeats into independent semantic units?

I. Did R2 preserve the prior claim boundaries: five frozen operationalized skeleton interactions only; finite 1/32 directional sign interpretation; observable router as hand-engineered actor-visible policy rather than learned semantic discovery?

J. Does the R2 authorization/preflight design remain fail-closed and zero-authority at present? Does any artifact in this review itself grant Stage-A or Stage-B execution?

K. Is there any implementation/protocol defect that MUST be fixed before the first Stage-A provider call? Do not propose broader experiments, extra models, more skeletons, or optional hardening. List only defects that change the immediate execution verdict.

## 9. Required final decision

Choose exactly one final verdict:

- `PASS_TO_SEPARATE_STAGE_A_AUTHORIZATION`
- `REVISE_BEFORE_STAGE_A`
- `STOP_V3`

A PASS means only: the frozen R2 protocol/control plane is scientifically adequate to proceed to the **separate fresh actor-model identity qualification**, after which the already-specified single-use authorization may be minted if identity passes. The review itself has no experiment authority.

If and only if PASS, use:

- execution recommendation: `ALLOW_SEPARATE_STAGE_A_AUTHORIZATION`
- remaining blockers: `[]`
- stage-B authority: `false`
- paper-claim authority: `false`
- scientific authority: `false`
- experiment authority: `false`

If REVISE or STOP, list only verdict-changing blockers.

End with exactly this machine-readable shape:

```json
{
  "contract_sha256_acknowledged": "f5382c552f2e6644e4cbda408510119664a8c6f8502628586c9ff5583abd1234",
  "verdict": "...",
  "execution_recommendation": "...",
  "remaining_blockers": [],
  "stage_b_authority": false,
  "paper_claim_authority": false,
  "scientific_authority": false,
  "experiment_authority": false
}
```
