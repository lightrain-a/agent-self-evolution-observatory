"""Unnumbered RSI idea candidate: diagnose what training signal is missing at a high-skill plateau."""
PAGE = {
 "slug":"learning-signal-bottlenecks",
 "title":"研究候选 · 高能力平台期，什么时候应该改变学习信号？",
 "en":"Learning-Signal Bottlenecks at the Edge of Expertise",
 "lead":"当模型在常规练习下已经很强，却总在细小规则条件上犯错，继续增加训练量是否还有效？先确认真实平台和可独立诊断的基础能力缺口，再比较改变学习目标、辨别训练及反馈是否能带来无提示的新题净收益。",
 "updated":"2026-10-29",
 "sections":[
 ("phenomenon","Observable Phenomenon｜已经会做大部分题，为什么还学不会剩下的细微区别？",'''
<div class="decision"><span class="kicker">UNNUMBERED RSI IDEA · SIGNAL / DIAGNOSIS / EXPERT PLATEAU</span><h3>When Does a Better Learning Signal Beat More Practice?</h3>
<p>一个Agent对常见工具调用或组合规则题已有很高正确率，连续补充相似训练样本后，仍反复混淆某个对象的身份、权限角色或推理方向。我们要先问：这是真正的训练平台，还是采样太少？如果确实已接近平台，哪些<b>可单独测量的基础辨别能力</b>仍缺失？训练它会不会比继续练最终任务更有效？</p>
<p><b>Science Advances 2020 的人类实验：</b>专业钢琴家通过带对错反馈的主动触觉辨别训练，改善了特定低力度按键控制，而普通目标按键误差练习在该剂量下未改善专家的表现；没有证明任意高水平学习者只要更换奖励就能提高所有技能。[[E380]]</p>
<p class="status">状态：独立候选 / 未占用新的I编号 / 未进行本站LLM训练。所有 P0 参数、监督强度与模型选型均为待核验方案。</p></div>
'''),
 ("mechanism","Why｜瓶颈可能不在执行能力，而在训练反馈不能揭示哪个条件错了",'''
<div class="table-wrap"><table><thead><tr><th>表现近似“平台”的三种情况</th><th>缺失的可能是什么</th><th>不该直接做什么</th></tr></thead><tbody>
<tr><td><b>Expert residual errors</b> · 大部分已会，但稳定错特定细微条件</td><td>对象/关系/数值范围的判别和反馈解释能力</td><td>不做诊断就追加千条同类成功例题</td></tr>
<tr><td><b>Sparse reward</b> · 难题几乎从未完成</td><td>可成功学习的中间问题或必要前置知识</td><td>把缺成功轨迹说成“专家已经达到上限”；SOAR已经覆盖相关方向 [[S47]]</td></tr>
<tr><td><b>Shortcut mastery</b> · 原训练题全对，未见冲突题错</td><td>能排除竞争捷径的训练例子</td><td>误将课题归为反馈粒度；<a href="idea-i10-learning-novelty.html">I10</a>直接研究这一变量</td></tr>
</tbody></table></div>
<p><b>可证伪的机制判断：</b>在某些接近平台的学习者中，直接执行目标任务的结果反馈已难以触发修复，但相关二择辨别任务能训练其尚未精确表示的基础条件。若这种缺口在训练前不能测出来，或者更新后仅记住辨别题却不会真正执行，机制就不成立。</p>
<p>2024年同组 <i>iScience</i>（120名钢琴家）进一步将机制指向主动运动探索、肌肉协调和预测性感觉整合；不能将2020研究简化成“感官更敏锐→运动必然提高”的唯一中介。[[E381]]</p>
'''),
 ("closest","Closest Related Work｜哪些“换学习信号”的形式早已有先例？",'''
<div class="table-wrap"><table><thead><tr><th>工作</th><th>某工作研究的是……</th><th>我们希望研究的是……</th></tr></thead><tbody>
<tr><td><b>Science Advances 2020</b> [[E380]]</td><td>对高水平钢琴家，转为主动触觉二择辨别能否突破常规按键练习的短期控制瓶颈</td><td>在可验证的LLM真实参数更新中，能否事前诊断“剩余的基础辨别缺口”，再改变监督目标并产生独立泛化</td></tr>
<tr><td><b>iScience 2024</b> [[E381]]</td><td>相关主动感觉训练如何改变运动探索和感觉预测整合</td><td>哪种反馈信息最影响模型辨别和使用关键条件，而不是简单提高奖励密度</td></tr>
<tr><td><b>SOAR · ICML 2026</b> [[S47]]</td><td>在0/128成功的极难推理任务中，用真实学生进步奖励教师产生stepping-stone</td><td>当前整体已高水平、但有系统细微错误时，基础辨别信号和目标任务直接练习有何差别</td></tr>
<tr><td><b>Hypothesis Testing · npj 2026</b> [[E26]]</td><td>人类局部运动策略与可迁移规则可以不同，练习结构影响哪种假设被验证</td><td>在相同样本/规则证据下，改变反馈要求的认知操作能否另行提高参数级规则应用</td></tr>
<tr><td><b>I9 / I10 / I12</b></td><td><a href="idea-i9-practice-switching.html">I9</a>安排同样材料的顺序；<a href="idea-i10-learning-novelty.html">I10</a>选择区分性样本；<a href="idea-i12-prerequisite-bottleneck.html">I12</a>修复未知共同前置知识</td><td>固定规则、样本、顺序和更新器，只改变监督<b>目标及其反馈信息</b>；必须超出上述解释才能独立成文</td></tr>
</tbody></table></div>
'''),
 ("design","Design｜怎样让细微错误变成真正可训练的辨别任务？",'''
<p><b>先从程序可验证任务开始。</b>以工具对象身份、规则反转或符号函数组合为例，把正确目标过程与一个“只错一处”的竞争过程并排：学习者必须指出错的是哪个对象、方向或作用域，并解释可被程序验证的判别条件。训练后撤掉二择备选，重新要求完成原始任务，测未见对象是否仍做对。</p>
<div class="flow"><div><b>确认平台期</b><small>直接训练固定预算无可检测新增收益</small></div><div><b>诊断基础辨别</b><small>发现细微条件错误和难度带</small></div><div><b>构造可验证判别题</b><small>同样原始对象/规则，改变回答任务与反馈</small></div><div><b>执行真实LoRA更新</b><small>等样本、等token、等步数、等成本</small></div><div><b>撤辅独立后测</b><small>原始执行 / 未见组合 / 旧能力</small></div></div>
<div class="table-wrap"><table><thead><tr><th>状态</th><th>训练组</th><th>关键目的</th></tr></thead><tbody>
<tr><td rowspan="5">S0 初学者<br>S1 高水平但仍有可诊断残差<br>S1' 高水平且该辨别能力已掌握（阴性对照）</td><td>F0 · 常规目标任务+正确性/误差反馈</td><td>普通练习基线</td></tr>
<tr><td>F0+ · 同等额外计算的更多目标练习</td><td>排除仅因额外更新量/标签数而改善</td></tr>
<tr><td>F1 · 相关细微辨别任务+可验证正确性反馈</td><td>检验改变训练目标的作用</td></tr>
<tr><td>F1-no-FB · 相同辨别任务无正确性反馈</td><td>区分判别操作本身与反馈强化</td></tr>
<tr><td>F1-irrelevant · 难度/表面相近但无关的辨别训练+反馈</td><td>区分诊断性信号与普通辅助任务多样性</td></tr>
</tbody></table></div>
<p>如果完全固定输入材料却改变输出任务导致有效标签数量不等，需再做<b>监督token、正确信息和GPU总预算匹配</b>。不能把训练更多步骤或额外教师调用的收益解释成信号机制。</p>
'''),
 ("p0","P0｜先验证“专家×对症训练”的交互，而不是直接造新控制器",'''
<p><b>主假设：</b>在 S1 已显现直接训练平台且仍存在显著相关辨别错误时，F1 对真实目标任务的独立增益高于F0；这种优势小于或不出现在 S0 及已掌握该辨别技能的 S1'。至少覆盖多个规则族和独立随机分支。</p>
<div class="equation">Interaction = [Gain(S1,F1) − Gain(S1,F0)] − [Gain(S0,F1) − Gain(S0,F0)]</div>
<p>其中Gain在同等LoRA预算、关闭教学反馈和外部记忆后，基于未见实例的<strong>参数级能力增量</strong>，并单列旧能力回归、成本和阴性结果。不能只报告训练上的二择正确率。</p>
<div class="table-wrap"><table><thead><tr><th>阶段</th><th>决定性观察</th><th>失败时怎么判断</th></tr></thead><tbody>
<tr><td>P0A · Qualification</td><td>高水平目标任务继续直接训练的收益近零；相关辨别探针未满分</td><td>常规训练仍进步→尚未构成平台；没有基础缺口→不做F1</td></tr>
<tr><td>P0B · Pairwise LoRA</td><td>F1与F0、F0+、F1-no-FB、F1-irrelevant在未见规则题上配对增益</td><td>只有标签/token更多或简单多练有效→不独立立题</td></tr>
<tr><td>P0C · Causal ablation</td><td>训练后基础判别改善与目标能力改善均可独立观察；负对照无同样增益</td><td>判别题变强但目标任务没变→只属于新辅助任务</td></tr>
<tr><td>P1 · Wider transfer</td><td>在新规则族、新模型家族及未来C训练中仍有额外收益</td><td>只在单一模板/模型有效→不宣称普适RSI机制</td></tr>
</tbody></table></div>
'''),
 ("limits","作者实验哪些地方没有做到严格配平？这会决定我们怎样设计 P0",'''
<p><b>Exp1并非同剂量“仅更换奖励”：</b>主动触觉400个二择试次对应约800次按键，而普通重复组400次按键；任务形式、负载与反馈类型同时改变。Exp2有/无辨别正确反馈是更接近单因素的比较，但效果局限于专家训练过的无名指。Exp3让专家和新手各做100次直接运动误差练习，钢琴家p=0.95并非训练达到永久硬上限。[[E380]]</p>
<p><b>迁移与长期保持都有限：</b>30分钟复测只能证明短时间尺度上感知变化仍可观察，没有证明数月保持、未训练食指或复杂作品受益。2024后续机制研究也提示预测感觉整合改变，不宜把一项感知测量直接充当唯一中介。[[E381]]</p>
<p>所以必须建立严格配对：同一基础模型、任务根族、真实正确标签来源、更新器与优化器状态；尽量令样本、有效监督信息、更新调用和总计算相同。对于无法匹配的细节，单独报告成本敏感性而非忽略。</p>
'''),
 ("gate","何时值得成为独立 RSI Idea？",'''
<p><b>GO：</b>高水平模型的可诊断基础辨别缺口真实存在；针对性训练跨规则族地改善该缺口和撤辅后目标执行；效果不能被更多直接训练/任意辅助任务/新样本区分性/额外标签与计算解释。只有这三层都成立，才考虑预测“下一轮应该换什么学习信号”的控制器。</p>
<p><b>MERGE：</b>若主要是挑更有用的样本，归 <a href="idea-i10-learning-novelty.html">I10</a>；若主要是先补必要前置知识，归 <a href="idea-i12-prerequisite-bottleneck.html">I12</a>；若主要是先后顺序，归 <a href="idea-i9-practice-switching.html">I9</a>；若只优化更新目标函数本身，考虑并入 <a href="learning-rule-evolution.html">学习规则演化候选</a>。</p>
<p><b>STOP：</b>基础判别训练只提高二择题正确率、对原任务没有独立新题益处，或提升全由更大训练量解释。</p>
<div class="links"><a class="link-btn" href="reading-notes.html#deep-scienceadv2020-expert-haptic-ceiling-hirano">Science Advances 2020 · 十节完整精读</a><a class="link-btn" href="https://www.science.org/doi/10.1126/sciadv.abd2558" target="_blank" rel="noopener noreferrer">原论文</a><a class="link-btn" href="reading-notes.html#deep-soar-2601-18778">SOAR · ICML 2026完整精读</a></div>
<p class="status">科研候选，尚未执行LLM真实训练；当前暂不占用任何新的正式研究编号，不声称“首次用更细反馈突破模型平台”。</p>
''')
 ]
}
