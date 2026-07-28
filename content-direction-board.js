Object.assign(window.PAGE_CONTENT,{
"direction-board":{
  eyebrow:{en:"Next Paper · 32-Idea Portfolio",zh:"下一篇论文 · 32 个方向候选池"},
  title:{en:"Thirty-two ranked directions after two-round self-review",zh:"经过两轮自我审查与完整排序的三十二个 Agent 自进化方向"},
  lead:{en:"The portfolio now starts from 55 formulations. We first remove direct literature collisions and scientifically unidentifiable bundles, then score every surviving direction by novelty, main-table identifiability, visual/venue fit, feasibility, failure value, and resource efficiency. The result is 32 standalone directions, eight merged sub-directions, and fifteen rejected formulations.",zh:"当前候选池从 55 个表述出发。第一轮排除与现有论文直接重合、无法识别科学变量或只是模块堆叠的方案；第二轮按新颖性、主表可识别性、视觉／会议契合、可行性、失败后价值和资源效率统一评分。最终得到 32 个独立方向、8 个并入的子方向和 15 个淘汰表述。"},
  callout:{en:"The rank is a project-selection rank, not a claim that lower-ranked questions are scientifically unimportant. Tier A contains the ten strongest immediate candidates, Tier B contains thirteen viable but conditional projects, and Tier C contains nine exploratory or infrastructure-heavy directions.",zh:"该排序用于项目选择，并不表示低排名问题在科学上不重要。A 级包含 10 个最值得立即讨论的候选；B 级包含 13 个可行但前置条件较多的方向；C 级包含 9 个探索性或基础设施成本较高的方向。"},
  sections:[
    {title:{en:"Two-round self-review protocol: 55 formulations → 32 ranked directions",zh:"两轮自我审查：55 个表述 → 32 个完整排序方向"},body:{en:`<div class="steps"><div class="step"><b>Round 1 · Collision and identifiability</b><p>Strip away application names, locate the closest paper, require one manipulable variable, and merge proposals that differ only by implementation surface.</p></div><div class="step"><b>Round 2 · Paper-strength audit</b><p>Require a normal-setting main table, a strongest baseline, a two-week minimum pilot, an explicit stop condition, and value if the learned method is weak.</p></div><div class="step"><b>Composite ranking</b><p>Novelty 25%, main-table identifiability 25%, visual/venue fit 15%, feasibility 15%, failure value 10%, and resource efficiency 10%.</p></div><div class="step"><b>Tier assignment</b><p>Tier A ranks 1–10, Tier B ranks 11–23, and Tier C ranks 24–32. Tier is assigned after scoring, not before.</p></div></div><div class="claim-box"><b>Retention rule</b>A direction remains standalone only when its central variable, strongest collision, minimum experiment, and Go/Stop boundary can each be stated in one sentence.</div>`,zh:`<div class="steps"><div class="step"><b>第一轮 · 碰撞与可识别性</b><p>去掉应用名称，定位最接近论文，要求只有一个可操纵变量，并合并仅在实现表面上不同的提案。</p></div><div class="step"><b>第二轮 · 论文强度审查</b><p>必须能构造正常设置主表、明确最强基线、两周最小 Pilot、停止条件，并保证方法效果一般时仍有研究价值。</p></div><div class="step"><b>综合排序</b><p>新颖性 25%、主表可识别性 25%、视觉／会议契合 15%、可行性 15%、失败后价值 10%、资源效率 10%。</p></div><div class="step"><b>分级</b><p>A 级为第 1–10 名，B 级为第 11–23 名，C 级为第 24–32 名。先评分，再分级。</p></div></div><div class="claim-box"><b>保留规则</b>只有当核心变量、最强碰撞、最小实验和 Go／Stop 边界都能分别用一句话说明时，方向才独立保留。</div>`}},
    {title:{en:"Fifteen formulations removed after collision review",zh:"碰撞审查后淘汰的十五种表述"},body:{en:`<table class="matrix"><thead><tr><th>Removed formulation</th><th>Why removed</th><th>Closest work or failure</th></tr></thead><tbody>
<tr><td>Generic visual question generation + GRPO</td><td>Difficulty/diversity visual self-play already exists.</td><td>VisPlay, Active Zero, Agent0-VL</td></tr>
<tr><td>Generic visual critic self-correction</td><td>Critique and iterative correction are crowded.</td><td>VISCO, Critic-V</td></tr>
<tr><td>Generic multimodal memory agent</td><td>Visual, semantic, episodic, and hierarchical memories already exist.</td><td>WorldMM, ViLoMem, VideoARM, R4</td></tr>
<tr><td>Generic long-term personalized memory</td><td>Remember–retrieve–align personalization is established.</td><td>PersonaVLM, M2A, POLAR</td></tr>
<tr><td>Generic macro-tool induction</td><td>Trajectory abstraction and skill lifecycle are existing mechanisms.</td><td>META, MUSE-Autoskill, SkillSmith</td></tr>
<tr><td>Generic dynamic multimodal GraphRAG</td><td>Interactive graph retrieval and editing are central already.</td><td>EvoGraph-R1, SAGE</td></tr>
<tr><td>Generic self-evolving world model</td><td>Deployment-time repair and selective foresight already exist.</td><td>WorldEvolver</td></tr>
<tr><td>Generic evaluator co-evolution</td><td>Non-stationary evaluator evolution is explicit.</td><td>Red Queen Gödel Machine</td></tr>
<tr><td>Generic pairwise release validator</td><td>Parent–child gates already replace scalar rewards.</td><td>Reward-Free Evolving Agents</td></tr>
<tr><td>Generic decentralized multi-agent memory</td><td>Local memory pools and diversity preservation already exist.</td><td>DecentMem</td></tr>
<tr><td>Generic evolution protocol</td><td>Versioned resources, lineage, and rollback are specified.</td><td>Autogenesis</td></tr>
<tr><td>Generic agent–environment co-evolution</td><td>Adaptive environment and curriculum synthesis are active directions.</td><td>Agent-World, SimWorld Studio</td></tr>
<tr><td>Generic process-reward self-evolution</td><td>In-distribution critic and policy co-evolution already exist.</td><td>Q-Evolve</td></tr>
<tr><td>Generic regression-aware release engineering</td><td>Canonical versions and flip-centered gating already exist.</td><td>AgentDevel</td></tr>
<tr><td>CapabilityPhase-Evo</td><td>Small updates may cause discontinuous behavior, but the proposal lacks a clean intervention, ground truth, and reproducible main experiment.</td><td>Too speculative for the current portfolio</td></tr>
</tbody></table>`,zh:`<table class="matrix"><thead><tr><th>淘汰表述</th><th>淘汰原因</th><th>最接近工作或失败点</th></tr></thead><tbody>
<tr><td>通用视觉问题生成 + GRPO</td><td>难度／多样性视觉自博弈已存在。</td><td>VisPlay、Active Zero、Agent0-VL</td></tr>
<tr><td>通用视觉 critic 自纠错</td><td>视觉批评与迭代纠错高度拥挤。</td><td>VISCO、Critic-V</td></tr>
<tr><td>通用多模态记忆 Agent</td><td>视觉、语义、情景和层级记忆均已有工作。</td><td>WorldMM、ViLoMem、VideoARM、R4</td></tr>
<tr><td>通用长期个性化记忆</td><td>记忆—检索—对齐式个性化已经建立。</td><td>PersonaVLM、M2A、POLAR</td></tr>
<tr><td>通用轨迹宏工具归纳</td><td>轨迹抽象和技能生命周期已有直接工作。</td><td>META、MUSE-Autoskill、SkillSmith</td></tr>
<tr><td>通用动态多模态 GraphRAG</td><td>交互式检索和图编辑已是核心机制。</td><td>EvoGraph-R1、SAGE</td></tr>
<tr><td>通用自进化世界模型</td><td>部署期修复与选择性预见已有工作。</td><td>WorldEvolver</td></tr>
<tr><td>通用评价器共进化</td><td>非平稳评价器进化已被明确提出。</td><td>Red Queen Gödel Machine</td></tr>
<tr><td>通用成对发布验证器</td><td>父子版本成对门控已替代标量奖励。</td><td>Reward-Free Evolving Agents</td></tr>
<tr><td>通用去中心化多 Agent 记忆</td><td>本地记忆池与多样性保持已有方案。</td><td>DecentMem</td></tr>
<tr><td>通用版本化进化协议</td><td>资源版本、溯源与回滚已有协议。</td><td>Autogenesis</td></tr>
<tr><td>通用 Agent—环境共进化</td><td>自适应环境和课程生成已形成方向。</td><td>Agent-World、SimWorld Studio</td></tr>
<tr><td>通用过程奖励自进化</td><td>分布内 critic 与策略共进化已有工作。</td><td>Q-Evolve</td></tr>
<tr><td>通用非回退发布工程</td><td>单一版本线和 flip 门控已有工作。</td><td>AgentDevel</td></tr>
<tr><td>CapabilityPhase-Evo</td><td>小更新可能引起行为突变，但当前表述缺少干净干预、真值和可复现主实验。</td><td>现阶段过于推测性</td></tr>
</tbody></table>`}},
    {title:{en:"New batch audit: sixteen proposals → eight retained, seven merged, one rejected",zh:"新增候选自查：16 个提案 → 8 个保留、7 个并入、1 个淘汰"},body:{en:`<table class="matrix"><thead><tr><th>New formulation</th><th>Decision</th><th>Reason</th></tr></thead><tbody>
<tr><td><strong>ScopeGuard-V</strong></td><td>Retain</td><td>Admission validity does not identify where a lesson remains valid; contrastive boundary probes make applicability scope measurable.</td></tr>
<tr><td><strong>InteractionGuard-V</strong></td><td>Retain</td><td>Individually valid updates can interact non-additively; co-commit interference is distinct from single-update regression.</td></tr>
<tr><td><strong>PerformativeEvo-V</strong></td><td>Retain</td><td>Separates external drift from distribution change caused by the agent's own deployed policy.</td></tr>
<tr><td><strong>AuditInvariant-Evo</strong></td><td>Retain</td><td>Tests whether an evolving agent behaves differently after inferring monitoring or sealed evaluation.</td></tr>
<tr><td><strong>OversightBudget-Evo</strong></td><td>Retain</td><td>Human review is a finite resource; the variable is which proposed persistent updates deserve escalation.</td></tr>
<tr><td><strong>GoalGuard-Evo</strong></td><td>Retain</td><td>Generic goal evolution exists, but constraint-preserving goal refinement and proxy-drift rejection remain identifiable.</td></tr>
<tr><td><strong>EvoGC-X</strong></td><td>Retain</td><td>Cross-surface semantic garbage collection differs from pruning one memory or skill library.</td></tr>
<tr><td><strong>DeleteCascade-Evo</strong></td><td>Retain</td><td>Tracks and removes derivatives of revoked evidence across memory, skills, tools, and adapters.</td></tr>
<tr><td>BranchMerge-Evo</td><td>Merge → InteractionGuard-V</td><td>Concurrent branch conflict is one important case of update interaction.</td></tr>
<tr><td>ShadowEvo</td><td>Merge → AuditInvariant-Evo</td><td>Shadow/canary deployment is a protocol for testing audit–deployment invariance.</td></tr>
<tr><td>TrustDecay-Evo</td><td>Merge → EvoFirewall-V</td><td>Time-varying source trust belongs inside the write-to-activation security channel.</td></tr>
<tr><td>FederatedEvo</td><td>Merge → CrossAgentTransfer-V</td><td>Privacy-preserving transfer is an evaluation axis, not a separate scientific variable.</td></tr>
<tr><td>ParetoGuard-Evo</td><td>Merge → BudgetEvolve-V</td><td>Preserving a quality–cost–safety frontier extends cost-aware evolution.</td></tr>
<tr><td>ModelSwap-Evo</td><td>Merge → EvoContract-V / CrossAgentTransfer-V</td><td>Backbone replacement combines semantic compatibility and cross-agent migration.</td></tr>
<tr><td>EvalDebt</td><td>Merge → EvalRedQueen-V / EvoDebt</td><td>Evaluator blind-spot accumulation is evaluator co-evolution plus longitudinal technical debt.</td></tr>
<tr><td>CapabilityPhase-Evo</td><td>Reject</td><td>No reliable minimum benchmark or identifiability test yet.</td></tr>
</tbody></table>`,zh:`<table class="matrix"><thead><tr><th>新增表述</th><th>决定</th><th>理由</th></tr></thead><tbody>
<tr><td><strong>ScopeGuard-V</strong></td><td>保留</td><td>经验有效并不等于知道它在哪些状态中有效；对比边界探针可使适用范围可测量。</td></tr>
<tr><td><strong>InteractionGuard-V</strong></td><td>保留</td><td>单独有效的更新可能产生非加性交互；联合提交干扰不同于单次更新回退。</td></tr>
<tr><td><strong>PerformativeEvo-V</strong></td><td>保留</td><td>区分外部漂移与 Agent 部署策略自身造成的未来数据变化。</td></tr>
<tr><td><strong>AuditInvariant-Evo</strong></td><td>保留</td><td>测试进化 Agent 推断监控或密封评测后是否改变行为。</td></tr>
<tr><td><strong>OversightBudget-Evo</strong></td><td>保留</td><td>人工审查是有限资源；核心变量是哪些持久更新提案值得升级人工。</td></tr>
<tr><td><strong>GoalGuard-Evo</strong></td><td>保留</td><td>通用目标进化已有工作，但保持约束的目标细化与代理目标漂移拒绝仍可识别。</td></tr>
<tr><td><strong>EvoGC-X</strong></td><td>保留</td><td>跨记忆、技能、工具和 Adapter 的语义垃圾回收不同于单一库剪枝。</td></tr>
<tr><td><strong>DeleteCascade-Evo</strong></td><td>保留</td><td>追踪并删除被撤销证据在记忆、技能、工具和 Adapter 中形成的派生物。</td></tr>
<tr><td>BranchMerge-Evo</td><td>并入 → InteractionGuard-V</td><td>并行分支冲突是更新交互的重要特例。</td></tr>
<tr><td>ShadowEvo</td><td>并入 → AuditInvariant-Evo</td><td>影子／金丝雀部署是测试审计—部署不变性的协议。</td></tr>
<tr><td>TrustDecay-Evo</td><td>并入 → EvoFirewall-V</td><td>随时间变化的来源信任应属于写入到激活的安全通道。</td></tr>
<tr><td>FederatedEvo</td><td>并入 → CrossAgentTransfer-V</td><td>隐私保护迁移是评测轴，而不是独立科学变量。</td></tr>
<tr><td>ParetoGuard-Evo</td><td>并入 → BudgetEvolve-V</td><td>保持质量—成本—安全前沿属于成本感知进化扩展。</td></tr>
<tr><td>ModelSwap-Evo</td><td>并入 → EvoContract-V／CrossAgentTransfer-V</td><td>主干替换同时涉及语义兼容与跨 Agent 迁移。</td></tr>
<tr><td>EvalDebt</td><td>并入 → EvalRedQueen-V／EvoDebt</td><td>评价器盲点累积属于评价器共进化与纵向技术债。</td></tr>
<tr><td>CapabilityPhase-Evo</td><td>淘汰</td><td>目前缺少可靠最小基准和可识别检验。</td></tr>
</tbody></table>`}}
  ]
}
});
