window.CURRENT_PAPER_BUDGET={
  schema_version:"1.0",
  as_of:"2026-09-02",
  policy:{
    reader_facing_budget_projection_only:true,
    does_not_grant_scientific_authority:true,
    does_not_grant_provider_authority:true,
    does_not_grant_gpu_authority:true,
    hard_caps_are_not_expected_spend:true,
    frozen_model_identity_cannot_be_replaced_for_cost_reasons:true
  },
  atomgit:{
    plan:"AtomGit CodingPlan Pro",
    account_window:"500 requests / 5h rolling window",
    token_policy:{zh:"总 Token 不设月度总量上限；主要约束是 5 小时滚动窗口的请求次数。",en:"No monthly total-token cap is imposed by the plan; the primary constraint is requests per five-hour rolling window."},
    models:["qwen3.8-27b","deepseek-v4-flash","GLM-5.2"],
    automation:{zh:"AtomCode 支持 headless CLI 与本地 daemon，因此可接入 lint / test / artifact audit / log triage / code repair 等科研工程流水线。",en:"AtomCode supports a headless CLI and local daemon, so it can drive lint/test/artifact-audit/log-triage/code-repair research-engineering pipelines."},
    rule:{zh:"默认把专业版当“科研工程算力”，而不是把计划内模型偷偷替换进已冻结的科学实验。只有在模型和服务商尚未冻结、并且先完成前瞻性方案修订与独立校准时，才可以把它升级为科学执行候选。",en:"Treat Pro as research-engineering capacity by default, not as a hidden replacement for frozen scientific treatments. It can become a scientific-execution candidate only before model/provider freeze and after a prospective amendment plus disjoint calibration."},
    sources:[
      {label:"AtomGit CodingPlan",url:"https://ai.atomgit.com/serverless-api"},
      {label:"CodingPlan dashboard",url:"https://ai.atomgit.com/dashboard/coding-plan"},
      {label:"AtomCode Headless / Daemon",url:"https://atomcode.atomgit.com/docs/zh/headless-daemon.html"}
    ]
  },
  spendPlan:{
    headline:{zh:"现金预算按“固定订阅 + 按量兜底 + 自有 GPU”拆开；不要把硬上限直接当成预计支出。",en:"Split cash planning into fixed subscriptions, pay-as-you-go fallback, and owned GPUs; never treat a hard ceiling as expected spend."},
    monthly:{zh:"新增 Ark 池先按 Medium ¥200/月做基准；只有额度或并发不够才升到 ¥500 / ¥1000，因为三档满额 AFP 单价相同。若账户仍显示 ¥49.9 优惠价则按实际付款记账。AtomGit Pro 已开通后，工程任务的边际 Token 现金成本按≈¥0看。",en:"Start a new Ark pool at Medium ¥200/month; move to ¥500/¥1000 only for capacity or concurrency because the full-use AFP unit price is the same across standard tiers. If the account still shows a ¥49.9 promotion, book the actual charge. Once AtomGit Pro is active, marginal token cash cost for engineering work is treated as ≈¥0."},
    pools:[
      {name:"AtomGit Pro",cash:{zh:"已开通 · 工程边际≈¥0",en:"Already active · engineering marginal ≈¥0"},papers:{zh:"9/9 都可承担工程任务",en:"Engineering work across all 9 papers"},rule:{zh:"优先承担代码修复、测试、日志审计、论文与数据管线工作；当前九篇里没有一条已冻结或正在执行的科学实验线允许直接换成计划内模型。",en:"Absorb code repair, tests, log audits, paper work, and data pipelines first; none of the nine current frozen/active scientific lanes permits a direct model swap to CodingPlan."}},
      {name:"Ark Agent Plan",cash:{zh:"Medium ¥200/月起；¥500 / ¥1000 主要增加容量与并发",en:"Starts at Medium ¥200/month; ¥500/¥1000 mainly add capacity and concurrency"},papers:{zh:"优先给确实需要商业大模型、且精确模型与接口仍符合冻结合同的实验线",en:"Prioritize commercial-model lanes only when the exact model and interface match the frozen contract"},rule:{zh:"E2 / Constraint 等先核对精确模型；C1 的 Qwen397、E2 的 DeepSeek V4 Pro 不能因为套餐便宜就换成近似模型。",en:"Verify exact models for E2/Constraint; C1 Qwen397 and E2 DeepSeek V4 Pro cannot be replaced by approximate models just because a plan is cheaper."}},
      {name:"典名词元 / 按量 API",cash:{zh:"按当前标价与真实账单计费；详细综合单价统一看实验成本页",en:"Bill at current posted prices and observed receipts; use the Experiment Costs page for composite unit prices"},papers:{zh:"给必须保持精确商业模型、但订阅套餐覆盖不了的调用兜底",en:"Fallback for exact commercial-model calls not covered by subscriptions"},rule:{zh:"主要价值是精确模型兜底，不建议为了“把余额用掉”增加实验。",en:"Its value is exact-model fallback; do not add experiments merely to consume balance."}},
      {name:"自有 GPU 池",cash:{zh:"直接 API 现金≈¥0；单独记电力 / 占卡 / 机会成本",en:"Direct API cash ≈¥0; track electricity/occupancy/opportunity cost separately"},papers:{zh:"B1、Paper A、Paper B、3D；G1 本地评测器也可进池",en:"B1, Paper A, Paper B, 3D; G1 local evaluator can also use the pool"},rule:{zh:"共享 checkpoint / simulator / cache / dataset，避免把同一底层工件在不同论文重复训练或下载。",en:"Share checkpoints, simulators, caches, and datasets to avoid retraining or redownloading the same substrate across papers."}}
    ],
    sources:[
      {label:"本站 · 实验成本详细页",url:"experiment-costs.html"},
      {label:"Ark Agent Plan / AFP 规则",url:"https://www.volcengine.com/docs/82379/2366394?lang=zh"},
      {label:"典名词元价格",url:"https://www.aa.com.cn/pricing"}
    ]
  },
  rows:[
    {
      id:"paper-e1",paper:"E1 · STRI",tier:"medium",costDriver:{zh:"V4 Hosted API + 阶段 gate",en:"V4 hosted API + staged gates"},
      gpu:{zh:"canonical 结构证据不需要 GPU；V4 软件 Agent 明确改为 hosted API-only，不再自托管 Qwen3.5-35B-A3B-FP8，也不为 E1 占用 A100 serving。除普通 Docker/CPU 环境外，V4 scientific actor 的本地 GPU 预算记为≈0。",en:"Canonical structural evidence needs no GPU. V4 is now explicitly hosted-API-only: no self-hosted Qwen3.5-35B-A3B-FP8 and no A100 serving reserved for E1. Apart from ordinary Docker/CPU execution, local GPU budget for the V4 scientific actor is ≈0."},
      cpu:{zh:"support-matrix / LP / artifact replay 仍主要是 CPU；V4 额外需要 SWE-bench Docker、trajectory bookkeeping、R2/R3/R4 分层分析。",en:"Support-matrix/LP/artifact replay remains CPU-heavy; V4 adds SWE-bench Docker, trajectory bookkeeping, and staged R2/R3/R4 analysis."},
      api:{zh:"Qwen3-Coder-Next V3 在 12/32 source 已产生 52.8M 输入 token、1,422 次调用并因 credit 停止，因此不再直接续跑。V4 改为 hosted Qwen API-only：先用 non-scientific capability / cost preflight 前瞻冻结一个 exact model + provider，再只开最小 P0；P0 开始后禁止因为价格或效果切模型。",en:"Qwen3-Coder-Next V3 used 52.8M input tokens and 1,422 calls by source 12/32 and stopped on credit, so it will not simply continue. V4 is now hosted-Qwen-API-only: a non-scientific capability/cost preflight must prospectively freeze one exact model + provider before the minimal P0, with no model switching after P0 begins."},
      envelope:{zh:"新预算按 gate 打开：P0 约 12–24 trajectories；通过后 P1 约 48；再通过才 P2 约 100–180；P3 跨 repo replication 约 48–72。任一 gate 无清晰信号即 STOP/PIVOT。",en:"Budget opens by gate: roughly 12–24 P0 trajectories, then ~48 P1, then ~100–180 P2 only if prior gates pass; P3 cross-repository replication is ~48–72. Any weak gate triggers STOP/PIVOT."},
      cash:{zh:"E1 接受用 API 现金换取 A100 释放：不再追求本地 serving 的≈0 现金，而是把 P0/P1/P2/P3 的 calls / input / output token 分别硬封顶。P0 receipt 出来后再外推后续阶段预算，避免再次按 432-run 一次性烧开。",en:"E1 now deliberately trades API cash for releasing A100 capacity. Instead of targeting near-zero cash via local serving, each P0/P1/P2/P3 stage gets hard caps on calls/input/output tokens; later-stage budgets are projected only from P0 receipts rather than opening the old 432-run envelope at once."},
      atomgit:{status:"engineering",label:{zh:"工程可用 · V4 actor 需单独冻结",en:"Engineering yes · V4 actor must be frozen separately"},use:{zh:"适合写/审 runner、token ledger、Docker preflight、trajectory analyzer 与页面；不能把 CodingPlan 模型直接当成尚未冻结的 V4 scientific actor。",en:"Useful for runner work, token ledgers, Docker preflight, trajectory analyzers, and paper/site updates; CodingPlan models cannot silently become the unfrozen V4 scientific actor."}}
    },
    {
      id:"paper-g1",paper:"G1 · Agent Safety R9",tier:"low",costDriver:{zh:"CPU/Web 环境 + evaluator",en:"CPU/web environment + evaluators"},
      gpu:{zh:"BrowserART actor 本身不是训练型 GPU 大户；本地 HarmBench-Llama-2-13B evaluator 路线可占用 A100 80GB 级 GPU。",en:"The BrowserART actor is not a training-heavy GPU workload; the local HarmBench-Llama-2-13B evaluator path can use an A100-80GB-class GPU."},
      cpu:{zh:"BrowserART / AWM 浏览器环境、persistent-state replay、trajectory 与标签审计。",en:"BrowserART/AWM browser environments, persistent-state replay, trajectories, and label auditing."},
      api:{zh:"历史双评价器包含 DeepSeek；当前真正 blocker 是 blinded human semantic labels，而不是继续堆模型调用。",en:"Historical dual evaluation includes DeepSeek; the current real blocker is blinded human semantic labels, not more model calls."},
      envelope:{zh:"当前剩余模型预算低；优先付出人工标注而不是新增 LLM evaluator。",en:"Remaining model budget is low; prioritize human labeling rather than another LLM evaluator."},
      cash:{zh:"低；新增现金主要可能来自人工标注。",en:"Low; incremental cash is more likely human-label cost."},
      atomgit:{status:"engineering",label:{zh:"工程可用 · 不能替代人标",en:"Engineering yes · cannot replace humans"},use:{zh:"可做 BrowserART harness、label UI、审计脚本、paper repair；不能用 CodingPlan 模型冒充独立 human semantic anchor。",en:"Useful for BrowserART harnesses, label UIs, audit scripts, and paper repair; a CodingPlan model cannot stand in for the independent human semantic anchor."}}
    },
    {
      id:"paper-c1",paper:"C1 · Stage-Resolved Transport",tier:"medium",costDriver:{zh:"canonical 已收口；扩展是 API 型",en:"Canonical closed; extension is API-heavy"},
      gpu:{zh:"canonical 不依赖本地大模型训练 GPU。",en:"Canonical work does not require local large-model training GPUs."},
      cpu:{zh:"Shopping / Reddit paired replay、native retrieval / first-action / terminal 分层分析。",en:"Shopping/Reddit paired replay and stage-resolved retrieval/first-action/terminal analysis."},
      api:{zh:"核心论文已 SUBMISSION_READY。PACTA / ReasoningBank 扩展候选使用 Qwen397；当前因来源轨迹溯源问题保持 HOLD，在重新开放前不应继续消耗 API。",en:"Canonical paper is SUBMISSION_READY. The PACTA/ReasoningBank extension candidate uses Qwen397 and is held on source-trajectory provenance, so provider spend should stay closed until reopen."},
      envelope:{zh:"HOLD 期间新增科学 API≈0；重新开放后才进入 Qwen397 模型服务预算池。",en:"Incremental scientific API ≈0 while on HOLD; Qwen397 provider spend begins only after a valid reopen."},
      cash:{zh:"当前低；若扩展重开则升为中/高 API 成本。",en:"Low now; medium/high API cost if the extension reopens."},
      atomgit:{status:"engineering",label:{zh:"工程可用 · Qwen397 不可替代",en:"Engineering yes · Qwen397 not replaceable"},use:{zh:"优先用 Pro 做 provenance compiler、receipt 检查、source trajectory 工具与测试；qwen3.8-27b 不是 Qwen397 的等价替代。",en:"Use Pro for provenance compilers, receipt checks, source-trajectory tooling, and tests; qwen3.8-27b is not an equivalent replacement for Qwen397."}}
    },
    {
      id:"paper-e2",paper:"E2 · R17",tier:"high",costDriver:{zh:"DeepSeek V4 Pro 商业模型调用",en:"DeepSeek V4 Pro 商业模型调用"},
      gpu:{zh:"当前 R17 主执行不要求本地训练 GPU。",en:"The current R17 execution does not require local training GPUs."},
      cpu:{zh:"runner / actor / MindMemOS / heldout bookkeeping 与 analyzer（完整结束后才允许）。",en:"Runner/actor/MindMemOS/held-out bookkeeping and the analyzer, which stays closed until completion."},
      api:{zh:"冻结的主模型是 DeepSeek V4 Pro。当前页面记录 17/48 对、36/96 个学习后状态、636/1728 个留出评测单元、609 次模型服务额度声明；剩余续跑仍是主要成本。",en:"The frozen primary is DeepSeek V4 Pro. The current paper state records 17/48 pairs, 36/96 learned states, 636/1728 held-out evaluations, and 609 provider claims; the remaining continuation is the main cost."},
      envelope:{zh:"剩余 31 对 / 60 个学习后状态 / 1092 个留出评测单元；模型服务上限继续由各续跑子合同单独约束，不能用一个粗略 Token 数替代。",en:"31 pairs / 60 learned states / 1,092 held-out evaluations remain; provider ceilings continue to be governed by each continuation child contract rather than a coarse token estimate."},
      cash:{zh:"高 · 九篇里最明确的持续商业 API 成本之一。",en:"High · one of the clearest continuing commercial-API costs in the portfolio."},
      atomgit:{status:"engineering",label:{zh:"高优先工程用 · 禁止替 frozen Pro",en:"High-priority engineering · no frozen-Pro substitution"},use:{zh:"很适合让 deepseek-v4-flash/GLM 做 runner repair、preflight、ledger lint、failure triage 与独立代码审查；但旧 Repair2/continuation 的科学 actor 必须保持 frozen DeepSeek V4 Pro。",en:"Excellent for runner repair, preflight, ledger linting, failure triage, and independent code review; the scientific actor in the existing Repair2/continuation must remain frozen DeepSeek V4 Pro."}}
    },
    {
      id:"paper-b1",paper:"B1 · Failure Memory Provenance",tier:"medium",costDriver:{zh:"本地 A100 推理 + Docker",en:"Local A100 inference + Docker"},
      gpu:{zh:"活跃 full350 lane 使用 231 的 NVIDIA A100-SXM4-80GB；Qwen2.5-7B-Instruct 与 all-mpnet-base-v2 同卡，本地推理。",en:"The active full350 lane uses an NVIDIA A100-SXM4-80GB on host 231; Qwen2.5-7B-Instruct and all-mpnet-base-v2 run locally on the same GPU."},
      cpu:{zh:"MemRL / MemoryOS、OSInteraction Docker 环境、source-bank build 与 AB bookkeeping。",en:"MemRL/MemoryOS, OSInteraction Docker environments, source-bank construction, and A/B bookkeeping."},
      api:{zh:"活跃 full350 执行清单采用本机回环服务，本地运行 Qwen2.5-7B；外部模型服务调用为 0。",en:"The active full350 execution manifest is loopback-only with local Qwen2.5-7B; external provider calls = 0."},
      envelope:{zh:"350 source tasks；GPU 成本是服务器占用，不是按 Token 付费。该 lane 仍属 2026-09-02 活跃执行分支，科学状态以其独立 receipt 为准。",en:"350 source tasks; cost is GPU occupancy rather than per-token billing. This is an active 2026-09-02 execution lane whose scientific state remains governed by its own receipts."},
      cash:{zh:"若使用现有 231：直接 API 现金≈0，主要是 A100 机会/电力成本。",en:"On existing host 231: direct API cash ≈0; the main cost is A100 opportunity/electricity cost."},
      atomgit:{status:"engineering",label:{zh:"工程可用 · 科学侧没必要替换",en:"Engineering yes · no scientific need to replace"},use:{zh:"Pro 最适合帮助写/审 MemRL adapter、Docker、source-bank / A-B 工具与失败恢复；不能降低已经接近 0 的科学 API 现金成本。",en:"Best used for MemRL adapters, Docker, source-bank/A-B tooling, and recovery; it cannot materially reduce scientific API cash that is already near zero."}}
    },
    {
      id:"paper-a",paper:"Paper A · Influence–Fidelity",tier:"medium",costDriver:{zh:"本地 VLA GPU rollout",en:"Local VLA GPU rollouts"},
      gpu:{zh:"MemoryVLA same-state counterfactual / rollout 需要本地 VLA GPU；当前论文合同尚未冻结统一 GPU 型号或 GPU-hour ceiling。",en:"MemoryVLA same-state counterfactuals/rollouts require a local VLA GPU; the paper contract has not yet frozen a universal GPU model or GPU-hour ceiling."},
      cpu:{zh:"LIBERO-Plus simulator、same-state snapshot / reset、wrong-memory / placebo control 生成与分析。",en:"LIBERO-Plus simulation, same-state snapshot/reset, and wrong-memory/placebo control generation and analysis."},
      api:{zh:"当前科学 actor 是本地 MemoryVLA 路线，没有商业 LLM API 预算。",en:"The current scientific actor is a local MemoryVLA path with no commercial LLM API budget."},
      envelope:{zh:"development 为 task0–2；当前重点是 correct / wrong / placebo 的 content-specific counterfactual，完整 confirmatory GPU 规模尚未冻结。",en:"Development uses task0–2; current focus is content-specific correct/wrong/placebo counterfactuals, while the full confirmatory GPU envelope is not yet frozen."},
      cash:{zh:"中 · 主要是现有 GPU wall-time；与 Paper B 可共享底层 VLA / LIBERO 基础设施。",en:"Medium · mainly existing GPU wall time; base VLA/LIBERO infrastructure can be shared with Paper B."},
      atomgit:{status:"engineering",label:{zh:"工程高适配 · 不替 VLA rollout",en:"Strong engineering fit · not a VLA replacement"},use:{zh:"可承担 counterfactual harness、snapshot、placebo 生成器、结果审计和第二 VLA 接入代码；CodingPlan 模型不能代替 MemoryVLA policy rollout。",en:"Useful for counterfactual harnesses, snapshots, placebo generators, result audits, and second-VLA integration; CodingPlan models cannot replace MemoryVLA policy rollouts."}}
    },
    {
      id:"paper-b",paper:"Paper B · Persistent Memory",tier:"medium",costDriver:{zh:"本地 VLA GPU + longitudinal rollout",en:"Local VLA GPU + longitudinal rollouts"},
      gpu:{zh:"MemoryVLA / frozen-base VLA rollout；GPU 型号与最终 GPU-hour ceiling 尚未冻结。",en:"MemoryVLA/frozen-base VLA rollouts; exact GPU model and final GPU-hour ceiling are not yet frozen."},
      cpu:{zh:"LIBERO-Plus simulator、persistent-memory state machine、future re-exposure 与 write-back ledger。",en:"LIBERO-Plus simulation, persistent-memory state machine, future re-exposure, and write-back ledgers."},
      api:{zh:"当前没有商业 LLM scientific API 主预算。",en:"There is no current commercial-LLM scientific API budget."},
      envelope:{zh:"task0–2 × 4 perturbations × 2 levels = 24 development scopes；future longitudinal confirmatory 另行冻结。",en:"task0–2 × four perturbations × two levels = 24 development scopes; future longitudinal confirmatory work will be frozen separately."},
      cash:{zh:"中；比 Paper A 更容易被 longitudinal rollout 放大，但二者应共享底层 checkpoint / simulator / infrastructure。",en:"Medium; longitudinal rollouts can make it larger than Paper A, but the two should share base checkpoints/simulator/infrastructure."},
      atomgit:{status:"engineering",label:{zh:"工程高适配 · 用于 slow-loop 系统",en:"Strong engineering fit · use for slow-loop systems"},use:{zh:"适合实现 admission→verify→commit→reuse 状态机、队列、checkpoint/ledger 与回归测试；不能把 CodingPlan 模型当作具身 policy。",en:"Good for the admission→verify→commit→reuse state machine, queues, checkpoint/ledger handling, and regressions; CodingPlan models are not the embodied policy."}}
    },
    {
      id:"paper-agent-constraint",paper:"Constraint Externality",tier:"medium",costDriver:{zh:"AppWorld CPU + future LLM actor",en:"AppWorld CPU + future LLM actor"},
      gpu:{zh:"当前不需要本地 GPU 训练。",en:"No local GPU training is currently required."},
      cpu:{zh:"AppWorld app/database reset、container、trajectory collection 与 exactly-once ledger。",en:"AppWorld app/database reset, containers, trajectory collection, and exactly-once ledgers."},
      api:{zh:"旧 4+8 / 144-episode 包络已不再适用。MiMo capability PASS，但旧 F0 source 8/8 success 后 mandatory stop。当前只冻结 12-case Direct-SFQ-A0。2026-09-05 readiness R1 因 credential 未注入而 0-request STOP；随后 R2 安全恢复同一 approved credential，并按冻结契约只发 1 次 synthetic request，得到 HTTP 400 / insufficient_credit。当前 blocker 已明确为 frozen provider 可用额度不足，不是模型能力或机制结果。",en:"The old 4+8 / 144-episode envelope no longer applies. MiMo passed capability, but the old F0 source stopped after 8/8 successes. Only the 12-case Direct-SFQ-A0 is currently frozen. Readiness R1 on 2026-09-05 stopped with zero requests because the credential was absent; R2 then securely restored the same approved credential and sent exactly one frozen-contract synthetic request, which returned HTTP 400 / insufficient_credit. The current blocker is therefore insufficient usable credit on the frozen provider, not a model-capability or mechanism result."},
      envelope:{zh:"恢复/充值同一 frozen provider 的可用额度 → 新 provider-readiness authority → 单次 zero-tool/zero-retry readiness。只有 PASS 后再单独授权 R2 capability → Direct-SFQ-A0。source gate 通过后：24-family reserve → TARGET_ONLY_VERIFICATION 冻结 eligibility → outcome 前冻结 N*/R*。进入 I/L/H 后 target outcome 只报告、不筛 family；禁止 effect-driven 扩样。",en:"Restore/top up usable credit on the same frozen provider → fresh provider-readiness authority → one zero-tool/zero-retry readiness request. Only after PASS may separate R2 capability authority open → Direct-SFQ-A0. After the source gate: 24-family reserve → TARGET_ONLY_VERIFICATION freezes eligibility → freeze N*/R* before outcomes. After entry into I/L/H, target outcomes are reported rather than filtered; no effect-driven expansion."},
      cash:{zh:"中 · 近期只需 capability recovery + 12-case SFQ。若 source gate 通过，先做 target-only eligibility verification，再冻结默认高效主机制目标 N*=16、R*=2（192 probes）+ 8-family sham control（32）；RQ3/RQ4/跨模型均按前一层 PASS 条件打开，而不是预先跑满最大 envelope。",en:"Medium · near-term cost is limited to capability recovery plus the 12-case SFQ. If the source gate passes, run target-only eligibility verification first, then freeze the efficient default mechanism target N*=16, R*=2 (192 probes) plus an 8-family sham control (32); RQ3, RQ4, and cross-model checks open only after upstream PASS rather than exhausting a maximum envelope up front."},
      atomgit:{status:"engineering",label:{zh:"只用于工程 · 不再作为这篇论文的 scientific actor",en:"Engineering only · no longer the scientific actor"},use:{zh:"CodingPlan/AtomCode 可继续用于 runner、ledger、AppWorld 工程和静态构造，但 native-tool/persona contamination 已证明它不适合当前 clean scientific actor contract。",en:"CodingPlan/AtomCode may still support runner, ledger, AppWorld engineering, and static construction, but native-tool/persona contamination makes it unsuitable for the current clean scientific-actor contract."}}
    },
    {
      id:"paper-3d",paper:"3D · Relational Topology",tier:"very-high",costDriver:{zh:"A100 80GB 官方训练",en:"A100-80GB official training"},
      gpu:{zh:"目标硬件 A100 80GB 或经 exact-batch preflight 证明的等价卡；当前 developmental plan 有 3 个独立组件，可最多并行 3 卡。",en:"Target hardware is A100 80GB or equivalent proven by an exact-batch preflight; the developmental plan has three independent components and allows up to three concurrent GPUs."},
      cpu:{zh:"3D-FRONT / 3D-FUTURE 解包、语料构造、dataloader workers、checkpoint / hash / provenance。",en:"3D-FRONT/3D-FUTURE extraction, corpus construction, dataloading, checkpoint/hash/provenance work."},
      api:{zh:"科学主实验不使用商业 LLM API。",en:"The scientific main experiment does not use a commercial LLM API."},
      envelope:{zh:"BEDROOM-SG2SC-SHARED + SGP-12 + SGP-14：每个 batch=128、1,000,000 optimizer steps、1 developmental seed；50k checkpoint，三组件全保留约 38.2 GiB。exact batch-128 forward/backward preflight 通过前，禁止外推 GPU-hours。",en:"BEDROOM-SG2SC-SHARED + SGP-12 + SGP-14: each uses batch 128, 1,000,000 optimizer steps, and one developmental seed; checkpoints every 50k total about 38.2 GiB if retained. GPU-hours must not be extrapolated before the exact batch-128 forward/backward preflight passes."},
      cash:{zh:"最高 · 主要是 GPU wall-time / 占卡机会成本，而不是 API token。",en:"Very high · dominated by GPU wall time/opportunity cost rather than API tokens."},
      atomgit:{status:"engineering",label:{zh:"工程高适配 · 不能省训练 GPU",en:"Strong engineering fit · cannot replace training GPU"},use:{zh:"非常适合写训练 orchestration、resource preflight、checkpoint/heartbeat、failure recovery、dataset/provenance audit；但不会替代 InstructScene 的 A100 训练。",en:"Excellent for training orchestration, resource preflight, checkpoints/heartbeats, failure recovery, and dataset/provenance audits; it does not replace InstructScene A100 training."}}
    }
  ]
};
