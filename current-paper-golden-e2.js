window.CURRENT_PAPER_GOLDEN_SPECS=window.CURRENT_PAPER_GOLDEN_SPECS||{};
window.CURRENT_PAPER_GOLDEN_SPECS["paper-e2"]={
 scenario:{title:{zh:"为什么搜索 Agent 做事时只选 winner，但学习时不一定也只该看 winner？",en:"Why can acting and learning need different search evidence?"},lead:{zh:"Search / planning 系统天然会生成很多候选轨迹。执行当前任务时只选最优结果很合理；但 self-evolution 还多了一个 learner，而 learner 关心的是‘我哪里还不会’，这和当前动作最优不是同一个目标。",en:"Search generates many candidates; acting and learning optimize different objectives."},reasons:[
  {t:{zh:"执行需要一个最终动作",en:"Acting needs one choice"},d:{zh:"当前任务必须选一个 winner，不能把所有 near-miss 都执行一遍。",en:"Only one candidate should be executed."}},
  {t:{zh:"学习需要诊断信息",en:"Learning needs diagnosis"},d:{zh:"near-miss / failure 常常最清楚地暴露缺失规则、错误假设或证据冲突。",en:"Near misses and failures expose capability gaps."}},
  {t:{zh:"winner 可能把错误隐藏掉",en:"Winners can hide errors"},d:{zh:"最终答案正确，不代表中间没有差点导致失败的检索或推理问题。",en:"A correct winner can hide fragile reasoning."}},
  {t:{zh:"同一个 filter 不必服务两个目标",en:"One filter need not serve both objectives"},d:{zh:"用于 acting 的 selection rule 如果原封不动复制给 learner，可能把最有价值的诊断证据删掉。",en:"An acting filter may censor useful learning evidence."}}
 ],why:{zh:"大量 self-evolving Agent 都会把‘刚才成功的轨迹’直接当学习材料。E2 问的是：这个默认做法是否把执行最优错误地当成了学习最优。",en:"Many self-evolving agents reuse successful trajectories directly; E2 tests that assumption."}},
 worked:{title:{zh:"一个具体例子：做题当然用最佳答案，但复盘时‘差一点错’可能更值得学",en:"Worked example: the winner is right, the near miss is more diagnostic"},lead:{zh:"教学示例，不是 R17 的逐字样本。假设 Agent 要回答一个带时间截止点的官方数据问题。搜索产生三条候选轨迹。",en:"Teaching example using a time-sensitive evidence task."},steps:[
  {k:"01",t:{zh:"候选 A · 最佳轨迹",en:"Candidate A · winner"},d:{zh:"找到正确官方发布页，也用了截止日期之前的正确版本，所以当前任务成功。",en:"Correct source and cutoff; task succeeds."}},
  {k:"02",t:{zh:"候选 B · 差一点成功",en:"Candidate B · near-miss"},d:{zh:"数字几乎对，但偷偷用了截止日期之后才发布的修订页。它最清楚地暴露：Agent 还没真正学会‘只能用当时已经发布的信息’。",en:"Nearly correct but violates the release cutoff."}},
  {k:"03",t:{zh:"候选 C · 明显失败",en:"Candidate C · failure"},d:{zh:"找到了旧版数据，却引用错了数据系列，暴露另一个‘来源选择’问题。",en:"Wrong series exposes a source-selection failure."}},
  {k:"04",t:{zh:"做题和复盘分开",en:"Separate acting and learning"},d:{zh:"做当前任务时，两组都毫无争议地使用 A。真正的实验只改一件事：复盘学习时，是只给 Agent 看 A，还是把 B/C 这些能暴露错误原因的线索也保留下来。",en:"Act with A; vary only what the learner sees."}}
 ],compare:[
  {a:{zh:"只看赢家组（WIN-C）",en:"WIN-C"},b:{zh:"复盘只保留最佳轨迹",en:"Winner-centric"},d:{zh:"优点是简单，但可能只看到‘这次做对了’，看不到自己差点在哪里出错。",en:"Simple winner-centric learning."}},
  {a:{zh:"保留诊断线索组（MRW）",en:"MRW"},b:{zh:"最佳轨迹之外，也保留能解释能力缺口的轨迹",en:"Diagnostic witnesses"},d:{zh:"让学习模块同时看到‘为什么差点错’和‘为什么真的错’，但当前任务执行仍然完全一样。",en:"Preserves evidence of what nearly failed."}}
 ],note:{zh:"所以 R17 不是让 Agent 故意执行差答案。两组做题都用同一个最佳轨迹；唯一差别是‘事后复盘时给它看哪些学习材料’。",en:"Current-task acting is identical; only learning evidence changes."}},
 spotlight:{title:"Reinforcement Learning for Self-Improving Agent with Skill Library (SAGE)",problem:{zh:"怎样让 Agent 在连续任务中积累并利用技能，而不是每次靠 prompt 临时生成？",en:"How can agents accumulate and reuse skills across sequential tasks?"},added:{zh:"SAGE 把 skill library 真正放进强化学习过程，用 sequential rollout 和 skill-integrated reward 推动技能积累与复用。",en:"SAGE integrates skill libraries into RL through sequential rollouts and skill-aware reward."},method:{zh:"它说明 acting 之后的 learning pipeline 本身已经成为核心研究对象。",en:"It makes the post-action learning pipeline a first-class object."},bridge:{zh:"E2 再把问题往证据层拆：即使当前执行 winner 是正确选择，也不等于 learner 应该只看 winner。E2 的新增轴是 learning-evidence selection。",en:"E2 isolates learning-evidence selection from acting choice."}},
 architecture:{lead:{zh:"R17 可以理解成一条很直白的链：先搜索出多条候选 → 当前任务照常用最佳轨迹 → 学习阶段给两组看不同的复盘材料 → 最后用一批此前没见过的未来任务检查谁学得更好。",en:"R17 is a search→learning→future-test chain."},layers:[
  {k:"A",t:"BEA / NOAA / EIA + BLS / FOMC",d:{zh:"真实、按时间发布的官方数据源。每个任务都有明确的‘到这个日期为止你能看到哪些信息’。",en:"Real time-stamped public releases."}},
  {k:"B",t:{zh:"同一次搜索产生的候选轨迹",en:"Frozen search evidence"},d:{zh:"把最佳轨迹、差一点成功的轨迹和失败轨迹一起冻结，保证两组起点完全一样。",en:"Freeze winner/near-miss/failure from the same search."}},
  {k:"C",t:{zh:"只看赢家组 vs 保留诊断线索组",en:"WIN-C vs MRW"},d:{zh:"两组当前执行完全一样，只改变事后学习时能看到哪些轨迹。",en:"Same acting, different learning projection."}},
  {k:"D",t:{zh:"学习后才打开的未来测试任务",en:"Held-out future tasks"},d:{zh:"这些任务前面没有参与学习，用来判断‘不同复盘材料’到底有没有改变未来能力。",en:"Future tasks reserved for post-learning evaluation."}}
 ]},
 arc:[
  {k:"A",t:{zh:"先确认：看起来提升了，功劳到底该给谁？",en:"Repair attribution first"},q:{zh:"只比较两个实验组时看到 +28 个百分点，真能说明目标技能修好了问题吗？",en:"Is a two-arm gain true repair?"},found:{zh:"加入原始 Agent 后，T/G/N=100/72/100：原始 Agent 本来就是 100，说明不是目标方法变好，而是对照组变差。",en:"T/G/N=100/72/100 reveals comparator degradation."},meaning:{zh:"第一课是：一个漂亮提升数字，可能只是对照组被破坏了，不能直接把功劳记给目标方法。",en:"A clean gain can be misattributed."}},
  {k:"B",t:{zh:"再问：是不是简单整理信息就能得到同样收益？",en:"Add benign organizer"},q:{zh:"如果加入一个不包含目标知识、只负责把信息整理清楚的简单对照，它能不能吸收所谓‘目标技能’的收益？",en:"Can a simpler organizer absorb the credit?"},found:{zh:"在部分数据上，它确实完全或部分吸收了收益。",en:"Some targeted credit is absorbed."},meaning:{zh:"因此论文继续把‘真正属于目标方法的那部分贡献’往窄处收。",en:"Further narrows the residual."}},
  {k:"C",t:{zh:"R17 · 做题材料和复盘材料分开",en:"R17"},q:{zh:"做题时选最佳轨迹很合理；复盘学习时也必须只看最佳轨迹吗？",en:"Should acting and learning evidence be decoupled?"},found:{zh:"冻结了 48 组配对实验。两组做题始终用同一个最佳轨迹，只改变复盘材料。",en:"Freezes a 48-pair decisive design with identical acting."},meaning:{zh:"这样未来如果表现不同，差异才有资格归因给‘学习时看了哪些轨迹’。",en:"Creates a clean causal contrast."}},
  {k:"D",t:{zh:"运行中断后也不偷看中间答案",en:"Exactly-once continuation"},q:{zh:"实验跑到一半意外退出后，怎么避免根据已经完成的结果改剩余设计？",en:"Can interruption remain outcome-blind?"},found:{zh:"只允许继承已经完成的对象，证明哪些单元还没跑，再按原合同补齐；中间效果明确不用于改模型、提示词或统计。",en:"Only missing units may be continued under frozen rules."},meaning:{zh:"这样最终 48/48 的结论不会被‘跑到一半看到趋势后改实验’污染。",en:"Protects final inference from mid-run adaptation."}}
 ]
};
