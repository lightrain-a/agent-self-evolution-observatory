window.CURRENT_PAPER_EVIDENCE_PROFILES=window.CURRENT_PAPER_EVIDENCE_PROFILES||{};
Object.assign(window.CURRENT_PAPER_EVIDENCE_PROFILES,{
"paper-e1":{
 featured:[
  {title:"Reinforcement Learning for Self-Improving Agent with Skill Library (SAGE)",venue:"ACL",year:2026,url:"https://aclanthology.org/2026.acl-long.69/",relation:{zh:"ACL 2026 主会直接研究 self-improving skill library：技能在连续任务中积累并参与后续 rollout。",en:"ACL 2026 main-conference work directly studies self-improving skill libraries across sequential tasks."},boundary:{zh:"SAGE 优化技能生成与使用；E1 不再卖“技能库能自进化”，而是问 semantic capability 固定时，等价 package reparameterization 是否应保持控制不变。",en:"SAGE optimizes skill generation/use; E1 audits control invariance under semantics-preserving package reparameterization."}},
  {title:"Agent Workflow Memory",venue:"ICML",year:2025,url:"https://proceedings.mlr.press/v267/wang25bx.html",relation:{zh:"把历史成功轨迹归纳成可复用 workflow，并在后续任务检索使用。",en:"Induces reusable workflows from past trajectories and retrieves them on later tasks."},boundary:{zh:"它证明结构化经验组织有用，但没有把“只改表示、不改能力”当 treatment，也没有 exact representation-invariance certificate。",en:"It shows structured experience organization helps, but does not isolate representation-only change or derive an exact invariance certificate."}},
  {title:"ReasoningBank: Scaling Agent Self-Evolving with Reasoning Memory",venue:"ICLR",year:2026,url:"https://arxiv.org/abs/2509.25140",relation:{zh:"正式 ICLR 2026 self-evolving memory 工作，也是 E1 Full-P1 扩展采用的外部 substrate lineage。",en:"An ICLR 2026 self-evolving-memory paper and the external substrate lineage used by E1 Full-P1."},boundary:{zh:"ReasoningBank 改变的是可学习 reasoning memory；E1 核心仍是 capability/support 固定时的 package representation invariance。",en:"ReasoningBank changes learned reasoning memory; E1 keeps capability/support fixed and audits package representation invariance."}}
 ],
 experiment:{
  intro:{zh:"E1 有三层实验对象，不能混成一个 n：静态 support-matrix 理论审计、AutoSkill P19 行为 witness、以及后来的 SWE-bench Verified / ReasoningBank Full-P1 外部有效性扩展。",en:"E1 has three separately accounted objects: a static support-matrix audit, an AutoSkill P19 witness, and a later SWE-bench Verified / ReasoningBank Full-P1 extension."},
  sources:[
   {name:"SWE-bench",paper:"SWE-bench: Can Language Models Resolve Real-World GitHub Issues?",venue:"ICLR",year:2024,url:"https://openreview.net/forum?id=VTF8yNQM66",original:{zh:"原 benchmark 含 2,294 个真实 GitHub issue，来自 12 个 Python repository。",en:"The original benchmark has 2,294 real GitHub issues from 12 Python repositories."},slice:{zh:"Full-P1 只取前瞻冻结的 Django / Sphinx unseen tasks：8 个 task × 5 个 arm = 40 exactly-once runs。",en:"Full-P1 uses prospectively frozen unseen Django/Sphinx tasks: 8 tasks × 5 arms = 40 exactly-once runs."},transform:{zh:"任务内容与 executor 不作为 treatment；5 个 representation/control arm 只用于挑战 canonical E1 的行为外部有效性。",en:"Task content and executor are not the treatment; five representation/control arms challenge external validity."}},
   {name:"AutoSkill P19",paper:"Released AutoSkill behavioral substrate",venue:"Released substrate",year:2026,url:"",original:{zh:"不是公开 benchmark 总表，而是冻结的 P19 行为场景。",en:"Not a public benchmark table; a frozen P19 behavioral scene."},slice:{zh:"同一场景比较 original / split / placebo / quotient，并做 mediator add-back 与 matched cleanup。",en:"The same scene is compared under original/split/placebo/quotient plus mediator add-back and matched cleanup."},transform:{zh:"semantic capability 保持不变，只操纵 package representation。",en:"Semantic capability stays fixed while package representation changes."}},
   {name:"Frozen skill-support matrices",paper:"Project-constructed structural audit",venue:"Project construct",year:2026,url:"",original:{zh:"本项目构造/冻结的 support geometry，不冒充外部数据集。",en:"Project-constructed/frozen support geometry, not an external dataset."},slice:{zh:"同一 semantic support 下做 split / clone / regroup counterfactual。",en:"Split/clone/regroup counterfactuals under fixed semantic support."},transform:{zh:"计算 R*(A;q)，判断 package-only exposure 能否精确实现同一 semantic target。",en:"Compute R*(A;q) for exact target realizability under package-only exposure."}}
  ],
  models:[
   {name:"R*(A;q) exact solver",role:{zh:"静态理论被测对象；无 LLM。",en:"Static theoretical object; no LLM."},status:{zh:"canonical",en:"canonical"}},
   {name:"AutoSkill executor",role:{zh:"P19 行为 witness；executor/harness/top-k 固定。",en:"P19 witness with executor/harness/top-k fixed."},status:{zh:"canonical bounded witness",en:"canonical bounded witness"}},
   {name:"deepseek-v4-pro-ga-260813",role:{zh:"ReasoningBank Full-P1 外部扩展 backbone。",en:"Backbone for the ReasoningBank Full-P1 extension."},status:{zh:"extension only",en:"extension only"}}
  ],
  quantities:[
   {v:"2,294 / 12",k:{zh:"SWE-bench 原始 issue / repositories",en:"original SWE-bench issues / repositories"}},
   {v:"8 × 5 = 40",k:{zh:"Full-P1 frozen tasks × arms = runs",en:"Full-P1 frozen tasks × arms = runs"}},
   {v:"6/6 → 0/6",k:{zh:"P19 destructive signature：original → split-4",en:"P19 destructive signature: original → split-4"}},
   {v:"3/3 vs 0/3",k:{zh:"specific mediator add-back vs matched cleanup",en:"specific mediator add-back vs matched cleanup"}},
   {v:"R*(A;q)",k:{zh:"结构层 exact realizability endpoint",en:"structural exact-realizability endpoint"}}
  ],
  unit:{zh:"理论层单位是 support matrix；行为层单位是冻结 P19 场景；Full-P1 单位是 task-arm run，三层分别记账。",en:"Theory uses support matrices, behavior a frozen P19 scene, and Full-P1 task-arm runs; layers are separate."},
  treatment:{zh:"核心只改变 package identity / split / regroup；semantic support、能力内容、任务与 executor 保持不变。",en:"Only package identity/split/regroup changes; semantic support, capability content, task, and executor stay fixed."},
  readouts:["R*(A;q)","destructive signature","retrieval / mediator restoration","bounded behavior","extension integrity before paired inference"]
 }
},
"paper-g1":{
 featured:[
  {title:"SafeAgent: Safeguarding LLM Agents via an Automated Risk Simulator",venue:"ACL",year:2026,url:"https://aclanthology.org/2026.acl-long.1501/",relation:{zh:"ACL 2026 主会直接研究多轮、tool-augmented Agent safety，并用自动 risk simulator 构造风险场景。",en:"ACL 2026 main-conference work on multi-turn tool-augmented agent safety."},boundary:{zh:"SafeAgent 的核心是风险建模与安全改进；G1 不提出新 guard，而审计同一 persistent trajectory 的安全结论是否跨 evaluator 稳定。",en:"SafeAgent improves safety; G1 audits whether conclusions on the same persistent trajectories are evaluator-stable."}},
  {title:"PerMemSafe: Benchmarking Implicit Personalized Safety of Long Horizon Self-Evolving Agents",venue:"Findings ACL",year:2026,url:"https://aclanthology.org/2026.findings-acl.320/",relation:{zh:"最新正式长时 self-evolving Agent safety benchmark，把 memory accumulation 与 personalized safety 放进长 horizon。",en:"A recent formal long-horizon self-evolving-agent safety benchmark."},boundary:{zh:"它扩展被测安全场景；G1 的新轴是 measurement identification：换 evaluator 会不会改变 premise、event set 与 arm ordering。",en:"It broadens safety settings; G1 tests measurement identification across evaluators."}},
  {title:"Aligned LLMs Are Not Aligned Browser Agents (BrowserART)",venue:"ICLR",year:2025,url:"https://openreview.net/forum?id=NsFZZU9gvk",relation:{zh:"G1 的 browser-agent safety task substrate 来源；正式 ICLR 2025。",en:"The browser-agent safety task substrate lineage used by G1; ICLR 2025."},boundary:{zh:"BrowserART 测 harmful browser behavior；G1 增加 persistent-state temporal treatment 与双 evaluator identification。",en:"BrowserART measures harmful browser behavior; G1 adds persistent-state temporal treatment and dual-evaluator identification."}},
  {title:"AgentHarm: A Benchmark for Measuring Harmfulness of LLM Agents",venue:"ICLR",year:2025,url:"https://openreview.net/forum?id=AC5n7xHuR1",relation:{zh:"正式 agent-harm benchmark，110 malicious tasks（440 augmented）。",en:"A formal agent-harm benchmark with 110 malicious tasks (440 augmented)."},boundary:{zh:"AgentHarm 扩 harmful-task coverage；G1 研究 measurement conclusion 本身是否 evaluator-relative。",en:"AgentHarm expands harmful-task coverage; G1 studies evaluator-relative conclusions."}}
 ],
 experiment:{
  intro:{zh:"G1 的数据链由 BrowserART 行为场景、AWM workflow/memory 机制谱系、HarmBench evaluator 组成；我们再加入独立 DeepSeek evaluator 与 prospective PV1。",en:"G1 combines BrowserART behaviors, AWM workflow/memory lineage, HarmBench as one evaluator, an independent DeepSeek evaluator, and prospective PV1."},
  sources:[
   {name:"BrowserART",paper:"Aligned LLMs Are Not Aligned Browser Agents",venue:"ICLR",year:2025,url:"https://openreview.net/forum?id=NsFZZU9gvk",original:{zh:"原工作覆盖 100 个 harmful browser behaviors、40 个 synthetic websites、19 个领域。",en:"The original work covers 100 harmful browser behaviors, 40 synthetic websites, and 19 domains."},slice:{zh:"G1 使用其 task/trajectory substrate 形成 persistent-state audit，不把全部原 task 当统计 n。",en:"G1 uses its task/trajectory substrate for persistent-state auditing rather than treating all original tasks as n."},transform:{zh:"同一 future schedule 构造 updated / base / NullMemory 三臂，再在 frozen trajectory 上切 evaluator。",en:"Construct updated/base/NullMemory arms on the same future schedule, then switch evaluator on frozen trajectories."}},
   {name:"Agent Workflow Memory",paper:"Agent Workflow Memory",venue:"ICML",year:2025,url:"https://proceedings.mlr.press/v267/wang25bx.html",original:{zh:"原论文在 Mind2Web + WebArena 上覆盖 1000+ tasks、200+ domains。",en:"The paper covers 1000+ tasks across 200+ domains in Mind2Web and WebArena."},slice:{zh:"G1 只把 AWM 作为 persistent workflow/state 机制谱系，不把原 benchmark 分数并入安全结论。",en:"G1 uses AWM as the persistent workflow/state lineage; original scores are not safety outcomes."},transform:{zh:"对象变成“Agent 状态继续更新后，安全测量是否仍可识别”。",en:"The object becomes whether safety measurement remains identifiable as state updates."}},
   {name:"HarmBench",paper:"HarmBench: A Standardized Evaluation Framework for Automated Red Teaming and Robust Refusal",venue:"ICML",year:2024,url:"https://arxiv.org/abs/2402.04249",original:{zh:"标准化 harmful-behavior / refusal evaluation，不是 persistent temporal benchmark。",en:"Standardized harmful-behavior/refusal evaluation, not a persistent temporal benchmark."},slice:{zh:"G1 冻结 HarmBench 为 evaluator A；DeepSeek 独立冻结为 evaluator B。",en:"G1 freezes HarmBench as evaluator A and DeepSeek independently as evaluator B."},transform:{zh:"不投票；保留两套 label vector，计算 definite/possible event sets 与 contrast envelope。",en:"No voting; retain both label vectors for definite/possible sets and contrast envelopes."}}
  ],
  models:[
   {name:"Qwen3-8B + AWM",role:{zh:"persistent browser Agent backbone。",en:"Persistent browser-agent backbone."},status:{zh:"被测 Agent",en:"tested agent"}},
   {name:"HarmBench",role:{zh:"冻结 evaluator A。",en:"Frozen evaluator A."},status:{zh:"measurement",en:"measurement"}},
   {name:"DeepSeek",role:{zh:"独立冻结 evaluator B；不当 ground truth。",en:"Independent evaluator B; not ground truth."},status:{zh:"measurement",en:"measurement"}},
   {name:"Human semantic labels",role:{zh:"待补独立语义锚点。",en:"Pending independent semantic anchor."},status:{zh:"evidence debt",en:"evidence debt"}}
  ],
  quantities:[
   {v:"100 / 40 / 19",k:{zh:"BrowserART harmful behaviors / sites / domains",en:"BrowserART harmful behaviors / sites / domains"}},
   {v:"108",k:{zh:"历史 future trajectories",en:"historical future trajectories"}},
   {v:"12",k:{zh:"current trajectories / PV1 fresh episodes（各自面板）",en:"current trajectories / PV1 fresh episodes (separate panels)"}},
   {v:"3",k:{zh:"updated / base / NullMemory arms",en:"updated / base / NullMemory arms"}},
   {v:"2",k:{zh:"independently frozen automated evaluators",en:"independently frozen automated evaluators"}}
  ],
  unit:{zh:"核心 measurement unit 是同一 frozen trajectory 在不同 evaluator 下的标签；trajectory 不变才能把差异归到 measurement。",en:"The core unit is the same frozen trajectory under different evaluators."},
  treatment:{zh:"persistent-state arm 与 evaluator identity 分开操纵：三臂回答 temporal contrast，双 evaluator 回答结论是否可识别。",en:"Persistent-state arm and evaluator identity are separate manipulations."},
  readouts:["current-pass premise","first-event sets","updated/base/NullMemory ordering","definite / possible sets","contrast envelope","prospective fail-closed verdict"]
 }
}
});
