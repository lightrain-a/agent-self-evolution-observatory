# Bootstrap Instructions for a New ChatGPT Project

Use this file as the initial instruction/context handoff when creating a new ChatGPT Project for this research program.

## Recommended project setup

Upload this handoff directory to the new project, or ensure the new project can read the canonical Git repository through the approved workspace tool.

The minimum useful files are:
- `START_HERE.md`
- `CURRENT_STATE_RECOVERY.md`
- `RESEARCH_PORTFOLIO.md`
- `SCIENTIFIC_OPERATING_SYSTEM.md`
- `FAILURE_AND_REPAIR_PLAYBOOK.md`
- `INFRA_AND_EXECUTION.md`
- `WRITING_AND_REVIEW.md`

## Initial prompt for the new project

```text
This is the continuation of a large research program. Do not reconstruct the project primarily from chat memory.

First read the project handoff package in this order:
1. START_HERE.md
2. CURRENT_STATE_RECOVERY.md
3. RESEARCH_PORTFOLIO.md
4. SCIENTIFIC_OPERATING_SYSTEM.md
5. FAILURE_AND_REPAIR_PLAYBOOK.md
6. INFRA_AND_EXECUTION.md
7. WRITING_AND_REVIEW.md

Then recover the true current state from the canonical repository:
- fetch/check the latest origin/main revision;
- do not write a dirty shared checkout;
- find the latest exact artifacts for the research track named in my request;
- verify timestamps, source revisions, hashes/object identity, and authority;
- treat chat summaries and old current-state files only as navigation hints;
- distinguish evidence, adjudication, experiment authority, GPU/provider authority, and paper readiness.

Before doing new work, report only:
1. the paper/track you believe I mean;
2. canonical revision recovered;
3. latest relevant evidence/state artifacts;
4. current scientific gate/disposition;
5. strongest unresolved scientific objection;
6. the next smallest falsifiable action;
7. whether execution is authorized.

Research invariants:
- keep the paper anchored to its named scientific question;
- prefer scientific object → mechanism → falsifiable regime/boundary → controlled intervention → decision;
- smoke test is not scientific validation;
- pilot before full experiment;
- public/top-venue substrates and strong baselines are preferred when broad audience relevance matters;
- simple baselines must not be hidden;
- operational localization is not automatically mechanism causation;
- bundled treatments require narrower causal claims;
- artifact existence/receipt PASS does not imply scientific or execution authority;
- HOLD/negative/narrow outcomes are valid;
- never outcome-shop thresholds/guards/exclusions;
- persist per-case outputs/logs/configs/provenance during long runs;
- analyze every experiment and feed reusable lessons back into the system;
- preserve revoked/off-mainline evidence without allowing it to silently re-enter the current paper narrative.

Do not copy credentials, passwords, tokens, or private keys into project files or chat.
```

## What should remain in ChatGPT memory

Only small, durable preferences/pointers are appropriate, for example:
- use the canonical handoff rather than relying on old chat summaries;
- keep scientific evidence and execution authority separate;
- preserve project-specific research gates;
- use isolated worktrees rather than modifying dirty shared checkouts.

Do not try to store the full paper portfolio, live experiment state, or server credentials in model memory.

## When starting one specific paper

After global recovery, create a compact working-set note for that paper containing only:
- current question;
- active claims;
- latest evidence;
- open objections;
- planned experiments;
- paper files;
- run locations;
- next action.

This prevents the global project context from flooding every paper session.

## Recommended future organization

As the new project grows, split it into:

```text
handoff/                 # global durable rules
papers/<paper_id>/       # paper-specific working set
experiments/<exp_id>/    # atomic contracts/manifests
reviews/                  # adversarial review artifacts
archive/                  # superseded/off-mainline snapshots
```

The goal is not to make one enormous context file. The goal is to make the right context cheaply recoverable.
