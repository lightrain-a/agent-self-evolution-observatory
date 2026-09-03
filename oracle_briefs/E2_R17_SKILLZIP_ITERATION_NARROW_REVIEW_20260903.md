# E2-R17 narrow review after SkillZip/SkillZip Pro paper iteration

Act as a fresh independent adversarial senior ICLR/NeurIPS/ICML agent-systems methodology reviewer. This is a narrow ZERO-PROVIDER paper/claim audit. Do not redesign the already-reviewed V3/R2 scientific experiment and do not infer any V3 outcome.

Frozen R2 scientific object:
- commit `29799c83c662887694db52acba4bb19e83131bb0`
- contract SHA256 `f5382c552f2e6644e4cbda408510119664a8c6f8502628586c9ff5583abd1234`
- primary mechanism unit: five matched-skeleton interactions `I_h = D_h,PROCEDURAL - D_h,BINDING`
- primary PASS requires all five `I_h>0`; R=4 is measurement replication only
- protocol already prospectively reports all five `D_h,PROCEDURAL` and all five `D_h,BINDING` after the primary gate
- no V3 provider call/outcome exists; Stage-A/Stage-B authority false

Previous paper-strength review found that V3 interaction PASS alone may be too weak for the memorable act/learn-divergence thesis if MRW4 is worse than WIN-C in both cells. It also noted that selecting a positive cell after seeing all ten simple effects would be post-hoc.

A follow-up suggested `mean_h D_h,PROCEDURAL>0` plus an exact 2^5 sign-flip test at `p<=1/32`. We identified a mathematical issue: with five independent procedural effects and the mean/sum statistic, attaining the minimum one-sided sign-flip p-value 1/32 requires all five observed effects to be positive. If any observed effect is negative, flipping its sign yields a larger statistic, so p>=2/32.

We therefore froze the following SECONDARY claim-adjudication gate without changing any data collection or primary mechanism verdict:

```
SECONDARY_CONTROLLED_DIVERGENCE_GATE = PASS
iff
  primary V3 interaction gate == PASS
  AND
  D_h,PROCEDURAL > 0 for all five frozen skeletons.
```

All five magnitudes must be reported. PASS may unlock only the controlled-suite statement that the alternative learner projection outperformed WIN-C across all five preregistered procedural-transformation skeletons while exact pools and acting were held fixed. FAIL leaves the primary interaction verdict unchanged, locks the stronger act/learn-divergence thesis, and forbids selecting a favorable cell post-outcome.

The paper has also been reorganized, inspired by the research discipline of SkillZip/SkillZip Pro, into:
- RQ1 availability/censoring: what evidence exists in T_K but is absent from winner-coupled learner visibility? No utility claim.
- RQ2 causal projection effect: exact-same-pool, acting-fixed learner projection intervention. Completed global DeepSeek result remains inconclusive; reliable global MRW benefit not established.
- RQ3 prospective structural effect modification: the frozen five-skeleton V3 interaction.
- RQ4 controlled act/learn divergence: the secondary 5/5 procedural simple-effect gate above.
- RQ5 one natural/out-of-family observable-projection transport test, only after controlled evidence warrants claim expansion. No benchmark zoo; primary endpoint is positive future-skill simple effect with exact same pool/acting fixed.

The paper identity is now CAUSAL_SYSTEMS_INTERFACE_PAPER, not a failure-learning method paper and not a router paper. `Act–Learn Dual Projection` is only the organizing abstraction; the strongest novelty claim is exact-same-pool, acting-fixed causal identification of the serving-to-persistent-learning projection interface plus prospective structural effect modification if supported.

Audit only these questions:
1. Is the mathematical correction about the 2^5 sign-flip test correct?
2. Is the explicit 5/5 procedural secondary gate a scientifically defensible pre-outcome claim gate, or does it create a new fatal mismatch with the primary interaction? It may be conservative; judge whether it is valid, not whether it maximizes power.
3. Does its PASS actually license the bounded controlled-suite existential act/learn-divergence statement, and is its FAIL correctly kept separate from primary V3 mechanism PASS/FAIL?
4. Does the RQ1→RQ5 hierarchy correctly separate availability, causal consequence, structural moderator, positive divergence, and natural transport?
5. Does this SkillZip-inspired restructuring strengthen the paper without changing R2 or smuggling in new outcomes?
6. Identify at most ONE verdict-changing zero-provider correction still needed before the existing fresh-identity → separately authorized Stage-A boundary. Do not ask for a new experiment/model/benchmark before Stage A unless absolutely necessary.

End with exactly one verdict:
`PASS_SKILLZIP_DERIVED_PAPER_ITERATION`
`REVISE_ZERO_PROVIDER_CLAIM_GATE`
`REVISE_PAPER_ARCHITECTURE_BEFORE_STAGE_A`
`STOP_E2_R17`
