# Agent Self-Evolution Observatory

A bilingual, CVPR-oriented research observatory for self-evolving agents.

- Website: <https://agent-evolution.lightrain.asia>
- Repository: <https://github.com/lightrain-a/agent-self-evolution-observatory>

## Information architecture

The site follows the same research-observatory framework as the LLM Distillation Lineage Observatory:

- grouped sticky sidebar navigation;
- global literature search;
- automatic per-page table of contents;
- persistent English/Chinese switching;
- responsive mobile navigation;
- linked numbered references;
- a separate next-paper workspace;
- explicit QA and coverage protocols.

The current site contains 23 main pages.

### Foundations

- Definitions and history
- Four-axis knowledge map and taxonomy

### Evolution mechanisms

- Foundation-model parameter improvement
- Prompt and context evolution
- Memory evolution
- Tool and skill evolution
- Workflow and architecture evolution

### Visual and interactive agents

- Visual and multimodal agents
- GUI and web agents
- Embodied agents and world models

### Evaluation and reliability

- Evaluation, safety, governance, and rollback
- Datasets, environments, and longitudinal benchmarks
- Coverage and search protocol

### Resources

- Repositories and reproducible systems
- Live bibliography
- Long-term research agenda

### Research structure

- Ten stable research directions with explicit scientific boundaries
- A bilingual 1920×1080 direction map covering all thirty-four retained paper ideas
- A high-density bilingual historical overview with six phases, thirty capability cells, ten direction-formation rows, twenty-three published milestones, paradigm shifts, enabling factors, and open problems
- Field taxonomy and mechanism pages kept separate from paper selection

### Paper idea portfolio

- Thirty-four concrete paper ideas retained from a 69-formulation lifecycle audit
- Every idea includes a thesis, minimum experiment, strongest baseline, and Go/Stop boundary
- Global, within-direction, and four track-specific rankings
- Seventeen rejected formulations and eighteen merged sub-questions with collision reasons

### Selected paper workspace

- Problem formulation, benchmark and staged experiments
- Thesis, contribution ladder, roadmap, review status, and unresolved objections

## Literature corpus

The bibliography synchronizes two complementary survey-maintained catalogs in the browser:

1. `selfimproving-agent/Awesome-Self-Improving-Agents`
2. `FrontisAI/Awesome-Self-Improving-Agents`

It merges and normalizes these records with a manually verified visual/CVPR core set. The historical figure additionally prioritizes formally published conference and journal papers, while preprint-only frontier work stays in the searchable bibliography rather than the historical spine. The live interface includes:

- method × publication-year heatmap;
- publication-type × year heatmap;
- update-surface × feedback-signal matrix;
- year, method, feedback, publication status, and vision filters;
- filter-preserving share links and paginated rendering;
- global full-text search;
- linked numbered references from topic pages;
- JSON, CSV, and generic BibTeX export;
- per-record citation copying and print layout.

The site does **not** claim literal mathematical completeness. It targets comprehensive and auditable coverage under the inclusion, exclusion, source, deduplication, and publication-status protocol documented on `coverage-method.html`.

## Current research direction

The broader roadmap is **GroundEvo: Causally-Grounded Multilevel Self-Evolution for Visual Agents**. The frozen first-paper scope is **GroundEvo-Admission: Visual Causal Lesson Admission**.

The first falsifiable study asks whether visual agents admit spurious lessons from successful and failed trajectories, and whether active visual re-observation plus minimal environment counterfactual replay improves persistent-memory admission, lowers harmful commits, and preserves future-task gain under matched cost.

The current hierarchy contains **10 research directions** and **34 concrete paper ideas**. The 69-formulation audit applies three review rounds to paper ideas: literature collision and identifiability, paper-strength scoring, and module–lifecycle coverage. Eighteen formulations are merged as sub-questions or evaluation axes and seventeen are rejected. Research directions are structural categories and are not globally ranked.

**Tier A, ranks 1–12:** NegEvoBench-V, ScopeGuard-V, GroundEvo-Admission, AmplificationGuard-X, EvoContract-V, ViMEvo-Repair, RelianceGuard-V, CapabilityLease-Evo, EvoFirewall-V, InteractionGuard-V, PerformativeEvo-V, and ConfidenceFlow-Evo.

**Tier B, ranks 13–26:** EvoValue-V, EgoShift, OversightBudget-Evo, MultiRateEvo-V, MemoryFormRouter-V, BudgetEvolve-V, AuditInvariant-Evo, PluralLineage-Evo, SkillUnlearn-V, ExploreRepair-V, WorldPatch-V, EvoProvenance-V, SkillProof-V, and PersonaShift-V.

**Tier C, ranks 27–34:** ProcessCredit-V, EvoGC-X, MetaGuard-V, GoalGuard-Evo, SimEvo-CF, EvalRedQueen-V, UpdateRoute-V, and CrossAgentTransfer-V.

The latest lifecycle batch retains the paper ideas AmplificationGuard-X, CapabilityLease-Evo, ConfidenceFlow-Evo, and PluralLineage-Evo. PopulationImmunity-MAS, ServeStageGuard-Evo, QuarantineCommit-Evo, EvidenceExpiry-Evo, StopRule-Evo, UpdateAssurance-Evo, PermissionDrift-Evo, and RollbackOrder-Evo are merged into broader ideas. Generic runtime attestation and generic uncertainty-aware agents are rejected because direct methods already exist. The ten-direction hierarchy is published on `research-directions.html`; full paper plans are on `paper-ideas.html`; rankings are on `direction-board.html`.

## External-agent review status

The configured CodexFlow service at `127.0.0.1:4318` and the installed Claude CLI are currently unavailable because the service or authentication is invalid. The repository therefore distinguishes completed role-separated audits—including the 2026 frontier-collision pass that froze GroundEvo-Admission—from independent external-agent consensus. See `REVIEWER_PROTOCOL.md` and `review-log.html`.

## Quality assurance

Run static site integrity checks:

```bash
python3 site_smoke_test.py
```

Run the online literature and citation audit:

```bash
python3 catalog_audit.py
```

Run the real-browser interaction test when Firefox and geckodriver are available:

```bash
python3 browser_smoke_test.py
```

The checks cover:

- all 23 main HTML pages;
- navigation targets and content configurations;
- JavaScript syntax;
- sitemap, CNAME, favicon, manifest, robots, and 404 resources;
- upstream catalog counts and deduplication;
- missing URLs and unresolved topic-page citations;
- dynamic catalog loading, three bibliography maps, filters, URL state, and pagination;
- knowledge-map rendering, linked resource pages, and mobile navigation.

## Deployment

GitHub Pages publishes the `main` branch with the custom domain stored in `CNAME`:

```text
agent-evolution.lightrain.asia
```
