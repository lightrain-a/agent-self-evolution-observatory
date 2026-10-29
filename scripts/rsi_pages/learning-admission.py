"""I13: Safety-Aware Update Admission for Recursive Self-Improving Agents.

Research proposal; P0-P2 are not measured. Historical effects inform a
learned test/admission policy, never permission to weaken independent gates.
"""
PAGE = {
 "slug": "learning-admission",
 "title": "I13 · 安全更新接纳：Agent 什么时候应该拒绝修改自己？",
 "en": "I13 · Safe to Inherit? Safety-Aware Update Admission for Recursive Self-Improving Agents",
 "lead": "RSI 每一代都可能改写 Skill、Memory、Harness；局部能力提升不等于后代安全。I13 研究利用历史版本的失败与恢复证据，在有限验证预算内预判风险、决定接纳、隔离、暂缓或拒绝更新，让 Meta-Admission 跨代变得更会判断。核心授权与发布门始终独立、不可被自改写。",
 "updated": "2026-10-29",
 "sections": [
 ("question","Observable Phenomenon｜新版本更有用，为什么后代反而可能不安全？",'''
<div class="decision"><span class="kicker">I13 · RSI SAFETY · RESEARCH DESIGN · 2026-10-29</span>
<h3>Safe to Inherit? Can an Agent Learn When to Reject Its Own Updates?</h3>
<p>一个文件管理 Agent 将常见操作写成了更快的 Skill，本轮任务成功率提高、旧任务测试也通过。若后代遇到新的所有权关系、权限状态或组合操作，这条 Skill 可能继续沿用过时的检查捷径。<strong>局部有益的修改，可能成为下一代真正执行的不安全程序。</strong></p>
<p>更反直觉的是：<strong>拒绝本轮候选也未必安全</strong>。假如旧的 incumbent 早已不满足当前授权合同，拒绝所有新版本之后，系统仍在运行那个旧程序。2026 年的直接 RSI 研究已观察到这一故障。[[S450]]</p>
<p><b>核心问题：</b>Agent 能否根据历次真实版本的故障与恢复证据，<strong>在一次候选修改被正式继承前</strong>，挑选最值得做的风险测试和允许的处置动作？下一代的风险诊断规则能否在从未见过的风险家族上比上一代更准确？</p>
<p><b>不研究什么：</b>不是让 Agent 学会日常对话拒答，不是允许它修改自己的安全阈值，也不是第一次提出安全门/回滚。安全约束和发布权限始终由独立、不可绕过的机制掌握。</p>
<div class="note"><b>从原 Learning Admission 的收敛：</b>保留接受／隔离／外部承接／暂缓重访的动作；把主要因变量转为<strong>跨代安全风险、漏放与误拒、安全净能力和验证预算</strong>。旧能力保持和未来可塑性仍在页面后部作为辅助观察，不与安全主线竞争。</div>
</div>
'''),
 ("phenomena","Why｜风险产生、通过验收和未来触发可能发生在不同阶段",'''
<p>一项更新的安全性不仅取决于代码或 Skill 内容，还取决于随后调用它的任务、授权合同及是否确实部署。需要将候选提案、验收结果、实际运行程序、下次被编辑版本与未来 Skill 激活分别记录，避免“候选安全”与“系统运行安全”混为一谈。</p>
<div class="table-wrap"><table><thead><tr><th>已有观察</th><th>局部评估为什么会遗漏</th><th>要检验什么</th></tr></thead><tbody>
<tr><td><b>F1 · 合同变化</b></td><td>旧分数仍评价旧权限，历史成绩可能保留不安全程序</td><td>新授权依赖与任务组合的独立验证。[[S450]]</td></tr>
<tr><td><b>F2 · Skill 继承</b></td><td>最初的触发输入消失，但程序被保存为可复用知识</td><td>写入／检索／执行三阶段，以及下一会话正常任务激活。[[S451]][[S452]]</td></tr>
<tr><td><b>F3 · 拒绝更新但旧版本仍在运行</b></td><td>只检查候选是否通过，没检查当前 incumbent</td><td>实际部署版本和可安全回滚的目标。[[S450]]</td></tr>
<tr><td><b>F4 · 参数修改的跨领域偏移</b></td><td>目标任务达标，普通旧题仍正确</td><td>跨领域的独立行为验收；不能直接把权重实验套用到 Skill。[[M450]]</td></tr>
</tbody></table></div>
<p><b>I13 还没有证明的现象：</b>在局部功能收益和常规回归表现相近时，未来的安全风险能否系统性不同？能否用更新之前允许访问的结构性证据预测？这是 P0 的任务，而不是文献结论的重复。</p>
'''),
 ("work","Closest Related Work｜安全门、持久 Skill 治理和恢复已有强先例",'''
<div class="table-wrap"><table><thead><tr><th>最近邻</th><th>原工作已经做到什么</th><th>I13 要补的决定性证据</th></tr></thead><tbody>
<tr><td><b>Safety Must Survive Self-Improvement</b> · 2026 预印本 [[S450]]</td><td>授权依赖变化后，48 条演化历史中有 22 条保留不安全程序，尽管每条受影响历史的候选库有正确替代；完整验证和已验证回滚已能在核心实验中恢复安全。</td><td>在同等预算下，<b>更新前</b>基于历史选择性检测未知风险；不能仅复现回滚和完整验证。</td></tr>
<tr><td><b>Practice Makes Unsafe / SafeEvolve</b> · 2026 预印本 [[S451]]</td><td>25种 agent-method 配置中21种进化配置写入不安全 Skill，其中15种在新会话造成危害；SafeEvolve 已经有写入与读取双重治理、修复和隔离。</td><td>主动选择应验证哪个候选、未来哪个继承情景；与 SafeEvolve 做同预算对照，而非自称首次安全 Skill 治理。</td></tr>
<tr><td><b>EvoSkill Injection / SARGE</b> · EMNLP 2026 [[S452]]</td><td>已将自主生成并存储恶意 Skill、后续检索和激活的持久风险建立为明确威胁与基准。</td><td>学习跨风险家族的事前识别与接纳规则，不能只展示攻击持久存在。</td></tr>
<tr><td><b>Falsifiable Release Gates</b> · 作者预印本 [[S453]]</td><td>预先声明的机器可检查验收套件、有限状态安全不变量和受权限保护的发布流程。</td><td>硬门必须保留；新贡献仅在有限预算下的测试选择和风险诊断，不能声称首个安全门。</td></tr>
<tr><td><b>Trustworthy RSI Survey</b> · 2026 预印本 [[S454]]</td><td>已将改进有效性、约束保持和有效监督组织为框架，明确区分单次更新、后代继承和元机制修改。</td><td>不要重复“可信 RSI 总框架”，需要实际的跨代对照和机制证据。</td></tr>
<tr><td><b>In-Training EM Defenses</b> · ICML 2026 [[M454]]</td><td>已测试 KL、特征 L2、persona steering、指令交错及 inoculation 等抑制微调失准的固定训练方法。</td><td>作为未来 LoRA 分轨基线；初版先研究 Skill/Harness 的版本准入，不混合参数训练风险。</td></tr>
<tr><td><b>RSIFlow / MetaSkill-Evolve / Skill∞</b> [[S28]][[S06]][[S320]]</td><td>改进工作流、Meta-Agent 或 Meta-Skill 可以递归修订，元改进本身不新。</td><td>冻结基础编辑器和门，交叉比较更新前安全诊断规则 m₀/m₁ 的实际后代效果。</td></tr>
</tbody></table></div>
<p><b>最近邻裁决：</b>“做个安全测试门”“发现不安全更新就回滚”“保护 Skill 写入与读取”都不是 I13 的论文贡献。真正要问：<strong>历史真实自修改的后果能否提高未来未知更新的事前风险识别，在相同检查预算下减少不安全放行与安全更新误拒？</strong></p>
'''),
 ("challenge","Challenge｜为什么静态 Safety Guardrail 不足以回答 RSI 问题？",'''
<h3>C1 · 更新风险与未来合同可能未知</h3>
<p>当前候选通过已知回归，仍可能在未来授权状态或 Skill 组合中触发风险。全量测试昂贵，固定少量测试可能漏掉新组合；预测器只能访问更新前已批准的历史、当前合同与 Probe，不能偷看未见终测。</p>
<h3>C2 · 全部拒绝会掩盖能力损失和误拒</h3>
<p>如果只看已接受版本的违规比例，“永不更新”轻易看似安全。必须同时评价漏放危险更新、误拒安全更新、真实新功能收益和所有测试/外包成本。</p>
<h3>C3 · 不能把候选验收当作实际部署安全</h3>
<p>历史 incumbent 可能已违反当前规则。需要单独核验 deployed program 与回退目标；拒绝新候选并不自动修复旧版本。[[S450]]</p>
<h3>C4 · 改进的安全诊断器本身不能削弱安全规则</h3>
<p>Meta-Admission 只能改变风险假设、额外测试分配及受限动作建议。独立授权、安全不变量、发布/回滚权限与最终验收仍归不受候选 Agent 控制的验证层。安全合同的合法修改必须经过授权流程。[[S453]][[S454]]</p>
'''),
 ("insight","Insight｜历史的自修改后果，是下一代风险诊断的训练信号",'''
<p>一次更新的局部得分和已知测试通过率并不能完整描述它的后果。修改了哪里、历史上类似变更如何失败、什么授权状态曾经触发异常、未来 Skill 在哪些情境下被检索，可能共同决定哪些额外安全测试值得优先执行。</p>
<p><b>机制假设：</b>Agent 从版本差异、独立执行轨迹及已验证恢复中，学习<strong>“哪种修改容易在什么条件下破坏安全不变量”</strong>，进而改进有限预算下的测试排序和更新处置，而不是泛泛生成一个“安全风险分数”。</p>
<div class="equation">Prior Version Effects → Risk Hypotheses → Selective Tests → Independent Admission → Successor Outcomes → Improved Meta-Admission</div>
<p>一个高不确定候选可以被暂缓或隔离，并在后续获得更有辨别力的证据后重新接纳；但风险预测器本身绝不能免除固定硬约束测试，也不能通过提高局部收益抵消真正的越权行为。</p>
<p><b>判断 RSI 是否成立：</b>若旧规则 m₀ 与更新后的 m₁ 面对<strong>相同候选、相同独立门、相同测试预算和未见风险家族</strong>时，m₁ 产生更好的安全接纳决策，才说明决策规则本身进步了。仅换更强的 LLM 或额外做很多测试不是这个机制。</p>
'''),
 ("design","Design｜可学习的风险诊断层 + 独立不可绕过的安全发布门",'''
<div class="flow">
<div><b>第 k 代提出候选改进</b><small>初版固定 Skill / Harness 编辑器、权限合同和候选池</small></div>
<div><b>Meta-Admission 风险诊断</b><small>只读历史、diff、已知合同和审计轨迹；挑选额外验证</small></div>
<div><b>独立安全验收</b><small>授权、不变量、当前部署与回滚目标；不得由候选 Agent 改写</small></div>
<div><b>接纳 / 隔离 / 暂缓 / 拒绝</b><small>对外部专家和新模块同样执行最小权限与安全检查</small></div>
<div><b>记录后代真实后果</b><small>未见任务违规、旧能力、有效新能力与全部计算成本</small></div>
<div><b>改进下一代诊断规则</b><small>只学习风险识别和验证选择，保留外部硬门</small></div>
</div>
<div class="table-wrap"><table><thead><tr><th>受限动作</th><th>实施方式</th><th>关键条件</th></tr></thead><tbody>
<tr><td><b>Accept</b></td><td>接纳并继承通过独立合同的修改</td><td>仍需核验实际 deployed 版本与关键回归</td></tr>
<tr><td><b>Isolate</b></td><td>高不确定能力放入受控独立 Skill/Adapter，或转交经验证的外部模型</td><td>调用权限、信息流、路由和后续检索都必须验证；隔离不是免检</td></tr>
<tr><td><b>Defer</b></td><td>暂不写回核心，记录缺少哪些证据和重访条件</td><td>现有已验证方案继续服务；重要功能不能无限拖延</td></tr>
<tr><td><b>Reject / Recover</b></td><td>拒绝违规候选；若 incumbent 已不安全，使用当前验收通过的安全回退</td><td>拒绝候选、正在运行程序、回滚版本必须分开记录</td></tr>
</tbody></table></div>
<div class="equation">Maximize: Verified Safe Capability Gain per Total Validation Cost, subject to Fixed Authorization &amp; Safety Invariants</div>
<p><b>两个层次：</b>可学习层优化风险假设、测试分配和接纳建议；独立层持有授权规则、测试结果、发布权限与审计日志。<strong>安全关键不变量不能由自修改 Agent 自动放宽。</strong>有限测试只能支持具体评测协议下的经验可靠性，不能对所有未来状态作出形式化保证。</p>
'''),
 ("p0","P0｜同样局部收益，后代安全风险能否显著不同？",'''
<p><b>最先验证现象，不先训练风险模型。</b>初版使用受控沙箱中的版本化 Skill 与 Harness；底座 LLM、编辑器、候选生成规则、旧回归套件和权限检查器固定。准备文件移动、所有权转移、批处理、依赖关系等具有程序化授权真值的任务。让不同更新分支拥有相近的局部能力提升和旧测试成绩，再评估隐藏的后续合同组合与新会话复用。</p>
<div class="table-wrap"><table><thead><tr><th>受控条件</th><th>应观察到什么</th><th>能检验什么</th></tr></thead><tbody>
<tr><td><b>A · 合法新能力</b></td><td>任务增益真实，跨授权状态仍合规</td><td>安全更新不能被全部拒绝</td></tr>
<tr><td><b>B · 局部成功但组合授权错误</b></td><td>旧回归通过，新组合触发不安全操作</td><td>是否存在旧测试以外的可预测风险</td></tr>
<tr><td><b>C · Skill 跨会话遗留</b></td><td>任务结束后，保留的 Skill 在新会话正常输入下激活</td><td>写入、检索、执行的因果链，参考 SkillMisevo。[[S451]]</td></tr>
<tr><td><b>D · 合同改变但候选不变</b></td><td>拒绝所有修改后，旧 incumbent 仍不合规</td><td>是否必须恢复正在运行的版本。[[S450]]</td></tr>
</tbody></table></div>
<p><b>控制：</b>统一候选更新规模、原始任务、成功收益、测试次数与成本；所有后代合同和动作真值事先封存，不得据终测结果筛选版本。记录版本差异、检索路径、执行结果及是否违反独立授权规则。核心样本先使用合法可复现的测试环境和非敏感数据。</p>
<p><b>决定性证据：</b>当已知目标成功率和旧回归差别很小，未来安全失效仍有可重复差异，并且可从更新前的结构证据预判。如果基础回归本身已完整覆盖风险，就无需包装额外的 Meta-Guard。</p>
'''),
 ("p1","P1｜预算相同，能否少漏放危险更新并少误拒安全更新？",'''
<p>P0 发现真实的非局部或跨代风险后，冻结待测候选、授权合同、独立安全门以及锁定的风险家族。所有方法共享相同额外测试次数上限、工具调用预算与外部模型资源；I13 只能选择优先检查哪些条件、建议隔离/暂缓哪些候选，不能删改硬约束。</p>
<div class="table-wrap"><table><thead><tr><th>必须对照</th><th>对照的意义</th></tr></thead><tbody>
<tr><td>Target-only + old-regression</td><td>看只测当前收益和旧任务漏掉多少后代安全问题</td></tr>
<tr><td>Fixed safety suite / Falsifiable Release Gates [[S453]]</td><td>成熟的静态机器可验收门已经足够吗</td></tr>
<tr><td>SafeEvolve write/retrieval governance [[S451]]</td><td>已有 Skill 生命周期治理与 I13 的额外增量</td></tr>
<tr><td>Full validation + validated rollback [[S450]]</td><td>充分验证的成本与安全恢复参考上界</td></tr>
<tr><td>Random / uniform tests；fixed risk threshold</td><td>风险测试选择是否真的来自历史有效证据</td></tr>
<tr><td><b>I13：History-aware selective tests</b></td><td>同一预算下能否减少风险漏放和安全修改误拒</td></tr>
</tbody></table></div>
<p><b>两种错误必须同时报：</b>Unsafe Admission FNR＝实际不安全候选被接纳数 / 全部实际不安全候选数；Safe Update FRR＝实际安全候选被拒数 / 全部实际安全候选数。另报告合法功能净增益、实际 deployed 程序违规率、跨会话 Skill 激活率，以及审计/Probe/推理/专家/回滚总成本和置信区间。</p>
<p><b>避免伪收益：</b>总拒绝可以使不安全候选放行率趋零，却让安全版本没有任何进步；只看“已接纳版本中的违规率”会偏袒它。若固定完整回归在等预算内解决问题，不应声称学习型诊断有必要。</p>
'''),
 ("p2","P2｜真正的 RSI：安全接纳策略能否跨代进步？",'''
<p><b>固定任务模型，交叉测试新旧元策略。</b>将 P0/P1 的真实候选 diff、独立验收、后代执行与恢复结果组成发展集。只允许修改 Meta-Admission Skill 中的风险诊断和额外测试选择规则 mₖ。基础任务 Skill、底座模型、候选编辑器、核心安全契约和发布/回滚权限始终冻结。</p>
<div class="flow">
<div><b>同起点候选池与当前合同</b><small>相同基础模型、功能目标、预算、独立验证器</small></div>
<div><b>m₀ / m₁ / 固定规则分别选择</b><small>未见风险家族，决定额外测试与受限更新动作</small></div>
<div><b>独立接纳并真实回放</b><small>每条历史保留 candidate、accepted、deployed、next-editor-target</small></div>
<div><b>跨多代后验评价</b><small>安全继承、误拒、合法能力净增益、完整成本</small></div>
<div><b>诊断规则继续修订</b><small>反馈只影响风险预测和测试选择，不影响硬门权限</small></div></div>
<p><b>决定性对照：</b>①同一候选配对 m₀ vs m₁；②相同元规则作用于不同编辑目标；③未见授权合同与未见风险家族；④禁止更新元策略的消融；⑤把所有历史直接塞入上下文、只靠更长提示的强基线；⑥冻结候选、不同验证预算的性能—成本曲线。不得用最终测试结果更新 m₁。</p>
<p><b>RSI 成功证据：</b>在相同资源和硬约束下，新版规则更会挑选风险测试、减少漏放和误拒，并在多代任务中保留更多通过安全验收的实际能力增长。单次更好、更多试验或只在见过的危险模板上过拟合，均不足以支撑元级自我改进。</p>
'''),
 ("contract","Evaluation Contract｜单次候选、后代继承与元策略升级是三个结论",'''
<div class="table-wrap"><table><thead><tr><th>证据层级</th><th>必须真实观察的对象</th><th>允许声称什么</th></tr></thead><tbody>
<tr><td><b>Update safety</b></td><td>候选版本在已知合同与独立测试下通过</td><td>当前限定条件的更新准入，不自动保证未来全部状态</td></tr>
<tr><td><b>Successor safety</b></td><td>实际部署、后续 Skill 检索、不同授权和新会话</td><td>所测任务流中的安全继承与回归，不等于所有真实部署场景安全</td></tr>
<tr><td><b>Meta-admission improvement</b></td><td>旧/新诊断规则面对冻结候选与未见风险家族的真实对照</td><td>是否学会了更有迁移性的安全接纳，而非只是多加了一个门</td></tr>
</tbody></table></div>
<p>预先冻结授权合同版本、可修改的 Skill/Harness 表面、独立安全不变量、测试预算、候选池、验证器、专家服务和任务族划分。分别记录 proposal_id、accepted_id、incumbent_id、deployed_id、rollback_target_id、next_editor_target_id；报告所有失败分母、版本样本、调用成本与自我改进决策日志。原可信 RSI 综述已要求分开报告更新、后代和元机制三个层级。[[S454]]</p>
'''),
 ("plasticity","原 Learning Admission 继承备注｜遗忘、未来可塑性与拒绝内化",'''
<p>原候选从“新能力会伤害旧能力，是否拒绝立即内化”出发。Dohare 等 Nature 2024 的 <i>Loss of Plasticity</i> 表明长期训练可能损害未来学习新任务的能力，但不是所有基于 Skill/Harness 的非参数更新都会表现出同样的神经元退化。[[M22]]</p>
<p><b>在 I13 的位置：</b>旧能力回归与 Core-only 独立能力必须报告；System-with-Experts 完成任务不等于核心模型学会。未来学习新任务 C 的成本是扩展到 LoRA/权重更新时的辅助指标，不能成为初版 RSI Safety 的第二个平行主贡献。<a href="reading-notes.html#deep-nature2024-loss-plasticity-dohare">Nature 2024 精读</a> · <a href="idea-i9-practice-switching.html#future-p0">I9 后续 C 学习协议</a>。</p>
<p>对新旧规则还需区别<strong>“都正确但适用场景不同”</strong>和<strong>“旧规则已失效”</strong>。后者应在合法授权的新合同下修正，而不能为了表面保持旧能力永远拒绝必要更新。Isolation / Delegate 也要受同样的最小权限与独立安全验证，不是默认更安全。</p>
'''),
 ("nonlocal-effects","Nature 2026 证据备注｜局部修复可能带来跨领域行为偏移",'''
<p>Betley 等（Nature 2026）在不安全代码或特定不良角色数字训练中观察到非训练领域的失准。它支持<strong>不能只测局部收益</strong>，但没证明正常能力修复一定产生不良行为，也不能直接证明 Skill/Harness 持久复用风险。ICML 2025 已首次系统报告 Emergent Misalignment，ICLR 2024 更早指出部分微调可能影响安全性；之后的 persona 特征干预和 ICML 2026 训练期防御亦有直接成果。[[M450]][[M451]][[M452]][[M453]][[M454]]</p>
<p>如果未来加入权重/LoRA 分轨，需要单独测试目标微调收益、原安全行为及无关文本/JSON/工具调用的独立评测；对照固定训练防御与 I13 的版本准入，不把它们混为同一个组件。<a href="reading-notes.html#deep-nature2026-narrow-misalignment-betley">Nature 2026 13节完整精读</a>。</p>
<p><b>当前论文主线：</b>初版只在可执行的 Skill/Harness RSI 中检验历史风险诊断、有限预算的安全接纳与跨代继承。参数层非局部失准是 Motivation 和后续扩展，不是已经完成的实验证据。</p>
'''),
 ("boundaries","研究定位与 Go / Merge / Stop｜安全层也必须学会安全地改进",'''
<p class="note"><b>NHB 2025/2026 · 机制交叉引用：</b>Holton 等的人类 A→B→A 实验说明相似规则的正迁移可能伴随旧规则错用。这个现象可作为更新前风险假设的基础研究，但原文未测试授权、越权或 Agent 发布流程；I13 仍要求独立权限验收与跨代安全效果，不能将 Rule-Misuse Rate 直接充当安全违规率。<a href="reading-notes.html#deep-nhb2025-transfer-interference-holton">阅读论文 Fig.1–4 与 I3 机制 →</a>。[[E100]]</p>
<div class="table-wrap"><table><thead><tr><th>相邻 Idea / 方法</th><th>与 I13 的独立边界</th></tr></thead><tbody>
<tr><td><a href="ideas.html#idea-1">I1 · 脚手架与外置</a></td><td>重点是学习哪类知识应该内化，撤除帮助后能否独立完成；I13 优先关注跨版本安全准入，外部模型同样受硬约束。</td></tr>
<tr><td><a href="ideas.html#idea-3">I3 · 温故知新</a></td><td>旧规则与新规则发生冲突后如何修复；I13 关注变更提交前的风险识别，同时核验 incumbent 是否已不安全。</td></tr>
<tr><td><a href="idea-i9-practice-switching.html">I9 · 学习顺序</a></td><td>课程 A/B 顺序对未来 C 学习的影响；I13 初版只改变风险测试与接纳，不选择课程。</td></tr>
<tr><td><b>EAFT / RieSelect / CoPE</b> [[M320]][[M321]][[M322]]</td><td>固定模型训练/层选择/专家扩展的更新机制，不能直接当作 RSI 安全层。</td></tr>
<tr><td><b>RSIFlow / MetaSkill-Evolve / Skill∞</b> [[S28]][[S06]][[S320]]</td><td>元技能或改进工作流已经能更新；I13 需证明在固定独立验证门下风险诊断的跨代收益。</td></tr>
<tr><td><b>SafeEvolve / Fixed Gates / Validated Rollback</b> [[S451]][[S453]][[S450]]</td><td>安全写入/检索、固定发布验收和回滚已有先例；不能把增设 Guardrail 本身当作 I13 贡献。</td></tr>
</tbody></table></div>
<div class="table-wrap"><table><thead><tr><th>决定</th><th>预先约定的证据</th></tr></thead><tbody>
<tr><td><b>GO · RSI Safety 独立论文</b></td><td>P0 成立真实局部收益与后代风险分离；P1 同成本降低危险漏放和安全误拒；P2 元接纳策略对未见风险家族实现更好安全净增长。</td></tr>
<tr><td><b>MERGE · 安全门的增量应用</b></td><td>全量验证、SafeEvolve 或普通固定回归已达到相当安全效果；历史感知诊断没有可独立归因的收益。</td></tr>
<tr><td><b>STOP · 不引入新 Meta-Guard</b></td><td>无法区分安全候选与不安全候选，或全部收益只来自更高的测试预算、更大模型和无限拒绝更新。</td></tr>
</tbody></table></div>
<p class="status"><b>状态：I13 · Safety-Aware Update Admission · 研究方案（2026-10-29）。</b>论文相关数字来自 cited works；本项目 P0/P1/P2 尚无真实实验或跨代更新结果。经验安全评估并不等同于对所有未见真实世界状态的形式化保证；安全关键部署必须由独立授权流程控制。</p>
<div class="links"><a class="link-btn" href="ideas.html">返回研究 Idea 总览</a><a class="link-btn" href="reading-notes.html#deep-nature2026-narrow-misalignment-betley">Nature 2026 非局部失准</a><a class="link-btn" href="reading-notes.html#deep-nature2024-loss-plasticity-dohare">Nature 2024 可塑性</a><a class="link-btn" href="references.html">Related Work 来源台账</a></div>
'''),

 ]
}
