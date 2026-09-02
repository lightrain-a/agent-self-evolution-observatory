window.CURRENT_PAPER_GOLDEN_SPECS=window.CURRENT_PAPER_GOLDEN_SPECS||{};
window.CURRENT_PAPER_GOLDEN_SPECS["paper-e2"]={
 scenario:{title:{zh:"为什么搜索 Agent 做事时只选 winner，但学习时不一定也只该看 winner？",en:"Why can acting and learning need different search evidence?"},lead:{zh:"Search / planning 系统天然会生成很多候选轨迹。执行当前任务时只选最优结果很合理；但 self-evolution 还多了一个 learner，而 learner 关心的是‘我哪里还不会’，这和当前动作最优不是同一个目标。",en:"Search generates many candidates; acting and learning optimize different objectives."},reasons:[
  {t:{zh:"执行需要一个最终动作",en:"Acting needs one choice"},d:{zh:"当前任务必须选一个 winner，不能把所有 near-miss 都执行一遍。",en:"Only one candidate should be executed."}},
  {t:{zh:"学习需要诊断信息",en:"Learning needs diagnosis"},d:{zh:"near-miss / failure 常常最清楚地暴露缺失规则、错误假设或证据冲突。",en:"Near misses and failures expose capability gaps."}},
  {t:{zh:"winner 可能把错误隐藏掉",en:"Winners can hide errors"},d:{zh:"最终答案正确，不代表中间没有差点导致失败的检索或推理问题。",en:"A correct winner can hide fragile reasoning."}},
  {t:{zh:"同一个 filter 不必服务两个目标",en:"One filter need not serve both objectives"},d:{zh:"用于 acting 的 selection rule 如果原封不动复制给 learner，可能把最有价值的诊断证据删掉。",en:"An acting filter may censor useful learning evidence."}}
 ],why:{zh:"大量 self-evolving Agent 都会把‘刚才成功的轨迹’直接当学习材料。E2 问的是：这个默认做法是否把执行最优错误地当成了学习最优。",en:"Many self-evolving agents reuse successful trajectories directly; E2 tests that assumption."}},
 worked:{title:{zh:"一个具体例子：当前答案是对的，但 near-miss 才暴露真正能力缺口",en:"Worked example: the winner is right, the near miss is more diagnostic"},lead:{zh:"教学示例，不是 R17 的逐字样本。假设 Agent 要回答一个带时间截止点的官方数据问题。",en:"Teaching example using a time-sensitive evidence task."},steps:[
  {k:"01",t:"Candidate A · winner",d:{zh:"找到正确官方发布页和正确日期，当前任务成功。",en:"Correct source and cutoff; task succeeds."}},
  {k:"02",t:"Candidate B · near-miss",d:{zh:"数字几乎对，但用了 cutoff 之后的修订页，暴露‘发布时间对齐’能力缺口。",en:"Nearly correct but violates the release cutoff."}},
  {k:"03",t:"Candidate C · failure",d:{zh:"找到旧版数据却引用错 series，暴露 source-selection 问题。",en:"Wrong series exposes a source-selection failure."}},
  {k:"04",t:{zh:"执行和学习分开",en:"Separate acting and learning"},d:{zh:"当前动作仍用 A；实验只比较 learner 是只看 A，还是也保留 B/C 的诊断 witness。",en:"Act with A; vary only what the learner sees."}}
 ],compare:[
  {a:"WIN-C",b:{zh:"主要保留 winner",en:"Winner-centric"},d:{zh:"最像传统 search→learn pipeline。",en:"Simple winner-centric learning."}},
  {a:"MRW",b:{zh:"保留诊断 witness",en:"Diagnostic witnesses"},d:{zh:"让 learner 看到 near-miss / failure 暴露出的能力缺口。",en:"Preserves evidence of what nearly failed."}}
 ],note:{zh:"实验不会故意让当前任务变差：acting 两边都用同一个 winner，唯一改变的是 learner 的证据投影。",en:"Current-task acting is identical; only learning evidence changes."}},
 spotlight:{title:"Reinforcement Learning for Self-Improving Agent with Skill Library (SAGE)",problem:{zh:"怎样让 Agent 在连续任务中积累并利用技能，而不是每次靠 prompt 临时生成？",en:"How can agents accumulate and reuse skills across sequential tasks?"},added:{zh:"SAGE 把 skill library 真正放进强化学习过程，用 sequential rollout 和 skill-integrated reward 推动技能积累与复用。",en:"SAGE integrates skill libraries into RL through sequential rollouts and skill-aware reward."},method:{zh:"它说明 acting 之后的 learning pipeline 本身已经成为核心研究对象。",en:"It makes the post-action learning pipeline a first-class object."},bridge:{zh:"E2 再把问题往证据层拆：即使当前执行 winner 是正确选择，也不等于 learner 应该只看 winner。E2 的新增轴是 learning-evidence selection。",en:"E2 isolates learning-evidence selection from acting choice."}},
 architecture:{lead:{zh:"E2/R17 的数据关系是一条 search→learning→future-test 链，而不是多个独立 benchmark 拼在一起。",en:"R17 is a search→learning→future-test chain."},layers:[
  {k:"A",t:"BEA / NOAA / EIA + BLS / FOMC",d:{zh:"真实、按时间发布的官方数据源，用来产生有 cutoff 的搜索任务。",en:"Real time-stamped public releases."}},
  {k:"B",t:"Frozen search evidence",d:{zh:"同一次 search 冻结 winner / near-miss / failure，保证两臂源证据一致。",en:"Freeze winner/near-miss/failure from the same search."}},
  {k:"C",t:"WIN-C vs MRW",d:{zh:"执行完全相同，只改变 learner 能看到哪些证据。",en:"Same acting, different learning projection."}},
  {k:"D",t:"Held-out future tasks",d:{zh:"学习结束后才打开的未来任务，用来判断 projection 是否真的改变后续能力。",en:"Future tasks reserved for post-learning evaluation."}}
 ]},
 arc:[
  {k:"A",t:{zh:"先修正 attribution",en:"Repair attribution first"},q:{zh:"两臂 gain 真的是 targeted repair 吗？",en:"Is a two-arm gain true repair?"},found:{zh:"T/G/N=100/72/100，把 +28pp 改判成 comparator degradation。",en:"T/G/N=100/72/100 reveals comparator degradation."},meaning:{zh:"先证明‘漂亮 gain’可能归因错了。",en:"A clean gain can be misattributed."}},
  {k:"B",t:{zh:"加入更简单 organizer",en:"Add benign organizer"},q:{zh:"targeted credit 会不会被普通组织方式吸收？",en:"Can a simpler organizer absorb the credit?"},found:{zh:"部分数据上可完全或部分吸收。",en:"Some targeted credit is absorbed."},meaning:{zh:"继续收窄真正 residual。",en:"Further narrows the residual."}},
  {k:"C",t:"R17",q:{zh:"acting winner 和 learning evidence 是否应该解耦？",en:"Should acting and learning evidence be decoupled?"},found:{zh:"冻结 48-pair decisive design；acting 始终 winner。",en:"Freezes a 48-pair decisive design with identical acting."},meaning:{zh:"把新问题变成干净因果对照。",en:"Creates a clean causal contrast."}},
  {k:"D",t:{zh:"Exactly-once continuation",en:"Exactly-once continuation"},q:{zh:"runner 中断后还能保持 outcome-blind 吗？",en:"Can interruption remain outcome-blind?"},found:{zh:"只允许继承完成对象、证明 remaining set，再补未执行单元；partial effect 不用于改设计。",en:"Only missing units may be continued under frozen rules."},meaning:{zh:"保护最终 R17 结论不被中途结果污染。",en:"Protects final inference from mid-run adaptation."}}
 ]
};
