from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT_DIR = Path(__file__).resolve().parent / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

fig, ax = plt.subplots(figsize=(8.4, 4.25))
ax.set_xlim(0, 12)
ax.set_ylim(0, 7)
ax.axis("off")


def box(x: float, y: float, w: float, h: float, text: str, *, fontsize: float = 9.0, linestyle: str = "-") -> None:
    patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04", fill=False, linewidth=1.15, linestyle=linestyle)
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize)


def arrow(x1: float, y1: float, x2: float, y2: float, text: str = "", *, mutation: float = 12) -> None:
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="->", mutation_scale=mutation, linewidth=1.0))
    if text:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.18, text, ha="center", va="bottom", fontsize=8.2)

# Shared semantic layer.
ax.text(6.0, 6.62, "Frozen semantic basis (unchanged)", ha="center", fontsize=11, fontweight="bold")
box(4.05, 5.58, 1.45, 0.66, r"primitive $u_a$")
box(6.50, 5.58, 1.45, 0.66, r"primitive $u_b$")
box(2.75, 4.35, 1.65, 0.62, r"$x_a:\{u_a\}$", fontsize=8.7)
box(5.18, 4.35, 1.65, 0.62, r"$x_{ab}:\{u_a,u_b\}$", fontsize=8.7)
box(7.60, 4.35, 1.65, 0.62, r"$x_b:\{u_b\}$", fontsize=8.7)
arrow(4.75, 5.55, 3.60, 5.00)
arrow(4.90, 5.55, 5.75, 5.00)
arrow(7.10, 5.55, 6.25, 5.00)
arrow(7.25, 5.55, 8.42, 5.00)

# Taxonomy T.
ax.text(2.2, 3.55, "Taxonomy $T$", ha="center", fontsize=10.5, fontweight="bold")
box(0.70, 2.55, 1.65, 0.65, r"package $s_a\to u_a$")
box(2.72, 2.55, 1.65, 0.65, r"package $s_b\to u_b$")
ax.text(2.55, 2.08, r"uniform package control: $p=(1/2,1/2)$", ha="center", fontsize=8.7)
ax.text(2.55, 1.58, r"primitive mass: $m(u_a)=1/2,\;m(u_b)=1/2$", ha="center", fontsize=8.7)

# Taxonomy phi(T): exact identity split as conceptual nuisance example.
ax.text(9.15, 3.55, r"Semantics-preserving reparameterization $\phi(T)$", ha="center", fontsize=10.5, fontweight="bold")
box(6.25, 2.55, 1.55, 0.65, r"$s_a^{(1)}\to u_a$")
box(8.15, 2.55, 1.55, 0.65, r"$s_a^{(2)}\to u_a$")
box(10.05, 2.55, 1.55, 0.65, r"$s_b\to u_b$")
ax.text(8.92, 2.08, r"same primitive support; one extra package identity", ha="center", fontsize=8.7)
ax.text(8.92, 1.58, r"uniform package control: $m(u_a)=2/3,\;m(u_b)=1/3$", ha="center", fontsize=8.7)

arrow(4.52, 2.88, 6.02, 2.88, "same $U$ and support predicates", mutation=13)

# STRI and certificate callouts.
box(1.15, 0.42, 4.10, 0.68, "STRI principle: semantic control should not change\nsolely because package representation changed", fontsize=8.6)
box(6.55, 0.42, 4.30, 0.68, r"STRI-Cert: audit frozen support geometry with $R^*(A)$\n$R^*=1$: equalizable; $R^*>1$: irreducible residual", fontsize=8.6)
arrow(5.42, 1.13, 5.42, 0.83)
arrow(6.00, 1.13, 7.05, 0.83)

ax.text(6.0, 6.95, "Skill-taxonomy representation is a nuisance variable, not a new semantic capability", ha="center", va="top", fontsize=10.2)
fig.tight_layout(pad=0.5)

for ext in ("pdf", "png"):
    fig.savefig(OUT_DIR / f"stri-overview.{ext}", dpi=220, bbox_inches="tight")

print(json.dumps({"pdf": str(OUT_DIR / "stri-overview.pdf"), "png": str(OUT_DIR / "stri-overview.png")}))
