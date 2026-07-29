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

The public information architecture now contains **9 canonical pages** and **19 compatibility redirects** for historical URLs. Every canonical page uses a page-specific semantic hierarchy rather than a flat list:

```text
H1 · canonical page
└── H2 · chapter / main question
    └── H3 · method family, domain, direction cluster, or evidence block
        └── H4 · concrete research question or subsection
```

The hierarchy and recommended reading order are defined centrally in `page-architecture-data.js`. The sidebar renders a nested H2/H3/H4 tree and deliberately excludes individual bibliography cards from the table of contents.

1. `index.html` — observatory home and reading paths.
2. `foundations.html` — definitions, four-axis taxonomy, and a bilingual paper-ready history SVG (`agent-self-evolution-history-en.svg` / `agent-self-evolution-history-zh.svg`).
3. `mechanisms.html` — parameter, prompt, memory, skill/tool, and workflow evolution.
4. `domains.html` — visual/multimodal, GUI/web, and embodied/world-model agents.
5. `evaluation.html` — evaluation, safety, governance, benchmarks, environments, and repositories.
6. `research-directions.html` — four beginner-level questions, a running example, plain-language explanations of ten stable directions, and the long-term agenda.
7. `paper-ideas.html` — thirty-four concrete paper plans plus global, within-direction, and track rankings.
8. `selected-paper.html` — GroundEvo problem, experiments, roadmap, and review log.
9. `bibliography.html` — coverage protocol, interactive maps, exports, and live bibliography.

Former topic URLs such as `memory-evolution.html` and `paper-roadmap.html` remain as `noindex` compatibility pages that redirect to the matching section of a canonical hub.

## Literature corpus

The bibliography synchronizes two complementary survey-maintained catalogs in the browser:

1. `selfimproving-agent/Awesome-Self-Improving-Agents`
2. `FrontisAI/Awesome-Self-Improving-Agents`

It merges and normalizes these records with a manually verified visual/CVPR core set. The bilingual 2400×1600 history SVG prioritizes formally published conference and journal papers, groups twenty-three milestones into five method families, and states each method's core action, update target, and feedback signal; preprint-only frontier work stays in the searchable bibliography rather than the historical spine. The live interface includes:

- method × publication-year heatmap;
- publication-type × year heatmap;
- update-surface × feedback-signal matrix;
- year, method, feedback, publication status, and vision filters;
- four ranking modes: recommended reading order, current frontier/recency, historical influence/citations, and venue tier;
- default role-aware ordering: recent field overviews → direct self-evolution methods → evaluation/safety/governance → enabling mechanisms → agent foundations → foundation-model precursors → adjacent resources;
- within each role, peer-reviewed and recent work is prioritized; citation count is only a tie-breaker, while Agent/model foundations are shown chronologically;
- a dated OpenAlex citation snapshot for 21 high-priority papers, with unmatched records explicitly marked rather than treated as zero-citation papers;
- filter-preserving share links and paginated rendering;
- global full-text search;
- linked numbered references from topic pages;
- JSON, CSV, and generic BibTeX export, including recommended rank, reading role, venue tier, citation metadata, and the six analysis fields;
- a collapsible six-part analysis for every paper in the order: problem motivation, comparative advantage, core intuition, rationale, method flow, and experimental validation;
- fully paper-specific bilingual six-part analyses for 24 high-priority milestones, with conservative summary- or metadata-derived fallbacks for the long tail;
- per-record citation copying and print layout.

The site does **not** claim literal mathematical completeness. It targets comprehensive and auditable coverage under the inclusion, exclusion, source, deduplication, and publication-status protocol documented on `bibliography.html#group-coverage-method`.

## Current research direction

The broader roadmap is **GroundEvo: Causally-Grounded Multilevel Self-Evolution for Visual Agents**. The frozen first-paper scope is **GroundEvo-Admission: Visual Causal Lesson Admission**.

The first falsifiable study asks whether visual agents admit spurious lessons from successful and failed trajectories, and whether active visual re-observation plus minimal environment counterfactual replay improves persistent-memory admission, lowers harmful commits, and preserves future-task gain under matched cost.

The current hierarchy contains **10 research directions** and **34 concrete paper ideas**. For new readers, the ten directions are first grouped into four questions—what to learn, what experience should become, what is changing around the agent, and how evolution remains controlled—and then explained through one GUI-agent example and a plain-language glossary. Every idea separately states its purpose/problem, core idea, rationale, method logic, research importance, and conditional comparative advantage, followed by a minimum experiment, strongest baseline, and Go/Stop boundary. The 69-formulation audit applies three review rounds to paper ideas: literature collision and identifiability, paper-strength scoring, and module–lifecycle coverage. Eighteen formulations are merged as sub-questions or evaluation axes and seventeen are rejected. Research directions are structural categories and are not globally ranked.

Every retained idea has bilingual reasoning and comparison records that separately state: **purpose/problem**, **core idea**, **rationale**, **method logic**, **research importance**, and **conditional comparative advantage**. The card then fixes its minimum experiment, strongest comparison, Go/Stop boundary, one-line thesis, rank, confidence, and paper track.

**Tier A, ranks 1–12:** NegEvoBench-V, ScopeGuard-V, GroundEvo-Admission, AmplificationGuard-X, EvoContract-V, ViMEvo-Repair, RelianceGuard-V, CapabilityLease-Evo, EvoFirewall-V, InteractionGuard-V, PerformativeEvo-V, and ConfidenceFlow-Evo.

**Tier B, ranks 13–26:** EvoValue-V, EgoShift, OversightBudget-Evo, MultiRateEvo-V, MemoryFormRouter-V, BudgetEvolve-V, AuditInvariant-Evo, PluralLineage-Evo, SkillUnlearn-V, ExploreRepair-V, WorldPatch-V, EvoProvenance-V, SkillProof-V, and PersonaShift-V.

**Tier C, ranks 27–34:** ProcessCredit-V, EvoGC-X, MetaGuard-V, GoalGuard-Evo, SimEvo-CF, EvalRedQueen-V, UpdateRoute-V, and CrossAgentTransfer-V.

The latest lifecycle batch retains the paper ideas AmplificationGuard-X, CapabilityLease-Evo, ConfidenceFlow-Evo, and PluralLineage-Evo. PopulationImmunity-MAS, ServeStageGuard-Evo, QuarantineCommit-Evo, EvidenceExpiry-Evo, StopRule-Evo, UpdateAssurance-Evo, PermissionDrift-Evo, and RollbackOrder-Evo are merged into broader ideas. Generic runtime attestation and generic uncertainty-aware agents are rejected because direct methods already exist. The ten-direction hierarchy and long-term agenda are published on `research-directions.html`; full paper plans and rankings are on `paper-ideas.html`.

## External-agent review status

The configured CodexFlow service at `127.0.0.1:4318` and the installed Claude CLI are currently unavailable because the service or authentication is invalid. The repository therefore distinguishes completed role-separated audits—including the 2026 frontier-collision pass that froze GroundEvo-Admission—from independent external-agent consensus. See `REVIEWER_PROTOCOL.md` and `selected-paper.html#group-review-log`.

## Quality assurance

Run static site integrity checks:

```bash
python3 site_smoke_test.py
```

Run the online literature and citation audit:

```bash
python3 catalog_audit.py
```

Generate a reviewable OpenAlex citation-cache chunk when the API budget is available:

```bash
python3 build_citation_cache.py --start 0 --limit 100 --chunk-id 0
```

The script prints JavaScript to standard output and never overwrites repository files. Title/year matches must be reviewed before extending the committed snapshot.

Run the real-browser interaction test. It uses Firefox/geckodriver when available and automatically falls back to Edge/msedgedriver:

```bash
python3 browser_smoke_test.py
```

Run the deterministic page-hierarchy test. It renders each canonical page in an independent Edge process, avoiding one long browser session:

```bash
python3 hierarchy_smoke_test.py
```

The checks cover:

- 9 canonical pages and 19 compatibility redirects;
- navigation targets, merged content groups, redirect anchors, and the page-specific chapter configuration;
- all 34 bilingual Idea reasoning records and their four mandatory fields;
- JavaScript syntax and one-to-one bilingual coverage of all six Idea reasoning fields;
- sitemap, CNAME, favicon, manifest, robots, and 404 resources;
- upstream catalog counts and deduplication;
- missing URLs and unresolved topic-page citations;
- venue-tier ranking configuration, the dated citation snapshot, four ranking modes, and all 24 bilingual top-paper analyses;
- dynamic catalog loading, three bibliography maps, sorting, filters, URL state, and pagination;
- exact H2/H3/H4 and nested-TOC counts for all nine canonical pages;
- history and direction figures, merged hub rendering, linked resources, legacy redirects, and mobile navigation.

## Deployment

GitHub Pages publishes the `main` branch with the custom domain stored in `CNAME`:

```text
agent-evolution.lightrain.asia
```
