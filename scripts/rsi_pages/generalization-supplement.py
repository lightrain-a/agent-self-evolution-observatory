"""Mechanism-led supplementary design for the RSI future-learnability dossier.

Separate from the reader-first review text to preserve concurrent site edits.
"""

METHOD_SECTIONS = [
        ('design-lessons', '方法学调研｜顶刊顶会怎样让一个“现象”成为有机制力度的论文？', '''
<p>这里不再重复各篇论文的摘要，而是只抽取其<strong>被操纵的变量、排除的混淆因素、用于验证机制的干预</strong>。这类“实验结构”比直接借用某个网络模块更值得迁移。</p>
<div class="table-wrap"><table><thead><tr><th>文献与原研究设计</th><th>方法为什么不止于简单A/B对照</th><th>我们的对应实验</th></tr></thead><tbody>
<tr><td><b>npj Science of Learning 2026 · Ding et al.</b><br>2个训练几何条件 + 无反馈探针；Exp2再次控制训练点与探针的距离 [[E26]]</td><td>有可能做对训练点但采取不同竞争规则；第二实验针对第一次实验里最强的替代解释</td><td><b>E0/E2</b>版本空间分歧题；在同输出格式、题长和组合深度下重做机制实验</td></tr>
<tr><td><b>NHB 2026 · Holton et al.</b><br>A→B→A、Same/Near/Far；人与逐trial匹配的线性ANN；rich/lazy学习模式干预 [[E100]]</td><td>行为效应、计算表征和主动改变学习模式形成链条；近似规则既帮助迁移又制造旧规则错用</td><td><b>E1/E2/E4</b>构造相容/冲突/无关新C，并对旧A/B回测、重置Adapter与优化器</td></tr>
<tr><td><b>NHB 2026 · Pesnot Lerousseau</b><br>重复/多样数据分布、混合分布和顺序课程三个实验 [[E360]]</td><td>区分对旧实例的记忆与对未见上下文规则的推断；先改数据统计、再单独改顺序</td><td><b>P0 与 E1 分开</b>：D/K内容干预不能混入纯顺序对照；记忆与规则指标分开</td></tr>
<tr><td><b>Nature 2024 · Dohare et al.</b><br>长期持续任务，多种网络/优化器，重新引入可更新单元等塑性控制 [[M22]]</td><td>只测旧任务遗忘不能证明还有没有能力学习新任务；需要长期曲线与反事实机制对照</td><td><b>E4/E5</b>新无关任务负控、长训练流、有效秩及新Adapter/优化器状态对照</td></tr>
<tr><td><b>ICML 2026 · Sweeney</b><br>Lie bracket预测A→B/B→A，再用多域SFT、DPO及其他模态作校验 [[M18]]</td><td>局部几何量具有明确可计算预测，直接接受对照基线检验，而非只画描述性热图</td><td><b>E2</b>以“给定C支持集时的几何预测”作为强基线；我们的无C标签状态诊断单列赛道</td></tr>
<tr><td><b>ICML 2026 · SOAR</b><br>学生真实训练收益奖励与intrinsic难度代理对照；检验训练稳定性与题目多样性 [[S47]]</td><td>教学材料评价的目标是学生实际进步，同时检查代理目标可能产生的坍缩</td><td><b>E3</b>与真实收益试训选题、QBC以及随机例题作等总成本比较</td></tr>
<tr><td><b>ICLR 2024 · Shortcut Learning</b><br>最小生成模型正交改变核心/捷径线索的可获得性与预测性</td><td>把“模型爱走捷径”转化为可操纵的任务因子，并解释架构差异</td><td><b>E0/E4</b>区分规则信息量、题面可获得性、表面多样性和真正组合覆盖</td></tr>
</tbody></table></div>
<p><b>从方法学到我们的论文叙事：</b>实验1建立不寻常的同分异学现象；实验2用分歧/边界探针给出可观察机制；实验3用随机补救改变这一机制；实验4解释替代原因和失效条件；实验5跨模型与任务族验证。如果只能做实验1和2，那适合作为<strong>现象发现的初步证据</strong>，尚不能将RCP写成验证有效的新算法。</p>
'''),
        ('paper-method', '论文级 Method｜从观察现象升级到可解释、可操纵的学习机制', '''
<div class="decision"><span class="kicker">PROPOSED METHOD · MECHANISM FIRST · NOT YET EXECUTED</span>
<h3>Rule-Contrastive Preparation &amp; Future-Learning Assay（规则对照式准备与后续学习测量）</h3>
<p><b>论文的单一主张：</b>历史训练即使带来相近的当前正确率，也可能留下不同的<strong>规则选择方式及适用边界</strong>。这些差异会影响后来学习新规则 C 的响应；有针对性地排除错误规则，可能改变这种响应。我们用<strong>规则层面的诊断 + 随机干预 + 真实参数更新</strong>检验，而不是只比较期末成绩。</p>
<div class="flow"><div><b>规则生成器</b><small>正确规则与可执行的竞争捷径</small></div><div><b>匹配历史分叉</b><small>同底座、同材料，改变顺序或信息</small></div><div><b>不反馈的规则探针</b><small>分歧、组合、适用边界</small></div><div><b>小预算针对性补救</b><small>规则分歧例 vs 表面新颖/难度/随机</small></div><div><b>新 C 真实更新</b><small>相容/冲突/无关，完整学习曲线+旧能力回归</small></div></div>
<p><b>三个有因果次序的问题：</b>Q1 同样的当前任务成绩是否隐藏不同的规则状态？Q2 这种状态和 C 的学习轨迹有何关系，能否排除梯度几何、C 前测和参数可塑性等解释？Q3 给定同样的补救预算，<strong>只改变旧任务中的规则辨别信息</strong>，能否主动改变其后的 C 学习效率？Q1 是现象、Q2 是机制鉴别、Q3 是机制干预。Q3 不成立时也应如实保留 Q1/Q2 的结论。</p>
<p><b>方法贡献的准确边界：</b>基于竞争假设选分歧样本已有 Query by Committee（<a href="https://doi.org/10.1145/130385.130417" target="_blank" rel="noopener noreferrer">COLT 1992</a>）；控制抽象特征的反事实增强已有 <a href="https://aclanthology.org/2025.findings-acl.50/" target="_blank" rel="noopener noreferrer">Findings ACL 2025</a>。本方案的潜在新增贡献不是“第一次选择反例”，而是<strong>先诊断学习者形成哪种规则，再用受控补救检验其对新规则真实学习曲线的因果影响</strong>，并将起点迁移、更新能力与旧能力回归分开。</p>
'''),
        ('method-rule-engine', 'Design 1｜可执行竞争规则图：把“会做题”与“学对规则”分开', '''
<p><b>形式化任务：</b>每个规则族用一组有限、可执行的程序组成 <code>R={r₁,…,rₘ}</code>，每道题有输入 <code>x</code>、情境 <code>c</code> 和唯一 oracle 答案 <code>r*(x,c)</code>。真实规则与至少一种竞争捷径在旧训练样本上给出相同输出，但在专门构造的输入上必须发生分歧。程序解释器只保存在实验环境/独立验证器中，不作为提示泄露给学生模型。</p>
<div class="table-wrap"><table><thead><tr><th>可直接理解的示例（列表规则）</th><th>输入与答案</th><th>实验作用</th></tr></thead><tbody>
<tr><td><b>旧训练样本</b>：保留首次出现的元素（正确）vs原样返回（捷径）</td><td><code>[2,1,3] → [2,1,3]</code></td><td>两种规则都正确，普通训练得分无法区分</td></tr>
<tr><td><b>分歧 witness</b>：只改变“是否有重复”</td><td><code>[2,1,2] → [2,1]</code>；捷径会输出 <code>[2,1,2]</code></td><td>直接排除错误规则，检验真正掌握</td></tr>
<tr><td><b>边界 witness</b>：情境切换到“保留最后一次出现”</td><td><code>[2,1,2] → [1,2]</code>（按保留元素原始位置排列）</td><td>检验是否把旧规则错用到新情境</td></tr>
<tr><td><b>无效对照</b>：重写题面、换整数，仍无重复</td><td><code>[7,4,3] → [7,4,3]</code></td><td>表面不同，但无法区分两个竞争程序</td></tr>
</tbody></table></div>
<p><b>构造方法：</b>枚举程序长度受限的候选规则，形成与当前训练集一致的版本空间 <code>V(D)={r∈R:∀(x,y)∈D,r(x)=y}</code>。从同一合法输入域选出三类测试：<b>Wsep</b>（候选规则给出不同答案）、<b>Wbind</b>（情境字段决定选择哪条规则）、<b>Wnull</b>（候选规则结果一致但文本多样）。根据 oracle 输出自动标注、检查歧义比例、题长、标签频次、规则复杂度和输入距离，不人为挑中看起来成功的题。</p>
<p><b>防止“只是更难”的混淆：</b>把规则可辨识性 D、结构组合覆盖 K、词面变化 L、A/B 相似度 S 分别作为可操作变量。匹配输入长度、表达式深度、输出格式、目标正确率区间及训练 Token；允许不同组在训练难度上仍不完全相同，但明确展示这些统计与控制，而不将其假定为相等。<a href="https://proceedings.iclr.cc/paper_files/paper/2024/hash/bf215fa7fe70a38c5e967e59c44a99d0-Abstract-Conference.html" target="_blank" rel="noopener noreferrer">ICLR 2024 Shortcut Learning</a> 已用受控生成器隔离线索的预测性与可获得性；<a href="https://www.nature.com/articles/s41539-026-00428-4" target="_blank" rel="noopener noreferrer">npj 2026 Hypothesis Testing</a> 用第二实验控制初始空间距离。我们也必须设置第二轮排除替代解释的实验。[[E26]]</p>
<p><b>数据结构可复用：</b><code>family_id, rule_id, context_id, program_ast, input, oracle_output, distractor_outputs, witness_type, surface_template, depth, split, seed</code>。训练、诊断、补救和最终C测试使用互斥输入与模板；最终留出整批<strong>规则族／组合图</strong>，而不只随机划分题面。</p>
'''),
        ('method-signature', 'Design 2｜学习者状态指纹：不用原题准确率猜测模型学到了什么', '''
<p>对于相同的历史后当前任务准确率，增加一组<strong>只做前向、不提供反馈、不更新参数</strong>的诊断。它是机制测量，不是给学习者的新课程；如果以后用诊断选补救，诊断本身的查询成本单独入账。</p>
<div class="table-wrap"><table><thead><tr><th>可观测量</th><th>计算与预期区分</th><th>证据地位</th></tr></thead><tbody>
<tr><td><b>Rule Discrimination</b></td><td><code>RD=Acc(Wsep)</code>；把正确规则与“训练数据同样能解释”的捷径分开</td><td>行为证据，不是神经表示的直接证明</td></tr>
<tr><td><b>Context Binding / Intrusion</b></td><td><code>BI=Pr(选择旧情境的规则 | Wbind中的新情境)</code>，同时记录反向错用</td><td>区分旧规则遗忘与新旧规则适用域混淆</td></tr>
<tr><td><b>Compositional Reach</b></td><td><code>CR=Acc(未见程序组合)</code>，按深度与未见组合阶数分层</td><td>区别局部模板记忆和可组合应用</td></tr>
<tr><td><b>Update-Response Control</b></td><td>在独立分支上使用少量旧 A/B 支持集做微更新，观察未见旧题改善；丢弃此分支</td><td>可塑性辅助诊断，额外训练成本必须计入；不调用 C 终测</td></tr>
</tbody></table></div>
<p>把三个无训练行为量记作 <code>z(S_H)=(RD,BI,CR)</code>；另记录参数层的梯度范数、A/B梯度相似度、表征有效秩、head-only与full-LoRA的相应结果。<b>不把 C 的标签、C 的终测结果或某次 C 更新后的梯度放进事前诊断器。</b>如果允许看到少量新C支持集，须单列为“C已知、适应前诊断”，不能和未知C预测混为一谈。</p>
<p><b>必须直接击败的近邻：</b><a href="https://proceedings.mlr.press/v306/sweeney26a.html" target="_blank" rel="noopener noreferrer">ICML 2026 Lie-bracket</a> 已能预测给定目标的训练顺序差异；<a href="https://arxiv.org/abs/2609.33620" target="_blank" rel="noopener noreferrer">2026 Learning Dynamics</a> 已有readout-based future-learnability诊断。我们要检验的是行为上的规则边界诊断是否在这些强基线之外还提供增量解释；若没有，保留现象，不包装新预测器。[[M18]][[M20]][[M22]]</p>
'''),
        ('method-intervention', 'Design 3｜主动干预：相同更新预算，只改变反例是否真正排除错误规则', '''
<p><b>针对性补救规则（可运行的最小方法）：</b>给每个历史后检查点 <code>S_H</code> 一小批旧任务域的候选样本，选择与其诊断中最常见的竞争规则产生冲突、但由外部oracle有唯一答案的样本。选择过程不使用未来C的训练题或测试标签。对每个候选 x，计算候选规则分歧度 <code>Dis(x)=Pr[rᵢ(x)≠rⱼ(x), rᵢ,rⱼ∈V(D)]</code>，再控制重复覆盖、题面长度与难度；优先同时覆盖高误用情境与尚未区分的规则对。</p>
<div class="flow"><div><b>旧训练记录</b><small>枚举一致的竞争规则 V(D)</small></div><div><b>学生诊断 z</b><small>哪条捷径、哪个情境最容易错用</small></div><div><b>选 k 个小剂量样本</b><small>分歧度 × 错用情境 × 去重复</small></div><div><b>固定 LoRA 补救</b><small>与全部对照等 Token / 梯度步</small></div><div><b>未来 C 正式学习</b><small>比较前测、增量曲线、旧能力回归</small></div></div>
<div class="table-wrap"><table><thead><tr><th>干预组</th><th>实际获得什么</th><th>要排除的解释</th></tr></thead><tbody>
<tr><td><b>RCP · Rule-contrastive</b></td><td>针对当前规则混淆选择分歧与边界 witness</td><td>研究中的主要干预</td></tr>
<tr><td><b>QBC · Query by Committee</b></td><td>同规模候选规则之间最大预测分歧，不针对具体适用边界</td><td>排除把传统主动学习重新命名为新方法</td></tr>
<tr><td><b>Diverse / Hard</b></td><td>词面/嵌入多样性，或当前难度/置信度选题</td><td>排除单纯难题或多样数据就足够</td></tr>
<tr><td><b>Random / Wnull</b></td><td>随机旧题或没有区分力的重述题，匹配长度与格式</td><td>排除额外训练计算与数据曝光</td></tr>
<tr><td><b>Oracle witness</b></td><td>实验生成器知道真实竞争规则时的理想干预</td><td>提供机制上界，不算真实自动教师的能力</td></tr>
<tr><td><b>SOAR-style grounded</b></td><td>同等总预算内以真实学生试训增益选小课程</td><td>排除真实收益反馈驱动选题已充分解决问题</td></tr>
</tbody></table></div>
<p><b>实施边界：</b>RCP在合成可验证规则族上首先使用已知规则图做机制研究。随后再尝试从旧执行轨迹提出候选规则、由独立判定器核验的非oracle版本；两者必须分开报告。不能在一个组用真实规则和免费oracle、另一个组只给自然语言猜测，然后比较优劣。对照所用试训、oracle调用与检索统一计费。[[S47]][[E26]]</p>
<p><b>可否证的核心预言：</b>若补救真正修复规则边界，在相近 A/B 分数时应观察到 <code>BI下降 / RD提高</code>，随后对相容 C₁ 学得更快、对冲突 C₂ 的旧规则错用减少；C₃ 未必改善。若只是A/B原题分数提高，或仅新C的零样本起点提高、继续训练曲线没有可重复变化，则不能声称提高未来可学习性。</p>
'''),
        ('method-analysis', 'Design 4｜机制鉴别：究竟改变了规则知识，还是训练器本身的可塑性？', '''
<div class="table-wrap"><table><thead><tr><th>竞争解释</th><th>它也能产生的表面结果</th><th>区分性实验</th></tr></thead><tbody>
<tr><td><b>已有特征更好（直接迁移）</b></td><td>C在0步就更准、末期也更准</td><td>绝对曲线L与增量曲线G分报；仅训练输出头、冻结主干、新Adapter逐项对照 [[M550]]</td></tr>
<tr><td><b>梯度几何 / 顺序效应</b></td><td>某个 A→B 更利于给定C</td><td>Lie-bracket预测、C支持集梯度、A/B角度基线；控制C已知与未知的信息权限 [[M18]]</td></tr>
<tr><td><b>优化器/适配器状态残留</b></td><td>继承Adam动量或LoRA满秩后，下一轮学习速度不同</td><td>分别重置与继承优化器；继续同Adapter vs合并历史权重并训练新Adapter</td></tr>
<tr><td><b>一般塑性下降</b></td><td>C₁、C₂、C₃都更难学</td><td>有效秩、梯度响应、不同LoRA rank/学习率和新无关任务；与现有plasticity机制比较 [[M22]][[M555]]</td></tr>
<tr><td><b>规则边界与错误复用</b></td><td>C₁可能更快，C₂因旧规则侵入而更慢</td><td>上下文反事实替换、Wbind错用矩阵、仅修复边界的随机补救与旧能力回归 [[E100]][[E99]]</td></tr>
<tr><td><b>选中的题恰好更难/更长</b></td><td>反例组“有帮助”但也多用监督或梯度量</td><td>同Token同步数、同难度分层、相同训练损失范围、多样性/QBC基线</td></tr>
</tbody></table></div>
<p><b>机制证据的强弱层次：</b>（1）<i>相关</i>：RD/BI能预测C的后续学习；（2）<i>干预</i>：随机分配规则对照样本后，RD/BI和C学习随之变化；（3）<i>特异性</i>：这种影响集中于规则相容/冲突的C，并在C₃和无效witness负控减弱；（4）<i>机制竞争</i>：已有几何、head-only与可塑性指标不能单独解释。不要仅凭表示CKA、线性探针或事后中介回归就声称已发现参数层面的严格因果通路。</p>
'''),
]

EXPERIMENT_SECTIONS = [
        ('experiment-master', '完整实验设计｜主实验、机制实验与补救实验如何拼成一篇论文？', '''
<p>先围绕上面<strong>一个因果机制</strong>组织实验；原有 P0–P3 仍作为不同 Idea 的公共工作包，不能把它们全部堆成一篇论文的“方法”。以下 E0–E5 是本专题建议给师兄讨论的<strong>论文级验证链</strong>，所有数量均为计划值而非已取得的数据。</p>
<div class="table-wrap"><table><thead><tr><th>实验</th><th>固定与操纵</th><th>关键对照</th><th>要画的图及决定性问题</th></tr></thead><tbody>
<tr><td><b>E0 · 生成器审计</b></td><td>有限程序规则、对照捷径、组合图与独立oracle；控制结构复杂度</td><td>人工抽检、重复/词面相似、rule-conflict覆盖、错误oracle负控</td><td>F1a 规则分歧示例和训练/测试分布；有没有真实的可辨识性？</td></tr>
<tr><td><b>E1 · 现象复现</b></td><td>同一个起始模型、完全相同的A/B数据多重集合；Blocked / Interleaved / 反向顺序</td><td>训练Token、LoRA、任务难度、C₀起点、旧A/B保持</td><td>F1b/F2：同样会做A/B，接下来学C曲线是否不同？</td></tr>
<tr><td><b>E2 · 机制分型</b></td><td>无反馈的Wsep/Wbind/组合测试 + A/B错用轨迹 + 表征/梯度诊断</td><td>仅得分、仅loss、梯度范数、Lie-bracket、readout诊断</td><td>F3：规则状态能否解释未来C增量，超过现有几何与塑性解释吗？</td></tr>
<tr><td><b>E3 · 随机补救</b></td><td>同一S_H分叉；RCP / QBC / Diverse-Hard / Random-Wnull / Oracle</td><td>同样补救数据量、Token、梯度步、oracle与试训计费</td><td>F4：规则边界改善是否伴随C₂学习曲线改善？</td></tr>
<tr><td><b>E4 · 反证及边界</b></td><td>相容C₁/冲突C₂/无关C₃；不同rank/优化器、新Adapter、输入模板反转</td><td>仅表面多样、仅当前难度、历史权重是否被保留</td><td>F5：哪些条件成立，哪些完全失效？是否只得到直接迁移？</td></tr>
<tr><td><b>E5 · 规模与现实性</b></td><td>第二模型、独立规则族、较长任务链、可单测工具/代码任务</td><td>跨模型重复、跨任务族统计、旧能力与总计算</td><td>F6：不是一个合成小模型或单一seed的偶然效应</td></tr>
</tbody></table></div>
<p><b>原 P0–P3 对应关系：</b>方法生成器+E0/E2支持 I10/I8；E1 是 I9 的未来可学习性核心；E3 是本专题为机制提出的新验证实验；I12 的补先修可以作为 E4 的独立推广，而不是与 E3 同时改动；P3 元规则进化必须在 E1–E4 的效应重复后才开展。这样能有一篇聚焦的现象+方法论文，也不损害原有 Idea 独立性。</p>
'''),
        ('experiment-resources', '可执行版本｜数据、模型、训练次数与成本控制', '''
<div class="table-wrap"><table><thead><tr><th>阶段</th><th>明确实验量（拟定）</th><th>只回答什么</th><th>扩张条件</th></tr></thead><tbody>
<tr><td><b>预备实验 / E0</b></td><td>3个可执行规则DSL：列表变换、符号/算术表达式、简单API状态机。每族至少4组真实/捷径规则对，生成独立训练、诊断、C训练与C测试数据；另做人类抽检</td><td>确保每个样本的真实规则、冲突与标签都可复核</td><td>语义不歧义、没有跨split程序模板答案泄漏</td></tr>
<tr><td><b>Pilot · E1</b></td><td><b>Qwen3-1.7B，2个规则族 × 3个历史组 × 3个种子 × 3类C = 54条后续C学习曲线</b>；每条C建议40步，测0/1/5/10/20/40步</td><td>判断差异真实存在、优化器/模板是否可运行</td><td>先看方差、C₀分布和现象是否跨两个族重复</td></tr>
<tr><td><b>Main · E1/E2</b></td><td><b>Qwen3-1.7B及Qwen3-4B，4个未见规则族 × 5种子 × 2个事前指定历史组 × 3类C = 240条C曲线</b>；6个新规则族可作为更强独立确认扩展</td><td>在不同任务图和模型规模下重现历史×C关系</td><td>按模型、族和种子报告层级效应，不把同一规则的数百题当独立样本</td></tr>
<tr><td><b>Mechanism · E3/E4</b></td><td>在E1中预先规定的代表性历史检查点上抽取同一起点分叉；<b>k=16</b>条补救样本为主剂量，k=8/32做剂量消融；先比较RCP、QBC、随机、无效witness，其他基线分阶段加入</td><td>小预算规则修复能否改变后续C学习，而非只提高A/B分数</td><td>不能从最终C测试挑“效果最好”的检查点</td></tr>
<tr><td><b>Transfer · E5</b></td><td>建议增加8B级模型、至少两类不同于开发用DSL的新任务环境（程序化工具调用与单元测试代码），以及5–10轮规则关系变化</td><td>检验是否超出最初构造的列表/数学规则</td><td>必须先完成核心机制；跨现实任务可退化为严格的外部验证，不强行声称完备因果规则</td></tr>
</tbody></table></div>
<p><b>训练合同（初稿）：</b>Qwen3系列开源权重，先用相同基础 Instruct 或 Base 口径（两者分别报告，不混合）。QLoRA/LoRA rank=16、AdamW、有效batch=32、最大输入512 Token，可在小Pilot开发集选择学习率与训练步数后一次冻结给全部条件；推理统一greedy / 温度0和结构化输出。40个C更新步骤为预先建议的初始测量网格，不保证足以覆盖学习平台期；若所有条件都饱和，必须在开发阶段统一调整预算后冻结，不依赖终测调整。<a href="https://github.com/QwenLM/Qwen3/blob/main/examples/llama-factory/finetune-zh.md" target="_blank" rel="noopener noreferrer">Qwen官方LoRA/QLoRA配置</a>可作实现起点。</p>
<p><b>计算量按真实分支核算：</b>每个历史只训练一次A/B并保存checkpoint；从其派生的C₁/C₂/C₃共享同一历史快照、使用固定C支持集，彼此独立更新。Pilot名义C训练步数为 <code>54 × 40 = 2160</code>，Main为 <code>240 × 40 = 9600</code>，<strong>不包含</strong>A/B预训练、补救、诊断、验证与重跑；GPU小时必须通过在目标3090/A100上实际计时再估计，不能把2160步直接折算成确定完成时间。先跑1个模型×1个任务族的端到端小闭环，再并行其余独立分支。</p>
<p><b>实际可提供给师兄的第一批结果：</b>一张 <code>A/B训练表现 vs Wsep/Wbind</code> 的双轴图、一张三种C的完整学习曲线、一个随机vs分歧witness补救表，以及资源账单。无需提前搭建完整元学习平台。</p>
'''),
        ('experiment-statistics', '实验统计契约｜主终点、独立重复、校准与审稿风险', '''
<p><b>主终点：</b>对每个新规则C，在固定预算范围内计算 <code>AULG(H,C)=AUC_b[L(H,C,b)−L(H,C,0)]/B</code>（归一化学习增量曲线面积）；同时把 <code>AULC=AUC_b[L(H,C,b)]/B</code> 作为同等重要的绝对表现。E1的主对比预先固定为 <b>Blocked vs Interleaved</b> 的 C₂-AULG 与 C₂-AULC，<b>History×C类型</b>作为主要机制交互；C₁和C₃整体报告。E3的主对比固定为 <b>RCP vs Random</b> 的 C₂-AULG，QBC为预设强基线。AULG在C起点高、接近上限时自然受到压缩，所以不能单独据此排名。</p>
<div class="equation">ΔHistory(C) = AULG(H_interleaved,C) − AULG(H_blocked,C)</div>
<div class="equation">ΔRescue(C) = AULG(H_RCP,C) − AULG(H_random,C)</div>
<p><b>其他必要报告：</b>0步C直接迁移、初始C损失、绝对学习曲线、达到开发集定义阈值的步数（没有达到须右删失）、A/B旧能力损失、规则错用矩阵、诊断probe/训练总Token、完整GPU时间。若不同条件的C₀差异很大，再增加同起点区间的预注册敏感性分析；不得根据终测分数事后筛选“能力一样”的成功分支。</p>
<p><b>数据划分与统计单位：</b>规则AST/组合图、词面模板、实例样本三层独立；开发族用于选择候选方法和学习率，确认族在方案冻结后才打开。随机种子与任务族是重复单位，题目只是嵌套测量。建议混合效应模型检验 <code>history × C_relation</code> 及 <code>intervention × C_relation</code>，对规则族分层bootstrap获得95%区间；主效应不按所有题目数量虚增n，检验多比较的预设主次顺序。正式样本量应在Pilot方差后做power/precision分析，再决定是否从4族扩至8–12族。</p>
<p><b>审稿人最可能的四种质疑：</b>（1）同C前测不同，算不上更会学习；（2）反例只是更多信息，传统主动学习也能做；（3）小合成语法的规则图由作者直接给出，真实Agent拿不到；（4）持续改变LoRA的参数、初始化或优化器状态造成了曲线差异。上述每项都有对应E2–E5的必要对照，不能只在Limitations解释。</p>
'''),
        ('experiment-mentor', '给师兄看的评议提纲｜论文主线、三个核心图与需要拍板的选择', '''
<div class="decision"><span class="kicker">MENTOR REVIEW · RESEARCH DESIGN v2 · OPEN QUESTIONS</span>
<h3>建议用五分钟讨论的版本</h3>
<p><b>一句话：</b>我们希望研究为什么两个模型当前都能完成同一任务，但后来接受完全相同的新任务训练后，学习速度和新旧规则冲突表现仍不同。方法是用程序化规则图发现“相同训练成绩下的不同解法”，再随机加入少量真正能排除错误规则的反例，检验其能否改变后续学习。</p>
<p><b>主图只要三张就能先判断选题：</b>F1“同分数、不同规则探针”；F2“相同C教学、不同学习曲线”；F4“随机反例补救能改变曲线，而非只改变原题成绩”。其他图是机制与泛化补充。第一阶段追求发现可复现的反常现象，第二阶段再判断是否值得把补救设计发展成新方法。</p>
<div class="table-wrap"><table><thead><tr><th>请师兄帮忙判断</th><th>现在的候选选择</th><th>什么答案会改变路线？</th></tr></thead><tbody>
<tr><td><b>1 · 选题核心</b></td><td>主打“当前能力相近、未来可学习性不同”及规则边界机制</td><td>如果看起来只是I9课程顺序现象，应收回I9，不单独立论文</td></tr>
<tr><td><b>2 · 方法贡献</b></td><td>规则状态诊断+分歧样本补救+完整未来学习测量</td><td>若QBC或更简单的随机反例完全一样，方法贡献应降级为实验范式</td></tr>
<tr><td><b>3 · 机制解释</b></td><td>先验证规则错用与future gain的特异性交互，再测表征/梯度</td><td>若Lie-bracket或读出层诊断解释完现象，优先机制论文而非新预测器</td></tr>
<tr><td><b>4 · 实验领域</b></td><td>列表、符号运算、程序化工具调用；两模型和跨族确认</td><td>若全靠人工编程规则而不落地到独立代码/工具任务，期刊层级应保守评估</td></tr>
<tr><td><b>5 · 投稿定位</b></td><td>Nature子刊风格：机制现象+反证实验；ICLR/ICML风格：算法必须胜过QBC/SOAR</td><td>根据E1–E3真实性与规模选择，不预先包装成“大一统RSI框架”</td></tr>
</tbody></table></div>
<p>可直接转发两份材料：<a href="generalization-mentor-brief.md">简洁的师兄评议稿（Markdown）</a>和<a href="generalization-protocol.json">可复核的实验契约（JSON）</a>。文献方法比较在上方，旧P0–P3仍保留作为其他Idea的关联研究；本页没有把待做实验写成结果。</p>
'''),
]
