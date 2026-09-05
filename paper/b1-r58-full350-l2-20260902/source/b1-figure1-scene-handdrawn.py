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
def ctext(r,text,fs=27,b=False):
    x0,y0,x1,y1=r; f=font(fs,b); ls=text.split('\n'); dims=[d.textbbox((0,0),t,font=f) for t in ls]; hs=[q[3]-q[1] for q in dims]; ws=[q[2]-q[0] for q in dims]; yy=(y0+y1-(sum(hs)+4*(len(ls)-1)))/2
    for t,w,h in zip(ls,ws,hs): d.text(((x0+x1-w)/2,yy),t,font=f,fill=INK); yy+=h+4
def box(x,y,w,h,text,fc='white',fs=27,b=False):
    x0,y1=xy(x,y); x1,y0=xy(x+w,y+h); r=(x0,y0,x1,y1); d.rounded_rectangle(r,radius=22,fill=fc,outline=INK,width=4); ctext(r,text,fs,b)
def arrow(x1,y1,x2,y2):
    a=xy(x1,y1); b=xy(x2,y2); d.line([a,b],fill=INK,width=4); ang=math.atan2(b[1]-a[1],b[0]-a[0]); L=22; d.polygon([b,(b[0]-L*math.cos(ang-.55),b[1]-L*math.sin(ang-.55)),(b[0]-L*math.cos(ang+.55),b[1]-L*math.sin(ang+.55))],fill=INK)
def title(x,y,t,fs=34): d.text(xy(x,y),t,font=font(fs,True),fill=INK,anchor='mm')
title(9,7.55,'Figure 1 · Same memory content, different provenance visibility',45)
title(9,7.12,'The treatment reveals one truthful source-outcome field; retrieved content and order stay fixed.',29)
box(.45,5.75,2.2,.72,'Source episode\nends SUCCESS or FAILURE',BLUE,26,True)
box(3.15,5.75,3.0,.72,'Memory item\nactionable content + provenance',GREEN,26,True)
box(6.65,5.75,3.0,.72,'Future retrieval\nsame rows + same order',PURPLE,26,True)
arrow(2.7,6.11,3.1,6.11); arrow(6.2,6.11,6.6,6.11)
box(7.05,4.50,2.2,.64,'freeze future task\n+ reset state',TAN,25,True); arrow(8.15,5.70,8.15,5.18)
# Two executor views.
title(5.0,3.95,'Arm A · field masked',32); title(13.1,3.95,'Arm B · truthful field revealed',32)
box(2.75,2.95,4.5,.72,'same memory text\nsource_outcome_success = [MASKED]',BLUE,25,True)
box(10.85,2.95,4.5,.72,'same memory text\nsource_outcome_success = TRUE / FALSE',GREEN,24,True)
box(3.35,1.82,3.3,.62,'executor chooses\nfirst executable action',PURPLE,25,True)
box(11.45,1.82,3.3,.62,'executor chooses\nfirst executable action',PURPLE,25,True)
arrow(5.0,2.90,5.0,2.48); arrow(13.1,2.90,13.1,2.48)
box(3.35,.78,3.3,.60,'terminal task outcome',TAN,26,True); box(11.45,.78,3.3,.60,'terminal task outcome',TAN,26,True)
arrow(5.0,1.78,5.0,1.42); arrow(13.1,1.78,13.1,1.42)
box(7.25,.22,3.65,.52,'Incremental field-exposure estimand\n≠ provenance value in general',YELLOW,22,True)
png=OUT/'b1-provenance-scene-handdrawn.png'; pdf=OUT/'b1-provenance-scene-handdrawn.pdf'; im.save(png,dpi=(240,240)); im.save(pdf,'PDF',resolution=240.0); print(png); print(pdf)
