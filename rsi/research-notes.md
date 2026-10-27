# RSI × 自主学习研究

核验日期：2026-10-27

本文件包含证据综述与待验证提案，不包含本项目实验结果。

## RSI × 自主学习研究 / 当前研究池：I1–I8 八个问题

<p>我们关心的不只是 Agent 能不能在一次任务里拿到更高分，而是：<strong>它能不能通过改写自身 Skill、Memory、Harness 或参数，真正学会下一次如何学得更好？</strong></p>
<div class="idea-board">
<a class="idea-board-card" href="ideas.html#idea-1"><span class="idea-id">I1 · 脚手架学习</span><b>哪些该自己学会，哪些用时再查？</b></a>
<a class="idea-board-card" href="ideas.html#idea-2"><span class="idea-id">I2 · 因材施教</span><b>同样犯错，怎么选适合自己的学习方法？</b></a>
<a class="idea-board-card" href="ideas.html#idea-3"><span class="idea-id">I3 · 温故知新</span><b>新方法有用却伤了旧能力，怎么办？</b></a>
<a class="idea-board-card" href="ideas.html#idea-4"><span class="idea-id">I4 · 生产性失败</span><b>失败一次就总结，还是再试几次？</b></a>
<a class="idea-board-card" href="ideas.html#idea-5"><span class="idea-id">I5 · 费曼学习法</span><b>和谁一起学，自己进步最快？</b></a>
<a class="idea-board-card" href="idea-i6-failure-value.html"><span class="idea-id">I6 · 错误轨迹</span><b>同题都答错，为什么有些失败过程更值得学习？</b></a>
<a class="idea-board-card" href="idea-i7-learning-order.html"><span class="idea-id">I7 · 学习顺序</span><b>先独立尝试，还是先看正确示范？</b></a>
<a class="idea-board-card" href="i8.html"><span class="idea-id">I8 · 纠错迁移</span><b>纠正哪个错误，能让我学会一整类题？</b></a>
</div>
<p>I1–I5 仍各自研究具体学习机制。<b>I6</b> 固定错误终点与教学过程，仅比较不同失败轨迹的学习价值；<b>I7</b> 固定教材与预算，比较尝试和示范的先后顺序；<b>I8</b> 则验证高置信度错误、前置知识与共享规则对纠错迁移的作用。<a href="ideas.html">研究方向总览</a> · <a href="idea-i6-failure-value.html">I6</a> · <a href="idea-i7-learning-order.html">I7</a> · <a href="i8.html">I8</a></p>
<p>例如 R²Orch / PATS 已研究支架撤除；RSIFlow 已选择自改进工作流；HCL / SkillBoost 已研究回归；ActiveSaddler 已选有用的失败；PopuLoRA / OPCoD / MACE 已涉及群体教学、反馈和伙伴探索。我们需要回答比这些工作更细的问题。<a class="cite" href="references.html#S26" title="R²Orch: Recursive Self-Improvement for Agent Orchestration via Self-Play within a Skill-Internalization Loop">[S26]</a><a class="cite" href="references.html#S27" title="PATS: Policy-Aware Training Scaffolding for Agentic Reinforcement Learning">[S27]</a><a class="cite" href="references.html#S28" title="RSIFlow: Adaptive Self-Improvement Workflows with an Evolving Meta-Agent">[S28]</a><a class="cite" href="references.html#S29" title="Harness Continual Learning: Continual Adaptation Beyond Model Parameters">[S29]</a><a class="cite" href="references.html#S30" title="Rethinking Self-Evolution: A Constrained Exploration-Exploitation Process for Mitigating Skill Overfitting (SkillBoost)">[S30]</a><a class="cite" href="references.html#S16" title="ActiveSaddler: Automated Curriculum Learning for Agent Harness Optimization">[S16]</a><a class="cite" href="references.html#S32" title="PopuLoRA: Co-Evolving LLM Populations for Reasoning Self-Play">[S32]</a><a class="cite" href="references.html#S33" title="Be My Tutor: On-Policy Co-Distillation for Mutual LLM Improvement via Peer Feedback (OPCoD)">[S33]</a><a class="cite" href="references.html#S34" title="Multi-Agent LLMs Fail to Explore Each Other (MACE: Multi-Agent Contextual Exploration)">[S34]</a></p>

## RSI × 自主学习研究 / 研究导航：从证据走到可执行实验

<div class="route-grid">
<a href="timeline.html"><b>研究时间轴</b><span>CVPR / ICML / ACL DDL、论文阅读进度与研究节点。</span></a>
<a href="ideas.html"><b>I1–I5：具体学习机制</b><span>每项独立的科学问题、最近邻与最小辨别实验。</span></a>
<a href="idea-i6-failure-value.html"><b>I6：失败轨迹有什么学习价值？</b><span>相同问题、相同错误终点，不同尝试过程能否产生不同独立迁移收益？</span></a>
<a href="idea-i7-learning-order.html"><b>I7：先自主尝试还是先看例题？</b><span>相同教材的学习顺序是否改变未来独立解题和可探索路径？</span></a>
<a href="i8.html"><b>I8：错误规则的跨题可学习性</b><span>从 Hypercorrection 出发，分析前置知识、共同错误规则与净学习收益。</span></a>
<a href="idea-i6.html"><b>历史草案：跨轮瓶颈切换</b><span>原版 I6 研究记录单独保留，不再使用当前 I6 编号。</span></a>
<a href="literature.html"><b>RSI 文献与竞争边界</b><span>改什么、如何改，哪些研究已进入元层自进化。</span></a>
<a href="reading-cards.html"><b>论文精读卡片</b><span>按信号、新信息、可采样性、保持和安全五问检索。</span></a>
<a href="reading-notes.html"><b>论文完整精读</b><span>保留方法细节、例子和已核实的论文信息。</span></a>
<a href="cross-domain.html"><b>相邻领域方法</b><span>元学习、课程、知识追踪、双重控制与持续学习。</span></a>
<a href="learning-science.html"><b>教育学与学习科学</b><span>哪些教育学机制有实证支持，哪些迁移仍是猜想。</span></a>
<a href="teaching.html"><b>教学反馈诊断 · I5 支线</b><span>此前“学生反馈能否暴露教师盲点”的详细实验草案，保留供比较。</span></a>
<a href="experiments.html"><b>实验执行方案</b><span>版本控制、持久更新、数据隔离与元学习评估。</span></a>
<a href="references.html"><b>来源与核验记录</b><span>77 条论文和官方资源，保留原始链接与阅读深度。</span></a></div>

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

<p>这是聚焦 RSI 选题的定向研究站，不是穷尽全领域的系统综述。<a href="ideas.html"><b>I1–I5 最新描述</b></a>以 2026-10-27 的问题表述为准：I5 主线为“按自身学习增益动态选择伙伴”；目前 <a href="idea-i6-failure-value.html">I6</a> 聚焦失败轨迹，<a href="idea-i7-learning-order.html">I7</a> 聚焦学习顺序。<a href="idea-i6.html">旧版瓶颈切换</a>已归档，不再占用 I6 编号。</p>
<p><a href="teaching.html">I5 教学反馈诊断</a>作为此前的独立技术支线保留：研究学生的误解能否暴露教师的隐性缺陷。这个实验与“动态伙伴选择”可以共享学生评估基础设施，但不是同一个问题。</p>
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

## RSI 研究时间轴 / 研究活动与投稿时间轴 · 8 个已知日期

<div class="rsi-tl-toolbar"><label for="rsi-tl-kind">事件类型<select id="rsi-tl-kind">
           <option value="all">全部事件</option><option value="deadline">会议 DDL</option>
           <option value="reading">论文精读</option><option value="research">研究记录</option></select></label>
           <label for="rsi-tl-time">时间范围<select id="rsi-tl-time">
           <option value="all">全部时间</option><option value="upcoming">尚未截止</option>
           <option value="past">已结束／已发生</option></select></label>
           <label class="rsi-tl-search" for="rsi-tl-query">检索记录<input type="search" id="rsi-tl-query" placeholder="例如 CVPR、R²Orch、实验、ARR"></label>
           <button type="button" id="rsi-tl-reset">重置</button>
           <output id="rsi-tl-count" aria-live="polite">显示全部</output></div><div class="rsi-tl-months" id="rsi-tl-months"><section class="rsi-tl-month" data-month="2026-10"><div class="rsi-tl-month-head"><h3>2026 年 10 月</h3><span>4 条记录</span></div><div class="rsi-tl-month-body"><article class="rsi-tl-item rsi-tl-item--research" id="rsi-dossier-20261021"
      data-kind="research" data-date="2026-10-21" data-due-at="">
      <div class="rsi-tl-item-date"><time datetime="2026-10-21">10-21</time></div>
      <div class="rsi-tl-item-main">
        <div class="rsi-tl-item-meta"><span class="rsi-tl-kind rsi-tl-kind--research">研究记录</span><span>站内研究记录</span></div>
        <h3>RSI 自主学习研究专题完成首版资料整理</h3>
        <p>网站形成 RSI 文献、跨领域学习科学、候选方向和实验方案的资料页；属于研究文档整理，不代表实验验证完成。</p>
        <div class="rsi-tl-item-footer"><a href="index.html">专题总览 ↗</a></div>
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
  <div class="links reading-links"><a class="link-btn reading-deep-link" href="reading-notes.html#deep-rsi-anything-2610-13912">阅读完整精读（公式 · 实验 · 研究缺口）</a><a class="link-btn" href="#rsi-anything-2610-13912" aria-label="复制或保存此卡片的锚点链接">卡片定位</a><a class="link-btn" href="https://arxiv.org/html/2610.13912" target="_blank" rel="noopener noreferrer">论文 HTML</a><a class="link-btn" href="https://arxiv.org/pdf/2610.13912" target="_blank" rel="noopener noreferrer">PDF</a><a class="link-btn" href="https://github.com/Gen-Verse/RSI-Anything" target="_blank" rel="noopener noreferrer">GitHub 代码</a></div>
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

<div class="deep-paper-head"><p class="deep-meta">PhAI Labs · PhAI Labs Technical Report · arXiv 预印本 · arXiv:2610.13912 · 2026-10-27 精读</p><h3>RSI-Anything: Unlocking Recursive Self-Improvement with World Models</h3><p class="deep-focus">它想解决一个简单问题：Agent 每次能想到好几个办法，但真正试错很贵。怎样挑着试，并保证下一轮比上一轮更好？</p><p class="deep-author-note">先读四个大标题下的一句话；要看例子、公式或实验细节时再展开。这份笔记区分作者结果、教学举例和我们的研究想法，尚未独立复现。</p><div class="deep-glossary"><p class="deep-glossary-title">先记住三个角色</p><dl class="deep-terms"><div><dt>Policy</dt><dd>负责想方案、做动作的 Agent</dd></div><div><dt>World Model</dt><dd>动手之前，先猜执行结果的预测器</dd></div><div><dt>Verifier</dt><dd>真正执行后，给出结果和判定标准的测试</dd></div></dl></div><nav class="deep-shortcuts" aria-label="RSI-Anything 四步精读"><a href="#deep-rsi-anything-2610-13912--stage-challenge">Challenge · 难在哪里</a><a href="#deep-rsi-anything-2610-13912--stage-insight">Insight · 为什么可解</a><a href="#deep-rsi-anything-2610-13912--stage-design">Design · 具体怎么做</a><a href="#deep-rsi-anything-2610-13912--stage-result">Result · 结果怎么样</a><a href="#deep-rsi-anything-2610-13912--stage-next">Next · 哪些问题还没解决</a></nav><section class="deep-stage" id="deep-rsi-anything-2610-13912--stage-challenge" data-story-stage="challenge"><header class="deep-stage-head"><span>01 · Challenge</span><h4>难在哪里</h4></header><p class="deep-stage-lead">Agent 能提出很多修复方案，但真实测试很贵；而且 Agent 变强后，旧预测器可能判断不准新方案。</p><div class="deep-stage-details"><details class="deep-chapter" id="deep-rsi-anything-2610-13912--problem"><summary>为什么一次任务做对了，还不算真正进步？<span class="deep-chapter-hint">展开细节</span></summary><div class="deep-chapter-body"><p class="deep-prose">在同一道题里反复修复，不等于系统能力持续提高。论文区分任务内的动作步 t 和系统更新周期 k：一次周期可以不接纳任何更新；只有被接纳的 Policy / Workflow 或 World Model 改变下一轮决策，才体现持久改进。</p><aside class="deep-note deep-note--example"><b>举个例子</b><p>今天修好了一个程序，不代表明天就会修同类错误。系统要在下一轮用上学到的东西，才算把这次经验留下来。</p></aside><aside class="deep-note deep-note--boundary"><b>证据边界</b><p>跨领域统一的是决策与反馈协议，不是七个领域共用一组通用世界模型权重（§2.1–2.2）。</p></aside></div></details></div></section><section class="deep-stage" id="deep-rsi-anything-2610-13912--stage-insight" data-story-stage="insight"><header class="deep-stage-head"><span>02 · Insight</span><h4>为什么可解</h4></header><p class="deep-stage-lead">先预测哪些方案值得试，可以少花测试成本。真实结果又能纠正预测器，但升级时必须看整套系统是否进步。</p><div class="deep-stage-details"><details class="deep-chapter" id="deep-rsi-anything-2610-13912--insight"><summary>为什么用预测先挑，再用真实结果纠错？<span class="deep-chapter-hint">展开细节</span></summary><div class="deep-chapter-body"><p class="deep-prose">关键不是让世界模型替代真实测试，而是把两者分工：预测负责省测试次数，真实结果负责检验预测准不准。Agent 变强后可能提出新方案，所以预测器也要根据新反馈调整。</p><div class="deep-table" tabindex="0" role="region" aria-label="精读内容比较表"><table><thead><tr><th scope="col">碰到的问题</th><th scope="col">容易掉进的坑</th><th scope="col">作者的办法</th></tr></thead><tbody><tr><td>测试费用高</td><td>四个候选全部跑完，预算很快用光</td><td>先预测，挑值得试的方案去真实执行</td></tr><tr><td>预测器会看走眼</td><td>把模型猜测当成事实，后面越学越偏</td><td>只用真实执行的结果检查预测是否可靠</td></tr><tr><td>模块之间不一定合拍</td><td>Agent 和预测器单独更好，搭配却可能更差</td><td>升级之前重新测试新组合</td></tr></tbody></table></div><aside class="deep-note deep-note--insight"><b>一句话理解</b><p>预测是为了少走弯路，真实反馈是为了知道有没有走对；系统是否进步，要看最后整套搭配。</p></aside></div></details></div></section><section class="deep-stage" id="deep-rsi-anything-2610-13912--stage-design" data-story-stage="design"><header class="deep-stage-head"><span>03 · Design</span><h4>具体怎么做</h4></header><p class="deep-stage-lead">Agent 提方案 → 世界模型预测 → 选择少数方案真实测试 → 按需更新 → 检查新旧组件组合，决定是否保留。</p><div class="deep-stage-details"><details class="deep-chapter" id="deep-rsi-anything-2610-13912--example"><summary>先看一个例子：四个补丁该测试哪一个？<span class="deep-chapter-hint">展开细节</span></summary><div class="deep-chapter-body"><aside class="deep-note deep-note--example"><b>示例数字，并非论文运行记录</b><p>固定代码生成器生成四种补丁，假设不确定性惩罚系数为 0.5。该例只是为了说明候选排序；论文真实实验是五类执行结果预测。</p></aside><div class="deep-table" tabindex="0" role="region" aria-label="精读内容比较表"><table><thead><tr><th scope="col">补丁</th><th scope="col">预测效用</th><th scope="col">不确定性</th><th scope="col">示例最终分数</th></tr></thead><tbody><tr><td>A 修改边界</td><td>0.35</td><td>0.10</td><td>0.300</td></tr><tr><td>B 改索引更新</td><td>0.75</td><td>0.40</td><td>0.550</td></tr><tr><td>C 补充终止条件</td><td>0.60</td><td>0.05</td><td>0.575（选择）</td></tr><tr><td>D 重写循环</td><td>0.48</td><td>0.20</td><td>0.380</td></tr></tbody></table></div><ol class="deep-steps"><li><strong>选择 C 并实际运行</strong><p>假设失败。只有 C 得到了真实结果，A/B/D 的预测不能当作已验证事实。</p></li><li><strong>判断是否需要更新 WM</strong><p>“预测成功率 60%、实际失败一次”并不足以证明 WM 失准；要积累同版本预测—观测记录。</p></li><li><strong>更新后仍须完整配对检查</strong><p>新 Policy、新 WM 单独更好时，最终系统也可能更差；不通过则继续使用旧组合。</p></li></ol></div></details><details class="deep-chapter" id="deep-rsi-anything-2610-13912--selection"><summary>怎么挑选值得真实测试的方案？（公式 7–8）<span class="deep-chapter-hint">展开细节</span></summary><div class="deep-chapter-body"><div class="deep-formula"><b>Eq. (7) · 预测效用与可选不确定性惩罚</b><code>R_d(τ̂) = Σ_j w_(d,j) · r_(τ,j) − Δ_d(τ̂)</code><p><strong>怎么理解：</strong>先按有效性与操作约束排除非法候选，再按预测收益排序；只有任务设置开启不确定性惩罚时 Δ 才非零。</p><p class="deep-caveat"><strong>边界：</strong>代码实验实际聚合五类执行结果概率，选四个补丁中的一个执行；不是简单地直接套用预测成功率。</p></div><div class="deep-table" tabindex="0" role="region" aria-label="精读内容比较表"><table><thead><tr><th scope="col">证据层级</th><th scope="col">是什么</th><th scope="col">解释边界</th></tr></thead><tbody><tr><td>E0</td><td>确定性规则检查</td><td>只覆盖明确规则</td></tr><tr><td>E1</td><td>学习模型预测 / 想象轨迹</td><td>不是实际执行真值</td></tr><tr><td>E2</td><td>专用模拟器或高保真计算</td><td>受模拟范围约束</td></tr><tr><td>E3</td><td>外部测试或真实实验</td><td>只覆盖真正被测试的候选</td></tr></tbody></table></div><div class="deep-formula"><b>Eq. (8) · 想象轨迹准入</b><code>e_τ = 1[v_τ=1] · 1[R_d(τ̂)≥r_min] · C_U(τ) · 1[ℓ_τ∈E_train]</code><p><strong>怎么理解：</strong>通过合法性、预测效用、不确定性检查和证据来源限制的模拟轨迹，才可能进入训练。</p><p class="deep-caveat"><strong>边界：</strong>选择去执行谁与选择让哪些想象轨迹参与训练是两件事；未开启模拟学习时 D_sim 为空。</p></div><aside class="deep-note deep-note--insight"><b>选择偏差</b><p>World Model 决定谁得到真实反馈；而这些反馈又用于训练下一版模型。被低估的好候选可能始终没有机会获得真实证据。</p></aside></div></details><details class="deep-chapter" id="deep-rsi-anything-2610-13912--reliability"><summary>预测错了，要不要马上重新训练？（公式 10–12）<span class="deep-chapter-hint">展开细节</span></summary><div class="deep-chapter-body"><div class="deep-formula"><b>Eq. (10) · 三种可靠性状态</b><code>ρᵂ_k ∈ {reliable, unreliable, insufficient}</code><p><strong>怎么理解：</strong>从当前版本的预测与真实观测检查误差、校准和覆盖；证据不足不等于预测可靠。</p><p class="deep-caveat"><strong>边界：</strong>不能把旧版预测记录直接混入新版错误率；必要时用新版重算历史输入。</p></div><div class="deep-formula"><b>Eq. (11) · 适配触发</b><code>uᵂ_k = 1[ρᵂ_k=unreliable] · 1[D_adapt 足够] · 1[B_update≥c_adapt]</code><p><strong>怎么理解：</strong>同时确认失准、有足够修正数据、有足够预算，才尝试适配。</p><p class="deep-caveat"><strong>边界：</strong>长期没被选择执行的候选缺少反馈，既不能宣称模型准确，也未必能触发适配。</p></div><div class="deep-formula"><b>Eq. (12) · 提出新预测器</b><code>φ′_(k+1) = Adapt(φ_k, D_adapt) if uᵂ_k=1; else φ_k</code><p><strong>怎么理解：</strong>提出一个新版本不等于已保留；更新候选仍要经过后续的组件和配对接纳检查。</p><p class="deep-caveat"><strong>边界：</strong>Policy 和 WM 可以异步更新，但外部反馈消耗与训练/评估计算开销不是同一个成本口径。</p></div></div></details><details class="deep-chapter" id="deep-rsi-anything-2610-13912--pair"><summary>为什么两个模块各自变好，组合后反而更差？（公式 13–18）<span class="deep-chapter-hint">展开细节</span></summary><div class="deep-chapter-body"><div class="deep-formula"><b>Eqs. (13)–(16) · 组件检查</b><code>Gπ = Qπ(θ′; θ, D_gateπ) ； GW = QW(φ′; φ, D_gateW)</code><p><strong>怎么理解：</strong>分别检查新 Policy 和新 WM；若某组件未通过，仍使用它的旧版本与其他已通过组件组装。</p><p class="deep-caveat"><strong>边界：</strong>新 WM 平均更准确，不代表它对新 Policy 产生的候选也更准确。</p></div><div class="deep-formula"><b>Eqs. (17)–(18) · 配对检查与保留</b><code>Gpair = Qpair((θ̄, φ̄); (θ, φ), D_compat); Gpair=0 则保留原配对</code><p><strong>怎么理解：</strong>组合决策行为需要在预先设定、可比的任务与约束下检查；配对失败时整体回退。</p><p class="deep-caveat"><strong>边界：</strong>已有的是通用协议定义，不能直接视为充分的 Pair Gate 消融证据。</p></div><div class="deep-table" tabindex="0" role="region" aria-label="精读内容比较表"><table><thead><tr><th scope="col">教学示例（非论文数字）</th><th scope="col">独立指标 / 配对成功率</th><th scope="col">解释</th></tr></thead><tbody><tr><td>旧 P₀+旧 W₀</td><td>任务成功率 68%</td><td>基线</td></tr><tr><td>新 P₁+旧 W₀</td><td>任务成功率 74%</td><td>新 Policy 有改善</td></tr><tr><td>单独检查新 W₁</td><td>Brier 0.40→0.32</td><td>新预测器有改善</td></tr><tr><td>新 P₁+新 W₁</td><td>任务成功率 64%</td><td>组合变差，拒绝升级</td></tr></tbody></table></div><aside class="deep-note deep-note--insight"><b>最重要的机制洞察</b><p>新 Policy 改变候选分布，新 World Model 改变被选中接受反馈的候选。版本接纳必须从单组件得分推进到组装后真实决策行为。</p></aside></div></details></div></section><section class="deep-stage" id="deep-rsi-anything-2610-13912--stage-result" data-story-stage="result"><header class="deep-stage-head"><span>04 · Result</span><h4>结果怎么样</h4></header><p class="deep-stage-lead">代码修复：固定生成器时，成功率由 26.3% 升至 31.2%。五轮规划得分由 21.80% 升至 46.01%，但并非同一实验中证明长期联合进化。</p><div class="deep-stage-details"><details class="deep-chapter" id="deep-rsi-anything-2610-13912--results"><summary>真正变好的是什么？五组实验分别说明什么？<span class="deep-chapter-hint">展开细节</span></summary><div class="deep-chapter-body"><div class="deep-evidence-grid"><article class="deep-evidence"><h4>代码修复 · 预测选择与适配的受控比较</h4><p><b>评测设置：</b>ReasonFlux-Coder-7B 固定；CodeContests 200 题×3 种子；每轮四候选选一执行，最多三轮。</p><p><b>作者报告：</b>随机 26.0%；静态验证器 26.3%；固定 WM 29.2%；适配 WM 31.2%。平均在线测试调用 3.71–3.72 次/题。静态→固定 WM 排序准确率 66.5%→72.8%，Brier 0.488→0.358。</p><p><b>能够支持：</b>预测器更会选、适配后还能进一步提升修复成功率。</p><p class="deep-caveat"><b>尚不能推断：</b>Coder 自身变强；总训练和门控计算费用完全相同。</p></article><article class="deep-evidence"><h4>GUI · 任务表现与动作效率</h4><p><b>评测设置：</b>MiniWoB++ checkbox 同一批 100 个实例；同时报告 OSWorld。</p><p><b>作者报告：</b>成功率 51%→79%→99%；平均动作 5.30→3.21；OSWorld 相对初始 Agent 提升 18.4%。</p><p><b>能够支持：</b>Policy 与 WM 的不同保留版本改善部分 GUI 任务结果。</p><p class="deep-caveat"><b>尚不能推断：</b>单独由 Pair Gate 导致全部提升，或在所有网页任务可复制。</p></article><article class="deep-evidence"><h4>实验室规划 · 连续 Policy 改善</h4><p><b>评测设置：</b>LabHorizon F200 Level-2，200 个任务，单个 4B Policy 的五个版本。</p><p><b>作者报告：</b>规划得分 21.80%→38.03%→41.99%→44.56%→46.01%。</p><p><b>能够支持：</b>连续 Policy 更新能提高所测规划指标。</p><p class="deep-caveat"><b>尚不能推断：</b>在相同任务里也完成多轮 WM 联合优化的独立证明。</p></article><article class="deep-evidence"><h4>化学实验 · 实测产率与预算</h4><p><b>评测设置：</b>Suzuki–Miyaura 的流动 LC–MS 筛选；BO 对照相同 40 次实验。</p><p><b>作者报告：</b>平均最佳观测产率 96.15%，Bayesian Optimization 为 82.16%。</p><p><b>能够支持：</b>在所报告的化学条件空间与预算内搜索更有效。</p><p class="deep-caveat"><b>尚不能推断：</b>任意反应或无限预算均占优。</p></article><article class="deep-evidence"><h4>免疫科学 · 研究假设生成</h4><p><b>评测设置：</b>工作流改进 + 状态预测 + 自我纠正的应用示范。</p><p><b>作者报告：</b>形成拟开展实验验证的干预假设。</p><p><b>能够支持：</b>完整研究系统可以串联多个领域能力。</p><p class="deep-caveat"><b>尚不能推断：</b>治疗有效性或湿实验已经得到证实。</p></article></div></div></details></div></section><section class="deep-stage" id="deep-rsi-anything-2610-13912--stage-next" data-story-stage="next"><header class="deep-stage-head"><span>05 · Next</span><h4>哪些问题还没解决</h4></header><p class="deep-stage-lead">这些是尚未解决的科学问题，不应当写成原论文已经证明的结论。</p><div class="deep-stage-details"><details class="deep-chapter" id="deep-rsi-anything-2610-13912--boundary"><summary>哪些结论还不能下？<span class="deep-chapter-hint">展开细节</span></summary><div class="deep-chapter-body"><div class="deep-table" tabindex="0" role="region" aria-label="精读内容比较表"><table><thead><tr><th scope="col">已有技术背景</th><th scope="col">该论文的推进</th></tr></thead><tbody><tr><td>MuZero、Dreamer：预测模型用于规划</td><td>把预测纳入候选反馈分配及跨轮次系统更新</td></tr><tr><td>强化学习、自训练、Reflexion：利用反馈改进行为</td><td>明确 Policy/Workflow 的版本继承和异步更新</td></tr><tr><td>常规校准与版本回退</td><td>用预测可靠性、证据覆盖、预算和 Policy–WM 配对检查组织统一协议</td></tr></tbody></table></div><aside class="deep-note deep-note--paper"><b>合理的创新定位</b><p>更像“系统级自我改进协议 + 多领域验证”，而不是首次提出世界模型、基于反馈学习或检查回退。五类实验覆盖不同路径；论文也说明仍需单一任务中的长期联合多轮评估。</p></aside><ul class="deep-bullets"><li>即时排序无法生成原 Policy 从未提出的好解，也不能解决候选分布外的可靠性。</li><li>只有被选中测试的候选提供观测，WM 可能持续低估某些正确但少见的方案。</li><li>配对门控不等同于旧任务长期不遗忘，或恶意行为不会被写入记忆。</li><li>评价标准在实验协议中固定；“评估器本身也会被改写”仍是开放问题。</li></ul></div></details><details class="deep-chapter" id="deep-rsi-anything-2610-13912--research"><summary>如果我们接着做，最值得验证什么？<span class="deep-chapter-hint">展开细节</span></summary><div class="deep-chapter-body"><aside class="deep-note deep-note--proposal"><b>延伸研究构想（非 RSI-Anything 原文结论）</b><p>Agent 能否预测“哪一次真实试错会让下一轮独立能力提升最多”，而不仅是“当前哪一个方案成功概率最高”？</p></aside><div class="deep-formula"><b>我们的学习收益目标（概念式）</b><code>V_learn(a) = E[Perf(θ_after | test(a)) − Perf(θ_after | matched no-test(a))]</code><p><strong>怎么理解：</strong>与相同训练预算但没有该候选反馈的路径做对照，度量真实学习增益。</p><p class="deep-caveat"><strong>边界：</strong>不同于论文 Eq. (7) 的即时效用；需要来自相同检查点的受控训练和独立测试。</p></div><div class="deep-test-list"><article class="deep-test"><h4>实验 A：即时成功 vs 学习价值</h4><p><b>实验设计：</b>固定代码生成器、更新机制及反馈预算；比较即时成功率排序与下一轮学习增益排序。</p><p><b>决定性证据：</b>在独立任务上衡量 ΔPerf、负迁移、实际测试成本；小型诊断集全测候选，估计选择偏差。</p></article><article class="deep-test"><h4>实验 B：Pair Gate 的独立必要性</h4><p><b>实验设计：</b>由同一组更新构造 P₀W₀、P₁W₀、P₀W₁、P₁W₁ 四配对；有/无 Pair Gate 多轮对照。</p><p><b>决定性证据：</b>记录“组件分别变好但组合退步”的频率、长期净增益和额外门控成本。</p></article><article class="deep-test"><h4>实验 C：I5 模型间交换舞伴</h4><p><b>实验设计：</b>从同一学生模型检查点，按最强伙伴、相近伙伴、随机伙伴、预测最高学习增益伙伴等预算学习。</p><p><b>决定性证据：</b>独立测试中相对于无教师等预算学习的增益，以及随模型能力变化而发生的最优伙伴迁移。</p></article></div><aside class="deep-note deep-note--boundary"><b>安全与追溯要求</b><p>保留候选/预测/真实执行/训练准入/门控数据的版本归因，独立检验评估器被绕过、越权操作及有害知识持久化，而非仅凭提高当前分数宣布安全。</p></aside></div></details></div></section><div class="deep-back"><a href="reading-cards.html#rsi-anything-2610-13912">返回论文速览卡片</a></div><div class="links deep-source-links"><a class="link-btn" target="_blank" rel="noopener noreferrer" href="https://arxiv.org/html/2610.13912">arXiv 原文</a><a class="link-btn" target="_blank" rel="noopener noreferrer" href="https://arxiv.org/pdf/2610.13912">PDF 原文</a><a class="link-btn" target="_blank" rel="noopener noreferrer" href="https://github.com/Gen-Verse/RSI-Anything">作者代码</a></div></div>

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

<p>Butterfield 与 Metcalfe（2001）发现 <b>Hypercorrection Effect</b>；Carpenter 等（2018）在真实大学课堂观察到高置信度错误在得到正确反馈后有时更容易被纠正。<a class="cite" href="references.html#E12" title="Errors committed with high confidence are hypercorrected">[E12]</a><a class="cite" href="references.html#E13" title="Hypercorrection of high-confidence errors in the classroom">[E13]</a></p><p>这不等于“自信错误必然值得训练”。Sitzman 等（2014）发现，学习者已有的领域知识与纠错表现密切相关；Foster 等（2022）观察了数学在线诊断题中的置信度与后续相似题表现。<a class="cite" href="references.html#E14" title="Prior knowledge is more predictive of error correction than subjective confidence">[E14]</a><a class="cite" href="references.html#E15" title="School students’ confidence when answering diagnostic questions online">[E15]</a></p><p>对 LLM，应区分正确反馈后的原题修复、参数的真实持久更新以及未见题的规则级迁移。详细机制与受控实验在 <a href="i8.html">I8：错误可学习性与跨题迁移</a>。</p>

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
 <a class="idea-board-card" href="#idea-2"><span class="idea-id">I2 · 因材施教</span><b>同样犯错，为什么学习方法不同？</b><small>根据真实学习反应选方法</small></a>
 <a class="idea-board-card" href="#idea-3"><span class="idea-id">I3 · 温故知新</span><b>新方法有用，却和旧方法冲突怎么办？</b><small>复习并解决适用条件冲突</small></a>
 <a class="idea-board-card" href="#idea-4"><span class="idea-id">I4 · 生产性失败</span><b>失败一次就总结，还是再试几次？</b><small>判断何时证据足够更新 Skill</small></a>
 <a class="idea-board-card" href="#idea-5"><span class="idea-id">I5 · 费曼学习法</span><b>和谁一起学，自己进步最快？</b><small>伙伴选择随能力一起演化</small></a>
 <a class="idea-board-card" href="idea-i6-failure-value.html"><span class="idea-id">I6 · 失败学习价值</span><b>同题都答错，为什么有些失败过程更值得学习？</b><small>固定错误结果与教学方式，比较失败轨迹的增量收益</small></a>
 <a class="idea-board-card" href="idea-i7-learning-order.html"><span class="idea-id">I7 · 学习顺序</span><b>先看例题，还是先独立尝试？</b><small>固定教材与预算，研究独立能力、探索与多轮迁移</small></a>
 <a class="idea-board-card" href="i8.html"><span class="idea-id">I8 · 错误学习迁移</span><b>改正哪个错误，能够学会一整类题？</b><small>Hypercorrection 与跨题净学习收益</small></a>
 </div>
 <p class="status">状态：I1–I8 研究问题已整理；I6 与 I7 正交拆分，I8 保留独立机制验证；尚无本项目的受控实测结果。</p>
 <p>本站将它们挂到 RSI 的四个问题与安全轴下：<b>信号对不对 / 有没有新东西 / 采不采得到 / 吸收了会不会丢 / 安全。</b>这些标签表示要研究的环节，不表示问题已经解决。详见 <a href="reading-cards.html">论文阅读卡片</a>。</p>


## I1–I8：八个研究问题 / I1：脚手架学习法——哪些该自己学会，哪些用时再查？


 <div class="idea-focus"><span class="idea-axis">采不采得到</span><span class="idea-axis">吸收了会不会丢</span><p><b>最直观的问题：</b>调试方法最好自己掌握；频繁变化的 API 细节可能用时再查就行。Agent 能不能自己学会这种取舍，并随能力与环境变化调整？</p></div>
 <h3>别人研究的是……</h3>
 <p><b>R²Orch</b> 研究什么时候可以撤掉已被内部能力替代的 Skill，并在自博弈中推动能力内化；<b>PATS</b> 把 Skill 当作训练时的临时支架，能力变强后修订或移除冗余提示。它们都不只是“减少提示词”，而是 I1 必须正面比较的工作。<a class="cite" href="references.html#S26" title="R²Orch: Recursive Self-Improvement for Agent Orchestration via Self-Play within a Skill-Internalization Loop">[S26]</a><a class="cite" href="references.html#S27" title="PATS: Policy-Aware Training Scaffolding for Agentic Reinforcement Learning">[S27]</a></p>
 <h3>我们想研究的是……</h3>
 <p><strong>同一份辅助经验，什么时候该学进自身，什么时候该留在外部、按需读取？</strong>例如稳定的排查步骤值得固化，易变的接口规则可能应保留检索入口。判断取舍的依据不能只看“有帮助时成功了没有”，还要看撤除帮助之后能不能在新任务上独立完成、环境改变后会不会出错。</p>
 <p><b>难点：</b>一次撤除成功，可能只是恰好不需要那个 Skill；完全不依赖 Skill 也不等于能力提高。</p>
 <p><b>可利用的观察：</b>辅助对当前完成任务有用，不代表把它写进长期能力最有用；知识稳定性、已有基础和后续更新都会改变最佳选择。</p>
 <div class="flow"><div><b>列出辅助经验</b><small>稳定规则 / 易变知识 / 临时提示</small></div><div><b>比较三种做法</b><small>内化、外置检索、渐隐</small></div><div><b>独立执行新任务</b><small>清空辅助与任务上下文</small></div><div><b>根据收益调整选择</b><small>新旧任务与成本一起算</small></div></div>
 <h3>最小验证</h3><p>同一 Agent、相同训练和工具预算，将稳定操作经验与会变动的 API 规则分开，比较<strong>全部内化 / 全部外置 / 固定渐隐 / 自适应取舍</strong>。看撤除后的独立正确率、环境变更后的退化、保留成本。再和 R²Orch/PATS 适配版比较。如果一律内化或简单撤除就同样好，我们不应硬说路由策略有新价值。</p>


## I1–I8：八个研究问题 / I2：因材施教——同样犯错，为什么学习方法不同？


 <div class="idea-focus"><span class="idea-axis">信号对不对</span><span class="idea-axis">采不采得到</span><p><b>最直观的问题：</b>两个 Agent 都不会修一个 Bug，一个看一次示范就学会了，另一个要对比几次失败才理解。只看“错在哪里”，够不够决定下一轮该怎么学？</p></div>
 <h3>别人研究的是……</h3>
 <p><b>RSIFlow</b> 根据执行瓶颈选择该改模型、Harness 还是任务产物，并让负责调度的 Meta-Agent 进化；<b>MetaSkill-Evolve</b> 让任务 Skill 与修改 Skill 的元流程在不同时间尺度上改进。它们已经覆盖“动态自我改进”这个大概念。<a class="cite" href="references.html#S28" title="RSIFlow: Adaptive Self-Improvement Workflows with an Evolving Meta-Agent">[S28]</a><a class="cite" href="references.html#S06" title="MetaSkill-Evolve: Recursive Self-Improvement of LLM Agents via Two-Timescale Meta-Skill Evolution">[S06]</a></p>
 <h3>我们想研究的是……</h3>
 <p><strong>即使失败类型相同、要更新的对象也相同，Agent 是否仍然有不同的最佳学习方法？</strong>有人更适合看示范，有人更适合自主重试，也有人需要比较正确与错误路径。能不能先花少量预算“试学”一轮，再选能让自己下一轮独立进步最多的方法？能力变了之后，也重新判断。</p>
 <p><b>难点：</b>一次试学效果好未必意味着长期收益好；试学本身花费预算，而且不同 Agent 的基础能力不一致。</p>
 <p><b>可利用的观察：</b>同样的错误标签不能完整预测对不同教学动作的反应；少量有控制的学习尝试可能比静态分类更有信息。</p>
 <div class="flow"><div><b>锁定同类失败</b><small>同一更新对象</small></div><div><b>少量试学</b><small>示范 / 反例 / 独立练习</small></div><div><b>观察独立进步</b><small>不看当前答题小分</small></div><div><b>下轮选更合适的方式</b><small>进化后重估</small></div></div>
 <h3>最小验证</h3><p>从同一快照分叉三种学习处理，先固定“修改 Skill”而不是混入更新表面。让两个当前分数接近的 Agent 学相同类型任务，比较<strong>固定方法 / 错误类型路由 / 通用 bandit / 试学后选择</strong>在未见任务上的等预算进步。再检验能力进化后原来最好的方法是否改变。若简单 bandit 就足够，保留现象但不夸大复杂模型的贡献。</p>


## I1–I8：八个研究问题 / I3：温故知新——新方法有用，却和旧方法冲突怎么办？


 <div class="idea-focus"><span class="idea-axis">吸收了会不会丢</span><span class="idea-axis">安全</span><p><b>最直观的问题：</b>Agent 学会更快的处理流程，却把另一种场景下原本正确的规则覆盖了。我们是否只能回滚这次更新？</p></div>
 <h3>别人研究的是……</h3>
 <p><b>Harness Continual Learning（HCL）</b> 在提交 Harness 更新前，同时检查新任务进步、历史能力保持和有效性；<b>SkillBoost</b> 用回归约束筛掉破坏旧能力的修改。它们解决了不少“新改动伤害旧任务”的问题。<a class="cite" href="references.html#S29" title="Harness Continual Learning: Continual Adaptation Beyond Model Parameters">[S29]</a><a class="cite" href="references.html#S30" title="Rethinking Self-Evolution: A Constrained Exploration-Exploitation Process for Mitigating Skill Overfitting (SkillBoost)">[S30]</a></p>
 <h3>我们想研究的是……</h3>
 <p><strong>当新旧 Skill 各自都有效，却会在不同条件下互相干扰时，Agent 能否通过针对性复习把两者都保留下来？</strong>不是每次全部重练，也不只是发现回归就拒绝更新，而是学清楚“这个规则什么时候用、什么时候不能用”。</p>
 <p><b>难点：</b>旧能力退化可能来自检索冲突、适用范围模糊，也可能确实是参数遗忘。需要定位干扰来源，而不是一律新增旧题。</p>
 <p><b>可利用的观察：</b>不少负迁移是两个局部有效策略之间的错误选择；练习条件边界可能比简单重复旧样本更有用。</p>
 <div class="flow"><div><b>检测新旧冲突</b><small>同一新版本 / 旧版本对照</small></div><div><b>找冲突条件</b><small>工具状态、触发与上下文</small></div><div><b>定向复习</b><small>边界任务，不是所有旧题</small></div><div><b>合并保留</b><small>旧、新和组合任务都通过</small></div></div>
 <h3>最小验证</h3><p>制作两组分别成功、混合却容易互相干扰的 Skill，加入自然更新中的同类案例。比较<strong>发现退化即回滚 / 均匀重放 / MIR 风格重放 / 针对冲突条件复习</strong>。固定复习调用数与存储预算，测试旧任务保持、新任务收益及两者组合。若只是因为多存了规则才进步，不属于新机制。</p>


## I1–I8：八个研究问题 / I4：生产性失败——失败一次就总结，还是再试几次？


 <div class="idea-focus"><span class="idea-axis">信号对不对</span><span class="idea-axis">有没有新东西</span><span class="idea-axis">采不采得到</span><p><b>最直观的问题：</b>API 超时一次，不能马上写进长期 Skill：“这个工具不可靠，以后别用”。Agent 怎么知道自己真的找到了通用规律，而不是遇到了偶然故障？</p></div>
 <h3>别人研究的是……</h3>
 <p><b>ActiveSaddler</b> 研究应该继续优化哪些失败模式；<b>Trace2Skill</b> 研究从很多执行轨迹中提炼统一、可迁移的 Skill。失败选择与跨轨迹总结并不是空白。<a class="cite" href="references.html#S16" title="ActiveSaddler: Automated Curriculum Learning for Agent Harness Optimization">[S16]</a><a class="cite" href="references.html#S31" title="Trace2Skill: Distill Trajectory-Local Lessons into Transferable Agent Skills">[S31]</a></p>
 <h3>我们想研究的是……</h3>
 <p><strong>对一次失败，应该马上形成经验，还是继续做能辨别原因的尝试？又该在哪一步停下来，认定证据足以修改 Skill？</strong>例如先复现超时，再改变请求大小或重试条件，区分 API 规则错误、环境偶发故障和策略错误。</p>
 <p><b>难点：</b>多试几次自然可能多成功，优势未必来自更好地理解失败。不能让训练时见到的测试答案泄漏给更新器。</p>
 <p><b>可利用的观察：</b>最值得学习的失败不一定最严重；能区分多个原因的下一次试验，可能比立刻反思一句话更有价值。</p>
 <div class="flow"><div><b>遇到失败</b><small>先列几个可检验的原因</small></div><div><b>选择下一次试验</b><small>最能区分解释</small></div><div><b>决定继续或归纳</b><small>证据是否稳定</small></div><div><b>更新 Skill 并外测</b><small>新任务、旧任务均验证</small></div></div>
 <h3>最小验证</h3><p>固定失败家族与执行预算，比较<strong>失败即更新 / 固定多次重试 / 随机补充试验 / 按争议原因选下一次试验并决定停止</strong>。指标是写入错误规则的比例、未见环境的迁移与最终改进效率，不是“试的次数越多越好”。整个过程可使用沙箱执行反馈，不需要外部教师告诉标准答案。</p>


## I1–I8：八个研究问题 / I5：费曼学习法——和谁一起学，自己进步最快？


 <div class="idea-focus"><span class="idea-axis">有没有新东西</span><span class="idea-axis">采不采得到</span><span class="idea-axis">吸收了会不会丢</span><p><b>最直观的问题：</b>同样让我和别的模型交流，最强的模型不一定最能帮助我成长；能力提高后，原来最好的伙伴可能也不再适合。</p></div>
 <h3>别人研究的是……</h3>
 <p><b>PopuLoRA</b> 研究在共同进化的教师与解题者群体中，谁给谁出题更有学习挑战；<b>OPCoD</b> 研究两模型互相教学时，什么时候应该交换和采纳同伴反馈；<b>MACE（Multi-Agent Contextual Exploration）</b> 研究怎样探索和选择协作伙伴，以改善当前交互任务和探索表现。它们各自涉及配对、反馈或伙伴探索，但衡量目标与我们不完全一样。<a class="cite" href="references.html#S32" title="PopuLoRA: Co-Evolving LLM Populations for Reasoning Self-Play">[S32]</a><a class="cite" href="references.html#S33" title="Be My Tutor: On-Policy Co-Distillation for Mutual LLM Improvement via Peer Feedback (OPCoD)">[S33]</a><a class="cite" href="references.html#S34" title="Multi-Agent LLMs Fail to Explore Each Other (MACE: Multi-Agent Contextual Exploration)">[S34]</a></p>
 <h3>我们想研究的是……</h3>
 <p><strong>谁能使我在交流结束后，自己做新任务时进步最多？这种最佳伙伴会不会随着我自己的能力变化而改变？</strong>不只比较参数大小，还看任务互补、对方擅长什么、我能否理解并吸收它的经验。也可以研究我教别人后是否反过来变强。</p>
 <p><b>难点：</b>伙伴可能直接帮我把当前题做对，但我并没有学会。必须撤走伙伴、清空对话，并比较自身新旧版本的独立表现。</p>
 <p><b>可利用的观察：</b>当前回答受益最大的人，未必是下次让我进步最多的人；最合适的差距可能随学习阶段变化。</p>
 <div class="flow"><div><b>能力不同的伙伴池</b><small>规模、领域、强弱互补</small></div><div><b>受控教学交流</b><small>按相同时间和预算</small></div><div><b>我自己的持久更新</b><small>参数、Skill 或 Harness</small></div><div><b>伙伴退出后测试</b><small>新任务进步决定下轮选谁</small></div></div>
 <h3>最小验证</h3><p>从三种能力档位的若干模型开始，控制教师/学生方向、任务、教学 token 和训练预算，比较<strong>随机匹配 / 同级匹配 / 永远找最强者 / PopuLoRA 式能力匹配 / MACE 式当前交互收益匹配 / 以独立学习增益为目标的选择</strong>。连续多轮重选伙伴，记录最佳伙伴的变化、下轮独立成功率和旧能力退化。进一步做“只获得答案、不更新自身”和“更新后撤除伙伴”对照，排除只是在组队解题。</p>
 <div class="note">已有 <a href="teaching.html">教学反馈诊断教师盲点的 I5 早期技术方案</a>独立保留，属于相邻支线：它研究“学生反馈暴露教师哪类缺陷”；本页 I5 主线研究“当前该与谁学，能让自己下一轮变强”。两者不能混成同一项已验证成果。</div>


## I1–I8：八个研究问题 / I6、I7 与 I8：一次只研究一个变量


<div class="table-wrap"><table><thead><tr><th>Idea</th><th>改变什么</th><th>固定什么</th><th>决定性结果</th></tr></thead><tbody>
<tr><td><a href="idea-i6-failure-value.html">I6 · 失败轨迹价值</a></td><td>同题失败过程</td><td>模型检查点、错误终点、正确反馈、学习顺序、预算</td><td>不同轨迹产生的后续独立学习增益</td></tr>
<tr><td><a href="idea-i7-learning-order.html">I7 · 学习顺序</a></td><td>先尝试 / 先看正确示范</td><td>题目、示范内容、更新器与预算</td><td>撤掉教师后的独立能力、有效探索与多轮迁移</td></tr>
<tr><td><a href="i8.html">I8 · 规则级错误迁移</a></td><td>知识准备、错误规则覆盖范围和更新兼容性</td><td>对应的纠错/更新方法</td><td>哪些错误修复后能迁移到一整类题</td></tr>
</tbody></table></div>
<p><b>不要混成一篇：</b>I6 的核心证据是“相同错误终点，不同失败过程”；I8 的核心证据是“错误知识状态与跨题规则”的关系。I7 不以 I6/I8 的分类结果作为必需前提。旧版<a href="idea-i6.html">跨轮瓶颈切换方案</a>仅作为历史草案保留，不再占用当前 I6 编号。</p>


## I1–I8：八个研究问题 / I8：Hypercorrection——为什么改正一种错误能学会一类题？


 <div class="idea-focus"><span class="idea-axis">信号对不对</span><span class="idea-axis">吸收了会不会丢</span><p><b>具体问题：</b>同样一道数学错题，一个模型得到正确反馈后只记住答案，另一个却能举一反三。纠正哪种错误值得投入下一轮学习预算？</p></div>
 <h3>Observable Phenomenon / Why</h3><p>Hypercorrection 的人类学习研究发现，高置信度错误经正确反馈后有时更容易被纠正；已有知识可能是重要解释。由此提出待验证的模型假设：前置知识是否充分、错误是否由影响多题的共同规则造成，可能共同决定一次纠错的跨题收益。<a class="cite" href="references.html#E12" title="Errors committed with high confidence are hypercorrected">[E12]</a><a class="cite" href="references.html#E13" title="Hypercorrection of high-confidence errors in the classroom">[E13]</a><a class="cite" href="references.html#E14" title="Prior knowledge is more predictive of error correction than subjective confidence">[E14]</a></p>
 <h3>Challenge / Insight / Design</h3><p><b>Challenge：</b>置信度不等于学得会；修复原题不等于迁移；真实收益通常要在更新后才能观察。<b>Insight：</b>已有知识准备程度 × 规则影响范围 × 更新兼容性，可能解释实际收益差异。<b>Design：</b>学习前诊断知识与错误模式，固定纠错方式和训练预算，在独立模型副本上检验跨题真实收益。</p>
 <h3>别人研究的是……；我们研究的是……</h3><p><b>Self-Error-Instruct</b> 已按错误类型合成题目，并用 one-shot 示例帮助筛选数据；<b>LESS</b> 已用梯度影响选择训练数据。I8 研究的是当前错误怎样转化为真实持久的跨题学习，以及能否提前预测。<a class="cite" href="references.html#S40" title="Self-Error-Instruct: Generalizing from Errors for LLMs Mathematical Reasoning">[S40]</a><a class="cite" href="references.html#M10" title="LESS: Selecting Influential Data for Targeted Instruction Tuning">[M10]</a></p>
 <p><b>与 I6 的区别：</b>I8 研究哪些错误规则更有可迁移性；<a href="idea-i6-failure-value.html">I6</a> 尽量保持错误规则与最终答案一致，单独研究失败过程作为学习材料的作用。</p><div class="links"><a class="link-btn" href="i8.html">阅读 I8：现象、原因、完整实验与否定条件</a></div>


## I1–I8：八个研究问题 / 这些 Idea 如何证明真的用于 RSI？


 <div class="table-wrap"><table><thead><tr><th>需要分开报告</th><th>最简单的检验办法</th></tr></thead><tbody>
 <tr><td>当前任务变好</td><td>协助、提示或多次尝试后的即时成功率；这是短期表现。</td></tr>
 <tr><td>我自己真的学会</td><td>只保留允许写入的 Skill / Memory / Harness / 权重；撤除教师、伙伴和临时上下文，在新任务上测独立能力。</td></tr>
 <tr><td>我越来越会学习</td><td>保留学到的“选帮助、选学法、选复习、选试验、选伙伴”策略，给新的学习者与新任务，测同预算下是否学得更快。</td></tr>
 </tbody></table></div>
 <p><b>共同对照：</b>同一学习器起点、相同训练/执行预算、固定外部验证器；报告新任务进步、旧任务保持、训练成本和多轮曲线。普通重试、固定规则、随机选择、通用 bandit 是必要基线。任务选择、训练数据和最终测试必须隔离。</p>
 <p><b>安全边界：</b>所有自修改先在受控沙箱中提议、测试、回滚；真实系统权限不随学习成功自动升级。Skill/Memory 写入保存来源与适用条件，拒绝把不稳定、污染或越权的经验固化。这里是协议要求，不是已完成的安全验证。</p>
 <p class="status">截至 2026-10-27：这些是有明确近邻的研究提案，不能声称“首次把教育学用于 RSI”；也不能因为已有相关组件，就断言上述更细化的问题已被解决。</p>


## I6 · 为什么有些错误更值得学习？ / 一句话科学问题


<p class="thesis"><b>I6：</b>同一模型面对同一道题，甚至最终给出相同的错误答案，却可能经历不同的失败过程。为什么使用其中一条失败轨迹纠错，比使用另一条更能帮助模型在后续独立解题时进步？</p>
<p>这里的“学习”必须对应可持续的参数或外置技能更新，之后撤掉原题答案与教师提示再测新题；单次纠错后能复述答案不算学会。</p>
<div class="note"><b>研究边界：</b>本篇只改变提供给固定学习器的<b>失败轨迹</b>，固定教学顺序、反馈形式、示范信息、更新器和训练预算。<a href="idea-i7-learning-order.html">I7</a> 才研究“先看示范还是先自主尝试”，不把两者塞入同一个 Router。</div>


## I6 · 为什么有些错误更值得学习？ / 一个可观察的现象


<div class="card-grid"><article class="research-card"><b>轨迹 A · 直接猜错</b><h3>没有形成有效中间过程</h3><p>模型面对一道多元积分题，直接套用错误公式，给出错误结果。</p></article><article class="research-card"><b>轨迹 B · 尝试后答错</b><h3>形成部分有效步骤</h3><p>同一模型在同题上尝试坐标变换、检查边界，却最终仍得到相同的错误结果。</p></article></div>
<p>两条轨迹从同一个模型检查点产生，问题与最终答案都一致。假设分别用它们作为学习材料，且获得<b>相同正确解法与等预算更新</b>，模型在新积分题上的收益仍可能不同。这是<b>待验证现象</b>，并不是断言 B 一定优于 A。</p>
<p><b>与 I8 不同：</b><a href="i8.html">I8</a> 以高置信度错误、前置知识与规则适用范围为切口，解释什么错误规则经纠正后能够跨题迁移；I6 则尽量固定题目和错误结果，只比较<b>不同失败过程本身</b>作为纠错材料的增量学习收益。高置信度与规则范围不作为 I6 的主要处理变量。</p>


## I6 · 为什么有些错误更值得学习？ / 先解释原因，再定义模块


<div class="table-wrap"><table><thead><tr><th>Challenge · 难在哪里</th><th>Insight · 为什么可能解决</th><th>Design · 如何验证</th></tr></thead><tbody>
<tr><td>当前正确率只能告诉我们“没做对”，不能告诉我们一次纠错将改变多少未来能力。</td><td>错误过程可能暴露已具备的子步骤、错误的知识规则以及缺口与其他题的共享程度。</td><td>先随机抽取失败轨迹，采用固定纠错程序逐条更新；再用未见题的独立增益为每条失败定价。</td></tr>
<tr><td>失败轨迹越长、越接近答案、越自信，可能只是更耗 token 或原本更接近正确。</td><td>学习价值应由更新后的因果收益定义，不能由“表面离正确答案多远”替代。</td><td>匹配题目、初始检查点、错误长度、教师反馈、更新步数与评测；增加错误严重度、置信度、语义相似度强基线。</td></tr>
<tr><td>纠正同一道题不代表学会同一规则，更不代表跨任务迁移。</td><td>某条轨迹可改写只针对原题的模式，也可能揭示跨题共用的推理规则。</td><td>把原题重做、同模板新题、结构变形题和旧能力回归分开统计，并评估多个后续更新之后是否保持。</td></tr>
</tbody></table></div>
<p><b>方法只放最必要的部分：</b>先用标准化纠错更新建立每条失败的实际学习价值，再训练一个轻量 Failure Value Estimator。预测器只能读取<b>纠错前</b>的轨迹特征与历史，不得偷看纠错答案或最终后测。</p>


## I6 · 为什么有些错误更值得学习？ / 最小辨别实验：同题、同反馈、不同错误


<div class="flow"><div><b>冻结学习者版本</b><small>同模型与参数检查点</small></div><div><b>同题采集失败轨迹</b><small>多种随机种子，先核实均错误</small></div><div><b>固定纠错更新</b><small>同一个教师答案 / LoRA 配置</small></div><div><b>无提示后测</b><small>新题迁移、旧能力回归</small></div><div><b>学习价值分析</b><small>解释差异与事前预测</small></div></div>
<p><b>P0：</b>先选一个数学任务族及一组跨题共享规则，收集同一检查点在同一道题上的多条自然失败轨迹。随机指定某条失败轨迹为学习材料；另一分支只读正确解法作基线。每个分支从<b>同一初始检查点</b>重新开始，而不是顺序累积训练。</p>
<p><b>配对控制：</b>优先匹配同一目标题、同一错误终点与已知错误规则，只让失败轨迹的中间过程不同；固定教师正确解法、训练器、token 上限、学习率、更新步数和测试集，并对轨迹长度/额外解释文本做预算敏感性分析。保留“只看答案”“随机失败”“按置信度选错误”“按答案距离选错误”等对照。</p>
<p><b>定义：</b>G(f)=Acc_after(f, D_holdout) − Acc_before(D_holdout)，并同时报告相对于“只看正确解法”的增量；D_holdout 按知识点与模板去重。分层估计同题组内的学习收益差，不把一题上的多个 Probe 当成独立样本。</p>
<p><b>下一步：</b>用不同题/不同模型上的纠错前轨迹预测 G(f)，比较随机选错误、按难度/置信度/长度选错误与收益预测选择；报告预算相同时的迁移增益和选择 regret。</p>


## I6 · 为什么有些错误更值得学习？ / 最近邻：做到了哪里、我们还要回答什么


<div class="table-wrap"><table><thead><tr><th>相关工作</th><th>已研究的关系</th><th>I6 的独立问题</th></tr></thead><tbody>
<tr><td><a href="i8.html">I8：高置信度错误与规则级迁移</a></td><td>针对错误的知识准备程度、规则覆盖范围以及持久更新后的跨题净收益。</td><td>固定题目与错误终点，仅研究<b>失败轨迹过程</b>是否提供额外有用信息。</td></tr>
<tr><td><a href="https://aclanthology.org/2024.acl-long.45/" target="_blank" rel="noopener noreferrer">Learn from Failure · ACL 2024</a></td><td>形式定理证明中，失败搜索轨迹可成为有价值的训练数据。</td><td>不是证明失败“可以用”，而是研究<b>哪条失败更值得用</b>。</td></tr>
<tr><td><a href="https://arxiv.org/abs/2610.13594" target="_blank" rel="noopener noreferrer">MENTOR: Learning from Failure with On-Policy Pedagogical Intervention · 2026 预印本</a></td><td>训练停滞时依据失败原因生成教学提示，帮助恢复学习信号。</td><td>固定教学方式后，仅比较失败轨迹本身的可学习价值，避免归功于更好的提示。</td></tr>
<tr><td><a href="references.html#E08">Productive / Unproductive Failure 学习科学文献</a></td><td>失败及其后续整合可能有不同教学结果。</td><td>把启发转为可审计的模型更新与无教师后测，不声称人类结论自动迁移到 LLM。</td></tr>
</tbody></table></div>
<p class="status">文献证据支持研究动机；同题失败价值差异、预测有效性和跨模型迁移尚待本项目验证。</p>


## I6 · 为什么有些错误更值得学习？ / 怎样决定继续还是停止


<p><b>继续：</b>匹配题目、示范与计算预算后，失败轨迹之间仍有可重复的迁移增益差异；简单的错误严重度、置信度、轨迹长度无法解释全部差异；预测器在未见任务上能减少同预算的错误选择。</p>
<p><b>缩题：</b>只发现纠错收益差异而无法事前预测时，优先做现象与机制分析，不夸大为学习策略优化系统。</p>
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
 <p>这里不是说“越自信就一定越有学习价值”。Sitzman 等（2014）发现，<b>已有领域知识</b>可能比主观置信度更能预测错误纠正；置信度的独立解释力有限。<a class="cite" href="references.html#E14" title="Prior knowledge is more predictive of error correction than subjective confidence">[E14]</a></p>
 <p>Foster 等（2022）在中小学在线数学诊断题中研究了置信度与后续类似题表现，但这种相似题纠正不等于复杂规则在 LLM 中已被更新，也不能直接推断因果。<a class="cite" href="references.html#E15" title="School students’ confidence when answering diagnostic questions online">[E15]</a></p>
 <div class="note"><b>可观察矛盾：</b>错误有多“自信”、一次反馈能否修复该题、以及修复后能迁移多少题，是三个不同的量。Hypercorrection 是提出机制假说的线索，不是已经证明的 LLM 结论。</div>


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
 <tr><td>LESS gradient-based selection <a class="cite" href="references.html#M10" title="LESS: Selecting Influential Data for Targeted Instruction Tuning">[M10]</a></td><td>梯度对齐是否已经足够</td></tr>
 <tr><td>LENS / ACE（学习目标对照）<a class="cite" href="references.html#S43" title="Don&#x27;t Waste Mistakes: Leveraging Negative RL-Groups via Confidence Reweighting">[S43]</a><a class="cite" href="references.html#S44" title="Overconfident Errors Need Stronger Correction: Asymmetric Confidence Penalties for Reinforcement Learning">[S44]</a></td><td>自信错误再加权改善训练信号，是否足够解释收益</td></tr>
 <tr><td>I8：Readiness + Rule Scope + Compatibility</td><td>是否新增可迁移、可解释的预测信息</td></tr>
 </tbody></table></div>
 <p><b>主指标：</b>学习前预测分数与真实未见同规则收益的排序相关；固定训练预算下的净迁移增益；跨模板、跨模型稳定性；回归率。额外报告原题修复率及单条样本筛选成本，防止以更多诊断调用换取假提升。</p>
 <div class="note"><b>强约束：</b>按规则族和模板族划分训练 / 诊断 / 选择验证 / 最终测试；每条候选的训练结果只能用于开发集建模，不能窥视最终测试。按独立规则族聚类计算区间，并单独报告自然错误与注入式错误的结果。</div>


## I8 · 哪些错误纠正一次，能让模型学会一类题？ / Related Work｜不能重复的已有贡献


 <div class="table-wrap"><table><thead><tr><th>工作</th><th>已经做了什么</th><th>I8 需要额外解决什么</th></tr></thead><tbody>
 <tr><td>Hypercorrection 2001 / 2018 <a class="cite" href="references.html#E12" title="Errors committed with high confidence are hypercorrected">[E12]</a><a class="cite" href="references.html#E13" title="Hypercorrection of high-confidence errors in the classroom">[E13]</a></td><td>人类高置信度错误在正确反馈后的超纠正现象</td><td>检验 LLM 上是否成立，以及真正决定迁移的知识状态</td></tr>
 <tr><td>Prior Knowledge 2014 <a class="cite" href="references.html#E14" title="Prior knowledge is more predictive of error correction than subjective confidence">[E14]</a></td><td>领域知识与纠错关系可能强于主观置信度</td><td>从人类单题纠正推进到机器参数更新与跨题迁移</td></tr>
 <tr><td>Self-Error-Instruct（ACL 2025）<a class="cite" href="references.html#S40" title="Self-Error-Instruct: Generalizing from Errors for LLMs Mathematical Reasoning">[S40]</a></td><td>按错误类型合成数据，用 one-shot 帮助效果筛选样本</td><td>区分上下文即时帮助与持久参数更新的真实收益</td></tr>
 <tr><td>LESS（ICML 2024）<a class="cite" href="references.html#M10" title="LESS: Selecting Influential Data for Targeted Instruction Tuning">[M10]</a></td><td>梯度相似性影响力数据选择</td><td>能否从错误知识结构提供额外、低成本的预测信息</td></tr>
 <tr><td>RULE-EDIT（EMNLP 2026）<a class="cite" href="references.html#S41" title="RULE-EDIT: Benchmarking Rule-Level Knowledge Editing in Large Language Models">[S41]</a></td><td>规则编辑的实例可迁移性评测</td><td>学习前预测哪些错误规则能被特定更新有效修复</td></tr>
 <tr><td>LENS / ACE（2025 / 2026）<a class="cite" href="references.html#S43" title="Don&#x27;t Waste Mistakes: Leveraging Negative RL-Groups via Confidence Reweighting">[S43]</a><a class="cite" href="references.html#S44" title="Overconfident Errors Need Stronger Correction: Asymmetric Confidence Penalties for Reinforcement Learning">[S44]</a></td><td>按错误置信度改变 RL 更新惩罚</td><td>目标并非“罚得更重”，而是预测哪些错误值得学习</td></tr>
 <tr><td>Learning Dynamics（ICML 2025）<a class="cite" href="references.html#M11" title="What Do Learning Dynamics Reveal About Generalization in LLM Mathematical Reasoning?">[M11]</a></td><td>训练过程的预记忆表现可以预测泛化</td><td>用尚未进行完整更新的诊断信号预测单次纠错的净收益</td></tr>
 </tbody></table></div>
 <p>因此 I8 <strong>不声称首次利用高置信度错误、首次按错误类别造数据、首次预测数据有用性或首次评估规则级迁移</strong>。可争取的新增贡献是经过严格控制的<strong>错误学习潜力与真实迁移收益之间的机制关系</strong>。</p>


## I8 · 哪些错误纠正一次，能让模型学会一类题？ / 预注册判断｜出现什么结果就停止？


 <p><b>H1：</b>控制已有知识后，高置信度错误的纠正优势可能明显减弱。若无差异，也应如实报告。</p>
 <p><b>H2：</b>在相同更新预算下，知识准备程度与共同错误规则影响范围，对未见题迁移有可复现的交互作用。<strong>这是最核心的机制实验。</strong></p>
 <p><b>H3：</b>学习前诊断相较难度、置信度、SEI one-shot 和 LESS 梯度策略，能够改善真实净迁移收益的预测与学习预算分配。</p>
 <p><b>继续：</b>H2 关系在独立规则族与至少两个模型配置复现，且 H3 对强基线有稳定增益。<b>缩题：</b>只有机制成立、排序方法没优势，则作为实证机制研究。<b>停止：</b>收益仅限原题或近似改写；在控制知识状态、诊断成本和预算后关系消失。</p>
 <div class="status">当前仅完成文献核对、机制假设、对照与门槛设计；无 I8 训练结果、无已证实的新模型能力增益。</div>


## I8 · 哪些错误纠正一次，能让模型学会一类题？ / 与其他 Idea 的边界｜只研究“纠错能否迁移”


 <p><b>I5</b> 问学生的独立执行能否帮助教师发现并修复自己的盲点；<b>I6</b> 的关注点是跨轮失败瓶颈诊断及下一步学习策略；<b>I7</b> 研究“先尝试还是先看示例”的学习次序；<b>I8</b> 固定学习方式之后，研究哪种<strong>模型当前错误</strong>可以被真正学会、迁移到多少未见题。</p>
 <p>I8 可以给 I6 提供一种学习价值信号，但不是 I6 的通用调度器，也不改变 I7 的教学顺序。网站目前保留独立编号，不因其他候选尚未纳入本站而重新编号。</p>
 <div class="links"><a class="link-btn" href="ideas.html">返回候选 Idea</a><a class="link-btn" href="learning-science.html">查看学习科学来源</a><a class="link-btn" href="references.html">查看全部原始来源</a></div>


## 教学反馈诊断 · I5 的早期研究支线 / 研究目标：更新教师，而不是帮学生提高分数


 <p class="status">历史研究支线（2026-10-21）；当前 I5 主线是<a href="ideas.html#idea-5">按自身学习增益动态选择伙伴</a>。此页作为“学生反馈诊断教师盲点”实验方案保留，不等同于当前 I5 主线。</p>
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

## 实验方案与推进门槛 / 按最短证据路径推进

<div class="timeline-rsi"><div><b>第 1 周</b><p>固定版本、官方基线、4 族预检；核验最近邻运行资产。</p></div><div><b>第 2 周</b><p>P0 分叉与统计，筛查 I1 / I2。没有自然失败证据则停。</p></div><div><b>第 3–4 周</b><p>只训练一个核心策略，加入强简单基线，扩第二环境。</p></div><div><b>第 5–6 周</b><p>冻结方法，跨模型、Meta-reset、消融，同步形成初稿。</p></div><div><b>缓冲</b><p>独立重跑、失败案例、来源及许可；证据不足就延长。</p></div></div><div class="note">这是执行目标，不是实验已启动或六周必能投稿的承诺。先判断固定强基线是否足够，比先实现庞大系统更接近明确论文。</div>

## 来源与核验记录 / 核验口径与检索范围

<p>本专题的基础综述始于 2026-10-21；I1–I5 新增最近邻于 2026-10-27 增量核验。定向覆盖 RSI、学习型改进器、课程/元学习、学习科学及实验资源。用论文标题、方法词与引用链交叉检索，优先 arXiv、会议页面、作者机构和官方仓库。</p><p><b>阅读深度不同：</b>“正文方法”表示核对了方法/实验设置，不等于逐条复现全部结果；“摘要”只支持摘要范围的陈述；“官方资源”只确认资产与文档存在。代码入口存在不等于依赖安装、运行、原表重现成功。</p><p><b>原始材料与本次研究：</b>用户分享的推文用于确定入口和问题，不把推文统计或数字自动当作原论文结论。新提案、框架与优先级属于本专题分析，均非文献已经证明的结果。</p><p><b>搜索主题：</b>recursive self-improvement / harness optimization / meta-learning / automated curriculum / learning progress / learner modeling / assistance dilemma / fading / retrieval practice / productive failure / interference replay / skill withdrawal / learning response / selective rehearsal / active failure probing / partner selection / co-distillation。</p><div class="note">这是针对选题的证据地图，不是穷尽全部文献的系统综述。未能核对的作者、发表状态、代码可运行性不补写；预印本标注月份。链接会随论文修订与仓库更新变化，实验须另锁 commit / revision。</div><div class="links"><a class="link-btn" href="sources.json" download>下载来源 JSON</a><a class="link-btn" href="sources.tsv" download>下载来源 TSV</a><a class="link-btn" href="research-notes.md" download>下载整篇研究笔记</a></div>

## 来源与核验记录 / RSI · 44 项

<article class="source-card" id="S01"><div class="source-meta"><span class="ref-id">S01</span><span>arXiv 26.07</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/2607.07663" target="_blank" rel="noopener noreferrer">Recursive Self-Improvement in AI: From Bounded Self-Refinement to Autonomous Research Loops</a></h3><p>按修改对象和闭环程度整理 RSI；用于界定范围，不把一种严格定义当成全领域共识。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2607.07663" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S02"><div class="source-meta"><span class="ref-id">S02</span><span>arXiv 25.05；核对 v3</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/2505.22954" target="_blank" rel="noopener noreferrer">Darwin Godel Machine: Open-Ended Evolution of Self-Improving Agents</a></h3><p>维护代码谱系，以任务执行评价自修改版本；代码自进化与开放式搜索已有系统基础。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2505.22954" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S03"><div class="source-meta"><span class="ref-id">S03</span><span>ICLR 2026 Oral；arXiv 25.07</span><span class="evidence">摘要与官方仓库核对</span></div><h3><a href="https://arxiv.org/abs/2507.19457" target="_blank" rel="noopener noreferrer">GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning</a></h3><p>反思执行轨迹，提出并测试提示修改、组合互补经验；可作共享编辑器和强搜索基线。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2507.19457" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/gepa-ai/gepa" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S04"><div class="source-meta"><span class="ref-id">S04</span><span>arXiv 25.06</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/2506.10943" target="_blank" rel="noopener noreferrer">Self-Adapting Language Models (SEAL)</a></h3><p>生成微调数据和更新指令，以更新后模型表现学习自编辑；属于参数持久更新。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2506.10943" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S05"><div class="source-meta"><span class="ref-id">S05</span><span>arXiv 26.03</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/2603.19461" target="_blank" rel="noopener noreferrer">Hyperagents</a></h3><p>任务 Agent 与修改它的 Meta-Agent 同在可编辑程序中；双层循环本身不再是充分创新。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2603.19461" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S06"><div class="source-meta"><span class="ref-id">S06</span><span>arXiv 26.07</span><span class="evidence">正文方法核对</span></div><h3><a href="https://arxiv.org/abs/2607.05297" target="_blank" rel="noopener noreferrer">MetaSkill-Evolve: Recursive Self-Improvement of LLM Agents via Two-Timescale Meta-Skill Evolution</a></h3><p>快慢时间尺度分别更新任务技能与元技能；与泛化的“改进器积累经验”直接相邻。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2607.05297" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S07"><div class="source-meta"><span class="ref-id">S07</span><span>arXiv 26.08</span><span class="evidence">摘要与官方仓库核对</span></div><h3><a href="https://arxiv.org/abs/2608.02276" target="_blank" rel="noopener noreferrer">Harness-R1: Learning to Edit Executable Runtime Harnesses from Agent Failure Trajectories</a></h3><p>训练专门的 Harness 编辑器，以真实执行表现优化修改；学习生成补丁不是新的空白。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2608.02276" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/DeepExperience/Harness-R1" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S08"><div class="source-meta"><span class="ref-id">S08</span><span>arXiv 26.09</span><span class="evidence">正文方法核对</span></div><h3><a href="https://arxiv.org/abs/2609.35738" target="_blank" rel="noopener noreferrer">Harness Learning Enables Generalizable Test-Time Adaptation</a></h3><p>把 Harness 修改作为元学习问题，学习可迁移适应策略；需比较新任务学习过程。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2609.35738" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S09"><div class="source-meta"><span class="ref-id">S09</span><span>arXiv 26.09</span><span class="evidence">正文方法与官方仓库核对</span></div><h3><a href="https://arxiv.org/abs/2609.14857" target="_blank" rel="noopener noreferrer">ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement</a></h3><p>成败轨迹对照、模块化修改与独立任务迁移；上述三项组合不能直接当作新方向。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2609.14857" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/IQuestLab/ModularRSI" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S10"><div class="source-meta"><span class="ref-id">S10</span><span>arXiv 26.09；核对 26.10 修订摘要</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/2609.24972" target="_blank" rel="noopener noreferrer">RRSI: Regularized Recursive Self-Improvement of Agent Harnesses</a></h3><p>正则化修改提议和选择，缓解递归搜索过拟合；不同修订的实验数字不混用。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2609.24972" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S11"><div class="source-meta"><span class="ref-id">S11</span><span>arXiv 26.09</span><span class="evidence">摘要与项目入口核对</span></div><h3><a href="https://arxiv.org/abs/2609.14858" target="_blank" rel="noopener noreferrer">Dream-RSI: Recursive Self-Improvement through Evolving Worlds</a></h3><p>利用历史发现树回放优化探索策略；回放覆盖范围之外的收益需真实执行验证。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2609.14858" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/zhengkid/Dream-RSI" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S12"><div class="source-meta"><span class="ref-id">S12</span><span>arXiv 26.10</span><span class="evidence">正文方法与官方仓库核对</span></div><h3><a href="https://arxiv.org/abs/2610.14224" target="_blank" rel="noopener noreferrer">Harness²: Recursive Agent Harnessing for an Open World</a></h3><p>任务内修改与跨任务 Harnessing 经验积累；行为对比不等于带标准答案的正确性证明。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2610.14224" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/google-research/harness2" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S13"><div class="source-meta"><span class="ref-id">S13</span><span>arXiv 26.10</span><span class="evidence">摘要与官方仓库核对</span></div><h3><a href="https://arxiv.org/abs/2610.13912" target="_blank" rel="noopener noreferrer">RSI-Anything: Unlocking Recursive Self-Improvement with World Models</a></h3><p>预测行动后果，再以真实反馈校正；环境动力学与学习者更新后能力变化是不同对象。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2610.13912" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/Gen-Verse/RSI-Anything" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S14"><div class="source-meta"><span class="ref-id">S14</span><span>arXiv 26.07</span><span class="evidence">摘要与官方仓库核对</span></div><h3><a href="https://arxiv.org/abs/2607.12227" target="_blank" rel="noopener noreferrer">Rethinking the Evaluation of Harness Evolution for Agents</a></h3><p>强调与等反馈、等推理预算的普通采样和顺序精修比较；复杂流程不能只按得分解释。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2607.12227" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/rethinking-harness-evolution/code" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S15"><div class="source-meta"><span class="ref-id">S15</span><span>arXiv 26.10</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/2610.14662" target="_blank" rel="noopener noreferrer">Does Failure Feedback Direct Agent Self-Modification?</a></h3><p>目标修复、相关失败迁移和独立测试增益须分开；反馈效果具有模型依赖性。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2610.14662" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S16"><div class="source-meta"><span class="ref-id">S16</span><span>arXiv 26.10</span><span class="evidence">正文方法与实验设置核对</span></div><h3><a href="https://arxiv.org/html/2610.00906v1" target="_blank" rel="noopener noreferrer">ActiveSaddler: Automated Curriculum Learning for Agent Harness Optimization</a></h3><p>失败模式作为动态 bandit 臂，以学习进展调整优先级并探索新失败；直接覆盖自动修复课程。</p><div class="links"><a class="link-btn" href="https://arxiv.org/html/2610.00906v1" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S17"><div class="source-meta"><span class="ref-id">S17</span><span>arXiv 26.01；核对 v3</span><span class="evidence">正文方法与实验设置核对</span></div><h3><a href="https://arxiv.org/html/2601.18778v3" target="_blank" rel="noopener noreferrer">Teaching Models to Teach Themselves: Reasoning at the Edge of Learnability (SOAR)</a></h3><p>双层元强化学习让教师出题，以学生在困难题上的实际进步作奖励，而非仅用难度代理。</p><div class="links"><a class="link-btn" href="https://arxiv.org/html/2601.18778v3" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S18"><div class="source-meta"><span class="ref-id">S18</span><span>arXiv 26.10</span><span class="evidence">正文方法与实验设置核对</span></div><h3><a href="https://arxiv.org/html/2610.04604v1" target="_blank" rel="noopener noreferrer">Anticipating the Consequences of Curriculum Decisions with Large Language Models</a></h3><p>将学习进展、下游迁移潜力和当前可学性结合；任务依赖图与前瞻课程已有近邻。</p><div class="links"><a class="link-btn" href="https://arxiv.org/html/2610.04604v1" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/Octavio-Pappalardo/curriculum-foresight" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S19"><div class="source-meta"><span class="ref-id">S19</span><span>arXiv 26.10</span><span class="evidence">正文方法与实验设置核对</span></div><h3><a href="https://arxiv.org/html/2610.06446v1" target="_blank" rel="noopener noreferrer">The Assistance Dilemma: Learning to Teach via Multi-Turn Reinforcement Learning</a></h3><p>遮蔽教师话语的近迁移后测仍保留学生话语；单题回报难覆盖支持撤除的远期价值。</p><div class="links"><a class="link-btn" href="https://arxiv.org/html/2610.06446v1" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/eth-lre/EduardoRL" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S20"><div class="source-meta"><span class="ref-id">S20</span><span>NeurIPS 2024；arXiv 24.06</span><span class="evidence">会议正文与官方仓库核对</span></div><h3><a href="https://proceedings.neurips.cc/paper_files/paper/2024/hash/8340b085045cf13f1f0b6c2c4cc0a89c-Abstract-Conference.html" target="_blank" rel="noopener noreferrer">Can LLMs Learn by Teaching for Better Reasoning? A Preliminary Study</a></h3><p>教师解释根据学生反馈选择；反馈可以构成 DPO 训练偏好；多学生多样性是已有近邻。不能把 teacher 由 student feedback 更新称作首次提出。</p><div class="links"><a class="link-btn" href="https://proceedings.neurips.cc/paper_files/paper/2024/hash/8340b085045cf13f1f0b6c2c4cc0a89c-Abstract-Conference.html" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/imagination-research/lbt" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S21"><div class="source-meta"><span class="ref-id">S21</span><span>AAAI 2026</span><span class="evidence">会议摘要与方法概述核对</span></div><h3><a href="https://ojs.aaai.org/index.php/AAAI/article/view/38668" target="_blank" rel="noopener noreferrer">MARS: Multi-Agent Adaptive Reasoning with Socratic Guidance for Automated Prompt Optimization</a></h3><p>Teacher-Critic-Student Socratic dialogue 用于提示优化；多智能体教学及问题驱动迭代不能单独作为方法创新。</p><div class="links"><a class="link-btn" href="https://ojs.aaai.org/index.php/AAAI/article/view/38668" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S22"><div class="source-meta"><span class="ref-id">S22</span><span>arXiv 26.07</span><span class="evidence">摘要与作者公开说明核对</span></div><h3><a href="https://arxiv.org/abs/2607.28048" target="_blank" rel="noopener noreferrer">SKILL-KD: Contrastive Skill Distillation for LLM Agents</a></h3><p>对比教师成功与学生失败轨迹，迭代修改学生的技能；本候选必须与“更新教师自己”区分，并避免只做反向技能蒸馏。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2607.28048" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S23"><div class="source-meta"><span class="ref-id">S23</span><span>arXiv 26.08</span><span class="evidence">论文正文与摘要核对</span></div><h3><a href="https://arxiv.org/abs/2608.20274" target="_blank" rel="noopener noreferrer">Break It Down, Pass It On: Cross-Task Skill Transfer in LLM Agents</a></h3><p>子任务级和任务级技能、文本与代码技能对跨任务迁移有不同影响；要求本候选与直接细粒度技能归纳和静态技能质量评价比较。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2608.20274" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S24"><div class="source-meta"><span class="ref-id">S24</span><span>arXiv 25.12</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/2512.13102" target="_blank" rel="noopener noreferrer">Socratic Students: Teaching Language Models to Learn by Asking Questions</a></h3><p>训练学生主动询问教师以改善学生的学习效率；不能把会追问的 Student 当作空白，需证明问题对 Teacher 自身能力有独立信息。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2512.13102" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S25"><div class="source-meta"><span class="ref-id">S25</span><span>arXiv 23.11</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/2311.06985" target="_blank" rel="noopener noreferrer">Large Language Models are In-context Teachers for Knowledge Reasoning</a></h3><p>提出 Self-Explain 和 Teach-Back 来提高学生的 in-context knowledge reasoning；Teach-Back 名称本身不保证与教师自进化相关。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2311.06985" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S26"><div class="source-meta"><span class="ref-id">S26</span><span>arXiv 26.10</span><span class="evidence">原始摘要核对；2026-10-27</span></div><h3><a href="https://arxiv.org/abs/2610.22740" target="_blank" rel="noopener noreferrer">R²Orch: Recursive Self-Improvement for Agent Orchestration via Self-Play within a Skill-Internalization Loop</a></h3><p>通过自博弈将经验蒸馏为技能再内化进参数；以撤掉技能后效果是否保持决定 Skill Withdrawal。I1 研究何时该内化、何时保留外部支持。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2610.22740" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S27"><div class="source-meta"><span class="ref-id">S27</span><span>arXiv 26.07</span><span class="evidence">正文方法核对；2026-10-27</span></div><h3><a href="https://arxiv.org/abs/2607.21419" target="_blank" rel="noopener noreferrer">PATS: Policy-Aware Training Scaffolding for Agentic Reinforcement Learning</a></h3><p>针对当前策略调整训练时支架，冗余时压缩或撤除，部署时不保留支架。I1 不能把随能力渐隐提示当成首次提出。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2607.21419" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/shi-yipeng/PATS" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S28"><div class="source-meta"><span class="ref-id">S28</span><span>arXiv 26.10</span><span class="evidence">原始摘要核对；2026-10-27</span></div><h3><a href="https://arxiv.org/abs/2610.21791" target="_blank" rel="noopener noreferrer">RSIFlow: Adaptive Self-Improvement Workflows with an Evolving Meta-Agent</a></h3><p>依据任务轨迹和反馈诊断瓶颈，选择模型、Harness 或产物更新流程，并改进 Meta-Agent。I2 需聚焦同一更新对象内部的学习方法反应。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2610.21791" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/1HUAN1/RSI-Flow" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S29"><div class="source-meta"><span class="ref-id">S29</span><span>arXiv 26.08</span><span class="evidence">原始摘要核对；2026-10-27</span></div><h3><a href="https://arxiv.org/abs/2608.19013" target="_blank" rel="noopener noreferrer">Harness Continual Learning: Continual Adaptation Beyond Model Parameters</a></h3><p>Harness 更新前检查新进步、历史保持和有效性，提出 harness-level forgetting。I3 应区分主动冲突巩固与事后守门。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2608.19013" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S30"><div class="source-meta"><span class="ref-id">S30</span><span>arXiv 26.07</span><span class="evidence">原始摘要核对；2026-10-27</span></div><h3><a href="https://arxiv.org/abs/2607.26643" target="_blank" rel="noopener noreferrer">Rethinking Self-Evolution: A Constrained Exploration-Exploitation Process for Mitigating Skill Overfitting (SkillBoost)</a></h3><p>结合结构化故障定位、候选探索与回归约束决定是否接受 Skill 修改。I3 研究保留有用新更新时怎样定向修复旧技能冲突。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2607.26643" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S31"><div class="source-meta"><span class="ref-id">S31</span><span>EMNLP 2026；arXiv 26.03</span><span class="evidence">会议摘要核对；2026-10-27</span></div><h3><a href="https://aclanthology.org/2026.emnlp-main.758/" target="_blank" rel="noopener noreferrer">Trace2Skill: Distill Trajectory-Local Lessons into Transferable Agent Skills</a></h3><p>并行分析多条执行轨迹，归纳为可复用且尽量无冲突的技能。I4 不是再次强调多轨迹，而是决定何时需要追加辨别实验、何时证据足够归纳。</p><div class="links"><a class="link-btn" href="https://aclanthology.org/2026.emnlp-main.758/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/Qwen-Applications/Trace2Skill" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S32"><div class="source-meta"><span class="ref-id">S32</span><span>arXiv 26.05</span><span class="evidence">原始摘要与作者说明核对；2026-10-27</span></div><h3><a href="https://arxiv.org/abs/2605.16727" target="_blank" rel="noopener noreferrer">PopuLoRA: Co-Evolving LLM Populations for Reasoning Self-Play</a></h3><p>教师 LoRA 生成任务，匹配学生求解，通过跨群体评估促进共同进化；I5 改问伙伴给我带来的后续独立学习收益。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2605.16727" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S33"><div class="source-meta"><span class="ref-id">S33</span><span>arXiv 26.06</span><span class="evidence">原始摘要核对；2026-10-27</span></div><h3><a href="https://arxiv.org/abs/2606.14368" target="_blank" rel="noopener noreferrer">Be My Tutor: On-Policy Co-Distillation for Mutual LLM Improvement via Peer Feedback (OPCoD)</a></h3><p>两个跨领域互补模型互相教学；通过认知门控决定是否给反馈并以问题锚定反馈。I5 要研究学习伙伴本身的跨阶段选择。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2606.14368" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S34"><div class="source-meta"><span class="ref-id">S34</span><span>arXiv 26.07</span><span class="evidence">原始摘要核对；2026-10-27</span></div><h3><a href="https://arxiv.org/abs/2607.11250" target="_blank" rel="noopener noreferrer">Multi-Agent LLMs Fail to Explore Each Other (MACE: Multi-Agent Contextual Exploration)</a></h3><p>以结构化同伴选择促进探索和协作任务表现；I5 必须区分当前协作收益与伙伴退出后的独立能力增长，且不与同名记忆方法混淆。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2607.11250" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/deeplearning-wisc/mace" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S35"><div class="source-meta"><span class="ref-id">S35</span><span>ICLR 2025</span><span class="evidence">ICLR 官方摘要核对；2026-10-27</span></div><h3><a href="https://proceedings.iclr.cc/paper_files/paper/2025/hash/63943ee9fe347f3d95892cf87d9a42e6-Abstract-Conference.html" target="_blank" rel="noopener noreferrer">Mind the Gap: Examining the Self-Improvement Capabilities of Large Language Models</a></h3><p>研究生成—验证差距与反复自我提升的条件。I6 不能将生成/验证/更新拆分称为首次，而应验证跨轮瓶颈变化及选择收益。</p><div class="links"><a class="link-btn" href="https://proceedings.iclr.cc/paper_files/paper/2025/hash/63943ee9fe347f3d95892cf87d9a42e6-Abstract-Conference.html" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S36"><div class="source-meta"><span class="ref-id">S36</span><span>arXiv 26.09</span><span class="evidence">arXiv 原始摘要核对；2026-10-27</span></div><h3><a href="https://arxiv.org/abs/2609.34327" target="_blank" rel="noopener noreferrer">Knowing When Thinking Is Not Enough: Teaching Small Reasoning Models to Reason Beyond Their Parametric Knowledge (FlyBy)</a></h3><p>通过中途干预区分知识与执行瓶颈，训练小模型选择性向更强模型查询；不等于持续参数/Skill 更新后的跨轮学习模式切换。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2609.34327" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S37"><div class="source-meta"><span class="ref-id">S37</span><span>ACL 2026</span><span class="evidence">ACL 官方摘要核对；2026-10-27</span></div><h3><a href="https://aclanthology.org/2026.acl-long.1393/" target="_blank" rel="noopener noreferrer">Why Supervised Fine-Tuning Fails to Learn: A Systematic Study of Incomplete Learning in Large Language Models</a></h3><p>分析训练数据未被吸收的五类原因，并对 SFT 不完全学习执行有针对性的干预；与 I6 的吸收检查高度重合。</p><div class="links"><a class="link-btn" href="https://aclanthology.org/2026.acl-long.1393/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S38"><div class="source-meta"><span class="ref-id">S38</span><span>COLM 2026</span><span class="evidence">COLM 官方摘要核对；2026-10-27</span></div><h3><a href="https://proceedings.colm.cc/paper_files/paper/2026/hash/9cdb4f8c4dfa13284d2d5a6e7853e5a2-Abstract-Conference.html" target="_blank" rel="noopener noreferrer">Unifying Group-Relative and Self-Distillation Policy Optimization via Sample Routing (SRPO)</a></h3><p>按采样结果将 GRPO 和自蒸馏组合，并针对训练阶段稳定性做调权；I6 需证明跨环节诊断的额外价值。</p><div class="links"><a class="link-btn" href="https://proceedings.colm.cc/paper_files/paper/2026/hash/9cdb4f8c4dfa13284d2d5a6e7853e5a2-Abstract-Conference.html" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S39"><div class="source-meta"><span class="ref-id">S39</span><span>EMNLP 2026</span><span class="evidence">ACL Anthology 官方摘要核对；2026-10-27</span></div><h3><a href="https://aclanthology.org/2026.emnlp-main.464/" target="_blank" rel="noopener noreferrer">From Rollouts to Recipes: Self-Contained Post-Training for LLMs</a></h3><p>按正确率与置信度路由 GRPO、自蒸馏、正则或跳过，路由比例随训练改变；I6 最接近的动态配方基线之一。</p><div class="links"><a class="link-btn" href="https://aclanthology.org/2026.emnlp-main.464/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S40"><div class="source-meta"><span class="ref-id">S40</span><span>ACL 2025</span><span class="evidence">ACL 正式论文摘要与方法流程核对</span></div><h3><a href="https://aclanthology.org/2025.acl-long.417/" target="_blank" rel="noopener noreferrer">Self-Error-Instruct: Generalizing from Errors for LLMs Mathematical Reasoning</a></h3><p>从模型错题聚类错误类型、合成数据，并用 one-shot 效果筛选微调数据；I8 不能声称首次按错误类型发现迁移价值。</p><div class="links"><a class="link-btn" href="https://aclanthology.org/2025.acl-long.417/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S41"><div class="source-meta"><span class="ref-id">S41</span><span>Findings of EMNLP 2026</span><span class="evidence">ACL Anthology 正式论文摘要核对</span></div><h3><a href="https://aclanthology.org/2026.findings-emnlp.1924/" target="_blank" rel="noopener noreferrer">RULE-EDIT: Benchmarking Rule-Level Knowledge Editing in Large Language Models</a></h3><p>验证数学抽象规则的直接编辑可能不迁移到实例；其知识编辑设置不直接等同于 SFT 或 LoRA 纠错。</p><div class="links"><a class="link-btn" href="https://aclanthology.org/2026.findings-emnlp.1924/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S42"><div class="source-meta"><span class="ref-id">S42</span><span>EMNLP 2026</span><span class="evidence">ACL Anthology 正式论文摘要核对</span></div><h3><a href="https://aclanthology.org/2026.emnlp-main.421/" target="_blank" rel="noopener noreferrer">Editing Rules in LLMs Requires More Than a Localized Update</a></h3><p>提出多层分布式规则编辑，不同形式的规则知识对应不同表示层；说明公式记忆与实例应用的编辑一致性并非自动成立。</p><div class="links"><a class="link-btn" href="https://aclanthology.org/2026.emnlp-main.421/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S43"><div class="source-meta"><span class="ref-id">S43</span><span>arXiv 25.10</span><span class="evidence">arXiv 摘要核对</span></div><h3><a href="https://arxiv.org/abs/2510.08696" target="_blank" rel="noopener noreferrer">Don&#x27;t Waste Mistakes: Leveraging Negative RL-Groups via Confidence Reweighting</a></h3><p>LENS 对高置信度错误增加惩罚以利用 GRPO 全错组，属于 RL 更新信号设计，并不直接预测一次错题的跨题学习收益。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2510.08696" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S44"><div class="source-meta"><span class="ref-id">S44</span><span>arXiv 26.02</span><span class="evidence">arXiv 摘要核对</span></div><h3><a href="https://arxiv.org/abs/2602.21420" target="_blank" rel="noopener noreferrer">Overconfident Errors Need Stronger Correction: Asymmetric Confidence Penalties for Reinforcement Learning</a></h3><p>ACE 利用相对参考策略的置信度位移调整错误 rollout 惩罚；与预测规则级净迁移收益的选题相邻但不相同。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2602.21420" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article>

## 来源与核验记录 / 相邻领域 · 11 项

<article class="source-card" id="M01"><div class="source-meta"><span class="ref-id">M01</span><span>arXiv 16.06</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/1606.04474" target="_blank" rel="noopener noreferrer">Learning to learn by gradient descent by gradient descent</a></h3><p>学习优化算法而非只优化任务模型；更新规则可作为学习对象，但不提供通用 RSI 保证。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/1606.04474" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="M02"><div class="source-meta"><span class="ref-id">M02</span><span>arXiv 16.11</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/1611.02779" target="_blank" rel="noopener noreferrer">RL²: Fast Reinforcement Learning via Slow Reinforcement Learning</a></h3><p>跨任务训练快速适应算法；启发重置学习者、保留元策略的检验。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/1611.02779" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="M03"><div class="source-meta"><span class="ref-id">M03</span><span>arXiv 17.04</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/1704.03003" target="_blank" rel="noopener noreferrer">Automated Curriculum Learning for Neural Networks</a></h3><p>用非平稳 bandit 和学习进度选择训练数据；难度改为进展并非新颖机制。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/1704.03003" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="M04"><div class="source-meta"><span class="ref-id">M04</span><span>arXiv 17.07</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/1707.00183" target="_blank" rel="noopener noreferrer">Teacher-Student Curriculum Learning (TSCL)</a></h3><p>优先练习进步快的子任务，也重访性能下降的任务；学习和防遗忘联合调度已有经典基线。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/1707.00183" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/tambetm/TSCL" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="M05"><div class="source-meta"><span class="ref-id">M05</span><span>NeurIPS 2015</span><span class="evidence">会议原始摘要核对</span></div><h3><a href="https://papers.nips.cc/paper/5654-deep-knowledge-tracing" target="_blank" rel="noopener noreferrer">Deep Knowledge Tracing</a></h3><p>从学习交互序列估计学生知识状态；下一题正确率预测不等于某种教学干预的因果收益。</p><div class="links"><a class="link-btn" href="https://papers.nips.cc/paper/5654-deep-knowledge-tracing" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="M06"><div class="source-meta"><span class="ref-id">M06</span><span>NeurIPS 2018</span><span class="evidence">会议原始摘要核对</span></div><h3><a href="https://proceedings.neurips.cc/paper/2018/hash/8051a3c40561002834e59d566b7430cf-Abstract.html" target="_blank" rel="noopener noreferrer">Learning to Teach with Dynamic Loss Functions</a></h3><p>教师按学生阶段输出动态损失，以开发集表现优化教学；应迁移双层目标而非师生角色名称。</p><div class="links"><a class="link-btn" href="https://proceedings.neurips.cc/paper/2018/hash/8051a3c40561002834e59d566b7430cf-Abstract.html" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="M07"><div class="source-meta"><span class="ref-id">M07</span><span>arXiv 15.10</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/1510.03591" target="_blank" rel="noopener noreferrer">Dual Control for Approximate Bayesian Reinforcement Learning</a></h3><p>行动同时改变状态并揭示未知动力学；需验证诊断信息是否真正改变后续更新决策。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/1510.03591" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="M08"><div class="source-meta"><span class="ref-id">M08</span><span>ICLR 2016；arXiv 15.11</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/1511.05952" target="_blank" rel="noopener noreferrer">Prioritized Experience Replay</a></h3><p>按经验重要性非均匀重放；间隔练习方案必须排除普通优先重放即可解释收益。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/1511.05952" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="M09"><div class="source-meta"><span class="ref-id">M09</span><span>NeurIPS 2019；arXiv 19.08</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/1908.04742" target="_blank" rel="noopener noreferrer">Online Continual Learning with Maximally Interfered Retrieval</a></h3><p>选择可能被当前更新干扰的旧样本重放；作为干扰感知巩固的重要对照。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/1908.04742" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="M10"><div class="source-meta"><span class="ref-id">M10</span><span>ICML 2024</span><span class="evidence">PMLR 正式论文摘要核对</span></div><h3><a href="https://proceedings.mlr.press/v235/xia24c.html" target="_blank" rel="noopener noreferrer">LESS: Selecting Influential Data for Targeted Instruction Tuning</a></h3><p>以优化器感知的低秩梯度相似性估计训练数据影响力；I8 必须与之比较而非声称训练前价值预测全新。</p><div class="links"><a class="link-btn" href="https://proceedings.mlr.press/v235/xia24c.html" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="M11"><div class="source-meta"><span class="ref-id">M11</span><span>ICML 2025</span><span class="evidence">PMLR 正式论文摘要核对</span></div><h3><a href="https://proceedings.mlr.press/v267/kang25f.html" target="_blank" rel="noopener noreferrer">What Do Learning Dynamics Reveal About Generalization in LLM Mathematical Reasoning?</a></h3><p>用预记忆阶段的训练题表现解释泛化并改进数据筛选，说明原题正确与记住解题步骤不同；不直接等于更新前单错题净迁移预测。</p><div class="links"><a class="link-btn" href="https://proceedings.mlr.press/v267/kang25f.html" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article>

## 来源与核验记录 / 学习科学 · 15 项

<article class="source-card" id="E01"><div class="source-meta"><span class="ref-id">E01</span><span>Theory Into Practice, 2002</span><span class="evidence">理论综述与元数据核对</span></div><h3><a href="https://www.tandfonline.com/doi/abs/10.1207/s15430421tip4102_2" target="_blank" rel="noopener noreferrer">Becoming a Self-Regulated Learner: An Overview</a></h3><p>自我调节的前瞻、执行监控与反思是设计视角；不是增加三个 Agent 模块即可有效的证明。</p><div class="links"><a class="link-btn" href="https://www.tandfonline.com/doi/abs/10.1207/s15430421tip4102_2" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E02"><div class="source-meta"><span class="ref-id">E02</span><span>Journal of Memory and Language, 2005</span><span class="evidence">作者存档与摘要核对</span></div><h3><a href="https://www.columbia.edu/cu/psychology/metcalfe/PDFs/Metcalfe%20Kornell%202005.pdf" target="_blank" rel="noopener noreferrer">A Region of Proximal Learning model of study time allocation</a></h3><p>在尚未掌握且可取得进展的材料间分配时间；不等同于挑最难题，也不与其他近侧发展区理论混称。</p><div class="links"><a class="link-btn" href="https://www.columbia.edu/cu/psychology/metcalfe/PDFs/Metcalfe%20Kornell%202005.pdf" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E03"><div class="source-meta"><span class="ref-id">E03</span><span>Psychological Science, 2006</span><span class="evidence">原始研究摘要核对</span></div><h3><a href="https://pubmed.ncbi.nlm.nih.gov/16507066/" target="_blank" rel="noopener noreferrer">Test-enhanced learning: taking memory tests improves long-term retention</a></h3><p>比较练习性检索与重复阅读的保持效果；冻结模型需要持久写入才能形成跨会话学习。</p><div class="links"><a class="link-btn" href="https://pubmed.ncbi.nlm.nih.gov/16507066/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E04"><div class="source-meta"><span class="ref-id">E04</span><span>Psychological Science, 2008</span><span class="evidence">原始研究摘要核对</span></div><h3><a href="https://pubmed.ncbi.nlm.nih.gov/19076480/" target="_blank" rel="noopener noreferrer">Spacing effects in learning: a temporal ridgeline of optimal retention</a></h3><p>间隔效果依赖保持时长；机器实验应操纵中间学习和干扰，不假定静止参数随时间遗忘。</p><div class="links"><a class="link-btn" href="https://pubmed.ncbi.nlm.nih.gov/19076480/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E05"><div class="source-meta"><span class="ref-id">E05</span><span>Journal of Educational Psychology, 2003</span><span class="evidence">作者机构摘要核对</span></div><h3><a href="https://asu.elsevierpure.com/en/publications/transitioning-from-studying-examples-to-solving-problems-effects-/" target="_blank" rel="noopener noreferrer">Transitioning From Studying Examples to Solving Problems: Effects of Self-Explanation Prompts and Fading Worked-Out Steps</a></h3><p>研究例题到自主解题、逐步撤去步骤及自我解释；支持撤除是教学干预，不只是评测删提示。</p><div class="links"><a class="link-btn" href="https://asu.elsevierpure.com/en/publications/transitioning-from-studying-examples-to-solving-problems-effects-/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E06"><div class="source-meta"><span class="ref-id">E06</span><span>Learning: Research and Practice, 2015</span><span class="evidence">作者机构摘要核对</span></div><h3><a href="https://repository.nie.edu.sg/entities/publication/cd4409fb-a12f-476f-ad02-febbf9caa4cc" target="_blank" rel="noopener noreferrer">Learning from productive failure</a></h3><p>生成探索后进行知识整理巩固；关键在教学次序与整合，不是错误越多越好。</p><div class="links"><a class="link-btn" href="https://repository.nie.edu.sg/entities/publication/cd4409fb-a12f-476f-ad02-febbf9caa4cc" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E07"><div class="source-meta"><span class="ref-id">E07</span><span>Educational Psychology Review, 2007</span><span class="evidence">作者机构记录与论文摘要核对</span></div><h3><a href="https://act-r.psy.cmu.edu/?post_type=publications&amp;p=14210" target="_blank" rel="noopener noreferrer">Exploring the assistance dilemma in experiments with Cognitive Tutors</a></h3><p>何时、以何种程度帮助是教学设计问题；不能直接推出 LLM 上的有效性。</p><div class="links"><a class="link-btn" href="https://act-r.psy.cmu.edu/?post_type=publications&amp;p=14210" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E08"><div class="source-meta"><span class="ref-id">E08</span><span>Educational Psychologist, 2016</span><span class="evidence">作者机构摘要核对</span></div><h3><a href="https://repository.eduhk.hk/en/publications/examining-productive-failure-productive-success-unproductive-fail-5/" target="_blank" rel="noopener noreferrer">Examining productive failure, productive success, unproductive failure, and unproductive success in learning</a></h3><p>区分学习时表现与长期学习收益；用于提出测量问题，机器机制须另行验证。</p><div class="links"><a class="link-btn" href="https://repository.eduhk.hk/en/publications/examining-productive-failure-productive-success-unproductive-fail-5/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E09"><div class="source-meta"><span class="ref-id">E09</span><span>Journal of the Learning Sciences, 2013</span><span class="evidence">完整论文机制与实验设计核对</span></div><h3><a href="https://aaalab.stanford.edu/research/assets/papers/2013/Learning_by_teaching_human_pupils.pdf" target="_blank" rel="noopener noreferrer">Learning by Teaching Human Pupils and Teachable Agents: The Importance of Recursive Feedback</a></h3><p>Recursive Feedback 要求学生在新环境中自主使用所学以及教师把学生行为映射回自己的理解；人类机制不能直接视为 LLM 有效性。</p><div class="links"><a class="link-btn" href="https://aaalab.stanford.edu/research/assets/papers/2013/Learning_by_teaching_human_pupils.pdf" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E10"><div class="source-meta"><span class="ref-id">E10</span><span>Behaviormetrika, 2026</span><span class="evidence">正文摘要与研究设计核对</span></div><h3><a href="https://link.springer.com/article/10.1007/s41237-026-00294-9" target="_blank" rel="noopener noreferrer">Beyond prior knowledge: the predictive role of knowledge-building in tutor learning</a></h3><p>人类教师面对 teachable agent 追问时 knowledge-building 比 knowledge-telling 更具诊断意义，相关性结果不是 LLM 教学自进化的因果证据。</p><div class="links"><a class="link-btn" href="https://link.springer.com/article/10.1007/s41237-026-00294-9" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E11"><div class="source-meta"><span class="ref-id">E11</span><span>Journal of Experimental Psychology: General, 2003</span><span class="evidence">PubMed 论文摘要与书目信息核对；2026-10-27</span></div><h3><a href="https://pubmed.ncbi.nlm.nih.gov/14640846/" target="_blank" rel="noopener noreferrer">The Dynamics of Learning and Allocation of Study Time to a Region of Proximal Learning</a></h3><p>人类实验显示把有限学习时间分配给中等难度材料可能取得更高收益；用于提分/任务选择假设，不可直接当作 RSI 实证。</p><div class="links"><a class="link-btn" href="https://pubmed.ncbi.nlm.nih.gov/14640846/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E12"><div class="source-meta"><span class="ref-id">E12</span><span>Journal of Experimental Psychology: Learning, Memory, and Cognition, 2001</span><span class="evidence">PubMed 摘要与 DOI 核对</span></div><h3><a href="https://pubmed.ncbi.nlm.nih.gov/11713883/" target="_blank" rel="noopener noreferrer">Errors committed with high confidence are hypercorrected</a></h3><p>在人类事实知识回答中，高置信度错误得到正确反馈后更可能在复测中纠正；不是 LLM 的直接证据。</p><div class="links"><a class="link-btn" href="https://pubmed.ncbi.nlm.nih.gov/11713883/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E13"><div class="source-meta"><span class="ref-id">E13</span><span>Memory, 2018</span><span class="evidence">期刊摘要与 DOI 核对</span></div><h3><a href="https://pubmed.ncbi.nlm.nih.gov/29781391/" target="_blank" rel="noopener noreferrer">Hypercorrection of high-confidence errors in the classroom</a></h3><p>大学园艺课堂学生答题、报告置信度并接受正确反馈，后测观察到超纠正；不能直接解释为跨题规则迁移。</p><div class="links"><a class="link-btn" href="https://pubmed.ncbi.nlm.nih.gov/29781391/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E14"><div class="source-meta"><span class="ref-id">E14</span><span>Memory &amp; Cognition, 2014</span><span class="evidence">PubMed 摘要与 DOI 核对</span></div><h3><a href="https://pubmed.ncbi.nlm.nih.gov/23797971/" target="_blank" rel="noopener noreferrer">Prior knowledge is more predictive of error correction than subjective confidence</a></h3><p>领域已有知识与纠错关系强，置信度独立解释力小；可能是已有知识的代理指标，而非其全部因果机制。</p><div class="links"><a class="link-btn" href="https://pubmed.ncbi.nlm.nih.gov/23797971/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E15"><div class="source-meta"><span class="ref-id">E15</span><span>Educational Studies in Mathematics, 2022（2021 online）</span><span class="evidence">期刊正文摘要与出版时间核对</span></div><h3><a href="https://link.springer.com/article/10.1007/s10649-021-10084-7" target="_blank" rel="noopener noreferrer">School students’ confidence when answering diagnostic questions online</a></h3><p>在线数学诊断数据研究学生置信度、答题正确率及后续相似题表现；不等于 LLM 的真实权重更新。</p><div class="links"><a class="link-btn" href="https://link.springer.com/article/10.1007/s10649-021-10084-7" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article>

## 来源与核验记录 / 实验资源 · 7 项

<article class="source-card" id="B01"><div class="source-meta"><span class="ref-id">B01</span><span>Findings of NAACL 2025；arXiv 24.08</span><span class="evidence">会议页面与官方介绍核对</span></div><h3><a href="https://aclanthology.org/2025.findings-naacl.65/" target="_blank" rel="noopener noreferrer">ToolSandbox: A Stateful, Conversational, Interactive Evaluation Benchmark for LLM Tool Use Capabilities</a></h3><p>带状态工具执行、用户模拟与轨迹里程碑；派生训练任务须与官方评测隔离。</p><div class="links"><a class="link-btn" href="https://aclanthology.org/2025.findings-naacl.65/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/apple/ToolSandbox" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="B02"><div class="source-meta"><span class="ref-id">B02</span><span>官方资源；核对 2026-10-21</span><span class="evidence">官方文档核对</span></div><h3><a href="https://github.com/sierra-research/tau2-bench" target="_blank" rel="noopener noreferrer">τ-bench / τ²-bench：官方仓库与版本化评测协议</a></h3><p>当前仓库持续演进，不能把 main 与论文 τ² 任务集混用；记录 commit、任务清单和模拟器。</p><div class="links"><a class="link-btn" href="https://github.com/sierra-research/tau2-bench" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/sierra-research/tau2-bench" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="B03"><div class="source-meta"><span class="ref-id">B03</span><span>官方资源；核对 2026-10-21</span><span class="evidence">官方仓库核对</span></div><h3><a href="https://github.com/harbor-framework/terminal-bench-2-1" target="_blank" rel="noopener noreferrer">Terminal-Bench 2.1</a></h3><p>可执行终端任务；固定容器、测试和超时，最终测试不得训练元策略。</p><div class="links"><a class="link-btn" href="https://github.com/harbor-framework/terminal-bench-2-1" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/harbor-framework/harbor" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="B04"><div class="source-meta"><span class="ref-id">B04</span><span>官方模型卡；核对 2026-10-21</span><span class="evidence">官方模型卡核对</span></div><h3><a href="https://huggingface.co/Qwen/Qwen3.5-9B" target="_blank" rel="noopener noreferrer">Qwen3.5-9B</a></h3><p>主学习者与元控制器初始化候选；工具解析、训练与吞吐尚待实际运行验证。</p><div class="links"><a class="link-btn" href="https://huggingface.co/Qwen/Qwen3.5-9B" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="B05"><div class="source-meta"><span class="ref-id">B05</span><span>官方模型资源；核对 2026-10-21</span><span class="evidence">官方模型目录核对</span></div><h3><a href="https://huggingface.co/Qwen/Qwen3.5-27B" target="_blank" rel="noopener noreferrer">Qwen3.5-27B</a></h3><p>同家族强模型对照；选型为保证可比性，不声称它是最新最强模型。</p><div class="links"><a class="link-btn" href="https://huggingface.co/Qwen/Qwen3.5-27B" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="B06"><div class="source-meta"><span class="ref-id">B06</span><span>官方模型卡；核对 2026-10-21</span><span class="evidence">官方模型卡核对</span></div><h3><a href="https://huggingface.co/google/gemma-4-31B-it" target="_blank" rel="noopener noreferrer">Gemma 4 31B instruction-tuned</a></h3><p>跨家族目标模型候选；固定工具与预算，并单独记录模型替换后的校准开销。</p><div class="links"><a class="link-btn" href="https://huggingface.co/google/gemma-4-31B-it" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="B07"><div class="source-meta"><span class="ref-id">B07</span><span>官方资源；核对 2026-10-21</span><span class="evidence">官方 README 与实验切分核对</span></div><h3><a href="https://github.com/StonyBrookNLP/appworld" target="_blank" rel="noopener noreferrer">AppWorld Benchmark: executable app-ecosystem agent tasks</a></h3><p>官方 train / dev / test_normal / test_challenge 严格隔离；后两者只能用于冻结终评，不得按任务反馈修改教学方法。</p><div class="links"><a class="link-btn" href="https://github.com/StonyBrookNLP/appworld" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/StonyBrookNLP/appworld" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article>


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
