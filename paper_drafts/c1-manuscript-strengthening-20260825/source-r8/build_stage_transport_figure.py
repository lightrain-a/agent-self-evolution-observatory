#!/usr/bin/env python3
from pathlib import Path
import matplotlib.pyplot as plt

out = Path(__file__).resolve().parent / "figures" / "fig4_stage_resolved_transport.pdf"
out.parent.mkdir(parents=True, exist_ok=True)

fig, ax = plt.subplots(figsize=(7.15, 3.35))
ax.axis("off")

xs = [0.10, 0.38, 0.66, 0.90]
labels = [
    ("PERSISTENT WRITE", "20/20 Shopping pairs diverge\nJaccard = 0.673"),
    ("SOURCE-ITEM EXPOSURE", "125/172 retrieval hits\nrate = 0.727"),
    ("FIRST-ACTION UPTAKE", "TV = 0.06944, p = 0.5801\n0/36 modal changes"),
    ("NATIVE OUTCOME", "Shopping |Δ| = 0.02083\np = 0.4289; 34/36 zero"),
]

for i, (x, (title, body)) in enumerate(zip(xs, labels)):
    ax.text(x, 0.80, title, ha="center", va="center", fontsize=8.0, fontweight="bold", transform=ax.transAxes)
    ax.text(
        x, 0.64, body, ha="center", va="center", fontsize=7.3, linespacing=1.30,
        transform=ax.transAxes,
        bbox=dict(boxstyle="round,pad=0.40", fc="white", ec="0.35", lw=0.8),
    )
    if i < len(xs) - 1:
        ax.annotate(
            "", xy=(xs[i + 1] - 0.105, 0.66), xytext=(x + 0.105, 0.66),
            xycoords=ax.transAxes, arrowprops=dict(arrowstyle="->", lw=1.05, color="0.35"),
        )

ax.annotate(
    "", xy=(0.735, 0.48), xytext=(0.30, 0.48), xycoords=ax.transAxes,
    arrowprops=dict(arrowstyle="-[,widthB=7.0,lengthB=0.7", lw=1.0, color="0.35"),
)
ax.text(
    0.52, 0.405,
    "strongest supported operational boundary: after exposure, before stable action uptake",
    ha="center", va="center", fontsize=7.6, fontweight="bold", transform=ax.transAxes,
)
ax.text(
    0.52, 0.345, "evidence localization only — not a causal mediation coefficient",
    ha="center", va="center", fontsize=6.9, transform=ax.transAxes,
)

ax.text(
    0.16, 0.15,
    "FORCED CAPACITY CONTROL\nbypasses native retrieval\nterminal |Δ| = 0.15625, p = 0.00074",
    ha="center", va="center", fontsize=7.0, linespacing=1.22, transform=ax.transAxes,
    bbox=dict(boxstyle="round,pad=0.40", fc="white", ec="0.35", lw=0.8),
)
ax.annotate(
    "", xy=(0.78, 0.55), xytext=(0.28, 0.20), xycoords=ax.transAxes,
    arrowprops=dict(arrowstyle="->", lw=0.85, color="0.50", linestyle="--", connectionstyle="arc3,rad=-0.08"),
)
ax.text(
    0.68, 0.15,
    "CROSS-DOMAIN BOUNDARY\nReddit write 4/4 diverges; native terminal |Δ| = 0.125, p = 0.2253\n6/8 cells zero; two nonzero effects have opposite signs",
    ha="center", va="center", fontsize=6.75, linespacing=1.22, transform=ax.transAxes,
)

fig.tight_layout(pad=0.45)
fig.savefig(out, bbox_inches="tight")
print(out)
