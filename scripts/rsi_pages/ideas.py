"""I1–I5 concrete learning ideas, current I6 failure trajectories, I7 learning order, I8 error-rule transfer.

The earlier bottleneck-switching proposal remains accessible as a historical draft.
Research hypotheses are separate from measured findings.
"""
PAGE = {
 "slug": "ideas",
 "title": "I1–I8：八个研究问题",
 "en": "I1–I8 · distinguish failure paths, learning order, and rule transfer",
 "lead": "八个想法统一按 Challenge、现有工作、Insight、Design、实验设计展开。I6 比较失败过程价值，I7 研究先试还是先学，I8 研究纠错后的跨题迁移；三个问题单独验证。",
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
 <a class="idea-board-card" href="#idea-6"><span class="idea-id">I6 · 失败学习价值</span><b>哪条失败更值得纠正？何时停下再回来？</b><small>固定纠错方式，比较失败的独立收益与继续尝试成本</small></a>
 <a class="idea-board-card" href="#idea-7"><span class="idea-id">I7 · 学习顺序</span><b>先看例题，还是先独立尝试？</b><small>固定教材与预算，研究独立能力、探索与多轮迁移</small></a>
 <a class="idea-board-card" href="#idea-8"><span class="idea-id">I8 · 错误学习迁移</span><b>改正哪个错误，能够学会一整类题？</b><small>Hypercorrection 与跨题净学习收益</small></a>
 </div>
 <p class="idea-outline-key"><b>I1–I8 统一阅读顺序：</b>Challenge（难在哪里） → 现有工作（别人做到了哪） → Insight（为何可解） → Design（如何做） → 实验设计（怎么验证）。每条研究方向先把科学问题和证据边界说清楚，再展开技术细节；I6–I8 均保留独立详情页。</p>
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
<div class="idea-focus"><span class="idea-axis">有没有新东西</span><span class="idea-axis">采不采得到</span><span class="idea-axis">吸收了会不会丢</span><p><b>一句话：</b>十个模型各自持续更新。我们不仅问谁更强，而是问谁教的东西我现在学得进、继续交流还有多少收益、何时换人才能共同成长。</p></div>
<div class="idea-steps">
<div class="idea-step"><h3>Challenge <small>（难在哪里）</small></h3><p>伙伴帮我答对，不等于自己学会；学完涨分，也可能只是同样预算自己练就能取得的进步。双方能力和已学知识不断变化，原先最好的搭档可能变得重复；换伴顺序的收益还可能只是普通课程效应。</p></div>
<div class="idea-step"><h3>现有工作 <small>（别人研究了什么）</small></h3><p><b>CORY</b> 已联合训练两个模型并交换角色；<b>PopuLoRA</b> 已做 LoRA 群体自博弈；<b>OPCoD</b> 已用同伴反馈进行双向自蒸馏；<b>CERA-MoA</b> 已联合更新路由与 Agent；<b>HACE</b> 已做异构互惠学习。动态伙伴选择也已有 AAMAS 2026 <b>SE Workshop</b> 前作，不能写成主会或首次提出。[[S200]][[S32]][[S33]][[S202]][[S90]][[S201]]</p><p>此前的 MACE 伙伴探索和 Nature 交流顺序研究继续作为相邻证据；它们不直接证明十模型权重学习收益。[[S34]][[E90]]</p></div>
<div class="idea-step"><h3>Insight <small>（为何可解）</small></h3><p>伙伴的价值应由<strong>双方撤伴后的表现，减去同预算自学后的表现</strong>衡量。对方独有的知识、我当前的可吸收性和过去接触过的内容，可能共同解释为何该留伴或换伴；这是待检验关系，不是固定强弱排名。</p></div>
<div class="idea-step"><h3>Design <small>（如何做）</small></h3><p>固定 OPCoD 式 LoRA 自蒸馏和反馈门控，正常每轮五对、双向教学。小规模受控试学得到有方向净增益；用同容量的带/不带历史收益预测器在十节点图中选配对，按边际收益与不确定性决定持续多久。缺乏可信增益时允许同预算自学。<strong>所有试探和回退成本计入总预算。</strong></p><div class="flow"><div><b>独立十模型</b><small>五规模 × 数学/代码</small></div><div><b>固定互教更新</b><small>只改变伙伴关系</small></div><div><b>相对自学测收益</b><small>撤伴、新题、保持</small></div><div><b>继续或重配</b><small>历史、预算与置信度</small></div></div></div>
<div class="idea-step"><h3>实验设计 <small>（怎么验证）</small></h3><p>先做四模型 6 配对，再开展十模型实验；比较固定伙伴、随机、round-robin、能力匹配、即时收益和独立净增益。顺序实验同时固定边集合、接触次数和预算，并加入<strong>相同材料重排、冻结教师、双方共同更新</strong>三层控制。主指标为个人独立能力、群体学习效率、旧能力保持与验证过的技能覆盖，不是投票成绩。</p><p class="idea-side-note">I5只研究谁与谁学、持续多久和伙伴顺序；不改变 I2 学法、I3 巩固、I6 轨迹、I7 先试/先学、I8 错误选择。<a href="idea-i5.html">完整方法、最近邻、公式和实验契约</a>；<a href="idea-i5.html#teaching-feedback">历史教学反馈支线</a>仍在唯一 I5 页面内。</p></div>
</div>'''),
 ("idea-6", "I6：失败学习价值——同样答错，哪条失败更值得学习？", '''
 <div class="idea-focus"><span class="idea-axis">信号对不对</span><span class="idea-axis">有没有新东西</span><span class="idea-axis">采不采得到</span><p><b>一句话：</b>同一个模型解同一道积分题，两次都给出相同的错误答案：一次直接套错公式，一次尝试了几个正确步骤却仍答错。<strong>用哪一次失败来学习，才能让以后更多新题做对？又该在什么时候停止重试、改天再学？</strong></p></div>
 <div class="idea-steps">
 <div class="idea-step"><h3>Challenge <small>（难在哪里）</small></h3><p>只看最终答案，两条失败都是零分；但错误过程中有没有正确子步骤、有没有暴露新原因，可能决定这次纠错能学到什么。<strong>失败轨迹更长、看起来更接近答案，也未必更值得训练</strong>。如果同一道题已连续失败，继续采样可能浪费预算；可现在学不会，不代表补过基础后仍学不会。</p></div>
 <div class="idea-step"><h3>现有工作 <small>（别人研究了什么）</small></h3><p><a href="https://aclanthology.org/2024.acl-long.45/" target="_blank" rel="noopener noreferrer"><b>Learn from Failure</b></a> 研究如何利用失败的定理证明轨迹；<b>SOAR</b> 根据学生实际进步生成值得学习的新题；<b>BEACON</b> 研究推理时何时停止继续采样；<b>Region of Proximal Learning</b> 研究人类何时离开当前学习材料。我们研究的是<strong>同题同样答错时，哪条失败过程在固定纠错后更能提高未来独立能力，以及何时停止收集这种失败</strong>，不是更换教学方式或提高当前 pass@k。[[S47]][[S48]][[E16]]</p></div>
 <div class="idea-step"><h3>Insight <small>（为何可解）</small></h3><p>失败过程比最终对错多提供一层信息：<strong>模型已经走对了哪几步、在哪个规则上反复走错、下一次失败是否仍会暴露新缺口</strong>。从相同模型出发，用相同正确反馈分别纠正不同失败，再比较未见题的独立进步，就可以为每条失败估计真实学习价值。如果新失败已很难增加收益，就应比较纠正已有失败、换题或暂缓后重访。</p></div>
 <div class="idea-step"><h3>Design <small>（如何做）</small></h3><p>从同一模型检查点在同一道题上采集多条自然失败，尽量匹配最终错误、轨迹长度与反馈信息；随机指定其中一条作为学习材料。<strong>固定正确答案、教学顺序、更新器和训练预算</strong>，分叉更新并在撤掉提示后测新题。先用真实迁移增益给失败定价，再训练只看纠错前信息的轻量预测器；比较继续收集、纠正已有、换题、暂缓重访的下一次投入。</p>
 <div class="flow"><div><b>同题收集不同失败</b><small>同版模型，结果尽量一致</small></div><div><b>固定纠错方法</b><small>同反馈、同 LoRA/Skill 预算</small></div><div><b>新题独立后测</b><small>迁移、旧能力回归、成本</small></div><div><b>选失败与停止时机</b><small>继续 / 换题 / 暂缓重访</small></div></div></div>
 <div class="idea-step"><h3>实验设计 <small>（怎么验证）</small></h3><p>先做同题配对实验，比较<strong>只看正确解法、随机失败、最长失败、最接近正确的失败、按置信度选、预测学习增益选</strong>；模型快照、教师反馈和总 token/FLOPs 匹配。报告无提示未见题提升、旧能力损失与失败价值的跨题稳定性。再比较固定重试 K 次、简单学习进展阈值、收益驱动停止/暂缓，并事先约定重访条件。如果差异只来自更长轨迹或更多训练，或早停没超过简单阈值，就缩小主张，不另加复杂停止模块。[[M12]][[S45]]</p><p class="idea-side-note"><b>正交边界：</b>I6 固定<strong>先试还是先学</strong>（交给 <a href="#idea-7">I7</a>）和<strong>纠错规则类型</strong>（交给 <a href="#idea-8">I8</a>），只研究失败中间过程的增量价值与是否继续投入。<a href="idea-i6-failure-value.html">查看同题配对、停学与重访的完整实验 →</a></p></div>
 </div>'''),
 ("idea-7", "I7：学习顺序——先看例题，还是先独立尝试？", '''
 <div class="idea-focus"><span class="idea-axis">采不采得到</span><span class="idea-axis">吸收了会不会丢</span><p><b>一句话：</b>学同一道多步骤数学题，模型 A 先看完整解法再练习，模型 B 先独立尝试、失败后再看同一解法。<strong>学完撤掉例题，谁更会解新题？这种优势会不会随着模型变强而反过来？</strong></p></div>
 <div class="idea-steps">
 <div class="idea-step"><h3>Challenge <small>（难在哪里）</small></h3><p>看过示范后立即答对，可能只是照着步骤模仿；先做再学的提升，也可能只是比另一组多练了一次。更难的是，两种顺序可能让模型探索到不同的<strong>正确解题路径</strong>，而当前分数却差不多。只比较一次做题正确率，无法判断模型有没有在后续更新中真正学会、是否丢掉了原有的解法。</p></div>
 <div class="idea-step"><h3>现有工作 <small>（别人研究了什么）</small></h3><p><a href="https://doi.org/10.3102/00346543211019105" target="_blank" rel="noopener noreferrer"><b>Sinha &amp; Kapur（2021）</b></a> 汇总 53 项人类教育研究，发现某些概念知识和迁移任务中“先解题后教学”有优势，但程序性知识未显示同样的总体差异；<a href="https://ijcai.org/proceedings/2015/614" target="_blank" rel="noopener noreferrer"><b>Najar 等（2015）</b></a> 已研究按学生状态选择示范或练习；<a href="https://doi.org/10.1007/s10648-025-09993-3" target="_blank" rel="noopener noreferrer"><b>He 等（2025）</b></a> 还观察到不同人群的顺序优势可能相反。<strong>我们不是首次比较教学顺序</strong>，而是研究 LLM 经过相同预算的持久更新后，独立解题能力、可采样的正确解法和多轮迁移如何受顺序影响。</p></div>
 <div class="idea-step"><h3>Insight <small>（为何可解）</small></h3><p>两组都能看到同一份正确示范，但<strong>先试的人在看到答案前，已经走过自己的候选路径</strong>；先看的人可能更快掌握标准步骤，却可能更依赖示范。这两种影响不能靠眼前一道题判断。只改变学习先后，撤掉教师和临时上下文后再测新题，就能判断顺序究竟改变了独立能力，还是只改变了即时模仿。</p></div>
 <div class="idea-step"><h3>Design <small>（如何做）</small></h3><p>在同一个模型检查点、同一组题目上随机分成两支：<strong>A 先看示范再练习，B 先独立尝试再看相同示范</strong>。控制示范内容、尝试次数、采样配置、教师调用、训练 token 和 LoRA/Skill 更新步数。更新完清空示范上下文，在未见题上独立测试。只有先证明不同任务或模型阶段的最佳顺序确实会变化，才考虑用先前历史训练顺序选择器。</p>
 <div class="flow"><div><b>同一检查点分两组</b><small>教师、题目、预算一致</small></div><div><b>只交换先后次序</b><small>先学再做 / 先做再学</small></div><div><b>撤掉示范独立考试</b><small>新题正确率与正确解法</small></div><div><b>多轮更新后复测</b><small>顺序优势是否改变</small></div></div></div>
 <div class="idea-step"><h3>实验设计 <small>（怎么验证）</small></h3><p>先选一类多步骤数学题，比较<strong>固定先学、固定先试、匹配次数的额外练习、无示范基线</strong>；后续只有在发现稳定顺序异质性时，才增加按历史能力选择和 contextual bandit 对照。用同预算的无提示 pass@1、固定 k 下的 pass@k、<strong>不同且正确的解法数量</strong>、旧能力保持及跨多轮更新的迁移作为指标。按知识点聚类统计，不按同题多次采样扩大样本量。如果优势只是练习次数更多或无效答案更多，就不能说顺序提高了探索与自我改进。</p><p class="idea-side-note"><b>正交边界：</b>I7 只改变<strong>尝试与示范的顺序</strong>；<a href="#idea-6">I6</a> 在顺序固定时选择哪条失败过程，<a href="#idea-8">I8</a> 在纠错方式固定时研究哪类错误有跨题迁移价值。<a href="idea-i7-learning-order.html">查看人类教学的前作边界、两顺序协议与长期对照 →</a></p></div>
 </div>'''),
 ("idea-8", "I8：错误学习迁移——为什么改正一种错误能学会一类题？", '''
 <div class="idea-focus"><span class="idea-axis">信号对不对</span><span class="idea-axis">吸收了会不会丢</span><span class="idea-axis">安全</span><p><b>一句话：</b>两个模型都把一道积分题做错。一个看完正确答案只会重做原题；另一个却学会同一公式，连几十道新题也能做。<strong>纠正哪个错误更可能举一反三？能否在真正训练前判断？</strong></p></div>
 <div class="idea-steps">
 <div class="idea-step"><h3>Challenge <small>（难在哪里）</small></h3><p>模型很自信地答错，不代表它缺的知识少，也不代表纠正后进步一定大。<strong>当前题答对、同模板变体答对、真正掌握一条规则</strong>是不同的结果。每个错题都完整训练一遍才能知道收益，成本太高；直接按难度、置信度或损失排序，又可能选中只会记住答案、却不会迁移的错误。</p></div>
 <div class="idea-step"><h3>现有工作 <small>（别人研究了什么）</small></h3><p><b>Hypercorrection</b> 与 <b>Nature Communications 2018</b> 的人类学习研究发现，已有信念与可信反馈的冲突可能影响纠错记忆，但不等于 LLM 已能跨题学习。<b>Self-Error-Instruct</b> 已按模型错误类型生成并筛选训练数据；<b>LESS</b> 和 <b>DATAPROPHET</b> 已研究训练前预测数据价值；<b>RULE-EDIT</b> 已区分规则文本修复与实例迁移。我们研究的是<strong>这个模型当前犯的某个错误，在固定纠错预算后究竟能让多少未见同规则题变好</strong>，而不是首次使用错题或首次预测训练价值。[[E12]][[E18]][[S40]][[M10]][[M13]][[S41]]</p></div>
 <div class="idea-step"><h3>Insight <small>（为何可解）</small></h3><p>一个错误有多值得纠正，至少可能受三个条件影响：<strong>模型是否已有理解正确规则的基础、这条错误规则影响多少道不同题、当前更新方式能否真正改变规则的使用</strong>。例如，遗漏同一积分公式分母的模型可能只差关键一步；但若连基本运算都不会，直接给公式未必能被吸收。置信度或强烈的“原来我错了”可以作为候选信号，不能直接等于真实学习收益。</p></div>
 <div class="idea-step"><h3>Design <small>（如何做）</small></h3><p>先用独立前置知识题、同规则变体和稳定性探针，诊断<strong>知识准备、规则影响范围与更新兼容性</strong>；正确答案与规则由独立验证器核实。然后从相同模型检查点分叉，用相同教师反馈与固定 LoRA/Skill 更新预算纠正不同错误。训练前估计可能的跨题收益，训练后撤掉例题与提示，分别测原题、异结构同规则新题、其他规则和旧能力损失。</p>
 <div class="flow"><div><b>确认错误与规则</b><small>先核实反馈正确</small></div><div><b>学习前诊断</b><small>前置知识 / 规则范围</small></div><div><b>固定预算纠错</b><small>同教师、同更新器</small></div><div><b>独立测跨题净收益</b><small>新题迁移 / 遗忘 / 成本</small></div></div></div>
 <div class="idea-step"><h3>实验设计 <small>（怎么验证）</small></h3><p>构造<strong>前置知识高/低 × 错误规则影响范围大/小</strong>的配对数学错题，匹配难度、置信度、正确反馈和训练预算；每个候选从同一模型快照独立更新。比较<strong>随机、最难优先、高置信度优先、稳定错误优先、Self-Error-Instruct 的 one-shot 信号、LESS 梯度信号、DATAPROPHET 式价值特征、I8 的规则诊断</strong>。主指标是训练前预测与真实未见题净增益的对应关系，以及同预算选错题的最终收益；另外报告旧能力退化和诊断成本。如果优势只出现在原题、近似改写，或在匹配知识状态后消失，就不能宣称发现了规则级迁移机制。</p><p class="idea-side-note"><b>正交边界：</b>I8 固定纠错方式，只研究<strong>哪个错误规则在当前模型上更有迁移价值</strong>；<a href="#idea-6">I6</a> 在同题同错误终点比较失败中间过程，<a href="#idea-7">I7</a> 只改教学顺序。<a href="i8.html">查看 Hypercorrection 原始证据、最近邻矩阵和完整受控实验 →</a>。目前<strong>没有 I8 的实际训练结果</strong>。</p></div>
 </div>'''),
 ("orthogonal", "I6、I7 与 I8：一次只研究一个变量", '''
<div class="table-wrap"><table><thead><tr><th>Idea</th><th>改变什么</th><th>固定什么</th><th>决定性结果</th></tr></thead><tbody>
<tr><td><a href="idea-i6-failure-value.html">I6 · 失败轨迹价值</a></td><td>同题失败过程</td><td>模型检查点、错误终点、正确反馈、学习顺序、预算</td><td>不同轨迹产生的后续独立学习增益</td></tr>
<tr><td><a href="idea-i7-learning-order.html">I7 · 学习顺序</a></td><td>先尝试 / 先看正确示范</td><td>题目、示范内容、更新器与预算</td><td>撤掉教师后的独立能力、有效探索与多轮迁移</td></tr>
<tr><td><a href="i8.html">I8 · 规则级错误迁移</a></td><td>知识准备、错误规则覆盖范围和更新兼容性</td><td>对应的纠错/更新方法</td><td>哪些错误修复后能迁移到一整类题</td></tr>
</tbody></table></div>
<p><b>不要混成一篇：</b>I6 的核心证据是“相同错误终点，不同失败过程”；I8 的核心证据是“错误知识状态与跨题规则”的关系。I7 不以 I6/I8 的分类结果作为必需前提。旧版<a href="idea-i6.html">跨轮瓶颈切换方案</a>仅作为历史草案保留，不再占用当前 I6 编号。</p>
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
