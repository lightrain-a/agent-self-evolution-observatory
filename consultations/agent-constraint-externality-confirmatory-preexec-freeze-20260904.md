# Agent Constraint Externality — Confirmatory Pre-execution Freeze

Date: 2026-09-04  
Scientific object: `AGENT-CONSTRAINT-EXTERNALITY-20260831`  
Status: **ZERO-PROVIDER PRE-EXECUTION FREEZE — EXECUTION AUTHORITY CLOSED**

This addendum does not reopen the independently reviewed minimum-effective R2 design. It only freezes the two execution details that R2 intentionally left to a later pre-execution step: the exact topology-neutral repair-uptake eligibility surface and the exact development-only repeat/precision rule.

## 1. TARGET_ONLY_VERIFICATION_V1

Purpose: determine repair-uptake eligibility **before** any INDEPENDENT/LOW/HIGH topology treatment.

For each reserve family that already has a valid semantic source failure and one frozen repair artifact:

1. Start every verification branch from the same `common_pre_update_snapshot_sha256`.
2. The model-visible task contains the target instruction and TARGET constraints only.
3. No non-target instruction, topology label, coupling description, topology-specific context, or non-target evaluator readout is available.
4. Use two branches: `NO_UPDATE` and `REAL_REPAIR`.
5. `REAL_REPAIR` injects the exact frozen repair bytes. The same `repair_sha256` must later be reused in all INDEPENDENT/LOW/HIGH arms.
6. Run the already-frozen `R*` repeats on both branches.
7. Every planned unit must terminate normally and pass interface/measurement validity.
8. Define target uptake as

   `mean(target_success_REAL_REPAIR) - mean(target_success_NO_UPDATE)`.

9. The family is uptake-eligible only if the target-uptake delta is at least **+0.50**.

The +0.50 threshold is fixed before any topology outcome. With `R*=2`, it requires at least one net success difference across the two repeats; with `R*=3`, the attainable positive difference that clears the threshold is at least 2/3.

Once a family is admitted to the confirmatory topology panel, later topology-specific target success/failure is a treatment-responsive outcome. It is retained and jointly reported with collateral outcomes; it can never be used to delete the family or backfill a reserve family.

## 2. Development repeat qualification

Use exactly **6** development-only families. They are permanently excluded from confirmatory inference.

The initial qualification runs two repeats for each of:

- 3 topology conditions: INDEPENDENT / LOW / HIGH;
- 2 branches: NO_UPDATE / REAL_REPAIR.

This gives 36 within-condition cells and 72 development episodes.

The repeat decision is based only on **within-condition repeat disagreement**, never on the sign or mean of an UPDATE-vs-NO_UPDATE or HIGH-vs-INDEPENDENT effect.

### Freeze `R*=2`

Use two repeats if both are at most **0.10**:

- target-success disagreement rate between repeat 1 and repeat 2;
- mean absolute CRR difference between repeat 1 and repeat 2.

### Add one development repeat and freeze `R*=3`

If the R2 rule fails but both metrics remain at most **0.20**, run exactly one additional repeat on the same six development families.

Freeze `R*=3` only if, over the three repeats:

- target non-unanimous-cell rate is at most 0.20; and
- mean within-cell CRR range is at most 0.20.

### Hard stop

Do not proceed to confirmatory execution if:

- either two-repeat instability metric exceeds 0.20;
- any repeat-qualification unit is technically invalid;
- the three-repeat stability rule still fails.

`R>3` is forbidden. A fourth seed/repeat may not be added to rescue instability.

## 3. Precision rule for N*

The reviewed design allows `N* ∈ {12,16,20,24}`. This addendum freezes the selection algorithm, not a desired numerical outcome.

After `R*` is fixed, compute on the same six permanently excluded development families:

- each family’s pooled RQ1 UE dispersion;
- each family’s RQ2 `UE_HIGH - UE_INDEPENDENT` dispersion.

For each quantity, use the conservative dispersion estimate:

`max(full-sample SD, every leave-one-family-out SD)`.

The decision artifact must not emit or use the development mean effect or effect sign.

Planning target:

- smallest scientifically meaningful planning effect: **0.20** absolute effect units;
- maximum planning standard error: **0.10** (= half of the planning effect).

Choose the smallest `N*` in `{12,16,20,24}` for which

- `conservative_SD_RQ1 / sqrt(N*) <= 0.10`, and
- `conservative_SD_RQ2 / sqrt(N*) <= 0.10`.

If `N*=24` still fails either condition, stop at `PRECISION_QUALIFICATION_STOP_N24_INSUFFICIENT`. Do not enlarge the reserve to 32/48 and do not add models/seeds to rescue the design.

This is a workload-planning precision rule, not a confirmatory effect-sign or p-value rule.

## 4. Reserve and panel selection

- Prospectively generate exactly 24 confirmatory reserve family IDs.
- Freeze stable ordering with salt `ACE-CONFIRMATORY-PANEL-ORDER-20260904-V1`.
- A family may be eligible only from pre-topology facts: valid semantic source failure, valid frozen repair artifact, TO-V uptake delta >=0.50, and no interface/measurement invalidity.
- Select the first `N*` eligible family IDs under the stable-hash ordering.
- If fewer than `N*` families are eligible, stop for insufficient support; do not silently shrink N.
- Reserve activation/backfill after any I/L/H outcome is forbidden.

## 5. Mechanical anti-rescue invariants

The implementation must test all of the following before any human execution authority can be granted:

- flipping all development treatment-effect signs leaves N* unchanged;
- development mean/sign is absent from the N* decision artifact;
- target outcome inside I/L/H cannot alter eligibility;
- a family with topology-specific target failure remains in the frozen panel;
- fewer than N* pre-topology eligible families causes STOP rather than shrinking N;
- any technical invalidity in repeat qualification stops qualification rather than selecting more repeats;
- R>3 is impossible;
- all provider/scientific execution authorities remain false in this freeze artifact.

## 6. Authority boundary

This addendum creates **zero** provider/model trajectories and **zero** externality/topology outcomes.

It does not authorize:

- Gate 0 direct actor execution;
- Gate 1 Direct-SFQ execution;
- development repeat qualification;
- TARGET_ONLY_VERIFICATION;
- RQ1/RQ2;
- RQ3;
- RQ4;
- secondary actor or external updater;
- any paper claim expansion.

The next valid step after mechanical consistency closure is a separate human execution-authority decision.
