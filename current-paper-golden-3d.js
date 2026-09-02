window.CURRENT_PAPER_GOLDEN_SPECS=window.CURRENT_PAPER_GOLDEN_SPECS||{};
window.CURRENT_PAPER_GOLDEN_SPECS["paper-3d"]={
 scenario:{title:{zh:"为什么语言生成 3D 房间时，‘4 条关系怎么连’可能比‘一共有 4 条关系’更重要？",en:"Why can relational topology matter more than relation count in 3D generation?"},lead:{zh:"想象模型要按一句话摆家具。四条要求如果彼此独立，可以各自处理；如果后一条一直依赖前一件家具，前面一个小错误就会一路传下去。所以只数‘有几条关系’会把真正的结构难度藏起来。",en:"Spatial instructions naturally create hubs, chains, and shared-object dependencies."},reasons:[
  {t:{zh:"很多要求围绕同一个家具",en:"Relations share objects"},d:{zh:"例如‘沙发在桌子左边、灯在桌子后面、椅子朝向桌子’，三条要求都要先把桌子的位置搞对。",en:"Many constraints revolve around one hub object."}},
  {t:{zh:"有些要求必须按顺序满足",en:"Some relations are sequential"},d:{zh:"如果‘灯在桌子左边’，而‘椅子又在灯后面’，椅子的位置天然依赖前两步。",en:"Later placements depend on earlier ones."}},
  {t:{zh:"关系数量相同，不代表难度相同",en:"Same count is not same complexity"},d:{zh:"4 条互不相关的要求可以分开解决；4 条链式要求却会让前一步误差影响后面多步。",en:"Independent relations and chains have different computational structure."}},
  {t:{zh:"模型出错还可能发生在三个完全不同的步骤",en:"Generation has multiple stages"},d:{zh:"第一步可能没读懂‘谁在谁左边’；第二步可能把关系结构记错；第三步也可能理解都对了，但真正摆家具时没摆对。",en:"Failure can arise in language, structure, or layout."}}
 ],why:{zh:"所以这篇论文真正想回答两件事：关系怎么连接会不会让任务更难；如果更难，问题到底出在‘没读懂关系’‘关系结构记错’还是‘家具没摆对’。",en:"A count curve neither identifies the mechanism nor tells designers which stage to fix."}},
 worked:{title:{zh:"一个具体例子：同样 4 条关系，Independent 和 Chain 为什么不是同一道题？",en:"Worked example: four independent relations vs a four-link chain"},lead:{zh:"教学示例，不是当前 scientific outcome。",en:"Teaching example; no scientific outcome is claimed."},steps:[
  {k:"01",t:"Independent",d:{zh:"床靠左墙；灯在窗边；椅子朝门；柜子在右墙。四条关系几乎互不依赖。",en:"Four mostly independent placement relations."}},
  {k:"02",t:"Chain",d:{zh:"桌子在沙发前；灯在桌子左；椅子在灯后；柜子在椅子右。后一条不断依赖前一对象位置。",en:"Each relation depends on the previous object."}},
  {k:"03",t:{zh:"关系数完全一样",en:"Same relation count"},d:{zh:"两边都是 4 条，所以简单 count 指标认为它们同难度。",en:"Both contain four relations."}},
  {k:"04",t:{zh:"结构负担不同",en:"Different structural burden"},d:{zh:"Chain 中前面一步的位置误差会改变后面多个约束的可满足空间。",en:"Early errors propagate through later constraints."}}
 ],compare:[
  {a:"4 Independent",b:{zh:"低共享 / 可并行",en:"Low sharing / parallel"},d:{zh:"关系之间互相牵制较少。",en:"Less cross-relation dependency."}},
  {a:"4 Chain",b:{zh:"高依赖 / 误差传播",en:"Dependent / error propagation"},d:{zh:"同 count 下可能显著更难。",en:"Can be harder at the same count."}}
 ],note:{zh:"⑨真正实验会固定 base scene、object universe、relation count、room type、asset vocabulary 和 seed，再只改变 topology。",en:"The decisive experiment holds scene/count/assets/seed fixed and changes topology only."}},
 spotlight:{title:"M3DLayout: A Multi-Source Dataset of 3D Indoor Layouts and Structured Descriptions for 3D Generation",problem:{zh:"3D 室内生成长期缺少同时覆盖布局、结构描述和多来源场景的大规模统一数据。",en:"3D layout generation needs richer structured multi-source data."},added:{zh:"M3DLayout 在 CVPR 2026 提供更丰富的室内布局与结构化描述，是最新正式 3D layout 数据近邻。",en:"M3DLayout provides multi-source indoor layouts with structured descriptions."},method:{zh:"它主要解决‘给模型更多、更结构化的 3D 房间数据’这个问题。",en:"Its contribution is broader structured data."},bridge:{zh:"⑨ 不和它竞争新数据集。我们反而把同一个房间和同样数量的关系固定住，只换‘这些关系怎么连接’，然后逐步检查：模型是没读懂、没把关系结构记对，还是最后没把家具摆对。",en:"The 3D paper isolates topology and stage bottlenecks on matched scenes."}},
 architecture:{lead:{zh:"这四层不是四个并列数据集。可以把整套实验理解成：3D-FRONT 给我们‘房间真值’，3D-FUTURE 给家具模型，InstructScene 负责‘读文字→整理关系→摆家具’，我们的实验只在最后这条流程上做受控比较。",en:"The stack separates scene data, assets, model pipeline, and matched intervention."},layers:[
  {k:"A",t:"3D-FRONT",d:{zh:"提供已经摆好的完整房间：房型、有哪些家具、每件家具在哪里。它是场景真值。",en:"Indoor scene/layout data."}},
  {k:"B",t:"3D-FUTURE",d:{zh:"提供一件件可放进房间里的 3D 家具模型。家具数量是资产规模，不是实验样本数。",en:"Furniture CAD asset lineage."}},
  {k:"C",t:"InstructScene",d:{zh:"它像一条三步流水线：①读懂文字里的空间关系 → ②整理成关系结构图 → ③真正生成家具布局。",en:"Text→semantic graph→3D layout carrier."}},
  {k:"D",t:{zh:"我们的受控实验",en:"Topology × Stage"},d:{zh:"先固定同一房间、同样 4 条关系，只换‘独立/链式/围绕中心物体/共享物体’；如果性能不同，再分别给第 1、2、3 步补标准信息，看在哪一步最能恢复。",en:"Matched topology treatment plus stage-localized interventions."}}
 ]},
 arc:[
  {k:"A",t:{zh:"最初只看‘关系越多会不会越难’",en:"Old count story"},q:{zh:"把关系从 2 条加到 4 条、6 条，性能是不是下降？",en:"Are more relations harder?"},found:{zh:"很容易看到一条下降曲线，但关系多的时候指令也更长、场景往往也更难。",en:"A count curve is easy to observe but confounded."},meaning:{zh:"所以这条曲线只能说明‘复杂样本更难’，不能告诉我们为什么。",en:"Not mechanistic."}},
  {k:"B",t:{zh:"发现这个旧故事已经被最近工作覆盖",en:"SceneNAT collision"},q:{zh:"‘关系越多越难’还够不够当新论文的核心？",en:"Is the count story still novel?"},found:{zh:"SceneNAT 等最近工作已经直接研究关系数量和超出训练范围后的稳健性。",en:"Recent work covers count robustness."},meaning:{zh:"所以我们主动放弃旧故事，不再包装一个已经有人做过的结论。",en:"The old story is abandoned."}},
  {k:"C",t:{zh:"把新问题改成：同样 4 条关系，只换连接方式",en:"Matched topology"},q:{zh:"彼此独立、链式依赖、围绕同一中心物体、共享同一物体，这几种情况会不会真的不同？",en:"Does topology matter at fixed count?"},found:{zh:"目前还在把官方模型、资产和匹配场景准备到可公平测试的状态，没有读取科学结果。",en:"Qualification precedes outcomes."},meaning:{zh:"这一步让‘关系怎么连接’成为真正唯一改变的条件。",en:"Makes topology the treatment."}},
  {k:"D",t:{zh:"如果真的不同，再问错误发生在哪一步",en:"Stage localization"},q:{zh:"模型是第一步没读懂关系、第二步把关系结构记错，还是第三步真正摆家具时出错？",en:"If there is an effect, where does it arise?"},found:{zh:"计划分别给三步补标准答案，看补哪一步时关系满足率恢复得最多。",en:"Future stage-specific information interventions."},meaning:{zh:"只有同时看到‘连接方式确实造成差异’和‘某一步补信息后能解释性恢复’，才升级机制结论。",en:"Mechanism requires both a topology residual and stage-localized recovery."}}
 ]
};
