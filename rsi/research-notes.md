# RSI × 自主学习研究

核验日期：2026-10-21

本文件包含证据综述与待验证提案，不包含本项目实验结果。

## RSI × 自主学习研究 / 本轮判断：先研究“怎样学会”，而不是再造一个大框架

<div class="decision"><span class="kicker">RESEARCH POSITION · 2026.10</span><h3>优先检验：帮助是否转化为可保留的独立能力？</h3><p>建议把主线收敛为<strong>跨多轮学习的支持获取、撤除与能力巩固</strong>。相邻备选是<strong>学习者响应建模</strong>：预测某种学习干预对未来多项能力的作用，而不只预测眼前补丁是否通过。</p><p>这是本轮调研后的<strong>研究建议，不是已确认的新颖性或实验结果</strong>。先做短程与长程目标的辨别实验，再决定是否训练完整元策略。</p></div><p>近期近邻已相当具体：ActiveSaddler 覆盖失败驱动课程；SOAR 用真实学习收益训练出题者；前瞻课程工作考虑下游迁移；EduardoRL 已区分帮助完成与学习收益。不能把这些笼统概念单独当创新。<a class="cite" href="references.html#S16" title="ActiveSaddler: Automated Curriculum Learning for Agent Harness Optimization">[S16]</a><a class="cite" href="references.html#S17" title="Teaching Models to Teach Themselves: Reasoning at the Edge of Learnability (SOAR)">[S17]</a><a class="cite" href="references.html#S18" title="Anticipating the Consequences of Curriculum Decisions with Large Language Models">[S18]</a><a class="cite" href="references.html#S19" title="The Assistance Dilemma: Learning to Teach via Multi-Turn Reinforcement Learning">[S19]</a></p>

## RSI × 自主学习研究 / 十个研究页面：时间轴 → 证据 → 方法 → 实验

<div class="route-grid"><a href="timeline.html"><b>01 · RSI 研究时间轴</b><span>CVPR / ICML / ACL DDL、精读卡片与研究记录。</span></a><a href="literature.html"><b>02 · RSI 文献与竞争边界</b><span>修改什么、学习什么、什么已经有人做。</span></a><a href="reading-cards.html"><b>03 · 论文精读卡片</b><span>长期积累：一眼记住论文问题、机制、证据与对我们的启发。</span></a><a href="cross-domain.html"><b>04 · 相邻领域的方法迁移</b><span>元学习、课程、知识追踪、双重控制、持续学习。</span></a><a href="learning-science.html"><b>05 · 教育学与学习科学</b><span>来源支持什么，哪些机制不能直接照搬给机器。</span></a><a href="ideas.html"><b>06 · 四个候选 Idea</b><span>框架、最近邻、强基线、首轮实验与否定条件。</span></a><a href="teaching.html"><b>07 · I5 教学反馈自进化</b><span>详细机制、学生独立执行、归因矩阵、算法伪代码、两周预实验与否定条件。</span></a><a href="experiments.html"><b>08 · 实验执行方案</b><span>模型、环境、持久更新、数据隔离与元能力重置测试。</span></a><a href="references.html"><b>09 · 来源与核验记录</b><span>51 条论文/官方资源，区分正文、摘要和资源核对。</span></a></div>

## RSI × 自主学习研究 / 必须分开的三个研究主张

<div class="table-wrap"><table><thead><tr><th>主张</th><th>应观察什么</th><th>不能据什么下结论</th></tr></thead><tbody><tr><td>任务完成得更好</td><td>当前环境的正确率、成功率或执行质量。</td><td>提示更长、教师直接给步骤后得分上涨。</td></tr><tr><td>系统获得持久改进</td><td>新会话只带允许保留的技能、记忆或参数，在新任务上仍有收益。</td><td>刚完成任务的答案还在上下文。</td></tr><tr><td>系统更会自我改进</td><td>保留学到的元策略，重置底层学习者；在未见任务族上以相同预算学得更好。</td><td>第八代 Agent 比第一代强，就称改进器变强。</td></tr></tbody></table></div><p>这些是本专题的操作性检验。元学习和自适应权重更新分别有 RL²、SEAL 等基础；不自动构成无边界、完全自主的 RSI。<a class="cite" href="references.html#M02" title="RL²: Fast Reinforcement Learning via Slow Reinforcement Learning">[M02]</a><a class="cite" href="references.html#S04" title="Self-Adapting Language Models (SEAL)">[S04]</a></p><div class="note">固定外部审计器可以与改进器学习并存。没必要为了使用 RSI 名称而让系统修改最终评分标准。应明确递归深度、可编辑对象和不参与学习的参照。</div>

## RSI × 自主学习研究 / 从教育学或其他领域得到 Idea 的工作流

<ol class="research-steps"><li><b>找矛盾，而非找比喻。</b>例如帮助使当下成功率上升，但新会话独立表现不升；同难度的题产生不同学习增益。</li><li><b>找可迁移机制。</b>支持撤除、可学性估计、信息价值、抗干扰重放各改变什么变量？</li><li><b>定义持久载体。</b>能力写入参数、技能文件、记忆条目，还是只存在于上下文？</li><li><b>找最简单的替代解释。</b>通用预测器、bandit、普通重放与强提示必须得到同样的数据与预算。</li><li><b>做最小辨别实验。</b>先确定现象在自然失败中存在，再投入大规模 RL。</li><li><b>按结果缩小主张。</b>固定策略足够就不称元策略学习；只有同模板收益就不称跨能力泛化。</li></ol>

## RSI × 自主学习研究 / 本专题边界与旧站关系

<p>本次是针对选题的<strong>定向、可追踪综述</strong>，不是声称收齐全部 RSI 工作的系统综述。覆盖自修改、学习型 Harness、课程与元学习、学习科学、实验资源；主要依赖原论文、作者机构和官方仓库。逐项阅读深度见来源页。</p><p>新增 <a href="teaching.html"><b>I5：教学反馈驱动教师自改进</b></a>，把学生独立执行、反事实归因、教师可回滚更新与 Meta-reset 明确为可执行实验，不将师生对话本身称作创新。</p><p>原站的 <a href="https://agent-evolution.lightrain.asia/paper-ideas.html">论文 Idea 实验室</a>与<a href="https://agent-evolution.lightrain.asia/selected-paper.html">已选方向</a>保留不变。旧记录已有 Delayed Regression Exams、Regression-Probe Half-Life 等提案。本轮不把“增加延迟考试”重新包装成新 idea；新候选须改变<strong>学习干预本身</strong>。</p><div class="status-strip"><b>当前状态</b><span>文献与方案已整理</span><span>环境运行验证待做</span><span>候选均未通过实验门槛</span><span>未宣称独立专家评审通过</span></div>

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

## RSI 研究时间轴 / 研究活动与投稿时间轴 · 7 个已知日期

<div class="rsi-tl-toolbar"><label for="rsi-tl-kind">事件类型<select id="rsi-tl-kind">
           <option value="all">全部事件</option><option value="deadline">会议 DDL</option>
           <option value="reading">论文精读</option><option value="research">研究记录</option></select></label>
           <label for="rsi-tl-time">时间范围<select id="rsi-tl-time">
           <option value="all">全部时间</option><option value="upcoming">尚未截止</option>
           <option value="past">已结束／已发生</option></select></label>
           <label class="rsi-tl-search" for="rsi-tl-query">检索记录<input type="search" id="rsi-tl-query" placeholder="例如 CVPR、R²Orch、实验、ARR"></label>
           <button type="button" id="rsi-tl-reset">重置</button>
           <output id="rsi-tl-count" aria-live="polite">显示全部</output></div><div class="rsi-tl-months" id="rsi-tl-months"><section class="rsi-tl-month" data-month="2026-10"><div class="rsi-tl-month-head"><h3>2026 年 10 月</h3><span>3 条记录</span></div><div class="rsi-tl-month-body"><article class="rsi-tl-item rsi-tl-item--research" id="rsi-dossier-20261021"
      data-kind="research" data-date="2026-10-21" data-due-at="">
      <div class="rsi-tl-item-date"><time datetime="2026-10-21">10-21</time></div>
      <div class="rsi-tl-item-main">
        <div class="rsi-tl-item-meta"><span class="rsi-tl-kind rsi-tl-kind--research">研究记录</span><span>站内研究记录</span></div>
        <h3>RSI 自主学习研究专题完成首版资料整理</h3>
        <p>网站形成 RSI 文献、跨领域学习科学、候选方向和实验方案的资料页；属于研究文档整理，不代表实验验证完成。</p>
        <div class="rsi-tl-item-footer"><a href="index.html">专题总览 ↗</a></div>
      </div>
    </article><article class="rsi-tl-item rsi-tl-item--reading" id="reading-r2orch-2610-22740"
      data-kind="reading" data-date="2026-10-27" data-due-at="">
      <div class="rsi-tl-item-date"><time datetime="2026-10-27">10-27</time></div>
      <div class="rsi-tl-item-main">
        <div class="rsi-tl-item-meta"><span class="rsi-tl-kind rsi-tl-kind--reading">论文精读</span><span>阅读卡片已归档</span></div>
        <h3>精读：R²Orch</h3>
        <p>任务要按“撤掉 Skill 后还能不能学”来挑；Skill 要靠同题随机对照判断是否真的不再需要。</p>
        <div class="rsi-tl-item-footer"><a href="reading-cards.html#r2orch-2610-22740">打开精读卡片 ↗</a></div>
      </div>
    </article><article class="rsi-tl-item rsi-tl-item--reading" id="reading-rsi-anything-2610-13912"
      data-kind="reading" data-date="2026-10-27" data-due-at="">
      <div class="rsi-tl-item-date"><time datetime="2026-10-27">10-27</time></div>
      <div class="rsi-tl-item-main">
        <div class="rsi-tl-item-meta"><span class="rsi-tl-kind rsi-tl-kind--reading">论文精读</span><span>阅读卡片已归档</span></div>
        <h3>精读：RSI-Anything</h3>
        <p>先用世界模型挑最值得真实验证的尝试；再用反馈改进策略和预测器，只有重新组合后也更好的版本才进入下一轮。</p>
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

## 论文精读卡片 / 自我改进系统必须回答的四问，外加安全

<p>这五个问题是本站对自我改进研究的<strong>统一比较坐标</strong>，并非作者声称已经全部解决。每篇论文分别标注“重点研究 / 部分涉及 / 未直接研究”，展开后对照<strong>论文做到了什么</strong>与<strong>仍未解决什么</strong>。论文作者单位严格按署名，不能与会议发表状态混为一谈。</p><div class="reading-guide-grid"><div class="reading-question-guide"><b>信号对不对</b><p>评估分数和真实能力是否一致；评估器也在变化时，用什么独立证据校准它。</p></div><div class="reading-question-guide"><b>有没有新东西</b><p>自己出题、自己造数据时，能够纠正模型的信息究竟从哪里来。</p></div><div class="reading-question-guide"><b>采不采得到</b><p>高质量解法是否处在可采样的候选空间中，候选支持范围在哪一环节收窄。</p></div><div class="reading-question-guide"><b>吸收了会不会丢</b><p>改进进入权重、记忆或技能后，旧能力是否保留、错误经验是否被排除。</p></div><div class="reading-question-guide"><b>安全</b><p>评估器被绕过、越权修改真实系统、坏行为被持久记录三类跨环节风险。</p></div></div><p class="reading-legend"><strong>标注口径：</strong><span class="reading-level reading-level--core">重点研究</span>直接提出机制或证据；<span class="reading-level reading-level--partial">部分涉及</span>只覆盖该问题的一部分；<span class="reading-level reading-level--not_addressed">未直接研究</span>缺乏专门机制或实验。以上表示研究覆盖程度，不表示已经彻底解决。</p>

## 论文精读卡片 / 论文卡片库 · 2 篇

<div class="reading-tools"><label for="reading-card-filter">搜索卡片</label><input type="search" id="reading-card-filter" placeholder="论文、单位、方法或机制…" autocomplete="off"><label for="reading-question-filter">对应问题</label><select id="reading-question-filter"><option value="all">全部问题</option><option value="signal">信号对不对</option><option value="novelty">有没有新东西</option><option value="reach">采不采得到</option><option value="retention">吸收了会不会丢</option><option value="safety">安全</option></select><label for="reading-coverage-filter">涉及程度</label><select id="reading-coverage-filter"><option value="addressed">重点或部分涉及</option><option value="core">重点研究</option><option value="partial">部分涉及</option><option value="not_addressed">未直接研究</option><option value="all">全部程度</option></select><span id="reading-card-count" aria-live="polite"></span></div><div class="reading-grid"><article class="reading-card" id="r2orch-2610-22740" data-paper-tags="RSI|Self-Play|Curriculum|Skill Lifecycle" data-question-coverage="signal:core|novelty:partial|reach:core|retention:core|safety:not_addressed">
  <div class="reading-card-head">
    <div class="reading-metadata"><span class="reading-paper-id">R²Orch</span><span>arXiv:2610.22740</span><span>精读 2026-10-27</span></div>
    <h3>R²Orch</h3>
    <p class="reading-full-title">R²Orch: Recursive Self-Improvement for Agent Orchestration via Self-Play within a Skill-Internalization Loop</p>
    <p class="reading-institution"><b>发表单位（作者署名）</b> 香港中文大学（深圳） <span>等 5 家署名机构</span></p>
    <div class="reading-tags"><span class="reading-tag">RSI</span><span class="reading-tag">Self-Play</span><span class="reading-tag">Curriculum</span><span class="reading-tag">Skill Lifecycle</span></div>
  </div>
  <div class="reading-issues"><p class="reading-issues-title">它研究了自我改进的哪些问题？</p><div class="reading-issue-tags"><span class="reading-issue reading-issue--core" title="评估分数和真实能力是否一致；评估器也在变化时，用什么独立证据校准它。">信号对不对<small>重点研究</small></span><span class="reading-issue reading-issue--partial" title="自己出题、自己造数据时，能够纠正模型的信息究竟从哪里来。">有没有新东西<small>部分涉及</small></span><span class="reading-issue reading-issue--core" title="高质量解法是否处在可采样的候选空间中，候选支持范围在哪一环节收窄。">采不采得到<small>重点研究</small></span><span class="reading-issue reading-issue--core" title="改进进入权重、记忆或技能后，旧能力是否保留、错误经验是否被排除。">吸收了会不会丢<small>重点研究</small></span><span class="reading-issue reading-issue--not_addressed" title="评估器被绕过、越权修改真实系统、坏行为被持久记录三类跨环节风险。">安全<small>未直接研究</small></span></div></div>
  <p class="reading-one-sentence">任务要按“撤掉 Skill 后还能不能学”来挑；Skill 要靠同题随机对照判断是否真的不再需要。</p>
  <dl class="reading-overview">
    <div><dt>它解决什么问题</dt><dd>以有 Skill 时的成功率选题，撤掉 Skill 后可能全错，GRPO 失去成败差异；仅凭整体成功率也分不清模型变强还是 Skill 仍有帮助。</dd></div>
    <div><dt>它怎么做</dt><dd>Proposer 选训练任务；Director 学习构建 Agent Graph；Workers 冻结。每个任务 5 条 Rollout，随机 3 条隐藏候选 Skill、2 条保留。</dd></div>
    <div><dt>到底更新了什么</dt><dd>真正通过 GRPO 更新的是 Director 和 Proposer 的 LoRA 参数；Skill 是外部提示文本，由 LLM Editor 修订、试用、撤回。随机隐藏只是训练时拿掉某一条 Skill 的上下文输入，并不撤销模型已经学到的参数；其余 Skill 可以仍然在场。</dd></div>
    <div><dt>和我们有什么关系</dt><dd>对 I5 的十模型共进化：将“选下一道题”对应为“选下一位教学伙伴”，但不能直接用交互成功率替代学习后的独立能力提升。</dd></div>
  </dl>
  <details class="reading-expand">
    <summary>展开五问判断、机制、实验证据与局限</summary>
    <div class="reading-expanded-content">
      <div class="reading-source-line"><b>作者</b> Mingda Zhang et al. · <b>首发</b> 2026-10-15 · <b>版本</b> v2 · 2026-10-22 · <b>阅读范围</b> Method §4.2–4.3 + Appendix A.2/A.3/A.7 精读；尚未独立复现</div>
      <p class="reading-institutions-full"><b>全部作者单位：</b>香港中文大学（深圳） · 复旦大学 · 伊利诺伊大学厄巴纳-香槟分校 · 清华大学 · 新加坡国立大学<br><b>发表状态：</b>arXiv 预印本 · <b>核对位置：</b>arXiv v2 论文首页作者署名</p>
      <h4>自我改进五问 · 论文做到哪里、还缺什么</h4>
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
</article>
<article class="reading-card" id="rsi-anything-2610-13912" data-paper-tags="RSI|World Model|Feedback Learning|Pair Retention|JEPA-Anything" data-question-coverage="signal:core|novelty:partial|reach:partial|retention:core|safety:partial">
  <div class="reading-card-head">
    <div class="reading-metadata"><span class="reading-paper-id">RSI-Anything</span><span>arXiv:2610.13912</span><span>精读 2026-10-27</span></div>
    <h3>RSI-Anything</h3>
    <p class="reading-full-title">RSI-Anything: Unlocking Recursive Self-Improvement with World Models</p>
    <p class="reading-institution"><b>发表单位（作者署名）</b> PhAI Labs <span>等 8 家署名机构</span></p>
    <div class="reading-tags"><span class="reading-tag">RSI</span><span class="reading-tag">World Model</span><span class="reading-tag">Feedback Learning</span><span class="reading-tag">Pair Retention</span><span class="reading-tag">JEPA-Anything</span></div>
  </div>
  <div class="reading-issues"><p class="reading-issues-title">它研究了自我改进的哪些问题？</p><div class="reading-issue-tags"><span class="reading-issue reading-issue--core" title="评估分数和真实能力是否一致；评估器也在变化时，用什么独立证据校准它。">信号对不对<small>重点研究</small></span><span class="reading-issue reading-issue--partial" title="自己出题、自己造数据时，能够纠正模型的信息究竟从哪里来。">有没有新东西<small>部分涉及</small></span><span class="reading-issue reading-issue--partial" title="高质量解法是否处在可采样的候选空间中，候选支持范围在哪一环节收窄。">采不采得到<small>部分涉及</small></span><span class="reading-issue reading-issue--core" title="改进进入权重、记忆或技能后，旧能力是否保留、错误经验是否被排除。">吸收了会不会丢<small>重点研究</small></span><span class="reading-issue reading-issue--partial" title="评估器被绕过、越权修改真实系统、坏行为被持久记录三类跨环节风险。">安全<small>部分涉及</small></span></div></div>
  <p class="reading-one-sentence">先用世界模型挑最值得真实验证的尝试；再用反馈改进策略和预测器，只有重新组合后也更好的版本才进入下一轮。</p>
  <dl class="reading-overview">
    <div><dt>它解决什么问题</dt><dd>Agent 的真实测试与实验很贵；策略进步后会尝试新类型动作，使旧世界模型的预测失准；即使策略和世界模型各自提升，二者组合后也可能退步。</dd></div>
    <div><dt>它怎么做</dt><dd>Policy/Workflow 提出多个候选，基于 JEPA-Anything 的 World Model 预测后果并筛选，再执行少量真实验证。代码修复、GUI、实验室规划、反应优化等领域共享改进流程，但仍使用不同领域的状态、行动与反馈适配器。</dd></div>
    <div><dt>到底更新了什么</dt><dd>真实反馈可以更新 Policy 参数或 Agent Workflow；只有预测不可靠、证据充足且预算允许时才适配 World Model。新 Policy、新 World Model 分别接受检查，再检查二者配对是否优于当前组合；未通过就保留旧版本。</dd></div>
    <div><dt>和我们有什么关系</dt><dd>我们的 I5 十模型交换舞伴：把预测对象从“动作会带来什么后果”改为“向哪个伙伴学习，等预算训练后的独立能力提升是多少”。</dd></div>
  </dl>
  <details class="reading-expand">
    <summary>展开五问判断、机制、实验证据与局限</summary>
    <div class="reading-expanded-content">
      <div class="reading-source-line"><b>作者</b> Taoyong Cui et al. · <b>首发</b> 2026-10-09 · <b>版本</b> v1 · 2026-10 · <b>阅读范围</b> 框架 §2.3–2.5、关键实验与官方项目说明精读；尚未独立复现</div>
      <p class="reading-institutions-full"><b>全部作者单位：</b>PhAI Labs · 香港中文大学 · 澳门大学 · 上海交通大学 · 复旦大学 · 牛津大学 · 斯坦福大学 · 北京大学<br><b>发表状态：</b>PhAI Labs Technical Report · arXiv 预印本 · <b>核对位置：</b>arXiv v1 论文附录 A（Author Affiliations and Correspondence）</p>
      <h4>自我改进五问 · 论文做到哪里、还缺什么</h4>
      <p class="reading-taxonomy-caveat">“重点研究”表示直接针对该问题提出机制或证据，不代表问题已被彻底解决。分类属于本站的文献研读判断。</p>
      <dl class="reading-question-details"><div class="reading-question-detail"><dt><span>信号对不对</span><span class="reading-level reading-level--core">重点研究</span></dt><dd><p><b>论文做到：</b>将预测与真实观测配对以检查 World Model 可靠性；Policy、World Model 及其组合分别经过事先规定的接纳检验（§2.4–2.5）。</p><p><b>仍未解决：</b>这里主要校准可更新的预测器；实际任务验证标准保持固定，并未解决评估器自身也会被重写时的真实性锚点问题。</p></dd></div><div class="reading-question-detail"><dt><span>有没有新东西</span><span class="reading-level reading-level--partial">部分涉及</span></dt><dd><p><b>论文做到：</b>用有限的真实程序测试、GUI 交互和科学实验获取外部结果，为下一轮训练提供新的观察反馈（§2.3）。</p><p><b>仍未解决：</b>新信息主要来自外部环境；没有证明完全自生成题目或数据能在封闭循环中不断产生正确的新知识。</p></dd></div><div class="reading-question-detail"><dt><span>采不采得到</span><span class="reading-level reading-level--partial">部分涉及</span></dt><dd><p><b>论文做到：</b>世界模型对已经提出的候选进行预测排序，优先执行有价值的方案，提高有限真实反馈预算的利用率（§2.3）。</p><p><b>仍未解决：</b>候选筛选不等于扩展采样支持集；如果好解最初不在 Policy 能提出的集合里，World Model 也无法将它挑出来。</p></dd></div><div class="reading-question-detail"><dt><span>吸收了会不会丢</span><span class="reading-level reading-level--core">重点研究</span></dt><dd><p><b>论文做到：</b>用版本化 Policy/Workflow、World Model 的组件检验与配对兼容性检验决定是否接受更新并继承到下一轮（§2.5）。</p><p><b>仍未解决：</b>验证的是组件更新和配对收益，不等同于证明长时间不遗忘旧任务、不会把错误经验写入记忆或权重。</p></dd></div><div class="reading-question-detail"><dt><span>安全</span><span class="reading-level reading-level--partial">部分涉及</span></dt><dd><p><b>论文做到：</b>任务协议中固定操作约束、预算和接纳规则，为真正执行候选与保留改进设置基本边界（§2.1、§2.5）。</p><p><b>仍未解决：</b>没有独立覆盖评估器被绕过、Agent 越权操作真实系统，以及恶意行为被持久学习的三类对抗测试。</p></dd></div></dl>
      <h4>核心机制 · 记住这几个公式</h4><ol class="reading-mechanisms"><li><b>预测引导的有限试错</b><p>先预测候选效果和不确定性，用有限的真实测试预算优先验证有价值的候选；未执行的候选不能当作真实反馈。</p><code class="reading-formula">a* = argmax_a [predicted reward(a) - uncertainty penalty(a)]（机制理解式）</code></li><li><b>按需更新世界模型</b><p>Policy 变强会改变候选分布，因此世界模型可靠性要按当前版本重新评价；证据或预算不足时不强行更新。</p><code class="reading-formula">update W iff unreliable(W) AND enough data AND enough budget（机制理解式）</code></li><li><b>策略—预测器联合保留</b><p>策略与世界模型各自通过评估还不够，还须验证搭配后的真实收益；确保下一轮继承的是有效组合。</p><code class="reading-formula">retain(Policy&#x27;, W&#x27;) iff pass(Policy&#x27;) AND pass(W&#x27;) AND pass(pair)（机制理解式）</code></li></ol>
      <h4>实验证据（作者报告，未复现）</h4><ul><li>CodeContests 200 道题、3 个种子，固定代码生成模型：静态验证器 26.3%，预测筛选 29.2%，再适配 World Model 31.2%；在线测试量相近。</li><li>MiniWoB++ checkbox 同一组 100 个实例：连续保留版本的任务成功数 51 → 79 → 99；平均动作数 5.30 → 3.21（下降 39.4%）。</li><li>LabHorizon F200 Level 2：五个策略版本的规划得分 21.80% → 46.01%；Suzuki 反应优化在相同 40 次实验预算下，平均最优产率 96.15%，BO 为 82.16%。</li></ul>
      <h4>限制与易错理解</h4><ul><li>“跨领域”指复用提出候选→预测→真实反馈→更新→保留的流程，不是一个共享权重的超级世界模型横跨所有任务。</li><li>五轮规划结果证明了连续策略改进，但不足以单独证明同一场景中 Policy 和 World Model 长期稳定的双向共同进化。</li><li>仅对被选中执行的候选获得真实反馈，预测器可能面对选择偏差与分布变化；预测误差降低也不自动意味着最终任务表现提升。</li></ul>
      <h4>对我们 RSI / I5 的启发</h4><ul><li>我们的 I5 十模型交换舞伴：把预测对象从“动作会带来什么后果”改为“向哪个伙伴学习，等预算训练后的独立能力提升是多少”。</li><li>可以借鉴“预测→少量真实教学验证→更新学习增益预测器→检查新伙伴策略是否真的更好”的递归闭环，而不是永远选择最强教师。</li><li>与我们的 Agent 多层更新研究相关：把修改 Prompt、Memory、Workflow 或模型参数的效果与预测器的判断分开审计，并保留独立测试。</li></ul>
      <div class="reading-next"><b>下一步最值得做的辨别实验</b><p>固定同一学生检查点，向强教师、能力相近教师、预测高增益教师和随机教师等预算学习；在未见测试集比较相对无教师的真实增益、负迁移率与成本，并观察多轮学习后最佳伙伴是否变化。</p></div>
    </div>
  </details>
  <div class="links reading-links"><a class="link-btn" href="#rsi-anything-2610-13912" aria-label="复制或保存此卡片的锚点链接">卡片定位</a><a class="link-btn" href="https://arxiv.org/html/2610.13912" target="_blank" rel="noopener noreferrer">论文 HTML</a><a class="link-btn" href="https://arxiv.org/pdf/2610.13912" target="_blank" rel="noopener noreferrer">PDF</a><a class="link-btn" href="https://github.com/Gen-Verse/RSI-Anything" target="_blank" rel="noopener noreferrer">GitHub 代码</a></div>
</article></div><p class="reading-empty" id="reading-empty" hidden>没有匹配的论文；可更换问题、涉及程度或清空搜索。</p><div class="links"><a class="link-btn" href="reading-cards.json" download>下载阅读卡片 JSON（可复用）</a></div>

## 论文精读卡片 / 下一篇论文如何进入卡片库

<p>在 <code>rsi/reading-cards.json</code> 的 <code>papers</code> 数组中追加新条目：包含作者单位、发表状态、原文链接、阅读日期与版本、核心机制及实验证据，并为 <strong>research_coverage</strong> 中的五问逐项填写 <code>level</code>、<code>contribution</code> 和 <code>open_question</code>。运行 <code>python3 scripts/build_rsi_research.py</code> 即可刷新网页、左侧目录和搜索索引。</p><p>把作者实际验证的内容与本站的研究判断明确分开；不能用“相关”替代“解决”，也不能把阅读结论写成已经独立复现的结果。</p>

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

## 教育学与学习科学：如何转成机器机制 / 这些思想已经部分进入 AI

<p>课程、知识追踪和学习型教学早已转化部分教育学问题；SOAR、ActiveSaddler、EduardoRL 又进入 LLM 与 Agent 场景。贡献须是<strong>新增机制或适用条件</strong>，而不是首次使用“自学、老师、考试”。<a class="cite" href="references.html#M03" title="Automated Curriculum Learning for Neural Networks">[M03]</a><a class="cite" href="references.html#M05" title="Deep Knowledge Tracing">[M05]</a><a class="cite" href="references.html#M06" title="Learning to Teach with Dynamic Loss Functions">[M06]</a><a class="cite" href="references.html#S16" title="ActiveSaddler: Automated Curriculum Learning for Agent Harness Optimization">[S16]</a><a class="cite" href="references.html#S17" title="Teaching Models to Teach Themselves: Reasoning at the Edge of Learnability (SOAR)">[S17]</a><a class="cite" href="references.html#S19" title="The Assistance Dilemma: Learning to Teach via Multi-Turn Reinforcement Learning">[S19]</a></p><p>EduardoRL 已遮蔽教师话语。我们的候选不是重做这一后测，而是问：后续不同能力学习带来干扰时，怎样组织<strong>帮助—独立练习—巩固</strong>的完整序列？须与短程目标、固定渐隐及普通重放直接比较。</p>

## 教育学与学习科学：如何转成机器机制 / 贯穿例子：分页工具调用

<div class="example"><h3>失败现象</h3><p>Agent 处理第一页却漏后续页。完整调用示范使当前任务成功，但换数据和 API 名称又失败。</p><h3>四种学习动作</h3><p><b>A：</b>给完整示范；<b>B：</b>仅提示检查 continuation token；<b>C：</b>先要求提出终止条件再给反例；<b>D：</b>无提示独立尝试。随后使用同一个固定更新器。</p><h3>三个层次</h3><p>原任务完成率；不同名称、页数的新任务独立成功率；学习另一种分页 / 重试机制后，原能力是否保留。近迁移不能仅替换答案数字；远迁移需改变工具组合、依赖或恢复条件。</p><h3>防止偷换概念</h3><p>保留技能文件时报告系统层面学习。只保留 LoRA 且清空会话与技能时，才评价参数学习。分栏报告，不相加为同一能力分。</p></div>

## 教育学与学习科学：如何转成机器机制 / 必须允许的相反结果

<p><b>强示范最好：</b>强教师示范加固定蒸馏可能在所有保持测试上占优。接受结果，不强行宣称“适度困难”有效。</p><p><b>延迟只是更多训练：</b>控制曝光、梯度步数和更新顺序后差异若消失，不能归因于间隔机制。</p><p><b>只有上下文记住了：</b>清空会话后增益消失，就属于上下文适应，不能改写为持久自进化。</p><div class="note">人类学习效应有任务、先备知识和教学设计条件。机器研究也要找适用边界，而不是只挑支持类比的例子。</div>

## 五个候选 Idea 与方法框架 / 候选池与推进顺序

<div class="table-wrap"><table><thead><tr><th>候选</th><th>问题</th><th>建议</th><th>风险</th></tr></thead><tbody><tr><td><a href="#idea-1">I1 · 长程支持获取与撤除</a></td><td>帮助如何转成跨轮保留的独立能力？</td><td>首选，先找现象。</td><td>EduardoRL 相近；固定渐隐可能足够。</td></tr><tr><td><a href="#idea-2">I2 · 干预响应驱动的自学</a></td><td>能否预测练什么、怎样练的后果？</td><td>主线技术备选。</td><td>通用预测器或 bandit 可解释收益。</td></tr><tr><td><a href="#idea-3">I3 · 干扰条件化巩固</a></td><td>重练什么、如何固化以减少退化？</td><td>扩展分支。</td><td>MIR / TSCL 和本站旧考试方向重叠。</td></tr><tr><td><a href="#idea-4">I4 · 先失败后学习的边界</a></td><td>什么时候自主尝试应先于示范？</td><td>机制筛查。</td><td>额外采样或更多数据造成假象。</td></tr><tr><td><a href="teaching.html">I5 · 教学反馈驱动教师自进化</a></td><td>学生独立运用教师经验时，能否暴露教师自己没发现的知识缺口？</td><td>新主力候选；先做等预算辨别试验。</td><td>LbT 2024、SKILL-KD、MARS 已十分接近。<a class="cite" href="references.html#S20" title="Can LLMs Learn by Teaching for Better Reasoning? A Preliminary Study">[S20]</a><a class="cite" href="references.html#S22" title="SKILL-KD: Contrastive Skill Distillation for LLM Agents">[S22]</a><a class="cite" href="references.html#S21" title="MARS: Multi-Agent Adaptive Reasoning with Socratic Guidance for Automated Prompt Optimization">[S21]</a></td></tr></tbody></table></div><p class="status">统一状态：候选假设 · 新颖性待最近邻复核 · 尚无本项目实测结果。</p>

## 五个候选 Idea 与方法框架 / I1：长程支持获取与撤除

<p class="thesis"><b>待检验命题：</b>在后续学习会引入干扰的任务流中，按延迟独立表现学习的支持策略，比按当前成功率或单题近迁移优化，更能形成保留能力。</p><p><b>来源与边界：</b>借鉴帮助困境、例题渐隐和表现—学习区分。最近邻为 EduardoRL、SOAR、ActiveSaddler；删教师话语或调难度不能当贡献。<a class="cite" href="references.html#E05" title="Transitioning From Studying Examples to Solving Problems: Effects of Self-Explanation Prompts and Fading Worked-Out Steps">[E05]</a><a class="cite" href="references.html#E07" title="Exploring the assistance dilemma in experiments with Cognitive Tutors">[E07]</a><a class="cite" href="references.html#E08" title="Examining productive failure, productive success, unproductive failure, and unproductive success in learning">[E08]</a><a class="cite" href="references.html#S19" title="The Assistance Dilemma: Learning to Teach via Multi-Turn Reinforcement Learning">[S19]</a><a class="cite" href="references.html#S17" title="Teaching Models to Teach Themselves: Reasoning at the Edge of Learnability (SOAR)">[S17]</a><a class="cite" href="references.html#S16" title="ActiveSaddler: Automated Curriculum Learning for Agent Harness Optimization">[S16]</a></p><div class="flow"><div><b>能力 / 依赖估计</b><small>有帮助与无帮助对照</small></div><div><b>选择支持</b><small>提问、提示、示范、独立练习</small></div><div><b>固定更新器</b><small>技能写入与 LoRA 分轨</small></div><div><b>后续异类学习</b><small>显式更新干扰</small></div><div><b>延迟独立反馈</b><small>更新支持策略</small></div></div><h3>方法设计</h3><p>元策略观察独立成功率、帮助收益、最近更新类型和不确定性；动作包含帮助形式、强度与是否独立巩固。先固定任务选择，隔离“如何教”。训练用元验证任务 H 轮后的独立收益，扣除回归和帮助成本；最终测试不参与奖励。</p><div class="equation">J(φ) = E[U_independent(s_t+H) − λ Regression_t+H − μ Cost_t:t+H]</div><h3>第一项实验</h3><p>同旧版本复制四分支：完整示范、固定渐隐、即时收益自适应、延迟收益自适应。任务、教师和总曝光一致；比较即时、近迁移、远迁移及两次干扰后的保持。先在开发阶段枚举支持动作，确认确实存在选择空间，再训练策略。</p><h3>强基线与消融</h3><p>强教师示范 + 相同更新器；固定渐隐；EduardoRL 风格短程目标；固定任务选择的 contextual bandit；无延迟项；打乱帮助历史；Meta-reset。双方均在未见任务族测试。</p><h3>继续 / 停止</h3><p><b>继续：</b>长程与即时最优支持稳定不一致，学习型策略在两个任务族超过预先固定规则。<b>停止或缩题：</b>同预算固定示范 / 渐隐足够；优势仅在教师文本仍可见时出现；自然失败不复现。若只现象成立，可以写机制研究，不强行称 Meta-RSI。</p>

## 五个候选 Idea 与方法框架 / I2：干预响应驱动的自学

<p class="thesis"><b>待检验命题：</b>当前成功率相同的 Agent 可能需要不同学习动作；从随机干预中估计响应，比只按错误频率或任务语义选择更有效。</p><p><b>来源与边界：</b>知识追踪提供状态估计，双重控制提供信息价值；前瞻课程已考虑下游收益。“给 learner 建世界模型”不足以成立贡献。<a class="cite" href="references.html#M05" title="Deep Knowledge Tracing">[M05]</a><a class="cite" href="references.html#M07" title="Dual Control for Approximate Bayesian Reinforcement Learning">[M07]</a><a class="cite" href="references.html#S18" title="Anticipating the Consequences of Curriculum Decisions with Large Language Models">[S18]</a></p><div class="flow"><div><b>同版本分叉</b><small>环境与更新种子可追踪</small></div><div><b>对照干预</b><small>练习、流程修复、知识补充</small></div><div><b>能力变化向量</b><small>不只预测总分</small></div><div><b>响应与不确定性</b><small>判断是否需 Probe</small></div><div><b>选择再执行</b><small>新任务、新模型验证</small></div></div><h3>方法设计</h3><p>首版只选三类动作，不搜索所有模块。用同版本随机分叉学习多输出响应，保留未选择动作结果供离线审计。未见干预组合允许拒绝预测、转真实测试；不把语义相似性当作因果可识别性。</p><h3>第一项实验</h3><p>比较当前成功率接近、缺口不同的状态：规范未知、已知规范但流程错误、旧技能被新提示遮蔽。加入自然失败。让错误频率、DKT 风格模型、同容量通用序列模型与响应模型获得相同数据，比较动作选择 regret 和未见任务净收益。</p><h3>额外贡献门槛</h3><p>预测准确还不够，必须改变决策。对不确定状态，信息价值选的 Probe 应比随机或最高熵 Probe 更有助于后续选择；跨模型同时报告校准数据开销。</p><h3>继续 / 停止</h3><p><b>继续：</b>匹配即时能力后仍有可重复的干预异质性，决策收益可迁移。<b>停止：</b>通用模型 + bandit 同容量下同样有效；结构没有必要性；只有植入故障有效。此时并入 I1 普通实现，不另立“因果模型”论文。</p>

## 五个候选 Idea 与方法框架 / I3：干扰条件化的巩固，而非频繁考试

<p class="thesis"><b>待检验命题：</b>按后续更新的具体干扰选择重练对象与固化形式，比同量重放更能保持组合能力。</p><p><b>来源与边界：</b>检索与间隔提供启发，但 PER、MIR、TSCL 已覆盖重访；本站还有 Delayed Regression Exams。新增部分须改变学习操作，不能只增加诊断。<a class="cite" href="references.html#E03" title="Test-enhanced learning: taking memory tests improves long-term retention">[E03]</a><a class="cite" href="references.html#E04" title="Spacing effects in learning: a temporal ridgeline of optimal retention">[E04]</a><a class="cite" href="references.html#M08" title="Prioritized Experience Replay">[M08]</a><a class="cite" href="references.html#M09" title="Online Continual Learning with Maximally Interfered Retrieval">[M09]</a><a class="cite" href="references.html#M04" title="Teacher-Student Curriculum Learning (TSCL)">[M04]</a></p><div class="flow"><div><b>更新指纹</b><small>工具、规则、参数变化</small></div><div><b>干扰估计</b><small>受影响的旧能力</small></div><div><b>独立检索练习</b><small>不显示原示范</small></div><div><b>对照后固化</b><small>条件化技能或参数更新</small></div><div><b>组合迁移</b><small>新旧能力共同使用</small></div></div><h3>第一项实验</h3><p>固定学习数据与更新次数，对比连续重复、均匀穿插、随机重放、MIR 风格重放，以及联合选择重练与固化的策略。时间按<strong>发生多少次什么更新</strong>定义，不是等待几小时。</p><h3>控制与判定</h3><p>记忆预算、曝光、梯度步数、教师调用匹配；仅评测不重练作消融。参数与外置层分轨。只有优于 MIR 和等预算固定重放、且能说明新学习操作作用时继续；多测试或多存记忆已解释收益则停止。</p>

## 五个候选 Idea 与方法框架 / I4：先失败后解释，何时促进迁移？

<p class="thesis"><b>待检验命题：</b>对具备一定先备能力的 Agent，先尝试再对照最小反例，可能比示范优先形成更可迁移更新；其适用条件可识别。</p><p><b>来源与边界：</b>生产性失败要求后续知识整合；与 ModularRSI 成败对照及 SOAR 相邻。“读失败日志”不是新机制。<a class="cite" href="references.html#E06" title="Learning from productive failure">[E06]</a><a class="cite" href="references.html#E08" title="Examining productive failure, productive success, unproductive failure, and unproductive success in learning">[E08]</a><a class="cite" href="references.html#S09" title="ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement">[S09]</a><a class="cite" href="references.html#S17" title="Teaching Models to Teach Themselves: Reasoning at the Edge of Learnability (SOAR)">[S17]</a></p><div class="flow"><div><b>自主尝试</b><small>暴露错误假设</small></div><div><b>最小反例</b><small>改变关键条件</small></div><div><b>验证性解释</b><small>提出可执行预测</small></div><div><b>固定更新</b><small>同曝光、同训练量</small></div><div><b>新组合任务</b><small>检验规则而非答案</small></div></div><h3>第一项实验</h3><p>随机对比“示范→练习”“自主失败→示范”“他人匹配失败→示范”“自主失败→最小对照解释”。控制 Token、样例数和更新量；额外采样组排除多思考一次。</p><h3>推进边界</h3><p>可快速检验现象，但已有自训练、反思、对照学习很接近。只有稳定适用条件确实改善后续学习选择，才考虑方法论文；否则作为 I1 消融。若效果在匹配曝光后消失，停止该分支。</p>

## 五个候选 Idea 与方法框架 / 本轮不推进的包装型方案

<p><strong>计划—监控—反思三个 Agent：</strong>组织图不是学习机制，缺少新监督或更新规则。</p><p><strong>挑不会的题 + 自动出题 + RL：</strong>课程与 SOAR 已有强近邻，需明确额外变量。</p><p><strong>每轮考试，不好就回滚：</strong>必要基础设施，但与已有门控及本站旧 idea 重复。</p><div class="note">五个候选不应塞入一篇论文。I5 与 I1 / I2 共用可控学习试验基础设施，但须独立证明学生反馈相对教师自我探索的增量信息。详见 <a href="teaching.html">I5 完整方法设计</a>。</div>

## I5 · 教学反馈驱动的 Agent 自我进化 / 研究目标：更新教师，而不是帮学生提高分数


 <div class="decision"><span class="kicker">CANDIDATE I5 · PRE-EXPERIMENT DESIGN</span>
 <h3>Learner-Induced Blindspot Discovery for Recursive Agent Self-Improvement</h3>
 <p>核心假设：学生在<strong>独立使用</strong>教师教出的经验时，会暴露一些教师自己执行任务或自我反思时没有发现的隐藏前提、例外条件和错误泛化。这些差异如果能被<strong>独立执行证据</strong>确认，就可能成为教师技能、Harness 或参数更新的有效学习信号。</p>
 <p><b>主要终点：</b>教师 Agent 在更新并清除会话与学生提示之后，在未参与教学/版本选择的新任务上的独立成功率净增益；同时看旧任务的能力回归。</p></div>
 <p>NeurIPS 2024 LbT 已让学生表现影响教师解释选择和教师权重微调；SKILL-KD 已由师生轨迹差异改进<strong>学生</strong>技能；AAAI 2026 MARS 已引入苏格拉底式 Teacher–Student–Critic 提示优化。故本方向不以“有一个学生”“学生会追问”“教师看反馈”作为 novelty。<a class="cite" href="references.html#S20" title="Can LLMs Learn by Teaching for Better Reasoning? A Preliminary Study">[S20]</a><a class="cite" href="references.html#S22" title="SKILL-KD: Contrastive Skill Distillation for LLM Agents">[S22]</a><a class="cite" href="references.html#S21" title="MARS: Multi-Agent Adaptive Reasoning with Socratic Guidance for Automated Prompt Optimization">[S21]</a><a class="cite" href="references.html#S25" title="Large Language Models are In-context Teachers for Knowledge Reasoning">[S25]</a></p>
 <p>教育学 Recursive Feedback 原始研究强调两点：学生在新环境独立运用所学、教师将其行为映射回自身的知识结构。这里的“recursive”是教育学的反馈机制；只有随后证明 Agent 及其改进策略的持久改进，才可称为我们定义下的 RSI。<a class="cite" href="references.html#E09" title="Learning by Teaching Human Pupils and Teachable Agents: The Importance of Recursive Feedback">[E09]</a></p>


## I5 · 教学反馈驱动的 Agent 自我进化 / 机制抓手：学生反馈究竟比自我测试多了什么？


 <p>把“教师原来能做对”与“教师能否把规则交给另一模型可靠执行”分开。先假设教师 T 有一组成功经验 <code>H_T</code>，通过固定格式提取技能 <code>K_t</code>。学生 S 只能读 <code>K_t</code> 和必要工具文档，不能读教师原任务答案。随后在新的同族 / 邻域任务上独立执行。</p>
 <div class="flow"><div><b>Teacher T 的原经验</b><small>成功轨迹、技能版本</small></div><div><b>教学契约 K_t</b><small>触发、前提、不变量、例外</small></div><div><b>Student S 的独立执行</b><small>新状态、新工具/参数</small></div><div><b>对教师的反事实审计</b><small>是教师漏了还是学生不会？</small></div><div><b>更新 T 而非只更新 S</b><small>独立留出任务检验</small></div></div>
 <p>学生提供的信息可以有三类：<b>疑问</b>（需要条件明确化）、<b>错误执行</b>（教学规则的错误解释）、<b>意外成功</b>（可能揭示与教师不同的有效路径）。必须先判明该现象对教师知识具有增量信息，不能把所有 Student Failure 都写成 Teacher Blindspot。</p>
 <p><b>最低辨别标准：</b>教师自行测试在<strong>相同任务、相同环境调用预算</strong>下的结果，与从学生轨迹得到的增益进行对比。若教师自己探索已同样发现缺陷，则不能声称教学反馈具有不可替代的信息优势。<a class="cite" href="references.html#S20" title="Can LLMs Learn by Teaching for Better Reasoning? A Preliminary Study">[S20]</a><a class="cite" href="references.html#S24" title="Socratic Students: Teaching Language Models to Learn by Asking Questions">[S24]</a></p>


## I5 · 教学反馈驱动的 Agent 自我进化 / 模块 1｜教学材料是可检验的 Skill Contract


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


## I5 · 教学反馈驱动的 Agent 自我进化 / 模块 2｜学生必须真实独立执行，而非模拟会不会


 <p><b>固定学生池：</b>建议两种不同模型家族或能力水平的 Student；可加入与教师同底座的干净 Student 副本。所有学生在同一轮使用冻结权重和 Harness，当前任务上下文清零；教学材料仅包含该版本 Skill。</p>
 <div class="table-wrap"><table><thead><tr><th>执行臂</th><th>学生获得的信息</th><th>意义</th></tr></thead><tbody>
 <tr><td>S0</td><td>任务与公开工具文档，无该技能</td><td>学生基础能力基线。</td></tr>
 <tr><td>S1</td><td>相同任务 + Teacher K_t</td><td>测教学技能的实际可迁移性。</td></tr>
 <tr><td>S2</td><td>同任务 + 基于官方规则的完整参考说明（仅开发集）</td><td>排查“学生根本无法执行”的可能；不是无条件金标准。</td></tr>
 <tr><td>T0</td><td>原教师快照独立执行同任务，不能看学生轨迹</td><td>区分教师自己能否解决及普通探索机会。</td></tr>
 </tbody></table></div>
 <p>对 S0/S1/S2/T0 采用可复位环境快照、匹配试验种子与同等 Token/工具调用上限。学生可提交最多 2 条<strong>可定位到任务事实的追问</strong>，但学生的自述困惑不是证据；必须附有执行轨迹、工具响应或受验证的边界例子。另设<strong>只追问不执行</strong>的消融，检验是否只是多生成了一些疑问。</p>
 <p><b>切分：</b>技能源轨迹、学生试教任务、补丁筛选任务、最终教师独立评测按任务族、状态约束、工具组合隔离。学生试教任务属于训练反馈，不能再用作最终测试。</p>


## I5 · 教学反馈驱动的 Agent 自我进化 / 模块 3｜教学失败归因：不能把学生弱当教师错


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


## I5 · 教学反馈驱动的 Agent 自我进化 / 模块 4｜把被验证的盲点转成教师自己的持久更新


 <p>首版共享固定 Editor（可以是相同 LLM + 相同编辑模板），每个候选最多修改一项前提、不变量、边界或恢复步骤。原则：<b>学生证据只告诉我们哪里需要查，不保证应该怎样改</b>。</p>
 <div class="flow"><div><b>生成候选 patch</b><small>引用具体技能条款</small></div><div><b>局部可执行复现</b><small>最小反例消失？</small></div><div><b>独立开发验证</b><small>同类新任务/旧正确任务</small></div><div><b>置信与成本门控</b><small>收益、回归、验证次数</small></div><div><b>接受 / 拒绝 / 回滚</b><small>保存版本链</small></div></div>
 <p>对每个候选 <code>K_t'</code>，统计目标修复、同机制新任务迁移、其他任务回归、执行成本。开发门控与最终独立测试分开；一个任务成功不能把 patch 升级为“有效”。保留所有被拒修改与失败原因。补丁需要清楚记录：哪个学生行为触发、哪条语义规则被修改、具体执行结果、教师在更新前后表现。</p>
 <p><b>两条升级轨道：</b>A 轨将技能文件版本 <code>K_t → K_t'</code> 装载给<strong>教师自己</strong>，权重不动；B 轨在 A 轨验证有效后，以同样数据预算训练教师 LoRA，再彻底清除额外技能与会话进行评测。不能把 A 轨提升称为“权重学会了”，也不能把学生变强算作教师结果。<a class="cite" href="references.html#S20" title="Can LLMs Learn by Teaching for Better Reasoning? A Preliminary Study">[S20]</a><a class="cite" href="references.html#S04" title="Self-Adapting Language Models (SEAL)">[S04]</a></p>


## I5 · 教学反馈驱动的 Agent 自我进化 / 可编程最小算法：一轮 Teaching-to-Improve


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


## I5 · 教学反馈驱动的 Agent 自我进化 / 升级到 RSI 的必要一步：改进“如何教学试验”本身


 <p>只在固定算法下迭代更新技能，可以称<strong>教学反馈驱动的系统层面持续自改进</strong>；还不足以声称改进器本身学会递归改进。后续元策略 <code>π_φ</code> 可选择 <code>a=(选哪种学生, 何种试教任务/追问, 证据检查, 编辑目标, 停止/拒绝)</code>。</p>
 <p>元控制器从历史的<strong>教师自身</strong>独立增益学习，而不是从学生答对率学习；例如：</p>
 <div class="equation">R_meta = Δ Success_T,on-meta-dev − λ Regression_T − μ (Tokens + ToolCalls + Compute)</div>
 <p>元策略训练只读 <code>D_meta</code> 的效果标签，最外层 <code>D_test</code> 彻底封存。比较固定 Student 策略、随机 Probe、教师自己选 Probe、普通 contextual bandit，以及训练后的 <code>π_φ</code>。特别重要：<b>Meta-reset</b>——把教师重置为同一个初始快照，仅保留新旧两版元控制器，在未见任务流比较“能否更高效地找到、验证并修复盲点”。</p>
 <p>学生提问策略可能已经能通过 DPO 训练，本身也不是新颖性；我们检验的是<strong>提问对教师后续改进决策的价值</strong>，并与固定问句和普通不确定性采样比较。<a class="cite" href="references.html#S24" title="Socratic Students: Teaching Language Models to Learn by Asking Questions">[S24]</a><a class="cite" href="references.html#M07" title="Dual Control for Approximate Bayesian Reinforcement Learning">[M07]</a></p>


## I5 · 教学反馈驱动的 Agent 自我进化 / 模型 / 数据集 / 工程实现建议


 <div class="table-wrap"><table><thead><tr><th>组件</th><th>初始建议</th><th>验收要求</th></tr></thead><tbody>
 <tr><td>Teacher</td><td>Qwen3.5-9B（主），27B 同族扩展。</td><td>先选有成功也有失败的工具任务，且单次运行可复位。<a class="cite" href="references.html#B04" title="Qwen3.5-9B">[B04]</a><a class="cite" href="references.html#B05" title="Qwen3.5-27B">[B05]</a></td></tr>
 <tr><td>Student pool</td><td>一个弱于 T、一个与 T 不同家族的冻结 Student；另设同底座干净副本。</td><td>强弱关系用环境基线<strong>实测</strong>，不靠参数量猜测。</td></tr>
 <tr><td>诊断 / Patch Editor</td><td>共享冻结模型；条件间不换 Editor。</td><td>相同任务、样例、生成候选数和上下文预算。</td></tr>
 <tr><td>机制主环境</td><td>ToolSandbox + 在其 API 风格下构造的独立任务族。</td><td>可复位状态、工具轨迹、真实终止判断。<a class="cite" href="references.html#B01" title="ToolSandbox: A Stateful, Conversational, Interactive Evaluation Benchmark for LLM Tool Use Capabilities">[B01]</a></td></tr>
 <tr><td>第二环境</td><td>AppWorld 的 train / dev，或版本锁定的 τ 文本任务。</td><td>评测集不进入教学或选择；AppWorld 的 test_normal / test_challenge 仅作最终测试。<a class="cite" href="references.html#B07" title="AppWorld Benchmark: executable app-ecosystem agent tasks">[B07]</a><a class="cite" href="references.html#B02" title="τ-bench / τ²-bench：官方仓库与版本化评测协议">[B02]</a></td></tr>
 <tr><td>外部评测</td><td>固定 Terminal-Bench 2.1 / AppWorld test。</td><td>只评冻结方法及整体结果，不看单题测试报告调参。<a class="cite" href="references.html#B03" title="Terminal-Bench 2.1">[B03]</a><a class="cite" href="references.html#B07" title="AppWorld Benchmark: executable app-ecosystem agent tasks">[B07]</a></td></tr></tbody></table></div>
 <p>推荐 <code>Python 3.12 + pydantic + vLLM/LiteLLM + Docker + Parquet/JSONL</code> 实现小规模闭环；并行分支用任务队列与独立环境快照。第二阶段再引入 LoRA / GRPO，不把大规模 RL 训练作为 P0 前提。这里只规定接口与验收，暂未安装运行以上栈。</p>


## I5 · 教学反馈驱动的 Agent 自我进化 / P0：两周内应该产出的硬证据


 <p><b>先验证两个现象，而不是直接跑完整 RSI。</b>第一，教学后的独立 Student 行为是否比教师等预算直接 Probe 更常暴露<strong>经复现的教师规则缺口</strong>？第二，针对这些缺口的同预算 patch 是否比自我反思和直接技能归纳提升了<strong>教师自身</strong>的未见任务表现？</p>
 <div class="table-wrap"><table><thead><tr><th>阶段</th><th>建议规模（计划）</th><th>准入门槛</th></tr></thead><tbody>
 <tr><td>P0a · 管线预检</td><td>4 个任务族 × 2 Student × 3 seed</td><td>环境可复位、数据/答案隔离、Student 真正独立执行。</td></tr>
 <tr><td>P0b · 盲区辨别</td><td>24 个任务族 × 2 Student × 3 seed；每轮限制提问/执行</td><td>有稳定、验证通过且不能完全由学生弱点解释的事件。</td></tr>
 <tr><td>P0c · 方法对照</td><td>对 P0b 中合法事件生成 3 个 patch，同父版本配对比较</td><td>相同调用/编辑/验证成本下，教师未见任务净收益优于最强朴素基线。</td></tr>
 <tr><td>P1 · 长程与迁移</td><td>2 个通用环境、≥2 教师、不同家族学生、5 条独立学习流</td><td>效果迁移到自然失败、不同工具组合；报告所有失败与回归。</td></tr>
 </tbody></table></div>
 <p>以上为计划规模，不是已跑实验。先按任务族聚类分析；多条相似 Probe 不能假装是独立统计单位。选择成功与失败混合的 T 初始状态须遵守<strong>事先固定的筛选规则</strong>并披露丢弃比例，不能只挑特别容易修复的案例。</p>


## I5 · 教学反馈驱动的 Agent 自我进化 / 六种不可省的基线、消融与失败条件


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


## I5 · 教学反馈驱动的 Agent 自我进化 / 论文路线与可投稿主张的上限


 <p><b>最小论文主张：</b>存在并可量化一种“学生独立应用所教规则所暴露的、教师自我测试容易遗漏的错误信息”，且验证后可用于教师自身的持久技能改进。</p>
 <p><b>更强论文主张：</b>在相同任务、预算、编辑器与验证器条件下，基于 Student 反馈的归因与更新比通用反思/直接 Probe 改进了跨任务的教师独立成功率，并能在新学生和新任务机制上复现。</p>
 <p><b>Meta-RSI 级主张：</b>训练后的教学 Probe 策略，在重置底层教师后的新任务流中比冻结元策略更高效；它优化的是未来学习过程，而不只是当前补丁。</p>
 <div class="note">这三个主张递进但不等价。论文初期应只承诺前两层；看到 P0 / P1 结果后再决定第三层。与 2024 LbT、AAAI 2026 MARS、SKILL-KD 和学生提问研究的逐实验对比仍需要在正式投稿前持续更新。<a class="cite" href="references.html#S20" title="Can LLMs Learn by Teaching for Better Reasoning? A Preliminary Study">[S20]</a><a class="cite" href="references.html#S21" title="MARS: Multi-Agent Adaptive Reasoning with Socratic Guidance for Automated Prompt Optimization">[S21]</a><a class="cite" href="references.html#S22" title="SKILL-KD: Contrastive Skill Distillation for LLM Agents">[S22]</a><a class="cite" href="references.html#S24" title="Socratic Students: Teaching Language Models to Learn by Asking Questions">[S24]</a></div>


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

<p>本专题截至 2026-10-21，定向覆盖 RSI、学习型改进器、课程/元学习、学习科学及实验资源。用论文标题、方法词与引用链交叉检索，优先 arXiv、会议页面、作者机构和官方仓库。</p><p><b>阅读深度不同：</b>“正文方法”表示核对了方法/实验设置，不等于逐条复现全部结果；“摘要”只支持摘要范围的陈述；“官方资源”只确认资产与文档存在。代码入口存在不等于依赖安装、运行、原表重现成功。</p><p><b>原始材料与本次研究：</b>用户分享的推文用于确定入口和问题，不把推文统计或数字自动当作原论文结论。新提案、框架与优先级属于本专题分析，均非文献已经证明的结果。</p><p><b>搜索主题：</b>recursive self-improvement / harness optimization / meta-learning / automated curriculum / learning progress / learner modeling / assistance dilemma / fading / retrieval practice / productive failure / interference replay。</p><div class="note">这是针对选题的证据地图，不是穷尽全部文献的系统综述。未能核对的作者、发表状态、代码可运行性不补写；预印本标注月份。链接会随论文修订与仓库更新变化，实验须另锁 commit / revision。</div><div class="links"><a class="link-btn" href="sources.json" download>下载来源 JSON</a><a class="link-btn" href="sources.tsv" download>下载来源 TSV</a><a class="link-btn" href="research-notes.md" download>下载整篇研究笔记</a></div>

## 来源与核验记录 / RSI · 25 项

<article class="source-card" id="S01"><div class="source-meta"><span class="ref-id">S01</span><span>arXiv 26.07</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/2607.07663" target="_blank" rel="noopener noreferrer">Recursive Self-Improvement in AI: From Bounded Self-Refinement to Autonomous Research Loops</a></h3><p>按修改对象和闭环程度整理 RSI；用于界定范围，不把一种严格定义当成全领域共识。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2607.07663" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S02"><div class="source-meta"><span class="ref-id">S02</span><span>arXiv 25.05；核对 v3</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/2505.22954" target="_blank" rel="noopener noreferrer">Darwin Godel Machine: Open-Ended Evolution of Self-Improving Agents</a></h3><p>维护代码谱系，以任务执行评价自修改版本；代码自进化与开放式搜索已有系统基础。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2505.22954" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S03"><div class="source-meta"><span class="ref-id">S03</span><span>ICLR 2026 Oral；arXiv 25.07</span><span class="evidence">摘要与官方仓库核对</span></div><h3><a href="https://arxiv.org/abs/2507.19457" target="_blank" rel="noopener noreferrer">GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning</a></h3><p>反思执行轨迹，提出并测试提示修改、组合互补经验；可作共享编辑器和强搜索基线。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2507.19457" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/gepa-ai/gepa" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S04"><div class="source-meta"><span class="ref-id">S04</span><span>arXiv 25.06</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/2506.10943" target="_blank" rel="noopener noreferrer">Self-Adapting Language Models (SEAL)</a></h3><p>生成微调数据和更新指令，以更新后模型表现学习自编辑；属于参数持久更新。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2506.10943" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S05"><div class="source-meta"><span class="ref-id">S05</span><span>arXiv 26.03</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/2603.19461" target="_blank" rel="noopener noreferrer">Hyperagents</a></h3><p>任务 Agent 与修改它的 Meta-Agent 同在可编辑程序中；双层循环本身不再是充分创新。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2603.19461" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S06"><div class="source-meta"><span class="ref-id">S06</span><span>arXiv 26.07</span><span class="evidence">正文方法核对</span></div><h3><a href="https://arxiv.org/abs/2607.05297" target="_blank" rel="noopener noreferrer">MetaSkill-Evolve: Recursive Self-Improvement of LLM Agents via Two-Timescale Meta-Skill Evolution</a></h3><p>快慢时间尺度分别更新任务技能与元技能；与泛化的“改进器积累经验”直接相邻。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2607.05297" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S07"><div class="source-meta"><span class="ref-id">S07</span><span>arXiv 26.08</span><span class="evidence">摘要与官方仓库核对</span></div><h3><a href="https://arxiv.org/abs/2608.02276" target="_blank" rel="noopener noreferrer">Harness-R1: Learning to Edit Executable Runtime Harnesses from Agent Failure Trajectories</a></h3><p>训练专门的 Harness 编辑器，以真实执行表现优化修改；学习生成补丁不是新的空白。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2608.02276" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/DeepExperience/Harness-R1" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S08"><div class="source-meta"><span class="ref-id">S08</span><span>arXiv 26.09</span><span class="evidence">正文方法核对</span></div><h3><a href="https://arxiv.org/abs/2609.35738" target="_blank" rel="noopener noreferrer">Harness Learning Enables Generalizable Test-Time Adaptation</a></h3><p>把 Harness 修改作为元学习问题，学习可迁移适应策略；需比较新任务学习过程。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2609.35738" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S09"><div class="source-meta"><span class="ref-id">S09</span><span>arXiv 26.09</span><span class="evidence">正文方法与官方仓库核对</span></div><h3><a href="https://arxiv.org/abs/2609.14857" target="_blank" rel="noopener noreferrer">ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement</a></h3><p>成败轨迹对照、模块化修改与独立任务迁移；上述三项组合不能直接当作新方向。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2609.14857" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/IQuestLab/ModularRSI" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S10"><div class="source-meta"><span class="ref-id">S10</span><span>arXiv 26.09；核对 26.10 修订摘要</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/2609.24972" target="_blank" rel="noopener noreferrer">RRSI: Regularized Recursive Self-Improvement of Agent Harnesses</a></h3><p>正则化修改提议和选择，缓解递归搜索过拟合；不同修订的实验数字不混用。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2609.24972" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S11"><div class="source-meta"><span class="ref-id">S11</span><span>arXiv 26.09</span><span class="evidence">摘要与项目入口核对</span></div><h3><a href="https://arxiv.org/abs/2609.14858" target="_blank" rel="noopener noreferrer">Dream-RSI: Recursive Self-Improvement through Evolving Worlds</a></h3><p>利用历史发现树回放优化探索策略；回放覆盖范围之外的收益需真实执行验证。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2609.14858" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/zhengkid/Dream-RSI" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S12"><div class="source-meta"><span class="ref-id">S12</span><span>arXiv 26.10</span><span class="evidence">正文方法与官方仓库核对</span></div><h3><a href="https://arxiv.org/abs/2610.14224" target="_blank" rel="noopener noreferrer">Harness²: Recursive Agent Harnessing for an Open World</a></h3><p>任务内修改与跨任务 Harnessing 经验积累；行为对比不等于带标准答案的正确性证明。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2610.14224" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/google-research/harness2" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S13"><div class="source-meta"><span class="ref-id">S13</span><span>arXiv 26.10</span><span class="evidence">摘要与官方仓库核对</span></div><h3><a href="https://arxiv.org/abs/2610.13912" target="_blank" rel="noopener noreferrer">RSI-Anything: Unlocking Recursive Self-Improvement with World Models</a></h3><p>预测行动后果，再以真实反馈校正；环境动力学与学习者更新后能力变化是不同对象。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2610.13912" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/Gen-Verse/RSI-Anything" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S14"><div class="source-meta"><span class="ref-id">S14</span><span>arXiv 26.07</span><span class="evidence">摘要与官方仓库核对</span></div><h3><a href="https://arxiv.org/abs/2607.12227" target="_blank" rel="noopener noreferrer">Rethinking the Evaluation of Harness Evolution for Agents</a></h3><p>强调与等反馈、等推理预算的普通采样和顺序精修比较；复杂流程不能只按得分解释。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2607.12227" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/rethinking-harness-evolution/code" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S15"><div class="source-meta"><span class="ref-id">S15</span><span>arXiv 26.10</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/2610.14662" target="_blank" rel="noopener noreferrer">Does Failure Feedback Direct Agent Self-Modification?</a></h3><p>目标修复、相关失败迁移和独立测试增益须分开；反馈效果具有模型依赖性。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2610.14662" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S16"><div class="source-meta"><span class="ref-id">S16</span><span>arXiv 26.10</span><span class="evidence">正文方法与实验设置核对</span></div><h3><a href="https://arxiv.org/html/2610.00906v1" target="_blank" rel="noopener noreferrer">ActiveSaddler: Automated Curriculum Learning for Agent Harness Optimization</a></h3><p>失败模式作为动态 bandit 臂，以学习进展调整优先级并探索新失败；直接覆盖自动修复课程。</p><div class="links"><a class="link-btn" href="https://arxiv.org/html/2610.00906v1" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S17"><div class="source-meta"><span class="ref-id">S17</span><span>arXiv 26.01；核对 v3</span><span class="evidence">正文方法与实验设置核对</span></div><h3><a href="https://arxiv.org/html/2601.18778v3" target="_blank" rel="noopener noreferrer">Teaching Models to Teach Themselves: Reasoning at the Edge of Learnability (SOAR)</a></h3><p>双层元强化学习让教师出题，以学生在困难题上的实际进步作奖励，而非仅用难度代理。</p><div class="links"><a class="link-btn" href="https://arxiv.org/html/2601.18778v3" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S18"><div class="source-meta"><span class="ref-id">S18</span><span>arXiv 26.10</span><span class="evidence">正文方法与实验设置核对</span></div><h3><a href="https://arxiv.org/html/2610.04604v1" target="_blank" rel="noopener noreferrer">Anticipating the Consequences of Curriculum Decisions with Large Language Models</a></h3><p>将学习进展、下游迁移潜力和当前可学性结合；任务依赖图与前瞻课程已有近邻。</p><div class="links"><a class="link-btn" href="https://arxiv.org/html/2610.04604v1" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/Octavio-Pappalardo/curriculum-foresight" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S19"><div class="source-meta"><span class="ref-id">S19</span><span>arXiv 26.10</span><span class="evidence">正文方法与实验设置核对</span></div><h3><a href="https://arxiv.org/html/2610.06446v1" target="_blank" rel="noopener noreferrer">The Assistance Dilemma: Learning to Teach via Multi-Turn Reinforcement Learning</a></h3><p>遮蔽教师话语的近迁移后测仍保留学生话语；单题回报难覆盖支持撤除的远期价值。</p><div class="links"><a class="link-btn" href="https://arxiv.org/html/2610.06446v1" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/eth-lre/EduardoRL" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S20"><div class="source-meta"><span class="ref-id">S20</span><span>NeurIPS 2024；arXiv 24.06</span><span class="evidence">会议正文与官方仓库核对</span></div><h3><a href="https://proceedings.neurips.cc/paper_files/paper/2024/hash/8340b085045cf13f1f0b6c2c4cc0a89c-Abstract-Conference.html" target="_blank" rel="noopener noreferrer">Can LLMs Learn by Teaching for Better Reasoning? A Preliminary Study</a></h3><p>教师解释根据学生反馈选择；反馈可以构成 DPO 训练偏好；多学生多样性是已有近邻。不能把 teacher 由 student feedback 更新称作首次提出。</p><div class="links"><a class="link-btn" href="https://proceedings.neurips.cc/paper_files/paper/2024/hash/8340b085045cf13f1f0b6c2c4cc0a89c-Abstract-Conference.html" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/imagination-research/lbt" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="S21"><div class="source-meta"><span class="ref-id">S21</span><span>AAAI 2026</span><span class="evidence">会议摘要与方法概述核对</span></div><h3><a href="https://ojs.aaai.org/index.php/AAAI/article/view/38668" target="_blank" rel="noopener noreferrer">MARS: Multi-Agent Adaptive Reasoning with Socratic Guidance for Automated Prompt Optimization</a></h3><p>Teacher-Critic-Student Socratic dialogue 用于提示优化；多智能体教学及问题驱动迭代不能单独作为方法创新。</p><div class="links"><a class="link-btn" href="https://ojs.aaai.org/index.php/AAAI/article/view/38668" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S22"><div class="source-meta"><span class="ref-id">S22</span><span>arXiv 26.07</span><span class="evidence">摘要与作者公开说明核对</span></div><h3><a href="https://arxiv.org/abs/2607.28048" target="_blank" rel="noopener noreferrer">SKILL-KD: Contrastive Skill Distillation for LLM Agents</a></h3><p>对比教师成功与学生失败轨迹，迭代修改学生的技能；本候选必须与“更新教师自己”区分，并避免只做反向技能蒸馏。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2607.28048" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S23"><div class="source-meta"><span class="ref-id">S23</span><span>arXiv 26.08</span><span class="evidence">论文正文与摘要核对</span></div><h3><a href="https://arxiv.org/abs/2608.20274" target="_blank" rel="noopener noreferrer">Break It Down, Pass It On: Cross-Task Skill Transfer in LLM Agents</a></h3><p>子任务级和任务级技能、文本与代码技能对跨任务迁移有不同影响；要求本候选与直接细粒度技能归纳和静态技能质量评价比较。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2608.20274" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S24"><div class="source-meta"><span class="ref-id">S24</span><span>arXiv 25.12</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/2512.13102" target="_blank" rel="noopener noreferrer">Socratic Students: Teaching Language Models to Learn by Asking Questions</a></h3><p>训练学生主动询问教师以改善学生的学习效率；不能把会追问的 Student 当作空白，需证明问题对 Teacher 自身能力有独立信息。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2512.13102" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="S25"><div class="source-meta"><span class="ref-id">S25</span><span>arXiv 23.11</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/2311.06985" target="_blank" rel="noopener noreferrer">Large Language Models are In-context Teachers for Knowledge Reasoning</a></h3><p>提出 Self-Explain 和 Teach-Back 来提高学生的 in-context knowledge reasoning；Teach-Back 名称本身不保证与教师自进化相关。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/2311.06985" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article>

## 来源与核验记录 / 相邻领域 · 9 项

<article class="source-card" id="M01"><div class="source-meta"><span class="ref-id">M01</span><span>arXiv 16.06</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/1606.04474" target="_blank" rel="noopener noreferrer">Learning to learn by gradient descent by gradient descent</a></h3><p>学习优化算法而非只优化任务模型；更新规则可作为学习对象，但不提供通用 RSI 保证。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/1606.04474" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="M02"><div class="source-meta"><span class="ref-id">M02</span><span>arXiv 16.11</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/1611.02779" target="_blank" rel="noopener noreferrer">RL²: Fast Reinforcement Learning via Slow Reinforcement Learning</a></h3><p>跨任务训练快速适应算法；启发重置学习者、保留元策略的检验。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/1611.02779" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="M03"><div class="source-meta"><span class="ref-id">M03</span><span>arXiv 17.04</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/1704.03003" target="_blank" rel="noopener noreferrer">Automated Curriculum Learning for Neural Networks</a></h3><p>用非平稳 bandit 和学习进度选择训练数据；难度改为进展并非新颖机制。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/1704.03003" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="M04"><div class="source-meta"><span class="ref-id">M04</span><span>arXiv 17.07</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/1707.00183" target="_blank" rel="noopener noreferrer">Teacher-Student Curriculum Learning (TSCL)</a></h3><p>优先练习进步快的子任务，也重访性能下降的任务；学习和防遗忘联合调度已有经典基线。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/1707.00183" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a><a class="link-btn repo" href="https://github.com/tambetm/TSCL" target="_blank" rel="noopener noreferrer">代码 / 官方执行资源</a></div></article><article class="source-card" id="M05"><div class="source-meta"><span class="ref-id">M05</span><span>NeurIPS 2015</span><span class="evidence">会议原始摘要核对</span></div><h3><a href="https://papers.nips.cc/paper/5654-deep-knowledge-tracing" target="_blank" rel="noopener noreferrer">Deep Knowledge Tracing</a></h3><p>从学习交互序列估计学生知识状态；下一题正确率预测不等于某种教学干预的因果收益。</p><div class="links"><a class="link-btn" href="https://papers.nips.cc/paper/5654-deep-knowledge-tracing" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="M06"><div class="source-meta"><span class="ref-id">M06</span><span>NeurIPS 2018</span><span class="evidence">会议原始摘要核对</span></div><h3><a href="https://proceedings.neurips.cc/paper/2018/hash/8051a3c40561002834e59d566b7430cf-Abstract.html" target="_blank" rel="noopener noreferrer">Learning to Teach with Dynamic Loss Functions</a></h3><p>教师按学生阶段输出动态损失，以开发集表现优化教学；应迁移双层目标而非师生角色名称。</p><div class="links"><a class="link-btn" href="https://proceedings.neurips.cc/paper/2018/hash/8051a3c40561002834e59d566b7430cf-Abstract.html" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="M07"><div class="source-meta"><span class="ref-id">M07</span><span>arXiv 15.10</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/1510.03591" target="_blank" rel="noopener noreferrer">Dual Control for Approximate Bayesian Reinforcement Learning</a></h3><p>行动同时改变状态并揭示未知动力学；需验证诊断信息是否真正改变后续更新决策。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/1510.03591" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="M08"><div class="source-meta"><span class="ref-id">M08</span><span>ICLR 2016；arXiv 15.11</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/1511.05952" target="_blank" rel="noopener noreferrer">Prioritized Experience Replay</a></h3><p>按经验重要性非均匀重放；间隔练习方案必须排除普通优先重放即可解释收益。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/1511.05952" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="M09"><div class="source-meta"><span class="ref-id">M09</span><span>NeurIPS 2019；arXiv 19.08</span><span class="evidence">摘要核对</span></div><h3><a href="https://arxiv.org/abs/1908.04742" target="_blank" rel="noopener noreferrer">Online Continual Learning with Maximally Interfered Retrieval</a></h3><p>选择可能被当前更新干扰的旧样本重放；作为干扰感知巩固的重要对照。</p><div class="links"><a class="link-btn" href="https://arxiv.org/abs/1908.04742" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article>

## 来源与核验记录 / 学习科学 · 10 项

<article class="source-card" id="E01"><div class="source-meta"><span class="ref-id">E01</span><span>Theory Into Practice, 2002</span><span class="evidence">理论综述与元数据核对</span></div><h3><a href="https://www.tandfonline.com/doi/abs/10.1207/s15430421tip4102_2" target="_blank" rel="noopener noreferrer">Becoming a Self-Regulated Learner: An Overview</a></h3><p>自我调节的前瞻、执行监控与反思是设计视角；不是增加三个 Agent 模块即可有效的证明。</p><div class="links"><a class="link-btn" href="https://www.tandfonline.com/doi/abs/10.1207/s15430421tip4102_2" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E02"><div class="source-meta"><span class="ref-id">E02</span><span>Journal of Memory and Language, 2005</span><span class="evidence">作者存档与摘要核对</span></div><h3><a href="https://www.columbia.edu/cu/psychology/metcalfe/PDFs/Metcalfe%20Kornell%202005.pdf" target="_blank" rel="noopener noreferrer">A Region of Proximal Learning model of study time allocation</a></h3><p>在尚未掌握且可取得进展的材料间分配时间；不等同于挑最难题，也不与其他近侧发展区理论混称。</p><div class="links"><a class="link-btn" href="https://www.columbia.edu/cu/psychology/metcalfe/PDFs/Metcalfe%20Kornell%202005.pdf" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E03"><div class="source-meta"><span class="ref-id">E03</span><span>Psychological Science, 2006</span><span class="evidence">原始研究摘要核对</span></div><h3><a href="https://pubmed.ncbi.nlm.nih.gov/16507066/" target="_blank" rel="noopener noreferrer">Test-enhanced learning: taking memory tests improves long-term retention</a></h3><p>比较练习性检索与重复阅读的保持效果；冻结模型需要持久写入才能形成跨会话学习。</p><div class="links"><a class="link-btn" href="https://pubmed.ncbi.nlm.nih.gov/16507066/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E04"><div class="source-meta"><span class="ref-id">E04</span><span>Psychological Science, 2008</span><span class="evidence">原始研究摘要核对</span></div><h3><a href="https://pubmed.ncbi.nlm.nih.gov/19076480/" target="_blank" rel="noopener noreferrer">Spacing effects in learning: a temporal ridgeline of optimal retention</a></h3><p>间隔效果依赖保持时长；机器实验应操纵中间学习和干扰，不假定静止参数随时间遗忘。</p><div class="links"><a class="link-btn" href="https://pubmed.ncbi.nlm.nih.gov/19076480/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E05"><div class="source-meta"><span class="ref-id">E05</span><span>Journal of Educational Psychology, 2003</span><span class="evidence">作者机构摘要核对</span></div><h3><a href="https://asu.elsevierpure.com/en/publications/transitioning-from-studying-examples-to-solving-problems-effects-/" target="_blank" rel="noopener noreferrer">Transitioning From Studying Examples to Solving Problems: Effects of Self-Explanation Prompts and Fading Worked-Out Steps</a></h3><p>研究例题到自主解题、逐步撤去步骤及自我解释；支持撤除是教学干预，不只是评测删提示。</p><div class="links"><a class="link-btn" href="https://asu.elsevierpure.com/en/publications/transitioning-from-studying-examples-to-solving-problems-effects-/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E06"><div class="source-meta"><span class="ref-id">E06</span><span>Learning: Research and Practice, 2015</span><span class="evidence">作者机构摘要核对</span></div><h3><a href="https://repository.nie.edu.sg/entities/publication/cd4409fb-a12f-476f-ad02-febbf9caa4cc" target="_blank" rel="noopener noreferrer">Learning from productive failure</a></h3><p>生成探索后进行知识整理巩固；关键在教学次序与整合，不是错误越多越好。</p><div class="links"><a class="link-btn" href="https://repository.nie.edu.sg/entities/publication/cd4409fb-a12f-476f-ad02-febbf9caa4cc" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E07"><div class="source-meta"><span class="ref-id">E07</span><span>Educational Psychology Review, 2007</span><span class="evidence">作者机构记录与论文摘要核对</span></div><h3><a href="https://act-r.psy.cmu.edu/?post_type=publications&amp;p=14210" target="_blank" rel="noopener noreferrer">Exploring the assistance dilemma in experiments with Cognitive Tutors</a></h3><p>何时、以何种程度帮助是教学设计问题；不能直接推出 LLM 上的有效性。</p><div class="links"><a class="link-btn" href="https://act-r.psy.cmu.edu/?post_type=publications&amp;p=14210" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E08"><div class="source-meta"><span class="ref-id">E08</span><span>Educational Psychologist, 2016</span><span class="evidence">作者机构摘要核对</span></div><h3><a href="https://repository.eduhk.hk/en/publications/examining-productive-failure-productive-success-unproductive-fail-5/" target="_blank" rel="noopener noreferrer">Examining productive failure, productive success, unproductive failure, and unproductive success in learning</a></h3><p>区分学习时表现与长期学习收益；用于提出测量问题，机器机制须另行验证。</p><div class="links"><a class="link-btn" href="https://repository.eduhk.hk/en/publications/examining-productive-failure-productive-success-unproductive-fail-5/" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E09"><div class="source-meta"><span class="ref-id">E09</span><span>Journal of the Learning Sciences, 2013</span><span class="evidence">完整论文机制与实验设计核对</span></div><h3><a href="https://aaalab.stanford.edu/research/assets/papers/2013/Learning_by_teaching_human_pupils.pdf" target="_blank" rel="noopener noreferrer">Learning by Teaching Human Pupils and Teachable Agents: The Importance of Recursive Feedback</a></h3><p>Recursive Feedback 要求学生在新环境中自主使用所学以及教师把学生行为映射回自己的理解；人类机制不能直接视为 LLM 有效性。</p><div class="links"><a class="link-btn" href="https://aaalab.stanford.edu/research/assets/papers/2013/Learning_by_teaching_human_pupils.pdf" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article><article class="source-card" id="E10"><div class="source-meta"><span class="ref-id">E10</span><span>Behaviormetrika, 2026</span><span class="evidence">正文摘要与研究设计核对</span></div><h3><a href="https://link.springer.com/article/10.1007/s41237-026-00294-9" target="_blank" rel="noopener noreferrer">Beyond prior knowledge: the predictive role of knowledge-building in tutor learning</a></h3><p>人类教师面对 teachable agent 追问时 knowledge-building 比 knowledge-telling 更具诊断意义，相关性结果不是 LLM 教学自进化的因果证据。</p><div class="links"><a class="link-btn" href="https://link.springer.com/article/10.1007/s41237-026-00294-9" target="_blank" rel="noopener noreferrer">原论文 / 原始来源</a></div></article>

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
