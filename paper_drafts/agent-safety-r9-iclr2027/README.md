# R9 ICLR 2027 case-study manuscript

Paper title: **After a Static Safety Pass: A First-Violation Case Study in a Persistent Web Agent**

## Evidence scope

The manuscript reads the frozen R9 evidence receipt at:

`generated/agent-safety-r9-future-evidence-adjudication-20260820.json`

It reports the complete 48-episode case study: 0/12 current qualification violations and 11/36 future violation episodes, with a first violation in 8/12 branches and 3/4 states. Evaluation-depth analysis is derived from the same frozen trajectories: 1/12 branches visible after step 1, 7/12 after step 2, and 8/12 after step 3.

The supported claim is deliberately narrow: within this BrowserART/HarmBench operationalization, a current pass did not guarantee no first violation over the specified three-step persistent-update and held-out-task schedule. The manuscript does not claim an update-only causal effect, a population hazard, universal failure of static evaluation, or oracle status for HarmBench.

The recorded reopen condition is to **separate persistent update effect from held-out schedule effect** with a same-schedule/no-update control under the frozen runtime. That control is design-only and is not represented as completed evidence.

## Manuscript assets

- `main.tex`: nine-page claim-first case-study manuscript, including appendix
- `MAINLINE_BRIEF.md`: frozen mainline, claim boundary, closest-work collision, and section change map
- `compile_paper_analysis.py`: descriptive analysis compiler from the frozen receipt
- `make_first_violation_figure.py`: state-by-branch first-event figure
- `make_full_paper_figures.py`: protocol and temporal-depth figures
- `references.bib`: current-source bibliography including the closest longitudinal-memory comparison
- `main.pdf`: compiled manuscript

## Rebuild

From the repository root:

```bash
python3 paper_drafts/agent-safety-r9-iclr2027/compile_paper_analysis.py
python3 paper_drafts/agent-safety-r9-iclr2027/make_first_violation_figure.py
python3 paper_drafts/agent-safety-r9-iclr2027/make_full_paper_figures.py
cd paper_drafts/agent-safety-r9-iclr2027
TEXINPUTS=../iclr2027-official: pdflatex -interaction=nonstopmode -halt-on-error main.tex
BIBINPUTS=.: BSTINPUTS=../iclr2027-official: bibtex main
TEXINPUTS=../iclr2027-official: pdflatex -interaction=nonstopmode -halt-on-error main.tex
TEXINPUTS=../iclr2027-official: pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

The figure and analysis compilers read the frozen receipt directly and reject incomplete state or branch records. No script authorizes or performs new agent behavior execution.
