window.PAPER_STORY_DATA.papers["STRI"]={
thesis:{zh:"自进化系统不应该因为‘同样能力被怎样拆成 skill package’就改变控制决策；STRI 把这个工程直觉变成可检验的不变量，并给出 package-only controller 下的精确可均衡性证书。",en:"A self-evolution controller should not change merely because the same capability is repackaged; STRI turns that intuition into an auditable invariant with an exact certificate."},
scene:{zh:"Agent 的 skill library 会不断扩张。相同语义能力可能因为版本升级、自动拆分、vendor 格式或去重策略，被表示成一个 skill、多个子 skill、clone 或重新分组的 package；控制器再根据 package identity 决定曝光、检索或更新。",en:"Skill libraries evolve, and the same capability can be represented as one skill, subskills, clones, or regrouped packages. Controllers then make exposure/retrieval/update decisions over package identities."},
value:{zh:"如果控制结果依赖 package 表示而不是语义能力，同一个 Agent 只因为技能怎么打包就会走向不同的自进化轨迹：结果不可复现，也可能被 split/clone 操纵。",en:"If control depends on packaging rather than capability, semantically identical agents can follow different evolution trajectories and can be manipulated by split/clone choices."},
failure_example:{zh:"一个‘查航班并比较价格’技能被拆成 4 个语义等价子包。任务能力没增加，但 package-level controller 看到 4 个 identity 后改变 exposure，其他技能被挤出，最终检索/行为改变。",en:"A capability is split into four semantically equivalent packages. Capability does not increase, yet package-level exposure changes and alters downstream retrieval/behavior."},
approaches:[
{name:"语义检索 / embedding routing",how_zh:"按 query 与 skill description 的语义相似度选技能。",how_en:"Route by semantic similarity.",problem_zh:"通常不问 semantic support 完全相同、只改 package identity 时，控制是否必须保持不变。",problem_en:"Rarely tests invariance under semantics-preserving repackaging."},
{name:"skill decomposition / composition",how_zh:"把大技能拆小、组合、路由，以提升覆盖或复用。",how_en:"Split, compose, and route skills.",problem_zh:"granularity 和 representation 一起变化，难区分‘能力真的变了’还是‘只是打包变了’。",problem_en:"Granularity and representation change together, confounding capability with packaging."},
{name:"exposure / ranking balancing",how_zh:"通过权重或公平约束平衡不同 item 的曝光。",how_en:"Balance exposure through weights or fairness constraints.",problem_zh:"可以优化给定目标，但不直接判断冻结 support geometry 后 package-only controller 是否能彻底消掉表示差异。",problem_en:"Does not directly diagnose exact removability under the frozen support geometry."}
],
gaps:[
{id:"G1",title_zh:"缺少表示不变量对象",title_en:"Missing invariance object",text_zh:"没有明确测试只改 split/clone/regroup、semantic support 不变时 controller 是否应保持不变。",text_en:"No explicit test of invariance when only package representation changes."},
{id:"G2",title_zh:"缺少可修复性的精确边界",title_en:"No exact removability boundary",text_zh:"观察到 effect 后还要区分：调权重能修，还是 support geometry 决定的不可均衡。",text_en:"Need to distinguish removable weighting effects from structurally non-equalizable geometry."},
{id:"G3",title_zh:"需要行为后果",title_en:"Need behavioral consequence",text_zh:"纯 certificate 不能说明真实 Agent 会不会因此改变检索、mediator 或行为。",text_en:"A certificate alone does not show a real behavioral consequence."}
],
motivation:{zh:"因此方法必须同时做到：冻结 semantic support、只操纵 package representation；用 R*(A) 给出 exact equalizability boundary；再用独立行为 witness 验证 representation change 是否沿 retrieval/mediator 传到行为。",en:"The method freezes semantic support while changing package representation, gives an exact R*(A) equalizability boundary, and tests a bounded representation→retrieval/mediator→behavior witness."},
components:[
{name:"Frozen support matrix A",solves:"G1",role_zh:"把‘能力变了’这个替代解释锁死，只改 package identity。",role_en:"Freezes capability so only package identity changes."},
{name:"R*(A) exact certificate",solves:"G2",role_zh:"给出 package-only nonnegative additive exposure 是否可精确均衡的 iff 边界。",role_en:"Gives the iff boundary for package-only additive exposure equalizability."},
{name:"Positive / negative geometry witnesses",solves:"G2",role_zh:"同时展示 R*>1 和高-overlap 但 R*=1，排除‘overlap 多就一定失真’。",role_en:"Uses positive and negative regimes to reject raw overlap prevalence."},
{name:"P19 behavior + mediator add-back",solves:"G3",role_zh:"检查 representation→retrieval/mediator→behavior，不把 certificate 直接外推成 utility。",role_en:"Tests a bounded behavior chain without overclaiming utility."}
],
experiments:[
{rq:"RQ1",q_zh:"同样 semantic support，换 package 表示会不会改变控制？",q_en:"Does repackaging change control under fixed semantic support?",baseline_zh:"原表示 / split / clone / regroup，support 相同。",baseline_en:"Original versus split/clone/regroup with identical support.",answer_zh:"会；存在 representation-sensitive regime。",answer_en:"Yes, in identified representation-sensitive regimes."},
{rq:"RQ2",q_zh:"是 overlap 多造成，还是 support geometry 真不可均衡？",q_en:"Is the effect overlap prevalence or non-equalizable geometry?",baseline_zh:"高 overlap 但 R*=1 的 logical-compiler / Level-3 negative regimes。",baseline_en:"High-overlap but R*=1 negative regimes.",answer_zh:"R*(A) 与可/不可均衡 geometry 对齐，而不是简单 overlap 计数。",answer_en:"R*(A) tracks equalizability geometry rather than overlap count."},
{rq:"RQ3",q_zh:"真实 Agent 行为里 effect 是否传下去？",q_en:"Does the effect propagate to behavior?",baseline_zh:"split-4、placebo/control、matched cleanup。",baseline_en:"Split-4, placebo/control, and matched cleanup.",answer_zh:"P19 原始表示 6/6 destructive signature，split-4 为 0/6；post-checkout add-back 3/3，matched cleanup 0/3。",answer_en:"P19 is 6/6 under the original representation versus 0/6 after split-4; add-back is 3/3 versus 0/3 matched cleanup."}
],
why_better:{zh:"比 overall-performance 比较更强，因为 semantic support 被固定；比 decomposition study 更强，因为 treatment 只有 package representation；比普通 balancing 更强，因为 R*(A) 告诉你什么时候 package-only 修复结构上不可能。",en:"It fixes semantic support, isolates package representation as the treatment, and identifies when package-only repair is structurally impossible."},
component_evidence:[
{component:"R*(A)",evidence_zh:"正/负 support geometry 与 certificate 对齐。",evidence_en:"Positive/negative geometries align with the certificate.",meaning_zh:"关键是 support geometry，不是 overlap prevalence。",meaning_en:"Support geometry is the key object."},
{component:"split-4",evidence_zh:"6/6 → 0/6 destructive signature。",evidence_en:"6/6 → 0/6 destructive signature.",meaning_zh:"表示方式可以改变实际行为链。",meaning_en:"Representation can alter the executed behavior chain."},
{component:"mediator add-back",evidence_zh:"3/3 vs matched cleanup 0/3。",evidence_en:"3/3 versus matched cleanup 0/3.",meaning_zh:"恢复特定 mediator 才恢复现象，不是任意 cleanup。",meaning_en:"A specific mediator, not arbitrary cleanup, restores the effect."}
],
boundary:{zh:"论文应卖 representation-invariance property + exact audit certificate + bounded behavior witness；不是新 LP 算法，也不是一般 downstream utility theorem。",en:"Sell the invariance property, exact audit certificate, and bounded behavioral witness—not a novel LP solver or general utility theorem."},
outline:["场景：skill package 是实现细节却可能改变 evolution","现有 routing/decomposition 为什么没有 invariance guarantee","定义 representation invariance 与 frozen support matrix","R*(A) certificate 与 exact boundary","support-geometry positive/negative tests","P19 behavioral witness 与 mediator controls","scope：package-only controller / no general utility claim"]
};