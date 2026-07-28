Object.assign(window.PAGE_CONTENT,{
"direction-board":{
  eyebrow:{en:"Next Paper · 20-Idea Portfolio",zh:"下一篇论文 · 20 个方向候选池"},
  title:{en:"Twenty self-checked directions across agent self-evolution",zh:"经过自查保留的二十个 Agent 自进化方向"},
  lead:{en:"We generated 34 candidate formulations, removed direct literature collisions and proposals without a falsifiable main experiment, and retained 20 directions spanning experience admission, memory, skills, embodied adaptation, world models, evaluation, governance, personalization, and multi-agent evolution.",zh:"我们先生成 34 个候选表述，再排除与现有论文直接重合、无法构造可证伪主实验或仅靠系统堆叠成立的方向，最终保留 20 个，覆盖经验准入、记忆、技能、具身适应、世界模型、评测、治理、个性化与多 Agent 进化。"},
  callout:{en:"The twenty directions are not equal recommendations. Tier A contains six directions worth immediate discussion; Tier B contains eight viable but more conditional projects; Tier C contains six exploratory directions requiring special assets or stronger preliminary evidence.",zh:"这二十个方向并非同等推荐。A 级六个方向值得立即讨论；B 级八个方向可行但前置条件更多；C 级六个方向需要特殊资源或更强预实验。"},
  sections:[
    {title:{en:"Self-check protocol: 34 candidates → 20 retained",zh:"自查流程：34 个候选 → 保留 20 个"},body:{en:`<div class="steps"><div class="step"><b>Direct-collision test</b><p>Remove a direction when its central mechanism already exists after stripping away the application name.</p></div><div class="step"><b>Scientific-variable test</b><p>Require one identifiable variable—admission, repair, drift, credit, routing, cost, diversity, or rollback—not a bundle of modules.</p></div><div class="step"><b>Main-table test</b><p>Require a normal-setting table that directly demonstrates the claimed advantage.</p></div><div class="step"><b>Minimum-demo test</b><p>Require a result before multi-backbone or large-scale training.</p></div><div class="step"><b>Failure-value test</b><p>Prefer projects that still yield a benchmark, diagnostic, dataset, or negative result when the method is weak.</p></div></div><div class="claim-box"><b>Retention rule</b>A direction remains only when its novelty boundary fits one sentence, its strongest baseline is known, and a stop condition can be evaluated in the first pilot.</div>`,zh:`<div class="steps"><div class="step"><b>直接碰撞检查</b><p>去掉应用名称后，如果核心机制已经存在，则淘汰该表述。</p></div><div class="step"><b>科学变量检查</b><p>必须围绕一个可识别变量：准入、修复、漂移、归因、路由、成本、多样性或回滚，而不是模块堆叠。</p></div><div class="step"><b>主表检查</b><p>必须能在正常设置主表中直接证明核心优势。</p></div><div class="step"><b>最小 Demo 检查</b><p>必须能在多骨干或大规模训练前得到初步结果。</p></div><div class="step"><b>失败价值检查</b><p>方法较弱时，仍能产出基准、诊断、数据集或有价值负结果的方向优先。</p></div></div><div class="claim-box"><b>保留规则</b>只有当新颖性边界能够用一句话说明、最强基线明确、且停止条件能在首个 Pilot 中评估时，方向才被保留。</div>`}},
    {title:{en:"Fourteen formulations removed after collision review",zh:"碰撞审查后淘汰的十四种表述"},body:{en:`<table class="matrix"><thead><tr><th>Removed formulation</th><th>Why removed</th><th>Closest work</th></tr></thead><tbody>
<tr><td>Generic visual question generation + GRPO</td><td>Difficulty/diversity visual self-play already exists.</td><td>VisPlay, Active Zero, Agent0-VL</td></tr>
<tr><td>Generic visual critic self-correction</td><td>Critique and iterative correction are crowded.</td><td>VISCO, Critic-V</td></tr>
<tr><td>Generic multimodal memory agent</td><td>Visual, semantic, episodic, and hierarchical memories already exist.</td><td>WorldMM, ViLoMem, VideoARM, R4</td></tr>
<tr><td>Generic long-term personalized memory</td><td>Remember–retrieve–align personalization is established.</td><td>PersonaVLM, M2A, POLAR</td></tr>
<tr><td>Generic macro-tool induction</td><td>Trajectory abstraction and skill lifecycle are existing mechanisms.</td><td>META, MUSE-Autoskill, SkillSmith</td></tr>
<tr><td>Generic dynamic multimodal GraphRAG</td><td>Interactive graph retrieval and editing are central already.</td><td>EvoGraph-R1</td></tr>
<tr><td>Generic self-evolving world model</td><td>Deployment-time memory repair and selective foresight already exist.</td><td>WorldEvolver</td></tr>
<tr><td>Generic evaluator co-evolution</td><td>Non-stationary evaluator evolution is explicit.</td><td>Red Queen Gödel Machine</td></tr>
<tr><td>Generic pairwise release validator</td><td>Pairwise parent–child gates already replace scalar rewards.</td><td>Reward-Free Evolving Agents</td></tr>
<tr><td>Generic decentralized multi-agent memory</td><td>Local memory pools and diversity preservation already exist.</td><td>DecentMem</td></tr>
<tr><td>Generic evolution protocol</td><td>Versioned resources, lineage, and rollback are specified.</td><td>Autogenesis</td></tr>
<tr><td>Generic agent–environment co-evolution</td><td>Adaptive environment and curriculum synthesis are active directions.</td><td>Agent-World, SimWorld Studio</td></tr>
<tr><td>Generic process-reward self-evolution</td><td>In-distribution critic and policy co-evolution already exist.</td><td>Q-Evolve</td></tr>
<tr><td>Generic regression-aware release engineering</td><td>Canonical versions and flip-centered gating already exist.</td><td>AgentDevel</td></tr>
</tbody></table><p>Retained ideas are narrower descendants. EvalRedQueen-V targets visual shortcuts rather than generic evaluator evolution; WorldPatch-V targets localized causal patches rather than generic world-model memory updates.</p>`,zh:`<table class="matrix"><thead><tr><th>淘汰表述</th><th>淘汰原因</th><th>最接近工作</th></tr></thead><tbody>
<tr><td>通用视觉问题生成 + GRPO</td><td>难度／多样性平衡视觉自博弈已存在。</td><td>VisPlay、Active Zero、Agent0-VL</td></tr>
<tr><td>通用视觉 critic 自纠错</td><td>视觉批评与迭代纠错高度拥挤。</td><td>VISCO、Critic-V</td></tr>
<tr><td>通用多模态记忆 Agent</td><td>视觉、语义、情景和层级记忆均已有工作。</td><td>WorldMM、ViLoMem、VideoARM、R4</td></tr>
<tr><td>通用长期个性化记忆</td><td>记忆—检索—对齐式个性化已经建立。</td><td>PersonaVLM、M2A、POLAR</td></tr>
<tr><td>通用轨迹宏工具归纳</td><td>轨迹抽象和技能生命周期已有直接工作。</td><td>META、MUSE-Autoskill、SkillSmith</td></tr>
<tr><td>通用动态多模态 GraphRAG</td><td>交互式检索和图编辑已是核心机制。</td><td>EvoGraph-R1</td></tr>
<tr><td>通用自进化世界模型</td><td>部署期记忆修复与选择性预见已有工作。</td><td>WorldEvolver</td></tr>
<tr><td>通用评价器共进化</td><td>非平稳评价器进化已经被明确提出。</td><td>Red Queen Gödel Machine</td></tr>
<tr><td>通用成对发布验证器</td><td>父子版本成对门控已替代标量奖励。</td><td>Reward-Free Evolving Agents</td></tr>
<tr><td>通用去中心化多 Agent 记忆</td><td>本地记忆池与多样性保持已有方案。</td><td>DecentMem</td></tr>
<tr><td>通用版本化进化协议</td><td>资源版本、溯源与回滚已有协议。</td><td>Autogenesis</td></tr>
<tr><td>通用 Agent—环境共进化</td><td>自适应环境和课程生成已形成方向。</td><td>Agent-World、SimWorld Studio</td></tr>
<tr><td>通用过程奖励自进化</td><td>分布内 critic 与策略共进化已有工作。</td><td>Q-Evolve</td></tr>
<tr><td>通用非回退发布工程</td><td>单一版本线和 flip 门控已有工作。</td><td>AgentDevel</td></tr>
</tbody></table><p>保留方向是更窄的后代。EvalRedQueen-V 针对视觉捷径，而不是通用评价器进化；WorldPatch-V 针对局部因果补丁，而不是通用世界模型记忆更新。</p>`}}
  ]
}
});
