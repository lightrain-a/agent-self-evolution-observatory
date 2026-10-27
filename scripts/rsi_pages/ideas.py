"""I1–I5 concrete learning ideas, current I6 failure trajectories, I7 learning order, I8 error-rule transfer.

The earlier bottleneck-switching proposal remains accessible as a historical draft.
Research hypotheses are separate from measured findings.
"""
PAGE = {
 "slug": "ideas",
 "title": "I1–I8：八个研究问题",
 "en": "I1–I8 · distinguish failure paths, learning order, and rule transfer",
 "lead": "I6 比较失败轨迹的独立学习收益，并判断何时继续、切换错误或暂缓重访；I7 研究学习顺序，I8 研究错误规则的迁移。三个问题各自验证。",
 "updated": "2026-10-27",
 "sections": [
 ("portfolio", "研究方向，一眼看懂",  '''
 <p>共同目标：<strong>让 Agent 不只是从执行结果里积累经验，还能随着自身能力变化，学会选择更好的自我改进方式。</strong>I1–I5 保留原有研究问题；I6 只比较失败轨迹过程，I7 只比较学习顺序，I8 从知识准备与共同错误规则解释迁移。</p>
 <div class="idea-board">
 <a class="idea-board-card" href="#idea-1"><span class="idea-id">I1 · 脚手架学习法</span><b>哪些该自己学会，哪些用时再查？</b><small>辅助使用与内化的取舍</small></a>
 <a class="idea-board-card" href="#idea-2"><span class="idea-id">I2 · 因材施教</span><b>同样犯错，为什么学习方法不同？</b><small>根据真实学习反应选方法</small></a>
 <a class="idea-board-card" href="#idea-3"><span class="idea-id">I3 · 温故知新</span><b>新方法有用，却和旧方法冲突怎么办？</b><small>复习并解决适用条件冲突</small></a>
 <a class="idea-board-card" href="#idea-4"><span class="idea-id">I4 · 生产性失败</span><b>失败一次就总结，还是再试几次？</b><small>判断何时证据足够更新 Skill</small></a>
 <a class="idea-board-card" href="idea-i5.html"><span class="idea-id">I5 · 十模型互教</span><b>什么时候交换舞伴，才能一起变强？</b><small>十模型学习网络的动态重组</small></a>
 <a class="idea-board-card" href="idea-i6-failure-value.html"><span class="idea-id">I6 · 失败学习价值</span><b>哪条失败更值得纠正？何时停下再回来？</b><small>固定纠错方式，比较失败的独立收益与继续尝试成本</small></a>
 <a class="idea-board-card" href="idea-i7-learning-order.html"><span class="idea-id">I7 · 学习顺序</span><b>先看例题，还是先独立尝试？</b><small>固定教材与预算，研究独立能力、探索与多轮迁移</small></a>
 <a class="idea-board-card" href="i8.html"><span class="idea-id">I8 · 错误学习迁移</span><b>改正哪个错误，能够学会一整类题？</b><small>Hypercorrection 与跨题净学习收益</small></a>
 </div>
 <p class="idea-outline-key"><b>I1–I5 统一阅读顺序：</b>Challenge（难在哪里） → 现有工作（别人做到了哪） → Insight（为何可解） → Design（如何做） → 实验设计（怎么验证）。先说清问题，再谈方法，可直接用于向师兄汇报和论文初稿。</p>
 <p class="status">状态：I1–I8 研究问题已整理；I6 与 I7 正交拆分，I8 保留独立机制验证；尚无本项目的受控实测结果。</p>
 <p>本站将它们挂到 RSI 的四个问题与安全轴下：<b>信号对不对 / 有没有新东西 / 采不采得到 / 吸收了会不会丢 / 安全。</b>这些标签表示要研究的环节，不表示问题已经解决。详见 <a href="reading-cards.html">论文阅读卡片</a>。</p>
 '''),
 ("idea-1", "I1：脚手架学习法——哪些该自己学会，哪些用时再查？", '''
 <div class="idea-focus"><span class="idea-axis">采不采得到</span><span class="idea-axis">吸收了会不会丢</span><p><b>一句话：</b>调试思路最好自己掌握，但经常变化的 API 规则可以用时再查。Agent 能自己判断哪些该学会、哪些该留作外部帮助吗？</p></div>
 <div class="idea-steps">
 <div class="idea-step"><h3>Challenge <small>（难在哪里）</small></h3><p>在帮助下完成任务，不等于撤掉帮助后还能独立做。什么都写进 Skill，可能把过时规则也记住；什么都留在外部，又要反复查询。难的是还不知道未来任务怎么变，就要先决定哪些知识值得长期掌握。</p></div>
 <div class="idea-step"><h3>现有工作 <small>（别人研究了什么）</small></h3><p><b>R²Orch</b> 研究的是怎样把 Skill 内化、什么时候可以撤掉 Skill；<b>PATS</b> 研究的是随着学习进展怎样调整并撤除临时支架。我们不是再做一次“帮助逐渐减少”，而是研究<strong>不同经验究竟该留在哪里</strong>。[[S26]][[S27]]</p></div>
 <div class="idea-step"><h3>Insight <small>（为何可解）</small></h3><p>外部帮助并不都一样。稳定且反复使用的操作方法可能适合自己学会；容易变化的事实可能更适合按需查询。比较<strong>撤除帮助后的独立能力、知识变化频率和长期成本</strong>，有机会学会这两种方式的取舍。</p></div>
 <div class="idea-step"><h3>Design <small>（如何做）</small></h3><p>将辅助经验分成稳定方法、易变规则和临时提示，让 Agent 选择内化、外置查询或混合保留。分开测“完全不给帮助”和“允许按需查询”的表现，再根据这些结果更新下一轮的选择方式。</p>
 <div class="flow"><div><b>拆分辅助经验</b><small>稳定方法 / 易变知识</small></div><div><b>选择存放方式</b><small>内化 / 查询 / 混合</small></div><div><b>新任务测能力</b><small>撤辅与查询分开</small></div><div><b>更新取舍规则</b><small>比较收益和成本</small></div></div></div>
 <div class="idea-step"><h3>实验设计 <small>（怎么验证）</small></h3><p>准备稳定的调试技巧与会变动的 API 规则，在相同预算下比较<strong>全部内化、全部外置、固定渐隐、自适应取舍</strong>，并与 R²Orch/PATS 的可复现做法比较。重点看无辅助的新任务成功率、API 更新后的适应性、调用成本和旧能力退化。如果固定规则同样好，说明动态选择还没有额外价值。</p></div>
 </div>'''),
 ("idea-2", "I2：因材施教——同样犯错，为什么学习方法不同？", '''
 <div class="idea-focus"><span class="idea-axis">信号对不对</span><span class="idea-axis">采不采得到</span><p><b>一句话：</b>两个 Agent 都不会修一个 Bug，一个看示范就会了，另一个要比较几次失败才学得会。怎样找到各自最适合的学习方法？</p></div>
 <div class="idea-steps">
 <div class="idea-step"><h3>Challenge <small>（难在哪里）</small></h3><p>知道“错在哪里”，不等于知道“怎么学最快”。同一种错误，换个模型或学习阶段，最有用的学习方式可能不同；但把所有学法试一遍又太贵。还要避免把眼前这道题的进步当成长久的能力提升。</p></div>
 <div class="idea-step"><h3>现有工作 <small>（别人研究了什么）</small></h3><p><b>RSIFlow</b> 研究的是失败后该修改模型、Harness 还是任务产物；<b>MetaSkill-Evolve</b> 研究的是任务 Skill 和改进 Skill 的方法怎样一起演化。我们先固定<strong>更新的是 Skill</strong>，只研究同样的失败该用哪种学习方法，而不是重新做更新对象路由。[[S28]][[S06]]</p></div>
 <div class="idea-step"><h3>Insight <small>（为何可解）</small></h3><p>只看错误标签，可能看不出 Agent 最适合的学法；但是少量“试学”能告诉我们，<strong>它看示范、做反例对照或自己重试后，哪一种真的学得更快</strong>。Agent 变强后重新测，就能发现原来有效的方式是否还适合。</p></div>
 <div class="idea-step"><h3>Design <small>（如何做）</small></h3><p>对同一种失败，从相同 Skill 快照出发，分叉尝试示范、对比失败和独立练习。用另一批任务检验每种方式学完后的独立能力，再选择下一轮学法，并记录它在不同能力阶段的效果。</p>
 <div class="flow"><div><b>固定同类失败</b><small>同一个 Skill 更新目标</small></div><div><b>小预算试学</b><small>示范 / 反例 / 重试</small></div><div><b>测独立进步</b><small>测试任务不能参与试学</small></div><div><b>下轮重新选</b><small>随能力更新学法</small></div></div></div>
 <div class="idea-step"><h3>实验设计 <small>（怎么验证）</small></h3><p>选多个能力阶段的 Agent，在同类任务上比较<strong>固定学法、只按错误类型选、普通 bandit、根据少量试学反应选</strong>。试学本身的费用也计入预算；主要看未见题的独立提升，以及能力变强后最佳学法是否改变。与 <a href="idea-i6.html">I6</a> 分开：I2 只决定当前学习任务该怎么学，不决定跨多轮要转去补知识还是改验证器。</p></div>
 </div>'''),
 ("idea-3", "I3：温故知新——新方法有用，却和旧方法冲突怎么办？", '''
 <div class="idea-focus"><span class="idea-axis">吸收了会不会丢</span><span class="idea-axis">安全</span><p><b>一句话：</b>Agent 学会一个更快的新方法，却把以前在另一种场景下正确的做法弄坏了。新旧本事能不能都留下来？</p></div>
 <div class="idea-steps">
 <div class="idea-step"><h3>Challenge <small>（难在哪里）</small></h3><p>新 Skill 确实提高了部分任务的成功率，却可能让旧任务变差。直接回滚就失去了新进步；把所有旧题重做一遍又浪费预算。首先得弄清是旧知识真忘了，还是新旧规则用错了地方。</p></div>
 <div class="idea-step"><h3>现有工作 <small>（别人研究了什么）</small></h3><p><b>HCL</b> 研究的是 Harness 更新后如何兼顾新任务与旧任务；<b>SkillBoost</b> 研究的是用回归检查和约束防止新 Skill 伤害旧能力。我们进一步研究<strong>当新旧方法都各有用处时，怎样通过复习修好冲突，而不是只能拒绝新更新</strong>。[[S29]][[S30]]</p></div>
 <div class="idea-step"><h3>Insight <small>（为何可解）</small></h3><p>有些退化未必是忘记，而是<strong>两个原本都有效的方法，被用在了不适合的场景</strong>。只要找到“什么时候用旧规则、什么时候用新规则”的区别，少量针对这些边界的练习，可能比全部重放旧经验更有效。</p></div>
 <div class="idea-step"><h3>Design <small>（如何做）</small></h3><p>比较修改前后的失败轨迹，找到出现冲突的条件，自动生成少量只改变一个关键条件的练习。用这些例子修订 Skill 的适用范围或选择规则，必要时再对参数做巩固。最终既要会用新方法，也不能丢旧能力。</p>
 <div class="flow"><div><b>发现旧任务退化</b><small>新旧版本对比</small></div><div><b>定位冲突条件</b><small>何时该用哪一条</small></div><div><b>有针对性地复习</b><small>只练容易混淆的场景</small></div><div><b>一起检验新旧能力</b><small>旧题 / 新题 / 组合题</small></div></div></div>
 <div class="idea-step"><h3>实验设计 <small>（怎么验证）</small></h3><p>准备两套分别有效、合起来容易冲突的 Skill，并加入自然学习中出现的冲突案例。比较<strong>退化即回滚、均匀重放、MIR 风格重放、针对冲突条件复习</strong>；固定复习次数和记忆预算。分别测旧能力保持、新能力增益、组合任务成功率。如果优势只来自存了更多规则或多练了题，就不能归因于我们的复习方法。[[M09]]</p></div>
 </div>'''),
 ("idea-4", "I4：生产性失败——失败一次就总结，还是再试几次？", '''
 <div class="idea-focus"><span class="idea-axis">信号对不对</span><span class="idea-axis">有没有新东西</span><span class="idea-axis">采不采得到</span><p><b>一句话：</b>API 超时一次，Agent 就总结“这个工具以后别用”，可能学错。什么时候应该继续试，什么时候才值得把经验写进 Skill？</p></div>
 <div class="idea-steps">
 <div class="idea-step"><h3>Challenge <small>（难在哪里）</small></h3><p>一次失败可能是策略错了，也可能只是网络偶尔超时。太早总结，会把偶然现象当成通用规律；继续试太久，又会浪费探索预算。RSI 不一定有人告诉它正确做法，需要它自己根据执行反馈辨别原因。</p></div>
 <div class="idea-step"><h3>现有工作 <small>（别人研究了什么）</small></h3><p><b>ActiveSaddler</b> 研究的是哪些失败模式更值得继续训练；<b>Trace2Skill</b> 研究的是怎样从多条执行轨迹提炼可复用 Skill。我们研究的是<strong>面对这一次失败，下一步试什么，什么时候证据够了可以开始总结</strong>。[[S16]][[S31]]</p></div>
 <div class="idea-step"><h3>Insight <small>（为何可解）</small></h3><p>不同失败原因，往往会对下一次尝试给出不同预测。<strong>一次只改变一个关键条件</strong>，就有可能排除错误解释。当继续探索已经很难提供新信息时，再停止并总结经验。关键不是失败越多越好，而是每次尝试能否帮助弄清原因。</p></div>
 <div class="idea-step"><h3>Design <small>（如何做）</small></h3><p>失败后先列出两三个可能原因，选择最能把它们区分开的安全小实验，例如同样条件重试或只改变一个 API 参数。持续记录支持和反对各原因的证据，足够确定再更新 Skill；证据不够时允许暂不总结。所有试验只在受控环境运行。</p>
 <div class="flow"><div><b>列出失败原因</b><small>策略错 / 工具故障 / 偶发</small></div><div><b>做辨别性尝试</b><small>只变一个关键条件</small></div><div><b>判断何时停止</b><small>证据是否足够</small></div><div><b>形成新 Skill</b><small>再到未见任务复验</small></div></div></div>
 <div class="idea-step"><h3>实验设计 <small>（怎么验证）</small></h3><p>在 API 异常、工具使用和代码执行任务上，比较<strong>失败后立即总结、固定重试 N 次、随机补充尝试、针对可能原因选试验并决定停止</strong>。匹配 Token、环境调用和总预算，混合可控故障与自然失败。主要比较写入错误规则的比例、未见场景的迁移、单位成本的学习收益；不把“多试几次自然多成功”误当成新机制。整个过程不需要外部教师告诉标准答案。</p></div>
 </div>'''),
 ("idea-5", "I5：十模型互教——什么时候交换舞伴，才能一起变强？", '''
 <div class="idea-focus"><span class="idea-axis">有没有新东西</span><span class="idea-axis">采不采得到</span><span class="idea-axis">吸收了会不会丢</span><p><b>一句话：</b>十个能力、专长各异的模型像一个学习班，每轮两两互教、各自更新，再交换搭档。我们想知道<strong>什么时候应继续和原伙伴学、什么时候应换人，才能让更多模型长期学到新本领，而不只是一起把眼前的题做对？</strong></p></div>
 <div class="idea-steps">
 <div class="idea-step"><h3>Challenge <small>（难在哪里）</small></h3><p>一直与同一模型交流，可能反复交换已经掌握的知识；总跟最强模型，又可能难以吸收它的解法，甚至让十个模型越来越相似。更重要的是，组队答对不代表离开伙伴后学会。不同轮次的交换顺序、知识互补和双方收益都可能影响长期增长。</p></div>
 <div class="idea-step"><h3>现有工作 <small>（别人研究了什么）</small></h3><p><b>NC 2019《Bridge ties》</b> 研究相同交流次数下，先跨圈还是先组内交流如何改变群体记忆；<b>NC 2026</b> 研究多代人机群体如何通过选择示范者传播新策略。<b>PopuLoRA</b> 已做模型群体出题与共同进化；<b>OPCoD</b> 已做双模型互教；<b>MACE</b> 已做合作伙伴选择；<b>HACE</b> 已做异构模型和 Agent 的相互进化。它们不是空白。[[E90]][[E93]][[S32]][[S33]][[S34]][[S90]]</p></div>
 <div class="idea-step"><h3>Insight <small>（为何可解）</small></h3><p>一个伙伴的价值，不在于他有多强，而在于双方交流后<strong>各自能独立学到多少以前不会的东西</strong>。有效的伙伴关系可能随能力和知识变化而变化：需要新方法时跨圈交流，需要消化时保持配对，双方都学不到新东西时再换。Nature 系列关于知识分布、网络结构与收益学习的发现支持研究动机，但未直接验证 LLM 的这种更新。[[E91]][[E92]][[E94]][[E95]]</p></div>
 <div class="idea-step"><h3>Design <small>（如何做）</small></h3><p>十个模型分成五对，分别交换验证过的正确和错误轨迹，双方使用<strong>相同且固定的更新器</strong>更新自己的 LoRA / Skill（首轮只固定一种更新面）。交流后撤除伙伴、清空临时上下文，在未见题上独立测试新能力和旧能力保持，再估计原配对继续交流与换伴的下一轮收益。在十节点伙伴网络里重配五对，而不是固定让最强模型当老师。</p><div class="flow"><div><b>十个独立模型</b><small>不同能力 × 不同专长</small></div><div><b>五对双向互教</b><small>同预算、同教学协议</small></div><div><b>撤伴独立考试</b><small>双方能力增益与保持</small></div><div><b>重选伙伴与顺序</b><small>边际学习收益决定留伴或换伴</small></div></div></div>
 <div class="idea-step"><h3>实验设计 <small>（怎么验证）</small></h3><p>先用 4 模型做全配对的学习收益测量，再扩展到 10 模型，比较<strong>固定伙伴、随机轮换、round-robin、固定最强教师、同级配对、跨专长配对、先跨组后巩固、PopuLoRA / MACE 风格匹配、学习收益驱动的动态换伴</strong>。各模型交流、参数更新和算力预算匹配，报告个人独立能力、全班净增益、旧能力保持、新解法发现与过早同质化。如果简单轮换已同样有效，就不单独提出复杂路由器。</p><p class="idea-side-note"><b>正交边界：</b>I5 只研究<strong>谁和谁学、何时换伴</strong>；I2 负责如何教学，I3 负责巩固，I6 研究失败轨迹的学习价值，I7 研究先试还是先学，I8 研究高置信错误的迁移。<a href="idea-i5.html">查看 Nature 证据、完整十模型实验与停止条件 →</a>。<a href="teaching.html">教学反馈诊断教师盲点</a>是历史支线，不与 I5 主线混作同一贡献。</p></div>
 </div>'''),
 ("orthogonal", "I6、I7 与 I8：一次只研究一个变量", '''
<div class="table-wrap"><table><thead><tr><th>Idea</th><th>改变什么</th><th>固定什么</th><th>决定性结果</th></tr></thead><tbody>
<tr><td><a href="idea-i6-failure-value.html">I6 · 失败轨迹价值</a></td><td>同题失败过程</td><td>模型检查点、错误终点、正确反馈、学习顺序、预算</td><td>不同轨迹产生的后续独立学习增益</td></tr>
<tr><td><a href="idea-i7-learning-order.html">I7 · 学习顺序</a></td><td>先尝试 / 先看正确示范</td><td>题目、示范内容、更新器与预算</td><td>撤掉教师后的独立能力、有效探索与多轮迁移</td></tr>
<tr><td><a href="i8.html">I8 · 规则级错误迁移</a></td><td>知识准备、错误规则覆盖范围和更新兼容性</td><td>对应的纠错/更新方法</td><td>哪些错误修复后能迁移到一整类题</td></tr>
</tbody></table></div>
<p><b>不要混成一篇：</b>I6 的核心证据是“相同错误终点，不同失败过程”；I8 的核心证据是“错误知识状态与跨题规则”的关系。I7 不以 I6/I8 的分类结果作为必需前提。旧版<a href="idea-i6.html">跨轮瓶颈切换方案</a>仅作为历史草案保留，不再占用当前 I6 编号。</p>
'''),
("idea-8", "I8：Hypercorrection——为什么改正一种错误能学会一类题？", '''
 <div class="idea-focus"><span class="idea-axis">信号对不对</span><span class="idea-axis">吸收了会不会丢</span><p><b>具体问题：</b>同样一道数学错题，一个模型得到正确反馈后只记住答案，另一个却能举一反三。纠正哪种错误值得投入下一轮学习预算？</p></div>
 <h3>Observable Phenomenon / Why</h3><p>Hypercorrection 的人类学习研究发现，高置信度错误经正确反馈后有时更容易被纠正；已有知识可能是重要解释。由此提出待验证的模型假设：前置知识是否充分、错误是否由影响多题的共同规则造成，可能共同决定一次纠错的跨题收益。[[E12]][[E13]][[E14]]</p>
 <h3>Challenge / Insight / Design</h3><p><b>Challenge：</b>置信度不等于学得会；修复原题不等于迁移；真实收益通常要在更新后才能观察。<b>Insight：</b>已有知识准备程度 × 规则影响范围 × 更新兼容性，可能解释实际收益差异。<b>Design：</b>学习前诊断知识与错误模式，固定纠错方式和训练预算，在独立模型副本上检验跨题真实收益。</p>
 <h3>别人研究的是……；我们研究的是……</h3><p><b>Self-Error-Instruct</b> 已按错误类型合成题目，并用 one-shot 示例帮助筛选数据；<b>LESS</b> 已用梯度影响选择训练数据。I8 研究的是当前错误怎样转化为真实持久的跨题学习，以及能否提前预测。[[S40]][[M10]]</p>
 <p><b>与 I6 的区别：</b>I8 研究哪些错误规则更有可迁移性；<a href="idea-i6-failure-value.html">I6</a> 尽量保持错误规则与最终答案一致，单独研究失败过程作为学习材料的作用。</p><div class="links"><a class="link-btn" href="i8.html">阅读 I8：现象、原因、完整实验与否定条件</a></div>
 '''),
 ("shared", "这些 Idea 如何证明真的用于 RSI？", '''
 <div class="table-wrap"><table><thead><tr><th>需要分开报告</th><th>最简单的检验办法</th></tr></thead><tbody>
 <tr><td>当前任务变好</td><td>协助、提示或多次尝试后的即时成功率；这是短期表现。</td></tr>
 <tr><td>我自己真的学会</td><td>只保留允许写入的 Skill / Memory / Harness / 权重；撤除教师、伙伴和临时上下文，在新任务上测独立能力。</td></tr>
 <tr><td>我越来越会学习</td><td>保留学到的“选帮助、选学法、选复习、选试验、选伙伴”策略，给新的学习者与新任务，测同预算下是否学得更快。</td></tr>
 </tbody></table></div>
 <p><b>共同对照：</b>同一学习器起点、相同训练/执行预算、固定外部验证器；报告新任务进步、旧任务保持、训练成本和多轮曲线。普通重试、固定规则、随机选择、通用 bandit 是必要基线。任务选择、训练数据和最终测试必须隔离。</p>
 <p><b>安全边界：</b>所有自修改先在受控沙箱中提议、测试、回滚；真实系统权限不随学习成功自动升级。Skill/Memory 写入保存来源与适用条件，拒绝把不稳定、污染或越权的经验固化。这里是协议要求，不是已完成的安全验证。</p>
 <p class="status">截至 2026-10-27：这些是有明确近邻的研究提案，不能声称“首次把教育学用于 RSI”；也不能因为已有相关组件，就断言上述更细化的问题已被解决。</p>
 ''')
 ]
}
