# Changelog

## 2026-07-29 · Page-specific multilevel information architecture

- Added `page-architecture-data.js` as the single bilingual chapter model for all nine canonical pages.
- Replaced flat merged-page headings with a semantic hierarchy: H1 page → H2 chapter/main question → H3 method family or domain → H4 concrete research question.
- Reorganized `mechanisms.html` into model-internal adaptation, externalized experience/capability, and system-level self-design, while preserving all original method sections and historical anchors.
- Added page-specific chapter flows to Foundations, Domains, Evaluation, Research Directions, Paper Ideas, Selected Paper, Bibliography, and the Home page.
- Grouped the ten research directions and thirty-four paper ideas beneath the same four lifecycle questions instead of presenting them as unrelated parallel labels.
- Rebuilt the sidebar table of contents as a nested H2/H3/H4 tree and excluded individual bibliography cards from TOC generation.
- Added `hierarchy_smoke_test.py`, which renders each canonical page in an independent Edge process and verifies exact chapter and TOC-depth counts.
- Extended static QA to require the architecture configuration and all canonical pages to load it while preserving nineteen compatibility redirect anchors.

## 2026-07-29 · Venue/citation literature ranking and curated top-paper analyses

- Added a total ordering for the full bibliography: flagship peer-reviewed venues first, then other peer-reviewed publications, arXiv/preprints, and other records.
- Added four switchable ranking modes: research priority, citation count, venue tier, and recency; non-default sort state is preserved in shareable URLs.
- Added `citation-ranking-data.js` with a dated OpenAlex snapshot for twenty-one high-priority papers, including an exact DOI match for BERT. Unmatched papers remain explicitly pending and are never treated as zero-citation papers.
- Added venue-tier badges, citation badges, priority ranks, citation source/match metadata, coverage reporting, and citation-aware JSON/CSV exports.
- Added `top-paper-analysis-data.js` with paper-specific bilingual analyses for twenty-four milestone papers in the required order: problem motivation → comparative advantage → core intuition → rationale → method flow → experimental validation.
- Reordered every bibliography card to use the same six-part reading sequence; the first twelve curated priority papers open automatically, while long-tail records retain visibly labeled conservative fallbacks.
- Added `build_citation_cache.py` for reviewable, chunked OpenAlex snapshot generation without overwriting repository files.
- Extended static and Edge tests for venue patterns, citation snapshot coverage, ranking order, sort switching, all twenty-four bilingual analyses, export fields, and the first eighty ranked paper cards.

## 2026-07-29 · Six-part analysis for every paper

- Added a collapsible six-part reading structure to every bibliography card: purpose/problem, core idea, rationale, method logic, importance, and conditional comparative advantage.
- Added `paper-analysis-data.js` with paper-specific method notes for key published milestones.
- Added conservative summary-derived and metadata-derived fallbacks for the synchronized long tail, with an explicit warning to consult the original paper before citing method details.
- Extended global search plus JSON and CSV exports to include the six structured analysis fields and the analysis basis.
- Added an analysis-reading guide to the bibliography, static checks for method-note coverage and renderer fields, and real-browser checks for all six fields on the first eighty papers plus a directly opened VisPlay record.
- Initialized the curated catalog before first paint and changed the browser test to wait for the actual live-catalog condition rather than a fixed delay.

## 2026-07-29 · Paper-ready history SVG and beginner direction guide

- Replaced the page-native historical overview with bilingual standalone SVG files: `agent-self-evolution-history-en.svg` and `agent-self-evolution-history-zh.svg`.
- Preserved six historical phases, capability growth, ten direction families, and paradigm shifts in a 2400×1600 vector layout suitable for direct paper embedding.
- Reorganized the twenty-three formally published milestones into five method-family swimlanes and added a concise method action, update target, and feedback signal to every milestone card.
- Added `direction-guide-data.js`, which groups the ten directions under four beginner questions: what to learn, what experience should become, what is changing around the agent, and how evolution remains controlled.
- Added a running GUI-agent example, plain-language definitions, research objects, typical cases, neighboring-direction boundaries, and a glossary for memory, skills, workflows, world models, provenance, meta-control, and lineage.
- Added visible standalone-SVG links plus static XML, milestone-count, bilingual direction-guide, and real-browser rendering checks.

## 2026-07-29 · Importance and comparative advantage for every Idea

- Added `idea-comparisons.js` with bilingual research-importance and comparative-advantage records for all thirty-four paper ideas.
- Required every Idea to explain why the problem matters for trustworthy self-evolution and under what conditions the design is better suited than the strongest existing alternatives.
- Kept comparative advantages explicitly conditional and testable rather than claiming empirical superiority before the minimum pilot.
- Extended Idea cards, global search, static one-to-one coverage checks, and real-browser tests for the two new fields.

## 2026-07-28 · Complete reasoning schema for all paper ideas

- Added `idea-explanations.js` with bilingual reasoning records for all thirty-four retained paper ideas.
- Required every idea to answer four distinct questions: purpose/problem, core idea, why the idea is reasonable, and method logic.
- Reorganized each Idea card into a research-argument layer and a separate validation layer containing the minimum experiment, strongest comparison, Go/Stop boundary, one-line thesis, rank, confidence, and paper track.
- Extended Idea search to cover the new reasoning fields.
- Added static checks for one-to-one explanation coverage and non-empty English/Chinese fields, plus real-browser checks for all thirty-four rendered reasoning blocks.

## 2026-07-28 · Nine-page information architecture consolidation

- Consolidated twenty-three public content entries into nine canonical high-density pages: home, foundations, mechanisms, domains, evaluation, directions, ideas, selected paper, and bibliography.
- Merged definitions/history with taxonomy; five mechanism pages into one mechanism atlas; three application-domain pages into one domain hub; evaluation, benchmarks, environments, and repositories into one evidence/infrastructure hub.
- Merged the direction map with the long-term agenda, the idea portfolio with all rankings, the four GroundEvo workspace pages into one selected-paper page, and the coverage protocol with the live bibliography.
- Preserved nineteen historical URLs as `noindex` compatibility redirects to precise canonical section anchors.
- Reduced the primary navigation to nine entries and rebuilt the sitemap around canonical pages only.
- Added merged-page rendering, section-group quick navigation, dynamic benchmark/repository panels inside the evaluation hub, and canonical-page search routing.
- Extended static QA to validate nine canonical pages, nineteen redirects, group coverage, sitemap scope, and redirect targets.
- Added Edge WebDriver fallback to the browser smoke test and verified merged content, 661-paper loading, filtering, pagination, bilingual figures, all 34 ideas, redirects, and mobile navigation.

## 2026-07-28 · High-density historical overview figure

- Replaced the short four-row history summary with a high-density, bilingual, page-native historical figure on `foundations.html`.
- Added six historical phases, a five-by-six capability maturity matrix, formation timelines for ten research directions, a five-level historical claim ladder, seven paradigm shifts, six enabling factors, and eight open problems.
- Added twenty-three formally published milestone papers spanning NeurIPS 2017 through CVPR 2026; preprint-only frontier work remains outside the historical spine.
- Added `history-figure-data.js` as the single bilingual data source for the figure, keeping milestones, stage descriptions, and direction formation auditable.
- Added curated bibliography records for Transformer, BERT, GPT-3, chain-of-thought prompting, STaR, ReAct, Self-Instruct, Toolformer, Reflexion, Self-Refine, OPRO, Retroformer, and Voyager.
- Added offline Edge rendering checks confirming 6 stages, 30 capability cells, 10 directions, 23 milestones, 5 claim levels, and zero unresolved citations.
- Extended static QA so missing history stages, directions, milestones, bibliography records, or renderer components fail the site audit.

## 2026-07-28 · Direction/Idea hierarchy reconstruction

- Replaced the incorrect flat “34 directions” model with a four-level hierarchy: field → research direction → concrete paper idea → selected-paper workspace.
- Defined ten stable research directions and mapped all thirty-four retained paper ideas to exactly one direction.
- Added `research-directions.html` as the canonical direction map; converted `paper-ideas.html` into a concrete paper-plan portfolio and `direction-board.html` into an Idea-only ranking board.
- Added bilingual 1920×1080 overview figures that switch with page language and contain all ten directions and all thirty-four ideas.
- Centralized direction and idea metadata in `portfolio-data.js`, including thesis, minimum experiment, strongest baseline, Go/Stop boundary, global rank, confidence, and paper track.
- Added global, within-direction, and track-specific Idea rankings without ranking research directions themselves.
- Extended global search to return research directions, paper ideas, and literature separately.
- Added automated checks for ten unique directions, thirty-four unique ranks, one-to-one Idea-to-direction mapping, and complete bilingual figure coverage.

## 2026-07-28 · Lifecycle-wide 34-idea iteration

- Expanded the formulation pool from 55 to 69 and audited every proposal across five agent modules and five lifecycle stages.
- Generated fourteen new lifecycle-oriented formulations; retained AmplificationGuard-X, CapabilityLease-Evo, ConfidenceFlow-Evo, and PluralLineage-Evo.
- Merged PopulationImmunity-MAS, ServeStageGuard-Evo, QuarantineCommit-Evo, EvidenceExpiry-Evo, StopRule-Evo, UpdateAssurance-Evo, PermissionDrift-Evo, and RollbackOrder-Evo into broader directions.
- Rejected generic runtime attestation and generic uncertainty-aware agents because direct capability-governance and trajectory-uncertainty methods already exist.
- Folded DeleteCascade-Evo into EvoProvenance-V and DiversityGuard-MAS into PluralLineage-Evo / CrossAgentTransfer-V, producing 34 standalone directions, 18 merged sub-directions, and 17 rejected formulations.
- Re-ranked all directions with collision margin and pilot readiness, added High/Medium/Low rank-confidence labels, and changed tiers to A ranks 1–12, B ranks 13–26, and C ranks 27–34.
- Added separate Visual/CVPR, Systems/Security, Benchmark/Analysis, and Long-horizon Learning rankings instead of relying only on one heterogeneous global rank.
- Added literature on lineage-persistent attack amplification, capability-permission separation, pre-action authorization, dynamic capability binding, trajectory uncertainty, evidence provenance, and active video observation.
- Added module–lifecycle safety evaluation, lineage amplification factor, permission drift rate, confidence retention, lineage portfolio regret, and recovery-completeness metrics.
- Updated the research agenda, candidate-idea summary, review log, README, bibliography, and citation map for the third-round audit.

## 2026-07-28 · 32-idea expansion and full re-ranking

- Generated a new batch of 16 formulations after the first 24-direction audit.
- Retained eight standalone directions: ScopeGuard-V, InteractionGuard-V, PerformativeEvo-V, AuditInvariant-Evo, OversightBudget-Evo, GoalGuard-Evo, EvoGC-X, and DeleteCascade-Evo.
- Merged BranchMerge-Evo, ShadowEvo, TrustDecay-Evo, FederatedEvo, ParetoGuard-Evo, ModelSwap-Evo, and EvalDebt into broader existing directions; rejected CapabilityPhase-Evo as currently unidentifiable.
- Expanded the audit to 55 formulations: 32 standalone directions, eight merged sub-directions, and fifteen rejected formulations.
- Re-ranked every retained direction with a frozen composite score: novelty 25%, main-table identifiability 25%, visual/venue fit 15%, feasibility 15%, failure value 10%, and resource efficiency 10%.
- Reorganized the Friday Board into Tier A ranks 1–10, Tier B ranks 11–23, and Tier C ranks 24–32, with a unique rank and Go/Stop boundary for every direction.
- Added recent literature on concurrent agent updates, human oversight capacity, monitoring awareness, goal evolution, self-evolving software agents, and endogenous/performative distribution shift.
- Updated the long-term agenda and review log to record the two-round portfolio audit and evidence-only re-ranking rule.

## 2026-07-28 · Observatory parity and corpus expansion

- Added datasets, environments, and benchmarks page.
- Added repositories and reproducible systems page.
- Added long-term research agenda page.
- Expanded the curated core with recent visual, multimodal, memory, skill, harness, and longitudinal-evaluation work.
- Added linked numbered references to topic pages.
- Added method × publication-year heatmap.
- Added publication-type × year heatmap.
- Added update-surface × feedback-signal matrix.
- Added year, publication status, feedback, and vision/multimodal filters.
- Added filter-preserving share links, reset controls, print layout, and 80-record pagination.
- Added JSON, CSV, and generic BibTeX export.
- Added per-record citation copy and stable bibliography anchors.
- Added an original overview knowledge-map SVG and live update-surface distribution on the home page.
- Added favicon, manifest, robots, sitemap, canonical URLs, Open Graph/Twitter metadata, structured data, and custom 404 page.
- Added online catalog and citation audit script plus headless Firefox browser QA.
- Added dynamic repository and benchmark/environment indexes extracted from the full corpus.
- Added a 2026 frontier-collision review against counterfactual trace auditing, skill–tool co-evolution, memory skills, longitudinal evaluation, calibration-free VLA, memory benchmarks, and environment co-evolution.
- Expanded the direction audit from 34 to 39 formulations, removed 14 generic or directly collided formulations, retained 24 standalone ideas, and folded EvoDebt into NegEvoBench-V as a longitudinal benchmark axis.
- Expanded the Friday Direction Board to three tiers with unified novelty, CVPR fit, feasibility, compute, minimum-demo, Go, and Stop comparisons.
- Added the new retained directions RelianceGuard-V, MemoryFormRouter-V, SkillUnlearn-V, BudgetEvolve-V, WorldPatch-V, ExploreRepair-V, EvalRedQueen-V, EvoProvenance-V, ProcessCredit-V, CrossAgentTransfer-V, PersonaShift-V, DiversityGuard-MAS, EvoContract-V, EvoFirewall-V, MetaGuard-V, and MultiRateEvo-V.
- Added six July-frontier references covering self-evolution meta-skills, memory–skill co-evolution, evolvable harnesses, compositional and sleeper memory poisoning, and selective forgetting.
- Added mechanism-level coverage for activation-time memory defense, semantic compatibility contracts, evolution-controller drift, multi-timescale consolidation, and delayed evolution debt.
- Added an explicit rejected-formulation table covering generic visual self-play, critic correction, multimodal memory, personalization, macro-tools, dynamic GraphRAG, world models, evaluator co-evolution, pairwise gates, decentralized memory, protocols, environment co-evolution, process rewards, and release engineering.
- Froze the first-paper scope as **GroundEvo-Admission: Visual Causal Lesson Admission**; multilevel update routing remains a later roadmap.
- Upgraded site smoke tests from 19 to 23 main pages and from global script loading to page-specific dependency checks.

## 2026-07-27 · Multi-page research observatory

- Replaced the initial single-page site with the same multi-page framework used by the Distillation Lineage Observatory.
- Added grouped sidebar navigation, global search, automatic page TOC, bilingual state, and mobile navigation.
- Added mechanism pages for model, prompt, memory, tool/skill, workflow, visual, GUI/web, embodied, and evaluation research.
- Added the GroundEvo paper workspace, experiment plan, roadmap, and review log.
- Added live synchronization from two survey-maintained literature catalogs.

## 2026-07-27 · Initial deployment

- Created the repository and deployed GitHub Pages.
- Configured `agent-evolution.lightrain.asia` and HTTPS.
