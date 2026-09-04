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
      id:"paper-e1",paper:"E1 · STRI",tier:"low",costDriver:{zh:"CPU / 已有 artifact 为主",en:"CPU / existing artifacts"},
      gpu:{zh:"canonical 结构证据不需要 GPU；当前没有新增 GPU 主预算。",en:"Canonical structural evidence needs no GPU; no material new GPU budget is currently required."},
      cpu:{zh:"support-matrix / LP / robustness / artifact replay 与少量 Docker 行为桥。",en:"Support-matrix/LP/robustness/artifact replay plus a small Docker behavioral bridge."},
      api:{zh:"canonical 主张几乎不需要新增 API。ReasoningBank Full-P1 扩展曾冻结 deepseek-v4-pro-ga-260813，40/40 run 已执行但扩展 HOLD。",en:"Canonical claims need almost no new API spend. The ReasoningBank Full-P1 extension froze deepseek-v4-pro-ga-260813; 40/40 runs executed but the extension remains on HOLD."},
      envelope:{zh:"当前新增：≈0 GPU；扩展未重新开放前，模型服务支出≈0。",en:"Current incremental: ≈0 GPU; ≈0 provider spend until the extension reopens."},
      cash:{zh:"低；主要是已发生的历史 API / 工程成本。",en:"Low; mostly sunk historical API/engineering cost."},
      atomgit:{status:"engineering",label:{zh:"工程可用 · 科学替换禁止",en:"Engineering yes · scientific replacement no"},use:{zh:"适合做论文/表格、静态审计、测试修复、Full-P1 失败日志定位；不能把 deepseek-v4-flash 替换 frozen DeepSeek V4 Pro 后继续旧实验。",en:"Useful for paper/table work, static audits, test repair, and Full-P1 failure triage; deepseek-v4-flash cannot replace the frozen DeepSeek V4 Pro inside the old experiment."}}
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
      id:"paper-e2",paper:"E2 · State Regeneration R5",tier:"high",costDriver:{zh:"DeepSeek V4 Pro 商业模型调用；当前仍被 quota / fresh identity 硬门约束",en:"DeepSeek V4 Pro commercial model calls, currently gated by quota and fresh identity"},
      gpu:{zh:"当前 E2/R5 不要求本地训练 GPU；主要科学成本来自 Ark Plan actor/updater calls。",en:"Current E2/R5 does not require local training GPUs; scientific cost is dominated by Ark Plan actor/updater calls."},
      cpu:{zh:"runner / SpreadsheetBench / MindMemOS、content-addressed state/trajectory bookkeeping、completion audit 与独立 analysis authorization。",en:"Runner/SpreadsheetBench/MindMemOS, content-addressed state/trajectory bookkeeping, completion audits, and separately authorized analysis."},
      api:{zh:"V2 的 48 pairs / 96 states / 1,728 held-out 已是完成证据，不再继续付费扩同类 volume。M2 Recovery V3 只允许继承 45 个有效 completed units 并补 27 个 remaining；M3R4 设计为 72 个 actor-only logical units、0 updater，当前 scientific provider calls=0，且旧 2026-08-31 model identity 明确不可复用。Bridge V4-R2 仍是 zero-provider pre-execution design。",en:"V2's 48 pairs / 96 states / 1,728 held-out evaluations are completed evidence and will not be expanded merely for volume. M2 Recovery V3 may inherit 45 valid completed units and execute only 27 remaining units. M3R4 is 72 actor-only logical units with zero updater calls; current scientific provider calls are zero and the 2026-08-31 model identity is explicitly non-reusable. Bridge V4-R2 remains a zero-provider pre-execution design."},
      envelope:{zh:"M3R4 的 actor-only structural hard ceiling 是 720 calls = 72 logical units × 10 max turns，per-unit 10、provider retry 0；这是最坏结构上限，不是预计实际 calls。Bridge / SkillRevise / SkillOpt / public transport 都没有当前执行 authority，只有 Q1 fresh PASS 后才单独预算。",en:"M3R4's actor-only structural hard ceiling is 720 calls = 72 logical units × 10 max turns, with per-unit 10 and provider retry 0. This is a worst-case structural ceiling, not an expected call count. Bridge, SkillRevise, SkillOpt, and public transport have no current execution authority and receive separate budgets only after a fresh Q1 PASS."},
      cash:{zh:"当前增量现金≈0（quota/identity gate 期间）；恢复 scientific execution 后为高 API 成本线，但预算只投到 decisive M2/M3R4/M4 gate，不再堆同 substrate cell。",en:"Incremental cash is currently ≈0 while quota/identity gates are closed. Once scientific execution resumes this remains a high-API-cost line, but spend is reserved for decisive M2/M3R4/M4 gates rather than more same-substrate cells."},
      atomgit:{status:"engineering",label:{zh:"高优先工程用 · 禁止替 frozen scientific identity",en:"High-priority engineering · no substitution for frozen scientific identity"},use:{zh:"可用于 runner/preflight、ledger lint、baseline adapter、静态审查与 publication tooling；不能把 deepseek-v4-flash/GLM 或新的 DeepSeek release 自动替换 fresh-contract 要求的 exact resolved identity。",en:"Useful for runner/preflight work, ledger linting, baseline adapters, static review, and publication tooling; deepseek-v4-flash/GLM or a new DeepSeek release cannot automatically replace the exact resolved identity required by a fresh scientific contract."}}
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
      api:{zh:"PRE-F0.5 冻结 12 个匹配 family、4 个能力校准 family + 8 个 F0 family，最大包络为 144 个 episode。2026-09-02 活跃能力校准线已进入 qwen3.7-plus R4 局部资格验证，F0 仍未授权。",en:"PRE-F0.5 freezes 12 matched families with 4 capability + 8 F0 and a maximum envelope of 144 episodes. As of 2026-09-02 the active capability lane is already in qwen3.7-plus R4 partial qualification; F0 remains unauthorized."},
      envelope:{zh:"当前主能力模型已经进入资格验证，不应为了价格在中途切换；后续科学结果仍必须等待能力门禁通过。",en:"The primary capability model has already entered qualification and should not be switched midstream for price reasons; scientific outcomes still wait on the capability gate."},
      cash:{zh:"中 · 主要是 qwen3.7-plus 等商业 actor 的 capability / 后续 F0 API 成本。",en:"Medium · mainly capability and later F0 API cost for the commercial qwen3.7-plus actor."},
      atomgit:{status:"future",label:{zh:"工程可用 · 未来新 arm 可候选",en:"Engineering yes · future new arm candidate"},use:{zh:"不要把当前 qwen3.7-plus 能力校准线中途换成计划内模型。AtomGit Pro 更适合做 AppWorld 执行框架与修复；若以后需要第二个主干模型做外部有效性实验，可从零开始前瞻预注册一个独立 AtomGit 实验臂，再冻结精确模型与 AtomCode 无界面调用合同。",en:"Do not switch the current qwen3.7-plus capability lane to CodingPlan mid-qualification. Use Pro for AppWorld harness/repair; if a second-backbone external-validity experiment is later needed, preregister a fresh AtomGit arm from scratch and freeze the exact model plus AtomCode headless/daemon invocation contract."}}
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
