# RSI × 自主学习研究

核验日期：2026-10-27

本文件包含证据综述与待验证提案，不包含本项目实验结果。

## RSI × 自主学习研究 / 当前研究池：I1–I8 八个问题

<p>我们关心的不只是 Agent 能不能在一次任务里拿到更高分，而是：<strong>它能不能通过改写自身 Skill、Memory、Harness 或参数，真正学会下一次如何学得更好？</strong></p>
<div class="idea-board">
<a class="idea-board-card" href="ideas.html#idea-1"><span class="idea-id">I1 · 脚手架学习</span><b>哪些该自己学会，哪些用时再查？</b></a>
<a class="idea-board-card" href="idea-i2.html"><span class="idea-id">I2 · 因材施教</span><b>学生越来越会做题，教师也能越来越会教吗？</b></a>
<a class="idea-board-card" href="ideas.html#idea-3"><span class="idea-id">I3 · 温故知新</span><b>新方法有用却伤了旧能力，怎么办？</b></a>
<a class="idea-board-card" href="ideas.html#idea-4"><span class="idea-id">I4 · 生产性失败</span><b>失败一次就总结，还是再试几次？</b></a>
<a class="idea-board-card" href="idea-i5.html"><span class="idea-id">I5 · 十模型互教</span><b>什么时候交换舞伴，才能一起变强？</b></a>
<a class="idea-board-card" href="idea-i6-failure-value.html"><span class="idea-id">I6 · 错误轨迹</span><b>哪次失败值得学，什么时候该停下再回来？</b></a>
<a class="idea-board-card" href="idea-i7-learning-order.html"><span class="idea-id">I7 · 学习顺序</span><b>先独立尝试，还是先看正确示范？</b></a>
<a class="idea-board-card" href="i8.html"><span class="idea-id">I8 · 纠错迁移</span><b>纠正哪个错误，能让我学会一整类题？</b></a>
</div>
<p><b>I2 最新合并：</b>保留因材施教与小预算试学，增加教师自身的教学更新；分别证明学生独立能力和教师教学能力增长。<a href="idea-i2.html">进入师生共进化方案</a>。</p>
<p>I1–I5 每项都按 Challenge → 现有工作 → Insight → Design → 实验设计展开；其中 <a href="idea-i5.html"><b>I5</b></a> 专门研究十模型互教的动态配对与交换顺序，不重新设计学习方法。<b>I6</b> 固定错误终点与教学过程，比较失败轨迹的学习价值，并用它决定继续、换错题或暂缓重访；<b>I7</b> 固定教材与预算，比较尝试和示范的先后顺序；<b>I8</b> 则验证高置信度错误、前置知识与共享规则对纠错迁移的作用。<a href="ideas.html">研究方向总览</a> · <a href="idea-i6-failure-value.html">I6</a> · <a href="idea-i7-learning-order.html">I7</a> · <a href="i8.html">I8</a></p>
<p>例如 R²Orch / PATS 已研究支架撤除；RSIFlow 已选择自改进工作流；HCL / SkillBoost 已研究回归；ActiveSaddler 已选有用的失败；PopuLoRA / OPCoD / MACE 已涉及群体教学、反馈和伙伴探索。我们需要回答比这些工作更细的问题。<a class="cite" href="references.html#S26" title="R²Orch: Recursive Self-Improvement for Agent Orchestration via Self-Play within a Skill-Internalization Loop">[S26]</a><a class="cite" href="references.html#S27" title="PATS: Policy-Aware Training Scaffolding for Agentic Reinforcement Learning">[S27]</a><a class="cite" href="references.html#S28" title="RSIFlow: Adaptive Self-Improvement Workflows with an Evolving Meta-Agent">[S28]</a><a class="cite" href="references.html#S29" title="Harness Continual Learning: Continual Adaptation Beyond Model Parameters">[S29]</a><a class="cite" href="references.html#S30" title="Rethinking Self-Evolution: A Constrained Exploration-Exploitation Process for Mitigating Skill Overfitting (SkillBoost)">[S30]</a><a class="cite" href="references.html#S16" title="ActiveSaddler: Automated Curriculum Learning for Agent Harness Optimization">[S16]</a><a class="cite" href="references.html#S32" title="PopuLoRA: Co-Evolving LLM Populations for Reasoning Self-Play">[S32]</a><a class="cite" href="references.html#S33" title="Be My Tutor: On-Policy Co-Distillation for Mutual LLM Improvement via Peer Feedback (OPCoD)">[S33]</a><a class="cite" href="references.html#S34" title="Multi-Agent LLMs Fail to Explore Each Other (MACE: Multi-Agent Contextual Exploration)">[S34]</a></p>

## RSI × 自主学习研究 / 研究导航：从证据走到可执行实验

<div class="route-grid">
<a href="idea-i2.html"><b>I2：因材施教的师生共进化</b><span>教师从学生真实学习收益中改进教法；学生持续获得独立能力。</span></a>
<a href="timeline.html"><b>研究时间轴</b><span>CVPR / ICML / ACL DDL、论文阅读进度与研究节点。</span></a>
<a href="ideas.html"><b>I1–I5：具体学习机制</b><span>Challenge、现有工作、Insight、Design 与实验设计，统一为可直接讨论的研究卡片。</span></a>
<a href="idea-i5.html"><b>I5：十模型互教与交换舞伴</b><span>Nature 群体学习、Jigsaw 与双向共进化的动态伙伴网络。</span></a>
<a href="idea-i6-failure-value.html"><b>I6：哪些失败值得学，何时该停？</b><span>同题同错误终点的轨迹为什么学习价值不同；何时换错题、暂缓和重访？</span></a>
<a href="idea-i7-learning-order.html"><b>I7：先自主尝试还是先看例题？</b><span>相同教材的学习顺序是否改变未来独立解题和可探索路径？</span></a>
<a href="i8.html"><b>I8：错误规则的跨题可学习性</b><span>从 Hypercorrection 出发，分析前置知识、共同错误规则与净学习收益。</span></a>
<a href="idea-i6.html"><b>历史草案：跨轮瓶颈切换</b><span>原版 I6 研究记录单独保留，不再使用当前 I6 编号。</span></a>
<a href="literature.html"><b>RSI 文献与竞争边界</b><span>改什么、如何改，哪些研究已进入元层自进化。</span></a>
<a href="reading-cards.html"><b>论文精读卡片</b><span>按信号、新信息、可采样性、保持和安全五问检索。</span></a>
<a href="reading-notes.html"><b>论文完整精读</b><span>保留方法细节、例子和已核实的论文信息。</span></a>
<a href="cross-domain.html"><b>相邻领域方法</b><span>元学习、课程、知识追踪、双重控制与持续学习。</span></a>
<a href="learning-science.html"><b>教育学与学习科学</b><span>哪些教育学机制有实证支持，哪些迁移仍是猜想。</span></a>
<a href="experiments.html"><b>实验执行方案</b><span>版本控制、持久更新、数据隔离与元学习评估。</span></a>
<a href="references.html"><b>来源与核验记录</b><span>109 条论文和官方资源，保留原始链接与阅读深度。</span></a></div>

## RSI × 自主学习研究 / 必须分开的三个研究主张

<div class="table-wrap"><table><thead><tr><th>主张</th><th>应观察什么</th><th>不能据什么下结论</th></tr></thead><tbody>
<tr><td>眼前任务做得更好</td><td>有人帮忙、提示或额外执行后的成功率。</td><td>当前题目答对，就说自己学会。</td></tr>
<tr><td>Agent 获得了持久能力</td><td>只保留版本化 Skill / Memory / Harness / 参数，清空临时上下文，在新任务上仍进步。</td><td>答案、同伴或教师仍在上下文里。</td></tr>
<tr><td>Agent 更会自我改进</td><td>保留学到的学习策略，重置任务 Agent，在新的任务流中能否更快改进。</td><td>迭代次数更多、模型更大或训练预算更多。</td></tr>
</tbody></table></div>
<p>只要设计了循环，就能叫自我迭代，但<strong>要声称“递归地改进改进器”还需要额外证据</strong>。如 MetaSkill-Evolve 已研究元技能进化，不能再把“有两个循环”本身作为创新。<a class="cite" href="references.html#S06" title="MetaSkill-Evolve: Recursive Self-Improvement of LLM Agents via Two-Timescale Meta-Skill Evolution">[S06]</a></p>
<div class="note">独立评测必须固定并与训练数据隔离；能力提升不会自动扩大 Agent 的真实工具权限。即便改进器学习，安全审计仍应独立。</div>

## RSI × 自主学习研究 / 从教育学概念到论文问题，怎么做？

<ol class="research-steps">
<li><b>先说一个生活中的具体例子。</b>例如为什么新 Skill 影响旧 Skill，或为何同样 Bug 有人看示范就会、有人不会。</li>
<li><b>说清最近邻研究了什么。</b>不能因为前人没用“费曼”“温故知新”这些词，就认定没人研究机制。</li>
<li><b>问一个更具体的差异。</b>别人研究哪个失败值得修，我们研究失败后下一次试验何时该做、什么时候可以归纳。</li>
<li><b>定义 Agent 真的学到了什么。</b>明确 Skill / Memory / Harness / 权重的可持久写入与回滚。</li>
<li><b>先做最小对照。</b>同预算比较固定简单策略与我们的方法，排除更多尝试、更多 token、外部答案泄漏。</li>
<li><b>再检验长期进步。</b>连续多轮、新任务、旧能力回归，最后才评价改进策略本身有没有变好。</li>
</ol>

## RSI × 自主学习研究 / 网站范围、历史方案与证据状态

<p>这是聚焦 RSI 选题的定向研究站，不是穷尽全领域的系统综述。<a href="ideas.html"><b>I1–I5 最新描述</b></a>以 2026-10-27 的问题表述为准：<a href="idea-i5.html">I5 主线</a>为“十模型按双向独立学习收益动态配对与决定换伴”；目前 <a href="idea-i6-failure-value.html">I6</a> 聚焦失败轨迹，<a href="idea-i7-learning-order.html">I7</a> 聚焦学习顺序。<a href="idea-i6.html">旧版瓶颈切换</a>已归档，不再占用 I6 编号。</p>
<p><a href="idea-i5.html#teaching-feedback">I5 统一详情页</a>同时保留“教学反馈诊断”作为历史研究支线：学生的误解能否暴露教师自己的隐性缺陷。它与当前的“动态伙伴选择”有不同的研究问题，因此在详情页中区分，不再在左侧目录重复出现。</p>
<p><a href="i8.html">I8</a> 研究不同知识准备程度和共享错误规则的跨题迁移；<a href="idea-i6-failure-value.html">I6</a> 则保持同题同错误终点，研究失败过程本身。两者可复用对照平台，但主张不能混用；所有研究都尚待真实训练验证。</p>
<p>原 <a href="/">Agent 自进化研究站</a>与本 RSI 站互相跳转。旧研究池中已经存在 Delayed Regression Exams 等关于回归测试的方案；I3 必须研究主动巩固操作本身，不能重新包装“多测一次”。</p>
<div class="status-strip"><b>截至 2026-10-27</b><span>I1–I8 候选研究问题已整理</span><span>最近邻来源已列出</span><span>独立实验待开展</span><span>不声称首次或已验证</span></div>

## RSI 研究时间轴 / 投稿目标与时间轴概览

<div class="rsi-tl-intro">
    <div class="rsi-tl-intro-main"><span class="rsi-tl-kicker">RSI / RESEARCH ROADMAP / 2026—2027</span>
    <h3>研究进展与投稿窗口，在同一条时间轴上。</h3>
    <p>将 RSI 论文阅读和资料整理记录，与目标会议正式 DDL 分层展示。所有日期都保留原始来源，<b>未公布的截稿日期不采用猜测值</b>。</p></div>
    <div class="rsi-tl-overview">
      <div><strong>03</strong><span>目标会议</span></div>
      <div><strong>04</strong><span>已确认投稿节点</span></div>
      <div><strong>02</strong><span>精读论文卡片</span></div>
    </div>
</div><p class="rsi-tl-validation">信息核验：2026-10-27 · 所有已确认投稿节点均为 23:59 AoE（UTC−12）；倒计时按 UTC−12 的真实截止时刻计算，非本地日历零点。</p>

## RSI 研究时间轴 / 会议 DDL · CVPR / ICML / ACL

<div class="rsi-tl-venue-grid"><article class="rsi-tl-venue rsi-tl-venue--official" id="cvpr-2027">
        <div class="rsi-tl-venue-top"><span class="rsi-tl-venue-serial">CVPR <small>2027</small></span>
        <span class="rsi-tl-status rsi-tl-status--official">官方已确认</span></div>
        <h3>IEEE/CVF Conference on Computer Vision and Pattern Recognition</h3><p class="rsi-tl-track">Computer Vision · Embodied AI</p>
        <ul class="rsi-tl-deadlines"><li class="rsi-tl-ddl" data-status="official"><span class="rsi-tl-ddl-name">论文注册 / 摘要</span><span class="rsi-tl-ddl-date">2026-11-10 <small>AoE 23:59</small></span><span class="rsi-tl-countdown" data-countdown="2026-11-10T23:59:00-12:00">官方日期</span></li><li class="rsi-tl-ddl" data-status="official"><span class="rsi-tl-ddl-name">主会全文投稿</span><span class="rsi-tl-ddl-date">2026-11-16 <small>AoE 23:59</small></span><span class="rsi-tl-countdown" data-countdown="2026-11-16T23:59:00-12:00">官方日期</span></li><li class="rsi-tl-ddl" data-status="official"><span class="rsi-tl-ddl-name">补充材料</span><span class="rsi-tl-ddl-date">2026-11-23 <small>AoE 23:59</small></span><span class="rsi-tl-countdown" data-countdown="2026-11-23T23:59:00-12:00">官方日期</span></li></ul>
        <p class="rsi-tl-venue-context">官方公布的 2027 主会投稿节点。注册/全文/补充材料是不同截止时间。</p>
        <a class="rsi-tl-source-link" href="https://cvpr.thecvf.com/Conferences/2027/Dates" target="_blank" rel="noopener noreferrer">
          查看官方投稿日程 ↗</a>
        </article><article class="rsi-tl-venue rsi-tl-venue--pending" id="icml-2027">
        <div class="rsi-tl-venue-top"><span class="rsi-tl-venue-serial">ICML <small>2027</small></span>
        <span class="rsi-tl-status rsi-tl-status--pending">等待官方</span></div>
        <h3>International Conference on Machine Learning</h3><p class="rsi-tl-track">Machine Learning · RSI</p>
        <ul class="rsi-tl-deadlines"><li class="rsi-tl-ddl" id="icml-2027-abstract" data-status="pending"><span class="rsi-tl-ddl-name">摘要注册</span><span class="rsi-tl-ddl-date">待公布</span><span class="rsi-tl-pending">不显示预测倒计时</span></li><li class="rsi-tl-ddl" id="icml-2027-paper" data-status="pending"><span class="rsi-tl-ddl-name">主会全文投稿</span><span class="rsi-tl-ddl-date">待公布</span><span class="rsi-tl-pending">不显示预测倒计时</span></li></ul>
        <p class="rsi-tl-venue-context">截至 2026-10-27，未核实到 ICML 2027 官方投稿日程。第三方预测及 ICML 2026 的日期不能作为 2027 DDL。</p>
        <a class="rsi-tl-source-link" href="https://icml.cc/" target="_blank" rel="noopener noreferrer">
          查看会议主办方网站 ↗</a>
        </article><article class="rsi-tl-venue rsi-tl-venue--official_partial" id="acl-2027">
        <div class="rsi-tl-venue-top"><span class="rsi-tl-venue-serial">ACL <small>2027</small></span>
        <span class="rsi-tl-status rsi-tl-status--official_partial">部分确认</span></div>
        <h3>Annual Meeting of the Association for Computational Linguistics</h3><p class="rsi-tl-track">NLP · LLM Agents</p>
        <ul class="rsi-tl-deadlines"><li class="rsi-tl-ddl" data-status="official"><span class="rsi-tl-ddl-name">ARR 投稿截止</span><span class="rsi-tl-ddl-date">2027-01-04 <small>AoE 23:59</small></span><span class="rsi-tl-countdown" data-countdown="2027-01-04T23:59:00-12:00">官方日期</span></li><li class="rsi-tl-ddl" id="acl-2027-commit" data-status="pending"><span class="rsi-tl-ddl-name">会议 Commitment</span><span class="rsi-tl-ddl-date">待公布</span><span class="rsi-tl-pending">不显示预测倒计时</span></li></ul>
        <p class="rsi-tl-venue-context">ACL 2027 使用 ARR 投稿→会议 Commit 的两阶段流程。ARR 最晚投稿轮次已有官方日期；Commitment 截止未公布。</p>
        <a class="rsi-tl-source-link" href="https://2027.aclweb.org/calls/main/" target="_blank" rel="noopener noreferrer">
          查看官方投稿日程 ↗</a>
        </article></div><p class="rsi-tl-notice"><b>ICML 2027:</b> 当前仅可确认会议主办方官方渠道，未确认 2027 摘要或全文截稿日。ACL 2027 的 ARR 截稿与后续 Commitment 不应混为一个节点；日历中仅对有正式日期的节点生成倒计时。</p>

## RSI 研究时间轴 / 研究活动与投稿时间轴 · 9 个已知日期

<div class="rsi-tl-toolbar"><label for="rsi-tl-kind">事件类型<select id="rsi-tl-kind">
           <option value="all">全部事件</option><option value="deadline">会议 DDL</option>
           <option value="reading">论文精读</option><option value="research">研究记录</option></select></label>
           <label for="rsi-tl-time">时间范围<select id="rsi-tl-time">
           <option value="all">全部时间</option><option value="upcoming">尚未截止</option>
           <option value="past">已结束／已发生</option></select></label>
           <label class="rsi-tl-search" for="rsi-tl-query">检索记录<input type="search" id="rsi-tl-query" placeholder="例如 CVPR、R²Orch、实验、ARR"></label>
           <button type="button" id="rsi-tl-reset">重置</button>
           <output id="rsi-tl-count" aria-live="polite">显示全部</output></div><div class="rsi-tl-months" id="rsi-tl-months"><section class="rsi-tl-month" data-month="2026-10"><div class="rsi-tl-month-head"><h3>2026 年 10 月</h3><span>5 条记录</span></div><div class="rsi-tl-month-body"><article class="rsi-tl-item rsi-tl-item--research" id="rsi-dossier-20261021"
      data-kind="research" data-date="2026-10-21" data-due-at="">
      <div class="rsi-tl-item-date"><time datetime="2026-10-21">10-21</time></div>
      <div class="rsi-tl-item-main">
        <div class="rsi-tl-item-meta"><span class="rsi-tl-kind rsi-tl-kind--research">研究记录</span><span>站内研究记录</span></div>
        <h3>RSI 自主学习研究专题完成首版资料整理</h3>
        <p>网站形成 RSI 文献、跨领域学习科学、候选方向和实验方案的资料页；属于研究文档整理，不代表实验验证完成。</p>
        <div class="rsi-tl-item-footer"><a href="index.html">专题总览 ↗</a></div>
      </div>
    </article><article class="rsi-tl-item rsi-tl-item--research" id="rsi-i2-coevolution-20261027"
      data-kind="research" data-date="2026-10-27" data-due-at="">
      <div class="rsi-tl-item-date"><time datetime="2026-10-27">10-27</time></div>
      <div class="rsi-tl-item-main">
        <div class="rsi-tl-item-meta"><span class="rsi-tl-kind rsi-tl-kind--research">研究记录</span><span>站内研究记录</span></div>
        <h3>I2 合并为因材施教的师生共进化方案</h3>
        <p>核对 Bayesian Teaching、RLT、SOAR、Sherpa、Eduardo、OPCoD 与学生感知蒸馏；区分教师教学能力与学生解题能力，形成交叉验证方案。仅文献与方案更新，无本项目实验结果。</p>
        <div class="rsi-tl-item-footer"><a href="idea-i2.html">I2 完整方案 ↗</a></div>
      </div>
    </article><article class="rsi-tl-item rsi-tl-item--research" id="rsi-i8-mechanism-20261027"
      data-kind="research" data-date="2026-10-27" data-due-at="">
      <div class="rsi-tl-item-date"><time datetime="2026-10-27">10-27</time></div>
      <div class="rsi-tl-item-main">
        <div class="rsi-tl-item-meta"><span class="rsi-tl-kind rsi-tl-kind--research">研究记录</span><span>站内研究记录</span></div>
        <h3>I8 · 错误可学习性与跨题迁移研究方案归档</h3>
        <p>从 Hypercorrection 原始研究出发，提出已有知识、共享错误规则与更新兼容性的待验证关系，列明匹配对照和否定条件；尚无实际训练结果。</p>
        <div class="rsi-tl-item-footer"><a href="i8.html">I8 完整研究记录 ↗</a></div>
      </div>
    </article><article class="rsi-tl-item rsi-tl-item--reading" id="reading-r2orch-2610-22740"
      data-kind="reading" data-date="2026-10-27" data-due-at="">
      <div class="rsi-tl-item-date"><time datetime="2026-10-27">10-27</time></div>
      <div class="rsi-tl-item-main">
        <div class="rsi-tl-item-meta"><span class="rsi-tl-kind rsi-tl-kind--reading">论文精读</span><span>阅读卡片已归档</span></div>
        <h3>精读：R²Orch</h3>
        <p>先把辅助提示拿掉，再判断哪些题值得学、哪些提示可以撤掉。</p>
        <div class="rsi-tl-item-footer"><a href="reading-cards.html#r2orch-2610-22740">打开精读卡片 ↗</a></div>
      </div>
    </article><article class="rsi-tl-item rsi-tl-item--reading" id="reading-rsi-anything-2610-13912"
      data-kind="reading" data-date="2026-10-27" data-due-at="">
      <div class="rsi-tl-item-date"><time datetime="2026-10-27">10-27</time></div>
      <div class="rsi-tl-item-main">
        <div class="rsi-tl-item-meta"><span class="rsi-tl-kind rsi-tl-kind--reading">论文精读</span><span>阅读卡片已归档</span></div>
        <h3>精读：RSI-Anything</h3>
        <p>先预测哪个方案值得测试，再用真实反馈更新系统，最后检查整套 Agent 是否真的变好。</p>
        <div class="rsi-tl-item-footer"><a href="reading-cards.html#rsi-anything-2610-13912">打开精读卡片 ↗</a></div>
      </div>
    </article></div></section><section class="rsi-tl-month" data-month="2026-11"><div class="rsi-tl-month-head"><h3>2026 年 11 月</h3><span>3 条记录</span></div><div class="rsi-tl-month-body"><article class="rsi-tl-item rsi-tl-item--deadline" id="cvpr-2027-registration"
      data-kind="deadline" data-date="2026-11-10" data-due-at="2026-11-10T23:59:00-12:00">
      <div class="rsi-tl-item-date"><time datetime="2026-11-10">11-10</time></div>
      <div class="rsi-tl-item-main">
        <div class="rsi-tl-item-meta"><span class="rsi-tl-kind rsi-tl-kind--deadline">会议 DDL</span><span>官方确认 · AoE</span></div>
        <h3>CVPR 2027 · 论文注册 / 摘要</h3>
        <p>Paper Registration Deadline（AoE）。来源：IEEE/CVF Conference on Computer Vision and Pattern Recognition 官方会议日程。</p>
        <div class="rsi-tl-item-footer"><a href="https://cvpr.thecvf.com/Conferences/2027/Dates" target="_blank" rel="noopener noreferrer">会议官方日期 ↗</a><span class="rsi-tl-live" data-countdown="2026-11-10T23:59:00-12:00">AoE · 23:59</span></div>
      </div>
    </article><article class="rsi-tl-item rsi-tl-item--deadline" id="cvpr-2027-paper"
      data-kind="deadline" data-date="2026-11-16" data-due-at="2026-11-16T23:59:00-12:00">
      <div class="rsi-tl-item-date"><time datetime="2026-11-16">11-16</time></div>
      <div class="rsi-tl-item-main">
        <div class="rsi-tl-item-meta"><span class="rsi-tl-kind rsi-tl-kind--deadline">会议 DDL</span><span>官方确认 · AoE</span></div>
        <h3>CVPR 2027 · 主会全文投稿</h3>
        <p>Submission Deadline（AoE）。来源：IEEE/CVF Conference on Computer Vision and Pattern Recognition 官方会议日程。</p>
        <div class="rsi-tl-item-footer"><a href="https://cvpr.thecvf.com/Conferences/2027/Dates" target="_blank" rel="noopener noreferrer">会议官方日期 ↗</a><span class="rsi-tl-live" data-countdown="2026-11-16T23:59:00-12:00">AoE · 23:59</span></div>
      </div>
    </article><article class="rsi-tl-item rsi-tl-item--deadline" id="cvpr-2027-supplementary"
      data-kind="deadline" data-date="2026-11-23" data-due-at="2026-11-23T23:59:00-12:00">
      <div class="rsi-tl-item-date"><time datetime="2026-11-23">11-23</time></div>
      <div class="rsi-tl-item-main">
        <div class="rsi-tl-item-meta"><span class="rsi-tl-kind rsi-tl-kind--deadline">会议 DDL</span><span>官方确认 · AoE</span></div>
        <h3>CVPR 2027 · 补充材料</h3>
        <p>Supplementary Materials Deadline（AoE）。来源：IEEE/CVF Conference on Computer Vision and Pattern Recognition 官方会议日程。</p>
        <div class="rsi-tl-item-footer"><a href="https://cvpr.thecvf.com/Conferences/2027/Dates" target="_blank" rel="noopener noreferrer">会议官方日期 ↗</a><span class="rsi-tl-live" data-countdown="2026-11-23T23:59:00-12:00">AoE · 23:59</span></div>
      </div>
    </article></div></section><section class="rsi-tl-month" data-month="2027-01"><div class="rsi-tl-month-head"><h3>2027 年 01 月</h3><span>1 条记录</span></div><div class="rsi-tl-month-body"><article class="rsi-tl-item rsi-tl-item--deadline" id="acl-2027-arr"
      data-kind="deadline" data-date="2027-01-04" data-due-at="2027-01-04T23:59:00-12:00">
      <div class="rsi-tl-item-date"><time datetime="2027-01-04">01-04</time></div>
      <div class="rsi-tl-item-main">
        <div class="rsi-tl-item-meta"><span class="rsi-tl-kind rsi-tl-kind--deadline">会议 DDL</span><span>官方确认 · AoE</span></div>
        <h3>ACL 2027 · ARR 投稿截止</h3>
        <p>ACL 2027 的最晚 ARR 投稿轮次（AoE）；其他更早 ARR 轮次也可能适用。来源：Annual Meeting of the Association for Computational Linguistics 官方会议日程。</p>
        <div class="rsi-tl-item-footer"><a href="https://2027.aclweb.org/calls/main/" target="_blank" rel="noopener noreferrer">会议官方日期 ↗</a><span class="rsi-tl-live" data-countdown="2027-01-04T23:59:00-12:00">AoE · 23:59</span></div>
      </div>
    </article></div></section></div><p class="rsi-tl-no-results" id="rsi-tl-empty" hidden>该筛选条件下没有时间轴记录，请调整类型、时间范围或检索词。</p>

## RSI 研究时间轴 / 来源、时间口径与后续扩展

<p>截至 <strong>2026-10-27</strong>，CVPR 2027 的注册、投稿、补充材料三个日期，以及 ACL 2027 的 ARR 投稿日期已从大会官方页面核实。ICML 2027 及 ACL 2027 Commitment 尚未核实到正式 DDL，因此只标记“待公布”。会议截稿以官方最新通知为准。</p><p>本页面的研究记录来自本站已归档的资料与论文精读卡片，<strong>不暗示实验已经成功、已经投稿或会议已经接收。</strong>论文卡片日期从 <code>reading-cards.json</code> 自动读取。</p><p>扩展方法：向 <code>timeline-data.json</code> 增加正式核对过的会议信息、日期和引用；向 <code>research_events</code> 增加可溯源的 RSI 里程碑；运行站点构建脚本后同步更新本页。未知日期必须保留 <code>null</code>。</p><div class="links"><a class="link-btn" href="timeline-data.json" download>下载时间轴结构化数据</a><a class="link-btn" href="reading-cards.html">查看论文精读卡片</a></div>

## RSI 文献与竞争边界 / 机制图谱：从提出修改到学习如何学习

<div class="table-wrap"><table><thead><tr><th>机制层</th><th>代表工作</th><th>已有覆盖</th><th>不能只做什么</th></tr></thead><tbody><tr><td>代码 / Prompt 搜索</td><td>DGM、GEPA <a class="cite" href="references.html#S02" title="Darwin Godel Machine: Open-Ended Evolution of Self-Improving Agents">[S02]</a><a class="cite" href="references.html#S03" title="GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning">[S03]</a></td><td>生成、执行、反思、保留修改。</td><td>把修改流程换成多 Agent 编排。</td></tr><tr><td>参数自适应</td><td>SEAL <a class="cite" href="references.html#S04" title="Self-Adapting Language Models (SEAL)">[S04]</a></td><td>生成训练数据与更新指令，以更新后效果作反馈。</td><td>“自己造数据再微调”。</td></tr><tr><td>可学习编辑器</td><td>Harness-R1、Harness Learning <a class="cite" href="references.html#S07" title="Harness-R1: Learning to Edit Executable Runtime Harnesses from Agent Failure Trajectories">[S07]</a><a class="cite" href="references.html#S08" title="Harness Learning Enables Generalizable Test-Time Adaptation">[S08]</a></td><td>训练可执行修改与跨任务适应策略。</td><td>只把固定 LLM 改成 RL 编辑器。</td></tr><tr><td>元改进 / 两时间尺度</td><td>Hyperagents、MetaSkill-Evolve、Harness² <a class="cite" href="references.html#S05" title="Hyperagents">[S05]</a><a class="cite" href="references.html#S06" title="MetaSkill-Evolve: Recursive Self-Improvement of LLM Agents via Two-Timescale Meta-Skill Evolution">[S06]</a><a class="cite" href="references.html#S12" title="Harness²: Recursive Agent Harnessing for an Open World">[S12]</a></td><td>改进器或其经验参与后续改进。</td><td>用双环图证明“递归”。</td></tr><tr><td>修改泛化与正则</td><td>ModularRSI、RRSI <a class="cite" href="references.html#S09" title="ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement">[S09]</a><a class="cite" href="references.html#S10" title="RRSI: Regularized Recursive Self-Improvement of Agent Harnesses">[S10]</a></td><td>模块化、成败对照、限制过拟合。</td><td>只加 Held-out 门控和跨模型测试。</td></tr><tr><td>预测 / 回放辅助搜索</td><td>Dream-RSI、RSI-Anything <a class="cite" href="references.html#S11" title="Dream-RSI: Recursive Self-Improvement through Evolving Worlds">[S11]</a><a class="cite" href="references.html#S13" title="RSI-Anything: Unlocking Recursive Self-Improvement with World Models">[S13]</a></td><td>借历史或预测减少真实尝试。</td><td>给补丁打分器起名“世界模型”。</td></tr><tr><td>课程与可学性</td><td>ActiveSaddler、SOAR、前瞻课程 <a class="cite" href="references.html#S16" title="ActiveSaddler: Automated Curriculum Learning for Agent Harness Optimization">[S16]</a><a class="cite" href="references.html#S17" title="Teaching Models to Teach Themselves: Reasoning at the Edge of Learnability (SOAR)">[S17]</a><a class="cite" href="references.html#S18" title="Anticipating the Consequences of Curriculum Decisions with Large Language Models">[S18]</a></td><td>决定练什么、依据什么学习收益练。</td><td>只选择成功率居中的任务。</td></tr><tr><td>教学干预与能力获取</td><td>EduardoRL <a class="cite" href="references.html#S19" title="The Assistance Dilemma: Learning to Teach via Multi-Turn Reinforcement Learning">[S19]</a></td><td>将帮助解题与不直接给答案的教学分开。</td><td>仅在评测时删除教师话语。</td></tr></tbody></table></div>

## RSI 文献与竞争边界 / 优先精读的六个最近邻

<div class="card-grid"><article class="research-card"><h3>ActiveSaddler</h3><p>失败模式随 Agent 变化，课程也随之变化。我们的额外变量只能是支持强度、巩固方式或更长时程，而非重新选择失败类别。<a class="cite" href="references.html#S16" title="ActiveSaddler: Automated Curriculum Learning for Agent Harness Optimization">[S16]</a></p><b>追加核验</b><p>模式注册、非平稳性、任务切分与实际代码发布状态。</p></article><article class="research-card"><h3>SOAR</h3><p>教师由学生真正学到多少来奖励。“用学习增益代替难度”不能单独成为贡献。<a class="cite" href="references.html#S17" title="Teaching Models to Teach Themselves: Reasoning at the Edge of Learnability (SOAR)">[S17]</a></p><b>比较边界</b><p>同一出题分布下，教学方式和保留机制是否仍有作用。</p></article><article class="research-card"><h3>前瞻课程</h3><p>估计当前进展之外的下游收益和准备度。新方案须优于同信息量的任务图与通用效果预测器。<a class="cite" href="references.html#S18" title="Anticipating the Consequences of Curriculum Decisions with Large Language Models">[S18]</a></p><b>比较边界</b><p>从实际随机干预学习响应，而非只靠任务语义先验。</p></article><article class="research-card"><h3>The Assistance Dilemma</h3><p>已有遮蔽教师内容的近迁移后测；仍保留学生自身话语，不能直接解释为新会话参数内化。<a class="cite" href="references.html#S19" title="The Assistance Dilemma: Learning to Teach via Multi-Turn Reinforcement Learning">[S19]</a></p><b>比较边界</b><p>多轮不同能力学习之后，怎样获取、撤除帮助并巩固。</p></article><article class="research-card"><h3>Harness Learning / Harness-R1</h3><p>已有学习型修改。先共享其候选编辑能力，只研究学习干预选择，避免混入编辑器差异。<a class="cite" href="references.html#S07" title="Harness-R1: Learning to Edit Executable Runtime Harnesses from Agent Failure Trajectories">[S07]</a><a class="cite" href="references.html#S08" title="Harness Learning Enables Generalizable Test-Time Adaptation">[S08]</a></p><b>比较边界</b><p>同样候选、轨迹和 Token，谁选择的学习过程更好。</p></article><article class="research-card"><h3>评测重审与失败反馈审计</h3><p>对齐普通测试时扩展；目标修复和独立任务收益分开报告。<a class="cite" href="references.html#S14" title="Rethinking the Evaluation of Harness Evolution for Agents">[S14]</a><a class="cite" href="references.html#S15" title="Does Failure Feedback Direct Agent Self-Modification?">[S15]</a></p><b>比较边界</b><p>完整成本、失败修改和冻结检查点，而非只报最好一代。</p></article></div>

## RSI 文献与竞争边界 / 反馈：可信度与可得性要分开

<div class="table-wrap"><table><thead><tr><th>信号</th><th>用途</th><th>不足与处理</th></tr></thead><tbody><tr><td>可执行成功、状态约束</td><td>训练与审计。</td><td>测试覆盖不完整；训练检查与隐藏检查隔离。</td></tr><tr><td>成对执行效应</td><td>比较相同旧版本的不同干预。</td><td>控制环境、更新随机性；单次修复不是因果金标。</td></tr><tr><td>LLM 诊断 / 解释</td><td>提出故障与教学假设。</td><td>不是根因标签，必须经干预检验。</td></tr><tr><td>学习响应预测</td><td>筛选值得执行的学习动作。</td><td>会随分布漂移失准，保留预测与实测误差。</td></tr><tr><td>教师答案</td><td>训练示范或检查候选解。</td><td>若进入测试上下文，会混淆教学与代做。</td></tr></tbody></table></div><p>这些是我们的设计要求，不是在断言已有方法都缺少控制；形式正确的 verifier 也不能自动代表所有实际目标。<a class="cite" href="references.html#S14" title="Rethinking the Evaluation of Harness Evolution for Agents">[S14]</a><a class="cite" href="references.html#S15" title="Does Failure Feedback Direct Agent Self-Modification?">[S15]</a><a class="cite" href="references.html#S19" title="The Assistance Dilemma: Learning to Teach via Multi-Turn Reinforcement Learning">[S19]</a></p>

## RSI 文献与竞争边界 / 教学相长方向的直接竞争与明确边界

<p><b>NeurIPS 2024 LbT</b>：学生学习表现影响教师解释选择和 DPO 权重微调，教师因学生表现改善不是新的事实。<b>AAAI 2026 MARS</b>：Teacher–Critic–Student 与苏格拉底对话已有提示优化实现。<b>SKILL-KD</b>：用师生成功/失败轨迹对照、迭代验证技能补丁，主要改善 Student。<b>Socratic Students</b>：训练 Student 主动提问以提高学生获取知识效率。<a class="cite" href="references.html#S20" title="Can LLMs Learn by Teaching for Better Reasoning? A Preliminary Study">[S20]</a><a class="cite" href="references.html#S21" title="MARS: Multi-Agent Adaptive Reasoning with Socratic Guidance for Automated Prompt Optimization">[S21]</a><a class="cite" href="references.html#S22" title="SKILL-KD: Contrastive Skill Distillation for LLM Agents">[S22]</a><a class="cite" href="references.html#S24" title="Socratic Students: Teaching Language Models to Learn by Asking Questions">[S24]</a></p><p>候选 I5 的额外主张只保留：<strong>学生独立运用教案所得的轨迹，能否发现教师自身在同等预算的直接测试中无法稳定暴露的隐藏知识条件？是否能可靠归因和更新教师自己？</strong> 具体模型、伪代码和最小否定实验见 <a href="teaching.html">I5：教学反馈驱动 Agent 自进化</a>。</p>

## RSI 文献与竞争边界 / 对前面对话方案的收敛

<p><strong>保留：</strong>研究整个改进过程，利用充足算力做同版本分叉；同时评价跨任务、跨模型和长期退化。</p><p><strong>收窄：</strong>训练元控制器、主动选择失败、预测修改收益均有强近邻，须落到明确动作空间与延迟目标，不能单靠模块组合。</p><p><strong>纠正：</strong>公开仓库存在不等于复现通过；不同论文修订的数字不混用；当前 τ-bench 仓库不能直接视为历史 τ² 固定设置。<a class="cite" href="references.html#S10" title="RRSI: Regularized Recursive Self-Improvement of Agent Harnesses">[S10]</a><a class="cite" href="references.html#B02" title="τ-bench / τ²-bench：官方仓库与版本化评测协议">[B02]</a></p><div class="note">本轮没有给任何候选颁发“新颖性通过”。下一阶段应逐节对照最近邻并实际复现，不能因为标题中没有某个词就断言研究空白。</div>

## 论文精读卡片 / 论文卡片库 · 2 篇

<div class="reading-tools"><label for="reading-card-filter">搜索卡片</label><input type="search" id="reading-card-filter" placeholder="论文、单位、方法或机制…" autocomplete="off"><label for="reading-question-filter">对应问题</label><select id="reading-question-filter"><option value="all">全部问题</option><option value="signal">信号对不对</option><option value="novelty">有没有新东西</option><option value="reach">采不采得到</option><option value="retention">吸收了会不会丢</option><option value="safety">安全</option></select><label for="reading-coverage-filter">涉及程度</label><select id="reading-coverage-filter"><option value="addressed">重点或部分涉及</option><option value="core">重点研究</option><option value="partial">部分涉及</option><option value="not_addressed">未直接研究</option><option value="all">全部程度</option></select><span id="reading-card-count" aria-live="polite"></span></div><div class="reading-grid"><article class="reading-card" id="rsi-anything-2610-13912" data-paper-tags="RSI|World Model|Feedback Learning|Pair Retention|JEPA-Anything" data-question-coverage="signal:core|novelty:partial|reach:partial|retention:core|safety:partial">
  <div class="reading-card-head">
    <div class="reading-metadata"><span class="reading-paper-id">RSI-Anything</span><span>arXiv:2610.13912</span><span>阅读 2026-10-27</span><span class="reading-deep-available">含完整精读</span></div>
    <h3>RSI-Anything</h3>
    <p class="reading-full-title">RSI-Anything: Unlocking Recursive Self-Improvement with World Models</p>
    <p class="reading-institution"><b>发表单位（作者署名）</b> PhAI Labs <span>等 8 家署名机构</span></p>
    <div class="reading-tags"><span class="reading-tag">RSI</span><span class="reading-tag">World Model</span><span class="reading-tag">Feedback Learning</span><span class="reading-tag">Pair Retention</span><span class="reading-tag">JEPA-Anything</span></div>
  </div>
  <p class="reading-one-sentence">先预测哪个方案值得测试，再用真实反馈更新系统，最后检查整套 Agent 是否真的变好。</p>
  <div class="reading-story" aria-label="Challenge Insight Design Result 四步读懂"><div class="reading-story-step" data-story-stage="challenge"><h4><span>Challenge</span>难在哪里</h4><p>Agent 能提出很多修复方案，但真实测试很贵；而且 Agent 变强后，旧预测器可能判断不准新方案。</p></div><div class="reading-story-step" data-story-stage="insight"><h4><span>Insight</span>为什么可解</h4><p>先预测哪些方案值得试，可以少花测试成本。真实结果又能纠正预测器，但升级时必须看整套系统是否进步。</p></div><div class="reading-story-step" data-story-stage="design"><h4><span>Design</span>具体怎么做</h4><p>Agent 提方案 → 世界模型预测 → 选择少数方案真实测试 → 按需更新 → 检查新旧组件组合，决定是否保留。</p></div><div class="reading-story-step" data-story-stage="result"><h4><span>Result</span>结果怎么样</h4><p>代码修复：固定生成器时，成功率由 26.3% 升至 31.2%。五轮规划得分由 21.80% 升至 46.01%，但并非同一实验中证明长期联合进化。</p></div></div>
  <div class="reading-issues"><p class="reading-issues-title">自我改进四问 + 安全：这篇研究到哪一步？</p><div class="reading-issue-tags"><span class="reading-issue reading-issue--core" title="评估分数和真实能力是否一致；评估器也在变化时，用什么独立证据校准它。">信号对不对<small>重点研究</small></span><span class="reading-issue reading-issue--partial" title="自己出题、自己造数据时，能够纠正模型的信息究竟从哪里来。">有没有新东西<small>部分涉及</small></span><span class="reading-issue reading-issue--partial" title="高质量解法是否处在可采样的候选空间中，候选支持范围在哪一环节收窄。">采不采得到<small>部分涉及</small></span><span class="reading-issue reading-issue--core" title="改进进入权重、记忆或技能后，旧能力是否保留、错误经验是否被排除。">吸收了会不会丢<small>重点研究</small></span><span class="reading-issue reading-issue--partial" title="评估器被绕过、越权修改真实系统、坏行为被持久记录三类跨环节风险。">安全<small>部分涉及</small></span></div></div>
  <details class="reading-expand">
    <summary>继续看：真实证据、公式和没解决的问题</summary>
    <div class="reading-expanded-content">
      <div class="reading-source-line"><b>作者</b> Taoyong Cui et al. · <b>首发</b> 2026-10-09 · <b>版本</b> v1 · 2026-10 · <b>阅读范围</b> 框架 §2.3–2.5、关键实验与官方项目说明精读；尚未独立复现</div>
      <p class="reading-institutions-full"><b>全部作者单位：</b>PhAI Labs · 香港中文大学 · 澳门大学 · 上海交通大学 · 复旦大学 · 牛津大学 · 斯坦福大学 · 北京大学<br><b>发表状态：</b>PhAI Labs Technical Report · arXiv 预印本 · <b>核对位置：</b>arXiv v1 论文附录 A（Author Affiliations and Correspondence）</p>
      <h4>更新的是哪一部分？</h4><p>真实反馈可以更新 Policy 参数或 Agent Workflow；只有预测不可靠、证据充足且预算允许时才适配 World Model。新 Policy、新 World Model 分别接受检查，再检查二者配对是否优于当前组合；未通过就保留旧版本。</p>
      <h4>自我改进五问：论文做到哪里、还缺什么</h4>
      <p class="reading-taxonomy-caveat">“重点研究”表示直接针对该问题提出机制或证据，不代表问题已被彻底解决。分类属于本站的文献研读判断。</p>
      <dl class="reading-question-details"><div class="reading-question-detail"><dt><span>信号对不对</span><span class="reading-level reading-level--core">重点研究</span></dt><dd><p><b>论文做到：</b>将预测与真实观测配对以检查 World Model 可靠性；Policy、World Model 及其组合分别经过事先规定的接纳检验（§2.4–2.5）。</p><p><b>仍未解决：</b>这里主要校准可更新的预测器；实际任务验证标准保持固定，并未解决评估器自身也会被重写时的真实性锚点问题。</p></dd></div><div class="reading-question-detail"><dt><span>有没有新东西</span><span class="reading-level reading-level--partial">部分涉及</span></dt><dd><p><b>论文做到：</b>用有限的真实程序测试、GUI 交互和科学实验获取外部结果，为下一轮训练提供新的观察反馈（§2.3）。</p><p><b>仍未解决：</b>新信息主要来自外部环境；没有证明完全自生成题目或数据能在封闭循环中不断产生正确的新知识。</p></dd></div><div class="reading-question-detail"><dt><span>采不采得到</span><span class="reading-level reading-level--partial">部分涉及</span></dt><dd><p><b>论文做到：</b>世界模型对已经提出的候选进行预测排序，优先执行有价值的方案，提高有限真实反馈预算的利用率（§2.3）。</p><p><b>仍未解决：</b>候选筛选不等于扩展采样支持集；如果好解最初不在 Policy 能提出的集合里，World Model 也无法将它挑出来。</p></dd></div><div class="reading-question-detail"><dt><span>吸收了会不会丢</span><span class="reading-level reading-level--core">重点研究</span></dt><dd><p><b>论文做到：</b>用版本化 Policy/Workflow、World Model 的组件检验与配对兼容性检验决定是否接受更新并继承到下一轮（§2.5）。</p><p><b>仍未解决：</b>验证的是组件更新和配对收益，不等同于证明长时间不遗忘旧任务、不会把错误经验写入记忆或权重。</p></dd></div><div class="reading-question-detail"><dt><span>安全</span><span class="reading-level reading-level--partial">部分涉及</span></dt><dd><p><b>论文做到：</b>任务协议中固定操作约束、预算和接纳规则，为真正执行候选与保留改进设置基本边界（§2.1、§2.5）。</p><p><b>仍未解决：</b>没有独立覆盖评估器被绕过、Agent 越权操作真实系统，以及恶意行为被持久学习的三类对抗测试。</p></dd></div></dl>
      <h4>核心机制 · 记住这几个公式</h4><ol class="reading-mechanisms"><li><b>预测引导的有限试错</b><p>先预测候选效果和不确定性，用有限的真实测试预算优先验证有价值的候选；未执行的候选不能当作真实反馈。</p><code class="reading-formula">a* = argmax_a [predicted reward(a) - uncertainty penalty(a)]（机制理解式）</code></li><li><b>按需更新世界模型</b><p>Policy 变强会改变候选分布，因此世界模型可靠性要按当前版本重新评价；证据或预算不足时不强行更新。</p><code class="reading-formula">update W iff unreliable(W) AND enough data AND enough budget（机制理解式）</code></li><li><b>策略—预测器联合保留</b><p>策略与世界模型各自通过评估还不够，还须验证搭配后的真实收益；确保下一轮继承的是有效组合。</p><code class="reading-formula">retain(Policy&#x27;, W&#x27;) iff pass(Policy&#x27;) AND pass(W&#x27;) AND pass(pair)（机制理解式）</code></li></ol>
      <h4>实验证据（作者报告，未复现）</h4><ul><li>CodeContests 200 道题、3 个种子，固定代码生成模型：静态验证器 26.3%，预测筛选 29.2%，再适配 World Model 31.2%；在线测试量相近。</li><li>MiniWoB++ checkbox 同一组 100 个实例：连续保留版本的任务成功数 51 → 79 → 99；平均动作数 5.30 → 3.21（下降 39.4%）。</li><li>LabHorizon F200 Level 2：五个策略版本的规划得分 21.80% → 46.01%；Suzuki 反应优化在相同 40 次实验预算下，平均最优产率 96.15%，BO 为 82.16%。</li></ul>
      <h4>限制与易错理解</h4><ul><li>“跨领域”指复用提出候选→预测→真实反馈→更新→保留的流程，不是一个共享权重的超级世界模型横跨所有任务。</li><li>五轮规划结果证明了连续策略改进，但不足以单独证明同一场景中 Policy 和 World Model 长期稳定的双向共同进化。</li><li>仅对被选中执行的候选获得真实反馈，预测器可能面对选择偏差与分布变化；预测误差降低也不自动意味着最终任务表现提升。</li></ul>
      <h4>对我们 RSI / I5 的启发</h4><ul><li>我们的 I5 十模型交换舞伴：把预测对象从“动作会带来什么后果”改为“向哪个伙伴学习，等预算训练后的独立能力提升是多少”。</li><li>可以借鉴“预测→少量真实教学验证→更新学习增益预测器→检查新伙伴策略是否真的更好”的递归闭环，而不是永远选择最强教师。</li><li>与我们的 Agent 多层更新研究相关：把修改 Prompt、Memory、Workflow 或模型参数的效果与预测器的判断分开审计，并保留独立测试。</li></ul>
      <div class="reading-next"><b>下一步最值得做的辨别实验</b><p>固定同一学生检查点，向强教师、能力相近教师、预测高增益教师和随机教师等预算学习；在未见测试集比较相对无教师的真实增益、负迁移率与成本，并观察多轮学习后最佳伙伴是否变化。</p></div>
    </div>
  </details>
  <div class="links reading-links"><a class="link-btn reading-deep-link" href="reading-notes.html#deep-rsi-anything-2610-13912">完整精读 · 公式与实验</a><a class="link-btn reading-related-link" href="reading-notes.html#deep-rsi-anything-2610-13912--stage-related">Related Work · 与前人的区别</a><a class="link-btn" href="#rsi-anything-2610-13912" aria-label="复制或保存此卡片的锚点链接">卡片定位</a><a class="link-btn" href="https://arxiv.org/html/2610.13912" target="_blank" rel="noopener noreferrer">论文 HTML</a><a class="link-btn" href="https://arxiv.org/pdf/2610.13912" target="_blank" rel="noopener noreferrer">PDF</a><a class="link-btn" href="https://github.com/Gen-Verse/RSI-Anything" target="_blank" rel="noopener noreferrer">GitHub 代码</a></div>
</article>
<article class="reading-card" id="r2orch-2610-22740" data-paper-tags="RSI|Self-Play|Curriculum|Skill Lifecycle" data-question-coverage="signal:core|novelty:partial|reach:core|retention:core|safety:not_addressed">
  <div class="reading-card-head">
    <div class="reading-metadata"><span class="reading-paper-id">R²Orch</span><span>arXiv:2610.22740</span><span>阅读 2026-10-27</span></div>
    <h3>R²Orch</h3>
    <p class="reading-full-title">R²Orch: Recursive Self-Improvement for Agent Orchestration via Self-Play within a Skill-Internalization Loop</p>
    <p class="reading-institution"><b>发表单位（作者署名）</b> 香港中文大学（深圳） <span>等 5 家署名机构</span></p>
    <div class="reading-tags"><span class="reading-tag">RSI</span><span class="reading-tag">Self-Play</span><span class="reading-tag">Curriculum</span><span class="reading-tag">Skill Lifecycle</span></div>
  </div>
  <p class="reading-one-sentence">先把辅助提示拿掉，再判断哪些题值得学、哪些提示可以撤掉。</p>
  <div class="reading-story" aria-label="Challenge Insight Design Result 四步读懂"><div class="reading-story-step" data-story-stage="challenge"><h4><span>Challenge</span>难在哪里</h4><p>Agent 带着 Skill 能做对题，却不一定真的学会；只看正确率，无法判断这道题是否还有学习价值。</p></div><div class="reading-story-step" data-story-stage="insight"><h4><span>Insight</span>为什么可解</h4><p>先撤掉提示再做一次，才能看出真实能力；同一道题随机给不给提示，才能判断 Skill 还有没有用。</p></div><div class="reading-story-step" data-story-stage="design"><h4><span>Design</span>具体怎么做</h4><p>每题做 5 次：3 次隐藏 Skill、2 次保留。用没有提示时的表现选训练题，再根据对照结果决定何时撤回 Skill。</p></div><div class="reading-story-step" data-story-stage="result"><h4><span>Result</span>结果怎么样</h4><p>AIME 2026：81.33%，对照方法为 74.00%；去掉其选题机制后为 70.67%。这是论文报告，尚未独立复现。</p></div></div>
  <div class="reading-issues"><p class="reading-issues-title">自我改进四问 + 安全：这篇研究到哪一步？</p><div class="reading-issue-tags"><span class="reading-issue reading-issue--core" title="评估分数和真实能力是否一致；评估器也在变化时，用什么独立证据校准它。">信号对不对<small>重点研究</small></span><span class="reading-issue reading-issue--partial" title="自己出题、自己造数据时，能够纠正模型的信息究竟从哪里来。">有没有新东西<small>部分涉及</small></span><span class="reading-issue reading-issue--core" title="高质量解法是否处在可采样的候选空间中，候选支持范围在哪一环节收窄。">采不采得到<small>重点研究</small></span><span class="reading-issue reading-issue--core" title="改进进入权重、记忆或技能后，旧能力是否保留、错误经验是否被排除。">吸收了会不会丢<small>重点研究</small></span><span class="reading-issue reading-issue--not_addressed" title="评估器被绕过、越权修改真实系统、坏行为被持久记录三类跨环节风险。">安全<small>未直接研究</small></span></div></div>
  <details class="reading-expand">
    <summary>继续看：真实证据、公式和没解决的问题</summary>
    <div class="reading-expanded-content">
      <div class="reading-source-line"><b>作者</b> Mingda Zhang et al. · <b>首发</b> 2026-10-15 · <b>版本</b> v2 · 2026-10-22 · <b>阅读范围</b> Method §4.2–4.3 + Appendix A.2/A.3/A.7 精读；尚未独立复现</div>
      <p class="reading-institutions-full"><b>全部作者单位：</b>香港中文大学（深圳） · 复旦大学 · 伊利诺伊大学厄巴纳-香槟分校 · 清华大学 · 新加坡国立大学<br><b>发表状态：</b>arXiv 预印本 · <b>核对位置：</b>arXiv v2 论文首页作者署名</p>
      <h4>更新的是哪一部分？</h4><p>真正通过 GRPO 更新的是 Director 和 Proposer 的 LoRA 参数；Skill 是外部提示文本，由 LLM Editor 修订、试用、撤回。随机隐藏只是训练时拿掉某一条 Skill 的上下文输入，并不撤销模型已经学到的参数；其余 Skill 可以仍然在场。</p>
      <h4>自我改进五问：论文做到哪里、还缺什么</h4>
      <p class="reading-taxonomy-caveat">“重点研究”表示直接针对该问题提出机制或证据，不代表问题已被彻底解决。分类属于本站的文献研读判断。</p>
      <dl class="reading-question-details"><div class="reading-question-detail"><dt><span>信号对不对</span><span class="reading-level reading-level--core">重点研究</span></dt><dd><p><b>论文做到：</b>在同一道题和同一当前策略下随机隐藏或保留 Skill，用成功率差和 Bayesian Bootstrap 后验检验 Skill 是否还有帮助（§4.3、附录 A.7）。</p><p><b>仍未解决：</b>仍依赖外部任务正确性验证器；没有研究验证器自身更新、被绕过时怎样保持校准。</p></dd></div><div class="reading-question-detail"><dt><span>有没有新东西</span><span class="reading-level reading-level--partial">部分涉及</span></dt><dd><p><b>论文做到：</b>Proposer 根据撤掉 Skill 后的可学习性动态选训练任务，让当前失败暴露出下一轮训练目标（§4.2）。</p><p><b>仍未解决：</b>主要从候选任务库中选题；没有解释封闭自生成数据能否持续引入真正的新信息。</p></dd></div><div class="reading-question-detail"><dt><span>采不采得到</span><span class="reading-level reading-level--core">重点研究</span></dt><dd><p><b>论文做到：</b>用无 Skill 成功率的正负结果方差选题，避免 GRPO 训练时出现全对或全错导致优势信号消失（§4.2）。</p><p><b>仍未解决：</b>改善训练时可学性，并没有证明原本完全采样不到的好解会进入模型的候选支持集。</p></dd></div><div class="reading-question-detail"><dt><span>吸收了会不会丢</span><span class="reading-level reading-level--core">重点研究</span></dt><dd><p><b>论文做到：</b>让外部 Skill 经自博弈逐步内化进 Director 参数；撤回 Skill 依据随机对照证据，并安排后续回测（§4.3）。</p><p><b>仍未解决：</b>主要检验撤走 Skill 后的任务表现，未完整检验跨长期任务的旧能力遗忘或错误 Skill 的记忆污染。</p></dd></div><div class="reading-question-detail"><dt><span>安全</span><span class="reading-level reading-level--not_addressed">未直接研究</span></dt><dd><p><b>论文做到：</b>框架聚焦课程选择、技能贡献测量与技能撤回，而非 Agent 安全威胁。</p><p><b>仍未解决：</b>没有针对评分器攻击、越权真实操作、恶意 Skill 持久化开展系统的安全验证。</p></dd></div></dl>
      <h4>核心机制 · 记住这几个公式</h4><ol class="reading-mechanisms"><li><b>Recursive Learnability</b><p>KL 约束的局部策略改进与二值结果方差相关。用撤掉候选 Skill 后的成功率 p⁻ 而非有 Skill 时的 p⁺ 选择任务。</p><code class="reading-formula">L_rec(x) = 4 p⁻(1 − p⁻)</code></li><li><b>随机隐藏对比</b><p>固定任务与当前策略，随机分配隐藏/保留 Skill；两组成功率之差估计该 Skill 的剩余贡献，避免把任务难度和 Skill 效果混在一起。</p><code class="reading-formula">zₓ = mean(y_visible) − mean(y_hidden)</code></li><li><b>后验撤回与回测</b><p>为每个 Skill 累积对照记录，用 Dirichlet 加权的 Bayesian Bootstrap 估计平均贡献；仅当预期正向贡献足够低才撤回，之后仍定期回测。</p><code class="reading-formula">withdraw iff nₖ ≥ 12 and E[max(Δₖ,0) | data] ≤ 0.02</code></li></ol>
      <h4>实验证据（作者报告，未复现）</h4><ul><li>论文在 12 个 IID/OOD 数据集报告多领域结果；AIME 2026：81.33%（PATS 74.00%），SWE-Bench：42.81%（PATS 40.16%）。</li><li>在 AIME 2026 的消融中，去掉 Recursive Learnability 后为 70.67%，换成固定 Skill 库后为 66.67%（完整方法 81.33%）。</li></ul>
      <h4>限制与易错理解</h4><ul><li>L_rec 衡量小 KL 更新下的局部结果方差，不等于未来真实学习增益；冻结 Worker 的随机性也会制造结果方差。</li><li>对照无偏性依赖固定任务/策略、随机分配和无干扰；记录在自适应选题与持续更新下会发生分布漂移。</li><li>无 Skill 部署指不提供外部 Skill 文本，仍可调用冻结 Workers 和 Agent Graph；Proposer 主要从候选题库选题。</li></ul>
      <h4>对我们 RSI / I5 的启发</h4><ul><li>对 I5 的十模型共进化：将“选下一道题”对应为“选下一位教学伙伴”，但不能直接用交互成功率替代学习后的独立能力提升。</li><li>可复用 3/2 随机对照 + 后验决策的思路；实际迁移时应从同一学习者检查点分叉，等预算训练后在独立测试集比较无教师增益。</li><li>把“辅助撤离”作为实验协议：验证 Skill/教师何时已不再贡献新收益，而不是只报告当前任务正确率。</li></ul>
      <div class="reading-next"><b>下一步最值得做的辨别实验</b><p>在同一学生检查点上，比较不同教师、随机教师和无教师的等预算学习；以撤掉教师后的 held-out ΔAcc 与负迁移率，检验 L_rec 是否优于直接学习增益。</p></div>
    </div>
  </details>
  <div class="links reading-links"><a class="link-btn" href="#r2orch-2610-22740" aria-label="复制或保存此卡片的锚点链接">卡片定位</a><a class="link-btn" href="https://arxiv.org/html/2610.22740v2" target="_blank" rel="noopener noreferrer">论文 HTML</a><a class="link-btn" href="https://arxiv.org/pdf/2610.22740" target="_blank" rel="noopener noreferrer">PDF</a><a class="link-btn" href="https://github.com/beita6969/R2Orch" target="_blank" rel="noopener noreferrer">GitHub 代码</a></div>
</article></div><p class="reading-empty" id="reading-empty" hidden>没有匹配的论文；可更换问题、涉及程度或清空搜索。</p><div class="links"><a class="link-btn" href="reading-cards.json" download>下载阅读卡片 JSON（可复用）</a></div>

## 论文精读卡片 / 五问标签怎么理解？

<p>四步读懂一篇论文之后，可以用这五个问题比较它研究到哪一步。<strong>重点研究</strong>指有直接方法和证据，不代表已经彻底解决。</p><div class="reading-guide-grid"><div class="reading-question-guide"><b>信号对不对</b><p>评估分数和真实能力是否一致；评估器也在变化时，用什么独立证据校准它。</p></div><div class="reading-question-guide"><b>有没有新东西</b><p>自己出题、自己造数据时，能够纠正模型的信息究竟从哪里来。</p></div><div class="reading-question-guide"><b>采不采得到</b><p>高质量解法是否处在可采样的候选空间中，候选支持范围在哪一环节收窄。</p></div><div class="reading-question-guide"><b>吸收了会不会丢</b><p>改进进入权重、记忆或技能后，旧能力是否保留、错误经验是否被排除。</p></div><div class="reading-question-guide"><b>安全</b><p>评估器被绕过、越权修改真实系统、坏行为被持久记录三类跨环节风险。</p></div></div><p class="reading-legend"><span class="reading-level reading-level--core">重点研究</span>直接研究这一问题；<span class="reading-level reading-level--partial">部分涉及</span>涉及其中一部分；<span class="reading-level reading-level--not_addressed">未直接研究</span>没有专门机制或实验。</p><details class="reading-maintenance"><summary>以后如何新增论文？</summary><p>维护说明在 <code>scripts/rsi_pages/README.md</code>，每篇只需追加结构化记录，网页和搜索由构建脚本自动生成。文献事实、阅读判断和待做实验分开记录。</p></details>

## 论文完整精读 / 精读 · RSI-Anything

<div class="deep-paper-head"><p class="deep-meta">PhAI Labs · PhAI Labs Technical Report · arXiv 预印本 · arXiv:2610.13912 · 2026-10-27 精读</p><h3>RSI-Anything: Unlocking Recursive Self-Improvement with World Models</h3><p class="deep-focus">它想解决一个简单问题：Agent 每次能想到好几个办法，但真正试错很贵。怎样挑着试，并保证下一轮比上一轮更好？</p><p class="deep-author-note">先读四个大标题下的一句话；要看例子、公式或实验细节时再展开。这份笔记区分作者结果、教学举例和我们的研究想法，尚未独立复现。</p><div class="deep-glossary"><p class="deep-glossary-title">先记住三个角色</p><dl class="deep-terms"><div><dt>Policy</dt><dd>负责想方案、做动作的 Agent</dd></div><div><dt>World Model</dt><dd>动手之前，先猜执行结果的预测器</dd></div><div><dt>Verifier</dt><dd>真正执行后，给出结果和判定标准的测试</dd></div></dl></div><nav class="deep-shortcuts" aria-label="RSI-Anything 四步精读"><a href="#deep-rsi-anything-2610-13912--stage-challenge">Challenge · 难在哪里</a><a href="#deep-rsi-anything-2610-13912--stage-insight">Insight · 为什么可解</a><a href="#deep-rsi-anything-2610-13912--stage-design">Design · 具体怎么做</a><a href="#deep-rsi-anything-2610-13912--stage-result">Result · 结果怎么样</a><a href="#deep-rsi-anything-2610-13912--stage-related">Related Work · 和前人到底哪里不同</a><a href="#deep-rsi-anything-2610-13912--stage-next">Next · 哪些问题还没解决</a></nav><section class="deep-stage" id="deep-rsi-anything-2610-13912--stage-challenge" data-story-stage="challenge"><header class="deep-stage-head"><span>01 · Challenge</span><h4>难在哪里</h4></header><p class="deep-stage-lead">Agent 能提出很多修复方案，但真实测试很贵；而且 Agent 变强后，旧预测器可能判断不准新方案。</p><div class="deep-stage-details"><details class="deep-chapter" id="deep-rsi-anything-2610-13912--problem"><summary>为什么一次任务做对了，还不算真正进步？<span class="deep-chapter-hint">展开细节</span></summary><div class="deep-chapter-body"><p class="deep-prose">在同一道题里反复修复，不等于系统能力持续提高。论文区分任务内的动作步 t 和系统更新周期 k：一次周期可以不接纳任何更新；只有被接纳的 Policy / Workflow 或 World Model 改变下一轮决策，才体现持久改进。</p><aside class="deep-note deep-note--example"><b>举个例子</b><p>今天修好了一个程序，不代表明天就会修同类错误。系统要在下一轮用上学到的东西，才算把这次经验留下来。</p></aside><aside class="deep-note deep-note--boundary"><b>证据边界</b><p>跨领域统一的是决策与反馈协议，不是七个领域共用一组通用世界模型权重（§2.1–2.2）。</p></aside></div></details></div></section><section class="deep-stage" id="deep-rsi-anything-2610-13912--stage-insight" data-story-stage="insight"><header class="deep-stage-head"><span>02 · Insight</span><h4>为什么可解</h4></header><p class="deep-stage-lead">先预测哪些方案值得试，可以少花测试成本。真实结果又能纠正预测器，但升级时必须看整套系统是否进步。</p><div class="deep-stage-details"><details class="deep-chapter" id="deep-rsi-anything-2610-13912--insight"><summary>为什么用预测先挑，再用真实结果纠错？<span class="deep-chapter-hint">展开细节</span></summary><div class="deep-chapter-body"><p class="deep-prose">关键不是让世界模型替代真实测试，而是把两者分工：预测负责省测试次数，真实结果负责检验预测准不准。Agent 变强后可能提出新方案，所以预测器也要根据新反馈调整。</p><div class="deep-table" tabindex="0" role="region" aria-label="精读内容比较表"><table><thead><tr><th scope="col">碰到的问题</th><th scope="col">容易掉进的坑</th><th scope="col">作者的办法</th></tr></thead><tbody><tr><td>测试费用高</td><td>四个候选全部跑完，预算很快用光</td><td>先预测，挑值得试的方案去真实执行</td></tr><tr><td>预测器会看走眼</td><td>把模型猜测当成事实，后面越学越偏</td><td>只用真实执行的结果检查预测是否可靠</td></tr><tr><td>模块之间不一定合拍</td><td>Agent 和预测器单独更好，搭配却可能更差</td><td>升级之前重新测试新组合</td></tr></tbody></table></div><aside class="deep-note deep-note--insight"><b>一句话理解</b><p>预测是为了少走弯路，真实反馈是为了知道有没有走对；系统是否进步，要看最后整套搭配。</p></aside></div></details></div></section><section class="deep-stage" id="deep-rsi-anything-2610-13912--stage-design" data-story-stage="design"><header class="deep-stage-head"><span>03 · Design</span><h4>具体怎么做</h4></header><p class="deep-stage-lead">Agent 提方案 → 世界模型预测 → 选择少数方案真实测试 → 按需更新 → 检查新旧组件组合，决定是否保留。</p><div class="deep-stage-details"><details class="deep-chapter" id="deep-rsi-anything-2610-13912--example"><summary>先看一个例子：四个补丁该测试哪一个？<span class="deep-chapter-hint">展开细节</span></summary><div class="deep-chapter-body"><aside class="deep-note deep-note--example"><b>示例数字，并非论文运行记录</b><p>固定代码生成器生成四种补丁，假设不确定性惩罚系数为 0.5。该例只是为了说明候选排序；论文真实实验是五类执行结果预测。</p></aside><div class="deep-table" tabindex="0" role="region" aria-label="精读内容比较表"><table><thead><tr><th scope="col">补丁</th><th scope="col">预测效用</th><th scope="col">不确定性</th><th scope="col">示例最终分数</th></tr></thead><tbody><tr><td>A 修改边界</td><td>0.35</td><td>0.10</td><td>0.300</td></tr><tr><td>B 改索引更新</td><td>0.75</td><td>0.40</td><td>0.550</td></tr><tr><td>C 补充终止条件</td><td>0.60</td><td>0.05</td><td>0.575（选择）</td></tr><tr><td>D 重写循环</td><td>0.48</td><td>0.20</td><td>0.380</td></tr></tbody></table></div><ol class="deep-steps"><li><strong>选择 C 并实际运行</strong><p>假设失败。只有 C 得到了真实结果，A/B/D 的预测不能当作已验证事实。</p></li><li><strong>判断是否需要更新 WM</strong><p>“预测成功率 60%、实际失败一次”并不足以证明 WM 失准；要积累同版本预测—观测记录。</p></li><li><strong>更新后仍须完整配对检查</strong><p>新 Policy、新 WM 单独更好时，最终系统也可能更差；不通过则继续使用旧组合。</p></li></ol></div></details><details class="deep-chapter" id="deep-rsi-anything-2610-13912--selection"><summary>怎么挑选值得真实测试的方案？（公式 7–8）<span class="deep-chapter-hint">展开细节</span></summary><div class="deep-chapter-body"><div class="deep-formula"><b>Eq. (7) · 预测效用与可选不确定性惩罚</b><code>R_d(τ̂) = Σ_j w_(d,j) · r_(τ,j) − Δ_d(τ̂)</code><p><strong>怎么理解：</strong>先按有效性与操作约束排除非法候选，再按预测收益排序；只有任务设置开启不确定性惩罚时 Δ 才非零。</p><p class="deep-caveat"><strong>边界：</strong>代码实验实际聚合五类执行结果概率，选四个补丁中的一个执行；不是简单地直接套用预测成功率。</p></div><div class="deep-table" tabindex="0" role="region" aria-label="精读内容比较表"><table><thead><tr><th scope="col">证据层级</th><th scope="col">是什么</th><th scope="col">解释边界</th></tr></thead><tbody><tr><td>E0</td><td>确定性规则检查</td><td>只覆盖明确规则</td></tr><tr><td>E1</td><td>学习模型预测 / 想象轨迹</td><td>不是实际执行真值</td></tr><tr><td>E2</td><td>专用模拟器或高保真计算</td><td>受模拟范围约束</td></tr><tr><td>E3</td><td>外部测试或真实实验</td><td>只覆盖真正被测试的候选</td></tr></tbody></table></div><div class="deep-formula"><b>Eq. (8) · 想象轨迹准入</b><code>e_τ = 1[v_τ=1] · 1[R_d(τ̂)≥r_min] · C_U(τ) · 1[ℓ_τ∈E_train]</code><p><strong>怎么理解：</strong>通过合法性、预测效用、不确定性检查和证据来源限制的模拟轨迹，才可能进入训练。</p><p class="deep-caveat"><strong>边界：</strong>选择去执行谁与选择让哪些想象轨迹参与训练是两件事；未开启模拟学习时 D_sim 为空。</p></div><aside class="deep-note deep-note--insight"><b>选择偏差</b><p>World Model 决定谁得到真实反馈；而这些反馈又用于训练下一版模型。被低估的好候选可能始终没有机会获得真实证据。</p></aside></div></details><details class="deep-chapter" id="deep-rsi-anything-2610-13912--reliability"><summary>预测错了，要不要马上重新训练？（公式 10–12）<span class="deep-chapter-hint">展开细节</span></summary><div class="deep-chapter-body"><div class="deep-formula"><b>Eq. (10) · 三种可靠性状态</b><code>ρᵂ_k ∈ {reliable, unreliable, insufficient}</code><p><strong>怎么理解：</strong>从当前版本的预测与真实观测检查误差、校准和覆盖；证据不足不等于预测可靠。</p><p class="deep-caveat"><strong>边界：</strong>不能把旧版预测记录直接混入新版错误率；必要时用新版重算历史输入。</p></div><div class="deep-formula"><b>Eq. (11) · 适配触发</b><code>uᵂ_k = 1[ρᵂ_k=unreliable] · 1[D_adapt 足够] · 1[B_update≥c_adapt]</code><p><strong>怎么理解：</strong>同时确认失准、有足够修正数据、有足够预算，才尝试适配。</p><p class="deep-caveat"><strong>边界：</strong>长期没被选择执行的候选缺少反馈，既不能宣称模型准确，也未必能触发适配。</p></div><div class="deep-formula"><b>Eq. (12) · 提出新预测器</b><code>φ′_(k+1) = Adapt(φ_k, D_adapt) if uᵂ_k=1; else φ_k</code><p><strong>怎么理解：</strong>提出一个新版本不等于已保留；更新候选仍要经过后续的组件和配对接纳检查。</p><p class="deep-caveat"><strong>边界：</strong>Policy 和 WM 可以异步更新，但外部反馈消耗与训练/评估计算开销不是同一个成本口径。</p></div></div></details><details class="deep-chapter" id="deep-rsi-anything-2610-13912--pair"><summary>为什么两个模块各自变好，组合后反而更差？（公式 13–18）<span class="deep-chapter-hint">展开细节</span></summary><div class="deep-chapter-body"><div class="deep-formula"><b>Eqs. (13)–(16) · 组件检查</b><code>Gπ = Qπ(θ′; θ, D_gateπ) ； GW = QW(φ′; φ, D_gateW)</code><p><strong>怎么理解：</strong>分别检查新 Policy 和新 WM；若某组件未通过，仍使用它的旧版本与其他已通过组件组装。</p><p class="deep-caveat"><strong>边界：</strong>新 WM 平均更准确，不代表它对新 Policy 产生的候选也更准确。</p></div><div class="deep-formula"><b>Eqs. (17)–(18) · 配对检查与保留</b><code>Gpair = Qpair((θ̄, φ̄); (θ, φ), D_compat); Gpair=0 则保留原配对</code><p><strong>怎么理解：</strong>组合决策行为需要在预先设定、可比的任务与约束下检查；配对失败时整体回退。</p><p class="deep-caveat"><strong>边界：</strong>已有的是通用协议定义，不能直接视为充分的 Pair Gate 消融证据。</p></div><div class="deep-table" tabindex="0" role="region" aria-label="精读内容比较表"><table><thead><tr><th scope="col">教学示例（非论文数字）</th><th scope="col">独立指标 / 配对成功率</th><th scope="col">解释</th></tr></thead><tbody><tr><td>旧 P₀+旧 W₀</td><td>任务成功率 68%</td><td>基线</td></tr><tr><td>新 P₁+旧 W₀</td><td>任务成功率 74%</td><td>新 Policy 有改善</td></tr><tr><td>单独检查新 W₁</td><td>Brier 0.40→0.32</td><td>新预测器有改善</td></tr><tr><td>新 P₁+新 W₁</td><td>任务成功率 64%</td><td>组合变差，拒绝升级</td></tr></tbody></table></div><aside class="deep-note deep-note--insight"><b>最重要的机制洞察</b><p>新 Policy 改变候选分布，新 World Model 改变被选中接受反馈的候选。版本接纳必须从单组件得分推进到组装后真实决策行为。</p></aside></div></details></div></section><section class="deep-stage" id="deep-rsi-anything-2610-13912--stage-result" data-story-stage="result"><header class="deep-stage-head"><span>04 · Result</span><h4>结果怎么样</h4></header><p class="deep-stage-lead">代码修复：固定生成器时，成功率由 26.3% 升至 31.2%。五轮规划得分由 21.80% 升至 46.01%，但并非同一实验中证明长期联合进化。</p><div class="deep-stage-details"><details class="deep-chapter" id="deep-rsi-anything-2610-13912--results"><summary>真正变好的是什么？五组实验分别说明什么？<span class="deep-chapter-hint">展开细节</span></summary><div class="deep-chapter-body"><div class="deep-evidence-grid"><article class="deep-evidence"><h4>代码修复 · 预测选择与适配的受控比较</h4><p><b>评测设置：</b>ReasonFlux-Coder-7B 固定；CodeContests 200 题×3 种子；每轮四候选选一执行，最多三轮。</p><p><b>作者报告：</b>随机 26.0%；静态验证器 26.3%；固定 WM 29.2%；适配 WM 31.2%。平均在线测试调用 3.71–3.72 次/题。静态→固定 WM 排序准确率 66.5%→72.8%，Brier 0.488→0.358。</p><p><b>能够支持：</b>预测器更会选、适配后还能进一步提升修复成功率。</p><p class="deep-caveat"><b>尚不能推断：</b>Coder 自身变强；总训练和门控计算费用完全相同。</p></article><article class="deep-evidence"><h4>GUI · 任务表现与动作效率</h4><p><b>评测设置：</b>MiniWoB++ checkbox 同一批 100 个实例；同时报告 OSWorld。</p><p><b>作者报告：</b>成功率 51%→79%→99%；平均动作 5.30→3.21；OSWorld 相对初始 Agent 提升 18.4%。</p><p><b>能够支持：</b>Policy 与 WM 的不同保留版本改善部分 GUI 任务结果。</p><p class="deep-caveat"><b>尚不能推断：</b>单独由 Pair Gate 导致全部提升，或在所有网页任务可复制。</p></article><article class="deep-evidence"><h4>实验室规划 · 连续 Policy 改善</h4><p><b>评测设置：</b>LabHorizon F200 Level-2，200 个任务，单个 4B Policy 的五个版本。</p><p><b>作者报告：</b>规划得分 21.80%→38.03%→41.99%→44.56%→46.01%。</p><p><b>能够支持：</b>连续 Policy 更新能提高所测规划指标。</p><p class="deep-caveat"><b>尚不能推断：</b>在相同任务里也完成多轮 WM 联合优化的独立证明。</p></article><article class="deep-evidence"><h4>化学实验 · 实测产率与预算</h4><p><b>评测设置：</b>Suzuki–Miyaura 的流动 LC–MS 筛选；BO 对照相同 40 次实验。</p><p><b>作者报告：</b>平均最佳观测产率 96.15%，Bayesian Optimization 为 82.16%。</p><p><b>能够支持：</b>在所报告的化学条件空间与预算内搜索更有效。</p><p class="deep-caveat"><b>尚不能推断：</b>任意反应或无限预算均占优。</p></article><article class="deep-evidence"><h4>免疫科学 · 研究假设生成</h4><p><b>评测设置：</b>工作流改进 + 状态预测 + 自我纠正的应用示范。</p><p><b>作者报告：</b>形成拟开展实验验证的干预假设。</p><p><b>能够支持：</b>完整研究系统可以串联多个领域能力。</p><p class="deep-caveat"><b>尚不能推断：</b>治疗有效性或湿实验已经得到证实。</p></article></div></div></details></div></section><section class="deep-stage" id="deep-rsi-anything-2610-13912--stage-related" data-story-stage="related"><header class="deep-stage-head"><span>05 · Related Work</span><h4>和前人到底哪里不同</h4></header><p class="deep-stage-lead">过去的工作分别改代码、训练奖励、管理记忆、规划动作；RSI-Anything 把可更新的预测器接到真实反馈选择和系统版本接纳中。</p><div class="deep-stage-details"><div class="deep-related"><p class="deep-related-takeaway">区别主要是更新对象和反馈用途，而不是第一次联合更新模型或第一次保留通过测试的版本。</p><h5>这条研究路线怎么发展？</h5><ol class="deep-related-evolution"><li><b>2023 · 技能积累</b><span>Voyager 把任务经验存成可复用的技能代码，强调长期保留与调用。</span><a href="https://arxiv.org/abs/2305.16291" target="_blank" rel="noopener noreferrer">原论文</a></li><li><b>2025 · 自改写与反馈学习</b><span>Darwin Gödel Machine 改 Agent 代码；CURE 让 Coder 与 Tester 从执行反馈中共同训练。</span></li><li><b>2026 · 更多组件一起改变</b><span>RLAnything 联合训练策略、奖励和环境；ScienceBuddy 让 Harness 与模型双环改进，Recuris 管理长程记忆。</span></li><li><b>2026 · 世界预测进入改进回路</b><span>JEPA-Anything 学习跨领域预测；RSI-Anything 用预测选反馈、用反馈修正预测器，并检查 Policy–WM 配对。</span></li></ol><h5>最相近的 7 篇 · 实际研究边界</h5><p class="deep-related-instructions">先扫四列表，再展开具体论文。这里比较的是研究问题、更新对象和实际验证条件，不是给本文设计“全部胜出”的勾选表。</p><div class="deep-related-matrix" role="region" aria-label="相关工作可横向滚动的比较表" tabindex="0"><table><thead><tr><th scope="col">工作 / 年份</th><th scope="col">原工作解决什么</th><th scope="col">更新什么、靠什么反馈</th><th scope="col">与本文区别</th></tr></thead><tbody><tr><td><a href="#related-rsi-anything-2610-13912--cure">CURE</a><small>2025 · NeurIPS 2025</small></td><td>让代码生成器和单元测试器从彼此错误中学习。</td><td><b>Coder 与 Unit Tester 权重</b><small>执行与测试反馈，无需标准代码作监督</small></td><td>RSI-Anything 代码修复实验固定由 CURE 获得的 ReasonFlux-Coder，只更新候选结果预测器，并用它决定运行哪个补丁。</td></tr><tr><td><a href="#related-rsi-anything-2610-13912--rlanything">RLAnything</a><small>2026 · ICML 2026 (PMLR 306)</small></td><td>训练时如何让 Policy、奖励模型和环境共同改进，产生更有用的强化学习信号？</td><td><b>Policy、Reward Model、训练环境</b><small>逐步/最终奖励、模型间一致性和 critic 反馈</small></td><td>RLAnything 重点是训练信号与环境共同优化；RSI-Anything 重点是用可更新的预测 World Model 挑选真实测试候选，并检验 Policy–预测器的版本配对。</td></tr><tr><td><a href="#related-rsi-anything-2610-13912--jepa">JEPA-Anything</a><small>2026 · PhAI Labs Technical Report · arXiv</small></td><td>视觉、分子、物理、生命等不同领域能否使用同一种状态预测原则？</td><td><b>训练潜在状态预测器与因子化表征（OPF）</b><small>各领域状态、干预与后继目标</small></td><td>JEPA 研究如何学会预测；RSI 用预测决定去哪采集反馈，并让 Policy/Workflow 和预测器在接纳检查后进入下一轮。</td></tr><tr><td><a href="#related-rsi-anything-2610-13912--dreamer">DreamerV3</a><small>2025 · Nature 640 (2025)</small></td><td>不用人工为每个任务重新设计 RL 方法，也能在想象未来的过程中学习控制策略吗？</td><td><b>World Model、Actor、Critic 权重</b><small>环境交互 + 想象轨迹</small></td><td>Dreamer 已经将 World Model 与 Actor 联合训练；RSI-Anything 关注候选外部验证预算、预测可靠性变化、异步更新和配对的版本保留。</td></tr><tr><td><a href="#related-rsi-anything-2610-13912--dgm">Darwin Gödel Machine</a><small>2026 · ICLR 2026（预印本 2025）</small></td><td>Agent 能否修改自己的代码，并积累能进一步改进自己的版本？</td><td><b>Agent 的实现代码与工作流，保留版本档案</b><small>编程基准上的执行评测</small></td><td>DGM 通过开放式搜索代码改写和版本档案探索 Agent；RSI 对 Policy/WM 配对的预测可靠性和反馈选择建模。</td></tr><tr><td><a href="#related-rsi-anything-2610-13912--sciencebuddy">ScienceBuddy</a><small>2026 · PhAI Labs Technical Report · arXiv</small></td><td>研究人员的任务、反馈和执行记录，怎样持续改进科研 Agent？</td><td><b>内循环优化 Harness，外循环对模型执行 RL</b><small>真实科研交互、执行记录与评测 rubrics</small></td><td>ScienceBuddy 聚焦 Harness–Model 双环演化；RSI 额外把预测后果的 World Model 放进反馈选择与组件配对。</td></tr><tr><td><a href="#related-rsi-anything-2610-13912--recuris">Recuris</a><small>2026 · 2026 arXiv 预印本</small></td><td>很长的任务中，记忆历史越多，Agent 越容易找错技能和忘记当前进度。</td><td><b>工作记忆、技能记忆；固定元代理管理局部更新</b><small>长任务执行记录和验证门控</small></td><td>Recuris 修的是记忆和 Skill 调用；RSI 更关注行动后果预测器及 Policy–WM 搭配。</td></tr></tbody></table></div><details id="related-rsi-anything-2610-13912--cure" class="deep-related-paper"><summary><span>CURE · 反馈学习</span><small>展开核查与区别</small></summary><div class="deep-related-paper-body"><p class="deep-related-venue"><b>Co-Evolving LLM Coder and Unit Tester via Reinforcement Learning</b> · NeurIPS 2025</p><p><b>RSI-Anything 怎么引用它：</b>§4.1、§4.2；共享代码反馈；是 RSI 代码实验的生成器来源</p><p><b>相同点：</b>都利用代码执行结果判断候选与提供学习反馈。</p><p><b>真正不同：</b>RSI-Anything 代码修复实验固定由 CURE 获得的 ReasonFlux-Coder，只更新候选结果预测器，并用它决定运行哪个补丁。</p><p><b>为什么这个区别重要：</b>生成器能力提升与筛选器能力提升是两件事。</p><p><b>论文实际有的证据：</b>RSI 论文固定 Coder：静态验证器 26.3% → 固定 WM 29.2% → 适配 WM 31.2%；并非重训 CURE 的同预算对照。</p><p><b>还需要什么决定性对照：</b>同一个固定 Coder、相同候选与在线测试预算，分别比较普通验证器、固定预测器、可适配预测器；若还声称胜过训练 Coder，需额外控制训练成本。</p><p class="deep-related-source"><a target="_blank" rel="noopener noreferrer" href="https://proceedings.neurips.cc/paper_files/paper/2025/hash/d38653cdaa8e992549e1e9e1621610d7-Abstract-Conference.html">核对原论文 / 官方项目</a> · NeurIPS 官方摘要；RSI §3.1、§4.1–4.2 · 官方会议页已核对；跨论文方法差异已核对</p></div></details><details id="related-rsi-anything-2610-13912--rlanything" class="deep-related-paper"><summary><span>RLAnything · 反馈学习</span><small>展开核查与区别</small></summary><div class="deep-related-paper-body"><p class="deep-related-venue"><b>RLAnything: Forge Environment, Policy, and Reward Model in Completely Dynamic RL System</b> · ICML 2026 (PMLR 306)</p><p><b>RSI-Anything 怎么引用它：</b>§4.1、§4.2；§3.2 对比；原文中的邻近方法，也是 GUI 结果的对照</p><p><b>相同点：</b>都不是只更新一个模块，而是把反馈用于多个相互影响的组件。</p><p><b>真正不同：</b>RLAnything 重点是训练信号与环境共同优化；RSI-Anything 重点是用可更新的预测 World Model 挑选真实测试候选，并检验 Policy–预测器的版本配对。</p><p><b>为什么这个区别重要：</b>训练奖励质量与执行后果预测不是同一预测目标；不能宣称 RSI 首次提出共同优化。</p><p><b>论文实际有的证据：</b>RSI 论文在 OSWorld 报告相对 RLAnything 的 +5.5% 相对增益；未提供完全同设置的长期 Pair Gate 因果消融。</p><p><b>还需要什么决定性对照：</b>在相同 Policy、训练/真实交互预算及环境上，对照 RLAnything 的联合奖励更新与 RSI 的预测选择、预测适配及配对门控。</p><p class="deep-related-source"><a target="_blank" rel="noopener noreferrer" href="https://proceedings.mlr.press/v306/wang26jf.html">核对原论文 / 官方项目</a> · ICML 官方 PMLR 摘要；RSI §3.2、§4.1–4.2 · ICML 官方 proceedings 已核对；相对百分比口径按 RSI 原文</p></div></details><details id="related-rsi-anything-2610-13912--jepa" class="deep-related-paper"><summary><span>JEPA-Anything · 预测模型</span><small>展开核查与区别</small></summary><div class="deep-related-paper-body"><p class="deep-related-venue"><b>JEPA-Anything: Learning Predictive Models across Different Worlds</b> · PhAI Labs Technical Report · arXiv</p><p><b>RSI-Anything 怎么引用它：</b>§4.3；Introduction、§2.2；直接继承的模型基础，不是独立同任务竞争 baseline</p><p><b>相同点：</b>RSI 直接继承其预测架构和领域适配思想。</p><p><b>真正不同：</b>JEPA 研究如何学会预测；RSI 用预测决定去哪采集反馈，并让 Policy/Workflow 和预测器在接纳检查后进入下一轮。</p><p><b>为什么这个区别重要：</b>能准确预测下一步不等于能够持续自我改进。</p><p><b>论文实际有的证据：</b>JEPA 支撑跨领域预测方法；RSI 代码/GUI/规划实验分别支持后续决策与更新，但没有证明所有领域共用同一权重。</p><p><b>还需要什么决定性对照：</b>固定同一个 JEPA 预测器，比较仅预测/规划与加入真实反馈、按需适配和版本接纳后的下一轮独立能力。</p><p class="deep-related-source"><a target="_blank" rel="noopener noreferrer" href="https://arxiv.org/abs/2609.20800">核对原论文 / 官方项目</a> · 官方 arXiv 摘要；RSI §2.2、§4.3 · arXiv 原文摘要已核对；技术继承由 RSI §2.2 支持</p></div></details><details id="related-rsi-anything-2610-13912--dreamer" class="deep-related-paper"><summary><span>DreamerV3 · 预测模型</span><small>展开核查与区别</small></summary><div class="deep-related-paper-body"><p class="deep-related-venue"><b>Mastering Diverse Control Tasks through World Models</b> · Nature 640 (2025)</p><p><b>RSI-Anything 怎么引用它：</b>§4.3；最重要的 World Model + Actor 机制先例</p><p><b>相同点：</b>模型预测行动后果，预测又影响接下来采取哪些行动。</p><p><b>真正不同：</b>Dreamer 已经将 World Model 与 Actor 联合训练；RSI-Anything 关注候选外部验证预算、预测可靠性变化、异步更新和配对的版本保留。</p><p><b>为什么这个区别重要：</b>“World Model 与 Policy 一起变强”不是 RSI 首次提出；需要定位在接纳协议和反馈分配。</p><p><b>论文实际有的证据：</b>两篇来自不同任务体系，并无 Dreamer vs RSI 的严格同环境同预算实验；不能用跨领域展示直接比较性能。</p><p><b>还需要什么决定性对照：</b>在统一环境和预算中控制两者的更新频率，检验显式版本可靠性/Pair Gate 是否能带来独立增益。</p><p class="deep-related-source"><a target="_blank" rel="noopener noreferrer" href="https://www.nature.com/articles/s41586-025-08744-2">核对原论文 / 官方项目</a> · Nature 官方全文/摘要；RSI §4.3 · Nature 正式论文内容已核对；无直接同预算跨论文比较</p></div></details><details id="related-rsi-anything-2610-13912--dgm" class="deep-related-paper"><summary><span>Darwin Gödel Machine · Agent 自改写</span><small>展开核查与区别</small></summary><div class="deep-related-paper-body"><p class="deep-related-venue"><b>Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents</b> · ICLR 2026（预印本 2025）</p><p><b>RSI-Anything 怎么引用它：</b>§4.1；最近邻：版本改写与经验验证</p><p><b>相同点：</b>都强调改完后必须真实测评，且有效更新要影响下一轮。</p><p><b>真正不同：</b>DGM 通过开放式搜索代码改写和版本档案探索 Agent；RSI 对 Policy/WM 配对的预测可靠性和反馈选择建模。</p><p><b>为什么这个区别重要：</b>原工作已有更新后测试和保留，RSI 不应据此声称首次采用版本接纳。</p><p><b>论文实际有的证据：</b>DGM 报告自改写 Agent 的性能演进；RSI 报告预测选择与适配效果；未做严格跨方法同环境实验。</p><p><b>还需要什么决定性对照：</b>在同一个 Agent 自改写任务上固定候选版本库、验证预算，比较带/不带预测筛选和 Pair Gate 的累计收益。</p><p class="deep-related-source"><a target="_blank" rel="noopener noreferrer" href="https://arxiv.org/abs/2505.22954">核对原论文 / 官方项目</a> · ICLR 2026 论文（OpenReview pUpzQZTvGY）；Sakana AI 官方项目；RSI §4.1 · ICLR 2026 正式发表状态、论文机制与作者网站已核对</p></div></details><details id="related-rsi-anything-2610-13912--sciencebuddy" class="deep-related-paper"><summary><span>ScienceBuddy · Agent 自改写</span><small>展开核查与区别</small></summary><div class="deep-related-paper-body"><p class="deep-related-venue"><b>ScienceBuddy: Recursive-in-Recursive Self-Improvement for Interactive Scientific Agents</b> · PhAI Labs Technical Report · arXiv</p><p><b>RSI-Anything 怎么引用它：</b>§4.1、§4.4；同机构邻近 RSI 系统，更新对象有所不同</p><p><b>相同点：</b>都让真实使用经验进入下一轮更新，并允许不同组件在不同轮次改进。</p><p><b>真正不同：</b>ScienceBuddy 聚焦 Harness–Model 双环演化；RSI 额外把预测后果的 World Model 放进反馈选择与组件配对。</p><p><b>为什么这个区别重要：</b>两者都不是一次性 Self-Refine，需分清更新的组件角色。</p><p><b>论文实际有的证据：</b>各自展示不同任务/子系统提升；论文没有统一科学任务上的同成本分解对照。</p><p><b>还需要什么决定性对照：</b>固定科学任务与反馈预算，比 Harness/RL 更新、WM 预测筛选及两者合用的多轮净收益。</p><p class="deep-related-source"><a target="_blank" rel="noopener noreferrer" href="https://arxiv.org/abs/2609.17523">核对原论文 / 官方项目</a> · arXiv 摘要 + 作者代码说明；RSI §4.1、§4.4 · 官方 arXiv 摘要已核对</p></div></details><details id="related-rsi-anything-2610-13912--recuris" class="deep-related-paper"><summary><span>Recuris · Agent 自改写</span><small>展开核查与区别</small></summary><div class="deep-related-paper-body"><p class="deep-related-venue"><b>Recursive Experiential-Working Memory Evolution for Long-Horizon Agent Harnesses</b> · 2026 arXiv 预印本</p><p><b>RSI-Anything 怎么引用它：</b>§4.1；记忆更新与验证的直接邻近</p><p><b>相同点：</b>两者都验证更新是否值得保留，并让上一轮经验影响下一轮。</p><p><b>真正不同：</b>Recuris 修的是记忆和 Skill 调用；RSI 更关注行动后果预测器及 Policy–WM 搭配。</p><p><b>为什么这个区别重要：</b>存在外置记忆版本门控先例，RSI 的门控贡献应聚焦配对决策，而非泛称首次验证更新。</p><p><b>论文实际有的证据：</b>Recuris 关注长程记忆增益，RSI 关注选择/模型适配；没有同一任务的直接配对消融。</p><p><b>还需要什么决定性对照：</b>在固定长程任务上比较独立记忆门控和 Policy–WM 配对检查的额外收益、遗忘及成本。</p><p class="deep-related-source"><a target="_blank" rel="noopener noreferrer" href="https://arxiv.org/abs/2608.24876">核对原论文 / 官方项目</a> · 官方 arXiv 摘要；RSI §4.1 · 官方 arXiv 摘要已核对</p></div></details><details class="deep-related-context"><summary>其他相关工作 · 2 篇（课程 / 科研 Agent）</summary><div class="deep-related-matrix" role="region" aria-label="相关工作可横向滚动的比较表" tabindex="0"><table><thead><tr><th scope="col">工作 / 年份</th><th scope="col">原工作解决什么</th><th scope="col">更新什么、靠什么反馈</th><th scope="col">与本文区别</th></tr></thead><tbody><tr><td><a href="#related-rsi-anything-2610-13912--agent0">Agent0</a><small>2026 · COLM 2026（预印本 2025）</small></td><td>没有人工标注的数据时，Agent 能否自己出任务、自己进步？</td><td><b>Curriculum Agent 与 Executor Agent</b><small>自生成任务、求解不确定性、工具使用及投票伪标签</small></td><td>Agent0 主要在构建前沿课程与可用训练数据；RSI 主要决定已有候选中哪个值得消耗真实环境反馈。</td></tr><tr><td><a href="#related-rsi-anything-2610-13912--aide2">AIDE²</a><small>2026 · 2026 arXiv 预印本</small></td><td>AI 研究 Agent 能否改写自身代码，让以后研究任务完成得更好？</td><td><b>AI Research Agent 的代码、搜索策略与上下文记忆结构</b><small>AI 研发基准的隐藏评测</small></td><td>AIDE² 优化科研 Agent 的实现与研究效率；RSI-Anything 优化预测后果的 WM 与策略之间的反馈和配对。</td></tr></tbody></table></div><details id="related-rsi-anything-2610-13912--agent0" class="deep-related-paper"><summary><span>Agent0 · 课程与数据</span><small>展开核查与区别</small></summary><div class="deep-related-paper-body"><p class="deep-related-venue"><b>Agent0: Unleashing Self-Evolving Agents from Zero Data via Tool-Integrated Reasoning</b> · COLM 2026（预印本 2025）</p><p><b>RSI-Anything 怎么引用它：</b>§4.1；相邻问题：新数据从何而来</p><p><b>相同点：</b>都研究哪些经历值得进入下一轮学习。</p><p><b>真正不同：</b>Agent0 主要在构建前沿课程与可用训练数据；RSI 主要决定已有候选中哪个值得消耗真实环境反馈。</p><p><b>为什么这个区别重要：</b>训练任务来自哪里，与外部反馈怎样分配，是两种不同的学习瓶颈。</p><p><b>论文实际有的证据：</b>原论文分别在推理和跨领域反馈任务中评测，不存在同任务对照。</p><p><b>还需要什么决定性对照：</b>统一候选生成与校准资源后，对照课程生成和 WM 选择哪部分带来未来 held-out 增益。</p><p class="deep-related-source"><a target="_blank" rel="noopener noreferrer" href="https://aiming-lab.github.io/Agent0/">核对原论文 / 官方项目</a> · 作者论文列表显示 COLM 2026，官方 Agent0 项目机制说明；RSI §4.1 · 作者项目与作者论文列表已核对</p></div></details><details id="related-rsi-anything-2610-13912--aide2" class="deep-related-paper"><summary><span>AIDE² · Agent 自改写</span><small>展开核查与区别</small></summary><div class="deep-related-paper-body"><p class="deep-related-venue"><b>Recursive Self-Improvement of AI Research Agents</b> · 2026 arXiv 预印本</p><p><b>RSI-Anything 怎么引用它：</b>§4.1；相邻领域：自主研究 Agent 自修改</p><p><b>相同点：</b>把经过测试的 Agent 版本持久保留，并反馈给下一轮搜索。</p><p><b>真正不同：</b>AIDE² 优化科研 Agent 的实现与研究效率；RSI-Anything 优化预测后果的 WM 与策略之间的反馈和配对。</p><p><b>为什么这个区别重要：</b>两者都依赖隐藏评测，但更新对象和关键机制不同。</p><p><b>论文实际有的证据：</b>AIDE² 报告 7 次连续改善及跨任务保留集效果；RSI 无相同 R&amp;D 基准的直接比较。</p><p><b>还需要什么决定性对照：</b>固定 AI 研发任务、版本候选与隐藏评测，对照预测筛选是否提升单位反馈预算的改进收益。</p><p class="deep-related-source"><a target="_blank" rel="noopener noreferrer" href="https://arxiv.org/abs/2609.26457">核对原论文 / 官方项目</a> · arXiv 摘要；RSI §4.1 · 官方 arXiv 摘要已核对</p></div></details></details><p class="deep-related-boundary"><b>读表结论：</b>过去的工作分别改代码、训练奖励、管理记忆、规划动作；RSI-Anything 把可更新的预测器接到真实反馈选择和系统版本接纳中。</p><p class="deep-related-boundary"><b>目前无法下的结论：</b>缺少在同一任务、同一完整预算下长期联合更新 Policy + World Model、并隔离验证 Pair Check 独立贡献的实验。</p><p class="deep-related-provenance">核验日期：2026-10-27 · 根据 RSI-Anything §4.1 自我改进；§4.2 验证与策略学习；§4.3 预测世界模型；§4.4 科学 Agent 所列文献定位，逐篇对照原论文或作者项目。“同任务直接对照”和“领域相邻”两种证据不能互相替代。</p></div></div></section><section class="deep-stage" id="deep-rsi-anything-2610-13912--stage-next" data-story-stage="next"><header class="deep-stage-head"><span>06 · Next</span><h4>哪些问题还没解决</h4></header><p class="deep-stage-lead">这些是尚未解决的科学问题，不应当写成原论文已经证明的结论。</p><div class="deep-stage-details"><details class="deep-chapter" id="deep-rsi-anything-2610-13912--boundary"><summary>哪些结论还不能下？<span class="deep-chapter-hint">展开细节</span></summary><div class="deep-chapter-body"><div class="deep-table" tabindex="0" role="region" aria-label="精读内容比较表"><table><thead><tr><th scope="col">已有技术背景</th><th scope="col">该论文的推进</th></tr></thead><tbody><tr><td>MuZero、Dreamer：预测模型用于规划</td><td>把预测纳入候选反馈分配及跨轮次系统更新</td></tr><tr><td>强化学习、自训练、Reflexion：利用反馈改进行为</td><td>明确 Policy/Workflow 的版本继承和异步更新</td></tr><tr><td>常规校准与版本回退</td><td>用预测可靠性、证据覆盖、预算和 Policy–WM 配对检查组织统一协议</td></tr></tbody></table></div><aside class="deep-note deep-note--paper"><b>合理的创新定位</b><p>更像“系统级自我改进协议 + 多领域验证”，而不是首次提出世界模型、基于反馈学习或检查回退。五类实验覆盖不同路径；论文也说明仍需单一任务中的长期联合多轮评估。</p></aside><ul class="deep-bullets"><li>即时排序无法生成原 Policy 从未提出的好解，也不能解决候选分布外的可靠性。</li><li>只有被选中测试的候选提供观测，WM 可能持续低估某些正确但少见的方案。</li><li>配对门控不等同于旧任务长期不遗忘，或恶意行为不会被写入记忆。</li><li>评价标准在实验协议中固定；“评估器本身也会被改写”仍是开放问题。</li></ul></div></details><details class="deep-chapter" id="deep-rsi-anything-2610-13912--research"><summary>如果我们接着做，最值得验证什么？<span class="deep-chapter-hint">展开细节</span></summary><div class="deep-chapter-body"><aside class="deep-note deep-note--proposal"><b>延伸研究构想（非 RSI-Anything 原文结论）</b><p>Agent 能否预测“哪一次真实试错会让下一轮独立能力提升最多”，而不仅是“当前哪一个方案成功概率最高”？</p></aside><div class="deep-formula"><b>我们的学习收益目标（概念式）</b><code>V_learn(a) = E[Perf(θ_after | test(a)) − Perf(θ_after | matched no-test(a))]</code><p><strong>怎么理解：</strong>与相同训练预算但没有该候选反馈的路径做对照，度量真实学习增益。</p><p class="deep-caveat"><strong>边界：</strong>不同于论文 Eq. (7) 的即时效用；需要来自相同检查点的受控训练和独立测试。</p></div><div class="deep-test-list"><article class="deep-test"><h4>实验 A：即时成功 vs 学习价值</h4><p><b>实验设计：</b>固定代码生成器、更新机制及反馈预算；比较即时成功率排序与下一轮学习增益排序。</p><p><b>决定性证据：</b>在独立任务上衡量 ΔPerf、负迁移、实际测试成本；小型诊断集全测候选，估计选择偏差。</p></article><article class="deep-test"><h4>实验 B：Pair Gate 的独立必要性</h4><p><b>实验设计：</b>由同一组更新构造 P₀W₀、P₁W₀、P₀W₁、P₁W₁ 四配对；有/无 Pair Gate 多轮对照。</p><p><b>决定性证据：</b>记录“组件分别变好但组合退步”的频率、长期净增益和额外门控成本。</p></article><article class="deep-test"><h4>实验 C：I5 模型间交换舞伴</h4><p><b>实验设计：</b>从同一学生模型检查点，按最强伙伴、相近伙伴、随机伙伴、预测最高学习增益伙伴等预算学习。</p><p><b>决定性证据：</b>独立测试中相对于无教师等预算学习的增益，以及随模型能力变化而发生的最优伙伴迁移。</p></article></div><aside class="deep-note deep-note--boundary"><b>安全与追溯要求</b><p>保留候选/预测/真实执行/训练准入/门控数据的版本归因，独立检验评估器被绕过、越权操作及有害知识持久化，而非仅凭提高当前分数宣布安全。</p></aside></div></details></div></section><div class="deep-back"><a href="reading-cards.html#rsi-anything-2610-13912">返回论文速览卡片</a></div><div class="links deep-source-links"><a class="link-btn" target="_blank" rel="noopener noreferrer" href="https://arxiv.org/html/2610.13912">arXiv 原文</a><a class="link-btn" target="_blank" rel="noopener noreferrer" href="https://arxiv.org/pdf/2610.13912">PDF 原文</a><a class="link-btn" target="_blank" rel="noopener noreferrer" href="https://github.com/Gen-Verse/RSI-Anything">作者代码</a></div></div>

## 从相邻领域迁移方法 / 六条方法桥接路线

<div class="table-wrap"><table><thead><tr><th>来源</th><th>迁移对象</th><th>强简单替代</th><th>继续的依据</th></tr></thead><tbody><tr><td>元学习 / 学习优化器 <a class="cite" href="references.html#M01" title="Learning to learn by gradient descent by gradient descent">[M01]</a><a class="cite" href="references.html#M02" title="RL²: Fast Reinforcement Learning via Slow Reinforcement Learning">[M02]</a></td><td>跨初始 Agent 学到可重用改进策略。</td><td>固定优化器、同容量历史条件策略。</td><td>重置学习者后仍改善新任务学习曲线。</td></tr><tr><td>课程 / Learning-to-Teach <a class="cite" href="references.html#M03" title="Automated Curriculum Learning for Neural Networks">[M03]</a><a class="cite" href="references.html#M04" title="Teacher-Student Curriculum Learning (TSCL)">[M04]</a><a class="cite" href="references.html#M06" title="Learning to Teach with Dynamic Loss Functions">[M06]</a></td><td>联合选择任务、帮助和巩固方式。</td><td>均匀、难度优先、学习进展 bandit。</td><td>任务相同时，干预方式或次序仍重要。</td></tr><tr><td>知识追踪 <a class="cite" href="references.html#M05" title="Deep Knowledge Tracing">[M05]</a></td><td>跟踪独立表现、帮助依赖和受干扰后的状态。</td><td>历史成功率、DKT 风格序列预测。</td><td>预测干预效果，而非仅预测下一题成败。</td></tr><tr><td>双重控制 <a class="cite" href="references.html#M07" title="Dual Control for Approximate Bayesian Reinforcement Learning">[M07]</a></td><td>Probe 既练习又辨别瓶颈。</td><td>随机、最高不确定性 Probe；普通 bandit。</td><td>信息真正改变后续决策和延迟收益。</td></tr><tr><td>持续学习 / 重放 <a class="cite" href="references.html#M08" title="Prioritized Experience Replay">[M08]</a><a class="cite" href="references.html#M09" title="Online Continual Learning with Maximally Interfered Retrieval">[M09]</a></td><td>按更新干扰安排重练与固化。</td><td>随机重放、PER、MIR、TSCL。</td><td>多看一遍旧数据不能解释收益。</td></tr><tr><td>预测辅助规划 <a class="cite" href="references.html#S11" title="Dream-RSI: Recursive Self-Improvement through Evolving Worlds">[S11]</a><a class="cite" href="references.html#S13" title="RSI-Anything: Unlocking Recursive Self-Improvement with World Models">[S13]</a></td><td>从环境动作后果转向学习干预后的能力变化。</td><td>直接总分预测、任务语义先验。</td><td>多步规划比单步选择有用，误差可控。</td></tr></tbody></table></div>

## 从相邻领域迁移方法 / 候选核心：学习响应，而非自评分数表

<p>系统状态为 <code>s_t = (θ_t, h_t, m_t)</code>：参数、Harness 与持久记忆；元策略为 <code>π_φ</code>。学习动作 <code>a_t</code> 指定练习对象、帮助方式和更新操作。我们拟学习：</p><div class="equation">F_ψ(b_t, a_t, Δ_t) → distribution(Δc_now, Δc_after-H)</div><p><code>b_t</code> 是依据执行形成的能力状态估计，<code>Δ_t</code> 描述后续干扰，<code>c</code> 是多个能力族的独立表现向量。预测同时包括目标收益与其他能力退化。这是待验证设计，不预先宣称能够识别所有隐变量。</p><div class="flow"><div><b>同一旧版本</b><small>冻结快照与环境</small></div><div><b>随机分配干预</b><small>帮助 / 更新动作</small></div><div><b>即时与延迟探测</b><small>不用训练答案</small></div><div><b>学习响应分布</b><small>收益、退化、不确定性</small></div><div><b>新状态选动作</b><small>以执行校正</small></div></div><p>“某动作常在困难样本上失败”不代表动作有害。先用同版本分叉和随机干预获取局部效应，再谈建模。与知识追踪及前瞻课程的区别须通过此设计验证，而非靠“因果世界模型”命名。<a class="cite" href="references.html#M05" title="Deep Knowledge Tracing">[M05]</a><a class="cite" href="references.html#S18" title="Anticipating the Consequences of Curriculum Decisions with Large Language Models">[S18]</a></p>

## 从相邻领域迁移方法 / 什么时候值得多做一次诊断？

<p>理想信息价值：得到诊断后，最佳改进决策的期望收益增加多少，再减诊断成本。</p><div class="equation">VOI(q) = E_q[max_a E(U(a) | D,q)] − max_a E(U(a) | D) − cost(q)</div><p>这是目标，不是假设能精确求解的公式。先用小型预测集成和一步候选重排，比较随机、最高分歧与收益相关的 Probe。只有信息确实改善后续选择，才扩大为多步元 RL。双重控制的现成理论保证不能直接套用到非平稳 LLM 自修改。<a class="cite" href="references.html#M07" title="Dual Control for Approximate Bayesian Reinforcement Learning">[M07]</a></p><p><b>反例：</b>Probe 准确判断某个 API 是否存在，但所有候选修复都不依赖该 API；信息很多，却没有决策价值。</p>

## 从相邻领域迁移方法 / 重置学习者，保留元策略

<div class="table-wrap"><table><thead><tr><th>条件</th><th>保留</th><th>重置 / 破坏</th><th>检验</th></tr></thead><tbody><tr><td>旧元策略</td><td>固定 π₀</td><td>相同参数、Harness、空历史。</td><td>学习效率基线。</td></tr><tr><td>新元策略</td><td>训练后的 π₁</td><td>与上行完全相同。</td><td>元经验迁移。</td></tr><tr><td>打乱历史</td><td>相同长度、数量记录。</td><td>破坏干预和结果的对应。</td><td>是否只是更多上下文。</td></tr><tr><td>持续更新消融</td><td>底层 Agent 都允许更新。</td><td>仅一组冻结元策略。</td><td>在线元更新是否有效。</td></tr></tbody></table></div><p>重置测试沿用元学习思想，不是独立算法创新。它是 Meta-RSI 主张所需证据之一；双方获得同等长度历史和调用额度。<a class="cite" href="references.html#M02" title="RL²: Fast Reinforcement Learning via Slow Reinforcement Learning">[M02]</a><a class="cite" href="references.html#S08" title="Harness Learning Enables Generalizable Test-Time Adaptation">[S08]</a></p>

## 从相邻领域迁移方法 / 避免模块堆叠

<p>第一版只引入一个新决策：<strong>何时、如何提供与撤除学习支持</strong>。编辑器、底座、任务池、验证器共享。若出现长期收益，再加入响应模型；若固定规则同样有效，保留机制结论，不强行加入 RL。</p><div class="note">通用预测器 + contextual bandit 不是弱基线，须得到同样的轨迹、参数规模和执行预算。若它们足以解释结果，复杂结构就没有必要性。</div>

## 教育学与学习科学：如何转成机器机制 / 八类来源的可操作映射

<div class="table-wrap"><table><thead><tr><th>来源</th><th>可借鉴机制</th><th>机器实验变量</th><th>不能照搬</th></tr></thead><tbody><tr><td>自我调节学习 <a class="cite" href="references.html#E01" title="Becoming a Self-Regulated Learner: An Overview">[E01]</a></td><td>目标、监控、策略调整的反馈。</td><td>依据可执行证据改变学习动作。</td><td>三个 Agent 对应三个教学阶段就是创新。</td></tr><tr><td>近端可学区域 <a class="cite" href="references.html#E02" title="A Region of Proximal Learning model of study time allocation">[E02]</a></td><td>不会但可能取得进展，不是盲目追难题。</td><td>同难度题在不同支持下的学习收益。</td><td>模型自报“不懂”是可信能力标签。</td></tr><tr><td>练习性检索 <a class="cite" href="references.html#E03" title="Test-enhanced learning: taking memory tests improves long-term retention">[E03]</a></td><td>主动恢复知识，而非只重读。</td><td>不看答案生成、验证、持久写回。</td><td>冻结模型输出一次就改变了权重。</td></tr><tr><td>间隔学习 <a class="cite" href="references.html#E04" title="Spacing effects in learning: a temporal ridgeline of optimal retention">[E04]</a></td><td>练习组织与后测时距影响保持。</td><td>隔若干其他能力更新后重练。</td><td>静止参数随日历时间自然遗忘。</td></tr><tr><td>例题渐隐 / 自我解释 <a class="cite" href="references.html#E05" title="Transitioning From Studying Examples to Solving Problems: Effects of Self-Explanation Prompts and Fading Worked-Out Steps">[E05]</a></td><td>完整例题到自行补步骤。</td><td>帮助强度、撤除时机、可验证解释。</td><td>解释越长理解越深。</td></tr><tr><td>生产性失败 <a class="cite" href="references.html#E06" title="Learning from productive failure">[E06]</a></td><td>尝试生成后对照与整合知识。</td><td>先尝试后讲解 vs 先讲解后尝试。</td><td>所有错误都有学习价值。</td></tr><tr><td>帮助困境 <a class="cite" href="references.html#E07" title="Exploring the assistance dilemma in experiments with Cognitive Tutors">[E07]</a></td><td>帮助过少与过多都可能不利。</td><td>提示、示范和独立练习的选择。</td><td>帮助越少越高级，强教师必然更差。</td></tr><tr><td>表现与学习不一致 <a class="cite" href="references.html#E08" title="Examining productive failure, productive success, unproductive failure, and unproductive success in learning">[E08]</a></td><td>当前顺利未必长期学得最好。</td><td>即时完成与延迟新任务分开。</td><td>暂时低分就是“更深学习”。</td></tr></tbody></table></div>

## 教育学与学习科学：如何转成机器机制 / 新增机制来源：让教师观察学生独立行动

<p>2013 年 Okita 与 Schwartz 的原始实验将 <b>Recursive Feedback（RF）</b> 与直接反馈区分：学生必须在新情境独立行动，教师再将学生的行为映射回自己曾教过的知识。这给 <a href="teaching.html">I5 教学反馈自进化</a>提供了明确的机器实验条件；但 <b>RF 是教育学概念，不等于 RSI</b>。<a class="cite" href="references.html#E09" title="Learning by Teaching Human Pupils and Teachable Agents: The Importance of Recursive Feedback">[E09]</a></p><p>2026 年 <i>Behaviormetrika</i> 研究进一步发现，在它的人类教育实验中，教师回答可教代理追问时，知识建构型回应与概念/程序能力后测呈正向关系；它提示可设计追问与对照解释，而不能证明 LLM 的参数或技能会因解释而更新。<a class="cite" href="references.html#E10" title="Beyond prior knowledge: the predictive role of knowledge-building in tutor learning">[E10]</a></p><p>相邻 AI 工作已覆盖学生反馈微调教师（NeurIPS 2024 LbT）、学生主动追问（arXiv 25.12）和 Teacher–Student 提示优化（AAAI 2026 MARS），因此仅以费曼学习法命名模型没有创新性。<a class="cite" href="references.html#S20" title="Can LLMs Learn by Teaching for Better Reasoning? A Preliminary Study">[S20]</a><a class="cite" href="references.html#S24" title="Socratic Students: Teaching Language Models to Learn by Asking Questions">[S24]</a><a class="cite" href="references.html#S21" title="MARS: Multi-Agent Adaptive Reasoning with Socratic Guidance for Automated Prompt Optimization">[S21]</a></p>

## 教育学与学习科学：如何转成机器机制 / Hypercorrection：最自信的错误为什么反而可能更容易纠正？

<p>Butterfield 与 Metcalfe（2001）发现 <b>Hypercorrection Effect</b>；Carpenter 等（2018）在真实大学课堂观察到高置信度错误在得到正确反馈后有时更容易被纠正。<a class="cite" href="references.html#E12" title="Errors committed with high confidence are hypercorrected">[E12]</a><a class="cite" href="references.html#E13" title="Hypercorrection of high-confidence errors in the classroom">[E13]</a></p><p>这不等于“自信错误必然值得训练”。Sitzman 等（2014）发现，学习者已有的领域知识与纠错表现密切相关；Foster 等（2022）观察了数学在线诊断题中的置信度与后续相似题表现。<a class="cite" href="references.html#E14" title="Prior knowledge is more predictive of error correction than subjective confidence">[E14]</a><a class="cite" href="references.html#E15" title="School students’ confidence when answering diagnostic questions online">[E15]</a></p><p><b>神经机制的补充：</b>Pine 等（<i>Nature Communications</i>，2018）发现，来自事实反馈的语义预测误差与一周后的记忆更新有关，腹侧纹状体等脑区对该信号敏感。但原研究还展示了错误反馈也可能形成错误记忆，提醒 RSI 必须验证反馈来源，不是冲突越大就越应该直接写入。<a class="cite" href="references.html#E18" title="Knowledge acquisition is governed by striatal prediction errors">[E18]</a></p><p>对 LLM，应区分正确反馈后的原题修复、参数的真实持久更新以及未见题的规则级迁移。详细机制与受控实验在 <a href="i8.html">I8：错误可学习性与跨题迁移</a>。</p>

## 教育学与学习科学：如何转成机器机制 / 这些思想已经部分进入 AI

<p>课程、知识追踪和学习型教学早已转化部分教育学问题；SOAR、ActiveSaddler、EduardoRL 又进入 LLM 与 Agent 场景。贡献须是<strong>新增机制或适用条件</strong>，而不是首次使用“自学、老师、考试”。<a class="cite" href="references.html#M03" title="Automated Curriculum Learning for Neural Networks">[M03]</a><a class="cite" href="references.html#M05" title="Deep Knowledge Tracing">[M05]</a><a class="cite" href="references.html#M06" title="Learning to Teach with Dynamic Loss Functions">[M06]</a><a class="cite" href="references.html#S16" title="ActiveSaddler: Automated Curriculum Learning for Agent Harness Optimization">[S16]</a><a class="cite" href="references.html#S17" title="Teaching Models to Teach Themselves: Reasoning at the Edge of Learnability (SOAR)">[S17]</a><a class="cite" href="references.html#S19" title="The Assistance Dilemma: Learning to Teach via Multi-Turn Reinforcement Learning">[S19]</a></p><p>EduardoRL 已遮蔽教师话语。我们的候选不是重做这一后测，而是问：后续不同能力学习带来干扰时，怎样组织<strong>帮助—独立练习—巩固</strong>的完整序列？须与短程目标、固定渐隐及普通重放直接比较。</p>

## 教育学与学习科学：如何转成机器机制 / 贯穿例子：分页工具调用

<div class="example"><h3>失败现象</h3><p>Agent 处理第一页却漏后续页。完整调用示范使当前任务成功，但换数据和 API 名称又失败。</p><h3>四种学习动作</h3><p><b>A：</b>给完整示范；<b>B：</b>仅提示检查 continuation token；<b>C：</b>先要求提出终止条件再给反例；<b>D：</b>无提示独立尝试。随后使用同一个固定更新器。</p><h3>三个层次</h3><p>原任务完成率；不同名称、页数的新任务独立成功率；学习另一种分页 / 重试机制后，原能力是否保留。近迁移不能仅替换答案数字；远迁移需改变工具组合、依赖或恢复条件。</p><h3>防止偷换概念</h3><p>保留技能文件时报告系统层面学习。只保留 LoRA 且清空会话与技能时，才评价参数学习。分栏报告，不相加为同一能力分。</p></div>

## 教育学与学习科学：如何转成机器机制 / 必须允许的相反结果

<p><b>强示范最好：</b>强教师示范加固定蒸馏可能在所有保持测试上占优。接受结果，不强行宣称“适度困难”有效。</p><p><b>延迟只是更多训练：</b>控制曝光、梯度步数和更新顺序后差异若消失，不能归因于间隔机制。</p><p><b>只有上下文记住了：</b>清空会话后增益消失，就属于上下文适应，不能改写为持久自进化。</p><div class="note">人类学习效应有任务、先备知识和教学设计条件。机器研究也要找适用边界，而不是只挑支持类比的例子。</div>

## I1–I8：八个研究问题 / 研究方向，一眼看懂


 <p>共同目标：<strong>让 Agent 不只是从执行结果里积累经验，还能随着自身能力变化，学会选择更好的自我改进方式。</strong>I1–I5 保留原有研究问题；I6 只比较失败轨迹过程，I7 只比较学习顺序，I8 从知识准备与共同错误规则解释迁移。</p>
 <div class="idea-board">
 <a class="idea-board-card" href="#idea-1"><span class="idea-id">I1 · 脚手架学习法</span><b>哪些该自己学会，哪些用时再查？</b><small>辅助使用与内化的取舍</small></a>
 <a class="idea-board-card" href="idea-i2.html"><span class="idea-id">I2 · 因材施教</span><b>学生变强，教师也能越来越会教吗？</b><small>真实学习反馈驱动教师与学生共同更新</small></a>
 <a class="idea-board-card" href="#idea-3"><span class="idea-id">I3 · 温故知新</span><b>新方法有用，却和旧方法冲突怎么办？</b><small>复习并解决适用条件冲突</small></a>
 <a class="idea-board-card" href="#idea-4"><span class="idea-id">I4 · 生产性失败</span><b>失败一次就总结，还是再试几次？</b><small>判断何时证据足够更新 Skill</small></a>
 <a class="idea-board-card" href="idea-i5.html"><span class="idea-id">I5 · 十模型互教</span><b>什么时候交换舞伴，才能一起变强？</b><small>十模型学习网络的动态重组</small></a>
 <a class="idea-board-card" href="#idea-6"><span class="idea-id">I6 · 失败学习价值</span><b>哪条失败更值得纠正？何时停下再回来？</b><small>固定纠错方式，比较失败的独立收益与继续尝试成本</small></a>
 <a class="idea-board-card" href="#idea-7"><span class="idea-id">I7 · 学习顺序</span><b>先看例题，还是先独立尝试？</b><small>固定教材与预算，研究独立能力、探索与多轮迁移</small></a>
 <a class="idea-board-card" href="#idea-8"><span class="idea-id">I8 · 错误学习迁移</span><b>改正哪个错误，能够学会一整类题？</b><small>Hypercorrection 与跨题净学习收益</small></a>
 </div>
 <p class="idea-outline-key"><b>I1–I8 统一阅读顺序：</b>Challenge（难在哪里） → 现有工作（别人做到了哪） → Insight（为何可解） → Design（如何做） → 实验设计（怎么验证）。每条研究方向先把科学问题和证据边界说清楚，再展开技术细节；I6–I8 均保留独立详情页。</p>
 <p class="status">状态：I1–I8 研究问题已整理；I6 与 I7 正交拆分，I8 保留独立机制验证；尚无本项目的受控实测结果。</p>
 <p>本站将它们挂到 RSI 的四个问题与安全轴下：<b>信号对不对 / 有没有新东西 / 采不采得到 / 吸收了会不会丢 / 安全。</b>这些标签表示要研究的环节，不表示问题已经解决。详见 <a href="reading-cards.html">论文阅读卡片</a>。</p>


## I1–I8：八个研究问题 / I1：脚手架学习法——哪些该自己学会，哪些用时再查？


 <div class="idea-focus"><span class="idea-axis">采不采得到</span><span class="idea-axis">吸收了会不会丢</span><p><b>一句话：</b>调试思路最好自己掌握，但经常变化的 API 规则可以用时再查。Agent 能自己判断哪些该学会、哪些该留作外部帮助吗？</p></div>
 <div class="idea-steps">
 <div class="idea-step"><h3>Challenge <small>（难在哪里）</small></h3><p>在帮助下完成任务，不等于撤掉帮助后还能独立做。什么都写进 Skill，可能把过时规则也记住；什么都留在外部，又要反复查询。难的是还不知道未来任务怎么变，就要先决定哪些知识值得长期掌握。</p></div>
 <div class="idea-step"><h3>现有工作 <small>（别人研究了什么）</small></h3><p><b>R²Orch</b> 研究的是怎样把 Skill 内化、什么时候可以撤掉 Skill；<b>PATS</b> 研究的是随着学习进展怎样调整并撤除临时支架。我们不是再做一次“帮助逐渐减少”，而是研究<strong>不同经验究竟该留在哪里</strong>。<a class="cite" href="references.html#S26" title="R²Orch: Recursive Self-Improvement for Agent Orchestration via Self-Play within a Skill-Internalization Loop">[S26]</a><a class="cite" href="references.html#S27" title="PATS: Policy-Aware Training Scaffolding for Agentic Reinforcement Learning">[S27]</a></p></div>
 <div class="idea-step"><h3>Insight <small>（为何可解）</small></h3><p>外部帮助并不都一样。稳定且反复使用的操作方法可能适合自己学会；容易变化的事实可能更适合按需查询。比较<strong>撤除帮助后的独立能力、知识变化频率和长期成本</strong>，有机会学会这两种方式的取舍。</p></div>
 <div class="idea-step"><h3>Design <small>（如何做）</small></h3><p>将辅助经验分成稳定方法、易变规则和临时提示，让 Agent 选择内化、外置查询或混合保留。分开测“完全不给帮助”和“允许按需查询”的表现，再根据这些结果更新下一轮的选择方式。</p>
 <div class="flow"><div><b>拆分辅助经验</b><small>稳定方法 / 易变知识</small></div><div><b>选择存放方式</b><small>内化 / 查询 / 混合</small></div><div><b>新任务测能力</b><small>撤辅与查询分开</small></div><div><b>更新取舍规则</b><small>比较收益和成本</small></div></div></div>
 <div class="idea-step"><h3>实验设计 <small>（怎么验证）</small></h3><p>准备稳定的调试技巧与会变动的 API 规则，在相同预算下比较<strong>全部内化、全部外置、固定渐隐、自适应取舍</strong>，并与 R²Orch/PATS 的可复现做法比较。重点看无辅助的新任务成功率、API 更新后的适应性、调用成本和旧能力退化。如果固定规则同样好，说明动态选择还没有额外价值。</p></div>
 </div>

## I1–I8：八个研究问题 / I2：因材施教——学生变强，教师也能越来越会教吗？


 <div class="idea-focus"><span class="idea-axis">信号对不对</span><span class="idea-axis">吸收了会不会丢</span><p><b>一句话：</b>学生通过教学学会解题，教师通过学生真正的学习结果学会教学；当学生能力变化，教师继续修订教法。</p></div>
 <div class="idea-steps">
 <div class="idea-step"><h3>Challenge <small>（难在哪里）</small></h3><p>同一个学生变强后，原来最有用的教法可能不再合适。但师生两边分数都上涨，不代表教师更会教——也可能只是学生本来就更容易教了。必须把教师教学能力与学生解题能力分开测。</p></div>
 <div class="idea-step"><h3>现有工作 <small>（别人研究了什么）</small></h3><p><b>Bayesian Teaching</b> 表明模仿证据条件下的判断可能比模仿 Oracle 答案更有迁移价值；<b>RLT</b> 已训练教师产生可学的解释；<b>SOAR</b> 已用学生真实训练增益更新出题教师，并提升学生检查点。我们研究固定题目后，教师如何从持续成长的学生身上学习更合适的教法，不把双边更新本身当创新。<a class="cite" href="references.html#S100" title="Bayesian teaching enables probabilistic reasoning in large language models">[S100]</a><a class="cite" href="references.html#S101" title="Reinforcement Learning Teachers of Test Time Scaling (RLT)">[S101]</a><a class="cite" href="references.html#S17" title="Teaching Models to Teach Themselves: Reasoning at the Edge of Learnability (SOAR)">[S17]</a> 同时保留原来的边界：<b>RSIFlow</b> 选择更新对象，<b>MetaSkill-Evolve</b> 更新任务与元技能；I2 首先固定更新器，只比较教法如何学习。<a class="cite" href="references.html#S28" title="RSIFlow: Adaptive Self-Improvement Workflows with an Evolving Meta-Agent">[S28]</a><a class="cite" href="references.html#S06" title="MetaSkill-Evolve: Recursive Self-Improvement of LLM Agents via Two-Timescale Meta-Skill Evolution">[S06]</a></p></div>
 <div class="idea-step"><h3>Insight <small>（为何可解）</small></h3><p>学生对不同教法的<b>学习反应</b>可能随能力改变。少量同起点试教能揭示这种变化；把结果写入教师的教学策略，就有机会让教师不仅适应一次任务，而且积累可迁移的教学能力。</p></div>
 <div class="idea-step"><h3>Design <small>（如何做）</small></h3><p>固定伙伴、教材和教学顺序，从同一学生快照试教；学生真实更新后，清空课堂对话并测新题。用独立收益改进教师教法，同时保留学生新能力；下一轮面对成长后的学生继续循环。原 I2 的固定 Skill 更新轨道保留，双 LoRA 参数更新单独验证。</p><div class="flow"><div><b>同起点试教</b><small>固定题目，改变解释</small></div><div><b>学生真学习</b><small>参数 / 任务 Skill</small></div><div><b>撤辅测新题</b><small>收益、回归与总成本</small></div><div><b>教师学教法</b><small>教学策略持久更新</small></div></div></div>
 <div class="idea-step"><h3>实验设计 <small>（怎么验证）</small></h3><p>比较固定教法、可读取当前状态但不更新的教师、在固定学生库上训练的教师，以及由当前学生真实收益训练的教师。另做<b>教师版本 × 冻结学生快照</b>交叉测试，检验后期教师是否真的更会教。I2 不更换伙伴，不选择失败材料，不优化先做还是先学；分别与 I5、I6、I7、I8 保持边界。</p><p><a href="idea-i2.html"><b>阅读 I2 合并方案：证据、最近邻、双边更新与决定性实验 →</b></a></p></div>
 </div>

## I1–I8：八个研究问题 / I3：温故知新——新方法有用，却和旧方法冲突怎么办？


 <div class="idea-focus"><span class="idea-axis">吸收了会不会丢</span><span class="idea-axis">安全</span><p><b>一句话：</b>Agent 学会一个更快的新方法，却把以前在另一种场景下正确的做法弄坏了。新旧本事能不能都留下来？</p></div>
 <div class="idea-steps">
 <div class="idea-step"><h3>Challenge <small>（难在哪里）</small></h3><p>新 Skill 确实提高了部分任务的成功率，却可能让旧任务变差。直接回滚就失去了新进步；把所有旧题重做一遍又浪费预算。首先得弄清是旧知识真忘了，还是新旧规则用错了地方。</p></div>
 <div class="idea-step"><h3>现有工作 <small>（别人研究了什么）</small></h3><p><b>HCL</b> 研究的是 Harness 更新后如何兼顾新任务与旧任务；<b>SkillBoost</b> 研究的是用回归检查和约束防止新 Skill 伤害旧能力。我们进一步研究<strong>当新旧方法都各有用处时，怎样通过复习修好冲突，而不是只能拒绝新更新</strong>。<a class="cite" href="references.html#S29" title="Harness Continual Learning: Continual Adaptation Beyond Model Parameters">[S29]</a><a class="cite" href="references.html#S30" title="Rethinking Self-Evolution: A Constrained Exploration-Exploitation Process for Mitigating Skill Overfitting (SkillBoost)">[S30]</a></p></div>
 <div class="idea-step"><h3>Insight <small>（为何可解）</small></h3><p>有些退化未必是忘记，而是<strong>两个原本都有效的方法，被用在了不适合的场景</strong>。只要找到“什么时候用旧规则、什么时候用新规则”的区别，少量针对这些边界的练习，可能比全部重放旧经验更有效。</p></div>
 <div class="idea-step"><h3>Design <small>（如何做）</small></h3><p>比较修改前后的失败轨迹，找到出现冲突的条件，自动生成少量只改变一个关键条件的练习。用这些例子修订 Skill 的适用范围或选择规则，必要时再对参数做巩固。最终既要会用新方法，也不能丢旧能力。</p>
 <div class="flow"><div><b>发现旧任务退化</b><small>新旧版本对比</small></div><div><b>定位冲突条件</b><small>何时该用哪一条</small></div><div><b>有针对性地复习</b><small>只练容易混淆的场景</small></div><div><b>一起检验新旧能力</b><small>旧题 / 新题 / 组合题</small></div></div></div>
 <div class="idea-step"><h3>实验设计 <small>（怎么验证）</small></h3><p>准备两套分别有效、合起来容易冲突的 Skill，并加入自然学习中出现的冲突案例。比较<strong>退化即回滚、均匀重放、MIR 风格重放、针对冲突条件复习</strong>；固定复习次数和记忆预算。分别测旧能力保持、新能力增益、组合任务成功率。如果优势只来自存了更多规则或多练了题，就不能归因于我们的复习方法。<a class="cite" href="references.html#M09" title="Online Continual Learning with Maximally Interfered Retrieval">[M09]</a></p></div>
 </div>

## I1–I8：八个研究问题 / I4：生产性失败——失败一次就总结，还是再试几次？


 <div class="idea-focus"><span class="idea-axis">信号对不对</span><span class="idea-axis">有没有新东西</span><span class="idea-axis">采不采得到</span><p><b>一句话：</b>API 超时一次，Agent 就总结“这个工具以后别用”，可能学错。什么时候应该继续试，什么时候才值得把经验写进 Skill？</p></div>
 <div class="idea-steps">
 <div class="idea-step"><h3>Challenge <small>（难在哪里）</small></h3><p>一次失败可能是策略错了，也可能只是网络偶尔超时。太早总结，会把偶然现象当成通用规律；继续试太久，又会浪费探索预算。RSI 不一定有人告诉它正确做法，需要它自己根据执行反馈辨别原因。</p></div>
 <div class="idea-step"><h3>现有工作 <small>（别人研究了什么）</small></h3><p><b>ActiveSaddler</b> 研究的是哪些失败模式更值得继续训练；<b>Trace2Skill</b> 研究的是怎样从多条执行轨迹提炼可复用 Skill。我们研究的是<strong>面对这一次失败，下一步试什么，什么时候证据够了可以开始总结</strong>。<a class="cite" href="references.html#S16" title="ActiveSaddler: Automated Curriculum Learning for Agent Harness Optimization">[S16]</a><a class="cite" href="references.html#S31" title="Trace2Skill: Distill Trajectory-Local Lessons into Transferable Agent Skills">[S31]</a></p></div>
 <div class="idea-step"><h3>Insight <small>（为何可解）</small></h3><p>不同失败原因，往往会对下一次尝试给出不同预测。<strong>一次只改变一个关键条件</strong>，就有可能排除错误解释。当继续探索已经很难提供新信息时，再停止并总结经验。关键不是失败越多越好，而是每次尝试能否帮助弄清原因。</p></div>
 <div class="idea-step"><h3>Design <small>（如何做）</small></h3><p>失败后先列出两三个可能原因，选择最能把它们区分开的安全小实验，例如同样条件重试或只改变一个 API 参数。持续记录支持和反对各原因的证据，足够确定再更新 Skill；证据不够时允许暂不总结。所有试验只在受控环境运行。</p>
 <div class="flow"><div><b>列出失败原因</b><small>策略错 / 工具故障 / 偶发</small></div><div><b>做辨别性尝试</b><small>只变一个关键条件</small></div><div><b>判断何时停止</b><small>证据是否足够</small></div><div><b>形成新 Skill</b><small>再到未见任务复验</small></div></div></div>
 <div class="idea-step"><h3>实验设计 <small>（怎么验证）</small></h3><p>在 API 异常、工具使用和代码执行任务上，比较<strong>失败后立即总结、固定重试 N 次、随机补充尝试、针对可能原因选试验并决定停止</strong>。匹配 Token、环境调用和总预算，混合可控故障与自然失败。主要比较写入错误规则的比例、未见场景的迁移、单位成本的学习收益；不把“多试几次自然多成功”误当成新机制。整个过程不需要外部教师告诉标准答案。</p></div>
 </div>

## I1–I8：八个研究问题 / I5：十模型互教——什么时候交换舞伴，才能一起变强？


<div class="idea-focus"><span class="idea-axis">有没有新东西</span><span class="idea-axis">采不采得到</span><span class="idea-axis">吸收了会不会丢</span><p><b>一句话：</b>十个模型各自持续更新。我们不仅问谁更强，而是问谁教的东西我现在学得进、继续交流还有多少收益、何时换人才能共同成长。</p></div>
<div class="idea-steps">
<div class="idea-step"><h3>Challenge <small>（难在哪里）</small></h3><p>伙伴帮我答对，不等于自己学会；学完涨分，也可能只是同样预算自己练就能取得的进步。双方能力和已学知识不断变化，原先最好的搭档可能变得重复；换伴顺序的收益还可能只是普通课程效应。</p></div>
<div class="idea-step"><h3>现有工作 <small>（别人研究了什么）</small></h3><p><b>CORY</b> 已联合训练两个模型并交换角色；<b>PopuLoRA</b> 已做 LoRA 群体自博弈；<b>OPCoD</b> 已用同伴反馈进行双向自蒸馏；<b>CERA-MoA</b> 已联合更新路由与 Agent；<b>HACE</b> 已做异构互惠学习。动态伙伴选择也已有 AAMAS 2026 <b>SE Workshop</b> 前作，不能写成主会或首次提出。<a class="cite" href="references.html#S200" title="Coevolving with the Other You: Fine-Tuning LLM with Sequential Cooperative Multi-Agent Reinforcement Learning (CORY)">[S200]</a><a class="cite" href="references.html#S32" title="PopuLoRA: Co-Evolving LLM Populations for Reasoning Self-Play">[S32]</a><a class="cite" href="references.html#S33" title="Be My Tutor: On-Policy Co-Distillation for Mutual LLM Improvement via Peer Feedback (OPCoD)">[S33]</a><a class="cite" href="references.html#S202" title="CERA-MoA: Co-Evolving Routing Mechanisms with Continually Learning LLM Agents">[S202]</a><a class="cite" href="references.html#S90" title="Heterogeneous Agentic Coevolution (HACE)">[S90]</a><a class="cite" href="references.html#S201" title="LLM Agents Learn Effective Partner Selection for Mutual Cooperation in Social Dilemmas">[S201]</a></p><p>此前的 MACE 伙伴探索和 Nature 交流顺序研究继续作为相邻证据；它们不直接证明十模型权重学习收益。<a class="cite" href="references.html#S34" title="Multi-Agent LLMs Fail to Explore Each Other (MACE: Multi-Agent Contextual Exploration)">[S34]</a><a class="cite" href="references.html#E90" title="Bridge ties bind collective memories">[E90]</a></p></div>
<div class="idea-step"><h3>Insight <small>（为何可解）</small></h3><p>伙伴的价值应由<strong>双方撤伴后的表现，减去同预算自学后的表现</strong>衡量。对方独有的知识、我当前的可吸收性和过去接触过的内容，可能共同解释为何该留伴或换伴；这是待检验关系，不是固定强弱排名。</p></div>
<div class="idea-step"><h3>Design <small>（如何做）</small></h3><p>固定 OPCoD 式 LoRA 自蒸馏和反馈门控，正常每轮五对、双向教学。小规模受控试学得到有方向净增益；用同容量的带/不带历史收益预测器在十节点图中选配对，按边际收益与不确定性决定持续多久。缺乏可信增益时允许同预算自学。<strong>所有试探和回退成本计入总预算。</strong></p><div class="flow"><div><b>独立十模型</b><small>五规模 × 数学/代码</small></div><div><b>固定互教更新</b><small>只改变伙伴关系</small></div><div><b>相对自学测收益</b><small>撤伴、新题、保持</small></div><div><b>继续或重配</b><small>历史、预算与置信度</small></div></div></div>
<div class="idea-step"><h3>实验设计 <small>（怎么验证）</small></h3><p>先做四模型 6 配对，再开展十模型实验；比较固定伙伴、随机、round-robin、能力匹配、即时收益和独立净增益。顺序实验同时固定边集合、接触次数和预算，并加入<strong>相同材料重排、冻结教师、双方共同更新</strong>三层控制。主指标为个人独立能力、群体学习效率、旧能力保持与验证过的技能覆盖，不是投票成绩。</p><p class="idea-side-note">I5只研究谁与谁学、持续多久和伙伴顺序；不改变 I2 学法、I3 巩固、I6 轨迹、I7 先试/先学、I8 错误选择。<a href="idea-i5.html">完整方法、最近邻、公式和实验契约</a>；<a href="idea-i5.html#teaching-feedback">历史教学反馈支线</a>仍在唯一 I5 页面内。</p></div>
</div>

## I1–I8：八个研究问题 / I6：失败学习价值——同样答错，哪条失败更值得学习？


 <div class="idea-focus"><span class="idea-axis">信号对不对</span><span class="idea-axis">有没有新东西</span><span class="idea-axis">采不采得到</span><p><b>一句话：</b>同一个模型解同一道积分题，两次都给出相同的错误答案：一次直接套错公式，一次尝试了几个正确步骤却仍答错。<strong>用哪一次失败来学习，才能让以后更多新题做对？又该在什么时候停止重试、改天再学？</strong></p></div>
 <div class="idea-steps">
 <div class="idea-step"><h3>Challenge <small>（难在哪里）</small></h3><p>只看最终答案，两条失败都是零分；但错误过程中有没有正确子步骤、有没有暴露新原因，可能决定这次纠错能学到什么。<strong>失败轨迹更长、看起来更接近答案，也未必更值得训练</strong>。如果同一道题已连续失败，继续采样可能浪费预算；可现在学不会，不代表补过基础后仍学不会。</p></div>
 <div class="idea-step"><h3>现有工作 <small>（别人研究了什么）</small></h3><p><a href="https://aclanthology.org/2024.acl-long.45/" target="_blank" rel="noopener noreferrer"><b>Learn from Failure</b></a> 研究如何利用失败的定理证明轨迹；<b>SOAR</b> 根据学生实际进步生成值得学习的新题；<b>BEACON</b> 研究推理时何时停止继续采样；<b>Region of Proximal Learning</b> 研究人类何时离开当前学习材料。我们研究的是<strong>同题同样答错时，哪条失败过程在固定纠错后更能提高未来独立能力，以及何时停止收集这种失败</strong>，不是更换教学方式或提高当前 pass@k。<a class="cite" href="references.html#S47" title="Teaching Models to Teach Themselves: Reasoning at the Edge of Learnability (SOAR)">[S47]</a><a class="cite" href="references.html#S48" title="BEACON: Bayesian Optimal Stopping for Efficient LLM Sampling">[S48]</a><a class="cite" href="references.html#E16" title="A Region of Proximal Learning model of study time allocation">[E16]</a></p></div>
 <div class="idea-step"><h3>Insight <small>（为何可解）</small></h3><p>失败过程比最终对错多提供一层信息：<strong>模型已经走对了哪几步、在哪个规则上反复走错、下一次失败是否仍会暴露新缺口</strong>。从相同模型出发，用相同正确反馈分别纠正不同失败，再比较未见题的独立进步，就可以为每条失败估计真实学习价值。如果新失败已很难增加收益，就应比较纠正已有失败、换题或暂缓后重访。</p></div>
 <div class="idea-step"><h3>Design <small>（如何做）</small></h3><p>从同一模型检查点在同一道题上采集多条自然失败，尽量匹配最终错误、轨迹长度与反馈信息；随机指定其中一条作为学习材料。<strong>固定正确答案、教学顺序、更新器和训练预算</strong>，分叉更新并在撤掉提示后测新题。先用真实迁移增益给失败定价，再训练只看纠错前信息的轻量预测器；比较继续收集、纠正已有、换题、暂缓重访的下一次投入。</p>
 <div class="flow"><div><b>同题收集不同失败</b><small>同版模型，结果尽量一致</small></div><div><b>固定纠错方法</b><small>同反馈、同 LoRA/Skill 预算</small></div><div><b>新题独立后测</b><small>迁移、旧能力回归、成本</small></div><div><b>选失败与停止时机</b><small>继续 / 换题 / 暂缓重访</small></div></div></div>
 <div class="idea-step"><h3>实验设计 <small>（怎么验证）</small></h3><p>先做同题配对实验，比较<strong>只看正确解法、随机失败、最长失败、最接近正确的失败、按置信度选、预测学习增益选</strong>；模型快照、教师反馈和总 token/FLOPs 匹配。报告无提示未见题提升、旧能力损失与失败价值的跨题稳定性。再比较固定重试 K 次、简单学习进展阈值、收益驱动停止/暂缓，并事先约定重访条件。如果差异只来自更长轨迹或更多训练，或早停没超过简单阈值，就缩小主张，不另加复杂停止模块。<a class="cite" href="references.html#M12" title="Automated Curriculum Learning for Neural Networks">[M12]</a><a class="cite" href="references.html#S45" title="SPaCe: Unlocking Sample-Efficient Large Language Models Training With Self-Pace Curriculum Learning">[S45]</a></p><p class="idea-side-note"><b>正交边界：</b>I6 固定<strong>先试还是先学</strong>（交给 <a href="#idea-7">I7</a>）和<strong>纠错规则类型</strong>（交给 <a href="#idea-8">I8</a>），只研究失败中间过程的增量价值与是否继续投入。<a href="idea-i6-failure-value.html">查看同题配对、停学与重访的完整实验 →</a></p></div>
 </div>

## I1–I8：八个研究问题 / I7：学习顺序——先看例题，还是先独立尝试？


 <div class="idea-focus"><span class="idea-axis">采不采得到</span><span class="idea-axis">吸收了会不会丢</span><p><b>一句话：</b>学同一道多步骤数学题，模型 A 先看完整解法再练习，模型 B 先独立尝试、失败后再看同一解法。<strong>学完撤掉例题，谁更会解新题？这种优势会不会随着模型变强而反过来？</strong></p></div>
 <div class="idea-steps">
 <div class="idea-step"><h3>Challenge <small>（难在哪里）</small></h3><p>看过示范后立即答对，可能只是照着步骤模仿；先做再学的提升，也可能只是比另一组多练了一次。更难的是，两种顺序可能让模型探索到不同的<strong>正确解题路径</strong>，而当前分数却差不多。只比较一次做题正确率，无法判断模型有没有在后续更新中真正学会、是否丢掉了原有的解法。</p></div>
 <div class="idea-step"><h3>现有工作 <small>（别人研究了什么）</small></h3><p><a href="https://doi.org/10.3102/00346543211019105" target="_blank" rel="noopener noreferrer"><b>Sinha &amp; Kapur（2021）</b></a> 汇总 53 项人类教育研究，发现某些概念知识和迁移任务中“先解题后教学”有优势，但程序性知识未显示同样的总体差异；<a href="https://ijcai.org/proceedings/2015/614" target="_blank" rel="noopener noreferrer"><b>Najar 等（2015）</b></a> 已研究按学生状态选择示范或练习；<a href="https://doi.org/10.1007/s10648-025-09993-3" target="_blank" rel="noopener noreferrer"><b>He 等（2025）</b></a> 还观察到不同人群的顺序优势可能相反。<strong>我们不是首次比较教学顺序</strong>，而是研究 LLM 经过相同预算的持久更新后，独立解题能力、可采样的正确解法和多轮迁移如何受顺序影响。</p></div>
 <div class="idea-step"><h3>Insight <small>（为何可解）</small></h3><p>两组都能看到同一份正确示范，但<strong>先试的人在看到答案前，已经走过自己的候选路径</strong>；先看的人可能更快掌握标准步骤，却可能更依赖示范。这两种影响不能靠眼前一道题判断。只改变学习先后，撤掉教师和临时上下文后再测新题，就能判断顺序究竟改变了独立能力，还是只改变了即时模仿。</p></div>
 <div class="idea-step"><h3>Design <small>（如何做）</small></h3><p>在同一个模型检查点、同一组题目上随机分成两支：<strong>A 先看示范再练习，B 先独立尝试再看相同示范</strong>。控制示范内容、尝试次数、采样配置、教师调用、训练 token 和 LoRA/Skill 更新步数。更新完清空示范上下文，在未见题上独立测试。只有先证明不同任务或模型阶段的最佳顺序确实会变化，才考虑用先前历史训练顺序选择器。</p>
 <div class="flow"><div><b>同一检查点分两组</b><small>教师、题目、预算一致</small></div><div><b>只交换先后次序</b><small>先学再做 / 先做再学</small></div><div><b>撤掉示范独立考试</b><small>新题正确率与正确解法</small></div><div><b>多轮更新后复测</b><small>顺序优势是否改变</small></div></div></div>
 <div class="idea-step"><h3>实验设计 <small>（怎么验证）</small></h3><p>先选一类多步骤数学题，比较<strong>固定先学、固定先试、匹配次数的额外练习、无示范基线</strong>；后续只有在发现稳定顺序异质性时，才增加按历史能力选择和 contextual bandit 对照。用同预算的无提示 pass@1、固定 k 下的 pass@k、<strong>不同且正确的解法数量</strong>、旧能力保持及跨多轮更新的迁移作为指标。按知识点聚类统计，不按同题多次采样扩大样本量。如果优势只是练习次数更多或无效答案更多，就不能说顺序提高了探索与自我改进。</p><p class="idea-side-note"><b>正交边界：</b>I7 只改变<strong>尝试与示范的顺序</strong>；<a href="#idea-6">I6</a> 在顺序固定时选择哪条失败过程，<a href="#idea-8">I8</a> 在纠错方式固定时研究哪类错误有跨题迁移价值。<a href="idea-i7-learning-order.html">查看人类教学的前作边界、两顺序协议与长期对照 →</a></p></div>
 </div>

## I1–I8：八个研究问题 / I8：错误学习迁移——为什么改正一种错误能学会一类题？


 <div class="idea-focus"><span class="idea-axis">信号对不对</span><span class="idea-axis">吸收了会不会丢</span><span class="idea-axis">安全</span><p><b>一句话：</b>两个模型都把一道积分题做错。一个看完正确答案只会重做原题；另一个却学会同一公式，连几十道新题也能做。<strong>纠正哪个错误更可能举一反三？能否在真正训练前判断？</strong></p></div>
 <div class="idea-steps">
 <div class="idea-step"><h3>Challenge <small>（难在哪里）</small></h3><p>模型很自信地答错，不代表它缺的知识少，也不代表纠正后进步一定大。<strong>当前题答对、同模板变体答对、真正掌握一条规则</strong>是不同的结果。每个错题都完整训练一遍才能知道收益，成本太高；直接按难度、置信度或损失排序，又可能选中只会记住答案、却不会迁移的错误。</p></div>
 <div class="idea-step"><h3>现有工作 <small>（别人研究了什么）</small></h3><p><b>Hypercorrection</b> 与 <b>Nature Communications 2018</b> 的人类学习研究发现，已有信念与可信反馈的冲突可能影响纠错记忆，但不等于 LLM 已能跨题学习。<b>Self-Error-Instruct</b> 已按模型错误类型生成并筛选训练数据；<b>LESS</b> 和 <b>DATAPROPHET</b> 已研究训练前预测数据价值；<b>RULE-EDIT</b> 已区分规则文本修复与实例迁移。我们研究的是<strong>这个模型当前犯的某个错误，在固定纠错预算后究竟能让多少未见同规则题变好</strong>，而不是首次使用错题或首次预测训练价值。<a class="cite" href="references.html#E12" title="Errors committed with high confidence are hypercorrected">[E12]</a><a class="cite" href="references.html#E18" title="Knowledge acquisition is governed by striatal prediction errors">[E18]</a><a class="cite" href="references.html#S40" title="Self-Error-Instruct: Generalizing from Errors for LLMs Mathematical Reasoning">[S40]</a><a class="cite" href="references.html#M10" title="LESS: Selecting Influential Data for Targeted Instruction Tuning">[M10]</a><a class="cite" href="references.html#M13" title="Demystifying Supervision Data Generalization in Multimodal LMs (DATAPROPHET)">[M13]</a><a class="cite" href="references.html#S41" title="RULE-EDIT: Benchmarking Rule-Level Knowledge Editing in Large Language Models">[S41]</a></p></div>
 <div class="idea-step"><h3>Insight <small>（为何可解）</small></h3><p>一个错误有多值得纠正，至少可能受三个条件影响：<strong>模型是否已有理解正确规则的基础、这条错误规则影响多少道不同题、当前更新方式能否真正改变规则的使用</strong>。例如，遗漏同一积分公式分母的模型可能只差关键一步；但若连基本运算都不会，直接给公式未必能被吸收。置信度或强烈的“原来我错了”可以作为候选信号，不能直接等于真实学习收益。</p></div>
 <div class="idea-step"><h3>Design <small>（如何做）</small></h3><p>先用独立前置知识题、同规则变体和稳定性探针，诊断<strong>知识准备、规则影响范围与更新兼容性</strong>；正确答案与规则由独立验证器核实。然后从相同模型检查点分叉，用相同教师反馈与固定 LoRA/Skill 更新预算纠正不同错误。训练前估计可能的跨题收益，训练后撤掉例题与提示，分别测原题、异结构同规则新题、其他规则和旧能力损失。</p>
 <div class="flow"><div><b>确认错误与规则</b><small>先核实反馈正确</small></div><div><b>学习前诊断</b><small>前置知识 / 规则范围</small></div><div><b>固定预算纠错</b><small>同教师、同更新器</small></div><div><b>独立测跨题净收益</b><small>新题迁移 / 遗忘 / 成本</small></div></div></div>
 <div class="idea-step"><h3>实验设计 <small>（怎么验证）</small></h3><p>构造<strong>前置知识高/低 × 错误规则影响范围大/小</strong>的配对数学错题，匹配难度、置信度、正确反馈和训练预算；每个候选从同一模型快照独立更新。比较<strong>随机、最难优先、高置信度优先、稳定错误优先、Self-Error-Instruct 的 one-shot 信号、LESS 梯度信号、DATAPROPHET 式价值特征、I8 的规则诊断</strong>。主指标是训练前预测与真实未见题净增益的对应关系，以及同预算选错题的最终收益；另外报告旧能力退化和诊断成本。如果优势只出现在原题、近似改写，或在匹配知识状态后消失，就不能宣称发现了规则级迁移机制。</p><p class="idea-side-note"><b>正交边界：</b>I8 固定纠错方式，只研究<strong>哪个错误规则在当前模型上更有迁移价值</strong>；<a href="#idea-6">I6</a> 在同题同错误终点比较失败中间过程，<a href="#idea-7">I7</a> 只改教学顺序。<a href="i8.html">查看 Hypercorrection 原始证据、最近邻矩阵和完整受控实验 →</a>。目前<strong>没有 I8 的实际训练结果</strong>。</p></div>
 </div>

## I1–I8：八个研究问题 / I6、I7 与 I8：一次只研究一个变量


<div class="table-wrap"><table><thead><tr><th>Idea</th><th>改变什么</th><th>固定什么</th><th>决定性结果</th></tr></thead><tbody>
<tr><td><a href="idea-i6-failure-value.html">I6 · 失败轨迹价值</a></td><td>同题失败过程</td><td>模型检查点、错误终点、正确反馈、学习顺序、预算</td><td>不同轨迹产生的后续独立学习增益</td></tr>
<tr><td><a href="idea-i7-learning-order.html">I7 · 学习顺序</a></td><td>先尝试 / 先看正确示范</td><td>题目、示范内容、更新器与预算</td><td>撤掉教师后的独立能力、有效探索与多轮迁移</td></tr>
<tr><td><a href="i8.html">I8 · 规则级错误迁移</a></td><td>知识准备、错误规则覆盖范围和更新兼容性</td><td>对应的纠错/更新方法</td><td>哪些错误修复后能迁移到一整类题</td></tr>
</tbody></table></div>
<p><b>不要混成一篇：</b>I6 的核心证据是“相同错误终点，不同失败过程”；I8 的核心证据是“错误知识状态与跨题规则”的关系。I7 不以 I6/I8 的分类结果作为必需前提。旧版<a href="idea-i6.html">跨轮瓶颈切换方案</a>仅作为历史草案保留，不再占用当前 I6 编号。</p>


## I1–I8：八个研究问题 / 这些 Idea 如何证明真的用于 RSI？


 <div class="table-wrap"><table><thead><tr><th>需要分开报告</th><th>最简单的检验办法</th></tr></thead><tbody>
 <tr><td>当前任务变好</td><td>协助、提示或多次尝试后的即时成功率；这是短期表现。</td></tr>
 <tr><td>我自己真的学会</td><td>只保留允许写入的 Skill / Memory / Harness / 权重；撤除教师、伙伴和临时上下文，在新任务上测独立能力。</td></tr>
 <tr><td>我越来越会学习</td><td>保留学到的“选帮助、选学法、选复习、选试验、选伙伴”策略，给新的学习者与新任务，测同预算下是否学得更快。</td></tr>
 </tbody></table></div>
 <p><b>共同对照：</b>同一学习器起点、相同训练/执行预算、固定外部验证器；报告新任务进步、旧任务保持、训练成本和多轮曲线。普通重试、固定规则、随机选择、通用 bandit 是必要基线。任务选择、训练数据和最终测试必须隔离。</p>
 <p><b>安全边界：</b>所有自修改先在受控沙箱中提议、测试、回滚；真实系统权限不随学习成功自动升级。Skill/Memory 写入保存来源与适用条件，拒绝把不稳定、污染或越权的经验固化。这里是协议要求，不是已完成的安全验证。</p>
 <p class="status">截至 2026-10-27：这些是有明确近邻的研究提案，不能声称“首次把教育学用于 RSI”；也不能因为已有相关组件，就断言上述更细化的问题已被解决。</p>


## I2：因材施教的师生共进化——学生变强，教师也更会教 / 核心问题：学生在变强，教师能否越来越会教？


<p class="thesis"><b>I2：</b>同一个学生，早期可能需要补全关键步骤，后来可能只需要指出错误前提。教师能否从过去“怎样教、学生后来真正学会了什么”的经验中改进教学，并随着学生的成长持续调整？</p>
<p>例如，学生最初不会设置二重积分的积分边界，教师给出分步解释；学生掌握基础后，逐步展开可能只是在重复旧知识，比较两个相似区域的差别反而更有帮助。这个顺序只是<b>待验证例子</b>，不预设弱学生必须看示范、强学生必须自主探索。</p>
<div class="card-grid"><article class="research-card"><b>学生学会解题</b><h3>把知识写入自己的能力</h3><p>真实更新参数或版本化任务 Skill。清空课堂对话、撤掉教师后，在新题和后续轮次上独立进步。</p></article><article class="research-card"><b>教师学会教学</b><h3>把教学经验写入自己的教法</h3><p>真实更新教学策略、教学 Skill 或教学 LoRA。对同一批冻结学生，后期教师比早期教师带来更高的独立学习增益。</p></article></div>
<div class="note"><b>合并而不是另起编号：</b>保留原 I2 的“同样犯错，最合适的学法可能不同”与小预算试学；把试学结果进一步用于<b>教师自身的持久更新</b>。不再只是固定教师帮学生选一次学习方法。</div>


## I2：因材施教的师生共进化——学生变强，教师也更会教 / Bayesian Teaching 提供的启发：正确答案不等于好的教学目标


<p><b>论文实际做了什么：</b>Qiu 等的 <i>Bayesian teaching enables probabilistic reasoning in large language models</i>（Nature Communications，2026）让模型模仿根据当前证据更新判断的 Bayesian Assistant，并与始终给出正确选项的 Oracle 比较；在所测推荐任务中，Bayesian 教学更有效，并展示跨任务迁移。<a class="cite" href="references.html#S100" title="Bayesian teaching enables probabilistic reasoning in large language models">[S100]</a></p>
<p><b>可以迁移的洞察：</b>教学监督要对应学生未来能执行的判断，而不能仅由教师答案正确率来评价。Oracle 利用真实偏好给出正确选项，未必示范如何从有限证据逐步判断。</p>
<p><b>不能扩大成的结论：</b>该论文训练的是学生去模仿预测行为，不是训练一个持续进化的 LLM 教师，也没有证明必须传递显式思维链；它不主张故意给错答案、更弱教师永远更好，或禁止教师使用额外信息。I2 将其作为教学目标的启发，不把它当作师生共进化已经有效的证据。</p>


## I2：因材施教的师生共进化——学生变强，教师也更会教 / Challenge：两边分数都涨，还不能证明教师更会教


<p><b>第一，学生变了，教法的效果也可能变。</b>同一错误标签不能说明已有子技能、可理解的解释和最有效的练习方式。旧反馈可能不再代表当前学生的真实学习反应。</p>
<p><b>第二，教师评价存在混淆。</b>学生因训练而变强，本来就更容易答对；不能把教师后来面对更强学生时的课堂成功率，当成教师教学能力提高。</p>
<p><b>第三，当场听懂不等于学会。</b>教师话语、标准答案甚至学生自己的课堂笔记留在上下文中，都可能改善眼前表现，但不一定转化为持久能力。</p>
<p><b>第四，试教也花计算。</b>真实更新学生副本才知道哪种教法有效，但多分支会增加训练成本。每次诊断、候选教学、学生更新和独立后测都要计费，不能只比较学生主分支的步数。</p>


## I2：因材施教的师生共进化——学生变强，教师也更会教 / Insight：学习反应会变化，而真实反馈能教会教师如何跟上


<p class="thesis"><b>待检验关系：</b>随着学生获得新能力，教学方式的收益排序可能改变；教师若持续利用当前学生更新后的独立学习增益，就可能学会跟随这种变化，而不仅是反复输出更正确的答案。</p>
<p>“因材施教”在这里不是让教师给学生贴一个静态标签，而是用真实经历更新判断：<b>什么状态的学生，接受什么解释或练习后，能够在新问题上独立进步。</b>原 I2 的试学用于获得这种证据，教师的持久更新用于把一次经验转成以后可复用的教法。</p>
<p>这条关系可能不成立：若固定教法已经足够，或固定教师仅凭当前学生描述就能同样好地调整，就没有证据说明必须持续训练教师。实验要允许这些结果，而不是预设共进化一定获胜。</p>


## I2：因材施教的师生共进化——学生变强，教师也更会教 / 最近邻：共同进化已经存在，I2 需要多证明哪一步？


<p><b>历史起点：</b><i>Learning to Teach</i>（ICLR 2018）已明确用学生反馈优化教师策略，提出师生共进化。因此“教师和学生都更新”不是新的研究主张。<a class="cite" href="references.html#M100" title="Learning to Teach">[M100]</a> 下表区分论文实际更新什么、反馈来自哪里，以及 I2 的决定性对照。</p>
<div class="table-wrap"><table><thead><tr><th>Closest work</th><th>已有机制与共同点</th><th>I2 的具体差别</th><th>为什么重要 / 必需证据</th></tr></thead><tbody>
<tr><td><b>RLT</b>，2025 <a class="cite" href="references.html#S101" title="Reinforcement Learning Teachers of Test Time Scaling (RLT)">[S101]</a></td><td>教师看到题目和答案，学习产生适合学生的解释；以学生对解释/答案的概率等信号训练教师，再蒸馏学生。</td><td>原文明确未探索两者并行训练；I2 持续保留学生成长，并以真实更新后的新题收益修订教法。</td><td>比较固定 RLT 教师、持续条件化但不更新的教师与持续更新教师，不能只胜过通用 Prompt。</td></tr>
<tr><td><b>SCAS</b>，2026 预印本 <a class="cite" href="references.html#S102" title="The Strongest Teacher Is Not Always the Best Teacher: Student-Centric Answer Selection (SCAS)">[S102]</a></td><td>在已经核实正确的教师答案中，依据学生相关的学习成本代理选择监督。</td><td>I2 不只从固定答案池选答案，而是更新教学策略；主要反馈是持久学习收益。</td><td>与学生感知的答案选择和相同代理奖励比较，检验真实反馈是否有增量信息。此处只记录已核对预印本，不沿用未核实的会议标签。</td></tr>
<tr><td><b>Sherpa</b>，2026-10 预印本 <a class="cite" href="references.html#S103" title="Sherpa: Teaching LLMs to Teach Adaptively">[S103]</a></td><td>多轮 RL 训练教师适应不同模拟学生；学生骨干冻结，收益由教学后的上下文表现定义。</td><td>I2 学生必须真实持久更新，下一轮需求由学习自然改变，不靠预设学习偏好标签。</td><td>把同样的教学接口接到可更新学生上，验证课堂收益与独立更新后收益是否不同。</td></tr>
<tr><td><b>Eduardo / Assistance Dilemma</b>，2026-10 <a class="cite" href="references.html#S19" title="The Assistance Dilemma: Learning to Teach via Multi-Turn Reinforcement Learning">[S19]</a></td><td>遮蔽教师话语，在新变体上后测；冻结学生，保留学生自己的课堂话语。</td><td>I2 主要后测清空双方临时对话，只保留允许的学习产物。</td><td>分别报告原文的“只留学生笔记”后测与无课堂笔记的持久学习测试，不把两种目标混用。</td></tr>
<tr><td><b>SOAR</b>，ICML 2026 <a class="cite" href="references.html#S17" title="Teaching Models to Teach Themselves: Reasoning at the Edge of Learnability (SOAR)">[S17]</a><a class="cite" href="references.html#S47" title="Teaching Models to Teach Themselves: Reasoning at the Edge of Learnability (SOAR)">[S47]</a></td><td>教师生成练习题；真实训练学生，以困难题上的增益更新教师；算法也会提升学生检查点。已经包含双边更新。</td><td>I2 首先固定题目与答案，研究怎样表达、解释与纠错，而不是主要研究出什么题。</td><td>保留 SOAR 式真实学习奖励作为强基线；固定课程，比较是否使用当前学生状态/历史反应。不能声称首次用学习增益训练教师。</td></tr>
<tr><td><b>OPCoD</b>，2026 <a class="cite" href="references.html#S33" title="Be My Tutor: On-Policy Co-Distillation for Mutual LLM Improvement via Peer Feedback (OPCoD)">[S33]</a></td><td>互补模型轮流互教，双方参数持续更新；依据认知状态门控反馈并锚定问题。</td><td>I2 单独用受教者的学习增益更新教师教学能力，不把教师自身答题变强等同于更会教。</td><td>比较只更新解题能力的互教，与显式更新教学策略的方案；对同一冻结学生库交叉评估教师版本。</td></tr>
<tr><td><b>Pedagogical RL</b>，作者研究报告 2026-05 <a class="cite" href="references.html#S104" title="Pedagogical RL: Teaching Models to Teach Themselves from Privileged Information">[S104]</a></td><td>特权信息辅助教师生成正确且学生较易吸收的轨迹，随后以 surprisal-gated imitation 更新学生。</td><td>I2 研究持续教学经验是否能追踪变化中的学生，以及代理可学性与真实跨题增益是否一致。</td><td>同监督源、同成本比较概率代理与真实学习反馈；该来源是作者报告，不标作已发表会议论文。</td></tr>
<tr><td><b>Bayesian Teaching</b>，Nature Communications 2026 <a class="cite" href="references.html#S100" title="Bayesian teaching enables probabilistic reasoning in large language models">[S100]</a></td><td>监督学生模仿证据条件下的规范预测行为，展示策略迁移。</td><td>I2 的教师策略本身可更新，目标是对当前学生产生可持续学习收益。</td><td>作为“结果正确性不是唯一教学质量指标”的证据，不作为共同进化的直接基线。</td></tr>
</tbody></table></div>
<p><b>保留原 I2 的边界：</b>RSIFlow 研究改模型、Harness 还是任务产物；MetaSkill-Evolve 研究任务与元技能的共同改进。I2 固定更新对象与更新器，不再同时做更新表面路由。<a class="cite" href="references.html#S28" title="RSIFlow: Adaptive Self-Improvement Workflows with an Evolving Meta-Agent">[S28]</a><a class="cite" href="references.html#S06" title="MetaSkill-Evolve: Recursive Self-Improvement of LLM Agents via Two-Timescale Meta-Skill Evolution">[S06]</a></p>
<p><b>范围判断：</b>“学生状态—教法—实际学习收益”的跨轮变化，以及教师能否从中学出可迁移的教学能力，是本方案要验证的关系。表中多项组件已有直接前作，不能仅把它们拼起来就宣称新的机制。</p>


## I2：因材施教的师生共进化——学生变强，教师也更会教 / Design：教一轮、真学习、独立测，再更新教法


<div class="flow"><div><b>保存师生版本</b><small>教师 T_t 与学生 S_t</small></div><div><b>固定教材试教</b><small>同题、同答案、不同表达</small></div><div><b>学生真实更新</b><small>固定训练器 / Skill 写入器</small></div><div><b>撤辅独立测试</b><small>新题收益与旧能力保持</small></div><div><b>教师改进教法</b><small>保留经验，面对 S_(t+1)</small></div></div>
<h3>1. 固定配对和教学材料，隔离“怎样教”</h3>
<p>第一阶段只用一个教师与一个持续成长的学生；不同学生起点作为独立重复，而非动态换伴。所有对照共享题目流、参考答案、题目难度和教师可用知识。固定“先完成统一诊断尝试 → 教师反馈 → 学生更新”的顺序，不优化 I7 的先后顺序。</p>
<h3>2. 先用三种可检查的教学形式</h3>
<p>同一知识点生成<b>分步解释、关键反例对比、针对错误步骤的引导修正</b>。这三种形式只是启动实验的候选，不是三个声称新颖的模块。教师读取学生历史与诊断证据，学习如何组织当前反馈；不得读取最终测试答案。</p>
<h3>3. 原 I2 的小预算试学，变成教师的经验来源</h3>
<p>从同一个 S_t 快照复制配对分支，使用不同教学内容、相同学生更新步数与随机种子集合。清空课堂上下文，在另一个开发题集测收益。只在可信差异下形成“哪种教法更好”的反馈；差异小于噪声时保留为不确定，不强行选冠军。</p>
<h3>4. 教师与学生分别保留不同的学习产物</h3>
<p><b>Skill 验证轨道：</b>继承原 I2 的固定任务 Skill 写入器；学生更新任务 Skill，教师更新有长度上限的教学 Skill。冻结底座、编辑器与权限，测的是系统层持久学习，不称权重增长。<b>参数验证轨道：</b>教师教学 LoRA 与学生解题 LoRA 分开保存，学生更新规则固定；教师可先用配对教学收益形成偏好更新，再比较 RL。两条轨道分别报告，不把载体切换收益归功于因材施教。</p>
<p><b>跨轮闭环：</b>保留 S_(t+1) 的真实更新，教师保留 T_(t+1) 的教学更新；下一轮针对已经变化的学生重新教学。每个测量窗口内冻结教师和学生起点，窗口结束后再交替更新，避免把同时漂移的两个变量混在一次因果比较里。</p>
<div class="note">教师在主实验中不增加新的教材或答案权限，以便隔离教学经验的作用；它的自身解题能力作为辅助指标记录。允许后续研究知识与教法共同增长，但不把它塞入首篇 I2。</div>


## I2：因材施教的师生共进化——学生变强，教师也更会教 / 教师的奖励：不是把眼前题讲对，而是学生以后自己会做


<div class="equation">S'_t(a) = U(S_t, Teach(T_t, x, history_t; a); B_S)</div>
<p>U 是每组相同的学生更新器，a 表示教学候选。教师反馈在<b>真实更新后</b>计算，而不是用学生点头、复述答案或当前题解出与否替代。</p>
<div class="equation">G_t(a) = Acc_ind(S'_t(a), D_meta) − Acc_ind(S_t, D_meta)<br>R_T(a) = G_t(a) − λ · Regression_old(a) − μ · Cost(a)</div>
<p>D_meta 是用于教师学习的开发集，不是最终未见测试集。能力回归按旧任务独立评估；成本包括诊断、教师生成、学生分支训练、教师更新与后测。λ、μ 与预算在开发阶段固定，同时分开报告原始收益、回归和花费，不只报告一个合成分数。</p>
<p>同一 S_t 的候选教法可以相互作为配对基线。跨阶段比较时，优先增加一个固定教学策略的同起点分支，避免学生自然变强导致教师获得虚高奖励。最终测试族和教师交叉评估学生库不进入教师训练。</p>


## I2：因材施教的师生共进化——学生变强，教师也更会教 / 决定性实验：分开证明学生会做、教师会教、两者需要共同更新


<h3>E1 · 学生变强后，原来的最佳教法真的会改变吗？</h3>
<p>保存同一学生在早、中、后三个真实学习阶段的快照。固定知识点、教师参考知识与训练预算，随机分叉三种教学形式，估计各自新题学习增益。比较错误标签/当前正确率、普通 contextual bandit、少量试学响应和学生感知答案选择，检验是否存在可重复的教法排序变化。没有变化也要保留，不能只展示发生反转的题。</p>
<h3>E2 · 教师越来越会教，还是学生越来越好教？</h3>
<p><b>教师版本 × 冻结学生快照的交叉评估。</b>让早期教师 T_0、后期教师 T_k 分别教同一个 S_0、同一个 S_k，以及训练中从未见过的学生快照。每一格重新复制该学生、实施同量教学与更新，比较它在未知题上的增益。若 T_k 只在和自己一起长大的 S_k 上有效，只能说明局部适配；在新学生/新任务上也改善，才支持教学能力的迁移。</p>
<div class="equation">TeachingGain(T, S) = Acc_ind(U(S, Teach(T); B), D_audit) − Acc_ind(S, D_audit)</div>
<p>不能比较 T_0 教弱学生的绝对分数与 T_k 教强学生的绝对分数。也不能把某个单一静态学生上的教法提升自动称为普遍教学能力提高。</p>
<h3>E3 · 持续改进教师，是否优于静态教师已有的自适应能力？</h3>
<div class="table-wrap"><table><thead><tr><th>对照</th><th>教师是否持久更新</th><th>学生是否持续更新</th><th>区分什么</th></tr></thead><tbody>
<tr><td>固定教材 / 固定教法</td><td>否</td><td>是</td><td>普通训练已经带来的进步</td></tr>
<tr><td>固定教师 + 当前学生状态</td><td>否，但可用当前历史生成不同反馈</td><td>是</td><td>只靠上下文适应，是否已足够</td></tr>
<tr><td>教师学习，但反馈来自固定初始学生库</td><td>是</td><td>是</td><td>通用教学能力提升能否替代跟随当前学生</td></tr>
<tr><td>I2：当前学生真实学习收益驱动教师更新</td><td>是</td><td>是</td><td>成长中学生与持续变化教法的闭环</td></tr>
</tbody></table></div>
<p>另做两项消融：<b>把真实学习增益换成当场成功率/概率代理</b>；<b>打乱同预算试教的学生—反馈对应关系</b>。加入真实学习奖励相同但不读取当前学生状态的教师，以及普通 bandit、RLT 风格解释、SCAS 监督筛选。SOAR 原版课程生成与 OPCoD 互教单列为相邻强基线；若为固定教材做适配，明确标注改动，不把适配结果冒充原论文复现。</p>
<h3>最小验证规模与数据隔离</h3>
<p>先用一对师生和 4 个知识点检查管线；再扩到 12 个任务族、2 个学生能力快照、3 种教法、3 个更新重复，共 216 个学生试学分支（计划数，不是结果）。连续学习先运行 6 轮，逐轮保存师生快照；出现稳定现象后，再扩跨模型和更多任务。</p>
<p>数据按题目模板与知识点家族拆分为教学、诊断、教师奖励、版本选择和最终审计；教师奖励集会被训练利用，不能称未见测试。教师升级不以最终测试成绩作奖励。主指标是未知题独立学习曲线、旧能力保持和固定学生库上的教师教学增益；全部分支与教师训练费用计入预算，同时报告匹配学生更新次数和匹配总算力两个视角。</p>


## I2：因材施教的师生共进化——学生变强，教师也更会教 / I2 与 I5–I8 的边界，以及什么结果足以支持论文


<div class="table-wrap"><table><thead><tr><th>方向</th><th>研究变量</th><th>I2 中如何处理</th></tr></thead><tbody>
<tr><td><b>I2 · 师生共同学习</b></td><td>当前学生真实学习反馈如何改变教师教法</td><td>固定配对与任务，教师教学策略和学生能力分别持久更新</td></tr>
<tr><td><a href="idea-i5.html">I5 · 动态伙伴</a></td><td>跟谁学、什么时候交换伙伴</td><td>不换教师；跨学生测试只是独立验证，不学习配对网络</td></tr>
<tr><td><a href="idea-i6-failure-value.html">I6 · 失败学习价值</a></td><td>哪些失败轨迹值得投入学习</td><td>错误材料按统一协议固定，不同时优化失败选择</td></tr>
<tr><td><a href="idea-i7-learning-order.html">I7 · 学习顺序</a></td><td>先尝试还是先看示范</td><td>首轮固定教学顺序，不将顺序选择当成 I2 贡献</td></tr>
<tr><td><a href="i8.html">I8 · 规则级迁移</a></td><td>哪类错误知识状态更可迁移</td><td>迁移作为结果测量，不重做错误机制分类</td></tr>
</tbody></table></div>
<p><b>支持继续：</b>真实学生成长伴随稳定的教学收益变化；后期教师在固定学生交叉评估中更有效；闭环优于可看当前状态的固定教师、固定学生库训练教师及相同奖励的通用策略，并能排除更多预算和答案泄漏。</p>
<p><b>缩小主张：</b>只有共同成长的一对师生受益，报告配对内适应；没有跨学生提升就不称通用教学能力。如果静态条件化教师同样有效，则保留学习响应现象，不宣称教师持久更新必不可少。</p>
<p><b>定位：</b>双边更新本身是已有方法。I2 希望解释和利用的是<b>学生学习反应的变化，以及教师如何从这种变化中学会更有效的教法</b>。需要新的受控证据，而不是“两个 Agent + 双层优化”的命名。</p>
<p class="status">研究方案已合并；本页所有预期关系、实验规模与策略均为待验证提案，没有宣称本项目已获得共进化收益。</p>
<div class="links"><a class="link-btn" href="ideas.html#idea-2">返回 I2 摘要</a><a class="link-btn" href="experiments.html#i2-coevolution">I2 实验执行入口</a><a class="link-btn" href="references.html">文献与核验记录</a></div>


## I5：十模型互教——什么时候换舞伴，才能一起变强？ / I5：谁能让我学得更快、更好，何时该换舞伴？


<p class="thesis"><b>核心问题：</b>十个能力和专长不同的模型持续互教、各自更新。<strong>一个伙伴是否合适，不仅取决于它比我强多少，还取决于它会的东西我是否学得进、之前与谁学过，以及继续交流还有多少新增收益。</strong>我们研究配对对象、关系持续时间和接触顺序，不把十个聊天角色或多数投票当成共进化。</p><p>例如 A 先向 B 学到一种基础分解方法，之后才可能吸收 C 的复杂证明。直接先找最强的 C 未必有效；A 已掌握 B 的方法后，继续留在原配对又可能重复。<b>这是待验证的机制例子，不是已经观察到的模型结果。</b></p><p>主线保持为<strong>十模型动态互教</strong>：每个模型拥有独立的持久状态；正常一轮五对，双方先独立作答，再交换受检验的反馈、各自更新、撤伴复测。暂不适合互教的成员保留同预算自学选项，不强制有害配对。人类轮换同伴/Jigsaw 只提供组织启发。<a class="cite" href="references.html#E97" title="Effects of the Jigsaw method on student educational outcomes: systematic review and meta-analyses">[E97]</a></p><div class="links"><a class="link-btn" href="#collisions">最接近的 LLM 前作</a><a class="link-btn" href="#design">一轮具体怎么做</a><a class="link-btn" href="#gain">怎么测真实学习收益</a><a class="link-btn" href="i5-method-protocol.json" download>下载方法与实验契约 JSON</a></div><p class="status">版本 2026-10-27 · 文献核验与方法设计；尚未执行本项目多模型训练，不展示推测成绩。</p>


## I5：十模型互教——什么时候换舞伴，才能一起变强？ / Challenge：强、互补、能教会，是三个不同条件


<p><b>第一，知识不同不等于可以传过去。</b>模型可能拥有对方缺失的解法，却无法把它变成对方的持久能力。Off-Trajectory Reasoning 区分了接受正确引导和从错误引导中恢复，说明独立推理水平不能替代协作可用性；它研究推理轨迹利用，不能据此断言所有训练迁移都会失败。<a class="cite" href="references.html#S204" title="Off-Trajectory Reasoning: Can LLMs Collaborate on Reasoning Trajectories?">[S204]</a></p><p><b>第二，学完涨分不等于伙伴带来的收益。</b>同一模型用同样算力自己练，也可能涨分。必须从同一检查点分叉，与同数据/更新预算的自学比较；双方都要分别测，不能只算较弱者。</p><p><b>第三，配对收益会变化。</b>我和伙伴都在更新，旧的最优配对记录会过时；同一条边反复访问还可能只传播重复内容。新伙伴带来新颖材料，是否能帮助独立新题，仍须真实学习验证。</p><p><b>第四，交流顺序的效果可能只是普通课程顺序。</b>先 B 后 C 比反过来好，不足以证明双向共进化；模型训练本来就可能受数据顺序影响。必须控制冻结老师、相同材料和普通课程重排。</p><p><b>第五，群体平均分不能掩盖退化。</b>平均进步可能由少数强模型贡献；文本更不同也不等于技能更多。需要每个模型的独立曲线、旧能力回归、可验证技能覆盖和误差相关性。R-Diverse 的技能层面去重可作为测量启发，不作为我们的新模块。<a class="cite" href="references.html#S205" title="R-Diverse: Mitigating Diversity Illusion in Self-Play LLM Training">[S205]</a></p>


## I5：十模型互教——什么时候换舞伴，才能一起变强？ / 现有工作：继承什么，I5 必须额外证明什么？


<p>下表将学习者是否持久更新、交换对象和选择信号分开。论文原始机制、我们的适配方式和待验证差异不能混写；这不是穷尽性的多 Agent 综述。</p><div class="table-wrap"><table><thead><tr><th>最近邻 / 核验状态</th><th>别人研究的机制</th><th>I5 的继承与决定性差异</th></tr></thead><tbody><tr><td><b>CORY</b> · NeurIPS 2024 主会 <a class="cite" href="references.html#S200" title="Coevolving with the Other You: Fine-Tuning LLM with Sequential Cooperative Multi-Agent Reinforcement Learning (CORY)">[S200]</a></td><td>复制出 Pioneer/Observer 两个模型，协同 RL，并周期性交换角色。</td><td>双模型共同训练和角色互换已有前作；I5 固定每对内部角色协议，只改变多伙伴配对与关系持续时间。</td></tr><tr><td><b>PopuLoRA</b> · arXiv 2026.05 <a class="cite" href="references.html#S32" title="PopuLoRA: Co-Evolving LLM Populations for Reasoning Self-Play">[S32]</a></td><td>教师/学生 LoRA 群体出题解题，能力匹配与交叉评估，带权重空间进化。</td><td>继承低成本独立适配器与群体对照思想；I5 不把“多人共进化”当首创，主实验不做权重遗传。必须证明独立学习收益比难度/胜率更能指导互教配对。</td></tr><tr><td><b>OPCoD / Be My Tutor</b> · arXiv 2026.06 <a class="cite" href="references.html#S33" title="Be My Tutor: On-Policy Co-Distillation for Mutual LLM Improvement via Peer Feedback (OPCoD)">[S33]</a></td><td>互补的两个学生通过受门控的反馈进行 on-policy 自蒸馏；以自身正确 rollout 和同伴反馈构造 self-teacher 条件。</td><td>它是固定互教底座和固定双人基线；I5 额外研究十模型的配对、持续时间与接触历史。不能把双向学习、反馈门控、双方改善当首次。</td></tr><tr><td><b>LLM Partner Selection</b> · AAMAS 2026 SE Workshop <a class="cite" href="references.html#S201" title="LLM Agents Learn Effective Partner Selection for Mutual Cooperation in Social Dilemmas">[S201]</a></td><td>社会困境中的伙伴选择与合作，存在动态关系网络研究。<a href="https://sites.google.com/view/se-aamas2026/accepted-papers" target="_blank" rel="noopener noreferrer">官方 Workshop 录用名单</a>。</td><td><strong>纠正此前主会表述：</strong>不是 AAMAS 主会论文。目标是合作收益，不是撤除伙伴后的知识习得；正文网页本次受访问限制，网络规模/参数共享与精确重连频率不补写为已核实事实。</td></tr><tr><td><b>CERA-MoA</b> · arXiv 2026.09 <a class="cite" href="references.html#S202" title="CERA-MoA: Co-Evolving Routing Mechanisms with Continually Learning LLM Agents">[S202]</a></td><td>动态任务路由器与独立 Agent 策略共同更新；隐藏状态熟悉度用于样本分发与能力分化。</td><td>“路由与模型共同进化”已有直接前作；I5 选择的是两个学习者的关系，反馈是更新后相对自学的净增益。需要当前表现路由与同容量净收益预测器正面对照。</td></tr><tr><td><b>GENOME / GENOME+</b> · ACL 2026 <a class="cite" href="references.html#S203" title="Nature-Inspired Population-Based Evolution of Large Language Models (GENOME / GENOME+)">[S203]</a></td><td>以权重交叉、变异、选择和继承演化模型群体，不依赖梯度来完成其进化步骤。</td><td>群体人数和能力组合不是创新。I5 通过可审计的教学和各自训练积累能力，不生成替代子代；系统级比较不能与纯配对消融混为一谈。</td></tr><tr><td><b>HACE</b> · arXiv 2026.10 <a class="cite" href="references.html#S90" title="Heterogeneous Agentic Coevolution (HACE)">[S90]</a></td><td>专用基础模型和 LLM Agent 双向更新，并演化交换信息与训练经验的 Harness。</td><td>异构相互改进已存在；I5 固定 Harness 和更新算法，检验多人关系序列带来的增量。</td></tr></tbody></table></div><p><b>两篇约束方法设计的证据：</b>Off-Trajectory Reasoning（ICLR 2026）提醒我们先检验可引导性与恢复性，而不是假设更强伙伴的推理必然可用；R-Diverse 提醒我们按真实技能而非措辞测多样性。本次只确认 R-Diverse 的 arXiv 版本，不沿用未经本次核实的 ICML 标签。<a class="cite" href="references.html#S204" title="Off-Trajectory Reasoning: Can LLMs Collaborate on Reasoning Trajectories?">[S204]</a><a class="cite" href="references.html#S205" title="R-Diverse: Mitigating Diversity Illusion in Self-Play LLM Training">[S205]</a></p><p>此前收录的 <b>MACE</b> 保留在伙伴探索的近邻中；本次原始页面访问受限，未重新核验其详细算法/结果，不把“即时协作收益”的适配基线冒称官方复现。<a class="cite" href="references.html#S34" title="Multi-Agent LLMs Fail to Explore Each Other (MACE: Multi-Agent Contextual Exploration)">[S34]</a></p><div class="note"><b>本轮最重要的文献结论：</b>研究空间不是“有十个模型就新”，而是<strong>伙伴选择为什么需要考虑可吸收性、已传播知识和更新后的真实学习收益，以及哪些顺序效果不能被普通课程解释</strong>。这些仍是待检验差异，不是已经证明的首次性。</div>


## I5：十模型互教——什么时候换舞伴，才能一起变强？ / Insight：选择可吸收的新知识，而不是选择一个固定排名的老师


<p class="thesis"><b>待检验判断：</b>伙伴价值取决于<strong>对方拥有而我缺少的技能 × 我当前能吸收它的程度 × 它是否已通过其他伙伴传播给我</strong>。三个因素不是预设的乘法定律，而是要分别操作和检验的解释变量。</p><p>我们把伙伴关系看成<strong>有方向、随版本变化的学习机会</strong>：A 从 B 获益不要求 B 从 A 获益同样多；现在合适也不保证三轮后合适。最便宜的观测是技能正确率与已接触材料记录；决定性标签仍来自更新后相对自学的增量。</p><p>与 PopuLoRA 的题目难度匹配、OPCoD 的反馈接收门控、CERA-MoA 的任务分发相比，I5 将<strong>双方未来独立学习收益</strong>作为配对反馈，并单独检验关系持续时间和历史顺序是否有额外价值。现有组件组合不自动产生新颖性，必须用等预算控制建立这一因果差异。<a class="cite" href="references.html#S32" title="PopuLoRA: Co-Evolving LLM Populations for Reasoning Self-Play">[S32]</a><a class="cite" href="references.html#S33" title="Be My Tutor: On-Policy Co-Distillation for Mutual LLM Improvement via Peer Feedback (OPCoD)">[S33]</a><a class="cite" href="references.html#S202" title="CERA-MoA: Co-Evolving Routing Mechanisms with Continually Learning LLM Agents">[S202]</a></p>


## I5：十模型互教——什么时候换舞伴，才能一起变强？ / Design：固定互教更新器，只改变伙伴关系


<div class="flow"><div><b>冻结本轮快照</b><small>十模型各自参数与优化器</small></div><div><b>匹配五对</b><small>互补性、可吸收性、历史</small></div><div><b>双向反馈与更新</b><small>固定教学协议和 LoRA 更新器</small></div><div><b>撤伴独立测试</b><small>相对同预算自学的净增益</small></div><div><b>继续或重配</b><small>不确定性、预算、回归共同决定</small></div></div><h3>互教底座：借用 OPCoD，而不是重新发明蒸馏</h3><p>采用 <b>OPCoD 式、按 LoRA 适配的 on-policy 自蒸馏</b>作为首版固定实现。原工作用学习者自身正确 rollout 和同伴反馈作为 self-teacher 的条件；我们将同一更新器用于所有配对策略，不把跨规模数学/代码适配的效果当作原论文结论。原文主要是双模型 Science Q&amp;A，十模型和跨规模属于本项目待测扩展。<a class="cite" href="references.html#S33" title="Be My Tutor: On-Policy Co-Distillation for Mutual LLM Improvement via Peer Feedback (OPCoD)">[S33]</a></p><p><b>一步一步：</b>① 每个模型从预先锁定的训练任务流独立采样；② 配对伙伴先通过题目/技能检查，再对对方的尝试给有限长度反馈；③ 学习者用自己的轮初快照、可用的自有正确轨迹和同伴反馈形成带辅助的 self-teacher 分布；④ 对无辅助 student 做固定自蒸馏更新，两个方向分别执行；⑤ 清空对话、伙伴与临时上下文，在严格隔离的未见任务上独立测量。每个学习块结束后双方的新状态才成为下一块教师，避免更新顺序造成隐含优势。</p><p>伙伴之间只交换文本反馈，不交换 logits、权重或优化器状态；self-distillation 的分布比较在同一学习者内部进行，避免跨词表对齐。强者不必永远当老师，每条配对都评估两个方向。</p><h3>正确反馈的边界</h3><p>有一条正确答案，不等于解释每一步正确；题面出现某概念也不是事实证明。题目、测试、答案校验器固定，代码在隔离环境执行；记录反馈导致“原本正确→错误”的 break-rate，拒绝明显污染/泄漏内容。没有可信反馈时按冻结规则退回自学，保留失败记录，不临时引入额外强教师。门控策略在所有基线中相同，不能把改门控的收益算作换伴收益。<a class="cite" href="references.html#S33" title="Be My Tutor: On-Policy Co-Distillation for Mutual LLM Improvement via Peer Feedback (OPCoD)">[S33]</a></p><h3>模型池：保留十个不同规模/专长模型的主线</h3><p>主实验沿用 <b>Qwen3-1.7B / 4B / 8B / 14B / 32B × 数学、代码两类专长 = 10 个独立学习者</b>。专长由互不重叠的训练切分形成，领域分数实测，不把参数量当智力。正式运行固定 checkpoint revision、思考模式和 tokenizer；这些是可用模型规格，不是最新模型推荐。<a class="cite" href="references.html#B200" title="Qwen3: Think Deeper, Act Faster — official dense-model release">[B200]</a></p><p>先用 4B/8B × 两专长做四模型验证；另加同规模十个独立 LoRA 对照，区分规模差距与知识差异。共享冻结底座可节约资源，但 LoRA、优化器、数据历史必须独立。无需十模型同时驻留显存；相同轮初快照下可以顺序执行五对，计入总算力、显存峰值和运行时间。首版不做权重交叉或成员替换，避免与 GENOME/PopuLoRA 的遗传算子混淆。<a class="cite" href="references.html#S203" title="Nature-Inspired Population-Based Evolution of Large Language Models (GENOME / GENOME+)">[S203]</a><a class="cite" href="references.html#S32" title="PopuLoRA: Co-Evolving LLM Populations for Reasoning Self-Play">[S32]</a></p>


## I5：十模型互教——什么时候换舞伴，才能一起变强？ / 收益标签：比同样预算自己练，多学会了多少？


<p>对冻结状态 sᵢ，Uᵢ⟵ⱼ 表示与伙伴 j 学习一个固定块，Uᵢ⟵∅ 表示相同数据与更新步数的无伙伴自蒸馏。A 是撤除帮助后的开发集独立准确率，按任务族预先等权；Tʰ 是相同的 h 个后续干扰学习块。</p><div class="equation">Gᵢ⟵ⱼ(h) = A[Tʰ(Uᵢ⟵ⱼ(sᵢ))] − A[Tʰ(Uᵢ⟵∅(sᵢ))]</div><p><b>h=0</b> 看立即学会；<b>h=2</b> 暂作预注册候选，经过相同的两块后续学习再测保持。用相同初态、数据切分、更新预算与尽可能配对的随机种子；后续干扰任务一致，不把墙上经过几小时当成模型遗忘。以上 h 是方案参数，不是文献最优值。</p><p>分开报告两个自学基线：<b>等更新量</b>（隔离同伴信息作用）和<b>等总计算量</b>（把省下的交流算力用于更多自学，检验实际效率）。G 不能用训练前后差、当次合作正确率或教师自评替代。两分支用同一开发题成对比较，置信区间按独立任务族与随机种子聚类，不能把同题的多条 rollout 当成独立样本。</p><h3>如何避免诊断比训练还贵？</h3><p>四模型阶段枚举 6 个无向配对、分别记录 12 个方向；同起点的 solo 对照可在协议一致时复用。十模型正式阶段不在每轮把 45 条边全部试训：先做三轮低成本平衡探索，仅在候选边不确定、旧估计明显过时或抽样审计时克隆小分支。<strong>所有探测、回退分支、延迟标签和候选排序的算力均计入总预算。</strong>首版探测上限设为 10%，仅在开发集比较 5%/10%/20% 后冻结，不能运行中为方法额外加预算。</p><p>非探测轮的边收益只是预测值，不是已观察的因果效应；记录是否测过、距上次测量的版本差、估计区间和反馈缺失。未选边不能按零收益训练预测器，未知边靠有预算的随机探索补证据。最终测试集从不生成配对标签。</p>


## I5：十模型互教——什么时候换舞伴，才能一起变强？ / 换伴规则：保留收益、探索未知、避免追逐噪声


<h3>先得到有方向的能力与学习记录</h3><p>每个模型维护经过验证的技能成功率、自己的弱项、近期独立学习增益、旧能力保持；每条方向边记录互补技能覆盖、接受反馈后的修复/破坏比例、真正试学增益、已交换材料的来源标识以及两个模型的版本。相似解法的文字差异不计为新技能；不把不同错误强行保留下来作为“多样性”。</p><h3>首版控制器：历史感知收益预测 + 一般图匹配</h3><p>使用小型上下文收益预测器估计 Gᵢ⟵ⱼ 和 Gⱼ⟵ᵢ；输入中包含双方能力、知识互补、近期曝光和配对历史，保留模型版本差以降低旧证据权重。对同一组固定实现同时比较：只看当前能力的预测器、去掉历史的同容量预测器、包含历史的预测器。所用 bandit、回归和匹配都是基础工具，不声称这些工具新颖。</p><div class="equation">M* = argmaxₘ Σ{ i,j }∈M [Ĝᵢ⟵ⱼ + Ĝⱼ⟵ᵢ + 探索项] − κ × 改变配对的成本<br>约束：每个成员至多一个伙伴；总计算 ≤ 剩余预算；回归与安全门通过</div><p>十节点完全图有 945 种完整配对，可直接枚举匹配分数；这是便宜的调度计算，不需要让模型生成 945 次答案。正常组成五对；若可信增益不足或安全门不通过，允许未匹配成员执行同预算 solo。各成员获得相同的预注册学习机会，另设最低探索覆盖；不能只让强者一直获得资源。</p><h3>什么时候换？</h3><p>沿用既有方案的候选范围：<strong>至少学习 20 个优化步，每 10 步检查一次，到 80 步必须重新评估</strong>；80 步不是强制换人。如果新匹配相对继续当前匹配的优势，扣除切换成本后仍超过成对估计的不确定性边界，才更换；连续两个检查点确认是首版防抖规则，明确作为待调参数。若所有边同样不确定，用预算内探索而不是 LLM 自述理由拍板。</p><p>初版用滚动数据/近期权重应对模型能力变化，并检验“固定边表”“每轮只看即时分数”“历史感知净增益”三者。上置信界用于受约束探索，不代表安全保证；对旧任务退化和验证器异常使用独立门控，必要时回滚。无法可靠估计长期收益时先保留可检验现象，不预设一定需要复杂序列规划器。</p>


## I5：十模型互教——什么时候换舞伴，才能一起变强？ / 实验：从四模型可传性，到十模型持续共进化


<div class="table-wrap"><table><thead><tr><th>实验</th><th>唯一主要变化</th><th>必须排除的替代解释</th></tr></thead><tbody><tr><td><b>E0 · 互教能否真正传过去</b></td><td>四模型 6 配对，双向更新；同版本 peer / solo / 无更新对照</td><td>只是多生成答案或保留提示。即时帮助和真实训练后新题能力分别报告。</td></tr><tr><td><b>E1 · 学习收益能否预测配对</b></td><td>规模与专长交叉，同能力差距下比较实际 G</td><td>“找大模型”或“相同题目多练”已解释全部收益；同规模十模型和匿名伙伴 ID 作控制。</td></tr><tr><td><b>E2 · 留伴多久、何时换</b></td><td>固定块长 vs 边际收益触发；其余互教更新完全一致</td><td>多检查、多训练或额外接触更强模型。包括检查开销，分别做等曝光与等总计算比较。</td></tr><tr><td><b>E3 · 接触顺序是否有独立价值</b></td><td>固定伙伴集合、各边次数与材料预算，比较 A←B→C 与 A←C→B</td><td>普通数据课程顺序。加入相同材料包重排、冻结教师、实时双向更新三层对照。</td></tr><tr><td><b>E4 · 十模型长期增长</b></td><td>相同十模型起点，只变配对/时机/历史信息</td><td>群体更多算力、只有弱者受益、协作投票冒充独立能力、文本多样性冒充技能增长。</td></tr></tbody></table></div><h3>E3 为什么需要三层对照？</h3><p>先冻结 B/C、提前固定教学材料，只改变材料顺序，测一般课程效应；再保持教师冻结、允许反馈依学习者当前错误而变；最后让双方持续更新。三组都锁定接触图、学习步数、任务与种子。只有后两层相对材料重排提供额外效果，并且该效果可预测下一次配对收益，才支持“动态学习关系”解释。不存在这个增量也应如实保留结果，不能把所有非交换性都称作共进化。</p><h3>主要基线与对齐层次</h3><p><b>调度器直接对照：</b>固定五对、随机换伴、9 轮 round-robin（45 对全部覆盖）、能力匹配、知识互补匹配、即时合作收益、无历史净增益、历史感知净增益。它们共享同一更新器、任务流和反馈门控。固定最强老师的星形方案不满足一对一伙伴约束，应单列为系统级等成本对照，不能与五对方案假装结构完全一致。</p><p><b>论文适配基线：</b>OPCoD 固定双人互教；PopuLoRA 风格的难度/能力匹配；CERA-MoA/MACE 风格的当前能力或合作收益选伴。仅借用匹配信号时标为“受启发的适配基线”，不能冒称完整复现原算法；完整系统复现另列轨道，因为题目生成、样本分发、权重遗传都改变了变量。<a class="cite" href="references.html#S32" title="PopuLoRA: Co-Evolving LLM Populations for Reasoning Self-Play">[S32]</a><a class="cite" href="references.html#S33" title="Be My Tutor: On-Policy Co-Distillation for Mutual LLM Improvement via Peer Feedback (OPCoD)">[S33]</a><a class="cite" href="references.html#S202" title="CERA-MoA: Co-Evolving Routing Mechanisms with Continually Learning LLM Agents">[S202]</a><a class="cite" href="references.html#S34" title="Multi-Agent LLMs Fail to Explore Each Other (MACE: Multi-Agent Contextual Exploration)">[S34]</a></p><h3>消融和统计</h3><p>去掉伙伴反馈、打乱增益标签、移除历史、冻结一方、用即时奖励代替延迟独立增益；保留相同可用预算。四模型探索至少 3 个种子，十模型确认目标为 5 个；报告置信区间，资源不足时说明实际分母而非用更多测试题伪造训练重复。核心估计单位是独立训练种子与任务族。</p>


## I5：十模型互教——什么时候换舞伴，才能一起变强？ / 独立评测、预算与可否证的结论


<p><b>四种数据严格分开：</b>train 用于能力更新；probe-dev 产生配对收益；meta-valid 只用于冻结策略超参数；最终 test 只在预定检查点由隔离评测器运行，不把成绩或答案返给调度器。数学按问题/模板族拆分，代码按题源与测试家族拆分；来源和派生关系可追踪，不能只做字符串去重。</p><p><b>主指标：</b>每模型固定推理预算下的独立 pass@1；全班平均增益随累计训练 FLOPs 的曲线及曲线面积；最弱成员/下四分位的增益；原专长回归和每个模型的改进人数。不能仅由平均分上升声称 Pareto 改善，应对所有成员做预注册非劣界与不确定性报告。</p><p><b>新知识与同质化：</b>统计经验证的技能覆盖、错误相关性和跨专长组合题的独立迁移。所谓“新发现”只表示在预先锁定采样预算 K 下，原群体未采到、更新后采到的有效解；有限采样不能证明原来绝对不会。R-Diverse 提醒我们区分表面题型变化与技能重复。<a class="cite" href="references.html#S205" title="R-Diverse: Mitigating Diversity Illusion in Self-Play LLM Training">[S205]</a></p><p><b>成本：</b>分别记生成 token、教师反馈、前向/反向估算 FLOPs、试训分支、验证调用和墙钟时间。PopuLoRA 的 4T+4S 设置按每适配器匹配训练量；其报告的约 1.31× 墙钟不能外推成“八个模型只用 1.31× 总算力”，更不能套给五种大小的十模型。主表必须有整个群体的总预算控制。<a class="cite" href="references.html#S32" title="PopuLoRA: Co-Evolving LLM Populations for Reasoning Self-Play">[S32]</a></p><h3>什么证据支持 I5？</h3><p><b>支持：</b>真实学习后的边收益随状态变化；历史信息在同容量、同预算预测器中改善决策；换伴机制在自然任务上提高多个成员的独立增长，且保留旧能力。<b>收缩解释：</b>如果固定最强者、round-robin 或无历史 bandit 已解释全部收益，保留观察，不夸大新调度机制。<b>定位问题：</b>如果 E0 不传，不据此放弃十模型目标；先检查反馈正确性、能力差距与固定更新器兼容性，修复互教底座后，再重新做所有配对策略的公平比较。</p><p><b>安全边界：</b>成员之间无凭据与系统权限共享；反馈视为不可信数据；验证器不与模型共同训练；沙箱禁外网/敏感文件；模型或 LoRA 写入按版本记录且可回滚。网站发布不是授权启动 GPU 实验。</p>


## I5：十模型互教——什么时候换舞伴，才能一起变强？ / 与其他 Idea 解耦：I5 只输出伙伴和接触计划


<div class="table-wrap"><table><thead><tr><th>其他研究问题</th><th>I5 的固定边界</th></tr></thead><tbody><tr><td>I1：内化、外查与撤辅</td><td>主实验固定 LoRA 为持久更新面；不让 I5 同时学习存储/检索策略。</td></tr><tr><td>I2：同类失败适合什么学法</td><td>所有调度基线使用同一 OPCoD 式教学和更新器。换更新器只能另做正交复核。</td></tr><tr><td>I3：新旧能力冲突与巩固</td><td>重放比例、回归阈值与回滚固定；I5 不发明新的遗忘修复算法。</td></tr><tr><td>I4：单次失败继续试验还是总结</td><td>每个任务的重试、反馈和停止协议相同；I5 决定伙伴关系的持续时间，而不是题内搜索。</td></tr><tr><td>I6：失败轨迹价值与重访</td><td>主实验固定每模型的训练任务流与轨迹取样，不让伙伴控制哪些错题被训练。</td></tr><tr><td>I7：先尝试还是先示范</td><td>配对内部统一先独立作答再反馈；I5 的顺序变量是跨伙伴 B→C，而不是教学内部先试/先学。</td></tr><tr><td>I8：纠正哪些错误能迁移</td><td>错误选择规则与更新器不变，只看不同伙伴/关系历史的增量。</td></tr></tbody></table></div><p><b>接口：</b>输入为各成员版本、技能结果、历史接触、预算与候选边；输出为五对关系（或少量 solo）、每对允许持续的学习块、重评时机和选择依据。I5 不修改测试答案、工具权限或教师规则。<a href="ideas.html">返回 I1–I8 总览</a>。</p>


## I5：十模型互教——什么时候换舞伴，才能一起变强？ / Related Work：Nature 系列已经发现了哪些群体机制？



 <div class="table-wrap"><table><thead><tr><th>论文</th><th>别人研究的是……</th><th>对 I5 的可验证启发</th></tr></thead><tbody>
 <tr><td><b>Bridge ties bind collective memories</b>，Nature Communications 2019 <a class="cite" href="references.html#E90" title="Bridge ties bind collective memories">[E90]</a></td><td>16 人网络、每人 4 次依次与不同伙伴交流；控制交流次数，只变更先跨组还是先组内。</td><td>配对的<strong>时间顺序</strong>可能影响知识先扩散还是先巩固；但它测的是群体记忆，主群体收敛差异统计上较边缘，不能直接证明模型训练有效。</td></tr>
 <tr><td><b>Clustering knowledge and dispersing abilities</b>，Nature Communications 2019 <a class="cite" href="references.html#E91" title="Clustering knowledge and dispersing abilities enhances collective problem solving in a network">[E91]</a></td><td>在群体求解的计算模型中分别改变知识与能力在网络上的分布。</td><td><strong>能力差距</strong>与<strong>专长互补</strong>要分开建模，参数规模不是学习互补性的代理。</td></tr>
 <tr><td><b>Modularity and composite diversity</b>，Nature Communications 2021 <a class="cite" href="references.html#E92" title="Modularity and composite diversity affect the collective gathering of information online">[E92]</a></td><td>真实在线信息检索/预测实验，研究成员多样性、分组模块化和群体规模的交互。</td><td>既不能让信息长期困在小圈子，也不应假设全连接最好；要监测误差相关性和独立收益。</td></tr>
 <tr><td><b>Propagation and preservation of AI-discovered strategies</b>，Nature Communications 2026 <a class="cite" href="references.html#E93" title="Propagation and preservation of AI-discovered problem-solving strategies in human culture">[E93]</a></td><td>多代人类/AI 实验，按表现选上一代示范者，检验超出原学习者发现范围的策略能否被学习、传播和保留。</td><td>好老师不只要“会”，还要能传；但论文不是<strong>同一代十个持续更新模型的双向配对</strong>。</td></tr>
 <tr><td><b>Feature-based reward learning shapes human social learning</b>，Nature Human Behaviour 2025 <a class="cite" href="references.html#E94" title="Feature-based reward learning shapes human social learning strategies">[E94]</a></td><td>6 项实验、1,941 人，表明社会学习策略可以随历史收益而调整。</td><td>不必写死“找最强/找相似的人”，可从自身真正的学习收益更新选伴规则。</td></tr>
 <tr><td><b>Copy or collaborate?</b>，npj Complexity 2025 <a class="cite" href="references.html#E95" title="Copy or collaborate? How networks impact collective problem solving">[E95]</a></td><td>计算模型将模仿强者与组合专长合作分开；群体平均表现与最优解探索存在不同收益。</td><td>配对不应只传播现成答案，还要留出发现新解法的机会；“先协作后复制”是强基线而不是我们的首创。</td></tr>
 <tr><td><b>Payoff selectivity drives collective intelligence</b>，Nature Communications 2026 <a class="cite" href="references.html#E96" title="Payoff selectivity drives collective intelligence during dynamic resource tracking in humans">[E96]</a></td><td>621 人动态资源追踪实验中，能看到他人收益时，群体更容易适应性调整信息流。</td><td>伙伴筛选应观察可信的收益信号，但该论文评估的是合作表现，并未证实权重更新后的独立学习。</td></tr>
 </tbody></table></div>
 <p>这些工作共同提示三个变量：<strong>接触谁、先后顺序、信息在群体中如何传播</strong>。NC 并没有直接给出“十模型长程参数共进化”的现成算法；以上是可迁移的机制证据，而不是 I5 的实验证明。</p>



## I5：十模型互教——什么时候换舞伴，才能一起变强？ / I5 的历史研究支线：教别人能否发现自己的盲点？



 <p><b>为什么放在同一个 I5 下？</b>前面的十模型互教是当前主线，研究<strong>和谁学、何时交换伙伴</strong>。此前还有一个相邻问题：Agent 教另一个 Agent 时，学生的追问或误用，能否帮教师发现自己本来没发现的知识缺口？两者都从“以教促学”出发，但<strong>研究变量、更新对象和主要实验不同</strong>，不作为两个并列的 I5。</p>
 <div class="table-wrap"><table><thead><tr><th>同属 I5 的研究记录</th><th>要回答的问题</th><th>独立验证</th></tr></thead><tbody>
 <tr><td><strong>当前主线：十模型动态互教</strong></td><td>随着双方能力变化，下一轮跟谁学、何时换伴最有效？</td><td>撤除伙伴后各模型的独立能力增益、群体学习曲线</td></tr>
 <tr><td>历史支线：教学反馈诊断</td><td>学生的错误和追问，能否暴露教师自己原本没有意识到的知识缺口？</td><td>教师从学生反馈更新前后的独立任务表现，与同预算自测比较</td></tr>
 </tbody></table></div>
 <p>我们保留这份早期技术方案与原始实验契约，方便以后回溯，但不再把它单独放在左侧研究方向菜单。<a href="teaching.html">查看历史支线的完整方法和实验设计</a>。</p>



## I5：十模型互教——什么时候换舞伴，才能一起变强？ / 一句话和最有说服力的结果


<p class="thesis"><strong>我们不只问谁更强，而是问：他掌握的东西我现在能不能学会；学过以后这段关系是否还值得继续；换一个伙伴是否能带来自己练得不到的新能力。</strong></p><p>因此首版方法固定双向自蒸馏，通过同预算自学对照获得有方向的净学习收益，用带历史的轻量预测器决定配对和换伴；最终用四模型配对、冻结教师/固定材料顺序、十模型长期增长三层证据，判断动态关系本身有没有价值。真正需要展示的是独立学习曲线和可迁移技能，不是十模型一起答题的高分。</p><p><b>当前状态：</b>本轮完成原始文献复核、方法与实验契约；未启动训练。<a href="i5-method-protocol.json" download>下载协议</a> · <a href="#teaching-feedback">历史教学反馈支线</a> · <a href="ideas.html#idea-5">Idea 摘要</a>。</p>


## I6 · 为什么有些错误更值得学习？ / 一句话科学问题


<p class="thesis"><b>I6：</b>同一模型面对同一道题，甚至最终给出相同的错误答案，却可能经历不同的失败过程。为什么使用其中一条失败轨迹纠错，比使用另一条更能帮助模型在后续独立解题时进步？</p>
<p><b>发现 E 并入 I6：</b>当同一道题反复失败时，下一条失败轨迹是否还值得收集？如果预计新增失败的学习价值已小于成本，是否应该停止当前尝试、把预算用在别的错题上，或者暂缓后再回来？<strong>停止当前题 ≠ 永远放弃这道题</strong>。</p>
<p>这里的“学习”必须对应可持续的参数或外置技能更新，之后撤掉原题答案与教师提示再测新题；单次纠错后能复述答案不算学会。</p>
<div class="note"><b>研究边界：</b>核心因果实验只改变提供给固定学习器的<b>失败轨迹</b>，固定教学顺序、反馈形式、示范信息、更新器和训练预算。新增的停止实验仅决定<b>是否继续收集当前题的错误、改用另一题的错误，或暂缓重访</b>，不自行选择教学方法。<a href="idea-i7-learning-order.html">I7</a> 才研究“先看示范还是先自主尝试”；<a href="idea-i6.html">旧版跨轮瓶颈路由</a>作为历史草案单独保留。</div>


## I6 · 为什么有些错误更值得学习？ / 一个可观察的现象


<div class="card-grid"><article class="research-card"><b>轨迹 A · 直接猜错</b><h3>没有形成有效中间过程</h3><p>模型面对一道多元积分题，直接套用错误公式，给出错误结果。</p></article><article class="research-card"><b>轨迹 B · 尝试后答错</b><h3>形成部分有效步骤</h3><p>同一模型在同题上尝试坐标变换、检查边界，却最终仍得到相同的错误结果。</p></article></div>
<p>两条轨迹从同一个模型检查点产生，问题与最终答案都一致。假设分别用它们作为学习材料，且获得<b>相同正确解法与等预算更新</b>，模型在新积分题上的收益仍可能不同。这是<b>待验证现象</b>，并不是断言 B 一定优于 A。</p>
<p><b>再进一步：</b>如果模型已经反复产出同一种错误过程，继续在这道题上重采样可能只得到更多相似失败；另一个暂时不会做的题，反而可能提供一种更容易学会的新规则。<strong>两道题都没进展，并不代表下一条失败轨迹有同样的学习价值。</strong>这也是 I6 中“何时停止当前学习”需要验证的现象。</p>
<p><b>与 I8 不同：</b><a href="i8.html">I8</a> 以高置信度错误、前置知识与规则适用范围为切口，解释什么错误规则经纠正后能够跨题迁移；I6 则尽量固定题目和错误结果，只比较<b>不同失败过程本身</b>作为纠错材料的增量学习收益。高置信度与规则范围不作为 I6 的主要处理变量。</p>


## I6 · 为什么有些错误更值得学习？ / 先解释原因，再定义模块


<div class="table-wrap"><table><thead><tr><th>Challenge · 难在哪里</th><th>Insight · 为什么可能解决</th><th>Design · 如何验证</th></tr></thead><tbody>
<tr><td>当前正确率只能告诉我们“没做对”，不能告诉我们一次纠错将改变多少未来能力。</td><td>错误过程可能暴露已具备的子步骤、错误的知识规则以及缺口与其他题的共享程度。</td><td>先随机抽取失败轨迹，采用固定纠错程序逐条更新；再用未见题的独立增益为每条失败定价。</td></tr>
<tr><td>失败轨迹越长、越接近答案、越自信，可能只是更耗 token 或原本更接近正确。</td><td>学习价值应由更新后的因果收益定义，不能由“表面离正确答案多远”替代。</td><td>匹配题目、初始检查点、错误长度、教师反馈、更新步数与评测；增加错误严重度、置信度、语义相似度强基线。</td></tr>
<tr><td>纠正同一道题不代表学会同一规则，更不代表跨任务迁移。</td><td>某条轨迹可改写只针对原题的模式，也可能揭示跨题共用的推理规则。</td><td>把原题重做、同模板新题、结构变形题和旧能力回归分开统计，并评估多个后续更新之后是否保持。</td></tr>
</tbody></table></div>
<p><b>方法只放最必要的部分：</b>先用标准化纠错更新建立每条失败的实际学习价值，再训练一个轻量 Failure Value Estimator。预测器只能读取<b>纠错前</b>的轨迹特征与历史，不得偷看纠错答案或最终后测。停止机制只复用它的收益估计和不确定性，不另外训练一个负责选择教学法的大型 Router。</p>


## I6 · 为什么有些错误更值得学习？ / 最小辨别实验：同题、同反馈、不同错误


<div class="flow"><div><b>冻结学习者版本</b><small>同模型与参数检查点</small></div><div><b>同题采集失败轨迹</b><small>多种随机种子，先核实均错误</small></div><div><b>固定纠错更新</b><small>同一个教师答案 / LoRA 配置</small></div><div><b>无提示后测</b><small>新题迁移、旧能力回归</small></div><div><b>学习价值分析</b><small>解释差异与事前预测</small></div></div>
<p><b>P0：</b>先选一个数学任务族及一组跨题共享规则，收集同一检查点在同一道题上的多条自然失败轨迹。随机指定某条失败轨迹为学习材料；另一分支只读正确解法作基线。每个分支从<b>同一初始检查点</b>重新开始，而不是顺序累积训练。</p>
<p><b>配对控制：</b>优先匹配同一目标题、同一错误终点与已知错误规则，只让失败轨迹的中间过程不同；固定教师正确解法、训练器、token 上限、学习率、更新步数和测试集，并对轨迹长度/额外解释文本做预算敏感性分析。保留“只看答案”“随机失败”“按置信度选错误”“按答案距离选错误”等对照。</p>
<p><b>定义：</b>G(f)=Acc_after(f, D_holdout) − Acc_before(D_holdout)，并同时报告相对于“只看正确解法”的增量；D_holdout 按知识点与模板去重。分层估计同题组内的学习收益差，不把一题上的多个 Probe 当成独立样本。</p>
<p><b>下一步：</b>用不同题/不同模型上的纠错前轨迹预测 G(f)，比较随机选错误、按难度/置信度/长度选错误与收益预测选择；报告预算相同时的迁移增益和选择 regret。</p>


## I6 · 为什么有些错误更值得学习？ / 发现 E · 何时停止当前错误的学习，何时重新回来？


<p><b>Challenge｜难在哪里？</b>模型连续做错同一道题，并不说明再来一次毫无价值。也许下一条失败轨迹会暴露新的推理缺口；也许模型已经反复犯同一种错，继续采样只会浪费预算。更难的是，<b>现在学不动，不代表补充知识或模型版本改变后依旧学不动</b>。</p>
<p><b>Insight｜可以比较什么？</b>I6 已经要预测“纠正一条失败轨迹，能够让未来的独立能力提高多少”。顺着这个指标，进一步比较：<b>继续收集这道题的新失败</b>，与<b>纠正手头已有错误</b>、<b>换另一道题的错误</b>，哪个给下一轮带来的净学习收益更高？当新增轨迹的边际收益变小，而其他失败更值得学时，就应该停止当前题的尝试。这里的目标是学习价值，不是最低当前解题时间。</p>
<div class="table-wrap"><table><thead><tr><th>可选行动</th><th>为什么这样做</th><th>必须检查的风险</th></tr></thead><tbody>
<tr><td><b>继续尝试当前题</b></td><td>预计再得到一条不同失败后，按固定纠错程序学习，仍有新增迁移收益。</td><td>不能把更长轨迹、更多采样或当前题 pass@k 上升算成独立能力提升。</td></tr>
<tr><td><b>纠正已有错误</b></td><td>当前已经收集到高价值失败，再采样的边际价值不如直接开始固定更新。</td><td>纠错答案、更新器与教学顺序固定，预测器不许偷看正确答案。</td></tr>
<tr><td><b>换其他错题</b></td><td>另一个待学失败在相同学习成本下预计贡献更大的跨题增益。</td><td>不能把换成了更强教师、更简单训练器算作选择收益。</td></tr>
<tr><td><b>暂缓并重访</b></td><td>目前没有值得继续投入的失败轨迹，但前置能力或下一版模型可能改变它的可学习性。</td><td>事前写明重访条件，不根据独立终测结果决定何时回来。</td></tr>
<tr><td><b>结束本轮投入</b></td><td>题目已掌握，或在既定预算内所有可选失败的预计收益都不足。</td><td>严格区分“已掌握”“当前不值得学”和“还无法判断”，不能声称永远学不会。</td></tr>
</tbody></table></div>
<p><b>Design｜怎样实施？</b>沿用 I6 的 Failure Value Estimator，记录当前失败池、已有失败的预计纠错增益、再次采样可能获得的新轨迹价值、其他待学错误的机会成本，以及实际 token / 更新 FLOPs。选择<strong>预计独立净收益</strong>最高的行动；在估计不可靠时保留探索份额，防止把稀有但高价值的错误过早排除。所有 Probe、额外轨迹、纠错更新和重访都算入总预算。</p>
<div class="flow"><div><b>同题失败池</b><small>同版模型，记录新失败是否真的提供不同信息</small></div><div><b>预估学习增益</b><small>固定纠错后，新题独立表现将改变多少</small></div><div><b>比较下一次投入</b><small>继续收集 / 纠正已有 / 换错题 / 暂缓</small></div><div><b>按条件重访</b><small>前置能力变强、模型版本更新或预定复测点</small></div><div><b>真实更新后验收</b><small>撤辅助、未见题迁移与旧能力保持</small></div></div>
<p>暂缓的错误进入 <b>Deferred Failure Queue</b>，附原模型版本、估计收益区间和重访条件。<b>重访不一定更有效</b>：同一个错误在新模型上可能已经掌握，也可能变得更难学，必须重新测可学习性，而不能沿用旧分数。</p>
<p><b>学习科学启发，而非既有 RSI 结论。</b>Metcalfe 与 Kornell（2005）的 Region of Proximal Learning 区分选择学习材料与决定学习多久，用 jROL（对学习速率的判断）解释停止当前材料。<a class="cite" href="references.html#E16" title="A Region of Proximal Learning model of study time allocation">[E16]</a> MetaCLASS（EMNLP 2026）在教学动作预测里观察到：41.7% 的标注轮次无需干预，最佳模型预测“不干预”却只有 6.6%。<a class="cite" href="references.html#E17" title="MetaCLASS: Metacognitive Coaching for Learning with Adaptive Self-regulation Support">[E17]</a> 两者分别来自人类学习和教学决策，<b>不能直接证明 LLM 停学有效</b>；I6 必须用真实更新后的独立迁移来验证。</p>
<p class="note"><b>不扩写成大而全的策略路由：</b>I6 的新增选择对象是<b>哪条失败轨迹值得继续投入</b>，不是换哪一种训练算法。固定纠错方法的局部选法属于 I2；<a href="idea-i7-learning-order.html">I7</a> 研究尝试与示范的先后；<a href="i8.html">I8</a> 研究错误规则与知识准备对迁移的作用。</p>


## I6 · 为什么有些错误更值得学习？ / E2 · 继续、停止、暂缓与重访的辨别实验


<p><b>先验证现象。</b>选同一道题上反复产生失败的冻结模型状态，记录各次新增轨迹；从同一 checkpoint 分叉，把每一条轨迹单独送入同一个纠错程序。测新增轨迹的实际跨题独立收益，看看“同样连续答错”，下一条失败的学习价值是否有可重复差异。以题目/规则簇作为统计单位，不把一次题目的几十条采样当几十个独立任务。</p>
<p><b>再验证停止决策。</b>固定同一个可用错误池与计算预算，比较：固定采样 K 次、随机挑错误、近期正确率或 jROL 式学习速率阈值、学习进展课程选择、I6 的失败价值预测 + 停止决策。把<strong>不允许停止/暂缓</strong>作为消融；将实际纠错后的最佳行动只作为事后 oracle 上界，不能提前交给策略。</p>
<p><b>最后验证重访。</b>将当轮预计低收益的困难题随机分为“持续采集失败”“离开且不返回”“暂缓、在前置能力/检查点发生预定义变化后重访”。先固定重访触发条件与后续任务流，再用未见题测净收益，避免按测试答案挑时机。只有出现重访后明显增益，才能说“暂停比继续死磕更好”；否则只支持任务切换而不支持重访。</p>
<p><b>统一结果：</b>未来未见题的撤辅增益 / 总计算成本、旧能力回归、过早停止率、错过可恢复失败的比例，以及重访的增量收益。教师答案、训练器、示范顺序、更新步数都固定；探索阶段可记录不同长度，但评测须有严格等 token / FLOPs 对照。</p>


## I6 · 为什么有些错误更值得学习？ / 最近邻：做到了哪里、我们还要回答什么


<div class="table-wrap"><table><thead><tr><th>相关工作</th><th>已研究的关系</th><th>I6 的独立问题</th></tr></thead><tbody>
<tr><td><a href="i8.html">I8：高置信度错误与规则级迁移</a></td><td>针对错误的知识准备程度、规则覆盖范围以及持久更新后的跨题净收益。</td><td>固定题目与错误终点，仅研究<b>失败轨迹过程</b>是否提供额外有用信息。</td></tr>
<tr><td><a href="https://aclanthology.org/2024.acl-long.45/" target="_blank" rel="noopener noreferrer">Learn from Failure · ACL 2024</a></td><td>形式定理证明中，失败搜索轨迹可成为有价值的训练数据。</td><td>不是证明失败“可以用”，而是研究<b>哪条失败更值得用</b>。</td></tr>
<tr><td><a href="https://arxiv.org/abs/2610.13594" target="_blank" rel="noopener noreferrer">MENTOR: Learning from Failure with On-Policy Pedagogical Intervention · 2026 预印本</a></td><td>训练停滞时依据失败原因生成教学提示，帮助恢复学习信号。</td><td>固定教学方式后，仅比较失败轨迹本身的可学习价值，避免归功于更好的提示。</td></tr>
<tr><td><a href="references.html#E08">Productive / Unproductive Failure 学习科学文献</a></td><td>失败及其后续整合可能有不同教学结果。</td><td>把启发转为可审计的模型更新与无教师后测，不声称人类结论自动迁移到 LLM。</td></tr>
<tr><td><b>Metcalfe &amp; Kornell · RPL（2005）</b> <a class="cite" href="references.html#E16" title="A Region of Proximal Learning model of study time allocation">[E16]</a></td><td>人类学习者根据主观学习速度选择何时停下当前材料。</td><td>在 RSI 中判断的不是主观学习感受，而是<b>纠正新增失败后未来能力能涨多少</b>。</td></tr>
<tr><td><b>Graves · Automated Curriculum Learning（ICML 2017）</b>与 <b>SPaCe（ACL 2026）</b> <a class="cite" href="references.html#M12" title="Automated Curriculum Learning for Neural Networks">[M12]</a><a class="cite" href="references.html#S45" title="SPaCe: Unlocking Sample-Efficient Large Language Models Training With Self-Pace Curriculum Learning">[S45]</a></td><td>按学习进展分配训练任务/样本与计算预算。</td><td>不能把“进步少就换题”当成新意；要比较同样停滞时不同<b>失败轨迹</b>的收益。</td></tr>
<tr><td><b>Scaf-GRPO（ICLR 2026）</b> <a class="cite" href="references.html#S46" title="Scaf-GRPO: Scaffolded Group Relative Policy Optimization for Enhancing LLM Reasoning">[S46]</a></td><td>训练停滞时提供分层提示帮助模型继续获得有效信号。</td><td>固定纠错反馈，不把更好的提示当成 I6 的失败轨迹价值。</td></tr>
<tr><td><b>SOAR（ICML 2026）</b>与 <b>STRETCH（EMNLP 2026）</b> <a class="cite" href="references.html#S47" title="Teaching Models to Teach Themselves: Reasoning at the Edge of Learnability (SOAR)">[S47]</a><a class="cite" href="references.html#S49" title="STRETCH the Boundaries: A Unified Self-Taught Framework for Progressive LLM Evolution">[S49]</a></td><td>根据模型学习收益生成题目、调整挑战难度。</td><td>不仅看哪道题能学，还看同题的哪条失败值得学以及何时不再收集。</td></tr>
<tr><td><b>BEACON（EMNLP 2026）</b> <a class="cite" href="references.html#S48" title="BEACON: Bayesian Optimal Stopping for Efficient LLM Sampling">[S48]</a></td><td>在推理时平衡多采样的潜在答案收益与推理成本。</td><td>I6 的停止价值是<b>参数/Skill 纠错更新后的未来独立能力</b>，不是当前答案质量。</td></tr>
<tr><td><b>MetaCLASS（EMNLP 2026）</b> <a class="cite" href="references.html#E17" title="MetaCLASS: Metacognitive Coaching for Learning with Adaptive Self-regulation Support">[E17]</a></td><td>人类教学中的不干预动作预测出现偏差。</td><td>“不立即干预”是否提高 RSI 能力还需受控真实训练；不移植 41.7% / 6.6% 作为训练规则。</td></tr>
</tbody></table></div>
<p class="status">文献证据支持研究动机；同题失败价值差异、预测有效性和跨模型迁移尚待本项目验证。</p>


## I6 · 为什么有些错误更值得学习？ / 研究方向的 Go / 缩题 / Stop（与模型的停学决策分开）


<p><b>继续：</b>匹配题目、示范与计算预算后，失败轨迹之间仍有可重复的迁移增益差异；简单的错误严重度、置信度、轨迹长度无法解释全部差异；预测器在未见任务上能减少同预算的错误选择。新增的停止/重访策略若也能带来独立净收益，作为 I6 的强化证据。</p>
<p><b>缩题：</b>只发现纠错收益差异而无法事前预测时，优先做现象与机制分析，不夸大为学习策略优化系统；若停止策略没有超越简单阈值，保留主线并撤掉停止控制器，不强行增设模块。</p>
<p><b>停止：</b>不同错误的差异在同反馈/同预算后消失，或只在原题重复出现、撤掉教师后失效。</p>
<div class="links"><a class="link-btn" href="ideas.html">返回研究候选池</a><a class="link-btn" href="idea-i7-learning-order.html">查看正交方向 I7：学习顺序</a><a class="link-btn" href="experiments.html">通用实验隔离契约</a></div>


## I7 · 先尝试，还是先看示范？ / 一句话科学问题


<p class="thesis"><b>I7：</b>面对相同题目、相同教师示范，先独立尝试再学习，与先看示范再练习，为什么可能造成不同的后续独立能力？这种顺序效应会不会随模型持续更新而改变？</p>
<p>本篇的处理变量只有<b>尝试与正确示范的先后次序</b>。不按错误类型给失败打价值分，不训练 I6 的 Failure Value Estimator。短期分数、解法探索和长期迁移形成一条需要逐步验证的机制链，不是三个同时优化的模块。</p>
<div class="note"><b>与 I6 正交：</b><a href="idea-i6-failure-value.html">I6</a> 在固定教学顺序和方式下，比较哪条失败轨迹值得纠正；I7 固定学习材料与预算，比较先尝试和先看示范。两者共享评测基础设施，但不互为前提。</div>


## I7 · 先尝试，还是先看示范？ / 已有论文研究到了哪一步


<div class="table-wrap"><table><thead><tr><th>论文</th><th>已回答什么</th><th>I7 不能重复什么</th></tr></thead><tbody>
<tr><td><a href="https://doi.org/10.3102/00346543211019105" target="_blank" rel="noopener noreferrer">Sinha &amp; Kapur · Review of Educational Research 2021</a></td><td>53 项研究、166 组比较：在概念知识与迁移指标上，先解题后教学（PS-I）总体优于先教学后解题（I-PS），g = 0.36；程序性知识的汇总差异则不显著。存在任务和学习者边界。</td><td>不能再把“先试错通常更好”直接当成新发现。</td></tr>
<tr><td><a href="https://ijcai.org/proceedings/2015/614" target="_blank" rel="noopener noreferrer">Najar et al. · IJCAI 2015</a></td><td>按学生先前需要多少帮助，动态决定给完整例题、渐隐例题或自主解题。</td><td>简单按正确率/帮助次数分流已经有直接前作。</td></tr>
<tr><td><a href="https://doi.org/10.1109/TLT.2019.2896080" target="_blank" rel="noopener noreferrer">Chen et al. · IEEE TLT 2020</a></td><td>将正确例题、错误例题与自主解题作为可自适应选择的学习活动。</td><td>换成 LLM 四选一教学活动本身不是充分的新颖性。</td></tr>
<tr><td><a href="https://doi.org/10.1007/s10648-025-09993-3" target="_blank" rel="noopener noreferrer">He et al. · Educational Psychology Review 2025</a></td><td>在两个先验知识不同的群体中观察到相反的顺序优势，作者并未证明差异由先验知识单独造成。</td><td>不能武断地说“弱模型先示范、强模型先尝试”。</td></tr>
<tr><td><a href="https://doi.org/10.1007/s11251-020-09528-z" target="_blank" rel="noopener noreferrer">Hartmann et al. · Instructional Science 2021</a></td><td>区分亲自尝试与观察他人失败；准备性学习效果不一定来自自己先失败。</td><td>必须区分“亲自试过”与“额外看过一段失败解法”。</td></tr>
</tbody></table></div>
<p>以上是人类学习/教学系统证据，不等价于 LLM 参数更新的因果效果。I7 的新问题必须落到<b>更新后的模型在没有教师时还能做什么</b>。</p>


## I7 · 先尝试，还是先看示范？ / Challenge → Insight → Design


<div class="table-wrap"><table><thead><tr><th>Challenge · 难在哪里</th><th>Insight · 为什么值得研究</th><th>Design · 怎样解决</th></tr></thead><tbody>
<tr><td>看了示范后正确率更高，可能只是照着答案复现；先试后学的收益又可能仅来自多思考了一次。</td><td>当前表现与真正形成的独立能力不同；顺序必须通过<b>撤掉示范后的持久更新</b>衡量。</td><td>同一检查点做两个随机分支，教师内容、token、训练器、学习步数对齐；清空上下文后用新题后测。</td></tr>
<tr><td>两种顺序短期正确率相近，也可能让模型以后更容易或更难自主找到新解法。</td><td>示范优先可能快速集中概率质量；先尝试可能先激活多条候选路径。但两种方向都只是待检验假设。</td><td>测 pass@1 / 固定 k 的 pass@k、有效不同解法数量、正确路径分布，而不是把无效的多样性当进步。</td></tr>
<tr><td>某一轮有效的顺序，可能在多轮自我改进后不再有效。</td><td>一次教学改变模型内部状态，因而可能改变下一轮适合的学习顺序。</td><td>固定后续任务流，在多次版本更新后测试迁移与旧能力保持；先建立顺序效应，再考虑事前选择器。</td></tr>
</tbody></table></div>


## I7 · 先尝试，还是先看示范？ / 两条学习顺序：只改变先后，不改变教材


<div class="card-grid"><article class="research-card"><b>A · Instruction First</b><h3>先学再做</h3><p>展示同一完整例题与关键步骤 → 再让模型独立完成等价练习 → 统一更新 → 关掉示范、独立后测。</p></article><article class="research-card"><b>B · Problem Solving First</b><h3>先做再学</h3><p>先允许同预算独立尝试 → 展示与 A 完全相同的教师例题 → 统一更新 → 关掉示范、独立后测。</p></article></div>
<p><b>要控制的变量：</b>原始模型检查点、知识点和任务配对、相同正确示范、教师调用次数、训练 token 与更新步数、采样/温度、后测题和外部工具。报告尝试轨迹长度不齐造成的残余预算差异，额外做计算量严格匹配试验。</p>
<p><b>一个容易漏掉的陷阱：</b>不能先让模型在<b>目标题</b>上做一次诊断，再根据这次尝试决定它是否应该“先尝试”。因为诊断本身已经构成处理。事前顺序选择必须基于此前的题目历史或独立诊断题，不能泄漏目标题的先试轨迹。</p>
<p><b>学习载体：</b>首选固定 LoRA 或同一外置技能写入器，分别报告；一次在上下文里读到答案不叫 RSI。学习后清空上下文，冻结独立测试。</p>


## I7 · 先尝试，还是先看示范？ / 决定性实验：短期表现相近，未来能力是否不同？


<div class="flow"><div><b>同版随机分叉</b><small>两种学习顺序</small></div><div><b>固定学习更新</b><small>等教师信息、等预算</small></div><div><b>即时无提示后测</b><small>新题 pass@1 / pass@k</small></div><div><b>多轮后测</b><small>正确解法覆盖与迁移</small></div><div><b>顺序选择</b><small>仅在可复现异质性后尝试</small></div></div>
<p><b>P0：</b>先在一类多步骤数学题上，从同一检查点建立“先看再做 / 先做再看”配对分支。前测、近迁移与结构变形题分开；用固定 k 和固定推理预算评估不同且<b>正确</b>的解法路径。按知识点为统计单位而非题目重复采样次数。</p>
<p><b>机制区分：</b>如果 A 的 pass@1 升高、B 的 pass@k 或正确解法覆盖扩大，需要再检验是否源于采样温度、示范污染或有效样本数不同；多样性变大但正确率下降不能称探索改进。</p>
<p><b>长期检验：</b>继续以冻结任务序列更新多个版本，比较新任务迁移、旧能力回归及学习效率曲线。实验前定义“长期”为经历了多少次<b>新学习更新</b>，不是静态等待多少天。</p>
<p><b>选择策略作为第二阶段：</b>只有不同任务或学习者状态出现稳定的最佳顺序切换，且事前信号可预测时，再用历史状态训练轻量顺序选择器，与固定 A、固定 B、简单按正确率规则和普通 contextual bandit 同预算比较。</p>


## I7 · 先尝试，还是先看示范？ / 什么时候值得继续做成一篇 RSI 论文


<p><b>继续：</b>两种顺序在匹配预算下，对独立更新后的能力出现稳定差异，并且这种差异不能仅由额外练习、教师信息量、采样长度解释；至少有一个关于探索空间或后续轮次迁移的独立、可复验发现。</p>
<p><b>缩题：</b>若只发现短期迁移差异，则只报告有边界的顺序效应；没有可预测的异质性就不强行引入 Router。</p>
<p><b>停止：</b>在清空教师上下文、等学习预算后，先后顺序完全不影响独立能力；或任何优势都可由重复采样数量解释。</p>
<div class="links"><a class="link-btn" href="ideas.html">返回研究候选池</a><a class="link-btn" href="idea-i6-failure-value.html">查看正交方向 I6：错误学习价值</a><a class="link-btn" href="learning-science.html">学习科学基础</a></div>


## I8 · 哪些错误纠正一次，能让模型学会一类题？ / 一句话问题与研究定位


 <div class="decision"><span class="kicker">I8 · MECHANISM VALIDATION · 2026-10-27</span>
 <h3>Why does correcting one mistake sometimes fix a whole class of problems?</h3>
 <p>两个模型都做错同一道题：一个看完答案只能重新答对原题，另一个却能解决几十道共享同一规则的新题。<strong>为什么会有这种差别？我们能否在真正更新参数之前预测？</strong></p>
 <p><b>本研究首先解释学习收益的差异，而不是先发明一个错题排序器。</b>特别区分原题纠正、同规则新题迁移、跨模板迁移、长期保持与旧能力损失。</p>
 </div>
 <p><b>研究状态：</b>机制假设与受控实验协议已形成；尚无本站 I8 的真实训练结果。研究单位是<strong>模型快照 × 当前错误 × 固定反馈/更新操作</strong>；不能将人类学习效应直接宣称为模型已具有的性质。</p>


## I8 · 哪些错误纠正一次，能让模型学会一类题？ / Observable Phenomenon｜最自信的错题，未必最难纠正


 <p>Butterfield 与 Metcalfe（2001）观察到：在得到正确反馈后，人类对原本<strong>高置信度</strong>的错误，有时反而比低置信度错误纠正得更好，即 <b>Hypercorrection Effect</b>。<a class="cite" href="references.html#E12" title="Errors committed with high confidence are hypercorrected">[E12]</a></p>
 <p>Carpenter 等（2018）将这一现象带入大学园艺课程，学生答题、报告置信度、获得正确反馈并参加后测，观察到显著的超纠正现象。<a class="cite" href="references.html#E13" title="Hypercorrection of high-confidence errors in the classroom">[E13]</a></p>
 <p><b>预测误差的机制证据：</b>Pine 等（<i>Nature Communications</i>，2018）让参与者学习事实材料，回答问题并报告置信度，随后收到事实反馈，一周后再测记忆。行为结果显示，当反馈更强烈地违反原本的知识与预期时，语义预测误差（Semantic Prediction Error, PE）与更明显的记忆更新相关；fMRI 进一步观察到腹侧纹状体等区域编码这一差异信号。研究还发现：<b>误导性反馈同样可能把原本正确的记忆改成错误记忆</b>。<a class="cite" href="references.html#E18" title="Knowledge acquisition is governed by striatal prediction errors">[E18]</a></p>
 <p>这里不是说“越自信就一定越有学习价值”。Sitzman 等（2014）发现，<b>已有领域知识</b>可能比主观置信度更能预测错误纠正；置信度的独立解释力有限。<a class="cite" href="references.html#E14" title="Prior knowledge is more predictive of error correction than subjective confidence">[E14]</a></p>
 <p>Foster 等（2022）在中小学在线数学诊断题中研究了置信度与后续类似题表现，但这种相似题纠正不等于复杂规则在 LLM 中已被更新，也不能直接推断因果。<a class="cite" href="references.html#E15" title="School students’ confidence when answering diagnostic questions online">[E15]</a></p>
 <div class="note"><b>可观察矛盾：</b>错误有多“自信”、反馈引起的预期冲突有多强、一次反馈能否修复该题、以及修复后能迁移多少题，是不同的量。Hypercorrection 与语义预测误差提供人类认知证据，但尚未证明 LLM 参数学习具有同样规律，<b>更不能把强烈的信念冲突直接等同于正确、可靠的学习信号</b>。<a class="cite" href="references.html#E18" title="Knowledge acquisition is governed by striatal prediction errors">[E18]</a></div>


## I8 · 哪些错误纠正一次，能让模型学会一类题？ / Why｜为什么有些错误可能具有更大的学习杠杆？


 <p>考虑同一条积分规则的两种错误。<b>模型 A</b> 缺乏指数运算和基本积分等前置知识，单次反馈难以被有效吸收。<b>模型 B</b> 已具备相关基础，却稳定地遗漏幂函数积分公式中的关键分母；若能真正修复这条规则，可能同时改善不同数字与题型中的一批错误。</p>
 <p>这只是<strong>待验证的机制例子</strong>。它提示一次错误纠正的学习价值至少有两个来源：模型有多接近掌握正确规则，以及该规则是否反复影响其他问题。第三个限制是：目前的更新方式能不能实际改变模型在推理时使用该规则的行为。</p>
 <div class="table-wrap"><table><thead><tr><th>可能的错误状态</th><th>已有基础</th><th>共享规则影响范围</th><th>待验证的预测</th></tr></thead><tbody>
 <tr><td>偶然算术失误</td><td>较充分</td><td>小</td><td>容易修复原题，但跨题收益可能很小</td></tr>
 <tr><td>稳定误用共同公式</td><td>较充分</td><td>大</td><td>具有较高规则级纠错潜力</td></tr>
 <tr><td>缺多个前置知识的系统性错误</td><td>不足</td><td>大</td><td>潜在覆盖广，但单次纠正可能难以吸收</td></tr>
 <tr><td>不稳定、难复现的局部错误</td><td>待判定</td><td>小</td><td>不应只因当前失分就优先训练</td></tr>
 </tbody></table></div>
 <p>因此我们的科学问题不是“高置信度错题要不要加权”，而是<strong>同样难度和置信度的错误，为什么具有不同的可学习性与迁移性？</strong></p>


## I8 · 哪些错误纠正一次，能让模型学会一类题？ / Challenge｜真正困难的三个地方


 <h3>C1｜错误表象不等于模型的知识状态</h3>
 <p>相同错误可能来自前置知识缺失、稳定的错误规则或偶然失误；置信度、自评“我会了”和单次采样一致率都不等于知识准备程度。</p>
 <h3>C2｜原题纠正不等于规则内化</h3>
 <p>记住公式、在当前上下文仿照示范作答，并不意味着参数更新后能把规则用于不同结构的新题。RULE-EDIT 已在抽象规则编辑场景中观察到公式层修复与实例迁移之间的落差；不同更新范式不能直接混同。<a class="cite" href="references.html#S41" title="RULE-EDIT: Benchmarking Rule-Level Knowledge Editing in Large Language Models">[S41]</a><a class="cite" href="references.html#S42" title="Editing Rules in LLMs Requires More Than a Localized Update">[S42]</a></p>
 <h3>C3｜学习价值是更新后的反事实结果</h3>
 <p>真正的收益取决于模型、学习材料、优化器、更新预算以及后续任务分布。逐条训练才能测准，但成本高；仅用 one-shot 提示收益、梯度相似性或损失作为替代，则可能测错目标。<a class="cite" href="references.html#S40" title="Self-Error-Instruct: Generalizing from Errors for LLMs Mathematical Reasoning">[S40]</a><a class="cite" href="references.html#M10" title="LESS: Selecting Influential Data for Targeted Instruction Tuning">[M10]</a><a class="cite" href="references.html#M11" title="What Do Learning Dynamics Reveal About Generalization in LLM Mathematical Reasoning?">[M11]</a></p>


## I8 · 哪些错误纠正一次，能让模型学会一类题？ / Insight｜可学性 × 规则影响范围 × 更新兼容性


 <p><b>核心假设：</b>某个错误的跨题收益，受到三个可以部分观察、但不可直接互相替代的条件影响：</p>
 <div class="flow">
 <div><b>Readiness</b><small>是否具备理解正确规则的前置基础</small></div>
 <div><b>Rule Scope</b><small>错误规则是否共同影响大量新题</small></div>
 <div><b>Update Compatibility</b><small>当前更新能否真正改变规则的使用</small></div>
 </div>
 <p><b>Readiness</b> 可以由与最终测试集分离的前置技能探针估计；<b>Rule Scope</b> 可以由规则图、错误在独立变体中复现的频度估计；<b>Update Compatibility</b> 可以由小预算诊断更新或局部学习信号估计，但不能把探针数据、验证数据泄露进最终测试。</p>
 <p><b>Prediction Error 的位置：</b>相对于已有答案与置信度，来自可靠反馈的强烈冲突可以作为待验证的<strong>纠错触发信号</strong>。但它不直接衡量模型能否吸收正确规则，更不直接衡量可以改善多少未见题；错误率、难度或高置信度都不能单独替代真实净迁移收益。<a class="cite" href="references.html#E18" title="Knowledge acquisition is governed by striatal prediction errors">[E18]</a></p>
 <p>操作性目标不是简单的三因子乘积。固定模型 <code>θ</code> 和更新算子 <code>u</code> 后，候选错误 <code>e</code> 的价值应由<strong>真实未见题增益 − 旧能力回归 − 更新成本</strong>定义；上述三因素只是待证实的预测解释变量。</p>
 <div class="equation">V(e | θ, u) = E[Δ Unseen-Rule-Accuracy] − λ E[Regression] − μ Update-Cost</div>
 <p><b>为什么可能提前判断：</b>如果已有知识与错误结构在训练前就含有与实际迁移收益相关的信息，我们无需对全部候选做完整权重更新，而可以先筛出少量最值得验证的错误。该推断需要受控实验确认。</p>


## I8 · 哪些错误纠正一次，能让模型学会一类题？ / Design｜先原因后模块：学习前判断，再有限预算纠错


 <div class="flow">
 <div><b>诊断错误状态</b><small>前置知识、置信度、稳定性、错误规则</small></div>
 <div><b>估计迁移潜力</b><small>Readiness / Rule Scope / Compatibility</small></div>
 <div><b>选择学习对象</b><small>与随机、难度、one-shot、梯度基线比较</small></div>
 <div><b>固定预算的持久更新</b><small>同一 SFT / LoRA 优化器与反馈协议</small></div>
 <div><b>独立验证</b><small>原题、异结构同规则、保持、遗忘</small></div>
 </div>
 <p>首版不同时更换教师、模型规模、训练器与提示模板：固定正确反馈质量和更新方式，只研究<strong>选哪一个错误</strong>。外置 Skill 更新可在后续单独跑，但不能与 LoRA 参数学习混算。</p>
 <p><b>可信反馈门槛：</b>要测量“预测误差是否帮助学会”，必须先由独立验证器确认标准答案及规则。Pine 等的误导性反馈条件提醒我们：意外且被采纳的信息不等于真知识；如果反馈不可靠，应先核验而不是因为冲突很强就自动写入记忆或权重。<a class="cite" href="references.html#E18" title="Knowledge acquisition is governed by striatal prediction errors">[E18]</a></p>
 <p>一旦发现前置知识不足，就先验证“补基础”是否真比“重复给原题反馈”更有效；不能把“错误类型诊断”的分类准确率直接当作学习收益。</p>


## I8 · 哪些错误纠正一次，能让模型学会一类题？ / 决定性实验｜能否在更新前预测跨题收益？


 <h3>实验 A：验证高置信度与已有知识到底是什么关系</h3>
 <p>选取具有规则与前置技能注释的数学题，构造知识准备程度（较高 / 较低）× 规则影响范围（较大 / 较小）的受控分组。报告真实错误来源与受控构造错误分开；匹配题目难度、初始准确率、模型置信度、反馈质量和更新 token。不要用最终测试集来定义规则影响范围。</p>
 <p>每次从同一个模型快照复制独立分支，在候选错误上做固定预算的持久更新。测试时撤掉答案、例题和辅助 Prompt，分别测原题、同规则不同数字、异结构同规则、其他规则以及经过中间训练后的保持。</p>
 <h3>实验 B：真实学习收益预测与选择</h3>
 <div class="table-wrap"><table><thead><tr><th>选择策略</th><th>检验什么</th></tr></thead><tbody>
 <tr><td>Random、Hardest-first</td><td>是否只是比随便挑题更好</td></tr>
 <tr><td>Confidence-first / Stable-error-first</td><td>是否只靠置信度或重复频率就能解释</td></tr>
 <tr><td>Self-Error-Instruct one-shot selection <a class="cite" href="references.html#S40" title="Self-Error-Instruct: Generalizing from Errors for LLMs Mathematical Reasoning">[S40]</a></td><td>即时示例迁移能否替代真实权重更新预测</td></tr>
 <tr><td>LESS gradient-based selection <a class="cite" href="references.html#M10" title="LESS: Selecting Influential Data for Targeted Instruction Tuning">[M10]</a></td><td>梯度对齐是否已经足够；可用相同小样本目标能力集合</td></tr>
 <tr><td>DATAPROPHET-style 价值特征 <a class="cite" href="references.html#M13" title="Demystifying Supervision Data Generalization in Multimodal LMs (DATAPROPHET)">[M13]</a></td><td>困惑度、相似性和多样性等数据集特征在单错误设置下能否解释收益；仅比较经过同任务适配的版本</td></tr>
 <tr><td>SOAR-style 真实学习进步 <a class="cite" href="references.html#S17" title="Teaching Models to Teach Themselves: Reasoning at the Edge of Learnability (SOAR)">[S17]</a></td><td>将实际试训收益作为有成本的参照，不当成训练前无成本预测</td></tr>
 <tr><td>LENS / ACE（学习目标对照）<a class="cite" href="references.html#S43" title="Don&#x27;t Waste Mistakes: Leveraging Negative RL-Groups via Confidence Reweighting">[S43]</a><a class="cite" href="references.html#S44" title="Overconfident Errors Need Stronger Correction: Asymmetric Confidence Penalties for Reinforcement Learning">[S44]</a></td><td>改变错误惩罚是否已能解释收益；与纯样本排序分别报告</td></tr>
 <tr><td>I8：Readiness + Rule Scope + Compatibility</td><td>是否新增可迁移、可解释的预测信息</td></tr>
 </tbody></table></div>
 <p><b>主指标：</b>学习前预测分数与真实未见同规则收益的排序相关；固定训练预算下的净迁移增益；跨模板、跨模型稳定性；回归率。额外报告原题修复率及单条样本筛选成本，防止以更多诊断调用换取假提升。</p>
 <div class="note"><b>强约束：</b>按规则族和模板族划分训练 / 诊断 / 选择验证 / 最终测试；每条候选的训练结果只能用于开发集建模，不能窥视最终测试。按独立规则族聚类计算区间，并单独报告自然错误与注入式错误的结果。</div>


## I8 · 哪些错误纠正一次，能让模型学会一类题？ / Related Work｜最近邻做到了哪一步，I8 真正差在哪里？


 <p>按照 <b>研究问题与假设 → 选择时能看到什么 → 实际修改什么 → 用什么结果证明学会</b> 对照最近邻。这几项不一定谁更强：有的工作研究如何更新，有的研究如何选数据，还有的专门研究规则迁移。<strong>最接近 I8 的不是某一个模型模块，而是 SEI 的错误驱动训练、LESS / DATAPROPHET 的训练前价值预测，以及 RULE-EDIT 的规则级迁移。</strong></p>
 <div class="table-wrap"><table id="i8-related-matrix"><thead><tr>
 <th>代表工作</th><th>研究对象与条件</th><th>用什么信号判断</th><th>操作与实际评价</th><th>与 I8 相同 / 不同之处</th>
 </tr></thead><tbody>
 <tr>
 <td>Self-Error-Instruct<br><small>ACL 2025 <a class="cite" href="references.html#S40" title="Self-Error-Instruct: Generalizing from Errors for LLMs Mathematical Reasoning">[S40]</a></small></td>
 <td>模型已犯的数学错题；使用教师模型分析错误、聚类错误类型。</td>
 <td>用合成例子在开发错题上的 <b>one-shot 即时帮助</b>筛选训练数据。</td>
 <td>合成数据再微调；评价数学任务内与任务外的准确率。</td>
 <td><b>相同：</b>从模型错误出发，关注泛化。<b>差异：</b>I8 要解释并预测<strong>同一次真实参数纠错</strong>对未见同规则题的净收益，而不直接把 one-shot 效果当作该收益。</td>
 </tr>
 <tr>
 <td>LESS<br><small>ICML 2024 <a class="cite" href="references.html#M10" title="LESS: Selecting Influential Data for Targeted Instruction Tuning">[M10]</a></small></td>
 <td>面向目标能力的指令微调数据选择；需要目标能力示例。</td>
 <td>训练前计算优化器感知的低秩梯度相似性，估计样本影响。</td>
 <td>选择指令数据做微调；评价下游目标能力表现。</td>
 <td><b>相同：</b>学习前估计训练价值。<b>差异：</b>I8 的单位是<strong>模型当前的错误及其知识状态</strong>，须检验前置知识和共同错误规则能否提供超出梯度信号的解释与预测。</td>
 </tr>
 <tr>
 <td>DATAPROPHET<br><small>ICLR 2026 <a class="cite" href="references.html#M13" title="Demystifying Supervision Data Generalization in Multimodal LMs (DATAPROPHET)">[M13]</a></small></td>
 <td>视觉语言模型的监督数据集之间的迁移；候选是整批数据而非单道错题。</td>
 <td>不试训候选数据，使用多模态困惑度、相似性及多样性估计影响。</td>
 <td>预测训练集对目标基准的迁移排名，并用实际训练增益核验。</td>
 <td><b>相同：</b>训练前预测真实训练收益，<strong>这不是 I8 首创</strong>。<b>差异：</b>不同数据粒度与任务条件；I8 研究单个当前错误的可纠正性和规则级迁移。跨域结果不能直接当公平的同任务胜负。</td>
 </tr>
 <tr>
 <td>SOAR<br><small>ICML 2026 <a class="cite" href="references.html#S17" title="Teaching Models to Teach Themselves: Reasoning at the Edge of Learnability (SOAR)">[S17]</a></small></td>
 <td>极难数学任务的自动课程；教师生成帮助学生越过学习停滞的新题。</td>
 <td>用<strong>真实训练后的学生进步</strong>奖励教师，而非只用难度代理指标。</td>
 <td>更新出题教师及学生；评价困难题上的实际学习进步。</td>
 <td><b>相同：</b>看真实学习，而不只看当前答题。<b>差异：</b>SOAR 利用已观测的训练收益改进出题；I8 问能否在给定更新预算<strong>花出去之前</strong>预测哪条既有错误更值得纠正。</td>
 </tr>
 <tr>
 <td>RULE-EDIT / DMLE<br><small>EMNLP 2026 <a class="cite" href="references.html#S41" title="RULE-EDIT: Benchmarking Rule-Level Knowledge Editing in Large Language Models">[S41]</a><a class="cite" href="references.html#S42" title="Editing Rules in LLMs Requires More Than a Localized Update">[S42]</a></small></td>
 <td>给定需要编辑的数学 / 物理规则，研究编辑能否从公式迁移到描述和实例。</td>
 <td>使用待编辑的规则及可检验实例；分析不同知识形式与层位置。</td>
 <td>局部或多层知识编辑；测公式修复、实例可迁移性及规则理解。</td>
 <td><b>相同：</b>不能用“会背公式”替代“会应用”。<b>差异：</b>它们侧重<strong>怎样编辑与怎么评估编辑</strong>；I8 先问当前模型的哪类错误规则值得投入同样纠错预算。</td>
 </tr>
 <tr>
 <td>Learning Dynamics<br><small>ICML 2025 <a class="cite" href="references.html#M11" title="What Do Learning Dynamics Reveal About Generalization in LLM Mathematical Reasoning?">[M11]</a></small></td>
 <td>数学推理微调中，区分训练题被记住和真正的泛化。</td>
 <td>观察训练过程、在模型开始复述原训练步骤前的表现。</td>
 <td>分析训练动态与测试性能，并据此改善数据选择。</td>
 <td><b>相同：</b>反对把训练题答对等同于学会。<b>差异：</b>主要信号来自<strong>训练动态</strong>；I8 首先检验不完成候选更新时的错误知识诊断能否预测迁移。</td>
 </tr>
 <tr>
 <td>LENS / ACE<br><small>arXiv 2025–2026 <a class="cite" href="references.html#S43" title="Don&#x27;t Waste Mistakes: Leveraging Negative RL-Groups via Confidence Reweighting">[S43]</a><a class="cite" href="references.html#S44" title="Overconfident Errors Need Stronger Correction: Asymmetric Confidence Penalties for Reinforcement Learning">[S44]</a></small></td>
 <td>可验证奖励强化学习中的错误 rollout；使用采样置信度或相对参考策略的概率变化。</td>
 <td>识别全错误采样组、被异常强化的高置信度错误。</td>
 <td>改变 RL 负奖励或优势权重；评价推理准确率与探索表现。</td>
 <td><b>相同：</b>错误不应一视同仁。<b>差异：</b>它们研究<strong>对错误如何惩罚</strong>；I8 固定反馈与更新方式，研究<strong>先挑哪个错误来学</strong>及其跨题净收益。</td>
 </tr>
 <tr>
 <td><b>I8（待验证）</b></td>
 <td>给定模型快照、已确认的错误、可信纠正反馈和固定 SFT/LoRA 更新预算；规则与前置技能须有可审计的诊断依据。</td>
 <td>更新前的前置知识掌握、错误在规则变体中的稳定性和规则适用范围；另测置信度及轻量更新信号。</td>
 <td>同一更新器纠正不同错误；<b>单独测原题、未见异结构同规则题、后续保持和旧能力损失</b>。</td>
 <td><b>待检验增量：</b>Readiness × Rule Scope 能否解释并预测实际净迁移；并须优于同预算 one-shot、梯度与其他简单信号，当前<strong>没有结果</strong>。</td>
 </tr>
 </tbody></table></div>
 <p class="note"><b>读表结论：</b>I8 不是第一次用错题、第一次选择训练数据或第一次测试规则迁移。我们改变的是<strong>预测对象</strong>：从整批训练数据 / 即时示例 / 已给定的编辑，转向“这个模型现在犯的这一种错误，按同样纠错预算更新后能让多少未见题变好，是否值得优先学习”。</p>
 <p><b>认知机制来源，不作为直接算法基线：</b>Pine 等（<i>Nature Communications</i>，2018）研究人类事实性知识中反馈引发的语义预测误差与一周后记忆更新；其原题复测与 fMRI 结果不等于 LLM 的参数更新或跨题规则迁移。I8 继承的是“已有预期 × 可信反馈冲突”这一待检验线索，而不是把纹状体信号作为语言模型的实现模块。<a class="cite" href="references.html#E18" title="Knowledge acquisition is governed by striatal prediction errors">[E18]</a></p>
 <h3>三处最容易发生 Novelty Collision 的地方</h3>
 <p><b>1. SEI（最接近的错误驱动方法）。</b><b> Same：</b>都是围绕模型错题和同类泛化组织学习。<b> Different：</b>SEI 已有 one-shot 筛选及最终微调增益；I8 的研究对象是某个错误的<strong>训练前状态 → 更新后的真实迁移</strong>之间的关系。<b> Why：</b>一个例子能在提示中帮忙，不保证参数就学到了同一规则。<b> Evidence：</b>冻结同一模型、反馈及 LoRA 预算，直接比较 SEI one-shot 排名和实际未见题净增益的排序相关与固定预算选择收益。<a class="cite" href="references.html#S40" title="Self-Error-Instruct: Generalizing from Errors for LLMs Mathematical Reasoning">[S40]</a></p>
 <p><b>2. LESS / DATAPROPHET（最接近的学习价值预测）。</b><b> Same：</b>不必先完成每个候选的训练就估计其影响。<b> Different：</b>它们使用梯度或数据集统计；I8 针对<strong>已有知识 × 错误规则影响范围</strong>预测单次纠错收益。<b> Why：</b>题目难度、梯度相似性与模型当前是否具备理解规则的基础，可能不能互相替代。<b> Evidence：</b>同一错题候选池、同一可见诊断数据与总调用预算下，比较难度、one-shot、梯度、知识诊断及其组合；另列出 DATAPROPHET 的任务级迁移场景差异，不做跨域分数硬比较。<a class="cite" href="references.html#M10" title="LESS: Selecting Influential Data for Targeted Instruction Tuning">[M10]</a><a class="cite" href="references.html#M13" title="Demystifying Supervision Data Generalization in Multimodal LMs (DATAPROPHET)">[M13]</a></p>
 <p><b>3. RULE-EDIT（最接近的迁移评测对象）。</b><b> Same：</b>都区分修复规则文本与在新题中正确使用规则。<b> Different：</b>RULE-EDIT 研究给定规则后的编辑可迁移性；I8 研究<strong>更新前</strong>哪条错误值得修。<b> Why：</b>潜在能影响很多题的规则，若模型缺少前置知识或当前更新无法吸收，实际收益也可能很小。<b> Evidence：</b>固定更新器，按前置知识高/低 × 规则影响范围大/小做匹配对照，分开报告原题、异结构迁移与旧能力损失。<a class="cite" href="references.html#S41" title="RULE-EDIT: Benchmarking Rule-Level Knowledge Editing in Large Language Models">[S41]</a><a class="cite" href="references.html#S42" title="Editing Rules in LLMs Requires More Than a Localized Update">[S42]</a></p>
 <p><b>对 I8 本身的限制：</b>前置技能探针和规则归属需要可信标注或验证器，诊断本身也有成本；这不是一个“不需要标签、不需要额外计算”的方法。只有上述关系成立、且在强基线下仍有可重复的选择收益，才有充分依据将 I8 从机制研究推进到学习策略算法。</p>


## I8 · 哪些错误纠正一次，能让模型学会一类题？ / 预注册判断｜出现什么结果就停止？


 <p><b>H1：</b>控制已有知识后，高置信度错误的纠正优势可能明显减弱。若无差异，也应如实报告。</p>
 <p><b>H2：</b>在相同更新预算下，知识准备程度与共同错误规则影响范围，对未见题迁移有可复现的交互作用。<strong>这是最核心的机制实验。</strong></p>
 <p><b>H3：</b>学习前的知识与规则诊断，相较难度、置信度、SEI one-shot、LESS 梯度和同任务适配的 DATAPROPHET 式信号，能改善真实净迁移收益预测和等预算学习选择。这个结论目前尚待验证。</p>
 <p><b>继续：</b>H2 关系在独立规则族与至少两个模型配置复现，且 H3 对强基线有稳定增益。<b>缩题：</b>只有机制成立、排序方法没优势，则作为实证机制研究。<b>停止：</b>收益仅限原题或近似改写；在控制知识状态、诊断成本和预算后关系消失。</p>
 <div class="status">当前仅完成文献核对、机制假设、对照与门槛设计；无 I8 训练结果、无已证实的新模型能力增益。</div>


## I8 · 哪些错误纠正一次，能让模型学会一类题？ / 与其他 Idea 的边界｜只研究“纠错能否迁移”


 <p><b>I5</b> 问学生的独立执行能否帮助教师发现并修复自己的盲点；<b>I6</b> 的关注点是跨轮失败瓶颈诊断及下一步学习策略；<b>I7</b> 研究“先尝试还是先看示例”的学习次序；<b>I8</b> 固定学习方式之后，研究哪种<strong>模型当前错误</strong>可以被真正学会、迁移到多少未见题。</p>
 <p>I8 可以给 I6 提供一种学习价值信号，但不是 I6 的通用调度器，也不改变 I7 的教学顺序。网站目前保留独立编号，不因其他候选尚未纳入本站而重新编号。</p>
 <div class="links"><a class="link-btn" href="ideas.html">返回候选 Idea</a><a class="link-btn" href="learning-science.html">查看学习科学来源</a><a class="link-btn" href="references.html">查看全部原始来源</a></div>


## 教学反馈诊断 · I5 的早期研究支线 / 研究目标：更新教师，而不是帮学生提高分数


 <p class="status">历史研究支线（2026-10-21）；当前 I5 统一入口是<a href="idea-i5.html#teaching-feedback">费曼学习法：十模型动态互教与研究支线</a>。此页作为“学生反馈诊断教师盲点”历史实验方案保留，不等同于当前 I5 主线。</p>
 <div class="decision"><span class="kicker">CANDIDATE I5 · PRE-EXPERIMENT DESIGN</span>
 <h3>Learner-Induced Blindspot Discovery for Recursive Agent Self-Improvement</h3>
 <p>核心假设：学生在<strong>独立使用</strong>教师教出的经验时，会暴露一些教师自己执行任务或自我反思时没有发现的隐藏前提、例外条件和错误泛化。这些差异如果能被<strong>独立执行证据</strong>确认，就可能成为教师技能、Harness 或参数更新的有效学习信号。</p>
 <p><b>主要终点：</b>教师 Agent 在更新并清除会话与学生提示之后，在未参与教学/版本选择的新任务上的独立成功率净增益；同时看旧任务的能力回归。</p></div>
 <p>NeurIPS 2024 LbT 已让学生表现影响教师解释选择和教师权重微调；SKILL-KD 已由师生轨迹差异改进<strong>学生</strong>技能；AAAI 2026 MARS 已引入苏格拉底式 Teacher–Student–Critic 提示优化。故本方向不以“有一个学生”“学生会追问”“教师看反馈”作为 novelty。<a class="cite" href="references.html#S20" title="Can LLMs Learn by Teaching for Better Reasoning? A Preliminary Study">[S20]</a><a class="cite" href="references.html#S22" title="SKILL-KD: Contrastive Skill Distillation for LLM Agents">[S22]</a><a class="cite" href="references.html#S21" title="MARS: Multi-Agent Adaptive Reasoning with Socratic Guidance for Automated Prompt Optimization">[S21]</a><a class="cite" href="references.html#S25" title="Large Language Models are In-context Teachers for Knowledge Reasoning">[S25]</a></p>
 <p>教育学 Recursive Feedback 原始研究强调两点：学生在新环境独立运用所学、教师将其行为映射回自身的知识结构。这里的“recursive”是教育学的反馈机制；只有随后证明 Agent 及其改进策略的持久改进，才可称为我们定义下的 RSI。<a class="cite" href="references.html#E09" title="Learning by Teaching Human Pupils and Teachable Agents: The Importance of Recursive Feedback">[E09]</a></p>


## 教学反馈诊断 · I5 的早期研究支线 / 机制抓手：学生反馈究竟比自我测试多了什么？


 <p>把“教师原来能做对”与“教师能否把规则交给另一模型可靠执行”分开。先假设教师 T 有一组成功经验 <code>H_T</code>，通过固定格式提取技能 <code>K_t</code>。学生 S 只能读 <code>K_t</code> 和必要工具文档，不能读教师原任务答案。随后在新的同族 / 邻域任务上独立执行。</p>
 <div class="flow"><div><b>Teacher T 的原经验</b><small>成功轨迹、技能版本</small></div><div><b>教学契约 K_t</b><small>触发、前提、不变量、例外</small></div><div><b>Student S 的独立执行</b><small>新状态、新工具/参数</small></div><div><b>对教师的反事实审计</b><small>是教师漏了还是学生不会？</small></div><div><b>更新 T 而非只更新 S</b><small>独立留出任务检验</small></div></div>
 <p>学生提供的信息可以有三类：<b>疑问</b>（需要条件明确化）、<b>错误执行</b>（教学规则的错误解释）、<b>意外成功</b>（可能揭示与教师不同的有效路径）。必须先判明该现象对教师知识具有增量信息，不能把所有 Student Failure 都写成 Teacher Blindspot。</p>
 <p><b>最低辨别标准：</b>教师自行测试在<strong>相同任务、相同环境调用预算</strong>下的结果，与从学生轨迹得到的增益进行对比。若教师自己探索已同样发现缺陷，则不能声称教学反馈具有不可替代的信息优势。<a class="cite" href="references.html#S20" title="Can LLMs Learn by Teaching for Better Reasoning? A Preliminary Study">[S20]</a><a class="cite" href="references.html#S24" title="Socratic Students: Teaching Language Models to Learn by Asking Questions">[S24]</a></p>


## 教学反馈诊断 · I5 的早期研究支线 / 模块 1｜教学材料是可检验的 Skill Contract


 <p>不要把教案写成自由散文。首版限定为工具型 Agent 的小型程序技能，学生拿到如下结构化产物：</p>
 <pre><code>{
  "skill_id": "paginate_records",
  "trigger": "must exhaust a paginated result set",
  "preconditions": ["API returns items and a continuation token"],
  "state_invariants": ["do not repeat a consumed cursor",
                       "preserve retrieved records across pages"],
  "stop_condition": "confirmed terminal token/flag; not an empty page",
  "edge_cases": ["empty page with next token", "rate limit",
                 "repeated cursor", "duplicated records"],
  "recovery": "bound retries; surface invalid cursor as an error",
  "evidence": ["source trajectory id", "version id"]
}</code></pre>
 <p>这是<strong>示意 API</strong>，终止条件必须按具体 API 规范确定，不可把某一接口的分页约定推广到所有工具。模块输出包括 <code>K_t</code> 和“教师对于规则适用范围的预测”，便于后续构造可证伪的任务变体。</p>
 <p>第一版只更新可回滚、可差分的技能文本；不要同时修改整个 Harness 和权重。对照包含从完整成功轨迹直接归纳技能、子任务级归纳技能。后者是已被研究的重要变量，不能让我们的优势仅来自粒度更细。<a class="cite" href="references.html#S23" title="Break It Down, Pass It On: Cross-Task Skill Transfer in LLM Agents">[S23]</a></p>


## 教学反馈诊断 · I5 的早期研究支线 / 模块 2｜学生必须真实独立执行，而非模拟会不会


 <p><b>固定学生池：</b>建议两种不同模型家族或能力水平的 Student；可加入与教师同底座的干净 Student 副本。所有学生在同一轮使用冻结权重和 Harness，当前任务上下文清零；教学材料仅包含该版本 Skill。</p>
 <div class="table-wrap"><table><thead><tr><th>执行臂</th><th>学生获得的信息</th><th>意义</th></tr></thead><tbody>
 <tr><td>S0</td><td>任务与公开工具文档，无该技能</td><td>学生基础能力基线。</td></tr>
 <tr><td>S1</td><td>相同任务 + Teacher K_t</td><td>测教学技能的实际可迁移性。</td></tr>
 <tr><td>S2</td><td>同任务 + 基于官方规则的完整参考说明（仅开发集）</td><td>排查“学生根本无法执行”的可能；不是无条件金标准。</td></tr>
 <tr><td>T0</td><td>原教师快照独立执行同任务，不能看学生轨迹</td><td>区分教师自己能否解决及普通探索机会。</td></tr>
 </tbody></table></div>
 <p>对 S0/S1/S2/T0 采用可复位环境快照、匹配试验种子与同等 Token/工具调用上限。学生可提交最多 2 条<strong>可定位到任务事实的追问</strong>，但学生的自述困惑不是证据；必须附有执行轨迹、工具响应或受验证的边界例子。另设<strong>只追问不执行</strong>的消融，检验是否只是多生成了一些疑问。</p>
 <p><b>切分：</b>技能源轨迹、学生试教任务、补丁筛选任务、最终教师独立评测按任务族、状态约束、工具组合隔离。学生试教任务属于训练反馈，不能再用作最终测试。</p>


## 教学反馈诊断 · I5 的早期研究支线 / 模块 3｜教学失败归因：不能把学生弱当教师错


 <p>诊断器输入：已冻结的教师/学生执行记录、技能条款引用、环境快照标识、验证器断言；输出带可复现证据的<strong>候选</strong>诊断，而不是单凭语言推断的“根因金标”。</p>
 <div class="table-wrap"><table><thead><tr><th>观察</th><th>解释优先级</th><th>需要的额外验证</th></tr></thead><tbody>
 <tr><td>T0 成功；S1 失败；S2 成功</td><td>教学表达不充分、学生对技能理解偏差。</td><td>换学生、只改技能表达后是否修复？旧 T 能否使用原技能完成任务？</td></tr>
 <tr><td>T0 失败；S1 失败；参考执行成功</td><td>教师自身技能 / 知识盲点的候选。</td><td>重建最小反例；教师的错误规则是否能稳定触发？</td></tr>
 <tr><td>T0 成功；S1 失败；S2 也失败</td><td>学生模型能力或工具接口障碍。</td><td>不同学生、同上下文的参考脚本、环境复位。</td></tr>
 <tr><td>T0 失败；S1 成功</td><td>学生可能提供不同且有效的规则。</td><td>教师无学生提示独立重试；检验学生成功非偶然。</td></tr>
 <tr><td>执行或参考脚本不稳定</td><td>不可判定。</td><td>重现工具/验证器问题，禁止直接用于教师更新。</td></tr>
 </tbody></table></div>
 <p><b>反事实检查：</b>可尝试仅替换 Skill 中一条候选规则（如把“空页就停止”改为“看终止 token”），在相同快照中重跑；再通过其他模型与新状态确认修复没有依赖学生特定提示。将事件分类为 <code>TEACHER_GAP</code>、<code>EXPRESSION_GAP</code>、<code>STUDENT_LIMIT</code>、<code>ENV_FAULT</code>、<code>UNRESOLVED</code>。</p>
 <div class="note">“T0 失败、S1 失败”仍不自动证明教师根因；“S2 成功”也不是证明 S1 的唯一原因。原因标签是可反驳的工作假设，后续通过干预建立更强证据。</div>


## 教学反馈诊断 · I5 的早期研究支线 / 模块 4｜把被验证的盲点转成教师自己的持久更新


 <p>首版共享固定 Editor（可以是相同 LLM + 相同编辑模板），每个候选最多修改一项前提、不变量、边界或恢复步骤。原则：<b>学生证据只告诉我们哪里需要查，不保证应该怎样改</b>。</p>
 <div class="flow"><div><b>生成候选 patch</b><small>引用具体技能条款</small></div><div><b>局部可执行复现</b><small>最小反例消失？</small></div><div><b>独立开发验证</b><small>同类新任务/旧正确任务</small></div><div><b>置信与成本门控</b><small>收益、回归、验证次数</small></div><div><b>接受 / 拒绝 / 回滚</b><small>保存版本链</small></div></div>
 <p>对每个候选 <code>K_t'</code>，统计目标修复、同机制新任务迁移、其他任务回归、执行成本。开发门控与最终独立测试分开；一个任务成功不能把 patch 升级为“有效”。保留所有被拒修改与失败原因。补丁需要清楚记录：哪个学生行为触发、哪条语义规则被修改、具体执行结果、教师在更新前后表现。</p>
 <p><b>两条升级轨道：</b>A 轨将技能文件版本 <code>K_t → K_t'</code> 装载给<strong>教师自己</strong>，权重不动；B 轨在 A 轨验证有效后，以同样数据预算训练教师 LoRA，再彻底清除额外技能与会话进行评测。不能把 A 轨提升称为“权重学会了”，也不能把学生变强算作教师结果。<a class="cite" href="references.html#S20" title="Can LLMs Learn by Teaching for Better Reasoning? A Preliminary Study">[S20]</a><a class="cite" href="references.html#S04" title="Self-Adapting Language Models (SEAL)">[S04]</a></p>


## 教学反馈诊断 · I5 的早期研究支线 / 可编程最小算法：一轮 Teaching-to-Improve


 <pre><code>for episode in teaching_stream:
    parent = freeze_teacher_state()
    skill = extract_skill_contract(parent, seed_successes)

    # All branches start from independent, resettable copies.
    for task in probe_tasks:   # training feedback only
        t0 = execute(teacher=parent, task=task, skill=skill)
        for student in frozen_student_pool:
            s0 = execute(student, task, lesson=None)
            s1 = execute(student, task, lesson=skill)
            questions = bounded_questions(s1, max_questions=2)
            record(task, student, t0, s0, s1, questions)

    evidence = attribute_with_counterfactuals(records)
    candidates = fixed_editor(parent, evidence, max_edits=3)

    winner = None
    for patch in candidates:
        if not executable_reproduction(patch, evidence):
            continue
        result = independent_dev_and_regression_gate(patch)
        if result.pre_registered_accept:
            winner = choose_without_test_leakage(winner, patch, result)

    commit_or_keep_parent(winner)
    seal_version_and_cost_ledger()

# Outside adaptation, evaluate NEW task families:
# old/new teacher, equal inference, no student feedback,
# no training probes, and clean conversation state.</code></pre>
 <p>实现时的核心数据结构：<code>TeacherRevision</code>（权重与技能哈希）、<code>StudentRevision</code>、<code>SkillContract</code>、<code>TeachingEpisode</code>、<code>AttributionRecord</code>、<code>PatchCandidate</code>、<code>PairedOutcome</code>。每条记录含 <code>parent_state_id</code>、环境镜像/commit、随机种子、任务族、Split、学生可见材料、执行成本和审计来源。</p>
 <div class="links"><a class="link-btn" href="teaching-protocol.json" download>下载结构化实验协议</a><a class="link-btn" href="research-notes.md" download>下载完整研究笔记</a></div>


## 教学反馈诊断 · I5 的早期研究支线 / 升级到 RSI 的必要一步：改进“如何教学试验”本身


 <p>只在固定算法下迭代更新技能，可以称<strong>教学反馈驱动的系统层面持续自改进</strong>；还不足以声称改进器本身学会递归改进。后续元策略 <code>π_φ</code> 可选择 <code>a=(选哪种学生, 何种试教任务/追问, 证据检查, 编辑目标, 停止/拒绝)</code>。</p>
 <p>元控制器从历史的<strong>教师自身</strong>独立增益学习，而不是从学生答对率学习；例如：</p>
 <div class="equation">R_meta = Δ Success_T,on-meta-dev − λ Regression_T − μ (Tokens + ToolCalls + Compute)</div>
 <p>元策略训练只读 <code>D_meta</code> 的效果标签，最外层 <code>D_test</code> 彻底封存。比较固定 Student 策略、随机 Probe、教师自己选 Probe、普通 contextual bandit，以及训练后的 <code>π_φ</code>。特别重要：<b>Meta-reset</b>——把教师重置为同一个初始快照，仅保留新旧两版元控制器，在未见任务流比较“能否更高效地找到、验证并修复盲点”。</p>
 <p>学生提问策略可能已经能通过 DPO 训练，本身也不是新颖性；我们检验的是<strong>提问对教师后续改进决策的价值</strong>，并与固定问句和普通不确定性采样比较。<a class="cite" href="references.html#S24" title="Socratic Students: Teaching Language Models to Learn by Asking Questions">[S24]</a><a class="cite" href="references.html#M07" title="Dual Control for Approximate Bayesian Reinforcement Learning">[M07]</a></p>


## 教学反馈诊断 · I5 的早期研究支线 / 模型 / 数据集 / 工程实现建议


 <div class="table-wrap"><table><thead><tr><th>组件</th><th>初始建议</th><th>验收要求</th></tr></thead><tbody>
 <tr><td>Teacher</td><td>Qwen3.5-9B（主），27B 同族扩展。</td><td>先选有成功也有失败的工具任务，且单次运行可复位。<a class="cite" href="references.html#B04" title="Qwen3.5-9B">[B04]</a><a class="cite" href="references.html#B05" title="Qwen3.5-27B">[B05]</a></td></tr>
 <tr><td>Student pool</td><td>一个弱于 T、一个与 T 不同家族的冻结 Student；另设同底座干净副本。</td><td>强弱关系用环境基线<strong>实测</strong>，不靠参数量猜测。</td></tr>
 <tr><td>诊断 / Patch Editor</td><td>共享冻结模型；条件间不换 Editor。</td><td>相同任务、样例、生成候选数和上下文预算。</td></tr>
 <tr><td>机制主环境</td><td>ToolSandbox + 在其 API 风格下构造的独立任务族。</td><td>可复位状态、工具轨迹、真实终止判断。<a class="cite" href="references.html#B01" title="ToolSandbox: A Stateful, Conversational, Interactive Evaluation Benchmark for LLM Tool Use Capabilities">[B01]</a></td></tr>
 <tr><td>第二环境</td><td>AppWorld 的 train / dev，或版本锁定的 τ 文本任务。</td><td>评测集不进入教学或选择；AppWorld 的 test_normal / test_challenge 仅作最终测试。<a class="cite" href="references.html#B07" title="AppWorld Benchmark: executable app-ecosystem agent tasks">[B07]</a><a class="cite" href="references.html#B02" title="τ-bench / τ²-bench：官方仓库与版本化评测协议">[B02]</a></td></tr>
 <tr><td>外部评测</td><td>固定 Terminal-Bench 2.1 / AppWorld test。</td><td>只评冻结方法及整体结果，不看单题测试报告调参。<a class="cite" href="references.html#B03" title="Terminal-Bench 2.1">[B03]</a><a class="cite" href="references.html#B07" title="AppWorld Benchmark: executable app-ecosystem agent tasks">[B07]</a></td></tr></tbody></table></div>
 <p>推荐 <code>Python 3.12 + pydantic + vLLM/LiteLLM + Docker + Parquet/JSONL</code> 实现小规模闭环；并行分支用任务队列与独立环境快照。第二阶段再引入 LoRA / GRPO，不把大规模 RL 训练作为 P0 前提。这里只规定接口与验收，暂未安装运行以上栈。</p>


## 教学反馈诊断 · I5 的早期研究支线 / P0：两周内应该产出的硬证据


 <p><b>先验证两个现象，而不是直接跑完整 RSI。</b>第一，教学后的独立 Student 行为是否比教师等预算直接 Probe 更常暴露<strong>经复现的教师规则缺口</strong>？第二，针对这些缺口的同预算 patch 是否比自我反思和直接技能归纳提升了<strong>教师自身</strong>的未见任务表现？</p>
 <div class="table-wrap"><table><thead><tr><th>阶段</th><th>建议规模（计划）</th><th>准入门槛</th></tr></thead><tbody>
 <tr><td>P0a · 管线预检</td><td>4 个任务族 × 2 Student × 3 seed</td><td>环境可复位、数据/答案隔离、Student 真正独立执行。</td></tr>
 <tr><td>P0b · 盲区辨别</td><td>24 个任务族 × 2 Student × 3 seed；每轮限制提问/执行</td><td>有稳定、验证通过且不能完全由学生弱点解释的事件。</td></tr>
 <tr><td>P0c · 方法对照</td><td>对 P0b 中合法事件生成 3 个 patch，同父版本配对比较</td><td>相同调用/编辑/验证成本下，教师未见任务净收益优于最强朴素基线。</td></tr>
 <tr><td>P1 · 长程与迁移</td><td>2 个通用环境、≥2 教师、不同家族学生、5 条独立学习流</td><td>效果迁移到自然失败、不同工具组合；报告所有失败与回归。</td></tr>
 </tbody></table></div>
 <p>以上为计划规模，不是已跑实验。先按任务族聚类分析；多条相似 Probe 不能假装是独立统计单位。选择成功与失败混合的 T 初始状态须遵守<strong>事先固定的筛选规则</strong>并披露丢弃比例，不能只挑特别容易修复的案例。</p>


## 教学反馈诊断 · I5 的早期研究支线 / 六种不可省的基线、消融与失败条件


 <div class="table-wrap"><table><thead><tr><th>Baselines / 消融</th><th>必须匹配</th><th>排除什么解释</th></tr></thead><tbody>
 <tr><td>Self-Reflection / Reflexion</td><td>教师看自己轨迹，获得同样验证预算</td><td>只是普通自我复盘起作用。</td></tr>
 <tr><td>Self-Probe / Self-Questioning</td><td>教师独立访问<strong>同一批</strong> Probe 任务，调用预算匹配</td><td>学生只是替教师做了额外测试。</td></tr>
 <tr><td>LbT-Feedback / LbT-DPO 风格</td><td>学生反馈与更新数据规模可比</td><td>已有学习型教学反馈已足够。<a class="cite" href="references.html#S20" title="Can LLMs Learn by Teaching for Better Reasoning? A Preliminary Study">[S20]</a></td></tr>
 <tr><td>Teacher→Student Distill（SKILL-KD 类）</td><td>一致的 Skill 与学生执行任务</td><td>收益仅由让学生变强产生。<a class="cite" href="references.html#S22" title="SKILL-KD: Contrastive Skill Distillation for LLM Agents">[S22]</a></td></tr>
 <tr><td>Direct Skill Induction / GEPA</td><td>相同候选数、Skill 粒度与实际执行调用</td><td>只因更细粒度或更多提示搜索。<a class="cite" href="references.html#S03" title="GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning">[S03]</a><a class="cite" href="references.html#S23" title="Break It Down, Pass It On: Cross-Task Skill Transfer in LLM Agents">[S23]</a></td></tr>
 <tr><td>随机/打乱 Student Trace、Question-Only</td><td>相同上下文长度与编辑器</td><td>任何学生文字、更多 Token 都能提高分数。</td></tr>
 </tbody></table></div>
 <p><b>主指标：</b><code>Verified Teacher-Gap Yield / 100 env calls</code>、<code>Teacher Held-out Net Gain</code>、旧任务回归率、跨学生一致性、同机制/新机制迁移、完整训练与验证预算。<b>不能以学生成绩、解释长度或教师的自评信心替代教师独立收益。</b></p>
 <p><b>立即停止或缩题：</b>① Student 事件基本都来自 Student 能力上限；② 同预算 Teacher Self-Probe 也能暴露一样多盲点；③ 修复仅提升 Student，教师自身不升；④ 清空教师对话与教学材料后收益消失；⑤ 结果仅在人工故障或原题中出现。若只证实学生反馈有助于技能转移，可写分析但不要称 RSI 方法突破。</p>


## 教学反馈诊断 · I5 的早期研究支线 / 论文路线与可投稿主张的上限


 <p><b>最小论文主张：</b>存在并可量化一种“学生独立应用所教规则所暴露的、教师自我测试容易遗漏的错误信息”，且验证后可用于教师自身的持久技能改进。</p>
 <p><b>更强论文主张：</b>在相同任务、预算、编辑器与验证器条件下，基于 Student 反馈的归因与更新比通用反思/直接 Probe 改进了跨任务的教师独立成功率，并能在新学生和新任务机制上复现。</p>
 <p><b>Meta-RSI 级主张：</b>训练后的教学 Probe 策略，在重置底层教师后的新任务流中比冻结元策略更高效；它优化的是未来学习过程，而不只是当前补丁。</p>
 <div class="note">这三个主张递进但不等价。论文初期应只承诺前两层；看到 P0 / P1 结果后再决定第三层。与 2024 LbT、AAAI 2026 MARS、SKILL-KD 和学生提问研究的逐实验对比仍需要在正式投稿前持续更新。<a class="cite" href="references.html#S20" title="Can LLMs Learn by Teaching for Better Reasoning? A Preliminary Study">[S20]</a><a class="cite" href="references.html#S21" title="MARS: Multi-Agent Adaptive Reasoning with Socratic Guidance for Automated Prompt Optimization">[S21]</a><a class="cite" href="references.html#S22" title="SKILL-KD: Contrastive Skill Distillation for LLM Agents">[S22]</a><a class="cite" href="references.html#S24" title="Socratic Students: Teaching Language Models to Learn by Asking Questions">[S24]</a></div>


## 历史草案：跨轮瓶颈诊断（原 I6） / 编号更新说明：这不是当前 I6


 <p class="thesis"><b>历史版本：</b>以下“瓶颈诊断”曾临时被编号为 I6。2026-10-27 研究拆分后，当前 <a href="idea-i6-failure-value.html">I6</a> 只研究失败过程的学习价值，<a href="idea-i7-learning-order.html">I7</a> 研究先做还是先学，<a href="i8.html">I8</a> 研究 Hypercorrection 与规则级迁移。本页作为旧版构思归档，不占用 I6 编号，也没有改名为新的 I9。</p>


## 历史草案：跨轮瓶颈诊断（原 I6） / 历史问题：同样 70 分，为什么下一轮不该用同一种方法？


 <p class="thesis"><b>I6 的问题：</b>一个自我改进系统已经进入平台期，能否用少量可复验的干预确定当前最限制<strong>后续独立能力增长</strong>的环节，并在主要瓶颈发生转移时及时切换学习模式？</p>
 <p>例子：两个数学 Agent 的单次正确率都是 70%。A 多次采样常能产生正确解，但自己的答案选择器总选错；B 不论怎么重采样都很少成功，但补一条前置定理后明显改善。继续统一做 GRPO、统一增加教师示范，甚至只按“70 分应该练什么”选任务，都可能用错力。</p>
 <p><b>研究定位：</b>I6 是<strong>跨轮学习闭环的元控制问题</strong>（什么时候应该从补知识切到搜索、从搜索切到修验证或巩固等），不是发明四个底层学习算法。四个环节是能力形成的先后依赖，<strong>不是</strong>所有模型必经的四个时间阶段，也不是排他的四选一错误标签。</p>
 <div class="idea-focus"><span class="idea-axis">信号对不对</span><span class="idea-axis">有没有新东西</span><span class="idea-axis">采不采得到</span><span class="idea-axis">吸收了会不会丢</span><span class="idea-axis">安全</span><p>考试 0–60 / 60–80 / 80–90 / 90–100 的分段仅用来提出“学习方式可能反转”的启发性假设；实际切换依据是可观测的瓶颈与干预收益，不是固定成绩阈值、模型参数规模或“智力”标签。</p></div>


## 历史草案：跨轮瓶颈诊断（原 I6） / Challenge：同一个平台期，可能卡在四个不同环节


 <div class="table-wrap"><table><thead><tr><th>环节 / 可观察现象</th><th>最小受控检查</th><th>可调用的动作族</th></tr></thead><tbody>
 <tr><td><b>① 知识不足</b><br>基础前置题、概念题也失败</td><td>保持搜索与验证预算不变，随机对照“给经过核验的缺失知识”与“不给”；测可迁移解题率，而不是只看同一题的抄答。</td><td>知识补充、简短示例、前置任务学习、按需查询（必要时调用 I1）</td></tr>
 <tr><td><b>② 搜索不足</b><br>多次采样偶尔正确，单次命中很低</td><td>固定信息与验证器，提高候选数或加入回溯；比较 pass@1、固定 k 下候选覆盖及新增有效路径。</td><td>探索、对比成功与失败路径、搜索或强化学习</td></tr>
 <tr><td><b>③ 选择不足</b><br>正确候选已经产生，却没有被选中</td><td>冻结同一批候选，比较原验证器与可信独立验证/排序；不能把重新生成更好候选算成验证改进。</td><td>校准验证器、候选排序、独立测试反馈</td></tr>
 <tr><td><b>④ 吸收不足</b><br>答案或 Skill 在手，但撤除后仍不会</td><td>冻结已验证示例与训练预算，允许真实更新后清空提示/伙伴/临时记忆；用未见题和后续回归测持久收益。</td><td>技能或权重更新、针对性训练、撤辅评测；具体学习方式由 I2/I3 实现</td></tr>
 </tbody></table></div>
 <p><b>关键困难：</b>单个测试的失败不能证明某类能力绝对不存在。有限 pass@k=0 不等于正确路径不可采样；外部知识带来的即时成功不等于知识已内化；验证器本身可能被污染。四项检查应记录对照差、样本量、成本、置信区间和互相干扰，允许“多重瓶颈 / 无法判定”。</p>


## 历史草案：跨轮瓶颈诊断（原 I6） / Insight：更有用的是发现瓶颈何时发生转移


 <h3>原因先于模块</h3>
 <p>对于停滞模型，增加数据、搜索次数、验证精度或参数更新并不等价。如果知识已经足够，但候选长期被评估器错选，继续补教材可能无法提高最终表现；如果验证器已可靠、训练后仍忘记新方法，就需要改善吸收与巩固环节。<b>同一模型连续进步时，曾经最有效的干预可能失效，因为瓶颈已经转移。</b></p>
 <p>学习科学中的 <b>Region of Proximal Learning</b> 提醒我们，单位时间内最值得学的内容不必是最难的；但这来自人类实验，只支持研究动机，不直接证明 LLM 的最优学习区域。<a class="cite" href="references.html#E11" title="The Dynamics of Learning and Allocation of Study Time to a Region of Proximal Learning">[E11]</a></p>
 <div class="flow">
 <div><b>知识可用？</b><small>若缺失，先补前置条件</small></div>
 <div><b>路径可采？</b><small>若可采但稀少，加强探索</small></div>
 <div><b>候选可选？</b><small>若错选，修验证与排序</small></div>
 <div><b>更新可留？</b><small>若撤辅仍失败，改变吸收过程</small></div>
 </div>
 <p class="note"><b>递进不等于固定顺序训练：</b>这里描述的是能力产出的依赖链。模型可以同时缺知识又选错答案，也可能在任何一轮回到前面环节。I6 的可检验贡献应是<strong>准确发现主导瓶颈的切换时刻</strong>，并把这种发现转化成下轮的独立学习收益。</p>


## 历史草案：跨轮瓶颈诊断（原 I6） / Design：低成本探测 + 跨轮切换，而非又造一个万能 Learner


 <div class="flow">
 <div><b>冻结学习状态</b><small>版本、任务与预算锚定</small></div>
 <div><b>四组局部 Probe</b><small>测候选覆盖、错选、知识与撤辅</small></div>
 <div><b>判断瓶颈变化</b><small>对照差 + 不确定性 + 切换成本</small></div>
 <div><b>路由到动作族</b><small>执行已有 I1–I5 或工具模块</small></div>
 <div><b>未见题独立复测</b><small>收益、遗忘、安全回归后再判断</small></div>
 </div>
 <h3>机制：发现“继续沿用当前学习模式不划算”的证据</h3>
 <p>对每轮学习状态保留 <b>Probe Report</b>，记录各环节可恢复的错误质量与估计误差。只在某类干预的预期净收益超过当前模式，并通过最小持续性/置信门槛时切换，避免一次随机错题就频繁改策略。低置信度时允许继续诊断、复习或暂不更新。</p>
 <div class="equation">next_mode = switch_if( gain(new mode) − gain(current mode) &gt; cost_of_switch + uncertainty_margin )</div>
 <p>此式是待评估的控制原则，不代表已经训练出模型。实际增益指<strong>未来未见任务、撤除临时帮助后的能力变化</strong>，估计用开发任务，最终测试集绝不参与路由决策。诊断开销和多分支试训均计入总预算。</p>
 <h3>组件协议：只决定“下一轮修哪一环”</h3>
 <div class="table-wrap"><table><thead><tr><th>I6 接口</th><th>职责</th><th>明确不做</th></tr></thead><tbody>
 <tr><td>输入</td><td>冻结版本 ID、各类 Probe 证据、学习历史、可调用动作族、成本与安全限额</td><td>不直接修改执行器、权重、Skill 或线上权限</td></tr>
 <tr><td>输出</td><td>瓶颈假设（可多标签）、置信度、切换/继续原因、下一动作族及试验预算</td><td>不选择 I5 具体伙伴、不制定 I3 巩固内容、不实现 I2 学习算法</td></tr>
 <tr><td>反馈</td><td>跨轮无辅助能力增益、保持率、诊断成本、版本回归和安全门</td><td>不以当前答题总分或自我解释替代外部验证</td></tr>
 </tbody></table></div>


## 历史草案：跨轮瓶颈诊断（原 I6） / 与 I1–I5 的正交边界：调用它们，不接管它们


 <div class="table-wrap"><table><thead><tr><th>已有 Idea 的独立研究对象</th><th>I6 与它的关系</th><th>不可重复声称的贡献</th></tr></thead><tbody>
 <tr><td><a href="ideas.html#idea-1"><b>I1 · 脚手架学习</b></a>：哪些知识应内化，哪些适合外部检索/撤辅？</td><td>I6 只检测当前是否主要受知识/支架依赖限制；需要内化还是查询，由 I1 决策。</td><td>不能把“支持获取与撤除”作为 I6 的新机制。</td></tr>
 <tr><td><a href="ideas.html#idea-2"><b>I2 · 因材施教</b></a>：同样失败、同一更新对象，哪一种试学方法最有效？</td><td><b>最需解耦：</b>I2 做给定学习需求下的局部教学动作优化与响应估计；I6 只研究跨环节主导瓶颈的检测、持续性与跨轮模式切换。可以把 I2 作为“吸收环节”的已固定子模块和强基线。</td><td>不能把“试学→比较收益→选更好教学法”重新包装成 I6。</td></tr>
 <tr><td><a href="ideas.html#idea-3"><b>I3 · 温故知新</b></a>：新旧 Skill/能力冲突时怎么定向巩固？</td><td>I6 把旧能力退化作为状态与硬约束，必要时把处理请求交给 I3。</td><td>不提出新型重放/抗遗忘算法。</td></tr>
 <tr><td><a href="ideas.html#idea-4"><b>I4 · 生产性失败</b></a>：单次失败后是否继续试验，何时足以写 Skill？</td><td>I6 在<strong>多轮学习</strong>尺度上决定应不应该从搜索转到验证/补知识/吸收。单个失败链的试验与证据停止规则仍由 I4 负责。</td><td>不抢“失败后什么时候总结”的贡献。</td></tr>
 <tr><td><a href="ideas.html#idea-5"><b>I5 · 费曼学习法</b></a>：与哪个伙伴互教，才能让自己独立能力增长最多？</td><td>I6 判断是否需要外部教学/协作；若需要，I5 负责伙伴匹配与交换。</td><td>不学习伙伴图或声称发现最佳能力差。</td></tr>
 </tbody></table></div>
 <p class="note"><b>正交判据：</b>只保留 I6 的变化检测器与模式切换规则，其余每个动作均调用固定实现，仍能单独检验“何时换模式”带来的增量；反过来固定 I6，I1–I5 每项方法也必须能各自检验自身研究问题。如果 I6 的全部优势只是更好的 I2 单轮动作预测，就应合并而不是新立方法。</p>


## 历史草案：跨轮瓶颈诊断（原 I6） / Related Work：已有诊断与动态路由，我们还差在哪？


 <div class="table-wrap"><table><thead><tr><th>直接前作</th><th>他们研究的是什么</th><th>I6 额外必须证明</th></tr></thead><tbody>
 <tr><td><b>Mind the Gap</b>，ICLR 2025 <a class="cite" href="references.html#S35" title="Mind the Gap: Examining the Self-Improvement Capabilities of Large Language Models">[S35]</a></td><td>生成—验证差距、可改进性与迭代收益；生成/验证/更新的模块分析已有基础。</td><td>不是首次分瓶颈，而是跨轮检测主瓶颈转移并改善后续选择。</td></tr>
 <tr><td><b>FlyBy</b>，2026 <a class="cite" href="references.html#S36" title="Knowing When Thinking Is Not Enough: Teaching Small Reasoning Models to Reason Beyond Their Parametric Knowledge (FlyBy)">[S36]</a></td><td>以受控推理状态区分知识与执行瓶颈，再选择是否向强模型查询。</td><td>从一次推理中的查询决策推进到经过持久更新的下一轮学习机制切换。</td></tr>
 <tr><td><b>Why SFT Fails to Learn</b>，ACL 2026 <a class="cite" href="references.html#S37" title="Why Supervised Fine-Tuning Fails to Learn: A Systematic Study of Incomplete Learning in Large Language Models">[S37]</a></td><td>诊断监督训练无法吸收数据的多种具体原因，并试验对应干预。</td><td>不限于 SFT 的内化子问题，比较知识/生成/选择/吸收跨环节瓶颈迁移。</td></tr>
 <tr><td><b>SRPO</b>，COLM 2026 <a class="cite" href="references.html#S38" title="Unifying Group-Relative and Self-Distillation Policy Optimization via Sample Routing (SRPO)">[S38]</a></td><td>按样本正确/错误，将 GRPO 和自蒸馏目标路由，抑制后期不稳定。</td><td>需要证明比固定样本级优化路由更有效的<strong>跨轮诊断重分配</strong>。</td></tr>
 <tr><td><b>From Rollouts to Recipes</b>，EMNLP 2026 <a class="cite" href="references.html#S39" title="From Rollouts to Recipes: Self-Contained Post-Training for LLMs">[S39]</a></td><td>按 rollout 正确性与置信度路由 GRPO、蒸馏、正则化或跳过，路由比例随训练改变。</td><td>这是最强近邻之一：必须控制相同动作集与预算，证明因果 Probe 和瓶颈变迁信息具有额外价值。</td></tr>
 <tr><td><b>R²Orch</b>，2026 <a class="cite" href="references.html#S26" title="R²Orch: Recursive Self-Improvement for Agent Orchestration via Self-Play within a Skill-Internalization Loop">[S26]</a></td><td>根据 Skill Withdrawal 的可学习性选任务，撤 Skill 后检验独立能力。</td><td>在技能撤辅之外，独立识别并切换验证/搜索/知识等主环节。</td></tr>
 </tbody></table></div>
 <p>上述工作已经覆盖失败分类、试训干预和动态优化目标。因此 I6 的贡献门槛不能是“四类标签”“根据错误给建议”或“会变化的训练配方”。还需要额外排除仅多采样、仅更大的验证器和仅增加训练数据带来的收益。</p>


## 历史草案：跨轮瓶颈诊断（原 I6） / 决定性实验：验证切换的必要性，而不是做一个花哨路由器


 <h3>E1 · 同分不同因</h3>
 <p>选数学与代码任务，构造<strong>初始 pass@1 相近</strong>但验证错选、知识缺失、搜索稀缺或内化失败各不相同的冻结状态；加入未经人工注入的自然失败状态。对每个状态随机进行四类有限预算干预，并在独立新题上确认实际最佳动作。核心是同分条件下出现可复验的<strong>跨环节最优动作差异</strong>，而不是分类器拟合人工标签。</p>
 <h3>E2 · 同一模型能力变化后的策略反转</h3>
 <p>冻结多个连续训练检查点，考察某环节已经修复后，继续沿用原模式与切换新模式的等预算后续收益。记录预先固定的 Probe 阈值、切换延迟、误报率、模式抖动和切换成本。以只看当前总分、只看 rollout 成败、LLM 自述原因、I2 风格单轮试学/通用 bandit 作为强对照。</p>
 <h3>E3 · 多轮能力平台期能否真实突破</h3>
 <p>弱/中/强学习者按<strong>预先独立测得的能力</strong>分组，而非直接按参数量代表智力；使用同一模型家族与跨家族复核。固定候选动作实现、教师预算、总训练 token、探测成本与计算开销，对比<strong>固定策略 / 成绩分段规则 / 样本状态路由 / 单轮 I2 / I6 的跨轮切换</strong>。只在未见题的独立能力、旧能力保持和多轮有效收益上作主要结论。</p>
 <h3>Go / Merge / Stop</h3>
 <div class="table-wrap"><table><thead><tr><th>裁决</th><th>预先需要的证据</th></tr></thead><tbody>
 <tr><td>继续 I6</td><td>自然失败中能稳定观察到瓶颈主导关系变化；跨轮诊断比静态规则和等预算 I2/样本路由有可重复的独立收益。</td></tr>
 <tr><td>并入 I2</td><td>收益完全由单轮试学/上下文 bandit 解释，诊断历史与瓶颈切换并无增量信息。</td></tr>
 <tr><td>停止或缩题</td><td>瓶颈不可辨、切换成本超过收益、优势只在当前题/保留提示时出现，或旧能力/安全回归无法通过。</td></tr>
 </tbody></table></div>
 <p class="status">状态：研究假设与实验方案；截至 2026-10-27 尚未开展 I6 的受控实验，图表不含虚构成绩。</p>


## 历史草案：跨轮瓶颈诊断（原 I6） / 安全与实验口径：成绩上升不等于 RSI 成立


 <p>所有 Probe 和候选更新先在受控环境运行，冻结外部独立验证器及任务划分；开发集可用于模式切换，最终测试只能在策略冻结后运行。相同初始状态的干预分支必须共享数据拆分、执行预算与可访问工具。多种模式一起改变时，要记录交互效应，不能把增益简单归因于单个原因。</p>
 <p><b>跨轮安全硬门：</b>验证器被绕过、Agent 越权执行、恶意轨迹写入长期 Skill/Memory、旧能力出现不可接受退化时拒绝晋级并保留回滚。这里是在给出安全协议要求，不是声称已经解决自进化安全。</p>
 <p><b>成功的定义：</b>移除教师、临时提示与多余在线计算后，允许保留的模型/Skill/Memory/Harness 版本在不同、未见的任务上仍能持续进步；不能用分数波动、一次 pass@k 提高、或增加测试调用替代能力增长。<a href="ideas.html">返回 I1–I5 研究主线</a> · <a href="experiments.html">现有实验协议</a>。</p>


## 实验方案与推进门槛 / 少量主环境，明确版本

<div class="table-wrap"><table><thead><tr><th>资产</th><th>角色</th><th>要求</th></tr></thead><tbody><tr><td>ToolSandbox <a class="cite" href="references.html#B01" title="ToolSandbox: A Stateful, Conversational, Interactive Evaluation Benchmark for LLM Tool Use Capabilities">[B01]</a></td><td>状态依赖、缺信息、工具流程的机制实验。</td><td>先跑官方基线；派生训练任务单独命名，按根任务族去重划分。</td></tr><tr><td>τ 系列文本交互 <a class="cite" href="references.html#B02" title="τ-bench / τ²-bench：官方仓库与版本化评测协议">[B02]</a></td><td>规则遵循、用户交互、领域迁移。</td><td>锁定 commit、任务 manifest、模拟器和文本协议；当前 main 不与历史 τ² 表混用。</td></tr><tr><td>Terminal-Bench 2.1 <a class="cite" href="references.html#B03" title="Terminal-Bench 2.1">[B03]</a></td><td>冻结外部测试。</td><td>固定容器、工具、网络、verifier；不进入课程或元奖励。</td></tr><tr><td>ModularRSI 资源 <a class="cite" href="references.html#S09" title="ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement">[S09]</a></td><td>可执行编辑的候选训练来源。</td><td>先审查许可及任务/仓库重叠；本地预检待做。</td></tr><tr><td>Qwen3.5-9B / 27B <a class="cite" href="references.html#B04" title="Qwen3.5-9B">[B04]</a><a class="cite" href="references.html#B05" title="Qwen3.5-27B">[B05]</a></td><td>主学习者与规模对照；9B 可初始化控制器。</td><td>冻结权重 revision、采样模式、上下文和额度。</td></tr><tr><td>Gemma 4 31B IT <a class="cite" href="references.html#B06" title="Gemma 4 31B instruction-tuned">[B06]</a></td><td>跨家族验证。</td><td>先过工具解析和基础成功率预检；服务兼容问题不当能力缺陷。</td></tr></tbody></table></div><p>这是<strong>官方页面核对过的候选资产</strong>，不是已经跑通的组合；选型为保证可比性，不声称最新最强。首轮暂不引入 GUI 与具身平台，减少额外环境故障。</p>

## 实验方案与推进门槛 / 先固定“学习发生在哪里”

<div class="table-wrap"><table><thead><tr><th>轨道</th><th>允许写入</th><th>后测复位</th><th>允许结论</th></tr></thead><tbody><tr><td>A · 系统学习</td><td>有长度上限的技能、Harness 或记忆。</td><td>清空任务对话，只装载版本化产物。</td><td>系统持久适应，不称权重增长。</td></tr><tr><td>B · 参数学习</td><td>固定配置 LoRA 等更新。</td><td>清空对话、示范与新增技能；同基础 Harness。</td><td>参数载体的保持与迁移。</td></tr><tr><td>C · 上下文对照</td><td>只保留会话。</td><td>分别保留 / 清空上下文。</td><td>定位暂时适应与答案泄漏。</td></tr></tbody></table></div><p>先做 A，B 检验跨持久载体成立与否；分轨报告。共享 GEPA 或固定编辑模型可减少实现，编辑器差异不能混入支持策略贡献。<a class="cite" href="references.html#S03" title="GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning">[S03]</a><a class="cite" href="references.html#S04" title="Self-Adapting Language Models (SEAL)">[S04]</a><a class="cite" href="references.html#S07" title="Harness-R1: Learning to Edit Executable Runtime Harnesses from Agent Failure Trajectories">[S07]</a></p>

## 实验方案与推进门槛 / P0：一个足以否定主线的问题

<p><b>即时最优帮助，是否经常不是延迟独立能力最优帮助？</b>若排序基本一致，就没有理由先训练复杂长程策略。</p><p><b>计划规模：</b>一个环境、12 个原始任务族、2 个学习者、4 个支持条件、3 个重复，共 <code>12×2×4×3=288</code> 个学习分支。各分支用 2 个近迁移、2 个远迁移、2 个旧能力探针，即时和两次干扰后各测一次，共 <code>288×6×2=3,456</code> 次后测。训练、干扰、前测另计。这是计划数，不是已有数据。</p><p>先在 4 族做管线预检，再扩展。任务族是独立统计单位，多个 Probe 不是多个独立样本。用开发集选支持动作、用另一批 Probe 评分，避免同一噪声既选冠军又评价冠军。只在人工故障上出现则不进入大规模 RL。</p>

## 实验方案与推进门槛 / 数据隔离：不止一个 Held-out

<div class="flow"><div><b>D_train</b><small>练习与候选生成</small></div><div><b>D_meta</b><small>训练元策略的延迟奖励</small></div><div><b>D_gate</b><small>版本选择与停止</small></div><div><b>D_test</b><small>最终冻结评测</small></div></div><p>按根任务、模板、仓库、语义近重复分组隔离，不随机打散同模板。课程生成器不可读测试答案、verifier、轨迹。反复查询的 D_gate 也会过拟合；记录次数，使用滚动窗口或预限频次，不永远称其未见。</p><p>新任务、新模型、新错误机制分别评价；换几个参数不等于跨机制泛化。旧正确任务必须进入回归评估，正常与困难任务都展示。</p>

## 实验方案与推进门槛 / 主实验与强基线

<div class="table-wrap"><table><thead><tr><th>对照</th><th>保持一致</th><th>排除解释</th></tr></thead><tbody><tr><td>无更新、强示范、固定渐隐</td><td>学习器和后测。</td><td>简单教学规则足够。</td></tr><tr><td>学习进展 bandit / ActiveSaddler 风格</td><td>轨迹、编辑器、任务、预算。</td><td>只是课程选择收益。<a class="cite" href="references.html#M03" title="Automated Curriculum Learning for Neural Networks">[M03]</a><a class="cite" href="references.html#M04" title="Teacher-Student Curriculum Learning (TSCL)">[M04]</a><a class="cite" href="references.html#S16" title="ActiveSaddler: Automated Curriculum Learning for Agent Harness Optimization">[S16]</a></td></tr><tr><td>短程教学 / SOAR 风格学习奖励</td><td>教师、可用支持动作。</td><td>近迁移目标已充分。<a class="cite" href="references.html#S17" title="Teaching Models to Teach Themselves: Reasoning at the Edge of Learnability (SOAR)">[S17]</a><a class="cite" href="references.html#S19" title="The Assistance Dilemma: Learning to Teach via Multi-Turn Reinforcement Learning">[S19]</a></td></tr><tr><td>同容量预测器 + contextual bandit</td><td>全部数据与特征，不故意减配。</td><td>复杂结构没必要。</td></tr><tr><td>普通多采样 / 顺序精修</td><td>累计推理和执行预算。</td><td>额外计算带来提升。<a class="cite" href="references.html#S14" title="Rethinking the Evaluation of Harness Evolution for Agents">[S14]</a></td></tr><tr><td>冻结元策略、打乱历史、重置学习者</td><td>底层仍允许更新。</td><td>误把任务能力当元能力。</td></tr></tbody></table></div><p>改造基线标成“基于原方法的本环境适配版”，披露复现差异；不能拿论文原表与新环境结果横比。</p><p>完整实验建议起点：2 个学习者 × 2 个环境 × 4 个核心策略 × 5 条独立学习流 × 8 轮 = <code>640</code> 个更新轮。每轮含多次执行，不是 640 次调用。第三家族用于冻结外推，不重复全部调参。</p>

## 实验方案与推进门槛 / 指标、统计与总成本

<div class="table-wrap"><table><thead><tr><th>指标</th><th>定义</th></tr></thead><tbody><tr><td>即时 / 延迟独立增益</td><td>清空任务对话后比较新旧版；延迟按干扰更新定义。</td></tr><tr><td>近 / 远迁移</td><td>同机制新实例与新组合、机制分开，报告族覆盖。</td></tr><tr><td>回归与净收益</td><td>原成功变失败比例和所有任务总增益同时报。</td></tr><tr><td>Meta-reset 曲线</td><td>重置相同学习者，仅改变元策略，比较等预算曲线。</td></tr><tr><td>帮助依赖</td><td>有无帮助差值仅作诊断；小差值可能两边都失败。</td></tr><tr><td>选择 regret / 校准</td><td>在独立分叉数据上评价选动作损失及预测误差。</td></tr><tr><td>总成本</td><td>训练 GPU 时、Token、教师、verifier、环境调用与墙钟时间。</td></tr></tbody></table></div><p>成对任务流与随机种子；按族/流聚类区间，报告每条流。预定主终点和检查点，负迁移与失败修改全部保留。元训练成本与部署摊销分开，不能隐去前期数据生成。</p>

## 实验方案与推进门槛 / 实现的数据契约

<pre><code>{
  "learner_revision": "weight-and-artifact-hash",
  "meta_policy_revision": "policy-hash",
  "task_family": "grouped-before-splitting",
  "split": "train | meta | gate | test",
  "environment_revision": "commit-and-image-digest",
  "parent_state_id": "shared-by-paired-branches",
  "intervention": {"support": "hint", "update": "skill"},
  "environment_seed": 0, "update_seed": 0,
  "persistent_artifact_hash": "post-update-hash",
  "teacher_visible_at_test": false,
  "intervening_updates": [],
  "independent_outcomes": {}, "regressions": [],
  "cost": {"tokens": 0, "gpu_seconds": 0, "env_calls": 0}
}</code></pre><p>这是 schema 示意，零值不是测量。真实运行保存复位检查、解析错误、验证器版本、失败证据与随机分配记录。只在授权沙箱执行，编辑器不得改最终审计代码。</p>

## 实验方案与推进门槛 / 新候选 I5：教学反馈自进化的独立实验轨道

<p>独立候选 <a href="teaching.html"><b>I5：Learner-Induced Blindspot Discovery</b></a> 不仅需要学生得到更高分，更需要 Student 的独立应用能触发<strong>对 Teacher 本身的可验证技能修正</strong>。</p><p>前两周先按 <code>Teacher T0</code>、<code>Student S0/S1/S2</code> 四臂执行，在相同环境与调用预算下定位知识/表达/学生容量/环境问题；P0 必须对比 Teacher Self-Probe、Self-Reflection、NeurIPS 2024 LbT 和教师→学生技能蒸馏。详见方法页中的 24 个任务族预实验与否定条件。<a class="cite" href="references.html#S20" title="Can LLMs Learn by Teaching for Better Reasoning? A Preliminary Study">[S20]</a><a class="cite" href="references.html#S22" title="SKILL-KD: Contrastive Skill Distillation for LLM Agents">[S22]</a><a class="cite" href="references.html#E09" title="Learning by Teaching Human Pupils and Teachable Agents: The Importance of Recursive Feedback">[E09]</a></p><p>这条路线不与 I1 原有的“支持渐隐”实验直接混成一个分数。后续仅在 Student 反馈相比 Teacher 自探更有独特信息、教师自己确实改善时，才尝试学习元级教学策略。</p>

## 实验方案与推进门槛 / I2：师生共进化的独立验证轨道

<p><b>首要问题：</b>教师的教法能否跟随学生成长而改进？第一阶段固定伙伴、教材、教师参考知识和教学顺序，不同时改变课程或更新表面。</p><p>先在相同学生快照上做等预算试教，真实更新后清空课堂上下文测新题；保留学生能力，并用真实学习反馈更新教师的教学策略。原有任务 Skill 写入器作为系统学习轨道；教学 LoRA 与解题 LoRA 的双参数更新作为独立轨道，不混合解释。</p><p><b>三项决定性实验：</b>不同学生阶段的教法收益排序；教师版本 × 冻结学生快照的交叉教学；固定教师、仅上下文适应、固定学生库训练教师与当前学生反馈驱动教师的等总成本比较。</p><p>教师的开发奖励集与最终审计严格隔离；全部学生副本训练、教师更新、诊断和后测计入预算。当前仅为方案整理，未开始本项目训练。<a href="idea-i2.html#experiments">查看 I2 完整实验和基线</a>。</p>

## 实验方案与推进门槛 / 按最短证据路径推进

<div class="timeline-rsi"><div><b>第 1 周</b><p>固定版本、官方基线、4 族预检；核验最近邻运行资产。</p></div><div><b>第 2 周</b><p>P0 分叉与统计，筛查 I1 / I2。没有自然失败证据则停。</p></div><div><b>第 3–4 周</b><p>只训练一个核心策略，加入强简单基线，扩第二环境。</p></div><div><b>第 5–6 周</b><p>冻结方法，跨模型、Meta-reset、消融，同步形成初稿。</p></div><div><b>缓冲</b><p>独立重跑、失败案例、来源及许可；证据不足就延长。</p></div></div><div class="note">这是执行目标，不是实验已启动或六周必能投稿的承诺。先判断固定强基线是否足够，比先实现庞大系统更接近明确论文。</div>

## 来源与核验记录 / 核验口径与检索范围

<p>本专题的基础综述始于 2026-10-21；I1–I5 新增最近邻于 2026-10-27 增量核验。定向覆盖 RSI、学习型改进器、课程/元学习、学习科学及实验资源。用论文标题、方法词与引用链交叉检索，优先 arXiv、会议页面、作者机构和官方仓库。</p><p><b>阅读深度不同：</b>“正文方法”表示核对了方法/实验设置，不等于逐条复现全部结果；“摘要”只支持摘要范围的陈述；“官方资源”只确认资产与文档存在。代码入口存在不等于依赖安装、运行、原表重现成功。</p><p><b>原始材料与本次研究：</b>用户分享的推文用于确定入口和问题，不把推文统计或数字自动当作原论文结论。新提案、框架与优先级属于本专题分析，均非文献已经证明的结果。</p><p><b>搜索主题：</b>recursive self-improvement / harness optimization / meta-learning / automated curriculum / learning progress / learner modeling / assistance dilemma / fading / retrieval practice / productive failure / interference replay / skill withdrawal / learning response / selective rehearsal / active failure probing / partner selection / co-distillation。</p><div class="note">这是针对选题的证据地图，不是穷尽全部文献的系统综述。未能核对的作者、发表状态、代码可运行性不补写；预印本标注月份。链接会随论文修订与仓库更新变化，实验须另锁 commit / revision。</div><div class="links"><a class="link-btn" href="sources.json" download>下载来源 JSON</a><a class="link-btn" href="sources.tsv" download>下载来源 TSV</a><a class="link-btn" href="research-notes.md" download>下载整篇研究笔记</a></div>

## 来源与核验记录 / RSI · 61 项

<article class="source-card" id="S01"><div class="source-meta"><span class="ref-id">S01</span><span>arXiv 26.07</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/2607.07663" target="_blank" rel="noopener noreferrer">Recursive Self-Improvement in AI: From Bounded Self-Refinement to Autonomous Research Loops</a></h3><p>按修改对象和闭环程度整理 RSI；用于界定范围，不把一种严格定义当成全领域共识。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2607.07663" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S02"><div class="source-meta"><span class="ref-id">S02</span><span>arXiv 25.05；核对 v3</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/2505.22954" target="_blank" rel="noopener noreferrer">Darwin Godel Machine: Open-Ended Evolution of Self-Improving Agents</a></h3><p>维护代码谱系，以任务执行评价自修改版本；代码自进化与开放式搜索已有系统基础。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2505.22954" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S03"><div class="source-meta"><span class="ref-id">S03</span><span>ICLR 2026 Oral；arXiv 25.07</span><span class="evidence">摘要与官方仓库核对</span></div><h3><a href="https://arxiv.org/abs/2507.19457" target="_blank" rel="noopener noreferrer">GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning</a></h3><p>反思执行轨迹，提出并测试提示修改、组合互补经验；可作共享编辑器和强搜索基线。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2507.19457" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/gepa-ai/gepa" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S04"><div class="source-meta"><span class="ref-id">S04</span><span>arXiv 25.06</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/2506.10943" target="_blank" rel="noopener noreferrer">Self-Adapting Language Models (SEAL)</a></h3><p>生成微调数据和更新指令，以更新后模型表现学习自编辑；属于参数持久更新。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2506.10943" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S05"><div class="source-meta"><span class="ref-id">S05</span><span>arXiv 26.03</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/2603.19461" target="_blank" rel="noopener noreferrer">Hyperagents</a></h3><p>任务 Agent 与修改它的 Meta-Agent 同在可编辑程序中；双层循环本身不再是充分创新。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2603.19461" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S06"><div class="source-meta"><span class="ref-id">S06</span><span>arXiv 26.07</span><span class="evidence">正文方法核对</span></div><h3><a href="https://arxiv.org/abs/2607.05297" target="_blank" rel="noopener noreferrer">MetaSkill-Evolve: Recursive Self-Improvement of LLM Agents via Two-Timescale Meta-Skill Evolution</a></h3><p>快慢时间尺度分别更新任务技能与元技能；与泛化的“改进器积累经验”直接相邻。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2607.05297" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S07"><div class="source-meta"><span class="ref-id">S07</span><span>arXiv 26.08</span><span class="evidence">摘要与官方仓库核对</span></div><h3><a href="https://arxiv.org/abs/2608.02276" target="_blank" rel="noopener noreferrer">Harness-R1: Learning to Edit Executable Runtime Harnesses from Agent Failure Trajectories</a></h3><p>训练专门的 Harness 编辑器，以真实执行表现优化修改；学习生成补丁不是新的空白。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2608.02276" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/DeepExperience/Harness-R1" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S08"><div class="source-meta"><span class="ref-id">S08</span><span>arXiv 26.09</span><span class="evidence">正文方法核对</span></div><h3><a href="https://arxiv.org/abs/2609.35738" target="_blank" rel="noopener noreferrer">Harness Learning Enables Generalizable Test-Time Adaptation</a></h3><p>把 Harness 修改作为元学习问题，学习可迁移适应策略；需比较新任务学习过程。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2609.35738" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S09"><div class="source-meta"><span class="ref-id">S09</span><span>arXiv 26.09</span><span class="evidence">正文方法与官方仓库核对</span></div><h3><a href="https://arxiv.org/abs/2609.14857" target="_blank" rel="noopener noreferrer">ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement</a></h3><p>成败轨迹对照、模块化修改与独立任务迁移；上述三项组合不能直接当作新方向。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2609.14857" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/IQuestLab/ModularRSI" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S10"><div class="source-meta"><span class="ref-id">S10</span><span>arXiv 26.09；核对 26.10 修订摘要</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/2609.24972" target="_blank" rel="noopener noreferrer">RRSI: Regularized Recursive Self-Improvement of Agent Harnesses</a></h3><p>正则化修改提议和选择，缓解递归搜索过拟合；不同修订的实验数字不混用。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2609.24972" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S11"><div class="source-meta"><span class="ref-id">S11</span><span>arXiv 26.09</span><span class="evidence">摘要与项目入口核对</span></div><h3><a href="https://arxiv.org/abs/2609.14858" target="_blank" rel="noopener noreferrer">Dream-RSI: Recursive Self-Improvement through Evolving Worlds</a></h3><p>利用历史发现树回放优化探索策略；回放覆盖范围之外的收益需真实执行验证。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2609.14858" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/zhengkid/Dream-RSI" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S12"><div class="source-meta"><span class="ref-id">S12</span><span>arXiv 26.10</span><span class="evidence">正文方法与官方仓库核对</span></div><h3><a href="https://arxiv.org/abs/2610.14224" target="_blank" rel="noopener noreferrer">Harness²: Recursive Agent Harnessing for an Open World</a></h3><p>任务内修改与跨任务 Harnessing 经验积累；行为对比不等于带标准答案的正确性证明。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2610.14224" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/google-research/harness2" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S13"><div class="source-meta"><span class="ref-id">S13</span><span>arXiv 26.10</span><span class="evidence">摘要与官方仓库核对</span></div><h3><a href="https://arxiv.org/abs/2610.13912" target="_blank" rel="noopener noreferrer">RSI-Anything: Unlocking Recursive Self-Improvement with World Models</a></h3><p>预测行动后果，再以真实反馈校正；环境动力学与学习者更新后能力变化是不同对象。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2610.13912" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/Gen-Verse/RSI-Anything" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S14"><div class="source-meta"><span class="ref-id">S14</span><span>arXiv 26.07</span><span class="evidence">摘要与官方仓库核对</span></div><h3><a href="https://arxiv.org/abs/2607.12227" target="_blank" rel="noopener noreferrer">Rethinking the Evaluation of Harness Evolution for Agents</a></h3><p>强调与等反馈、等推理预算的普通采样和顺序精修比较；复杂流程不能只按得分解释。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2607.12227" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/rethinking-harness-evolution/code" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S15"><div class="source-meta"><span class="ref-id">S15</span><span>arXiv 26.10</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/2610.14662" target="_blank" rel="noopener noreferrer">Does Failure Feedback Direct Agent Self-Modification?</a></h3><p>目标修复、相关失败迁移和独立测试增益须分开；反馈效果具有模型依赖性。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2610.14662" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S16"><div class="source-meta"><span class="ref-id">S16</span><span>arXiv 26.10</span><span class="evidence">正文方法与实验设置核对</span></div><h3><a href="https://arxiv.org/html/2610.00906v1" target="_blank" rel="noopener noreferrer">ActiveSaddler: Automated Curriculum Learning for Agent Harness Optimization</a></h3><p>失败模式作为动态 bandit 臂，以学习进展调整优先级并探索新失败；直接覆盖自动修复课程。</p><div class="links"><a class="link-btn" href="https://arxiv.org/html/2610.00906v1" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S17"><div class="source-meta"><span class="ref-id">S17</span><span>arXiv 26.01；核对 v3</span><span class="evidence">正文方法与实验设置核对</span></div><h3><a href="https://arxiv.org/html/2601.18778v3" target="_blank" rel="noopener noreferrer">Teaching Models to Teach Themselves: Reasoning at the Edge of Learnability (SOAR)</a></h3><p>双层元强化学习让教师出题，以学生在困难题上的实际进步作奖励，而非仅用难度代理。</p><div class="links"><a class="link-btn" href="https://arxiv.org/html/2601.18778v3" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S18"><div class="source-meta"><span class="ref-id">S18</span><span>arXiv 26.10</span><span class="evidence">正文方法与实验设置核对</span></div><h3><a href="https://arxiv.org/html/2610.04604v1" target="_blank" rel="noopener noreferrer">Anticipating the Consequences of Curriculum Decisions with Large Language Models</a></h3><p>将学习进展、下游迁移潜力和当前可学性结合；任务依赖图与前瞻课程已有近邻。</p><div class="links"><a class="link-btn" href="https://arxiv.org/html/2610.04604v1" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/Octavio-Pappalardo/curriculum-foresight" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S19"><div class="source-meta"><span class="ref-id">S19</span><span>arXiv 26.10</span><span class="evidence">正文方法与实验设置核对</span></div><h3><a href="https://arxiv.org/html/2610.06446v1" target="_blank" rel="noopener noreferrer">The Assistance Dilemma: Learning to Teach via Multi-Turn Reinforcement Learning</a></h3><p>遮蔽教师话语的近迁移后测仍保留学生话语；单题回报难覆盖支持撤除的远期价值。</p><div class="links"><a class="link-btn" href="https://arxiv.org/html/2610.06446v1" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/eth-lre/EduardoRL" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S20"><div class="source-meta"><span class="ref-id">S20</span><span>NeurIPS 2024；arXiv 24.06</span><span class="evidence">会议正文与官方仓库核对</span></div><h3><a href="https://proceedings.neurips.cc/paper_files/paper/2024/hash/8340b085045cf13f1f0b6c2c4cc0a89c-Abstract-Conference.html" target="_blank" rel="noopener noreferrer">Can LLMs Learn by Teaching for Better Reasoning? A Preliminary Study</a></h3><p>教师解释根据学生反馈选择；反馈可以构成 DPO 训练偏好；多学生多样性是已有近邻。不能把 teacher 由 student feedback 更新称作首次提出。</p><div class="links"><a class="link-btn" href="https://proceedings.neurips.cc/paper_files/paper/2024/hash/8340b085045cf13f1f0b6c2c4cc0a89c-Abstract-Conference.html" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/imagination-research/lbt" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S21"><div class="source-meta"><span class="ref-id">S21</span><span>AAAI 2026</span><span class="evidence">会议摘要与方法概述核对</span></div><h3><a href="https://ojs.aaai.org/index.php/AAAI/article/view/38668" target="_blank" rel="noopener noreferrer">MARS: Multi-Agent Adaptive Reasoning with Socratic Guidance for Automated Prompt Optimization</a></h3><p>Teacher-Critic-Student Socratic dialogue 用于提示优化；多智能体教学及问题驱动迭代不能单独作为方法创新。</p><div class="links"><a class="link-btn" href="https://ojs.aaai.org/index.php/AAAI/article/view/38668" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S22"><div class="source-meta"><span class="ref-id">S22</span><span>arXiv 26.07</span><span class="evidence">摘要与作者公开说明核对</span></div><h3><a href="https://arxiv.org/abs/2607.28048" target="_blank" rel="noopener noreferrer">SKILL-KD: Contrastive Skill Distillation for LLM Agents</a></h3><p>对比教师成功与学生失败轨迹，迭代修改学生的技能；本候选必须与“更新教师自己”区分，并避免只做反向技能蒸馏。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2607.28048" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S23"><div class="source-meta"><span class="ref-id">S23</span><span>arXiv 26.08</span><span class="evidence">论文正文与摘要核对</span></div><h3><a href="https://arxiv.org/abs/2608.20274" target="_blank" rel="noopener noreferrer">Break It Down, Pass It On: Cross-Task Skill Transfer in LLM Agents</a></h3><p>子任务级和任务级技能、文本与代码技能对跨任务迁移有不同影响；要求本候选与直接细粒度技能归纳和静态技能质量评价比较。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2608.20274" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S24"><div class="source-meta"><span class="ref-id">S24</span><span>arXiv 25.12</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/2512.13102" target="_blank" rel="noopener noreferrer">Socratic Students: Teaching Language Models to Learn by Asking Questions</a></h3><p>训练学生主动询问教师以改善学生的学习效率；不能把会追问的 Student 当作空白，需证明问题对 Teacher 自身能力有独立信息。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2512.13102" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S25"><div class="source-meta"><span class="ref-id">S25</span><span>arXiv 23.11</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/2311.06985" target="_blank" rel="noopener noreferrer">Large Language Models are In-context Teachers for Knowledge Reasoning</a></h3><p>提出 Self-Explain 和 Teach-Back 来提高学生的 in-context knowledge reasoning；Teach-Back 名称本身不保证与教师自进化相关。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2311.06985" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S26"><div class="source-meta"><span class="ref-id">S26</span><span>arXiv 26.10</span><span class="evidence">原始摘要核对；2026-10-27</span></div><h3><a href="https://arxiv.org/abs/2610.22740" target="_blank" rel="noopener noreferrer">R²Orch: Recursive Self-Improvement for Agent Orchestration via Self-Play within a Skill-Internalization Loop</a></h3><p>通过自博弈将经验蒸馏为技能再内化进参数；以撤掉技能后效果是否保持决定 Skill Withdrawal。I1 研究何时该内化、何时保留外部支持。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2610.22740" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S27"><div class="source-meta"><span class="ref-id">S27</span><span>arXiv 26.07</span><span class="evidence">正文方法核对；2026-10-27</span></div><h3><a href="https://arxiv.org/abs/2607.21419" target="_blank" rel="noopener noreferrer">PATS: Policy-Aware Training Scaffolding for Agentic Reinforcement Learning</a></h3><p>针对当前策略调整训练时支架，冗余时压缩或撤除，部署时不保留支架。I1 不能把随能力渐隐提示当成首次提出。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2607.21419" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/shi-yipeng/PATS" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S28"><div class="source-meta"><span class="ref-id">S28</span><span>arXiv 26.10</span><span class="evidence">原始摘要核对；2026-10-27</span></div><h3><a href="https://arxiv.org/abs/2610.21791" target="_blank" rel="noopener noreferrer">RSIFlow: Adaptive Self-Improvement Workflows with an Evolving Meta-Agent</a></h3><p>依据任务轨迹和反馈诊断瓶颈，选择模型、Harness 或产物更新流程，并改进 Meta-Agent。I2 需聚焦同一更新对象内部的学习方法反应。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2610.21791" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/1HUAN1/RSI-Flow" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S29"><div class="source-meta"><span class="ref-id">S29</span><span>arXiv 26.08</span><span class="evidence">原始摘要核对；2026-10-27</span></div><h3><a href="https://arxiv.org/abs/2608.19013" target="_blank" rel="noopener noreferrer">Harness Continual Learning: Continual Adaptation Beyond Model Parameters</a></h3><p>Harness 更新前检查新进步、历史保持和有效性，提出 harness-level forgetting。I3 应区分主动冲突巩固与事后守门。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2608.19013" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S30"><div class="source-meta"><span class="ref-id">S30</span><span>arXiv 26.07</span><span class="evidence">原始摘要核对；2026-10-27</span></div><h3><a href="https://arxiv.org/abs/2607.26643" target="_blank" rel="noopener noreferrer">Rethinking Self-Evolution: A Constrained Exploration-Exploitation Process for Mitigating Skill Overfitting (SkillBoost)</a></h3><p>结合结构化故障定位、候选探索与回归约束决定是否接受 Skill 修改。I3 研究保留有用新更新时怎样定向修复旧技能冲突。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2607.26643" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S31"><div class="source-meta"><span class="ref-id">S31</span><span>EMNLP 2026；arXiv 26.03</span><span class="evidence">会议摘要核对；2026-10-27</span></div><h3><a href="https://aclanthology.org/2026.emnlp-main.758/" target="_blank" rel="noopener noreferrer">Trace2Skill: Distill Trajectory-Local Lessons into Transferable Agent Skills</a></h3><p>并行分析多条执行轨迹，归纳为可复用且尽量无冲突的技能。I4 不是再次强调多轨迹，而是决定何时需要追加辨别实验、何时证据足够归纳。</p><div class="links"><a class="link-btn" href="https://aclanthology.org/2026.emnlp-main.758/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/Qwen-Applications/Trace2Skill" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S32"><div class="source-meta"><span class="ref-id">S32</span><span>arXiv 26.05</span><span class="evidence">原文机制及附录计算口径核对；2026-10-27；未复现</span></div><h3><a href="https://arxiv.org/abs/2605.16727" target="_blank" rel="noopener noreferrer">PopuLoRA: Co-Evolving LLM Populations for Reasoning Self-Play</a></h3><p>教师/学生独立 LoRA 群体通过匹配、自博弈和交叉评估更新，并带权重空间进化。按每适配器匹配训练量；1.31倍墙钟不能理解为相同总计算量。I5固定互教更新器，检验撤伴后的双向净学习收益。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2605.16727" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S33"><div class="source-meta"><span class="ref-id">S33</span><span>arXiv 26.06</span><span class="evidence">原文 Section 3、实验域与限制核对；2026-10-27；未复现</span></div><h3><a href="https://arxiv.org/abs/2606.14368" target="_blank" rel="noopener noreferrer">Be My Tutor: On-Policy Co-Distillation for Mutual LLM Improvement via Peer Feedback (OPCoD)</a></h3><p>双模型通过受门控同伴反馈进行 on-policy 自蒸馏，self-teacher同时以自身正确rollout和同伴反馈为条件；Science Q&amp;A验证不自动外推到十模型数学/代码。I5采用固定适配底座，单独比较伙伴关系。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2606.14368" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S34"><div class="source-meta"><span class="ref-id">S34</span><span>arXiv 26.07</span><span class="evidence">此前原始摘要核对；2026-10-27本轮正文页面访问受限</span></div><h3><a href="https://arxiv.org/abs/2607.11250" target="_blank" rel="noopener noreferrer">Multi-Agent LLMs Fail to Explore Each Other (MACE: Multi-Agent Contextual Exploration)</a></h3><p>以结构化同伴选择促进探索和协作任务表现；I5 必须区分当前协作收益与伙伴退出后的独立能力增长，且不与同名记忆方法混淆。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2607.11250" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/deeplearning-wisc/mace" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S35"><div class="source-meta"><span class="ref-id">S35</span><span>ICLR 2025</span><span class="evidence">ICLR 官方摘要核对；2026-10-27</span></div><h3><a href="https://proceedings.iclr.cc/paper_files/paper/2025/hash/63943ee9fe347f3d95892cf87d9a42e6-Abstract-Conference.html" target="_blank" rel="noopener noreferrer">Mind the Gap: Examining the Self-Improvement Capabilities of Large Language Models</a></h3><p>研究生成—验证差距与反复自我提升的条件。I6 不能将生成/验证/更新拆分称为首次，而应验证跨轮瓶颈变化及选择收益。</p><div class="links"><a class="link-btn" href="https://proceedings.iclr.cc/paper_files/paper/2025/hash/63943ee9fe347f3d95892cf87d9a42e6-Abstract-Conference.html" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S36"><div class="source-meta"><span class="ref-id">S36</span><span>arXiv 26.09</span><span class="evidence">arXiv 原始摘要核对；2026-10-27</span></div><h3><a href="https://arxiv.org/abs/2609.34327" target="_blank" rel="noopener noreferrer">Knowing When Thinking Is Not Enough: Teaching Small Reasoning Models to Reason Beyond Their Parametric Knowledge (FlyBy)</a></h3><p>通过中途干预区分知识与执行瓶颈，训练小模型选择性向更强模型查询；不等于持续参数/Skill 更新后的跨轮学习模式切换。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2609.34327" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S37"><div class="source-meta"><span class="ref-id">S37</span><span>ACL 2026</span><span class="evidence">ACL 官方摘要核对；2026-10-27</span></div><h3><a href="https://aclanthology.org/2026.acl-long.1393/" target="_blank" rel="noopener noreferrer">Why Supervised Fine-Tuning Fails to Learn: A Systematic Study of Incomplete Learning in Large Language Models</a></h3><p>分析训练数据未被吸收的五类原因，并对 SFT 不完全学习执行有针对性的干预；与 I6 的吸收检查高度重合。</p><div class="links"><a class="link-btn" href="https://aclanthology.org/2026.acl-long.1393/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S38"><div class="source-meta"><span class="ref-id">S38</span><span>COLM 2026</span><span class="evidence">COLM 官方摘要核对；2026-10-27</span></div><h3><a href="https://proceedings.colm.cc/paper_files/paper/2026/hash/9cdb4f8c4dfa13284d2d5a6e7853e5a2-Abstract-Conference.html" target="_blank" rel="noopener noreferrer">Unifying Group-Relative and Self-Distillation Policy Optimization via Sample Routing (SRPO)</a></h3><p>按采样结果将 GRPO 和自蒸馏组合，并针对训练阶段稳定性做调权；I6 需证明跨环节诊断的额外价值。</p><div class="links"><a class="link-btn" href="https://proceedings.colm.cc/paper_files/paper/2026/hash/9cdb4f8c4dfa13284d2d5a6e7853e5a2-Abstract-Conference.html" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S39"><div class="source-meta"><span class="ref-id">S39</span><span>EMNLP 2026</span><span class="evidence">ACL Anthology 官方摘要核对；2026-10-27</span></div><h3><a href="https://aclanthology.org/2026.emnlp-main.464/" target="_blank" rel="noopener noreferrer">From Rollouts to Recipes: Self-Contained Post-Training for LLMs</a></h3><p>按正确率与置信度路由 GRPO、自蒸馏、正则或跳过，路由比例随训练改变；I6 最接近的动态配方基线之一。</p><div class="links"><a class="link-btn" href="https://aclanthology.org/2026.emnlp-main.464/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S40"><div class="source-meta"><span class="ref-id">S40</span><span>ACL 2025</span><span class="evidence">ACL 正式论文摘要与方法流程核对</span></div><h3><a href="https://aclanthology.org/2025.acl-long.417/" target="_blank" rel="noopener noreferrer">Self-Error-Instruct: Generalizing from Errors for LLMs Mathematical Reasoning</a></h3><p>从模型错题聚类错误类型、合成数据，并用 one-shot 效果筛选微调数据；I8 不能声称首次按错误类型发现迁移价值。</p><div class="links"><a class="link-btn" href="https://aclanthology.org/2025.acl-long.417/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S41"><div class="source-meta"><span class="ref-id">S41</span><span>Findings of EMNLP 2026</span><span class="evidence">ACL Anthology 正式论文摘要核对</span></div><h3><a href="https://aclanthology.org/2026.findings-emnlp.1924/" target="_blank" rel="noopener noreferrer">RULE-EDIT: Benchmarking Rule-Level Knowledge Editing in Large Language Models</a></h3><p>验证数学抽象规则的直接编辑可能不迁移到实例；其知识编辑设置不直接等同于 SFT 或 LoRA 纠错。</p><div class="links"><a class="link-btn" href="https://aclanthology.org/2026.findings-emnlp.1924/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S42"><div class="source-meta"><span class="ref-id">S42</span><span>EMNLP 2026</span><span class="evidence">ACL Anthology 正式论文摘要核对</span></div><h3><a href="https://aclanthology.org/2026.emnlp-main.421/" target="_blank" rel="noopener noreferrer">Editing Rules in LLMs Requires More Than a Localized Update</a></h3><p>提出多层分布式规则编辑，不同形式的规则知识对应不同表示层；说明公式记忆与实例应用的编辑一致性并非自动成立。</p><div class="links"><a class="link-btn" href="https://aclanthology.org/2026.emnlp-main.421/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S43"><div class="source-meta"><span class="ref-id">S43</span><span>arXiv 25.10</span><span class="evidence">arXiv 摘要核对</span></div><h3><a href="https://arxiv.org/abs/2510.08696" target="_blank" rel="noopener noreferrer">Don&#x27;t Waste Mistakes: Leveraging Negative RL-Groups via Confidence Reweighting</a></h3><p>LENS 对高置信度错误增加惩罚以利用 GRPO 全错组，属于 RL 更新信号设计，并不直接预测一次错题的跨题学习收益。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2510.08696" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S44"><div class="source-meta"><span class="ref-id">S44</span><span>arXiv 26.02</span><span class="evidence">arXiv 摘要核对</span></div><h3><a href="https://arxiv.org/abs/2602.21420" target="_blank" rel="noopener noreferrer">Overconfident Errors Need Stronger Correction: Asymmetric Confidence Penalties for Reinforcement Learning</a></h3><p>ACE 利用相对参考策略的置信度位移调整错误 rollout 惩罚；与预测规则级净迁移收益的选题相邻但不相同。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2602.21420" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S45"><div class="source-meta"><span class="ref-id">S45</span><span>Findings ACL 2026</span><span class="evidence">ACL Anthology 正式摘要核对；2026-10-27</span></div><h3><a href="https://aclanthology.org/2026.findings-acl.171/" target="_blank" rel="noopener noreferrer">SPaCe: Unlocking Sample-Efficient Large Language Models Training With Self-Pace Curriculum Learning</a></h3><p>按聚类难度、解题率和学习进展用 bandit 调度训练样本；I6 不能将按学习速率换题当作新意。</p><div class="links"><a class="link-btn" href="https://aclanthology.org/2026.findings-acl.171/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S46"><div class="source-meta"><span class="ref-id">S46</span><span>ICLR 2026</span><span class="evidence">ICLR 2026 正式 PDF 与作者仓库核对；2026-10-27</span></div><h3><a href="https://openreview.net/pdf?id=bOwVr0yr7r" target="_blank" rel="noopener noreferrer">Scaf-GRPO: Scaffolded Group Relative Policy Optimization for Enhancing LLM Reasoning</a></h3><p>检测独立学习平台期，在训练中引入由抽象到具体的分级提示恢复非零学习信号；I6 需比较换提示以外的行动。</p><div class="links"><a class="link-btn" href="https://openreview.net/pdf?id=bOwVr0yr7r" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/JIA-Lab-research/Scaf-GRPO" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S47"><div class="source-meta"><span class="ref-id">S47</span><span>ICML 2026</span><span class="evidence">PMLR 正式摘要与书目信息核对；2026-10-27</span></div><h3><a href="https://proceedings.mlr.press/v306/sundaram26a.html" target="_blank" rel="noopener noreferrer">Teaching Models to Teach Themselves: Reasoning at the Edge of Learnability (SOAR)</a></h3><p>通过自博弈生成练习题、以学生实际困难题能力提升训练教师，缓解极难题零奖励平台期；I6 不重复动态出题。</p><div class="links"><a class="link-btn" href="https://proceedings.mlr.press/v306/sundaram26a.html" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S48"><div class="source-meta"><span class="ref-id">S48</span><span>Findings EMNLP 2026</span><span class="evidence">ACL Anthology 正式摘要核对；2026-10-27</span></div><h3><a href="https://aclanthology.org/2026.findings-emnlp.105/" target="_blank" rel="noopener noreferrer">BEACON: Bayesian Optimal Stopping for Efficient LLM Sampling</a></h3><p>依据额外采样的预期收益与成本停止推理候选生成；与训练后独立能力的跨轮停止决策不同。</p><div class="links"><a class="link-btn" href="https://aclanthology.org/2026.findings-emnlp.105/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S49"><div class="source-meta"><span class="ref-id">S49</span><span>Findings EMNLP 2026</span><span class="evidence">ACL Anthology 正式摘要核对；2026-10-27</span></div><h3><a href="https://aclanthology.org/2026.findings-emnlp.1168/" target="_blank" rel="noopener noreferrer">STRETCH the Boundaries: A Unified Self-Taught Framework for Progressive LLM Evolution</a></h3><p>根据当前解题能力动态生成挑战，缓解固定难度导致的自学习停滞；未直接区分换方法与暂缓后重访的因果收益。</p><div class="links"><a class="link-btn" href="https://aclanthology.org/2026.findings-emnlp.1168/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S90"><div class="source-meta"><span class="ref-id">S90</span><span>arXiv 26.10</span><span class="evidence">作者论文与官方项目页核对；2026-10-27</span></div><h3><a href="https://arxiv.org/abs/2610.16078" target="_blank" rel="noopener noreferrer">Heterogeneous Agentic Coevolution (HACE)</a></h3><p>专用模型与 LLM Agent 的互惠学习，且通过进化 Harness 调整数据交换与训练样本；I5 不能声称首次异构共进化，须证明十模型间动态接触关系的独立收益。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2610.16078" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://wenqian-ye.github.io/hace/" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S100"><div class="source-meta"><span class="ref-id">S100</span><span>Nature Communications 2026；2026-01-07</span><span class="evidence">原文 arXiv v3 方法与作者官方说明核对；2026-10-27</span></div><h3><a href="https://www.nature.com/articles/s41467-025-67998-6" target="_blank" rel="noopener noreferrer">Bayesian teaching enables probabilistic reasoning in large language models</a></h3><p>学生 SFT 模仿规范 Bayesian 预测行为，在所测推荐任务中优于 Oracle 监督并展示跨任务迁移；不是显式思维链教学，也不是可更新教师与学生的共同进化。公开正文：https://arxiv.org/html/2503.17523v3</p><div class="links"><a class="link-btn" href="https://www.nature.com/articles/s41467-025-67998-6" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S101"><div class="source-meta"><span class="ref-id">S101</span><span>arXiv 2025-06；作者官方项目</span><span class="evidence">正文奖励、蒸馏阶段与局限核对；2026-10-27</span></div><h3><a href="https://arxiv.org/abs/2506.08388" target="_blank" rel="noopener noreferrer">Reinforcement Learning Teachers of Test Time Scaling (RLT)</a></h3><p>用题目与答案训练教师生成适合学生的解释；奖励含学生条件概率与分布差异项，之后做学生蒸馏。论文局限明确未探索教师学生并行训练。I2 比较持续教学更新及真实后测奖励。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2506.08388" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/SakanaAI/RLT" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S102"><div class="source-meta"><span class="ref-id">S102</span><span>arXiv 2026-05；本轮未核实正式会议状态</span><span class="evidence">原始正文方法核对；2026-10-27</span></div><h3><a href="https://arxiv.org/abs/2605.26872" target="_blank" rel="noopener noreferrer">The Strongest Teacher Is Not Always the Best Teacher: Student-Centric Answer Selection (SCAS)</a></h3><p>依据学生相关的学习成本代理，从已验证正确的教师输出中选监督；强教师不必给出最有用的训练答案。I2 不把答案选择或教师强弱比较声称为新机制。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2605.26872" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S103"><div class="source-meta"><span class="ref-id">S103</span><span>arXiv 2026-10-06 预印本</span><span class="evidence">正文 Sec. 2.1–2.3 冻结学生与奖励定义核对；2026-10-27</span></div><h3><a href="https://arxiv.org/html/2610.08778" target="_blank" rel="noopener noreferrer">Sherpa: Teaching LLMs to Teach Adaptively</a></h3><p>多轮 RL 训练教师适应不同模拟学生，学生骨干冻结，收益来自上下文中的当前题表现；不等于学生跨轮参数持续更新。I2 需控制静态教师本已有的上下文适应能力。</p><div class="links"><a class="link-btn" href="https://arxiv.org/html/2610.08778" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S104"><div class="source-meta"><span class="ref-id">S104</span><span>作者研究报告 2026-05-14；不标作会议论文</span><span class="evidence">作者报告 Sec. 2–3 方法与早期实验口径核对；2026-10-27</span></div><h3><a href="https://noahziems.com/pedagogical-rl" target="_blank" rel="noopener noreferrer">Pedagogical RL: Teaching Models to Teach Themselves from Privileged Information</a></h3><p>用特权信息和当前学生的轨迹可吸收性代理训练自教师，再以 surprisal-gated imitation 更新学生；已经覆盖教得可学与学生吸收，I2 必须检验持续跟踪学习反应的独立作用。</p><div class="links"><a class="link-btn" href="https://noahziems.com/pedagogical-rl" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S200"><div class="source-meta"><span class="ref-id">S200</span><span>NeurIPS 2024 · Main Conference Track</span><span class="evidence">NeurIPS 官方发表页与摘要核对；2026-10-27；未复现</span></div><h3><a href="https://proceedings.neurips.cc/paper_files/paper/2024/hash/1c2b1c8f7d317719a9ce32dd7386ba35-Abstract-Conference.html" target="_blank" rel="noopener noreferrer">Coevolving with the Other You: Fine-Tuning LLM with Sequential Cooperative Multi-Agent Reinforcement Learning (CORY)</a></h3><p>Pioneer 与 Observer 两个模型联合 RL，并周期性交换角色；I5 不把双模型共训练或角色交换作为新颖性，固定对内教学协议后研究群体配对。</p><div class="links"><a class="link-btn" href="https://proceedings.neurips.cc/paper_files/paper/2024/hash/1c2b1c8f7d317719a9ce32dd7386ba35-Abstract-Conference.html" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S201"><div class="source-meta"><span class="ref-id">S201</span><span>AAMAS 2026 SE Workshop；不是主会</span><span class="evidence">官方 Workshop 录用名单、题录与检索摘要核对；正文网页访问受限；2026-10-27</span></div><h3><a href="https://openreview.net/forum?id=Q2zS4ZHjJ0" target="_blank" rel="noopener noreferrer">LLM Agents Learn Effective Partner Selection for Mutual Cooperation in Social Dilemmas</a></h3><p>社会困境中的动态伙伴关系与合作。发表状态已由 SE @ AAMAS 2026 官方 accepted-papers 页面确认；本次不补写无法核验的网络规模、参数共享或精确重连超参，不作为知识互教效果的直接证据。</p><div class="links"><a class="link-btn" href="https://openreview.net/forum?id=Q2zS4ZHjJ0" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S202"><div class="source-meta"><span class="ref-id">S202</span><span>arXiv 26.09 · v1</span><span class="evidence">原文 Section 3 路由与 Agent 更新、反馈定义核对；2026-10-27；未复现</span></div><h3><a href="https://arxiv.org/html/2609.18779v1" target="_blank" rel="noopener noreferrer">CERA-MoA: Co-Evolving Routing Mechanisms with Continually Learning LLM Agents</a></h3><p>隐藏状态熟悉度支持动态样本路由，路由与各 Agent 策略共同更新。I5 需与当前表现路由比较，并隔离伙伴关系与任务分发两个变量；不能声称首次动态路由共进化。</p><div class="links"><a class="link-btn" href="https://arxiv.org/html/2609.18779v1" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S203"><div class="source-meta"><span class="ref-id">S203</span><span>ACL 2026 · Long Papers</span><span class="evidence">ACL 官方摘要与发表记录核对；2026-10-27；未复现</span></div><h3><a href="https://aclanthology.org/2026.acl-long.2044/" target="_blank" rel="noopener noreferrer">Nature-Inspired Population-Based Evolution of Large Language Models (GENOME / GENOME+)</a></h3><p>以模型权重交叉、变异、选择和继承进行群体进化；I5 以各自持续训练和文本互教为边，不用群体人数或能力组合本身声称创新。</p><div class="links"><a class="link-btn" href="https://aclanthology.org/2026.acl-long.2044/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/ZhangYiqun018/GENOME" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S204"><div class="source-meta"><span class="ref-id">S204</span><span>ICLR 2026 · Conference</span><span class="evidence">ICLR 官方状态与 arXiv 2510.06410v2 的方法/结论核对；2026-10-27</span></div><h3><a href="https://proceedings.iclr.cc/paper_files/paper/2026/hash/93f3ac5bb6d24ed7cec95ae11209ca34-Abstract-Conference.html" target="_blank" rel="noopener noreferrer">Off-Trajectory Reasoning: Can LLMs Collaborate on Reasoning Trajectories?</a></h3><p>区分从错误外部轨迹恢复与利用正确引导；solo 分数不能代表协作轨迹可用性。为 I5 提供可传性与负迁移检查，不证明所有互教训练都无效。</p><div class="links"><a class="link-btn" href="https://proceedings.iclr.cc/paper_files/paper/2026/hash/93f3ac5bb6d24ed7cec95ae11209ca34-Abstract-Conference.html" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S205"><div class="source-meta"><span class="ref-id">S205</span><span>arXiv 26.02；本轮未确认会议版本</span><span class="evidence">原始摘要与方法描述核对；2026-10-27；未复现</span></div><h3><a href="https://arxiv.org/abs/2602.13103" target="_blank" rel="noopener noreferrer">R-Diverse: Mitigating Diversity Illusion in Self-Play LLM Training</a></h3><p>跨轮记忆和技能层面多样性用于缓解 self-play 表面多样而底层重复；I5 应以验证过的技能覆盖测群体同质化。本轮不沿用尚未核验的 ICML 录用标签。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2602.13103" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/Gengsheng-Li/R-Diverse" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article>

## 来源与核验记录 / 相邻领域 · 14 项

<article class="source-card" id="M01"><div class="source-meta"><span class="ref-id">M01</span><span>arXiv 16.06</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/1606.04474" target="_blank" rel="noopener noreferrer">Learning to learn by gradient descent by gradient descent</a></h3><p>学习优化算法而非只优化任务模型；更新规则可作为学习对象，但不提供通用 RSI 保证。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/1606.04474" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="M02"><div class="source-meta"><span class="ref-id">M02</span><span>arXiv 16.11</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/1611.02779" target="_blank" rel="noopener noreferrer">RL²: Fast Reinforcement Learning via Slow Reinforcement Learning</a></h3><p>跨任务训练快速适应算法；启发重置学习者、保留元策略的检验。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/1611.02779" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="M03"><div class="source-meta"><span class="ref-id">M03</span><span>arXiv 17.04</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/1704.03003" target="_blank" rel="noopener noreferrer">Automated Curriculum Learning for Neural Networks</a></h3><p>用非平稳 bandit 和学习进度选择训练数据；难度改为进展并非新颖机制。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/1704.03003" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="M04"><div class="source-meta"><span class="ref-id">M04</span><span>arXiv 17.07</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/1707.00183" target="_blank" rel="noopener noreferrer">Teacher-Student Curriculum Learning (TSCL)</a></h3><p>优先练习进步快的子任务，也重访性能下降的任务；学习和防遗忘联合调度已有经典基线。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/1707.00183" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/tambetm/TSCL" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="M05"><div class="source-meta"><span class="ref-id">M05</span><span>NeurIPS 2015</span><span class="evidence">会议原始摘要核对</span></div><h3><a href="https://papers.nips.cc/paper/5654-deep-knowledge-tracing" target="_blank" rel="noopener noreferrer">Deep Knowledge Tracing</a></h3><p>从学习交互序列估计学生知识状态；下一题正确率预测不等于某种教学干预的因果收益。</p><div class="links"><a class="link-btn" href="https://papers.nips.cc/paper/5654-deep-knowledge-tracing" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="M06"><div class="source-meta"><span class="ref-id">M06</span><span>NeurIPS 2018</span><span class="evidence">会议原始摘要核对</span></div><h3><a href="https://proceedings.neurips.cc/paper/2018/hash/8051a3c40561002834e59d566b7430cf-Abstract.html" target="_blank" rel="noopener noreferrer">Learning to Teach with Dynamic Loss Functions</a></h3><p>教师按学生阶段输出动态损失，以开发集表现优化教学；应迁移双层目标而非师生角色名称。</p><div class="links"><a class="link-btn" href="https://proceedings.neurips.cc/paper/2018/hash/8051a3c40561002834e59d566b7430cf-Abstract.html" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="M07"><div class="source-meta"><span class="ref-id">M07</span><span>arXiv 15.10</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/1510.03591" target="_blank" rel="noopener noreferrer">Dual Control for Approximate Bayesian Reinforcement Learning</a></h3><p>行动同时改变状态并揭示未知动力学；需验证诊断信息是否真正改变后续更新决策。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/1510.03591" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="M08"><div class="source-meta"><span class="ref-id">M08</span><span>ICLR 2016；arXiv 15.11</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/1511.05952" target="_blank" rel="noopener noreferrer">Prioritized Experience Replay</a></h3><p>按经验重要性非均匀重放；间隔练习方案必须排除普通优先重放即可解释收益。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/1511.05952" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="M09"><div class="source-meta"><span class="ref-id">M09</span><span>NeurIPS 2019；arXiv 19.08</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/1908.04742" target="_blank" rel="noopener noreferrer">Online Continual Learning with Maximally Interfered Retrieval</a></h3><p>选择可能被当前更新干扰的旧样本重放；作为干扰感知巩固的重要对照。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/1908.04742" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="M10"><div class="source-meta"><span class="ref-id">M10</span><span>ICML 2024</span><span class="evidence">PMLR 正式论文摘要核对</span></div><h3><a href="https://proceedings.mlr.press/v235/xia24c.html" target="_blank" rel="noopener noreferrer">LESS: Selecting Influential Data for Targeted Instruction Tuning</a></h3><p>以优化器感知的低秩梯度相似性估计训练数据影响力；I8 必须与之比较而非声称训练前价值预测全新。</p><div class="links"><a class="link-btn" href="https://proceedings.mlr.press/v235/xia24c.html" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="M11"><div class="source-meta"><span class="ref-id">M11</span><span>ICML 2025</span><span class="evidence">PMLR 正式论文摘要核对</span></div><h3><a href="https://proceedings.mlr.press/v267/kang25f.html" target="_blank" rel="noopener noreferrer">What Do Learning Dynamics Reveal About Generalization in LLM Mathematical Reasoning?</a></h3><p>用预记忆阶段的训练题表现解释泛化并改进数据筛选，说明原题正确与记住解题步骤不同；不直接等于更新前单错题净迁移预测。</p><div class="links"><a class="link-btn" href="https://proceedings.mlr.press/v267/kang25f.html" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="M12"><div class="source-meta"><span class="ref-id">M12</span><span>ICML 2017</span><span class="evidence">PMLR 正式摘要核对；2026-10-27</span></div><h3><a href="https://proceedings.mlr.press/v70/graves17a.html" target="_blank" rel="noopener noreferrer">Automated Curriculum Learning for Neural Networks</a></h3><p>使用学习进展反馈与非平稳多臂老虎机分配课程；说明学习速率驱动的训练预算调度早有直接前作。</p><div class="links"><a class="link-btn" href="https://proceedings.mlr.press/v70/graves17a.html" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="M13"><div class="source-meta"><span class="ref-id">M13</span><span>ICLR 2026</span><span class="evidence">ICLR 官方摘要和方法指标核对</span></div><h3><a href="https://proceedings.iclr.cc/paper_files/paper/2026/hash/edcd1aa172dceda2ea9d45a48f25d3e3-Abstract-Conference.html" target="_blank" rel="noopener noreferrer">Demystifying Supervision Data Generalization in Multimodal LMs (DATAPROPHET)</a></h3><p>在视觉语言模型跨数据集监督迁移中，训练前综合困惑度、相似性和多样性预测各数据集对目标基准的真实训练收益；候选单位是数据集而非当前模型单条错误。</p><div class="links"><a class="link-btn" href="https://proceedings.iclr.cc/paper_files/paper/2026/hash/edcd1aa172dceda2ea9d45a48f25d3e3-Abstract-Conference.html" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="M100"><div class="source-meta"><span class="ref-id">M100</span><span>ICLR 2018</span><span class="evidence">正式会议条目与原始摘要核对；2026-10-27</span></div><h3><a href="https://openreview.net/forum?id=HJewuJWCZ" target="_blank" rel="noopener noreferrer">Learning to Teach</a></h3><p>用学生反馈优化教师策略，已明确提出 teacher–student co-evolution。属于一般机器学习的先驱，而非 LLM 共进化首作；双边更新与双层优化本身不能作为 I2 新颖性。</p><div class="links"><a class="link-btn" href="https://openreview.net/forum?id=HJewuJWCZ" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article>

## 来源与核验记录 / 学习科学 · 26 项

<article class="source-card" id="E01"><div class="source-meta"><span class="ref-id">E01</span><span>Theory Into Practice, 2002</span><span class="evidence">理论综述与元数据核对</span></div><h3><a href="https://www.tandfonline.com/doi/abs/10.1207/s15430421tip4102_2" target="_blank" rel="noopener noreferrer">Becoming a Self-Regulated Learner: An Overview</a></h3><p>自我调节的前瞻、执行监控与反思是设计视角；不是增加三个 Agent 模块即可有效的证明。</p><div class="links"><a class="link-btn" href="https://www.tandfonline.com/doi/abs/10.1207/s15430421tip4102_2" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E02"><div class="source-meta"><span class="ref-id">E02</span><span>Journal of Memory and Language, 2005</span><span class="evidence">作者存档与摘要核对</span></div><h3><a href="https://www.columbia.edu/cu/psychology/metcalfe/PDFs/Metcalfe%20Kornell%202005.pdf" target="_blank" rel="noopener noreferrer">A Region of Proximal Learning model of study time allocation</a></h3><p>在尚未掌握且可取得进展的材料间分配时间；不等同于挑最难题，也不与其他近侧发展区理论混称。</p><div class="links"><a class="link-btn" href="https://www.columbia.edu/cu/psychology/metcalfe/PDFs/Metcalfe%20Kornell%202005.pdf" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E03"><div class="source-meta"><span class="ref-id">E03</span><span>Psychological Science, 2006</span><span class="evidence">原始研究摘要核对</span></div><h3><a href="https://pubmed.ncbi.nlm.nih.gov/16507066/" target="_blank" rel="noopener noreferrer">Test-enhanced learning: taking memory tests improves long-term retention</a></h3><p>比较练习性检索与重复阅读的保持效果；冻结模型需要持久写入才能形成跨会话学习。</p><div class="links"><a class="link-btn" href="https://pubmed.ncbi.nlm.nih.gov/16507066/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E04"><div class="source-meta"><span class="ref-id">E04</span><span>Psychological Science, 2008</span><span class="evidence">原始研究摘要核对</span></div><h3><a href="https://pubmed.ncbi.nlm.nih.gov/19076480/" target="_blank" rel="noopener noreferrer">Spacing effects in learning: a temporal ridgeline of optimal retention</a></h3><p>间隔效果依赖保持时长；机器实验应操纵中间学习和干扰，不假定静止参数随时间遗忘。</p><div class="links"><a class="link-btn" href="https://pubmed.ncbi.nlm.nih.gov/19076480/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E05"><div class="source-meta"><span class="ref-id">E05</span><span>Journal of Educational Psychology, 2003</span><span class="evidence">作者机构摘要核对</span></div><h3><a href="https://asu.elsevierpure.com/en/publications/transitioning-from-studying-examples-to-solving-problems-effects-/" target="_blank" rel="noopener noreferrer">Transitioning From Studying Examples to Solving Problems: Effects of Self-Explanation Prompts and Fading Worked-Out Steps</a></h3><p>研究例题到自主解题、逐步撤去步骤及自我解释；支持撤除是教学干预，不只是评测删提示。</p><div class="links"><a class="link-btn" href="https://asu.elsevierpure.com/en/publications/transitioning-from-studying-examples-to-solving-problems-effects-/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E06"><div class="source-meta"><span class="ref-id">E06</span><span>Learning: Research and Practice, 2015</span><span class="evidence">作者机构摘要核对</span></div><h3><a href="https://repository.nie.edu.sg/entities/publication/cd4409fb-a12f-476f-ad02-febbf9caa4cc" target="_blank" rel="noopener noreferrer">Learning from productive failure</a></h3><p>生成探索后进行知识整理巩固；关键在教学次序与整合，不是错误越多越好。</p><div class="links"><a class="link-btn" href="https://repository.nie.edu.sg/entities/publication/cd4409fb-a12f-476f-ad02-febbf9caa4cc" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E07"><div class="source-meta"><span class="ref-id">E07</span><span>Educational Psychology Review, 2007</span><span class="evidence">作者机构记录与论文摘要核对</span></div><h3><a href="https://act-r.psy.cmu.edu/?post_type=publications&amp;p=14210" target="_blank" rel="noopener noreferrer">Exploring the assistance dilemma in experiments with Cognitive Tutors</a></h3><p>何时、以何种程度帮助是教学设计问题；不能直接推出 LLM 上的有效性。</p><div class="links"><a class="link-btn" href="https://act-r.psy.cmu.edu/?post_type=publications&amp;p=14210" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E08"><div class="source-meta"><span class="ref-id">E08</span><span>Educational Psychologist, 2016</span><span class="evidence">作者机构摘要核对</span></div><h3><a href="https://repository.eduhk.hk/en/publications/examining-productive-failure-productive-success-unproductive-fail-5/" target="_blank" rel="noopener noreferrer">Examining productive failure, productive success, unproductive failure, and unproductive success in learning</a></h3><p>区分学习时表现与长期学习收益；用于提出测量问题，机器机制须另行验证。</p><div class="links"><a class="link-btn" href="https://repository.eduhk.hk/en/publications/examining-productive-failure-productive-success-unproductive-fail-5/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E09"><div class="source-meta"><span class="ref-id">E09</span><span>Journal of the Learning Sciences, 2013</span><span class="evidence">完整论文机制与实验设计核对</span></div><h3><a href="https://aaalab.stanford.edu/research/assets/papers/2013/Learning_by_teaching_human_pupils.pdf" target="_blank" rel="noopener noreferrer">Learning by Teaching Human Pupils and Teachable Agents: The Importance of Recursive Feedback</a></h3><p>Recursive Feedback 要求学生在新环境中自主使用所学以及教师把学生行为映射回自己的理解；人类机制不能直接视为 LLM 有效性。</p><div class="links"><a class="link-btn" href="https://aaalab.stanford.edu/research/assets/papers/2013/Learning_by_teaching_human_pupils.pdf" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E10"><div class="source-meta"><span class="ref-id">E10</span><span>Behaviormetrika, 2026</span><span class="evidence">正文摘要与研究设计核对</span></div><h3><a href="https://link.springer.com/article/10.1007/s41237-026-00294-9" target="_blank" rel="noopener noreferrer">Beyond prior knowledge: the predictive role of knowledge-building in tutor learning</a></h3><p>人类教师面对 teachable agent 追问时 knowledge-building 比 knowledge-telling 更具诊断意义，相关性结果不是 LLM 教学自进化的因果证据。</p><div class="links"><a class="link-btn" href="https://link.springer.com/article/10.1007/s41237-026-00294-9" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E11"><div class="source-meta"><span class="ref-id">E11</span><span>Journal of Experimental Psychology: General, 2003</span><span class="evidence">PubMed 论文摘要与书目信息核对；2026-10-27</span></div><h3><a href="https://pubmed.ncbi.nlm.nih.gov/14640846/" target="_blank" rel="noopener noreferrer">The Dynamics of Learning and Allocation of Study Time to a Region of Proximal Learning</a></h3><p>人类实验显示把有限学习时间分配给中等难度材料可能取得更高收益；用于提分/任务选择假设，不可直接当作 RSI 实证。</p><div class="links"><a class="link-btn" href="https://pubmed.ncbi.nlm.nih.gov/14640846/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E12"><div class="source-meta"><span class="ref-id">E12</span><span>Journal of Experimental Psychology: Learning, Memory, and Cognition, 2001</span><span class="evidence">PubMed 摘要与 DOI 核对</span></div><h3><a href="https://pubmed.ncbi.nlm.nih.gov/11713883/" target="_blank" rel="noopener noreferrer">Errors committed with high confidence are hypercorrected</a></h3><p>在人类事实知识回答中，高置信度错误得到正确反馈后更可能在复测中纠正；不是 LLM 的直接证据。</p><div class="links"><a class="link-btn" href="https://pubmed.ncbi.nlm.nih.gov/11713883/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E13"><div class="source-meta"><span class="ref-id">E13</span><span>Memory, 2018</span><span class="evidence">期刊摘要与 DOI 核对</span></div><h3><a href="https://pubmed.ncbi.nlm.nih.gov/29781391/" target="_blank" rel="noopener noreferrer">Hypercorrection of high-confidence errors in the classroom</a></h3><p>大学园艺课堂学生答题、报告置信度并接受正确反馈，后测观察到超纠正；不能直接解释为跨题规则迁移。</p><div class="links"><a class="link-btn" href="https://pubmed.ncbi.nlm.nih.gov/29781391/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E14"><div class="source-meta"><span class="ref-id">E14</span><span>Memory &amp; Cognition, 2014</span><span class="evidence">PubMed 摘要与 DOI 核对</span></div><h3><a href="https://pubmed.ncbi.nlm.nih.gov/23797971/" target="_blank" rel="noopener noreferrer">Prior knowledge is more predictive of error correction than subjective confidence</a></h3><p>领域已有知识与纠错关系强，置信度独立解释力小；可能是已有知识的代理指标，而非其全部因果机制。</p><div class="links"><a class="link-btn" href="https://pubmed.ncbi.nlm.nih.gov/23797971/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E15"><div class="source-meta"><span class="ref-id">E15</span><span>Educational Studies in Mathematics, 2022（2021 online）</span><span class="evidence">期刊正文摘要与出版时间核对</span></div><h3><a href="https://link.springer.com/article/10.1007/s10649-021-10084-7" target="_blank" rel="noopener noreferrer">School students’ confidence when answering diagnostic questions online</a></h3><p>在线数学诊断数据研究学生置信度、答题正确率及后续相似题表现；不等于 LLM 的真实权重更新。</p><div class="links"><a class="link-btn" href="https://link.springer.com/article/10.1007/s10649-021-10084-7" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E16"><div class="source-meta"><span class="ref-id">E16</span><span>Journal of Memory and Language, 2005</span><span class="evidence">期刊摘要与 ERIC 书目信息核对；2026-10-27</span></div><h3><a href="https://doi.org/10.1016/j.jml.2004.12.001" target="_blank" rel="noopener noreferrer">A Region of Proximal Learning model of study time allocation</a></h3><p>将学习选择与学习坚持区分开，以主观学习速率判断 jROL 解释何时停止当前材料；是人类认知证据，不是 LLM 停止训练的实验证明。</p><div class="links"><a class="link-btn" href="https://doi.org/10.1016/j.jml.2004.12.001" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E17"><div class="source-meta"><span class="ref-id">E17</span><span>Findings EMNLP 2026</span><span class="evidence">ACL Anthology 摘要及元信息核对；2026-10-27</span></div><h3><a href="https://aclanthology.org/2026.findings-emnlp.2209/" target="_blank" rel="noopener noreferrer">MetaCLASS: Metacognitive Coaching for Learning with Adaptive Self-regulation Support</a></h3><p>对话教学动作预测中，41.7% 轮次标注无需干预，而最佳模型仅在 6.6% 轮次预测不干预；反映教学动作偏差，不等于 RSI 停学收益。</p><div class="links"><a class="link-btn" href="https://aclanthology.org/2026.findings-emnlp.2209/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E18"><div class="source-meta"><span class="ref-id">E18</span><span>Nature Communications 9, article 1673 (2018)</span><span class="evidence">Nature Communications 官方全文（方法、结果、误导反馈条件）与 PubMed 书目信息核对；2026-10-27</span></div><h3><a href="https://www.nature.com/articles/s41467-018-03992-5" target="_blank" rel="noopener noreferrer">Knowledge acquisition is governed by striatal prediction errors</a></h3><p>Pine 等通过事实知识答题、0–100 置信度、正确/部分错误反馈及一周后复测，发现反馈引出的语义预测误差与后续记忆更新关联，腹侧纹状体等区域编码该信号；错误反馈也能改写原本正确的记忆。支持 I8 将经核验的信念冲突作为候选诊断信号，不证明 LLM 权重更新或跨题规则迁移。</p><div class="links"><a class="link-btn" href="https://www.nature.com/articles/s41467-018-03992-5" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E90"><div class="source-meta"><span class="ref-id">E90</span><span>Nature Communications 2019</span><span class="evidence">Nature Communications 正文与方法核对；2026-10-27</span></div><h3><a href="https://www.nature.com/articles/s41467-019-09452-y" target="_blank" rel="noopener noreferrer">Bridge ties bind collective memories</a></h3><p>16人网络每人4次轮换对话，只改变跨簇/簇内的先后次序；群体记忆对齐受次序影响，主总体收敛比较p约0.052；不是模型参数学习证据。</p><div class="links"><a class="link-btn" href="https://www.nature.com/articles/s41467-019-09452-y" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E91"><div class="source-meta"><span class="ref-id">E91</span><span>Nature Communications 2019</span><span class="evidence">Nature Communications 原文摘要与模拟结果核对；2026-10-27</span></div><h3><a href="https://www.nature.com/articles/s41467-019-12650-3" target="_blank" rel="noopener noreferrer">Clustering knowledge and dispersing abilities enhances collective problem solving in a network</a></h3><p>基于 Agent 的群体求解研究知识与能力在网络中的空间分布；支持分别操纵能力差距和专长互补，不能直接当作 LLM 动态换伴训练结果。</p><div class="links"><a class="link-btn" href="https://www.nature.com/articles/s41467-019-12650-3" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E92"><div class="source-meta"><span class="ref-id">E92</span><span>Nature Communications 2021</span><span class="evidence">Nature Communications 正文与实验分析核对；2026-10-27</span></div><h3><a href="https://www.nature.com/articles/s41467-021-23424-1" target="_blank" rel="noopener noreferrer">Modularity and composite diversity affect the collective gathering of information online</a></h3><p>真实在线信息搜索及预测任务，随机操纵群体多样性与模块化，观察独立和群体预测收益；不是持续权重更新。</p><div class="links"><a class="link-btn" href="https://www.nature.com/articles/s41467-021-23424-1" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E93"><div class="source-meta"><span class="ref-id">E93</span><span>Nature Communications 2026</span><span class="evidence">Nature Communications 论文正文与实验流程核对；2026-10-27</span></div><h3><a href="https://www.nature.com/articles/s41467-026-76113-2" target="_blank" rel="noopener noreferrer">Propagation and preservation of AI-discovered problem-solving strategies in human culture</a></h3><p>五代人机群体从上一代选择示范者；策略须新颖、可学、有可辨优势才能长久传播；不等于同一代十个模型双向更新。</p><div class="links"><a class="link-btn" href="https://www.nature.com/articles/s41467-026-76113-2" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E94"><div class="source-meta"><span class="ref-id">E94</span><span>Nature Human Behaviour 2025</span><span class="evidence">Nature Human Behaviour 原文方法核对；2026-10-27</span></div><h3><a href="https://www.nature.com/articles/s41562-025-02269-4" target="_blank" rel="noopener noreferrer">Feature-based reward learning shapes human social learning strategies</a></h3><p>六项人类实验n=1941，社会学习策略可随历史收益而改变；激励学习伙伴选择机制，但不能直接视为 RSI 训练实测。</p><div class="links"><a class="link-btn" href="https://www.nature.com/articles/s41562-025-02269-4" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E95"><div class="source-meta"><span class="ref-id">E95</span><span>npj Complexity 2025</span><span class="evidence">npj Complexity 原文模型与结果核对；2026-10-27</span></div><h3><a href="https://www.nature.com/articles/s44260-025-00058-8" target="_blank" rel="noopener noreferrer">Copy or collaborate? How networks impact collective problem solving</a></h3><p>基于群体求解模型区分模仿现有较优解与组合知识探新解，两者对群体平均收益与最佳解影响不同；并非真实 LLM 参数共进化。</p><div class="links"><a class="link-btn" href="https://www.nature.com/articles/s44260-025-00058-8" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E96"><div class="source-meta"><span class="ref-id">E96</span><span>Nature Communications 2026</span><span class="evidence">Nature Communications 正文实验分析核对；2026-10-27</span></div><h3><a href="https://www.nature.com/articles/s41467-026-77762-z" target="_blank" rel="noopener noreferrer">Payoff selectivity drives collective intelligence during dynamic resource tracking in humans</a></h3><p>621人动态群体资源追踪，可信收益信息使其选择性关注表现好的同伴且灵活重组信息流；属于合作表现而非新模型能力的长程学习。</p><div class="links"><a class="link-btn" href="https://www.nature.com/articles/s41467-026-77762-z" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E97"><div class="source-meta"><span class="ref-id">E97</span><span>教育学系统综述 2023</span><span class="evidence">系统综述摘要与学习流程核对；2026-10-27</span></div><h3><a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC10436097/" target="_blank" rel="noopener noreferrer">Effects of the Jigsaw method on student educational outcomes: systematic review and meta-analyses</a></h3><p>Jigsaw 包含临时专家组与原学习组的往返和互教；只是组织结构启发，不是动态伙伴匹配或 RSI 共进化的直接证据。</p><div class="links"><a class="link-btn" href="https://pmc.ncbi.nlm.nih.gov/articles/PMC10436097/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article>

## 来源与核验记录 / 实验资源 · 8 项

<article class="source-card" id="B01"><div class="source-meta"><span class="ref-id">B01</span><span>Findings of NAACL 2025；arXiv 24.08</span><span class="evidence">会议页面与官方介绍核对</span></div><h3><a href="https://aclanthology.org/2025.findings-naacl.65/" target="_blank" rel="noopener noreferrer">ToolSandbox: A Stateful, Conversational, Interactive Evaluation Benchmark for LLM Tool Use Capabilities</a></h3><p>带状态工具执行、用户模拟与轨迹里程碑；派生训练任务须与官方评测隔离。</p><div class="links"><a class="link-btn" href="https://aclanthology.org/2025.findings-naacl.65/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/apple/ToolSandbox" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="B02"><div class="source-meta"><span class="ref-id">B02</span><span>官方资源；核对 2026-10-21</span><span class="evidence">官方文档核对</span></div><h3><a href="https://github.com/sierra-research/tau2-bench" target="_blank" rel="noopener noreferrer">τ-bench / τ²-bench：官方仓库与版本化评测协议</a></h3><p>当前仓库持续演进，不能把 main 与论文 τ² 任务集混用；记录 commit、任务清单和模拟器。</p><div class="links"><a class="link-btn" href="https://github.com/sierra-research/tau2-bench" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/sierra-research/tau2-bench" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="B03"><div class="source-meta"><span class="ref-id">B03</span><span>官方资源；核对 2026-10-21</span><span class="evidence">官方仓库核对</span></div><h3><a href="https://github.com/harbor-framework/terminal-bench-2-1" target="_blank" rel="noopener noreferrer">Terminal-Bench 2.1</a></h3><p>可执行终端任务；固定容器、测试和超时，最终测试不得训练元策略。</p><div class="links"><a class="link-btn" href="https://github.com/harbor-framework/terminal-bench-2-1" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/harbor-framework/harbor" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="B04"><div class="source-meta"><span class="ref-id">B04</span><span>官方模型卡；核对 2026-10-21</span><span class="evidence">官方模型卡核对</span></div><h3><a href="https://huggingface.co/Qwen/Qwen3.5-9B" target="_blank" rel="noopener noreferrer">Qwen3.5-9B</a></h3><p>主学习者与元控制器初始化候选；工具解析、训练与吞吐尚待实际运行验证。</p><div class="links"><a class="link-btn" href="https://huggingface.co/Qwen/Qwen3.5-9B" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="B05"><div class="source-meta"><span class="ref-id">B05</span><span>官方模型资源；核对 2026-10-21</span><span class="evidence">官方模型目录核对</span></div><h3><a href="https://huggingface.co/Qwen/Qwen3.5-27B" target="_blank" rel="noopener noreferrer">Qwen3.5-27B</a></h3><p>同家族强模型对照；选型为保证可比性，不声称它是最新最强模型。</p><div class="links"><a class="link-btn" href="https://huggingface.co/Qwen/Qwen3.5-27B" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="B06"><div class="source-meta"><span class="ref-id">B06</span><span>官方模型卡；核对 2026-10-21</span><span class="evidence">官方模型卡核对</span></div><h3><a href="https://huggingface.co/google/gemma-4-31B-it" target="_blank" rel="noopener noreferrer">Gemma 4 31B instruction-tuned</a></h3><p>跨家族目标模型候选；固定工具与预算，并单独记录模型替换后的校准开销。</p><div class="links"><a class="link-btn" href="https://huggingface.co/google/gemma-4-31B-it" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="B07"><div class="source-meta"><span class="ref-id">B07</span><span>官方资源；核对 2026-10-21</span><span class="evidence">官方 README 与实验切分核对</span></div><h3><a href="https://github.com/StonyBrookNLP/appworld" target="_blank" rel="noopener noreferrer">AppWorld Benchmark: executable app-ecosystem agent tasks</a></h3><p>官方 train / dev / test_normal / test_challenge 严格隔离；后两者只能用于冻结终评，不得按任务反馈修改教学方法。</p><div class="links"><a class="link-btn" href="https://github.com/StonyBrookNLP/appworld" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/StonyBrookNLP/appworld" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="B200"><div class="source-meta"><span class="ref-id">B200</span><span>官方模型发布 2025-04-29；核对 2026-10-27</span><span class="evidence">官方发布页的模型规格核对；训练兼容性和本地资源未验证</span></div><h3><a href="https://qwenlm.github.io/blog/qwen3/" target="_blank" rel="noopener noreferrer">Qwen3: Think Deeper, Act Faster — official dense-model release</a></h3><p>确认 Qwen3-1.7B/4B/8B/14B/32B 的公开规格，支持既定五规模×两专长的十模型实验候选；不是最新性能推荐，不代表十模型可以同时装入当前显存。</p><div class="links"><a class="link-btn" href="https://qwenlm.github.io/blog/qwen3/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article>


## 原始来源

- [S01] Recursive Self-Improvement in AI: From Bounded Self-Refinement to Autonomous Research Loops · arXiv 26.07
  https://arxiv.org/abs/2607.07663
- [S02] Darwin Godel Machine: Open-Ended Evolution of Self-Improving Agents · arXiv 25.05；核对 v3
  https://arxiv.org/abs/2505.22954
- [S03] GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning · ICLR 2026 Oral；arXiv 25.07
  https://arxiv.org/abs/2507.19457
- [S04] Self-Adapting Language Models (SEAL) · arXiv 25.06
  https://arxiv.org/abs/2506.10943
- [S05] Hyperagents · arXiv 26.03
  https://arxiv.org/abs/2603.19461
- [S06] MetaSkill-Evolve: Recursive Self-Improvement of LLM Agents via Two-Timescale Meta-Skill Evolution · arXiv 26.07
  https://arxiv.org/abs/2607.05297
- [S07] Harness-R1: Learning to Edit Executable Runtime Harnesses from Agent Failure Trajectories · arXiv 26.08
  https://arxiv.org/abs/2608.02276
- [S08] Harness Learning Enables Generalizable Test-Time Adaptation · arXiv 26.09
  https://arxiv.org/abs/2609.35738
- [S09] ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement · arXiv 26.09
  https://arxiv.org/abs/2609.14857
- [S10] RRSI: Regularized Recursive Self-Improvement of Agent Harnesses · arXiv 26.09；核对 26.10 修订摘要
  https://arxiv.org/abs/2609.24972
- [S11] Dream-RSI: Recursive Self-Improvement through Evolving Worlds · arXiv 26.09
  https://arxiv.org/abs/2609.14858
- [S12] Harness²: Recursive Agent Harnessing for an Open World · arXiv 26.10
  https://arxiv.org/abs/2610.14224
- [S13] RSI-Anything: Unlocking Recursive Self-Improvement with World Models · arXiv 26.10
  https://arxiv.org/abs/2610.13912
- [S14] Rethinking the Evaluation of Harness Evolution for Agents · arXiv 26.07
  https://arxiv.org/abs/2607.12227
- [S15] Does Failure Feedback Direct Agent Self-Modification? · arXiv 26.10
  https://arxiv.org/abs/2610.14662
- [S16] ActiveSaddler: Automated Curriculum Learning for Agent Harness Optimization · arXiv 26.10
  https://arxiv.org/html/2610.00906v1
- [S17] Teaching Models to Teach Themselves: Reasoning at the Edge of Learnability (SOAR) · arXiv 26.01；核对 v3
  https://arxiv.org/html/2601.18778v3
- [S18] Anticipating the Consequences of Curriculum Decisions with Large Language Models · arXiv 26.10
  https://arxiv.org/html/2610.04604v1
- [S19] The Assistance Dilemma: Learning to Teach via Multi-Turn Reinforcement Learning · arXiv 26.10
  https://arxiv.org/html/2610.06446v1
- [M01] Learning to learn by gradient descent by gradient descent · arXiv 16.06
  https://arxiv.org/abs/1606.04474
- [M02] RL²: Fast Reinforcement Learning via Slow Reinforcement Learning · arXiv 16.11
  https://arxiv.org/abs/1611.02779
- [M03] Automated Curriculum Learning for Neural Networks · arXiv 17.04
  https://arxiv.org/abs/1704.03003
- [M04] Teacher-Student Curriculum Learning (TSCL) · arXiv 17.07
  https://arxiv.org/abs/1707.00183
- [M05] Deep Knowledge Tracing · NeurIPS 2015
  https://papers.nips.cc/paper/5654-deep-knowledge-tracing
- [M06] Learning to Teach with Dynamic Loss Functions · NeurIPS 2018
  https://proceedings.neurips.cc/paper/2018/hash/8051a3c40561002834e59d566b7430cf-Abstract.html
- [M07] Dual Control for Approximate Bayesian Reinforcement Learning · arXiv 15.10
  https://arxiv.org/abs/1510.03591
- [M08] Prioritized Experience Replay · ICLR 2016；arXiv 15.11
  https://arxiv.org/abs/1511.05952
- [M09] Online Continual Learning with Maximally Interfered Retrieval · NeurIPS 2019；arXiv 19.08
  https://arxiv.org/abs/1908.04742
- [E01] Becoming a Self-Regulated Learner: An Overview · Theory Into Practice, 2002
  https://www.tandfonline.com/doi/abs/10.1207/s15430421tip4102_2
- [E02] A Region of Proximal Learning model of study time allocation · Journal of Memory and Language, 2005
  https://www.columbia.edu/cu/psychology/metcalfe/PDFs/Metcalfe%20Kornell%202005.pdf
- [E03] Test-enhanced learning: taking memory tests improves long-term retention · Psychological Science, 2006
  https://pubmed.ncbi.nlm.nih.gov/16507066/
- [E04] Spacing effects in learning: a temporal ridgeline of optimal retention · Psychological Science, 2008
  https://pubmed.ncbi.nlm.nih.gov/19076480/
- [E05] Transitioning From Studying Examples to Solving Problems: Effects of Self-Explanation Prompts and Fading Worked-Out Steps · Journal of Educational Psychology, 2003
  https://asu.elsevierpure.com/en/publications/transitioning-from-studying-examples-to-solving-problems-effects-/
- [E06] Learning from productive failure · Learning: Research and Practice, 2015
  https://repository.nie.edu.sg/entities/publication/cd4409fb-a12f-476f-ad02-febbf9caa4cc
- [E07] Exploring the assistance dilemma in experiments with Cognitive Tutors · Educational Psychology Review, 2007
  https://act-r.psy.cmu.edu/?post_type=publications&p=14210
- [E08] Examining productive failure, productive success, unproductive failure, and unproductive success in learning · Educational Psychologist, 2016
  https://repository.eduhk.hk/en/publications/examining-productive-failure-productive-success-unproductive-fail-5/
- [B01] ToolSandbox: A Stateful, Conversational, Interactive Evaluation Benchmark for LLM Tool Use Capabilities · Findings of NAACL 2025；arXiv 24.08
  https://aclanthology.org/2025.findings-naacl.65/
- [B02] τ-bench / τ²-bench：官方仓库与版本化评测协议 · 官方资源；核对 2026-10-21
  https://github.com/sierra-research/tau2-bench
- [B03] Terminal-Bench 2.1 · 官方资源；核对 2026-10-21
  https://github.com/harbor-framework/terminal-bench-2-1
- [B04] Qwen3.5-9B · 官方模型卡；核对 2026-10-21
  https://huggingface.co/Qwen/Qwen3.5-9B
- [B05] Qwen3.5-27B · 官方模型资源；核对 2026-10-21
  https://huggingface.co/Qwen/Qwen3.5-27B
- [B06] Gemma 4 31B instruction-tuned · 官方模型卡；核对 2026-10-21
  https://huggingface.co/google/gemma-4-31B-it
- [S20] Can LLMs Learn by Teaching for Better Reasoning? A Preliminary Study · NeurIPS 2024；arXiv 24.06
  https://proceedings.neurips.cc/paper_files/paper/2024/hash/8340b085045cf13f1f0b6c2c4cc0a89c-Abstract-Conference.html
- [S21] MARS: Multi-Agent Adaptive Reasoning with Socratic Guidance for Automated Prompt Optimization · AAAI 2026
  https://ojs.aaai.org/index.php/AAAI/article/view/38668
- [S22] SKILL-KD: Contrastive Skill Distillation for LLM Agents · arXiv 26.07
  https://arxiv.org/abs/2607.28048
- [S23] Break It Down, Pass It On: Cross-Task Skill Transfer in LLM Agents · arXiv 26.08
  https://arxiv.org/abs/2608.20274
- [S24] Socratic Students: Teaching Language Models to Learn by Asking Questions · arXiv 25.12
  https://arxiv.org/abs/2512.13102
- [S25] Large Language Models are In-context Teachers for Knowledge Reasoning · arXiv 23.11
  https://arxiv.org/abs/2311.06985
- [E09] Learning by Teaching Human Pupils and Teachable Agents: The Importance of Recursive Feedback · Journal of the Learning Sciences, 2013
  https://aaalab.stanford.edu/research/assets/papers/2013/Learning_by_teaching_human_pupils.pdf
- [E10] Beyond prior knowledge: the predictive role of knowledge-building in tutor learning · Behaviormetrika, 2026
  https://link.springer.com/article/10.1007/s41237-026-00294-9
- [B07] AppWorld Benchmark: executable app-ecosystem agent tasks · 官方资源；核对 2026-10-21
  https://github.com/StonyBrookNLP/appworld
- [S26] R²Orch: Recursive Self-Improvement for Agent Orchestration via Self-Play within a Skill-Internalization Loop · arXiv 26.10
  https://arxiv.org/abs/2610.22740
- [S27] PATS: Policy-Aware Training Scaffolding for Agentic Reinforcement Learning · arXiv 26.07
  https://arxiv.org/abs/2607.21419
- [S28] RSIFlow: Adaptive Self-Improvement Workflows with an Evolving Meta-Agent · arXiv 26.10
  https://arxiv.org/abs/2610.21791
- [S29] Harness Continual Learning: Continual Adaptation Beyond Model Parameters · arXiv 26.08
  https://arxiv.org/abs/2608.19013
- [S30] Rethinking Self-Evolution: A Constrained Exploration-Exploitation Process for Mitigating Skill Overfitting (SkillBoost) · arXiv 26.07
  https://arxiv.org/abs/2607.26643
- [S31] Trace2Skill: Distill Trajectory-Local Lessons into Transferable Agent Skills · EMNLP 2026；arXiv 26.03
  https://aclanthology.org/2026.emnlp-main.758/
- [S32] PopuLoRA: Co-Evolving LLM Populations for Reasoning Self-Play · arXiv 26.05
  https://arxiv.org/abs/2605.16727
- [S33] Be My Tutor: On-Policy Co-Distillation for Mutual LLM Improvement via Peer Feedback (OPCoD) · arXiv 26.06
  https://arxiv.org/abs/2606.14368
- [S34] Multi-Agent LLMs Fail to Explore Each Other (MACE: Multi-Agent Contextual Exploration) · arXiv 26.07
  https://arxiv.org/abs/2607.11250
- [S35] Mind the Gap: Examining the Self-Improvement Capabilities of Large Language Models · ICLR 2025
  https://proceedings.iclr.cc/paper_files/paper/2025/hash/63943ee9fe347f3d95892cf87d9a42e6-Abstract-Conference.html
- [S36] Knowing When Thinking Is Not Enough: Teaching Small Reasoning Models to Reason Beyond Their Parametric Knowledge (FlyBy) · arXiv 26.09
  https://arxiv.org/abs/2609.34327
- [S37] Why Supervised Fine-Tuning Fails to Learn: A Systematic Study of Incomplete Learning in Large Language Models · ACL 2026
  https://aclanthology.org/2026.acl-long.1393/
- [S38] Unifying Group-Relative and Self-Distillation Policy Optimization via Sample Routing (SRPO) · COLM 2026
  https://proceedings.colm.cc/paper_files/paper/2026/hash/9cdb4f8c4dfa13284d2d5a6e7853e5a2-Abstract-Conference.html
- [S39] From Rollouts to Recipes: Self-Contained Post-Training for LLMs · EMNLP 2026
  https://aclanthology.org/2026.emnlp-main.464/
- [E11] The Dynamics of Learning and Allocation of Study Time to a Region of Proximal Learning · Journal of Experimental Psychology: General, 2003
  https://pubmed.ncbi.nlm.nih.gov/14640846/
- [E12] Errors committed with high confidence are hypercorrected · Journal of Experimental Psychology: Learning, Memory, and Cognition, 2001
  https://pubmed.ncbi.nlm.nih.gov/11713883/
- [E13] Hypercorrection of high-confidence errors in the classroom · Memory, 2018
  https://pubmed.ncbi.nlm.nih.gov/29781391/
- [E14] Prior knowledge is more predictive of error correction than subjective confidence · Memory & Cognition, 2014
  https://pubmed.ncbi.nlm.nih.gov/23797971/
- [E15] School students’ confidence when answering diagnostic questions online · Educational Studies in Mathematics, 2022（2021 online）
  https://link.springer.com/article/10.1007/s10649-021-10084-7
- [S40] Self-Error-Instruct: Generalizing from Errors for LLMs Mathematical Reasoning · ACL 2025
  https://aclanthology.org/2025.acl-long.417/
- [S41] RULE-EDIT: Benchmarking Rule-Level Knowledge Editing in Large Language Models · Findings of EMNLP 2026
  https://aclanthology.org/2026.findings-emnlp.1924/
- [S42] Editing Rules in LLMs Requires More Than a Localized Update · EMNLP 2026
  https://aclanthology.org/2026.emnlp-main.421/
- [S43] Don't Waste Mistakes: Leveraging Negative RL-Groups via Confidence Reweighting · arXiv 25.10
  https://arxiv.org/abs/2510.08696
- [S44] Overconfident Errors Need Stronger Correction: Asymmetric Confidence Penalties for Reinforcement Learning · arXiv 26.02
  https://arxiv.org/abs/2602.21420
- [M10] LESS: Selecting Influential Data for Targeted Instruction Tuning · ICML 2024
  https://proceedings.mlr.press/v235/xia24c.html
- [M11] What Do Learning Dynamics Reveal About Generalization in LLM Mathematical Reasoning? · ICML 2025
  https://proceedings.mlr.press/v267/kang25f.html
- [E16] A Region of Proximal Learning model of study time allocation · Journal of Memory and Language, 2005
  https://doi.org/10.1016/j.jml.2004.12.001
- [E17] MetaCLASS: Metacognitive Coaching for Learning with Adaptive Self-regulation Support · Findings EMNLP 2026
  https://aclanthology.org/2026.findings-emnlp.2209/
- [E18] Knowledge acquisition is governed by striatal prediction errors · Nature Communications 9, article 1673 (2018)
  https://www.nature.com/articles/s41467-018-03992-5
- [S45] SPaCe: Unlocking Sample-Efficient Large Language Models Training With Self-Pace Curriculum Learning · Findings ACL 2026
  https://aclanthology.org/2026.findings-acl.171/
- [S46] Scaf-GRPO: Scaffolded Group Relative Policy Optimization for Enhancing LLM Reasoning · ICLR 2026
  https://openreview.net/pdf?id=bOwVr0yr7r
- [S47] Teaching Models to Teach Themselves: Reasoning at the Edge of Learnability (SOAR) · ICML 2026
  https://proceedings.mlr.press/v306/sundaram26a.html
- [S48] BEACON: Bayesian Optimal Stopping for Efficient LLM Sampling · Findings EMNLP 2026
  https://aclanthology.org/2026.findings-emnlp.105/
- [S49] STRETCH the Boundaries: A Unified Self-Taught Framework for Progressive LLM Evolution · Findings EMNLP 2026
  https://aclanthology.org/2026.findings-emnlp.1168/
- [M12] Automated Curriculum Learning for Neural Networks · ICML 2017
  https://proceedings.mlr.press/v70/graves17a.html
- [M13] Demystifying Supervision Data Generalization in Multimodal LMs (DATAPROPHET) · ICLR 2026
  https://proceedings.iclr.cc/paper_files/paper/2026/hash/edcd1aa172dceda2ea9d45a48f25d3e3-Abstract-Conference.html
- [S90] Heterogeneous Agentic Coevolution (HACE) · arXiv 26.10
  https://arxiv.org/abs/2610.16078
- [E90] Bridge ties bind collective memories · Nature Communications 2019
  https://www.nature.com/articles/s41467-019-09452-y
- [E91] Clustering knowledge and dispersing abilities enhances collective problem solving in a network · Nature Communications 2019
  https://www.nature.com/articles/s41467-019-12650-3
- [E92] Modularity and composite diversity affect the collective gathering of information online · Nature Communications 2021
  https://www.nature.com/articles/s41467-021-23424-1
- [E93] Propagation and preservation of AI-discovered problem-solving strategies in human culture · Nature Communications 2026
  https://www.nature.com/articles/s41467-026-76113-2
- [E94] Feature-based reward learning shapes human social learning strategies · Nature Human Behaviour 2025
  https://www.nature.com/articles/s41562-025-02269-4
- [E95] Copy or collaborate? How networks impact collective problem solving · npj Complexity 2025
  https://www.nature.com/articles/s44260-025-00058-8
- [E96] Payoff selectivity drives collective intelligence during dynamic resource tracking in humans · Nature Communications 2026
  https://www.nature.com/articles/s41467-026-77762-z
- [E97] Effects of the Jigsaw method on student educational outcomes: systematic review and meta-analyses · 教育学系统综述 2023
  https://pmc.ncbi.nlm.nih.gov/articles/PMC10436097/
- [S100] Bayesian teaching enables probabilistic reasoning in large language models · Nature Communications 2026；2026-01-07
  https://www.nature.com/articles/s41467-025-67998-6
- [S101] Reinforcement Learning Teachers of Test Time Scaling (RLT) · arXiv 2025-06；作者官方项目
  https://arxiv.org/abs/2506.08388
- [S102] The Strongest Teacher Is Not Always the Best Teacher: Student-Centric Answer Selection (SCAS) · arXiv 2026-05；本轮未核实正式会议状态
  https://arxiv.org/abs/2605.26872
- [S103] Sherpa: Teaching LLMs to Teach Adaptively · arXiv 2026-10-06 预印本
  https://arxiv.org/html/2610.08778
- [S104] Pedagogical RL: Teaching Models to Teach Themselves from Privileged Information · 作者研究报告 2026-05-14；不标作会议论文
  https://noahziems.com/pedagogical-rl
- [M100] Learning to Teach · ICLR 2018
  https://openreview.net/forum?id=HJewuJWCZ
- [S200] Coevolving with the Other You: Fine-Tuning LLM with Sequential Cooperative Multi-Agent Reinforcement Learning (CORY) · NeurIPS 2024 · Main Conference Track
  https://proceedings.neurips.cc/paper_files/paper/2024/hash/1c2b1c8f7d317719a9ce32dd7386ba35-Abstract-Conference.html
- [S201] LLM Agents Learn Effective Partner Selection for Mutual Cooperation in Social Dilemmas · AAMAS 2026 SE Workshop；不是主会
  https://openreview.net/forum?id=Q2zS4ZHjJ0
- [S202] CERA-MoA: Co-Evolving Routing Mechanisms with Continually Learning LLM Agents · arXiv 26.09 · v1
  https://arxiv.org/html/2609.18779v1
- [S203] Nature-Inspired Population-Based Evolution of Large Language Models (GENOME / GENOME+) · ACL 2026 · Long Papers
  https://aclanthology.org/2026.acl-long.2044/
- [S204] Off-Trajectory Reasoning: Can LLMs Collaborate on Reasoning Trajectories? · ICLR 2026 · Conference
  https://proceedings.iclr.cc/paper_files/paper/2026/hash/93f3ac5bb6d24ed7cec95ae11209ca34-Abstract-Conference.html
- [S205] R-Diverse: Mitigating Diversity Illusion in Self-Play LLM Training · arXiv 26.02；本轮未确认会议版本
  https://arxiv.org/abs/2602.13103
- [B200] Qwen3: Think Deeper, Act Faster — official dense-model release · 官方模型发布 2025-04-29；核对 2026-10-27
  https://qwenlm.github.io/blog/qwen3/
