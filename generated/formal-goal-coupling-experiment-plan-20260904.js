window.FORMAL_GOAL_COUPLING_EXPERIMENT_PLAN = {
  schema_version: "formal-goal-coupling-experiment-plan-v3.0",
  generated_at: "2026-09-04T11:13:00+08:00",
  as_of: "2026-09-04T11:12:17+08:00",
  object_id: "SUCC-C-BEHAVIOR2026-TWO-FAMILY-SHARED-MULTITASK-PANEL",
  parent_object: "SUCC-C-FORMAL-GOAL-COUPLING",
  display_name: {zh:"Formal Goal Coupling · BEHAVIOR 2026 两策略族配对面板",en:"Formal Goal Coupling · BEHAVIOR 2026 two-family matched panel"},
  status: "PI05_FORMAL_RUN2_FDLIMIT_RUNNING",
  phase: {zh:"π0.5 practical batch16 正式训练 run2",en:"π0.5 practical-batch16 formal training run2"},
  question: {
    zh:"在 goal 数量与主要逻辑结构精确匹配时，shared-argument goal coupling 更高的任务，官方 BEHAVIOR task Q 是否更低？",
    en:"With goal count and major logical structure exactly matched, is official BEHAVIOR task Q lower for the higher shared-argument goal-coupling member?"
  },
  thesis: {
    zh:"任务复杂度至少有两个维度：有多少目标，以及这些目标通过共享对象/变量耦合得有多紧。当前实验只检验配对关联，不声称 coupling 导致规划深度或执行顺序困难。",
    en:"Task complexity has at least two axes: how many goals there are and how tightly those goals are coupled through shared objects/variables. The current experiment tests a matched association only, not a causal planning-depth or execution-order claim."
  },
  construct: {
    nodes:"BDDL atomic goal-predicate occurrences",
    edges:"shared object / scope-resolved variable arguments",
    primary_metric:"shared_argument_edge_count",
    matched_on:["atomic_goal_count","branch_operator_count","goal_logic_depth","quantifier_count"]
  },
  panel: {
    tasks:26,
    matched_pairs:13,
    official_instances_per_task:10,
    families:["π0.5","GR00T N1.7"],
    frozen_task_indices:[8,10,12,13,14,17,33,41,42,46,51,56,59,62,65,67,68,73,74,77,81,84,85,88,89,94],
    selection_rule:{zh:"只用 formal structure 做 outcome-blind 选择；不换 pair、不换 task。",en:"Outcome-blind structural selection only; no pair or task replacement."}
  },
  data: {
    benchmark_revision:"b1979916ec1549b10a4e65e630bc6504a9af1b00",
    demo_revision:"4f50b44796641a4d526a19d9aeadc8aa51e2f2c2",
    episodes:5200,
    sealed_files:1380,
    sealed_bytes:236480375583,
    host231_seal_sha256:"0538097f09aae41f407f1a923cd1d6249366566a2592b38ad30dcbe40d5de8a3"
  },
  negative_control: {
    status:"CLOSED_NOT_SUPPORTED",
    label:{zh:"Human demo horizon 负控",en:"Human-demo horizon negative control"},
    result:{zh:"高 coupling 并没有让成功人类 demo 系统性更长；因此不能把 policy-Q 结果解释成“人类路径更长”的简单中介。",en:"Higher coupling did not make successful human demos systematically longer, so a later policy-Q association cannot be reduced to a simple longer-human-path mediator."},
    beta_edge:-0.009792957356752403,
    permutation_p:0.5342746572534275
  },
  pi05_training: {
    selected_recipe:{physical_batch:16,effective_optimizer_batch:16,gradient_accumulation:1,seed:42,optimizer_updates:50000,num_workers:0,action_horizon:32,terminal_checkpoint_label:49999},
    selection_reason:{zh:"预注册 practical ladder 16→8→4；batch16 第一项就通过完整 synthetic source train_step（forward/backward + AdamW + EMA），所以 8/4 永久不运行。",en:"The preregistered practical ladder was 16→8→4. Batch16, the first candidate, passed a complete synthetic source train_step (forward/backward + AdamW + EMA), so batch8/4 are never run."},
    source_batch64:{status:"INFEASIBLE_SINGLE_A100",note:{zh:"单 A100 80GB 能装 step-0 state，但真实 batch64 gradient OOM。",en:"A single A100-80GB can hold the step-0 state, but the real batch64 gradient OOMs."}},
    accumulation_ladder:[
      {micro:16,k:4,effective:64,status:"GPU_OOM_SECOND_MICRO",extra_allocation_bytes:17055690208},
      {micro:8,k:8,effective:64,status:"GPU_OOM_SECOND_MICRO",extra_allocation_bytes:15816065656},
      {micro:4,k:16,effective:64,status:"GPU_OOM_SECOND_MICRO",extra_allocation_bytes:15207781752}
    ],
    accumulation_conclusion:{zh:"三档都能完成第一个 micro-gradient，但完整 FP32 全参数 accumulator 驻留后，第二次 backward 仍需约 15–17GB；effective-batch64 accumulation 路线已正式关闭。",en:"All three candidates complete the first micro-gradient, but the next backward still needs roughly 15–17GB while the full FP32 gradient accumulator is resident; the effective-batch64 accumulation route is formally closed."},
    run1:{status:"CLOSED_FAILED_INFRASTRUCTURE_EMFILE",completed_optimizer_updates:1,checkpoint_labels:[],state_reused_by_run2:false,note:{zh:"纯文件描述符耗尽；无 checkpoint、无 outcome/loss 读取，不进入科学评估。",en:"Pure file-descriptor exhaustion; no checkpoint and no outcome/loss reads, excluded from scientific evaluation."}},
    run2:{status:"RUNNING",host:"231",pid:1696549,completed_optimizer_updates:401,last_completed_loop_label:400,target_optimizer_updates:50000,progress_as_of:"2026-09-04T11:12:17+08:00",gpu_memory_mib:73535,fd_count:1183,fd_soft_limit:65536,loss_values_read_or_reported:false,policy_outcomes_read:false,checkpoint_labels_present:[],authority_kind:"fresh run2; no run1 model/optimizer/checkpoint reuse"},
    engineering_repairs:[
      {name:"Direct-device checkpoint restore",scope:"resource lifetime only"},
      {name:"RGB metadata projection",scope:"remove unused depth decode; sealed RGB bytes unchanged"},
      {name:"Source-equivalent fast normalization",scope:"same z-score semantics"},
      {name:"User-space FFmpeg 6 runtime",scope:"TorchCodec runtime dependency only"},
      {name:"RLIMIT_NOFILE=65536",scope:"video-decoder FD capacity only"},
      {name:"state-first + serialized next-batch materialization",scope:"buffer lifetime/synchronization only"}
    ]
  },
  policies: {
    pi05:{train:true,checkpoint:"terminal label 49999 only for scientific evaluation"},
    groot:{train:false,checkpoint:"checkpoint-238000",note:{zh:"GR00T 只使用冻结公开 checkpoint；零训练 job。",en:"GR00T uses the frozen checkpoint only; zero training jobs."}}
  },
  gates:[
    {id:"G0",name:{zh:"Formal construct / matched panel",en:"Formal construct / matched panel"},status:"PASS",objection:{zh:"coupling 只是 goal 数量的别名？",en:"Is coupling only a proxy for goal count?"},answer:{zh:"13 对任务精确匹配 goal count 与主要逻辑结构，只让 shared-argument coupling 不同。",en:"Thirteen pairs exactly match goal count and major logical structure while shared-argument coupling differs."}},
    {id:"G1",name:{zh:"Human-demo horizon 负控",en:"Human-demo horizon negative control"},status:"CLOSED_NOT_SUPPORTED",objection:{zh:"高 coupling 只是让成功路径更长？",en:"Does higher coupling simply imply longer successful paths?"},answer:{zh:"未支持；该简单中介不能作为后续 policy-Q 解释。",en:"Not supported; this simple mediator cannot explain a later policy-Q effect."}},
    {id:"G2",name:{zh:"π0.5 训练实现资格",en:"π0.5 training realization"},status:"PASS_BATCH16",objection:{zh:"单卡 recipe 是不是看到结果后随意改的？",en:"Was the single-GPU recipe changed after seeing outcomes?"},answer:{zh:"所有 recipe 选择都在 policy outcome 前由资源 gate 触发；batch16 是 practical ladder 的第一项且第一项即 PASS。",en:"All recipe decisions were triggered by resource gates before policy outcomes; batch16 was the first practical-ladder candidate and passed immediately."}},
    {id:"G3",name:{zh:"π0.5 formal run2",en:"π0.5 formal run2"},status:"RUNNING",objection:{zh:"训练是否已经进入唯一可评估 terminal checkpoint？",en:"Has training reached the sole evaluable terminal checkpoint?"},answer:{zh:"尚未；当前只允许观察 progress / FD / GPU / checkpoint labels，禁止 loss 与中间 checkpoint 评估。",en:"Not yet; only progress/FD/GPU/checkpoint labels may be observed. Loss and intermediate-checkpoint evaluation are forbidden."}},
    {id:"G4",name:{zh:"Terminal 49999 content-address + serving",en:"Terminal 49999 content-address + serving"},status:"LOCKED",objection:{zh:"是否 checkpoint shopping？",en:"Could checkpoint shopping drive the result?"},answer:{zh:"只允许 49999 进入科学评估；10k/20k/30k/40k 仅 exact-state recovery。",en:"Only label 49999 may enter scientific evaluation; 10k/20k/30k/40k are exact-state recovery only."}},
    {id:"G5",name:{zh:"520 官方 rollout",en:"520 official rollouts"},status:"LOCKED",objection:{zh:"一个模型/少量实例的偶然性？",en:"Could the result be one-model or few-instance noise?"},answer:{zh:"π0.5@49999 与 GR00T@238000，各26任务×10官方实例×1 rollout；不重试成功、不换任务。",en:"π0.5@49999 and GR00T@238000 each run 26 tasks × 10 official instances × one rollout, with no retry-to-success or task replacement."}},
    {id:"G6",name:{zh:"完整矩阵后统计",en:"Analysis after complete matrix"},status:"LOCKED",objection:{zh:"结果是否依赖 partial peek / 后验统计选择？",en:"Could partial peeking or post-hoc analysis drive the claim?"},answer:{zh:"520矩阵封闭后一次性计算13个pair contrast和全部8192 exact sign flips。",en:"Only after the 520-cell matrix closes are the 13 pair contrasts and all 8192 exact sign flips computed."}}
  ],
  outcome_protocol:{
    rollouts_total:520,
    per_policy_task_instances:10,
    one_rollout_per_instance:true,
    family_contrast:"Δ_f = Q_high − Q_low",
    joint_contrast:"Δ_pair = (Δ_π0.5 + Δ_GR00T) / 2",
    test:"all 8192 exact sign flips; two-sided α=.05",
    support_requires:["mean joint contrast < 0","exact p < .05","median π0.5 contrast < 0","median GR00T contrast < 0"]
  },
  claim_boundary:{
    allowed:{zh:"两策略族、冻结13对/26任务面板上的 matched association。",en:"A matched association on the frozen 13-pair/26-task panel across two policy families."},
    forbidden:["causal planning-difficulty claim","three-family or broad cross-policy generalization","projection back to the old strict task-specific parent","reopening PORT-010","intermediate-checkpoint evaluation","partial Q/effect/p-value peeking"]
  },
  next:[
    {status:"RUNNING",zh:"完成 π0.5 run2 到 50,000 optimizer updates。",en:"Finish π0.5 run2 to 50,000 optimizer updates."},
    {status:"LOCKED",zh:"只对 terminal label 49999 做 content-address / serving qualification。",en:"Content-address and serving-qualify terminal label 49999 only."},
    {status:"LOCKED",zh:"执行 π0.5 + GR00T 的 520 个官方 rollout；期间不看 partial Q。",en:"Run 520 official π0.5 + GR00T rollouts without partial-Q inspection."},
    {status:"LOCKED",zh:"完整矩阵后一次性做 8192 exact sign-flip 与四条 support gate。",en:"After the full matrix, run the 8192 exact sign-flip analysis and the four support gates once."}
  ]
};
