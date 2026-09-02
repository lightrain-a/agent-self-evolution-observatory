window.CURRENT_PAPER_GOLDEN_SPECS=window.CURRENT_PAPER_GOLDEN_SPECS||{};
window.CURRENT_PAPER_GOLDEN_SPECS["paper-b"]={
 scenario:{title:{zh:"为什么 embodied Agent 需要把‘当前用了 memory’和‘长期自我进化’分开？",en:"Why is memory-conditioned control not yet self-evolution?"},lead:{zh:"机器人每个 episode 都会遇到局部失败和偶然成功。工程上如果看到一次好结果就永久写 memory，噪声会直接变成长期状态；因此真实 self-evolution 必须有写入、验证、提交和未来复用的生命周期。",en:"Embodied agents need a memory lifecycle rather than immediate write-back."},reasons:[
  {t:{zh:"一次成功可能是偶然",en:"One success may be accidental"},d:{zh:"环境随机性、动作噪声或碰巧恢复都可能让结果看起来很好。",en:"Noise or luck can produce a good episode."}},
  {t:{zh:"错误 credit 会被永久放大",en:"Bad credit persists"},d:{zh:"把偶然成功归给错误经验并写入，会让后续 episode 反复复用错误 memory。",en:"Misattributed memories can persist across episodes."}},
  {t:{zh:"当前 recovery 不等于长期 benefit",en:"Recovery is not future benefit"},d:{zh:"这一次动作变好，不能证明下一次遇到相似状态还能检索并受益。",en:"Current recovery says nothing about future reuse."}},
  {t:{zh:"长期状态需要可撤销治理",en:"Persistent state needs governance"},d:{zh:"真实系统需要 candidate / provisional / verified / downgrade / revoke 等状态，而不是 always-write。",en:"Persistent memories need admission, verification, and revocation states."}}
 ],why:{zh:"‘memory-on 后成功一次’和‘Agent 真正通过经验长期变强’是两个完全不同的科学主张。Paper B 把中间缺失的闭环补出来。",en:"One memory-conditioned success is far weaker than persistent self-evolution."}},
 worked:{title:{zh:"一个具体例子：一次机器人 recovery 怎样才有资格变成长期 memory？",en:"Worked example: when should one recovery become persistent memory?"},lead:{zh:"教学示例，不是当前 confirmatory rollout。假设机器人第一次遇到抽屉前方被物体挡住。",en:"Teaching example for a cross-episode robot task."},steps:[
  {k:"01",t:{zh:"当前 episode 产生经验",en:"Current experience"},d:{zh:"机器人从左侧绕行后成功接近目标，形成 candidate memory。",en:"A recovery produces a candidate memory."}},
  {k:"02",t:{zh:"先 provisional，不立刻永久写入",en:"Keep it provisional"},d:{zh:"记录‘从左侧绕行’但暂时不当成长期规则。",en:"Do not immediately commit the experience."}},
  {k:"03",t:{zh:"验证 effect",en:"Verify the effect"},d:{zh:"用 same-state counterfactual / independent verifier 检查收益是否真来自这段 memory。",en:"Verify attribution before commitment."}},
  {k:"04",t:{zh:"未来 re-exposure",en:"Future re-exposure"},d:{zh:"另一个 episode 再遇相似遮挡时，必须能检索、复用并带来可验证 benefit。",en:"Later related episodes must retrieve and benefit from it."}}
 ],compare:[
  {a:{zh:"Fast loop",en:"Fast loop"},b:{zh:"当前 retrieval → action → recovery",en:"Current retrieval→action→recovery"},d:{zh:"回答‘这一次有没有影响’。",en:"Current behavioral effect."}},
  {a:{zh:"Slow loop",en:"Slow loop"},b:{zh:"write → verify → commit → future reuse",en:"write→verify→commit→future reuse"},d:{zh:"回答‘有没有形成长期自我进化’。",en:"Persistent self-evolution."}}
 ],note:{zh:"Paper B 的最终硬门不是一次 action shift，而是跨 episode 的 write→reuse→benefit。",en:"The final gate is cross-episode write→reuse→benefit."}},
 spotlight:{title:"Agentic Memory: Learning Unified Long-Term and Short-Term Memory Management for Large Language Model Agents",problem:{zh:"Agent 同时需要短期工作记忆和长期经验，但固定规则很难决定什么该保留、更新或忘记。",en:"Agents need coordinated short- and long-term memory management."},added:{zh:"ACL 2026 的 Agentic Memory 把长期/短期 memory management 统一成可学习的管理问题，是‘memory lifecycle’的直接近邻。",en:"Agentic Memory learns unified long/short-term memory management."},method:{zh:"它强调怎样管理 memory state；Paper B 则把 embodied self-evolution 的科学硬门放到 future re-exposure 上。",en:"It focuses on memory management; Paper B requires future re-exposure evidence."},bridge:{zh:"两者都反对‘存进去就算记住’。Paper B 更进一步要求：候选经验经过验证和提交后，必须在未来机器人 episode 中再次被检索并产生收益，才叫长期自进化。",en:"Paper B requires verified future reuse in embodied episodes."}},
 architecture:{lead:{zh:"Paper B 把同一 LIBERO/MemoryVLA 底座从‘当前 influence’延伸成‘跨 episode 生命周期’。",en:"Paper B extends the same embodied substrate into a longitudinal lifecycle."},layers:[
  {k:"A",t:"LIBERO / LIBERO-Plus",d:{zh:"提供语言操控任务和受控扰动场景。",en:"Robot tasks and perturbations."}},
  {k:"B",t:"MemoryVLA",d:{zh:"提供真实 memory-conditioned action channel。",en:"Memory-conditioned VLA carrier."}},
  {k:"C",t:"24 development scopes",d:{zh:"task0–2 × Camera/Robot/Noise/Layout × 两档，开发 repair / rejoin / success / write-back 判定。",en:"Development scopes for robustness and write-back logic."}},
  {k:"D",t:"Longitudinal stream",d:{zh:"真正确证层：source episode → verified update → future related episode。",en:"Confirmatory source→update→future-reuse stream."}}
 ]},
 arc:[
  {k:"A",t:{zh:"底座复现",en:"Substrate reproduction"},q:{zh:"官方 MemoryVLA 路线可信可跑吗？",en:"Is the base carrier reliable?"},found:{zh:"task0 reproduction PASS。",en:"Task0 reproduction passes."},meaning:{zh:"先取得实验资格。",en:"Qualifies the carrier."}},
  {k:"B",t:{zh:"当前影响",en:"Current influence"},q:{zh:"memory 会在同状态改变动作吗？",en:"Does memory change action?"},found:{zh:"同状态 ||Δa||₂≈0.5541。",en:"Same-state action shift ≈0.5541."},meaning:{zh:"只是 fast-loop prerequisite。",en:"Fast-loop prerequisite only."}},
  {k:"C",t:{zh:"24-scope 开发",en:"24-scope development"},q:{zh:"influence 能否稳定变成 repair / rejoin / success？",en:"Can influence become robust recovery?"},found:{zh:"测试空间已冻结，不能写成 robustness 已证明。",en:"The test space is frozen; robustness is not yet established."},meaning:{zh:"开发 slow-loop admission / verification 规则。",en:"Develops slow-loop admission/verification."}},
  {k:"D",t:{zh:"未来复用确证",en:"Future-reuse confirmation"},q:{zh:"写进去的 memory 未来还能产生 benefit 吗？",en:"Does committed memory help later?"},found:{zh:"完整 confirmatory evidence 尚未闭合。",en:"Confirmatory evidence is pending."},meaning:{zh:"longitudinal self-evolution claim 仍 pending。",en:"Longitudinal claim remains pending."}}
 ]
};
