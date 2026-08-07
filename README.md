# Agent Self-Evolution Observatory

A bilingual, ICLR-first research observatory for self-evolving agents, with CVPR visual specializations preserved as a secondary roadmap.

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

The public information architecture now contains **10 canonical pages** and **19 compatibility redirects** for historical URLs. Every canonical page uses a page-specific semantic hierarchy rather than a flat list:

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
6. `system-overview.html` — technical documentation for the live backend: literature ingestion, the interactive citation/evidence graph, idea generation, R1/R2 review, P0/P1/P2, automation boundaries, and current idea states.
7. `research-directions.html` — four beginner-level questions, a running example, plain-language explanations of ten stable directions, thirty representative literature cards with one-line methods, and the long-term agenda.
8. `paper-ideas.html` — an ICLR-first literature audit, eight mechanism tracks, seven review gates, twenty-six passed low-resource candidates, the historical advisor board, and a folded CVPR follow-up archive.
9. `selected-paper.html` — Regression-Gated Self-Evolution problem formulation, matched-budget experiments, execution roadmap, and ICLR review gates.
10. `bibliography.html` — coverage protocol, interactive maps, exports, and live bibliography.

Former topic URLs such as `memory-evolution.html` and `paper-roadmap.html` remain as `noindex` compatibility pages that redirect to the matching section of a canonical hub.

## Literature corpus

The bibliography synchronizes two complementary survey-maintained catalogs in the browser:

1. `selfimproving-agent/Awesome-Self-Improving-Agents`
2. `FrontisAI/Awesome-Self-Improving-Agents`

It merges and normalizes these records with a manually verified ICLR mechanism core and a secondary visual/CVPR follow-up set. The bilingual 2400×1600 history SVG prioritizes formally published conference and journal papers, groups twenty-three milestones into five method families, and states each method's core action, update target, and feedback signal; preprint-only frontier work stays in the searchable bibliography rather than the historical spine. The live interface includes:

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

The primary target is now **ICLR**, with **CVPR as a secondary visual-specialization venue**. The frozen first-paper scope is **Regression-Gated Self-Evolution for Reliable Agent Improvement**.

The first falsifiable study asks whether compact agent updates—prompts, memories, workflows, routers, or small modules—should be treated as constrained policy improvement. A candidate update is committed only after attributed replay shows that it fixes the target failure and a disjoint regression suite shows no unacceptable loss on mastered and out-of-loop capabilities under matched interaction, token, model-call, training, and wall-clock budgets.

The automatic ICLR backend starts from **41 formulations**, structures **29 mechanism-level candidates**, passes **26** through seven review dimensions, blocks **3** after structured review, and rejects **12** before full development. The eight mechanism tracks are constrained continual evolution, failure credit and experience admission, memory and skill consolidation, self-correction and policy internalization, curriculum evolution, workflow and update-surface search, reward/evaluator evolution, and world-model/embodied adaptation.

Every passed ICLR candidate states the learning problem, evolving object, update operator, falsifiable hypothesis, nearest-work boundary, cross-domain assets, two-open-model protocol, disjoint discovery/calibration/test splits, P0/P1/P2 execution phases, matched controls, complete cost accounting, decisive multi-round main table, ablations, and Go/Stop rules. Seven explicit gates test reality of evolution, mechanistic specificity, credit assignment, update stability, out-of-loop generalization, feedback integrity, and efficiency/reproducibility.

The previous thirty-four lifecycle ideas, twelve-item advisor board, forty-two passed visual candidates, one structured visual block, and eighteen early visual rejections remain available for traceability and CVPR follow-up. GroundEvo-Admission, long-video contradiction memory, visual reward-shortcut audits, and VLA recovery are no longer mixed into the first ICLR claim.

## Evidence-gated literature-to-idea backend

The continuous backend in `research_pipeline/` normalizes literature, evidence, ideas, reviews, and pilot results into one auditable state. It now runs—not merely documents—reusable mechanisms from ResearchAgent, AI-Researcher, MOOSE-Chem/Deep-Ideation, CycleResearcher, PaperQA/OpenScholar, and the safe parts of AI-Scientist-style experiment management. No single agent output may accept a paper direction.

```text
research scope and assets
  -> multi-route query planning and citation expansion
  -> paper/query/claim/mechanism evidence graph
  -> structured gap and contradiction candidates
  -> eight problem-discovery operators
  -> independent mechanism-inspiration retrieval and concept-path bridging
  -> multi-branch method-tree search and solution concretization
  -> mechanism irreducibility, supervision-independence, and deployment-effect gates
  -> hybrid problem/mechanism/experiment deduplication
  -> idea lineage and non-destructive branch preservation
  -> seven ICLR reviewer gates
  -> reviewer-objection repair queue
  -> P0/P1/P2 pilot registry and result feedback
  -> evidence-calibrated advance / revise / hold / stop decision
```

Provider contracts in `research_pipeline/providers.py` define swappable interfaces for query planning, literature retrieval, facet extraction, gap mining, idea synthesis, novelty checking, review, pilot planning, and final gate decisions. Semantic Scholar is now connected through the ignored server `.env`, while OpenAlex, local-PDF, embedding, and LLM providers can still be added without changing the browser-facing idea schema.

On `10.42.8.52`, the Git checkout remains under `/home/wyt/code/agent-self-evolution-observatory`, while corpora, datasets, PDFs, indexes, caches, and experiment runs are stored under `/data/wyt/agent-self-evolution-observatory` on the local 33 TB data disk. Small browser snapshots remain beside the code for deployment.

Validate storage, live literature, or the current snapshot:

```bash
python -m research_pipeline --storage-status
python -m research_pipeline --init-storage
python -m research_pipeline --s2-status
python -m research_pipeline --sync-s2
python -m research_pipeline --iclr-status
python -m research_pipeline --build-iclr-bank
python -m research_pipeline --machine-school-status
python -m research_pipeline --build-machine-school-bank
python -m research_pipeline --idea-discovery-v3-status
python -m research_pipeline --build-idea-discovery-v3
python -m research_pipeline --iclr-audit-status
python -m research_pipeline --build-iclr-audit
python -m research_pipeline --research-system-status
python -m research_pipeline --build-research-system
python -m research_pipeline.automation_cycle --mode manual
python -m research_pipeline --cvpr-status
python -m research_pipeline --build-cvpr-bank
python -m research_pipeline --check
python -m research_pipeline
```

The deployment snapshots under `generated/` include the ICLR-first 26-candidate mechanism bank, the 24-candidate internet-inspired expansion, the solution-first v3/v3.1 method trees and their complete external reviews, a twelve-paper ICLR experiment-substrate audit, the preserved 42-candidate CVPR visual bank, the historical portfolio, and the current Semantic Scholar corpus. `research-system-state.json/js` currently reports 555 evidence nodes, 943 evidence edges, all 406 pairwise comparisons among 29 structured candidates, 258 lineage edges, 78 registered pilot phases, 14 v3 method children, and 6 reviewer-repaired v3.1 children. Bulk corpora, caches, raw pilot results, and automation logs remain outside Git.

## Continuous operation

The system ships two fail-safe systemd cycles for `10.42.8.52`:

- `agent-evolution-daily.timer`: deterministic offline rebuild, evidence/collision/lineage refresh, pilot-result ingestion, and health reporting;
- `agent-evolution-weekly.timer`: conservative Semantic Scholar refresh plus at most two project-scoped web-GPT repair reviews.

Both cycles use exclusive locks, preserve the previous valid deployment snapshot when one step fails, and write run reports under `/data/wyt/agent-self-evolution-observatory/runs/automation/`. Install or update the timers on server 52 with `python3 scripts/install_research_timers.py`. Automated publication uses a dedicated, write-enabled deploy key scoped to this repository: `scripts/configure_github_ssh.py` pins GitHub's official Ed25519 host key and configures repository-local SSH, while `scripts/add_github_deploy_key.py` uses the already authenticated local Git Credential Manager only during one-time public-key registration and never stores or prints its token. Transient fetch/push failures are marked `deferred` and retried on the next cycle. Unrestricted autonomous code execution is intentionally disabled; experiments run through controlled code/Codex workflows, while their structured results are ingested automatically using `research_pipeline/pilot_result.example.json` as the contract.

## External-agent review status

The ICLR programmatic first round passes 26 ideas. On 2026-08-06, all 26 were independently audited through Code Oracle and the signed-in ChatGPT Agent project on `admin01-NF5468M5`. The strict verdict distribution is **4 PASS, 10 REVISE, and 12 BLOCK**. The public ICLR bank is now ordered by R2 verdict while preserving every idea's original R1 rank.

The persistent review source is `generated/iclr-external-reviews.json`; daily ICLR-bank rebuilds merge it without erasing completed reviews or converting missing reports into passes. The batch module is `research_pipeline/iclr_external_review.py`:

```bash
# Prepare prompts only
python3 -m research_pipeline.iclr_external_review --batch-size 5

# Execute on the authoritative Oracle/browser host
./scripts/on-52.sh python3 -m research_pipeline.iclr_external_review --run --batch-size 5
```

The four standalone R2 PASS directions are Regression-Gated Self-Evolution, Contradiction-Preserving Memory Consolidation, Compositional Update Compatibility, and Agent Update Trust Region. They remain experiment-pending rather than selected-ready because no P0/P1/P2 result has entered the pilot registry. The Oracle-mediated Agent-project audit is one consistent external-review route, not a multi-agent vote. CodexFlow remains unavailable because account connection fails, and previous visual verdicts remain isolated in the secondary CVPR artifact.

## Internet-inspired candidate expansion

A user-supplied “machine school” metaphor was converted into six research variables: uneven cross-form capability, longitudinal regression exams, version-differential blame, retry dependence, model-swap compatibility, and behavior-conditioned privilege control. `research_pipeline/machine_school_idea_factory.py` expands these into **24 raw candidates**, then applies the same low-resource and falsifiability discipline:

- **11 internal PASS** candidates were sent to Code Oracle and the signed-in Agent-project ChatGPT;
- **7 internal REVISE/MERGE** candidates remain visible as repair components;
- **6 direct-collision candidates** were rejected before external review;
- the external audit of all 11 retained candidates produced **1 PASS, 7 REVISE, and 3 BLOCK**.

The sole direct `pilot-now` direction is **Regression-Probe Half-Life**: learn a probe-specific survival/decay model that predicts which regression tests retain future value across chronologically held-out agent versions. The teacher-discussion shortlist also retains seven repair-first alternatives: Version-Differential Failure Localization, Model-Swap Compatibility Certificate, Update-Aware Permission Downgrade, Cross-Form Capability Transfer Gap, Delayed Regression Exams, Privilege Recovery Curriculum, and Behavior-Triggered Privilege Lease.

Persistent artifacts are `generated/machine-school-inspired-ideas.json/js` and `generated/machine-school-external-reviews.json`. The weekly automation cycle rebuilds and publishes the inspired bank without erasing stored external reviews. The public page keeps this new batch separate from the already audited 26-idea ICLR bank.

## Solution-first Idea Discovery v3

The first two idea rounds were strong at problem discovery but often weak at method invention. The v3 workflow therefore separates problem capsules from mechanism inspirations and adopts official-repository patterns from ResearchAgent, MOOSE-Chem, SciAgents, OmniScientist, AI-Scientist-v2, RD-Agent, and SciPIP. It adds six solution operators—mechanism-inspiration retrieval, concept-path bridging, reviewer-vector repair, method-tree search, experiment-feedback induction, and resource-grounded design—to the previous eight problem operators.

The resulting workflow has nine stages and five mechanism gates. The most important new gate is irreducibility: a candidate is blocked before expensive review when the same inputs and logs can be consumed by a capacity-matched generic predictor, gate, contextual bandit, offline-RL learner, or rule learner. Candidates must also learn a new persistent object, use non-circular supervision, alter frozen future-task behavior, and support any claimed calibration or risk guarantee with enough independent units.

The first v3 round produced 14 solution-first children. Ten passed internal mechanism screening, but independent R2 returned **0 PASS, 6 REVISE, and 4 BLOCK**. A v3.1 reviewer-vector repair round continued only the six REVISE children; it returned **0 PASS, 2 REVISE, and 4 BLOCK**. The two surviving boundaries are Restoration-Clause Learning and Conformal Effect-Transport Gate, both still requiring theory or an identifiable induction rule. These results do not change the four formal PASS ideas in the main bank and are published precisely to prevent internal specificity from being mistaken for novelty.

Persistent artifacts are `generated/idea-discovery-v3.json/js`, `generated/idea-discovery-v3-external-reviews.json`, `generated/idea-discovery-v31.json/js`, and `generated/idea-discovery-v31-external-reviews.json`.

## Constrained-composition Idea Discovery v4

V4 relaxes the earlier rule that treated familiar mechanism combinations as presumptively weak. A combination is now admissible when it closes a real failure loop and every atom addresses a distinct necessary link. Earlier REVISE/BLOCK ideas are also retained as conditional-revival branches rather than permanently deleted; revival requires a material change to the learned object, supervision, deployment boundary, or executable hypothesis language.

The workflow adds official-repository patterns from HypoGeniC/HypoRefine, Open Co-Scientist, Virtual Scientists, autoresearch, autoresearch-agents, ScholarEval, and data-to-paper to the existing ResearchAgent, MOOSE-Chem, AI-Scientist-v2, and RD-Agent mechanisms. It builds a real-problem bank, a mechanism-atom bank, a structural compatibility graph, constrained one-to-three-atom compositions, conditional revivals, tournament/proximity selection, reduction challenges, resource grounding, and experiment-feedback recombination.

The first v4 pool contains **28 candidates**: 14 new compositions, 8 conditional revivals, 4 repair candidates, and 2 component/baseline branches. Sixteen tournament finalists were independently reviewed through the Agent-project Oracle route. The final external distribution is **5 PASS, 8 REVISE, and 3 BLOCK**, where BLOCK means “not standalone now” rather than deletion.

The five v4 PASS directions are:

1. **Correction-Action Causal Compiler** — learn minimal typed correction-action combinations and compile applicability-bounded programs for unseen mixed failures;
2. **Memory Interaction Clause Learner** — learn persistent compatibility, exclusion, and precedence clauses from controlled co-retrieval outcomes;
3. **Probe Mutation and Retirement Policy** — manage a fixed-budget regression-probe portfolio through keep, mutate, merge, and retire decisions;
4. **Update-Composition Repair Compiler** — learn reusable cross-surface compatibility clauses and compile preservation-maximizing repairs for unseen update compositions;
5. **Monotone Applicability-Set Specializer v4** — minimally shrink executable applicability sets from counterexamples while preserving unaffected positive regions.

All 28 candidates remain visible in `paper-ideas.html`; external BLOCK branches remain available as components, baselines, merge targets, or future revival paths. Persistent artifacts are `generated/idea-discovery-v4.json/js` and `generated/idea-discovery-v4-external-reviews.json`.

## Wide-search Idea Discovery v5 → v5.3

V5 makes the search target explicit: accumulate at least **20 strict external R2 PASS ideas** before senior-level direction discussion, without counting internal shortlists, REVISE ideas, or the supplementary internet-inspired batch. It expands evidence sources with empirical failure capsules, knowledge-graph neighbors, multi-team proposal diversity, simplification challenges, and micro-experiment keep/revert signals. The raw v5 pool contains 36 candidates; 32 finalist/revival candidates received official-source R2 review, yielding **6 PASS, 19 REVISE, and 7 BLOCK**.

REVISE does not trigger free-form rewriting. V5.1 generated exactly one reviewer-vector child for each of 19 v5 REVISE parents and returned **3 PASS, 12 REVISE, and 4 BLOCK**. V5.2 repaired only those 12 REVISE children against their second reviewer vectors and returned **1 PASS, 8 REVISE, and 3 BLOCK**. Because the strict portfolio was still 19/20, v5.3 selected only four closest-to-PASS v5.2 REVISE ideas with one explicit surviving boundary; their final-boundary review returned **3 PASS and 1 REVISE**.

The strict discussion-ready portfolio is therefore **22/20**: 4 main-bank PASS + 5 v4 PASS + 6 v5 PASS + 3 v5.1 PASS + 1 v5.2 PASS + 3 v5.3 PASS. The search stops after reaching the target. `generated/discussion-ready-ideas.json/js` is the single authoritative roster used by both the system overview and idea page.

Persistent artifacts include `generated/idea-discovery-v5*.json/js`, the per-round external-review stores for v5/v5.1/v5.2/v5.3, and the strict discussion-ready roster. All BLOCK branches remain preserved as components, baselines, or future revival sources; they are never silently deleted or renamed into later rounds.

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

- 10 canonical pages and 19 compatibility redirects;
- navigation targets, merged content groups, redirect anchors, and the page-specific chapter configuration;
- all 34 bilingual Idea reasoning records and their six mandatory argument fields;
- the ICLR-first evidence pipeline, eight mechanism tracks, seven reviewer dimensions, twenty-six R1 passes, complete 26/26 Oracle/web-GPT review coverage, the 4 PASS / 10 REVISE / 12 BLOCK R2 distribution, and the separate 24-candidate internet-inspired expansion with 11/11 external reviews and a 1 PASS / 7 REVISE / 3 BLOCK verdict distribution;
- the eight-item teacher-discussion shortlist, with Regression-Probe Half-Life as the only `pilot-now` inspired direction;
- three structured ICLR blocks, twelve historical advisor dossiers, the complete 34-idea archive, and the folded CVPR follow-up bank;
- 42 executable low-resource CVPR protocols, one structured block, 18 early rejections, 12 published experiment-substrate audits, and project-scoped web-GPT verdicts;
- JavaScript syntax and one-to-one bilingual coverage of all six Idea reasoning fields;
- sitemap, CNAME, favicon, manifest, robots, and 404 resources;
- upstream catalog counts and deduplication;
- missing URLs and unresolved topic-page citations;
- venue-tier ranking configuration, the dated citation snapshot, four ranking modes, and all 24 bilingual top-paper analyses;
- dynamic catalog loading, three bibliography maps, sorting, filters, URL state, and pagination;
- exact H2/H3/H4 and nested-TOC counts for all ten canonical pages;
- history and direction figures, including twenty literature citations inside the bilingual direction SVG and thirty linked evidence cards on the page;
- merged hub rendering, linked resources, legacy redirects, and mobile navigation.

## Deployment

GitHub Pages publishes the `main` branch with the custom domain stored in `CNAME`:

```text
agent-evolution.lightrain.asia
```
