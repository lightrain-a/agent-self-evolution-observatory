# Cross-Project Migration Checklist

Use this checklist once when opening a new ChatGPT Project and again whenever the research program is re-homed.

## A. Canonical handoff integrity

- [ ] The new project knows the repository and handoff tag.
- [ ] The handoff tag exists on `origin`, not only in a local clone.
- [ ] `START_HERE.md` is readable.
- [ ] `handoff_manifest.json` matches the actual handoff files.
- [ ] The handoff contains no credentials/secrets.

## B. Live-state recovery

- [ ] Fetch current `origin/main`.
- [ ] Record the exact canonical revision used for the current task.
- [ ] Do not assume the handoff base revision is still current.
- [ ] Identify the exact paper/track requested by the user.
- [ ] Find the latest dated/content-addressed artifacts for that track.
- [ ] Check source revisions, timestamps, object hashes, and provenance.
- [ ] Check whether any `current-*` file is stale relative to newer dated artifacts.
- [ ] Recover the current scientific gate and explicit execution authority independently.

## C. Scientific boundary recovery

- [ ] State the one-sentence scientific question.
- [ ] State the mechanism hypothesis and falsifiable prediction/boundary.
- [ ] Identify the strongest unresolved objection.
- [ ] Separate active claims from narrowed/revoked claims.
- [ ] Confirm that off-mainline experiments cannot silently re-enter the narrative.
- [ ] Confirm whether public benchmark/baseline breadth is adequate for the intended venue/scope.

## D. Execution safety and reproducibility

- [ ] Shared checkout status inspected.
- [ ] Dirty shared checkout is not modified.
- [ ] Isolated worktree/branch is used for edits.
- [ ] Long-run manifest/config is saved before execution.
- [ ] Seeds, environment, dataset revision, model revision, prompts, and evaluator revisions are pinned.
- [ ] Per-case outputs/trajectories/logs are persisted during execution, not only at the end.
- [ ] Resume/replay path is defined.
- [ ] Targeted validation is run before commit/push.

## E. Manuscript recovery

- [ ] Latest paper source and PDF are located by revision/artifact identity, not filename alone.
- [ ] Claim ledger is consistent with current evidence.
- [ ] Comparison table contains strong and simple baselines where applicable.
- [ ] Related-work collision claims are source-backed.
- [ ] Mechanism language is no stronger than the intervention identifies.
- [ ] Experiment results are analyzed, not merely copied into the paper.

## F. New-project response contract

Before continuing substantive work, the new project should report:

1. paper/track identity;
2. recovered canonical revision;
3. latest relevant evidence artifacts;
4. current scientific gate/disposition;
5. strongest unresolved objection;
6. next smallest falsifiable action;
7. whether execution is currently authorized.

If any of these cannot be recovered, say exactly which one is missing and proceed only with actions that do not require inventing it.
