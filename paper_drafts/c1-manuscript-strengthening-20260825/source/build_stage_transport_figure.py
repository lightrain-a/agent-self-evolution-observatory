#!/usr/bin/env python3
from pathlib import Path
import matplotlib.pyplot as plt

out = Path(__file__).resolve().parent / "figures" / "fig4_stage_resolved_transport.pdf"
out.parent.mkdir(parents=True, exist_ok=True)

fig, ax = plt.subplots(figsize=(7.15, 3.55))
ax.axis("off")

xs = [0.07, 0.29, 0.51, 0.73, 0.93]
labels = [
    ("WRITE", "20/20 Shopping pairs diverge\nJaccard = 0.673"),
    ("FORCED LEVERAGE", "terminal |Δ| = 0.15625\np = 0.00074"),
    ("NATIVE EXPOSURE", "125/172 retrieval hits"),
    ("POLICY UPTAKE", "first-action TV = 0.06944\np = 0.5801\n0/36 modal changes"),
    ("NATIVE OUTCOME", "Shopping |Δ| = 0.02083\np = 0.4289\n34/36 zero"),
]

for i, (x, (title, body)) in enumerate(zip(xs, labels)):
    ax.text(x, 0.68, title, ha="center", va="center", fontsize=8.2, fontweight="bold", transform=ax.transAxes)
    ax.text(x, 0.47, body, ha="center", va="center", fontsize=7.5, linespacing=1.35, transform=ax.transAxes,
            bbox=dict(boxstyle="round,pad=0.45", fc="white", ec="0.35", lw=0.8))
    if i < len(xs)-1:
        ax.annotate("", xy=(xs[i+1]-0.08, 0.53), xytext=(x+0.08, 0.53), xycoords=ax.transAxes,
                    arrowprops=dict(arrowstyle="->", lw=1.1, color="0.35"))

ax.text(0.50, 0.21, "Native attenuation after exposure", ha="center", va="center", fontsize=9.0,
        fontweight="bold", transform=ax.transAxes)
ax.annotate("", xy=(0.91, 0.27), xytext=(0.53, 0.27), xycoords=ax.transAxes,
            arrowprops=dict(arrowstyle="-[,widthB=8.0,lengthB=0.7", lw=1.0, color="0.35"))

ax.text(0.50, 0.08,
        "Reddit replication: write 4/4 diverges; native terminal |Δ| = 0.125, p = 0.2253; 6/8 zero, two nonzero cells have opposite signs.",
        ha="center", va="center", fontsize=7.3, transform=ax.transAxes)

fig.tight_layout(pad=0.5)
fig.savefig(out, bbox_inches="tight")
print(out)
