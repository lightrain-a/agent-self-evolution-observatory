"""I13 RSI research idea: conflict-aware admission before internal learning.

Distinct from I3 post-hoc repair and I1 stable-knowledge storage. The agent's
meta-admission policy must improve on unseen future task sequences to qualify
as RSI, beyond fixed-model continual learning or test-time deferral.
"""
PAGE = {
 "slug":"learning-admission",
 "title":"I13 · 更新接纳与拒绝：什么时候不应该立即学习新能力？",
 "en":"I13 · Learning When Not to Update · Conflict-Aware Skill Admission",
 "lead":"I13 研究自我更新的接纳决策：内化一项新能力是否会损害旧能力、未来可塑性或无关领域的行为可靠性？Agent 能否选择核心更新、隔离、外部委托或暂缓，并在持续迭代中学会更准确地决定何时更新自己。I3 保留冲突发生后的修复主线。",
 "updated":"2026-10-28",
 "sections":[
 ("question","Observable Phenomenon｜学会新能力之后，整个系统为什么可能反而变差？",'''
<div class="decision"><span class="kicker">I13 · RSI RESEARCH IDEA · 2026-10-28 · NOT YET EXPERIMENTALLY VALIDATED</span>
<h3>When should a self-improving agent say “not in my core model, at least not yet”?</h3>
<p>一个内容安全 Agent 已经稳定识别旧风险类型。新领域能力可以通过微调获得，但若直接更新共享模型，旧类别的误判也随之上升。即使新任务单独成绩很高，<strong>整个系统的净能力也可能下降</strong>。若现成外部审核模型或独立 Adapter 已能承接新任务，强迫核心模型马上内化新能力未必最划算。</p>
<p><b>主科学问题：</b>多轮自我改进中，Agent 能否根据新能力的必要性、旧能力是否仍正确、预期干扰成本和可用外部能力，主动选择<b>内化 / 隔离 / 委托 / 暂缓</b>；并在后续版本更新后重新决定是否内化？</p>
<p><b>拒绝什么：</b>拒绝一次高风险的<b>内部参数/核心 Skill 接纳</b>，不是拒绝必须执行的任务或安全要求；系统依然可以使用经验证的外置能力。若旧规则已过时，必须允许修订，不能以保护旧能力为理由阻止必要纠正。</p>
<div class="note"><b>与 I3 的关系：</b><a href="ideas.html#idea-3">I3</a> 研究新能力已写入后，旧能力受损怎样修复；I13 在正式提交更新前做决策。与 <a href="ideas.html#idea-1">I1</a> 的区别：I1 比较知识稳定性、内化与检索位置，I13 必须在<strong>知识稳定性与外部查询成本匹配</strong>时，通过旧能力冲突风险解释不同的接纳决策。</div>
</div>
'''),
 ("phenomena","Why｜同样冲突很大，却不该总是“拒学”",'''
<div class="table-wrap"><table><thead><tr><th>新旧规则的真实关系</th><th>单看冲突的错误判断</th><th>合理的待验证行动</th></tr></thead><tbody>
<tr><td><b>A 兼容增长：</b>新能力补足旧能力空白，核心规则都有效</td><td>把未知当冲突，过度拒绝更新</td><td>优先内化并验收</td></tr>
<tr><td><b>B 双方有效但场景不同：</b>新旧规则在各自条件下成立，却会互相干扰</td><td>一味混合训练或一味保护旧参数</td><td>隔离 Adapter / 外部专家，保留准确路由与未来重访条件</td></tr>
<tr><td><b>C 旧规则已失效：</b>新规则才是当前应使用的规范</td><td>误把旧准确率当作必须保护的能力</td><td>接受新规则并有条件淘汰旧规则，检查时间/适用范围</td></tr>
<tr><td><b>D 核心能力应当掌握：</b>高频、低延迟或外部专家不可靠</td><td>长久外包使核心学习停滞</td><td>即使内部风险不小，也应考虑更稳健的内部学习与修复</td></tr>
</tbody></table></div>
<p><b>重要洞察：</b>“冲突程度”与“正确的学习接纳行动”不是单调关系。旧规则仍有效吗？外部服务可靠吗？该能力未来调用多少次？其他任务的学习会不会让内化变容易？这些变量共同决定系统级净收益。</p>
<p>人类研究的认知卸载与干扰控制提供动机，不能直接证明 LLM 在拒绝内化后会长期变强；AI 中的 RAG/持续更新在时间知识漂移时也可能错误，因此外部委托不应被当成绝对安全的答案。[[E100]][[M327]]</p>
'''),
 ("work","Related Work｜先把持续学习、外部委托和真正 RSI 分三层",'''
<div class="table-wrap"><table><thead><tr><th>研究层级</th><th>已有论文真正解决什么</th><th>它没有直接验证什么</th></tr></thead><tbody>
<tr><td><b>固定训练器：Continual Learning</b></td><td><b>EAFT</b> 针对 SFT 高置信度冲突 token 降低梯度；<b>RieSelect</b> 在联邦持续学习中选择风险较低的更新层；<b>CoPE</b> 由 Probe 决定何时增设 VLM 专家。[[M320]][[M321]][[M322]]</td><td>一次候选新能力可以直接拒绝内部学习、外部专家承接、未来再尝试；元接纳策略在后代任务上变好</td></tr>
<tr><td><b>可逆/非权重存放</b></td><td><b>ReGrad</b> 用可检索梯度实现临时权重适配；<b>Modular Memory</b> 主张结合参数和上下文学习；<b>Chronos</b> 在时间知识漂移下改进检索的时间一致性。[[M323]][[M326]][[M327]]</td><td>按照“干扰旧能力—未来内化收益”的反事实证据选择能力承载表面，并提升下一代选择能力</td></tr>
<tr><td><b>推理时外部委托</b></td><td><b>Learning to Defer</b> 与 <b>Online L2D</b> 决定当前样本交给自身还是可变专家。[[M324]][[M325]]</td><td>是否接纳新技能为长期能力、外包后核心的独立学习、下一代再内化</td></tr>
<tr><td><b>真正 RSI 邻近</b></td><td><b>RSIFlow</b> 诊断并选择工作流、演化 Meta-Agent；<b>MetaSkill-Evolve</b> 共同演化任务 Skill 与 Meta-Skill；<b>Skill∞</b> 递归改进并跨任务复用 Meta-Skill。[[S28]][[S06]][[S320]]</td><td>针对能力冲突，做“拒绝本轮核心更新/外包/暂缓/重访”的跨代学习接纳决策与相应的后续可学习性验证</td></tr>
</tbody></table></div>
<p><b>核心边界：</b>EAFT、RieSelect、CoPE 可以作为某个候选学习动作的<b>固定实现或强基线</b>，但它们不是 RSI 论文。反之，给 EAFT 外围套一层 Meta-Agent、把“新任务扩一个专家”命名为 RSI，也不足以形成贡献。必须用跨代交叉测试证明决策原则本身在变好。</p>
<p><b>特别区分 CoPE：</b>此处引用的是 <i>CoPE: Continual Probe-guided Expansion for Large Vision-Language Models</i>（ICML 2026），不是同会的同名“Planning and Execution Coordination” Agent 工作。[[M322]]</p>
'''),
 ("challenge","Challenge｜学习接纳是比普通任务路由更难的决策",'''
<h3>C1 · 不能把梯度冲突直接当旧能力损害</h3>
<p>某 token 的低概率和低熵、某层 Fisher 冲突分数，未必对应未见旧任务退化；旧任务有时本来就应该被新规则替代。必须通过相同 checkpoint 的真实小规模更新与冻结回归样本估计。[[M320]][[M321]]</p>
<h3>C2 · 外包后的成功不等于核心能力增长</h3>
<p>独立 Adapter 或外部模型可以立即提高系统成功率，却也可能导致核心模型长期没有学会新技能。需分开测 <b>Core-only</b> 与 <b>System-with-Experts</b>，并计入专家不可用和模型版本变化。</p>
<h3>C3 · 未来的学习收益看不见</h3>
<p>现在不学，可能避免破坏旧规则；但一直不学，会失去未来降低调用成本的机会。重访条件如果由终测成绩选取，就会产生数据泄漏。要把未见后续学习序列预先冻结，学习收益在事后独立验收。</p>
<h3>C4 · 不能把外部接口变成安全绕行</h3>
<p>外部模型可能过时、泄露数据、依赖网络，也可能给出无法解释的错误结论；安全关键动作须经过同样的验证和权限隔离，不能因为不是核心参数输出就免除回归门。</p>
'''),
 # placeholder
 ("plasticity","Nature 2024 新增备注｜现在不会做，还是后续越来越学不进去？",'''
<p><b>论文的可迁移 Insight：</b>Dohare 等（Nature 2024）发现深度网络经过长时持续训练，可能逐渐失去学习新任务的能力；CIFAR-100 中，即使每一阶段都继续训练全部已见类别、与相同当前数据从头训练比较，普通持续网络后期仍落后。作者的 <b>Continual Backpropagation</b> 通过少量重置低使用价值单元缓解可塑性下降。<a href="reading-notes.html#deep-nature2024-loss-plasticity-dohare">完整原文实验、图1–4、机制与限制</a>。[[M22]]</p>
<p><b>新增科学问题：</b>某次内化更新既提高新能力，也没有明显伤害旧能力，但是否可能透支未来学习新规则的速度？这与“当下新旧知识互相冲突”是两个不同风险，不能只用旧任务回归或 dormant units / stable rank 当成已校准的未来学习指标。<strong>它不自动适用于只改 Prompt/Memory、未更新参数的 Agent</strong>。</p>
<div class="table-wrap"><table><thead><tr><th>冲突 / 可塑性</th><th>观测到的状态</th><th>合理的待验证动作</th></tr></thead><tbody>
<tr><td><b>可塑性尚好、冲突可控</b></td><td>复制检查点后，监督试训能学会且旧能力损害小</td><td>Internalize · 直接内化</td></tr>
<tr><td><b>可塑性尚好、旧能力冲突高</b></td><td>试训新题可学会，但旧任务回归差</td><td>Isolate / Delegate / 暂缓核心更新</td></tr>
<tr><td><b>多类新任务的可塑性不足</b></td><td>初始难度与监督一致、优化器重置后仍持续难学</td><td>先诊断或恢复学习能力；可用新 Adapter/外部专家暂时承接</td></tr>
<tr><td><b>旧规则已经过时</b></td><td>保护旧模型会保留错误规范</td><td>不得以抗遗忘或保持可塑性为由拒绝必要纠正</td></tr>
</tbody></table></div>
<p><b>最小独立 P0：</b>从同一基础模型生成两种受控更新历史，匹配当前 A/B 能力、旧任务保持、参数预算和总训练 FLOPs；冻结全新 C₁（共享规则）、C₂（规则冲突）、C₃（无关规则）并重置 AdamW 状态后做等预算学习曲线。复制 checkpoint 的 Probe 更新必须丢弃。将<span lang="en"> current gain / old forgetting / future learnability </span>分开测，诊断成本全部入账。若差异仅来自学习率、旧 LoRA 的可更新面积或优化器动量，则不能声称核心表示丧失可塑性。[[M20]][[M22]][[M23]]</p>
<p><b>对 RSI 的意义：</b>P0/P1 证明更新历史确实影响未来 C 学习之后，P2 才训练新旧 <b>Meta-Admission Skill</b>，在相同模型/专家池/任务序列上比较“何时内化、隔离、委托、恢复或重访”的后代净增益。<strong>只实现 CBP 或一个固定的塑性阈值不构成 RSI 新贡献</strong>；外部专家能完成任务也不代表核心模型恢复塑性。</p>
<p class="status">Nature 论文是深度网络持续学习证据；上面的 LLM 与 RSI 诊断、接纳决策和跨代更新仍为本项目研究假设，尚未执行。</p>
'''),
 ("nonlocal-effects","Nature 2026 新增证据｜局部能力修复的风险也可能扩散到无关领域",'''
<p><b>原论文的现象：</b>Betley 等（Nature 2026）在局部不安全代码和特定角色数字序列训练后，发现模型在原训练领域之外的普通问题上出现不当行为；不当回答与训练内容、语境、输出格式及模型状态有关。作者的关键安全代码 / 教学语境对照已在 ICML 2025 原始论文提出，Nature 增加格式、训练动态与基础模型的分析。原实验没有证明<strong>任意正常的局部修复都会造成失准</strong>。<a href="reading-notes.html#deep-nature2026-narrow-misalignment-betley">完整论文精读、Figs.1–5、13节原文及 RSI P0</a>。[[M450]][[M451]]</p>
<p><b>与既有两个风险严格分开：</b>①旧任务遗忘（旧任务精度退化）；②未来可塑性下降（下次学新任务更难）；③<strong>非局部行为漂移</strong>（局部学习成功、旧任务准确率近似不变，但在其他普通问答或结构化输出中表现出不同的助手行为）。不能仅凭旧任务正确率通过，就宣布更新安全；也不能将人格特征检测直接当作已校准的部署风险。有关persona方向的因果干预已有后续工作，不能声称本项目首次发现。[[M452]][[M453]]</p>
<div class="table-wrap"><table><thead><tr><th>同一局部修复后的观测</th><th>需要单独检验</th><th>Learning Admission 的接纳影响</th></tr></thead><tbody>
<tr><td>目标任务已达到预定水平</td><td>独立目标任务与训练来源隔离</td><td>必要但不充分</td></tr>
<tr><td>旧能力表现稳定</td><td>旧题、关键安全约束与权限边界</td><td>不能替代全域行为验收</td></tr>
<tr><td>下一任务学习能力稳定</td><td>未来C任务等预算学习曲线</td><td>不能替代全域行为验收</td></tr>
<tr><td>无关领域与格式出现行为变化</td><td>文本、JSON、代码、工具动作的独立评测</td><td>可触发隔离、拒绝本轮提交或回滚；不可用新能力收益抵消严重违规</td></tr>
</tbody></table></div>
<p><b>P0 最小方案：</b>不用不安全目标数据来复现已知现象。先选择合法可验证的代码/数学任务修复，从同一模型检查点比较共享参数 LoRA、隔离 Adapter、外部 Skill/专家等路径，严格匹配目标学习收益、训练 token/FLOPs 与可用外部信息。在独立多领域和多输出格式的验证集上检查版本相对变化及安全行为，报告原始样本、置信区间、Judge误差与人工审核分歧。</p>
<p><b>RSI 关键：</b>只有在 P0 观察到可重复、预先定义的非局部副作用后，才用历史版本证据更新 <b>Meta-Admission Skill</b>，并在未见任务/版本组合上比较旧版和新版的跨域风险预判、接纳动作与等预算净能力。一个固定的全域安全门如果已经足够，就不应包装复杂元控制器。[[S06]][[S320]]</p>
<p class="status">Nature 是局部训练可引发非局部风险的证据；本项目合法修复、工具行动、事前预测与跨代 RSI 收益均为尚未验证的假设。</p>
'''),
 ("insight","Insight｜不是拒绝新知识，而是保留将来再学的选择权",'''
<p><b>候选机制：</b>对同一个新能力，Agent 不仅比较一次训练后的新旧能力变化，还比较现在内化、隔离承担和未来重访三者的长期净收益。对有效但不兼容的两套能力，<b>暂缓核心更新</b>可能减少不必要的回归；当条件改善时，再尝试内化，有机会把临时外接能力变为自身能力。</p>
<p>需要区分<b>旧规则正确而适用范围不同</b>和<b>旧规则过时</b>。前者可以分叉路由，后者不应因“拒绝遗忘”而永远保存错误。新能力的来源必须经过真实验证，也不因模型自述“冲突很大”就自动判定不可学。</p>
<p>这比静态选择“存记忆还是存参数”更进一步：Agent 学习的是<strong>根据新旧冲突的可修复性和未来学习机会，判断什么时候值得改变自身更新表面</strong>。任务优化器可以保持固定，元接纳策略必须跨任务、跨版本持续被验证并修订。</p>
'''),
("design","Design｜学习接纳的两层进化闭环",'''
<div class="flow">
<div><b>冻结候选能力与核心模型</b><small>版本号、旧规则有效性、训练与专家访问条件</small></div>
<div><b>小成本反事实 Probe</b><small>真实小样本更新、旧能力回归、外部专家可靠性</small></div>
<div><b>Admission 选择</b><small>内化 / 独立隔离 / 外部专家 / 暂缓</small></div>
<div><b>接受与版本化</b><small>保持高优先级约束；记录接纳原因和未来重访条件</small></div>
<div><b>后续任务真实验收</b><small>Core-only / System / 旧能力 / 算力 / 将来还能否学</small></div>
<div><b>改进 Meta-Admission Skill</b><small>使用受控历史结果而非自述，下一代重新判断</small></div>
</div>
<h3>候选动作：不是每项新能力都必须修改共享核心</h3>
<div class="table-wrap"><table><thead><tr><th>动作</th><th>执行方式</th><th>必须满足的约束</th></tr></thead><tbody>
<tr><td><b>Internalize</b></td><td>按固定训练器在核心模型或通用 Skill 中真实更新</td><td>新任务增益真实、旧任务和安全回归达标</td></tr>
<tr><td><b>Isolate</b></td><td>独立 Adapter / 版本化专用 Skill，在路由条件下使用</td><td>原核心不被污染；组合执行和可用性可复验</td></tr>
<tr><td><b>Delegate</b></td><td>保留核心不变，调用已有且经过验证的外部专家</td><td>权限、数据、延迟、服务可靠性及服务费用计入总成本</td></tr>
<tr><td><b>Defer and Revisit</b></td><td>本轮不做高风险内化，记录条件和后续触发；必要时由外部服务承担</td><td>目标能力持续可用；不得永久掩盖重要欠缺</td></tr>
</tbody></table></div>
<p>另有一项<strong>拒绝无效提案</strong>，例如训练材料被证伪或试图绕过安全约束。这与“真实新能力、暂不内化”不是同一决定，不能合并统计。</p>
<h3>把当前最优和未来学习潜力分开</h3>
<div class="equation">AdmissionChoice = argmax expected [System Gain + Future Learnability − Total Cost], subject to Old-Capability &amp; Safety Gates</div>
<p>上述为拟研究的决策原则，不是已经训练出的策略。<b>System Gain</b> 同时测新任务和旧任务；<b>Future Learnability</b> 通过下一批冻结的、未见的新任务需要多少学习预算来衡量；<b>Total Cost</b> 包含所有探测、训练、搜索、外部服务、版本维护与重访。安全硬约束不可由其他任务分数抵消。</p>
<p><b>两个时间尺度：</b>快环每次决定某项新能力由哪个载体承担；慢环根据真实版本的得失修订 <b>Meta-Admission Skill</b>。慢环可以是版本化 Skill 或经过固定训练程序更新的 LoRA，但必须能被独立重复测试，不能仅指当前 Agent 想到了一个新 Prompt。</p>
'''),
("p0","P0｜同样有冲突，新能力为什么应该被不同地接纳？",'''
<p><b>先验证现象，再构建新模块。</b>用可以程序验证的数学规则与代码工具任务，从同一基础模型/Agent 版本构造三种真实关系：A 新旧兼容；B 新旧各自正确但适用条件不同、同时学容易冲突；C 旧规则已过时，需要明确修订。最好再加入 D：外部专家低可靠或高频/低时延要求的能力。固定新能力训练文本、任务调用分布、旧能力优先级、专家可靠性，以及规则有效性标签。</p>
<div class="table-wrap"><table><thead><tr><th>对照</th><th>可以做什么</th><th>为什么必须比较</th></tr></thead><tbody>
<tr><td>Always-internalize</td><td>每次普通 SFT/LoRA 内化</td><td>强制学习导致的旧能力净损失</td></tr>
<tr><td>EAFT / RieSelect（可适配时）</td><td>仍在既定训练表面内做冲突敏感更新</td><td>排除“仅降低破坏性梯度即可解决问题”</td></tr>
<tr><td>Always-external / Always-isolated</td><td>固定调用现成专家或独立模块</td><td>排除“只要外置就足够”的朴素策略</td></tr>
<tr><td>Fixed conflict threshold</td><td>只凭梯度冲突或预训练准确率阈值选择</td><td>判断能否识别 B、C 的不同正确决策</td></tr>
<tr><td>Evidence-based admission</td><td>相同 probe 预算，比较旧规则有效性、可恢复性及未来净收益</td><td>验证冲突信息是否提供超出静态路由的价值</td></tr>
<tr><td>Oracle（仅上界）</td><td>事后看所有分支的真实收益并选择</td><td>评估策略后悔值；绝不可让策略提前偷看</td></tr>
</tbody></table></div>
<p><b>决定性观察：</b>在稳定性、使用频率、外部服务费等 I1 变量相近时，仅改变新旧规则的有效性和冲突可修复性，最佳接纳方式就会发生可重复反转。如果普通固定存放规则已经一样好，不应再设计复杂 Admission Policy。</p>
<p>验证指标分为<strong>Core-only 未见题正确率</strong>、<strong>System-with-Experts 正确率</strong>、旧/新/组合任务保持、安全回归、全部 token / FLOPs / 专家费用及对应的总体效用。外部模型不能因为天然更强且预算不对齐就被宣布为优胜者。对于不可真实重训的 API 闭源模型，外部委托和 Skill 版本轨可测，但参数内化轨需使用可训练的本地模型。</p>
'''),
("p1","P1｜今天拒绝内化，明天什么时候应该回来学？",'''
<p>只有 P0 证实存在不同的最佳接纳动作，才启动多轮实验。选出 B 类高干扰、但可由外部专家可靠承担的新技能，冻结一条连续任务流；让系统先保持核心不变，记录每次专家调用和误差，再在后续知识/参数变化后考虑重访。</p>
<div class="table-wrap"><table><thead><tr><th>重访策略</th><th>关键问题</th></tr></thead><tbody>
<tr><td>永久外包</td><td>核心是否永远停滞、长期费用会不会反超？</td></tr>
<tr><td>立即内化后修复</td><td>是否花费大量预算补救旧能力损失？</td></tr>
<tr><td>固定周期重试</td><td>是否只是更频繁地训练带来收益？</td></tr>
<tr><td>条件触发重访</td><td>前置能力、冲突诊断或累计调用成本变化时，是否更适合内化？</td></tr>
</tbody></table></div>
<p>预先固定重访触发器，不通过未见终测的答案挑重访时刻。新增能力的监督信息、训练器和更新预算严格匹配，并计入外包阶段的所有成本。关键结果是长期系统净收益、核心独立能力、过早接纳造成的回归、错过可安全内化机会的比率，而不是简单统计委托多少次。</p>
<p><b>特别注意：</b>如果外部专家始终更可靠而更便宜，选择永久外包也可能是长期最优；不能为证明“RSI 必须内化”强迫模型学习。相反，若新能力是安全必需的核心判断且外包不可靠，则暂缓可能不符合任务合同。</p>
'''),
("p2","P2｜真正的 RSI：新一代是否更会决定什么值得自己学？",'''
<p><b>固定任务 Skill 后，交叉比较元策略版本。</b>把通过 P0/P1 获得的、可审计的接纳决策结果作为发展集，改进 <b>Meta-Admission Skill</b>；然后将旧策略 m₀、新策略 m₁、固定规则与通用 RSIFlow / MetaSkill-Evolve / Skill∞ 风格的统一优化器（共享相同候选动作和预算）放入<strong>从未用于改进元策略的未来任务族</strong>中。</p>
<p>每个分支从完全相同的 Agent、专家服务清单、能力库和训练器快照开始，外部模型身份与费用被冻结。只有元接纳策略不同，后续才允许系统自主决策并形成不同后代。另作<strong>冻结任务 Skill 的逐次决策测试</strong>，防止“新策略看到了更多新能力”冒充元能力提升。</p>
<div class="flow"><div><b>冻结同一代能力</b><small>任务 Skill、模型、专家池、预算与验证器</small></div><div><b>旧/新元规则分别决策</b><small>Internalize / Isolate / Delegate / Defer</small></div><div><b>实际执行独立学习</b><small>安全回归与全成本记录</small></div><div><b>对未见任务继续迭代</b><small>观察第 k+1、k+2 代系统</small></div><div><b>跨代验收</b><small>新知识掌握、旧能力、决策 regret 与未来学习速度</small></div></div>
<p><b>RSI 成功证据：</b>在同任务、同外部资源、同总预算下，新版元策略更准确地判断何时应内化/暂缓，且最终能以更低的跨轮代价获得更高的持久系统净能力；新元策略优势要在未见冲突类型和后续任务流上保持。</p>
<p><b>不可省的消融：</b>去掉后续学习收益目标；去掉冲突有效性校验；去掉暂缓/重访；永远固定外部专家；固定元规则仅做更多 Probe；完整上下文历史 vs 净元规则更新。没有这些对照，很容易只验证一个额外提示词或多用了一家强模型。</p>
'''),
("boundaries","与 I1 / I3 / RSI 近邻的最终裁决",'''
<div class="table-wrap"><table><thead><tr><th>方向</th><th>在研究什么</th><th>判断是否碰撞</th></tr></thead><tbody>
<tr><td><a href="ideas.html#idea-1">I1</a>：内化还是外置</td><td>相对稳定的知识应保存在哪里，外部调用和内化各有多少成本</td><td>若新候选只根据频率和存储成本决定外包，直接并入 I1</td></tr>
<tr><td><a href="ideas.html#idea-3">I3</a>：冲突后修复</td><td>新能力已被接纳且旧能力受损，怎样定向巩固、修复适用边界</td><td>若必须先造成损害才能诊断并修复，而事前选择无增量，归入 I3</td></tr>
<tr><td>RSIFlow / MetaSkill-Evolve / Skill∞</td><td>已能演化改进工作流或 Meta-Skill</td><td>若只是多一个会选择工具的 Meta-Agent，应归入这些工作；关键是接纳元规则的跨代独立收益</td></tr>
<tr><td><b>I13：Learning Admission</b></td><td>先判断新能力是否适宜写入核心，暂缓时让外部能力承接、保留未来再内化机会；使这一决策规则逐代改进</td><td><b>事前冲突证据 × 决策行为 × 未来可学习性</b>三者共同成立才独立</td></tr>
</tbody></table></div>
<h3>Go / Merge / Stop</h3>
<div class="table-wrap"><table><thead><tr><th>决策</th><th>预先需要什么证据</th></tr></thead><tbody>
<tr><td><b>GO · 独立成篇</b></td><td>P0 出现同等冲突但最佳接纳不同、P1 暂缓/重访有可解释的长期价值、P2 新版元策略在未见任务上显著降低决策 regret 并提高等预算净学习收益</td></tr>
<tr><td><b>MERGE · 并入 I1 / I3</b></td><td>只得到内化与外置的一般成本权衡，或只得到已经发生冲突后需如何修复</td></tr>
<tr><td><b>STOP · 不再设计新路由器</b></td><td>简单静态路由/固定外部专家/EAFT 式稳定训练已达到相同结果；试探成本吃掉全部增益；元策略新旧版本之间无可复现的学习差异</td></tr>
</tbody></table></div>
<p class="status">状态：I13 正式列入 RSI 研究池；原始相关工作已核对；所有 P0/P1/P2 为待验证实验，尚无真实训练或递归进化结果。不将外部专家答对直接称作核心模型学会。</p>
<div class="links"><a class="link-btn" href="ideas.html#idea-3">I3 · 冲突后的能力修复</a><a class="link-btn" href="ideas.html#idea-1">I1 · 内化与外置知识</a><a class="link-btn" href="experiments.html">通用冻结评测协议</a><a class="link-btn" href="references.html">相关文献来源</a></div>
''')
 ]
}
