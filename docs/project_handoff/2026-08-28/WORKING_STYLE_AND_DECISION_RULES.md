# Working Style and Decision Rules

This file captures durable collaboration preferences that materially affect how research work should be carried out. These are process constraints, not scientific evidence.

## 1. Do the work, do not only describe the work

When tools/servers are available, prefer inspecting the real repository, artifacts, jobs, logs, and outputs over giving a hypothetical command list.

Never claim a checkout, run, commit, upload, submission, review, or server connection happened unless it was actually verified.

## 2. Analyze after experiments

Obtaining a result is not the end of an experiment. Always analyze:
- whether it supports the intended hypothesis;
- alternative explanations;
- failures/confounds;
- how it changes the paper story;
- what should be learned by the research system;
- whether another experiment is actually justified.

## 3. Preserve the paper mainline

Do not chase every interesting local result. Repeatedly re-anchor to the paper's original scientific question and motivation.

When an exploratory branch is useful but off-mainline, keep it in an archive/side branch with explicit narrative status rather than silently allowing it to influence the paper later.

## 4. Prefer scientific depth to integration-only novelty

A paper should not merely combine several known techniques. Seek a deeper insight:
- a newly isolated scientific object;
- a mechanism;
- a regime/boundary law;
- a falsifiable causal prediction;
- a controlled intervention;
- a meaningful engineering/scientific implication.

## 5. Strong substrate and baseline expectations

When possible, use:
- top-venue/peer-reviewed and community-recognized base methods;
- public datasets/benchmarks;
- public baselines;
- model families consistent with the comparison literature;
- pilot experiments before full-scale runs.

Do not choose a niche baseline simply because it is convenient to run.

## 6. Persist long-run state

For nontrivial experiments, record execution location, command, process/job identity, logs, outputs, checkpoints/partial results, and resume instructions during the run so a later session can safely continue.

## 7. Reviewer-grade skepticism

Use Stanford/top-conference-style or independent reviewer critique to pressure-test a paper, but do not treat prestige labels or model opinions as authority.

The useful output is the objection and the falsifiable fix, not the positive tone of the reviewer.

## 8. Multi-model consultation

Independent consultation with multiple strong models can be used to diversify critique and design alternatives. Their suggestions should be reconciled against evidence and the frozen scientific question.

Do not let an external model redefine the paper by momentum.

## 9. Server/canonical discipline

Before writing a shared repository:
- verify the real server/path;
- inspect Git state;
- do not write a dirty shared checkout;
- prefer isolated worktrees;
- preserve unrelated changes;
- commit task-scoped work when it becomes a durable artifact.

## 10. Communication style for research progress

Useful progress reporting is concrete:
- what was actually checked/done;
- what was learned;
- what remains blocked;
- what scientific decision follows.

Avoid generic status language that does not identify evidence or next action.

## 11. No fake closure

If evidence is missing, say it is missing. If an external API is unavailable, prepare everything else but do not manufacture completion. If a claim remains blocked, preserve the HOLD.

Partial but truthful progress is better than a false end-to-end success claim.

## 12. Reusable handoff preference

When a project becomes large, compress it into a canonical, versioned, queryable handoff rather than relying on dozens of chats. New sessions should load only the relevant working set after reading the global entry point.
