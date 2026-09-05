# B1 R80 — Pre-execution scale freeze and 321-run authority

Date: 2026-09-05

## Purpose

R72/R73 already passed a fresh independent R3 review with a frozen 321-trajectory design. R80 performs the final zero-outcome actions needed before execution:

1. freeze the future targeted capability-boundary model before any R72/R73 outcome is opened;
2. freeze an outcome-blind matched-control selection rule for that future scale check;
3. avoid modifying the dirty historical shared MemRL checkout by binding a clean worktree at the exact same pinned source commit; and
4. grant execution-only authority for the already-reviewed Qwen/Llama stages.

R80 does **not** change the R72/R73 panel, arms, schedule, statistics, missingness policy, or claim hierarchy.

## Future strong-model freeze

The selected external-validity executor is the already-present local checkpoint:

`Qwen3.5-27B`

Host/path:

`222.20.126.231:/data/lry/models/Qwen3.5-27B`

The checkpoint identity is frozen by a full recursive file manifest before any prospective P/T outcome is opened. Its role is targeted external-validity / capability-boundary diagnosis only; it is not a third primary executor and receives no execution authority in R80.

## Matched-control rule

After the sealed Qwen stage is eventually opened:

- `D` = complete Qwen P/T pairs whose terminal outcomes disagree;
- `C` = complete Qwen P/T pairs whose terminal outcomes agree;
- technical-missing pairs enter neither set and are never replaced.

If `D=0`, no strong-model scale check runs.

If `1 <= |D| <= |C|`, R80 chooses exactly `|D|` distinct controls by a deterministic greedy one-to-one rule. Discordant tasks are processed in frozen R54 eligible order. Each unused concordant candidate is ranked by a pre-outcome lexicographic cost using only:

1. retrieved-memory count match;
2. success/failure provenance composition;
3. command/skill-signature Jaccard distance;
4. signature-size difference;
5. task-instruction byte-length difference;
6. frozen R54 order distance; and
7. deterministic pre-outcome tie breakers.

No terminal outcome enters the matching cost. The future strong-model workload is then exactly:

`D discordant + D matched controls × P/T = 4D trajectories`.

If `|D|>|C|`, the scale check fails closed under this plan rather than changing the control rule.

## Execution realization

The parent manifests point to a historical shared checkout that now contains unrelated untracked temporary files. R80 does not clean, delete, ignore, or otherwise modify that checkout.

Instead it binds:

`/data/wyt/b1-r77-clean-memrl`

at the exact pinned source revision:

`c1b322ca43de36ddf64c6712f89d0095bfc35ce0`

The R80 wrapper re-runs the frozen R73 static checks, verifies the clean checkout against the parent revision, pinned source-file hashes, and validation split, changes only the checkout path in memory, then delegates rendering, exposure semantics, retry policy, trace persistence, and terminal ledger behavior to R73.

## Authority

R80 execution authority opens only:

- Qwen execution: yes;
- Llama execution: yes;
- GPU use for those frozen stages: yes.

It keeps closed:

- analysis;
- PSMG;
- L3;
- paper claim changes;
- Qwen3.5-27B scale execution.

Execution order is Qwen 189 first, then Llama 132, with no effect inspection before a separate analysis authority is generated after the required stage seals. Operationally, R80 may execute the frozen schedule in fixed-size chunks that stop only after terminal ledger items; chunk boundaries are chosen without inspecting outcomes and never alter schedule order, retry policy, or treatment realization.

## Validation

R80 hard tests cover receipt integrity, strong-model pre-outcome freezing, 66-task outcome-blind covariates, all 66×65 pair costs, deterministic one-to-one control selection, fail-closed insufficient-control behavior, narrow authority scope, and path-only source migration.
