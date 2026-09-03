# E2-R17 Semantic-Transfer V3 Stage-A R2 — verdict-changing review repair

Date: 2026-09-03
Scientific status: ZERO PROVIDER / PRE-STAGE-A
Parent frozen contract SHA256: `6104caa0d797b3a6bdb94988626f8715ea697fe1c896ef839fa1837a80513fdd`
Parent independent review verdict: `REVISE_BEFORE_STAGE_A`
Parent review conversation: `https://chatgpt.com/c/6a996224-4b10-83e8-a7d3-db5ca6b6747a`

This repair changes only the three verdict-changing protocol defects identified by the independent GPT-5.6 Sol / Extra High review. It does not change the 270-task generated suite, the 20 scientific update streams, the five crossed skeletons, the observable router, the requested actor model, K=8, the equal failure dose of four treated pools, or any scientific outcome. No scientific provider call is authorized by this document.

## R2-1 — mixed-only MRW4 treatment candidate domain

For stream `s`, after **all 160 Stage-A K=8 pools have been sealed**, define

```text
C_s = { p in stream s : p contains >=1 verifier-success trajectory
                         and >=1 verifier-failure trajectory }
```

The support gate is `|C_s| >= 4` for every one of the 20 frozen streams. If any stream fails, the only scientific verdict is `HOLD_SEMANTIC_TRANSFER_V3_INSUFFICIENT_EQUAL_DOSE_SUPPORT`.

If and only if all 20 streams pass support, the treated set is

```text
T_s = the four p in C_s with smallest
      SHA256("semantic-transfer-mrw4-v3|stream_id|task_id")
```

The hash ranking domain is **exactly `C_s` and no other pool**. Unmixed pools are ineligible and can never be selected. The failed-witness selector is defined only for a selected mixed pool and remains the lowest original rollout index among verifier-failure nonwinner trajectories.

This is not a new scientific algorithm: the frozen adjudicator already accepts `mixed_task_ids` as the candidate list. R2 makes the candidate domain an explicit contract invariant and adds a zero-provider test so prose and code cannot diverge.

## R2-2 — actor-enforced atomic per-task exactly-once acquisition

The Stage-A acquisition universe is predeclared as exactly the 160 task IDs in the frozen `e1_update_streams` split and content-addressed by a separate acquisition-unit manifest.

For every scientific Stage-A task `u`, the actor must perform the following state transition **before any external provider I/O for any of its K=8 rollouts**:

1. Resolve the contract-bound claim root inside the unique contract-bound run root.
2. Atomically create an immutable `u.attempt.json` marker using filesystem `O_CREAT|O_EXCL` semantics.
3. Fsync the marker before starting any provider call.
4. If the attempt marker already exists, reject the invocation before provider I/O. There is no replay exception.
5. Run the K=8 acquisition exactly once.
6. After all trajectories and nested pools are durably frozen, atomically create a separate immutable `u.sealed.json` receipt binding the attempt SHA and frozen K=8 pool SHA.

The attempt marker is never overwritten or removed. Therefore:

- a second direct actor invocation under the same otherwise-valid authorization/lease is rejected;
- a process crash after the attempt marker but before sealing leaves an ambiguous/in-flight burned unit;
- that unit may not be recollected automatically or under the same authorization;
- the entire run fails closed and preserves its run root / lineage lease for separate adjudication;
- provider retry limit 0 remains unchanged;
- replacement sampling remains forbidden.

The Stage-A runner must verify before emitting its terminal `COMPLETED_ALL_160_POOLS...` summary that there are exactly 160 immutable attempt markers and exactly 160 sealed receipts, one pair for each predeclared acquisition unit, with no missing or extra task IDs and with all contract / authorization / pool bindings intact.

A total provider-budget ledger remains an additional bound, but it is not used as a substitute for per-task exactly-once consumption.

## R2-3 — common Stage-B update order; arm order separated from pool order

Stage B still has **zero execution authority**, but its prospective ordering semantics are corrected before Stage A so the later projection-only causal intervention is well-defined.

For each stream `s` and replicate `r`, both WIN-C and MRW4 must consume the same eight frozen Stage-A task/pool IDs in this identical order:

```text
sort task_id by
SHA256("semantic-transfer-v3-update-order|stream_id|replicate_index|task_id")
```

The update-pool ordering key **contains the task/pool ID and does not contain the treatment arm**. Thus the sequence of state updates is identical across WIN-C and MRW4; only the learner-visible projection for the four frozen treated pools may differ.

If the implementation needs to decide which learned-state arm is constructed first in wall-clock time, that is a distinct scheduling object:

```text
sort arm in {WIN-C, MRW4} by
SHA256("semantic-transfer-v3-state-arm-order|stream_id|replicate_index|arm")
```

This arm scheduling key must never be reused as the within-arm pool ordering key.

Heldout evaluation is non-mutating, but its provider-call schedule is also frozen unambiguously as a deterministic ordering of `(heldout_task_id, arm)` tuples:

```text
SHA256("semantic-transfer-v3-heldout-eval-order|stream_id|replicate_index|heldout_task_id|arm")
```

The R=4 replicate semantics and seed rule remain unchanged: R is measurement replication, not semantic replication; if provider seed control exists, paired arms share the same pre-frozen replicate seed, otherwise no common-random-number claim is made.

## Unchanged scientific boundaries

- Acting remains verifier-winner fixed; only learning projection changes in Stage B.
- Five matched-skeleton interactions remain the independent mechanism units.
- The all-positive exact sign resolution remains 1/32 under the narrow frozen directional interpretation.
- The observable router remains an engineered actor-visible policy, not a claim of learned semantic discovery.
- Stage A remains search-pool acquisition/support qualification only: zero updater calls, zero learned states, zero heldout evaluations, zero treatment-effect inference.
- This repair grants no Stage-A or Stage-B authority.

## R2 gate

After code, tests, acquisition-unit manifest, R2 contract, and zero-provider preflight are frozen and content-addressed, obtain a **fresh independent ChatGPT-web review** using exactly GPT-5.6 Sol + Extra High. A prior review cannot authorize the revised contract. Only a fresh PASS on the exact new contract SHA may permit the separate fresh model-identity qualification and subsequent single-use Stage-A authorization step.
