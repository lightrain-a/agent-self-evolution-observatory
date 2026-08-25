from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.gridspec import GridSpec
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PHASE = ROOT / "generated/asset-first-stri-r2-credit-fragmentation-phase-result-20260825.json"
PARTITION = ROOT / "generated/asset-first-stri-r2-partition-geometry-result-20260825.json"
DECOMP = ROOT / "generated/asset-first-stri-r2-selection-credit-decomposition-result-20260825.json"
OUT_PDF = HERE / "figures/stri-r2-mechanism-closure.pdf"
OUT_PNG = HERE / "figures/stri-r2-mechanism-closure.png"

phase = json.loads(PHASE.read_text())
partition = json.loads(PARTITION.read_text())
decomp = json.loads(DECOMP.read_text())

plt.rcParams.update({
    "font.size": 8.5,
    "axes.titlesize": 9.5,
    "axes.labelsize": 8.5,
    "xtick.labelsize": 7.5,
    "ytick.labelsize": 7.5,
    "font.family": "DejaVu Sans",
    "pdf.fonttype": 42,
})

fig = plt.figure(figsize=(7.0, 5.0))
gs = GridSpec(2, 2, figure=fig, height_ratios=[1.0, 1.15], width_ratios=[1.06, 0.94], hspace=0.38, wspace=0.28)
ax_a = fig.add_subplot(gs[0, :])
ax_b = fig.add_subplot(gs[1, 0])
ax_c = fig.add_subplot(gs[1, 1])

# Panel A: two identity surfaces in one persistent loop.
ax_a.set_xlim(0, 12)
ax_a.set_ylim(0, 4)
ax_a.axis("off")

def box(ax, xy, w, h, text, fc, ec="#333333", lw=1.1, fs=8.3, weight="normal"):
    r = patches.FancyBboxPatch(xy, w, h, boxstyle="round,pad=0.04,rounding_size=0.08", facecolor=fc, edgecolor=ec, linewidth=lw)
    ax.add_patch(r)
    ax.text(xy[0]+w/2, xy[1]+h/2, text, ha="center", va="center", fontsize=fs, weight=weight)
    return r

def arrow(ax, x1, y1, x2, y2, text=None, dy=0.0):
    ax.annotate("", xy=(x2,y2), xytext=(x1,y1), arrowprops=dict(arrowstyle="-|>", lw=1.15, color="#444444"))
    if text:
        ax.text((x1+x2)/2, (y1+y2)/2+dy, text, ha="center", va="center", fontsize=7.4, color="#333333")

box(ax_a, (0.25, 1.45), 1.65, 1.05, "Semantic\nskill class", "#f4f4f4", weight="bold")
box(ax_a, (2.55, 1.45), 1.85, 1.05, "Identity\nrepresentation", "#e7eef8", weight="bold")
box(ax_a, (5.05, 2.35), 1.85, 1.0, "Selection\nsurface", "#dceadf", weight="bold")
box(ax_a, (5.05, 0.60), 1.85, 1.0, "Credit / lifecycle\nsurface", "#f4dfdc", weight="bold")
box(ax_a, (7.70, 2.35), 1.65, 1.0, "Semantic\nselection mass", "#eef6ef")
box(ax_a, (7.70, 0.60), 1.65, 1.0, "Persistent\nactive library", "#faefed")
box(ax_a, (10.15, 1.45), 1.55, 1.05, "Future\nagent state", "#f4f4f4", weight="bold")
arrow(ax_a, 1.90, 1.98, 2.55, 1.98, "exact split")
arrow(ax_a, 4.40, 2.05, 5.05, 2.78)
arrow(ax_a, 4.40, 1.88, 5.05, 1.10)
arrow(ax_a, 6.90, 2.85, 7.70, 2.85, "select")
arrow(ax_a, 6.90, 1.10, 7.70, 1.10, "update")
arrow(ax_a, 9.35, 2.78, 10.15, 2.15)
arrow(ax_a, 9.35, 1.10, 10.15, 1.78)
ax_a.text(5.98, 3.62, "identity counted before action", ha="center", fontsize=7.2, color="#47704f")
ax_a.text(5.98, 0.18, "identity partitions evidence before gate", ha="center", fontsize=7.2, color="#8b4c45")
ax_a.text(-0.02, 3.70, "A", fontsize=11, weight="bold")
ax_a.set_title("One skill identity can be used on two different control surfaces", pad=2, weight="bold")

# Panel B: arbitrary-partition geometry.  The value is the exact fraction of weak
# compositions of N evidence items into k identities that fragment under M=8.
rows = partition["rows"]
ks = list(range(2, 7))
Ns = list(range(8, 49))
mat = np.zeros((len(ks), len(Ns)))
for r in rows:
    mat[int(r["k"])-2, int(r["N"])-8] = float(r["fragmentation_fraction"])
im = ax_b.imshow(mat, aspect="auto", origin="lower", interpolation="nearest", cmap="Greys", vmin=0, vmax=1)
ax_b.set_yticks(np.arange(len(ks)), [str(k) for k in ks])
ax_b.set_xticks([0,8,16,24,32,40], ["8","16","24","32","40","48"])
ax_b.set_xlabel("semantic evidence count $N$")
ax_b.set_ylabel("exact identity multiplicity $k$")
ax_b.set_title("B  Arbitrary-partition fragmentation geometry ($M=8$)", loc="left", weight="bold")
for yi, k in enumerate(ks):
    boundary_index = 8*k - 8
    if 0 <= boundary_index < len(Ns):
        ax_b.plot([boundary_index-0.5, boundary_index-0.5], [yi-0.48, yi+0.48], color="#555555", lw=1.15, ls="--")
ax_b.text(1.0, 3.68, "$M\\leq N<kM$: 100% fragmented", fontsize=8.0, weight="bold", color="#222222")
ax_b.text(0.0, -0.82, "light = fewer fragmented partitions", fontsize=6.9)
ax_b.text(20.0, -0.82, "dark = larger exact fraction", fontsize=6.9)

# Panel C: 2x2 repair decomposition.
cells = decomp["cells"]
mat2 = np.array([
    [0, 0],
    [0, 1],
], dtype=float)
ax_c.imshow(mat2, cmap="Greys", vmin=0, vmax=1, aspect="auto")
ax_c.set_xticks([0,1], ["Native", "Quotient"])
ax_c.set_yticks([0,1], ["Native", "Quotient"])
ax_c.set_xlabel("Credit / lifecycle handling")
ax_c.set_ylabel("Selection handling")
ax_c.set_title("C  Orthogonal repair channels", loc="left", weight="bold")
keys = [["S_native__C_native", "S_native__C_quotient"], ["S_quotient__C_native", "S_quotient__C_quotient"]]
for yi in range(2):
    for xi in range(2):
        c = cells[keys[yi][xi]]
        sel = "✓" if c["selection_matches_canonical"] else "×"
        cred = "✓" if c["post_credit_lifecycle_matches_canonical"] else "×"
        both = c["both_invariance_endpoints_match_canonical"]
        text = f"selection {sel}\nlifecycle {cred}"
        ax_c.text(xi, yi, text, ha="center", va="center", fontsize=8.2, weight="bold" if both else "normal", color="white" if both else "black")
ax_c.text(1, 1.42, "only both quotient → full match", ha="center", fontsize=7.1, color="#333333")

fig.subplots_adjust(top=0.96, bottom=0.10, left=0.08, right=0.98)
OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT_PDF, bbox_inches="tight")
fig.savefig(OUT_PNG, dpi=240, bbox_inches="tight")
print(OUT_PDF)
