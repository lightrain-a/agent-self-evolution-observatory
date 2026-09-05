window.ADVISOR_MEETING_DATA = {
  "schema_version": "2.0",
  "generated_at": "2026-09-05",
  "meeting": {
    "id": "2026-09-06-advisor",
    "main_ref": "bb9b99d915de1141ac39654550dd91f81070ee00",
    "status": "9_OF_9_READY",
    "review_route": "exception-and-boundary-review"
  },
  "route_summary": {
    "FREEZE_SUBMIT": 2,
    "EXECUTE_FROZEN": 2,
    "QUALIFY_FIRST": 3,
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
      "route": "FREEZE_SUBMIT",
      "best_case": "把 memory 写入了却没改变行为拆成 write → native exposure → uptake → endpoint 的阶段证据，定位 persistent-memory transport 在哪里衰减。",
      "story": "persistent state divergence 本身不是 behavioral learning；C1 用 stage-resolved measurement 追踪 branch difference 从写入、原生检索、policy uptake 到 terminal outcome 的传输边界。",
      "premise": "把 heterogeneous stage evidence 保持为分层估计，比一个 end-to-end 成败率更能回答 memory difference 到底在哪一层消失，并且这种 diagnosis 本身有独立研究价值。",
      "risk": "writer intervention 是 bundled protocol change，native exposure 还不是 treatment-residual exposure，uptake 主要落在 first action；如果读者要求 causal atom 或新治理方法，当前 measurement paper 会被认为只做诊断。",
      "strongest_simplification": "forced fixed-evidence capacity 与 native transport 分开：若 memory 在 forced exposure 下可影响行为、但 native path 衰减，就不应继续堆 writer/model baseline；这已经是最便宜、最判别的解释。",
      "evidence_state": "CURRENT CLAIM SCIENCE CLOSED：write divergence、native exposure、first-action uptake 与 endpoint 分层结果已冻结；forced fixed-evidence capacity 4×4 共 256 rollouts 显示 latent leverage；CBRG method extension 因缺 outcome-independent semantic adjudicator 已 STOP/MERGE，不影响 measurement paper。",
      "next_closure": "不再新增 provider/GPU 实验。只做 manuscript convergence，并让师兄判断 stage-resolved diagnosis 是否足够 standalone；不得为了更像方法论文重开已停止的 CBRG。",
      "cost_class": "ZERO_REQUIRED",
      "cost_to_next_decision": "0 新 scientific API/GPU；只剩 paper integration / human review。",
      "dependencies": [
        "current frozen evidence ledger",
        "no new semantic-adjudicator asset is currently admissible"
      ],
      "default_action": "FREEZE_MEASUREMENT_PAPER",
      "override_trigger": "只有出现新的、独立资格化 outcome-independent semantic validity asset，或师兄明确认为 standalone measurement value 不足并要求 merge，才改变路线。",
      "cross_paper_leverage": "为 Paper A/B/E2 提供写入≠使用≠终端效果的 stage vocabulary；可复用测量思想，但不要共享同一 scientific claim。",
      "advisor_question": "stage-resolved diagnosis 本身是否足够构成 paper-level contribution，还是更适合作为 Paper A/B 的测量组件？",
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
      "route": "QUALIFY_FIRST",
      "best_case": "用 task-local graph-complete benign twin 把更安全与只是不会/拒绝做任务分开，再在 shared-capability slots 上比较 Updated vs Frozen。",
      "story": "harmful non-execution 有两种解释：安全边界或能力缺失。MCTA 只有在 Updated 与 Frozen 都能完成同一共享浏览器 action graph 时，才把 harmful R1 差异解释为 capability-preserved boundary drift。",
      "premise": "task-local capability witness 可以在不泄漏 harmful outcome 的情况下被可靠定义；canonical shared action graph 能覆盖真实可行路径，而不会把合法 alternate paths/cycles 误判为没能力。",
      "risk": "C 是 post-treatment capability，因此 shared-capability conditioning 有 selection 限制；canonical DAG 可能过度固定唯一操作路径。Stanford 4.8 的真正压力集中在这两点，而不是旧 ERTA evaluator disagreement。",
      "strongest_simplification": "M0 raw harmful-action temporal contrast → M1 global 10/10 capability gate → M2 same-surface benign twin → M3 graph-complete MCTA。若 M1/M2 已给出相同判断，则 MCTA 复杂度没有增量识别价值。",
      "evidence_state": "T0 static/runtime qualification 已 PASS：8 admitted pairs，8/8 shared graphs/runtime binding；Q0 exact qwen3.5-397b-a17b ten-task BrowserART gate 仍 PENDING_PROVIDER_CREDENTIAL。P0/P1 尚无 provider execution authority，历史 4-step traces 只作 discovery。",
      "next_closure": "只做 Q0：官方 10 个 benign BrowserART task × 10-step exact stack，必须 10/10。Q0 PASS 后才允许考虑 P0 的 32 episodes；P1 的 336 episodes 当前不进入预算。",
      "cost_class": "LOW_NOW / HIGH_IF_QUALIFIED",
      "cost_to_next_decision": "眼前成本仅 Q0 的 10 个 benign agent episodes。若 PASS，下一门 P0=32 episodes；只有 P0 至少 6 pair IDs 获得 shared-capability support 才进入 P1=336。",
      "dependencies": [
        "exact qwen3.5-397b-a17b provider credential",
        "pinned BrowserART official 10 benign tasks",
        "canonical graph + alternate-path validity protocol"
      ],
      "default_action": "RUN_Q0_ONLY",
      "override_trigger": "Q0 非 10/10 → STOP safety execution，转 substrate diagnosis；P0 support <6 pairs → 不做 P1，报告 measurement limitation/merge；shared-capability P1 null 时按冻结 identity rule pivot/stop。",
      "cross_paper_leverage": "与 Constraint Externality 共用先证明 capability/target repair、再解释 safety/collateral 的 controlled-update discipline；可共享资格门思想但实验对象不同。",
      "advisor_question": "MCTA 的 task-local capability conditioning 是否是足够强的 methodology object？canonical shared action graph 应怎样允许 alternate valid paths/cycles 才不会制造 selection bias？",
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
