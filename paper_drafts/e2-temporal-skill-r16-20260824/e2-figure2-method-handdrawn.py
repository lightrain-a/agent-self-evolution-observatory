from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math
OUT=Path(__file__).resolve().parent/'figures'; OUT.mkdir(parents=True,exist_ok=True)
W,H=3600,1600; S=W/20.0
INK='#263238'; BG='#fffdf8'; PURPLE='#ddd8f5'; BLUE='#d9e7f5'; GREEN='#dcefdc'; TAN='#f3e6cf'; RED='#f3d9d6'; YELLOW='#fff2c7'
im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'; BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def font(px,b=False): return ImageFont.truetype(BOLD if b else FONT,px)
def xy(x,y): return int(x*S),int(H-y*S)
def ctext(r,text,fs=23,b=False):
    x0,y0,x1,y1=r; f=font(fs,b); ls=text.split('\n'); dims=[d.textbbox((0,0),t,font=f) for t in ls]; hs=[q[3]-q[1] for q in dims]; ws=[q[2]-q[0] for q in dims]; yy=(y0+y1-(sum(hs)+4*(len(ls)-1)))/2
    for t,w,h in zip(ls,ws,hs): d.text(((x0+x1-w)/2,yy),t,font=f,fill=INK); yy+=h+4
def box(x,y,w,h,text,fc='white',fs=23,b=False):
    x0,y1=xy(x,y); x1,y0=xy(x+w,y+h); r=(x0,y0,x1,y1); d.rounded_rectangle(r,radius=22,fill=fc,outline=INK,width=4); ctext(r,text,fs,b)
def arrow(x1,y1,x2,y2):
    a=xy(x1,y1); b=xy(x2,y2); d.line([a,b],fill=INK,width=4); ang=math.atan2(b[1]-a[1],b[0]-a[0]); L=22; d.polygon([b,(b[0]-L*math.cos(ang-.55),b[1]-L*math.sin(ang-.55)),(b[0]-L*math.cos(ang+.55),b[1]-L*math.sin(ang+.55))],fill=INK)
def title(x,y,t,fs=32): d.text(xy(x,y),t,font=font(fs,True),fill=INK,anchor='mm')
title(10,8.25,'Figure 2 · Intervention ladder for repair and attribution',44)
title(10,7.82,'Separate net repair, operation output, surface perturbation, and integration surface before assigning credit.',27)
# Main R16 intervention ladder.
box(.45,6.25,3.0,.72,'N · original agent\nno experimental helper',GREEN,23,True)
box(4.15,6.25,3.0,.72,'G₀ · same helper surface\nempty output',TAN,23,True)
box(7.85,6.25,3.0,.72,'T · same helper surface\ntargeted operation output',PURPLE,23,True)
box(11.55,6.25,3.0,.72,'Rsurf · exact T output\nordinary context',BLUE,23,True)
arrow(3.50,6.61,4.10,6.61); arrow(7.20,6.61,7.80,6.61); arrow(10.90,6.61,11.50,6.61)
box(.85,4.95,2.55,.62,'T − N\nNET REPAIR',GREEN,24,True)
box(4.15,4.95,3.0,.62,'T − G₀\nsame-surface output',PURPLE,23,True)
box(7.85,4.95,3.0,.62,'G₀ − N\nsurface perturbation',TAN,23,True)
box(11.55,4.95,3.0,.62,'T − Rsurf\nintegration surface',BLUE,23,True)
arrow(9.35,6.20,2.13,5.62); arrow(9.35,6.20,5.65,5.62); arrow(5.65,6.20,9.35,5.62); arrow(9.35,6.20,13.05,5.62)
box(15.35,5.45,4.15,1.16,'Fail-closed rules\nT>G but T≤N → no repair\nG₀−N≠0 → surface-interacting\nRsurf only tests placement',RED,21,True)
# Bounded R17 child: same-pool serving projection, not a promotion claim.
title(6.5,3.78,'Bounded R17 mechanism child',29)
box(.65,2.70,3.05,.68,'same realized search pool\nexact candidates frozen',BLUE,22,True)
box(4.30,3.05,2.55,.64,'WIN-C\nwinner-only view',TAN,22,True)
box(4.30,2.15,2.55,.64,'MRW\nricher evidence view',GREEN,22,True)
arrow(3.75,3.04,4.25,3.37); arrow(3.75,2.96,4.25,2.47)
box(7.55,2.55,3.25,.78,'persistent updater\nstate generation',PURPLE,23,True); arrow(6.90,3.37,7.50,3.05); arrow(6.90,2.47,7.50,2.85)
box(11.50,2.55,3.55,.78,'global effect unresolved\nMRW−WIN-C = +0.023148\n48 paired units · 12 streams',YELLOW,21,True); arrow(10.85,2.94,11.45,2.94)
box(15.65,2.55,3.75,.78,'frozen First-Fail state stable\n+1/18 · +4/18\nfresh updater states: 0/18 · −1/18',RED,20,True); arrow(15.10,2.94,15.60,2.94)
box(4.20,.65,11.6,.72,'R17 interpretation: one beneficial state can be stable, yet the evidence projection does not reproducibly generate it.\nUpdater-state generation is the current bottleneck; no standalone promotion or rescue experiment follows from this result.',YELLOW,22,True)
arrow(17.52,2.50,10.0,1.42)
png=OUT/'e2-repair-attribution-method-handdrawn.png'; pdf=OUT/'e2-repair-attribution-method-handdrawn.pdf'; im.save(png,dpi=(240,240)); im.save(pdf,'PDF',resolution=240.0); print(png); print(pdf)
