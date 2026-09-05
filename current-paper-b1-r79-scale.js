(()=>{
const Z=(zh,en)=>({zh,en}),pid="paper-b1";
window.CURRENT_PAPER_B1_SCALE={
  status:"PLANNED_TARGETED_EXTERNAL_VALIDITY_CHECK_NOT_AUTHORIZED",
  headline:Z("为什么主实验用 7B/8B 仍然合理，以及为什么还要补一个约 30B 的 targeted scale check","Why 7B/8B are appropriate for the main study—and why a targeted ~30B scale check is still useful"),
  lead:Z("B1 的主问题首先是受控因果识别，而不是大模型排行榜。7B/8B open-weight executor 让我们能固定模型字节、temperature=0、读取 logits、做 exact replay 与 branch mediation；R76–R78 又显示 provenance-sensitive flip 具有 executor-specific decision geometry，因此更强模型的价值是检查‘小模型能力边界 artifact’，不是替换主实验。","B1 is first a controlled causal-identification study, not a model leaderboard. Open-weight 7B/8B executors allow byte-frozen model identity, temperature=0, logit access, exact replay, and branch mediation. R76–R78 then reveal executor-specific decision geometry, so a stronger model is useful as a capability-boundary check—not as a replacement for the main experiment."),
  literature:[
    {name:"Memory-R1 · ACL 2026",models:"Llama-3.1-8B · Qwen2.5 3B/7B/14B",note:Z("memory-management / RL 论文常用 3B–14B open models 做主实验。","Memory-management/RL work commonly uses 3B–14B open models as primary substrates.")},
    {name:"AgeMem / Agentic Memory · ACL 2026",models:"Qwen2.5-7B · Qwen3-4B",note:Z("说明 4B/7B 级 memory-agent 实验本身并不异常。","Shows that 4B/7B memory-agent experimentation is not unusual.")},
    {name:"ReasoningBank · ICLR 2026",models:"Gemini-2.5-Flash/Pro · Claude-3.7-Sonnet",note:Z("也有工作直接用 frontier / hosted model，说明外部有效性不能只靠一种规模。","Other work uses frontier/hosted models, so external validity should not rely on one scale regime.")},
    {name:"RAMPART · 2026",models:"Qwen3-8B · Qwen2.5-7B · Llama-3.1-8B · Mistral-7B · Qwen3-14B",note:Z("7B–14B 仍是机制与 robustness 对比里的常见范围。","7B–14B remains a common regime for mechanism and robustness comparisons.")}
  ],
  whySmall:[
    {k:"01",title:Z("受控性比规模更重要","Control before scale"),body:Z("当前 treatment 只切 provenance field；open-weight 本地模型允许锁死权重、tokenizer、temperature、parser 与 runtime。","The treatment changes only provenance exposure; local open-weight models let us freeze weights, tokenizer, temperature, parser, and runtime.")},
    {k:"02",title:Z("机制证据需要内部可读","Mechanism evidence needs internal access"),body:Z("R77 直接读取 same-state logits，并做 exact greedy replay；黑盒 API 很难给出同等级别的可审计证据。","R77 reads same-state logits and performs exact greedy replay; black-box APIs cannot easily provide the same auditability.")},
    {k:"03",title:Z("7B/8B 已经跨 family","7B/8B already cross families"),body:Z("Qwen2.5-7B 与 Llama-3.1-8B 不是同一模型 family，而且结果中的成功任务集合和 flip geometry 明显不同。","Qwen2.5-7B and Llama-3.1-8B are from different model families, with different success sets and flip geometry.")},
    {k:"04",title:Z("不能从小模型直接推广到所有 Agent","Do not universalize from small models"),body:Z("R78 说明同样四个 Llama flip 在 Qwen 上全部 concordant；这要求我们把结论限定为 executor-specific，而不是所有现代 Agent。","R78 shows that the four Llama flips are all concordant under Qwen, so the claim must remain executor-specific rather than universal.")}
  ],
  ladder:[
    {stage:"A",model:"Qwen2.5-7B-Instruct",role:Z("主 causal executor","Primary causal executor"),runs:"189",detail:Z("66×P + 66×T + 57×S。回答 truthful provenance beyond matched neutral field，以及 correctness sensitivity。","66×P + 66×T + 57×S. Identifies truthful provenance beyond a matched neutral field plus correctness sensitivity.")},
    {stage:"B",model:"Meta-Llama-3.1-8B-Instruct",role:Z("跨 family executor replication","Cross-family executor replication"),runs:"132",detail:Z("66×P + 66×T；不 pooling，不复制所有 secondary controls。","66×P + 66×T; no pooling and no redundant replication of every secondary control.")},
    {stage:"C",model:Z("约 27–32B open-weight instruct · 具体 identity 需另行冻结","~27–32B open-weight instruct · exact identity to be frozen separately"),role:Z("targeted capability-boundary check","Targeted capability-boundary check"),runs:Z("触发式 · 预计约 20–40","Triggered · expected ~20–40"),detail:Z("只在 321-run 完成后，对真实 P/T discordant IDs + 1:1 matched concordant controls 跑 P/T；不是第三个 primary model。","Only after the 321-run study, run P/T on observed P/T-discordant IDs plus 1:1 matched concordant controls; this is not a third primary model.")}
  ],
  trigger:{
    title:Z("强模型什么时候才值得跑？","When should the stronger model run?"),
    body:Z("先完成冻结的 321 trajectories。设实际 P/T terminal-discordant task 数为 D：强模型只跑全部 D 个 discordant task，再按预先冻结的 task-family / difficulty / budget 特征选 D 个 concordant controls，每个 task 只做 P/T，因此规模约为 4D trajectories。若 D 很小，成本自然很小；若 D=0，则 capability-boundary flip check 不触发。","Complete the frozen 321 trajectories first. Let D be the number of observed P/T terminal-discordant tasks. The stronger model runs all D discordant tasks plus D concordant controls selected by a preregistered task-family/difficulty/budget matching rule, with P/T only, for about 4D trajectories. If D is small, the check stays small; if D=0, the capability-boundary flip check is not triggered."),
    rules:[
      Z("强模型的具体 checkpoint / tokenizer / decoding config 要在看到 strong-model outcome 前 content-addressed 冻结；不能根据结果换模型。","The exact strong-model checkpoint/tokenizer/decoding config must be content-addressed before any strong-model outcome is observed; no result-driven model switching."),
      Z("matched control 的选择规则在 strong-model outcome 前冻结；只能用既有 task metadata 与 321-run 的 discordant/concordant 分类，不看强模型结果。","The matched-control rule is frozen before strong-model outcomes and may use existing task metadata plus the 321-run discordant/concordant classification, never strong-model results."),
      Z("强模型只回答 external-validity / capability-boundary 问题，不与 Qwen/Llama 合并估计总体 effect。","The strong model answers an external-validity/capability-boundary question only and is never pooled with Qwen/Llama for the population effect."),
      Z("不因为强模型结果漂亮而回头改 321-run primary claim，也不为追显著性扩大 D 或增加更多模型。","A favorable strong-model result cannot rewrite the 321-run primary claim, and D/models are not expanded to chase significance.")
    ]
  },
  mechanism:{
    title:Z("为什么现在才需要 scale check？因为 R77 改变了 objection landscape","Why add scale now? R77 changed the objection landscape"),
    body:Z("在旧 32-pair Llama 中，125/136/193/327 四个 terminal flip 在 temperature=0 exact rerun 下 4/4 复现；same-state logit probe 又显示 125/193 有 direct decision-boundary shift，136/327 更依赖 transcript/self-conditioning。相同四个 task 在 Qwen 上全部 concordant。于是新的 reviewer 问题不再只是‘field format 是否匹配’，而是‘这些 flip 是否只存在于 7–8B executor 的能力/恢复边界附近？’","In the historical Llama study, all four terminal flips (125/136/193/327) reproduced under exact temperature=0 reruns. Same-state logit probes show direct decision-boundary shifts for 125/193 and stronger transcript/self-conditioning effects for 136/327. The same four tasks are all concordant under Qwen. The next reviewer question is therefore no longer only field-format matching, but whether these flips are artifacts of the capability/recovery boundary of 7–8B executors."),
    caveat:Z("这仍然不是‘模型越大就越稳定’的假设。136/327 在 Qwen 上两边都失败，而 Llama 至少一个 arm 成功；scale check 测的是 decision geometry 是否改变，不是单调的模型强弱排序。","This is not a monotonic bigger-is-more-stable hypothesis. Qwen fails both arms on 136/327 while Llama succeeds in at least one arm; the scale check tests changing decision geometry, not a scalar strength ranking.")
  },
  authority:Z("当前只是前端记录的 prospective scale-validation plan；没有生成 execution authority，也不改变 R72/R73 已通过独立 R3 审查的 321-run protocol。","This is a prospective scale-validation plan recorded in the frontend only. It grants no execution authority and does not modify the independently R3-reviewed 321-run R72/R73 protocol.")
};

const p=window.CURRENT_PAPER_PAGES?.papers?.[pid];
if(p){
  p.next=Z("先执行已经独立审查通过的 R72/R73 321-run P/T/S 设计；只有真实 discordant IDs 出现后，再按冻结规则触发约 27–32B 的 targeted P/T scale check，而不是把第三个大模型加入主实验。","Execute the independently reviewed R72/R73 321-run P/T/S design first. Only after real discordant IDs emerge should a frozen ~27–32B targeted P/T scale check be triggered; do not add a third large model to the primary experiment.");
}
const d=window.CURRENT_PAPER_DETAILS?.papers?.[pid];
if(d?.collection){
  d.collection.model=Z("Qwen2.5-7B + Llama-3.1-8B · targeted ~30B follow-up","Qwen2.5-7B + Llama-3.1-8B · targeted ~30B follow-up");
}
const oldFactory=window.CURRENT_PAPER_BEGINNER_FACTORIES?.[pid];
if(oldFactory)window.CURRENT_PAPER_BEGINNER_FACTORIES[pid]=(Y)=>{
  const s=oldFactory(Y);
  s.nextPlain=Y("主科学路线先保持 321-run 不变：Qwen 189 + Llama 132。更强模型不是第三个主实验；只有 321-run 产生真实 P/T discordant IDs 后，才用约 27–32B open-weight model 做小规模 targeted capability-boundary check。","Keep the primary 321-run design unchanged: Qwen 189 + Llama 132. A stronger model is not a third primary experiment; only after real P/T-discordant IDs appear should a ~27–32B open-weight model run a small targeted capability-boundary check.");
  return s;
};
})();
