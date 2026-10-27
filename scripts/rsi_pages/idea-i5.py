"""I5 · rotating study partners / population co-improvement.

This is a research proposal, not measured RSI performance.
Unlike I2/I6, pairing and contact order are the independent variables;
actual within-pair teaching and model update mechanisms stay fixed.
"""
PAGE = {
 "slug": "idea-i5",
 "title": "I5：十模型互教——什么时候换舞伴，才能一起变强？",
 "en": "Learning-Gain-Driven Partner Rewiring for Population Co-Improvement",
 "lead": "把十个能力、专长不同的模型放进同一个学习班：每轮两两互教，各自独立更新，再重新分配伙伴。研究的不是谁能帮我做对眼前的题，而是怎样安排同伴关系，让整个班级长期获得新能力。",
 "updated": "2026-10-27",
 "sections": [
 ("scene", "Scene：十个模型像一个不断换学习搭档的班级", '''
 <p class="thesis"><b>一句话：</b>十个模型各有所长。固定搭档容易反复交换已经熟悉的东西；永远追随最强模型，又可能让大家学成一个样子。<strong>能不能随着每个人的能力变化重新排座位，让更多模型在伙伴退出后仍能独立进步？</strong></p>
 <p>设想班里有数学强、代码强、逻辑证明强、复杂工具操作强的同学。第一周，数学强的和代码强的互相教；第二周，有人已经补齐基础，原伙伴的帮助开始变少，就与另一组同学交换；第三周，新学会方法的人可以反过来教以前比自己强的同学。这里<strong>没有一位永远最强的固定教师</strong>。</p>
 <p>教育学上，这更接近<strong>轮换同伴学习、互惠同伴辅导（reciprocal peer tutoring）、拼图式合作学习（Jigsaw）</strong>，而不是“走读生”制度。Jigsaw 的学生先到专家组学习，再回原组互教；但本 I5 进一步研究哪一轮应该更换伙伴，以及双方发生持久学习后的网络如何再调整。[[E97]]</p>
 <div class="idea-focus"><span class="idea-axis">有没有新东西</span><span class="idea-axis">采不采得到</span><span class="idea-axis">吸收了会不会丢</span><p>这里的十个模型是十个<strong>拥有各自持久状态</strong>的学习者，不是一次推理时的十个聊天角色，也不是十票投票后选最好答案。首版可用固定底座的独立 LoRA 作为不同学习者，再用跨规模与跨模型家族复核。</p></div>
 '''),
 ("papers", "Related Work：Nature 系列已经发现了哪些群体机制？", '''
 <div class="table-wrap"><table><thead><tr><th>论文</th><th>别人研究的是……</th><th>对 I5 的可验证启发</th></tr></thead><tbody>
 <tr><td><b>Bridge ties bind collective memories</b>，Nature Communications 2019 [[E90]]</td><td>16 人网络、每人 4 次依次与不同伙伴交流；控制交流次数，只变更先跨组还是先组内。</td><td>配对的<strong>时间顺序</strong>可能影响知识先扩散还是先巩固；但它测的是群体记忆，主群体收敛差异统计上较边缘，不能直接证明模型训练有效。</td></tr>
 <tr><td><b>Clustering knowledge and dispersing abilities</b>，Nature Communications 2019 [[E91]]</td><td>在群体求解的计算模型中分别改变知识与能力在网络上的分布。</td><td><strong>能力差距</strong>与<strong>专长互补</strong>要分开建模，参数规模不是学习互补性的代理。</td></tr>
 <tr><td><b>Modularity and composite diversity</b>，Nature Communications 2021 [[E92]]</td><td>真实在线信息检索/预测实验，研究成员多样性、分组模块化和群体规模的交互。</td><td>既不能让信息长期困在小圈子，也不应假设全连接最好；要监测误差相关性和独立收益。</td></tr>
 <tr><td><b>Propagation and preservation of AI-discovered strategies</b>，Nature Communications 2026 [[E93]]</td><td>多代人类/AI 实验，按表现选上一代示范者，检验超出原学习者发现范围的策略能否被学习、传播和保留。</td><td>好老师不只要“会”，还要能传；但论文不是<strong>同一代十个持续更新模型的双向配对</strong>。</td></tr>
 <tr><td><b>Feature-based reward learning shapes human social learning</b>，Nature Human Behaviour 2025 [[E94]]</td><td>6 项实验、1,941 人，表明社会学习策略可以随历史收益而调整。</td><td>不必写死“找最强/找相似的人”，可从自身真正的学习收益更新选伴规则。</td></tr>
 <tr><td><b>Copy or collaborate?</b>，npj Complexity 2025 [[E95]]</td><td>计算模型将模仿强者与组合专长合作分开；群体平均表现与最优解探索存在不同收益。</td><td>配对不应只传播现成答案，还要留出发现新解法的机会；“先协作后复制”是强基线而不是我们的首创。</td></tr>
 <tr><td><b>Payoff selectivity drives collective intelligence</b>，Nature Communications 2026 [[E96]]</td><td>621 人动态资源追踪实验中，能看到他人收益时，群体更容易适应性调整信息流。</td><td>伙伴筛选应观察可信的收益信号，但该论文评估的是合作表现，并未证实权重更新后的独立学习。</td></tr>
 </tbody></table></div>
 <p>这些工作共同提示三个变量：<strong>接触谁、先后顺序、信息在群体中如何传播</strong>。NC 并没有直接给出“十模型长程参数共进化”的现成算法；以上是可迁移的机制证据，而不是 I5 的实验证明。</p>
 '''),
 ("collisions", "最接近的 LLM 工作：必须承认已经做到了哪里", '''
 <div class="table-wrap"><table><thead><tr><th>工作</th><th>已经覆盖</th><th>I5 不同于它的地方</th></tr></thead><tbody>
 <tr><td><b>PopuLoRA</b>（2026） [[S32]]</td><td>多个教师/学生 LoRA 群体、生成题目、自博弈、匹配与交叉评估；已经是群体共同演化。</td><td>I5 研究<strong>双向知识交换之后的独立能力净增益</strong>怎样决定下轮伙伴网络，而不是只按题目挑战与求解效果联结。</td></tr>
 <tr><td><b>OPCoD</b>（2026） [[S33]]</td><td>两个专长互补的模型多轮互教，双方参数持续更新，按可靠性决定何时给反馈。</td><td>I5 研究从固定双人互教到<strong>多人网络重新配对</strong>，并将换伴时机和群体停滞作为对象；双向反馈机制本身不是首创。</td></tr>
 <tr><td><b>MACE</b>（2026） [[S34]]</td><td>多 Agent 学习探索对方的能力并选择合作伙伴，以改善即时交互与任务表现。</td><td>合作完成当次任务并不代表离开同伴后学会；I5 以<strong>持久的个人更新</strong>为主要指标。</td></tr>
 <tr><td><b>HACE</b>（2026） [[S90]]</td><td>专用模型与 Agent 相互改进，甚至演化两者的信息交换流程（Harness）。</td><td>I5 固定教学/更新过程，重点研究<strong>十个学习者之间边的选择与持续重连</strong>；不能声称首次异构共进化。</td></tr>
 </tbody></table></div>
 <p class="note"><b>新颖性底线：</b>“有十个模型”“动态选老师”“两个模型双向蒸馏”“奖励驱动换伴”都已有强近邻。若不能证明<strong>学习收益驱动的配对序列</strong>相对固定配对、随机轮转及适应性协作路由有独立增益，I5 不应当作新方法论文。</p>
 '''),
 ("challenge", "Challenge：好伙伴不等于强伙伴，换得勤也不一定好", '''
 <p><b>① 对方比我强，不等于能教会我。</b>它的解法可能超出我的可吸收范围；也可能我们会的东西完全一样。</p>
 <p><b>② 当次合作解题变好，不等于我自己变强。</b>模型在聊天上下文里抄到答案，撤除伙伴后仍可能不会。</p>
 <p><b>③ 总是跟表现最好的同学学，可能早早失去新知识来源。</b>都在模仿相同解法时，班里虽平均分变高，却可能失去不同路径的探索。</p>
 <p><b>④ 换伴过快或过慢都有成本。</b>太快缺乏消化时间；太慢重复已经传过的知识。要测<strong>继续当前关系的边际学习收益</strong>，而不只是看固定每三轮换一次。</p>
 <p><b>⑤ 全班进步与每个人进步可能冲突。</b>只优化平均成绩可能长期忽略几个最弱成员；只保证每人平均交流次数，也不能保证教学有效。需要单列最低表现与覆盖。</p>
 '''),
 ("insight", "Insight：伙伴关系也要像能力一样一起进化", '''
 <p>我们希望验证的机制是：<strong>早期与知识不同的人接触，带来以前没见过的新方法；随后与可吸收、能相互纠错的伙伴多交流几轮，让方法真正学会；当重复交流不再提供新收益，就跨圈换伴。</strong></p>
 <p>这是从 NC 的桥接顺序、知识分布和社会收益学习研究中提炼的<strong>待验证假设</strong>，并不是人类实验已经证明的 LLM 训练规律。固定的“先跨圈后巩固”必须作为基线；I5 额外要学的是<strong>每个个体何时需要跨圈、与谁继续最合算</strong>。</p>
 <p>学习网络可分成三件事：<strong>新知识流入</strong>（对方是否掌握我缺少且能理解的东西）、<strong>双方真正吸收</strong>（各自撤离后是否进步）以及<strong>下一轮还有探索余地</strong>（是否只在同一类解法中循环）。三个量都可测，任何一个都不能用当前协作分数替代。</p>
 '''),
 ("design", "Design：五对同学互教，离开伙伴独立考试，再换下一轮", '''
 <div class="flow">
 <div><b>10 个独立学习者</b><small>初始能力 × 专长矩阵</small></div>
 <div><b>每轮组成 5 对</b><small>固定总交流时间与教学协议</small></div>
 <div><b>双向教学 + 更新</b><small>同伴反馈，各自 LoRA / Skill 写入</small></div>
 <div><b>撤除伙伴独立考试</b><small>新题学习增益 + 旧能力保持</small></div>
 <div><b>决定留伴或换伴</b><small>估计边际收益、独特知识与成本</small></div>
 </div>
 <h3>最小可执行设计</h3>
 <p>每个模型初始各有一个单独检查点，按<strong>能力强/中/弱</strong>及<strong>擅长领域</strong>交叉构建。每轮固定一个配对图：十个模型组成五对，每对先交换经过验证的解题轨迹/错误反馈，再使用同一种冻结的更新规则分别写入各自 LoRA（最初不同时改权重、Skill 与 Harness），最后删除聊天内容、移除伙伴，独立作答。</p>
 <p>对每个模型记录<strong>独立新题增益、旧能力回归、教师和学习者双方收益、未见任务覆盖</strong>；对每条曾出现的配对边记录预期净收益和不确定性。当一对伙伴继续交流的边际收益下降，且另一伙伴有更可信的未覆盖互补知识时，允许换伴。初期保留少量随机轮换，避免只凭早期噪声把关系锁死。</p>
 <h3>互教网络的选择目标</h3>
 <div class="equation">选择下一轮五对伙伴 = 最大化全班的预期独立净学习增益 − 交流/更新成本，受回归、安全和成员覆盖约束</div>
 <p>这是问题定义，不是已验证的最优匹配公式。首次验证可用<strong>bandit 估计各配对边的双向增益，再在十节点一般图中做最大权匹配</strong>，与不用学习网络参数的静态方案比较；不要上来设计庞大的多 Agent 架构。若使用探索奖金，必须同时记录它是否真的带来新知识而非仅增加互动次数。</p>
 <h3>正交接口：I5 只管“谁与谁、什么时候换”</h3>
 <p><a href="ideas.html#idea-1">I1</a> 研究学进自身还是外查；<a href="ideas.html#idea-2">I2</a> 研究配对后采用什么教学方式；<a href="ideas.html#idea-3">I3</a> 研究新旧能力怎么巩固；<a href="ideas.html#idea-4">I4</a> 研究一次失败是否继续探索；<a href="idea-i6-failure-value.html">I6</a> 研究失败轨迹的学习价值；<a href="idea-i7-learning-order.html">I7</a> 研究先试还是先学；<a href="i8.html">I8</a> 研究哪些错误能产生跨题迁移。<strong>I5 不负责这些动作，只生成伙伴配对与交换时机。</strong>固定其余动作的实现后，I5 的作用仍应能被独立检验。</p>
 '''),
 ("experiments", "决定性实验：交换舞伴真的能让整个班级长得更快吗？", '''
 <h3>E1 · 先证明“同样能力差距，并不等于同样教学收益”</h3>
 <p>先用 4 个模型做小规模配对全枚举；控制题目、冻结初始检查点和交互预算，测有无先验互补、可吸收性和两人各自更新后的收益。用不同规模和同规模不同专长模型，把“参数量差距”与“知识差异”分开。若能力差距已足够解释所有最优配对，复杂互补估计就没必要。</p>
 <h3>E2 · 固定交流次数，只改变十模型的接触网络和顺序</h3>
 <p>在 10 模型上比较<strong>固定伴侣 / 随机轮换 / round-robin / 最强者为师 / 同级配对 / 互补知识配对 / 先跨组后组内 / PopuLoRA 式匹配 / 基于短期协作收益的 MACE 式匹配 / I5 学习净收益驱动的动态换伴</strong>。每模型总曝光、更新步数、可用验证器与总计算成本匹配；特别控制不同模型规模的 FLOPs。报告配对随轮次变化的动态图，而不是只展示最终最高分。</p>
 <h3>E3 · 区分传播已有解法与真正发现新解法</h3>
 <p>训练数据中为不同学习者分配部分独特技能；预留需要<strong>跨专长组合</strong>才能解决的未见问题。分开测（a）学到别人已有的能力、（b）两者结合后找到以前都没发现的正确路径、（c）下一轮独立迁移与保持。加入“只交流答案不更新”“只更新不轮换”“轮换但打乱增益反馈”消融；用 4–5 个随机种子检验网络是否过早同质化及弱者是否被冷落。</p>
 <h3>Go / Merge / Stop</h3>
 <div class="table-wrap"><table><thead><tr><th>裁决</th><th>要求</th></tr></thead><tbody>
 <tr><td>继续 I5</td><td>不同伙伴的独立学习收益可重复地因能力和知识状态而变；换伴相对静态与轮换强基线带来<strong>跨轮全班净收益</strong>，且不是增加交流预算所致。</td></tr>
 <tr><td>退为现象工作</td><td>证实顺序/互补有显著现象，但简单 round-robin 或 bandit 已达到全部收益；保留因果发现，不硬包装新路由器。</td></tr>
 <tr><td>停止/合并</td><td>只提高当前共同答题表现，撤除伙伴后无收益；优势只来自反复传播现成答案或固定最强教师；退化与计算成本抵消增长。</td></tr>
 </tbody></table></div>
 <p class="status">截至 2026-10-27：本页是 I5 调研后的研究问题与验证方案；尚无十模型持续训练的本项目受控结果。</p>
 '''),
 ("teaching-feedback", "I5 的历史研究支线：教别人能否发现自己的盲点？", '''
 <p><b>为什么放在同一个 I5 下？</b>前面的十模型互教是当前主线，研究<strong>和谁学、何时交换伙伴</strong>。此前还有一个相邻问题：Agent 教另一个 Agent 时，学生的追问或误用，能否帮教师发现自己本来没发现的知识缺口？两者都从“以教促学”出发，但<strong>研究变量、更新对象和主要实验不同</strong>，不作为两个并列的 I5。</p>
 <div class="table-wrap"><table><thead><tr><th>同属 I5 的研究记录</th><th>要回答的问题</th><th>独立验证</th></tr></thead><tbody>
 <tr><td><strong>当前主线：十模型动态互教</strong></td><td>随着双方能力变化，下一轮跟谁学、何时换伴最有效？</td><td>撤除伙伴后各模型的独立能力增益、群体学习曲线</td></tr>
 <tr><td>历史支线：教学反馈诊断</td><td>学生的错误和追问，能否暴露教师自己原本没有意识到的知识缺口？</td><td>教师从学生反馈更新前后的独立任务表现，与同预算自测比较</td></tr>
 </tbody></table></div>
 <p>我们保留这份早期技术方案与原始实验契约，方便以后回溯，但不再把它单独放在左侧研究方向菜单。<a href="teaching.html">查看历史支线的完整方法和实验设计</a>。</p>
 '''),
 ("summary", "I5 最后应该回答什么？", '''
 <p class="thesis"><strong>不是“十个模型投票会不会更聪明”，也不是“谁当老师最好”，而是：每个人都在成长时，如何安排下一轮的学习伙伴与交换顺序，使新知识能被更多模型真正学会，又不丧失继续发现新解法的能力？</strong></p>
 <p>我们希望最终证明的不是“班级平均分暂时上升”，而是同等总训练预算下，<strong>每个模型独立能力的长期曲线、全班累计净学习增益、旧能力保持与新组合任务的发现率</strong>比固定配对更好。<a href="ideas.html#idea-5">返回 I5 摘要</a> · <a href="teaching.html">教学反馈诊断教师盲点（历史独立支线）</a>。</p>
 ''')
 ]
}
