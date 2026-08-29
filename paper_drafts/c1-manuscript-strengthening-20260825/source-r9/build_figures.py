from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAPER = Path(__file__).resolve().parent
FIG = PAPER / "figures"
BUILD = FIG / "_build"

F0 = ROOT / "generated/d2-proxy-reward-memory-f0.json"
PROMPT = ROOT / "generated/d2-proxy-reward-memory-f0c-prompt-control.json"
F1D = ROOT / "generated/d2-proxy-reward-memory-f1d-distributional-audit.json"
F2 = ROOT / "generated/d2-proxy-reward-terminal-fixed-evidence.json"
F2R1 = ROOT / "generated/d2-proxy-reward-memory-f2r1-confirmatory.json"
VAR = ROOT / "generated/d2-proxy-reward-memory-f2r1-derived-corruption-variance.json"
HET = ROOT / "generated/d2-proxy-reward-memory-f2r1-heterogeneity-bootstrap.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def compile_tex(name: str, text: str) -> None:
    BUILD.mkdir(parents=True, exist_ok=True)
    tex = BUILD / f"{name}.tex"
    tex.write_text(text, encoding="utf-8")
    subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex.name],
        cwd=BUILD,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    shutil.copy2(BUILD / f"{name}.pdf", FIG / f"{name}.pdf")


def fig1() -> str:
    return r"""\documentclass[tikz,border=2pt]{standalone}
\usepackage{tikz}
\usepackage{amsmath,amssymb}
\usetikzlibrary{arrows.meta,positioning,fit,calc}
\begin{document}
\begin{tikzpicture}[
  font=\sffamily\small,
  box/.style={draw,rounded corners=2pt,minimum height=10mm,align=center,inner xsep=5pt},
  arrow/.style={-{Latex[length=2.3mm]},thick},
  fixed/.style={draw,dashed,rounded corners=2pt,inner sep=4pt,align=center,font=\sffamily\scriptsize}
]
\node[box,fill=blue!12,minimum width=20mm] (traj) {fixed trajectory\\$\tau$};
\node[box,fill=orange!18,minimum width=20mm,right=5mm of traj] (reward) {reward label\\$r\in\{0,1\}$};
\node[box,fill=orange!10,minimum width=25mm,right=5mm of reward] (writer) {reward-conditioned\\reflection writer $G$};
\node[box,fill=green!15,minimum width=25mm,right=5mm of writer] (memory) {persistent memory\\$M=G(\tau,r)$};
\node[box,fill=blue!10,minimum width=22mm,right=5mm of memory] (future) {matched future\\state $x'$};
\node[box,fill=purple!12,minimum width=22mm,right=5mm of future] (outcome) {action / terminal\\outcome $Y$};

\draw[arrow] (traj) -- (writer);
\draw[arrow] (reward) -- (writer);
\draw[arrow] (writer) -- (memory);
\draw[arrow] (memory) -- (outcome);
\draw[arrow] (future) -- (outcome);

\node[fixed,below=7mm of writer] (intervention) {intervention: flip only $r$\\while reusing the same $\tau$};
\draw[arrow,dashed] (intervention.north) -- ($(reward.south)+(0,-1mm)$);

\node[fixed,below=7mm of future] (matched) {future task evidence, policy,\\decoding, and cell set held fixed};
\draw[arrow,dashed] (matched.north) -- (future.south);

\node[box,fill=red!10,minimum width=48mm,below=7mm of outcome] (variance) {between-memory variance\\$\mathrm{Var}_{M}(\mathbb{E}[Y\mid M])$};
\draw[arrow] (outcome.south) -- (variance.north);

\node[font=\sffamily\scriptsize,below=2mm of traj] {source episode};
\node[font=\sffamily\scriptsize,above=2mm of writer] {write channel};
\node[font=\sffamily\scriptsize,above=2mm of outcome] {reuse channel};
\end{tikzpicture}
\end{document}
"""


def fig2() -> str:
    f0 = load(F0)
    prompt = load(PROMPT)
    pairs = [r for r in f0.get("pairs", []) if r.get("token_jaccard_distance") is not None]
    pair_coords = " ".join(f"({r['task_id']},{float(r['token_jaccard_distance']):.6f})" for r in pairs)
    pair_mean = float(f0["summary"]["mean_token_jaccard_distance"])

    rows = [r for r in prompt.get("rows", []) if r.get("complete")]
    task_ids = [str(r["task_id"]) for r in rows]
    between = " ".join(f"({r['task_id']},{float(r['between_original_distance']):.6f})" for r in rows)
    within = " ".join(f"({r['task_id']},{float(r['within_mean_distance']):.6f})" for r in rows)
    xcoords = ",".join(task_ids)
    between_mean = float(prompt["summary"]["mean_between_original_distance"])
    within_mean = float(prompt["summary"]["mean_within_mode_distance"])
    delta = float(prompt["summary"]["mean_delta_between_minus_within"])
    pval = float(prompt["summary"]["exact_one_sided_sign_flip_p"])

    return rf"""\documentclass[tikz,border=2pt]{{standalone}}
\usepackage{{pgfplots}}
\usepgfplotslibrary{{groupplots}}
\pgfplotsset{{compat=1.18}}
\begin{{document}}
\begin{{tikzpicture}}
\begin{{groupplot}}[
 group style={{group size=2 by 1,horizontal sep=1.25cm}},
 height=5.0cm,
 axis line style={{black!65}},
 tick style={{black!65}},
 label style={{font=\sffamily\scriptsize}},
 tick label style={{font=\sffamily\scriptsize}},
 title style={{font=\sffamily\small}},
 ymin=0,ymax=0.86,
 ylabel={{token-set Jaccard distance}},
 ymajorgrids=true,grid style={{black!8}},
]
\nextgroupplot[
 width=6.3cm,
 title={{(a) Same trajectory, flipped reward mode}},
 ybar,bar width=12pt,
 symbolic x coords={{21,22,23,25}},xtick=data,
 xlabel={{source trajectory}},
]
\addplot+[fill=blue!50,draw=blue!70] coordinates {{{pair_coords}}};
\addplot[black,densely dashed] coordinates {{(21,{pair_mean:.6f}) (25,{pair_mean:.6f})}};
\node[anchor=north west,font=\sffamily\scriptsize] at (rel axis cs:0.03,0.97) {{4/4 changed; mean={pair_mean:.3f}}};

\nextgroupplot[
 width=8.8cm,
 title={{(b) Stronger same-mode prompt control}},
 ybar,bar width=4pt,
 symbolic x coords={{{xcoords}}},xtick=data,
 xlabel={{fresh trajectory}},
 legend style={{font=\sffamily\scriptsize,draw=none,at={{(0.5,-0.28)}},anchor=north,legend columns=2}},
]
\addplot+[fill=orange!65,draw=orange!80] coordinates {{{between}}};
\addplot+[fill=gray!55,draw=gray!75] coordinates {{{within}}};
\legend{{reward-mode contrast,same-mode rewording}}
\node[anchor=north west,font=\sffamily\scriptsize,align=left] at (rel axis cs:0.02,0.97) {{mean {between_mean:.3f} vs. {within_mean:.3f}\\paired excess={delta:.3f}, $p={pval:.4f}$}};
\end{{groupplot}}
\end{{tikzpicture}}
\end{{document}}
"""


def fig3() -> str:
    f1d = load(F1D)
    f2 = load(F2)
    f2r1 = load(F2R1)
    var = load(VAR)
    het = load(HET)

    action = f1d["task_results"]
    action_coords = " ".join(f"({r['future_task']},{float(r['success_vs_failure_tv']):.6f})" for r in action)
    action_x = ",".join(str(r["future_task"]) for r in action)
    action_mean = float(f1d["summary"]["observed_mean_tv"])
    action_p = float(f1d["summary"]["permutation_p_ge_observed"])

    cells = f2r1["cell_results"]
    labels = [f"{r['source_memory_task']}/{r['future_task']}" for r in cells]
    cell_coords = " ".join(f"({lab},{float(r['signed_failure_minus_success']):.6f})" for lab, r in zip(labels, cells))
    cell_x = ",".join(labels)
    f2_mean = float(f2["summary"]["observed_mean_absolute_success_rate_difference"])
    f2_p = float(f2["summary"]["permutation_p_ge_observed"])
    f2r1_mean = float(f2r1["summary"]["observed_mean_absolute_success_rate_difference"])
    f2r1_p = float(f2r1["summary"]["permutation_p_ge_observed"])

    coef = float(var["mean_squared_conditional_success_effect"])
    ci = het["cell_resampling_sensitivity"]["mean_squared_effect_percentile_95_interval"]
    coef_lo, coef_hi = float(ci[0]), float(ci[1])
    zero_cells = int(het["heterogeneity"]["zero_effect_cells"])
    pos_cells = int(het["heterogeneity"]["positive_failure_minus_success_cells"])
    neg_cells = int(het["heterogeneity"]["negative_failure_minus_success_cells"])
    q_points = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
    curve = " ".join(f"({q:.1f},{coef*q*(1-q):.6f})" for q in q_points)
    curve_lo = " ".join(f"({q:.1f},{coef_lo*q*(1-q):.6f})" for q in q_points)
    curve_hi = " ".join(f"({q:.1f},{coef_hi*q*(1-q):.6f})" for q in q_points)

    return rf"""\documentclass[tikz,border=2pt]{{standalone}}
\usepackage{{pgfplots}}
\usepgfplotslibrary{{groupplots}}
\pgfplotsset{{compat=1.18}}
\begin{{document}}
\begin{{tikzpicture}}
\begin{{groupplot}}[
 group style={{group size=3 by 1,horizontal sep=0.9cm}},
 height=5.2cm,
 axis line style={{black!65}},tick style={{black!65}},
 label style={{font=\sffamily\scriptsize}},tick label style={{font=\sffamily\tiny}},
 title style={{font=\sffamily\small}},
 ymajorgrids=true,grid style={{black!8}},
]
\nextgroupplot[
 width=5.0cm,
 title={{(a) Fixed-state action distributions}},
 ybar,bar width=10pt,
 symbolic x coords={{{action_x}}},xtick=data,
 ymin=0,ymax=0.72,
 ylabel={{TV distance}},xlabel={{future task}},
]
\addplot+[fill=blue!50,draw=blue!70] coordinates {{{action_coords}}};
\addplot[black,densely dashed] coordinates {{({action[0]['future_task']},{action_mean:.6f}) ({action[-1]['future_task']},{action_mean:.6f})}};
\node[anchor=north west,font=\sffamily\tiny,align=left] at (rel axis cs:0.02,0.97) {{mean={action_mean:.3f}\\permutation $p={action_p:.3f}$}};

\nextgroupplot[
 width=7.4cm,
 title={{(b) Terminal effect by frozen cell}},
 ybar,bar width=3.2pt,
 symbolic x coords={{{cell_x}}},xtick=data,
 x tick label style={{rotate=70,anchor=east,font=\sffamily\fontsize{{5.6}}{{6}}\selectfont}},
 ymin=-0.45,ymax=0.82,
 ylabel={{signed $\Delta$ success rate}},xlabel={{source memory / future task}},
]
\addplot+[fill=orange!65,draw=orange!80] coordinates {{{cell_coords}}};
\addplot[black!60] coordinates {{({labels[0]},0) ({labels[-1]},0)}};
\node[anchor=north west,font=\sffamily\tiny,align=left] at (rel axis cs:0.02,0.97) {{mean $|\Delta|$={f2r1_mean:.3f}, $p={f2r1_p:.5f}$\\{zero_cells}/16 zero; signs {pos_cells}$+$/ {neg_cells}$-$}};

\nextgroupplot[
 width=5.0cm,
 title={{(c) Plug-in corruption variance}},
 xmin=0,xmax=0.5,ymin=0,ymax=0.045,
 xlabel={{hypothetical corruption $q$}},ylabel={{between-memory variance}},
 xtick={{0,0.1,0.2,0.3,0.4,0.5}},
]
\addplot+[densely dashed,black!55] coordinates {{{curve_lo}}};
\addplot+[densely dashed,black!55] coordinates {{{curve_hi}}};
\addplot+[very thick,mark=*,mark size=1.4pt,blue!70] coordinates {{{curve}}};
\node[anchor=north west,font=\sffamily\tiny,align=left] at (rel axis cs:0.03,0.97) {{$V(q)={coef:.4f}q(1-q)$\\cell-bootstrap range shown dashed}};
\end{{groupplot}}
\end{{tikzpicture}}
\end{{document}}
"""


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    compile_tex("fig1_reward_write_channel", fig1())
    compile_tex("fig2_write_and_prompt_control", fig2())
    compile_tex("fig3_downstream_variance", fig3())
    print(json.dumps({
        "status": "PASS",
        "figures": [
            str(FIG / "fig1_reward_write_channel.pdf"),
            str(FIG / "fig2_write_and_prompt_control.pdf"),
            str(FIG / "fig3_downstream_variance.pdf"),
        ],
        "data": [str(F0), str(PROMPT), str(F1D), str(F2), str(F2R1), str(VAR), str(HET)],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
