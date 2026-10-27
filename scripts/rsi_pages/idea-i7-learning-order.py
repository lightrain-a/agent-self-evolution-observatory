"""I7 research card: instructional order, independent of failure-value ranking."""
PAGE = {
    "slug": "idea-i7-learning-order",
    "title": "I7 · 先尝试，还是先看示范？",
    "en": "When Should a Model Try Before Being Taught?",
    "lead": "学习顺序在人类教育与智能教学系统中早有研究。I7 关注它迁移到 LLM 递归自我改进后，是否改变无提示独立能力、可探索解法及长期迁移。",
    "updated": "2026-10-27",
    "sections": [
        ("question", "一句话科学问题", """
<p class="thesis"><b>I7：</b>面对相同题目、相同教师示范，先独立尝试再学习，与先看示范再练习，为什么可能造成不同的后续独立能力？这种顺序效应会不会随模型持续更新而改变？</p>
<p>本篇的处理变量只有<b>尝试与正确示范的先后次序</b>。不按错误类型给失败打价值分，不训练 I6 的 Failure Value Estimator。短期分数、解法探索和长期迁移形成一条需要逐步验证的机制链，不是三个同时优化的模块。</p>
<div class="note"><b>与 I6 正交：</b><a href="idea-i6-failure-value.html">I6</a> 在固定教学顺序和方式下，比较哪条失败轨迹值得纠正；I7 固定学习材料与预算，比较先尝试和先看示范。两者共享评测基础设施，但不互为前提。</div>
"""),
        ("prior", "已有论文研究到了哪一步", """
<div class="table-wrap"><table><thead><tr><th>论文</th><th>已回答什么</th><th>I7 不能重复什么</th></tr></thead><tbody>
<tr><td><a href="https://doi.org/10.3102/00346543211019105" target="_blank" rel="noopener noreferrer">Sinha &amp; Kapur · Review of Educational Research 2021</a></td><td>53 项研究、166 组比较：在概念知识与迁移指标上，先解题后教学（PS-I）总体优于先教学后解题（I-PS），g = 0.36；程序性知识的汇总差异则不显著。存在任务和学习者边界。</td><td>不能再把“先试错通常更好”直接当成新发现。</td></tr>
<tr><td><a href="https://ijcai.org/proceedings/2015/614" target="_blank" rel="noopener noreferrer">Najar et al. · IJCAI 2015</a></td><td>按学生先前需要多少帮助，动态决定给完整例题、渐隐例题或自主解题。</td><td>简单按正确率/帮助次数分流已经有直接前作。</td></tr>
<tr><td><a href="https://doi.org/10.1109/TLT.2019.2896080" target="_blank" rel="noopener noreferrer">Chen et al. · IEEE TLT 2020</a></td><td>将正确例题、错误例题与自主解题作为可自适应选择的学习活动。</td><td>换成 LLM 四选一教学活动本身不是充分的新颖性。</td></tr>
<tr><td><a href="https://doi.org/10.1007/s10648-025-09993-3" target="_blank" rel="noopener noreferrer">He et al. · Educational Psychology Review 2025</a></td><td>在两个先验知识不同的群体中观察到相反的顺序优势，作者并未证明差异由先验知识单独造成。</td><td>不能武断地说“弱模型先示范、强模型先尝试”。</td></tr>
<tr><td><a href="https://doi.org/10.1007/s11251-020-09528-z" target="_blank" rel="noopener noreferrer">Hartmann et al. · Instructional Science 2021</a></td><td>区分亲自尝试与观察他人失败；准备性学习效果不一定来自自己先失败。</td><td>必须区分“亲自试过”与“额外看过一段失败解法”。</td></tr>
</tbody></table></div>
<p>以上是人类学习/教学系统证据，不等价于 LLM 参数更新的因果效果。I7 的新问题必须落到<b>更新后的模型在没有教师时还能做什么</b>。</p>
"""),
        ("mechanism", "Challenge → Insight → Design", """
<div class="table-wrap"><table><thead><tr><th>Challenge · 难在哪里</th><th>Insight · 为什么值得研究</th><th>Design · 怎样解决</th></tr></thead><tbody>
<tr><td>看了示范后正确率更高，可能只是照着答案复现；先试后学的收益又可能仅来自多思考了一次。</td><td>当前表现与真正形成的独立能力不同；顺序必须通过<b>撤掉示范后的持久更新</b>衡量。</td><td>同一检查点做两个随机分支，教师内容、token、训练器、学习步数对齐；清空上下文后用新题后测。</td></tr>
<tr><td>两种顺序短期正确率相近，也可能让模型以后更容易或更难自主找到新解法。</td><td>示范优先可能快速集中概率质量；先尝试可能先激活多条候选路径。但两种方向都只是待检验假设。</td><td>测 pass@1 / 固定 k 的 pass@k、有效不同解法数量、正确路径分布，而不是把无效的多样性当进步。</td></tr>
<tr><td>某一轮有效的顺序，可能在多轮自我改进后不再有效。</td><td>一次教学改变模型内部状态，因而可能改变下一轮适合的学习顺序。</td><td>固定后续任务流，在多次版本更新后测试迁移与旧能力保持；先建立顺序效应，再考虑事前选择器。</td></tr>
</tbody></table></div>
"""),
        ("design", "两条学习顺序：只改变先后，不改变教材", """
<div class="card-grid"><article class="research-card"><b>A · Instruction First</b><h3>先学再做</h3><p>展示同一完整例题与关键步骤 → 再让模型独立完成等价练习 → 统一更新 → 关掉示范、独立后测。</p></article><article class="research-card"><b>B · Problem Solving First</b><h3>先做再学</h3><p>先允许同预算独立尝试 → 展示与 A 完全相同的教师例题 → 统一更新 → 关掉示范、独立后测。</p></article></div>
<p><b>要控制的变量：</b>原始模型检查点、知识点和任务配对、相同正确示范、教师调用次数、训练 token 与更新步数、采样/温度、后测题和外部工具。报告尝试轨迹长度不齐造成的残余预算差异，额外做计算量严格匹配试验。</p>
<p><b>一个容易漏掉的陷阱：</b>不能先让模型在<b>目标题</b>上做一次诊断，再根据这次尝试决定它是否应该“先尝试”。因为诊断本身已经构成处理。事前顺序选择必须基于此前的题目历史或独立诊断题，不能泄漏目标题的先试轨迹。</p>
<p><b>学习载体：</b>首选固定 LoRA 或同一外置技能写入器，分别报告；一次在上下文里读到答案不叫 RSI。学习后清空上下文，冻结独立测试。</p>
"""),
        ("eval", "决定性实验：短期表现相近，未来能力是否不同？", """
<div class="flow"><div><b>同版随机分叉</b><small>两种学习顺序</small></div><div><b>固定学习更新</b><small>等教师信息、等预算</small></div><div><b>即时无提示后测</b><small>新题 pass@1 / pass@k</small></div><div><b>多轮后测</b><small>正确解法覆盖与迁移</small></div><div><b>顺序选择</b><small>仅在可复现异质性后尝试</small></div></div>
<p><b>P0：</b>先在一类多步骤数学题上，从同一检查点建立“先看再做 / 先做再看”配对分支。前测、近迁移与结构变形题分开；用固定 k 和固定推理预算评估不同且<b>正确</b>的解法路径。按知识点为统计单位而非题目重复采样次数。</p>
<p><b>机制区分：</b>如果 A 的 pass@1 升高、B 的 pass@k 或正确解法覆盖扩大，需要再检验是否源于采样温度、示范污染或有效样本数不同；多样性变大但正确率下降不能称探索改进。</p>
<p><b>长期检验：</b>继续以冻结任务序列更新多个版本，比较新任务迁移、旧能力回归及学习效率曲线。实验前定义“长期”为经历了多少次<b>新学习更新</b>，不是静态等待多少天。</p>
<p><b>选择策略作为第二阶段：</b>只有不同任务或学习者状态出现稳定的最佳顺序切换，且事前信号可预测时，再用历史状态训练轻量顺序选择器，与固定 A、固定 B、简单按正确率规则和普通 contextual bandit 同预算比较。</p>
"""),
        ("gate", "什么时候值得继续做成一篇 RSI 论文", """
<p><b>继续：</b>两种顺序在匹配预算下，对独立更新后的能力出现稳定差异，并且这种差异不能仅由额外练习、教师信息量、采样长度解释；至少有一个关于探索空间或后续轮次迁移的独立、可复验发现。</p>
<p><b>缩题：</b>若只发现短期迁移差异，则只报告有边界的顺序效应；没有可预测的异质性就不强行引入 Router。</p>
<p><b>停止：</b>在清空教师上下文、等学习预算后，先后顺序完全不影响独立能力；或任何优势都可由重复采样数量解释。</p>
<div class="links"><a class="link-btn" href="ideas.html">返回研究候选池</a><a class="link-btn" href="idea-i6-failure-value.html">查看正交方向 I6：错误学习价值</a><a class="link-btn" href="learning-science.html">学习科学基础</a></div>
""")
    ]
}
