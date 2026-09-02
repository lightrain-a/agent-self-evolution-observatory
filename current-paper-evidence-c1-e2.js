window.CURRENT_PAPER_EVIDENCE_PROFILES=window.CURRENT_PAPER_EVIDENCE_PROFILES||{};
Object.assign(window.CURRENT_PAPER_EVIDENCE_PROFILES,{
"paper-c1":{
 featured:[
  {title:"How Memory Management Impacts LLM Agents: An Empirical Study of Experience-Following Behavior",venue:"ACL",year:2026,url:"https://aclanthology.org/2026.acl-long.27/",relation:{zh:"ACL 2026 主会直接操纵 memory addition/deletion，并研究 experience-following、error propagation 与 misleading value。",en:"ACL 2026 directly manipulates memory addition/deletion and studies experience-following and error propagation."},boundary:{zh:"它研究 memory management 对行为的总体影响；C1 把同一 memory difference 沿 write → retrieval → uptake → terminal 分阶段记账。",en:"It studies overall behavioral effects; C1 accounts for a memory difference stage by stage."}},
  {title:"Mem2ActBench: A Benchmark for Evaluating Long-Term Memory Utilization in Task-Oriented Autonomous Agents",venue:"ACL",year:2026,url:"https://aclanthology.org/2026.acl-long.370/",relation:{zh:"最新主会 benchmark 专门区分被动记忆问答与把长期记忆真正用于 tool action；包含 400 个 tool-use tasks。",en:"A recent main-conference benchmark separating passive recall from active memory use, with 400 tool-use tasks."},boundary:{zh:"Mem2ActBench 解决 active-use coverage；C1 的 object 是一个已写入差异在 native pipeline 的哪一层衰减。",en:"Mem2ActBench broadens active-use coverage; C1 asks where a written difference attenuates in the native pipeline."}},
  {title:"Memory-R1: Enhancing Large Language Model Agents to Manage and Utilize Memories via Reinforcement Learning",venue:"ACL",year:2026,url:"https://aclanthology.org/2026.acl-long.583/",relation:{zh:"ACL 2026 主会学习 ADD/UPDATE/DELETE/NOOP memory operations，并跨三 benchmark、3B–14B 模型验证。",en:"ACL 2026 learns ADD/UPDATE/DELETE/NOOP memory operations across three benchmarks and 3B–14B models."},boundary:{zh:"Memory-R1 优化 manager；C1 不提出 manager，而审计 state divergence 是否真的传到 native behavior。",en:"Memory-R1 optimizes a manager; C1 audits transport from state divergence to native behavior."}},
  {title:"ReasoningBank: Scaling Agent Self-Evolving with Reasoning Memory",venue:"ICLR",year:2026,url:"https://arxiv.org/abs/2509.25140",relation:{zh:"ICLR 2026 正式 self-evolving reasoning-memory 工作，是 C1 扩展线的重要近邻。",en:"An ICLR 2026 self-evolving reasoning-memory paper and important neighbor for C1's extension."},boundary:{zh:"ReasoningBank 关注积累/复用 reasoning memory；C1 核心贡献是 stage-resolved transport identification。",en:"ReasoningBank focuses on accumulating/reusing reasoning memory; C1 identifies stage-resolved transport."}}
 ],
 experiment:{
  intro:{zh:"C1 canonical 实验不是把某个公开 benchmark 的全部任务直接拿来跑，而是由项目冻结的 Shopping / Reddit task domains 与 paired source/future units 组成。公开 ReasoningBank/AWM 等工作提供方法谱系，统计 n 按我们冻结的 pair/cell 记账。",en:"C1 does not simply run an entire public benchmark. Canonical experiments use project-frozen Shopping/Reddit task domains and paired source/future units; statistical n follows frozen pairs/cells."},
  sources:[
   {name:"Shopping task domain",paper:"Project-frozen task domain",venue:"Project construct",year:2026,url:"",original:{zh:"不是把公开 benchmark 总任务数当 n；任务域在项目内冻结并做 paired source/future accounting。",en:"The public benchmark total is not treated as n; the domain is frozen with paired source/future accounting."},slice:{zh:"20 个 complete paired writes；172 个 native retrieval opportunities；36 个 paired first-action/terminal cells。",en:"20 paired writes, 172 native retrieval opportunities, and 36 paired first-action/terminal cells."},transform:{zh:"同一 byte-identical source trajectory 只切 success/failure reflection writer，随后恢复 native retrieval。",en:"A byte-identical source trajectory changes only the success/failure reflection writer before native retrieval is restored."}},
   {name:"Reddit task domain",paper:"Project-frozen cross-domain replication",venue:"Project construct",year:2026,url:"",original:{zh:"作为跨域复现，不把 domain name 冒充某篇公开 benchmark 的独立样本量。",en:"Used as cross-domain replication without presenting the domain label as a public benchmark sample count."},slice:{zh:"复制 write divergence，并单独记录 native terminal transport 的稀疏/符号异质性。",en:"Replicates write divergence and tracks sparse/sign-heterogeneous native terminal transport."},transform:{zh:"复用同一 stage-resolved protocol，检验结论是否只依赖 Shopping。",en:"Reuses the same stage-resolved protocol to test whether the finding is Shopping-specific."}},
   {name:"ReasoningBank",paper:"ReasoningBank: Scaling Agent Self-Evolving with Reasoning Memory",venue:"ICLR",year:2026,url:"https://arxiv.org/abs/2509.25140",original:{zh:"正式 self-evolving reasoning-memory framework。",en:"A formally published self-evolving reasoning-memory framework."},slice:{zh:"在 C1 中属于 PACTA / ReasoningBank 扩展谱系；fresh source-trajectory provenance 未闭合前不进入 canonical inference。",en:"Used in the PACTA/ReasoningBank extension lineage; it does not enter canonical inference before source provenance closes."},transform:{zh:"扩展测试更严格 state-conditioned binding / source provenance，而不是替换 canonical evidence。",en:"The extension tests stricter state-conditioned binding/source provenance rather than replacing canonical evidence."}}
  ],
  models:[
   {name:"ReasoningBank-style writer / executor",role:{zh:"生成 paired durable memory。",en:"Generates paired durable memories."},status:{zh:"canonical",en:"canonical"}},
   {name:"Frozen native policy",role:{zh:"retrieval / first-action / terminal audit。",en:"Retrieval / first-action / terminal audit."},status:{zh:"canonical",en:"canonical"}},
   {name:"Qwen397",role:{zh:"PACTA / ReasoningBank 扩展候选。",en:"PACTA / ReasoningBank extension candidate."},status:{zh:"extension gate separate",en:"extension gate separate"}}
  ],
  quantities:[
   {v:"20 / 20",k:{zh:"paired writes 出现 durable divergence",en:"paired writes with durable divergence"}},
   {v:"172",k:{zh:"native retrieval opportunities",en:"native retrieval opportunities"}},
   {v:"36",k:{zh:"paired first-action / terminal cells",en:"paired first-action / terminal cells"}},
   {v:"4 × 4",k:{zh:"source-memory pairs × frozen future tasks",en:"source-memory pairs × frozen future tasks"}},
   {v:"256",k:{zh:"forced fixed-evidence rollouts",en:"forced fixed-evidence rollouts"}}
  ],
  unit:{zh:"write 层单位是 byte-identical source trajectory pair；native 行为层按 paired future cell 记账；256 forced rollouts 只属于 capacity side-control。",en:"Write-stage units are byte-identical source-trajectory pairs; native behavior uses paired future cells; 256 forced rollouts are a capacity side-control."},
  treatment:{zh:"固定 source trajectory、writer model 与 temperature，只切 success/failure reflection branch；随后区分 forced exposure=1 与 native retrieval。",en:"Source trajectory, writer model, and temperature stay fixed while only the reflection branch changes; forced exposure is separated from native retrieval."},
  readouts:["durable-state divergence","retrieval exposure","first-action TV / modal change","terminal outcome","forced latent capacity vs native transport"]
 }
},
"paper-e2":{
 featured:[
  {title:"Reinforcement Learning for Self-Improving Agent with Skill Library (SAGE)",venue:"ACL",year:2026,url:"https://aclanthology.org/2026.acl-long.69/",relation:{zh:"最新主会 skill-based self-improvement：技能随连续任务累积并参与后续 rollout。",en:"Recent main-conference skill-based self-improvement with skills accumulating across tasks."},boundary:{zh:"SAGE 优化 skill generation/use；E2/R17 的问题更窄：search winner 对 acting 有价值，不代表 learner 也只该看 winner。",en:"SAGE optimizes skills; E2/R17 asks whether acting's winner should define learner-visible evidence."}},
  {title:"CoEvolve: Training LLM Agents via Agent-Data Mutual Evolution",venue:"ACL",year:2026,url:"https://aclanthology.org/2026.acl-long.1055/",relation:{zh:"ACL 2026 主会根据 forgetting/uncertainty 从 rollout 中找 failure-prone pattern，再让 data distribution 随 Agent 一起演化。",en:"ACL 2026 uses forgetting/uncertainty from rollouts to co-evolve the data distribution with the agent."},boundary:{zh:"CoEvolve 选择/生成新训练数据；R17 在同一次 search 内固定 acting winner，只操纵 learner 看哪条既有 evidence。",en:"CoEvolve selects/generates data; R17 fixes the acting winner and changes only learner-visible existing evidence."}},
  {title:"Agent Workflow Memory",venue:"ICML",year:2025,url:"https://proceedings.mlr.press/v267/wang25bx.html",relation:{zh:"ICML 2025 证明从历史 trajectory 归纳 reusable workflow 可以显著提升 Web Agent。",en:"ICML 2025 shows reusable workflows induced from historical trajectories can improve web agents."},boundary:{zh:"它回答什么经验可抽成 workflow；E2/R17 识别 winner/near-miss/rejected evidence 的 learning credit。",en:"It asks what experience becomes a workflow; E2/R17 identifies learning credit across search evidence."}}
 ],
 experiment:{
  intro:{zh:"E2 有两条数据线必须分开：canonical E2 使用真实公开经济/能源 release 系统做 temporal attribution；R17 decisive experiment 是本项目冻结的 search-evidence panel，并不是某篇公开 benchmark 的原表。",en:"E2 has two distinct data lines: canonical E2 uses real public economic/energy release systems, while R17 is a project-frozen search-evidence panel."},
  sources:[
   {name:"BEA / NOAA / EIA",paper:"Real public release systems",venue:"Public data sources",year:2026,url:"",original:{zh:"政府/机构真实时间序列 release，而不是论文 benchmark。",en:"Real government/institution release streams rather than a paper benchmark."},slice:{zh:"canonical E2 冻结 cutoff、release alignment 与 future query，审计 targeted temporal operation attribution。",en:"Canonical E2 freezes cutoffs, release alignment, and future queries for attribution auditing."},transform:{zh:"加入 original-agent N、same-surface controls，防止 comparator degradation 冒充 repair。",en:"Adds original-agent N and same-surface controls so comparator degradation cannot masquerade as repair."}},
   {name:"BLS CPI / Federal Reserve FOMC",paper:"Real public release systems",venue:"Public data sources",year:2026,url:"",original:{zh:"R16 / planning follow-up 的真实公开 release。",en:"Real public releases used in R16/planning follow-up."},slice:{zh:"用于 benign organizer 与 prospective planning falsifier；不和 R17 n 混算。",en:"Used for benign-organizer and prospective planning falsification; not pooled with R17 n."},transform:{zh:"判断 targeted credit 能否被更简单 information organization 吸收。",en:"Tests whether targeted credit is absorbed by simpler information organization."}},
   {name:"R17 frozen search-evidence panel",paper:"Project-constructed decisive experiment",venue:"Project construct",year:2026,url:"",original:{zh:"12 个 stream，每个 4 个 paired replicate。",en:"Twelve streams with four paired replicates each."},slice:{zh:"48 pairs → 96 learned states → 1,728 held-out evaluations。",en:"48 pairs → 96 learned states → 1,728 held-out evaluations."},transform:{zh:"acting 两臂都用 winner；learning 才比较 WIN-C winner-centric 与 MRW diagnostic witness。",en:"Both arms act from the winner; learning alone contrasts WIN-C with MRW."}}
  ],
  models:[
   {name:"DeepSeek",role:{zh:"R17 primary paired-learning backbone。",en:"R17 primary paired-learning backbone."},status:{zh:"decisive design",en:"decisive design"}},
   {name:"DeepSeek + Kimi",role:{zh:"canonical Temporal Skill attribution 历史模型。",en:"Historical models for canonical Temporal Skill attribution."},status:{zh:"historical evidence only",en:"historical evidence only"}}
  ],
  quantities:[
   {v:"12",k:{zh:"R17 independent streams / primary treatment units",en:"R17 independent streams / primary treatment units"}},
   {v:"4",k:{zh:"paired replicates per stream",en:"paired replicates per stream"}},
   {v:"48",k:{zh:"WIN-C vs MRW pairs",en:"WIN-C vs MRW pairs"}},
   {v:"96",k:{zh:"learned states",en:"learned states"}},
   {v:"1,728",k:{zh:"held-out future evaluations",en:"held-out future evaluations"}}
  ],
  unit:{zh:"primary treatment unit 是 12 个 stream 的 D_s，不是 1,728 个 held-out row；48 个 d_sr 是配对 replicate 诊断。",en:"The primary treatment unit is the 12 stream-level D_s values, not 1,728 held-out rows."},
  treatment:{zh:"Search 和 acting 完全相同；唯一处理是 learner 可见 evidence projection：WIN-C vs MRW。",en:"Search and acting are identical; the sole treatment is learner-visible evidence projection: WIN-C versus MRW."},
  readouts:["post-learning held-out performance","stream-level D_s","pair-level d_sr","sign-flip / bootstrap / TOST","heterogeneity"]
 }
}
});
