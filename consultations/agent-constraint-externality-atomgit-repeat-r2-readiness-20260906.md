# Agent Constraint Externality — AtomGit R*=2 development repeat readiness

Date: 2026-09-06
Scientific object: `AGENT-CONSTRAINT-EXTERNALITY-20260831`

## Verdict

`ATOMGIT_REPEAT_DEV_R2_ZERO_PROVIDER_READY_AWAITING_SEPARATE_HUMAN_AUTHORITY`

The six development families and six exact model-generated repairs are frozen. The initial repeat-qualification panel is now mechanically executable, but **no repeat/topology provider authority is open**.

## Frozen R*=2 panel

- development families: 6, permanently excluded from confirmatory inference;
- category balance: 3 FG + 3 TNF;
- topology arms: `INDEPENDENT / LOW / HIGH`;
- branches: `NO_UPDATE / REAL_REPAIR`;
- repeats: `1 / 2`;
- repeat seeds: `1201 / 1202`;
- total condition cells: 36;
- total episodes: 72;
- `R3` seed `1203` is reserved only if the direction-blind R2 stability rule explicitly triggers one extra repeat;
- `R>3` remains forbidden.

`REAL_REPAIR` is always the exact frozen repair byte string appended after the base arm instruction with one frozen prefix. `NO_UPDATE` contains no repair bytes. Repair bytes are identical across every arm/repeat for a family.

## CRR and paired-state binding

The frozen collateral regression rate is the original protocol definition:

`CRR = newly failed initially-satisfied non-target constraints / eligible non-target constraints`.

Every development arm contains exactly two initially satisfied non-target constraints, so the runner computes CRR mechanically as the fraction of those two evaluators that are false. This is equivalent to `1 - non_target_preservation` here, but the implementation uses the per-constraint booleans directly.

For every `(family, arm, repeat)` pair, NO_UPDATE and REAL_REPAIR must begin from the same scientific AppWorld state. A dedicated `scientific_state_sha256` hashes only the family-relevant App DBs and excludes supervisor prompt text. Runtime adjudication rejects a pair if those scientific-state SHAs differ.

## Zero-request Q1

The new topology wrapper was exercised on both branches of one real paired cell through AtomCode MCP up to `tools/list`, with **zero model requests**.

- family: `ACE-DEV-FG-104`
- arm: `INDEPENDENT`
- repeat: `1`
- scientific-state SHA on both branches: `0332183fca56607ad2fb2d4e2c7091b1f6cc1b250ce14a59544dba2843ac6d2a`
- the full initial snapshot SHA differs across branches as expected because it includes the visible instruction;
- both branches listed 84 AppWorld tools;
- no scientific episode or topology outcome was created.

The AtomGit account observation immediately before and after readiness remained `470/500 used, 30 remaining`, proving the readiness/Q1 path consumed zero model requests. This is only an operational observation, not a reservation. The frozen runner requires at least 117 remaining before starting a new paired cell and at least 61 before each individual undispatched episode. With 30 remaining at readiness time, execution would therefore HOLD before provider dispatch even if authority existed.

## Direction-blind adjudication

After all 72 episodes finish normally, the adjudicator first checks exact matrix coverage, paired scientific-state identity, and exact repair SHA binding. It then runs only the preregistered within-condition stability rule:

- freeze `R*=2` if target disagreement rate <= 0.10 and mean absolute CRR repeat difference <= 0.10;
- require exactly one third repeat if R2 fails but both metrics remain <= 0.20;
- otherwise STOP for excessive stochasticity / technical invalidity.

Only if `R*=2` is frozen does the same development panel feed the existing direction-blind precision rule for `N* ∈ {12,16,20,24}`. The decision artifact emits dispersion/SE only and no development effect mean or sign.

## Authority boundary

Still false:

- development repeat qualification execution;
- TARGET_ONLY_VERIFICATION;
- confirmatory source/repair;
- RQ1/RQ2;
- RQ3;
- RQ4;
- paper-claim expansion.

The next legal action is a **separate human execution authority for exactly the frozen 72-episode R*=2 development panel**. If current quota is below the predispatch headroom gate, the runner must HOLD without burning a unit.
