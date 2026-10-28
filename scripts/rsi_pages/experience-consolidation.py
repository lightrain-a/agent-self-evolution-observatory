"""Unnumbered RSI memory/experience research hypothesis.

Keep the distinctions between memory retrieval, skill compilation, parameter
internalization and inherited learnability explicit. No completed experiments.
"""
PAGE = {
 "slug": "experience-consolidation",
 "title": "研究候选 · 经验何时应该成为长期能力？",
 "en": "From Experience to Competence: When to Retain, Abstract, or Internalize?",
 "lead": "研究可验证的成功与失败经历，何时应保留原始 Episode、何时可安全抽象为 Skill、何时才值得写入模型参数。先证明真实净收益，再研究能否事前选择和持续改进这套决策规则。",
 "updated": "2026-10-29",
 "sections": [
 ("question", "Observable Phenomenon｜有用的经历，为什么保留下来反而可能伤害后代？", '''
<div class="decision"><span class="kicker">RSI CANDIDATE · EXPERIENCE / MEMORY / SKILL · 2026-10-29</span><h3>When Does an Experience Deserve to Become a Skill?</h3>
<p>Agent成功执行了一次工具流程，留下可信的原始操作记录。下次遇到类似任务，<b>原样检索</b>可能有帮助；但把该记录概括为“一律这样做”的规则，可能省掉关键条件。新的任务在表面上接近，实际权限、选择条件或规则却不同，于是一个本来成功的经验在后代变成了错误的行动依据。</p>
<p><b>我们关心的科学矛盾：</b>相同的原始Episode、当前同样有效，经过不同的巩固动作后，为什么未来独立能力和错误传播会出现不同的结果？能否在巩固之前预测哪种动作真值得做？</p>
<p><b>研究状态：</b>只有来自真实论文的动机与待测假设，本站尚没有这一候选的真实训练结果。当前不占用新I编号，也不替换I6。</p></div>
<div class="table-wrap"><table><thead><tr><th>四种不同的“继承”</th><th>携带的内容</th><th>什么才叫收益？</th></tr></thead><tbody>
<tr><td><b>Episode / Memory</b></td><td>原始问题、环境、执行过程与结果</td><td>未来检索后当前任务更可靠；必须量化检索成本</td></tr>
<tr><td><b>Abstract Rule</b></td><td>自然语言总结、适用条件和反例</td><td>比原样Episode更省或更能迁移，且没有更多误用</td></tr>
<tr><td><b>Executable Skill</b></td><td>条件化的工具流程或脚本，具备版本和回滚</td><td>在未来新场景可运行、满足权限和前提</td></tr>
<tr><td><b>Parameter Update</b></td><td>SFT/LoRA更新形成模型权重改变</td><td>移除外部帮助仍能独立完成未见题、且旧能力不退化</td></tr>
</tbody></table></div>
'''),
 ("evidence", "证据链｜Science 2024 + 两篇LLM论文分别贡献什么？", '''
<div class="table-wrap"><table><thead><tr><th>原论文</th><th>真实实验结论</th><th>RSI 尚未验证的步骤</th></tr></thead><tbody>
<tr><td><a href="reading-notes.html#deep-sharp-wave-ripples-science2024-yang"><b>Science 2024 · 小鼠SPW-R</b></a></td><td>清醒被重放的经历，在之后睡眠中也更常被重放（5鼠/16会话，R=0.86），属于内容选择关联，不是长期成绩或成功/失败价值。</td><td>能否用经验结束时的标签信号预测未来巩固净收益？</td></tr>
<tr><td><a href="reading-notes.html#deep-memory-management-acl2026-xiong"><b>ACL 2026 · Memory Management</b></a></td><td>四Agent全量新增都劣于固定库；严格筛选优于全量。记忆检索存在Experience-Following和Misaligned Replay，历史调用评分可用于有限清退。</td><td>单条Memory的随机有/无检索效应，能否预测转成Skill后实际价值？</td></tr>
<tr><td><a href="reading-notes.html#deep-faulty-memory-arxiv2026-zhang"><b>arXiv 2026 v2 · Faulty Memory</b></a></td><td>真实正确轨迹在多轮抽象/原地改写中可能失真；19题100%→54%，Table5 Raw 76.6 对 Default 43.2。Auto/Episodic-only已是强基线。</td><td>何时Abstract可在等资源条件下比Raw更好？能否在新任务族上预测并通过验证？</td></tr>
</tbody></table></div>
<p><b>相关的更早工作：</b><a href="https://ojs.aaai.org/index.php/AAAI/article/view/29936" target="_blank" rel="noopener noreferrer">ExpeL（AAAI 2024）</a>已从成功/失败轨迹提炼经验；<a href="https://proceedings.mlr.press/v306/wu26bf.html" target="_blank" rel="noopener noreferrer">EvolveR（ICML 2026）</a>已研究经验效用评分、原则整理和下游学习。因此“总结失败经验”“删除低质量Memory”“Auto决定是否抽象”均不是可独立主张的创新。</p>
'''),
 ("mechanism", "机制假设｜真正的冲突不只发生在“是否保留”，还发生在“如何使用和改写”", '''
<div class="flow"><div><b>Episode 生成</b><small>一次成功/失败及可靠反馈，保留原始出处</small></div><div><b>候选价值估计</b><small>未来何时会用、规则关系、前置条件、潜在风险</small></div><div><b>巩固动作选择</b><small>Raw / Abstract / Skill / Parameter / Defer</small></div><div><b>独立未来验收</b><small>迁移、误传播、旧能力、总成本</small></div><div><b>学习决策规则</b><small>能否跨任务/模型代际提高实际选择质量</small></div></div>
<div class="table-wrap"><table><thead><tr><th>机制变量</th><th>为什么要单独测</th><th>容易混淆的结果</th></tr></thead><tbody>
<tr><td>原始经验正确性</td><td>成功记录也可能含偶然捷径或不适用步骤</td><td>当前Success ≠ 可泛化规则</td></tr>
<tr><td>适用边界的保真性</td><td>摘要可能删除前置条件、反例及排除条件</td><td>自然语言总结流畅 ≠ 真实可执行</td></tr>
<tr><td>学习者状态</td><td>同一Episode对已有基础强/弱、旧能力冲突不同的模型可能价值相反</td><td>记忆固有得分 ≠ 条件化收益</td></tr>
<tr><td>真实更新表面</td><td>检索Memory、执行Skill与修改权重的收益不能混为一谈</td><td>一次任务成功 ≠ 持久参数能力</td></tr>
<tr><td>未来任务/验证合同</td><td>旧环境正确的Rule在新权限/输入模式下可能有害</td><td>历史平均效用 ≠ 新分布风险</td></tr>
</tbody></table></div>
<p><b>两个相互竞争的假设：</b>H1，在具备可靠的共同规则关系、已观察到关键正反例时，抽象可以超过相同上下文预算下的原始Episode；H2，在规则尚未明确分族或学习者缺前置基础时，抽象更可能造成误传播，保留原始证据优于立即写回。H1和H2都要通过真实未来任务验证，不能把条件本身定义为成功标签。</p>
'''),
 ("formal", "操作性定义｜把“经验有用”和“巩固有用”分别定价", '''
<p>定义冻结学习者状态 <code>s=(θ, SkillVersion, MemoryBank, Harness)</code>、候选经验 <code>e</code>、巩固动作 <code>a∈{none,episodic,abstract,skill,lora,defer}</code>、未来测试流 <code>D_future</code>。</p>
<div class="equation">U(s,e,a) = E[ΔIndependentFutureAbility | do(a),s,e] − λ·OldRegression − μ·MisuseRisk − β·FullCost</div>
<p>这个式子是本站的<strong>候选净效用定义</strong>。不能对仅在检索时显示的Memory宣称“无提示独立能力上升”；外部记忆价值与权重内化价值分别出表，系数在实验前确定，并报告多目标Pareto敏感性。</p>
<div class="equation">ValueOfAbstraction(s,e) = U(s,e,abstract) − U(s,e,episodic)</div>
<p>当原始Episode与Abstract在可见训练资料、检索token、工具预算或新增验证次数不同，必须另外做资源匹配；差异不是一个不需代价的“理论收益”。</p>
<div class="equation">MetaGate_φ(obs_before) → {retain, abstract, compile, update, defer}</div>
<p>理论上可以从多次历史巩固的因果结果学习一个门控策略；不过自动Memory门控早已有先例，<b>只有当它在全新任务族与学习者版本上，胜过同预算最优固定策略并真正提升未来学习能力时，才构成RSI的进一步贡献</b>。</p>
<p>相关公式的长期引用：<a href="theory-notes.html#experience-tag-vs-consolidation-utility">经验选择与巩固收益</a>；<a href="theory-notes.html#memory-retrieval-causal-utility">单条记忆的反事实使用价值</a>；<a href="theory-notes.html#memory-consolidation-fidelity">抽象保真性与因果损坏控制</a>。</p>
'''),
 ("p0", "P0 · 先验证现象：同样正确的经历，抽象何时比保留Episode更有益？", '''
<p><b>优先用已有代码和确定性任务生成：</b>先在 <a href="https://github.com/DylanZSZ/Memory-Collapse-Eval" target="_blank" rel="noopener noreferrer">Memory-Collapse-Eval</a> 的ARC-AGI Stream / 同类可验证规则任务上复用环境，不再为了科研新意重复搭建庞大Memory平台。固定6个任务族、7类变换的组合结构，设计同族新对象/新数值、表面相似却规则不同、任务组合三个独立评测分布。</p>
<div class="table-wrap"><table><thead><tr><th>对照组</th><th>只改变什么</th><th>核心要排除</th></tr></thead><tbody>
<tr><td>NoMemory</td><td>不检索任何历史</td><td>模型本来会做、记忆只是干扰</td></tr>
<tr><td>Raw Episode</td><td>检索经过核验的原始经历</td><td>同一内容不抽象时的强基线</td></tr>
<tr><td>One-shot Abstract</td><td>同样Episode一次抽象</td><td>单次抽象是否真的增加跨例泛化</td></tr>
<tr><td>Family-grouped Abstract</td><td>按已知正确任务家族分组抽象</td><td>已知分组对泛化的上限，不是现实免费Oracle</td></tr>
<tr><td>Streaming / In-place</td><td>多轮相同证据重写</td><td>重复抽象的累计误差</td></tr>
<tr><td>Scope-preserving Candidate</td><td>显式保存前提、排除条件和反例，发布前验证</td><td>如果只是多token/多调用或能看测试答案，就不能算改进</td></tr>
</tbody></table></div>
<p><b>最小执行建议：</b>先选2个模型、6个规则家族、每家族8–12条高质量Episode、3次独立随机分支，使用同一外部正确性验证器。每组读取同样来源的Episode；先做相同检索token限制的外部Memory比较，随后另做Full-cost计价。评价跨规则新对象、家族边界负例、未来任务漂移。这里是计划规模，不代表已有实验结果或保证统计功效。</p>
<p><b>决定性现象：</b>在相同任务/预算下，存在部分Episode抽象后显著提高未见同规则任务，并存在另一部分Episode抽象后显著误导相似但不同规则任务；其差异不能只由当前Success/任务难度解释。如果不存在这种稳定交互，就不应发展新的门控系统。</p>
'''),
 ("p1", "P1 · 识别究竟是选错经历，还是巩固方式损坏了经历", '''
<p>这里需要<strong>正交随机化</strong>，不能先用好策略选出一组经验，再让它使用更好的巩固器与低成本预算对比。</p>
<div class="table-wrap"><table><thead><tr><th>固定条件</th><th>随机变量</th><th>结论只能是什么</th></tr></thead><tbody>
<tr><td>相同原始Episode与未来任务</td><td>有/无该Episode检索（其它检索内容、token控制）</td><td>这条Memory的反事实使用效用</td></tr>
<tr><td>固定入选Episode池</td><td>Raw / Once-Abstract / Stream / Scope-validated Abstract</td><td>巩固方式的额外作用</td></tr>
<tr><td>固定巩固方式</td><td>Random / Success-only / Historical utility / New gate</td><td>候选选择规则的额外作用</td></tr>
<tr><td>固定规则与当前能力</td><td>未见任务分布/关键条件变化</td><td>已学规则适用边界和误用风险</td></tr>
</tbody></table></div>
<p>特别要观察两种极端：<b>原始记录正确但抽象错误</b>（反事实降低表现），以及<b>原始记录笨重但可靠抽象使泛化更强</b>（越过Raw的同成本优势）。记录每次摘要的“引用哪个Episode、删除了哪个条件、加入了哪个泛化规则”的版本谱系。</p>
'''),
 ("p2", "P2 · 怎样从好Memory跨到真正的持久Skill/权重能力？", '''
<p>当P0/P1确认存在可预测的巩固收益差异后，才增加更贵的长期参数更新测试。</p>
<div class="flow"><div><b>同样的经历池</b><small>固定任务/反馈/正确答案来源</small></div><div><b>Skill编译</b><small>规则和明确前提；含反例验证</small></div><div><b>独立执行</b><small>新场景中的实际工具/规则复用</small></div><div><b>LoRA更新</b><small>等token/步数，训练后撤除外置内容</small></div><div><b>Future-C学习</b><small>与后续任务的可学习性及A/B保持</small></div></div>
<p><b>两种不同的迁移指标必须分别报告：</b>Memory/Skill可用时的任务收益；以及删除临时记忆、关闭Skill后、相同LoRA检查点获得的新能力。后一项不能用文本检索的成绩代替。</p>
<p>未来任务C也应在相同资源下执行一次真实更新，以测Meta-RSI是否使后代更会学，而不是只学会当前所有旧任务。<a href="theory-notes.html#rsi-future-learnability-objective">DiscoRL / 未来可学习性参考</a>。</p>
'''),
 ("closest", "Closest Related Work 与新颖性边界｜不能再把哪些设计称为第一篇？", '''
<div class="table-wrap"><table><thead><tr><th>已有研究</th><th>直接结果</th><th>需要超过什么</th></tr></thead><tbody>
<tr><td>ExpeL / EvolveR（2024/2026）</td><td>成功/失败轨迹抽取经验、原则并用于新任务</td><td>“总结经验、去重、选择原则”本身不新</td></tr>
<tr><td><a href="reading-notes.html#deep-memory-management-acl2026-xiong">Xiong et al. ACL2026</a></td><td>增删原始q-e记录、经验跟随、历史使用效用清退</td><td>比其历史效用阈值与严格选择有独立价值</td></tr>
<tr><td><a href="reading-notes.html#deep-faulty-memory-arxiv2026-zhang">Zhang et al. 2026 preprint</a></td><td>Static/Stream/Auto/Force/Episodic-only以及反复改写危害</td><td>不能重复“Auto保留Episode比Force好”的结论</td></tr>
<tr><td>CLIN / ACE / AWM / Dynamic Cheatsheet</td><td>记忆抽象、持续cheatsheet及程序流程复用</td><td>文本摘要门控需要与强Raw和现有动态框架对比</td></tr>
<tr><td>Learning Admission / SafeEvolve / Skill治理</td><td>更新候选接纳、版本/读写安全治理已有研究</td><td>单独保留I13的授权和安全发布门；本方向只研究经验学习效用</td></tr>
</tbody></table></div>
<p><b>潜在独立机制：</b>同一次正确经验，在不同模型准备程度、任务边界和巩固动作下的<strong>条件性因果净收益</strong>可否在写回前可靠预测，并跨后代提高真实学习收益？若只是更好的文本摘要或小缓存淘汰器，优先合并进I6而不另成论文。</p>
'''),
 ("research-boundary", "与 I6 / I8 / I10 / I13 的正交关系", '''
<div class="table-wrap"><table><thead><tr><th>原主线</th><th>研究处理变量</th><th>本候选不能重复的目标</th></tr></thead><tbody>
<tr><td><a href="idea-i6-failure-value.html">I6 · 失败轨迹价值</a></td><td>固定纠错器，比较同题同错误终点的不同失败过程是否值得学</td><td>本方向先固定输入Episode，只改变写回或调用表面</td></tr>
<tr><td><a href="i8.html">I8 · 错误规则跨题迁移</a></td><td>固定反馈，评估纠错A后未训练B的直接改善</td><td>本方向评估同Episode不同巩固操作的收益与保真度</td></tr>
<tr><td><a href="idea-i10-learning-novelty.html">I10 · 规则泛化</a></td><td>学规则与局部记忆的区别</td><td>本方向不定义组合泛化的新认知机制，关注写回动作及其效用</td></tr>
<tr><td><a href="learning-admission.html">I13 · 安全更新接纳</a></td><td>风险测试、拒绝/隔离与后代安全门</td><td>这里不修改独立授权门，不把经验收益替代安全准入</td></tr>
</tbody></table></div>
<p><b>目前的组织建议：</b>维持未编号跨I候选；其中经验价值预测归I6，记忆巩固保真性留此页，安全继承归I13。只在P0出现清晰、可复现、不是已有Memory Gate能解释的机制后再考虑升级。</p>
'''),
 ("decision", "Go / Narrow / Stop｜避免把多模块工程包装成科研突破", '''
<p><b>Go：</b>同样的原始Episode和当前成绩下，巩固动作产生稳定的正负净效用交互；事前可观测的学习者状态、规则结构和历史巩固漂移能预测这种差异；并在同预算、未见规则族及未来版本上超过Raw、Auto、History-based deletion和强固定巩固方法。</p>
<p><b>Narrow：</b>只发现坏摘要容易伤害已有表现，则收敛为“适用边界/抽象保真性”的测量论文，不强行增加新的自我改进元网络。若Raw总是最优，说明需要先研究摘要为什么无法可靠提升，而不是花算力优化Gate。</p>
<p><b>Stop：</b>严格控制原始轨迹质量、检索长度、更新步骤和额外验证成本后，全部差异消失；或者所谓收益仅来自本轮上下文帮助，撤辅后没有真实能力增益。</p>
<p><b>应长期保存的数据：</b>Episode ID及版本、模型/任务状态、候选抽象全文、规则前提/反例、预注册干预、独立测试结果、预算及回滚结果。后续可供 <a href="theory-notes.html#experience-tag-vs-consolidation-utility">理论工具箱</a>和I6/I13的真实学习响应模型复用。</p>
<div class="links"><a class="link-btn" href="reading-notes.html#deep-memory-management-acl2026-xiong">ACL 2026 完整精读</a><a class="link-btn" href="reading-notes.html#deep-faulty-memory-arxiv2026-zhang">2026 Faulty Memory 完整精读</a><a class="link-btn" href="reading-notes.html#deep-sharp-wave-ripples-science2024-yang">Science 2024 实验证据</a></div>
''')
 ]
}
