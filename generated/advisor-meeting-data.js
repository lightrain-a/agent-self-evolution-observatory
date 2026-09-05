window.ADVISOR_MEETING_DATA = {
  "schema_version": "3.2",
  "generated_at": "2026-09-06",
  "meeting": {
    "id": "2026-09-06-advisor",
    "main_ref": "bb9b99d915de1141ac39654550dd91f81070ee00",
    "status": "9_OF_9_READY",
    "review_route": "exception-and-boundary-review",
    "freeze_status": "MEETING_CANDIDATE_FROZEN",
    "candidate_hash": "58e21fc579519a0110bf802bf5f83f21391092360ef9b3475c93b5f2fbd2de81"
  },
  "route_summary": {
    "FREEZE_SUBMIT": 3,
    "EXECUTE_FROZEN": 2,
    "QUALIFY_FIRST": 2,
    "FORMALIZE_FIRST": 2
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
      "route": "FREEZE_SUBMIT",
      "best_case": "用精确证书刻画：语义等价的 skill 打包/身份不应改变实际可访问的技能控制面，并定位 finite-budget access 下的表示不稳定。",
      "story": "语义 capability 没变时，仅改变 skill package 的拆分、身份或重叠表示，就可能改变 agent 实际拿到的 capability；STRI 给出这种表示依赖何时无法靠 package-only weighting 消掉的精确边界。",
      "premise": "现实 self-evolving skill system 确实把 package identity 当作控制单元，并且 finite access budget、priority 或 overlap 足够常见，使 representation invariance 成为真实系统属性而非只在构造例子中成立。",
      "risk": "运行时 semantic projection φ(E_t) 在不同系统里的实例化仍偏抽象；动态行为传播目前只有一个 AutoSkill P19 bounded witness，不能把 access-level invariance 自动升级成普遍 utility/safety 影响。",
      "strongest_simplification": "先用 exact-semantic quotient、whole-package pruning、uniform/optimal package weights 和 capacity+1 对照。若这些简单 same-information controls 已消掉现象，就不需要额外修复方法故事。",
      "evidence_state": "CURRENT CLAIM SCIENCE CLOSED：Skill-SP support geometry 含 R*=2 residual/equalizable regimes；SkillRL fresh-ID × finite-budget identity sensitivity；AutoSkill P19 有 bounded representation→access→behavior mediator witness；held-out behavior propagation 按冻结门 STOP。",
      "next_closure": "当前 narrow paper 不需要新增 scientific closure。周日只需决定：保持冻结直接进入 human submission，还是把 non-clone repeated-access V4 作为一份完全独立的 claim-expansion contract。",
      "cost_class": "ZERO_REQUIRED / OPTIONAL_MEDIUM",
      "cost_to_next_decision": "当前论文：0 新 model/GPU。若师兄明确打开 V4，第一道门只做约 12–24 个 hosted-agent P0 trajectories；后续 P1/P2/P3 均 conditional。",
      "dependencies": [
        "human author/OpenReview signoff",
        "optional V4 needs a genuinely repeated-access, non-clone substrate"
      ],
      "default_action": "FREEZE_AND_SUBMIT_NARROW",
      "override_trigger": "只有师兄认为 package-identity abstraction 在真实 skill ecosystem 中缺乏意义，或明确授权一个与当前投稿解耦的 V4 扩展，才改变默认路线。",
      "cross_paper_leverage": "可为 E2/C1 提供 representation/state identity 不是中性工程细节的系统级语言，但不需要与它们合并。",
      "advisor_question": "这个 abstraction 在真实 Agent skill ecosystem 中是否足够常见、足够重要，值得 standalone paper？",
      "reality_support": {
        "reality_verdict": "SUPPORTED_WITH_BOUNDARY",
        "supporting_cases": [
          {
            "title": "SkillZip: Evaluation-Free Skill Compression for Self-Evolving Agents",
            "url": "https://arxiv.org/abs/2608.11079",
            "why": "Explicitly models self-evolving agents that continually accumulate reusable skills and failure fixes; supports the premise that skill libraries grow and need maintenance."
          },
          {
            "title": "SkillZip Pro: Execution-Aware Dynamic Compression of Progressively Loaded Skills",
            "url": "https://arxiv.org/abs/2608.30785",
            "why": "Treats production skills as directory bundles with progressive loading and routing boundaries; directly supports selective access to parts of a skill bundle rather than loading everything."
          },
          {
            "title": "HyperSkill: Self-Evolving LLM Agents via Hypergraph-Structured Skill Memory",
            "url": "https://arxiv.org/abs/2608.16114",
            "why": "Uses structured skill memory, retrieval ranking, pruning, and merging; supports dynamic skill-memory organization and finite retrieval as real system operations."
          }
        ],
        "what_this_does_not_prove": "These systems establish dynamic skill libraries, routing, retrieval, and maintenance; they do not establish that package identity or finite access budget causes the specific STRI instability observed in E1.",
        "strongest_escape": "Semantic deduplication/canonical IDs or semantic-first retrieval may make package identity largely irrelevant in well-designed systems."
      },
      "resource_plan": {
        "authorized_now": {
          "cash_cny": 0,
          "gpu": "0",
          "api_units": 0,
          "work": "human paper/signoff only"
        },
        "resource_dimensions": {
          "api_cash": "¥0",
          "local_gpu_occupancy": "0",
          "human_time": "1–3 h",
          "provider_credential_dependency": "N/A",
          "calendar_latency": "human signoff only; not compute-bound"
        },
        "next_if_pass": "None for the narrow paper. Optional V4 only if explicitly opened by advisor/human authority.",
        "conditional_envelope": "Optional V4 first gate: approximately 12–24 hosted-agent trajectories; later stages remain conditional.",
        "human_effort_estimate": "1–3 h advisor/author positioning + submission signoff",
        "parallelization": "Fully parallel; no scarce compute dependency.",
        "priority_note": "High scheduling priority because closure is cheap and submission-near."
      },
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
        "token_fingerprint_sha256_16": "6bc64d7089d84ab4",
        "reviewed_pdf_sha256": "cb09d2dd54a5b59725bcda9895be3ccfa668d274d09d027761c518a38865c9e1",
        "exact_current_pdf": true
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
      "route": "EXECUTE_FROZEN",
      "best_case": "在 retrieved content/order 固定时，审计显式 source-outcome/provenance 信息到底改变多少局部动作与终端结果，并进一步定位 executor-specific decision geometry。",
      "story": "同一条 memory 内容不变，只改变 executor 能否看到真实 source outcome；B1 问这个 provenance channel 是否提供 content 之外的增量决策信息，以及这种影响为什么只在部分 executor/task 边界出现。",
      "premise": "source provenance 是 content 之外可被 agent 使用的独立信息通道，而不是 field-format、implicit failure wording 或模型能力边界造成的 prompt sensitivity。",
      "risk": "terminal discordance 稀疏且明显 executor-specific；若完整 semantic controls 后差异主要由 prompt surface 或小模型 decision boundary 解释，standalone provenance claim 会明显收窄，并可能被 Paper A 吸收。",
      "strongest_simplification": "同结构字段的 P_neutral / T_truthful / S_shuffled 三臂是当前 strongest same-information control；若 shuffled/neutral 能解释 truthful 差异，则语义 provenance 使用不成立。",
      "evidence_state": "R76：历史 Llama 4 个 terminal flips 在 temperature=0 exact rerun 下 4/4 复现；R77：其中 2 个表现为 same-state decision-boundary shift，另 2 个更依赖 transcript/self-conditioning；相同 4 个 task 在 Qwen 上均 concordant。最新 R81 仅授予 Qwen stage execution authority：189 trajectories、P/T/S 三臂、no interim scientific analysis；Llama、analysis、claim change、strong-model execution 均关闭。R80 已 outcome-blind 冻结 future scale model Qwen2.5-32B-Instruct 及 4D matched-control rule，但当前不授权下载/执行。",
      "next_closure": "当前只完成 sealed Qwen 189。Qwen stage seal 后，若执行完整性通过，再单独申请 Llama 132 successor authority；两阶段都 seal 后才生成 P/T discordance classification 并另开 analysis authority。Future Qwen2.5-32B scale check 只按两 executor 的 union discordant 数 D 触发 4D，且仍需独立下载/执行 authority。",
      "cost_class": "MEDIUM · ALREADY_RUNNING",
      "cost_to_next_decision": "眼前只计 Qwen 189：本地 A100/open-weight 推理，直接 API cash≈0；主成本是 A100 占用与 Qwen stage wall-time。Llama 132 和 future 4D strong-scale check 都不是当前已授权成本。当前 Qwen execution 已启动，不能因中间结果改 schedule。",
      "dependencies": [
        "path-equivalent clean MemRL checkout pinned to c1b322ca…",
        "local Qwen2.5-7B runtime for current stage",
        "Qwen stage seal before any Llama authority",
        "separate Llama successor authority",
        "separate post-seal analysis authority"
      ],
      "default_action": "COMPLETE_QWEN_189_ONLY_NO_INTERIM_ANALYSIS",
      "override_trigger": "若执行完整性或 technical seal 失败则 fail closed；若最终 semantic-control 结果不支持独立 provenance 信息价值，或师兄判断与 Paper A scientific object 重叠过高，再考虑 merge/narrow。",
      "cross_paper_leverage": "与 Paper A 共用 provenance/source-fidelity 边界；B1 可提供数字 Agent 上的 format/provenance control 经验，Paper A 必须避免重复造同一 scientific object。",
      "advisor_question": "在 executor-specific、terminal effect 稀疏的边界下，provenance audit 是否仍值得 standalone，还是应成为 Paper A 的数字-Agent机制证据？",
      "reality_support": {
        "reality_verdict": "SUPPORTED_WITH_BOUNDARY",
        "supporting_cases": [
          {
            "title": "From Agent Traces to Trust: Evidence Tracing and Execution Provenance in LLM Agents",
            "url": "https://arxiv.org/abs/2606.04990",
            "why": "Explicitly argues that evidence and execution provenance, including provenance-bearing memory, are needed to explain how memory influenced later decisions."
          },
          {
            "title": "MemoryArena: Benchmarking Agent Memory in Interdependent Multi-Session Agentic Tasks",
            "url": "https://arxiv.org/abs/2602.16313",
            "why": "Implements memory-agent-environment loops where actions, observations, feedback, and memory are reused across sessions; supports provenance-bearing historical context as a realistic object."
          },
          {
            "title": "Agentic Memory: Learning Unified Long-Term and Short-Term Memory Management",
            "url": "https://aclanthology.org/2026.acl-long.981/",
            "why": "Lets an agent actively store, retrieve, update, summarize, and discard memory, supporting memory metadata/control as a real decision surface."
          }
        ],
        "what_this_does_not_prove": "Prior work supports provenance and memory-management relevance, not that an explicit truthful source-outcome field has standalone terminal value beyond identical content.",
        "strongest_escape": "Observed action shifts may be explained by prompt-surface sensitivity, implicit failure wording already present in memory text, or executor-specific decision boundaries."
      },
      "resource_plan": {
        "authorized_now": {
          "cash_cny": 0,
          "gpu": "1×A100-80GB local",
          "api_units": 0,
          "work": "Qwen semantic-control stage, 189 trajectories"
        },
        "resource_dimensions": {
          "api_cash": "¥0",
          "local_gpu_occupancy": "1×A100-80GB; frozen Qwen 189 stage",
          "human_time": "<1 h active monitoring",
          "provider_credential_dependency": "N/A",
          "calendar_latency": "roughly 6.4 h remaining at the 22:55 observed average; operational estimate only; throughput-sensitive"
        },
        "operational_snapshot": {
          "observed_at": "2026-09-05T22:55:00+08:00",
          "completed_trajectories": 39,
          "target_trajectories": 189,
          "elapsed_seconds": 5948,
          "rough_remaining_hours_if_current_average_holds": 6.4,
          "note": "Operational estimate only; no interim scientific analysis. Remaining-time estimates are throughput-sensitive and may move non-monotonically."
        },
        "next_if_pass": "Llama 132 trajectories require separate successor authority after Qwen stage seal.",
        "conditional_envelope": "After Qwen+Llama seals, analysis authority is separate. Strong-scale Qwen2.5-32B check is 4D only if future discordant-task count D is nonzero and separately authorized.",
        "human_effort_estimate": "<1 h runtime oversight now; later analysis/review is separate",
        "parallelization": "Runs independently from 3D because it uses a different local GPU resource pool.",
        "priority_note": "Do not interrupt: frozen experiment is already running and has a short remaining wall-time relative to other compute work."
      },
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
        "token_fingerprint_sha256_16": "baab94e480450fbc",
        "reviewed_pdf_sha256": "7337d7eaf2edbb21673ec147af37d55a36693ed71b17cd1c99ba09a4d96ef957",
        "exact_current_pdf": true
      }
    },
    {
      "paper_id": "C1",
      "order": 3,
      "title": "From Feedback to Memory to Behavior: How Persistent Differences Are Written and Where Native Transport Breaks",
      "paper_status": "PDF_READY",
      "pages": 14,
      "pdf_sha256": "fb09cbb4811b7350097f7c4659aa08238105076197e9ed487524cb6d75dee937",
      "pdf": "downloads/advisor-20260906/03-C1-Stage-Resolved-Memory-Transport.pdf",
      "paper_candidate_ref": "C1 unified feedback→persistent-state→native-transport meeting candidate rebuilt 2026-09-06",
      "scientific_canonical_ref": "origin/main@bb9b99d915de1141ac39654550dd91f81070ee00",
      "science_delta": "Unified framing now integrates the old feedback-to-state result with the stage-resolved native-transport result; later collision/noise-floor diagnostics remain separate unless explicitly integrated.",
      "route": "FREEZE_SUBMIT",
      "best_case": "同一 source experience 经不同 feedback-conditioned writer branch 会被写成不同 persistent state；这些差异在 forced exposure 下有行为杠杆，但在 native exposure → uptake → outcome 链路中不一定传成稳定行为差异。",
      "story": "C1 是一条完整的 feedback → persistent state → behavior 链：第一幕解释差异如何被写进 durable memory，第二幕解释已经写入的差异为什么在 deployed native reuse 中不一定获得稳定 behavioral authority。",
      "premise": "feedback-to-state 与 state-to-behavior 是同一个 persistent self-improvement lifecycle 的相邻科学问题；把两者放在同一 controlled lineage 中，比只讲 writer effect 或只讲 stage diagnosis 更能解释“写入强但终端弱”的表面矛盾。",
      "risk": "writer intervention 仍是 bundled protocol change（instruction + outcome semantics），不是 pure reward-bit；native exposure 还是 source-item level，uptake 主要测 first action。因此不能把第一幕写成 atom-level reward causality，也不能把第二幕写成 causal mediation。",
      "strongest_simplification": "统一故事不需要新 method：same-trajectory writer contrast + stronger wording control 回答“怎么写进去”；forced capacity + native exposure/uptake/outcome 回答“为什么不一定传下去”。这是现有证据的最小完整解释。",
      "evidence_state": "CURRENT CLAIM SCIENCE CLOSED：24/24 paired source experiences 写出不同 branch memory；same-mode wording control paired excess 0.105, p=0.0078；forced fixed-evidence 256 rollouts 显示 |Δ|=0.15625, p=0.00074；native Shopping 125/172 exposure，但 first-action TV=0.06944, p=0.5801、0/36 modal changes，terminal |Δ|=0.02083, p=0.4289、34/36 zero。",
      "next_closure": "不新增 provider/GPU 实验。完成 unified-story manuscript convergence；让师兄只判断这条“写进去 + 传不下去”的两幕链是否足够 standalone，以及 bundled writer boundary 是否需要在标题/摘要进一步降噪。",
      "cost_class": "ZERO_REQUIRED",
      "cost_to_next_decision": "0 新 scientific API/GPU；当前只需 manuscript integration、PDF QA 与 human/advisor review。",
      "dependencies": [
        "current frozen feedback-to-state evidence",
        "current frozen stage-resolved transport evidence"
      ],
      "default_action": "FREEZE_UNIFIED_C1_AFTER_MANUSCRIPT_CONVERGENCE",
      "override_trigger": "只有师兄认为 feedback-to-state 与 transport 两幕放在一起反而稀释核心贡献，或发现 decisive closest-work collision，才重新考虑拆 C2；不是因为旧 6.7 分数高就机械拆稿。",
      "cross_paper_leverage": "为 Paper A/B/E2 提供“state creation ≠ native uptake ≠ terminal effect”的 lifecycle vocabulary；但 C1 自己保留完整 feedback→memory→behavior 证据链。",
      "advisor_question": "把“差异怎么写进去”与“写进去以后为什么不一定传得下去”合成一篇 C1，是否比拆成 C1/C2 更完整、更有说服力？",
      "reality_support": {
        "reality_verdict": "SUPPORTED",
        "supporting_cases": [
          {
            "title": "MemoryArena",
            "url": "https://arxiv.org/abs/2602.16313",
            "why": "Directly evaluates whether memory acquired in earlier interaction is used to guide later actions, supporting the need to distinguish memorization from action."
          },
          {
            "title": "MemoryLake on MemoryArena: A Matched Study of Agent Memory Backends",
            "url": "https://arxiv.org/abs/2608.13883",
            "why": "Distinguishes write, retrieval, consolidation, budgeting, and prompt assembly as different but still bundled backend operations; this supports stage-aware concern without claiming that MemoryLake causally isolates those components."
          },
          {
            "title": "From Agent Traces to Trust",
            "url": "https://arxiv.org/abs/2606.04990",
            "why": "Motivates process-level provenance and failure localization rather than final-answer accuracy alone."
          }
        ],
        "what_this_does_not_prove": "These works motivate stage-aware diagnosis but do not prove that C1's exact write→exposure→uptake→endpoint ladder is the uniquely right decomposition or sufficient as a standalone contribution.",
        "strongest_escape": "A simpler end-to-end matched intervention plus forced-exposure diagnostic may answer most practical questions without a full stage taxonomy."
      },
      "resource_plan": {
        "authorized_now": {
          "cash_cny": 0,
          "gpu": "0",
          "api_units": 0,
          "work": "manuscript convergence only"
        },
        "resource_dimensions": {
          "api_cash": "¥0",
          "local_gpu_occupancy": "0",
          "human_time": "2–4 h",
          "provider_credential_dependency": "N/A",
          "calendar_latency": "human/editorial only; not compute-bound"
        },
        "next_if_pass": "No new experiment for the current claim.",
        "conditional_envelope": "Method-extension reopen only with a new independently qualified semantic-validity asset.",
        "human_effort_estimate": "2–4 h manuscript/advisor boundary work",
        "parallelization": "Fully parallel.",
        "priority_note": "Cheap closure; should advance while GPU/API-heavy papers run."
      },
      "stanford": {
        "status": "PRIOR_VERSION",
        "numerical_score": 5.2,
        "textual_signal": "MIXED_POSITIVE",
        "review_date": "2026-09-05T09:10:37.869549",
        "advisor_digest": {
          "strongest_positive": "- Technical novelty and innovation - Introduces a clean, same-trajectory writer intervention (flipping success/failure reflection) to isolate persistent-state changes without changing the source experience. - Proposes a stage-evidence ladder that preserves the distinct inferential semantics of heterogeneous measurements (write distance, exposure rate, action TV, endpoint contrast), avoiding spurious scalar “transport efficiency” scores. - Separates forced fixed-evidence “capacity” from native transport, enabling a principled diagnosis that avoids concluding “memory can never matter” from weak native endpoints. - Experimental rigor and validation - Uses paired designs, permutation/sign-flip …",
          "decision_changing_concern": "- Technical limitations or concerns - The write intervention is a bundled protocol change (instruction + outcome semantics), not a pure reward-bit manipulation; atom-level causal attribution is thus unresolved. - Native exposure is measured at the source-item level, not at the “treatment-residual” level; it remains unknown whether the branch-differentiating content enters the policy’s effective readout. - Uptake is probed only at the first structured action; later-step or plan-level differences could exist but are not assessed. - Experimental gaps or methodological issues - Limited domains and sample sizes for downstream transport (36 Shopping states; Reddit lacks matched exposure/uptake pr…",
          "reviewer_question": "1. How exactly is native retrieval implemented and scored (embedding model, indexing, k, reranking, rank thresholds), and how sensitive are the exposure and uptake results to these choices and to retrieval budget k? 2. Can you report retrieval rank distributions for the source-item exposure across branches and analyze whether lower ranks correlate with weaker uptake or endpoints? 3. Did you control for or analyze interference from other items in the memory bank (e.g., competition from similar items or cross-branch contamination) when measuring exposure and uptake? 4. Beyond the first action, did you assess second-step or plan-level divergences (e.g., action sequences, tool call chains, plan…"
        },
        "token_fingerprint_sha256_16": "c277515d89920ce3",
        "reviewed_pdf_sha256": "a5ce511a11a7781ca5374e0f54f7830454927874ca8dc6112c87e6106ab20167",
        "exact_current_pdf": false,
        "prior_version_note": "External review is for the immediately preceding PDF SHA, not the current meeting candidate."
      }
    },
    {
      "paper_id": "G1",
      "order": 4,
      "title": "Temporal Safety Conclusions Are Evaluator-Relative: A Controlled Audit of Persistent Web Agents",
      "paper_status": "PDF_READY",
      "pages": 11,
      "pdf_sha256": "77d746801d41298e588882821218b2654392243af0c3e9e8a85054212bc17fe0",
      "pdf": "downloads/advisor-20260906/04-G1-ERTA.pdf",
      "paper_candidate_ref": "G1 ERTA R8 exact candidate; same SHA as Stanford submission 2026-08-30",
      "scientific_canonical_ref": "origin/main@bb9b99d915de1141ac39654550dd91f81070ee00",
      "science_delta": "MCTA capability-matching is a separate G2 candidate and remains STOP/HOLD; it is not the next revision of ERTA. ERTA remains the G1 empirical paper.",
      "route": "FREEZE_SUBMIT",
      "best_case": "同一批 persistent-agent trajectories 在 HarmBench 与 DeepSeek 下不仅个别标签不同，还改变 current-pass premise 与 Updated/Frozen/NullMemory 的 temporal ordering；ERTA 把 evaluator identity 从“实现细节”提升为 temporal-safety claim 的显式测量维度。",
      "story": "G1/ERTA 问的是：当 persistent agent 随时间变化时，我们能否把某个自动 evaluator 的 first-violation 轨迹直接当成 evaluator-independent safety conclusion？相同 trajectories 在两个 frozen evaluators 下给出不同 current-pass 与 arm ordering，因此 ERTA 保留 evaluator-indexed vector/envelope 并 fail closed，而不是事后选一个 judge。",
      "premise": "LLM/evaluator choice 是 longitudinal agent-safety measurement 的 load-bearing component；如果同一 completed trajectory 在合理 frozen evaluators 下改变 premise 或 intervention ordering，就必须把 evaluator uncertainty 暴露在 scientific claim 中。",
      "risk": "当前仍是 finite one-backbone BrowserART/AWM case study，主要 derivation 是在观察到 evaluator instability 后形成；缺 blinded human semantic adjudication/更广 evaluator family，且 trace-positive 不等于 externally observed harmful completion。",
      "strongest_simplification": "不要做 MCTA capability matching来“救”G1。最强简单版本就是在 exact same completed trajectories 上分别报告 HarmBench 与 DeepSeek 的 current-pass、event sets 与 contrasts，并让 ERTA 在 disagreement 时返回 measurement-inconclusive。",
      "evidence_state": "ERTA empirical object 已完成：HarmBench 与 DeepSeek 对相同 trajectories 改变 current-pass premise 与三臂 ordering；有 blinded second judge、NullMemory、exact matched-slot analysis 与 prospective held-out ERTA application。当前 paper gate PREBUTTAL，remaining blocker 是 human semantic-label evidence；MCTA 已单独 STOP_PROTOCOL_UNIDENTIFIED_NO_OUTCOMES_OPENED，不是 G1 后续实验。",
      "next_closure": "完成既有 human semantic-label / adjudication evidence 与 prebuttal binding；随后 manuscript convergence + delivery QA。不要再为 G1 启动 MCTA Q0/P0/P1。",
      "cost_class": "HUMAN_ONLY",
      "cost_to_next_decision": "0 新 provider/GPU；下一道判断主要消耗既有 24-item human semantic-label/adjudication工作与 manuscript integration。",
      "dependencies": [
        "frozen ERTA R8 manuscript and exact trajectories",
        "human semantic-label evidence / adjudication packet",
        "prebuttal integration"
      ],
      "default_action": "COMPLETE_HUMAN_SEMANTIC_EVIDENCE_THEN_FREEZE_ERTA",
      "override_trigger": "只有师兄认为 evaluator-relative temporal safety 本身不够 standalone，或 human adjudication 证明两 evaluator 中一方存在明确系统性无效性，才改变 ERTA positioning。MCTA 的成败不得作为 G1 override。",
      "cross_paper_leverage": "给九篇 Research OS 一个更一般的 measurement lesson：judge/evaluator 不应被静默当 ground truth；但它不与 Constraint Externality 合并，也不需要 capability-matching 才成立。",
      "advisor_question": "ERTA 的 evaluator-relative temporal-safety measurement object 是否足够 standalone？当前 human semantic adjudication 做到什么程度就足够投稿，而不需要再扩第三 judge/backbone？",
      "reality_support": {
        "reality_verdict": "STRONGLY_SUPPORTED",
        "supporting_cases": [
          {
            "title": "ST-WebAgentBench",
            "url": "https://arxiv.org/abs/2410.06703",
            "why": "Shows realistic web-agent safety evaluation requires policy-aware measurement beyond task completion, supporting evaluator design as a load-bearing part of the safety conclusion."
          },
          {
            "title": "BrowserART",
            "url": "https://github.com/scaleapi/browser-art",
            "why": "Provides the browser-agent safety substrate used by the frozen study and demonstrates that web-agent safety behavior is evaluated through dedicated safety instrumentation rather than task success alone."
          },
          {
            "title": "Safety in Self-Evolving LLM Agent Systems",
            "url": "https://arxiv.org/abs/2606.23075",
            "why": "Motivates longitudinal safety evaluation under persistent updates, making the stability of the evaluator across time and intervention arms a real scientific concern."
          }
        ],
        "what_this_does_not_prove": "These works motivate longitudinal/policy-aware safety measurement; they do not prove that HarmBench or DeepSeek is semantic ground truth, nor that the exact evaluator reversal observed in G1 generalizes beyond the frozen BrowserART/AWM case.",
        "strongest_escape": "If a prospectively defined human/ground-truth adjudicator showed one frozen evaluator to be clearly invalid on the disagreement strata, the ERTA envelope could be unnecessarily conservative; this is why the human semantic-label closure matters."
      },
      "resource_plan": {
        "authorized_now": {
          "cash_cny": 0,
          "gpu": "0",
          "api_units": 0,
          "work": "human semantic-label/adjudication + manuscript/prebuttal integration only"
        },
        "resource_dimensions": {
          "api_cash": "¥0",
          "local_gpu_occupancy": "0",
          "human_time": "bounded human semantic-label/adjudication + 2–4 h manuscript/prebuttal work",
          "provider_credential_dependency": "N/A for current G1/ERTA",
          "calendar_latency": "human-review bound, not compute-bound"
        },
        "next_if_pass": "Freeze ERTA manuscript after human evidence is integrated; proceed to content convergence and delivery QA.",
        "conditional_envelope": "Any third evaluator, cross-backbone replication, or MCTA capability-matching program is optional/new science and is not required for the current ERTA claim.",
        "human_effort_estimate": "existing 24-item semantic-label/adjudication packet plus manuscript integration",
        "parallelization": "Fully parallel with GPU/API experiments on other papers.",
        "priority_note": "Cheap high-leverage closure; do not spend provider budget on MCTA under the G1 label."
      },
      "stanford": {
        "status": "READY",
        "numerical_score": 6.3,
        "textual_signal": "MIXED_POSITIVE",
        "review_date": "2026-08-30T09:10:34.034124",
        "advisor_digest": {
          "strongest_positive": "- Technical novelty and innovation\n  - Introduces ERTA, a clear, partial-identification style framework for longitudinal agent-safety claims that preserves evaluator-indexed outputs rather than collapsing to a single label.\n  - Formalizes premise stability, event-set envelopes, and contrast-envelope stability; articulates a constructive identification boundary showing why opposite-signed contrasts cannot be resolved without additional assumptions.\n  - Localizes evaluator disagreement by task identity, suggesting structured semantic shifts rather than exchangeable noise.\n- Experimental rigor and validation\n  - Careful controlled audit: updated vs base-workflow arms share matched slots; NullMemory is preregistered with a clean current gate; DeepSeek co-evaluator is blinded to arm/labels and frozen prior to unblinding.\n  - Transparent finite-sample statistics (paired/matched-slot exact tests) and explicit execution-source audit distinguishing trace-level evaluator positives from lack of verified external effects.\n  - Prospective held-out application (new tasks with ERTA fixed) that exercises ERTA’s fail-closed outcome.\n- Clarity of presentation\n  - Clear separation of evaluator-specif",
          "decision_changing_concern": "- Technical limitations or concerns\n  - ERTA is formalized post-hoc in response to observed evaluator instability; while the subsequent held-out application is helpful, the primary derivation evidence remains observational.\n  - The identification argument (Proposition 1) is conceptually correct but informal; a more rigorous treatment (e.g., explicit latent-variable models) would strengthen the theoretical footing.\n- Experimental gaps or methodological issues\n  - Very small N (4 states × 3 branches per arm, H=3); no cross-backbone replication due to infra issues; no human adjudication to arbitrate disagreements or calibrate either judge.\n  - Only two evaluators are considered; no open-source policy-trained guardrails or diverse judge families are included to triangulate the disagreement (e.g., POLICYGUARD, GPT-4o-based judges, or RULERS-style locked rubric evaluators).\n  - Evaluations are over “thought fallback” traces rather than verified external outcomes, which may bias certain evaluators; implications for external harm remain unquantified.\n- Clarity or presentation issues\n  - Some notational slips (e.g., switching between Ae and Δe) and the definition J=1 when both sets are empty could be counterintuitive; more intuition/examples for ERTA objects would help.\n  - Limited detail on evaluator prompts, thresholds, and rubric text impedes external reproducibility beyond content h",
          "reviewer_question": "1. Please provide the exact prompts/rubrics and configurations (including thresholds) used for HarmBench and DeepSeek to facilitate independent reproduction. Were any prompt variants tested, and how sensitive are results to reasonable prompt perturbations?\n2. Can you share concrete example episodes (redacted as needed) from behavior IDs 21/33 where evaluators disagreed, to help diagnose the task-semantic interaction driving NullMemory positives at step 3 under DeepSeek?\n3. Did you attempt a third evaluator family (e.g., a policy-trained open model like POLICYGUARD-4B or a locked-rubric judge à la RULERS)? If not, what are the anticipated costs/benefits, and how might adding such evaluators change the ERTA envelopes?\n4. Could ERTA incorporate optional reliability weights when independent human adjudication is available on a subset (e.g., a verification panel)? How would the method report both the unweighted envelope and a weighted sensitivity analysis without collapsing to a single scalar?\n5. Given all outcomes were “thought-fallback” traces, did you observe any systematic mismatch between trace-level judgments and environment-side listener artifacts in pilot runs on other setups? How might such mismatches bias different evaluators?"
        },
        "token_fingerprint_sha256_16": "d560549eaae16d22",
        "reviewed_pdf_sha256": "77d746801d41298e588882821218b2654392243af0c3e9e8a85054212bc17fe0",
        "exact_current_pdf": true
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
      "route": "QUALIFY_FIRST",
      "best_case": "同一 byte-identical evidence 经过 updater 可以生成不同 persistent states；把 state generator 本身从 evidence selection 中分离出来，审计 regeneration instability。",
      "story": "历史上一个有用的 persistent state 在冻结后仍可工作，但从完全相同 evidence 重新生成 state 时优势不稳定；E2 因此把 evidence→state generator 作为独立实验变量。",
      "premise": "same-evidence state disagreement 超过 downstream actor noise，且不是一个 outcome-selected First-Fail 特例；typed canonicalization 的增量若存在，应来自 generator constraint，而不是 generic scope/hygiene。",
      "risk": "当前最强现象仍来自 selected development case、单 backbone/private suite；generator-factor 与 actor variance 尚未 prospective 分开。Stanford 的核心 concern 是 M3R4/M4 仍未执行。",
      "strongest_simplification": "先做同一 frozen state 的 actor repeat 与 same-evidence repeated synthesis；M4 再用 FREE vs typed COMP 加 score-only / diagnosis-cardinality generic controls。若 actor noise 或 generic canonicalization 已解释差异，就没有 state-generator bottleneck 方法故事。",
      "evidence_state": "48-pair source study 总体 MRW−WIN-C=+0.023、p=.172，HOLD heterogeneous/underpowered。历史 First-Fail state 的优势在 fresh same-evidence regeneration 中不稳定。M3R4 independent preexecution design PASS，但 scientific execution=0；72 logical actor units/0 updater calls 已静态资格化，卡在 fresh DeepSeek model-identity requalification。",
      "next_closure": "只执行一次 fresh non-scientific model-identity qualification：requested deepseek-v4-pro 必须解析为 deepseek-v4-pro-ga-260813、thinking disabled、retry=0。Exact PASS 后再冻结 final contract/actual-path preflight；此时才讨论 72-unit M3R4。",
      "cost_class": "NEAR_ZERO_NOW / HIGH_IF_QUALIFIED",
      "cost_to_next_decision": "当前 next-decision 只是一笔 identity smoke/qualification，不是 720 calls。若通过，M3R4=72 actor logical units，结构 hard cap 720 provider calls，0 updater calls。",
      "dependencies": [
        "Recovery V3 resource priority first",
        "Ark quota/provider availability",
        "exact DeepSeek resolved identity",
        "frozen MindMemOS runtime/state SHA"
      ],
      "default_action": "QUALIFY_MODEL_IDENTITY_ONLY",
      "override_trigger": "resolved identity drift 或 qualification fail → HOLD，无自动替代模型；M3R4 primary generator result fail → STOP automatic state-generation-method story，不用第二 backbone/benchmark rescue。",
      "cross_paper_leverage": "与 E1/C1 共享 persistent representation/state identity 不能当中性实现细节的上层问题；与 Paper B 的长期 memory lifecycle 不同，E2 聚焦 state realization。",
      "advisor_question": "state-regeneration instability 是否是 self-evolving agent 中足够基础的 scientific object，还是当前 evidence 仍太像一个 selected-case implementation instability？",
      "reality_support": {
        "reality_verdict": "SUPPORTED_CONTEXT_ONLY",
        "supporting_cases": [
          {
            "title": "Agentic Memory",
            "url": "https://aclanthology.org/2026.acl-long.981/",
            "why": "Makes memory state generation and update an explicit learned operation rather than a passive store."
          },
          {
            "title": "HyperSkill",
            "url": "https://arxiv.org/abs/2608.16114",
            "why": "Periodically prunes, merges, and restructures skill memory, showing that the evidence→persistent-state transformation is an active system component."
          },
          {
            "title": "Robo-Cortex",
            "url": "https://arxiv.org/abs/2605.18729",
            "why": "Distills trajectories into reusable heuristics and long-term principle memory, supporting experience-to-state synthesis as a realistic self-evolution step."
          }
        ],
        "what_this_does_not_prove": "These systems establish that persistent state is synthesized from evidence, but they do not report same-evidence regeneration instability or show that generator variance dominates actor/runtime variance.",
        "strongest_escape": "If frozen-state actor repeats or generic canonicalization explain the observed disagreement, state-generation instability may be implementation noise rather than a standalone scientific object."
      },
      "resource_plan": {
        "authorized_now": {
          "cash_cny": "approximately ¥0.02 token-route order for one typical identity request; exact route may be AFP",
          "gpu": "0",
          "api_units": "1 non-scientific model-identity qualification",
          "work": "identity/route qualification only"
        },
        "resource_dimensions": {
          "api_cash": "~¥0.02 planning order for the single identity request; route-dependent",
          "local_gpu_occupancy": "0",
          "human_time": "<1 h",
          "provider_credential_dependency": "Ark/provider availability + exact resolved DeepSeek identity",
          "calendar_latency": "one request once provider is available"
        },
        "planning_cost_reference": "Recent DeepSeek actor tranche averaged ~2991 input + ~188 output tokens/call. At the token-route reference rate this is ~¥0.016/call.",
        "next_if_pass": "M3R4: 72 logical actor units with a structural hard cap of 720 provider calls; requires separate frozen execution authority.",
        "conditional_envelope": "If future calls resemble the recent actor-token average, 720 calls are roughly ¥11.5 token-route order; Ark AFP billing can differ materially.",
        "human_effort_estimate": "<1 h qualification/preflight now",
        "parallelization": "Provider-limited rather than GPU-limited; can run alongside local GPU work if quota/priority permits.",
        "priority_note": "Current spend should stop at one identity gate; do not reserve the 720-call envelope before qualification."
      },
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
        "token_fingerprint_sha256_16": "31104be789d9f7cf",
        "reviewed_pdf_sha256": "6194ac7a97a34bdb7f21c36ed2fa5b6f14c4c7184007d5418c643ff11b1c3f15",
        "exact_current_pdf": true
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
      "route": "FORMALIZE_FIRST",
      "best_case": "从 memory 会影响动作推进到这种影响是否忠实追随 source experience，用 matched counterfactual controls 做 causal fidelity audit。",
      "story": "MemoryVLA 的 memory edit 已能改变 action，但这不说明 agent 使用的是 source experience 的正确语义。Paper A 要把 influence 与 source fidelity 分开识别。",
      "premise": "可以从 source trajectory/state/action 记录中定义 outcome-independent、programmatic fidelity signature，并且下游 source-consistent direction 可以在多种有效策略下仍被稳定判定。",
      "risk": "目前只有 carrier influence（同状态 action shift，||Δa||₂≈0.5541），没有 source-fidelity 或 utility 证据；signature、endpoint、阈值与 same-condition replay 还不够具象，科学对象可能被 B1 provenance 或 Paper B lifecycle 吸收。",
      "strongest_simplification": "No-op serialization control + unrelated-content edit + same-content/different-provenance + frozen baseline memory。若 unrelated/no-op 产生同样 action shift，就直接否定 source-fidelity interpretation。",
      "evidence_state": "PRECONFIRMATORY：MemoryVLA/LIBERO carrier 可编辑且存在局部 action influence；decisive native closed-loop influence/fidelity/utility 尚未执行。Stanford 5.7 主要要求具体 fidelity signature examples、primary endpoints、thresholds 与 stochastic replay contract。",
      "next_closure": "不要直接启动 128-run confirmatory。先零/低成本冻结至少 2 个 task 的 fidelity-signature worked examples、source-consistent endpoint、随机性控制和 A0 no-op tolerance；A0/construct PASS 后才开 32 units×4 conditions=128 downstream runs。",
      "cost_class": "LOW_NOW / MEDIUM_IF_QUALIFIED",
      "cost_to_next_decision": "当前只需 protocol/CPU qualification≈0 GPU；正式 base confirmatory 才需要本地 VLA GPU 128 downstream runs，扩到 64 units 只能按预先 precision rule。",
      "dependencies": [
        "MemoryVLA + LIBERO-Plus frozen carrier",
        "versioned source trajectory/state/action records",
        "deterministic or frozen stochastic replay",
        "programmatic kinematic/source-fidelity signature"
      ],
      "default_action": "QUALIFY_FIDELITY_OBJECT_BEFORE_128",
      "override_trigger": "若 signature 无法 outcome-independently 冻结、no-op gate fail、或师兄判断与 B1/Paper B scientific object 重合，应 MERGE/NARROW 而不是用更多 rollouts rescue。",
      "cross_paper_leverage": "直接承接 B1 的 provenance-control lessons，并可成为 Paper B future-episode mechanism readout；周日需要明确它是 standalone identification paper 还是 family-level measurement module。",
      "advisor_question": "Influence–Fidelity 是否应该独立成 embodied-memory identification paper，还是并入 Paper B，并把 B1 当数字-Agent对照证据？",
      "reality_support": {
        "reality_verdict": "SUPPORTED_WITH_BOUNDARY",
        "supporting_cases": [
          {
            "title": "MemoryVLA",
            "url": "https://iclr.cc/virtual/2026/poster/10011504",
            "why": "Uses a memory bank to retrieve decision-relevant perceptual/cognitive entries for long-horizon robotic action, directly validating memory-conditioned VLA behavior as a real carrier."
          },
          {
            "title": "From Agent Traces to Trust",
            "url": "https://arxiv.org/abs/2606.04990",
            "why": "Motivates tracing how memory and evidence support later actions rather than treating influence alone as sufficient explanation."
          },
          {
            "title": "MemoryArena",
            "url": "https://arxiv.org/abs/2602.16313",
            "why": "Explicitly tests whether experience distilled into memory guides later decisions across sessions."
          }
        ],
        "what_this_does_not_prove": "Memory-conditioned action is real, but prior work does not establish that source fidelity is separable from generic memory influence under Paper A's proposed controls.",
        "strongest_escape": "If no-op or unrelated-content edits cause comparable action changes, the proposed fidelity interpretation collapses to generic memory/prompt sensitivity."
      },
      "resource_plan": {
        "authorized_now": {
          "cash_cny": 0,
          "gpu": "0",
          "api_units": 0,
          "work": "formalize fidelity signatures, endpoints, no-op tolerance, replay contract"
        },
        "resource_dimensions": {
          "api_cash": "¥0",
          "local_gpu_occupancy": "0 committed now; contingent Phase A GPU type/count and GPU-hours are UNKNOWN until frozen carrier/A0 runtime preflight",
          "human_time": "2–5 h scientific formalization",
          "provider_credential_dependency": "N/A for current formalization",
          "calendar_latency": "formalization first; later 128-run wall-clock UNKNOWN until frozen runtime preflight"
        },
        "next_if_pass": "Base confirmatory: 32 units × 4 conditions = 128 local VLA downstream runs. Before authorization, freeze GPU type/count, measured per-run throughput, resulting GPU-hours and wall-clock occupancy in the A0/runtime preflight.",
        "conditional_envelope": "Expansion to 64 units is allowed only by a predeclared precision rule; no automatic second-carrier expansion.",
        "human_effort_estimate": "2–5 h scientific formalization before any GPU run",
        "parallelization": "Formalization is fully parallel. Later VLA runs should use an idle eligible GPU and must not preempt frozen B1/3D work.",
        "priority_note": "High information-per-cost now because the next gate is essentially zero-compute."
      },
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
        "token_fingerprint_sha256_16": "72f8cb12c0806023",
        "reviewed_pdf_sha256": "11716be6f78402b26a4e17067b9d902e58346bf86d25e3928b95ce63b3c553c9",
        "exact_current_pdf": true
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
      "route": "QUALIFY_FIRST",
      "best_case": "同一个局部 benign repair 在保持 target gain 时可能对非目标约束产生 collateral regression；用 matched UPDATE/NO_UPDATE 与 coupling topology 分离这种 externality。",
      "story": "局部修复不是免费操作：它可能通过共享资源或依赖拓扑伤到未被修的约束。论文要测的是 update-attributable collateral，而不是一般任务难度。",
      "premise": "首先必须有真实可修 failure；repair 能严格 target-local；INDEPENDENT/LOW/HIGH coupling 在 outcome-blind graph 上构成真正的结构干预，而不是难度/规模代理。",
      "risk": "当前没有已确认的主现象：旧 source 8/8 success 导致 zero repair families；repair writer locality、topology manipulation check 与统计功效仍未被 outcome 验证。Stanford 6.2 也把没有 core phenomenon evidence 列为最大限制。",
      "strongest_simplification": "先做 TARGET_ONLY / UPDATE-vs-NO_UPDATE 在 topology-neutral source 上，证明 target repair 可发生且不会由 generic update magnitude 解释；在这之前任何 topology table 都没有识别价值。",
      "evidence_state": "旧 F0 因 8/8 target success 按协议 STOP。Direct-SFQ-A0 的 12-case public-oracle reachability/freshness 已完成 12/12，但 scientific dispatch 尚未开始。最新 provider-readiness R2 仅发送 1 次 non-scientific synthetic request，返回 HTTP 400 / insufficient_credit；readiness_pass=false，Gate 0 及全部 scientific authority 仍关闭。这是 infrastructure/credit blocker，不是机制证据。",
      "next_closure": "先恢复/充值同一 frozen provider credit 或修复同一 interface，不替换 provider/model；随后需要一份新的 explicit provider-readiness authority，只允许 1 次 synthetic readiness request、zero tools、zero retries。只有 readiness PASS 才能另行打开 Gate 0；Direct-SFQ-A0 与后续 source/repair qualification 仍是更后面的 gate。",
      "cost_class": "NEAR_ZERO_NOW / MEDIUM_IF_QUALIFIED",
      "cost_to_next_decision": "眼前不是 12-case science，而是 provider credit/interface repair + 1 次 non-scientific readiness request。只有 readiness PASS 后才逐级预算 Gate 0 / Direct-SFQ-A0；192+32 的主实验在这些 gates 前都不是承诺成本。",
      "dependencies": [
        "same frozen direct provider credit/interface restored",
        "new explicit one-request readiness authority",
        "no provider/model substitution",
        "strict target-local repair writer only after later gates",
        "outcome-blind topology graph"
      ],
      "default_action": "RESTORE_CREDIT_THEN_ONE_READINESS_ATTEMPT",
      "override_trigger": "readiness 仍 fail → STOP，无 scientific dispatch；未来 Gate 0 / SFQ 若不通过也按各自 frozen rule fail closed，不得通过换 provider、topology 或扩大 workload 制造现象。",
      "cross_paper_leverage": "与 G1 共享先证明 capability/repair、再解释 safety/collateral 的资格顺序；若两篇都成立，可形成 controlled-update family，但不应共享 outcome。",
      "advisor_question": "constraint externality 最终应该把贡献落在 measurement、topology prediction，还是 mitigation/control？在现象尚未确认前，哪一层值得优先保留？",
      "reality_support": {
        "reality_verdict": "SUPPORTED_AS_ENGINEERING_RISK",
        "supporting_cases": [
          {
            "title": "AgentDevel: Reframing Self-Evolving LLM Agents as Release Engineering",
            "url": "https://arxiv.org/abs/2601.04620",
            "why": "Treats pass→fail regressions as first-class evidence in agent updates and promotes changes through explicit non-regression gating, directly supporting collateral regression as a practical update risk."
          },
          {
            "title": "Safety in Self-Evolving LLM Agent Systems",
            "url": "https://arxiv.org/abs/2606.23075",
            "why": "Shows persistent updates can activate cross-cutting threats and amplify failures across lifecycle stages, supporting the premise that local updates can have non-local consequences."
          }
        ],
        "what_this_does_not_prove": "The engineering risk of regression is real, but no cited work establishes that graph coupling topology causally moderates collateral regression under an identical local repair.",
        "strongest_escape": "Strong regression testing and target-local update interfaces may already control most collateral effects without a new topology-based mechanism."
      },
      "resource_plan": {
        "authorized_now": {
          "cash_cny": 0,
          "gpu": "0",
          "api_units": 0,
          "work": "restore the same provider credit/interface only; the prior one-request readiness authority was consumed and the failed request cannot be retried without new explicit authority"
        },
        "resource_dimensions": {
          "api_cash": "¥0 committed now; credit restoration is account funding, not a scientific-call budget",
          "local_gpu_occupancy": "0",
          "human_time": "<1 h operational recovery",
          "provider_credential_dependency": "same provider credit/interface restored + NEW explicit one-request readiness authority",
          "calendar_latency": "UNKNOWN until credit/interface restoration"
        },
        "planning_cost_reference": "Historical full-plan token envelope was ~8–16M input + 0.5–1M output. At qwen3.7-plus first-tier rates that corresponds to roughly ¥19–39 for the full envelope, not current authorized spend.",
        "next_if_pass": "After credit/interface restoration AND a new explicit provider-readiness authority: exactly one non-scientific readiness request. Only a fresh readiness PASS can lead to separately authorized Gate 0 / Direct-SFQ-A0; a 12-case source-qualification stage is later still.",
        "conditional_envelope": "Mechanism block was planned at roughly 192 probes + ~32 sham probes, but this is not a committed cost until all source/repair gates pass.",
        "human_effort_estimate": "<1 h operational recovery now; later protocol review is conditional",
        "parallelization": "API/provider-limited; can proceed independently of GPU work after credit recovery.",
        "priority_note": "Do not budget the 192+32 mechanism block until the source phenomenon is qualified."
      },
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
        "token_fingerprint_sha256_16": "55b1bcd5772015d6",
        "reviewed_pdf_sha256": "f107dbff4c9126ad71bd376b2a33374ee2b9e54f195a1a1dda991a1b5658fa8b",
        "exact_current_pdf": true
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
      "route": "FORMALIZE_FIRST",
      "best_case": "用 exact persistent-state fork（Committed-Update vs Frozen-Preupdate）和 disjoint source/verification/future episodes，定义真正跨 episode 的 embodied self-evolution。",
      "story": "看过 memory 后动作变了不是 persistent learning。Paper B 要证明一个经过治理的 committed update 从 source episode 存入后，能在独立 future episode 被原生检索并相对 exact pre-update state 造成 durable benefit。",
      "premise": "persistent-state fork 可在 simulator/RNG/memory service 下做到可审计；native retrieval failure 应作为 total effect 的一部分；source/verification/future 分工可以避免未来 outcome 泄漏。",
      "risk": "当前没有 longitudinal causal result；potential-outcome/SCM estimand、unit/clustering、exact object identity 与 stochastic fork 还未完全形式化。若只是 carrier influence，它与 Paper A/C1 没有足够 distinctness。",
      "strongest_simplification": "Primary 是 COMMITTED_UPDATE vs exact FROZEN_PREUPDATE；NullMemory 只作依赖诊断，wrong/sham 控 extra context；只有要声称 governance superiority 才必须增加 ALWAYS_WRITE。",
      "evidence_state": "PRECONFIRMATORY：MemoryVLA carrier/local influence 已知，但 persistent commit→native retrieval→future utility 链没有 confirmatory outcome。Stanford 5.6 主要要求 formal causal estimand、fork reproducibility、hash identity、randomization unit/power。",
      "next_closure": "先冻结 causal estimand/SCM、stream-level randomization、exact persistent-state/hash/RNG fork qualification。通过后只启动 Phase A semantic sensitivity 32×4=128；Phase B 24 streams×3=72 只有 Phase A PASS 才开，完整 base=200 runs。",
      "cost_class": "LOW_NOW / MEDIUM_HIGH_IF_QUALIFIED",
      "cost_to_next_decision": "当前 formalization + fork qualification 接近零 GPU；Phase A 才需要 128 local VLA runs。不要现在把 Phase B 72 runs 也当成承诺成本。",
      "dependencies": [
        "MemoryVLA/LIBERO persistent store snapshot",
        "immutable committed-object identity/hash",
        "source/verification/future split",
        "native retrieval rule",
        "deterministic snapshot/RNG policy"
      ],
      "default_action": "FREEZE_CAUSAL_FORK_THEN_PHASE_A_ONLY",
      "override_trigger": "fork 不可精确复现、Phase A semantic sensitivity fail、或师兄决定与 Paper A 合并 → 不进入 Phase B；governance superiority 未执行 ALWAYS_WRITE 时不得写方法优越性。",
      "cross_paper_leverage": "Paper A 可作为 future-episode influence/fidelity mechanism readout；C1 提供 transport vocabulary；B1 提供 provenance control，但 Paper B 的主 claim 必须保持 longitudinal utility。",
      "advisor_question": "longitudinal persistent-state fork 是否足够构成独立 embodied self-evolution paper？Paper A 应作为它的 measurement module，还是保持两篇？",
      "reality_support": {
        "reality_verdict": "STRONGLY_SUPPORTED_WITH_NOVELTY_PRESSURE",
        "supporting_cases": [
          {
            "title": "MemoryArena",
            "url": "https://arxiv.org/abs/2602.16313",
            "why": "Directly defines multi-session loops where agents learn from earlier actions/feedback and use memory on later tasks."
          },
          {
            "title": "Agentic Memory",
            "url": "https://aclanthology.org/2026.acl-long.981/",
            "why": "Provides explicit long-term memory store/retrieve/update/discard operations across long-horizon agent tasks."
          },
          {
            "title": "Robo-Cortex",
            "url": "https://arxiv.org/abs/2605.18729",
            "why": "Maintains long-term principle memory distilled from past trajectories in a continuous reflection-adaptation loop."
          },
          {
            "title": "MemoryVLA",
            "url": "https://iclr.cc/virtual/2026/poster/10011504",
            "why": "Demonstrates memory-conditioned long-horizon robotic manipulation, supporting embodied memory as a real deployment substrate."
          }
        ],
        "what_this_does_not_prove": "Persistent embodied memory is clearly real, but this creates novelty pressure: Paper B must defend the exact persistent-state fork and longitudinal identification standard, not generic long-term memory or self-evolution.",
        "strongest_escape": "If the committed-update vs frozen-preupdate fork cannot be reproduced exactly, or native retrieval transport is weak, existing multi-session memory evaluation may cover the practical question more simply."
      },
      "resource_plan": {
        "authorized_now": {
          "cash_cny": 0,
          "gpu": "0",
          "api_units": 0,
          "work": "formalize causal estimand, randomization unit, exact state/hash/RNG fork"
        },
        "resource_dimensions": {
          "api_cash": "¥0",
          "local_gpu_occupancy": "0 committed now; contingent Phase A GPU type/count and GPU-hours are UNKNOWN until exact fork/runtime preflight",
          "human_time": "2–5 h SCM/fork formalization",
          "provider_credential_dependency": "N/A for current formalization",
          "calendar_latency": "formalization first; later 128-run wall-clock UNKNOWN until frozen runtime preflight"
        },
        "next_if_pass": "Phase A: 32 units × 4 semantic conditions = 128 local VLA runs. Before authorization, freeze GPU type/count, measured throughput, GPU-hours and wall-clock occupancy for the exact persistent-state fork.",
        "conditional_envelope": "Phase B: 24 streams × 3 branches = 72 local VLA runs only after Phase A PASS; full base program = 200 runs.",
        "human_effort_estimate": "2–5 h SCM/fork formalization before compute",
        "parallelization": "Formalization is fully parallel. Later VLA phases must wait for their own gates and available local GPU.",
        "priority_note": "Do not treat 200 runs as current budget; only formalization is authorized now."
      },
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
        "token_fingerprint_sha256_16": "08011461988e7036",
        "reviewed_pdf_sha256": "deee83f4e6d033ec9b5a09d63910c0566e8f8d1c8e9aa6ea9d5983ae8bc6ca68",
        "exact_current_pdf": true
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
      "route": "EXECUTE_FROZEN",
      "best_case": "在 relation count、对象、谓词和 decoder 全部匹配时，只改变 Chain/Hub endpoint-sharing topology，再用 oracle graph substitution 定位 Text→Graph 与 Graph→Scene bottleneck。",
      "story": "relation count 相同的 instruction 仍可能因 endpoint-sharing topology 不同而难度不同；3D 用 count-matched Chain/Hub counterfactual 和 exact graph intervention 隔离这个结构轴。",
      "premise": "Chain/Hub 的差异来自 endpoint connectivity，而不是重复 hub object 带来的 lexical/coreference load、object salience/size 或 predicate implication；一个 frozen shared decoder 足以做条件化 localization。",
      "risk": "目前 zero scientific outcomes；单 substrate/窄 predicate set，且 lexical/coreference/salience confounds 还要在 P1 前显式 manipulation check。Stanford 4.1 的低分主要是尚无结果，不是已观察到负效应。",
      "strongest_simplification": "固定 count/object/predicate multiset/token budget 的 Chain/HUB matched pairs，再做 predicted-graph vs exact instructed-graph substitution；若 lexical/salience matching 或 oracle substitution 不能按预期改变 gap，就停止 topology/localization claim。",
      "evidence_state": "DEVELOPMENTAL TRAINING ONLY：SGP-14 与 shared SG2SC decoder 正在训练，scientific_outcomes=0、P1 authority=false。2026-09-05 live check：shared decoder 272,249/1,000,000 steps；SGP-14 25,170/1,000,000；training loss 不进入论文证据。",
      "next_closure": "继续已授权 developmental training 到两个组件 checkpoint seal，期间不打开 validation/test/topology metrics。训练完成后另行申请 frozen P1 validation authority，并先补 lexical/coreference + hub-object salience manipulation checks。",
      "cost_class": "VERY_HIGH · ALREADY_RUNNING",
      "cost_to_next_decision": "当前持续占用两张 RTX 3090（shared decoder + SGP-14）；0 commercial API。成本主要是剩余 optimizer wall-time/opportunity，P1 不是当前已授权成本。",
      "dependencies": [
        "two-RTX-3090 training capacity",
        "content-addressed checkpoints",
        "frozen matched compiler",
        "shared decoder identity",
        "separate P1 authority after training seal"
      ],
      "default_action": "CONTINUE_TRAINING_NO_OUTCOME_INSPECTION",
      "override_trigger": "只因机械/resource failure 才暂停/修复训练；不能因 training loss 或开发观察改 topology/predicate/panel。P1 若不支持 count-matched topology residual，则按 frozen STOP，不加 5/6 relations rescue。",
      "cross_paper_leverage": "方法学上与全 portfolio 共用 matched-counterfactual / strongest-simplification discipline，但科学对象独立，几乎没有 merge 风险。",
      "advisor_question": "endpoint-sharing topology 是真实 3D instruction complexity 的关键变量，还是 controlled benchmark 中才突出的分析轴？P1 前最必须补哪一个 confound control？",
      "reality_support": {
        "reality_verdict": "SUPPORTED_WITH_NOVELTY_BOUNDARY",
        "supporting_cases": [
          {
            "title": "InstructScene",
            "url": "https://arxiv.org/abs/2402.04717",
            "why": "Uses a semantic graph prior and layout decoder for instruction-driven 3D scene synthesis, validating relational graph structure as a real generation interface."
          },
          {
            "title": "SceneNAT",
            "url": "https://arxiv.org/abs/2601.07218",
            "why": "Uses explicit subject-predicate-object triplets to improve relational reasoning in language-guided indoor scene synthesis."
          },
          {
            "title": "GeoSceneGraph",
            "url": "https://arxiv.org/abs/2511.14884",
            "why": "Leverages scene-graph structure and geometric symmetries for text-guided 3D indoor scene synthesis."
          }
        ],
        "what_this_does_not_prove": "These works establish that graph relations matter; they do not establish a fixed-count endpoint-sharing effect or locate it to text→graph versus graph→scene.",
        "strongest_escape": "Lexical repetition, hub-object salience/size, or predicate implication may explain Chain/Hub differences even after relation count is matched."
      },
      "resource_plan": {
        "authorized_now": {
          "cash_cny": 0,
          "gpu": "2×RTX 3090 local",
          "api_units": 0,
          "work": "developmental SGP-14 + shared SG2SC training to 1,000,000 optimizer steps each"
        },
        "resource_dimensions": {
          "api_cash": "¥0",
          "local_gpu_occupancy": "2×RTX 3090 live; SGP-14 + shared decoder",
          "human_time": "low active monitoring",
          "provider_credential_dependency": "N/A",
          "calendar_latency": "rough remaining ~11.6 / ~7.5 GPU-days at 22:55 observed averages; operational estimate only"
        },
        "operational_snapshot": {
          "observed_at": "2026-09-05T22:55:10+08:00",
          "sgp14_step": 31281,
          "shared_decoder_step": 279572,
          "target_step_each": 1000000,
          "rough_remaining_gpu_days_if_current_average_holds": {
            "sgp14": 11.6,
            "shared_decoder": 7.5
          },
          "note": "Derived from current process elapsed time and heartbeat step counts; operational estimate only, not a scientific result or guarantee."
        },
        "next_if_pass": "After both training seals, P1 validation needs separate authority. No validation/test/topology metrics are opened during training.",
        "conditional_envelope": "If P1 GO later justifies replication, additional seeds require a fresh compute authority; they are not part of the current committed budget.",
        "human_effort_estimate": "Low active human time while training; checkpoint/resource monitoring only",
        "parallelization": "Keep the two running 3090 jobs isolated. Other zero-compute/API work can proceed in parallel.",
        "priority_note": "High opportunity cost but already committed; stopping early without a frozen mechanical failure wastes sunk compute and violates the protocol."
      },
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
        "token_fingerprint_sha256_16": "13e0eceaadad19de",
        "reviewed_pdf_sha256": "76909e7572849dca55aca38f2cc5488462a74d3262b19d7669c24465173bcf1f",
        "exact_current_pdf": true
      }
    }
  ],
  "spinoffs": [
    {
      "paper_id": "G2_CANDIDATE",
      "title": "Separating Capability Unlock from Safety Drift in Persistent Browser Agents",
      "status": "HOLD_FOR_IDENTIFICATION",
      "relation": "Separate MCTA capability-matching protocol candidate; not a later revision of G1/ERTA.",
      "stanford": {
        "numerical_score": 4.8,
        "textual_signal": "CRITICAL",
        "review_date": "2026-09-05T09:11:12.602100",
        "advisor_digest": {
          "strongest_positive": "- Technical novelty and innovation - Introduces a clear task-local capability witness (benign twin completion + shared graph coverage) that separates refusal from inability, addressing a central confound in longitudinal agent safety. - Proposes a principled shared-capability gate S(u,t) and analyzes R0/R1/R2/R3 endpoints to decompose behavioral shifts, focusing prospectively on R1 as the primary endpoint. - Designs an Updated-vs-Frozen, same-schedule longitudinal identification with a balanced incomplete block assignment and pre-declared support criteria, minimizing researcher degrees of freedom in analysis. - Adds a thoughtful “length/structure” placebo to disentangle semantic workflow upd…",
          "decision_changing_concern": "- Technical limitations or concerns - Conditioning on post-treatment capability (C=1) necessarily induces selection; while the paper acknowledges this and frames claims narrowly, the causal interpretation remains limited to a “shared-capability subset,” not a general causal effect. - The canonical shared action graph is assumed acyclic and frozen; many web tasks allow alternate valid paths, optional loops, or branching. The protocol lacks detail on how to handle multiple feasible paths, cycles, or re-planning while avoiding bias. - The capability witness requires “full shared-graph coverage,” which risks penalizing benignly extraneous but harmless interactions or valid alternative orderings…",
          "reviewer_question": "1. How are canonical shared action graphs derived and validated? Do you have a protocol for inter-annotator reliability, alternative-path handling, and allowable deviations (e.g., optional fields, retries) without overfitting the graph to one path? 2. Many web workflows are not acyclic in practice. Why enforce DAGs, and how would you extend MCTA to graphs with cycles or conditional branches? 3. How do you define the “authorized benign twin” concretely for each harmful task to ensure it exercises precisely the same primitives/transitions? Can you provide specific examples and release templates? 4. What is your plan for uncertainty quantification on the P1 contrast (e.g., CIs, randomization i…"
        }
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
      "id": "measurement-validity",
      "label": "Measurement / evaluator validity",
      "papers": [
        "G1",
        "C1",
        "B1"
      ],
      "question": "这些论文都在区分 observed measurement surface 与真正 scientific property；是否存在一个共享的 evaluator/measurement assumption 一旦失效会同时改变多篇结论？"
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
  "resource_pricing_basis": {
    "source": "generated/provider-price-comparison-snapshot-20260903.json",
    "rule": "API estimates are planning references only. Exact billing must be summed call-by-call using the actual provider route and per-call context tier.",
    "reference_rates_cny_per_million_tokens": {
      "qwen3.5-397b-a17b_first_tier": {
        "input": 1.204,
        "output": 7.224,
        "context": "<=128K"
      },
      "qwen3.7-plus_first_tier": {
        "input": 1.932,
        "output": 7.707,
        "context": "<=256K"
      },
      "deepseek-v4-pro_token_route_reference": {
        "input": 4.5,
        "output": 13.5
      }
    }
  },
  "portfolio_schedule": [
    {
      "lane": "A · cheap closure",
      "papers": [
        "E1",
        "C1"
      ],
      "action": "Finish manuscript/advisor decisions immediately; no scarce compute."
    },
    {
      "lane": "B · already-running compute",
      "papers": [
        "B1",
        "3D"
      ],
      "action": "Let frozen jobs run uninterrupted; collect only operational receipts, no interim science."
    },
    {
      "lane": "C · near-zero qualification",
      "papers": [
        "G1",
        "E2",
        "CONSTRAINT_EXTERNALITY"
      ],
      "action": "Resolve credential/identity/credit gates one at a time; spend only the next-gate budget."
    },
    {
      "lane": "D · formalize before compute",
      "papers": [
        "PAPER_A",
        "PAPER_B"
      ],
      "action": "Use Web GPT + human review to freeze the causal objects before allocating VLA GPU runs."
    }
  ],
  "overlay_audit": {
    "independent_verdict": "REVISE_REALITY_COST_OVERLAY",
    "postfix_status": "FIXES_APPLIED_DETERMINISTIC_PASS",
    "verification_path": "DETERMINISTIC_SCHEMA_AND_EXACT_TEXT_GUARDS",
    "model_slug": "gpt-5-6-thinking",
    "extra_high": true,
    "authority": {
      "scientific": false,
      "experiment": false,
      "submission": false,
      "advisor_overlay_only": true
    },
    "stale_for_papers": [
      "C1",
      "G1"
    ],
    "stale_reason": "C1 story and G1 lineage were materially corrected after the prior reality/cost overlay review; their current decision cards supersede the old object."
  },
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
