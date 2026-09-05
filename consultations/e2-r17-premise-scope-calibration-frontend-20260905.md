# E2-R17 premise/scope calibration — frontend projection

Date: 2026-09-05

## Why this calibration was needed

The earlier lay explanation could be read as assuming that modern agents generally generate many complete trajectories in parallel and then choose the best one to execute. That is too broad.

The paper should instead target **search-augmented / test-time-scaling agents**: systems that generate or explore more than one candidate action, branch, or trajectory before committing to served behavior.

This is a scope calibration, not a change to the frozen R2 causal intervention.

## Correct substrate

The scientific object remains a richer pre-serving search object `T_K` with two consumers:

- serving projection `a(T_K)`;
- persistent-learning projection `g(T_K)`.

`T_K` should not be defined as necessarily K parallel full trajectories. It may be produced by:

- Best-of-N / wide sampling;
- tree or MCTS search;
- step-wise candidate generation and reranking;
- beam or shallow-lookahead search.

The key requirement is that multiple candidate evidence items are actually generated/explored before the serving commit and are therefore available, in principle, to the persistent learner.

## Out-of-scope boundary

A single-path sequential agent with no separable pre-serving candidate-search object does not automatically instantiate Search-Projection Censoring. The paper must not present this as a universal defect of all agents.

The intended claim boundary is therefore:

> a serving-to-persistent-learning interface problem in search-enabled agents.

## Public-P1 implication

`SpreadsheetBench Verified-400` is a task substrate, not by itself evidence that the paper's search-interface premise holds in a realistic workflow.

When Public P1 is later frozen, its causal-transport component must instantiate a real search-enabled workflow in which `T_K_public` is generated/explored before serving. The existing C4 same-object design still applies:

- common `S0_public`;
- one common realized/content-addressed `T_K_public`;
- common served action `a(T_K_public)`;
- common updater/config/budget/order/evaluation panel;
- only `g(T_K_public)` differs.

If a public experiment uses SpreadsheetBench only as a benchmark without a real candidate-search workflow, it may support benchmark performance, but not external validity of the search-interface claim.

## Authority boundary

This frontend clarification:

- does not modify the frozen R2 contract or preflight;
- does not execute the fresh identity qualification;
- does not mint Stage-A, Stage-B, or Public-P1 authority;
- does not add scientific provider calls.
