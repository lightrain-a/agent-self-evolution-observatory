"""Reader-facing Chapter 3: concrete acquisition trade-offs, evidence near claims.

Rendered by rsi_framework.framework_pages as the sole experience chapter source.
Preserve four-function classification and stable chapter/deep-link anchors.
Manuscript reference: RSI_review2610, 8f3eec2e, sections/acquisition.tex.
"""
PAGE = {
    "slug": "experience",
    "title": "经验获取：下一步该经历什么，才会真正学到东西？",
    "en": "Chapter 3 · Acquiring Useful Learning Experiences",
    "lead": "多出题、多采样、找更强的老师，都可能有用，却也可能只是重复旧错误。本章先看几组具体矛盾，再讨论怎样补缺口、构造新经历、获取外部信息，以及判断这些经历是否值得学习。",
    "updated": "2026-10-29",
    "chapter": 3,
    "primary_function": "experience",
    "sections": [
        ("question", "先看六个发现：经历更多，不一定学得更多", '''
<p>假设一个代码 Agent 连续做错十次。下一步应该再生成十个解法、找老师给答案、运行一个测试，还是先补一条基础规则？这些动作都在增加经历，却不一定解决同一种问题。</p>
<div class="exp-insights">
<article><a href="#section-3-1"><span>01 · 尝试次数 ↔ 瓶颈突破</span><b>继续练没进步，可能缺的不是练习量</b></a><p>已有技能的瓶颈可能藏在感知或子能力里；扩大搜索与补基础，应当分别检验。[[E380]][[S763]]</p></article>
<article><a href="#section-3-2"><span>02 · 候选覆盖 ↔ 单次可靠性</span><b>解法更多，不等于第一条答案更准</b></a><p>探索可以覆盖更多路径，但最终能否选对、以后是否真正学会，是后面两件事。[[S764]]</p></article>
<article><a href="#novelty-not-volume"><span>03 · 表面新颖 ↔ 规则信息</span><b>题目换了名字，可能仍在强化同一个捷径</b></a><p>关键是新例子有没有迫使不同规则给出不同预测，而不只是文本看起来不同。[[M17]][[E26]]</p></article>
<article><a href="#section-3-3"><span>04 · 教师答对 ↔ 学生学会</span><b>全知老师给出的正确答案，未必最好学</b></a><p>学生看不到老师的隐藏信息时，示范怎样在不确定中判断，可能更有帮助。[[S100]]</p></article>
<article><a href="#section-3-4"><span>05 · 难度/新颖性 ↔ 更新后收益</span><b>题目很难、很新，也不代表当前学生学得动</b></a><p>有用的经验应与当前学习者相配；SOAR直接用学生实际进步来训练出题教师。[[S47]]</p></article>
<article><a href="#retain-or-replace"><span>06 · 新数据增长 ↔ 旧覆盖与成本</span><b>自生成数据会不会越学越窄，要看旧数据去哪了</b></a><p>用生成数据替换旧数据，与保留原数据后累积新数据，是不同实验条件。[[S766]][[S767]]</p></article>
</div>
<p class="exp-takeaway"><strong>本章的主线：</strong>不是问“怎样再弄来一批数据”，而是问“当前学习者缺哪一种经历，这次新增经历会改变什么”。这些关系未必是不可突破的取舍；改对获取方式，有时可以同时改善多个结果。</p>
<p class="exp-small">下文每节先讲原论文证据，再讲 LLM／RSI 可以怎样检验。我们的扩展标为“待检验”，不写成已完成结果。章节仍对应能力缺口、任务交互、外部信息、经验选择四个问题。</p>
'''),
        ("section-3-1", "3.1 做不出来：是没试到办法，还是缺一块基础？", '''
<p>失败次数告诉我们问题没有解决，却没有告诉我们该补什么。代码报错可能来自没见过某种任务、没有探索到可行步骤，也可能是不会使用关键工具。若瓶颈没有变化，多做几遍也可能原地打转。</p>
<div class="exp-paper" data-source-id="E380"><h3>跨领域证据｜专家没进步，换一种练习才出现改善</h3>
<p><a href="reading-notes.html#deep-scienceadv2020-expert-haptic-ceiling-hirano"><b>Hirano 等 · Science Advances 2020</b></a>：钢琴专家在所测普通运动练习下没有明显改善；主动触觉辨别训练及反馈，则改善了特定低力度控制。这个结果提示，有时应训练支撑表现的相关功能，而不只是重复目标动作。它不是证明“所有平台期都缺基础”，不同训练的任务和剂量也并非完全相同。[[E380]]</p></div>
<div class="exp-paper" data-source-id="S763"><h3>语言模型的另一种处理｜先确认是不是搜索没覆盖到</h3>
<p><a href="references.html#S763"><b>Representation-Based Exploration（RepExp）· ICLR 2026</b></a>利用回答的内部表征引导探索，改善所测候选覆盖与 pass@k。它处理的是“有没有找到更多有效路径”，与上面“目标表现依赖的子能力没准备好”并不是同一个诊断。[[S763]]</p></div>
<div class="exp-actions">
<p data-layer="llm-proposal"><b>LLM 可以怎样试｜待检验：</b>从同一模型状态分出三组：增加候选搜索、专门训练疑似缺失的子能力、继续练原任务；分别控制反馈与总成本。只有补基础后在未练过的同类任务也受益，才更支持缺口诊断。</p>
<p data-layer="rsi-proposal"><b>RSI 再往前一步｜待检验：</b>记录每种失败后来被什么干预真正修好，让下一代更会判断“该探索、求助还是补基础”。<a href="idea-i12-prerequisite-bottleneck.html">I12</a>进一步检验先修知识是否提高第二阶段学习；<a href="idea-i6-failure-value.html">I6</a>比较不同失败过程的学习价值，不改变本章分类。</p>
</div>
<p class="exp-check"><b>一起看：</b>新方法是否被找到、真实更新后的未见任务表现、诊断与训练成本，而不只看这一次有没有答对。</p>
<details class="exp-detail"><summary>同样“增加经验”，三项经典工作补的东西并不相同</summary>
<p><a href="references.html#S760"><b>Self-Instruct · ACL 2023</b></a>从种子指令扩展任务和实例；<a href="references.html#S762"><b>Voyager · TMLR 2024</b></a>通过环境交互获得可复用程序；<a href="references.html#S47"><b>SOAR · ICML 2026</b></a>产生能让当前学生进步的教学材料。它们分别涉及任务覆盖、行动经历和中间学习机会，不能只按数据条数比较。Voyager的技能库是持久外部状态，不应默认写成底座模型权重增长。[[S760]][[S762]][[S47]]</p>
</details>
'''),
        ("section-3-2", "3.2 该换一道题，还是为同一道题寻找另一条解法？", '''
<p>一个 Agent 已经做过一千道相似题，还在同一种边界条件下犯错。继续增加题目数量、为原题寻找不同解法、专门构造一条反例，可能产生完全不同的学习材料。先分清要改变的是<strong>题目分布</strong>还是<strong>解法分布</strong>。</p>
<div class="exp-paper-pair">
<article class="exp-paper" data-source-id="S760"><h3>Self-Instruct：扩大“会遇到哪些题”</h3><p><b>ACL 2023</b>，由种子任务生成指令与实例，过滤后训练模型。它首先改变任务覆盖。[[S760]]</p></article>
<article class="exp-paper" data-source-id="S761"><h3>STaR：为给定问题补推理轨迹</h3><p><b>NeurIPS 2022</b>，生成推理、筛选正确结果；失败时也利用已知答案重新生成，再用于微调。它不是从完全没有答案的条件开始。[[S761]]</p></article>
</div>
<h3 id="candidate-coverage">候选集更丰富，第一条答案却未必更可靠</h3>
<div class="exp-paper" data-source-id="S764"><p><a href="references.html#S764"><b>ESamp · ICML 2026，Large Language Models Explore by Latent Distilling</b></a>在解码时训练轻量辅助预测器，用表征预测差异调整采样；主语言模型保持冻结。论文与综述记录都区分了候选覆盖和单样本表现，部分设置并非两项一起上升。<strong>“多条答案中出现正确答案”与“实际输出选中了它”不是同一指标。</strong>[[S764]]</p></div>
<p><a href="references.html#S763"><b>RepExp</b></a>则可以从已有候选中选出更有差异的子集，减少送给验证器的候选；它的训练分支还会把表征奖励加入任务奖励。选择候选、改变解码和更新主模型，是三个不同作用点，不能都简称“模型学会探索”。[[S763]]</p>
<h3 id="novelty-not-volume">一道真正能排除捷径的题，可能比十道换词题更有信息</h3>
<div class="exp-paper" data-source-id="E26"><p><a href="reading-notes.html#deep-hypothesis-testing-2026-ding"><b>Ding 等 · npj Science of Learning 2026</b></a>通过改变运动训练的位置，让竞争策略能否蒙对变得不同；初期进步快的设置，未必在无反馈新位置上使用正确规则。它提供的是“用经历区分解释”的实验线索，不是直接测到了快脑／慢脑回路。[[E26]]</p></div>
<p><a href="reading-notes.html#deep-mosaic-memory-2026-shilov"><b>The mosaic memory of large language models · Nature Communications 2026</b></a>还提醒：文字变了，不代表记忆依赖已经独立。该论文测的是文本记忆，并没有证明所有改写题都不能帮助推理。对我们而言，应另测新题是否要求不同规则、能否排除当前捷径。[[M17]]</p>
<div class="exp-actions">
<p data-layer="llm-proposal"><b>LLM 可以怎样试｜待检验：</b>固定原题和生成预算，比较随机多采样、表征多样性选择、针对错误规律的反例；分别测 pass@1、候选中的正确覆盖、实际选择后的正确率，以及用这些材料真实训练后的未见题收益。</p>
<p data-layer="rsi-proposal"><b>RSI 再往前一步｜待检验：</b>让 Agent 根据历史更新结果，学会判断本轮应该扩大问题覆盖，还是只需要一条能推翻错误解释的经历。<a href="idea-i10-learning-novelty.html">I10</a>聚焦反例和组合信息；何时停止探索并总结则属于<a href="ideas.html#idea-4">I4</a>。</p>
</div>
<p class="exp-check"><b>一起看：</b>题型覆盖、规则区别、一次输出质量、验证成本和下一轮学习收益；样本数量不是这些指标的替代。</p>
<details class="exp-detail"><summary>有限反馈应该标注给谁：帮当前选答案，还是训练更好的评价器？</summary>
<p><a href="references.html#S765"><b>Let's Verify Step by Step · ICLR 2024</b></a>的主动采集关注看起来有说服力、最终却错误的解法，为过程评价提供标注；RepExp 的候选子集选择则更多用于分配本次验证覆盖。前者可以改善未来评价器，后者可改善当前候选选择。要分别计生成、筛选、标注和训练成本，不能把少调用几次验证器直接称作全流程更省算力。[[S765]][[S763]]</p>
</details>
'''),
        ("section-3-3", "3.3 老师答得全对，学生就一定学得最好吗？", '''
<p>假设老师知道用户真正喜欢什么，直接给出正确推荐；学生却只能看到几条不完整的历史。如果只模仿老师的选择，学生可能学不到“信息不够时怎样判断”。<strong>答案正确，与示范能否从学生可见的信息中学会，是两个问题。</strong></p>
<div class="exp-paper" data-source-id="S100"><h3>原论文｜会在不确定中推断的老师，可能比全知老师更适合教</h3>
<p><a href="references.html#S100"><b>Bayesian teaching enables probabilistic reasoning in large language models · Nature Communications 2026</b></a>让语言模型模仿规范贝叶斯学习者的预测。在所测交互推荐任务中，这种教学优于直接提供用户正确选择的 Oracle 教师，并展示部分跨任务迁移。它并不是鼓励教师故意答错，而是让示范反映学生实际面对的信息与不确定性。[[S100]]</p></div>
<div class="exp-paper" data-source-id="S105"><h3>另一条获取途径｜让学生主动问缺失的信息</h3>
<p><a href="references.html#S105"><b>INTERACT · ACL 2025</b></a>研究由学生提问、和教师交互来获取新概念。它说明主动提问本身已经有直接前作；上下文中获益，还需要另测对话撤除后是否保留到参数或持久技能里。[[S105]]</p></div>
<div class="exp-actions">
<p data-layer="llm-proposal"><b>LLM 可以怎样试｜待检验：</b>控制学生与训练量，比较只给正确答案、按学生能看到的信息给示范、允许少量主动提问。教师整体成绩不是唯一筛选条件；应测学生在没有老师时能否独立处理新例子。</p>
<p data-layer="rsi-proposal"><b>RSI 再往前一步｜待检验：</b>用实际受教后的结果判断哪个伙伴提供了新线索、哪个只重复共同盲点。这里讨论信息从哪里来；跨轮教法怎么变化和何时换伙伴，分别由<a href="idea-i2.html">I2</a>与<a href="idea-i5.html">I5</a>研究。</p>
</div>
<p class="exp-check"><b>一起看：</b>教师答案质量、学生可见信息、撤除帮助后的表现、外部调用成本；多模型一致不能自动视为独立证据。</p>
<h3 id="external-information">没有新人工标签，不等于没有外部信息</h3>
<div class="exp-paper-pair">
<article class="exp-paper" data-source-id="S768"><h3>SPIN：保留的目标数据仍是参照</h3><p><b>ICML 2024</b>，使用已有 SFT 目标与模型连续生成进行对比训练。没有每轮新增人工答案，不等于原始目标分布不再起作用。[[S768]]</p></article>
<article class="exp-paper" data-source-id="S769"><h3>Absolute Zero：执行环境提供约束</h3><p><b>NeurIPS 2025</b>，构造程序、输入、输出任务，由执行器验证。自生成任务依然依赖预训练模型、设计的任务格式与真实运行反馈。[[S769]]</p></article>
</div>
<p><strong>因此，要说明系统新获得了什么。</strong>是老师提供了原先不知道的事实，工具返回了新的执行结果，还是模型把已有知识换一种说法？三者都可能有用，但不能当作同一种信息增长。反馈是否可信，接着由<a href="signals.html">第四章“学习信号”</a>回答。</p>
'''),
        ("section-3-4", "3.4 更难、更新颖的经历，为什么未必更值得学？", '''
<p>一道题很难，可能正好补上薄弱环节，也可能远超当前能力；一条失败很新颖，可能暴露共同错误规则，也可能只是偶然噪声。<strong>价值属于“这条经验与当前学习者的关系”，不永久贴在题目本身。</strong></p>
<div class="exp-paper" data-source-id="S47"><h3>直接的 AI 证据｜用学生真正进步多少，训练出题老师</h3>
<p><a href="reading-notes.html#deep-soar-2601-18778"><b>SOAR · ICML 2026，Teaching Models to Teach Themselves</b></a>让教师提出训练题，再从同一起点真实训练学生，用其在目标难题上的进步奖励教师。这比只看题目难度更贴近实际教学收益，但也增加试训和评价成本。其教师奖励所用题目与最后独立测试还要分开，不能把内部奖励直接当最终泛化。[[S47]]</p></div>
<div class="exp-paper" data-source-id="M52"><h3>选择已经有学习收益目标，代理仍需要验收</h3>
<p><a href="references.html#M52"><b>RHO-LOSS · ICML 2022</b></a>按可约化的留出损失选择可学、值得学且未学会的样本。它说明“根据学习者状态挑数据”不是空白；真正需要比较的是这些代理能否预测当前任务与预算下的独立学习收益。[[M52]]</p></div>
<div class="exp-actions">
<p data-layer="llm-proposal"><b>LLM 可以怎样试｜待检验：</b>同一个学生、同样的更新器和预算，比较按难度、语义新颖性、可学习性代理选题，以及少量实际试训后选题。评价未见同规则任务和旧能力变化，并把试训成本算进去。</p>
<p data-layer="rsi-proposal"><b>RSI 再往前一步｜待检验：</b>保留“什么材料在什么学习状态下带来真实进步”的记录，让下一轮选择依据更新，而不只是累积更多错题。<a href="i8.html">I8</a>研究纠错的规则级收益；<a href="idea-i6-failure-value.html">I6</a>比较同题不同失败过程；课程分配与停止则放回第六章。</p>
</div>
<p class="exp-check"><b>一起看：</b>当前成功率、真实更新后的新题增量、旧能力保持、验证与训练总成本；难度没有天然统一的最优值。</p>
<h3 id="retain-or-replace">长期获取还要问：新数据进来后，旧数据去了哪里？</h3>
<div class="exp-paper-pair">
<article class="exp-paper" data-source-id="S766"><h3>Nature 2024：递归替换可以丢掉分布信息</h3><p><b>AI models collapse when trained on recursively generated data</b>研究递归生成与有限重采样中的退化，包括用新一代合成数据替换原数据的条件。不能据此概括所有使用合成数据的系统。[[S766]]</p></article>
<article class="exp-paper" data-source-id="S767"><h3>COLM 2024：保留并累积，结论可以不同</h3><p><b>Is Model Collapse Inevitable?</b>保留初始数据并累积生成数据，在所测实验和限定分析中避免渐进误差爆炸；但保留量与训练暴露随之改变。[[S767]]</p></article>
</div>
<p><strong>这不是一句“合成数据好还是坏”能回答的。</strong>新增经历是否扩大覆盖，哪些旧经历被丢掉，保留需要多少资源，以及模型有没有从中学到新能力，要分别测。避免退化不等于无限变强；若预算固定，还需要比较保留、压缩或替换哪部分经验。</p>
<details class="exp-detail"><summary>把三种“多样性”分开，避免指标替代</summary><p>文本不重复、内部表征覆盖广、需要不同解法，是三个不同量；Mosaic Memory 的文本记忆结果不能直接当作推理无效，RepExp/ESamp 的候选覆盖也不能直接当作训练信息独立。针对同样的输入预算，应分别检验表面重叠、策略差异和真实后测收益。[[M17]][[S763]][[S764]]</p></details>
'''),
        ("research-directions", "这些问题归哪个 I？获取经验，不等于已经形成能力", '''
<p>第三章研究<strong>系统接下来看到什么、尝试什么、向谁取得哪些信息</strong>；第四章检查结果与反馈是否可靠，第五章讨论如何形成持久能力，第六章研究多轮安排与机制更新。一个工作可以涉及几个环节，但主分类不因这次表达改版改变。</p>
<div class="exp-ideas">
<a href="idea-i10-learning-novelty.html"><b>I10 · 本章主线</b><span>新增例子能否区分正确规则与捷径，能否支持新的组合？</span></a>
<a href="idea-i12-prerequisite-bottleneck.html"><b>I12 · 缺口与后续学习</b><span>识别前置缺口只是起点；补基础后下一段真实训练是否更有效，属于跨轮学习调控。</span></a>
<a href="idea-i2.html"><b>I2 / I5 · 信息来源与教法</b><span>教师和伙伴本轮提供什么信息，在本章讨论；教法与伙伴关系如何进化，在第六章讨论。</span></a>
<a href="i8.html"><b>I6 / I8 · 从失败到学习价值</b><span>不能只收集错题，还要确认纠错后哪些独立能力发生了变化；主归属是学习信号。</span></a>
</div>
<p class="exp-takeaway"><b>真正的 RSI 问题再多一步：</b>经历了几轮真实学习后，系统是否更会选择下一条经验？要固定学习者、候选来源和预算，比较新旧获取策略在未见任务上的后续效果。反复运行一个固定生成器，与获取策略本身变好，应分开表述。</p>
'''),
        ("evidence-connection", "读完这一章，怎样判断“这次经验获取真的有用”？", '''
<p>一个最小的验证闭环是：从同一学习者状态出发，按不同方式获取等预算经历，使用相同的反馈与更新机制，最后在没参与选择的新任务上测试。下面三层结果要分别记录。</p>
<div class="exp-audit">
<div><span>先看获取</span><p>这次拿到了什么新约束或新解法？候选覆盖、正确性与采集成本如何？</p></div>
<div><span>再看学习</span><p>模型或持久 Skill 更新后，独立新题进步多少？旧能力受损了吗？改善保存在哪里？</p></div>
<div><span>最后看策略</span><p>新一代获取规则在相同起点和预算下是否优于旧规则，而不只是任务模型更强、查了更多资料？</p></div>
</div>
<details class="exp-detail"><summary>让论文中的三个比较可以落地</summary><p><b>平台期诊断：</b>更多搜索 vs训练疑似子能力 vs普通练习，比较未练同类任务收益和总成本。<b>获取方式：</b>固定题目换候选，或固定候选生成方式换题目，避免同时改变两个分布。<b>教学适配：</b>固定学生与可见信息，比较答案质量代理、学习收益代理和真实短程试训后的选择。</p><p>pass@k 表示一组候选中包含正确答案的程度，不等于真实选择器能认出它；pass@1、选中答案表现与持久学习后成绩要分开。推理时帮助、外部技能和参数学习也分别报告。这里是我们的比较设计，不是已执行的新实验。</p></details>
<div class="links"><a class="link-btn" href="generalization-learnability.html">泛化专题：先看指标之间的权衡</a><a class="link-btn" href="evidence.html">第七章：独立证据与评价</a><a class="link-btn" href="signals.html">接着读：如何判断经历说明了什么</a></div>
'''),
        ("representative-work", "回到原论文：按问题找文献，不必从末尾倒推论点", '''
<p>关键文献已在3.1–3.4相应论点旁边介绍。这里仅提供复查入口，不另堆一份同内容的长表。</p>
<details class="exp-detail"><summary>按本章问题查看来源与完整精读</summary>
<p><b>平台期与缺口：</b><a href="reading-notes.html#deep-scienceadv2020-expert-haptic-ceiling-hirano">主动触觉训练精读</a>、RepExp、SOAR。[[E380]][[S763]][[S47]]</p>
<p><b>题目、解法与信息：</b>Self-Instruct、STaR、ESamp、RepExp、Let's Verify Step by Step；<a href="reading-notes.html#deep-hypothesis-testing-2026-ding">假设检验精读</a>与<a href="reading-notes.html#deep-mosaic-memory-2026-shilov">Mosaic Memory精读</a>。[[S760]][[S761]][[S764]][[S765]]</p>
<p><b>外部教师与约束：</b>Bayesian Teaching、INTERACT、SPIN、Absolute Zero。[[S100]][[S105]][[S768]][[S769]]</p>
<p><b>学习价值与跨轮覆盖：</b><a href="reading-notes.html#deep-soar-2601-18778">SOAR精读</a>、RHO-LOSS、递归数据退化与累积保留对照。[[M52]][[S766]][[S767]]</p>
</details>
<details class="exp-detail"><summary>与综述论文的对应关系：网站扩展解释，回填时仍核对原文</summary>
<p>参考 <a href="https://github.com/lightrain-a/RSI_review2610/blob/8f3eec2e370e251e7d72ec7e981ba44285f9f75a/sections/acquisition.tex" target="_blank" rel="noopener noreferrer">RSI_review2610 · 第三章源码（读取版本 8f3eec2e）</a>，保留原稿关于需求诊断、题目/轨迹分布、探索作用点、教师信息条件、跨轮数据保留与外部约束的论证。本页按网站四个稳定小节重新编排，将相关论文移到论点旁，并补充中文例子与“LLM／RSI待检验”分层。</p>
<p>论文原来的“选择适合学习者的经历”与“覆盖及外部信息”跨越网站3.3/3.4，不能机械按小节序号回填。后续修改论文应按具体问题和原始文献对齐；网站不是第二份独立科学证据。本轮未修改论文仓库，也没有执行本页提出的新实验。</p>
</details>
<p class="exp-small">更新：2026-10-29。代表论文的发表信息与范围保留在来源台账；跨领域启发不直接证明 LLM／RSI 机制。已认可的 I 编号、四功能分类和历史锚点保持不变。</p>
<div class="links"><a class="link-btn" href="references.html?function=experience#function-experience">全部经验获取来源</a><a class="link-btn" href="reading-cards.html?function=experience">筛选相关精读</a></div>
'''),

    ],
}
