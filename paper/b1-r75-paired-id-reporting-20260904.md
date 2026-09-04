# B1 R75 — Paired Task-ID Outcome Reporting

Date: 2026-09-04  
Status: ZERO-PROVIDER / DESCRIPTIVE REPORTING EXTENSION  
Paper: `D2-PAPER-FAILURE-MEMORY-PROVENANCE`

## Why this layer is required

Aggregate success totals do not determine whether the same tasks succeed under two paired conditions.

For a paired binary experiment, these two results are scientifically different:

```text
P success = 17/32
T success = 17/32
```

could mean:

```text
same 17 task IDs succeed under both arms
```

or:

```text
15 succeed under both,
2 succeed only under P,
2 different tasks succeed only under T.
```

Both have a net effect of zero percentage points, but only the second shows task-level outcome substitution.

R75 therefore adds an ID-level descriptive reporting layer without changing the R72/R73 experiment, statistical gates, workload, or execution authority.

## Historical R56 Qwen audit

Content-only successes, 15:

`15, 98, 125, 150, 193, 202, 235, 236, 282, 325, 335, 414, 441, 467, 470`

Truthful-field successes, 16:

`15, 98, 125, 150, 193, 202, 235, 236, 252, 282, 325, 335, 414, 441, 467, 470`

Paired decomposition:

- both success: 15;
- content-only-only success: 0;
- truthful-only success: 1 — **Task 252**;
- both fail: 16;
- outcome discordance: 1/32 = 3.125%;
- success-set Jaccard: 15/16 = 0.9375.

Thus Qwen's historical result is not a broad reshuffling of successful tasks. The content-only success set is a strict subset of the truthful-field success set, and Task 252 is the sole terminal gain.

## Historical R61 Llama audit

Content-only successes, 17:

`15, 71, 98, 125, 150, 235, 236, 252, 260, 275, 325, 327, 414, 441, 463, 467, 470`

Truthful-field successes, 17:

`15, 71, 98, 136, 150, 193, 235, 236, 252, 260, 275, 325, 414, 441, 463, 467, 470`

Paired decomposition:

- both success: 15;
- content-only-only success: 2 — **Tasks 125 and 327**;
- truthful-only success: 2 — **Tasks 136 and 193**;
- both fail: 13;
- outcome discordance: 4/32 = 12.5%;
- success-set Jaccard: 15/19 ≈ 0.7895.

Therefore the historical Llama `17/32 vs 17/32 = 0pp` result must not be narrated as no task-level effect. Four task outcomes switch arm-specific success status and cancel in the aggregate count.

The four discordant tasks are substantively heterogeneous:

- Task 125: change `testuser` login shell to `/bin/zsh` and ensure `/bin/zsh` is in `/etc/shells` — content-only-only success;
- Task 327: multi-step user/group/shared-directory/file/symlink/shell configuration — content-only-only success;
- Task 136: construct sample log files, count ERROR lines, write `/reports/error_count.txt` — truthful-only success;
- Task 193: change `testuser` shell to `/bin/newshell`, add it to `/etc/shells`, verify — truthful-only success.

Tasks 125 and 193 are both shell-configuration tasks yet flip in opposite directions, so these four historical discordances do not support a simple task-family mechanism claim.

## Cross-executor overlap is also incomplete

Under historical content-only:

- Qwen successes: 15;
- Llama successes: 17;
- both-executor success IDs: 11;
- success-set Jaccard: 11/21 ≈ 0.5238.

Under historical truthful field:

- Qwen successes: 16;
- Llama successes: 17;
- both-executor success IDs: 12;
- success-set Jaccard: 12/21 ≈ 0.5714.

This is descriptive executor dependence only. It does not authorize cross-model pooling.

## Required reporting for the future R72/R73 experiment

For every paired contrast, report both the aggregate effect and the identity decomposition.

### Qwen primary, P vs T, n=66

Required:

- P success count;
- T success count;
- net T-P success-count difference;
- both-success count and task IDs;
- P-only-success count and task IDs;
- T-only-success count and task IDs;
- both-fail count and task IDs;
- all discordant task IDs;
- success-set intersection / union;
- success-set Jaccard;
- outcome agreement / discordance fraction.

### Qwen correctness, S vs T, n=57

Use the same ID-level report. The existing R72 confirmatory gate remains unchanged.

### Llama replication, P vs T, n=66

Use the same ID-level report and keep the executor estimate separate from Qwen.

## Main-table recommendation

At minimum, the paired outcome table should show:

| Contrast | Left success | Right success | Both success | Left-only | Right-only | Both fail | Net Δ |
|---|---:|---:|---:|---:|---:|---:|---:|

Exact discordant task IDs should be listed in the appendix or companion audit table.

## Interpretation rule

Never infer:

```text
same aggregate success count
=> same successful tasks
=> no task-level treatment effect
```

Instead distinguish:

1. **net effect** — how many more/fewer tasks succeed overall;
2. **task substitution** — which individual tasks switch success/failure status;
3. **agreement structure** — how stable the successful-task set is across arms.

R75 is descriptive and does not change R72/R73 execution, inferential hierarchy, R3 PASS, or the user-gated execution hold.
