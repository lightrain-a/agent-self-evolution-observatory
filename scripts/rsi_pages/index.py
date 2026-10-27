PAGE = {
"slug":"index", "title":"RSI × 自主学习研究", "en":"Research on how agents learn · I1–I8",
"lead":"I1–I5 保留原问题；I6 研究失败轨迹的学习价值，以及何时继续、换错题或暂缓重访；I7 单独研究学习顺序，I8 研究错误规则迁移。",
"updated":"2026-10-27",
"sections":[
("decision","当前研究池：I1–I8 八个问题", '''<p>我们关心的不只是 Agent 能不能在一次任务里拿到更高分，而是：<strong>它能不能通过改写自身 Skill、Memory、Harness 或参数，真正学会下一次如何学得更好？</strong></p>
<div class="idea-board">
<a class="idea-board-card" href="ideas.html#idea-1"><span class="idea-id">I1 · 脚手架学习</span><b>哪些该自己学会，哪些用时再查？</b></a>
<a class="idea-board-card" href="ideas.html#idea-2"><span class="idea-id">I2 · 因材施教</span><b>同样犯错，怎么选适合自己的学习方法？</b></a>
<a class="idea-board-card" href="ideas.html#idea-3"><span class="idea-id">I3 · 温故知新</span><b>新方法有用却伤了旧能力，怎么办？</b></a>
<a class="idea-board-card" href="ideas.html#idea-4"><span class="idea-id">I4 · 生产性失败</span><b>失败一次就总结，还是再试几次？</b></a>
<a class="idea-board-card" href="ideas.html#idea-5"><span class="idea-id">I5 · 费曼学习法</span><b>和谁一起学，自己进步最快？</b></a>
<a class="idea-board-card" href="idea-i6-failure-value.html"><span class="idea-id">I6 · 错误轨迹</span><b>哪次失败值得学，什么时候该停下再回来？</b></a>
<a class="idea-board-card" href="idea-i7-learning-order.html"><span class="idea-id">I7 · 学习顺序</span><b>先独立尝试，还是先看正确示范？</b></a>
<a class="idea-board-card" href="i8.html"><span class="idea-id">I8 · 纠错迁移</span><b>纠正哪个错误，能让我学会一整类题？</b></a>
</div>
<p>I1–I5 每项都按 Challenge → 现有工作 → Insight → Design → 实验设计展开，方便直接汇报与组织论文；它们各自研究具体学习机制。<b>I6</b> 固定错误终点与教学过程，比较失败轨迹的学习价值，并用它决定继续、换错题或暂缓重访；<b>I7</b> 固定教材与预算，比较尝试和示范的先后顺序；<b>I8</b> 则验证高置信度错误、前置知识与共享规则对纠错迁移的作用。<a href="ideas.html">研究方向总览</a> · <a href="idea-i6-failure-value.html">I6</a> · <a href="idea-i7-learning-order.html">I7</a> · <a href="i8.html">I8</a></p>
<p>例如 R²Orch / PATS 已研究支架撤除；RSIFlow 已选择自改进工作流；HCL / SkillBoost 已研究回归；ActiveSaddler 已选有用的失败；PopuLoRA / OPCoD / MACE 已涉及群体教学、反馈和伙伴探索。我们需要回答比这些工作更细的问题。[[S26]][[S27]][[S28]][[S29]][[S30]][[S16]][[S32]][[S33]][[S34]]</p>'''),
("reading","研究导航：从证据走到可执行实验",'''<div class="route-grid">
<a href="timeline.html"><b>研究时间轴</b><span>CVPR / ICML / ACL DDL、论文阅读进度与研究节点。</span></a>
<a href="ideas.html"><b>I1–I5：具体学习机制</b><span>Challenge、现有工作、Insight、Design 与实验设计，统一为可直接讨论的研究卡片。</span></a>
<a href="idea-i6-failure-value.html"><b>I6：哪些失败值得学，何时该停？</b><span>同题同错误终点的轨迹为什么学习价值不同；何时换错题、暂缓和重访？</span></a>
<a href="idea-i7-learning-order.html"><b>I7：先自主尝试还是先看例题？</b><span>相同教材的学习顺序是否改变未来独立解题和可探索路径？</span></a>
<a href="i8.html"><b>I8：错误规则的跨题可学习性</b><span>从 Hypercorrection 出发，分析前置知识、共同错误规则与净学习收益。</span></a>
<a href="idea-i6.html"><b>历史草案：跨轮瓶颈切换</b><span>原版 I6 研究记录单独保留，不再使用当前 I6 编号。</span></a>
<a href="literature.html"><b>RSI 文献与竞争边界</b><span>改什么、如何改，哪些研究已进入元层自进化。</span></a>
<a href="reading-cards.html"><b>论文精读卡片</b><span>按信号、新信息、可采样性、保持和安全五问检索。</span></a>
<a href="reading-notes.html"><b>论文完整精读</b><span>保留方法细节、例子和已核实的论文信息。</span></a>
<a href="cross-domain.html"><b>相邻领域方法</b><span>元学习、课程、知识追踪、双重控制与持续学习。</span></a>
<a href="learning-science.html"><b>教育学与学习科学</b><span>哪些教育学机制有实证支持，哪些迁移仍是猜想。</span></a>
<a href="teaching.html"><b>教学反馈诊断 · I5 支线</b><span>此前“学生反馈能否暴露教师盲点”的详细实验草案，保留供比较。</span></a>
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
("scope","网站范围、历史方案与证据状态",'''<p>这是聚焦 RSI 选题的定向研究站，不是穷尽全领域的系统综述。<a href="ideas.html"><b>I1–I5 最新描述</b></a>以 2026-10-27 的问题表述为准：I5 主线为“按自身学习增益动态选择伙伴”；目前 <a href="idea-i6-failure-value.html">I6</a> 聚焦失败轨迹，<a href="idea-i7-learning-order.html">I7</a> 聚焦学习顺序。<a href="idea-i6.html">旧版瓶颈切换</a>已归档，不再占用 I6 编号。</p>
<p><a href="teaching.html">I5 教学反馈诊断</a>作为此前的独立技术支线保留：研究学生的误解能否暴露教师的隐性缺陷。这个实验与“动态伙伴选择”可以共享学生评估基础设施，但不是同一个问题。</p>
<p><a href="i8.html">I8</a> 研究不同知识准备程度和共享错误规则的跨题迁移；<a href="idea-i6-failure-value.html">I6</a> 则保持同题同错误终点，研究失败过程本身。两者可复用对照平台，但主张不能混用；所有研究都尚待真实训练验证。</p>
<p>原 <a href="/">Agent 自进化研究站</a>与本 RSI 站互相跳转。旧研究池中已经存在 Delayed Regression Exams 等关于回归测试的方案；I3 必须研究主动巩固操作本身，不能重新包装“多测一次”。</p>
<div class="status-strip"><b>截至 2026-10-27</b><span>I1–I8 候选研究问题已整理</span><span>最近邻来源已列出</span><span>独立实验待开展</span><span>不声称首次或已验证</span></div>''')]
}
