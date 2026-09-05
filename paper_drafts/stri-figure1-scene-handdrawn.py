from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random, math

OUT=Path(__file__).resolve().parent/'figures'; OUT.mkdir(parents=True,exist_ok=True)
W,H=3000,1500; S=W/16.0; random.seed(17)
INK='#263238'; BG='#fffdf8'; PURPLE='#ddd8f5'; BLUE='#d9e7f5'; GREEN='#dcefdc'; TAN='#f3e6cf'; RED='#f3d9d6'; YELLOW='#fff2c7'
im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'; BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def font(px,bold=False): return ImageFont.truetype(BOLD if bold else FONT,px)
def xy(x,y): return int(x*S), int(H-y*S)
def center_text(box,text,fs=34,bold=False,fill=INK):
    x0,y0,x1,y1=box; lines=text.split('\n'); f=font(fs,bold); gap=4
    heights=[]; widths=[]
    for line in lines:
        b=d.textbbox((0,0),line,font=f); widths.append(b[2]-b[0]); heights.append(b[3]-b[1])
    total=sum(heights)+gap*(len(lines)-1); yy=(y0+y1-total)/2
    for line,w,h in zip(lines,widths,heights): d.text(((x0+x1-w)/2,yy),line,font=f,fill=fill); yy+=h+gap
def box(x,y,w,h,text,fc='white',fs=32,bold=False):
    x0,y1=xy(x,y); x1,y0=xy(x+w,y+h); rect=(x0,y0,x1,y1)
    for j in range(2):
        off=random.randint(-2,2); d.rounded_rectangle((x0+off,y0-off,x1+off,y1-off),radius=24,fill=fc if j==0 else None,outline=INK,width=3)
    center_text(rect,text,fs,bold); return rect
def arrow(x1,y1,x2,y2):
    a=xy(x1,y1); b=xy(x2,y2); d.line([a,b],fill=INK,width=4)
    ang=math.atan2(b[1]-a[1],b[0]-a[0]); L=22
    p1=(b[0]-L*math.cos(ang-.55),b[1]-L*math.sin(ang-.55)); p2=(b[0]-L*math.cos(ang+.55),b[1]-L*math.sin(ang+.55))
    d.polygon([b,p1,p2],fill=INK)
def title(x,y,text,fs=38):
    p=xy(x,y); d.text(p,text,font=font(fs,True),fill=INK,anchor='mm')

# Header and invariant.
title(8,7.55,'Figure 1 · Same capability, different packaging, different access',46)
title(8,7.13,'A semantics-preserving refactor should not silently change what the actor can use.',30)
box(.45,6.12,2.1,.68,'User task\nprepare a multi-step job',BLUE,28,True)
box(3.0,6.12,4.0,.68,'Frozen semantic capability U\ncontent + support unchanged',GREEN,28,True)
box(7.52,6.12,3.45,.68,'Same access mechanism\n+ same budget B',PURPLE,28,True)
box(11.52,6.12,3.95,.68,'Only package identity / count /\npartition may change',TAN,27,True)
arrow(2.6,6.46,2.95,6.46); arrow(7.05,6.46,7.48,6.46); arrow(11.02,6.46,11.47,6.46)

# Canonical library branch.
title(3.55,5.48,'A · Canonical packaging',34)
for x,t,c in [(.55,'skill α\nsemantic A',GREEN),(2.42,'skill β\nsemantic B',BLUE),(4.29,'skill γ\nsemantic C',PURPLE),(6.16,'skill δ\nsemantic D',TAN)]: box(x,4.55,1.65,.62,t,c,25)
box(2.05,3.45,3.0,.66,'fixed selector / access boundary',PURPLE,27,True)
arrow(1.38,4.5,2.6,4.12); arrow(3.25,4.5,3.25,4.12); arrow(5.12,4.5,3.95,4.12)
box(2.05,2.46,3.0,.62,'actor-visible semantics\n{A, B, C}',GREEN,28,True); arrow(3.55,3.4,3.55,3.12)
# Refactored library branch: repeated identities consume slots.
title(12.35,5.48,'B · Semantics-preserving refactor',34)
for x,t,c,w in [(8.28,'α₁\nA',GREEN,1.45),(9.90,'α₂\nA',GREEN,1.45),(11.52,'α₃\nA',GREEN,1.45),(13.14,'β\nB',BLUE,1.45),(14.76,'γ\nC',PURPLE,.82)]: box(x,4.55,w,.62,t,c,25)
box(10.45,3.45,3.65,.66,'same fixed selector / same budget',PURPLE,27,True)
for x in [9.0,10.62,12.24,13.86,15.17]: arrow(x,4.5,12.28,4.12)
box(10.45,2.46,3.65,.62,'actor-visible semantics\n{A, B} · C crowded out',RED,27,True); arrow(12.28,3.4,12.28,3.12)

# Same actor icons.
def actor(cx):
    x,y=xy(cx,1.68); r=34; d.ellipse((x-r,y-r,x+r,y+r),fill='white',outline=INK,width=4)
    d.line((x,y+r,x,y+115),fill=INK,width=4); d.line((x-45,y+65,x+45,y+65),fill=INK,width=4)
    d.line((x,y+115,x-38,y+155),fill=INK,width=4); d.line((x,y+115,x+38,y+155),fill=INK,width=4)
actor(3.55); actor(12.28)
title(3.55,.48,'same actor',25); title(12.28,.48,'same actor',25)
box(5.45,.28,5.15,.92,'STRI question: should semantic access change\nonly because the same capability was repackaged?',YELLOW,29,True)
arrow(5.38,.78,4.0,1.18); arrow(10.66,.78,11.85,1.18)

png=OUT/'stri-scene-handdrawn.png'; pdf=OUT/'stri-scene-handdrawn.pdf'
im.save(png,dpi=(240,240)); im.save(pdf,'PDF',resolution=240.0)
print(png); print(pdf)
