# Independent adversarial review — STRI Claim-Expansion Experiment Plan V2.1

Date: 2026-09-04
Reviewer role: fresh independent senior ICLR/NeurIPS/ICML agent-systems methodology reviewer
Reviewer substrate: ChatGPT Web via Oracle Browser on host 52
Model: GPT-5.6 Sol
Thinking effort: Extra High
Scientific outcomes opened: none
Execution authority: CLOSED

## Frozen review lineage

### V2 object

Commit:

`2de8168f55f93078a4fbbe33d3a247b75bcd8022`

Initial independent verdict:

`REVISE_BEFORE_EXECUTION`

The reviewer explicitly judged the proposed workload direction as scientifically appropriate and did **not** request more models, benchmarks, ordinary baselines, or P0 checkpoints. It identified four verdict-changing protocol defects:

1. P0→P1 could open on gain-only `D_sem>0` even when P1's loss/reacquisition estimand `L0` was empty, and the gate did not guarantee P1's own minimum checkpoint geometry.
2. P1 did not fully specify which representation-derived cache/index/router/search/load state is restored in the one-shot arm versus retained in the persistent arm.
3. The advertised 24 P0 access replays omitted the workload required to acquire natural Original-only source trajectories if no frozen pool already existed.
4. P1's prospective 4–8 checkpoint range allowed unnecessary/adaptive expansion; the reviewer judged 4 qualified checkpoints × 3 arms = 12 full trajectories to be the smallest convincing mechanistic block.

One optional no-new-provider addition was suggested: descriptively decompose P0 semantic divergences into cases associated with native ranking changes versus whole-package semantic-capacity prefix admission. This was explicitly not a gate or baseline requirement.

### V2.1 repair object

Commit:

`b13354f6b572d798afe3ee323d0c87d40e00a1f0`

Repairs:

- GO_P1 now requires exactly 4 loss-bearing (`L0 != empty`) checkpoints, valid ID placebos, all contract checks, and >=2 independent source trajectories. If >4 qualify, exactly 4 are selected by frozen hash. If <4 qualify, dynamic expansion stops.
- P1 now has an explicit treatment-state boundary. Representation-controlled package/index/embedding/router/search/load/cache state is restored to Original in the one-shot arm before the next access while endogenous historical consequences of the t0 exposure are preserved; persistent keeps Repacked representation state for later accesses.
- Checkpoint source acquisition is now separately bounded: either a pre-existing frozen untouched pool or exactly 8 prospectively frozen Original-only natural source trajectories. No adaptive extension is allowed; insufficient eligibility returns `STOP_INSUFFICIENT_ELIGIBLE` before P0 replays.
- P1 is fixed at exactly 4 checkpoints × 3 arms = 12 full trajectories. No automatic 5–8 checkpoint expansion.
- P2 is a separate optional second-access-architecture claim branch rather than an automatic next stage.
- The optional ranking-vs-prefix diagnostic uses existing P0 logs only and remains descriptive.

## Final re-review

The same independent reviewer re-audited only the four required repairs and returned:

> All four prior verdict-changing objections are now closed. I find no new contradiction introduced by the repairs and no remaining defect that should block execution authority once that authority is separately granted.

Its workload judgment was:

- P0: 24 O/R/I access replays is sufficient; 8 checkpoints are enough for the explicitly mechanistic, non-population claim.
- Checkpoint source acquisition: 0 new trajectories with a valid frozen pool, otherwise exactly 8 Original-only natural trajectories under a finite prospectively frozen schedule.
- P1: exactly 12 full trajectories is sufficient; adding checkpoints after a clean 4-checkpoint block would buy breadth rather than identification and create avoidable adaptive continuation.
- P2: 24 access replays is sufficient **only** if an explicit second-architecture access claim is pursued; otherwise do not execute it.
- No additional models, benchmarks, checkpoints, trajectories, or MMR-style main baselines are required for execution validity.

Final verdict:

`PASS_MINIMUM_CLAIM_EXPANSION_DESIGN`

## Scientific boundary

This review authorizes no execution. It validates only the prospective design. The current narrow STRI paper remains submission-ready without P0/P1/P2. Any provider/model/substrate/task/seed freeze and actual execution authority must be opened separately and prospectively.
