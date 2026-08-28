# Project Handoff — START HERE

Date: 2026-08-28
Purpose: canonical migration entry point for moving the research program into a new ChatGPT Project or a new human/agent working context.
Base revision when this handoff was created: `610b9fe2da9f71f42fdd355bc786095000f91502` (`origin/main` at handoff creation).

## 0. What this package is

This package is a durable **research handoff**, not a frozen transcript and not a replacement for live machine state.

It preserves:
- durable scientific questions and paper identities;
- experiment and evidence rules;
- infrastructure/worktree/run-recording conventions;
- failure modes and repair strategies learned across iterations;
- writing/review discipline;
- the procedure a new agent must use to recover the actual latest state.

It deliberately does **not** preserve secrets, access tokens, passwords, personal email addresses, transient PIDs, or unverified/stale server endpoints.

## 1. Source-of-truth order

When sources disagree, use this trust order:

1. **Exact current Git revision + content-addressed experiment/evidence artifacts**.
2. **Machine-readable canonical state in `generated/`, after checking `generated_at`, source revision, and whether newer dated artifacts exist.**
3. Versioned paper/experiment manifests and claim ledgers.
4. This handoff package for durable interpretation, rules, and navigation.
5. Obsidian notes / human summaries.
6. Chat transcripts and model memory.

Never let a chat summary override a newer canonical artifact.

## 2. Mandatory startup procedure in a new project

Before changing science, code, experiments, or manuscript claims:

1. Read this file.
2. Read `CURRENT_STATE_RECOVERY.md` and recover the true latest Git revision and latest relevant evidence.
3. Read `RESEARCH_PORTFOLIO.md` for the stable identity of each research track.
4. Read `SCIENTIFIC_OPERATING_SYSTEM.md` before authorizing any new experiment.
5. Read `FAILURE_AND_REPAIR_PLAYBOOK.md` before changing a failed design, threshold, baseline, substrate, or claim.
6. Read `INFRA_AND_EXECUTION.md` before touching a server or starting a long run.
7. Read `WRITING_AND_REVIEW.md` before editing a paper or interpreting reviewer feedback.
8. State explicitly which paper/track is being worked on, the recovered canonical revision, the current scientific gate, the strongest unresolved objection, and the next falsifiable action.

## 3. Core research philosophy

The program is not trying to produce papers by accumulating metrics. The target scientific chain is:

> scientific object → mechanism model → falsifiable prediction/regime boundary → controlled intervention → evidence-backed engineering or scientific decision

A valid negative result, HOLD, or narrowed claim is preferable to an unsupported positive result.

The recurrent anti-pattern is **experimental momentum replacing the research question**. Every new run must answer a named scientific uncertainty and must have a pre-declared interpretation for both success and failure.

## 4. Stable research families

The project contains several partially independent research families. Their exact current execution status must be recovered rather than assumed from old conversations.

- **E1 / STRI** — representation/taxonomy sensitivity and invariance in skill/self-evolution systems; recent work emphasizes using a broad, defensible public substrate rather than making the paper depend on a niche method.
- **E2 / Temporal Skill** — temporal/order-sensitive skill conversion/evolution; requires public benchmark/baseline alignment, pilot-before-full execution, and runtime artifact persistence.
- **C1 / Proxy Reward / Memory Write** — separates direct feedback/reward effects from memory-mediated amplification; no-memory controls and heterogeneity checks are central to causal interpretation.
- **B1 / Failure Memory** — failure/resample/memory effects; the story should be confirmed on an independently motivated substrate instead of loosening a gate to preserve an old result.
- **C06 / Controlled Intervention** — stagewise/counterfactual interventions used to distinguish mechanism from metric/evaluation artifacts.
- **R9 / PORT-010 / embodied-agent safety line** — strict separation between artifact existence and execution/scientific authority; behavioral per-case evidence and replay authority matter more than receipts or metadata.
- **Research-system / idea-search control plane** — the meta-system that manages problem search, evidence, paper state, gates, provenance, and explicit scientific stopping states.

See `RESEARCH_PORTFOLIO.md` for durable details and scope boundaries.

## 5. What must never be inferred from this file

Do not infer that:
- an experiment is currently authorized;
- a paper is currently submission-ready;
- a server address is still valid;
- a dated state snapshot is the newest state;
- a receipt marked PASS proves a scientific claim;
- a previous reviewer score or model consultation is scientific authority;
- an experiment that ran successfully is relevant to the current paper question.

Recover those facts from current canonical evidence.

## 6. Migration storage model

Recommended three-layer model:

### Layer A — Git canonical handoff
This directory is the durable and versioned source of truth for cross-project transfer. Changes should be reviewed and committed like code.

### Layer B — ChatGPT Project files
Upload a copy of this handoff directory (at minimum `START_HERE.md`, `CURRENT_STATE_RECOVERY.md`, `RESEARCH_PORTFOLIO.md`, and `SCIENTIFIC_OPERATING_SYSTEM.md`) to the new ChatGPT Project. Project chat context is a convenience layer, not canonical authority.

### Layer C — Obsidian human navigation
Maintain a short human-facing index that links to these Git files and records high-level lessons. Do not manually duplicate live experiment state into Obsidian unless it is clearly labeled as a snapshot with revision/date.

## 7. Security and privacy rule

This handoff must remain credential-free. Store only server aliases, repository paths, directory conventions, and validation procedures. Credentials belong in the user's existing secure SSH/key/secret-management mechanism, never in a migration document.

## 8. Next file

Read: `CURRENT_STATE_RECOVERY.md`.
