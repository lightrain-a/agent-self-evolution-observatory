#!/usr/bin/env python3
from pathlib import Path
import matplotlib.pyplot as plt

out = Path(__file__).resolve().parent / "figures" / "fig4_stage_resolved_transport.pdf"
out.parent.mkdir(parents=True, exist_ok=True)

fig, ax = plt.subplots(figsize=(7.15, 3.75))
ax.axis("off")

# The native transport chain contains only stages the deployed reuse path
# actually traverses. Forced fixed-evidence exposure is intentionally drawn as
# a side control because it bypasses native retrieval.
xs = [0.10, 0.38, 0.66, 0.90]
labels = [
    ("PERSISTENT WRITE", "20/20 Shopping pairs diverge\nJaccard = 0.673"),
    ("NATIVE EXPOSURE", "125/172 retrieval hits\nrate = 0.727"),
    ("FIRST-ACTION UPTAKE", "TV = 0.06944, p = 0.5801\n0/36 modal changes"),
    ("NATIVE OUTCOME", "Shopping |Δ| = 0.02083\np = 0.4289; 34/36 zero"),
]

for i, (x, (title, body)) in enumerate(zip(xs, labels)):
    ax.text(x, 0.70, title, ha="center", va="center", fontsize=8.2, fontweight="bold", transform=ax.transAxes)
    ax.text(
        x,
        0.55,
        body,
        ha="center",
        va="center",
        fontsize=7.4,
        linespacing=1.35,
        transform=ax.transAxes,
        bbox=dict(boxstyle="round,pad=0.42", fc="white", ec="0.35", lw=0.8),
    )
    if i < len(xs) - 1:
        ax.annotate(
            "",
            xy=(xs[i + 1] - 0.105, 0.58),
            xytext=(x + 0.105, 0.58),
            xycoords=ax.transAxes,
            arrowprops=dict(arrowstyle="->", lw=1.1, color="0.35"),
        )

# Operational localization: exposure remains common while the first measured
# action contrast is weak. This is a localization statement, not mediation.
ax.annotate(
    "",
    xy=(0.735, 0.41),
    xytext=(0.30, 0.41),
    xycoords=ax.transAxes,
    arrowprops=dict(arrowstyle="-[,widthB=7.0,lengthB=0.7", lw=1.0, color="0.35"),
)
ax.text(
    0.52,
    0.34,
    "strongest supported attenuation boundary: after exposure, before stable action uptake",
    ha="center",
    va="center",
    fontsize=7.8,
    fontweight="bold",
    transform=ax.transAxes,
)
ax.text(
    0.52,
    0.285,
    "operational localization only - not a causal mediation coefficient",
    ha="center",
    va="center",
    fontsize=7.0,
    transform=ax.transAxes,
)

# Capacity/leverage control. It bypasses native exposure, so it is not placed
# on the horizontal chain.
ax.text(
    0.15,
    0.13,
    "FORCED CAPACITY CONTROL\nfixed-evidence terminal |Δ| = 0.15625\np = 0.00074",
    ha="center",
    va="center",
    fontsize=7.3,
    linespacing=1.25,
    transform=ax.transAxes,
    bbox=dict(boxstyle="round,pad=0.42", fc="white", ec="0.35", lw=0.8),
)
ax.annotate(
    "bypasses native retrieval",
    xy=(0.80, 0.47),
    xytext=(0.27, 0.15),
    xycoords=ax.transAxes,
    fontsize=6.8,
    ha="center",
    arrowprops=dict(arrowstyle="->", lw=0.9, color="0.35"),
)

ax.text(
    0.66,
    0.13,
    "Cross-domain boundary: Reddit write 4/4 diverges; native terminal |Δ| = 0.125, p = 0.2253;\n6/8 cells are zero and the two nonzero cells have opposite signs.",
    ha="center",
    va="center",
    fontsize=7.0,
    linespacing=1.25,
    transform=ax.transAxes,
)

fig.tight_layout(pad=0.45)
fig.savefig(out, bbox_inches="tight")
print(out)
