from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math, random
OUT=Path(__file__).resolve().parent/'figures'; OUT.mkdir(parents=True,exist_ok=True)
W,H=3200,1450; S=W/18.0; random.seed(19)
INK='#263238'; BG='#fffdf8'; PURPLE='#ddd8f5'; BLUE='#d9e7f5'; GREEN='#dcefdc'; TAN='#f3e6cf'; RED='#f3d9d6'; YELLOW='#fff2c7'
im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'; BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def font(px,b=False): return ImageFont.truetype(BOLD if b else FONT,px)
def xy(x,y): return int(x*S), int(H-y*S)
def ctext(rect,text,fs=28,b=False):
    x0,y0,x1,y1=rect; f=font(fs,b); lines=text.split('\n'); hs=[]; ws=[]
    for line in lines:
        q=d.textbbox((0,0),line,font=f); ws.append(q[2]-q[0]); hs.append(q[3]-q[1])
    yy=(y0+y1-(sum(hs)+4*(len(lines)-1)))/2
    for line,w,h in zip(lines,ws,hs): d.text(((x0+x1-w)/2,yy),line,font=f,fill=INK); yy+=h+4
def box(x,y,w,h,text,fc='white',fs=27,b=False):
    x0,y1=xy(x,y); x1,y0=xy(x+w,y+h); r=(x0,y0,x1,y1)
    d.rounded_rectangle(r,radius=22,fill=fc,outline=INK,width=4); ctext(r,text,fs,b)
def arrow(x1,y1,x2,y2):
    a=xy(x1,y1); b=xy(x2,y2); d.line([a,b],fill=INK,width=4); ang=math.atan2(b[1]-a[1],b[0]-a[0]); L=22
    d.polygon([b,(b[0]-L*math.cos(ang-.55),b[1]-L*math.sin(ang-.55)),(b[0]-L*math.cos(ang+.55),b[1]-L*math.sin(ang+.55))],fill=INK)
def title(x,y,t,fs=34): d.text(xy(x,y),t,font=font(fs,True),fill=INK,anchor='mm')
title(9,7.55,'Figure 2 · STRI audit: representation intervention → fail-closed claim',45)
title(9,7.12,'Runtime invariance and structural realizability are parallel audit views—not one causal algorithm.',29)
# 1 Freeze comparison.
title(2.2,6.48,'1 · Freeze comparison',33)
box(.35,5.42,1.7,.62,'pre-access state\nHₜ',BLUE,25,True); box(2.25,5.42,1.7,.62,'access request\nUₜ',BLUE,25,True)
box(.35,4.52,1.7,.62,'budget\nBₜ',BLUE,25,True); box(2.25,4.52,1.7,.62,'paired randomness\nξₜ',BLUE,24,True)
box(.72,3.55,2.85,.66,'semantic support + payload\nFROZEN',GREEN,26,True)
box(.72,2.55,2.85,.68,'representation r changes\nidentity · count · partition',TAN,25,True); arrow(2.15,3.50,2.15,3.25)
# 2 Runtime STRI.
title(6.5,6.48,'2 · Runtime STRI',33)
box(4.82,5.20,3.36,.72,'fixed access mechanism  Aθ',PURPLE,27,True)
box(4.82,4.18,1.50,.64,'package view\nr',TAN,25); box(6.68,4.18,1.50,.64,'package view\nr′',TAN,25)
arrow(5.57,5.15,5.57,4.86); arrow(7.43,5.15,7.43,4.86)
box(4.70,3.18,1.75,.64,'exposure\nEₜ⁽ʳ⁾',BLUE,25); box(6.55,3.18,1.75,.64,'exposure\nEₜ⁽ʳ′⁾',BLUE,25)
arrow(5.57,4.13,5.57,3.85); arrow(7.43,4.13,7.43,3.85)
box(5.14,2.12,2.72,.70,'compare semantic projection\nφ(Eₜ⁽ʳ⁾) vs φ(Eₜ⁽ʳ′⁾)',GREEN,24,True)
arrow(5.57,3.13,6.07,2.85); arrow(7.43,3.13,6.93,2.85)
# 3 Structural certificate.
title(11.1,6.48,'3 · Structural certificate',33)
box(9.22,5.42,3.76,.64,'freeze support matrix A + target q',GREEN,25,True)
box(9.22,4.46,3.76,.64,'quotient exact semantic clones',YELLOW,25,True)
box(9.22,3.50,3.76,.64,'overgrant arbitrary package mass  w ≥ 0',PURPLE,24,True)
box(9.22,2.52,3.76,.68,'solve  R*(A;q)  + dual witness',BLUE,26,True)
arrow(11.1,5.37,11.1,5.14); arrow(11.1,4.41,11.1,4.18); arrow(11.1,3.45,11.1,3.22)
box(8.82,1.46,1.95,.60,'R* = 1\nequalizable',GREEN,24,True); box(11.45,1.46,1.95,.60,'R* > 1\nstructural residual',RED,23,True)
arrow(10.48,2.47,9.80,2.08); arrow(11.72,2.47,12.42,2.08)
# 4 Evidence ladder.
title(15.7,6.48,'4 · Evidence ladder',33)
box(14.18,5.42,3.05,.62,'released control surfaces\nSkill-SP · SkillRL',BLUE,24,True)
box(14.18,4.48,3.05,.62,'bounded runtime witness\nAutoSkill P19',GREEN,24,True)
box(14.18,3.54,3.05,.62,'held-out retrieval\nqualification',PURPLE,24,True)
box(14.18,2.60,3.05,.62,'behavior propagation\npilot gate',TAN,24,True)
arrow(15.70,5.37,15.70,5.14); arrow(15.70,4.43,15.70,4.20); arrow(15.70,3.49,15.70,3.26)
box(14.02,1.46,3.38,.66,'gate fails → STOP\ndo not claim general propagation',RED,23,True); arrow(15.70,2.55,15.70,2.16)
box(4.50,.30,8.95,.66,'Diagnosis ≠ repair · access sensitivity may be supported while general downstream propagation remains unestablished',PURPLE,25,True)
png=OUT/'stri-method-handdrawn.png'; pdf=OUT/'stri-method-handdrawn.pdf'
im.save(png,dpi=(240,240)); im.save(pdf,'PDF',resolution=240.0)
print(png); print(pdf)
