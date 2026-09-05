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
def ctext(r,text,fs=24,b=False):
    x0,y0,x1,y1=r; f=font(fs,b); ls=text.split('\n'); dims=[d.textbbox((0,0),t,font=f) for t in ls]; hs=[q[3]-q[1] for q in dims]; ws=[q[2]-q[0] for q in dims]; yy=(y0+y1-(sum(hs)+4*(len(ls)-1)))/2
    for t,w,h in zip(ls,ws,hs): d.text(((x0+x1-w)/2,yy),t,font=f,fill=INK); yy+=h+4
def box(x,y,w,h,text,fc='white',fs=24,b=False):
    x0,y1=xy(x,y); x1,y0=xy(x+w,y+h); r=(x0,y0,x1,y1); d.rounded_rectangle(r,radius=22,fill=fc,outline=INK,width=4); ctext(r,text,fs,b)
def arrow(x1,y1,x2,y2):
    a=xy(x1,y1); b=xy(x2,y2); d.line([a,b],fill=INK,width=4); ang=math.atan2(b[1]-a[1],b[0]-a[0]); L=22; d.polygon([b,(b[0]-L*math.cos(ang-.55),b[1]-L*math.sin(ang-.55)),(b[0]-L*math.cos(ang+.55),b[1]-L*math.sin(ang+.55))],fill=INK)
def title(x,y,t,fs=33): d.text(xy(x,y),t,font=font(fs,True),fill=INK,anchor='mm')
title(9.5,7.55,'Figure 1 · A skill can look helpful because the comparator is harmful',44)
title(9.5,7.12,'Temporal repair claims need the original agent and same-surface controls before assigning credit.',28)
box(.55,5.75,3.05,.74,'Question\nlatest value known by cutoff',BLUE,25,True)
box(4.05,6.15,3.0,.66,'N · original agent\n100% in cutoff cell',GREEN,24,True)
box(4.05,5.15,3.0,.66,'G · target-blind stress helper\n72% in cutoff cell',RED,23,True)
box(4.05,4.15,3.0,.66,'T · targeted temporal helper\n100% in cutoff cell',PURPLE,23,True)
arrow(3.65,6.10,4.00,6.45); arrow(3.65,6.00,4.00,5.45); arrow(3.65,5.90,4.00,4.45)
box(8.00,5.75,4.25,.78,'Naive two-arm story\nT − G = +28 points\n“the skill repaired the agent”',YELLOW,25,True)
arrow(7.10,5.48,7.95,5.92)
box(13.15,5.75,4.65,.78,'Original-agent anchor changes verdict\nT − N = 0\nNO REPAIR',RED,25,True)
arrow(12.30,6.14,13.10,6.14)
# Surface attribution example.
box(2.0,2.70,3.35,.70,'G₀ · same helper surface\nempty operation output',TAN,24,True)
box(6.15,2.70,3.35,.70,'T · same surface\ntargeted operation output',PURPLE,24,True)
box(10.30,2.70,3.35,.70,'Rsurf · exact T output\nordinary context, no helper',BLUE,23,True)
box(14.45,2.70,3.15,.70,'N · no experimental\nhelper surface',GREEN,24,True)
arrow(5.40,3.05,6.10,3.05); arrow(9.55,3.05,10.25,3.05); arrow(13.70,3.05,14.40,3.05)
box(4.25,.90,10.8,.74,'Audit question: what was actually repaired—and was the gain due to the operation,\nthe helper surface, or simply a bad comparator?',YELLOW,26,True)
png=OUT/'e2-temporal-repair-scene-handdrawn.png'; pdf=OUT/'e2-temporal-repair-scene-handdrawn.pdf'; im.save(png,dpi=(240,240)); im.save(pdf,'PDF',resolution=240.0); print(png); print(pdf)
