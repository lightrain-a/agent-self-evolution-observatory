PAGE = {
"slug":"index", "title":"RSI × 自主学习研究", "en":"Research on how agents learn · I1–I14",
"lead":"I1–I14 研究 Agent 的持续学习、学习规则与安全继承。新增 I14：固定学习者、任务与预算，检验从历史学习结果中改进更新规则，是否使模型真正更会学习。",
"updated":"2026-10-29",
"sections":[
("decision","当前研究池：I1–I14 · 十四个研究方向", '''<p>我们关心的不只是 Agent 能不能在一次任务里拿到更高分，而是：<strong>它能不能通过改写自身 Skill、Memory、Harness 或参数，真正学会下一次如何学得更好？</strong></p>
<div class="idea-board">
<a class="idea-board-card" href="ideas.html#idea-1"><span class="idea-id">I1 · 脚手架学习</span><b>哪些该自己学会，哪些用时再查？</b></a>
<a class="idea-board-card" href="idea-i2.html"><span class="idea-id">I2 · 因材施教</span><b>学生越来越会做题，教师也能越来越会教吗？</b></a>
<a class="idea-board-card" href="ideas.html#idea-3"><span class="idea-id">I3 · 温故知新</span><b>新方法有用却伤了旧能力，怎么办？</b></a>
<a class="idea-board-card" href="ideas.html#idea-4"><span class="idea-id">I4 · 生产性失败</span><b>失败一次就总结，还是再试几次？</b></a>
<a class="idea-board-card" href="idea-i5.html"><span class="idea-id">I5 · 十模型互教</span><b>什么时候交换舞伴，才能一起变强？</b></a>
<a class="idea-board-card" href="idea-i6-failure-value.html"><span class="idea-id">I6 · 错误轨迹</span><b>哪次失败值得学，什么时候该停下再回来？</b></a>
<a class="idea-board-card" href="idea-i7-learning-order.html"><span class="idea-id">I7 · 学习顺序</span><b>先独立尝试，还是先看正确示范？</b></a>
<a class="idea-board-card" href="i8.html"><span class="idea-id">I8 · 纠错迁移</span><b>纠正哪个错误，能让我学会一整类题？</b></a>
<a class="idea-board-card" href="idea-i9-practice-switching.html"><span class="idea-id">I9 · 集中与交错练习</span><b>何时交错？同样学会后谁更容易学新规则？</b></a>
<a class="idea-board-card" href="idea-i10-learning-novelty.html"><span class="idea-id">I10 · 规则区分与组合学习</span><b>哪种练习才能真正教会模型规则？</b></a>
<a class="idea-board-card" href="idea-i11-emotional-rsi.html"><span class="idea-id">I11 · 情绪反馈与自我迭代</span><b>鼓励、批评还是中性反馈，能让我下一版真正变强？</b></a>
<a class="idea-board-card" href="idea-i12-prerequisite-bottleneck.html"><span class="idea-id">I12 · 共同前置知识瓶颈</span><b>补一条规则，能否让多个任务开始学得会？</b></a>
<a class="idea-board-card" href="learning-admission.html"><span class="idea-id">I13 · RSI 安全更新接纳</span><b>哪些自我修改可以安全继承？</b></a>
<a class="idea-board-card" href="learning-rule-evolution.html"><span class="idea-id">I14 · 学习规则自进化</span><b>学会做题后，能否越来越会学习？</b></a>
</div>
<p><b>I13 · Safety-Aware Update Admission：</b><a href="learning-admission.html">研究跨代安全风险的事前诊断与有限预算验证</a>。候选更新可以被接纳、隔离、暂缓或拒绝；最关键是同时降低不安全更新漏放和安全更新误拒，并让 Meta-Admission 的诊断策略跨代改进。安全不变量和最终发布权仍由独立验证层掌握。P0/P1/P2 均待实验。</p>
<p><b>I14 · 正式编号：</b><a href="learning-rule-evolution.html">Learning Rule Evolution</a> 已纳入研究池，固定同一学生、数据、训练顺序和教师，研究更新规则 η 能否提高未见任务 C 的真实学习曲线。<a href="reading-notes.html#deep-hattori-ofc-metarl-nn2023">Hattori 2023</a> 提供快/慢机制和干预范式，<a href="reading-notes.html#deep-discorl-nature2025-oh">DiscoRL 2025</a> 提供可学习目标生成先例。编号不代表已经完成 P0；结果不足可降级合并。</p>
<p><b>I2 最新合并：</b>保留因材施教与小预算试学，增加教师自身的教学更新；分别证明学生独立能力和教师教学能力增长。<a href="idea-i2.html">进入师生共进化方案</a>。</p>
<p>I1–I5 每项都按 Challenge → 现有工作 → Insight → Design → 实验设计展开；其中 <a href="idea-i5.html"><b>I5</b></a> 专门研究十模型互教的动态配对与交换顺序，不重新设计学习方法。<b>I6</b> 固定错误终点与教学过程，比较失败轨迹的学习价值，并用它决定继续、换错题或暂缓重访；<b>I7</b> 固定教材与预算，比较尝试和示范的先后顺序；<b>I8</b> 则验证高置信度错误、前置知识与共享规则对纠错迁移的作用；<b>I9</b> 固定各主题训练材料，研究集中和交错的切换时点；<b>I10</b> 在同一规则下比较区分性反例能否经真实参数更新产生组合泛化；<b>I11</b> 固定正确反馈与更新器，只改变语气，评估学习控制决策和持久净收益；<b>I12</b> 固定学习器、反馈与后续目标题流，研究修复共同因果前置知识能否解锁新一轮学习。<a href="ideas.html">研究方向总览</a> · <a href="idea-i6-failure-value.html">I6</a> · <a href="idea-i7-learning-order.html">I7</a> · <a href="i8.html">I8</a> · <a href="idea-i9-practice-switching.html">I9</a> · <a href="idea-i10-learning-novelty.html">I10</a> · <a href="idea-i11-emotional-rsi.html">I11</a> · <a href="idea-i12-prerequisite-bottleneck.html">I12</a> · <a href="learning-admission.html">I13</a> · <a href="learning-rule-evolution.html">I14</a></p>
<p>例如 R²Orch / PATS 已研究支架撤除；RSIFlow 已选择自改进工作流；HCL / SkillBoost 已研究回归；ActiveSaddler 已选有用的失败；PopuLoRA / OPCoD / MACE 已涉及群体教学、反馈和伙伴探索。我们需要回答比这些工作更细的问题。[[S26]][[S27]][[S28]][[S29]][[S30]][[S16]][[S32]][[S33]][[S34]]</p>'''),
("reading","研究导航：从证据走到可执行实验",'''<div class="route-grid">
<a href="idea-i2.html"><b>I2：因材施教的师生共进化</b><span>教师从学生真实学习收益中改进教法；学生持续获得独立能力。</span></a>
<a href="idea-i2.html#learner-response-question"><b>I2 扩展：训练前预测学习者对教学的真实响应</b><span>Centaur × StudentSim：下一次回答与真实 LoRA 更新后的独立能力不同；已设计 LR-P0/P1/P2、强基线与成本账本。</span></a>
<a href="reading-notes.html#deep-nature2025-centaur-binz"><b>Nature 2025 · Centaur 完整精读</b><span>Psych-101、QLoRA、未见实验 OOD、开放环、fMRI 与认知机制发现；对照 StudentSim 的直接最近邻。</span></a>
<a href="timeline.html"><b>研究时间轴 · 交互月历</b><span>CVPR / ICML / ACL 秒级 DDL 倒计时、月历、论文精读与研究标签联动。</span></a>
<a href="idea-prioritization.html"><b>I1–I14 · 优先级与决定性实验（2026-10-29）</b><span>I1–I13 保留历史双排名，I14 已编号但分数待评估；列出 P0、强基线、Go/降级标准与原始论文依据。</span></a>
<a href="ideas.html"><b>I1–I14：具体学习机制</b><span>Challenge、现有工作、Insight、Design 与实验设计，统一为可直接讨论的研究卡片。</span></a>
<a href="idea-i5.html"><b>I5：十模型互教与交换舞伴</b><span>Nature 群体学习、Jigsaw 与双向共进化的动态伙伴网络。</span></a>
<a href="idea-i6-failure-value.html"><b>I6：哪些失败值得学，何时该停？</b><span>同题同错误终点的轨迹为什么学习价值不同；何时换错题、暂缓和重访？</span></a>
<a href="idea-i7-learning-order.html"><b>I7：先自主尝试还是先看例题？</b><span>相同教材的学习顺序是否改变未来独立解题和可探索路径？</span></a>
<a href="i8.html"><b>I8：错误规则的跨题可学习性</b><span>从 Hypercorrection 出发，分析前置知识、共同错误规则与净学习收益。</span></a>
<a href="reading-notes.html#deep-nhb2025-transfer-interference-holton"><b>Nature Human Behaviour 2025/2026 · 迁移与干扰</b><span>305人的A→B→A和Rich/Lazy神经网络：学B更快为何容易错用旧A规则？I3规则边界修复P0/P1/P2。[[E100]]</span></a>
<a href="reading-notes.html#deep-nature2025-orthogonalized-state-machine-sun"><b>Nature 2025 · 海马体学习潜在状态机（完整精读）</b><span>CA1 正交化随学习形成；CSCG、LSTM、Transformer 的反例；关联 I8 的状态别名与 I9 的未来学习。[[E353]]</span></a>
<a href="curriculum-scale-evidence.html"><b>LLM/VLM跨规模证据：重复、多样性与遗忘</b><span>ICLR/ACL/NeurIPS/CVPR 3B–70B模型近邻；为什么小Transformer中的动态课程不能直接迁移到大LLM和VLM。[[M500]][[M501]][[M505]]</span></a>
<a href="reading-notes.html#deep-nhb2025-distribution-curriculum-pesnot-lerousseau"><b>Nature Human Behaviour 2026：记忆与规则的课程竞争</b><span>530人+小Transformer的Zipf频次、混合分布、Figure4b/c/e、C1/C2命名冲突；完整十节精读。[[E360]]</span></a>
<a href="idea-i9-practice-switching.html"><b>I9：课程顺序与未来可学习性</b><span>保留集中/交错切换；新增 A→B 与 B→A 当前能力相近时，学习 C 的速度是否不同。</span></a>
<a href="idea-i10-learning-novelty.html"><b>I10：规则区分、参数吸收与组合泛化</b><span>Nature 2023 MLC、100%正确监督与20%人类式错误标签的区别；T1/T2对照及受控 P0。</span></a>
<a href="idea-i11-emotional-rsi.html"><b>I11：哪种情绪反馈能改善长期自我迭代？</b><span>固定真实反馈，只改鼓励/批评/紧迫/中性措辞；测校准、学习动作及 Skill/LoRA 多轮净增益。</span></a>
<a href="idea-i12-prerequisite-bottleneck.html"><b>I12：发现共同前置知识瓶颈</b><span>Nature 高阶知识骨架与真实 RSI 因果验证：为什么先补一个关键规则，会让多任务下游训练变得有效？</span></a>
<a href="memory-research-map.html"><b>RSI 记忆研究地图 · 历史、检索、巩固和记忆策略</b><span>梳理历史状态诊断、记忆检索、经验巩固与元记忆控制。学习规则自身的更新已编号I14；记忆子问题仍保持未编号候选。[[E370]][[M530]]</span></a>
<a href="reading-notes.html#deep-nhb2026-hybrid-memory-eckstein"><b>Nature Human Behaviour 2026 · Hybrid Memory-ANN完整精读</b><span>862人、617871次选择、Q值 vs Context-ANN vs Memory-ANN，Figure 3i/4g的多时间尺度历史、与RSI未来LoRA学习状态的边界。[[E370]]</span></a>
<a href="learning-signal-bottlenecks.html"><b>新候选：高水平平台期，换训练信号还是继续练习？</b><span>Science Advances 2020 的主动触觉训练、普通练习与正确反馈消融；按“专家残差型/低成功稀疏型/局部捷径型”区分平台，并设计真实LoRA辨别训练对照。[[E380]][[E381]]</span></a>
<a href="reading-notes.html#deep-scienceadv2020-expert-haptic-ceiling-hirano"><b>Science Advances 2020 · 专家技能瓶颈与主动触觉训练</b><span>三项原实验、训练剂量未配平、30分钟短时保持、2024 iScience机制补充与RSI迁移。</span></a>
<a href="learning-rule-evolution.html"><b>I14 · 学习规则自进化：Agent 什么时候真正变得更会学习？</b><span>Hattori 2023 的快慢元学习干预 + DiscoRL 2025 的更新目标生成；只改变学习规则，验证未见任务C的真实学习曲线。</span></a>
<a href="experience-consolidation.html"><b>研究候选：经验何时升级成长期能力？</b><span>结合Science 2024、ACL 2026与Faulty Memory预印本；保留原始Episode、抽象Skill或真实LoRA更新怎样选择、验证与继承？</span></a>
<a href="learning-admission.html"><b>I13：Safe to Inherit？RSI 安全更新接纳</b><span>已核对跨代故障与 Skill 持久风险；固定独立硬门，学习风险诊断和选择性测试，比较漏放、误拒及长期安全净能力。</span></a>
<a href="reading-notes.html#deep-nc2025-metacognition-underconfidence-katyal"><b>NC 2025 · 局部信心与整体自评</b><span>真实反馈选择如何改变总体自评？全文精读、D1/D2/D3 与 I11 实验。[[E29]]</span></a>
<a href="idea-i6.html"><b>历史草案：跨轮瓶颈切换</b><span>原版 I6 研究记录单独保留，不再使用当前 I6 编号。</span></a>
<a href="literature.html#rsi-landscape-20261003"><b>RSI 领域全景与竞争边界</b><span>新增 2026-10-03 综述导读：改什么、固定什么，四问 + 安全与一手证据。</span></a>
<a href="reading-cards.html"><b>论文精读卡片</b><span>按信号、新信息、可采样性、保持和安全五问检索。</span></a>
<a href="reading-notes.html#deep-lake-baroni-mlc-nature2023"><b>Nature 2023 · MLC 元学习与系统性组合泛化</b><span>10节完整精读、20%错误监督为什么存在、Table1与Table2的不同指标及外推边界。[[E350]]</span></a>
<a href="reading-notes.html#deep-nn2024-planning-replay-jensen"><b>Nature Neuroscience 2024 · Planning &amp; Hippocampal Replay 完整精读</b><span>Think vs Act；94人/5模型/37动物session；Figure 3 同数量随机时机对照，迁移到I4/I6的多采样 vs 立即更新 P0。[[E355]]</span></a>
<a href="reading-notes.html"><b>论文完整精读</b><span>保留方法细节、例子和已核实的论文信息。</span></a>
<a href="reading-notes.html#deep-hattori-ofc-metarl-nn2023"><b>Nature Neuroscience 2023 · OFC快慢元强化学习</b><span>小鼠概率反转任务、5个A2C递归模型、早期/专家可塑性抑制与OFC活动抑制，区分当前任务改进和学习策略形成。</span></a>
<a href="reading-notes.html#deep-nonlocal-replay-science2021-liu"><b>Science 2021 · 非局部学习与反向重放</b><span>29人的奖励路径实验、MEG证据、Need × Gain与8篇LLM最近邻；接到I8单次纠错的独立迁移实验。</span></a>
<a href="theory-notes.html"><b>理论工具箱：学习规则与元梯度</b><span>DiscoRL 的目标生成、半梯度可表达性、元梯度推导与稳定化：固定锚点、公式、LaTeX及证据边界，后续论文可以直接引用。</span></a>
<a href="reading-notes.html#deep-onan-self-organized-interleaving-2024"><b>npj 2024 · 自主安排学习顺序：反驳错误观念与元认知提示</b><span>91 人随机实验、35 次逐项排课、5–7 天策略迁移；为什么交错行为显著改变，但分类成绩组间不显著？对 I9 自主学习计划的启发。[[E310]]</span></a>
<a href="reading-notes.html#deep-hgm-2510-21614"><b>HGM · ICLR 2026 Oral 完整精读</b><span>当前成绩为何不等于后代潜力？详解 GMP/CMP、支系统计、Thompson Sampling、Table 1–4 和 RSI 研究边界。[[S310]]</span></a>
<a href="reading-notes.html#deep-soar-2601-18778"><b>SOAR · ICML 2026 完整精读</b><span>双层Meta-RL、真实学习增益、Intrinsic奖励实际公式、Promotion、多样性坍缩及I2/I6/I8/I9的研究边界。</span></a>
<a href="reading-notes.html#deep-rote-learning-iclr2026-wu"><b>ICLR 2026 · Rote Learning：先记忆再泛化</b><span>读懂两阶段记忆与语义映射；重点看两跳生成36%、多选16%与ICL直给事实95%的不同条件。</span></a>

<a href="reading-notes.html#deep-mosaic-memory-2026-shilov"><b>Nature Communications 2026 · Mosaic Memory</b><span>模糊重复为何仍强化记忆？精读MIA校准、词序与语义对照，以及RSI“新文本≠新能力”的实验边界。</span></a>
<a href="cross-domain.html"><b>相邻领域方法</b><span>元学习、课程、知识追踪、双重控制与持续学习。</span></a>
<a href="learning-science.html"><b>教育学与学习科学</b><span>哪些教育学机制有实证支持，哪些迁移仍是猜想。</span></a>
<a href="experiments.html"><b>实验执行方案</b><span>版本控制、持久更新、数据隔离与元学习评估。</span></a>
<a href="references.html"><b>来源与核验记录</b><span>[[SOURCE_COUNT]] 条论文和官方资源，保留原始链接与阅读深度。</span></a></div>'''),
("claims","必须分开的三个研究主张",'''<div class="table-wrap"><table><thead><tr><th>主张</th><th>应观察什么</th><th>不能据什么下结论</th></tr></thead><tbody>
<tr><td>眼前任务做得更好</td><td>有人帮忙、提示或额外执行后的成功率。</td><td>当前题目答对，就说自己学会。</td></tr>
<tr><td>Agent 获得了持久能力</td><td>只保留版本化 Skill / Memory / Harness / 参数，清空临时上下文，在新任务上仍进步。</td><td>答案、同伴或教师仍在上下文里。</td></tr>
<tr><td>Agent 更会自我改进</td><td>保留学到的学习策略，重置任务 Agent，在新的任务流中能否更快改进。</td><td>迭代次数更多、模型更大或训练预算更多。</td></tr>
</tbody></table></div>
<p>只要设计了循环，就能叫自我迭代，但<strong>要声称“递归地改进改进器”还需要额外证据</strong>。如 MetaSkill-Evolve 已研究元技能进化，不能再把“有两个循环”本身作为创新。[[S06]]</p>
<div class="note">独立评测必须固定并与训练数据隔离；能力提升不会自动扩大 Agent 的真实工具权限。即便改进器学习，安全审计仍应独立。</div>'''),
("method","从教育学概念到论文问题，怎么做？",'''<ol class="research-steps">
<li><b>先说一个生活中的具体例子。</b>例如为什么新 Skill 影响旧 Skill，或为何同样 Bug 有人看示范就会、有人不会。</li>
<li><b>说清最近邻研究了什么。</b>不能因为前人没用“费曼”“温故知新”这些词，就认定没人研究机制。</li>
<li><b>问一个更具体的差异。</b>别人研究哪个失败值得修，我们研究失败后下一次试验何时该做、什么时候可以归纳。</li>
<li><b>定义 Agent 真的学到了什么。</b>明确 Skill / Memory / Harness / 权重的可持久写入与回滚。</li>
<li><b>先做最小对照。</b>同预算比较固定简单策略与我们的方法，排除更多尝试、更多 token、外部答案泄漏。</li>
<li><b>再检验长期进步。</b>连续多轮、新任务、旧能力回归，最后才评价改进策略本身有没有变好。</li>
</ol>'''),
("scope","网站范围、历史方案与证据状态",'''<p>这是聚焦 RSI 选题的定向研究站，不是穷尽全领域的系统综述。<a href="ideas.html"><b>I1–I5 最新描述</b></a>以 2026-10-27 的问题表述为准：<a href="idea-i5.html">I5 主线</a>为“十模型按双向独立学习收益动态配对与决定换伴”；目前 <a href="idea-i6-failure-value.html">I6</a> 聚焦失败轨迹，<a href="idea-i7-learning-order.html">I7</a> 聚焦学习顺序。<a href="idea-i6.html">旧版瓶颈切换</a>已归档，不再占用 I6 编号。</p>
<p><a href="idea-i5.html#teaching-feedback">I5 统一详情页</a>同时保留“教学反馈诊断”作为历史研究支线：学生的误解能否暴露教师自己的隐性缺陷。它与当前的“动态伙伴选择”有不同的研究问题，因此在详情页中区分，不再在左侧目录重复出现。</p>
<p><a href="idea-i9-practice-switching.html">I9</a> 固定教材，研究跨主题集中/交错的切换，并增加同材料不同顺序的第三任务学习曲线实验；<a href="i8.html">I8</a> 研究不同知识准备程度和共享错误规则的跨题迁移；<a href="idea-i6-failure-value.html">I6</a> 则保持同题同错误终点，研究失败过程本身。两者可复用对照平台，但主张不能混用；所有研究都尚待真实训练验证。</p>
<p>原 <a href="/">Agent 自进化研究站</a>与本 RSI 站互相跳转。旧研究池中已经存在 Delayed Regression Exams 等关于回归测试的方案；I3 必须研究主动巩固操作本身，不能重新包装“多测一次”。</p>
<div class="status-strip"><b>截至 2026-10-28</b><span>I1–I14 已整理，I14 P0/P1 待实验</span><span>最近邻来源已列出</span><span>独立实验待开展</span><span>不声称首次或已验证</span></div>''')]
}
