from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math
OUT=Path(__file__).resolve().parent/'figures'; OUT.mkdir(parents=True,exist_ok=True)
W,H=3200,1500; S=W/18.0
INK='#263238'; BG='#fffdf8'; PURPLE='#ddd8f5'; BLUE='#d9e7f5'; GREEN='#dcefdc'; TAN='#f3e6cf'; RED='#f3d9d6'; YELLOW='#fff2c7'
im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'; BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def font(px,b=False): return ImageFont.truetype(BOLD if b else FONT,px)
def xy(x,y): return int(x*S),int(H-y*S)
def ctext(r,text,fs=26,b=False):
    x0,y0,x1,y1=r; f=font(fs,b); ls=text.split('\n'); dims=[d.textbbox((0,0),t,font=f) for t in ls]; hs=[q[3]-q[1] for q in dims]; ws=[q[2]-q[0] for q in dims]; yy=(y0+y1-(sum(hs)+4*(len(ls)-1)))/2
    for t,w,h in zip(ls,ws,hs): d.text(((x0+x1-w)/2,yy),t,font=f,fill=INK); yy+=h+4
def box(x,y,w,h,text,fc='white',fs=26,b=False):
    x0,y1=xy(x,y); x1,y0=xy(x+w,y+h); r=(x0,y0,x1,y1); d.rounded_rectangle(r,radius=22,fill=fc,outline=INK,width=4); ctext(r,text,fs,b)
def arrow(x1,y1,x2,y2):
    a=xy(x1,y1); b=xy(x2,y2); d.line([a,b],fill=INK,width=4); ang=math.atan2(b[1]-a[1],b[0]-a[0]); L=22; d.polygon([b,(b[0]-L*math.cos(ang-.55),b[1]-L*math.sin(ang-.55)),(b[0]-L*math.cos(ang+.55),b[1]-L*math.sin(ang+.55))],fill=INK)
def title(x,y,t,fs=34): d.text(xy(x,y),t,font=font(fs,True),fill=INK,anchor='mm')
title(9,7.55,'Figure 1 · Memory divergence is not behavioral divergence',45)
title(9,7.12,'The same source experience can produce different persistent memories without a stable native action change.',29)
box(.55,5.85,3.2,.72,'Frozen source trajectory τ\nsame task + same action history',BLUE,26,True)
box(4.35,6.05,2.15,.64,'SUCCESS\nreflection branch',GREEN,25,True)
box(4.35,5.05,2.15,.64,'FAILURE\nreflection branch',RED,25,True)
arrow(3.8,6.2,4.28,6.35); arrow(3.8,6.0,4.28,5.35)
box(7.05,6.05,3.0,.64,'persistent memory mˢ\nbranch-specific advice',GREEN,25,True)
box(7.05,5.05,3.0,.64,'persistent memory mᶠ\nbranch-specific advice',RED,25,True)
arrow(6.55,6.35,7.0,6.35); arrow(6.55,5.35,7.0,5.35)
box(11.0,5.55,2.55,.72,'native retrieval\nsource item exposed',PURPLE,25,True)
arrow(10.1,6.35,10.95,5.98); arrow(10.1,5.35,10.95,5.83)
box(14.2,5.55,2.8,.72,'future Shopping task\nsame matched state',TAN,25,True); arrow(13.6,5.91,14.15,5.91)
# Downstream convergence example.
box(4.0,3.35,4.0,.72,'first structured action\nbranch S',GREEN,25,True)
box(10.0,3.35,4.0,.72,'first structured action\nbranch F',RED,25,True)
box(6.75,2.02,4.5,.72,'same modal action can remain\ndespite different memories',PURPLE,26,True)
arrow(6.0,3.30,8.1,2.78); arrow(12.0,3.30,9.9,2.78)
box(6.4,.68,5.2,.68,'Question: where is the first measured native stage\nwhose branch contrast is no longer supported?',YELLOW,26,True); arrow(9.0,1.97,9.0,1.40)
png=OUT/'c1-memory-divergence-scene-handdrawn.png'; pdf=OUT/'c1-memory-divergence-scene-handdrawn.pdf'; im.save(png,dpi=(240,240)); im.save(pdf,'PDF',resolution=240.0); print(png); print(pdf)
