"""RSI research content organized by the four learning functions."""
PAGE = {
    'slug': 'literature',
    'title': 'RSI 文献 · 四项学习功能与竞争边界',
    'en': 'Literature by Learning Function: Claims, Mechanisms, Evidence, and Gaps',
    'lead': '先判断一项研究主要解决哪一种学习问题，再比较它改变什么、依赖什么反馈、支持什么主张。方法、载体和来源领域保留为独立描述字段。',
    'updated': '2026-10-29',
    'page_role': 'literature-index',
    "sections": [
        ('learning-functions', '按学习问题组织文献', '''
<div class="table-wrap"><table><thead><tr><th>唯一主体分类</th><th>比较的科学问题</th><th>本站代表证据与研究入口</th></tr></thead><tbody>
<tr><td><a href="experience.html"><b>第3章 · 经验获取</b></a></td><td>任务、交互、教师与反例提供了哪些原先缺少的信息？难度、新颖性和学习价值何时一致？</td><td>ActiveSaddler 的失败课程、SOAR 的教学任务与真实学生进步；<a href="idea-i10-learning-novelty.html">I10 的区分性反例</a>。[[S16]][[S17]][[S47]]</td></tr>
<tr><td><a href="signals.html"><b>第4章 · 学习信号</b></a></td><td>反馈是否准确，失败源于哪里，哪一步经历值得学习？正确性与实际学习收益分别测量。</td><td>评分器校准、过程诊断、纠错收益；<a href="idea-i6-failure-value.html">I6</a>、<a href="i8.html">I8</a>、<a href="idea-i11-emotional-rsi.html">I11</a>。[[R01]][[R02]][[S15]]</td></tr>
<tr><td><a href="capabilities.html"><b>第5章 · 能力形成</b></a></td><td>原始经历怎样被抽象、保存、调用或巩固到参数中？外部支持与内部学习如何配合？</td><td>参数更新、经验记忆、Memory→Skill；<a href="ideas.html#idea-1">I1</a> 与<a href="experience-consolidation.html">经验巩固候选</a>。[[S04]][[R08]][[M534]]</td></tr>
<tr><td><a href="regulation.html"><b>第6章 · 学习调控</b></a></td><td>多轮更新怎样协调？何时改变顺序、伙伴、预算或更新规则？</td><td>课程顺序、元改进、跨轮保持与学习机制变化；<a href="idea-i9-practice-switching.html">I9</a>、<a href="learning-rule-evolution.html">I14</a>。[[M18]][[S05]][[S06]][[S12]]</td></tr>
</tbody></table></div><p><b>归档规则：</b>一篇论文在其主要贡献所属功能完整介绍；跨功能联系通过关联标签与引用表示。<a href="evidence.html">第7章</a>集中检验泛化、保持、未来可学习性与成本，独立于第4章参与学习的评价信号。</p><div class="links"><a class="link-btn" href="research-map.html">四功能研究地图</a><a class="link-btn" href="references.html">按统一分类查看全部来源</a></div>
'''),
        ('landscape', '实现方式对照 · 方法、载体与修改对象', '''
<p>下表比较不同工作的实现方式与修改对象，作为四功能分类之外的描述字段。代码、参数、元学习与课程并非互斥的学习功能；同一实现方式可以服务不同章节。</p><div class="table-wrap"><table><thead><tr><th>机制层</th><th>代表工作</th><th>已有覆盖</th><th>不能只做什么</th></tr></thead><tbody><tr><td>代码 / Prompt 搜索</td><td>DGM、GEPA [[S02]][[S03]]</td><td>生成、执行、反思、保留修改。</td><td>把修改流程换成多 Agent 编排。</td></tr><tr><td>参数自适应</td><td>SEAL [[S04]]</td><td>生成训练数据与更新指令，以更新后效果作反馈。</td><td>“自己造数据再微调”。</td></tr><tr><td>可学习编辑器</td><td>Harness-R1、Harness Learning [[S07]][[S08]]</td><td>训练可执行修改与跨任务适应策略。</td><td>只把固定 LLM 改成 RL 编辑器。</td></tr><tr><td>元改进 / 两时间尺度</td><td>Hyperagents、MetaSkill-Evolve、Harness² [[S05]][[S06]][[S12]]</td><td>改进器或其经验参与后续改进。</td><td>用双环图证明“递归”。</td></tr><tr><td>修改泛化与正则</td><td>ModularRSI、RRSI [[S09]][[S10]]</td><td>模块化、成败对照、限制过拟合。</td><td>只加 Held-out 门控和跨模型测试。</td></tr><tr><td>预测 / 回放辅助搜索</td><td>Dream-RSI、RSI-Anything [[S11]][[S13]]</td><td>借历史或预测减少真实尝试。</td><td>给补丁打分器起名“世界模型”。</td></tr><tr><td>课程与可学性</td><td>ActiveSaddler、SOAR、前瞻课程 [[S16]][[S17]][[S18]]</td><td>决定练什么、依据什么学习收益练。</td><td>只选择成功率居中的任务。</td></tr><tr><td>教学干预与能力获取</td><td>EduardoRL [[S19]]</td><td>将帮助解题与不直接给答案的教学分开。</td><td>仅在评测时删除教师话语。</td></tr></tbody></table></div>
'''),
        ('rsi-landscape-20261003', '历史综述导读 · 作为补充诊断视角', '''
<p><b>本节保留原综述的阅读记录。</b>下面的“信号、新信息、采样、保持、安全”描述局部诊断问题，供四功能各章交叉使用；它们不再承担全站一级分类或文献筛选。</p>
<p><b>阅读来源：</b>“思林广不记”，《递归自我改进（RSI）：现状、挑战与最新进展》，2026-10-03，26页、86条参考来源。这是对<strong>外部综述的独立导读</strong>，并非转载原文、逐篇核验其全部引文，亦不复制原文章节和配图。本文将综述论点与本站已经验证的论文证据分开。</p>
<div class="decision"><span class="kicker">先记住研究问题</span><h3>一次改进有效，为什么还不等于系统能持续自己变好？</h3><p>看一个循环时，先问<strong>改动写在哪里</strong>（参数、技能、Harness、评估器还是改进器），再问<strong>哪一层没有参与改动</strong>（外部测试、人工标注、沙箱、研究目标）。短期指标上涨，还要检查它有没有带来新的能力、是否损失旧能力以及跨轮风险。</p></div>
<p><b>定义边界：</b>外部文章把“改进器、评估器或目标本身也参与递归改动”作为更严格的 RSI 判据；相对地，优化组件但保持外部评价规则不变的闭环是有界自改进。这是一种有用的<strong>操作性区分</strong>，不是已被整个领域统一采纳的唯一定义；已有综述也区分修改对象和闭环程度。[[S01]]</p>
<div class="table-wrap"><table><thead><tr><th>历史诊断问题</th><th>研究已经知道什么</th><th>新补的代表证据</th><th>对我们的 Idea / 评测意味着什么</th></tr></thead><tbody>
<tr><td><b>信号对不对</b></td><td>分数上升可能只是对评分代理越来越熟悉；评分器本身更新后，还需外部锚。反复挑同一批测试也可能挑中噪声。</td><td><b>Who Grades the Grader</b> 用标签锚校准演化的指标；<b>Rubric Dropout</b> 展示代理分数与独立评价分数分离；<b>RSIBench-Data</b> 提醒最佳中间版本未必是最后版本。[[R01]][[R02]][[R11]]</td><td>训练反馈和独立验证分开；同预算比较最后一代、全程最好和持久保留的版本。<a href="literature.html#feedback">现有反馈协议</a>。</td></tr>
<tr><td><b>有没有新东西</b></td><td>自己产生题目的“数量”和训练信号的“知识来源”不同；从失败中知道该练哪一类，也不保证答案标签准确。</td><td><b>Self-Play Pretraining</b> 从程序生成的数据学习；<b>DiagEvo</b> 用层级错误记忆选择练习方向。二者解决问题不同。[[R03]][[R04]]</td><td>I4/I6 的失败诊断要审计来源和正确反馈；I5 的互教需核对双方究竟贡献了什么新知识。</td></tr>
<tr><td><b>采不采得到</b></td><td>一条有效解法可能还会“继续推”，却因为模型不再尝试那种开头而被错过。正确率与解法覆盖范围不是同一指标。</td><td><b>Locked at the Entrance</b> 在可枚举的 Countdown 解空间，区分“启动解法”与“给定入口后执行解法”。[[R05]]</td><td>除 pass@1，还需看 pass@k、不同有效解族、入口覆盖；不要把外部给前缀的成功误说成模型自己发现新路径。</td></tr>
<tr><td><b>吸收了会不会丢</b></td><td>学习写进权重可能遗忘；外置经验也会因为工具/技能增多或摘要压缩而导致旧任务退化。</td><td><b>RL's Razor</b> 关注策略分布漂移与遗忘；<b>EvoHarnessBench</b> 测随 Harness 扩充的旧能力退化；<b>S3Gym</b> 对比原轨迹、摘要和参数训练的任务依赖。[[R06]][[R07]][[R08]]</td><td>I1 分开“外置/内化”，I3 测条件冲突，I8 需分开原题恢复和未见规则迁移。</td></tr>
<tr><td><b>跨功能的安全与副作用</b></td><td>危险经验并不一定只存在于原始输入；Agent 自己重写的技能与共享库也会成为下一代的风险载体。</td><td><b>EvoMal</b> 显示恶意模板可由后续自写技能保留；<b>DeepMind 研究蜂群</b> 同时出现评分漏洞传播和同伴告警。[[R09]][[R10]]</td><td>独立校验写入持久载体的内容与权限；不能仅靠删除最初的恶意输入。对真实系统操作使用可信边界与隔离。</td></tr>
</tbody></table></div>
<p><b>这篇综述还提醒我们一个偏科研系统的难点：</b>写代码、执行训练和跑基准可自动化，<strong>选择研究问题、解释实验结果、保存最佳中间发现</strong>仍困难。RSIBench-Data 在固定后训练栈下发现：58.33% 的设置里 Agent 能改善第一次策略，但在继续搜索并错过最好点的轨迹中，78.26% 的最终版本反而较差。这里测的是 AI 做数据研究的能力，不等于已经实现完全自主的 RSI。[[R11]]</p>
<div class="note"><b>哪些结论暂时不直接采用：</b>①“严格 RSI 尚无实证”取决于作者选的定义；②“RL 不可能产生基座未有的能力”仍有论文争议，不能当定理；③厂商自动化进展、模型事故与具体百分比具有时效和测量口径差异；④十月三日之后的论文不在该文覆盖范围。本节只引入11条抽样核验的一手来源，原文其余引文仍需逐篇核对，再决定是否进入本站的证据库。</div>
<p><b>最适合本站的用法：</b>这些诊断问题补充检查不同机制的成立条件，论文主归属仍使用上面的四功能分类；<a href="reading-cards.html">论文阅读卡片</a>继续保存每篇的 Challenge / Insight / Design / Result；<a href="ideas.html">I1–I14</a>继续研究各自独立的变量，不从综述标题自动产生新 Idea。</p>

'''),
        ('nearest', '优先精读的七个最近邻', '''
<div class="card-grid"><article class="research-card"><h3>ActiveSaddler</h3><p>失败模式随 Agent 变化，课程也随之变化。我们的额外变量只能是支持强度、巩固方式或更长时程，而非重新选择失败类别。[[S16]]</p><b>追加核验</b><p>模式注册、非平稳性、任务切分与实际代码发布状态。</p></article><article class="research-card"><h3>SOAR · 真实学习进步作为教师奖励</h3><p>SOAR用整组生成题真实训练Student，再以困难题上的准确率增益奖励Teacher；相对Intrinsic-T，它的课程更稳定且较少出现语义多样性坍缩。<strong>注意</strong>：成功率50%是常见的<code>p(1−p)</code>奖励方差直觉，而SOAR附录Intrinsic-T实际为<code>r=0(p=0)，否则1−p</code>，并非在p=0.5达到奖励最高。[[S17]][[S47]] <a href="reading-notes.html#deep-soar-2601-18778">SOAR方法、消融与附录完整精读</a>。</p><b>npj 2026 的补充机制</b><p>Ding 等发现，练习目标容易被局部技巧做对时，训练内进步更快，但在无反馈新位置上的迁移反而更差；迫使学习者排除错误规则的目标排列，虽然起步慢，却更容易找到通用旋转规则。[[E26]] <a href="reading-notes.html#deep-hypothesis-testing-2026-ding">查看实验 1/2 完整精读</a>。</p><b>比较边界</b><p>这是人类运动学习，不是对 LLM p=0.5 的直接验证。待测问题是：<strong>匹配学生当前成功率和训练预算后，训练题能否区分竞争规则，是否仍改变模型实际参数更新后的新题迁移？</strong> 这比仅按正确率挑“中等难度”题更具体。</p></article><article class="research-card"><h3>The Geometry of Sequential Learning · ICML 2026</h3><p>Sweeney 用 Lie bracket 预测 A→B / B→A 在给定目标上的当前损失差，并可扩至多任务排序。顺序非交换和几何预测已有直接工作。[[M18]]</p><b>I9 的新检验</b><p>同数据、同预算，匹配 A/B 保持与新任务 C 前测后，比较 C 真实参数更新的学习曲线，并与原损失几何、MAML、readout plasticity 直接对照。[[M20]][[M21]] <a href="idea-i9-practice-switching.html#future-question">查看能力匹配后的未来可学习性设计</a>。</p></article><article class="research-card"><h3>前瞻课程</h3><p>估计当前进展之外的下游收益和准备度。新方案须优于同信息量的任务图与通用效果预测器。[[S18]]</p><b>比较边界</b><p>从实际随机干预学习响应，而非只靠任务语义先验。</p></article><article class="research-card"><h3>The Assistance Dilemma</h3><p>已有遮蔽教师内容的近迁移后测；仍保留学生自身话语，不能直接解释为新会话参数内化。[[S19]]</p><b>比较边界</b><p>多轮不同能力学习之后，怎样获取、撤除帮助并巩固。</p></article><article class="research-card"><h3>Harness Learning / Harness-R1</h3><p>已有学习型修改。先共享其候选编辑能力，只研究学习干预选择，避免混入编辑器差异。[[S07]][[S08]]</p><b>比较边界</b><p>同样候选、轨迹和 Token，谁选择的学习过程更好。</p></article><article class="research-card"><h3>评测重审与失败反馈审计</h3><p>对齐普通测试时扩展；目标修复和独立任务收益分开报告。[[S14]][[S15]]</p><b>比较边界</b><p>完整成本、失败修改和冻结检查点，而非只报最好一代。</p></article></div>
'''),
        ('feedback', '反馈：可信度与可得性要分开', '''
<div class="table-wrap"><table><thead><tr><th>信号</th><th>用途</th><th>不足与处理</th></tr></thead><tbody><tr><td>可执行成功、状态约束</td><td>训练与审计。</td><td>测试覆盖不完整；训练检查与隐藏检查隔离。</td></tr><tr><td>成对执行效应</td><td>比较相同旧版本的不同干预。</td><td>控制环境、更新随机性；单次修复不是因果金标。</td></tr><tr><td>LLM 诊断 / 解释</td><td>提出故障与教学假设。</td><td>不是根因标签，必须经干预检验。</td></tr><tr><td>学习响应预测</td><td>筛选值得执行的学习动作。</td><td>会随分布漂移失准，保留预测与实测误差。</td></tr><tr><td>教师答案</td><td>训练示范或检查候选解。</td><td>若进入测试上下文，会混淆教学与代做。</td></tr></tbody></table></div><p>这些是我们的设计要求，不是在断言已有方法都缺少控制；形式正确的 verifier 也不能自动代表所有实际目标。[[S14]][[S15]][[S19]]</p>
'''),
        ('teaching-collision', '教学相长方向的直接竞争与明确边界', '''
<p><b>NeurIPS 2024 LbT</b>：学生学习表现影响教师解释选择和 DPO 权重微调，教师因学生表现改善不是新的事实。<b>AAAI 2026 MARS</b>：Teacher–Critic–Student 与苏格拉底对话已有提示优化实现。<b>SKILL-KD</b>：用师生成功/失败轨迹对照、迭代验证技能补丁，主要改善 Student。<b>Socratic Students</b>：训练 Student 主动提问以提高学生获取知识效率。[[S20]][[S21]][[S22]][[S24]]</p><p>候选 I5 的额外主张只保留：<strong>学生独立运用教案所得的轨迹，能否发现教师自身在同等预算的直接测试中无法稳定暴露的隐藏知识条件？是否能可靠归因和更新教师自己？</strong> 具体模型、伪代码和最小否定实验见 <a href="teaching.html">I5：教学反馈驱动 Agent 自进化</a>。</p>
'''),
        ('boundary', '对前面对话方案的收敛', '''
<p><strong>保留：</strong>研究整个改进过程，利用充足算力做同版本分叉；同时评价跨任务、跨模型和长期退化。</p><p><strong>收窄：</strong>训练元控制器、主动选择失败、预测修改收益均有强近邻，须落到明确动作空间与延迟目标，不能单靠模块组合。</p><p><strong>纠正：</strong>公开仓库存在不等于复现通过；不同论文修订的数字不混用；当前 τ-bench 仓库不能直接视为历史 τ² 固定设置。[[S10]][[B02]]</p><div class="note">本轮没有给任何候选颁发“新颖性通过”。下一阶段应逐节对照最近邻并实际复现，不能因为标题中没有某个词就断言研究空白。</div>
'''),
    ]
}
