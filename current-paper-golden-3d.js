window.CURRENT_PAPER_GOLDEN_SPECS=window.CURRENT_PAPER_GOLDEN_SPECS||{};
window.CURRENT_PAPER_GOLDEN_SPECS["paper-3d"]={
 scenario:{title:{zh:"为什么语言生成 3D 场景时，关系‘怎么连’会比关系‘有几条’更重要？",en:"Why can relational topology matter more than relation count in 3D generation?"},lead:{zh:"真实空间指令往往围绕同一个物体形成 hub、前后依赖形成 chain，或者共享对象形成耦合。即使关系数量相同，模型需要维护的依赖结构完全不同，所以只数 relation count 很容易把真正难点藏起来。",en:"Spatial instructions naturally create hubs, chains, and shared-object dependencies."},reasons:[
  {t:{zh:"用户指令天然共享对象",en:"Relations share objects"},d:{zh:"‘沙发在桌子左边、灯在桌子后面、椅子朝向桌子’都围绕同一个 hub。",en:"Many constraints revolve around one hub object."}},
  {t:{zh:"有些关系有顺序依赖",en:"Some relations are sequential"},d:{zh:"后一件家具的位置必须等前一件确定，形成 dependency chain。",en:"Later placements depend on earlier ones."}},
  {t:{zh:"同 count 不等于同计算难度",en:"Same count is not same complexity"},d:{zh:"4 条独立关系可以并行满足，4 条 chain 关系却会把误差逐层传播。",en:"Independent relations and chains have different computational structure."}},
  {t:{zh:"生成系统本身又有多个 stage",en:"Generation has multiple stages"},d:{zh:"失败可能来自语言解析、semantic graph，也可能来自最终 layout decoding。",en:"Failure can arise in language, structure, or layout."}}
 ],why:{zh:"如果只报告‘关系越多性能越低’，既解释不了失败原因，也无法告诉模型设计者应该修语言理解、结构表示还是布局解码。⑨要把这两个问题分开。",en:"A count curve neither identifies the mechanism nor tells designers which stage to fix."}},
 worked:{title:{zh:"一个具体例子：同样 4 条关系，Independent 和 Chain 为什么不是同一道题？",en:"Worked example: four independent relations vs a four-link chain"},lead:{zh:"教学示例，不是当前 scientific outcome。",en:"Teaching example; no scientific outcome is claimed."},steps:[
  {k:"01",t:"Independent",d:{zh:"床靠左墙；灯在窗边；椅子朝门；柜子在右墙。四条关系几乎互不依赖。",en:"Four mostly independent placement relations."}},
  {k:"02",t:"Chain",d:{zh:"桌子在沙发前；灯在桌子左；椅子在灯后；柜子在椅子右。后一条不断依赖前一对象位置。",en:"Each relation depends on the previous object."}},
  {k:"03",t:{zh:"关系数完全一样",en:"Same relation count"},d:{zh:"两边都是 4 条，所以简单 count 指标认为它们同难度。",en:"Both contain four relations."}},
  {k:"04",t:{zh:"结构负担不同",en:"Different structural burden"},d:{zh:"Chain 中前面一步的位置误差会改变后面多个约束的可满足空间。",en:"Early errors propagate through later constraints."}}
 ],compare:[
  {a:"4 Independent",b:{zh:"低共享 / 可并行",en:"Low sharing / parallel"},d:{zh:"关系之间互相牵制较少。",en:"Less cross-relation dependency."}},
  {a:"4 Chain",b:{zh:"高依赖 / 误差传播",en:"Dependent / error propagation"},d:{zh:"同 count 下可能显著更难。",en:"Can be harder at the same count."}}
 ],note:{zh:"⑨真正实验会固定 base scene、object universe、relation count、room type、asset vocabulary 和 seed，再只改变 topology。",en:"The decisive experiment holds scene/count/assets/seed fixed and changes topology only."}},
 spotlight:{title:"M3DLayout: A Multi-Source Dataset of 3D Indoor Layouts and Structured Descriptions for 3D Generation",problem:{zh:"3D 室内生成长期缺少同时覆盖布局、结构描述和多来源场景的大规模统一数据。",en:"3D layout generation needs richer structured multi-source data."},added:{zh:"M3DLayout 在 CVPR 2026 提供更丰富的室内布局与结构化描述，是最新正式 3D layout 数据近邻。",en:"M3DLayout provides multi-source indoor layouts with structured descriptions."},method:{zh:"它主要扩数据与 structured description 覆盖，帮助模型学习更丰富场景。",en:"Its contribution is broader structured data."},bridge:{zh:"⑨ 不和它竞争新数据集。⑨ 固定同一 scene/data 后，只改变关系 topology，并进一步用 stage intervention 定位失败发生在 language、graph 还是 layout。",en:"The 3D paper isolates topology and stage bottlenecks on matched scenes."}},
 architecture:{lead:{zh:"⑨ 的四个对象分别扮演‘场景数据、家具资产、text→graph→layout 模型、我们的 matched intervention’四种角色。",en:"The stack separates scene data, assets, model pipeline, and matched intervention."},layers:[
  {k:"A",t:"3D-FRONT",d:{zh:"完整室内房间、家具类别与布局的 scene ground truth。",en:"Indoor scene/layout data."}},
  {k:"B",t:"3D-FUTURE",d:{zh:"家具 CAD 资产库；资产数量不是实验 n。",en:"Furniture CAD asset lineage."}},
  {k:"C",t:"InstructScene",d:{zh:"把文本关系要求转 semantic graph，再生成 3D layout 的官方方法/任务载体。",en:"Text→semantic graph→3D layout carrier."}},
  {k:"D",t:"Topology × Stage",d:{zh:"我们的 matched treatment：固定 count/scene，只改 independent/chain/hub/shared-object，并做 stage-localized oracle。",en:"Matched topology treatment plus stage-localized interventions."}}
 ]},
 arc:[
  {k:"A",t:{zh:"旧 count story",en:"Old count story"},q:{zh:"关系越多是否越难？",en:"Are more relations harder?"},found:{zh:"容易看到 capacity curve，但 count 与长度/难度混杂。",en:"A count curve is easy to observe but confounded."},meaning:{zh:"不足以识别机制。",en:"Not mechanistic."}},
  {k:"B",t:"SceneNAT collision",q:{zh:"旧故事还有 novelty 吗？",en:"Is the count story still novel?"},found:{zh:"最近工作已经覆盖 relation-count 与 beyond-support robustness。",en:"Recent work covers count robustness."},meaning:{zh:"旧 scalar story 主动 STOP。",en:"The old story is abandoned."}},
  {k:"C",t:{zh:"matched topology",en:"Matched topology"},q:{zh:"固定 count 后 chain / hub / shared-object 还会不同吗？",en:"Does topology matter at fixed count?"},found:{zh:"construct / official stack 先完成 qualification；不提前读 outcome。",en:"Qualification precedes outcomes."},meaning:{zh:"把 topology 变成真正 treatment。",en:"Makes topology the treatment."}},
  {k:"D",t:{zh:"stage localization",en:"Stage localization"},q:{zh:"如果有 effect，失败在哪一层？",en:"If there is an effect, where does it arise?"},found:{zh:"未来分别补 language / graph / layout 信息看恢复。",en:"Future stage-specific information interventions."},meaning:{zh:"最终机制主张必须同时有 topology residual + 可解释 recovery。",en:"Mechanism requires both a topology residual and stage-localized recovery."}}
 ]
};
