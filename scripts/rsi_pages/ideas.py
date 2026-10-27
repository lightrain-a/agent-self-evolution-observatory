"""I1–I5: concrete education-inspired RSI hypotheses; I6 is a separate cross-round controller.

These are research candidates, not verified experimental findings or novelty claims.
Paper comparisons are limited to the linked abstracts/method descriptions as dated.
"""
PAGE = {
 "slug": "ideas",
 "title": "I1–I6 与 I8：相互独立的 RSI 研究方向",
 "en": "I1–I6 plus I8 · mechanisms, bottlenecks and transferable error learning",
 "lead": "I1–I5 研究具体学习机制，I6 研究跨轮瓶颈切换；I8 独立研究哪些错误能产生真实跨题迁移。先验证现象与原因，而非拼接多个模块。",
 "updated": "2026-10-27",
 "sections": [
 ("portfolio", "研究方向，一眼看懂",  '''
 <p>共同目标：<strong>让 Agent 不只是从执行结果里积累经验，还能随着自身能力变化，学会选择更好的自我改进方式。</strong>I1–I5 研究各自的学习机制；I6 研究跨轮瓶颈阶段的转换判断，不能替代其他五项。</p>
 <div class="idea-board">
 <a class="idea-board-card" href="#idea-1"><span class="idea-id">I1 · 脚手架学习法</span><b>哪些该自己学会，哪些用时再查？</b><small>辅助使用与内化的取舍</small></a>
 <a class="idea-board-card" href="#idea-2"><span class="idea-id">I2 · 因材施教</span><b>同样犯错，为什么学习方法不同？</b><small>根据真实学习反应选方法</small></a>
 <a class="idea-board-card" href="#idea-3"><span class="idea-id">I3 · 温故知新</span><b>新方法有用，却和旧方法冲突怎么办？</b><small>复习并解决适用条件冲突</small></a>
 <a class="idea-board-card" href="#idea-4"><span class="idea-id">I4 · 生产性失败</span><b>失败一次就总结，还是再试几次？</b><small>判断何时证据足够更新 Skill</small></a>
 <a class="idea-board-card" href="#idea-5"><span class="idea-id">I5 · 费曼学习法</span><b>和谁一起学，自己进步最快？</b><small>伙伴选择随能力一起演化</small></a>
 <a class="idea-board-card" href="idea-i6.html"><span class="idea-id">I6 · 跨轮瓶颈切换</span><b>模型停滞后，究竟该换哪一类学习机制？</b><small>诊断知识、搜索、选择、吸收中的主导瓶颈迁移</small></a>
 <a class="idea-board-card" href="i8.html"><span class="idea-id">I8 · 错误学习迁移</span><b>改正哪个错误，能够学会一整类题？</b><small>Hypercorrection 与跨题净学习收益</small></a>
 </div>
 <p class="status">状态：I1–I6 与 I8 已归档；相关工作存在交集；各方案尚无本站的受控实测结果，不能宣称首次或已验证。</p>
 <p>本站将它们挂到 RSI 的四个问题与安全轴下：<b>信号对不对 / 有没有新东西 / 采不采得到 / 吸收了会不会丢 / 安全。</b>这些标签表示要研究的环节，不表示问题已经解决。详见 <a href="reading-cards.html">论文阅读卡片</a>。</p>
 '''),
 ("idea-1", "I1：脚手架学习法——哪些该自己学会，哪些用时再查？", '''
 <div class="idea-focus"><span class="idea-axis">采不采得到</span><span class="idea-axis">吸收了会不会丢</span><p><b>最直观的问题：</b>调试方法最好自己掌握；频繁变化的 API 细节可能用时再查就行。Agent 能不能自己学会这种取舍，并随能力与环境变化调整？</p></div>
 <h3>别人研究的是……</h3>
 <p><b>R²Orch</b> 研究什么时候可以撤掉已被内部能力替代的 Skill，并在自博弈中推动能力内化；<b>PATS</b> 把 Skill 当作训练时的临时支架，能力变强后修订或移除冗余提示。它们都不只是“减少提示词”，而是 I1 必须正面比较的工作。[[S26]][[S27]]</p>
 <h3>我们想研究的是……</h3>
 <p><strong>同一份辅助经验，什么时候该学进自身，什么时候该留在外部、按需读取？</strong>例如稳定的排查步骤值得固化，易变的接口规则可能应保留检索入口。判断取舍的依据不能只看“有帮助时成功了没有”，还要看撤除帮助之后能不能在新任务上独立完成、环境改变后会不会出错。</p>
 <p><b>难点：</b>一次撤除成功，可能只是恰好不需要那个 Skill；完全不依赖 Skill 也不等于能力提高。</p>
 <p><b>可利用的观察：</b>辅助对当前完成任务有用，不代表把它写进长期能力最有用；知识稳定性、已有基础和后续更新都会改变最佳选择。</p>
 <div class="flow"><div><b>列出辅助经验</b><small>稳定规则 / 易变知识 / 临时提示</small></div><div><b>比较三种做法</b><small>内化、外置检索、渐隐</small></div><div><b>独立执行新任务</b><small>清空辅助与任务上下文</small></div><div><b>根据收益调整选择</b><small>新旧任务与成本一起算</small></div></div>
 <h3>最小验证</h3><p>同一 Agent、相同训练和工具预算，将稳定操作经验与会变动的 API 规则分开，比较<strong>全部内化 / 全部外置 / 固定渐隐 / 自适应取舍</strong>。看撤除后的独立正确率、环境变更后的退化、保留成本。再和 R²Orch/PATS 适配版比较。如果一律内化或简单撤除就同样好，我们不应硬说路由策略有新价值。</p>
 '''),
 ("idea-2", "I2：因材施教——同样犯错，为什么学习方法不同？", '''
 <div class="idea-focus"><span class="idea-axis">信号对不对</span><span class="idea-axis">采不采得到</span><p><b>最直观的问题：</b>两个 Agent 都不会修一个 Bug，一个看一次示范就学会了，另一个要对比几次失败才理解。只看“错在哪里”，够不够决定下一轮该怎么学？</p></div>
 <h3>别人研究的是……</h3>
 <p><b>RSIFlow</b> 根据执行瓶颈选择该改模型、Harness 还是任务产物，并让负责调度的 Meta-Agent 进化；<b>MetaSkill-Evolve</b> 让任务 Skill 与修改 Skill 的元流程在不同时间尺度上改进。它们已经覆盖“动态自我改进”这个大概念。[[S28]][[S06]]</p>
 <h3>我们想研究的是……</h3>
 <p><strong>即使失败类型相同、要更新的对象也相同，Agent 是否仍然有不同的最佳学习方法？</strong>有人更适合看示范，有人更适合自主重试，也有人需要比较正确与错误路径。能不能先花少量预算“试学”一轮，再选能让自己下一轮独立进步最多的方法？能力变了之后，也重新判断。</p>
 <p><b>难点：</b>一次试学效果好未必意味着长期收益好；试学本身花费预算，而且不同 Agent 的基础能力不一致。</p>
 <p><b>可利用的观察：</b>同样的错误标签不能完整预测对不同教学动作的反应；少量有控制的学习尝试可能比静态分类更有信息。</p>
 <div class="flow"><div><b>锁定同类失败</b><small>同一更新对象</small></div><div><b>少量试学</b><small>示范 / 反例 / 独立练习</small></div><div><b>观察独立进步</b><small>不看当前答题小分</small></div><div><b>下轮选更合适的方式</b><small>进化后重估</small></div></div>
 <h3>最小验证</h3><p>从同一快照分叉三种学习处理，先固定“修改 Skill”而不是混入更新表面。让两个当前分数接近的 Agent 学相同类型任务，比较<strong>固定方法 / 错误类型路由 / 通用 bandit / 试学后选择</strong>在未见任务上的等预算进步。再检验能力进化后原来最好的方法是否改变。若简单 bandit 就足够，保留现象但不夸大复杂模型的贡献。</p>
 '''),
 ("idea-3", "I3：温故知新——新方法有用，却和旧方法冲突怎么办？", '''
 <div class="idea-focus"><span class="idea-axis">吸收了会不会丢</span><span class="idea-axis">安全</span><p><b>最直观的问题：</b>Agent 学会更快的处理流程，却把另一种场景下原本正确的规则覆盖了。我们是否只能回滚这次更新？</p></div>
 <h3>别人研究的是……</h3>
 <p><b>Harness Continual Learning（HCL）</b> 在提交 Harness 更新前，同时检查新任务进步、历史能力保持和有效性；<b>SkillBoost</b> 用回归约束筛掉破坏旧能力的修改。它们解决了不少“新改动伤害旧任务”的问题。[[S29]][[S30]]</p>
 <h3>我们想研究的是……</h3>
 <p><strong>当新旧 Skill 各自都有效，却会在不同条件下互相干扰时，Agent 能否通过针对性复习把两者都保留下来？</strong>不是每次全部重练，也不只是发现回归就拒绝更新，而是学清楚“这个规则什么时候用、什么时候不能用”。</p>
 <p><b>难点：</b>旧能力退化可能来自检索冲突、适用范围模糊，也可能确实是参数遗忘。需要定位干扰来源，而不是一律新增旧题。</p>
 <p><b>可利用的观察：</b>不少负迁移是两个局部有效策略之间的错误选择；练习条件边界可能比简单重复旧样本更有用。</p>
 <div class="flow"><div><b>检测新旧冲突</b><small>同一新版本 / 旧版本对照</small></div><div><b>找冲突条件</b><small>工具状态、触发与上下文</small></div><div><b>定向复习</b><small>边界任务，不是所有旧题</small></div><div><b>合并保留</b><small>旧、新和组合任务都通过</small></div></div>
 <h3>最小验证</h3><p>制作两组分别成功、混合却容易互相干扰的 Skill，加入自然更新中的同类案例。比较<strong>发现退化即回滚 / 均匀重放 / MIR 风格重放 / 针对冲突条件复习</strong>。固定复习调用数与存储预算，测试旧任务保持、新任务收益及两者组合。若只是因为多存了规则才进步，不属于新机制。</p>
 '''),
 ("idea-4", "I4：生产性失败——失败一次就总结，还是再试几次？", '''
 <div class="idea-focus"><span class="idea-axis">信号对不对</span><span class="idea-axis">有没有新东西</span><span class="idea-axis">采不采得到</span><p><b>最直观的问题：</b>API 超时一次，不能马上写进长期 Skill：“这个工具不可靠，以后别用”。Agent 怎么知道自己真的找到了通用规律，而不是遇到了偶然故障？</p></div>
 <h3>别人研究的是……</h3>
 <p><b>ActiveSaddler</b> 研究应该继续优化哪些失败模式；<b>Trace2Skill</b> 研究从很多执行轨迹中提炼统一、可迁移的 Skill。失败选择与跨轨迹总结并不是空白。[[S16]][[S31]]</p>
 <h3>我们想研究的是……</h3>
 <p><strong>对一次失败，应该马上形成经验，还是继续做能辨别原因的尝试？又该在哪一步停下来，认定证据足以修改 Skill？</strong>例如先复现超时，再改变请求大小或重试条件，区分 API 规则错误、环境偶发故障和策略错误。</p>
 <p><b>难点：</b>多试几次自然可能多成功，优势未必来自更好地理解失败。不能让训练时见到的测试答案泄漏给更新器。</p>
 <p><b>可利用的观察：</b>最值得学习的失败不一定最严重；能区分多个原因的下一次试验，可能比立刻反思一句话更有价值。</p>
 <div class="flow"><div><b>遇到失败</b><small>先列几个可检验的原因</small></div><div><b>选择下一次试验</b><small>最能区分解释</small></div><div><b>决定继续或归纳</b><small>证据是否稳定</small></div><div><b>更新 Skill 并外测</b><small>新任务、旧任务均验证</small></div></div>
 <h3>最小验证</h3><p>固定失败家族与执行预算，比较<strong>失败即更新 / 固定多次重试 / 随机补充试验 / 按争议原因选下一次试验并决定停止</strong>。指标是写入错误规则的比例、未见环境的迁移与最终改进效率，不是“试的次数越多越好”。整个过程可使用沙箱执行反馈，不需要外部教师告诉标准答案。</p>
 '''),
 ("idea-5", "I5：费曼学习法——和谁一起学，自己进步最快？", '''
 <div class="idea-focus"><span class="idea-axis">有没有新东西</span><span class="idea-axis">采不采得到</span><span class="idea-axis">吸收了会不会丢</span><p><b>最直观的问题：</b>同样让我和别的模型交流，最强的模型不一定最能帮助我成长；能力提高后，原来最好的伙伴可能也不再适合。</p></div>
 <h3>别人研究的是……</h3>
 <p><b>PopuLoRA</b> 研究在共同进化的教师与解题者群体中，谁给谁出题更有学习挑战；<b>OPCoD</b> 研究两模型互相教学时，什么时候应该交换和采纳同伴反馈；<b>MACE（Multi-Agent Contextual Exploration）</b> 研究怎样探索和选择协作伙伴，以改善当前交互任务和探索表现。它们各自涉及配对、反馈或伙伴探索，但衡量目标与我们不完全一样。[[S32]][[S33]][[S34]]</p>
 <h3>我们想研究的是……</h3>
 <p><strong>谁能使我在交流结束后，自己做新任务时进步最多？这种最佳伙伴会不会随着我自己的能力变化而改变？</strong>不只比较参数大小，还看任务互补、对方擅长什么、我能否理解并吸收它的经验。也可以研究我教别人后是否反过来变强。</p>
 <p><b>难点：</b>伙伴可能直接帮我把当前题做对，但我并没有学会。必须撤走伙伴、清空对话，并比较自身新旧版本的独立表现。</p>
 <p><b>可利用的观察：</b>当前回答受益最大的人，未必是下次让我进步最多的人；最合适的差距可能随学习阶段变化。</p>
 <div class="flow"><div><b>能力不同的伙伴池</b><small>规模、领域、强弱互补</small></div><div><b>受控教学交流</b><small>按相同时间和预算</small></div><div><b>我自己的持久更新</b><small>参数、Skill 或 Harness</small></div><div><b>伙伴退出后测试</b><small>新任务进步决定下轮选谁</small></div></div>
 <h3>最小验证</h3><p>从三种能力档位的若干模型开始，控制教师/学生方向、任务、教学 token 和训练预算，比较<strong>随机匹配 / 同级匹配 / 永远找最强者 / PopuLoRA 式能力匹配 / MACE 式当前交互收益匹配 / 以独立学习增益为目标的选择</strong>。连续多轮重选伙伴，记录最佳伙伴的变化、下轮独立成功率和旧能力退化。进一步做“只获得答案、不更新自身”和“更新后撤除伙伴”对照，排除只是在组队解题。</p>
 <div class="note">已有 <a href="teaching.html">教学反馈诊断教师盲点的 I5 早期技术方案</a>独立保留，属于相邻支线：它研究“学生反馈暴露教师哪类缺陷”；本页 I5 主线研究“当前该与谁学，能让自己下一轮变强”。两者不能混成同一项已验证成果。</div>
 '''),
 ("idea-8", "I8：Hypercorrection——为什么改正一种错误能学会一类题？", '''
 <div class="idea-focus"><span class="idea-axis">信号对不对</span><span class="idea-axis">吸收了会不会丢</span><p><b>具体问题：</b>同样一道数学错题，一个模型得到正确反馈后只记住答案，另一个却能举一反三。纠正哪种错误值得投入下一轮学习预算？</p></div>
 <h3>Observable Phenomenon / Why</h3><p>Hypercorrection 的人类学习研究发现，高置信度错误经正确反馈后有时更容易被纠正；已有知识可能是重要解释。由此提出待验证的模型假设：前置知识是否充分、错误是否由影响多题的共同规则造成，可能共同决定一次纠错的跨题收益。[[E12]][[E13]][[E14]]</p>
 <h3>Challenge / Insight / Design</h3><p><b>Challenge：</b>置信度不等于学得会；修复原题不等于迁移；真实收益通常要在更新后才能观察。<b>Insight：</b>已有知识准备程度 × 规则影响范围 × 更新兼容性，可能解释实际收益差异。<b>Design：</b>学习前诊断知识与错误模式，固定纠错方式和训练预算，在独立模型副本上检验跨题真实收益。</p>
 <h3>别人研究的是……；我们研究的是……</h3><p><b>Self-Error-Instruct</b> 已按错误类型合成题目，并用 one-shot 示例帮助筛选数据；<b>LESS</b> 已用梯度影响选择训练数据。I8 研究的是当前错误怎样转化为真实持久的跨题学习，以及能否提前预测。[[S40]][[M10]]</p>
 <div class="links"><a class="link-btn" href="i8.html">阅读 I8：现象、原因、完整实验与否定条件</a></div>
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
