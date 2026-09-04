window.E2_R17_FRONTEND_STATUS = {
  schema_version: "1.0",
  as_of_date: "2026-09-04",
  project_track: "E2-R17",
  title: {
    zh: "解耦 Test-Time Search 的 Serving 与 Persistent Learning",
    en: "Decoupling Serving and Persistent Learning over Test-Time Search"
  },
  subtitle: {
    zh: "Exact-Same-Pool 因果识别 · Search-Projection Censoring · identity qualification 为下一条可执行资格门；Stage A/B/Public P1 科学权限仍关闭",
    en: "Exact-same-pool causal identification · Search-Projection Censoring · identity qualification is the next executable qualification gate; Stage A/B/Public P1 scientific authority remains closed"
  },
  paper_identity: "CAUSAL_SYSTEMS_INTERFACE_PAPER",
  scientific_object: {
    zh: "Search 先生成同一个 realized object T_K；当前行为消费 a(T_K)，持久学习消费 g(T_K)。核心实验固定 T_K 与 serving，只改变 learner-visible projection。",
    en: "Search first generates one realized object T_K; current behavior consumes a(T_K), while persistent learning consumes g(T_K). The core intervention fixes T_K and serving, changing only the learner-visible projection."
  },
  frozen_scientific_r2: {
    commit: "29799c83c662887694db52acba4bb19e83131bb0",
    contract_sha256: "f5382c552f2e6644e4cbda408510119664a8c6f8502628586c9ff5583abd1234",
    preflight_sha256: "e257438bd482d4f2209a8321d4a222bd97acf2c03bff46a1d5513b55a42ca766",
    changed_by_frontend: false
  },
  authority: {
    fresh_identity_qualification_permitted: true,
    fresh_identity_called: false,
    stage_a: false,
    stage_b: false,
    public_p1: false,
    baseline_execution: false,
    provider_calls_current_continuation: 0
  },
  next_gate: {
    code: "ONE_FRESH_DEEPSEEK_IDENTITY_THEN_LOCAL_ADJUDICATION_THEN_SEPARATE_STAGE_A_AUTH",
    zh: "当前已允许的下一边界：恰好 1 次 fresh DeepSeek identity qualification → 本地 adjudication → PASS 后另行签发一次性 Stage-A authorization。",
    en: "Current permitted next boundary: exactly one fresh DeepSeek identity qualification → local adjudication → if PASS, separately mint single-use Stage-A authorization."
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
      title_zh: "Fresh model identity gate",
      title_en: "Fresh model identity gate",
      status: "NEXT_EXECUTABLE",
      scale_zh: "1 次 provider identity call；无科学 outcome",
      scale_en: "1 provider identity call; no scientific outcome",
      gate_zh: "identity PASS 才能另行 mint Stage-A authorization。",
      gate_en: "Only identity PASS permits a separately minted Stage-A authorization."
    },
    {
      id: "B1",
      title_zh: "V3 Stage A · support acquisition",
      title_en: "V3 Stage A · support acquisition",
      status: "PLANNED_LOCKED",
      scale_zh: "5 skeletons · 20 streams · 160 tasks · K=8 · 1280 actor rollouts · 0 updater · 0 heldout",
      scale_en: "5 skeletons · 20 streams · 160 tasks · K=8 · 1280 actor rollouts · 0 updater · 0 heldout",
      gate_zh: "20/20 streams 都必须至少有 4 个 mixed pools；任一失败即 HOLD，不换 task/model/K。",
      gate_en: "All 20 streams must have at least 4 mixed pools; any failure causes HOLD with no task/model/K replacement."
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
    plan_revision: "1e3db1ec2d25addddde2112f7871223f1e3d0728"
  }
};
