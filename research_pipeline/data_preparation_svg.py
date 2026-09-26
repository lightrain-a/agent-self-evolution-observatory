"""Small deterministic SVG renderer for numeric candidate previews.

All marks are computed from the bound values. No external templates, invented
uncertainty, synthetic samples, model calls or runtime package installation.
"""
from __future__ import annotations
from collections import Counter, defaultdict
import hashlib
import html
import math
import textwrap
from .data_preparation_figures import validate_asset, BY_ID

COLORS = ('#2563eb','#0891b2','#7c3aed','#d97706','#059669','#db2777')


def color(label):
    return COLORS[int(hashlib.sha256(str(label).encode()).hexdigest()[:8],16) % len(COLORS)]


def quantile(values, p):
    vals = sorted(values); k = (len(vals)-1)*p; i = int(k)
    return vals[i] + (vals[min(i+1,len(vals)-1)]-vals[i])*(k-i)


def render_svg(asset: dict, candidate: dict) -> str:
    errors = validate_asset(asset)
    if errors: raise ValueError(';'.join(errors))
    recipe = candidate['recipe']
    if recipe not in BY_ID or BY_ID[recipe]['kind'] != asset['kind']: raise ValueError('incompatible-recipe')
    if recipe == 'bubble' and any(type(r.get('size')) not in (int,float) or not math.isfinite(r['size']) or r['size']<0 for r in asset['rows']): raise ValueError('bubble-size-missing')
    esc = lambda v: html.escape(str(v), quote=True)
    W,H,L,R,T,B = 680,460,132,616,100,350
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">',
             '<title>'+esc(asset['question']+' — '+BY_ID[recipe]['label'])+'</title>',
             '<desc>'+esc('Data: '+candidate['data_sha256']+'; '+asset['scope']+'; role='+asset['data_role'])+'</desc>',
             '<rect width="680" height="460" fill="white"/>',
             '<style>text{font-family:'+esc(candidate.get('style',{}).get('font_family','Georgia, serif'))+';fill:#172033} .muted{fill:#526174}</style>']
    def line(x1,y1,x2,y2,stroke='#cbd5e1',width=1,extra=''):
        parts.append(f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="{stroke}" stroke-width="{width}" {extra}/>')
    def text(x,y,v,size=13,anchor='start',cls='',extra=''):
        parts.append(f'<text x="{x:.3f}" y="{y:.3f}" font-size="{size}" text-anchor="{anchor}" class="{cls}" {extra}>{esc(v)}</text>')
    def circle(x,y,r=4,fill='#2563eb',opacity=1):
        parts.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{r:.3f}" fill="{fill}" opacity="{opacity}"/>')
    def rect(x,y,w,h,fill,opacity=1):
        parts.append(f'<rect x="{x:.3f}" y="{y:.3f}" width="{max(0,w):.3f}" height="{max(0,h):.3f}" fill="{fill}" opacity="{opacity}" rx="2"/>')
    def poly(points,stroke,width=2,extra=''):
        parts.append('<polyline points="'+' '.join(f'{x:.3f},{y:.3f}' for x,y in points)+f'" fill="none" stroke="{stroke}" stroke-width="{width}" {extra}/>')
    title = textwrap.wrap(asset['question'], 56)[:2]
    for i, s in enumerate(title): text(24,30+i*23,s,20)
    text(24,80,BY_ID[recipe]['label'].split(' / ')[-1]+' · '+asset['analysis_unit'],13,cls='muted')
    text(656,80,'SYNTHETIC DEMO' if asset['data_role']=='SYNTHETIC_DEMO' else asset['data_role'],11,'end','muted')
    def bounds(vals, zero=False):
        lo,hi = min(vals),max(vals)
        if zero: lo,hi=min(lo,0),max(hi,0)
        if hi==lo: return (0,1) if hi==0 else (lo-abs(lo)*.1,hi+abs(hi)*.1)
        margin=(hi-lo)*.06
        return (lo-margin if lo!=0 else 0,hi+margin if hi!=0 else 0)
    def sx(v, domain): return L+(v-domain[0])/(domain[1]-domain[0])*(R-L)
    def sy(v, domain): return B-(v-domain[0])/(domain[1]-domain[0])*(B-T)
    def axis_x(domain, label):
        line(L,B,R,B,stroke='#8290a1')
        for i in range(5):
            v=domain[0]+(domain[1]-domain[0])*i/4; x=sx(v,domain)
            line(x,B,x,B+5); text(x,B+23,f'{v:.3g}',12,'middle','muted')
        text((L+R)/2,B+52,label,14,'middle')
    def axis_y(domain,label):
        line(L,T,L,B,stroke='#8290a1')
        for i in range(5):
            v=domain[0]+(domain[1]-domain[0])*i/4; y=sy(v,domain)
            line(L,y,R,y,extra='stroke-dasharray="2 5"'); text(L-10,y+4,f'{v:.3g}',12,'end','muted')
        text(24,(T+B)/2,label,13,'middle',extra=f'transform="rotate(-90 24 {(T+B)/2})"')
    def label_y(i,n): return T+(i+.5)*(B-T)/n
    def row_labels(rows):
        for i,r in enumerate(rows): text(L-12,label_y(i,len(rows))+4,str(r.get('label',r.get('group','')))[:18],12,'end')
    rows=asset.get('rows',[]); unit=asset['unit']
    if recipe in {'dot','lollipop','bar','tile','delta','dumbbell','forest'}:
        if recipe=='delta': values=[r['after']-r['before'] for r in rows]
        elif recipe=='dumbbell': values=[v for r in rows for v in (r['before'],r['after'])]
        elif recipe=='forest': values=[v for r in rows for v in (r['lower'],r['upper'])]
        else: values=[r['value'] for r in rows]
        domain=bounds(values,zero=True); axis_x(domain,unit); row_labels(rows)
        line(sx(0,domain),T,sx(0,domain),B,stroke='#94a3b8',extra='stroke-dasharray="4 4"')
        for i,r in enumerate(rows):
            y=label_y(i,len(rows)); h=min(32,(B-T)/len(rows)*.55)
            if recipe=='dumbbell':
                a,b=sx(r['before'],domain),sx(r['after'],domain)
                line(a,y,b,y,stroke='#94a3b8',width=3); circle(a,y,5,'#94a3b8'); circle(b,y,6,color(r.get('label')))
                continue
            if recipe=='forest':
                a,b=sx(r['lower'],domain),sx(r['upper'],domain)
                line(a,y,b,y,stroke=color(r['label']),width=3); line(a,y-5,a,y+5); line(b,y-5,b,y+5); circle(sx(r['value'],domain),y,5,color(r['label'])); continue
            value=r['after']-r['before'] if recipe=='delta' else r['value']; x=sx(value,domain); c='#dc5263' if value<0 else color(r['label'])
            if recipe=='bar': rect(min(sx(0,domain),x),y-h/2,abs(x-sx(0,domain)),h,c,.85)
            elif recipe=='tile':
                intensity=abs(value)/max(max(abs(v) for v in values),1e-12)
                rect(L,y-h/2,R-L,h,c,.12+.7*intensity); text((L+R)/2,y+4,f'{value:.3g}',13,'middle'); continue
            elif recipe in {'lollipop','delta'}: line(sx(0,domain),y,x,y,stroke=c,width=2)
            if recipe!='bar': circle(x,y,6,c)
            text(min(R+10,x+10),y+4,f'{value:.3g}',12)
        if recipe=='dumbbell': text(L,T-9,'gray: before   colored: after',12,cls='muted')
        if recipe=='forest': text(L,T-9,asset['interval_kind']+'; '+str(asset.get('confidence_level','')),12,cls='muted')
    elif recipe=='slope':
        domain=bounds([v for r in rows for v in (r['before'],r['after'])]); axis_y(domain,unit)
        for r in rows:
            c=color(r['label']); a,b=sy(r['before'],domain),sy(r['after'],domain)
            line(L+40,a,R-95,b,c,2); circle(L+40,a,5,c); circle(R-95,b,5,c)
            text(R-85,b+4,str(r['label'])[:16],11)
        text(L+40,B+26,'Before',14,'middle'); text(R-95,B+26,'After',14,'middle')
    elif recipe in {'parity','scatter','bubble'}:
        xs=[r['before'] if recipe=='parity' else r['x'] for r in rows]
        ys=[r['after'] if recipe=='parity' else r['y'] for r in rows]
        xd,yd=(bounds(xs+ys),bounds(xs+ys)) if recipe=='parity' else (bounds(xs),bounds(ys))
        axis_x(xd,'Before ('+unit+')' if recipe=='parity' else asset['x_unit']); axis_y(yd,'After ('+unit+')' if recipe=='parity' else asset['y_unit'])
        if recipe=='parity': line(sx(xd[0],xd),sy(xd[0],yd),sx(xd[1],xd),sy(xd[1],yd),stroke='#64748b',extra='stroke-dasharray="5 4"')
        for r,x,y in zip(rows,xs,ys):
            radius=5 if recipe!='bubble' else 16*math.sqrt(r['size']/max(max(q['size'] for q in rows),1e-12))
            circle(sx(x,xd),sy(y,yd),radius,color(r.get('label',r['id'])),.75)
        if recipe=='bubble': text(L,425,'Area: '+asset['size_unit']+'; max='+str(max(r['size'] for r in rows)),11,cls='muted')
    elif recipe in {'line','step'}:
        groups=defaultdict(list)
        for r in rows: groups[r['group']].append(r)
        xd=bounds([r['x'] for r in rows]); yd=bounds([r['y'] for r in rows]); axis_x(xd,asset['x_unit']); axis_y(yd,asset['y_unit'])
        for group,rs in groups.items():
            rs=sorted(rs,key=lambda r:r['x']); points=[]
            for i,r in enumerate(rs):
                if recipe=='step' and i: points.append((sx(r['x'],xd),sy(rs[i-1]['y'],yd)))
                points.append((sx(r['x'],xd),sy(r['y'],yd)))
            poly(points,color(group))
            # Step corners are interpolation guides, not extra observed samples.
            for r in rs: circle(sx(r['x'],xd),sy(r['y'],yd),3,color(group))
    elif recipe in {'ecdf','box','histogram','strip'}:
        groups=defaultdict(list)
        for r in rows: groups[r['group']].append(r['value'])
        allvals=[r['value'] for r in rows]; domain=bounds(allvals)
        if recipe=='ecdf':
            axis_x(domain,unit); axis_y((0,1),'Empirical probability')
            for group,vals in groups.items():
                points=[(L,B)]; total=0
                for value,count in sorted(Counter(vals).items()):
                    points.append((sx(value,domain),sy(total/len(vals),(0,1)))); total+=count
                    points.append((sx(value,domain),sy(total/len(vals),(0,1))))
                points.append((R,T)); poly(points,color(group))
        elif recipe=='histogram':
            lo,hi=domain; bins=min(12,max(2,int(math.sqrt(len(allvals))))); bw=(hi-lo)/bins
            counts={g:[0]*bins for g in groups}
            for g,vals in groups.items():
                for v in vals: counts[g][min(bins-1,max(0,int((v-lo)/bw)))]+=1
            yd=(0,max(max(c) for c in counts.values())*1.15 or 1); axis_x(domain,unit); axis_y(yd,'Sample count')
            for j,(g,ct) in enumerate(counts.items()):
                for i,n in enumerate(ct):
                    width=(R-L)/bins/len(groups)*.9; x=L+i*(R-L)/bins+j*(R-L)/bins/len(groups)
                    rect(x,sy(n,yd),width,B-sy(n,yd),color(g),.7)
        else:
            axis_y(domain,unit)
            for i,(g,vals) in enumerate(groups.items()):
                x=L+(i+.5)*(R-L)/len(groups); text(x,B+25,g[:16],12,'middle')
                if recipe=='strip':
                    for j,v in enumerate(vals): circle(x+((j*37)%23-11),sy(v,domain),3.5,color(g),.75)
                else:
                    q1,median,q3=quantile(vals,.25),quantile(vals,.5),quantile(vals,.75)
                    line(x,sy(min(vals),domain),x,sy(max(vals),domain),color(g),2)
                    rect(x-21,sy(q3,domain),42,sy(q1,domain)-sy(q3,domain),color(g),.3)
                    line(x-21,sy(median,domain),x+21,sy(median,domain),color(g),3)
            if recipe=='box': text(L,T-9,'Q1 / median / Q3; whiskers = min/max',11,cls='muted')
        for i,(g,vs) in enumerate(groups.items()): text(L+i*145,425,g[:14]+f' (n={len(vs)})',11,cls='muted')
    elif recipe in {'heatmap','bubble_matrix'}:
        values=asset['values']; nr,nc=len(values),len(values[0]); cw,ch=(R-L)/nc,(B-T)/nr
        vmax=max(abs(v) for row in values for v in row if v is not None) or 1
        for i,row in enumerate(values):
            text(L-9,T+(i+.5)*ch+4,str(asset['row_labels'][i])[:18],11,'end')
            for j,v in enumerate(row):
                x,y=L+j*cw,T+i*ch; rect(x+1,y+1,cw-2,ch-2,'#edf2f7')
                if v is None: text(x+cw/2,y+ch/2+4,'NA',11,'middle'); continue
                c='#dc5263' if v<0 else '#2563eb'
                if recipe=='heatmap': rect(x+1,y+1,cw-2,ch-2,c,.15+.7*abs(v)/vmax)
                else: circle(x+cw/2,y+ch/2,min(cw,ch)*.36*math.sqrt(abs(v)/vmax),c,.75)
                text(x+cw/2,y+ch/2+4,f'{v:.3g}',11,'middle')
        for j,label in enumerate(asset['column_labels']): text(L+(j+.5)*cw,B+23,str(label)[:12],11,'middle')
        text(L,B+50,unit+'; color/area scale |v| ≤ '+f'{vmax:.3g}',12,cls='muted')
    else: raise ValueError('renderer-not-implemented')
    if recipe in {'line','step'}:
        for i,g in enumerate(dict.fromkeys(r['group'] for r in rows)): text(L+i*145,425,g[:17],11,cls='muted')
    text(24,449,'Candidate only · '+candidate['id']+' · data '+candidate['data_sha256'][:12],10,cls='muted')
    parts.append('</svg>')
    return '\n'.join(parts)
