from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math
OUT=Path(__file__).resolve().parent/'figures'; OUT.mkdir(parents=True,exist_ok=True)
W,H=3400,1500; S=W/19.0
INK='#263238'; BG='#fffdf8'; PURPLE='#ddd8f5'; BLUE='#d9e7f5'; GREEN='#dcefdc'; TAN='#f3e6cf'; YELLOW='#fff2c7'
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
title(9.5,7.55,'Figure 2 · Prospective L2 provenance-field audit',45)
title(9.5,7.12,'Build the bank first, qualify memory use, then compare masked vs truthful field exposure on paired tasks.',29)
title(2.05,6.46,'1 · Build source bank',32)
box(.45,5.35,3.2,.68,'350 frozen source tasks\n176 success · 174 failure',BLUE,24,True)
box(.45,4.30,3.2,.68,'MemRL writes memory\ncontent + provenance field',GREEN,24,True); arrow(2.05,5.30,2.05,5.03)
title(6.25,6.46,'2 · Qualify and freeze',32)
box(4.45,5.35,3.6,.68,'fresh support qualification\n106 / 108 clusters eligible',GREEN,24,True)
box(4.45,4.30,3.6,.68,'hash-freeze\n32 primary + 8 utilization',PURPLE,24,True); arrow(6.25,5.30,6.25,5.03)
title(10.55,6.46,'3 · Memory-use gate',32)
box(8.75,5.35,3.6,.68,'true · null · reversed\nshuffled · no-memory',TAN,23,True)
box(8.75,4.30,3.6,.68,'first-action gate must pass\nbefore primary outcomes',GREEN,24,True); arrow(10.55,5.30,10.55,5.03)
title(15.55,6.46,'4 · Paired primary L2',32)
box(13.45,5.35,1.95,.68,'A\nfield masked',BLUE,24,True); box(15.72,5.35,2.0,.68,'B\ntruthful field',GREEN,24,True)
box(13.45,4.25,4.27,.72,'same content/order · same task\nseparate reset environment',PURPLE,23,True); arrow(14.43,5.30,15.05,5.00); arrow(16.72,5.30,16.10,5.00)
# The top row is one frozen sequence, not four independent experiments.
arrow(3.70,4.64,4.38,4.64); arrow(8.10,4.64,8.68,4.64); arrow(12.40,4.64,13.38,4.64)
box(4.40,2.78,4.10,.74,'Executor 1 · Qwen2.5-7B-Instruct\n32 paired clusters',BLUE,24,True)
box(10.45,2.78,4.10,.74,'Executor 2 · Llama-3.1-8B-Instruct\nsame frozen bank + retrieval',GREEN,24,True)
# Both executors receive the exact same frozen paired L2 object.
arrow(15.58,4.20,7.90,3.58); arrow(15.58,4.20,12.95,3.58)
box(4.35,1.58,10.25,.72,'Readouts: first executable action · step count · terminal success\npaired sign test + preregistered bootstrap · conservative sparse-discordance audit',PURPLE,24,True)
arrow(6.45,2.73,7.25,2.34); arrow(12.50,2.73,11.70,2.34)
box(5.15,.38,8.65,.64,'Fail-closed interpretation: local action sensitivity ≠ semantic provenance reasoning ≠ practical equivalence',YELLOW,23,True)
png=OUT/'b1-provenance-method-handdrawn.png'; pdf=OUT/'b1-provenance-method-handdrawn.pdf'; im.save(png,dpi=(240,240)); im.save(pdf,'PDF',resolution=240.0); print(png); print(pdf)
