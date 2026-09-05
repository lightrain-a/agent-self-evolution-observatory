from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math
OUT=Path(__file__).resolve().parent/'figures'; OUT.mkdir(parents=True,exist_ok=True)
W,H=3500,1500; S=W/20.0
INK='#263238'; BG='#fffdf8'; PURPLE='#ddd8f5'; BLUE='#d9e7f5'; GREEN='#dcefdc'; TAN='#f3e6cf'; RED='#f3d9d6'; YELLOW='#fff2c7'
im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'; BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def font(px,b=False): return ImageFont.truetype(BOLD if b else FONT,px)
def xy(x,y): return int(x*S),int(H-y*S)
def ctext(r,text,fs=24,b=False):
    x0,y0,x1,y1=r; f=font(fs,b); ls=text.split('\n'); dims=[d.textbbox((0,0),t,font=f) for t in ls]; hs=[q[3]-q[1] for q in dims]; ws=[q[2]-q[0] for q in dims]; yy=(y0+y1-(sum(hs)+4*(len(ls)-1)))/2
    for t,w,h in zip(ls,ws,hs): d.text(((x0+x1-w)/2,yy),t,font=f,fill=INK); yy+=h+4
def box(x,y,w,h,text,fc='white',fs=24,b=False):
    x0,y1=xy(x,y); x1,y0=xy(x+w,y+h); r=(x0,y0,x1,y1); d.rounded_rectangle(r,radius=22,fill=fc,outline=INK,width=4); ctext(r,text,fs,b)
def arrow(x1,y1,x2,y2):
    a=xy(x1,y1); b=xy(x2,y2); d.line([a,b],fill=INK,width=4); ang=math.atan2(b[1]-a[1],b[0]-a[0]); L=22; d.polygon([b,(b[0]-L*math.cos(ang-.55),b[1]-L*math.sin(ang-.55)),(b[0]-L*math.cos(ang+.55),b[1]-L*math.sin(ang+.55))],fill=INK)
def title(x,y,t,fs=33): d.text(xy(x,y),t,font=font(fs,True),fill=INK,anchor='mm')
title(10,7.55,'Figure 2 · Evaluator-Robust Temporal Audit (ERTA)',45)
title(10,7.12,'Freeze evaluators and trajectories first; expose uncertainty instead of selecting a preferred judge after disagreement.',28)
box(.45,5.30,3.2,.76,'Frozen longitudinal substrate\nupdated · base · NullMemory\nsame state/task/seed/horizon',BLUE,23,True)
box(4.25,5.30,3.2,.76,'Independent frozen evaluators\nHarmBench · DeepSeek\nno post-hoc judge replacement',PURPLE,23,True); arrow(3.70,5.68,4.20,5.68)
box(8.05,5.30,3.2,.76,'1 · Premise stability\ncurrent-pass must hold\nfor every evaluator',GREEN,23,True); arrow(7.50,5.68,8.00,5.68)
box(11.85,5.30,3.2,.76,'2 · Event-set envelope\ndefinite D = intersection\npossible U = union',TAN,23,True); arrow(11.30,5.68,11.80,5.68)
box(15.65,5.30,3.65,.76,'3 · Contrast envelope\narm direction must keep sign\nunder every evaluator',YELLOW,23,True); arrow(15.10,5.68,15.60,5.68)
# Diagnostics and compiler.
box(2.20,3.35,4.3,.72,'4 · Task-localized disagreement\nwhich behavior IDs drive judge differences?',BLUE,24,True)
box(7.70,3.35,4.3,.72,'Deterministic claim compiler\nROBUST_SUPPORTED · ROBUST_REFUTED\nEVALUATOR_UNIDENTIFIED',PURPLE,22,True)
box(13.20,3.35,4.3,.72,'Prospective held-out application\nfreeze rule + tasks before new labels\nPV1: 0 vs 3 positives',GREEN,23,True)
arrow(17.45,5.25,15.35,4.15); arrow(6.55,3.71,7.65,3.71); arrow(12.05,3.71,13.15,3.71)
# STOP side branch.
box(.80,1.55,5.5,.72,'MCTA capability-matched extension · STOP\nno qualified pre-treatment capability variable\nno MCTA safety outcomes opened',RED,23,True)
box(7.10,1.55,11.9,.72,'Fail-closed output: evaluator-specific measurements remain valid,\nbut evaluator-independent temporal direction is withheld when premise/event/order disagree.',YELLOW,24,True)
arrow(9.85,3.30,11.50,2.32)
png=OUT/'g1-erta-method-handdrawn.png'; pdf=OUT/'g1-erta-method-handdrawn.pdf'; im.save(png,dpi=(240,240)); im.save(pdf,'PDF',resolution=240.0); print(png); print(pdf)
