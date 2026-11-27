# Dump absolute pad positions / nets of a .kicad_pcb and report pad-box and courtyard-ish overlaps between footprints.
import re,sys,math,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import sch
def load(path):
    s=open(path,encoding='utf8').read(); fps={}
    for m in re.finditer(r'\(footprint "([^"]+)"',s):
        e=sch.block_end(s,m.start()); b=s[m.start():e]
        ref=re.search(r'\(property "Reference" "([^"]+)"',b).group(1)
        at=re.search(r'\(at ([\d.\-]+) ([\d.\-]+)(?: ([\d.\-]+))?\)',b); fx,fy,fr=float(at.group(1)),float(at.group(2)),float(at.group(3) or 0)
        pads=[]
        for pm in re.finditer(r'\(pad "([^"]*)" (\w+) (\w+)',b):
            pe=sch.block_end(b,pm.start()); pb=b[pm.start():pe]
            a=re.search(r'\(at ([\d.\-]+) ([\d.\-]+)(?: ([\d.\-]+))?\)',pb); px,py=float(a.group(1)),float(a.group(2)); pr=float(a.group(3) or 0)
            sz=re.search(r'\(size ([\d.]+) ([\d.]+)\)',pb); w,h=float(sz.group(1)),float(sz.group(2))
            net=re.search(r'\(net (?:\d+ )?"([^"]*)"\)',pb)
            t=math.radians(fr); x=fx+px*math.cos(t)+py*math.sin(t); y=fy-px*math.sin(t)+py*math.cos(t)
            if round((pr)%180)==90: w,h=h,w
            pads.append((pm.group(1),round(x,3),round(y,3),w,h,net.group(1) if net else '',pm.group(2)))
        fps[ref]=dict(fp=m.group(1),x=fx,y=fy,rot=fr,pads=pads)
    return fps
if __name__=='__main__':
    fps=load(sys.argv[1])
    for r in sys.argv[2:]:
        print(r,fps[r]['fp'],fps[r]['x'],fps[r]['y'],fps[r]['rot'])
        for p in fps[r]['pads']: print('  ',p)
    box={}
    for r,f in fps.items():
        if not f['pads']: continue
        box[r]=(min(p[1]-p[3]/2 for p in f['pads']),min(p[2]-p[4]/2 for p in f['pads']),max(p[1]+p[3]/2 for p in f['pads']),max(p[2]+p[4]/2 for p in f['pads']))
    rs=sorted(box)
    for i,a in enumerate(rs):
        for b in rs[i+1:]:
            A,B=box[a],box[b]; g=0.25
            if A[0]-g<B[2] and B[0]-g<A[2] and A[1]-g<B[3] and B[1]-g<A[3]: print('NEAR/OVERLAP',a,[round(v,2) for v in A],b,[round(v,2) for v in B])
