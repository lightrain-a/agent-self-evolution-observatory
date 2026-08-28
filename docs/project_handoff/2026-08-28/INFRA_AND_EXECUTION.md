# Infrastructure and Execution Conventions

This file records durable operational rules. It intentionally excludes passwords, tokens, private keys, personal email addresses, and unverified endpoint details.

## 1. Canonical repository

Primary research-system repository:

```text
/home/wyt/code/agent-self-evolution-observatory
```

The 69 server has been used as the canonical repository host for this program.

Important: the shared checkout may be dirty, stale, or behind `origin/main`. Never equate the visible shared checkout with canonical state without checking Git.

## 2. Worktree discipline

For any substantive task:

1. inspect shared checkout status;
2. `git fetch`;
3. record `origin/main` SHA;
4. create a task-specific isolated worktree/branch from the validated canonical parent;
5. modify/test only in the isolated worktree;
6. inspect diff;
7. run targeted validation;
8. commit with a narrow descriptive message;
9. push the task branch when the work should be recoverable by another project/agent;
10. merge only through the project's normal adjudication process.

Do not overwrite or clean unrelated dirty files in a shared checkout.

## 3. Server naming and endpoint rule

The broader research program has used server aliases including variants such as vla52, vla60, vla67, vla69, vla231, vla232, and other experiment hosts.

Because endpoints and routing have changed and at least one historical vla52 address was previously misrecorded, this handoff does **not** freeze IP addresses.

Before execution:
- resolve the current alias/address from the user's current SSH config or canonical infrastructure documentation;
- test direct connectivity;
- confirm the intended filesystem and GPU inventory;
- record the verified endpoint only in the run manifest if needed;
- do not invent a jump-host route that is not explicitly supported.

## 4. Heavy experiment storage

Keep large datasets, checkpoints, and raw rollouts outside the Git repository when appropriate. Git should contain the manifest, hashes/pointers, code, compact derived evidence, and decisions needed to reproduce or audit them.

A previously used shared embodied-experiment convention is:

```text
/data/zmy/exp/emise/
  shared/
    raw_rollouts/
    probes/
    manifests/
  policy/
    runs/
    checkpoints/
    replay/
  belief/
    runs/
    checkpoints/
    datasets/
```

Treat this as a convention, not proof that every current experiment uses those directories.

## 5. Required run-location record

Every long or remote experiment should persist a small status record containing at least:

```text
run_id
paper/track
scientific question
server alias / verified host
working directory
Git SHA / branch
command or scheduler job
PID/job ID
GPU allocation
start timestamp
log path
artifact/output path
progress/heartbeat path
resume command
expected completion condition
failure/restart policy
```

This record should be written when the process starts, not reconstructed from chat after the fact.

## 6. Runtime persistence rule

For long runs, write incremental artifacts so partial progress survives:
- per-case JSONL/Parquet/other append-safe records;
- periodic aggregates;
- logs;
- explicit failed-case records;
- checkpoint/state if resumption is meaningful;
- a final manifest that lists expected vs materialized outputs.

Do not make the final process exit the only place where scientific data becomes available.

## 7. Experiment provenance

At minimum, bind outputs to:
- repository SHA;
- experiment/config ID;
- benchmark/data revision;
- checkpoint/model identity;
- seed(s);
- dependency/runtime image or environment summary;
- evaluator version;
- output hash/manifest where practical.

For evidence-sensitive tasks, content-addressed artifacts are preferred.

## 8. External API/provider discipline

External model/API availability is an execution constraint, not a reason to change the scientific question.

When providers are unavailable:
- finish design, literature review, manifests, runners, local validation, and preregistration-like contracts first;
- do not fabricate provider results;
- do not substitute a different provider/backbone unless the substitution is scientifically justified and versioned as a new design;
- when access returns, execute the already-frozen qualified plan where possible.

## 9. Multi-agent/model consultation

Consultations with systems such as Kimi/DeepSeek/other reviewers can be useful for adversarial design critique. Preserve their outputs as **review artifacts**, not experimental evidence or authorization.

A productive consultation asks each reviewer to independently attack:
- novelty collision;
- confounds;
- identifiability;
- baseline strength;
- external validity;
- weakest claim;
- cheapest falsifying experiment.

Resolve disagreements through evidence/design, not majority vote.

## 10. Obsidian

A previously used human-note root is:

```text
D:\ProgramData\Obsidian\Yu
```

Use Obsidian for human navigation, synthesis, and lessons. The Git handoff should remain canonical for cross-project machine recovery.

Recommended Obsidian entry: one note titled `Research Project Handoff` containing the Git repository, branch/tag, handoff path, and a short instruction to read `START_HERE.md`.

## 11. Secret handling

Never place in this handoff:
- passwords;
- API keys;
- SSH private keys;
- authentication cookies;
- private email credentials;
- security answers.

Use the user's existing secure connection/secret mechanisms. The handoff should only explain *where and how to recover context*, not carry credentials itself.
