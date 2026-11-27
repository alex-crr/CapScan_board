# Hand-laid copper for the analog front end, written before the autorouter runs:
# socket pin -> switch A (straight), GND vias under each switch, the CIN and EXC buses, the reference branch.
# Run after tools/place.py:  python3 tools/prelay.py   (input must have no tracks)
import sys,os,uuid
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import pads
P='CapScan5x5.kicad_pcb'; s=open(P,encoding='utf8').read()
assert '(segment' not in s and '(via' not in s, 'board already has copper'
F=pads.load(P); out=[]
def pad(ref,n):
    for p in F[ref]['pads']:
        if p[0]==str(n): return p[1],p[2]
def seg(net,*pts,w=0.2):
    for a,b in zip(pts,pts[1:]):
        out.append('\t(segment (start %.3f %.3f) (end %.3f %.3f) (width %s) (layer "F.Cu") (net "%s") (uuid "%s"))\n'%(a[0],a[1],b[0],b[1],w,net,uuid.uuid4()))
def via(net,x,y): out.append('\t(via (at %.3f %.3f) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net "%s") (uuid "%s"))\n'%(x,y,net,uuid.uuid4()))
YB=114.5; YV=113.85
RX=['U9','U10','U11','U12','U13']; TX=['U4','U5','U6','U7','U8']
for row,sock,name in ((RX,'J2','RX'),(TX,'J1','TX')):
    for k,u in enumerate(row,1):
        a=pad(u,4); j=pad(sock,k); assert abs(a[0]-j[0])<1e-3
        seg('%s%d'%(name,k),a,j)                                   # line: switch A straight up to the socket pin
        g1=pad(u,1); g2=pad(u,2); m=((g1[0]+g2[0])/2,g1[1]+0.26)
        seg('GND',(g1[0],m[1]),(g2[0],m[1]))
        if u=='U8':   # the EXC link to U2 runs under U8: its GND via goes left, shared with C4
            via('GND',127.3,112.55); seg('GND',(g1[0],m[1]),(127.3,112.55),pad('C4',2))
        else: seg('GND',m,(m[0],YV)); via('GND',m[0],YV)
        b=pad(u,3); seg('CIN' if name=='RX' else 'EXC',b,(b[0],YB))  # B0 stub down to the bus
# CIN bus: under the RX row, ends on U2 pin 8
c8=pad('U2',8); seg('CIN',(pad('U13',3)[0],YB),(c8[0],YB))
# reference switch U14: GND via to the left, B0 jogs into U2 pin 8 from above
g1=pad('U14',1); g2=pad('U14',2); seg('GND',(g1[0],g1[1]+0.26),(g2[0],g2[1]+0.26)); seg('GND',(g1[0],g1[1]+0.26),(121.75,113.3),(121.75,YV)); via('GND',121.75,YV)
b=pad('U14',3); seg('CIN',b,(b[0],113.2),(c8[0]+0.1,113.2),(c8[0],113.3),(c8[0],c8[1]))
# EXC bus: under the TX row, then above U2 pins 1-2 into pin 3
e3=pad('U2',3); u8=pad('U8',3)
seg('EXC',(pad('U4',3)[0],YB),(u8[0],YB)); seg('EXC',(u8[0],113.2),(e3[0],113.2),(e3[0],e3[1]))
# reference branch: EXC -> C8 -> U14 A
c1=pad('C8',1); seg('EXC',c1,(125.75,c1[1]+0.37),(125.75,113.2))
c2=pad('C8',2); a=pad('U14',4); seg('Net-(C8-Pad2)',c2,(a[0],c2[1]+(c2[0]-a[0])),a)
i=s.rindex(')'); s=s[:i]+''.join(out)+s[i:]
open(P,'w',encoding='utf8').write(s); print('segments+vias written:',len(out))
