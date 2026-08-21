from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt


def _box(ax, x, y, text, width=0.19, height=0.18):
    from matplotlib.patches import FancyBboxPatch
    p = FancyBboxPatch((x-width/2, y-height/2), width, height, boxstyle="round,pad=0.02", fill=False, linewidth=1.5)
    ax.add_patch(p)
    ax.text(x, y, text, ha="center", va="center", fontsize=9, wrap=True)


def _arrow(ax, x1, y1, x2, y2, label=""):
    ax.annotate("", xy=(x2,y2), xytext=(x1,y1), arrowprops=dict(arrowstyle="->", linewidth=1.4))
    if label:
        ax.text((x1+x2)/2, (y1+y2)/2+0.04, label, ha="center", va="center", fontsize=8)


def failure_provenance(out: Path):
    out.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.0, 2.7))
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    _box(ax,.10,.62,"Past trajectory")
    _box(ax,.34,.62,"Provenance mode\nsuccess / failure")
    _box(ax,.58,.62,"Written memory\ncontent")
    _box(ax,.82,.62,"Future action\nand outcome")
    _arrow(ax,.20,.62,.24,.62); _arrow(ax,.44,.62,.48,.62); _arrow(ax,.68,.62,.72,.62)
    _box(ax,.34,.22,"Task difficulty",width=.18,height=.14)
    _arrow(ax,.34,.29,.34,.52,"confound")
    _arrow(ax,.43,.22,.79,.53,"baseline difficulty path")
    ax.text(.5,.92,"Failure provenance is an upstream intervention on memory construction",ha="center",fontsize=11)
    fig.tight_layout(); fig.savefig(out/"fig1_provenance_causal.pdf", bbox_inches="tight"); plt.close(fig)

    labels=["Retrieval accuracy","W->W share among failures"]
    success=[93.1,0.0]; failure=[64.7,83.3]
    x=[0,1]; w=.32
    fig,ax=plt.subplots(figsize=(6.5,3.3))
    ax.bar([i-w/2 for i in x],success,width=w,label="Success-derived")
    ax.bar([i+w/2 for i in x],failure,width=w,label="Failure-derived")
    ax.set_xticks(x,labels); ax.set_ylim(0,100); ax.set_ylabel("Percent")
    ax.legend(frameon=False,loc="upper center",ncol=2)
    ax.set_title("Released financial-agent audit: provenance-conditioned outcomes")
    for i,v in enumerate(success): ax.text(i-w/2,v+2,f"{v:.1f}",ha="center",fontsize=8)
    for i,v in enumerate(failure): ax.text(i+w/2,v+2,f"{v:.1f}",ha="center",fontsize=8)
    fig.tight_layout(); fig.savefig(out/"fig2_source_reanalysis.pdf", bbox_inches="tight"); plt.close(fig)


def proxy_reward(out: Path, f0_path: Path):
    out.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.0,2.7))
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    _box(ax,.09,.58,"Identical\ntrajectory")
    _box(ax,.30,.58,"Reward bit")
    _box(ax,.51,.58,"Success/failure\nreflection prompt")
    _box(ax,.72,.58,"Written memory\ncontent")
    _box(ax,.91,.58,"Future\nbehavior",width=.15)
    for a,b in [(.18,.21),(.39,.42),(.60,.63),(.81,.835)]: _arrow(ax,a,.58,b,.58)
    ax.text(.5,.91,"Reward error becomes persistent state through reward-conditioned memory writing",ha="center",fontsize=11)
    fig.tight_layout(); fig.savefig(out/"fig1_reward_write_channel.pdf", bbox_inches="tight"); plt.close(fig)

    if f0_path.exists():
        r=json.loads(f0_path.read_text(encoding="utf-8")); pairs=[p for p in r.get("pairs") or [] if p.get("token_jaccard_distance") is not None]
        if pairs:
            labels=[p["task_id"] for p in pairs]; vals=[p["token_jaccard_distance"] for p in pairs]
            fig,ax=plt.subplots(figsize=(6.5,3.2)); ax.bar(labels,vals)
            ax.set_ylim(0,1); ax.set_xlabel("Released trajectory task ID"); ax.set_ylabel("Token Jaccard distance")
            ax.set_title("Paired memory divergence under reward-label intervention")
            for i,v in enumerate(vals): ax.text(i,v+.025,f"{v:.2f}",ha="center",fontsize=8)
            fig.tight_layout(); fig.savefig(out/"fig2_f0_memory_divergence.pdf", bbox_inches="tight"); plt.close(fig)


def temporal_skill(out: Path):
    out.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.0,2.8))
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    _box(ax,.10,.62,"Recurring\nrelease period")
    _box(ax,.31,.62,"Temporal / exogenous\nfailure mode")
    _box(ax,.53,.62,"Targeted reusable\nskill")
    _box(ax,.75,.62,"Matched future\nendpoint")
    _box(ax,.92,.62,"Outcome",width=.13)
    for a,b in [(.20,.21),(.41,.43),(.63,.65),(.85,.855)]: _arrow(ax,a,.62,b,.62)
    _box(ax,.53,.22,"Generic skill control",width=.20,height=.14)
    _arrow(ax,.53,.29,.53,.52,"same evidence")
    ax.text(.5,.92,"Targeted temporal skills isolate a mechanism behind recurring grounding failures",ha="center",fontsize=11)
    fig.tight_layout(); fig.savefig(out/"fig1_temporal_skill_causal.pdf", bbox_inches="tight"); plt.close(fig)

    fig,ax=plt.subplots(figsize=(6.2,3.0))
    ax.bar(["No reusable skill\n(reference)","Reusable skill\nTimeSage-1.0"],[1.0,.82])
    ax.set_ylim(0,1.15); ax.set_ylabel("Relative token cost")
    ax.set_title("Released TimeSage evidence: reusable skills reduce token cost")
    for i,v in enumerate([1.0,.82]): ax.text(i,v+.025,f"{v:.2f}x",ha="center",fontsize=9)
    fig.tight_layout(); fig.savefig(out/"fig2_source_skill_efficiency.pdf", bbox_inches="tight"); plt.close(fig)


def main():
    failure_provenance(Path("paper_drafts/d2-failure-memory-provenance-iclr2027/figures"))
    proxy_reward(Path("paper_drafts/d2-proxy-reward-memory-variance-iclr2027/figures"),Path("generated/d2-proxy-reward-memory-f0.json"))
    temporal_skill(Path("paper_drafts/d2-temporal-skill-bottleneck-iclr2027/figures"))

if __name__=="__main__": main()
