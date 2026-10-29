"""I1–I14 research registry: preserve the dated I1–I13 rankings; I14 awaits scoring.

All rankings are editorial judgments, not experimental findings or acceptance odds.
"""
from html import escape
from json import loads
from pathlib import Path

folder = Path(__file__).parent
ideas = {}
for name in ("idea-prioritization-a.json", "idea-prioritization-b.json"):
    ideas.update({int(k): v for k, v in loads((folder / name).read_text(encoding="utf-8")).items()})

SCIENCE = [12, 8, 9, 10, 13, 5, 11, 6, 4, 2, 1, 3, 7]
FEASIBILITY = [7, 6, 10, 8, 11, 3, 1, 9, 4, 12, 2, 13, 5]
INVESTMENT = [8, 10, 12, 9, 11, 6, 13, 7, 4, 3, 1, 2, 5]
assert set(SCIENCE) == set(FEASIBILITY) == set(INVESTMENT) == set(ideas) == set(range(1, 14))  # Historical I1–I13 ranking snapshot
esc = escape

def idea_link(i):
    v = ideas[i]
    return '<a href="' + esc(v["href"], quote=True) + '">I' + str(i) + ' · ' + esc(v["name"]) + '</a>'

actions = {
    8: "主攻：规则正负迁移的受控 P0",
    10: "并行：区分性样本 2×2 P0",
    12: "先修补偿后第二阶段学习曲线",
    9: "不同学习历史 × 后续 C 关系",
    11: "反馈展示 → 自评 → 学习动作",
    6: "同题同错，只换失败轨迹",
    13: "先收窄跨代安全风险与误拒",
    7: "严格同信息、交换先后",
    4: "对照有/无诊断性的重试",
    3: "MIR 和混合规则强基线",
    1: "超越固定成本阈值的存放取舍",
    2: "先证明真实学生回应增量",
    5: "四模型合格再十模型",
}
rows = []
for rank, i in enumerate(INVESTMENT, 1):
    v = ideas[i]
    rows.append(
        '<tr><td><strong>' + str(rank) + '</strong></td><td>' + idea_link(i)
        + '<br><small>' + esc(v["question"]) + '</small></td><td>'
        + str(SCIENCE.index(i) + 1) + '</td><td>' + str(FEASIBILITY.index(i) + 1)
        + '</td><td><a href="#idea-' + str(i) + '">' + esc(actions[i]) + '</a></td></tr>'
    )

rows.append('<tr><td><strong>待排序</strong></td><td><a href="learning-rule-evolution.html">I14 · 学习规则自进化</a><br><small>相同学生、数据、顺序与预算，学习目标/更新规则改变是否提升未来C真实学习？</small></td><td>待评估</td><td>待评估</td><td><a href="#idea-14">P0 学法差异；P1 元规则冻结/重置</a></td></tr>')

sections = [
("decision", "当前立项建议", '''
<div class="decision"><span class="kicker">RSI IDEA PORTFOLIO · 2026-10-29 · RESEARCH JUDGMENT</span>
<h3>I8 主攻，I10 并行；I12 与增强版 I9 先验证科学现象</h3>
<p><a href="i8.html"><strong>I8</strong></a> 研究纠错何时改变共同规则，<a href="idea-i10-learning-novelty.html"><strong>I10</strong></a> 研究新增例子何时提供可吸收的区分信息。这两项可共用规则生成、真实更新与跨题迁移平台，但干预变量须分开。</p>
<p><a href="idea-i12-prerequisite-bottleneck.html"><strong>I12</strong></a> 需要证明补前置知识改变第二阶段学习增益；<a href="idea-i9-practice-switching.html"><strong>I9</strong></a> 需要证明训练历史改变后续 C 的学习曲线。<a href="idea-i11-emotional-rsi.html">I11</a> 可轻量并行，I6/I7 先做小型受控检验，I2/I5 只运行资格实验。</p>
<p><b>I13 的最新口径：</b>以候选更新的跨版本安全风险、独立验收、危险更新漏放与安全更新误拒为中心；既不让候选 Agent 改写安全硬门，也不把 I1 的存放方式选择当成 I13 的全部新颖性。</p>
<p><b>I14 已正式编号，历史排名暂不调整：</b><a href="learning-rule-evolution.html">I14 · Learning Rule Evolution</a> 基于Hattori 2023的快/慢干预与DiscoRL 2025的更新目标生成，固定学生、训练材料与顺序，只改变更新规则η。该项的科学上限和完成把握<b>尚未在同一评分口径下评估</b>，本轮不凭印象加入旧名次。P0/P1需胜过最佳固定规则和随机历史并结算元发现成本；若失败，允许缩题或降级合并。</p>
<p><b>证据状态：</b>原 I1–I13 两份排名保留为2026-10-29的编辑判断；I14正式进入研究池但尚待评分。名次不是录用概率，也不代表完成训练。<a href="ideas.html">查看 I1–I14 的研究定义 →</a></p></div>
'''),
("ranking", "三张排序表合在一起读", '''
<p><b>科学上限</b>衡量在核心机制成立、排除最近邻解释时可形成多强的科学论文；<b>完成把握</b>衡量在现有资源下取得可复现、可解释证据的可行性。综合顺序不是两个名次相加，另外纳入实验平台复用、近邻占位与研究周期。</p>
<div class="table-wrap"><table><thead><tr><th>投入顺序</th><th>原方案与唯一问题</th><th>科学上限名次</th><th>完成把握名次</th><th>下一步</th></tr></thead>
<tbody>''' + ''.join(rows) + '''</tbody></table></div>
<p><strong>科学问题与投稿上限（历史 I1–I13）：</strong>''' + ' ＞ '.join('I' + str(i) for i in SCIENCE) + '''。</p>
<p><strong>有限资源下完成决定性证据的把握（历史 I1–I13）：</strong>''' + ' ＞ '.join('I' + str(i) for i in FEASIBILITY) + '''。</p>
<div class="note">相邻名次不宜过度精确化。容易跑完程序不等于容易中稿；顶刊已有现象只能作为研究动机，不能替代 LLM RSI 的真实证据。本页若发现新强近邻、预实验无效或算力不可承受，应主动重排。</div>
'''),
("criteria", "影响中稿与完成的评审准则", '''
<div class="table-wrap"><table><thead><tr><th>考察因素</th><th>关键问题</th><th>常见减分原因</th></tr></thead><tbody>
<tr><td>近邻与剩余新颖性</td><td>最近邻真的没回答哪个可证伪问题？</td><td>把已有课程、记忆、重放、互教或安全门改名</td></tr>
<tr><td>科学解释能力</td><td>能否提前预测正效应、无效、负效应或反转？</td><td>只在结果出来后解释平均分</td></tr>
<tr><td>论文证据结构</td><td>现象、控制、机制干预、迁移价值能否形成因果链？</td><td>加很多模块，却无法证明必要性</td></tr>
<tr><td>实验可控性</td><td>一个变量能否准确被操纵，规则和正确答案是否可验证？</td><td>信息量、训练步数、教师质量与处理变量混杂</td></tr>
<tr><td>资源与模型要求</td><td>是否可用小模型先验证？会不会发生组合爆炸？</td><td>多重教师/学生/伙伴/更新动作同时变化</td></tr>
<tr><td>稳定与外推</td><td>规则族、模型快照、训练种子上的作用是否稳定？</td><td>同题多次采样当成独立训练重复</td></tr>
</tbody></table></div>
<p>严格区分<strong>当前任务更会做</strong>、<strong>撤掉帮助后持久能力增强</strong>、<strong>改进器自身跨任务变得更会改进</strong>三个尺度。第三层需要固定任务 Agent，比较新旧元策略在相同初始条件和任务流中的作用。</p>
'''),
("literature", "Nature／Science／NC 与顶会可迁移的实验设计", '''
<div class="table-wrap"><table><thead><tr><th>原始研究</th><th>值得借鉴的实验辨别逻辑</th><th>对应</th></tr></thead><tbody>
<tr><td>The mosaic memory of large language models [[M17]] · NC 2026</td><td>区分表面重复、语义相似和真正获得新规则。</td><td>I8 / I10</td></tr>
<tr><td>Compressive learning scaffolds higher-order network structure [[E401]] · NC 2026</td><td>预学习与后续学习拆成两阶段，测后续新增收益。</td><td>I12</td></tr>
<tr><td>Humans and neural networks show similar patterns of transfer and interference [[E100]] · NHB</td><td>A→B→A，同时测新知识迁移与旧规则干扰。</td><td>I3 / I8 / I9</td></tr>
<tr><td>A recurrent network model of planning... [[E355]] · Nature Neuroscience 2024</td><td>相同rollout数量随机化发生时机使奖励下降；借鉴为I4/I6的采样时机对照，不把隐藏状态优化误写成持久参数更新。</td><td>I4 / I6，参考I9 / I13</td></tr>
<tr><td>Hypothesis testing governs strategic motor learning [[E26]] · npj 2026</td><td>比较预测相同与预测不同的竞争假设试验。</td><td>I4 / I6 / I8</td></tr>
<tr><td>Distorted learning from local metacognition [[E29]] · NC 2025</td><td>真实能力不变时操纵反馈展示，分开自评与表现。</td><td>I11</td></tr>
<tr><td>The Geometry of Sequential Learning [[M18]] · ICML 2026</td><td>检验顺序效应是否能被更新几何与局部关系解释。</td><td>I9</td></tr>
<tr><td>SOAR [[S47]] · ICML 2026</td><td>已有学生真实学习收益驱动教学；需证明额外变量。</td><td>I2 / I6 / I12</td></tr>
<tr><td>Human-like systematic generalization [[E350]] · Nature 2023</td><td>将未见组合泛化与原任务记忆/纠正分开。</td><td>I8 / I10</td></tr>
<tr><td>Loss of plasticity in deep continual learning [[M22]] · Nature 2024</td><td>用下一任务等预算学习曲线测未来可学习性。</td><td>I9 / I13</td></tr>
<tr><td>Practice Makes Unsafe [[S451]] 与 Safety Must Survive Self-Improvement [[S450]] · 预印本</td><td>固定候选自改进、实际部署版本及后代风险，双侧报告漏放和误拒。</td><td>I13</td></tr>
</tbody></table></div>
<p>这里借鉴的是<strong>控制变量与证据结构</strong>，不将人类或动物学习结论外推为 LLM 已经具备的机制。参考文献发表状态、官方链接和核验深度见 <a href="references.html">来源台账</a>。</p>
'''),
("contract", "十四项共用的受控实验契约", '''
<ol class="research-steps">
<li><b>冻结同一父版本。</b>记录模型、Skill、Memory、Harness、优化器、教师与版本化评测；明确本轮更新了什么。</li>
<li><b>P0 只改变一项关键变量。</b>相同答案、题数、训练 token/FLOPs、教师信息与工具调用；额外探测、分支失败和回退成本全部计入。</li>
<li><b>优先使用可验证任务。</b>以明确规则和程序/数学验证器形成机制反事实，再扩到真实任务；Judge 分歧单独核查。</li>
<li><b>撤辅独立后测。</b>原题、异表面同规则、同表面不同规则、旧能力保持及下一任务学习曲线分开报告。</li>
<li><b>配齐强简单对照。</b>随机、均匀、固定阈值、置信度、常用重放/课程/路由与对应最接近论文；不能只比弱基线。</li>
<li><b>跨规则族和训练种子重复。</b>主要置信区间按规则族/独立训练计算；同题重复采样不可当成独立实验。</li>
<li><b>预定义 Go / Merge / Stop。</b>核心现象不成立就收缩主张；简单对照同效就不继续堆元控制器。</li>
</ol>
<p>资源紧张时先用可训练小模型与两个规则族完成代码路径和方差评估，再决定扩大模型/种子规模。不同时启动十四项完整 RSI 闭环。</p>
'''),
]
for i in range(1, 14):
    v = ideas[i]
    sections.append((f'idea-{i}',
      f'I{i} · {v["name"]}｜科学上限 #{SCIENCE.index(i)+1} · 完成把握 #{FEASIBILITY.index(i)+1}',
      '<div class="idea-focus"><p><b>唯一科学问题：</b>' + esc(v["question"]) + '</p></div>'
      + '<div class="idea-steps">'
      + '<div class="idea-step"><h3>P0 · 决定性对照</h3><p>' + esc(v["p0"]) + '</p></div>'
      + '<div class="idea-step"><h3>最强控制</h3><p>' + esc(v["control"]) + '</p></div>'
      + '<div class="idea-step"><h3>Go · 决定升级的证据</h3><p>' + esc(v["gate"]) + '</p></div>'
      + '<div class="idea-step"><h3>最近邻与中稿风险</h3><p>' + v["risk"] + '</p></div>'
      + '</div><p><a href="' + esc(v["href"], quote=True) + '">返回 I' + str(i) + ' 详细研究页 →</a></p>'))
sections.append(('idea-14', 'I14 · 学习规则自进化｜科学上限与完成把握待统一评估', '''
<div class="idea-focus"><p><b>唯一科学问题：</b>固定学生模型检查点、学习任务/材料/顺序/教师及预算，仅改变由历史真实学习收益积累的更新规则 η，能否让相同起点学习者在未见C任务上取得更好的持久净学习收益？</p></div>
<div class="idea-steps"><div class="idea-step"><h3>P0 · 决定性现象</h3><p>同样数据、同样课程顺序，比较固定SFT、保持旧能力的约束更新与目标生成式更新；匹配当前A/B能力及C前测，真实继续学习C并报告全曲线AULC。允许零效果和反向效果，不根据结果事后挑选模型快照。</p></div><div class="idea-step"><h3>最强对照</h3><p>Fixed Best Rule、Old/New Meta-Rule、打乱历史、无任务学生更新；相同θ₀和优化器状态，计入Meta训练、选择与验证全部成本。与I9仅改训练顺序严格区分。</p></div><div class="idea-step"><h3>Go / 缩题 / 降级</h3><p>只有冻结/重置实验支持学习规则本身的可继承净收益、并在未见规则族与模型快照上优于强固定规则，才继续投入完整元规则训练。若解释仅为训练历史或课程安排，降级并入I9或保留机制测量；如复杂Meta与固定规则同效，停止增加模块。</p></div><div class="idea-step"><h3>最近邻与论文依据</h3><p><a href="reading-notes.html#deep-hattori-ofc-metarl-nn2023">Hattori 2023</a> 验证快/慢机制与阶段干预；<a href="reading-notes.html#deep-discorl-nature2025-oh">DiscoRL 2025</a> 已研究自动学习目标生成。不能把两个循环本身当成首次提出。</p></div></div>
<p><a href="learning-rule-evolution.html"><b>进入 I14 完整研究与 P0/P1 →</b></a></p>
'''))
sections.extend([
("execution", "实际推进与何时重新排序", '''
<div class="table-wrap"><table><thead><tr><th>研究组</th><th>本轮动作</th><th>停止继续堆叠模块的条件</th></tr></thead><tbody>
<tr><td>主攻</td><td><a href="#idea-8">I8</a> 规则迁移与负迁移；<a href="#idea-10">I10</a> 规则区分信息 2×2。</td><td>在至少两个独立规则族中没有可重现差异，或效应完全由信息量解释。</td></tr>
<tr><td>高上限 P0</td><td><a href="#idea-12">I12</a> 第一阶段 P → 第二阶段 T；<a href="#idea-9">I9</a> A/B 历史 → C 学习曲线。</td><td>后续收益完全由第一阶段起点、优化器状态或筛选偏差解释。</td></tr>
<tr><td>轻量并行</td><td><a href="#idea-11">I11</a> 反馈自评链；<a href="#idea-6">I6</a> 轨迹配对；<a href="#idea-7">I7</a> 同信息顺序。</td><td>只出现即时回答或自评变化，无法证明持久独立学习。</td></tr>
<tr><td>储备／收窄</td><td><a href="#idea-13">I13</a> 跨代安全风险；I1/I3/I4 补强对照；I2/I5 先资格实验。</td><td>固定门、固定老师或简单互教已经等效，复杂层没有增量。</td></tr>
<tr><td>新增编号待评分</td><td><a href="#idea-14">I14</a> 更新规则自进化，先做固定学生、相同教材/预算的P0。</td><td>若Meta规则与最佳固定Rule同效、或只提升当前任务分数，缩题/降级；不直接投入大规模Meta-gradient。</td></tr>
</tbody></table></div>
<p><b>重排依据：</b>新近邻、P0 效应规模/重复性、实际计算成本和能否解释反例。任何图表的视觉吸引力都不改变证据级别。</p>
'''),
("state", "状态、编号与引用边界", '''
<p><b>2026-10-29 · 研究方案排序，非已完成实验。</b>现有 I1–I13 编号保持不变，<b>I14 已正式追加为学习规则自进化</b>；I14 暂未进入历史13项名次，待P0结果或同口径评估后排序。当前 I6 是失败轨迹的学习价值（旧跨轮瓶颈切换仅留归档）；I9 为课程切换与未来学习历史的增强版；I10 已有规则区分和组合学习详情；I13 采用跨版本安全接纳主线。所有新机制、P0 与主张均待真实验证。</p>
<p>本页的原始论文依照 <a href="references.html">站内逐条核验来源</a>标注；“论文原始发现”不等于“我们实验已得到同样结果”。优先级可在新证据到来后修改，保留研究过程与排序理由。</p>
''')
])
PAGE = {"slug":"idea-prioritization",
        "title":"I1–I14 · 科学上限、完成把握与实验优先级",
        "en":"Scientific Ceiling, Feasibility and Experiment Gates",
        "lead":"I1–I14 研究决策：保留原 I1–I13 双排名快照，I14 已正式编号并列出 P0/P1 与降级标准，但科学上限和可行性待同口径评分。所有结果尚待真实训练验证。",
        "updated":"2026-10-29", "sections":sections}
