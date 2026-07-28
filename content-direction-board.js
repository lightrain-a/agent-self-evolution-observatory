Object.assign(window.PAGE_CONTENT,{
"direction-board":{
  eyebrow:{en:"Next Paper · 34-Idea Portfolio",zh:"下一篇论文 · 34 个方向候选池"},
  title:{en:"Thirty-four ranked directions after lifecycle-wide iteration",zh:"经过生命周期级整体迭代的三十四个 Agent 自进化方向"},
  lead:{en:"The portfolio now starts from 69 formulations. A third review round maps every proposal onto the module–lifecycle attack and reliability surface, adds ranking confidence and paper-track fit, merges two overlapping former directions, and retains only four of fourteen newly generated proposals. The result is 34 standalone directions, 18 merged sub-directions, and 17 rejected formulations.",zh:"当前候选池从 69 个表述出发。第三轮审查把所有提案映射到模块—生命周期攻击与可靠性表面，新增排序置信度和论文赛道适配，并合并两个重叠度较高的旧方向；本轮新生成的 14 个提案中仅保留 4 个。最终得到 34 个独立方向、18 个并入子方向和 17 个淘汰表述。"},
  callout:{en:"One global rank is retained for project selection, but heterogeneous paper types are no longer forced into a single interpretation. The board also provides separate visual/CVPR, systems-security, benchmark-analysis, and long-horizon learning rankings.",zh:"为了项目选择仍保留一个总榜，但不再把不同论文类型强行解释为同一种价值。页面同时给出视觉／CVPR、系统安全、基准分析和长期学习四类赛道榜。"},
  sections:[
    {title:{en:"Third-round protocol: 69 formulations → 34 standalone directions",zh:"第三轮审查：69 个表述 → 34 个独立方向"},body:{en:`<div class="steps"><div class="step"><b>Lifecycle coverage audit</b><p>Map each proposal across Brain, Cognitive Resource, Execution, Self-Design, and Collective modules, and across Bootstrap, Propose, Evaluate, Commit, and Serve stages.</p></div><div class="step"><b>Collision and variable test</b><p>Remove generic authorization, generic uncertainty, generic provenance, and generic runtime-monitoring proposals when a direct method or survey already defines the same scientific target.</p></div><div class="step"><b>Standalone-versus-axis test</b><p>Merge a proposal when it is better treated as an attack type, metric, protocol, or ablation of an existing direction rather than a new estimand.</p></div><div class="step"><b>Global score</b><p>Novelty 22%, main-table identifiability 23%, venue fit 15%, pilot readiness 15%, failure value 10%, resource efficiency 10%, and collision margin 5%.</p></div><div class="step"><b>Confidence label</b><p>High means a clear literature boundary and accessible minimum pilot; Medium means one material dependency remains; Low means the main claim still depends on special infrastructure or weakly identifiable ground truth.</p></div></div><div class="claim-box"><b>Ranking rule</b>The global rank selects projects. Track ranks select venues and paper forms. A lower global rank can still lead its own track when it requires specialized assets.</div>`,zh:`<div class="steps"><div class="step"><b>生命周期覆盖审查</b><p>把每个提案映射到 Brain、认知资源、执行、自设计和群体五类模块，以及 Bootstrap、Propose、Evaluate、Commit 和 Serve 五个阶段。</p></div><div class="step"><b>碰撞与变量检验</b><p>当已有直接方法或综述已经定义同一科学目标时，淘汰通用授权、通用不确定性、通用溯源和通用运行时监控提案。</p></div><div class="step"><b>独立方向或评测轴检验</b><p>如果一个提案更适合作为现有方向的攻击类型、指标、协议或消融，而不是新的估计目标，则予以合并。</p></div><div class="step"><b>总分</b><p>新颖性 22%、主表可识别性 23%、会议契合 15%、Pilot 就绪度 15%、失败后价值 10%、资源效率 10%、碰撞余量 5%。</p></div><div class="step"><b>排序置信度</b><p>高表示文献边界清晰且最小 Pilot 资源可得；中表示仍有一个重要依赖；低表示主张依赖特殊基础设施或真值较弱。</p></div></div><div class="claim-box"><b>排序规则</b>总榜用于选择项目，赛道榜用于选择会议与论文形式。某个方向总榜较低，仍可能在需要特殊资产的赛道中排名靠前。</div>`}},
    {title:{en:"Lifecycle coverage audit and the four retained gaps",zh:"生命周期覆盖审查与四个新增保留缺口"},body:{en:`<table class="matrix"><thead><tr><th>Observed blind spot</th><th>Retained direction</th><th>Why existing ideas are insufficient</th></tr></thead><tbody><tr><td>A small harmful update persists and grows across descendant versions or agent populations.</td><td><strong>AmplificationGuard-X</strong></td><td>EvoFirewall blocks local channels and EvoProvenance records lineage, but neither estimates or controls a cross-generation amplification factor.</td></tr><tr><td>A newly evolved skill or tool becomes more capable while retaining stale or overly broad authorization.</td><td><strong>CapabilityLease-Evo</strong></td><td>Static pre-action authorization does not decide how permissions should expire, renew, or shrink when the capability version changes.</td></tr><tr><td>Confidence is calibrated at the source experience but lost when the experience is summarized, crystallized, composed, or distilled.</td><td><strong>ConfidenceFlow-Evo</strong></td><td>Trajectory uncertainty and provenance exist, but downstream confidence propagation across persistent artifacts remains a distinct target.</td></tr><tr><td>A single canonical version accumulates incompatible trade-offs and destroys useful specialization.</td><td><strong>PluralLineage-Evo</strong></td><td>Multi-agent ensembles operate at inference time; the proposed variable is a persistent portfolio of versioned lineages with branch, route, merge, and retire decisions.</td></tr></tbody></table><div class="survey-note"><b>Consolidation in this round</b>DeleteCascade-Evo is folded into EvoProvenance-V as derivative-state revocation. DiversityGuard-MAS is folded into PluralLineage-Evo and CrossAgentTransfer-V as lineage/population diversity evaluation.</div>`,zh:`<table class="matrix"><thead><tr><th>发现的盲区</th><th>保留方向</th><th>为什么现有方向不足</th></tr></thead><tbody><tr><td>一个小型有害更新会在后代版本或 Agent 群体中持久化并逐步放大。</td><td><strong>AmplificationGuard-X</strong></td><td>EvoFirewall 阻断局部通道，EvoProvenance 记录谱系，但二者都不估计或控制跨代放大因子。</td></tr><tr><td>新进化出的技能或工具能力增强，却继续持有过期或过宽权限。</td><td><strong>CapabilityLease-Evo</strong></td><td>静态动作前授权无法决定能力版本变化后权限应如何到期、续租或收缩。</td></tr><tr><td>来源经验上的置信度已校准，但在摘要、技能固化、组合或蒸馏后丢失。</td><td><strong>ConfidenceFlow-Evo</strong></td><td>轨迹不确定性和溯源已有研究，但持久派生产物之间的置信传播仍是独立目标。</td></tr><tr><td>单一规范版本不断累积不兼容权衡，并丢失有用专门化。</td><td><strong>PluralLineage-Evo</strong></td><td>多 Agent 集成主要发生在推理时；这里研究的是带分支、路由、合并和退役决策的持久版本谱系组合。</td></tr></tbody></table><div class="survey-note"><b>本轮合并</b>DeleteCascade-Evo 作为派生状态撤销并入 EvoProvenance-V；DiversityGuard-MAS 作为谱系／群体多样性评测并入 PluralLineage-Evo 与 CrossAgentTransfer-V。</div>`}},
    {title:{en:"Seventeen formulations removed after collision or identifiability review",zh:"碰撞或可识别性审查后淘汰的十七种表述"},body:{en:`<table class="matrix"><thead><tr><th>Removed formulation</th><th>Why removed</th><th>Closest boundary</th></tr></thead><tbody>
<tr><td>Generic visual question generation + GRPO</td><td>Visual self-play with difficulty and diversity control already exists.</td><td>VisPlay, Active Zero, Agent0-VL</td></tr>
<tr><td>Generic visual critic self-correction</td><td>Critique and iterative correction are crowded.</td><td>VISCO, Critic-V</td></tr>
<tr><td>Generic multimodal memory agent</td><td>Visual, semantic, episodic, and hierarchical memories already exist.</td><td>WorldMM, ViLoMem, VideoARM, R4</td></tr>
<tr><td>Generic long-term personalized memory</td><td>Remember–retrieve–align personalization is established.</td><td>PersonaVLM, M2A, POLAR</td></tr>
<tr><td>Generic macro-tool induction</td><td>Trajectory abstraction and skill lifecycle are established.</td><td>META, MUSE-Autoskill, SkillSmith</td></tr>
<tr><td>Generic dynamic multimodal GraphRAG</td><td>Interactive graph retrieval and editing are central mechanisms already.</td><td>EvoGraph-R1</td></tr>
<tr><td>Generic self-evolving world model</td><td>Deployment-time repair and selective foresight exist.</td><td>WorldEvolver</td></tr>
<tr><td>Generic evaluator co-evolution</td><td>Non-stationary evaluator evolution is explicit.</td><td>Red Queen Gödel Machine</td></tr>
<tr><td>Generic pairwise release validator</td><td>Pairwise parent–child release gates already exist.</td><td>Reward-Free Evolving Agents</td></tr>
<tr><td>Generic decentralized multi-agent memory</td><td>Local memory pools and diversity preservation are existing mechanisms.</td><td>DecentMem</td></tr>
<tr><td>Generic evolution protocol</td><td>Versioned resources, lineage, and rollback are specified.</td><td>Autogenesis</td></tr>
<tr><td>Generic agent–environment co-evolution</td><td>Adaptive environment and curriculum synthesis are active directions.</td><td>Agent-World, SimWorld Studio</td></tr>
<tr><td>Generic process-reward self-evolution</td><td>Critic and policy co-evolution already exists.</td><td>Q-Evolve</td></tr>
<tr><td>Generic regression-aware release engineering</td><td>Canonical versions and flip-centered gating already exist.</td><td>AgentDevel</td></tr>
<tr><td>CapabilityPhase-Evo</td><td>No clean intervention, ground truth, or reproducible main experiment for discontinuous capability emergence.</td><td>Insufficient identifiability</td></tr>
<tr><td>Generic runtime attestation</td><td>Cryptographic capability binding, signed ledgers, and replay verification directly cover the mechanism.</td><td>Dynamic capability governance</td></tr>
<tr><td>Generic uncertainty-aware agent</td><td>Trajectory-level uncertainty memory and targeted reflection already exist.</td><td>Agentic Uncertainty Quantification</td></tr>
</tbody></table>`,zh:`<table class="matrix"><thead><tr><th>淘汰表述</th><th>淘汰原因</th><th>最接近边界</th></tr></thead><tbody>
<tr><td>通用视觉问题生成 + GRPO</td><td>带难度和多样性控制的视觉自博弈已存在。</td><td>VisPlay、Active Zero、Agent0-VL</td></tr>
<tr><td>通用视觉 critic 自纠错</td><td>视觉批评与迭代纠错高度拥挤。</td><td>VISCO、Critic-V</td></tr>
<tr><td>通用多模态记忆 Agent</td><td>视觉、语义、情景和层级记忆均已有工作。</td><td>WorldMM、ViLoMem、VideoARM、R4</td></tr>
<tr><td>通用长期个性化记忆</td><td>记忆—检索—对齐式个性化已经建立。</td><td>PersonaVLM、M2A、POLAR</td></tr>
<tr><td>通用轨迹宏工具归纳</td><td>轨迹抽象和技能生命周期已有直接工作。</td><td>META、MUSE-Autoskill、SkillSmith</td></tr>
<tr><td>通用动态多模态 GraphRAG</td><td>交互式图检索和编辑已是已有核心机制。</td><td>EvoGraph-R1</td></tr>
<tr><td>通用自进化世界模型</td><td>部署期修复与选择性预见已有工作。</td><td>WorldEvolver</td></tr>
<tr><td>通用评价器共进化</td><td>非平稳评价器进化已被明确提出。</td><td>Red Queen Gödel Machine</td></tr>
<tr><td>通用成对发布验证器</td><td>父子版本成对发布门控已有工作。</td><td>Reward-Free Evolving Agents</td></tr>
<tr><td>通用去中心化多 Agent 记忆</td><td>本地记忆池与多样性保持已有机制。</td><td>DecentMem</td></tr>
<tr><td>通用版本化进化协议</td><td>资源版本、溯源与回滚已有协议。</td><td>Autogenesis</td></tr>
<tr><td>通用 Agent—环境共进化</td><td>自适应环境和课程生成已形成方向。</td><td>Agent-World、SimWorld Studio</td></tr>
<tr><td>通用过程奖励自进化</td><td>Critic 与策略共进化已有工作。</td><td>Q-Evolve</td></tr>
<tr><td>通用非回退发布工程</td><td>规范版本线和 flip 门控已有工作。</td><td>AgentDevel</td></tr>
<tr><td>CapabilityPhase-Evo</td><td>能力突变缺少干净干预、可靠真值和可复现主实验。</td><td>可识别性不足</td></tr>
<tr><td>通用运行时证明</td><td>密码学能力绑定、签名账本和重放验证已直接覆盖核心机制。</td><td>动态能力治理</td></tr>
<tr><td>通用不确定性感知 Agent</td><td>轨迹级不确定性记忆与定向反思已存在。</td><td>Agentic Uncertainty Quantification</td></tr>
</tbody></table>`}},
    {title:{en:"New lifecycle batch: fourteen proposals → four retained, eight merged, two rejected",zh:"新增生命周期候选：14 个提案 → 4 个保留、8 个并入、2 个淘汰"},body:{en:`<table class="matrix"><thead><tr><th>New formulation</th><th>Decision</th><th>Reason</th></tr></thead><tbody>
<tr><td><strong>AmplificationGuard-X</strong></td><td>Retain</td><td>Defines and controls persistence, reproduction, and amplification across descendant versions and populations.</td></tr>
<tr><td><strong>CapabilityLease-Evo</strong></td><td>Retain</td><td>Studies expiring and renewable authorization tied to the exact version and scope of an evolving capability.</td></tr>
<tr><td><strong>ConfidenceFlow-Evo</strong></td><td>Retain</td><td>Propagates calibrated uncertainty from source evidence into memories, skills, tools, adapters, and descendants.</td></tr>
<tr><td><strong>PluralLineage-Evo</strong></td><td>Retain</td><td>Maintains, routes, merges, and retires multiple persistent specialized lineages instead of one canonical version.</td></tr>
<tr><td>PopulationImmunity-MAS</td><td>Merge → AmplificationGuard-X</td><td>Population contagion and immunization are one propagation topology within the amplification problem.</td></tr>
<tr><td>ServeStageGuard-Evo</td><td>Merge → EvoFirewall-V / AuditInvariant-Evo</td><td>Serve-stage monitoring is a lifecycle stage, not a separate estimand.</td></tr>
<tr><td>QuarantineCommit-Evo</td><td>Merge → EvoFirewall-V / AuditInvariant-Evo</td><td>Quarantine and canary release are evaluation protocols for the same safety variables.</td></tr>
<tr><td>EvidenceExpiry-Evo</td><td>Merge → ScopeGuard-V / ViMEvo-Repair</td><td>Temporal expiry is applicability scope plus stale-state repair.</td></tr>
<tr><td>StopRule-Evo</td><td>Merge → EvoValue-V / BudgetEvolve-V</td><td>Stopping is the marginal-value decision under a finite evolution budget.</td></tr>
<tr><td>UpdateAssurance-Evo</td><td>Merge → EvoProvenance-V / EvoContract-V</td><td>A machine-checkable assurance case combines provenance and executable compatibility evidence.</td></tr>
<tr><td>PermissionDrift-Evo</td><td>Merge → CapabilityLease-Evo</td><td>Permission drift is the central failure mode tested by version-bound leases.</td></tr>
<tr><td>RollbackOrder-Evo</td><td>Merge → InteractionGuard-V / EvoProvenance-V</td><td>Rollback ordering is a recovery operation over interacting lineage dependencies.</td></tr>
<tr><td>Generic runtime attestation</td><td>Reject</td><td>Direct cryptographic capability and replay-attestation methods already exist.</td></tr>
<tr><td>Generic uncertainty-aware agent</td><td>Reject</td><td>Direct trajectory-level uncertainty-control frameworks already exist.</td></tr>
</tbody></table>`,zh:`<table class="matrix"><thead><tr><th>新增表述</th><th>决定</th><th>理由</th></tr></thead><tbody>
<tr><td><strong>AmplificationGuard-X</strong></td><td>保留</td><td>定义并控制更新在后代版本与群体中的持久化、复制与放大。</td></tr>
<tr><td><strong>CapabilityLease-Evo</strong></td><td>保留</td><td>研究与进化能力精确版本和适用范围绑定的可到期、可续租授权。</td></tr>
<tr><td><strong>ConfidenceFlow-Evo</strong></td><td>保留</td><td>把来源证据上的校准不确定性传播到记忆、技能、工具、Adapter 与后代版本。</td></tr>
<tr><td><strong>PluralLineage-Evo</strong></td><td>保留</td><td>维护、路由、合并和退役多条持久专门化谱系，而不是只保留单一规范版本。</td></tr>
<tr><td>PopulationImmunity-MAS</td><td>并入 → AmplificationGuard-X</td><td>群体传播与免疫是放大问题中的一种传播拓扑。</td></tr>
<tr><td>ServeStageGuard-Evo</td><td>并入 → EvoFirewall-V／AuditInvariant-Evo</td><td>Serve 阶段监控属于生命周期阶段，而不是独立估计目标。</td></tr>
<tr><td>QuarantineCommit-Evo</td><td>并入 → EvoFirewall-V／AuditInvariant-Evo</td><td>隔离与金丝雀发布是相同安全变量的评测协议。</td></tr>
<tr><td>EvidenceExpiry-Evo</td><td>并入 → ScopeGuard-V／ViMEvo-Repair</td><td>时间到期属于适用范围与过期状态修复。</td></tr>
<tr><td>StopRule-Evo</td><td>并入 → EvoValue-V／BudgetEvolve-V</td><td>停止本质上是有限进化预算下的边际价值决策。</td></tr>
<tr><td>UpdateAssurance-Evo</td><td>并入 → EvoProvenance-V／EvoContract-V</td><td>机器可检查安全论证由溯源和可执行兼容证据共同组成。</td></tr>
<tr><td>PermissionDrift-Evo</td><td>并入 → CapabilityLease-Evo</td><td>权限漂移正是版本绑定租约需要测试的核心失败模式。</td></tr>
<tr><td>RollbackOrder-Evo</td><td>并入 → InteractionGuard-V／EvoProvenance-V</td><td>回滚顺序是对交互谱系依赖进行恢复的操作。</td></tr>
<tr><td>通用运行时证明</td><td>淘汰</td><td>已有直接密码学能力证明与重放验证方法。</td></tr>
<tr><td>通用不确定性感知 Agent</td><td>淘汰</td><td>已有直接轨迹级不确定性控制框架。</td></tr>
</tbody></table>`}}
  ]
}
});
