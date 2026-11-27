# Courtyard overlap check + SVG preview of the placement.
import re,sys,os,math
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import sch,pads
s=open(sys.argv[1],encoding='utf8').read(); box={}
for m in re.finditer(r'\(footprint "([^"]+)"',s):
    e=sch.block_end(s,m.start()); b=s[m.start():e]
    ref=re.search(r'\(property "Reference" "([^"]+)"',b).group(1)
    a=re.search(r'\(at ([\d.\-]+) ([\d.\-]+)(?: ([\d.\-]+))?\)',b); fx,fy,t=float(a.group(1)),float(a.group(2)),math.radians(float(a.group(3) or 0))
    pts=[]
    for g in re.finditer(r'\((fp_line|fp_rect|fp_poly|fp_circle)',b):
        gb=b[g.start():sch.block_end(b,g.start())]
        if 'CrtYd' not in gb: continue
        c=re.search(r'\(center ([\d.\-]+) ([\d.\-]+)\)',gb)
        if c:
            en=re.search(r'\(end ([\d.\-]+) ([\d.\-]+)\)',gb); r=math.hypot(float(en.group(1))-float(c.group(1)),float(en.group(2))-float(c.group(2)))
            pts+=[(float(c.group(1))-r,float(c.group(2))-r),(float(c.group(1))+r,float(c.group(2))+r),(float(c.group(1))-r,float(c.group(2))+r),(float(c.group(1))+r,float(c.group(2))-r)]
        else: pts+=[(float(x),float(y)) for x,y in re.findall(r'\((?:start|end|xy) ([\d.\-]+) ([\d.\-]+)\)',gb)]
    if not pts: continue
    g=[(fx+px*math.cos(t)+py*math.sin(t),fy-px*math.sin(t)+py*math.cos(t)) for px,py in pts]
    box[ref]=(min(p[0] for p in g),min(p[1] for p in g),max(p[0] for p in g),max(p[1] for p in g))
rs=sorted(box);bad=0
for i,a in enumerate(rs):
    for b in rs[i+1:]:
        A,B=box[a],box[b]
        if A[0]<B[2]-1e-6 and B[0]<A[2]-1e-6 and A[1]<B[3]-1e-6 and B[1]<A[3]-1e-6: print('COURTYARD OVERLAP',a,b); bad+=1
print('courtyard overlaps:',bad)
fps=pads.load(sys.argv[1]); col={'GND':'#888','+3V3':'#d33','+3.3VA':'#e80','CIN':'#0a0','EXC':'#06c'}
o=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="99 98 52 51" width="1040" height="1020"><rect x="99" y="98" width="52" height="51" fill="#fff"/><rect x="101" y="100" width="48" height="47" rx="2" fill="#f4f1e6" stroke="#000" stroke-width="0.15"/>']
for r,(a,b,c,d) in box.items():
    o.append(f'<rect x="{a:.2f}" y="{b:.2f}" width="{c-a:.2f}" height="{d-b:.2f}" fill="none" stroke="#b0b" stroke-width="0.06"/><text x="{(a+c)/2:.2f}" y="{b-0.15:.2f}" font-size="0.9" text-anchor="middle" font-family="sans-serif">{r}</text>')
for r,f in fps.items():
    for n,x,y,w,h,net,typ in f['pads']: o.append(f'<rect x="{x-w/2:.3f}" y="{y-h/2:.3f}" width="{w}" height="{h}" fill="{col.get(net,"#c90" if net else "#ccc")}"/>')
open(sys.argv[2],'w').write(''.join(o)+'</svg>')
