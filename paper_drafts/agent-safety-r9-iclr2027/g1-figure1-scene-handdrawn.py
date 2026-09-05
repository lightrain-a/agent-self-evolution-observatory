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
title(9.5,7.55,'Figure 1 · The same trajectories can imply different temporal safety conclusions',43)
title(9.5,7.12,'Evaluator identity changes the premise, first-event set, and arm ordering without changing the agent trajectory.',28)
box(.55,5.75,3.2,.74,'Persistent web agent\nQwen3-8B + AWM',BLUE,26,True)
box(4.25,5.75,3.35,.74,'Frozen completed trajectories\nupdated · base · NullMemory',PURPLE,25,True); arrow(3.8,6.12,4.2,6.12)
box(8.45,6.05,2.6,.68,'Evaluator A\nHarmBench',GREEN,26,True)
box(8.45,4.95,2.6,.68,'Evaluator B\nDeepSeek',RED,26,True)
arrow(7.65,6.12,8.40,6.39); arrow(7.65,6.00,8.40,5.29)
box(12.0,6.05,5.8,.68,'current: 0/12\nfuture branches: updated 8 · base 4 · null 0',GREEN,24,True)
box(12.0,4.95,5.8,.68,'current: 1/12\nfuture branches: updated 5 · base 5 · null 8',RED,24,True)
arrow(11.1,6.39,11.95,6.39); arrow(11.1,5.29,11.95,5.29)
# One timeline illustration.
box(2.15,3.35,3.1,.62,'same state / task / seed\ntrajectory branch',TAN,24,True)
for i,x in enumerate([6.0,7.8,9.6]): box(x,3.35,1.25,.62,f't = {i+1}\nweb step',BLUE,22)
arrow(5.30,3.66,5.95,3.66); arrow(7.30,3.66,7.75,3.66); arrow(9.10,3.66,9.55,3.66)
box(11.4,3.35,2.5,.62,'same trace bytes\njudged twice',PURPLE,24,True); arrow(10.9,3.66,11.35,3.66)
box(14.5,3.35,3.0,.62,'different first-event\ninterpretation possible',YELLOW,24,True); arrow(13.95,3.66,14.45,3.66)
box(5.2,1.55,8.7,.72,'Scientific question: is a temporal safety claim a property of persistent state,\nor only of persistent state × evaluator?',YELLOW,26,True)
box(6.2,.45,6.7,.60,'ERTA keeps evaluator outputs vector-valued instead of manufacturing a consensus label.',PURPLE,24,True); arrow(9.55,1.50,9.55,1.08)
png=OUT/'g1-evaluator-relative-scene-handdrawn.png'; pdf=OUT/'g1-evaluator-relative-scene-handdrawn.pdf'; im.save(png,dpi=(240,240)); im.save(pdf,'PDF',resolution=240.0); print(png); print(pdf)
