# C06 reproducibility entrypoint

This manuscript evaluates three intervention surfaces that are commonly called a reusable agent skill: persistent text, supplied procedure output, and executable procedure state. The paper preserves the complete F0--F12 audit lineage in the appendix while the main text is organized by scientific comparison.

Key evidence states:

- F0 tests persistent text and does not show matched separation.
- F1 is a procedure-output reachability manipulation check; it is not downstream evidence.
- F2 prospectively tests supplied output on the benchmark downstream finding and is negative under the frozen matched test.
- F3/F4 test an executable hidden-implementation swap on Qwen2.5-32B and DeepSeek-v4-Pro; both matched gates remain open.
- F5/F5-R2/F8 preserve the append-only support-recovery lineage. Only seven genuinely first-time F8 endpoints carry F8 closure authority; repeated endpoints carry zero new authority.
- F8 gives the frozen deterministic STL result 5/7 targeted versus 0/7 matched generic, exact one-sided p=0.03125.
- The deduplicated first-observation completion of the original frozen F5 population is 10/20 versus 2/20, p=0.00390625, and is robustness evidence with formal closure authority false.
- F6 is a post-hoc substantive off-target diagnostic and has no primary closure authority.
- F9/F10 use a fresh L2 source population and substantive task-local off-target procedures across five non-STL target families. Qwen gives 5/8 versus 1/8, p=0.0625. DeepSeek gives 5/9 versus 2/9, p=0.125. The two runs are adjudicated independently and their p-values are never pooled.
- F11 audits all 21 answers from the seven first-time F8 endpoints with arm identities hidden. One predeclared reviewer is valid and gives 6/7 targeted versus 2/7 generic strict semantic correctness, p=0.109375. The second reviewer is nonvoting after a parse failure and is not replaced. The deterministic F8 score stays frozen; semantic robustness is not established.
- F12 is a source-saturation audit, not a model experiment. The predeclared GO threshold is at least 16 fresh task-level pairs. Unused L2 yields zero fresh measurement-valid STL candidates after excluding F9. A complete 60-task L1 snapshot yields 12 broad strong-control metadata candidates. Because 12 < 16, no F12 model outcome is generated and same-substrate experiment expansion stops.

TimeSage-EV remains the longitudinal scientific object for period-sequential persistence. The audited public repository still lacks the evaluated period-sequential snapshot needed for the frozen C4 replay. Support absence has no negative scientific authority.

## Recompute headline statistics

From the repository root:

```bash
python scripts/reproduce_d2_temporal_skill_paper.py
```

Expected terminal markers include:

```text
F0 target-generic delta=0.076923 p=0.500000000000 gate=FAIL
F2 downstream target-generic delta=-0.050000 p=0.875000000000 gate=FAIL
F3 executable target-generic delta=0.210526 p=0.109375000000 magnitude=PASS primary=FAIL
F8 dedup first-time target-generic delta=0.714286 p=0.031250000000 gate=PASS endpoints=7 repeated_zero_authority=5
F5 frozen-population first-observation completion delta=0.400000 p=0.003906250000 endpoints=20 formal_closure=FALSE
F9 non-STL strong-control Qwen delta=0.500000 p=0.062500000000 primary=FAIL
F10 non-STL strong-control DeepSeek delta=0.333333 p=0.125000000000 primary=FAIL
F11 blinded semantic audit strict target-generic=6/7 vs 2/7 p=0.109375000000 semantic_gate=FAIL deterministic_F8_unchanged=TRUE
F12 source audit NO_GO: L2 fresh STL=0; L1 fresh broad=12 < minimum 16; model_outcomes=0
numeric_recompute=PASS
```

## Regenerate the main comparison figure

Use an environment containing matplotlib:

```bash
python scripts/reproduce_d2_temporal_skill_paper.py --figure
```

This regenerates:

`paper_drafts/d2-temporal-skill-bottleneck-iclr2027/figures/fig3_independent_probes.pdf`

## Compile and audit the manuscript

```bash
cd paper_drafts/d2-temporal-skill-bottleneck-iclr2027
latexmk -g -pdf -interaction=nonstopmode -halt-on-error main.tex
```

The final-stop manuscript CI is driven by:

`generated/d2-temporal-skill-bottleneck-final-stop-qa-contract.json`

and writes:

`generated/d2-temporal-skill-bottleneck-paper-qa-final-stop.json`

The current contract checks the nine-page main-text boundary separately from the appendix, source/figure-to-PDF freshness, F8 deterministic authority, F11 semantic non-reproduction, F9/F10 open broad-family gates, and F12 source saturation with zero new model outcomes.

The source bundle records content hashes for sanitized public evidence and manuscript sources. Provider failures, data-transfer failures, and build failures carry no scientific authority.
