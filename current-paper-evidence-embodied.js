window.CURRENT_PAPER_EVIDENCE_PROFILES=window.CURRENT_PAPER_EVIDENCE_PROFILES||{};
Object.assign(window.CURRENT_PAPER_EVIDENCE_PROFILES,{
"paper-a":{
 featured:[
  {title:"Global Prior Meets Local Consistency: Dual-Memory Augmented VLA (OptimusVLA)",venue:"CVPR",year:2026,url:"https://openaccess.thecvf.com/content/CVPR2026/html/Li_Global_Prior_Meets_Local_Consistency_Dual-Memory_Augmented_Vision-Language-Action_Model_for_CVPR_2026_paper.html",relation:{zh:"CVPR 2026 直接把 dual memory 引入 VLA，在 LIBERO/CALVIN/RoboTwin 与真实机器人上验证。",en:"CVPR 2026 directly augments VLAs with dual memory across LIBERO, CALVIN, RoboTwin, and real robots."},boundary:{zh:"它证明 memory architecture 能提高控制；Paper A 不提新 memory architecture，而问 action shift 何时才算忠实使用具体 source memory。",en:"It shows memory architecture can improve control; Paper A audits when action shift qualifies as faithful use of a specific source memory."}},
  {title:"Affordance Field Intervention: Enabling VLAs to Escape Memory Traps",venue:"CVPR",year:2026,url:"https://openaccess.thecvf.com/content/CVPR2026/html/Xu_Affordance_Field_Intervention_Enabling_VLAs_to_Escape_Memory_Traps_in_CVPR_2026_paper.html",relation:{zh:"CVPR 2026 明确提出 VLA memory trap，并在 π0/π0.5 与 LIBERO-Pro 上做 intervention。",en:"CVPR 2026 explicitly identifies VLA memory traps and intervenes on π0/π0.5 and LIBERO-Pro."},boundary:{zh:"AFI 解决 OOD memory trap；Paper A 的对象是跨方法 measurement：retrieval ≠ influence，influence ≠ source fidelity。",en:"AFI repairs an OOD memory trap; Paper A contributes method-agnostic measurement."}},
  {title:"Mem2ActBench: A Benchmark for Evaluating Long-Term Memory Utilization in Task-Oriented Autonomous Agents",venue:"ACL",year:2026,url:"https://aclanthology.org/2026.acl-long.370/",relation:{zh:"ACL 2026 主会把 memory 从被动 retrieval 推进到 action-level utilization evaluation。",en:"ACL 2026 moves memory evaluation from passive retrieval to action-level utilization."},boundary:{zh:"Mem2ActBench 扩 task coverage；Paper A 更细分 same-state causal influence、wrong-memory/placebo 与 source-alignment。",en:"Mem2ActBench broadens task coverage; Paper A separates causal influence, wrong-memory/placebo, and source alignment."}}
 ],
 experiment:{
  intro:{zh:"Paper A 的载体是 MemoryVLA，但数据来源是正式 CVPR 2026 的 LIBERO-Plus robustness benchmark lineage；我们不照搬 benchmark 总分，而只取 task0–2 做 same-state memory counterfactual，再逐步加 wrong-memory / placebo / source-alignment。",en:"Paper A uses MemoryVLA as carrier and the CVPR 2026 LIBERO-Plus robustness lineage as substrate, turning task0–2 into same-state memory counterfactuals."},
  sources:[
   {name:"LIBERO-Plus",paper:"LIBERO-Plus: A Progressive Robustness Benchmark for Visual-Language-Action Models",venue:"CVPR",year:2026,url:"https://openaccess.thecvf.com/content/CVPR2026/html/Fei_LIBERO-Plus_A_Progressive_Robustness_Benchmark_for_Visual-Language-Action_Models_CVPR_2026_paper.html",original:{zh:"正式 CVPR 2026 benchmark，在 LIBERO 上扩展 7 类 controlled perturbation，并系统评估 10 个 SOTA model。",en:"A CVPR 2026 benchmark extending LIBERO with seven controlled perturbation dimensions and evaluating ten SOTA models."},slice:{zh:"Paper A development 只取 task0–2；重点使用 Camera / Robot / Noise / Layout 等可控扰动。",en:"Paper A development uses task0–2, focusing on Camera/Robot/Noise/Layout perturbations."},transform:{zh:"把 robustness task 转成同一 observation/state 下的 memory-off / correct / wrong / placebo counterfactual。",en:"Transforms robustness tasks into memory-off/correct/wrong/placebo counterfactuals at the same state."}},
   {name:"LIBERO",paper:"LIBERO: Benchmarking Knowledge Transfer for Lifelong Robot Learning",venue:"NeurIPS D&B",year:2023,url:"https://proceedings.neurips.cc/paper_files/paper/2023/hash/8c3c666820ea055a77726d66fc7d447f-Abstract-Datasets_and_Benchmarks.html",original:{zh:"原 benchmark 有 4 个 task suite、共 130 个 robot manipulation tasks，并提供 demonstrations。",en:"The original benchmark has four task suites and 130 robot-manipulation tasks with demonstrations."},slice:{zh:"作为 LIBERO-Plus 基础 task lineage；Paper A 不把 130 tasks 全部当当前 n。",en:"Serves as the base-task lineage for LIBERO-Plus; all 130 tasks are not current n."},transform:{zh:"先在受控 task0–2 上资格化 measurement contract，再冻结第二 VLA / 更大 panel。",en:"Qualify the measurement contract on task0–2 before freezing a second VLA/larger panel."}}
  ],
  models:[
   {name:"MemoryVLA",role:{zh:"当前 primary VLA / native memory channel。",en:"Current primary VLA / native memory channel."},status:{zh:"carrier; not contribution",en:"carrier; not contribution"}},
   {name:"Second VLA / memory mechanism",role:{zh:"外部有效性。",en:"External validity."},status:{zh:"尚未冻结；不能按结果挑模型",en:"not frozen; cannot be outcome-selected"}}
  ],
  quantities:[
   {v:"4 suites / 130",k:{zh:"LIBERO 原始 suites / tasks",en:"original LIBERO suites / tasks"}},
   {v:"7",k:{zh:"LIBERO-Plus controlled perturbation dimensions",en:"LIBERO-Plus controlled perturbation dimensions"}},
   {v:"10",k:{zh:"LIBERO-Plus 原论文系统评测 models",en:"models systematically evaluated by LIBERO-Plus"}},
   {v:"task0–2",k:{zh:"Paper A 当前 development task slice",en:"Paper A current development task slice"}},
   {v:"||Δa||₂ ≈ .5541",k:{zh:"same-state memory influence qualification",en:"same-state memory influence qualification"}}
  ],
  unit:{zh:"核心单位是同一 observation/state 的 counterfactual action comparison，不是不同 episode 间的原始成功率差。",en:"The core unit is a counterfactual action comparison at the same observation/state."},
  treatment:{zh:"memory surface 从 off → correct / wrong / placebo；model、state、接口、token budget 尽量固定。",en:"The memory surface changes from off to correct/wrong/placebo while model, state, interface, and token budget stay fixed."},
  readouts:["interface integrity","same-state action influence","content specificity","source-direction fidelity","corridor / rejoin","terminal task consequence"]
 }
},
"paper-b":{
 featured:[
  {title:"Global Prior Meets Local Consistency: Dual-Memory Augmented VLA (OptimusVLA)",venue:"CVPR",year:2026,url:"https://openaccess.thecvf.com/content/CVPR2026/html/Li_Global_Prior_Meets_Local_Consistency_Dual-Memory_Augmented_Vision-Language-Action_Model_for_CVPR_2026_paper.html",relation:{zh:"最新 CVPR 主会 VLA memory 方法，证明历史 trajectory/memory 可以直接进入当前 control。",en:"A recent CVPR VLA-memory method showing historical memory can condition current control."},boundary:{zh:"它主要优化 memory-conditioned action generation；Paper B 的硬门是跨 episode admission → verify → commit → future reuse。",en:"It optimizes memory-conditioned action generation; Paper B requires cross-episode admission → verification → commitment → future reuse."}},
  {title:"Affordance Field Intervention: Enabling VLAs to Escape Memory Traps",venue:"CVPR",year:2026,url:"https://openaccess.thecvf.com/content/CVPR2026/html/Xu_Affordance_Field_Intervention_Enabling_VLAs_to_Escape_Memory_Traps_in_CVPR_2026_paper.html",relation:{zh:"CVPR 2026 显示 VLA 对记忆/轨迹先验可能产生 memory trap，并通过 affordance intervention 恢复。",en:"CVPR 2026 shows VLAs can fall into memory traps and recover through affordance intervention."},boundary:{zh:"AFI 是当前 episode repair；Paper B 继续追问 repair experience 是否有资格成为持久 state 并在未来再利用。",en:"AFI repairs the current episode; Paper B asks whether a repair experience deserves persistence and later reuse."}},
  {title:"Agentic Memory: Learning Unified Long-Term and Short-Term Memory Management for Large Language Model Agents",venue:"ACL",year:2026,url:"https://aclanthology.org/2026.acl-long.981/",relation:{zh:"ACL 2026 主会将 LTM/STM 操作直接纳入 policy，是主动管理 persistent memory 的强近邻。",en:"ACL 2026 integrates LTM/STM operations into the policy, a strong active-memory-management neighbor."},boundary:{zh:"AgeMem 学习何时存取删改；Paper B 更强调 write authority 必须绑定独立 effect verification 与 future re-exposure。",en:"AgeMem learns when to manage memory; Paper B ties write authority to effect verification and future re-exposure."}}
 ],
 experiment:{
  intro:{zh:"Paper B 和 Paper A 共用 LIBERO-Plus / MemoryVLA development substrate，但科学对象不同：A 测“有没有忠实使用”，B 测“这次 experience 有没有资格被永久写入并在未来复用”。",en:"Paper B shares the LIBERO-Plus / MemoryVLA substrate with Paper A but asks whether an experience deserves permanent commitment and future reuse."},
  sources:[
   {name:"LIBERO-Plus",paper:"LIBERO-Plus: A Progressive Robustness Benchmark for Visual-Language-Action Models",venue:"CVPR",year:2026,url:"https://openaccess.thecvf.com/content/CVPR2026/html/Fei_LIBERO-Plus_A_Progressive_Robustness_Benchmark_for_Visual-Language-Action_Models_CVPR_2026_paper.html",original:{zh:"7 类 perturbation；原论文系统评测 10 个 VLA model。",en:"Seven perturbation dimensions; the paper systematically evaluates ten VLA models."},slice:{zh:"task0–2 × Camera/Robot/Noise/Layout × 两档 = 24 development scopes；task3–9 保留。",en:"task0–2 × Camera/Robot/Noise/Layout × two levels = 24 development scopes; task3–9 remain reserved."},transform:{zh:"每个 scope 拆 retrieval、action influence、repair、rejoin、terminal success 与 write-back eligibility。",en:"Each scope separates retrieval, action influence, repair, rejoin, terminal success, and write-back eligibility."}},
   {name:"LIBERO",paper:"LIBERO: Benchmarking Knowledge Transfer for Lifelong Robot Learning",venue:"NeurIPS D&B",year:2023,url:"https://proceedings.neurips.cc/paper_files/paper/2023/hash/8c3c666820ea055a77726d66fc7d447f-Abstract-Datasets_and_Benchmarks.html",original:{zh:"4 suites、130 tasks 的 lifelong robot manipulation benchmark。",en:"A lifelong robot-manipulation benchmark with four suites and 130 tasks."},slice:{zh:"作为 LIBERO-Plus 基础 task lineage，不把全部 130 tasks 当当前 longitudinal n。",en:"Provides the base-task lineage for LIBERO-Plus; all 130 tasks are not current longitudinal n."},transform:{zh:"当前只在 development slice 上冻结 slow-loop admission/verification/commit 规则。",en:"Slow-loop rules are currently frozen only on the development slice."}},
   {name:"Longitudinal episode stream",paper:"Project-constructed future re-exposure panel",venue:"Project construct",year:2026,url:"",original:{zh:"不是现成公开 benchmark；source episode 与未来相关 state 必须成对冻结。",en:"Not an off-the-shelf public benchmark; source episodes and future related states must be frozen as pairs."},slice:{zh:"future confirmatory 只在 preregistered source/future pairs 上测试 write → reuse → benefit。",en:"Future confirmatory uses preregistered source/future pairs for write → reuse → benefit."},transform:{zh:"candidate memory 先 provisional，经 effect verification 后才 commit。",en:"Candidate memory remains provisional until effect verification authorizes commitment."}}
  ],
  models:[
   {name:"MemoryVLA",role:{zh:"primary memory-conditioned control backbone。",en:"Primary memory-conditioned-control backbone."},status:{zh:"carrier",en:"carrier"}},
   {name:"Frozen base VLA",role:{zh:"no-update / retrieval-disabled control。",en:"No-update / retrieval-disabled control."},status:{zh:"control",en:"control"}}
  ],
  quantities:[
   {v:"task0–2",k:{zh:"development tasks",en:"development tasks"}},
   {v:"4 × 2",k:{zh:"Camera/Robot/Noise/Layout × two levels",en:"Camera/Robot/Noise/Layout × two levels"}},
   {v:"24",k:{zh:"development robustness scopes",en:"development robustness scopes"}},
   {v:"task3–9",k:{zh:"reserved tasks; not used for development tuning",en:"reserved tasks; not used for development tuning"}},
   {v:"write → reuse → benefit",k:{zh:"future confirmatory longitudinal unit",en:"future confirmatory longitudinal unit"}}
  ],
  unit:{zh:"真正 longitudinal unit 是 source episode → update → future related episode；单步 action 或单 episode 不是 self-evolution unit。",en:"The true longitudinal unit is source episode → update → future related episode."},
  treatment:{zh:"no-update / retrieval-only / provisional / certified 分离当前 context effect、memory availability 与 verified commitment。",en:"No-update/retrieval-only/provisional/certified separate context effects, memory availability, and verified commitment."},
  readouts:["action influence","target repair","collateral effect","sustained rejoin","terminal success","future retrieval / reuse / benefit"]
 }
}
});
