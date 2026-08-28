# Current State Recovery Protocol

This document prevents a new project from treating an old summary as live scientific state.

## 1. Why recovery is required

At handoff creation, `generated/current-research-status.json` reports `generated_at=2026-08-24`, while the repository already contains multiple 2026-08-28 review/evidence directories. Therefore a file named `current-*` is not automatically current.

The correct question is not “what did the last chat say?” but:

> What is the newest canonical revision, and what is the newest admissible evidence for the exact research object being worked on?

## 2. Recovery algorithm

For every new session or project migration:

1. Fetch the remote Git refs and record `origin/main` SHA.
2. Inspect the shared checkout only to understand its state; do not assume its HEAD equals canonical and do not write through a dirty shared checkout.
3. Search `generated/` and versioned manifests for the exact paper/candidate identifier and inspect dates, source revisions, hashes, and authority fields.
4. Compare general summary files with newer paper-specific artifacts. The more specific, newer, content-addressed artifact wins unless a later canonical reconciliation explicitly supersedes it.
5. Distinguish **observation**, **evidence**, **adjudication**, and **authorization**. They are different state transitions.
6. Recover the latest manuscript/claim ledger independently from the experiment state; a manuscript may lag science or vice versa.
7. Produce a short recovered-state record before executing anything.

## 3. Minimal recovered-state record

A new agent should state:

```text
track/paper:
canonical origin/main SHA:
working branch/worktree:
latest relevant artifact(s):
artifact date/source revision/hash if available:
current scientific disposition:
experiment authority: yes/no
GPU/provider authority: yes/no
strongest unresolved objection:
next falsifiable action:
claim boundary:
```

If any authority field is unclear, treat it as **NO** until resolved from canonical evidence.

## 4. Useful canonical surfaces

These are navigation surfaces, not guarantees of freshness:

- `generated/paper-registry.json`
- `generated/research-system-state.json`
- `generated/current-research-status.json`
- `generated/research-timeline.json`
- `generated/paper-first-*.json`
- paper/track-specific dated artifacts under `generated/`
- versioned experiment plans, manifests, claim audits, verification receipts, and canonical reconciliations
- downloadable paper/source artifacts under `downloads/` when relevant

Always inspect the metadata and search for newer track-specific files.

## 5. Supersession rule

A later artifact supersedes an earlier one only when it refers to the same scientific object and its role permits supersession. For example:

- a later **review** can supersede an earlier review judgment;
- a later **canonical reconciliation/projection** can supersede an earlier state projection;
- a new raw result does not automatically supersede a frozen adjudication;
- metadata availability does not create behavioral evidence;
- a paper QA PASS does not create method/scientific authority;
- a model consultation does not authorize GPU/provider execution.

## 6. Chat/project-memory rule

Old conversation text is useful for reconstructing intent and rationale, but should be used as a search hint. It is not sufficient evidence for current run state, scientific claims, or authorization.

## 7. When live state is inconsistent

If two current-looking artifacts disagree:

1. stop execution;
2. identify whether the disagreement is about data, interpretation, or authority;
3. trace each artifact to source revision and parent evidence;
4. create an explicit reconciliation artifact rather than silently choosing the preferred result;
5. preserve the losing/older interpretation for auditability.

This rule exists because stale or orphaned experimental results can later re-enter paper writing and pull the narrative away from the actual scientific question.
