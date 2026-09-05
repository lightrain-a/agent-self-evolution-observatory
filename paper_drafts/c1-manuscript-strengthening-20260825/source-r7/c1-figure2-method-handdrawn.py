from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math
OUT=Path(__file__).resolve().parent/'figures'; OUT.mkdir(parents=True,exist_ok=True)
W,H=3400,1500; S=W/19.0
INK='#263238'; BG='#fffdf8'; PURPLE='#ddd8f5'; BLUE='#d9e7f5'; GREEN='#dcefdc'; TAN='#f3e6cf'; RED='#f3d9d6'; YELLOW='#fff2c7'
im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'; BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def font(px,b=False): return ImageFont.truetype(BOLD if b else FONT,px)
def xy(x,y): return int(x*S),int(H-y*S)
def ctext(r,text,fs=25,b=False):
    x0,y0,x1,y1=r; f=font(fs,b); ls=text.split('\n'); dims=[d.textbbox((0,0),t,font=f) for t in ls]; hs=[q[3]-q[1] for q in dims]; ws=[q[2]-q[0] for q in dims]; yy=(y0+y1-(sum(hs)+4*(len(ls)-1)))/2
    for t,w,h in zip(ls,ws,hs): d.text(((x0+x1-w)/2,yy),t,font=f,fill=INK); yy+=h+4
def box(x,y,w,h,text,fc='white',fs=25,b=False):
    x0,y1=xy(x,y); x1,y0=xy(x+w,y+h); r=(x0,y0,x1,y1); d.rounded_rectangle(r,radius=22,fill=fc,outline=INK,width=4); ctext(r,text,fs,b)
def arrow(x1,y1,x2,y2):
    a=xy(x1,y1); b=xy(x2,y2); d.line([a,b],fill=INK,width=4); ang=math.atan2(b[1]-a[1],b[0]-a[0]); L=22; d.polygon([b,(b[0]-L*math.cos(ang-.55),b[1]-L*math.sin(ang-.55)),(b[0]-L*math.cos(ang+.55),b[1]-L*math.sin(ang+.55))],fill=INK)
def title(x,y,t,fs=33): d.text(xy(x,y),t,font=font(fs,True),fill=INK,anchor='mm')
title(9.5,7.55,'Figure 2 · Stage-resolved memory transport audit',45)
title(9.5,7.12,'Keep stage-specific evidence semantics; localize the first unsupported measured native stage.',29)
# Native chain.
box(.45,4.65,3.05,.78,'1 · Persistent write\n20/20 Shopping diverge\ncontrol excess = 0.105 · p=.0078',GREEN,24,True)
box(4.30,4.65,3.05,.78,'2 · Native source-item exposure\n125 / 172 opportunities\nDirectly observed availability',BLUE,23,True)
box(8.15,4.65,3.05,.78,'3 · First-action uptake\nTV = 0.06944 · p=.5801\n0 / 36 modal changes',RED,23,True)
box(12.00,4.65,3.05,.78,'4 · Native terminal outcome\n|Δ| = 0.02083 · p=.4289\n34 / 36 zero',TAN,23,True)
arrow(3.55,5.04,4.25,5.04); arrow(7.40,5.04,8.10,5.04); arrow(11.25,5.04,11.95,5.04)
# Evidence boundary.
box(7.80,3.35,3.75,.64,'b* = FIRST-ACTION UPTAKE\nfirst unsupported measured native stage',YELLOW,24,True); arrow(9.67,4.60,9.67,4.04)
# Forced side control.
box(2.00,2.65,4.15,.78,'Forced fixed-evidence side control\n|Δ| = 0.15625 · p=.00074\nbranch-specific memory has leverage',PURPLE,24,True)
box(12.65,2.65,4.25,.78,'Cross-domain boundary · Reddit\n4/4 writes diverge · 6/8 terminal zero\nnonzero directions oppose',BLUE,23,True)
arrow(4.08,3.48,4.08,4.58); arrow(14.78,3.48,14.10,4.58)
# Interpretation boundary.
box(5.20,.95,8.90,.74,'Evidence localization ≠ latent causal attenuation onset\nsource-item exposure ≠ treatment-residual exposure ≠ policy use',RED,25,True)
arrow(9.67,3.30,9.67,1.75)
png=OUT/'c1-stage-transport-method-handdrawn.png'; pdf=OUT/'c1-stage-transport-method-handdrawn.pdf'; im.save(png,dpi=(240,240)); im.save(pdf,'PDF',resolution=240.0); print(png); print(pdf)
