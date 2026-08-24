# Agent Self-Evolution Research OS

This directory is the backend source of truth for the Agent Self-Evolution Observatory. It is no longer only a literature-to-idea pipeline: it governs the full paper-first research lifecycle from evidence and novelty formation through experiment admission, local scientific validation, method freeze, full experiments, evidence closure, and system learning.

## 1. Canonical system model

The backend exposes **one temporal lifecycle** and **six functional responsibility layers**. These are different views of the same system and must not be treated as competing workflows.

### Temporal lifecycle: when research may advance

The canonical order lives in `system_architecture.py::TEMPORAL_FLOW`:

```text
1  SCOPE                Paper target, research boundary, claim boundary
2  EVIDENCE             Literature, closest work, provenance, collision evidence
3  NOVELTY              Paper Novelty Contract
4  METHOD               Principle Certificate + Method Contract
5  EXPERIMENT BLUEPRINT Claim → experiment / baseline / ablation / local-full matrix
6  ECONOMY + COMPILE    Cheapest decisive test + Protocol/REP/Pre-Experiment admission
7  LOCAL VALIDATION     F0 → P0-Support → minimal P0-Method
8  METHOD FREEZE        Freeze method hash + experiment-blueprint hash
9  FULL EXPERIMENT      Main tables, replication, ablations, efficiency, generalization
10 PAPER EVIDENCE       Chain-of-Evidence and claim closure
11 PAPER DESIGN         Frozen Paper Contract + competing story candidates
12 MANUSCRIPT           Evidence-bound manuscript construction
13 MOCK PC              Blind-manuscript and artifact-aware internal review
14 TARGETED REPAIR      Repair decision-critical issues without silently expanding science
15 CLAIM AUDIT          Sentence/claim → frozen-evidence audit
16 PDF QA               Rendered artifact and Manuscript CI
17 PREBUTTAL            Internal stress test of decision-critical objections
18 SUBMISSION READY     Final internal readiness receipt; zero submission authority
19 SUBMITTED            External receipt-bound state; requires explicit human authority
20 REBUTTAL             External review/response state; receipt-bound
21 LEARN                Rules, tests, Failure Assets, review prechecks, Meta-Trace, public snapshot
```

Stages 1–18 are the internal research-to-paper-readiness lifecycle. Stages 19–20 are external receipt-bound states and are not autonomous Research OS actions. This repository may represent those states for provenance, but no internal readiness result grants submission authority. Stage 21 turns scientific outcomes and privacy-safe structured internal-review patterns into reusable memory.

A local pilot validates an already designed paper method. It does **not** discover the core method. If local evidence forces a core-method change, full-experiment authority is invalidated and the project returns to `NOVELTY → METHOD → EXPERIMENT BLUEPRINT`.

### Functional architecture: who owns each responsibility

The canonical layer registry lives in `system_architecture.py::FUNCTIONAL_LAYERS`:

1. **Evidence, scope, and closest work** — literature retrieval, evidence graph, provenance, collision boundary.
2. **Novelty, principle, and method formation** — idea search/lineage, human terminal state, Paper Novelty Contract, Principle Certificate, method design, AI clinic.
3. **Experiment blueprint and launch admission** — Claim→Experiment matrix, information-gain scheduling, P0 Economy, Pre-P0 identifiability, Protocol Validity, Research Execution Plan, Pre-Experiment 8/8 compiler.
4. **Scientific validation, freeze, and scale** — F0, P0-Support, P0-Method, typed failure semantics, atomic repair, method freeze, P1/full evidence.
5. **Runtime, resources, and authority** — capability routing, single-writer authority, GPU leases, raw traces, progress/heartbeat, AI trigger automation, restricted execution.
6. **Scientific memory, system learning, and publication** — Decision Ledger, Scientific Meta-Trace, Failure Assets, research-system replay, external-system learning, public snapshots, Chain-of-Evidence.

Every component published in `research-system-state.json/js` has a stable `key` and exactly one `primary_layer`. Adding or renaming a component without updating the architecture manifest is a validation error rather than a silent frontend drift.

### Cross-cutting methodology controls

Some methods govern more than one temporal stage but do not deserve a seventh functional layer. `methodology_controls.py` therefore attaches four controls to existing owner components:

1. **Exploration Frontier** (`wide-search-ideation`) — measure portfolio-level quality/diversity/novelty breadth, seed-literature distance, semantic dispersion, novelty-axis coverage, and branch entropy. Pairwise collision is not sufficient to detect portfolio collapse.
2. **Experimental Design Integrity** (`protocol-and-replay`) — preregister model/prompt/tool/split/metric/analysis/stopping choices before outcomes are visible, and audit web/tool search trajectories for benchmark metadata, question-context, or explicit-answer leakage. Outcome-contingent redesign creates a new contract rather than silently mutating the old one.
3. **Reproducibility Readiness** (`literature-evidence-integrity`) — reconstruct a dependency-aware workflow graph and require independent re-execution of load-bearing results. Claim traceability is necessary but is not by itself reproducibility.
4. **Mechanism-to-Intervention Closure** (`paper-story-and-evidence`) — after an analysis rules out simple explanations and localizes a bottleneck, explicitly decide whether that bottleneck yields a preregistrable intervention against the strongest same-information baseline. If it does, the intervention needs its own Go/Stop contract. If it does not, the paper must be framed honestly as measurement / identification / negative-boundary work and state which evaluation or engineering decision changes. Algorithmic complexity is never accepted as closure by itself.

These controls inherit authority from their owner component. Their current states are deliberately `spec-ready` / `contract-ready` until measured; the system may not claim improved exploration, contamination resistance, reproducibility, or mechanism-derived intervention quality before the corresponding evaluation is actually run. EurekAgent-style permissions/artifact/budget/HITL environment engineering is recorded as a merge into the existing Runtime & Authority layer, not duplicated as another component.

## 2. Source-of-truth modules

| Responsibility | Canonical backend |
|---|---|
| System architecture | `system_architecture.py` |
| Cross-cutting methodology controls | `methodology_controls.py` |
| Paper-first contract | `paper_design_contract.py` |
| Principle / falsification semantics | `principle_adjudication.py` |
| Experiment protocol compilation | `pre_experiment_compiler.py`, `pre_experiment_specs.py` |
| P0 Economy | `p0_economy_gate.py` |
| Scientific validation state machine | `governance_protocol.py` |
| Pilot/result registry | `pilot_registry.py` |
| Experiment diagnosis / atomic repair | `experiment_iteration.py` |
| Current experiment authority | `p0_decision_ledger.py` |
| Runtime orchestration | `experiment_orchestrator.py`, resource/authority lease modules |
| Evidence graph / collision / lineage | `evidence_graph.py`, `idea_collision.py`, `idea_lineage.py` |
| External paper bibliographic intake / official asset handoff | `paper_first_external_paper_identity.py`, `paper_first_external_asset_audit.py` |
| Scientific memory | `scientific_meta_trace.py`, `failure_asset_library.py`, `research_memory_wiki.py` |
| Paper Acceptance ledger / internal readiness | `paper_acceptance.py`, `paper_acceptance_ledger.py` |
| ResearchItem / PaperRegistry projection | `research_item_state.py` |
| Experiment value advisory | `experiment_value_scheduler.py` |
| System replay / external learning | `research_system_replay.py`, `external_system_learning.py` |
| Public system composition | `research_system.py` |

`research_system.py` composes these modules; it should not become a second implementation of their rules. Stable ordering belongs in `system_architecture.py`, experiment gates belong in `pre_experiment_specs.py`, and scientific-stage semantics belong in `governance_protocol.py`.

## 3. Paper-first scientific contract

Before implementation or local experimentation, a new research formulation must define:

### Paper Novelty Contract

- concrete paper problem and claim boundary;
- closest work with source references;
- novelty axis;
- contribution claim;
- irreducible difference from the closest work / strongest simplification;
- collision status.

### Principle + Method Contract

- primitives, assumptions, scope conditions, mechanism;
- observable predictions and genuine falsification conditions;
- method name and core mechanism;
- novelty → method mapping;
- load-bearing components;
- strongest same-information simplification;
- explicit rule for what counts as a core-method change.

### Experiment Blueprint

- Claim→Experiment matrix;
- baseline matrix;
- ablation matrix;
- local-validation scope;
- full-experiment scope;
- method/blueprint freeze rule.

Historical Pre-Experiment cards that predate this rule remain historical. They are not retroactively rewritten to look paper-first.

## 4. Experiment admission

Experiment admission is intentionally layered. Prerequisites are not silently counted as extra formal gates.

```text
Paper Design Contract
  → Principle Certificate
  → P0 Economy / cheapest decisive test
  → Protocol Validity
  → derived Research Execution Plan
  → Updater / substrate competence
  → formal Pre-Experiment Gate 1..8
  → local execution authorization
```

The formal Pre-Experiment compiler remains exactly **eight gates**. Paper Design, Principle, Protocol Validity, REP, and updater/substrate qualification are explicit prerequisites/derived contracts rather than hidden ninth/tenth gates.

No AI reviewer, value scheduler, or generated plan can override a failed machine gate or grant GPU/scientific authority.

## 5. Scientific validation and failure semantics

`governance_protocol.py` exposes a seven-stage **experiment-evidence sub-state-machine**:

```text
Problem → Substrate → F0 Identifiability → P0-Support → P0-Method → P1 Replication → Paper Experiment
```

This seven-stage state machine is nested inside the canonical 21-stage lifecycle, primarily spanning the local scientific-validation portion. It is not a second top-level workflow.

Core rules:

- `P0-Support` asks whether the necessary phenomenon/support exists; support insufficiency is not `METHOD_FAIL`.
- `P0-Method` requires frozen support evidence.
- implementation/runtime/provenance failures do not update method or principle belief.
- representation/operationalization failures repair the measurement bridge rather than falsifying the principle.
- matched-simplification equivalence weakens method novelty/headroom, not automatically the broader research problem.
- a principle is falsified only when a registered prediction is contradicted with assumptions, scope, operationalization, identifiability, optimization, independent truth, and matched baseline all intact.
- one repair child changes one load-bearing variable; repeated representation/objective rescue is budgeted.

## 6. Runtime and authority

Research logic is separated from long-running execution.

- MCP/Codex controls code and remote servers.
- Experiment Orchestrator owns server/GPU selection, per-run isolation, tmux jobs, heartbeat, budgets, checkpoints, and typed terminal state.
- Idea scientific authority and GPU UUID resource leases are separate contracts.
- raw traces are mandatory for GPU scientific runs.
- a pre-model-load audit freezes code/config/data/model/runtime identity before scientific rows may be produced.
- long jobs must persist progress incrementally and expose a resumable state.
- unrestricted autonomous code execution remains intentionally disabled.

A chat disconnect must never be part of the experiment lifecycle.

## 7. Scientific memory and publication

Three state types must remain separate:

1. **Raw execution trace** — observations, actions, choices, logs, checkpoints.
2. **Active scientific state** — current assumptions, evidence, decisions, unresolved uncertainty.
3. **Institutional memory** — reusable Failure Assets, dead ends, prior system lessons, external-system patterns.

The Decision Ledger is the single current experiment-decision view; old planned states remain provenance only. Public generation never rewrites historical experiment evidence.

Every publishable claim must close against a real artifact through Evidence Integrity / Chain-of-Evidence. Uncalibrated judges are not ground truth.

PaperRegistry also has a mandatory reader-facing **Paper Story V3** contract. It is a zero-authority explanatory projection, not a second scientific ledger. Every current PaperState must have one matching Paper Story that follows the 15-step argument chain `concrete scene → practical stake → current paradigm → concrete failure → missing scientific object → falsifiable question → design requirements → gap/component mapping → mechanism prediction → evaluation contract → main effect → mechanism-aligned stress test → component/alternative tests → generalization/failure boundary → bounded claim`. The full schema, archetype rules, required fields, manuscript outline, onboarding procedure, and authority boundary live in `PAPER_STORY_V3.md`. `scripts/validate_paper_story_contract.js` enforces a one-to-one PaperRegistry↔PaperStory mapping and fails closed when a future paper omits load-bearing reasoning fields such as the missing scientific object, mechanism prediction, strongest alternative explanation, evaluation contract, failure regime, or Chain-of-Evidence.

Paper readiness uses two deliberately different quantities. `ledger_submission_ready` records that an append-only readiness receipt was reached historically; `gate_clean_submission_ready` asks whether the latest effective internal audit is still clean. A later failed Paper Preparation receipt never disappears behind an older state label. Every PaperState also exposes one zero-authority `primary_next_action`; a fully closed internal paper receives `NO_INTERNAL_ACTION`, while a named external support blocker remains `EXTERNAL_EVIDENCE_REQUIRED`.

Every ResearchItem now exposes the same single-action control-plane shape without creating execution authority. `STOPPED → NO_INTERNAL_ACTION`, `MERGED → MERGED_NO_STANDALONE_ACTION`, `HOLD → REOPEN_CONDITION_REQUIRED`, and `PAPER_READY → PAPERSTATE_HANDOFF`. These are derived read-only instructions over canonical state; `machine_actionable_research_items` must remain zero unless a future, separately authorized execution contract changes that rule.

`ResearchDashboard.current_attention` is a **visibility queue, not an activity or execution queue**. It keeps one `PAPERSTATE_HANDOFF` and five `REOPEN_CONDITION_REQUIRED` items visible so lineage and blockers remain legible, while `machine_actionable_attention=0`. The canonical ResearchItem registry explicitly permits `active_research_items=0`; visibility never backfills a synthetic active slot. A closed object such as F-4 remains visible in history/portfolio views only through its stopped state and can never become the fallback active row. Frontends must present this split explicitly instead of describing tracked items as work that is actively advancing.

Mock-PC learning enters Research Memory only through structured aggregates such as objection category, evidence state, and action class. Reviewer prose and rationale remain private. These `REVIEW_LESSON` entries are reusable Paper Design prechecks only: they cannot update a scientific principle or authorize an experiment. Human paper-development guidance is stored separately as structured `PAPER_DEVELOPMENT_GUIDANCE`, never as raw advisor prose. The 2026-08-23 senior-review lesson explicitly separates scientific value from manuscript maturity: the current five problems remain worth pursuing and their method directions are broadly plausible, while the present manuscripts are treated as `INITIAL_DRAFT_NEEDS_DEEPENING`. The next material paper revision must explicitly revisit four dimensions—problem necessity/challenge/Related Work, method intuition/design/detail, experiment-program breadth, and plain/direct writing—and bind `ICLR-AGENT-SELF-EVOLUTION-MANUSCRIPT-V1` (`generated/iclr-agent-paper-template.json/js`, human-readable `ICLR_AGENT_PAPER_TEMPLATE.md`). The template fixes the main-body argument jobs, six-question Method component contract, E1–E6 experiment-planning lanes, archetype adapters, and answer→evidence→interpretation→boundary result prose. This paper-only development backlog cannot expand supported claims or authorize model/GPU/experiment execution. Every new durable Paper Design backlog entry compiles a content-addressed `PAPER_DESIGN` memory precheck before human review; the query pack reserves both the development guidance and a structured review lesson when available. New Story Search receipts bind the same zero-authority class of Paper Design memory context. Historical Story Search receipts remain valid and are not retroactively invalidated. `public_projection_invariants.py` cross-checks ResearchItem, PaperRegistry, ResearchSystem, ResearchDashboard, and ResearchMemory so a daily projection cannot silently change one layer without the others failing validation. Both the automation-cycle publisher and the static-site builder execute this invariant before publication; a mismatch fails closed and skips publication rather than emitting a partially updated public control plane.

## 8. Automation boundary

Automatically allowed:

- deterministic rebuilds, caching, deduplication, schema validation;
- literature/evidence snapshots;
- external-paper title↔arXiv verification; a mismatched pair is quarantined, and only a verified bibliographic receipt may trigger read-only inspection of primary-declared GitHub/Hugging Face/project endpoints;
- preflight/runtime checks and resource discovery;
- content-addressed AI consultation triggers;
- structured result ingestion after validation;
- public snapshot generation.

Conditionally automated:

- local experiment launch only after all required paper/scientific/runtime contracts pass;
- screening/qualification progression under frozen protocol;
- repair generation within explicit repair budgets.

Human scientific authority remains required for:

- research/venue/claim boundary;
- accepting a materially changed core method;
- budget escalation and new backbone/domain expansion;
- final interpretation of negative evidence at the principle level;
- final paper claims and external wording.

## 9. Storage and public artifacts

The Git checkout stores code, configs, tests, and small browser-consumable snapshots. Large corpora, caches, traces, and runs belong on the configured data disk through `StorageSettings`.

Important public artifacts include:

- `generated/research-system-state.json/js` — composed system state, architecture, health, and public summaries;
- `generated/research-governance-v2.json/js` — scientific validation governance;
- `generated/p0-decision-ledger.json/js` — current experiment decisions;
- `generated/ai-consultation-clinic.json/js` and automation summary;
- literature/idea/experiment snapshots required by the site.

Raw reviewer output, secrets, raw traces, runtime locks, resource leases, and large datasets remain backend-only.

## 10. Validation and build

From the repository root, the principal checks are:

```bash
python -m unittest \
  research_pipeline.test_system_architecture \
  research_pipeline.test_research_system \
  research_pipeline.test_pre_experiment_compiler \
  research_pipeline.test_research_learning_loop \
  research_pipeline.test_experiment_iteration

node scripts/validate_paper_story_contract.js
python site_smoke_test.py
python hierarchy_smoke_test.py
SYSTEM_OVERVIEW_ONLY=1 python browser_smoke_test.py
python paper_control_plane_browser_smoke_test.py
python scripts/build_research_timeline.py --dashboard-only  # refresh the current control plane without rewriting timeline history
python scripts/build_static_site.py
SYSTEM_OVERVIEW_ONLY=1 python idea_browser_smoke_test.py
```

Useful CLI entry points remain available through:

```bash
python -m research_pipeline --storage-status
python -m research_pipeline --research-system-status
python -m research_pipeline --build-research-system
python -m research_pipeline.automation_cycle --mode manual
python -m research_pipeline --check

# External paper intake must bind title and arXiv identity before asset inspection.
python -m research_pipeline.paper_first_external_paper_identity \
  --title "<paper title>" --ref "arXiv:<id>" \
  --output generated/external-paper-identity.json
python -m research_pipeline.paper_first_external_asset_audit \
  --identity-receipt generated/external-paper-identity.json \
  --output generated/external-paper-asset-audit.json
```

The second command is fail-closed: it performs no asset-network probe unless the identity receipt is `VERIFIED_BIBLIOGRAPHIC_IDENTITY`. Bibliographic verification grants only read-only asset-audit progression; it never grants Method, Experiment, P0, GPU, or scientific authority.

A release is complete only when backend tests, state validation, static-site build, real-browser smoke, deployment, and live-site verification all agree on the same architecture and scientific state.
