# Applies the placement table and the board outline to CapScan5x5.kicad_pcb (file edit; reload the board in KiCad afterwards).
import re,sys,os,uuid,math
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import sch
P='CapScan5x5.kicad_pcb'; s=open(P,encoding='utf8').read()
X0,Y0,W,H,R=101,100,48,47,2
SW=111.5
T={'J2':(120.92,107,-90),'J1':(139.24,107,-90),
 'U9':(120.27,SW,90),'U10':(117.73,SW,90),'U11':(115.19,SW,90),'U12':(112.65,SW,90),'U13':(110.11,SW,90),
 'U4':(138.59,SW,90),'U5':(136.05,SW,90),'U6':(133.51,SW,90),'U7':(130.97,SW,90),'U8':(128.43,SW,90),
 'C6':(108.4,SW,-90),'C7':(124.9,SW,-90),'U14':(122.81,SW,90),'C8':(124.9,109.2,180),'C4':(126.6,SW,-90),'C5':(140.3,SW,-90),
 'U2':(125,117.5,-90),'U3':(132.5,119.2,-90),'C3':(137.3,121.8,90),
 'C1':(126.2,123,0),'C2':(129,124.1,0),'FB1':(132.4,124.1,0),
 'U1':(125,136.5,180),'R4':(136.4,127,90),'R5':(138,127,90),'J3':(141,128.83,0),
 'R2':(113.9,131.37,0),'D2':(110.9,131.37,0),'R3':(113.9,133.91,0),'D3':(110.9,133.91,0),'R1':(113.9,138.99,0),'D1':(110.9,138.99,0),
 'H1':(105.5,104.5,0),'H2':(144.5,104.5,0),'H3':(105.5,142.5,0),'H4':(144.5,142.5,0)}
def fmt(v): return ('%.4f'%v).rstrip('0').rstrip('.')
out=[];pos=0;done=set()
for m in re.finditer(r'\(footprint "[^"]+"',s):
    e=sch.block_end(s,m.start()); b=s[m.start():e]
    ref=re.search(r'\(property "Reference" "([^"]+)"',b).group(1)
    if ref not in T: continue
    x,y,rot=T[ref]
    a=re.search(r'\(at ([\d.\-]+) ([\d.\-]+)(?: ([\d.\-]+))?\)',b); old=float(a.group(3) or 0); d=(rot-old)%360
    head=b[:a.start()]+'(at %s %s%s)'%(fmt(x),fmt(y),'' if rot%360==0 else ' '+fmt(rot))
    rest=b[a.end():]
    if d:
        def fix(mm):
            ang=(float(mm.group(3) or 0)+d)%360
            return '(at %s %s%s)'%(mm.group(1),mm.group(2),'' if ang==0 else ' '+fmt(ang))
        # pads and texts carry absolute angles
        def blockfix(kind,txt):
            res=[];p=0
            for k in re.finditer(r'\((?:%s) '%kind,txt):
                if k.start()<p: continue
                ke=sch.block_end(txt,k.start()); kb=txt[k.start():ke]
                kb=re.sub(r'\(at ([\d.\-]+) ([\d.\-]+)(?: ([\d.\-]+))?\)',fix,kb,1)
                res.append(txt[p:k.start()]+kb); p=ke
            return ''.join(res)+txt[p:]
        rest=blockfix('pad|property|fp_text',rest)
    out.append(s[pos:m.start()]+head+rest); pos=e; done.add(ref)
s=''.join(out)+s[pos:]
assert done==set(T), set(T)-done
# H4: plated, grounded M3 hole (same geometry as MountingHole_3.2mm_M3_Pad)
for m in re.finditer(r'\(footprint "[^"]+"',s):
    e=sch.block_end(s,m.start()); b=s[m.start():e]
    if '"Reference" "H4"' not in b: continue
    i=b.index('(pad'); j=sch.block_end(b,i)
    if 'np_thru_hole' in b[i:j]:
        nb=b[:i]+'(pad "1" thru_hole circle (at 0 0) (size 6.4 6.4) (drill 3.2) (layers "*.Cu" "*.Mask") (net "GND") (uuid "%s"))'%uuid.uuid4()+b[j:]
        nb=nb.replace('(footprint "MountingHole:MountingHole_3.2mm_M3"','(footprint "MountingHole:MountingHole_3.2mm_M3_Pad"',1)
        nb=re.sub(r'(\(property "Value" )"[^"]*"',r'\1"M3 GND (plated)"',nb,1)
        s=s[:m.start()]+nb+s[e:]
    break
# outline
res=[];p=0;n=0
for k in re.finditer(r'\(gr_(?:line|arc|rect|poly|circle)\b',s):
    ke=sch.block_end(s,k.start())
    if '"Edge.Cuts"' in s[k.start():ke]: res.append(s[p:k.start()]); p=ke; n+=1
s=''.join(res)+s[p:]
x1,y1,x2,y2=X0,Y0,X0+W,Y0+H; q=R*(1-math.sqrt(.5))
def line(a,b): return '\t(gr_line (start %s %s) (end %s %s) (stroke (width 0.1) (type default)) (layer "Edge.Cuts") (uuid "%s"))\n'%(fmt(a[0]),fmt(a[1]),fmt(b[0]),fmt(b[1]),uuid.uuid4())
def arc(a,mid,b): return '\t(gr_arc (start %s %s) (mid %s %s) (end %s %s) (stroke (width 0.1) (type default)) (layer "Edge.Cuts") (uuid "%s"))\n'%(fmt(a[0]),fmt(a[1]),fmt(mid[0]),fmt(mid[1]),fmt(b[0]),fmt(b[1]),uuid.uuid4())
g=line((x1+R,y1),(x2-R,y1))+arc((x2-R,y1),(x2-q,y1+q),(x2,y1+R))+line((x2,y1+R),(x2,y2-R))+arc((x2,y2-R),(x2-q,y2-q),(x2-R,y2))\
 +line((x2-R,y2),(x1+R,y2))+arc((x1+R,y2),(x1+q,y2-q),(x1,y2-R))+line((x1,y2-R),(x1,y1+R))+arc((x1,y1+R),(x1+q,y1+q),(x1+R,y1))
i=s.rindex(')'); s=s[:i]+g+s[i:]
d=0;qq=False
for k,c in enumerate(s):
    if c=='"' and s[k-1]!='\\': qq=not qq
    elif not qq: d+=(c=='(')-(c==')')
assert d==0
open(P,'w',encoding='utf8').write(s); print('moved',len(done),'edge items removed',n)
