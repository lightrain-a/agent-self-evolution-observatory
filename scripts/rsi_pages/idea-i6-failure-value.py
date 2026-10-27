"""I6 research card: failure value, deliberately independent from learning order."""
PAGE = {
    "slug": "idea-i6-failure-value",
    "title": "I6 · 为什么有些错误更值得学习？",
    "en": "Not All Failures Are Equally Learnable",
    "lead": "同一道题、同样答错，失败轨迹却可能具有不同的后续学习价值。只研究错误的学习收益，不改变先做还是先学的顺序。",
    "updated": "2026-10-27",
    "sections": [
        ("question", "一句话科学问题", """
<p class="thesis"><b>I6：</b>同一模型面对同一道题，甚至最终给出相同的错误答案，却可能经历不同的失败过程。为什么使用其中一条失败轨迹纠错，比使用另一条更能帮助模型在后续独立解题时进步？</p>
<p>这里的“学习”必须对应可持续的参数或外置技能更新，之后撤掉原题答案与教师提示再测新题；单次纠错后能复述答案不算学会。</p>
<div class="note"><b>研究边界：</b>本篇只改变提供给固定学习器的<b>失败轨迹</b>，固定教学顺序、反馈形式、示范信息、更新器和训练预算。<a href="idea-i7-learning-order.html">I7</a> 才研究“先看示范还是先自主尝试”，不把两者塞入同一个 Router。</div>
"""),
        ("observation", "一个可观察的现象", """
<div class="card-grid"><article class="research-card"><b>轨迹 A · 直接猜错</b><h3>没有形成有效中间过程</h3><p>模型面对一道多元积分题，直接套用错误公式，给出错误结果。</p></article><article class="research-card"><b>轨迹 B · 尝试后答错</b><h3>形成部分有效步骤</h3><p>同一模型在同题上尝试坐标变换、检查边界，却最终仍得到相同的错误结果。</p></article></div>
<p>两条轨迹从同一个模型检查点产生，问题与最终答案都一致。假设分别用它们作为学习材料，且获得<b>相同正确解法与等预算更新</b>，模型在新积分题上的收益仍可能不同。这是<b>待验证现象</b>，并不是断言 B 一定优于 A。</p>
<p><b>与 I8 不同：</b><a href="i8.html">I8</a> 以高置信度错误、前置知识与规则适用范围为切口，解释什么错误规则经纠正后能够跨题迁移；I6 则尽量固定题目和错误结果，只比较<b>不同失败过程本身</b>作为纠错材料的增量学习收益。高置信度与规则范围不作为 I6 的主要处理变量。</p>
"""),
        ("reason", "先解释原因，再定义模块", """
<div class="table-wrap"><table><thead><tr><th>Challenge · 难在哪里</th><th>Insight · 为什么可能解决</th><th>Design · 如何验证</th></tr></thead><tbody>
<tr><td>当前正确率只能告诉我们“没做对”，不能告诉我们一次纠错将改变多少未来能力。</td><td>错误过程可能暴露已具备的子步骤、错误的知识规则以及缺口与其他题的共享程度。</td><td>先随机抽取失败轨迹，采用固定纠错程序逐条更新；再用未见题的独立增益为每条失败定价。</td></tr>
<tr><td>失败轨迹越长、越接近答案、越自信，可能只是更耗 token 或原本更接近正确。</td><td>学习价值应由更新后的因果收益定义，不能由“表面离正确答案多远”替代。</td><td>匹配题目、初始检查点、错误长度、教师反馈、更新步数与评测；增加错误严重度、置信度、语义相似度强基线。</td></tr>
<tr><td>纠正同一道题不代表学会同一规则，更不代表跨任务迁移。</td><td>某条轨迹可改写只针对原题的模式，也可能揭示跨题共用的推理规则。</td><td>把原题重做、同模板新题、结构变形题和旧能力回归分开统计，并评估多个后续更新之后是否保持。</td></tr>
</tbody></table></div>
<p><b>方法只放最必要的部分：</b>先用标准化纠错更新建立每条失败的实际学习价值，再训练一个轻量 Failure Value Estimator。预测器只能读取<b>纠错前</b>的轨迹特征与历史，不得偷看纠错答案或最终后测。</p>
"""),
        ("protocol", "最小辨别实验：同题、同反馈、不同错误", """
<div class="flow"><div><b>冻结学习者版本</b><small>同模型与参数检查点</small></div><div><b>同题采集失败轨迹</b><small>多种随机种子，先核实均错误</small></div><div><b>固定纠错更新</b><small>同一个教师答案 / LoRA 配置</small></div><div><b>无提示后测</b><small>新题迁移、旧能力回归</small></div><div><b>学习价值分析</b><small>解释差异与事前预测</small></div></div>
<p><b>P0：</b>先选一个数学任务族及一组跨题共享规则，收集同一检查点在同一道题上的多条自然失败轨迹。随机指定某条失败轨迹为学习材料；另一分支只读正确解法作基线。每个分支从<b>同一初始检查点</b>重新开始，而不是顺序累积训练。</p>
<p><b>配对控制：</b>优先匹配同一目标题、同一错误终点与已知错误规则，只让失败轨迹的中间过程不同；固定教师正确解法、训练器、token 上限、学习率、更新步数和测试集，并对轨迹长度/额外解释文本做预算敏感性分析。保留“只看答案”“随机失败”“按置信度选错误”“按答案距离选错误”等对照。</p>
<p><b>定义：</b>G(f)=Acc_after(f, D_holdout) − Acc_before(D_holdout)，并同时报告相对于“只看正确解法”的增量；D_holdout 按知识点与模板去重。分层估计同题组内的学习收益差，不把一题上的多个 Probe 当成独立样本。</p>
<p><b>下一步：</b>用不同题/不同模型上的纠错前轨迹预测 G(f)，比较随机选错误、按难度/置信度/长度选错误与收益预测选择；报告预算相同时的迁移增益和选择 regret。</p>
"""),
        ("related", "最近邻：做到了哪里、我们还要回答什么", """
<div class="table-wrap"><table><thead><tr><th>相关工作</th><th>已研究的关系</th><th>I6 的独立问题</th></tr></thead><tbody>
<tr><td><a href="i8.html">I8：高置信度错误与规则级迁移</a></td><td>针对错误的知识准备程度、规则覆盖范围以及持久更新后的跨题净收益。</td><td>固定题目与错误终点，仅研究<b>失败轨迹过程</b>是否提供额外有用信息。</td></tr>
<tr><td><a href="https://aclanthology.org/2024.acl-long.45/" target="_blank" rel="noopener noreferrer">Learn from Failure · ACL 2024</a></td><td>形式定理证明中，失败搜索轨迹可成为有价值的训练数据。</td><td>不是证明失败“可以用”，而是研究<b>哪条失败更值得用</b>。</td></tr>
<tr><td><a href="https://arxiv.org/abs/2610.13594" target="_blank" rel="noopener noreferrer">MENTOR: Learning from Failure with On-Policy Pedagogical Intervention · 2026 预印本</a></td><td>训练停滞时依据失败原因生成教学提示，帮助恢复学习信号。</td><td>固定教学方式后，仅比较失败轨迹本身的可学习价值，避免归功于更好的提示。</td></tr>
<tr><td><a href="references.html#E08">Productive / Unproductive Failure 学习科学文献</a></td><td>失败及其后续整合可能有不同教学结果。</td><td>把启发转为可审计的模型更新与无教师后测，不声称人类结论自动迁移到 LLM。</td></tr>
</tbody></table></div>
<p class="status">文献证据支持研究动机；同题失败价值差异、预测有效性和跨模型迁移尚待本项目验证。</p>
"""),
        ("gate", "怎样决定继续还是停止", """
<p><b>继续：</b>匹配题目、示范与计算预算后，失败轨迹之间仍有可重复的迁移增益差异；简单的错误严重度、置信度、轨迹长度无法解释全部差异；预测器在未见任务上能减少同预算的错误选择。</p>
<p><b>缩题：</b>只发现纠错收益差异而无法事前预测时，优先做现象与机制分析，不夸大为学习策略优化系统。</p>
<p><b>停止：</b>不同错误的差异在同反馈/同预算后消失，或只在原题重复出现、撤掉教师后失效。</p>
<div class="links"><a class="link-btn" href="ideas.html">返回研究候选池</a><a class="link-btn" href="idea-i7-learning-order.html">查看正交方向 I7：学习顺序</a><a class="link-btn" href="experiments.html">通用实验隔离契约</a></div>
""")
    ]
}
