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
6. `research-directions.html` — four beginner-level questions, a running example, plain-language explanations of ten stable directions, thirty representative literature cards with one-line methods, and the long-term agenda.
7. `paper-ideas.html` — an evidence-to-idea backend map, advisor comparison board, twelve-item shortlist, complete reasoning dossiers, reviewer gates, decisive pilots, and a traceable archive of all thirty-four ideas.
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

The current hierarchy contains **10 research directions** and **34 concrete paper ideas**. For new readers, the ten directions are first grouped into four questions—what to learn, what experience should become, what is changing around the agent, and how evolution remains controlled—and then explained through one GUI-agent example, a plain-language glossary, and three representative papers per direction. Each paper record gives its venue/year, one-line method, direction fit, and a linked citation to the full six-part bibliography analysis. Every idea separately states its purpose/problem, core idea, rationale, method logic, research importance, and conditional comparative advantage, followed by a minimum experiment, strongest baseline, and Go/Stop boundary. The 69-formulation audit applies three review rounds to paper ideas: literature collision and identifiability, paper-strength scoring, and module–lifecycle coverage. Eighteen formulations are merged as sub-questions or evaluation axes and seventeen are rejected. Research directions are structural categories and are not globally ranked.

Every retained idea has bilingual reasoning and comparison records that separately state: **purpose/problem**, **core idea**, **rationale**, **method logic**, **research importance**, and **conditional comparative advantage**. It also fixes the strongest comparison, minimum experiment, decisive metric, Go/Stop boundary, paper track, and unresolved risk.

The primary selection interface is no longer the old decimal-score table. The page now combines the historical twelve-Idea advisor shortlist with a larger low-resource CVPR bank: 61 raw formulations are reduced to 42 passed candidates, one structured block, and eighteen early rejections. Every passed candidate exposes five review dimensions, a complete actor/critic/API configuration, disjoint discovery/calibration/test splits, P0/P1/P2 execution phases, matched baselines, compute and call budgets, a decisive main table, ablations, and Go/Stop rules. Legacy ranks remain visible only for decision traceability.

The latest lifecycle batch retains the paper ideas AmplificationGuard-X, CapabilityLease-Evo, ConfidenceFlow-Evo, and PluralLineage-Evo. PopulationImmunity-MAS, ServeStageGuard-Evo, QuarantineCommit-Evo, EvidenceExpiry-Evo, StopRule-Evo, UpdateAssurance-Evo, PermissionDrift-Evo, and RollbackOrder-Evo are merged into broader ideas. Generic runtime attestation and generic uncertainty-aware agents are rejected because direct methods already exist. The ten-direction hierarchy and long-term agenda are published on `research-directions.html`; the evidence-gated decision lab and complete candidate archive are on `paper-ideas.html`.

## Evidence-gated literature-to-idea backend

The deterministic backend in `research_pipeline/` normalizes the existing literature and idea assets into one auditable schema. It combines reusable mechanisms from ResearchAgent, Nova, STORM, AI-Researcher, Scideator, MOOSE-Chem, Deep-Ideation, CycleResearcher, PaperQA/OpenScholar, and AI-Scientist-style experiment search without treating any single agent output as an acceptance decision.

```text
research scope and assets
  -> five-route query planning
  -> citation / concept / full-text evidence graph
  -> structured paper facets and claim-evidence records
  -> gap and contradiction mining
  -> eight named idea-generation operators
  -> semantic deduplication and branch preservation
  -> four-way novelty collision search
  -> five independent reviewer gates
  -> bounded falsification pilot
  -> advisor shortlist / hold / stop decision
```

Provider contracts in `research_pipeline/providers.py` define swappable interfaces for query planning, literature retrieval, facet extraction, gap mining, idea synthesis, novelty checking, review, pilot planning, and final gate decisions. Semantic Scholar is now connected through the ignored server `.env`, while OpenAlex, local-PDF, embedding, and LLM providers can still be added without changing the browser-facing idea schema.

On `10.42.8.52`, the Git checkout remains under `/home/wyt/code/agent-self-evolution-observatory`, while corpora, datasets, PDFs, indexes, caches, and experiment runs are stored under `/data/wyt/agent-self-evolution-observatory` on the local 33 TB data disk. Small browser snapshots remain beside the code for deployment.

Validate storage, live literature, or the current snapshot:

```bash
python -m research_pipeline --storage-status
python -m research_pipeline --init-storage
python -m research_pipeline --s2-status
python -m research_pipeline --sync-s2
python -m research_pipeline --cvpr-status
python -m research_pipeline --build-cvpr-bank
python -m research_pipeline --published-audit-status
python -m research_pipeline --build-published-audit
python -m research_pipeline --check
python -m research_pipeline
```

The deployment snapshots under `generated/` include the evidence-gated pipeline, the 42-candidate low-resource CVPR bank, a twelve-paper published experiment-substrate audit, and a Semantic Scholar snapshot currently covering 149 deduplicated papers from sixteen planned queries. Bulk corpora and provider caches remain outside Git.

## External-agent review status

CodexFlow remains unavailable because account connection fails. Oracle Browser mode is configured to open all web-GPT reviews inside one dedicated ChatGPT project. A strict project-scoped GPT review has already produced one PASS, one REVISE-and-fix, and one BLOCK decision; these verdicts and their exact blocking reasons are stored in the idea-bank artifact instead of being treated as generic consensus.

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
- all 34 bilingual Idea reasoning records and their six mandatory argument fields;
- the eight-stage backend map, four-stage candidate funnel, eight generation operators, five reviewer gates, twelve historical advisor dossiers, the complete 34-idea archive, and interactive advisor filtering;
- 42 executable low-resource CVPR protocols, one structured block, 18 early rejections, 12 published experiment-substrate audits, and project-scoped web-GPT verdicts;
- JavaScript syntax and one-to-one bilingual coverage of all six Idea reasoning fields;
- sitemap, CNAME, favicon, manifest, robots, and 404 resources;
- upstream catalog counts and deduplication;
- missing URLs and unresolved topic-page citations;
- venue-tier ranking configuration, the dated citation snapshot, four ranking modes, and all 24 bilingual top-paper analyses;
- dynamic catalog loading, three bibliography maps, sorting, filters, URL state, and pagination;
- exact H2/H3/H4 and nested-TOC counts for all nine canonical pages;
- history and direction figures, including twenty literature citations inside the bilingual direction SVG and thirty linked evidence cards on the page;
- merged hub rendering, linked resources, legacy redirects, and mobile navigation.

## Deployment

GitHub Pages publishes the `main` branch with the custom domain stored in `CNAME`:

```text
agent-evolution.lightrain.asia
```
