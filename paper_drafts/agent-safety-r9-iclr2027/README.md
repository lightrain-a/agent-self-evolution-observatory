# R9 controlled ICLR 2027 manuscript

Paper title: **After a Static Safety Pass: Controlled First-Violation Evidence in a Persistent Web Agent**

## Evidence scope

The manuscript reports 120 completed behavior episodes under a frozen Qwen3-8B/AWM, BrowserART, BrowserGym, and HarmBench operationalization:

- 12 current qualification episodes: 0 violations.
- 36 updated future episodes: 11 violations and 8/12 event branches.
- 36 same-schedule base-workflow episodes: 7 violations and 4/12 event branches.
- Paired branch discordance: 4 update-only, 0 control-only, 4 both-event, 4 neither-event.
- 36 new fixed-probe snapshot episodes, reusing 12 clean step-0 outcomes: first violations in 4/12 state–probe trajectories.

The saved reopen condition, **separate persistent update effect from held-out schedule effect**, is satisfied for this frozen finite design. The manuscript does not claim a population causal effect, population hazard, universal failure of static evaluation, or oracle status for HarmBench.

## Primary evidence artifacts

- `generated/agent-safety-r9-future-evidence-adjudication-20260820.json`
- `generated/agent-safety-r9-controlled-longitudinal-adjudication-20260821.json`
- `generated/agent-safety-r9-controlled-longitudinal-scientific-review-20260821.json`
- `generated/agent-safety-r9-controlled-paper-claim-table-20260821.json`
- `generated/agent-safety-r9-controlled-memory-graph21-inputs-20260821.json`

## Manuscript assets

- `main.tex`: claim-first controlled case-study manuscript
- `MAINLINE_BRIEF.md`: evidence spine and claim boundary
- `make_controlled_longitudinal_figure.py`: paired-control and fixed-probe figure
- `make_first_violation_figure.py`: original state-by-branch event figure
- `make_full_paper_figures.py`: controlled protocol and temporal-depth figures
- `main.pdf`: compiled manuscript

## Rebuild

From the repository root:

```bash
python3 paper_drafts/agent-safety-r9-iclr2027/compile_paper_analysis.py
python3 paper_drafts/agent-safety-r9-iclr2027/make_first_violation_figure.py
python3 paper_drafts/agent-safety-r9-iclr2027/make_full_paper_figures.py
python3 paper_drafts/agent-safety-r9-iclr2027/make_controlled_longitudinal_figure.py \
  --adjudication generated/agent-safety-r9-controlled-longitudinal-adjudication-20260821.json \
  --output-prefix paper_drafts/agent-safety-r9-iclr2027/figures/controlled_longitudinal_comparison
cd paper_drafts/agent-safety-r9-iclr2027
TEXINPUTS=../iclr2027-official: pdflatex -interaction=nonstopmode -halt-on-error main.tex
BIBINPUTS=.: BSTINPUTS=../iclr2027-official: bibtex main
TEXINPUTS=../iclr2027-official: pdflatex -interaction=nonstopmode -halt-on-error main.tex
TEXINPUTS=../iclr2027-official: pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

All figure and evidence compilers consume frozen receipts. They authorize no new behavior execution.
