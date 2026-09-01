# E2-R17 MRW Primary-Control Design — Pre-Outcome Decision Memo

Date: 2026-08-29
Status: DESIGN_ONLY / NEGATIVE-CONTROL OUTCOME STILL UNOPENED
Scientific authority: ZERO

## Fixed upstream facts

- E1-A exact K=8 pools are already frozen: 96 tasks / 12 streams.
- Pre-treatment support passed strongly: 78/96 mixed pools; 12/12 exposed streams; 6/6 failure families.
- E1-B identical-treatment negative-control full run is currently executing under a frozen contract.
- WIN-A and WIN-B are byte-identical V3.1 winner-evidence treatments from cloned initial states, with independent hosted updater calls and the same 18 held-out K=1 probes.
- The negative-control outcome has not been adjudicated or used in this design memo.
- MRW execution remains unauthorized unless the preregistered WIN-A/WIN-B equivalence gate passes.

## The remaining design choice if the negative control passes

The MRW causal experiment must compare the mixed-rejected-witness learning projection against a winner-only control. The exact search pools, served acting winner, initial skill, updater implementation/configuration, executor, held-out probes, K=1 evaluation, renderer, and budgets remain fixed.

The only unresolved question is the temporal placement of the winner control.

### Option A — Reuse the existing WIN-A/WIN-B controls

For each stream s:

- execute one MRW cloned state after negative-control PASS;
- primary control is the preregistered mean of the already-collected identical-treatment controls:
  C_s = (J_s(WIN-A) + J_s(WIN-B))/2;
- primary effect D_s = J_s(MRW) - C_s.

Advantages:
- no additional winner updater/evaluation calls;
- averages two nuisance-control replicates and therefore reduces control-side sampling noise;
- maximally reuses already-qualified evidence.

Risk:
- MRW provider/evaluator calls occur later in wall-clock time than WIN-A/WIN-B, so provider/model/service drift could be aliased with projection treatment even if the resolved model ID is unchanged.

### Option B — Run a fresh contemporaneous WIN-C with MRW

For each stream s:

- after negative-control PASS, create fresh WIN-C and MRW states from the same initial skill and exact pools;
- interleave/hash-balance WIN-C vs MRW update order and held-out evaluation order;
- primary effect D_s = J_s(MRW) - J_s(WIN-C);
- historical WIN-A/WIN-B remain nuisance characterization / bridge evidence only.

Advantages:
- projection treatment is contemporaneous with its control;
- minimizes temporal provider/service drift as an alternative explanation;
- preserves clean paired same-tranche causal interpretation.

Cost:
- doubles the post-negative-control learned states from 12 to 24;
- adds approximately one full winner-control update + 18 K=1 held-out evaluations per stream.

## Decision principle

The choice must be made now, while the negative-control result is unknown. It must not depend on whether WIN-A and WIN-B happen to look favorable beyond the binary preregistered equivalence gate.

Reviewers should answer:

1. Which option gives the stronger causal identification for a top-conference paper?
2. Is temporal provider/model/service drift a material enough confound to justify Option B's extra cost after WIN-A/WIN-B equivalence has already passed?
3. If Option A is acceptable, should the primary control be WIN-A only (matching the original V3 plan) or the preregistered mean of WIN-A/WIN-B? Does averaging identical-treatment replicates change the estimand or only reduce nuisance noise?
4. If Option B is preferred, should historical WIN-A/WIN-B be used only as secondary bridge/stability evidence rather than pooled into the primary control?
5. What exact primary estimand and null/STOP/HOLD rule should be frozen before MRW outcomes exist?
6. Do not propose changing tasks, K, failure taxonomy, equivalence margin, model, or held-out probes based on results. MRW remains unauthorized if the negative-control equivalence gate fails.
