"""Unnumbered RSI memory research map; boundaries before standalone numbered ideas."""
PAGE={
 "slug":"memory-research-map",
 "title":"RSI 记忆研究地图｜历史、检索、巩固与未来可学习性",
 "en":"RSI Memory Research Map: State, Retrieval, Consolidation and Learning Decisions",
 "lead":"为什么当前正确率和近期奖励相同的 Agent，下一轮可能学得完全不同？记忆要分别作为学习状态的观测、外部证据、能力巩固材料和学习策略的信息；先做正交实验，再决定是否拆成新的 I 编号。",
 "updated":"2026-10-29",
 "sections":[
 ("phenomenon","现象：当前成绩相同，不代表下次会同样学得好",'''
 <div class="decision"><span class="kicker">UNNUMBERED RESEARCH POOL · 2026-10-29</span><h3>What Does a Learning Agent Actually Need to Remember?</h3>
 <p>两个Agent都能做对70%的规则题，最近奖励也相近。一个刚经历了失败—纠错—泛化，另一个却在靠重复训练记住旧答案。若只看当前分数，它们很难区分；但是如果继续给它们同一批新任务，实际更新后的收益可能不同。<b>这是一项需要通过真实更新验证的假设，不是Nature已经在LLM上观察到的结果。</b></p></div>
 <p><b>原始机制证据：</b>Eckstein等在 <i>Nature Human Behaviour</i>（2026）比较862名参与者的奖励学习，发现加入独立、多时间尺度的记忆变量明显优于只用少量Q值表示历史的模型。Memory-ANN更能复现重复行动、周期探索和非单调的历史影响。它研究<b>人类决策模型</b>而非Agent训练器。[[E370]] <a href="reading-notes.html#deep-nhb2026-hybrid-memory-eckstein">阅读完整十节精读 →</a></p>
 <p><b>一句话研究目标：</b>哪类历史信息会改变一次经验的实际学习价值？哪些应在模型状态中预测，哪些需要在未来被主动检索，哪些适合压缩成规则或写入权重？</p>
 '''),
 ("layers","先分清四种记忆：它们不是同一个变量",'''
 <div class="table-wrap"><table><thead><tr><th>层次</th><th>记录或影响的是什么</th><th>能声称学会了吗？</th></tr></thead><tbody>
 <tr><td><b>S · Learner-state history</b></td><td>训练前的奖励趋势、失败—恢复、重复/切换、旧规则干扰、优化器/权重快照</td><td>仅是诊断：预测状态并不等于凭空增加能力</td></tr>
 <tr><td><b>E · Episodic evidence memory</b></td><td>可验证的任务输入、工具执行、真实反馈、条件与反例，下一任务按需检索</td><td>若依赖检索成功，只能报告有外部记忆时的能力</td></tr>
 <tr><td><b>C · Consolidated knowledge</b></td><td>把Episode抽象成规则、可执行Skill或LoRA权重更新</td><td>撤掉外部辅助后仍能独立迁移，才可称参数能力</td></tr>
 <tr><td><b>M · Meta-memory policy</b></td><td>什么时候保存、检索、纠错、忘却、巩固或推迟，并根据后果修订选择规则</td><td>须证明学习策略在新任务/后代更好，不是只换一个Router</td></tr>
 </tbody></table></div>
 <p><b>两条需要切开的因果方向：</b>(1) 过去训练改变了模型参数与优化器状态，历史日志帮助预测将来怎样更新；(2) Agent决策器真正读取历史并选择不同学习动作，导致不同训练结果。第一条可能只是隐藏参数状态的代理，第二条才是可干预的记忆控制。两个完全相同的参数、优化器和未来训练流，若无人读取日志，确定性更新不会因为日志文本本身不同而改变。</p>
 '''),
 ("candidates","四个正交候选：先积累机制证据，暂不编号",'''
 <div class="table-wrap"><table><thead><tr><th>候选 / 具体问题</th><th>实验只改变什么</th><th>决定性证据</th><th>现有相邻研究</th></tr></thead><tbody>
 <tr><td><b>A · 历史状态诊断</b><br>当前成绩一样，历史能预测下一次学得怎样吗？</td><td>固定模型快照和未来C训练合同，只改变预测器看到的历史粒度</td><td>超过当前分数、窗口统计、梯度/表示和优化器强基线的未来净学习收益预测；跨规则家族成立</td><td>本文Memory-ANN是认知类比；与<a href="idea-i9-practice-switching.html">I9</a>历史顺序重叠 [[E370]]</td></tr>
 <tr><td><b>B · 记忆检索的因果价值</b><br>保存的哪个Episode真的该被重新拿出来？</td><td>固定全部原始Episode与Agent，只随机干预一次候选Memory是否被检索</td><td>同token/调用预算下未见任务成功增量、错误误用与检索成本；跨条件的负效用也成立</td><td><a href="reading-notes.html#deep-memory-management-acl2026-xiong">ACL2026 Experience Following</a>、Memory-R1已研究读写策略 [[M530]]</td></tr>
 <tr><td><b>C · 原始经验的巩固</b><br>正确经验什么时候值得变成规则/Skill/LoRA？</td><td>固定入选Episode，正交比较Raw/Abstract/Skill/LoRA及必要时Defer</td><td>撤辅后独立迁移与新条件误用、旧能力回归和全成本；抽象有时好有时坏的可预测交互</td><td>本站已有<a href="experience-consolidation.html">经验巩固候选</a>；MSCE已做有证据的Memory→Skill [[M534]]</td></tr>
 <tr><td><b>D · 记忆与学习控制</b><br>历史会帮助下一轮选题、停学、更新接纳吗？</td><td>固定候选动作、任务池、训练预算和验证器，仅改变策略读取历史状态与否</td><td>新规则家族的长期净学习曲线高于简单固定/随机/上下文只读与强记忆管理器</td><td>Memory-R1、<a href="ideas.html#idea-1">I1</a> 与<a href="learning-admission.html">I13</a>存在明显交叉 [[M530]][[M531]]</td></tr>
 </tbody></table></div>
 <p><b>本记忆地图不新增编号：</b><a href="learning-rule-evolution.html">I14 已独立研究学习规则自进化</a>，固定任务、顺序与教师，只改变更新规则。这里的A历史状态诊断可先进入I9/I14的机制对照；C保留经验巩固候选；B/D已有记忆管理与元控制近邻，必须先得到独立因果证据，才考虑未来是否另占I15及后续编号。</p>
 '''),
 ("p0","最值得先做的P0：历史预测与真实LoRA学习收益",'''
 <p><b>Stage 0 · 能力匹配：</b>固定模型家族、A/B题目多重集合和更新预算，仅随机化集中/交错、错误反馈重访与干扰顺序。冻结A/B新题、第三任务C前测和旧能力检查；用预注册容差报告匹配覆盖率，不事后只挑效果好的快照。</p>
 <p><b>Stage 1 · 相同后续训练：</b>给每个快照同样的C训练材料和LoRA步骤，清空训练时外部提示，测未见组合、规则纠错、A/B遗忘与实际成本。将每条历史的未来结果作为训练前预测目标，而不是在训练前偷看后测答案。</p>
 <div class="table-wrap"><table><thead><tr><th>对照预测器</th><th>所见状态</th><th>成本与碰撞</th></tr></thead><tbody>
 <tr><td>B0 · Score only</td><td>当前正确率、近期reward均值</td><td>最简单必要下界</td></tr>
 <tr><td>B1 · Handcrafted</td><td>相同窗口内趋势/方差/重复与错误恢复</td><td>检查是否真的需要高维记忆</td></tr>
 <tr><td>B2 · Sequence encoder</td><td>训练之前观察到的完整事件顺序或固定窗口事件序列</td><td>序列长短和编码器训练成本计入总预算</td></tr>
 <tr><td>B3 · Strong state</td><td>当前训练loss、梯度/表示、优化器状态、参数版本（若可用）</td><td>防止把旧历史的代理效应误认为新的因果记忆</td></tr>
 <tr><td>B4 · Negative control</td><td>等频次打乱、删除关键事件、伪历史配对</td><td>验证模型是否在读真正的时间结构</td></tr>
 </tbody></table></div>
 <p><b>主指标：</b>预注册 C 的真实新题净增益 / 新规则迁移 − λ×旧能力损失 − μ×诊断及训练成本（按可比单位归一化）；另独立报告原始分项及Pareto，不允许只报一个加权总分。预测器选择C学习动作后，还须验证同预算未来任务的净收益是否真的改善。</p>
 <div class="flow"><div><b>同材料不同历史</b><small>A→B / B→A / 交错</small></div><div><b>匹配当前能力</b><small>控制A/B/C前测</small></div><div><b>历史状态诊断</b><small>B0–B4竞争</small></div><div><b>真正学新任务C</b><small>固定LoRA和数据</small></div><div><b>独立后测与学习选择</b><small>迁移/保留/成本</small></div></div>
 <p><b>Go/Stop：</b>若B2只优于B0但不优于B1/B3，不应宣称发现了一种不可压缩的历史学习状态。若B2可预测但主动使用并未改善未来学习选择，则只保留诊断贡献，不包装为RSI自我改进算法。</p>
 '''),
 ("literature","相关顶会证据：记忆已经做到了哪一步？",'''
 <div class="table-wrap"><table><thead><tr><th>证据</th><th>别人研究的是……</th><th>我们还要验证……</th></tr></thead><tbody>
 <tr><td><b>Nature Human Behaviour 2026 · Memory-ANN</b> [[E370]]</td><td>独立历史状态可提高人类下一动作的拟合、再现非单调的选择历史效应</td><td>状态是否预测真实LLM下一轮LoRA的独立净学习，而不是人的行为选择</td></tr>
 <tr><td><b>ACL 2026 · Memory-R1</b> [[M530]]</td><td>经理/回答Agent经RL学习ADD、UPDATE、DELETE、NOOP、记忆筛选与QA</td><td>明确跨模型代际的训练后能力和未来学习收益，避免只重做记忆管理</td></tr>
 <tr><td><b>ACL 2026 · Storage→Experience survey</b> [[M531]]</td><td>综述存储、反思和经验抽象的演化路线</td><td>做严格的独立因果对照，不以重新分类作为创新点</td></tr>
 <tr><td><b>Findings ACL 2026 · MLE Agents</b> [[M532]]</td><td>记忆能帮助chain式迭代，却可能损害tree搜索的多样性</td><td>哪些历史在不同探索结构中应故意不被检索</td></tr>
 <tr><td><b>Findings ACL 2026 · Memory forgetting</b> [[M533]]</td><td>旧记忆可能被过度复用，环境变化时记忆更新失败</td><td>任务边界条件及过期经验如何进入版本安全回归</td></tr>
 <tr><td><b>Findings EMNLP 2026 · Memory→Skill</b> [[M534]]</td><td>有证据链和条件的经验转换可调用Skill已经存在</td><td>何时必须保留原始证据、何时抽象比原样更好、何时真正值得参数化</td></tr>
 </tbody></table></div>
 <p><b>结论：</b>读写、长时检索、删除、抽象、技能化都有强最近邻。我们要从“增加Memory”移到“记忆究竟提供什么独立可学习信息、导致何种可验证的后续更新差异”。</p>
 '''),
 ("visuals","Figure 3i与Figure 4g：历史时间尺度图怎么画？",'''
 <div class="table-wrap"><table><thead><tr><th>图</th><th>学习它的可视化结构</th><th>必需原始数据</th></tr></thead><tbody>
 <tr><td><b>F3i · latent state decoding</b></td><td>按不同PC分组的历史解码强度×lag曲线；短期峰与长时基线分开</td><td><code>model_id, seed, PC_id, lag, probe_coefficient, fit_split, uncertainty</code></td></tr>
 <tr><td><b>F4g · lagged-history effects</b></td><td>人类vs模型的过去奖励/动作影响系数与95% CI；零基线，不隐去负方向</td><td><code>participant_or_model, feature_type, lag, regression_beta, bootstrap_low, bootstrap_high</code></td></tr>
 </tbody></table></div>
 <p>这两个结构适合展示“历史中哪一段仍有用”。但图内任何点、曲线、置信区间必须基于实际日志和训练统计，不能复制认知实验的数值作为RSI结果。<a href="https://www.nature.com/articles/s41562-025-02324-0/figures/3" target="_blank" rel="noopener noreferrer">Nature Figure 3</a> · <a href="https://www.nature.com/articles/s41562-025-02324-0/figures/4" target="_blank" rel="noopener noreferrer">Nature Figure 4</a>。</p>
 '''),
 ("route","后续拆题的决策方式",'''
 <p><b>近期：</b>先把A作为 <a href="idea-i9-practice-switching.html">I9</a>的预测与机制消融，加到其“当前能力相近、未来任务C学习曲线不同”的现有实验，不改变I9已冻结的教材/顺序主线。并列维持<a href="experience-consolidation.html">经验→长期能力候选</a>：它的独立变量是经验存放和巩固方式，不是状态预测器。</p>
 <p><b>中期：</b>若A的结果能超越参数状态、梯度信号与简单历史特征，或者B发现稳定的有害/有益记忆调用交互，才分别审查是否升级为独立I方案。若C仅重复已有Memory→Skill工作则继续归档，不争编号。</p>
 <p><b>RSI的中心约束：</b>当前回答更像人、单任务答对更多、记忆库增长，都不等于后代真的更会学习。必须执行同一训练更新、撤除临时提示、测未见任务净能力、旧能力和总成本。</p>
 <p class="status">状态：科研机制地图/待验证候选；未新建I14–I17，未进行真实模型训练，论文原始人类认知实验与RSI假设严格分开。</p>
 ''')
 ]
}
