# Changelog

## 2026-08-07 · Solution-first idea discovery and evidence-graph explorer

- Added an interactive Idea-centered citation/evidence graph backed by the real 555-node / 943-edge research graph, with selectable local neighborhoods, relation-aware edges, source links, and bilingual node details.
- Made backend component names and evidence bilingual at the generated-state layer; added persistent Chinese required-action localization and required bilingual fields for future external reviews.
- Audited official GitHub idea-generation mechanisms from ResearchAgent, MOOSE-Chem, SciAgents, OmniScientist, AI-Scientist-v2, RD-Agent, and SciPIP, then added six solution-invention operators to the existing eight problem operators.
- Added a nine-stage solution-first workflow, multi-branch method trees, Reviewer-vector repair, public-resource grounding, experiment-feedback induction, and five mechanism-irreducibility gates.
- Generated 14 v3 method children; independent R2 returned 0 PASS, 6 REVISE, and 4 BLOCK. Continued only the six REVISE children into v3.1; independent R2 returned 0 PASS, 2 REVISE, and 4 BLOCK.
- Preserved Restoration-Clause Learning and Conformal Effect-Transport Gate as theory/identifiability repair directions; stopped generic predictor, contextual-bandit, offline-RL, diagnostic-controller, and rule-induction recombinations.
- Added persistent v3/v3.1 artifacts, complete bilingual review records, CLI/automation/publication integration, frontend decision panels, and dedicated unit/static/real-browser assertions.

## 2026-08-06 · Technical research-system and idea overview

- Reworked `system-overview.html` from an advisor-facing brief into technical documentation of the live backend and decision state.
- Added seven backend layers, ten input/process/output stages, ten stage data contracts, eight persistent-artifact classes, and explicit frontend-versus-backend visibility.
- Expanded literature ingestion, normalization, paper-field extraction, evidence graph, idea synthesis, R1 review, mechanism collision, R2 external review, and P0/P1/P2 feedback paths.
- Replaced the short automation note with complete bilingual cards for automatic execution, conditional automation, and human-controlled decisions, including failure recovery and static frontend publication.
- Fixed the component table to read the actual `component`, `source`, `status`, and `evidence` fields from the generated system state.
- Removed the advisor-message and advisor-question copy while preserving direct links to the main and supplementary Idea banks.
- Extended static and real-browser tests to require seven layers, ten stages/contracts, eight artifacts, three automation-boundary categories, fourteen boundary rules, seven backend components, and complete non-overflowing Chinese rendering.

## 2026-08-06 · Internet-inspired candidate expansion and self-screening

- Translated six user-provided “machine school” metaphors into precise research variables: cross-form capability gaps, longitudinal regression exams, version-differential blame, retry dependence, model-swap compatibility, and version-conditioned privilege control.
- Generated 24 raw candidates and completed internal screening: 11 PASS, 7 REVISE/MERGE, and 6 direct-collision REJECT.
- Reviewed all 11 internal passes through Code Oracle and the signed-in Agent-project ChatGPT in three resumable batches; the strict external distribution is 1 PASS, 7 REVISE, and 3 BLOCK.
- Identified Regression-Probe Half-Life as the sole `pilot-now` direction and created an eight-item teacher-discussion shortlist containing one direct PASS and seven explicitly repair-first alternatives.
- Added persistent inspired-bank and external-review artifacts, retry-safe external review tooling, CLI commands, weekly automation rebuild/publication, and a separate website decision panel.
- Added internal/external rank separation, final statuses, full review evidence, strongest baselines, decisive pilots, and Stop rules for every retained idea.
- Extended unit, static, publication, and real-browser tests to verify all 24 candidates, 11 external reports, the 1/7/3 verdict distribution, and the teacher shortlist.

## 2026-08-06 · Complete Oracle review of all ICLR first-round passes

- Restored access to the authoritative `admin01-NF5468M5` execution host and verified the exact Agent-project ChatGPT route with an Oracle browser smoke test.
- Completed official-source, mechanism-level external reviews for all 26 first-round-passed ICLR ideas through four resumable five-idea batches plus the previously stored review.
- Recorded the strict verdict distribution: 4 PASS, 10 REVISE, and 12 BLOCK, with zero pending ideas and zero failed final batches.
- Added per-batch retries for transient ChatGPT errors, atomic persistence, unique attempt sessions, and resumable continuation without rerunning completed ideas.
- Reordered the ICLR bank by R2 verdict while retaining the original R1 rank and frozen programmatic priority for traceability.
- Added explicit external verdict fields, confidence, verdict counts, colored cards, R2 badges, and complete review-log reporting.
- Preserved the four PASS directions as experiment-pending rather than selected-ready because no P0/P1/P2 results have been ingested.

## 2026-08-01 · All-pass Oracle and Agent-project review queue

- Identified the authoritative ICLR first-round portfolio as 26 seven-dimension passes, with one existing Agent-project web-GPT review and twenty-five pending independent reviews.
- Added `research_pipeline/iclr_external_review.py` to batch every pending idea through Code Oracle and the signed-in ChatGPT Agent project using one strict official-source ICLR review contract.
- Added atomic JSON parsing, per-batch persistence, resumable reviewed/pending accounting, host enforcement, and automatic ICLR-bank rebuilding after each successful batch.
- Moved external reviews into `generated/iclr-external-reviews.json` so daily generated-bank refreshes cannot erase expensive reviewer results or silently treat missing reviews as passes.
- Added website progress reporting and a current review-log chapter that distinguishes programmatic first-round passes, independent external review, consensus reconciliation, and P0/P1/P2 evidence.
- Attempted a real batch run on the current worker; it correctly stopped at the host guard because the authenticated Oracle/Chrome session is restricted to `admin01-NF5468M5`. The published truth therefore remains 1 reviewed and 25 pending.
- Added unit, static, and real-browser assertions for batch preparation, JSON validation, persistence, and reviewed-versus-pending counts.

## 2026-07-30 · Continuous self-calibrating research system

- Added a running evidence graph connecting 281 papers, planned queries, claims, mechanisms, tracks, datasets, models, and 29 structured ICLR candidates.
- Added a hybrid problem/mechanism/experiment collision engine that evaluates all 406 candidate pairs and exposes duplicate, near-duplicate, shared-problem, shared-mechanism, and merge-candidate relations.
- Added non-destructive Idea lineage with track roots, generation operators, programmatic reviews, project-scoped web-GPT reviews, blocked branches, and early-rejection provenance.
- Added a P0/P1/P2 pilot registry with a validated result schema and automatic planned/revise/pilot-ready/selected-ready/stop state transitions.
- Added a blocker-to-operator repair queue and optional bounded project-web-GPT repair reviews; no reviewer or provider can self-approve a candidate.
- Added fail-safe daily and weekly automation cycles, systemd timers, exclusive locks, `/data` run reports, conservative literature retry limits, and previous-snapshot preservation on partial failure.
- Added repository-scoped Ed25519 deploy-key publication with pinned GitHub host fingerprint, normalized-content hashing, pending-push recovery, bounded Git timeouts, and deferred retry on transient network failure.
- Added an online automation dashboard showing component status, evidence coverage, collision pairs, repair queue, and pilot-result feedback.
- Intentionally kept unrestricted autonomous code execution disabled; controlled experiment results can still flow back automatically.

## 2026-07-30 · ICLR-first automatic research pipeline

- Changed the primary venue from CVPR to ICLR and kept the existing visual bank as a folded CVPR follow-up archive.
- Rebuilt `research_scope.json` around continual self-improvement, constrained updates, causal credit, memory consolidation, self-correction, curricula, workflows, evaluator evolution, and world models; the refreshed Semantic Scholar snapshot contains 281 deduplicated papers from 26 planned queries with no provider errors.
- Added `iclr_idea_factory.py`: 41 raw formulations become 29 structured candidates, 26 seven-review passes, three structured blocks, and twelve early rejections across eight mechanism tracks.
- Added `iclr_experiment_audit.py` with twelve published ICLR baselines covering Retroformer, OPRO, evolutionary prompt optimization, continual embodied learning, AFlow, WebRL, SCoRe, self-evolved rewards, WorfBench, world-model web agents, AgentRefine, and Flow.
- Froze Regression-Gated Self-Evolution as the first-paper workspace and moved GroundEvo plus other visual mechanisms to CVPR follow-ups.
- Required every ICLR candidate to distinguish persistent learning from extra inference, name the evolving object, support causal attribution, survive multi-round regression tests, generalize out of loop, use independently grounded feedback, and match interaction/token/call/training/wall-clock budgets.
- Added ICLR/CVPR dual filtering, bilingual experiment audits, complete cross-domain P0/P1/P2 protocols, new backend tests, and real-browser assertions.

## 2026-07-30 · Live low-resource CVPR Idea laboratory

- Connected Semantic Scholar through an ignored local key and exported a deployment snapshot with 149 deduplicated papers from sixteen topic, failure, mechanism, analogy, seed, citation, and reference queries.
- Added a 61-formulation low-resource CVPR funnel with 42 passed candidates, one structured block, and eighteen early rejections.
- Added a complete execution protocol to every passed Idea: actor, cross-model architecture, critic, visual tools, optional API role, update scope, disjoint data splits, P0/P1/P2 phases, controls, repeats, budgets, decisive main table, ablations, artifacts, and Go/Stop conditions.
- Added a twelve-paper audit of published visual-agent experiment substrates, separating API-only, open-weight, and hybrid systems while preserving unknown hardware or version details as unknown.
- Routed Oracle Browser reviews into one dedicated ChatGPT project and stored the resulting PASS, REVISE, and BLOCK verdicts in the generated Idea artifact.
- Added server/data-disk separation, local secret templates, provider caching and rate limiting, project-scoped web-GPT tooling, nineteen backend tests, static QA, and real-browser assertions for all new views.

## 2026-07-30 · Evidence-gated paper Idea decision lab

- Added `research_pipeline/`, a deterministic literature-to-Idea backend with typed schemas, eight controlled generation operators, five independent reviewer roles, bounded pilot gates, and explicit advance/investigate/hold/stop decisions.
- Added swappable provider contracts for query planning, literature retrieval, facet extraction, gap mining, idea synthesis, four-way novelty collision search, review, pilot planning, and final gate decisions.
- Rebuilt `paper-ideas.html` around an eight-stage backend map, a four-stage candidate funnel, a twelve-Idea advisor shortlist, and a complete archive of all thirty-four retained candidates.
- Replaced the decimal-score-first presentation with evidence stages; legacy ranks and scores remain only as traceability metadata.
- Added complete advisor dossiers that state purpose/problem, core idea, rationale, method logic, research importance, conditional comparative advantage, nearest literature, unresolved collision, strongest baseline, decisive pilot, and Go/Stop evidence.
- Added interactive filters for selected, novelty-check, reviewer-check, and visual/CVPR candidates, while preserving bilingual content and stable anchors.
- Extended static, hierarchy, and real-browser tests for the backend stages, generation operators, reviewers, shortlist dossiers, literature neighborhoods, filtering, archive completeness, and all existing site behavior.

## 2026-07-30 · Evidence-backed direction map

- Added `direction-literature-data.js` with three representative papers for each of the ten research directions.
- Required every representative record to state the exact paper title, year/venue, a bilingual one-line method description, and why the paper supports that direction.
- Added thirty linked literature-evidence cards to `research-directions.html`; citation numbers are generated from the current bibliography order and each title opens the full six-part paper analysis.
- Reworked both standalone direction SVGs so every direction cites two representative papers and summarizes their methods instead of listing only proposed Ideas.
- Preserved the thirty-four Idea portfolio on the Paper Ideas page while making the field map evidence-backed rather than purely taxonomic.
- Extended global search, static checks, XML validation, and real-browser tests for ten evidence sections, thirty paper cards, twenty SVG paper citations, bilingual content, and zero unresolved references.

## 2026-07-30 · Role-aware bibliography order

- Replaced the citation-dominated default bibliography order with a recommended reading sequence based on each paper's role in Agent self-evolution.
- Added seven visible reading layers: recent field overviews, direct self-evolution methods, evaluation/safety/governance, enabling mechanisms, agent foundations, foundation-model precursors, and adjacent resources.
- Within a layer, peer-reviewed status and recency now precede citation count; total citations remain available as a separate historical-influence view.
- Moved Transformer, BERT, GPT-3, ReAct, and similar precursors out of the default top results while retaining them in chronological foundation sections.
- Aligned stable reference numbers with the recommended order across all canonical pages by loading the same ranking configuration before citation indexing.
- Added reading-role badges, grouped bibliography headers, role-aware JSON/CSV export fields, and browser assertions that old foundations do not dominate the top twenty.

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
