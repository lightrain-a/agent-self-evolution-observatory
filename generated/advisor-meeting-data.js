window.ADVISOR_MEETING_DATA = {
  "schema_version": "1.0",
  "generated_at": "2026-09-05",
  "meeting": {
    "id": "2026-09-06-advisor",
    "main_ref": "bb9b99d915de1141ac39654550dd91f81070ee00",
    "status": "9_OF_9_READY",
    "review_route": "exception-and-boundary-review"
  },
  "papers": [
    {
      "paper_id": "E1",
      "order": 1,
      "title": "Self-Evolution Should Not Depend on How Skills Are Split: An Exact Certificate for Skill-Taxonomy Representation Invariance",
      "paper_status": "PDF_READY",
      "pages": 12,
      "pdf_sha256": "cb09d2dd54a5b59725bcda9895be3ccfa668d274d09d027761c518a38865c9e1",
      "pdf": "downloads/advisor-20260906/01-E1-STRI.pdf",
      "paper_candidate_ref": "origin/main@bb9b99d9 + clean rebuild from STRI source commit 8a924e8c",
      "scientific_canonical_ref": "origin/main@bb9b99d915de1141ac39654550dd91f81070ee00",
      "science_delta": "Claim-expansion P0/P1/P2 remains separate/prospective unless explicitly integrated.",
      "best_case": "用精确证书刻画：语义等价的 skill 打包/身份不应改变实际可访问的技能控制面，并定位 capacity-limited dynamic retrieval 下的表示不稳定。",
      "advisor_question": "真实 Agent skill ecosystem 中，capacity-limited dynamic retrieval 是否足够常见、足够重要，使这个 abstraction 值得 standalone paper？",
      "stanford": {
        "status": "READY",
        "numerical_score": 6.5,
        "textual_signal": "POSITIVE",
        "review_date": "2026-09-05T09:09:21.449587",
        "advisor_digest": {
          "strongest_positive": "- Technical novelty and innovation - Introduces a clear, system-level invariance object (STRI) that cleanly separates semantic support/payload from physical packaging and access mechanism. - Provides an exact structural certificate (R*(A; q)) connecting realizability of target exposure to classical cone feasibility with a dual certificate, plus an interpretable factor-2 witness pattern. - Proposes a quotient-factorization characterization of exact-refinement invariance, precisely delineating clone sensitivity in identity-local normalization and giving a semantic-first action-basis alternative. - Experimental rigor and validation - Uses released, first-party artifacts and validators for Skil…",
          "decision_changing_concern": "- Technical limitations or concerns - The definition and operationalization of the semantic projection φ(E_t) at runtime remain somewhat abstract; practical instantiation may be nontrivial outside the audited settings. - The reliance on binary support matrices with “independent support truth” is strong; in many real systems, noisy or graded supports prevail and the estimation of L ≤ A ≤ U bounds is deferred. - The primary target q is mostly the neutral uniform vector; limited exploration of alternative target rays relevant to specific controllers or objectives weakens generality claims. - Experimental gaps or methodological issues - Behavior-level propagation beyond the P19 witness is not e…",
          "reviewer_question": "1. How is the semantic projection φ(E_t) instantiated in each runtime experiment, and how sensitive are results to reasonable alternative φ choices (e.g., equivalence classes of callable capabilities versus tool-call sets)? 2. Beyond q = 1, which target rays do you believe are operationally justified for common controllers (e.g., demand-weighted or performance-weighted targets), and how do R*(A; q) conclusions vary across them? 3. In settings without crisp binary validators, how would you recommend estimating L ≤ A ≤ U robustly enough for the box-robust audit to remain informative? Any preliminary experience with graded supports? 4. The SkillRL phenotype is identity-sensitive under finite b…"
        },
        "token_fingerprint_sha256_16": "6bc64d7089d84ab4"
      }
    },
    {
      "paper_id": "B1",
      "order": 2,
      "title": "Failure Memory Provenance",
      "paper_status": "PDF_READY",
      "pages": 16,
      "pdf_sha256": "7337d7eaf2edbb21673ec147af37d55a36693ed71b17cd1c99ba09a4d96ef957",
      "pdf": "downloads/advisor-20260906/02-B1-Failure-Memory-Provenance.pdf",
      "paper_candidate_ref": "origin/main downloads/B1-Failure-Memory.pdf (R66 release)",
      "scientific_canonical_ref": "origin/main@bb9b99d915de1141ac39654550dd91f81070ee00",
      "science_delta": "R75-R79 paired-ID/repeatability/mechanism/scale diagnostics postdate this integrated PDF; show separately in evidence drawer.",
      "best_case": "在 retrieved content/order 固定时，直接审计显式 source-outcome 信息到底改变多少局部动作与终端结果，把 provenance 的增量价值从 memory content 中分离出来。",
      "advisor_question": "在 terminal effect 稀疏的边界下，这个 provenance audit 是否仍足够 standalone，还是应与 Paper A 合并成更强的因果链？",
      "stanford": {
        "status": "READY",
        "numerical_score": 6.1,
        "textual_signal": "MIXED_POSITIVE",
        "review_date": "2026-09-05T09:09:29.732412",
        "advisor_digest": {
          "strongest_positive": "- Technical novelty and innovation - Introduces a clear, actionable L0–L3 identification ladder that separates association (L0), writer-mode interventions (L1), exact-information field exposure (L2), and source-faithful transport (L3). - Executes a precise L2 contrast: same retrieved content/order, only toggling a truthful outcome field to isolate the incremental value of that field beyond content. - Proposes Provenance-Separated Memory Governance (PSMG), which preserves provenance in the control plane but avoids hard-coding SUCCESS/FAILURE as a trust prior. - Experimental rigor and validation - Careful preregistration of thresholds (|Δ| ≥ 0.15), randomization/tests (paired sign test; paire…",
          "decision_changing_concern": "- Technical limitations or concerns - The masked arm (T=0) can still contain implicit outcome clues in the memory text, diluting the purity of the L2 contrast; this is acknowledged but remains a confound. - The structured-field manipulation changes the prompt surface; without a format-matched control (e.g., field present in all arms with unknown/truthful/reversed values), it remains hard to separate semantic provenance use from generic structured-prompt sensitivity. - Sparse discordance leads to low-resolution inferential power; the paper cannot establish practical equivalence nor exclude moderate effects. - Experimental gaps or methodological issues - Limited to one environment (OSInteract…",
          "reviewer_question": "1. Can you provide stratified analyses by the proportion of failure-derived retrieved items within each cluster and by whether the exposed field indicates success vs failure? Do “failure” labels produce larger action changes than “success” labels? 2. How often did the masked-content arm include explicit or easily inferable failure signals in the memory text (e.g., “reflection,” “error,” “fix”)? Can you quantify this and estimate how much it dilutes the L2 contrast? 3. Have you considered a format-matched control where the source_outcome field is present in both arms but set to UNKNOWN vs TRUTHFUL vs REVERSED to separate semantic use of outcome from structured-prompt sensitivity? 4. Beyond f…"
        },
        "token_fingerprint_sha256_16": "baab94e480450fbc"
      }
    },
    {
      "paper_id": "C1",
      "order": 3,
      "title": "Stage-Resolved Memory Transport",
      "paper_status": "PDF_READY",
      "pages": 14,
      "pdf_sha256": "a5ce511a11a7781ca5374e0f54f7830454927874ca8dc6112c87e6106ab20167",
      "pdf": "downloads/advisor-20260906/03-C1-Stage-Resolved-Memory-Transport.pdf",
      "paper_candidate_ref": "C1 R7 post-Stanford repair PDF",
      "scientific_canonical_ref": "origin/main@bb9b99d915de1141ac39654550dd91f81070ee00",
      "science_delta": "Sep4 first-action/collision/noise-floor audits postdate R7 PDF; do not silently fold into claims.",
      "best_case": "把“记忆写入了却没改变行为”拆成 write → native exposure → uptake → endpoint 的阶段证据，定位 persistent-memory transport 在哪里衰减。",
      "advisor_question": "stage-resolved diagnosis 本身是否足够构成 paper-level contribution，还是必须升级成 prospective repair/routing method？",
      "stanford": {
        "status": "READY",
        "numerical_score": 5.2,
        "textual_signal": "MIXED_POSITIVE",
        "review_date": "2026-09-05T09:10:37.869549",
        "advisor_digest": {
          "strongest_positive": "- Technical novelty and innovation - Introduces a clean, same-trajectory writer intervention (flipping success/failure reflection) to isolate persistent-state changes without changing the source experience. - Proposes a stage-evidence ladder that preserves the distinct inferential semantics of heterogeneous measurements (write distance, exposure rate, action TV, endpoint contrast), avoiding spurious scalar “transport efficiency” scores. - Separates forced fixed-evidence “capacity” from native transport, enabling a principled diagnosis that avoids concluding “memory can never matter” from weak native endpoints. - Experimental rigor and validation - Uses paired designs, permutation/sign-flip …",
          "decision_changing_concern": "- Technical limitations or concerns - The write intervention is a bundled protocol change (instruction + outcome semantics), not a pure reward-bit manipulation; atom-level causal attribution is thus unresolved. - Native exposure is measured at the source-item level, not at the “treatment-residual” level; it remains unknown whether the branch-differentiating content enters the policy’s effective readout. - Uptake is probed only at the first structured action; later-step or plan-level differences could exist but are not assessed. - Experimental gaps or methodological issues - Limited domains and sample sizes for downstream transport (36 Shopping states; Reddit lacks matched exposure/uptake pr…",
          "reviewer_question": "1. How exactly is native retrieval implemented and scored (embedding model, indexing, k, reranking, rank thresholds), and how sensitive are the exposure and uptake results to these choices and to retrieval budget k? 2. Can you report retrieval rank distributions for the source-item exposure across branches and analyze whether lower ranks correlate with weaker uptake or endpoints? 3. Did you control for or analyze interference from other items in the memory bank (e.g., competition from similar items or cross-branch contamination) when measuring exposure and uptake? 4. Beyond the first action, did you assess second-step or plan-level divergences (e.g., action sequences, tool call chains, plan…"
        },
        "token_fingerprint_sha256_16": "c277515d89920ce3"
      }
    },
    {
      "paper_id": "G1",
      "order": 4,
      "title": "Separating Capability Unlock from Safety Drift in Persistent Browser Agents",
      "paper_status": "PDF_READY",
      "pages": 6,
      "pdf_sha256": "4e9059f1f14fcb92c2b5911d4f90df40fc36e3d376ef8694eec3902acf800314",
      "pdf": "downloads/advisor-20260906/04-G1-MCTA.pdf",
      "paper_candidate_ref": "origin/paper/g1-mcta-paper-iteration-20260904@236d4efe",
      "scientific_canonical_ref": "origin/main@bb9b99d915de1141ac39654550dd91f81070ee00",
      "science_delta": "Preconfirmatory MCTA manuscript: future safety outcome remains prospective.",
      "best_case": "在安全干预改变 task-local capability 时，用 shared-capability witness 把“更安全”与“只是不会/拒绝做任务”分开，再比较 Updated vs Frozen 的纵向安全变化。",
      "advisor_question": "capability-matched safety evaluation 是足够强的 methodology problem，还是应收窄成特定 web-agent evaluation protocol？",
      "stanford": {
        "status": "READY",
        "numerical_score": 4.8,
        "textual_signal": "CRITICAL",
        "review_date": "2026-09-05T09:11:12.602100",
        "advisor_digest": {
          "strongest_positive": "- Technical novelty and innovation - Introduces a clear task-local capability witness (benign twin completion + shared graph coverage) that separates refusal from inability, addressing a central confound in longitudinal agent safety. - Proposes a principled shared-capability gate S(u,t) and analyzes R0/R1/R2/R3 endpoints to decompose behavioral shifts, focusing prospectively on R1 as the primary endpoint. - Designs an Updated-vs-Frozen, same-schedule longitudinal identification with a balanced incomplete block assignment and pre-declared support criteria, minimizing researcher degrees of freedom in analysis. - Adds a thoughtful “length/structure” placebo to disentangle semantic workflow upd…",
          "decision_changing_concern": "- Technical limitations or concerns - Conditioning on post-treatment capability (C=1) necessarily induces selection; while the paper acknowledges this and frames claims narrowly, the causal interpretation remains limited to a “shared-capability subset,” not a general causal effect. - The canonical shared action graph is assumed acyclic and frozen; many web tasks allow alternate valid paths, optional loops, or branching. The protocol lacks detail on how to handle multiple feasible paths, cycles, or re-planning while avoiding bias. - The capability witness requires “full shared-graph coverage,” which risks penalizing benignly extraneous but harmless interactions or valid alternative orderings…",
          "reviewer_question": "1. How are canonical shared action graphs derived and validated? Do you have a protocol for inter-annotator reliability, alternative-path handling, and allowable deviations (e.g., optional fields, retries) without overfitting the graph to one path? 2. Many web workflows are not acyclic in practice. Why enforce DAGs, and how would you extend MCTA to graphs with cycles or conditional branches? 3. How do you define the “authorized benign twin” concretely for each harmful task to ensure it exercises precisely the same primitives/transitions? Can you provide specific examples and release templates? 4. What is your plan for uncertainty quantification on the P1 contrast (e.g., CIs, randomization i…"
        },
        "token_fingerprint_sha256_16": "e2b0424889948002"
      }
    },
    {
      "paper_id": "E2",
      "order": 5,
      "title": "Same Evidence, Different Skill: State Regeneration Instability in Self-Evolving Agents",
      "paper_status": "PDF_READY",
      "pages": 16,
      "pdf_sha256": "6194ac7a97a34bdb7f21c36ed2fa5b6f14c4c7184007d5418c643ff11b1c3f15",
      "pdf": "downloads/advisor-20260906/05-E2-State-Regeneration.pdf",
      "paper_candidate_ref": "origin/research/e2-r17-manuscript-state-generation-20260903@19d56a54",
      "scientific_canonical_ref": "origin/main@bb9b99d915de1141ac39654550dd91f81070ee00",
      "science_delta": "Typed compiler bridge remains prospective where explicitly stated; no unobserved V3/V4 outcome inferred.",
      "best_case": "同一 evidence package 可以生成不同 persistent state；把 state generation 本身从 evidence selection 中分离出来，审计 self-evolution 的 regeneration instability。",
      "advisor_question": "“acting/serving evidence → persistent state”中的 generator-factor instability 是否是现实 self-evolving agent 的核心问题，正确 abstraction 应落在哪个 community vocabulary？",
      "stanford": {
        "status": "READY",
        "numerical_score": 5.4,
        "textual_signal": "MIXED_POSITIVE",
        "review_date": "2026-09-05T09:13:09.203935",
        "advisor_digest": {
          "strongest_positive": "- Technical novelty and innovation - The paper isolates the state-generation step itself (G) as an experimental variable, decoupling evidence selection (E) from state realization (S), and identifies a state-regeneration instability phenomenon. - The proposed SHA-based state identity handling, repeated frozen-state audits, and prospective generator-factor bridge are methodologically careful and novel in the agent self-evolution literature. - The typed compiler intervention is deliberately modest yet conceptually useful to constrain degrees of freedom in state materialization under matched evidence. - Experimental rigor and validation - Thorough bookkeeping with content-addressed artifacts (s…",
          "decision_changing_concern": "- Technical limitations or concerns - The strongest empirical evidence is a selected-case anomaly; key prospective tests (M3R4 localization, M4 balanced bridge) are not executed yet, so the central generator-factor claim remains unproven. - The typed compiler currently uses a very small, spreadsheet-specific repair vocabulary; the causal mechanism behind any potential gains (if later observed) may primarily reflect hygiene and scope control rather than semantic diagnosis. - Reliance on a single backbone (DeepSeek-V4-Pro) and a private, controlled suite limits generality; no variance decomposition is quantified to separate generator vs. actor variance at population scale. - Experimental gaps…",
          "reviewer_question": "1. How much of the observed same-evidence disagreement do you attribute to decoding non-determinism (e.g., missing seeds) versus true model variability? Can you fix or log seeds end-to-end to narrow this? 2. In the 48-pair study, did you analyze moderators (e.g., task family, evidence length, success/failure density) that might explain heterogeneity? Any insights that inform the First-Fail anomaly? 3. Can you report descriptive differences between the historical strong state and the two regenerated states (length, clause inventory, ordering, specificity) to concretize the instability? 4. For M3R4, what practical diagnostics will you use to assess the iid/stationarity and cross-task factoriz…"
        },
        "token_fingerprint_sha256_16": "31104be789d9f7cf"
      }
    },
    {
      "paper_id": "PAPER_A",
      "order": 6,
      "title": "From Memory Influence to Source Fidelity: A Causal Audit of Failure-Derived Memory in Embodied Agents",
      "paper_status": "ADVISOR_DRAFT_PRECONFIRMATORY",
      "pages": 3,
      "pdf_sha256": "11716be6f78402b26a4e17067b9d902e58346bf86d25e3928b95ce63b3c553c9",
      "pdf": "downloads/advisor-20260906/06-Paper-A-Influence-Fidelity.pdf",
      "paper_candidate_ref": "paper/embodied-memory-plans-20260904@dda11db4 + generated preconfirmatory advisor draft",
      "scientific_canonical_ref": "origin/main@bb9b99d915de1141ac39654550dd91f81070ee00",
      "science_delta": "Decisive native closed-loop P0/P1/P2 outcomes remain prospective; current carrier evidence only.",
      "best_case": "从“memory 会影响动作”推进到“这种影响是否忠实追随 source experience”，用 no-op / unrelated / same-content provenance controls 做 causal fidelity audit。",
      "advisor_question": "Influence–Fidelity 是否应该独立成 embodied-memory identification paper，还是作为 B1/Paper B 的机制证据更合适？",
      "stanford": {
        "status": "READY",
        "numerical_score": 5.7,
        "textual_signal": "MIXED_POSITIVE",
        "review_date": "2026-09-05T09:21:59.889611",
        "advisor_digest": {
          "strongest_positive": "- Technical novelty and innovation - Separates the often-conflated notions of memory influence and source fidelity, proposing a principled identification standard with matched controls (no-op/serialization, unrelated-content, and same-content/different-provenance). - Introduces hard-stop decision rules that guard against common pitfalls (e.g., attributing utility to interface sensitivity or generic perturbations), encouraging cleaner causal interpretations. - Prospective, outcome-blind design that emphasizes frozen interfaces, pre-specified units, and programmatic fidelity signatures constructed from state/action/kinematics without target-outcome leakage. - Experimental rigor and validation…",
          "decision_changing_concern": "- Technical limitations or concerns - The paper reports no completed confirmatory experiments; the central claims (that the audit can reliably distinguish source fidelity from generic influence) remain prospective. - Definitions of key constructs (e.g., “programmatic source-fidelity signature,” “source-consistent direction,” “same-content/different-provenance”) are described at a high level but lack formal operationalization and concrete examples. - Carrier-bounded scope (MemoryVLA/LIBERO-Plus) limits generality; the protocol may behave differently with other memory substrates (e.g., learned embedding memories vs textual scratchpads, hierarchical scene/episodic banks). - Experimental gaps o…",
          "reviewer_question": "1. How exactly is the “programmatic source-fidelity signature” computed? Please provide concrete examples for at least two tasks, including the predicates on state/action logs and how an induced source-level outcome flip deterministically flips the signature. 2. What are the primary quantitative endpoints for RQ1–RQ3 (e.g., action KL, trajectory deviation metrics, subgoal predicate flips) and what are the pre-specified decision thresholds and statistical tests (permutation/randomization, paired tests) you plan to use? 3. How do you ensure “same-condition replay” under stochastic policies and non-deterministic simulators? Will you fix random seeds, control action sampling temperature, or use…"
        },
        "token_fingerprint_sha256_16": "72f8cb12c0806023"
      }
    },
    {
      "paper_id": "CONSTRAINT_EXTERNALITY",
      "order": 7,
      "title": "Agent Constraint Externality",
      "paper_status": "PDF_READY",
      "pages": 8,
      "pdf_sha256": "f107dbff4c9126ad71bd376b2a33374ee2b9e54f195a1a1dda991a1b5658fa8b",
      "pdf": "downloads/advisor-20260906/07-Constraint-Externality.pdf",
      "paper_candidate_ref": "origin/main paper_drafts/agent-constraint-externality-iclr2027/main.pdf@c3b9db68",
      "scientific_canonical_ref": "origin/main@bb9b99d915de1141ac39654550dd91f81070ee00",
      "science_delta": "Sep5 readiness/provider-gate updates postdate the PDF; scientific execution remains gated.",
      "best_case": "同一个局部 repair 在保持 target gain 时可能对非目标约束产生 collateral regression；用 matched UPDATE/NO_UPDATE 和预声明 coupling topology 分离这种外部性。",
      "advisor_question": "constraint externality 的核心贡献更应该是 measurement、prediction 还是 mitigation/control？",
      "stanford": {
        "status": "READY",
        "numerical_score": 6.2,
        "textual_signal": "MIXED_POSITIVE",
        "review_date": "2026-09-05T09:13:11.948903",
        "advisor_digest": {
          "strongest_positive": "- Technical novelty and innovation - Introduces a clearly defined estimand for update-attributable collateral regression (UE), separating target repair uptake from non-target regressions under matched UPDATE/NO_UPDATE replays. - Proposes a same-update matched-topology design (INDEPENDENT/LOW/HIGH) to causally probe structural coupling effects while freezing the exact repair bytes and pre-update snapshot. - Enforces outcome-blind graph construction restricted to declared resource/prerequisite edges, avoiding post hoc leakage from outcomes into structure. - Presents a minimal, preregistered prospective ranking (ExposureRank) and a simple mitigation (GTCC) contingent on mechanism confirmation,…",
          "decision_changing_concern": "- Technical limitations or concerns - No confirmatory evidence of the core phenomenon (positive UE) or of topology moderation (Δtopo) is available; the paper is largely a preregistered protocol without executed results. - The “repair writer” component is underspecified (how repairs are generated, constrained, and validated as target-local only); without this, construct validity is at risk. - Stochasticity control is mentioned (same snapshot/seed policy) but not fully elaborated (e.g., multi-run variance estimation, confidence intervals, equivalence tests, or power analysis). - ExposureRank is a hand-crafted heuristic; absent empirical validation, its prospective value and calibration remain…",
          "reviewer_question": "1. How is the repair writer implemented and constrained to ensure strict target-locality (e.g., interfaces, redactions, provenance checks) and to prevent leakage of non-target outcomes into the repair content? 2. What is the concrete operationalization of INDEPENDENT/LOW/HIGH coupling, and what quantitative manipulation checks will you report to verify that these arms differ only in structural coupling? 3. What is your statistical analysis plan (paired tests, confidence intervals, variance modeling) and power analysis (n families, r repeats, minimum detectable UE and Δtopo) for both phenomenon detection and mechanism contrasts? 4. How will stochasticity be handled beyond single matched seed…"
        },
        "token_fingerprint_sha256_16": "55b1bcd5772015d6"
      }
    },
    {
      "paper_id": "PAPER_B",
      "order": 8,
      "title": "When Does an Embodied Agent Actually Self-Evolve? Causal Identification of Persistent Memory Across Episodes",
      "paper_status": "ADVISOR_DRAFT_PRECONFIRMATORY",
      "pages": 3,
      "pdf_sha256": "deee83f4e6d033ec9b5a09d63910c0566e8f8d1c8e9aa6ea9d5983ae8bc6ca68",
      "pdf": "downloads/advisor-20260906/08-Paper-B-Persistent-Memory.pdf",
      "paper_candidate_ref": "paper/embodied-memory-plans-20260904@dda11db4 + generated preconfirmatory advisor draft",
      "scientific_canonical_ref": "origin/main@bb9b99d915de1141ac39654550dd91f81070ee00",
      "science_delta": "Longitudinal committed-update vs frozen-preupdate confirmatory outcome remains prospective.",
      "best_case": "用 exact persistent-state fork（Committed-Update vs Frozen-Preupdate）和 source/verification/future 分离，定义真正跨 episode 的 embodied self-evolution。",
      "advisor_question": "persistent embodied memory 的 longitudinal identification 是否值得作为独立主 paper，还是应与 Paper A 合并成一个完整 causal story？",
      "stanford": {
        "status": "READY",
        "numerical_score": 5.6,
        "textual_signal": "MIXED_POSITIVE",
        "review_date": "2026-09-05T09:23:10.539248",
        "advisor_digest": {
          "strongest_positive": "- Technical novelty and innovation - Introduces a clear identification standard for persistent memory that isolates the effect of a single committed update relative to a matched frozen pre‑update state, avoiding the confound of resetting entire memory histories. - Treats native retrieval as part of the total effect (akin to intention‑to‑treat), avoiding post‑hoc “rescues” via manual injection and thereby preventing optimistic bias. - Defines disjoint source/verification/future roles and exact object identity for the committed memory, reducing label leakage and post‑selection artifacts. - Explicitly distinguishes the causal object (persistent state fork) from commonly used but weaker control…",
          "decision_changing_concern": "- Technical limitations or concerns - Lacks a formal causal model (e.g., potential outcomes/SCM) specifying assumptions (SUTVA variants, interference across episodes, ignorability/randomization) and estimands beyond “total effect,” limiting theoretical clarity. - “Exact persistent‑state fork” is under‑specified for non‑deterministic components (e.g., stochastic policies, nondeterministic simulators, async memory services); reproducibility of the forked branches is not fully addressed. - “Exact committed‑object identity” is mentioned but the operational definition and integrity checks (hashing, serialization, versioning under compression) are not detailed. - Counting retrieval failures in th…",
          "reviewer_question": "1. Can you formalize the causal estimands (e.g., in potential outcomes/SCM terms) and list the identification assumptions explicitly, including how you address interference across episodes and environment stochasticity? 2. What is the unit of randomization and analysis—per source–verification–future stream, per environment/task family, or per agent checkpoint? How will you handle clustering and variance estimation? 3. How will you ensure an “exact persistent‑state fork” in practice (e.g., deterministic simulator snapshots, fixed RNG seeds, identical action sampling temperatures), and how will you audit “exact committed‑object identity” (hashing, immutable IDs)? 4. What is your planned power…"
        },
        "token_fingerprint_sha256_16": "08011461988e7036"
      }
    },
    {
      "paper_id": "3D",
      "order": 9,
      "title": "Beyond Relation Count: Endpoint-Sharing Topology in Text-Guided 3D Scene Generation",
      "paper_status": "ADVISOR_DRAFT_PRECONFIRMATORY",
      "pages": 3,
      "pdf_sha256": "76909e7572849dca55aca38f2cc5488462a74d3262b19d7669c24465173bcf1f",
      "pdf": "downloads/advisor-20260906/09-3D-Relational-Topology.pdf",
      "paper_candidate_ref": "origin/research/relational-topology-stage-3d-runtime-20260905@bb9b99d9 + generated preconfirmatory advisor draft",
      "scientific_canonical_ref": "origin/main@bb9b99d915de1141ac39654550dd91f81070ee00",
      "science_delta": "Primary SGP-14 training/untouched-test topology evidence remains prospective; development evidence is not paper evidence.",
      "best_case": "在 relation count、对象、谓词和 decoder 全部匹配时，只改变 Chain/Hub endpoint-sharing topology，再用 oracle-graph substitution 定位 Text→Graph 与 Graph→Scene bottleneck。",
      "advisor_question": "relation topology 是真实 3D instruction complexity 的关键变量，还是 controlled benchmark 中才突出的分析轴？",
      "stanford": {
        "status": "READY",
        "numerical_score": 4.1,
        "textual_signal": "CRITICAL",
        "review_date": "2026-09-05T09:24:03.199789",
        "advisor_digest": {
          "strongest_positive": "- Technical novelty and innovation - The Chain/Hub counterfactual design under strict count/predicate/object/tokenization matching is a crisp way to isolate topology from relation count—an aspect often conflated in prior evaluations. - The exact-identity oracle graph substitution, run under identical decoder randomness, is a clean stage-localization tool to attribute residuals to text-to-graph vs. graph-to-scene. - The preregistered GO/STOP gates, frozen compiler, and cluster bootstrap plan indicate commendable attention to experimental hygiene and reproducibility. - Experimental rigor and validation - The authors predefine a primary estimand (Δ_topo = mean(iRecall_Hub − iRecall_Chain)), pl…",
          "decision_changing_concern": "- Technical limitations or concerns - No empirical results are provided: the core claims remain untested at submission time, making it impossible to assess correctness, magnitude, or robustness of the purported effects. - The study currently targets a single decoder substrate and a narrow predicate set (behind, right_of), limiting external validity even if effects are later observed. - Hub/Chain difficulty could be confounded by object salience, centrality biases, or lexical/coreference artifacts in the instructions; controls for these are not yet demonstrated empirically. - Experimental gaps or methodological issues - Power analysis and expected effect sizes are not presented; the smallish…",
          "reviewer_question": "1. What is your expected effect size for Δ_topo at counts 3 and 4, and what power analysis supports the current panel sizes for validation and test? 2. How do you ensure that Hub vs. Chain instructions are matched in lexical complexity and coreference load (e.g., repeated mention of the hub object) so that parsing difficulty is not confounded with topology? 3. Are hub objects balanced across classes, sizes, and salience (e.g., large furniture vs. small decor) to avoid centrality and collision biases? 4. Which full set of predicates will be included beyond behind and right_of, and how will you handle anti-symmetric or transitive implications that may differ across topologies even with matche…"
        },
        "token_fingerprint_sha256_16": "13e0eceaadad19de"
      }
    }
  ],
  "shared_risks": [
    {
      "id": "persistent-memory-object",
      "label": "Persistent-memory object / state semantics",
      "papers": [
        "B1",
        "C1",
        "E2",
        "PAPER_A",
        "PAPER_B"
      ],
      "question": "这些论文是否共享了一个未经充分验证的 persistent-state / memory semantics 前提？一个 closure 是否能同时给多篇降风险？"
    },
    {
      "id": "provenance-fidelity",
      "label": "Provenance / source-fidelity distinction",
      "papers": [
        "B1",
        "PAPER_A",
        "PAPER_B"
      ],
      "question": "provenance、source fidelity 与 longitudinal persistent utility 是否应拆成三篇，还是应形成 parent-child / merge 结构？"
    },
    {
      "id": "controlled-update",
      "label": "Controlled update and capability preservation",
      "papers": [
        "G1",
        "CONSTRAINT_EXTERNALITY"
      ],
      "question": "安全 capability confound 与 update collateral 是否共享一个更高层 controlled-update scientific object？"
    },
    {
      "id": "representation-support",
      "label": "Representation / identity support",
      "papers": [
        "E1",
        "E2",
        "C1"
      ],
      "question": "identity/representation changes 是否只是各自 substrate artifact，还是 self-evolution control surface 的共同系统问题？"
    }
  ],
  "schedule": [
    {
      "start": "14:00",
      "end": "14:15",
      "label": "Portfolio Dashboard + Common-Cause Risk Scan"
    },
    {
      "start": "14:15",
      "end": "14:40",
      "label": "E1"
    },
    {
      "start": "14:40",
      "end": "15:30",
      "label": "Memory / Provenance / Evolution family"
    },
    {
      "start": "15:30",
      "end": "15:55",
      "label": "G1 + Constraint Externality"
    },
    {
      "start": "15:55",
      "end": "16:10",
      "label": "3D"
    },
    {
      "start": "16:10",
      "end": "16:35",
      "label": "Exception-based nine-paper closure sweep"
    },
    {
      "start": "16:35",
      "end": "16:53",
      "label": "Cost / Dependencies / Scheduling"
    },
    {
      "start": "16:53",
      "end": "17:00",
      "label": "Read-back"
    }
  ]
};
