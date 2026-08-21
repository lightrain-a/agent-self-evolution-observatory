# R9 ICLR 2027 paper draft

Paper title: **After a Static Safety Pass: First-Violation Events in a Persistent Web-Agent Evaluation**

## Evidence scope

The manuscript uses the frozen R9 evidence receipt at:

`generated/agent-safety-r9-future-evidence-adjudication-20260820.json`

It reports 12/12 current qualification non-violations and the completed 36-episode future evaluation (11 violation episodes; first violation in 8/12 branches and 3/4 states). The manuscript does not claim an update-only causal effect.

The recorded reopen condition is the same-held-out-schedule no-update control under the frozen runtime. That control is design-only and is not represented as completed evidence.

## Build

From the repository root:

```bash
python3 paper_drafts/agent-safety-r9-iclr2027/make_first_violation_figure.py
cd paper_drafts/agent-safety-r9-iclr2027
TEXINPUTS=../iclr2027-official: pdflatex -interaction=nonstopmode -halt-on-error main.tex
BIBINPUTS=.: BSTINPUTS=../iclr2027-official: bibtex main
TEXINPUTS=../iclr2027-official: pdflatex -interaction=nonstopmode -halt-on-error main.tex
TEXINPUTS=../iclr2027-official: pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

The checked draft is `main.pdf` (6 pages). The figure renderer reads the receipt directly and fails if its four state rows or three branch event times are missing or outside the frozen horizon.
