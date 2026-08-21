window.IDEA_PIPELINE_META = {
  architectureVersion:"2.1-evidence-gated",
  generatedFrom:"69-formulation audit + structured direction literature",
  selectedIdea:"GroundEvo-Admission",
  advisorShortlist:[
    "GroundEvo-Admission",
    "ScopeGuard-V",
    "NegEvoBench-V",
    "RelianceGuard-V",
    "ViMEvo-Repair",
    "EvoContract-V",
    "SkillProof-V",
    "ExploreRepair-V",
    "EgoShift",
    "WorldPatch-V",
    "MemoryFormRouter-V",
    "ProcessCredit-V"
  ],
  funnel:[
    {key:"formulations",count:69,label:{en:"Candidate formulations",zh:"候选表述"},desc:{en:"High-recall formulations before collision and identifiability checks.",zh:"在文献碰撞与可识别性检查前保留高召回候选。"}},
    {key:"retained",count:34,label:{en:"Structurally complete ideas",zh:"结构完整 Idea"},desc:{en:"Every idea has a problem, mechanism, rationale, experiment, and Stop rule.",zh:"每个 Idea 都具备问题、机制、依据、实验与停止条件。"}},
    {key:"shortlist",count:12,label:{en:"Advisor shortlist",zh:"导师短名单"},desc:{en:"Candidates displayed first for expert judgment; this is not automatic acceptance.",zh:"优先进入人工判断，并不代表自动通过。"}},
    {key:"selected",count:1,label:{en:"Selected for falsification",zh:"已进入证伪实验"},desc:{en:"The current project has a bounded pilot and explicit claim boundary.",zh:"当前项目已具有有界 Pilot 与明确主张边界。"}}
  ],
  stages:{
    selected:{label:{en:"Selected",zh:"已选中"},tone:"advance"},
    "collision-check":{label:{en:"Novelty check",zh:"新颖性核验"},tone:"investigate"},
    review:{label:{en:"Reviewer check",zh:"评审核验"},tone:"review"},
    archived:{label:{en:"Hold / archive",zh:"暂缓／归档"},tone:"hold"}
  },
  operators:[
    {key:"limitation-inversion",name:{en:"Limitation inversion",zh:"限制反转"},question:{en:"Which repeated limitation should become the paper's primary target?",zh:"哪个反复出现的限制应被反转为论文主问题？"}},
    {key:"assumption-removal",name:{en:"Assumption removal",zh:"假设移除"},question:{en:"Which unrealistic supervision or observability assumption can be removed?",zh:"可以移除哪个不现实的监督或可观测性假设？"}},
    {key:"objective-evaluation-mismatch",name:{en:"Objective–evaluation mismatch",zh:"目标—评测错位"},question:{en:"Does the optimized surrogate actually establish the claimed behavior?",zh:"当前优化代理目标是否真的能证明目标行为？"}},
    {key:"pme-recombination",name:{en:"Purpose–mechanism–evaluation",zh:"问题—机制—评测重组"},question:{en:"Can a verified mechanism solve a structurally similar visual problem?",zh:"已验证机制能否解决结构相似的视觉问题？"}},
    {key:"contradiction-resolution",name:{en:"Contradiction resolution",zh:"矛盾消解"},question:{en:"Which hidden variable explains conflicting results across papers?",zh:"哪个隐藏变量解释了论文之间的冲突结论？"}},
    {key:"missing-cell",name:{en:"Missing-cell completion",zh:"空白单元补全"},question:{en:"Which important task × mechanism × evidence cell is empty?",zh:"任务×机制×证据矩阵中哪个重要单元仍为空？"}},
    {key:"cross-domain-analogy",name:{en:"Cross-domain analogy",zh:"跨领域结构类比"},question:{en:"Which mechanism transfers because the causal structure is shared?",zh:"哪个机制因共享因果结构而可跨领域迁移？"}},
    {key:"metric-replacement",name:{en:"Metric replacement",zh:"指标替换"},question:{en:"Which convenient metric hides the failure the paper should expose?",zh:"哪个方便指标掩盖了论文真正应暴露的失败？"}}
  ],
  reviewers:[
    {key:"novelty",name:{en:"Novelty / collision",zh:"新颖性／碰撞"},question:{en:"Is the same problem–mechanism combination already published?",zh:"相同问题—机制组合是否已经发表？"}},
    {key:"scientific",name:{en:"Scientific validity",zh:"科学成立性"},question:{en:"Is the observation–failure–mechanism chain identifiable?",zh:"观察—失败—机制链是否可识别？"}},
    {key:"experiment",name:{en:"Main-table evidence",zh:"主表证据"},question:{en:"Can one normal-setting experiment prove the core claim?",zh:"一项正常设置实验能否证明核心主张？"}},
    {key:"feasibility",name:{en:"Pilot feasibility",zh:"Pilot 可行性"},question:{en:"Can the phenomenon be tested before building the full method?",zh:"能否在开发完整方法前先验证现象？"}},
    {key:"venue",name:{en:"CVPR fit",zh:"CVPR 契合"},question:{en:"Is visual information indispensable rather than replaceable?",zh:"视觉信息是否不可替代，而不是可替换测试域？"}}
  ],
  warnings:[
    {en:"Decimal legacy scores are shown only in the archive. The advisor board uses evidence gates and decision stages.",zh:"旧小数分数仅在归档中保留；导师决策板采用证据门槛与阶段。"},
    {en:"Direction-level neighboring papers do not establish idea-level novelty. Exact collision checks remain mandatory.",zh:"方向级近邻论文不能证明 Idea 级新颖性；仍必须做精确碰撞检索。"}
  ]
};
