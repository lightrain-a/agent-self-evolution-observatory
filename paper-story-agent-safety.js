window.PAPER_STORY_DATA.papers["AGENT-SAFETY-R9"]={
paper_archetype:"evaluation_protocol",
thesis:{zh:"一次‘现在安全’的通过，不应被误当成‘未来一段时间安全’的证书；我们把安全评测改写成有限 horizon 的 first-violation 检验，并用同 schedule no-update 对照隔离 update-associated contrast。",en:"A safety pass now should not be mistaken for a future certificate; the paper reframes evaluation as a finite-horizon first-violation test with a same-schedule no-update control."},
scene:{zh:"持续运行的 Web Agent 会把经历写入 memory、更新 workflow，再处理后续任务。真实部署往往在某个 snapshot 做一次安全检查，然后继续运行。",en:"Persistent web agents write experience into memory, update workflows, and continue acting after a safety check at a particular snapshot."},
value:{zh:"如果 current PASS 被错误解释成 future guarantee，组织可能在 Agent state 已变化时仍沿用旧安全结论。真正需要问的是：这个 PASS 对声明 horizon 到底保证了什么。",en:"If a current PASS is treated as a future guarantee, deployments may rely on stale safety conclusions after agent state changes."},
failure_example:{zh:"4 个 persistent state 在当前 qualification panel 上 12/12 都不违规；但沿冻结的三步未来继续运行后，updated workflow 出现 8/12 first-violation branch。",en:"All 12 current qualification episodes are clean, yet updated workflows produce first violations in 8/12 branches over the frozen future."},
approaches:[
{name:"静态安全 benchmark",how_zh:"在当前 Agent snapshot 上跑一组安全任务。",how_en:"Evaluate safety on the current snapshot.",problem_zh:"只能回答‘现在是否通过’，不能回答 state 更新后 horizon 内是否仍安全。",problem_en:"Answers current safety but not future safety after state updates."},
{name:"before/after longitudinal probe",how_zh:"在多个 snapshot 重复同类 probe，看安全分如何变化。",how_en:"Repeat probes across snapshots.",problem_zh:"能看到变化，但没有相同 future schedule 的 no-update 对照时，无法把变化局部化到 update。",problem_en:"Shows change but cannot localize it to updating without a same-schedule no-update control."},
{name:"aggregate violation rate",how_zh:"统计未来总体违规率或平均安全分。",how_en:"Report aggregate future violation rates or mean safety scores.",problem_zh:"丢失‘第一次什么时候出问题’的时间结构，也难定义 certificate failure。",problem_en:"Loses first-event timing and blurs the certificate interpretation."}
],
gaps:[
{id:"G1",title_zh:"PASS 没有 horizon 语义",title_en:"PASS lacks horizon semantics",text_zh:"需要把 current pass 变成可反驳的未来命题：H 步内是否出现 first violation。",text_en:"Turn a current pass into a falsifiable first-violation claim over horizon H."},
{id:"G2",title_zh:"future schedule 是混杂",title_en:"Future schedule is a confound",text_zh:"即使不更新 workflow，同样 future tasks 也可能更难；必须有 same-schedule no-update。",text_en:"Future tasks can be risky even without updates, requiring a same-schedule no-update control."},
{id:"G3",title_zh:"需要 state-dependence 证据",title_en:"Need state-dependence evidence",text_zh:"除了 branch event，还要把同一 probe/seed 放到后续 snapshot，检查 label 是否随 state 变化。",text_en:"Replay identical probes and seeds across snapshots to test state dependence."}
],
missing_scientific_object:{zh:"现有静态 safety evaluation 缺少一个明确的 temporal certification object：当前 snapshot 的 PASS 对声明的未来 horizon 到底意味着什么，以及 future schedule 自身的风险与 persistent-state update 带来的差异如何分开。",en:"Static safety evaluation lacks an explicit temporal certification object: what a current PASS means over a declared future horizon and how to separate schedule risk from persistent-state updating."},
research_question:{zh:"一个当前安全 panel 的 clean PASS 是否能作为声明 horizon 的 future certificate；在同一 future task / seed / branch / evaluator schedule 下，updated workflow 相比固定 step-0 workflow 是否出现额外 first-violation events？",en:"Does a clean current safety panel certify a declared future, and under an identical future schedule does updating the workflow produce additional first-violation events relative to a fixed step-0 workflow?"},
design_requirements:[
{zh:"先证明 qualification 起点 clean，避免把已有违规当作未来退化。",en:"Establish a clean qualification starting point."},
{zh:"future schedule 必须在 updated / no-update 两臂完全匹配。",en:"Match the future schedule exactly across updated and no-update arms."},
{zh:"endpoint 必须保留 first-event timing，而不只给 aggregate violation rate。",en:"Preserve first-event timing rather than only aggregate violation rate."},
{zh:"需要一个 probe identity / seed 固定且 no-writeback 的 state-dependence control。",en:"Include a fixed-probe, fixed-seed, no-writeback state-dependence control."}
],
mechanism_predictions:[
{prediction_zh:"如果 current PASS 不是 temporal certificate，就应存在 qualification clean 但 horizon 内首次违规的 branch。",prediction_en:"If a current PASS is not a temporal certificate, some clean-qualified branches should first violate within the future horizon.",tested_by:"Updated future first-violation trajectories"},
{prediction_zh:"如果一部分 future risk 与 workflow update 相关，而不只是 schedule 风险，paired outcomes 应出现 update-only branch，而不是全部在 fixed-workflow control 中重现。",prediction_en:"If some future risk is update-associated rather than schedule-only, paired outcomes should include update-only branches.",tested_by:"Same-schedule updated vs step-0 control"},
{prediction_zh:"如果评测结果依赖 persistent snapshot，同一 qualification probe / seed 在后续 snapshot 上可能出现 label change，即使 probe 本身不写回。",prediction_en:"If evaluated behavior depends on persistent snapshot, identical probes and seeds can change labels at later snapshots without probe writeback.",tested_by:"Fixed-probe snapshot replay"}
],
alternative_explanations:[
{name:"future task schedule 本来更危险",control_zh:"同 task / seed / branch / horizon / evaluator 的 step-0 fixed-workflow control。",control_en:"Step-0 fixed-workflow control on the identical task/seed/branch/horizon/evaluator schedule."},
{name:"只是换了 probe",control_zh:"同一 qualification probe identity + seed 在多个 workflow snapshot 重放，禁止 writeback。",control_en:"Replay the same qualification probe identity and seed across workflow snapshots with writeback disabled."},
{name:"平均违规率的随机波动",control_zh:"报告 12 个 paired branch 的 event/no-event 与 first-event time，而不是只给 pooled episode rate。",control_en:"Report all paired branch events and first-event times rather than only pooled episode rates."}
],
evaluation_contract:{strongest_baseline_zh:"same-schedule step-0 workflow control；辅助 baseline 是同一 qualification probe 的 snapshot replay。",strongest_baseline_en:"Same-schedule step-0 workflow control, plus fixed qualification-probe snapshot replay.",held_fixed_zh:"behavior ID、task、seed、branch、三步 horizon、runtime、evaluator、guard、threshold、call policy；主对照只改变 workflow snapshot 是否随步更新。",held_fixed_en:"Behavior ID, task, seed, branch, three-step horizon, runtime, evaluator, guard, threshold, and call policy; only workflow updating changes.",unit_zh:"12 个预先构造的 state×branch pair；36 episode 是 event-time 观测，不当作总体独立样本。",unit_en:"Twelve frozen state×branch pairs; 36 episodes provide event-time observations, not population-independent samples.",success_rule_zh:"反驳 temporal certificate 只需出现 declared-horizon first violation；update-associated contrast 只做 frozen finite paired interpretation，不升级为 population causal effect。",success_rule_en:"Any first violation falsifies the declared-horizon certificate; the update contrast remains a frozen finite paired result rather than a population causal effect."},
motivation:{zh:"方法不是再发明 safety score，而是定义 temporal certificate：冻结当前 PASS 和未来 task schedule；updated workflow 与 step-0 workflow 走完全相同 schedule；终点看 first violation，再用 fixed-probe snapshot replay 检查 state dependence。",en:"The method defines a temporal certificate: freeze the current pass and future schedule, compare updated and step-0 workflows on the same schedule, track first violation, and replay fixed probes across snapshots."},
components:[
{name:"Frozen current qualification",solves:"G1",role_zh:"先证明起点 clean，避免把已有违规误叫未来退化。",role_en:"Establishes a clean starting point."},
{name:"Same-schedule step-0 control",solves:"G2",role_zh:"固定 future task difficulty，让 schedule-only risk 可见。",role_en:"Holds future schedule fixed and exposes schedule-only risk."},
{name:"First-violation endpoint",solves:"G1",role_zh:"把 certificate failure 定义成有限 horizon 内第一次 event，而不是平均分。",role_en:"Defines certificate failure as the first event within a finite horizon."},
{name:"Fixed-probe snapshot replay",solves:"G3",role_zh:"probe/seed 不变且不写回 memory，只换 workflow snapshot。",role_en:"Keeps probe and seed fixed while changing only workflow snapshot."}
],
experiments:[
{rq:"RQ1",q_zh:"当前安全 panel 是否真的 clean？",q_en:"Is the current panel actually clean?",baseline_zh:"冻结 qualification panel。",baseline_en:"Frozen qualification panel.",answer_zh:"12/12 CLEAN。",answer_en:"12/12 clean."},
{rq:"RQ2",q_zh:"future violation 是 update 造成，还是 schedule 本身就危险？",q_en:"Are future violations update-associated or schedule-driven?",baseline_zh:"同 task / seed / branch / horizon 的 step-0 fixed workflow。",baseline_en:"Same task/seed/branch/horizon with step-0 workflow fixed.",answer_zh:"updated=8/12，base=4/12；paired discordance=4 update-only / 0 control-only。",answer_en:"Updated=8/12 versus base=4/12; four update-only / zero control-only discordances."},
{rq:"RQ3",q_zh:"相同 probe 是否会因为后续 state 改变而首次违规？",q_en:"Can the same probe first violate at a later state?",baseline_zh:"相同 probe identity + seed，禁止 probe writeback。",baseline_en:"Same probe identity and seed with no writeback.",answer_zh:"4/12 state–probe trajectory 在后续 snapshot 首次被判违规。",answer_en:"4/12 state–probe trajectories first violate at later snapshots."}
],
why_better:{zh:"比静态 benchmark 多了 horizon；比普通 longitudinal tracking 多了 same-schedule no-update 因果对照；比平均安全分多了 first-event timing。它不是证明‘所有 memory 都危险’，而是给出更严格的安全证书测试。",en:"It adds a horizon to static evaluation, a same-schedule no-update control to longitudinal tracking, and first-event timing to aggregate safety scores."},
component_evidence:[
{component:"same-schedule control",evidence_zh:"8/12 中有 4/12 同样出现在 base workflow。",evidence_en:"4/12 of the 8/12 updated events also occur under the base workflow.",meaning_zh:"没有这个对照，会把 schedule 自带风险全部错算成 update effect。",meaning_en:"Without it, schedule risk would be misattributed to updating."},
{component:"paired discordance",evidence_zh:"4 update-only / 0 control-only。",evidence_en:"Four update-only / zero control-only.",meaning_zh:"剩余有限 contrast 与 update 方向一致，但不是 population hazard。",meaning_en:"The finite contrast is update-associated but not a population hazard estimate."},
{component:"fixed probes",evidence_zh:"4/12 后续 label change。",evidence_en:"4/12 later label changes.",meaning_zh:"current PASS 不是 snapshot-independent certificate。",meaning_en:"A current PASS is not snapshot-independent."}
],
mechanism_tests:[
{name:"Static-pass falsifier",prediction_zh:"12/12 qualification clean 仍可能在未来 first violate。",prediction_en:"A 12/12 clean qualification panel can still be followed by future first violations.",result_zh:"updated workflow 8/12 branch 在 H=3 内出现 first violation。",result_en:"8/12 updated-workflow branches first violate within H=3."},
{name:"Same-schedule control",prediction_zh:"若 schedule-only 不能解释全部差异，应存在 update-only discordance。",prediction_en:"If schedule-only risk is insufficient, update-only discordances should remain.",result_zh:"4 update-only / 0 control-only；4 both / 4 neither。",result_en:"Four update-only / zero control-only; four both / four neither."},
{name:"Fixed-probe state dependence",prediction_zh:"同 probe/seed 的 label 可随 workflow snapshot 变化。",prediction_en:"Identical probes/seeds can change labels across workflow snapshots.",result_zh:"4/12 state–probe trajectory 后续首次违规；其中部分随后恢复，说明不是单调 degradation。",result_en:"4/12 trajectories first violate later; some subsequently revert, rejecting a monotonic-degradation story."}
],
generalization:{zh:"当前证据覆盖一个 Qwen3-8B + AWM + BrowserART/BrowserGym + HarmBench operationalization、4 个 selected states 和 H=3；它验证的是 measurement object 与有限 protocol，不声称跨 architecture 的 hazard law。",en:"Evidence covers one Qwen3-8B + AWM + BrowserART/BrowserGym + HarmBench operationalization, four selected states, and H=3; it validates a measurement object, not a cross-architecture hazard law."},
failure_regimes:[
{zh:"base-workflow control 自己也有 4/12 first-violation branch：future schedule 不是无风险背景。",en:"The base-workflow control itself has 4/12 event branches; the future schedule is not risk-free."},
{zh:"fixed probes 的 step-1/2 event 会在后续 snapshot 恢复，不能写成 monotonic safety degradation。",en:"Some fixed-probe events revert at later snapshots, so monotonic safety degradation is unsupported."},
{zh:"单 evaluator、有限 horizon、deliberately selected states 限制外部效度；不能拟合 population hazard。",en:"A single evaluator, finite horizon, and deliberately selected states limit external validity; no population hazard is estimated."}
],
boundary:{zh:"主贡献是 temporal certificate + paired first-event methodology。不要卖 longitudinal memory safety 首创，也不要把 12 个 branch 外推成总体 hazard；NullMemory、第二 evaluator、更长 horizon 仍是最强外部审稿缺口。",en:"The contribution is the temporal-certificate and paired first-event methodology, not the invention of longitudinal memory safety or a population hazard estimate."},
chain_of_evidence:[
{claim:"C1",evidence:"12 qualification episodes clean → 8/12 updated future branches first violate",boundary_zh:"只反驳当前 PASS 自动推出 H=3 future guarantee。",boundary_en:"Only falsifies the implication from current PASS to an H=3 future guarantee."},
{claim:"C2",evidence:"Same-schedule paired control: 8/12 updated vs 4/12 fixed workflow; 4 update-only / 0 control-only",boundary_zh:"有限 realized contrast，不是总体 causal effect。",boundary_en:"A finite realized contrast, not a population causal effect."},
{claim:"C3",evidence:"Fixed-probe snapshot replay: 4/12 later first violations",boundary_zh:"支持 snapshot dependence，不支持单调退化或 semantic mechanism。",boundary_en:"Supports snapshot dependence, not monotonic degradation or a semantic mechanism."}
],
outline:["场景：为什么 current PASS 会被误用成 future guarantee","定义 temporal certificate 与 first violation","same-schedule updated vs fixed-workflow design","当前 12/12 clean → future 8/12 vs 4/12","fixed-probe snapshot dependence","组件识别：schedule control / first-event / fixed probe","scope：single backbone/evaluator/H=3，NullMemory 等待扩展"]
};