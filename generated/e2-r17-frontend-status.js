window.E2_R17_FRONTEND_STATUS = {
  schema_version: "1.0",
  as_of_date: "2026-09-05",
  project_track: "E2-R17",
  title: {
    zh: "解耦 Test-Time Search 的 Serving 与 Persistent Learning",
    en: "Decoupling Serving and Persistent Learning over Test-Time Search"
  },
  subtitle: {
    zh: "Exact-Same-Pool 因果识别 · Search-Projection Censoring · R3 matched-censor recovery 已通过 exact-hash 审查并完成 reset-readiness；2026-09-07 00:00 +0800 前禁止 provider call",
    en: "Exact-same-pool causal identification · Search-Projection Censoring · R3 matched-censor recovery passed exact-hash review and reset-readiness; provider calls are forbidden before 2026-09-07 00:00 +0800"
  },
  paper_identity: "CAUSAL_SYSTEMS_INTERFACE_PAPER",
  scientific_object: {
    zh: "面向 search-augmented agents：系统在 serving commit 前已经生成或探索一个 richer search object T_K；当前行为消费 a(T_K)，持久学习消费 g(T_K)。核心实验固定 T_K 与 serving，只改变 learner-visible projection。",
    en: "For search-augmented agents, the system has already generated or explored a richer search object T_K before the serving commit; current behavior consumes a(T_K), while persistent learning consumes g(T_K). The core intervention fixes T_K and serving, changing only the learner-visible projection."
  },
  premise_scope: {
    verdict: "SCOPE_CALIBRATED_SEARCH_AUGMENTED_AGENTS",
    title_zh: "适用范围校准：不是所有 Agent 都先跑多条完整轨迹",
    title_en: "Scope calibration: not every agent runs multiple full trajectories first",
    premise_zh: "论文不再假设“现代 Agent 普遍并行生成多条完整轨迹再选最好的一条”。更准确的对象是 search-augmented / test-time-scaling agents：它们在最终 serving commit 前，会生成或探索多个 candidate actions、branches 或 trajectories。",
    premise_en: "The paper no longer assumes that modern agents generally generate many complete trajectories in parallel and then choose one. The intended substrate is search-augmented / test-time-scaling agents that generate or explore multiple candidate actions, branches, or trajectories before the final serving commit.",
    tk_definition_zh: "T_K 是 serving commit 前已经实际产生并被系统评估过的 candidate evidence/search object；它可以来自 Best-of-N、tree/MCTS、step-wise candidate reranking、beam/lookahead，不要求必须是 K 条并行完整 trajectory。",
    tk_definition_en: "T_K is the candidate evidence/search object actually produced and evaluated before the serving commit. It may come from Best-of-N, tree/MCTS, step-wise candidate reranking, or beam/lookahead; it need not be K parallel complete trajectories.",
    out_of_scope_zh: "如果一个 Agent 只有单轨 sequential execution，且 serving 前没有产生可分离的 candidate search object，那么本文的 projection-censoring 问题并不天然存在。",
    out_of_scope_en: "If an agent only performs single-path sequential execution and produces no separable candidate search object before serving, the projection-censoring problem studied here does not arise by default.",
    why_it_matters_zh: "因此论文 claim 应限定为 search-enabled agents 的 serving→persistent-learning interface，而不是所有 Agent 的普遍缺陷。",
    why_it_matters_en: "Accordingly, the paper's claim is about the serving→persistent-learning interface in search-enabled agents, not a universal defect of all agents.",
    representative_workflows: ["Best-of-N / wide sampling", "Tree or MCTS search", "Step-wise candidate reranking", "Beam / shallow lookahead"]
  },
  frozen_scientific_r2: {
    commit: "29799c83c662887694db52acba4bb19e83131bb0",
    contract_sha256: "f5382c552f2e6644e4cbda408510119664a8c6f8502628586c9ff5583abd1234",
    preflight_sha256: "e257438bd482d4f2209a8321d4a222bd97acf2c03bff46a1d5513b55a42ca766",
    changed_by_frontend: false
  },
  authority: {
    fresh_identity_qualification_permitted: false,
    fresh_identity_called: true,
    r3_fresh_identity_required_after_reset: true,
    r3_recovery_authorized: false,
    stage_a: false,
    stage_b: false,
    public_p1: false,
    baseline_execution: false,
    identity_provider_generation_attempts: 1,
    stage_a_provider_pre_io_claims: 4,
    stage_a_complete_pools: 0,
    support_inspected: false
  },
  stage_a_incident: {
    status: "R3_RECOVERY_READY_WAIT_PROVIDER_RESET",
    cause: "Ark AccountQuotaExceeded",
    provider_reset_time: "2026-09-07 00:00:00 +0800",
    burned_task_id: "r17-b21-cgwb-p0",
    matched_no_provider_censor_task_id: "r17-b21-cgwp-p0",
    attempted_task_markers: 1,
    sealed_task_receipts: 0,
    frozen_k8_pools: 0,
    completed_streams: 0,
    support_inspected: false,
    updater_calls: 0,
    heldout_access: 0,
    replay_allowed: false,
    replacement_allowed: false,
    proposed_recovery_zh: "R3 matched-censor recovery 已冻结并通过 exact-hash 独立审查：burned task 永久 technical-missing，其 exact semantic counterpart 作为 0-provider matched censor；reset 后只执行其余 158 个原始 task（1264 actor rollouts），保持 7/7/8 opportunity geometry 与每 stream >=4 mixed pools 的绝对阈值。",
    proposed_recovery_en: "The R3 matched-censor recovery is frozen and independently exact-hash reviewed: the burned task remains terminal technical-missing, its exact semantic counterpart is a zero-provider matched censor, and only the other 158 original tasks (1264 actor rollouts) may execute after reset while preserving 7/7/8 opportunity geometry and the absolute >=4 mixed-pools threshold per stream."
  },
  r3_recovery: {
    status: "PASS_ZERO_PROVIDER_R3_RESET_READINESS_WAIT_PROVIDER_RESET",
    contract_sha256: "3d0db7078c073613a27bc643675aa8755c7b2f241345ef6371570be48f2dd085",
    preflight_sha256: "56208e171b2524a01ec429618c7b018a4fee1a9a785028f024fee5a40bd10df2",
    exact_hash_review_verdict: "PASS_TO_SEPARATE_R3_RECOVERY_AUTHORIZATION",
    provider_execution_tasks: 158,
    actor_rollouts: 1264,
    max_provider_interactions: 12640,
    run_root_exists: false,
    lease_exists: false,
    control_tests: "3/3 PASS",
    stale_r2_identity_rejected: true,
    support_inspected: false
  },
  next_gate: {
    code: "WAIT_PROVIDER_RESET_THEN_FRESH_R3_IDENTITY_THEN_SEPARATE_RECOVERY_AUTHORIZATION",
    zh: "当前硬门：2026-09-07 00:00 +0800 前不做 provider call。reset 后恰好 1 次 fresh DeepSeek R3 identity → 本地 adjudication → PASS 才单独 mint R3 recovery authorization → 只跑冻结的 158 个原始 task。",
    en: "Hard gate now: no provider call before 2026-09-07 00:00 +0800. After reset: exactly one fresh DeepSeek R3 identity → local adjudication → only on PASS mint a separate R3 recovery authorization → run only the frozen 158 original tasks."
  },
  completed_evidence: [
    {
      id: "A1",
      title_zh: "Availability / censoring 支持",
      title_en: "Availability / censoring support",
      status: "COMPLETE",
      metrics_zh: "96 个 K=8 pools · 768 rollouts · 78/96 mixed pools · 12/12 exposed streams · 6/6 failure families",
      metrics_en: "96 K=8 pools · 768 rollouts · 78/96 mixed pools · 12/12 exposed streams · 6/6 failure families",
      claim_zh: "只证明 search object 中存在 winner-coupled learner 看不到的 evidence；不证明这些 evidence 有学习价值。",
      claim_en: "Shows that evidence exists in the search object but is hidden from winner-coupled learning; it does not establish learning value."
    },
    {
      id: "A2",
      title_zh: "Closed global exact-same-pool causal study",
      title_en: "Closed global exact-same-pool causal study",
      status: "COMPLETE_INCONCLUSIVE",
      metrics_zh: "12 streams · 48 paired replicates · 96 learned states · 1728 heldout units · MRW−WIN-C=+2.31pp · p=0.171875",
      metrics_en: "12 streams · 48 paired replicates · 96 learned states · 1728 heldout units · MRW−WIN-C=+2.31pp · p=0.171875",
      claim_zh: "可靠的 global universal-MRW benefit 未建立；结果与 underpower、heterogeneity 或两者兼容。",
      claim_en: "A reliable global universal-MRW benefit was not established; the result is compatible with underpower, heterogeneity, or both."
    }
  ],
  mandatory_controlled: [
    {
      id: "B0",
      title_zh: "Model identity gate · R3 requalification",
      title_en: "Model identity gate · R3 requalification",
      status: "R3_REQUALIFICATION_WAIT_PROVIDER_RESET",
      scale_zh: "首次 identity 已 PASS 并被 fail-closed Stage-A run 消费；R3 要求 reset 后重新做恰好 1 次 fresh identity，旧 identity 已验证会被 authorizer 拒绝。",
      scale_en: "The first identity PASS was consumed by the fail-closed Stage-A run. R3 requires exactly one fresh post-reset identity; the authorizer has been verified to reject the stale R2 identity.",
      gate_zh: "2026-09-07 00:00 +0800 前禁止 fresh R3 identity provider call。",
      gate_en: "A fresh R3 identity provider call is forbidden before 2026-09-07 00:00 +0800."
    },
    {
      id: "B1",
      title_zh: "V3 Stage A · R3 matched-censor recovery",
      title_en: "V3 Stage A · R3 matched-censor recovery",
      status: "R3_RECOVERY_READY_WAIT_PROVIDER_RESET",
      scale_zh: "160 原始 opportunities = 1 terminal technical missing + 1 matched 0-provider censor + 158 provider tasks；K=8 → 1264 actor rollouts；R3 run root/lease 尚未创建。",
      scale_en: "160 original opportunities = 1 terminal technical missing + 1 matched zero-provider censor + 158 provider tasks; K=8 gives 1264 actor rollouts; the R3 run root/lease do not yet exist.",
      gate_zh: "exact-hash review 与 reset-readiness 均 PASS；reset 后 fresh R3 identity PASS + separate authorization 才能执行。support 仍未读取，Stage B 仍关闭。",
      gate_en: "Exact-hash review and reset-readiness both PASS; execution still requires a fresh post-reset R3 identity PASS plus separate authorization. Support remains unread and Stage B remains closed."
    },
    {
      id: "B2",
      title_zh: "V3 Stage B · exact-same-pool causal mechanism",
      title_en: "V3 Stage B · exact-same-pool causal mechanism",
      status: "CONDITIONAL_LOCKED",
      scale_zh: "20 streams · R=4 measurement reps · 80 paired units · 160 learned states · 3200 heldout evaluations · 5 independent skeleton interactions",
      scale_en: "20 streams · R=4 measurement reps · 80 paired units · 160 learned states · 3200 heldout evaluations · 5 independent skeleton interactions",
      gate_zh: "Primary gate 由 5 个 I_h 决定。FAIL 后 public benchmark、router、第二模型都不能 rescue。",
      gate_en: "The primary gate is decided by five I_h values. After FAIL, public benchmarks, router results, or a second model cannot rescue the mechanism claim."
    },
    {
      id: "B3",
      title_zh: "Secondary controlled-divergence gate",
      title_en: "Secondary controlled-divergence gate",
      status: "NO_NEW_DATA",
      scale_zh: "不新增调用；读取 B2 已冻结的 5 个 D_h,PROCEDURAL",
      scale_en: "No new calls; reads the five frozen D_h,PROCEDURAL values from B2",
      gate_zh: "Primary PASS 且 5/5 D_h,PROCEDURAL>0 才解锁 controlled act/learn divergence；不能事后挑正例。",
      gate_en: "Only primary PASS plus 5/5 D_h,PROCEDURAL>0 unlocks controlled act/learn divergence; no post-hoc positive-cell selection."
    }
  ],
  public_p1: {
    status: "CONDITIONAL_NOT_FROZEN",
    entry_zh: "只有 B2 primary interaction PASS 后才能冻结并独立预审 Public P1；绝不能用 public benchmark rescue V3 FAIL。",
    entry_en: "Public P1 may be frozen and independently prereviewed only after B2 primary interaction PASS; a public benchmark cannot rescue V3 FAIL.",
    substrate: "SpreadsheetBench Verified-400",
    split_policy: "80 evolution / 40 validation / 280 heldout test",
    exact_ids_frozen: false,
    purpose_zh: "同一条 public lane 承载两个分开的 estimand：统一 end-to-end closest-method comparison，以及 exact-same-pool / same-acting 的 paired causal transport；二者不能混为一个结果。",
    purpose_en: "One public lane carries two separate estimands: unified end-to-end closest-method comparison and paired exact-same-pool / same-acting causal transport; they must not be conflated.",
    search_workflow_requirement_zh: "SpreadsheetBench Verified-400 只是任务 substrate。冻结 Public P1 时，还必须明确一个真实 search-enabled workflow，使 T_K_public 来自 serving 前实际生成/探索的 candidate actions、branches 或 trajectories；否则只能证明 benchmark performance，不能支撑本文的 search-interface 外部有效性。",
    search_workflow_requirement_en: "SpreadsheetBench Verified-400 is only the task substrate. When Public P1 is frozen, it must also instantiate a real search-enabled workflow so that T_K_public comes from candidate actions, branches, or trajectories actually generated/explored before serving; otherwise the experiment supports benchmark performance but not the paper's search-interface external validity.",
    primary_model_zh: "先只用一个统一主模型/harness：优先 DeepSeek V4-Pro exact qualified release；不做 4×4 模型矩阵。",
    primary_model_en: "Use one common primary model/harness first: preferably the exact qualified DeepSeek V4-Pro release; no 4×4 model matrix.",
    anchors: ["No Skill", "Initial / Parent Skill", "WIN-C", "Universal MRW4 / prospectively frozen public-compatible alternative"],
    closest_baselines: ["RethinkSkill Normal", "RethinkSkill Success-only", "RethinkSkill Fail-only", "SkillOpt"],
    contrastive_baseline_zh: "至少 1 个 credible trajectory-to-skill / contrastive baseline：优先 source-faithful Trace2Skill；否则清楚标注 SkillCAT-style reconstruction。",
    contrastive_baseline_en: "At least one credible trajectory-to-skill / contrastive baseline: prefer source-faithful Trace2Skill; otherwise clearly label a SkillCAT-style reconstruction.",
    evaluation_zh: "方法主表：所有最终 frozen artifacts 在同一 280 heldout tasks 上评估；若 evolution 本身随机，用预注册的 3 个 paired full-evolution seeds；heldout 重复只量化 measurement noise。Causal transport 另用同一自然 unit 的 common S0/T_K/served action，仅改变 g(T_K)。",
    evaluation_en: "Method table: evaluate all final frozen artifacts on the same 280 heldout tasks; if evolution itself is stochastic, use 3 preregistered paired full-evolution seeds, while heldout repeats quantify measurement noise only. Causal transport separately fixes common S0/T_K/served action per natural unit and changes only g(T_K).",
    transport_stop_zh: "transport 不支持时，不换 benchmark、不改 eligibility、不挖 subgroup、不用第二模型 rescue。",
    transport_stop_en: "If transport is unsupported, do not swap benchmark, alter eligibility, mine subgroups, or use a second model as rescue."
  },
  optional_after_required: [
    {id:"D1",zh:"一个第二模型 robustness：Qwen sparse 35B-class 或 Kimi K3，二选一。",en:"One second-model robustness lane: Qwen sparse 35B-class or Kimi K3, choose one."},
    {id:"D2",zh:"Failure-specific diagnostic：只有要声称 failure-specific causal value 才开。",en:"Failure-specific diagnostic only if the paper wants a failure-specific causal-value claim."},
    {id:"D3",zh:"Source-faithful appendix reproductions：验证 baseline adapter fidelity，不参与跨 split 直接排名。",en:"Source-faithful appendix reproductions to validate baseline-adapter fidelity; no direct cross-split ranking."},
    {id:"D4",zh:"SpreadsheetBench 2：只有回答新的 workflow-level question 才开。",en:"SpreadsheetBench 2 only if it answers a new workflow-level question."}
  ],
  rq: [
    {id:"RQ1",zh:"有没有 serving-induced censoring？",en:"Is serving-induced censoring measurable?"},
    {id:"RQ2",zh:"learner projection 是否具有 causal consequence？",en:"Does learner projection have a causal consequence?"},
    {id:"RQ3",zh:"projection effect 是否被 task/evidence structure 调节？",en:"Is the projection effect modified by task/evidence structure?"},
    {id:"RQ4",zh:"是否存在真正 positive 的 controlled act/learn divergence？",en:"Is there genuine positive controlled act/learn divergence?"},
    {id:"RQ5",zh:"能否 transport 到 natural public tasks，并与 closest methods 公平比较？",en:"Does the effect transport to natural public tasks and compare fairly with closest methods?"}
  ],
  workload_rule: {
    verdict: "CONTROLLED_WORKLOAD_SUFFICIENT_MISSING_PUBLIC_EVIDENCE_TYPE",
    zh: "Controlled workload 已经足够；后续不按 rollout/GPU/model/benchmark 数量堆工作量，只允许能新增可识别科学信息的 tranche。",
    en: "Controlled workload is already sufficient. Future workload is admitted only when it adds identifiable scientific information—not because it adds rollouts, GPU hours, models, or benchmarks.",
    admit_if_zh: ["服务新的 paper-level claim", "排除 verdict-changing alternative explanation", "补 external validity / transport", "提供 fair closest-method baseline", "把测量不确定性降到会改变预注册决策边界"],
    admit_if_en: ["serves a new paper-level claim", "removes a verdict-changing alternative explanation", "adds external validity / transport", "provides a fair closest-method baseline", "reduces measurement uncertainty enough to change a preregistered decision boundary"]
  },
  plan_artifacts: {
    roadmap: "consultations/e2-r17-experiment-plan-v4-20260904.md",
    execution_map: "consultations/e2-r17-experiment-plan-v4-execution-map-20260904.md",
    paper_outline: "paper_drafts/e2-r17-paper-outline-skillzip-iteration-20260903.md",
    scope_calibration: "consultations/e2-r17-premise-scope-calibration-frontend-20260905.md",
    r3_reset_readiness: "consultations/e2-r17-v3-stage-a-r3-reset-readiness-audit-20260905.md",
    plan_revision: "1e3db1ec2d25addddde2112f7871223f1e3d0728"
  }
};
