## 2026-08-28 · Outcome-blind cross-substrate constraint-integration proposal

- Preserved the VWE-specific PORT-010 `HOLD_EVIDENCE_REVIEW_BLOCKED / BLOCK_BAKE_IN` object and staged a separate zero-authority LEGO-Bench proposal instead of treating benchmark substitution as a scientific reopen or completion.
- Rejected raw released constraint count as the primary complexity dose before reading any per-case generator/evaluator outcomes because it is strongly confounded with instruction length (Spearman `rho=0.861988`). The surviving candidate construct is Shannon entropy over the four official LEGO constraint types (`rho=0.195851` with instruction length), interpreted only as a candidate cross-type integration burden pending Generator/ProblemGate review.
- Froze an outcome-independent robustness panel of 11 disjoint pairs matched exactly on total constraint count and an analyst-defined metadata-order block, within 10 instruction words, with at least 0.35-bit type-entropy contrast. The later collision review strengthened the full-sample null from additive per-type difficulty to conditional-independent multiplicative accumulation using the same marginal observables; no outcome rematching, threshold retuning, generator dropping, provider execution, or GPU execution is authorized by this preflight.
- Hardened the metadata parser against a real release-schema trap: LEGO label list order is not always constraint order (rows 121, 127, and 129). Constraint types are therefore bound only through the released `condition_idx`, matching the official evaluator, and extra label metadata are ignored by the construct audit.
- A current-source collision pass further narrowed the object: LEGO-Eval already reports count-based complexity degradation, GraphDreamer/InstructScene already establish generic graph-structured generation priors, and arXiv:2608.12426 supplies a stronger cross-domain independent-failure/multiplicative null. The surviving candidate is therefore conditional cross-type failure coupling in 3D generation. Any future coupling result must also beat evaluator-dependence controls, including human-curated satisfying scenes and a bounded fresh-state per-constraint evaluation check.

## 2026-08-28 · Make pinned Hugging Face release surface executable

- Closed a projection/runtime mismatch in PORT-010 release monitoring: canonical state already pinned the VWE-Bench Hugging Face dataset, but the live watcher still filtered every non-GitHub support-audited target.
- Added a strict `FIRST_PARTY_DATASET` endpoint type for canonical `huggingface.co/datasets/<namespace>/<repo>` URLs. The watcher resolves the official dataset-info `sha` plus file manifest into a revision-bound fingerprint; endpoint type and declaration kind must match, and a 40-hex baseline remains mandatory.
- Verified against the current canonical PORT-010 state that both GitHub VibeWorlding-Gym and Hugging Face VWE-Bench now enter the same content-addressed zero-authority watch contract. Dataset revision drift can request release recheck only; it cannot qualify support, reopen Problem Gate, authorize execution, or release science.


## 2026-08-28 · PORT-010 full first-party release-surface coverage

- Closed the F18/PORT-010 release-watch coverage gap without reopening science: the independently verified Hugging Face `usail-hkust/VWE-Bench` dataset surface is now content-addressed at `1f085b54166a8253d7a42854e2b1c7e1fe8dcceb` alongside the GitHub VibeWorlding-Gym source.
- The dataset audit found query/training assets but no author-released per-case Pass@1/model-evaluator outcomes or sufficient original trajectories. `per_case_outcomes` therefore remains the frozen reopen blocker; provider/GPU/offline-replay/scientific authority remain false and local rollouts cannot stand in for author outcomes.
- Generalized the F18 binding from a single first-party target to a content-addressed target set. Exact-F0 now hashes the whole source-surface set, so adding or changing a first-party surface changes provenance but cannot silently create scientific authority.

## 2026-08-28 · F18 ↔ PORT-010 replay/authority contract

- Bound F18 to the current VWE PORT-010 scientific object by candidate snapshot, release-watch contract hash, source revision, and frozen HOLD/BLOCK_BAKE_IN state; candidate id alone is explicitly insufficient because historical PORT-010 objects exist.
- Added an exact-F0 content-addressed zero-modification reference and a fail-closed replay receipt validator: replay cannot mutate F0, missing/mismatched artifact provenance is rejected, receipts cannot self-authorize or override canonical evidence review, and local rollouts remain prohibited from masquerading as author-released outcomes.
- Added a system-gate-only regression runner whose PASS state still reports `scientific_release=HOLD` and creates no scientific evidence or execution authority.

# Changelog

## 2026-08-27 · Effective-HOLD release-watch recovery

- Audited the first-party VibeWorlding-Gym source after a real same-day revision change from `ddb6ff54...` to `ec8bdebf...`. Immutable Git objects show two commits: `LICENSE.md` / `NOTICE.md` were added and the README changed only inside the Citation/licensing section; no outcome-, trajectory-, reward-, result-, or rollout-like artifact was introduced. The release is therefore `RECHECKED_RELEASE_IRRELEVANT`, not scientific reopen evidence.
- Closed a release-monitor coverage hole for Pre-F0 candidates that initially allowed bounded first-party evidence design but later became source-specific after independent `BLOCK_BAKE_IN`. Release watch and asset recheck now consume the same effective zero-authority support-HOLD population, rather than keying only on the historical `bounded_first_party_evidence_design_allowed` flag.
- Added a content-addressed `release_watch_contract` bound to candidate snapshot, immutable repository baseline, and required reopen components. PORT-010 now watches VibeWorlding-Gym from `ec8bdebf...`; the remaining frozen reopen component is still `per_case_outcomes`, and a release revision alone cannot qualify support or authorize Problem Gate, method, experiment, P0, GPU, or provider execution.
- Added an exact-Git source-release audit receipt and replayed the full path `release drift → zero-authority asset recheck → irrelevant-release resolution → HOLD`. The live post-audit watch returns `NO_RELEASE_CHANGE` at the new baseline, while the historical drift replay clears only the recheck task and leaves scientific state unchanged.

## 2026-08-26 · Fail-closed primary-release reopen semantics

- Split first-party release handling into `RELEASE_CHANGE_AUDIT_ONLY` versus `DESIGN_REVIEW_ONLY`: a changed upstream revision is now recorded without reopening a scientific HOLD unless the frozen reopen condition is actually satisfied.
- Added structured reopen-component accounting (`required_reopen_components`, `materialized_reopen_components`, and `remaining_reopen_blockers`) plus zero-authority validation so metadata-only releases cannot silently stand in for missing author-released outcomes.
- Re-adjudicated PORT-010 against VWE-Bench: 254 released test metadata units remain useful provenance-bearing support, but the missing author-released per-case Pass@1/outcome artifact keeps the prior `BLOCK_BAKE_IN` / `HOLD_EVIDENCE_REVIEW_BLOCKED` contract effective. Self-generated `main.py`/`eval.py` rollouts remain prohibited from being represented as author-released evidence.
- Preserved the historical erroneous reopen receipt as audit provenance, set effective reopen count to zero, refreshed only the Pre-F0-derived composite projection, and kept provider/GPU/scientific execution authority at zero.

## 2026-08-17 · Site-wide Chinese-first frontend pass

- Fixed language switching at the shared shell level: brand, sidebar navigation, search placeholder, sidebar note, footer, and the global current-research strip now rerender with the selected language instead of leaving an English shell around Chinese page content.
- Made the Chinese current-state views Chinese-first across Paper Ideas, Experiments, and Selected Paper: paper-ready/evidence-debt/canonical/shadow labels, STRI evidence blocks, claim/exclusion text, handoff text, historical ledger headings, ENS components, and common paper-first terminology now use Chinese descriptions while exact machine IDs and typed terminal enums remain unchanged.
- Localized bibliography/evaluation display taxonomies without changing internal filter keys: update surfaces, publication types, feedback signals, live-literature categories, maps, filter controls, and resource-index summaries now render Chinese labels while preserving stable URLs/data values.
- Added real-browser Chinese assertions for the shared shell plus Paper Ideas, Experiments, Selected Paper, Bibliography, and Evaluation. Final full-site browser/mobile and focused system/idea suites both pass; remaining pure-English leaf text is intentionally dominated by paper/model/benchmark names and exact machine status identifiers.
- Deepened the Paper Ideas Chinese layer after a DOM-level audit: matched-budget/resource constraints, historical pilot explanations, final routing, revived terminal contracts, Paper-first/Shadow summaries, closest-work labels, SP-15 support inventory, ENS, and absorbed internal method assets now render Chinese-first. Exact PA/PF/SP IDs, typed `STOP_*` codes, model names, and official paper titles remain available for auditability.
- Removed the remaining mixed-language narrative on Paper Ideas and its shared status strip: `Paper Design`/`Method Design`/`Fresh`/`Shadow`/`standalone`/raw method slugs now render as Chinese reader terms, with raw machine identities retained only as codes or hover audit metadata. The fully expanded Chinese DOM no longer contains the audited English explanatory phrases.
- Audited all 11 canonical frontend pages as one UI contract. Chinese explanatory text now passes a final display-localization layer while typed machine IDs/status enums/hashes remain protected; all page TOCs stop at H3; direct visible text is at least 11.5px, prose/table text at least 12px (12.5px on narrow screens), and long status codes wrap instead of creating page-level horizontal overflow. The full browser regression now expands details on every canonical page and enforces these Chinese/readability/mobile invariants site-wide.

## 2026-08-17 · Readable research-system flow

- Reorganized `system-overview.html` around seven reader chapters: start-here architecture → real-problem discovery → paper design → pre-experiment compile → execute/diagnose/freeze/scale → paper evidence/release → system learning/memory. The canonical 11-stage lifecycle and six backend responsibility layers remain unchanged scientific/runtime sources of truth.
- Added backend `READING_GROUPS` with machine validation that the six advancing reader groups cover all 11 canonical temporal stages exactly once; missing, duplicated, or unknown stage mappings now fail the research-system architecture health check.
- Replaced the module-history-heavy main narrative with compact phase cards using `Input → Decision → Output`, a short decision flow, current signals, and an explicit stop/reset rule. Architecture internals, full Pre-Experiment gates, runtime/artifact inventories, and methodology references remain available as four collapsed machine-detail sections.
- Simplified the start page to six architecture statistics, six research invariants, a seven-chapter roadmap, and one three-level authority model. The sidebar now keeps the seven chapter H2 headings plus visible H3 section headings, while H4 and collapsed machine-detail headings remain excluded so the TOC shows useful second/third-level structure without becoming an engineering dump.
- Reworked the Chinese reader layer to use Chinese-first terminology for `Input → Decision → Output`, problem discovery/reduction, Economy/Protocol/Updater admission, method freeze, paper-evidence closure, system replay, authority examples, roadmap outputs, and deep-dive summaries. English is retained only where a code/status/paper term benefits from an explicit parenthetical anchor.
- Preserved all existing machine-level content and selectors for auditability; focused, system-only, and full-site real-browser smoke tests continue to pass, including Chinese switching and mobile navigation.
- Added a page-scoped readability floor after computed-font auditing: default visible text is at least 11.5px, prose/table explanations at least 12px, mobile prose at least 12.5px, and expanded machine-detail sections are covered by the same browser regression check.

## 2026-08-17 · Content-addressed manuscript evidence completion

- Closed a generic Paper Quality loophole in which plausible-looking artifact path strings could satisfy manuscript completion without proving that the referenced files existed or still matched the frozen evidence receipt.
- Added fail-closed content-addressed completion: every completed baseline, ablation, analysis, output, figure, figure-data source, and generation script used by paper-ready mode must resolve to a safe in-project file with a matching SHA256 receipt; missing files, stale digests, absolute/path-traversal references, and unregistered claim evidence IDs block readiness.
- Replayed the stronger gate on STRI: 14 actually referenced manuscript/evidence/visual files are SHA-bound, Paper Quality remains `PASS_MANUSCRIPT_EVIDENCE`, evidence debt remains zero, and the paper remains `READY_NARROW_ICLR` without changing any scientific claim or experiment result.
- Exposed content-addressed completion in the public STRI projection and System Overview, and recorded the closed local gap under the Science One Chain-of-Evidence learning entry.

## 2026-08-17 · Substrate-gated multi-paper F0 portfolio

- Added `PA-05-SKILL-VALIDATION-TRANSFER`, asking whether local skill replay/validation identifies deployment-time procedural transfer rather than proposing another skill generator.
- Bound PA-05 to the first-party SkillEvolBench commit `9e3daa339987c3cfa624121e1be442593a53d43c` and archive SHA256 `2892e337780746e547a748c947b379b3c55af09eea1d273ace383b80d2e569ee`. Official asset/config validation passes for 30 latent families / 180 primary tasks; `raw_trajectory_rag` and `selfgen_experience_always` each compile to the identical 270-trial schedule (180 primary + 90 frozen T1-T3 replays) with zero model calls executed during preflight.
- Added the content-addressed `skill-validation-transfer-f0-v1` analyzer. A GO requires both representations to win nontrivial local and deployment family subsets, at least 10 jointly decisive families, at least 40% local-to-deployment preference inversions, positive family-bootstrap oracle-vs-local-selection regret, and no material advantage of the local selector over the best global arm. Global representation dominance therefore STOPs instead of being relabeled as a selection-validity problem.
- PA-05 is currently the sole design-ready fresh F0 and is held only by execution environment/controller authority. PA-01 is `STOP_REDUCTION` after its authorized generic-repetition F0; PA-02 is `STOP_REDUCTION` after same-information Pareto/overblocking reduction; PA-03 remains `HOLD_SUPPORT`; PA-04 is `STOP_REDUCTION` after the primary paper's visual-grounding explanation.
- Frontend current-state rendering enumerates the whole fresh portfolio, and System Overview distinguishes design-ready, execution-HOLD, support-HOLD, reduction-STOP, and ACTIVE_F0 states.

## 2026-08-17 · Fresh Phenomenon Portfolio and evidence-echo F0

- Added a zero-authority Fresh Phenomenon Portfolio between primary-source discovery and canonical Problem Gate. The portfolio permits at most one `ACTIVE_F0`; a candidate may occupy that slot only when it already has a provenance-audited local substrate and a frozen same-information falsifier. Source-only ideas remain support HOLDs and cannot consume experiment/GPU budget.
- Registered four current scouts without inflating the canonical queue: PA-01 evidence echo is the sole `ACTIVE_F0`; security/utility collapse in self-evolving defense, train/test harness-selection inversion, and high-relevance spatial-memory failure remain `HOLD_SUPPORT`. A positive F0 still grants no Problem-Gate, Paper-Design, Method, P0, GPU, or full-experiment authority.
- Bound PA-01 to the frozen 128-unit P06/DocAtlas substrate. On the 64 benchmark-unanswerable units, the existing `naive_summary` arm raises false-answer rate from 10.9% to 21.9% relative to the negative-evidence baseline, with 7 induced versus 0 repaired false answers (exact paired p=0.015625) and zero net exact-accuracy change on the 64 answerable units. This is treated only as a retrospective phenomenon, not novelty evidence.
- Compiled a five-arm decisive falsifier: `RAW_ONLY`, `ECHO_EXTRACTIVE`, `VERBATIM_DUPLICATE`, `TOKEN_MATCHED_NEUTRAL`, and `DEDUP_WARNING`. Raw pages, BM25 ranking, model snapshot, temperature, two-step decision budget, and retrieval expansion are frozen; all four non-RAW note arms have an exact common token budget. `ECHO_EXTRACTIVE` and `DEDUP_WARNING` preserve the identical extractive evidence payload, so token matching never deletes evidence.
- The F0 distinguishes correlated-evidence double counting from extractive-summary salience and generic prompt-length/repetition/calibration effects. Neutral-padding reproduction, loss of the paired effect, or costly warning recovery is a preregistered STOP; either scoped GO only advances to current-source collision review, never directly to a paper claim.
- Integrated fresh-F0/hold counts into the research-system and current-status projections and added a System Overview card documenting the single-slot/no-substrate-no-compute rule. Updated browser invariants for the current four scientific-object lanes, digest-based relation-universe staleness, and the new terminal fresh-support HOLD accounting.
- No PA-01 GPU run was launched in this change: all authorized GPUs inspected on 52/69 were occupied, while MCP-Yu credentials for 60/220 were unavailable. The experiment is protocol-ready rather than silently queued or run by preempting unrelated jobs.

## 2026-08-16 · Visual Evidence Contract v2.1

- Benchmarked paper-evidence presentation patterns from The AI Scientist / AI Scientist-v2, PaperVizAgent, Agent Laboratory, ERA / AI co-scientist / Kosmos, and Science One, then compiled the reusable parts into Paper Evidence Quality v2.1 rather than treating them as manuscript-style advice.
- Added a fail-closed Visual Evidence Contract: every planned figure now declares a reviewer question, takeaway, target claims, source evidence IDs, visual type/role, main-vs-appendix placement, uncertainty requirement, and whether negative/failure evidence must be visible. Manuscript completion requires versioned data, generation script, rendered artifact, caption binding, and figure QA for labels, scales, source data, uncertainty, and failure visibility.
- Added archetype-specific visual portfolios. Method papers require main comparison + ablation + mechanism + failure + sensitivity views; system papers additionally require scaling/progression and recommend human-evaluation visuals; theory/certificate papers require boundary + mechanism + failure + sensitivity. Multi-panel figures may satisfy several roles only when they answer one explicit reviewer question.
- Upgraded all four current paper-first P0 design contracts to v2.1 with four reviewer-question-driven main visuals each, and added a zero-authority `Paper Visual Evidence Portfolio` exposing 16 planned main visuals across those four designs plus four completed STRI main figures.
- Replaced STRI's former representation-ablation table with a compact three-panel result figure: clone/split raw-representation distortion versus exact quotient recovery; 49/49 leave-one-tool, 399/399 leave-one-row, and 500-resample witness robustness; and the 49-tool failure/boundary taxonomy. The richer visual evidence still fits the official 9/9-page ICLR main-text limit.
- Rebuilt the paper/supplement chain: narrow manuscript QA is now 60/60, official ICLR QA remains 50/50 with 9/9 main pages, anonymous supplement reproduction is 13/13 tests with all four figures reproducible, and the post-visualization independent final review remains `READY_TO_SUBMIT` with zero required revisions.

## 2026-08-16 · Paper Evidence Quality v2 and STRI fail-closed reclassification

- Added `paper_quality_gate.py` so Paper Design validates scientific evidence structure rather than merely checking that baseline/ablation fields are nonempty.
- Added typed baseline roles with matched-information/budget requirements; claim-level `why better / where better`, alternative explanations, and ruling-out tests; component/representation/boundary ablations; and mandatory mechanism, failure, sensitivity/robustness, and uncertainty analyses where applicable.
- Added manuscript-evidence completion checks: planned evidence must resolve to versioned artifacts with `PASS`, `FAIL`, `INCONCLUSIVE`, or justified `NOT_APPLICABLE`; failed and inconclusive evidence remains visible.
- Activated Paper Evidence Quality v2 for schema 2.3+ Paper Design contracts while preserving historical pre-v2 cards without retroactively inventing evidence.
- Migrated the four current paper-first P0 contracts to schema 2.3 with 3 typed empirical baselines, 2 ablations, 5 analyses, and 5 planned manuscript outputs each.
- Replayed the new gate on STRI. Existing 59/59 manuscript QA, 50/50 ICLR format QA, page-limit checks, and supplement reproduction remained valid mechanical checks, but the first v2 replay correctly downgraded the paper to `HOLD_PAPER_QUALITY_V2` with eight explicit scientific-evidence debts.
- Added a frozen CPU analysis suite on the released Skill-SP support matrix. The matched baseline ladder now shows 183/314 Level-1 overlap rows, minimum exact-coverage pruning reducing 183 to 71 (61.2% removed) without absorbing the residual, and exact global package reweighting remaining `R*=2` on full/calibration/heldout versus `R*=1` on the released Level-3 negative control.
- Added explicit representation ablations and analysis: exact clone/split operations can change raw multiplicity and the human-readable singleton witness, but exact-support quotienting recovers every original support row and witness count; both Level-1 witnesses survive 49/49 leave-one-tool and 399/399 leave-one-row deletions, while 500 fixed-seed tool resamples retain at least one witness in 100% and both in 97.2% of replicates. Per-tool failure regimes are retained as closed-form witness / overlap-but-inconclusive / singleton-only / no-support instead of silently treating witness absence as a negative result.
- Revised the 9-page ICLR body to consume the new evidence as an explicit matched-baseline table, representation-ablation table, failure analysis, and sensitivity analysis. `Paper Quality v2` now returns `PASS_MANUSCRIPT_EVIDENCE` with evidence debt 0; 59/59 manuscript QA and 50/50 official-format QA still pass, isolated source compilation remains 9/9 main-text pages, and the post-revision independent final reviewer returns `READY_TO_SUBMIT` with score 8/10 and zero required revisions.
- Rebuilt the anonymous PDF/source/supplement artifacts; the supplement now reproduces the clone/split/ruling-out/failure/sensitivity analysis in addition to the earlier exact certificate and negative controls. Updated the public STRI status/front-end and reviewer protocol so mechanical/format QA can never substitute for this claim-matched evidence closure.
- Bound the Paper Quality v2 receipt to SHA256 digests of the exact reduction, coherence, final-review, analysis, pruning, body, and table artifacts. Any later evidence/manuscript drift now invalidates the public READY projection until the quality receipt is recomputed.

## 2026-08-08 · Reviewer-first paper-idea reading flow

- Reorganized `paper-ideas.html` around the senior-review sequence rather than the backend generation chronology.
- Moved the 22 independently R2-PASS ideas to the primary reading layer and regrouped them into four scientific-problem clusters instead of v4/v5 provenance buckets.
- Expanded every discussion card into the full senior-review argument contract: purpose/problem → research importance → core idea → core intuition → rationale → method logic → comparative advantage → closest work/collision boundary → method flow → strongest baseline → decisive pilot → independent ground truth → Stop.
- Added evidence-grounded fallbacks for v4/v5/v5.x fields, including lineage-based recovery of the original research problem, learning-signal/independent-truth separation, and Chinese localization of the four main-bank R2 findings.
- Added a compact three-step reading guide and a direct link to `system-overview.html` for backend details.
- Collapsed experiment-substrate audits, the full R1/R2 banks, v3/v4/v5 repair lineage, network-inspired candidates, historical advisor material, and CVPR follow-ups by default while preserving complete traceability.
- Reduced the `paper-ideas` page TOC to four chapters and three useful level-3 review nodes; hidden trace/archive headings no longer pollute the sidebar.

## 2026-08-08 · Keep the full strict-R2 discussion pool

- Froze idea expansion after the strict portfolio reached 22 independent R2 PASS directions, exceeding the 20-idea discussion target.
- Simplified the pre-advisor policy: independent Agent-project web R2 PASS is the only admission criterion for the senior discussion pool.
- Removed the comparative shortlist / first-read layer from the active workflow and public site; all 22 qualifying ideas are presented equally for senior/teacher discussion.
- Kept the authoritative `discussion-ready-ideas` roster and the full per-idea R2 evidence, mechanisms, baselines, pilots, and lineage.

## 2026-08-07 · Target-driven 20-idea search (Idea Discovery v5–v5.3)

- Added a 36-candidate wide-search v5 bank spanning empirical failures, memory, update history, cross-surface transfer, tool/API semantics, workflows, evaluators, curricula, multi-agent communication, permissions, and model migration.
- Completed strict official-source R2 for all 32 v5 finalists/revivals: 6 PASS, 19 REVISE, and 7 BLOCK.
- Added reviewer-vector repair rounds rather than renaming failed ideas: v5.1 = 3 PASS / 12 REVISE / 4 BLOCK; v5.2 = 1 PASS / 8 REVISE / 3 BLOCK.
- Added v5.3 final-boundary repair for only four closest-to-PASS v5.2 REVISE ideas; result = 3 PASS / 1 REVISE / 0 BLOCK.
- Added `discussion_portfolio.py` and generated discussion-ready artifacts with a strict external-PASS-only stop target. The portfolio now contains 22 qualified ideas against a target of 20 and automatically stops further expansion.
- Added v5/v5.1/v5.2/v5.3 rendering, strict `/20` progress, simplification challenges, final-boundary repair traceability, CLI/automation/publication integration, and frontend-only deployment coverage.

## 2026-08-07 · Constrained composition and conditional revival (Idea Discovery v4)

- Added a 28-candidate v4 bank with 14 new compositions, 8 conditional revivals, 4 repair candidates, and 2 retained component/baseline branches.
- Replaced the implicit “known components imply weak novelty” rule with an atom-necessity audit: combinations are allowed when every atom closes a distinct link in a real failure loop and no capacity-matched simpler method reproduces the result.
- Added eleven official GitHub workflow patterns, including HypoGeniC/HypoRefine, Open Co-Scientist, Virtual Scientists, autoresearch, autoresearch-agents, ScholarEval, and data-to-paper.
- Completed independent Oracle/Agent-project reviews for all 16 tournament finalists: 5 PASS, 8 REVISE, and 3 BLOCK, with bilingual findings, actions, collision boundaries, and combination audits.
- Identified five new PASS methods: Correction-Action Causal Compiler, Memory Interaction Clause Learner, Probe Mutation and Retirement Policy, Update-Composition Repair Compiler, and Monotone Applicability-Set Specializer v4.
- Preserved all BLOCK branches as components, baselines, merge targets, or future revival paths rather than deleting them.
- Added the v4 website panel, R2-ordered finalists, parent/revival traceability, mechanism atoms, composition logic, public assets, decisive pilots, and mobile rendering.
- Integrated v4 into the CLI, weekly automation, publication manifest, unified research-system state, static tests, browser tests, and frontend-only build.

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
